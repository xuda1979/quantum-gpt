"""Automatic checkpoint gate for teacher-free FV-GSPO.

Implements the plan's "自动 checkpoint gate" / "接受、拒绝、回滚并轮换角色"
deliverable (Teacher-Free-FV-GSPO-Final-Plan-ZH.docx, tables 27 & 28 and the
file-responsibility table 31):

    * evaluate a candidate checkpoint against the accepted checkpoint's fixed
      validation suites (accept / reject with a list of failing criteria);
    * on accept: rotate roles (previous accepted -> judge; candidate -> anchor;
      current policy -> trainable copy of the candidate); judge always lags.
    * on reject: keep anchor, reset the trainable policy to the anchor, halve
      the LR and raise the KL beta (the "rollback and reduce step size" path).

This is intentionally a PURE module (no I/O, no torch, no Huanxin): fully
unit-testable and with zero chance of corrupting a live training run. The
trainer loop calls `evaluate_checkpoint_gate`, then based on the result calls
the accept/reject role transitions.

Judge role lag (table 29): a newly accepted checkpoint becomes the anchor
immediately, but it is NOT its own judge — the judge is the *previous*
accepted checkpoint, so the judge always trails at least one generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Small noise allowance on quantum semantic V so a tiny nominal dip inside the
# suite's error band is not treated as a hard regression.
SEMANTIC_REGRESSION_ALLOW = 0.05


@dataclass
class GateMetrics:
    """Reported metric bundle for one checkpoint (fixed-suite evaluation).

    Values are sample means over the fixed validation suite. The caller is
    responsible for computing them and for supplying the statistical error
    margin on the quantum pass@1 (so a small nominal dip inside the error band
    is not treated as a regression — the plan requires '改善，或在统计误差内
    不下降').
    """

    quantum_pass1: float = 0.0
    code_pass1: float = 0.0
    semantic_v: float = 0.0
    quantum_error: float = 0.0
    diversity_ok: bool = True
    safety_ok: bool = True
    numeric_ok: bool = True

    def clamp(self) -> GateMetrics:
        return GateMetrics(
            quantum_pass1=max(0.0, min(1.0, self.quantum_pass1)),
            code_pass1=max(0.0, min(1.0, self.code_pass1)),
            semantic_v=max(0.0, min(1.0, self.semantic_v)),
            quantum_error=max(0.0, self.quantum_error),
            diversity_ok=bool(self.diversity_ok),
            safety_ok=bool(self.safety_ok),
            numeric_ok=bool(self.numeric_ok),
        )


@dataclass
class GateConfig:
    max_code_regression_pp: float = 0.03  # code pass@1 may fall at most -3pp
    require_quantum_improve: bool = True  # quantum pass@1 improve or within error
    min_semantic_no_regress: bool = True  # don't clearly regress semantic V


@dataclass
class GateDecision:
    accepted: bool
    reasons: list[str] = field(default_factory=list)

    @property
    def rejecting_reason(self) -> str | None:
        return self.reasons[0] if self.reasons and not self.accepted else None


def evaluate_checkpoint_gate(
    candidate: GateMetrics,
    accepted: GateMetrics,
    config: GateConfig | None = None,
) -> GateDecision:
    """Return accept/reject for a candidate checkpoint vs the accepted anchor.

    The candidate is accepted only if NONE of the fixed-suite gates fail. Every
    failing gate appends a human-readable reason so the rollback path can log
    exactly what regressed. All metrics are clamped to [0,1] before comparison.
    """
    cfg = config or GateConfig()
    c = candidate.clamp()
    a = accepted.clamp()
    failures: list[str] = []

    # 1) Quantum pass@1: improve, or within statistical error of the accepted.
    allowed = c.quantum_error
    if cfg.require_quantum_improve and c.quantum_pass1 < a.quantum_pass1 - allowed:
        failures.append(
            f"quantum_pass1 regressed ({c.quantum_pass1:.3f} < "
            f"{a.quantum_pass1:.3f} - err {allowed:.3f})"
        )

    # 2) Generic code pass@1: at most `max_code_regression_pp` percentage points down.
    if c.code_pass1 < a.code_pass1 - cfg.max_code_regression_pp:
        failures.append(
            f"code_pass1 regressed by {100 * (a.code_pass1 - c.code_pass1):.1f}pp "
            f"(> {100 * cfg.max_code_regression_pp:.1f}pp)"
        )

    # 3) Quantum semantic V: no clear regression (overall & key algorithm families).
    if cfg.min_semantic_no_regress and c.semantic_v < a.semantic_v - SEMANTIC_REGRESSION_ALLOW:
        failures.append(
            f"semantic_v regressed ({c.semantic_v:.3f} < "
            f"{a.semantic_v - SEMANTIC_REGRESSION_ALLOW:.3f})"
        )

    # 4) Diversity: must not have tripped unique/duplicate/entropy breakers.
    if not c.diversity_ok:
        failures.append("diversity breaker tripped")

    # 5) Safety: no test reads / network / harness bypass.
    if not c.safety_ok:
        failures.append("safety/harness-bypass violation")

    # 6) Numerical stability: finite loss/gradient; clip fraction and KL in limits.
    if not c.numeric_ok:
        failures.append("numerical instability (non-finite loss/grad or KL out of limits)")

    return GateDecision(accepted=not failures, reasons=failures)


@dataclass
class RoleState:
    """Tracks the four plan roles for rounding logic."""

    anchor_id: str | None = None
    judge_id: str | None = None
    current_id: str | None = None
    base_id: str | None = None

    def accept(
        self,
        *,
        new_checkpoint_id: str,
        base_id: str | None = None,
    ) -> RoleState:
        """Rotate roles on an accepted checkpoint (plan table 28, accept branch).

        previous accepted  -> judge (judge always lags at least one generation)
        new checkpoint     -> anchor
        policy current     -> trainable copy of the new checkpoint (same id here;
                              the trainer actually loads a trainable copy).
        """
        previous_anchor = self.anchor_id
        self.judge_id = (
            previous_anchor if previous_anchor is not None else (base_id or self.judge_id)
        )
        self.anchor_id = new_checkpoint_id
        # The current (trainable) policy is initialized from the new anchor.
        self.current_id = new_checkpoint_id
        return self

    def reject(
        self,
        *,
        lr_factor: float = 0.5,
        kl_factor: float = 1.5,
    ) -> dict[str, float]:
        """Return rollback step factors on a rejected checkpoint (table 28).

        The trainer is expected to: reset the trainable policy to the anchor,
        multiply LR by `lr_factor`, multiply KL beta by `kl_factor`, and discard
        stale rollouts. This method only returns the factors; it does not itself
        touch any optimizer.
        """
        # Rejecting never changes anchor/judge roles; only policy/optimizer state.
        return {"lr_factor": lr_factor, "kl_factor": kl_factor}

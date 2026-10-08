#!/usr/bin/env python3
# ruff: noqa: UP038  # (X | Y) isinstance is py3.10-only; this CLI runs under the py3.9 .venv
"""sapo_reward_audit.py — independent REWARD-PATH verification for SAPO RL.

Standing lane #18 (REWARD-PATH VERIFIER, .sapo-loop/rewardpath.md). For every
step record that carries ``rollout_rewards`` this script recomputes, for EVERY
candidate, the reward path from the recorded components — and, when raw
harness outputs (``{step, index, passed, details}``) are supplied, from the
harness result itself — plus the group-level advantage normalization
(LOO mean_other, shared running-MAD scale, +-clip). A wrong-reward bug cannot
hide behind clean loss identities: the loss only sees the final rewards and
advantages, so the audit verifies those against the contract.

CONTRACT (run-4-R2 launch, configs/rl/qwen36_27b_fv_gspo_asi2.json + launch
argv, verified 2026-08-25 against the box launch_config.json):
  weights       pass/shaped 0.45, syntax 0.05, interface 0.10, verifier 0.10,
                brevity 0.05, import-hygiene 0.05  (total 0.80, renormalized)
  reward-mode   p_dominant default; r17 adopts comprehensive masses
                0.50 pass / 0.40 shaped / 0.10 judge — CALIBRATION-GATED:
                no calibration file -> judge mass exactly 0 and the masses
                renormalize over P+S (J contributes NOTHING until calibrated);
                with judge_reward recorded -> total = clamp01((0.50P + 0.40S
                + 0.10J)/total_mass)
  shaped        shaped_reward_from_details: 1.0 on pass; on fail 0.0 (crash /
                no numeric evidence) or 0.5..0.9 (near-miss tiers); the
                recorded value must be 0.0 or in [0.5, 0.9] for failures
  advantages    LOO r_i - mean_other_i, divided by the shared running MAD
                (recorded as step ``advantage_scale``), clamped to +-2.5
                (--advantage-clip default); ``advantage`` in rollout_rewards
                is the final clamped value

Because interface_reward and import_hygiene_reward are NOT persisted in
``rollout_rewards`` (build_rollout_rewards gap, reported 2026-08-25), the
composition check for failing candidates is a feasibility band with those two
components free in [0,1]; passing candidates are exact (total must be 1.0).
When raw harness outputs exist (future instrumentation), shaped/pass/verifier
are recomputed exactly from ``shaped_reward_from_details`` (production code).

Usage:
  python3 scripts/sapo_reward_audit.py --metrics <grpo_step_metrics.jsonl> \
      [--config configs/rl/qwen36_27b_fv_gspo_asi2.json] \
      [--argv-json <launch_config.json>] [--min-step N] [--max-steps N] \
      [--harness-results <file.jsonl>] [--tolerance 1e-4] [--json]
  # pull the live run's metrics from the box daemon in small chunks, then audit:
  python3 scripts/sapo_reward_audit.py --daemon-url http://127.0.0.1:19005/exec \
      --box-path /root/work/software/quantum-gpt/outputs/<run>/grpo_step_metrics.jsonl \
      --pull-out /tmp/grpo_step_metrics.jsonl [same audit flags]

Exit codes: 0 = clean, 1 = internal error, 2 = reward-path violations found.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# ── contract constants (mirror the production wiring; keep in sync with
#    training/grpo_utils.py + training/grpo_trainer.py compose_policy_training_reward) ──
DEFAULT_WEIGHTS = {
    "shaped": 0.45,  # --reward-pass-weight applied to the shaped credit
    "syntax": 0.05,  # --reward-syntax-weight
    "interface": 0.10,  # --reward-interface-weight
    "verifier": 0.10,  # --reward-verifier-weight
    "brevity": 0.05,  # --reward-brevity-weight (research audit P5 2026-08-27: counterweight)
    "hygiene": 0.05,  # --reward-import-hygiene-weight
}
DEFAULT_MODE = "p_dominant"  # --reward-mode
DEFAULT_PASS_MASS = 0.50  # --reward-pass-mass (research memo 2026-08-26 r17)
DEFAULT_SHAPED_MASS = 0.40  # --reward-shaped-mass (research memo 2026-08-26 r17)
DEFAULT_JUDGE_MASS = 0.10  # --reward-judge-mass (calibration-gated, research memo 2026-08-26 r17)
DEFAULT_ADVANTAGE_CLIP = 2.5  # --advantage-clip default
DEFAULT_TOLERANCE = 1e-4  # fp tolerance (recorded values passed float32)

SHAPED_FAIL_TIERS = (0.0, 0.5, 0.9)  # fail -> 0.0 or [0.5, 0.9]


# ── weights resolution ──────────────────────────────────────────────────────


def resolve_weights_from_argv(argv: list[str]) -> dict[str, float]:
    """Parse ``--reward-*-weight`` / ``--reward-*-mass`` / ``--reward-mode`` /
    ``--advantage-clip`` from a launch argv list (launch_config.json ``argv``).
    Any flag absent from argv keeps its documented default."""
    weights = dict(DEFAULT_WEIGHTS)
    cfg = {
        "mode": DEFAULT_MODE,
        "pass_mass": DEFAULT_PASS_MASS,
        "shaped_mass": DEFAULT_SHAPED_MASS,
        "judge_mass": DEFAULT_JUDGE_MASS,
        "clip": DEFAULT_ADVANTAGE_CLIP,
    }
    mapping = {
        "--reward-pass-weight": ("shaped", weights),
        "--reward-syntax-weight": ("syntax", weights),
        "--reward-interface-weight": ("interface", weights),
        "--reward-verifier-weight": ("verifier", weights),
        "--reward-brevity-weight": ("brevity", weights),
        "--reward-import-hygiene-weight": ("hygiene", weights),
        "--reward-mode": ("mode", cfg),
        "--reward-pass-mass": ("pass_mass", cfg),
        "--reward-shaped-mass": ("shaped_mass", cfg),
        "--reward-judge-mass": ("judge_mass", cfg),
        "--advantage-clip": ("clip", cfg),
    }
    i = 0
    while i < len(argv):
        flag = argv[i]
        if flag in mapping and i + 1 < len(argv):
            key, table = mapping[flag]
            try:
                value: float | str = float(argv[i + 1])
            except ValueError:
                value = argv[i + 1]
            table[key] = value
            i += 2
            continue
        i += 1
    weights["total"] = sum(max(0.0, float(w)) for w in weights.values())
    for key, value in cfg.items():
        if isinstance(value, (int, float)):
            weights[key] = float(value)
        else:
            weights[key] = value
    return weights


def resolve_weights_from_config(path: str | Path) -> dict[str, float]:
    """Read the ``training`` section of a config JSON (asi2/asi3 style)."""
    cfg = json.loads(Path(path).read_text(encoding="utf-8"))
    training = cfg.get("training", cfg)
    weights = dict(DEFAULT_WEIGHTS)
    aliases = {
        "shaped": ("reward_pass_weight", "reward_pass_mass"),
        "syntax": "reward_syntax_weight",
        "interface": "reward_interface_weight",
        "verifier": "reward_verifier_weight",
        "brevity": "reward_brevity_weight",
        "hygiene": "reward_import_hygiene_weight",
    }
    for key, names in aliases.items():
        for name in names if isinstance(names, tuple) else (names,):
            if name in training:
                weights[key] = float(training[name])
                break
    weights["total"] = sum(max(0.0, float(w)) for w in weights.values())
    weights["mode"] = str(training.get("reward_mode", DEFAULT_MODE))
    weights["pass_mass"] = float(training.get("reward_pass_mass", DEFAULT_PASS_MASS))
    weights["shaped_mass"] = float(training.get("reward_shaped_mass", DEFAULT_SHAPED_MASS))
    weights["judge_mass"] = float(training.get("reward_judge_mass", DEFAULT_JUDGE_MASS))
    weights["clip"] = float(training.get("advantage_clip", DEFAULT_ADVANTAGE_CLIP))
    return weights


# ── reward composition math (pure python mirror of the production contract) ─


def progress_reward(
    shaped: float,
    syntax: float,
    interface: float,
    verifier: float,
    brevity: float,
    hygiene: float,
    weights: dict[str, float],
) -> float:
    """Weighted executable progress, renormalized by the total weight
    (mirrors compose_policy_training_reward's progress_reward)."""
    total = max(
        sum(
            max(0.0, float(weights.get(k, 0.0)))
            for k in ("shaped", "syntax", "interface", "verifier", "brevity", "hygiene")
        ),
        1e-8,
    )
    return (
        max(0.0, weights["shaped"]) * _clamp01(shaped)
        + max(0.0, weights["syntax"]) * _clamp01(syntax)
        + max(0.0, weights["interface"]) * _clamp01(interface)
        + max(0.0, weights["verifier"]) * _clamp01(verifier)
        + max(0.0, weights["brevity"]) * _clamp01(brevity)
        + max(0.0, weights["hygiene"]) * _clamp01(hygiene)
    ) / total


def compose_total(
    pass_reward: float,
    shaped: float,
    syntax: float,
    interface: float,
    verifier: float,
    brevity: float,
    hygiene: float,
    weights: dict[str, float],
    judge: float | None = None,
) -> float:
    """Compose the recorded total under the launch's reward mode.

    p_dominant with the judge disabled (dim_weights={} -> total_w=0):
        total = clamp01(P + (1-P) * progress_reward)  — mirrors
        blend_comprehensive_reward(..., mode="p_dominant", dim_weights={}).

    comprehensive (2026-08-26 r16 judge wave, judge ENABLED):
        total = clamp01((pass_mass*P + shaped_mass*S + judge_mass*J) / total_mass)
        with judge_mass active when the candidate carries judge_reward and
        renormalized away when it does not — mirrors the trainer's
        blend_comprehensive_reward(..., mode="comprehensive"). J is the
        recorded judge composite (the exact value the blend used)."""
    progress = progress_reward(shaped, syntax, interface, verifier, brevity, hygiene, weights)
    p = _clamp01(pass_reward)
    mode = str(weights.get("mode", DEFAULT_MODE))
    if mode == "comprehensive":
        pass_mass = max(0.0, float(weights.get("pass_mass", DEFAULT_PASS_MASS)))
        shaped_mass = max(0.0, float(weights.get("shaped_mass", DEFAULT_SHAPED_MASS)))
        judge_mass = max(0.0, float(weights.get("judge_mass", DEFAULT_JUDGE_MASS)))
        # 2026-09-01 (ADVERSARIAL-JUDGE lane): EXACT mirror of the blend's
        # structural cap in grpo_utils.blend_comprehensive_reward — the judge
        # mass never exceeds [0,1], the residual (1 - w_P - w_S), or the pass
        # mass, so the recompute stays byte-exact with the recorded totals.
        judge_mass = min(judge_mass, 1.0, max(0.0, 1.0 - pass_mass - shaped_mass), pass_mass)
        if judge is None:
            judge_mass = 0.0  # judge inactive -> masses renormalize over P+S
        j = _clamp01(judge) if judge is not None else 0.0
        total_mass = max(pass_mass + shaped_mass + judge_mass, 1e-8)
        return _clamp01(
            (pass_mass * p + shaped_mass * _clamp01(progress) + judge_mass * j) / total_mass
        )
    if judge is not None:
        # p_dominant with the frozen judge ACTIVE: production blends the judge
        # term into the shaped term with weight w = min(weight_sum, 0.05)
        # (MAX_MODEL_JUDGE_WEIGHT — grpo_utils.blend_comprehensive_reward).
        # The dim weights are not persisted per candidate, so this mirror
        # returns the MAX-judge-weight point; total_band brackets the unknown
        # w in [0, 0.05] around it (2026-09-01 reward-verifier fix).
        j = _clamp01(judge)
        return _clamp01(p + (1.0 - p) * (0.95 * progress + 0.05 * j))
    return _clamp01(p + (1.0 - p) * progress)


def total_band(
    cand: dict,
    weights: dict[str, float],
) -> tuple[float, float]:
    """Feasible [lo, hi] band for a candidate's total_reward when
    interface_reward / import_hygiene_reward are not recorded (free in [0,1]).
    Uses the recorded components; returns exact [x, x] when everything is
    recorded (or the candidate passed — pass pins total to 1.0)."""
    pass_reward = float(cand.get("pass_reward", 0.0) or 0.0)
    shaped = float(cand.get("shaped_reward", 0.0) or 0.0)
    syntax = float(cand.get("syntax_reward", 0.0) or 0.0)
    verifier = float(cand.get("verifier_reward", 0.0) or 0.0)
    brevity = float(cand.get("brevity_reward", 0.0) or 0.0)
    interface = cand.get("interface_reward")
    hygiene = cand.get("import_hygiene_reward")
    # 2026-08-26 (r16 judge wave): the recorded judge composite rides the
    # 3-way blend recompute (exact when present; masses renormalize over
    # pass+shaped when absent, mirroring the trainer).
    judge = cand.get("judge_reward")
    if interface is not None and hygiene is not None:
        if judge is not None and str(weights.get("mode", DEFAULT_MODE)) != "comprehensive":
            # p_dominant with the judge active: the blend's judge weight
            # w = min(weight_sum, 0.05) is not persisted, so bracket it —
            # [judge contributes 0, judge at max weight 0.05]. The judge term
            # is SUBTRACTED from the shaped term (J < S drags the total
            # down), so the band is unordered (2026-09-01 reward-verifier).
            lo = compose_total(
                pass_reward,
                shaped,
                syntax,
                float(interface),
                verifier,
                brevity,
                float(hygiene),
                weights,
                judge=None,
            )
            hi = compose_total(
                pass_reward,
                shaped,
                syntax,
                float(interface),
                verifier,
                brevity,
                float(hygiene),
                weights,
                judge=judge,
            )
            return min(lo, hi), max(lo, hi)
        exact = compose_total(
            pass_reward,
            shaped,
            syntax,
            float(interface),
            verifier,
            brevity,
            float(hygiene),
            weights,
            judge=judge,
        )
        return exact, exact
    if interface is None and hygiene is None:
        lo = compose_total(
            pass_reward, shaped, syntax, 0.0, verifier, brevity, 0.0, weights, judge=judge
        )
        hi = compose_total(
            pass_reward, shaped, syntax, 1.0, verifier, brevity, 1.0, weights, judge=judge
        )
        return lo, hi
    known_interface = float(interface) if interface is not None else 1.0
    known_hygiene = float(hygiene) if hygiene is not None else 1.0
    missing = 1.0 if interface is None else 0.0
    lo = compose_total(
        pass_reward,
        shaped,
        syntax,
        known_interface * (1.0 - missing),
        verifier,
        brevity,
        known_hygiene * (1.0 - missing),
        weights,
        judge=judge,
    )
    hi = compose_total(
        pass_reward,
        shaped,
        syntax,
        known_interface + missing,
        verifier,
        brevity,
        known_hygiene + missing,
        weights,
        judge=judge,
    )
    return lo, hi


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


# Marker set mirroring production training/grpo_utils._has_runtime_failure —
# kept in lockstep (cross-checked by test_runtime_failure_marker_set_matches_production).
_RUNTIME_MARKERS = (
    "SyntaxError:",
    "IndentationError:",
    "TabError:",
    "AttributeError:",
    "ImportError:",
    "ModuleNotFoundError:",
    "NameError:",
    "TypeError:",
    "unsupported operand type",
)


def _has_runtime_failure(details: list[str]) -> bool:
    """True when any detail line carries a runtime-failure (crash) marker.

    A crash zeroes BOTH shaped and verifier reward in production; the audit
    mirrors that rule here (2026-08-26: run-6 exposed a false-positive in the
    details-based verifier recompute that omitted it — 30 candidates flagged
    as verifier mismatches when the recorded 0.0 was the correct crash rule).
    """
    return any(any(marker in detail for marker in _RUNTIME_MARKERS) for detail in (details or []))


# ── harness-level recomputation (production shaped math) ────────────────────


def recompute_shaped_from_details(passed: bool, details: list[str]) -> float:
    """Delegate to the production shaped_reward_from_details so the audit can
    never drift from the contract. Requires the repo venv (torch)."""
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from training.grpo_utils import shaped_reward_from_details
    except ImportError as exc:  # pragma: no cover - env-specific
        raise RuntimeError(
            "cannot import training.grpo_utils (torch missing?); run the audit "
            f"with the repo venv: {exc}"
        ) from exc
    return float(shaped_reward_from_details(bool(passed), list(details or [])))


# ── per-candidate checks ────────────────────────────────────────────────────


def audit_candidate(
    cand: dict,
    weights: dict[str, float],
    harness: dict | None = None,
    tolerance: float = DEFAULT_TOLERANCE,
) -> list[dict]:
    """All reward-path checks for ONE candidate. Returns check records with
    ``ok``, ``check``, ``expected``, ``recorded``, ``detail``. Harness (optional)
    = raw scorer output {"passed": bool, "details": [...]} for exact
    recomputation of shaped/pass/verifier."""
    checks: list[dict] = []
    passed = bool(cand.get("pass"))
    pass_reward = float(cand.get("pass_reward", 0.0) or 0.0)
    shaped = float(cand.get("shaped_reward", 0.0) or 0.0)
    total = float(cand.get("total_reward", 0.0) or 0.0)
    syntax = float(cand.get("syntax_reward", 0.0) or 0.0)
    verifier = float(cand.get("verifier_reward", 0.0) or 0.0)

    # C1: pass flag <-> binary pass_reward
    checks.append(
        _check(
            "pass_flag_vs_pass_reward",
            ok=(passed == (pass_reward > 0.0)) and pass_reward in (0.0, 1.0),
            expected=f"pass={passed} -> pass_reward {1.0 if passed else 0.0}",
            recorded=pass_reward,
        )
    )
    # C2: shaped contract: 1.0 iff pass; fail -> 0.0 or [0.5, 0.9]
    if passed:
        shaped_ok = abs(shaped - 1.0) <= tolerance
        expected_shaped = 1.0
    else:
        shaped_ok = shaped == 0.0 or 0.5 - 1e-12 <= shaped <= 0.9 + 1e-12
        expected_shaped = "0.0 or [0.5, 0.9]"
    checks.append(
        _check(
            "shaped_tier_contract",
            ok=shaped_ok,
            expected=expected_shaped,
            recorded=shaped,
        )
    )
    # C4: syntax is binary
    checks.append(
        _check(
            "syntax_binary",
            ok=syntax in (0.0, 1.0),
            expected="{0.0, 1.0}",
            recorded=syntax,
        )
    )
    # C5: total in [0, 1]
    checks.append(
        _check(
            "total_in_unit_interval",
            ok=0.0 <= total <= 1.0,
            expected="[0, 1]",
            recorded=total,
        )
    )
    # C6: pass pins total to exactly 1.0 (p_dominant, judge disabled); in
    # comprehensive mode with the judge active a passing candidate totals
    # pass_mass + shaped_mass + judge_mass*J (exact when judge_reward is
    # recorded — 2026-08-26 r16 judge wave).
    if passed:
        if str(weights.get("mode", DEFAULT_MODE)) == "comprehensive":
            lo, hi = total_band(cand, weights)
            checks.append(
                _check(
                    "total_composition_on_pass",
                    ok=lo - tolerance <= total <= hi + tolerance,
                    expected=f"[{lo:.6f}, {hi:.6f}] (comprehensive blend)",
                    recorded=total,
                )
            )
        else:
            checks.append(
                _check(
                    "total_exact_on_pass",
                    ok=abs(total - 1.0) <= tolerance,
                    expected=1.0,
                    recorded=total,
                )
            )
    else:
        # C7: failing total must sit in the composition band
        lo, hi = total_band(cand, weights)
        checks.append(
            _check(
                "total_composition_band",
                ok=lo - tolerance <= total <= hi + tolerance,
                expected=f"[{lo:.6f}, {hi:.6f}]",
                recorded=total,
            )
        )
    # C8: n_tokens sane
    n_tokens = cand.get("n_tokens")
    checks.append(
        _check(
            "n_tokens_nonnegative",
            ok=n_tokens is None or (isinstance(n_tokens, (int, float)) and n_tokens >= 0),
            expected=">= 0",
            recorded=n_tokens,
        )
    )
    # H1/H2: raw harness output available -> recompute shaped + pass exactly
    if harness is not None:
        harness_passed = bool(harness.get("passed"))
        checks.append(
            _check(
                "harness_pass_verdict",
                ok=(passed == harness_passed),
                expected=harness_passed,
                recorded=passed,
            )
        )
        recomputed = recompute_shaped_from_details(harness_passed, harness.get("details") or [])
        checks.append(
            _check(
                "harness_shaped_recomputed",
                ok=abs(recomputed - shaped) <= 1e-9,
                expected=recomputed,
                recorded=shaped,
            )
        )
        # verifier: 1.0 on pass; 0.0 on runtime failure (crash rule); else
        # 1 - min(failures, budget)/budget (exact only when the task budget
        # is known via the harness entry). Mirrors build_reward_breakdown.
        budget = harness.get("detail_budget")
        if budget is not None:
            if harness_passed:
                expected_v = 1.0
            elif _has_runtime_failure(harness.get("details") or []):
                expected_v = 0.0
            else:
                failures = max(1, len(harness.get("details") or []))
                expected_v = max(
                    0.0, 1.0 - min(failures, max(1, int(budget))) / max(1, int(budget))
                )
            checks.append(
                _check(
                    "harness_verifier_recomputed",
                    ok=abs(expected_v - verifier) <= 1e-9,
                    expected=expected_v,
                    recorded=verifier,
                    detail="crash -> 0.0 rule applied when runtime markers present",
                )
            )
    # H4-H6: full eval_results.jsonl schema row (r9 wave, G1 resolved) — the
    # trainer persists the components it actually used, so the composition
    # band check becomes an EXACT composition check.
    if harness is not None and all(
        harness.get(key) is not None
        for key in ("syntax", "interface", "verifier", "import_hygiene")
    ):
        row_syntax = float(harness["syntax"])
        row_interface = float(harness["interface"])
        row_verifier = float(harness["verifier"])
        row_hygiene = float(harness["import_hygiene"])
        checks.append(
            _check(
                "component_syntax_vs_row",
                ok=abs(row_syntax - syntax) <= 1e-9,
                expected=row_syntax,
                recorded=syntax,
            )
        )
        checks.append(
            _check(
                "component_verifier_vs_row",
                ok=abs(row_verifier - verifier) <= 1e-9,
                expected=row_verifier,
                recorded=verifier,
            )
        )
        row_brevity = float(harness.get("brevity", harness.get("brevity_reward", 0.0)) or 0.0)
        judge = cand.get("judge_reward")
        if judge is not None:
            # judge-active candidate: the exact point is unknowable (the
            # blend's judge weight w is not persisted) — the recorded total
            # must sit in the [w=0, w=0.05] band (2026-09-01 reward-verifier).
            lo, hi = total_band(cand, weights)
            checks.append(
                _check(
                    "total_exact_composition",
                    ok=lo - 1e-9 <= total <= hi + 1e-9,
                    expected=f"[{lo:.9f}, {hi:.9f}] (judge-active band, w in [0, 0.05])",
                    recorded=total,
                    detail="all six executable components persisted; judge weight "
                    "bracketed (dim weights not persisted per candidate)",
                )
            )
        else:
            expected_total = compose_total(
                pass_reward,
                shaped,
                row_syntax,
                row_interface,
                row_verifier,
                row_brevity,
                row_hygiene,
                weights,
            )
            checks.append(
                _check(
                    "total_exact_composition",
                    ok=abs(expected_total - total) <= 1e-9,
                    expected=expected_total,
                    recorded=total,
                    detail="all six executable components persisted; exact composition",
                )
            )
    return checks


def _check(check: str, *, ok: bool, expected, recorded, detail: str = "") -> dict:
    return {
        "check": check,
        "ok": bool(ok),
        "expected": expected,
        "recorded": recorded,
        "detail": detail,
    }


# ── group-level checks (advantages + stats) ─────────────────────────────────


def audit_step(
    record: dict,
    weights: dict[str, float],
    harness_details: list[dict] | None = None,
    tolerance: float = DEFAULT_TOLERANCE,
) -> dict:
    """Audit one step record. Returns {ok, errors, gaps, mean_other, raw_loo,
    scale, n_candidates, step}."""
    result: dict = {
        "step": int(record.get("step", 0)),
        "task": str(record.get("task", "?")),
        "ok": True,
        "errors": [],
        "gaps": [],
        "n_candidates": 0,
    }
    rollout = record.get("rollout_rewards")
    if not isinstance(rollout, list) or not rollout:
        result["gaps"].append(
            {"gap": "no_rollout_rewards", "detail": "record carries no per-candidate rewards"}
        )
        return result

    harness_by_index: dict[tuple[int, int], dict] = {}
    if harness_details:
        for entry in harness_details:
            key = (int(entry.get("step", -1)), int(entry.get("index", -1)))
            harness_by_index[key] = entry

    rewards = [float(c.get("total_reward", 0.0) or 0.0) for c in rollout]
    g = len(rewards)
    result["n_candidates"] = g
    result["scale"] = None
    scale = record.get("advantage_scale")
    if scale is not None:
        try:
            result["scale"] = float(scale)
        except (TypeError, ValueError):
            result["gaps"].append({"gap": "bad_advantage_scale", "detail": str(scale)})
            scale = None

    # per-candidate reward checks
    exact_records: list[dict] = []
    for i, c in enumerate(rollout):
        harness = None
        if (int(record.get("step", 0)), i) in harness_by_index:
            harness = harness_by_index[(int(record.get("step", 0)), i)]
        full_schema = bool(
            harness is not None
            and all(
                harness.get(k) is not None
                for k in ("syntax", "interface", "verifier", "import_hygiene")
            )
        )
        for check in audit_candidate(c, weights, harness=harness, tolerance=tolerance):
            if not check["ok"]:
                check = dict(check)
                check["candidate"] = i
                check["step"] = int(record.get("step", 0))
                result["errors"].append(check)
                result["ok"] = False
            elif full_schema and check["check"].startswith(
                ("harness_", "component_", "total_exact_")
            ):
                exact_records.append(dict(check, candidate=i, step=int(record.get("step", 0))))
    if exact_records:
        result["exact"] = exact_records

    # advantage normalization: LOO mean_other -> raw LOO -> /scale -> clamp
    group_total = sum(rewards)
    mean_other = [(group_total - r) / float(g - 1) if g > 1 else 0.0 for r in rewards]
    # 2026-09-01 (manager, runtime-gate): plain zip — strict=False is the
    # py3.10-only keyword form; this CLI runs under the py3.9 .venv. The
    # lists are same-length by construction (both derive from `rewards`).
    raw_loo = [r - m for r, m in zip(rewards, mean_other)]  # noqa: B905
    result["mean_other"] = mean_other
    result["raw_loo"] = raw_loo
    clip = float(weights.get("clip", DEFAULT_ADVANTAGE_CLIP))
    if g == 1:
        result["gaps"].append({"gap": "group_size_1", "detail": "LOO advantages undefined for G=1"})
    for i, c in enumerate(rollout):
        recorded_adv = c.get("advantage")
        if recorded_adv is None:
            continue
        recorded_adv = float(recorded_adv)
        if scale is None:
            result["gaps"].append(
                {
                    "gap": "advantage_scale_missing",
                    "candidate": i,
                    "detail": "recorded advantage present but step advantage_scale absent "
                    "(shared_mad scale unverifiable); recorded=" + str(recorded_adv),
                }
            )
            continue
        if g == 1:
            continue
        recomputed = max(-clip, min(clip, raw_loo[i] / float(scale)))
        if abs(recomputed - recorded_adv) > tolerance:
            result["errors"].append(
                {
                    "check": "advantage_recomputed",
                    "candidate": i,
                    "step": int(record.get("step", 0)),
                    "ok": False,
                    "expected": recomputed,
                    "recorded": recorded_adv,
                    "detail": f"mean_other={mean_other[i]:.8f} raw_loo={raw_loo[i]:.8f} "
                    f"scale={float(scale):.8f} clip=+-{clip}",
                }
            )
            result["ok"] = False

    # loo_advantage_rms identity (recorded after clamp)
    if "loo_advantage_rms" in record:
        recorded_rms = float(record["loo_advantage_rms"])
        recomputed_rms = (
            math.sqrt(sum(v * v for v in raw_loo) / g) / float(scale) if scale else None
        )
        if recomputed_rms is not None:
            clamped = [max(-clip, min(clip, v / float(scale))) for v in raw_loo]
            recomputed_rms = math.sqrt(sum(v * v for v in clamped) / g)
            if abs(recomputed_rms - recorded_rms) > tolerance:
                result["errors"].append(
                    {
                        "check": "loo_advantage_rms",
                        "ok": False,
                        "expected": recomputed_rms,
                        "recorded": recorded_rms,
                        "detail": "RMS of clamped scaled LOO advantages",
                    }
                )
                result["ok"] = False

    # group statistics identities
    stats = {
        "pass_rate": sum(1.0 for c in rollout if bool(c.get("pass"))) / g,
        "mean_reward": sum(rewards) / g,
        "mean_shaped_reward": sum(float(c.get("shaped_reward", 0.0) or 0.0) for c in rollout) / g,
        "reward_std": math.sqrt(sum((r - sum(rewards) / g) ** 2 for r in rewards) / g),
    }
    for key, recomputed in stats.items():
        recorded = record.get(key)
        if recorded is None:
            continue
        if abs(float(recorded) - recomputed) > tolerance:
            result["errors"].append(
                {
                    "check": key,
                    "ok": False,
                    "expected": recomputed,
                    "recorded": float(recorded),
                    "detail": "group statistic does not match the recorded rollout_rewards",
                }
            )
            result["ok"] = False
    return result


# ── file-level orchestration ────────────────────────────────────────────────


def load_step_records(path: str | Path) -> tuple[list[dict], int]:
    """Load the metrics JSONL; returns (records, corrupt_lines)."""
    records: list[dict] = []
    corrupt = 0
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            corrupt += 1
    return records, corrupt


def audit_metrics_file(
    path: str | Path,
    weights: dict[str, float],
    harness_details: list[dict] | None = None,
    min_step: int = 0,
    max_steps: int | None = None,
    tolerance: float = DEFAULT_TOLERANCE,
) -> dict:
    """Audit a metrics JSONL file; returns the aggregate report."""
    records, corrupt = load_step_records(path)
    steps = [r for r in records if int(r.get("step", 0)) >= min_step]
    if max_steps:
        steps = steps[:max_steps]
    step_results = [audit_step(r, weights, harness_details, tolerance) for r in steps]
    errors = [e for sr in step_results for e in sr["errors"]]
    gaps = [gr for sr in step_results for gr in sr["gaps"]]
    return {
        "ok": not errors,
        "steps_total": len(records),
        "steps_audited": len(steps),
        "lines_skipped": corrupt,
        "candidates_audited": sum(sr["n_candidates"] for sr in step_results),
        "errors": len(errors),
        "error_records": errors,
        "gaps": gaps,
        "per_step": step_results,
    }


# ── daemon pull (small chunks, read-only on the box) ────────────────────────


def _daemon_exec(url: str, command: str) -> str:
    req = urllib.request.Request(
        url,
        data=json.dumps({"command": command}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        payload = json.loads(resp.read().decode())
    if not payload.get("ok"):
        raise RuntimeError(f"daemon exec failed: {payload.get('error')}")
    return str(payload.get("output", ""))


def pull_metrics_via_daemon(
    daemon_url: str,
    box_path: str,
    out_path: str | Path,
    chunk_bytes: int = 3000,
    max_attempts: int = 5,
) -> int:
    """Copy grpo_step_metrics.jsonl from the box in small byte chunks.

    The daemon /exec capture is lossy in two ways: it wraps long streams by
    inserting newlines mid-token (~120 cols) and it drops bytes beyond a few
    KB per call (measured 2026-08-25: 3072 bytes decode intact, 3500 loses
    data). Transport is therefore base64 chunks of <=3000 raw bytes with the
    box-side python emitting one base64 line; newlines inserted by the
    capture are stripped, the chunk is verified by length, and short chunks
    are retried. Returns bytes written.
    """
    import base64

    size = int(_daemon_exec(daemon_url, f"wc -c < {box_path} 2>/dev/null").strip().splitlines()[-1])
    if size <= 0:
        raise RuntimeError(f"box file {box_path} has size {size}")
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with out.open("wb") as handle:
        while written < size:
            chunk = min(chunk_bytes, size - written)
            data = None
            for _attempt in range(max_attempts):
                probe = (
                    f"import base64;d=open('{box_path}','rb').read()[{written}:{written + chunk}];"
                    "print(base64.b64encode(d).decode())"
                )
                block = _daemon_exec(daemon_url, f'python3 -c "{probe}"')
                b64 = block.replace("\n", "").replace("\r", "")
                try:
                    decoded = base64.b64decode(b64, validate=True)
                except Exception:  # noqa: BLE001 - truncated mid-chunk
                    decoded = b""
                if len(decoded) == chunk:
                    data = decoded
                    break
            if data is None:
                raise RuntimeError(
                    f"daemon pull: could not fetch bytes [{written}:{written + chunk}] "
                    f"of {size} after {max_attempts} attempts (capture lossy)"
                )
            handle.write(data)
            written += len(data)
    if written != size:
        raise RuntimeError(f"daemon pull size mismatch: expected {size} bytes, wrote {written}")
    return written


# ── CLI ─────────────────────────────────────────────────────────────────────


def _fmt_check(check: dict) -> str:
    return (
        f"[{check['step']}/cand {check['candidate']}] {check['check']}: "
        f"expected={check['expected']!r} recorded={check['recorded']!r} "
        f"{check.get('detail', '')}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SAPO reward-path audit")
    parser.add_argument("--metrics", type=str, help="local grpo_step_metrics.jsonl")
    parser.add_argument("--config", type=str, help="config JSON (weights/masses)")
    parser.add_argument(
        "--argv-json", type=str, help="launch_config.json (argv weights win over config)"
    )
    parser.add_argument(
        "--harness-results",
        type=str,
        help="JSONL of {step, index, passed, details[, detail_budget]} — "
        "live source: the trainer's run-dir eval_results.jsonl "
        "(2026-08-25, verifier G1)",
    )
    parser.add_argument("--min-step", type=int, default=0)
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--tolerance", type=float, default=DEFAULT_TOLERANCE)
    parser.add_argument("--json", action="store_true", help="emit report as JSON")
    parser.add_argument(
        "--daemon-url",
        type=str,
        default=None,
        help="pull --box-path from this daemon /exec before auditing",
    )
    parser.add_argument(
        "--box-path", type=str, default=None, help="box-side metrics path (with --daemon-url)"
    )
    parser.add_argument(
        "--pull-out",
        type=str,
        default=None,
        help="local file for the daemon pull (default --metrics)",
    )
    args = parser.parse_args(argv)

    weights = dict(DEFAULT_WEIGHTS)
    weights["total"] = sum(weights.values())
    weights.update(
        mode=DEFAULT_MODE,
        pass_mass=DEFAULT_PASS_MASS,
        shaped_mass=DEFAULT_SHAPED_MASS,
        judge_mass=DEFAULT_JUDGE_MASS,
        clip=DEFAULT_ADVANTAGE_CLIP,
    )
    if args.config:
        weights.update(resolve_weights_from_config(args.config))
    if args.argv_json:
        launch = json.loads(Path(args.argv_json).read_text(encoding="utf-8"))
        weights.update(resolve_weights_from_argv(launch.get("argv", [])))

    metrics_path = args.metrics
    if args.daemon_url:
        if not args.box_path:
            parser.error("--box-path required with --daemon-url")
        pull_out = args.pull_out or args.metrics
        if not pull_out:
            parser.error("--metrics or --pull-out required with --daemon-url")
        written = pull_metrics_via_daemon(args.daemon_url, args.box_path, pull_out)
        print(f"[audit] pulled {written} bytes from {args.box_path} -> {pull_out}", file=sys.stderr)
        metrics_path = pull_out
    if not metrics_path or not Path(metrics_path).exists():
        parser.error("--metrics file required (or --daemon-url pull)")

    harness = []
    if args.harness_results:
        harness, corrupt = load_step_records(args.harness_results)
        if corrupt:
            print(
                f"[audit] WARNING: {corrupt} corrupt harness-result lines skipped", file=sys.stderr
            )

    report = audit_metrics_file(
        metrics_path,
        weights,
        harness,
        min_step=args.min_step,
        max_steps=args.max_steps,
        tolerance=args.tolerance,
    )
    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        summary = (
            f"[audit] steps {report['steps_audited']}/{report['steps_total']} "
            f"candidates {report['candidates_audited']} "
            f"violations {report['errors']} gaps {len(report['gaps'])}"
        )
        print(summary)
        for check in report["error_records"]:
            print("VIOLATION " + _fmt_check(check))
        for gap in report["gaps"]:
            print("GAP " + json.dumps(gap, default=str))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())

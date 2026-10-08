"""TDD (coverage lane, PASS 16): doubly-robust (DR) loss math identities —
compute_dr_pair_loss + compute_dr_variance_correction recomputed from the
documented closed forms (arXiv:2506.01183, paper.md §2 + §DPO), NOT from the
implementation under audit.

The honest-record pattern: hand-chosen rewards/log-probs/advantages, expected
values computed in-test with independent torch expressions. If an identity
ever fails it is a REAL training-math bug; if it passes it is pinned.

Pinned identities:

  * variance correction:  psi * E[ (r - 1) * A ],  r = exp(clamp(lp - old, ±clip))
    with linear psi warmup over dr_psi_warmup_steps;
  * pair loss:            weight * softplus(-beta * ((lp[c]-old[c]) - (lp[r]-old[r])))
    over the mined (chosen, rejected) pair with reward gap >= min_gap and
    distinct codes;
  * all no-op paths (no methods, non-DR method, psi=0, weight<=0, no pair,
    non-finite) return a ZERO scalar tensor + info defaults — the trainer
    must never inject NaN/None into the total loss.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.grpo_trainer import (  # noqa: E402
    compute_dr_pair_loss,
    compute_dr_variance_correction,
)

# Honest group fixture (from the step-record audit pattern):
#   r = [0.4, 0.3, 0.0, 0.5] -> A = [0.2666667, 0.0, -0.8, 0.5333333]
ADVANTAGES = torch.tensor([2.0 / 7.5, 0.0, -0.8, 0.8 / 1.5])
CLIP = 2.5
PSI = 0.5
WEIGHT = 0.3
BETA = 0.07


class FakeResearchMethod:
    """Stand-in for a loaded research-method plugin (method_id +
    extra_run_config are the only surface the trainer touches)."""

    def __init__(self, method_id: str, cfg: dict) -> None:
        self.method_id = method_id
        self._cfg = cfg

    def extra_run_config(self) -> dict:
        return {"doubly_robust_quantum_grpo": self._cfg}


def _dr_method(cfg: dict) -> list:
    return [FakeResearchMethod("doubly_robust_quantum_grpo", cfg)]


def _non_dr_method() -> list:
    return [FakeResearchMethod("clause_aware_verifier_reward", {})]


def _default_cfg() -> dict:
    return {
        "dr_dpo_beta": BETA,
        "dr_pair_min_reward_gap": 0.4,
        "dr_pair_max_per_step": 1,
        "dr_pair_loss_weight": WEIGHT,
        "dr_psi_init": PSI,
        "dr_psi_warmup_steps": 0,
    }


def _expected_variance_correction(
    log_probs: torch.Tensor, old_log_probs: torch.Tensor, advantages: torch.Tensor, psi: float
) -> torch.Tensor:
    """Independent recomputation of the documented closed form."""
    log_ratio = (log_probs - old_log_probs.detach()).clamp(-CLIP, CLIP)
    ppo_ratio = torch.exp(log_ratio)
    return psi * ((ppo_ratio - 1.0) * advantages.detach()).mean()


# ---------------------------------------------------------------------------
# compute_dr_variance_correction — closed-form identity
# ---------------------------------------------------------------------------


def test_variance_correction_matches_closed_form() -> None:
    log_probs = torch.tensor([0.1, -0.2, 0.05, 0.3], requires_grad=False)
    old_log_probs = torch.tensor([0.0, 0.0, 0.0, 0.0])
    correction, info = compute_dr_variance_correction(
        research_methods=_dr_method(_default_cfg()),
        log_probs=log_probs,
        old_log_probs=old_log_probs,
        advantages=ADVANTAGES,
        ratio_clip_log_delta=CLIP,
    )
    expected = _expected_variance_correction(log_probs, old_log_probs, ADVANTAGES, PSI)
    assert torch.allclose(correction, expected, atol=1e-6)
    assert info["dr_psi"] == PSI
    assert info["dr_psi_init"] == PSI
    assert info["dr_variance_correction_value"] == pytest.approx(float(correction.item()))
    # the correction is a scalar, finite, on the same device/dtype family
    assert correction.ndim == 0
    assert torch.isfinite(correction)


def test_variance_correction_clipping_applies_before_ratio() -> None:
    """Ratios are clamped to exp(±ratio_clip_log_delta) — a wild ratio must
    not dominate the correction."""
    log_probs = torch.tensor([10.0, 0.0, 0.0, 0.0])  # e^10 >> e^2.5
    old_log_probs = torch.tensor([0.0, 0.0, 0.0, 0.0])
    correction, _info = compute_dr_variance_correction(
        research_methods=_dr_method(_default_cfg()),
        log_probs=log_probs,
        old_log_probs=old_log_probs,
        advantages=ADVANTAGES,
        ratio_clip_log_delta=CLIP,
    )
    expected = _expected_variance_correction(
        torch.clamp(log_probs, -CLIP, CLIP), old_log_probs, ADVANTAGES, PSI
    )
    assert torch.allclose(correction, expected, atol=1e-6)


def test_variance_correction_warmup_linear_ramp() -> None:
    cfg = _default_cfg()
    cfg["dr_psi_warmup_steps"] = 10
    log_probs = torch.tensor([0.1, -0.2, 0.05, 0.3])
    old_log_probs = torch.tensor([0.0, 0.0, 0.0, 0.0])
    # step 4 of 10: psi = 0.5 * 4/10 = 0.2
    correction, info = compute_dr_variance_correction(
        research_methods=_dr_method(cfg),
        log_probs=log_probs,
        old_log_probs=old_log_probs,
        advantages=ADVANTAGES,
        ratio_clip_log_delta=CLIP,
        current_step=4,
    )
    assert info["dr_psi"] == pytest.approx(0.2)
    assert info["dr_psi_warmup_steps"] == 10
    assert info["dr_psi_current_step"] == 4
    expected = _expected_variance_correction(log_probs, old_log_probs, ADVANTAGES, 0.2)
    assert torch.allclose(correction, expected, atol=1e-6)
    # after warmup (step >= 10) psi holds at psi_init
    _c2, info2 = compute_dr_variance_correction(
        research_methods=_dr_method(cfg),
        log_probs=log_probs,
        old_log_probs=old_log_probs,
        advantages=ADVANTAGES,
        ratio_clip_log_delta=CLIP,
        current_step=10,
    )
    assert info2["dr_psi"] == pytest.approx(PSI)


def test_variance_correction_warmup_step_zero_is_zero() -> None:
    cfg = _default_cfg()
    cfg["dr_psi_warmup_steps"] = 10
    correction, info = compute_dr_variance_correction(
        research_methods=_dr_method(cfg),
        log_probs=torch.tensor([0.1, -0.2, 0.05, 0.3]),
        old_log_probs=torch.tensor([0.0, 0.0, 0.0, 0.0]),
        advantages=ADVANTAGES,
        ratio_clip_log_delta=CLIP,
        current_step=0,
    )
    assert float(correction) == 0.0
    assert info["dr_psi"] == 0.0


def test_variance_correction_psi_zero_returns_zero() -> None:
    cfg = _default_cfg()
    cfg["dr_psi_init"] = 0.0
    correction, info = compute_dr_variance_correction(
        research_methods=_dr_method(cfg),
        log_probs=torch.tensor([0.1, -0.2, 0.05, 0.3]),
        old_log_probs=torch.tensor([0.0, 0.0, 0.0, 0.0]),
        advantages=ADVANTAGES,
        ratio_clip_log_delta=CLIP,
    )
    assert float(correction) == 0.0
    assert info["dr_psi"] == 0.0
    assert info["dr_variance_correction_value"] == 0.0


def test_variance_correction_no_methods_returns_zero() -> None:
    correction, info = compute_dr_variance_correction(
        research_methods=[],
        log_probs=torch.tensor([0.1, -0.2, 0.05, 0.3]),
        old_log_probs=torch.tensor([0.0, 0.0, 0.0, 0.0]),
        advantages=ADVANTAGES,
        ratio_clip_log_delta=CLIP,
    )
    assert float(correction) == 0.0
    assert info["dr_psi"] == 0.0


def test_variance_correction_none_tensors_no_methods_returns_zero_tensor() -> None:
    """log_probs=None (no rollout tensors at all) with no methods must still
    return a usable ZERO scalar tensor — the trainer never receives None."""
    correction, info = compute_dr_variance_correction(
        research_methods=[],
        log_probs=None,
        old_log_probs=None,
        advantages=None,
        ratio_clip_log_delta=CLIP,
    )
    assert correction is not None
    assert float(correction) == 0.0
    assert info["dr_psi"] == 0.0
    assert info["dr_variance_correction_value"] == 0.0


def test_variance_correction_non_dr_method_returns_zero() -> None:
    correction, _info = compute_dr_variance_correction(
        research_methods=_non_dr_method(),
        log_probs=torch.tensor([0.1, -0.2, 0.05, 0.3]),
        old_log_probs=torch.tensor([0.0, 0.0, 0.0, 0.0]),
        advantages=ADVANTAGES,
        ratio_clip_log_delta=CLIP,
    )
    assert float(correction) == 0.0


def test_variance_correction_non_finite_fails_closed_to_zero() -> None:
    """NaN must never enter the total loss — the function returns a zero
    tensor and records 0.0."""
    log_probs = torch.tensor([float("nan"), 0.0, 0.0, 0.0])
    correction, info = compute_dr_variance_correction(
        research_methods=_dr_method(_default_cfg()),
        log_probs=log_probs,
        old_log_probs=torch.tensor([0.0, 0.0, 0.0, 0.0]),
        advantages=ADVANTAGES,
        ratio_clip_log_delta=CLIP,
    )
    assert float(correction) == 0.0
    assert info["dr_variance_correction_value"] == 0.0


# ---------------------------------------------------------------------------
# compute_dr_pair_loss — closed-form identity
# ---------------------------------------------------------------------------


def test_pair_loss_matches_dpo_closed_form() -> None:
    """chosen=idx0 (reward 0.5), rejected=idx1 (reward 0.0), gap 0.5 >= 0.4.
    loss = weight * softplus(-beta * ((lp[0]-old[0]) - (lp[1]-old[1])))."""
    rewards = torch.tensor([0.5, 0.0, 0.3, 0.2])
    codes = ["cand_a", "cand_b", "cand_c", "cand_d"]
    current = [torch.tensor(v) for v in (0.1, -0.1, 0.05, 0.0)]
    old = [torch.tensor(0.0) for _ in range(4)]

    loss, info = compute_dr_pair_loss(
        research_methods=_dr_method(_default_cfg()),
        rewards=rewards,
        codes=codes,
        current_log_probs=current,
        old_log_probs=old,
    )
    assert info["dr_pair_mined"] is True
    assert info["dr_pair_reward_gap"] == pytest.approx(0.5)
    assert info["dr_pair_loss_weight"] == WEIGHT
    expected_pair = torch.nn.functional.softplus(torch.tensor(-BETA * ((0.1 - 0.0) - (-0.1 - 0.0))))
    expected = WEIGHT * expected_pair
    assert torch.allclose(loss, expected, atol=1e-6)
    assert info["dr_pair_loss_value"] == pytest.approx(float(expected_pair.item()))
    assert float(loss) > 0.0


def test_pair_loss_has_gradient_on_current_log_probs() -> None:
    rewards = torch.tensor([0.5, 0.0, 0.3, 0.2])
    current = [torch.tensor(v, requires_grad=True) for v in (0.1, -0.1, 0.05, 0.0)]
    old = [torch.tensor(0.0) for _ in range(4)]
    loss, _info = compute_dr_pair_loss(
        research_methods=_dr_method(_default_cfg()),
        rewards=rewards,
        codes=["a", "b", "c", "d"],
        current_log_probs=current,
        old_log_probs=old,
    )
    assert loss.requires_grad is True
    loss.backward()
    assert current[0].grad is not None and current[1].grad is not None
    assert torch.isfinite(current[0].grad) and torch.isfinite(current[1].grad)


def test_pair_loss_no_pair_when_reward_gap_below_min() -> None:
    rewards = torch.tensor([0.5, 0.3, 0.4, 0.4])  # gap 0.2 < 0.4
    current = [torch.tensor(0.1) for _ in range(4)]
    old = [torch.tensor(0.0) for _ in range(4)]
    loss, info = compute_dr_pair_loss(
        research_methods=_dr_method(_default_cfg()),
        rewards=rewards,
        codes=["a", "b", "c", "d"],
        current_log_probs=current,
        old_log_probs=old,
    )
    assert float(loss) == 0.0
    assert info["dr_pair_mined"] is False
    assert info["dr_pair_loss_value"] == 0.0


def test_pair_loss_no_pair_when_identical_codes() -> None:
    rewards = torch.tensor([0.5, 0.0, 0.3, 0.2])
    codes = ["same_code", "same_code", "c", "d"]  # chosen and rejected identical
    current = [torch.tensor(0.1) for _ in range(4)]
    old = [torch.tensor(0.0) for _ in range(4)]
    loss, info = compute_dr_pair_loss(
        research_methods=_dr_method(_default_cfg()),
        rewards=rewards,
        codes=codes,
        current_log_probs=current,
        old_log_probs=old,
    )
    assert float(loss) == 0.0
    assert info["dr_pair_mined"] is False


def test_pair_loss_zero_weight_is_noop() -> None:
    cfg = _default_cfg()
    cfg["dr_pair_loss_weight"] = 0.0
    rewards = torch.tensor([0.5, 0.0, 0.3, 0.2])
    current = [torch.tensor(0.1) for _ in range(4)]
    old = [torch.tensor(0.0) for _ in range(4)]
    loss, info = compute_dr_pair_loss(
        research_methods=_dr_method(cfg),
        rewards=rewards,
        codes=["a", "b", "c", "d"],
        current_log_probs=current,
        old_log_probs=old,
    )
    assert float(loss) == 0.0
    assert info["dr_pair_loss_weight"] == 0.0


def test_pair_loss_no_methods_returns_zero() -> None:
    rewards = torch.tensor([0.5, 0.0, 0.3, 0.2])
    loss, info = compute_dr_pair_loss(
        research_methods=[],
        rewards=rewards,
        codes=["a", "b", "c", "d"],
        current_log_probs=[torch.tensor(0.1) for _ in range(4)],
        old_log_probs=[torch.tensor(0.0) for _ in range(4)],
    )
    assert float(loss) == 0.0
    assert info["dr_pair_mined"] is False


def test_pair_loss_none_rewards_no_methods_returns_zero_tensor() -> None:
    """rewards=None (no rollout tensors at all) with no methods must still
    return a usable ZERO scalar tensor — the trainer never receives None."""
    loss, info = compute_dr_pair_loss(
        research_methods=[],
        rewards=None,
        codes=[],
        current_log_probs=[],
        old_log_probs=[],
    )
    assert loss is not None
    assert float(loss) == 0.0
    assert info["dr_pair_mined"] is False


def test_pair_loss_none_rewards_non_dr_method_returns_zero_tensor() -> None:
    loss, info = compute_dr_pair_loss(
        research_methods=_non_dr_method(),
        rewards=None,
        codes=[],
        current_log_probs=[],
        old_log_probs=[],
    )
    assert loss is not None
    assert float(loss) == 0.0
    assert info["dr_pair_mined"] is False


def test_pair_loss_non_dr_method_returns_zero() -> None:
    rewards = torch.tensor([0.5, 0.0, 0.3, 0.2])
    loss, _info = compute_dr_pair_loss(
        research_methods=_non_dr_method(),
        rewards=rewards,
        codes=["a", "b", "c", "d"],
        current_log_probs=[torch.tensor(0.1) for _ in range(4)],
        old_log_probs=[torch.tensor(0.0) for _ in range(4)],
    )
    assert float(loss) == 0.0


def test_pair_loss_non_finite_fails_closed_to_zero() -> None:
    rewards = torch.tensor([0.5, 0.0, 0.3, 0.2])
    current = [torch.tensor(float("nan")) for _ in range(4)]
    old = [torch.tensor(0.0) for _ in range(4)]
    loss, info = compute_dr_pair_loss(
        research_methods=_dr_method(_default_cfg()),
        rewards=rewards,
        codes=["a", "b", "c", "d"],
        current_log_probs=current,
        old_log_probs=old,
    )
    assert float(loss) == 0.0
    assert info["dr_pair_loss_value"] == 0.0


def test_pair_loss_plugin_load_failure_fails_closed_to_zero(monkeypatch) -> None:
    """The plugin is lazily loaded from research/papers — if it cannot be
    located the pair loss must be a ZERO scalar, never a crash or None."""
    import importlib.util as _ilu

    monkeypatch.setattr(_ilu, "spec_from_file_location", lambda *a, **k: None)
    rewards = torch.tensor([0.5, 0.0, 0.3, 0.2])
    loss, info = compute_dr_pair_loss(
        research_methods=_dr_method(_default_cfg()),
        rewards=rewards,
        codes=["a", "b", "c", "d"],
        current_log_probs=[torch.tensor(0.1) for _ in range(4)],
        old_log_probs=[torch.tensor(0.0) for _ in range(4)],
    )
    assert float(loss) == 0.0
    assert info["dr_pair_mined"] is False
    assert info["dr_pair_loss_value"] == 0.0


def test_pair_loss_plugin_exec_failure_fails_closed_to_zero(monkeypatch) -> None:
    """A plugin module that raises AT EXEC must also fail closed to zero (and
    be removed from sys.modules so a later retry can re-import)."""
    import importlib.util as _ilu

    real_spec = _ilu.spec_from_file_location

    def _spec_with_failing_exec(*a, **k):
        spec = real_spec(*a, **k)
        assert spec.loader is not None
        spec.loader.exec_module = lambda mod: (_ for _ in ()).throw(RuntimeError("exec boom"))
        return spec

    monkeypatch.setattr(_ilu, "spec_from_file_location", _spec_with_failing_exec)
    rewards = torch.tensor([0.5, 0.0, 0.3, 0.2])
    loss, info = compute_dr_pair_loss(
        research_methods=_dr_method(_default_cfg()),
        rewards=rewards,
        codes=["a", "b", "c", "d"],
        current_log_probs=[torch.tensor(0.1) for _ in range(4)],
        old_log_probs=[torch.tensor(0.0) for _ in range(4)],
    )
    assert float(loss) == 0.0
    assert info["dr_pair_mined"] is False
    assert "dr_pair_loss_mod" not in sys.modules  # popped on exec failure


def test_variance_correction_plugin_exec_failure_falls_back_inline(monkeypatch) -> None:
    """A plugin that raises AT EXEC is popped from sys.modules and the
    trainer falls back to the inline math (same closed form)."""
    import importlib.util as _ilu

    real_spec = _ilu.spec_from_file_location

    def _spec_with_failing_exec(*a, **k):
        spec = real_spec(*a, **k)
        assert spec.loader is not None
        spec.loader.exec_module = lambda mod: (_ for _ in ()).throw(RuntimeError("exec boom"))
        return spec

    monkeypatch.setattr(_ilu, "spec_from_file_location", _spec_with_failing_exec)
    log_probs = torch.tensor([0.1, -0.2, 0.05, 0.3])
    old_log_probs = torch.tensor([0.0, 0.0, 0.0, 0.0])
    correction, info = compute_dr_variance_correction(
        research_methods=_dr_method(_default_cfg()),
        log_probs=log_probs,
        old_log_probs=old_log_probs,
        advantages=ADVANTAGES,
        ratio_clip_log_delta=CLIP,
    )
    expected = _expected_variance_correction(log_probs, old_log_probs, ADVANTAGES, PSI)
    assert torch.allclose(correction, expected, atol=1e-6)
    assert info["dr_variance_correction_value"] == pytest.approx(float(correction.item()))
    assert "dr_pair_loss_mod_v2" not in sys.modules  # popped on exec failure


def test_variance_correction_inline_fallback_matches_closed_form(monkeypatch) -> None:
    """When the plugin helper is unimportable the trainer falls back to
    inline math — the fallback must satisfy the SAME closed form."""
    import importlib.util as _ilu

    monkeypatch.setattr(_ilu, "spec_from_file_location", lambda *a, **k: None)
    log_probs = torch.tensor([0.1, -0.2, 0.05, 0.3])
    old_log_probs = torch.tensor([0.0, 0.0, 0.0, 0.0])
    correction, info = compute_dr_variance_correction(
        research_methods=_dr_method(_default_cfg()),
        log_probs=log_probs,
        old_log_probs=old_log_probs,
        advantages=ADVANTAGES,
        ratio_clip_log_delta=CLIP,
    )
    expected = _expected_variance_correction(log_probs, old_log_probs, ADVANTAGES, PSI)
    assert torch.allclose(correction, expected, atol=1e-6)
    assert info["dr_psi"] == PSI
    assert info["dr_variance_correction_value"] == pytest.approx(float(correction.item()))


def test_variance_correction_inline_fallback_non_finite_fails_closed(monkeypatch) -> None:
    """The inline fallback's NaN guard must also fail closed to zero."""
    import importlib.util as _ilu

    monkeypatch.setattr(_ilu, "spec_from_file_location", lambda *a, **k: None)
    log_probs = torch.tensor([float("nan"), 0.0, 0.0, 0.0])
    correction, info = compute_dr_variance_correction(
        research_methods=_dr_method(_default_cfg()),
        log_probs=log_probs,
        old_log_probs=torch.tensor([0.0, 0.0, 0.0, 0.0]),
        advantages=ADVANTAGES,
        ratio_clip_log_delta=CLIP,
    )
    assert float(correction) == 0.0
    assert info["dr_variance_correction_value"] == 0.0


def test_pair_loss_gap_exactly_at_min_is_mined() -> None:
    """The mining rule skips gaps < min_reward_gap — an EXACT-equal gap is a
    valid pair (boundary pin). Uses power-of-two rewards so the gap is
    float-exact (0.25 == min_gap 0.25, no representation noise)."""
    cfg = _default_cfg()
    cfg["dr_pair_min_reward_gap"] = 0.25
    rewards = torch.tensor([0.5, 0.25, 0.375, 0.3125])  # gap 0.25 == min_gap
    current = [torch.tensor(0.1) for _ in range(4)]
    old = [torch.tensor(0.0) for _ in range(4)]
    loss, info = compute_dr_pair_loss(
        research_methods=_dr_method(cfg),
        rewards=rewards,
        codes=["a", "b", "c", "d"],
        current_log_probs=current,
        old_log_probs=old,
    )
    assert info["dr_pair_mined"] is True
    assert float(loss) > 0.0
    assert math.isfinite(float(loss))
    # and one epsilon BELOW the min is skipped (0.25 - 2^-12 gap)
    below = torch.tensor([0.5, 0.25 + 2.0**-12, 0.375, 0.3125])
    loss2, info2 = compute_dr_pair_loss(
        research_methods=_dr_method(cfg),
        rewards=below,
        codes=["a", "b", "c", "d"],
        current_log_probs=current,
        old_log_probs=old,
    )
    assert info2["dr_pair_mined"] is False
    assert float(loss2) == 0.0

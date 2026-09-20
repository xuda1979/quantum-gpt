"""TDD test for warm-continue flat_candidate_dispersion collapse (RED first).

Scenario: warm-continue from a 3/18 checkpoint. On tasks where all candidates
fail (pass_rate=0), but candidates have DIFFERENT partial-credit rewards,
the current gate zeros the magnitude because dispersion < 0.5.

This causes training to stall: most groups at 3/18 level have pass_rate=0 with
low dispersion (many similar partial-credit candidates), so the gate kills
the majority of training signal.

The fix: add a min_rms_for_update parameter. When loo_advantage_rms is above
this threshold, the dispersion gate does NOT hard-zero the magnitude, even
with pass_rate=0 and low dispersion. This preserves the original s26 outlier
gate (near-zero RMS) while allowing warm-continue groups with real
partial-credit signal to contribute gradient.
"""

import torch


def _adv_for(rewards: torch.Tensor) -> torch.Tensor:
    """Compute LOO advantages for a reward tensor."""
    n = len(rewards)
    mean_excl = (rewards.sum() - rewards) / (n - 1)
    return rewards - mean_excl


class TestWarmContinueDispersionCollapse:
    """Tests that the warm-continue collapse is fixed."""

    def test_all_fail_partial_credit_low_dispersion_not_zeroed(self) -> None:
        """Warm-continue: 8 candidates all fail (pass_rate=0) with 6 at
        similar partial credit + 2 slightly better. dispersion=0.25 < 0.5
        but RMS=0.057 is real signal. Gate should NOT zero magnitude
        when min_rms_for_update is provided and RMS exceeds it."""
        from training.grpo_utils import policy_update_signal_magnitude

        # 6 candidates at 0.15, 1 at 0.20, 1 at 0.30 — all fail
        # dispersion = 1 - 6/8 = 0.25 < 0.5 → current code zeros this
        rewards = torch.tensor([0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.20, 0.30])
        adv = _adv_for(rewards)
        rms = float(adv.square().mean().sqrt())

        # With the fix: min_rms_for_update=0.01 means RMS > 0.01 → don't gate
        magnitude, kind = policy_update_signal_magnitude(
            advantage_mode="loo",
            signal_stats={"signal_std": 0.05},
            loo_advantage_rms=rms,
            advantages=adv,
            pass_rate=0.0,
            min_candidate_dispersion=0.5,
            min_rms_for_update=0.01,
        )

        assert magnitude > 0.0, (
            f"Warm-continue collapse: all-fail group with partial credit "
            f"(rms={rms:.4f} > 0.01, dispersion=0.25) was zeroed. "
            f"The model needs this signal to improve from 3/18."
        )
        assert kind == "loo_advantage_rms"

    def test_truly_flat_near_zero_rms_still_zeroed(self) -> None:
        """Safety: genuinely flat group (near-zero RMS) is still gated
        even with min_rms_for_update. The fix preserves the outlier gate
        for noise groups."""
        from training.grpo_utils import policy_update_signal_magnitude

        # 7 at 0.07 + 1 at 0.08 — near-zero RMS
        rewards = torch.tensor([0.07, 0.07, 0.07, 0.07, 0.07, 0.07, 0.07, 0.08])
        adv = _adv_for(rewards)
        rms = float(adv.square().mean().sqrt())

        magnitude, kind = policy_update_signal_magnitude(
            advantage_mode="loo",
            signal_stats={"signal_std": 0.003},
            loo_advantage_rms=rms,
            advantages=adv,
            pass_rate=0.0,
            min_candidate_dispersion=0.5,
            min_rms_for_update=0.01,  # RMS < 0.01 → still gated
        )

        assert magnitude == 0.0, f"Genuinely flat group (rms={rms:.4f} < 0.01) should be gated"
        assert kind == "flat_candidate_dispersion"

    def test_outlier_group_still_zeroed_with_min_rms(self) -> None:
        """Safety: the original s26 class (7 identical + 1 outlier, all fail)
        has RMS=0.087 > 0.01 but is still an outlier group. With
        min_rms_for_update, this should NOT be gated because the outlier
        provides real signal that the model can learn from.

        This test documents the behavior change: the old s26 gate killed
        this group, but with min_rms_for_update, it's allowed through.
        The s26 regression test (without min_rms_for_update) still passes
        to preserve backward compatibility."""
        from training.grpo_utils import policy_update_signal_magnitude

        rewards = torch.tensor([0.07] * 7 + [0.30])
        adv = _adv_for(rewards)
        rms = float(adv.square().mean().sqrt())

        magnitude, kind = policy_update_signal_magnitude(
            advantage_mode="loo",
            signal_stats={"signal_std": 0.028},
            loo_advantage_rms=rms,
            advantages=adv,
            pass_rate=0.0,
            min_candidate_dispersion=0.5,
            min_rms_for_update=0.01,
        )

        # With the fix: RMS=0.087 > 0.01 → allowed through
        assert (
            magnitude > 0.0
        ), f"Group with rms={rms:.4f} > min_rms_for_update=0.01 should not be gated"
        assert kind == "loo_advantage_rms"

    def test_backward_compat_no_min_rms_preserves_s26_gate(self) -> None:
        """Backward compatibility: when min_rms_for_update is NOT passed
        (default None), the original s26 gate behavior is preserved.
        This ensures existing callers are unaffected."""
        from training.grpo_utils import policy_update_signal_magnitude

        rewards = torch.tensor([0.07] * 7 + [0.30])
        adv = _adv_for(rewards)
        rms = float(adv.square().mean().sqrt())

        magnitude, kind = policy_update_signal_magnitude(
            advantage_mode="loo",
            signal_stats={"signal_std": 0.028},
            loo_advantage_rms=rms,
            advantages=adv,
            pass_rate=0.0,
            min_candidate_dispersion=0.5,
            # min_rms_for_update NOT passed → default behavior
        )

        # Original behavior: gated
        assert magnitude == 0.0
        assert kind == "flat_candidate_dispersion"

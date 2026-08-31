"""TDD (coverage lane, PASS 16): the step-loop guardrails — degenerate-policy
alarm (2026-08-26 r10 rescue), the quarantine-integrity gate (2026-08-27 T1a),
and the train-pass sequence cap bookkeeping (2026-08-25 OOM fix).

Before this suite: alarm_degenerate_policy 2/8 stmts (25%), quarantine_gate_active
2/10 (20%), train_pass_truncation_breakdown 1/5 (20%), DegeneratePolicyDetector
untested directly. Every expectation below is derived from the documented
contracts, not the implementation:

  * the alarm fires on the WINDOW-CROSSING step (3rd consecutive degenerate
    step) and on every subsequent degenerate step, and escalates the SAME
    temperature ladder as low-reward-signal skips;
  * a healthy step resets the streak;
  * the quarantine gate engages on ANY of: alarm fired, entropy below the
    degenerate floor (0.05), or an all-stub completion group (max token < 8);
  * the truncation bookkeeping is honest: rate = truncated/total, cap 0
    means disabled, zero-total means rate 0.0.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.grpo_trainer import (  # noqa: E402
    DEGENERATE_POLICY_ENTROPY_MAX,
    QUARANTINE_GATE_COLLAPSE_MAX_TOKENS,
    DegeneratePolicyDetector,
    _sigterm_payload_step,
    alarm_degenerate_policy,
    is_degenerate_policy_step,
    quarantine_gate_active,
    train_pass_truncation_breakdown,
)
from training.grpo_utils import (  # noqa: E402
    DEGENERATE_POLICY_REASON,
    AdaptiveTemperatureState,
)

COLLAPSED = dict(entropy_mean=0.01, completion_token_lengths=[1, 1, 1, 1])
HEALTHY = dict(entropy_mean=0.4, completion_token_lengths=[24, 31, 18, 42])


# ---------------------------------------------------------------------------
# DegeneratePolicyDetector — the EOS-collapse streak
# ---------------------------------------------------------------------------


def test_detector_healthy_step_resets_streak() -> None:
    detector = DegeneratePolicyDetector()
    assert detector.observe(**COLLAPSED) is False
    assert detector.observe(**HEALTHY) is False
    assert detector.consecutive_degenerate == 0


def test_detector_fires_on_window_crossing_and_keeps_firing() -> None:
    detector = DegeneratePolicyDetector()
    assert detector.observe(**COLLAPSED) is False  # step 1
    assert detector.observe(**COLLAPSED) is False  # step 2
    assert detector.observe(**COLLAPSED) is True  # step 3 — the alarm step
    assert detector.consecutive_degenerate == 3
    # every SUBSEQUENT degenerate step keeps the alarm raised so the rescue
    # ladder keeps escalating during an ongoing collapse
    assert detector.observe(**COLLAPSED) is True


def test_detector_respects_custom_window() -> None:
    detector = DegeneratePolicyDetector(window=1)
    assert detector.observe(**COLLAPSED) is True  # 1-step window fires at once


def test_detector_healthy_after_collapse_resets() -> None:
    detector = DegeneratePolicyDetector()
    detector.observe(**COLLAPSED)
    detector.observe(**COLLAPSED)
    assert detector.observe(**HEALTHY) is False
    assert detector.consecutive_degenerate == 0
    # the streak restarts: the next alarm needs a fresh window of 3
    assert detector.observe(**COLLAPSED) is False
    assert detector.observe(**COLLAPSED) is False
    assert detector.observe(**COLLAPSED) is True


def test_is_degenerate_policy_step_requires_both_conditions() -> None:
    # both required: near-zero entropy AND ~1-token completions
    assert is_degenerate_policy_step(**COLLAPSED) is True
    assert is_degenerate_policy_step(entropy_mean=0.01, completion_token_lengths=[20, 30]) is False
    assert is_degenerate_policy_step(entropy_mean=0.4, completion_token_lengths=[1, 1]) is False
    assert is_degenerate_policy_step(entropy_mean=None, completion_token_lengths=[1, 1]) is False
    assert is_degenerate_policy_step(entropy_mean=0.01, completion_token_lengths=None) is False
    # boundary: entropy exactly AT the floor is NOT degenerate
    assert (
        is_degenerate_policy_step(
            entropy_mean=DEGENERATE_POLICY_ENTROPY_MAX, completion_token_lengths=[1]
        )
        is False
    )


# ---------------------------------------------------------------------------
# alarm_degenerate_policy — the rescue-ladder trigger
# ---------------------------------------------------------------------------


def test_alarm_escalates_ladder_on_window_crossing() -> None:
    detector = DegeneratePolicyDetector()
    temp = AdaptiveTemperatureState(base_temp=1.0, step_size=0.15, max_temp=1.3)
    assert alarm_degenerate_policy(detector, temp, **COLLAPSED) is False
    assert alarm_degenerate_policy(detector, temp, **COLLAPSED) is False
    assert temp.consecutive_low_signal_skips == 0
    # window-crossing step: alarm fires AND the ladder escalates IMMEDIATELY
    assert alarm_degenerate_policy(detector, temp, **COLLAPSED) is True
    assert temp.consecutive_low_signal_skips == 1
    assert temp.current_temp() == pytest.approx(1.0 * 1.15)


def test_alarm_keeps_escalating_during_collapse() -> None:
    detector = DegeneratePolicyDetector()
    temp = AdaptiveTemperatureState(base_temp=1.0, step_size=0.15, max_temp=1.3)
    for _ in range(3):
        alarm_degenerate_policy(detector, temp, **COLLAPSED)
    assert alarm_degenerate_policy(detector, temp, **COLLAPSED) is True
    assert temp.consecutive_low_signal_skips == 2  # ladder keeps climbing
    assert temp.current_temp() == pytest.approx(1.0 * 1.30)  # clamped at 1.3


def test_alarm_healthy_step_no_alarm_no_escalation() -> None:
    detector = DegeneratePolicyDetector()
    temp = AdaptiveTemperatureState(base_temp=1.0)
    assert alarm_degenerate_policy(detector, temp, **HEALTHY) is False
    assert temp.consecutive_low_signal_skips == 0


def test_alarm_reason_is_the_skip_reason_contract() -> None:
    # The ladder escalation must use the degenerate_policy reason (the same
    # ladder as low_reward_signal) — pin the constant used.
    assert DEGENERATE_POLICY_REASON == "degenerate_policy"


# ---------------------------------------------------------------------------
# quarantine_gate_active — quarantine/repair-routing suppression
# ---------------------------------------------------------------------------


def test_gate_engages_on_alarm() -> None:
    assert quarantine_gate_active(degenerate_policy_alarm=True, **HEALTHY) is True


def test_gate_engages_on_low_entropy_even_without_alarm() -> None:
    assert (
        quarantine_gate_active(
            degenerate_policy_alarm=False,
            entropy_mean=0.01,
            completion_token_lengths=[30, 40, 20],
        )
        is True
    )


def test_gate_engages_on_stub_collapse_group() -> None:
    """The near-EOS-collapse class: EVERY completion shorter than 8 tokens —
    engaged even at non-tiny entropy (the run-6 step-25 class)."""
    assert (
        quarantine_gate_active(
            degenerate_policy_alarm=False,
            entropy_mean=0.3,
            completion_token_lengths=[3, 5, 2, 7],
        )
        is True
    )


def test_gate_inactive_when_healthy() -> None:
    assert quarantine_gate_active(degenerate_policy_alarm=False, **HEALTHY) is False


def test_gate_inactive_when_observations_missing() -> None:
    assert (
        quarantine_gate_active(
            degenerate_policy_alarm=False, entropy_mean=None, completion_token_lengths=None
        )
        is False
    )


def test_gate_stub_boundary_is_lt_collapse_max_tokens() -> None:
    """The stub class is max < QUARANTINE_GATE_COLLAPSE_MAX_TOKENS (8): a
    group with exactly 8 tokens is NOT a stub-collapse group."""
    assert QUARANTINE_GATE_COLLAPSE_MAX_TOKENS == 8
    assert (
        quarantine_gate_active(
            degenerate_policy_alarm=False,
            entropy_mean=0.3,
            completion_token_lengths=[8, 8, 8],
        )
        is False
    )
    assert (
        quarantine_gate_active(
            degenerate_policy_alarm=False,
            entropy_mean=0.3,
            completion_token_lengths=[7, 7, 7],
        )
        is True
    )


# ---------------------------------------------------------------------------
# train_pass_truncation_breakdown — the honest cap bookkeeping
# ---------------------------------------------------------------------------


def test_truncation_breakdown_rate_and_cap() -> None:
    fields = train_pass_truncation_breakdown(seq_cap=360, n_truncated=2, n_total=4)
    assert fields["train_pass_seq_cap"] == 360
    assert fields["train_pass_truncation_rate"] == 0.5


def test_truncation_breakdown_disabled_cap_is_zero() -> None:
    fields = train_pass_truncation_breakdown(seq_cap=0, n_truncated=5, n_total=10)
    assert fields["train_pass_seq_cap"] == 0
    assert fields["train_pass_truncation_rate"] == 0.0  # honest: no cap, no truncation claim


def test_truncation_breakdown_zero_total_no_division_error() -> None:
    fields = train_pass_truncation_breakdown(seq_cap=360, n_truncated=0, n_total=0)
    assert fields["train_pass_seq_cap"] == 360
    assert fields["train_pass_truncation_rate"] == 0.0


def test_truncation_breakdown_rounding_six_digits() -> None:
    fields = train_pass_truncation_breakdown(seq_cap=360, n_truncated=1, n_total=3)
    assert fields["train_pass_truncation_rate"] == 0.333333


# ---------------------------------------------------------------------------
# _sigterm_payload_step — the SIGTERM payload step coherence (code-review F2)
# ---------------------------------------------------------------------------


def test_sigterm_payload_step_matches_inflight_boundary() -> None:
    """The resume_state payload step on SIGTERM must match the checkpoint dir
    being written — the IN-FLIGHT step, falling back to last-completed."""
    assert _sigterm_payload_step(stop_step=12, last_completed=10) == 12
    assert _sigterm_payload_step(stop_step=None, last_completed=10) == 10
    assert _sigterm_payload_step(stop_step=0, last_completed=3) == 0

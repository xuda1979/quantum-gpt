"""Test-pin the capability-sentinel rule table (STATUS.md STANDUP #234, 2026-09-01).

The box-side capability_sentinel.py (autostop=1, 60s poll) fires RED + AUTO-STOPS
training on four rules:
  1. entropy drift: recent mean > 3x min-baseline AND min>0.01 AND recent>0.3
  2. trust-region violations in >=5 windows
  3. NaN/Inf in loss/rewards
  4. NPU ERR99999

This local module mirrors the rule table so the sentinel's contract is
test-pinned and validated against the real RUN-12 degradation: min-baseline
0.042 vs recent 1.056 -> WOULD FIRE (per STANDUP #234).
"""

import pytest

from scripts import sapo_capability_sentinel_rules as rules

# ---------------------------------------------------------------------------
# Rule 1: entropy drift  (validated against real RUN-12 data)
# ---------------------------------------------------------------------------


def test_entropy_drift_fires_on_run12_validation_case():
    # REAL RUN-12 degradation: min-baseline 0.042, recent mean 1.056.
    # Per STANDUP #234 this MUST fire (the first-3-mean rule missed it).
    assert rules.entropy_drift_fires(0.042, 1.056) is True


def test_entropy_drift_quiet_below_recent_gate():
    # recent <= 0.3 -> no fire regardless of the 3x multiple.
    assert rules.entropy_drift_fires(0.042, 0.20) is False
    assert rules.entropy_drift_fires(0.042, 0.30) is False  # strict >


def test_entropy_drift_quiet_below_min_baseline_floor():
    # min-baseline <= 0.01 -> no fire even with a high recent mean.
    assert rules.entropy_drift_fires(0.008, 1.5) is False
    assert rules.entropy_drift_fires(0.01, 1.5) is False  # strict >


def test_entropy_drift_quiet_below_3x_multiple():
    # recent > 0.3 but below 3x min-baseline -> no fire.
    assert rules.entropy_drift_fires(0.15, 0.44) is False  # 0.44 < 3*0.15
    assert rules.entropy_drift_fires(0.15, 0.45) is True  # exactly 3x -> strict > fires


def test_entropy_drift_fires_when_all_gates_met():
    assert rules.entropy_drift_fires(0.05, 0.31) is True  # 0.31 > 3*0.05, both gates met


# ---------------------------------------------------------------------------
# Rule 2: trust-region violations
# ---------------------------------------------------------------------------


def test_trust_region_fires_at_five_windows():
    assert rules.trust_region_fires(5) is True
    assert rules.trust_region_fires(9) is True


def test_trust_region_quiet_below_five_windows():
    assert rules.trust_region_fires(0) is False
    assert rules.trust_region_fires(4) is False


# ---------------------------------------------------------------------------
# Rule 3: NaN/Inf in loss or rewards
# ---------------------------------------------------------------------------


def test_nonfinite_loss_fires():
    assert rules.nonfinite_fires(float("nan"), [0.1, 0.2]) is True
    assert rules.nonfinite_fires(float("inf"), [0.1, 0.2]) is True


def test_nonfinite_rewards_fire():
    assert rules.nonfinite_fires(-0.05, [0.1, float("nan")]) is True
    assert rules.nonfinite_fires(-0.05, [float("inf"), 0.2]) is True
    assert rules.nonfinite_fires(-0.05, [-float("inf"), 0.2]) is True


def test_finite_metrics_quiet():
    assert rules.nonfinite_fires(-0.07, [0.1, 0.2, -0.3]) is False


# ---------------------------------------------------------------------------
# Rule 4: NPU ERR99999
# ---------------------------------------------------------------------------


def test_err99999_fires():
    assert rules.npu_err99999_fires("step 12: NPU ERR99999 on card 3") is True
    assert rules.npu_err99999_fires("ERROR:ERR99999") is True


def test_clean_log_quiet():
    assert rules.npu_err99999_fires("step_begin step 12 quantum_shor") is False
    assert rules.npu_err99999_fires("") is False


# ---------------------------------------------------------------------------
# Composite: fired-signal list for a snapshot
# ---------------------------------------------------------------------------


def test_composite_all_clear_returns_empty_list():
    fired = rules.evaluate(
        entropy_min_baseline=0.042,
        entropy_recent_mean=0.05,
        trust_region_violation_windows=0,
        loss=-0.05,
        rewards=[0.1, 0.2],
        log_text="step_begin step 1 quantum_shor_phase_error_correction",
    )
    assert fired == []


def test_composite_run12_entropy_degradation_fires_entropy_only():
    # Real RUN-12 snapshot from STANDUP #234: entropy min-baseline 0.042,
    # recent 1.056 -> exactly the entropy_drift signal.
    fired = rules.evaluate(
        entropy_min_baseline=0.042,
        entropy_recent_mean=1.056,
        trust_region_violation_windows=2,
        loss=-0.05,
        rewards=[0.1, 0.2],
        log_text="step_begin step 12",
    )
    assert fired == ["entropy_drift"]


def test_composite_fires_all_rules_together():
    fired = rules.evaluate(
        entropy_min_baseline=0.05,
        entropy_recent_mean=0.31,
        trust_region_violation_windows=6,
        loss=float("nan"),
        rewards=[0.1],
        log_text="NPU ERR99999",
    )
    assert fired == [
        "entropy_drift",
        "nonfinite_loss_rewards",
        "npu_err99999",
        "trust_region_violations",
    ]


# ---------------------------------------------------------------------------
# Non-vacuous smoke: the module under test is really the one being exercised
# ---------------------------------------------------------------------------


def test_bellwether_module_is_imported_and_live():
    # Guards the shadowed-helper vacuity class: this must exercise the real
    # module (module object identity + a known probe answer).
    assert rules.__name__ == "scripts.sapo_capability_sentinel_rules"
    assert rules.entropy_drift_fires(0.042, 1.056) is True


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))

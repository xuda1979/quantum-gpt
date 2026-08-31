"""sapo_capability_sentinel_rules.py — local mirror of the capability-sentinel rule table.

Reference implementation of the rule table deployed box-side as
capability_sentinel.py (STATUS.md STANDUP #234, 2026-09-01; autostop=1, 60s poll
on the ACTIVE training log). The box-side watcher performs the log parsing; this
module pins the RULES so they are test-validated locally:

  1. entropy drift:  recent mean > 3x min-baseline  AND  min-baseline > 0.01
                     AND  recent mean > 0.3              -> FIRE
  2. trust-region violations in >= 5 windows              -> FIRE
  3. NaN/Inf in loss or rewards                           -> FIRE
  4. "ERR99999" (NPU death) in the log text               -> FIRE

Validated against the real RUN-12 degradation (STANDUP #234): min-baseline
0.042 vs recent mean 1.056 -> WOULD FIRE (the earlier first-3-mean rule missed
it because the entropy spiked within the first 3 records).

Python 3.9-safe (no zip-strict, no X|Y unions). Pure functions; no I/O.
"""

from __future__ import annotations

import math

# Rule constants (mirror of the box-side sentinel's thresholds).
ENTROPY_MIN_BASELINE_FLOOR = 0.01  # min-baseline must exceed this to count
ENTROPY_RECENT_GATE = 0.3  # recent mean must exceed this
ENTROPY_DRIFT_MULTIPLE = 3.0  # recent mean must exceed 3x min-baseline
TRUST_REGION_FIRE_WINDOWS = 5  # >= 5 windows fires
NPU_ERR_TOKEN = "ERR99999"


def entropy_drift_fires(min_baseline, recent_mean):
    """Rule 1: entropy drift. Returns True iff all three gates are met.

    Fires iff: min_baseline > 0.01 AND recent_mean > 0.3
               AND recent_mean > 3.0 * min_baseline.
    """
    if min_baseline <= ENTROPY_MIN_BASELINE_FLOOR:
        return False
    if recent_mean <= ENTROPY_RECENT_GATE:
        return False
    return recent_mean > ENTROPY_DRIFT_MULTIPLE * min_baseline


def trust_region_fires(violation_windows):
    """Rule 2: trust-region violations. Fires at >= 5 windows."""
    return int(violation_windows) >= TRUST_REGION_FIRE_WINDOWS


def nonfinite_fires(loss, rewards):
    """Rule 3: NaN/Inf in loss or any reward fires."""
    if loss is None:
        return True  # missing measurement is not healthy
    try:
        if not math.isfinite(float(loss)):
            return True
        for reward in rewards or []:
            if not math.isfinite(float(reward)):
                return True
    except (TypeError, ValueError):
        return True
    return False


def npu_err99999_fires(log_text):
    """Rule 4: NPU ERR99999 in the log text fires."""
    return NPU_ERR_TOKEN in (log_text or "")


def evaluate(
    entropy_min_baseline,
    entropy_recent_mean,
    trust_region_violation_windows,
    loss,
    rewards,
    log_text,
):
    """Composite check over one training-log snapshot.

    Returns the sorted list of fired signal names:
    "entropy_drift", "trust_region_violations", "nonfinite_loss_rewards",
    "npu_err99999". Empty list = all clear.
    """
    fired = []
    if entropy_drift_fires(entropy_min_baseline, entropy_recent_mean):
        fired.append("entropy_drift")
    if trust_region_fires(trust_region_violation_windows):
        fired.append("trust_region_violations")
    if nonfinite_fires(loss, rewards):
        fired.append("nonfinite_loss_rewards")
    if npu_err99999_fires(log_text):
        fired.append("npu_err99999")
    return sorted(fired)

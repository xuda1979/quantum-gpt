"""C-9024: ASI2 :19004 stuck-boot classifier.

Classifies same-pid stall vs boot-restart loop from >=10 min of /health
(pid, uptime) snapshots, fail-closed: any transport gap, short window, or
malformed snapshot -> UNKNOWN, never a guess.

Precedent (SAPO standup #430): ASI2 BOOT-RESTART LOOP confirmed by
pid 73113->51740 with uptime reset to 1s (platform code 170022, B-187
USER-GATED); ASI1 same-pid with monotonically growing uptime was NOT a loop.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asi2_boot_classifier import classify


def snap(ts, pid, uptime, ready=False):
    return {"ts": ts, "pid": pid, "uptime": uptime, "ready": ready}


class TestClassify:
    def test_same_pid_monotonic_uptime_is_stall(self):
        probes = [snap(0, 21416, 672), snap(660, 21416, 1332)]
        assert classify(probes) == "STALL_SAME_PID"

    def test_pid_change_is_boot_restart_loop(self):
        probes = [snap(0, 73113, 300), snap(660, 51740, 60)]
        assert classify(probes) == "BOOT_RESTART_LOOP"

    def test_uptime_reset_same_pid_is_loop(self):
        probes = [snap(0, 21416, 1200), snap(660, 21416, 30)]
        assert classify(probes) == "BOOT_RESTART_LOOP"

    def test_ready_true_overrides(self):
        probes = [snap(0, 21416, 672), snap(660, 21416, 1332, ready=True)]
        assert classify(probes) == "READY"

    def test_transport_gap_is_unknown(self):
        probes = [snap(0, 21416, 672), None]
        assert classify(probes) == "UNKNOWN"

    def test_short_window_is_unknown(self):
        probes = [snap(0, 21416, 672), snap(599, 21416, 1271)]
        assert classify(probes) == "UNKNOWN"

    def test_missing_fields_is_unknown(self):
        probes = [{"ts": 0, "pid": 21416}, snap(660, 21416, 1332)]
        assert classify(probes) == "UNKNOWN"

    def test_single_probe_is_unknown(self):
        assert classify([snap(0, 21416, 672)]) == "UNKNOWN"

    def test_empty_is_unknown(self):
        assert classify([]) == "UNKNOWN"

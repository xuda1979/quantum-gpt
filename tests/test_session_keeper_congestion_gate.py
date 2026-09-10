#!/usr/bin/env python3
"""RED test: keeper congestion/backlog-wedge detector (2026-09-09 ASI3 wedge).

Two live failure classes, both observed 2026-09-08T16:32Z -> 09-09T02:50Z on
ASI3 daemon :20653 (14 pending, zero completions for 2h21m, keeper silent):

  Class 1 (vacuous probe): the congestion probe called json.load(sys.stdin)
  TWICE - the 2nd read hit EOF, the traceback was swallowed by 2>/dev/null,
  and $busy was always empty, so no case pattern ever matched and the check
  could NEVER fire. Detector deployed but vacuous = blind keeper.

  Class 2 (missing backlog arm): busy:false + ready:true + pendingRequestCount
  >= SK_PENDING_MAX is the live wedge signature (dispatch works, completion
  path broken), but the original detector only matched busy:true.

Contract (pinned against the SHIPPED script text, the level where both bugs
lived): the probe pipeline reads stdin exactly once, and the case dispatch
contains arms for (busy=True,ready=True) congested and (busy=False,ready=True,
pending>=SK_PENDING_MAX) backlog wedge, with pending capped at -1 when absent
(fail-safe for older daemon builds).
"""
import re
import pathlib

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "session_keeper.sh"


def _probe_block():
    text = SCRIPT.read_text()
    m = re.search(r"daemon_congested_check\(\) \{(.*?)\n\}", text, re.S)
    assert m, "daemon_congested_check() not found in session_keeper.sh"
    return m.group(1)


def test_probe_reads_stdin_exactly_once():
    block = _probe_block()
    # B-038 fix: count CODE lines only - the probe body carries a comment that
    # MENTIONS the old double-read bug, and counting comments made this test
    # RED-for-the-wrong-reason (2026-09-09 #293).
    code_lines = [ln for ln in block.splitlines() if not ln.strip().startswith("#")]
    n = sum(ln.count("json.load(sys.stdin)") for ln in code_lines)
    assert n == 1, (
        "congestion probe calls json.load(sys.stdin) %dx - the 2nd read hits "
        "EOF, the traceback is swallowed, and $busy is always empty so NO case "
        "pattern can ever match (the 2026-09-09 vacuous detector class). "
        "Exactly one read is the contract." % n
    )


def test_busy_congested_arm_exists():
    block = _probe_block()
    assert re.search(r'"True True"\*\)', block), (
        "case arm for busy=True ready=True (congested) missing - keeper would "
        "never restart a busy-but-alive daemon with a non-round-trip output path"
    )


def test_backlog_wedge_arm_exists_with_pending_threshold():
    block = _probe_block()
    assert re.search(r'"False True"\*', block), (
        "case arm for busy=False ready=True (backlog wedge) missing - the live "
        "16:41Z ASI3 class (dispatch ok, completions broken, pending 14) was "
        "invisible to every auto-heal layer"
    )
    assert "SK_PENDING_MAX" in block, (
        "backlog arm must gate on the SK_PENDING_MAX threshold"
    )
    assert "-1 if pend is None else pend" in block, (
        "pendingRequestCount must default to -1 when absent so older daemon "
        "builds never false-fire the wedge restart"
    )


def test_threshold_is_small_enough_to_catch_wedge():
    text = SCRIPT.read_text()
    m = re.search(r"^SK_PENDING_MAX=(\d+)", text, re.M)
    assert m, "SK_PENDING_MAX not defined"
    assert int(m.group(1)) <= 4, (
        "threshold too high: the live wedge sat at pending=14 for 2h21m, but a "
        "healthy daemon must drain below the bar within ~2 keeper cycles"
    )


# -- B-039 (2026-09-09): the REMEDY was blind for the backlog-wedge class --
# Live relapse 20:23Z: ASI3 :20653 ready:true, pending>=4, no completions for
# 46min+ on pid 3431. The B-036 detector fires (it detects), but
# daemons_recover() only launchctl-kickstarts the heartbeat - and the heartbeat
# restarts daemons ONLY on error/authfail/booting>15m. ready:true+backlogged
# matches NONE of those, so detection GREEN but remedy BLIND: the wedge
# survived every keeper cycle. Contract: daemons_recover must restart a
# backlogged daemon DIRECTLY (POST /stop to its port; the daemon's supervisor
# relaunches it), falling back to the heartbeat kick only otherwise.


def _recover_block():
    text = SCRIPT.read_text()
    m = re.search(r"daemons_recover\(\) \{(.*?)\n\}", text, re.S)
    assert m, "daemons_recover() not found in session_keeper.sh"
    return m.group(1)


def test_wedge_recovery_posts_stop_to_daemon_port():
    block = _recover_block()
    assert re.search(r"POST.*/stop", block), (
        "daemons_recover never POSTs /stop to the wedged daemon port - "
        "ready:true+backlogged never matches the heartbeat's restart triggers "
        "(error/authfail/booting>15m), so a backlog wedge survives every "
        "keeper cycle (the 20:23Z pid-3431 relapse). Direct restart required."
    )


def test_wedge_recovery_targets_monitored_ports():
    # B-039: recovery and detection must iterate the SAME port list. The ports
    # come from SK_DAEMON_PORTS; recovery falls back to the heartbeat kick only
    # when no monitored port is wedged.
    #
    # 2026-09-10: the default grew from "20653 19004" to include ASI1 (:20646) —
    # §9.1 requires EVERY provisioned env's daemon to be watched, and ASI1 was
    # previously invisible to the keeper. The invariant this test guards (one
    # shared list for detection AND recovery) is unchanged.
    text = SCRIPT.read_text()
    m = re.search(r'^SK_DAEMON_PORTS="\$\{SK_DAEMON_PORTS:-(20653 19004 20646)\}"', text, re.M)
    assert m, "SK_DAEMON_PORTS default must be 20653 19004 20646 - recovery must target the ports congestion monitoring watches, or the restart is a silent no-op"
    block = _recover_block()
    assert "$SK_DAEMON_PORTS" in block and "$SK_DAEMON_PORTS" in _probe_block(), (
        "daemons_recover and daemon_congested_check must both iterate SK_DAEMON_PORTS"
    )

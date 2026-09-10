"""B-075: the heartbeat's state dispatch must read the variable its helper sets.

Found live 2026-09-11: `action_for_state()` assigns the GLOBAL ``ACTION``, but the
dispatch read lowercase ``"$action"`` — a name that never exists. Under ``set -u``
that aborts the whole script with "line 173: action: unbound variable" on EVERY
tick, *before* it can restart a single daemon.

The consequence was not a missed tick, it was a permanently dark transport: the
heartbeat logged "heartbeat start" over and over with no "relaunched" line in
between, all three env daemons (ASI1/20646, ASI2/19004, ASI3/20653) went down,
and nothing in the system could bring them back. A supervisor whose dispatch
crashes is worse than no supervisor, because its own log still looks alive.

This is the "shadowed/never-assigned name" class this repo has hit before (B-038
counted its own comment line; B-039's probe read stdin twice so its detector
could never fire). The guard below is deliberately textual AND behavioural: it
asserts the shipped script's dispatch reads ``$ACTION``, and it exercises the
real function to prove the value it sets is the one the dispatch consumes.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "sapo_huanxin_heartbeat.sh"


def _dispatch_case_line() -> str:
    """The `case ... in` that dispatches on the probe state.

    Anchored to the `action_for_state` call so it cannot pick up the other
    `case` statements in this script (e.g. bootval_for's numeric validation).
    """
    lines = SCRIPT.read_text().splitlines()
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#") or "{" in line:
            continue  # skip comments and the function DEFINITION
        if "action_for_state" in line:  # the CALL site inside the daemon loop
            for following in lines[idx + 1 : idx + 12]:
                if following.strip().startswith("#"):
                    continue  # explanatory comments may sit between call and case
                if re.match(r"\s*case\s", following):
                    return following
                break  # first real statement is not the dispatch
    raise AssertionError("no state dispatch `case` found after the action_for_state() call")


def test_dispatch_reads_the_variable_the_helper_sets():
    """The case must read $ACTION — the name action_for_state() assigns."""
    case_line = _dispatch_case_line()
    assert "ACTION" in case_line, (
        f"heartbeat dispatch reads {case_line.strip()!r}. action_for_state() sets "
        "$ACTION, so a lowercase read is never assigned and `set -u` aborts the "
        "script on every tick (B-075) — all daemons stay dark."
    )
    assert "$action" not in case_line, (
        f"heartbeat dispatch still reads the never-assigned $action: {case_line.strip()!r}"
    )


def test_action_for_state_sets_the_global_the_dispatch_consumes():
    """Behavioural proof: source the shipped function and read back $ACTION.

    Runs the real script with SAPO_HEARTBEAT_SOURCE_ONLY=1 (the file's own test
    hook), so this cannot drift from the shipped implementation.
    """
    probe = (
        "set -u; "
        ". \"$0\" >/dev/null 2>&1; "
        'for s in ready booting unknown down error garbage; do '
        'action_for_state "$s"; printf "%s=%s\\n" "$s" "$ACTION"; '
        "done"
    )
    out = subprocess.run(
        ["bash", "-c", probe, str(SCRIPT)],
        capture_output=True,
        text=True,
        env={"SAPO_HEARTBEAT_SOURCE_ONLY": "1", "PATH": "/usr/bin:/bin", "HOME": "/tmp"},
        timeout=30,
    )
    assert out.returncode == 0, f"probe failed: {out.stderr[-400:]}"
    got = dict(line.split("=", 1) for line in out.stdout.strip().splitlines() if "=" in line)

    # Every state maps to a defined action — none may leave ACTION unset, or the
    # dispatch would itself abort under `set -u`.
    for state in ("ready", "booting", "unknown", "down", "error", "garbage"):
        assert state in got, f"action_for_state did not set ACTION for {state!r}: {out.stdout!r}"
        assert got[state], f"ACTION empty for {state!r} — dispatch would abort under set -u"

    assert got["ready"] == "clear"
    assert got["booting"] == "timer"
    # Three-state rule (B-051): an unreadable probe is INERT, never a restart.
    assert got["unknown"] == "inert"
    assert got["garbage"] == "inert"
    # A positive DEAD signal is the only thing that restarts.
    assert got["down"] == "restart"
    assert got["error"] == "restart"


def test_no_unassigned_case_variable_in_dispatch():
    """No `case "$<lower>"` may exist anywhere in the heartbeat script."""
    offenders = [
        line.strip()
        for line in SCRIPT.read_text().splitlines()
        if re.match(r"\s*case\s+\"\$[a-z]", line)
    ]
    assert not offenders, (
        "lowercase case-dispatch variables found — `set -u` will abort the "
        f"heartbeat on every tick: {offenders}"
    )

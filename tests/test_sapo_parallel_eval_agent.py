"""TDD (2026-09-01, user mandate): EVERY checkpoint is evaluated IMMEDIATELY,
and evaluation runs on ALL envs (ASI1/2/3) in parallel.

The old eval agent had two latency defects the mandate kills:
1. It slept 1800s between scans — a new checkpoint waited up to 30 min.
2. The eval loop picked only the NEWEST checkpoint per invocation — older
   unevaluated checkpoints could starve behind it.

The parallel agent (scripts/sapo_parallel_eval_agent.sh — the live repo copy;
a /tmp copy was wiped by the 2026-09-01 Mac reboot and the repo script is the
authoritative deployment) fixes both: a fast scan (default 120s) and a
per-checkpoint loop that evaluates EVERY unevaluated checkpoint newest-first,
one agent per env (ASI1:20646, ASI2:19004, ASI3:20653), each driving the
corrected eval loop (frozen holdout) with DAEMON_PORT set.
"""

from __future__ import annotations

from pathlib import Path

AGENT = Path(__file__).resolve().parents[1] / "scripts" / "sapo_parallel_eval_agent.sh"


def test_agent_scan_is_fast_not_30min() -> None:
    source = AGENT.read_text(encoding="utf-8")
    assert "SCAN" in source
    assert 'sleep "$SCAN"' in source
    # the default scan must be far below the old 1800s
    assert 'SCAN="${4:-120}"' in source


def test_agent_evaluates_every_unevaluated_checkpoint() -> None:
    source = AGENT.read_text(encoding="utf-8")
    # the per-checkpoint loop must enumerate ALL checkpoints and skip only
    # already-evaluated ones (state file), never "only the newest"
    assert "ls -d $RUN_DIR/step_*_adapter" in source
    # one eval at a time (holdout~1.4h), then re-scan picks the next
    assert "one eval at a time" in source
    assert "startswith('done')" in source


def test_agent_is_parameterized_per_env_and_uses_frozen_holdout_loop() -> None:
    source = AGENT.read_text(encoding="utf-8")
    assert 'ENV_NAME="${1:-ASI3}"' in source
    assert 'PORT="${2:-20653}"' in source
    assert 'RUN_DIR="${3:-' in source
    # the corrected eval loop is driven with the env's port
    assert "asi2_loop_eval.sh" in source
    assert 'DAEMON_PORT="$PORT"' in source


def test_agent_remote_root_resolves_to_repo_root_not_doubled_outputs() -> None:
    """2026-09-02 (manager, realtime bug fix): the parallel agent derived
    REMOTE_ROOT as ``dirname RUN_DIR | sed 's|/outputs||' + /outputs`` which
    resolved to the DOUBLED path ``.../quantum-gpt/outputs`` instead of the
    box repo root ``.../quantum-gpt``. Result: ``cd ${REMOTE_ROOT}`` landed in
    ``outputs/outputs``, so the rubric-eval launch ``python3 scripts/...``
    could never be found and NO frozen-holdout verdict ever fired for the
    resume-3 run (only prechecks ran, all gated inert_at_precision/wrote into
    outputs/outputs/). The AGENT must derive REMOTE_ROOT as two ``dirname``s
    up from RUN_DIR = <root>/outputs/<run>.
    """
    from subprocess import run

    run_dir = "/root/work/software/quantum-gpt/outputs/sapo-27b-ai-20260901T015238-resume3"
    expected = "/root/work/software/quantum-gpt"
    # shell: two dirnames up from RUN_DIR
    got = run(
        ["bash", "-c", f'RUN_DIR="{run_dir}"; dirname "$(dirname "$RUN_DIR")"'],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert got == expected
    # the agent script must use the two-dirname derivation, not the sed+outputs one
    source = AGENT.read_text(encoding="utf-8")
    assert 'REMOTE_ROOT="$(dirname "$(dirname "$RUN_DIR")")"' in source
    assert "| sed 's|/outputs||')/outputs" not in source


def test_agent_does_not_stamp_transient_pending_as_done() -> None:
    """2026-09-02 (manager, realtime bug fix): the agent previously wrote
    ``status: done`` whenever the eval leg exited 0 — but asi2_loop_eval.sh
    exits 0 for TRANSIENT states too (PRECHECK_RUNNING / EVAL_PENDING /
    ALREADY_EVALUATED / INERT). That made the agent fire a leg ONCE (often a
    precheck-only run), stamp the checkpoint "done", and never return to
    collect the real frozen-holdout rubric verdict. The agent must keep a
    checkpoint PENDING (retry next scan) unless the leg itself landed a real
    terminal state (status 'done' or 'inert' from the leg's update_state).
    """
    source = AGENT.read_text(encoding="utf-8")
    # the writeback must be state-aware (re-read the entry after the leg)
    assert "json.load(open('$STATE'))" in source
    assert "real = cur.startswith('done') or cur.startswith('inert')" in source
    # it must NOT unconditionally write 'done' on rc==0
    assert "'done' if $RC == 0" not in source

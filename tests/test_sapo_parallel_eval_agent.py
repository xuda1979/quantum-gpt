"""TDD (2026-09-01, user mandate): EVERY checkpoint is evaluated IMMEDIATELY,
and evaluation runs on ALL envs (ASI1/2/3) in parallel.

The old eval agent had two latency defects the mandate kills:
1. It slept 1800s between scans — a new checkpoint waited up to 30 min.
2. The eval loop picked only the NEWEST checkpoint per invocation — older
   unevaluated checkpoints could starve behind it.

The parallel agent (/tmp/sapo_parallel_eval_agent.sh) fixes both: a fast scan
(default 120s) and a per-checkpoint loop that evaluates EVERY unevaluated
checkpoint newest-first, one agent per env (ASI1:20646, ASI2:19004, ASI3:19005),
each driving the corrected eval loop (frozen holdout) with DAEMON_PORT set.
"""

from __future__ import annotations

from pathlib import Path

AGENT = Path("/tmp/sapo_parallel_eval_agent.sh")


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
    assert "ls -t ${CKPT_DIR}" in source
    assert 'grep -q "^${CK}$" "$STATE"' in source
    assert "EVALUATING ${CK}" in source


def test_agent_is_parameterized_per_env_and_uses_frozen_holdout_loop() -> None:
    source = AGENT.read_text(encoding="utf-8")
    assert 'ENV="${1:?env required}"' in source
    assert 'PORT="${2:?port required}"' in source
    assert 'CKPT_DIR="${3:?checkpoint root required}"' in source
    # the corrected eval loop is driven with the env's port
    assert "asi2_loop_eval.sh" in source
    assert 'DAEMON_PORT="$PORT"' in source

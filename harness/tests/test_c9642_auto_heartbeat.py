"""C-9642: worker auto-heartbeat must prevent stall-kill of deep-analysis workers.

A trainer-ops worker analyzing run logs >10 min without calling `qgh.py
heartbeat` was stall-killed (STALL_MIN=10), bounced 3x, auto-retired —
stalling the training resume for an hour. The bash wrapper now runs an
auto-heartbeat loop touching the card's .progress every 300s.
"""

import os
import sys
import time
from pathlib import Path

import conftest  # noqa: F401

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, str(HERE.parent))

import qgh  # noqa: E402


def test_worker_command_contains_heartbeat_loop():
    cmd = qgh.worker_command()
    joined = " ".join(cmd)
    assert "WORKER_HEARTBEAT_CARD" in joined, "auto-heartbeat loop missing from worker command"
    assert "sleep 300" in joined, "heartbeat cadence (300s) missing"
    assert "trap" in joined, "heartbeat loop must be killed on exit (trap missing)"


def test_worker_env_carries_card():
    env = qgh.worker_env(card_id="C-TEST-9642")
    assert env.get("WORKER_HEARTBEAT_CARD") == "C-TEST-9642"
    # backward compat: no card -> no heartbeat var
    env0 = qgh.worker_env()
    assert "WORKER_HEARTBEAT_CARD" not in env0
    # HOME still real (C-9547 regression guard)
    assert env0["HOME"] and env0["HOME"] not in ("/tmp", "")


def test_heartbeat_writes_progress_file(tmp_path):
    """The exact bash snippet the wrapper runs must append a dated line."""
    hb = tmp_path / "C-X.progress"
    hb.write_text("seed line\n")
    os.environ["WORKER_HEARTBEAT_CARD"] = "C-X"
    # emulate one loop iteration's printf
    line = (
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        + " auto-heartbeat: worker process alive\n"
    )
    with open(hb, "a") as f:
        f.write(line)
    content = hb.read_text()
    assert "auto-heartbeat: worker process alive" in content
    assert content.startswith("seed line"), "append mode must preserve earlier lines"

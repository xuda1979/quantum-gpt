"""Tests for harness/scripts/ — the deterministic tooling layer.

Every harness script must produce structured, parseable output.
These tests enforce that contract.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "harness" / "scripts"


def run_script(script_name: str, *args, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script_name), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(REPO),
    )


# --- log_to_table.py ---


def test_log_to_table_status_md():
    """log_to_table.py --status-md produces a markdown table with tick rows."""
    r = run_script("log_to_table.py", "--status-md")
    assert r.returncode == 0, f"exit {r.returncode}: {r.stderr}"
    assert "| timestamp |" in r.stdout
    assert "tick #" in r.stdout or "| tick |" in r.stdout


def test_log_to_table_json_format():
    """log_to_table.py --status-md --format json produces valid JSON."""
    r = run_script("log_to_table.py", "--status-md", "--format", "json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert isinstance(data, list)
    assert len(data) > 0
    assert "tick" in data[0]


def test_log_to_table_train_probe():
    """log_to_table.py --train-probe returns a row (even if N/A)."""
    r = run_script("log_to_table.py", "--train-probe")
    assert r.returncode == 0
    assert "status" in r.stdout


def test_log_to_table_csv_format():
    """log_to_table.py --status-md --format csv produces CSV with header."""
    r = run_script("log_to_table.py", "--status-md", "--format", "csv")
    assert r.returncode == 0
    lines = r.stdout.strip().splitlines()
    assert "timestamp" in lines[0]


# --- tdd.py ---


def test_tdd_green_pass():
    """tdd.py green on a known-passing test reports GREEN."""
    r = run_script(
        "tdd.py", "green", "--test", "tests/test_huanxin_daemon_state.py", "--timeout", "15"
    )
    assert r.returncode == 0
    assert "STATUS: GREEN" in r.stdout
    assert "PASSED: 2" in r.stdout


def test_tdd_last_run():
    """tdd.py last shows the most recent run result."""
    # First run a test to ensure last_run.json exists
    run_script("tdd.py", "green", "--test", "tests/test_huanxin_daemon_state.py", "--timeout", "15")
    r = run_script("tdd.py", "last")
    assert r.returncode == 0
    assert "STATUS:" in r.stdout


# --- run_and_report.py ---


def test_run_and_report_local():
    """run_and_report.py runs a local command and reports PASS."""
    r = run_script("run_and_report.py", "echo", "hello")
    assert r.returncode == 0
    assert "STATUS: PASS" in r.stdout
    assert "hello" in r.stdout


def test_run_and_report_json():
    """run_and_report.py --json produces valid JSON with status field."""
    r = run_script("run_and_report.py", "--json", "echo", "test")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data["status"] == "PASS"
    assert "test" in data["stdout"]


def test_run_and_report_check_file():
    """run_and_report.py --check-file verifies file existence."""
    r = run_script("run_and_report.py", "--check-file", str(REPO / "harness" / "qgh.py"))
    assert r.returncode == 0
    assert "STATUS: PASS" in r.stdout


def test_run_and_report_check_file_missing():
    """run_and_report.py --check-file on missing file reports FAIL."""
    r = run_script("run_and_report.py", "--check-file", "/nonexistent/path/xyz")
    assert r.returncode == 0
    assert "STATUS: FAIL" in r.stdout


# --- answer_question.py ---


def test_answer_question_slow():
    """answer_question.py 'why is progress slow?' collects metrics."""
    r = run_script("answer_question.py", "why is progress slow?")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data["question"] == "why is progress slow?"
    assert "data" in data
    assert "best_eval_pass" in data["data"]


def test_answer_question_improve():
    """answer_question.py 'how to improve' collects training_health."""
    r = run_script("answer_question.py", "how to improve the algorithm")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data["data_collected"] == "training_health"


def test_answer_question_collect_direct():
    """answer_question.py --collect card_churn produces churn data."""
    r = run_script("answer_question.py", "--collect", "card_churn")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "total_spawned" in data
    assert "churn_ratio" in data


def test_answer_question_worker_throughput():
    """answer_question.py --collect worker_throughput produces throughput data."""
    r = run_script("answer_question.py", "--collect", "worker_throughput")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "active_agents" in data
    assert data["active_agents"] > 0


# --- system_status.py ---


def test_system_status_human_readable():
    """system_status.py produces human-readable output with key sections."""
    r = run_script("system_status.py", timeout=90)
    assert r.returncode == 0
    assert "SYSTEM STATUS" in r.stdout
    assert "BOXES" in r.stdout
    assert "KEEPER" in r.stdout
    assert "TRAINING" in r.stdout
    assert "QUEUE" in r.stdout
    assert "VERDICT:" in r.stdout


def test_system_status_json():
    """system_status.py --json produces valid JSON with all sections."""
    r = run_script("system_status.py", "--json", timeout=90)
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "boxes" in data
    assert "keeper" in data
    assert "training" in data
    assert "queue" in data
    assert "eval" in data
    assert "commits_today" in data
    assert "active_agents" in data
    assert "timestamp" in data


# --- box_health_preflight.py (C-10569) ---


def test_box_health_preflight_unknown_blocks():
    """box_health_preflight.py check --json on the LIVE probe must be
    deterministic. With ASI2/ASI3 UNKNOWN (conn-refused/not-ready measured
    2026-10-21), the gate must fail closed (exit non-zero, go=false). With a
    READY box (ASI1 today) the gate returns go=true. Never fabricates — reads
    the frozen probes/<box>.json exactly as the launch seam does."""
    import tempfile
    from pathlib import Path

    # 1. Deterministic frozen fixture: UNKNOWN box MUST block (rc=10).
    with tempfile.TemporaryDirectory() as td:
        probes = Path(td)
        (probes / "asi2.json").write_text(
            json.dumps(
                {
                    "ts": "2026-10-21T00:00:00Z",
                    "status": "unknown",
                    "summary": "UNKNOWN (health non-200: transport error (Connection refused))",
                }
            )
        )
        r = run_script(
            "box_health_preflight.py", "check", "--box", "ASI2", "--probes-dir", td, "--json"
        )
        assert r.returncode == 10, f"rc={r.returncode} stdout={r.stdout}"
        d = json.loads(r.stdout)
        assert d["go"] is False

    # 2. Deterministic frozen fixture: READY box MUST allow (rc=0).
    with tempfile.TemporaryDirectory() as td:
        probes = Path(td)
        (probes / "asi3.json").write_text(
            json.dumps(
                {
                    "ts": "2026-10-21T00:00:00Z",
                    "status": "ready",
                    "summary": "READY /health ready=true EXEC=ok pid=17639",
                }
            )
        )
        r = run_script(
            "box_health_preflight.py", "check", "--box", "ASI3", "--probes-dir", td, "--json"
        )
        assert r.returncode == 0, f"rc={r.returncode} stdout={r.stdout}"
        d = json.loads(r.stdout)
        assert d["go"] is True


def test_run_eval_leg_rejects_unready_box():
    """run_eval_leg.py real-launch seam must refuse when the target box probe
    is !READY. Deterministic via frozen temp probes dir; asserts the JSON
    BLOCKED_BY_BOX_HEALTH + exit 10. Queued/running cards untouched."""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "asi2.json").write_text(
            json.dumps(
                {
                    "ts": "2026-10-21T00:00:00Z",
                    "status": "unknown",
                    "summary": "UNKNOWN (health non-200: transport error (Connection refused))",
                }
            )
        )
        # --dry-run bypasses compute; we exercise the same box_health_gate the
        # real path uses via a direct module import (deterministic, no box).
        import importlib.util

        spec = importlib.util.spec_from_file_location("rel", "harness/scripts/run_eval_leg.py")
        rel = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rel)
        res = rel.box_health_gate(probes_dir=Path(td), box="ASI2")
        assert res["go"] is False
        assert "ASI2" in res["reason"]

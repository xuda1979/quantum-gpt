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


def run_script(script_name: str, *args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script_name), *args],
        capture_output=True,
        text=True,
        timeout=30,
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

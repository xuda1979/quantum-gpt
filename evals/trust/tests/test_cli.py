"""End-to-end CLI tests for evals.trust — proves the full workflow."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_PY = sys.executable


def _run_cli(args: list[str], env: dict | None = None) -> subprocess.CompletedProcess:
    e = dict(os.environ)
    e["PYTHONPATH"] = str(_REPO) + os.pathsep + e.get("PYTHONPATH", "")
    if env:
        e.update(env)
    return subprocess.run([_PY, "-m", "evals.trust.cli.main", *args],
                          capture_output=True, text=True, env=e, timeout=120)


@pytest.fixture
def mini_suite(tmp_path):
    """Create a 2-task mini suite where tests check candidate content.

    Each test loads the candidate module and checks that it defines a
    ``flag`` variable equal to ``"good"``. This lets us distinguish a
    passing candidate (with flag="good") from an empty/mock candidate.
    """
    tests_body = (
        "import importlib.util\n"
        "def run_tests(c):\n"
        "    spec = importlib.util.spec_from_file_location('cand', c)\n"
        "    m = importlib.util.module_from_spec(spec)\n"
        "    spec.loader.exec_module(m)\n"
        "    if getattr(m, 'flag', None) == 'good':\n"
        "        return {'passed': True, 'details': ['ok']}\n"
        "    return {'passed': False, 'details': ['flag != good']}\n"
    )
    for tid in ("t1", "t2"):
        td = tmp_path / "tasks" / tid
        td.mkdir(parents=True)
        (td / "task.json").write_text(json.dumps({
            "id": tid, "name": tid, "domain": "quantum", "category": "x",
        }))
        (td / "tests.py").write_text(tests_body)
        (td / "candidate.py").write_text('flag = "good"\n')
    lock = tmp_path / "suite.lock.json"
    r = _run_cli(["suite-init", "--tasks", str(tmp_path / "tasks"), "--out", str(lock)])
    assert r.returncode == 0, r.stderr
    return tmp_path, lock


def test_cli_suite_init_and_verify(mini_suite):
    tmp_path, lock = mini_suite
    r = _run_cli(["suite-verify", "--suite", str(lock)])
    assert r.returncode == 0
    assert "OK" in r.stdout


def test_cli_suite_verify_detects_tamper(mini_suite):
    tmp_path, lock = mini_suite
    (tmp_path / "tasks" / "t1" / "tests.py").write_text("# TAMPER\n")
    r = _run_cli(["suite-verify", "--suite", str(lock)])
    assert r.returncode == 1
    assert "FAIL" in r.stdout


def test_cli_run_mock_and_verify(mini_suite):
    tmp_path, lock = mini_suite
    out = tmp_path / "run-mock"
    r = _run_cli(["run", "--suite", str(lock), "--out", str(out),
                  "--mock", "--model-label", "mock", "--k", "1"])
    assert r.returncode == 0, r.stderr
    assert (out / "ledger.db").is_file()
    assert (out / "recipe.json").is_file()
    assert (out / "summary.json").is_file()
    # mock produces empty code → 0/2 pass
    s = json.loads((out / "summary.json").read_text())
    assert s["n_pass"] == 0
    # verify should pass (hashes intact, rescore agrees)
    r2 = _run_cli(["verify", "--run", str(out)])
    assert r2.returncode == 0, r2.stderr
    assert "OK" in r2.stdout


def test_cli_run_exec_with_good_candidates(mini_suite):
    """Run with an exec-command that emits passing candidates."""
    tmp_path, lock = mini_suite
    gen = tmp_path / "gen.sh"
    gen.write_text('#!/bin/bash\necho \'flag = "good"\'\n')
    gen.chmod(0o755)
    out = tmp_path / "run-exec"
    r = _run_cli(["run", "--suite", str(lock), "--out", str(out),
                  "--exec-command", str(gen), "--model-label", "exec", "--k", "1"])
    assert r.returncode == 0, r.stderr
    s = json.loads((out / "summary.json").read_text())
    assert s["n_pass"] == 2


def test_cli_audit_backs_correct_claims(mini_suite):
    tmp_path, lock = mini_suite
    out = tmp_path / "run-mock"
    _run_cli(["run", "--suite", str(lock), "--out", str(out),
              "--mock", "--model-label", "mock", "--k", "1"])
    # mock → 0/2 pass
    report = tmp_path / "r.md"
    report.write_text("# R\n\n- 0/2 passed\n- n_tasks: 2\n- pass@1 = 0.0\n")
    r = _run_cli(["audit", "--run", str(out), "--report", str(report)])
    assert r.returncode == 0, r.stdout + r.stderr
    assert "unbacked=0" in r.stdout


def test_cli_audit_flags_wrong_claims(mini_suite):
    tmp_path, lock = mini_suite
    out = tmp_path / "run-mock"
    _run_cli(["run", "--suite", str(lock), "--out", str(out),
              "--mock", "--model-label", "mock", "--k", "1"])
    report = tmp_path / "wrong.md"
    report.write_text("# W\n\n- 2/2 passed\n- pass@1 = 1.0\n")
    r = _run_cli(["audit", "--run", str(out), "--report", str(report)])
    assert r.returncode == 1
    assert "unbacked=" in r.stdout


def test_cli_report(mini_suite):
    tmp_path, lock = mini_suite
    out = tmp_path / "run-mock"
    _run_cli(["run", "--suite", str(lock), "--out", str(out),
              "--mock", "--model-label", "mock", "--k", "1"])
    r = _run_cli(["report", "--run", str(out)])
    assert r.returncode == 0
    report = out / "REPORT.md"
    assert report.is_file()
    text = report.read_text()
    assert "run_hash" in text
    assert "pass_at_1" in text


def test_cli_reproduce(mini_suite):
    tmp_path, lock = mini_suite
    out = tmp_path / "run-mock"
    _run_cli(["run", "--suite", str(lock), "--out", str(out),
              "--mock", "--model-label", "mock", "--k", "1"])
    r = _run_cli(["reproduce", "--run", str(out)])
    assert r.returncode == 0
    assert "recipe identical" in r.stdout


def test_cli_compare(mini_suite):
    tmp_path, lock = mini_suite
    base = tmp_path / "base"; adap = tmp_path / "adap"
    _run_cli(["run", "--suite", str(lock), "--out", str(base),
              "--mock", "--model-label", "base", "--k", "1"])
    _run_cli(["run", "--suite", str(lock), "--out", str(adap),
              "--mock", "--model-label", "adap", "--k", "1"])
    r = _run_cli(["compare", "--base", str(base), "--adapter", str(adap)])
    assert r.returncode == 0
    assert "delta" in r.stdout


def test_cli_verify_detects_tamper(mini_suite):
    tmp_path, lock = mini_suite
    out = tmp_path / "run-mock"
    _run_cli(["run", "--suite", str(lock), "--out", str(out),
              "--mock", "--model-label", "mock", "--k", "1"])
    # tamper with a tests.py after the run
    (tmp_path / "tasks" / "t1" / "tests.py").write_text("# TAMPER\n")
    r = _run_cli(["verify", "--run", str(out), "--skip-rescore"])
    assert r.returncode == 1
    assert "tests.py changed" in r.stdout or "suite_hash mismatch" in r.stdout

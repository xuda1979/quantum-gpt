"""Self-tests for evals.trust.core.* — proves the harness is correct."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure repo root is importable when run via `pytest` from anywhere.
_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from evals.trust.core import audit, hashing, ledger, repro, sandbox, scoring, suite


# ── hashing ─────────────────────────────────────────────────────────────────

def test_hash_text_stable():
    # SHA-256("hello") = 2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
    expected = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    assert hashing.hash_text("hello") == expected
    assert hashing.hash_text("hello") == hashing.hash_text("hello")


def test_hash_json_canonical_keys():
    a = hashing.hash_json({"a": 1, "b": 2})
    b = hashing.hash_json({"b": 2, "a": 1})
    assert a == b, "canonical JSON must be order-independent"


def test_hash_file_round_trip(tmp_path):
    p = tmp_path / "x.txt"
    p.write_bytes(b"abc")
    assert hashing.hash_file(p) == hashlib.sha256(b"abc").hexdigest()


def test_is_hash():
    assert hashing.is_hash("a" * 64)
    assert not hashing.is_hash("a" * 63)
    assert not hashing.is_hash("g" * 64)  # not hex


# ── scoring ─────────────────────────────────────────────────────────────────

def test_pass_at_k_unbiased_estimator():
    # n=10, c=5, k=5 → 1 - C(5,5)/C(10,5) = 1 - 1/252
    assert abs(scoring.pass_at_k(10, 5, 5) - (1 - 1/252)) < 1e-9


def test_pass_at_k_zero_passes():
    assert scoring.pass_at_k(10, 0, 5) == 0.0


def test_pass_at_k_all_pass():
    assert scoring.pass_at_k(10, 10, 5) == 1.0


def test_pass_at_k_k_ge_n():
    assert scoring.pass_at_k(3, 1, 5) == 1.0  # k>=n, c>0 → 1.0


def test_score_task_any_pass_is_pass_at_1():
    v = [
        {"sample_index": 0, "judge": "deterministic", "passed": False, "failure_category": "assertion"},
        {"sample_index": 1, "judge": "deterministic", "passed": True, "failure_category": None},
    ]
    s = scoring.score_task(task_id="t", k=2, verdicts=v)
    assert s.pass_at_1 == 1.0
    assert s.n_pass_det == 1


def test_score_task_disagreement_flag():
    v = [
        {"sample_index": 0, "judge": "deterministic", "passed": True, "failure_category": None},
        {"sample_index": 0, "judge": "llm", "passed": False, "failure_category": None},
    ]
    s = scoring.score_task(task_id="t", k=1, verdicts=v)
    assert s.judge_disagreement is True


# ── suite ────────────────────────────────────────────────────────────────────

def test_suite_discover_and_lock(tmp_path):
    # build a fake task
    td = tmp_path / "t1"
    td.mkdir()
    (td / "task.json").write_text(json.dumps({
        "id": "t1", "name": "T1", "domain": "quantum", "category": "x",
    }))
    (td / "tests.py").write_text("def run_tests(c):\n    return {'passed': True, 'details': []}\n")
    tasks = suite.discover_tasks(tmp_path)
    assert len(tasks) == 1
    assert tasks[0].task_id == "t1"
    lock = suite.write_lock(tasks, out_path=tmp_path / "lock.json", source_dir=str(tmp_path))
    assert "suite_hash" in lock
    # verify should pass
    res = suite.verify_lock(tmp_path / "lock.json")
    assert res["ok"] is True


def test_suite_verify_detects_tamper(tmp_path):
    td = tmp_path / "t1"
    td.mkdir()
    (td / "task.json").write_text(json.dumps({"id": "t1", "name": "T1", "domain": "q", "category": "x"}))
    (td / "tests.py").write_text("def run_tests(c):\n    return {'passed': True, 'details': []}\n")
    tasks = suite.discover_tasks(tmp_path)
    suite.write_lock(tasks, out_path=tmp_path / "lock.json", source_dir=str(tmp_path))
    # tamper
    (td / "tests.py").write_text("# TAMPER\n")
    res = suite.verify_lock(tmp_path / "lock.json")
    assert res["ok"] is False
    assert any(m["task_id"] == "t1" for m in res["mismatches"])


# ── sandbox ─────────────────────────────────────────────────────────────────

def test_sandbox_passes_reference_candidate():
    repo_task = _REPO / "evals/tasks/quantum/grover_oracle_diffusion"
    if not repo_task.is_dir():
        pytest.skip("grover task not present")
    code = (repo_task / "candidate.py").read_text()
    res = sandbox.run_test_hermetic(
        task_dir=repo_task, test_file="tests.py", candidate_code=code,
        timeout_sec=30,
    )
    assert res.passed is True
    assert res.returncode == 0


def test_sandbox_catches_broken_candidate():
    repo_task = _REPO / "evals/tasks/quantum/grover_oracle_diffusion"
    if not repo_task.is_dir():
        pytest.skip("grover task not present")
    res = sandbox.run_test_hermetic(
        task_dir=repo_task, test_file="tests.py",
        candidate_code="def grover_search(*a, **k):\n    return [0.5]\n",
        timeout_sec=30,
    )
    assert res.passed is False
    assert res.failure_category in {"assertion", "runtime"}


def test_sandbox_is_hermetic_no_site_packages(tmp_path):
    # The sandbox must not see the host's site-packages; verify that a
    # candidate importing a non-stdlib module fails cleanly.
    td = tmp_path / "t"
    td.mkdir()
    (td / "task.json").write_text(json.dumps({"id": "t", "name": "T", "domain": "q", "category": "x"}))
    (td / "tests.py").write_text(
        "def run_tests(c):\n"
        "    import sys\n"
        "    # if numpy is visible, fail\n"
        "    try:\n"
        "        import numpy\n"
        "        return {'passed': False, 'details': ['numpy should not be visible']}\n"
        "    except ImportError:\n"
        "        return {'passed': True, 'details': ['numpy correctly hidden']}\n"
    )
    res = sandbox.run_test_hermetic(
        task_dir=td, test_file="tests.py", candidate_code="# stub\n",
        timeout_sec=30,
    )
    assert res.passed is True, f"sandbox leaked site-packages: {res.details}"


# ── ledger ──────────────────────────────────────────────────────────────────

def test_ledger_round_trip(tmp_path):
    L = ledger.Ledger(tmp_path / "l.db")
    tid = L.register_task(
        task_id="t1", name="T1", domain="q", category="x",
        task_json_hash="h1", tests_py_hash="h2", candidate_ref_hash="h3",
    )
    sid = L.register_suite(suite_hash="sh", source_dir=".", n_tasks=1, task_ids=["t1"])
    mid = L.register_model(label="m", base_path="p", base_hash=None,
                           adapter_path=None, adapter_hash=None, model_kind="base")
    rid = L.register_run(
        run_hash="rh", created_at_utc="2026-01-01T00:00:00+00:00",
        suite_id=sid, model_id=mid, prompt_template_id=None, k=1,
        temperature=None, seed=42, max_new_tokens=512,
        python_version="3.14", platform="linux", status="running",
    )
    smid = L.record_sample(
        run_id=rid, task_id="t1", sample_index=0, candidate_code="print('hi')",
        generated_at_utc="2026-01-01T00:00:00+00:00", gen_sec=0.1, finish_reason="ok",
    )
    L.record_verdict(
        sample_id=smid, judge="deterministic", passed=True, details=["ok"],
        failure_category=None, test_stdout_hash="sh1", test_stderr_hash="sh2",
        test_returncode=0,
    )
    summ = L.run_summary(rid)
    assert summ["n_tasks"] == 1
    assert summ["n_pass"] == 1
    assert summ["pass_at_1"] == 1.0
    L.close()


# ── audit ───────────────────────────────────────────────────────────────────

def test_audit_extracts_and_backs_claims(tmp_path):
    L = ledger.Ledger(tmp_path / "l.db")
    # set up a run with 2 tasks, 1 pass
    L.register_task(task_id="t1", name="T1", domain="q", category="x",
                    task_json_hash="h1", tests_py_hash="h2", candidate_ref_hash="h3")
    L.register_task(task_id="t2", name="T2", domain="q", category="x",
                    task_json_hash="h1", tests_py_hash="h2", candidate_ref_hash="h3")
    sid = L.register_suite(suite_hash="sh", source_dir=".", n_tasks=2, task_ids=["t1", "t2"])
    mid = L.register_model(label="m", base_path="p", base_hash=None,
                           adapter_path=None, adapter_hash=None, model_kind="base")
    rid = L.register_run(
        run_hash="rh", created_at_utc="2026-01-01T00:00:00+00:00",
        suite_id=sid, model_id=mid, prompt_template_id=None, k=1,
        temperature=None, seed=42, max_new_tokens=512,
        python_version="3.14", platform="linux", status="running",
    )
    for tid, passed in [("t1", True), ("t2", False)]:
        smid = L.record_sample(
            run_id=rid, task_id=tid, sample_index=0, candidate_code="x",
            generated_at_utc="2026-01-01T00:00:00+00:00", gen_sec=0.0, finish_reason="ok",
        )
        L.record_verdict(
            sample_id=smid, judge="deterministic", passed=passed,
            details=["d"], failure_category=None if passed else "assertion",
            test_stdout_hash="s", test_stderr_hash="s", test_returncode=0,
        )
    report = tmp_path / "r.md"
    report.write_text("# R\n\n- 1/2 passed\n- pass@1 = 0.5\n- n_tasks: 2\n")
    res = audit.audit_report(ledger=L, run_id=rid, report_path=report)
    assert res["passed"] is True
    assert res["n_backed"] >= 2
    L.close()


def test_audit_flags_wrong_claims(tmp_path):
    L = ledger.Ledger(tmp_path / "l.db")
    L.register_task(task_id="t1", name="T1", domain="q", category="x",
                    task_json_hash="h1", tests_py_hash="h2", candidate_ref_hash="h3")
    sid = L.register_suite(suite_hash="sh", source_dir=".", n_tasks=1, task_ids=["t1"])
    mid = L.register_model(label="m", base_path="p", base_hash=None,
                           adapter_path=None, adapter_hash=None, model_kind="base")
    rid = L.register_run(
        run_hash="rh", created_at_utc="2026-01-01T00:00:00+00:00",
        suite_id=sid, model_id=mid, prompt_template_id=None, k=1,
        temperature=None, seed=42, max_new_tokens=512,
        python_version="3.14", platform="linux", status="running",
    )
    smid = L.record_sample(
        run_id=rid, task_id="t1", sample_index=0, candidate_code="x",
        generated_at_utc="2026-01-01T00:00:00+00:00", gen_sec=0.0, finish_reason="ok",
    )
    L.record_verdict(
        sample_id=smid, judge="deterministic", passed=True, details=["d"],
        failure_category=None, test_stdout_hash="s", test_stderr_hash="s", test_returncode=0,
    )
    report = tmp_path / "wrong.md"
    report.write_text("# W\n\n- 0/1 passed\n- pass@1 = 0.0\n")
    res = audit.audit_report(ledger=L, run_id=rid, report_path=report)
    assert res["passed"] is False
    assert res["n_unbacked"] >= 2
    L.close()


# ── repro ───────────────────────────────────────────────────────────────────

def test_recipe_hash_stable():
    r1 = repro.build_recipe(
        suite_hash="a", suite_lock_path="x", model_label="m",
        model_base_path="p", model_base_hash=None, model_adapter_path=None,
        model_adapter_hash=None, model_kind="base", prompt_style="s",
        prompt_version="v", prompt_template_hash="h", k=1, temperature=None,
        seed=42, max_new_tokens=512,
    )
    r2 = repro.build_recipe(
        suite_hash="a", suite_lock_path="x", model_label="m",
        model_base_path="p", model_base_hash=None, model_adapter_path=None,
        model_adapter_hash=None, model_kind="base", prompt_style="s",
        prompt_version="v", prompt_template_hash="h", k=1, temperature=None,
        seed=42, max_new_tokens=512,
    )
    assert r1.hash() == r2.hash()


def test_recipe_drift_detected():
    r1 = repro.build_recipe(
        suite_hash="a", suite_lock_path="x", model_label="m",
        model_base_path="p", model_base_hash=None, model_adapter_path=None,
        model_adapter_hash=None, model_kind="base", prompt_style="s",
        prompt_version="v", prompt_template_hash="h", k=1, temperature=None,
        seed=42, max_new_tokens=512,
    )
    r2 = repro.build_recipe(
        suite_hash="b", suite_lock_path="x", model_label="m",
        model_base_path="p", model_base_hash=None, model_adapter_path=None,
        model_adapter_hash=None, model_kind="base", prompt_style="s",
        prompt_version="v", prompt_template_hash="h", k=1, temperature=None,
        seed=42, max_new_tokens=512,
    )
    cmp = repro.compare_recipes(r1, r2)
    assert cmp["identical"] is False
    assert any(d["field"] == "suite_hash" for d in cmp["diffs"])

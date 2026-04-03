"""Fast local GRPO pipeline smoke tests — no model loading, runs in < 10s.

Validates the full: discover_tasks → load_harness → score_candidate → reward chain.
Catches harness bugs, reward regressions, and benchmark file issues before ai2 runs.
"""
from __future__ import annotations

import importlib.util
import json
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "evals" / "tasks"
TRAINING_BM = ROOT / "evals" / "benchmarks" / "quantum_grpo_training_v1.txt"

from training.grpo_utils import build_reward_breakdown, reward_signal_stats, summarize_python_interface
import torch


def _load_harness(tests_py: Path):
    spec = importlib.util.spec_from_file_location(f"tests_{uuid.uuid4().hex[:6]}", str(tests_py))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_training_task_ids() -> set[str]:
    ids = set()
    for line in TRAINING_BM.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            ids.add(line)
    return ids


def _all_quantum_tasks() -> list[dict]:
    tasks = []
    quantum_dir = TASKS_DIR / "quantum"
    if not quantum_dir.exists():
        return tasks
    for task_dir in sorted(quantum_dir.iterdir()):
        if not task_dir.is_dir():
            continue
        task_json = task_dir / "task.json"
        tests_py = task_dir / "tests.py"
        candidate_py = task_dir / "candidate.py"
        if task_json.exists() and tests_py.exists():
            meta = json.loads(task_json.read_text())
            tasks.append({
                "meta": meta,
                "task_dir": task_dir,
                "tests_py": tests_py,
                "candidate_py": candidate_py,
            })
    return tasks


# ── Task discovery ────────────────────────────────────────────────────────────

def test_all_quantum_tasks_discoverable():
    tasks = _all_quantum_tasks()
    assert len(tasks) >= 13, f"Expected ≥13 quantum tasks, found {len(tasks)}"


def test_all_training_benchmark_tasks_exist_on_disk():
    training_ids = _load_training_task_ids()
    found = {
        json.loads((t["task_dir"] / "task.json").read_text()).get("id")
        for t in _all_quantum_tasks()
    }
    missing = training_ids - found
    assert not missing, f"Tasks in benchmark but missing on disk: {missing}"


# ── Test harness loading ──────────────────────────────────────────────────────

@pytest.mark.parametrize("task", _all_quantum_tasks(), ids=lambda t: t["meta"].get("id", t["task_dir"].name))
def test_task_harness_loads(task):
    """Every task's tests.py must be importable."""
    harness = _load_harness(task["tests_py"])
    assert hasattr(harness, "run_tests"), f"{task['tests_py']} missing run_tests()"


# ── Reference candidate passes its own tests ─────────────────────────────────

@pytest.mark.parametrize("task", _all_quantum_tasks(), ids=lambda t: t["meta"].get("id", t["task_dir"].name))
def test_reference_candidate_passes(task):
    """The bundled candidate.py must pass all tests for this task."""
    if not task["candidate_py"].exists():
        pytest.skip("No reference candidate.py")
    harness = _load_harness(task["tests_py"])
    result = harness.run_tests(str(task["candidate_py"]))
    assert result.get("passed"), f"Reference candidate failed: {result.get('details')}"


# ── Reward breakdown on reference candidate ───────────────────────────────────

@pytest.mark.parametrize("task", _all_quantum_tasks(), ids=lambda t: t["meta"].get("id", t["task_dir"].name))
def test_reference_candidate_gets_full_reward(task):
    """Reference solution should score total_reward close to 1.0."""
    if not task["candidate_py"].exists():
        pytest.skip("No reference candidate.py")
    harness = _load_harness(task["tests_py"])
    result = harness.run_tests(str(task["candidate_py"]))
    code = task["candidate_py"].read_text()
    reward = build_reward_breakdown(
        code=code,
        result=result,
        required_interface=summarize_python_interface(code),
        detail_budget=4,
        pass_weight=0.6,
        syntax_weight=0.1,
        interface_weight=0.15,
        verifier_weight=0.15,
    )
    assert reward["pass_reward"] == 1.0, "Reference candidate should pass all tests"
    assert reward["total_reward"] >= 0.9, f"Reference total_reward={reward['total_reward']:.3f}"


# ── Empty candidate gets near-zero reward ────────────────────────────────────

def test_empty_candidate_gets_near_zero_reward():
    task = next(t for t in _all_quantum_tasks() if "qaoa" in t["meta"].get("id", ""))
    harness = _load_harness(task["tests_py"])
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write("")
        tmp = f.name
    try:
        result = harness.run_tests(tmp)
    except Exception:
        result = {"passed": False, "details": ["error"]}
    finally:
        os.unlink(tmp)
    reward = build_reward_breakdown(
        code="",
        result=result,
        required_interface=[],
        detail_budget=4,
        pass_weight=0.6,
        syntax_weight=0.1,
        interface_weight=0.15,
        verifier_weight=0.15,
    )
    assert reward["total_reward"] < 0.2, f"Empty candidate should score < 0.2, got {reward['total_reward']}"


# ── Group reward variance (key GRPO health check) ────────────────────────────

def test_diverse_group_has_sufficient_reward_variance():
    """A realistic diverse group of 8 completions must exceed min_reward_std=0.02."""
    required = ["maxcut_cost(bits, edges)", "brute_force_maxcut(n, edges)", "qaoa_cost_landscape(n, edges)"]
    candidates_code = [
        "",
        "x = 1",
        "def maxcut_cost(bits, edges):\n    return 0",
        "def maxcut_cost(bits, edges):\n    return sum(1 for a,b in edges if bits[a]!=bits[b])",
        "def maxcut_cost(b,e):\n    pass\ndef brute_force_maxcut(n,e):\n    pass",
        "\n".join(f"line_{i}=0" for i in range(60)),
        "def maxcut_cost(bits, edges):\n    return len(edges)\ndef brute_force_maxcut(n, edges):\n    return '0'*n, 0",
        "def maxcut_cost(bits,edges):\n    return sum(1 for a,b in edges if bits[a]!=bits[b])\ndef brute_force_maxcut(n,edges):\n    best,bc='0'*n,0\n    for i in range(2**n):\n        bs=format(i,'0'+str(n)+'b')\n        c=maxcut_cost(bs,edges)\n        if c>bc: best,bc=bs,c\n    return best,bc\ndef qaoa_cost_landscape(n,edges):\n    return sorted([(format(i,'0'+str(n)+'b'),maxcut_cost(format(i,'0'+str(n)+'b'),edges)) for i in range(2**n)],key=lambda x:-x[1])",
    ]
    rewards = []
    pass_r, syntax_r, iface_r, verif_r, brev_r = [], [], [], [], []
    for code in candidates_code:
        r = build_reward_breakdown(
            code=code,
            result={"passed": False, "details": ["f1", "f2", "f3", "f4"]},
            required_interface=required,
            detail_budget=4,
            pass_weight=0.6, syntax_weight=0.1,
            interface_weight=0.15, verifier_weight=0.15,
            brevity_weight=0.05,
        )
        rewards.append(r["total_reward"])
        pass_r.append(r["pass_reward"]); syntax_r.append(r["syntax_reward"])
        iface_r.append(r["interface_reward"]); verif_r.append(r["verifier_reward"])
        brev_r.append(r["brevity_reward"])

    stats = reward_signal_stats(
        torch.tensor(rewards), torch.tensor(pass_r), torch.tensor(syntax_r),
        torch.tensor(iface_r), torch.tensor(verif_r), torch.tensor(brev_r),
    )
    assert stats["signal_std"] >= 0.02, (
        f"Diverse group signal_std={stats['signal_std']:.4f} < 0.02 — GRPO would skip every step"
    )

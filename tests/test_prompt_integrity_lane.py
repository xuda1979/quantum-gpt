"""PROMPT-INTEGRITY lane (2026-09-01 SAPO dev-ops audit).

Locks the five audit contracts across the train + eval pipeline:

  (1) prompt-contract stability: same prompt text -> same hash; the public
      eval contract includes task metadata; the TRAIN prompt carries task
      metadata and never embeds reference code / tests.py content.
  (2) holdout contamination: the current training manifests (v7/v8/v9) are
      id-disjoint from the frozen 18-task promotion holdout, and the v9
      task_prompts (verbatim quantum_rl_questions_v2.jsonl questions) have
      no near-duplicate (difflib ratio < 0.8) of any holdout prompt.
  (3) reference-code leakage: the interface summaries that enter prompts are
      signatures only -- never function bodies.
  (4) EVAL_HIDE_REFERENCE: the ASI2 rubric eval prompt is question-only in
      BOTH flag states -- the reference solution cannot enter the prompt.
  (5) behavior-hint hygiene: prompt-visible hints derived from tests.py must
      not leak decisive numeric answers (exact expected values / answer
      bounds); structural sizes (amplitudes, entries, shape, ...) stay.

The frozen holdout (evals/tasks/** and sapo_promotion_holdout_v1_18.txt)
is read-only here.
"""

from __future__ import annotations

import difflib
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evals.runner.frozen_contract import (
    aggregate_sha256,
    sha256_file,
    sha256_text,
)
from evals.runner.public_task_spec import build_public_task_spec, extract_public_api
from training.grpo_trainer import build_prompt, task_behavior_hints
from training.grpo_utils import (
    extract_behavior_hints_from_test_source,
    summarize_python_interface,
)

ROOT = Path(__file__).resolve().parents[1]
HOLDOUT_MANIFEST = ROOT / "evals/benchmarks/sapo_promotion_holdout_v1_18.txt"
V9_MANIFEST = ROOT / "evals/benchmarks/quantum_grpo_training_v9_rl_questions_v2.txt"
V8_MANIFEST = ROOT / "evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt"
V7_MANIFEST = ROOT / "evals/benchmarks/quantum_grpo_training_v7_targeted_integrity.txt"
V9_BUILDER = ROOT / "scripts/build_grpo_v9_manifest.py"

DECISIVE_HINT_MARKERS: dict[str, list[str]] = {
    # task dir -> substrings that must NOT appear in prompt-visible hints
    "quantum_rl_v2_shor_order_finding": [
        "(3 and 5)",  # the factor answer
        "order of 8 mod 15 is 4",  # the order-finding answer
    ],
    "quantum_rl_v2_qaoa_p2_maxcut": [
        "cut_0101",  # graded cut value of a named bitstring
        "cut_0011",
        "expected 4",  # best-maxcut answer
        "expected 3",
    ],
    "quantum_three_qubit_entropy": [
        "expected 1.000000",  # reduced-entropy answer
    ],
    "quantum_qft_periodic_state": [
        "expected 0.500000",  # QFT amplitude answer
    ],
    "quantum_vqe_heisenberg_energy": [
        "need<=-2.600000",  # energy answer bound
    ],
    "quantum_qaoa_ring4_landscape": [
        "need>=2.950000",  # QAOA expectation answer bound
        "best_maxcut_value=0, expected 4",
    ],
    "quantum_qml_variational_classifier": [
        "need>=0.875000",  # accuracy answer bound
    ],
    "bitstring_maxcut_landscape": [
        "should be 0",
        "should be 2",
        "should be 3",
    ],
    "quantum_bell_basis_discrimination": [
        "need>=0.990000",
    ],
}

# structural hints that MUST survive suppression
STRUCTURAL_HINT_MARKERS: dict[str, list[str]] = {
    "quantum_rl_v2_shor_order_finding": [
        "expected 2048",  # shots count (question states it)
        "16x16",  # matrix shape
    ],
    "quantum_rl_v2_w_state_entropy": [
        "expected 8 amplitudes",
    ],
    "quantum_rl_v2_depolarizing_kraus": [
        "kraus_count",  # structural op count
        "channel_trace",  # trace identity
    ],
    "quantum_three_qubit_entropy": [
        "expected 16",  # pt entries
        "expected 2x2",  # matrix shape
    ],
    "quantum_trotter_heisenberg_evolution": [
        "need<=0.050000",  # error tolerance
    ],
    "bitstring_maxcut_landscape": [
        "landscape length",  # structural size
    ],
}


def _manifest_ids(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def _task_dir(task_id: str) -> Path:
    for task_json in (ROOT / "evals/tasks").glob("*/*/task.json"):
        meta = json.loads(task_json.read_text(encoding="utf-8"))
        if str(meta.get("id", task_json.parent.name)) == task_id:
            return task_json.parent
    return ROOT / "evals/tasks/quantum" / task_id


def _load_task(task_id: str) -> dict:
    task_dir = _task_dir(task_id)
    return {
        "meta": json.loads((task_dir / "task.json").read_text(encoding="utf-8")),
        "task_dir": task_dir,
        "tests_py": task_dir / "tests.py",
    }


def _task_prompt_text(task_id: str) -> str:
    """Model-visible question text: task_prompt > description > name.

    Legacy holdout bundles (e.g. braket_bell_state) carry only a name; the
    name is the model-visible identity and the best proxy for the overlap
    check when no question text exists.
    """
    meta = json.loads((_task_dir(task_id) / "task.json").read_text(encoding="utf-8"))
    return str(meta.get("task_prompt") or meta.get("description") or meta.get("name") or "")


# ---------------------------------------------------------------------------
# (1) prompt contract: stable hashes, metadata in contract, clean train prompt
# ---------------------------------------------------------------------------


def test_contract_hashes_are_deterministic() -> None:
    text = "You are a careful quantum-computing coding assistant.\n"
    assert sha256_text(text) == sha256_text(text)
    assert sha256_text(text) != sha256_text(text + " ")
    payload = {
        "system_prompt_sha256": sha256_text(text),
        "tasks": [
            {"id": "a", "prompt_sha256": "x", "task_json_sha256": "y"},
            {"id": "b", "prompt_sha256": "u", "task_json_sha256": "v"},
        ],
    }
    assert aggregate_sha256(payload) == aggregate_sha256(dict(payload))
    # same content constructed twice -> identical digest (stable contract)
    assert aggregate_sha256(payload) == aggregate_sha256(
        {
            "system_prompt_sha256": sha256_text(text),
            "tasks": [
                {"id": "a", "prompt_sha256": "x", "task_json_sha256": "y"},
                {"id": "b", "prompt_sha256": "u", "task_json_sha256": "v"},
            ],
        }
    )


def test_public_eval_contract_includes_task_metadata() -> None:
    # The public eval contract digest must depend on task.json bytes: a
    # metadata change MUST change the contract hash (contamination of the
    # contract would otherwise be invisible).
    task_id = "quantum_rl_v2_shor_order_finding"
    task_dir = _task_dir(task_id)
    meta = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
    prompt_text = build_public_task_spec(task_dir, meta)
    base_records = [
        {
            "id": task_id,
            "prompt_sha256": sha256_text(prompt_text),
            "task_json_sha256": sha256_file(task_dir / "task.json"),
        }
    ]
    tampered_records = [
        {"id": task_id, "prompt_sha256": sha256_text(prompt_text), "task_json_sha256": "0" * 64}
    ]
    system_hash = sha256_text("system\n")
    base = aggregate_sha256({"system_prompt_sha256": system_hash, "tasks": base_records})
    tampered = aggregate_sha256({"system_prompt_sha256": system_hash, "tasks": tampered_records})
    assert base != tampered, "contract digest ignores task metadata"


def test_train_prompt_is_deterministic_and_carries_task_metadata() -> None:
    task = _load_task("quantum_rl_v2_shor_order_finding")
    p1 = build_prompt(task)
    p2 = build_prompt(task)
    assert p1 == p2, "build_prompt must be deterministic for the same task"
    assert "Task id" in p1
    assert "Domain: quantum" in p1
    assert "Category:" in p1
    assert "quantum_rl_v2_shor_order_finding" in p1
    assert "Return only the final Python code" in p1


@pytest.mark.parametrize(
    "task_id",
    _manifest_ids(V8_MANIFEST) + _manifest_ids(V9_MANIFEST),
)
def test_train_prompt_has_no_reference_or_tests_content(task_id: str) -> None:
    task = _load_task(task_id)
    prompt = build_prompt(task)
    tests_text = (task["task_dir"] / "tests.py").read_text(encoding="utf-8")
    # no checker internals may reach the train prompt
    assert "failures.append" not in prompt
    assert "def run_tests" not in prompt
    assert "# Test " not in prompt
    # no full tests.py body: any tests.py line that is a checker statement
    # must not appear verbatim in the prompt
    for line in tests_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("assert ", "failures.", "details.")):
            assert stripped not in prompt, f"tests.py line leaked into prompt: {stripped!r}"
    # interface summary must not include reference bodies (checked in (3) too)
    assert "return " not in "".join(task.get("required_interface") or []).lower()


# ---------------------------------------------------------------------------
# (2) holdout contamination: ids disjoint, v9 prompts textually distinct
# ---------------------------------------------------------------------------


def test_v7_v8_v9_ids_disjoint_from_frozen_holdout() -> None:
    holdout_ids = set(_manifest_ids(HOLDOUT_MANIFEST))
    assert len(holdout_ids) == 18
    for manifest in (V7_MANIFEST, V8_MANIFEST, V9_MANIFEST):
        ids = set(_manifest_ids(manifest))
        overlap = ids & holdout_ids
        assert not overlap, f"{manifest.name} overlaps the frozen holdout: {sorted(overlap)}"


def test_v9_prompts_have_no_near_duplicate_of_any_holdout_prompt() -> None:
    """Verbatim jsonl question texts must not be near-duplicates of holdout
    prompts (difflib ratio > 0.8 would flag contamination)."""
    holdout_prompts = {tid: _task_prompt_text(tid) for tid in _manifest_ids(HOLDOUT_MANIFEST)}
    assert all(holdout_prompts.values()), "every holdout task must have a prompt text"
    for v9_id in _manifest_ids(V9_MANIFEST):
        v9_prompt = _task_prompt_text(v9_id)
        assert v9_prompt, f"{v9_id} has no task_prompt"
        best = 0.0
        for holdout_id, holdout_prompt in holdout_prompts.items():
            ratio = difflib.SequenceMatcher(None, v9_prompt, holdout_prompt).ratio()
            best = max(best, ratio)
            assert ratio <= 0.8, f"near-duplicate: {v9_id} vs {holdout_id} ratio={ratio:.3f}"
        # informational tightness bound only when both texts are substantial
        # (short name-only holdout texts inflate difflib ratios)
        if len(v9_prompt) >= 40 and all(len(p) >= 40 for p in holdout_prompts.values()):
            assert best < 0.15, f"{v9_id} suspiciously similar to a holdout prompt: {best:.3f}"


def test_v9_manifest_regenerates_byte_identical() -> None:
    result = subprocess.run(
        [sys.executable, str(V9_BUILDER), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "OK" in result.stdout


def test_v9_manifest_contract_hash_matches_recomputation() -> None:
    from scripts.build_grpo_v9_manifest import render

    rendered = render()
    header = next(
        line for line in rendered.splitlines() if line.startswith("# task_contract_sha256=")
    )
    manifest_header = next(
        line
        for line in V9_MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.startswith("# task_contract_sha256=")
    )
    assert manifest_header == header


# ---------------------------------------------------------------------------
# (3) reference-code leakage: interface summaries are signatures only
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("task_id", _manifest_ids(V9_MANIFEST))
def test_train_interface_summary_is_signatures_only(task_id: str) -> None:
    task_dir = _task_dir(task_id)
    meta = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
    candidate_name = meta.get("candidate_file", "candidate.py")
    source = (task_dir / candidate_name).read_text(encoding="utf-8")
    lines = summarize_python_interface(source)
    assert lines, f"{task_id}: interface summary must not be empty"
    for line in lines:
        assert "return " not in line, f"body leaked into interface: {line!r}"
        assert not line.startswith(("import ", "from ")), f"import leaked: {line!r}"


@pytest.mark.parametrize("task_id", _manifest_ids(V9_MANIFEST))
def test_eval_public_api_is_signatures_and_docstrings_only(task_id: str) -> None:
    task_dir = _task_dir(task_id)
    meta = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
    candidate_name = meta.get("candidate_file", "candidate.py")
    source = (task_dir / candidate_name).read_text(encoding="utf-8")
    public = extract_public_api(source)
    spec = build_public_task_spec(task_dir, meta)
    # no executable statements from the reference may reach the eval prompt
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith(("return ", "import ", "from ", "print(")):
            assert stripped not in public, f"body leaked into public api: {stripped!r}"
            assert stripped not in spec, f"body leaked into eval prompt: {stripped!r}"


# ---------------------------------------------------------------------------
# (4) EVAL_HIDE_REFERENCE: question-only eval prompt in both flag states
# ---------------------------------------------------------------------------


def test_asi2_rubric_eval_prompt_is_question_only_in_both_flag_states() -> None:
    from scripts.run_asi2_base_adapter_rubric_eval import build_prompt

    task_dir = _task_dir("quantum_rl_v2_shor_order_finding")
    meta = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
    visible = build_prompt(task_dir, meta, hide_reference=False)
    hidden = build_prompt(task_dir, meta, hide_reference=True)
    assert visible == hidden, "reference visibility must not change the prompt"
    for prompt in (visible, hidden):
        assert "Existing/reference" not in prompt
        assert "failures.append" not in prompt
        assert "assert " not in prompt
        assert "def " not in prompt
        assert "Return only the final Python code" in prompt


def test_asi2_rubric_eval_prompt_never_embeds_reference_for_holdout_task() -> None:
    from scripts.run_asi2_base_adapter_rubric_eval import build_prompt

    holdout_id = "quantum_error_correction_shor_9qubit"
    task_dir = _task_dir(holdout_id)
    meta = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
    reference = (task_dir / meta.get("candidate_file", "candidate.py")).read_text(encoding="utf-8")
    body_marker = next(
        (
            line.strip()
            for line in reference.splitlines()
            if line.strip().startswith(("return ", "qc =", "circuit ="))
        ),
        None,
    )
    prompt = build_prompt(task_dir, meta, hide_reference=False)
    if body_marker:
        assert body_marker not in prompt
    assert "Existing/reference API shape" not in prompt
    assert reference[:100] not in prompt


def test_asi2_rubric_eval_gate_interface_still_accepted() -> None:
    # 3d68087 gate: --hide-reference remains an accepted interface, and the
    # no-leak behavior is now UNCONDITIONAL (working tree 2026-08-21 review
    # finding: question-only prompt; embedding is gone entirely).
    source = (ROOT / "scripts" / "run_asi2_base_adapter_rubric_eval.py").read_text(encoding="utf-8")
    assert "--hide-reference" in source  # gate interface survives (3d68087)
    assert "no-leak prompt is now unconditional" in source or "question-only" in source


# ---------------------------------------------------------------------------
# (5) behavior-hint hygiene: no decisive numeric answers in prompt hints
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("task_id", sorted(DECISIVE_HINT_MARKERS))
def test_prompt_visible_hints_do_not_leak_decisive_numerics(task_id: str) -> None:
    task = _load_task(task_id)
    hints = task_behavior_hints(task)
    for marker in DECISIVE_HINT_MARKERS[task_id]:
        assert not any(
            marker in hint for hint in hints
        ), f"{task_id} prompt hint leaks decisive numeric {marker!r}: {hints}"


@pytest.mark.parametrize("task_id", sorted(STRUCTURAL_HINT_MARKERS))
def test_prompt_visible_hints_keep_structural_guidance(task_id: str) -> None:
    task = _load_task(task_id)
    hints = task_behavior_hints(task)
    assert hints, f"{task_id} lost ALL hints (over-suppression)"
    for marker in STRUCTURAL_HINT_MARKERS[task_id]:
        assert any(
            marker in hint for hint in hints
        ), f"{task_id} lost structural hint {marker!r}: {hints}"


def test_raw_extractor_default_keeps_decisive_hints_for_backward_compat() -> None:
    # the RAW extractor contract (locked by the holdout-enrichment suite) is
    # unchanged: suppression is opt-in via suppress_decisive_numeric
    source = (
        'failures.append("factors_recovered=0, expected 2 (3 and 5)")\n'
        'failures.append("sampled_shots=100, expected 2048")\n'
    )
    raw = extract_behavior_hints_from_test_source(source, cap=6)
    assert any("(3 and 5)" in hint for hint in raw)
    suppressed = extract_behavior_hints_from_test_source(
        source, cap=6, suppress_decisive_numeric=True
    )
    assert not any("(3 and 5)" in hint for hint in suppressed)
    assert any(
        "expected 2048" in hint for hint in suppressed
    ), "structural shots hint must survive suppression"

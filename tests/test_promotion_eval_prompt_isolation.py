from __future__ import annotations

import json
from pathlib import Path

import pytest

from evals.runner.prepare_prompts import build_user_prompt, write_run_artifacts
from evals.runner.public_task_spec import build_public_task_spec, extract_public_api
from scripts.run_hf_pass1_eval import verify_prompt_contract

ROOT = Path(__file__).resolve().parents[1]
PROMOTION_MANIFEST = ROOT / "evals/benchmarks/sapo_promotion_holdout_v1_18.txt"
TRAINING_MANIFEST = ROOT / "evals/benchmarks/quantum_grpo_training_v4_targeted_disjoint.txt"

PUBLIC_CONTRACT_CASES = {
    "quantum_gate_alias_normalization": {
        "required": ("hadamard as H", "pauli_x as X", "cnot as CX", "Raise ValueError"),
        "forbidden": ("_ALIASES", "normalized.append"),
    },
    "quantum_superdense_coding": {
        "required": ("00 to I", "01 to X", "10 to Z", "11 to XZ", "exact inverse"),
        "forbidden": ("operations =", "inverse ="),
    },
    "quantum_binary_measurement_decoder": {
        "required": ("most-significant-bit-first", "2**len(bits)", "non-binary"),
        "forbidden": ("value = (value << 1)", "scale = 1 << len(bits)"),
    },
    "quantum_phase_register_roundtrip": {
        "required": ("most-significant-bit-first", "floor(phase * 2**n_qubits)", "0 <= phase < 1"),
        "forbidden": ("integer_rep =", "bits.append"),
    },
    "quantum_pennylane_vqe_h2": {
        "required": (
            "-0.4804 I(0)",
            "0.0910 Y(0)Y(1)",
            "deterministic seeded variational minimization",
        ),
        "forbidden": ("np.random.uniform", "opt.step_and_cost"),
    },
    "quantum_qiskit_qft_entangled": {
        "required": (
            "computational-basis statevector indexing",
            "forward n-qubit QFT without final swaps",
            "(1 + exp(2*pi*i*7*k/8))/4",
        ),
        "forbidden": ("c.compose", "Statevector.from_instruction"),
    },
    "quantum_pennylane_qml_iris_classification": {
        "required": ("L2-normalize", "sigmoid(K @ alpha) >= 0.5", "shape (20, 4)"),
        "forbidden": ("rng.normal", "alpha = np.zeros"),
    },
}


def _promotion_task_dirs() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for task_json in (ROOT / "evals/tasks").glob("*/*/task.json"):
        metadata = json.loads(task_json.read_text(encoding="utf-8"))
        result[str(metadata["id"])] = task_json.parent
    return result


def _manifest_ids(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def _task(tmp_path: Path) -> tuple[Path, dict]:
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    metadata = {
        "id": "quantum_hidden_sentinel",
        "name": "Hidden sentinel",
        "domain": "quantum",
        "category": "reasoning",
        "candidate_file": "candidate.py",
        "test_file": "tests.py",
    }
    (task_dir / "task.json").write_text(json.dumps(metadata), encoding="utf-8")
    (task_dir / "candidate.py").write_text(
        "def solve(value: int) -> int:\n"
        '    """Return the transformed value."""\n'
        "    REFERENCE_SOLUTION_SENTINEL = 9173\n"
        "    return value + REFERENCE_SOLUTION_SENTINEL\n",
        encoding="utf-8",
    )
    (task_dir / "tests.py").write_text(
        'HIDDEN_TEST_SENTINEL = "never-model-visible"\n', encoding="utf-8"
    )
    return task_dir, metadata


def test_public_api_keeps_signature_and_docstring_but_not_body() -> None:
    api = extract_public_api(
        "def solve(value: int) -> int:\n"
        '    """Return the transformed value."""\n'
        "    SECRET = 9173\n"
        "    return value + SECRET\n"
    )
    assert "def solve(value: int) -> int" in api
    assert "Return the transformed value." in api
    assert "SECRET" not in api
    assert "9173" not in api


def test_all_promotion_prompt_builders_hide_reference_and_tests(tmp_path: Path) -> None:
    task_dir, metadata = _task(tmp_path)
    prompts = [
        build_public_task_spec(task_dir, metadata),
        build_user_prompt(task_dir, metadata, prompt_style="direct"),
    ]
    for prompt in prompts:
        assert "def solve(value: int) -> int" in prompt
        assert "Return the transformed value." in prompt
        assert "REFERENCE_SOLUTION_SENTINEL" not in prompt
        assert "9173" not in prompt
        assert "HIDDEN_TEST_SENTINEL" not in prompt

    harness_source = (Path(__file__).resolve().parents[1] / "evals/subsystem/harness.py").read_text(
        encoding="utf-8"
    )
    assert "def build_task_prompt" in harness_source
    assert "return build_public_task_spec(task_dir, meta)" in harness_source
    assert (
        'read_text(encoding="utf-8")'
        not in harness_source.split("def build_task_prompt", 1)[1].split("def sanitize_code", 1)[0]
    )


@pytest.mark.parametrize("task_id", sorted(PUBLIC_CONTRACT_CASES))
def test_underspecified_promotion_tasks_have_public_semantics_without_bodies(
    task_id: str,
) -> None:
    task_dir = _promotion_task_dirs()[task_id]
    metadata = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
    prompt = build_public_task_spec(task_dir, metadata)
    case = PUBLIC_CONTRACT_CASES[task_id]

    for phrase in case["required"]:
        assert phrase in prompt
    for body_fragment in case["forbidden"]:
        assert body_fragment not in prompt
    assert "run_tests" not in prompt
    assert "failures.append" not in prompt


def test_prepared_run_freezes_and_checks_public_prompt_hashes(tmp_path: Path) -> None:
    task_dir, _ = _task(tmp_path)
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    write_run_artifacts(
        run_dir,
        prompt_style="direct",
        notes="hash test",
        task_files=[task_dir / "task.json"],
    )

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["public_eval_contract_sha256"]) == 64
    assert len(manifest["system_prompt_sha256"]) == 64
    assert len(manifest["tasks"][0]["prompt_sha256"]) == 64
    assert len(manifest["tasks"][0]["task_json_sha256"]) == 64
    assert verify_prompt_contract(run_dir, manifest) == manifest["public_eval_contract_sha256"]

    prompt_path = run_dir / manifest["tasks"][0]["prompt_file"]
    prompt_path.write_text(prompt_path.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="Frozen prompt hash mismatch"):
        verify_prompt_contract(run_dir, manifest)


def test_sapo_promotion_manifest_is_unique_complete_and_training_disjoint() -> None:
    promotion_ids = _manifest_ids(PROMOTION_MANIFEST)
    training_ids = set(_manifest_ids(TRAINING_MANIFEST))
    task_dirs = _promotion_task_dirs()

    assert len(promotion_ids) == 18
    assert len(set(promotion_ids)) == 18
    assert set(promotion_ids).isdisjoint(training_ids)
    assert set(promotion_ids) <= set(task_dirs)

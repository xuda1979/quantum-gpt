from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from evals.runner.prepare_prompts import write_run_artifacts
from evals.runner.run_eval import run_task
from scripts import run_hf_pass1_eval
from scripts.decide_sapo_promotion_gate import decide
from scripts.run_hf_pass1_eval import verify_prompt_contract

ROOT = Path(__file__).resolve().parents[1]
PROMOTION = ROOT / "evals/benchmarks/sapo_promotion_holdout_v1_18.txt"
TRAINING = ROOT / "evals/benchmarks/quantum_grpo_training_v6_runtime30_disjoint.txt"
TARGETED_TRAINING = ROOT / "evals/benchmarks/quantum_grpo_training_v4_targeted_disjoint.txt"
LAUNCHER = ROOT / "scripts/asi3_launch_grpo_direct.sh"


def _ids(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def _registry() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for task_json in (ROOT / "evals/tasks").glob("*/*/task.json"):
        metadata = json.loads(task_json.read_text(encoding="utf-8"))
        result[str(metadata["id"])] = task_json
    return result


def _launcher_default_training_manifest() -> Path:
    source = LAUNCHER.read_text(encoding="utf-8")
    match = re.search(r'BENCHMARK_FILE="\$\{ASI3_SAPO_BENCHMARK_FILE:-([^}]+)\}"', source)
    assert match is not None
    return ROOT / match.group(1)


def test_frozen_promotion_contract_rejects_scorer_mutation(tmp_path: Path) -> None:
    source = _registry()[_ids(PROMOTION)[0]]
    task_dir = tmp_path / "task"
    shutil.copytree(source.parent, task_dir)
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    write_run_artifacts(
        run_dir,
        prompt_style="direct",
        notes="scorer tamper regression",
        task_files=[task_dir / "task.json"],
    )
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))

    assert len(manifest["scorer_contract_sha256"]) == 64
    assert len(manifest["evaluation_runner_sha256"]) == 64
    assert verify_prompt_contract(run_dir, manifest) == manifest["public_eval_contract_sha256"]

    tests_path = task_dir / "tests.py"
    tests_path.write_text(
        tests_path.read_text(encoding="utf-8") + "\n# unauthorized scorer mutation\n",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit, match="Frozen scorer hash mismatch"):
        verify_prompt_contract(run_dir, manifest)


def test_runtime30_stdout_only_shortcut_is_rejected_by_every_semantic_scorer(
    tmp_path: Path,
) -> None:
    registry = _registry()
    semantic_ids = _ids(TRAINING)[10:]
    assert len(semantic_ids) == 30
    exploit = tmp_path / "solution.py"
    exploit.write_text("print({'000': 2000, '111': 2000})\n", encoding="utf-8")

    unexpected_passes = []
    for task_id in semantic_ids:
        result = run_task(registry[task_id], {task_id: exploit})
        if result["passed"]:
            unexpected_passes.append(task_id)
        else:
            assert any("source contract" in detail for detail in result["details"]), result
            assert result["error_type"] == "RewardIntegrityCircuitBreaker", result
            assert len(result["candidate_sha256"]) == 64, result
    assert unexpected_passes == []


def test_canonical_launcher_defaults_to_targeted10_not_semantic30() -> None:
    source = LAUNCHER.read_text(encoding="utf-8")
    default_manifest = _launcher_default_training_manifest()
    default_line = next(
        line for line in source.splitlines() if line.startswith("export BENCHMARK_FILE=")
    )
    assert "runtime30" not in default_line
    assert "runtime42" not in default_line
    # 2026-08-25 (test-update wave): the canonical launcher default is the v8
    # 20-task holdout-adjacent manifest (targeted10 + 10 adjacent tasks), not
    # the old v4/v7 targeted10.
    assert default_manifest.name in {
        "quantum_grpo_training_v4_targeted_disjoint.txt",
        "quantum_grpo_training_v7_targeted_integrity.txt",
        "quantum_grpo_training_v8_holdout_adjacent.txt",
    }
    # the v8 manifest contains the full targeted10 set (superset, not equal)
    assert set(_ids(TARGETED_TRAINING)) <= set(_ids(default_manifest))

    manifest_source = default_manifest.read_text(encoding="utf-8")
    assert "# required_import_roots=" in manifest_source
    assert "# reference_execution_verified=true " in manifest_source
    assert "# source=" in manifest_source and " sha256=" in manifest_source
    contract_line = next(
        line for line in manifest_source.splitlines() if line.startswith("# task_contract_sha256=")
    )
    expected_contract = contract_line.split("=", 1)[1]
    registry = _registry()
    digest = hashlib.sha256()
    for task_id in sorted(_ids(default_manifest)):
        task_dir = registry[task_id].parent
        for name in ("task.json", "tests.py"):
            digest.update(task_id.encode())
            digest.update(b"\0")
            digest.update(name.encode())
            digest.update(b"\0")
            digest.update((task_dir / name).read_bytes())
            digest.update(b"\0")
    assert digest.hexdigest() == expected_contract


def test_targeted10_is_complete_training_disjoint_and_reference_valid() -> None:
    registry = _registry()
    targeted_ids = _ids(_launcher_default_training_manifest())
    promotion_ids = set(_ids(PROMOTION))

    # 2026-08-25 (test-update wave): the v8 20-task manifest (targeted10 +
    # 10 holdout-adjacent) is the canonical default; it must stay disjoint
    # from the frozen 18-task holdout.
    assert len(targeted_ids) == len(set(targeted_ids)) == 20
    assert set(targeted_ids).isdisjoint(promotion_ids)
    failures = [
        result for task_id in targeted_ids if not (result := run_task(registry[task_id]))["passed"]
    ]
    assert failures == []


@pytest.mark.parametrize(
    "shortcut",
    [
        "print({'000': 2000, '111': 2000})\n",
        (
            "sentinel = object()\n"
            "print({'000': 2000, '111': 2000} if sentinel is not None else {})\n"
        ),
        "def solve(*args, **kwargs):\n    return 0\n",
    ],
    ids=("constant-stdout", "disguised-stdout", "generic-constant-function"),
)
def test_targeted10_rejects_generic_reward_shortcuts(tmp_path: Path, shortcut: str) -> None:
    candidate = tmp_path / "candidate.py"
    candidate.write_text(shortcut, encoding="utf-8")
    registry = _registry()

    unexpected_passes = [
        task_id
        for task_id in _ids(_launcher_default_training_manifest())
        if run_task(registry[task_id], {task_id: candidate})["passed"]
    ]
    assert unexpected_passes == []


def test_targeted10_rejects_hidden_scorer_frame_introspection(
    tmp_path: Path,
) -> None:
    """Candidate code must not be able to read hidden expected values in-process."""
    candidate = tmp_path / "candidate.py"
    candidate.write_text(
        "import inspect\n"
        "def _hidden_expected():\n"
        "    frame = inspect.currentframe().f_back\n"
        "    while frame is not None:\n"
        "        value = frame.f_locals.get('expected')\n"
        "        if isinstance(value, dict):\n"
        "            return value\n"
        "        frame = frame.f_back\n"
        "    return {}\n"
        "def encode_message(bits):\n"
        "    return _hidden_expected()[bits]\n"
        "def decode_message(opcode):\n"
        "    opcode = 'XZ' if opcode.lower() == 'zx' else opcode\n"
        "    reverse = {value: key for key, value in _hidden_expected().items()}\n"
        "    if opcode not in reverse:\n"
        "        raise ValueError(opcode)\n"
        "    return reverse[opcode]\n",
        encoding="utf-8",
    )
    task_json = ROOT / "evals/tasks/quantum/superdense_pauli_router/task.json"

    result = run_task(task_json, {"quantum_superdense_pauli_router": candidate})

    assert result["passed"] is False, result


@pytest.mark.parametrize(
    "shortcut_body",
    [
        "print({'000': 2000, '111': 2000} if samples is not None else {})",
        "print(samples and {'000': 2000, '111': 2000})",
        "print(dict([('000', 2000), ('111', 2000)]))",
        (
            "def fabricated_counts():\n"
            "    return {'000': 2000, '111': 2000}\n"
            "print(fabricated_counts())"
        ),
        "print(samples)\nprint({'000': 2000, '111': 2000})",
        ("counts = samples.histogram(key='m')\ncounts = {'000': 2000, '111': 2000}\nprint(counts)"),
        (
            "counts = samples.histogram(key='m')\n"
            "counts.clear()\n"
            "counts.update({'000': 2000, '111': 2000})\n"
            "print(counts)"
        ),
        (
            "sample_count = len(samples.measurements['m'])\n"
            "print({'000': 2000 + 0 * sample_count, "
            "'111': 2000 + 0 * sample_count})"
        ),
        "print(samples)\nprint('000: 2000')\nprint('111: 2000')",
        (
            "print(samples)\n"
            "fabricated = 2000\n"
            "print(f'000: {fabricated}')\n"
            "print(f'111: {fabricated}')"
        ),
        (
            "sample_count = len(samples.measurements['m'])\n"
            "fabricated = 2000 + sample_count - sample_count\n"
            "print({'000': fabricated, '111': fabricated})"
        ),
        (
            "print(samples)\n"
            "zero_key = '0' * 3\n"
            "one_key = '1' * 3\n"
            "print({zero_key: 2000, one_key: 2000})"
        ),
        (
            "def identity(value):\n"
            "    return value\n"
            "print(samples)\n"
            "print({'000': identity(2000), '111': identity(2000)})"
        ),
        ("print(samples)\nkeys = ['0' * 3, '1' * 3]\nprint(dict(zip(keys, [2000, 2000])))"),
    ],
    ids=(
        "conditional",
        "boolop",
        "dict-constructor",
        "helper-return",
        "derived-plus-static",
        "derived-then-overwrite",
        "derived-clear-update",
        "zeroed-dependency",
        "derived-plus-static-lines",
        "derived-plus-static-fstrings",
        "cancelled-derived-arithmetic",
        "computed-bitstring-keys",
        "constant-through-helper-argument",
        "computed-dict-constructor",
    ),
)
def test_active_semantic_scorer_rejects_disguised_hardcoded_stdout(
    tmp_path: Path, shortcut_body: str
) -> None:
    candidate = tmp_path / "solution.py"
    candidate.write_text(
        "import cirq\n"
        "qubits = cirq.LineQubit.range(3)\n"
        "circuit = cirq.Circuit(cirq.H(qubits[0]), cirq.measure(*qubits, key='m'))\n"
        "simulator = cirq.Simulator()\n"
        "samples = simulator.run(circuit, repetitions=1)\n"
        f"{shortcut_body}\n",
        encoding="utf-8",
    )
    task_json = ROOT / "evals/tasks/quantum_distill_sampling/qc-0421/task.json"

    result = run_task(task_json, {"qc-0421": candidate})

    assert result["passed"] is False, result
    assert any("source contract" in detail for detail in result["details"]), result


def test_candidate_map_scores_only_explicit_frozen_tasks(tmp_path: Path) -> None:
    task_json = _registry()[_ids(PROMOTION)[0]]
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    write_run_artifacts(
        run_dir,
        prompt_style="direct",
        notes="subset scoring regression",
        task_files=[task_json],
    )
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    task = manifest["tasks"][0]
    metadata = json.loads(task_json.read_text(encoding="utf-8"))
    shutil.copyfile(
        task_json.parent / metadata["candidate_file"],
        run_dir / task["candidate_file"],
    )

    completed = subprocess.run(
        [
            "python3",
            "evals/runner/run_eval.py",
            "--candidate-map",
            str(run_dir / "candidate-map.json"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    scorecard = json.loads((run_dir / "scorecard.json").read_text(encoding="utf-8"))
    assert [result["id"] for result in scorecard["results"]] == [task["id"]]
    assert scorecard["results"][0]["source"] == "override"
    assert len(scorecard["results"][0]["candidate_sha256"]) == 64


def test_promotion_eval_balanced_map_uses_every_visible_npu(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeNpu:
        @staticmethod
        def device_count() -> int:
            return 8

    class FakeTorch:
        npu = FakeNpu()

    monkeypatch.setattr(
        run_hf_pass1_eval,
        "_balanced_npu_device_map",
        lambda config, torch_module: {"model.layers.0": "npu:0"},
    )
    monkeypatch.setattr(
        run_hf_pass1_eval,
        "_filter_device_map",
        lambda mapping, model_loader, config: mapping,
    )
    kwargs = run_hf_pass1_eval.balanced_device_map_kwargs(
        config=object(),
        model_loader=object(),
        torch_module=FakeTorch(),
        device="npu",
        device_map="balanced-layers",
        npu_max_memory_gib=54,
    )

    assert kwargs["device_map"] == {"model.layers.0": "npu:0"}
    assert kwargs["max_memory"] == {f"npu:{index}": "54GiB" for index in range(8)}


def test_three_state_gate_requires_sapo_to_beat_base_and_hold_warm() -> None:
    contract = "a" * 64

    def run(name: str, passed: set[int]) -> dict:
        results = [
            {
                "id": f"task-{index:02d}",
                "passed": index in passed,
                "failure_category": None if index in passed else "assertion",
            }
            for index in range(18)
        ]
        return {
            "run_dir": name,
            "results": results,
            "scorecard": {
                "public_eval_contract_sha256": contract,
                "scorer_contract_sha256": contract,
                "evaluation_runner_sha256": contract,
            },
        }

    base = run("base", {0, 1, 2, 3})
    warm = run("warm", {0, 1, 2, 3, 4})
    sapo = run("sapo", {0, 1, 2, 3, 4, 5})
    payload = decide(base, warm, sapo)

    assert payload["decision"] == "continue"
    assert payload["metrics"]["sapo"]["strict_pass"] == 6
    assert payload["task_matrix"][5]["vs_base"] == "fixed"


def test_security_allows_legitimate_math_stack_attribute() -> None:
    """2026-09-01 (fork, v9 validation): the security gate banned ANY
    attribute named 'stack' — including the legitimate PennyLane API
    qml.math.stack (used by quantum_rl_v2_qml_jacobian_rx_ry's reference).
    That task's reference failed the gate, so a v9 launch would fail-closed
    on it. Real introspection vectors (inspect/traceback/sys) are already
    banned at the import-root level; the bare 'stack' attribute ban is
    over-broad and must not reject library APIs."""
    from evals.runner.candidate_security import candidate_security_violations

    legit = (
        "import pennylane as qml\n"
        "def jac():\n"
        "    return qml.math.stack([qml.expval(qml.PauliX(0)), qml.expval(qml.PauliZ(0))])\n"
    )
    assert candidate_security_violations(legit) == []

    # the introspection vector itself must STAY banned
    introspect = "import inspect\nstack = inspect.stack()\n"
    assert candidate_security_violations(introspect) != []

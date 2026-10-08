"""TDD gate for the SAPO RL v9 training manifest prompt fidelity.

2026-08-31 V9-CONTRACT VERIFIER lane (Pass 70). Locks the v9 first wave
(12 task dirs under evals/tasks/quantum/quantum_rl_v2_* wired by
evals/benchmarks/quantum_grpo_training_v9_rl_questions_v2.txt) to:

(a) every task_prompt is the VERBATIM (byte-identical) jsonl question text
    from quantum_rl_questions_v2.jsonl, matched to exactly one source line;
(b) no two v9 tasks share the same jsonl source line (injective wiring);
(c) the manifest header's jsonl source sha256 is the true file hash;
(d) the manifest regenerates deterministically and its
    task_contract_sha256 (sorted task.json + tests.py bytes) is valid.

The frozen holdout sapo_promotion_holdout_v1_18.txt is read-only here;
the v9 manifest itself and the task dirs are regenerable.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

ROOT = Path(__file__).resolve().parents[1]
V9_MANIFEST = ROOT / "evals/benchmarks/quantum_grpo_training_v9_rl_questions_v2.txt"
SOURCES_JSONL = ROOT / "quantum_rl_questions_v2.jsonl"
MANIFEST_BUILDER = ROOT / "scripts/build_grpo_v9_manifest.py"


# The manifest is the single source of truth for the task set (waves
# 1+2+3 = 44 tasks as of 2026-09-01, contract 594c015a...). V9_TASK_IDS is
# DERIVED from the manifest so the list cannot drift from it.
def _read_manifest_ids() -> list[str]:
    return [
        line.strip()
        for line in V9_MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


V9_TASK_IDS: list[str] = _read_manifest_ids()
_LEGACY_LIST: list[str] = [
    # wave 1
    "quantum_rl_v2_ry_cx_entropy",
    "quantum_rl_v2_w_state_entropy",
    "quantum_rl_v2_shor_order_finding",
    "quantum_rl_v2_trotter_suzuki_1qubit",
    "quantum_rl_v2_depolarizing_kraus",
    "quantum_rl_v2_depolarizing_bell_mixed",
    "quantum_rl_v2_vqe_penny_energy",
    "quantum_rl_v2_qaoa_p2_maxcut",
    "quantum_rl_v2_bell_chsh",
    "quantum_rl_v2_phase_encode_decode",
    "quantum_rl_v2_stim_cluster_tableau",
    "quantum_rl_v2_bitflip_code_ancilla",
    # wave 2
    "quantum_rl_v2_teleport_rz_ry",
    "quantum_rl_v2_grover_cirq_1000",
    "quantum_rl_v2_walk_cycle16_7step",
    "quantum_rl_v2_walk_cycle4_3step",
    "quantum_rl_v2_qml_classifier_x0x1",
    "quantum_rl_v2_readout_mitigation",
    "quantum_rl_v2_qpe_cirq_0125",
    "quantum_rl_v2_measure_helper_5q",
    "quantum_rl_v2_chsh_phiplus_estimator",
    "quantum_rl_v2_grover_qiskit_101",
    "quantum_rl_v2_amplitude_estimation",
    "quantum_rl_v2_qpe_qiskit_0375",
    # wave 3
    "quantum_rl_v2_ghz_mabk_witness",
    "quantum_rl_v2_ghz_mabk_4party",
    "quantum_rl_v2_zne_richardson_zz",
    "quantum_rl_v2_hubbard_jw_2x1",
    "quantum_rl_v2_hubbard_jw_3x1",
    "quantum_rl_v2_heisenberg_trotter_3q",
    "quantum_rl_v2_tfim_trotter_3q",
    "quantum_rl_v2_qft_matrix_5q",
    "quantum_rl_v2_qft_repair_2q",
    "quantum_rl_v2_stateprep_amplitudes",
    "quantum_rl_v2_stateprep_2q",
    "quantum_rl_v2_swap_test_ry",
]

JSONL_QUESTIONS: list[str] = [
    json.loads(line)["question"] for line in SOURCES_JSONL.read_text(encoding="utf-8").splitlines()
]


def _manifest_ids(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def _task_contract_hash(task_ids: list[str]) -> str:
    """Recompute the v8/v9 contract hash scheme from the file bytes."""
    task_dirs: dict[str, Path] = {}
    for task_json in (ROOT / "evals/tasks").glob("*/*/task.json"):
        meta = json.loads(task_json.read_text(encoding="utf-8"))
        task_dirs[str(meta.get("id", task_json.parent.name))] = task_json.parent
    digest = hashlib.sha256()
    for task_id in sorted(task_ids):
        task_dir = task_dirs.get(task_id)
        assert task_dir is not None, f"missing task dir for {task_id}"
        for name in ("task.json", "tests.py"):
            path = task_dir / name
            assert path.is_file(), f"missing artifact {path}"
            digest.update(task_id.encode())
            digest.update(b"\0")
            digest.update(name.encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
    return digest.hexdigest()


def test_v9_manifest_ids_are_the_expected_44() -> None:
    """The manifest is the single source of truth; V9_TASK_IDS derives from it
    (waves 1+2+3 = 44 tasks as of 2026-09-01, contract 594c015a...). The
    per-task parametrized checks below verify every manifest id's prompt is
    verbatim to its jsonl source."""
    assert len(V9_TASK_IDS) == 44
    assert _manifest_ids(V9_MANIFEST) == V9_TASK_IDS


@pytest.mark.parametrize("task_id", V9_TASK_IDS)
def test_every_v9_prompt_is_verbatim_jsonl_question(task_id: str) -> None:
    task_json = ROOT / "evals/tasks" / "quantum" / task_id / "task.json"
    meta = json.loads(task_json.read_text(encoding="utf-8"))
    prompt = meta["task_prompt"]
    matches = [i for i, q in enumerate(JSONL_QUESTIONS) if q == prompt]
    assert len(matches) == 1, (
        f"{task_id}: task_prompt not verbatim to exactly one jsonl question "
        f"(matches={matches}). Prompt head: {prompt[:100]!r}"
    )


def test_v9_prompt_sources_are_injective() -> None:
    used: list[int] = []
    for task_id in V9_TASK_IDS:
        meta = json.loads(
            (ROOT / "evals/tasks" / "quantum" / task_id / "task.json").read_text(encoding="utf-8")
        )
        prompt = meta["task_prompt"]
        used += [i for i, q in enumerate(JSONL_QUESTIONS) if q == prompt]
    assert len(used) == len(set(used)) == len(V9_TASK_IDS), f"shared/dup sources: {used}"


def test_v9_jsonl_source_hash_matches_header() -> None:
    source = V9_MANIFEST.read_text(encoding="utf-8")
    header = next(line for line in source.splitlines() if line.startswith("# source="))
    real_hash = hashlib.sha256(SOURCES_JSONL.read_bytes()).hexdigest()
    assert header == f"# source={SOURCES_JSONL.name} sha256={real_hash}", header


def test_v9_manifest_regenerates_with_valid_contract_hash(tmp_path: Path) -> None:
    out = tmp_path / "manifest.txt"
    subprocess.run(
        [sys.executable, str(MANIFEST_BUILDER), "--output", str(out)],
        check=True,
        capture_output=True,
        text=True,
    )
    rendered = out.read_text(encoding="utf-8")
    assert rendered == V9_MANIFEST.read_text(encoding="utf-8"), "manifest drifted"
    contract_line = next(
        line for line in rendered.splitlines() if line.startswith("# task_contract_sha256=")
    )
    expected = _task_contract_hash(_manifest_ids(out))
    assert contract_line.split("=", 1)[1] == expected


def test_v9_manifest_check_exits_zero() -> None:
    proc = subprocess.run(
        [sys.executable, str(MANIFEST_BUILDER), "--check"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    assert "OK" in proc.stdout

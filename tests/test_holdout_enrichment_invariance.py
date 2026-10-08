"""Holdout-scorer enrichment binary-invariance tests (SAPO loop, 2026-08-24).

Locks the enrichment contract for the working-tree scorer changes under
``evals/tasks/quantum/`` BEFORE they are deployed to the ASI2 scoring host:

  1. every reference solution still passes its task (18/18 frozen holdout
     references, plus every task dir whose files were touched);
  2. pass/fail verdicts are unchanged old-vs-new for representative failing
     candidates (the old version is ``git show HEAD:<path>`` of the same
     scorer, run against the SAME candidates — the harness protocol
     ``tests.run_tests(candidate_path) -> {"passed", "details"}``);
  3. numeric failure details are emitted — the 2026-08-24 enriched scorers
     must produce details the fine scorer (scripts/fine_score.py / the
     shaped-reward parser) can parse into a non-zero grade for near-miss
     failures.

Run this BEFORE committing/deploying the enrichment (after the changes are
committed, the old-vs-new comparison degenerates to a no-op identity check —
that is expected and harmless).

Adversarial candidates are derived deterministically from each task's
reference candidate: a None-stub (every function returns None — the cached
base-leg failure mode), a missing-function variant (last function deleted),
a crash variant (first function raises), and a constant-perturbation
near-miss (+1 on the first returned numeric literal, when one exists).
"""
# ruff: noqa: UP038  # (X | Y) isinstance is py3.10-only; py3.9 .venv gate (precedent: training/grpo_trainer.py)

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "evals" / "tasks" / "quantum"
BENCHMARK = ROOT / "evals" / "benchmarks" / "sapo_promotion_holdout_v1_18.txt"
FINE_SCORE = ROOT / "scripts" / "fine_score.py"

# ---------------------------------------------------------------------------
# Task inventories (dir names under evals/tasks/quantum/)
# ---------------------------------------------------------------------------

HOLDOUT_TASKS = [
    "gate_alias_normalization",
    "phase_estimation_circuit",
    "qaoa_maxcut",
    "superdense_coding",
    "grover_oracle_diffusion",
    "density_matrix_partial_trace",
    "quantum_error_correction_shor_9qubit",
    "trotterized_hamiltonian_evolution",
    "quantum_channel_depolarizing",
    "ghz_state_witness",
    "pennylane_vqe_h2",
    "cirq_qaoa_line",
    "braket_bell_state",
    "qiskit_qft_entangled",
    "qiskit_stabilizer_5qubit_code",
    "pennylane_qml_iris_classification",
    "phase_register_roundtrip",
    "binary_measurement_decoder",
]

# Task dirs with working-tree changes (git diff evals/tasks/quantum/) at the
# time the enrichment was verified (2026-08-24).  Kept in sync with git by
# test_modified_inventory_matches_git_diff.
MODIFIED_TASKS = [
    "bell_pair_construction",
    "binary_measurement_decoder",
    "bitstring_maxcut_landscape",
    "braket_bell_state",
    "circuit_phase_repair",
    "density_matrix_partial_trace",
    "error_detection_bit_flip",
    "gate_alias_casefold_barrier",
    "gate_alias_normalization",
    "gate_alias_registry_cleanup",
    "gate_token_canonicalizer",
    "ghz_state_witness",
    "grover_oracle_diffusion",
    "maxcut_assignment_enumerator",
    "maxcut_partition_ranker",
    "measurement_bug_repair",
    "pauli_message_codec",
    "pennylane_qml_iris_classification",
    "pennylane_vqe_h2",
    "phase_estimation_circuit",
    "phase_measurement_register",
    "phase_register_roundtrip",
    "qaoa_maxcut",
    "qft_phase_pattern",
    "qiskit_qft_entangled",
    "qiskit_stabilizer_5qubit_code",
    "quantum_channel_depolarizing",
    "quantum_error_correction_shor_9qubit",
    "stabilizer_tableau_update_repair",
    "superdense_coding",
    "superdense_identity_lookup",
    "superdense_pauli_router",
    "teleportation_corrections",
    "vqe_energy_minimization",
]

# Scorers whose 2026-08-24 enrichment appends numeric closeness summaries for
# the shaped/fine parser (verified in reports/sapo-harness-enrichment-2026-08-24.md).
ENRICHED_NUMERIC_TASKS = [
    "bitstring_maxcut_landscape",
    "measurement_bug_repair",
    "superdense_pauli_router",
    "stabilizer_tableau_update_repair",
]

# The 2026-08-24 enrichment verifier reverted these 3 scorers to HEAD because
# the enrichment batch's version-shim changes FLIPPED verdicts.  They were
# then repaired by the dep-matrix lane's version-fragility fixes (depmatrix
# §2 rows 1-2; fix shas 76a0106a / 5fe817cf / 8982efe7, deployed and
# sha-verified on the box 2026-08-26 per .sapo-loop/depmatrix.md §3) and
# COMMITTED as ec46ad0 (2026-08-31) — VERDICT-INVARIANT repairs that
# un-poison the task's OWN reference (the old exact-bound checks failed
# correct references under pennylane 0.38+ `.terms` callables and qiskit 2.x
# amplitude conventions).  FROZEN_SCORER_PINS locks each to the deployed
# bytes so any future unverified scorer edit trips the deploy gate
# (test_repaired_scorers_locked_to_deployed_bytes); the old HEAD-identity
# lock is superseded because HEAD now CONTAINS the repairs.
FROZEN_SCORER_PINS = {
    "pennylane_qml_iris_classification": "8982efe7a2fdcde6fa723d77db797137a741508ebda8d2f4cc0610ebc25c4829",
    "pennylane_vqe_h2": "76a0106a456cea4652535dfe4ba9dadeac6825cae4ba3196e50e3a88ab4305b9",
    "qiskit_qft_entangled": "68623b0f10b54b330c0c140532732c7fc381ec4c2050b5d7207c5da42c201376",
}
REVERTED_TESTS_PENDING_BOX_REPAIR = []

# Targeted near-miss function BODIES for the enriched-4: a failing candidate
# that is structurally valid and mostly right, so the scorer's numeric
# closeness lines (not a crash) carry the signal.  Each entry replaces the
# named function's body inside the reference candidate source.
NEAR_MISS_BODIES = {
    # landscape sorted ascending instead of descending (only that check fails)
    "bitstring_maxcut_landscape": (
        "qaoa_cost_landscape",
        "    from itertools import product\n"
        "    landscape = []\n"
        "    for bits in product('01', repeat=n_nodes):\n"
        "        bitstring = ''.join(bits)\n"
        "        landscape.append((bitstring, maxcut_cost(bitstring, edges)))\n"
        "    landscape.sort(key=lambda item: (item[1], item[0]))\n"
        "    return landscape\n",
    ),
    # one wrong conjugation rule (H X -> X instead of Z): axis mostly right
    "stabilizer_tableau_update_repair": (
        "apply_gate_sequence",
        "    rules = {\n"
        "        'H': {'I': (1, 'I'), 'X': (1, 'X'), 'Y': (-1, 'Y'), 'Z': (1, 'X')},\n"
        "        'S': {'I': (1, 'I'), 'X': (1, 'Y'), 'Y': (-1, 'X'), 'Z': (1, 'Z')},\n"
        "        'SDG': {'I': (1, 'I'), 'X': (-1, 'Y'), 'Y': (1, 'X'), 'Z': (1, 'Z')},\n"
        "    }\n"
        "    raw = pauli.strip()\n"
        "    sign = -1 if raw.startswith('-') else 1\n"
        "    label = raw[1:] if raw.startswith('-') else raw\n"
        "    label = label.strip().upper()\n"
        "    if label not in {'I', 'X', 'Y', 'Z'}:\n"
        "        raise ValueError(f'unsupported Pauli operator: {pauli!r}')\n"
        "    for gate in gates:\n"
        "        gate_name = gate.strip().upper()\n"
        "        if gate_name not in rules:\n"
        "            raise ValueError(f'unsupported gate: {gate!r}')\n"
        "        gate_sign, label = rules[gate_name][label]\n"
        "        sign *= gate_sign\n"
        "    return sign, label\n",
    ),
}

MODIFIED_SET = set(MODIFIED_TASKS)
HOLDOUT_SET = set(HOLDOUT_TASKS)


def _git_diff_quantum_dirs() -> set[str]:
    out = subprocess.check_output(
        ["git", "-C", str(ROOT), "diff", "--name-only", "evals/tasks/quantum/"],
        text=True,
    )
    return {Path(line).parent.name for line in out.splitlines() if line.strip()}


def _git_show_head(path: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "show", f"HEAD:{path}"], text=True)


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    assert spec is not None and spec.loader is not None, f"cannot load {path}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _score(task_id: str, tests_module, candidate_path: Path) -> tuple[bool, list[str]]:
    """Harness-protocol scoring; a crash scores as a failure (like the runner)."""
    try:
        result = tests_module.run_tests(str(candidate_path))
    except Exception as exc:  # noqa: BLE001 - harness-equivalent crash handling
        return False, [f"{type(exc).__name__}: {exc}"]
    if not isinstance(result, dict):
        return False, [f"Unexpected harness return type: {type(result).__name__}"]
    return bool(result.get("passed")), list(result.get("details") or [])


def _near_miss_candidate(task_id: str, tmp_path: Path) -> Path | None:
    """Reference source with one function body replaced (targeted near-miss)."""
    if task_id not in NEAR_MISS_BODIES:
        return None
    fn_name, body_src = NEAR_MISS_BODIES[task_id]
    src = (TASKS / task_id / "candidate.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    replacement = ast.parse(f"def {fn_name}(*args, **kwargs):\n{body_src}").body[0]
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == fn_name:
            node.body = replacement.body
            break
    else:
        return None
    path = tmp_path / f"{task_id}_near_miss.py"
    path.write_text(ast.unparse(tree), encoding="utf-8")
    return path


def _adversarial_variants(task_id: str, tmp_path: Path) -> list[tuple[str, Path]]:
    """Deterministic failing candidates derived from the reference source."""
    src = (TASKS / task_id / "candidate.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    funcs = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    if not funcs:
        return []
    variants: list[tuple[str, str]] = []

    # None-stub: every return becomes None (cached base-leg failure mode).
    stub_tree = ast.parse(src)
    for node in ast.walk(stub_tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Return) and stmt.value is not None:
                    stmt.value = ast.Constant(value=None)
    variants.append(("none_stub", ast.unparse(stub_tree)))

    # Missing-function: delete the last top-level function.
    missing_tree = ast.parse(src)
    missing_funcs = [
        n for n in missing_tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    if missing_funcs:
        missing_tree.body.remove(missing_funcs[-1])
        variants.append(("missing_fn", ast.unparse(missing_tree)))

    # Crash: first function raises on call.
    crash_tree = ast.parse(src)
    crash_first = [
        n for n in crash_tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ][0]
    crash_first.body = [
        ast.Raise(
            exc=ast.Call(
                func=ast.Name(id="RuntimeError", ctx=ast.Load()),
                args=[ast.Constant("adversarial crash")],
                keywords=[],
            )
        )
    ]
    variants.append(("crash", ast.unparse(crash_tree)))

    # Near-miss: +1 on the first numeric literal in the first returned
    # expression (only when such a literal exists).
    perturb_tree = ast.parse(src)
    patched = False
    for node in ast.walk(perturb_tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Return) and stmt.value is not None:
                    for lit in ast.walk(stmt.value):
                        if (
                            isinstance(lit, ast.Constant)
                            and isinstance(lit.value, (int, float))
                            and not isinstance(lit.value, bool)
                        ):
                            lit.value = lit.value + 1
                            patched = True
                            break
                    if patched:
                        break
            if patched:
                break
    if patched:
        variants.append(("const_perturb", ast.unparse(perturb_tree)))

    written: list[tuple[str, Path]] = []
    for name, source in variants:
        path = tmp_path / f"{task_id}_{name}.py"
        path.write_text(source, encoding="utf-8")
        written.append((name, path))
    near_miss = _near_miss_candidate(task_id, tmp_path)
    if near_miss is not None:
        written.append(("near_miss", near_miss))
    return written


def _fine_grade(passed: bool, details: list[str]) -> float:
    """Grade the fine scorer assigns to a candidate's details."""
    sys.path.insert(0, str(ROOT))
    from training.grpo_utils import shaped_reward_from_details  # noqa: PLC0415

    return shaped_reward_from_details(bool(passed), list(details or []))


# ---------------------------------------------------------------------------
# 1. Reference solutions still pass
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "task_id", [t for t in HOLDOUT_TASKS if t not in REVERTED_TESTS_PENDING_BOX_REPAIR]
)
def test_holdout_reference_passes(task_id: str):
    """Frozen-holdout references pass (18/18 under the current deployed scorers;
    the 3 previously-reverted scorers now carry the box-verified dep-matrix
    fixes and are pinned by FROZEN_SCORER_PINS)."""
    module = _load_module(TASKS / task_id / "tests.py", f"tests_{task_id}")
    passed, details = _score(task_id, module, TASKS / task_id / "candidate.py")
    assert passed is True, f"{task_id} reference failed: {details}"


@pytest.mark.parametrize(
    "task_id", [t for t in MODIFIED_TASKS if t not in REVERTED_TESTS_PENDING_BOX_REPAIR]
)
def test_modified_scorer_reference_passes(task_id: str):
    """Every task with working-tree scorer changes keeps a passing reference."""
    module = _load_module(TASKS / task_id / "tests.py", f"tests_{task_id}")
    passed, details = _score(task_id, module, TASKS / task_id / "candidate.py")
    assert passed is True, f"{task_id} reference failed: {details}"


@pytest.mark.parametrize("task_id", sorted(FROZEN_SCORER_PINS))
def test_repaired_scorers_locked_to_deployed_bytes(task_id: str):
    """The 3 box-repaired scorers are frozen at their deployed bytes.

    Replaces the old byte-identity-to-HEAD lock (the HEAD baseline is the
    pre-repair poisoned scorer).  Any future unverified edit to these files
    must trip this gate and be re-verified on the box with TDD.
    """
    current = hashlib.sha256((TASKS / task_id / "tests.py").read_bytes()).hexdigest()
    assert current == FROZEN_SCORER_PINS[task_id], (
        f"{task_id}/tests.py no longer matches the deployed bytes "
        f"({current} != {FROZEN_SCORER_PINS[task_id]}) — unverified scorer "
        "mutation; re-verify on the box before updating the pin"
    )


def test_modified_inventory_matches_git_diff():
    """The locked task inventory must cover exactly the git-modified dirs."""
    assert _git_diff_quantum_dirs() == MODIFIED_SET


# ---------------------------------------------------------------------------
# 2. Pass/fail verdicts unchanged old-vs-new (binary invariance)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("task_id", MODIFIED_TASKS)
def test_adversarial_verdicts_binary_invariant(task_id: str, tmp_path: Path):
    """Same failing candidates, same verdict with the HEAD scorer version.

    (After ec46ad0 the 3 repaired scorers are byte-identical to HEAD, so their
    old-vs-new comparison is an identity check — expected and harmless.)
    """
    tests_new = _load_module(TASKS / task_id / "tests.py", f"tests_new_{task_id}")
    head_src = _git_show_head(f"evals/tasks/quantum/{task_id}/tests.py")
    head_path = tmp_path / f"tests_head_{task_id}.py"
    head_path.write_text(head_src, encoding="utf-8")
    tests_old = _load_module(head_path, f"tests_old_{task_id}")

    variants = _adversarial_variants(task_id, tmp_path)
    assert variants, f"{task_id}: no adversarial candidates derivable"
    verdicts: list[tuple[str, bool, bool]] = []
    for name, candidate in variants:
        passed_new, _ = _score(task_id, tests_new, candidate)
        passed_old, _ = _score(task_id, tests_old, candidate)
        verdicts.append((name, passed_new, passed_old))
        assert passed_new == passed_old, (
            f"{task_id}/{name}: verdict changed old={passed_old} new={passed_new} — "
            f"binary-invariance violated"
        )
    # The variant set must be genuinely adversarial: at least one candidate
    # fails under BOTH scorer versions (else the equality check is vacuous).
    assert any(
        (not new and not old) for _name, new, old in verdicts
    ), f"{task_id}: no adversarial variant actually fails — variant set vacuous"


# ---------------------------------------------------------------------------
# 3. Numeric failure details emitted (fine scorer parses them)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("task_id", ENRICHED_NUMERIC_TASKS)
def test_enriched_scorer_emits_numeric_details(task_id: str, tmp_path: Path):
    """The 2026-08-24 enriched scorers emit numbers the fine scorer can parse.

    At least one failing candidate class must carry numeric closeness evidence
    (fine grade > 0.0), not just a binary verdict.
    """
    module = _load_module(TASKS / task_id / "tests.py", f"tests_em_{task_id}")
    grades = []
    for _name, candidate in _adversarial_variants(task_id, tmp_path):
        passed, details = _score(task_id, module, candidate)
        if not passed:
            grades.append(_fine_grade(passed, details))
    assert grades, f"{task_id}: no failing candidate produced by variants"
    assert max(grades) > 0.0, (
        f"{task_id}: no failing candidate emitted parseable numerics "
        f"(grades all 0.0) — enrichment lost its signal"
    )


def test_fine_score_cli_parses_enriched_details(tmp_path: Path):
    """End-to-end: scripts/fine_score.py grades a scorecard built from the
    enriched scorers' failing details with a non-zero fine mean."""
    results: list[dict] = []
    for task_id in ENRICHED_NUMERIC_TASKS:
        module = _load_module(TASKS / task_id / "tests.py", f"tests_cli_{task_id}")
        details = []
        for _name, candidate in _adversarial_variants(task_id, tmp_path):
            passed, cand_details = _score(task_id, module, candidate)
            if not passed and cand_details:
                details = cand_details
                break
        results.append({"id": f"quantum_{task_id}", "passed": False, "details": details})

    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "scorecard.json").write_text(
        json.dumps({"schema_version": "eval-scorecard-v2", "results": results}, indent=2),
        encoding="utf-8",
    )
    proc = subprocess.run(
        [sys.executable, str(FINE_SCORE), str(run_dir)],
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, f"fine_score.py failed: {proc.stderr}"
    assert (
        "fine_mean=0.0000" not in proc.stdout
    ), f"fine_score.py graded the enriched failures at 0.0:\n{proc.stdout}"

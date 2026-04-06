#!/usr/bin/env python3
"""Build a tiny dataset-v0 seed corpus from existing eval tasks."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASKS_ROOT = ROOT / "evals" / "tasks"
OUTPUT_DIR = ROOT / "data" / "seed"
OUTPUT_PATH = OUTPUT_DIR / "train.jsonl"

TASK_SPECS = [
    {
        "task_dir": TASKS_ROOT / "quantum" / "bell_pair_construction",
        "example_id": "quantum_bell_pair_001",
        "task_type": "implementation",
        "source": "eval_derived",
        "difficulty": "easy",
        "framework": None,
        "tags": ["bell-pair", "state-preparation", "amplitudes"],
        "instruction": "Write a Python file that returns the Bell state |Phi+> amplitudes as a length-4 list and satisfies the supplied tests.",
        "artifacts": ["tests", "reference_style"],
        "metadata": {},
    },
    {
        "task_dir": TASKS_ROOT / "quantum" / "measurement_bug_repair",
        "example_id": "quantum_measurement_repair_001",
        "task_type": "repair",
        "source": "eval_derived",
        "difficulty": "easy",
        "framework": None,
        "tags": ["repair", "measurement", "bit-ordering"],
        "instruction": "Repair the Python file so two-bit measurement strings map correctly from q1q0 input ordering into a {'q0': ..., 'q1': ...} dictionary.",
        "artifacts": ["broken_candidate", "tests"],
        "artifact_overrides": {
            "broken_candidate": "def measurement_mapping(bitstring: str) -> dict[str, int]:\n    \"\"\"Map q0/q1 to integer measurement results from a two-bit string.\n\n    Input ordering is q1q0, so the rightmost bit is q0.\n    \"\"\"\n    if len(bitstring) != 2 or any(ch not in \"01\" for ch in bitstring):\n        raise ValueError(\"expected a two-bit measurement string\")\n    return {\"q0\": int(bitstring[0]), \"q1\": int(bitstring[1])}\n"
        },
        "metadata": {"preferred_prompt_style": "repair_focused"},
    },
    {
        "task_dir": TASKS_ROOT / "quantum" / "superdense_coding",
        "example_id": "quantum_superdense_coding_001",
        "task_type": "implementation",
        "source": "eval_derived",
        "difficulty": "easy",
        "framework": None,
        "tags": ["superdense-coding", "encoding", "decoding"],
        "instruction": "Write a Python file with encode_message(bits) and decode_message(operation) implementing the standard two-bit superdense coding mapping.",
        "artifacts": ["tests", "reference_style"],
        "metadata": {},
    },
    {
        "task_dir": TASKS_ROOT / "quantum" / "stabilizer_tableau_update_repair",
        "example_id": "quantum_stabilizer_tableau_repair_001",
        "task_type": "repair",
        "source": "eval_derived",
        "difficulty": "medium",
        "framework": None,
        "tags": ["repair", "stabilizer", "clifford", "sign-tracking"],
        "instruction": "Repair the Python file so apply_gate_sequence(pauli, gates) correctly tracks signed single-qubit Pauli updates under H, S, and SDG conjugation, rejecting unsupported operators and gates.",
        "artifacts": ["broken_candidate", "tests"],
        "artifact_overrides": {
            "broken_candidate": "def _normalize_pauli(label: str) -> str:\n    normalized = label.strip().upper()\n    if normalized not in {\"I\", \"X\", \"Y\", \"Z\"}:\n        raise ValueError(f\"unsupported Pauli operator: {label!r}\")\n    return normalized\n\n\ndef apply_gate_sequence(pauli: str, gates: list[str]) -> tuple[int, str]:\n    raw = pauli.strip()\n    sign = -1 if raw.startswith(\"-\") else 1\n    label = raw[1:] if raw.startswith(\"-\") else raw\n    label = _normalize_pauli(label)\n\n    for gate in gates:\n        gate_name = gate.strip().upper()\n        if gate_name == \"H\":\n            if label == \"X\":\n                label = \"Z\"\n            elif label == \"Z\":\n                label = \"X\"\n        elif gate_name == \"S\":\n            if label == \"X\":\n                label = \"Y\"\n            elif label == \"Y\":\n                label = \"X\"\n        elif gate_name == \"SDG\":\n            if label == \"X\":\n                label = \"Y\"\n            elif label == \"Y\":\n                label = \"X\"\n        else:\n            raise ValueError(f\"unsupported gate: {gate!r}\")\n\n    return sign, label\n"
        },
        "metadata": {"preferred_prompt_style": "repair_focused"},
    },
    {
        "task_dir": TASKS_ROOT / "software" / "off_by_one_bugfix",
        "example_id": "software_bugfix_off_by_one_001",
        "task_type": "repair",
        "source": "eval_derived",
        "difficulty": "easy",
        "framework": None,
        "tags": ["bugfix", "ranges", "boundary-conditions"],
        "instruction": "Repair the function so inclusive_range_sum(start, end) includes the end value and still returns 0 when end < start.",
        "artifacts": ["broken_candidate", "tests"],
        "artifact_overrides": {
            "broken_candidate": "def inclusive_range_sum(start: int, end: int) -> int:\n    if end < start:\n        return 0\n    return sum(range(start, end))\n"
        },
        "metadata": {"preferred_prompt_style": "repair_focused"},
    },
    {
        "task_dir": TASKS_ROOT / "software" / "patch_application_conflict_resolver",
        "example_id": "software_patch_conflict_resolver_001",
        "task_type": "repair",
        "source": "eval_derived",
        "difficulty": "medium",
        "framework": None,
        "tags": ["repair", "patches", "stateful-logic", "conflicts", "versioning"],
        "instruction": "Repair the Python file so apply_patches(base_state, patches) applies ordered updates with duplicate patch suppression, conflict reporting, version monotonicity, and input immutability.",
        "artifacts": ["broken_candidate", "tests"],
        "artifact_overrides": {
            "broken_candidate": "def apply_patches(base_state: dict[str, dict], patches: list[dict]) -> dict:\n    state = base_state\n    applied_patch_ids = []\n    conflicts = []\n\n    for patch in patches:\n        key = patch[\"key\"]\n        if key not in state:\n            state[key] = {\"value\": patch[\"value\"], \"version\": patch[\"new_version\"]}\n            applied_patch_ids.append(patch[\"patch_id\"])\n            continue\n\n        actual_version = state[key][\"version\"]\n        if patch[\"new_version\"] <= actual_version:\n            conflicts.append({\"patch_id\": patch[\"patch_id\"], \"key\": key, \"reason\": \"version_mismatch\"})\n            continue\n\n        state[key] = {\"value\": patch[\"value\"], \"version\": patch[\"new_version\"]}\n        applied_patch_ids.append(patch[\"patch_id\"])\n\n    return {\"state\": state, \"applied_patch_ids\": applied_patch_ids, \"conflicts\": conflicts}\n"
        },
        "metadata": {"preferred_prompt_style": "repair_focused"},
    },
    {
        "task_dir": TASKS_ROOT / "software" / "parser_regression_tests",
        "example_id": "software_parser_tests_001",
        "task_type": "test_writing",
        "source": "eval_derived",
        "difficulty": "easy",
        "framework": None,
        "tags": ["tests", "parser", "regression"],
        "instruction": "Write a Python file containing parse_assignment(line) plus regression_cases() that covers whitespace trimming, embedded equals, and empty-key rejection.",
        "artifacts": ["implementation_context"],
        "metadata": {},
    },
    {
        "task_dir": TASKS_ROOT / "software" / "duplicate_logic_refactor",
        "example_id": "software_refactor_duplicate_logic_001",
        "task_type": "refactor",
        "source": "eval_derived",
        "difficulty": "easy",
        "framework": None,
        "tags": ["refactor", "duplication", "maintainability"],
        "instruction": "Refactor the module to use a shared normalization helper while preserving the behavior of build_user_record and build_audit_record.",
        "artifacts": ["original_file", "tests"],
        "artifact_overrides": {
            "original_file": "def build_user_record(name: str, email: str) -> dict[str, str]:\n    username = name.strip().lower().replace(\" \", \"_\")\n    return {\n        \"name\": name.strip(),\n        \"email\": email.strip().lower(),\n        \"username\": username,\n    }\n\n\ndef build_audit_record(name: str, action: str) -> dict[str, str]:\n    username = name.strip().lower().replace(\" \", \"_\")\n    return {\n        \"actor\": username,\n        \"action\": action.strip().lower(),\n    }\n"
        },
        "metadata": {},
    },
    # --- New tasks wired in 2026-03-19 ---
    {
        "task_dir": TASKS_ROOT / "quantum" / "circuit_phase_repair",
        "example_id": "quantum_circuit_phase_repair_001",
        "task_type": "implementation",
        "source": "eval_derived",
        "difficulty": "medium",
        "framework": None,
        "tags": ["phase-cancellation", "gate-normalization", "circuit-optimization"],
        "instruction": "Write a Python function repair_phase_sequence(ops) that normalizes a one-qubit gate stream (H, X, Z, S, SDG), cancels adjacent inverse/self-inverse pairs, and raises ValueError on unsupported gates.",
        "artifacts": ["reference_style", "tests"],
        "metadata": {},
    },
    {
        "task_dir": TASKS_ROOT / "quantum" / "gate_alias_normalization",
        "example_id": "quantum_gate_alias_normalization_001",
        "task_type": "implementation",
        "source": "eval_derived",
        "difficulty": "easy",
        "framework": None,
        "tags": ["gate-aliases", "normalization", "api"],
        "instruction": "Write a Python function normalize_gate_sequence(gates) that maps common gate aliases (h, hadamard, x, pauli_x, cx, cnot) to canonical names (H, X, CX), raising ValueError for unknown gates.",
        "artifacts": ["reference_style", "tests"],
        "metadata": {},
    },
    {
        "task_dir": TASKS_ROOT / "quantum" / "qft_phase_pattern",
        "example_id": "quantum_qft_phase_pattern_001",
        "task_type": "implementation",
        "source": "eval_derived",
        "difficulty": "medium",
        "framework": None,
        "tags": ["qft", "phase", "statevector", "algorithm-reasoning"],
        "instruction": "Write a Python function qft_basis_state(n_qubits, basis_index) that returns the exact QFT statevector for a computational basis state, using the standard phase formula.",
        "artifacts": ["reference_style", "tests"],
        "metadata": {},
    },
    {
        "task_dir": TASKS_ROOT / "quantum" / "teleportation_corrections",
        "example_id": "quantum_teleportation_corrections_001",
        "task_type": "implementation",
        "source": "eval_derived",
        "difficulty": "easy",
        "framework": None,
        "tags": ["teleportation", "pauli-corrections", "protocol"],
        "instruction": "Write a Python function teleportation_corrections(m0, m1) that returns the ordered list of Pauli corrections (X and/or Z) for quantum teleportation given two measurement bits.",
        "artifacts": ["reference_style", "tests"],
        "metadata": {},
    },
    {
        "task_dir": TASKS_ROOT / "software" / "config_merge",
        "example_id": "software_config_merge_001",
        "task_type": "implementation",
        "source": "eval_derived",
        "difficulty": "easy",
        "framework": None,
        "tags": ["config", "merge", "recursion", "immutability"],
        "instruction": "Write a Python function merge_config(defaults, overrides) that recursively merges override dicts into defaults without mutating inputs. Non-dict values replace entirely.",
        "artifacts": ["reference_style", "tests"],
        "metadata": {},
    },
    {
        "task_dir": TASKS_ROOT / "software" / "docstring_contract",
        "example_id": "software_docstring_contract_001",
        "task_type": "implementation",
        "source": "eval_derived",
        "difficulty": "easy",
        "framework": None,
        "tags": ["normalization", "identifiers", "string-processing"],
        "instruction": "Write a Python function normalize_identifier(raw) that converts a human label to lowercase snake_case, stripping non-ASCII and collapsing whitespace/hyphens into underscores.",
        "artifacts": ["reference_style", "tests"],
        "metadata": {},
    },
    {
        "task_dir": TASKS_ROOT / "software" / "multifile_patch_conflict_repair",
        "example_id": "software_multifile_patch_conflict_repair_001",
        "task_type": "implementation",
        "source": "eval_derived",
        "difficulty": "medium",
        "framework": None,
        "tags": ["patches", "conflicts", "versioning", "dataclasses"],
        "instruction": "Write apply_patch_plan, apply_patches, and render_conflict_report functions implementing ordered patch application with duplicate suppression, version checks, missing-key detection, and conflict reporting.",
        "artifacts": ["reference_style", "tests"],
        "metadata": {},
    },
    {
        "task_dir": TASKS_ROOT / "software" / "session_event_log",
        "example_id": "software_session_event_log_001",
        "task_type": "implementation",
        "source": "eval_derived",
        "difficulty": "medium",
        "framework": None,
        "tags": ["state-machine", "events", "sessions", "stateful-logic"],
        "instruction": "Write a Python function apply_events(events) that processes start/message/end session events into an active/history state machine, raising ValueError on invalid transitions.",
        "artifacts": ["reference_style", "tests"],
        "metadata": {},
    },
    {
        "task_dir": TASKS_ROOT / "software" / "session_window_summary",
        "example_id": "software_session_window_summary_001",
        "task_type": "implementation",
        "source": "eval_derived",
        "difficulty": "medium",
        "framework": None,
        "tags": ["sessions", "windowing", "summary", "stateful-logic"],
        "instruction": "Write a Python function summarize_sessions(events, active_window=...) that tracks open/message/close events and returns active sessions within a time window, closed sessions, message counts, and a timeline.",
        "artifacts": ["reference_style", "tests"],
        "metadata": {},
    },
    # --- New tasks wired in 2026-03-19 (evening batch) ---
    {
        "task_dir": TASKS_ROOT / "quantum" / "phase_estimation_circuit",
        "example_id": "quantum_phase_estimation_001",
        "task_type": "implementation",
        "source": "eval_derived",
        "difficulty": "medium",
        "framework": None,
        "tags": ["phase-estimation", "eigenvalue", "qpe", "algorithm-implementation"],
        "instruction": "Write Python functions phase_estimation(eigenvalue_phase, n_counting_bits) and phase_from_measurement(measurement, n_counting_bits) that simulate ideal quantum phase estimation: mapping a phase to the integer QPE measurement outcome and recovering the phase from a measurement.",
        "artifacts": ["reference_style", "tests"],
        "metadata": {},
    },
    {
        "task_dir": TASKS_ROOT / "quantum" / "vqe_energy_minimization",
        "example_id": "quantum_vqe_energy_001",
        "task_type": "implementation",
        "source": "eval_derived",
        "difficulty": "medium",
        "framework": None,
        "tags": ["vqe", "variational", "energy", "ansatz", "hamiltonian"],
        "instruction": "Write Python functions ry_state(theta), energy_expectation(theta, h_coeffs), and find_min_energy(h_coeffs) implementing a single-qubit VQE: RY ansatz statevector, energy expectation for H = c_I*I + c_Z*Z + c_X*X, and brute-force minimization over theta.",
        "artifacts": ["reference_style", "tests"],
        "metadata": {},
    },
    {
        "task_dir": TASKS_ROOT / "quantum" / "qaoa_maxcut",
        "example_id": "quantum_qaoa_maxcut_001",
        "task_type": "implementation",
        "source": "eval_derived",
        "difficulty": "medium",
        "framework": None,
        "tags": ["qaoa", "maxcut", "combinatorial-optimization", "cost-function"],
        "instruction": "Write Python functions maxcut_cost(bitstring, edges), brute_force_maxcut(n_nodes, edges), and qaoa_cost_landscape(n_nodes, edges) implementing MaxCut cost evaluation, exhaustive optimal search, and a sorted cost landscape for QAOA analysis.",
        "artifacts": ["reference_style", "tests"],
        "metadata": {},
    },
    {
        "task_dir": TASKS_ROOT / "quantum" / "circuit_depth_optimization",
        "example_id": "quantum_circuit_depth_opt_001",
        "task_type": "implementation",
        "source": "eval_derived",
        "difficulty": "medium",
        "framework": None,
        "tags": ["circuit-optimization", "scheduling", "depth", "asap"],
        "instruction": "Write Python functions optimize_circuit(gates) and circuit_depth(gates) that schedule quantum gates into minimum-depth layers using greedy ASAP scheduling, where gates on disjoint qubits can run in parallel.",
        "artifacts": ["reference_style", "tests"],
        "metadata": {},
    },
    {
        "task_dir": TASKS_ROOT / "software" / "retry_decorator",
        "example_id": "software_retry_decorator_001",
        "task_type": "implementation",
        "source": "eval_derived",
        "difficulty": "medium",
        "framework": None,
        "tags": ["decorator", "retry", "backoff", "resilience", "design-pattern"],
        "instruction": "Write a Python decorator retry(max_attempts, base_delay, backoff_factor, exceptions) that retries a function on specified exceptions with exponential backoff, preserving the wrapped function's name and docstring via functools.wraps.",
        "artifacts": ["reference_style", "tests"],
        "metadata": {},
    },
    {
        "task_dir": TASKS_ROOT / "software" / "tree_serialization",
        "example_id": "software_tree_serialization_001",
        "task_type": "implementation",
        "source": "eval_derived",
        "difficulty": "medium",
        "framework": None,
        "tags": ["tree", "serialization", "json", "recursion", "data-structures"],
        "instruction": "Write a TreeNode class and Python functions serialize(root), deserialize(data), and tree_depth(root) implementing JSON-based n-ary tree serialization/deserialization with depth computation.",
        "artifacts": ["reference_style", "tests"],
        "metadata": {},
    },
]


REQUIRED_COMMON_FIELDS = [
    "schema_version",
    "example_id",
    "domain",
    "category",
    "task_type",
    "source",
    "difficulty",
    "language",
    "framework",
    "tags",
    "instruction",
    "response",
    "artifacts",
    "metadata",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_task_metadata(task_dir: Path) -> dict:
    return json.loads(read_text(task_dir / "task.json"))


def resolve_tests_path(task_dir: Path, meta: dict) -> Path:
    tests_path = task_dir / meta.get("test_file", "tests.py")
    if not tests_path.exists():
        task_id = meta.get("id", task_dir.name)
        raise FileNotFoundError(f"Missing test file for task {task_id}: {tests_path}")
    return tests_path


def build_artifacts(spec: dict, candidate_text: str, tests_text: str) -> dict:
    artifact_names = spec["artifacts"]
    overrides = spec.get("artifact_overrides", {})
    artifacts = {}
    for name in artifact_names:
        if name in overrides:
            artifacts[name] = overrides[name]
        elif name == "tests":
            artifacts[name] = tests_text
        elif name in {"reference_style", "broken_candidate", "original_file", "implementation_context"}:
            artifacts[name] = candidate_text
        else:
            raise ValueError(f"Unknown artifact name: {name}")
    return artifacts


def build_example(spec: dict) -> dict:
    task_dir = spec["task_dir"]
    meta = load_task_metadata(task_dir)
    candidate_text = read_text(task_dir / meta["candidate_file"])
    tests_text = read_text(resolve_tests_path(task_dir, meta))

    example = {
        "schema_version": "dataset-v0",
        "example_id": spec["example_id"],
        "domain": meta["domain"],
        "category": meta["category"],
        "task_type": spec["task_type"],
        "source": spec["source"],
        "difficulty": spec["difficulty"],
        "language": "python",
        "framework": spec["framework"],
        "tags": spec["tags"],
        "instruction": spec["instruction"],
        "response": candidate_text,
        "artifacts": build_artifacts(spec, candidate_text, tests_text),
        "metadata": {
            "task_id": meta["id"],
            "task_name": meta["name"],
            **spec["metadata"],
        },
    }
    validate_examples([example])
    return example


def validate_examples(examples: list[dict]) -> None:
    seen_ids = set()
    for example in examples:
        missing = [field for field in REQUIRED_COMMON_FIELDS if field not in example]
        if missing:
            raise ValueError(f"Missing required fields for {example.get('example_id')}: {missing}")
        if example["schema_version"] != "dataset-v0":
            raise ValueError(f"Unexpected schema version for {example['example_id']}: {example['schema_version']}")
        if example["domain"] not in {"quantum", "software"}:
            raise ValueError(f"Unexpected domain for {example['example_id']}: {example['domain']}")
        if not isinstance(example["instruction"], str) or not example["instruction"].strip():
            raise ValueError(f"Instruction must be a non-empty string for {example['example_id']}")
        if not isinstance(example["response"], str) or not example["response"].strip():
            raise ValueError(f"Response must be a non-empty string for {example['example_id']}")
        if not isinstance(example["artifacts"], dict):
            raise ValueError(f"Artifacts must be an object for {example['example_id']}")
        if example["example_id"] in seen_ids:
            raise ValueError(f"Duplicate example_id detected: {example['example_id']}")
        seen_ids.add(example["example_id"])


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    examples = [build_example(spec) for spec in TASK_SPECS]
    validate_examples(examples)
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        for example in examples:
            handle.write(json.dumps(example, ensure_ascii=False) + "\n")
    print(f"Wrote {len(examples)} examples to {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

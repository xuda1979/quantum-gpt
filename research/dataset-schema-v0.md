# Dataset Schema v0

## Purpose

Define a minimal, inspectable JSONL schema for the first training-data and eval-adjacent artifacts in this workspace.

The schema is designed for the current phase:

- CPU-first local iteration
- small manually curated examples
- compatibility with the existing eval harness
- support for both quantum and software-engineering tasks
- easy later conversion into chat/instruction tuning formats

This is not a final training spec. It is the smallest practical schema that keeps examples structured enough for filtering, slicing, and later transformation.

## Design Principles

- **One example per JSON object.** Easy to diff, grep, append, and validate locally.
- **Task-first metadata.** Domain, category, and source provenance should be explicit.
- **Support multiple supervision modes.** The project needs implementation tasks, repair tasks, and test-writing tasks.
- **Store executable artifacts by reference or inline text.** Small examples may be stored inline; larger ones can later move to file-backed packaging.
- **Keep prompt/answer separation clean.** This helps convert examples into different model-provider formats later.
- **Favor boring fields over clever abstraction.** The goal is operational clarity, not schema maximalism.

## File Convention

Recommended initial layout:

```text
data/
  seed/
    train.jsonl
    val.jsonl
    test.jsonl
```

Each line is a single JSON object following one of the schemas below.

## Common Fields

These fields appear in every example type.

```json
{
  "schema_version": "dataset-v0",
  "example_id": "software_bugfix_off_by_one_001",
  "domain": "software",
  "category": "bugfix",
  "task_type": "implementation",
  "source": "synthetic",
  "difficulty": "easy",
  "language": "python",
  "framework": null,
  "tags": ["bugfix", "lists", "boundary-conditions"],
  "instruction": "Fix the off-by-one bug in the function.",
  "response": "def ...",
  "artifacts": {},
  "metadata": {}
}
```

### Field meanings

- `schema_version`: fixed string for this first schema version
- `example_id`: stable unique identifier
- `domain`: `quantum` or `software`
- `category`: task family such as `bugfix`, `test_writing`, `refactor`, `circuit_construction`, `debug_repair`, `reasoning`
- `task_type`: one of `implementation`, `repair`, `test_writing`, `refactor`, `explanation`
- `source`: where the item came from, e.g. `synthetic`, `curated`, `eval_derived`, `human`
- `difficulty`: coarse label such as `easy`, `medium`, `hard`
- `language`: usually `python` for now
- `framework`: e.g. `qiskit`, `cirq`, `pennylane`, or `null`
- `tags`: lightweight freeform retrieval/filter labels
- `instruction`: the user-visible task statement
- `response`: the gold target output for supervised learning
- `artifacts`: structured auxiliary payloads like starter code, tests, or context files
- `metadata`: freeform but non-essential bookkeeping

## Example Type 1: Single-file implementation

Use for tasks where the model should produce a full candidate file from a task description and tests.

```json
{
  "schema_version": "dataset-v0",
  "example_id": "quantum_bell_pair_001",
  "domain": "quantum",
  "category": "circuit_construction",
  "task_type": "implementation",
  "source": "eval_derived",
  "difficulty": "easy",
  "language": "python",
  "framework": "qiskit",
  "tags": ["bell-pair", "circuits", "state-preparation"],
  "instruction": "Write a Python file that constructs a Bell pair circuit and satisfies the supplied tests.",
  "response": "def build_bell_pair():\n    ...\n",
  "artifacts": {
    "tests": "def run_tests(candidate_path: str) -> dict:\n    ...\n",
    "reference_style": "def build_bell_pair():\n    ...\n"
  },
  "metadata": {
    "task_id": "quantum_bell_pair_construction"
  }
}
```

## Example Type 2: Repair task

Use when the model is given broken code and asked for a corrected replacement.

```json
{
  "schema_version": "dataset-v0",
  "example_id": "quantum_measurement_repair_001",
  "domain": "quantum",
  "category": "debug_repair",
  "task_type": "repair",
  "source": "eval_derived",
  "difficulty": "easy",
  "language": "python",
  "framework": "qiskit",
  "tags": ["repair", "measurement", "qubit-ordering"],
  "instruction": "Repair the candidate file so the measurement mapping matches the expected classical bit ordering.",
  "response": "from qiskit import QuantumCircuit\n...",
  "artifacts": {
    "broken_candidate": "from qiskit import QuantumCircuit\n...",
    "tests": "def run_tests(candidate_path: str) -> dict:\n    ...\n"
  },
  "metadata": {
    "task_id": "quantum_measurement_bug_repair",
    "preferred_prompt_style": "repair_focused"
  }
}
```

## Example Type 3: Test-writing task

Use when the target output is a test file rather than implementation code.

```json
{
  "schema_version": "dataset-v0",
  "example_id": "software_parser_tests_001",
  "domain": "software",
  "category": "test_writing",
  "task_type": "test_writing",
  "source": "eval_derived",
  "difficulty": "easy",
  "language": "python",
  "framework": null,
  "tags": ["tests", "parser", "regression"],
  "instruction": "Write regression tests for the parser bug described below.",
  "response": "def test_parser_handles_trailing_separator():\n    ...\n",
  "artifacts": {
    "implementation_context": "def parse_record(text: str) -> dict:\n    ...\n",
    "bug_report": "Trailing separators currently produce an empty field instead of being ignored."
  },
  "metadata": {
    "task_id": "software_parser_regression_tests"
  }
}
```

## Example Type 4: Refactor/edit task

Use when the target is a cleaned-up full file and behavior preservation matters.

```json
{
  "schema_version": "dataset-v0",
  "example_id": "software_refactor_duplicate_logic_001",
  "domain": "software",
  "category": "refactor",
  "task_type": "refactor",
  "source": "eval_derived",
  "difficulty": "easy",
  "language": "python",
  "framework": null,
  "tags": ["refactor", "duplication", "maintainability"],
  "instruction": "Refactor the module to remove duplicated logic while preserving behavior.",
  "response": "def _normalize(...):\n    ...\n",
  "artifacts": {
    "original_file": "def transform_a(...):\n    ...\n",
    "tests": "def run_tests(candidate_path: str) -> dict:\n    ...\n"
  },
  "metadata": {
    "task_id": "software_duplicate_logic_refactor"
  }
}
```

## Mapping from current eval tasks

The current six seed eval tasks already map cleanly into this schema:

- `quantum_bell_pair_construction` → `implementation`
- `quantum_measurement_bug_repair` → `repair`
- `quantum_superdense_coding` → `implementation`
- `software_off_by_one_bugfix` → `repair`
- `software_parser_regression_tests` → `test_writing`
- `software_duplicate_logic_refactor` → `refactor`

That is a good sign: the schema matches real artifacts already present in the repo instead of being purely speculative.

## Minimal validation rules

A local validator for `dataset-v0` should enforce:

1. required common fields exist
2. `schema_version == "dataset-v0"`
3. `domain` is one of `quantum` or `software`
4. `instruction` and `response` are non-empty strings
5. `artifacts` is a JSON object
6. `example_id` values are unique within a file

Nice-to-have validation later:

- category whitelist checks
- task-type/category consistency checks
- artifact-specific field requirements
- approximate token/character length checks
- split leakage checks between train/val/test

## Why this schema is enough for now

It supports the immediate next layer of work without dragging in premature complexity:

- manual curation of a seed corpus
- extraction of training items from eval-style tasks
- filtering by domain/category/framework
- conversion into chat-format instruction tuning records
- later generation of train/val/test manifests

The obvious next step after this note is not more schema design. It is to create a tiny seed JSONL file derived from the existing six eval tasks and then build a validator/converter around that real data.

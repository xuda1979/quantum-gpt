# Eval Spec v0

## Purpose

Define the first compact, CPU-feasible evaluation slice for the quantum coding LLM project. This spec is intentionally small enough to implement quickly, but broad enough to measure both target capabilities:

1. quantum algorithm and framework competence
2. general software-engineering competence

The goal is not benchmark prestige. The goal is to produce a local eval harness that can distinguish:

- weak prompting from better prompting
- general coding skill from domain-specific quantum skill
- superficial code generation from executable, maintainable solutions

## Evaluation Design Principles

- **Executable first.** Prefer tasks with tests, numerical checks, or structural validation.
- **CPU-only by default.** Keep dependencies and runtime small enough for routine local execution.
- **Short-context tasks first.** Avoid repository-wide or long-context evaluation in v0.
- **Balanced capability mix.** Quantum and software-engineering tasks both count.
- **Simple scoring.** Binary pass/fail plus a few lightweight secondary metrics.
- **Prompt-stable.** The same task should support repeated baseline comparisons across prompt styles.

## Initial Task Mix

Target: **24 tasks total**

- **12 quantum tasks**
- **12 software-engineering tasks**

This is large enough to avoid pure anecdote, but small enough to curate manually in the current phase.

## Quantum Task Categories

Create three categories with four tasks each.

### 1. Circuit Construction

Focus: can the model write correct small circuits from textual requirements?

Example task types:

- build a Bell pair circuit
- implement quantum teleportation skeleton logic
- prepare a GHZ state for 3 qubits
- implement a simple QFT circuit for a small number of qubits

Scoring:

- circuit builds successfully
- expected operations or output state checks pass
- no unnecessary complexity for a tiny task

### 2. Quantum Debug / Repair

Focus: can the model fix broken small examples?

Example task types:

- repair an incorrect Qiskit measurement mapping
- fix a teleportation example with misplaced classical control
- repair an invalid import or outdated API usage
- correct a wrong qubit ordering bug in a simple circuit test

Scoring:

- failing tests become passing
- fix is minimal and preserves task intent
- no new errors introduced

### 3. Quantum Reasoning with Code

Focus: can the model connect algorithm intent to implementation?

Example task types:

- write a small oracle for a 2-qubit Grover toy problem
- implement superdense coding encode/decode steps
- produce a simple phase-kickback demonstration
- complete a VQE toy helper or cost-function scaffold

Scoring:

- executable correctness
- alignment with the intended protocol or algorithm
- testable outputs for tiny simulators

## Software-Engineering Task Categories

Create three categories with four tasks each.

### 1. Bug Fixing

Focus: minimal targeted repairs in ordinary Python code.

Example task types:

- repair an off-by-one error
- fix a broken parser helper
- correct a mistaken data-class default behavior
- patch a function that mishandles edge cases

Scoring:

- tests pass
- fix is small and relevant
- no obvious regressions

### 2. Test Writing

Focus: can the model add useful tests rather than only implementation code?

Example task types:

- add tests for a utility with missing edge-case coverage
- write regression tests for a reported bug
- extend an existing pytest file for boundary conditions
- add tests that verify a refactor preserves behavior

Scoring:

- tests are valid and runnable
- tests meaningfully cover intended behavior
- tests are not vacuous or redundant

### 3. Small Refactors / API Cleanup

Focus: maintainability-oriented edits.

Example task types:

- extract duplicate logic into a helper
- simplify a function interface while preserving tests
- improve naming and docstrings in a tiny module
- replace brittle branching with a clearer structure

Scoring:

- existing tests still pass
- structure improves without overengineering
- change remains local and readable

## Framework and Dependency Scope

### Quantum Frameworks

For v0, prioritize:

1. **Qiskit first**
2. optional second slice later for **Cirq or PennyLane**, but not required in the first implementation

Reasoning:

- Qiskit has broad ecosystem familiarity and many small educational examples
- one framework is enough to stand up the harness quickly
- multi-framework coverage can be added after the first harness is stable

### General Python Stack

- Python
- pytest
- standard library wherever possible
- avoid heavy scientific dependencies unless truly needed

## Prompt Protocol

Each task should support three prompt modes:

1. **direct_solve**
2. **plan_then_code**
3. **repair_mode** where applicable

Store prompts as templates so the same eval set can compare response strategies consistently.

## Scoring Model

### Primary Score

Per task:

- **pass = 1**
- **fail = 0**

Aggregate:

- overall pass rate
- quantum pass rate
- software-engineering pass rate
- pass rate by category

### Secondary Diagnostics

Track lightweight metadata for later analysis:

- syntax/runtime failure
- test failure
- wrong API usage
- partial completion
- excessive or irrelevant edits

These should not complicate the main scoring path; they are diagnostic tags.

## File Layout Proposal

```text
research/
  eval-spec-v0.md

evals/
  tasks/
    quantum/
      circuit_construction/
      debug_repair/
      reasoning/
    software/
      bugfix/
      test_writing/
      refactor/
  prompts/
    direct_solve.txt
    plan_then_code.txt
    repair_mode.txt
  runner/
    README.md
    run_eval.py
```

## Acceptance Criteria for v0 Harness

The first implementation is good enough if it can:

1. load a small local task set
2. run reference tests for each task
3. evaluate model outputs with consistent prompt templates
4. emit per-task pass/fail results plus a summary table
5. finish on local CPU in a practical amount of time for a small batch

## Recommended Next Build Order

1. create the directory skeleton under `evals/`
2. implement **6 seed tasks** first, not all 24
   - 3 quantum
   - 3 software-engineering
3. build the minimal runner around those seed tasks
4. verify summary reporting and task reproducibility
5. expand to the full 24-task v0 set only after the runner works

## Seed Task Recommendation

Suggested first six tasks:

### Quantum seed tasks

- Bell pair circuit construction
- Qiskit measurement bug repair
- superdense coding encode/decode completion

### Software seed tasks

- off-by-one bug fix
- regression test writing for a parser bug
- tiny duplicate-logic refactor

## Open Questions

- Should the runner expect unified diff patches, full-file rewrites, or freeform code blocks?
- Should task packaging mimic repository-edit workflows immediately, or begin with simpler single-file tasks?
- What latency budget per task is acceptable for routine local comparisons on this machine?
- When local inference is flaky or unavailable, should the same harness support hosted baseline runs for prompt comparison while preserving local test execution?

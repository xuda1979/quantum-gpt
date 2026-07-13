# Track N3 — Import-Path Discipline DPO (IP-DPO)

**Owner:** subagent track (loop 2026-07-13, iteration 15:25)
**Status:** design + scaffold
**Target students:** Qwen3.6-27B (ASI1), Qwen3.6-35B-A3B (ASI2/3)
**Constraint:** post-training only; no architecture change.

## Problem (from 2026-07-11 iter-2 gap report §3 item 1)

The dominant failure mode across verified evals is `ImportError` from wrong
module paths. Examples observed:

- `from qiskit.algorithms import MinimumEigenOptimizer` (moved to
  `qiskit_algorithms` in modern Qiskit)
- `from qiskit import QuantumCircuit` used as `circuit` without the import
  being executed in the roll-out
- `from braket.devices import LocalSimulator` vs `from braket.tasks`
  confusion

Per `evals/subsystem/recommendations/qaoa-glm52-base-recs.json`, at least
3 of the 8 recommended tasks have `failure_category: import_error`.

## Approach

Build a DPO pair set where:

- **chosen side** = a correct, import-grounded `def main()` program that
  passes the task's `tests.py`.
- **rejected side** = a program with the **same algorithmic structure** but
  an `ImportError`-inducing import line (wrong module path / missing import /
  deprecated path).

The rejected side is *constructed to fail* on the import axis only. This
makes the DPO signal corruption-proof: the model cannot learn to prefer the
rejected side because the rejected side literally cannot run.

## Data source

- Tasks: the 58-task `evals/tasks/quantum/` directory, filtered to those
  whose `candidate.py` imports a quantum SDK.
- chosen = `candidate.py` content, reformatted into the canonical assistant
  chat-template form.
- rejected = chosen with exactly one import line mutated to a known-bad
  path (drawn from `configs/dpo/import_path_mutations_v1.json`).

## Success metric

On the 56-task QAOA scorecard, an IP-DPO-LoRA adapter (on base) must show
**zero `ImportError`-class failures** (currently ≥3), with no regression on
the 49 currently passing tasks.

## Out of scope

- Any NPU run. This track produces code + config + tests only.
- Modifying the LoRA trainer or the DPO loss.
- Generating new GLM5.2 teacher corrections.

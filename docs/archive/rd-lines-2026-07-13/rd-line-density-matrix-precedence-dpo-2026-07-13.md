# Track N7 — DensityMatrix Operator-Precedence DPO (DM-DPO)

**Owner:** subagent track (loop 2026-07-13, iteration 15:25)
**Status:** design + scaffold
**Target students:** Qwen3.6-27B (ASI1), Qwen3.6-35B-A3B (ASI2/3)
**Constraint:** post-training only; no architecture change.

## Problem (from 2026-07-11 iter-2 gap report §3 item 4)

`TypeError` on `DensityMatrix @` — deepseek-v4-pro fails
`quantum_partial_trace_bipartite` due to operator-precedence / type
confusion when composing density-matrix operators. The model writes
`rho @ sigma @ P` where `@` binds incorrectly or where one operand is a
`Statevector` not a `DensityMatrix`, producing a `TypeError`.

## Approach

Build a DPO pair set on the density-matrix / partial-trace family:

- **chosen** = correct program using explicit `DensityMatrix(...)` wrappers,
  parenthesized `@` chains, and `partial_trace()` calls that pass
  `tests.py`.
- **rejected** = the same program with the `DensityMatrix()` wrapper removed
  on one operand, or with parentheses dropped from the `@` chain —
  constructed to raise `TypeError`.

The rejected side is *constructed to fail* on the type-precedence axis.

## Data source

- Seed tasks: `density_matrix_partial_trace`,
  `quantum_partial_trace_bipartite` (if present in the 58-task set).
- Variants: 2-qubit and 3-qubit bipartite splits, with the subsystem-trace
  axis parameterized.

## Success metric

On the density-matrix family tasks, a DM-DPO-LoRA adapter (on base) must
show **zero `TypeError`-class failures** (currently ≥1), with no regression
on the 49 passing tasks.

## Out of scope

- Any NPU run.
- Modifying the DPO loss or trainer.
- Non-density-matrix tasks.

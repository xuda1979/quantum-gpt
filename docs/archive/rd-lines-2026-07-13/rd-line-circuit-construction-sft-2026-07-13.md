# Track N5 — Circuit-Construction Discipline SFT (CC-SFT)

**Owner:** subagent track (loop 2026-07-13, iteration 15:25)
**Status:** design + scaffold
**Target students:** Qwen3.6-27B (ASI1), Qwen3.6-35B-A3B (ASI2/3)
**Constraint:** post-training only; no architecture change.

## Problem (from 2026-07-11 iter-2 gap report §4e)

`NameError: circuit` and `SyntaxError` on the Deutsch-Jozsa and
Bernstein-Vazirani tasks. The model writes a function that references a
`circuit` symbol without ever constructing it, or emits a fragment that is
not a valid Python program. Per the gap report §4e, the fix is
"3-5 examples of complete `def main()` programs with explicit circuit
construction and measurement."

## Approach

Build an SFT set focused narrowly on the circuit-construction + measurement
pattern. Each row is a complete program that:

1. Constructs a `QuantumCircuit` (or framework-equivalent) explicitly.
2. Applies the task's required gates.
3. Measures.
4. Prints the deterministic result from `def main()`.

The set is drawn from the Deutsch-Jozsa, Bernstein-Vazirani, and
Bell-pair tasks (the 3 named in §4e), plus synthetic variants (different
hidden strings, different oracle sizes) to reach the recommended 3-5x
multiplicity per task.

## Data source

- Seed tasks: `deutsch_jozsa_balance_test`, `bernstein_vazirani_hidden_string`,
  `bell_pair_construction` from `evals/tasks/quantum/`.
- Variants: parameterized by `n` (qubit count) and hidden-string value,
  generated programmatically and verified by the task's `tests.py`.

## Success metric

On the 3 named tasks (plus their parameterized variants in a held-out
split), a CC-SFT-LoRA adapter (on base) must pass **all variant tests**
with zero `NameError` / `SyntaxError` failures.

## Out of scope

- Any NPU run.
- Tasks outside the circuit-construction family.
- Modifying the SFT trainer.

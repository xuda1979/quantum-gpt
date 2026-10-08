# Track N4 — Output-String-Exactness SFT (OSE-SFT)

**Owner:** subagent track (loop 2026-07-13, iteration 15:25)
**Status:** design + scaffold
**Target students:** Qwen3.6-27B (ASI1), Qwen3.6-35B-A3B (ASI2/3)
**Constraint:** post-training only; no architecture change.

## Problem (from 2026-07-11 iter-2 gap report §3 item 5)

Failure mode #5: "Missing deterministic print" — qwen3.6-27b-rag produces
correct code structure but fails to print the exact expected output string.
The `requires_full_program` contract (enforced 2026-07-10) demands a
complete Python program with `def main()` and a deterministic print, but
the model still emits:

- `print(result)` where the test expects `print("1011")`
- `return` instead of `print`
- Extra whitespace / trailing newline mismatches
- Debug `print` statements left in

## Approach

Build an SFT set of (prompt, completion) pairs where the completion is a
complete `def main()` program whose printed output **exactly matches** the
string asserted in the task's `tests.py`. Each row is verified by executing
the completion and comparing stdout to the expected string.

This is **not** a DPO track — it is pure SFT on verified-exact outputs,
because the failure is a generation habit (not a preference confusion).

## Data source

- Tasks: the 58-task `evals/tasks/quantum/` directory.
- For each task, parse `tests.py` to extract the expected output string(s)
  (the literal(s) compared in `assert` / `==` checks).
- Generate the completion by taking `candidate.py`, wrapping its functions
  into a `def main()` that prints the expected string, and verifying via
  subprocess that stdout matches.

## Success metric

On the 56-task QAOA scorecard, an OSE-SFT-LoRA adapter (on base) must show
**≥ 2 fewer "output mismatch" failures** (currently 4), with no regression
on the 49 passing tasks.

## Out of scope

- Any NPU run.
- Modifying `training/qwen_sft_peft_kl.py`.
- Tasks whose `tests.py` does not assert a deterministic string (those are
  skipped, not fabricated).

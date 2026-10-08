# Task Design Conventions

**Date:** 2026-07-09
**Status:** Active convention. Applies to all new tasks in `evals/tasks/`.

## Core rule: tasks must require a complete, runnable program that computes and prints a result.

A task is valid only if the candidate must write a **full program with a `main()` (or equivalent top-level execution) that calculates a concrete value and prints it** — not just a function that returns a value for the test harness to inspect.

### Why

1. **End-to-end realism.** Real users ask "write a program that solves X and shows the answer," not "write a function returning a list." The eval should match the use case.
2. **Forces computation, not just shape.** A function can pass by returning the right type/shape without ever running the quantum circuit. A program that must *print the computed answer* cannot fake it.
3. **Catches import/runtime errors at the top level.** A function-only task can hide a broken `from qiskit_algorithms import MinimumEigenOptimizer` (the deepseek-v4-pro failure on 2026-07-09) because the import may not execute until `main()` runs.
4. **Matches the QAOA 5-cycle gold standard.** `quantum_qaoa_maxcut_5cycle` is the reference: it requires building the graph, running QAOA, and printing binary solution + vertex sets + cut value. New tasks should follow this shape.

### Acceptable task shapes

| Shape | Allowed? | Example |
|-------|----------|---------|
| Full program, `main()`, prints computed result | ✅ Yes — preferred | `qaoa_maxcut_5cycle` |
| Full program, top-level code, prints computed result | ✅ Yes | script that runs and prints |
| Function that returns a value, test harness calls it | ⚠️ Only if computation is verifiable AND the function body runs the real algorithm (not a lookup) | `bell_pair_construction` (returns amplitudes, but the math is the computation) |
| Function that returns a hardcoded constant | ❌ No | `def bell_pair_state(): return [0.707, 0, 0, 0.707]` with no computation |
| Program that prints only "done" / no computed value | ❌ No | fails the "calculate something" rule |

### Test harness contract

For full-program tasks, `tests.py` must:
1. Execute the candidate as a subprocess (see `qaoa_maxcut_5cycle/tests.py` for the pattern).
2. Parse the printed output (regex for the binary solution / cut value / etc.).
3. Verify the *computed* value is correct, not just that the program ran.
4. Timeout (180s default) so a hung program fails, not hangs the eval.

For function-style tasks (legacy, allowed only per the table above), `tests.py` imports the candidate and calls the function — but a follow-up task should always exist that requires the full-program form.

### Migration

Existing function-style tasks in `evals/tasks/quantum/` and `evals/tasks/software/` are **not** deleted — they still test shape-level correctness. But every new task added from 2026-07-09 onward must be the full-program-computes-and-prints form. When iter-3 dataset curation begins, prioritize converting high-value function tasks to full-program form.

## Reference implementation

- Task spec: `evals/tasks/quantum/qaoa_maxcut_5cycle/task.json`
- Reference solution: `evals/tasks/quantum/qaoa_maxcut_5cycle/candidate.py` (uses `main()`, builds QP, runs QAOA, prints binary + sets + cut)
- Test harness: `evals/tasks/quantum/qaoa_maxcut_5cycle/tests.py` (subprocess + output parsing + value verification)

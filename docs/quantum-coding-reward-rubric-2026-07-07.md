# Quantum-Coding Reward Rubric v1

**Date:** 2026-07-07
**Author:** Track D (parallel session B)
**Status:** Spec only. No trainer changes in this track.
**Scope:** Defines the reward function for RLVR / GRPO on the quantum-coding
LLM (Qwen3.6-27B and Qwen3.6-35B-A3B). The rubric is *framework-aware* and
*hardware-plausible*: it rewards code that actually runs and produces the
right answer, and penalizes code that is merely plausible-looking.

## 1. Why a rubric

The current GRPO pipeline (`training/qwen35b_*.py`,
`training/agentic_grpo_trainer.py`) uses a binary pass/fail verifier reward.
For quantum coding, binary pass/fail is too sparse:

- A candidate that produces the correct statevector but uses a deprecated
  Qiskit API (`qiskit.Aer` instead of `qiskit_aer.AerSimulator`) gets 0
  today, even though the algorithm is correct.
- A candidate that runs but gives a wrong numerical answer due to a single
  sign error in a Hamiltonian coefficient gets 0, indistinguishable from a
  candidate that crashes on import.
- A candidate that produces correct results for the easy 80% of test cases
  but fails the hard 20% gets the same 0 as a total failure.

A dense, framework-aware rubric lets GRPO extract signal from partial
credit, accelerating convergence without sacrificing correctness.

## 2. Reward composition

```
R(response, task) = w_pass * R_pass
                   + w_partial * R_partial
                   + w_run * R_runnable
                   + w_api * R_api_correct
                   + w_style * R_style
                   - w_len * R_length_penalty
                   - w_halluc * R_hallucination_penalty
```

Default weights (in `configs/rl/reward_rubric_v1.json`):

| Component | Weight | Range | What it measures |
|---|---|---|---|
| `R_pass` | 1.0 | {0, 1} | All tests pass |
| `R_partial` | 0.3 | [0, 1] | Fraction of test cases passed |
| `R_runnable` | 0.2 | {0, 1} | Code executes without raising on import or first call |
| `R_api_correct` | 0.2 | [0, 1] | Fraction of framework API calls that are current (not deprecated) |
| `R_style` | 0.1 | [0, 1] | Lint-clean (pyflakes + import sort) |
| `R_length_penalty` | 0.05 | [0, 1] | `min(1, max(0, len_chars - 4000) / 4000)` |
| `R_hallucination_penalty` | 0.5 | [0, 1] | Fraction of imported symbols that do not exist in the framework |

`R_pass` is the dominant signal. `R_partial`, `R_runnable`, and `R_api_correct`
provide gradient when `R_pass = 0`. The penalties are negative and capped.

## 3. Component definitions

### 3.1 R_pass

Binary. Computed by the existing task `tests.py` runner:

```python
result = tests.run_tests(candidate_path)
R_pass = 1.0 if result["passed"] else 0.0
```

### 3.2 R_partial

When `tests.py` reports per-test-case failures (the standard `details` list
in this repo's task format), `R_partial` is `n_passed / n_total`:

```python
details = result.get("details", [])
if result["passed"]:
    R_partial = 1.0
elif details and all(isinstance(d, str) and d.startswith("FAIL") for d in details):
    # details are per-case failure strings; n_total comes from the task spec
    n_failed = len(details)
    n_total = task.n_test_cases
    R_partial = max(0.0, (n_total - n_failed) / n_total)
else:
    R_partial = 0.0
```

Tasks that don't expose per-case details give `R_partial = 0` on failure.
This is intentional: we don't want to guess partial credit when the test
harness can't tell us how close we got.

### 3.3 R_runnable

The candidate module must be importable AND the function the task asks for
must be callable without raising:

```python
import importlib.util
spec = importlib.util.spec_from_file_location("candidate", candidate_path)
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
    fn = getattr(mod, task.entry_function)
    R_runnable = 1.0 if callable(fn) else 0.0
except Exception:
    R_runnable = 0.0
```

### 3.4 R_api_correct

Framework-aware. For each framework we maintain a list of deprecated API
paths and their replacements. The candidate's AST is scanned for
`Attribute` chains matching deprecated paths.

```python
deprecated = {
    "qiskit": {
        "qiskit.Aer": "qiskit_aer.AerSimulator",
        "qiskit.execute": "backend.run",
        "qiskit.tools.monitor": "qiskit.providers.job_status",
        "qiskit.circuit.QuantumCircuit.qasm": "QuantumCircuit.qasm() -> str  # use qiskit.qasm2.export",
    },
    "cirq": {
        "cirq.google.XmonDevice": "cirq.google.devices.XmonDevice",
    },
    "pennylane": {
        "pennylane.DefaultQubit": "pennylane.devices.DefaultQubit",
    },
    "braket": {},
}
```

`R_api_correct = 1 - (n_deprecated_calls / max(1, n_framework_calls))`.

### 3.5 R_style

Run `pyflakes` on the candidate file (no external dependency beyond what's
already in the dev env). `R_style = 1` if no warnings, `0` otherwise. We do
NOT use black/autopep8 output as a reward signal because style formatting
is cheap to fix in post-processing and we don't want to spend RL budget on
it.

### 3.6 R_length_penalty

```python
R_length_penalty = min(1.0, max(0.0, (len(candidate_text) - 4000) / 4000))
```

Penalizes responses longer than 4000 characters, linearly up to 8000
characters where the penalty saturates at 1.0. This is a soft prior against
verbose completions; the 4000-char threshold is calibrated to the 95th
percentile of the iter-2 teacher responses.

### 3.7 R_hallucination_penalty

For each `import` statement in the candidate, attempt to resolve the
imported module + attribute. If the attribute does not exist in the
installed version of the framework, it counts as a hallucination.

```python
import importlib
n_total = 0
n_halluc = 0
for stmt in ast.parse(candidate_text).body:
    if not isinstance(stmt, ast.Import) and not isinstance(stmt, ast.ImportFrom):
        continue
    # resolve and check getattr existence
    ...
    n_total += 1
    n_halluc += 0 if resolved else 1
R_hallucination_penalty = n_halluc / max(1, n_total)
```

This is the strongest penalty (weight 0.5) because hallucinated APIs are
worse than wrong numbers: they signal that the model is pattern-matching
rather than recalling real framework structure.

## 4. Framework detection

The task spec carries an optional `framework` field (`qiskit`, `cirq`,
`pennylane`, `braket`, or `none`). If absent, the rubric infers it from
imports in the candidate. If detection fails, `R_api_correct` and
`R_hallucination_penalty` are both set to 0 (no reward, no penalty) so the
rubric degenerates to pass/partial/runnable/style.

## 5. Reward normalization

The final reward is clamped to `[-0.5, 1.6]` (the theoretical min/max from
the weights above) and then min-max normalized per-batch in the GRPO
advantage computation. The existing `training/grpo_utils.py` normalization
is preserved; the rubric only changes the *pre-normalization* reward.

## 6. Floor for training

Following the iter-2 RL-distill config (`rl_distill_35b_asi3_v1.json`
`eval.reward_floor_for_train: 0.20`), only rollouts with `R >= 0.20` are
admitted to the GRPO advantage buffer. This drops hopeless rollouts early
and avoids wasting trainer steps on negative-advantage noise.

## 7. Configuration

The rubric is fully specified by `configs/rl/reward_rubric_v1.json`, which
is loaded by the trainer at startup. Changing the rubric does NOT require a
code change to the trainer; only a config edit. This lets us ablate
components easily (e.g. set `w_partial: 0.0` to measure the value of
partial credit).

## 8. Ablation plan (suggested, not enforced)

| Run | Change | Hypothesis |
|---|---|---|
| A | Default weights | Baseline |
| B | `w_partial: 0.0` | Partial credit adds gradient noise |
| C | `w_halluc: 0.0` | Hallucination penalty blocks valid exploration |
| D | `w_len: 0.0` | Length penalty biases against necessary verbosity |
| E | `w_pass: 2.0`, all others 0 | Binary pass/fail is sufficient after warmup |

Run A vs. E is the most important comparison: it tests whether the dense
rubric accelerates convergence relative to the current binary reward.

## 9. Out of scope for this track

- Modifying `training/grpo_trainer.py` or `training/agentic_grpo_trainer.py`
  (owned by the training-launch session).
- Modifying the RL-distill pipeline (owned by session-A).
- Running the ablation plan (requires NPU time; owned by training-launch).
- Adding new task specs.

## 10. Files produced by this track

- `docs/quantum-coding-reward-rubric-2026-07-07.md` (this file)
- `configs/rl/reward_rubric_v1.json` (machine-readable rubric config)

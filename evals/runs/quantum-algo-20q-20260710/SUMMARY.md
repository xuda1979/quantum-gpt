# 20 Quantum Algorithm Problems × Multi-Model Eval — Summary

**Run dir:** `evals/runs/quantum-algo-20q-20260710/`
**Generated:** 2026-07-10 19:32:59 CST
**Total candidates:** 60 (20 problems × 3 models)
**Overall pass rate:** 19/60 (31.7%)

## Important context

- All 20 problems require a **full Python program with `def main()`** that calculates and prints a deterministic result (per the user's requirement).
- Each problem has a **reference solution** that passes its own tests (20/20 — see `logs/reference_check.txt`).
- The **qwen3.6-27b-rag** backend (the 27B Qwen3.6 + RAG adapter, served via the quantum-intelligence MCP service) was **down the entire session** (`HTTP 503: no healthy upstream`). Its 20 candidates are error-stub files; all 20 are scored as failures. **If the service comes back, re-run `/tmp/regen_failed.py` then `/tmp/evaluate_candidates.py` to get real qwen-rag numbers.**
- The two frontier base models (`glm5.2`, `deepseek-v4-pro`) both produced 20/20 code candidates, but `glm5.2` tends to mix explanatory prose into its code output (despite the system prompt forbidding commentary), which causes many `EXIT` failures at parse time.

## Models

| short name | role | backend |
|---|---|---|
| `glm5.2` | frontier base (teacher) | local proxy `http://127.0.0.1:18105/v1/responses` (OpenAI Responses API) |
| `deepseek-v4-pro` | frontier base (teacher) | Huanxin `qdlake` chat completions |
| `qwen3.6-27b-rag` | **27B Qwen3.6 + RAG adapter** (quantum-intelligence MCP backend) | Huanxin `kunlun` chat completions — **DOWN (503)** |

## Per-model pass rate

| Model | Pass | Total | Rate | Notes |
|---|---|---|---|---|
| `glm5.2` | 6 | 20 | 30% | tends to mix prose into code output |
| `deepseek-v4-pro` | 13 | 20 | 65% |  |
| `qwen3.6-27b-rag` | 0 | 20 | 0% | service down (503); all candidates are error stubs |

**Excluding the qwen-rag outage:** 19 / 40 = 47.5% pass rate across the 2 working base models.

## Per-problem results

| # | Problem | `glm5.2` | `deepseek-v4-pro` | `qwen3.6-27b-rag` |
|---|---|---|---|---|
| 1 | `quantum_bell_state_probability` | ✅ PASS | ✅ PASS | ❌ MISSING |
| 2 | `quantum_qft_3qubit_phase` | ❌ EXIT | ✅ PASS | ❌ MISSING |
| 3 | `quantum_grover_2qubit_marked11` | ❌ EXIT | ✅ PASS | ❌ EXIT |
| 4 | `quantum_maxcut_bruteforce_4vertices` | ✅ PASS | ✅ PASS | ❌ MISSING |
| 5 | `quantum_qaoa_maxcut_triangle` | ❌ EXIT | ❌ EXIT | ❌ MISSING |
| 6 | `quantum_deutsch_jozsa_balanced` | ❌ EXIT | ✅ PASS | ❌ EXIT |
| 7 | `quantum_bernstein_vazirani_hidden` | ✅ PASS | ✅ PASS | ❌ MISSING |
| 8 | `quantum_swap_test_overlap` | ❌ MISSING | ❌ MISSING | ❌ MISSING |
| 9 | `quantum_teleportation_fidelity` | ❌ MISSING | ❌ EXIT | ❌ MISSING |
| 10 | `quantum_density_matrix_pure_state` | ✅ PASS | ✅ PASS | ❌ EXIT |
| 11 | `quantum_partial_trace_bipartite` | ❌ EXIT | ❌ EXIT | ❌ EXIT |
| 12 | `quantum_pauli_expectation_x` | ❌ EXIT | ❌ EXIT | ❌ EXIT |
| 13 | `quantum_ising_ground_state_energy` | ✅ PASS | ✅ PASS | ❌ MISSING |
| 14 | `quantum_vqe_h2_energy` | ❌ EXIT | ✅ PASS | ❌ MISSING |
| 15 | `quantum_grover_3qubit_marked101` | ❌ EXIT | ✅ PASS | ❌ EXIT |
| 16 | `quantum_phase_estimation_pi4` | ❌ MISSING | ❌ MISSING | ❌ MISSING |
| 17 | `quantum_bit_flip_code_recovery` | ❌ MISSING | ✅ PASS | ❌ MISSING |
| 18 | `quantum_superdense_coding_11` | ❌ EXIT | ❌ EXIT | ❌ MISSING |
| 19 | `quantum_ghz_state_5qubit` | ✅ PASS | ✅ PASS | ❌ MISSING |
| 20 | `quantum_trotterized_xxz` | ❌ EXIT | ✅ PASS | ❌ EXIT |

## Failure categories

- `EXIT`: 22
- `PASS`: 19
- `MISSING`: 19

## Per-problem, per-model failure details

| Problem | Model | Status | Detail |
|---|---|---|---|
| `quantum_bell_state_probability` | `qwen3.6-27b-rag` | MISSING | missing: ['P(00) = 0.', 'P(11) = 0.'] |
| `quantum_qft_3qubit_phase` | `glm5.2` | EXIT | Error: unexpected indent |
| `quantum_qft_3qubit_phase` | `qwen3.6-27b-rag` | MISSING | missing: ['Top: ', '2nd: '] |
| `quantum_grover_2qubit_marked11` | `glm5.2` | EXIT | Error: name 'qc' is not defined |
| `quantum_grover_2qubit_marked11` | `qwen3.6-27b-rag` | EXIT | Error: invalid syntax |
| `quantum_maxcut_bruteforce_4vertices` | `qwen3.6-27b-rag` | MISSING | missing: ['Max cut value: 4', 'Optimal bitstring: '] |
| `quantum_qaoa_maxcut_triangle` | `glm5.2` | EXIT | Error: 'Maxcut' object has no attribute 'max_cut_value' |
| `quantum_qaoa_maxcut_triangle` | `deepseek-v4-pro` | EXIT | Error: cannot import name 'COBYLA' from 'qiskit_algorithms' (/Users/daxu/software/quantum-gpt/.venv/lib/python3.9/site-packages/qiskit_algorithms/__in |
| `quantum_qaoa_maxcut_triangle` | `qwen3.6-27b-rag` | MISSING | missing: ['Binary solution: ', 'Max-cut value: 2'] |
| `quantum_deutsch_jozsa_balanced` | `glm5.2` | EXIT | Error: name 'circuit' is not defined |
| `quantum_deutsch_jozsa_balanced` | `qwen3.6-27b-rag` | EXIT | Error: invalid syntax |
| `quantum_bernstein_vazirani_hidden` | `qwen3.6-27b-rag` | MISSING | missing: ['Hidden string: 101'] |
| `quantum_swap_test_overlap` | `glm5.2` | MISSING | missing: ['P(0) = 0.7', '|<A|B>|^2 = 0.'] |
| `quantum_swap_test_overlap` | `deepseek-v4-pro` | MISSING | missing: ['P(0) = 0.7', '|<A|B>|^2 = 0.'] |
| `quantum_swap_test_overlap` | `qwen3.6-27b-rag` | MISSING | missing: ['P(0) = 0.7', '|<A|B>|^2 = 0.'] |
| `quantum_teleportation_fidelity` | `glm5.2` | MISSING | missing: ['<X> on Bob = 1.000000'] |
| `quantum_teleportation_fidelity` | `deepseek-v4-pro` | EXIT | Error(f"Invalid observable type: {type(observable)}") TypeError: Invalid observable type: <class 'tuple'> |
| `quantum_teleportation_fidelity` | `qwen3.6-27b-rag` | MISSING | missing: ['<X> on Bob = 1.000000'] |
| `quantum_density_matrix_pure_state` | `qwen3.6-27b-rag` | EXIT | Error: invalid syntax |
| `quantum_partial_trace_bipartite` | `glm5.2` | EXIT | Error: invalid syntax |
| `quantum_partial_trace_bipartite` | `deepseek-v4-pro` | EXIT | Error: unsupported operand type(s) for @: 'DensityMatrix' and 'DensityMatrix' |
| `quantum_partial_trace_bipartite` | `qwen3.6-27b-rag` | EXIT | Error: invalid syntax |
| `quantum_pauli_expectation_x` | `glm5.2` | EXIT | Error: name 'QuantumCircuit' is not defined |
| `quantum_pauli_expectation_x` | `deepseek-v4-pro` | EXIT | Error( ValueError: Length of () inconsistent with last dimension of [0.] |
| `quantum_pauli_expectation_x` | `qwen3.6-27b-rag` | EXIT | Error: invalid syntax |
| `quantum_ising_ground_state_energy` | `qwen3.6-27b-rag` | MISSING | missing: ['Ground state energy = -1.414214'] |
| `quantum_vqe_h2_energy` | `glm5.2` | EXIT | Error: cannot import name 'Estimator' from 'qiskit.primitives' (/Users/daxu/software/quantum-gpt/.venv/lib/python3.9/site-packages/qiskit/primitives/_ |
| `quantum_vqe_h2_energy` | `qwen3.6-27b-rag` | MISSING | missing: ['VQE energy = -1.85'] |
| `quantum_grover_3qubit_marked101` | `glm5.2` | EXIT | Error: invalid syntax |
| `quantum_grover_3qubit_marked101` | `qwen3.6-27b-rag` | EXIT | Error: invalid syntax |
| `quantum_phase_estimation_pi4` | `glm5.2` | MISSING | missing: ['Estimated phase: 0.2500'] |
| `quantum_phase_estimation_pi4` | `deepseek-v4-pro` | MISSING | missing: ['Estimated phase: 0.2500'] |
| `quantum_phase_estimation_pi4` | `qwen3.6-27b-rag` | MISSING | missing: ['Measurement: ', 'Estimated phase: 0.2500'] |
| `quantum_bit_flip_code_recovery` | `glm5.2` | MISSING | missing: ['P(majority=1) = 1.000'] |
| `quantum_bit_flip_code_recovery` | `qwen3.6-27b-rag` | MISSING | missing: ['P(majority=1) = 1.000'] |
| `quantum_superdense_coding_11` | `glm5.2` | EXIT | Error: invalid syntax |
| `quantum_superdense_coding_11` | `deepseek-v4-pro` | EXIT | Error: cannot import name 'StatevectorSampler' from 'qiskit_aer.primitives' (/Users/daxu/software/quantum-gpt/.venv/lib/python3.9/site-packages/qiskit |
| `quantum_superdense_coding_11` | `qwen3.6-27b-rag` | MISSING | missing: ['Decoded bits: 11', 'Probability: 1.000'] |
| `quantum_ghz_state_5qubit` | `qwen3.6-27b-rag` | MISSING | missing: ['P(all-0 or all-1) ='] |
| `quantum_trotterized_xxz` | `glm5.2` | EXIT | Error: name 'circuit' is not defined |
| `quantum_trotterized_xxz` | `qwen3.6-27b-rag` | EXIT | Error: invalid syntax |

## Files

- `prompts/<id>.txt` — user prompt for each problem
- `reference/<id>.py` — golden solution (passes 20/20)
- `tests/<id>.json` — expected key output substrings
- `candidates/<model>/<id>.py` — generated candidate code (60 files)
- `logs/reference_check.txt` — reference verification log (20/20 pass)
- `logs/generation_log.json` — model call timings + status
- `logs/evaluation_results.json` — full per-candidate evaluation results
- `logs/evaluation_results.txt` — pipe-separated human-readable results
- `CODE_DOCUMENTATION.md` — **all 60 candidate programs + 20 reference solutions** (full source)
- `SESSION_TRACKER.md` — R&D method, status, and resumption notes
- `PROBLEMS.json` — problem manifest

## How to reproduce

```bash
# 1. Verify reference solutions (should be 20/20)
.venv/bin/python3 /tmp/verify_references2.py

# 2. Generate candidates from all 3 models
.venv/bin/python3 /tmp/gen_candidates.py

# 3. Retry any that failed (e.g. qwen-rag once service recovers)
.venv/bin/python3 /tmp/regen_failed.py

# 4. Evaluate every candidate
.venv/bin/python3 /tmp/evaluate_candidates.py

# 5. Rebuild the documentation
.venv/bin/python3 /tmp/build_doc.py
```

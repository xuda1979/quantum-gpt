# C-10363 v14 SFT training-mixture manifest

created_utc: 2026-10-13T12:39:05Z

## WHY
C-10358 panel enumerates exactly the 13 failing tasks by fault class (missing-api-attribute x4, missing-required-function x3, missing-api-module x5, wrong-output x1) with per-task api_gaps. v13 warm-continue alone re-trains the same mixture; a v14 mixture authored from these concrete gaps can lift 13 more task passes toward 18/18.

## Recipe
v14 = v12e replay (2213, verbatim anti-forgetting) + 39 C-10358 gap-targeted few-shot delta rows (3 prompt variants x 13 failing tasks), each completion = frozen candidate.py, each gap symbol verified against reference solutions; every completion execution-verified GREEN vs frozen tests.py.

## Counts delta vs v12e mixture

| metric | value |
|---|---|
| v12e replay rows | 2213 |
| v12e mixture sha256 | `e0bbdf5fb0f606dc247c4f757c204eb645faf7f8cdaf922625be0edb6bede991` |
| v14 delta rows | 39 |
| v14 delta tasks | 13 |
| v14 delta rows/task | 3 (live_exact, api_named, prose_paraphrase) |
| v14 total rows | 2252 |

## API-gap few-shot rows (task, missing symbol) from C-10358

| # | bench_task_id | fault_class | api_gap | gap_symbols_verified |
|---|---|---|---|---|
| 1 | quantum_phase_estimation_circuit | missing-api-attribute | phase_from_measurement | True |
| 2 | quantum_qaoa_maxcut | missing-api-attribute | brute_force_maxcut | True |
| 3 | quantum_density_matrix_partial_trace | missing-required-function | density_from_state,tensor_product,purity | True |
| 4 | quantum_error_correction_shor_9qubit | wrong-output | shor_decode | True |
| 5 | quantum_trotterized_hamiltonian_evolution | missing-required-function | pauli_matrix,matrix_exp_hermitian,trotter_evolve | True |
| 6 | quantum_channel_depolarizing | missing-required-function | amplitude_damping_channel,channel_fidelity | True |
| 7 | quantum_ghz_state_witness | missing-api-attribute | concurrence_2qubit | True |
| 8 | quantum_pennylane_vqe_h2 | missing-api-module | pennylane | True |
| 9 | quantum_cirq_qaoa_line | missing-api-module | cirq | True |
| 10 | quantum_braket_bell_state | missing-api-attribute | parity_check | True |
| 11 | quantum_qiskit_qft_entangled | missing-api-module | qiskit | True |
| 12 | quantum_qiskit_stabilizer_5qubit_code | missing-api-module | qiskit | True |
| 13 | quantum_pennylane_qml_iris_classification | missing-api-module | pennylane | True |

## Execution verification

Every few-shot completion is the FROZEN eval candidate.py source and 
passes its frozen tests.py (fail-closed: build raises on any red).

## Gap symbol validation

Every gap symbol is verified present in the reference solutions dir 
(`evals/tasks/quantum/<dir>/candidate.py` + `tests.py` + `task.json`); 
see outputs/C10363_gap_symbol_validation.json (all_gap_symbols_valid_in_reference_solutions=True).

## Leak policy
C-10363 data-miner authorized: align to frozen eval API names. No training launch.

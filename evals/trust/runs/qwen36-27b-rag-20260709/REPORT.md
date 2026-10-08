# Trustable Evaluation Report

- **run_hash**: `23c0cc51081f7bd6793babfb0d104cd5f645b87719f74e29e350030d7a1652d5`
- **suite_hash**: `00261c29f0a74168a0989a016dcf4aeb61c3ca044da9405bf0d1d916597d678c`
- **model**: `qwen3.6-27b-rag` (legacy)
- **k**: 1  **temperature**: None  **seed**: 0
- **python**: `3.14.5` on `Darwin arm64 CPython`
- **git_commit**: `e7c5d3d142e318fd26793a08900dd5349f918657`

## Summary

- n_tasks: **56**
- n_pass: **47**
- pass_at_1: **0.8393**

## Per-task

| task_id | domain | category | n_pass_det | pass_at_1 |
|---|---|---|---|---|
| quantum_bell_pair_construction | quantum | circuit_construction | 1 | 1.0 |
| quantum_binary_measurement_decoder | quantum | algorithm_implementation | 1 | 1.0 |
| quantum_bitstring_maxcut_landscape | quantum | algorithm_implementation | 1 | 1.0 |
| quantum_braket_bell_state | quantum | algorithm_implementation | 0 | 0.0 |
| quantum_channel_depolarizing | quantum | algorithm_implementation | 1 | 1.0 |
| quantum_circuit_depth_optimization | quantum | circuit_optimization | 1 | 1.0 |
| quantum_circuit_phase_repair | quantum | debug_repair | 1 | 1.0 |
| quantum_cirq_qaoa_line | quantum | algorithm_implementation | 0 | 0.0 |
| quantum_density_matrix_partial_trace | quantum | algorithm_implementation | 1 | 1.0 |
| quantum_error_correction_shor_9qubit | quantum | algorithm_implementation | 1 | 1.0 |
| quantum_error_detection_bit_flip | quantum | debug_repair | 1 | 1.0 |
| quantum_gate_alias_casefold_barrier | quantum | api_normalization | 1 | 1.0 |
| quantum_gate_alias_normalization | quantum | api_normalization | 1 | 1.0 |
| quantum_gate_alias_registry_cleanup | quantum | api_normalization | 1 | 1.0 |
| quantum_gate_token_canonicalizer | quantum | api_normalization | 1 | 1.0 |
| quantum_ghz_state_witness | quantum | algorithm_implementation | 1 | 1.0 |
| quantum_grover_oracle_diffusion | quantum | algorithm_implementation | 1 | 1.0 |
| quantum_maxcut_assignment_enumerator | quantum | algorithm_implementation | 1 | 1.0 |
| quantum_maxcut_partition_ranker | quantum | algorithm_reasoning | 1 | 1.0 |
| quantum_measurement_bug_repair | quantum | debug_repair | 1 | 1.0 |
| quantum_pauli_message_codec | quantum | api_normalization | 1 | 1.0 |
| quantum_pennylane_qml_iris_classification | quantum | quantum_ml | 0 | 0.0 |
| quantum_pennylane_vqe_h2 | quantum | algorithm_implementation | 0 | 0.0 |
| quantum_phase_estimation_circuit | quantum | algorithm_implementation | 1 | 1.0 |
| quantum_phase_measurement_register | quantum | algorithm_implementation | 1 | 1.0 |
| quantum_phase_register_roundtrip | quantum | interface_contract | 1 | 1.0 |
| quantum_qaoa_maxcut | quantum | algorithm_implementation | 1 | 1.0 |
| quantum_qaoa_maxcut_5cycle | quantum | algorithm_implementation | 0 | 0.0 |
| quantum_qft_phase_pattern | quantum | algorithm_reasoning | 1 | 1.0 |
| quantum_qiskit_qft_entangled | quantum | algorithm_implementation | 0 | 0.0 |
| quantum_qiskit_stabilizer_5qubit_code | quantum | quantum_error_correction | 0 | 0.0 |
| quantum_stabilizer_tableau_update_repair | quantum | debug_repair | 1 | 1.0 |
| quantum_superdense_coding | quantum | reasoning | 1 | 1.0 |
| quantum_superdense_identity_lookup | quantum | reasoning | 1 | 1.0 |
| quantum_superdense_pauli_router | quantum | reasoning | 1 | 1.0 |
| quantum_teleportation_corrections | quantum | protocol_logic | 1 | 1.0 |
| quantum_trotterized_hamiltonian_evolution | quantum | algorithm_implementation | 1 | 1.0 |
| quantum_vqe_energy_minimization | quantum | algorithm_implementation | 1 | 1.0 |
| software_async_task_timeout_retry | software | concurrency | 1 | 1.0 |
| software_config_merge | software | data_transforms | 1 | 1.0 |
| software_docstring_contract | software | api_quality | 1 | 1.0 |
| software_duplicate_logic_refactor | software | refactor | 1 | 1.0 |
| software_json_schema_validator | software | data_validation | 1 | 1.0 |
| software_log_parser_aggregator | software | data_processing | 1 | 1.0 |
| software_multifile_patch_conflict_repair | software | multifile_repair | 1 | 1.0 |
| software_off_by_one_bugfix | software | bugfix | 1 | 1.0 |
| software_parser_regression_tests | software | test_writing | 1 | 1.0 |
| software_patch_application_conflict_resolver | software | stateful_logic | 1 | 1.0 |
| software_regex_capturing_group_extractor | software | string_parsing | 1 | 1.0 |
| software_retry_decorator | software | design_pattern | 1 | 1.0 |
| software_session_event_log | software | stateful_logic | 1 | 1.0 |
| software_session_window_summary | software | stateful_logic | 1 | 1.0 |
| software_sql_join_resolver | software | data_processing | 1 | 1.0 |
| software_tree_serialization | software | data_structures | 1 | 1.0 |
| software_workspace_patch_bundle_repair | software | workspace_repair | 0 | 0.0 |
| software_workspace_runner_smoke | software | workspace_smoke | 0 | 0.0 |

## Disagreements

- 0 tasks with judge disagreement: []

## Reproduction

Reproduce with:
```bash
python -m evals.trust.cli.main reproduce --run 23c0cc51081f7bd6793babfb0d104cd5f645b87719f74e29e350030d7a1652d5
```

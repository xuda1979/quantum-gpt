# Iter-3 Dataset Rows — Finalized 2026-07-12

**Purpose:** Consolidate the manual gap draft (`iter2-eval-gap-report-2026-07-11.md` §4)
with the machine-generated gap recs (`docs/iter3-gap-rec-crossref-2026-07-12.md`)
into a single, finalized iter-3 dataset row list for `scripts/prepare_iter3_distill_sft.py`.

**Key finding:** The manual draft and machine recs are **complementary, not conflicting**.
The manual draft was derived from the 20q eval scorecard (QAOA/DensityMatrix/Pauli/
teleportation/DJ-BV task families). The machine recs were derived from the QAOA 56-task
scorecard (braket/cirq/pennylane framework gaps + software data_processing tasks).
**Zero task overlap** between the two lists — together they cover distinct gap surfaces.

## Finalized iter-3 dataset rows

### A. Quantum algorithm families (from manual draft §4a-4e, 20q eval)

| Row | Task family | Tasks | Examples to add | Source |
|-----|-------------|-------|-----------------|--------|
| A1 | QAOA end-to-end | `quantum_qaoa_maxcut_5cycle` | 3-5 `StatevectorSampler` programs printing deterministic cut value | manual §4a |
| A2 | DensityMatrix / partial_trace | `quantum_partial_trace_bipartite`, `quantum_density_matrix_pure_state` | 3-5 examples using `qiskit.quantum_info.DensityMatrix` + `partial_trace` with correct `@` semantics | manual §4b |
| A3 | Pauli expectation value | `quantum_pauli_expectation_x`, `quantum_ising_ground_state_energy` | 3-5 examples with explicit `QuantumCircuit` import + `SparsePauliOp` shape correctness | manual §4c |
| A4 | Teleportation / swap test | `quantum_teleportation_fidelity`, `quantum_swap_test_overlap` | 3-5 examples printing exact deterministic marker strings (e.g. `<X> on Bob = 1.000000`) | manual §4d |
| A5 | Deutsch-Jozsa / Bernstein-Vazirani | `quantum_deutsch_jozsa_balanced`, `quantum_bernstein_vazirani_hidden` | 3-5 complete `def main()` programs with explicit circuit construction + measurement | manual §4e |

### B. Quantum framework gaps (from machine recs, QAOA 56-task eval — universal across 3 models)

| Row | Task | Domain/category | Examples to add | Source |
|-----|------|-----------------|-----------------|--------|
| B1 | `quantum_braket_bell_state` | quantum/algorithm_implementation | 3-5 worked examples (braket framework) | machine rec (all 3 models fail) |
| B2 | `quantum_cirq_qaoa_line` | quantum/algorithm_implementation | 3-5 worked examples (cirq framework) | machine rec (all 3 models fail) |
| B3 | `quantum_pennylane_vqe_h2` | quantum/algorithm_implementation | 3-5 worked examples (pennylane VQE) | machine rec (all 3 models fail) |
| B4 | `quantum_qiskit_qft_entangled` | quantum/algorithm_implementation | 3-5 worked examples (qiskit QFT on entangled input) | machine rec (all 3 models fail) |
| B5 | `quantum_pennylane_qml_iris_classification` | quantum/quantum_ml | 3-5 worked examples (pennylane QML iris) | machine rec (all 3 models fail) |

### C. Software data_processing gaps (from machine recs, QAOA 56-task eval — universal across 3 models)

| Row | Task | Domain/category | Examples to add | Source |
|-----|------|-----------------|-----------------|--------|
| C1 | `software_log_parser_aggregator` | software/data_processing | 3-5 worked examples | machine rec (all 3 models fail) |
| C2 | `software_sql_join_resolver` | software/data_processing | 3-5 worked examples | machine rec (all 3 models fail) |

### D. Code-vs-prose discipline (from manual draft §4f, cross-cutting)

| Row | Discipline | Applies to | Examples to add | Source |
|-----|-----------|------------|-----------------|--------|
| D1 | Full-program contract (emit `def main()` code, not doc prose) | All quantum tasks, esp. qwen3.6-27b-rag | 3-5 examples per affected task showing correct code-only output | manual §4f |

## Summary

- **Total task families:** 13 (5 quantum-algo from manual, 5 quantum-framework from machine, 2 software from machine, 1 cross-cutting discipline)
- **Total new examples:** ~39-65 (3-5 per family × 13 families)
- **Confidence:** HIGH for B/C rows (machine-verified across 3 models), MEDIUM for A rows (manual analysis of 20q, awaits full-holdout re-pull)

## Next actions

1. Implement these rows in `scripts/prepare_iter3_distill_sft.py` (transition from scaffold to `build` subcommand).
2. Generate the actual training examples (reference solutions) for each task family — this is the LIMA-style curation work.
3. Once iter-2 adapter weights are materialized (see `models/iter2-adapters-manifest.json`), re-run the 12-task eval to verify the "11/12" claim before training iter-3 on these rows.
4. After iter-3 training, re-run both the 20q and QAOA 56-task evals to measure gap closure on rows B1-B5 and C1-C2 (the machine-verifiable wins).

## Source documents

- `docs/iter2-eval-gap-report-2026-07-11.md` (manual draft §4)
- `docs/iter3-gap-rec-crossref-2026-07-12.md` (machine recs cross-reference)
- `evals/subsystem/recommendations/qaoa-{glm52,deepseek-v4-pro,qwen36-27b-rag}-base-recs.json` (raw machine recs)

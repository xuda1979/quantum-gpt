# Iter-2 Eval Gap Report — 2026-07-11

**Purpose:** Identify which iter-2 eval results are verified vs. missing/corrupt,
and produce concrete recommendations for iter-3 dataset rows.

**Context:**
- Iter-2 LoRA SFT adapters for 27B (ASI1) and 35B (ASI3) are **UNVERIFIED** —
  adapter weights missing locally (per 2026-07-10 finding). The 12-task eval
  JSONs in `evals/runs/iter2-pull/` are **CORRUPT** (truncated to 2179 bytes,
  invalid UTF-8 at position 2127).
- The "11/12" claims in the July reports are **not reproducible** from this
  machine. This is the #1 blocker for iter-3 dataset fill.
- Two **verified** local evals are available as the only reproducible
  GLM5.2-era signal: `qaoa-maxcut-5cycle-20260709` (56-task, 3 models) and
  `quantum-algo-20q-20260710` (20-task, 3 models).

## 1. Verified eval results (local-disk reproducible)

### 1a. `qaoa-maxcut-5cycle-20260709` — 56-task scorecard, 3 models

| Model | Role | QAOA 5-cycle | Overall 56-task | Failure mode |
|-------|------|:---:|:---:|---|
| `glm5.2` | teacher/base | ✅ PASS (cut=4, optimum) | 49/56 | — |
| `deepseek-v4-pro` | base | ❌ FAIL | 48/56 | `ImportError`: `MinimumEigenOptimizer` from wrong module |
| `qwen3.6-27b-rag` | RAG service (no LoRA) | ❌ FAIL | 48/56 | output is doc prose, not code |

**No trained LoRA adapter was available for this eval.** Source:
`evals/runs/qaoa-maxcut-5cycle-20260709/SUMMARY.md`.

### 1b. `quantum-algo-20q-20260710` — 20-task full-program, 3 models

| Model | Pass | Total | Rate | Notes |
|---|---|---|---|---|
| `glm5.2` | 6 | 20 | 30% | tends to mix prose into code output |
| `deepseek-v4-pro` | 13 | 20 | 65% | strongest base |
| `qwen3.6-27b-rag` | 0 | 20 | 0% | service down (503); all candidates are error stubs |

**Excluding the qwen-rag outage:** 19 / 40 = 47.5% pass rate across the 2
working base models. Failure categories: `EXIT` 22, `PASS` 19, `MISSING` 19.

Source: `evals/runs/quantum-algo-20q-20260710/SUMMARY.md`.

## 2. Missing / corrupt iter-2 artifacts

| Artifact | Status | Location |
|----------|--------|----------|
| `eval-27b-glm52-distill-iter2-pass1-12task-20260706T115000Z.json` | **CORRUPT** (2179 bytes, invalid UTF-8 at pos 2127) | `evals/runs/iter2-pull/` |
| Iter-2 LoRA adapter (27B, ASI1) | **MISSING locally** — `latest_checkpoint: None` per 2026-07-09 SUMMARY | NAS `/root/work/.../outputs/` (not in S3 mirror) |
| Iter-2 LoRA adapter (35B, ASI3) | **MISSING locally** — 11/12 claim not reproducible | NAS `/root/work/.../outputs/` (not in S3 mirror) |
| `asi3-recovered-20260710/` | **EMPTY** — recovery attempt produced no files | `evals/runs/asi3-recovered-20260710/` |

## 3. Failure modes worth targeting in iter-3

Aggregated across the two verified evals, the dominant failure modes are:

1. **`ImportError` from wrong module path** (deepseek-v4-pro on QAOA):
   `MinimumEigenOptimizer` imported from wrong qiskit_algorithms submodule.
2. **`SyntaxError: invalid syntax`** (qwen3.6-27b-rag across many tasks):
   model emits doc prose or markdown-fenced blocks that aren't valid Python.
3. **`NameError`: undefined symbol** (glm5.2 on `quantum_pauli_expectation_x`):
   `QuantumCircuit` / `circuit` used without import.
4. **`TypeError` on DensityMatrix `@`** (deepseek-v4-pro on
   `quantum_partial_trace_bipartite`): operator precedence / type confusion.
5. **Missing deterministic output markers** (qwen3.6-27b-rag): correct code
   structure but fails to print the exact expected output string.
6. **QAOA p=1 cut value off** (qwen3.6-27b-rag): outputs doc prose instead
   of a code program.

## 4. Concrete iter-3 dataset row recommendations

Per the 2026-07-08 MEMORY.md note: `dataset_gap recommend --eval <scorecard.json>
--model adapter` produces concrete "add 3-5 examples for <task>" recs on the
local 25-task scorecards. The 44-task / 495-task holdout eval JSONs live on
remote and the one pulled copy is CORRUPTED — re-pull needed before full-holdout
gap analysis.

Based on the **verified** 20q + QAOA scorecards, the iter-3 dataset should add
3-5 examples for each of these task families:

### 4a. Qiskit `MinimumEigenOptimizer` / QAOA usage
- Tasks: `quantum_qaoa_maxcut_5cycle`, `quantum_qaoa_maxcut_triangle`
- Failure: `ImportError` — `MinimumEigenOptimizer` from wrong module
- Add 3-5 examples showing the correct import:
  `from qiskit_algorithms.optimizers import COBYLA`
  `from qiskit_algorithms import QAOA, MinimumEigenOptimizer`
- Add 2-3 examples of `StatevectorSampler` end-to-end QAOA programs that
  print the deterministic cut value.

### 4b. DensityMatrix / partial_trace operations
- Tasks: `quantum_partial_trace_bipartite`, `quantum_density_matrix_pure_state`
- Failure: `TypeError` on `@` operator; `DensityMatrix` API misuse
- Add 3-5 examples using `qiskit.quantum_info.DensityMatrix` and
  `partial_trace` with correct operator semantics.

### 4c. Pauli expectation value measurement
- Tasks: `quantum_pauli_expectation_x`, `quantum_ising_ground_state_energy`
- Failure: `NameError: QuantumCircuit not defined`; `SparsePauliOp` shape mismatch
- Add 3-5 examples that import `QuantumCircuit` explicitly and compute
  expectation values via `Statevector.expectation_value()`.

### 4d. Teleportation / swap-test fidelity
- Tasks: `quantum_teleportation_fidelity`, `quantum_swap_test_overlap`
- Failure: `MISSING` deterministic output markers
- Add 3-5 examples that print exactly the expected marker strings
  (e.g., `<X> on Bob = 1.000000`).

### 4e. Deutsch-Jozsa / Bernstein-Vazirani
- Tasks: `quantum_deutsch_jozsa_balanced`, `quantum_bernstein_vazirani_hidden`
- Failure: `NameError: circuit`; `SyntaxError`
- Add 3-5 examples of complete `def main()` programs with explicit
  circuit construction and measurement.

### 4f. Code-vs-prose discipline (full-program contract)
- Failure: qwen3.6-27b-rag emits doc prose, not code
- Add 5-10 examples reinforcing the `requires_full_program` contract:
  every response must be a complete Python program with `def main()`
  and a deterministic print.

## 5. Blockers for completing the gap report

- **Re-pull the 12-task iter-2 eval JSONs from NAS/Huanxin.** The
  `evals/runs/iter2-pull/eval-27b-*.json` is corrupt (2179 bytes). Until a
  clean copy is pulled, the "11/12" claim cannot be verified or gap-analyzed.
- **Run `dataset_gap recommend` on the verified 20q + QAOA scorecards.**
  This should be done next tick to produce machine-generated gap
  recommendations (this report's §4 is a manual draft pending that run).

## 6. Immediate next steps

1. Re-pull `eval-27b-glm52-distill-iter2-pass1-12task-*.json` from NAS via
   Huanxin (blocked on flaky transport — see `docs/huanxin-adapter-recovery-2026-07-11.md`).
2. Run `python3 evals/subsystem/dataset_gap.py recommend \
   --eval evals/runs/quantum-algo-20q-20260710/<model>/scorecard.json \
   --model <model>` for each of glm5.2, deepseek-v4-pro to get
   machine-generated gap recs.
3. Cross-reference this manual draft (§4) with the machine recs to finalize
   the iter-3 dataset row list.
4. Fill the iter-3 dataset rows in `scripts/prepare_iter3_distill_sft.py`
   using the finalized list.

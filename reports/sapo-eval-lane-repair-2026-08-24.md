# SAPO eval-lane repair — 2026-08-24 (18-task holdout fully instrumented)

Author: eval-lane repair agent (one-shot directive, 20:18 CST).
Scope: ASI2 eval lane (4 NPUs, exec `http://127.0.0.1:19004/exec`). Read-only on live
training (ASI3, trainer 81132) — untouched. TDD for all scorer changes.

## Verdict (TL;DR)

- All 18 frozen-holdout tasks now score cleanly: **0 import failures, 0 runner
  exceptions** (was: 3 import failures + 4 NoneType runner tracebacks + 1 qiskit
  import failure).
- Reference pass: **18/18** on the ASI2 box through the production flow
  (`prepare_prompts.py` → frozen-contract verification → `run_eval.py`).
- Cached base leg re-scored: **8/18, exact same pass set** as the original
  scorecard — matched comparison stays valid (verdict in §4).
- Scorer repair: 5 tasks hardened, 20 regression tests (TDD, red→green),
  commits `b10d64d`, `e4aa1db`, `e09ec7a`.

## 1. Gap 1 — missing quantum frameworks on the eval host

Before: the scoring interpreter (`/usr/local/python3.11.14/bin/python3`, Python
3.11.14) had NO qiskit, pennylane, cirq or braket — the cached base run
(20260824T044144Z) shows `import failed` for quantum_pennylane_vqe_h2,
quantum_cirq_qaoa_line, quantum_braket_bell_state AND quantum_qiskit_qft_entangled
(the "qiskit present" assumption was wrong for the scoring interpreter).

After (installed into the scoring interpreter; numpy kept at 1.26.4 to protect the
torch_npu 2.9 stack — verified `numpy 1.26.4 torch 2.9.0+cpu` post-install):

| Package | Version | Notes |
|---|---|---|
| cirq-core | 1.4.1 | matches the ASI3 runtime reference (cirq 1.4.1). cirq-core provides the `cirq` module without provider plugins; the `cirq` metapackage pulls cirq-rigetti→pyquil→rpcq, whose sdist fails to build in pip's isolated build env on this host |
| pennylane | 0.38.0 | numpy<2 compatible (0.45.x needs numpy>=2.0, which conflicts with cirq 1.4.1's `numpy~=1.22`) |
| qiskit | 1.4.2 | numpy<2 compatible (2.x needs numpy>=2.0); provides `qiskit.primitives.StatevectorSampler` + `qiskit.quantum_info.Statevector` used by holdout tasks |
| amazon-braket-sdk | 1.98.0 | `braket.circuits.Circuit` + `braket.devices.LocalSimulator` |
| autoray | 0.6.11 | pinned down from 0.11.0 (fresh resolver pick) — 0.11.0 breaks `import pennylane` (`NumpyMimic` removed); 0.6.11 is the proven pairing |

Conflict trace (why not latest): `ResolutionImpossible` — cirq-core 1.4.1
`numpy~=1.22` vs pennylane 0.45.1 `numpy>=2.0` vs qiskit 2.5.0 `numpy>=2.0,<3`.
The box stack requires numpy 1.26.4, so cirq 1.4.1 (directive) wins and the others
are pinned to their numpy-1.x releases.

## 2. Gap 2 — runner-exception tasks (scorer hardening)

Before: candidates returning `None` (or omitting functions) crashed the scorers
with NoneType TypeErrors / AttributeErrors → `error_type=TypeError|AttributeError,
failure_category=runtime` (runner_exception) instead of a verdict.

Fix (smallest change per task; rubric untouched): all candidate-call sites treat
`None` returns as clean assertion failures with diagnostic details; each scorer
gains a contract-completeness precheck (missing required function → clean fail
with the exact missing names).

| Task | Before | Fix | After (base candidate) |
|---|---|---|---|
| density_matrix_partial_trace | `_mat_close`: `len(None)` → TypeError | `_mat_close`/`_num_close` None guards; required-fn precheck (density_from_state, tensor_product, partial_trace, purity) | `assertion: candidate missing required function(s): purity` |
| quantum_error_correction_shor_9qubit | `len(encoded_0)` on None (incl. inside the failure message itself) | `_close` None guard; shor_encode/apply_x_error None branches; message no longer calls `len(None)`; required-fn precheck | `assertion: missing apply_x_error, shor_decode` |
| trotterized_hamiltonian_evolution | `result[0][0]` on None | `_close_vec`/`_close_mat` guards; matrix_exp_hermitian/trotter_evolve/pauli_matrix('Y') None branches; required-fn precheck | `assertion: missing trotter_evolve` |
| quantum_channel_depolarizing | `_close`: `abs(None - b)` | `_close`/`_mat_close` guards; trace-check None branch; required-fn precheck | `assertion: fidelity(...) = None, expected 1.0` |
| cirq_qaoa_line (newly exposed by the cirq install) | `module.best_maxcut_value` missing → AttributeError | required-fn precheck (maxcut_line_edges, best_maxcut_value, maxcut_value, qaoa_line_circuit, measure_bitstrings) | `assertion: missing best_maxcut_value, maxcut_value` |

TDD: `tests/test_eval_lane_repair_scorers.py` — 20 tests (4 per task × 5 tasks):
`test_reference_solution_passes_without_traceback`,
`test_none_returning_candidate_scores_clean_fail`,
`test_harness_classifies_none_candidate_as_assertion` (via `run_eval.run_task`:
`error_type is None`, `failure_category == "assertion"`),
`test_missing_function_candidate_scores_clean_fail`. Red confirmed for every
failure mode first (the None-stub test reproduced the exact
`TypeError: object of type 'NoneType' has no len()` traceback; the missing-fn
tests reproduced the exact AttributeError the cached base candidates trigger).
20/20 green. Eval suites re-run: test_promotion_eval_prompt_isolation,
test_aggregate_strict_holdout_comparisons, test_artifact_scoring,
test_assert_no_strict_holdout_regression — all pass.

## 3. Verification — all 18 references pass under the fixed harness

- Local (Mac): 18/18 via `run_eval.py` over the frozen 18-task manifest.
- ASI2 box: 18/18 via the production flow — `prepare_prompts.py` (regenerates
  manifest incl. the NEW `test_file_sha256`/`scorer_contract_sha256`), then
  `run_eval.py --candidate-map` (frozen-contract verification included, no
  SystemExit). Run dir: `evals/runs/sapo-repair-reference-20260824T131444Z`.

## 4. Cached base leg — reuse verdict

Re-scored the cached base candidates (byte-identical copies from
`sapo-promotion-base-20260824T044144Z`) under the repaired env + scorers
(run dir `evals/runs/sapo-promotion-base-rescore-20260824T131503Z`):

- **8/18 — identical pass set** to the original scorecard (gate_alias_normalization,
  phase_estimation_circuit, qaoa_maxcut, superdense_coding, grover_oracle_diffusion,
  ghz_state_witness, phase_register_roundtrip, binary_measurement_decoder).
- Failure summary: `{'assertion': 10}` — **zero runtime, zero runner exceptions,
  zero import failures**; every failure carries a diagnostic detail.
- The 4 previously-runner-exception tasks and the 5 previously-unscorable tasks
  now produce real verdicts (all FAIL for the base model — genuine model-quality
  deficits now visible, e.g. `missing purity`, `fidelity = None`, braket
  `run_openqasm()` API mismatch, `syndrome_of('IIIII') must be '0000'`).

VERDICT: **the cache is reusable as candidate artifacts; the old scorecard itself
is not reusable as-is.** The old manifest bakes in the OLD `test_file_sha256` /
scorer contract, and `run_eval.py` fails closed on that mismatch by design.
Re-scoring costs zero model inference (scoring is a deterministic pure function of
candidate files + task tests + env), so future legs regenerate the base scorecard
under the same env+scorers — the matched base-vs-SAPO comparison stays valid with
no workflow change (`run_sapo_three_state_promotion_eval.sh` already prepares
fresh manifests per leg).

## 5. Ready command for the next holdout

```bash
cd /root/work/software/quantum-gpt
SAPO_PROMOTION_WARM_ADAPTER=/root/work/software/quantum-gpt/outputs/qg-27b-glm52-distill-sft-glm52-distill-27b-20260706T083156Z/adapter \
SAPO_PROMOTION_SAPO_ADAPTER=/root/work/software/quantum-gpt/outputs/sapo-27b-ai-<RUN_ID>/step_<N>_adapter \
bash scripts/run_sapo_three_state_promotion_eval.sh
```

(Precheck the checkpoint first — verdict must be ACTIVE — per the 08-24 runbook.)
All 18 tasks will score cleanly on every leg.

## 6. Env state (exact, ASI2 box scoring interpreter)

```
python3 = /usr/local/python3.11.14/bin/python3 (Python 3.11.14)
PennyLane==0.38.0
PennyLane_Lightning==0.40.0
amazon-braket-default-simulator==1.40.1
amazon-braket-schemas==1.32.1
amazon-braket-sdk==1.98.0
autoray==0.6.11
cirq-core==1.4.1
networkx==3.6.1
numpy==1.26.4
qiskit==1.4.2
rustworkx==0.18.1
scipy==1.17.0
scipy-openblas32==0.3.34.106.0
sympy==1.14.0
torch==2.9.0+cpu / torch_npu==2.9.0 (unchanged)
```

Install was routed through the tsinghua PyPI mirror (`-i
https://pypi.tuna.tsinghua.edu.cn/simple`) after pypi.org measured ~30 kB/s;
network flake on pypi.org caused one interrupted install (no partial state —
restart resumes from pip's wheel cache).

## 7. Artifacts

- Commits: `b10d64d` (None-safe scorers + first 12 tests), `e4aa1db`
  (missing-function prechecks + 4 tests), `e09ec7a` (cirq_qaoa_line precheck + 4 tests).
- Box run dirs: `evals/runs/sapo-repair-reference-20260824T131444Z` (18/18 refs),
  `evals/runs/sapo-promotion-base-rescore-20260824T131503Z` (cached base re-score).
- Old base cache untouched: `evals/runs/sapo-promotion-base-20260824T044144Z`
  (original 8/18 scorecard preserved for provenance).
- Tests: `tests/test_eval_lane_repair_scorers.py` (20 tests, 20 pass).

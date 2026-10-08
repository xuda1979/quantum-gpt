# Qwen3.6-27B Quantum Coding Eval Manifest

## Recommendation

Use `evals/benchmarks/qwen36_27b_quantum_holdout_v1.txt` as the primary Qwen3.6-27B quantum coding holdout for base-vs-trained checkpoint comparisons.

This is the current best holdout because it is small enough for repeatable checkpoint gating, task-disjoint from the Qwen3.6 domain-expert curriculum, resolves to executable quantum eval tasks, and every task is grounded in curated local quantum docs.

## Artifact Contract

- Benchmark: `evals/benchmarks/qwen36_27b_quantum_holdout_v1.txt`
- Manifest: `data/generated/qwen36-27b-quantum-test-artifacts/manifest.json`
- Source curriculum: `data/generated/qwen36-27b-domain-expert-curriculum-v1/manifest.json`
- Verification JSON: `reports/qwen36_27b_quantum_eval_manifest_report.json`
- Integrity rerun: `reports/qwen36_27b_domain_expert_curriculum_holdout_integrity_rerun.json`

## Holdout Tasks

- `quantum_density_matrix_partial_trace`
- `quantum_channel_depolarizing`
- `quantum_ghz_state_witness`
- `quantum_grover_oracle_diffusion`
- `quantum_phase_register_roundtrip`
- `quantum_binary_measurement_decoder`

## Quality Evidence

- Task count: 6
- Missing task ids: 0
- Artifact train overlap: 0
- Source curriculum train overlap: 0
- Source curriculum eval overlap: 0
- Docs grounded: 6 / 6
- Expected doc source hits: 6 / 6
- Curriculum train/eval integrity: 1696 train rows, 756 eval rows, zero example-id/task-id/prompt-family overlap

## Metric Gate

Primary proof metric: pass@1 on `qwen36_27b_quantum_holdout_v1`, scored by the executable eval runner with no manual repair.

A trained Qwen3.6-27B checkpoint should be considered better than base only if it improves exact pass count over the base checkpoint on the same benchmark, prompt style, token budget, decoding settings, and scorer. For a 6-task holdout, require at least a +2 absolute pass-count gain over base, with no regression on already-passing base tasks, before treating the checkpoint as a meaningful quantum-coding improvement.

Secondary sanity metric: eval loss/perplexity on the high-quality distillation SFT eval split may track training health, but it must not replace executable pass@1 on the holdout.

## Validation Commands

```bash
.venv/bin/python scripts/verify_quantum_eval_artifact.py --output reports/qwen36_27b_quantum_eval_manifest_report.json
python3 scripts/verify_holdout_dataset.py --train-file data/generated/qwen36-27b-domain-expert-curriculum-v1/train.jsonl --eval-file data/generated/qwen36-27b-domain-expert-curriculum-v1/eval.jsonl --manifest data/generated/qwen36-27b-domain-expert-curriculum-v1/manifest.json --min-train-count 1600 --min-eval-count 700 --require-task-disjoint --require-prompt-family-disjoint --output reports/qwen36_27b_domain_expert_curriculum_holdout_integrity_rerun.json
.venv/bin/pytest tests/test_qwen36_quantum_holdout_v1_integrity.py -q
```

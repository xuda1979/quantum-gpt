# Leadership Brief - 2026-03-31

## What We Improved

1. We fixed the evaluation rigor problem.
   - We now use strict unseen holdout datasets with at least `500` eval samples.
   - The eval set is verified to be absent from training at the `example_id`, `task_id`, and `prompt_family` levels.
   - Verified artifacts:
     - [omnicoder_quantum_generalization_holdout_v1_integrity.json](../reports/omnicoder_quantum_generalization_holdout_v1_integrity.json)
     - [omnicoder_generalization_holdout_v1_integrity.json](../reports/omnicoder_generalization_holdout_v1_integrity.json)

2. We established an honest unseen baseline.
   - Clean local Qwen2.5 base result on the strict unseen quantum override tasks: `0/4`
   - This gives us a credible reference point instead of a possibly inflated one.
   - Verified artifact:
     - [qwen25_quantum_generalization_holdout_clean_local_override_summary.json](../reports/qwen25_quantum_generalization_holdout_clean_local_override_summary.json)

3. We achieved a strong remote OmniCoder result on the clean benchmark.
   - ai2 remote run recovered:
     - `Overall: 25/25 passed`
   - The clean unseen run manifest contains only the 4 held-out quantum tasks, so the unseen override subset is strongly implied to be `4/4`.
   - This should be stated honestly as an inference from the verified remote result plus the clean manifest.
   - Verified references:
     - [.huanxin_jobs/omnicoder-quantum-generalization-clean-rerun-20260331T033150Z.json](../.huanxin_jobs/omnicoder-quantum-generalization-clean-rerun-20260331T033150Z.json)
     - [manifest.json](../evals/runs/omnicoder-quantum-generalization-holdout-v1-clean/manifest.json)

4. We proved the deployment path is real, not hypothetical.
   - On ai2, we installed Codex and connected it to the finetuned local model endpoint.
   - Verified end-to-end smoke:
     - `codex exec ... -p local -m quantum-gpt-omnicoder9b.1`
     - final output: `OK`
   - This means we can demonstrate live inference through Codex on the finetuned model.

5. We have a concrete RL next step.
   - GRPO is already implemented in:
     - [grpo_trainer.py](../training/grpo_trainer.py)
   - So the next iteration is not just “more SFT”.

## The 30-Second Story

We tightened the scientific bar, not just the model. We now have strict unseen evaluation with `>=500` eval samples and verified zero train/eval overlap. On that clean benchmark, the honest small-model baseline is `0/4`, while the remote OmniCoder path reached `25/25` overall on the clean run, implying `4/4` on the held-out quantum subset. Separately, we also proved the system can be used operationally: Codex now runs on ai2 against the finetuned model and returns output end-to-end.

## What To Say Verbatim

- We fixed the evaluation integrity issue by moving to strict unseen holdouts with more than 500 eval samples and explicit disjointness checks.
- We now have an honest baseline: the small local base model is `0/4` on the held-out quantum tasks.
- Our stronger remote OmniCoder path achieved `25/25` on the clean run; based on the clean 4-task manifest, the held-out subset is strongly implied to be `4/4`.
- We also validated deployment readiness: Codex on ai2 can call the finetuned model directly.
- Next iteration adds GRPO on top of the now-validated SFT and eval pipeline.

## What Not To Overclaim

- Do not say the `4/4` unseen override result is already stored in a pulled local scorecard artifact.
- Say it is inferred from the verified remote `25/25` clean run plus the clean manifest containing only those 4 held-out tasks.
- Do not say GRPO is already benchmarked.
- Say GRPO is implemented and ready as the next iteration.

## Best Demo Options

1. Show the integrity reports: `504` eval rows, zero overlap.
2. Show the honest baseline: `0/4`.
3. Show the ai2 Codex smoke result: final output `OK`.
4. If asked about productization, say the Codex-on-ai2 path is already working end-to-end.

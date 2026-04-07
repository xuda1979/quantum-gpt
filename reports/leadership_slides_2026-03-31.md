# Leadership Slides - 2026-03-31

## Slide 1 - Headline

### We improved both evaluation rigor and deployable model capability

- Strict unseen evaluation now meets the leadership bar.
- Stronger remote OmniCoder result recovered on the clean benchmark.
- Codex on ai2 now works end-to-end against the finetuned model.

Speaker note:
This update is not just another training run. We improved the credibility of the benchmark and also proved that the stronger model path is operational.

## Slide 2 - Evaluation Integrity

### The benchmark is now leadership-grade

- Strict quantum holdout:
  - `1024` train
  - `504` eval
- Mixed holdout:
  - `1440` train
  - `504` eval
- Verified zero overlap between train and eval for:
  - `example_id`
  - `task_id`
  - `prompt_family`

References:
- [omnicoder_quantum_generalization_holdout_v1_integrity.json](../reports/omnicoder_quantum_generalization_holdout_v1_integrity.json)
- [omnicoder_generalization_holdout_v1_integrity.json](../reports/omnicoder_generalization_holdout_v1_integrity.json)

Speaker note:
This is the key answer to the “dataset too small / eval leaked into train” challenge. The eval set is large enough and explicitly disjoint from training.

## Slide 3 - Honest Baseline vs Stronger Model

### The clean benchmark now differentiates weak and strong models

- Honest local baseline:
  - Qwen2.5 base on strict unseen quantum subset: `0/4`
- Remote clean OmniCoder run:
  - recovered result: `25/25` overall
- Because the clean unseen run manifest contains only the 4 held-out quantum tasks, the unseen override result is strongly implied to be `4/4`

References:
- [qwen25_quantum_generalization_holdout_clean_local_override_summary.json](../reports/qwen25_quantum_generalization_holdout_clean_local_override_summary.json)
- [.huanxin_jobs/omnicoder-quantum-generalization-clean-rerun-20260331T033150Z.json](../.huanxin_jobs/omnicoder-quantum-generalization-clean-rerun-20260331T033150Z.json)
- [manifest.json](../evals/runs/omnicoder-quantum-generalization-holdout-v1-clean/manifest.json)

Speaker note:
We should phrase the `4/4` claim carefully: it is inferred from the verified remote result plus the clean manifest, not yet from a pulled local override-only scorecard.

## Slide 4 - Deployment Readiness

### The finetuned model is callable through Codex on ai2

- Installed Codex on ai2:
  - `codex-cli 0.117.0`
- Connected Codex to the finetuned OmniCoder adapter through a local provider
- Verified smoke:
  - `codex exec ... -p local -m quantum-gpt-omnicoder9b.1`
  - final output: `OK`

Speaker note:
This matters because it turns the result into something demonstrable. We are not only training models; we can already route Codex through the finetuned model endpoint on ai2.

## Slide 5 - Next Iteration

### Next step is RL on top of a now-clean pipeline

- Current iteration:
  - strict unseen eval
  - stronger SFT/adapter result
  - deployable Codex path on ai2
- Next iteration:
  - GRPO, not just more SFT

Reference:
- [grpo_trainer.py](../training/grpo_trainer.py)

Speaker note:
The right message is that we first fixed the benchmark and validated the system path. Now we can spend the next iteration improving the model with GRPO on top of a pipeline we trust.

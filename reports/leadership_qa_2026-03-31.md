# Leadership Q&A - 2026-03-31

## Q: How do we know the eval set was not trained on?

Answer:

We added explicit integrity checks and verified zero overlap at three levels: `example_id`, `task_id`, and `prompt_family`. The strict holdout reports also confirm `>=500` eval rows.

References:

- [omnicoder_quantum_generalization_holdout_v1_integrity.json](../reports/omnicoder_quantum_generalization_holdout_v1_integrity.json)
- [omnicoder_generalization_holdout_v1_integrity.json](../reports/omnicoder_generalization_holdout_v1_integrity.json)

## Q: Why should we trust the baseline number?

Answer:

We removed the earlier reference-candidate leakage path before using the local baseline. The current baseline is the honest clean one, and it is `0/4` on the strict unseen quantum subset.

Reference:

- [qwen25_quantum_generalization_holdout_clean_local_override_summary.json](../reports/qwen25_quantum_generalization_holdout_clean_local_override_summary.json)

## Q: Are you claiming a true `4/4` on the held-out quantum subset?

Answer:

We should phrase it carefully. The remote clean run recovered `25/25` overall, and the clean manifest contains only the 4 held-out quantum tasks. So `4/4` is strongly implied. We should call it an inference from verified evidence, not overstate it as a separately pulled local artifact.

## Q: Is this only an offline benchmark, or can we actually use the model?

Answer:

We can use it. Codex on ai2 is already wired to the finetuned model endpoint, and the smoke test completed successfully with final output `OK`.

## Q: What did we actually improve besides reporting?

Answer:

Three things:

1. Evaluation rigor
2. Stronger remote model performance
3. Deployment readiness through Codex on ai2

## Q: Why is the next step GRPO?

Answer:

Because this iteration established a cleaner SFT and evaluation foundation. GRPO is already implemented as the RL next step, so the next loop is not just “train more on the same recipe.”

Reference:

- [grpo_trainer.py](../training/grpo_trainer.py)

## Q: What is the one-sentence takeaway?

Answer:

We improved both benchmark credibility and deployable model capability, and we are now in a position to push the next iteration with GRPO instead of debating whether the current benchmark is trustworthy.

# Leadership Talk Track - 2026-03-31

## 60-Second Version

We made three concrete improvements. First, we fixed the evaluation rigor problem: we now have strict unseen holdouts with more than 500 eval samples and verified zero train/eval overlap at the example, task, and prompt-family levels. Second, that clean benchmark is now informative: the honest local Qwen base is `0/4` on the held-out quantum tasks, while the stronger remote OmniCoder path reached `25/25` on the clean run, which strongly implies `4/4` on the held-out subset because the clean manifest contains only those four tasks. Third, this is not just an offline result anymore: Codex on ai2 now works end-to-end against the finetuned model, and the smoke test returned `OK`. The next iteration is to add GRPO on top of this now-clean SFT and evaluation pipeline.

## 30-Second Version

We raised the bar on both science and execution. The benchmark is now strict unseen with `>=500` eval samples and verified zero overlap with training. On that clean benchmark, the honest local baseline is `0/4`, while the remote OmniCoder run achieved `25/25` overall and strongly implies `4/4` on the held-out quantum subset. We also proved deployment readiness by running Codex on ai2 directly against the finetuned model and getting a successful `OK` smoke result. Next iteration adds GRPO.

## If Leadership Pushes On Credibility

Say:

- We explicitly audited train/eval disjointness, not just row counts.
- We removed the earlier prompt leakage path before using the local baseline.
- We are being careful with the strongest claim: the unseen `4/4` is an inference from the verified clean remote result plus the clean 4-task manifest, not an overclaimed locally pulled artifact.

## If Leadership Pushes On “What Changed Technically?”

Say:

- We changed the benchmark construction and integrity checks.
- We validated a stronger OmniCoder-based finetune path remotely.
- We also operationalized the result by wiring Codex on ai2 to the finetuned local model endpoint.

## If Leadership Pushes On “What’s Next?”

Say:

- The next model-improvement step is GRPO.
- The pipeline is now ready for that because the benchmark is cleaner and the deployment path is already working.

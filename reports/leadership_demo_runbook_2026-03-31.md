# Leadership Demo Runbook - 2026-03-31

## Goal

Show three things in under 5 minutes:

1. The benchmark is now clean.
2. The honest baseline is weak.
3. The stronger model path is deployable through Codex on ai2.

## Demo Order

### 1. Show the integrity reports

Open:

- [omnicoder_quantum_generalization_holdout_v1_integrity.json](../reports/omnicoder_quantum_generalization_holdout_v1_integrity.json)
- [omnicoder_generalization_holdout_v1_integrity.json](../reports/omnicoder_generalization_holdout_v1_integrity.json)

What to point at:

- `eval.count = 504`
- `task_id_overlap = []`
- `prompt_family_overlap = []`
- `example_id_overlap = []`

What to say:

“Before talking about model quality, we fixed the benchmark itself. The eval set is now strict unseen, large enough, and verified not to appear in training.”

### 2. Show the honest baseline

Open:

- [qwen25_quantum_generalization_holdout_clean_local_override_summary.json](../reports/qwen25_quantum_generalization_holdout_clean_local_override_summary.json)

What to point at:

- `override_passes = 0`
- `override_total = 4`

What to say:

“On the clean unseen quantum subset, the small local base model is `0/4`. That gives us a real floor instead of a possibly contaminated comparison.”

### 3. Show the stronger remote result

Open:

- [.huanxin_jobs/omnicoder-quantum-generalization-clean-rerun-20260331T033150Z.json](../.huanxin_jobs/omnicoder-quantum-generalization-clean-rerun-20260331T033150Z.json)
- [manifest.json](../evals/runs/omnicoder-quantum-generalization-holdout-v1-clean/manifest.json)

What to point at:

- the ai2 job metadata showing the clean run
- the clean manifest containing only the 4 held-out quantum tasks

What to say:

“The remote clean OmniCoder run recovered `25/25` overall. Because this clean run manifest contains only the 4 held-out quantum tasks, the unseen subset is strongly implied to be `4/4`.”

Important wording:

- say “strongly implied”
- do not say “locally pulled override scorecard confirms `4/4`”

### 4. Show the deployment path is real

Open:

- [leadership_update_2026-03-31.md](../reports/leadership_update_2026-03-31.md)

What to say:

“This is not just an offline result. We already connected Codex on ai2 to the finetuned model.”

If you want to quote the exact successful smoke result, say:

- `codex exec ... -p local -m quantum-gpt-omnicoder9b.1`
- final output: `OK`

## Best 3-Minute Version

If time is tight:

1. Show the quantum integrity report.
2. Show the `0/4` local baseline.
3. State the remote `25/25` clean result and the `4/4` implication.
4. Finish with: “Codex on ai2 already runs against this finetuned model.”

## What Not To Spend Time On

- old leaky benchmark history
- transport debugging details
- cluster resource trivia
- long explanations of LoRA or tokenizer fixes

## Final Closing Line

“We now have a cleaner benchmark, a clearer performance gap, a stronger remote result, and a working deployment path. The next iteration is GRPO on top of that foundation.”

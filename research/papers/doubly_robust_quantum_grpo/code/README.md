# Doubly-Robust GRPO — Operator Runbook

This is the operational companion to `../paper.md`. It covers how to
launch, monitor, and diagnose the DR-GRPO run on ASI1 (Qwen3.6-27B,
2 NPUs).

## Prerequisites

- ASI1 reachable, with `/root/work/quantum-gpt` synced to the latest
  repo state.
- `Qwen3.6-27B` available at `/root/work/filestorage/Qwen3.6-27B`
  (override with `MODEL=...`).
- `torch`, `torch_npu`, `transformers`, `peft`, `accelerate` importable
  on ASI1 (the existing preflight in `scripts/asi1_launch_rl_distill_27b_2npu.sh`
  already checks this).
- The benchmark file at
  `evals/benchmarks/quantum_grpo_training_v2_disjoint.txt` (override
  with `BENCHMARK_FILE=...`).

## Quick start

```bash
# On ASI1:
cd /root/work/quantum-gpt

# Dry-run to inspect the config without launching:
bash research/papers/doubly_robust_quantum_grpo/code/asi1_dr_grpo_2npu.sh dry-run

# Launch (writes to outputs/dr-grpo-27b-<timestamp>/):
bash research/papers/doubly_robust_quantum_grpo/code/asi1_dr_grpo_2npu.sh

# Check status:
bash research/papers/doubly_robust_quantum_grpo/code/asi1_dr_grpo_2npu.sh status

# Stop:
bash research/papers/doubly_robust_quantum_grpo/code/asi1_dr_grpo_2npu.sh stop
```

## What the launcher does

1. Preflight: verifies the model dir, benchmark file, trainer, and
   plugin files all exist.
2. Writes `run_config.json` to the output directory with the full DR
   hyperparameter block.
3. Launches `torchrun --nproc_per_node=2 training/grpo_trainer.py`
   with `--research-methods doubly_robust_quantum_grpo` and the
   standard 27B GRPO flags.
4. Pipes trainer stdout/stderr to `logs/trainer.log`.
5. Records the trainer PID in `trainer.pid` for the `status` and
   `stop` subcommands.

The launcher does NOT start a vLLM server. The GRPO trainer loads the
model directly with LoRA, which is the same shape as the existing
`scripts/asi1_launch_rl_distill_27b_2npu.sh` trainer burst.

## Hyperparameters

All hyperparameters are environment variables with sensible defaults
mirroring the existing 27B GRPO config. The DR-specific ones are:

| Variable | Default | Meaning |
| :--- | :--- | :--- |
| `DR_DPO_BETA` | 0.07 | DPO inverse temperature (matches `configs/dpo/qwen36_35b_a3b_dpo_v1.json`) |
| `DR_PAIR_LOSS_WEIGHT` | 0.3 | Weight on the DPO pair loss added to the PPO loss |
| `DR_PAIR_MIN_REWARD_GAP` | 0.4 | Minimum within-group reward gap to mine a pair |
| `DR_PAIR_MAX_PER_STEP` | 1 | Max pairs per group per step (keeps the extra backward cost predictable) |
| `DR_PSI_INIT` | 0.5 | Initial DR variance-correction coefficient (tune after step 50) |
| `RESEARCH_METHODS` | `doubly_robust_quantum_grpo` | Comma- or space-separated list of research methods to enable |

The standard GRPO hyperparameters (`GRPO_STEPS`, `GROUP_SIZE`,
`MAX_NEW_TOKENS`, `MAX_SEQ_LENGTH`, `LEARNING_RATE`, `LORA_RANK`,
`LORA_ALPHA`, etc.) all have the same defaults as the existing 27B
GRPO launcher.

## Monitoring

```bash
# Status subcommand (PID + log tail):
bash research/papers/doubly_robust_quantum_grpo/code/asi1_dr_grpo_2npu.sh status

# Tail the trainer log directly:
tail -f outputs/dr-grpo-27b-*/logs/trainer.log

# Watch the per-step metrics JSONL:
tail -f outputs/dr-grpo-27b-*/grpo_step_metrics.jsonl | python3 -m json.tool
```

The per-step record will include the existing fields (`mean_reward`,
`reward_std`, `signal_std`, `pass_rate`, etc.) plus, when the plugin
is active, the DR pair-loss fields written by the trainer. If you do
not see `dr_pair_loss` in the JSONL, the plugin's reward-shaping ran
but the trainer did not invoke the pairwise backward — check that
`--research-methods doubly_robust_quantum_grpo` is in the trainer
command in `logs/trainer.log`.

## A/B against base GRPO

The whole point of this paper is to compare DR-GRPO against base
GRPO on the same workload. Run them with the same seed, benchmark,
and step budget:

```bash
# Base GRPO (no DR plugin):
RESEARCH_METHODS="" \
  bash research/papers/doubly_robust_quantum_grpo/code/asi1_dr_grpo_2npu.sh

# DR-GRPO:
bash research/papers/doubly_robust_quantum_grpo/code/asi1_dr_grpo_2npu.sh
```

Then compare the per-step JSONL:

```bash
python3 - <<'PY'
import json
from pathlib import Path

base = Path("outputs/<base-run>/grpo_step_metrics.jsonl")
dr = Path("outputs/<dr-run>/grpo_step_metrics.jsonl")

def stats(p):
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    n = len(rows)
    skipped = sum(1 for r in rows if r.get("skipped"))
    updated = [r for r in rows if not r.get("skipped")]
    mean_r = sum(r.get("mean_reward", 0) for r in updated) / max(1, len(updated))
    return {"steps": n, "skipped": skipped, "skip_rate": skipped / max(1, n),
            "mean_reward_updated": mean_r}

print("base:", stats(base))
print("dr:  ", stats(dr))
PY
```

The success criterion from the paper is: the DR run reaches the same
pass@1 as the base run in <= 60% of the wall-clock steps. The
fast-abandon rules are:

1. DR pair loss is consistently NaN or > 10x the PPO loss after step 10.
2. Skip rate does not drop by at least 25% relative to base GRPO in a
   50-step window.
3. DR pass@1 is below base by more than 5 percentage points after
   step 100.

If any of these fire, stop the run, disable the plugin
(`RESEARCH_METHODS=""`), and continue with base GRPO.

## Troubleshooting

### `FATAL: missing plugin` or `FATAL: missing dr_pair_loss`

The launcher preflight checks for
`research/papers/doubly_robust_quantum_grpo/code/plugin.py` and
`dr_pair_loss.py`. If they are missing, the repo is not fully synced
to ASI1. Re-sync with the existing rclone/S3 pipeline.

### `dr_pair_loss` is always 0

This means `build_dr_pairs` is returning an empty list every step.
Check:

- The group reward spread is not zero (look for `reward_std > 0` in
  the JSONL).
- The reward gap exceeds `DR_PAIR_MIN_REWARD_GAP` (default 0.4). If
  the group rewards are all in `[0.0, 0.2]`, no pair will be mined;
  lower the threshold to `0.1` and re-run.
- The chosen and rejected codes are not identical. If the student is
  producing near-duplicate completions, increase `--max-new-tokens`
  or the sampling temperature.

### NaN in the DR pair loss

The DPO loss `softplus(-beta * (s_chosen - s_rejected))` can NaN if
the implicit reward gap is huge. Mitigations:

- Lower `DR_DPO_BETA` from 0.07 to 0.03.
- Lower `DR_PAIR_LOSS_WEIGHT` from 0.3 to 0.1.
- Add `--logit-clip 30.0` to the trainer command (already the
  default in some launchers; check `logs/trainer.log` for the actual
  value used).

### Out-of-memory on 2 NPUs

The DR pair loss adds one extra backward per step. If the 27B model
OOMs with the DR plugin enabled:

- Reduce `MAX_SEQ_LENGTH` from 2048 to 1536.
- Reduce `GROUP_SIZE` from 4 to 2 (this also reduces the chance of
  pair mining, so prefer reducing sequence length first).
- Ensure `--gradient-checkpointing` is in the trainer command (it is
  in the launcher).

## Files

- `plugin.py` — research-method plugin (loaded by
  `training/research_plugins.py`).
- `dr_pair_loss.py` — pairwise DPO loss helper.
- `asi1_dr_grpo_2npu.sh` — ASI1 2-NPU launcher.
- `README.md` — this file.
- `../paper.md` — the research note.

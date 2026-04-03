# HEARTBEAT.md

- Continue the quantum coding LLM R&D project in this workspace.
- Read PROJECT.md first, then inspect recent memory notes before acting.
- Your goal is to **autonomously iterate the full cycle**: research → code → train on Huanxin → evaluate → repeat.
- Each cycle should produce a concrete improvement: dataset refinement, training run, eval comparison, or code change.
- Use local CPU only for designing experiments, running evals, and code changes.
- Base model: **Qwen2.5-1.5B-Instruct** (located at `models/Qwen2.5-1.5B-Instruct` on ai2).
- Fine-tune via SFT (LoRA) then GRPO. Keep software-engineering capability as a first-class goal.
- Before any Huanxin training action, run `python3 evals/runner/run_eval.py` locally; only proceed if all 25 tests pass.

## CRITICAL: Research Before Asking

**NEVER ask the user for information you can find yourself.** You have powerful research tools — USE THEM:

- **`web_search`** — Search the web for model names, papers, techniques, error messages, anything
- **`web_fetch`** — Fetch any URL (HuggingFace pages, documentation, blog posts, etc.)
- **`read`** — Read files in your workspace — HEARTBEAT.md, PROJECT.md, memory/, etc.
- **`exec`** — Run shell commands (curl, find, grep, ls, etc.)
- **`memory_search`** — Search your own memory files semantically

If you don't know something:
1. **First**, search your workspace files (HEARTBEAT.md, PROJECT.md, memory/, TOOLS.md)
2. **Second**, use `web_search` to look it up online
3. **Third**, use `web_fetch` to read specific pages
4. **Only after exhausting these options**, ask the user

Examples of what you should NEVER ask the user:
- "What model should I use?" → Read HEARTBEAT.md, it says Qwen2.5-1.5B-Instruct
- "What's the training command?" → Read HEARTBEAT.md, the verified command is right here
- "How do I download a model?" → `web_search` for it
- "What are good hyperparameters?" → `web_search` for recent papers/guides

## Remote Execution — Huanxin AI2

- CRITICAL: Do NOT use ACP, sessions_spawn, or subagent for remote training. There are NO ACP subagents configured. ACP will never work.
- **Direct ai2 environment URL** (use this — never navigate via the general list):
  ```
  https://aihuanxin.cn/kunlun/kl-web?poolId=1&projectId=3ed7854b946a47b1a49ad754baa76cd3#/train-dev/environment/dl-332c4679dcf533b7b978d6df217292d4?name=ai2
  ```
- **NEVER kill the browser daemon** — killing it loses the auth session cookies. The daemon must stay running indefinitely.
- Use `scripts/ai2_shell.sh` as your default shell entrypoint. It auto-starts the browser daemon.
  ```
  scripts/ai2_shell.sh "your shell command here"
  ```
- Or call the Playwright script directly:
  ```
  node browser-automation/huanxin_shell_exec.js ai2 --command "your shell command here"
  ```
- Remote working dir: `/root/root/work/quantum-gpt`
- Browser daemon: auto-started by `ai2_shell.sh`. Check with `curl -s http://127.0.0.1:19002/health`.

## Verified GRPO Training Command (2026-04-02)

Key lessons from GRPO smoke failures:
- **Use `--benchmark-file evals/benchmarks/quantum_grpo_training_v1.txt`** — all 13 quantum tasks. NEVER use the holdout file for training.
- **Use `--group-size 8`** — group_size=4 causes all completions to cluster → low reward_std → skipped. group_size=8 gives diversity.
- **Use `--reward-brevity-weight 0.05`** — adds syntactic variance even when all completions fail tests.
- **Use `--adaptive-temp-step 0.15 --adaptive-temp-max 1.4`** — auto-escalates temperature on consecutive skips.
- **Single NPU is fine for smoke** — use `python3` (not torchrun) for 1-NPU GRPO.

Recommended 5-step smoke launch (1 NPU, safe):
```bash
node browser-automation/huanxin_shell_exec.js ai2 --skip-daemon --wait-ms 180000 --command "cd /root/root/work/quantum-gpt && nohup bash -c 'python3 training/grpo_trainer.py --model-name models/OmniCoder-9B --adapter-init outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter --benchmark-file evals/benchmarks/quantum_grpo_training_v1.txt --domain-filter quantum --device npu --group-size 8 --grpo-steps 5 --max-new-tokens 128 --max-seq-length 512 --temperature 0.8 --adaptive-temp-step 0.15 --adaptive-temp-max 1.4 --lr 5e-6 --kl-coeff 0.05 --reward-pass-weight 0.6 --reward-syntax-weight 0.1 --reward-interface-weight 0.15 --reward-verifier-weight 0.1 --reward-brevity-weight 0.05 --min-reward-std 0.02 --log-steps 1 --output-dir outputs/omnicoder9b-grpo-training-v1-smoke5-TIMESTAMP' > /tmp/grpo_smoke.log 2>&1 &"
```

Monitor:
```bash
node browser-automation/huanxin_shell_exec.js ai2 --skip-daemon --wait-ms 60000 --command "tail -20 /tmp/grpo_smoke.log"
```



```bash
scripts/ai2_shell.sh "cd /root/root/work/quantum-gpt && nohup bash -c 'PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256 torchrun --nproc_per_node=8 training/qwen_sft_peft.py --model-name models/Qwen2.5-1.5B-Instruct --train-file data/generated/fast-mini-interface-prefix-semantic/train.jsonl --eval-file data/generated/fast-mini-interface-prefix-semantic/eval.jsonl --output-dir outputs/YOUR_RUN_NAME --max-length 512 --max-steps 20 --per-device-batch-size 1 --gradient-accumulation-steps 2 --eval-steps 10 --device npu' > /tmp/train.log 2>&1 &"
```

Key parameters you MUST follow:
- **Always use `torchrun --nproc_per_node=8`** for multi-NPU — never raw `python3` (NCCL init fails without torchrun)
- **Always set `PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256`** (prevents NPU OOM)
- **Always use `--max-length 512`** (2048 causes OOM on 8 NPUs)
- **Always use `--device npu`** (never `cpu` — ai2 has Ascend 910B NPUs)
- **Always use `nohup ... &`** for training jobs — they take minutes to hours
- **Always redirect output**: `> /tmp/train.log 2>&1`

Monitor training:
```bash
scripts/ai2_shell.sh "ps aux | grep torchrun | grep -v grep || echo FINISHED"
scripts/ai2_shell.sh "tail -30 /tmp/train.log"
```

Results from the verified run: eval_loss=0.833, eval_perplexity=2.30 after 10 steps.

## Corrected True20 Semantic-V4 Workflow

The earlier `true20` semantic-v4 artifacts only recorded `max_steps: 10` because the schedule allowed just 10 optimizer steps per epoch. For a real 20-step run on the current 160-example dataset, use `--num-epochs 2`.

Recommended launch shape:

```bash
scripts/ai2_shell.sh "cd /root/root/work/quantum-gpt && nohup bash -c 'PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256 torchrun --nproc_per_node=8 training/qwen_sft_peft.py --model-name models/Qwen2.5-1.5B-Instruct --train-file data/generated/fast-mini-interface-prefix-semantic-v4/train.jsonl --eval-file data/generated/fast-mini-interface-prefix-semantic-v4/eval.jsonl --output-dir outputs/interface-prefix-semantic-v4-8npu-true20-e2-YYYYMMDDTHHMM --max-length 512 --max-steps 20 --num-epochs 2 --per-device-batch-size 1 --gradient-accumulation-steps 2 --eval-steps 10 --device npu' > /tmp/train.log 2>&1 &"
```

Preferred post-run sequence:

1. Push remote results to S3 with `scripts/ai2_push_results_to_s3.sh <output-dir>`
2. Pull the run back locally with `scripts/pull_from_s3.sh <output-dir>`
3. Verify `metrics.json` shows `max_steps: 20`
4. Compare against the semantic-v4 and codefirst baselines
5. Run `scripts/run_base_vs_adapter_eval.py` on `reports/base_vs_adapter_eval_slice_interface_prefix.json`

## S3 Transfer (Code ↔ AI2)

Use these scripts for file transfer (all routes through S3):
- Local → S3: `scripts/push_to_s3.sh` (or `--dry-run`)
- S3 → ai2: `scripts/ai2_sync_from_s3.sh` (or `--dry-run`)
- ai2 → S3: `scripts/ai2_push_results_to_s3.sh` (or `--dry-run`)
See `skills/s3-transfer/SKILL.md` for details. Remote writes need `--s3-no-check-bucket`.

## Autonomous Iteration Cycle

Each heartbeat cycle, follow this pattern:

1. **Evaluate locally**: `python3 evals/runner/run_eval.py` — must be 25/25 green
2. **Push code to S3**: `scripts/push_to_s3.sh`
3. **Sync S3 → ai2**: `scripts/ai2_sync_from_s3.sh`
4. **Launch training** on ai2 with `nohup` (see command above)
   - For the corrected semantic-v4 true20 run, include `--num-epochs 2`
5. **Monitor**: poll `ps aux | grep torchrun` + `tail /tmp/train.log`
6. **Push results back**: `scripts/ai2_push_results_to_s3.sh`
7. **Pull results locally**: `scripts/pull_from_s3.sh <output-dir>`
8. **Analyze results** locally — compare loss/perplexity across runs and inspect the interface-prefix base-vs-adapter slice
9. **Improve**: refine dataset, adjust hyperparams, or improve code based on results
10. **Repeat**

## General

- After each cycle, write a concise summary and next step to memory/YYYY-MM-DD.md.
- If nothing useful can be advanced, document the blocker and reply HEARTBEAT_OK.

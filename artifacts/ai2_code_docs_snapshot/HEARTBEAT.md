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

## Verified Training Command (PROVEN WORKING)

The following command completed successfully on 8 NPUs on 2026-03-22:

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
5. **Monitor**: poll `ps aux | grep torchrun` + `tail /tmp/train.log`
6. **Push results back**: `scripts/ai2_push_results_to_s3.sh`
7. **Analyze results** locally — compare loss/perplexity across runs
8. **Improve**: refine dataset, adjust hyperparams, or improve code based on results
9. **Repeat**

## General

- After each cycle, write a concise summary and next step to memory/YYYY-MM-DD.md.
- If nothing useful can be advanced, document the blocker and reply HEARTBEAT_OK.

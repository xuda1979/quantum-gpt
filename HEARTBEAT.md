# HEARTBEAT.md

- Continue the quantum coding LLM R&D project in this workspace.
- Read PROJECT.md first, then inspect recent memory notes before acting.
- Your goal is to **autonomously iterate the full cycle**: research → code → train on Huanxin → evaluate → repeat.
- Current phase priority (2026-06-30): train model code ability first. Keep quantum code generation, API correctness, software engineering, tests, RAG-assisted repair, and executable pass@1 as the active training target.
- Future phase: after code ability stabilizes, build the 1000-classic-paper quantum science corpus, generate progressive paper-grounded QA/code/research-direction data, run distillation SFT, then mixed distillation + RL. See `docs/two-stage-training-roadmap-2026-06-30.md`.
- Each cycle should produce a concrete improvement: dataset refinement, training run, eval comparison, or code change.
- Use local CPU only for designing experiments, running evals, and code changes.
- Base model for new training: **Qwen/Qwen3.6-27B** at `models/Qwen3.6-27B` under Huanxin `AI`.
- Fine-tune via SFT (LoRA) then GRPO/RL in Huanxin `AI`. Keep software-engineering capability as a first-class goal.
- Before any Huanxin training action, run `python3 evals/runner/run_eval.py` locally; only proceed if the full current task suite passes.
- If `.huanxin_manual_mode` exists, do not run Huanxin browser automation, shell wrappers, Safari keepalive, profile repair, or Huanxin browser probes. Treat Huanxin automation as intentionally paused for human manual webshell use.
- Huanxin automation is disabled by default. `scripts/huanxin_manual_mode.sh --manual-off` / `--disable` only removes the manual lock; it does not create `.huanxin_automation_enabled`. Only use `scripts/huanxin_manual_mode.sh --enable-automation` after the human explicitly asks Codex to control Huanxin again.

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

## Remote Execution — Huanxin AI

- CRITICAL: Do NOT use ACP, sessions_spawn, or subagent for remote training. There are NO ACP subagents configured. ACP will never work.
- **Train-dev route**:
  ```
  https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=21b4208dde424e96b159362ef49c9c96#/train-dev/environment/dl-9a5a098accce31c28cf4c6ca23391341?name=AI
  ```
- From 2026-04-26 onward, **all new training, fine-tuning, SFT, GRPO, PPO, DPO, and other RL work must use Huanxin `AI`**, not ai1 or ai2.
- Keep ai1/ai2 notes only for historical migration/debugging. Do not launch new training there unless the user explicitly overrides this rule.
- Do not kill the browser daemon during normal autonomous work because that may lose auth cookies. This rule is overridden by manual webshell protection: if the human reports refreshes, lost input, or `.huanxin_manual_mode` exists, stop local Huanxin automation instead of preserving daemon state.
- Use the Huanxin environment regularly only when automation is explicitly enabled. Do not keepalive, probe, or refresh Huanxin while manual mode is active.
- Treat the Safari `#/train-dev` session and the browser-automation profile as two separate states. Do not confuse “Safari is still logged in” with “Playwright/daemon auth is still valid.”
- For a no-new-page keepalive on the already-open Safari Huanxin tab, use:
  `bash scripts/huanxin_safari_keepalive.sh --refresh`
- That helper only reuses the existing Safari `#/train-dev` tab; it does not create a new browser page.
- For automatic periodic refresh, run:
  `bash scripts/install_huanxin_safari_keepalive_agent.sh --install`
- Check the installed keepalive agent with:
  `bash scripts/install_huanxin_safari_keepalive_agent.sh --status`
- For one-command diagnosis of keepalive vs automation-profile state, use:
  `bash scripts/huanxin_status.sh`
- The manual fallback loop still exists:
  `bash scripts/huanxin_safari_keepalive_loop.sh`
- Use `scripts/huanxin_shell.sh AI "<cmd>"` as the generic shell entrypoint.
- Convenience wrapper: `scripts/ai_shell.sh "<cmd>"`.
- Treat the daemon-backed shell path as mandatory by default. Do not silently fall back to standalone browser launches because that churns session state and reintroduces login problems.
- Only allow standalone shell fallback for explicit recovery/debugging by setting `HUANXIN_ALLOW_STANDALONE_FALLBACK=1`.
  ```
  scripts/huanxin_shell.sh AI "your shell command here"
  scripts/ai_shell.sh "your shell command here"
  ```
- Or call the Playwright script directly:
  ```
  node browser-automation/huanxin_shell_exec.js ai1 --command "your shell command here"
  node browser-automation/huanxin_shell_exec.js ai2 --command "your shell command here"
  ```
- Remote working dir: `/root/software/quantum-gpt`
- Browser daemon port for AI shell control is managed by the wrapper; verify with `bash scripts/huanxin_status.sh`.

## Current AI Session State (2026-04-28)

- `scripts/ai_shell.sh` verified canonical `AI` shell access and remote root `/root/software/quantum-gpt`.
- Remote project files, trainer, and strict quantum train/eval JSONL are present.
- Current training blocker: `models/Qwen3.6-27B/config.json` is missing in AI.
- Safari keepalive LaunchAgent install attempted but `launchctl bootstrap` failed with `Bootstrap failed: 5: Input/output error`; do not assume automatic keepalive is loaded.
- Before any remote training action, run a fresh short probe:
  `HUANXIN_WAIT_MS=120000 bash scripts/ai_shell.sh "cd /root/software/quantum-gpt && pwd && test -f training/qwen_sft_peft.py && test -f models/Qwen3.6-27B/config.json"`

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

## S3 Transfer (Code ↔ AI)

Use these scripts for file transfer (all routes through S3):
- Local → S3: `scripts/push_to_s3.sh` or `scripts/upload_quantum_gpt_to_iner_s3.sh` (use `--dry-run` first for broad uploads)
- S3 → AI: `scripts/ai_sync_from_s3.sh` (or `--dry-run`)
- AI → S3: `scripts/ai_push_results_to_s3.sh` (or `--dry-run`)
- S3 → local: `scripts/pull_from_s3.sh`
- Active S3 relay for the current workflow: `iner:jtdlp-21b4208dde424e96b159362ef49c9c96/software/quantum-gpt`
See `skills/iner-s3-transfer/SKILL.md` and `TOOLS.md` for details. Remote writes need `--s3-no-check-bucket`.

## Autonomous Iteration Cycle

Each heartbeat cycle, follow this pattern:

1. **Evaluate locally**: `python3 evals/runner/run_eval.py` — must be green on the full current suite
2. **Push code to S3**: `scripts/push_to_s3.sh`
3. **Sync S3 → AI**: `scripts/ai_sync_from_s3.sh`
4. **Launch training** on `AI` with the current verified `AI` command path
5. **Monitor**: use the current `AI` shell / job helpers and log tails for the launched run
6. **Push results back**: `scripts/ai_push_results_to_s3.sh`
7. **Pull results locally**: `scripts/pull_from_s3.sh <output-dir>`
8. **Analyze results** locally — compare loss/perplexity across runs and inspect the interface-prefix base-vs-adapter slice
9. **Improve**: refine dataset, adjust hyperparams, or improve code based on results
10. **Repeat**

## General

- After each cycle, write a concise summary and next step to memory/YYYY-MM-DD.md.
- If nothing useful can be advanced, document the blocker and reply HEARTBEAT_OK.

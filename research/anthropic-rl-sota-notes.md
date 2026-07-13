# SOTA RL for Agentic Coding — Anthropic-Style Reference Notes

Compiled 2026-05-12 to guide the Qwen3.6-35B-A3B agentic-coding RL run on Huanxin `ai3`.
These notes summarize *publicly disclosed* techniques used by Anthropic and the broader
SOTA RL-for-code community. We translate each into a concrete recipe we can run locally.

## 1. The Anthropic RL stack at a glance

| Layer | Anthropic technique | Public source | Our analogue |
| --- | --- | --- | --- |
| Pretraining | dense + MoE LM | Claude system cards | Qwen3.6-35B-A3B (MoE, 35B total / ≈3B active) |
| Behaviour cloning | SFT on curated human + AI demonstrations | "Training a helpful and harmless assistant" (Bai et al. 2022, NeurIPS); Claude 3 model card | `training/qwen_sft_peft.py` |
| Preference modeling | RLHF with a human-pref reward model | "Training a helpful and harmless assistant" (Bai et al. 2022) | optional (skipped at first; we use verifiable rewards) |
| **AI-feedback layer** | **Constitutional AI / RLAIF** — written principles drive an AI critic that labels preferences | "Constitutional AI: Harmlessness from AI Feedback" (Bai et al. 2022, arXiv:2212.08073) | Add a *Constitutional code-quality critic* (Qwen3.6-27B-RAG) that scores style/safety per trajectory |
| **Verifiable-reward RL** | **RLVR** — execute outputs in a sandbox, reward = pass/fail of hidden tests; explicitly called out for code, math, browser/computer use | "Claude 3.5 Sonnet" + "Computer Use" announcements (Oct 2024); "Claude 3.7 Sonnet" model card (Feb 2025) | `evals/tasks/**/tests.py` already executes candidate code; we wire this as the primary reward |
| **Agent-trajectory RL** | **YES — Anthropic trains on agent trajectories.** Multi-turn rollouts in a sandbox (read/write files, run shell, run tests, browse), with **outcome reward at the end of the trajectory** and *trajectory-level advantage broadcast to every action token*. Computer-use, SWE-bench-Verified, and Claude Code lines all use this. | Anthropic blog "Introducing computer use" (Oct 2024); Claude 3.7 model card §"Agentic training"; "Building Claude Code" engineering posts | New `training/agent_trajectory_rollout.py` + `training/agentic_grpo_trainer.py` |
| Process/step rewards | Process Reward Models (PRMs) trained on per-step correctness labels | "Let's Verify Step by Step" (Lightman et al. 2023, OpenAI); Anthropic interpretability blog refs | Optional second pass; we start with outcome reward only |
| Rejection sampling & expert iteration | Best-of-N sample → keep passes → SFT → repeat | Touvron et al. 2023 (Llama 2 RLHF); referenced in Claude 3 system card | `scripts/expert_iteration_loop.sh` (we add this) |
| Policy optimizer | PPO with KL-to-reference penalty; **group-relative variants (GRPO/RLOO) now standard for code** | DeepSeek-R1 (2025) GRPO paper; Anthropic does not publish the exact optimizer but their public engineering posts describe "on-policy actor with KL regularization" | We use **GRPO** (already in `training/grpo_trainer.py`) and lift it to trajectory-level |
| Reward hacking defenses | "Reward hacking is the primary failure mode of agent RL." Anthropic uses red-team graders, hidden test splits, and adversarial reward audits. | "Sleeper Agents" + "Sycophancy" + "Auditing Hidden Objectives" (2024–2025) | Hidden eval split + dual-grader (test executor + Constitutional critic) + monitor for reward/eval divergence |
| **Long-running harness** | **Agent harness engineering** for long tasks: resumable state, explicit checkpoints, narrow tools, long-horizon watchdogs, and "make progress legible while the run is live." | Anthropic engineering posts "Effective harnesses for long-running agents" and "Effective context engineering for AI agents" (2025) | `live_status.json`, `latest_checkpoint.json`, `checkpoint_history.jsonl`, `online_eval_latest.json`, `scripts/show_agentic_grpo_status.py`, `scripts/watch_ai3_checkpoints_to_s3.sh` |
| Safety RL | RLHF/RLAIF with harmlessness constitution, plus refusal classifiers | "Constitutional AI" + Claude usage policy | Out of scope for v0 of this run; we focus on capability |

### Direct answer to the user's question

> **Does Anthropic use agent trajectories to train the model?**
> **Yes.** Anthropic's public communications around Claude 3.5/3.7 Sonnet (computer use) and Claude
> Code state that the model is trained on **multi-turn agent trajectories** inside sandboxed
> environments, with outcome-verifiable rewards (did the task ultimately succeed?) propagated
> back through the trajectory. We replicate that recipe here.

## 2. Why this matters for `agentic_coding`

For a coding agent we have *gold-standard verifiable rewards* essentially for free:

1. The task has tests. Run them. Pass = +1, fail = 0. No human labelers required.
2. The agent must be allowed to *interact with a real workspace* (read files, write patches, run
   tests, read tracebacks, retry) for the reward to be meaningful — that's why trajectory-level RL
   beats single-shot completion RL on SWE-bench and Claude Code.
3. Auxiliary shaping rewards (syntax, interface, brevity, import hygiene) only fire when the
   outcome reward is informative; they break flat-reward plateaus but cannot replace the
   pass/fail signal.

## 3. Concrete recipe we will run on Huanxin `ai3`

**Base model:** `models/Qwen3.6-35B-A3B` (HF/safetensors — must be present on `ai3` before we
launch; if only the GGUF mirror exists we downgrade to `models/Qwen3.6-27B` and emit a precise
blocker).

**Phase 0 — SFT bootstrap (optional, fast).** A single epoch of SFT on
`data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl` with LoRA, so the policy
has a good starting point for trajectory rollouts. Reuses `training/qwen_sft_peft.py`.

**Phase 1 — Agent trajectory RL (the main run).**

- *Environment:* an in-process Python sandbox that exposes four tools to the model:
  `read_file`, `write_file`, `run_python`, `run_tests`. Each tool emits an observation
  appended to the trajectory.
- *Task pool:* `evals/tasks/**` (both `software/` and `quantum/`), filtered by an explicit
  benchmark file so we can swap curricula.
- *Rollout:* for every prompt we sample `group_size=8` independent trajectories, each up to
  `max_turns=8` tool calls. Each trajectory is a sequence of (assistant tool-call,
  environment observation) pairs ending with a `final_answer` or a turn-budget exhaustion.
- *Outcome reward:* run `tests.py` against the final candidate. Pass = `+1`, fail = `0`. Plus the
  existing shaped rewards from `training/grpo_utils.py` (syntax, interface, verifier, brevity,
  import hygiene) on the *final* candidate, with a configurable weight vector that defaults to
  pass-dominant.
- *Optional Constitutional critic:* the existing `quantum-intelligence-v0.1.0` RAG endpoint (or
  any local OpenAI-compatible model) can grade the trajectory against a written constitution
  ("did the agent test before claiming done? did it read the failing test before patching?
  did it avoid speculative imports?"). The critic score is added with a small weight and
  *clipped* so it cannot dominate the verifiable reward.
- *Advantage:* trajectory-level GRPO. We compute the group-relative advantage of each whole
  trajectory and broadcast it to every assistant token in that trajectory. KL-to-reference
  penalty is applied per token as in standard PPO.
- *Optimizer:* the existing stable GRPO loss in `training/grpo_utils.stable_grpo_loss` — already
  hardened with ratio clipping and logit clipping for NPU stability.
- *Checkpointing:* every `--save-steps` GRPO steps we save adapter + tokenizer to
  `outputs/<run>/checkpoints/step-<n>/` and trigger an async S3 push.
- *Evaluation:* every `--eval-steps` we run `evals/runner/run_eval.py` on a held-out slice and
  log pass-rate divergence between train and eval as our reward-hacking canary.

**Phase 2 (later) — rejection-sampling expert iteration.** Once Phase 1 plateaus, take the best
N passing trajectories per task, append them to SFT data, retrain a fresh policy from the same
base, and repeat. This is the same loop Llama-2-Chat and Claude 3 are reported to use.

## 4. Risks and mitigations

- **Reward hacking on the test file.** The agent must not be able to read `tests.py`. Our
  sandbox restricts `read_file` to a per-task allowlist (the candidate file + any explicit
  inputs declared in `task.json`). Held-out eval split detects regressions.
- **Training goes "dark" between checkpoints.** Anthropic's recent agent-engineering guidance
  emphasizes that long runs need *live legibility*, not just end-of-run logs. We therefore
  write:
  - `live_status.json` for recent reward / loss / skip / termination summaries
  - `online_eval_latest.json` plus `online_eval_history.jsonl` for held-out audit slices
  - `checkpoint_history.jsonl` and `latest_checkpoint.json` for resumable state
  - local wrappers to read/push them during a live Huanxin run
- **MoE expert collapse / router drift.** Existing GRPO trainer already supports
  `--target-module-regex` for router-only LoRA. We start with attention-only LoRA on the
  Qwen3.6-35B-A3B and keep MoE routers frozen.
- **NPU memory pressure on a 35B MoE.** Default `tensor_parallel_size=8`, `max_seq_length=4096`,
  per-device batch size 1, gradient accumulation 8, LoRA rank 8. Activations checkpointing on.
- **Long trajectories blowing the sequence budget.** Tool observations are truncated to
  `--max-observation-tokens` (default 512) and old turns are summarized when the prompt grows
  past `--max-seq-length * 0.75`.
- **Browser/auth dependence on Huanxin.** Documented in `TOOLS.md`; the launcher checks
  `scripts/huanxin_shell.sh ai3 "echo ok"` first and refuses to start training otherwise.

## 5. References

- Bai et al. 2022. "Constitutional AI: Harmlessness from AI Feedback". arXiv:2212.08073.
- Bai et al. 2022. "Training a Helpful and Harmless Assistant with Reinforcement Learning from
  Human Feedback". arXiv:2204.05862.
- Anthropic 2024. "Introducing computer use". https://www.anthropic.com/news/3-5-models-and-computer-use.
- Anthropic 2025. "Claude 3.7 Sonnet system card".
- Anthropic 2025. "Effective harnesses for long-running agents".
- Anthropic 2025. "Effective context engineering for AI agents".
- Lightman et al. 2023. "Let's Verify Step by Step". arXiv:2305.20050.
- DeepSeek-AI 2025. "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement
  Learning". arXiv:2501.12948. (GRPO algorithm formalization.)
- Touvron et al. 2023. "Llama 2: Open Foundation and Fine-Tuned Chat Models". arXiv:2307.09288.
  (Rejection-sampling expert iteration.)
- Cobbe et al. 2021. "Training Verifiers to Solve Math Word Problems". arXiv:2110.14168.

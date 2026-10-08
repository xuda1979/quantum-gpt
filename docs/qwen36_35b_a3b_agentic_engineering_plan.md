# Qwen3.6 35B A3B Agentic Engineering Plan

This is the repo-local execution plan for turning `Qwen/Qwen3.6-35B-A3B` into a stronger agentic model for quantum coding and general software engineering.

The plan is intentionally practical and sized for the current cluster: 24 Ascend 910C NPUs.

The plan is intentionally practical:

- keep the training target explicit
- define a data pipeline that can be verified locally
- use objective evals before any remote training
- treat Huanxin `AI` as the execution target only after local checks pass

## Target Split

- Model target: reasoning, patch generation, tests, tool use, long-horizon repo navigation, and resistance to malicious repo text
- Agent-system target: evaluate the same trained model under one thin scaffold with fixed tools, retry policy, time budget, hidden tests, and review gates

## Architecture

The intended runtime stays monolithic: one main Qwen policy model with controlled tools. Specialist agents are only for offline data generation, review, red teaming, and labeling.

Hardware assumption:

- available compute: 24 Ascend 910C NPUs
- default placement: treat the cluster as a 24-way budget for SFT/GRPO launches, then pick the smallest tensor/pipeline/data parallel split that fits the run
- avoid architecture claims that depend on a larger rack count than this budget actually supports

Required runtime components:

- tool API: `search_repo`, `read_file`, exact-string replacement, `create_file`, `bash`, test commands, `git diff`, docs lookup, and compact memory updates
- sandbox: per-task isolated repo clone with CPU, RAM, time, and network limits
- verifier: public tests, hidden tests, lint/type checks, build checks, and property tests where hidden tests are unavailable
- memory condenser: session summaries and repository maps
- reviewer: optional reward shaping and risk review, never the sole oracle

## Data Factory

Five data classes are mandatory:

1. General coding SFT data: bug fixes, feature work, refactors, test writing, code review, CI/debug logs, browser tasks, and DevOps repairs
2. Agent trajectories: multi-turn tool-use traces that inspect before editing, patch minimally, run tests, diagnose failure logs, and summarize validation
3. Preference pairs: chosen trajectories pass objective verifiers and preserve maintainability; rejected trajectories skip tests, rewrite broadly, hardcode, leak secrets, or break APIs
4. Synthetic repo tasks: bug injector plus issue/test generator with original-pass, mutated-fail, known-patch-pass proofs
5. Private gold benchmark: frozen by repo SHA, hidden from training, hidden from teacher generation, and scored with blind review

## Training Sequence

1. Baseline evaluation: raw chat, thin scaffold, long-context repo access, retrieval/tools, and closed-model comparisons only if terms allow
2. Clean SFT: LoRA/DoRA only, router frozen, 1 epoch, high-quality tool and coding data
3. Rejection-sampled SFT: keep only candidates that pass objective verifiers and maintain small, safe diffs
4. DPO/KTO/IPO: preference-align for minimality, test discipline, diagnosis, compatibility, security, and maintainability
5. RLVR: GRPO/DAPO over executable coding tasks with tests, compilers, lint, type checks, fuzz/property checks, browser checks, and security scanners
6. Agentic RL: train full tool trajectories, ambiguous edit rejection, retries from logs, and long-session summaries
7. Long-context curriculum: 8k/16k first, then 32k, 64k/128k, and only then 262k+ tasks that genuinely require it
8. Safety/adversarial RL: prompt injection, unsafe shell, secrets access, dependency risk, test cheating, and broad rewrite penalties

## Huanxin Preflight Reality Check

The current verified Huanxin target for new training work is `AI`, not `ai1` or `ai2`.

Before any launch:

- run local tests for the touched launcher/trainer paths
- verify the selected Huanxin environment shell/login path with an exact environment target
- sync repo code to the remote workdir expected by that environment
- verify dependencies and benchmark files on the selected environment
- run launcher `--dry-run` and inspect the rendered remote command

If `peft`, `accelerate`, `torch_npu`, repo code, or benchmark files are missing, record the exact failed command and stop instead of launching a partial run.

## 90-Day Milestones

- Days 1-7: baseline harness, selected-environment preflight, private benchmark v0, first 50-100 internal tasks
- Days 8-21: normalize issue/PR/CI data, build synthetic bug injector, hidden-test generator, 10k-50k executable tasks, 100k-500k SFT examples, 20k-100k preference pairs
- Days 22-35: LoRA SFT v1, eval every 1k-5k steps, stop on private regression
- Days 36-49: DPO/KTO over actual failures and preferred patch traits, build trajectory replay buffer
- Days 50-75: GRPO RLVR from 1k easy to 10k medium tasks, 4-8 rollouts per task, convert successful rollouts into replay data
- Days 76-90: larger agentic RL, long-context repo tasks, browser/frontend tasks, security tasks, full private benchmark, and model/safety report

## Success Standard

The target is not pretty code once. The target is four independent runs on the same task producing the same correct patch family, passing hidden tests, with no unsafe behavior and a clear validation report.

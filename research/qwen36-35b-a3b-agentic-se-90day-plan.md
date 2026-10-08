# Qwen3.6 35B A3B Agentic Software-Engineering 90-Day Plan

This is the durable research plan for adapting `Qwen/Qwen3.6-35B-A3B` into a strong agentic software-engineering and quantum-coding model. The operational runbook lives in `docs/qwen36_35b_a3b_agentic_engineering_plan.md`; this file tracks the research program.

## Operating Assumptions

- Current user-selected Huanxin target for this work is `ASI1`.
- ASI1's verified 35B A3B checkpoint path is `/root/work/filestorage/Qwen3.6-35B-A3B-W8A8`.
- Training must not silently substitute another model. If the requested model, repo, or dependencies are missing, emit a blocker.
- Local validation comes before S3 sync or Huanxin launch.
- Private holdout tasks remain excluded from SFT, preference data, rejection sampling, prompt tuning, teacher generation, and RL.

## Phase 1: Foundation, Days 1-14

Deliverables:

- ASI1 shell/sync/dependency preflight.
- Baseline eval harness for raw model, thin agent scaffold, long-context repo access, and retrieval/tool access.
- Private benchmark v0 with task-id-only manifests and hidden tests.
- First model/source contract for Qwen3.6 35B A3B.

Gates:

- Launcher dry-run renders the ASI1 model path.
- Existing agentic trainer tests pass locally.
- Benchmark training and holdout lists are disjoint.

## Phase 2: Data Engine, Days 15-30

Deliverables:

- Agentic trajectory schema and dataset builder.
- Synthetic bug injector and hidden-test generator.
- Preference-pair schema for chosen/rejected patch trajectories.
- 10k-50k executable tasks, then 100k-500k SFT examples if quality checks hold.

Gates:

- Original repo passes, mutated repo fails, known patch passes for generated tasks.
- Dataset manifests record task ids, prompt families, sources, licenses, and split policy.
- Holdout verifier reports zero overlap.

## Phase 3: Clean SFT, Days 31-45

Deliverables:

- LoRA/DoRA SFT v1 using `configs/sft/qwen36_35b_a3b_lora_sft_v1.json`.
- Evaluation every 1k-5k steps.
- Early-stop rule for private benchmark regression.

Gates:

- Tool format and final-answer format remain stable.
- Test-discipline metrics do not regress.
- No router updates until load-balance telemetry exists.

## Phase 4: Preference Optimization, Days 46-60

Deliverables:

- DPO/KTO/IPO path over objective verifier-backed preference pairs.
- Preference audit report covering minimality, compatibility, security, and test behavior.
- Trajectory replay buffer seeded from successful candidates.

Gates:

- Objective execution results dominate preference labels.
- Model-judge-only labels remain below the configured audit threshold.

## Phase 5: RLVR, Days 61-75

Deliverables:

- GRPO/DAPO RLVR using executable sandbox rewards.
- Reward hacking audit.
- Hindsight trajectory distillation from failed-then-successful runs.

Gates:

- Hidden tests and public tests dominate reward.
- Unsafe shell, secrets access, hardcoding, and broad rewrites are penalized.
- Checkpoints include live status, online eval, and resumable runtime state.

## Phase 6: Agentic RL And Release Candidate, Days 76-90

Deliverables:

- Multi-turn repo-edit agent training.
- Long-context curriculum only for tasks that require it.
- Browser/frontend and security-hardening tasks.
- Model card, safety report, private eval report, and deployment recommendation.

Gates:

- Four independent runs solve the same task with the same correct patch family.
- Human blind review approves risk analysis and validation reports.
- No autonomous merge without reliability gates.

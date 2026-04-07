# Quantum Coding LLM R&D Project

## Mission

Build an R&D program for a quantum-coding LLM that can write high-quality quantum algorithms and still retain strong general software-engineering ability.

## Model Direction

- Base model: **Qwen2.5-1.5B-Instruct** (on ai2 at `models/Qwen2.5-1.5B-Instruct`)
- Near-term orchestration model: yunwu/gpt-5.4
- Training hardware: 8x Ascend 910B NPUs on Huanxin AI2

## Current Objective

Use this workspace to incrementally research, design, and implement a CPU-first local development and validation pipeline for the target Qwen model, then move validated code into the Huanxin environment from the local machine and run remote fine-tuning there.

The work should stay realistic under current constraints:

- No GPU assumptions
- Favor small experiments, synthetic data generation, evaluation harnesses, and reproducible scripts
- Prefer narrow but working end-to-end prototypes over ambitious incomplete systems

## Remote Fine-Tuning Path

- Huanxin route: `https://aihuanxin.cn/kunlun/kl-web?poolId=1&projectId=3ed7854b946a47b1a49ad754baa76cd3#/train-dev`
- Intended remote workdir: `/root/root/work/quantum-gpt`
- Transfer mode: S3 staging via `./scripts/push_to_s3.sh`, `./scripts/ai2_sync_from_s3.sh`, `./scripts/ai2_push_results_to_s3.sh`
- Shell access: `./scripts/ai2_shell.sh "your command"`
- Local validation is mandatory before remote training:
	- run `python3 evals/runner/run_eval.py`
	- run any additional local tests for files you changed
	- do not push code or trigger remote training unless all local checks pass
- If Huanxin auth or the remote editing surface is unavailable, treat that as a blocker and document it precisely instead of pretending the remote step completed

## Deliverables To Build Iteratively

1. A concrete project plan and backlog
2. A dataset strategy for quantum algorithms plus software-engineering tasks
3. Data generation and curation scripts
4. Evaluation harnesses for quantum-code correctness and software quality
5. CPU-feasible fine-tuning or adaptation experiments
6. Research notes documenting findings, tradeoffs, and next steps

## Domain Requirements

- Focus on quantum algorithm code in frameworks like Qiskit, Cirq, PennyLane, and small educational simulators when appropriate
- Cover algorithm families such as QFT, Grover, VQE, QAOA, teleportation, superdense coding, phase estimation, error mitigation, and circuit optimization
- Preserve software-engineering quality: testing, refactoring, documentation, interfaces, and maintainable Python tooling
- Prefer verifiable tasks with executable tests or simulators

## Operating Rules

- Start each cycle by reading AGENTS.md, PROJECT.md, HEARTBEAT.md, USER.md, and any recent notes under memory/
- Keep a running log in memory/YYYY-MM-DD.md
- When a substantial decision is made, update MEMORY.md if it exists or create it if needed
- If code is changed, leave the repo in a runnable state and record how to verify it
- Before any remote training attempt, run the local eval harness and any relevant local tests first; only proceed if they all pass
- Transfer code via S3 scripts, run training via `./scripts/ai2_shell.sh`
- If blocked, document the blocker and define the smallest next experiment

## First Milestones

1. Define scope and success metrics for the target model
2. Choose a CPU-feasible adaptation strategy for Qwen2.5-1.5B-Instruct
3. Build a starter corpus specification for quantum and software-engineering tasks
4. Create evaluation tasks with objective scoring
5. Implement the first end-to-end prototype pipeline in this workspace

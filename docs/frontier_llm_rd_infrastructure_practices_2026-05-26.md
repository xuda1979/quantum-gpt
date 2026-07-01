# Frontier LLM R&D Infrastructure Practices

Date: 2026-05-26

This note summarizes public evidence about how frontier AI teams and mature LLM platform teams structure R&D infrastructure. It is not a claim about any lab's private internals. It extracts practices visible in public system cards, eval docs, safety policies, tracing docs, and RLVR environment docs, then maps them to the `quantum-gpt` ASI1 training loop.

## Short Answer

Top teams do not rely on one dashboard. They run a layered control system:

1. Experiment tracking for every run: config, metrics, system metrics, artifacts, logs, and lineage.
2. Evaluation gates: private held-out evals, public evals, adversarial/safety evals, regression tests, and pass/fail promotion criteria.
3. Agent trace observability: model calls, tool calls, guardrails, errors, latency, and replayable trajectories.
4. RL environment infrastructure: isolated sandboxes, verifiers, reproducible task state, reward computation, and rollout archives.
5. Governance gates: safety tiers, red-team review, human approval, canary deployment, and incident review.
6. Data governance: dataset versioning, contamination controls, split integrity checks, and artifact hashing.
7. Operational monitoring: device utilization, job health, throughput, memory, failed workers, queue depth, cost, and alerting.

For this repo, the current local dashboard is a useful beginning, but it should become one tab in a larger R&D control plane.

## Public Evidence

### OpenAI Pattern: evals, system cards, traces, deployment stages

OpenAI's public safety page describes a cycle of teaching, testing, and sharing, including red teaming, system cards, preparedness evals, staged alpha/beta/GA rollout, feedback, and safety committees.

OpenAI's Preparedness Framework makes this more operational: it defines tracked risk categories, capability thresholds, development-time and pre-deployment evals, safeguards before deployment, and escalation/oversight through a Safety Advisory Group and leadership/Board processes.

OpenAI's public infrastructure writing also shows the operational side: Kubernetes-scale clusters, Prometheus/Grafana dashboards, alerts, health checks, GPU error tracking, quota controls, and incident-driven improvements.

OpenAI's evals docs emphasize that evals are essential for reliable applications, especially when upgrading or trying new models. Their Evals API flow separates task description, test inputs, testing criteria/graders, result analysis, and dashboard exploration.

OpenAI's open-source `evals` repository describes a framework for evaluating LLMs and LLM systems, a registry of benchmarks, custom/private evals, result logging, and private workflow-specific evals.

OpenAI's Agents SDK tracing docs show the observability layer frontier teams expect for agentic systems: end-to-end traces, spans for model generations, tool calls, guardrails, handoffs, custom events, sensitive-data controls, and exporters to other observability backends.

### Anthropic Pattern: capability tiers and safety-triggered gates

Anthropic's Responsible Scaling Policy defines AI Safety Levels where higher capability requires stricter demonstrations of safety, security, and operational controls. The public policy explicitly connects autonomy and dangerous-capability evals to deployment decisions.

The practical lesson is that promotion gates should not be only "loss went down" or "pass rate went up." Capability increases should trigger stricter security, autonomy, elicitation, and red-team gates. Anthropic has also publicly discussed missed eval intervals and under-elicitation gaps, which is a useful warning: eval cadence and elicitation budget need to be explicit system fields.

### Google DeepMind Pattern: early-warning evals across the lifecycle

Google DeepMind's Frontier Safety Framework uses Critical Capability Levels, alert thresholds, material capability change assessments, residual-risk assessments, safety cases, incident detection, and post-market monitoring.

For this repo, every meaningful post-training checkpoint should be treated as a possible material capability change: compare against the last blessed checkpoint on quantum/coding holdouts, agentic autonomy tasks, unsafe-code/security tasks, and regression baselines before promotion.

### Meta Pattern: hidden evals and training reliability

Meta's Llama 3 disclosures emphasize hidden human eval sets, benchmark/eval details, safety red teaming, Llama Guard/CyberSecEval/Code Shield, data filtering, scaling-law-driven compute decisions, automated error detection, silent data corruption detection, checkpoint/rollback storage, and high effective training time.

For us, the strongest lesson is to keep promotion evals sealed from data generation and prompt tuning, then make infrastructure reliability measurable: checkpoint age, rollback path, data corruption checks, and effective training time should be surfaced.

### NVIDIA / NeMo Pattern: RLVR environments and verifiers

NVIDIA NeMo Gym frames agent/RL infrastructure around environments that contain task data, an agent harness, verifier, state, and runtime/sandbox. Verifiers score attempts with exact match, code execution, tests, rubrics, LLM-as-judge, or reward models, and the same scores are used for evaluation and training.

NeMo Gym's tutorials use a decoupled architecture: agent server, model server, and resources server for tools and verification. This is close to what this repo needs for ASI1: one learner/trainer, rollout workers, sandboxed tool execution, and a verifier API.

### W&B / Ray / LangSmith / Phoenix Pattern: production-grade observability

W&B documents the standard experiment-tracking unit: a run with hyperparameters, time-series metrics, system metrics, model artifacts, dashboards, reports, sweeps, artifacts, and registry.

Ray's observability docs are a useful model for distributed job health: dashboards, task/actor state, logs, metrics, resource scheduling, memory/OOM, checkpointing, fault tolerance, and failure/preemption handling.

LangSmith and Phoenix represent the agent-app observability pattern: detailed traces, dashboards, alerts, feedback, online evals, replay, datasets, experiments, and root-cause analysis over recurring failures.

MLflow adds another common pattern: runs with params, metrics, artifacts, model registry, dataset association, and comparison UI. Even if this repo stays dependency-light, the local JSON artifacts should preserve the same data model.

## What Top-Firm Practice Means For This Repo

### P0: Must Have Before Scaling ASI1 Runs

- Run registry with immutable run ID, command, git SHA, config hash, dataset hash, model hash, adapter hash, artifact hash, and environment fingerprint.
- Live training metrics: reward, pass rate, reward variance, loss, KL, grad norm, learning rate, rollout count, skipped steps, and optimizer updates.
- Standardized step JSONL fields: `step`, `global_step`, `loss`, `kl`, `entropy`, `lr`, `reward_mean`, `reward_std`, `pass_rate`, `group_pass_rate`, `advantage_energy`, `tokens_in`, `tokens_out`, `context_used`, `oom_retry_count`, `skipped`, and `skip_reason`.
- Device health: NPU utilization, HBM usage, host RAM, disk, throughput, dataloader stalls, worker failures, OOMs, and restart count.
- Verifier health: public tests, hidden tests, timeout rate, flaky-test rate, hardcoding/cheating flags, sandbox failures, and tool-policy violations.
- Private eval gate: held-out benchmark must run automatically at cadence, with exact benchmark version and no training contamination.
- Trace capture for agentic rollouts: prompt, tool calls, file reads, edits, tests, final answer, reward components, and termination reason. Minimum trace span fields should be `trace_id`, `run_id`, `task_id`, `rollout_id`, `parent_span_id`, `span_type`, `tool_name`, `prompt_tokens`, `completion_tokens`, `latency_ms`, `input_digest`, `output_digest`, `error`, and `state_summary`.
- Safety guardrails: destructive command blocks, network egress controls, secret redaction, dependency change review, prompt-injection tests.

### P1: Should Have For Fast Research Iteration

- Compare runs side by side by reward/pass rate/eval score/tool behavior, not only by run directory.
- Regression dashboard: latest run vs baseline vs best-known model on the same frozen evals.
- Data dashboard: examples by source/domain/license/split, dedup statistics, contamination checks, and train/eval overlap reports.
- Rollout replay UI: inspect successful and failed trajectories with exact verifier outputs.
- Failure taxonomy trend: context overflow, read-only loop, low reward variance, tool misuse, no final answer, test timeout, syntax/runtime error.
- Automated alerts: P0 gate failure, stalled metrics, no checkpoint, NPU underutilization, spike in unsafe tool use, eval regression.
- Promotion workflow: smoke -> 1-NPU canary -> 4-NPU run -> 16-NPU run -> full private eval -> model card.
- Incident reports for failed/aborted runs: exact command, environment, run ID, stderr/log tail, last good step, suspected cause, mitigation, retry safety, and artifact hashes.
- Elicitation tracking: prompt style, max tokens, sampling, best-of-N, scaffold/tool access, and whether the score is minimal elicitation or strong elicitation.

### P2: Useful After The Loop Works

- Hyperparameter sweeps and ablation tracking.
- Automatic task difficulty curriculum using pass@k bands.
- Offline data factory dashboard: bug injector, test writer, solver, reviewer, judge, red-team queues.
- Cost and throughput accounting: tokens/sec, samples/sec, NPU-hours per eval point gained.
- Multi-environment RLVR: software, quantum, security, terminal, browser, and long-context tasks.

## Dashboard Roadmap

The local dashboard should become a tabbed console with these views:

1. Overview: current health, P0/P1/P2 gates, active blockers.
2. Training: reward/loss/KL/pass-rate curves, optimizer updates, skipped steps.
3. Infrastructure: NPU/CPU/RAM/disk/network, worker health, queue depth, checkpoint age.
4. Evaluations: private eval, public eval, regression table, per-category pass rates.
5. Rollouts: trace replay, tool-call counts, termination reasons, reward components.
6. Data: dataset manifests, split integrity, contamination checks, license/source counts.
7. Artifacts: run lineage, hashes, checkpoints, adapters, logs, model cards.
8. Safety: destructive-command blocks, secrets redaction, prompt-injection evals, dependency/security scans.
9. Alerts: current incidents, historical failures, owner/action/status.

## Near-Term Implementation Plan

1. Extend `reports/agentic_training_run_registry.json` to include command, git SHA, config hash, dataset hash, model hash, adapter hash, environment fingerprint, and checkpoint metadata.
2. Add a canonical `run_manifest.json` per ASI1 run: run ID, git SHA, trainer command, model path, adapter init, benchmark file, holdout file, tokenizer/config hashes, environment name, and NPU device list.
3. Add an `infra` tab to `scripts/render_agentic_training_dashboard.py` for local/remote NPU health when artifacts are available.
4. Add an `evals` tab that compares each run against a frozen baseline and best-known adapter.
5. Add `training/agentic_trace_schema.py` or equivalent schema docs for rollout trace JSONL records.
6. Add a validator that fails P0 when metrics exist but traces, verifier outputs, or lineage are missing.
7. Add ASI1 artifact fetch once the shell/sync path is stable enough, so the local dashboard is driven by real remote run status.
8. Add alert generation into `live_status.json` rather than only deriving alerts in the renderer.
9. Add a lightweight ASI1 heartbeat sampler: `pid_alive`, `last_metric_age_sec`, `last_log_age_sec`, `npu_visible`, `npu_mem_used`, `npu_util`, `disk_free`, `checkpoint_age_sec`, and `remote_path`.
10. On failure, write `failure_report.json` with exact command, stderr tail, exit reason, last good step, artifact hashes, and next recommended action.

## Source Pointers

- OpenAI safety overview: https://openai.com/safety/
- OpenAI Preparedness Framework v2: https://cdn.openai.com/pdf/18a02b5d-6b67-4cec-ab64-68cdfbddebcd/preparedness-framework-v2.pdf
- OpenAI Kubernetes scaling infrastructure: https://openai.com/index/scaling-kubernetes-to-7500-nodes/
- OpenAI GPT-5 system card: https://openai.com/index/gpt-5-system-card/
- OpenAI Evals docs: https://developers.openai.com/api/docs/guides/evals
- OpenAI Evals repository: https://github.com/openai/evals
- OpenAI Agents SDK tracing: https://openai.github.io/openai-agents-python/tracing/
- Anthropic Responsible Scaling Policy: https://www.anthropic.com/news/anthropics-responsible-scaling-policy
- Anthropic updated RSP: https://www.anthropic.com/news/announcing-our-updated-responsible-scaling-policy
- Google DeepMind Frontier Safety Framework: https://deepmind.google/discover/blog/strengthening-our-frontier-safety-framework/
- Meta Llama 3 blog: https://ai.meta.com/blog/meta-llama-3/
- Meta Llama 3 Herd paper: https://ai.meta.com/research/publications/the-llama-3-herd-of-models/
- Meta large-scale LLM training infrastructure: https://engineering.fb.com/2024/06/12/data-infrastructure/training-large-language-models-at-scale-meta/
- NVIDIA NeMo Gym environments: https://docs.nvidia.com/nemo/gym/main/about/concepts/environments
- NVIDIA NeMo Gym single-step environment tutorial: https://docs.nvidia.com/nemo/gym/latest/environment-tutorials/creating-training-environment.html
- W&B experiment tracking: https://docs.wandb.ai/models/track
- MLflow tracking: https://www.mlflow.org/docs/latest/ml/tracking
- Ray observability: https://docs.ray.io/en/latest/ray-observability/index.html
- LangSmith observability: https://docs.langchain.com/langsmith/observability
- Arize Phoenix overview: https://arize.com/docs/phoenix

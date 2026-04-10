# Autonomous R&D Cycle System

## Vision and Scope

The autonomous R&D cycle system is a staged control plane for the end-to-end loop: research intake, sprint coding, local validation, Gemma-target preflight, remote fine-tuning preparation, evaluation, and artifact generation. It is explicitly engineered to keep stakeholder concerns visible (safety, auditability, delivery cadence) while maintaining the speed needed for rapid experimentation.

The current implementation should not be described as full remote-training enforcement. Its honest role today is narrower:

- collect the evidence needed before a Gemma 4 switch is credible
- emit a structured report and command sheet for each iteration
- emit a machine-readable cycle-state artifact naming the current blocking stage and next action
- emit a concrete OmniCoder 9B fallback action when Gemma is blocked on transfer/runtime but local gates are already green
- keep runtime/backend blockers explicit instead of hiding them behind vague orchestration language

## Stakeholder Concerns

- **Leadership/Delivery:** Track clear milestones (dataset hygiene, training handoffs, rollout readiness) and emit one consolidated report per iteration. The control plane must describe dataset provenance, validation results, and deployment gating status so leadership can sign-off without re-running low-level checks.
- **Research/Engineering:** Provide reproducible runbooks for each experiment, including the precise dataset+model pairing and CLI commands. The control plane should surface whether local gates, paper references, and artifact metadata are present before a new phase is proposed.
- **Safety/Compliance:** Surface the risk posture (e.g., dataset overlap, hallucination metrics, resource pressures) as structured reports rather than buried logs. Automated alerts or stop conditions can be created from these reports when thresholds are exceeded.

## Gemma 4 Next-Target Gate

Gemma 4 is the designated next-model target. Before the system switches the training trajectory to Gemma 4 we must demonstrate:

1. Coverage buckets defined in this control plane (e.g., quantum-generalization holdout and interface prefix mix) are reliably produced and validated.
2. Local evaluation reports (pass/fail, per-task breakdown) show parity or improvement over the current baseline.
3. Gemma-target source and trainer/backend preflight pass locally: the checkpoint is auditable from the local machine, the local snapshot path is explicit, and the local Gemma gate rejects unsupported conditional-generation backends before any Huanxin launch.
4. Artifact cataloging is complete: there is a documented command sheet, dataset manifest, evaluation scorecard, and human-readable summary for each Gemma 4 preflight or training attempt.

The current verified state is more specific than a generic "remote blocked" summary:

- ai2/Huanxin shell access is repaired on the exact train-dev route and is no longer the primary blocker
- the remote launcher is Gemma-target aware, but only in the guarded sense that it exits early with a concrete preflight blocker
- Gemma still remains blocked locally until snapshot verification and runtime/backend readiness pass
- when those Gemma blockers are active but local eval and holdout integrity have already passed, the control plane can now emit the verified OmniCoder 9B continuation lane as a parallel next step instead of idling

The control plane currently stages these checks through `scripts/run_autonomous_rd_cycle.py`, which is wrapped by `code/run_command.sh`. In its current form, it generates three concrete iteration artifacts:

- a structured JSON/Markdown report
- a command sheet
- a machine-readable cycle-state JSON artifact with `current_stage`, `next_action`, `stop_reason`, and per-stage status

The current stage graph covers local eval, holdout verification, Gemma source audit, local snapshot acquire/verify, Gemma trainer/backend preflight, and remote-launcher readiness. Snapshot acquire should be interpreted carefully: the control plane now distinguishes between "missing", "partially materialized and still downloading", and "present but not yet verified". For large sharded checkpoints like Gemma 4 31B, it now also reports indexed total weight bytes, observed downloaded bytes, a progress percentage, and whether incomplete shard mtimes still show recent activity. The Gemma source-audit stage is also more robust now: if a verified local audit artifact for the exact target already exists, the control plane can continue using that evidence even when a same-turn live refresh fails due transient network or DNS resolution. It also separates remote-path health from model-family readiness, so Gemma can remain locally blocked even after ai2 repair success. The system does not yet automatically enforce remote handoff or remote training transitions, and it should continue to report Gemma 4 as blocked until runtime and conditional-generation backend readiness are validated.

## Reporting and Artifact Emission

Every iteration must emit:

- A **comprehensive report** (auditable, time-stamped) detailing which datasets were used, which benchmarks were run, their aggregate scores, and any anomalies or blockers. This report also references the pending next steps (e.g., moving to Gemma 4 fine-tuning).
- A **cycle-state artifact** naming the current blocking stage, the next command to run, and the last completed local-preflight stage.
- A **research paper artifact** documenting the controls, rationale, and any architecture modifications required to keep the loop autonomous.
- A **code artifact** (the companion `run_command.sh`, which delegates to `scripts/run_autonomous_rd_cycle.py`) capturing the staged local-preflight entrypoint for the iteration.

The combination of narrative, cycle-state, report, and runnable preflight instructions keeps the control plane visible and traceable for every stakeholder group without overstating the current level of automation.

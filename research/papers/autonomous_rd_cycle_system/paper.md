# Autonomous R&D Cycle System

## Vision and Scope

The autonomous R&D cycle system orchestrates the end-to-end loop: research intake, sprint coding, local validation, remote fine-tuning, evaluation, and artifact generation. It is explicitly engineered to keep stakeholder concerns visible (safety, auditability, delivery cadence) while maintaining the speed needed for rapid experimentation.

## Stakeholder Concerns

- **Leadership/Delivery:** Track clear milestones (dataset hygiene, training handoffs, rollout readiness) and emit one consolidated report per iteration. The control plane must describe dataset provenance, validation results, and deployment gating status so leadership can sign-off without re-running low-level checks.
- **Research/Engineering:** Provide reproducible runbooks for each experiment, including the precise dataset+model pairing and CLI commands. The control plane must gate transitions by verifying that documentation, tests, and artifact metadata have been published before a new phase begins.
- **Safety/Compliance:** Surface the risk posture (e.g., dataset overlap, hallucination metrics, resource pressures) as structured reports rather than buried logs. Automated alerts or stop conditions can be created from these reports when thresholds are exceeded.

## Gemma 4 Next-Target Gate

Gemma 4 is the designated next-model target. Before the system switches the training trajectory to Gemma 4 we must demonstrate:

1. Coverage buckets defined in this control plane (e.g., quantum-generalization holdout and interface prefix mix) are reliably produced and validated.
2. Local evaluation reports (pass/fail, per-task breakdown) show parity or improvement over the current baseline.
3. Artifact cataloging is complete: there is a documented run command, dataset manifest, evaluation scorecard, and human-readable summary for each Gemma 4 training attempt.

The control plane enforces these gates by requiring the completion of the `code/run_command.sh` steps (see companion file) and by publishing a report entry whenever a gate is cleared or a hold condition fires.

## Reporting and Artifact Emission

Every iteration must emit:

- A **comprehensive report** (auditable, time-stamped) detailing which datasets were used, which benchmarks were run, their aggregate scores, and any anomalies or blockers. This report also references the pending next steps (e.g., moving to Gemma 4 fine-tuning).
- A **research paper artifact** documenting the controls, rationale, and any architecture modifications required to keep the loop autonomous.
- A **code artifact** (the companion `run_command.sh`) capturing the executable steps needed to reproduce the iteration end-to-end.

The combination of narrative, report, and runnable instructions keeps the control plane visible and traceable for every stakeholder group.

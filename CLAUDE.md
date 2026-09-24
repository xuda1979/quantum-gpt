# CLAUDE.md — quantum-gpt project instructions (fresh-session load path)

You are working on **quantum-gpt**: a harness-driven R&D loop whose single
objective is a LoRA adapter on Qwen3.8-27B that passes **18/18** on the
frozen 18-task quantum holdout, fail-closed verified (adapter-applied +
probe-differs, candidates differ from base), and **beats base**.

## Load this workflow — it lives in the REPO, not in conversation memory

1. **Machine spec (source of truth for stages):**
   `harness/workflow_spec.json` — stages `train -> eval_leg ->
   compose_verdict`, each with predecessor requirements and executable checks.
2. **Executable stage gate:** `harness/scripts/workflow_gate.py`
   - `check --stage <id>` — exit 0 = GO; anything else = BLOCKED. A stage
     runs ONLY when every predecessor has an OK attestation in
     `harness/state/atts/<stage>.ATT.json`. Fail-closed.
   - `attest --stage <id> --status OK|FAILED --evidence '{...}'` — record a
     stage outcome. NEVER attest OK without primary evidence.
3. **Independent audit:** `harness/scripts/workflow_audit.py <stage>` —
   re-verifies an attestation against PRIMARY evidence (not its self-claim);
   contradicted atts are REVOKED in place and block successors.
4. **Live state:** `harness/state/GOAL.json` (objective), `QUEUE.json`
   (cards), `training_source_of_truth.json` (authoritative engine),
   `.sapo-loop/STATUS.md` (rolling log).
5. **Loop control:** `python3 harness/qgh.py tick` (dispatch), `standup`,
   `done-check`. Launchd jobs tick every 120s; a retired/done goal stops all
   work — verify `GOAL.json status` is OPEN after any goal-related change.

## Hard rules (enforced by the gate + review, not by memory)

- A stage whose predecessor FAILED or lacks an attestation MUST NOT run —
  check the gate first; it is the same check the launch path uses.
- Never fabricate a measurement. Never mark DONE on an unverified claim.
- Eval artifacts are fail-closed: adapter-applied + probe-differs markers,
  sha pins, two independent legs for any goal-retiring verdict.
- TDD for harness changes: RED first, smallest fix, GREEN + touched suites.
- Training/eval compute lives on Huanxin boxes ASI1/ASI2/ASI3 (exec daemons
  on ports 20646/19004/20653 via `run_box`); the authoritative trainer is
  `SFT_peft_resume` on ASI3 (see `training_source_of_truth.json`).
- A dead trainer is not a stop condition: `harness/scripts/resume_training.py`
  resumes from the LATEST-RUN checkpoint (mtime-ranked, C-9746); the
  self_resume_guardian does this automatically when tests are green.

## Quick start for any session

```
python3 harness/scripts/workflow_gate.py check --stage eval_leg   # am I allowed?
python3 harness/scripts/workflow_audit.py train                   # does the train att stand?
python3 harness/qgh.py standup                                    # full loop state
```

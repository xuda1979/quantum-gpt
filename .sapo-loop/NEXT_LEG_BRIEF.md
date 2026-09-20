# NEXT LEG BRIEF - written 2026-09-15 06:25 CST (standup #466 wave; manager)

## Goal
First leg designed to actually LEARN: B-236 repair auto-relaunch (legs survive past step 20),
B-232 crash-progress-credit ON (58 percent of candidates were hard-zeroed), B-237 verifier-credit
survival (near-misses earn real shaped reward). Calibrated defaults apply.

## BINDING LAUNCH RULES
1. Do NOT pass an explicit ASI3_SAPO_LR override - the calibrated default (2.5e-5) must apply.
2. Warm-init: outputs/sapo-27b-ai-20260908T094427Z/step_000097_adapter (3/18 banked; the
   085136Z step_000097 is a DIFFERENT adapter, 2/18 - do not confuse them). Backup: s26 same run.
3. Harness is FULLY AUTOMATIC — launch when fleet ready + TDD green.

## GATE ORDER (each blocks the next)
- G1 TRANSPORT: ASI3 :20653 exec answers a canary (<5s). Currently DOWN (keeper healing, cycle 107).
- G2 DEPLOY: surgical box patch, one wave: (a) B-236 sidecar auto-relaunch helper + wiring in
  training/grpo_trainer.py (Mac lines 49-104 + 6769-6772; exact-match patches <4.5KB, .bak first);
  (b) B-224 instrumentation incl. the SECOND file grpo_utils.py (sig 390-391 + merge 565-569).
  DEPENDENCY GATE: grep box trainer for train_seq_cap + strict_zip FIRST - if absent, land B-212/compat
  before the B-224 rows or the trainer crashes at runtime. Verify: grep B-224 >=8 hits, py_compile both
  files, strict-zip scan empty. Lesson B-163/B-223: a landed patch is not a running fix - a relaunch
  is required for it to execute.
- G3 SMOKE: scripts/sapo_smoke_probe.py --ckpt <warm-init adapter> on the box - greedy syntax rate
  must PASS its refusal gate AND sampled-spread token lengths must be hundreds (not single digits;
  leg5 step-1 entropy collapse signature).
- G4 PRE-LAUNCH CHECKLIST: tests green (this wave: 426/426 reward sweep, 44/44 launcher+guards,
  133/135 repair slice, 7/7 sidecar new), config audit (lr default, group 8, MAX_SEQ_KL 0.6,
  reject-mode env-overridable, crash-credit default 1, repair sidecar ensure at boot), box gate
  0 trainer procs, boot verify echo (lr + adapter_init + benchmark + step_begin), watchers re-armed.

## EXPECTED FIRST-3-STEP VERDICT (user test of the calibrated stack)
pass_rate > 0 AND mean_response_length in the hundreds AND no all-skip steps.
If repair queues appear: sidecar_relaunch_attempted true + conversions > 0 within ~2 steps = B-236 working.

## AFTER LAUNCH (watch, do not touch)
- Breaker watch: all_fail_without_repair should NOT fire before ~step 60; if it does, harvest the
  per-candidate reward vector (B-224 rows) before any relaunch decision.
- Eval economy: no sweep of old checkpoints; first eval trigger = first drift-ACTIVE checkpoint.

## USER ITEMS (unchanged, console-gated)
- dp4 judge upstream (judge mass inert: BATCH_COMPARATIVE_JUDGE off + upstream RED).
- ASI1 console re-open if 20646 does not converge.

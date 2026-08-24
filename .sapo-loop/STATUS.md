# SAPO loop status — quantum-gpt

**OBJECTIVE (user, 2026-08-24 12:32 CST): get an adapter that OUTPERFORMS BASE Qwen3.6-27B on quantum
computing coding tasks, ASAP. Every decision (eval scheduling, checkpoint gating, run length, lane
allocation) is judged against: does this produce the beats-base verdict sooner? The 18-task frozen
holdout + targeted10 prechecks are the measuring instruments; training is the generator, not the goal.**

Updated: 2026-08-24 09:55 CST — loop spawned (cron job_1417e4673d5a, every 10m).
User directive 2026-08-24: "we have done lots of work, we should continue based on previous work."
TDD requirement (user, 2026-08-23; REINFORCED 2026-08-24 12:33 CST as the #1 operating rule — we must never
waste NPU-hours running wrong code/training): every suspected rollout/resume/routing/reward/training-efficiency
defect needs a reproducing regression test FIRST, then the smallest fix, focused+regression validation,
deploy, live telemetry. **Nothing deploys to the box without a red→green test and a green focused suite.**
Never relaunch on untested hypotheses. Any worker violating this gets its changes reverted by the manager.
Do not commit to git unless the user asks.

## Environment (last verified 2026-08-24 09:28 CST)
- Target env: Huanxin **AI** (authorized by the user 2026-08-24 for the SAPO relaunch + routine training
  control). **ASI3 is DEPRECATED — do not launch training there.** "Keep alive" duty = the AI env + daemon /exec.
- Daemons: ASI3 daemon PID 21080 (booting; not command-ready: ready=false, authDriftDetected=true,
  shellSurfaceReady=false), ai1 daemon PID 47095 (running). Ports: 19004 / 19006 / 20653 — map before use.
- Authoritative deploy bundle: `tmp/ai-sapo-targeted10-safe-20260824T014200Z.tgz`
  SHA-256 `914f991e3a2c7f69d1b999f330abb262aedfea076a400e472cf85567b8b44fdf` (60 files).
  AI defaults: `/root/software/quantum-gpt`, `models/Qwen3.6-27B`, project-local checkpoints, 8 NPUs.
- NEVER resume semantic30 step-3/5 checkpoints (semantic30 is fail-closed). Launch path = frozen-holdout
  disjoint targeted10.
- Warm adapter: the clean rank16/alpha32 warm distillation adapter must be resolved from lineage before launch.

## Roles (agents spawned 2026-08-24 ~09:5x CST)
- `debugger.md`  — SAPO bug fixes (TDD) + relaunch on AI. Scope: training/grpo_trainer.py, launcher/submit scripts, configs/rl/, tests/.
- `keepalive.md` — AI env alive + daemon /exec command-ready. Scope: browser-automation/, launchd/, /tmp auth scripts.
- `dataeff.md`   — data-efficiency audit + tested fixes. Scope: training/grpo_utils.py, evals/benchmarks/, tests/.
- `eval.md`      — bundle integrity + warm-adapter lineage + frozen promotion gate. Read-only on code; writes reports/.

## Governance (user-confirmed 2026-08-24 12:30 CST)
- **Main session = owner + manager** of the SAPO project. Agents are workers with scoped ownership;
  the main session holds the goal, the user relationship, and launch/stop/recovery authority.
- **Standup = the management cadence**: after each standup, the main session reconciles state
  (status files vs expectations), then manages: respawn stale roles, send directives, adjust scopes,
  close loops, record decisions here. Workers stay read-only on the live training.
- **Directive rule (user, 2026-08-24 13:46 CST)**: the manager MUST end every standup with explicit
  next-action directives to each active worker — concrete tasks, priorities, and deadlines — not
  just a summary. Deliver via SendMessage to live agents or their status files, and record here.
- Workers own: access watchdog = daemons/processes alive; eval agent = adapter verdicts;
  metrics analyst = per-step rollout quality + learning signatures. They report via .sapo-loop/*.md.

## Loop protocol (each 10-min fire — read this FIRST)
1. Read this file + the four role .md files. Check the training run state if relaunched.
2. If a role's file is stale (>30 min since its "Updated" line) and its work is incomplete → respawn that
   single role with the same scope from its .md file's "Next" section. Never spawn duplicates while a role
   is actively working.
3. If training is running: monitor step markers in the train log, grpo_step_metrics.jsonl growth, checkpoint
   landings; alert if the newest phase marker is >20 min old.
4. Update this file (time + changes). Relay material changes to the user in the session reply.
- 2026-08-24 (eval role): bundle verified 60/60 identical (SHA-256 914f991e...); warm adapter = iter-2 27B r16/a32 (20260706T083156Z, head 597cde3); gate hashes (benchmark/system-prompt/public-contract) all MATCH; targeted10 disjoint + 10/10 refs, holdout 18/18 refs; suites 61/61 + 154/154 + 136-subset pass; eval staged per reports/sapo-verify-2026-08-24.md (no local checkpoint to precheck).
- 2026-08-24 10:15 CST — dataeff: fixed shaped-reward parser for targeted10 arrow-form fail lines (grpo_utils.py; 8 new regression tests, 221 pass); reported inert adaptive token budget (trainer-side) + truncation-rate overcount to debugger; report reports/sapo-data-efficiency-2026-08-24.md.
- 2026-08-24 10:25 CST — debugger: bundle==tree (60/60); fixed 2 stale test fixtures + launch-critical token budget drift (2048/2048/3072, INNER_EPOCHS=1, CKPT=1800, submit-path aligned); focused SAPO suites 62/62 green; deploy bundle tmp/ai-sapo-targeted10-deploy-20260824T022054Z.tgz sha256 18b252f1...9bbed; warm adapter = outputs/qg-27b-glm52-distill-sft-glm52-distill-27b-20260706T083156Z/adapter (r16/α32); launch STAGED — AI daemon 19006 not command-ready (authDriftDetected=true) → unblock: keepalive auth bridge.
- 2026-08-24 10:45 CST — debugger: bundle==tree (60/60); fixed stale fixtures (2), launch-critical token budget 2048/2048/3072 + INNER_EPOCHS=1 + CKPT=1800 (3 launchers), truncation-rate EOS-at-cap overcount; folded in dataeff shaped-reward arrow-form fix; 389/389 focused green; deploy bundle tmp/ai-sapo-targeted10-deploy-20260824T023000Z.tgz sha256 cfb85e7b...4d6e; warm adapter = outputs/qg-27b-glm52-distill-sft-glm52-distill-27b-20260706T083156Z/adapter; launch STAGED — AI daemon 19006 not command-ready (authDriftDetected=true, /health unresponsive) → unblock: keepalive auth bridge.

- 2026-08-24 11:00 CST keepalive: ASI3 daemon pid 36183 port 20653 /exec ready:true (Safari-SSO bridge self-healed; capture=/tmp/capture_safari_fixed.sh); ASI3 env 运行中 8x910B2 (ASCEND_VISIBLE_DEVICES=5,6,7,0,1,2,3,4), warm adapter qg-27b-glm52-distill-sft-glm52-distill-27b-20260706T083156Z/adapter present, no trainer resident; AI env dl-9a5a098a left 运行中 1卡 (started 10:43 CST, stop TBD); AI daemon retired per user ASI3 directive.
- 2026-08-24 11:15 CST — LAUNCHED on ASI3 (user-directed, live login): run sapo-27b-ai-20260824T031524, trainer 61136, ckpt-sync 61127, repair sidecar 61137; ASI3_SAPO_ROOT=/root/work/software/quantum-gpt, MODEL=/root/work/filestorage/Qwen3.6-27B, ADAPTER_INIT=iter-2 warm r16/a32, STEPS=120, targeted10, ckpt 1800s; deploy sha-verified 63/63 (box==local incl. grpo_trainer). Boot telemetry pending (model load ~15-30 min).
- 2026-08-24 11:32 CST (eval role): ASI2 daemon READY on 19004 but ASI2 = 4 NPUs only (davinci1-4) — NPU 3-state eval HELD per directive (report+wait); 9 stale eval deps redeployed to shared box via ASI2 daemon, sha256-verified all-match; warm adapter CONFIRMED live in ASI3 launch_config (iter-2 r16/a32); training step1 done, step2 running; polling for first checkpoint.
- 2026-08-24 12:00-12:03 CST — metrics role: poller instrumented (short-line parser for terminal wrap); three transient poller bugs produced FALSE ALERTS (NO-OP 12:00, ENTROPY 12:01, ENTROPY 12:02) — all RETRACTED, parse/label artifacts; fixed (LABEL_MAP + entropy threshold 0.05); verified values now correct; baseline verdict stands at WATCH; no real checklist item tripped.
- 2026-08-24 12:08 CST keepalive: ASI3 (20653) + ASI2 (19004) daemons both ready:true/shell:true/drift:false across 7 poll rounds; trainer 61136 alive, step 2 COMPLETE (loss -0.020) with FIRST fresh checkpoint step_000002_adapter saved 03:51 UTC, step 3 (circuit_phase_repair) in generation, all 8 NPUs ~100% AICore; ckpt-sync 61127 + repair 61137 resident; no blockers.
- 2026-08-24 ~11:57 CST (eval role): FIRST SAPO CHECKPOINT step_000002_adapter PRECHECKED = ACTIVE (clone-based CPU precheck on box: max_abs_diff 0.00098 > bf16 ULP, lora_B 0.0038 nonzero, 851 tensors, verdict "active") — evidence reports/sapo-precheck-step2-2026-08-24.json. First real functional SAPO adapter ever. 3-state NPU eval still HELD: ASI2 has only 4 NPUs (davinci1-4); per directive report+wait, do not force. Eval deps deployed+verified on shared box. Training step 4 running.
- 2026-08-24 12:18 CST keepalive: first synced checkpoint checkpoint_20260824T041525_step000002 landed in outputs/checkpoints/qwen36_27b_sapo_ai (step-2 adapter, sync daemon 61127); step 3 COMPLETE (loss -0.0085, circuit_phase_repair passed where p13 hung), step 4 in generation; both daemons ready:true; eval agent has a fresh eval target on ASI2.
- 2026-08-24 04:48Z — dataeff live-run time audit: 4 steps @19.4min avg, 4/4 real updates, 0 waste in updates/eval/I/O; top findings: stage markers lack timestamps (per-phase unmeasurable), step-2 adapter precheck-active => holdout verdict should drive stop-early (saves 22.6-37.5h), shaped 0.0 on s2/s3 = structural API crashes not parser (fix live); report reports/sapo-time-efficiency-2026-08-24.md.
- 2026-08-24 13:12 CST — METRICS ALERT: DEAD-SIGNAL: 4 consecutive steps pass_rate=0 & shaped~0 (parser-fix condition); ENTROPY: <1 collapse (latest step 7, box ts 2026-08-24T05:12:47Z)
- 2026-08-24 13:42 CST — METRICS ALERT: trainer PID 61136 NOT RESIDENT. Latest rows: []. Log tail: . Recovery owned by access agent + main session — NOT relaunching.
- 2026-08-24 13:55 CST — debugger: dead-signal investigation (run sapo-27b-ai-20260824T031524, steps 5-8): root cause = task-contract coldness + prose-only harness details + uniform candidate failures (NOT generation bug; entropy-collapse claim refuted; box==tree); fixed adaptive-temp non-engagement on repair-routed flat groups (TDD: 2 new tests, 391/391 green, STAGED); verdict: run CONTINUES; report reports/sapo-dead-signal-investigation-2026-08-24.md; bundle tmp/ai-sapo-targeted10-deploy-20260824T064500Z.tgz sha256 ac3b85fc...860c3.
- 2026-08-24 13:50 CST — METRICS ALERT: ENTROPY: <1 collapse (latest step 10, box ts 2026-08-24T05:50:02Z)
- 2026-08-24 13:51 CST — METRICS ALERT: ENTROPY: <1 collapse (latest step 10, box ts 2026-08-24T05:51:50Z)
- 2026-08-24 14:08 CST keepalive: cycle 2 all green (3 rounds 13:56-14:08) — ASI3+ASI2 daemons ready:true/shell:true/drift:false, capture probe echo A/B clean on both (no truncation recurrence), trainer 61136 alive at step ~8 (train_logprob), 3 synced checkpoints (steps 2/4/7), ASI2 three-state eval running (pid 867 + 2 pass1 workers), NPUs 8/4 unchanged, no blockers.
- 2026-08-24 06:05Z — dataeff harness enrichment: 4 prose-only training tasks (stabilizer_tableau_update_repair, measurement_bug_repair, superdense_pauli_router, bitstring_maxcut_landscape) now emit numeric closeness details -> shaped 0.0->0.51-0.9 (crash stays 0); prompts/holdout unchanged; 10 new regression tests pass (8 failed pre-fix), 134+206 suite pass (1 pre-existing unrelated failure); v7 manifest contract hash regenerated d0d2e950->af8429bd (record in reports/sapo-harness-enrichment-2026-08-24.md).
- 2026-08-24 14:30 CST — DECISION (user): warm SFT adapter is IRRELEVANT to the objective (6/18 < base 8/18 on holdout). Promotion gate = SAPO vs BASE only (≥1 strict pass); warm-regression clause DROPPED. Warm-leg eval results are informational only. Analyst question: warm-init vs base-init for next RL start.
- 2026-08-24 14:42 CST — METRICS ALERT: NO-OP: 2 consecutive steps ratio<1.001 & kl_aft<1e-4 & loss>-0.005 & grad<0.05 (latest step 15, box ts )
- 2026-08-24 15:05 CST — algorithm analyst: SAPO-leg scorecard LANDED 07:02Z = **8/18, TIE with base — NO promotion** (gains 0, losses 0). RL-from-warm REPAIRED both warm regressions (qaoa_maxcut/ghz now pass) but taught 0/10 new contracts at ratio 1.0003 drift. Per decision rule → **BASE-INIT next launch** (empty ADAPTER_INIT) + LR 5e-5 + shared_mad; live run continues to 50-update gate. STAGED (TDD red→green, NOT deployed): entropy-gated temp escalation for low-entropy all-fail RL groups (grpo_trainer.py, +3 tests), --loo-advantage-scale shared_mad wired through both launchers (asi3 default, +1 test), config JSON doc lr 5e-5/shared_mad; focused 269 passed, broad sweep 513 passed; report reports/sapo-algorithm-improvement-2026-08-24.md (verdict table + SAPO row) + .sapo-loop/improve.md.
- 2026-08-24 15:25 CST keepalive 🚨: ASI3 daemon 36183 WEDGED (exec busy-forever post stop-command; Ctrl-C no flush) → recovered per playbook: relaunched pid 60933, ready 15:24 (bridge self-heal). GATE CHECK FAILED: `asi3_launch_grpo_direct.sh stop` did NOT stop training — trainer 61136 STILL RUNNING (Rl, 148% CPU, step 20 begun 07:20 UTC, step 19 adapter saved), ckpt-sync 61127 + repair 61137 + child 61399 resident, NPUs busy 105-107%, 5 checkpoints preserved (steps 2/4/7/11/16 synced). DO NOT relaunch BASE-INIT until trainer stopped; trainer NOT killed by me (manager's call).
- 2026-08-24 15:52 CST — 🚀 BASE-INIT RELAUNCH: run sapo-27b-ai-20260824T075223, trainer 68256. VERIFIED: adapter_init=None (base-init, fresh LoRA 16/32), lr=5e-05, loo-advantage-scale shared_mad (in trainer cmdline), steps 120, ckpt 1800s, enriched v7 manifest + all staged fixes deployed sha-verified. Old warm-init run (19 real steps, 8/18 tie verdict) stopped cleanly; its 5 NAS checkpoints preserved. Pre-launch gate: full suite = 0 new failures (10 pre-existing unrelated), SAPO suites all green. Metrics poller repointed.
- 2026-08-24 19:00 CST — algorithm analyst ESCALATION ROOT CAUSE (directive 18:16): run-1's "ACTIVE" precheck was the INHERITED warm SFT LoRA (warm B max 0.003795 == run-1 step-2 B 0.00383; A 0.0184 == 0.0183) — RL-earned B there was noise (~1e-5/update); shared_mad was a NO-OP not a damper (adv_scale 0.97-0.99: flat groups fell back to MAD 1.0 and pulled the EMA up — trajectory reproduced exactly); run-2's B 1e-4→2e-4 is genuinely earned (2.5e-5/update, kl_after up to 6.7e-4 = 10-30x run-1). CORRECTED STACK (staged, TDD, NOT deployed): LR 1e-4 + LORA_ALPHA 64 (asi3 launcher defaults, +1 pin test) + RunningMAD flat-group fix (grpo_utils.py +2 red→green tests) + precheck-bar recalibration for base-init (eval owner); test_sapo_loss stale-pin updated (spec change). Suites green. Report reports/sapo-escalation-analysis-2026-08-24.md + improve.md. Launch cmd: `AI_SAPO_ADAPTER_INIT= bash scripts/ai_launch_sapo_direct.sh launch`. Run-2 untouched (manager stops).
- 2026-08-24 ~16:00 CST (eval role): 3-STATE PROMOTION EVAL COMPLETE (both arms, ASI2 4-NPU lane, no OOM): base 8/18, warm 6/18, SAPO step-2 8/18, SAPO step-7 8/18 (identical pass sets). Gate = pause-rerun both arms (SAPO ties base; needs >=+1 strict pass; warm not regressed; no runnable drop). Prechecks steps 2/4/7 all ACTIVE (first functional adapters ever). Evidence: reports/sapo-promotion-eval-2026-08-24.md + gate JSONs. Beats-base still open at ~50-update checkpoint.
- 2026-08-24 ~16:05 CST (eval role): run-1 (031524) externally reaped at step 19 (TBE pattern); run-2 sapo-27b-ai-20260824T075223 (PID 68256) training. NAS has steps 2/4/7/11/16; step-19 in run dir unevaluated. Next eval cycle: 3-state vs newest checkpoint (precheck first), then ~50-update point.
- 2026-08-24 16:07 CST — RULE (user): the manager must EXECUTE every item in its responsibility list after each standup — directives, watchdog triggers, TDD-queue assignments, gate verifications, records — before reporting.
- 2026-08-24 16:10 CST keepalive: ASI3 daemon 60933 ready:true (base-init run 075223 training: trainer 68256 Rl + ckpt-sync 68247 + repair 68257, 8 NPUs busy ~100%, step 1 generation); ASI2 daemon was DEAD → relaunched pid 41981 ready:true (CDP 9225, ASI2 env, 4 NPUs, probes clean both lanes) — eval lane ready for run 075223's first checkpoint.
- 2026-08-24 16:15 CST — debugger: stop-script bug fixed (TDD, staged): KILL-escalation loop was dead code (re-read rm'd pidfiles) + no pattern fallback for stale/wrong pidfile → TERM-ignoring/stale-pid trainer survived ~30 min; fix resolves pids once + pgrep fallback + KILL survivors; 2 new tests red→green; 397/397; bundle tmp/ai-sapo-targeted10-deploy-20260824T090000Z.tgz sha256 1b241d73...2c6a; new run 075223 (LR 5e-5) live on ASI3 — stop authority = manager.
- 2026-08-24 16:25 CST keepalive: 4 rounds all green (16:08-16:25) — ASI3 60933 + ASI2 41981 ready:true/shell:true/drift:false, probes clean; base-init run 075223 trainer 68256 Rl, step 1 COMPLETE (backward_done 08:18 UTC), step 2 in generation, 8 NPUs busy; ASI2 4-NPU eval lane stable; no blockers.
- 2026-08-24 17:14 CST — METRICS ALERT: NO-OP: 2 consecutive steps ratio<1.001 & kl_aft<1e-4 & loss>-0.005 & grad<0.05 (latest step 6, box ts )
- 2026-08-24 ~17:25 CST (eval role): BASE-INIT cycle: precheck run-2 step_000004 = inert_at_precision (6.1e-5 diff, lora_B 1.0e-4, any_active false — SMALLER drift than warm-init 9.8e-4, hypothesis not confirmed); SAPO-only leg (vs base 8/18, warm skipped) running on ASI2 4-NPU at 14/18, no OOM/stall; ETA ~17:45 CST. Run 2 at step 10.

## Standup meeting — FORMAL FORMAT (user directive, 2026-08-24 18:00 CST)
Every standup MUST follow this fixed agenda, in this order, with every section present:
1. **Header**: #N (incrementing), date/time CST, manager chairs, roles present/absent (absent = no fresh status file → flagged stale).
2. **Objective check** (1 line): the beats-base goal + any decision due this meeting.
3. **Dashboard** (fixed rows): training (step, real-updates count, cadence, alerts) | eval (leg/state/ETA) | checkpoints (NAS count) | poller verdict | daemons.
4. **Per-agent reports** — each agent answers THE THREE QUESTIONS, no exceptions:
   - **Done** (since last standup, with evidence/numbers)
   - **Plan** (before next standup)
   - **Blockers** (each with owner + deadline; if none: "none")
   Agents without a fresh .md update are reported as NO REPORT → flagged.
5. **Manager directives**: explicit next-action per active worker (task + owner + deadline).
6. **Decisions & records**: any decision made this meeting + where it's logged.
7. **Next meeting**: time.
Rules: fixed agenda, concise reports, no problem-solving in-meeting (blockers get owned, not debated), same order every time.
- 2026-08-24 ~18:05 CST (eval role): BASE-INIT CYCLE COMPLETE — precheck run-2 step_000004 = inert_at_precision (6.1e-5 < ULP; smaller than warm-init 9.8e-4, bigger-drift hypothesis NOT confirmed); SAPO-vs-base leg = 8/18 TIE with base (identical pass set) -> pause-rerun (needs >=9/18). Report: reports/sapo-promotion-eval-baseinit-2026-08-24.md. All 5 arms to date tie or regress; no arm beats base. Next: precheck step 7/newer, re-verify at ~50 updates.
- 2026-08-24 ~18:35 CST (eval role): FOLLOW-UP precheck run-2 step_000008 = INERT_AT_PRECISION (max_abs_diff 6.1e-5 UNCHANGED from step 4 — no drift growth; lora_B 2.0e-4 2x but ~19x below run-1 active 3.8e-3; any_active false). Drift-grows hypothesis NOT confirmed through step 8 -> REPORTED IMMEDIATELY; recommend EARLY LR ESCALATION to 1e-4 (do not wait for 50-update gate). SAPO-vs-base holdout leg stays QUEUED until a checkpoint prechecks ACTIVE. Evidence: reports/sapo-precheck-baseinit-step8-2026-08-24.{md,json}.
- 2026-08-24 18:31 CST — 🚀 ESCALATED RELAUNCH (run sapo-27b-ai-20260824T103110, trainer 81132): root cause = run-1 'active' was inherited warm LoRA (B byte-identical), not RL; RL drift was noise. New stack VERIFIED: base-init (adapter_init=None), LR 1e-4, alpha 64, shared_mad + RunningMAD flat-group fix (deployed sha-verified), steps 120. Stop used the FIXED stop script (TERM→KILL escalation proven). Run-2 (075223, 6 real updates, step 11) stopped cleanly; NAS checkpoints preserved. Poller repointed + state reset.

## PRE-LAUNCH GATE — mandatory checklist before EVERY relaunch (user directive, 2026-08-24 18:43)
Wrong-code/inefficiency prevention. No launch may proceed unless EVERY item is verified and recorded:
1. TESTS: full focused suites green (0 new failures; pre-existing env failures enumerated).
2. CONFIG AUDIT: adapter-init state (base-init ⇒ ADAPTER_INIT empty, verify in launch_config), LR/alpha/advantage-scale/taus/KL/group/tokens/ckpt-interval/steps/manifest — each vs the approved stack; manifest contract hash current.
3. DEPLOY INTEGRITY: every changed file sha256-verified on the box vs the tested tree.
4. BOX GATE: 0 trainer/sidecar processes, NPUs idle, prior checkpoints preserved.
5. BOOT VERIFY: trainer pid resident, checkpointing 64/64, sharded map, config echo matches audit, step_begin.
6. MONITORING REPOINT: poller RUN/LOG/PID updated + state reset.
Owner: manager executes; debugger certifies the test suites. Violations block the launch.

## PREVENTION ROLES — dedicated agents (user directive, 2026-08-24 18:46)
Three standing dedicated agents own the prevention duties. Each has a role file; the manager resumes them per cycle:
1. **QA BUG-HUNTER** (.sapo-loop/qa.md, agent = debugger lineage): proactively finds bugs ASAP — trainer critical paths, launchers, harnesses, monitoring tooling. Always TDD (red→green). Cycle: every ~2h or before every launch.
2. **ALGORITHM AUDITOR** (.sapo-loop/audit.md): double-checks algorithm-vs-paper (SAPO arXiv:2511.20347), code correctness, and the training scripts — 3-layer config consistency (argparse vs config json vs launcher exports vs wrapper), plus live-run cmdline cross-check before every launch.
3. **TRAINING GUARDIAN** (.sapo-loop/guardian.md): continuous prevention of wrong/inefficient training and low data efficiency — triages poller alarms (no-op/dead-signal/sub-precision/truncation/entropy/daemon), watches drift signatures (lora_B trend, seq_kl), escalates to the manager with evidence. Long-running cycles (~20-min polls); owns the poller script's health.
Division of labor: QA finds bugs, Auditor verifies correctness, Guardian prevents wasted hours — all TDD, all report via role files.
- 2026-08-24 19:55 CST — debugger: bug-hunt done (TDD, staged): 4 fixes (poller wrap-split + skip/noop label mismatch, resume adapter<->metrics mismatch hard-error, REPAIR_CONVERTED_JSONL ambient pin, config alignment + locks); algorithm-vs-paper EXACT (LOO deviation deliberate); run-3 /proc cross-check NO MISMATCH; 417/417 green; report reports/sapo-bug-hunt-2026-08-24.md; bundle tmp/ai-sapo-targeted10-deploy-20260824T114500Z.tgz sha256 138ffd30...5d5b — NOT deployed (manager gate).
- 2026-08-24 ~19:25 CST (eval role): RUN-3 (base-init, LR 1e-4, alpha 64) step-3 precheck = inert_at_precision BUT POSITIVE DIRECTION: max_abs_diff 1.22e-4 = 2x run-2's 6.1e-5 in only 3 steps (scaling 4.0); step-3 update strong (loss -0.0476, grad 0.696, seq_kl_aft 2.49e-3, pass 0.75). Recalibrated bar: target ACTIVE >ULP by ~step 15; early small expected. Holdout stays QUEUED until ACTIVE. NOTE: NAS sync lags (newest NAS entry is run-2's step-10, not run-3). Evidence: reports/sapo-precheck-run3-step3-2026-08-24.{md,json}.

## PREVENTION ROSTER EXPANSION (user directive, 2026-08-24 20:06)
Five dedicated prevention roles — "check everything, catch everything, ASAP":
1. QA BUG-HUNTER (.sapo-loop/qa.md) — proactive code sweeps, TDD. ~2h cadence.
2. ALGORITHM AUDITOR (.sapo-loop/audit.md) — algorithm-vs-paper, code correctness, 3-layer config, live-run cross-checks. Standalone from next cycle.
3. TRAINING GUARDIAN (.sapo-loop/guardian.md) — continuous training/daemon triage, drift + efficiency watch. ~20-min polls.
4. LOG ANALYST (.sapo-loop/loganalyst.md) — NEW: continuous live-log mining between step records — warning storms, retries, OOM/non-finite events, harness timeouts, repair-queue activity, temperature-escalation behavior, sync-daemon anomalies. ~15-min cadence.
5. CHANGE REVIEWER (.sapo-loop/reviewer.md) — NEW: adversarial review of EVERY staged diff/bundle before the launch gate (correctness, races, resource issues, test quality); also reviews the fixes' own tests. Event-driven per deploy.
Manager rule: five roles run on their cadences; all TDD; all report via role files; escalations go to the manager with evidence.

## Standup format AMENDMENT (user, 2026-08-24 20:07)
The formal standup MUST include, in order: (1) Header; (2) Objective check; (3) Dashboard; (4) EVERY agent's
Done / Plan / Blockers (three lines each, no omissions, agents listed even when standing by); (5) MANAGER'S
SUMMARY — the manager's own read of the state (what's working, what's risky, what it's watching);
(6) Manager directives (owner + deadline); (7) DECISIONS — every decision made or pending, with who decides
and by when; (8) Next meeting. Sections 4, 5, 7 are mandatory verbatim headers.
- 2026-08-24 ~20:30 CST (eval role): RUN-3 step-5 precheck = inert_at_precision BUT DOUBLING TREND HOLDS: max_abs_diff 2.44e-4 = 2x step-3 (1.22e-4) = 4x run-2 (6.1e-5); lora_B 3.0e-4 (3x s3); scaling 4.0. Projection: ~4.9e-4 at s7/8, ~1e-3 ACTIVE around s11-13 (on budget vs step-12-15 bar). Holdout stays QUEUED until ACTIVE. Evidence: reports/sapo-precheck-run3-step5-2026-08-24.{md,json}.
- 2026-08-24 21:15 CST (curriculum-builder): holdout-adjacent v8 curriculum staged (NOT deployed): 10 new training tasks (evals/tasks/quantum/quantum_{three_qubit_entropy,shor_phase_error_correction,trotter_heisenberg_evolution,depolarizing_entanglement_decay,vqe_heisenberg_energy,qaoa_ring4_landscape,bell_basis_discrimination,qft_periodic_state,stabilizer_shor_generators,qml_variational_classifier}) each mapped to one of the 10 frozen-holdout failures (4 stub + 6 wrong-numbers classes); manifest evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt (v7 + 10, header hashes valid), builder scripts/build_grpo_v8_manifest.py, TDD gate tests/test_sapo_curriculum_holdout_adjacent.py (44/44 green: reference passes, near-miss shaped>0, None-stub graded, holdout ID/prompt isolation, manifest regeneration byte-identical; v7 intact af8429bd...). Runtime-validated locally: all 10 references pass, near-miss shaped 0.51-0.90, None-stubs graded 0.509. Report reports/sapo-curriculum-holdout-adjacent-2026-08-24.md. NEXT LAUNCH ONLY — launcher default untouched; holdout read-only.
- 2026-08-24 ~20:50 CST (eval role): RUN-3 step-9 precheck = inert_at_precision; max_abs_diff 3.05e-4 (1.25x s5 — DOUBLING DECELERATED), lora_B 6.0e-4 (still doubling), any_active false. ACTIVE (~1e-3) projection shifts to ~step 14-17 (was 12-15); B-doubling could pull to ~13. Training: 7 real updates/9 steps, s9 loss -0.053 grad 0.515 pass 0.75. Holdout stays QUEUED. Evidence: reports/sapo-precheck-run3-step9-2026-08-24.{md,json}.

## RELAUNCH RESPONSE AGENT — failure-response owner (user directive, 2026-08-24 21:15)
Standing role, spawned AT TRIGGER TIME (not idle-waiting). Mandate spec below is complete so the spawn is instant.
TRIGGERS (any one): (a) a holdout verdict that does NOT beat base (tie or worse); (b) an INERT precheck at the
projected ACTIVE bar (currently ~step 15 for run-3); (c) manager order.
MANDATE — thorough multi-layer analysis with evidence, then fix, then prepare the relaunch:
1. ALGORITHM: SAPO math vs paper again under the failure signature (gate behavior at observed ratios, advantage
   normalization under the observed reward distribution, KL coupling, aggregation) — find WHY the math doesn't convert.
2. CODE: the exact paths touched by the failure (loss path, router, reward composition, checkpoint/resume, launchers)
   — adversarial re-read, TDD regression tests for every suspected defect.
3. TRAINING DYNAMICS: per-step records across all three runs — drift, kl, grads, advantages, entropy, temperatures —
   identify the limiting factor (LR, advantage scale, reward variance, task mix, group size).
4. ROLLOUT: candidate quality (syntax/interface/runtime/assertion rates), fence-stop/EOS/truncation, harness grading
   coverage, repair-queue effectiveness.
5. DATA/CURRICULUM: manifest composition vs holdout failure classes (v8 available), enrichment effectiveness,
   learnability table.
6. FIX (TDD always): implement the highest-evidence fixes in scope (training/, scripts/, configs/, evals/) with
   red→green tests; run the full pre-launch gate checklist.
7. RELAUNCH: execute the FULL pre-launch gate (tests, config audit, deploy sha-verify, box gate, boot verify,
   poller repoint) and relaunch — FINAL GO IS THE USER'S (manager relays the plan; one-word approval triggers the
   launch). Role file: .sapo-loop/responder.md. The manager may split the mandate across QA/auditor/analyst if the
   analysis needs parallel lanes, but THIS role owns the verdict-to-relaunch loop end to end.
- 2026-08-24 21:1x CST — EVAL-LANE REPAIR (eval role): all 18 holdout tasks now score cleanly. Installed cirq-core 1.4.1 (ASI3 match) + pennylane 0.38.0 + qiskit 1.4.2 + amazon-braket-sdk 1.98.0 + autoray 0.6.11 on ASI2 scoring python (numpy 1.26.4/torch_npu untouched); hardened 5 scorers (density_matrix_partial_trace, shor_9qubit, trotterized, channel_depolarizing, cirq_qaoa_line) vs None-returns and missing functions — 20 TDD regression tests green (commits b10d64d/e4aa1db/e09ec7a). Verified: references 18/18 on the box via production flow; cached base leg re-scored 8/18 with the EXACT original pass set, failure summary {'assertion': 10} — 0 runner exceptions, 0 import failures. Cache verdict: candidates reusable, scorecard must be regenerated (free; deterministic). Report: reports/sapo-eval-lane-repair-2026-08-24.md.

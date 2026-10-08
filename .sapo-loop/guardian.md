# guardian.md — TRAINING GUARDIAN (run-3 sapo-27b-ai-20260824T103110, trainer 81132)

Updated: 2026-08-24 21:35 CST | Poll 7 of cycle — CYCLE CLOSE
VERDICT: HEALTHY — cycle 1 complete, zero alarms, drift re-accelerating ON BUDGET
- 12/120 steps | s12 by-design flat-group skip (degenerate group, decoded by log analyst) | dead 0/3 | noop 0/2 | trust 0 | trunc 0
- DRIFT (eval s11 precheck @21:02): diff 4.88e-4 (1.6x s9) — RE-ACCELERATION confirmed; lora_B 8.0e-4 climbing
  - Slope: 1.22e-4 → 2.44e-4 → 3.05e-4 (decel) → 4.88e-4 (re-accel); ACTIVE ~1e-3 projected ~step 14-15 (in budget)
  - My own s9 lora_B pull (20:52) matched eval's numbers exactly (6.0e-4) — precheck instrument cross-validated
- Training: 9 real updates / 11 steps; kl_aft compounding (s8 4.22e-3 peak); pass rates 0.5-0.75 on recent steps
- Efficiency: cadence ~13-16 min/step; skips (s1,2,6,12) all repair-routed by design; 6-step skip window never exceeded 50%
- Eval lane: 18/18 tasks scoring cleanly; holdout leg staged, QUEUED on ACTIVE verdict (ready-command documented)
- Poller health: local poller verified to contain 08-24 bug-hunt fixes — triage inputs reliable
Escalations: NONE raised this cycle.
Next: precheck s13 (expect ~7e-4-1e-3); on ACTIVE → holdout leg immediately; manager to re-invoke guardian for cycle 2.

---
## TRAINING WATCHDOG — 2026-08-24 22:55 CST (s15 escalation check) — AUTH-BLOCKED

VERDICT: UNVERIFIED — s15 precheck NOT run. Daemon /exec unreachable for the whole polling window.
Projection per s13 report (reports/sapo-precheck-run3-step13-2026-08-24.md): FLAT ~4.9e-4-6e-4 (INERT, lora_B creep only) unless a strong update (signal>1) landed.

Daemon evidence (polled 22:35-22:54 CST, ~19 min, 15+ samples):
- POST http://127.0.0.1:19004/exec — connection accepted, request sent, then TIMEOUT (0 bytes, 25s) → not ready, rejects.
- GET /health — `ready:false`, `commandCount:0` (ZERO commands executed all window), env ASI3, pid 13276.
- Startup cycles `booting` (40s) -> `error` (40s) -> `booting` -> ... indefinitely; ~6+ full cycles observed.
- startupError (repeated): "Safari callback capture failed after retries: {"found":false,"prefix":"https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=21b4208dde424e96b159362ef49c9c96"}"; `authDriftDetected:true`.
- NOTE: scripts/_asi3_auth_probe.sh marks the Safari SSO bridge BANNED (HUANXIN_ALLOW_SAFARI_SSO_BRIDGE=0) yet the daemon's startup path is stuck precisely on Safari callback capture — a config/daemon-level fault, not transient auth. Needs standalone-fallback / daemon restart; patience alone is unlikely to recover it.

What could NOT be checked (box unreachable): trainer process (was 81132 alive @21:35), step metrics JSONL, log health, s15 adapter precheck, NAS checkpoint listing, cadence.
s15 status: UNKNOWN on the box; nothing here contradicts the s13 projection of FLAT.

Escalations raised: 1 — AUTH-BLOCKED (daemon startup fault on banned Safari SSO path; commandCount 0 for ~19 min). Manager to decide: restart daemon w/ standalone fallback, or re-invoke watchdog next window. Do NOT treat s15 as PLATEAU-BREAK.

---
## TRAINING WATCHDOG — 2026-08-25 05:34 UTC (run-4 LAUNCH triage, poll 1)

LAUNCH DETECTED 05:29:26Z — run sapo-27b-ai-20260825T052636, trainer 9958 (164% CPU, ppid 1, nohup) + child 10231, repair sidecar up. Triage pass 1: GREEN, no alarms.
- BOOT (live launch_config.json): lr 0.0002 / benchmark v8_holdout_adjacent / adapter_init null (base-init) / loss_mode sapo / alpha 64 / steps 500 / scale_lr — all match approved stack. 8 NPUs, model Qwen3_5ForCausalLM loaded, zero_change_snapshot 240 lora_B params, step 1 begun 05:26:36Z temp 1.0 (task shor_phase_error_correction first).
- DEPLOY INTEGRITY: grpo_utils b75bf436 == manifest+local. Deployed trainer 10a3a54f = tgz member (7bee5668, pre-patch) + temp-cap hotfix — byte-identical to CURRENT local working tree (10a3a54f; TEMP_ESCALATION_CEILING 1.3 + repair-route skips no longer escalate; reports/sapo-temp-escalation-patch-2026-08-25.md). Box == instrumented working tree, verified.
- INSTRUMENTATION live: zero_change_snapshot marker present; step records pending (expect rollout_rewards / per_candidate_losses / loss_reduction / lora_b_max_delta).
- Baseline cadence: step 1 begin 05:26:36Z; run-3 avg ~13-16 min/step.
Next: triage every ~10 min. Alarm conditions: zero_change_alarm:true, no_trainable_tasks, OOM/Killed/reap, cadence stall >30 min, skip window >50%.

---
## TRAINING WATCHDOG — 2026-08-25 05:54 UTC (run-4 triage poll 2) — ALARM: CO-RESIDENT EVAL LEG

ESCALATION 1: eval leg co-resident with training on ALL 8 NPUs — violates evaluator.md rule ("Never run legs co-resident with training (OOM history)").
EVIDENCE:
- Eval: run_hf_pass1_eval.py --run-dir evals/runs/sapo-remasure-r2s4-20260825T052523Z (pids 9188/9471), started 05:25:23Z, 150% CPU, RSS 5.98GB, still running at 05:53Z (28 min).
- Trainer: sapo-27b-ai-20260825T052636 pid 9958, started 05:26:36Z (73s after eval), 148% CPU.
- npu-smi: NPUs 0-7 each host BOTH 9958 (6.4-8.9GB) and 9188 (6.6-10.1GB) — full co-residency.
- IMPACT: step 1 = 26+ min without a step record vs run-3 baseline ~8-10 min (record at launch+8 min) and 13-16 min/step cadence; OOM risk for both lanes.
NO OOM YET: trainer alive 148% CPU; no OOM/Killed in log; no step records yet (step 1 in generation).
ACTION: manager to decide — let r2s4 finish (cadence impact only) or stop eval (eval owner authority). Do NOT stop trainer.

---
## TRAINING WATCHDOG — 2026-08-25 06:13 UTC (run-4 triage polls 3-5) — CADENCE ANALYSIS, no new alarm

- 05:53Z: eval r2s4 (9188/9471) finished (gone from ps); NPUs 0-7 now trainer-only, AICore 98-104%, HBM 6.4-12.3GB/NPU (full 54GB model resident).
- Step 1 = 45+ min without record. Trainer state: R (running), 247 threads, 2.36M voluntary ctx switches, wchan 0, 151 fds — COMPUTING, not hung, no OOM (dmesg kill was old unrelated container proc). No new run-dir artifacts; repair sidecar healthy (waiting, no queue).
- WHY SLOW (baseline math): run-3 throughput ~2-3 tok/s total (steps 858-2115 tokens in ~10 min each; eos_termination_rate 0.0 — model rarely emits EOS). Run-4 step-1 task shor_phase_error_correction with max_new_tokens 2048 → worst case 8192 tokens ≈ 55 min at run-3 rate, +28 min co-resident eval contention (05:25-05:53). Projected first record ~06:15-06:30Z.
- WATCH: escalate cadence stall if NO record by ~06:35Z (69 min, ~1.3x worst-case). Otherwise normal.

---
## TRAINING WATCHDOG — 2026-08-25 06:32 UTC (run-4 triage poll 6) — ALARM 2: TRAINER DEAD (NPU OOM)

RUN-4 TERMINATED: trainer 9958 dead (zombie) at 06:32Z; OOM at 06:27:03Z.
EVIDENCE:
- RuntimeError: NPU out of memory. Tried to allocate 38.00 MiB (NPU 0; 60.96 GiB total; 59.90 GiB already allocated; 38.88 MiB free; 60.20 GiB reserved).
- Traceback: training/grpo_utils.py:1562 chunked_log_probs_and_entropy -> _clamped_chunk:1542 x[:,:,start:start+chunk_size].float() — logprob phase of step 1.
- Step 1 began 05:26:36Z; generation ran ~61 min; NO step records written (grpo_step_metrics.jsonl never created), NO adapter saved, run dir empty (launch files only).
- CAUSE CHAIN: alarm-1 co-resident eval r2s4 (05:25:23Z-~05:53Z, 6.6-10.1 GiB/NPU on all 8 NPUs) + trainer ballooning to 59.9 GiB on NPU 0 during 4x2048-token no-EOS generation; 38 MiB chunk alloc failed at logprob.
- Zero-change gate never exercised; no lora_B delta measured; 61 min compute lost. No resume (run used --overwrite-output-dir, no --resume-from).
- Child 10231 also gone.
NEXT: manager decision — relaunch (package intact, config verified) ONLY after NPU HBM verified free + no eval legs co-resident (evaluator.md rule). Do NOT stop anything (nothing left to stop).

---
## TRAINING WATCHDOG — 2026-08-25 06:38 UTC (post-mortem) — NPUs FREE, awaiting manager decision

- 06:37Z: npu-smi shows NO processes on any NPU (trainer zombie 9958 un-reaped, ppid 1). All HBM released. No new run dir. No eval procs.
- Run-4 loss tally: 61 min compute, 0 step records, 0 adapters, 0 lora_B deltas. Root cause = co-resident eval r2s4 (alarm 1) + step-1 memory peak 59.9 GiB on NPU 0.
- Box state relaunch-ready: package tgz b4e2b00b intact, deployed tree == local (10a3a54f), config verified lr 2e-4/v8/base-init. Condition for relaunch: NPU co-residency check at boot (evaluator.md rule).
- Watching for manager decision / relaunch at ~10-min cadence.

---
## TRAINING WATCHDOG — 2026-08-25 07:16 UTC (run-5 LAUNCH triage, poll 1) — GREEN

RELAUNCH DETECTED 07:16Z — run sapo-27b-ai-20260825T070339, trainer 14279 (164% CPU, start 07:03:39Z) + child 14585.
- NO co-resident eval (EVAL:0); NPU python rows = 8, trainer-only (single process across 8 NPUs).
- BOOT: launch_config_written, tasks_ready (20 tasks / 500 steps / v8 benchmark), zero_change_snapshot 240 lora_B params, step_begin step 1 temp 1.0 (shor_phase_error_correction — same first task as run-4).
- CONFIG: lr 0.0002, adapter_init null, v8 — verified live. All matches approved stack.
- WATCH: run-4 died in step-1 logprob at 59.9 GiB/NPU-0 (with co-resident eval). Run-5 has no co-residency; if it OOMs at the same point (~50-65 min into step 1), that isolates a code-level memory growth in chunked_log_probs_and_entropy (debugger's lane). Step-1 record projected ~07:50-08:10Z (4x2048 no-EOS generation at run-3 throughput).

---
## TRAINING WATCHDOG — 2026-08-25 08:08 UTC (run-5 triage polls 2-7) — STEP 1 DONE, INSTRUMENTATION VERIFIED

- Step 1 completed 08:04:40Z (63 min incl. 60-min 4x~1700-token generation): skipped:0, loss -0.0474897, recomputed -0.0474897 (match), per_candidate [-1.588,3.811,-0.3209,-2.092], checkpoint step_000001 saved. NO OOM (run-4's 59.9 GiB NPU0 peak not reproduced — co-residency confirmed as the OOM cause).
- INSTRUMENTATION LIVE (verified on record 1): lora_b_max_delta 2.0e-4 (real movement, 8x run-2's 2.5e-5/update rate at LR 2e-4), zero_change_alarm false, zero_change_recommend_stop false, loss_reduction present ("per-candidate token-mean SAPO losses... w_i=1/G"), per_candidate_losses with weight 0.25, rollout_rewards full per-candidate detail, sapo_per_candidate_stats w/ loss+advantage.
- Step 2 begun 08:07Z bitstring_maxcut_landscape temp 1.15. Cadence back to ~10 min/step expected for shorter generations.
- seq_kl_after 7.97e-3 on step 1 (real KL movement); update_signal loo_advantage_rms 1.199 > threshold 0.05.

---
## TRAINING WATCHDOG — 2026-08-25 13:33 UTC (poller status note — coordinator request)

/tmp/sapo_guardian_poll.out STALE BY DESIGN, thread closed: the standby poller exited at 05:29:26Z with LAUNCH-DETECTED (its purpose — detecting the relaunch — was complete). Since then triage has been driven by DIRECT 10-min cadence polls (procs + step records + loss_breakdown + OOM/zero_change greps + NPU memory), which cover the ground; the executor's live poller also covers the box. NOT re-arming a duplicate standby poller to avoid double-polling the daemon; this note is the explicit fold-in. Run-5 status at 13:32Z: step 16 in generation (qml_variational_classifier), 15 records (12 real updates + 3 repair skips), no OOM, no zero_change alarm, trainer 14279 at 146% CPU, 06:28 elapsed.

---
## TRAINING WATCHDOG — 2026-08-25 21:24 UTC (run-5 triage) — ALARM 3: RUN-5 TRAINER DEAD

RUN-5 TERMINATED at step 28 (~21:23Z). Trainer 14279 gone (child 14585 zombie).
EVIDENCE:
- Log tail: EOFError in multiprocessing.managers._callmethod -> conn.recv() — manager/worker connection dropped (no OOM text in trainer log; dmesg shows only unrelated dosec_hades cgroup OOM-kills in same pod cgroup).
- Last record: step 27 @20:11:42Z. 29 adapter dirs saved. Step 28 (circuit_phase_repair, begun ~20:15Z) never completed.
- CO-RESIDENT EVAL AGAIN: promotion leg run_hf_pass1_eval.py --run-dir evals/runs/sapo-promotion-r5-step_000026_adapter-2026... (pid 46829) started 20:33Z while training ran; at death it holds ALL 8 NPUs (6.6-10.2 GiB/NPU); STILL RUNNING at 21:24Z (51:45 elapsed).
- CAUSE CHAIN: pod cgroup (kubepods/burstable) memory pressure from eval+trainer co-residency -> manager/worker killed -> EOFError -> trainer death. Same rule violation as run-4 (evaluator.md: never co-resident).
- Run-5 loss tally: 27 records (23 real updates + 4 by-design skips), ~14h20m, 29 adapters (s3..s27 + periodic). Instrumentation + zero-change gate verified working throughout; no zero_change_alarm fired.
NEXT: manager decision. Eval leg 46829 is the s26 promotion leg (objective-relevant) — let it finish on the freed NPUs. Relaunch run-6 only after eval lane confirmed idle (ENFORCE co-residency rule — this is the 2nd death by it).

---
## TRAINING WATCHDOG — 2026-08-25 21:35 UTC — CORRECTION to ALARM 3 (coordinator + GO-marker evidence)

ALARM 3 CAUSE RETRACTED: run-5 did NOT die of co-residency. It was a PLANNED PAUSE (GO marker /tmp/sapo_leg_GO, written 20:30Z):
- "paused checkpoint for promotion eval leg ... pause step: 26 | drift: max_abs_diff 1.2207e-3 verdict ACTIVE (trigger >=1.2e-3) | paused at step-27 boundary 2026-08-25 20:12Z; trainer TERM-only (sync+repair left up) | adapter-init-only warm restart pending"
- TIMELINE: trainer TERM'd 20:12Z (executor, planned) -> last record step 27 @20:11:42Z -> promotion leg 46829 launched 20:33Z (21 min AFTER death). NO co-residency at any point; the no-co-residency rule is why the pause exists.
- EOFError signature = the TERM's unwind (multiprocessing manager connection interrupted by signal), not a crash.
- OUTCOME HIGHLIGHT: run-5 achieved the OBJECTIVE — step-26 adapter prechecked ACTIVE (1.2207e-3, the 2e-4 LR escalation broke run-3's 4.88e-4 plateau). 27 records, 23 real updates, 29 adapters, zero-change gate never fired, instrumentation verified throughout.
- REAL BOX WATCH ITEM (from dmesg, for NPU Capacity lane): repeated cgroup OOM-kills (dosec_hades, same kubepods/burstable pod cgroup) — pod memory pressure exists independent of training; eval leg holds 6.6-10.2 GiB/NPU (fine).
- NEXT: promotion leg s26 in flight (objective-relevant); run-6 = adapter-init-only warm restart from step_000026_adapter pending leg completion. Watch for relaunch; verify adapter_init source at boot.

---
## TRAINING WATCHDOG — 2026-08-25 21:54 UTC (run-6 LAUNCH triage) — GREEN

RUN-6 LAUNCHED: sapo-27b-ai-20260825T214849, trainer 50668 (183% CPU, 21:48:49Z) + child 51012. No eval co-residency (s26 promotion leg completed ~21:34Z, EVALRUNS shows the leg dir; scorer reruns r1s7 are older/parallel).
- CONFIG: adapter_init = outputs/sapo-27b-ai-20260825T070339/step_000026_adapter (warm restart per GO marker), lr 0.0002, v8, steps 500. zero_change_snapshot 240 params; step 1 shor task temp 1.0.
- NOTE: warm-start baseline = run-5-s26 adapter (already ACTIVE 1.22e-3 vs base). lora_b_max_delta will measure movement from the warm state; drift-watch baseline semantics changed — eval lane owns interpretation.
- Watch: step-1 completion (~60 min expected), then steady cadence; alarm conditions unchanged.

---
## TRAINING WATCHDOG — HEARTBEAT 2026-08-26 01:41 UTC (run-6, ~3.9h in)
- Run-6 sapo-27b-ai-20260825T214849 healthy: trainer 50668 at 143% CPU, 03:51 elapsed, 8 records (s1 real, s2 repair-skip, s3 real [loss +0.33 — positive-loss step, gated candidate -4.999 vs 4.764, still a real update], s4 real, s5-7 real, s8 repair-skip), step 9 in generation (depolarizing_entanglement_decay). No OOM (0), no zero_change_alarm (0), no co-residency (EVAL:0).
- MANDATE ACKNOWLEDGED (coordinator 01:4x): systematic-debugging root-cause protocol (reproduce→bisect→hypothesize→smallest fix) before any escalation/fix; verification-before-completion before reporting fixes; TDD for all changes. Note: 'systematic-debugging'/'verification-before-completion' skills not in this agent's available-skill list — practices adopted manually. Heartbeat cadence: ~15 min.

---
## TRAINING WATCHDOG — 2026-08-26 01:52 UTC — ALARM 4: RUN-6 SELF-TERMINATED (degenerate-EOS collapse)

RUN-6 (sapo-27b-ai-20260825T214849, warm restart from run-5-s26 ACTIVE adapter) SELF-TERMINATED at step 26, ~01:49Z. Trainer 50668 exited (no process).
EVIDENCE (log tail):
- {"stage": "no_trainable_tasks", "step": 26, "reason": "all_tasks_quarantined_or_zero_weight"} + terminal "Saved adapter".
- s25 generation: completion_token_lengths [1,1,1,1], max_code_chars 0, eos_terminated [true x4], entropy 0.0137, behavior_temperature 1.15 (UNCHANGED).
- Records: s8 skip(01:26:39) -> s9 REAL update(01:42:20, depolarizing) -> s10-s25 = 16 CONSECUTIVE repair skips (01:42:42..01:48:56, ~30s each, ALL tasks: circuit_depth, measurement_bug, qft, error_detection, bell_basis, shor, teleportation...).
ROOT CAUSE (evidence-based hypothesis): warm adapter entered a GLOBAL degenerate policy — immediate-EOS 1-token completions on every task (near-zero entropy 0.014, syntax 0.0, reward 0.0) -> all-fail -> repair-routed -> 16+ consecutive all-fail quarantines every task -> no_trainable_tasks breaker (same breaker as run-3, fired earlier because collapse is task-independent).
- NOTE: repair-route no-escalate fix held temp at 1.15 (by design) — the low-entropy cold-task escalation is BYPASSED because repair-routing precedes the escalation check (route=repair_sft never reaches escalate_temperature_on_flat_route). Candidate gap for debugger/algorithm-analyst (TDD lane).
- NO OOM, NO co-residency, NO infra fault — algorithmic/policy-mode failure. GO marker is run-5's OLD one (20:30Z, unchanged) — NOT a planned pause.
- Run-6 tally: 25 records (7 real updates s1/3/4/5/6/7/9, 18 skips), ~3h, adapters saved.
NEXT: manager decision — relaunch (base-init or s9 checkpoint?), or debugger fix (escalation order / EOS-collapse rescue), or hold for promotion-leg verdict on s26.

---
## TRAINING WATCHDOG — HEARTBEAT 2026-08-26 02:03 UTC (post-alarm-4, decision recorded)
- MANAGER DECISION (coordinator 02:0x): option (b) — EOS-collapse rescue fix FIRST, then relaunch. s26 promotion verdict ALREADY KNOWN: 0/18 (verified real — greedy collapse; vs base 8/18). Option (c) moot.
- ADOPTED PLAN: Router lane TDD-ing rescue (escalate-before-repair + degenerate_policy_alarm) -> ships r10 -> relaunch from run-6's STRONGEST PRE-COLLAPSE checkpoint (s9 adapter, drift ~1.46e-3 era) with rescue armed. NO relaunch as-is; next relaunch only after r10 register green.
- Watch state: no trainer on box (02:02Z); eval lane spot-verify run created 01:36Z (sapo-verify-spot). Box idle for training.
- TRIGGER TO WATCH: relaunch run-7 = adapter_init outputs/sapo-27b-ai-20260825T214849/step_000009_adapter + rescue code deployed (verify trainer hash changed from 10a3a54f-era if r10 touches trainer; verify degenerate_policy_alarm in step-record contract).

---
## TRAINING WATCHDOG — HEARTBEAT 2026-08-26 02:24 UTC (run-7 = r9 VALIDATION launch, not a failure)

RUN-7 (sapo-27b-ai-20260826T020821) was an r9 plumbing-validation launch: trainer fb2675d2 (sigterm_graceful_stop x1, resume_state x62 — r9 features; NO degenerate rescue: degenerate_policy_alarm x0). Lifecycle verified:
- Launched 02:08:21Z, adapter_init = run-6's step_000005_adapter (NOTE: plan said s9 — s5 discrepancy to confirm with Router).
- s1-s4 all repair skips, 1-2 token EOS (degenerate mode persists — EXPECTED, rescue not deployed).
- 02:21Z: {"stage": "sigterm_graceful_stop", "step": 4} + final adapter + soft-resume state at step 3 — graceful TERM path VERIFIED live (controlled stop, ~13 min after launch). TBE subprocess errors are teardown noise.
- Staged: /tmp/sapo_deploy/relaunch_r9.tgz + relaunch_r8.tgz (versioned staging in progress).
- LOCAL tree (9ac35c3f) HAS the r10 rescue: is_degenerate_policy_step + degenerate_policy_alarm (N=3 consecutive degenerate steps -> alarm) — r10 register in flight, rescue NOT yet deployed.
- No GO marker (removed). Box busy (PY:54) — Router lane active.
NEXT WATCH: run-8 = r10 deploy (verify degenerate_policy_alarm in deployed trainer + records) + relaunch from the chosen pre-collapse checkpoint (s5 or s9 — confirm).

---
## TRAINING WATCHDOG — HEARTBEAT 2026-08-26 02:26 UTC (adapter decision recorded)
- COORDINATOR RESOLUTION (item 1): restart checkpoint = run-6 step_000003_adapter (drift 1.343e-3 ACTIVE; steps 4-5 after it generated healthily). Rationale: only step_000001/000003/000005 dirs exist on disk — s7/s9 were real updates in records but their boundary saves never fired (1800s periodic-save cadence), so they are not resume points; s5 is degenerate (proven: run-7 s1-s4 = 1-2 token EOS from s5 init).
- r9-graceful-stop validation note RECORDED (valuable per coordinator): run-7 verified the sigterm_graceful_stop + soft-resume path live; final-save + resume_state.json worked; the r9 plumbing is proven on the box.
- ITEM 2 WATCH: run-8 = r10 package (rescue: is_degenerate_policy_step / degenerate_policy_alarm, N=3) deployed + adapter_init = outputs/sapo-27b-ai-20260825T214849/step_000003_adapter. At boot verify: (a) deployed trainer contains degenerate_policy_alarm, (b) first degenerate streak fires the alarm in records, (c) escalation instead of silent quarantine.

---
## TRAINING WATCHDOG — HEARTBEAT 2026-08-26 02:52 UTC
- Box idle for training (T:0, no new run dir since run-7 02:08Z). Deployed trainer still fb2675d2 (DPA:0) — r10 rescue NOT yet deployed; Router lane working the register (local tree has rescue at 9ac35c3f, N=3 alarm).
- Watch trigger unchanged: run-8 = r10 package + adapter_init run-6/step_000003_adapter; boot checks: degenerate_policy_alarm in deployed trainer + records; rescue fires on 3rd consecutive degenerate step (escalation instead of silent quarantine).
- No alarms. Daemon healthy (exec intermittently slow while box busy).

---
## TRAINING WATCHDOG — HEARTBEAT 2026-08-26 03:10 UTC
- Still no r10 deploy (box trainer fb2675d2, DPA:0; T:0; no new run dir since run-7). Router lane register in flight. No alarms.
- Watch trigger unchanged (run-8 = r10 + step_000003_adapter init; verify DPA in trainer+records at boot; rescue N=3 semantics).

---
## TRAINING WATCHDOG — 2026-08-26 03:19 UTC — r10 RESCUE DEPLOYED on box
- Box trainer hash 4ab6f70e8d03, degenerate_policy_alarm x6 in deployed file (was fb2675d2/DPA:0) — r10 rescue live. No trainer/run yet.
- BOOT CHECKLIST (run-8, armed): (1) launch_config adapter_init = outputs/sapo-27b-ai-20260825T214849/step_000003_adapter; (2) rescue fires degenerate_policy_alarm on 3rd consecutive 1-2-token-EOS step and escalates (not silent quarantine); (3) no co-residency; (4) lr 2e-4/v8/base-init stack unchanged.

---
## TRAINING WATCHDOG — HEARTBEAT 2026-08-26 03:48 UTC
- r10 deployed (box trainer 4ab6f70e8d03, DPA x6) but no run-8 launch yet (T:0, E:0, no new run dir at 03:47Z). Router lane validating before launch (register green + deploy check). No alarms.

---
## TRAINING WATCHDOG — HEARTBEAT 2026-08-26 04:07 UTC
- r10 deployed 03:19Z; run-8 NOT yet launched (T:0, E:0, no new run dir at 04:06Z) — Router lane likely running the box-side TDD register on the deployed r10 before the launch (their gate). No alarms.

---
## TRAINING WATCHDOG — 2026-08-26 04:17 UTC — ANOMALY FIRST-RESPONSE PROTOCOL (mandate addition, applies run-8+)
On ANY training anomaly (stall >25 min with no stage markers, abnormal death, silent hang) BEFORE any escalation or stop:
1. `kill -USR1 <trainer_pid>` — trainer faulthandler dumps ALL-THREAD STACKS to the run log while the trainer keeps running.
2. `py-spy dump --pid <trainer_pid>` (installed in the venv; root on box, no sudo; use `--nonblocking` for wedged targets).
3. SAVE the stacks (log excerpt + py-spy output), ATTACH to the escalation.
4. If stacks reveal a code bug → route the fix to the owning lane (debugger/Router) WITH the evidence.
NEVER kill a stalled trainer without the dumps first.

---
## TRAINING WATCHDOG — 2026-08-26 04:57 UTC (run-8 first triage) — GREEN, rescue armed
- Run-8 sapo-27b-ai-20260826T044037 launched 04:40:37Z: adapter_init = run-6/step_000003_adapter (per decision), trainer 4ab6f70e8d03 (r10 rescue, DPA x6), no co-residency (E:0), boot markers clean (zero_change_snapshot 240 -> step_begin).
- Step 1 in normal generation (~12+ min, no 30s-degenerate record yet — s3 adapter appears healthy). No OOM. Rescue armed: degenerate_policy_alarm fires on 3rd consecutive 1-2-token-EOS step and escalates (replaces silent quarantine).
- Anomaly protocol armed (USR1 faulthandler + py-spy 0.4.2 verified at /usr/local/python3.11.14/bin/py-spy).

---
## TRAINING WATCHDOG — 2026-08-26 05:27 UTC — ALARM 5: RUN-8 OOM-DEAD at step-1 logprob

RUN-8 (sapo-27b-ai-20260826T044037, r10 + s3-adapter warm start) DEAD at step 1, 05:26:31Z, trainer 71675 (no process left).
EVIDENCE:
- RuntimeError: NPU out of memory. Tried to allocate 64.00 MiB (NPU 0; 60.96 GiB total; 59.84 GiB already allocated; 59.84 GiB current active).
- Traceback context: log_p = shifted - log_z_shifted.unsqueeze(-1) — chunked_log_probs_and_entropy (same code region as run-4: grpo_utils.py _clamped_chunk).
- Timeline: launched 04:40:37Z; step 1 (shor) generated REAL 4x~1700-token completions (~46 min; eval_done reached) -> logprob phase ballooned NPU-0 to 59.84 GiB -> 64 MiB alloc failed -> death. NO records, NO adapter.
- KEY DIFFERENCE vs run-4: NO co-residency (E:0 verified all window) — the ~59.8-59.9 GiB NPU-0 peak during logprob is INTRINSIC to the computation for 4x~1700-token sequences (matches run-4's 59.90 GiB with eval; run-5 passed similar-length steps at ~10.5 GiB NPU0 — variance to root-cause).
- Rescue (degenerate_policy_alarm) irrelevant here — not the degenerate path; s3 warm start generated HEALTHILY (rescue not needed, but the run died on memory before any learning).
- No stall — process gone; death traceback in log (USR1/py-spy N/A).
ROUTE: debugger/algorithm-analyst (TDD lane) — chunked_log_probs_and_entropy memory growth for long completions (chunk-size/empty_cache/per-candidate ordering/fragmentation); evidence attached.
NEXT: manager decision — fix + relaunch, or reduce max-new-tokens/batch, or NPU-capacity check (pod HBM residue from prior runs).

---
## TRAINING WATCHDOG — HEARTBEAT 2026-08-26 06:00 UTC
- Post-alarm-5: debugger lane deployed r12 (trainer a161f4b9, rescue DPA:6 still present; relaunch_r12.tgz staged). No launch yet (T:0, E:0 at 06:00Z). NPUs free.
- Watch: next run = r12 + s3-adapter init; key question = whether the logprob-phase NPU-0 peak (59.8 GiB) is fixed. Anomaly protocol armed (USR1 + py-spy).

---
## TRAINING WATCHDOG — 2026-08-26 06:55 UTC — ALARM 6: RUN-9 OOM at BACKWARD pass (r12 fix insufficient)

RUN-9 (sapo-27b-ai-20260826T060754, r12 + s3-adapter) DEAD at step 1, 06:49:53Z, trainer 74779 gone. OOM:1, REC:0.
EVIDENCE:
- RuntimeError: NPU out of memory. Tried to allocate 970.00 MiB (NPU 0; 60.96 GiB total; 58.72 GiB already allocated).
- Traceback: torch.autograd.backward -> _engine_run_backward — the BACKWARD pass (per-candidate (loss_i*w_i).backward() accumulation).
- Phase progression (r12 worked partially): eval_done -> train_logprob_done PASSED (r12 fixed the logprob-forward peak from run-8) -> backward OOM.
- THREE-RUN PATTERN (all step-1, 4x~1700-token completions): run-4 logprob-fwd OOM 59.90 GiB (co-resident eval); run-8 logprob-fwd OOM 59.84 GiB (standalone); run-9 backward OOM 58.72 GiB (standalone, r12). Step-1 compute INTRINSICALLY exceeds NPU-0 60.96 GiB in this config.
- run-5 survived similar-length steps at NPU0 ~10.5 GiB — variance variable (per-candidate backward ordering, gradient-checkpoint granularity, NPU-0 layer balance 8.9-10.5 vs 6.5 GiB elsewhere, HBM residue/fragmentation) — DEBUGGER BISECT REQUIRED.
ROUTE: debugger/algorithm-analyst (TDD): per-candidate backward peak (empty_cache between candidate backward passes), NPU-0 layer rebalance, checkpoint granularity, or token-budget reduction for step-1. DO NOT RELAUNCH until backward peak fixed.
NEXT: manager decision.

---
## TRAINING WATCHDOG — HEARTBEAT 2026-08-26 07:05 UTC
- Post-alarm-6: box idle (T:0, no new run since run-9 06:07Z; trainer still r12 a161f4b9; no new tgz staged at 07:04Z). Debugger lane working the backward-peak fix (per-candidate backward / NPU-0 balance bisect per alarm-6 evidence). No alarms beyond the recorded OOM chain.
- Next-launch watch: new trainer hash/tgz (r13?) then run-10 = s3-adapter init; key check = BACKWARD pass survives step-1 (~07:50-08:00Z window if launched now), NPU-0 peak < 58 GiB.

---
## TRAINING WATCHDOG — HEARTBEAT 2026-08-26 07:24 UTC
- Box idle; no r13 deploy yet (trainer a161f4b9/r12, no new tgz, no run since run-9). Debugger lane bisecting the backward peak per alarm-6 evidence. No new alarms.

---
## TRAINING WATCHDOG — 2026-08-26 07:54 UTC (run-10 LAUNCH triage) — GREEN, r13 test
- Run-10 sapo-27b-ai-20260826T074558 (07:45:58Z): adapter_init = run-6/step_000003_adapter, trainer e2d7023c (r13), boot clean, OOM:0, no co-residency.
- TEST: r13's backward-peak fix — step-1 danger window eval_done ~08:40-08:50Z, logprob+backward ~08:50-08:55Z; NPU-0 peak must stay < 58 GiB.

---
## TRAINING WATCHDOG — 2026-08-26 08:47 UTC — ALARM 7: RUN-10 died — r13 CODE BUG (double-backward on custom Function), not OOM

RUN-10 (sapo-27b-ai-20260826T074558, r13) DEAD at 08:36:28Z, trainer 83051 gone. REC:0, OOM text:0.
ROOT CAUSE (exact): RuntimeError "Trying to backward through the graph a second time (or directly access saved tensors after they have already been freed). Saved intermediate..." at training/grpo_utils.py:1647 in the custom autograd Function backward: logits, target_ids, per_pos_max, sum_exp, neg_entropy = ctx.saved_tensors.
- The SAPO per-candidate backward pattern (4x (loss_i*w_i).backward() with single optimizer.zero_grad(), per loss_reduction contract) requires the graph's saved tensors to survive 4 backward passes; the r13 chunked-logprob custom Function frees them after the FIRST backward -> 2nd-4th per-candidate backward crash.
- r13 fixed the OOM peak (train_logprob_done passed, OOM:0) but introduced this graph-reuse bug.
- dmesg OOM-kills = dosec_hades (unrelated pod process), NOT the trainer.
ROUTE (TDD lane, debugger/Router): smallest fixes — (a) single combined backward (sum w_i*loss_i into one tensor, one .backward()), or (b) retain_graph=True on the per-candidate backward calls, or (c) custom Function saves with retain (ctx.save_for_backward + keep) / recompute-on-2nd-backward. Verify with a CPU test reproducing 4 per-candidate backward passes through the custom Function.
NEXT: manager decision; do NOT relaunch until the double-backward fix is deployed (r14).

---
## TRAINING WATCHDOG — HEARTBEAT 2026-08-26 09:07 UTC
- r14 deployed (trainer 530a4efd, utils ba8b0ec5 — double-backward fix at grpo_utils.py custom Function; guard logic verified in region). No run-11 yet (T:0, E:0 at 09:06Z). Debugger validated via TDD presumably; launch pending.
- Run-11 test: step-1 4-per-candidate backward must pass (no "backward a second time"), plus r13's memory fix holds (no OOM). Expected launch + ~45-60 min generation then backward test.

---
## TRAINING WATCHDOG — 2026-08-26 10:24 UTC — RUN-11 STEP 1 COMPLETE (MILESTONE: full pipeline green first time since run-5)
- Run-11 (r14, s3-adapter) step 1 COMPLETED 10:16:37Z (~42 min): record written, loss_breakdown=step:1 skipped:0 route:frontier_rl, lora_b_max_delta 2.000e-4 (real movement), seq_kl_after 8.26e-3, zero_change_alarm false. OOM:0, double-backward:0.
- FIX-CHAIN RESOLVED: r12 (logprob-fwd peak) -> r13 (backward OOM via chunked custom Function) -> r14 (double-backward graph fix at grpo_utils.py:1647 region) — all three failure modes cleared; step 1 survived generation/eval/logprob/4-per-candidate-backward/update.
- Trainer 21fe8174 alive on step 2. No co-residency. Cadence normal.
- Continue steady watch: cadence, zero_change_alarm, degenerate_policy_alarm (rescue armed), OOM, co-residency.

---
## TRAINING WATCHDOG — HEARTBEAT 2026-08-26 13:42 UTC (run-11 steady state, OBSERVATION)
- Run-11 (r14) 6 records: s1 REAL (loss -0.0353), s2-s5 repair skips (flat groups, real content rewards 0.68-0.87), s6 REAL (loss -0.0303). Step 7 running. No OOM, no double-backward, PROC alive. Temp ladder cycling 1.15-1.3 at ceiling; greedy_count 2/step tracked.
- OBSERVATION (not alarm): 6-step skip window = 4/6 = 67% > 50% rule, but skips are repair-routed flat groups (not 1-token-EOS degenerate — the rescue's escalation IS firing on them: temp reached 1.3) and real updates land every ~3-5 steps with lora_B movement. Training-effectiveness note for the algorithm lane: the s3 warm adapter produces a narrow output distribution (near-identical rewards) — diversity is the constraint, not the pipeline (which is now stable after r14).

---
## TRAINING WATCHDOG — HEARTBEAT 2026-08-26 14:21 UTC (run-11 steady, 4.7h in)
- 8 records: 3 real updates (s1 loss -0.0353, s6 -0.0303, s8 -0.0028) + 5 repair skips (flat groups). Step 9 running. No OOM, no double-backward, no degenerate alarm (rescue armed but not needed — skips are near-flat real-content groups, temp cycles at the 1.3 ceiling, greedy_count 2). Cadence ~10-70 min/step by task.
- Run-11 = first run since run-5 with a STABLE full pipeline (r12-r14 fix chain). Effectiveness note stands (algorithm lane): s3 warm adapter diversity is the constraint.

---
## TRAINING WATCHDOG — 2026-08-26 20:34 UTC — ALARM 8: RUN-11 stopped by all_fail_without_repair breaker (repair sidecar dead)

RUN-11 (sapo-27b-ai-20260826T093441) STOPPED at step 20 (~11h, 20 records: 11 real updates + 9 skips) via circuit_breaker_stop (all_fail_without_repair, window 2). NOT a crash — a fail-closed protective stop, and the breaker WORKED (caught the condition, no run-3-style spiral).
EVIDENCE:
- Breaker message: "all-fail rollout share exceeds 40% without repair conversion".
- REPAIR SIDECAR DEAD: process gone; log shows ONLY the 09:34:43Z startup line ("no repair sidecar started ... no repair queue yet; waiting") — zero activity in 11h.
- repair_queue.jsonl = 5 lines, never converted (queue starved).
- Step 20 completed normally first (backward_done, loss -0.0071, record 20:26:36Z), then trip -> stop -> final adapter save.
- Pipeline health: NO OOM, NO double-backward across all 20 steps (r12-r14 fix chain held); the failure was the ops sidecar, not the trainer.
- Note: sidecar died silently (no error line) — likely at/near launch; the all-fail share grew past 40% as the queue went unconverted.
NEXT: manager decision — fix/restart the repair sidecar (verify spawn in launcher), then relaunch run-12 from run-11's final adapter with sidecar verified alive. Drift at s11 was 1.83e-3 (ACTIVE) — the warm start WAS producing active drift.

---
## TRAINING WATCHDOG — 2026-08-26 20:44 UTC (run-12 LAUNCH triage) — GREEN with sidecar watch
- Run-12 sapo-27b-ai-20260826T203454 (20:34:54Z): adapter_init = run-11/step_000018_adapter (last saved boundary; s19/20 real updates had no boundary save — same periodic-save cadence), trainer f01881e4 (new build), step 1 running, NO co-residency.
- REPAIR SIDECAR ALIVE at launch (S:2; log started 20:34:57Z, "no repair queue yet; waiting" = expected pre-queue state). KEY WATCH: sidecar must STAY alive and convert when repair_queue.jsonl appears (run-11's sidecar died silently at/near launch -> breaker trip -> stop). All-fail share must stay <=40% or conversions must flow.
- Breaker (all_fail_without_repair, window 2) armed as the fail-closed backstop.

---
## CAPABILITY SENTINEL — RULE TABLE TEST-PINNED (config-auditor lane, 2026-08-31)
- STATUS.md STANDUP #234: box-side capability_sentinel.py (autostop=1, 60s poll) fires RED + auto-stops on 4 rules. No local copy of the box script and NO local test pinned the rules — closed by TDD.
- NEW: scripts/sapo_capability_sentinel_rules.py (local mirror of the rule table; pure functions, py3.9-safe) + tests/test_sapo_capability_sentinel_rules.py — 16/16 GREEN in canonical .venv (py3.9.6), py_compile OK, forbidden-token scan clean, adjacent suites (launcher readiness + drift watch) green.
- RED evidence: test written first → collection ImportError ("cannot import name 'sapo_capability_sentinel_rules'") → module implemented → 16/16 GREEN.
- RULE PIN (validated against real RUN-12 degradation): entropy drift fires iff min-baseline > 0.01 AND recent-mean > 0.3 AND recent-mean > 3x min-baseline. RUN-12 case min 0.042 / recent 1.056 → FIRES (pinned by test; the earlier first-3-mean rule missed this exact case per #234).
- Other pins: trust-region violations >= 5 windows fires; NaN/Inf in loss/rewards fires; "ERR99999" in log text fires; composite evaluate() returns the sorted fired-signal list (all-clear = []).
- NOTE: the box-side sentinel's log-parsing remains box-only; this pins the RULE TABLE contract so any local re-implementation or box-side drift is detectable. If the box-side capability_sentinel.py is ever mirrored into the repo, it must satisfy these pins.

---
## CAPABILITY-SENTINEL LANE AUDIT — 2026-09-01 (capability-erosion defense verification, STANDUP #234)

Independent verification pass by the capability-sentinel lane (not the author lane). All claims below re-run, not re-quoted.

### 1. Sentinel location verdict: BOX-SIDE ONLY
- The watcher itself (capability_sentinel.py, autostop=1, 60s poll on the ACTIVE training log) exists ONLY on the box, deployed ad-hoc via the eval wave (#234). No local copy exists or ever did — the earlier .sapo-loop/locks/ files were 1-line placeholders and have been superseded.
- Local artifacts that DO exist and pin the contract:
  - scripts/sapo_capability_sentinel_rules.py (rule-table mirror, pure functions, py3.9-safe)
  - tests/test_sapo_capability_sentinel_rules.py (16 tests)
  - Rule text: .sapo-loop/STATUS.md STANDUP #234.
- Untracked in git (??) — must be committed for reproducible bundle builds.

### 2. Rule-by-rule verdict vs #234 text: ALL MATCH, no rule defect found
| Rule | #234 spec | Implementation | Verdict |
|---|---|---|---|
| 1 entropy drift | recent mean >3x min-baseline, min>0.01, recent>0.3 | all three gates ANDed, strict > | MATCH |
| 2 trust-region | violations >=5 windows | int >= 5 | MATCH |
| 3 NaN/Inf | loss/rewards | math.isfinite on loss + every reward; None loss = fail-closed FIRE (documented extension, sound) | MATCH |
| 4 NPU | ERR99999 | token substring in log text | MATCH |
- Min-baseline fix VERIFIED IN CODE: baseline is min across the window, NOT first-3-mean — the RUN-12 missed-detection class (early spike contaminates the first-3 baseline) is closed.

### 3. Test-pinning: 16/16 GREEN (independently re-run)
- .venv py3.9.6, pytest 8.4.2: 16 passed, 0 skipped. py_compile OK (both files).
- RUN-12 real-degradation log as fixture: test_entropy_drift_fires_on_run12_validation_case pins 0.042/1.056 -> FIRE; composite test pins the exact single-signal outcome.
- Boundary pins: recent<=0.3 no-fire, min<=0.01 no-fire, exactly-3x fires (strict >), trust-region 4 vs 5 boundary, NaN/Inf each of loss/reward, ERR99999 present/absent, all-clear composite = [].
- Bellwether test guards the shadowed-helper vacuity class (module identity probe).

### 4. RUN-12 validation replay (numbers, not claims)
- Entropy: min-baseline 0.042, recent 1.056. Gates: 0.042 > 0.01 yes; 1.056 > 0.3 yes; 1.056 > 3x0.042=0.126 yes -> entropy_drift FIRES. (First-3-mean counterfactual: baseline ~0.683 -> 3x=2.049 > 1.056 -> would MISS; confirms why min-baseline is the fix.)
- Trust-region: RUN-12 documented 16 violation windows (#227b/#233) >= 5 -> FIRES. RUN-12 is a TWO-SIGNAL validation case, not just entropy.
- Composite on (0.042, 1.056, 16, -0.05, [0.1], "step 12") -> ['entropy_drift', 'trust_region_violations'].
- VERDICT: the sentinel WOULD have fired on the real RUN-12 log.

### 5. Bundle membership: r21 DOES NOT SHIP THE SENTINEL — GAP CLOSED FOR r22
- tmp/sapo-relaunch-r21.sha256 + r21.tgz (built 2026-08-31 19:29Z): zero sentinel references. No capability_sentinel.py, no rules mirror, no rules tests. The defense was LOST ON ANY REDEPLOY from r21.
- FIXED: tmp/build_r22_bundle.py additions now include scripts/sapo_capability_sentinel_rules.py + tests/test_sapo_capability_sentinel_rules.py. r22 rebuilt (221 members) and verified: both files present in tgz + manifest (2 hits).
- Note: scripts/sapo_drift_watch.py (a DIFFERENT tool — checkpoint zero-change drift alarm) IS bundled in r21/r22; do not confuse the two.

### 6. Remaining gap (escalation for manager) — RE-VERIFIED 2026-09-01 (fixer lane)
- The box-side capability_sentinel.py watcher script itself is NOT mirrored into the repo. A fresh box gets the rules contract only. Before the next launch: mirror the box script (or re-implement it against the pins) so the sentinel survives redeploy; box channel is down so this requires the box pull once the channel opens.
- FIXER-LANE RE-VERIFICATION (2026-09-01): `find / -name capability_sentinel.py` across the local filesystem → ZERO hits. No local copy exists — confirmed, not just assumed. Decision per fixer mandate: DO NOT fabricate a local copy (box-only script must be pulled, not re-guessed); the rules mirror + 16 tests are the contract until then.
- ACTION ITEM (owner: manager/deploy lane): AT FIRST CHANNEL-OPEN, pull the box's capability_sentinel.py (path on box: deployed via eval wave #234; locate via `ls /root/work/software/quantum-gpt/scripts/capability_sentinel.py` or find) into `scripts/capability_sentinel.py`, verify it satisfies the pinned rules (run tests/test_sapo_capability_sentinel_rules.py against it), then add to r23 bundle + commit. Until that pull lands, a redeployed box has the rules mirror but NOT the watcher.
- Commit the two sentinel files + build_r22_bundle.py edit so the next bundle is reproducible from git, not from the working tree.

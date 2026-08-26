# REPAIR-QUEUE WATCH — lane #13 (SAPO RL loop)

Role: watch the repair-queue pipeline (queue -> conversion -> SFT/DPO stage) of the
ASI3 SAPO run. Fix authority: repair-sidecar/queue mechanics via TDD + redeploy.
Never touch the trainer while healthy. Box daemon: `POST http://127.0.0.1:19005/exec`
payload `{"command": "..."}` (shell serves ASI3; repo at /root/work/software/quantum-gpt).

## Check routine (loop ~5 min)

1. Queue growth: `wc -l <OUT>/repair_queue.jsonl` vs `<OUT>/repair_stage/repair_converted.jsonl`.
   Entry queued >15 min unconverted while sidecar alive = stall -> diagnose
   (sidecar dead / dedupe collision / crash in `scripts/fv_gspo_repair_stage.py`)
   with `logs/sapo_27b_ai/repair_sidecar_<RUN>.log`.
2. Sidecar liveness: `pgrep -f fv_gspo_repair_sidecar` (beware self-match of the
   daemon's base64 wrapper — confirm via `/proc/<pid>/environ` OUT/RUN_ID and the
   pid files in `logs/sapo_27b_ai/`). If dead while trainer lives -> relaunch per
   `scripts/asi3_launch_grpo_direct.sh` sidecar invocation
   (`bash scripts/fv_gspo_repair_sidecar.sh <OUT>` via nohup).
3. Queue quality: entries must carry task_id + failures evidence. SyntaxError-only
   flood = temp-collapse artifact -> report to manager + data-eff (don't fix alone).
4. Run-3 poison pattern: mastered task (pass_rate >= 0.95/1.0) queued with junk
   candidates -> flag instantly.

## Run-5 status — 2026-08-25 12:38Z (healthy)

- Trainer pid 14279 (`python3 training/grpo_trainer.py`, child 14585, 99% CPU),
  at step 14->15 (log `grpo_train_20260825T070339.log`, last write 12:31Z; step 13
  adapter checkpointed; zero_change_alarm:false; 0 traceback/error/oom in last 60 lines).
- Sidecar pid 14280 (`bash scripts/fv_gspo_repair_sidecar.sh`, started 07:03Z,
  log `repair_sidecar_20260825T070339.log`; REPAIR_POLL_SECONDS=60; last poll 12:36:27Z
  -> "repair stage pass; converted=3"). ALIVE.
- Queue `<OUT>/outputs/sapo-27b-ai-20260825T070339/repair_queue.jsonl`:
  3 entries, all converted <=35s after queueing (08:13:29->08:13:50;
  10:57:52->10:57:53; 11:43:15->11:43:48). No stall, no dedupe collision
  (converted ledger dedup_keys == queue dedup_keys: maxcut f9296fa173,
  measurement 0b2cd386a4, qft fdfa9b9771). No crash in fv_gspo_repair_stage.
- Quality: all entries carry task_id + failure evidence. Entry 3
  (quantum_qft_periodic_state, step 12) is single-failure IndentationError
  (SyntaxError-class) — not a flood; note for manager/data-eff as possible
  temp-collapse signature (indent-broken extraction), no action.
- Poison pattern: none (all queued pass_rate 0.0; no mastered-task entries).

## Heartbeat 13:35Z (re-invoke after ~55 min stale)

- Queue: 3 entries / 3 converted — unchanged since 12:38Z, fully drained, no stall.
  No new all-fail rollouts queued during steps 15-16 (step 15 had 2/4 passes).
- Sidecar 14280 alive, last poll 13:35:05Z "repair stage pass; converted=3".
- Stale run-4 sidecar 9959 GONE from process list (reaped after the hygiene note —
  resolved, no longer looping).
- Trainer 14279 alive, step 16 begun (quantum_qml_variational_classifier);
  step 15 adapter saved, 2/4 candidates passed, seq_kl ~2e-4-4e-4, clip 0,
  zero_change_alarm:false; 0 traceback/error/oom in last 40 lines.
- Poison pattern: none (no queue growth; last entry remains step-12 qft, pass 0.0).

## GUARDIAN ALARM 8 — 2026-08-26/27: silent sidecar death (runs 11 + 12)

ROOT CAUSE (reproduced live on run-12): the box-prep flow
(/tmp/sapo_run12_box.sh, run by the restart operator) SIGKILLs ANY process
matching `fv_gspo_repair_sidecar` ("stale cleanup") and can run again
mid-run (`sapo_run12_launch.out`: "ERROR: SAPO trainer already running
pid=120801"). SIGKILL is untrappable -> the sidecar's TERM/INT trap never
runs, the pidfile is left behind, the log freezes right after the startup
line (both run-11 and run-12 logs are exactly 2 lines / 359 bytes), and the
all_fail_without_repair breaker stops the run hours later with zero
operator-visible signal. Trainer health was never the issue (run-11: 20
healthy steps, adapters at 6/8/11/13/15/18, drift active).

FIX (TDD, landed for the next bundle):
- training/sidecar_liveness.py (new): shared pidfile + log-heartbeat check
  (alive / dead_pid / missing_pidfile / stale_log), CLI emits JSON, exit 1
  on alarm. Grep markers SIDECAR_ALIVE / SIDECAR_DEAD_ALARM.
- scripts/sapo_ensure_repair_sidecar.sh (new): idempotent boot guard —
  alive -> no-op; dead/stale -> LOUD alarm + nohup relaunch (the spawn that
  provably survives the daemon transport; run-5's sidecar survived hours).
- scripts/asi3_launch_grpo_direct.sh: calls the ensure guard before trainer
  launch; required_files now includes both new files (boot fails loudly if
  the bundle is missing them).
- training/grpo_trainer.py: boot check + per-step check (state-change alarm
  + every-30th-step while dead), step-record flag `sidecar_alive` in
  grpo_step_metrics.jsonl; new flags --repair-sidecar-pidfile/-log/-max-log-age.
- training/grpo_utils.py: build_grpo_step_record persists `sidecar_alive`.
- scripts/asi3_secure_python_s3_pull.py: bundle manifest includes both new files.
- tests/test_sidecar_liveness_guard.py: 13 tests (unit matrix + ensure-script
  e2e that SIGKILLs the sidecar and asserts relaunch + heartbeat + idempotency
  + launcher/trainer pins). All green locally.

IMMEDIATE ACTIONS TAKEN (missions 3+4):
- Run-11 sidecar restarted (pid 122014) -> 5/5 queued entries converted to
  repair_converted.jsonl / repair_sft.jsonl / repair_dpo.jsonl (verified).
- Run-12 sidecar spawned (pid 122015) BEFORE its first queue entries; run-12
  trainer (pid 120801) at step 1..N with the sidecar polling every 60s.
- NOTE: run-12's boot scripts do NOT spawn the sidecar — if run-12 restarts,
  the sidecar must be re-spawned (or the bundle with the boot guard applied).
- RUN-12 BOOT-VERIFY MUST INCLUDE: `ps -eo pid,args | grep fv_gspo_repair_sidecar`
  (sidecar present) AND the sidecar log mtime fresh within ~300s. Do NOT re-run
  the box-prep kill loop after the sidecar is up (that is the killer).

## Hygiene note for manager (no action taken)

Stale run-4 sidecar pid 9959 (`/proc/9959/environ`: RUN_ID=20260825T052636,
OUT=outputs/sapo-27b-ai-20260825T052636, launched via nohup 05:26Z) still loops
"no repair queue yet; waiting" every 60s (log `repair_sidecar_20260825T052636.log`).
Run-4 died 06:27Z and its queue file never existed. Benign (0% CPU, isolated OUT,
no GPU, no interaction with run-5 breaker/converted ledger), but it will loop
forever. Suggested: kill 9959, and add a launcher guard that reaps prior-RUN_ID
sidecars before launch. Not fixed here (minimal-touch; current sidecar healthy).

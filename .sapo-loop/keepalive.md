# keepalive status

Updated: 2026-08-24 16:25 CST (08:25 UTC)

## Daemon/port/env map
- **ASI3 (TRAINING) daemon pid 60933, port 20653, Chrome CDP [::1]:9224 — ready:true, shell:true, drift:false.** NEW base-init run training (run 075223): trainer **68256** (Rl, 148% CPU), checkpoint_sync 68247 + repair_sidecar 68257 resident. 8 NPUs busy (AICore ~100-105%, HBM 9.7-12GB/card). Log markers: text_forward_preflight → step_begin (step 1 in generation; ~20 min/step cadence expected). Read-only only — never type/navigate its terminal.
- **ASI2 (EVAL LANE) daemon RELAUNCHED pid 41981, port 19004, Chrome CDP 127.0.0.1:9225 — ready:true, shell:true, drift:false** (ready 16:09 CST; bridge self-healed ~90s). Old ASI2 daemon was dead (background task exited) → relaunched with proven recipe (HUANXIN_ALLOW_SAFARI_SSO_BRIDGE=1 HUANXIN_CAPTURE_SCRIPT=/tmp/capture_safari_fixed.sh HUANXIN_FORGE_KC_CALLBACK=1 HUANXIN_CDP_PORT=9225 HUANXIN_TRAIN_DEV_URL=dl-868c196fb82d3e0b8cfbbe826d8afd0a?name=ASI2). Verified: hostname dl-868c196f..., **4 NPUs**. Eval lane ready for the next eval cycle (first checkpoint of run 075223).
- ai1 daemon pid 47095, port 19001, Chrome 47102 holds 127.0.0.1:9224 + quantum-rnd copy — do NOT touch.
- AI env dl-9a5a098a (platform name ASI1) still RUNNING 1卡 — stop decision pending user/loop.

## Capture probes
- ASI3: `echo A; echo B` → both lines, clean (2 rounds this cycle). ASI2: both lines, clean. No truncation.

## Actions this cycle
- Relaunched ASI2 daemon (was dead), verified shell + 4 NPUs. ASI3 trainer + sidecars resident, NPUs busy.
- Poll rounds 1-4 (16:08-16:25): both daemons ready:true throughout; capture probes clean every round (no truncation). **Base-init run: step 1 COMPLETED (backward_done 08:18:28 UTC), step 2 in generation** — trainer 68256 Rl 33 min, NPUs ~100% AICore. First checkpoint of run 075223 expected at step-1 boundary + sync (~30 min). Eval lane ready on ASI2 for it.

## Blockers
- None. Watch: trainer 68256 — if dead, report immediately, do NOT relaunch training.

## DAEMON (auth/daemon watch, 2026-08-25 ~20:35 CST)
- **ASI3 daemon pid 20484, port 19005 — ready:true, shellSurfaceReady:true, authDriftDetected:false.** Uptime ~10.2h, commandCount 1576, busy:false. URL dl-c72bd81a96e33134bbe0ae4a478fbab0?name=ASI3 (headless, launchFallbackUsed:false).
- /exec round-trip clean: `echo x` → `x`, exit 0 (2.7s). No failure, no recovery this cycle.

## CAPACITY (lane #10, 2026-08-25 12:36-12:42 UTC / 20:36 CST)
Polled via ASI3 daemon /exec (127.0.0.1:19005, env dl-c72bd81a96e33134bbe0ae4a478fbab0). Run-5 = sapo-27b-ai-20260825T070339, trainer **14279** (grpo_trainer.py, base-init, --npu-max-memory-gib 54 cap + --train-pass-max-seq-length 2048 present = step-1 OOM fix in place). Checkpoints synced: steps 1/3/6/9/13; ~step 14 in progress (latest metrics row all_fail, entropy 0.51 — metrics lane's call, not capacity).

**Process inventory (NPU context via npu-smi process table):** trainer 14279 on all 8 cards (8.1-12.4 GiB/card) + multiprocessing children 14641-14659 (no NPU ctx). ONLY other NPU user = drift watcher 17592 (sapo_drift_watch.py, card 0, 436 MB) — protected sidecar, NOT killed. **No eval legs, no stray python → co-residency CLEAN.** (r2s4 class: no live instance.)

**Per-card HBM (MB / 65536 wall), poll1 12:35Z → poll2 12:40Z:**
| card | poll1 | poll2 | Δ |
|---|---|---|---|
| 0 | 16151 | 16152 | +1 |
| 1 | 11721 | 11722 | +1 |
| 2 | 11769 | 11769 | 0 |
| 3 | 11543 | 11543 | 0 |
| 4 | 11439 | 11439 | 0 |
| 5 | 11439 | 11439 | 0 |
| 6 | 11844 | 11845 | +1 |
| 7 | 15148 | 15148 | 0 |

Max card 0 = 15.8 GiB (15.8/60.96 wall = 26%). All cards far under 56 GiB OOM-flag threshold. **Trend: flat (±1 MB noise), no creep.** Trainer footprint 8.1-12.4 GiB/card — inside the expected 7-14 GiB band. AICore: cards 2-7 ~100% steady; cards 0/1 instantaneous dips (7%→4%, 1%→0%) = balanced-layers generation-phase bubble, not a fault (HBM stable). No kills this cycle; no alerts to manager.
### CATCH-UP PASS (manager resilience duty, 2026-08-25 ~21:22 CST / 13:22Z)
No outage this cycle (daemon uptime ~10.2h, /exec clean) — ran mailbox scan per standing duty. Findings:
- /tmp/sapo_relaunch_exec_health.log: LIVE, all VERDICT=OK (last 13:15Z); P=2 cpu=146 errs=0 zero_change_alarm:false; drift diff 0.0009766.
- /tmp/sapo_relaunch_exec_ALARM: absent (no alarm). /tmp/sapo_guardian_poll.out: last POLL 10 at 05:29Z (ready:True, run 052636 launch detected) — stale ~8h, note only.
- Run 070339: drift_alarms.log=1 line (step 3, 08:46Z, diff 0.000244); alarms.jsonl 1 entry (08:46Z step 3); repair_queue.jsonl 2 entries (steps 11/12, last 11:43Z) — all old, no new alarms. zero_change_alarm:false.
- Train: step 15 COMPLETE (backward_done loss -0.0416, grad_norm 0.528), step 16 in generation (quantum_qml_variational_classifier). sapo_drift_watch: 1 proc alive.
- VERDICT: nothing alarming; shell healthy end-to-end.
- **DISK (coordinator pass, 2026-08-25 13:33Z / 21:33 CST)** — `df -h /root/work /root/work/filestorage` (both NAS mounts; box root is itself a NAS share):
  - `/root/work` (box root, NAS share-3cfddb17): 2.0T total, 547G used, **1.5T free (1501.7 GiB)**, 27% — no flag.
  - `/root/work/filestorage` (NAS share-051971f2): 9.8T total, 2.5T used, **7.3T free (7449 GiB)**, 26% — no flag.
  - Both far above the ~20 GiB free flag threshold; adapter checkpoints (312 MB) + NAS copies are a rounding error against this headroom. No disk action needed.
### HARDENING NOTE (capture script repo-homed, 2026-08-25 ~21:35 CST)
- Canonical capture script: **scripts/huanxin_capture_safari_fixed2.sh** (repo, /Users/daxu/software/quantum-gpt/scripts/huanxin_capture_safari_fixed2.sh) — verified byte-identical to /tmp/capture_safari_fixed2.sh (both 5145 B, +x). macOS /tmp cleanup can wipe the /tmp copy.
- RECOVERY RECIPE (updated): prefer repo copy → `HUANXIN_CAPTURE_SCRIPT=/Users/daxu/software/quantum-gpt/scripts/huanxin_capture_safari_fixed2.sh`. If the /tmp copy is missing and something requires it at that path, `cp /Users/daxu/software/quantum-gpt/scripts/huanxin_capture_safari_fixed2.sh /tmp/capture_safari_fixed2.sh` BEFORE daemon relaunch.

## DAEMON HEARTBEAT (2026-08-26 ~10:10 CST / 02:10Z)
- **ASI3 daemon pid 20484, port 19005 — ready:true, shellSurfaceReady:true, authDriftDetected:false.** Uptime ~23.8h, commandCount 4753.
- /exec round-trip clean: `echo x` → `x`, exit 0 (3.2s) — queued fine behind daemon busy.
- NOTE: daemon was mid-exec of executor's run-7 launch (busyLabel:exec): removes /tmp/sapo_leg_GO, exports ASI3_SAPO_ROOT/MODEL_PATH/ADAPTER_INIT=outputs/sapo-27b-ai-20260825T214849/step_000005_adapter, launches scripts/asi3_launch_grpo_direct.sh launch → /tmp/sapo_run7_launch.out. Legacy markers being superseded at run-7 gate per coordinator — no action needed (verified /tmp/sapo_leg_GO already gone; only pause scripts remain in /tmp, no pause marker).
- Watch resumed per lane-liveness re-invoke; no recovery needed this cycle.
- **🚨 OOM-HAZARD ALARM (2026-08-26 04:18Z / 12:18 CST) — TRAINING IS DOWN, NPUs IDLE.** New watch item from log analyst confirmed + escalated: the pod (kubepods/burstable/pod93295acf) cgroup memory limit is being hit repeatedly; OOM-killer fires at pod level (CONSTRAINT_MEMCG) and takes the platform's oom_score_adj=999 agents as victims. dmesg -T kills: **dosec_hades at 2026-08-25 20:40:56Z, 23:44:03Z, 2026-08-26 02:47:09Z** (each ~3.1 GB anon-rss, oom_score 2060/2058/2064). Host RAM is NOT the constraint (free -h: 2.0T total, 1.9T available; PSI unavailable on kernel 4.19) — the pod cgroup ceiling is the binding limit; the limit value is not readable from inside the container (cgroup ns root).
  - **Correlated trainer deaths (3 runs, 12h):** run-5 `070339` reached step 27 (last drift poll 20:26:19Z, drift watcher 17592 died with it) — death window 20:26-20:40Z = kill #1. Run `214849` (21:48Z launch, resume chain) saved adapter, replaced by relaunch at 02:08Z. Run `020821` reached step 4 (drift poll 02:56:45Z) then died — train log ends `[ERROR] TBE Subprocess[task_distribute] ... main process disappeared!` = the EOFError/worker-death class under the 02:47Z kill window.
  - **Protection status:** trainer oom_score_adj = **-997** (near-immune to direct kill — dmesg shows NO our-process kills, only dosec_hades/dosec_hunter); but workers/forkserver children die from allocation failures under pod pressure. The killer CANNOT be ruled out for our processes under a heavier pod mix (trainer + 3 sidecars + 3 stale repair sidecars + platform agents).
  - **(a) dosec_hades count this poll: 0 present** (killed 02:47Z, no respawn). (b) free -h: 59 Gi used / 1.9T available; dmesg oom count total: 384 (platform-wide since Aug 15). (c) **ALARM TRIPPED: OOM-kill coincides with trainer death — 3 kills, 3 run deaths.**
  - **Current state (04:18Z): NO trainer on NPUs.** npu-smi: cards 1-7 no processes, HBM ~3.4 GB/card baseline; card 0 only drift watcher 65698 (436 MB, alive, but its drift_watch.log silent since 02:56:45Z — possibly stuck; not killed, protected). checkpoint_sync alive (log 04:08Z); **3 stale repair sidecars resident** (070339/214849/020821 sidecars, all logging at 04:18Z) — zombies of dead runs, NOT killed by capacity lane (protected list), flag to manager: 2 of them belong to dead runs and should be reaped by the relaunch executor.
  - **Recommendation to manager/relaunch executor:** do NOT relaunch blindly — the pod cgroup ceiling kills each new trainer within 1-4 steps. Either (1) get the pod memory limit raised (host has 1.9 TiB free), or (2) shrink pod host-RAM footprint (stale sidecars, drift watcher 2 GB RSS), before relaunching. Next relaunch should confirm trainer survives > 2h AND > kill-window cadence (kills come every ~3h).
- **CAPACITY HEARTBEAT run-9 (2026-08-26 06:23Z / 14:23 CST)** — trainer **74779** live, run `sapo-27b-ai-20260826T060754` (launched 06:07:54Z, elapsed 15m). Sampler fix IN cmdline: `--greedy-rollout-fraction 0.4 --entropy-floor 1.5 --entropy-floor-weight 0.01 --adaptive-temp-max 1.3` (vs 2.0) + caps `--npu-max-memory-gib 54` / train-pass 2048. Run-8 = `044037` (launched 04:40Z) was the NPU-0 59.8 GiB casualty. Run-9: no step checkpoints yet (first step in generation).
  - **Per-card HBM @06:23Z (MB / 65536):** 0=12390, 1=9805, 2=9806, 3=9807, 4=9804, 5=9806, 6=9806, 7=12229. **NPU-0 = 12.1 GiB — success signal ≤20 GiB holding vs run-8's 59.8** (train-logprob peak pending — first backward not yet hit). No card >56 GiB flag.
  - **Process/NPU inventory:** npu-smi process table = ONLY 74779 (trainer, 6.3-8.8 GiB/card). No drift watcher on NPUs (75878 idle, not holding). **Co-residency CLEAN. Zero kills.**
  - **OOM cadence (dmesg -T): 2 NEW pod-cgroup kills at 05:35:01Z + 05:35:27Z** — dosec_hades 429735 (3.05 GB) + dosec_hunter 495569, both under pod93295acf (run-8's death window). Kill cadence now: 20:40Z, 23:44Z, 02:47Z, 05:35Z = every ~3h; **next expected ~08:3xZ — watch run-9 through it.**
  - **Disk:** /root/work 1.5T free (27% used, +4G since 13:33Z), filestorage 7.3T free — no flag.
  - dosec present: 0. Host RAM: not the constraint (pod cgroup is). Trainer oom_score_adj -997 (protected from direct kill).
- **CAPACITY HEARTBEAT run-9 (2026-08-26 06:37Z / 14:37 CST)** — trainer 74779 alive, run 060754, ~30m in. Step 1 still in generation (no metrics rows, no checkpoints — first backward pending).
  - Per-card HBM @06:37Z: card 0 proc 9030 MB (HBM total ~12.4 GiB, unchanged), cards 1-6 9804-9807 MB (flat), card 7 12278 MB (+49 MB vs 06:23Z, proc 8918 MB). **No card >56 GiB; no creep trend; NPU-0 peak signal still ≤20 GiB, confirmed through first 30 min.**
  - Process/NPU: npu-smi process table = ONLY 74779 across all 8 cards. Co-residency CLEAN. Zero kills. dosec: 0.
  - OOM cadence: no new kills since 05:35Z. Next expected ~08:3xZ (4-kill cadence 20:40Z/23:44Z/02:47Z/05:35Z ≈ every 3h) — must confirm run-9 survives it; will re-poll before then.
  - Disk: unchanged (1.5T / 7.3T free). No flags.
- **🚨 CAPACITY ALARM run-9 DIED — NPU-0 train-pass OOM (2026-08-26 06:52Z / 14:52 CST).** Trainer 74779 dead; NPUs idle again (no relaunch as of 06:53Z; run 060754 still newest). **The ≤20 GiB success signal FAILED — cross-check verdict: run-9 NPU-0 train-logprob peak ≈ 59.49 GiB reserved, same wall-hit as run-8.**
  - **Death evidence (train log grpo_train_20260826T060754.log):** step_begin 1 → generation_done (completions ≤2009 tokens) → `RuntimeError: NPU out of memory. Tried to allocate 970.00 MiB (NPU 0; 60.96 GiB total; 58.72 GiB already allocated; 540.43 MiB free; 59.49 GiB reserved)` at **grpo_trainer.py:5140 `entropy_floor_penalty_tensor.backward()`**, 06:49:53Z. Run-8 (044037) identical signature: 59.84 GiB active / 60.13 reserved, 64 MiB alloc failed. Both died at step 1, **zero checkpoints** (RUN8CKS 0, RUN9CKS 0).
  - **Why my polls missed it:** HBM on NPU-0 was flat 12.4 GiB at 06:23/06:37/06:43Z; the spike to 58.7 GiB happened entirely inside the 6-min window 06:43→06:49:53Z (train-pass backward). npu-smi spot polls cannot catch this phase — **the definitive signal is the train log RuntimeError line**, which I now check every poll.
  - **Executor fix verdict: sampler changes did NOT fix the train pass.** Greedy-rollout-fraction/entropy-floor cap rollout-side memory; the killer is the backward accumulation on card 0 (only card 0 spikes; 1-6 flat at 6.4 GiB, card 7 8.9 GiB). Fix must target the train-pass backward on card 0 (e.g., entropy-floor penalty path at grpo_trainer.py:5140, card-0 layer allocation, or train-pass activation cap) — executor's call, evidence here.
  - **OOM cadence:** no cgroup OOM-kill at this death (last dmesg kill 05:35Z) — this was a DEVICE OOM, distinct from the pod-cgroup pattern. **Next cgroup kill expected ~08:3xZ (cadence 20:40/23:44/02:47/05:35Z ≈ 3h)** — any relaunch must survive past it.
  - Co-residency: CLEAN throughout (only 74779 on cards at every poll). dosec: 0. Disk: 1.5T/7.3T free, no flag. Zero kills by me.

## DAEMON RECOVERY (2026-08-26 ~17:10Z / 2026-08-27 01:10 CST)
- **WEDGE**: daemon pid 20484 reported ready:true but terminal-exec wedged — busy 13s+ on trivial `ps | wc -l`, /exec probes queued empty (pending:1), commandCount stuck ~7047, lastActivity 17:02:01Z. Matches watcher alarm: /tmp/sapo_relaunch_exec_ALARM = ALARM-A 17:03:53Z DAEMON_UNREACHABLE (store-and-forward surfaced; root cause = wedge, not trainer).
- **RECOVERY (proven recipe, repo-homed capture script)**: killed daemon node + its automation Chrome (CDP 9225, profile dir — bridge-owned headless, NOT user browser) → rm profile/SingletonLock* → relaunched pid **99989** with HUANXIN_CAPTURE_SCRIPT=/Users/daxu/software/quantum-gpt/scripts/huanxin_capture_safari_fixed2.sh (repo copy) + standard env. Booted ready in ~80s.
- **VERIFIED**: ready:true, shellSurfaceReady:true, authDriftDetected:false. /exec `echo x` → `x` exit 0 (6.8s).
- **TRAINER UNTOUCHED (run-11 TRAINING)**: grpo_trainer procs=2 alive on box; current run sapo-27b-ai-20260826T093441 at step_begin 13 (quantum_circuit_depth_optimization, temp 1.3); drift last 15:33Z step 11, diff healthy; no drift_alarms.log in current run dir. Old run-7 log shows step 26 no_trainable_tasks (historical).
- Watcher mailbox: relaunch_exec_health.log last pre-wedge VERDICT=OK 16:58:08Z (P=2 cpu=145 zc=false); ALARM file present from wedge — next healthy poll should overwrite it.

## DAEMON RECOVERY #2 (recurring wedge, 2026-08-27 ~01:40-01:45 CST)
- Wedge #2: pid 99989 (relaunched ~20 min earlier) wedged same signature — busy:true 75s+ on `tail -n 1 grpo_train_...log`, /exec probe empty, cmdCount frozen 43. Recovered with proven recipe: kill daemon + automation Chrome (CDP 9225) → rm SingletonLock* → relaunch pid **22908** with repo-homed capture script. Booted ready in ~100s.
- VERIFIED: ready:true, shellSurfaceReady:true, authDriftDetected:false; /exec `echo x` → x exit 0 (2.7s); trainer_procs=2 (run-11 untouched, current run sapo-27b-ai-20260826T093441).
- ROOT CAUSE (recurring, now documented in debugger.md): unbounded page.evaluate/keyboard I/O in sendCommand under the withLock mutex — a stalled xterm renderer hangs forever, busy=true sticks, all /exec queue-empty; health stays green (cheap evaluate) so it is NOT a wedge detector. Fixes ranked in debugger.md (bound readTerminalText, per-call timeouts, exec deadline, stuck-lock watchdog, box-side status aggregator, scrollback hygiene). WEDGE WATCH: monitor busyAgeMs + pendingRequestCount, NOT ready flag.

## DAEMON RESTART #3 — WEDGE FIXES PICKED UP (2026-08-27 ~02:00-02:05 CST)
- Debug lane wedge fixes GREEN (4/4 node tests incl. "simulated stall does NOT wedge" + watchdog force-release; venv canary green). Restarted daemon per recipe: kill 22908 + automation Chrome → rm SingletonLock* → relaunch pid **34607** with repo-homed capture script. Booted ready ~100s.
- VERIFIED: ready:true, shellSurfaceReady:true, authDriftDetected:false, busy:false, pending:0, cmdCount 4; /exec `echo x` → x exit 0 (3.2s); trainer_procs=2 (run-11 untouched).
- NEW WATCH ITEMS (fix contract): (1) structured **HUANXIN_TIMEOUT** / **HUANXIN_EXEC_DEADLINE** errors instead of hangs — a 504 means the deadline path fired (recoverable), silence+freeze means old-style wedge; (2) daemon log line `stage: lock_watchdog_force_release` = stuck-lock watchdog fired and shell was force-reopened — expect 1-3 occurrences max, then steady state; (3) health busy/pending remain the primary wedge signals; ready:true is NOT a wedge detector.
- Fix source: huanxin_browser_daemon.js (withLock watchdog + reopen callback) + huanxin_shell_exec.js (withTimeout, EXEC_DEADLINE) — uncommitted working-tree changes, noted for commit.

## DAEMON STATE 2026-08-28 ~09:50 CST (Mac reboot recovery)
- Mac rebooted 09:09 CST → all session-scoped box daemons + Mac judge watcher dropped (/tmp wiped).
- ASI3 box daemon RELAUNCHED pid 21857, port 19005 (recovery recipe: repo capture script
  scripts/huanxin_capture_safari_fixed2.sh, HUANXIN_TRAIN_DEV_URL=dl-c72bd81a...?name=ASI3,
  HUANXIN_CDP_PORT=9224, ASI3 env). Health: ready:false / booting, background auth retry cycling —
  needs user Huanxin SSO (Safari callback capture fail: found:false). Self-heals on a valid session.
- dp4 proxy upstream TESTED HEALTHY 09:22 CST (rapid correct response via 127.0.0.1:49679) — the
  06:10 degradation has recovered.
- TO RESTORE judge blend: once daemon ready, re-arm sapo_judge_mac_watcher.py (SAPO_DAEMON=:19005,
  SAPO_BOX_QUEUE=<R22>/judge_bridge, SAPO_DP4_PROXY=<working dp4 port>).
- Box R22 training (sapo-27b-ai-20260827T195801Z) self-continues on the box independent of daemon;
  judge-absent → P+S-only (safe). NOT relaunched (no code bug).

## MANDATE UPDATE 2026-08-28 13:20 CST (user directive: "make the access agent be responsible to keep it alive forever")
GAP OWNED: ASI3 env was terminated on the platform and died UNNOTICED because this lane watched only the
daemon's health, and the daemon was SSO-locked (could not /exec). THE DAEMON IS NOT THE ENV.
NEW RULES (binding):
1. ENV LIVENESS = /exec probe, never daemon health alone: every cycle, /exec `hostname && uptime && npu-smi | head -3`
   while the daemon is ready. env dead / exec fails → ESCALATE IMMEDIATELY to manager + user with
   "ASI3 ENV TERMINATED — restart required" (user restarts on the platform console; env state is NOT
   recoverable by this lane).
2. AUTH-LOCK ESCALATION: if authDrift:true for >30 min, this lane must NOT report "daemon alive, waiting
   for SSO" as a stable state — it must escalate "env liveness UNVERIFIABLE (transport auth-locked) — env
   may be dead behind the lock" and ask the user for BOTH: (a) one Safari SSO login, (b) confirm the env
   is running on the platform console.
3. WATCH CYCLE after any unlock: first 3 cycles verify env alive + trainer resident + NPUs busy; report
   env alive/trainer/NPU lines each cycle (provenance: /exec output).
4. KEEP-ALIVE AUTHORITY: this lane keeps the DAEMON alive (relaunch on wedge/death per recovery recipe);
   the ENV's keep-alive is the platform's own policy (user action) — this lane's duty is DETECTION +
   ESCALATION within the budgets above, not silent waiting.

---

## KEEPALIVE/WEDGE LANE AUDIT (2026-09-01, run 2026-08-31 22:00-22:07 CST / 14:00-14:07Z)

Audit of the daemon liveness machinery after the aihuanxin.cn IPv6-route outage. All processes checked
live at 22:06 CST.

### 1. Process table
| Process | PID | Started | Uptime | Last activity | State |
|---|---|---|---|---|---|
| /tmp/asi3_daemon_keeper.sh | 42740 | Aug 31 15:56 | 6h10m | log write 13:52:56Z | ALIVE |
| /tmp/sapo_eval_agent.sh (ASI2 keeper) | 79701 | Aug 31 11:22 | 10h45m | log write 14:04:32Z (relaunch fired) | ALIVE |
| scripts/sapo_judge_mac_watcher.py | 42035 | Aug 30 15:45 | 1d6h | log write 14:02:38Z | ALIVE (ticking, erroring — see below) |
| /tmp/sapo_train_monitor.sh | 12609 | Aug 30 12:56 | 1d9h | log write 14:06:11Z | ALIVE (reporting CHANNEL_DOWN) |
| scripts/sapo_box_pull_watch.sh | 55523 | Aug 31 19:51 | 2h15m | ledger write 14:01:00Z | ALIVE (60s poll) |
| launchd com.quantumgpt-new.huanxin-keepalive → /Users/daxu/software/quantum-gpt-new/scripts/huanxin_all_keepalive.sh | job 6718 | n/a | n/a | log write 14:00:43Z | ALIVE — but port-stale (defect, §6) |
| ASI3 daemon (node, port 19005) | 46344 | 21:52 CST | ~14m | health 14:02Z booting | ALIVE, SSO-locked |
| ASI2 daemon (node, port 19004) | 65188 | 22:04:32 CST | ~2m | health empty (booting) | ALIVE, booting — was in death-loop |
| ASI1 daemon (node, port 20646) | 95234 | 18:32 CST | 3.5h | health 14:02Z booting | ALIVE, SSO-locked |

Notes: huanxin_all_keepalive.sh is not a long-running process by design (launchd StartInterval 60s,
RunAtLoad; job currently runs every ~3 min — see §6). ASI1's port 20646 is the daemon's DEFAULT
(ENV_PORTS in huanxin_browser_daemon.js: ASI1:20646, ASI2:19004, ASI3:20653); ASI3 is deployed on
19005 (explicit --port 19005), which is the mismatch behind §6.

### 2. Keeper verdict — /tmp/asi3_daemon_keeper.sh: PASS
- Fires ONLY on process absence (`pgrep -f "huanxin_browser_daemon.js ASI3 --port 19005"`); binary
  state only — there is no UNKNOWN path, so it can never fire on UNKNOWN. The 3-state discipline lives
  in the eval agent's wait_daemon (ready=ALIVE / process-present+booting=UNKNOWN→wait / no-process×2
  =DEAD→relaunch) and is implemented correctly — UNKNOWN never fires there either.
- Min relaunch interval enforced: 60s sleep post-launch + 30s loop = 90s floor. Observed gaps today:
  13 fires, min gap 92s. No storm. The 10:32-10:37Z burst (4 fires at 92s cadence) was legitimate
  dead-detection — each freshly launched daemon died within ~1.5 min (Safari callback capture failures
  during the outage); the 90s discipline held throughout.
- Log shows healthy cycling: last fire 13:52:56Z produced the current ASI3 daemon 46344, alive since.
  The keeper also pkills before relaunching (stale-daemon guard). No ALIVE ticks logged — silence is
  the healthy signal.

### 3. Wedge detection: GAP — NO ACTIVE DETECTOR (proposal below, NOT implemented)
- Spec is documented (08-27): "monitor busyAgeMs + pendingRequestCount, NOT ready flag" and
  "ready:true is NOT a wedge detector". The health endpoint exposes all needed fields
  (busy/busyAgeMs/pendingRequestCount/commandCount/lastActivity — confirmed live on 19005).
- No watcher consumes them: the old /tmp/sapo_relaunch_exec_health.log watcher was wiped in the
  Aug 28 /tmp cleanup and never re-armed (no cron, no launchd entry). The ASI3 keeper checks process
  existence only; box-pull watch checks the ready flag for its one-shot purpose (correct for that, NOT
  a wedge detector); judge watcher is the blend feed; train monitor is a step counter via /exec.
- PROPOSED DETECTOR (for the loop owner; wedge class: busy=true stuck / terminal-exec wedged):
  a small watcher (e.g. /tmp/sapo_wedge_watch.py, nohup'd like the other watchers) polling
  19005+19004 /health every 60s; ALARM when busy=true AND busyAgeMs>120000, OR pendingRequestCount>3,
  on 2 consecutive polls; on alarm: append to .sapo-loop/keepalive.md + kill ONLY that daemon's node
  pid (the ASI3 keeper auto-relaunches within 90s; eval agent owns ASI2). Post-08-27 wedge fixes
  (EXEC_DEADLINE, lock watchdog) make wedges rare — this is belt-and-suspenders.

### 4. Watch health — scripts/sapo_box_pull_watch.sh: ALIVE, correct, expiry-bound
- bash -n PASS. scripts/asi3_exec.py EXISTS (default port 20653, but the watch passes --port 19005 /
  19004 explicitly — correct). Health-check loop dry-run: correct port pair, 60s cadence,
  MAX_POLLS=240 (~4h) → started 19:51 → exits ~23:51 CST if both pulls don't complete.
- /tmp/sapo_box_pull_watch.log is 0 bytes by design (all output goes to the ledger — not a defect).
- Ledger fresh (14:01:00Z). Both pulls pending: ASI3 ready is SSO-blocked, ASI2 booting → likely
  timeout exit tonight unless SSO unlocks; the watch will record it. (The "channel-recovery" ledger
  entries are written by an external writer, not this watch — noted, no action.)

### 5. Chrome profile hygiene + IPv6 pin
- PIN IN PLACE: /tmp/relaunch_asi3_daemon.sh line 7 HUANXIN_HOST_RESOLVER_RULES="MAP aihuanxin.cn
  36.212.177.181"; /tmp/relaunch_asi2_daemon.sh likewise. Verified LIVE in process env: both ASI1 and
  ASI3 Chrome cmdlines carry --host-resolver-rules=MAP aihuanxin.cn 36.212.177.181. The IPv6 workaround
  is functioning — ASI3's health shows the SSO login page loading (IPv4 reachability proven; the box
  is reachable, the SESSION is missing → user action: ONE Safari SSO login, same as 08-28 pattern).
- Singleton locks: ASI3 dir (huanxin-profile-quantum-rnd-ASI3) → owner 46361 LIVE (its own Chrome).
  ASI1 dir → owner 95294 LIVE. Both CLEAR. ASI2 dir had a STALE lock (owner 58965, dead) at 22:00 —
  the 22:04 relaunch's fresh Chrome re-initialized the dir (lock gone on re-check). Base quantum-rnd
  dir lock owner 52476 DEAD (stale, unused — daemons get -ENV-suffixed dirs). ~15 dead locks in
  auto-*/.bak/rnd2/rnd3/standalone dirs = dead leftovers from failed launches; harmless, cleanup-worthy.

### 6. REAL DEFECTS (proposals; NO code changed this cycle)
1. launchd keepalive (quantum-gpt-new/scripts/huanxin_all_keepalive.sh) is PORT-STALE and
   DOUBLE-OWNS ASI2:
   - Checks ASI3 on 20653 (daemon DEFAULT) while ASI3 is deployed on 19005 → perpetual "down" → today
     it spawned 7 stray daemons (05:13Z ×3, 06:29Z ×1, 08:31Z ×3) WITHOUT sourcing the env file (no
     API keys) and WITHOUT the IPv6 resolver pin — the exact failure the pin was added for. All died.
   - It also owns ASI2 keepalive on 19004 with a DIFFERENT recipe than the eval agent (CDP 9225 +
     profile quantum-rnd-ASI2 vs eval's CDP 9224 + quantum-rnd) — two keepers racing one port.
   - RECOMMEND: point ASI3 check at 19005; drop ASI2 (eval agent owns it) or source
     /tmp/daemon_env_asi2.sh + the pin in its relaunch; keep ASI1 here (its default 20646 matches).
     Its relaunches are currently suppressed anyway (NODE_BIN empty under launchd) — treat that as
     the current mitigation, not a design.
2. ASI2 death-loop 21:5x-22:04 CST: 4+ eval-agent relaunches failed with launchPersistentContext
   TimeoutError (browser-automation/huanxin_browser_launch.js:140). Candidate chain: competing
   keepers racing port 19004 + stale SingletonLock in the ASI2 profile dir + CDP 9224 double-bind
   (ASI1's Chrome holds it; ASI2/ASI3 relaunch scripts also set 9224 — benign today because Playwright
   uses the pipe, but wrong). The eval agent's restart_daemon does NOT kill leftover Chrome or clean
   profile locks — the documented recovery recipe (08-26) does. RECOMMEND (keeper-side fix, not daemon):
   add Chrome pkill + `rm -f <asi2-profile-dir>/SingletonLock*` to restart_daemon, and canonicalize
   CDP ports ASI1=9224 / ASI2=9225 / ASI3=9226.
3. Stale SingletonLock hygiene (auto-*/standalone*/.bak/rnd2/rnd3 dirs): cleanup-worthy, harmless.

### 7. Blockers (user action, not machinery)
- ASI3 and ASI2 are SSO-auth-locked (authDrift:true, currentUrl=login page; ASI3 boot loop cycling
  background auth retries). Transport reachability over IPv4 is PROVEN. One Safari SSO login unlocks
  both; until then env liveness is UNVERIFIABLE per the 08-28 mandate rule 2.
- Judge watcher ticks but errors (HTTP 500 / RemoteDisconnected) — consistent with the locked
  transport; not a watcher defect.

### 8. Verdict
- Keepers: all 5 watcher processes + launchd job ALIVE; ASI3 keeper discipline PASS (no UNKNOWN fires,
  90s floor held, cycling healthy).
- Wedge detector: MISSING (proposal in §3).
- Box-pull watch: ALIVE, correct, expiry ~23:51 CST tonight if pulls stay blocked.
- Chrome locks: live-owner locks clear; pin verified live in 2 Chrome processes.
- Fixes applied this cycle: NONE (all findings are propose-only; the two REAL defects are the launchd
  stale-port/double-ownership and the eval-agent relaunch lacking lock cleanup).

---

## Connection Keeper Agent (dated 2026-09-01)

Standing Huanxin-connection liveness lane. Loop: 60 ticks (22:06–23:31 CST, 2026-08-31, ~120s cadence). Heartbeat log: /tmp/sapo_connection_keeper.log (70 lines).

### Ticks run
60 probe ticks over ~85 min (compressed cadence during the ASI2 forensics window). Every tick probed /health on 19005 (ASI3), 19004 (ASI2), 20646 (ASI1); one log line per tick; 3-state discipline (ALIVE/DEAD/UNKNOWN — parse failures and timeouts logged, never fired a kill).

### Per-daemon recovery events (with evidence)
- **ASI3 (19005) — 3 recoveries, keeper (pid 42740) auto-relaunched each time within ~90s:**
  1. tick1: `startupState:"error"` + authDrift, "Safari callback capture failed" loop → killed daemon 46344 + Chrome tree + Singleton locks. Keeper relaunch OK.
  2. 22:23: booting 1000s, authDrift true, currentUrl frozen on auth page (lastActivity == boot time) → >15min-no-progress recovery → killed daemon + Chrome + locks. Keeper relaunch OK.
  3. 23:06: busy-wedge class (busyAgeMs 699,817, pendingRequestCount 12, shellSurfaceReady false) → killed daemon 57365 + Chrome + locks. Keeper relaunch OK (current daemon pid 18578).
- **ASI2 (19004) — found DEAD at t0; 7 of my relaunch attempts, 2 bug classes found and fixed:**
  - Attempt 1 died instantly: pre-written /tmp/huanxin-daemon-ASI2.pid made the daemon see its OWN pid alive → "Daemon for ASI2 already running (PID 89632)" self-exit (daemon.js:255-264 checks the pidfile with process.kill(pid,0)). Fix: never pre-write the pidfile.
  - Attempts 2-4: launchPersistentContext handshake TimeoutError (~53s) with Chrome spawned but never ready. Root cause PROVEN by raw-Chrome experiment: fresh profile copy boots in 2s; the per-env profile dir (torn by copy-under-write races from repeated kill/relaunch cycles) never boots. Fix: wipe the per-env dir; daemon's ensureProfileDir re-copies from the healthy base.
  - Attempt 8 launched after the wipe → but an EXTERNAL launch (pid 30080, 22:35 — launched by another lane/watcher, not this one) already owned 19004 → my duplicate (36590) killed; 30080 is the daemon of record.
- **ASI1 (20646) — NEVER killed (out of kill scope without demonstrated need). Log-only throughout.** Wedged-booting signature (booting 5h, authDrift, no shell) — its Chrome (95234) was launched WITHOUT the resolver pin (cmdline lacks --host-resolver-rules); the same IPv6-route bug class that the pin fixes. Recommend: manager decides if ASI1 is still needed; if yes, recover with the pinned env.

### Root causes established this cycle
1. **IPv6 route bug**: aihuanxin.cn AAAA hangs macOS; IPv4 36.212.177.181 works. Resolver pin shipped in all relaunch scripts + new Chromes (verified in process cmdlines). /etc/hosts pin STILL MISSING (4 LOUD log lines; user's sudo command pending).
2. **Auth-lock class (all 3 daemons)**: SSO session expired. All three PASSED the auth page ~22:55-23:00 (authDriftDetected:false, currentUrl on the kunlun app page) but the terminal shell never rendered (shellSurfaceReady:false) — they cycle booting/error behind the auth capture. Recovery kills are a no-op for this class (fresh profile copies carry the same expired session) → escalate, not kill. One user Safari SSO login is expected to unblock all three.
3. **ASI3 busy-wedge class**: busyAgeMs + pendingRequestCount is the wedge signal (NOT the ready flag) — documented in keepalive.md history; box-pull watch (pid 55523) polling 19005 contributes pending backlog. Recovery recipe remains the fix; the keeper's env carries the lock-watchdog fixes.

### Current state table (2026-08-31 23:31 CST)
| Port | Env | Daemon pid | State | ready | authDrift | Shell | Notes |
|---|---|---|---|---|---|---|---|
| 19005 | ASI3 (dl-c72bd81a) | 18578 | booting/error cycling | false | true (flickers false) | false | auth-locked; keeper-managed |
| 19004 | ASI2 (dl-868c196f) | 30080 | booting | false | false | false | on app page, shell pending; external launch 22:35 |
| 20646 | ASI1 (dl-9a5a098a) | 95234 | booting | false | false | false | 5h boot; no resolver pin in Chrome |

All three daemons ALIVE with responding health — no dead channel at handover. None ready:true.

### Hosts-pin status
MISSING — user must run: `echo '36.212.177.181 aihuanxin.cn' | sudo tee -a /etc/hosts && sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder` (repeated LOUD every 5th tick; 4 lines in log).

### Recommendations for next keeper cycle
- User: (1) run the sudo hosts pin; (2) one Safari SSO login (refreshes the bridge files) — expected to move all three to ready.
- Manager: decide ASI1's need (recoverable with the pinned env if required); consider throttling box-pull watch polling of 19005 (the pending backlog fed the ASI3 wedge).

---
## WEDGE DETECTOR — ARMED 2026-09-01 (fixer lane, closes the audit's propose-only gap)

- scripts/sapo_wedge_watch.py + tests/test_sapo_wedge_watch.py (11 tests, TDD RED->GREEN)
  committed; the detector ONLY ALARMS (never kills — keeper owns relaunch).
- Signals: busy=true AND busyAgeMs>120000 (busy-wedge) OR pendingRequestCount>3
  (backlog-wedge); conservative on partial payloads (missing fields never alarm).
- ARMED via nohup: `scripts/sapo_wedge_watch.py --ports 19005,19004,20646 --poll-seconds 60`
  (pid in pgrep -f sapo_wedge_watch); ticks -> /tmp/sapo_wedge_watch.log, alarms ->
  /tmp/sapo_wedge_alarms.log (one line per tick per port).
- LIVE FIND on first smoke (15:43Z): port 19005 (ASI3) was busy-wedged right then —
  busyAgeMs 400,917 / pendingRequestCount 4 — the 23:06 wedge class recurring.
  Keepers to verify relaunch happened; if the wedge persists past a keeper cycle,
  this is the launchd-port/keeper-race class (20653 vs 19005) — see audit above.
- Detector-only discipline: a wedge alarm is a KEEPALIVE-OWNER input, not an action.

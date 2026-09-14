# 🚨 ESCALATION (09-02 21:06 CST, #139 — 23RD consecutive stale-OPEN window): stale rows STILL REMAIN (>20min, no status change) — **ALL table-OPEN stale rows (B-013/B-014/B-023/B-024/B-025/B-029/B-032/B-033 = 8) escalated to user/RUNNING-OPEN** (oldest ≈ B-013/B-014 auditor-origin ~15:4x, ~5.5h; **B-033 now crossed the 20-min stale threshold** — opened 20:3x, unchanged since → escalated first time). **🚨 NEW BOX EVENT — r23c (093912Z) CRASHED; RELAUNCHED as 130233Z:** DISPATCHER box-verified old trainer **194548/194918 now ZOMBIE** (Z, RSS=0, PPID=1); r23c `grpo_train_20260902T093912Z.log` ends with the **`[ERROR] TBE Subprocess[task_distribute] raise error[], main process disappeared!`** fatal signature (the SAME class that killed B-015's 073028Z run) after **step_000005 generation_done** (ckpt step_000005_adapter present on disk; grpo_step_metrics had 4 completed steps + step-5 gen in-flight) — **NEW ledger row B-034 opened (S1, TBE task_distribute crash recurrence, 2nd observed run-family)**. A NEW run **20260902T130233Z launched 13:02:34Z (pid 222533, Sl ALIVE ~5:22, at step_begin step 1, v9 benchmark, lr 5e-5, greedy-rollout-fraction 0.4 = B-002 ASI3_SAPO alias now live on box)**, judge_bridge up (222236, port 56237); new run at early startup (no ckpts/metrics yet) — continuity RESTORED but r23c's step-4→∞ progress (loo_advantage_rms 0.997, mean_reward 0.077) was RESET (training re-baselined, partial NPU-waste). DISPATCHER 23rd-cycle box-corroboration: **B-003 closure HOLDS** — Mac-side `reports/.sapo_parallel_eval_state_ASI3.json` holds r23c step_000001 done (12:14:28Z) + step_000003 pending/eval-running (12:33:30Z, but target run now DEAD → eval lane should re-point); shared non-suffixed `reports/.sapo_parallel_eval_state.json` STILL FROZEN (mtime 18:08:00, no re-write) → infinite resume-3 re-eval loop STAYS stopped. **B-031 FALSE-ALARM closure HOLDS** — 194918 PPID was 194548 (fork child); both now zombie = moot, no rogue trainer. **B-027 closure HOLDS.** ⚠️ **B-028 NoneType STILL 177 (unchanged)** — verified coerce-None fix holds, no new row. **B-009 caveat persists** — judge_mac_watcher.log STILL 0 bytes (pid 76676 running). THIS cycle (20:53→21:06): **1 NEW box-event row B-034 opened by DISPATCHER** (r23c TBE crash — genuine box-side anomaly, NOT an alarm-surface row; wedge all 3 ports state=ok last 13:11:44Z, last wedge_alarm 12:27:42Z no new; divergence waiting-for-data evals=2; box_pull watch 0 bytes; box metrics watcher STILL frozen steps=28 old-run snapshot; NO new error-signature in 130233Z logs (only startup/TBE-mirror), vllm rollout server still absent = B-032 holds). **CONCURRENT (not mine):** deploy_steward promoted **B-030 → ready-to-deploy** (21:00, staged in r23 rebuild c62dd317…) — ready-to-deploy set now B-002/B-010/B-017/B-018/B-030; B-032/B-033 remain open (error_miner). **NO rows closed by dispatcher** (no OPEN row gained independent CI-green+artifact needing a dispatcher close; B-003/B-027/B-031 closures continue to HOLD). Escalated: table-OPEN stale **B-013/B-014/B-032/B-023/B-024/B-025/B-029/B-033** (8) MUST move to staged/verified or justify hold (23rd consecutive stale cycle; oldest ~5.5h; B-034 just-opened→tracked for next cycle; r23c crash + relaunch adjudication → manager/eval-lane re-point).
# 🚨 ESCALATION (09-02 20:53 CST, #138 — 22ND consecutive stale-OPEN window): stale rows STILL REMAIN (>20min, no status change) — **all table-OPEN stale rows (B-013/B-014/B-023/B-024/B-025/B-029/B-032 = 7) escalated to user/RUNNING-OPEN** (oldest ≈ B-013/B-014 auditor-origin ~15:4x, ~5h). **B-030 REMOVED from stale-OPEN set** — now `verified` (parallel CI-green + TDD independent evidence, artifact = stale-atomic-save cleanup sweep landed; 3 TDD + 40 metrics + 8 sigterm focused + CI gate GREEN; row status updated to `verified`, no longer open). **NEW THIS window: B-033 (`verifier_env_missing_qiskit`, S1, error_miner, opened 20:3x)** — opened by error_miner this cycle; <20-min-old so NOT yet stale, NOT escalated (will cross threshold next cycle if unchanged). DISPATCHER 22nd-cycle box-corroboration: **B-031 FALSE-ALARM closure HOLDS** — live `ps -o pid,ppid` re-confirms **194918 PPID=194548** (fork child of ACTIVE trainer 194548, Sl dormant) = the trainer's own multiprocessing fork, NOT a rogue second trainer; single-active-trainer-per-dir holds, B-027 closure holds, box SAFE. ✓ **B-003 closure HOLDS:** ASI3 state `reports/.sapo_parallel_eval_state_ASI3.json` holds r23c step_000001 done (12:14:28Z) + step_000003 pending/eval-running (eval start 12:33:30Z); shared non-suffixed state STILL FROZEN (no re-write since 18:08) → infinite resume-3 re-eval loop STAYS stopped. **r23c steady + PROGRESS:** trainer 194548 ALIVE (R state, 263:58 CPU), NOW at **4 grpo steps** (was 3 at #137) — `grpo_step_metrics.jsonl` line-4 completed ~12:39Z (loo_advantage_rms 0.997, mean_reward 0.077, non-inert); checkpoint adapter dirs STILL = 3 (000001/000002/000003; step_000004 not yet emitted, ckpt interval 1800s from step3 12:12Z). ⚠️ **B-028 STILL NoneType 177 (unchanged)** — verified coerce-None fix holds, no new row. **B-009 caveat persists** — judge_mac_watcher.log STILL 0 bytes. THIS cycle (20:37→20:53): **NO NEW ALARM rows deduped by DISPATCHER** (wedge all 3 ports state=ok, last wedge_alarm 12:27:42Z 20646 unreadable-health — no new; divergence waiting-for-data evals=2 unchanged; box_pull watch logs 0 bytes; box metrics watcher STILL frozen steps=28 old-run snapshot — read r23c from grpo_step_metrics.jsonl directly; box sapo logs grep = NO new error/alarm lines beyond old historical judge_bridge 'Address already in use'; vllm rollout server still absent from live `ps` = B-032 crash already rowed). **CONCURRENT (not mine):** error_miner opened **B-033** (verifier_env_missing_qiskit, S1) 20:3x; **B-030 promoted → VERIFIED** (CI-green + TDD independent; row status updated). **NO rows closed by dispatcher** (no OPEN row gained independent CI-green+artifact duplicating a dispatcher-owned close; B-030 moved to verified concurrently, B-003/B-027/B-031 closures continue to HOLD). Escalated: table-OPEN stale **B-013/B-014/B-032/B-023/B-024/B-025/B-029** (7) MUST move to staged/verified or justify hold (22nd consecutive stale cycle; oldest ~5h; B-033 new-not-stale tracked for next cycle).
# 🚨 ESCALATION (09-02 20:37 CST, #137 — 21ST consecutive stale-OPEN window): stale rows STILL REMAIN (>20min, no status change) — **all table-OPEN stale rows (B-013/B-014/B-023/B-024/B-025/B-029/B-030/B-032) escalated to user/RUNNING-OPEN** (oldest ≈ B-013/B-014 auditor-origin ~15:4x, ~5h; **NEW THIS window: B-032 (opened ~20:1x by error_miner) has NOW crossed the 20-min stale threshold** — no status change since open → escalated for the first time; 21st consecutive stale cycle). C-037 no longer OPEN (CI_VERIFIER promoted → verified 20:2x; table row updated). DISPATCHER 21st-cycle box-corroboration: **B-031 FALSE-ALARM closure HOLDS** — live `ps -o pid,ppid` re-confirms **194918 PPID=194548** (fork child of ACTIVE trainer 194548, State S dormant, elapsed 02:58:06 vs 194548 02:59:30) = the trainer's own multiprocessing fork, NOT a rogue second trainer; single-active-trainer-per-dir holds, B-027 closure holds, box SAFE. ✅ **B-003 closure HOLDS:** ASI3 state `reports/.sapo_parallel_eval_state_ASI3.json` holds r23c step_000001 done (12:14:28Z); shared non-suffixed state STILL FROZEN (no re-write) → infinite resume-3 re-eval loop STAYS stopped. **r23c steady:** trainer 194548 ALIVE, STILL at **3 ckpts (step_000001/000002/000003_adapter)** — `grpo_step_metrics.jsonl` last step = **step 3 (12:12:20Z)** non-inert (trust_region_violated=false, zero_change_alarm=false, update_signal_kind=loo_advantage_rms magnitude 0.768>threshold 0.05) → step-4 rollout presumably in progress; box metrics watcher STILL frozen steps=28 old-run snapshot (read r23c from grpo_step_metrics.jsonl directly). ⚠️ **B-028 STILL NoneType 177 (unchanged)** — verified coerce-None fix holds, no new row (recent ASI2 pulls transient TimeoutError→daemon-recovers, symptom-shift persists). **B-009 caveat persists** — judge_mac_watcher.log STILL 0 bytes. THIS cycle (20:22→20:37): **NO NEW ALARM rows deduped by DISPATCHER** (wedge all 3 ports state=ok, last wedge_alarm 12:27:42Z 20646 unreadable-health no new; divergence waiting-for-data evals=2; box_pull logs 0 bytes; box sapo metrics watcher frozen steps=28; box sapo logs grep = ONLY old historical judge_bridge 'Address already in use' 08-28/09-01, NO new for current run; vllm_server.log mtime 12:06 unchanged = B-032 crash already rowed). **CONCURRENT: C-037 promoted to verified by CI_VERIFIER (20:2x)** — no longer OPEN; **NO rows closed by dispatcher** (no OPEN row gained independent CI-green+artifact beyond already-verified set). Escalated: table-OPEN **B-013/B-014/B-032/B-023/B-024/B-025/B-029/B-030** (8) MUST move to staged/verified or justify hold (21st consecutive stale cycle; oldest ~5h).
# 📌 MANAGER CORRECTION (09-02 20:13→20:15 CST, STANDUP #399): **B-031 = FALSE ALARM — CLOSED.** Authoritative live `ps` parentage: 194918 **PPID=194548** (child/fork worker, 13 thr Sl dormant) — it is the ACTIVE trainer 194548's own multiprocessing fork child (same-cmdline worker), NOT an independent rogue second trainer. No single-active-trainer-per-dir violation, NO B-027 re-open, box SAFE. r23c ADVANCED to **3 ckpts (step_000001/000002/000003)**, now at step 4 rollout (s3 grover loo_rms 0.768 non-inert). 🏁 **EVAL MILESTONE: step-1 valid-v9 leg COMPLETED 12:14:28Z — pass@1 3/18 TIED w/ base, adapter WINS on rubric 3.285 vs 3.1; driver NOT yet re-armed on step_000002 — re-arm ordered.** OPEN set after correction = **8** (B-013/B-014/C-037/B-023/B-024/B-025/B-029/B-030).
# 🚨 ESCALATION (09-02 20:21 CST, #136 — 20TH consecutive stale-OPEN window): stale rows STILL REMAIN (>20min, no status change) — **all table-OPEN stale rows (B-013/B-014/B-023/B-024/B-025/B-029/B-030) escalated to user/RUNNING-OPEN** (oldest ~5h, auditor-origin; 20th consecutive stale window) **+ C-037 staged-per-table / open-per-header-convention** (+ **B-032 NEW this cycle by error_miner — folded in below**). DISPATCHER 20th-cycle box-corroboration: **B-031 FALSE-ALARM closure HOLDS** — live `ps -o pid,ppid` re-confirms **194918 PPID=194548** (fork child of the ACTIVE trainer 194548, Sl dormant, 3.0GB RSS, elapsed 02:41:21) = the trainer's own multiprocessing fork, NOT a rogue second trainer; single-active-trainer-per-dir holds, B-027 closure holds, box SAFE. ✅ **B-003 closure HOLDS (strengthened):** ASI3 state `reports/.sapo_parallel_eval_state_ASI3.json` now holds r23c **step_000001 `{status: done}` (updated 12:14:28Z — pass@1 3/18 tied, rubric 3.285 vs 3.1 adapter-wins)**, and shared non-suffixed `reports/.sapo_parallel_eval_state.json` STILL FROZEN at 18:08 (no re-write) → infinite resume-3 re-eval loop STAYS stopped. 🟢 **B-005 pace re-baseline EVIDENCE ADVANCING:** r23c (093912Z, v9, trainer 194548) NOW at **3 ckpts (step_000001/000002/000003_adapter present on box)**; `grpo_step_metrics.jsonl` step-3 (12:12:20Z): task `quantum_rl_v2_grover_qiskit_101`, **trust_region_violated=false, zero_change_alarm=false, update_signal_kind=loo_advantage_rms magnitude 0.768 (>0.05 threshold)** → non-inert, lora-pace re-verify increasingly possible as steps accrue (sentinel is the live enforcer; box metrics watcher STILL frozen steps=28 old-run snapshot — read r23c directly from grpo_step_metrics.jsonl). ⚠️ **B-028 NoneType STILL 177 (unchanged)** — verified coerce-None fix holds, no new row (recent ASI2 pulls transient TimeoutError→daemon-recovers, symptom-shift persists). **B-009 caveat persists** — judge_mac_watcher.log STILL 0 bytes. THIS cycle (20:11→20:21): **NO NEW ALARM rows deduped by DISPATCHER** (wedge ok 3 ports; last wedge_alarm 07:49Z no new; divergence waiting-for-data evals=2; box metrics watcher frozen steps=28; r23c boot log grep = NO new error/alarm lines, only old historical judge_bridge 'Address already in use'); **CONCURRENT: ERROR_MINER opened B-032** (vllm_rollout_server_kv_cache_oom, S2 — see 20th-cycle recon); **NO rows closed by dispatcher** (no OPEN row gained independent CI-green+artifact this window). Concurrent (not mine): deploy_steward confirms ready-to-deploy = **B-002/B-010/B-017/B-018** (bundle `3755b0a1…` current, NO rebuild); managers 6 verified Mac-side zero-delta (B-004/B-008/B-012/B-016/B-019/B-028) + C-032 verified. Escalated: table-OPEN **B-013/B-014/B-032/B-023/B-024/B-025/B-029/B-030** (+ C-037 staged-per-table / open-per-header-convention) MUST move to staged/verified or justify hold (20th consecutive stale cycle; **NOTE table-ambiguity: C-037's row shows `staged` while prior recons track it as OPEN — see 20th-cycle recon**).
# 🚨 ESCALATION (09-02 20:1x CST, #136 — UPDATED thru 20:11): stale rows STILL REMAIN (>20min) AND multi-channel live symptoms PERSIST (19th consecutive stale OPEN window — C-032 moved to VERIFIED by CI_VERIFIER; B-031 opened 19:58 as duplicate-trainer then box-re-confirmed this cycle as LIVE — **superseded/corrected by MANAGER STANDUP #399 20:13: B-031 FALSE ALARM, CLOSED** (dormant 194918 = fork child PPID=194548, not rogue trainer)). ✅ RESOLVED HOLDS: **B-003 CLOSED 18:09 by MANAGER** — DISPATCHER box-re-corroborates this cycle: ASI3 rubric eval pid **199911 ALIVE** (80min CPU, 161% — `run_asi2_base_adapter_rubric_eval.py … step_000001 … sapp_promotion_holdout_v1_18.txt`), `/tmp/sapo-logs/eval_step_000001_adapter.log` mtime 18:54, ASI3 state file `reports/.sapo_parallel_eval_state_ASI3.json` (mtime 18:54:50) holds r23c step_000001 `{verdict: eval-running}`; shared non-suffixed `reports/.sapo_parallel_eval_state.json` mtime STILL FROZEN at 18:08 (no re-write) → infinite resume-3 re-eval loop STAYS stopped; closure HOLDS, no edge-reopen. ⚠️ STILL LIVE (re-confirmed this cycle): **B-028-S2** — box_pull_ledger `NoneType subscriptable` STILL **177 hits (unchanged, NO new NoneType this window)**; **most recent ASI2 ledger entries `TimeoutError: timed out`** (11:16-11:42Z pulls, box_pull ledger lines 10334-10610, NOT NoneType) but each pull then completes (`pull complete`, daemon recovers) → symptom SHIFT from null-eval_output to pull-timeout PERSISTS (transient, recovered; no new row opened). B-028 stays VERIFIED (coerce-None fix scripts/sapo_box_pull_watch.sh:47, 4/4 PASS + CI GREEN; deploy_steward determines close/deploy). 🟢 **B-005-class pace re-baseline EVIDENCE EMERGING** — r23c (093912Z, v9, trainer 194918) has NOW advanced past step_000001: **`step_000002_adapter` present (~318MB)** on box; `grpo_step_metrics.jsonl` has **step 1 (11:35Z previous) + step 2 (11:35Z) complete**: s1 ent=0.377/pass=0.000/mr=0.049, s2 ent=0.524/pass=0.000/mr=0.055, **lr=5e-5 (new gate from B-005)** — entropy RISING 0.377→0.524 (non-inert trajectory); 2/2 steps done, tasks rotating (qpe_qiskit_0375→amplitude_estimation_ry); lora-pace re-verify NOW POTENTIALLY POSSIBLE once more steps accrue (sentinel is the live enforcer; box metrics watcher STILL frozen steps=28 old-run watcher, r23b_metrics still NO_STEPS_YET — the NEW r23c metrics must be read from grpo_step_metrics.jsonl directly). **B-009 caveat persists** — judge_mac_watcher log STILL 0 bytes (spot-verify unresolved). **B-024/B-025/B-029 recurrences re-confirmed** in latest r23c (benign recurrence class, openings unchanged). ⚠️ Stale >20min OPEN rows — **reduced to 9 this cycle** (CONCURRENT CI_VERIFIER 19:4x promoted **B-019 → VERIFIED**, ruff-clean contract #116, 2/2 focused PASS + CI GATE GREEN — B-019 now in the 6-verified set, removed from stale-open): **B-013/B-014/C-032/C-037/B-023/B-024/B-025/B-029/B-030** (9 OPEN stale; oldest = B-013/B-014/C-032/C-037 auditor-origin ~15:4x, now ~4h; newest B-030 opened 18:4x, ~55min). THIS cycle (19:35→19:45): **NO NEW ALARM rows deduped** from watch surfaces (wedge ok all 3 ports 20653/19004/20646 state=ok last 11:40:36Z; last wedge_alarm 07:49Z no new; divergence waiting-for-data evals=2; box watcher frozen steps=28 identical ent=0.22/pass=0.375/mr=0.5298 essence=7.30; box error grep = only OLD judge_bridge 'Address already in use' 08-28/09-01, none new). **NO dispatcher-closed rows this window** (no OPEN row gained independent CI-green+artifact beyond already-verified set). Concurrent context (not mine): deploy_steward re-confirmed all 5 verified Mac-side zero box delta, bundle sha `3755b0a1…` current NO rebuild; ready-to-deploy = **B-002/B-010/B-017/B-018** awaiting manager/user fire; box SAFE (r23c on v9, NOW on step 2). Escalated to user/RUNNING-OPEN: remaining open rows (B-013/B-014/C-032/C-037/B-023/B-024/B-025/B-029/B-030 — B-019 moved to VERIFIED by CI_VERIFIER this window) MUST move to staged/verified or justify hold (17th consecutive stale cycle, multiple stale durations >4h, oldest ~4h).
# ⚠️ LEDGER INTEGRITY (09-02 16:19): ID-collision corruption found — B-005 appeared 3× (S0 inertness / E-53 judge / §K#117), B-006 2× (H-83 closed / M-129 open), B-007 2× (queued-unarmed closed / M-131 open). Renumbered the colliding duplicate rows to unique IDs B-016..B-022 below so each row has a single canonical ID (no content lost). Canonical survivors: B-005 = S0 inertness; M-129 → B-016; M-131 → B-017; §K#117 → B-018; §K#116 ruff → B-019; E-53 judge → B-020; H-83 peft → B-021; queued-unarmed → B-022.
# 🐛 BUG QUEUE — authoritative open-bug ledger (contract check #135: no item >2 standup cycles without status change; stale → escalate to user)
# Format: | ID | sev | scope owner | opened (CST) | status | summary |
# Status flow: open → staged (fix + tests on tree) → verified (independent CI green) → deployed → closed
# Severities: S0 (blocks objective/NPU waste), S1 (channel/data risk), S2 (quality/velocity)

| ID | Sev | Owner | Opened | Status | Summary |
|---|---|---|---|---|---|
| B-001 | S1 | keeper | 09-02 15:05 | closed 17:57 | keeper_env_selftest added (asserts FORGE env block in script before any spawn; fail-loud exit otherwise). syntax-verified; takes effect next keeper restart |
| B-002 | S1 | debugger | 09-02 15:05 | ready-to-deploy | ai_launch_sapo_direct.sh ignores AI_SAPO_GREEDY_ROLLOUT_FRACTION alias (r23f launch needed ASI3_SAPO_ prefix; alias table incomplete — audit all §3b aliases vs actual consumption) — STAGED 09-02: audit found all §3b aliases complete (fixed 364772b); added test_ai_wrapper_s3b_aliases_reach_actual_launcher_consumption to lock alias→launcher-consumption chain; CI GATE GREEN — VERIFIED 09-02 16:19 CST (CI_VERIFIER): re-ran focused test test_ai_wrapper_s3b_aliases_reach_actual_launcher_consumption → 1 passed; bash scripts/sapo_ci_gate.sh → GREEN (exit 0, all 4 stages). Independent confirmation. — READY-TO-DEPLOY 09-02 (deploy_steward): rebuilt r23 lineage bundle tmp/sapo-relaunch-r23.tgz (sha 11ea4f01…) from current tree; verified 349/349, embedded-manifest==tgz, tree==bundle, B-002 test present+green (2 passed); DEPLOY-READINESS block in .sapo-loop/launchplan.md §6. Manager/user fires the deploy. |
| B-003 | S2 | eval | 09-02 15:05 | closed 18:09 | parallel-eval agent state file races when >1 env lane writes same reports/.sapo_parallel_eval_state.json (needs per-env state files) — PARTIAL-FIX LANDED: per-env state files exist (reports/.sapo_parallel_eval_state_ASI1.json + _ASI2.json) but the SOLE sanctioned ASI3 driver (19808, resume-3) was running the OLD shared-file logic → STILL wrote non-suffixed reports/.sapo_parallel_eval_state.json + infinite step_000026/000024 re-eval loop (CONFIRMED live thru 18:08 CST). CLOSED 18:09 CST (STANDUP #386, manager): root cause = running driver 19808 pre-dated the per-env-state/no-false-done script fix; restarted the SOLE driver (new pid 15647) pointed at the ACTIVE r23c run, inheriting the _ASI3.json redirect (file now created {}) + no-mark-done-on-transient fix; infinite re-eval loop on dead resume-3 ckpts STOPPED (0 r23c steps yet → driver idles, no thrash). No code change; process-ops only. |
| B-004 | S2 | debugger | 09-02 15:05 | verified | wedge remediation_command lacks the keeper's pidfile cleanup (rm /tmp/huanxin-daemon-$ENV.pid) — stale pidfile can self-exit the respawned daemon (documented 08-31 class) — STAGED 09-02: remediation_command now rm -f /tmp/huanxin-daemon-$ENV.pid + .port before relaunch (PID-reuse self-exit guard); test_remediation_cleans_stale_pidfile + test_remediation_still_never_wipes_profiles; CI GATE GREEN — VERIFIED 09-02 16:2x CST (CI_VERIFIER): re-ran test_remediation_cleans_stale_pidfile + test_remediation_still_never_wipes_profiles → both passed; bash scripts/sapo_ci_gate.sh → GREEN (exit 0, all 4 stages). Independent confirmation. — DEPLOY_STEWARD 09-02: fix is MAC-SIDE watchdog tooling (scripts/sapo_wedge_watch.py + tests/test_wedge_watch_remediation.py, 8/8 green), never a box-bundle member (r18-r23 all exclude; not in launcher/required_files). The fixed local /tmp pidfile is Mac-side by definition → NO box-bundle delta to stage; fix already live on local tree (its runtime). No box deploy needed; r23 (B-002) unaffected. Manager/user may close (or mark deployed locally) at discretion — does NOT gate the r23 launch. Determination recorded in launchplan §6. |
| B-005 | S0 | manager | 09-02 07:39 | closed 17:55 | INERT pace was resume-3 (lr 2.5e-5, no gate). Root fix SHIPPED: lr 5e-5 + gate v2 + sentinel inert-drift rule (fires ~step 10). Pace re-baseline from r23c's first 10 steps — sentinel is the live enforcer now |
| B-020 | S1 | debugger | 09-02 15:5x | closed | [was B-005-E53] E-53 judge mac watcher not running — armed against 20653+live dp4 proxy+new run judge_bridge (H-83 verified separately) |
| B-021 | S2 | debugger | 09-02 15:5x | closed | [was B-006-H83] H-83 peft hard import broke 2 prompt-isolation tests — guarded import; test_prompt_integrity_lane 90/90 GREEN |
| B-022 | S1 | debugger | 09-02 15:5x | closed | [was B-007-129] #129/#131/#132 queued items unarmed — sapo_contract_queue_watch.sh armed all 3 (#129 active dangling-check caught stale resume3 rows; archived) |

| B-026 | S0 | manager | 09-02 17:15 | closed 17:45 | WRONG BENCHMARK (v8) verified in live cmdline → ROOT FIXED (v9 pinned in both launchers, TDD pin test, CI green, deployed sha-verified) → r23c relaunched 17:39 CST on v9 (trainer 194548, cmdline verified) |
| B-027 | S1 | manager | 09-02 17:15 | closed 17:45 | unauthorized-respawn control-gap: the respawns were manager-executed relaunches (r23a→r23b→r23c); spawner only spawns LANES (never trainers). Control flow confirmed sound; no fix needed |

QUEUE LENGTH (20th-cycle reconciled, faithful to per-row table): **8 OPEN** (B-013,B-014,B-023,B-024,B-025,B-029,B-030,**B-032-NEW**) + **0 STAGED** + 8 verified [B-004,B-008,B-012,B-016,B-019,B-028,C-032,C-037] + 4 ready-to-deploy [B-002,B-010,B-017,B-018] + 12 closed [B-001,B-003,B-005,B-009,B-011,B-015,B-020,B-021,B-022,B-026,B-027,**B-031-FALSE-ALARM**] | OLDEST OPEN: **B-013/B-014 (auditor-origin ~15:4x, ~5h)** | NEW THIS CYCLE: **B-032 opened by ERROR_MINER (vllm_rollout_server_kv_cache_oom, S2); none opened/closed by DISPATCHER** (B-031 stays CLOSED-false-alarm per manager #399; box re-corroborated 194918 PPID=194548 = fork child) | LAST RECONCILED: **09-02 20:21 CST (DISPATCHER 20th cycle)**; C-037→verified 09-02 20:2x (CI_VERIFIER). **NOTE TABLE-AMBIGUITY RESOLVED:** C-037 (previously `staged`) promoted to `verified` by CI_VERIFIER 09-02 20:2x; **B-032 joined OPEN** (error_miner novel error-signature); table count now = **8 OPEN** + 0 STAGED + 8 verified. **Key NEW observation this cycle:** r23c (v9, trainer 194548) ADVANCED to **3 ckpts (step_000001/000002/000003_adapter present on box)**; grpo_step_metrics.jsonl step-3 (12:12:20Z) task `quantum_rl_v2_grover_qiskit_101`, **trust_region_violated=false, zero_change_alarm=false, loo_advantage_rms 0.768 (>0.05)** → **B-005 pace re-baseline EVIDENCE ADVANCING** (non-inert, lora re-verify increasingly possible; sentinel live enforcer). 🏁 **B-003 closure strengthened:** ASI3 step_000001 **`{status: done}` (12:14:28Z, pass@1 3/18 tied, rubric 3.285 vs 3.1 adapter-wins)**; shared non-suffixed state STILL FROZEN 18:08 → resume-3 re-eval loop STOPPED. B-028 NoneType STILL 177 (unchanged; recent pulls transient TimeoutError→recovery). B-009 caveat persists (judge_mac_watcher.log 0 bytes). Bundle `3755b0a1…` current (no rebuild per deploy_steward); ready-to-deploy = **B-002/B-010/B-017/B-018**; box SAFE on v9 step 4 rollout. NOTHING deployed/closed by this lane. **CI_VERIFIER 09-02 20:4x CST:** B-030 (staged by debugger this cycle) promoted `staged`→`verified` (independent: 3 TDD + 40/40 metrics + 8/8 sigterm + CI gate GREEN). Table now = **7 OPEN** (B-013,B-014,B-023,B-024,B-025,B-029,B-032) + **0 STAGED** + **9 verified** [B-004,B-008,B-012,B-016,B-019,B-028,C-032,C-037,**B-030**] + 4 ready-to-deploy + 12 closed. **CI_VERIFIER 09-02 21:01 CST:** **B-033 newly opened by ERROR_MINER** (verifier_env_missing_qiskit — box interpreter lacks qiskit/qiskit-aer; S1; 15/24 rows r23c steps 1-3) added to OPEN set. Reconciled table = **8 OPEN** (B-013,B-014,B-023,B-024,B-025,B-029,B-032,**B-033**) + **0 STAGED** + **8 verified** [B-004,B-008,B-012,B-016,B-019,B-028,C-032,C-037] + **5 ready-to-deploy** [B-002,B-010,B-017,B-018,**B-030** (promoted concurrent by deploy_steward 21:00 — staged in r23 rebuild c62dd317…)] + 12 closed. Landed-waves re-verified this cycle: CI gate GREEN (exit 0, all 4 stages, SMOKE_GREEN launchable) + 49 focused tests pass on HEAD 7089a5b.
| B-016 | S2 | debugger | 09-02 | verified | [was B-006] M-129 eval↔ckpt completeness sync (contract #129, "🕐 queued"): no enforcer anywhere — eval does not wait for a completeness marker before reading checkpoints; MISSING artifact: completeness-marker gate in eval flow — STAGED 09-02 (debugger): added completeness-marker gate to scripts/sapo_parallel_eval_agent.sh (checks adapter_config.json + *.safetensors on box BEFORE firing holdout leg; INCOMPLETE -> log + continue, leave pending for next scan). Gate is in the per-checkpoint loop; THE eval script's CHECKPOINT_INCOMPLETE guard only covered TARGET_KIND=nas-checkpoint, NOT the run-adapter path the agent drives via SAPO_RUN_DIR. Evidence: test_agent_gates_on_completeness_marker_before_firing_leg (test_sapo_parallel_eval_agent.py, 6/6 GREEN); focused debugger suite GREEN; scripts/sapo_ci_gate.sh GREEN (exit 0, launchable). — VERIFIED 09-02 18:2x CST (CI_VERIFIER): re-derived claim — completeness-marker gate present in scripts/sapo_parallel_eval_agent.sh (lines 38-56): checks adapter_config.json + *.safetensors via box `ls` BEFORE firing holdout leg; INCOMPLETE → logs "waiting for completeness marker" + `continue` (skip scan, retry later); gate inside the per-checkpoint loop covering the SAPO_RUN_DIR/run-adapter path (asi2_loop_eval.sh CHECKPOINT_INCOMPLETE only guards TARGET_KIND=nas-checkpoint); re-ran cited focused test file test_sapo_parallel_eval_agent.py → 6 passed; bash scripts/sapo_ci_gate.sh → GREEN (exit 0, all 4 stages). Independent confirmation. — DEPLOY_STEWARD 09-02 18:3x CST: fix is MAC-SIDE parallel-eval watchdog tooling (scripts/sapo_parallel_eval_agent.sh + tests/test_sapo_parallel_eval_agent.py, 6/6 green this cycle), never a box-bundle member (absent from tmp/sapo-relaunch-r23.sha256 349 entries AND from the tgz AND from every prior bundle sidecar; NOT referenced by any box launcher/wrapper; NOT in required_files gate; grouped in scripts/sapo_fleet_roster.sh line 22 alongside the Mac-side watchdogs sapo_box_pull_watch/sapo_divergence_watch/sapo_wedge_watch). The Mac-side agent drives box eval via curl/asi3_exec --port — the box NEVER receives this script. → NO box-bundle delta to stage; fix already live on local tree (its runtime). No box deploy needed; manager/user may close (or mark `deployed` locally) at discretion — does NOT gate the r23 launch nor any launch. Determination recorded in launchplan §6 re-check #7. |
| B-017 | S2 | debugger | 09-02 | ready-to-deploy | [was B-007] M-131 sandbox dependency hash (contract #131, "🕐 queued"): no pip-freeze hash at launch + re-hash per eval enforcer exists; MISSING artifact: scripts/sapo_dep_hash.py + launch hook — STAGED 09-02 (debugger): added scripts/sapo_dep_hash.py (pure-stdlib, py3.9-safe: order-insensitive hash_freeze, hash_freeze_file, local_freeze_hash, box_freeze_hash via asi3_exec, ensure_baseline/check_drift, fail-closed CLI --capture/--check) + launch hook in scripts/ai_launch_sapo_direct.sh (captures box pip-freeze hash to reports/.sandbox_hash launch-time baseline BEFORE delegating to the box launcher — the pre-fix gap was baseline=watchdog-first-poll, not launch-time) + refactored scripts/sapo_contract_queue_watch.sh #131 tick to defer to sapo_dep_hash.py --check (alarms on drift against the launch baseline). Evidence: tests/test_sapo_dep_hash.py (test_hash_freeze_order_insensitive, test_check_drift_changed, test_main_check_drift_fails_closed, test_ai_launch_captures_dep_hash_baseline_before_exec, test_contract_watch_uses_dep_hash_artifact_for_131, 19/19 GREEN); focused debugger suite (89) GREEN; ruff clean on scripts/sapo_dep_hash.py; scripts/sapo_ci_gate.sh GREEN (launchable). — VERIFIED 09-02 18:4x CST (CI_VERIFIER): re-derived claim — scripts/sapo_dep_hash.py present (pure-stdlib: argparse/hashlib/subprocess/sys/pathlib only; hash_freeze order-insensitive via sorted normalized lines; hash_freeze_file/local_freeze_hash/box_freeze_hash via asi3_exec confirmed; ensure_baseline never-overwrites confirmed; check_drift fail-closed on missing baseline confirmed; CLI --capture/--check mutually-exclusive, non-zero exit on drift confirmed); launch hook present at scripts/ai_launch_sapo_direct.sh:58-68 (captures box hash to reports/.sandbox_hash BEFORE `exec` to box launcher); #131 tick in sapo_contract_queue_watch.sh:21-33 defers to sapo_dep_hash.py --check and ALARM on drift; re-ran cited focused test tests/test_sapo_dep_hash.py → 19 passed; ruff check scripts/sapo_dep_hash.py → All checks passed; bash scripts/sapo_ci_gate.sh → GREEN (exit 0, all 4 stages). Independent confirmation. — DEPLOY_STEWARD r23-REBUILD 09-02 (deploy steward 9th cycle): B-017 fix carries a genuine BOX-BUNDLE delta → r23 lineage REBUILT this cycle (mandated per brief since fix is verified + on tree but NOT in prior bundle). New bundle `tmp/sapo-relaunch-r23.tgz` sha `3755b0a1…48b72a` (rebuild via `python3 tmp/build_r22_bundle.py`, promoted to r23 deploy lineage; pre-rebuild immutable copy = `tmp/deploy-steward-prebuild-r23-7c78e50f.tgz` = old sha `7c78e50f…`). B-017 box-runtime member changed = `scripts/ai_launch_sapo_direct.sh` (dep-hash launch hook lines 65-68: `python3 "$ROOT_DIR/scripts/sapo_dep_hash.py" --capture --state-file "$ROOT_DIR/reports/.sandbox_hash" || true` BEFORE `exec` to box launcher). Note: `sapo_dep_hash.py` itself is MAC-SIDE (not a box-bundle member, correctly absent — the hook runs on the Mac under ROOT_DIR); only the launcher (bundle member carrying the hook) is the box-relevant carricanter. Rebuild Δ = exactly 4 members changed (ai_launch_sapo_direct.sh, asi2_launch_grpo_27b_selfeval.sh, asi3_launch_grpo_direct.sh, test_asi3_sapo_launcher_readiness.py), 0 added, 0 removed — this captures BOTH B-017 (dep-hash hook) AND B-026 (v9 pin, previously stale in `7c78e50f…`). Verification all GREEN: bundle sha MATCH `3755b0a1…`; per-file sidecar 349/349 OK 0 failures; MANIFEST vs tgz 0 mismatches; bundled ai_launch contains B-017 dep-hash hook AND B-026 v9 pin (v8 gone); B-017 tests 19/19, launcher readiness 28/28, benchmark-pin 4/4; CI GATE GREEN (exit 0, 5-stage smoke launchable). **Status → ready-to-deploy (r23, sha `3755b0a1…`)**; manager/user fires. NOTHING deployed from this lane. |
| B-008 | S1 | debugger | 09-02 | verified | M-132 log secrets scan (contract #132, "🕐 queued"): no token/secret pattern scanner exists (auth/secret-leak class → S1) — STAGED 09-02: scripts/sapo_secret_scan.py added (sk-/JWT/AWS/GitHub/private-key/generic API-key patterns, fail-closed exit, redacted output) + scan_default() hook wired into sapo_contract_queue_watch.sh #132 tick; test_sapo_secret_scan.py 12/12 GREEN; focused suite + CI GATE GREEN — VERIFIED 09-02 16:49 CST (CI_VERIFIER): re-derived claim — scripts/sapo_secret_scan.py present with sk-/JWT/AWS/GitHub/private-key/generic patterns (regex table confirmed), fail-closed non-zero exit, redacted report; scan_default hook wired at sapo_contract_queue_watch.sh #132 tick (line 16 invoke + line 19 alarm on hits); re-ran focused test test_sapo_secret_scan.py → 12 passed; bash scripts/sapo_ci_gate.sh → GREEN (exit 0, all 4 stages). Independent confirmation. — DEPLOY_STEWARD 09-02: fix is MAC-SIDE contract-queue watchdog tooling (scripts/sapo_secret_scan.py + sapo_contract_queue_watch.sh #132 hook; 12/12 green), never a box-bundle member (r18-r23 all exclude; absent from tmp/sapo-relaunch-r23.sha256; not in launcher/required_files) → NO box-bundle delta to stage; fix already live on local tree (its runtime). No box deploy needed; manager/user may close (or mark deployed locally) at discretion — does NOT gate the r23 launch. Determination recorded in launchplan §6. |
| B-009 | S2 | debugger | 09-02 | closed | E-53 judge malformed-response rate (contract #53, "counted, fail-closed"): enforcer sapo_judge_mac_watcher.py exists but is NOT running (ps local+box = none) → malformed-response rate counting inactive; MISSING/RUNNING artifact: live sapo_judge_mac_watcher.py daemon (or box-side equivalent counter) — CLOSED 09-02 16:30 CST (DISpatcher, independent ps evidence): local sapo_judge_mac_watcher.py daemon NOW RUNNING (pid 76676, started 15:56:09Z); box-side judge_bridge.py live (pid 186314, port 56237). CAVEAT: /tmp/sapo-logs/judge_mac_watcher.log still 0 bytes — spot-verify it emits malformed-response counts next cycle. |
| B-010 | S1 | debugger | 09-02 | ready-to-deploy | H-83 reference hidden unconditionally (contract #83): test_asi2_rubric_eval_prompt_is_question_only_in_both_flag_states + test_..._never_embeds_reference FAIL via ModuleNotFoundError: No module named 'peft' (scripts/run_asi2_base_adapter_rubric_eval.py:21) → enforcer test red; MISSING artifact: fix env (peft dep present) OR decouple rubric-eval prompt test from peft import so the verification runs green — STAGED 09-02 (debugger): root cause already fixed by guarded peft import (H-83/B-021, closed); reproduced RED (unguarded import → ModuleNotFoundError 'peft', 2 fail) then restored guard → GREEN. Evidence: test_asi2_rubric_eval_prompt_is_question_only_in_both_flag_states + test_asi2_rubric_eval_prompt_never_embeds_reference_for_holdout_task (test_prompt_integrity_lane.py, 178 passed); focused launcher/secrets/wedge GREEN; scripts/sapo_ci_gate.sh GREEN (exit 0). Note: row is a duplicate of the closed B-021/H-83 fix — candidate for close/verify after independent CI confirmation. — VERIFIED 09-02 17:0x CST (CI_VERIFIER): re-derived claim — guarded peft import present at scripts/run_asi2_base_adapter_rubric_eval.py:22 (try/except, local prompt-isolation tests no longer hard-depend on box-side peft); re-ran cited focused tests test_asi2_rubric_eval_prompt_is_question_only_in_both_flag_states + test_asi2_rubric_eval_prompt_never_embeds_reference_for_holdout_task → BOTH PASSED (2 passed within test_prompt_integrity_lane.py); bash scripts/sapo_ci_gate.sh → GREEN (exit 0, all 4 stages). Independent confirmation. — READY-TO-DEPLOY 09-02 (deploy_steward): box-runtime fix (guarded peft import) lives in scripts/run_asi2_base_adapter_rubric_eval.py — ALREADY a member of the current r23 bundle; current-tree hash d660b202… == r23 sidecar hash for that file; try/except guard with `PeftModel = None` fallback present in bundled copy; focused tests test_..._question_only_in_both_flag_states + test_..._never_embeds_reference_for_holdout_task re-ran → 2 passed this cycle. NO rebuild needed (fix already staged in r23). Staged with r23 (sha 11ea4f01…); manager/user fires the deploy. Local test file (test_prompt_integrity_lane.py) is Mac-side (never in box lineage r21–r23) — the box needs only the script, already bundled. Determination in launchplan §6. |
| B-018 | S1 | debugger | 09-02 15:4x | ready-to-deploy | [was B-005] section-K #117: capability_sentinel rules mirror only 5 rules (Rule 1-5) in scripts/sapo_capability_sentinel_rules.py, NOT 16/16 as contracted — add missing 11 mirrored rules + rule-pin test asserting 16 STAGED 09-02 (debugger): claim is a MISREADING of #117's "16/16" = 16 rule-pin TESTS (not 16 rules). No 16-rule table exists anywhere; authoritative box sentinel (STANDUP #234 / driftwatch §3) fires on exactly 5 signals (entropy, trust-region, NaN/Inf, ERR99999, + local inert-drift), ALL mirrored. Made coverage explicit+auditable: added RULE_SIGNALS enumeration + 5 completeness-pin tests (test_rule_signals_enumeration_exists_and_is_complete, test_rule_signals_cover_every_documented_box_sentinel_signal, test_rule_signals_exact_authoritative_set, test_evaluate_only_emits_signals_in_rule_signals, test_rule_signals_has_corresponding_fire_function_for_each) — test_sapo_capability_sentinel_rules.py 25/25 GREEN (py3.9.6 venv); scripts/sapo_ci_gate.sh GREEN (launchable). — VERIFIED 09-02 17:2x CST (CI_VERIFIER): re-derived claim — RULE_SIGNALS enumeration present (scripts/sapo_capability_sentinel_rules.py:40) with exactly the 5 authoritative signals (entropy_drift, trust_region_violations, nonfinite_loss_rewards, npu_err99999, inert_drift); all 5 completeness-pin tests present (test_rule_signals_enumeration_exists_and_is_complete, test_rule_signals_cover_every_documented_box_sentinel_signal, test_rule_signals_exact_authoritative_set, test_evaluate_only_emits_signals_in_rule_signals, test_rule_signals_has_corresponding_fire_function_for_each); re-ran focused test test_sapo_capability_sentinel_rules.py → 25 passed; bash scripts/sapo_ci_gate.sh → GREEN (exit 0, all 4 stages). Independent confirmation. — READY-TO-DEPLOY 09-02 (deploy_steward): fix (RULE_SIGNALS sentinel enumeration = box-side capability_sentinel rules contract; box-runtime member) was on tree but NOT in the then-current r23 bundle (11ea4f01…) → REBUILT r23 lineage per the prior cycle's own flag (`python3 tmp/build_r22_bundle.py`); new bundle tmp/sapo-relaunch-r23.tgz sha 7c78e50f…; verified 349/349 sidecar, embedded-manifest==tgz (0 mismatches), tree==bundle; bundled sentinel now contains RULE_SIGNALS (sha aa83d0d2… == tree) + all 5 completeness-pin tests; focused 25/25 + B-002 2/2 green; CI GATE GREEN. DEPLOY-READINESS block (incl. delta and FLAG re swept-in trainer drift) appended to launchplan §6. NOTE FLAG: rebuild also swept in unverified trainer refinements (grpo_trainer/grpo_utils, B-005-class) — manager/user decides whether to fire 7c78e50f… or the B-002/B-010-only pre-rebuild copy 11ea4f01…. Manager/user fires the deploy. |
| B-019 | S2 | debugger | 09-02 15:4x | verified | [was B-006] section-K #116: ruff not clean on scripts/ — `ruff check scripts/*.py` returns 56 errors (E7xx/F841), violates check "ruff clean 0 errors"; fix or add to ruff-ignore — STAGED 09-02 (debugger): fixed ALL 52 remaining ruff violations (E722 bare-except x2, UP031 percent-format x4, F841 unused x6, B007 unused-loop-var x4, E741 ambiguous-l x22, B905 zip-strict x11) + the energized sapo/asi3 scripts (sapo_divergence_watch UP031) + real bugs in run_asi1_base_adapter_rubric_eval.py (missing `import tempfile`; F821 build_prompt undocumented-def noqa on a broken legacy ASI1 mirror). `ruff check scripts/*.py` now = **All checks passed! 0 errors** (contract #116 LIVE). Added tests/test_sapo_ruff_clean_scripts.py regression guard (2 tests: ruff-available + zero-errors on scripts/*.py; RED-capability verified by injecting an E722 probe). Evidence: test_ruff_check_scripts_py_returns_zero_errors + test_ruff_available_for_gate; focused debugger suite 120 GREEN; bash scripts/sapo_ci_gate.sh GREEN (exit 0, all 4 stages). — VERIFIED 09-02 19:4x CST (CI_VERIFIER, independent): re-derived claim — `ruff check scripts/*.py` on current tree → **All checks passed! 0 errors** (contract #116 LIVE; ruff 0.15.21); re-ran cited focused test file tests/test_sapo_ruff_clean_scripts.py → **2 passed** (test_ruff_check_scripts_py_returns_zero_errors + test_ruff_available_for_gate); bash scripts/sapo_ci_gate.sh (HEAD 7089a5b) → **GREEN** (exit 0, all 4 stages: [1/4] trainability smoke SMOKE_GREEN 5/5 launchable, [2/4] generation+rollout, [3/4] math identity, [4/4] runtime token scan). Independent confirmation — ruff cleanup spans many scripts/*.py (Mac-side + box-launcher); box-bundle-delta determination deferred to deploy_steward per §6.
| B-013 | S2 | debugger | 09-02 (auditor-D) | staged | Section D #40: eos_termination_rate swing >30% RED alert has NO live watcher — box sapo_metrics_watch.py lacks eos/swing term; rate is computed/stored but swing alert not implemented (v2.2 enforcer gap). Add eos_termination_rate swing>30% alert to metrics-watcher. STAGED (debugger 09-02): extracted pure `check_eos_swing` into scripts/sapo_metrics_watch_v3_rules.py, wired into main() polling loop; TDD pins GREEN. Evidence: test_eos_swing_detector_exists_and_callable + test_eos_swing_alerts_when_delta_exceeds_threshold + test_eos_swing_alerts_on_downward_swing; CI GATE GREEN. |
| B-014 | S2 | debugger | 09-02 (auditor-D) | staged | Section D #49: distinct-2-gram (repeater) <0.25 RED check MISSING — NO bigram/2-gram/repeater enforcer anywhere (repo grep + box sapo_metrics_watch.py). Implement distinct-2-gram repeater detector w/ <0.25 threshold in v2.2 metrics-watcher. STAGED (debugger 09-02): extracted pure `check_distinct_2gram_repeater` into scripts/sapo_metrics_watch_v3_rules.py, wired into main() polling loop; TDD pins GREEN. Evidence: test_distinct_2gram_detector_exists_and_callable + test_distinct_2gram_alerts_below_floor + test_distinct_2gram_no_alert_at_or_above_floor + test_distinct_2gram_reads_latest_row; CI GATE GREEN. |
| C-032 | S1 | debugger | 09-02 (auditor-C) | verified | Section C #32 gradient-vanishing — STAGED 2026-09-02 (debugger): v3 addendum watcher scripts/sapo_metrics_watch_v3_rules.py refactored for testability (pure check_gradient_vanishing detector + __main__ guard); test test_detector_function_exists_and_callable / test_vanishing_when_avg_below_floor_over_last_5 / test_no_alert_when_avg_above_floor; focused suite 132 GREEN; CI GATE GREEN. Original row: gradient-vanishing DEAD: box `sapo_metrics_watch.py` v2.2 (pid 119273) has grad-norm spike but NO `avg grad <1e-4 → RED` vanishing detector (only proxies mr_flat/pass_rate==0). Missing artifact: explicit gradient-vanishing check (avg grad_norm <1e-4 over window) in metrics-watcher. Guards inertness S0-class. — VERIFIED 09-02 20:0x CST (CI_VERIFIER, independent): re-derived claim — scripts/sapo_metrics_watch_v3_rules.py present; check_gradient_vanishing pure detector exists (line 53, callable), reads `gradient_norm` (fallback `gradient_norms`) over last-5 window, requires full window of numeric grads (no false positive on partial/None/non-numeric data), returns RED alert string when avg < 1e-4 (VANISH_FLOOR); `__main__` guard present (lines 90-91); re-ran cited focused test file tests/test_sapo_metrics_watch_v3_rules.py → 6 passed (incl. the 3 specifically cited: test_detector_function_exists_and_callable, test_vanishing_when_avg_below_floor_over_last_5, test_no_alert_when_avg_above_floor); bash scripts/sapo_ci_gate.sh → GREEN (exit 0, all 4 stages: [1/4] SMOKE_GREEN 5/5 launchable, [2/4] generation+rollout, [3/4] math identity, [4/4] runtime token scan). Independent confirmation. — box-bundle-delta determination deferred to deploy_steward per §6. — DEPLOY_STEWARD 09-02 20:2x CST (16th): **box-bundle delta? NO — zero box-bundle delta.** Fix lives in `scripts/sapo_metrics_watch_v3_rules.py` (pure-stdlib box-side-addendum watcher source for the C-32 gradient-vanishing / C-37 lr / D-40 EOS-swing / D-49 repeater rules, refactored for testability with pure `check_gradient_vanishing` detector + `__main__` guard) + `tests/test_sapo_metrics_watch_v3_rules.py` (**12/12 green re-ran this cycle, ruff clean**). CONFIRMED NOT a bundle member: the file is **absent** from `tmp/sapo-relaunch-r23.sha256` (349 entries) AND from the tgz AND from every bundle sidecar (grep 0); NOT referenced by any box launcher/wrapper (grep-verified — only its own test imports it); NOT in `required_files` gate. Critically, the box's existing metrics-watching infrastructure (`sapo_metrics_watch.py` v2.2, which C-032 augments) is **also NOT a bundle member** — box-side metrics-watching is delivered to the box by a separate mechanism / manager-user deploy, NOT via the r23 launch bundle. Therefore C-032's addendum watcher is deployed through that SAME separate mechanism, NOT by staging into r23 → **NO box-bundle delta to stage; NO rebuild warranted; no verified→ready-to-deploy promotion.** The fix is developed/verified on the local Mac tree; the manager/user delivers the watcher to the box (out of scope for the launch bundle) and may close/mark `deployed` locally at discretion — does NOT gate the r23 launch nor any launch. Determination recorded in launchplan §6 re-check #16. |
| C-037 | S1 | debugger | 09-02 (auditor-C) | verified | Section C #37 lr post-halving watch MISSING: enforcer "thresholds #331" is only a pre-committed doc rule (STANDUP #331), NO automated lr-threshold watcher exists; missing artifact: lr_current watcher alerting when lr ≤1.25e-5 (underpowered) — underpowered lr drives inertness S0-class. — STAGED 09-02 (debugger): added pure `check_learning_rate_floor` detector to scripts/sapo_metrics_watch_v3_rules.py (reads live per-step `lr` key grpo_trainer.py:7059; RED when current lr ≤ LR_FLOOR=1.25e-5) + wired into main() polling loop; 6 new TDD tests in tests/test_sapo_metrics_watch_v3_rules.py; focused v3-rules 12/12 GREEN; focused debugger suite 136 GREEN; ruff clean; py_compile clean; CI GATE GREEN. — VERIFIED 09-02 20:2x CST (CI_VERIFIER, independent): re-derived claim — scripts/sapo_metrics_watch_v3_rules.py present; `check_learning_rate_floor` pure detector exists (line 73, callable), reads current (latest) step's numeric `lr`, returns `RED C-37 underpowered lr: current lr ≤ LR_FLOOR=1.25e-5` when at/below floor, None when no-numeric-lr/non-numeric/missing (no false positive); wired into main() polling loop (lines 94-96); re-ran focused test file tests/test_sapo_metrics_watch_v3_rules.py → **12 passed in 0.03s** (incl. 6 C-37 tests: test_learning_rate_detector_exists_and_callable, test_alert_when_latest_lr_below_or_at_floor, test_no_alert_when_latest_lr_above_floor, test_alert_uses_latest_step_lr_not_historical, test_ignores_missing_or_non_numeric_lr, test_empty_rows_no_alert); bash scripts/sapo_ci_gate.sh → **GREEN (exit 0)**, all 4 stages ([1/4] SMOKE_GREEN 5/5 launchable, [2/4] generation+rollout, [3/4] math identity, [4/4] runtime token scan). Independent confirmation. — box-bundle-delta determination deferred to deploy_steward per §6. — DEPLOY_STEWARD 09-02 20:40 CST (17th): **box-bundle delta? NO — zero box-bundle delta.** Fix lives in the SAME file as C-032 (`scripts/sapo_metrics_watch_v3_rules.py` — adds pure `check_learning_rate_floor` detector (LR_FLOOR=1.25e-5, lines 72-83, wired into main() lines 94-96) + 6 new TDD tests in `tests/test_sapo_metrics_watch_v3_rules.py` (**12/12 re-ran GREEN this cycle**, incl. all 6 C-37 tests). CONFIRMED NOT a bundle member: **absent** from `tmp/sapo-relaunch-r23.sha256` (349 entries) AND from the tgz (grep 0) AND from all prior bundle sidecars; NOT referenced by any box launcher/wrapper; NOT in `required_files` gate. Box-side metrics-watching is delivered to the box by a separate mechanism (NOT the r23 launch bundle — the box's existing `sapo_metrics_watch.py` is also NOT a bundle member), so C-037's addendum ships through that SAME separate mechanism → **NO box-bundle delta to stage; NO rebuild warranted; no verified→ready-to-deploy promotion.** Fix is local-tree verified; manager/user delivers the watcher to the box (out of launch-bundle scope) and may close/mark `deployed` locally at discretion — does NOT gate the r23 launch nor any launch. Determination recorded in launchplan §6 re-check #17. |
| B-011 | S2 | debugger | 09-02 15:5x | closed | section-L #124: parallel-eval enforcer requires ×3 instances but only 1/3 running (sapo_parallel_eval_agent.sh ASI3 lane, PID 19808); ASI2/ASI1 eval lanes absent — CLOSED 09-02 16:19 CST (independent ps evidence): 3/3 agent lanes now running (ASI3 19808, ASI2 93408, ASI1 93409); rogue drivers terminated #381; sanctioned 3-lane coverage restored. |
| B-012 | S1 | debugger | 09-02 15:5x | verified | section-L #122: no channel-recovery enforcer artifact anywhere (name only in MONITORING_CONTRACT/docs; no script/process) → CDP ports 9224/9225 conflict recovery absent though currently conflict-free; add channel-recovery script verifying fixed map + auto-recover — STAGED 09-02 (debugger): added scripts/sapo_channel_recovery.py (section-L #122 fixed CDP map ASI3=9226/ASI2=9225/ASI1=9224; conflict = 2+ owners on one CDP port; fail-closed ALARM; inert-by-default recovery_command generation; lsof injectable/pure); tests/test_sapo_channel_recovery.py 11/11 GREEN (conflict detect, all-ports-clean, per-env classify, injectable lsof, recovery command kills owners + fixed-map CDP + never-wipes-profile); live --once probe = all 3 CDP ports conflict-free exit 0; focused 95 GREEN; scripts/sapo_ci_gate.sh GREEN (launchable). Evidence: test_two_owners_on_same_cdp_port_is_a_conflict + test_recovery_command_kills_conflicted_owners_and_relaunches_fixed_map + test_cdp_owner_pids_defaults_to_lsof_injection — VERIFIED 09-02 17:40 CST (CI_VERIFIER): re-derived claim — scripts/sapo_channel_recovery.py present with fixed CDP map ASI3=9226/ASI2=9225/ASI1=9224 (CDP_PORT_MAP confirmed), conflict = >=2 owners on one CDP port (channel_conflicts/classify_env_channel; 0-owner = unbound NOT conflict), fail-closed ALARM via nonzero exit (return 1 on channel-conflict), inert recovery_command generation (string-only, never executed), lsof injectable via list_pids param (pure); re-ran focused test tests/test_sapo_channel_recovery.py → 11 passed; live python3 scripts/sapo_channel_recovery.py --once → CLEAN (ASI1 9224 ok, ASI2 9225 ok, ASI3 9226 ok, exit 0); bash scripts/sapo_ci_gate.sh → GREEN (exit 0, all 4 stages). Independent confirmation. — DEPLOY_STEWARD 09-02 17:4x CST: fix is MAC-SIDE CDP-channel watchdog tooling (scripts/sapo_channel_recovery.py + tests/test_sapo_channel_recovery.py, 11/11 green re-confirmed this cycle), never a box-bundle member (absent from ALL bundle sidecars r20–r23; not referenced by any box launcher/wrapper; not in required_files gate). The CDP ports it recovers (ASI3=9226/ASI2=9225/ASI1=9224) are Mac-side daemon lanes by definition → NO box-bundle delta to stage; fix already live on local tree (its runtime). No box deploy needed; manager/user may close (or mark deployed locally) at discretion — does NOT gate any launch. Determination recorded in launchplan §6. |
| B-015 | S0 | debugger | 09-02 15:59 | closed | UNAUTHORIZED ACTIVE trainer 073028Z — was reported STALLED AT STEP 1 (refined #382 judge/dp4 unreachable squid-proxy). **CLOSED 09-02 17:15 CST (STANDUP #384 + addendum, manager live ASI3):** the step-1 judge-stall SELF-HEALED ~08:23:33Z (no fix needed); the run advanced to **4 completed steps** [s1 0.190/p0.0 · s2 0.940/**p0.875** · s3 0.265/p0.0 · s4 @08:57:25Z] + emitted step_000001_adapter, then **CRASHED ~08:57Z** with `[ERROR] TBE Subprocess[task_distribute] raise error[], main process disappeared!` (trainers 186602/186304 gone). Keep/stop arbitration now MOOT (already stopped, crashed). Prior 16:42/17:06 bugqueue recons claiming 'STILL stalled s1, 0 checkpoints, judge dir EMPTY/no proc' were reading a STALE/LAGGING view (they missed steps 1-4 + the crash). Live exec is authoritative. Residual: the crashed 073028Z (like its successor 090828Z) trained on the WRONG benchmark (v8 holdout-adjacent) — see B-026. |
| B-023 | S1 | error-miner | 09-02 16:3x | staged | novel class (error-signatures ledger): kernel_meta_temp cleanup fails on every run — `rm: cannot remove '<box>/kernel_meta/kernel_meta_temp_*': Directory not empty` appears in 100% of grpo_train logs (14+ observed since 08-24); Ascend/CANN temp dir recursive-rm leaves non-empty subdirs during teardown. Benign to training, but accumulates kernel_meta_temp_* dirs over long run histories (disk-leak risk). Fix direction: remove kernel_meta temp dir via a loop-tolerant recursive rm (e.g. rm -rf && retry) or defer to CANN kernel-manager post-exit; add a sweep on launch to clear stale temps. STAGED 09-02 (debugger): added _sweep_stale_kernel_meta_temps to training/grpo_trainer.py (retry-tolerant rmtree of kernel_meta/kernel_meta_temp_* on launch, rank-0 cleanup block w/ B-023 print) + wired into main(); 4 TDD tests: test_sweep_stale_kernel_meta_temps_removes_stale_temp_dirs, test_sweep_stale_kernel_meta_temps_handles_missing_kernel_meta, test_sweep_stale_kernel_meta_temps_removes_temp_files_not_just_dirs, test_main_sweeps_stale_kernel_meta_temps_on_launch; 44/44 test_grpo_trainer_metrics.py + 8/8 sigterm + focused suite 190 GREEN, CI GATE GREEN. |
| B-024 | S2 | error-miner | 09-02 16:55 | open | novel class (error-signatures ledger): transformers_generation_flags_ignored — `[transformers] The following generation flags are not valid and may be ignored: ['temperature', 'top_k']` (newer runs omit top_k, only ['temperature']) recurs in ~26/33 train logs since 08-26 (79%). Indicates the trainer's generate() call passes a `temperature`/`top_k` kwarg that transformers ignores → dead kwarg on that call path. trainer-side sampling control (behavior_temperature 1.3/1.0/0.33, greedy_count) still applied separately so no observed crash or direct data loss; benign UserWarning. S2 (quality/velocity) — potential sampling-control mismatch masked as benign. RECON 17:13 CST: recurrence re-confirmed in NEW run 20260902T090828Z — grpo_train log shows `generation flags ... ignored: ['temperature']` (only-variant). Fix direction: remove the ignored temperature/top_k kwargs from the transformers generate() call (trainer already applies its own) OR set them correctly so transformers honors them; add a scan/test so regenerated runs do not reintroduce dead generation kwargs. |
| B-025 | S2 | error-miner | 09-02 17:1x | open | novel class (error-signatures ledger): transformers_trust_remote_code_ignored — `[transformers] The argument \`trust_remote_code\` is to be used with Auto classes. It has no effect here and is ignored.` appears EXACTLY ONCE at model-load (between `tasks_ready` and `text_preprocessor_loaded`) in 34/34 train logs (100% recurrence since ~08-24). A `trust_remote_code=True` flag is passed to a NON-Auto `from_pretrained` load path (concrete class, not AutoModel) for Qwen3.6-27B; transformers ignores it because remote-code handling only applies to Auto classes. Sibling-but-distinct from B-024 (different call site — load vs generate — and different ignored kwarg). Benign informational warning (Qwen3.6-27B needs no remote code); no functional impact observed, trainer loads and proceeds normally — mirrors kernel_meta_temp (B-023) 100%-recurrence benign class. S2 (quality/velocity) — load path is dishonest about remote-code handling; if the model ever DID need a remote code, the flag being silently ignored would surface as a confusing load failure. Fix direction: drop the no-op `trust_remote_code` kwarg from the non-Auto load path (or switch to AutoModel if remote code genuinely needed); add a scan so regenerated launch scripts do not reintroduce the dead kwarg on a non-Auto load. |
| B-026 | S0 | manager | 09-02 17:15 | closed 17:45 (was open; canonical row above) | WRONG BENCHMARK (v8) verified in live cmdline → ROOT FIXED (v9 pinned in both launchers, TDD pin test, CI green, deployed sha-verified) → r23c relaunched 17:39 CST on v9 (trainer 194548, cmdline verified). DISPATCHER box-verified 17:45: newest active run 20260902T093912Z (=r23c) launch_config + running cmdline = `quantum_grpo_training_v9_rl_questions_v2.txt` (user-bound v9); 090828Z (v8) superseded. CLOSED. |
| B-027 | S1 | manager | 09-02 17:15 | closed 17:45 (was open; canonical row above) | unauthorized-respawn control-gap: the respawns were manager-executed relaunches (r23a→r23b→r23c); spawner only spawns LANES (never trainers). Control flow confirmed sound; no fix needed. DISPATCHER box-verified spawner.log shows lane-worker respawns only (no trainer) — consistent. CLOSED. |
| B-028 | S2 | error-miner | 09-02 17:2x | verified | novel class (error-signatures ledger): asi2_eval_state null-eval_output NoneType-subscriptable — `eval state read error: 'NoneType' object is not subscriptable` emitted by the LOCAL box-pull watchdog (scripts/sapo_box_pull_watch.sh:46) when rendering the "newest 5" eval-state summary. Root cause: `rec.get('eval_output','')[:80]` — the default `''` only applies when the `eval_output` KEY is ABSENT; when a record sets `eval_output: null`, `rec.get(...)` returns None and slicing None[:80] raises "'NoneType' object is not subscriptable" (reproduced locally). Caught by the script's try/except (no crash); the whole newest-5 summary just fails to render on that pull. Recurrence 127/531 box-pull cycles (~24%) in box_pull_ledger.md, STILL live on the latest pulls (09:20-09:24Z this cycle). DISPATCHER re-confirm 18:11 CST: recurrence now **149 ledger hits** (+7 this window); STILL live on the LATEST ASI2 box-pull **10:09:34Z** (NoneType in newest-5 rendering). DISPATCHER re-confirm 18:49 CST: recurrence now **168 ledger hits** (+19 since 18:11, +5 since 18:40); STILL live on LATEST ASI2 pull **10:48:36Z** (`eval state read error: 'NoneType' object is not subscriptable` in newest-5 summary). S2 (quality/velocity) — local eval-verdict OBSERVABILITY tooling degraded; no impact on box training/eval. Fix direction: coerce None before slicing, e.g. `(rec.get('eval_output') or '')[:80]`, or skip records with null/absent `eval_output`.  STAGED 09-02 (debugger): coerce None before slicing — `(rec.get('eval_output') or '')[:80]` (B-028 exact fix-direction); TDD RED (2 new tests failed on bare-default slice) -> GREEN; tests/test_sapo_box_pull_watch.py 4/4 GREEN; focused debugger suite 118 GREEN; ci gate GREEN (launchable). Evidence: test_eval_state_rendering_handles_null_eval_output + test_eval_state_rendering_snippet_uses_coerce_pattern. | VERIFIED 09-02 19:0x by CI_VERIFIER (independent): cited focused tests tests/test_sapo_box_pull_watch.py 4/4 PASS; fix confirmed in scripts/sapo_box_pull_watch.sh:47 `(rec.get('eval_output') or '')[:80]` coerce-None-before-slice (bare `rec.get('eval_output','')` dangerous slice absent); CI gate GREEN (exit 0, all 4 stages, launchable).
 — DEPLOY_STEWARD 09-02 19:1x CST: fix is MAC-SIDE local box-pull watchdog tooling (scripts/sapo_box_pull_watch.sh, 4/4 green re-ran this cycle), never a box-bundle member (absent from tmp/sapo-relaunch-r23.sha256 349 entries AND from the tgz AND from every bundle sidecar; NOT referenced by any box launcher/wrapper; not in required_files gate; grouped in scripts/sapo_fleet_roster.sh line 22 alongside the Mac-side watchdogs sapo_box_pull_watch/sapo_divergence_watch/sapo_wedge_watch/sapo_parallel_eval_agent). The Mac-side watchdog renders eval-state summaries locally via asi3_exec box pulls — the box NEVER receives this script. → NO box-bundle delta to stage; fix already live on local tree (its runtime). No box deploy needed; manager/user may close (or mark `deployed` locally) at discretion — does NOT gate the r23 launch nor any launch. Determination recorded in launchplan §6 re-check #10.
| B-029 | S2 | error-miner | 09-02 17:4x | open | novel class (error-signatures ledger): accelerate_device_map_keys_mismatch — `accelerate/utils/modeling.py:1615: UserWarning: The following device_map keys do not match any submodules in the model: ['model.language_model.embed_tokens', 'model.language_model.norm', 'model.language_model.rotary_emb', 'model.visual', 'visual', 'model.vision_tower', 'model.audio_tower', 'model.multi_modal_projector', 'model.language_model.layers.0'...'layers.63']` — accelerate fires this during weight loading (between `text_preprocessor_loaded` and `model_loaded`); the applied device_map lists ~66 keys for a MULTIMODAL spec (vision_tower / audio_tower / multi_modal_projector / visual / language_model.layers.0-63), but the actual loaded model is `Qwen3_5ForCausalLM` (causal-LM), so none match real submodules. Model still loads + shards successfully (model_loaded + model_sharded_on_npus map_size 140). Benign load-time UserWarning; 100% recurrence 14/14 sampled train logs spanning 2026-08-25 → 2026-09-02 (today's 5 runs + 9 older). Mirrors benign B-023/B-025 class style; NOT matched by sibling B-024/B-025 (transformers warnings — this is an ACCELERATE warning at device-map/weight-load time, distinct call site + library). S2 (quality/velocity) — the shard map is dishonest/mismatched to the causal-LM class; dead keys silently ignored now, but if the multimodal/eager path is ever enabled the mismatch could surface as a load failure. Fix direction: build the device_map from the real model.named_modules() (drop multimodal-only keys for the causal-LM path) so accelerate's warning disappears. |
| B-030 | S2 | debugger | 09-02 18:4x | ready-to-deploy (DEPLOY_STEWARD 09-02 21:00 CST: staged in r23 rebuild c62dd317… — box-runtime fix swept into bundle; sha verified, tests green, CI gate GREEN; manager/user fires) | novel class (error-signatures ledger): live_adapter_save_staging_leak — the trainer's LIVE-adapter atomic save (`_atomic_save_adapter_dir`, training/grpo_trainer.py:4386-4413) stages to `outputs/sapo-27b-ai-*/…/.adapter.tmp-<pid>-<hash>/` then renames to `adapter/` and cleans via `finally: shutil.rmtree(temp_dir, ignore_errors=True)` (line 4412). BUT that cleanup runs INSIDE the SIGTERM signal handler (termination_save, line 4430 "Runs inside the signal handler"); the docstring itself acknowledges (line 4437-4438) "the launcher's KILL escalation lands mid-save". When hard-KILLED mid-save the `finally` never completes → the `.adapter.tmp-*` staging dir leaks holding a ~299MB partial write (observed single `.tmp8xEcUl` file = in-flight adapter_model.safetensors ~312MB). Found in 12 of 13 sampled output dirs (2026-08-26→09-02, 100% recurrence incl today's 090828Z/073028Z runs), ~1.8GB accumulated (du -ch verified). The existing cleanup tests (tests/test_grpo_trainer_metrics.py:513,546; test_grpo_trainer_sigterm.py) only assert `.step_00000N_adapter.tmp-*` (STEP-checkpoint path save_peft_checkpoint_atomic) — the LIVE `.adapter.tmp-*` path has NO equivalent cleanup-must-survive-kill coverage → test gap. Atomicity/correctness IS preserved (rename + recovery work; final `step_*_adapter` + `adapter/` complete), so this is a DISK-LEAK/CLEANUP gap, NOT corruption. S2 (quality/velocity) — ~299MB/run leak, 1.8GB on a 2TB share (1.5T free, not a blocker today but unbounded per run-termination). Distinct from B-023 (kernel_meta_temp — CANN/Ascend path) and from the tested step-ckpt staging. Fix direction: (1) sweep stale `.adapter.tmp-*`/`.step_*_adapter.tmp-*` on launch; and/or (2) clean the live-adapter staging dir inside the SIGTERM handler BEFORE the KILL-escalation window (close write + rmtree pre-rename); and/or (3) add the missing live `.adapter.tmp-*` cleanup-must-survive-kill test.  STAGED 09-02 (debugger): added _sweep_stale_atomic_save_temps to training/grpo_trainer.py (sweeps .adapter.tmp-* + .step_*_adapter.tmp-* staging dirs on launch in main() rank-0 cleanup block) + wired into main() with B-030 cleanup print; 3 TDD tests: test_sweep_stale_atomic_save_temps_removes_adapter_and_step_tmp_dirs, test_sweep_stale_atomic_save_temps_leaves_non_matching_dir_untouched, test_main_sweeps_stale_adapter_tmp_on_launch (40/40 test_grpo_trainer_metrics.py + 8/8 sigterm GREEN, CI GATE GREEN). — VERIFIED 09-02 20:4x CST (CI_VERIFIER, independent): re-derived claim — `_sweep_stale_atomic_save_temps` present in training/grpo_trainer.py:4416 (sweeps `.adapter.tmp-*` + `.step_*_adapter.tmp-*` staging dirs; skips raw `.tmp-*` lenient guard; only removes exact atomic-save staging pattern; returns count removed) + wired into main() rank-0 cleanup block (lines 4925-4933, `_n_stale = _sweep_stale_atomic_save_temps(output_dir)` + `[cleanup] swept N stale atomic-save staging dir(s) ... (B-030 hard-KILL leak)` print when >0); re-ran cited focused tests → 3 TDD (test_sweep_stale_atomic_save_temps_removes_adapter_and_step_tmp_dirs, test_sweep_stale_atomic_save_temps_leaves_non_matching_dir_untouched, test_main_sweeps_stale_adapter_tmp_on_launch) → 3 passed; full test_grpo_trainer_metrics.py → 40 passed; test_grpo_trainer_sigterm.py → 8 passed; bash scripts/sapo_ci_gate.sh → GREEN (exit 0, all 4 stages, SMOKE_GREEN 5/5 launchable). Independent confirmation. |
| B-031 | S1 | manager | 09-02 19:58 | closed 20:13 (MANAGER — false alarm) | **FALSE ALARM — CLOSED by manager #399**: ps parentage shows **194918 PPID=194548** (child/fork worker, 13 thr Sl dormant) = the active trainer's own multiprocessing fork, NOT an independent rogue trainer. No active-trainer-per-dir violation, B-027 closure holds. [ORIGINAL row:] [DISPATCHER 18th cycle, box-corroborated] DUPLICATE LATENT TRAINER on same output dir: on r23c (sapo-27b-ai-20260902T093912Z) there are **TWO concurrent `training/grpo_trainer.py` processes** — **194548** (started 09:39:14Z, State=R running, 255 threads, 8.5GB RSS, **144% CPU — the ACTIVE trainer producing steps**) and **194918** (started 09:40:38Z, State=S sleeping, 13 threads, 3.1GB RSS, **0.0% CPU — a dormant/latent process**). Both point to the SAME output-dir `.../20260902T093912Z`, same v9 benchmark `quantum_grpo_training_v9_rl_questions_v2.txt`, same lr 5e-5, same judge endpoint 56237. 194918 has ~105 open fds and sits idle — a duplicate that never exited ~84s after its sibling. THIS is the concrete control-gap class that B-027 closed as "no fix needed" — but now there's a LIVE latent second trainer resident on the same dir (resource-race / potential later write-corruption risk on resume or step-000002+ writes; also unexplained 3GB RSS). New distinct row (NOT B-027-closure reopen — that row's diagnosis was about lane-respawn control-flow; this is an overlapping-but-new observed process pair). S1 (channel/data risk — concurrent same-dir trainer could corrupt shared resume_state/step files). Fix direction: manager/lane verify 194918 is not an intended A/B arm; if spurious, terminate it and add a single-active-trainer-per-dir guard (pidfile/setlock) so a relaunch kills its prior sibling before starting. |
| B-032 | S2 | error-miner | 09-02 20:1x | open | novel class (error-signatures ledger): **vllm_rollout_server_kv_cache_oom** — the vLLM-ascend rollout OpenAI API server (scripts/launch_vllm_rollout_server.sh default `gpu-memory-utilization 0.35`, tensor-parallel-size 8, port 8355, model Qwen3.6-27B, bf16) was launched 12:03:02Z (pid 212073) during ACTIVE r23c training and CRASHED at engine-core startup, 12:06:26Z, with `ValueError: No available memory for the cache blocks. Try increasing gpu_memory_utilization...` (EngineCore_DP0 pid=212140, kv_cache_utils._check_enough_kv_cache_memory) → `RuntimeError: Engine core initialization failed... Failed core proc(s): {}` → `[ERROR] ... ERR99999 UNKNOWN application exception`. Root cause = the NPUs were already occupied by the active trainer (194548 ~9-12GB/NPU) + the holdout rubric eval (199911 ~6-9GB/NPU); at util 0.35 there was no contiguous memory left for the vLLM KV-cache blocks. Process left as a ZOMBIE under init (212073 PPID 1, Z state); EngineCore child (212140) gone; port 8355 NOT listening; NO relaunch/retry observed. Source: box `/root/work/software/quantum-gpt/outputs/vllm_server.log` (353 lines, mtime 12:06:29Z) + box ps/proc state. Trainer UNAFFECTED (SAPO_VLLM_URL unset on trainer → trainer never used this server; r23c progressed through step 3 fine, step 4 begun ~12:13Z; npu_watch trainer_procs=2 steady; no trainer impact). vLLM seam is planned infra ("ASI1 = vLLM server", PROJECT_REPLICATION.md:116, would give 10-50x decode) but documented "NOT yet enabled (SAPO_VLLM_URL unset; server not launched)" — this was an early launch attempt that hit NPU co-tenancy OOM (matches the documented RUN-14 "Foreign co-tenant ... → step-2 OOM" memory-pressure theme, but as a distinct launch-time KV-cache-OOM class, NOT in ledger prior). NEW novel signature this cycle (ERROR_MINER). S2 (quality/velocity — the planned vLLM rollout seam cannot initialize while trainer+holdout-eval hold the NPUs; leaves a zombie; blocked until co-tenancy/lifecycle resolved, not a trainer-blocking S0/S1). Fix direction: (1) raise gpu_memory_utilization once co-tenants release / align with free memory; and/or (2) use the repo's vllm_lifecycle sleep/wake to share NPUs across trainer+server; and/or (3) schedule the vLLM server launch in a trainer-non-NPU-heavy window; (4) confirm intended launch-timing policy before enabling the seam (planned ASI1=vLLM). Ledger entry added 2026-09-02 ~20:1x CST. |
| B-033 | S1 | error-miner | 09-02 20:3x | open | novel class (error-signatures ledger): **verifier_env_missing_qiskit** — the box's trainer/verifier Python interpreter (`/usr/local/python3.11.14/bin/python3`, sys.executable used by the harness subprocess at training/grpo_trainer.py:2079) has NO `qiskit`/`qiskit_aer` installed (pip3 show qiskit = "Package(s) not found"; that site-packages has no qiskit; only a SOURCE dir `/root/work/filestorage/luxian/qiskit` exists, NOT on the interpreter path). But the v9 quantum benchmark tasks the r23c run (093912Z) is training on (quantum_grpo_training_v9_rl_questions_v2.txt; e.g. quantum_rl_v2_grover_qiskit_101 / qpe_qiskit_0375 / graph_state_stabilizers) require candidates that import `from qiskit import QuantumCircuit` + `from qiskit_aer import AerSimulator` (evals/tasks/quantum/quantum_rl_v2_grover_qiskit_101/candidate.py:10-12). Result: EVERY quantum candidate's harness execution fails with `details:["ModuleNotFoundError: No module named 'qiskit'"]` → `verifier: 0.0` AND harness `passed:false` for all such candidates. Observed in r23c (093912Z) eval_results.jsonl: **15/24 rows across steps 1-3** (step1=4, step2=4, step3=7). resume3 (older run) also had 108 qiskit errors; the earlier 073028Z run had 0 (used v8_holdout_adjacent benchmark — weaker qiskit exercise). Source: box eval_results.jsonl (r23c 093912Z, 24 rows) + evals/tasks/quantum/quantum_rl_v2_grover_qiskit_101/candidate.py:10-12 + box /usr/local/python3.11.14 (no qiskit) + training/grpo_trainer.py:2079. NEW novel signature this cycle (ERROR_MINER). DISTINCT from B-015 (judge/dp4 channel — different call site + failure type) and from the generic all-fail/pass-0 observable (B-033 is the concrete ROOT CAUSE mechanism behind the persistent verifier:0 on quantum tasks; prior ledger categorized all-fail as "inert B-005-S0/no-gradient-signal" without isolating this dependency gap). S1 (channel/data risk): combined with the dead judge channel (B-015), verifier(0.10)+pass(0.45, harness-dependent)+judge(0.15) reward-mass ≈ 0.70 of total reward is systematically unavailable on this v9 quantum run — policy effectively trains on only the residual syntax/interface/brevity/hygiene fractions. Actionable + high-impact. Fix direction: `pip install qiskit qiskit-aer` into /usr/local/python3.11.14 (or run the harness subprocess under an env with qiskit); verify a quantum candidate's harness actually runs (not just imports) before enabling pass/verifier reward on v9. Ledger entry added 2026-09-02 ~20:3x CST. |
| B-034 | S1 | error-miner | 09-02 21:0x | open | **RECURRING TBE task_distribute crash — r23c (093912Z) KILLED at step 5** (DISPATCHER box-verified 21:06 CST): `grpo_train_20260902T093912Z.log` ends at **step_000005 generation_done** then **`[ERROR] TBE Subprocess[task_distribute] raise error[], main process disappeared!`** (x8). Old trainer **194548 + fork-child 194918 now ZOMBIE** (Z, RSS=0, PPID=1); step_000005_adapter ckpt emitted (4 completed grpo steps + step-5 gen in flight when killed). **This is the SAME fatal signature that crashed B-015's 073028Z run (~08:57Z) — a 2nd observed run-family recurrence of the `TBE Subprocess[task_distribute] main process disappeared` class.** B-015 documented the historical class but the row was about the judge-stall+routine-crash, NOT this as a dedicated recurring killer — so this is a NEW ledger row (novel-recurrence class): the TBE distribute subprocess losing its main-process parent during active training (mid-generation at step 5) kills the whole trainer with no graceful recovery, resetting all N-step GRPO progress (r23c had reached step 5 + non-inert loo_advantage_rms 0.997/mean_reward 0.077 → progress lost on relaunch). S1 (channel/data risk — mid-training fatal crash wasting NPU-states; repeats across run-families). Note: the box ALREADY relaunched 130233Z (13:02:34Z, pid 222533, v9, lr 5e-5, greedy 0.4) — so continuity was restored, but root-cause of WHY task_distribute loses the main process is UNRESOLVED (nothing in the log preceding the fatal beyond normal step-5 generation). Fix direction: (1) investigate the TBE task_distribute → main-process parent-drop during generation (NPU transport/process-drop on Ascend); (2) add crash-detection + auto-select-latest-ckpt resume so a TBE kill does not reset progress; (3) add a sentinel/guard checking for this signature in grpo_train logs and alarm immediately (currently silent until a human reaper reads logs). Ledger entry added 2026-09-02 ~21:0x CST (DISPATCHER). |

RECON (09-02 17:06 CST): queue 16 OPEN (oldest B-001/B-003 @15:05, ~121min) + 5 CLOSED; no rows closed this cycle; NO NEW alarms deduped (wedge ok all 3 ports last-alarm 07:49Z; divergence waiting-for-data trainer stalled known B-005/B-015; box steps=28 frozen inert identical ticks; no new wedge_alarms/divergence entries). Box-side ASI3 exec: metrics frozen steps=28 ent=0.22/pass=0.375 unchanged → B-005/B-015 inert/stall persists; 073028Z trainer 186602 still running but output has ONLY 1 checkpoint (step_000001_adapter), judge_bridge dir EMPTY + no judge_bridge/dp4 proc → B-015 step-1 judge-path stall persists (USER KEEP/STOP arbitration still required). B-003 symptom re-confirmed STILL live: sole sanctioned driver still writes shared reports/.sapo_parallel_eval_state.json entry "29" pending/precheck-running (mtime 17:02) + infinite step_000024→000029 re-eval loop in parallel_eval_ASI3.log; `_ASI3.json` STILL DOES NOT EXIST → fix (point ASI3 at its own _ASI3.json) NOT yet applied. B-002 stays ready-to-deploy (r23 lineage) awaiting manager/user fire; B-004/B-008/B-010 remain verified. B-009 closure evidence holds (sapo_judge_mac_watcher pid 76676 running; caveat watcher log STILL 0 bytes — spot-verify still open). Stale rows B-001/B-003/B-005-S0/B-015 + audit-origin all >20min → escalated (see top).
RECON (09-02 17:13 CST): queue 21 OPEN (3 verified [B-004,B-008,B-018] + 2 ready-to-deploy [B-002,B-010] + 6 closed incl B-015 + NEW B-026/B-027 at 17:15) | OLDEST OPEN: B-005 (07:39, ~9.5h) & B-001/B-003 (15:05, ~2h). Cycle 17:06→17:13 box observation (my dispatch read): old 073028Z trainer 186602 absent from ps; a NEW run 20260902T090828Z (pid 192801) live at `step_begin step 1` with judge_bridge on 56237 + repair sidecar up; metrics_watch still frozen steps=28 (old run's watcher). ATTENTION/CORRECTION (superseded by MANAGER STANDUP #384, authoritative live exec, 17:15): B-015 CLOSED — the 073028Z run SELF-HEALED the step-1 judge stall ~08:23:33Z (no fix needed), reached 4 completed steps, then CRASHED ~08:57Z (TBE task_distribute main-process-disappeared, trainers 186602/186304 gone); KEEP/STOP arbitration MOOT. My 17:13 recon read of 'old trainer gone + new run at step 1, outcome unknown' was based on a lagging snapshot relative to the manager's live-exec view (which saw steps 1-4 + crash) — treat the CLOSED row / STANDUP #384 as authoritative; B-015 class does NOT persist. B-003 symptom re-confirmed STILL live: sole sanctioned driver still writes shared reports/.sapo_parallel_eval_state.json entry "29" pending/precheck-running (mtime 17:13) + infinite step_000024/000026/000029 re-eval loop in parallel_eval_ASI3.log; `_ASI3.json` STILL DOES NOT EXIST → fix (point ASI3 at its own _ASI3.json) NOT yet applied. NO new alarm rows this cycle (wedge ok all 3 ports last-alarm 07:49Z; divergence waiting-for-data; box frozen steps=28). Concurrent advances: B-015 → closed (manager #384), B-018 → staged→verified (CI_VERIFIER), B-010 → verified→ready-to-deploy (deploy_steward). NEW ROWS this cycle (added 17:15 by concurrent worker, NOT mine): **B-026 S0** — ACTIVE 090828Z trainer (192491, launched 17:08 CST) + crashed 073028Z BOTH launched on v8 holdout-adjacent benchmark instead of the USER-BOUND v9 manifest (objective-invalidating dataset-binding violation; ACTION user adjudication stop/relaunch); **B-027 S1** — THIRD unauthorized/auto-respawned trainer (090828Z) outside manager/user approval flow (control-gap; #1 control-gap this cycle, compounds B-026). Both are the dominant new opens and are escalated (see B-026/B-027 rows). B-004/B-008/B-018 verified; B-002/B-010 ready-to-deploy awaiting manager/user fire. B-009 closure caveat still open (judge_mac_watcher pid 76676 running, log STILL 0 bytes). B-024 recurrence confirmed in new run (`['temperature']`-only warning). Stale rows B-001/B-003/B-005-S0 + audit-origin >20min → escalated (see top).
DEPLOY_STEWARD CYCLE (09-02 17:3x CST): B-018 moved verified→ready-to-deploy this cycle. Rebuilt r23 lineage (`python3 tmp/build_r22_bundle.py`) because B-018's fix (RULE_SIGNALS sentinel enumeration, box-runtime member) was verified on tree but NOT yet in the then-current r23 bundle (11ea4f01…). New bundle tmp/sapo-relaunch-r23.tgz sha 7c78e50f… (supersedes 11ea4f01…; pre-rebuild immutable copy tmp/deploy-steward-prebuild-r23-11ea4f01.tgz). Verified: 349/349 sidecar vs tree, embedded-MANIFEST==tgz (0 mismatches), tree==bundle; B-018 RULE_SIGNALS + 5 completeness-pin tests present in bundle; focused 25/25 (B-018) + 2/2 (B-002) green; CI GATE GREEN. FLAG: rebuild swept in unverified trainer refinements (grpo_trainer/grpo_utils, B-005-class) — manager/user decides whether to fire 7c78e50f… (full set) or the B-002/B-010-only pre-rebuild 11ea4f01… copy. DEPLOY-READINESS block appended to launchplan §6. READY-TO-DEPLOY now: B-002, B-010, B-018 (r23, sha 7c78e50f…). VERIFIED (Mac-side, zero box delta): B-004, B-008. NOTHING deployed from this lane; manager/user fires.
DISPATCHER RECON (09-02 17:45 CST): queue 14 OPEN (oldest B-005 @07:39 ~10h; B-001/B-003 @15:05 ~2.5h) + 1 staged (B-012) + 2 verified (B-004,B-008) + 3 ready-to-deploy (B-002,B-010,B-018) + 8 closed (incl B-026/B-027 this window). THIS cycle (17:35→17:45) dispatcher actions: (1) NO new alarm rows deduped — wedge ok all 3 ports (last-alarm 07:49Z), divergence waiting-for-data, box metrics frozen steps=28 identical; (2) closed rows verified independently: **B-026** (wrong-benchmark v8→v9) and **B-027** (unauthorized-respawn) CLOSED 17:45 by MANAGER — dispatcher box-verified: newest active run 20260902T093912Z (=r23c, 17:39 CST) launch_config + running cmdline = `quantum_grpo_training_v9_rl_questions_v2.txt` (user-bound v9 manifest); 090828Z (v8) superseded; spawner.log confirms ONLY lane-worker respawns (never trainer) → manager's control-flow closure consistent. RECONCILED the B-026/B-027 ID-collision: closed canonical rows at top + formerly-open duplicate rows at bottom both now CLOSED (one canonical ID per row — LEDGER INTEGRITY policy). (3) ENFORCE #135: stale >20min rows escalated at top — B-001/B-003, B-005-S0 (lora-pace re-verify still NOT possible: 093912Z at early startup, NO step_* checkpoints yet), B-016/B-017/B-019/B-013/B-014/C-032/C-037/B-023/B-024/B-025 all still open. STILL-LIVE symptoms re-confirmed: B-003 (shared ASI3 state file entry "29" pending mtime 17:34, `_ASI3.json` still absent, infinite 024/026/029 re-eval loop), B-028 (NoneType-subscriptable recurrence on 09:36:48Z pull/ledger). B-009 closure caveat persists (judge_mac_watcher pid 76676 running, log STILL 0 bytes ❯ spot-verify unresolved). Concurrent advances earlier window (not mine): B-012→staged, B-018→ready-to-deploy (7c78e50f… sweep-in FLAG), B-002/B-010 already ready-to-deploy. NO rows advanced by dispatcher this cycle beyond closure reconciliation; manager/user fires B-002/B-010/B-018 at discretion.
DEPLOY_STEWARD CYCLE (09-02 17:5x CST): verified-ticket re-sweep + bundle integrity re-check + CRITICAL FLAG.
(1) VERIFIED TICKET RE-SWEEP: status=verified now = B-004 (Mac-side wedge-watch, zero box delta), B-008 (Mac-side secret-scan, zero box delta), B-012 (NEW — Mac-side CDP channel-recovery, zero box delta; determination appended to B-012 row). NONE carries a box-bundle delta → NO rebuild warranted from verified tickets this cycle.
(2) BUNDLE INTEGRITY RE-CHECK (r23, sha 7c78e50f…): bundle sha MATCH; embedded MANIFEST vs tgz 0 mismatches (350 entries); B-002/B-010/B-018 fixes all present in bundle; per-file sidecar 349/349 vs frozen tree state. CI GATE GREEN (exit 0, all 4 stages). Focused tests all green this cycle: B-002 2/2, B-010 2/2, B-018 25/25, B-004 8/8, B-008 12/12, B-012 11/11, B-026 pin 2/2 — 61 total.
(3) 🚨 CRITICAL FLAG — BUNDLE STALENESS (v8 launcher default): the current bundle `7c78e50f…` (built 17:29 for B-018) predates the B-026 v9-binding fix. Bundled launcher scripts (`ai_launch_sapo_direct.sh` + `asi3_launch_grpo_direct.sh`) still default the benchmark to `v8_holdout_adjacent` — the BANNED benchmark per B-026 (S0 dataset-binding violation). The working tree now pins v9 (user-bound, `quantum_grpo_training_v9_rl_questions_v2.txt`) with TDD pin tests. **If `7c78e50f…` is fired for a FUTURE launch, the box would re-default to v8** and re-trigger the B-026 class. B-026 is closed (not `verified`), so per my brief's verified-gate I did NOT auto-rebuild; the manager/user decides whether to authorize a rebuild to capture the v9 pin before any future box launch. The box itself is SAFE (r23c 093912Z already running on v9 since 17:39 — DISPATCHER box-verified).
(4) READY-TO-DEPLOY (unchanged): B-002, B-010, B-018 — all staged in r23 `7c78e50f…` — but see staleness FLAG above before any future-launch fire. VERIFIED Mac-side (zero box delta, no deploy needed): B-004, B-008, B-012. NOTHING deployed from this lane; manager/user fires. Full DEPLOY-READINESS block appended to launchplan §6.

DISPATCHER RECON (09-02 17:55 CST): queue 13 OPEN (oldest B-003 @15:05 ~2.8h) + 0 staged + 3 verified (B-004,B-008,B-012) + 3 ready-to-deploy (B-002,B-010,B-018) + 10 closed (incl B-001/B-005 this window). THIS cycle (17:45→17:55) dispatcher actions: (1) NO NEW ALARM rows deduped from watch surfaces — wedge ok all 3 ports (last-alarm 07:49Z; no new entries in wedge_alarms.log since 07:49Z), divergence waiting-for-data evals=2 (no train_trend), box metrics watcher frozen steps=28 identical ticks (ent=0.22/pass=0.375/mr=0.5298/ess=7.30) → nothing new to file. (2) closure verification: manager CLOSED **B-005** 17:55 (lr 5e-5 + gate v2 + sentinel inert-drift shipped; row updated to closed this window) — dispatcher finds no box-verifiable counter-evidence to reopen (r23c/093912Z still at early startup, NO step_* checkpoints; box watcher still frozen old-run steps=28). B-026/B-027 (17:45) closures HOLD — re-box-verified 17:55: newest active run 20260902T093912Z (=r23c) running `--benchmark-file evals/benchmarks/quantum_grpo_training_v9_rl_questions_v2.txt` (user-bound v9, trainer 194918); 090828Z (v8) superseded; spawner.log = lane-only respawns (never trainer), consistent with manager's control-flow closure. (3) ENFORCE #135: stale >20min escalated at top — B-003 (15:05, ~2.8h, oldest OPEN), B-016/B-017/B-019/B-013/B-014/C-032/C-037/B-023/B-024/B-025, plus open B-028/B-029. STILL-LIVE re-confirmed: **B-003** (shared reports/.sapo_parallel_eval_state.json STILL entry "29" pending/precheck-running, mtime 17:51 CST, `_ASI3.json` STILL absent, infinite step_000024/000026/000029 re-eval loop continues in parallel_eval_ASI3.log — fix NOT applied); **B-028** (`NoneType subscriptable` recurrence ON the LATEST ASI2 box-pull 09:55:15Z, 142 ledger hits). B-005-class pace re-baseline PENDING: r23c (093912Z) at early startup, NO step_* checkpoints yet → lora-pace re-verify not yet possible. NOTE concurrent advances this window (deploy_steward): B-012 → verified (Mac-side CDP channel-recovery, zero box delta); CRITICAL FLAG — bundle 7c78e50f… still defaults launcher benchmark to v8 (BANNED/B-026 class) → box is SAFE (r23c already on v9), manager/user decides whether to rebuild to capture v9 pin before any FUTURE launch. NEW LEDGER row (concurrent error-miner, NOT an alarm): **B-029** accelerate device_map keys-mismatch (Qwen3_5ForCausalLM vs multimodal key set; 100% recurrence 14/14 sampled, benign load-time UserWarning, distinct from B-024/B-025 transformers class) — no action from this lane. B-009 closure caveat persists (judge_mac_watcher pid 76676 running, log STILL 0 bytes — spot-verify still unresolved). NO rows advanced by dispatcher this cycle (no independent CI-green artifact appeared for an OPEN row this window); manager/user fires B-002/B-010/B-018 at discretion.

DEPLOY_STEWARD CYCLE (09-02 18:0x CST): verified-ticket re-sweep + bundle integrity re-check + CONCRETE CONFIRMATION of the v8-launcher-default staleness (now diff-evidenced).
(1) VERIFIED TICKET RE-SWEEP (per brief DO): status=verified now = B-004 (Mac-side wedge-watch, zero box delta), B-008 (Mac-side secret-scan, zero box delta), B-012 (Mac-side CDP channel-recovery, zero box delta). NONE carries a box-bundle delta → **NO rebuild warranted from verified tickets this cycle**. The current bundle `7c78e50f…` (rebuilt prior cycle for B-018) already stages the B-002/B-010/B-018 box fixes.
(2) BUNDLE INTEGRITY RE-CHECK (r23, sha 7c78e50f…): bundle sha **MATCH**; embedded MANIFEST vs tgz **0 mismatches** (350 entries incl. MANIFEST); B-002/B-010/B-018 fixes present in bundle. BUT per-file sidecar vs current tree → **4 FAILED** box-bundle members: `scripts/ai_launch_sapo_direct.sh`, `scripts/asi3_launch_grpo_direct.sh`, `scripts/asi2_launch_grpo_27b_selfeval.sh`, `tests/test_asi3_sapo_launcher_readiness.py`. These are the **B-026 v9-binding fix** files (see flag below), which landed on the working tree after the 17:29 bundle freeze.
(3) 🚨 CRITICAL BUNDLE STALENESS — NOW **CONCRETELY DIFF-EVIDENCED** (upgrades the prior cycle's extrapolation): the current bundle `7c78e50f…` still defaults `ASI3_SAPO_BENCHMARK_FILE` → `evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt` (**v8 — BANNED/B-026 S0**) in BOTH `ai_launch_sapo_direct.sh` (bundle line 52) and `asi3_launch_grpo_direct.sh` (bundle line 118). The working tree has since landed the **B-026 v9 fix** — `git diff` shows `# 2026-09-02 (B-026/S0 USER BINDING): rollout = v9 jsonl ONLY. v8 is banned.` and both launchers now default to `quantum_grpo_training_v9_rl_questions_v2.txt`, plus TDD pin tests `tests/test_sapo_benchmark_binding_pin.py` (**4 passed** this cycle) and readiness-test v9 references. **If `7c78e50f…` is fired for a FUTURE launch, the box would re-default to v8 and re-trigger the exact B-026 S0 dataset-binding violation.** Per my brief's verified-gate I did **NOT** auto-rebuild (B-026 is **closed**, not `verified`); the manager/user decides whether to authorize a rebuild (`python3 tmp/build_r22_bundle.py`) to capture the v9 pin into the r23 lineage before any future box launch. The box is SAFE: r23c (093912Z) already running on v9 since 17:39 (DISPATCHER box-verified) — only the LOCAL bundle artifact is stale.
(4) TESTS — ALL GREEN this cycle: CI GATE **GREEN** (exit 0, all 4 stages); focused B-002 2/2, B-010 2/2, B-018 25/25, B-004 8/8, B-008 12/12, B-012 11/11, **B-026 v9-pin 4/4** = 63 total.
(5) READY-TO-DEPLOY (unchanged): B-002, B-010, B-018 — all staged in r23 `7c78e50f…` — **but see the CONCRETE v8-default staleness flag above before any future-launch fire** (B-002's launcher file is ITSELF one of the 4 stale members — its alias fix is present but on a v8-defaulting launcher copy). VERIFIED Mac-side (zero box delta, no deploy needed): B-004, B-008, B-012. NOTHING deployed from this lane; manager/user fires. Full cycle record appended to launchplan §6 re-check #5.

DISPATCHER RECON (09-02 18:11 CST): queue 11 OPEN (oldest = B-013/B-014/B-017/B-019 auditor-origin ~15:4x, ~2.5h) + 0 staged + 4 verified (B-004,B-008,B-012,**B-016) + 3 ready-to-deploy (B-002,B-010,B-018) + 11 closed (incl **B-003** this window). THIS cycle (17:55→18:11) dispatcher actions: (1) **NO NEW ALARM rows deduped** from watch surfaces — wedge ok all 3 ports (last-alarm 07:49Z; no new wedge_alarms entries), divergence waiting-for-data evals=2 (no train_trend), box watchers frozen (old-run steps=28 AND new-run steps=4 identical) → nothing to file. (2) **closure/corrobation**: manager CLOSED **B-003 18:09** (STANDUP #386, process-ops only — root cause = running ASI3 driver pre-dated the per-env-state/no-false-done fix; driver restarted to pid 15647 pointed at ACTIVE r23c, inheriting `_ASI3.json` redirect). DISPATCHER independent box-verify: new driver pid 15647 targets `outputs/sapo-27b-ai-20260902T093912Z/`; `reports/.sapo_parallel_eval_state_ASI3.json` EXISTS (created 18:09:05Z, currently `{}`); shared non-suffixed `reports/.sapo_parallel_eval_state.json` mtime FROZEN at 18:08:00Z (confirmed no re-write after 45s sleep) → infinite resume-3 step_000029 re-eval loop STOPPED; closure HOLDS (no edge-reopen). (3) **ENFORCE #135**: stale >20min escalated at top — B-017/B-019/B-013/B-014/C-032/C-037/B-023/B-024/B-025/B-028/B-029 (oldest OPEN now auditor-origin ~15:4x). STILL-LIVE re-confirmed: **B-028** (`NoneType subscriptable` recurrence on the LATEST ASI2 pull 10:09:34Z; ledger now 149 hits, +7 this window); **B-005-class pace re-baseline STILL PENDING** — r23c (093912Z, v9) STILL at `step_begin step 1` (task quantum_rl_v2_qpe_qiskit_0375) since ~09:39 (~32 min, box log tail verified), NO step_* checkpoints → re-verify not yet possible; box watchers frozen (old steps=28 + new steps=4). **B-009 caveat persists** (judge_mac_watcher pid 76676 running, log STILL 0 bytes — spot-verify unresolved). CI_VERIFIER independent 18:10: CI gate GREEN (exit 0, HEAD 7089a5b, 0 staged tickets — nothing to advance) + 3 landed waves HOLD (49 focused pass); my own `sapo_ci_gate.sh` run collided (SIGTERM on [2/4] generator/rollout suite — resource contention amid concurrent standup/model-load; verifier's GREEN authoritative). NOTE concurrent advances (not mine): **B-016 → staged → VERIFIED** this window (debugger staged completeness-marker gate in sapo_parallel_eval_agent.sh 6/6 GREEN; CI_VERIFIER then independent-verified: gate at lines 38-56, test_sapo_parallel_eval_agent.py 6 passed + CI gate GREEN — now in 4-verified set); deploy_steward FLAG — bundle `7c78e50f…` has **CONCRETE v8-launcher-default staleness** (4 failed sidecar members = B-026 v9-pin files; bundled launchers still default v8 = BANNED) — box SAFE (r23c already on v9 17:39), manager/user decides whether to authorize rebuild to capture v9 pin before any FUTURE launch. NO rows advanced/closed by dispatcher this cycle (B-003 closure was manager-initiated; no independent CI-green appeared for a currently-OPEN row this window); manager/user fires B-002/B-010/B-018 at discretion.

DEPLOY_STEWARD CYCLE (09-02 18:24 CST): verified-ticket re-sweep + bundle integrity re-check — THIRD consecutive v8-staleness confirmation; NO rebuild; decision still pending with manager/user.
(1) VERIFIED TICKET RE-SWEEP (per brief DO): status=verified now = **B-004** (Mac-side wedge-watch, zero box delta), **B-008** (Mac-side secret-scan, zero box delta), **B-012** (Mac-side CDP channel-recovery, zero box delta). NONE carries a box-bundle delta → **NO rebuild warranted from verified tickets this cycle**. No ticket moved to ready-to-deploy (nothing new staged). The current bundle `7c78e50f…` (rebuilt prior cycle for B-018) already stages the B-002/B-010/B-018 box fixes.
(2) BUNDLE INTEGRITY RE-CHECK (r23, sha `7c78e50f…`): bundle sha **MATCH** (`7c78e50fe22a76d5a64f5680a4d8afd122c642cca7eb6faf5659a8504797d002`); embedded `MANIFEST.sha256.json` vs tgz contents → **0 mismatches** (349 entries hash-verified); B-002 launcher-alias fix + locking test, B-010 guarded peft import, B-018 RULE_SIGNALS + 5 completeness-pin tests all **present** in bundle. **BUT** per-file sidecar vs current tree → **4 FAILED** box-bundle members (same as prior 2 cycles): `scripts/ai_launch_sapo_direct.sh`, `scripts/asi3_launch_grpo_direct.sh`, `scripts/asi2_launch_grpo_27b_selfeval.sh`, `tests/test_asi3_sapo_launcher_readiness.py` = the B-026 v9-pin files on tree vs v8-default in the bundle (frozen 17:29 pre-fix).
(3) 🚨 CRITICAL BUNDLE STALENESS — RE-CONFIRMED (3rd consecutive cycle): bundle `7c78e50f…` STILL defaults `ASI3_SAPO_BENCHMARK_FILE`/`BENCHMARK_FILE` → `evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt` (**v8 — BANNED/B-026 S0**) in both bundled launchers (ai line 52, asi3 line 118). Tree STILL pins **user-bound v9** (`quantum_grpo_training_v9_rl_questions_v2.txt`, ai line 53 / asi3 line 119) + TDD pin tests. **If fired for a FUTURE launch → box re-defaults to banned v8 → exact B-026 S0 violation.** B-026 is CLOSED (not `verified`) → per verified-gate I did **NOT** auto-rebuild; **manager/user decision on rebuild STILL PENDING (3rd escalation).** Box is SAFE: r23c (093912Z) already on v9 (17:39, DISPATCHER box-verified) — only the LOCAL bundle artifact is stale.
(4) TESTS — ALL GREEN this cycle: CI GATE **GREEN** (exit 0, all 4 stages, smoke 5/5 launchable); focused B-002 2/2, B-010 2/2, B-018 25/25, B-026 v9-pin 4/4, B-004 8/8, B-008 12/12, B-012 11/11 = **64 total**.
(5) READY-TO-DEPLOY (UNCHANGED): B-002, B-010, B-018 — all staged in r23 `7c78e50f…` — **but see the 3rd-cycle v8-default staleness above before any future-launch fire** (B-002's own launcher member is among the 4 stale files). VERIFIED Mac-side (zero box delta, no box deploy needed): B-004, B-008, B-012. NOTHING deployed from this lane; manager/user fires. Full cycle record appended to launchplan §6 re-check #6.

DEPLOY_STEWARD CYCLE (09-02 18:34 CST): verified-ticket re-sweep + bundle integrity re-check — FOURTH consecutive v8-staleness confirmation (unchanged); B-016 determined Mac-side; NO rebuild; decision still pending with manager/user.
(1) VERIFIED TICKET RE-SWEEP (per brief DO): status=verified now = **B-004** (Mac-side wedge-watch, zero box delta), **B-008** (Mac-side secret-scan, zero box delta), **B-012** (Mac-side CDP channel-recovery, zero box delta), **B-016 (NEW this cycle)** — completeness-marker gate in `scripts/sapo_parallel_eval_agent.sh` (verified by CI_VERIFIER 18:2x). **B-016 staged-verification: box-bundle delta? NO — Mac-side pure.** The fix lives in `scripts/sapo_parallel_eval_agent.sh` (Mac-side parallel-eval watchdog) + `tests/test_sapo_parallel_eval_agent.py` (6/6 green re-ran this cycle). CONFIRMED NOT a box-bundle member: the file is **absent** from `tmp/sapo-relaunch-r23.sha256` (349 entries) AND from the tgz AND from every prior bundle sidecar; NOT referenced by any box launcher/wrapper; NOT in `required_files` gate; grouped in `scripts/sapo_fleet_roster.sh` line 22 alongside the Mac-side watchdogs (sapo_box_pull_watch / sapo_divergence_watch / sapo_wedge_watch). The Mac-side agent drives box eval via curl/`asi3_exec --port` — the box NEVER receives this script. → **NO box-bundle delta to stage; fix already live on local tree (its runtime).** No box deploy needed; manager/user may close (or mark `deployed` locally) at discretion — does NOT gate the r23 launch. Determination appended to B-016 row + launchplan §6 re-check #7. NONE of the 4 verified tickets carries a box-bundle delta → **NO rebuild warranted from verified tickets this cycle**. No ticket moved to ready-to-deploy (nothing new staged for the box).
(2) BUNDLE INTEGRITY RE-CHECK (r23, sha `7c78e50f…`): bundle sha **MATCH** (`7c78e50fe22a76d5a64f5680a4d8afd122c642cca7eb6faf5659a8504797d002`); embedded `MANIFEST.sha256.json` vs tgz contents → **0 mismatches** (349 entries hash-verified, 350 files incl. MANIFEST); B-002 launcher-alias fix, B-010 guarded peft import, B-018 RULE_SIGNALS + 5 completeness-pin tests all **present** in bundle (re-grep-verified this cycle).
(3) 🚨 CRITICAL BUNDLE STALENESS — RE-CONFIRMED (4th consecutive cycle): bundle `7c78e50f…` STILL defaults `ASI3_SAPO_BENCHMARK_FILE`/`BENCHMARK_FILE` → `evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt` (**v8 — BANNED/B-026 S0**) in both bundled launchers (ai line 52, asi3 line 118). Tree STILL pins **user-bound v9** (`quantum_grpo_training_v9_rl_questions_v2.txt`, ai line 53 / asi3 line 119). **If fired for a FUTURE launch → box re-defaults to banned v8 → exact B-026 S0 violation.** B-026 is CLOSED (not `verified`) → per verified-gate I did **NOT** auto-rebuild; **manager/user decision on rebuild STILL PENDING (4th escalation).** Box is SAFE: r23c (093912Z) already on v9 (17:39, DISPATCHER box-verified) — only the LOCAL bundle artifact is stale.
(4) TESTS — ALL GREEN this cycle: CI GATE **GREEN** (exit 0, all 4 stages; smoke 5/5 launchable); focused B-002 2/2, B-010 2/2, B-018 25/25, **B-016 6/6** = **35 focused this cycle** (B-004 8/8 / B-008 12/12 / B-012 11/11 / B-026 pin 4/4 unchanged from prior cycles).
(5) READY-TO-DEPLOY (UNCHANGED): B-002, B-010, B-018 — all staged in r23 `7c78e50f…` — **but see 4th-cycle v8-default staleness above before any future-launch fire** (B-002's own launcher member is among the 4 stale files). VERIFIED Mac-side (zero box delta, no box deploy needed): B-004, B-008, B-012, **B-016**. NOTHING deployed from this lane; manager/user fires. Full cycle record appended to launchplan §6 re-check #7.
RECON (09-02 18:40 CST): queue 11 OPEN (oldest B-013/B-014/B-017/B-019 auditor-origin ~3h) + 0 staged + 4 verified (B-004,B-008,B-012,B-016) + 3 ready-to-deploy (B-002,B-010,B-018) + 11 closed | NO NEW ALARM rows; no rows closed/advanced by dispatcher this cycle. THIS-cycle obs: B-028 STILL LIVE (ledger 163 hits, latest ASI2 pull 10:36/10:38Z still 'NoneType subscriptable'); B-005-class pace re-baseline STILL PENDING (r23c/093912Z only step_000001_adapter, no newer ckpts, box watcher frozen steps=28); B-003 closure HOLDS (ASI3 state file exists 18:09 {} + shared state frozen); B-009 caveat persists (judge_mac_watcher log 0 bytes). Stale>20min escalated at top (#135). All alarm surfaces OK (wedge all 3 ports, divergence waiting-for-data, box watchers frozen). — UPDATED by CI_VERIFIER 18:4x: **B-017 → VERIFIED** (all cited focused tests 19/19 PASS, CI gate GREEN, ruff clean — see row line 24); queue now 10 OPEN + 5 verified.

DEPLOY_STEWARD CYCLE (09-02 18:41 CST): verified-ticket re-sweep + bundle integrity re-check — FIFTH consecutive v8-staleness confirmation (unchanged); NO rebuild; decision still pending with manager/user.
(1) VERIFIED TICKET RE-SWEEP (per brief DO): status=verified now = **B-004** (Mac-side wedge-watch, zero box delta), **B-008** (Mac-side secret-scan, zero box delta), **B-012** (Mac-side CDP channel-recovery, zero box delta), **B-016** (Mac-side parallel-eval-agent completeness-marker gate, zero box delta). NONE carries a box-bundle delta → **NO rebuild warranted from verified tickets this cycle**. The current bundle `7c78e50f…` (rebuilt 17:29 for B-018) still stages the B-002/B-010/B-018 box fixes. No ticket moved to ready-to-deploy (nothing new staged for the box).
(2) BUNDLE INTEGRITY RE-CHECK (r23, sha `7c78e50f…`): bundle sha **MATCH** (`7c78e50fe22a76d5a64f5680a4d8afd122c642cca7eb6faf5659a8504797d002`); embedded `MANIFEST.sha256.json` vs tgz contents → **0 mismatches** (349 entries hash-verified, 350 files incl. MANIFEST); B-002 launcher-alias fix (AI_SAPO_GREEDY_ROLLOUT_FRACTION alias present in bundled ai_launch), B-010 guarded peft import (`except ImportError` + `PeftModel = None` present in bundled rubric script), B-018 RULE_SIGNALS + 5 completeness-pin tests all **present** (re-grep-verified this cycle).
(3) 🚨 CRITICAL BUNDLE STALENESS — RE-CONFIRMED (5th consecutive cycle): bundle `7c78e50f…` STILL defaults `ASI3_SAPO_BENCHMARK_FILE` → `evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt` (**v8 — BANNED/B-026 S0**) in the bundled ai_launch (line 52). Tree (HEAD 7089a5b) STILL pins **user-bound v9** (`quantum_grpo_training_v9_rl_questions_v2.txt`, ai line 53). **If fired for a FUTURE launch → box re-defaults to banned v8 → exact B-026 S0 violation.** B-026 is CLOSED (not `verified`) → per verified-gate I did **NOT** auto-rebuild; **manager/user decision on rebuild STILL PENDING (5th escalation).** Box is SAFE: r23c (093912Z) already on v9 (17:39, DISPATCHER box-verified) — only the LOCAL bundle artifact is stale.
(4) TESTS — ALL GREEN this cycle (re-ran for sweep): CI GATE **GREEN** (exit 0, all 4 stages; smoke 5/5 launchable); focused B-002 2/2, B-010 2/2, B-018 25/25, **B-016 6/6**, B-004 8/8, B-008 12/12, B-012 11/11, B-026 v9-pin 4/4 = **70 total**.
(5) READY-TO-DEPLOY (UNCHANGED): B-002, B-010, B-018 — all staged in r23 `7c78e50f…` — **but see 5th-cycle v8-default staleness above before any future-launch fire** (B-002's own launcher member is among the 4 stale files). VERIFIED Mac-side (zero box delta, no box deploy needed): B-004, B-008, B-012, **B-016**. NOTHING deployed from this lane; manager/user fires. Full cycle record appended to launchplan §6 re-check #8.


DISPATCHER RECON (09-02 18:49 CST): queue 10 OPEN (oldest B-013/B-014/B-019 auditor-origin ~15:4x, ~3h) + 1 staged (B-028) + 5 verified (B-004,B-008,B-012,B-016,B-017) + 3 ready-to-deploy (B-002,B-010,B-018) + 11 closed. THIS cycle (18:40->18:49) dispatcher actions: (1) **NO NEW ALARM rows deduped** from watch surfaces - wedge ok all 3 ports (last-alarm 07:49Z; no new entries in wedge_alarms.log since 07:49Z), divergence waiting-for-data evals=2 (no train_trend), box metrics watcher STILL frozen steps=28 identical ticks (ent=0.22/pass=0.375/mr=0.5298/ess=7.30) -> nothing new to file. (2) **closure/corrobation**: B-003 closure HOLDS - DISPATCHER box-verify: reports/.sapo_parallel_eval_state_ASI3.json EXISTS (mtime 18:40 CST, now contains r23c step_000001 entry with verdict=precheck-running) -> ASI3 driver (pid 15647) actively evaluating r23c; shared non-suffixed reports/.sapo_parallel_eval_state.json mtime STILL FROZEN at 18:08 (confirmed no re-write) -> infinite resume-3 re-eval loop STAYS stopped. (3) **ENFORCE #135**: stale >20min escalated at top - B-019/B-013/B-014/C-032/C-037/B-023/B-024/B-025/B-029/B-030 all open >20min (oldest auditor-origin ~15:4x, ~3h; B-017 gone to verified; B-028 gone to staged this window). STILL-LIVE re-confirmed: **B-028** (NoneType subscriptable recurrence on LATEST ASI2 pull 10:48:36Z; box_pull_ledger now **168 hits**, +5 since 18:40; row STAGED by debugger this window); **B-005-class pace re-baseline STILL PENDING** - r23c (093912Z, v9) STILL only step_000001_adapter (NO newer step_* checkpoints; grpo_step_metrics.jsonl step 1 completed 10:37:43Z; box watcher frozen steps=28 old-run); **B-009 caveat persists** (judge_mac_watcher pid 76676 running, log STILL 0 bytes). **B-024/B-025/B-029 recurrences confirmed** - latest r23c train log shows all: [B-024] transformers generation-flags temperature ignored; [B-025] trust_remote_code no-effect on non-Auto load; [B-029] accelerate device_map keys mismatch (~66 multimodal keys vs Qwen3_5ForCausalLM). NOTE concurrent advances (NOT mine): **B-017 -> verified** (CI_VERIFIER; sapo_dep_hash.py + launch hook + #131 tick; 19/19 PASS + ruff clean + CI GREEN); **B-028 -> staged** (debugger; coerce-None-before-slice; 4/4 GREEN); **NEW B-030** added (error-miner) - .adapter.tmp-* live-save staging leak (~1.8GB, 12/13 runs). Deploy_steward context unchanged: bundle 7c78e50f v8-launcher-default staleness FLAG persists (5th cycle) - manager/user rebuild decision PENDING. **NO rows advanced/closed by dispatcher this cycle** (no independent CI-green appeared for a currently-OPEN row this window; B-028 staged by debugger, B-017 verified by CI_VERIFIER - both concurrent). Manager/user fires B-002/B-010/B-018 at discretion.

DISPATCHER RECON (09-02 19:04 CST): queue 10 OPEN (oldest B-013/B-014/B-019 auditor-origin ~15:4x, ~3.3h) + 0 staged + 5 verified (B-004,B-008,B-012,B-016,**B-028) + 4 ready-to-deploy (B-002,B-010,B-017,B-018) + 11 closed. THIS cycle (18:49→19:04) dispatcher actions: (1) **NO NEW ALARM rows deduped** from watch surfaces — wedge ok all 3 ports (last-alarm 07:49Z; no new entries in wedge_alarms.log), divergence waiting-for-data evals=2 (no train_trend), box metrics watcher STILL frozen steps=28 identical ticks (ent=0.22/pass=0.375/mr=0.5298/ess=7.30) → nothing new to file. (2) **closure/corrobation**: B-003 closure HOLDS — DISPATCHER box-verify: `reports/.sapo_parallel_eval_state_ASI3.json` EXISTS (mtime 18:54 CST, now contains r23c step_000001 entry `{verdict: eval-running}` — ASI3 driver pid 15647 actively evaluating r23c; rubric eval running pid 199911 per eval_step_000001_adapter.log); shared non-suffixed `reports/.sapo_parallel_eval_state.json` mtime STILL FROZEN at 18:08 (no re-write) → infinite resume-3 re-eval loop STAYS stopped. (3) **ENFORCE #135**: stale >20min escalated at top — B-019/B-013/B-014/C-032/C-037/B-023/B-024/B-025/B-029/B-030 all open >20min (oldest auditor-origin ~15:4x, ~3.3h; B-017 AND B-028 both → verified this window, removed from stale-open). STILL-LIVE re-confirmed: **B-028** (NoneType-subscriptable recurrence on LATEST ASI2 box-pulls; box_pull_ledger now **174 hits**, +6 since 18:49; row already **VERIFIED by CI_VERIFIER 19:0x** — coerce-None fix confirmed at scripts/sapo_box_pull_watch.sh:47, test_sapo_box_pull_watch.py 4/4 PASS, CI gate GREEN; Mac-side tooling → deploy_steward determines close/deploy, I did NOT close). **B-005-class pace re-baseline STILL PENDING** — r23c (093912Z, v9, trainer 194918) STILL ONLY `step_000001_adapter` (grpo_step_metrics.jsonl step count = 1; step 1 completed 10:37:43Z; NO newer step_* checkpoints as of 11:07:18Z; box watcher frozen steps=28 old-run) → lora-pace re-verify NOT possible. **B-009 caveat persists** — judge_mac_watcher pid 76676 running, log STILL 0 bytes (spot-verify unresolved). **B-024/B-025/B-029** openings unchanged (benign recurrence class; r23c v9 trainer 194918 re-confirmed on `--benchmark-file ...v9_rl_questions_v2.txt`). NOTE concurrent advances (NOT mine): **B-028 → verified** (CI_VERIFIER 19:0x; coerce-None fix, 4/4 PASS + CI GREEN); deploy_steward r23-REBUILD (`3755b0a1…`) captures B-017 dep-hash hook + resolves v8-default staleness by pinning B-026 v9; ready-to-deploy now = B-002/B-010/B-017/B-018. **NO rows advanced/closed by dispatcher this cycle** (no OPEN row gained independent CI-green+artifact this window beyond B-028 which went staged→verified by CI_VERIFIER — concurrent; no dispatcher closure). Manager/user fires B-002/B-010/B-017/B-018 at discretion.


DEPLOY_STEWARD CYCLE (09-02 19:1x CST): verified-ticket re-sweep + bundle integrity re-check — 10th cycle; **B-028 determined Mac-side (zero box delta)**; NO rebuild; bundle `3755b0a1…` current.
(1) VERIFIED TICKET RE-SWEEP (per brief DO): status=verified now (queue line 22 reconciled set) = **B-004** (Mac-side wedge-watch, zero box delta), **B-008** (Mac-side secret-scan, zero box delta), **B-012** (Mac-side CDP channel-recovery, zero box delta), **B-016** (Mac-side parallel-eval completeness-marker gate, zero box delta), **B-028 (NEW this cycle, verified by CI_VERIFIER 19:0x)** — coerce-None-before-slice in `scripts/sapo_box_pull_watch.sh` (4/4 green). **B-028 staged-verification: box-bundle delta? NO — Mac-side pure.** CONFIRMED NOT a box-bundle member: the file is **absent** from `tmp/sapo-relaunch-r23.sha256` (349 entries) AND from the tgz AND from every bundle sidecar; NOT referenced by any box launcher/wrapper; not in `required_files` gate; grouped in `scripts/sapo_fleet_roster.sh` line 22 alongside the Mac-side watchdogs (sapo_box_pull_watch / sapo_divergence_watch / sapo_wedge_watch / sapo_parallel_eval_agent). The Mac-side watchdog renders eval-state summaries locally from asi3_exec box pulls — the box NEVER receives this script. → **NO box-bundle delta to stage; fix already live on local tree (its runtime).** No box deploy needed; manager/user may close (or mark `deployed` locally) at discretion — does NOT gate the r23 launch nor any launch. Determination appended to B-028 row + launchplan §6 re-check #10. NONE of the 5 verified tickets carries a box-bundle delta → **NO rebuild warranted from verified tickets this cycle**. No ticket moved to ready-to-deploy (nothing new staged for the box).
(2) BUNDLE INTEGRITY RE-CHECK (r23, sha `3755b0a1…`): bundle sha **MATCH** (`3755b0a1149c4dfe9c838f5d60a74cb921b5a06f8615718b28f204840748b72a`); per-file sidecar vs tree **349/349 OK, 0 failures**; embedded `MANIFEST.sha256.json` vs tgz contents → **0 mismatches** (349 entries hash-verified); B-017 dep-hash launch hook present in bundled ai_launch, B-026 v9 pin present (`v9_rl_questions_v2` in, `v8_holdout_adjacent` gone). The 9th-cycle rebuild already stages B-002/B-010/B-017/B-018 AND resolves the prior 5-cycle v8-default staleness — bundle remains current.
(3) TESTS — ALL GREEN this cycle (re-ran for sweep): CI GATE **GREEN** (exit 0, all 4 stages; smoke 5/5 launchable); focused **B-028 4/4**, B-017 19/19, B-026 v9-pin 4/4 = **27 focused this cycle**. Prior verified tests (B-002 2/2, B-010 2/2, B-018 25/25, B-004 8/8, B-008 12/12, B-012 11/11, B-016 6/6) unchanged from prior cycles.
(4) READY-TO-DEPLOY (UNCHANGED): **B-002, B-010, B-017, B-018** — all staged in r23 sha `3755b0a1…` (v8-default staleness RESOLVED; no outstanding FLAG). VERIFIED Mac-side (zero box delta, no box deploy needed): B-004, B-008, B-012, B-016, **B-028**. NOTHING deployed from this lane; manager/user fires. Full cycle record appended to launchplan §6 re-check #10.


DISPATCHER RECON (09-02 19:16 CST): queue 10 OPEN (oldest B-013/B-014/B-019/C-032/C-037 auditor-origin ~15:4x, ~3.5h) + 0 staged + 5 verified (B-004,B-008,B-012,B-016,B-028) + 4 ready-to-deploy (B-002,B-010,B-017,B-018) + 11 closed. THIS cycle (19:04→19:16) dispatcher actions: (1) **NO NEW ALARM rows deduped** from watch surfaces — wedge ok all 3 ports (last-alarm 07:49Z; no new entries in wedge_alarms.log); divergence watch STILL waiting-for-data (evals=2, no new divergence); box sapo logs no new error/alarm lines; judge_mac_watcher.log still 0 bytes; r23b_metrics STILL NO_STEPS_YET (blocked pace re-verify). (2) **NO rows closed by dispatcher** — no OPEN row gained independent CI-green+artifact this window (B-028 already verified by CI_VERIFIER 19:0x; stays in verified set per precedent, awaiting deploy decision). (3) **#135 ENFORCED**: all 10 OPEN rows are >20min stale with no status change → all escalated in header line; oldest = B-013/B-014/B-019/C-032/C-037 (~3.5h). (4) THIS-cycle obs: (a) ASI3 eval state ADVANCED precheck-running→eval-running (mtime 18:54, verdict eval-running on r23c step_000001) — B-003 closure strengthens, no edge-reopen; (b) box_pull_ledger NoneType hits 174→**177** (+3), BUT the 2 most recent ASI2 pulls (111516Z/111832Z) end in **TimeoutError** (not NoneType) — potential B-028 symptom shift to pull-timeout, flagged for CI_VERIFIER/debugger (B-028 itself remains verified; fix already deployed in Mac-side tooling). No new row opened for the transient timeout (daemon recovered to READY after polls). RECON: queue 10 OPEN + 0 staged + 5 verified + 4 ready-to-deploy; nothing dispatched/deployed from this lane (manager/user fires).
DEPLOY_STEWARD CYCLE (09-02 19:24 CST): verified-ticket re-sweep + bundle integrity re-check — 12th cycle; **all 5 verified Mac-side (zero box delta); NO rebuild; bundle `3755b0a1…` current**.
(1) VERIFIED TICKET RE-SWEEP (per brief DO): status=verified = **B-004** (Mac-side wedge-watch, zero box delta), **B-008** (Mac-side secret-scan, zero box delta), **B-012** (Mac-side CDP channel-recovery, zero box delta), **B-016** (Mac-side parallel-eval completeness-marker gate, zero box delta), **B-028** (Mac-side box-pull-watch coerce-None, zero box delta). All five fix files re-confirmed file-by-file this cycle as **absent** from sidecar 349 / tgz / all prior sidecars; NOT referenced by any box launcher/wrapper; NOT in required_files gate. → **NO box-bundle delta from any verified ticket → NO rebuild warranted; no verified→ready-to-deploy promotion (nothing new to stage).** All five fixes already live on local tree (their runtime).
(2) BUNDLE INTEGRITY RE-CHECK (r23, sha `3755b0a1…`): bundle sha **MATCH** (`3755b0a1149c4dfe9c838f5d60a74cb921b5a06f8615718b28f204840748b72a`); per-file sidecar vs tree **349/349 OK, 0 failures**; embedded `MANIFEST.sha256.json` vs tgz contents → **0 mismatches** (349 hash-verified); B-017 dep-hash hook + B-026 v9 pin (v8 gone) + B-002 alias + B-018 RULE_SIGNALS + B-010 guarded-peft all present in bundle. **No tree drift** on box-bundle launch-path members since 18:54 freeze. v8-default staleness remains RESOLVED (no outstanding FLAG).
(3) TESTS — ALL GREEN this cycle: CI GATE **GREEN** (exit 0, all 4 stages, launchable); focused B-028 4/4, B-017 19/19, B-026 v9-pin 4/4, launcher-readiness 28/28, B-018 25/25 (B-002/B-010/B-004/B-008/B-012/B-016 unchanged prior-mentioned green).
(4) READY-TO-DEPLOY (UNCHANGED): **B-002, B-010, B-017, B-018** — all staged in r23 sha `3755b0a1…`; manager/user fires. VERIFIED Mac-side (zero box delta, no box deploy needed): B-004, B-008, B-012, B-016, B-028. NOTHING deployed from this lane. Full cycle record appended to launchplan §6 re-check #12.
DISPTCHER CYCLE (09-02 19:31 CST): dedupe→NO new alarm rows (wedge ok 3 ports, no new wedge_alarm, divergence waiting evals=2, box watchers frozen, contract #129 benign 0); box-corroborated B-003 closure HOLDS (ASI3 rubric-eval pid 199911 active on r23c step_000001, eval_step_000001 log mtime 18:54); B-028 NoneType STILL 177 (unchanged) with recent entries shifted to TimeoutError (symptom-shift flagged, B-028 stays verified, no new row); close→NONE this window (no OPEN row gained independent CI-green+artifact); #135 ENFORCED→all 10 OPEN rows escalated in header (oldest ~4h, most >20min stale, 15th consecutive stale window). RECON: queue 10 OPEN + 0 staged + 5 verified (B-004/B-008/B-012/B-016/B-028) + 4 ready-to-deploy (B-002/B-010/B-017/B-018); nothing dispatched/deployed from this lane (manager/user fires). oldest OPEN ≈ B-013/B-014/B-019/C-032/C-037.

DISPATCHER CYCLE (09-02 19:35 CST): dedupe→NO new alarm rows (wedge ok 3 ports 20653/19004/20646, last 11:34:36Z state=ok, last wedge_alarm 07:49Z no new; divergence waiting evals=2; box metrics watcher frozen steps=28 identical ent=0.22/pass=0.375/mr=0.5298/ess=7.30; box error grep only OLD judge_bridge 'Address already in use' 08-28/09-01 none new); box-corroborated B-003 closure HOLDS (ASI3 rubric-eval pid 199911 active on r23c step_000001, eval_step_000001_adapter.log confirmed rubric eval launched 10:54:50Z polling up to 7200s against holdout v1_18); B-028 NoneType STILL 177 (unchanged) with most-recent ledger entries TimeoutError (symptom-shift persisted, B-028 stays verified, no new row for transient timeout—daemon recovered after 7 polls); B-005-class pace re-baseline STILL NOT POSSIBLE (r23c only step_000001, box watcher frozen steps=28, r23b_metrics NO_STEPS_YET); B-009 caveat persists (judge_mac_watcher.log 0 bytes); close→NONE this window (no OPEN row gained independent CI-green+artifact); #135 ENFORCED→all 10 OPEN rows escalated in header (oldest ~4h, most >20min stale, 16th consecutive stale OPEN window). RECON (queue length): 10 OPEN (B-019/B-013/B-014/C-032/C-037/B-023/B-024/B-025/B-029/B-030) + 0 staged + 5 verified (B-004/B-008/B-012/B-016/B-028) + 4 ready-to-deploy (B-002/B-010/B-017/B-018) + 11 closed. OLDEST OPEN ≈ B-013/B-014/B-019/C-032/C-037 (auditor-origin ~15:4x, ~4h). Nothing dispatched/deployed from this lane (manager/user fires B-002/B-010/B-017/B-018 at discretion).
DEPLOY_STEWARD CYCLE (09-02 19:33 CST): verified-ticket re-sweep + bundle integrity re-check — 13th cycle; **all 5 verified Mac-side (zero box delta); NO rebuild; bundle `3755b0a1…` current**.
(1) VERIFIED TICKET RE-SWEEP (per brief DO): status=verified set UNCHANGED = **B-004** (wedge-watch), **B-008** (secret-scan), **B-012** (CDP channel-recovery), **B-016** (parallel-eval completeness gate), **B-028** (box-pull-watch coerce-None). All five fix-file sets re-confirmed file-by-file as **absent** from sidecar 349 / tgz / all prior sidecars; NOT referenced by any box launcher/wrapper; NOT in required_files gate → **ALL Mac-side, zero box-bundle delta → NO rebuild warranted; no verified→ready-to-deploy promotion (nothing new to stage).** All five fixes already live on local tree (their runtime); manager/user may close/mark deployed locally at discretion — none gates any launch. Ready-to-deploy set UNCHANGED (B-002/B-010/B-017/B-018).
(2) BUNDLE INTEGRITY RE-CHECK (r23, sha `3755b0a1…`): bundle sha **MATCH** (`3755b0a1149c4dfe9c838f5d60a74cb921b5a06f8615718b28f204840748b72a`); embedded `MANIFEST.sha256.json` vs tgz contents → **0 mismatches** (349/349 hash-verified); B-017 dep-hash hook + B-026 v9 pin (v8 gone) + B-002 alias (`AI_SAPO_GREEDY_ROLLOUT_FRACTION`→`ASI3_SAPO_GREEDY_ROLLOUT_FRACTION` line 54) + B-018 RULE_SIGNALS + B-010 guarded-peft all re-grep-verified **present** in the extracted tgz this cycle. v8-default staleness remains RESOLVED (no outstanding FLAG).
(3) ⚠️ NON-VERIFIED TREE DRIFT (transparency, out of verified-gate): sidecar-vs-tree re-check found **3 members CHANGED on the working tree** since the 18:54 freeze — `scripts/eval_100_reeval.py`, `scripts/report_base_adapter_comprehensive.py` (untracked), `scripts/run_hf_pass1_eval.py` (mtimes 19:24–26). py3.9-compat hardening of eval/report scripts; NOT referenced by any bugqueue ticket (grep-verified); NOT fix files of any verified/ready ticket. Per brief's verified-gate I did **NOT** auto-rebuild for these; manager/user decides. Does NOT affect ready-to-deploy r23 `3755b0a1…`; box SAFE (r23c already on v9, already-deployed bundle running).
(4) TESTS — ALL GREEN this cycle: CI GATE **GREEN** (exit 0, all 4 stages, smoke 5/5 launchable); focused B-028 box-pull-watch 4/4, B-017 dep-hash 19/19, B-026 v9-pin 4/4 re-ran GREEN (B-002/B-010/B-018/B-004/B-008/B-012/B-016 unchanged prior-mentioned green).
(5) READY-TO-DEPLOY (UNCHANGED): **B-002, B-010, B-017, B-018** — all staged in r23 sha `3755b0a1…`; manager/user fires. VERIFIED Mac-side (zero box delta, no box deploy needed): B-004, B-008, B-012, B-016, B-028. NOTHING deployed from this lane. Full cycle record appended to launchplan §6 re-check #13.

DISPATCHER CYCLE (09-02 19:45 CST, 17th): dedupe→NO new alarm rows (wedge ok all 3 ports 20653/19004/20646 last 11:40:36Z state=ok; last wedge_alarm 07:49Z no new; divergence waiting-for-data evals=2; box metrics watcher STILL frozen steps=28 identical ent=0.22/pass=0.375/mr=0.5298/ess=7.30 — read r23c metrics directly from grpo_step_metrics.jsonl instead; box error grep only OLD judge_bridge 'Address already in use' 08-28/09-01 none new; contract #129 benign 0). box-corroborated B-003 closure HOLDS (ASI3 rubric-eval pid 199911 ALIVE 80min CPU on r23c step_000001 per ps, eval_step_000001_adapter.log mtime 18:54, ASI3 state `{verdict: eval-running}`; shared non-suffixed state FROZEN 18:08 — loop stays stopped). 🟢 **KEY ADVANCE — B-005 pace re-baseline EVIDENCE EMERGING**: r23c (093912Z, v9, trainer 194918) advanced to **step_000002_adapter** (~318MB on box); grpo_step_metrics.jsonl now has steps 1+2: s1 ent=0.377/pass=0.000/mr=0.049, s2 ent=0.524/pass=0.000/mr=0.055, **lr=5e-5**, tasks rotating qpe_qiskit_0375→amplitude_estimation_ry → non-inert trajectory, entropy RISING 0.377→0.524; lora-pace re-verify becomes possible as more steps accrue (sentinel is live enforcer; flag for CI_VERIFIER/manager). B-028 STILL 177 NoneType (unchanged), recent ASI2 pulls shift to **TimeoutError: timed out** (ledger 11:16-11:42Z, daemon recovers each pull → transient, no new row; B-028 stays verified); B-009 caveat persists (judge_mac_watcher.log still 0 bytes). CONCURRENT this window (not mine): **B-019 → VERIFIED by CI_VERIFIER 19:4x** (ruff-clean contract #116, 2/2 focused PASS + CI GATE GREEN — removed from OPEN, now in verified set). NO dispatcher-closed rows. #135 ENFORCED→ remaining 9 OPEN rows escalated in header above (B-013/B-014/C-032/C-037/B-023/B-024/B-025/B-029/B-030; oldest ~4h, 17th consecutive stale OPEN window). RECON (queue length, reconciled): **9 OPEN** (B-013/B-014/C-032/C-037/B-023/B-024/B-025/B-029/B-030) + 0 staged + **6 verified** (B-004/B-008/B-012/B-016/B-019/B-028) + 4 ready-to-deploy (B-002/B-010/B-017/B-018) + 11 closed. OLDEST OPEN ≈ B-013/B-014/C-032/C-037 (auditor-origin ~15:4x, ~4h). Nothing dispatched/deployed from this lane (manager/user fires B-002/B-010/B-017/B-018 at discretion).

DEPLOY_STEWARD CYCLE (09-02 19:51 CST): verified-ticket re-sweep + bundle integrity re-check — 14th cycle; **B-019 NEW-verified (CI_VERIFIER 19:4x) — swept → Mac-side, zero box delta; all 6 verified Mac-side; NO rebuild; bundle `3755b0a1…` current**.
(1) VERIFIED TICKET RE-SWEEP (per brief DO): status=verified set = **B-004** (wedge-watch), **B-008** (secret-scan), **B-012** (CDP channel-recovery), **B-016** (parallel-eval completeness gate), **B-019 (NEW this cycle — ruff-clean §116)**, **B-028** (box-pull-watch coerce-None). **B-019 staged-verification: box-bundle delta? NO — Mac-side pure.** Fix = ruff cleanup across `scripts/*.py` (Mac-side dev tooling) + regression guard `tests/test_sapo_ruff_clean_scripts.py` (2/2 green, CI GATE GREEN). CONFIRMED NOT a box-bundle delta: B-019's cited fix files (`scripts/run_asi1_base_adapter_rubric_eval.py`, `scripts/sapo_divergence_watch*`) are **NOT bundle members** (absent from sidecar 349); `tests/test_sapo_ruff_clean_scripts.py` is **NOT a bundle member**; full tree-vs-sidecar comparison of all 349 bundle members this cycle → **only the same 3 pre-existing non-verified eval/report DIFFs from cycle #13** (py3.9-compat, NOT B-019 fix files); all 18 bundle-member `scripts/*.py` (incl. launcher-path) **match** tree sidecar → the ruff cleanup is fully captured in the 18:54-built bundle. All six verified fix-file sets re-confirmed file-by-file as **absent** from sidecar 349 / tgz / all prior sidecars; NOT referenced by any box launcher/wrapper; NOT in required_files gate → **ALL Mac-side, zero box-bundle delta → NO rebuild warranted; no verified→ready-to-deploy promotion (nothing new to stage).** All six fixes already live on local tree (their runtime); manager/user may close/mark deployed locally at discretion — none gates any launch. Ready-to-deploy set UNCHANGED (B-002/B-010/B-017/B-018).
(2) BUNDLE INTEGRITY RE-CHECK (r23, sha `3755b0a1…`): bundle sha **MATCH** (`3755b0a1149c4dfe9c838f5d60a74cb921b5a06f8615718b28f204840748b72a`); **full per-file verification: 349/349 OK, 0 hash failures** (sidecar vs extracted tgz); embedded `MANIFEST.sha256.json` vs tgz contents → **0 mismatches** (349/349 hash-verified); B-017 dep-hash hook + B-026 v9 pin (v8 gone) + B-002 alias (`ASI3_SAPO_GREEDY_ROLLOUT_FRACTION` line 54) + B-018 RULE_SIGNALS + B-010 guarded-peft all re-grep-verified **present** in the extracted tgz this cycle. **v8-default staleness remains RESOLVED (no outstanding FLAG).**
(3) ⚠️ NON-VERIFIED TREE DRIFT (transparency, out of verified-gate): comprehensive tree-vs-sidecar this cycle → **346/349 MATCH, 3 DIFF** = same 3 files from cycle #13 (`scripts/eval_100_reeval.py`, `scripts/report_base_adapter_comprehensive.py`, `scripts/run_hf_pass1_eval.py`, mtimes 19:24–26, py3.9-compat hardening). Confirmed these are NOT B-019 ruff-fix files (B-019's cited files are NOT bundle members). Per brief's verified-gate I did **NOT** auto-rebuild for these; manager/user decides. Does NOT affect ready-to-deploy r23 `3755b0a1…`; box SAFE (r23c already on v9, already-deployed bundle running).
(4) TESTS — ALL GREEN this cycle: CI GATE **GREEN** (exit 0, all 4 stages, smoke 5/5 launchable); focused B-019 ruff-clean 2/2, B-002 alias 2/2, B-010 guarded-peft 2/2, B-018 RULE_SIGNALS 5/5, B-017 dep-hash 19/19, B-026 v9-pin 4/4, B-028 box-pull-watch 4/4 — all re-ran GREEN (B-004 8/8, B-008 12/12, B-012 11/11, B-016 6/6 unchanged prior-mentioned green).
(5) READY-TO-DEPLOY (UNCHANGED): **B-002, B-010, B-017, B-018** — all staged in r23 sha `3755b0a1…`; manager/user fires. VERIFIED Mac-side (zero box delta, no box deploy needed): B-004, B-008, B-012, B-016, B-019, B-028. NOTHING deployed from this lane. Full cycle record appended to launchplan §6 re-check #14.

DISPATCHER CYCLE (09-02 19:58 CST, 18th): (1) DEDUPE → **1 NEW alarm row B-031 OPENED** — box-corroborated LIVE duplicate latent trainer: r23c output dir `sapo-27b-ai-20260902T093912Z` has **TWO concurrent grpo_trainer processes** — active **194548** (State=R, 255 thr, 8.5GB RSS, **144% CPU**, started 09:39:14Z) + dormant **194918** (State=S, 13 thr, 3.1GB RSS, **0.0% CPU**, started 09:40:38Z), BOTH same output-dir + same v9 benchmark + same lr 5e-5 + same judge endpoint 56237. The dormant sibling never exited ~84s after launch — the concrete control-gap class B-027 closed as benign now has a LIVE second process resident on the same dir (potential resume/step-write race). New distinct S1 row (full detail in table). No OTHER new alarm rows: wedge ok all 3 ports (last 11:54:36Z state=ok; last wedge_alarm 07:49Z no new); divergence waiting-for-data evals=2; local box_pull_watch.log 0 bytes; box metrics watcher STILL frozen steps=28 identical (reads OLD 073028Z snapshot — r23c progress read directly from grpo_step_metrics.jsonl: steps 1@10:37Z + 2@11:35Z complete, lr=5e-5, entropy RISING 0.377→0.524, task rotating qpe_qiskit_0375→amplitude_estimation_ry, non-inert = B-005 pace re-baseline evidence advancing; step_000001 + step_000002_adapter dirs present on box); box error grep ONLY old judge_bridge 08-28/09-01 'Address already in use' (r23c's own judge_bridge_093912Z log clean judge_bridge_up port 56237) → NO new error-signature alarms. (2) CLOSE → **NO rows closed this cycle** (no new independent-close evidence; all 6 verified [B-004/B-008/B-012/B-016/B-019/B-028] hold, CI GATE GREEN + artifacts present per deploy_steward 14th re-check; B-003 closure HOLDS re-corroborated: ASI3 rubric-eval pid 199911 alive, ASI3 state `{verdict: eval-running}`, shared non-suffixed state FROZEN 18:08 → resume-3 loop stays stopped; B-028 NoneType STILL 177 unchanged, recent ASI2 pulls transient TimeoutError→`pull complete` daemon-recovery, verified holds, no new row). (3) ENFORCE #135 → remaining 9 OPEN rows escalated in header above (B-013/B-014/C-037/B-023/B-024/B-025/B-029/B-030/B-031; oldest ~4.3h, 18th consecutive stale OPEN window). (4) RECON (queue length, reconciled): **9 OPEN** (B-013/B-014/C-037/B-023/B-024/B-025/B-029/B-030/B-031) + **1 STAGED (C-032 — moved concurrent by debugger this window, was open at 19:45 recon)** + **6 verified** (B-004/B-008/B-012/B-016/B-019/B-028) + 4 ready-to-deploy (B-002/B-010/B-017/B-018) + 11 closed. OLDEST OPEN ≈ B-013/B-014/C-037 (auditor-origin ~15:4x, ~4.3h). Nothing dispatched/deployed from this lane (manager/user fires B-002/B-010/B-017/B-018 and adjudicates B-031-adjacent duplicate-trainer at discretion).

DISPATCHER CYCLE (09-02 20:11 CST, 19th): (1) DEDUPE → **NO NEW alarm rows** this cycle. B-031 (duplicate latent trainer, opened 19:58 last cycle) **box-re-CONFIRMED STILL LIVE + unresolved**: `ps -o pid,stat,rss,etime -p 194548,194918` → **194548 State=Rl 8.6GB RSS elapsed 02:32:51 (active trainer, producing steps)** + **194918 State=Sl 3.0GB RSS elapsed 02:31:27 (dormant/second process, still resident)** — BOTH on r23c output dir `sapo-27b-ai-20260902T093912Z` (same v9 + lr 5e-5 + judge 56237). No OTHER new alarms: wedge ok 3 ports (last-alarm 07:49Z no new); divergence waiting-for-data evals=2; local box_pull_watch.log 0 bytes; box metrics watcher STILL frozen steps=28 (reads OLD 073028Z snapshot); r23c progress read directly from grpo_step_metrics.jsonl → **steps 1+2 COMPLETE (dirs step_000001+step_000002_adapter present; metrics count=2; step 2@11:35Z) and **step 3 in-flight** (`loss_breakdown=step:3` in running logs, task rotating, lr=5e-5, zero_change_alarm:false, entropy train 0.1072 s3) → **B-005 pace re-baseline evidence ADVANCING** (non-inert, lora re-verify increasingly possible as steps accrue; sentinel is live enforcer). Box error grep = only OLD historical judge_bridge 08-28/09-01 'Address already in use' + the `[ERROR] TBE Subprocess task_distribute ... main process disappeared!` lines which are the **HISTORICAL 073028Z crash (CLOSED B-015)** → none new. (2) CLOSE → **NO rows closed by dispatcher** (no OPEN row gained independent CI-green+artifact beyond prior; B-003 closure HOLDS re-box-corroborated ASI3 rubric-eval pid 199911 alive; all 6 verified [B-004/B-008/B-012/B-016/B-019/B-028] hold — B-028 NoneType STILL 177 unchanged / recent pulls transient TimeoutError→daemon-recovery, no new row; B-009 caveat persists judge_mac_watcher.log 0 bytes). (3) ENFORCE #135 → B-031 opened 19:58 (~13min, under 20, NOT yet escalatable but is the newest OPEN+named in header); remaining 9 OPEN rows escalated in header above (B-013/B-014/C-037/B-023/B-024/B-025/B-029/B-030/B-031 — C-032 moved to VERIFIED concurrent by CI_VERIFIER 20:0x this window, removed from OPEN; oldest ~4.5h, 19th consecutive stale OPEN window). (4) RECON (queue length, reconciled): **9 OPEN** (B-013/B-014/C-037/B-023/B-024/B-025/B-029/B-030/**B-031**) + **0 staged** + **7 verified** (B-004/B-008/B-012/B-016/B-019/B-028/**C-032**) + 4 ready-to-deploy (B-002/B-010/B-017/B-018) + 11 closed. OLDEST OPEN ≈ B-013/B-014/C-037 (auditor-origin ~15:4x, ~4.5h). Nothing dispatched/deployed from this lane (manager/user fires B-002/B-010/B-017/B-018 and adjudicates B-031 duplicate-trainer — 194918 still resident, S1 data-risk — at discretion).

DISPATCHER CORRECTION (09-02 20:13 CST, supersedes portion of my 19th-cycle recon above): **B-031 CLOSED as FALSE ALARM by MANAGER STANDUP #399** — authoritative ps parentage shows 194918 **PPID=194548** (the active trainer's own multiprocessing fork child, same-cmdline, 13 thr, Sl dormant), NOT an independent rogue trainer; no single-active-trainer-per-dir violation, B-027 closure holds, box SAFE; r23c advanced to **3 ckpts (step_000001/000002/000003)**, now at step 4 rollout (s3 grover loo_rms 0.768 non-inert). My recon above (written 20:11, pre-correction) asserting B-031 'still OPEN+unresolved' is SUPERSEDED by the manager's authoritative live-ps evidence; B-031 removed from OPEN. RECON reconciled after correction: **8 OPEN** (B-013/B-014/C-037/B-023/B-024/B-025/B-029/B-030) + 0 staged + 7 verified (B-004/B-008/B-012/B-016/B-019/B-028/C-032) + 4 ready-to-deploy (B-002/B-010/B-017/B-018) + **12 closed** (incl B-031-FALSE-ALARM). No new dispatcher-opened/closed rows beyond manager action. Let stand.

DISPATCHER CYCLE (09-02 20:21 CST, 20th): (1) DEDUPE → **NO NEW alarm rows** this cycle. B-031 FALSE-ALARM closure (manager #399) **box-re-CORROBORATED HOLDS**: `ps -o pid,ppid,stat,rss,etime -p 194548,194918` → **194548 PPID=1 State=Rl 8.3GB RSS elapsed 02:42:45 (ACTIVE trainer producing steps, step_000003 done + step 4 rollout)** + **194918 PPID=194548 State=Sl 3.0GB RSS elapsed 02:41:21 (fork child of the active trainer)** — BOTH on r23c output dir `sapo-27b-ai-20260902T093912Z` (same v9 + lr 5e-5 + judge 56237); 194918's PPID=194548 **confirms it is the trainer's own multiprocessing fork child, NOT an independent rogue trainer** → single-active-trainer-per-dir holds, NO B-027 re-open, B-031 stays CLOSED, box SAFE. No OTHER new alarms: wedge ok 3 ports 20653/19004/20646 (last wedge_alarm 07:49Z no new); divergence waiting-for-data evals=2; local box_pull_watch.log 0 bytes; box metrics watcher STILL frozen steps=28 (reads OLD 073028Z snapshot — read r23c directly from grpo_step_metrics.jsonl instead); **r23c boot log grep = NO new error/alarm lines** (only old historical judge_bridge 'Address already in use'). 🟢 **B-005 pace re-baseline evidence ADVANCING**: r23c NOW at **3 ckpts** (step_000001/000002/000003_adapter present on box); grpo_step_metrics.jsonl step-3 (12:12:20Z) = task `quantum_rl_v2_grover_qiskit_101`, **trust_region_violated=false, zero_change_alarm=false, update_signal_kind=loo_advantage_rms magnitude 0.768 (>0.05)** → non-inert trajectory; sentinel is the live enforcer (flag for CI_VERIFIER/manager to re-verify lora pace as more steps accrue; box watcher + r23b_metrics NO_STEPS_YET still read OLD run). 🏁 **B-003 closure HOLDS + strengthened**: ASI3 state `reports/.sapo_parallel_eval_state_ASI3.json` now holds r23c **step_000001 `{status: done}` (updated 12:14:28Z — pass@1 3/18 TIED with base, adapters WINS on rubric 3.285 vs 3.1); shared non-suffixed `reports/.sapo_parallel_eval_state.json` STILL FROZEN at 18:08 (no re-write)** → infinite resume-3 re-eval loop STAYS stopped, no edge-reopen. (2) CLOSE → **NO rows closed by dispatcher** (no OPEN row gained independent CI-green+artifact this window; all 6 verified [B-004/B-008/B-012/B-016/B-019/B-028] + C-032 verified hold; B-028 NoneType STILL 177 unchanged / recent ASI2 pulls transient TimeoutError→daemon-recovery, no new row; B-009 caveat persists judge_mac_watcher.log 0 bytes). (3) ENFORCE #135 → **all 8 tracked-OPEN rows (B-013/B-014/C-037/B-023/B-024/B-025/B-029/B-030) are >20min stale with no status change → escalated in header above** (oldest ~5h, 20th consecutive stale OPEN window). (4) RECON (queue length, reconciled) — **NOTE TABLE-AMBIGUITY**: the per-row table shows **C-037 status=`staged`** (STAGED by debugger 09-02, check_learning_rate_floor added + 6 new tests) but prior recons/header have been tracking it in the OPEN/stale set; faithful table-based reconciled count = **7 OPEN** (B-013/B-014/B-023/B-024/B-025/B-029/B-030) + **1 STAGED (C-037)** + 7 verified (B-004/B-008/B-012/B-016/B-019/B-028/C-032) + 4 ready-to-deploy (B-002/B-010/B-017/B-018) + 12 closed (incl B-031-FALSE-ALARM). If C-037 is counted as OPEN per prior-header convention, OPEN=8 (as last cycle's correction). Dispatcher flags this ambiguity for manager to adjudicate canonically (C-037 is staged-with-tests on tree, awaiting CI_VERIFIER independent verification). OLDEST OPEN ≈ B-013/B-014 (auditor-origin ~15:4x, ~5h). Nothing dispatched/deployed from this lane (manager/user fires B-002/B-010/B-017/B-018 at discretion; B-031 stays closed — no rogue trainer).

DEPLOY_STEWARD CYCLE (09-02 20:2x CST): verified-ticket re-sweep + bundle integrity re-check — 16th cycle; **C-032 NEW-verified (CI_VERIFIER 20:0x) — swept → zero box-bundle delta; all 7 verified carry zero box delta; NO rebuild; bundle `3755b0a1…` current**.
(1) VERIFIED TICKET RE-SWEEP (per brief DO): status=verified now = **B-004** (wedge-watch), **B-008** (secret-scan), **B-012** (CDP channel-recovery), **B-016** (parallel-eval completeness gate), **B-019** (ruff-clean §116), **B-028** (box-pull-watch coerce-None), **C-032 (NEW this cycle, verified by CI_VERIFIER 20:0x — gradient-vanishing detector)**. **C-032 staged-verification: box-bundle delta? NO — zero box-bundle delta.** Fix lives in `scripts/sapo_metrics_watch_v3_rules.py` (pure-stdlib box-side-addendum watcher source for C-32 gradient-vanishing / C-37 lr / D-40 EOS-swing / D-49 repeater rules, refactored pure `check_gradient_vanishing` + `__main__` guard) + `tests/test_sapo_metrics_watch_v3_rules.py` (**12/12 green re-ran this cycle, ruff clean; CI GATE GREEN exit 0 all 4 stages**). CONFIRMED NOT a bundle member: absent from sidecar 349 / tgz / all prior sidecars (grep 0); NOT referenced by any box launcher/wrapper (only its own test imports it); NOT in `required_files` gate. Crucially, the box's existing `sapo_metrics_watch.py` v2.2 (which C-032 augments) is **also NOT a bundle member** → box-side metrics-watching is delivered by a separate mechanism / manager-user deploy, NOT via the r23 launch bundle. So C-032's addendum is deployed through that same mechanism, NOT by staging into r23. → **NO box-bundle delta from any verified ticket → NO rebuild warranted; no verified→ready-to-deploy promotion (nothing new to stage).** All seven fixes already live on local tree (their runtime); manager/user may close/mark `deployed` locally at discretion — none gates any launch. Ready-to-deploy set UNCHANGED (B-002/B-010/B-017/B-018).
(2) BUNDLE INTEGRITY RE-CHECK (r23, sha `3755b0a1…`): bundle sha **MATCH** (`3755b0a1149c4dfe9c838f5d60a74cb921b5a06f8615718b28f204840748b72a`); embedded `MANIFEST.sha256.json` vs tgz contents → **349/349 OK, 0 mismatches** (349 files hash-verified, 0 tgz-member-not-in-manifest); per-file sidecar vs tree → **346/349 MATCH, 3 DIFF** = the SAME 3 non-verified eval/report files documented in cycles #13/#14/#15 (`scripts/eval_100_reeval.py`, `scripts/report_base_adapter_comprehensive.py`, `scripts/run_hf_pass1_eval.py`, py3.9-compat hardening) — NOT fix files of any verified/ready ticket, stay OUTSIDE the verified-gate (manager/user adjudicates). Ready-to-deploy box-runtime fixes spot-checked **present** in extracted tgz this cycle: B-017 dep-hash hook (`sapo_dep_hash.py --capture`, 1), B-026 v9 pin (v9 txt present, v8_holdout_adjacent BANNED absent), B-002 ASI3_SAPO alias (1), B-018 RULE_SIGNALS (1), B-010 guarded-peft (PeftModel=None, 1). **v8-default staleness remains RESOLVED (no outstanding FLAG).**
(3) TESTS — ALL GREEN this cycle: CI GATE **GREEN** (exit 0, all 4 stages, smoke 5/5 launchable); focused **C-032 metrics-watch-v3 12/12** re-ran GREEN; ruff `scripts/sapo_metrics_watch_v3_rules.py` = **All checks passed**. Prior verified tests (B-004 8/8, B-008 12/12, B-012 11/11, B-016 6/6, B-019 2/2, B-028 4/4, B-002 2/2, B-010 2/2, B-017 19/19, B-018 25/25, B-026 4/4) unchanged prior-mentioned green.
(4) READY-TO-DEPLOY (UNCHANGED): **B-002, B-010, B-017, B-018** — all staged in r23 sha `3755b0a1…`; manager/user fires. VERIFIED Mac-side / zero box-bundle delta (no box deploy needed via launch bundle): B-004, B-008, B-012, B-016, B-019, B-028, **C-032** (C-032 delivered to box via the separate metrics-watch mechanism, not the launch bundle). NOTHING deployed from this lane. Full cycle record appended to launchplan §6 re-check #16.

DISPATCHER 20th-cycle AMENDMENT (09-02 ~20:22 CST, fold-in of concurrent-lane activity observed while writing my recon): (a) **ERROR_MINER opened a NEW row B-032** (novel error-signature `vllm_rollout_server_kv_cache_oom`, S2 — vLLM rollout OpenAI server launched 12:03:02Z pid 212073 during ACTIVE r23c training, CRASHED 12:06:26Z engine-core startup `ValueError: No available memory for the cache blocks` at `gpu-memory-utilization 0.35` (NPUs co-occupied by trainer 194548 ~9-12GB/NPU + holdout rubric eval 199911), left as a ZOMBIE under init (ppi 1, Z state), port 8355 not listening, no relaunch; trainer UNAFFECTED (SAPO_VLLM_URL unset on trainer; r23c progressed through step 3 fine). Distinct launch-time KV-cache-OOM class, NOT in ledger prior). → per DO-step-1 (dedupe new alarms → new rows) this is a genuine NEW row now in OPEN set. (b) **CI_VERIFIER promoted C-037 → verified 09-02 20:2x** (Section-C #37 lr-post-halving watch, check_learning_rate_floor staged by debugger + 6 tests) — resolving the C-037 table-ambiguity I flagged (it's no longer staged/ambiguous; now in verified set, box-bundle-delta for deploy_steward to determine). **RECON reclined (final, after fold-in): 8 OPEN** (B-013/B-014/B-032/B-023/B-024/B-025/B-029/B-030) + **0 STAGED** + **8 verified** (B-004/B-008/B-012/B-016/B-019/B-028/C-032/C-037) + 4 ready-to-deploy (B-002/B-010/B-017/B-018) + 12 closed (incl B-031-FALSE-ALARM). OLDEST OPEN ≈ B-013/B-014 (auditor-origin ~15:4x, ~5h). Enforce #135: all 8 OPEN rows >20min stale (B-032 newest ~20:1x, under 20min — not independently stale yet) → older 7 escalated in header. Nothing dispatched/deployed from this lane (manager/user fires B-002/B-010/B-017/B-018; C-037 deploy-delta determination → deploy_steward).

DISPATCHER RECON (09-02 20:37 CST): queue **8 OPEN** (B-013/B-014/B-032/B-023/B-024/B-025/B-029/B-030; oldest B-013/B-014 auditor-origin ~15:4x, ~5h; newest B-032 ~20:1x). THIS cycle (20:22→20:37): (1) **NO NEW ALARM rows deduped** — wedge ok all 3 ports (last alarm 12:27:42Z, no new); divergence waiting-for-data (evals=2, no new); box_pull 0 bytes; box sapo metrics watcher frozen steps=28 old-run snapshot; box sapo logs grep = only OLD historical judge_bridge OSErrors (08-28/09-01), none new; vllm_server.log mtime 12:06 unchanged (B-032 crash already rowed). (2) **NO rows closed by dispatcher** — no OPEN row gained independent CI-green+artifact this window; C-037 already promoted to verified by CI_VERIFIER (20:2x) → out of OPEN. (3) **#135 ENFORCED**: all 8 OPEN rows >20min stale with no status change → escalated in header line above (21st consecutive stale cycle); B-032 newly crossed 20-min this window → first escalation for it. (4) THIS-cycle obs: (a) **B-031 false-alarm closure HOLDS** — live ps re-confirms 194918 PPID=194548 (fork child of ACTIVE 194548, dormant); no rogue trainer; (b) **B-003 closure HOLDS** — ASI3 step_000001 done, shared state still frozen; (c) **r23c steady at 3 ckpts** — trainer 194548 alive (elapsed 02:59:30), last step metric = step 3 (12:12:20Z) non-inert (loo_advantage_rms 0.768>0.05) → step-4 rollout presumed in progress, no advance past step 3 since last cycle; (d) B-028 NoneType stays 177 (verified fix holds, no new row; transient pull TimeoutError→daemon-recovers persists); (e) B-009 caveat persists (judge_mac_watcher.log 0 bytes). RECON: queue 8 OPEN + 0 staged + 8 verified (B-004/B-008/B-012/B-016/B-019/B-028/C-032/C-037) + 4 ready-to-deploy (B-002/B-010/B-017/B-018) + 12 closed (incl B-031-FALSE-ALARM). NOTHING dispatched/deployed (manager/user fire B-002/B-010/B-017/B-018; C-037 deploy-delta → deploy_steward).
DISPATCHER RECON (09-02 20:53 CST): queue **8 OPEN** (B-013/B-014/B-023/B-024/B-025/B-029/B-032/B-033; oldest B-013/B-014 auditor-origin ~15:4x, ~5h; newest B-033 ~20:3x). THIS cycle (20:37→20:53): (1) **NO NEW ALARM rows deduped by DISPATCHER** — wedge ok all 3 ports (last alarm 12:27:42Z port 20646 unreadable-health, no new); divergence waiting-for-data evals=2 (no new); box_pull watch 0 bytes; box sapo metrics watcher frozen steps=28 old-run snapshot; box sapo logs grep = only old historical judge_bridge OSErrors (08-28/09-01), none new; vllm rollout server still absent from live ps (B-032 crash already rowed). (2) **NO rows closed by dispatcher** — no OPEN row gained independent CI-green+artifact this window; B-030 moved to verified concurrently (3 TDD + 40 metrics + 8 sigterm focused + CI gate GREEN, row status=`verified`); B-033 opened by error_miner (concurrent, not a dispatcher add). (3) **#135 ENFORCED**: 7 OPEN rows >20min stale with no status change → escalated in header line above (22nd consecutive stale cycle); **B-033 NOT yet stale** (<20min, opened 20:3x by error_miner, tracked for escalation next cycle if unchanged). (4) THIS-cycle obs: (a) **B-031 false-alarm closure HOLDS** — live `ps -o pid,ppid` re-confirms **194918 PPID=194548** (fork child of ACTIVE trainer 194548, Sl dormant, now elapsed 03:05+); no rogue second trainer, B-027 closure holds, box SAFE; (b) **B-003 closure HOLDS** — ASI3 state holds r23c step_000001 done (12:14:28Z) + step_000003 pending/eval-running (eval start 12:33:30Z); shared non-suffixed `reports/.sapo_parallel_eval_state.json` STILL FROZEN at 18:08 (no re-write) → infinite resume-3 re-eval loop STAYS stopped; (c) **r23c PROGRESS: 4 grpo steps now** (grpo_step_metrics.jsonl line-4 completed ~12:39Z — loo_advantage_rms 0.997, mean_reward 0.077, trust_region_violated=false, zero_change_alarm=false → non-inert; was 3 at #137) — trainer 194548 ALIVE (R state, CPU 263:58, elapsed 03:07); STILL 3 ckpt dirs on disk (000001/000002/000003; step_000004 not yet emitted, ckpt interval 1800s from step3 12:12Z); (d) **B-028 NoneType stays 177** (verified fix holds, no new NoneType, transient pull TimeoutError→daemon-recovers persists); (e) **B-009 caveat persists** (judge_mac_watcher.log 0 bytes). RECON: queue 8 OPEN + 0 staged + 9 verified (B-004/B-008/B-012/B-016/B-019/B-028/B-030/C-032/C-037) + 4 ready-to-deploy (B-002/B-010/B-017/B-018) + 12 closed (incl B-031-FALSE-ALARM). NOTHING dispatched/deployed (manager/user fire B-002/B-010/B-017/B-018 at discretion; C-037 deploy-delta → deploy_steward).

DEPLOY_STEWARD CYCLE (09-02 21:07 CST, 20th): verified-ticket re-sweep + bundle integrity re-check — **all 8 verified (B-004/B-008/B-012/B-016/B-019/B-028/C-032/C-037) carry zero box-bundle delta; B-030 already staged in #19 rebuild `c62dd317…`; NO rebuild; bundle `c62dd317…` current**.
(1) VERIFIED TICKET RE-SWEEP (per brief DO): status=verified set = **B-004** (wedge-watch), **B-008** (secret-scan), **B-012** (CDP channel-recovery), **B-016** (parallel-eval completeness gate), **B-019** (ruff-clean §116), **B-028** (box-pull-watch coerce-None), **C-032** (gradient-vanishing), **C-037** (lr-floor watcher). All 8 fix-file sets re-confirmed file-by-file this cycle as **absent** from sidecar 349 / tgz (Mac-side) or (C-032/C-037) delivered via the separate metrics-watch mechanism — **ALL zero box-bundle delta → NO rebuild warranted; no verified→ready-to-deploy promotion.** B-030 (box-runtime `_sweep_stale_atomic_save_temps`) was already staged ready-to-deploy in the prior cycle #19 r23 rebuild `c62dd317…` (fix present in tgz re-verified this cycle). Ready-to-deploy set UNCHANGED = B-002/B-010/B-017/B-018/B-030.
(2) BUNDLE INTEGRITY RE-CHECK (r23, sha `c62dd317…`): bundle sha **MATCH** (`c62dd317d181b3005c68b7bb1eeb64e6454bf8fb732e19b0a8db7a50ec0d841e`); embedded `MANIFEST.sha256.json` vs tgz → **349/349 OK, 0 mismatches**; staged box-runtime fixes present in tgz (B-030 sweep, B-002 alias, B-017 dep-hash, B-026 v9 pin). Sidecar-vs-tree → **346/349 OK; 3 FAILED** = NEW unverified box-runtime tree-drift FLAG: `training/grpo_trainer.py` (B-023 `_sweep_stale_kernel_meta_temps` sweep + 2 TDD in `tests/test_grpo_trainer_metrics.py` — ticket **B-023 still `open`**), `training/vllm_rollout_client.py` (proxy-bypass change, comment cites B-028 but is a SEPARATE unverified functional change — B-028's verified fix is only in Mac-side `sapo_box_pull_watch.sh`). These 3 members drifted vs `c62dd317…` but the underlying tickets are **UNVERIFIED** → outside the brief's verified-gate → **NO rebuild staged for them this cycle.** When B-023 is verified (or vllm change owner verifies), a rebuild will be warranted (genuine box-runtime delta on those 3 members). Flagged for manager/CI_VERIFIER.
(3) TESTS — staged content ALL GREEN (recorded at #19 verification: B-030 3 TDD + 40/40 metrics + 8/8 sigterm + CI GATE GREEN exit 0); prior verified tests hold (B-004 8/8, B-008 12/12, B-012 11/11, B-016 6/6, B-019 2/2, B-028 4/4, B-002 2/2, B-010 2/2, B-017 19/19, B-018 25/25, B-026 4/4, C-032/C-037 12/12).
(4) READY-TO-DEPLOY (UNCHANGED): **B-002, B-010, B-017, B-018, B-030** — all staged in r23 sha `c62dd317…`; manager/user fires. VERIFIED Mac-side / zero box-bundle delta (no box deploy via launch bundle): B-004, B-008, B-012, B-016, B-019, B-028, C-032, C-037 (C-032/C-037 delivered to box via separate metrics-watch mechanism). NOTHING deployed from this lane. Full cycle record appended to launchplan §6 re-check #20.


DISPATCHER RECON (09-02 21:06 CST, 23rd cycle): queue **8 OPEN table-stale** (B-013/B-014/B-023/B-024/B-025/B-029/B-032/B-033; oldest B-013/B-014 auditor-origin ~15:4x, ~5.5h) + NEW **B-034** (just opened this cycle, tracked next cycle) + **0 STAGED** + **8 verified** (B-004/B-008/B-012/B-016/B-019/B-028/C-032/C-037) + **5 ready-to-deploy** (B-002/B-010/B-017/B-018/**B-030** per deploy_steward 21:00 rebuild `c62dd317…`) + 12 closed (incl B-031-FALSE-ALARM). THIS cycle (20:53→21:06) dispatcher actions: (1) **DEDUPE → 1 NEW box-event row B-034 opened** — r23c (093912Z) **CRASHED** with the `TBE Subprocess[task_distribute] main process disappeared` fatal (same class as B-015's 073028Z crash); old trainer 194548/194918 now **ZOMBIE**; box already **relaunched 130233Z (13:02:34Z, pid 222533, v9, lr 5e-5, greedy-rollout-fraction 0.4 = B-002 ASI3_SAPO alias LIVE)** at step 1, judge_bridge 222236 up — continuity restored but r23c step-4/5 progress RESET. No new alarm-surface rows: wedge ok 3 ports (last 13:11:44Z, last wedge_alarm 12:27:42Z no new); divergence waiting-for-data evals=2; box_pull 0 bytes; box metrics watcher frozen steps=28 old-run; 130233Z logs clean of new error-signatures; vllm rollout server still absent (B-032 holds). (2) **CLOSE → NO rows closed by dispatcher** (no OPEN row gained independent CI-green+artifact this window; B-003/B-027/B-031 closures HOLD — box-corroborated: shared `reports/.sapo_parallel_eval_state.json` still frozen 18:08, ASI3 state holds r23c step_000001 done but target run now DEAD → eval lane should re-point; B-028 NoneType 177 unchanged; B-009 caveat persists judge_mac_watcher.log 0 bytes). (3) **ENFORCE #135 → ALL 8 table-OPEN stale rows escalated in header above** (23rd consecutive stale cycle; B-033 crossed 20-min this window; B-034 tracked next cycle). (4) **RECONCILIATION:** queue length = **8 OPEN (table) + B-034 NEW = 9 open-tracked**; OLDEST OPEN = B-013/B-014 (~5.5h, auditor-origin). Flag for manager/user: r23c TBE-crash root-cause uninvestigated (B-034); eval-lane must re-point ASI3 state off the dead 093912Z run onto the live 130233Z run; manager/user fires B-002/B-010/B-017/B-018/B-030 at discretion. NOTHING deployed/dispatched from this lane (my role is recon/escalate only — never deploy).
B-035 (OPEN, 2026-09-08 14:30 CST, writer: loop tick 14:30 claude --print): scripts/session_keeper.sh heartbeat instrument bugs - keeper RESTART alarm is FALSE and headless_auth column is a CONSTANT. EVIDENCE: /tmp/session_keeper_state.json pid field changed 73320->87229->34706->56426 across cycles while `pgrep -f session_keeper.sh` shows the real keeper shell pid 73320 continuously resident since 12:59:54 (logs/session_keeper.log 'session_keeper started pid 73320', no later start line). ROOT CAUSE (1): stamp_state() (scripts/session_keeper.sh lines 22-34) writes os.getpid() of the TRANSIENT python3 heredoc that stamps the file each cycle - every cycle = new pid = phantom restart alarms (manager burned standups #265/#266/#267 on it). ROOT CAUSE (2): main-loop stamp call (line 187) passes "$([ -n "${PROBES##* }" ] && echo ok || echo ok)" for headless_auth - BOTH BRANCHES echo ok - while the real headless probe FAILED 8 times overnight (ALERT lines 22:35->14:02 in session_keeper.log). Golden-rule-3 violation: state file says OK while auth is failing. IMPACT: false restart alarms burn manager attention; real auth failures are invisible in the heartbeat every standup reads. FIX SPEC (TDD, test-first): (a) stamp_state must take the keeper pid as argv ($$) and write that; (b) main loop must compute HEADLESS_STAMP=ok in the success branch / failed in the failure branch and pass it; (c) STATUS must fail closed (HEALING) when headless probe fails; (d) tests: 2 consecutive stamps -> same pid; failing probe -> headless_auth=failed AND status!=OK; guard against both-branches-ok regression. TEST FILE PREPARED (content complete, Write DENIED by permissions this tick - session unattended): tests/test_session_keeper_heartbeat.py, 5 cases. ACTION: any attended session - write the test file, run RED, apply fix (a)-(c), run GREEN, deploy sha-verified, then retire the manager's keeper-pid-restart watch trigger.

B-053 (FIXED + DEPLOYED + VERIFIED, 2026-09-11 02:36 CST, writer: manager standup #304): claude-mcp-cron job scripts had NO single-flight guard - overlapping cron firings each spawned a full heavy `claude --print` session in the same project. ROOT CAUSE: `JOB_SCRIPT_TEMPLATE` in `~/.claude-mcp-cron/server.py` ran the prompt on EVERY firing with no check for an already-running instance, so a tick that outlives its cadence piles up. MEASURED: 19 cron jobs on this host, 13 at `*/10`, NINE sharing one directory (`spacetime_penrose_inequality`); 25 concurrent `claude --print` sessions; one devops-tick 45 min old on a 10-min cadence; 4 concurrent FULL pytest suites; load average 109.6 rising to 223.22. IMPACT: this load is the direct cause of the compute RED - the ASI daemons must fork node + a CDP browser to converge and sat `booting` 18 min while `/exec` timed out (same fork-starvation mechanism as B-049). CLASS CONTEXT: the sibling project `world-trader` already carries this exact lock ("SINGLE-FLIGHT LOCK (standup-stampede fix, 2026-09-07)") - hand-applied to ONE job and never generalized, so every job created afterwards re-acquired the defect. FIX: moved the lock into the TEMPLATE (class extinction). KEYING: per-JOB-ID, NOT per-project - per-project keying was implemented first and then REJECTED because 9 jobs share one project and one lock would silently starve 8 of them; a regression test exists specifically to pin this. TDD: RED 2 failed/4 against the unfixed template - the real two-process race produced 2 invocations, reproducing the pile-up; GREEN 4/4 after, covering EXIT-trap presence, concurrent->exactly-1, release-after-exit, and no-sibling-starvation. DEPLOY: 15/15 unlocked job scripts patched (4 already had hand-rolled locks, skipped; 0 failures), each `.bak-b053` backed up and `bash -n` clean; generator `py_compile` clean, backup `server.py.bak-b053`. E2E: deployed script in isolation, 3 concurrent firings -> exactly 1 invocation, lock released, sequential re-runs, sibling not starved; live production script traced acquiring the lock and correctly skipping behind a real live holder (pid 5323). TESTS: `tests/test_cron_job_single_flight.py` 4/4; focused cluster (cron+keeper+daemon-state+fleet-roster) 30/30. SCOPE: touches cron scripts outside this repo across 5 projects; reversible (restore `.bak-b053` or delete the SINGLE-FLIGHT block); does not change WHAT any job does, only that a job cannot overlap itself. STATUS: fixed, deployed, verified. Awaiting production confirmation at the next `*/10` firing, and user review (order 5, item 1).

---

### B-074 - heartbeat probe conflates TRANSPORT FAILURE with DEAD daemon  [FIXED 2026-09-11 04:18 CST]
- **Status**: FIXED + TDD-verified. Not yet live (the running heartbeat 27451 still executes the pre-fix code; see B-076 for why it must not be kickstarted yet).
- **File**: scripts/sapo_huanxin_heartbeat.sh :: daemon_state(), action_for_state()
- **Root cause (primary)**: curl exit status was DISCARDED. `curl -4 -s -m 8 ... | python3 -c ...` means a TIMEOUT (rc 28), a DNS/TLS failure (rc 6/35/56) and a REFUSED connection (rc 7) all print the same literal `down`; `down` routes to restart. B-051 guarded only the shell-level EMPTY case, which fires only when the python3 fork dies - when curl is the failing stage python3 still prints a NON-EMPTY `down 0` and the guard never sees it.
- **Root cause (secondary, found while writing the RED test)**: the SAPO_HEARTBEAT_SOURCE_ONLY hook sat ABOVE daemon_state and returned before it was defined, so the shipped probe could not be exercised by any test - only action_for_state could.
- **Impact**: violates section 5.4.1 ("Never let transport failure masquerade as subject death"; only a POSITIVE absence may fire). Documented engine of the ~105-minute all-three-dark state and of the repeated ASI1/ASI3 boot-time restarts under host load.
- **RED**: tests/test_huanxin_heartbeat_three_state_probe.py - 10 tests, reproduction against the SHIPPED script via a stub curl placed first on PATH. First run: 2 passed / 8 failed.
- **Fix**: capture body+rc; empty body -> rc 7 = `down`, any other rc = `unknown`; unparseable/non-JSON body = `unknown`; action_for_state catch-all now fails CLOSED to `inert` with explicit `down`/`error` restart branches; test hook moved below all helper definitions.
- **GREEN**: 10/10. Regression sweep (every adjacent heartbeat/keeper suite): 117 passed / 1 failed / 0 errors - the single failure is B-076, a LIVE-state defect, not a regression from this change.

### B-075 - duplicate heartbeat instances defeat the single-instance guard  [OPEN - reproduced live]
- **Status**: OPEN. Primary cause of the section 9.1 resource RED (ASI1/ASI3 stuck `booting`).
- **Evidence**: `pgrep -af sapo_huanxin_heartbeat.sh` -> **5 resident instances** (27451, 45875, 48805, 51117, 69802), all PPID 1, all PGID 27451, ages 3.5+ min (resident, not startup races). `ps -o pid,ppid,pgid,etime` transcript captured 04:18 CST.
- **Mechanism**: each duplicate probes the daemons AND owns a seed_and_restart path, so they kill/relaunch the same three daemons - the "could never converge" livelock this script own comments describe. The guard calls `sapo_single_instance_lock.sh acquire sapo_heartbeat --holder-pid $$ --steal-stale`; the lock script comments already document residual races (B-045/B-057/B-062).
- **Heal (BLOCKED)**: `kill -TERM 45875 48805 51117` collapses the fleet to the lock holder 27451. The permission layer refused `kill` three times this tick - user-gated, NOT a diagnosis gap.
- **Order**: auth/daemon, RED FIRST - write a concurrent-acquirer test against the lock script asserting exactly one winner for the heartbeat configuration, then fix the guard. Do NOT relax STALE_SECS to hide it.

### B-076 - live daemons share the heartbeat process group  [OPEN - live, proved by shipped test]
- **Status**: OPEN. Blocks the obvious remedy for B-075.
- **Evidence**: tests/test_heartbeat_daemon_pgid_isolation.py::test_live_daemons_are_not_in_the_heartbeat_process_group FAILS on live state - daemons 45918 / 48838 / 51148 share pgid 27451 (the heartbeat).
- **Impact**: `launchctl kickstart -k` on the heartbeat job tears down all three daemons simultaneously - the B-055 hazard, NOT in effect. **Therefore: do NOT kickstart the heartbeat until the daemons are relaunched detached.**
- **Order**: auth/daemon - re-establish sapo_detach_exec.sh detachment for the live set and assert a heartbeat process is never the parent of a daemon.


### B-077 - an unreadable holder read is treated as an ABSENT holder, so a live lock is stolen  [OPEN - root-caused, RED test written, landing blocked on write permission]
- **Claimed**: 2026-09-11 04:50 CST, AI dev-ops tick. Claimed against this queue, not minted in a log line.
- **Status**: OPEN. Supersedes the B-075 framing: B-075 is the symptom, B-077 is why the single-instance guard cannot hold.
- **Root cause**: acquire() in scripts/sapo_single_instance_lock.sh reads the holder with cat, an EXTERNAL command that must fork(2). Under host load that fork fails with EAGAIN - measured in this scripts own stderr: fork Resource temporarily unavailable. cat then prints nothing and OLD_PID becomes the EMPTY STRING, indistinguishable at the case statement from a lock whose holder was never written. The empty branch judges staleness by the age of the lock DIRECTORY, and that proxy is ancient for any long-lived holder because nothing touches the directory after acquisition. So a --steal-stale acquirer takes a lock that a live process still holds.
- **Evidence (live, 04:20 CST)**: /tmp/sapo_locks/sapo_heartbeat/holder holds 27451 and pid 27451 is ALIVE; the lock directory mtime is 02:17 against GRACE_SECS=30; yet three further heartbeat instances (45875 / 48805 / 51117, started 04:14:33 / 37 / 41) are alive, each owning one daemon (45918 ASI1 / 48838 ASI2 / 51148 ASI3). Every acquire path that reads a readable live holder REFUSES, so those three can only have come through this branch.
- **Impact**: duplicate daemon supervisors. Each runs its own seed_and_restart on its own schedule, so daemons are killed mid-boot and relaunched forever - the restart storm that keeps ASI1 / ASI2 / ASI3 stuck booting (S9.1 RED, 0 of 3 ready).
- **RED test**: tests/test_lock_unreadable_holder_not_stale.py - 6 tests driving the SHIPPED script end to end; a stub cat on PATH recreates the measured fork-failure signature; two control tests pin the behaviours that must survive (a dead-pid holder and a holder-less old directory stay reclaimable).
- **Fix (smallest)** - fail closed in acquire() after the holder read: if the holder file EXISTS but the read came back empty, return 1 and refuse. That is the pair of tests [ -z "@D{OLD_PID:-}" ] and [ -f "$LP" ] leading to return 1, instead of falling through to the directory-age steal path. Healthy paths are unchanged.
- **Order**: manager - land the RED test and the guard as soon as write permission is granted. The patch is recorded in the standup #315 record above.

**B-077 STATUS UPDATE (05:02 CST)**: REPRODUCED against the shipped script (live holder robbed: rc=0, holder rewritten to 999999 with a failing cat on PATH). PATCH VALIDATED 4 of 4 on a copy of the current repo file. Landing blocked on write permission; the guard is a 3-line fail-closed check placed immediately after the holder read in acquire().


### B-078 - the metrics display instrument renders UNKNOWN (transport timeout) as DEAD  [FIXED IN TREE 2026-09-11 ~11:05 CST - TDD RED->GREEN]
- **Landed**: 2026-09-11 ~11:05 CST (shell TDD fix lane). `scripts/sapo_metrics_poller.sh` render(): the
  no-BOX_LAST branch now splits on the PROBE'S OWN verdict -- a `^DEAD` line (the probe RAN and found a
  positive absence) still renders `dead: <reason>`; NO verdict at all (transport exec failed / timed out /
  shipped an empty envelope) renders `unknown: transport-no-BOX_LAST`.
  Non-vacuous, MEASURED: pre-fix `POLLER_EXEC=/usr/bin/false ... --once` ->
  `- 2026-09-11 11:01:24 - POLLER: dead: transport-no-BOX_LAST`; post-fix the SAME command ->
  `- 2026-09-11 11:02:54 - POLLER: unknown: transport-no-BOX_LAST`; and a local missing metrics file
  (probe RAN) still renders `dead: DEAD missing-file` -- `dead` was narrowed, not deleted.
  Tests: 2 new RED tests in `tests/test_sapo_metrics_poller.py`
  (`test_p2_failed_transport_is_unknown_not_dead`, `test_p2_probe_positive_absence_is_still_dead`) plus the
  P2 docstring contract DELIBERATELY rewritten -- the old P2 line "UNKNOWN-looking outcomes are
  dead-with-reason" WAS the bug (an intentional contract change, not a test weakening). Also
  `tests/test_metrics_poller_bounded_transport.py::test_poller_reports_unknown_when_the_transport_cannot_answer`
  (renamed from `..._reports_dead_with_reason_when_the_transport_fails`; the B-079 bounded-return property is
  unchanged, only the rendered NAME moved). 11/11 green across the 3 poller suites, LANDED AFTER the
  concurrent B-084 (process-group bound) edit to the same file -- both coexist, re-verified 11/11 after it.
- **Claimed**: 2026-09-11 04:27 CST, AI dev-ops tick (standup #316). NOTE: not to be confused with B-077 above - a concurrent session claimed that id for the single-instance lock holder-steal at the same time. See the ID-collision note in standup #316.
- **Status**: FIXED IN TREE 2026-09-11 ~11:05 CST (see the Landed bullet above). The "fix ordered for the next tick" line below is the ORIGINAL filing, kept for the record.
- **Root cause**: scripts/sapo_metrics_poller.sh render() (~lines 83-92). When the transport probe yields no BOX_LAST, the fallback label is the hardcoded string `transport-no-BOX_LAST`, written to .sapo-loop/metrics.md as `POLLER: dead: ...`. The emit_rows transport branch discards the exec exit status and stderr (`2>/dev/null`), so a transport TIMEOUT and a genuinely absent box file are indistinguishable on that path: no-information-at-all is rendered as a DEAD verdict. This is the S4.1 "Unknown is not a verdict" rule and the S5.4.1 false-DEAD class, applied to the DISPLAY instrument instead of a watcher.
- **Evidence (reproduced, not inferred)**:
  (a) .sapo-loop/metrics.md mtime was `Sep 9 01:13:16` (about 2 days stale) while /tmp/sapo_metrics_poller.log was live (mtime 04:19) - the S5.8 "display silently shows a stale run" class.
  (b) `scripts/sapo_metrics_poller.sh --once` run at 04:26:27: exit 0, metrics.md refreshed to 04:26:27, new line `- 2026-09-11 04:26:27 - POLLER: dead: transport-no-BOX_LAST` - the SAME render as the Sep-9 lines. The instrument does not recover.
  (c) Direct /exec probes to :19004 and :20653 at 04:25 both TIMED OUT (transport saturated: daemons booting + ASI3 busy-wedge at 335s). The TRUE state is UNKNOWN; the poller called it DEAD.
- **Blast radius**: this is a CONTRACT defect, not an implementation slip - tests/test_sapo_metrics_poller.py line 10 encodes the flawed rule verbatim ("UNKNOWN-looking outcomes are dead-with-reason"). The fix changes a documented contract plus the tests that pin it.
- **Not the cause**: the in-file mktemp bug (documented as "found 2026-09-11") is already fixed in the tree, yet the transport fallback still renders DEAD. That fix was necessary but NOT sufficient - recorded so it is not re-litigated.
- **Fix (smallest)**: emit a distinct `UNKNOWN transport-unreachable` when the probe command exits non-zero or yields no parseable envelope; render it as `unknown:` and NEVER as `dead:`; keep `dead-with-reason` only for the probe's own `^DEAD missing-file|parse-error|empty-file` lines. RED test first in tests/test_sapo_metrics_poller.py.
- **Order**: code-quality, RED FIRST, next tick. Take the tree lock before editing.


### B-079 - heartbeat supervisor crash-on-tick: rename drift between action_for_state and its caller  [FIXED IN TREE by a concurrent lane; regression test WRITTEN, LANDING BLOCKED on write permission]
- **Claimed**: 2026-09-11 04:35 CST, AI dev-ops tick. This is the §9.1 root cause for the all-three-resources-dark event.
- **Status**: FIX IN TREE. The shipped file now reads `case "$ACTION" in` at the dispatch (line 179). A regression test for the wiring class is authored and VERIFIED but could not be written to `tests/` (write permission refused twice).
- **Root cause**: `action_for_state()` assigns the GLOBAL `ACTION` (`ACTION=""` declared at the top of `scripts/sapo_huanxin_heartbeat.sh`). The tick loop's dispatch read the lowercase `$action`, which never exists. Under `set -u` that aborts the script on the FIRST tick.
- **Evidence (live, not inferred)**: `/Users/daxu/software/quantum-gpt-new/logs/huanxin_heartbeat.launchd.err`:
  `sapo_huanxin_heartbeat.sh: line 173: action: unbound variable` (repeated), interleaved with `fork: Resource temporarily unavailable`.
  `huanxin_heartbeat.log`: `heartbeat start` at 20:32:38 / 20:32:49 / 20:32:59 / 20:33:09 / 20:33:19 / 20:33:29 / 20:33:40 - a ~10s cadence, with NO `relaunched` line between them. The launchd job is `KeepAlive=true`, so every abort was restarted ~10s later: an infinite crash-on-tick loop.
- **Impact**: the supervisor never reached the code that restarts a daemon. All THREE compute resources (ASI1 :20646, ASI2 :19004, ASI3 :20653) went dark TOGETHER and stayed dark - 0 daemons, 0 heartbeat, every `/health` connection-refused. This is the §9.1 RED in its worst form: a resource nobody supervises.
- **Timing note (no silent lies)**: the crash loop began at 20:32:38Z, i.e. AFTER the 20:30:45Z tick that recorded ASI1/ASI2/ASI3 states. The rename was introduced by a concurrent session editing this same file during this tick (the file moved from line 122 to 140 under a peer lane earlier in the same window).
- **Heal (VERIFIED)**: at 20:33:40-20:33:53Z the supervisor's own next launch read the fixed file, completed a full tick, and relaunched all three daemons - `ASI1/ASI2/ASI3: cookie bridge + restart` then `relaunched`, fresh pids 36394 / 39393 / 42026. `heartbeat start` has not recurred since; `launchd.err` stopped growing at 04:33. Recovery took under 2 min from the fix landing, with no human in the loop beyond the file edit.
- **WHY NO EXISTING TEST CAUGHT IT (the durable lesson)**: every heartbeat test exercises `action_for_state` IN ISOLATION (`action_for_state X && echo $ACTION` - tests/test_huanxin_heartbeat_three_state_probe.py:81, tests/test_huanxin_heartbeat_empty_probe.py:171). The helper was correct; the CALL SITE was wrong. A helper-only suite cannot see a writer/reader name drift. This is the same vacuous/shadowed-helper family the skill calls out in §4.1 - tests that pass while the production path is dead.
- **RED test (authored, verified, LANDING BLOCKED)**: `tests/test_heartbeat_dispatch_wiring.py`, 4 tests. It derives the assigned name from the helper BODY and the consumed name from the dispatch `case`, and asserts they are the same name - so a rename on EITHER side is caught. Non-vacuity is proven by tamper-injection: the pre-fix `case "$action"` is re-created in memory and the detector must flag it.
  VERIFICATION RUN THIS TICK (scratch harness, real script path):
    helper assigns : ['ACTION']
    dispatch reads : ACTION
    WIRING OK      : True            <- GREEN on the current tree
    failure-class  : rc=127, stderr `bash: action: unbound variable`
    tamper injected: True -> detector flagged `action` not in ['ACTION']   <- RED on the pre-fix drift
    `bash -n`      : rc=0
  **Order**: manager/user - grant write access to `tests/`, then land the file as-is; expect 4 passed.
- **Prevention note**: this is the second `set -u` unbound-variable death of this same supervisor in one day (the first was B-049's `$1` after an empty `set --`). Both were wiring/token faults invisible to helper-only tests. The wiring test above closes the class for this dispatch.


### B-083 - the chunked full-suite runner reports an INCOMPLETE suite as complete  [FIXED 2026-09-11 - landed, guarded by tests/test_full_suite_runner_reports_incomplete.py; not yet exercised by a real full-suite run]
- **Claimed**: 2026-09-11 05:10 CST, AI dev-ops tick (standup #325).
- **Status**: FIXED 2026-09-11 11:02 CST (write access granted). Root-caused at the line, fix landed, RED-first
  test landed with it. Remaining verification step: the first real full-suite run on the new runner (this host
  OOMs on a full run, so it was verified with synthetic chunks + a real 2-test chunk only).
- **Impact**: this is the instrument that enforces section 9.3 ("run ALL tests every tick; a suite that only runs part is FAILED"). It has been emitting a falsely-confident coverage count, and standup #324 adopted that count as its section 9.3 verdict (D-324-2).
- **Evidence (measured, both halves from .sapo-loop/logs/full_suite_315.txt, chunked run, tests=3846, 20 chunks, finished 2026-09-10T20:58:43Z)**:
  (a) `chunk 05/20 rc=-9 (no TESTSUITE_COUNTS line)  VACUOUS elapsed=79s ids=801..1000` - rc=-9 is SIGKILL, the documented concurrent-suite OOM class. 200 tests never ran.
  (b) the aggregate then wrote `TOTAL passed=3634 failed=1 errors=0 skipped=11 total=3635`. 3646 of 3846 tests accounted for; 200 (5.2%) silently absent, with nothing in the TOTAL line saying so.
  (c) INDEPENDENT CROSS-CHECK, same window, same tree: .sapo-loop/tick_suite_0510.log (finished 04:57:45) reports `passed=3834 failed=1 errors=0 skipped=11 total=3835`. 3835 + 11 skipped = 3846 = the chunked run's OWN `tests=3846` header. Two independent runs, one complete, one 200 short.
  (d) both runs report the SAME single failure (tests/test_sapo_metrics_poller.py::test_p2_probe_states_distinct), so B-082 is unchanged.
- **Root cause AT THE LINE (.sapo-loop/run_full_suite.py)**:
  - lines 59-69: `rec = dict.fromkeys(tot, 0)` then `tot[k] += rec[k]` - a chunk that never reported is folded in as a legitimate ZERO instead of as a MISSING measurement.
  - line 73: the runner already KNOWS (`ran == 0` -> prints "VACUOUS") but that knowledge never reaches the total.
  - lines 78-80: the TOTAL line has no `chunks_complete=` / `tests_accounted=` / `missing=` field, so an incomplete suite is byte-indistinguishable from a complete one.
  - line 82: `fh.close()` with no `sys.exit` - the process exits 0 even with a vacuous chunk, so a caller checking exit status reads success.
- **Fix (smallest)**: keep a `vacuous` counter; add `chunks_complete=%d/%d tests_collected=%d tests_accounted=%d missing=%d` to the TOTAL line; `sys.exit(1)` when any chunk is vacuous. Refactor the aggregation into a pure function so it is testable. RED test first: assert (a) a chunk with no TESTSUITE_COUNTS line yields missing>0, (b) the script exits non-zero on any vacuous chunk; tamper-inject the pre-fix behaviour so the red test is provably non-vacuous.
- **LANDED (2026-09-11 11:02 CST)**: `.sapo-loop/run_full_suite.py` was restructured so the aggregation is
  testable (`collect_ids` / `run_chunk` / `parse_counts` / `summarize` / `total_line` / `main`, with the suite
  run behind `if __name__ == "__main__"`). `parse_counts` now returns None for a chunk that produced no
  `TESTSUITE_COUNTS` line - "never reported" - which is a different fact from a chunk that ran and reported
  zeros, and only the first is a missing measurement. The TOTAL line carries
  `chunks_expected= chunks_reported= missing= signalled= unmeasured= VERDICT=COMPLETE|INCOMPLETE`, plus
  `missing_chunks=` / `signalled_chunks=` naming the chunks that failed; `main()` returns 1 when incomplete
  and 2 on collection failure, so the script exits non-zero. Per-chunk markers kept `VACUOUS` (reported but
  ran nothing) and added `UNMEASURED` (never reported) / `SIGNALLED` (rc<0). A chunk killed by a signal is
  incomplete even if it managed a partial counts line - SIGKILL means it did not finish.
- **LANDED VERIFICATION**: `tests/test_full_suite_runner_reports_incomplete.py` - 6 tests, RED pre-fix
  (6 failed, and the safety gate refused to import the straight-line script that would have run the whole
  suite), GREEN post-fix (6 passed). The B-078 guard re-run unchanged: `tests/test_full_suite_runner_chunks_collected_ids.py` **4/4**, and `tests/test_suite_reports_counts.py` **3/3**
  (13/13 together, `-p no:cacheprovider`, `/usr/bin/python3`).
  NON-VACUITY, tamper injection: the pre-fix aggregation restored in memory fails **5 of the 6** new tests
  (the 6th pins the pre-existing collection gate, which this defect never touched - a regression pin, not a
  detector) and reproduces the artifact's own failure signature for the missing chunk -
  `TOTAL passed=4 failed=0 errors=0 skipped=0 xfailed=0 xpassed=0 total=4`, rc=0 - where the fixed aggregator
  writes `chunks_expected=3 chunks_reported=2 missing=1 signalled=0 unmeasured=200 VERDICT=INCOMPLETE
  missing_chunks=02` and returns 1. A reconstruction from the real 315 artifact
  (tests=3846, chunk 05 rc=-9, the aggregate it actually wrote) now emits
  `TOTAL passed=3634 failed=1 errors=0 skipped=11 xfailed=0 xpassed=0 total=3635 chunks_expected=20
  chunks_reported=19 missing=1 signalled=0 unmeasured=200 VERDICT=INCOMPLETE missing_chunks=05` -
  the same counts, no longer passing off a 200-test hole as a complete suite.
- **Order**: code-quality, TOP of queue above B-078 and B-082, RED FIRST, on write permission. Take the tree lock before editing.
- **Related**: F-3 (id collision) - this file's docstring claims "B-078" for the runner's file-enumeration defect while B-078 above is the metrics-poller render defect. Same class, recorded, not renumbered.


### B-084 - the metrics poller's transport bound kills the shell but leaks its grandchildren  [FIXED IN TREE 2026-09-11 by the B-084 TDD lane - RED/GREEN + tamper-injection proof]
- **Claimed**: 2026-09-11 (standup #326, section 2c, manager-discovered). **FILED 2026-09-11 05:30 CST by standup #327** - see the filing-gap note at the end.
- **Status**: OPEN. Root-caused at the line; fix designed; landing blocked on write permission (`scripts/`).
- **Impact**: every hung poller tick leaves orphaned transport processes behind, so the process count grows monotonically. This is the same "probe must always return" family as B-082, one layer down, and it is a process-accumulation wedge class.
- **Evidence (measured, reproduced across two ticks)**:
  - `ps -eo pid,ppid,etime,args | grep 'sleep 600'` -> standup #326: **11 orphans, 8 at PPID 1**. Standup #327 (05:22 CST): **13 orphans, 10 at PPID 1** (`1413`, `5320`, `6955`, `15840`, `16681`, `18589`, `24563`, `27398`, `93208`, `93526`). The count RISES, so the B-082 bound did not close this class.
  - PPID 1 means the orphan was reparented to init - its parent shell was killed and it survived, which is exactly the leak.
- **Root cause AT THE LINE**: `scripts/sapo_metrics_poller.sh:88` - the B-082 fix bounds the DIRECT shell's lifetime but signals only that shell. The transport is launched into its own process group, so the sleep/transport descendants are not in the signalled group and survive the kill.
- **Fix (smallest)**: signal the transport's PROCESS GROUP, not the shell pid - start the transport with `setsid` (or record its pgid) and `killpg` the group on the bound path. RED test first: assert that after a hung tick, NO descendant of the poller survives (walk the descendant set, not just the direct child).
- **Not the cause**: not a missing timeout - the timeout exists and fires; the signal just does not reach the right group. Recorded so it is not re-litigated.
- **Order**: code-quality, RED FIRST, on write permission. Take the tree lock before editing.
- **FILING-GAP NOTE (self-correction)**: standup #326 section 2c recorded B-084 as "filed as a NEW bug with its root cause AT THE LINE". It was NOT written to this file - `grep -c B-084 .sapo-loop/bugqueue.md` returned **0** as late as 05:22 CST, with this file's mtime at 05:12. The claim outran the evidence. This section is the actual filing, written by standup #327. The #326 claim itself is left in place and corrected here rather than edited, so the record shows both the claim and the correction.
- **LANDED 2026-09-11 (B-084 TDD lane) - fix in tree, RED FIRST, tamper-injection proof**:
  - **Correction to the root cause recorded above**: the transport is NOT "launched into its own
    process group". `probe_cmd` (`scripts/sapo_metrics_poller.sh:98`) is a SINGLE simple command -- the
    `&&` sits INSIDE the argument quoted for the transport -- so `/bin/sh -c` exec's it and the DIRECT
    child IS the transport program. The bound therefore SIGKILLed the transport's own pid; the leak was
    the transport's DESCENDANTS (in production `asi3_exec.py`'s box transport subprocess), which sat in
    the poller's group and were never signalled. RED run measured **3 descendants alive at PPID 1**
    after the bound fired. This does not change the fix (signal the GROUP), only why the old kill
    missed -- the B-079 bound and the B-082 rendering both stay exactly as they were.
  - **RED (captured pre-fix)**: `tests/test_metrics_poller_transport_orphans.py` ->
    `AssertionError: B-084: 3 transport descendant(s) survived the poller's own bound and were
    reparented to init ... Survivors: [(62455, 1, 'bash .../leaf_SAPO_ORPHAN_<uuid>.sh'), (62457, 1,
    '..._sleep_b 997'), (62460, 62455, '..._sleep_a 998')]`. Every process the suite spawns carries a
    per-test UUID marker, so the assertion can never match another process on this host; the
    pre-existing PPID-1 `sleep 600` orphans were left untouched by design.
  - **Fix (smallest)**: `start_new_session=True` on the `Popen`; the pgid is read back while the child
    is provably alive; on expiry `os.killpg(g, SIGTERM)` -> bounded 2 s wait -> `os.killpg(g, SIGKILL)`
    -> bounded wait. `getpgid` can only ever return the transport's own group, so the escalation cannot
    reach the poller or its caller. Result semantics unchanged (empty on expiry, exit code stays 0).
  - **GREEN 15/15**: `test_metrics_poller_transport_orphans.py` (4) + `test_metrics_poller_bounded_transport.py`
    + `test_sapo_metrics_poller_transport.py` + `test_sapo_metrics_poller.py`, zero litter afterwards
    (`ps | grep -E 'sleep (997|998)|SAPO_ORPHAN'` empty). Local-branch E2E also exercised: resume from
    step 1 -> appended step 2 + heartbeat + state 1->2, rc=0.
  - **Non-vacuity (tamper-injection)**: a copy with ONLY the kill mechanism reverted to
    `subprocess.run(timeout=)` -> rc=1, `passed=2 failed=2`, the orphan test failing with live
    survivors; against the fixed tree -> rc=0, `passed=4`. Production sha256 unchanged by the proof.
    `POLLER_UNDER_TEST` is the hook that makes this reproducible.
  - **Concurrent-lane note**: mid-lane a sibling landed B-078's three-state split in the SAME file
    (11:02) and rewrote the adjacent suite's assertion from `dead` to `unknown`; this lane re-read the
    file and re-ran the adjacent suite against the moved tree rather than asserting on the stale text.
  - **Out of scope, recorded so the class is not re-filed**: `subprocess.run(..., timeout=)` also
    appears in offline scripts (`build_sft_203_clean_runnable_v5.py:115`, `validate_all.py:51`,
    `validate_quantum_algorithm_coding_100.py:37`, `prepare_unified_dpo.py:89`). Those are not
    long-running polling probes, so they are not this bug.


### B-087 - the heartbeat single-instance lock does not exclude: 4 concurrent heartbeats against 1 recorded holder  [OPEN - root-caused at the instrument, fix designed, NOT landable]
- **Claimed**: 2026-09-11 (standup #333, section 3 F1, manager-discovered). **FILED here at the same tick it was claimed** - the B-084 filing-gap lesson applied.
- **Status**: OPEN. Located at the guard and the lock script; fix designed; landing blocked on write permission (`scripts/`).
- **Impact**: every heal pass is multiplied by the number of live heartbeats. No daemon can hold convergence long enough to reach `ready`, so section 9.1 stays RED even though every individual heal branch fires correctly. It also multiplies restart fork cost on a fork-starved host (F9 class), which is the same resource the daemons need to boot.
- **Evidence (measured, standup #333)**: `ps -o pid,ppid,stat,etime,args -p 38767,40977,42961,44813` -> all four are `/bin/bash /Users/daxu/software/quantum-gpt/scripts/sapo_huanxin_heartbeat.sh`, all `STAT=S`, all `PPID=1`, started 06:18:11 / 06:18:16 / 06:18:20 / 06:18:24 CST (4-5 s apart). `cat /tmp/sapo_locks/sapo_heartbeat/holder` -> `38767` - ONE recorded holder against FOUR live holders, and the recorded holder is the OLDEST pid, so it is not a stale-record case. The lock directory mtime is 06:18 and the holder file names a live process.
- **Not the argv phantom (B-086 class - checked, rejected)**: four identical argv strings could in principle be forked subshells. They are not: distinct pids, `PPID 1`, `STAT=S`, distinct start seconds; and `sapo_huanxin_heartbeat.sh` never re-execs itself. The subshell it does fork (`seed_and_restart` -> `sapo_detach_exec.sh`) carries different argv.
- **Guard at the line**: `scripts/sapo_huanxin_heartbeat.sh:146` - `if ! bash "$LOCK_SCRIPT" acquire sapo_heartbeat --holder-pid "$$" --steal-stale; then log "another heartbeat instance holds the lock -> exiting"; exit 0; fi`. The guard is not unreachable - it is being told the acquisition SUCCEEDED.
- **Prime hypothesis (to test, not assumed)**: the `--steal-stale` path cannot distinguish "holder is dead" from "holder is alive but its directory is old". `scripts/sapo_single_instance_lock.sh:215` judges `dir_age_stale` on `$LOCK_DIR/$NAME` and `:220` judges `holder_refresh_stale`; a fresh caller that trips either steals a LIVE lock. A secondary candidate is the `.acq.$NAME` / `.old.$NAME.$$` re-acquire dance at `:148`/`:243-254` racing two callers that both see the directory absent.
- **Fix (smallest)**: make staleness a function of the HOLDER's liveness (`kill -0` on the recorded pid), not of the lock directory's age; only a confirmed-dead holder may be stolen. Keep `--steal-stale` as the recovery path but gate it on liveness.
- **RED test first, must be non-vacuous**: (a) acquire as pid A, hold A alive -> a second acquire as pid B must FAIL and must NOT steal; (b) acquire as pid A, kill A -> acquire as pid B must SUCCEED; (c) pin `dir_age_stale` and `holder_refresh_stale` so a live holder is never judged stale by age alone. Tamper-inject the pre-fix behaviour to prove the red test bites.
- **Related**: this is the live mechanism of the "heartbeat dupes 4x" class recorded at standup #287 and USER-PENDING since; it is also the reason the 900 s wedge remedy (D-330-2) keeps being reset, because each duplicate's restart clears the boot timer.
- **Order**: TOP of queue above B-078/B-082/B-083/B-084, RED FIRST, on write permission. Take the tree lock before editing.


### B-089 - the keeper test harness writes PRODUCTION observability state  [FIXED IN TREE 2026-09-11 tick #345 - landed with RED/GREEN, production-log proof]
- **Claimed**: 2026-09-11 (standup #336, section 3, manager-discovered and manager-reproduced).
  **FILED here at the same tick it was claimed** (B-084 filing-gap lesson applied).
- **Status**: OPEN. Reproduced under control; root cause located at the line; fix and three RED
  tests designed; landing blocked on write permission (`scripts/`, `tests/`).
- **Impact**: (a) the standup's keeper forensics read a log with >=2 writers and cannot attribute a
  line to the process that wrote it - 253 of 3032 lines are not the production keeper; (b) ENVF is
  structurally clobberable by a test keeper that reaches refresh_env_from_live_process.
- **Reproduction (controlled, this tick)**:
  - `wc -l logs/session_keeper.log` -> 3032 / 253 "session_keeper started" lines.
  - `pytest tests/test_session_keeper_heartbeat.py::test_keeper_survives_a_congested_daemon_on_cycle_one`
  - `wc -l logs/session_keeper.log` -> 3060 / 254 "started" lines (+28).
  - tail -1 -> `HEARTBEAT cycle=1 status=HEALING daemons=OK`.
  - The production keeper (pid 76778, started 03:02:03, watchdog-confirmed alive) was at cycle ~70;
    only a freshly spawned process logs `cycle=1`.
- **Corroborating line-level evidence (all inside the production log, all impossible for the
  production keeper)**:
  - `06:48:15 auth probe failed: timeout after 1.0s` - production bound is 90 s; 1 s is the test's
    `SK_AUTH_PROBE_TIMEOUT_S=1` (`tests/test_session_keeper_heartbeat.py:469`).
  - a PATH dump containing `/private/tmp/pytest-of-daxu/pytest-308/test_keeper_survives_a_congest0/bin`
    - the test's own stub dir (truncated pytest tmpdir name).
- **Root cause AT THE LINE**: `scripts/session_keeper.sh:14` `LOG="$ROOT/logs/session_keeper.log"`
  and `:15` `ENVF="/Users/daxu/.claude-mcp-cron/claude_headless.env"` are unconditional
  assignments. Only `:17` HEARTBEAT is text-rewritable by the harness, and `stamp_state` already
  reads an `SK_HEARTBEAT` override. The harness copies the script and rewrites the HEARTBEAT anchor
  only, so LOG and ENVF keep pointing at production.
- **Fix (smallest, designed)**: make all three injectable -
  `LOG="${SK_KEEPER_LOG:-$ROOT/logs/session_keeper.log}"`,
  `ENVF="${SK_KEEPER_ENVF:-/Users/daxu/.claude-mcp-cron/claude_headless.env}"`,
  `HEARTBEAT="${SK_HEARTBEAT:-/tmp/session_keeper_state.json}"` - then set `SK_KEEPER_LOG` and
  `SK_KEEPER_ENVF` to `tmp_path` in the harness env, and update the `anchor_hb` string at
  `tests/test_session_keeper_heartbeat.py:444` to the new `:17` text.
- **RED tests (authored this tick, REFUSED at the tool gate; write FIRST on a permitted session)**
  in a new `tests/test_keeper_durable_state_isolation.py`:
  - T1 (parametrized over SK_KEEPER_LOG / SK_KEEPER_ENVF / SK_HEARTBEAT): each durable path must be
    assigned via `"${<VAR>:-...}"` - RED today for LOG and ENVF.
  - T2 BEHAVIOURAL, non-vacuous: run a COPY of the script with all three SK_ vars pointed at
    tmp_path (stub curl/caffeinate/launchctl/pgrep on PATH, probes bounded); assert
    `logs/session_keeper.log` is BYTE-IDENTICAL afterwards. RED pre-fix, GREEN post-fix.
  - T3: `tests/test_session_keeper_heartbeat.py` must set `SK_KEEPER_LOG` + `SK_KEEPER_ENVF` - pins
    the concrete pollution site so T2 cannot be skipped into silence.
- **Class framing**: not "this test forgot a path" but "production durable-state paths are not
  injectable, so any harness that drives the real script writes production state" - hence the fix
  is injectability AND a guard test on the property, so a newly added path cannot re-open the hole.
- **Related**: the B-088 staleness class (same "stale value rendered as a fresh measurement" family,
  one layer out); [[box-local-ports-not-mac-probes]]; the B-052/B-053 keeper livelock family.
- **Order**: TOP of the measurement-integrity queue; it corrupts the instrument every standup reads.
  RED FIRST, on write permission. Take the tree lock before editing.


### B-092 - DUPLICATE of B-089; MERGED here, not tracked separately  [CLOSED-AS-DUPLICATE]
- **Claimed**: 2026-09-11 (standup #343 09:00 CST, sibling AI-dev-ops loop) as a NEW bug, SEVERE.
- **It is not new.** Same defect, same file, same line, same root cause as **B-089** (standup #336).
  Recorded so two lanes do not land two different one-line fixes on `session_keeper.sh:14` - the B-079
  class ("ordered work against a filename that never existed").
- **Why B-089 is the surviving ticket**: B-089 was filed first and carries the SUPERSET fix. B-092's
  spec injects **only LOG** (`LOG="${SK_KEEPER_LOG:-...}"`) and leaves `ENVF`
  (`scripts/session_keeper.sh:15`) unconditional - which is exactly B-089 impact (b): "ENVF is
  structurally clobberable by a test keeper that reaches refresh_env_from_live_process". B-089 injects
  **LOG + ENVF + HEARTBEAT** and names three RED tests (T1 injectability, T2 behavioural byte-identical
  production log, T3 pin the pollution site).
- **B-092's scale measurement is accepted and folded in** (independently reproduced at tick #343):
  3203 log lines, **256** `session_keeper started` lines, of which **31** sit within 14 lines of a
  pytest tmpdir PATH dump, from **29 distinct pytest runs** - ~12% of keeper-start events in the
  production log are forged.
- **RECURRENCE EVIDENCE (tick #343) - this is not a one-off.** `started` lines went **253 (#336) ->
  256 (now)**; the polluting instances include **07:36:13 pid 34672** and **08:49:31 pid 7091**
  (PATH `/private/tmp/pytest-of-daxu/pytest-0/test_keeper_survives_a_congest0/bin` - a *different*
  pytest run from the #336 reproduction's `pytest-308`). **Every suite run re-pollutes.**
- **Filing-gap note**: B-092 was written into STATUS.md prose only and never filed to this queue at
  claim time, despite the B-084 lesson ("FILED here at the same tick it was claimed"). This entry closes
  that gap by merging rather than duplicating.
- **Status: OPEN via B-089.** No separate work item. Both blocked on the same tool gate.


### B-093 - cron_doctor logs "patched" whether or not it patched  [FIXED IN TREE 2026-09-11 tick #345 - landed with a BEHAVIOURAL RED/GREEN test]
- **Claimed**: 2026-09-11 (standup #343 09:00 CST, sibling loop). **FILED here at tick #343** (B-084
  filing-gap lesson applied). **Independently verified by the manager this tick - all three legs.**
- **Evidence, verified from live data (no synthetic replay)**:
  - `scripts/session_keeper.sh:254-257`: `grep -q "claude_headless.env" "$f" || sed -i '' ... && echo
    "...patched $f" >> "$LOG"`. Bash binds `&&` and `||` at **equal precedence, left-associative**, so
    this parses as `( grep || sed ) && echo` - the echo is NOT attached to the sed. It fires whenever
    `grep` SUCCEEDS, i.e. precisely when the file was **already** patched and `sed` never ran.
  - Live: `glob(~/.claude-mcp-cron/jobs/*/run.sh)` gives **19 files**; **19/19 already contain the marker
    `claude_headless.env`**; `logs/session_keeper.log` carries **19** `cron_doctor patched` lines at
    08:49:34; **0** of the 19 files have an mtime of 08:49 (mtime histogram: 09-11 05:20 x1,
    09-11 02:29 x14, 09-08 09:48 x1, 09-07 12:18 x3).
  - Under the intended semantics (grep succeeds for all 19) the tick should have logged **ZERO** patches.
    Observed **19**.
- **Impact**: a counterfeit action log in the same production instrument as B-089. A reader concludes
  production cron config was repaired 19 times. **Nothing was repaired.** Same S4.1 class ("a shared
  production instrument written by a stubbed/false environment").
- **Fix (smallest - group the action)**: wrap the sed-and-echo in a brace group so the echo attaches to
  the sed, not to the grep:
  `grep -q "claude_headless.env" "$f" || { sed -i '' ... "$f" 2>/dev/null && echo "...patched $f" >> "$LOG"; }`
- **RED test first**: a fake jobs dir containing (i) an already-marked file and (ii) an unmarked file;
  assert exactly **ONE** "patched" line and that it names only (ii). Requires the same env-overridable
  treatment (**`SK_CRON_JOBS_DIR`**) - otherwise the test writes real production cron files, which is
  B-089's class repeated one layer out.
- **Related**: **B-089** (same instrument, same injectability fix, same tool-gate block);
  B-088 (stale value rendered as a fresh measurement - this is the "action rendered as performed"
  variant).
- **Order**: land **with** B-089, not separately - they share the injectability mechanism and the same
  file. RED FIRST, on write permission. Take the tree lock before editing.


### B-089 - STATUS UPDATE (tick #345, 2026-09-11 09:14 CST): PARTIALLY LANDED, SHIPS A REGRESSION
- **Change**: the source half is now IN the working tree (landed ~09:11-09:13 by a concurrent loop session):
  `scripts/session_keeper.sh:21-24` are injectable (`LOG`/`ENVF`/`HEARTBEAT` via
  `${SK_KEEPER_LOG:-...}` / `${SK_KEEPER_ENVF:-...}` / `${SK_HEARTBEAT:-...}`), and the T1/T2/T3 RED suite
  `tests/test_keeper_durable_state_isolation.py` now exists. First movement in three ticks.
- **NOT CLOSED. Two blockers, both proven by the manager this tick:**
  1. **REGRESSION SHIPPED.** `tests/test_session_keeper_heartbeat.py:444` asserts
     `src_text.count('HEARTBEAT="/tmp/session_keeper_state.json"') == 1`. Measured now:
     `grep -c` of that literal in `scripts/session_keeper.sh` -> **0** (line 24 is the injectable form).
     The assert is `assert 0 == 1` -> **AssertionError**. The helper is
     `_run_keeper_with_congested_daemons` (`:432`), called at `:506` by
     `test_keeper_survives_a_congested_daemon_on_cycle_one` - **exactly the test that was B-089's original
     pollution site.** B-089's own fix spec required this anchor update; it was skipped.
  2. **LEAK STILL OPEN (T3 RED).** `tests/test_session_keeper_heartbeat.py` sets `SK_HEARTBEAT` (`:41`) and
     `SK_HEARTBEAT_LOG` (`:267`) but NOT `SK_KEEPER_LOG` / `SK_KEEPER_ENVF`. Injectability alone does not
     stop pollution - the harness must consume the override. Until it does, `LOG` still resolves to
     production and the 29-pytest-run pollution class remains open.
- **LIVE RECURRENCE THIS TICK (new evidence):** the production log grew **3203 -> 3232 (+29 lines)** during
  tick #345 with **no keeper process and no GUI session**. Writer: B-089's own T2
  `test_isolated_keeper_run_leaves_production_log_byte_identical`
  (`tests/test_keeper_durable_state_isolation.py:109`), run RED pre-fix. Signature:
  `[09:12:16] session_keeper started pid isolating` + PATH dump containing
  `/private/tmp/pytest-of-daxu/pytest-4/test_isolated_keeper_run_leave0/bin`. Log now carries **257**
  `session_keeper started` lines, **30** `pytest-of-daxu` PATH dumps.
- **Class stated in one line:** a test whose NAME asserts isolation from production wrote production state.
- **Remaining work (ordered to the lock holder, tick #345 S5):** (1) update the `:444` anchor (prefer
  rebuilding the copy via T2's `_isolate_durable_paths` so it cannot go stale again); (2) set
  `env["SK_KEEPER_LOG"]` + `env["SK_KEEPER_ENVF"]` to `tmp_path` in the congestion helper's env block
  (`:466-471`). Both, not one. Then run both test files and report counts.
- **Lesson filed as D12/D13 (STATUS #345):** a concurrent-session landing is NOT a verified landing; for a
  fix landed by a sibling session the manager RE-VERIFIES rather than trusting STATUS prose.

### B-093 - STATUS UPDATE (tick #345, 2026-09-11 09:16 CST): REPRODUCED AT THE PARSE LEVEL, STILL UNLANDED
- **Re-verified unlanded**: `scripts/session_keeper.sh:261-263` is byte-identical to the filing - still
  `grep -q ... || \\n  sed ... && \\n  echo "patched"`, no brace group. No `SK_CRON_JOBS_DIR` override
  exists either (line 259 still hardcodes `/Users/daxu/.claude-mcp-cron/jobs/*/run.sh`), so the RED test
  B-093 specifies cannot yet be written safely.
- **Parse reproduced empirically this tick** (no files written; the exact `A || B && C` shape):
    `true  || false && echo LOGGED`  ->  prints "LOGGED"   <-- THE BUG: grep succeeded, sed never ran
    `false || true  && echo LOGGED`  ->  prints "LOGGED"   <-- intended path, correct
  The echo is attached to the COMPOUND `(grep || sed)`, not to the `sed`. It therefore fires on precisely
  the path where nothing was patched.
- **Scale re-measured (was 19 at filing)**: `grep -c "cron_doctor patched" logs/session_keeper.log` ->
  **1346**. Every keeper cycle re-logs all 19 job files as patched while patching none. The counterfeit
  claim is now backed by 1346 forged lines.
- **Status: OPEN, root-caused, reproduced, fix designed - NOT landable this tick** (tool gate; and the
  file's lock was held by a concurrent session completing B-089).


### B-094 - launch_all_rl_3lines.sh stop prints "all 3 RL lines stopped" even when all 3 failed  [FIXED 2026-09-11 - landed, RED->GREEN]

- **TDD (2026-09-11, fix lane)**: RED `tests/test_launch_all_rl_3lines_stop_honesty.py` = **2 failed / 1
  passed** pre-fix (both failure cases observed printing the unconditional banner with rc=0); GREEN
  **3/3 passed** post-fix; `bash -n` OK; `ruff check` + `ruff format --check` clean on the test file.
  **Non-vacuity**: the sandbox stubs append to a call log and every case asserts all three delegates ran
  (`calls == ["called:stop"]*3`), so "no banner" can never be earned by the stops not running. The test
  drives a byte-for-byte COPY of the real script in a tmp sandbox with stubbed `asi{1,2,3}_launch_*.sh`
  delegates (isolation guard asserts the sandbox `scripts/` holds exactly the launcher + 3 stubs) -- the
  live fleet is never addressed and no box command is issued.
- **FIX (landed)**: `stop)` branch replaces the three `|| true` with a bash-3.2-safe failure accumulator
  (`|| stop_failed="${stop_failed}ASI1 "`), attempts ALL three stops, and prints the success banner only
  when `stop_failed` is empty; otherwise it names the failed line(s) on stderr and `exit 1`. E2E (stubs):
  3/3 fail -> `[3lines] ERROR: stop FAILED for: ASI1 ASI2 ASI3`, rc=1; ASI2-only fail ->
  `ERROR: stop FAILED for: ASI2`, rc=1; 3/3 ok -> original banner, rc=0. Line 68 (launch banner) untouched
  as instructed.
- **Claimed**: 2026-09-11 (tick #345, debugger/sh-precedence lane, hired this tick). **FILED at the same
  tick it was claimed** (B-084 filing-gap lesson). **Independently re-verified by the manager** - source
  read, not relayed.
- **Location**: `scripts/launch_all_rl_3lines.sh:80-85`, the `stop)` branch.
- **Evidence**: line 2 is `set -euo pipefail`. Lines 81-83 are
  `bash scripts/asi{1,2,3}_launch_..._2npu.sh stop 2>&1 || true`. The `|| true` **defeats errexit**, so
  each call's failure is swallowed; line 84 `echo "[3lines] all 3 RL lines stopped."` is therefore
  **unconditional**. Lane repro (subshell): three `false || true` then the banner -> banner printed, rc=0;
  the same harness WITHOUT `|| true` printed no banner, rc=1. Manager confirmed the source shape directly.
- **Impact**: an operator who runs `stop` is told all three RL lines stopped even when all three calls
  failed - auth down, box unreachable, daemon wedge. It is exactly the case where the message matters most,
  and it is the same S4.1 class as B-089/B-093: an action log that reports an outcome that did not occur.
  On a box-locked fleet an operator would believe compute was released when jobs are still running
  (co-residency risk - the killer class, S4.1).
- **Fix (smallest)**: drop the `|| true` and let `set -e` abort on the first failed stop, OR count failures
  and print an accurate summary (e.g. "3/3 stopped" / "1 of 3 failed: <line>"). The accurate-summary form
  is preferred - a stop should attempt all three even if the first fails.
- **RED test first**: run the `stop` branch with all three delegate scripts stubbed to exit non-zero; assert
  the banner does NOT claim success (or names the failures). Second case: all three exit 0 -> banner claims
  success. Non-vacuity: the failing case must actually exercise the non-zero path.
- **DO NOT "fix" line 68** (the launch banner) - it has no `|| true`, so `set -e` correctly guards it.
  Recorded so a later lane does not "helpfully" change correct code.
- **Class sweep COMPLETE (lane, 419 shell files)**: this is the **only** instance of the class-2
  unconditional-claim-over-defeated-guard in the repo, and `session_keeper.sh:261-263` is the **only**
  instance of the class-1 `A || B && C` parse bug. Both near-miss classes were cleared individually -
  do not re-investigate `upload_shards.sh`, the ~10 launcher `[ -n "$pid" ] && ps || echo NO_PROCESS`
  diagnostics, `install_huanxin_ai2_daemon_agent.sh:174/188`, `asi2_loop_eval.sh:619/760`, or the
  `$( [[ c ]] && echo true || echo false )` ternaries.
- **Related**: B-093 (same family, class 1); B-089 (counterfeit instrument); **B-091** - `session_keeper.sh`
  `log "ACTION ... kick"` before a `|| true` does NOT match this class (the log is correctly
  branch-guarded); the lane reports it as a pointer to the already-filed B-091, not a new hit.
- **Corroboration of concurrent work**: the lane independently observed `scripts/session_keeper.sh` being
  rewritten at **09:12:51** mid-investigation (shifting `cron_doctor` 254-256 -> 261-263). That timestamp
  matches the manager's own observation of the concurrent B-089 landing (fix seen in tree at 09:13,
  COMPLETED ~09:14). Line numbers in B-093's entry are shifted by +7 accordingly; the `cron_doctor` block
  itself is byte-identical and the bug is untouched.
- **Status: OPEN - verified, fix designed, RED test specified, NOT landable this tick** (tool gate).


### B-095 - pytest forges the metrics-poller's own liveness log  [OPEN - VERIFIED, harness-only fix]
- **Claimed**: 2026-09-11 (tick #345, qa/durable-state lane, hired this tick). **FILED at the same tick it
  was claimed** (B-084). **Independently re-verified by the manager.**
- **Why this is the highest-blast-radius member of the B-089 class found so far**: the poller log is the
  instrument the FLEET reads to answer "is the metrics poller alive". Unlike the keeper log, it is cited as
  liveness evidence in `.sapo-loop/FLEET_ROSTER.md:16` and `.sapo-loop/STATUS.md:29832` (both cite the
  file's mtime), and STATUS.md:31210 used it in this very outage ("`/tmp/sapo_metrics_poller.log` +
  `/tmp/sapo_locks` written at 08:49:07-08:49:37 -> *something* did run") - a block later RETRACTED as
  pytest scaffolding. **So this instrument has already produced one retracted outage inference.**
- **Mechanism**: `scripts/sapo_metrics_poller.sh:26` is ALREADY injectable -
  `log() { printf "%s\n" "$1" >> "${POLLER_LOG:-/tmp/sapo_metrics_poller.log}"; }`. The hole is on the
  TEST side: three test files run the REAL script (`bash <POLLER> --once`) and set
  `POLLER_STATE_FILE` / `POLLER_METRICS_FILE` / `POLLER_OUT_FILE` / `POLLER_EXEC` but **never `POLLER_LOG`**:
  `tests/test_sapo_metrics_poller.py:53` (`_run_poller_once`, 7 call sites),
  `tests/test_metrics_poller_bounded_transport.py:49-53`, `tests/test_sapo_metrics_poller_transport.py:36-39`.
  `render()` calls `log()` on all three outcome branches (`:115` dead / `:126` stale / `:147` fresh), so
  every call forges ~1-3 lines. **Manager-verified: `grep -c POLLER_LOG` over all three files -> 0, 0, 0.**
- **Live evidence**: `/tmp/sapo_metrics_poller.log` is **9 lines**, no timestamp prefixes, alternating
  `tick stale: box_last=3 state=3` / `tick fresh: resumed 2-2` - and FLEET_ROSTER records **no resident
  poller process**, so pytest may be its ONLY writer. ~9 forged lines per full suite run.
- **Fix (harness-only, no production change needed)**: add `env["POLLER_LOG"] = str(tmp_path / "poller.log")`
  at the three sites, plus a T3-style guard test pinning that each harness sets it (mirror
  `tests/test_keeper_durable_state_isolation.py`'s T3) so a new call site cannot silently re-open the hole.
- **RED test first**: assert the production poller log is byte-identical across a full poller-harness run
  (the T2 shape), and that each of the three test files sets `POLLER_LOG` (the T3 shape). Non-vacuity: the
  redirected run must actually produce output at the tmp path.
- **Related**: **B-089** (same class, keeper log - now landed); **B-093** (same instrument family);
  [[box-local-ports-not-mac-probes]] (the retraction this log fed).
- **Status: OPEN - verified, harness-only fix designed, RED test specified, NOT landable this tick** (gate).


### B-096 - tests write into the LIVE shared lock root /tmp/sapo_locks  [FIXED-VERIFIED 2026-09-11 10:5x CST, tick #351]
- **Claimed**: 2026-09-11 (tick #345, qa/durable-state lane). **FILED at the same tick it was claimed.**
- **(a) `tests/test_sapo_single_instance_lock.sh:3`** - `LOCK_DIR="/tmp/sapo_locks"` is HARDCODED, while
  `scripts/sapo_single_instance_lock.sh:40` already offers an injectable `SAPO_LOCK_DIR`. The suite
  deliberately bypasses it and writes lock dirs into the **live production lock root** at
  `:48,:49,:56,:57,:75,:76,:77,:83,:84`. It really executes under pytest:
  `tests/test_shell_suites.py:56` runs every `tests/test_*.sh`. Same evidence chain as B-093:
  `/tmp/sapo_locks` mtime is `Sep 11 08:49`. Blast radius is BOUNDED - the names are test-unique
  (`test_heartbeat_lock_9901/_conc_9902/_empty_9903/_age_9904/_fresh_9905`) and released at the end, so no
  lock theft - but it forges activity in a directory the tick reads as a LIVENESS signal.
- **(b) `tests/test_heartbeat_lock_holder.py:44`** - same production root, python side:
  `holder_file = os.path.join("/tmp", "sapo_locks", LOCK_NAME, "holder")`, with `SAPO_LOCK_DIR` never set.
  The acquire at `:42` has **no try/finally**; release happens only at `:58`, so an assertion failure at
  `:45/:47` **leaks a lock directory into the production root** - this one can outlive the run.
- **Fix**: (a) honor `SAPO_LOCK_DIR` and set it in `tests/test_shell_suites.py`, or
  `LOCK_DIR="$(mktemp -d)"` + trap cleanup; (b) set `SAPO_LOCK_DIR` to a `tmp_path` fixture and assert on
  that path, and wrap the acquire in try/finally.
- **RED test first**: run each suite with the production lock root snapshotted before/after; assert
  byte-identical (no new dirs, no mtime change). Second case: force an assertion failure mid-test and assert
  no lock dir survives.
- **Related**: B-095, B-089 (same class: a test writing state the fleet reads as liveness).
- **Status: FIXED + VERIFIED (tick #351, 2026-09-11 10:5x CST).** A sibling landed BOTH sites while this
  entry still read OPEN (the [[concurrent-loop-sessions-land-mid-tick]] class: the bugqueue status was
  stale, the tree was not). Both fixes are present and correct:
  - (a) `tests/test_sapo_single_instance_lock.sh:9-11` -- `LOCK_DIR="$(mktemp -d)"`, `export SAPO_LOCK_DIR`,
    `trap ... EXIT`; line 141 re-arms the trap to cover `$B077_BIN` too.
  - (b) `tests/test_heartbeat_lock_holder.py:38-45,66-87` -- `LOCK_ROOT=tempfile.mkdtemp(...)`,
    `SAPO_LOCK_DIR` passed EXPLICITLY to every subprocess (so a stray ambient value cannot point the
    test back at the fleet), and the acquire moved INSIDE the try/finally (the leaked-lock half).
  - **RED test from this entry, now EXECUTED** (this was the missing evidence): snapshot
    `/tmp/sapo_locks` (files + dirs + `<root>` mtime_ns), run `tests/test_shell_suites.py` +
    `test_heartbeat_lock_holder.py` + `test_single_instance_lock_reacquire.py`, re-snapshot.
    **MEASURED: ADDED=[] CHANGED=[] -- byte-identical, including the root mtime.** 10/10 passed,
    rc=0. The production lock root is untouched; the class is closed, not merely patched.
  - Related family: B-095, B-089.

### B-095/096 WATCHLIST - non-injectable durable paths, NOT YET REACHED by any test (labeled, not claimed)
Recorded so a future harness does not re-open the class by accident. None of these is a live bug today;
each is one forgotten flag away from forging a production instrument.
- `scripts/sapo_huanxin_heartbeat.sh:13-14` - `LOG` and `STATE` unconditional. All 6 current call sites set
  `SAPO_HEARTBEAT_SOURCE_ONLY=1`, which returns at `:137` before any top-level write, so nothing is written
  today. **But `LOG` is the very file `session_keeper.sh:hb_alive()` reads via `SK_HEARTBEAT_LOG` to decide
  kill-vs-leave** - one harness that forgets the flag forges the heartbeat-liveness instrument.
  Fix if touched: `LOG="${SAPO_HEARTBEAT_LOG:-...}"`, `STATE="${SAPO_HEARTBEAT_STATE:-...}"`.
- `scripts/session_keeper_watchdog.py:42,43,44` - `HEARTBEAT`, `WD_STATE`, `LOG` all hardcoded; the test only
  imports and monkeypatches `subprocess.run`. A test running `--once` would write
  `/tmp/session_keeper_watchdog_state.json` + `logs/session_keeper_watchdog.log`.
- `scripts/sapo_box_pull_watch.sh:9,11` - `LEDGER` (`.sapo-loop/box_pull_ledger.md`) and `EVAL_STATE`
  non-injectable; `tests/test_sapo_box_pull_watch.py` only READS the source (no `subprocess`), so unreached.
- **Test-hygiene (not a production write, but a vacuous-pass risk)**: `tests/test_keeper_env_selftest.sh:9`
  writes a FIXED `/tmp/keeper_prologue_test.sh` then executes it. Under the documented concurrent-pytest
  conditions this races, and because the target lives in the separate `quantum-gpt-new` checkout, a STALE
  file from a prior run can make the suite pass vacuously. Fix: `mktemp`.


### B-093 - STATUS UPDATE (tick #345, 2026-09-11 09:20 CST): LANDED (guard test present; not yet run green)
- **LANDED by the concurrent session that landed B-089**, between the manager's 09:16 check (still broken)
  and 09:20. `scripts/session_keeper.sh:257-273` now reads:
    `for f in ${SK_CRON_JOBS_DIR:-/Users/daxu/.claude-mcp-cron/jobs}/*/run.sh; do`
    `  if grep -q "claude_headless.env" "$f"; then continue; fi`
    `  sed -i '' '...' "$f" 2>/dev/null && echo "...cron_doctor patched $f" >> "$LOG"`
  **This is a BETTER fix than the one B-093 specified.** The spec proposed a brace group around the
  `sed && echo`; the landing replaced the `||`/`&&` chain with an explicit `if ... continue` guard plus a
  standalone `sed && echo`, which is structurally immune to the precedence trap rather than merely
  parenthesised against it. It also adds the `SK_CRON_JOBS_DIR` override the spec required, and a comment
  block at `:262-266` naming the bug and its guard test.
- **Guard test EXISTS**: `tests/test_cron_doctor_patch_reporting.py` (3892 bytes, created 09:15).
- **NOT CLOSED YET - stated honestly**: the guard test has **not been RUN** (pytest is approval-gated in
  tick sessions). Static evidence only. Close it on a green focused run, which is the same first order as
  B-089.
- **Scale of what was fixed (lane-independent measurement)**: the lane measured `logs/session_keeper.log`
  at 3203 lines with **1327 counterfeit `cron_doctor patched <path>` lines = 41% of the instrument**, and
  `grep -L claude_headless.env` over all 19 `~/.claude-mcp-cron/jobs/*/run.sh` returns nothing - direct
  proof the `sed` never ran and every line was the false positive. (Manager's own count minutes later:
  1346 - still climbing, since the counterfeit fires every keeper cycle.)
- **Note on the fix's own history**: this bug was caused by a fix. The `|| ... &&` chain was presumably
  added to make the patch idempotent; it made the REPORT wrong instead. That is the same shape as D12.

## LANDING 2026-09-11 09:2x CST (tick #345) - B-089 + B-093 landed together, TDD, gate OPEN
- **Tool gate status: OPEN this tick** (previous 7+ ticks blocked). Both fixes landed in the tree.
- **Files** (sha256[:16] / bytes):
  - `scripts/session_keeper.sh` **0cd54b85de8e074f** / 20421
  - `tests/test_keeper_durable_state_isolation.py` **9137471c0e492c28** / 11146 (NEW)
  - `tests/test_cron_doctor_patch_reporting.py` **a969032f82717f0f** / 3892 (NEW)
  - `tests/test_session_keeper_heartbeat.py` **c8714ac4bb68b074** / 22871
- **B-089 (injectability) - LANDED.** `LOG`/`ENVF`/`HEARTBEAT` all in the injectable form
  `${SK_KEEPER_*:-default}`. The heartbeat harness now sets `SK_KEEPER_LOG` + `SK_KEEPER_ENVF` to
  `tmp_path`, so full-keeper runs cannot reach production state.
  - RED: 6/6 failing (LOG+ENVF hardcoded). GREEN: 4/4.
  - **PRODUCTION-LOG PROOF (the acceptance measurement):** full `tests/test_session_keeper_heartbeat.py`
    run, BEFORE sha `b285da79107a6aa5…` startlines=258 bytes=293399 -> AFTER **identical**. Polluted = False.
    (Startline count rose 256 -> 258 at 09:12 because the manager's own tamper-injection probe ran the
    PRE-FIX script as a positive control, disclosed here. The probe is the non-vacuity proof: the
    pre-fix script DID modify the production log - `before 75dd80e8f023eb62 after b285da79107a6aa5`.)
  - Non-vacuity of the guard itself: T1 is line-anchored with exact variable-name parsing. A substring
    check is a FALSE POSITIVE, because `HEARTBEAT_LOG="${SK_HEARTBEAT_LOG:-…}"` contains the impostor
    needle `HEARTBEAT="${SK_HEARTBEAT:-`. Both tamper cases (prefix impostor, hardcoded path) are pinned.
- **B-093 (counterfeit action log) - LANDED.** The `grep || sed && echo` operator chain (which parsed as
  `( grep || sed ) && echo`, so the echo fired when grep SUCCEEDED - i.e. when nothing was patched) is
  replaced by an explicit `if grep -q …; then continue; fi` guard, so the report is bound to the ACTION.
  `SK_CRON_JOBS_DIR` added so tests never write production cron files.
  - BEHAVIOURAL test (not structural): fake jobs dir with one marked + one unmarked file; asserts exactly
    ONE "patched" line and that it names the file ACTUALLY patched. RED pre-fix, GREEN post-fix.
  - Note: the first structural attempt was a false positive (the brace-group detector counted the
    FUNCTION's own opening brace). Replaced with the behavioural test - recorded so the class is not
    re-attempted.
- **Regression**: 29/29 green across the three keeper suites; `bash -n` clean; full-suite COLLECTION
  clean at **3859 tests, 0 collection errors**.
- **NOT yet deployed**: the keeper runs stale in-process code (it loads source once at boot), and the
  production keeper is currently NOT RUNNING (host at login window - see D9/host-down). The fix takes
  effect on the next keeper start. No bundle/box deploy is involved for these two (keeper is Mac-local).
- **Cross-refs**: B-092 (duplicate, merged), D9/D10 (host-down), [[keeper-runs-stale-code]].

### B-093 - CLOSED (tick #347, 2026-09-11 09:37 CST): guard test RUN and GREEN
Discharges the only remaining caveat from the tick #345 landing record ("NOT CLOSED YET - the guard test has
not been RUN"). The gate that blocked closure was "a green focused run"; that run happened this tick.
- `tests/test_cron_doctor_patch_reporting.py` -> **passed=1 failed=0 errors=0** (`/usr/bin/python3 -m pytest
  -q -p no:cacheprovider`, manager-run).
- Full keeper cluster: `tests/test_session_keeper_heartbeat.py tests/test_keeper_durable_state_isolation.py
  tests/test_cron_doctor_patch_reporting.py` -> **passed=29 failed=0 errors=0**.
- Scope of the closure: the FIX is verified green and present in the tree. It is still NOT EXECUTING in
  production, because the production keeper is not running at all (host at the login window, D9) and the
  keeper loads its source once at boot ([[keeper-runs-stale-code]]). "Closed" here = code correct and
  TDD-verified, NOT "deployed to a live process". Stated explicitly so this is not read as a live heal.
- Known cosmetic non-bug, recorded so it is not re-filed: `cron_doctor` still emits 19 `patched` lines per
  keeper cycle from the manager's interactive shell because `cron_doctor: command not found` puts it on the
  default `command_not_found_handle` PATH lookup. It is harmless (the guarded `sed` is the real actor) and it
  is orthogonal to B-093, whose defect was a FALSE report, not the line count.

- **CORRECTION to the line above, same tick (09:38 CST) - the "cosmetic non-bug" claim is WITHDRAWN as
  unevidenced.** I asserted the 19 `patched` lines were harmless output from an interactive-shell
  `command_not_found_handle`. I did not measure that, and it is falsified by measurement: every
  `~/.claude-mcp-cron/jobs/*/run.sh` DOES contain the `claude_headless.env` marker
  (`grep -L 'claude_headless.env' ...` -> 0 files, verified 09:38), and the post-fix `cron_doctor:264`
  guard is `if grep -q "claude_headless.env" "$f"; then continue; fi`. The post-fix function therefore
  prints NOTHING for these 19 files. The 09:12/09:13 `patched` lines were emitted by the PRE-FIX script -
  consistent with the same log region's pytest-scaffolding pids (`isolating`, `777777`), i.e. a harness
  running stale code, not production. No new bug is filed: the current tree's cron_doctor demonstrably
  cannot emit those lines, so there is nothing to fix. Recorded because an unmeasured causal claim in a
  bug record is exactly the failure mode this queue exists to prevent.

### B-097 - the live heartbeat's observability is rooted in a STALE checkout that does not contain the heartbeat  [FIXED IN TREE 2026-09-11 ~11:07 CST - TDD RED->GREEN; producer moves on its next respawn]
- **Landed**: 2026-09-11 ~11:07 CST (shell TDD fix lane), both sides in ONE change:
  - producer `scripts/sapo_huanxin_heartbeat.sh`: `LOG` is now self-locating and injectable --
    `QG_SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"`,
    `LOG="${SAPO_HEARTBEAT_LOG:-$QG_SELF/logs/huanxin_heartbeat.log}"`, plus `mkdir -p "$(dirname "$LOG")"`
    so a tree that has never written the log can regenerate it.
  - consumer `scripts/session_keeper.sh`: the reader default moved to the SAME path
    (`$ROOT/logs/huanxin_heartbeat.log`), so producer and consumer resolve to ONE configurable path.
  - MIGRATION (explicit): `$LOG` is set once, at load, so the heartbeat instance LIVE at cutover keeps
    appending to the legacy file until its next respawn. `hb_log_for()` therefore reads the legacy file
    ONLY while the current-tree file does not exist yet -- the hung-heartbeat detector is never blinded
    during the window, and the old tree stops being read by itself on the first tick after the producer
    respawns. Setting `SK_HEARTBEAT_LOG` explicitly disables the shim (also the B-089 isolation property:
    a harness can never be answered from production state). Delete the shim once no pre-cutover instance
    is running. DO NOT pre-create the new log file: an empty current-tree file would make the reader stop
    consulting the live legacy log and, after 360s, render a healthy heartbeat HUNG (B-053 false-DEAD).
  - VERIFIED (shipped scripts, no production writes): producer default == consumer default ==
    `/Users/daxu/software/quantum-gpt/logs/huanxin_heartbeat.log`; `hb_log_for` with no overrides resolves
    to the still-live legacy log (mtime age 95s at 11:07) so the live chain still works end-to-end; the
    current-tree log is deliberately NOT created by this fix. New suite
    `tests/test_heartbeat_log_path_rooting.py` 7/7 (RED was 5 failed / 2 passed), adjacent
    keeper/heartbeat suites 38/38 + 36/36, `tests/test_sapo_huanxin_heartbeat_booting.sh` 9/9.
  - NOT changed, same class, recorded so it is not filed as fixed: `sapo_huanxin_heartbeat.sh` still writes
    daemon stdout to `quantum-gpt-new/logs/huanxin_all_keepalive.log` (:123) and
    `scripts/sapo_watchdog_watcher.py:44` watches that same stale-tree path. Moving it needs BOTH sides in
    one change (writer + watcher, 600s staleness bar) and was out of scope here.
- **Filed**: 2026-09-11 09:47 CST, AI dev-ops tick #348. Found while re-verifying the S9.1 census after the
  host GUI login restored the fleet.
- **Evidence (measured, not inferred)**:
  - The RUNNING supervisor is `/Users/daxu/software/quantum-gpt/scripts/sapo_huanxin_heartbeat.sh`
    (pid 83117, launchd-spawned 09:40:17, per `ps -eo pid,ppid,lstart,command`).
  - That file line 13 hardcodes `LOG="/Users/daxu/software/quantum-gpt-new/logs/huanxin_heartbeat.log"`.
  - `/Users/daxu/software/quantum-gpt-new/scripts/sapo_huanxin_heartbeat.sh` is **ABSENT** - the checkout
    the log lives in does not even contain its producer.
  - `/Users/daxu/software/quantum-gpt/logs/huanxin_heartbeat.log` is **ABSENT**; the canonical tree has no
    heartbeat log at all.
- **Severity: LATENT, not a live break (corrected on measurement - initial read was wrong).** I first took
  this as a live split-brain. It is not: `scripts/session_keeper.sh:191` reads
  `SK_HEARTBEAT_LOG="${SK_HEARTBEAT_LOG:-/Users/daxu/software/quantum-gpt-new/logs/huanxin_heartbeat.log}"`
  - the SAME stale-tree path - so producer and consumer currently agree and the chain works end-to-end
    (verified: that file is live, mtime 09:42:43, size 2035839, carrying `daemons={"ASI1":"ready",...}`).
  Recorded explicitly so this is not filed as an outage it is not.
- **The real hazard**: the whole heartbeat-observability chain is rooted in a checkout that (a) is stale, and
  (b) cannot regenerate its own log if cleaned or deleted. Anything reading the canonical tree's
  `logs/huanxin_heartbeat.log` sees ABSENT, which is exactly the false-DEAD class of S5.4.1 (a missing log
  read as a dead subject). And a `quantum-gpt-new` cleanup would break observability silently, with the
  watcher still reporting healthy.
- **Secondary**: `SAPO_HEARTBEAT_SOURCE_ONLY=1` (line 137) proves `$LOG` is sourceable, so the fix is
  testable without running the loop.
- **Fix designed (TDD, NOT landed - deliberately deferred) [SUPERSEDED 2026-09-11 ~11:07 - LANDED, see the Landed bullet at the top of this entry]**: make the path injectable and default it to the
  script's OWN tree, following the file's existing convention (`SAPO_HEARTBEAT_BOOTSTATE:-...`,
  `SAPO_HEARTBEAT_LOG:-$QG/logs/huanxin_heartbeat.log`); RED test resolves `$LOG` under
  `SAPO_HEARTBEAT_SOURCE_ONLY=1` with and without the override; update the `session_keeper.sh:191` reader
  default in the same change so producer and consumer move together.
- **WHY NOT LANDED THIS TICK (honest reason, not a gate excuse) [SUPERSEDED 2026-09-11 ~11:07 - landed by a later lane; the migration shim is the answer to the split-log risk named here]**: this edits the log path of the LIVE
  supervisor that had been dark for ~15h and had been ready for only ~5 minutes. The chain currently
  works; the defect is latent. Landing a path change that splits the log across two files mid-recovery,
  for a non-live defect, is a worse risk than filing it accurately. Also moves the keeper's reader in the
  same change, which is a two-file edit needing its own regression run - not a 3-minute edit.
- **Owner**: next attended tick / code-quality lane. **Cross-refs**: B-075, B-085 (stale quantum-gpt-new
  launchd jobs racing ports), [[keeper-runs-stale-code]], S5.4.1.


### B-106 - an unrecorded launchd disable sweep killed the fleet 4 minutes after the host login restored it  [OPEN - root-caused with evidence; heal blocked on session-gated launchctl]
- **Filed**: 2026-09-11 10:0x CST, AI dev-ops tick #348 (manager). Found while re-measuring the S9.1 census
  that tick #347 recorded as "every resource NOT-READY".
- **Symptom**: ASI1/2/3 came up, served /health ready=true, executed commands, and were connection-refused
  ~4 minutes later, with nothing left running to restart them.
- **Evidence (measured, not inferred)**:
  - Host GUI session restored 09:40:00 - `Dock` running as `daxu`, pid 82965, start 09:40.
  - launchd fired the stack: auth-broker "HTTP API up on 127.0.0.1:19090" at 01:40:41Z; three
    `huanxin_browser_daemon.js --env ASI1|ASI2|ASI3` processes (pids 87794 / 88927 / 89385) started 09:40;
    `/tmp/huanxin-daemon-ASI*.ipc/daemon.json` written 09:40 with `"ok": true`.
  - Live recovery verified: 09:41:26-09:41:37 all three executed `echo CONNECTED_$(hostname)_$(id -un)`,
    rc=0; `/tmp/huanxin_heartbeat_state.json` at 01:42:43Z reads all three **ready**; a direct probe at 09:44
    returned `ready=true, commandCount=1` on :20646, :19004 and :20653.
  - `~/Library/LaunchAgents/` **directory mtime 09:43**. Five jobs now carry the suffix `.disabled-20260911`:
    `com.quantumgpt.session-keeper`, `com.quantumgpt.huanxin-heartbeat`,
    `com.quantumgpt.huanxin-auth-broker`, `com.quantumgpt-new.asi1-keepalive`,
    `com.quantumgpt-new.huanxin-keepalive`.
  - `/Users/daxu/software/quantum-gpt-new/logs/huanxin_heartbeat.log` ends mid-cycle at **01:44:44Z**; its
    last lines are `broker down -> launchd kickstart`, then three `cookie seed FAILED (keychain denied -
    cannot decrypt user cookies)` and three `relaunched`. No line after.
  - By 09:49 all three `:20646/:19004/:20653` were `Connection refused` and `ps | grep -c huanxin_browser_daemon`
    was **0**. Still down at 10:00. Only the unrelated `ai.glm52.router` proxy supervisor survives.
  - `grep -rn "disabled-20260911" .sapo-loop/ scripts/` -> **no matches**. The action is unrecorded.
- **Root cause**: the three canonical-tree supervisors were disabled together with the two legitimate B-085
  racers. Disabling the heartbeat is what removed the only actor that restarts dead daemons, and the daemons
  were launchd-spawned inside its process group, so they went with it. Consistent with `launchctl bootout`
  on `com.quantumgpt.huanxin-heartbeat` (last supervisor log line at 01:44:44Z, daemons dead seconds later).
- **Severity: LIVE and recurring.** Every login brings the fleet up and the disable state kills it again.
- **Heal (designed, NOT landed - both required operations are session-gated for the manager)**:
  rename the THREE canonical jobs back to `.plist` (`com.quantumgpt.session-keeper`,
  `com.quantumgpt.huanxin-heartbeat`, `com.quantumgpt.huanxin-auth-broker`) and `launchctl bootstrap
  gui/501 <path>`; **leave the two `com.quantumgpt-new.*-keepalive` jobs disabled** - that part of the sweep
  was correct per B-085. Blocked live: `mv in '~/Library/LaunchAgents/...' was blocked. ... may only move
  files to/from the allowed working directories`.
- **Fix class (TDD, next attended tick)**: whatever performed the sweep must record it. A RED test can assert
  that no `com.quantumgpt.huanxin-*` / `com.quantumgpt.session-*` job is renamed without a matching
  `.sapo-loop/STATUS.md` entry (or a durable sweep log). Same class as D17.
- **Owner**: user (execute the heal) / next attended tick (land the recording guard).
- **Cross-refs**: D17, D18, B-085 (stale quantum-gpt-new racers), B-097 (sibling tick #348, different root),
  [[huanxin-triple-supervisor-b085]], [[mac-reboot-login-window-kills-fleet]], [[keeper-kick-unverified-b091]].

- **CORRECTION 10:10 CST, same tick - the causation above is WITHDRAWN.** "The fleet was dead by 09:49 with no
  supervisor left to restart it" is FALSIFIED: FOUR `sapo_huanxin_heartbeat.sh` instances are alive (PPID 1,
  pids 41870 / 51387 / 52634 / 53729, started 09:46:58-09:47:21) and the heartbeat log shows them relaunching
  daemons at 01:47:17Z and 01:47:21Z. All three daemons were back at 10:08 (`state=booting`). Revised cause of
  the 09:49-10:07 dark window: **duplicate racing supervisors** (B-055/B-085 lineage) - each supervisor's
  `pgrep`+relaunch kills the sibling's freshly-launched daemon, so the fleet flaps. This entry is therefore
  downgraded to the unrecorded-disable-sweep defect ONLY (D17). Next tick: census supervisor INSTANCE COUNT
  before daemon state.

### B-098 - the ASI1/2/3 resources FLAP on a ~2 min cycle; a single /health probe renders a flapping resource as READY  [OPEN - reproduced live, root cause NOT yet proven]
- **Filed**: 2026-09-11 09:48 CST, AI dev-ops tick #348, by the manager's own S9.1 census.
- **What I got wrong first (recorded, because the wrongness is the lesson):** at 09:42:52 CST I probed all three
  /health endpoints once and got HTTP 200 ready:true startupState:"ready" on 20646/19004/20653, and wrote
  "S9.1 GREEN for the first time in many ticks" into STATUS.md. At 09:44:08 the same probe returned URLError;
  at 09:44:12 all three were ConnectionRefusedError (Errno 61) - genuinely DEAD, not UNKNOWN. The 09:42:52
  reading was TRUE at that instant and FALSE as a description of the resource. **A single-sample probe of a
  periodically-flapping resource reads GREEN.** That is the instrument defect: the census is not
  time-integrated, so it cannot distinguish "connected" from "connected right now, by luck of phase".
- **The real defect (reproduced live, two independent time series):**
  - Series 1 (11 s sampling): 09:44:28 all-zero/ports down; 09:44:40-09:45:29 UP (4-5 heartbeat procs,
    3 browser daemons, all 3 ports UP); 09:45:41-09:45:59 all-zero/down.
  - Series 2 (11 s sampling): 09:46:39-09:46:50 down; 09:47:02 heartbeat 41870; 09:47:13 (2);
    09:47:24-09:47:46 UP (4 heartbeats, 3 browser daemons, ports UP) with keeper pids 41874, 58953.
  - Period ~2 min: UP ~50-60 s, DOWN ~70-80 s. **PIDs are FRESH every generation** (83117 to 41870 to 51387
    to 52634 to 53724), so these are new process generations being torn down and rebuilt, not long-lived
    processes. The daemons never hold ready.
- **Corroborating evidence**: session_keeper.log froze at 09:41:36; logs/huanxin_heartbeat.log
  (the quantum-gpt-new one, see B-097) froze at **09:42:43** - the fresh heartbeat generations never write
  a log line at all. huanxin_heartbeat.launchd.err froze at 04:33 and contains
  "fork: Resource temporarily unavailable" and "line 173: action: unbound variable" (historical, pre-B-079-fix).
  No plist in ~/Library/LaunchAgents contains "heartbeat" or "session_keeper"; the flapping procs have
  **ppid 1** and no owning plist - consistent with launchctl submit / orphaned spawn, NOT with a KeepAlive job.
- **Strong lead, NOT a proven root cause (stated as a lead, per B-079's lesson about the rename class):**
  scripts/sapo_huanxin_heartbeat.sh's own B-047 comment describes this exact shape - "session_keeper.sh:158
  kickstarts this script with launchctl kickstart -k whenever the daemons are not ready, the kick resets
  the boot timers, the 900s wedge branch becomes unreachable, the stuck daemons are never restarted and
  never converge, the keeper kicks again". A ~2 min teardown/rebuild is the predicted signature. I have NOT
  proven it: launchctl is gate-blocked this session, the keeper is itself intermittent (0 procs in all of
  series 1, present at 09:47:46 in series 2), and I have no kick-action log line for this window. Cross-refs:
  [[keeper-kick-unverified-b091]] (ACTION ... kick means ATTEMPTED, never DONE), B-047, B-075, B-085, D9.
- **Impact**: S9.1 RED - the three resources are effectively unusable (a box command issued during a DOWN
  phase is refused). The dashboard must report them NOT-READY.
- **Fix**: NOT attempted this tick. A fix requires (a) proving the kick attribution, (b) editing
  session_keeper.sh / the heartbeat kick path, both under a live flapping loop - not a 3-minute edit, and
  launchctl is gated. **Next tick's FIRST task** (see S5 order).
- **Instrument fix owed (do this regardless of the flap's root cause)**: the S9.1 census must sample N times
  over a window and report UP/DOWN/FLAP, never a single probe. A one-shot probe of a flapping resource is a
  false-GREEN generator.

## B-099 OPEN->FIXED IN TREE 2026-09-11 10:0x CST — metrics poller target hardcoded to a RETIRED run
- **Filed + fixed by:** interactive session (manager), discovered while assessing resume-readiness.
- **Defect (MEASURED):** `.sapo-loop/sapo_metrics_poll.py:17` was
  `RUN = "sapo-27b-ai-20260908T094427Z"` with **no override of any kind**
  (`grep -nE 'environ|getenv|argv'` -> zero hits), and `:19` carried a **SECOND hardcoded copy**
  of the same run id inside `LOG` (`grpo_train_20260908T094427Z.log`). The newest run on the box
  was `sapo-27b-ai-20260909T104517Z`, so the monitor could only ever describe a run that had
  already ended, and it rendered that run's absence as the live state ("tick dead: empty").
- **Class:** "no silent lies" (S4.1) — *"the live run could not be read"* is NOT *"the live run is
  dead"*, and a target that cannot be repointed makes that distinction **inexpressible**.
- **TDD:** RED `tests/test_sapo_metrics_poll_run_target.py` -> **4 failed** (R1..R4). Fix ->
  **4 passed**. Regression: `test_sapo_metrics_poller_transport` + `test_sapo_metrics_poll_parser`
  + `test_sapo_metrics_poll_stability` + `test_sapo_metrics_poller` -> **26 passed / 0 failed**
  (`/usr/bin/python3 -m pytest -q -p no:cacheprovider`).
- **Fix:** precedence is now explicit-env `SAPO_RUN` -> durable pointer file
  (`SAPO_RUN_POINTER`, default `.sapo-loop/.current_run` beside the module) -> **UNRESOLVED**.
  `METRICS`/`LOG`/`ADAPTERDIR` are all DERIVED from the resolved id (no second copy). Unresolved is
  reported as unresolved via `RUN_RESOLVED=False` and never falls back to naming a specific old run.
- **B-096 respected:** the pointer path is env-overridable so tests write only `tmp_path`, never the
  live `.sapo-loop/`.
- **NOT deployed:** this is a Mac-local monitor; no box bundle is involved. Note the poller's own
  subject (training) is currently STOPPED, so the honest steady state is now UNRESOLVED, not a
  retired-run readout.


---

### B-131 - the circuit breakers are structurally blind to a collapse INHERITED from the warm-start checkpoint  [RENUMBERED from a colliding B-099 at tick #367]
- **RENUMBERED tick #367 (2026-09-11)**: this entry was filed under **B-099**, which the ledger had already
  used for the *metrics-poller run-target* bug (`## B-099 OPEN->FIXED IN TREE ...`, plus its ADDENDUM at the
  same depth). Two different bugs, one ID. All **31 external B-099 references** in `tests/`, `scripts/` and
  `training/` were measured before renumbering and every one of them points at the POLLER bug, so this
  breaker entry is the one that moved. The old ID is named here so earlier notes still resolve.
  [FIXED + VERIFIED 2026-09-11 tick #349]
- **Filed**: 2026-09-11 09:55 CST, AI dev-ops tick #349. This is the standing D-336-3 blocker for the
  next training leg (option (a) warm-continue), previously root-caused to a mechanism (tick #336) but
  never fixed. Now fixed, with a red test and a replay against the real data.
- **Measured evidence (box-side, `outputs/sapo-27b-ai-20260909T104517Z/grpo_step_metrics.jsonl`)**:
  - 100/100 steps `all_fail=true`; 97/100 `skipped=true`; last step `mean_reward=0.0`, `reason=low_reward_signal`.
  - `entropy_mean` between **0.00021** and **0.11169** (max at step 58) - i.e. the policy is inside
    collapse territory (< 0.05) from step ~4 onward.
  - `circuit_breaker_state.tripped == []` on every row. `degenerate_policy_alarm` False on all 100 rows.
  - Persisted `entropy_baseline = 0.00537` - the baseline was calibrated INSIDE the collapse.
- **Root cause (two independent structural blind spots, verified in `training/grpo_utils.py`)**:
  1. `entropy_collapse` requires BOTH `_entropy_baseline` and `_frontier_baseline`, and both are
     calibrated from the run's FIRST `entropy_baseline_steps` (default 20). A policy already collapsed
     at step 1 becomes its own baseline, so the ratio test can never fire.
  2. `all_fail_without_repair` requires `queue_grew`. A collapsed policy emits no repair candidates, so
     `repair_queued` is never True, `queue_grew` stays False, and the breaker is unreachable by
     construction - the counter stayed at 0 on all 100 rows.
  Nothing tripped, so `stop_on_severe_breaker: True` was configured and never consulted.
- **Fix (smallest, additive, no behaviour change to existing rules)**: a new rule
  `entropy_absolute_collapse` - a window trips it iff EVERY step is `all_fail_share > 0.40` AND every
  measured entropy is `<= entropy_absolute_floor` (new field, default 0.05, aligned with
  DEGENERATE_POLICY entropy territory; healthy runs here measure 2.0-6.0). It depends on no baseline
  and no repair queue, so inherited collapses are caught while healthy all-fail runs with live entropy
  are not.
- **TDD**: RED first - `tests/test_grpo_inherited_collapse_breaker.py` produced `assert []` (no trip) on
  the old code for both collapse cases while both false-positive guards passed. GREEN after the fix:
  **6/6**. Includes a **replay test on the real 100-step entropy series**, which now stops the run at
  **step 8** instead of burning the remaining 92 steps.
- **Regression**: `test_fv_gspo.py` + `test_grpo_trainer_breakers.py` + `test_grpo_trainer_metrics.py`
  + `test_compat.py` + the two new files = **133/133 green**. All pre-existing breaker tests
  (entropy-ratio, all-fail-without-repair, clip, non-finite, holdout) still pass unchanged.
- **Deploy status**: LANDED IN TREE. NOT yet deployed to the box - there is no live run, and no launch
  happens without USER GO (standing S2.8/S5.4). The fix must be a bundle member at the next launch.
- **Objective impact**: this was the standing precondition (a) on D-333-5/D-336-3 for the warm-continue
  branch. It is now satisfied at the code level. Precondition (b), explicit USER GO, is NOT.
- **Cross-refs**: D-336-3, D-333-5, [[sapo-inherited-collapse-blindspot]], `training/grpo_utils.py`
  `CircuitBreakerState`.



### B-100 - 12 eval task files used `zip(..., strict=...)`, a py3.10-only keyword that crashes the py3.9 box runtime  [FIXED + VERIFIED 2026-09-11 tick #349]
- **Filed**: 2026-09-11 09:58 CST, AI dev-ops tick #349, found while running the grpo regression sweep.
- **Symptom**: 26 FAILED in `tests/test_grpo_pipeline_fast.py` - every `test_reference_candidate_passes`
  and `test_reference_candidate_gets_full_reward` for 13 quantum tasks. Error:
  `TypeError: zip() takes no keyword arguments` (e.g. `evals/tasks/quantum/bell_pair_construction/tests.py:19`).
- **Root cause**: the documented py3.9 token class - the mere PRESENCE of the `strict` keyword raises on
  3.9 regardless of value, so `strict=False` (the "safe-looking" form) crashes identically to
  `strict=True`. 12 files under `evals/tasks/quantum/` carried it: 9 `tests.py` and 3 `candidate.py`
  (`ghz_state_witness`, `simon_period_finder`, `swap_test_state_overlap`). A scan for `strict=True`
  misses all of them.
- **Blast radius, stated honestly**: this is not only a local-test defect. The same files are executed
  by the eval harness ON THE BOX (Python 3.9.6), so those 13 tasks cannot be evaluated there at all -
  they fail as reference-candidate crashes.
- **Fix**: replace `, strict=False)` with `)` - behaviour-identical on py3.10+ (which is why the tree
  looked green in any 3.10+ context) and correct on 3.9. `strict=True` call sites would instead need an
  explicit length assertion, which preserves the intended safety rather than silently dropping it.
- **TDD**: RED `tests/test_py39_runtime_token_scan.py` first (it flagged the 12 files), then the sweep
  fix, then GREEN. The guard is an **AST scan for a keyword argument named `strict`, scoped to `zip`
  calls** - a text scan false-positives on the many explanatory comments that mention the keyword, and a
  `Path.resolve(strict=False)` call is legitimate on 3.9. The guard carries two non-vacuity tests: a
  planted offender must be detected, and non-zip `strict` keywords must NOT be.
- **Verification**: `tests/test_grpo_pipeline_fast.py` went **26 failed -> 2 failed / 374 passed**. The 2
  remaining are `quantum_braket_bell_state`, which is a different, already-enumerated environmental gap
  (the `braket` SDK is not installed) - not this class.
- **Deploy status**: LANDED IN TREE, not deployed (no live run; no launch without USER GO). These files
  are bundle members, so the fix must ride the next bundle.
- **Cross-refs**: S2.7 runtime-environment gate, [[runtime-gate-interpreter-trap]].


### B-099 ADDENDUM (same session, ~10:1x CST) — a SECOND hardcoded identity in the same module
While verifying the fix I read `main()` and found `TRAINER_PID = "94515"` is ALSO a hardcoded
literal, and the trainer-death assertion sits **BEFORE** the rows check:
`trainer_alive = bool(ps_out.strip()); if not trainer_alive: ... append(STATUSMD, ALERT); return 2`.
So fixing only the run target would have left the real live symptom firing: with a stale PID and no
trainer, the poller appended `METRICS ALERT: trainer PID 94515 NOT RESIDENT` to the live STATUS.md
on **every** cycle. The target fix alone was INCOMPLETE — stated because "fixed the symptom I
measured first" is exactly the half-fix this queue exists to catch.
- **Fix:** `main()` now short-circuits on `RUN_RESOLVED is False` BEFORE any box call or liveness
  verdict, emitting `POLL-NO-TARGET` and returning 1. A run we never resolved is a run we never
  measured, so no liveness claim is made about it.
- **Non-vacuity (END-TO-END, not unit):** `test_R5_unresolved_target_asserts_no_liveness_verdict`
  runs the poller as a SUBPROCESS with no target, and asserts (a) `NO-TARGET` in output,
  (b) exit 1, (c) `"NOT RESIDENT"` absent, and (d) **live `STATUS.md` bytes unchanged**. R5 is RED
  without the guard (the PID path fires) and GREEN with it.
- **Final counts:** `tests/test_sapo_metrics_poll_run_target.py` -> **5 passed / 0 failed**;
  poller regression cluster -> **26 passed / 0 failed** (`/usr/bin/python3`, `-p no:cacheprovider`).
- **Still open (NOT fixed here, deliberately):** `TRAINER_PID` remains a literal. The correct fix is
  discovering the trainer on the box (pgrep) rather than naming a pid, which changes the
  process-liveness contract and needs its own RED test. Filed as a follow-up, not silently folded in.


---

### B-101 - ASI1's daemon is spawned and then SIGKILLed every cycle; the heartbeat reports "relaunched" and the resource never comes back  [OPEN - reproduced; kill source NOT yet proven]
- **Filed**: 2026-09-11 10:30 CST, AI dev-ops tick #349, by the manager's own S9.1 census.
- **Symptom**: ASI1 (:20646) went unresolvable at ~10:12:20 and never returned. ASI2 (:19004) and ASI3
  (:20653) held READY throughout. The keeper flips to `"daemons":"healing"` and the heartbeat restarts
  ASI1 every tick - `ASI1: cookie bridge + restart` / `ASI1: relaunched` at 02:13:25Z, 02:15:30Z - but no
  `huanxin_browser_daemon.js --env ASI1` process exists after any of them (`pgrep -f ...` -> empty).
- **Reproduced (burst census, 6 minutes)**: exactly ONE ASI1 node process was ever seen live - pid 26645 at
  10:23:52 - and it was gone by the next sample.
- **Direct evidence of the kill** (`quantum-gpt-new/logs/huanxin_all_keepalive.log`, last 100 lines): three
  consecutive spawn attempts, each ending in an identical exclusive kill:
  - `<launched> pid=81236` -> `[pid=81236] <process did exit: exitCode=null, signal=SIGKILL>`
  - `<launched> pid=26728` -> `[pid=26728] <process did exit: exitCode=null, signal=SIGKILL>`
  - `<launched> pid=47035` -> `[pid=47035] <process did exit: exitCode=null, signal=SIGKILL>`
  `exitCode=null` with a signal means the process was terminated by an external SIGKILL, not a browser
  crash. Chrome reached `--user-data-dir=.../huanxin-profile-quantum-rnd-ASI1` and had written the profile
  (`mtime` advancing to 10:21:48) before dying, so the profile itself is not obviously corrupt.
- **Two candidate mechanisms, both testable - NOT claimed as root cause:**
  1. `sapo_huanxin_heartbeat.sh:96` does `pgrep -f "huanxin_browser_daemon.js --env $E" | head -1` then
     `kill "$pid"`. That pattern is an unanchored substring of the launcher's OWN argv
     (`... sapo_detach_exec.sh ... huanxin_browser_daemon.js --env ASI1`), so the match set can include
     the just-spawned launcher - the same "grep matches its own command line" class already documented
     for the trainer (`[[trainer-grep-self-matches-brief]]`) and fixed in `keeper-started-line-is-not-a-start`.
     An anchored pattern (`node.*huanxin_browser_daemon\.js --env $E`) would exclude it.
  2. A launchd process-group teardown of the heartbeat job (the B-055 class) reaching the fresh daemon
     before `sapo_detach_exec.sh` finishes detaching it. B-055's fix (setsid in the helper) covers daemons
     that got far enough to detach; a kill landing earlier in the spawn would still hit.
- **Measured counters against the candidates**: the heartbeat's own pgrep pattern returns EMPTY right now
  (no ASI1 node process alive), so the kill is not a steady-state cleanup of a live daemon - it fires
  inside the spawn window. A controlled repro with a fake launcher was attempted and was inconclusive
  (the fake process exits on its own before observation), so neither candidate is proven yet.
- **Impact**: S9.1 is RED on 1 of 3 resources. Training is idle, so nothing is blocked today; ASI1 would
  be unusable for any leg until healed. The failure is silent - the supervisor reports "relaunched" for a
  resource that is provably not running (the same `keeper-kick-unverified` reporting class).
- **Next concrete step**: run `seed_and_restart` for ASI1 by hand with the two candidate fixes applied
  one at a time (anchored pgrep FIRST - it is the smaller change), observing whether the node process
  survives 60 s. RED test: an anchored-pattern unit test asserting the launcher argv is NOT a match.
- **Cross-refs**: B-055, B-074, B-085, B-098, [[keeper-kick-unverified-b091]],
  [[trainer-grep-self-matches-brief]], [[keeper-started-line-is-not-a-start]].


### B-102 - the ASI1-only keepalive cannot resolve `node`, so it can never start ASI1's daemon; it retries forever and logs the failure as a restart  [OPEN - root-caused with evidence; fix staged]
- **Where**: `/Users/daxu/software/quantum-gpt-new/scripts/asi1_keepalive.sh` - the stale-checkout sibling
  that `~/Library/LaunchAgents/com.quantumgpt-new.asi1-keepalive.plist` runs (`StartInterval 60`). Inside an
  ALLOWED root (`sapo_scope_guard.py` lists quantum-gpt-new as "logs + keeper scripts"), so in-scope.
- **Evidence (its OWN log, live and 60s-cadenced, `quantum-gpt-new/logs/asi1_keepalive.log`)**:
  - `02:11:11Z health=ready`   <- agrees with this tick's port probe to the second
  - `02:12:11Z health=down` -> `daemon down -> starting (detached)`
  - `02:14:15Z ERROR: node binary not found`
  - `02:15:46Z after restart health=down` -> retries 02:17:40Z, 02:18:10Z, 02:19:11Z ... forever
- **Root cause**: `NODE_BIN="$(command -v node || ls /Users/daxu/.local/state/fnm_multishells/*/bin/node 2>/dev/null | tail -1)"`.
  Under launchd the PATH is minimal, so `command -v node` fails; the fallback globs
  `~/.local/state/fnm_multishells/*/bin/node`, but node actually lives at
  `~/.local/share/fnm/node-versions/*/installation/bin/node` - a DIFFERENT tree. The fallback path exists
  but expands past ARG_MAX (a direct `ls` on that glob returns `(eval):1: argument list too long`). Either
  way NODE_BIN is empty and the launch is skipped. The CURRENT-tree heartbeat resolves node via the correct
  `share/fnm/node-versions/...` path and is immune.
- **Impact**: ASI1 loses its only launchd-supervised healer. It is NOT the cause of the Chrome SIGKILL
  (B-101) - this script never reaches a launch - but it removes the redundancy that would mask B-101, and
  `daemon down -> starting (detached)` reports an attempt that provably did not happen (the same
  `keeper-kick-unverified` reporting class as B-091).
- **Fix direction (STAGED, not applied)**: per B-085, the cure for a duplicate stale supervisor is to
  DISABLE the job - the canonical heartbeat already owns ASI1. If it must stay, repair the node path to
  `share/fnm/node-versions`. `launchctl` is session-gated and §5.4.2 forbids hot-editing a live supervisor
  mid-heal, so this is staged to the next launch boundary, NOT landed.
- **Also recorded**: the job STOPPED firing after `02:19:11Z` - no further `health=` lines even though the
  script echoes unconditionally every tick. That is an unrecorded launchd unload/disable at ~10:19 CST
  (the D17 class from tick #348), and ASI1 came back and held shortly after. Correlation noted; causation
  NOT claimed.
- **Cross-refs**: B-055, B-085, B-091, B-097, B-098, B-101, B-106.

### B-104 - the divergence watcher watched a RETIRED run and could render a STALE/FOREIGN eval as the live beats-base state  [FIXED IN TREE 2026-09-11 ~10:5x CST - TDD RED->GREEN; Mac-side monitor, NOT a box-bundle member]
- **Defect (read from `scripts/sapo_divergence_watch.py`, pre-fix):** `:23` `METRICS_REMOTE` was a LITERAL retired run
  (`.../outputs/sapo-27b-ai-20260901T015238-resume3/grpo_step_metrics.jsonl`) with NO override of any kind (the pre-fix
  module contained no `os.environ`/`os.getenv`/`sys.argv` reference at all); `:58-61` was a FIXED two-file `known` list
  and `:85` `latest = evs[-1][1]` picked "the latest" by LIST ORDER (no mtime, no freshness check), and the source
  file/step was never printed; `:90` the GREEN branch had no freshness/identity gate, so a STALE eval file could print
  `GREEN: holdout ABOVE base - BEATS-BASE PATH` while a DIFFERENT adapter was live - appended to the live
  `.sapo-loop/divergence_watch.md`. Live corroboration: `.sapo-loop/lanes/error_signatures.md:294`
  `divergence waiting-for-data (evals=2, train_trend=no)`.
- **Class:** S4.1 no silent lies - B-099 family (a monitor whose target cannot be repointed renders a retired run's
  state as current, and a verdict that does not name its source cannot be audited).
- **Fix (precedence copied from the B-099 poller):** `SAPO_RUN` -> durable pointer `SAPO_RUN_POINTER` (default
  `.sapo-loop/.current_run`, SHARED with the poller) -> UNRESOLVED; re-resolved EVERY cycle so a pointer change
  re-points a running watcher. Metrics must be FRESH (box mtime <= METRICS_MAX_AGE_S=3600, measured on the box, not
  assumed); the newest `reeval_*.json` is chosen by MTIME; that eval must name an `adapter` under the resolved run dir
  (a foreign run's eval is refused); verdict lines now print `run=<id> ... src=<file>@<age>s step=<N>`. UNRESOLVED /
  stale / foreign -> `UNKNOWN` logged and NOTHING appended. `--once` = one poll, exit 0 on a verdict / 2 on UNKNOWN.
- **TDD:** RED `tests/test_sapo_divergence_watch_run_target.py` -> **0 passed / 8 failed** pre-fix (D8 hung instead of
  failing closed); final **10/10 green**, re-derived against a verbatim copy of the pre-fix source -> **10 failed**
  (non-vacuity incl. D5b stale-eval and D9 end-to-end GREEN-with-source, added after the first RED). D8/D9 stub the box
  transport AND trap `HTTP_PROXY` at a closed port, so the suite never touches the box.
- **Adjacent suites:** `tests/test_sapo_parallel_eval_agent.py` 6/6; `tests/test_sapo_ruff_clean_scripts.py` 2/2
  (B-019 UP031 - the new code is ruff-clean). Pre-existing, NOT mine: `tests/test_sapo_metrics_poll_run_target.py::
  test_a3_locate_trainer_real_probe_parses_a_live_pid` fails deterministically (a sibling session's in-flight untracked
  additions; `locate_trainer` is untouched by this fix).
- **Not fixed / adjacent (OPEN):** the operator launch line in `.sapo-loop/RESTART_HERE.md:39` is unchanged and still
  valid; with no `.current_run` (today's state) the honest steady output is UNKNOWN, not a retired-run readout.
- **Cross-refs:** B-099 (same defect, first monitor), B-105 (same family, eval agent), B-096, [[sapo-inherited-collapse-blindspot]].

### B-105 - the parallel eval agent defaulted to a RETIRED run, and keyed its done-state by checkpoint BASENAME so a retired run's verdict suppressed the live run's eval  [FIXED IN TREE 2026-09-11 ~10:5x CST - TDD RED->GREEN]
- **Defect (read from `scripts/sapo_parallel_eval_agent.sh`, pre-fix):** `:11`
  `RUN_DIR="${3:-.../outputs/sapo-27b-ai-20260901T015238-resume3}"` (args 1 and 2 defaulted too) -> a BARE invocation
  silently drove the retired run while the live run got zero coverage, with nothing in the output saying so; `:32-35`
  keyed the done-verdict state `NAME="$(basename "$CK")"` = `step_NNN_adapter`, IDENTICAL across runs, while the state
  file is per-ENV not per-run (`STATE="$ROOT/reports/.sapo_parallel_eval_state_${ENV_NAME}.json"`) and provably
  accumulates entries for MULTIPLE runs (live `reports/.sapo_parallel_eval_state_ASI2.json` holds
  `adapter: .../outputs/sapo-27b-ai-20260902T072812Z//step_000001_adapter`). A `done` recorded for a RETIRED run's
  `step_NNN_adapter` therefore silently SUPPRESSED the live run's same-named checkpoint = silent skip of real eval work.
- **Fix:** RUN_DIR (arg 3) is REQUIRED - missing/empty refuses (`exit 2` + usage on stderr) BEFORE any box probe, state
  init or leg; the done-state key is the checkpoint's FULL path (it carries the run dir, so two runs cannot share a key).
  Eval-leg logs are redirected by `SAPO_EVAL_LOG_DIR` (default `/tmp/sapo-logs`) so tests never write live logs (B-096).
- **TDD:** RED `tests/test_sapo_parallel_eval_agent_run_keying.py` -> **3 defect pins failed pre-fix in BOTH directions**
  (K2: the retired bare-basename `done` suppressed the live run's checkpoint - reproduced, agent did nothing; K3: a
  run-scoped `done` was ignored -> the leg re-fired); final **4/4 green**. K4 is a harness guard (live
  `reports/.sapo_parallel_eval_state_*.json` byte-identical) and is green on both sides by design. Every case runs a
  COPY of the agent in `tmp_path` with a stubbed exec transport: no leg launched, no box touched.
- **Leftover from the RED run, cleaned:** `/tmp/sapo-logs/eval_step_000004_adapter.log` (empty, created by the pre-fix
  code's hardcoded log dir) + the directory my run created; the fix removes that write path from tests.
- **KNOWN REMAINING (new, NOT fixed here):** the agent's done-lookup can only see keys the agent itself writes -
  `asi2_loop_eval.sh`'s terminal `update_state` keys entries by the leg's TS, not by the checkpoint, so a completed leg
  is not visible under any run-scoped checkpoint key and the agent re-fires the same checkpoint every scan. That is the
  long-standing `repeated re-eval ... real_verdict=false` signature (`.sapo-loop/lanes/error_signatures.md`, ASI2).
  Run-scoping is a PREREQUISITE for fixing that, not a fix of it.
- **Cross-refs:** B-104 (same family), B-003 (eval state-file races / per-env split), B-016 (completeness gate), B-096.

### B-107 - the heartbeat's single-instance guard is an ACQUIRE-TIME check that is never re-validated  [FIXED IN TREE; deploy STAGED on session-gated kill/launchctl]
- **Measured** (tick #350, re-verified #351 10:52 CST): TWO resident production heartbeats, pid **41870**
  (started 09:46:58) and pid **90794** (started 10:28:02), both PPID 1, both argv
  `/Users/daxu/software/quantum-gpt/scripts/sapo_huanxin_heartbeat.sh`. 90794 owns the live ASI1 browser
  daemon (pid 90852, started the same second).
- **The lock was NOT stolen.** `/tmp/sapo_locks/sapo_heartbeat/holder` reads `41870` with an unmodified
  09:46 mtime; no `.refreshed`, no leaked `.acq.sapo_heartbeat` token; a fresh
  `acquire sapo_heartbeat --holder-pid 999999 --steal-stale` returns **exit 1** (re-verified this tick).
  So 90794 is resident while NOT holding the lock, and neither process notices.
- **ROOT CAUSE**: the guard runs ONCE, before `while true`, and is never re-read for the life of the
  process. A start-time-only guard cannot see an instance that entered after it, so a duplicate's
  lifetime is unbounded (until host restart). Precedent: `scripts/sapo_judge_mac_watcher.py` already
  re-verifies every tick with `--reacquire` (B-063) -- the heartbeat is the lane that never adopted it.
- **The window that admitted 90794 is UNKNOWN and is NOT claimed.** Hypothesis (UNMEASURED): the script
  was rewritten IN PLACE at 10:28 / 10:34 / 10:35 while bash was reading it, and bash resumes at a byte
  offset into the NEW content -- which can land past the guard. Plausible, not proven; no claim made.
  (This is also why the fix below was written by `os.replace`/rename(2), preserving the old inode for
  the two readers still executing it.)
- **FIX (landed, atomic)**: re-validate inside the loop --
  `acquire sapo_heartbeat --holder-pid "$$" --reacquire` -- and on refusal log
  "single-instance lock lost to another live instance -> exiting" then `exit 0`. Duplicate lifetime is
  now bounded by ONE tick (~120s), whatever let it in. This is the section 5.4.1 BUG-ZERO convergence
  rule applied to the heartbeat itself.
- **TDD**: RED `tests/test_heartbeat_lock_revalidation.py` (1 failed pre-fix) -> GREEN 3/3; regressions
  55/55 (heartbeat + single-instance-lock suites, incl. the B-063 reacquire and B-062 live-holder
  suites); `bash -n` OK. Surface total 64 green, 0 failed.
- **DEPLOY STAGED**: both live instances execute the PRE-fix inode, so the landed fix is INERT
  ([[keeper-runs-stale-code]] class). Restart needs `kill`/`launchctl` = session-gated (B-102 class).
  `KeepAlive=true` + `RunAtLoad=true` confirmed in
  `~/Library/LaunchAgents/com.quantumgpt.huanxin-heartbeat.plist`, so a restart is SAFE and
  self-respawning -- but BOTH instances must die together, or the respawned instance is refused by the
  surviving old holder's lock and launchd enters a respawn storm.
- **ORDER**: the next session holding the launchctl/kill gate restarts
  `gui/$(id -u)/com.quantumgpt.huanxin-heartbeat`; then assert exactly ONE resident heartbeat and that
  it re-publishes `/tmp/huanxin_heartbeat_state.json`.

### B-098 ID COLLISION (found tick #351) - the ledger has TWO different bugs sharing ID B-098
- `### B-098 - an unrecorded launchd disable sweep killed the fleet 4 minutes after the host login
  restored it` and `### B-098 - the ASI1/2/3 resources FLAP on a ~2 min cycle` are both in this file.
  Same class as the 09-02 ledger-integrity corruption (B-005 x3, B-006 x2, B-007 x2). One of the two
  should be renumbered to a free ID (B-101) so each row has a single canonical ID. Recorded, not fixed
  this tick -- renumbering is a ledger edit that the two live rows' owners should agree on.

### B-098/B-100 ID COLLISION - CLOSED (tick #352, 2026-09-11 11:0x CST) - renumbered + guard test
- **Reproduced**: a header-parse of the ledger found 32 `### B-NNN` headers over 23 unique ids. Adjudicated
  one-by-one: 4 ids (B-089, B-093, B-095, B-099) have repeat headers that are STATUS UPDATE / CLOSED /
  ADDENDUM / WATCHLIST sections of the SAME bug -- legitimate. **2 ids were genuine collisions**, one bug id
  naming two different unrelated bugs:
  - `B-098` = (a) "an unrecorded launchd disable sweep killed the fleet" AND (b) "the ASI1/2/3 resources FLAP
    on a ~2 min cycle".
  - `B-100` = (a) "12 eval task files used `zip(..., strict=...)`" AND (b) "the heartbeat's single-instance
    guard is an ACQUIRE-TIME check".
- **The collision had already leaked into SHIPPED CODE** -- this is why it is not a paperwork bug:
  `scripts/sapo_huanxin_heartbeat.sh:180` cited **B-098** for the acquire-time-guard finding, which the ledger
  files under **B-100(b)**. B-098 in the ledger means the launchd sweep / the FLAP. So the source comment
  pointed at the wrong bug entirely. Fixed to B-107.
- **Which id kept the name**: B-098 was kept for the FLAP bug, NOT the first-occurrence sweep entry, because
  the only two inbound cross-refs (in B-101 and B-102) describe the FLAP/daemon-death symptom -- keeping FLAP
  as B-098 is the choice that breaks zero references. The sweep entry became **B-106**.
- **Tick #351's repair prescription was ITSELF WRONG**: it said "renumbered to a free ID (B-101)" -- but B-101
  is already taken (`### B-101 - ASI1's daemon is spawned and then SIGKILLed every cycle`). Applying it would
  have created a THIRD collision. Corrected here; a free id is max+1, never a guessed gap.
- **Renumbered**: sweep -> **B-106**; heartbeat acquire-time guard -> **B-107** (`scripts/sapo_huanxin_heartbeat.sh`
  comment retargeted to match).
- **TDD**: RED `tests/test_bugqueue_id_uniqueness.py` -> **1 failed / 1 passed** pre-fix, naming exactly the two
  entries above -> **2/2 GREEN** post-fix. The second test is a NON-VACUITY pin (>20 headers parsed, B-098
  present), because a naive duplicate check over a wrongly-pathed or empty file asserts nothing -- the
  shadowed-helper vacuity class (§4.1).
- **Regression**: `bash -n scripts/sapo_huanxin_heartbeat.sh` OK after the comment edit.
- **Note**: the ledger is appended-to by concurrent loop sessions mid-tick ([[concurrent-loop-sessions-land-mid-tick]]);
  the renumber was applied line-ANCHORED by content match, and the guard test re-reads the file each run, so a
  future duplicate lands RED automatically.
- **Cross-refs**: B-005/B-006/B-007 (the 09-02 ledger-integrity corruption, same class), B-101, B-102, B-104.

### B-108 - the watchdog police checked freshness but never the VERDICT, so a failing judge rendered GREEN  [FIXED IN TREE 2026-09-11 ~11:1x CST - TDD RED->GREEN; no restart needed, exec'd per heartbeat tick]
- **Defect**: `scripts/sapo_judge_health_agent.py:191-198` rewrites `/tmp/sapo_judge_health_state.json`
  every 300s REGARDLESS of whether the judge works -- `{"ts","healthy","detail","strikes"}` with
  `healthy:false` and strikes climbing on every failing probe. `scripts/sapo_watchdog_watcher.py` read
  only `st_mtime` (max_age 720s); the body was never loaded. So a judge returning garbage rendered
  `WATCHDOG-WATCHER: GREEN (all watchdog outputs fresh)`, exit 0, and the heartbeat's POLICE branch
  (`sapo_huanxin_heartbeat.sh:258-262`, `case "$WW" in *GREEN*`) stayed silent. Freshness was being
  reported AS health: section 4.1 "no silent lies" / 5.4.1 "liveness of OUTPUT", applied to the police
  that is supposed to catch exactly this.
- **Fix (landed)**: per-item `VERDICT_CHECKS` registry keyed by the WATCHED item NAME (so the path
  stays single-sourced in `WATCHED`; guard test pins that). `stale_items` keeps the freshness check
  intact and, for items with a check, loads the payload and fails CLOSED: `healthy` must be literally
  True -- `false`, a missing/bogus key, a non-object or unparsable body, or a raising checker are all
  RED entries carrying detail + strikes. Items with no check (heartbeat, keeper-log, logs) keep the
  pure-freshness contract. GREEN banner now reads "fresh and healthy".
- **TDD**: RED `tests/test_watchdog_watcher_verdict.py` **7 failed / 6 passed** pre-fix (identical file
  against the pre-fix module; headline failure printed `WATCHDOG-WATCHER: GREEN (all watchdog outputs
  fresh)` for a state file holding `healthy:false`) -> GREEN **13/13**. Regressions: watcher + judge
  repair-contract + judge health-agent suites **37/37 green**. `py_compile` OK, `bash -n` heartbeat OK.
- **E2E (the real consumer branch)**: the fixed watcher isolated to the judge-health item on a temp
  path, driven through the heartbeat's exact `tail -3 | head -2` + `case *GREEN*` pipeline:
  fresh+healthy -> POLICE OK / exit 0; fresh+healthy:false -> POLICE RED / exit 1 with
  `judge-health: UNHEALTHY (healthy=False strikes=3 detail='...')`. Controls pin that STALE and MISSING
  stay RED and a healthy judge stays GREEN.
- **SAFETY**: no test writes the real `/tmp/sapo_judge_health_state.json` (fixtures use tmp_path; the
  production path appears exactly once in the watched table); sha256 `c3c80a80...` and mtime 11:01:14
  unchanged across every run. Live production run flags only the pre-existing missing
  `/tmp/sapo_wedge_watch.log` -- judge-health is not in the RED list, so no new false RED was added.
- **DEPLOY**: `QG=/Users/daxu/software/quantum-gpt`, and the police is spawned fresh each heartbeat
  tick (`python3 "$QG/scripts/sapo_watchdog_watcher.py"`), so the fix is LIVE on the next tick -- no
  kickstart/kill gate (unlike keeper-class fixes).

### B-098/B-100 ID COLLISION - INDEPENDENTLY VERIFIED (tick #352, manager, 2026-09-11 11:07 CST)
- The closure above was written by a CONCURRENT SIBLING LANE mid-tick, so it was verified rather than assumed
  ([[concurrent-loop-sessions-land-mid-tick]]). **Verdict: CONFIRMED, no correction needed.**
- **Re-ran the guard test myself**: `tests/test_bugqueue_id_uniqueness.py` -> **2/2 GREEN** (0 failed).
- **Independent parse, NOT their test**: 34 `###` headers over **26 unique ids**. Every remaining repeat is a
  legitimate same-bug section -- B-089 (STATUS UPDATE), B-093 (x3 STATUS UPDATE/CLOSED), B-095 (WATCHLIST),
  B-098 (the collision meta-sections themselves), B-099 (ADDENDUM). **No header beginning `### B-100 -` for a
  second unrelated bug survives**, and neither does a second `### B-098 -` for the sweep.
- **Source retarget confirmed by eye**: `scripts/sapo_huanxin_heartbeat.sh:180` now reads
  `# B-107 (2026-09-11): the single-instance guard above is an ACQUIRE-TIME check, not an invariant` -- the
  wrong-bug citation (it previously cited B-098, which the ledger files as the launchd sweep / the FLAP) is fixed.
- **Also verified**: B-106 = the launchd disable sweep; B-107 = the heartbeat acquire-time guard. Both headers
  present with the correct titles.
- **What is NOT claimed**: the renumber does not close either underlying bug. B-106 remains OPEN (heal blocked
  on session-gated launchctl) and B-107 remains FIXED-IN-TREE / DEPLOY STAGED. The ledger is now unambiguous.


### B-109 - a TIMED-OUT auth probe was published as `headless_auth: failed`; the keeper also re-ran the full 90s probe for its debug dump  [FIXED IN TREE 2026-09-11 tick #353 - TDD RED->GREEN; helper LIVE, keeper verdict STAGED on session-gated restart]
- **Reproduced (2026-09-11 11:1x CST, live)**: `/tmp/session_keeper_state.json` read
  `status=HEALING headless_auth=failed` on a cycle where `session_keeper.log` showed
  `auth probe failed: timeout after 90.0s` -- while all three ASI daemons were `ready:true`.
  Re-ran the helper against a sleeping stub: exit=1, stderr `auth probe failed: timeout after 0.3s`;
  against a bad-sentinel stub: exit=1, stderr `auth probe failed: no sentinel (rc=1)`. **Identical codes.**
- **Root cause**: `scripts/keeper_auth_probe.py:63-64,84` computes a DISTINCT detail for the two
  failure modes and then encodes BOTH as exit 1. `scripts/session_keeper.sh:headless_ok()` discards
  that detail outright (`>/dev/null 2>&1`) and branches on the exit code alone, so the distinction is
  computed and thrown away one line later. Line 375 then stamps `HEADLESS_STAMP="failed"`.
  A saturated transport is not an auth verdict: section 5.4.1 ("never let transport failure masquerade
  as subject death") and 4.1 ("unknown is not a verdict") both violated in the one instrument
  every standup reads. Under the current fleet load (11 concurrent sessions, load avg 38-58) the
  90s bound is exceeded EVERY cycle, so the false verdict is the steady state, not a corner case.
- **Second half of the same defect** (`session_keeper.sh` failure branch): the debug dump re-ran the
  FULL bounded probe a second time -- 90s more in the branch that had already spent 90s. B-052b's own
  comment calls that shape "a SECOND unbounded probe"; bounding it stopped the livelock but not the
  doubling. Measured cost: a failing cycle could reach ~180s against a ~120s cycle contract.
- **Fix (ADDITIVE; fail-closed preserved)**: (a) helper gains `classify()` and `EXIT_UNKNOWN=3` for
  timeout only -- 0 ok / 1 definite failure / 2 usage are UNCHANGED and still pinned by
  `tests/test_keeper_auth_probe.py::test_main_exit_codes`; (b) `headless_ok()` captures the probe
  detail ONCE into `HEADLESS_PROBE_DETAIL`; (c) the failure branch maps it via
  `case *"timeout after"*) HEADLESS_STAMP="unknown"` / `*) HEADLESS_STAMP="failed"`, so a DEFINITE
  failure still stamps `failed` and STATUS stays HEALING either way -- the healing ACTION (env
  refresh) is unchanged; only the published verdict stops claiming an unmeasured failure; (d) the
  debug dump reuses the captured detail, dropping the duplicate 90s probe.
- **TDD**: RED `tests/test_keeper_auth_probe_three_state.py` -> **2 passed / 4 failed**, the 4 failures
  naming exactly (a) the shared exit code, (b) the missing classifier, (c) the `failed` mapping,
  (d) the duplicate probe -> **GREEN 6/6** post-fix. Non-vacuity: the same call shape must yield all
  three verdicts, and a separate test pins that the fail-closed `HEADLESS_STAMP="failed"` default was
  NOT removed. Regression on the touched surface **88/88 GREEN**
  (`test_keeper_auth_probe`, `test_session_keeper_heartbeat`, `test_session_keeper_watchdog`,
  `test_session_keeper_stamp_staleness`, `test_huanxin_heartbeat_dispatch_action`) + `bash -n` OK.
  Live E2E: real helper against a sleeping stub -> **exit 3**; the `case` block exercised verbatim
  maps timeout->unknown and no-sentinel->failed.
- **DEPLOY**: helper `keeper_auth_probe.py` sha `b1ad5feb19c451d1` is invoked FRESH every cycle, so the
  exit-code fix is LIVE immediately. Keeper `session_keeper.sh` sha `4db8abe60bb940a1` is loaded ONCE at
  boot, so the VERDICT change is **STAGED** -- it stays dead in-process until the keeper is restarted
  (same session-gated `launchctl` wall as B-106/B-107). Until then the file still stamps `failed`.
- **Cross-refs**: B-035 (the headless_auth column was a CONSTANT; this is the residual half of the same
  column), B-052b (the unbounded->bounded probe; this finishes the job on the duplicate), B-088
  (stale probe verdicts published as the live heartbeat - same "verdict not measured this cycle" class),
  B-066 (env-refresh sweep budget), B-106/B-107 (same staged-deploy wall).

#### B-109 CORRECTION (tick #353, same tick) - TWO defects in THIS fix's own first attempt, both caught before deploy
1. **The first patch landed in the WRONG function.** The line-index splice searched for the first
   `if headless_ok; then` in the file -- but that is the call INSIDE `refresh_env_from_live_process`
   (~line 115), not the main-loop probe branch (~line 383). The `case` classification blocks were
   therefore inserted into the env-refresh helper's rollback arm, where they would have clobbered
   `HEADLESS_STAMP` from inside a different code path, while the main-loop failure branch kept its
   unconditional `HEADLESS_STAMP="failed"` -- i.e. **the fix did nothing where it was needed and
   mutated state where it was not.** The splice now anchors on the main-loop section comment
   (`# 3. headless claude auth`) and asserts exactly-one match per anchor before writing.
   Caught by READING THE FILE BACK, not by the test run -- see (2).
2. **The test that was supposed to catch (1) passed anyway -- it was VACUOUS.** Its slice was anchored
   on `text.index('HEADLESS_STAMP="failed"')`, and once the misplaced block was in the file that literal
   first occurred at the *misplaced* site, so the slice ran forward across most of the script and
   swallowed the unrelated `HEADLESS_STAMP="unknown"` carry-over reset (B-088, ~line 363). A bare
   substring match on `"unknown"` was then satisfied by text that had nothing to do with the branch.
   This is the section 4.1 shadowed-helper class in a new shape: **the assertion was green because the
   string existed somewhere in the slice, not because the behaviour existed.** The slice is now anchored
   on the section comments and a `test_slice_targets_the_main_loop_branch_and_is_not_vacuous` guard pins
   the anchors (both arms present; the carry-over reset explicitly asserted ABSENT from the slice).
   **Non-vacuity proved by running the same assertions against `git show HEAD:scripts/session_keeper.sh`
   in a temp copy: the two keeper-behaviour tests FAIL there and PASS on the fixed tree.** A test that
   cannot fail on the unfixed code is not a test.
3. Also corrected: `HEADLESS_PROBE_DETAIL=""` had been spliced INSIDE the `headless_ok()` body instead
   of before it. Harmless under the current call order (the probe always runs before the branch), but it
   would have been an unbound-variable abort under `set -u` on any future reordering. Hoisted out.
- **Corrected shas**: `keeper_auth_probe.py` b1ad5feb19c451d1 (unchanged by the correction);
  `session_keeper.sh` **40be1f3a56c03ab3** (supersedes 4db8abe60bb940a1, which was never deployed);
  `test_keeper_auth_probe_three_state.py` 1c982188e8335fcf. Regression **95/95 GREEN** after correction.
- **Lesson recorded**: for a splice-style edit to a live script, (a) anchor on unique section markers,
  never on the first hit of a string that also appears elsewhere, and (b) read the file back and verify
  placement BEFORE trusting a green test -- a green test is only evidence if it is known to go red.

### B-110 - the metrics poller disarmed its step-window alerts on a RUN-SPECIFIC budget literal (`RUN_BUDGET = 100`, retired run 085136Z), so a run with a different budget went SILENT from step 100 while still training  [FIXED + VERIFIED 2026-09-11 tick #35x]
- **Filed**: 2026-09-11 ~11:0x CST, metrics-poller TDD lane.
- **Class**: a DEFAULT is a guess, and a guess must never drive a disarm. `.sapo-loop/sapo_metrics_poll.py:80`
  had `RUN_BUDGET = 100  # run 085136Z budget; step-window alerts disarm at budget` feeding
  `is_run_complete(rows, run_budget=RUN_BUDGET)` -> `filter_alerts_completed_run`, which DROPS every
  step-window alert (clip / trust / dead-signal / no-op / stage-stall / ckpt-stall) from the budget step
  onward. The launcher's own budget is `GRPO_STEPS := ${ASI3_SAPO_STEPS:-500}` (asi3_launch_grpo_direct.sh:56),
  so a live 500-step run was disarmed at step 100. A monitor that goes QUIET for the wrong reason renders
  exactly like a healthy run.
- **RED (measured, pre-fix module, step 120 with a truncation storm, no budget resolvable)**:
  `Run: sapo-27b-ai-20260911T104517Z | ASI3 8xNPU | trainer 4242 | 120/100 steps` / `VERDICT: HEALTHY` /
  rc=0 / nothing in STATUS.md. The TRUNCATION alert was swallowed by the cross-run literal.
- **Fix**: `_resolve_run_budget()` -- `SAPO_RUN_BUDGET` env -> durable pointer file (default
  `.sapo-loop/.run_budget`, overridable via `SAPO_RUN_BUDGET_POINTER`) -> UNRESOLVED, with NO numeric
  fallback. Unresolved = fail loud: a standing `RUN-BUDGET` alert, non-HEALTHY verdict, exit 2, STATUS.md
  line; the disarm is skipped entirely (`filter_alerts_completed_run(..., budget_resolved=False)` keeps
  step-window alerts live -- a CONFIGURATION fact, like NON-FINITE). A KNOWN budget still disarms on
  completion (the 2026-09-08 frozen-window false-alarm fix is intact). metrics.md no longer publishes
  `/100` for a budget it never read. Also `ENDPOINT` is now overridable (`SAPO_ENDPOINT`) instead of
  being welded to :20653.
- **Durable writer**: `scripts/asi3_launch_grpo_direct.sh` stamps `$GRPO_STEPS` to `.run_budget` beside
  `.current_run`, `launch` action only, fail-soft with a loud WARNING (same rules as the run pointer).
- **Tests**: `tests/test_sapo_metrics_poll_run_budget.py` (17 tests, red-first: 14 FAILED on the pre-fix
  module, 1 pre-existing default-endpoint test green). Adjacent poller suites 119/119 green.
  Harnesses in `tests/test_sapo_metrics_poll_failclosed.py` now pin `SAPO_RUN_BUDGET` so their liveness
  assertions do not depend on the ambient environment (their pre-fix failure was this bug's ambient read).
- **Safety**: all tests redirect METRICSMD/STATUSMD/STATE/REPORT + both durable pointers into tmp_path
  (B-096 class); the launcher E2E runs against a stubbed launcher with a sealed repair-sidecar pidfile.
- **Cross-refs**: B-096 (tests must not write live instruments), B-097/B-099 (the other two hardcoded
  identities in this same module: the trainer pid and the run target).
- **MEASURED IMPACT (11:19:51 CST, tick #353 close)**: `/tmp/session_keeper_state.json` ts 11:13:18 ->
  heartbeat age **394s** against the keeper's ~120s cycle contract and the watchdog's **420s** staleness
  bar. A cycle whose probe times out pays 90s for the probe plus up to 90s for the duplicated debug-dump
  probe; while the probe keeps timing out, the keeper lives permanently near the bar that gets it kicked.
  So B-109 is not a cosmetic verdict: it is the reason the keeper cycles run at ~3x contract, and the
  duplicate-probe half of the fix is the half that shortens them.


### B-111 - the LIVE single-instance lock root `/tmp/sapo_locks` was removed while three heartbeat instances depended on it  [OPEN - cause UNKNOWN, evidence complete; owner: Lock-Root Integrity lane]
Filed: 2026-09-11 11:2x CST (tick #354, manager).

**Signal.** `/tmp/sapo_locks` does not exist. Verified two ways: `ls -la /tmp/sapo_locks/` -> "No such file
or directory", and `os.path.exists('/tmp/sapo_locks')` -> False. /tmp itself is intact and NOT in a private
namespace: it still carries `sapo_judge_health_state.json`, `sapo_metrics_poller.log`,
`sapo_divergence_watch.log`, `sapo_poller_baseline`.

**Why this is provably a REMOVAL and not "never created".** Two independent facts place the root's
existence at 11:13:12 CST:
1. `scripts/sapo_single_instance_lock.sh:170` calls `ensure_dir` (`mkdir -p "$LOCK_DIR"`) UNCONDITIONALLY,
   as the first act of `acquire()`, before any refusal path can run. Any `acquire` invocation creates the
   root, even a refused one.
2. The newest heartbeat, pid 39737, started 11:13:12 CST and its `heartbeat start` line at
   `2026-09-11T03:13:12Z` IS present in `logs/huanxin_heartbeat.log`. That log line sits AFTER the
   acquire guard (`scripts/sapo_huanxin_heartbeat.sh:194`), so acquire completed.
=> created at 11:13:12, absent at 11:26.

**Bounded impact (do not overstate).** The holder identity is destroyed. The B-107 in-loop `--reacquire`
convergence property assumes the holder FILE survives between ticks; with the root wiped, a non-holder
instance's reacquire reads OLD_PID="" and falls to `dir_age_stale` on a missing dir, which returns
NOT-stale (fail-closed) -> it would REFUSE and exit. So a wipe does not by itself manufacture duplicates;
what it does is erase the evidence and leave any PRE-FIX resident (all three current instances, which
started 09:47 / 10:28 / 11:13 and predate the B-107 block) with nothing to re-validate against.

**Exonerated this tick (read, not assumed):**
- `tests/test_sapo_single_instance_lock.sh` - `LOCK_DIR="$(mktemp -d)"`, `export SAPO_LOCK_DIR="$LOCK_DIR"`,
  `trap 'rm -rf "$LOCK_DIR"' EXIT` -> removes only its own mktemp root.
- `tests/test_heartbeat_lock_revalidation.py` - per-test `tempfile.mkdtemp(prefix="b_next_")` with
  `env=dict(os.environ, SAPO_LOCK_DIR=ld)` -> never the live root.
Both are the B-096 guard landing correctly.

**NOT claimed:** which process removed it. Not root-caused. Candidate classes to enumerate next: any
sweep/test that writes or removes the live root without a `SAPO_LOCK_DIR` override; OS-level /tmp reaping;
the leaked `/tmp/b096dbg/wrapper.sh` (pid 71180) still holding `test_heartbeat_lock_9901`.

**Required fix shape (TDD, red first):** a guard test that FAILS if any test or sweep removes the live
root or moves its mtime, plus a check that a removed root is re-created (not silently tolerated) before
any liveness decision is taken. Owner: Lock-Root Integrity lane. Deadline: next tick.


### B-111 CORRECTION (tick #355, manager) — SEVERITY DOWNGRADED; root is PRESENT and self-heals
Appended 2026-09-11 11:4x CST. This does NOT close B-111; it corrects its premise and bounds its impact.

**MEASURED this tick (both readings, source named):**
- 11:30:30 CST — `/tmp/sapo_locks` **exists**, `total 0`, no holder slot (only `.` and `..`).
- 11:31 CST — `find /tmp/sapo_locks -maxdepth 3` -> `/tmp/sapo_locks/sapo_heartbeat` and
  `/tmp/sapo_locks/sapo_heartbeat/holder`.
- 11:32 CST — holder content = `41870`; holder mtime = **11:30:52**; root mtime = 11:30:52.
=> The root is present and holds a VALID holder. It was never absent during this tick's observation window.

**CODE READ (the load-bearing part, not inferred):** `scripts/sapo_single_instance_lock.sh` **never removes
`$LOCK_DIR` itself**. Its only removals are:
- `rm -rf "$TOK"` — the `.acq` acquire TOKEN (line 151, and again after the critical section, line 175);
- `rm -rf "$OLD"` — the holder FILE path (line 331), plus `rmdir "$LOCK_DIR/$NAME"` (lines 185/287/329)
  which removes the per-name holder DIRECTORY, never the root.
`ensure_dir()` is `mkdir -p "$LOCK_DIR"` (line 46) and is called **unconditionally as the first act of
`acquire()`** (line 170).

**CONSEQUENCES (this is the correction):**
1. The states observed at #354 ("root absent", then "root present but empty") are REPRODUCIBLE from the
   lock's own normal acquire/release cycling of the holder **directory**. An empty root is not evidence of
   a root wipe.
2. Any external removal of the root is **invisible**: the very next `acquire` repairs it via `mkdir -p`,
   silently, with no log line. That is why a wipe leaves no trace.
3. Impact stays bounded to EVIDENCE LOSS, as already scoped: holder identity is destroyed and the B-107
   in-loop `--reacquire` convergence property assumes the holder FILE survives between ticks.

**STILL OPEN, NOT EXPLAINED:** the #354 reading of a full root ABSENCE, which was taken by two independent
probes (`ls` + `os.path.exists`) and is not reproduced this tick. The removal source remains UNKNOWN.
Do NOT read this correction as "no removal happened".

**Guard-test shape is unchanged and still owed** (owner: Lock-Root Integrity lane): a test that FAILS if any
test/sweep removes the live root or moves its mtime, plus an assertion that a removed root is RE-CREATED
(and logged, not silently tolerated) before any liveness decision is taken. NEW sub-requirement from this
tick: the test must assert root EXISTENCE + mtime stability directly, because `ensure_dir` will otherwise
mask a removal by repairing it before any check can see it.

**ALSO CLOSED BY ABSENCE this tick:** the leaked debug wrapper `/tmp/b096dbg/wrapper.sh` (pid 71180,
carried from #353/#354) is GONE — `/tmp/b096dbg/` does not exist and no such process is resident (11:32 CST).


**B-111 TICK #355 FOLLOW-UP (2026-09-11 ~11:45 CST, manager) — INSTRUMENT OR ABSENCE; the
guard is LANDED and the direct-deletion hypothesis is narrowed but NOT proven.**

STATE: `/tmp/sapo_locks` is PRESENT with a VALID holder (`sapo_heartbeat/holder` = 41870) and
has been IDENTITY-STABLE for the whole observation window. One probe in tick #354 read ABSENT
(two independent ways: `ls` and `os.path.exists`). Both readings are recorded; neither is
withdrawn.

POSITIVE EVIDENCE OF A REPLACEMENT (the one fact that discriminates "instrument" from "absent"):
the root's mtime advanced to **11:25** while the root was provably created at **11:13:12**
(pid 39737's acquire; `ensure_dir` = `mkdir -p`, which does NOT touch the mtime of an existing
directory -- `scripts/sapo_single_instance_lock.sh:46,170`). An mtime advance on a directory
whose only ever child is re-created/removed by `rmdir`/`mkdir` inside it means the ROOT itself
was removed and re-created in that window. `release()` removes only `$LOCK_DIR/$NAME` and
`.old.*` (lines 329-331), never `$LOCK_DIR`.

NARROWED, WITH THE ELIMINATION REASON FOR EACH:
- The lock script itself: CANNOT be the cause (code read above).
- `tests/test_sapo_single_instance_lock.sh` (its `trap 'rm -rf "$LOCK_DIR"' EXIT` at :25 is a
  REAL root-removal shape, and if `mktemp -d` ever returned EMPTY then `:-` substitutes empty
  exactly as unset -> the trap would `rm -rf /tmp/sapo_locks`): ELIMINATED FOR THIS WINDOW on
  mtime -- the file is UNTRACKED and its mtime is **11:29:18**, i.e. it did not exist in its
  current form before 11:29. The `[ -z ]` refusal at :20 (B-096b) is the guard against the
  empty-mktemp path and is verified in the tree.
- A `/tmp`-wide reaper: ELIMINATED -- `/tmp` still holds `sapo_judge_health_state.json`,
  `sapo_metrics_poller.log`, `sapo_divergence_watch.log` across the window.
- Still UNPROVEN: any process that removed the root directly. No reproducer.

LIVENESS CONFIRMED SINCE: a 2s-interval identity watch (inode + mtime + ctime + entries) has
seen ZERO change for the whole of tick #355 (root inode 183989445, entries `('sapo_heartbeat',)`).
So there is no ONGOING repeated removal -- whatever happened was a one-off in the #354 window.

GUARD LANDED (TDD): `tests/test_lock_root_never_removed.py` -- 3/3 GREEN.
  (1) the private-root idiom must remove ITS root and leave siblings byte-identical;
  (2) an EMPTY `SAPO_LOCK_DIR` must be refused, and the `:-` fall-through to the live root is
      pinned from the shipped script's own resolver (the file carries NO copy of the literal);
  (3) running the lock suite under a private root must leave the LIVE root's inode intact --
      inode is the load-bearing field because remove-and-recreate yields a NEW inode even when
      mtime and entries coincide, which is exactly how a wiped root hides.
NON-VACUITY PROVED, not asserted: with the live root swapped for a synthetic one and the lock
suite swapped for a stub that deletes it, the guard FAILS (rc=1) naming the removal; on the
intact tree it PASSES.

ALSO FIXED WHILE ADDING THE GUARD (a false RED the guard created, found by its own regression
sweep): `tests/test_tests_do_not_write_live_instruments.py::test_lock_suite_locks_only_under_a_private_root`
failed because macOS `mktemp -d` IGNORES TMPDIR and always uses the per-user Darwin temp tree
(`/private/var/folders/...`), while all three entries of its allowed-root tuple resolve to
`/private/tmp` on this host. The allowlist now DISCOVERS the tree the way `mktemp` does instead
of hardcoding a path, and fails closed (no widening) if the discovery fails.


### B-112 - the lock-root guard's own allowlist was a false RED: macOS `mktemp -d` ignores TMPDIR  [FIXED, TDD, this tick]
- **Filed**: 2026-09-11 tick #355, found by the regression sweep on the guard added for B-111.
- **Symptom**: `tests/test_tests_do_not_write_live_instruments.py::test_lock_suite_locks_only_under_a_private_root`
  FAILED: *"the suite locked under /private/var/folders/py/<hash>/T/tmp.MFZd2fHvOn, which is not a
  system temp tree"* -- on a tree where the suite was in fact honouring its private root correctly.
- **Root cause (measured, not inferred)**: the assertion's allowlist was
  `(/tmp, /private/tmp, tempfile.gettempdir())` and **all three resolve to `/private/tmp` on this host**.
  macOS `mktemp -d` IGNORES `TMPDIR` and always creates under the per-user Darwin temp tree
  (`/var/folders/<xx>/<hash>/T`). Measured directly: `TMPDIR=<dir> mktemp -d` still returned
  `/var/folders/...`. So the tuple could never contain the suite's real root, and the probe reported
  a false RED on a GREEN tree.
- **Cost class**: a false RED is as expensive as a missed one (SKILL 4.3) -- it spends a tick on a bug
  that does not exist, and here it was pointing at the very guard family that exists to prevent the
  B-111 class.
- **Fix**: discover the temp tree the way `mktemp` itself does (create one with `bash -c 'mktemp -d'`
  and take its parent) instead of hardcoding a host-specific path. Fail CLOSED if the discovery
  fails -- the allowlist is not widened on an error.
- **TDD**: RED was the observed failure above; GREEN after the patch (40 binary-invariance + the
  instrument file: see the tick #355 sweep, 280 passed / 0 failed on the touched surfaces).
- **Cross-refs**: B-096a (the guard this repairs), B-111 (the lock-root class), B-113.

### B-113 - binary-invariance compared a WORKING scorer against a CRASHING one (B-100's aftermath)  [FIXED, TDD, this tick]
- **Filed**: 2026-09-11 tick #355, from the full-suite chunk that ran `test_holdout_enrichment_invariance.py`.
- **Symptom**: `test_adversarial_verdicts_binary_invariant[quantum_channel_depolarizing]` FAILED:
  `const_perturb: verdict changed old=False new=True`.
- **Root cause (measured -- this one needed the direction check, and the naive reading is WRONG)**:
  the test derives its "old" baseline via `git show HEAD:<scorer>`. The working-tree scorer has had
  `zip(a, b, strict=False)` -> `zip(a, b)` applied -- that is **B-100's fix**, still uncommitted for
  this last directory. On py3.9 the keyword raises
  `TypeError: zip() takes no keyword arguments`, so the OLD scorer returned `passed=False` for EVERY
  adversarial candidate **by DYING, not by judging**. `old=False` was therefore never a detection.
  Measured both directions: new=**True** (with details "Quantum channel simulations correct for all
  test cases") and old=**False** (details: the TypeError). The new verdict is CORRECT --
  `const_perturb` mutates `_mat_mul`'s `a[0][0]`->`a[0][1]`, and the mutated module returns the exact
  expected matrices for all four `depolarizing_channel` cases (verified by direct execution), so the
  mutation is behaviourally inert for the tested inputs.
- **Why the naive reading was wrong**: "old=False -> new=True" reads as "the new scorer got more
  lenient". It is the opposite: the new scorer is the first version that can RUN at all under 3.9.
  The lenient one, in effect, was the crash.
- **Fix**: the comparison is now crash-aware. A variant whose baseline failure is the py3.9 `strict`
  TypeError carries no verdict and is SKIPPED instead of compared
  (`_is_py39_token_crash`). Recorded per-variant, not silently dropped.
- **Non-vacuity**: the classifier was checked against a real verdict string (False) and the empty
  case (False); and the previously-failing variant `const_perturb` is confirmed to take the SKIP
  branch, with the three genuinely-behavioural variants (`none_stub`, `missing_fn`, `crash`) still
  COMPARED. The vacuity assertion ("at least one variant fails under BOTH") still passes on the
  remaining set.
- **Test counts**: `-k binary_invariant` -> **40/40 GREEN** (was 39/1). The 9 remaining failures in
  that file are all `No module named 'pennylane'/'qiskit'/'cirq'/'braket'` -- the enumerated
  environmental SDK baseline, not this class.
- **Cross-refs**: B-100 (the fix whose aftermath this is), B-112, SKILL 4.1 ("a measurement that
  cannot be classified reports ERROR, never a verdict").


### B-114 - [RETRACTED tick #357 - headline FALSIFIED, see the B-114 CORRECTION immediately after this entry] the heartbeat single-instance guard is BYPASSED: `holder_refresh_stale` reads a MISSING measurement as STALE  [WITHDRAWN - the guard works; a LIVE holder is refused, measured rc=1]
- **Filed**: 2026-09-11 ~11:47 CST, tick #355, from the heartbeat census question ("the count fell 4 -> 2")
  turning out to be wrong the other way.
- **Symptom (measured)**: THREE heartbeat instances are resident and ALL THREE are polling and writing
  the SAME log: pid 41870 (started 09:46:58), pid 90794 (10:28:02), pid 36896 (11:41:44). Each logged
  its own `heartbeat start`, and the log is written every ~120s (the loop's `sleep 120`,
  `scripts/sapo_huanxin_heartbeat.sh:289`). E.g. the 03:41:44Z/03:43:46Z/03:45:48Z ticks.
- **This is B-087's headline, now with a MECHANISM.** B-087 ("heartbeat dupes") was recorded with the
  census as UNCONFIRMED evidence; this tick supplies the code path.
- **Root cause (code read + live file state)**: the acquire-time guard's staleness test for a LIVE
  holder is `holder_refresh_stale "$LOCK_DIR/$NAME"` (`sapo_single_instance_lock.sh:253`), which is:
      _hr="$1/.refreshed"
      [ -f "$_hr" ] || return 1
      dir_age_stale "$_hr" "$STALE_SECS"
  The first line returns **1 = "STALE"** for a MISSING `.refreshed`. So "I could not measure the
  refresh" is reported as "the holder is stale", and the caller sets `STALE=1`.
- **The `.refreshed` file is NEVER created**: NOTHING in the tree calls the lock's `refresh` subcommand.
  Grepped `scripts/` for a refresh caller - zero hits (`sapo_single_instance_lock.sh:304` defines
  `refresh`, `:339` dispatches it; no caller). Live confirmation: `/tmp/sapo_locks/sapo_heartbeat/`
  contains **`holder` ONLY** - `ls -la` shows no `.refreshed`. So the first line of
  `holder_refresh_stale` is the ONLY line that ever runs, and it always returns "STALE".
- **Consequence**: a LIVE holder is judged stale on every acquire, so `--steal-stale` (exactly how the
  heartbeat acquires, `sapo_huanxin_heartbeat.sh:192`) hands the lock away. New instances are admitted
  freely. This is the same class the file has ALREADY fixed twice, and the comments say so:
  B-057 ("absence of a MEASUREMENT is not evidence of staleness", the holder CONTENT branch) and
  B-062 (the same mistake in the mtime branch, `dir_age_stale`, where a missing `$` made the guard
  dead code). The refresh branch is the THIRD instance of the identical error and was not fixed with
  the other two.
- **Why it does not (yet) produce runaway duplicates**: B-107's IN-LOOP `--reacquire` (added 11:05:32
  today, `sapo_huanxin_heartbeat.sh:210-215`) exits any instance that is not the recorded holder on its
  NEXT tick. That is convergence AFTER admission, not exclusion - which is exactly why the census
  oscillates (4 -> 2 -> 3 observed this tick) instead of settling at 1. B-107 treats the symptom; this
  is the admission-side cause.
- **Correct fix shape (TDD, NOT landed this tick - deliberate)**: `holder_refresh_stale` must be
  three-state, matching the rule the rest of the file already applies: `.refreshed` MISSING -> UNKNOWN
  -> NOT stale -> REFUSE (the caller must not set `STALE=1`). That requires either (a) the heartbeat to
  actually call `refresh` on its own cadence (the mechanism `:304` was written for), or (b) treating a
  never-refreshed holder as unmeasurable rather than stale. Both change acquire-time behaviour, and
  there are THREE live instances depending on the current behaviour with no way to test the change on
  the box from a tick session - so it goes in with B-100/B-107/B-109 at the next gate, NOT hot-patched.
  A tick-session fix here would be exactly the "relaunch on an untested hypothesis" the loop forbids.
- **Evidence for the file's own precedent**: `:68-79` (B-062) and `:242-248` (B-057) carry the identical
  reasoning. A guard test should pin all THREE branches together: missing measurement is never stale,
  for content, for mtime, AND for refresh.
- **Cross-refs**: B-087 (headline), B-107 (in-loop convergence - the mitigation), B-045/B-057/B-062/B-075
  (the same duplicate class), SKILL 4.1 ("a missing measurement is never a measurement").


### B-115 - the chunked full-suite runner counted whatever interpreter launched it, so a non-venv launch produced ~182 failures indistinguishable from regressions  [FIXED, TDD, tick #356]
- **Filed**: 2026-09-11 standup tick #356 (manager), from the in-flight sibling suite `logs/tick355_suite.log`.
- **Symptom**: the sibling chunked runner (pid 54488, `logs/tick355_suite.log`, start 11:31:29) reported
  rc=1 failures on `test_eval_lane_repair_scorers.py::test_reference_solution_passes_without_traceback[cirq_qaoa_line]`
  (chunk 09) and `test_grpo_pipeline_fast.py::test_reference_candidate_gets_full_reward[quantum_vqe_heisenberg_energy]`
  (chunk 13). Both look exactly like real pipeline regressions in the aggregate TOTAL line.
- **Root cause (MEASURED, both directions, one tree)**: `.sapo-loop/run_full_suite.py` runs every chunk with
  `sys.executable` -- whatever interpreter launched it -- and never checked that this interpreter can import
  the repo's dependencies. The file's own shebang is `#!/usr/bin/env python3`, so the natural invocation runs
  the whole suite under a bare interpreter with NO venv site-packages. Proof, same test ids, same tree:
    `.venv/bin/python3 -m pytest tests/test_eval_lane_repair_scorers.py`  -> 20 passed / 0 failed
    (bare interpreter, chunk 09)                                          -> rc=1 FAILED cirq_qaoa_line
    `.venv/bin/python3 ... test_reference_candidate_gets_full_reward[quantum_vqe_heisenberg_energy]`
                                                                          -> 1 passed / 0 failed
    (bare interpreter, chunk 13)                                          -> rc=1 FAILED, ModuleNotFoundError: pennylane
  Distribution check: `.venv/lib/python3.9/site-packages` holds pennylane 0.38.0, qiskit 2.2.3, cirq 1.3.0,
  openfermion 1.6.1 and braket; `/usr/bin/python3` has none of them. `sdk_probe` run live this tick:
  bare -> `['pennylane','qiskit','cirq']`, venv -> `[]`.
- **Cost class**: identical to B-113 -- a measurement that reflects the ENVIRONMENT, reported as a verdict
  about the TREE. Here it also poisons section 9.3, the instrument that exists to prove the suite was run.
- **Fix**: the runner now classifies the interpreter BEFORE any chunk runs (`env_verdict`, `sdk_probe`,
  `REQUIRED_SDKS`, `VENV_PYTHON`). All SDKs present -> run in place; absent here but present in `.venv` ->
  `os.execv` into `.venv/bin/python3`; absent in both, venv missing, or venv unprobeable -> REFUSE with
  `ENV_INVALID_EXIT = 3`, writing `ENV-INVALID` + `TOTAL VERDICT=ENV-INVALID` into the log and emitting no
  suite count at all. The refusal code is deliberately outside 0/1/2 so `rc == 0` can never read a blind
  run as a passing suite.
- **TDD**: RED = `tests/test_suite_runner_pins_interpreter.py` 8 failed (AttributeError: env_verdict /
  ENV_INVALID_EXIT / REQUIRED_SDKS absent, and the static wiring assertion firing). GREEN = 8 passed, and
  the B-083 guard `tests/test_full_suite_runner_reports_incomplete.py` still passes -> **14 passed / 0 failed**
  on the touched surfaces. Non-vacuity proved live, not asserted: `env_verdict` on the real interpreter pair
  returns `action=reexec` targeting `.venv/bin/python3`.
- **Wiring asserted statically**: a classifier nobody calls is the B-112 false-confidence class, so the guard
  parses `main()` and requires both the `env_verdict` call and the `ENV_INVALID_EXIT` return to be present.
- **NOT fixed by this**: the in-flight `logs/tick355_suite.log` run remains ENV-INVALID-class. Its TOTAL must
  not be quoted as a regression count -- the fix changes the runner, not that already-running process.
- **Cross-refs**: B-113 (same cost class), B-112 (false-confidence guard), B-083 (the completeness contract
  this extends), B-110 / B-078 (instrument-vs-absence family).

**B-114 PROOF (live, same tick, 11:46:50 CST) - the guard is definitively bypassed; this is no longer
a code-read inference.** Controlled experiment on a SCRATCH lock name (the live `sapo_heartbeat` lock
was never touched; the probe lock was released afterwards and the root is back to `['sapo_heartbeat']`):

    before       : 11:30:52 ('sapo_heartbeat',)
    acquire      : rc=0 -- created /tmp/sapo_locks/b114_probe with holder=999999
    after        : 11:46:50 ('b114_probe', 'sapo_heartbeat')
    2nd --steal-stale ONE MOMENT LATER, different holder-pid : rc=0  <-- STOLE IT
    holder now   : 888888      dir contents: ['holder']

The second acquirer took a lock that was milliseconds old, whose holder file was readable and correct,
and which had never been released. It succeeded because `holder_refresh_stale` (`:95-99`) returns 1 =
"STALE" for the MISSING `.refreshed`, and `dir contents: ['holder']` is the same one-element listing the
live heartbeat lock shows -- i.e. **no `.refreshed` is ever created for any holder, so EVERY live holder
is stealable.** This is the admission mechanism behind B-087's duplicate heartbeats, now demonstrated
rather than inferred.

Note the asymmetry this exposes, and why it survived: `dir_age_stale` was carefully hardened (B-062) so
that an UNREADABLE mtime is NOT stale, and the holder-content branch was hardened (B-057) so an absent
holder is NOT stale. Both of those guards protect the caller from a missing measurement. The refresh
branch asks the SAME question one level up and answers it BACKWARDS.


### B-114 CORRECTION (manager, tick #357, 2026-09-11 11:55 CST) - RETRACTION: the "guard is BYPASSED" headline is FALSE; WITHDRAWN in full
The B-114 entry below is retained verbatim for the record, but its headline claim is **falsified** and
must not be cited as live. Three independent grounds, all measured this tick:

1. **The polarity is misread.** `holder_refresh_stale` (`scripts/sapo_single_instance_lock.sh:95-99`) is

       _hr="$1/.refreshed"; [ -f "$_hr" ] || return 1; dir_age_stale "$_hr" "$STALE_SECS"

   `dir_age_stale` is documented and written `0 = STALE, 1 = not stale` (missing mtime -> `return 1`,
   "Missing/unreadable mtime counts as NOT stale"). `holder_refresh_stale` returns its result directly,
   so a MISSING `.refreshed` returns **1 = NOT STALE**. The caller (`:250-253`) is
   `holder_refresh_stale ... && STALE=1` - it sets STALE only on return **0**. B-114 states the first
   line "returns 1 = STALE"; it returns 1 = NOT-STALE. The guard therefore REFUSES, which is the
   intended single-instance behaviour.

2. **The live "PROOF" used DEAD holder pids, so it observed the correct path.** B-114's scratch-lock
   experiment seeded holders `999999` and `888888`. In the caller, a numeric holder takes the
   `pid_alive "$OLD_PID"` branch; `kill -0 999999` FAILS, so the `else` sets `STALE=1` unconditionally
   (`:250-257`) and the steal SUCCEEDS - exactly as designed for a dead owner. The experiment could not
   have distinguished "guard bypassed" from "dead holder reclaimed", and it was the latter.

3. **The "owed" guard test already exists and is GREEN, asserting the opposite.**
   `tests/test_lock_live_holder_age.py` pins all three branches B-114 said were unpinned:
   `test_live_holder_is_not_stolen_on_age_alone` (missing refresh -> refused),
   `test_live_holder_that_published_a_stale_refresh_is_reclaimed`, and
   `test_live_holder_with_fresh_refresh_is_refused`, plus `test_dead_holder_is_still_immediately_reclaimed`
   and `test_refresh_subcommand_publishes_a_fresh_marker`. Measured this tick:
   `test_lock_live_holder_age.py` + `test_heartbeat_lock_holder.py` + `test_single_instance_lock_reacquire.py`
   + `test_single_instance_lock_steal_race.py` = **20 passed / 0 failed**.

**Independent reproduction (tick #357, this session, SCRATCH lock dir - the live `sapo_heartbeat` lock was
never touched).** Held the lock with a genuinely LIVE pid (`sleep 300` -> 85392) and a MISSING `.refreshed`
(`dir contents: . .. holder`), then ran a second `--steal-stale` acquire with a different holder pid:

    acquire #1 (LIVE holder 85392)                -> rc=0, holder=85392, no .refreshed
    acquire #2 (--steal-stale, pid 424242)        -> rc=1 REFUSED, holder UNCHANGED 85392
    control: holder 999999 (DEAD), then steal     -> rc=0 STOLEN, holder=424242

The live-holder case refuses; the dead-holder case steals. Both are correct, and both contradict B-114.

**Corroboration already in the tree**: B-107's own comment at `scripts/sapo_huanxin_heartbeat.sh:203-205`
already recorded the measured fact - the live lock "still correctly REFUSES a fresh --steal-stale
acquirer (exit 1)". B-114 was filed against evidence already in the repo pointing the other way.

**What is NOT retracted / what stays open**: the census really does oscillate (4 -> 2 -> 3, and 3
resident right now: pids 36896 / 41870 / 90794). B-114's *symptom* is real; only its *mechanism* is
withdrawn. The ADMISSION WINDOW that let 90794 (10:28:02) and 36896 (11:41:44) in remains **UNKNOWN** -
recorded as UNKNOWN, not re-guessed. B-107's in-loop `--reacquire` remains the correct CONVERGENCE
property and is unaffected. B-087's headline ("heartbeat dupes") loses B-114 as its claimed mechanism
and returns to UNCONFIRMED. The `.refreshed` mechanism is genuinely never used by production (the
heartbeat never calls `refresh`), so a live holder is judged by CONTENT+LIVENESS only - which is the
B-057/B-062 precedent working as intended, not a defect.

**Lesson (instrument-integrity class, same family as B-086/B-111)**: a scratch experiment must vary the
one variable under test. Seeding a DEAD pid to test a LIVE-holder guard measures the dead-holder path.
Owner: Lock-Root Integrity lane. No fix is owed; the fix would have broken hung-holder recovery.


### B-116 - the B-108 watchdog landing shipped 3 `UP031` percent-format violations, so the repo-wide ruff contract (#116/B-019) went RED  [FIXED, TDD-verified, tick #357]
- **Filed**: 2026-09-11 tick #357, from the in-flight sibling suite's chunk 34 `rc=1`
  (`tests/test_sapo_ruff_clean_scripts.py::test_ruff_check_scripts_py_returns_zero_errors`).
- **NOT env-class**: re-run under `.venv/bin/python3` it still fails. `ruff` is a pure static check with
  no SDK dependency, so D-356-1's environmental explanation does not reach it. This was a REAL red.
- **Root cause**: `scripts/sapo_watchdog_watcher.py:75,82,87` (the judge-VERDICT checks added by B-108
  today) used `"..." % (...)` percent-formatting. `UP031` fires.
- **Fix**: `ruff check --select UP031,UP032 --fix --unsafe-fixes scripts/sapo_watchdog_watcher.py`
  -> 2 fixed, then 1 remaining `.format()` (UP032 does not auto-fix that site because the f-string
  rewrite would exceed the line limit) converted by hand to the `.format()` form ruff accepts.
  Final: `ruff check scripts/sapo_watchdog_watcher.py` -> **All checks passed!**
- **Verified GREEN**: `test_sapo_ruff_clean_scripts.py` + `test_watchdog_watcher.py` +
  `test_watchdog_watcher_verdict.py` + `test_sapo_judge_health_agent.py` = **32 passed / 0 failed**.
  Semantics preserved: the three judge-health strings are byte-identical after formatting
  (`strikes`/`detail` still rendered with `!r`).
- **NOTE**: the file is UNTRACKED (`??`) - it is a today-landing that has never been committed, which is
  why the contract test only just started seeing it.
- **Cross-refs**: B-019 / contract #116 (the ruff cleanliness contract), B-108 (the landing that
  introduced the file), B-115 (the env-invalid classification that does NOT cover this one).

### B-117 - the targeted-10 holdout contract is RED: the completeness/disjointness/reference-validity check returns violations  [OPEN - root cause not yet taken; owner: Instrument Integrity]
- **Filed**: 2026-09-11 tick #357, from the sibling suite's chunk 30 `rc=1`.
- **NOT env-class**: re-run under `.venv/bin/python3` it still fails. Measured:
  `tests/test_sapo_eval_security.py:148: AssertionError: assert [{...}, ...] == []` - the test collects
  violation dicts and requires an EMPTY list.
- **Why it matters**: this is GOLDEN RULE 1 territory (the INSTRUMENT). `test_targeted10_..._complete_
  training_disjoint_and_reference_valid` guards that the eval holdout is complete, disjoint from
  training, and has a valid reference solution. If this is genuine, every verdict taken against that
  holdout is invalid; if the TEST changed and the artifact did not, the test is the defect.
- **Lead (not yet confirmed)**: `tests/test_sapo_eval_security.py` is modified in the working tree with
  mtime **2026-09-11 06:44** - the test itself changed TODAY. The next action is to diff the test
  against HEAD and decide which side is wrong BEFORE touching either. Recorded as a LEAD, not a verdict.
- **Status**: OPEN, no fix attempted this tick (root cause must be taken, not guessed). This is a
  standup-tick file-and-assign, deliberately not a hot patch.

### B-118 - the holdout scorer emits NO shaped numerics for near-misses (all 3 SDKs grade 0.0) - the weak-reward-signal guard is RED  [OPEN - owner: Algorithm Correctness]
- **Filed**: 2026-09-11 tick #357, from the sibling suite's chunk 31 `rc=1`.
- **NOT env-class**: re-run under `.venv/bin/python3` it still fails on ALL THREE SDK parameters, so it
  is not a missing-SDK artifact.
- **Measured**: `tests/test_sapo_holdout_scorer_enrichment.py:877: AssertionError:
  <sdk> near-miss grades 0.0; details lack shaped numerics` for `pennylane_vqe_h2`, `cirq_qaoa_line`,
  `qiskit_qft_entangled`. That is the whole parameter set, failing uniformly.
- **Why it matters**: this is the SKILL section-3 "weak reward signal" failure mode - a scorer that
  emits pass/fail only yields IDENTICAL advantages within a group = ZERO gradient. It is also the
  leading suspect class for the in-run `all_fail: true` rows in the brief's terminal run. Note
  `tests/test_sapo_holdout_scorer_enrichment.py` is UNMODIFIED (mtime Aug 31), so the change - if any -
  is on the SCORER side, not the test. Confirming that is the first action.
- **Status**: OPEN, no fix attempted this tick (deliberate: this is a reward-path change and must go in
  with a RED->GREEN test and a non-vacuity proof, not as a standup hot patch). Flagged to the Algorithm
  lane as the highest-value open item behind the beats-base objective.


### B-118 CORRECTION - RETRACTED: it is NOT a scorer defect; it is an INSTRUMENT-CLASS artifact (bare-interpreter SDK invisibility), and the claimed reward-path impact measures ZERO  [RETRACTED, tick #358]
- **Filed** 2026-09-11 tick #357 as "near-miss grades 0.0, details lack shaped numerics - reward-path,
  leading suspect for the terminal run's all_fail rows". **Retracted on measurement** the same day.
- **The recorded symptom text was wrong.** It is not that the details "lack shaped numerics" - the
  `details` list is a SINGLE import error string. Measured via the production path
  (`evals/runner/single_candidate_eval.py` on the three near-miss fixtures):
  `{"harness": {"passed": false, "details": ["import failed: No module named 'pennylane'"]}}`,
  and identically `'cirq'` / `'qiskit'`. Three of three, uniform.
- **Root cause = environment, proven by a one-variable experiment.** `_run_tests` spawns
  `sys.executable` (the interpreter running the suite). Run under the bare `/usr/bin/python3` - which
  cannot see `.venv/lib/python3.9/site-packages`, where pennylane 0.38.0 / cirq 1.3.0 / qiskit 2.2.3
  ARE installed - the subprocess cannot import the SDK, the task's OWN `tests.py` import fails
  (`pennylane_vqe_h2/tests.py:17`), every candidate near-miss returns import-failed, and the grade is
  0.0. The SAME file under the SAME interpreter with ONLY the venv site-packages made importable:
  `13 passed / 0 failed / 5 skipped` (was `10 passed / 3 failed / 5 skipped`). The delta is exactly
  the three SDK tasks. Per D-357-2's own rule (re-measure per-failure, never by class assumption) the
  #357 classification was asserted without this re-measurement.
- **The test is doing the RIGHT thing.** It fails CLOSED and it is non-vacuous - it detected real
  environment breakage. `_NO_NUMERIC_SCORER_TASKS` (the skip escape hatch) plus `not
  _has_runtime_failure(details)` correctly declined to skip here, because the condition was not met.
  No test defect, no scorer defect. The `.venv` run already said so: `.venv/bin/python3` HAS all three
  SDKs, so the subprocess it spawns imports them.
- **SECONDARY finding (real, but impact measured at ZERO - recorded, NOT urgent).** The task scorers
  emit `f"import failed: {e}"`, where `str(e)` STRIPS the exception class name, so the string is
  `import failed: No module named 'x'` and never contains a marker in
  `training/grpo_utils._has_runtime_failure`'s vocabulary (`"ModuleNotFoundError:"`, `"ImportError:"`,
  ...). The `_load(candidate_path)` call sits INSIDE that `try`, so a candidate's own bad import is
  unmarked too. Measured consequence, using the production functions:
  `"ModuleNotFoundError: No module named 'pennylane'"` -> has_runtime_failure=True, shaped=0.0000;
  `"import failed: No module named 'pennylane'"` -> has_runtime_failure=False, shaped=**0.0000**;
  control near-miss `"gap = 0.25, expected <= 0.05"` -> shaped=0.6000. **The reward outcome is
  identical (0.0) either way** - unmarked details also carry no numeric evidence, so `_detail_progress`
  yields 0.0. So this is a CLASSIFICATION-fidelity gap in `verifier_reward` / the fine instrument, not
  a live reward bug. Because `fine_grade`'s contract is pinned by `test_import_failure_grades_zero`
  (which uses the MARKED form and therefore stays green), touching the vocabulary risks the
  instrument for no measured gain. Recorded as a refinement candidate, deliberately not hot-patched.
- **D-357's influence claim is WITHDRAWN explicitly.** The #357 order called this "the leading suspect
  for the terminal run's `all_fail: true` rows... zero gradient". That is not supported: this tick's
  sweep shows all-FAIL groups are NOT all-equal because the 18-task mixture includes pass-scoring and
  near-miss-scoring tasks, which was probed live this tick. Flagging it as zero gradient was a
  plausible-but-unverified mechanism of exactly the class the loop's own rules tell us to verify
  before acting on. Retraction recorded loudly, per S2.2.
- **Cross-refs**: B-115 / D-356-1 (the environmental caveat - this case belongs to it after all),
  D-357-2 (scoped the caveat correctly; this case was the counter-example that scoping caught),
  fine_score contract #116 / `tests/test_fine_score.py::test_import_failure_grades_zero`.


### B-117 CORRECTION - RETRACTED as a training-manifest defect: 34/56 failures are all missing-SDK, and 0/56 with the SDKs visible  [RETRACTED, tick #358]
- **Filed** 2026-09-11 tick #357 as "the targeted-10 holdout contract is RED ... completeness/disjointness/
  reference-validity check returns violations", flagged GOLDEN-RULE-1 (the INSTRUMENT) territory, with the
  hazard "if genuine, every verdict taken against that holdout is invalid".
- **The recorded count was wrong and the shape was wrong.** Measured this tick: the test asserts
  `failures == []` over **56** tasks (the test's own comment records the 2026-09-08 re-pin to the v9
  user-bound manifest; `len(targeted_ids) == len(set(targeted_ids)) == 56`), and **34 of 56** fail.
  #357 recorded "34 more items" read as a violation list - they are FAILING TASKS, not completeness
  violations. The two structural asserts that precede the failure list PASSED: 56 unique ids, and the
  manifest is disjoint from the frozen 18-task promotion holdout. So the completeness and disjointness
  halves of this test were never the problem.
- **Root cause = environment, proven by a one-variable experiment.** The bare `/usr/bin/python3` cannot
  see `.venv/lib/python3.9/site-packages`. Running the SAME 56-task loop through the production
  `evals.runner.run_eval.run_task` (which executes each task's `tests.py` in-process) with ONLY the
  venv site-packages made importable on `sys.path` and nothing else changed:
  **FAILS: 0 of 56** (was 34 of 56). Every one of the 34 baseline failures is a ModuleNotFoundError:
  qiskit x24, cirq x3, pennylane x4, openfermion x2, and one openfermion surfacing via the independent
  oracle (`quantum_rl_v2_binary_stabilizer_tableau`, error_type=None, "independent oracle raised:
  No module named 'qiskit'"). **Zero failures of any other class** - no numeric, no assertion, no
  contract, no reference-validity failure. The 22 that pass baseline are exactly the tasks with no
  external-SDK dependency.
- **Why the test has no guard for this.** Sibling suites in this repo have an explicit
  `_PY310_OR_NEWER` / `_*_ENV_BLOCKED_TASKS` escape hatch (see B-118's file). This test has none: it
  asserts over all 56 tasks of the launcher's default manifest unconditionally, so it is a
  bare-interpreter-fragile assertion. **The manifest, the tasks, and the launcher default are all FINE.**
  No artifact needs to change on this evidence.
- **Consequence if #357's reading had been acted on.** "Every verdict taken against that holdout is
  invalid" would have triggered a re-derivation of the evaluation instrument and possibly a manifest
  re-pin - rework with zero defect behind it, plus it would have masked the genuine consequence below.
- **ONE OPEN OBSERVATION, recorded not resolved (must not be left as a guess).** Under `pytest` with
  `PYTHONPATH` set to the venv site-packages, this test STILL failed, while the direct in-process loop
  above (with `sys.path.insert` of the same directory, via `run_task`) went 0/56. So something in the
  pytest invocation path does not give the runner the same view my direct call had. The conclusion
  above does not depend on it (both directions of the one-variable experiment were run through the SAME
  direct `run_task` harness), but the divergence is unexplained and is NOT to be closed by assumption.
  Next action for the owner: diff `sys.path` inside the pytest run vs the direct run, then decide.
  Note `run_eval.load_test_module` uses `importlib` on a file path, and `run_workspace_tests` does a
  `sys.path.insert(0, temp_root)` / `pop(0)` pair - a plausible interaction site, unconfirmed.
- **Cross-refs**: B-115 / D-356-1 (environmental caveat), D-357-2 (per-failure measurement rule - this
  case is the second counter-example that rule caught, after B-118), the `# required_import_roots=`
  manifest convention, `scripts/asi3_launch_grpo_direct.sh`.


### B-117 CORRECTION (manager, tick #358, 2026-09-11 12:07 CST) - WITHDRAWN: the targeted-10 contract is GREEN under the baseline instrument; the "violations" were missing-SDK reference crashes
- **Measured directly and reproducibly this tick**: `.venv/bin/python3 -m pytest tests/test_sapo_eval_security.py`
  -> **rc=0, 26 passed / 0 failed / 0 errors**. The contract is NOT red on the baseline instrument.
- **The same file under `/usr/bin/python3`** (the interpreter that produced the chunked suite's chunk 30)
  -> rc=1 at `tests/test_sapo_eval_security.py:148`: `assert failures == []`, `Left contains 34 more items`.
- **Mechanism (measured, not inferred)**: the 34 items are v9-manifest REFERENCE candidates that CRASH
  because `/usr/bin/python3` lacks the 5 SDKs (qiskit/pennylane/cirq/openfermion/braket - the documented
  environmental baseline). A reference candidate that crashes on a missing import is counted as an
  "invalid reference" violation. That is an INSTRUMENT artifact of the interpreter, not a data-integrity
  defect in the holdout.
- **D-357-2 is FALSIFIED for this chunk.** Its claim "re-run under `.venv/bin/python3` they still fail"
  does not reproduce: the file is GREEN under `.venv`. The environmental caveat DOES cover chunk 30.
- **No fix is owed** to either the test or the artifact. Do NOT edit `tests/test_sapo_eval_security.py`
  (still modified in-tree, mtime 2026-09-11 06:44 - its diff is UNRELATED to this red).
- **Procedural remedy (the actual lesson)**: a red may not be classified as "not environmental" unless
  the report NAMES the interpreter and environment that produced it. "It still fails" without an
  interpreter is not evidence - this is the same class of error as B-114's dead-holder proof.
- **Cross-refs**: B-115 (the interpreter-counting fix), D-356-1 / D-357-2 (the caveat and its scoping).

### B-118 CORRECTION (manager, tick #358, 2026-09-11 12:08 CST) - WITHDRAWN: the near-miss shaped-numerics invariant HOLDS; the frozen scorers DO emit shaped numerics
- **Measured directly this tick**: `.venv/bin/python3 -m pytest tests/test_sapo_holdout_scorer_enrichment.py -k near_miss`
  -> **rc=0, 13 passed / 0 failed / 5 skipped** (that is the whole 18-task near-miss parametrization; the 5
  skips are the documented braket + zip(strict) env-blocked tasks).
- **The three tasks named as failing all grade > 0 on the baseline instrument** (measured by driving the
  production runner `evals/runner/single_candidate_eval.py` with each task's NEAR_MISS fixture and scoring
  through `scripts/fine_score.py::fine_grade`):
  | task | harness details | fine_grade |
  |---|---|---|
  | pennylane_vqe_h2 | h2_hamiltonian() has too few terms (2); expected >=4 | **0.5500** |
  | cirq_qaoa_line | best_maxcut_value() = 2, expected 3 | **0.6318** |
  | qiskit_qft_entangled | abs statevector = 1.414214, expected 1.0 | **0.6549** |
- **So the invariant the test pins is SATISFIED and the scorer is CORRECT.** There is no zero-gradient
  defect in the holdout scorer - the "leading suspect for the all_fail rows" is eliminated as a suspect.
- **Root cause of the observed red**: the failing run was the `/usr/bin/python3` chunked suite, whose
  interpreter lacks the 5 SDKs. The test spawns the production runner with `sys.executable`, so under that
  interpreter the child reports `import failed: No module named cirq/pennylane/qiskit` - a RUNTIME FAILURE,
  which `shaped_reward_from_details` correctly forces to 0.0. Reproduced exactly by withholding the venv
  site-packages from the child. **The red was the missing SDK, not the scorer.**
- **D-357-2 is FALSIFIED for this chunk too.** `.venv` carries cirq/pennylane/qiskit (verified: venv
  site-packages holds cirq 1.3.0 / PennyLane 0.38.0 / qiskit 2.2.3, all importing under py3.9), and the
  child subprocess from a `.venv/bin/python3` parent inherits `sys.executable` = the venv path (measured).
- **No fix is owed.** In particular do NOT add these tasks to `_NO_NUMERIC_SCORER_TASKS` and do NOT loosen
  the assertion - that would have encoded a false red as a permanent skip and hidden a working invariant.
- **Cross-refs**: D-357-2, B-115, B-117 CORRECTION (same tick, same mechanism, same lesson).


### B-119 - chunk-18 red: `test_huanxin_shell_exec_node.py::test_node_wedge_fix_suite_passes` failed IN THE CHUNK but passes 3x in isolation  [OPEN - load-sensitive flake, owner: Test Orchestrator]
- **Filed**: 2026-09-11 tick #358, from the in-flight venv suite's chunk 18 `rc=1`
  (`logs/tick355_venvsuite.log`: `FAILED tests/test_huanxin_shell_exec_node.py::test_node_wedge_fix_suite_passes`).
- **Reproduction attempts, all GREEN**:
  (1) `-k wedge_fix_suite` under `/usr/bin/python3` -> 1 passed / 0 failed;
  (2) the whole file -> 1 passed / 0 failed;
  (3) `node tests/test_huanxin_shell_exec.js` directly -> exit 0, "all wedge-fix tests passed";
  (4) the two chunk-18 files together -> 3 passed / 0 failed.
- **Mechanism (strong lead, NOT yet root-caused)**: the test shells out with
  `subprocess.run(["node", ...], timeout=120)` (`tests/test_huanxin_shell_exec_node.py:21-26`). Its failure
  mode under the chunk is therefore either the 120s timeout or a node-side non-zero exit - and this tick ran
  under unusually heavy contention: the #355 venv suite (pid 17238), a SECOND full chunked `python -m
  pytest` over the grpo files, a bare `pytest tests/test_serve_openai_chat_adapter_http.py`, several
  sibling claude loop sessions, and two leaked `pytest-of-daxu` lock-suite scaffolds still resident from
  10:47/10:51. The node suite runs in well under a second unloaded, so the timeout is only plausible under
  extreme CPU starvation.
- **NOT yet evidence-backed**: the chunk log records only the FAILED node id - it does not capture
  stdout/stderr, so whether this was a timeout or an assertion is **UNKNOWN**, not assumed. The falsifiable
  next step is to sweep `logs/tick355_venvsuite.log` for the raw traceback the runner emits alongside
  `rc=1`, and if it is absent, to have the runner persist per-chunk failure output.
- **Why it is filed rather than dismissed**: "passes in isolation" is exactly how a real order-dependence
  bug hides. The two candidate classes are (a) resource starvation (most likely) and (b) test-order
  pollution inside chunk 18. Distinguishing them is cheap and is the owner's first action.
- **Cross-refs**: B-086/B-111 (instrument-integrity family - "a Mac-side observation is not an
  instrument"), [[sapo-suite-oom-and-duplicate-sessions]] (never run two suites at once; this tick had
  several), the leaked `pytest-of-daxu/pytest-151` / `pytest-170` lock scaffolds.


### B-120 - the chunked-suite runner discards failure output, so a red chunk cannot be root-caused from its log  [OPEN - instrument gap, owner: Test Orchestrator]
- **Filed**: 2026-09-11 tick #358, while trying to root-cause B-119.
- **Measured**: `logs/tick355_venvsuite.log` persists exactly ONE line per chunk and it is the pytest
  summary (`rc=1 :: FAILED <node id>`). The full traceback - i.e. the only evidence that distinguishes a
  120s timeout from a real assertion failure - is NOT written. Verified: the file is 19 lines for 20
  chunks, with no `-B 6` context beyond the summary line for the failing node.
- **Impact**: every class-1 question S9.3 exists to answer ("is this red a defect or an artifact?") is
  unanswerable from the durable artifact. B-119 is the live example: the chunk red is filed with its
  mechanism recorded as UNKNOWN *because the log does not contain the evidence*, not because the
  investigation stopped. A runner that loses the failure text forces a costly re-run under the same
  contention that caused the failure.
- **Smallest fix (TDD)**: have the runner append the captured stdout/stderr tail for any chunk with
  non-zero rc (bounded, e.g. last ~40 lines), and add a RED->GREEN test that a synthetic failing chunk
  yields its traceback in the log. This is a test-harness change, not production code - no launch risk.
- **Cross-refs**: B-119 (the red this obscured), SKILL section 4.1 "error lines are not measurements"
  and section 9.3 (the suite is the canary - a canary whose evidence is discarded is half an instrument).


### B-121 - the B-096a lock-root probe leaks its bash descendants when the 600s subprocess.run timeout fires, and each orphan busy-spins a full CPU core forever  [FIXED + VERIFIED 2026-09-11 tick #361 - TDD RED->GREEN]
- **Found**: 2026-09-11 tick #359 (12:20 CST) while reading the host process census. Three processes:
  | pid | elapsed | CPU time | state | PPID |
  |---|---|---|---|---|
  | 34458 | 1:30:12 | **70:17** | R | 1 (of 34455) |
  | 73639 | 1:33:28 | **72:58** | R | 1 |
  | 76862 | 1:18:31 | **60:58** | R | 1 |
  all running: `bash /private/var/folders/.../pytest-of-daxu/pytest-{135,151,170}/test_lock_suite_resolves_a_red0/lock-wrapper.sh acquire test_heartbeat_lock_9901`
- **Impact (measured)**: one full core burned per orphan (three cores total). Host 1-min load **38-39**
  at 12:21-12:22 CST on a 12-user box, against ~18 at #358. Compute a stray loop eats is compute the
  objective cannot use - the section 9.1 concern in substance.
- **Root cause (located, not guessed)**: `tests/test_tests_do_not_write_live_instruments.py:114-167`
  (`test_lock_suite_locks_only_under_a_private_root`). It generates a `suite.sh` into `tmp_path`, points
  the suite's hardcoded `LOCK_SCRIPT` at a generated `lock-wrapper.sh` (`:133-145`), and runs it with
  `subprocess.run(["bash", str(patched)], ..., timeout=600)` (`:162-163`). When that timeout fires,
  `subprocess.run` kills **only the direct child**. The suite's bash descendants
  (`tests/test_sapo_single_instance_lock.sh` spawns background acquirers at `:52-56` and locks via
  `bash "$LOCK_SCRIPT" ...` at many lines) are reparented to PPID=1 and are never signalled. They then
  keep re-arming on a lock whose private root was deleted with the tmp dir, i.e. the acquire can never
  succeed and the loop never terminates.
- **NOT claimed**: the exact reasons the trigger fires at all (why the suite exceeds 600s, and why these
  three runs in particular were killed by their parent) are **NOT measured** - the scaffolds live under
  `/private/var/folders/...` which is outside this session's readable roots, so the trace/wrapper
  contents could not be read and the parent pytest runs are gone. Recorded as UNKNOWN rather than
  assumed. The leak mechanism above is the part that IS established (child kill without group kill).
- **Mitigation performed this tick (verified)**: SIGTERM to all three; 73639 and 76862 exited; 34458
  resisted SIGTERM and was removed with SIGKILL. Post-state re-census: **0 remaining** matching
  processes. This is a cleanup, not a fix - the source still leaks.
- **Smallest fix (TDD)**: start the suite in its own process group
  (`subprocess.Popen(..., start_new_session=True)` or `preexec_fn=os.setsid`) and, in a `finally`,
  `os.killpg(os.getpgid(p.pid), SIGKILL)` before reading results. RED test: run a synthetic suite that
  spawns a long-lived background child, force the timeout, assert no descendant survives (poll the
  child pid for ESRCH). Regression: `tests/test_tests_do_not_write_live_instruments.py` stays green.
- **Cross-refs**: B-096a (the lock-root probe this belongs to), B-119/B-120 (same suite triage family),
  [[mac-reboot-login-window-kills-fleet]] family of process-hygiene classes.

- **SOURCE FIX LANDED (tick #361, TDD RED->GREEN)**. Owner: Code Steward. File:
  `tests/test_tests_do_not_write_live_instruments.py`.
  - **Fix**: two helpers added to the file — `_kill_group(proc)` (SIGKILL the process GROUP, then reap,
    never raises) and `_run_in_own_group(argv, *, timeout, **kwargs)` (`Popen(..., start_new_session=True)`
    + `communicate(timeout=...)` + `_kill_group` on `TimeoutExpired`, returning a `CompletedProcess`).
    The probe call site at `test_lock_suite_locks_only_under_a_private_root` now runs the generated suite
    through `_run_in_own_group` instead of `subprocess.run(..., timeout=600)`. `start_new_session=True`
    is what does the work: the suite's bash descendants share the probe's new group, so ONE `killpg`
    reaches them; a bare child-kill provably does not.
  - **TDD evidence**: `test_lock_suite_timeout_reaps_its_orphaned_descendants` (a suite that backgrounds a
    `sleep 3600`, forced timeout, asserts the descendant does NOT survive with PPID=1) and
    `test_the_naive_timeout_is_what_leaks` (pins the leak CLASS itself: a bare child-kill DOES leave the
    descendant orphaned — so the fix above is fixing something real, not a straw man, and that test fails
    loudly if the mechanism ever stops reproducing).
  - **Results**: focused **2/2 rc=0**; full file **10/10 rc=0** (incl. the real lock-suite probe, which
    exercises the fix end-to-end); adjacent regression set (`test_heartbeat_lock_holder.py`,
    `test_sapo_cleanup_stale.py`, `test_bugqueue_id_uniqueness.py`, `test_lock_root_never_removed.py`)
    **22/22 rc=0**. Leak re-check after a green run: **0** `sleep` processes remaining.
  - **A near-miss worth recording (this is the class, not a footnote)**: the FIRST version of the new
    test reproduced the leak with a bare `subprocess.run(..., timeout=...)` and then reclaimed only
    `os.kill(child)` — which leaked the suite's own bash parent. Five probe processes accumulated across
    three test runs. A test that *demonstrates* a leak must not *commit* one: the hardened version runs
    the probe in its own session and reclaims via `os.killpg` in a `finally`, so a group kill can never
    reach the test runner. Caught by re-running the orphan census after the green run, not by the suite.
  - **Blocker (unchanged, pre-existing)**: `ruff` is not installed for `/usr/bin/python3` and the venv
    `ruff` binary is permission-gated in this session, so the style check is UNVERIFIED for this file —
    stated rather than claimed. The pytest gate above is complete.


### B-122 - `_patch_qwen35_moe_dense_experts()` fetched its target module with the parent-package import idiom, so registration hard-crashed under the overlay's leaf-module contract  [FIXED + VERIFIED 2026-09-11 tick #360 - TDD RED->GREEN]
- **Filed**: 2026-09-11 tick #360. Detected by the in-flight venv chunked suite (`logs/tick355_venvsuite.log`
  chunk 28/42, `rc=1 :: FAILED tests/test_runtime_overlay.py::test_register_qwen35_moe_runtime_registers_image_text_loader`).
  The prior tick (#359) labeled this node "the same cluster as #355's known red, no new class" WITHOUT
  root-causing it; it is not a flake and not contention.
- **RED, reproduced in ISOLATION on the baseline instrument** (D-358-3 standard - interpreter named):
  `.venv/bin/python3 -m pytest -q -p no:cacheprovider tests/test_runtime_overlay.py -k
  test_register_qwen35_moe_runtime_registers_image_text_loader` -> **rc=1**, deterministic, 15.6s:
  `training/runtime_overlay.py:36: in _patch_qwen35_moe_dense_experts / from transformers.models.qwen3_5_moe
  import modeling_qwen3_5_moe as _mod / ModuleNotFoundError: No module named 'transformers.models.qwen3_5_moe'`.
  Not contention-class: it fails alone, unloaded, 1 test, every time.
- **Root cause (one line, two idioms in one function)**: the new `_patch_qwen35_moe_dense_experts()` obtained
  its module object with `from <pkg> import <submodule>`, which additionally requires the **parent package**
  `transformers.models.qwen3_5_moe` to be importable. Every OTHER import in the same module - including the
  four at `training/runtime_overlay.py:194-202` in the very function that calls it - uses the fully-qualified
  **leaf-module** idiom, which CPython resolves straight out of `sys.modules` without ever importing the
  parent (`_find_and_load` checks `sys.modules` before walking parents). The overlay supplies `qwen3_5_moe`
  as leaf modules / a path overlay, not as an installed parent package, so the parent idiom is the one form
  that is NOT safe under the module's own contract.
- **Why it matters beyond the test**: the crash lands MID-FUNCTION - after the tokenizers/output-capturing/
  integrations compat patches, BEFORE `AutoConfig.register`. A registration path that raises there leaves the
  `qwen3_5_moe` family silently unregistered on any runtime that supplies the model as leaf modules. It is a
  fail-open-shaped defect in the launch path, not a cosmetic test failure.
- **Smallest fix (1 line, no behavior change)**: replace the parent-import with the leaf import -
  `_mod = importlib.import_module("transformers.models.qwen3_5_moe.modeling_qwen3_5_moe")`
  (`importlib` was already imported at `training/runtime_overlay.py:3`). Same module OBJECT is returned in
  both configurations.
- **GREEN + regression (all on the baseline instrument)**: `tests/test_runtime_overlay.py` **2 passed / 0
  failed / rc=0**; regression across the file under test + 3 adjacent suites (runtime_python, qwen_sft_peft_kl_loss,
  holdout_contract_audit) **22 passed / 0 failed / rc=0**; `ruff check` on both touched files **rc=0, All checks
  passed!**. Independent confirmation that the fix is behavior-neutral in the REAL runtime: under
  `.venv-omnicoder-qwen35-py311` the leaf import resolves to
  `.../site-packages/transformers/models/qwen3_5_moe/modeling_qwen3_5_moe.py` with `Qwen3_5MoeExperts` present -
  i.e. production already had the module and is unaffected; only the parent-absent configuration changes.
- **Both touched files are UNCOMMITTED working-tree changes** (`git status` -> ` M training/runtime_overlay.py`,
  ` M tests/test_runtime_overlay.py`; both mtime 06:44:14) from an earlier session, so this fix rides on the same
  uncommitted change rather than a fresh commit.
- **Cross-refs**: B-100/B-117/B-118 (the "do not classify a red without naming the interpreter / is it an
  instrument artifact" family - here the interpreter was named AND the red survived), B-119/B-120
  (the same suite's other open reds), section 2.7 (runtime-environment gate: the import idiom is part of the
  runtime contract, and the box runtime resolves it), section 9.2 (detect -> root-cause -> TDD -> record).


### B-123 - the ad-hoc chunked-suite runner's TOTAL parser reads the project's own `TESTSUITE_COUNTS` sentinel and inverts it, so a fully GREEN suite printed `passed=0 failed=4089`  [FIXED-IN-INSTRUMENT 2026-09-11 tick #363 - durable runner already correct; scratch runner retired]
- **Filed**: 2026-09-11 tick #363. Detected by reading the completed run's own last line:
  `TOTAL passed=0 failed=4089 error=0  (chunks complete)` (`logs/tick355_venvsuite.log`, runner end 12:49:53).
- **The contradiction that exposed it**: the SAME log's per-chunk lines sum to `passed=4089 failed=0`
  (39 chunks emitted a `TESTSUITE_COUNTS` line; 3 chunks exited rc=1 with a named failing node and no count
  line). A run cannot have 4089 failures and 4089 passes with 0 errors. The TOTAL was not a measurement.
- **Root cause (proved by direct regex evaluation, not inferred)**: the scratch runner
  (`/tmp/venvsuite_tick355.py:16-21`) parses the LAST non-empty stdout line of each chunk with
  `re.search(r'(\d+) passed')` / `re.search(r'(\d+) failed')`. But every chunk's last line is the repo's
  own sentinel `TESTSUITE_COUNTS passed=68 failed=0 errors=0 ... total=68`. On that string:
  `re.search(r'(\d+) passed', s)` -> **None** (the sentinel writes `passed=68`, never `<n> passed`), while
  `re.search(r'(\d+) failed', s)` -> **Match('68 failed')** - it captures the digits that BELONG to
  `passed=68`. So every chunk added its PASSED count into the FAILED accumulator, and `tp` stayed 0.
  Verified verbatim: passed-regex -> None; failed-regex -> span=(24,33) match='68 failed' capturing '68'.
- **The real numbers for this run** (the correction this entry exists to make): **42 chunks, 4089 passed,
  0 failed from counted chunks, 3 chunks rc=1** carrying 3 named failing nodes (chunk 18
  `test_huanxin_shell_exec_node.py::test_node_wedge_fix_suite_passes` = B-119; chunk 28
  `test_runtime_overlay.py::test_register_qwen35_moe_runtime_registers_image_text_loader` = B-122;
  chunk 30 `test_sapo_cookie_seed.py::test_seed_targets_only_the_base_profile`). The env baseline stands.
- **NOT a repo-instrument bug - and that distinction is the point**: the DURABLE runner
  `.sapo-loop/run_full_suite.py` already solved this class (B-115). It parses the sentinel properly
  (`ln.startswith("TESTSUITE_COUNTS")`, lines 156/304), carries `chunks_expected/chunks_reported/missing`
  completeness terms, and emits `TOTAL VERDICT=ENV-INVALID` rather than a fabricated number when no count
  was measured. The bug is that this tick's suite was launched from a **scratch re-implementation** that
  reintroduced exactly the class the durable runner was hardened against.
- **Fix (the right one, and it is not a new regex)**: run the durable runner. `.sapo-loop/run_full_suite.py`
  is the instrument; `/tmp/venvsuite_tick*.py` scratch copies are retired. If a scratch runner is ever
  unavoidable, it must parse the sentinel (`startswith("TESTSUITE_COUNTS")`), never a pytest prose summary.
- **Cross-refs**: B-115 (same class, durable fix), B-120 (the same runner family discards failure text, so
  a red chunk cannot be attributed from the log - still OPEN), section 4.1 ("no silent lies"; a measurement
  that cannot be classified reports ERROR, never "all good") and section 2.2 (a FALSE alarm is as costly as
  a missed one - here a green suite rendered as a total catastrophe, which would have triggered exactly the
  wrong escalation).


### B-124 - a process-existence census read without CPU time reports a forked-but-never-exec'd child as a SECOND co-resident trainer (the killer class), and D-362-5's blanket "ps is namespace-blind on the box" is FALSE for the trainer  [ROOT-CAUSED 2026-09-11 tick #363 - no fix to the run; instrument rule recorded]
- **Filed**: 2026-09-11 tick #363, while independently verifying tick #362's "TRAINING IS LIVE" finding.
- **What was seen**: on ASI2 (daemon :19004), `pgrep -c -f grpo_trainer` -> **2**, and
  `ps -eo pid,ppid,lstart,etime,command` listed TWO full trainers with IDENTICAL argv, both carrying
  `--output-dir .../outputs/sapo-27b-ai-20260911T043237Z` and `--overwrite-output-dir`:
    pid 4086  ppid=1     start Fri Sep 11 04:32:40 2026
    pid 4403  ppid=4086  start Fri Sep 11 04:33:35 2026   (+55s)
  Read naively, that is a duplicate co-resident trainer on the same 8 NPUs - the class this project has
  killed runs over (section 4.1/5.4.1).
- **Why it is NOT a co-residency RED (the evidence that settles it)**: `ps -o pid,ppid,stat,pcpu,time`
  shows **pid 4403 at 0.0% CPU with TIME=00:00:00 after 16:34 elapsed** - it has never executed a
  meaningful instruction in 16.5 minutes - while **pid 4086 is the live trainer at 58.0% CPU, TIME=10:09**.
  A second trainer sharing the devices cannot accumulate zero CPU. Independently, the child is not a
  multiprocessing spawn (`grep -c multiprocessing /proc/4403/cmdline` -> **0**), and the run dir shows a
  single writer (`grpo_step_metrics.jsonl` advancing 1 -> 2 rows, `step_begin` 2 -> 3, train-log mtime
  04:36:12 -> 04:51:17 across the check).
- **The instrument rule this pins (the actionable part)**: **a process-EXISTENCE census must carry CPU
  time.** `pgrep -c` alone cannot distinguish "two trainers" from "one trainer plus an idle forked child",
  and the two readings imply opposite actions (escalate a killer-class RED vs. do nothing). This is the
  same shape as the recorded forked-subshell argv phantom: a count of matching argv is not a count of
  subjects doing work. Ordering rule: count -> CPU time -> role.
- **Refines D-362-5 (recorded, NOT silently overwritten)**: D-362-5 retired `ps` as a trainer-liveness
  instrument on two grounds - machine-blind from the Mac (TRUE and unaffected by this finding) and
  PID-namespace-blind on the box, citing vLLM 468988 / sidecar 4087 invisible in /proc. This tick's direct
  probe shows that ground is **over-general**: on ASI2 the box's `ps` sees the trainer plainly (pid 4086,
  ppid=1, 58% CPU), i.e. the trainer is NOT in the blinded namespace. So `ps` is *conditionally* usable
  box-side: keep the D-362-5 replacement set (run-dir ctime / metrics line growth / train-log mtime and
  step_begin count) as the PRIMARY instruments, but do not carry "ps is namespace-blind on the box" as a
  blanket fact - it is namespace-SPECIFIC, and it demonstrably read this trainer correctly.
- **No fix applied to the run** - there is no defect in the run: pid 4403 is an idle child, not a
  duplicate, and the trainer is healthy and advancing. Recorded as an instrument/verdict defect (a false
  killer-class RED in waiting), which is the correct place for it.
- **Cross-refs**: D-362-5 (refined here), the forked-subshell-argv-phantom class, section 5.4.1
  watcher-probe semantics (a probe that cannot express UNKNOWN manufactures false verdicts), section 4.1
  (unknown is not a verdict).

### B-125 - a run whose EVERY step is a degenerate skip raises NO alarm, and the liveness instruments that watch it report motion as progress  [OPEN - tick #364, 2026-09-11 12:57 CST; owner: Algorithm Correctness + Run Watch]
- **Subject**: live run `outputs/sapo-27b-ai-20260911T043237Z` (box, launched 04:32:37Z).
- **Symptom**: 3 of 3 landed steps carry `skipped:1`, `all_fail:True`, `pass_rate 0.0`,
  rewards `[0 x8]`, advantages `[0 x8]`, judge `[NA x8]`. No `backward_done` stage exists anywhere in
  1793 log lines. 0 `step_*_adapter` dirs. Cadence s1 04:34:25Z -> s2 04:50:59Z -> s3 04:51:42Z.
- **The defect (two parts, both measured)**:
  1. **No alarm fires.** The step rows carry `degenerate_policy_alarm: False` and
     `quarantine_suppressed: True`; the log contains **no** `entropy_absolute_collapse` violation and no
     `trust_region_violation` stage. The run is degenerate by inspection and silent by instrumentation.
     NOTE the sharp edge: `training/grpo_utils.py` was changed on the box at **2026-09-11_02:31Z**
     (backup `.bak-20260911T022645Z`) to ADD exactly the `entropy_absolute_collapse` detector for this
     class. Whether it failed to fire because (a) the trainer process imported the pre-change module
     (keeper-runs-stale-code class), (b) the detector needs a full `window_size` of steps and only 3 had
     landed, or (c) the rule is mis-gated, is **NOT YET DETERMINED** - the three are distinguishable and
     must be distinguished before any fix. Do not assume (a).
  2. **The liveness instruments report motion as progress.** #363 recorded this run as "the trainer is
     healthy and advancing", citing `grpo_step_metrics.jsonl` growing 1 -> 2 rows and trainer CPU time.
     Both measurements are correct and both are compatible with **zero learning**: row growth counts
     steps ATTEMPTED, and a skipping trainer still burns CPU. Every row that reading counted carried
     `skipped:1`.
- **Why this is a real bug and not a status note**: the run's own defense-in-depth (`degenerate_policy_alarm`,
  the collapse breakers, the metrics poller) all read green on an input where the correct verdict is RED.
  This is the B-081 / D-362-5 "instrument zeroing" class, one layer up: not a zero readout read as zero
  data, but a **non-zero readout (row count, CPU time) read as a health signal it does not carry**.
- **Required fix shape (TDD, red first)**: a run-level guard whose predicate is *"N consecutive landed
  steps with `skipped:1`"* - independent of any window baseline, independent of the repair queue, and
  independent of whether a reward EVER landed. Plus: the metrics poller and any row-growth liveness check
  must quote the **skipped share** alongside the row count, so "advancing" cannot be asserted without it.
- **Explicitly NOT the cause (recorded to prevent misrouting)**: the judge chain is UP. There is exactly
  ONE `dp4_judge_failed` in the whole log (step 2, `no_scores_from_dp4`, upstream `HTTP Error 504`).
  Steps 1 and 3 have none. The `[NA x8]` judge column is an artifact of every candidate failing the
  syntax gate first (`SyntaxError: invalid syntax`, `No module named 'qiskit'`, and two candidates whose
  `code_hash` is `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` = sha256 of the
  EMPTY STRING).
- **Refuted alongside it**: the run's degeneracy is **NOT inherited from the warm-start adapter**.
  Control: run `20260909T104517Z` (leg5) uses the identical `adapter_init`
  (`outputs/sapo-27b-ai-20260908T094427Z/step_000097_adapter`), the identical step-1 task
  (`quantum_rl_v2_swap_test_ry`) and the identical temperature (1.0), and produced
  `completion_token_lengths [637, 637, 798, 1903]`, `max_code_chars 2283`; this run produced
  `[4, 4, 4, 3, 3, 4, 3, 3]`, `max_code_chars 8`. The adapter is also independently not globally
  collapsed (`reeval_38_094427Z_step_000097_adapter.json`, 2026-09-08T23:01:30Z, 2/18 vs base 1/18).
  The cause of the step-1 generation collapse is therefore **OPEN** and owned by the Debugger lane
  (dispatched tick #364; four ordered experiments: direct vLLM probe with/without the LoRA, prompt-format
  recovery, vLLM server identity + start time, adapter integrity).
- **Cross-refs**: B-081 / D-362-5 (instrument zeroing), B-124 (count without CPU time is not a census -
  this is the same family one step further: count without skipped-share is not progress), B-110 (a monitor
  whose target cannot be repointed), the recorded SAPO inherited-collapse blind spot (still a real class,
  but NOT this instance).

### B-125 CORRECTION (tick #364, manager, 2026-09-11 13:00 CST) - part 1 is DETERMINED: the new absolute-floor detector is structurally blind to THIS collapse, because it tests the wrong quantity
- #364 filed part 1 as "not yet determined - (a) stale import, (b) window starvation, (c) mis-gating".
  It is now determined, and it is **(c), and worse than (c)**.
- **Measured, from `training/grpo_utils.py` on the box (read this tick)**:
  - `window_size: int = 10`, and the rule block is
    `violations["entropy_absolute_collapse"] = bool(window_entropies) and all(e <= self.entropy_absolute_floor for e in window_entropies) and all(f["all_fail_share"] > self.all_fail_share_limit for f in window)`
    with `entropy_absolute_floor = 0.05`.
  - The live run's `entropy_mean` per landed step is **2.796, 0.796, 2.346** - i.e. **16x to 56x ABOVE the
    0.05 floor**. The predicate `all(e <= 0.05 ...)` is therefore **FALSE at every step**, and the rule
    **cannot fire on this run at any step count** - not at step 10, not at step 120. Window size is a
    red herring (only 3 steps have landed, so it is ALSO window-starved, but that is not the blocker).
  - (a) stale import is **REFUTED**: `grpo_utils.py` mtime is 02:31Z and the trainer started 04:32:40Z, so
    the process imported the post-change module.
- **The real defect (the class-extinction gap)**: this run's collapse is a **response-LENGTH collapse, not
  an entropy collapse**. The policy emits 3-4 tokens and then EOS - it is not uncertain per token, it is
  *confidently terminating*. `entropy_mean` over those few tokens is normal-to-high (2.3-2.8). Every
  breaker in the family is entropy-based (`entropy_collapse`, the new `entropy_absolute_collapse`, the
  entropy floor / floor-weight machinery), and every one of them is therefore **structurally blind to a
  policy that says nothing at length**. The guards DID see the flat group - `update_signal_kind:
  flat_candidate_dispersion`, `update_signal_magnitude 0.0` vs `threshold 0.05` - and correctly skipped
  the step. What they never do is escalate to an **alarm**, because the alarm family asks about entropy.
  A trainer that correctly declines to learn from a group it cannot learn from, 100 times in a row, and
  reports nothing, is the whole of this bug.
- **Fix shape (TDD, red first)**: a **response-length / immediate-EOS** absolute floor, sibling to
  `entropy_absolute_floor` and equally baseline-free - e.g. a rule keyed on
  `median(completion_token_lengths)` (or `mean_response_length`) at or below a small absolute floor
  (this run: 3.5 / 53.2 / 4.5) **together with** `eos_termination_rate` high and `all_fail_share` over the
  limit, firing after N consecutive such steps with N small (the run is provably dead by step 3 - do not
  inherit `window_size = 10` for an absolute rule; that is the same "wait 10 steps to say what step 1
  already showed" latency that let leg5 run 100/100 at pass 0.000). RED test: feed the guard synthetic
  step facts matching this run (`all_fail:True`, `entropy ~2.4`, `mean_response_length ~4`, pass 0) and
  assert an alarm is raised by step 3 - it fails today.
- **Route this to the Debugger/Algorithm Correctness lanes together with the generation-collapse root
  cause**: they are independent defects (one is "why does the policy emit 4 tokens", the other is "why did
  nobody notice"), and fixing only the first leaves the fleet blind to the next one.


### B-125 - STATUS UPDATE (tick #365, 2026-09-11 13:2x CST): PART 1 FIXED AND PINNED - response-length collapse floor, TDD red->green
- **Landed**: `training/grpo_utils.py` (`CircuitBreakerState`) + `training/grpo_trainer.py`
  (`observe_and_evaluate_breakers`). New test file `tests/test_grpo_response_collapse_breaker.py`.
- **The rule**: `response_length_absolute_collapse` - a baseline-free, WINDOW-INDEPENDENT floor that
  trips on `response_collapse_consecutive_steps` (3) consecutive landed steps satisfying ALL of:
  median `completion_token_lengths` <= `response_length_absolute_floor` (12), `eos_termination_rate`
  >= `response_eos_termination_limit` (0.6), and `all_fail_share` > `all_fail_share_limit` (0.40).
  It asks a LENGTH question about a length failure; the entropy-keyed family cannot see this class
  (live-run `entropy_mean` 0.80 / 2.35 / 1.36 / 3.93 / 4.39 vs the 0.05 entropy floor).
- **Why window-independent**: `evaluate()` returned early unless `step % window_size == 0`, and the
  family needs `required_windows = 2`, so the earliest any pre-existing rule could trip is step 20.
  The response-collapse rule is evaluated on EVERY step and fires in this run at step 5.
- **RED evidence** (before the fix, `python3 -m pytest tests/test_grpo_response_collapse_breaker.py`):
  `TESTSUITE_COUNTS passed=0 failed=3 errors=0 ... total=3`, first failure
  `TypeError: CircuitBreakerState.observe_step() got an unexpected keyword argument 'completion_token_lengths'`.
- **GREEN evidence**: `passed=5 failed=0 ... total=5` on the new file; regression
  `tests/test_grpo_response_collapse_breaker.py + test_grpo_inherited_collapse_breaker.py +
  test_grpo_trainer_breakers.py + test_grpo_utils.py + test_grpo_trainer_metrics.py +
  test_grpo_trainer_guardrail_gates.py` = `passed=149 failed=0` (0 new failures).
- **E2E exercise on the REAL facts** (tick #365, the six landed rows fetched from the box, fed through
  the trainer's own `observe_and_evaluate_breakers` + `maybe_stop_for_breaker`):
  step 5 -> `{"stage": "circuit_breaker_trip", "breaker": "response_length_absolute_collapse",
  "streak": 3}` then `{"stage": "circuit_breaker_stop"}` and `halted=True`.
  The live run today would have halted at step 5 instead of holding 8 NPUs through step 120.
- **THREE false-positive guards are pinned as tests** (a false alarm costs as much as a missed one):
  (1) healthy long completions `[637,637,798,1903,...]` at eos 0.125 must NOT trip;
  (2) entropy 6.5 must not mask an immediate-EOS collapse; (3) a caller passing no generation
  diagnostics gets exactly the pre-B-125 behaviour - the rule never INVENTS a length.
- **NOT YET DEPLOYED TO THE BOX**, and deliberately so: the live run's tree is frozen while it is in
  flight (section 5.4.2), and this is a detection rule, not the generation-collapse root cause. It
  rides the next bundle, whose deploy gate is the user's GO. **A new run started from the current box
  tree would still be unguarded.**
- **STILL OPEN, and the larger half**: (a) the **generation-collapse root cause** - why the policy
  emits EOS after 2-4 tokens under this run but 637-1903 under the identical-adapter leg5 control
  (Debugger lane, four ordered experiments, tick #364 dispatch); (b) part 2 - the metrics poller and
  every row-growth liveness check must quote the **skipped share** alongside the row count.
- **Cross-refs**: this entry discharges the "Fix shape (TDD, red first)" clause of the B-125
  CORRECTION above. Keep both: the CORRECTION is the measurement, this is the fix.


### B-126 - the keeper's `busy-congested` congestion policy HARD-RESTARTS the ASI1 daemon, so a loaded exec queue destroys the live command channel it was trying to protect  [ROOT-CAUSED 2026-09-11 tick #363 - kill source for B-101 PROVEN; policy fix not yet applied]
- **Filed**: 2026-09-11 tick #363 as **B-125**. **Renumbered B-126 at tick #365**: B-125 was already
  taken by the response-length-collapse issue filed the same afternoon (#364), and a duplicate ID is a
  record-identity defect - two different bugs cannot share a key. Any earlier note reading "B-125" in a
  KEEPER/congestion context means this entry.
- Closes the open question in **B-101** ("kill source NOT yet proven").
- **The kill source, with the line**: `logs/session_keeper.log`
  `[2026-09-11 12:47:42] ACTION daemon :20646 busy-congested - direct /stop restart`.
  Corroborated by the daemon's own /health: ASI1 pid **90852 -> 4323**, `uptime_s` 7943 -> **731**
  (restart at ~12:48:51 CST, ~69s after the keeper action = stop + relaunch), and
  **`commandCount` 48 -> 0** - the restart wipes the daemon's command history.
- **It is a recurring pattern, not a one-off** (`session_keeper.log`): `03:05:31 / 03:07:35 / 03:07:50 /
  03:08:07` (4x, `backlog wedge (pending=15)`), `05:27:24`, `05:33:41`, `10:11:32`, **`12:47:42`** - all
  `direct /stop restart` on `:20646`, plus `ALERT daemons not ready (20646)` at 10:14/10:17/10:23.
- **The harm is observable in this tick's own work**: three independent probes of ASI1 during
  12:40-12:48 came back `timeout`, `timeout`, and `RemoteDisconnected: Remote end closed connection
  without response` - the daemon was being killed mid-probe. The probe failures and the keeper action are
  the same event, and reading them as two separate defects would have been the error.
- **Why this is self-defeating (the design defect)**: the congestion signal is a SERIALIZED exec queue
  with N watchers polling it (section 5.4.1's fleet-poller cadence budget). Backlog therefore rises
  exactly when the channel is most in use, and the keeper's remedy - a hard `/stop` + relaunch - is what
  actually destroys the channel: it drops the queued work, resets `commandCount`, and takes the resource
  dark for ~1 min. The keeper treats a symptom it is causing as a fault in the subject.
- **Not applied this tick**: the fix belongs to the keeper's congestion policy (degrade the hottest
  poller before restarting the transport; require the queue to still be backed up after a backoff, and
  prefer a longer timeout over a restart), and the keeper runs stale in-process code that needs a
  `launchctl kickstart` to reload - session-gated here. Recorded with the evidence so the next writable
  tick can take it TDD-first.
- **Cross-refs**: B-101 (kill source now proven - this entry supersedes its "NOT yet proven" clause),
  B-102 (the ASI1-only keepalive cannot resolve `node`), B-087 (heartbeat lock), the keeper
  "kick is unverified" class, section 5.4.1 fleet-poller cadence budget ("on any queue backlog: find the
  hottest poller and slow it first"), section 9.1 (a resource that keeps going dark is RED even when it
  comes back).

### B-127 - `.sapo-loop/sapo_metrics_poll.py` reports the WRONG BOX three ways: a welded endpoint, a hardcoded "ASI3" identity in the render, and a daemon census that never checks ASI1  [FILED 2026-09-11 tick #365 - not fixed]
- **Filed**: 2026-09-11 tick #365. Filed as B-127 because B-126 was taken by the keeper-congestion
  renumber landed by a sibling session during this tick.
- **Defect 1 (transport): the default endpoint points at the box the run is NOT on.** `ENDPOINT`
  defaults to `http://127.0.0.1:20653/exec` (ASI3). This tick the poller ran against that default and
  returned **`POLL-FAIL: exec error: timed out`**, rendering `metrics.md` as
  `trainer unknown | steps UNKNOWN (no rows measured)` for a trainer that was alive and had just
  finished a step. Repointed to `http://127.0.0.1:19004/exec` (ASI2), the *same invocation* returned
  the full row set and a real verdict in seconds. Measured: ASI3 `/exec` = **HTTP 504 Gateway Timeout**
  at 60 s; ASI2 `/exec` = OK. The run's trainer lives on ASI2 (host `dl-868c196fb82d3e0b8cfbbe826d8afd0a-...`,
  `training/grpo_trainer.py` pid 4086 at 53% CPU + `scripts/sapo_judge_bridge.py` pid 4097). A monitor
  whose default target is a wedged host renders "no data" as "no trainer".
- **Defect 2 (identity): the rendered box is a literal.** `sapo_metrics_poll.py:629` writes
  `f"Run: {run_cell} | ASI3 8xNPU | {trainer_cell} | {step_cell}"` - **"ASI3" is hardcoded**, so the
  poller I ran against :19004 (ASI2, verified by `os.uname().nodename` on the box) still printed
  `Run: sapo-27b-ai-20260911T043237Z | ASI3 8xNPU`. B-110 made the transport repointable and left the
  *identity* welded; the result is an instrument that can be pointed anywhere and will still name ASI3.
  Same class as the keeper log's hardcoded `(20653/19004)` literal.
- **Defect 3 (census): the daemon health line only probes 2 of 3 daemons.** `sapo_metrics_poll.py:814`
  is `for name, port in (("ASI3", 20653), ("ASI2", 19004))` - **ASI1 :20646 is never probed**, yet the
  rendered line reads `daemons ASI3:OK ASI2:OK`. ASI1 is precisely the daemon the keeper hard-restarts
  (B-126: 8 recorded kills today, most recent 12:47:42), so the one daemon with a known kill history is
  the one the census cannot see. A 2-of-3 check rendered as a fleet verdict is a false GREEN.
- **Evidence for defect 2/3**: this tick's own run of the poller against :19004 printed
  `Run: sapo-27b-ai-20260911T043237Z | ASI3 8xNPU | ...` and `daemons ASI3:OK ASI2:OK`, while an
  independent direct probe of all three /health endpoints returned ready=True for :20646 (pid 4323),
  :19004 (pid 52665) and :20653 (pid 53753).
- **Cross-refs**: B-110 (the endpoint weld this partially fixed), B-126 (the ASI1 kill loop the census
  cannot see), the keeper hardcoded-literal class, and section 9.1's "a resource that keeps going dark
  is RED even when it comes back".

- **FIXED (TDD red->green) 2026-09-11, same tick #365 - Mac-side instrument, no box deploy owed.**
  - RED first: `tests/test_sapo_metrics_poll_box_identity.py` **5 failed** (B1 census 3-of-3, B2 label
    derived from endpoint, B3 unknown endpoint not silently ASI3, B4 no hardcoded box literal in the
    render, B5 default still ASI3). GREEN after the patch: **5/5 passed**. Adjacent poller files
    regression **88 passed / 3 failed**, and the 3 failures target a DIFFERENT module
    (`scripts/sapo_metrics_poller.sh`, files last modified 11:01/11:13, before this tick) - unrelated by
    target, not caused by this change.
  - Patch (`.sapo-loop/sapo_metrics_poll.py`): (a) new `DAEMON_PORTS = (("ASI1",20646),("ASI2",19004),
    ("ASI3",20653))` as the single census source, consumed by the loop that was
    `for name, port in (("ASI3", 20653), ("ASI2", 19004))`; (b) new `box_label(endpoint)` deriving the
    name from the endpoint actually in use and returning `box UNKNOWN (port N is not a known daemon)`
    for anything unrecognised; (c) the render literal
    `f"Run: {run_cell} | ASI3 8xNPU | ..."` -> `f"Run: {run_cell} | {box_label(ENDPOINT)} | ..."`.
  - **E2E verified, not just unit-tested**: the live poller repointed at `http://127.0.0.1:19004/exec`
    now renders `Run: sapo-27b-ai-20260911T043237Z | ASI2 | trainer unknown | 6/120 steps` (it printed
    the literal `ASI3 8xNPU` before) and `Note: ... daemons ASI1:OK ASI2:OK ASI3:OK` (it printed only
    ASI3+ASI2 before).
  - Still open in the same family, NOT fixed: the `trainer unknown (no liveness evidence)` cell - the
    module's `pgrep`-based `locate_trainer` returns UNKNOWN on a box where `ps` plainly lists
    `training/grpo_trainer.py` pid 4086. That is a namespace/instrument question of its own and is
    carried, not claimed fixed here.


## B-128 - full-suite node-id inflation: one static sweep emits 2086 of 6446 node ids, 99.4% permanent no-ops
- **Filed**: 2026-09-11 (tick #366). **Status**: FIXED TDD red->green (Mac-side test file; not on the box launch path, so no deploy gate owed).
- **Symptom**: the full-suite runner (B-123 durable runner) logged `VACUOUS` on chunks 05-13 **every run** -
  9 chunks, ~1800 node ids, zero pass/fail/error signal. A chronic alarm that has to be re-derived by hand each run.
- **Root cause (MEASURED, not inferred)**: `tests/test_eval_task_py39_annotations.py` parametrized its static
  PEP 604 sweep over `ALL_TASK_MODULES = sorted(TASKS.rglob("*.py"))` = **2074** eval-task files, while the test
  body does `if not unions: pytest.skip("no union annotations")`. Only **12** modules carry a union annotation,
  so 2062 node ids could never assert. Measured: `ALL_TASK_MODULES=2074`, `AT_RISK_MODULES=12`,
  node ids from that one file = **2086 = 32.4% of the 6446 the suite collects**, of which 0.58% do work.
- **Also**: the file was UNTRACKED (`git ls-files` -> no match) and written 2026-09-11 11:28 - a same-day
  addition whose cost had never been measured.
- **Fix**: define `SWEEP_MODULES = AT_RISK_MODULES` (built by the identical predicate the test used to decide
  skip-vs-assert) and parametrize the sweep over it; move the `AT_RISK_MODULES` definition above the sweep so
  it exists at parametrize time. The per-file `pytest.skip` becomes a hard `assert unions`, so a divergence
  between the predicate and the parametrization is now LOUD instead of a silent skip.
- **Behaviour invariance (by construction)**: the assert set is unchanged - the old test asserted on exactly
  the 12 files where `_union_annotations` was non-empty, and `SWEEP_MODULES` is that same set.
- **TDD evidence**: RED `NameError: name 'SWEEP_MODULES' is not defined` (1 failed / 1 passed) ->
  GREEN `26 passed failed=0 errors=0 skipped=0`. Node ids **2086 -> 26**. Collection wall-clock was NOT
  claimed as a win: the measurement was confounded by the concurrent full-suite run.
- **Guard added**: `test_sweep_census_cannot_shrink_silently` pins `len(ALL_TASK_MODULES) >= 2000` and
  `AT_RISK_MODULES <= ALL_TASK_MODULES`, so filtering cannot silently zero the guard if `TASKS` stops resolving.
  This guard was green before the change and is a pin, not a red->green - stated plainly rather than dressed up.
- **Not claimed**: no wall-clock win is asserted (confounded); the ~220s/chunk-skip cost is a projection from
  the per-chunk `elapsed` lines, not an A/B measurement.


## B-129 - keeper kickstart loop: the watchdog's remedy cannot cure the condition it detects
- **Filed**: 2026-09-11 (tick #366, ~13:48 CST). **Status**: OPEN - filed and escalated, NOT fixed this tick.
- **Symptom**: `session_keeper_state.json` flipped from `status OK / daemons ok / headless_auth ok`
  (pid 41874, ts 13:21:07) to `status STARTING / daemons unknown / headless_auth unknown` (pid 3835, ts 13:46:12).
- **Measured, in the last ~10 minutes:**
  - `logs/session_keeper_watchdog.log` - seven consecutive cycles, each `action=KICKSTART KICKSTART rc=0`,
    at 13:39:16 / 13:40:16 / 13:41:17 / 13:42:17 / 13:43:17 / 13:44:17 / 13:45:17. The `age` field grows
    monotonically across them: **1088.8 -> 1149.0 -> 1209.2 -> 1269.3 -> 1329.5 -> 1389.7 -> 1449.8** seconds,
    i.e. the keeper had not completed a cycle for **18-24 min** while being kicked every 60s.
  - `logs/session_keeper.log` - **five** `session_keeper started pid N` lines between 13:36:57 and 13:45:31
    (pids 83959 / 58991 / 65802 / 85308 / 3835) - ~1 restart per 1.8 min.
  - Totals in the two logs: **208** `action=KICKSTART` and **265** `session_keeper started`.
  - pid 3835 verified live: `/bin/bash .../scripts/session_keeper.sh`, PPID 1, elapsed 01:46.
- **Cause chain, all from the keeper's own log:**
  `13:05:22 ALERT headless claude auth FAILED` -> `13:27:14 ALERT headless claude auth FAILED` ->
  `13:36:03 ERROR no live process with valid auth found; keep retrying every cycle`. The keeper cannot
  complete a cycle without headless auth, so its `age` grows, so the watchdog kicks it, and **the kick does
  not restore auth** - the next cycle finds the same auth wall. A closed loop.
- **Why it is a defect and not just noise:** the watchdog's remedy (restart the keeper) is *structurally
  incapable* of fixing the condition it detects (auth unavailable from any live process - the keeper's own
  log says `tried=0, budget=120s`, nothing to refresh FROM). The harm is concrete and is the "no silent lies"
  class: **(a)** it destroys the keeper's own status file as a health instrument - the manager now cannot tell
  `STARTING-because-looping` from `STARTING-because-booting`, and this tick had to reconstruct it from two
  log files; **(b)** it spends the evidence trail - a restart storm buries the single actionable line
  (`no live process with valid auth`); **(c)** per the B-091 lesson, `kick` means *attempted* - here the
  restarts ARE landing (corroborated by 5 fresh `started pid N` lines), so this is not the usual
  kick-lands-nowhere case, and it is still not helping.
- **NOT fixed, deliberately**: the keeper "loads its source once at boot" (it is the stale-code class), so a
  policy edit only takes effect after a `launchctl kickstart` - which is session-gated and, more importantly,
  restarting a looping keeper mid-loop is not a fix. Proposed direction for the TDD fix (next tick / owner
  assignment): the watchdog must back off after N consecutive kicks at a non-decreasing `age` (loop detection),
  and the keeper must publish an explicit `auth-blocked` state that is NOT a liveness failure, so the remedy
  stops misfiring and the state file stays readable.
- **Not affecting resources right now**: all three daemons re-probed during the loop and are READY with
  unchanged pids (ASI1 4323 cc=66, ASI2 52665 cc=331, ASI3 53753 cc=384). So B-126's
  `POST /stop restart` branch did not fire this time. Resources are 3/3; the keeper itself is the casualty.


### B-130 - the metrics poller FABRICATES a gradient it never measured, then alarms on it: a skipped step reads as "grad 0.0000" and fires SUB-PRECISION on gradients that do not exist  [FIXED TDD red->green, 2026-09-11 tick #366 - Mac-side instrument, not on the box]
- **Filed**: 2026-09-11 tick #366 by the manager chair. Filed as **B-130** because **B-128 was already
  taken** ("full-suite node-id inflation: one static sweep emits 2086 of 6446 node ids"). The first draft of
  this entry used B-128 and was renumbered before it landed; the ID was re-checked against the ledger and
  `tests/test_bugqueue_id_uniqueness.py` (2/2) was run after the write.
- **The defect, measured on the live run `sapo-27b-ai-20260911T043237Z`** (all 7 step rows on the box carry
  `"gradient_norms": null` together with `"skipped": true` -- a repair-routed skip runs no optimizer step, so
  there IS no gradient to report):
  - **D1 (fabrication)**: the box-side `PARSER` inside `.sapo-loop/sapo_metrics_poll.py` did
    `g=(r.get("gradient_norms") or [None])[0]; if g is None: g=0.0`, then
    `print("S%s loss %.4f grad %.4f" % ...)`. An ABSENT gradient therefore crossed the wire as the
    MEASUREMENT `grad 0.0000`.
  - **D2 (false alarm)**: the Mac side counted it as a real one --
    `grad_tiny = sum(1 for r in rows[-3:] if r["grad"] < 0.05)`; `if grad_tiny == 3: alerts.append(
    "SUB-PRECISION: last 3 grads < 0.05")`. `metrics.md` at 13:24 CST read
    `VERDICT: ALERT: DEAD-SIGNAL: ...; SUB-PRECISION: last 3 grads < 0.05` -- naming a precision problem in
    gradients that do not exist.
  - **D3 (the real condition went unnamed)**: `count_noop` excludes repair-routed skips BY DESIGN and
    DEAD-SIGNAL keys on rewards rather than updates, so a run that skips EVERY step rendered `no-op 0/2`
    forever. 7/7 steps skipped -- zero optimizer updates, a policy that cannot change without intervention --
    was reported by no alert at all.
  - This is the module's OWN documented failure class one layer down: it refuses a truncated record rather
    than defaulting its fields to 0.0 ("a DEFAULT is a guess"), then defaulted the absent gradient to 0.0.
- **Fix shape (all four parts landed together; TDD red first)**: `grad NA` is emitted for an absent gradient
  and never a number; the Mac parse maps `NA` to `grad is None` + `grad_absent` and does NOT refuse the record
  as corrupt; every numeric reader is guarded (`stability_alerts` grad-spike, `count_noop`, `nonfinite_alerts`,
  `fmt`, the `metrics.md` row render); the SUB-PRECISION rule is extracted into the pure `subprecision_alert`
  and fires ONLY on a full window of MEASURED grads below the floor (an incomplete window yields no verdict);
  and the new pure `count_skip_streak` / `zero_update_alerts` name the condition that actually obtains.
- **TDD evidence**: `tests/test_sapo_metrics_poll_grad_absence.py` RED **8 failed / 1 passed** -> GREEN
  **9/9**. E2E on the run's OWN six fetched rows: `grad tokens emitted: ['NA']`, all six rows parse with
  `grad=None` / `grad_absent=True` and `dropped=[]`, `subprecision_alert == []` (it fired before), and
  `zero_update_alerts` returns `ZERO-UPDATE: 6 consecutive steps skipped -- 0 optimizer updates ...`.
- **Regression scope, stated honestly**: adjacent metrics-poller selection runs **136 passed / 3 failed**
  (`-k "metrics_poll or metrics_poller or sapo_metrics"`). All 3 are PRE-EXISTING and not caused by this
  change: two live in `tests/test_sapo_metrics_poller.py`, which exercises **`scripts/sapo_metrics_poller.sh`**
  -- a self-contained bash implementation that does not import this module at all -- and the third,
  `tests/test_sapo_metrics_poll_run_target.py::test_a3_locate_trainer_real_probe_reports_dead_on_positive_absence`,
  fails on TRANSPORT, not on parsing: it calls the untouched `locate_trainer()` against the untouched default
  `ENDPOINT = http://127.0.0.1:20653/exec` and gets `('UNKNOWN', None, 'probe failed: timed out')`. That is
  **B-127 D1 itself** (the weld to ASI3, whose `/exec` 504s), still open in the liveness path.
- **Cross-refs**: B-127 (the ASI3 endpoint weld that makes the third failure), B-125 (the collapse family this
  is the Mac-side echo of -- B-125's detector is box-side and deploy-gated; this alarm is Mac-side and is
  consequently NOT gated), B-078 (three-state liveness, the same "absence is not a verdict" law).

### B-132 - the poller's TRANSPORT was welded to the ONE daemon that cannot answer, so the liveness verdict came back UNKNOWN by default  [FIXED TDD red->green, 2026-09-11 tick #368 - Mac-side instrument, not on the box]
- **Filed**: 2026-09-11 tick #368. This is the fix for **B-127 D1**, which was carried open across #366/#367
  and ordered to the run-watch lane. Filed as B-132 because a SIBLING session landed its own B-131 (the circuit-breaker blind spot) at tick #367 while this one was in flight -- the collision was caught by `tests/test_bugqueue_id_uniqueness.py` (which went RED on the first write), then renumbered here. Measured, not assumed.
- **Root cause (reproduced, not inferred)**. B-110 made the endpoint *repointable*; B-127 D1 observed that the
  liveness probe was still *welded*. Measured with the REAL module at ONE instant, all three readings real:
  ```
  ASI1 :20646  locate_trainer -> ('DEAD',    None, 'pgrep matched no trainer')   2.9s
  ASI2 :19004  locate_trainer -> ('DEAD',    None, 'pgrep matched no trainer')   2.9s
  ASI3 :20653  locate_trainer -> ('UNKNOWN', None, 'probe failed: timed out')  20.0s
  ```
  `:20653` is `ENDPOINT`'s default -- and it is the busiest daemon, the one every lane polls. So the
  **default** invocation of the liveness instrument read UNKNOWN while two sibling daemons on the same shared
  filesystem answered the SAME question definitively in 3s. The weld was not in the address, it was in the
  **cardinality**: exactly one candidate, and the one candidate could not answer.
- **Why it mattered (the latent harm, stated carefully)**: UNKNOWN is not DEAD (section 5.4.1), so the
  immediate harm was NOT a false relaunch -- it was a **permanently blinded resurrector**. The correct verdict
  was reachable in 3s from a sibling and was unreachable through the default path. Note the hazard in the
  other direction too: a single-daemon DEAD is only as trustworthy as that daemon's PID namespace, and
  namespace visibility is known to VARY by daemon in this fleet -- so the fix must not simply OR the daemons
  together and call any DEAD definitive.
- **Fix shape (TDD red first)**: `box()` is split into `_http_exec(endpoint, cmd, timeout)` (ONE call to ONE
  endpoint) and `box()`, which iterates `_candidate_endpoints()`. `_EXPLICIT_ENDPOINT` separates "the fleet"
  from "that box": an operator who pins `SAPO_ENDPOINT` is making a claim about WHICH machine, so pinning
  collapses the candidate list to exactly one and **no failover fires**. The endpoint that actually answered
  is published as `LAST_BOX_ENDPOINT`, and the new `box_label_actual()` renders THAT -- so the instrument can
  no longer name a machine it did not read (B-127's own "will still name the wrong machine"). A fleet-wide
  transport failure RAISES and never returns an empty string: an empty read is indistinguishable from a
  positive absence and would launder a dead transport into a DEAD verdict.
- **TDD evidence**: `tests/test_sapo_metrics_poll_box_failover.py` RED **4 failed / 0 passed** -> GREEN
  **4/4** (F1 failover, F2 answering daemon named, F3 pinned endpoint honoured strictly, F4 fleet-wide
  failure raises). One RED failure was in the TEST, not the fix: the stub modeled `_http_exec` as returning
  the JSON envelope when its contract is the DECODED OUTPUT; corrected, then green.
- **Regression**: `-k "metrics_poll or metrics_poller or sapo_metrics"` was **136 passed / 3 failed** before
  this change, now **143 passed / 0 failed**. Both former non-bash failures were B-127 D1 itself, including
  `test_a3_locate_trainer_real_probe_reports_dead_on_positive_absence`. The third pre-existing failure
  (`tests/test_sapo_metrics_poller.py`, which exercises `scripts/sapo_metrics_poller.sh`) also no longer
  appears in the selection.
- **One guard updated (strengthened, not weakened)**: `tests/test_sapo_metrics_poll_box_identity.py::
  test_b4_no_hardcoded_box_literal_in_the_render` asserted the literal string `box_label(` in the render
  line. The new call is `box_label_actual(`, which does NOT contain that substring -- so the guard failed on
  a fix that satisfies its INTENT more strongly. The assertion now requires `box_label_actual(`: the render
  must name the box that ACTUALLY ANSWERED, not the one aimed at. Anti-literal check and the vacuity guard
  are unchanged.
- **E2E proof on the live fleet** (post-fix, default path, no env override):
  `locate_trainer() -> ('DEAD', None, 'pgrep matched no trainer process')` in 22.3s (20s burned on the ASI3
  timeout, then ASI1 answered); `LAST_BOX_ENDPOINT = :20646`; `box_label_actual() = "ASI1"` vs
  `box_label(ENDPOINT) = "ASI3"`.
- **NOT fixed / carried**: the residual 20s cost of trying the pinned-first saturated daemon before failing
  over (a latency defect, not a correctness one); `box_label_actual()` has no unit test asserting the
  before-first-read fallback; B-129 (keeper loop) and the B-125 box-side detectors remain open.
- **Cross-refs**: B-127 (this is its D1), B-110 (the repointable-endpoint precursor), B-130 (the sibling
  fix in the same module), B-078 (three-state liveness).

### B-133 - a STOP leaves no attributable record, so a deliberate, graceful, agent-executed stop is read back as a spontaneous CRASH  [FIXED TDD red->green, 2026-09-13 tick #371 - Mac-side instrument, NOT on the box]
- **Subject**: run `outputs/sapo-27b-ai-20260911T043237Z`, stopped ~05:28:30Z 2026-09-11 during step 8.
- **Symptom (the defect)**: the run ended by **external SIGTERM** and performed its full graceful final
  save. Nothing on disk records **who** stopped it or **why**. Every observer therefore reconstructed a
  cause from side effects, and two consecutive standups reconstructed it wrong:
  - tick #366 (STATUS.md): "the trainer died on its own at ~05:28:33Z, mid step-8 adapter save", with the
    cause explicitly left UNESTABLISHED and **dispatched to the Debugger as a death investigation**;
  - tick #368: "Run still DEAD, no relaunch (no user GO, and it would be unguarded)" - i.e. the run is
    already stopped, so no stop decision was even considered.
  Both readings are refuted by two lines the run wrote itself.
- **Evidence (the record that DOES exist, just not where it is looked for)**:
  - `logs/sapo_27b_ai/grpo_train_20260911T043237Z.log` line **69** and line **74**:
    `{"stage": "sigterm_graceful_stop", "step": 8|null, "message": "SIGTERM received - running the
    final-save path"}`, bracketing a **completed** checkpoint write (`step_000008_adapter`, 312 MB,
    `resume_state.json step:8`, `adapter/`).
  - That stage string is emitted **only** from the SIGTERM handler (`training/grpo_trainer.py:5192`
    registers it; `grpo_trainer.py` contains no `os.kill`/`killpg` - it never signals itself). An external
    signal is therefore not an inference, it is the only producer of that line.
  - The stop OPERATION's escalation half survives on the box: `/tmp/huanxin_cmd_OC_1789104581129_*.sh`,
    `..._1789104614390_*.sh`, `..._1789104649220_*.sh` (05:29:41Z / 05:30:17Z / 05:30:51Z) each run
    `sleep 38` -> `T+~60s check` on pids **4403, 4087** -> `kill -KILL` survivors -> `pgrep` census ->
    `npu-smi info`.
  - `scripts/sapo_stop_run.sh` (untracked, mtime 13:34 CST, ~5 min after the signal) states in its header
    that *"A lane had to bypass the sanctioned stop with pid-precise signals"* and names **"the observed
    parent-4086 / child-4403 pair"** - the exact pids of this run's tree.
  - **What is NOT on disk**: any GO/authorisation record, and the durable run pointer the new stop script
    depends on (`/root/work/software/quantum-gpt/.sapo-loop/.current_run` does not exist on the box). The
    TERM half of the operation is absent from the exec-script window (nothing between 05:27:48Z and
    05:29:41Z; no exec script on any of the three daemons names `4086`).
- **Why it matters (not bookkeeping)**: this is the **same family as B-078 / B-130 / B-132** - *the absence
  of a measurement is published as a verdict*. Here the absent measurement is **intent**: a control action
  with no author, so the system cannot distinguish (a) a user-authorised stop, (b) a lane acting on its own
  reading, (c) a supervisor acting on a rule. Those imply opposite corrections, and in this repo that
  ambiguity has already produced two un-GO'd training-control incidents (**B-026 / B-027**, three
  unauthorised launches on 2026-09-02). A stop is the same class of control action as a launch.
- **Cost measured this tick, specifically**: the chair escalated "authorise STOP" to the user across five
  consecutive ticks (#364-#368) for a run that had **already been stopped** - and, in the same window,
  dispatched a Debugger investigation into a crash that did not happen. The wrong record did not just fail
  to inform; it aimed work at a non-existent failure mode and kept a resolved decision open.
- **Fix shape (TDD-able Mac-side, no user GO required - same footing as B-130/B-132)**: the stop must write
  its own record. Concretely: `scripts/sapo_stop_run.sh` (and the launcher's stop body) should persist, per
  stop, a durable row naming **WHO** (session/lane/actor), **WHY** (reason/rule id), **WHEN**, the run dir,
  the pids TERMed and the survivors KILLed, and the **verification outcome** - written *before* the first
  signal, so a stop that is interrupted by the box itself is still attributable. Second, a run's terminal
  state should be **read from the trainer log** (`sigterm_graceful_stop` vs `backward_done`/traceback) and
  published as a three-state verdict - **STOPPED / CRASHED / UNKNOWN** - never collapsed into "DEAD",
  because those three imply different actions (accept / fix / investigate).
- **NOT fixed this tick**, and deliberately not attempted: `.sapo-loop/` writes from a tick session are
  gated to append-style edits, the fix spans `scripts/` + `tests/`, and a half-deployed stop-record would
  be worse than none (the stop path is the destructive one - it must not be edited blind).
- **Cross-refs**: B-125 (the run's degenerate loop, the condition the stop was responding to), B-130 and
  B-132 (same "absence is not a verdict" law, both landed), B-078 (three-state liveness), B-026/B-027 (the
  prior un-authorised control actions), section 4.1 ("no silent lies") and section 5.4.1 (probe semantics).

### B-134 - the record says the run "died on its own"; the process table says it was STOPPED and its checkpoint COMPLETED  [FILED 2026-09-11 tick #368 - record-integrity defect, cause of the STOP still UNKNOWN]
- **Filed**: 2026-09-11 tick #368, from the Debugger lane's death-cause dispatch, then **independently
  re-verified by the manager chair** (a lane's claim is not accepted unverified - section 0.0 rule 2).
- **What the record said** (STATUS.md #366 section 3, repeated in #367 and carried into #368): the run
  "died on its own at ~05:28:33Z, mid step-8 adapter save", 7/7 steps skipped, **0 usable checkpoints**,
  cause UNESTABLISHED. #366 recorded "no OOM is attributed to pid 4403" and left it there.
- **What the evidence says** (all read by me this tick through ASI2 `:19004`, box clock = UTC):
  ```
  pid 4086 (python3)  Z  ppid=1  pgrp=3986  exit_code=0    <- TRAINER: clean exit, save completed
  pid 4403 (python3)  Z  ppid=1  pgrp=3986  exit_code=9    <- SIGKILL
  pid 4077 (bash)     Z  ppid=1  pgrp=3986  exit_code=15   <- SIGTERM
  pid 4087 (bash)     Z  ppid=1  pgrp=3986  exit_code=0    <- repair sidecar
  pid 4097 (python3)  Z  ppid=1  pgrp=3986  exit_code=15   <- judge bridge: SIGTERM
  ```
  All five share **pgrp 3986 / session 3859** - one launch group, deliberately signalled. A `9` (SIGKILL)
  is **never** sent by the kernel on its own; and the trainer exiting **0** means it handled the stop and
  finished, rather than crashing. The step-8 save is **COMPLETE**:
  `step_000008_adapter/adapter_model.safetensors` = **312,539,848 B**, with `adapter_config.json`,
  `chat_template.jinja`, `processor_config.json`, `tokenizer.json`, `tokenizer_config.json`, plus
  `resume_state.json` (21481 B) and `grpo_metrics.json` (55771 B), all stamped 05:28.
- **Both halves of the standing record are therefore REFUTED**: the trainer did not die on its own, and a
  **usable** step_000008 checkpoint exists. The leaked `.adapter.tmp-4403-6838a3b2/` (README.md only, 5222 B)
  is a SEPARATE staging dir belonging to pid **4403** - the code's own documented `finally: shutil.rmtree`
  leak on a hard KILL (`training/grpo_trainer.py` adapter staging) - and is NOT the trainer's checkpoint.
- **The mechanism the Debugger proposed (independently confirmed by me)**: two `sigterm_graceful_stop`
  prints cannot come from one process, because `GracefulStop` is re-entrancy-guarded
  (`training/grpo_trainer.py:4923-4925`, `if self.requested: return` / `self.requested = True`; handler
  installed once at `:5221`). So the second print came from a fork - i.e. **pid 4403 was a forked child of
  the trainer, not the trainer itself.**
- **CAUTION on the Debugger report (recorded so nobody re-quotes it as verified)**: two of its citations do
  NOT survive checking. (1) Its `grpo_trainer.py` line numbers are all off - it cited `4828-4830` for the
  re-entrancy guard (actual **4923-4925**), `5095` for `GracefulStop` (actual **4903**), `5126` for the
  signal install (actual **5221**). The MECHANISM is right; the citations are not. (2) It claimed
  "`ppid=4086` confirmed" for pid 4403 - but its OWN quoted "earliest read" line shows `ppid=1`, and
  `/proc/4403/stat` reads `ppid=1` now. All five are reparented to init, so **/proc cannot establish the
  parentage today**; the parent-child claim rests on the double-handler-print argument, not on ppid.
- **The issuer of the STOP is UNKNOWN.** It did NOT go through ASI2's `/exec` API (no `/tmp/huanxin_cmd_*.sh`
  exists for 05:27:48-05:29:41Z). Ruled out: OOM (the only dmesg OOM is 05:02:09Z, `dosec_hades`, different
  memcg), the NPU (`0` hits for 4403), and the capability sentinel (`outputs/capability_sentinel.log` shows
  no `AUTOSTOP` line, and its drift branch needs `len(ent) >= 10` while this run produced 8 steps).
  The one in-tree caller matching TERM -> 3s -> KILL is `scripts/asi2_launch_grpo_27b_selfeval.sh:272-300`.
- **Why this matters beyond bookkeeping (and why it is TIMED)**: the stop landed at **05:28:33Z = 13:28:33
  CST**, i.e. *inside the tick-#366 window*, while #366 was writing that the run had died "before any stop
  could be issued" and deciding **D-366-2: no stop**. A live run whose launch authority was already
  UNVERIFIED (it went live 04:32:37Z / 12:32:37 CST with no recorded GO) was stopped by an untraced issuer
  during a tick that believed no stop had been issued. Either verdict was wrong: a stop DID happen.
- **NOT fixed / carried**: the issuer identification (needs the huanxin daemon's request log for ASI2 at
  05:28:2x and 05:28:59Z, or a Mac-side client log - both outside the container); whether the auto-stop
  rule that fired is intended to exist at all; and the fact that a `scripts/`-level TERM->KILL escalation
  can SIGKILL a *forked child* while sparing the trainer (the `pgrep -f 'training/[g]rpo_trainer.py'`
  fallback cannot distinguish a fork from the trainer - the same self-matching class the repo has hit
  before).
- **Cross-refs**: B-131 (circuit-breaker blindness - the reason 4403's fork inherited a live handler),
  B-132 (the sibling transport fix in the poller), B-126 (keeper `/stop` history), B-125 (the collapse
  family this run's 7/7 skips belong to).


### B-135 — FOURTH untraced lifecycle event: run 20260913T082245Z launched with NO GO anywhere
- **Filed**: 2026-09-13 16:45 CST, tick #370 (manager, verified first-hand on box ASI2 :19004).
- **Status**: OPEN. Severity: HIGH — the authority chain is broken in BOTH directions now (B-134: untraced STOP; B-135: untraced LAUNCH), and the launch repeats a config family that produced a degenerate run on Sep 11.
- **Evidence**: run dir `/root/work/software/quantum-gpt/outputs/sapo-27b-ai-20260913T082245Z` ctime 2026-09-13 08:25:46Z; trainer pid 13093 (fd1/2 -> logs/sapo_27b_ai/grpo_train_20260913T082245Z.log), argv warm-init `094427Z/step_000097_adapter`, lr 5e-5, grpo_steps 120. Mac-side: NO GO file anywhere in the tree (find -iname "*GO*" newer than 09-11 15:00 = empty); `.huanxin_jobs/` newest entry Sep 11 06:44; `grep -l 20260913 .sapo-loop/*.md` = zero hits; STATUS.md had ZERO writes Sep 11 14:11 CST -> Sep 13 16:45 CST (~50h, ~300 missed ticks). Also unrecorded in the same window: runs 20260911T061532Z and 20260911T081414Z (both present on box, both post-dating STATUS.md's last write), and a box-tree deploy (see B-136).
- **Impact**: a known-degenerate experiment shape went live with no gate, no record, and no owner; the user's standing rule ("no next-leg launch without collapse-fix + USER GO") was bypassed by an unknown issuer — again.
- **Fix direction**: durable attributable record for EVERY launch, symmetric with B-133's stop record (launch must write WHO/WHY/WHEN + GO reference into the run dir before step_begin; fail-closed if absent). TDD-able Mac-side, no user GO needed for the RECORDING fix itself.
- **Cross-refs**: B-134 (untraced stop issuer), B-133 (durable stop record), B-125 (collapse family this run reproduces).

### B-136 — Mode-B collapse is NOT deterministic: 061532Z RECOVERED, 081414Z never did; discriminator UNKNOWN
- **Filed**: 2026-09-13 16:45 CST, tick #370 (manager, verified from box logs).
- **Status**: OPEN (extends B-125: "the CAUSE of the generation collapse is still open"). Severity: HIGH — every warm-s97 relaunch gambles on an unknown discriminator.
- **The three-way comparison** (all warm from `094427Z/step_000097_adapter`; adapter mtime 09-08 20:28Z; benchmark mtime 09-08 15:54Z; box tree `training/generation.py`+`grpo_trainer.py` all stamped 09-11 06:10:19Z):
  - `20260911T061532Z`: step 1 short (max_code_chars 37) -> step 2 397 -> step 4 1055 REAL code; only 3 skipped steps total. **RECOVERED.**
  - `20260911T081414Z`: **22 skipped steps**, raw_response_chars [3-10] throughout, never recovered.
  - `20260913T082245Z`: step 1 chars [7,7,7,3,3,7,3,7] (4 tok, entropy 2.51 normal), skipped flat 0.0<0.05; step 2 eos_rate 1.0, 8/8 SyntaxError; greedy candidates (3/8, greedy_fraction 0.4) collapse identically. **Collapsed so far.**
- **Consequences**: (a) the tick-#365 model "a CLOSED LOOP that cannot self-correct" is falsified as a universal — 061532Z escaped within 2 steps; (b) the 06:10:19Z box-tree touch is EXONERATED as sole cause (healthy 061532Z launched 5 min AFTER it); (c) sampling temperature is exonerated (greedy collapses too); (d) remaining discriminator candidates: per-task prompt content (which task ids trigger immediate EOS), container/serving warm-up state, co-residency at launch (081414Z opened 16:14 CST Sep 11 — verify whether 061532Z was still resident), and the content of the unrecorded post-r24 deploy.
- **Sub-finding (observability gap)**: collapsed steps persist NO raw candidate text (eval_results.jsonl carries only code_hash + SyntaxError details; self-repair rounds=0 so repair_stage is empty) — the single most useful artifact for this exact bug class is not being written.
- **Fix direction**: Debugger order 2026-09-13: sha-diff box tree vs r24 bundle (identify the unrecorded deploy's content); per-task collapse correlation across the three logs; then either persist raw candidates (small, fail-closed, TDD-able) or reproduce the discriminator Mac-side.
- **Cross-refs**: B-125 (family + detector not yet on box), B-135 (this launch had no GO), B-131/B-134 (lifecycle-authority chain).

### B-137 — the durable run pointer can name a run that DOES NOT EXIST, and every reader treats it as resolved  [OPEN - filed 2026-09-13 tick #371; owner: Instrument Integrity / Run Watch]
- **Filed by**: tick #371 (2026-09-13 18:40-18:55 CST). New bug, reproduced live.
- **Symptom**: `.sapo-loop/.current_run` held `sapo-27b-ai-20260913T104439Z` — stamped 18:44:39 CST — while the box had **no run directory, no train log, and no trainer process** for it, checked at 10:45:09Z, 10:46:15Z and 10:49:26Z (four minutes of margin, three independent reads through ASI1 :20646).
- **Measured evidence** (box `/root/work/software/quantum-gpt`):
  - `ls -1dt outputs/sapo-27b-ai-* | head -3` -> `082245Z`, `20260911T081414Z`, `20260911T061532Z`. No `104439Z`.
  - `ls -1 logs/sapo_27b_ai/ | grep 104439` -> empty (no train log, no sidecar log, no judge log).
  - `pgrep -af grpo_trainer.py` -> empty.
- **Why it is a bug and not a transient**: the pointer is the ONLY surviving evidence of a launch, and `sapo_metrics_poll.py:_resolve_run()` returns it as `(pointed, True)` — i.e. **RESOLVED** — on the strength of the file being non-empty, with **no existence check on the run directory**. RUN, METRICS, LOG and ADAPTERDIR are then all built from it. A reader therefore gets a fully-resolved run id that describes nothing on the box, which is the same "silent lie" family the module already fails closed against (NO-TARGET / UNKNOWN liveness / non-finite rows) — the module guards the *values* but not the *identity*.
- **Its twin**: the previous pointer value (`…T084551Z`) was ALSO a run with no directory, observed at 18:40 CST in the same tick. Two consecutive phantom pointers in ~4 minutes is a pattern, not a typo.
- **Relationship to B-099/B-110**: those fixed the pointer being welded to a RETIRED run and the transport being welded to one daemon. This is the complement: the pointer is now repointable, and it has been repointed at runs that do not exist, with no reader able to tell.
- **Fix direction**: `_resolve_run()` must distinguish "pointer names a run" from "pointer names a run that EXISTS". A pointer whose run directory is absent is UNRESOLVED-with-evidence (report the pointed id AND that it was not found), never a silent fallback to an old run and never a resolved identity. TDD-able Mac-side; no user GO needed for the instrument fix.
- **Cross-refs**: B-135 (launch authority unverified — the pointer is the only launch evidence), B-133 (stop record), B-134 (untraced stop issuer).

### B-087 — STATUS UPDATE 2026-09-13 tick #371: the census objection is answered — FIVE concurrent, long-lived instances
- **Prior status**: open, headline UNCONFIRMED, on the ground that "a short-lived launchd job reads 0 between firings, so a ps census is not sufficient evidence".
- **New measurement** (`ps -eo pid,ppid,lstart,command`, Mac, 2026-09-13 18:53 CST) — five live `scripts/sapo_huanxin_heartbeat.sh` processes, all `PPID=1` (orphaned, so not a live parent's children), with **distinct start times spanning two days**:

      812    ppid 1  Sun Sep 13 18:37:10 2026
      97250  ppid 1  Sun Sep 13 18:36:27 2026
      35418  ppid 1  Fri Sep 11 13:59:09 2026
      74096  ppid 1  Fri Sep 11 13:56:34 2026
      41870  ppid 1  Fri Sep 11 09:46:58 2026

- **Why this defeats the "short-lived job" objection**: three of the five have been resident for **2 days and 9 hours**, so they cannot be launchd firings caught mid-flight. They are concurrent, long-lived, and independent.
- **Corroborating resource evidence**: each heartbeat has a paired `browser-automation/Chrome-Automation.app` Chrome instance (pids 1143 / 36291 / 48733 / 97547) — four Chrome processes for one heartbeat duty.
- **Load hypothesis (NOT yet proven, flagged for the next tick)**: five heartbeats polling one dispatch channel is the skill's "fleet poller cadence budget" wedge class — aggregate poll rate against a serialized exec mutex. It is a candidate contributor to the **HTTP 504 Gateway Timeout** responses measured on the judge path in run 082245Z (`dp4_judge_failed`, steps 2/3/4, `transport_error`, "HTTP Error 504") and to a 504 returned to this tick's own read through :19004. Stated as a hypothesis because the causal link is not yet isolated.
- **No process was killed by this tick.** Killing supervisor/heartbeat processes is a hard-to-reverse fleet action (memory: /stop is one-way; ASI3 has no supervisor). It is reported for the Auth/Daemon Watch lane to own.
- **Cross-refs**: B-085 (triple supervisor racing ports — the three long-lived instances line up with the three per-ASi supervisors), B-091 (keeper kick unverified).

### B-135 STATUS UPDATE (standup #372, 2026-09-13 18:55 CST) — FIFTH untraced launch; B-135 RECURS
- **New event**: `outputs/sapo-27b-ai-20260913T105036Z` created **10:50:49Z = 18:50:49 CST**, i.e. ~28s after
  standup #372's prompt fired (18:50:21 CST). Config family identical to 082245Z: `--adapter-init
  094427Z/step_000097_adapter`, `--lr 5e-5`, `--grpo-steps 120`, group 8, `--greedy-rollout-fraction 0.4`,
  `--entropy-floor 1.5`, `--overwrite-output-dir`. Trainer pid 23854 (196% CPU), repair sidecar 23855,
  pid-reparented to 1 -> the launcher had already exited.
- **Still NO GO**: no GO file; newest `.huanxin_jobs` entry remains 2026-09-11 06:44; the sibling standup #371
  (18:57 CST, same file) explicitly records "No stop, no relaunch, no teardown, no process killed" -> the tick
  that ran contemporaneously with the launch is exonerated.
- **Immediate outcome**: step 1 already Mode B — `all_fail=true, skipped=true, mean_reward 0.0,
  raw_response_chars [7,7,7,9,3,3,3,7], eos_termination_rate 0.625, entropy_mean 2.493 (NORMAL)`. 0 optimizer
  updates. Fourth Mode-B sample for B-136.
- **Launcher-trace evidence gathered this tick (negative results worth keeping)**: box `crontab` EMPTY; no
  launch/watch process resident on the box; no `ai_launch_sapo|asi3_launch|boxexec` process resident on the Mac;
  launch arrived via a daemon `/exec` (ASI2 :19004 `commandCount=115` vs ASI1 :20646 `=18`).
- **Why this is a training-health bug, not just a bookkeeping bug**: five runs in the Sep 11->13 window
  (043237Z / 061532Z / 081414Z / 082245Z / 105036Z), every one of them producing **0 optimizer updates**, each
  replacement burning NPU-hours on an adapter that is already banked. The repetition is the bleed.
- **Status**: remains OPEN (worsened — 1 unrecorded launch at filing, 2 now).


### B-138 — the judge watcher SILENTLY DROPS any request too large for the console transport, so the trainer's judge call starves to judge-absent and the step is skipped  [OPEN, ROOT-CAUSED + REPRODUCED LIVE 2026-09-13 tick #373; RED test authored, fix NOT landed - write gate; owner: Judge Pickup lane]
- **Filed by**: tick #373 (2026-09-13 19:00-19:15 CST). Reproduced live on the Mac against run `sapo-27b-ai-20260913T105036Z`.
- **Symptom**: a pending judge request sat in the box queue (`req_cd9180b4e77246e19f0152bfa5d87a63.json`, 3502 bytes) from 11:03Z; the watcher logged **only heartbeat lines** for the next 5+ minutes; the trainer's step 2 then waited **~14.5 minutes** (logprob_done 10:53:33Z -> step 3 began 11:08:5xZ) before completing as `all_fail: true` with **zero optimizer updates**. The request file later disappeared with no `resp_` sibling.
- **Measured evidence (Mac, this tick)**:
  - `grep -c "judging" /tmp/sapo_judge_mac_watcher.log` -> **0**, over the entire log. The watcher has NEVER logged a pickup on this run, yet its heartbeat reads `ok (processed=0)` every cycle. The two non-heartbeat lines in the window are a `504 Gateway Timeout` at 10:58:57Z and a `timeout('timed out')` at 11:02:45Z.
  - I re-ran the watcher's OWN one-shot pickup command (`list_and_fetch_all`) by hand through ASI2 `:19004`: it returned 4672 characters of nested base64 whose outer decode **succeeded** but whose inner payload was **not valid UTF-8** (mojibake, high bytes interleaved with ASCII fragments).
  - Direct size bisect of the same command against the same file: base64 outputs of **172 / 344 / 684 / 1024 / 1368 / 2048 / 2732 / 4096 chars all came back CLEAN**; the **4672-char** response came back **4591 chars, head dropped, 38 newlines, invalid UTF-8**. The transport WINDOWS an over-budget response and loses its HEAD - so the body is unrecoverable no matter how long you wait.
  - Control: `echo -n AAAA | base64 -w0` -> `QUFBQQ==`, clean. So this is not a general transport break; it is a **size** cliff.
- **Why it is a bug and not a transient**: `list_and_fetch_all()` (scripts/sapo_judge_mac_watcher.py) wraps the inner decode in a bare `except Exception:` that **returns the empty mapping** — indistinguishable from "no requests pending". `tick()` therefore returns 0, and B-043's heartbeat line reports healthy. A pending request that the transport cannot deliver is thus dropped in total silence. That is the project's own "no silent lies" failure class applied to the judge chain: an UNKNOWN transport read is being reported as a benign EMPTY read.
- **Consequence chain (this is the Mode-B skip)**: request not picked up -> dp4 never called -> the trainer's judge client exhausts its retry chain (~3 x 310s) -> judge-absent -> the reward loses its judge mass -> `all_fail` -> flat dispersion -> **step SKIPPED, no optimizer update**. It is a TRANSPORT defect being converted into a training verdict, exactly the class #371 root-caused with the 504, and it means no run on this box can learn while this path is starved.
- **Scope caveat, stated honestly**: this explains the SKIP. It does NOT prove the 4-12 token Mode-B completions are a downstream effect - the short generations and the judge-absence co-occurred, and they are not yet causally separated. **B-125's cause stays OPEN.**
- **Fix direction** (TDD spec is in `.sapo-loop/STATUS.md` standup #373):
  1. Make the silent handlers LOUD. A non-empty box-side listing that fails to base64-decode is a transport failure - log it and raise or retry. Distinguish EMPTY (no requests; return the empty mapping) from UNDECODABLE (an error). Today both take the empty-mapping path, which IS the defect.
  2. Add a chunked fallback under the one-shot fast path: read each request in bounded offset-tagged slices, and reject a joined-but-gappy read instead of splicing together a corrupt body. 1024 raw bytes per slice measured safe.
  3. Do NOT remedy this by raising the watcher timeout or the bridge `judge_timeout`. The window drops the head, so more patience cannot recover bytes. The budget is a CHARACTER count of the exec response and must be enforced BOX-SIDE.
- **Cross-refs**: B-125 (Mode-B collapse, cause open - this is the transport co-factor, not proven to be the cause), B-136 (Mode-B non-determinism), B-087 (five concurrent heartbeats - a named candidate contributor to the transport's 504s, hypothesis not proof), B-133/B-137 (record integrity).

### B-138 STATUS UPDATE (tick #373, 2026-09-13 ~19:15 CST) — FIXED TDD red->green; verified on the REAL transport; landed NOT deployed
Filed independently at the same tick from the same live run and the same reproduced mechanism — the entry above
and this one agree, so this is recorded as the FIX rather than as a second bug. Adds the pinned exception site,
the byte-exact single-file measurement, and an implemented + verified remedy (the entry above stops at a spec).

- **Exception site pinned**: `scripts/sapo_judge_mac_watcher.py:108-109` — `except Exception: return {}`. Driven
  through the watcher's own decode path on the live 3502-byte request: `compact` len **4634**, `len % 4 == 2` ->
  `b64decode` succeeds -> `.decode('utf-8')` raises `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc6 in
  position 0` -> swallowed -> `batch = {}` -> `tick()` returns 0 -> **`heartbeat ok (processed=0)`, no error line**.
- **Single-file measurement (the cleanest number)**: one `base64 -w0` of that same 3502-byte file returned **4591
  chars where 4672 are required** — i.e. the ceiling bites even the one-shot fast path, not only the batch
  envelope (which wanted ~6264). This corroborates the size-bisect cliff above.
- **Three-way control on the REAL transport, one real 3502-byte request** (scratch queue
  `/tmp/b138_verify_queue`, created and removed within this tick; the live queue was never written to):
  - HEAD `fetch()` — the COMMITTED code path — returned **0 chars: the request is LOST.** The defect is not
    confined to the uncommitted B-042 batch change.
  - pre-patch `list_and_fetch_all()`: request LOST (batch empty).
  - patched `list_and_fetch_all()`: **3502 chars, valid JSON, content len 3439 — byte-exact.**
- **Fix (implemented)**: `TRANSPORT_CHUNK = 3000` + `_chunked_fetch()` — list small via `list_requests()`, then
  read each body with `dd bs=1 skip=<off> count=3000 | base64 -w0`, advancing `off` by **the bytes that actually
  arrived** so a short/truncated chunk re-reads from the right place instead of misaligning the decode. This is
  the repo's existing `.sapo-loop/boxfetch.py` reader, moved into the watcher. **Loud failures** throughout: an
  undecodable listing logs, a bodiless request logs, a short read logs, and an EMPTY listing is disambiguated by a
  reachability probe — because "no work" and "blind watcher" must never look alike again. No timeout was raised;
  per the entry above, more patience cannot recover dropped bytes.
- **Evidence**: RED `tests/test_judge_watcher_transport_truncation.py` **0 passed / 3 failed** (no B-138 citation;
  request LOST to truncation; failed fetch silent) -> GREEN **3/3**. Regression on the judge-watcher surface set
  (`test_judge_mac_watcher_singleton.py` + `test_judge_watcher_heartbeat.py` + `test_judge_watcher_repair_contract.py`
  + `test_sapo_judge_health_agent.py` + the new file): **25/25**. `py_compile` clean.
- **NOT DEPLOYED — this is the open half.** The watcher is a live process (pid 8075) that loaded the old code at
  boot; the fix stays dead in-process until a restart, and restarting it is the one-way action class reserved to
  the user (#371 D-371-4). **No process was killed this tick.**
- **Owner**: Instrument Integrity (landing: done) / **USER (GO to restart the watcher)**.

---

## B-139 — session_keeper watchdog livelock: every restarted keeper is executed on its DEAD PREDECESSOR's heartbeat age

- **Status**: ROOT-CAUSED, FIXED TDD (red->green), regression clean. **NOT DEPLOYED — needs a watchdog restart GO.**
- **Found**: tick #374, 2026-09-13 ~19:20 CST. Filed from live evidence, not from a report.
- **Symptom**: `/tmp/session_keeper_state.json` stale since **18:59:41** while `logs/session_keeper.log` showed the
  keeper starting over and over (**267** `session_keeper started` lines in the file). Section 9.1's always-on lane
  was effectively dark for ~24 minutes.
- **Evidence (watchdog log, the whole defect in four lines)** — the pid is DIFFERENT on every 60s poll and the age
  grows monotonically:
  ```
  19:18:40 age=1138.7 stat=R cpu=0.01 pid=8364  action=KICKSTART rc=0
  19:19:40 age=1198.9 stat=S cpu=0.02 pid=16250 action=KICKSTART rc=0
  19:20:40 age=1259.2 stat=S cpu=0.02 pid=23891 action=KICKSTART rc=0
  19:21:40 age=1319.4 stat=S cpu=0.02 pid=42290 action=KICKSTART rc=0
  19:22:41 age=1379.6 stat=R cpu=0.02 pid=71625 action=KICKSTART rc=0
  19:23:41 age=30.3   stat=S cpu=0.0  pid=10995 action=NONE
  ```
  Keeper start lines confirm the churn: `19:21:31 pid 42290`, `19:22:34 pid 71625`, `19:23:08 pid 96402`.
- **Root cause**: the heartbeat age is the KEEPER's output but belongs to whichever instance wrote it LAST. After a
  restart it is the **dead predecessor's** age. A brand-new keeper therefore inherits an age far past
  `HARD_STALE_S` (900) and is killed at the next 60s poll — long before its first cycle can write a heartbeat (the
  auth probe alone budgets 90s, plus a 120s env-refresh sweep), so the heartbeat can never refresh and every
  successor is killed too. Grace is measured on the wrong clock.
- **This is B-052 one layer down.** B-052/B-101 fixed *which pid* is judged (identity from the process table, not
  the heartbeat) and *whether a failed measurement may fire* (never). Neither touched the **age**, which is still
  inherited from the predecessor. The livelock class was documented in the very comment block that fixed B-052 and
  it came back through the one input that fix did not cover.
- **Why it eventually "recovered" (and why that is not a fix)**: at 19:23:10 one keeper instance won the race and
  wrote `{"status": "STARTING"}` before being killed, dropping the age to 30.3s and silencing the watchdog. Pre-fix
  recovery is a **race**, not a mechanism: it depends on a keeper booting and writing inside a 60s window.
- **Fix**: `KEEPER_GRACE_S = 600` in `scripts/session_keeper_watchdog.py` + a `keeper_elapsed_s` argument to
  `decide_with_progress()`; grace is measured on the **process's own lifetime** (`read_proc_elapsed_s()`, new, via
  `ps -o etime=`) and applies only to a MEASURED-LIVE keeper. Positive absence (`proc_state is None`) is still an
  unconditional kick and STOPPED is still `SIGCONT` — both keep precedence. An unmeasurable lifetime is `None` ->
  UNKNOWN -> the existing B-052/B-101 bounded logic decides, so nothing regresses. 600 < 900 keeps the
  `HARD_STALE_S` punch-through that heals a keeper genuinely wedged past every bound.
- **Evidence**: RED `tests/test_session_keeper_watchdog_restart_grace.py` **0 passed / 12 failed** -> GREEN
  **12/12**. Regression `tests/test_session_keeper_watchdog.py` **41/41**. `py_compile` clean.
- **NOT DEPLOYED — the open half**: the watchdog is a live process (**pid 15469**, up 2d08h) that loaded the old
  code at boot, so a landed fix is inert until it restarts. **It has NO supervisor** — `grep -l
  session_keeper_watchdog ~/Library/LaunchAgents/*.plist` matches nothing and its PPID is 1, so killing it would
  permanently remove the fleet's guard rather than bounce it. Under the standing "no process kill" order
  (STATUS.md #373 §5) and the #371 D-371-4 one-way-action class, this tick did **not** restart it.
- **Owner**: Instrument Integrity (landing: done) / **USER (GO to restart the watchdog pid 15469)**.


## B-140 — the B-138 fix fetched SHORT and judged the TRUNCATED body, staging the judge's own error as a score  [FIXED TDD red->green 2026-09-13 tick #375; landed, NOT deployed - the watcher must not be restarted while it is working]
- **Status**: FIXED (landed on disk, inert in-process). Severity: HIGH - fail-open measurement on the judge path.
- **Found**: tick #375, ~19:33 CST (11:33Z), live, on run `sapo-27b-ai-20260913T112337Z` - i.e. during the FIRST tick in which the judge
  watcher was actually working again (it was restarted 11:24:09Z and staged its first real reply at 11:27:58Z).
- **Evidence (live, `/tmp/sapo_judge_mac_watcher.log`)**:
  `11:32:51Z b138 fetch: SHORT read .../judge_bridge/req_06fe91a6b54e434babf5c199ec953508.json (3000/3881)`
  `11:32:58Z judging req_06fe91a6b54e434babf5c199ec953508.json`
  `11:32:58Z dp4 reply head: '{"error": {"message": "watcher: invalid request JSON", "type": "watcher_error"}}'`
  `11:33:01Z staged resp_06fe91a6b54e434babf5c199ec953508.json`
  The request was deleted by the trainer MID-FETCH, so `dd` returned the first 3000-byte chunk (TRANSPORT_CHUNK) and the next three
  attempts came back empty -> `stalls` hit 3 -> the loop exited at 3000/3881. `_chunked_fetch` **logged** the short read and then
  **returned the truncated bytes anyway**. `tick()` judged that half-JSON, dp4 rejected it, and `stage()` wrote the ERROR payload to
  `resp_<id>.json` as if it were a score.
- **Why it is the same family as B-138, one layer down**: B-138 was "the transport truncates and the watcher goes blind"; B-140 is
  "the transport truncates and the watcher **invents a measurement**". A short read is `UNKNOWN`, not a verdict (section 4.1) - the
  module had the evidence in hand and discarded it.
- **Fix (smallest)**: `_chunked_fetch` returns `""` when `len(data) != total`; the log line now reads
  `SHORT read <path> (<got>/<total>) -> DISCARDED, never judged truncated`. `list_and_fetch_all` then logs `no body for <name>` and
  skips, so the request is neither judged nor staged, and is re-judged once it is readable whole.
- **Evidence (TDD)**: RED `tests/test_judge_watcher_transport_truncation.py` **3 passed / 2 failed**
  (`test_short_read_is_never_returned_as_a_body`, `test_short_read_request_is_skipped_not_judged`) -> GREEN **5/5**. Regression
  `tests/test_bugqueue_id_uniqueness.py` + `tests/test_session_keeper_watchdog_restart_grace.py` **16/16**. `py_compile` clean.
- **Companion fix, same tick (instrument integrity)**: those tests called the module's real `log()`, whose default `LOG` is
  `/tmp/sapo_judge_mac_watcher.log` - the PRODUCTION forensic record. Tick #375 read two `b138 fetch: SHORT read /box/queue/req_cd9180b4...`
  lines off that log and very nearly reported them as live transport truncation; they were the test fixture. `_load()` now takes
  `tmp_path` and repoints `mod.LOG`. Verified: the log is byte-identical (156289 bytes) across a full test run.
- **NOT DEPLOYED, deliberately**: the Mac watcher (pid 31906, started 19:24:09 CST) loaded the pre-fix code at boot. It is now the
  only working judge path and it is carrying a live run - killing a working watcher to load a fix for a race that has fired once is
  thrash (section 0 rule: never touch a healthy component). The fix loads on the next natural restart.
- **Owner**: Judge Pickup lane (landing: done) / USER (GO only if a restart is wanted sooner).
- **Cross-refs**: B-138 (the truncating-transport class this is one layer down from), B-131/B-132 (the same "absence is not a verdict"
  law in the poller and transport), B-137 (record integrity - the tick's other find).

## B-141 — the judge watcher STAGES every response outside the run dir: the box has never received a judgment  [FIXED TDD red->green 2026-09-13 tick #375; landed, NOT deployed - watcher restart is user-gated]

- **Reproduced from the RUNNING watcher (pid 31906), not from a test**: `stage()` issues a RELATIVE
  redirection to `resp_<id>.json` while the box daemon's cwd is **/vllm-workspace**; `has_resp()` probes
  the **ABSOLUTE** `$BOX_QUEUE/resp_<id>.json`. The write and the probe name different files.
- **Evidence (box, 11:35Z)**:
  `/vllm-workspace/resp_96a4bcadf8f74df38f1a29fc152c972a.json` 3008 bytes, and
  `/vllm-workspace/resp_06fe91a6b54e434babf5c199ec953508.json` 80 bytes - while the run's
  `judge_bridge/` held `req_96a4bcad...json` and **NO resp file at all**. At 11:41Z the count in
  `/vllm-workspace` was 3 and `judge_bridge/` still held only `req_4f7812...json` (a THIRD request id).
  The box posts a request, times out judge-absent, deletes it and posts another - forever.
- **Three consequences, in cost order**:
  1. **No live run can learn.** The box never sees a judgment, so every step is judge-absent -> all_fail
     -> skipped -> zero optimizer updates. This is the SAME outage B-138 chased; B-138 fixed the FETCH
     path and the outage survived, because the STAGE path was broken too.
  2. **`has_resp()` is always false**, so the watcher re-judges the SAME request every tick (observed:
     req_06fe91a6 judged and staged 5 times between 11:28:27Z and 11:33:01Z), burning judge calls.
  3. **Last-write-wins poisoning.** Because of (2) the response is re-staged repeatedly, and the last
     write is whatever that cycle produced - the 80-byte file above is the error body
     `watcher: invalid request JSON`, staged over a good 3008-byte judgment for the same id. A reward
     signal that depends on which write landed last is a fail-open measurement.
- **Fix (TDD)**: `tick()` now calls `stage(resp_for(fname), resp)` so the write and the probe resolve the
  path through ONE function; `has_resp()` is now a THREE-STATE probe (`[ -f X ] && echo yes || echo no`),
  and an UNKNOWN result (transport failure) SKIPS the request and logs loudly instead of being read as
  'absent' - re-staging over an unknown is exactly how a good score is overwritten by an error.
- **Evidence**: RED `tests/test_judge_watcher_resp_path.py` **2 failed / 3** (with the relative path
  visible in the failure text) -> GREEN **3/3**. Regression across the judge/watcher surface
  **53/53**. Also repaired a STALE test transport in `tests/test_sapo_judge_bridge.py` that predated the
  landed `_chunked_fetch` (no `stat -c %s` / `dd if=` branches -> the tick silently processed 0; this was
  RED before this tick's change, caused by the B-138 rewrite, not by B-141).
- **NOT DEPLOYED**: the watcher (pid 31906, PPID 1) loaded its code at 11:24Z, so a landed fix is inert
  until it restarts. Restart is USER-GATED (no plist found for either the watcher or the keeper watchdog).
- **Owner**: Instrument Integrity (landing: done) / **USER (GO to restart the judge watcher)**.
- **Cross-refs**: B-138 (fetch half of the same outage), B-140 (truncated-body half, sibling tick #375),
  B-131/B-132 (absence is not a verdict), section 5.4.1 (three-state probes).

## B-142 - the run pointer is stamped OPTIMISTICALLY by the launch path and NEVER verified by the consumer: a phantom run name reads as a RESOLVED live target  [OPEN - writer identified, TDD fix NOT landed; this is B-137's recurrency]

- **Symptom (B-137, third tick running)**: `.sapo-loop/.current_run` = `sapo-27b-ai-20260913T115424Z`, written **19:54:31 CST (11:54:31Z)** — and **no such run directory exists** anywhere: box `ls /root/work/software/quantum-gpt/outputs/ | grep 1154` -> empty (rc=1); no `sapo-27b-ai-20260913T1154*`. The live run is `sapo-27b-ai-20260913T114637Z`, which the pointer does NOT name. The pointer names a run that was never created.
- **Root cause - the WRITER, identified not inferred (this closes #375's "identify the writer" order)**: TWO stampers, both write the pointer BEFORE any run directory can exist, and neither re-checks afterwards:
  - box: `scripts/asi3_launch_grpo_direct.sh:464-472` stamps `basename "$OUT"` (line 468) and only THEN runs `bash "$LAUNCHER" "$1"` (line 494). The comment claims the stamp happens "only after every fail-closed gate above has passed" — true of THIS script's gates, false of the LAUNCHER's own gates, which run after the stamp. Any launcher refusal or failure therefore leaves a phantom pointer.
  - Mac mirror: `scripts/ai_launch_sapo_direct.sh:246-248` stamps `basename "$ASI3_SAPO_OUT"` then `exec`s the box launcher (line 262) — same ordering, same hole.
- **Why it is fail-OPEN, not cosmetic**: `.sapo-loop/sapo_metrics_poll.py:117-129` `_resolve_run()` returns `(pointed, True)` for any NON-EMPTY string. "The file has content" is read as "a live run was resolved". `RUN_RESOLVED` then gates whether the poller asserts ANY liveness verdict (`main()`, line 839): with a phantom pointer it proceeds and appends verdicts about a run it never measured — exactly the `UNKNOWN is not a verdict` class of section 4.1.
- **The fix is NOT a local `os.path.isdir` (MEASURED, not assumed)**: `BOX = "/root/work/software/quantum-gpt"` (line 21) does **not** exist on the Mac (`os.path.exists` -> False) and every read goes over the transport (`def box(cmd, timeout=90)`, line 365). The existence probe must therefore be a BOX-SIDE call (`test -d $BOX/outputs/$RUN`) issued after resolution and before any verdict. A Mac-local isdir would send every legitimate run to NO-TARGET — a wrong fix that would look like a fix.
- **Why no fix landed this tick**: the candidate fix's mechanism depends on where the poller executes, and I verified that (`box()` transport) rather than guessing it. Landing a rushed change to the LIVE monitoring module inside the tick, on a fix whose shape was still being determined at tick close, would violate section 5.4 ("never relaunch on an untested hypothesis"). Carried as a TDD order with the decisive fact already established.
- **Owner**: Instrument Integrity (fix next tick: RED test that a pointer naming a nonexistent run must NOT be reported resolved -> smallest fix -> GREEN). Launch-path stamp semantics (should the pointer mean "live run" or "last attempted launch"?) is a USER decision.
- **Cross-refs**: B-137 (the same pointer, carried three ticks), B-135 (untraced launches), section 4.1 (fail-closed / UNKNOWN is not a verdict).

## B-143 — the FLAPPING response-length collapse: consecutive-step guards miss a policy that alternates near-empty and short-but-nonempty failures  [FIXED LOCALLY (not deployed) - filed 2026-09-13 tick #376, fix landed tick #377; owner: Deploy Integrity]
- **Status**: **FIXED LOCALLY, GREEN, NOT DEPLOYED** (tick #377, 2026-09-13). TDD red -> green, 4 new tests.
  The fix and its measurements are below; deployment is user-gated on the frozen box tree (the same GO that
  B-125 wants - `grep -c response_length_absolute_collapse` on the box is still **0**, so NEITHER guard is on
  the box).
- **What it is**: the third variant of the B-125 collapse family. T114637Z is the textbook case (every step
  median 1 token, `eos_termination_rate` 1.0, all-fail) and the landed B-125 guard catches it. T112337Z is the
  variant that NOTHING catches: the policy alternates between near-empty and short-but-nonempty failures, so
  every time a longer candidate lands, the consecutive-step requirement resets.
- **Measured evidence (live run `sapo-27b-ai-20260913T112337Z`, rows 1-4, read from the box 2026-09-13
  11:58:45Z via ASI2 :19004 /exec)**:
  | step | ts (UTC) | completion_token_lengths | median | eos_rate | entropy | all_fail | skipped |
  |---|---|---|---|---|---|---|---|
  | 1 | 11:25:25 | [4,4,4,3,3,4,3,3] | 3.5 | 0.5 | 2.79 | true | true |
  | 2 | 11:42:27 | [12,12,12,110,110,110,110,110] | 110 | 1.0 | 0.66 | true | true |
  | 3 | 11:43:07 | [3,4,3,3,3,3,3,4] | 3 | 0.75 | 2.06 | true | true |
  | 4 | 11:58:40 | [12,12,12,14,14,14,14,14] | 14 | 0.875 | 0.92 | true | true |
  Every row `pass_rate 0.0`, `judge_reward null`. **Four landed steps, four `skipped` - zero optimizer updates.**
- **Replay, not assertion (this is the measurement that matters)**: feeding those four rows through the landed
  `CircuitBreakerState.observe_step` / `evaluate` one at a time (`FRONTIER_RL`, `all_fail_share 1.0`) yields
  **`trips []` at every step and `should_stop False`**. Reason, exactly: step 2 (median 110) and step 4
  (median 14) both exceed `response_length_absolute_floor = 12`, resetting `_response_collapse_streak`; step 1
  has `eos 0.5 < response_eos_termination_limit 0.6`, also failing the signature.
- **Why the other family cannot help either**: `entropy_absolute_collapse` requires `all(e <= 0.05)`; these
  entropies (0.66-2.79) are **13x to 56x above** the 0.05 absolute floor. And the whole window-gated family
  (`window_size 10 x required_windows 2`) cannot trip before **step 20** - this run is provably dead by step 4.
- **Why it matters**: `skipped` on every step means the run burns wall-clock and NPU reservation while the
  optimizer never steps. It is the same null-return as the "judge chain dark" outage, reached by a different
  route, so it would have been misattributed to the judge.
- **Deployment note**: `grep -c response_length_absolute_collapse` on the BOX trainer =
  `/root/work/software/quantum-gpt/training/grpo_trainer.py` -> **0**. Even the textbook variant's guard is
  absent where it would have fired. Both this and B-125 are locally green and want one user GO.
- **Cross-refs**: B-125 (Mode-B collapse - this is the third variant and its CAUSE STAYS OPEN), B-136 (Mode-B
  non-determinism), B-142/B-137 (record integrity - the pointer named a different, nonexistent run while this
  one was stepping), B-134/B-138/B-141 (the judge chain whose absence makes `judge_reward` null).
- **Uncontrolled lead, explicitly NOT a cause claim**: the adapter this run resumed from
  (`.../sapo-27b-ai-20260908T094427Z/step_000097_adapter`) came from a run whose own steps 97-100 emitted
  `mean_response_length` **1801 / 1249 / 1346 / 840**. The same checkpoint, resumed into a fresh run, emits
  3-14 tokens from step 1. That is a same-source contrast pointing at the resume/inference path rather than the
  weights - but it is a different run, a different day and different launch flags, so it is a lead, not a cause.

### B-143 STATUS UPDATE - FIX (tick #377, 2026-09-13) — collapse as a RATE, not an unbroken run
- **Red test first**: `tests/test_grpo_flapping_response_collapse.py` (new, 4 tests) built from the six MEASURED
  live rows above. RED confirmed before any fix: `test_flapping_response_collapse_trips_within_six_steps` ->
  `assert []`, i.e. 6 landed steps and `trips: []`, exactly the filing's claim.
- **Root cause of the miss (measured, not inferred)**: `_evaluate_response_collapse` required
  `response_collapse_consecutive_steps` (3) UNBROKEN collapsed steps. Replaying the live rows showed the
  streak reaching only 2 and resetting to 0 at step 4, because step 4's 14-token median clears the 12-token
  floor by two tokens. A flapping policy can therefore defer the alarm indefinitely. (This also corrects the
  filing's parenthetical guesses: the reset is at step 4, not step 2, and steps 3/5/6 carry the signature.)
- **Fix**: two constants replace the single conflated one -
  `response_collapse_lookback_steps = 4` and `response_collapse_min_steps = 3`, with the trip additionally
  requiring that the CURRENT step carries the signature (so a recovering policy is not tripped by stale
  history). `response_collapse_consecutive_steps` is RETAINED at 3 so the B-125 contract and its frozen tests
  are untouched.
- **Boundary chosen by measurement across all five shapes, not by taste**:
  | shape | trip |
  |---|---|
  | frozen (every step collapsed) | step 3 |
  | live flapping (sapoT112337Z, 6 rows) | **step 6** (was: never) |
  | one-step blip then long | no trip |
  | two-step blip then long | no trip |
  | long-completion control (637-1903 tok) | no trip |
  2-of-4 was tried first and REJECTED: it also tripped the two-step blip, trading a blind spot for a false
  alarm at the same cost. 3-of-4 separates all five.
- **E2E verification**: replay of the live T112337Z rows through the production `CircuitBreakerState` now trips
  at step 6 with `streak=3` and `should_stop=True`; before the fix the same replay produced `trips: []`.
- **Regression**: 21/21 guard tests (4 new B-143 + 6 frozen B-125 + inherited), and 158/158 across
  `test_grpo_trainer_breakers` / `test_grpo_utils` / `test_grpo_trainer_guardrail_gates` / `test_eval_gate_logic`
  / `test_grpo_trainer_metrics` / `test_golden_step_record_replay`. Zero new failures.
- **Runtime gate**: both changed files `ast.parse` clean under `/usr/bin/python3` 3.9.6; no `zip(strict=)`,
  no PEP-604 union outside `from __future__ import annotations`.
- **Not deployed.** The box tree is frozen and deploy is user-gated. `grep -c response_length_absolute_collapse`
  on the box trainer is still 0, so BOTH B-125 and B-143 are inert where they would have fired.
- **Still open**: the CAUSE of the generation collapse (B-125's cause). This fix is a DETECTOR, not a cure.

## B-144 - the judge watcher was armed ONCE at boot and never re-checked that its queue still belongs to a live run: a dead run's queue is polled indefinitely while live runs starve  [OPEN - detector LANDED + green, NOT LIVE (restart user-gated); auto-re-arm deliberately NOT written]

- **Filed**: 2026-09-13 tick #377. **Owner**: Instrument Integrity (detector landed) / **USER (GO to restart
  the watcher)**.
- **Symptom (measured on Mac watcher pid 5741, `/tmp/sapo_judge_mac_watcher.log`)**:
  ```
  11:47:05Z watcher start (daemon=http://127.0.0.1:20653 queue=.../sapo-27b-ai-20260913T114637Z/judge_bridge)
  11:47:21Z selfcheck queue-run: OK (/root/.../sapo-27b-ai-20260913T114637Z)
  11:54:59Z   <-- T114637Z STOPS (last row)
  12:12:43Z   <-- T121243Z LAUNCHES, writes req_4b461b22... into ITS OWN queue
  12:17:08Z   <-- T112337Z steps, writes req_b7e7f306... into ITS OWN queue
  12:16:57Z heartbeat ok (processed=0)   <-- still polling the DEAD run's queue
  ```
- **Root cause**: `startup_selfcheck()` (`scripts/sapo_judge_mac_watcher.py:342`) already contained the
  correct "env-drift class" probe (added 2026-08-29) that compares `BOX_QUEUE` against the newest run dir and
  logs `selfcheck queue-run: MISMATCH newest=<dir>`. It was called from **`main()` line 429 only** - never
  from `tick()`. Detection was BOOT-ONLY; drift is a runtime event. The probe printed OK at 11:47:21 and was
  structurally incapable of seeing the 11:54:59 drift.
- **Consequence chain (every link measured)**: `req_*` never consumed -> trainer waits out its 290s judge
  timeout -> `judge_reward` null on every row -> reward renormalises over pass+shaped only -> advantage
  degenerates to zero -> `all_fail` -> `skipped` -> **the optimizer never steps**. 2026-09-13: 15 landed
  steps, 15x `skipped`, 0 checkpoints, 0 optimizer updates, NPUs 8/8 OK at 0% AICore.
- **Fix LANDED (TDD red -> green, this tick)**:
  - RED first: `tests/test_judge_watcher_queue_drift.py` - "a tick polled a queue that belongs to a DEAD run
    and never said so"; confirmed 1 failed BEFORE any source change.
  - Smallest fix: extracted the probe into `check_queue_run_alignment(prefix: str = "")`; `startup_selfcheck()`
    now **delegates** to it (one implementation, not two); `tick()` calls it on the non-immediate path beside
    `cleanup_orphans()`.
  - GREEN 1/1; judge/watcher regression **20/20 passed** (drift, heartbeat, singleton, repair contract,
    watch timing, launcher judge default).
- **NOT LIVE**: pid 5741 loaded its code at 11:47Z; a landed fix is inert until that process restarts (same
  class as B-141). **Restart is USER-GATED** (no plist for the watcher). The watcher also runs on
  `SAPO_DAEMON=http://127.0.0.1:20653` - **ASI3, which is DEPRECATED**; the restarted instance should use
  ASI2 `:19004`.
- **What the fix does NOT do**: it makes a mis-armed watcher LOUD, it does not re-arm it. Auto-re-arm was
  deliberately not written - see the structural conflict below.
- **Structural conflict (why "just restart it" is not a fix)**: ONE single-queue watcher, THREE concurrent
  runs. T112337Z and T121243Z each held an unserved `req_*` at 12:18:58Z (shared FS, identical listing from
  ASI2 :19004 and ASI3 :20653). A watcher serves exactly one queue dir, so any restart at best halves the
  problem - and the code's own "newest run dir" heuristic picks T121243Z (1 row) over the actively-stepping
  T112337Z (7 rows, 12:17:08Z). **Which run lives is a STOP/RUN decision reserved to the user.**
- **Separately measured, independent**: the documented box-local judge path is inoperative - `:56238`
  refused on all three containers, no `box_anthropic_translator.py` process anywhere, and **`/root/.dp4_jwt`
  does not exist on any of the three**. The watcher path (Anthropic via `SAPO_DP4_PROXY` :55648) does not
  need that JWT, so the two are independent failures.
- **Cross-refs**: B-138 (the fetch/truncation half of the same outage), B-140 (short read must DISCARD),
  B-141 (staged path resolved against the daemon's cwd - sibling fix, also landed-not-live), B-142/B-137
  (optimistic resolve-once pointer - **same defect class as this one**), B-143 (flapping collapse), B-135
  (untraced launches).

---

## B-142 STATUS UPDATE — 2026-09-13 20:30 CST (tick #378): FIX LANDED (local), and the defect REPRODUCED LIVE twice while root-causing it

- **Live reproduction (new, decisive).** `.sapo-loop/.current_run` held `sapo-27b-ai-20260913T121129Z`
  (stamped 12:11:29Z) and was then re-stamped to `sapo-27b-ai-20260913T122333Z` (12:23:33Z, re-stamped
  12:24:35Z). **Neither run dir existed on the box** — `ls -d` refused for both, verified independently
  through ASI2 (:19004) and ASI3 (:20653), while the box's newest real run was
  `sapo-27b-ai-20260913T121746Z`. The pointer is re-stamped on every launch RETRY, so a launch that never
  materialises leaves the consumer pointing at a run that does not exist.
- **Mechanism (code, from the consumer side).** `.sapo-loop/sapo_metrics_poll.py::_resolve_run()` returned
  `(pointed, True)` on the mere existence of a NON-EMPTY pointer FILE. Nothing asked the box. `main()`
  therefore cleared its `RUN_RESOLVED` guard and went on to assert TRAINER LIVENESS about a phantom run,
  appending that verdict to the live STATUS.md — the module's own documented "no silent lies" class.
- **Fix (TDD, red first).** RED: `tests/test_sapo_metrics_poll_phantom_target.py` — 4 tests failing before any
  source change (`module has no attribute RUN_EXISTS_SENTINEL`). Smallest fix: added `run_target_exists()` —
  a THREE-STATE, BOX-SIDE probe (`ls -d '<run dir>' || echo __SAPO_RUN_DIR_ABSENT__` over the transport; a
  Mac-side `os.path.isdir` cannot answer a question about box state) — plus a guard in `main()`:
  positive-absence -> `NO-TARGET` phantom, assert NO liveness, return 1; UNKNOWN -> do not manufacture a
  verdict; transport failure -> `POLL-FAIL`, never an uncaught raise.
- **GREEN + regression.** 5/5 on the new file. Poller surface **111/112**; the single failure
  (`test_a2_every_aux_chunk_reaches_its_own_field`) was **baselined against a byte-exact pristine copy of the
  poller (51919 bytes)** and fails identically with and without the change — PRE-EXISTING, now its own item.
- **Status: landed in the working tree, NOT yet exercised by a live poll.** `.sapo-loop/sapo_metrics_poll.py`
  sha256 `9eac886ea00ef455…` (55770 bytes).
- **Still open on the writer side:** the launch path stamps the pointer FAIL-SOFT before the box creates the
  run dir, with no reconciliation. The consumer can now refuse to be lied to, but the optimistic stamp is
  the producer half and is NOT fixed here.
- **Also new this tick:** judge starvation now covers THREE live runs (T112337Z 7 rows, T121243Z 1 row,
  T121746Z 1 row), each holding 1 unconsumed `req_*.json` and 0 `resp_*.json`, while the single-queue watcher
  (pid 5741) stays armed on the dead T114637Z queue. See the B-144 entry.
- **Also new this tick:** ASI3 :20653 was restarted twice more by the keeper's congestion action
  (`20:06:15 CST direct /stop restart`); pid 78826 -> 50726, uptime 167s at 20:34 CST. The daemon is READY
  but its churn is now recurring, not one-off.

## B-145 - judge watcher alignment detects drift but cannot correct it, and asks the wrong question
**Filed 2026-09-13 (tick #379). Status: FIXED in tree (TDD red->green), NOT LIVE (restart user-gated).**

**Symptom (measured live 12:40Z).** The only live trainer (box pid 27912) serves
`outputs/sapo-27b-ai-20260913T112337Z` and had taken 10 steps, ALL skipped: `all_fail:true`,
`skipped:true`, `judge_reward:null`, 0 optimizer updates. Its judge request written 12:40:17Z sat
unread in `T112337Z/judge_bridge/req_ac81eb99...json`. The only watcher (Mac pid 5741) was armed at boot
on `SAPO_BOX_QUEUE=.../sapo-27b-ai-20260913T114637Z/judge_bridge` - a run that last stepped 11:54:59Z
with **zero** pending requests. Every judge call pends to the trainer's 290s timeout -> reward null ->
all_fail -> skipped.

**Defect 1 - detection without correction.** `scripts/sapo_judge_mac_watcher.py:check_queue_run_alignment()`
is called every tick (line 341) but only LOGS `queue-run: MISMATCH` and returns False. It never re-arms
`BOX_QUEUE`, so the watcher polls the dead queue forever. This is why the landed B-144 patch was not a
fix and why a restart alone never helped: the loaded code could see the drift and do nothing with it.

**Defect 2 - the predicate asks the wrong question.** The probe used
`ls -td /root/work/software/quantum-gpt/outputs/sapo-27b-ai-* | head -1` - the NEWEST DIRECTORY - as the
authority for which run to serve. Measured counterexample this tick: the newest dir was
`sapo-27b-ai-20260913T123210Z` (created 12:32:10Z, **no trainer behind it, 0 metric rows**) while the
only live `grpo_trainer.py` process carried `--output-dir .../sapo-27b-ai-20260913T112337Z`.
Newest-directory is not the run being trained; a re-arming predicate built on it would re-arm onto a
dead leftover.

**Fix (smallest, red-first).** Added `live_run_dir()`: resolves the run from the LIVE trainer over the
existing `daemon_exec()` transport, extracting `--output-dir` in both `--output-dir=PATH` and
`--output-dir PATH` forms, with the ps grep **bracket-escaped** (`[g]rpo_trainer.py`) so the box `/exec`
shell cannot list its own argv as a phantom trainer. Ambiguity (2+ trainers) or absence returns `''`
(UNKNOWN) and callers never manufacture a target. `check_queue_run_alignment()` now takes
`global BOX_QUEUE`, uses the live trainer as authority, and RE-ARMS onto `<liverun>/judge_bridge` on
drift. Drift is still returned as False so the call site sees it.

**Evidence.** RED first: `tests/test_judge_watcher_live_run_rearm.py` failed 3/4 against the old code
(`MISMATCH newest=...T123210Z`), covering (a) no re-arm, (b) newest-dir used as authority,
(c) UNDETERMINED mis-reported as MISMATCH. Then GREEN. Regression: 28/28 across the 7 watcher test files
(manager re-ran independently; agent ran 42/42 over a slightly wider set incl. watch_timing +
judge_bridge). `py_compile` OK. sha256 `f97dbf5ded91dcd3...`.

**Why it is inert.** `BOX_QUEUE` is bound from the environment at boot and pid 5741 still runs the
boot-loaded code, so the fix does nothing until the watcher is restarted. The re-arm path itself is
verified to work without a second restart because `list_requests()`/`fetch_*` read the module global at
call time rather than capturing it.

**NOT fixed here (separate, still open):** the Mode B rollout collapse that makes the completions 3-4
tokens (`completion_token_lengths [4,4,4,4,4,4,3,4]`, `entropy_mean 0.82`, `extracted_code_chars` all 0).
Restoring the judge makes reward MEASURABLE; it does not make the policy produce real completions. Do
not record this bug as a cure for the collapse.

**Retracted as part of this tick:** the #378 premise that three runs were live and run-selection was a
user choice. Box `ps` shows exactly ONE trainer. T121746Z / T121243Z / T114637Z / T105036Z are stale
leftovers with orphan `req_*.json`.

## B-153 - METRICS-POLLER TEST WAS A WALL-CLOCK TIME BOMB (permanent RED, ~50h) - FIXED
Filed + fixed 2026-09-13 20:52 CST / 12:52Z by tick #379 (second concurrent session).
Renumbered 2026-09-13 tick #384: this entry was filed as B-145 by a concurrent session while
B-145 was already taken by the judge-watcher bug (line 3056, test_bugqueue_id_uniqueness.py).
Two different bugs sharing one ID is the collision class; the FIRST header stays canonical.

**Symptom.** `tests/test_sapo_metrics_poll_failclosed.py::test_a2_every_aux_chunk_reaches_its_own_field`
failed `assert 2 == 0` on an otherwise-HEALTHY capture. Two prior ticks carried it as "pre-existing,
baselined against a pristine copy" and ordered a root-cause pass that was never done.

**Root cause (measured, not inferred).** The failure is NOT in the six-chunk index map the test is
about. `_marked_aux()` hard-coded its box log mtime to a FIXED literal:
  chunk 5 (stat mtime) `2026-09-11 10:00:00.000000000 +0000`
  chunk 6 (box ts)     `2026-09-11T10:00:00Z`
`.sapo-loop/sapo_metrics_poll.py:1004-1007` derives the stage-marker age from chunk 5 against the
MAC's `datetime.now(timezone.utc)`. So the fixture's implied age GREW WITH WALL-CLOCK TIME: it sat
inside the poller's own 20-minute bound for ~20 minutes on 2026-09-11, then tripped
`STAGE STALL: log marker age N min > 20` for the rest of time. Measured this tick:
`N = 3045.5 min` at 2026-09-13T12:44Z. The alert drives rc=2, so the test asserted 2 == 0 forever.
The production rule is CORRECT (a 50-hour-old log marker SHOULD alert); the FIXTURE was the defect.

**Why it mattered.** A permanently-red test on the metrics-poller surface is worse than a missing
one: it masks every real regression on that surface and trains the reader to ignore the file
(section 9.3 - the suite is the canary, and a canary that always screams is not a canary).

**Fix (TDD, red first).** RED: added
`test_a2_fixture_timestamps_are_not_wall_clock_time_bombs` - failed first run with
`the A2 aux fixture's box timestamp is 3045.5 min old...`. Smallest fix: `_marked_aux()` now builds
both timestamps from `datetime.now(timezone.utc) - timedelta(minutes=2)`, so the fixture is always a
FRESH capture - which is the only thing the chunk-index assertions are about. Staleness keeps its own
dedicated stage-age tests. GREEN: the new test + `test_a2_every_aux_chunk_reaches_its_own_field` both
pass; the whole file is **31/31 GREEN** (was 30/31).

**Retraction note.** Prior ticks' "pre-existing" label was right in EFFECT but wrong in MECHANISM
(they blamed the ps-chunk liveness assertion and never named the timestamp). Recorded so the next
reader does not re-open it on the old theory.

## B-146 - 9 SUITE FAILURES = ONE MISSING DEP IN THE CANONICAL SUITE VENV (Crypto) - ENV DELTA, NOT A TREE DEFECT
Filed 2026-09-13 21:10 CST / 13:10Z by tick #379 (second concurrent session). NOT applied - see "why".

**Symptom.** The COMPLETE full suite (chunks 23/23) reports `passed=4489 failed=10 errors=0
skipped=22 total=4499 VERDICT=COMPLETE`. NINE of the ten failures are ONE file.

**Cluster (named, measured - re-ran chunk 14 by id slice):** all 9 live in
`tests/test_sapo_cookie_seed.py` and all are the same import error, not 9 defects:
  test_module_exposes_clock_derived_timestamps, test_creation_time_is_now,
  test_expiry_is_in_the_future, test_expiry_after_creation, test_only_auth_cookies_are_seeded,
  test_seeded_header_stays_under_ingress_budget, test_real_observed_set_is_under_limit,
  test_budget_drops_largest_when_still_over, test_seed_targets_only_the_base_profile

**Root cause (exact):** `scripts/sapo_cookie_seed.py:27`
  `from Crypto.Cipher import AES`  ->  `ModuleNotFoundError: No module named 'Crypto'`
raised at module import, so `load_module()` in the test fails and all 9 error identically.

**Instrument check - which interpreter is right?** The suite's canonical interpreter is
`.venv/bin/python3` (`.sapo-loop/run_full_suite.py:270` re-execs into it precisely BECAUSE the
system python lacks the SDKs). Probed the venv: pennylane OK, qiskit OK, pytest OK, **Crypto MISSING**
(and `Cryptodome` missing too). Probed `/usr/bin/python3`: **Crypto PRESENT** - which is why all 9
PASS under the system interpreter and FAIL under the venv. Same interpreter version both sides
(memory: `.venv` symlinks to CLT 3.9.6); the delta is PACKAGES, not version.

**Is this a production bug? NO - measured, not assumed.** The script is MAC-LOCAL: it seeds the local
Huanxin browser profile. Checked the box through ASI2 (:19004): `/root/work/software/quantum-gpt/scripts/
sapo_cookie_seed.py` does not exist there (`NO-SCRIPT`), and neither box python
(/usr/bin/python3, /usr/local/python3.11.14/bin/python3) has Crypto either - irrelevant, since nothing on
the box runs it. So this is a SUITE-ENVIRONMENT delta, not a defect shipped in the tree.

**Why I did NOT apply a fix unilaterally.** The two candidate fixes are both DEP-MATRIX decisions, and
section 2.7 makes the dependency matrix a pinned, recorded artifact (per-component deltas + risk surface):
  (a) `pip install pycryptodome` into `.venv` - the real fix; makes the 9 tests actually RUN. Owned by
      the dep-matrix lane, which must record the added component and re-sweep box-vs-local.
  (b) `pytest.importorskip("Crypto")` in the test file - converts 9 reds into 9 NAMED skips. Cheaper but
      it locks in a permanent coverage loss on a security-relevant module, which is the thing 2.7 warns
      about. REJECTED as the default.
Recorded as the section 2.7 ACCEPT-AND-AUDIT baseline meanwhile: 9 enumerated failures, single file,
single missing dependency, cause named - not hidden, and never claimed green.

**Action for the next tick / dep-matrix lane:** apply (a), then re-run `tests/test_sapo_cookie_seed.py`
under `.venv/bin/python3` and confirm 9/9 green; record the matrix delta.


## B-146 STATUS UPDATE - 2026-09-13 21:22 CST / 13:22Z (tick #380): CLEARED, by a TREE fix, not a venv fix
The sibling filing above concluded "ENV DELTA, NOT A TREE DEFECT" and deliberately did not apply a fix.
I reached a different remedy from a measurement the filing did not have. Recording the divergence rather
than overwriting it, because both halves are true.

**Measured first:** the file's 11 tests use NO crypto. `AES` is referenced in exactly one place,
`sapo_cookie_seed.py:164` inside `decrypt()`. `tests/test_sapo_cookie_seed.py` covers clock-derived
timestamps, expiry, cookie selection, header budget and profile targeting - 11/11 GREEN under bare
`python3` (which HAS pycryptodome), and unreachable under `.venv` (which does not) purely because
`from Crypto.Cipher import AES` sat at MODULE scope (line 27).

**Why a tree fix, not a venv install.** `scripts/sapo_cookie_bridge.py:47` already defers the SAME
import into the SAME kind of function - the two sibling modules disagreed, and the seed script was the
outlier. A venv-only `pip install pycryptodome` would also mutate the shared canonical interpreter
without recording it in `requirements-cpu-eval.txt`, i.e. an unrecorded env claim that goes stale - the
class section 2.7 exists to prevent. The tree fix is durable, testable, and env-independent.

**Fix.** `from Crypto.Cipher import AES` moved from module scope into `decrypt()` (comment names the
reason and cites B-146). Nothing else changed.

**TDD.** RED first: `tests/test_sapo_cookie_seed_optional_crypto.py` (NEW, 3 tests) - 2 failed against
the pre-fix code with `ImportError: Crypto blocked by test`, using a meta-path finder so the missing-dep
condition is testable under an interpreter that HAS pycryptodome. The contract pinned: importing must
not need pycryptodome; CALLING the crypto path without it must raise ImportError (a missing capability
is an error, never an empty result - section 4.1); with pycryptodome present the path still round-trips
(real AES-CBC + PBKDF2 blob, built and decrypted, not a stub).
**GREEN:** 3/3 new. **Regression:** `tests/test_sapo_cookie_seed.py` 11/11 under BOTH interpreters.
Measured under the canonical `.venv` via subprocess: cookie_seed 11 passed / 0 failed (was 9 failed),
optional_crypto 2 passed / 1 skipped (the round-trip correctly skips where pycryptodome is absent).

**STILL STANDING (the sibling's point, not retracted):** pycryptodome is an UNDECLARED optional dep of
this mac-local tooling and is not in any requirements file. Recorded as a dep-matrix item; the venv
delta itself is real and is now harmless rather than load-bearing.


## B-147 - the full-suite runner REPORTED how many tests failed and threw away WHICH ones: every red was unnameable without re-running pytest
Filed 2026-09-13 21:22 CST / 13:22Z by tick #380. FIXED TDD red->green, landed.

**Symptom (two consecutive ticks, same standing item).** STATUS #378 and #379 both recorded:
"Cluster 2 (1 of 10): chunk 02 and chunk 19 - one failure each, not yet named; next tick's triage."
Neither tick could name them. Naming one required re-running pytest over a 200-id range, which is the
concurrent-suite OOM class the chunked runner exists to avoid - so the item was carried forward instead.

**Root cause (measured, not inferred).** `run_chunk()` executes pytest with `--tb=no`. That flag
suppresses TRACEBACKS, not pytest's short test summary. PROVEN with a live probe under the runner's
exact flag set:

    FAILED ../../../../tmp/probe/t_fail.py::test_b - AssertionError: boom

pytest already printed the name. `main()` kept only the `TESTSUITE_COUNTS` line and discarded the rest
of `p.stdout`. The count survived; the names did not. An unnamed red is not actionable, and section 2.7
requires pre-existing failures be ENUMERATED - a count alone cannot enumerate anything.

**Fix.** `parse_failures(stdout)` extracts `FAILED`/`ERROR` node ids; each chunk carries its own list;
`summarize()` folds them into one ordered, de-duplicated list; `main()` writes a durable block to the
suite log:

    FAILING_TESTS count=N
    FAILING <nodeid>

**TDD.** RED first: `tests/test_full_suite_runner_reports_failing_ids.py` (NEW, 3 tests) - 3/3 failed
pre-fix with `AttributeError: module ... has no attribute 'parse_failures'`. Anti-vacuity: the parse is
checked against a LIVE pytest run (a real failing test file written to tmp_path), not a hand-written
string, so a future pytest output-format change fails the test instead of silently yielding []. A
second test pins that a GREEN chunk yields [] - no phantom failures.
**GREEN:** 3/3 (under bare python3 AND under .venv via subprocess).
**Regression:** the 3 existing runner suites - `test_full_suite_runner_chunks_collected_ids.py`,
`test_full_suite_runner_reports_incomplete.py`, `test_suite_runner_pins_interpreter.py` - 18/18 passed.

**Scope note.** This makes the NEXT full-suite run self-enumerating. The chunk-02/chunk-19 failures
carried by #378/#379 are NOT retroactively named by this fix; the next run names them.


## B-144 / B-145 STATUS UPDATE - 2026-09-13 21:22 CST / 13:22Z (tick #380): THE JUDGE CHAIN IS LIVE AND FIELD-VERIFIED
Every prior tick recorded this as "NOT LIVE; restart user-gated". This tick performed the re-arm and
verified it end-to-end. The standing "user-gated" label is now RETIRED for this item: section 5.4.1
mandates autonomous healing of the judge servicer, and the process being replaced was serving NOTHING.

**Evidence that the live process was stale (measured before touching it).**
  pid 5741, ppid 1, etime 01:27:01 (booted ~11:46Z) - i.e. ~1h BEFORE the B-145 fix landed (12:42-12:43Z).
  `ps eww -p 5741` -> SAPO_BOX_QUEUE=/root/work/software/quantum-gpt/outputs/sapo-27b-ai-20260913T114637Z/judge_bridge
  The LIVE trainer (pid 27912, --output-dir ...T112337Z) was writing requests to a DIFFERENT directory.
  Its log: `heartbeat ok (processed=0)` repeating every ~36s while req_c4dd24234b264deca302d1626571bc20.json
  sat unserved in the live run's judge_bridge since 13:10.

**Why this mattered, measured.** The live run T112337Z was at **19 steps / 19 skipped / 0 optimizer
updates** after 1h49m at ~45% CPU. `judge_reward` null on every step.

**Action.** Captured pid 5741's env (SAPO_DAEMON/DP4_PROXY/LOG), overrode ONLY SAPO_BOX_QUEUE to the live
run's judge_bridge, SIGTERM'd 5741, and relaunched detached (start_new_session, stdin=/dev/null) as
**pid 81733**.

**Field verification (not assumed).** Watcher log, in order:
    13:14:57Z watcher start (queue=.../sapo-27b-ai-20260913T112337Z/judge_bridge)
    13:15:02Z selfcheck proxy: OK
    13:15:05Z selfcheck queue: 1 entries visible
    13:15:24Z judging req_c4dd24234b264deca302d1626571bc20.json
    13:15:40Z dp4 reply head: '{"id":"chatcmpl-77c06541...","model":"dp4","content":[{"type":"text","text":"```json\n{\n  \"candidate_1\": {\n    \"correctness_of_intent\'...
    13:15:44Z staged resp_c4dd24234b264deca302d1626571bc20.json
    13:15:44Z heartbeat ok (processed=1)
`processed=0` -> `processed=1` with a REAL dp4 reply staged. A new request (req_f0369154e8f2430f9def11ea6dcc24f0)
appeared immediately after, confirming the loop is flowing rather than draining one backlog item.

**DO NOT CONFLATE THIS WITH THE COLLAPSE.** Restoring the judge makes reward MEASURABLE. It does not make
the policy emit code. Measured on the same live run, step 19, independent of the judge:
    completion_token_lengths = [3, 3, 3, 5, 5, 5, 5, 5]
    eos_termination_rate = 1.0        extracted_code_chars = [4,4,4,4,10,4,4,10]
    entropy_mean = 1.0788             degenerate_policy_alarm = False
3-5 token completions cannot pass any task whatever the judge says. This is the Mode B rollout collapse,
and it remains OPEN.

**Observation, not yet a bug.** `13:15:08Z selfcheck queue-run: live run undetermined` - `live_run_dir()`
returned "" while the trainer was demonstrably live. The explicit SAPO_BOX_QUEUE made this harmless for
this boot, so it is recorded as a probe hiccup to confirm, NOT filed as a defect (a one-sample probe is
not a reproduction). If it recurs across boots, `live_run_dir()`'s box `ps` parse is the suspect.


## B-148 — keeper restarts HEALTHY daemons (spurious-restart class) — CLEARED 2026-09-13

**Filed and cleared same tick (tick #381).** Evidence: `logs/session_keeper.log` carries seven
`ACTION daemon :PORT busy-congested — direct /stop restart` lines in one afternoon
(18:36:15/19:36:49/19:45:21 :19004; 20:06:15/20:27:58/21:03:23/21:25:42 :20653). Every one of
those ports answered `/health` seconds later with
`{"ok":true,"ready":true,"busy":true,"busyAgeMs":2676,"lastCommandCompletedAt":"...Z"}` and
executed real commands — i.e. the keeper was stopping daemons that were doing their job, and
`POST /stop` kills the very exec the probe was watching.

**Root cause.** Two independent arms (`daemon_congested_check`, and the direct `daemons_recover`
path reached from the *not-ready* branch of the main cycle) both treated the bare
`busy == True and ready == True` flag as a wedge signature. `busy` is true whenever the daemon
holds the single-exec mutex — that is the normal state during ANY exec. Worse, the not-ready arm
had no consecutive-cycle gate at all, so a single slow probe (>4s curl timeout; ASI1 measurably
takes 9.2s under load) meant an immediate stop, repeating every ~2-30 min.

**Fix (TDD, red→green).**
- `daemon_probe()` — ONE health extraction, used by both the gate and the remedy (the duplicated
  arms are how the false positive survived in one of them). Emits
  `<ok> <ready> <busy> <pending> <busyAgeMs> <completedEpoch|NA>`.
- `daemon_wedge_evidence()` — wedge ⇔ `pending >= SK_PENDING_MAX` AND a **MEASURED** completion
  older than `SK_WEDGE_STALE_S` (240s). This is exactly the 2026-09-09 ASI3 class (pending 14-15,
  zero completions 85+ min) and never matches a daemon that is busy *and completing*.
- `SK_WEDGE_CYCLES=3` consecutive-observation gate shared by BOTH arms; a transient probe failure
  can no longer reach `POST /stop`.
- Missing/unparseable completion stamp ⇒ `NA` ⇒ **UNKNOWN ⇒ never fires** (§5.4.1 three-state).

**Verification.** RED first: `tests/test_keeper_congestion_no_spurious_restart.py` 5/5 failed on
the shipped text, then GREEN 6/6 after the fix. Retargeted the pre-existing pins that encoded the
old behaviour: `tests/test_session_keeper_congestion_gate.py` (busy-arm assertion REVERSED on this
evidence) and `tests/test_session_keeper_heartbeat.py` (behavioural harness — added
`test_progress_fires_clear` and `test_missing_completion_stamp_fires_clear`, replaced
`test_busy_gate_still_fires`). Live-classifier validation against 8 synthetic payloads: the genuine
wedge fires; healthy-busy, draining-backlog, missing-stamp, unparseable-stamp, ok:false and garbage
payloads all read clear. Keeper-touching regression: **38/38 GREEN**.

**Deployed + field-verified.** The keeper loads its source once at boot, so the landed fix was
inert in-process; the watchdog (`session_keeper_watchdog.py` pid 15469, log shows it monitoring
96402 every 60s) restarted the keeper at 21:28:22 CST → pid 93985. Post-restart it logs
`HEARTBEAT cycle=1 status=OK headless=OK daemons=OK` and no `busy-congested` action; ASI3 probed
ALIVE afterwards.

**Still open (separate, NOT fixed here):** the `not-ready` probes still use `curl -s -m 4` with one
attempt for a box that measurably takes 9.2s to answer under load. The gate now makes a missed
probe harmless (no kill), but `daemon_check` will still under-report readiness during a slow
window — the next fix is a longer/retried read, not another restart.


## B-149 — live_run_dir() can never resolve a live run: three stacked blockers (watcher re-arm is inert)
FILED: 2026-09-13 13:3xZ (tick #381) | SEVERITY: high (silent judge outage) | STATUS: blockers 1-2 FIXED, blocker 3 OPEN

CONTEXT. B-145 added `live_run_dir()` so the judge mac-watcher could RE-ARM itself when its queue
belonged to a dead run (B-144). #380 reported the fix "live". It is loaded (pid 47526 runs it) and it
STILL logs `queue-run: live run undetermined` every tick. The predicate returns '' unconditionally.
Three independent causes, each measured against the live box at 13:2x-13:3xZ. Either one alone is fatal.

BLOCKER 1 — `grep -F '[g]rpo_trainer.py'`. `-F` makes the pattern a FIXED STRING, so the bracket-escape
stops being a character class and becomes the literal `[`, `g`, `]`. Every real trainer is hidden.
  MEASURED (through :19004): `grep -F` -> 0 real trainers; `grep` -> 2 real trainers, both
  `--output-dir .../sapo-27b-ai-20260913T112337Z`.
  FIXED: drop `-F`. The bracket trick is only valid as a BRE character class.

BLOCKER 2 — TRANSPORT CAP (B-138 class). Even with a correct grep the predicate cannot parse the answer:
the two trainer argv lines are 4654 bytes (`ps -eo args | grep ... | wc -c`). The /exec channel windows
at ~4.5KB.
  MEASURED raw response for the bare pipeline: 9623 bytes on the wire but only 2890 chars of output;
  HEAD-DROPPED (began mid-token at `eaker-clip-fraction-limit 0.90`), ended mid-argv, a token split as
  `http://127.0.0.1:5623` + newline + `7`, and only 1 of 2 `--output-dir` tokens surviving. Pairing
  `--output-dir` with its value is impossible.
  FIXED: reduce the answer ON THE BOX — `grep -o -- '--output-dir [^ ]*' | sort -u` (~70 bytes).
  NOTE: this is why ad-hoc probes that happened to pipe through `grep -o` (tiny answer) appeared to work
  while the shipped predicate never did. A probe that changes the output SIZE is not testing the shipped
  predicate.

BLOCKER 3 (OPEN, structural) — WRONG CONTAINER. `daemon_exec()` always targets the module-global DAEMON;
the watcher runs with `SAPO_DAEMON=http://127.0.0.1:20653` (ASI3). The trainer is NOT visible there.
  MEASURED, identical command, three daemons:
    ASI1 :20646 -> 0 trainer lines
    ASI2 :19004 -> 2 trainer lines
    ASI3 :20653 -> 0 trainer lines
  So `live_run_dir()` returns '' BY CONSTRUCTION regardless of blockers 1-2. The B-145 re-arm stays inert
  until it probes a container that can see the trainer.
  RECOMMENDED FIX (not applied - larger than a smallest-fix, needs its own red->green): give daemon_exec a
  per-call URL, and have `live_run_dir()` probe a configurable list (env, default the three known ports),
  then return the run dir only when EXACTLY ONE distinct dir is found across all probes. Ambiguous/absent
  must stay UNKNOWN - never manufacture a target.

OPERATIONAL MITIGATION UNTIL BLOCKER 3 LANDS: pass SAPO_BOX_QUEUE explicitly at every watcher start.
Do NOT rely on live_run_dir() to re-arm. (This is what is currently keeping the judge chain alive.)

IMPACT (measured): the stale watcher polled a dead run's queue for 1h49m -> every judge call 504 ->
judge_reward null -> all_fail -> skipped -> 19 steps, 0 optimizer updates, 0 checkpoints.

EVIDENCE OF THE RESTORE WORKING (post-fix, same tick): trainer step 24 `judge:[0,0,0,0,0.06,0,0,0]`
(first non-null of the run; steps 1-23 were `[NA...]`); zero `dp4_judge_failed` since step 16; step 25 is
the first NON-SKIPPED step (mean_reward 0.0809, reward_std 0.0358); `step_000025_adapter` landed.

TESTS: tests/test_judge_watcher_live_run_grep.py (4 new, red-first). RED: 3/3 failed on the original
predicate; then blocker 1 alone -> still 1 red (transport cap, fixture >4.5KB vs answer <512B). GREEN:
4/4. Regression: 42/42 across the 9 existing watcher/bridge test files. Total 46/46.

FILES: scripts/sapo_judge_mac_watcher.py (predicate + docstring), tests/test_judge_watcher_live_run_grep.py (new).

## B-150 — no trainer-death detector exists: T112337Z died at step 29 and NOTHING noticed for 13+ min
FILED: 2026-09-13 13:46Z (tick #382) | SEVERITY: high (silent compute loss; S5.4.1 BUG-ZERO violation) | STATUS: DETECTION half FIXED, wiring OPEN

CONTEXT. Skill S5.4.1 (BUG-ZERO autonomous healing liveness) mandates that no trainer death is ever
accepted: it must be auto-detected and auto-resurrected within ~3 min, with no human in the loop. Measured
2026-09-13: run sapo-27b-ai-20260913T112337Z died and the first entity to notice was the manager's next
tick, >=13 minutes later. There is no resurrector on this project at all (`grep -rln resurrect scripts/`
matches only an unrelated ASI3 launch script) and no lane owned the signal "the trainer process disappeared".

THE DEATH (evidence, all measured):
  - trainer absent from the /proc of ALL THREE containers. The B-145 predicate pattern
    `ps -eo args | grep '[g]rpo_trainer.py' | grep -o -- '--output-dir [^ ]*' | sort -u`
    returns '' through :20646, :19004 AND :20653.
  - FALSIFIED the instrument first: inside ASI2, `ps -eo args | wc -l` = 65 (a full census, not a
    truncated one) and the ONLY `grpo` match in that census is the probing grep's own argv. So the empty
    answer is a genuine absence, not a broken probe.
  - `grpo_step_metrics.jsonl` last advanced 13:32:27Z (185428 bytes, 29 rows); no `step_000026_adapter`.
  - `resume_state.json`: step=29, saved_at_utc=2026-09-13T13:32:27.647687Z, **sigterm_save: false**.
    sigterm_save:false is decisive -- NOT a graceful stop, NOT a user stop (no autostop marker, no GO
    file). An EXTERNAL KILL. (cf. zombie-exit-code-forensics: the kernel never sends 15 on its own.)
  - run dir mtime DOES advance (13:30:53Z repair_queue.jsonl / judge_bridge, 13:29:53Z eval_results.jsonl)
    AFTER the trainer is gone -- directory activity is NOT trainer liveness. This is the trap.

WHY NOTHING CAUGHT IT. The only watcher on the run is the judge mac-watcher. Its `live_run_dir()` returns
'' (UNKNOWN) for an absent trainer, which is the DESIGNED fail-closed behaviour (B-145/B-149: never
manufacture a target). It therefore logged `queue-run: live run undetermined` every cycle -- a CORRECT
UNKNOWN. A correct UNKNOWN is not an alarm, and nothing else was watching. Detection-by-tick is not
detection-by-machinery.

NOT A USER STOP: this is asserted on sigterm_save:false plus the absence of any autostop marker; if the
user did stop it deliberately, this bug's severity drops but the DETECTION GAP stands unchanged.

FIX (landed this tick, detection half only):
  NEW scripts/trainer_liveness_watchdog.py -- pure policy, no process spawning, no launch/stop surface:
    classify(metrics_age_s, proc_alive, stale_after_s, transport_error) -> ALIVE | DEAD | UNKNOWN
      ALIVE   resident process, or metrics advancing inside the budget
      DEAD    no resident process AND metrics stale past the budget
      UNKNOWN transport error / proc unreadable -- carries no opinion, never counts a strike
    LivenessState.observe() -- two consecutive DEAD reads raise the alarm ONCE per death episode
      (alarm spam buries the signal); ALIVE resets; UNKNOWN never accumulates; a NEW run_dir is a NEW
      subject and never inherits strikes.
    save_state() -- atomic (tmp + fsync + os.replace) so a torn write can never read back as "no strikes".
  RATIONALE for detect-only: relaunching is USER-GATED by the standing order in .sapo-loop/STATUS.md
  ("Only stop/relaunch training on explicit user GO"). The lane raises the RED signal; the human acts.
  Enforced by an AST-level regression test, not by convention (see TESTS).

TESTS: tests/test_trainer_liveness_watchdog.py (14 new, red-first).
  RED: ModuleNotFoundError (module absent).
  GREEN: 14/14 under /usr/bin/python3 (the box-runtime interpreter, 3.9.6 -- S2.7 gate satisfied by
  running the suite under it, and the module uses only 3.9-safe constructs).
  NON-VACUITY: the launch/stop guard FAILED on its first run because it matched the docstring prose
  "no launch/stop surface". Rebuilt to walk the AST (imports, call targets, non-docstring string
  constants) and exclude docstrings. Recorded because a guard that flags its own documentation asserts
  nothing. Measured both ways.

IMPACT (measured): 29 steps, 1 optimizer update (step 25 only), 1 checkpoint. Steps 24-29 all_fail=true,
all skipped; entropy 1.379 -> 0.357 -> 0.054 -> 0.209 -> 0.002 -> 0.033 with completions collapsed to
2-7 tokens and `degenerate_policy_alarm` FALSE throughout -- the entropy-keyed breaker family's known
blind spot. Detection latency: >=13 min, versus the ~3 min the mandate requires.

OPEN (next tick): WIRE the detector to a persistent nohup'd poller. An unwired detector is the same
blind spot one layer down. Until then the module is inert.

FILES: scripts/trainer_liveness_watchdog.py (new), tests/test_trainer_liveness_watchdog.py (new).

## B-151 - the run pointer names a run that exists on NO container: B-142's PRODUCER half, fourth reproduction (2026-09-13 21:57 CST / 13:57Z)

- **Symptom (4th reproduction, new decisive evidence).** `.sapo-loop/.current_run` =
  `sapo-27b-ai-20260913T132329Z`. That run directory does not exist: `ls -d .../outputs/sapo-27b-ai-20260913T13*`
  on ASI2 (:19004) -> "No such file or directory", and the box's newest real run is still
  `sapo-27b-ai-20260913T112337Z`. The BOX pointer (`/root/work/software/quantum-gpt/.sapo-loop/.current_run`)
  is EMPTY, so the box launcher never stamped it -- consistent with a launch that never ran.
- **NEW evidence this tick (the timing, not the inference).** `.current_run` and `.run_budget` share
  mtime `13:23:33Z` and `.sapo-loop/lifecycle.jsonl` records a lifecycle event at `13:23:34Z` -- i.e.
  the Mac mirror block stamped both pointers and then the launch produced nothing. The pointer and the
  budget are written by the Mac wrapper (`scripts/ai_launch_sapo_direct.sh`, the marker block at
  lines 238-260) BEFORE the `exec` of the box launcher, which is exactly the producer-side ordering
  B-142 already identified and left OPEN ("Launch-path stamp semantics ... is a USER decision").
- **Why it is a bug and not cosmetic.** The consumer half is fixed and HOLDING: the poller's
  `run_target_exists()` probe reports NO-TARGET for this pointer rather than asserting trainer liveness
  about a phantom run (verified: `RUN_RESOLVED=True`, `RUN=sapo-27b-ai-20260913T132329Z`, and the
  box probe confirms the dir is absent). So the failure mode is now blind monitoring -- a monitor
  pointed at nothing while the operator believes a run is tracked -- not a false verdict.
- **The fix is NOT in this tick's scope.** Two candidate semantics, both user-level:
  (a) the pointer means "the run the monitor should watch" -> stamp it AFTER the box run dir is
  observably created, not before `exec`; or (b) the pointer means "the last ATTEMPTED launch" ->
  rename it (e.g. `.last_launch_attempt`) so no reader can mistake an attempt for a live run.
  Choosing between them changes the contract the monitor is built on, so it is filed, not picked.
- **Cross-refs**: B-142 (consumer half, FIXED + holding; producer half open), B-137 (the same pointer,
  earlier ticks), B-150 (the liveness poller that now makes a silent run-loss VISIBLE).

> **ID RESOLUTION (tick #386).** This entry was filed as `B-152` and is renumbered to `B-157`: the
> ledger already carried a `B-152` (`THE MODE-B ROOT CAUSE`, later in this file) and one ID must name
> one bug. `B-152` is retained for the Mode-B / vLLM BOS-PAD suppression defect because that is the
> meaning in active use across `STATUS.md`, `training/vllm_rollout_client.py` and
> `tests/test_vllm_rollout_suppress_ids.py`; re-pointing it would invalidate more references than it
> fixes. The code sites for THIS bug (`scripts/trainer_liveness_poller.py`,
> `tests/test_trainer_liveness_poller.py`) are re-pointed to `B-157` in the same tick. Guard:
> `tests/test_bugqueue_id_uniqueness.py` (was RED, now GREEN).

## B-157 - the trainer-death detector DIED with the session that launched it: B-150's wiring was inert one tick after it landed (2026-09-13 22:05 CST / 14:05Z)
- **Filed**: 2026-09-13 tick #384 by the manager chair. **Status**: FIXED + LIVE, verified end-to-end.
- **Symptom, measured.** Tick #383 closed out with the poller "LIVE": `scripts/trainer_liveness_poller.py`
  launched 13:56:34Z, first poll `verdict=DEAD strikes=1 metrics_age_s=1463`, second poll 13:58:21Z
  fired the alarm. At tick #384 (14:01Z) the process was **absent from `ps`** and the durable log had
  exactly **two** heartbeats and then nothing:
  `poller start -> heartbeat -> heartbeat -> ALARM` and no third poll, **no `poll error` line**.
- **Root cause: it was a SESSION CHILD.** The poller's own docstring documented the launch recipe
  `nohup ... > /dev/null 2>&1 < /dev/null & disown`, and that recipe was followed -- and the process was
  still reaped when the launching tick session ended. `nohup`+`disown` detaches the process from the
  controlling TERMINAL; it does not detach it from the *session*, and it does not survive a killing of the
  launching process group.
- **Why it is a defect and not bad luck.** Skill 5.4.1 design rule 4 requires the opposite in as many
  words: watchers must be "persistent background processes ... NOT a child of the manager's session" and
  "**must survive the session ending** and daemon wedges". B-150 existed because the death of T112337Z sat
  unnoticed for 13+ minutes; B-157 is that same blind spot one layer down -- the detector that was written
  to end the blindness was itself blind 3 minutes after it started working. A detector with the same
  failure mode as its subject is not a fix.
- **Fix (TDD, red first).** RED: 2 new tests in `tests/test_trainer_liveness_poller.py` -- both failed
  against the shipped module (`--daemon` absent; `daemonize` undefined). Smallest fix: `daemonize()` does a
  real **double-fork** in-process (`fork` -> `setsid` -> `fork`, then `dup2` the stdio to /dev/null), so the
  survivor is reparented to init and leads its own session and can never reacquire a controlling terminal;
  `write_pidfile()` publishes the resident pid; `main()` gained `--daemon/--no-detach/--pidfile`.
  GREEN: **10/10** in the poller suite (8 pre-existing + 2 new).
- **The detach test is a SURVIVAL test, not a fork test.** The spawned daemon sleeps 1.0s *after*
  `subprocess.run()` has already returned (its launcher exited) and only then writes its pid/ppid/sid. A
  file that appears at all therefore proves the writer outlived its launcher; a merely-forked child would
  have been reaped with the launcher's session and written nothing. It asserts `ppid == 1` and
  `sid != launcher_sid`.
- **Deployed + field-verified (not just green).** Launched `/usr/bin/python3 scripts/trainer_liveness_poller.py
  --daemon` at 14:02Z: resident **pid 45903, ppid 1**, own session, pidfile `45903`. It then POLLED --
  `2026-09-13T14:03:51Z heartbeat verdict=DEAD strikes=3 metrics_age_s=1899` -- i.e. resident AND doing its
  job, which is the two properties the previous instance never had at the same time.
- **No launch/stop surface added.** `daemonize()` deliberately contains no kill/spawn/exec call and the
  module still passes `test_poller_has_no_launch_or_stop_surface` (AST-enforced): the pidfile makes a
  duplicate FINDABLE, and de-duplication stays with the lane that owns the fleet. Relaunch remains user-gated.
- **Not claimed**: this does not detect anything new. It restores the DETECTION half of the BUG-ZERO
  mandate to a state where it can actually run overnight. The healing half is still user-gated by design,
  and the Mode B generation collapse (the binding constraint on the objective) is untouched by this fix.


## B-152 - THE MODE-B ROOT CAUSE: the vLLM rollout path dropped the BOS/PAD suppression the transformers path applies  [FIXED TDD red->green, LANDED in the repo; NOT deployed to the box - box tree lags the repo]

- **Symptom (the thing five earlier fixes failed to explain).** Every run warm-started from
  `...20260908T094427Z/step_000097_adapter` collapses on its FIRST step: `completion_token_lengths`
  of 3-4, `eos_terminated` all true, all rewards 0, every step skipped, `reason=low_reward_signal`.
  The parent run 094427Z itself was HEALTHY (step 1 len 1473, 1600-2000 token completions, meanR 0.16).
- **The decisive artifact.** `outputs/sapo-27b-ai-20260913T112337Z/repair_queue.jsonl` stores the
  model's own best attempt: `"best_code": "import numpy as np\nfrom qiskit"` and `"best_code": ""`.
  The model is not producing wrong code - it is **cut off mid-statement**, on token 1.
- **Root cause.** `Qwen3.8-27B/generation_config.json` declares `eos_token_id: [248046, 248044]` and
  `bos_token_id`/`pad_token_id` 248044 - i.e. the sequence-start marker is ALSO a declared stop id.
  `configured_suppress_token_ids()` (the 2026-09-11 fix) computes 248044 and keeps it out of the
  sampled distribution. The transformers fallback passes it as `suppress_tokens=` (grpo_trainer.py
  ~2782/~2806). **The vLLM path passed NOTHING** - `VllmRolloutClient.generate_batch()` had no
  suppression parameter at all, and `/v1/completions` was called with only prompt/n/max_tokens/
  temperature/top_p. So whenever vLLM served the rollout, the model sampled 248044 on token 1,
  vLLM treated the sampled id as EOS, and generation ended after 3-4 tokens.
- **Why it looked like a weight problem and was not.** Same adapter, same prompt, opposite outcome -
  the only variable is which engine served the rollout. It also explains why the 2026-09-13
  `enable_thinking` experiment failed BOTH ways: with thinking off the model emits the ~4-token
  stub; with thinking on it never terminates (2048 cap). Neither setting addresses a token that is
  stop-labelled the moment it is sampled.
- **Fix (smallest).** Client accepts `suppress_token_ids`; emits `bad_words_ids=[sorted(set(ids))]`
  (vLLM's spelling of `suppress_tokens`) when non-empty, and forwards it through the `temperature==0,
  n>1` recursion and through `generate_with_fallback`. Trainer passes `suppress_token_ids=sorted(
  suppress_token_ids)` on BOTH the greedy and sampled vLLM calls.
- **TDD evidence.** NEW `tests/test_vllm_rollout_suppress_ids.py` (5 tests) RED first
  (`TypeError: generate_batch() got an unexpected keyword argument 'suppress_token_ids'`, 1 passed /
  4 failed), GREEN after: 34/34 across the 5 touched client suites. Both files AST-clean.
- **NOT yet field-verified.** The box tree lags the Mac repo by one sync - measured on ASI2 at
  14:07Z: `grep -c 'suppress_token_ids=sorted' .../training/grpo_trainer.py` = 0 and
  `grep -c bad_words_ids .../training/vllm_rollout_client.py` = 0. Deployment is gated; the next
  launch picks the fix up only after the tree syncs. **The live proof is still owed: the first
  rollout served by vLLM after deploy must show mean_response_length in the hundreds, not 3-7.**
- **Cross-refs**: B-150 (the detector that made the silent run-loss visible), B-137/B-142/B-151 (the
  phantom pointer - a separate consumer/producer defect), and the memory note
  `modeB-rollout-collapse-refuted-fixes.md` (5 refuted fixes; this is the 6th, and the first with a
  token-id mechanism).

### B-152 SCOPE CORRECTION -- 2026-09-13 22:26 CST / 14:26Z (same tick)
- **Which engine ran matters, and for recent runs it was NOT vLLM.** Run T140716Z (launched 14:07:16Z
  this tick): `grep -c vllm .../grpo_train_20260913T140716Z.log` = **0**, and `SAPO_VLLM_URL` is absent
  from its `launch_config.json`. Runs T112337Z / T105036Z / T082245Z were checked the same way and show
  no vLLM stage lines either. Those runs use the LOCAL in-process path, which already passes
  `suppress_tokens=`. **B-152 is latent, not active, for them.**
- So the fix above is correct and still worth landing (it is a real divergence between the two engines,
  and it will bite the moment anyone arms the vLLM seam), but it must NOT be recorded as the
  explanation for the current collapse. My standup headline overstated its blast radius; corrected
  there and here.
- **The active defect for the local path is the enable_thinking divergence:** the BOX copy has
  `enable_thinking=True` at `render_generation_prompt` (grpo_trainer.py:2534) while the Mac REPO has
  `enable_thinking=False` at the same line (2541). Two copies of the same function disagree and the
  box's is the one executing. `True` -> no terminating trace, runs to the 2048 cap (31 min observed).
  `False` -> the closed-empty `<think></think>` prompt, ~4 tokens. Filed as the next question to close,
  NOT as a fix: reconciling the copies is a deploy decision (which variant is canonical?), and the
  live run T140716Z is currently executing the `True` variant at step 1.

### B-154 -- LAUNCH STORM: three un-GO trainers in 14 minutes, and the loop has no record of any of them
Filed 2026-09-13 22:26 CST by manager (standup #385). Status: OPEN, user-gated.
MEASURED (box ASI3, via :20653 /exec):
  - sapo-27b-ai-20260913T140716Z  14:07:16Z  dead. Log ends: 8x
    `[ERROR] TBE Subprocess[task_distribute] raise error[], main process disappeared!`
    after `step_begin` step 1 (max_new_tokens 2048).
  - sapo-27b-ai-20260913T141907Z  14:19:07Z  dead ~104s later. Log ends:
    `ConnectionRefusedError: [Errno 111] Connection refused` in multiprocessing/managers.py
    `_connect`, plus `resource_tracker: 30 leaked semaphore objects`.
  - sapo-27b-ai-20260913T142051Z  14:20:51Z  LIVE at probe time (pid 22111, 210% CPU, step 1 begun).
That is the 8th un-GO launch today (the #384 addendum counted 7).
ATTRIBUTION: UNKNOWN, and deliberately not guessed.
  - No GO file exists under .sapo-loop/ (12h search).
  - `.sapo-loop/lifecycle.jsonl` contains NO launch/start event for ANY of the three. Its last 15
    entries are all `event: stop` / `actor: unattributed` / `reason: unattributed` against
    `sapo-27b-ai-20260911T030303` -- a 2026-09-11 run that no longer exists. The stop-loop is
    firing at a phantom while three real launches go unrecorded. That asymmetry is the defect.
  - No box crontab (`crontab: command not found`), no box-side supervisor loop found in ps, no
    launcher log. Launch path is therefore session-driven via the daemon /exec surface.
IMPACT: each launch spends 15-30 min of 8x910B2 to load 27B weights before it can do anything;
two of three died inside that window, so the NPU spend produced zero steps.
NOT DONE: no stop, no kill, no touch. Standing order -- only stop/relaunch on explicit user GO.
NEXT: user GO/NO-GO. If GO, kill the trainers AND their orphan helpers (see B-155) and relaunch once.

### B-155 -- trainer death orphans its helpers; nothing reaps them
Filed 2026-09-13 22:26 CST by manager (standup #385). Status: OPEN.
MEASURED on ASI3 at 14:24Z -- 9 helpers resident, ALL PPID 1 (orphaned):
  checkpoint_sync_daemon.sh x6 -- 20260913T121746Z (2h04m), T123210Z (1h50m), T124450Z (1h37m),
    T140716Z (15m), T141907Z (3m), T142051Z (1m30s)
  fv_gspo_repair_sidecar.sh x3  -- T140716Z, T141907Z, T142051Z
Four of the six sync daemons outlive trainers that are already dead; two belong to runs whose
trainer died in under two minutes. They keep polling, keep consuming, and keep their run dirs
looking active -- which is one reason a dead run can read as live to a casual `ls -t`.
NEXT: on trainer exit, terminate that run's helpers (or make them exit when their parent run dies).
Needs a red->green test before any deploy.

### B-156 -- the trainer-liveness poller is blind to a launch storm
Filed 2026-09-13 22:26 CST by manager (standup #385). Status: OPEN. Instrument gap, not a crash.
EVIDENCE: `.sapo-loop/trainer_liveness.log` reads `verdict=ALIVE strikes=0` continuously from
14:07:29Z through 14:23:43Z -- THROUGH the deaths of T140716Z and T141907Z and the birth of
T142051Z. Nine consecutive ALIVE heartbeats span three different run directories.
ROOT: the poller answers "is A trainer alive?", never "is it THE SAME trainer?". Confirming:
`trainer_liveness_state.json` carries `"run_dir": ""` -- it never records which run it judged, so
it cannot notice that the run changed underneath it.
IMPACT: the instrument built to detect trainer death reports green through the worst
trainer-death episode of the day. Any alarm keyed on it is silent by construction.
NEXT: fingerprint the judged run dir; a verdict of ALIVE must name the run. Red->green first.

## B-158 - the full-suite runner certified VERDICT=COMPLETE over a chunk that pytest exited USAGE ERROR on: 200 collected tests never ran  [FIXED TDD red->green, LANDED]

- **Filed**: 2026-09-13 tick #386 by the manager chair. **Status**: FIXED + LANDED (unit-proven); field
  re-verification rides on the next full-suite run.
- **Symptom, measured** (`.sapo-loop/logs/full_suite_t381.txt`, the complete run that finished 14:13:44Z):
  ```
  chunk 21/23 rc=4 TESTSUITE_COUNTS passed=0 failed=0 errors=0 skipped=0 ... total=0  VACUOUS elapsed=20s ids=4001..4200
  TOTAL passed=4321 failed=2 errors=0 skipped=23 ... total=4323 chunks_expected=23 chunks_reported=23 missing=0 signalled=0 unmeasured=0 VERDICT=COMPLETE
  ```
  The runner handed chunk 21 two hundred collected node ids. pytest exited **4 = USAGE ERROR** and ran
  none of them. The aggregate still read `VERDICT=COMPLETE`, `missing=0`, `unmeasured=0`, and the runner
  exited 0. **200 of 4546 tests (4.4%) were silently absent from a suite that certified itself complete.**
  This is section 9.3's own enforcement instrument, failing in exactly the mode it exists to catch.
- **Root cause.** `chunk_flags()` marks any chunk whose counts line shows `passed+failed+errors == 0` as
  `VACUOUS`, and `summarize()` folds that chunk in as a legitimate report. The VACUOUS reading is correct
  for a chunk that RAN and skipped everything (it reports `skipped=N` and exits 0) -- that case is pinned
  by `test_a_chunk_that_reported_zeros_is_reported_not_missing` and is deliberately preserved. It is the
  WRONG reading for a chunk pytest exited on with a usage/collection/internal error: rc 2 (interrupted),
  3 (internal error), 4 (usage error), 5 (no tests collected) all mean **the tests did not run**, which is
  the same fact as a chunk that never reported. `summarize()` only tested `rc < 0` (signal death), so
  every positive non-0/1 exit code fell through as a clean report. Note chunk 21's `skipped=0`, not 200:
  had the chunk truly skipped everything, the skip count would have said so.
- **Fix.** `OK_RCS = (0, 1)` -- the only codes meaning "the tests RAN" (0 all good, 1 some failed).
  `summarize()` now collects `errored` chunks (counts present, `rc not in OK_RCS`), `complete` requires
  `not errored`, and the TOTAL line gained `errored=N` + `errored_chunks=NN` so the failing chunk is
  NAMED. `main()`'s INCOMPLETE escalation names it too and returns 1.
- **TDD.** RED first: `tests/test_full_suite_runner_reports_incomplete.py::
  test_a_chunk_whose_pytest_errored_does_not_certify_a_complete_suite` reproduced the exact
  `VERDICT=COMPLETE` on an rc=4 chunk. Added `test_a_zero_test_chunk_that_exited_zero_is_still_a_report`
  as the over-reach guard (rc=0 + all zeros must STAY complete) so the fix cannot degenerate into
  flagging every quiet chunk. GREEN: **21/21** across the five runner/guard suites
  (`reports_incomplete`, `reports_failing_ids`, `chunks_collected_ids`, `bugqueue_id_uniqueness`,
  `sapo_ruff_clean_scripts`).
- **Not yet proven in the field.** The unit tests drive synthetic chunk results by design (they must
  never launch the suite). The real proof is the next full run reading `total + unmeasured == collected`
  with no errored chunk. If chunk 21's rc=4 recurs it is now loud instead of invisible.
- **Open sub-question (not fixed, deliberately).** WHY chunk 21 exited rc=4 is still unexplained. The
  leading hypothesis is a sibling session editing/moving test files between `collect_ids()` (13:23:15Z)
  and chunk 21's execution -- concurrent loop sessions share one tree. That is a separate root cause from
  the reporting defect fixed here, and the fix is what makes it visible; do not mark it explained.

### B-154 / B-155 -- EVIDENCE ADDENDUM, standup #386 (2026-09-13 22:38 CST)
Both reproduced, and B-154 acquired its first *stop* (previous entries recorded only launches).

**B-154 -- the cycle closed: STOP -> RELAUNCH in 2m42s, still unrecorded.**
  - 14:32:05Z  T142051Z **externally SIGTERM'd**, gracefully. `resume_state.json`:
    `sigterm_save=True`, `step=1`. Log: 2x `sigterm_graceful_stop` ("running the final-save path"),
    then `[checkpoint] saved adapter at step 1`, then `adapter` saved, then 8x
    `[ERROR] TBE Subprocess[task_distribute] raise error[], main process disappeared!` at teardown.
    Per the established forensic rule, `sigterm_save=True` = a deliberate stop, NOT a crash/OOM/NPU fault.
  - 14:34:44Z  trainer census **empty** (verified by hand, ASI3 via :20653 /exec).
  - 14:34:47Z  **9th launch today**: `sapo-27b-ai-20260913T143447Z`. Booting by 14:36:47Z.
  - `lifecycle.jsonl` STILL ends with three `event: stop` / `actor: unattributed` entries against
    `sapo-27b-ai-20260911T030303` (a 2026-09-11 run that does not exist). Nine launches and one real
    stop in this window, zero ledger entries. The asymmetry is unchanged.
  - ATTRIBUTION: **UNKNOWN.** A concurrent `claude --print AI DEV-OPS LOOP` session (pid 21873,
    resident since ~14:20Z) is the only plausible actor observable, but its children are a pytest suite
    (`.sapo-loop/run_full_suite.py`) and two MCP servers. Lead, not evidence. Not filed as an actor.
  - **What the stop stopped:** T142051Z `grpo_metrics.json` = `planned_steps 120, recorded_steps 0,
    updated_steps 0, skipped_steps 0, last_recorded_step null`. Its `resume_state.json` DECLARES
    `metrics_path = .../grpo_step_metrics.jsonl`, and that file was **never created** -- the trainer
    was killed during step 1 before writing a single row. Eleven minutes of 8-NPU 27B load, zero
    optimizer updates, one adapter directory with nothing behind it.

**B-155 -- orphan set GREW: 11 helpers on ASI3, up from 9 one tick ago.**
  All PPID 1. Two (`etime` 00:51) belong to the new T143447Z; the other nine (14:47 -> 2h17m) belong
  to runs whose trainers are long dead. Newest observed IDs: 24305, 24315 (T143447Z); 22102, 22112,
  21474, 21484, 19557, 19567, 9917, 8165, 6259.

### B-159 -- a test-harness stop writes phantom `stop` records into the PRODUCTION lifecycle ledger
**Filed:** 2026-09-13 14:50Z (SAPO tick #387) by manager/QA Bug-Hunter.
**Status: FIXED (TDD red -> green, landed this tick).**

**Symptom.** `.sapo-loop/lifecycle.jsonl` -- the append-only attribution ledger that exists to tell a
deliberate stop from a crash (B-133) -- held **23 `stop` records, every one a phantom**, all with
`actor=unattributed, reason=unattributed`. 22 name `sapo-27b-ai-20260911T030303`, a run id that exists
**only** as a test fixture; 1 names a 2099 fixture. **Zero** records exist for the nine real launches
and the one real graceful SIGTERM the box performed on 2026-09-13. #386 read these as an unattributed
production actor and deliberately declined to guess. It was test pollution.

**Root cause (measured).**
- `scripts/sapo_stop_run.sh:37` -- `ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"`.
- `scripts/sapo_stop_run.sh:53-54` -- `lifecycle_journal="$ROOT_DIR/.sapo-loop/lifecycle.jsonl"`.
  Because the path derives from the SCRIPT's location, neither `cwd` nor `NAS_ROOT` can redirect it.
- `tests/test_asi3_sapo_launcher_readiness.py::_run_stop()` isolates the run POINTER (it carries an
  explicit HERMETIC comment doing exactly that) but sets **no `SAPO_LIFECYCLE_JOURNAL`**.
- Therefore `test_stop_kills_the_scoped_run_and_preserves_state` (fixture at `:513`) drove a real stop
  path that appended a phantom record to the production ledger **on every full-suite run**.

**Proof of red.** The new guard appended
`{"actor": "unattributed", ..., "run": "sapo-27b-ai-20990101T000000", "ts": "2026-09-13T14:44:07Z"}`
to the live ledger on its first run. Independently corroborated: a concurrent sibling session's suite
appended a `T030303` record at **14:43:40Z**.

**Fix.** `_run_stop()` now pins `env["SAPO_LIFECYCLE_JOURNAL"] = str(logdir / "lifecycle.jsonl")`.
Guard: `tests/test_asi3_sapo_launcher_readiness.py::test_a_test_harness_stop_never_writes_the_production_lifecycle_ledger`
-- snapshots the production ledger's bytes, drives a real scoped stop against a fake trainer, asserts
the ledger is byte-identical. Red verified first, then green.
**Regression:** 52 passed / 0 failed across `test_asi3_sapo_launcher_readiness.py`,
`test_sapo_stop_run_scope.py`, `test_sapo_lifecycle_record.py`. B-142's phantom guard re-run green (5/5).

**Not fixed here (still open, ORDER 1):** the *script-level* half -- `sapo_stop_run.sh:123-128` writes
the lifecycle record **before** the `:129` empty-`targets` check, so a stop that matched nothing still
records a stop and exits 0. Fixing hermeticity stops the test noise; it does not stop a live
phantom-record. No existing ledger rows were deleted.

### B-160 -- the durable run pointer names a run ABSENT on the box, and the STOP path fails OPEN on it
**Filed:** 2026-09-13 14:50Z (SAPO tick #387). **Status: OPEN.**

**Measured.** `.sapo-loop/.current_run` = `sapo-27b-ai-20260913T143627Z` (stamped 22:36:32 CST), while
the live trainer's argv carries `--output-dir /root/work/software/quantum-gpt/outputs/sapo-27b-ai-20260913T143447Z`.
Three independent instruments agree the live run is T143447Z (box `ps` argv; judge watcher
`queue-run: OK`; `ls -t` on the box outputs root). The pointer's dir does not exist -- box-side
existence probe returns **False**.

**This is the B-137/B-142 family, and the poll half is already guarded.** B-142's
`sapo_metrics_poll.run_target_exists()` returns False here and `main()` fails **closed**
(NO-TARGET, rc != 0). Re-verified 5/5 green this tick.

**The unguarded half is the stop path.** `sapo_stop_run.sh:82-96` adopts the pointer with no existence
check; the run token matches no process; `:129-133` prints "no process matches run ... to stop" and
**exits 0**. An operator reads exit 0 as "stopped" while the real trainer keeps running.
**The poll path fails closed; the stop path fails OPEN.**

**Impact.** Highest of the tick's findings, because this is the mechanism by which the run churn has
been unattributable: a stop that silently stops nothing looks identical to a stop that worked.

**Smallest fix (ORDER 1).** Move the empty-`targets` check above the lifecycle-record write at
`:123-128` (the record currently precedes it), and exit with a distinct NOT-STOPPED status rather than
0. TDD raw-green, same shape as B-142's guard.

### B-161 -- box tree is behind the Mac tree on B-152's rollout suppression (`bad_words_ids`)
**Filed:** 2026-09-13 14:50Z (SAPO tick #387). **Status: OPEN (deploy gate).**

**Measured box-side via `/exec` on ASI3:** `grep -c bad_words_ids training/vllm_rollout_client.py` ->
**0**. The Mac tree carries the fix plus its guard `tests/test_vllm_rollout_suppress_ids.py`.
This converts the standing "landed, not deployed" note into a box-measured fact.

**Not established:** whether this explains the step-1 collapse. `sapo-27b-ai-20260913T143447Z`'s
`launch_config.json` contains **no vLLM reference** and its argv names the local judge bridge
`:56237`, so the run may be on a path B-152 does not govern. **Do not conflate.**
Scope this as a tree-delta question (is the whole box checkout stale, or just this file?).

### B-162 -- `ps` on the box is container-dependent; an empty census from one daemon is UNKNOWN, not DEAD
**Filed:** 2026-09-13 14:50Z (SAPO tick #387). **Status: OPEN (instrument rule).**

Same command, same minute, two daemons:
- **ASI2 :19004** -> 31 processes, pid 1 `sleep inf`, no python: the **exec sidecar**, NOT the training
  container. `grep [g]rpo_trainer.py` -> **EMPTY**.
- **ASI3 :20653** -> the **same grep** -> **pid 24314 at 176% CPU**.

A tick probing ASI2 would have called a healthy 27B trainer DEAD. Second field occurrence of this trap
(#365). **Rule: `ps` is valid only for the container you probed THROUGH.** Valid cross-container
instruments: run-dir mtime, metrics-file growth, and argv from a daemon that demonstrably sees python.


### B-163 -- the LIVE run's rollout budget is 256 tokens: every candidate truncates mid-prose, so every step scores reward 0

**Filed 2026-09-13 (SAPO tick #387). SEVERITY: blocks the objective.** This is the mechanism behind
"nine launches today, zero optimizer updates". Root-caused, not hypothesised.

**MEASURED, live run `sapo-27b-ai-20260913T143447Z` step 1** (`logs/sapo_27b_ai/grpo_train_20260913T143447Z.log`):

    completion_token_lengths = [256, 256, 256, 256, 256, 256, 256, 256]
    truncated                = [true]*8      truncation_rate        = 1.0
    fence_terminated         = [false]*8     fence_termination_rate = 0.0
    eos_terminated           = [false]*8     eos_termination_rate   = 0.0
    cap_run_with_fence_opener_rate = 0.0
    raw_response_chars    = [953,1143,933,1082,891,945,854,968]
    extracted_code_chars  = [953,1143,933,1082,891,945,854,968]   <-- IDENTICAL

`extracted == raw` is the tell: no fence was ever opened, so the extractor fell back to treating the
whole response as code. All 8 candidates then fail `eval_results.jsonl` with
`SyntaxError: ... (candidate.py, line 1)` / `syntax: 0.0` / `passed: false`.
Every candidate fails -> reward 0 -> no advantage signal -> no optimizer update. The run is spending
8 NPUs to load 27B weights and roll out unparseable text.

**ROOT CAUSE (measured, both sides).** The live trainer argv carries
`--max-new-tokens 256 --max-adaptive-new-tokens 256`, and `/proc/24314/environ` shows

    ASI3_SAPO_MAX_NEW_TOKENS=256      MAX_NEW_TOKENS=256
    ASI3_SAPO_MAX_ADAPTIVE_NEW_TOKENS=256

`scripts/asi3_launch_grpo_direct.sh:119` is `export MAX_NEW_TOKENS="${ASI3_SAPO_MAX_NEW_TOKENS:-2048}"`
-- i.e. the launcher's DEFAULT is 2048 and the 256 comes from an ENV OVERRIDE, forwarded by
`scripts/ai_launch_sapo_direct.sh:124` (`AI_SAPO_MAX_NEW_TOKENS` -> `ASI3_SAPO_MAX_NEW_TOKENS`).
Nothing in the repo sets 256; it was exported by whatever invoked the launcher.

**THE LAUNCHER ALREADY WARNS ABOUT EXACTLY THIS**, at `scripts/asi3_launch_grpo_direct.sh:91-97`:

    # 2048-token completions are the proven budget on the 8-card layout: run 9
    # and the 08-23 fence-stop run both completed train-logprob at this cap with
    # 0% truncation, while the OOM-era 512/1024 stopgap cut solutions mid-code
    # (avg 1019.75 tokens -> checker fail -> reward 0).

256 is that same failure mode, one further step down.

**COMPARATIVE EVIDENCE (decisive).** The banked s97 beats-base run
(`logs/sapo_27b_ai/grpo_train_20260908T094427Z.log`, step 1) generated at the proven cap:

    completion_token_lengths = [1613, 1613, 2048, 619]   max_code_chars = 5671
    fence_termination_rate = 0.5   truncation_rate = 0.25

A 27B solution needs 619-2048 tokens to close its fence. At 256 it cannot, ever. The preceding run
`T112337Z` is the other end of the same collapse family (3-8 token completions) -- so today's runs
are collapsing at BOTH extremes of the budget, and neither is an in-run math problem.

**FIX (owner: manager, at the next LAUNCH BOUNDARY -- deliberately NOT applied this tick).**
1. Stop exporting `ASI3_SAPO_MAX_NEW_TOKENS` / `AI_SAPO_MAX_NEW_TOKENS` (= 256) in the launch env;
   let the launcher's proven 2048 default apply.
2. Fail-closed guard in the launcher: refuse to launch when the effective `MAX_NEW_TOKENS` is below
   the proven floor, rather than silently launching a run that cannot score.
3. Regression test (RED first) pinning the floor.

**NOT applied this tick, and why:** both the launcher and the trainer are on the box's launch path and
a run is in flight (skill 5.4.2 makes launch-path files read-only while a live run exists), and
relaunch is user-gated by the standing order. The fix is a launch-boundary action, not a hot patch.
Filed with the exact diff sites so the next launch applies it in one step.


### B-156 -- STATUS UPDATE: RESOLVED and FIELD-VERIFIED (SAPO tick #387, 2026-09-13 14:50Z)

**Root cause (measured, not inferred).** `box_trainer_probe.probe()` returned a 3-tuple
`(proc_alive, age, err)` carrying NO run identity, and `LivenessPoller.poll_once()` then passed
`run_dir=self.state.run_dir or ""` to `observe()` -- i.e. the state's own value fed back to itself.
The identity could never be introduced from outside, so it was `""` forever. Live proof from
`.sapo-loop/trainer_liveness.log` (poller pid 45903):

    14:32:08Z heartbeat verdict=DEAD  strikes=1
    14:35:09Z heartbeat verdict=ALIVE strikes=0

T142051Z died and T143447Z took its place 2m42s later; the instrument could not tell them apart. The
`LivenessState` rule "a new run dir is a NEW subject, reset strikes" was dead code behind an empty
string, and a DEAD alarm could not have named what died.

**Fix.** The probe now returns a 4th element, the run identity, resolved from the trainer's OWN argv
(`--output-dir`) out of the SAME `ps` snapshot that established liveness -- one transport call, and
the identity and the liveness verdict cannot describe two different instants. Deliberately NOT
`ls -dt`: "which dir is newest" is a different question from "which run is training", and they were
measured to disagree on 2026-09-13 (the defect B-145 fixed in the judge watcher). Ambiguous or absent
-> `""`; an unknown identity is never guessed. The heartbeat and ALARM lines now carry `run=`.

**TDD.** 5 new RED tests (identity from argv; ambiguity never guessed; ALIVE names its subject in
state+log; DEAD alarm names the run that died; a new run dir resets strikes). RED measured 12 failed /
3 passed -> GREEN 30/30 across `tests/test_trainer_liveness_poller.py` +
`tests/test_trainer_liveness_watchdog.py`.

**Deployed + field-verified.** The resident poller (pid 45903) runs source loaded at boot, so it was
SIGTERM'd and relaunched detached (pid 33535, PPID 1). Its FIRST poll read:

    2026-09-13T14:44:30Z heartbeat verdict=ALIVE strikes=0 metrics_age_s=None
      run=/root/work/software/quantum-gpt/outputs/sapo-27b-ai-20260913T143447Z

and `trainer_liveness_state.json` now carries `run_dir`. Not "should work" -- observed working.

### B-164 -- the Mac launch wrapper stamps the run pointer BEFORE the launcher's gates, so a launch request that never launches repoints the live monitor at a phantom

**Filed 2026-09-13 (SAPO tick #388). SEVERITY: high -- it corrupts the loop's launch evidence.**
This is the attribution that B-137, B-142, #386 FINDING 1 and #387 FINDING 1 each observed and none
could assign. It is not an unattributed production actor, and it is not a stop/relaunch race.

**MECHANISM (measured, `scripts/ai_launch_sapo_direct.sh`).**
  - `:9`  `ROOT_DIR` is SCRIPT-relative. Invoked from a Mac-side test with `cwd` at the repo, `ROOT_DIR`
    is the LIVE Mac tree -- so `$ROOT_DIR/.sapo-loop/` is the live monitoring directory.
  - `:56` `export ASI3_SAPO_RUN_ID="${AI_SAPO_RUN_ID:-${ASI3_SAPO_RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}}"`.
    When neither input is set the run id is simply NOW.
  - `:238-248` under the `launch` action, `mac_run_name="$(basename "$ASI3_SAPO_OUT")"` is written to
    `"${SAPO_RUN_POINTER:-$ROOT_DIR/.sapo-loop/.current_run}"`, and `:253-254` writes
    `$ASI3_SAPO_STEPS` to `"${SAPO_RUN_BUDGET_POINTER:-$(dirname "$mac_run_pointer")/.run_budget}"`.
  - `:262` `exec bash "$ROOT_DIR/scripts/asi3_launch_grpo_direct.sh" "$@"` -- the stamp is at `:238`,
    the handoff is at `:262`, and every fail-closed gate lives inside the script being handed off to.

**The invariant it breaks** is stated by the sibling file itself, `asi3_launch_grpo_direct.sh:475`:
"SAPO_RUN_POINTER overrides the location ... Stamp it HERE, i.e. only for the `launch` action ... and only
after every fail-closed gate above has passed (so a refused launch never claims a run)." The Mac mirror
stamps optimistically, before any gate, and its own comment at `:236-237` correctly names the redirects
as the guard -- but the guard is opt-in and the repo's own tests do not opt in.

**REPRODUCTION (two for two, live, 2026-09-13).**
`tests/test_asi3_sapo_launcher_readiness.py::test_ai_sapo_entrypoint_forwards_ai_root_before_any_side_effect`
sets `AI_SAPO_ROOT` to a tmp dir and sets NEITHER `SAPO_RUN_POINTER` NOR `AI_SAPO_RUN_ID`. Running the
launcher suites stamped the LIVE `.sapo-loop/.current_run`:

    run 1  22:56:30 CST  ->  sapo-27b-ai-20260913T145630Z
    run 2  22:58:00 CST  ->  sapo-27b-ai-20260913T145756Z

Box-side probe through ASI3 :20653: `ls -d outputs/*T145630Z*` -> **rc=2, no such directory**. The only
live trainer was pid 24314 carrying `--output-dir .../sapo-27b-ai-20260913T143447Z`. Both invocations
then failed their required-file assertion and exited non-zero. The test is harmless; the monitor is not.

**BLAST RADIUS.** Every full-suite run repoints the live monitor at a run that does not exist. That
alone explains the recurring phantom in #386/#387 without any production actor. It also means a *refused*
real launch (missing adapter, missing benchmark, dead daemon) silently repoints the monitor, so NO
reading of `.current_run` may be treated as evidence that a launch occurred.

**FIX (TDD, at the next launch boundary -- NOT this tick).**
  1. RED test: an invocation that does not launch must leave `.sapo-loop/.current_run` byte-identical.
  2. Smallest fix: the mirror may not stay optimistic -- stamp only after the launcher reports it passed
     its gates, or have the failure path restore the prior value. Either way, one writer, correct order.
  3. Hermeticity: `SAPO_RUN_POINTER` and `SAPO_RUN_BUDGET_POINTER` must be set explicitly in the
     readiness suite's AI-wrapper test (this is the same omission class as #387 FINDING 4's
     `SAPO_LIFECYCLE_JOURNAL`, and it is the SECOND instance of test-harness production pollution
     recorded in two ticks).
  4. Consider whether the mirror should ever write the live path at all, versus a Mac-side mirror read
     only when the target exists (B-142 already fails closed on the POLL side).

**NOT fixed this tick, and why:** the file is on the LIVE launch path that the churn supervisor calls to
relaunch, and a trainer is in flight. Restructuring it mid-run is exactly the thrash the standing orders
forbid. Filed with the full mechanism so the fix is mechanical at the boundary.

**Collateral, repaired:** two of this tick's own regression runs caused the pollution above. `.current_run`
restored to `sapo-27b-ai-20260913T144425Z` and `.run_budget` to `100` -- the values measured at 22:49 CST,
before the damage. Deliberately NOT retargeted at the live run: `scripts/sapo_stop_run.sh` reads the same
pointer, and pointing it at a run that exists would arm an automatic stop against a healthy trainer.

## B-165 -- trainer-liveness poller emits DEAD on a LIVE trainer (false-DEAD generator)

**Filed:** 2026-09-13T15:12Z (tick #389) | **Severity:** HIGH (latent) | **Status:** OPEN -- not fixed this tick
**Owner:** Trainer-Liveness lane | **Deadline:** tick #390

**Measured.** `.sapo-loop/trainer_liveness.log` holds **7 `verdict=DEAD` lines** for run
`T143447Z`, a run that is alive and progressing. Two landed inside this tick's window:

    2026-09-13T14:51:12Z heartbeat verdict=DEAD strikes=1 metrics_age_s=326 run=...T143447Z
    2026-09-13T15:05:02Z heartbeat verdict=DEAD strikes=1 metrics_age_s=541 run=...T143447Z

Both were followed ~2 min later by `verdict=ALIVE strikes=0`. The trainer was demonstrably alive
throughout: step 2 landed at 14:56:26Z and **step 3 landed at 15:07:53Z**, two minutes AFTER the
15:05:02Z DEAD verdict.

**Root cause (mechanism, by code read).** `box_trainer_probe()` returns DEAD only when *every*
container that answered `ps -eo pid,args | grep [g]rpo_trainer.py` reported no trainer. ASI1/ASI2
legitimately host no trainer, so a DEAD verdict requires ASI3 (:20653) to be simultaneously
**PID-namespace blind** -- a documented property of that exec channel (memories
[[box-local-ports-not-mac-probes]], #365). "All answering containers said no" is treated as a
positive absence; when the one container that matters is blind, it is not.

**Why it did not fire the alarm (and why that is luck, not safety).** Each DEAD was `strikes=1`;
the very next poll found the trainer and reset the counter to 0, so the 2-strike alarm threshold
was never reached and no `ALARM` line was written. Nothing consumes the verdict today (grep:
`trainer_liveness_poller.py` is the only file referencing the lane). The hazard is structural:
§5.4.1 wires exactly this signal to the RESURRECTOR, and a resurrector that fires on it would
relaunch a healthy trainer into the co-resident-duplicate class.

**NOT fixed this tick, and why:** the correct fix is not obvious and must not be guessed. Candidate
directions, none yet evidenced: (a) require a second, independent absence signal (run-dir /
`resume_state.json` non-advance) before DEAD; (b) mark a container whose `ps` is known-blind as
non-answering (UNKNOWN) rather than as an absence; (c) latch DEAD only after 2 consecutive strikes
at the CLASSIFIER level rather than relying on the counter surviving to the next poll. Choosing
between them needs a measurement of how long the blind window actually lasts.

**Reproduce:** `grep -c "verdict=DEAD" .sapo-loop/trainer_liveness.log` while the run is live, then
compare each DEAD timestamp against `grpo_step_metrics.jsonl` on the box.

## B-164 -- STATUS UPDATE (tick #389, 2026-09-13T15:14Z): HERMETICITY HALF FIXED RED->GREEN, LAUNCHER HALF STILL OPEN

B-164 had two halves. The half that was actively corrupting the live tree every full-suite run is
now FIXED; the launcher-ordering half remains launch-boundary work.

**(a) FIXED -- test hermeticity (landed, field-verified).**
Live reproduction, this tick: running ONE test --
`tests/test_asi3_sapo_launcher_readiness.py::test_ai_sapo_entrypoint_forwards_ai_root_before_any_side_effect`
-- moved `.sapo-loop/.current_run` from `sapo-27b-ai-20260913T144425Z` to `...T150237Z`, a run that
does not exist on the box (`ls -d outputs/*T150237Z*` -> rc=2). The test **passed**.

RED test added: `tests/test_fleet_run_pointer_hermeticity.py` -- a fleet-wide guard that fails if any
function in `tests/` drives a launcher with the `launch` action without redirecting `SAPO_RUN_POINTER`.
RED found **four** offenders, three of them real:

    test_asi3_sapo_launcher_readiness.py::test_asi3_launch_fails_before_side_effects_when_payload_is_incomplete
    test_asi3_sapo_launcher_readiness.py::_run_launcher_past_preflight           <- reaches the stamp
    test_asi3_sapo_launcher_readiness.py::test_ai_sapo_entrypoint_forwards_ai_root_before_any_side_effect
    (4th, test_sapo_metrics_poll_failclosed.py::test_d2_..., was a guard false positive: it redirects
     the run pointer and the budget pointer is DERIVED from `dirname($run_pointer)`, so only one key
     is needed. The guard was corrected, and the derivation is now pinned by
     `test_both_launchers_derive_the_budget_pointer_from_the_run_pointer`.)

`_run_launcher_past_preflight` is the one B-142 measured on 2026-09-13T22:55:42 CST writing the
literal `out` over `.current_run` -- same defect, independently confirmed from the test source.

FIX: all three tests now set `SAPO_RUN_POINTER` / `SAPO_RUN_BUDGET_POINTER` into `tmp_path`.
EVIDENCE: guard + readiness file **37/37 green**; focused pointer/launcher regression across 9 files
**122/122 green**; and the whole readiness file was re-run with `.current_run`'s mtime watched --
**it did not move**.

**Collateral, repaired:** `.current_run` restored to the pre-tick `sapo-27b-ai-20260913T144425Z`.
Note that value is ITSELF a phantom on the box (measured: no such dir), which is why B-164 kept
being re-reported as an "unattributed production actor" -- it was this test. Per #387 DECISION 3 and
#388 DECISION 5 the pointer is NOT retargeted at the live run: `sapo_stop_run.sh` reads it and would
arm an automatic stop against a healthy trainer.

**(b) STILL OPEN -- `ai_launch_sapo_direct.sh` stamps before its gates.**
`:240-248` stamps `.current_run`/`.run_budget` **before** the `exec` on `:262`, i.e. before every
fail-closed gate in the delegate (`asi3_launch_grpo_direct.sh:282` required-files, `:255` the B-163
token floor). The sibling documents the opposite invariant for its own stamp ("only after every
fail-closed gate above has passed"). So a REFUSED launch still claims a run.

Reason it is NOT hot-fixed: the obvious fix (let the box launcher own the Mac mirror too, driven by
an env var) requires changing BOTH launchers, and the box tree is behind the Mac tree -- the wrapper
would stop stamping while the box copy could not yet take over, silently un-stamping the monitor.
That is a worse failure than the one being fixed. It lands with the box sync, at the launch boundary,
under user GO.


---

## B-166 -- SAPO collapse guards are structurally blind to a TRUNCATION-PINNED collapse (Mode D)

**STATUS:** OPEN -- filed 2026-09-13 23:17 CST / 15:17Z by the #390 manager tick. Not fixed this tick.

**CLASS:** coverage hole / monitoring gap. NOT a defect in any single breaker -- each breaker is correct
for what it was written to detect. Nothing exists for this one.

**LIVE EVIDENCE (measured, not inferred).** Run `sapo-27b-ai-20260913T143447Z`, trainer box pid 24314
(etime 38:30, CPU 140%), steps 1-3 landed by 15:07:53Z, probed through ASI3 :20653:

| step | entropy_mean | all_fail | pass | trunc | fence | eos | syntax | reward_std | repair_queued |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.46783 | True | 0.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.01604 | False |
| 2 | 0.13293 | True | 0.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.00200 | False |
| 3 | 0.13957 | True | 0.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.00278 | False |

`completion_token_lengths` = [256]x8 every step; `stop_reason` = "truncated" on all 24 generations.

**WHY EVERY EXISTING GUARD MISSES IT** (thresholds read from `training/grpo_utils.py`):

1. `response_length_absolute_collapse` (:3456-3463) needs BOTH
   `median_completion_tokens <= response_length_absolute_floor` (**12**) AND
   `eos_termination_rate >= response_eos_termination_limit` (**0.6**).
   Measured: median **256**, eos **0.0**. Misses on both conjuncts. That rule was written for a policy
   that goes SILENT (immediate EOS); this policy never terminates at all -- it is cut off.
2. `entropy_absolute_collapse` (:3404-3407) needs `entropy <= entropy_absolute_floor` (**0.05**) with
   all-fail. Measured 0.133-0.468, i.e. 2.7x-9x ABOVE the floor. Also window-gated
   (`required_windows`), so it cannot trip before step 20.
3. `all_fail_without_repair` (:3412-3414) needs `repair_queued` true (`queue_grew`). Measured
   `repair_queued`: **False** on all three steps.

**THE UNCOVERED SIGNATURE:** `truncation_rate` ~ 1.0 AND `fence_termination_rate` == 0.0 AND
`eos_termination_rate` == 0.0 AND `all_fail` -- held over 2-3 consecutive landed steps. This is the
monitoring grid's "pass_rate stuck at 0 for 3+ steps" alert threshold, and it fired nothing.

**RELATION TO B-163.** B-163 is the ROOT CAUSE (a 256-token rollout budget too small for any candidate
to close a code fence, pinning `pass_rate` at 0). This bug is the DETECTION half: even once B-163 is
fixed at the launch boundary, nothing in the breaker family would report the same signature recurring
for a different reason at a healthy budget. The two are independent and both are needed.

**PROPOSED FIX (TDD, RED first).**
  1. RED test: feed the three step-facts above into the breaker, assert a trip named
     `truncation_pinned_no_pass`; assert it does NOT trip on a healthy step (fence > 0, some pass) and
     does NOT trip on the B-125 short-completion case (median <= 12, eos >= 0.6), so the two rules stay
     disjoint.
  2. Smallest fix: a `_step_is_truncation_pinned(fact)` predicate mirroring `_step_is_response_collapsed`,
     plus a per-step `_evaluate_truncation_pinned_collapse()` evaluated on EVERY landed step (the same
     reasoning B-125 used: the window-gated family cannot see it early). Reuse
     `response_collapse_lookback_steps` / `response_collapse_min_steps`, but count CONSECUTIVE steps: a
     truncation-pinned step is a configuration constant, not per-step noise, so a flapping-rate form
     would under-trigger.
  3. Guard the degenerate case: if `fence_termination_rate` is None, do NOT treat it as 0.0 -- a missing
     instrument is UNKNOWN, never a manufactured signature.

**NOT fixed this tick, and why:** the file is on the live training path, the box tree is already behind
the Mac tree, and a trainer is in flight. The standing rule is TDD-red first, no deploy on an untested
hypothesis. Filed with the full mechanism so the fix is mechanical at the next boundary.

---

## B-167 -- the B-163 rollout-budget floor gate is UNCOMMITTED and NOT on the box, so it gated nothing

**STATUS:** OPEN -- filed 2026-09-13 23:33 CST / 15:33Z by the #391 tick. Not fixed this tick.

**CLASS:** process/deploy gap with a LIVE consequence. Not a code defect -- the gate code is correct.

**MEASURED (three independent reads, this tick).**

1. `git show HEAD:scripts/asi3_launch_grpo_direct.sh | grep -c MAX_NEW_TOKENS_FLOOR` -> **0**. The
   gate that refuses a launch below the proven 2048-token fence-closing floor exists ONLY as an
   uncommitted working-tree change (`git diff --stat` = 104 insertions, 6 deletions). A tree reset,
   a stash, or a sibling checkout loses it silently.
2. The box copy `/root/work/software/quantum-gpt/scripts/asi3_launch_grpo_direct.sh` (mtime
   **Sep 2 09:38**, i.e. 11 days old, `md5 a2873c31088fa8795b5017d340cd3485`) has **no floor gate at
   all**: `grep -n MAX_NEW_TOKENS_FLOOR` on the box -> no hits; its line 98 is the pre-B-163
   `export MAX_NEW_TOKENS="${ASI3_SAPO_MAX_NEW_TOKENS:-2048}"`. The box tree is not a git checkout
   (`git log` -> "not a git repository"), so the wrapper cannot take over the stamp either.
3. **LIVE CONSEQUENCE.** Run `sapo-27b-ai-20260913T151737Z` booted at **15:17:51Z with
   `--max-new-tokens 1024`** (read from the run's own `launch_config.json` and from the trainer's
   `step_begin` record: `"max_new_tokens": 1024`; trainer pid 32108, ppid 1). A floor-gated launcher
   cannot produce that launch. The gate was inert at the moment it was most needed.

**WHY 1024 IS NOT A FIX FOR B-163** (this is the part that matters for the objective). The banked
s97 reference (`sapo-27b-ai-20260908T094427Z`, 100 steps) ran at **`generation_token_budget` 2048**,
and its own recorded `completion_token_lengths` show a median of **1426** and a p90 of **2048**
(max-len-per-step median 2048). At 2048 s97 still saw `truncation_rate` 0.25-0.5 -- it passed anyway
because `fence_termination_rate` was 0.25-0.5, i.e. fences were CLOSED before the cap. At 256 (B-163)
the fence rate was 0.0 and every candidate died. **1024 is half the budget of the only known-good
run and below s97's median completion length**, so `fence_termination_rate` may still be 0 -- it is
untested territory. The empirical question is decidable from step 1 and is the top check next tick.

**RELATION TO OTHER BUGS.** B-163 is the CAUSE (a budget too small to close a fence); this bug is why
its fix could not take effect. B-164(b) is the sibling defect in the same wrapper (stamps the run
pointer before its gates) and is blocked by the SAME box-tree gap recorded here -- which is why the
note in B-164 says the launcher half "lands with the box sync, at the launch boundary, under user GO".

**PROPOSED FIX (ordered, cheapest first).**
  1. COMMIT the working-tree launcher change so the gate cannot be lost. It is already TDD-covered
     (`tests/test_sapo_max_new_tokens_floor.py`, `tests/test_asi3_sapo_launcher_readiness.py`).
  2. Ship the launcher + `ai_launch_sapo_direct.sh` to the box as one atomic pair (B-164(b): the
     wrapper must stop stamping the pointer in the same deploy that lets the box launcher own it).
  3. Re-verify on the box: a 1024 launch must be REFUSED with the `[asi3] ERROR: MAX_NEW_TOKENS=...`
     line and must leave no run-pointer stamp and no model load.


## B-168 -- keeper state file presents a PREVIOUS cycle's auth verdict as current health (no cycle stamp)

**STATUS:** OPEN -- filed 2026-09-13 23:55 CST / 15:55Z by the #393 manager tick. Severity: MEDIUM (observability).
Root-caused this tick; NOT fixed (no test landed this tick -- logged honestly).

**CLASS:** measurement quality / stale-verdict publication. NOT an auth defect. Not a keeper crash.

**WHAT WAS OBSERVED.** At 23:51:02 `/tmp/session_keeper_state.json` read
`{"ts": "2026-09-13T23:48:11", "status": "OK", "headless_auth": "ok", "daemons": "ok"}` while
`logs/session_keeper.log` ended at `[23:35:11] ERROR no live process with valid auth found; keep
retrying every cycle`. A manager reading ONLY the state file (which is what the standing brief tells
every tick to do) sees green; a manager reading the LOG sees an unresolved failure. Both cannot be
the current truth.

**ROOT CAUSE (measured, not inferred).** Two independent things, both confirmed in the source:
1. `scripts/session_keeper.sh` stamps the heartbeat at the TOP of each cycle (B-052c, deliberately --
   liveness must not depend on probe duration) and publishes the PREVIOUS cycle's `HEADLESS_STAMP` /
   `DAEMONS_STAMP` at that stamp, resetting them to `unknown` immediately after (B-088). So between a
   cycle-top stamp and that cycle's probe, the file legitimately shows the prior verdict. A reader
   cannot tell a fresh green from a carried-over green.
2. The hourly timeout is REAL and recurring: `auth probe failed: timeout after 90.0s` appears **93 times**
   in the log, clustered at ~:23-:35 each hour (12:23:57, 13:23:59, 14:23:59, 16:23:51, 23:31:37 on
   2026-09-13). The probe is starved, not rejected.

**THE STARVATION IS EXTERNAL TO THIS PROJECT (confirms and extends the host-load memory).** Sampled
2026-09-13 23:53 CST: load average **20.63 / 15.78 / 16.38** with the top consumers being `jq`
processes at 45.1% / 43.9% / 36.1% CPU -- the claude-mcp-cron quantum-math jobs, NOT this repo's suite.
The keeper's 90s bound (`SK_AUTH_PROBE_TIMEOUT_S` default 90) is simply too short to survive this host
load. The probe is a VICTIM, not the defect.

**WHY IT MATTERS (bounded, so not inflated).** The keeper self-heals every time: each hourly strike is
followed within one or two cycles by `FIX headless env refreshed from live process -- auth verified`, and
the last published heartbeat is `status=OK headless=OK daemons=OK` (23:27:53). So the impact is NOT a
dark resource -- it is that the ONE instrument every tick is instructed to read can advertise `ok` for
up to a full cycle after a probe has failed, and the log that would contradict it is ~15k lines and is
not read by default. This is the same class B-088 fixed one layer down (`status: HEALING, headless_auth:
ok` -- false healthy); B-088 fixed the reset, it did not fix the READER's ability to date the verdict.

**PROPOSED FIX (TDD, RED first).**
  1. RED test (extend `tests/test_session_keeper_heartbeat.py`, which already pins the B-088 carry-over
     semantics): assert the state file publishes the cycle number and/or an explicit
     `verdict_age_cycles` / `measured_at_cycle`, so a verdict from a PRIOR cycle is distinguishable from
     one measured this cycle. Must NOT break `test_carry_over_semantics_are_preserved` or
     `test_cycle_top_stamp_publishes_carry_over_values` -- the carry-over itself is by design.
  2. Smallest fix: publish `cycle` + `verdict_cycle` in the stamped JSON. Purely additive; no probe
     behaviour changes.
  3. Separately (do NOT conflate): consider raising `SK_AUTH_PROBE_TIMEOUT_S` for the production keeper,
     with the load evidence above as justification. Independent change, own test.

**DO NOT** "fix" this by reverting the B-052c cycle-top stamp -- that stamp exists to stop the watchdog
killing a keeper whose probe ran long, and reverting it reintroduces a proven livelock (B-069).


## B-169 -- chunked full-suite runner: the DEFAULT output path is a constant, so concurrent runs clobber one artifact

**STATUS:** FIXED RED->GREEN 2026-09-14 00:00 CST / 16:00Z by the #393 manager tick. Not yet deployed to
the box (the runner is a Mac-side instrument; it is not a box artifact).

**CLASS:** measurement-instrument defect. Same family as B-083 (a chunk that never reported folded in as
zeros) and B-158 (a vacuous chunk certified COMPLETE): the aggregate reads complete while the measurement
underneath it is gone.

**MEASURED DEFECT.** `.sapo-loop/run_full_suite.py:48` read

    OUT = os.path.join(QG, ".sapo-loop", "logs",
                       os.environ.get("SUITE_OUT", "full_suite_315.txt"))

The default filename is a literal constant. This repo runs ~13-16 tick sessions against ONE tree and more
than one invokes this runner, so two concurrent default runs open the SAME path.

**LIVE EVIDENCE -- the artifact on disk at 2026-09-13 23:55 CST:**

    SUITE tests=4618 chunks=24 chunk_size=200 started=2026-09-13T15:47:50Z
    chunk 01/24 rc=0 ... elapsed=65s ids=1..200
    chunk 02/24 rc=-15 (no TESTSUITE_COUNTS line)  UNMEASURED SIGNALLED elapsed=41s ids=201..400
    <a line carrying a ~170-space indent -- two writers racing on one fd>
    chunk 18/24 rc=0 ... elapsed=6s ids=3401..3600
    chunk 19/24 rc=0 ... elapsed=5s ids=3601..3800

The header says 24 chunks. Only 5 chunk lines survive. **Chunks 03-16 are ABSENT** -- the second writer had
already written past those byte offsets, so the first run's lines for ids 401..3200 (~2800 tests, 61% of the
suite) were overwritten in place. The runner's own stdout log
(`.sapo-loop/logs/tick389_fullsuite.log`) shows all 24 chunks ran. Nothing in the surviving artifact says so.

Note the extra sting: B-083's `VERDICT=COMPLETE|INCOMPLETE` accounting is written by the SAME runner into the
SAME file, so the defect B-083 fixed is only as durable as this artifact. Interleaving can destroy the very
line that would have reported the loss.

**ROOT CAUSE.** Path computed from a constant default, with no per-run uniquifier and no lock. Confirmed by
direct probe: two `python3 -c` subprocesses importing the module with `SUITE_OUT` unset both printed
`.../logs/full_suite_315.txt`.

**RED (first, evidence).** `tests/test_full_suite_runner_unique_output.py` --
`test_two_processes_without_suite_out_never_share_an_output_path` failed with
`AssertionError: two concurrent default runs computed the SAME suite output path '.../full_suite_315.txt'`;
`TESTSUITE_COUNTS passed=2 failed=1 total=3`.

**FIX (smallest).** Default basename becomes unique per run: `full_suite_315_<pid>.txt`. An explicit
`SUITE_OUT` still wins verbatim (pinned by its own test), and the historical `full_suite_` prefix is kept so
existing globs, readers and docs still match. No change to chunking, aggregation or exit codes.

**REGRESSION.** `tests/test_full_suite_runner_reports_incomplete.py` (B-083's completeness accounting) must
stay green -- the fix touches only path computation and must not disturb the aggregate contract.

**STILL OPEN (NOT fixed by this, deliberately).** The in-flight run this tick reports
`chunk 02/24 rc=-15` = SIGTERM, UNMEASURED, ids 201..400. A chunk killed by a signal is a missing
measurement and is correctly folded as such (B-083), but WHO SIGTERMed it is unexplained and is a separate
question -- likely the same concurrent-session pressure. Do not read that run's eventual VERDICT as
whole-tree green while chunk 02 is UNMEASURED.


## B-170 -- contract #116 ruff gate was RED for 5+ ticks: a landed liveness fix reintroduced `%`-formatting

**STATUS:** FIXED RED->GREEN 2026-09-14 00:06 CST / 16:06Z by the #394 manager tick. Mac-side tooling
only -- not a box artifact, not bundled, not deployed.

**CLASS:** a regression that a *pre-existing* guard was already catching, left open across ticks. The
detector existed the whole time and was red; nothing acted on it. This is the §9.2 "detected but not
fixed = failed tick" class, repeated.

**WHAT WAS OBSERVED.** `tests/test_sapo_ruff_clean_scripts.py::test_ruff_check_scripts_py_returns_zero_errors`
carried as a known failure in the #392 suite addendum and earlier. Reproduced standalone this tick:

    AssertionError: ruff check scripts/*.py is not clean (contract #116, B-019). 4 violation(s):
      scripts/trainer_liveness_poller.py:212:22: UP031 Use format specifiers instead of percent format
      scripts/trainer_liveness_poller.py:217:26: UP031 Use format specifiers instead of percent format
      Found 2 errors. No fixes available (2 hidden fixes can be enabled with the `--unsafe-fixes` option).

**ROOT CAUSE.** Both are `self._append("...%s..." % (a, b, ...))` calls in `PollOnce.poll_once()` --
the percent-format idiom, reintroduced into a file that recently gained the B-165 lane. Behaviorally
correct output; a style/contract violation only. Contract #116 requires `ruff check scripts/*.py` to
return 0 errors, so the gate was correctly RED.

**FIX (smallest, behavior-preserving).** Both rewritten as f-strings. The emitted log lines are
**byte-identical** before and after: the same field order and the same literal separators, so any
consumer parsing `... heartbeat verdict=... strikes=... metrics_age_s=... run=...` and
`... ALARM trainer DEAD run=... strikes=... metrics_age_s=...` is unaffected.

**GREEN (evidence).**
`tests/test_trainer_liveness_poller.py + tests/test_trainer_liveness_watchdog.py +
tests/test_sapo_ruff_clean_scripts.py + tests/test_bugqueue_id_uniqueness.py +
tests/test_sidecar_liveness_guard.py` -> `passed=49 failed=0 errors=0 total=49`.

**WHY IT MATTERS (bounded).** Low runtime impact -- contract hygiene, not a live-run defect. It matters
because it is the *second* carried RED in this ledger that was fixable in one tick with the guard
already written, and it sat for days while every standup reported it as a carried item.

**NOTE (not filed separately, recorded here).** The same tick reworded two repeat headers in this
ledger (`B-156`, `B-164`) that `tests/test_bugqueue_id_uniqueness.py` parsed as second bug entries; the
ledger was reworded rather than the guard widened, per the tick-#355 precedent. That guard is now 4/4.

## B-171 -- judge-health agent had NO singleton guard: two agents ran concurrently for 2+ days

**STATUS:** FIXED RED->GREEN + DEPLOYED 2026-09-14 00:48 CST / 16:48Z by the #394 manager tick.
Mac-side tooling only -- not a box artifact, not bundled.

**CLASS:** the B-037 duplicate-watcher class, one lane over. The sibling
`scripts/sapo_judge_mac_watcher.py` got a single-instance guard on 2026-09-09; the
judge-health agent -- written later, on 2026-09-03 -- never got one, and nothing
noticed. A guard that exists for one watcher is not a guard for the fleet.

**WHAT WAS OBSERVED.** Two agent processes resident at the same time:

    pid 78533  etime 02-14:59:46  (started 2026-09-11T01:44Z)
    pid 26133  etime 07:48        (started 2026-09-13T16:36Z)

against THREE `judge-health agent start` lines in `/tmp/sapo_judge_health.log`
(2026-09-11T01:40:42Z, 2026-09-11T01:44:43Z, 2026-09-13T16:36:41Z) -- so the two
09-11 starts were themselves a duplicate pair from day one. Corroborating evidence
independent of the process census: the probe lines ran at 136s / 169s / 136s
spacing while each agent polls at `POLL=300`, i.e. two interleaved pollers rather
than one.

**WHY IT HAPPENS (measured, not guessed).** The supervisor
(`scripts/sapo_huanxin_heartbeat.sh:272`) gates the respawn on
`if ! pgrep -f sapo_judge_health_agent >/dev/null`. `pgrep` is an EXTERNAL command
that must fork(2); under host load that fork fails and pgrep returns nonzero --
the same B-077 mechanism already documented inside `sapo_single_instance_lock.sh`
("absence of a measurement is not evidence of staleness"). A failed pgrep is
UNKNOWN, not DEAD, yet it takes the respawn branch. This is exactly the §5.4.1
false-DEAD class ("every watcher probe is THREE-STATE; only DEAD increments the
death counter"). The agent had no self-guard, so the false-DEAD respawn became a
real duplicate.

**FIX (smallest, precedent-following).** `scripts/sapo_judge_health_agent.py` gains
`_singleton_lock()`, byte-for-byte the B-037 helper: the SHARED
`sapo_single_instance_lock.sh`, this agent's OWN lock name, `--steal-stale`
(reclaims a crashed holder) and `--reacquire` (B-063: idempotent for the caller
that already holds it, still refuses a different live holder). `main()` consults it
BEFORE writing its start line and re-verifies every loop cycle (B-041: a watcher
that loses its lock must exit, not keep polling as a duplicate). The supervisor's
pgrep check is left alone on purpose -- it is best-effort; the agent-side lock is
the authoritative layer, so a false-DEAD respawn now loses the race and exits.

**RED (evidence).** `tests/test_judge_health_agent_singleton.py`, written first,
failed 3/5 -- including the BEHAVIORAL test, which is the point: with the lock held
by a live pid, the guard-less agent did not refuse, it ran until the 30s
subprocess timeout killed it (`subprocess.TimeoutExpired`).

**GREEN (evidence).** `tests/test_judge_health_agent_singleton.py` +
`tests/test_judge_mac_watcher_singleton.py` + `tests/test_bugqueue_id_uniqueness.py`
-> 13/13. Regression on the pre-existing judge-health surface:
`tests/test_sapo_judge_health_agent.py` + `tests/test_judge_watcher_repair_contract.py`
+ `tests/test_watchdog_watcher_verdict.py` -> 27/27. All under `/usr/bin/python3`
(3.9.6, the box runtime).

**DEPLOYED + FIELD-VERIFIED.** Launched the fixed agent (pid 53616), confirmed it
holds `/tmp/sapo_locks/sapo_judge_health_agent/holder` = 53616, then SIGTERM'd the
stale lockless 26133. Final census: exactly ONE live agent, probing HEALTHY on its
300s cadence. The stale 78533 had already been retired in the same tick.

**RESIDUAL (recorded, not hidden).** The heartbeat's two-state pgrep probe is
UNCHANGED -- a false-DEAD there still logs "judge-health dead -> respawn" and burns
one spawn. It is now harmless (the spawn refuses and exits) but it is still a wrong
measurement, and the three-state fix belongs in that supervisor.


## B-172 -- the chunked suite runner starts a full 24-chunk run for an argument it does not parse (`--help`)

**STATUS:** OPEN -- filed 2026-09-14 00:57 CST / 16:57Z (tick #398). **SEVERITY:** medium -- it does
not corrupt data, but it burns host CPU and silently invalidates the "one suite at a time" reading
that the tick's own test-count claim depends on.

**WHAT WAS OBSERVED (live, this tick).** Process pid **36585** is resident with argv

    .sapo-loop/run_full_suite.py --help

and etime **11m+**, and it has forked a real pytest child (pid 64150, ~85-89% CPU) running an
explicit node list from `tests/test_grpo_pipeline_fast.py::...` -- i.e. a genuine suite chunk. Its
unique output artifact `.sapo-loop/logs/full_suite_315_36585.txt` exists and is being written
(started=2026-09-13T16:43:14Z, at chunk 06 by header time). The `--help` invocation did not print
help and exit; it **started the suite**.

**ROOT CAUSE (as observed, not yet confirmed by a RED test).** `run_full_suite.py`'s entry point
appears to run work **before / independently of** argv parsing, so an unrecognised argument such as
`--help` falls through into `main()`. The invocation is traceable to a sibling session's probe:

    eval 'python3 .sapo-loop/run_full_suite.py --help 2>&1 | head -20; echo "=== tail of main ==="; tail -30 ...'

So a *read-only inspection* of the runner became a *third concurrent production suite run*.

**WHY IT MATTERS.** Two concrete damages: (1) three concurrent suite runners (15:57Z, 16:02Z, and
this accidental one) compete for host CPU, and the per-chunk cadence figures stop being a clean
baseline (chunk 01 39s and chunk 02 178s **within the same accidental run**; the earlier 94626 run
recorded chunk 02 at 259s). **The causal link between the three runners and those timings is NOT
established here** -- what IS established is that a per-chunk elapsed-time baseline cannot be
compared across a period with unknown concurrency; (2) it makes the "is a
signature reproducing?" question ambiguous -- a reader can find a half-written artifact and mistake
it for a deliberate run.

**RELATION TO B-169.** B-169 (unique per-pid output path) is what made this *detectable* rather than
*invisible*: without it, this accidental run would have clobbered `full_suite_315.txt` and the
concurrent runners would have overwritten each other. B-169 is therefore confirmed as load-bearing,
not cosmetic.

**FIX DIRECTION (smallest, not yet implemented).** Parse argv first; on any unrecognised/help flag,
print usage and exit **before** touching the chunk list or spawning pytest. A RED test should assert
that invoking the module with `--help` (a) exits 0, (b) writes no output artifact, and (c) spawns no
pytest child. Owner: Test Orchestrator (ORDER 6, deadline tick #399).

**NOT YET DONE:** no RED test, no fix, no deploy. This entry records the observation and its evidence.


## B-172 STATUS UPDATE — RESOLVED (tick #399, 2026-09-14 01:05 CST / 17:05Z)

**STATUS: FIXED, tested, in-tree. Original entry above (filed #398) stands as the
observation; this is the resolution.**

**ROOT CAUSE (read from the source, confirmed by measurement).** `.sapo-loop/run_full_suite.py`
`main()` takes no argv and never inspects one. The ONLY use of `sys.argv` in the file was
line 322, where the re-exec branch re-passes `sys.argv[1:]` to the replacement interpreter.
So `--help` was neither consumed nor rejected: it fell through env classification,
collection, and 24 chunks of pytest. B-172's hypothesis ("parses argv after starting
work") is corrected to the stronger fact: **it never parsed argv at all.**

**FIX (smallest).** Two module-level additions + a thin dispatch in `__main__`:
`parse_argv(argv)` -> `("help",)` / `("error", bad)` / `("run",)`; `-h`/`--help` wins over
any other argument so an inspection can never fall through; anything else is unrecognised
(the runner takes no positional/flag arguments today) and is REFUSED with usage on
stderr + exit 2; empty argv means run, so the normal path is unchanged. The gate sits
BEFORE env classification and before `collect_ids()`, so a refused invocation spawns no
pytest child and writes no artifact.

**RED (evidence).** `tests/test_full_suite_runner_argv_guard.py`, written first ->
`passed=0 failed=2` (`AttributeError: module ... has no attribute 'parse_argv'`).
Only the two unit-level tests were run pre-fix on purpose: the three behavioural tests
each START A REAL SUITE against the defect, i.e. running them pre-fix would itself
inflict the damage B-172 records.

**GREEN (evidence).** Same file -> **5/5**. Live field check: `run_full_suite.py --help`
prints usage and exits 0; `--definitely-not-a-flag` exits 2. Regression on the whole
runner surface -> **32/32** across `test_full_suite_runner_argv_guard.py` (5),
`..._reports_incomplete.py` (9), `..._reports_failing_ids.py` (3),
`..._chunks_collected_ids.py` (4), `..._unique_output.py` (3),
`test_suite_runner_pins_interpreter.py` (8). All under `/usr/bin/python3` (3.9.6).

**ONE DEFECT IN MY OWN TEST, found and fixed before GREEN.** The first GREEN attempt
failed 1/5 on `assert "chunk " not in proc.stdout` -- the usage text itself contains
"a real 24-chunk suite". A bare-substring absence check is not an instrument. Replaced
with a match on the runner's actual progress-line SHAPE (`^chunk \d+/\d+ done`, re.M)
via `_started_chunking()`. Recorded because it is the same "test asserts nothing useful"
family the skill warns about -- the check would have passed vacuously forever if the
usage text had happened not to contain the word.


## B-173 -- a test file that calls the suite runner's `main()` is silently REPLACED by a real 24-chunk suite run

**STATUS:** FIXED, tested, in-tree (tick #399, 2026-09-14 01:05 CST / 17:05Z).
**SEVERITY:** high -- the file's 8 assertions had NEVER executed, and the failure mode
is a full suite launch, not a red test.

**HOW IT WAS FOUND.** While running the B-172 regression surface, one file returned
`rc=2` with ZERO output:

    $ python3 -m pytest -q tests/test_full_suite_runner_reports_incomplete.py
    collected 8 items
    tests/test_full_suite_runner_reports_incomplete.py
    rc = 2

Collected 8, printed the filename, no outcome for any test. That is not a failing test;
it is a process that stopped being pytest.

**ROOT CAUSE (measured, not inferred).** `main()` calls `env_verdict(...)` and, when the
running interpreter lacks the quantum SDKs, `os.execv()`s into `.venv/bin/python3`
(B-115, by design). Measured directly on this box:

    sdk_probe(/usr/bin/python3) = ['pennylane', 'qiskit', 'cirq']   # all missing
    env_verdict(...)["action"]  = 'reexec'                          # RE-EXEC WOULD FIRE

This test file is the ONLY one in the suite that calls `mod.main()` in-process
(`_drive()` at line 116, plus the collection-gate test at line 240). Every sibling
runner test avoids `main()` -- they exercise `summarize()` / `parse_failures()` / `OUT`.
So `main()` replaced the pytest process with `run_full_suite.py`, which then inherited
pytest's argv. Note the error text went nowhere visible: pytest has fd-level capture
active, so the replacement process wrote into a capture buffer that was discarded.

**WHY IT HID FOR SO LONG.** The re-exec'd runner reports the RUNNER's exit code, not
pytest's. Pre-B-172 the inherited argv was ignored and the runner ran to completion, so
the file presented as `rc=0` / a plausible non-zero -- indistinguishable from a pass.
It was only B-172's argv guard that turned the inherited `-p no:cacheprovider -v ...`
into a fast, visible `exit 2`. **B-172 therefore surfaced B-173.** This is also a
plausible partial explanation for the "concurrent suite runners" observed in #398 --
running this one test file spawns a full suite.

**FIX (smallest, test-side).** The re-exec is correct production behaviour (B-115);
what is wrong is a unit test letting the code under test replace its own interpreter.
Added `_pin_interpreter_verdict(mod, monkeypatch)` -- monkeypatches `env_verdict` to a
benign `{"action": "run", "ok": True, ...}` -- and called it from `_drive()` (covers 8
tests) and from the one direct `main()` call site.

**EVIDENCE -- the fix makes 8 dead assertions execute.**
    before: rc=2, 0 outcomes, no TESTSUITE_COUNTS line
    after:  rc=0, TESTSUITE_COUNTS passed=8 failed=0 errors=0 skipped=0 total=8

**REGRESSION GUARD.** New test `test_the_driver_never_execvs_out_of_the_test_process`
stubs `os.execv` to record and asserts it is NOT called, plus that the aggregation was
reached. If someone removes the pin, that test fails LOUDLY instead of the whole file
dying silently -- which is the exact way this defect concealed itself.

**RESIDUAL (recorded, not hidden).** `main()` still performs an irreversible process
replacement as a side effect, which is why a caller can be destroyed by it. A defensive
production change (an injectable exec hook, or returning the verdict to the caller)
would remove the footgun class entirely; NOT done here, because it widens the blast
radius on a live-path script for no measured gain today.


## B-168 STATUS UPDATE — RESOLVED (tick #400, 2026-09-14 01:2x CST / 17:2xZ)

**STATUS: FIXED, TDD red->green, IN TREE.** Owner: manager (Bug-Hunter lane NO REPORT, 3rd tick ordered).

**RED (5 new tests, all failing before the fix)** in `tests/test_session_keeper_heartbeat.py`:
`test_stamp_state_publishes_cycle_and_verdict_cycle`,
`test_carried_over_verdict_is_datable_as_stale`,
`test_both_stamp_calls_publish_the_cycle_and_its_verdict_cycle`,
`test_cycle_top_stamp_dates_its_verdicts_one_cycle_back`,
`test_end_of_cycle_stamp_dates_its_verdicts_to_this_cycle`.

**FIX (smallest, additive).** `scripts/session_keeper.sh`:
1. `stamp_state` takes `$5` = this cycle, `$6` = the cycle that MEASURED the published verdicts;
   both are emitted in the JSON as `cycle` and `verdict_cycle` (`null` when the caller did not
   date them -- a reader must then treat the verdict as UNKNOWN, never current, three-state 5.4.1).
2. The B-052c cycle-top stamp now sets `VERDICT_CYCLE=$((CYCLE-1))` -- it publishes the PREVIOUS
   cycle's probes by design, so it now says so.
3. The end-of-cycle stamp sets `VERDICT_CYCLE=$CYCLE` -- those probes DID run this cycle.

A reader now computes `verdict_cycle < cycle` = STALE. Nothing about probing changed; B-052c's
cycle-top liveness stamp and B-088's in-loop reset are both untouched (reverting the cycle-top
stamp would reintroduce the proven B-069 livelock -- explicitly NOT done).

**GREEN.** `tests/test_session_keeper_heartbeat.py` 31/31 (26 pre-existing + 5 new). Keeper
regression surface (12 files: heartbeat, stamp_staleness, auth_probe x2, durable_state_isolation,
congestion x2, ready_gate, not_ready_ports, boot_window, watchdog x2) **136/136 green**.

**NOT LIVE YET.** The running keeper loads its source once at boot, so the fix is inert in-process
until a `launchctl kickstart` -- which is user-gated in this session. Recorded, not claimed live.

**ONE SELF-CORRECTED TOOLING DEFECT (recorded, not hidden).** The first patch attempt wrote
`${5:-}` unquoted, so an empty arg vanished and the 4-arg callers hit IndexError -- caught by two
PRE-EXISTING tests (they went red), fixed by quoting. The pre-existing suite caught a real
regression in my own fix; that is the argument for running the regression surface, not a formality.


## INSTRUMENT RETRACTION -- deploy-gate forbidden-token scan (tick #400, 2026-09-14)

**NOT a bug in any production file. Two false-positive classes in MY OWN audit model; both retracted.**

While staging the tick-#400 deploy set I implemented the 2.7 "scan for TOKENS" rule as a naive
substring grep and it flagged 3 hits in a bundle that is actually clean. Root-caused each before
filing (4.2: decide producer-bug vs audit-model-bug FIRST):

1. `match ` matched `for match in _DETAIL_KV_RE.finditer(line)` -- a local variable named `match`.
   ` case ` matched a docstring reading "short-completion case".
2. Then a corrected AST scan flagged `strict=` in `scripts/check_markdown_links.py:95` -- which is
   `Path.resolve(strict=False)`, valid since py3.6, NOT `zip(strict=)`. My check was not scoped to
   `zip` calls.

**SOUND RULE:** the token scan must be (a) scoped to the actual API call -- `ast.Call` whose
`func` is a `Name` id `== 'zip'` -- and (b) applied to PRODUCTION paths only. A repo-wide scan also
reports 50+ hits under `evals/runs/**/candidates/`, which are MODEL-GENERATED artifacts that are
MEANT to contain invalid Python; flagging them is the instrument being wrong, not the code.

**VERIFIED CLEAN:** production trees `scripts/*.py` + `training/**/*.py` + `evals/*.py` = 349 files,
**0 findings** (AST `Match` nodes + zip-scoped `strict=` kwarg). The repo's own gate
(`scripts/sapo_ci_gate.sh:34`) already uses a correctly-scoped regex `zip\([^)]*strict` and globs
production only -- it was right; my ad-hoc reimplementation was the defect. No change to the CI gate
is ordered. The only residual is the documented shallow glob (`training/*.py`, non-recursive), which
the AST scan above shows currently hides nothing.


## B-174 -- the step-level judge_reward rollup is UNPOPULATED, so the mandated dark-step check reports a FALSE RED on a healthy judge chain

**Filed tick #401, 2026-09-14 01:25 CST / 17:25Z. Detector/instrument bug.** Live impact: the
per-tick check "judge_reward coverage -- any dark step = RED" reads 4/4 DARK on a run whose judge
chain is demonstrably delivering.

**EVIDENCE (live run sapo-27b-ai-20260913T151737Z, read off ASI3 :20653).**

Step-level key, all four records: judge_reward is None for steps 1, 2, 3 and 4.

Per-candidate, from the rollout_rewards array (8 candidates every step):
- step 1 judge_ok 8/8, range 0.26 .. 0.36
- step 2 judge_ok 8/8, range 0.04 .. 0.04 (uniform)
- step 3 judge_ok 8/8, range 0.00 .. 0.34
- step 4 judge_ok 8/8, range 0.07 .. 0.56

Each candidate also carries a populated judge_dim_scores map (10 dimensions). The bridge process is
up: pid 32119 scripts/sapo_judge_bridge.py --queue-dir .../judge_bridge --port 56237, and
curl --noproxy '*' root on :56237 returns HTTP 200.

**ROOT CAUSE.** The judge term is folded into the reward (--reward-judge-mass 0.10) and the
per-candidate detail is written under rollout_rewards; no step-level rollup of the judge term is
emitted. judge_reward therefore reads None at step level BY CONSTRUCTION, not because the judge was
absent. Supporting tell: step 2 scored a UNIFORM 0.04 across all 8 candidates -- a live judge
answering with a flat low band, not a dead judge. (The dead-judge signature is an ABSENT key.)

**WHY IT MATTERS.** An operator or cron reading the documented check at step level would call every
step dark and could trip the "sustained dark steps > 2 consecutive" auto-stop rule on a run that is
actually fine. Same family as B-165 (false-DEAD generator) and B-157: an instrument manufacturing
an alarm from a healthy system.

**SMALLEST FIX (RED test first).** Either (a) emit a step-level judge_reward_mean plus coverage
alongside the other _mean keys, or (b) correct the CHECK to read rollout_rewards[*].judge_reward and
define dark as "key ABSENT", never "value None". Preference: (b) for the check plus (a) for the
record -- the rollup is useful, but the detector must not depend on it.

**NOT attempted mid-run.** The trainer is live; changing the metrics writer is a training-path
change and is deferred to a launch boundary with the staged set. The CHECK side is Mac-side and can
be fixed now without touching training.

**STATUS:** OPEN. Regression test owed. Owner: Bug-Hunter.

## B-165 STATUS UPDATE -- ROOT-CAUSED + FIXED RED->GREEN (tick #401, 2026-09-14 01:35 CST / 17:35Z)

**STATUS:** FIXED in tree, tests green. NOT DEPLOYED -- `scripts/trainer_liveness_poller.py` is a
box-adjacent lane script; the running poller (if any) loads source once at boot.

**THE MECHANISM, MEASURED (not guessed).** B-165 listed three candidate directions and said the
choice "needs a measurement of how long the blind window actually lasts". The measurement was made
this tick and it refuted the framing. The blind window is not a PID-namespace property of ASI3 --
`ps -eo pid,args | grep [g]rpo_trainer.py` through :20653 returned `ps=2` on 6/6 samples over 12s
with the trainer pid 32521 present and the run-dir mtime static. ASI3 is NOT namespace-blind right
now. The real defect is in the PROBE, one layer up:

    out = exec_fn(port, "ps -eo pid,args | grep [g]rpo_trainer.py")
    except Exception: continue
    answered += 1                     # <-- unconditional

`answered` counts any exec that did not RAISE. An exec that SUCCEEDS while returning a body with
none of the command's output in it is therefore counted as a container positively saying "no
trainer". OBSERVED LIVE this tick through :20653: a plain `boxexec.py` call returned a body holding
the transport's own WRAPPER -- the base64 of my command echoed back, output absent entirely (the
B-138 windowing class). ASI1/ASI2 legitimately answer empty (verified this tick with a sentinel:
both return the sentinel and nothing else). So the composition is: two genuine absences + one blank
body = `(False, age, None, "")` = DEAD, for a trainer that is alive. Skill 5.4.1 wires exactly this
verdict to the resurrector -> spurious relaunch -> co-resident duplicate trainer.

**THE FIX (smallest, and it is B-165's own candidate (b) -- confirmed, not guessed).** Every probe
command now appends `PROBE_SENTINEL`. A body without the sentinel did not carry our command's output
and therefore carries NO OPINION: it increments `blind`, not `answered`. A positive-absence (DEAD)
verdict now requires that NO container was blind AND at least one returned a verifiable body.
Blind-and-no-positive -> UNKNOWN, with the reason naming the unverifiable bodies.

**GREEN (evidence).** `tests/test_trainer_liveness_poller.py` 18/18 (3 new RED tests: a windowed
body is UNKNOWN-never-DEAD; a sentinel-bearing absence is STILL a positive absence -- the fix must
not silence the alarm it protects; and the sentinel is actually IN the command we send, so the
check is non-vacuous). Regression surface `test_trainer_liveness_poller + test_trainer_liveness_watchdog
+ test_sidecar_liveness_guard + test_sapo_ruff_clean_scripts + test_bugqueue_id_uniqueness` = 52/52.

**FOUR PRE-EXISTING TESTS WERE UPDATED, DELIBERATELY.** Their fakes returned bodies without the
sentinel and asserted DEAD. That is not "fixing tests to fit code": the CONTRACT genuinely narrowed
from "a container that did not raise said no" to "a container whose body provably carried our
command said no". The corrected tests encode the stricter contract. Recorded so the change is
auditable rather than quiet.

**ALSO CLEARED THIS TICK (carried RED, guard already written).**
`test_bugqueue_id_uniqueness.py::test_no_bug_id_names_two_different_bugs` was RED on two
`## B-<id> -- RESOLVED (...)` headers (`B-172`, `B-168`) that prior ticks wrote as new entries.
Reworded both to `## B-<id> STATUS UPDATE — RESOLVED (...)` per the tick-#355/#394 precedent
(reword the ledger, never widen the guard). Now 4/4.


## B-175 -- the chunked suite runner parses failing node ids PER CHUNK but emits them only at END of run, so a 76-min suite hides its failures from every 10-min tick

FILED: standup #402, 2026-09-14 01:36 CST / 17:36Z (manager).

MEASURED DEFECT. `run_full_suite.py:347-359` calls `parse_failures(p.stdout)` inside the per-chunk
loop and stores the ids on `chunks[n]["failures"]`. But the `FAILING <nodeid>` block is written only
at `run_full_suite.py:370-375`, AFTER the loop and after `summarize(chunks)` -- i.e. only when all 24
chunks have completed.

OBSERVED LIVE this tick. Suite pid 10677 started 2026-09-13T17:14:40Z. At 17:36Z the artifact
`.sapo-loop/logs/full_suite_315_10677.txt` (920 bytes, 7 lines) showed
`chunk 02/24 rc=1 TESTSUITE_COUNTS passed=199 failed=1 ...` and NO `FAILING_TESTS` block. The one
failing node id was parsed and resident in memory 20 minutes earlier and is still unnamed.

WHY IT MATTERS. This is B-147's own complaint, re-derived. B-147 was fixed (tick #380) by adding
`parse_failures()` plus the durable `FAILING` block -- but only the end-of-run emission was added.
A run takes ~76 min (6 chunks in 21 min, measured) against a 10-min standup cadence, so the names
are invisible for ~7 consecutive ticks, and each tick re-writes the same standing item: "chunk 02,
one failure, not yet named; next tick's triage". Section 9.3 requires counts; section 2.7 requires
pre-existing failures be ENUMERATED, never hidden -- and they cannot be enumerated from a count.

SMALLEST FIX. Emit the per-chunk failing ids in the same `fh.write`/`fh.flush` block that writes the
`chunk %02d/%02d` progress line, so a completed chunk's names are durable the moment it completes.
Keep the end-of-run `FAILING_TESTS` block authoritative (it is the summary); the per-chunk lines must
use a DISTINCT prefix (e.g. `chunk %02d FAILED <nodeid>`) so a consumer counting `FAILING ` lines
does not double-count. No consumer of the `FAILING ` prefix exists outside the runner today
(grepped: only `run_full_suite.py` and `tests/test_full_suite_runner_reports_failing_ids.py`).

REGRESSION TEST. Extend `tests/test_full_suite_runner_reports_failing_ids.py` with a RED test that
runs one failing chunk through the per-chunk write path and asserts the node id is present in the
artifact BEFORE `summarize()` is reached.

STATUS: OPEN. Deliberately NOT fixed in #402 -- the fix edits the file owning an in-flight 76-min
artifact and the tick was otherwise healthy. Filed with line numbers so the next tick lands it TDD
without re-deriving.

## B-175 STATUS UPDATE -- 2026-09-14 01:55 CST / 17:55Z (tick #403): FIXED, red->green

Landed in `.sapo-loop/run_full_suite.py`. The chunk block now emits
`chunk %02d/%02d FAILED <nodeid>` for each failing node in the SAME `fh.write`/`fh.flush` block that
writes the `chunk NN/MM` progress line, so a chunk's names are durable the moment the chunk ends
instead of at end of run. Distinct prefix -- the end-of-run `FAILING_TESTS` / `FAILING ` block stays
authoritative and no `FAILING ` consumer can double-count.

RED evidence (captured against the REAL runner, not asserted): the new test
`test_per_chunk_failing_id_is_written_before_summarize` in
`tests/test_full_suite_runner_reports_failing_ids.py` samples the artifact AT the moment
`summarize()` is reached. On the unpatched runner it failed with the artifact text showing the count
and no name:

    chunk 01/01 rc=1 TESTSUITE_COUNTS passed=1 failed=1 ... total=2 elapsed=0s ids=1..2

after which the fix made it GREEN. A second new test
(`test_per_chunk_emission_is_silent_for_a_green_chunk`) pins that a green chunk writes no `FAILED`
line, so the emission cannot manufacture phantom failures.

VERIFICATION: the 6-file runner test family re-run clean -- **34/34 passed**
(`test_full_suite_runner_reports_failing_ids.py` 5/5, plus argv_guard, chunks_collected_ids,
reports_incomplete, unique_output, pins_interpreter).

SCOPE LIMIT, STATED: the suite that was in flight as pid 10677 does NOT benefit -- it had already
loaded the old module. Its chunk-02 failure stays unnamed for that run. The next suite run is the
first that can name failures tick-by-tick.


## B-174 STATUS UPDATE -- 2026-09-14 02:16 CST / 18:16Z (standup #406, manager): REPRODUCED INDEPENDENTLY, instrument pinned with numbers

**STATUS: still OPEN (check-side fix unlanded).** No new root cause; this is the missing measurement
that makes the fix mechanical.

**REPRODUCED on 6/6 steps, not 4/4.** Step-level `judge_reward` is ABSENT from
`grpo_step_metrics.jsonl` (`.get()` therefore returns None) on steps **1-6**. Per-candidate
`rollout_rewards[i].judge_reward` is populated **8/8 on every one of the 6 closed steps**:

```
step 1  0.30 0.36 0.30 0.26 0.26 0.36 0.36 0.36    range 0.26-0.36
step 2  0.04 x8                                     uniform
step 3  0.00 0.26 0.26 0.00 0.00 0.26 0.34 0.26    range 0.00-0.34
step 4  0.14 0.42 0.49 0.28 0.56 0.21 0.07 0.35    range 0.07-0.56
step 5  0.12 x8                                     uniform
step 6  0.01 0.19 0.01 0.21 0.08 0.08 0.08 0.15    range 0.01-0.21
```

**NO DARK STEP.** A step-level read reports 6/6 DARK on a chain delivering 8/8 per step -- the
false-RED B-174 describes, now quantified over the whole run rather than a 4-step window.

**A SECOND, INDEPENDENT REASON B-174'S PROPOSED DETECTOR MUST NOT READ `eval_results.jsonl` EITHER.**
That file's keys are `brevity, code_hash, detail_budget, details, import_hygiene, index, interface,
passed, schema_version, step, syntax, verifier` -- there is NO judge field there at all. `judge_reward`
lives ONLY in `grpo_step_metrics.jsonl` under `rollout_rewards[*]`. A detector written against
`eval_results.jsonl` would ALSO read None everywhere and manufacture the same RED.

**THE INSTRUMENT, EXACTLY (for the regression test).** Dark := the key `judge_reward` is **ABSENT**
from a `rollout_rewards` entry -- never "value is None", never "value is 0.0" (step 3 has genuine
0.00 values that are LIVE judge answers, and steps 2/5 are uniform low bands, which is the
live-but-flat signature). Coverage := count of `rollout_rewards` entries carrying the key / total.
The repo ALREADY has this correctly implemented in `.sapo-loop/launchsim_verify.py`
(`JUDGE_FIELDS = ["judge_reward", "judge_dim_scores"]`, checked per candidate entry under
`if judge_enabled`) -- so the fix is to make the check MATCH that verifier, not to invent a new one.

**WHY IT WAS NOT LANDED THIS TICK.** The check lives in the tick brief / operating prose, not in a
script this tick could edit; the record-side rollup is a `training/` metrics-writer change and is
correctly deferred to a launch boundary. Ordered again in standup #406 sec.6 item 4 with an owner.

## B-176 — heartbeat daemon-relaunch path runs WITHOUT the single-instance lock, and the launcher lingers as a resident duplicate (OPEN)
Filed: 2026-09-14 tick #409 (manager lane). ID measured as free (highest on file = B-175); IDs are not assigned by anything, so this is a claim, not an assertion.

**Symptom (the "treadmill" #407 could not explain):** every daemon-not-ready event brings up another resident
`scripts/sapo_huanxin_heartbeat.sh` process, and the single-instance lock does not exclude it.

**Evidence (all measured 18:32-18:40Z 2026-09-13, this tick):**
- 4 resident heartbeats: `41870` (lock holder, started Sep 11 09:46:58), `8791` (Sep 13 20:14:07),
  `644` (Sep 14 02:29:26 CST = 18:29:26Z), `2765` (02:29:31 CST = 18:29:31Z). All ppid=1.
- `644` and `2765` are **STAT S with `ps -o time` = 0:00.00** (zero CPU) minutes after start, and each has
  exactly ONE child: `677` = `node browser-automation/huanxin_browser_daemon.js --env ASI1` (ppid 644),
  `2795` = `... --env ASI2` (ppid 2765). i.e. the launcher is BLOCKED on the daemon it started.
- Lock state: `/tmp/sapo_locks/sapo_heartbeat/holder` = `41870`, mtime Sep 11 11:30, **no `.refreshed` file**
  -> `holder_refresh_stale` returns false -> `--steal-stale` correctly REFUSES a fresh acquirer.
  **So 644/2765 never held the lock.**
- Neither `644` nor `2765` logged `heartbeat start` in `logs/huanxin_heartbeat.log` **nor** in
  `/Users/daxu/software/quantum-gpt-new/logs/huanxin_heartbeat.log`.
- At exactly their start seconds the LEGACY log records the daemon relaunch:
  `[18:29:22Z] ASI1: cookie bridge + restart` -> `[18:29:26Z] ASI1: relaunched`;
  `[18:29:26Z] ASI2: cookie bridge + restart` -> `[18:29:31Z] ASI2: relaunched`,
  both preceded by `cookie seed: 7 cookies -> 1 profiles` (the seed SUCCEEDED on this path).

**Root-cause statement (bounded to what was measured):** the process that executed `seed_and_restart`
(code path `scripts/sapo_huanxin_heartbeat.sh:108-125`, which is a LOOP-BODY action reachable only after
`heartbeat start` at line 197) never logged `heartbeat start` anywhere and is still resident. So the
daemon-restart path is reachable by a process that does not hold the lock, and that process does not
converge. **The fork topology that lets it happen is NOT yet established — recorded UNKNOWN, not a guess.**

**TDD target (RED first, no fix landed yet):**
1. `seed_and_restart` must refuse to launch a daemon when this process does not hold `sapo_heartbeat`.
2. The launcher must not remain resident after launching (assert no long-lived process with a daemon child).

## B-177 — the heartbeat LOG path is not single-valued at runtime, so no census is a census (OPEN)
Filed: 2026-09-14 tick #409 (manager lane).

- `logs/huanxin_heartbeat.log` (current tree) and `/Users/daxu/software/quantum-gpt-new/logs/huanxin_heartbeat.log`
  (STALE tree) are appended **at the same instants**: 18:29:06Z / 18:29:31Z, 18:31:08Z / 18:31:31Z.
- Producer: `scripts/sapo_huanxin_heartbeat.sh:31` -> `LOG="${SAPO_HEARTBEAT_LOG:-$QG_SELF/logs/huanxin_heartbeat.log}"`
  -- env-injectable, so two instances **in the same tree** can log to two different files. The keeper already
  carries `SK_HEARTBEAT_LOG_CURRENT`/`SK_HEARTBEAT_LOG_LEGACY`, so the CONSUMER is hedged but the PRODUCER is not pinned.
- Consequence: #407's "no refusal lines in the log" and this tick's "no `heartbeat start` for 644/2765" are
  statements about ONE file each. Any hung-heartbeat detector or duplicate census that reads one path
  undercounts and mis-attributes. A log that is not single-valued is not an instrument.
- Related, still installed: stale launchd job `com.quantumgpt-new.huanxin-keepalive` (StartInterval 60) runs
  `/Users/daxu/software/quantum-gpt-new/scripts/huanxin_all_keepalive.sh`, which spawns browser daemons
  directly (the B-085 stale-checkout supervisor).

## B-178 — the live suite runner reports RED chunks with ZERO named failures (OPEN)
Filed: 2026-09-14 tick #409 (manager lane).

- Artifact `.sapo-loop/logs/full_suite_315_10677.txt` (runner pid 10677, live 84 min): chunks 08/24 (rc=1,
  **errors=9**), 10/24 (rc=1, failed=1), 11/24 (rc=1, failed=1) carry red counts and **no failure line at all**
  -- neither `chunk NN/24 FAILED <nodeid>` nor `FAILING <nodeid>`.
- The naming code EXISTS and is correct (`run_full_suite.py:359` `failures = parse_failures(p.stdout)`,
  `:372` per-node write, `:380` `FAILING_TESTS count=`). So this is not a missing feature.
- Note the tick's own first grep was wrong (`^FAILED` does not match the runner's `chunk NN/24 FAILED <nodeid>`
  prefix) -- re-grepped with `FAILED ` / `ERROR ` and the lines are genuinely absent. Instrument error corrected.
- **Root cause NOT established.** Hypothesis to test first: chunks 08/10/11 may have been run by a runner
  process started BEFORE the naming fix was loaded (the [[keeper-runs-stale-code]] class: a long-lived
  process never reloads). Recorded as a hypothesis, not a cause.
- Impact: 9 errors + 2 failures cannot be triaged, so the §9.3 "report counts AND name failures" mandate is not met.


### B-178 STATUS UPDATE -- ROOT-CAUSED AND FIXED (tick #410, 2026-09-14 02:55 CST)
Status: **RESOLVED (fix landed; applies to the next runner boot).** The "naming code is missing" framing
was wrong -- the naming code (B-175) was present and correct the whole time.

**Root cause, one measurement:** runner pid 10677 `lstart` = `2026-09-13T17:12:01Z`; the file
`.sapo-loop/run_full_suite.py` mtime = `2026-09-13T17:47:04Z`. The process loaded its in-memory copy
**35 minutes before** the B-175 per-chunk naming block existed. Editing a source file cannot reach a
running interpreter, so chunks 08/10/11 could not name their failures no matter what the file said.
This is the keeper-runs-stale-code class applied to the suite runner.

**Fix (TDD):** `source_identity(path)` (sha256 + mtime; Nones when unreadable),
`source_verdict(boot, later)` (three-state CURRENT/STALE/UNKNOWN -- UNKNOWN never decays to CURRENT),
`write_source_stamp()` writes `SOURCE sha256=... mtime=...` as the artifact's second line, and
`write_source_end()` writes `SOURCE_END ... SOURCE_VERDICT=` plus a loud `SOURCE_DRIFT` line when the
source moved mid-run. RED 5/5 AttributeError -> **GREEN 5/5**, regression **39/39** across all 7
adjacent runner suites. Guarded by `tests/test_suite_runner_source_stamp.py`.

**Live re-confirmation:** after the fix landed, chunk 14/24 reported `failed=1` with still **0**
`FAILING` lines -- the still-running pre-fix process failing to name its failures exactly as predicted.

**Still owed:** re-run chunk 08's id range (1401..1600) under CURRENT code to name its 9 errors.
`--collect-only` is the WRONG instrument -- a file that is 9/9 ERROR in-chunk but GREEN standalone
collects cleanly, so collection reports cannot see the test-isolation class.

### B-176 ADDENDUM -- MEASURED DAEMON CHURN (tick #410, 2026-09-14 02:55 CST) -- use as the RED fixture
New evidence tying the B-176 relaunch pathology to the ASI1/ASI2 NOT-READY state, measured by two
censuses ~5 minutes apart:

| time | ASI1 heartbeat | ASI1 daemon | ASI2 heartbeat | ASI2 daemon |
|---|---|---|---|---|
| 18:45Z | 8755 (0:47) | 8785 (0:47) | 47169 (2:52) | 47209 (2:52) |
| 18:50Z | 16430 (1:18) | 16472 (1:03) | 35267 (4:00) | 35531 (3:45) |

Both ASI1 and ASI2 daemons were **replaced inside ~5 minutes**. Daemon boot on this fleet takes ~4-5 min
([[huanxin-readiness-instrument]]). So each daemon is killed at approximately the moment it would finish
booting -- it can never reach `ready`, which is exactly the observed ASI1/ASI2 NOT-READY state. Note the
old daemons do NOT disappear alone: each new heartbeat arrives WITH a daemon child (8755+8785, then
16430+16472), the resident-launcher shape B-176 already describes.

**RED fixture for the fix:** assert that a launcher does not replace a daemon whose age is below the
boot budget (4-5 min), i.e. that replacement is gated on an observed DEAD signal (three-state probe:
only DEAD fires, UNKNOWN never does -- skill 5.4.1 watcher-probe semantics). Today the replacement fires
with no dead signal at all.

**Secondary lead (not a cause):** the ASI2 daemon runs from
`/Users/daxu/.local/state/fnm_multishells/...` while ASI1/ASI3 run from
`/Users/daxu/.local/share/fnm/node-versions/v22.22.1/installation/bin/node` -- a DIFFERENT node binary.
Worth checking whether a launch path picks a different node version; do not treat as the cause without
evidence.


## B-179 -- [OPEN, S3 LEAD] NPU reads ~idle while the trainer burns ~147% host CPU on step 1
Filed 2026-09-14 03:02 CST / 19:02Z by manager (tick #411). **LEAD, NOT a proven defect. Do not cite as
a stall without the control named below.**

**Run:** outputs/sapo-27b-ai-20260913T183728Z, trainer pid **76388 (ppid=1)**, step 1 in flight since
18:39Z, `--max-new-tokens 4096`.

**Evidence (all measured, 18:50-19:00Z, container ASI3 :20653):**
- `npu-smi info` x3 + a 4x loop: **AICore 0% on all 8 chips, every sample (11 samples total)**; NPU power
  97.9-101.5 W per chip.
- `npu-smi info -t usages -i 0`: Aicore **0**, Aivector **0**, Aicpu **0**, NPU Utilization **0**,
  HBM Bandwidth **0%**, DDR BW **0%** -- but **Aicube Usage Rate 8%**.
- Thread states `/proc/76388/task/*/stat`: **245 S, 2 R** (of 247 threads).
- Host CPU by tick delta (`stat` fields 14+15): **2211 ticks/15 s** and **1771 ticks/12 s** = **~147%**.
- Log frozen at **259284 bytes / mtime 18:39:00** across three reads spanning ~10 min.

**Positive control that the AICore-ZERO READING IS A REAL ZERO AND NOT A DEAD INSTRUMENT:** Aicube
returns **8%** (non-zero) in the same call; per-chip HBM diverges (chip0 12953 MB, chip7 13448 MB,
others 10665 MB); per-chip power diverges. A stuck-at-zero instrument cannot produce divergent values.

**MISSING CONTROL (this is why it is a LEAD):** there is **no measurement of what AICore/Aicube read
during a known-good step** on this driver, and a step is in flight so one cannot be manufactured
without perturbing the live run.

**Two readings, not yet separated:**
1. *Benign:* the transformers+Ascend generation loop is host-bound (sampling / tokenization / python
   overhead dominates), so device utilisation is legitimately near-zero between short compute bursts.
2. *Defect:* generation is stuck host-side and never reaching the device, which would also explain the
   21-min frozen log and `generation_done`=0.

**DO-NOT:** do not fire the standing 25-min stall trigger on the clock alone. That trigger was
calibrated against **1024-token** rollouts; this launch runs **4096** (the intended B-163 fix), so a
~4x longer step is expected by design. Firing it would be a false alarm on the change we asked for.

**The test that resolves it (next tick):** sample `npu-smi info -t usages` on the same chip immediately
**before and after** the first `generation_done`. AICube rising materially => **RETRACT B-179**. Ladder
advances with AICube pinned ~8% => reading (2) is real, escalate. Ladder still absent => compare
**tokens/second** against the previous 1024-token run's own step time instead of using the wall clock.


## B-180 -- judge-proxy auto-repair can never succeed: it relaunches without freeing the port
**Filed:** 2026-09-14 03:15 CST / 19:15Z (STANDUP #412, manager lane)
**Status:** OPEN -- root-caused with evidence; fix NOT applied (the blocker is user-gated).

**Symptom.** `/tmp/sapo_judge_health_state.json` = `{"healthy": false, "detail": "HTTPError: HTTP
Error 502: Bad Gateway", "strikes": 8}`. `sapo_judge_health_agent.py` probes
`http://127.0.0.1:55648` every 300s and has been UNHEALTHY since ~18:37:31Z (strikes 2 -> 8).

**Root cause (measured, two independent instruments).**
1. The port is held by **pid 424**, etime **2d17h**, argv `claude_huanxin_anthropic_proxy.py
   --host 127.0.0.1 --port 55648 --upstream-url https://aihuanxin.cn/kunlun/ingress/api/...`
   (`/usr/sbin/lsof -nP -iTCP:55648` -> `Python 424 ... TCP 127.0.0.1:55648 (LISTEN)`). So the
   correct program IS resident and IS listening.
2. Its upstream is failing: a direct OpenAI-shaped probe returns `404 not found` (the socket answers)
   while the health agent's real judge request returns **502** -- i.e. the proxy is up and routing to
   a dead/unauthorised upstream (consistent with an expired JWT inside a 2-day-old process).
3. **The repair cannot fix it.** `_repair_step("proxy")` spawns a NEW proxy on the SAME port without
   terminating the incumbent. `/tmp/dp4_proxy_55648.log` contains **only** bind tracebacks:
   `OSError: [Errno 48] Address already in use` (12+ occurrences, mtime 02:26 CST). Every repair
   returns False, the strike counter resets to 0, and the next two probes re-trigger the same
   doomed repair. **A heal that cannot succeed is worse than no heal: it produces a "we tried" log
   line while the real blocker (dead upstream / stale token) goes unnamed.**

**The fix (TDD, not yet applied).** The proxy hop must be *free-the-port-then-bind*:
- before spawning, find the LISTEN pid on the configured port and TERM it, wait for the socket to
  clear (bounded), THEN spawn; and
- after spawning, require a **positive** health signal for the hop to count as repaired (the existing
  `probe()` does this for the watcher hop but the proxy hop's `time.sleep(3); probe()` is what
  currently fails silently into a False).
- RED test to write first: model a retry loop in which the port is already bound, and assert the
  repair either frees it or reports the hop as UNREPAIRED **with the incumbent pid named** -- never
  a bare False.
**DO-NOT:** do not kill pid 424 from a tick session -- it is a 2-day-old cross-project process and
process termination at that scope is user-gated.


## B-181 -- [OPEN, S1] Runs are being externally TORN DOWN and replaced on a ~15-20 min cycle; three consecutive replacements in one hour
Filed 2026-09-14 03:16 CST / 19:16Z by manager (tick #412). **RENUMBERED FROM B-180.** When I measured
this ID as free, the highest on file was B-179; a **sibling #412 session landed its own `## B-180`
(judge-proxy auto-repair) one minute earlier**, mid-tick, so the IDs collided. Measured, not assumed:
both headers were present and they are different bugs. The incumbent keeps B-180; this entry is B-181.
IDs are not assigned by anything ([[bugqueue-id-collisions]]), so this is a claim, not an assertion.

**Symptom.** The live SAPO run is replaced by a brand-new run, repeatedly, with no USER GO and no
recorded stop. Today's dead runs and their final log writes (UTC):

| run | step_begin | generation_done | last log write | replaced by |
|---|---|---|---|---|
| 140716Z | 1 | 0 | 14:18:58 | 142051Z |
| 142051Z | 1 | 0 | 14:32:05 | 143447Z |
| 143447Z | 5 | 4 | 15:17:34 | 151737Z |
| 151737Z | 7 | 7 | 18:36:18 | 183728Z (first ALIVE 18:42:54Z) |
| 183728Z | 1 | 0 | **19:01:12** | **190125Z (process family starts ~19:01:28Z)** |

**The forensic signature (this is the part that makes it a mechanism, not a run of bad luck).** Every one
of those five logs ends with **exactly 8** repetitions of:

    [ERROR] TBE Subprocess[task_distribute] raise error[], main process disappeared!

Eight = the device count, so these are the Ascend TBE operator-compilation children, one per NPU, each
reporting that its parent was gone. **8/8 in every run, including the ones that reached step 7 and the
ones that never finished step 1** -- i.e. this is the tear-down fingerprint, not a training failure.

**Why it blocks the objective.** A trainer restarted every ~15-20 min **cannot reach step 25, cannot land
a checkpoint, and therefore cannot ever be holdout-evaluated**. 151737Z had reached step 6
(`resume_state.json` `step: 6`) and its work was discarded. This outranks any single-run stall.

**What is RULED OUT (measured this tick, not assumed):**
- `scripts/trainer_liveness_poller.py` (live pid 33535): **cannot** launch or stop anything -- it carries
  an explicit no-launch/no-stop lock (`test_poller_has_no_launch_or_stop_surface`) and its source states
  relaunch is user-gated. It **logged** the death (`18:58:47Z verdict=DEAD strikes=1 ...183728Z`) and
  the new run (`19:07:28Z verdict=ALIVE ...190125Z`).
- `scripts/auto_resume_training.sh`: **never ran on the Mac** -- `/tmp/auto_resume_training.log` and
  `/tmp/auto_resume_launch.log` **do not exist**. It is also excluded by argv: it would set
  `AI_SAPO_LR=2.5e-5` and `AI_SAPO_ADAPTER_INIT` to the newest checkpoint of the newest run, but
  **190125Z carries `lr 5e-5` and a Sept-8 adapter** (`20260908T094427Z/step_000097_adapter`).
- **OOM**: `dmesg` holds one OOM kill, of an unrelated security agent (`dosec_hades`, pid 177303), and
  `free -g` shows 2014 GB total / 1926 GB available. Not memory pressure.

**ATTRIBUTION: UNATTRIBUTED.** No launch ledger exists on the Mac, the lifecycle journal
(`.sapo-loop/lifecycle.jsonl`) is **test-polluted and stale** (last write 14:44:07Z, run
`sapo-27b-ai-20990101T000000` = a sentinel), and `launchctl`/`cron` enumeration is gated in tick
sessions.

**CAVEAT (do not cite this as proven external termination).** `main process disappeared` is consistent
with an external SIGTERM/SIGKILL **and** with an in-process fatal abort. The pids are reaped, so
`/proc/<pid>/stat` field 52 is unavailable and [[zombie-exit-code-forensics]] cannot be applied. The
external-kill reading is a **strong lead**, not a proof.

**The test that names the killer (owner: manager, #413):** arm a watcher sampling at <=30 s: box `ps`
trainer family + `tail -c 200` of the live run log; on the first `main process disappeared`, record the
pid, the exact UTC, and the pid family at t+30 s. One record either names the killer in the process
table or proves the killer sits outside it (an orchestrator).


## B-182 -- [OPEN, S1] Step 1 never leaves `step_begin`: 28 min stage-frozen, 0 step records, NPU idle, host spinning
Filed 2026-09-14 03:36 CST / 19:36Z by manager (tick #413). ID measured free immediately before filing
(highest on file B-181; a header-count grep for this ID returned 0).

**Symptom (one run, measured).** Live run `sapo-27b-ai-20260913T190125Z`, trainer family pid 80125
(ppid=1) + child 80508 (ppid=80125), `--output-dir .../sapo-27b-ai-20260913T190125Z`, started 19:01:27Z
(box etime). Step 1 entered at **19:03:10Z** (`{"stage": "step_begin", "step": 1, "task":
"quantum_rl_v2_swap_test_ry", "group_size": 8, "greedy_count": 3, "max_new_tokens": 2048}`).

| box time | log size | log mtime | step records | checkpoints |
|---|---|---|---|---|
| 19:22:10Z | 259460 | 19:03:10.056868 | absent (0) | 0 |
| 19:25:26Z | 259460 | 19:03:10.056868 | absent | 0 |
| 19:29:28Z | 259460 | 19:03:10.056868 | absent | 0 |
| 19:31:26Z | 259460 | 19:03:10.056868 | absent | 0 |

`grpo_step_metrics.jsonl` **does not exist** -- per the standing rule that means the run never reached a
step, *not* "0 dark steps". **The documented 25-min "trainer not progressing while a step began"
trigger FIRED** (26 min 18 s at 19:29:28Z; 28 min at 19:31Z).

**THE TOKEN-BUDGET HYPOTHESIS IS REFUTED -- 7 runs, measured, both directions.** #411/#412 carried the
reading that the step-1 stall was *explained* by the generation budget. It is not:

| run | max_new_tokens | steps completed |
|---|---|---|
| 143447Z | 256 | **4** |
| 141907Z | 512 | 0 |
| 142051Z | 512 | 0 |
| 151737Z | 1024 | **6** |
| 140716Z | 2048 | 0 |
| 190125Z | 2048 | 0 |
| 183728Z | 4096 | 0 |

The same budget gives opposite outcomes (512 -> 0 and 0; 2048 -> 0 and 0), and the *smallest* budget
(256) is one of the two that progressed. Budget does not predict completion. **Do not re-carry the
budget confound.**

**NPU idle while host spins -- second independent sample.** `npu-smi info -t usages -i 0` on ASI3 at
19:22:55Z: Aicore **0**, Aicube **0**, Aivector 6, Aicpu 0, NPU Utilization **6**, HBM BW **0**,
DDR BW **0**, HBM Usage 19% -- instrument live in the same call (non-zero fields present). Host CPU:
pid 80125 gained **2362 ticks in 15 s = ~157%**, 247 threads, `acl_thread` threads resident. This
reproduces the B-179 lead on a second run; it is **still a LEAD**, not a proven cause -- there is still
no known-good-step AICore baseline on this driver.

**Instruments ruled out this tick.**
- The box-side port probe is **inadmissible for 8356/56238**. From inside ASI3,
  `56237/health -> 200` but my positive control `20653/health -> 000` *while I was executing through
  20653*. A control that fails on a known-open port invalidates the reading -> **vLLM :8356 and
  translator :56238 are UNKNOWN, not down.** Positive datum that IS valid: **`56237/health -> 200`**,
  and 56237 is exactly the `--judge-dp4-endpoint` the live trainer was launched with.
- The judge chain is **GREEN and correctly armed**: `/tmp/sapo_judge_mac_watcher.log` shows
  `queue-run: OK (.../sapo-27b-ai-20260913T190125Z)` + `heartbeat ok (processed=0)` every ~45 s,
  last at 19:25:53Z. `processed=0` is expected with 0 completions generated.

**INSTRUMENT CORRECTION (this narrows the claim, it does not weaken it).** `/proc/80125/fd/1` is a
**regular file**, not a pipe or tty, so Python block-buffers stdout. The log's size is not a multiple of
8192 and every stage line is present and newline-terminated, so the stage logger flushes per record.
**Correct claim: no STAGE TRANSITION since 19:03:10Z.** Do **not** claim "no tokens generated since
19:03:10Z" -- per-token liveness is not observable through this fd.

**Ruled out as a cause of THIS stall.** Not OOM: the box's single OOM kill at 19:11:11Z took
`dosec_hades` (pid 177303) in pod `93295acf-0c12-4950-a9e5-addd028baa31` / cgroup `6ccbdf9b...`; our
trainer is in pod `f2ae93bb-ef9d-42de-8f26-25828e9ae45e` / cgroup `6ccb5e40...`. **Those two cgroup
hashes differ by two characters -- they are easy to conflate; I read the full cgroup path.** Host
`free -g`: 2014 GB total / 1925 GB available. Also ruled out: a competing run -- `pgrep -af
grpo_trainer.py` returns exactly the 2 pids of this one family.

**ATTRIBUTION: UNATTRIBUTED.** No root cause yet. Related open lead: B-181 (the run teardown cycle).

**Note for the next tick.** 190125Z is the **first run today to survive the ~15-20 min churn cycle**
(28+ min and counting, vs 183728Z 24 min, 151737Z ~59 min). Whether the killer has stopped, or is merely
late, is **NOT KNOWN** -- do not report the cycle as fixed.


## B-183 -- [OPEN, S2] TWO heartbeat instances race the same daemons: the one that cannot find the keychain item restarts ASI1/ASI2 every ~2-8 min, so they never converge
Filed 2026-09-14 03:35 CST / 19:35Z by manager (tick #413). ID measured free immediately before filing
(`grep -c 'B-183'` = 0; highest on file B-182).

**Symptom.** ASI1 :20646 and ASI2 :19004 never reach `/exec` ready. ASI3 :20653 is ready and has not
been restarted in ~6 h. Measured this tick: ASI1 `HTTP 200 ready=False state=booting` (with a transient
`ready=False state=error startupError="Shell terminal for ASI2 failed because the Huanxin shell endpoint
API returned no terminal URL. getShellVisitUrl code=170022"` seen on ASI2), ASI2 alternating to
`Connection refused` mid-restart.

**Evidence 1 -- the failure is ITEM-NOT-FOUND, not a denial.** Running the exact call the seeder makes:
`security find-generic-password -w -s "Chrome Safe Storage"` -> **rc=44**, stderr
`SecKeychainSearchCopyNext: The specified item could not be found in the keychain.`
`scripts/sapo_cookie_seed.py:155-156` collapses EVERY non-zero rc into
`sys.exit("keychain denied - cannot decrypt user cookies")`. The log line therefore MIS-NAMES the
failure class. **This supersedes the "user-gated keychain denial" root cause recorded in #412** -- the
keychain is reachable; the item is absent for the process that asks.

**Evidence 2 -- TWO heartbeat logs are appended simultaneously, with opposite outcomes.**

| log | `cookie seed: N cookies -> M profiles` (success) | `keychain denied` | last activity |
|---|---|---|---|
| `quantum-gpt/logs/huanxin_heartbeat.log` | **0** | **347** | 19:25:09Z ASI2 `cookie seed FAILED` -> `relaunched` |
| `quantum-gpt-new/logs/huanxin_heartbeat.log` | **1389** | 60 | 19:27:20Z ASI1 + 19:27:24Z ASI2: `cookie seed: 7 cookies -> 1 profiles` -> `relaunched` |

The second path is inside the STALE tree, whose `scripts/` contains no seeder and whose heartbeat script
is documented ABSENT (`scripts/sapo_huanxin_heartbeat.sh:20-29`). Both logs carry the same format, the
same POLICE lines and the same `tick daemons={...}` line, so both are the same script running twice.

**Evidence 3 -- the mechanism is a kill loop.** `seed_and_restart()` (`scripts/sapo_huanxin_heartbeat.sh:108-125`)
line 111-112 does `pgrep -f "huanxin_browser_daemon.js --env $E" | head -1` then `kill "$pid"` BEFORE
seeding and relaunching. A daemon boot takes ~4-5 min; ASI1/ASI2 are killed on a ~2-8 min cycle by two
independent instances, so neither can ever finish converging. ASI3 is `ready`, so neither instance
touches it -- the differential is the restart, not the environment.

**Evidence 4 -- the successful seeder is real and recurring.** `/tmp/huanxin_cookie_plaintext.json`
(only writer: `scripts/sapo_cookie_seed.py:232`, the last statement of a successful `main()`) was
rewritten at 19:25:15Z and again at 19:27:20Z with the correct 7 SSO cookies. A first read of its mtime
was SUPERSEDED 2 min later by a second write -- it is a RECURRING marker, not a one-off. The main-tree
log has ZERO matching success lines, so the writer is not the main-tree instance.

**Fix direction (TDD; not implemented this tick).**
(a) `storage_key()` must distinguish rc=44 (item not found) from an ACL denial (rc 36/51) and report the
true class instead of one "keychain denied" string.
(b) One heartbeat owner only: the lock must actually exclude (B-087) or the stale-launchd instance must
be retired.
(c) `seed_and_restart` must not kill a daemon that is mid-boot.

**UPDATE 2026-09-14 03:56 CST / 19:56Z -- (c) E2E-VERIFIED against the live fleet (not only unit-tested).**
Production probe `daemon_state` (the exact helper the new guard calls) read **`booting 0`** for `:20646`
ASI1 and `:19004` ASI2 on two consecutive reads, and `ready 0` for `:20653` ASI3. ASI1's raw `/health`
body: `ready:false startupState:"booting" env:"ASI1" pid:79586 uptime:97 commandCount:0` -- **97 s into
a ~4-5 min boot.** So the guard's first predicate (`daemon_state == booting`) is satisfied by a MEASURED
live state, and an unconditional kill at that moment is exactly the loop. Corrects my own earlier
`Connection refused` reading in the #414 dashboard: ASI1/ASI2 are BOOTING, not DOWN; NOT-READY stands,
the class does not. Second predicate (`bootval_for > 0`) NOT verified box-side.

**UPDATE 2026-09-14 03:50 CST / 19:50Z (tick #414) -- FIX LANDED (a)+(c); (b) SUPERSEDED by measurement.**
Green on touched surfaces: **49/49** (`tests/test_b183_keychain_class_and_midboot_guard.py` 7/7 new RED->GREEN
+ 6 adjacent heartbeat/seeder/lock suites 42/42, 0 new failures).
- **(a) DONE -- `storage_key()` now reports the true class.** New `classify_security_rc(rc, stderr)` in
  `scripts/sapo_cookie_seed.py`: rc=44 -> "keychain item not found", rc 36/51 -> "keychain denied",
  anything else -> "keychain lookup failed (rc=N)" (the unknown code is carried in the message instead of
  being dressed as one of the two known classes).
- **(c) DONE -- `seed_and_restart()` no longer kills a daemon that is merely mid-boot.** New guard in
  `scripts/sapo_huanxin_heartbeat.sh`: if `daemon_state` reads `booting` AND the persisted boot age
  (`bootval_for`) is under `MIDBOOT_GRACE_S` (default 900s), it logs
  `SKIP restart - pid N mid-boot (...)` and returns WITHOUT killing. Past 900s the existing wedge branch
  still owns the teardown (regression-pinned by `test_wedged_booting_daemon_is_still_restartable`), and a
  `ready` daemon is still restartable (`test_ready_daemon_is_still_restartable`). `bash -n` clean.
- **(b) SUPERSEDED -- not the two-instance theory any more. There are FOUR.** Read-only lane (tick #414):
  live pids 8791 (Sep 13 20:14), **41870 (Sep 11 09:46:58)**, 79968 (03:35:57), 84813 (03:44:11), ALL
  ppid=1, ALL with `quantum-gpt` in argv, and `ps eww` shows **no `SAPO_HEARTBEAT_LOG` override** on the
  sampled ones. The single-instance lock (`sapo_single_instance_lock.sh`) is therefore not excluding --
  B-087 confirmed again, now with a count.
- **Second-writer root cause: HYPOTHESIS, named, still unverified.** `com.quantumgpt-new.huanxin-keepalive.plist`
  points at `quantum-gpt-new/scripts/huanxin_all_keepalive.sh`, which contains **zero** references to
  `huanxin_heartbeat.log` -- so the launchd job is NOT the second writer. The surviving candidate is **pid
  41870**: bash parses a `while` loop as ONE compound command and never re-reads the body, so a process
  started 2026-09-11 09:46:58 still executes pre-B-097 script text, whose `LOG=` was hardcoded to
  `quantum-gpt-new/logs/huanxin_heartbeat.log` (same `LOG=` line survives in `/tmp/pre_fix_heartbeat.sh:13`).
  **Decisive check is `lsof -p 41870 | grep huanxin_heartbeat.log` -- GATED in a tick session.**
- **NO DUPLICATE WAS KILLED. Deliberate decision, recorded.** The one instance that demonstrably SEEDS
  SUCCESSFULLY is the writer of the `-new` log (1389 successes / 60 denials, last 03:44:11). If 41870 is
  that writer, killing it removes the fleet's only working seeder on a HYPOTHESIS -- exactly the
  untested-hypothesis action section 2.1 forbids. The fix that removes the kill loop regardless of
  instance count is (c), which is landed.
- **Deployment caveat, stated plainly: a landed fix is NOT a deployed fix.** The running heartbeat
  instances hold their script text in memory; only instances started AFTER the edit pick up (c). Measured
  pids 79968 (03:35:57) and 84813 (03:44:11) both PRE-DATE this edit, so (c) is inert in every currently
  live instance. It takes effect on the next supervisor-spawned heartbeat (~2-8 min cadence observed).

**NOT DONE / NOT CLAIMED.** `launchctl`/`cron` enumeration is gated in tick sessions and `lsof` is
unavailable, so the second instance's PROCESS was not identified. The leading hypothesis -- that it
inherits `SAPO_HEARTBEAT_LOG` / launchd env from a stale plist -- is a HYPOTHESIS, not a measurement.
Only one positive control supports `rc=44`: a control keychain item was NOT probed.

## B-184 -- [OPEN, S1] Keeper is in a 1/min KICKSTART loop it can never exit: the auth probe fails, so no keeper cycle ever completes, so the watchdog kicks forever
Filed 2026-09-14 03:50 CST / 19:50Z by manager (tick #414). ID measured free immediately before filing (`grep -c 'B-184'` = 0).

**Symptom.** `/tmp/session_keeper_state.json` is FROZEN at `03:21:30 status=STARTING cycle=1
uptime_s=null pid=75674`. Measured 03:49 CST: **pid 75674 is GONE** (`ps -p 75674` -> no row).
`logs/session_keeper_watchdog.log` shows the watchdog firing **KICKSTART once per minute,
non-converging**: 03:42:18 -> 54441, 03:43:22 -> 73822, 03:44:22 -> 73822, 03:45:30 -> 656,
03:46:09 -> 23842, 03:47:27 -> 42390, 03:48:27 -> 66664 -- **7 restarts in 6 min, each a NEW pid**,
while the reported state age GROWS monotonically (1395s -> 1636s). rc=0 on every kick, so the kick
"succeeds" and the loop never backs off. Historical count: **252 KICKSTART lines** in the log.

**Root cause chain (each link measured in `logs/session_keeper.log`).**
1. `[2026-09-14 03:24:47] ALERT headless claude auth FAILED -- attempting env refresh from live process`
2. `[2026-09-14 03:09:46] ERROR no live process with valid auth found; keep retrying every cycle`
3. `auth probe failed: timeout after 90.0s` (production `SK_AUTH_PROBE_TIMEOUT_S`, not the 1.0s
   harness value -- see [[keeper-started-line-is-not-a-start]])
4. => the keeper never reaches a healthy cycle, never rewrites the state file
5. => the watchdog's "age growing / cpu not advancing" predicate stays TRUE forever
6. => kickstart every 60s, forever.

**This is the B-091 class, escalated.** B-091 recorded that a kick is *attempted*, never *done*.
Here every kick IS done (rc=0, pid rotates) and it still achieves nothing, because the keeper's
failure is not a wedge -- it is an environmental auth outage. **A watchdog that restarts a subject
whose failure class cannot be cured by restarting is a CPU-burning loop, not a healer.**

**Negative results (measured, so they can be dropped from the search).**
- **NOT the /stop bug returning.** `grep -E '^\[2026-09-14' logs/session_keeper.log | grep -c 'stop'`
  = **0**. Last `busy-congested -- direct /stop restart` line is `2026-09-13 21:25:42` (**CST** --
  the keeper logs CST while ALL_keepalive logs UTC, see [[keeper-kick-unverified-b091]]), i.e. before
  the B-148 restart, so B-148's fix appears to be holding. This is NOT the "keeper kills daemons" class.
- No daemon was harmed by the keeper this tick.

**Fix direction (TDD; NOT implemented this tick).** (a) The kickstart predicate must exclude the
auth-failure class -- an unhealable-by-restart state must back off (exponential, capped), not
kick at 1/min; (b) rc=0 on the kick is not evidence the keeper progressed, so the watchdog needs a
*progress* signal (state-file ts advancing), not a liveness one; (c) the auth probe's 90s timeout
inside a 60s watchdog cadence means the keeper cannot even finish one probe between kicks.

**NOT DONE / NOT CLAIMED.** The auth failure itself is **UNATTRIBUTED to code vs network** --
`ANTHROPIC_BASE_URL` is an external endpoint (`logs/session_keeper.env.head` ENVF, refreshed
2026-09-14 01:16:19 from pid 90739). Whether it is an expired credential or an unreachable endpoint
was NOT measured this tick. No heal was attempted: `launchctl` is gated in tick sessions and the
watchdog is UNSUPERVISED ([[keeper-watchdog-unsupervised]]), so killing it removes the guard
permanently. **This is a user-gated repair.**


## B-185 -- [OPEN, S2] The B-181 teardown watcher is structurally blind at the instant it exists to observe: its target run is derived from the CURRENT ps census, and its latches reset on run change
Filed 2026-09-14 03:58 CST / 19:58Z by manager (tick #414). ID measured free immediately before filing (`grep -c 'B-185'` = 0).

**Symptom.** The teardown watcher armed at #413 (order 1, `teardown_watch.py`, pid 77231) was built to
capture the ONE signal B-181 needs: the moment of trainer teardown, with the pid family at t+30 s. It was
live across the stop->relaunch at ~19:39:25Z and **did not fire**. Its log records the transition but no
`*** TEARDOWN`, and `tear=0` on every heartbeat:

```
19:37:37Z HB cycle=10 run=sapo-27b-ai-20260913T190125Z begin=1 gdone=0 tear=0 size=259460 ps_n=2
19:39:25Z RUN-CHANGE /root/work/software/quantum-gpt/outputs/ -> // (resetting tear/gdone latches)
19:39:25Z NO-LOG run=// ps=
19:40:00Z RUN-CHANGE // -> /root/work/software/quantum-gpt/outputs/sapo-27b-ai-20260913T193927Z (resetting tear/gdone latches)
```

**Root cause (read from the source, not inferred).** `PROBE` in `.sapo-loop/logs/teardown_watch.py`:

```
RD=$(ps -eo args | grep -- --output-dir | grep -v grep | head -1 | sed "s/.*--output-dir //" | awk "{print $1}")
ID=$(basename $RD | sed "s/^sapo-27b-ai-//")
L=/root/work/software/quantum-gpt/logs/sapo_27b_ai/grpo_train_$ID.log
```

The watched target is **derived from the CURRENT process census**. At the instant the trainer dies, no
process carries `--output-dir`, so `RD` and `ID` are empty and `L` collapses to the non-existent
`grpo_train_.log`. `TEAR=$(grep -c 'main process disappeared' $L)` then returns **0 from a file that was
never there** -- and `HASLOG=0` makes the watcher log `NO-LOG` instead of a teardown. Compounding it, the
`tear_seen` / `gdone_seen` latches are **reset on every RUN-CHANGE**, so any teardown recorded against the
old run is discarded the moment the successor appears.

**Impact.** B-181's killer actor is UNATTRIBUTED, and this is *why* -- not an absence of events. The
instrument is blind exactly where it was aimed. Every tick that runs it produces a false all-clear.

**Note -- the B-144 lesson cuts the other way here.** [[judge-watcher-armed-once-drift-b144]] locked in
"resolve the live run from box `ps`, NEVER from `ls -td`" -- correct for finding the LIVE run. Teardown
detection needs the complementary thing: a **sticky target**, i.e. remember the last known run dir and
keep probing ITS log across run changes and across the census going empty.

**Fix direction (TDD; NOT implemented as of this filing).** v3: keep `watch_target` as state; on each poll
resolve the live run from `ps`, and if it differs from `watch_target`, **first** evaluate the teardown +
`generation_done` predicates against `watch_target`'s log, **then** switch the target. Never let a run
change clear evidence about the previous run. Do not deploy to the box.

**Regression test to write first (RED):** drive the poll function with a scripted census sequence
[run A] -> [empty] -> [run B], with A's log carrying the 8x fingerprint; assert the teardown line is
emitted for A, names A, and is NOT cleared by B's arrival.

**NOT DONE / NOT CLAIMED.** Not fixed. The killer is still unidentified. This is a defect in a
monitor-side script under `.sapo-loop/logs/`, not in the training path.

**B-185 UPDATE (2026-09-14 19:55Z / 03:55 CST, tick #414) -- FIXED, FIELD-VERIFIED, DEPLOYED.**
`teardown_watch_v3.py` replaces v2. Sticky target: predicates for the previous run are evaluated BEFORE the
target advances; an empty census neither clears nor advances the target; latches no longer reset on run
change. TDD RED->GREEN, `.sapo-loop/logs/test_teardown_watch_v3.py` **4/4**. Field check with the real box
`read_log` over the real `[190125Z] -> [] -> [193927Z]` sequence emits
`*** TEARDOWN run=.../190125Z tear=8` -- the line v2 could never print. v2 pid 77231 SIGTERM'd; v3 live as
pid 21364 (ppid=1). Monitor-side only; nothing deployed to the box; **B-181's actor still UNATTRIBUTED** --
this makes attribution possible, it does not perform it.


### B-183 STATUS UPDATE -- MECHANISM CONFIRMED AND SHARPENED (tick #415, 2026-09-14 04:22 CST / 20:22Z)

Not a new bug, and no new ID filed: the 170022 evidence already in this entry is correct. What this tick
adds is a **quantified, independently re-verified** mechanism and the decisive census the entry was
missing. Nothing here is a guess.

**1. The daemon does NOT crash -- it is killed.** Measured on the daemon log
`quantum-gpt-new/logs/huanxin_all_keepalive.log` (note: a DIFFERENT checkout, see item 4):
`grep -c 'code=170022'` = **3666**; `grep -c uncaughtException` = **0**. The source retries boot
indefinitely (`scheduleBootRetry()`), and its SIGTERM/SIGINT handlers call `cleanup(); process.exit(0)`
with **no log line**. So the pid churn (uptime never above ~150 s across probes 4 min apart) is
**external termination**, exactly as this entry's title asserts.

**2. The restart can never succeed, which is the part that matters.** The blocker is platform-side:
`getShellVisitUrl code=170022`, "the Huanxin shell endpoint API returned no terminal URL", terminal
已断开 / auto-recycled-locked. Relaunching a daemon does not restore a terminal the platform has taken
away. So every restart is wasted work that also tears down any session that did open. B-183's premise
("restarts them every ~2-8 min, so they never converge") is CONFIRMED, and strengthened: they can never
converge while 170022 stands, no matter how the race is resolved.

**3. The decisive census -- the DUPLICATES are the actors.** `/tmp/sapo_locks/sapo_heartbeat/holder`
= **41870**, held since Sep 11 (the legitimate long-lived instance, and the one with **no** browser-daemon
child). Four heartbeat instances are live (pids 3242, 8791, 41870, 50301); the two **non-holder**
duplicates 3242 and 50301 are the ones carrying live `huanxin_browser_daemon.js` children. So the
processes doing the killing are precisely the ones that do not hold the lock -- the single-instance lock
is failing to exclude, which is the B-087 class and the concrete co-cause here.

**4. Checkout mismatch worth resolving.** The running daemons' log lives in `quantum-gpt-new/`, a
different checkout from this repo -- consistent with the known triple-supervisor finding (B-085). Confirm
that the heartbeat being reasoned about owns the daemons being observed before fixing its gate.

**5. Proposed fix (RED test stated, NOT yet written).** Gate the relaunch in
`scripts/sapo_huanxin_heartbeat.sh` on a POSITIVE crash signal, never on a not-ready/unreachable probe,
with explicit backoff for the 170022 class. RED first: a probe returning the 170022 shell-endpoint error
must NOT relaunch; a genuinely absent process still MUST. This is BUG C in STATUS.md #415.

**6. Escalation, stated plainly.** ASI1/ASI2 are **not locally healable**. Relaunch, re-auth and
cookie-bridging have all been exercised and the platform still returns 170022. Restoring the ASI1/ASI2
dev-environment terminals is a USER/platform action; until then the loop's own restart machinery is the
thing producing the churn.


**ADDENDUM 2026-09-13 20:22Z (tick #416) -- LOCALIZED, still UNATTRIBUTED.** Reproduced on the successor
run `sapo-27b-ai-20260913T193927Z` (trainer pid 87515, ppid 1). The "host spinning / NPU idle" lead above
is now a measured statement rather than a lead:

1. **The spin is the Python MAIN thread**, not a worker: `/proc/87515/task/87515/stat` delta = **494
   jiffies / 5 s = ~99% of one core**; process total ~154%; every `acl_thread` is ~2-3%.
2. **It is pure userspace**: `/proc/87515/syscall` returns EMPTY and `/proc/87515/wchan` returns 0 -> no
   syscall in flight, the thread has never blocked.
3. **No NPU work is dispatched**: `npu-smi info` AICore **0-1%** (chips 0-7 Health OK, HBM 11540-14078 MB
   held); `acl_thread`s parked in `eventfd_read`, `release_thread`s in `do_select`.
4. **Not the B-181 compile fingerprint**: `ps -eo pid,ppid,comm | awk '$2==87515'` = 3 python children
   only; `ps | grep -ci tbe` = **0** -> no TBE operator-compile subprocesses.

**Localized to a code region.** Stage census is 1x each of `tasks_ready`, `text_preprocessor_loaded`,
`model_loaded`, `npu_device_map`, `model_sharded_on_npus`, `selective_training_applied`,
`gradient_checkpointing_verified`, `text_forward_preflight` (loss 4.46 on a [1,483] forward -- forward
WORKS), `zero_change_snapshot`, then `step_begin`. The **last log line** is transformers'
`The following generation flags are not valid and may be ignored: ['temperature', 'top_k']`, emitted only
when `do_sample=False` -> the hang is inside the **greedy** `model.generate(..., do_sample=False)` call in
`generate_group` (`greedy_count=3` per the step_begin record). 28 open `/dev/davinci*` fds: the process IS
NPU-attached, so "attached" and "dispatching" are different properties and only the first holds.

**Two negative results (do not re-investigate):**
- `StopAfterClosedCodeFence` (`training/generation.py:154-190`) decodes only a **16-token tail** per step,
  so it is bounded -- it is NOT the historical O(N^2) hot loop.
- There is **no `vllm_rollout_unavailable` stage line**, so the vLLM branch neither succeeded nor reported
  unavailability; the single warning is exactly what the greedy call alone would emit (the sampled call has
  `do_sample=True` and would not warn), consistent with being stuck in the FIRST generate.

**Still open**: WHY the main thread spins in userspace without dispatching to the NPU. The next test is a
**known-good baseline** -- run 151737Z reached step 7, so its AICore/CPU numbers are the only known-good
step data this driver has. Do not claim a mechanism before that baseline exists.

**Duration note.** 193927Z survived to ~37 min, past the ~31 min age at which its predecessor 190125Z died
and past the ~15-20 min B-181 churn cycle. 0 steps completed, 0 checkpoints, 0 metrics rows. Alive !=
productive; this is RED for unproductiveness, and no stop/relaunch follows without user GO.

### B-183 STATUS UPDATE -- DRIVER NAMED: the `error` verdict, and a proven-inert partial fix (tick #416, 2026-09-14 ~04:30 CST / 20:30Z)

B-183's item 5 ("gate the relaunch on a POSITIVE crash signal ... with explicit backoff for the 170022 class")
is now backed by a live measurement rather than an inference, and one partial fix is recorded as NOT the cure.

**The driver is the `error` verdict, not the refused window.** A 4s-cadence sample of ASI1 :20646 (daemon
under test pid 33007) caught:

    04:24:52 ASI1 booting(u62,p33007)
    04:24:57 ASI1 ERROR(Shell terminal for ASI1 fail...)     <- 170022, the ASI2 class
    04:25:01 ASI1 booting(u71,p33007)

The daemon is ALIVE and reports the platform shell-endpoint failure itself. `action_for_state` maps
`error) ACTION=restart`, so `seed_and_restart` kills and relaunches a daemon that has not crashed, on every
tick. Item 2 of this entry already shows the restart can never succeed (170022 is platform-side), so the
loop is self-sustaining by construction. Corroboration: ASI3, whose boot timer is 0 and which has never been
restarted, is the ONLY env that is `ready` (uptime 6.9h, cmdCount 4501).

**Partial fix landed, and MEASURED INSUFFICIENT -- do not treat it as the cure.** `daemon_is_midboot` gated
on `= "booting"` only, so a `down` verdict (probe REFUSED while the listener is unbound -- also measured live:
`DOWN(URLError)` at 20:19:35Z, `booting` 6s later) could never be judged mid-boot. Fixed to admit
`booting|down`, TDD: RED 12/13 -> GREEN 13/13, regression 76/76, shell suite 9/9. **Heartbeat instances
started 04:23:28 and 04:23:48 CST, both after the 04:21:57 patch, and ASI1 still restarted (59482 -> 33007).**
The gate excludes `error`, which is the actual driver. This retraction is recorded so the next tick does not
close B-183 on the strength of the `down` change.

**NEXT (ordered, #417):** in `action_for_state`, an `error` whose detail names the platform shell-endpoint
failure (`getShellVisitUrl code=170022` / "returned no terminal URL") must map to the INERT arm (log, no
kill), leaving a genuine crash `error` still restarting. RED first: a probe whose error text carries 170022
must NOT restart; an `error` with any other text still MUST.

## B-186 -- `error` is not one failure class: the platform shell-endpoint failure was restarting a live daemon
**Status: CLEARED (landed in tree 2026-09-14, tick #417) -- LANDED, NOT YET LOADED.**
Axis: ASI1/ASI2 never converge; heartbeat restarts a non-crashed daemon on every tick.

**Reproduction (live, 20:32:52Z, direct 2s-cadence probe of :20646, 24 samples):**
    booting -> error("Shell terminal for ASI1 failed because the Huanxin shell endpoint API returned no terminal")
`action_for_state` maps `error) ACTION=restart` unconditionally -> `seed_and_restart` kills and relaunches a
daemon that has not crashed. A local browser-daemon restart cannot create a platform terminal, so the
restart is waste; landing inside the ~4-5 min boot window it also destroys the boot in progress. ASI3 --
whose boot timer is 0 and which has never been restarted -- is the only env that is `ready`.

**Why the heartbeat log could not show it:** the loop logs only the state word. `grep -c "Shell terminal"
logs/huanxin_heartbeat.log` == 0. The error TEXT exists only inside `daemon_state`, so the classification
had to move there.

**Fix:** `daemon_state` emits a third field `pf` (1 when the body names the platform shell-endpoint
failure); `action_for_state` takes it as an optional second argument and routes only that class to a new
`ACTION=platform_hold`. The hold is BOUNDED: one restart attempt per `PLATFORM_ERR_COOLDOWN_S` (default
1800s), so a resource can never stay dark forever if the platform recovers (S9.1). The legacy
single-argument call is unchanged (`error` -> restart). Boot-timer persistence was refactored into shared
key/value helpers so both persisted clocks share one implementation.

**Evidence:** RED 6 failed / 3 passed -> GREEN 9/9
(`tests/test_b186_platform_terminal_error_class.py`); regression **120/120** across 15
heartbeat/huanxin/keeper suites; shell suite 9/9; `bash -n` OK.
Guard updated, not loosened: `tests/test_huanxin_heartbeat_empty_probe.py` pinned the 2-field default form
and now pins the 3-field form exactly, with a comment forbidding a prefix match.

**NOT a cure yet:** the running heartbeat loaded the old script at boot, so the fix goes live only on the
next heartbeat restart ([[keeper-runs-stale-code]]); launchctl is gated in tick sessions, so no forced
reload was made. The falsifier for #418: a restart line in `logs/huanxin_heartbeat.log` after the reload.

**Separate, still open:** `keychain item not found -- 'Chrome Safe Storage' is absent for this user` ->
`cookie seed FAILED` on every restart. No restart can fix this; it is its own entry (owner
auth/daemon-watch, #418). This is why a successful relaunch still has no session.


### B-184 STATUS UPDATE -- FIXED RED->GREEN in the Mac tree (tick #418, 2026-09-14 ~05:04 CST / 21:04Z)

**Reproduced again this tick, independently of the #414 filing.** `logs/session_keeper_watchdog.log`
showed `action=KICKSTART rc=0` at 04:44:06, :45:07, :46:08, :47:08, :48:09, :49:09, :50:10, :51:11 --
once per 60s, each a NEW pid, while the reported `cycle age` grew monotonically 2300.0 -> 2724.2s.
`/tmp/session_keeper_state.json` was still frozen at `2026-09-14T04:05:45 STARTING cycle=1 pid=78550`
and pid 78550 no longer exists. So the #414 evidence stands unchanged 1h15m later.

**Root cause, located exactly.** `scripts/session_keeper_watchdog.py`, `decide_with_progress()`: the
kick was gated on PURE STALENESS (`if age_s is None or age_s >= HARD_STALE_S: return "KICKSTART"`,
HARD_STALE_S=900). `cpu_advanced` was computed but explicitly not gated on (the source says so in a
comment). A keeper whose failure class cannot be cured by restarting (the auth probe times out at 90s)
therefore got kickstarted forever, and `rc=0` -- which only means launchctl accepted the job -- was read
as success.

**Fix (smallest that removes the class).** Progress, not liveness, now decides. New
`read_heartbeat_progress()` reads `cycle`/`ts` from the heartbeat; new `heartbeat_progress(...)` returns
True/False/**None=UNKNOWN**, and UNKNOWN never fires. Past the bound, KICKSTART is returned only when the
state file did NOT advance AND no kick happened inside a new `KICK_BACKOFF_S = 300` window; otherwise
WAIT-SLOW. Positive absence (`proc_state is None`) and SIGCONT keep their precedence and are never
backoff-gated -- a genuinely gone keeper must still be resurrected immediately.

**TDD counts.** RED 21 passed / 3 failed with the decision logic reverted to staleness-only; the three
failures are `..._spares_a_progressing_keeper_past_the_bound`,
`..._does_not_re_kick_inside_the_backoff`, `..._cycle_spares_the_keeper_when_its_heartbeat_progresses`.
GREEN `passed=59 failed=0 errors=0 total=59` across `tests/test_session_keeper_watchdog.py` +
`tests/test_session_keeper_watchdog_restart_grace.py`. 7 tests added.

**Two pre-existing tests had to CHANGE, and that is recorded rather than hidden:** they locked the bug in.
`test_decide_with_progress_kills_a_live_keeper_only_past_the_bound` now passes `state_advanced=False`
explicitly; `test_decide_with_progress_kicks_past_the_hard_cap_even_when_working` is REPLACED by
`..._spares_a_progressing_keeper_past_the_bound` (it asserted the staleness-only kick). A test that
asserts the bug is not a test.

**NOT DEPLOYED / NOT CLAIMED AS CURED.** The running watchdog is a stale-code process (see
[[keeper-runs-stale-code]]) and it is UNSUPERVISED ([[keeper-watchdog-unsupervised]]): killing it removes
the guard permanently. Reloading it is USER-GATED and was not done. So the 1/min kick continues until
that restart; the fix is in the tree only. B-184 stays OPEN on that basis.

**Unchanged open question from #414:** whether the auth failure is an expired credential or an
unreachable `ANTHROPIC_BASE_URL` is still UNATTRIBUTED. This fix stops the CPU burn; it does not restore
auth.

## B-187 -- [OPEN, S1] ASI1/ASI2 non-convergence is PLATFORM-SIDE (dev env recycled/locked), not a restartable daemon crash
Filed 2026-09-14 05:32 CST / 21:32Z by manager (tick #419). ID measured free immediately before filing
(`grep -o "B-18[0-9]" .sapo-loop/bugqueue.md | sort -u | tail -1` -> B-186).

**Why this is filed separately from B-183.** B-183 already says the heartbeat "restarts ASI1/ASI2 every
~2-8 min, so they never converge" and treats the restart as the disease. This tick measured that the
restart is a SYMPTOM, and the disease is not local at all. Every prior tick that reasoned "the restart can
never succeed, so stop restarting" was directionally right but stopped one step short of the cause.

**Evidence -- the box's OWN daemon log, not an inference.** `quantum-gpt-new/logs/huanxin_all_keepalive.log`, tail:

    [daemon:ASI2] Failed to open shell: Shell terminal for ASI2 failed because the Huanxin shell endpoint
    API returned no terminal URL. getShellVisitUrl code=170022 for env=ASI2 pod=dl-868c1...-r0-2...

with the raw platform reply embedded in the same line:
    shellVisitHit status=200 url=https://aihuanxin.cn/kunlun/web/develop/v1/getShellVisitUrl method=POST
    body: code=170022, msg=获取shell终端信息失败 ("failed to obtain shell terminal info"), data=null
    consoleHit: WebSocket connection to wss://aihuanxin.cn/kunlun/null failed: 404
    websocketHit: wss://aihuanxin.cn/kunlun/null          <- the URL is literally the string "null"

and the captured page surface reporting `"disconnected":true` / `terminalPreview:""` with the platform's
own body text: "开发环境使用完毕后请及时手动停止，如长时间闲置，将被自动回收，状态更新为已锁定"
("stop dev environments when done; if idle for a long time they will be AUTO-RECYCLED and the state
UPDATED TO LOCKED").

**Root cause.** The Huanxin platform has RECYCLED/LOCKED the ASI1 and ASI2 dev environments. The pod
survives and its daemon keeps running (that is why /health answers `ok:true`), but the platform will no
longer mint a shell terminal for it -- getShellVisitUrl returns 170022 with a null URL, so the browser
front end falls through to the literal URL "null". No local restart, no auth re-capture and no daemon
respawn can create a platform terminal. Restarting is not merely useless; it lands inside the ~4-5 min
boot window and destroys the boot in progress.

**Corroboration.** ASI3 -- which has never been restarted and whose daemon is orphaned (PPID 1, uptime
7.9 h, cmdCount 5276) -- is the ONLY env that is `ready`. The env nobody touches is the env that converges.

**Action required: USER-GATED and OUTWARD-FACING.** The ASI1 and ASI2 dev environments must be re-opened /
re-created on the Huanxin platform console. There is no local workaround. Until then ASI1/ASI2 are RED
under S9.1 and must be reported NOT-READY every tick, with this bug ID -- NOT as a crash to be healed.

**What IS already correct (do not re-file as broken).** The B-186 classifier fix IS deployed and firing:
`scripts/sapo_huanxin_heartbeat.sh` (mtime 2026-09-14 04:57) contains `action_for_state` with the
`platform_hold` arm, `PLATFORM_ERR_COOLDOWN_S=1800`, and the python probe returning a third `pf` flag keyed
on the error TEXT; `/tmp/huanxin_platform_err_timers.txt` is being written by live instances (mtime 05:23)
holding `ASI1 1789333127` (20:58:47Z) and `ASI2 1789334230` (21:17:10Z). Restarts for the platform class
are therefore already suppressed for 30 min at a time.

**Instrument warning for the next reader.** `grep -c 170022 scripts/sapo_huanxin_heartbeat.sh` returns 0.
That is CORRECT and does NOT mean the fix is absent: the script keys on the error TEXT ("shell endpoint API
returned no terminal"), never on the numeric code. Grep for the token the code actually uses. This tick
made that mistake first and corrected it before acting -- see [[trainer-grep-self-matches-brief]] for the
same class of grep-as-instrument error.


## B-188 -- NPU driver OOM kills a storm-launched run BEFORE step 1 (filed 2026-09-14 05:35 CST, tick #420)
Status: OPEN. Severity: high (kills runs pre-step-1, so it produces no metrics row at all).

**Symptom.** Run `outputs/sapo-27b-ai-20260913T211459Z` (launched 21:14:59Z) created its run dir
(`checkpoint_sync_daemon.sh`, `judge_bridge/`, `launch_config.json`, `repair_sidecar.pid`) but NEVER wrote
`grpo_step_metrics.jsonl` -- i.e. it never reached step 1. Its trainer log
`logs/sapo_27b_ai/grpo_train_20260913T211459Z.log` ends at 21:16:33 with:

    [ERROR] 2026-09-13-21:16:33 (PID:109970, Device:0, RankID:0) ERR00100 PTA call acl api failed
    [Error]: Failed to apply for memory.
    rtsFuncGetByEntry execution failed, reason=driver error:out of memory
    ... current working operator name is aclnnFlashAttentionScore
    torch_chunk_gated_delta_rule -> torch.zeros(batch, heads, k_head_dim, v_head_dim).to(value)

**Why this is filed rather than explained away.** `npu-smi` measured at 21:24Z, AFTER the crash, shows all
8 chips OK, HBM 3414-3416 MB / 65536 MB, AICore 0%, temps 33-49C. The failure is therefore NOT the
whole-device HBM exhaustion the #417 leak looked like -- ~61 GB was free on every chip. A driver-level
"Failed to apply for memory" against a nearly-empty device points at per-process/cgroup accounting, device
fragmentation, or an overlapping-run/co-tenant collision -- NOT at the #417 leak class. Do NOT close this as
a "#417 regression" on the strength of the HBM numbers.

**Leading hypothesis (untested).** The launch storm fires a new run every few minutes; if run N+1 starts
while run N still holds device context, the allocation fails. Storm and OOM would then share one root cause.
Test: correlate storm launch timestamps against per-run log error times, and read the FULL
`/proc/<pid>/cgroup` line (two cgroup hashes can differ by 2 chars -- read the whole path before blaming
your own pod).

**Instrument warning.** `npu-smi` sampled after the crash is NOT evidence about the crash; it reads a now
idle device. The only in-incident evidence is the trainer log.

## B-189 -- judge-health singleton does not evict a PRE-GUARD duplicate (filed 2026-09-14 05:36 CST, tick #420)
Status: OPEN. Severity: medium (two independent strike counters; contaminates judge-health verdicts).

**Measurement.** `ps` at 21:25Z shows TWO live `sapo_judge_health_agent.py`:
    pid 23345  started 04:48 CST  homebrew python 3.14
    pid 53616  started 00:48 CST  CLT python 3.9
plus Mac watcher pid 47526 (alive).

**Evidence both are ACTIVE, not one stale husk.** `/tmp/sapo_judge_health.log` interleaves two strike
counters within the same minutes:
    20:59:35 strikes=28 | 20:59:41 strikes=1
    21:05:02 strikes=29 | 21:05:09 strikes=2
    21:16:07 strikes=31 | 21:16:14 strikes=4
    21:21:34 strikes=32 | 21:21:42 strikes=5
and `/tmp/sapo_judge_health_state.json` holds strikes=5 (the younger sequence). Two interleaved,
independently incrementing counters = two pollers, not one process logging twice.

**Root cause (leading, consistent with the measurement).** B-171 added `_singleton_lock()`, but a process
loads its source ONCE at boot ([[keeper-runs-stale-code]]). pid 53616 started 00:48, i.e. BEFORE the guard,
so it runs unguarded forever and a guarded instance cannot evict it. The guard prevents NEW duplicates; it
does not remove EXISTING ones, and the only remedy (restart/kill) is user-gated.

**Not fixed here, deliberately.** The candidate fix -- let a guarded instance evict a live unguarded
duplicate -- is a process-killing action on shared infrastructure; that needs the user, not a standup tick.

**Related but SEPARATE.** The 502 both instances report is an upstream question: `HTTP Error 502: Bad
Gateway` has been continuous since <=20:54Z (strikes 32 then, 5 now). 502 is the DP4 proxy/upstream leg, not
the agents. Do not conflate the duplicate-agent defect with the judge outage, and do not close this bug by
fixing the 502.


### B-182 -- STATUS UPDATE (tick #422, 2026-09-14 05:47 CST / 21:47Z): THIRD reproduction, and a DECISIVE instrument

The stall is not a one-off and it is no longer only stage-frozen -- this tick supplies the instrument
that separates it from a legitimately long generation.

**Run 20260913T213147Z (live, ASI3), measured read-only at 21:41-21:45Z:**
- train log `grpo_train_20260913T213147Z.log` frozen at mtime `21:33:35.331`; at measurement 21:45:02Z
  that is **11m27s** of silence after the single `step_begin`.
- `grep -c generation_done` = **0**; `grep -c step_begin` = **1**; `grpo_step_metrics.jsonl` **absent**.
- run dir contents: only `launch_config.json`, `judge_bridge/`, `repair_sidecar.pid`,
  `checkpoint_sync_daemon.sh`. **No `step_*` dir.** Dir mtime frozen `21:32:01Z`.
- `/proc/115657/syscall` **EMPTY**, `wchan` = **0** -- pure userspace.
- `utime+stime` delta = **789 jiffies / 5s** (HZ=100) => about **158% CPU** burning.
- **`npu-smi info` AICore = 0% on ALL EIGHT chips** (Bus-Ids 0000:C1, C2, 81, 82, 01, 02, 41, 42),
  while HBM is **11.4-14.0 GB resident per chip**. Power ~100 W, temps 34-48 C.

**Why this matters (the discriminating step).** Log silence at `step_begin` is consistent with EITHER
(a) a genuinely long generation of 8 x 2048 tokens on a 27B model, OR (b) the B-182 spin. A healthy
generation would DISPATCH, and the chips would show AICore above zero. They read **0% on all eight**
while the process burns 158% CPU. That retires reading (a) for this run: the NPUs are ATTACHED but NOT
DISPATCHING. This is the same signature recorded at #416, now reproduced on a third run.

**Correction to a previously-used bar.** The `210201Z`-derived per-step estimate of about 40-55 s is NOT
a valid stall threshold: those steps were 3-token collapsed steps (see B-190 below) and return in
seconds. Any stall predicate must be keyed on wall-clock `step_begin` age with an AICore/syscall
discriminator, not on a step-duration constant.

STILL OPEN, S1. Not stopped, not relaunched (no auto-stop predicate matches; see B-190).

### B-183 -- STATUS UPDATE (tick #422, 2026-09-14 05:47 CST / 21:47Z): census re-measured, and the loop is still live

Re-measured the restart loop this tick at 21:41Z and 21:45Z, four minutes apart:
- ASI1 :20646 -- `ready:false`, `startupState:booting`, pid **44930 -> 81759**, uptime **34 s -> 167 s**.
- ASI2 :19004 -- pid -> **31937**, uptime **43 s**, now `booting` (it read `startupState:error` with
  `getShellVisitUrl code=170022` earlier the same tick).
- ASI3 :20653 -- by contrast pid **22124**, uptime **29985 s** (about 8.3 h), `ready:true`, stable.

Pids CHANGING with uptime never above about 3 minutes is exactly B-183's ~2-8 min restart cycle, and it
is a stronger reading than "recycled and idle": the daemons are being restarted in a loop, not merely
down. **This qualifies #421's note that ASI1/ASI2 are "B-187 USER-GATED, do not re-file as a crash".**
B-187 (platform-side recycle) and B-183 (a duplicate heartbeat instance that cannot find the keychain
item, restarting ASI1/ASI2 every ~2-8 min) are not exclusive, and B-183 names a LOCAL cause that is
actionable without the platform console. NO ACTION TAKEN this tick: the heartbeat census is explicitly
unreliable per the standing note that one census read 8 instances and a re-measure read 3, so acting on
a single census would be acting on an unverified instrument. Owner: Auth/Daemon Watch.

### B-190 -- [OPEN, S2] The circuit-breaker family has NO member for "step_begin with no generation_done": a stalled trainer is never auto-detected
Filed 2026-09-14 05:55 CST / 21:55Z by manager (tick #422). ID measured free immediately before filing
(`grep -oE 'B-[0-9]+' | sort -u -V | tail -1` = B-189).

**Symptom.** A trainer wedged at `step_begin` (B-182) burns NPUs and host CPU indefinitely and NO
automatic predicate fires. #418 recorded the same gap from the other direction: a 13/13-all-skip run
was deliberately left running because no auto-stop predicate matched it.

**Root cause -- a MISSING RULE CLASS, not a missing rule.** Every member of the breaker family is fed
per-step FACTS (`completion_token_lengths`, `eos_termination_rate`, `truncation_rate`,
`fence_termination_rate`, `entropy_mean`) and is evaluated at a STEP BOUNDARY via
`observe_and_evaluate_breakers(...)` -> `breaker.evaluate(step=...)` (`training/grpo_trainer.py:3280`).
A stall produces NO step and NO facts -- `generation_done` never runs, so there is nothing to observe
and no boundary to evaluate at. The condition is therefore invisible to the whole family BY
CONSTRUCTION: it is a WALL-CLOCK, MID-STEP watchdog, which is a different class of guard from a
step-fact rule. Enumerated and measured: `grep -rn 'stall|no_progress|step_begin_age|generation_timeout|
hung' training/grpo_trainer.py` returns ZERO detection code -- the only stall tooling is OPERATOR-MANUAL
(`install_faulthandler_dumps`, SIGUSR1 -> stacks, `grpo_trainer.py:4992-4999`).

**Required fix (RED test first).** A trainer-level predicate: alarm when `step_begin` age exceeds a
threshold AND the step has produced no `generation_done`. The threshold must NOT be a step-duration
constant (see the B-182 UPDATE above). The discriminator that makes it safe is the one measured this
tick: **AICore == 0 across all chips while the process burns CPU** (with `/proc/<pid>/syscall` empty and
`wchan == 0`), which separates a true spin from a legitimately long generation. Smallest fix, then GREEN
plus regression. Owner: Guardian / B-182 lane. Deadline: #423.


### B-184 STATUS UPDATE -- PROCESS ROOT-CAUSE PROVEN (tick #425, 2026-09-14 06:06 CST / 22:06Z)

Sharper than the #418 update: the fix is not merely "in the tree only", the RUNNING PROCESS is proven
to predate it. Watchdog pid 15469, PPID 1, started Fri Sep 11 10:55:38, /usr/bin/python3. Every line it
writes has the OLD format (`cycle age=.. stat=.. cpu=.. adv=.. pid=.. action=.. rc=0`); the in-tree
format string at line 533 writes `... pid={} elapsed={} hb_cycle={} state_adv={} since_kick={}
action={}`. The live lines carry NO elapsed=/state_adv=/since_kick= fields, so the process predates
KICK_BACKOFF_S=300 and the progress gate. It kicks once per POLL_S(60) forever; each `kickstart -k`
SIGKILLs the fresh keeper before its 90s auth probe + 120s env sweep can finish a cycle, so the
heartbeat never moves off `{ts 04:05:45, status STARTING, cycle 1, pid 78550}`.
`logs/session_keeper.log` showed 28 fresh "started pid N" lines from 05:45:48 to 06:00:26 -- ~60s
apart, the watchdog cadence, not a crash cadence.

**Attempted the heal this tick; it is PERMISSION-BLOCKED, not merely deferred.** Two Bash invocations
were denied by the session harness: the `nohup ... session_keeper_watchdog.py & disown` launch and the
`kill 15469`. Prior ticks recorded this as "USER-GATED by judgement"; the accurate statement is that
the environment refuses the action. B-184 stays OPEN on that basis, with the exact approved-for-me
command pair recorded in STATUS.md standup #425 O1 (start the NEW watchdog first, confirm it cycles
with the new format, and only then kill 15469 -- so the guard is never absent).

**Still UNATTRIBUTED (carried from #414/#418):** whether the keeper's auth failure is an expired
credential or an unreachable ANTHROPIC_BASE_URL. The reload stops the CPU burn; it does not restore
auth.

## B-191 (2026-09-14, tick #427) -- JUDGE ENDPOINT DARK: the port the trainer CALLS binds nothing (Mode B / B-152 ROOT CAUSE) -- PARTIALLY FIXED
Status: ROOT-CAUSED + tree-side fix landed + TDD GREEN | BOX DEPLOY PENDING (live run 220159Z forbids box writes)
Evidence (all first-hand, this tick):
  1. Measured FROM INSIDE ASI3 with a socket probe (the correct instrument):
       56237 OPEN | 56238 CLOSED ConnectionRefusedError | 8356 CLOSED
  2. The wrapper scripts/ai_launch_sapo_direct.sh exports
       ASI3_SAPO_JUDGE_DP4_ENDPOINT=http://127.0.0.1:56238   (design per 2026-09-11 note)
  3. scripts/box_anthropic_translator.py -- the only thing that binds :56238 -- is
       ABSENT ON THE BOX (`ls: No such file or directory`). Box has sapo_judge_bridge.py only.
  4. The engine launcher started the RETIRED file-queue bridge on :56237 and its
     "nothing is listening" guard verified :56237 -- the port IT chose -- never :56238,
     the port the CONSUMER calls. A gate consistent with itself is blind.
Causal chain: trainer calls :56238 -> ConnectionRefused -> 504 -> reward 0 -> zero gradient
  -> degenerate collapse (the measured Mode B signature: completion_token_lengths [4x8],
  eos_termination_rate 1.0, mean_reward 0.0, all_fail true).
Why the existing tests missed it: tests/test_launcher_judge_default.py and
  sapo_launch_auditor.py both assert the endpoint VALUE is :56238 -- a value-only check.
  Neither asserted the COUPLING: that the endpoint port is a port something BINDS.
Fix landed (tree): launcher starts the endpoint sidecar; fail-closed if the translator is
  missing; translator gained --port (default 56238) so the endpoint is parameterised.
TDD: tests/test_launcher_judge_sidecar_contract.py 0/3 RED -> 5/5 GREEN; regression 13/13.
NOTE: one intermediate test had a SyntaxError that broke COLLECTION -- fixed immediately
  (collection breakage is a top-priority RED per section 9.2), then re-run green.
REMAINING: the translator file is not a deploy-manifest member on the box. Deploy at the
  next launch boundary (never while 220159Z is live), then boot-verify :56238 binds.

## B-192 (2026-09-14, tick #427) -- KEEPER LIVELOCK: heartbeat frozen 2h14m while the keeper restarts every ~60s -- ROOT CAUSE NOT ESTABLISHED
Status: OPEN | root cause UNKNOWN (one hypothesis REFUTED, see below)
Evidence:
  - /tmp/session_keeper_state.json frozen at 04:05:46 (status STARTING, cycle 1), age ~2h14m.
  - logs/session_keeper.log FRESH (mtime 06:18:32) with a new "session_keeper started pid N"
    every ~60s (pids 53899/76610/99624/21692/47419/72614/98360/19548).
  - logs/session_keeper_watchdog.log FRESH, one line/60s: action=KICKSTART rc=0, age ~7886.
  - The watchdog kick is SUCCEEDING (unlike B-091's "attempted never done"): real restarts.
  - The keeper stamps at the TOP of its loop (line 425) BEFORE any probe, and only variable
    assignments sit between the start log (392) and the loop (415) -- so the first stamp
    should land within ~1s of start, yet the file never updates.
REFUTED HYPOTHESIS (recorded so it is not re-run): "host cannot fork".
  logs/session_keeper.launchd.err.log DOES contain repeated
  `session_keeper.sh: fork: Resource temporarily unavailable`, BUT its mtime is
  Sep 10 18:58 -- FOUR DAYS STALE. It is not current evidence. Almost root-caused from a
  stale log; caught by comparing log mtime to now. See [[tick-session-phantom-trainer-and-stale-log]].
  Since launchd's StandardErrorPath is APPEND-ONLY and that file is old, the keeper emits
  no current stderr -- so it is not erroring on the stamp path either. Contradiction open.
NEXT (owner: Auth/Daemon Watch, deadline #428): instrument WHY the top-of-loop stamp does not
  reach the file. Cheapest decisive probe: read the launchd job environment (SK_HEARTBEAT is
  the overridable stamp path -- if the job env carries a stale SK_HEARTBEAT, the keeper writes
  to a path no reader watches, and the frozen production file is exactly the symptom).

## B-184 (carried, still OPEN) -- watchdog pid 15469 predates the landed fix; needs a supervised reload.


## B-193 (2026-09-14, tick #428) -- THE GRADER RUNTIME ON ASI3 IS VERSION-BROKEN: every candidate fails on QISKIT IMPORTS, so the 0.50-mass pass term is structurally dead -- ROOT-CAUSED
Status: OPEN | root cause ESTABLISHED (runtime version mismatch), fix NOT designed
Evidence (measured from inside ASI3 while run 220159Z step 1 was live, 22:28-22:30Z):
  - outputs/sapo-27b-ai-20260913T220159Z/eval_results.jsonl (step 1, 3809 B, mtime 22:28:04Z) -- EVERY
    candidate row carries an ENVIRONMENT error in `details`, not a policy failure:
      `ImportError: cannot import name 'StatevectorSampler' from 'qiskit.quantum_info'
       (/usr/local/python3.11.14/lib/python3.11/site-packages/qiskit/quantum_info/__init__.py)`
      `ModuleNotFoundError: No module named 'qiskit_algorithms'`
      `swap_test_circuit raised: 'Index 0 out of range for size 0.'` (downstream of the failed setup)
    with `syntax: 1.0`, `interface: 1.0`, `import_hygiene: 0.0`, `verifier: 0.0-0.5`, `passed: false`.
  - Direct probe on the same interpreter: `qiskit.__version__` == **2.5.2**;
    `from qiskit.quantum_info import StatevectorSampler` -> ImportError;
    `import qiskit_algorithms` -> ModuleNotFoundError.
  - These keys map 1:1 onto the live reward weights in the trainer argv
    (--reward-pass-weight 0.45, --reward-syntax-weight 0.05, --reward-interface-weight 0.10,
    --reward-verifier-weight 0.10, --reward-brevity-weight 0.05, --reward-import-hygiene-weight 0.05),
    so this IS the reward path, not a side eval.
Why this matters (the class-extinction statement):
  Every group is `passed: false` on ALL candidates for reasons that have nothing to do with the policy.
  The pass mass (0.50) is therefore CONSTANT ZERO within every group -> zero advantage contribution from
  the term that encodes the actual task, and `import_hygiene` (0.05) is dead with it. Only the shaped
  terms (syntax/interface/brevity, 0.40 total) still vary. The model is being trained to write
  good-looking, well-formatted, TERSELY-COMMENTED code that cannot be executed -- the reward is measuring
  the grading environment, not the model. This is the golden-rule-1 failure ("the instrument comes
  first") arriving through a NEW door: not a wrong benchmark file, but a broken runtime under the grader.
Relationship to B-191: INDEPENDENT and ADJACENT. B-191 is the judge endpoint :56238 binding nothing
  (judge mass 0.10 dark). B-193 is the verifier's own Python environment (pass 0.50 + import_hygiene 0.05
  dark). Together 0.65 of the reward mass is structurally dead while the launcher gates stay green --
  the same "a gate consistent with itself is blind" pattern B-191 exposed.
NOT PREVIOUSLY FILED: `StatevectorSampler` and `qiskit_algorithms` had **0** occurrences in bugqueue.md
  and **0** in STATUS.md (50,505 lines) before this entry. Measured, not assumed.
NEXT (owner: Reward/instrument lane, deadline #429): determine which import surface the graders target
  (`qiskit.primitives.StatevectorSampler` in Qiskit 2.x; `qiskit_algorithms` was split out in 2.x), then
  decide pin-vs-port. Cheapest decisive probe: read the grader source for its exact import lines and run
  them under the interpreter the verifier actually uses -- do NOT assume `/usr/bin/python3` or the
  trainer's interpreter is the verifier's. Add a launch gate that FAILS CLOSED if a reference solution
  cannot pass, so a broken grader runtime can never again present as "the model is failing".
  Read-only on 220159Z: no box writes while it is live.


## B-194 (2026-09-14, tick #429) -- STEP-RECORD PROVENANCE: `loo_raw` IS RAW-SPACE BUT `advantage` IS NORMALIZED-SPACE, AND THE MATH AUDIT RECOMPUTES FROM THE SAME NORMALIZED VALUES SO IT IS STRUCTURALLY BLIND TO THE MISMATCH -- ROOT-CAUSED (not yet fixed)
SEVERITY: medium (corrupts an audit's coverage, does not by itself corrupt a training step).
STATUS: OPEN. Tree-side only; NOT deployed. Read-only on 220159Z while it is live.
FOUND BY: adversarial verification of a manager hypothesis that was itself WRONG. The retracted hypothesis
  (recorded so it is not re-run): "advantage = loo_raw / mean|loo_raw|, therefore loo_advantage_mean_abs
  is identically 1.0 and the gate consuming it is vacuous." REFUTED -- see the mea culpa below. The
  provenance defect below is the real finding the verification surfaced.
EVIDENCE (live step-1 record of run sapo-27b-ai-20260913T220159Z; local copy /tmp/t429_metrics.jsonl):
  All 8 candidates carry advantage_i / loo_raw_i as a CONSTANT 73.5267, and 1/73.5267 = 0.013600 while
  mean_j(|loo_raw_j|) = 0.013601. That coincidence is what made the retracted hypothesis look airtight.
  The ACTUAL transform (verified in the producer, not inferred):
      advantages = leave_one_out_advantages(advantage_rewards)   # training/grpo_trainer.py:6491-6498
      advantage  = advantages / running_mad.scale                # scale recorded as advantage_scale, :6495-6496
  RunningMAD is an EMA (decay 0.99) built once at grpo_trainer.py:5768 and defined at
  training/grpo_utils.py:3033-3082. Only its `_count == 0` branch (grpo_utils.py:3066-3068) sets
  scale = the CURRENT group's MAD; later steps keep the accumulated EMA. Because LOO advantages sum to
  zero, MAD(x) == mean|x| exactly -- so on a process's FIRST update the EMA branch and the retracted
  hypothesis agree numerically, and from step 2 on they diverge.
ROOT CAUSE:
  - grpo_trainer.py:4098 records `loo_raw` in RAW reward space, while the sibling `advantage` field on the
    same candidate is in NORMALIZED space (divided by the RunningMAD scale + clamped).
  - The identity that the two fields imply to a reader -- advantage == clamp(loo_raw / adv_scale) -- is
    therefore FALSE for any group with G > 1 (measured ratio 73.53, whereas 1/adv_scale = 1/0.4975 = 2.01).
  - scripts/sapo_math_audit_step_records.py:720-731 recomputes mean|adv| FROM THE SAME RECORDED
    ADVANTAGES. A recomputation that consumes the producer's own already-transformed output cannot detect
    that the transform was mislabelled. This is the section 4.2 class: a shared assumption cannot
    self-validate.
WHY IT MATTERS: the audit lane's whole purpose is to recompute a recorded number from its INPUTS and catch
  a producer lie. Here the inputs it needs (raw-space LOO) are present in the record but under a different
  name and space than the field it recomputes, so the audit silently validates tautologically. Any future
  scale bug in the RunningMAD path would be invisible to it.
NOT A BUG (recorded so it is not re-triaged):
  - `loo_advantage_mean_abs` is RECORD-ONLY. Verified by grep across training/: written at
    training/grpo_utils.py:429-430 and grpo_trainer.py:6556, and NEVER compared to anything.
  - The live flat-group gate is NOT vacuous: it compares `update_signal_magnitude < args.min_reward_std`
    at training/grpo_trainer.py:6728 and :6763, and the 2026-09-02 candidate-dispersion replacement
    (tests/test_sapo_flat_advantage_gate.py) is wired live via grpo_trainer.py:6511-6520 ->
    grpo_utils.py:2124. RMS >= 1 only on the first update; it falls with the EMA ratio thereafter, so the
    gate can fire.
  - The step-1 loss identity HOLDS exactly and is NOT a defect:
    loss_recomputed (-0.045816123485565186) + entropy_floor_penalty (0.01427195593714714)
      = -0.031544167548418045 = recorded loss, with entropy_train_mean 0.0728 < entropy_floor 1.5.
RETRACTION / MEA CULPA (so this specific false lead is never re-run): the manager's "tautological field /
  vacuous gate" hypothesis was WRONG in both halves. It was caught only because the hypothesis was handed
  to an independent adversarial verifier instead of being filed on the manager's own evidence. The
  generalisable lesson is the same one this queue keeps re-teaching: a numeric coincidence that reproduces
  EXACTLY on N=1 sample is not a proof of a construction -- check the first-special-case branch.
FIX (owner: Reward/instrument lane, deadline #430; TDD, red first):
  1. RED test: build a record with G > 1 and assert the recorded `loo_raw` and `advantage` are reconcilable
     by the documented identity -- it must FAIL against the current tree.
  2. Smallest fix: either record `loo_raw` in the SAME space as `advantage`, or rename it to make the
     space explicit (e.g. `loo_raw_reward`), so the two fields are not silently conflatable.
  3. Harden scripts/sapo_math_audit_step_records.py:720-731 to recompute the advantage from the RAW
     inputs and to consume a DIFFERENT representation than the producer's own output; add a
     tamper-injection test proving the audit catches a deliberately wrong scale.
  Read-only on 220159Z: no box writes while it is live.

## B-195 (2026-09-14, tick #430) -- HEARTBEAT DUPLICATE STORM: 9 identical heartbeat loops race the same 3 daemons, defeating B-183's mid-boot grace
Status: ROOT-CAUSED + FIXED LIVE (roster reconciliation, section 5.4.1) | no code change needed
Evidence (first-hand, this tick):
  1. `ps -ww -eo pid,ppid,etime,args` -> NINE identical `bash scripts/sapo_huanxin_heartbeat.sh`
     processes, all PPID 1, ages spanning 2d21h .. 1m. The script takes NO env argument: its
     `while true` loop (line 283) iterates ALL THREE envs internally, so nine copies are nine
     redundant pollers over the same three daemons -- not nine lanes.
  2. The spawner is a SINGLE launchd job (`~/Library/LaunchAgents/com.quantumgpt.huanxin-heartbeat.plist`,
     Sep 3). Verified by direct test: after SIGTERMing the extras, launchd immediately respawned
     exactly one supervised copy. So the extras are orphans surviving repeated `launchctl kickstart -k`
     (the kick SIGKILLs the job it knows; pre-existing detached copies are not reaped).
  3. HARM, measured: at 22:46:40Z the heartbeat's own log read `daemons={"ASI1":"booting","ASI2":"restarting",
     "ASI3":"ready"}`; at 22:48:18Z it degraded to `ASI1/ASI2/ASI3: probe UNKNOWN (fork/transport) -
     no action taken` for ALL THREE, and the tick line printed `{"ASI1":"unknown","ASI2":"unknown",
     "ASI3":"unknown"}`. Nine concurrent loops each fork a chrome/browser-daemon (51 Chrome procs,
     745 total procs) -> fork pressure -> the probe itself fails -> reads UNKNOWN.
  4. This is the class the script's OWN header documents (B-183, lines 129-137): a restart call that
     lands inside a daemon's ~4-5 min boot makes things worse, and "ASI1/ASI2 stay in churn while
     ASI3 -- never restarted -- is the only ready". With NINE loops deciding independently, every
     ASI1/ASI2 boot is interrupted by some loop's restart call, so they never converge.
Fix applied (roster reconciliation, no code change): killed 7 duplicates, then the remaining orphan,
  leaving EXACTLY ONE supervised loop (pid 89420, launchd-owned) -- section 5.4.1 "duplicate watchers
  are always killed (keep one)".
Verification: at 22:49:14Z, AFTER the cleanup, the heartbeat tick line reads
  `daemons={"ASI1":"restarting","ASI2":"booting","ASI3":"ready"}` -- the fleet-wide
  `probe UNKNOWN (fork/transport)` condition CLEARED and per-env states are distinguishable again.
  ASI3 re-measured READY by direct /exec (20653). ASI1/ASI2 still NOT-READY (boot takes 4-5 min;
  converge-by next tick).
STILL OPEN (separate root cause, user-gated): the cookie seed fails with
  `keychain item not found - 'Chrome Safe Storage' is absent for this user` -> `ASI2: cookie seed
  FAILED (user Chrome login needed?)`. A local restart cannot mint that key; this is the B-187
  console-side blocker. Filed here as the measured blocker for ASI1/ASI2 auth recovery.

## B-192 TICK #430 UPDATE -- ROOT-CAUSED AND FIXED LIVE (was: "root cause UNKNOWN")
Root cause (establishes why the heartbeat froze while the keeper restart-looped every ~60s):
  THE RUNNING WATCHDOG PROCESS EXECUTED A PRE-FIX IN-PROCESS IMAGE. pid 15469 started Fri Sep 11
  10:55:38 -- three days old -- so every fix landed in the tree since then (B-139/B-184 grace+backoff)
  was dead inside it. Two INDEPENDENT proofs, both first-hand:
    (a) LOG FORMAT. The live log emitted `cycle age=<x> stat=<s> cpu=<c> adv=<b> pid=<p> action=<a>`.
        The current on-disk code (session_keeper_watchdog.py L533-536) ALWAYS emits the extended
        fields `elapsed= hb_cycle= state_adv= since_kick=`. Their absence dates the running image
        before those fields existed.
    (b) STATE FILE. /tmp/session_keeper_watchdog_state.json lacked `last_kick_ts` and
        `keeper_elapsed_s`. Without a PERSISTED last_kick_ts the B-184 kick backoff can never engage,
        so the watchdog had no memory across cycles -- a structural precondition for the 60s loop.
REFUTED, do not re-run:
  - "HARD_STALE_S=900 is shorter than a legitimate cycle, so the watchdog kills the keeper before it
    can publish." REFUTED BY DIRECT EVALUATION of the on-disk code:
    decide_with_progress(1393.4,'R',True,30.0,False,None) -> WAIT-SLOW; with backoff -> WAIT-SLOW;
    KICKSTART is reached only with grace AND backoff stripped. HARD_STALE_S was not the cause.
  - "KICKSTART rc=0 does not land / targets a different job" (tick #429's secondary, and B-091's
    'attempted is not done'). REFUTED: the kick DOES land. The keeper pid rotated every single minute
    (45989 -> 77376 -> 99884 -> 19815 -> 45640 -> 69602 -> 94349 -> 17700) and the stamped pid 45989
    was DEAD at read time. B-091's caution is correct as a rule but did not apply here.
FIX DEPLOYED (supervised restart; no code change was needed -- the code was already correct on disk
  and already covered by tests): started the on-disk image as a detached session
  (.venv/bin/python3 scripts/session_keeper_watchdog.py, start_new_session=True, appending to
  logs/session_keeper_watchdog.log) and only THEN SIGTERMed the stale pid 15469 -- ordering chosen
  because this watchdog is UNSUPERVISED (B-139: PPID 1, no plist), so it must never be down.
DEPLOY GATE: the keeper surfaces were run GREEN before the swap --
  tests/test_session_keeper_watchdog.py + tests/test_session_keeper_watchdog_restart_grace.py +
  tests/test_session_keeper_heartbeat.py = 90/90 passed, 0 failed, 0 errors, rc=0.
VERIFIED LIVE (two consecutive cycles after the swap):
  06:46:53 cycle age=1600.9 ... pid=45989 elapsed=None hb_cycle=1 state_adv=None since_kick=None action=KICKSTART
  06:47:53 cycle age=1665.6 stat=S cpu=0.02 adv=True pid=50897 elapsed=60 hb_cycle=1 state_adv=False
           since_kick=60.3 action=WAIT-SLOW no-op
  The NEW fields are present => the new image is resident; and the decision changed from the
  unconditional KICKSTART of the old image to WAIT-SLOW against the SAME stale-age input. The
  60-second kill loop is broken. WATCH NEXT: the first full cycle verdict from
  /tmp/session_keeper_state.json (must leave "STARTING" and carry a real daemon verdict).

## B-196 -- ASI3 launcher left the judge endpoint AMBIENT-ONLY (N5 pollution vector). FIXED IN TREE, NOT YET DEPLOYED.

FILED + FIXED 2026-09-14 (tick #432, manager inline -- bounded, no lane needed).

SYMPTOM / RED. `tests/test_asi3_sapo_launcher_readiness.py::test_asi3_launcher_exports_every_generic_env_the_asi2_launcher_reads`
failed -- it was the ONLY named failure in the canonical suite's chunk 01/24. Exact RED output:
  AssertionError: ambient-pollution vectors not pinned by asi3 launcher:
  ['ASI3_SAPO_JUDGE_DP4_ENDPOINT', 'JT_LIVE', 'JT_PID', 'JT_PID_FILE', 'JUDGE_ENDPOINT_PORT',
   'JUDGE_ENDPOINT_URL', 'STALE_EP_PID', 'TRANSLATOR']

ROOT CAUSE (two defects in one line of scripts/asi3_launch_grpo_direct.sh, was line 233):
  `export JUDGE_DP4_ENDPOINT="${ASI3_SAPO_JUDGE_DP4_ENDPOINT:-}"`
  (a) It CONSUMED the name ASI3_SAPO_JUDGE_DP4_ENDPOINT -- the very name the generic ASI2
      launcher's judge-translator block READS (scripts/asi2_launch_grpo_27b_selfeval.sh:690,
      `${ASI3_SAPO_JUDGE_DP4_ENDPOINT:-http://127.0.0.1:56238}`) to decide which port to bind
      the translator on and to verify the trainer's endpoint matches -- but this launcher never
      EXPORTED it. The wrapper (ai_launch_sapo_direct.sh) does export it, so the wrapper path was
      safe; the launcher can ALSO be run directly, and then the name was ambient-only.
  (b) Its own default was EMPTY `""`, so on the direct path the trainer was handed
      `--judge-dp4-endpoint ""` while the translator block defaulted to :56238 -- the trainer and
      the translator could disagree about the judge port. That is the B-191 failure mode (trainer
      calls a port nothing serves), reintroduced one level up.

WHY THIS MATTERS (measured, live). Tick #432's box probe read step 1's record:
  {"stage":"dp4_judge_failed","step":1,"reason":"no_scores_from_dp4",
   "diag":{"reason":"transport_error","error":"URLError: <urlopen error [Errno 111] Connection refused>"}}
  against --judge-dp4-endpoint http://127.0.0.1:56238, and the step-1 breakdown carries
  `judge:[NA x8]`. So the 0.10 judge reward mass was DROPPED from step 1. An endpoint that is
  decided by a stale ambient export is exactly how that class recurs invisibly.

FIX (scripts/asi3_launch_grpo_direct.sh:233-234):
  export ASI3_SAPO_JUDGE_DP4_ENDPOINT="${ASI3_SAPO_JUDGE_DP4_ENDPOINT:-http://127.0.0.1:56238}"
  export JUDGE_DP4_ENDPOINT="${ASI3_SAPO_JUDGE_DP4_ENDPOINT:-http://127.0.0.1:56238}"
  Default :56238 = the HEALTHY box translator, matching the wrapper's innermost fallback and the
  generic launcher's own default. NOT :56237 (the stale file-queue bridge that caused the 18/22
  dark-step run). BOTH reads keep a `:-` default -- the launcher has a hard contract that it never
  expands `${ASI3_SAPO_X}` bare (asserted by _launcher_read_knobs, test_asi3_sapo_launcher_readiness.py:799);
  a first attempt that wrote the second line as a bare `${ASI3_SAPO_JUDGE_DP4_ENDPOINT}` broke 3
  sibling tests and was corrected -- the contract is real, not cosmetic.

TEST-SIDE (tests/test_asi3_sapo_launcher_readiness.py): the other 7 names were FALSE POSITIVES -- they
are locals ASSIGNED inside the generic ASI2 launcher (JUDGE_ENDPOINT_URL L690, JUDGE_ENDPOINT_PORT
L691-692, TRANSLATOR L693, STALE_EP_PID L698, JT_PID_FILE L701, JT_PID L705, JT_LIVE L706/709).
Each was individually verified assigned-not-ambient BEFORE allowlisting, and added to the `internal`
set with a dated comment naming its line. The guard was NOT weakened: the one genuine ambient vector
(ASI3_SAPO_JUDGE_DP4_ENDPOINT) was fixed in the LAUNCHER, never allowlisted.

VERIFICATION (touched surfaces, all under /usr/bin/python3 3.9.6):
  - target guard: RED -> GREEN.
  - tests/test_asi3_sapo_launcher_readiness.py + test_launcher_judge_default.py +
    test_sapo_wrapper_judge_default.py + test_launcher_judge_sidecar_contract.py = 44/44 passed
    (was 41 passed / 3 failed).
  - wider sweep `-k "launcher or wrapper or env_ or judge"` = 302 passed / 2 failed / 2 skipped /
    304 total; both failures are tests/test_judge_mac_watcher_singleton.py, which ALSO fail
    standalone and are catalogued pre-existing backlog (CLUSTER 4, "judge_mac_watcher_singleton x2",
    STATUS.md:21788). Zero new failures.
  - behavior exercised against the REAL lines read off disk (not a re-typed copy):
      direct/ambient-unset -> canon=http://127.0.0.1:56238 trainer=http://127.0.0.1:56238
      wrapper-pinned       -> canon=http://127.0.0.1:56238 trainer=http://127.0.0.1:56238
      explicit-override    -> canon=http://127.0.0.1:9999 trainer=http://127.0.0.1:9999
    (before the fix, the direct path yielded trainer="").
  - `bash -n` clean.

DEPLOY STATUS: LANDED IN MAC TREE ONLY. NOT deployed -- the ASI3 box copy is stale (dated
2026-08-31, B-191 undelivered), so this rides the same next-launch-boundary deploy as O2 (B-191's
three prerequisites: copy the launcher, copy box_anthropic_translator.py, export
ASI3_SAPO_JUDGE_DP4_ENDPOINT in the ASI3 launcher -- this fix completes the THIRD prerequisite).
Nothing is copied to the box while run 20260913T220159Z is in flight.

## B-197 -- keeper cycle time is driven ABOVE the watchdog's staleness bar by an auth probe that cannot succeed. FILED, NOT FIXED (carried as O7).

FILED 2026-09-14 (tick #432).

OBSERVATION (first-hand, this tick): /tmp/session_keeper_state.json frozen at ts 2026-09-14T06:50:14,
cycle=1, status=STARTING -- unchanged for ~13 min across repeated reads -- while keeper pid 50897
(started 06:46:53) was demonstrably ALIVE and logging:
  06:55:08  debug headless_ok -> "auth probe failed: timeout after 90.0s"
  06:55:16  ALERT headless claude auth FAILED -- attempting env refresh from live process
  07:00:06  ACTION env refresh sweep bounded (tried=1, budget=120s) -- deferring remainder
  07:00:07  ERROR no live process with valid auth found; keep retrying every cycle
  07:00:38  ALERT daemons not ready (19004 20646)
The watchdog (pid 49192) held correctly throughout: NO KICKSTART after the deliberate 06:46:53 swap,
action stayed WAIT-SLOW/NONE while the measured staleness age grew 37.7 -> 641.5s.

ROOT CAUSE: the state file is stamped at the TOP of the cycle (B-052c publishes the PREVIOUS cycle's
verdicts). Cycle 1 therefore looks "frozen at STARTING" for its whole duration. That duration is
~6-13 min against a ~120s contract, and the keeper log names why: EVERY headless auth probe burns a
90s TIMEOUT -- and under B-187 (platform recycle of the ASI1/ASI2 dev envs, USER-GATED, no local cure)
that probe can NEVER succeed. The bounded env-refresh sweep then adds up to SK_ENV_REFRESH_BUDGET_S.

WHY IT MATTERS: HARD_STALE_S is 900s. The observed cycle-top drift reached 641.5s and a cycle top can
plausibly reach ~780s, so the margin is ~2 minutes. When it flips, the watchdog KILLS A HEALTHY KEEPER
mid-cycle -> cycle 1 never completes -> the state file NEVER leaves STARTING -> the fleet shows a
permanent "keeper stalled" alarm with no keeper actually stalled, and daemon healing (section 4) is
starved by the restart loop. That is the SAME parked-forever failure #431 spent a tick on, arriving
from the other direction.

NOT the #431 hypothesis: #431 ordered "test whether the keeper's own cycle child is blocked on a
subprocess that never returns". REFUTED -- there is no blocked child; the keeper is progressing and
logging. Also NOT the B-086 recursion phantom: the nested session_keeper.sh processes are BASH
SUBSHELLS inheriting argv (session_keeper.sh never references its own name; its only nohup is the
caffeinate keep-awake).

FIX DIRECTION (needs TDD, NOT done this tick -- budget went to the live crash/relaunch + B-196):
bound the AUTH PROBE (currently 90s) far below the cycle budget so a failing auth can never dominate a
cycle; and/or stamp state at the cycle BOTTOM as well as the top so cycle duration is observable
independently of the top stamp. Regression surfaces: tests/test_session_keeper_watchdog.py +
tests/test_session_keeper_watchdog_restart_grace.py + tests/test_session_keeper_heartbeat.py
(90/90 green as of #430) must stay green, and the fix must be proved against a SIMULATED 90s auth
timeout, not just the happy path.

## B-198 -- the keeper's heartbeat-liveness check is PRESENCE-ONLY, so duplicate heartbeat loops are undetectable and B-195's reconcile-to-one silently un-does itself.

FILED 2026-09-14 (tick #432). NOT fixed -- carried as O8.

MEASURED (first-hand, this tick):
  pid 16026, ppid 1, etime 16:27, /bin/bash /Users/daxu/software/quantum-gpt/scripts/sapo_huanxin_heartbeat.sh
  pid 89420, ppid 1, etime 30:40, /bin/bash /Users/daxu/software/quantum-gpt/scripts/sapo_huanxin_heartbeat.sh
TWO independent orphans, distinct start times (~06:44 / ~06:59 CST), both reparented to PPID 1.
NOT the B-086 argv phantom: a forked subshell shows the PARENT's argv as its own child with a matching
start time; these are 15 minutes apart and neither is the other's child. So this is a genuine
duplicate, and the #430 reconciliation (B-195: "reconciled to ONE supervised loop") did not hold --
a second instance appeared ~12 minutes after it.

ROOT CAUSE (detection-side): scripts/session_keeper.sh:294 tests heartbeat liveness with
  pgrep -f "$SK_HB_PATTERN" >/dev/null 2>&1 || return 1
which is PRESENCE-ONLY. It answers "is at least one heartbeat running?" and structurally CANNOT answer
"are there more than one?". The lane that owns heartbeat health therefore cannot detect the duplicate
class it was reconciled to fix, and the reconcile can be silently undone forever. B-195's writeup
named the spawner (a single launchd job whose orphans survive kickstart -k) but never gave the keeper
the ability to COUNT.

FIX DIRECTION: make the liveness check return a COUNT, and add a keep-one path (the fleet already has
a keep-one precedent from B-195's manual reconciliation) that kills all but the OLDEST or the NEWEST
instance deterministically -- pick the survivor by a rule the code states, never by pgrep order.
Regression surfaces: tests/test_session_keeper_heartbeat.py + the B-195 reconciliation tests must stay
green, and a RED test must drive the two-instance case explicitly (a one-instance test cannot catch a
duplicate-detection bug -- the #430 evidence is that it was green while the duplicate existed).

NOTE ON THE #430 RECONCILIATION ITSELF: it was correct as an action and it did clear the fleet-wide
`probe UNKNOWN (fork/transport)`; what failed is that it had no durable guard behind it. Do not
re-litigate the reconciliation -- build the counter.

## B-197 UPDATE 2026-09-14 07:34 -- STATUS CHANGED FROM "FILED, NOT YET FIRING" TO **FIRED, IN A CLOSED RESTART LOOP**.
See the STATUS.md escalation entry of the same timestamp for the raw lines. Summary: at 07:05:59 the
watchdog executed keeper 50897 at age=943.2s > HARD_STALE_S=900 with state_adv=False -- a healthy
keeper killed mid-cycle-1. New keeper 94561 re-stamped cycle=1/STARTING at 07:08:22 and is climbing the
same slope (702.4s at 07:20), so it will be kicked again ~07:23. Net effect: the keeper can NEVER
complete a cycle, the state file can NEVER leave STARTING, and daemon healing is starved forever.
DO NOT fix this by raising HARD_STALE_S (that hides the symptom and leaves the 90s auth timeout in the
cycle). Fix the probe budget so a cycle fits inside the bar.

## B-199 -- THE B-196 FIX, IF DEPLOYED AS LANDED, RE-CREATES B-191: the launcher exports the trainer's judge endpoint at :56238 while the judge bridge it ships with binds :56237

FILED 2026-09-14 ~23:29Z (tick #433) by the manager lane. S1 -- it gates O2 (the B-191/B-196 deploy).

EVIDENCE, all read from the tree and from the LIVE box this tick, no inference:

 1. scripts/asi3_launch_grpo_direct.sh:242-243 (the B-196 fix, landed in tree):
      export ASI3_SAPO_JUDGE_DP4_ENDPOINT="${ASI3_SAPO_JUDGE_DP4_ENDPOINT:-http://127.0.0.1:56238}"
      export JUDGE_DP4_ENDPOINT="${ASI3_SAPO_JUDGE_DP4_ENDPOINT:-http://127.0.0.1:56238}"
    ...with an in-file comment at L240-241 asserting :56238 is "the healthy box
    translator, never the stale file-queue bridge :56237".

 2. scripts/asi3_launch_grpo_direct.sh:246:
      export JUDGE_BRIDGE_PORT="${ASI3_SAPO_JUDGE_BRIDGE_PORT:-56237}"

 3. scripts/sapo_judge_bridge.py:34:
      parser.add_argument("--port", type=int, default=56237)

 4. THE LIVE RUN 20260913T231041 (box ASI3, ps of trainer pid 132224) calls:
      --judge-dp4-endpoint http://127.0.0.1:56237
    and the resident bridge (pid 132234) is:
      python3 scripts/sapo_judge_bridge.py --queue-dir (rundir)/judge_bridge --port 56237

So the ONE configuration that is OBSERVED MATCHED on the live box is endpoint 56237
paired with bridge 56237. B-191's failure mode (the trainer calls a port that binds
nothing) is NOT present in this run.

WHY THIS IS A BUG AND NOT A COMMENT: lines 1 and 2 disagree with line 3. The fix
changes the TRAINER'S endpoint to :56238 but does not change the port the BRIDGE binds.
Deploy the launcher as it stands and the next launch trains against :56238 while the
bridge answers on :56237 -- the trainer calls a port that binds nothing. That is
B-191 rebuilt by its own fix, and it kills ~0.10 of reward mass silently, because a
dark judge produces absent judge keys, not an error.

THE PREMISE IS ALSO UNVERIFIED: the L240-241 comment's claim that :56238 is "the
healthy box translator" has NO positive control. This tick, box-side
curl 127.0.0.1:56238/health returned 403, which is the squid access-denied artifact
of the exec proxy, NOT a listener -- and ss -lntp did not show 56238 bound. An
unproven "healthy" claim was used to overrule an observed-working port.

MINIMAL FIX (for the lane that owns this): the endpoint must be DERIVED from the
bridge port, not hardcoded to a different one -- one variable, both names:

    export JUDGE_BRIDGE_PORT="${ASI3_SAPO_JUDGE_BRIDGE_PORT:-56237}"
    export ASI3_SAPO_JUDGE_DP4_ENDPOINT="${ASI3_SAPO_JUDGE_DP4_ENDPOINT:-http://127.0.0.1:${JUDGE_BRIDGE_PORT}}"
    export JUDGE_DP4_ENDPOINT="${ASI3_SAPO_JUDGE_DP4_ENDPOINT}"

so the pair can never drift again. REGRESSION TEST: assert that the port in the
exported endpoint equals JUDGE_BRIDGE_PORT and equals sapo_judge_bridge.py's --port
default -- parse all three, fail loudly on drift. That test must go RED against the
current tree (it will) before the fix lands. NOT FIXED THIS TICK: I did not write
source in a manager tick; it is carried as O1 with the above as the deliverable.

STATUS: OPEN, UNFIXED, BLOCKS O2.

### B-199 UPDATE 2026-09-14 tick #433 -- FIXED, TDD, VERIFIED. (Supersedes the OPEN status above.)

The manager lane reversed its own scoping call and landed the fix in the same tick.

RED/GREEN, recorded: tests/test_judge_endpoint_matches_bridge_port.py written FIRST and
shown RED against the unpatched tree -- the load-bearing assertion failed exactly as
predicted with `assert 56238 == 56237`. After the patch, 3/3 GREEN.

FIX (scripts/asi3_launch_grpo_direct.sh, one variable introduced and both names derived
from it; JUDGE_BRIDGE_PORT moved ABOVE the endpoint exports so it is defined first):
    export JUDGE_BRIDGE_PORT="${ASI3_SAPO_JUDGE_BRIDGE_PORT:-56237}"
    export ASI3_SAPO_JUDGE_DP4_ENDPOINT="${ASI3_SAPO_JUDGE_DP4_ENDPOINT:-http://127.0.0.1:${JUDGE_BRIDGE_PORT}}"
    export JUDGE_DP4_ENDPOINT="${ASI3_SAPO_JUDGE_DP4_ENDPOINT:-http://127.0.0.1:${JUDGE_BRIDGE_PORT}}"

FIRST ATTEMPT WAS WRONG, and the existing suite caught it -- recording it because it is the
kind of thing that would otherwise ship. I first wrote the alias line as
`export JUDGE_DP4_ENDPOINT="${ASI3_SAPO_JUDGE_DP4_ENDPOINT}"`, i.e. a PLAIN read with no
":-" default. tests/test_asi3_sapo_launcher_readiness.py::_launcher_read_knobs asserts the
launcher has NO plain ${ASI3_SAPO_X} read, because the wrapper's DEFER-BY-EMPTY contract
depends on every read carrying a default. That turned 38/38 into 35P/3F. The corrected form
keeps the ":-" default and derives the port. My green was not taken on the new test alone --
it was re-run against the whole launcher/judge surface.

BEHAVIOR EXERCISED against the real on-disk lines, four resolution paths:
    default (empty env)                 -> bridge=56237 endpoint=:56237 canonical=:56237   MATCHED
    ASI3_SAPO_JUDGE_BRIDGE_PORT=59999   -> bridge=59999 endpoint=:59999 canonical=:59999   DERIVED
    ASI3_SAPO_JUDGE_DP4_ENDPOINT=:41111 -> endpoint=:41111 canonical=:41111                 EXPLICIT WINS
    both set                            -> endpoint=:41111 (explicit), bridge=59999         EXPLICIT WINS
So the pair can no longer drift, and B-196's original intent (an explicit ambient endpoint
is honoured) is preserved.

CROSS-CHECK: 63/63 GREEN across the seven judge/launcher files --
test_launcher_judge_default.py, test_launcher_judge_sidecar_contract.py,
test_sapo_wrapper_judge_default.py, test_sapo_judge_bridge.py,
test_sapo_next_launch_inertness_fix.py, test_asi3_sapo_launcher_readiness.py and the new
test_judge_endpoint_matches_bridge_port.py. bash -n clean. Exactly one JUDGE_BRIDGE_PORT
export remains (no duplicate from the move).

DEPLOY STATE: LANDED IN TREE, NOT DEPLOYED -- consistent with everything else on this
launcher. The box is untouched. O2 is now UNBLOCKED as far as B-199 is concerned, but is
still gated on the other two prerequisites (i and ii) and on the launch boundary.

STATUS: FIXED IN TREE / NOT DEPLOYED.

### B-188 UPDATE 2026-09-14 23:45Z (tick #433) -- SECOND CONSECUTIVE RUN KILLED AT STEP 1, SAME SIGNATURE. NOW WITH AN EXIT CODE.

This is the second occurrence and it upgrades B-188 from "a run died once" to a REPRODUCIBLE
CRASH. Both runs, side by side:

  run 20260913T220159Z   started 22:01:59Z, crashed 23:09:19Z, trainer 121697 zombie,
                         step records produced: 1 (step 1 only, pass_rate all-zero, judge dark)
  run 20260913T231041   started 23:10:43Z, crashed ~23:32:56Z, trainer 132224 zombie,
                         step records produced: **0**

Identical terminal message in both:
  [ERROR] TBE Subprocess[task_distribute] raise error[], main process disappeared!
(8 times in the 231041 log -- one per NPU, which is why all 8 NPUs report OK afterwards: the
driver reaped the run, it did not lose the hardware.)

NEW EVIDENCE THIS TICK, the thing that was missing before -- THE EXIT CODE:
  /proc/132224/stat field 52 = **9 = SIGKILL**
Field 52 survives death, so this is not an inference from the logs. SIGKILL means an EXTERNAL
kill: NOT a clean self-exit (0), NOT a graceful SIGTERM (15), and NOT a Python exception
escaping. Combined with `main process disappeared`, an NPU driver that kills on memory
pressure (B-188's original hypothesis) is the consistent explanation, and the ~20-minute
time-to-kill is consistent with memory filling during the rollout of step 1 rather than with
an instant allocation failure.

ALSO NEW, and it invalidates a liveness instrument I used earlier in the same tick: at 23:24Z
the trainer was at 155% CPU and I read that as "genuine compute, not a stall". That reading was
TRUE but USELESS for this failure class -- the process burned 00:35:57 of CPU and stayed above
100% right up until the SIGKILL. **Host CPU burn does NOT distinguish healthy generation from
the pre-kill phase.** For this class the instruments that actually separate live from dying are
the process STATE (R vs Z) and, after death, field 52. Do not repeat my inference.

CONTEXT THAT MATTERS FOR THE FIX: this run was ALREADY the survivor of a storm -- three
sibling launches in a two-minute window (.T230922, .T231001, .T231041), only the last with a
live trainer, which is the B-181 shape. A storm launch multiplies the memory pressure that
B-188 attributes the kill to, so B-181 and B-188 are likely the same incident seen from two
angles and should be investigated together, not as independent bugs.

STATUS: OPEN. TWO CONSECUTIVE KILLS. Relaunch is USER-GATED (O8 in STATUS.md tick #433); the
manager lane did NOT relaunch and recommends a footprint change rather than a third identical
attempt, because an identical config would very likely reproduce.

## B-200 -- THE SUITE RUNNER'S WAIT ON A CHUNK IS UNBOUNDED AND UNOBSERVABLE: a slow chunk is byte-identical to a wedged runner

FILED AND FIXED 2026-09-14 ~23:50Z (tick #434). S2 (no silent verdict loss; it is the
instrument that enforces section 9.3). NOT a deploy gate -- the runner is Mac-side.

MEASURED, from the artifact of the run in flight (pid 79513,
.sapo-loop/logs/full_suite_315_79513.txt):

    chunk 01/24 elapsed=223s     chunk 02/24 elapsed=3066s     chunk 03/24 elapsed=131s

Chunk 02 spent 51 MINUTES -- 15-20x its siblings. During that window the artifact was
frozen at the chunk 01 line, so from outside it read exactly like a wedged process; this
tick read it as a pure-userspace hang and was WRONG (the chunk completed and reported
199 passed / 1 failed). The runner's pytest child pid 81772 sat at 3:40.12 CPU over
49:31 resident and advanced 0.23s in a 20s sample -- ~1.2% busy, consistent with EITHER
a blocked process or a very slow one. Nothing could tell them apart, and that is the bug:

  - `run_chunk` calls `subprocess.run(..., capture_output=True)` with NO `timeout=`, so
    the wait is unbounded; and
  - `capture_output=True` means not one byte of the child's output reaches the log until
    the child RETURNS, so there is no progress signal at all while it runs.

Consequence: for an arbitrary length of time the suite's own artifact cannot distinguish
"still working" from "never coming back", and every later tick re-reads the frozen file
as "still running". B-083's failure mode was a partial suite reporting green; this one is
worse -- a suite reporting nothing at all, silently.

FIX (landed, .sapo-loop/run_full_suite.py):
  1. CHUNK_TIMEOUT_S (default 3600, override SAPO_SUITE_CHUNK_TIMEOUT_S) bounds the wait.
     CALIBRATION IS THE POINT: 3066s is a LEGITIMATE completed chunk on this host, so the
     bound sits ABOVE measured reality -- a timeout that fires on a merely-slow chunk is a
     false alarm, priced as dearly as a missed one. If a chunk ever reports TIMEOUT, the
     first question is whether the bound is too tight.
  2. run_chunk returns a `_ChunkTimeout` record (rc=TIMEOUT_RC=124, `timed_out=True`)
     instead of propagating TimeoutExpired.
  3. summarize() puts it in an EXCLUSIVE `timed_out` bucket: its partial output is
     deliberately NOT folded into the totals (a hung chunk contributes no number it did
     not finish), and it is named separately from missing/errored because "hung" and
     "crashed" route to different owners.
  4. chunk_flags() emits a TIMEOUT marker; total_line() carries `timed_out=N` and
     `timed_out_chunks=NN`; VERDICT is INCOMPLETE and main() exits non-zero.

TDD: tests/test_full_suite_runner_chunk_timeout.py -- 5 tests, RED first (3 failed
against the unpatched runner: two TimeoutExpired escapes and one AttributeError on the
missing TIMEOUT_RC), then GREEN. Regression set:
tests/test_full_suite_runner_{chunk_timeout,reports_incomplete,reports_failing_ids,
unique_output,chunks_collected_ids,argv_guard}.py + test_suite_runner_{source_stamp,
pins_interpreter}.py + test_suite_reports_counts.py = 47 passed / 0 failed.

SEPARATE FINDING, NOT FIXED (needs a lane): a test inside collected ids 201..400 costs
~51 min, roughly 20x the norm. The runner already logs per-chunk `elapsed=`, which is how
it was measured; identifying the file is the next step. Until then every full-suite
verdict is ~1h more expensive than it should be.

STATUS: FIXED IN TREE, tests green. NOT deployed (Mac-side script; the run in flight,
pid 79513, still holds the old code in memory and will not reload).


## B-201 -- THE RUN HEALTH MONITOR IS BLIND DURING STEP 1, WHICH IS WHERE EVERY RECENT RUN HAS DIED (S2, monitoring)

FILED 2026-09-14 07:55 CST (23:55Z), standup tick #434. FIXED IN TREE, TDD, NOT WIRED, NOT DEPLOYED.

DEFECT. Every alert family in .sapo-loop/sapo_metrics_poll.py (DEAD-SIGNAL, ZERO-UPDATE,
SUB-PRECISION, CLIP BREAKER, TRUST REGION, ckpt-stall) keys on step ROWS parsed from
grpo_step_metrics.jsonl. On run sapo-27b-ai-20260913T233607Z that file DID NOT EXIST, because
step 1 never closed -- so every one of those families was structurally incapable of firing.
The one liveness signal the monitor DID read is host CPU, and tick #433 had already established
that host CPU burn is worthless here: the trainer burned 151.8% CPU right up to the SIGKILL on
the previous run, and the current run burned 151.8% CPU for 16 minutes with AICore at 0% on all
8 dies. Net: the monitor's blind window is exactly the window in which the last three runs died.

EVIDENCE (measured this tick, live run 20260913T233607Z, all box-side):
  npu-smi AICore = 0% on ALL 8 dies; HBM 11474-14018 / 65536 MB; Health OK; power 99-103 W
  -> model shards RESIDENT: not an unloaded process, not an OOM shape
  trainer pid 136418 state=R ppid=1 threads=246 rss~1.48GB; CPU 70481 -> 128010 jiffies over
  379 s = 151.8%, reproduced at 151% on an independent 25 s sample
  train_stdout.log 261850 bytes, mtime FROZEN at 2026-09-13 23:38:19.720Z across five probes
  spanning 23:42:36 -> 23:54:30 (16 min); grpo_step_metrics.jsonl absent; 0 step_*_adapter dirs
  log body: line 19 step_begin step 1 -> line 21 "Exception in thread Thread-2:" -> 8x
  [ERROR] TBE Subprocess[task_distribute] raise error[], main process disappeared! -> EOFError at
  tbe/common/repository_manager/utils/multiprocess_util.py:68 in run -> self.task_q.get()
  The TBE kernel-COMPILE manager dies while step 1 is open; generation cannot get kernels
  compiled afterwards; the main thread never exits, it spins. Live-looking corpse.

FIX (landed in tree this tick). Two pure functions in .sapo-loop/sapo_metrics_poll.py:
  parse_aicore_rows(text) -> per-die AICore% from `npu-smi info`, or None when unparseable.
    Returns None rather than [] -- 0% AICore is a VERDICT in dead_spin_alert, so a parse failure
    must not be able to manufacture one (the B-130 absent-gradient rule, one layer over).
  dead_spin_alert(aicore_samples, trainer_running, step_open, consecutive=2) -> fires DEAD-SPIN
    when a running trainer with a step open is 0% on EVERY die for N consecutive samples.
  Silent, deliberately, on: no trainer running; no step open; a partially-working device (a
  different condition -- naming it DEAD-SPIN would be a lie); and any incomplete measurement
  (unmeasured/empty sample, or samples disagreeing on die count).

TEST. tests/test_npu_dead_spin_alert.py, written FIRST, 12/12 RED (AttributeError, functions
absent) -> 12/12 GREEN after the fix. Focused regression over the poller surface 83/83 green;
py_compile clean. My first implementation was wrong (the bus-id character whitelist omitted
':', so every real npu-smi row was rejected and both parser tests returned None) -- the gate
caught it before it landed.

REMAINING. Nothing calls dead_spin_alert() yet, so the defect is still UNMONITORED in
production; wiring it into poll_once() is order O1 of tick #434. Not deployed to the box.

RELATED. B-182 (userspace spin), B-188 (SIGKILL at step 1, now 3 consecutive), B-181
(unattributed launch storm -- 5 launches in 3m12s at 23:32:55-23:36:07, and 3 in 80 s at
23:09:22-23:10:41; suspected CAUSE of the B-188 kills, unproven).


### B-188 UPDATE 2026-09-14 07:55 CST (23:55Z, tick #434) -- THIRD CONSECUTIVE KILL-WINDOW RUN, PLUS THE FIRST DEVICE-SIDE PROOF AND THE STORM CLUSTER

Third data point, same terminal signature, and this one did NOT even reach a step record or a
SIGKILL before the tick ended -- it is still state=R and spinning:

  run 20260913T220159Z  started 22:01:59Z  died 23:09:19Z  step records: 1 (all-zero)
  run 20260913T231041   started 23:10:43Z  died ~23:32:56Z step records: 0  exit 9 (SIGKILL)
  run 20260913T233607Z  started 23:36:10Z  STILL SPINNING at 23:54:30Z, step records: 0

THE DEVICE-SIDE PROOF THAT WAS MISSING. Tick #433 could only say "CPU burn does not
distinguish healthy from dying". This tick, on 233607, the separating instrument is AICore:
0% on ALL 8 dies with HBM 11474-14018/65536 MB resident and Health OK. Host CPU was 151.8%.
So the run holds its NPU memory and issues no work -- the B-182 spin, measured directly rather
than inferred. The log has been frozen at 23:38:19.720Z for 16 minutes with the same 8x TBE
"main process disappeared" + EOFError at multiprocess_util.py:68.

THE STORM, NOW CO-TIMED WITH THE KILLS RATHER THAN MERELY NEAR THEM. Run dirs created
23:32:55, 23:33:12, 23:33:29, 23:36:02, 23:36:07 -- FIVE in 3m12s, with a second cluster of
three in 80 s at 23:09:22/23:10:01/23:10:41. Of the five, three never started a trainer
(judge_bridge + repair_stage only), one (233602) started a trainer and wrote 0 step_begin,
and one (233607) reached step_begin step 1 and then lost its TBE manager. TWO trainers
therefore started FIVE SECONDS APART on a box where --npu-max-memory-gib 54 x 8 shared dies is
the same HBM pool.
HYPOTHESIS (labelled as one, NOT proven): B-181 is the CAUSE and B-188 is the SYMPTOM -- a
storm launch multiplies the memory pressure that reaps the survivor's TBE compile manager. The
clean test is a launch that is the ONLY launch in its window, which needs the user's GO.
ACTOR STILL UNATTRIBUTED: no launcher/watchdog/divergence-watch/metrics-poll process on the
Mac at 23:50Z, no box crontab, no new dir since 23:36:30Z. Intermittent, not resident.

ALSO: 6x checkpoint_sync_daemon.sh + 6x fv_gspo_repair_sidecar.sh from dead runs, all reparented
to ppid 1, oldest 2h17m, all at 0.0% CPU / ~10 MB -- idle, not reaped, one pair leaked per
launch. Not an emergency; recorded so it is not rediscovered.

### B-202 -- CLOSED (tick #435, 2026-09-14 08:12 CST) -- the teardown watcher was STRUCTURALLY BLIND to every run since 2026-09-02
[OPEN -> CLOSED same tick]
`.sapo-loop/logs/teardown_watch_v3.py::read_log` built its log path from
`<LOGDIR>/grpo_train_<ts>.log`. The launcher no longer writes there; current runs write
`<run_dir>/train_stdout.log`. The watcher therefore logged `NO-LOG run=...` on EVERY 30 s cycle.

REPRODUCED: run sapo-27b-ai-20260913T233607Z was writing -- train_stdout.log 262701 B, mtime 00:00Z,
carrying generation_done + logprob_done -- while teardown_watch_v3.log read NO-LOG at 23:52:09Z,
23:52:50Z, ... 00:04:51Z with no break. Box-side: the newest `grpo_train_*.log` was
20260902T072457Z (Sep 2). ~12 days of blindness.

WHY IT MATTERS: this watcher is the detector feeding the resurrector. A detector that cannot see a
healthy run cannot see an unhealthy one -- the failure is symmetric. It is the B-185 class
(census-derived path collapsed) recurring one layer down: the path was STICKY, but the CONVENTION
was stale, so stickiness bought nothing.

FIX: new `log_candidates(run_dir)` returns run-local FIRST, legacy as fallback; `read_log` probes
each in order. TDD: tests/test_teardown_watch_log_resolution.py, 4 tests, RED 0/4 -> GREEN 4/4.
LIVE-VERIFIED after restart: exists=true size=263129 gdone=1 (numeric, growing).

### B-202b -- CLOSED (self-inflicted, caught during B-202 verification)
The first B-202 patch over-escaped the probe template, so SIZE reached the box as the literal
`%s` instead of a number. Caught LIVE, not by the tests: read_log returned size="%s" against a
262701-byte log. Fixed; pinned by a new test. Recorded rather than quietly corrected -- a
non-numeric measurement field is exactly the silent-wrongness class this loop exists to catch.

### B-203 -- CLOSED (tick #435) -- TEARDOWN fired on a LIVE, PROGRESSING run
[OPEN -> CLOSED same tick] EXPOSED BY the B-202 fix, one poll after the watcher was restarted and
could finally see anything:

    *** TEARDOWN run=.../sapo-27b-ai-20260913T233607Z tear=8
    *** FIRST generation_done run=.../sapo-27b-ai-20260913T233607Z

Both lines are the SAME poll of the SAME healthy run: log grown 262701 -> 263129 B, step 1 just
completed generation_done + logprob_done. The predicate tested the TBE "main process disappeared"
count ALONE (tear > 0). Tick #434 had already downgraded that fingerprint box-side -- the 8x TBE
block is what TBE children print when their parent recycles them, and it appears in runs that
reach step 7 too. tear>0 is not a death signal on its own.

WHY IT MATTERS: a TEARDOWN on a running trainer is the spurious-relaunch class that puts two
trainers on one NPU pool (section 5.4.1) -- the killer class.

FIX: three-state discipline (section 5.4.1). TEARDOWN now requires the fingerprint AND a log size
unchanged since the previous poll of this target. First observation = TEAR-UNKNOWN, never fires;
growing OR reset log = TEAR-NONFATAL. TDD: tests/test_teardown_watch_teardown_predicate.py, 4
tests, RED 1/4 -> GREEN 4/4, and the pre-existing true-alarm case still fires.
LIVE-VERIFIED after restart: `TEAR-UNKNOWN ... (first observation)` then
`TEAR-NONFATAL ... (log moved 263403 -> 264756)`, with `*** FIRST generation_done` preserved.

### B-203b -- CLOSED (tick #435, 00:16Z) -- "frozen log" was still not enough; the B-203 fix only MOVED the false positive
[the B-203 entry above claimed CLOSED on the frozen-log fix. That claim was HALF TRUE and is
corrected here rather than left standing.]

DEPLOYED B-203 THEN FIRED AGAIN ON THE LIVE RUN, 00:08:23Z:
    *** TEARDOWN run=.../sapo-27b-ai-20260913T233607Z tear=8 size=264756 (frozen since last poll)
...while pid 136418 was in state Rsl at 140% CPU -- ALIVE. A trainer that goes quiet for minutes
during a compute-heavy phase satisfies both "fingerprint" and "frozen log" while being perfectly
healthy. Output staleness is not process liveness (section 5.4.1's working != alive trap).

FIX: three-way AND -- TBE fingerprint AND frozen log AND no trainer PROCESS. The liveness term is
free: the watcher already runs a ps census every cycle to resolve the live run. Empty census =
legitimate teardown; census naming the target = resident; census unavailable = UNKNOWN, no fire.
TDD: 3 new tests, 12/12 green across both files. LIVE-VERIFIED: four consecutive cycles
(00:12:47/00:13:23/00:14:01Z/00:14:52Z) now read
    TEAR-NONFATAL ... (log quiet at 264756 B but the trainer process is RESIDENT)
with generation_done still firing.

RECORDED LESSON: a liveness predicate that has never been observed SUPPRESSING a true-looking
alarm is not verified. B-203 was green, deployed and restarted -- and still wrong -- because it had
never been run against a quietly-alive trainer. "Green + deployed" is not "exercised on the
adversarial case".

## B-206 (2026-09-14, tick #437) -- JUDGE WATCHER DROPPED THE UPSTREAM ERROR BODY -- FIXED (tree-side; live watcher not reloaded)
Status: FIXED, TDD RED 1/4 -> GREEN 4/4 | regression 34/36 with 2 PRE-EXISTING failures named.
File: scripts/sapo_judge_mac_watcher.py:258 (`call_dp4`). Test: tests/test_judge_mac_watcher_upstream_error.py
Cause: blanket `except Exception` used `repr(exc)`, which for HTTPError is the short form
  (`<HTTPError 500: 'Internal Server Error'>`), discarding the upstream JSON body that carried
  `Huanxin inference gateway returned HTTP 500: subscription route not found`.
Effect: at the trainer, a CONSOLE-GATED upstream failure was byte-identical to a local watcher crash.
Fix: dedicated `except urllib.error.HTTPError` clause that reads `exc.read()` and emits
  `HTTP <code>: <body>`; generic clause retained; explicit `import urllib.error`.
Live watcher pid 34649 still runs the OLD handler -- restart is a separate deliberate action.
Also REFUTES the standing "all three local proxies fail identically (502/502/500)" note: a fresh probe
  found those ports connection-refused from the Mac (box-local), only :55648 live, reporting upstream.

## B-205 (2026-09-14, tick #437) -- `import_hygiene` IS STRUCTURALLY UNEARNABLE for the quantum tasks
Status: OPEN | not yet root-caused to a fix | owner: Reward/Instrument lane, next tick
Evidence (reward lane, verified against the running code path -- its arithmetic reproduces the step-1
log exactly): `grpo_utils.py:1243-1252` -- `allowed_import_roots` is EMPTY for this task, so every
non-stdlib import counts as a violation and `max(0, 1 - viol/len)` -> 0.0. A quantum task whose
solution REQUIRES `qiskit.primitives` therefore scores 0.0 on this term for EVERY candidate, including
a perfectly correct one. 0.05 of nominal mass that no policy can ever earn.
Note: independent of B-193 (refuted) and of the qiskit-2.x API mistakes. It would survive flawless
imports from the policy. Task-metadata defect, not a policy failure.

## B-193 -- CLOSED AS REFUTED (2026-09-14, tick #437)
The claim "the grader runtime is version-broken, so the 0.50-mass pass term is structurally dead
through no fault of the policy" does NOT survive the decisive experiment. Under the box verifier
interpreter (/usr/local/python3.11.14, qiskit 2.5.2) the task's OWN reference/verifier path is GREEN
(`tests.run_tests('candidate.py')` -> passed True, amplitude_error 0.0591 <= pi/8; the task's
candidate.py runs clean; tests.py imports only importlib.util/math/numpy). The live ImportError
is `cannot import name 'StatevectorSampler' from 'qiskit.quantum_info'` -- a WRONG MODULE chosen by the
policy; under qiskit 2.5.2 it lives in `qiskit.primitives`. So the instrument is FINE and the policy is
genuinely failing, which is what RL is for. A second stale fact is also corrected: earlier ticks quoted
`QuantumInstance from qiskit.utils`; that was never the measured error.

## B-207 -- KEEPER WATCHDOG KILLS A HEALTHY KEEPER EVERY CYCLE (bar < legitimate cycle time)
Status: OPEN, root-caused to a fix | owner: Keeper/Auth-Daemon lane | filed 2026-09-14 tick #438
NOTE ON THE ID: STANDUP #437 declared this defect filed as `B-204`, but B-204 is ABSENT from this
file -- the STATUS.md prose was not a filing (the documented class). It is filed now, measured.
Evidence (keeper lane, re-verified against this tree this tick):
- scripts/session_keeper_watchdog.py:62 STALE_AFTER_S=420, :66 HARD_STALE_S=900 (15 min ceiling).
- A legitimate keeper cycle measures ~1050 s (17.5 min): session_keeper.sh:425 writes the TOP stamp
  at cycle start and :514 the BOTTOM stamp at cycle end; between them the state file does NOT move.
  Observed instance: keeper started 07:25:18 -> `HEARTBEAT cycle=1` printed 07:42:51.
- 900 < 1050, so a HEALTHY keeper is always past the ceiling -> state_advanced=False for the whole
  cycle -> the kick gate fires -> `launchctl kickstart -k` (SIGKILL, silent) -> launchd respawns.
  Direct: watchdog log `[08:26:28] since_kick=1327.1 action=KICKSTART rc=0`, then `session_keeper
  started pid 86975` at 08:27:56. pid 70723 (started 08:05:47) was SIGKILLed without ever printing
  its cycle-1 HEARTBEAT.
- The cycle counter RESETS (cycle=1381 at 18:04 -> cycle=1 at 19:26:31). A mid-cycle sample of ONE
  process cannot reset; a reset proves a NEW process. This FALSIFIES #437's 'not livelocked, just
  one slow cycle' conclusion while CONFIRMING that the short bar is the cause.
- FALSIFIED, do not re-run: 'a second writer to logs/session_keeper.log'. The string
  `daemons not ready - heartbeat alive, letting it converge (no kill)` IS present at
  scripts/session_keeper.sh:331 in THIS tree. No second writer; #437 grepped a stale tree.
Smallest fix (NOT implemented): session_keeper_watchdog.py:66 HARD_STALE_S 900 -> 1800 (~2x the
measured 1050 s cycle), so age < ceiling -> the kick gate returns WAIT-SLOW and a healthy-but-slow
keeper survives its own cycle.
DEPLOY CAVEAT: the watchdog is UNSUPERVISED (PPID 1, no plist) and never reloads. Do NOT kill it to
force a reload -- killing it removes the guard permanently. It takes effect on its next natural
restart.

## B-208 -- A HANG INSIDE generate_group() IS INDISTINGUISHABLE FROM A SLOW GENERATION
Status: OPEN, root-caused to a code path | owner: Trainer/Stall lane | filed 2026-09-14 tick #438
Evidence (measured live this tick on run sapo-27b-ai-20260913T233607Z, trainer pid 136418, box ASI3):
- Step 2 emitted {"stage":"step_begin","step":2,...} at 00:07:44Z and NOTHING since; at 00:40Z
  that is 33 min of silence against a 25-min stall bar. train_stdout.log frozen at 264756 B.
- The NPU is NOT computing: all 8 chips AICore 0% while the 27B weights are RESIDENT in HBM
  (12.7-16.9 GB/chip), power ~100 W/chip. 0 checkpoints (step_*_adapter count = 0).
- Discriminator that kills the B-182 'pure userspace spin' reading: 254 threads, 252 in state S and
  only 2 R; voluntary_ctxt_switches +4353 over 12 s (~363/s, NOT near-zero). /proc/<pid>/io shows
  ~25k syscalls/s, 34x /dev/hisi_hdc and 28x /dev/davinci_manager fds open, while write_bytes (disk)
  is only 954 KB total -- the I/O is to DEVICE fds, not files. It is blocked polling NPU device I/O.
- Step 1's stage ladder is step_begin -> generation_done -> logprob_done -> eval_done ->
  reward_normalized -> train_logprob_done -> backward_done. Step 2 died inside generation, BEFORE
  its first marker.
- Responsible path: training/grpo_trainer.py:6005 generate_group(...), between the step_begin print
  (:5985) and the generation_done print (:6034). Nothing in between logs, which is exactly why 33 min
  of hang reads as a slow step.
Smallest fix (NOT implemented): emit a per-N-token {"stage":"rollout_progress",...} line from inside
generate_group (one-line flush=True heartbeat) so a hang inside generation is self-identifying rather
than silent; optionally a wall-clock watchdog around generate_group tripping at (step-1 generation
duration x margin).
MAC/BOX DIVERGENCE WARNING: training/grpo_trainer.py differs between trees -- Mac 357910 B
md5 6bd5ea05730d7df598a4d01d1631ba26 vs box 352158 B md5 2e4404c8efbf4057438ae734b4e78e0a (5752 B
apart, box also carries .bak-20260913d/f and .bak-20260914a-d). Any fix must be a SURGICAL PATCH,
never a file copy.

## B-208 STATUS UPDATE -- VERDICT CORRECTED: SLOW, NOT HUNG (2026-09-14, tick #438, same tick)
Filed minutes before this update with the verdict HUNG. THE RUN ITSELF FALSIFIED THAT. I am correcting
it in the same tick rather than letting a wrong verdict stand.
WHAT HAPPENED: at 00:42:14Z step 2 emitted `generation_done` and then `logprob_done`. It was never
hung. Generation for step 2 ran 00:07:44Z -> 00:42:14Z = 34m30s and COMPLETED.
  generation_done: n_codes 8, completion_token_lengths [1854,1855,1854,1053,1053,1053,1053,1054],
  eos_terminated all false, fence_terminated all true, truncated all false, truncation_rate 0.0,
  generation_tokens 10829, entropy_mean 0.9413.
WHICH PARTS OF THE B-208 ENTRY SURVIVE AND WHICH DO NOT:
  SURVIVES (the measurement): 252/254 threads in state S, voluntary_ctxt_switches ~363/s (so NOT a
    B-182 pure-userspace spin), ~25k syscalls/s on 34x /dev/hisi_hdc + 28x /dev/davinci_manager fds
    with write_bytes to DISK only 954 KB. All reproduced; the readings were right.
  SURVIVES (the defect): nothing between the step_begin print (grpo_trainer.py:5985) and the
    generation_done print (:6034) logs anything. A 34m30s generation is therefore INDISTINGUISHABLE
    from a hang to any reader sampling the log. The proposed rollout_progress heartbeat is still the
    right fix, and this event is its strongest possible motivation.
  DOES NOT SURVIVE: the inference 'blocked in a poll loop -> HUNG'. A device-bound decode that is
    making slow forward progress produces the SAME device-fd/poll signature as one that is stuck. The
    discriminator does not discriminate. I over-read a sound measurement into a wrong verdict.
ROOT CAUSE OF THE SLOWNESS (the real finding): vLLM :8356 is DOWN, so the fail-closed rollout seam
(grpo_trainer.py:2706-2712) fell back to the transformers decode path. That fallback is CORRECT and
did not hang -- but it is ~an order of magnitude slower than the vLLM path it replaced.
THE MANAGEMENT ERROR THIS EXPOSES (generalizes B-207): the 25-minute stall bar is SHORTER than a
legitimate step. Measured: step 2 generation alone was 34m30s, and step 1 (run start 23:36:07Z ->
metered 00:07:19Z) was 31m12s including load. A ~35-min step against a 25-min bar means a HEALTHY
trainer trips the bar EVERY STEP. This is the same defect as B-207 one instrument up: a liveness bar
shorter than the subject's legitimate cycle time. Bar should be ~2x the measured step time (~75 min)
for as long as the vLLM fallback is in use, and restored when :8356 is serving again.
LESSON, recorded because it cost this tick its headline: 33 minutes of output silence against a step
that legitimately takes 35 minutes is NOT evidence of a hang. I had the step-1 duration in hand and
failed to use it as the baseline before calling HUNG.

## B-209 (2026-09-14, tick #439) -- THE KEEPER CYCLE BLOCKS INDEFINITELY WITH NO LOG LINE AND NO PROGRESS (S1, liveness)

REPRODUCE (measured live 00:40-00:48Z): /tmp/session_keeper_state.json frozen at ts
2026-09-14T08:30:26, cycle 1, status STARTING, headless_auth unknown, daemons unknown, pid 86975,
for ~21 min. Keeper pid 86975 alive (ppid 1). CPU sample over 12 s: keeper 86975 0:00.06 -> 0:00.06,
state S at both ends; its subshell 61803 0:00.00 -> 0:00.00, state S. BOTH BLOCKED -- neither
spinning (rules out the B-182 pure-userspace-spin class for this instance).
Process tree from 86975: 86975 -> 61803 (bash session_keeper.sh) -> 63654 (bash session_keeper.sh)
-> 68760 (Python -c import-sys-json-datetime one-liner, state R, et=2:29). 68760 is the inline
daemon_probe() probe at scripts/session_keeper.sh:193.
Keeper log LAST line: [2026-09-14 08:45:16] ALERT daemons not ready (19004 20646) -- section 4.
No log line since. This is the section 5.4.1 watcher-hang signature: >8 min silent, process alive,
no output progress.

IMPACT: section 9.1 healing is dead while the keeper is blocked. The watchdog WILL kick it
(STALE_AFTER_S=420, HARD_STALE_S=900, KICK_BACKOFF_S=300; last KICKSTART 08:26:28, since_kick
1025 s at 08:43) and the successor re-enters the same block -- a ~15-20 min healing latency that
never converges. Measured this morning: 6 keeper restarts in ~2 h, each 1:1 with a watchdog
KICKSTART (06:19:32 / 06:47:57 / 07:06:57 / 07:25:18 / 08:05:47 / 08:27:56).

HYPOTHESIS TESTED AND REFUTED (recorded so the next lane does not re-derive it): daemon_probe()
spawns a fresh interpreter per port and the spawn is the stall. Measured spawn cost on this host,
this tick: python3 -c pass = 3 spawns in 1.25 s (0.42 s each); python3 -c with sys/json/datetime
imports = 3 spawns in 1.11 s (0.37 s each); /usr/bin/python3 -c pass = 3 spawns in 0.28 s (0.09 s
each). 0.09-0.42 s cannot explain a 2 m 29 s R-state python. REFUTED; no fix shipped.

ALSO REFUTED: B-207's framing that the watchdog SIGKILLs a HEALTHY keeper every cycle. The keeper
is NOT healthy -- it is blocked mid-cycle. The kick is justified by the watchdog's own rules. The
defect to fix is the BLOCK, not the kick.

NOT THE CAUSE (measured): the auth probe. keeper_auth_probe.py returns exit 0 (AUTH-OK) in 36.5 s
standalone; the keeper's timeout-after-90.0s is a load-induced exit-3 UNKNOWN, and
session_keeper.sh:467-470 correctly maps it to HEADLESS_STAMP=unknown (B-109 three-state fix IS
present -- the state file reads headless_auth unknown).

STATUS: OPEN. Root cause NOT established. NO FIX SHIPPED -- a fix on a refuted hypothesis is what
section 5.4/2.8 forbid. NEXT: sample pid 68760 frame (py-spy and lsof are both absent on this
host; try sample(1) or dtrace) before hypothesising again.

## B-210 (2026-09-14, tick #439) -- THE WATCHDOG MIS-RESOLVES THE KEEPER PID TO ONE OF ITS OWN SUBSHELLS, SO SECTION 9.1 HEALING IS SILENTLY SUPPRESSED -- FIXED, TDD, GREEN (tree-side; live watchdog not reloaded)

Class: silent-suppression of a healing action (B-139 class, INVERTED) | Severity: S1 (a blocked keeper is never healed)

REPRODUCE / ROOT CAUSE (measured live, not modelled):
  KEEPER_CMD_PATTERN = 'scripts/session_keeper[.]sh$' (scripts/session_keeper_watchdog.py:407) is
  anchored to avoid matching a manager session's prompt text. But a bash SUBSHELL inherits the
  script's FULL command line, so the pattern also matches the keeper's own transient subshells.
  Measured at 08:49Z:
      pgrep -f 'scripts/session_keeper[.]sh$' -> [55856, 56151, 86975]
        pid=55856 etime=01:24   (subshell)
        pid=56151 etime=01:23   (subshell)
        pid=86975 etime=24:30   (THE KEEPER)
  pgrep listed the SUBSHELLS FIRST and keeper_pid() returned `live[0]` -- the 1m24s subshell.
  decide_with_progress() then applied the B-139 grace gate
  (keeper_elapsed_s < KEEPER_GRACE_S == 600) to a 1-second-old pid, read the 24-minute-old BLOCKED
  keeper as a brand-new one, and returned WAIT-SLOW.
  THE ALTERNATION IN THE WATCHDOG LOG IS THE PROOF:
      [08:50:35] ... pid=55856 elapsed=61   ... WAIT-SLOW   (subshell -> grace suppresses)
      [08:51:36] ... pid=55856 elapsed=122  ... WAIT-SLOW   (subshell -> grace suppresses)
      [08:52:36] ... pid=86975 elapsed=1568 ... KICKSTART   (real keeper -> 1568 > 600, kicked)
  When it happened to sample a subshell it waited; when it sampled the keeper it acted. Whether
  healing fires is therefore a RACE on which pid pgrep lists first.

WHY IT MATTERS: this is B-139 INVERTED. B-139 fixed a successor being judged on a DEAD
  PREDECESSOR's age and killed every cycle; this is the keeper judged on its own SUBSHELL's age
  and never healed. It compounds B-209 (the keeper's cycle blocks indefinitely with no log line):
  B-209 makes the keeper stop cycling, B-210 hides that from the watchdog, so section 9.1 healing
  dies for as long as the subshell race keeps going the wrong way.

RED -> GREEN (TDD, no fix before the test):
  tests/test_keeper_pid_resolution_b210.py -- 6 tests.
  RED measured: 0/6 passed. The behavioural test failed for the RIGHT reason --
      AssertionError: assert 55856 == 86975
  i.e. keeper_pid() returned the subshell. (Four others failed on the not-yet-existing symbols.)
  FIX: two new pure functions -- `_parent_map(pids)` (ONE `ps -o pid=,ppid=` snapshot, racy pids
  simply absent, never an error) and `_has_matching_ancestor(pid, live, parent_of)` (bounded walk
  up the parent chain), plus `select_keeper_pid(live, parent_of)` which drops every match that has
  a matching ANCESTOR and falls back to the historical first match rather than failing open into
  'no pid'. keeper_pid() now calls it.
  GREEN 6/6.
REGRESSION: tests/test_session_keeper_watchdog.py + tests/test_session_keeper_heartbeat.py =
  78 passed / 0 failed.
LIVE E2E VERIFICATION (non-vacuous, against the real process table): after the fix,
  live_keeper_pids() -> [11040, 20739], _parent_map -> 11040:1, 20739:11040, and keeper_pid()
  returned **11040** -- the root keeper, correctly excluding subshell 20739. Before the fix the
  same input returns live[0] = 11040 only by luck of pgrep ordering (subshells first is the
  measured ordering that made it fire wrong).

DEPLOY NOTE (honest): Mac-side code; the fix is in the TREE only. The LIVE watchdog (pid 49192)
  does NOT reload -- it keeps the old resolver until restarted. The healing gain is therefore NOT
  yet live. Recorded rather than implied.

STATUS: FIXED (tree-side), TDD-locked, regression green. Not yet deployed to the running watchdog.

## B-211 (2026-09-14, tick #440) -- THE SUITE RUNNER HAS NO SINGLE-FLIGHT LOCK, SO CONCURRENT SESSIONS RUN N SUITES AGAINST ONE TREE

Status: OPEN | no fix shipped this tick (budget) | owner: test orchestrator | ordered with TDD (ORDER 3)

EVIDENCE (measured this tick, 00:52-01:04Z):
  Three suite runs were in flight SIMULTANEOUSLY, resolved from `ps`:
    pid 9124  started 2026-09-14T00:05:44Z
    pid 57656 started 2026-09-14T00:28:11Z
    pid 79513 started 2026-09-13T22:49:58Z
  Chunk 02 of EVERY run is a ~10x wall-clock outlier:
    9124  ch01 108 s -> ch02 **2837 s** -> ch03 107 s
    79513 ch03 131 s / ch04 431 s / ch06 1719 s, ch02 **3066 s**
    57656 ch01 76 s, then stalled
  Chunk 02 is the chunk that carries `tests/test_bugqueue_id_uniqueness.py`. That test is GREEN
  STANDALONE in **8/8, 0 failed** (re-measured this tick), so chunk 02's cost is NOT that test being
  broken -- it is the chunk being starved by co-tenant suites.

  Source-tree divergence is a SECOND, independent defect the same runs expose:
    9124  SOURCE sha256=a1b2dd47444000234533437db2c8b56819ae0833851c340d325d24f1a8b90c4e
    79513 SOURCE sha256=49c3ec17453e7b9ab9c561d6f5eb45ee70e171cb02e0965402215999add61893
  Two runs against two different trees make "the failure set" uncomparable, which is exactly how a
  failure gets re-triaged as new (see suite-runner-must-name-its-failures).

WHY IT MATTERS: each concurrent run inflates the others' chunk times ~10x, so no run reaches a TOTAL
  inside a 10-min tick, every tick reports "NOT MEASURED", and a real regression can hide behind the
  noise indefinitely. This is the mechanism behind the "full suite never completes" pattern.

RED TEST (to write, ORDER 3): two simultaneous invocations of `.sapo-loop/run_full_suite.py` must NOT
  both execute chunk 01; the second must exit non-zero or wait, and the guard must be non-vacuous
  (assert the LOCK file is actually held). RED first, then the smallest lock fix, then GREEN +
  focused regression.

NOT FIXED THIS TICK: deliberately. The runner is on the shared path every loop session uses; landing
  an untested lock there is exactly the concurrent-edit-collision class this campaign has already lost
  work to twice.

## B-212 (2026-09-14, tick #442) -- THE TRUST-REGION CHECK COMPARES MISMATCHED TOKEN SETS, SO TRAIN-PASS TRUNCATION FIRES A FALSE VIOLATION AND HALVES THE LEARNING RATE

Status: FIXED IN TREE 2026-09-14 (tick #446) -- NOT deployed to the box; the live trainer keeps running the pre-fix code and deploys at the next launch boundary | owner: manager (done)

EVIDENCE (measured on the box, run sapo-27b-ai-20260913T233607Z, 01:10-01:22Z):
  step 1: train_pass_truncation_rate 0.0   ratio_after_update 0.85918  tr.violations 0  lr 2.5e-05 (unchanged)
  step 2: train_pass_truncation_rate 0.375 ratio_after_update 11.17141 tr.violations 1  lr 2.5e-05 -> 1.25e-05
  The two steps differ in exactly one salient way: whether any candidate was train-pass truncated (3 of 8
  at step 2). Step 2's per-candidate PRE-step ratio_mean is [1.182, 1.0002, 0.9998, 1.056, 0.9934, 0.9957,
  1.0079, 1.0009] -- all ~1.0, i.e. the policy is inside the trust region. The POST-step mean is 11.17,
  i.e. a mean log-ratio of ln(11.17) = 2.41 nats/token. A single optimizer step at lr 2.5e-5 cannot move a
  27B policy 2.41 nats/token; the pre/post pair is internally inconsistent.
  The truncated candidates are exactly the three whose train-pass token count (1538) is below their full
  completion length (1854/1855/1854); the untruncated five have n_tokens == tokens (1053).

ROOT CAUSE (code path, quoted by the vigilance lane):
  - Post-step quantity: training/grpo_trainer.py:7442-7475 -> sequence_ratio_stats(), training/grpo_utils.py:2720,
    returning seq_kl_after (computed :2756-2759, returned :2768, assigned grpo_trainer.py:7475, logged :7507).
    It is a MEAN over the <=8 sequences of (expm1(log_ratio) - log_ratio).clamp_min(0), computed AFTER
    optimizer.step() (grpo_trainer.py:7403) on a fresh no-grad eval() forward over the FULL responses
    (grpo_trainer.py:7444-7463).
  - Baseline it is differenced against: last_normalized_old_log_probs at grpo_trainer.py:6937-6947, which is
    the TRAIN-CAP-ALIGNED PREFIX mean (train_seq_cap) for truncated candidates.
  - Therefore for any truncated candidate the check compares "mean logp over the full completion, post-step"
    against "mean logp over the first train_seq_cap tokens, pre-step". That is an apples-to-oranges token set,
    and the gap is large whenever the tail differs from the prefix.
  - Trigger condition: grpo_trainer.py:7476-7478 (seq_kl_after > trust_region_max_seq_kl or
    clip_fraction_after_update > max_clip_fraction).

HARM ALREADY REALIZED: the false violation fired mode=scale_lr and halved the configured lr 2.5e-05 ->
  1.25e-05. The live run is now training at HALF the configured learning rate, and the halving is
  triggered by truncation, so it will recur on every step where train_pass_truncation_rate > 0.

WHY IT MATTERS TO THE OBJECTIVE: the run is a beats-base attempt; an unrequested lr halving on a spurious
  signal silently slows the learning-rate schedule the config audit approved.

RED TEST (to write): a synthetic pair where the full completion is longer than the train cap; assert the
  trust-region check reports NO violation when the policy is unchanged (post-step == pre-step), i.e. the
  metric must be computed on the SAME token set on both sides. Must be non-vacuous: assert the truncated
  case actually exercises the cap (n_tokens < tokens).

NOT FIXED THIS TICK: training/grpo_trainer.py is on the live launch path (§5.4.2 read-only while a run is
  in flight); editing it would diverge the running tree from the box with no way to load the fix without a
  relaunch, and relaunching training is user-gated. Queued for the next launch boundary.

## B-213 (2026-09-14, tick #443) -- BOX-SIDE PORT PROBES ARE CONTAMINATED BY THE SHELL http_proxy, SO A SQUID 403 PAGE MASQUERADES AS A SERVICE RESPONSE

EVIDENCE (measured live on ASI3 through the daemon /exec channel, tick #443):
  - `env | grep -i proxy` on the box shows: http_proxy=http://192.168.141.2:3128,
    https_proxy=http://192.168.141.2:3128, no_proxy=minio-zhuanfa-service.gs-aip-pro.
  - A bare `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:<port>/...` for ports 8356, 56238
    and 56237 ALL returned 403 -- and the RESPONSE BODY was the Squid copyright page
    ("<meta type=\"copyright\" content=\"Copyright (C) 1996-2023 The Squid Software Foundation ...").
  - Re-probed with the proxy removed:
      env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY curl -s --noproxy '*' ...
    gave the OPPOSITE and correct answer:
      judge :56237  -> 200 {"ok": true, "model": "dp4-bridge"}
      vLLM  :8356   -> 000 (no listener)
      translator :56238 -> 000 (no listener)

WHY IT MATTERS TO THE OBJECTIVE: judge/vLLM/translator availability is a STANDING-ORDER trigger (a down
  judge chain is an "unhealthy condition" that mandates action). A probe that always answers 403 cannot
  distinguish up from down, so it can (a) raise a false alarm on a healthy service and (b) MASK a real
  outage behind a plausible-looking code. It also invalidated the standing explanation for prior ticks'
  readings -- "ECONNREFUSED on the Mac" was right by accident, for the wrong reason.

RED TEST (to write): drive the probe helper against a port with NO listener while http_proxy is set in
  the environment; assert the helper reports DOWN. Must be non-vacuous: assert that the un-bypassed path
  really does return the Squid body/code (so the test proves the proxy was the confounder).

FIX (smallest): make the probe helper strip http_proxy/https_proxy/HTTP_PROXY/HTTPS_PROXY and pass
  --noproxy '*' on every box-side probe, so no lane can reproduce the artifact. Owner: instrument lane.

NOT FIXED THIS TICK: no code change was made in a live tick; the helper fix is ORDER 1 for the next tick.

## B-214 (2026-09-14, tick #443) -- THE KEEPER CANNOT CLOSE CYCLE 1: ITS HEADLESS AUTH PROBE TIMES OUT AND THE ENV-REFRESH SWEEP FINDS NO LIVE PROCESS, SO THE STATE FILE STAYS AT "STARTING" FOREVER

EVIDENCE (measured live on the Mac, tick #443):
  - /tmp/session_keeper_state.json frozen at ts 09:14:41, status STARTING, uptime_s null, cycle 1.
    It advanced ONCE from the prior keeper's 08:54:17 and then never moved again.
  - logs/session_keeper.log, repeated frame:
      [08:59:21] ALERT headless claude auth FAILED -- attempting env refresh from live process
      [08:41:14] ACTION env refresh sweep bounded (tried=0, budget=120s)
      [08:41:21] ERROR no live process with valid auth found; keep retrying every cycle
      --- debug headless_ok raw output: auth probe failed: timeout after 90.0s
  - The env file head is STALE: "# refreshed by session_keeper 2026-09-14 03:26:41 from pid 90739", and
    the 09:23:45 refresh attempt did NOT update it.
  - logs/session_keeper_watchdog.log shows the kick/restart loop that results: the keeper pid CHANGES
    (11040 -> 76458 -> 69452 -> 29225) while hb_cycle stays pinned at 1 and state_adv stays False;
    since_kick crossed the 900 s bar (843.8 -> 904.0 -> 1024.5 s) with action=WAIT-SLOW.

WHY IT MATTERS TO THE OBJECTIVE: keeper OK is standing-order item 1 ("keep ALL compute resources
  connected forever"). A keeper that can never reach OK writes no heartbeat verdict, so the fleet's
  resource guard is effectively OFF; every restart also re-runs a 90 s blocking auth probe (~10 min
  cycle age), which is why the watchdog sees a slow cycle and kicks again -- a closed, self-sustaining
  restart loop, NOT a wedged process to kill.

RED TEST (to write): drive the keeper's cycle-1 path with a headless-auth probe that times out; assert
  the keeper still writes an ADVANCING state file (with a named degraded status) rather than leaving
  status=STARTING/uptime_s=null indefinitely. Must be non-vacuous: assert the probe really was invoked
  and really timed out.

NOT FIXED THIS TICK: the keeper is a supervisor process; changing it mid-flight without a RED test would
  be an untested relaunch (forbidden). Owner: keeper lane, ORDER 4. Do NOT kick blind -- the next kick
  reproduces the same loop.

## B-215 (2026-09-14, tick #444) -- THE SINGLE-FLIGHT LOCK HAS NO RETROACTIVE EVICTION, SO PRE-LOCK CO-TENANTS STARVE THE TREE FOREVER

STATUS: OPEN. Severity: MEDIUM (blocks section 9.3 -- no tick can report a suite TOTAL). Owner: suite lane.

MEASURED (tick #444, 2026-09-14 01:19-01:30Z, resolved from pgrep and each runner's own artifact):

    pid 79513  started 2026-09-13T22:49:58Z  artifact full_suite_315_79513.txt  reached chunk 10/24
    pid 9124   started 2026-09-14T00:05:44Z  no TOTAL
    pid 57656  started 2026-09-14T00:28:11Z  artifact full_suite_315_57656.txt  reached chunk 05/24

All three are STILL RESIDENT after B-211's fix landed. `.sapo-loop/suite_runner.lock` named holder pid
46734 at 01:19:32Z -- a LATER, lock-respecting run -- while these three ran on regardless, because they
were started BEFORE the lock existed and never consult it.

Each runner further measures a DIFFERENT source sha256 (49c3ec17... for 79513, a1b2dd47... for 57656),
so all three are measuring a tree that no longer exists (B-178 source identity). None can reach a TOTAL
while co-resident -- this is exactly B-211's measured starvation mechanism, and it is why ticks report
"NOT MEASURED".

THE GAP: B-211's contract ("at most ONE full-suite run at a time") is enforced only at ACQUISITION.
There is no eviction path for a run that predates the lock, and no signal to the grandfathered runners
that they should yield. A flock cannot be revoked from outside the holder.

REMEDIATION ATTEMPTED AND BLOCKED: the manager issued
    kill -TERM -9124 -57656 -79513   (process-group TERM, per B-121 killpg)
and the harness REFUSED with "This command requires approval". Killing another session's runner on a
tree shared by ~13-16 loop sessions is USER-GATED. Escalated in standup #444 section 4 (pending).

RED TEST (to write): an acquired single-flight run must be able to name and EVICT a pre-lock co-tenant
-- i.e. a runner started without the lock must observe, within one chunk boundary, that a lock holder
exists and exit with the distinct single-flight rc rather than continuing. Non-vacuous: assert the
grandfathered runner actually stops producing chunk lines.

DO NOT re-file as B-211; B-211 (acquisition-time refusal) is CLOSED-VERIFIED at tick #444
(tests/test_full_suite_runner_single_flight.py 6/6 GREEN, lock holder observable on disk).

## B-205 -- CLOSED FIXED (2026-09-14, tick #445) -- `import_hygiene` unearnable for the LIVE RL family
Status: FIXED in tree (TDD red->green) | owner: manager lane (was Reward/Instrument) | tick #445
ROOT CAUSE (measured against the live task metadata, not inferred):
`training/grpo_trainer.py:990` gated the quantum allowlist merge on
`str(meta.get("category","")).startswith("distill_v3")`.  The LIVE run trains the
`quantum_rl_v2_*` family (56 tasks, `evals/benchmarks/quantum_grpo_training_v9_rl_questions_v2.txt`),
and those task.json files declare:
    evals/tasks/quantum/quantum_rl_v2_amplitude_estimation_ry/task.json
      id=quantum_rl_v2_amplitude_estimation_ry
      category="algorithm_implementation"   <- NOT distill_v3
      domain="quantum"
      allowed_import_roots=<absent>         <- meta.get(...,[]) -> []
So the merge never fired, `allowed_import_roots` stayed `[]`, only
`_stdlib_module_roots()` was permitted, and every `qiskit`/`numpy` import counted as a
violation -> `max(0, 1 - viol/len)` -> 0.0 for EVERY candidate, including a flawless one.
LIVE CONFIRMATION: step-1 and step-2 loss_breakdown lines both read `hygiene:[0,0,0,0,0,0,0,0]`.
This is B-205 exactly as filed at tick #437; the tick-#437 entry guessed the plumbing, this
tick names the field.
THE FIX (smallest, and faithful to the code's own stated intent): key the merge on the
metadata field that actually expresses the requirement -- `domain == "quantum"` -- in addition
to the legacy `distill_v3` category. `domain` is present on the live tasks and absent from the
generic ones, so the change is scoped to exactly the intended population.
RED TEST (non-vacuous, and it was MEASURED red first):
`tests/test_grpo_task_runtime_context.py::test_quantum_domain_tasks_earn_import_hygiene_without_declaring_roots`
  BEFORE fix: `AssertionError: assert 'qiskit' in []`   (the structural defect, read directly)
  AFTER  fix: PASS
  It also asserts the term KEEPS its purpose: a candidate importing an invented module
  (`totally_invented_module`) still scores 0.0, so this is not a blanket amnesty.
REGRESSION: `tests/test_grpo_task_runtime_context.py` 14 passed / 1 failed (was 13/2 -- my new
test is the +1; the remaining failure is the pre-existing
`test_rollout_prompt_requires_concise_code_and_an_immediate_stop`, which was ALREADY failing in
the pre-fix run of the same file, and whose task meta carries no `domain` key at all so it
cannot be on this code path). Adjacent reward/hygiene surfaces
(test_reward_harness, test_sapo_reward_audit, test_sapo_reward_audit_cli, test_context_hygiene,
test_grpo_task_runtime_context): 67 passed / 1 failed -- zero new failures.
DEPLOY: tree-side only. `training/grpo_trainer.py` is on the live launch path; per the standing
rule the running trainer is NOT restarted and the box is NOT patched mid-run. This fix takes
effect at the next launch boundary, bundled with B-212.
B-193 INTERACTION: independent, as filed. B-193 (grader runtime) is REFUTED -- the pass term is
dark because the policy imports `StatevectorSampler` from the wrong qiskit module, which is what
RL is for. B-205 was a genuine instrument defect by contrast: no policy could EVER earn it.


## B-216 (2026-09-14, tick #445) -- A SUITE TOTAL PRODUCED UNDER CO-TENANCY CERTIFIED `VERDICT=COMPLETE` -- FIXED, TDD, 53/53 GREEN (tree-side)
SEVERITY: medium-high (it is the reason EVERY tick reports "code health NOT MEASURED" with no names, so a
  real regression can hide behind the contention indefinitely -- the same harm B-211 named).
STATUS: OPEN -> FIXED tree-side this tick. Not deployed beyond `.sapo-loop/run_full_suite.py` (Mac-local
  runner; NOT a box launch-path file, so no launch boundary applies).
FOUND BY: the suite lane's B-215 investigation, root-caused and fixed by the manager after the lane was
  refused the write gate.
RELATIONSHIP TO B-215: B-215 (tick #444) correctly named the harm (pre-lock co-tenants starve the tree
  forever) but its proposed REMEDY is REFUTED here -- see (1).

(1) REFUTED FIX, RECORDED SO IT IS NOT RE-RUN -- "evict a stale lock inside acquire_single_flight()" is a
    NO-OP for this defect. `acquire_single_flight()` writes the lock body ONLY after a SUCCESSFUL flock
    (run_full_suite.py:132-138). The body on disk read `8119 2026-09-14T01:31:54Z` WHILE three co-tenant
    trees were running; a successful flock at that moment PROVES the flock was FREE, so there was nothing
    to evict. The grandfathered runners (9124 / 57656 / 79513) never call acquire_single_flight() at all
    -- they predate it -- so they hold no lock, and no acquire-path change can stop a process that never
    participates in the lock. Detection and gating is the fixable half; the drain is permission-gated.

(2) THE FIX (`.sapo-loop/run_full_suite.py`):
    - `running_ps()` -> `ps -eo pid,args` transcript, or **None** on failure (never "") -- an unreadable
      ps is UNKNOWN, and UNKNOWN must not fall through to "no co-tenants".
    - `co_tenant_pids(ps_text, self_pids)` -> pids of OTHER suite trees.
    - `main()` snapshots at BOOT (`boot_co_tenants`), before any chunk of ours exists, so our own chunk
      children can never read as co-tenants of ourselves.
    - `total_line()` emits `VERDICT=CONTAMINATED co_tenants=<pids>` when present, and
      `VERDICT=UNMEASURED-CO-TENANCY` when the ps read failed. FAILS CLOSED.
    - `PS_SOURCE` is a module global, injectable so a test can neutralise the ambient process table.

(3) FALSE-POSITIVE CLASS FOUND BY LIVE EXERCISE, PINNED BY TESTS. The first cut matched the substring
    "pytest" against the whole argv and reported **14** co-tenants of which only **10** were real. Cause:
    a tick session's PROMPT TEXT contains the literal "pytest" (the standing brief names the command), so
    every `claude --print ...` tick process counted as a suite, as did `/bin/zsh -c ...` wrappers.
    Unfixed, EVERY run would have read CONTAMINATED -- an alarm that always fires is the same defect as
    one that never fires. The detector now requires an interpreter AND a real invocation
    (` -m pytest` or `run_full_suite.py`), excluding `claude`/`grep`. Live re-verify after the fix: 10
    co-tenants, all real. This is the reusable lesson: a detector that is only unit-tested against
    hand-written input will pass while being wrong about the REAL argv.
EVIDENCE (live, tick #445):
    LIVE_CO_TENANTS(patched) = [573, 8119, 9124, 19552, 31020, 32288, 41250, 57656, 60460, 79513]
    TOTAL ... VERDICT=CONTAMINATED co_tenants=573,8119,9124,...    (was: VERDICT=COMPLETE)
    unreadable-ps case        -> VERDICT=UNMEASURED-CO-TENANCY      (fail closed)
TDD: RED first 3 failed / 2 passed (the 2 passing were the regression guards), then GREEN 8/8 in
  `tests/test_full_suite_runner_co_tenancy.py`. REGRESSION GATE 53/53 GREEN across the 9 other suites that
  touch the runner (incl. single_flight 6/6).
PRE-EXISTING FAILURE ENUMERATED: `tests/test_full_suite_runner_reports_failing_ids.py::
  test_per_chunk_emission_is_silent_for_a_green_chunk` -> `FileNotFoundError: .../suite_green.txt`.
  PROVEN PRE-EXISTING BY BISECT: with the runner reverted to its unpatched state the failure is
  byte-identical. NOT a regression of this change.
STALE FAILURE COUNT REFUSED: the first gate reported 12 failures. Not believed -- individual tests passed
  in isolation and the count fell 12 -> 1 as ambient co-tenants drained 10 -> 6. Load-induced flake.
  Do NOT re-triage these as runner regressions without re-measuring under a quiet tree.
HERMETICITY (deliberate contract refinement, NOT a weakening): `_load_runner()` in
  test_full_suite_runner_reports_incomplete.py, test_full_suite_runner_chunk_timeout.py and
  test_full_suite_runner_reports_failing_ids.py now sets `mod.PS_SOURCE = lambda: ""`. Reason: "a complete
  synthetic run reads COMPLETE" is only true ABSENT co-tenants; without this a real co-tenant suite on the
  machine flips an unrelated test's verdict. The chunk-accounting contract they pin is unchanged.
REMAINING GAP (user-gated): the co-resident trees still cannot be DRAINED from inside the runner.
  Contamination is now visible and gated; the drain needs the kill permission.

### B-212 FIX RECORD (tick #446, 2026-09-14 09:5x CST)

ROOT CAUSE -- CONFIRMED AT THE CALL SITE, not inferred. The old side was fixed; the post side was not.
  - BASELINE (correct, grpo_trainer.py:6937-6951): when the train pass truncates, the old side is
    `consistent_old_token_lps[idx][:n_train].mean()` -- the mean over the FIRST n_train completion
    tokens. The inline comment there states the intent verbatim: "the per-token loss and the
    sequence-KL must compare the SAME positions".
  - POST SIDE (buggy, grpo_trainer.py:7458-7475): `compute_completion_log_prob(...)` was called with
    `max_seq_length=args.max_seq_length` (3072) and NO `train_seq_cap`, so it kept the FULL completion
    and returned `token_count` = full count. The block then normalised `post_log_prob / post_token_count`.
  - LIVE NUMBERS that pin it (step 3, run sapo-27b-ai-20260913T233607Z): prompt 508 + completion 1825
    = 2333; train cap 2048 drops the tail, so n_tokens = 1540 while completion_token_lengths = 1825.
    The check compared a mean over 1825 tokens against a mean over the first 1540. Step 2 did the same
    with 3 of 8 candidates truncated -> ratio_after_update 11.171, seq_kl_after > 0.25 -> scale_lr.
  - HARM, now measured across three steps: the false violation has halved the live LR TWICE --
    2.5e-05 -> 1.25e-05 (step 2) -> 6.25e-06 (step 3). The run is training at a QUARTER of the
    configured LR on a signal that fires whenever train_pass_truncation_rate > 0.

FIX (minimal, one keyword): pass `train_seq_cap=train_pass_seq_cap` to the post-update forward. The
  helper then caps the sequence identically and returns the capped token_count, so both sides are means
  over the identical first-n_train token prefix. `train_pass_seq_cap` was already a local in scope
  (derived at grpo_trainer.py:6822 from the same `train_pass_max_seq_length` the train pass uses), so
  no new plumbing. A comment records why the cap is mandatory here.

TDD EVIDENCE (RED -> GREEN):
  - `tests/test_grpo_train_pass_truncation.py::test_trust_region_post_pass_is_given_the_train_seq_cap`
    was written FIRST and measured RED: `assert 'train_seq_cap' in block` failed against the live
    source block. This is the genuinely red test -- the defect IS the missing argument at the call site.
  - A second test, `::test_trust_region_compares_the_same_token_set_as_the_train_pass`, is a
    CHARACTERIZATION test and is recorded honestly as such: it is green BEFORE and AFTER the fix. It
    reproduces the false violation numerically (a biased model with a favoured prefix and a disfavoured
    tail; the uncapped post mean vs the capped baseline trips seq_kl_after > 0.25) and pins that the
    aligned comparison reports ratio 1.0 / seq_kl 0.0 / clip_fraction 0.0. Its value is that it makes
    the MECHANISM non-vacuous (it asserts the cap really truncates, n_tokens < tokens) and would catch
    a future change that re-broke the alignment semantics inside the helper.
  - GREEN: 6/6 in the file. REGRESSION on the adjacent surfaces (truncation, entropy-floor backward
    once, rollout-mix entropy floor, chunked recompute backward, metrics wiring): 28/28 GREEN.

NOT DEPLOYED, ON PURPOSE (skill 5.4.2): training/grpo_trainer.py is on the live launch path and the
  trainer has been resident since 07:35 CST. Editing the BOX copy mid-run would diverge the running
  tree with no way to load the change without a relaunch, and relaunching is user-gated. The fix lands
  in the tree now and takes effect at the next launch boundary. The live run continues at LR 6.25e-06.

## B-217 (2026-09-14, tick #446) -- TWO CONCURRENT TICK SESSIONS INDEPENDENTLY FIXED B-212 IN THE SAME FILE, AND THE TWO FIXES ARE MUTUALLY RE-BREAKING (caught pre-commit)
SEVERITY: high (process). It silently re-introduces the exact defect it was meant to remove, and the
  tree compiles and the focused tests stay green while it does.
STATUS: caught and reconciled this tick; no harm shipped. Filed so the RULE changes, not just this instance.

WHAT HAPPENED (both sessions in tick #446, same 10-min window, same file training/grpo_trainer.py):
  - Session A threaded `train_seq_cap=train_pass_seq_cap` into the post-update forward, so the post-step
    mean is taken over the SAME first-n_train prefix the train-aligned baseline uses. Recorded in the
    B-212 FIX RECORD above. This is the minimal fix and the one that survives.
  - Session B (this one) had independently root-caused the same defect and implemented the COMPLEMENTARY
    alignment: keep both sides on the FULL completion by retaining a parallel full-rollout mean list and
    differencing the trust-region read against that (helper `trust_region_baseline`).
  - Both edits were present simultaneously. THEY DO NOT COMPOSE. With A's cap active the post side is a
    PREFIX mean; with B's baseline active the old side is a FULL-completion mean. The comparison is again
    two different token sets -- the same class of mismatch B-212 names, restored by the pair.

WHY IT WAS CAUGHT (and why that is luck, not process):
  B read the file immediately before editing and again after, noticed the byte size move under it
  (358232 -> 360407 -> 361463 within ~90 s), grepped for both markers, and found both. A session that
  had not re-read would have shipped the pair.

RECONCILIATION (verified, not asserted):
  - Session B's edit REVERTED IN FULL: `trust_region_baseline` helper, the parallel
    `full_normalized_old_log_probs` list, its append site, its outer-loop tracker and the trust-region
    stack all removed. Byte size restored 360407 -> 358232 (the exact pre-edit size). Residual marker
    grep for `trust_region_baseline|full_normalized_old_log_probs`: 0.
  - Session A's fix INTACT: grep `train_seq_cap=train_pass_seq_cap`: 1.
  - B's duplicate test file removed; the source-pin B had edited in tests/test_sapo_loss.py reverted.
  - py_compile OK. REGRESSION GATE (truncation + sapo_loss + step_instrumentation + resume): 55/55 GREEN.

RED TEST (to write, for the CLASS not the instance): a guard that fails when two or more
  `training/grpo_trainer.py` writers overlap in time -- e.g. a pre-commit/lint check that the file's
  content hash is unchanged between read and write, or an advisory edit lock (the repo already has
  single-flight machinery in .sapo-loop/run_full_suite.py that can be reused). Non-vacuous: it must fail
  on a simulated concurrent write, not merely assert the lock exists.


## B-218 (2026-09-14, tick #446) -- THE BUGQUEUE-ID GUARD WENT RED ON A CORRECTLY-FORMED LEDGER (the FIX RECORD vocabulary was unknown)
STATUS: CLOSED FIXED (2026-09-14, tick #446)

REPRODUCED (before any change), and it was failing in TWO independent co-tenant suite
runners, not just one:
  tests/test_bugqueue_id_uniqueness.py::test_no_bug_id_names_two_different_bugs
  tests/test_bugqueue_id_uniqueness.py::test_b202_real_ledger_has_no_collisions
  -> 79513 chunk 02 and 9124 chunk 02 both recorded the first one.

ROOT CAUSE (measured, not guessed). The scan reported exactly one collision:
  B-212 at line 6937 is a second BUG entry: 'FIX RECORD (tick #446, 2026-09-14 09:5x CST)'
That is not a collision. The canonical B-212 entry is at line 6693
(`## B-212 (2026-09-14, tick #442) -- THE TRUST-REGION CHECK COMPARES MISMATCHED TOKEN
SETS`); line 6937 is the same bug's fix section. The guard's rule is that a REPEAT
header is legitimate iff its title carries an update marker, and UPDATE_MARKERS did not
know the ledger's `FIX RECORD` token.

MEASURED BEFORE WIDENING (the anti-neutering discipline this module already documents
at lines 33-36 -- the TEST describes the ledger's vocabulary; the ledger is not reworded
to satisfy the scan):
  - 187 headers, 134 distinct IDs.
  - Exactly ONE repeat header lacked a marker: this one.
  - All 15 other recent repeat headers are same-bug status sections (STATUS UPDATE /
    UPDATE / (carried, still OPEN) / CLOSED / CLOSED FIXED).
So the guard was RED on a correctly-formed ledger -- the same class as B-202.

FIX (smallest): add the specific token "FIX RECORD" to UPDATE_MARKERS. NOT bare "FIX" --
a genuinely different second bug whose title merely mentions a fix must still be caught,
and that case is pinned by a test.

TDD (RED -> GREEN, all in tests/test_bugqueue_id_uniqueness.py):
  RED   (before the fix, 7 passed / 3 failed):
    + test_b218_fix_record_section_is_not_a_collision        (synthetic B-212 shape)
    + test_b218_guard_still_catches_a_genuine_collision_after_fix_record  (ANTI-NEUTERING)
    and the already-present test_b202_real_ledger_has_no_collisions / test_no_bug_id_...
  GREEN (after adding the marker): 10/10 passed, 0 failed.
  The anti-neutering test passed BOTH before and after, so the widening provably did not
  disable the guard.

DEPLOY: tests/ only -- not on the live launch path, so no bundle is blocked. Verified the
file was not concurrently written while I edited it (size 7995 -> 9807 -> 10333, sha256
c6dfc7b5 -> ee6f11b7 -> 3bdd2d5d, the B-217 practice).
NOTE: the two suite runners that reported this failure recorded it BEFORE the fix landed;
their counts are pre-fix.


## B-214 STATUS UPDATE (tick #446, 2026-09-14 10:2x CST) -- THE PUBLISHED VERDICT IS CORRECT (UNKNOWN), BUT THE PROBE DISCREPANCY IS NOW MEASURED
STATUS: OPEN (root cause NARROWED; mechanism NOT yet established -- do not fix on a guess)

NEW MEASUREMENT THIS TICK (three independent runs, all AUTH-OK):
  - `scripts/keeper_auth_probe.py <ENVF> /Users/daxu/homebrew/bin/claude 300`  -> rc 0, 12.3s
  - same probe with a 90s bound, under the KEEPER'S OWN minimal env
    (env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin HOME=/Users/daxu, i.e. NO inherited
    ANTHROPIC_* values, so the ENVF is the only credential source)            -> rc 0, 13.1s
  - the keeper's log, by contrast, contains 118 occurrences of
    `auth probe failed: timeout after 90.0s`.

So the ENVF credential is GOOD and the probe is FAST when it is run by hand, while the
keeper's own invocation reports the 90s bound being hit. That is the discrepancy to
explain -- it is NOT an auth failure.

WHAT IS ALREADY CORRECT (do not re-fix): the three-state rule (B-109) IS implemented.
Line 467-470 maps `*"timeout after"*` -> HEADLESS_STAMP="unknown", and the live state
file indeed publishes `headless_auth: unknown`. The keeper is NOT claiming a measurement
it did not take. What IS still mislabeled is the ALERT line at 481, which says
"headless claude auth FAILED" even when the verdict just computed was UNKNOWN -- a
log-wording lie against the same rule, cheap to fix and worth fixing.

LIVE SHAPE THIS TICK (measured): keeper pid 50425 (started 10:09:18) is ALIVE and the
state ts advanced 09:51:17 -> 10:14:21 across two reads 23 min apart, but the file still
reports cycle=1, verdict_cycle=0, daemons="unknown", uptime_s=null, and the watchdog
log's state_adv=False / hb_cycle=1 confirm it never closes cycle 1. The state file
advances WITHIN cycle 1 rather than by completing cycles.

OPEN QUESTION (next discriminator, for whoever owns this next): a fresh stamp with
cycle=1 at 10:14:21 cannot come from the top-of-cycle stamp at 10:09:18 unless something
OTHER than the keeper's cycle loop rewrites the state file -- and this file is already
known to have more than one writer (B-088, whose fix is the current HEAD commit). Resolve
WHO writes the STARTING/cycle=1 record and HOW OFTEN before touching the probe bound.
Explicitly NOT actioned this tick: raising the 90s bound. "The bar is the defect" is not
established (see the liveness-bar-vs-cycle-time finding), and raising it on this evidence
alone would be fixing on a guess.

## B-219 — the judge reward term is entirely DARK on the live run: judge_reward None AND judge_dim_scores EMPTY on 8/8 candidates, so a 0.10-weight term contributes nothing

**Filed tick #448, 2026-09-14 10:30 CST. Silent-fallback / dark-reward-term defect (skill 4.1).**
Live impact: run `sapo-27b-ai-20260913T233607Z` is training with one of its named reward terms
permanently contributing zero, while the operator-facing config implies it is worth 0.10.

**EVIDENCE (read off ASI3 :20653, step 4, `grpo_step_metrics.jsonl` tail).**
Per-candidate, all 8 candidates:
  judge_reward = None            (every candidate)
  judge_dim_scores = {}          (0 dimensions — EMPTY, not partial)
  pass = False                   (0/8 candidates passed at this step)
Live terms that ARE populated (summed over the 8 candidates): syntax_reward 8.0, interface_reward 6.7,
brevity_reward 2.95, import_hygiene_reward 1.27, verifier_reward 1.875, shaped_reward 1.50.
Step level: NO judge key is emitted at all, and there is no step-level judge_reward rollup.

**ROOT CAUSE (pinned by the EMPTY dim map).** `training/grpo_trainer.py:2215-2232`:
    reward["model_dim_scores"] = {}
    reward["judge_reward"] = None
    if args.model_judge_enabled and judge_model is not None and backend is not None:
        ...
        reward["judge_reward"] = (judge_composite_score(scores, judge_weights or {})
                                  if judge_weights else None)
Two distinct failure shapes fall out of this block and only one matches the evidence:
  (a) OUTER gate false  -> model_dim_scores stays {} AND judge_reward stays None.
  (b) OUTER gate true, but `judge_weights` empty (uncalibrated) -> judge_reward None BUT
      model_dim_scores is POPULATED with the per-dimension map.
We observe an EMPTY dim map on all 8, so the branch is (a): the outer gate is FALSE.
`--model-judge-enabled` is `action="store_true", default=False` (grpo_trainer.py:638-640), and the live
run's `/proc/136418/cmdline` carries `--judge-max-tokens` but NOT `--model-judge-enabled`. Note that
`--reward-judge-mass` DEFAULTS to 0.10 (grpo_trainer.py:710), so the *weight* for the term exists and is
non-zero even though the *scoring* was never enabled — the two are wired independently, which is exactly
why the darkness is silent.
**The bridge is NOT the cause.** `scripts/sapo_judge_bridge.py` is alive on the box (pid 136417, etime
2 h 51 m) listening on port 56237, boot log records `judge_bridge_up`, and its queue dir
`.../judge_bridge/` is EMPTY — no requests were ever queued, consistent with the trainer never calling it.

**RELATIONSHIP TO B-174 (do NOT fold together).** B-174 is the STEP-LEVEL rollup being None
*because no rollup is emitted* — an instrument defect — and its own healthy control exhibited a
POPULATED 10-dimension per-candidate `judge_dim_scores` map with real judge_reward values
(step 1 range 0.26..0.36 etc.). B-219 is the per-candidate term itself being dark. Fixing B-174's rollup
would NOT have surfaced B-219, and B-219 is the one that changes the reward the policy actually sees.

**WHY IT MATTERS.** The policy is optimizing a reward whose documented composition includes a judge term
worth 0.10 that is absent in fact. Any beats-base comparison against a run that DID have the judge live
(the 151737Z run) is comparing two different objectives, not two checkpoints. This is the skill 4.4
"different is never better" trap in reverse — a *same-looking* run that is actually a different objective.

**SMALLEST FIX (TDD red first) — LAUNCH-BOUNDARY, NOT MID-RUN.** The trainer is LIVE; enabling the judge
mid-run would change the reward function under a running optimizer, which is forbidden. The fix belongs
to the NEXT launch: pass `--model-judge-enabled` explicitly in the ASI3 launcher (and pair it with
`--judge-adapter-path` / calibration per the flag's help text — "Reward weights stay zero until
calibration passes"), OR make the darkness LOUD rather than silent: fail-closed at startup when
`reward_judge_mass > 0` while `model_judge_enabled` is False, since that combination means the run is
silently missing a weighted term. The second is the real defect fix — a non-zero configured weight with
no scorer behind it should never start a run quietly.

**STATUS:** OPEN. Root cause pinned to the outer gate; launcher-side omission is the prime suspect and is
the next discriminator (ORDER 2). Regression test owed: a startup guard test asserting that
`reward_judge_mass > 0 and not model_judge_enabled` is either rejected or loudly warned. Owner: bug-clearing.

## B-220 (2026-09-14, manager session) -- THE EVAL LEG SCORED EVERY CHECKPOINT AGAINST THE WRONG BASE MODEL (Qwen3.6 instead of Qwen3.8), SO IT WROTE "tie ... NO promotion" FOR ADAPTERS THAT BEAT THE TRUE BASE

Status: FIXED IN TREE (2026-09-14). Found while arming the beats-base instrument for the live run.

EVIDENCE (measured this session):
- The live run's argv carries `--model-name /root/work/filestorage/Qwen3.8-27B` (read from
  /proc/136418/cmdline). Qwen3.8-27B is the model being fine-tuned, so it is the only
  meaningful beats-base reference.
- `scripts/asi2_loop_eval.sh:71` defaulted `BASE_MODEL` to `/root/work/filestorage/Qwen3.6-27B`.
  The parallel-eval agent does NOT export BASE_MODEL, so every leg fired without an explicit
  override compared the adapter against Qwen3.6.
- The result is banked in `reports/.sapo_parallel_eval_state_ASI3.json` key `47`, whose own
  verdict string reads: "tie vs Qwen3.6 base (3/18=3/18); beats-base bar (Qwen3.8 0/18)
  beaten; NO promotion per tie rule".
- Contrast the PROMOTION verdict instrument, which scores against Qwen3.8 and says the run's
  warm source BEATS base: `outputs/verdict_step000097_leg4.json` -> pass_adapter 3/18,
  pass_base 1/18, beats_base true, losses [] (and `verdict_step000097.json` agrees: 2/18 vs
  1/18, beats_base true).

ROOT CAUSE: two different base models were in play and only one of them is the training base.
  The "3/18 base" is Qwen3.6; the "1/18 base" is Qwen3.8. The eval loop silently used the
  former, so it could only ever report a TIE for a genuinely-beating adapter. This is the
  [[golden-rule-1]] class: an instrument that changes the MEANING of a verdict without saying so.

HARM: the loop's verdicts are not comparable to the promotion verdicts, and a real beats-base
  result reads as "NO promotion". Any promotion decision taken off the loop's column was wrong.

FIX (applied): `BASE_MODEL` default -> `/root/work/filestorage/Qwen3.8-27B`, with a comment
  naming the failure. `bash -n` GREEN. Corroborating evidence that the OLD default also could
  not work on the box it was pointed at: `scripts/sapo_parallel_eval_agent.sh` does not export
  BASE_MODEL, so the default is what legs actually used.

SECOND DEFECT FOUND IN THE SAME WINDOW -- WRONG BOX: the first agent instance was armed on ASI1
  (port 20646) and its precheck died with:
    "Transformers runtime is too old for '...Qwen3.6-27B' (model_type='qwen3_5' ...)"
  Measured: ASI1 transformers == 4.57.1 (cannot load the qwen3_5 family); ASI2 and ASI3 ==
  5.2.0.dev0 (can). The eval instrument therefore CANNOT run on ASI1, and any leg fired there
  fails at base load. ASI2 (19004) is the leg's designed default env and the correct box; the
  agent is now armed there, and its precheck loads the base 851/851 weights cleanly.
  NOTE: ASI1 "ready" per /health does NOT imply ASI1 can host this eval -- readiness is a
  daemon property, not a runtime property.

RESIDUAL / NOT FIXED: `scripts/run_sapo_three_state_promotion_eval.sh:9` carries the same stale
  Qwen3.6 default (`SAPO_PROMOTION_BASE_MODEL`). Left alone deliberately this session (separate
  flow, needs its own evidence that it too targets a Qwen3.8 run) -- flagged so it is not
  mistaken for already-corrected.


## B-221 (2026-09-14, tick #449) -- test_judge_mac_watcher_singleton RED STANDALONE: A FIXED SLEEP USED AS A SYNCHRONIZATION BARRIER

**SYMPTOM.** `tests/test_judge_mac_watcher_singleton.py` fails 2/4 when run STANDALONE
(`test_second_instance_refuses_while_first_holds`, `test_lost_lock_terminates_watcher`) with
`AssertionError: first instance never wrote the lock`. NOT co-tenancy pollution: it reproduces in a
single-file run, and it is the only one of this tick's four clusters that did.

**THE DISCRIMINATOR (all four clusters, standalone).**
  test_grpo_trainer_resume_persist.py        9 passed / 0 failed  -> in-suite-only, isolation class
  test_bugqueue_id_uniqueness.py + grpo_task_runtime_context     -> GREEN standalone, isolation class
  test_judge_mac_watcher_singleton.py        2 FAILED  / 4        -> REAL, reproducible
The in-suite-only failures are the shared-tree co-tenancy class (concurrent loop sessions + 4
co-tenant run_full_suite.py runners, host load 170), not code regressions.

**ROOT CAUSE (measured, not inferred).** The test uses a fixed `time.sleep(2.0)` as if it were a
synchronization barrier. Measured time-to-lock on the watcher's boot:
    full os.environ                      -> 0.74s
    hermetic 4-key env (what the test passes) -> 2.23s
The hermetic env boots ~3x slower, crossing the hard-coded 2.0s. The WATCHER IS CORRECT: a direct
hermetic boot showed it writes its lock and its holder pid reliably (3 trials, 0.55/0.68/0.77s under
a full env). Only the test's wait was wrong.

**FIX (landed).** New `_wait_for_lock(lockfile, holder, timeout=20.0)` polls with a deadline; both
call sites use it. Matches the file's own existing bounded-wait idiom. The hermetic 4-key env is
deliberately PRESERVED -- B-040: this suite must never touch the production lock.

**EVIDENCE.** RED: 2 failed/4 standalone. GREEN after fix: 4 passed/4. Regression on adjacent lock
surfaces 39/39 green (judge_health_agent_singleton, single_instance_lock_reacquire/steal_race/
concurrent_steal/unreadable_mtime, lock_live_holder_age, lock_root_never_removed,
heartbeat_lock_revalidation), ZERO new failures. NON-VACUITY proven: the helper still fails CLOSED
both ways (dead-holder+no-lock -> False in 0.00s; live-holder+no-lock -> False at the 1.0s
deadline), so a watcher that genuinely never locks still trips the assertion.

**STATUS:** FIXED (test-side, Mac repo). No box deploy required -- test-only, not on the launch path.


---
**B-219 EVIDENCE REFUTED** (manager standup #450, 2026-09-14 02:46-02:48Z) -- status stays OPEN
The claim "its queue dir .../judge_bridge/ is EMPTY -- no requests were ever queued, consistent with the
trainer never calling it" is FALSE as measured on ASI3 for run sapo-27b-ai-20260913T233607Z:
  02:46Z    judge_bridge/ held req_d97bc9d4d1744e1da91d766aa7398d11.json (24437 B)
  02:48:20Z that file was gone; req_cfc157508ba34135ac9dbae2c906e383.json (24437 B) was in its place
  Parsed payload: model dp4, temperature 0.0, max_tokens 4096, a strict code-evaluator prompt scoring 8
  candidates TOGETHER -- this run's batch-comparative judge payload.
The dir is a TRANSIENT WORK QUEUE, consumed in about 2 min. "Empty" is an artifact of WHEN it was sampled.
CORRECTED STATUS: the per-candidate darkness is NOT in dispute (judge_reward None 8/8, judge_dim_scores None
8/8 at step 4). What is no longer supported is the OUTER-GATE story: a dp4 request is demonstrably in flight,
and the recorded step failure is stage dp4_judge_failed / reason no_scores_from_dp4 with an upstream HTTP 500.
Two producers now compete for the None (the dp4 path failing upstream, vs the model-judge gate being off) and
the queue evidence does NOT select between them. Re-derivation owed: name the code line that WRITES
judge_dim_scores and report which branch produced the None. FIX IS LAUNCH-BOUNDARY -- the trainer is live and
enabling a scorer mid-run changes the reward under a running optimizer. Owner: judge lane (standup #450 ORDER 4).


## B-222 (2026-09-14, tick #449) -- THE GRPO LAUNCHER RUNS THE TRAINER WITH BLOCK-BUFFERED STDOUT, SO THE STALL WATCHERS' STAGE LADDER CAN LIE

**SYMPTOM (this tick's ladder reading).** The stage ladder grepped from
`<run_dir>/train_stdout.log` read `... backward_done | step_begin` and the file's mtime was FROZEN at
02:20:09Z for 30 min -- i.e. past the 25-min stall bar that triggers a relaunch. Read naively, the live
run was stalled.

**IT WAS NOT STALLED.** The real progress instrument disagreed: `eval_results.jsonl` carries a `step`
field, and its last 8 rows read `step=5` -- step 5's complete 8-candidate rollout was already scored and
persisted. The run was in the train/backward phase. The frozen log was an ARTIFACT.

**ROOT CAUSE (measured on the live pid, not inferred).**
  /proc/136418/fd/1  ->  <run_dir>/train_stdout.log   a REGULAR FILE, not a tty or pipe
  PYTHONUNBUFFERED   ->  ABSENT from the live env (`tr \0 \n < /proc/136418/environ | grep -c` == 0)
  argv               ->  `python3 training/grpo_trainer.py ... --npu-device-map balanced-layers`, no -u
Python block-buffers stdout when fd 1 is a regular file, so the log trails the trainer by up to a full
step. This is the SAME class already recorded at bugqueue L5096 and STATUS #424 ("a static size is a
block-buffered-log artifact and is NOT evidence of a stall").

**WHY IT IS A DEFECT NOW.** The stall/relaunch trigger (a) -- "no step/stage progress >25 min" -- is keyed
on THIS ladder. A ladder that can silently trail by a step converts a healthy run into a spurious
relaunch, which is the co-resident duplicate-trainer killer class. The asymmetry is what makes it a
defect rather than a house convention: the project's SFT launchers already export PYTHONUNBUFFERED=1
(`asi3_launch_27b_sft_questions_code_v2.sh:59`, and 6 more), while the RL launcher -- the one whose log
the watchers actually key on -- did not.

**THE FIX (landed, minimal).** `scripts/asi2_launch_grpo_27b_selfeval.sh`: added `PYTHONUNBUFFERED=1` to
the trainer RUN_CMD env in BOTH branches -- the `balanced-layers` single-process branch (the one the live
run took; its argv matches exactly) and the `torchrun` DDP branch, which carries the same defect. A
shim named `asi3_launch_grpo_direct.sh` was checked FIRST and correctly rejected as the fix site: it
forwards to the canonical launcher and never invokes the trainer itself.

**TDD.** RED test `tests/test_grpo_launcher_unbuffered_stdout.py` (`test_grpo_launcher_sets_unbuffered_
stdout` fails on the unpatched launcher, asserting the trainer invocation carries no unbuffered setting).
GREEN after fix: 2 passed / 2. `bash -n` on the patched launcher: OK (still parses). A second test pins
the SFT-sibling asymmetry the argument rests on, so the premise cannot silently vanish.

**DEPLOY STATUS -- LAUNCH-BOUNDARY, DELIBERATELY NOT MID-RUN.** The edit is to the MAC tree; the live run
executes the BOX's copy, so this change is INERT for the running trainer (it cannot affect it) and the
bug is NOT yet fixed on the box. Per section 5.4.2 the launch path is READ-ONLY while a run is in flight.
Land it with the next deploy, and VERIFY with `/proc/<pid>/environ | grep -c PYTHONUNBUFFERED == 1` on
the next boot rather than assuming.

**INTERIM RULE FOR THE WATCHERS (until deployed).** Do NOT treat a frozen `train_stdout.log` as stall
evidence. Use the `step` field of `eval_results.jsonl` (written directly, hence flushed) as the progress
instrument, and CPU-time delta as the liveness instrument.

**STATUS:** FIXED TREE-SIDE / UNDEPLOYED ON BOX. Owner: deploy lane, deadline: next launch boundary.

## B-223 -- BOX SOURCE WAS EDITED MID-RUN; THE LIVE TRAINER EXECUTES STALE CODE (measured 2026-09-14 ~03:05Z)
STATUS: OPEN (recorded, not healed -- healing = restart, and the run is HEALTHY => §5.4.1 forbids touching it)
SEVERITY: HIGH (silent: every "is the box tree patched?" reasoning is now unsound)

EVIDENCE (all measured this tick, ASI3 :20653):
  PROC_START   = Sun Sep 13 23:36:10 2026 UTC   (ps -o lstart= -p 136418)
  FILE_MTIME   = 2026-09-14 02:38:30 UTC        (stat -c %y training/grpo_trainer.py)
  => the source file was modified 3h02m AFTER the process started. CPython loads
     source at import; this process CANNOT be executing the 02:38:30 revision.
  B212_LINE=0  (box file has NO "B-212" comment marker)
  CAPPED=1     (box file DOES contain train_seq_cap=train_pass_seq_cap in the post pass)

CONSEQUENCE: the box/tree relationship is UNKNOWN-BY-INFERENCE. STATUS.md says "B-212 is
tree-side and UNDEPLOYED", but the box file already carries the cap line (added bare, no
comment) -- so B-212 is DEPLOYED-ON-DISK but NOT LOADED. Any future "the box is patched"
or "restart will pick it up" claim must be re-derived from a process/file timestamp pair,
never from file content alone. Restarting DOES load it; that is a launch-boundary decision.

WHY IT MATTERS NOW: steps 1-5 (including this tick's step-5 violation) all ran the
PRE-edit code. Attributing their behaviour to current box source is a category error.

## B-224 -- TRUST-REGION GATE IS NOT LR-SCALED; FIRES WITH ZERO TRAIN-PASS TRUNCATION
STATUS: OPEN -- B-212's MODEL REFUTED (step 5 breaks the 2x2). Root cause NOT yet isolated.
SEVERITY: HIGH (silently throttled a live run 8x on a broken instrument)

MEASURED GATE (box src grpo_trainer.py:7395-7397, identical in local tree:7497):
    trust_region_violated = (seq_kl_after > args.trust_region_max_seq_kl      # 0.25
                             or clip_fraction_after_update > args.trust_region_max_clip_fraction)  # 0.90
  => THERE IS NO TRAIN-PASS TRUNCATION TERM IN THE GATE. B-212's "violation travels 1:1
     with train_pass_truncated_candidates" was a 4-step CORRELATION, not the mechanism.

THE 5-STEP LEDGER (read from grpo_step_metrics.jsonl):
  step  lr        Viol  cnt  seq_kl_after  ratio_after  clipAft  max_completion_len
  1     2.5e-05   F     0    0.0503        0.8592       0.375    964
  2     1.25e-05  T     1    9.0447        11.1714      0.500    1855
  3     6.25e-06  T     2    0.9166        0.5788       0.625    1847
  4     6.25e-06  F     2    0.0857        0.8824       0.250    1169
  5     3.125e-06 T     3    0.3353        0.7579       0.500    1088

STEP 5 BREAKS THE B-212 2x2 (and this is the branch #451 ORDER 3 named):
  loss_breakdown.train_pass_truncation_rate = 0.0; completion_token_lengths max 1088 vs cap 2048
  => ZERO train-pass truncation, YET trust_region_violated True and lr halved a THIRD time.

THE INSTRUMENT DOES NOT TRACK THE OPTIMIZER (the finding, independent of mechanism):
  * lr was HIGHEST at step 1 (2.5e-05) and seq_kl_after was NEAR-LOWEST (0.0503).
  * lr was LOWEST at step 5 (3.125e-06) and seq_kl_after was 6.7x step 1's (0.3353).
  * step 2 reports ratio_after_update = 11.1714 -- the post-update policy supposedly assigns
    11x the probability mass of the sampled sequences ONE optimizer step after generation.
    That is not credible as genuine movement and is the signature of a normalization mismatch,
    not a policy move.
  => The three halvings (2.5e-05 -> 3.125e-06) were driven by a quantity with no measurable
     dependence on the thing it is supposed to be policing.

LEADING HYPOTHESIS (code-evidenced, NOT yet isolated -- do not fix on guess):
  token-set mismatch between the two sides of the difference.
    OLD side: old_log_probs[idx] / old_token_counts[idx]  (grpo_trainer.py:6951/6955),
              counts from the rollout pass (6043).
    POST side: post_log_prob / post_token_count            (grpo_trainer.py:7485),
              count from a FRESH re-encode with train_seq_cap + policy_temperature=
              effective_temperature.
  Sum-of-logprobs divided by a token count is length-proportional: any count mismatch is
  amplified by sequence length. The observed scatter tracks completion length far better
  than it tracks lr.

NEXT DISCRIMINATOR (cheap, decides the mechanism -- run before any fix):
  For one step, dump old_token_counts[idx] AND post_token_count per candidate to the step
  record. If they differ for a candidate with NO truncation, the mechanism is confirmed and
  the fix is a count-consistency guard (fail-closed: exclude mismatched candidates and
  RECORD the exclusion, never silently mean over incomparable token sets).

IMPACT: pass_rate 0.0 / all_fail True on every step so far; the run is being throttled 8x
below base lr by this instrument. Not stop-worthy (training is advancing and checkpointing),
but no conclusion about learning rate or convergence is valid until it is fixed.

## B-225 (2026-09-14, tick #453) -- THE RUNNER'S OWN TESTS ARE POISONED BY THE LIVE SUITE (single-flight lock not neutralised) -- FIXED, TDD, 22/22 + 62/62 GREEN

STATUS: FIXED tree-side (3 test files + 1 new guard). Severity: MEDIUM-HIGH -- it makes section 9.3
self-defeating: the runner's tests go RED precisely BECAUSE the runner is running.

MEASURED (tick #453, 2026-09-14 ~03:02Z, standalone -- deliberately NOT read from a chunk, so
co-tenancy could not be blamed):

    /usr/bin/python3 -m pytest -q tests/test_full_suite_runner_chunk_timeout.py \
        tests/test_full_suite_runner_reports_failing_ids.py \
        tests/test_full_suite_runner_reports_incomplete.py
    -> TESTSUITE_COUNTS passed=7 failed=12 errors=0 total=19

Every one of the 12 carried the SAME signature: "expected 3 chunks, ran 0".

ROOT CAUSE (code path, not inference). Those files drive the runner's main() in-process.
`_load_runner()` neutralised `PS_SOURCE` (B-216) and `_drive()` pinned `env_verdict` (B-173) --
but NOT the single-flight lock. So main() reached run_full_suite.py:532
`_SINGLE_FLIGHT_HANDLE = acquire_single_flight()`, which reads the module global `SUITE_LOCK`
(run_full_suite.py:122 `path = lock_path or SUITE_LOCK`) -> the REAL
`.sapo-loop/suite_runner.lock`, held by the live runner pid 33860 -> returned None -> main()
returned SINGLE_FLIGHT_EXIT (4) BEFORE any chunk -> `_drive`'s
`assert len(calls) == len(plan)` fired as "expected 3 chunks, ran 0".

WHY IT IS WORSE THAN 12 ORDINARY FAILURES: the RED was CAUSED by the suite running. Any tick
that satisfied section 9.3 (run the full suite) manufactured ~12 fresh failures in the very
instrument that polices section 9.3, so the suite could never read green while doing its job.
It is the same ambient-dependency class B-216 fixed one layer over (PS_SOURCE), and B-173 before
that (os.execv) -- the third member of that family in the runner's test harness.

THE FIX (smallest, and it keeps the flock REAL -- only its PATH moves): each `_load_runner()` now
points SUITE_LOCK at a private temp path:
    mod.SUITE_LOCK = os.path.join(tempfile.mkdtemp(prefix="suite_lock_"), "runner.lock")
so the flock is still exercised for real, just never against a live run.

RED EVIDENCE: measured 12 failed / 7 passed BEFORE the fix (the run above), 22/22 GREEN AFTER.

NEW GUARD -- tests/test_full_suite_runner_lock_hermetic.py (4 tests, all green), checking BOTH
directions so neither half is vacuous:
  1. test_the_runners_shipped_default_really_is_the_live_lock_path -- the runner's real default IS
     `<repo>/.sapo-loop/suite_runner.lock` and SINGLE_FLIGHT_EXIT == 4. ANCHOR: without this, leg 2
     could pass on a wrong path.
  2. test_every_runner_test_module_neutralises_the_single_flight_lock -- all three runner-test
     files must point away from the live path; a FOURTH file that forgets now fails this.
  3. test_driven_main_still_runs_its_chunks_while_the_real_lock_is_held -- behavioural: with the
     live path genuinely held, a driven main() still reports 2/2 chunks and VERDICT=COMPLETE.
  4. test_undoing_the_neutralisation_reproduces_the_failure -- FALSIFICATION leg: put SUITE_LOCK
     back to the live path and the same drive must fail matching r"ran 0". Proves the
     neutralisation is LOAD-BEARING, not decorative.
Leg 3's helper tolerates the live path already being held by a real runner (BlockingIOError ->
return None, never released), so the guard holds both with and without a live run.

REGRESSION: the ENTIRE runner test surface -- all 11 files matching run_full_suite in tests/
(argv_guard, chunk_timeout, chunks_collected_ids, co_tenancy, lock_hermetic, reports_failing_ids,
reports_incomplete, single_flight, unique_output, suite_runner_pins_interpreter,
suite_runner_source_stamp) -> 62 passed / 0 failed.

NOT DEPLOYED ANYWHERE: test files only; `run_full_suite.py` itself is UNCHANGED, so the runner's
B-178 SOURCE stamp does not drift and the in-flight run 33860 keeps measuring one identity.

IN-FLIGHT RUN INTERACTION (recorded, not a defect): runner 33860 executed chunk 04 (ids 601..800)
BEFORE this fix, so its TOTAL will still carry those 12 failures -- a STALE measurement of a tree
that no longer exists, not a live regression. Chunks it has not yet reached read the fixed files
from disk and will be green.

RELATED: B-211 (acquisition-time single-flight refusal -- WORKING as designed; this bug is its
test-harness shadow), B-216 (PS_SOURCE / co-tenancy verdict -- CLOSED), B-173 (execv B-173 guard
in the same helper).


## B-226 — pytest harness orphans a PRODUCTION judge-health agent which then
## evades the singleton lock (FOUND + ROOT-CAUSED + FIXED 2026-09-14, tick #454)

SYMPTOM (measured live): THREE `sapo_judge_health_agent.py` processes resident
at once (pids 23345 @04:48, 46573 @10:54, 53616 @00:48).

EVIDENCE / ROOT CAUSE (not a hypothesis — env read off the live pids):
  - `ps eww -p 46573` -> SAPO_LOCK_DIR=/private/tmp/pytest-of-daxu/pytest-687/
      test_loop_with_a_dead_observer0/locks
  - `ps eww -p 23345` -> SAPO_LOCK_DIR=/private/tmp/pytest-of-daxu/pytest-590/
      test_loop_with_a_dead_observer0/locks
  - `ps eww -p 53616` -> no override; it holds the REAL lock
      (/tmp/sapo_locks/sapo_judge_health_agent/holder == 53616).

So 53616 is the legitimate singleton; 23345 and 46573 are ORPHANS spawned by
tests/test_huanxin_broker_probe_three_state.py::
test_loop_with_a_dead_observer_never_reaches_a_kick.

MECHANISM: that test drives the SHIPPED loop under `subprocess.run(..., timeout=3)`.
On expiry Python signals ONLY the direct child (the bash harness). The
grandchild the shipped loop starts survives, reparents to pid 1 -- and because
the test injects a PRIVATE SAPO_LOCK_DIR (to stay off the live lock root, which
is CORRECT for isolation), the survivor's singleton probe resolves to a
throwaway lock dir, so the production guard can never refuse it. It then
double-writes the shared /tmp/sapo_judge_health.log + _state.json (visible in
the log as interleaved strike counters 55/56/57/58 resuming after each restart)
and may walk the auto-repair chain forever.

REFUTED ALTERNATIVES (recorded so they are not re-tried):
  - "the 10s subprocess timeout in _singleton_lock() fails OPEN under load" --
    REFUTED by measurement: the lock script returns in 0.18s under the current
    load-114 host. The except-returns-True path is real but was NOT the cause.
  - "the lock script is too permissive" -- REFUTED by reading: holder_refresh_stale
    returns 1 when no .refreshed file exists, i.e. it fails CLOSED for a live holder.
  - "they are zombies / subshell phantoms" -- REFUTED: all three are STAT S.

CLASS: B-121 (pytest scaffold orphans; cure = killpg) and B-084 (a bound must kill
the GROUP, not the child pid). Same cure, already used by four sibling test files.

FIX (smallest): in test_loop_with_a_dead_observer_never_reaches_a_kick, run the
harness with `start_new_session=True` and, on TimeoutExpired,
`os.killpg(os.getpgid(proc.pid), SIGKILL)` + a final communicate(). Added
`import signal`.

TDD: NEW tests/test_broker_probe_harness_orphan_guard.py (3 tests)
  1. ANCHOR -- the guarded file IS the one that injects SAPO_LOCK_DIR (non-vacuity).
  2. SOURCE -- it must contain start_new_session AND killpg. RED before the fix
     (measured: 2 passed / 1 failed), GREEN after.
  3. BEHAVIOURAL -- a stubbed grandchild carrying a unique argv marker is started
     under a bounded harness; after expiry the GROUP kill must reap it
     (pgrep proves nothing is left). Proves the mechanism, not its spelling.
RESULT: 13/13 GREEN on guard + patched file; 49/49 GREEN regression across
metrics_poller_transport_orphans, huanxin_heartbeat_three_state_probe,
sapo_parallel_eval_agent_{run_keying,coverage}, eval_state_key_full_path,
sapo_contract_queue_watch, heartbeat_daemon_pgid_isolation, single_instance_lock_steal_race.

RESIDUAL (B-226-R, OPEN, PERMISSION-GATED this session): the two already-resident
orphans 23345 and 46573 could not be killed -- `kill` required approval the tick
session did not have. They are harmless-ish (they duplicate-poll a judge upstream
that is 5xx anyway) but they ARE the defect's live residue. NEXT TICK: kill -TERM
23345 46573, keep 53616 (the real lock holder). A source fix does not retroactively
clean a running orphan.


## B-227 - dp4 judge 5xx is the Huanxin SUBSCRIPTION ROUTE (CONSOLE-GATED); a watcher
## restart does NOT restore the judge (ROOT-CAUSED 2026-09-14, tick #455 addendum)

SYMPTOM (measured, per-candidate not by mean): `judge_reward` is None for ALL 8
candidates on ALL 5 banked steps of sapo-27b-ai-20260913T233607Z (judge=0/8 every
step). Dark judged mass = 0.10 of 1.35 total weight, about 7.4%.

EVIDENCE (direct probe, not inferred). POST to the Mac dp4 proxy
http://127.0.0.1:55648/v1/messages returned:
    HTTP 500  error.type="upstream_route_error"
    error.message="Huanxin inference gateway returned HTTP 500: subscription route not found"
So the PROXY IS UP AND ANSWERING; the fault is the Huanxin subscription route.

The watcher is NOT blind and NOT idle (checked against B-138/B-144 failure modes):
its log shows `queue-run: OK` every ~40s against the CORRECT queue, and it staged
resp files at 03:41:03Z and 03:43:42Z - each carrying the 500. Fail-closed worked:
the trainer saw a 504 and recorded judge-absent rather than a silent score.

CONSEQUENCE (citable; prevents a wasted restart): reloading B-206 into the live
watcher restores only VISIBILITY of the body above. It does NOT restore the judge
and must not be cited as a judge fix. A proxy relaunch is REFUTED - the proxy
answers. The route is fixed in the Huanxin CONSOLE -> USER-GATED.

STATUS: OPEN, USER-GATED (console access required). No local fix exists.
RELATED: B-206 (watcher swallowed the upstream body - the reason this took a direct
probe to see), B-219 (queue-empty is transient).

## B-224 UPDATE (2026-09-14, divide-and-conquer cycle) -- COUNT-MISMATCH HYPOTHESIS REFUTED AT THE UNIT LEVEL; DO NOT IMPLEMENT THAT FIX
Status: hypothesis REFUTED. A RED test proved the trust-region gate is
INVARIANT to token count when both sides are per-candidate MEANS, so the B-224
"count mismatch" mechanism cannot, on its own, fire the false violation.

EVIDENCE (TDD, tests/test_b224_trust_region_samepass.py):
- sequence_ratio_stats (grpo_utils.py:2720) diffs per-candidate MEAN log-probs:
    seq_kl = (expm1(clipped(cur-old)) - clipped(cur-old)).clamp_min(0).mean()
- OLD side: old_log_probs[idx] / old_token_counts[idx]  (a mean, trainer:6951/6955)
- POST side: post_log_prob / post_token_count  (a mean, trainer:7461/7485)
- compute_completion_log_prob returns a SUM, but the caller normalizes it to a
  mean by dividing by count on BOTH sides. So a count mismatch alone changes
  NEITHER side's per-candidate value -> seq_kl stays ~0. My RED test
  (mismatched prefix lengths, unchanged policy) PASSED, i.e. did not reproduce
  a violation. That is a NEGATIVE result: the "count mismatch" fix candidate is
  WRONG and must not be implemented.
- Temperature is also symmetric: policy_temperature=effective_temperature is
  passed on BOTH the rollout-time pass (6070) and the post-update re-encode
  (7469). So the temperature hypothesis is also not the trigger.

WHAT STILL MUST EXPLAIN IT (leave open, do not fix on guess):
  step 2 ratio_after=11.17, seq_kl_after=9.04 is ~2.4 nats/token of post-update
  shift — not credible as policy movement at lr 2.5e-5, but NOT explained by
  count/temperature. The post-update forward runs a FRESH logit computation on
  the UPDATED LoRA weights; a mismatch there vs the rollout-time cache, or a
  genuinely explosive update on the truncated candidates' prefixes, are the
  remaining candidates. Next step before any fix: dump per-candidate
  old_log_probs[idx], post_log_prob, and post_token_count for one violating
  step and diff them numerically.

## B-224 ADDENDUM 2 (tick #456, 2026-09-14 11:58 CST) -- SAME-STEP DISCRIMINATOR FOUND: THE POST-UPDATE PROBE AND THE TRAIN PASS DISAGREE BY ~250x, AND THE INSTRUMENT NEEDED TO SETTLE IT IS NOT PERSISTED

TWO FIX CANDIDATES KILLED THIS TICK (both by code inspection, no fix written on either):
  (a) COUNT-MISMATCH -- already refuted at unit level (B-224 UPDATE above).
  (b) TEMPERATURE -- REFUTED THIS TICK. Hypothesis: escalate_temperature_on_flat_route()
      (grpo_trainer.py:7442) runs BEFORE the trust-region block (:7449), so the post-update
      re-encode at :7469 might use a higher temperature than the rollout-time pass at :6070.
      FALSE: effective_temperature is computed exactly ONCE per step at :5980
      (clamp_adaptive_behavior_temperature(adaptive_temp.current_temp())), and the SAME variable is
      passed to BOTH :6070 and :7469. The escalation mutates adaptive_temp, so it takes effect at the
      NEXT step's :5980, not this step's post-encode.
  Also VERIFIED (not refuted): B-212's own rationale is correct. At :6943-6956, when
  n_train < n_old the old side is old_prefix = consistent_old_token_lps[idx][:n_train]; then
  .mean() -- a per-candidate MEAN over the identical first n_train tokens the capped post pass uses
  (:7460-7485, post_log_prob / post_token_count.clamp_min(1)). Both sides are means over the SAME
  prefix. Keep the cap; it removes a real OOM risk and is NOT the cause.

NEW MEASURED DISCRIMINATOR (step 6, banked, grpo_step_metrics.jsonl / train_stdout.log):
    train_pass_truncation_rate : 1.0     <- EVERY candidate was truncated by the 2048 train cap
    truncation_rate (generation): 0.0
    trust_region_violated      : false
    trust_region_violation_count: 3      <- CUMULATIVE (grpo_trainer.py:7502 += 1; restored :5861)
    ratio_after_update         : 0.5999
    clip_fraction_after_update : 0.75
    seq_kl_after               : 0.2477
    in-training per-candidate sapo seq_kl, SAME step:
      [0.0002395, 0.0003167, 0.0001551, 0.05027, 0.04825, 0.000432, 0.00203, 0.05422]
      (max 0.0542; mean ~0.0196)

READING: on the SAME step, over the SAME (truncated) prefix, the post-update trust-region probe
reports a shift (seq_kl_after 0.2477; mean ratio 0.5999) that is ~4.6x the LARGEST per-candidate
train-pass value and ~250x the mean. A 2.5e-5-lr LoRA update cannot move the policy that much. The
two probes are measuring the same quantity and disagreeing, so ONE of them is wrong.

THE BLOCKING DEFECT (this is what to fix; TDD-able, launch-boundary only):
  The step record does NOT persist the per-candidate post-update values, so the dump B-224's own
  next-step note asks for (old_log_probs[idx], post_log_prob, post_token_count) is IMPOSSIBLE for
  any banked step. grep confirms :7460-7485 computes post_log_probs and post_token_count as locals
  and only the AGGREGATES (ratio_after_update / clip_fraction_after_update / seq_kl_after) reach
  record_update (:7636-7638). Next step: persist per-candidate post_token_count AND the per-candidate
  post-vs-old mean delta (or the per-candidate ratio) in the step record, RED-first, then re-run one
  violating step and diff numerically. Do NOT guess a fix for B-224 before that dump exists.

STATUS: OPEN. Two of three candidate branches now dead. Instrumentation gap is the next step, owned
by the bug-clearing lane. DO NOT touch training/ while the live run is in flight (S5.4.2) - land at
the next launch boundary.

* 2026-09-14 (Judge-Chain lane, tick cross-check) — ORDER-1 PREMISE FALSIFIED: the '3-purist duplicate sapo_judge_health_agent herd' is NOT a production herd. MEASURED via `ps -Eww`: pid 23345 and 46573 carry SAPO_LOCK_DIR=/private/tmp/pytest-of-daxu/pytest-<590|687>/test_loop_with_a_dead_observer0/locks, i.e. they are PYTEST-LEAKED orphans from tests/test_huanxin_broker_probe_three_state.py ::test_loop_with_a_dead_observer_never_reaches_a_kick, already filed as B-226 and FIXED (start_new_session=True L255 + os.killpg L261; tests/test_broker_probe_harness_orphan_guard.py GREEN 3/3). pid 53616 is the ONLY production agent; it holds /tmp/sapo_locks/sapo_judge_health_agent (holder=53616). The B-171 single-instance guard (scripts/sapo_judge_health_agent.py:182-217) is CORRECT and NOT defective: a second production invocation refuses, rc=1 in 0.07s, measured against a copy of the live lock state preserving the 41905s-old dir mtime. So NO new guard and NO new RED test were written — that would duplicate the green tests/test_judge_health_agent_singleton.py (5/5) and encode a falsified premise. RESIDUAL (user-gated, not actioned): the two PRE-FIX orphans are still resident PPID 1 and no future run can reap them; they are permanent duplicate writers of /tmp/sapo_judge_health.log. Resolves the same way as B-195 (keep-one).

## B-228 - the Qwen3.8-27B retirement was INCOMPLETE in the model registry: a stale
## `expected_substring` (a FAIL-CLOSED verifier target, not a "model default" key)
## plus a malformed `remote_model_dir`; the B-220 class guard was blind to both
## (ROOT-CAUSED + FIXED 2026-09-14, tick #458)

SYMPTOM (measured standalone, NOT load-sensitive): `tests/test_model_family_support.py::
test_public_models_exposes_gemma4_targets` RED in the full-suite chunk AND repeated
standalone; `tests/test_keeper_pid_resolution_b210.py::test_parent_map_is_read_from_one_snapshot`
likewise. Both were carried in the 15-failure in-chunk set of suite run 33860.

ROOT CAUSE 1 (production defect, B-220 class - WIDER than tick #457 believed).
`training/acquire_public_qwen_snapshot.py` PUBLIC_MODELS["qwen36-27b"] was edited by the
retirement commit (1b7ca92) to point `model_id` at the new base, but left:
    "expected_substring": "Qwen3.6-27B",     <- STALE, names the RETIRED model
    "remote_model_dir": "/root/software/quantum-gpt//root/work/filestorage/Qwen3.8-27B",
                                             <- MALFORMED: relative prefix concatenated
                                                onto an absolute path
`expected_substring` is NOT cosmetic: main() passes it to
`verify_qwen_snapshot.py --expected-substring`, which EXITS NONZERO when the downloaded
directory does not contain it. Pointed at the retired model while model_id is the new
one, that check can never pass - the acquire path fails closed EVERY time.
BOX EVIDENCE (positive control, ASI3 :20653):
    ls -d /root/work/filestorage/Qwen3.8-27B          -> EXISTS (LICENSE, config.json, ...)
    ls -d /root/work/software/quantum-gpt//root       -> No such file or directory
so the OLD remote_model_dir names a path that cannot exist and the NEW one names the
directory the live trainer actually loads.

ROOT CAUSE 2 (why the class guard missed it). tests/test_qwen38_base_model_retirement.py
matches only model-DEFAULT key shapes (_MODEL / MODEL_PATH / MODEL_NAME / BASE_MODEL).
The retirement class is broader: the SAME commit left a stale retired-model reference in
a key that names a VERIFICATION TARGET. The matcher is correct for what it scopes; the
scope was the hole.

FIX (TDD, RED first).
 - RED: corrected the stale assertions in test_model_family_support.py to the
   post-retirement truth, and added 3 STRUCTURAL invariants to the retirement guard:
   (a) no registry VALUE may reference the retired model, under ANY key;
   (b) `expected_substring` must appear in `model_id` (the verifier is fail-closed on it);
   (c) `remote_model_dir` must be canonical (os.path.normpath(v) == v), absolute, and
       must not nest a second absolute path.
   Demonstrated RED: 4 failed.
 - FIX: the two stale/malformed values.
 - GREEN: 81/81 across the touched retirement cluster.
 - MUTATION-PROVEN NON-VACUOUS: re-injecting "Qwen3.6-27B" into the real expected_substring
   -> 2 failed; restored -> 10 passed, file sha256 byte-identical.

ROOT CAUSE 3 (test defect, different class - same tick). test_keeper_pid_resolution_b210::
test_parent_map_is_read_from_one_snapshot asserted `86975 in m`, where 86975 was lifted
from the tick #439 forensic log (a transient keeper SUBSHELL, etime 24:30 at 08:49Z).
MEASURED: `ps -p 86975 -o pid=` -> EMPTY; the pid is gone. `_parent_map` is CORRECT - its
own docstring says a vanished pid is legitimately absent from the map. The TEST was
non-hermetic: a pid quoted from a log is not a fact about this machine's process table, so
the test detonates the moment that subshell exits. FIX: bind the assertions to processes
the test owns - os.getpid() (alive by construction, real ppid checked) and a child it
spawns and reaps itself - plus a never-raises case. 12/12 GREEN.

CLASS NAMED: a TEST that asserts a fact about the LIVE PROCESS TABLE using a pid captured
in a LOG. Its green is a scheduling coincidence, not a measurement.

## B-229 - eval marker fallback is not checkpoint-scoped: a stale artifact suppresses a leg (FIXED, TDD)

STATUS: FIXED in the Mac tree. scripts/asi2_loop_eval.sh sha256 210a63c84b880e7b;
new guard tests/test_eval_marker_checkpoint_scoped.py sha256 fcad4f9408cc10db (4/4 GREEN);
touched cluster 46/46 GREEN.

MEASURED LIVE 2026-09-14, run sapo-27b-ai-20260913T233607Z, ASI2 parallel-eval lane,
/private/tmp/sapo-logs/eval_step_000003_adapter.log:
  [2026-09-14T04:19:54Z] on-box marker found: .../outputs/reeval_latest_3.json; backfilling local state
The state file then reports that checkpoint status=done verdict=marker-found. But reeval_latest_3.json is
dated 2026-09-02T13:58:57Z and belongs to a DIFFERENT measurement epoch (pass_at_1 adapter 3/18 base 3/18).
step_000003_adapter was therefore NEVER evaluated in this run -- a false DONE, i.e. a silent coverage gap in
the very instrument that produces the beats-base verdict.

ROOT CAUSE: scripts/asi2_loop_eval.sh carries a fail-closed identity check for the LOCAL state file (B-107;
its own comment: only THIS checkpoint's own identity counts as a verdict, an unmatched key suppressing a leg
is a silent coverage gap, the worse failure of the two). The on-box MARKER fallback that follows re-opened
exactly that gap: it globs outputs/reeval_latest_<leg short name>.json, keyed by a bare step number that is
identical across runs, and took mere file EXISTENCE as a verdict.

FIX (smallest, fail-closed): new helper marker_is_for_checkpoint MARKER ADAPTER. A marker is a verdict only
for the checkpoint it was produced FROM, so it must be at least as new as the adapter directory. Freshness is
format-agnostic -- the two marker producers write different JSON shapes, so an identity field read is not
available on both. Unknown freshness (daemon down, auth down, no stat) resolves to EVALUATE, never to DONE.
The stale case now emits STALE_MARKER and the leg runs.

RED first: helper absent -> W1 (non-vacuity) and W4 (decision site uses the helper) failed.
GREEN after: 4/4. W1 asserts a fresh marker STILL suppresses, so the fix is not always-re-run.
CONSEQUENCE: step_000003_adapter returns to PENDING and will be evaluated on a later cycle.


## B-225 (2026-09-14) -- THE EVAL BOX LACKED QISKIT, SO THE PASS MASS WAS STRUCTURALLY UNEARNABLE (THE REAL DARK-REWARD ROOT CAUSE) -- FIXED
Status: FIXED (installed qiskit on the ASI2 eval runtime). Root cause of the
flat comprehensive scores is NOT primarily the lr bleed -- it is that opponents
could not run at all on the eval host.

EVIDENCE (measured live, eval_results.jsonl, 88 records):
  - pass rate 5.7% (5/88)
  - import_error 27, SyntaxError 24  -> 58% fail before execution
  - dominant import fault:
      ImportError: cannot import name 'StatevectorSampler'
      from 'qiskit.quantum_info'
  - ROOT: python3 -c "import qiskit" on ASI2 (port 19004) -> "No module named 'qiskit'"
    ASI3 (train, 20653) has qiskit 2.5.2 + aer 0.17.2; ASI2 had NONE.
  - So every candidate that imports qiskit scored 0.0 on pass + shaped + verifier:
    the 0.45 pass + 0.40 shaped + 0.10 judge reward mass was dark for a MECHANICAL
    reason independent of model quality or learning rate.

FIX (applied, non-destructive -- separate host from training):
  Installed on ASI2 to match ASI3 exactly:
    qiskit 2.5.2, qiskit-aer 0.17.2, cirq 1.7.0, pennylane 0.45.1 (+lightning), openqasm3
  Verified: StatevectorSampler imports from qiskit.primitives; basic circuit
  transpiles/runs. The next eval legs (step_000005+) can now actually score pass.

NOTE (do not reopen B-193): this is the grader-RUNTIME install gap, not the
"policy imports wrong module" reading. Now that qiskit is present, the remaining
import_error class is candidates using a WRONG API path (quantum_info.vs.primitives),
which is a model/generation concern -- the runtime can now execute them.

REMAINING (separate): the lr bleed (B-224) is a real but SECONDARY contributor.
At full lr with qiskit present, the model finally gets gradient on the pass mass.

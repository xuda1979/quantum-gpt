# deploywatch — DEPLOY INTEGRITY WATCH (lane #15, SAPO RL loop)

Role: standing watch over the SAPO relaunch bundle + box deployment integrity.
Created 2026-08-25 (lane #15 activation). Loop cadence ~5 min.
PERSISTS across session boundaries via this file (durable standup cron).

## TREE-LOCK PROTOCOL (manager rule 2026-08-25, applies to r8+ bundles)
Before bundling ANY generation r8+:
1. Check `.sapo-loop/locks/` — if dir absent, NO locks → proceed.
2. Any shared file under `training/`, `scripts/`, `configs/`, `evals/` with an
   active lock (`.lock` file age < 2h:
   `find .sapo-loop/locks -name '*.lock' -mmin -120`) MUST NOT be bundled.
   Report the holder (lock file content) and RETRY in ~5 min — do NOT bundle
   the locked file's current content.
3. Stale locks (>2h) are the MANAGER's to break — deploywatch never breaks
   them, only reports.
4. Lanes editing shared files write their lock first (their responsibility).
5. Lock appearing MID-upload of an already-built bundle: bundle is frozen at
   build time — do not abort a verified deploy; next generation re-checks.
6. After r8: this protocol gates every rebuild in this lane; log lock checks
   in the cycle log.
7. Executed r8 under protocol 2026-08-25 21:57/14:36Z: locks/ empty → bundled.
   First execution. Empty `locks/tests/` subdir noted (no .lock files = no
   active lock; do not treat dirs as locks).

## Mandate
1. **Bundle freshness**: sha256 of every member of the CURRENT bundle manifest
   (newest `tmp/sapo-relaunch-lr2e4-20260825-r*.sha256`) vs the working tree.
   ANY difference → bundle STALE → rebuild immediately:
   - tar the manifest member list from the CURRENT tree (nested previous bundle
     rolled forward: rN nests `tmp/sapo-relaunch-lr2e4-20260825-rN-1.tgz`)
     → `tmp/sapo-relaunch-lr2e4-20260825-r<N+1>.tgz` + `.sha256` manifest
   - redeploy to box `/tmp/sapo_deploy/relaunch_r<N+1>.tgz` via 6000-byte
     chunked base64 `echo -n '<chunk>' >> /tmp/sapo_deploy/r5_<name>.b64`
     pattern through `POST http://127.0.0.1:19005/exec` (ASI3 daemon, ~12K cmd cap;
     11800-char chunks verified OK, 6000 is the established pattern)
   - sha-verify BOTH sides; report changed files
2. **Box-side integrity**: verify extracted tree (`/root/work/software/quantum-gpt`
   — the live run tree, trainer cwd) matches deployed bundle for the 5 critical
   files: `training/grpo_trainer.py`, `training/grpo_utils.py`,
   `scripts/run_hf_pass1_eval.py`, `configs/rl/qwen36_27b_fv_gspo_asi2.json`,
   `scripts/asi3_launch_grpo_direct.sh`. Box-side drift → report diff; do NOT
   overwrite blindly if box version is NEWER (compare mtimes first).
3. Record every bundle generation (member count + sha) below. Quiet otherwise.
   NOTE: trainer/dev files change while agents TDD — stale bundle is EXPECTED
   during active dev; job = deployed bundle + gate reference the LATEST verified
   tree at all times (the 10:27-tgz-vs-tree incident must never repeat).

## Deploy procedure (r5 pattern, 2026-08-25)
- Local: `awk '{print $2}' <prev>.sha256 | sed 's|r<N-1>.tgz|r<N>.tgz|' > members.txt`
  then `tar -czf r<N+1>.tgz -T members.txt`; `xargs shasum -a 256 > r<N+1>.sha256`;
  verify manifest == tree; `shasum -a 256` the tgz.
- Upload: `base64 -i r<N+1>.tgz -o /tmp/rN.b64`; `split -b 6000`; POST each chunk
  as `echo -n '<chunk>' >> /tmp/sapo_deploy/r5_<name>.b64` (driver: /tmp/r5_upload.py);
  assemble `cat r5_*.b64 | base64 -d > /tmp/sapo_deploy/relaunch_rN.tgz`.
- Verify box side: `sha256sum /tmp/sapo_deploy/relaunch_rN.tgz` == local.
- Refresh run tree: `tar -xzf /tmp/sapo_deploy/relaunch_rN.tgz -C /root/work/software/quantum-gpt`
  (only after mtime check — box files must NOT be newer than bundle).

## Box map (ASI3, daemon pid 20484, port 19005, dl-c72bd81a96e33134bbe0ae4a478fbab0)
- Deploy dir: `/tmp/sapo_deploy/` (relaunch_rN.tgz bundles, chunk .b64 staging)
- Run tree: `/root/work/software/quantum-gpt/` (live; trainer started 07:04Z run
  sapo-27b-ai-20260825T070339; sidecar fv_gspo_repair_sidecar.sh)
- `/tmp/sapo_deploy/extract/` = r0-era staging only (NOT the live tree; stale r0
  content as of 2026-08-25 — harmless, superseded by run tree)
- Exec probe: `POST /exec {"command": ...}` ~12K cap; `echo A; echo B` clean.

## Bundle generation log
| gen | members | tgz sha256 | deployed | notes |
|-----|---------|------------|----------|-------|
| r0 (10:27)  | 103 | b4e2b00b7eb728f0e2a8f22b54054173f2fb40f8598997f17a09054d35a10c0b | box 02:32Z relaunch.tgz | original bundle |
| r2          | 100 | a66d393f60a1d83445a8a13745d927cda890f00936fadeb3d10987cd06a12c1a | box 03:10Z relaunch_r2.tgz | nests r0.tgz |
| r3          | 101 | aa555ea7af9bc83a77d97a76458a06f423c17494f0a249bb5fe15d7a102c16fd | box 04:17Z relaunch_r3.tgz | nests r0.tgz |
| r4          | 102 | 27c28dc16dc60191a49efeec4d17152bdb4ce249a7b2bf258ee7a0cb9e34d8ba | box 07:03Z relaunch_r4.tgz | nests r3.tgz; run tree refreshed 07:04Z |
| **r5 (20:40 CST)** | **102** | **cdc8e9d35fd75b351a5a46eda95d1b540c37ba010fb2441e3bef1a2333c653ed** | **box 12:41Z relaunch_r5.tgz — DEPLOYED + VERIFIED** | nests r4.tgz; changed: training/grpo_trainer.py (M), scripts/sapo_drift_watch.py (new), tests/test_sapo_drift_watch.py (new); run tree refreshed 12:41Z |
| r6 (21:03 CST)   | 102 | b2cf92f49a828f90cbe926950f1a27e4d3fb2e6384dab8082c77f0da096d32cc | box 13:02Z relaunch_r6.tgz — DEPLOYED + VERIFIED | nests r5.tgz; changed vs r5: grpo_trainer.py (M), configs/rl/qwen36_27b_fv_gspo_asi2.json (M), scripts/asi3_launch_grpo_direct.sh (M), scripts/asi2_launch_grpo_27b_selfeval.sh (M); run tree refreshed 13:03Z |
| **r7 (21:22 CST)** | **102** | **bb76fa913174c3f96c19fd5c9d65a8ca30102bc0fb55407104fb47763b8856d8** | **box 14:22Z relaunch_r7.tgz — DEPLOYED + VERIFIED** | nests r6.tgz; changed vs r6: training/grpo_trainer.py (M, cc5ec4d1…); run tree refreshed 14:23Z; NOTE: transport dup chunk r7_fb (12000B) fixed by truncation to 6000B before assembly |
| **r8 (21:57 CST)** | **102** | **30aef49082d95e711701d07610e53b136aa759e37f5205826304103b0ce9ff09** | **box 14:36Z relaunch_r8.tgz — DEPLOYED + VERIFIED** | nests r7.tgz; changed vs r7: training/grpo_trainer.py (M, a8469ceb…); lock-check 21:57: locks/ empty → clear to bundle; run tree refreshed 14:36Z; transport dups r8_nn+r8_no (12000B each) fixed by truncation to 6000B |
| **r9 (2026-08-26 ~07:0x CST)** | **118** | **7f7404d2e6f2e27357a8f1155069de8a1d16bf4d56e09161d7ef3c02218d17df** | **box ~23:0xZ relaunch_r9.tgz — DEPLOYED + VERIFIED** | NO nested artifact; QA-escalation rebuild; gate clean; run tree refreshed; fine_score.py fix on box (ecdd038d…)  |
| **r10 (2026-08-26 ~11:1x CST)** | **136** | **4f2e93155a70875fd1c468899010ccc1e26ca065e7602350754fd5485b33023f** | **box ~11:1xZ relaunch_r10.tgz — DEPLOYED + VERIFIED** | register FULLY TICKED build; r9 118 + 18 wave files (compat.py, eval_100_reeval, sapo_reward_audit, calibrate_model_judge, report_base_adapter_comprehensive, seed_run_with_references, 12 wave tests); run tree refreshed; launchsim r10 smoke TRIGGERED — LATER REJECTED by launchsim (training/generation.py missing) |
| **r11 (2026-08-26 ~11:5x CST)** | **164** | **e694bc556ed42eaf1fc34da24996c02ccce38140df6f5cac27e46f420edbbf29** | **box ~11:5xZ relaunch_r11.tgz — DEPLOYED + VERIFIED** | r10 REJECTED (generation.py missing); r11 = r10 136 + 28 closure modules (CLOSURE OK via new permanent gate .sapo-loop/sapo_bundle_closure_check.py); GRPO_TRAINER IMPORT OK verified on box; run tree refreshed; launchsim re-signaled (/tmp/sapo_launchsim_r11_TRIGGER) |
| **r12 (2026-08-26 ~13:5x CST)** | **166** | **c0613c3431c99879a2d50155f79300bf68b82ed380b3112f94b5c7391b20a0e0** | **box ~13:5xZ relaunch_r12.tgz — DEPLOYED + VERIFIED** | run-8 OOM fix (entropy token cap 256, grpo_trainer/grpo_utils changed) + 2 new tests (test_grpo_entropy_token_cap, test_grpo_trainer_faulthandler); closure OK 166; GRPO_TRAINER IMPORT OK on box; launchsim slim-rehearsal signaled (/tmp/sapo_launchsim_r12_TRIGGER) |
| **r13 (2026-08-26 ~15:2x CST)** | **167** | **ba72bfbdc6a1d174656755dabed79fc1b79e19e2e0858244c89be30e5aa0db2f** | **box ~15:3xZ relaunch_r13.tgz — DEPLOYED + VERIFIED** | backward-OOM fix (chunked-recompute) + faulthandler guard (RED(2) resolved, independently re-verified 6/6); + test_grpo_chunked_recompute_backward.py; closure OK 167; GRPO_TRAINER IMPORT OK on box; launchsim signaled (/tmp/sapo_launchsim_r13_TRIGGER) — Executor auto-relaunches on its pass |
| **r14 (2026-08-26 ~16:5x CST)** | **168** | **b9c8b0b2fc43d974b6cfedeb86208f7817b8ea835ea0dca0eaf932ba26d99435** | **box ~16:5xZ relaunch_r14.tgz — DEPLOYED + VERIFIED** | double-backward fix (detached penalty + backward-once); + test_grpo_entropy_floor_backward_once.py; stale RED items re-verified 10/10; closure OK 168; GRPO_TRAINER IMPORT OK on box; rehearsal signaled (/tmp/sapo_launchsim_r14_TRIGGER) — Executor auto-relaunches on its pass |
| **r15 (2026-08-26 ~17:1x CST)** | **168** | **74576ab9114d4da84272e8204b271e43ac18e71ac3874148c327cc0001d4aa90** | **box ~17:3xZ relaunch_r15.tgz — DEPLOYED + VERIFIED** | F5 double-add fix (penalty composed exactly once via add_entropy_floor_penalty_value helper + common-tail guard :5440); launchsim r14 BLOCK addressed; F5 regression 4/4 venv-green; closure OK 168; GRPO_TRAINER IMPORT OK on box; re-smoke signaled (/tmp/sapo_launchsim_r15_TRIGGER) — Executor auto-relaunches on its pass |
| **r16 (2026-08-26 ~19:1x CST)** | **169** | **456317a7fcc6d6beb318868160f78f7aba06557784f13a0a11642bf155a2a6a8** | **box ~19:2xZ relaunch_r16.tgz — DEPLOYED + VERIFIED** | JUDGE WAVE (frozen base judge sharing training model, 0.40/0.35/0.25 blend, flags wired+echo-verified); + test_grpo_judge_wave.py (16/16 venv-green); launchsim r15 BLOCK cleared (re-smoke passed); closure OK 169; GRPO_TRAINER IMPORT OK on box; rehearsal signaled with judge-inference step (/tmp/sapo_launchsim_r16_TRIGGER) — Executor auto-relaunches on its pass with AI_SAPO_MODEL_JUDGE_ENABLED=1 AI_SAPO_MODEL_JUDGE_PATH=/root/work/filestorage/Qwen3.6-27B AI_SAPO_REWARD_MODE=comprehensive |
| **r17 (2026-08-26 ~19:4x CST)** | **169** | **2f2c2fc99f9cc31b8d9fdf327b89e94a28a6adffede520dae0265827769690e6** | **box ~19:5xZ relaunch_r17.tgz — DEPLOYED + VERIFIED** | calibration-gate supersede (no calibration => judge mass 0 + judge_reward=None; masses 0.50/0.40/0.10; audit contract updated); 21/21 wave tests venv-green; closure OK 169; GRPO_TRAINER IMPORT OK on box; rehearsal signaled with judge-inference step + MODEL_JUDGE_ENABLED=0 default (/tmp/sapo_launchsim_r17_TRIGGER) |
| **r18 (2026-08-26 ~19:5x CST)** | **170** | **8740e4ab22ec7f231e95be34c26caec0ad89954091d9c31591ab0379173dfc78** | **box ~20:0xZ relaunch_r18.tgz — DEPLOYED + VERIFIED** | full-terms instrumentation wave (every term per candidate + grep-able line; 3 code-review bugs fixed incl. judge-path crash; masses 0.50/0.40/0.10); + test_grpo_trainer_step_instrumentation.py; 39/39 wave tests venv-green; closure OK 170; GRPO_TRAINER IMPORT OK on box; rehearsal signaled with judge-step + full-terms check (/tmp/sapo_launchsim_r18_TRIGGER) — r18 supersedes r17 |

## Cycle log (2026-08-25)
- **20:39-20:41 CST (12:39-12:41Z)**: r4 manifest vs tree → STALE (3 files:
  grpo_trainer.py, sapo_drift_watch.py, test_sapo_drift_watch.py — all newer
  locally; TDD-active). Box run tree 5-critical == r4 bundle exactly (no drift,
  box files NOT newer than local). Rebuilt r5 (102 members), manifest verified
  == current tree (101/102 identical; nested bundle rolled r3→r4). Uploaded via
  6000B chunked b64 (202 chunks, 0 failed) → assembled on box
  `/tmp/sapo_deploy/relaunch_r5.tgz`; box sha256 `cdc8e9d3…` == local, size
  904832 both sides. Deployed bundle member hashes (5 critical) == r5 manifest.
  Extracted r5 over run tree `/root/work/software/quantum-gpt` (mtime check:
  box files r4-era, NOT newer → overwrite safe). Run tree now == deployed r5
  bundle for all 5 critical files + nested tmp/...r4.tgz (27c28dc1…) +
  sapo_drift_watch.py (8d630261…) + test_sapo_drift_watch.py (9348eb35…).
  DONE — deploy + extracted tree + gate all reference latest verified tree.
- NOTE: `/tmp/sapo_deploy/extract/` on box is r0-era staging, not the live run
  tree — leave untouched.
- **14:22Z (r7 finalized)**: tree moved AGAIN during r7 upload — grpo_trainer.py
  cc5ec4d1… → 4c520a1a… (TDD-active; expected). Deployed bundle + run tree =
  r7 (latest verified at build); NEXT LOOP CYCLE: build r8 (nested r7.tgz) and
  redeploy. No box-side drift observed at any point (box files never newer than
  local — mtimes checked before every run-tree refresh).
- Transport hardening learned: after upload, always verify chunk count + sizes
  on box BEFORE assembling (a lost-response retry can duplicate a chunk, as
  happened with r7_fb + r8_nn/r8_no; detect via `ls | awk '$5 != 6000'`).
- **14:36Z (r8 finalized)**: TREE-LOCK PROTOCOL first execution — locks dir
  exists (21:55) but EMPTY (only empty subdir `locks/tests/`) → no active
  locks → bundled r8. Deployed + verified both sides (30aef490…, 1627627B);
  run tree synced; 5 critical files match r8 manifest. Tree drifted during
  upload (6 files, TDD burst): grpo_trainer bc467299…, grpo_utils
  426edf93…, asi3_launch 1d6e5b80…, asi2_launch 1a165df6…,
  test_sapo_promotion_pipeline_hardening b7b4ad1b…, test_fine_score
  77b72840… → NEXT CYCLE: build r9 (nested r8.tgz) after lock re-check.
  No active/stale locks at cycle end; nothing for manager to break.

## QA ESCALATION — r9 hardened build (coordinator 2026-08-25 ~22:2x CST)
- **r8 defects (4)**: nested-bundle artifact in manifest; no py3.9 gate (shipped
  py3.10-only `zip(strict=True)`); no build-time member-hash-vs-tree rejection;
  member list not recorded. r8 as-is would crash box py3.9 venv.
- **r9 HARDENED PROCESS (this lane)**:
  1. EXPLICIT list: derived from r8 manifest members ONLY (`awk '{print $2}'`,
     no globbing) MINUS nested tmp artifact, PLUS 5 new files
     (evals/tasks/quantum/pennylane_vqe_h2/tests.py, tests/test_grpo_trainer_sigterm.py,
     tests/test_grpo_trainer_resume.py, tests/test_grpo_trainer_eval_results.py,
     tests/test_pennylane_vqe_h2_scorer_versions.py) → 106 members, all present.
  2. PY3.9 GATE (zip strict=True / strict=True grep over ALL bundled .py):
     **FAILED** — `scripts/fine_score.py:319` has LIVE `zip(base, report["scores"],
     strict=True)` (py3.10-only kwarg; crashes py3.9 at runtime). Hash
     7c6645277836f3b9fe4696facc13ba50d976ca61684c969492082f68127d2938 —
     UNCHANGED since r4; r8 shipped it; box run tree carries it (r8 refresh).
     Coordinator-claimed fixes VERIFIED in tree: training/grpo_utils.py:1371 +
     tests/test_fine_score.py:217 are comment-only (safe); all other strict=True
     hits are docstrings (grpo_trainer.py:117, test_grpo_trainer_resume.py:672).
  3. Member-hash vs tree: snapshot taken (below) — NO stale members at snapshot
     time; build will re-verify at tar time and reject on any change.
  4. Tree locks: `.sapo-loop/locks/` scanned before list build — no .lock files.
  5. Deploy: pending gate. 6. Full member list + hashes recorded below.
- **BUILD STATUS: BLOCKED by PY3.9 GATE (scripts/fine_score.py:319)** — not
  tarred. Per gate rule "any hit = fail the build". Waiting for code-lane fix
  (or manager decision); retry re-checks the gate every ~5 min. No bundle
  shipped with the poisoned file.

### r9 planned member list + hashes (106 members, snapshot 22:2x CST)
85106d8e4c0c337edbc95eec2972d363c96f50f2d91c0d4404438dff386c4f27  configs/rl/qwen36_27b_fv_gspo_asi2.json
7b8bdc04fe2a6b41ba867facdebe04170bf7c864a2e09c2b446718764f060f18  evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt
0108c020f916b8dbf8ab16d08560d0057265ecaee0f5f37289620a7e0e8f0e54  evals/tasks/quantum/bell_pair_construction/candidate.py
9f6bf09c6019fb84748c9df10638291fd62bfcc90fa049642b980a1541b52403  evals/tasks/quantum/bell_pair_construction/tests.py
976677faa3f3138f9ac53c1435cbb8002ef380dabff6dc74f2f4fc4821620da1  evals/tasks/quantum/binary_measurement_decoder/task.json
114bd9cf91467960db9b629475aad730929625271b7ea76e453199b3b40b6690  evals/tasks/quantum/binary_measurement_decoder/tests.py
48d45ea9b46d7e54f23edbb62e94e7fb132884250506e342c460c7c9bba2d7db  evals/tasks/quantum/bitstring_maxcut_landscape/tests.py
4b4c0ea792f29454d0430a473cdaa778bc1432801c7f2c8c0d935520c89a29e5  evals/tasks/quantum/circuit_phase_repair/tests.py
6ee4de0769c7dd49dfa317d83035cc870c83020b9094cac23d5724f6f30fbdc6  evals/tasks/quantum/density_matrix_partial_trace/candidate.py
311688fed1cf708c6cbbe7854c724c422758526c1e6d13f12d1f1d1eb409e804  evals/tasks/quantum/error_detection_bit_flip/tests.py
18ed2cb56ee7c96529c53d65921deb4c44dcfdedce5d2bb275e36b714d59e6ae  evals/tasks/quantum/gate_alias_casefold_barrier/candidate.py
5feaa43a0f846f7d605e3b9ee6946ba4e4d53e61da07ed4ea7d40117218db661  evals/tasks/quantum/gate_alias_casefold_barrier/tests.py
f1cf1e1144aeef96acac9f527b6b3d96ea9c0c938121a48d9f2fc735599d9525  evals/tasks/quantum/gate_alias_normalization/task.json
4e17b821390f6916b8fd29d64061489a7bde5367a648b8227b26276a79b97143  evals/tasks/quantum/gate_alias_normalization/tests.py
fb4c96d30a8260ad6aa9895e3c2673d3dd7cc264d9f0958bfa0d9a163eb7760b  evals/tasks/quantum/gate_alias_registry_cleanup/candidate.py
d02d9e3673930d64c3dd1483d8ebf00c6b23764fa18fe542f16930313722100f  evals/tasks/quantum/gate_alias_registry_cleanup/tests.py
8cba17a29939f736e18e729a86fbbef83be4db9811890f2467dac666f805d931  evals/tasks/quantum/gate_token_canonicalizer/tests.py
7a6d4835c6cf027a323a720cd9698cf80560470c9c3aba7652965da3aeaac224  evals/tasks/quantum/ghz_state_witness/candidate.py
48db0b26936ba658f1f6e9bc61e416c07888d4cb5c17a1fbcd1bea8b4e30d464  evals/tasks/quantum/ghz_state_witness/tests.py
8b0496f1b2f2d671774a3ff5ae38bbd3a12764f64a187274b022eb1f0592a0e6  evals/tasks/quantum/grover_oracle_diffusion/candidate.py
eca1461b210a9e9244be9876e7c4cc2ae0648beb6eb167c59247987a2fcc922c  evals/tasks/quantum/grover_oracle_diffusion/tests.py
0b0ac2c05ac0ddbe685a4244e4e39fd315669e1cce18b3546496f3a65414a600  evals/tasks/quantum/maxcut_assignment_enumerator/tests.py
c2ca2881a761af3709496a1598360c4b545cc489822445e30cbd2e7afaf878e7  evals/tasks/quantum/maxcut_partition_ranker/candidate.py
23377a27912b10f10417748b130a25cefa7d84c08fe5f44e3ee49b21ec9da758  evals/tasks/quantum/maxcut_partition_ranker/tests.py
4d96a1e736f4b95157c39e7bba399786142ccd8f9889d49de4d5ef8e73af87a6  evals/tasks/quantum/measurement_bug_repair/tests.py
563553f63aa5bd957cc4e73e52cc787864567e1e479d3199300bda019962bf0b  evals/tasks/quantum/pauli_message_codec/tests.py
3cab7c4111f541c247ff98769efadb772b4f9ca7d9846ea13bce96d3d4137061  evals/tasks/quantum/pennylane_qml_iris_classification/task.json
b8f8cd014abf677dd7f22e509043260db2e15ae2dc02f4bee0e6225bb44fd8b2  evals/tasks/quantum/pennylane_vqe_h2/candidate.py
18f1ff5d5dc2ee486e8a2f0faa6b2a00937cedbed8d967e7534b300eba93718e  evals/tasks/quantum/pennylane_vqe_h2/task.json
0ed7b78ecaaf776fbf8a0dc9e7709d58d17d4ea52c617b6ee3e164686fbd1121  evals/tasks/quantum/phase_estimation_circuit/candidate.py
9e4454a5be086d3484fe0f53fb63167e574baa04c9a632224bc25db34fd01fde  evals/tasks/quantum/phase_estimation_circuit/tests.py
06f85efba02647dc0c70e27450ece118df0ffc54d18d28df046ff319420547a9  evals/tasks/quantum/phase_measurement_register/tests.py
cef961ca651f7d14be1de207da598be883f1b3df1f1aadbec677c7f7ae724d8c  evals/tasks/quantum/phase_register_roundtrip/task.json
710ea354eb1d74d20d464f555428e2d78f77b1d0647cdfc6ab1543798335fe7c  evals/tasks/quantum/qaoa_maxcut/candidate.py
4bbfddd37158e6e2fc233b6feaeac391a929e0f34fcf6c4ce81f5ac9c1343e23  evals/tasks/quantum/qft_phase_pattern/candidate.py
ef7954bc50e7e39bd989a3d0feb0a6bea63b385aebc90c2d3d2215b9505b7b09  evals/tasks/quantum/qft_phase_pattern/tests.py
c7fdd0cdb37181a5d17ab9c2f9cbf2d7f41a877e45a58abed0bd89050cb280dd  evals/tasks/quantum/qiskit_qft_entangled/candidate.py
9847758ddba6fc2e70f1e6673787f0ab7ba3212dd218c4d003df54feec9dadac  evals/tasks/quantum/qiskit_qft_entangled/task.json
56828d0864714775e0c4d6bad5731e7fc1ba05d41bdb561c09030101a531612a  evals/tasks/quantum/quantum_bell_basis_discrimination/candidate.py
8ec6477bb5f1ad67655a1aad8120d4272f0e91eb11377958e17f83042ca1b764  evals/tasks/quantum/quantum_bell_basis_discrimination/task.json
0106c3e28e4406c38988bb6d99e253783e7b65194231471dd94623b6471caeaa  evals/tasks/quantum/quantum_bell_basis_discrimination/tests.py
a6dc2f09d5d1a26fa6a0a7c9bfee82f97277621c53e0cff451aa23148d2c53cc  evals/tasks/quantum/quantum_channel_depolarizing/candidate.py
e35912c10f0414dd665c50acf05ef5edd954aa2a7286177a8b50df8c8d5c207e  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/candidate.py
4b87bf5ec307d1fe6bbc2d06da8c31fe9102ca7dc36617075de3a309a9633784  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/task.json
16c446c9ff37b6000febfc411cfbb9b2afb966415473ac6d7aeeeb3d14019796  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/tests.py
704ae205c1689f1a422be5437f815d3f005cb3e6f9f18e14dce14108f0665bd2  evals/tasks/quantum/quantum_error_correction_shor_9qubit/candidate.py
53a4fca2a1d4bc50bbe1ae037365dfb4cb385867f86f17e43aac1826a49f942a  evals/tasks/quantum/quantum_qaoa_ring4_landscape/candidate.py
18c4c230851bea8b9a7c07e7e63a6c589a7aae0121c925c7464e9f5a169290a3  evals/tasks/quantum/quantum_qaoa_ring4_landscape/task.json
7b0edb9582b791f25e7f037ec2192e022a1aca156523c7a30b7e8b8323390ec0  evals/tasks/quantum/quantum_qaoa_ring4_landscape/tests.py
d120dacccc7a7e5275ae82e8fb51237633b30251f1b1630322d69a5c603ae8ab  evals/tasks/quantum/quantum_qft_periodic_state/candidate.py
ebd267d28641ee82b1ab3eb8cc1311a4404d9c2f4c396fc16e67f54d8f8b2590  evals/tasks/quantum/quantum_qft_periodic_state/task.json
1a5c67ea0d792acfb89b1f145a49f9e6a3b41ac1f5d01b2f2fcb794d67698b54  evals/tasks/quantum/quantum_qft_periodic_state/tests.py
da8a2df5ff111a370dce3dbc544fb0a94070e233d830e0209ae180196175c70a  evals/tasks/quantum/quantum_qml_variational_classifier/candidate.py
3797013aad4f4306494b05d6aaba2bcf58e9c0421399d98704c020004f8a15d7  evals/tasks/quantum/quantum_qml_variational_classifier/task.json
4ceb0643fe809c9d002605f18f949cbcc817ef46d73ee4d583fe6ab7ec99a814  evals/tasks/quantum/quantum_qml_variational_classifier/tests.py
cf077341049dda9bda626fea2988152c5578ed94019bf78f44b27a3004ce7494  evals/tasks/quantum/quantum_shor_phase_error_correction/candidate.py
924f62d00478418c0f8c050e9a5b1fa55d3dcc0c1ec33c2be275793849b99250  evals/tasks/quantum/quantum_shor_phase_error_correction/task.json
caa2f5ad530912bca05b7dc2fd653b545be269b4e2d04afb800316e27637a88d  evals/tasks/quantum/quantum_shor_phase_error_correction/tests.py
2fcbc2262b455b17fb03c676d706d815d17c00cfaeebb59f873860816a83beb4  evals/tasks/quantum/quantum_stabilizer_shor_generators/candidate.py
394cc88cf03ea9fa5455cbf6c5b70ee9322c303a64999ef730a0322765b12c5e  evals/tasks/quantum/quantum_stabilizer_shor_generators/task.json
4b624df712bace522ab885719fdf3c9d7f809a2ecf80332983302ce59c988714  evals/tasks/quantum/quantum_stabilizer_shor_generators/tests.py
94387663f339549e17e7140b689f21568c6aec325f998b43c7363a773d4f0e49  evals/tasks/quantum/quantum_three_qubit_entropy/candidate.py
b2b14d381a003e9b592ab7635309bb6dedf326cc4ee604f200862ee0e31a0216  evals/tasks/quantum/quantum_three_qubit_entropy/task.json
924589a11f316b781a2bcf859349605d26277616b50cd948d45858d67d53e160  evals/tasks/quantum/quantum_three_qubit_entropy/tests.py
4517812d3ba0b406e7d8c8bae538e6d8b98a2169315536e881e8d724567fb644  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/candidate.py
963bb4f6b79e121051a2d333653e000370aae6f3fc2cbf60b15039fc0204bb01  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/task.json
ea61dcafa29bff20cf30e0e9e5a3136f108849fdc60a66ff09ee00b3cadd0141  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/tests.py
20e155a60b412fa0567a163c6351b6ba1e65cd3aeb83aaca6c6d0faa3afe5f18  evals/tasks/quantum/quantum_vqe_heisenberg_energy/candidate.py
8509c851c68dff4c743dd3a7572579698ba9f382bb77f64bd7405dfdb49935fb  evals/tasks/quantum/quantum_vqe_heisenberg_energy/task.json
8a04b56c4c4ab367dc28bd579ad8a921fbca1ebc46270392fb9d89e5b32af16c  evals/tasks/quantum/quantum_vqe_heisenberg_energy/tests.py
7042529da93af3815df7941a9937a1476b1fd18d5571c0605acd617580b174f8  evals/tasks/quantum/stabilizer_tableau_update_repair/tests.py
e1bea2e227a012ae8b066f9cac0e3534a971b56a11270f3c40ca85d23d60a8cd  evals/tasks/quantum/superdense_coding/task.json
e3daa4ff10309b0044f6ed4fe5a707b6992fafcc180c30dd838af7bb906f9b7e  evals/tasks/quantum/superdense_identity_lookup/tests.py
fd6e10cad2e3c9c0d9176eefc5a165c2202b2c4ef97b3d513b64bfa922d3db59  evals/tasks/quantum/superdense_pauli_router/tests.py
dd4ff8fe03ad22e2d37a41683bd166ab787edc7f807dbef473babe54a0a96598  evals/tasks/quantum/teleportation_corrections/tests.py
c125239727ff913543e727979e7aa480341d99331b75f27324782c98793206c2  evals/tasks/quantum/vqe_energy_minimization/candidate.py
5f723b9e328abd5d08462d7dc0ccdb1c395eea31a89357c53e89ed07f16485a0  reports/sapo-holdout-enrichment-manifest-2026-08-24.json
ea5b263226494fa9a5831453e68c3f7a533ebfb2804e14094dc40d66fd890ff2  scripts/ai_launch_sapo_direct.sh
1a165df6e63597c2c89478bbfe431e269ba8a4d6bcb51eff5842cabbff67d9d4  scripts/asi2_launch_grpo_27b_selfeval.sh
63158871a80cfe275d168c0519149b88abdb707bae69b7b5a6e5036fff1159a9  scripts/asi2_watchdog_relaunch.sh
1d6e5b8078086bcd2bbcc6f463d314c23ad6d979d2b132bea519f742058853f4  scripts/asi3_launch_grpo_direct.sh
77bb097c26c6e3fbddb7911d92ed534f387eea7d1084b3da70efab32a9d3c94f  scripts/build_grpo_v8_manifest.py
c07351d46a03ae1669f6d5430dee7b966b8dce80ae6e23390220d7b32d482903  scripts/decide_sapo_promotion_gate.py
7c6645277836f3b9fe4696facc13ba50d976ca61684c969492082f68127d2938  scripts/fine_score.py
94274f251f762a8c5d7d9c4e3bcdfd1d482551729b6ee032f55105a3985bcc3e  scripts/fv_gspo_repair_sidecar.sh
5c769d6c9626f1551a48e4db0478ec4cae299140d740dcaafe251ba67970f989  scripts/run_hf_pass1_eval.py
8d630261dc6d5d0e51a147b304143fd6bd484568c9696014ec2af61809042f44  scripts/sapo_drift_watch.py
29defbe7f9fbb11e506352c27696cfafad0ceec1fd8959e3e2344429fafcb8c1  scripts/sapo_status_snapshot.py
7890847631dc903c6e07574aac47cb71f2dbf3c952527420ef6e22c768313f83  scripts/submit_asi2_grpo_27b_selfeval_task.sh
b3cacae4017cae68b74c9db162e20521a847a41a8ba622770f7a33b79e5063c2  tests/test_asi3_sapo_launcher_readiness.py
77b7284078155151c4b493e8eb4ce83e22ebce2b014fb76057e0f83b6947aab5  tests/test_fine_score.py
a97649ef1227988886fd29ad7fd5388430ac66248de53927a20e1de0aa72f5ca  tests/test_grpo_train_pass_truncation.py
9bf0a3c28b5dcde6dc456f0c45c7ae4001870ca6114103f89681ba3d40a1af80  tests/test_grpo_trainer_metrics.py
0f9d1b0f62e9c9a825061fd54c6ae1f71fd902733fb592a0beac82a0cd6df803  tests/test_holdout_enrichment_invariance.py
f43b364994eb1dfcdceb7314127da94a7154d292907f9c781119b54dd5fa3824  tests/test_promotion_eval_adapter_merge.py
7f37d88898c639d677eaeebd7c2a914f9710a6a71a9547cfa8956b16698a2b08  tests/test_sapo_curriculum_holdout_adjacent.py
9348eb35c72f1e5df7f9582cbcc8ebd2925455ce8a099429483eb411c02f52f6  tests/test_sapo_drift_watch.py
d79ae1884791178a1fd2902224055c3ba4939b531e4d28ba74ed18bd191e71f4  tests/test_sapo_loss.py
b7b4ad1b64e22d99c268d948583c00b419f6f0354d91e270d2146dab9ad94dbc  tests/test_sapo_promotion_pipeline_hardening.py
bc467299730e8899a5f9bb7962de80e94c9af423e2cd6a8d10c1fcc9fd8e3e99  training/grpo_trainer.py
426edf9301b7349eeb6dddd5af8f811d88aeef20887993c96b2ab7140df0d297  training/grpo_utils.py
76a0106a456cea4652535dfe4ba9dadeac6825cae4ba3196e50e3a88ab4305b9  evals/tasks/quantum/pennylane_vqe_h2/tests.py
517980777e2e61acef6ed4cd869c38db93a50e75bf29628d73739855a3c2ff9f  tests/test_grpo_trainer_sigterm.py
15bb6ca5d7394cb4273f7060c3b2cb36c3b38991fdc8cf0757a7b3aa9b07104b  tests/test_grpo_trainer_resume.py
c44fd773e1c799c310bc13c58211c83182cc2ab8438e61aefeca0dace399e207  tests/test_grpo_trainer_eval_results.py
6363e022f9c0d6a16200f385e9a5a845df5b0c93e66abcb9389c648fa4235a9c  tests/test_pennylane_vqe_h2_scorer_versions.py

### r9 retry log (14:52Z)
- 14:47Z: gate recheck — fine_score.py:319 STILL live zip(strict=True), hash
  7c664527… unchanged → BLOCKED (py3.9 gate).
- 14:52Z: LOCKS appeared — `training/grpo_trainer.py.lock` holder **qa-lane**
  (14:48:27Z, "generation-eos-fence-stop", active <2h) +
  `tests/test_grpo_trainer_generation_stop.py.lock` holder qa-lane (14:51:47Z;
  that test is NOT a bundle member). grpo_trainer.py IS a member → per
  tree-lock protocol r9 must NOT bundle it → BLOCKED (tree lock) in addition
  to the py3.9 gate. Stale-break policy: locks <2h are not stale; manager
  only. Retrying ~5 min cadence.
- 14:52Z recheck: gate STILL blocked (fine_score.py:319, 7c664527… unchanged);
  grpo_trainer.py now 8c1d558c… (qa-lane editing under lock — mid-edit, must
  not bundle anyway); both qa-lane locks active. r9 DEFERRED, dual-blocked.
  Next retry: re-run gate + lock scan (protocol ~5 min); build r9 immediately
  when (a) fine_score.py:319 clean, (b) no active lock on any member.
  Prepared bundle state: 106-member explicit list + per-member hashes recorded
  above; tar command ready (`tar -czf tmp/sapo-relaunch-lr2e4-20260825-r9.tgz
  -T /tmp/r9_members.txt`); deploy procedure as r5-r8.

### r9 DEPLOYED — final record (lane re-invoke 2026-08-26, ~22:5x CST / ~14:5xZ)
- Conditions met: locks dir EMPTY; fine_score.py gate CLEAN (QA fixed :319/:332,
  hash ecdd038d…, 0 strict=True in file). Built r9: explicit list = r8 manifest
  members MINUS nested tmp artifact + 3 evals tests.py (pennylane_vqe_h2,
  qiskit_qft_entangled, pennylane_qml_iris_classification) + 14 QA test files
  (generation_stop, self_eval, breakers, loss_stats_router, main_failclosed,
  execute_run, run_eval_scoring, prepare_prompts_coverage, sapo_reward_audit_cli,
  sapo_prompt_audit_cli, sigterm, resume, eval_results, pennylane_vqe_h2_scorer_versions)
  → **118 members**.
- PY3.9 gate: FULL SCAN of all 118 member .py — 0 real hits (test_fine_score.py
  strict= hits are docstrings; QA added source-level regression guard
  test_format_report_deltas_use_py39_safe_zip). PASS.
- Build-time integrity: fresh hashes computed at build; tar member-hash ==
  manifest (no stale members); manifest == tree at build AND after deploy
  (rc=0 both checks).
- Deploy: 63×6000B chunks, 0 failures, chunk audit clean (62×6000 + 628);
  box sha 7f7404d2… == local, 279471 B both sides.
- Run tree refreshed: 5 critical files == r9 manifest; scripts/fine_score.py on
  box = ecdd038d… (py3.9-safe, 0 strict=True) — r8's poisoned copy REPLACED.
- Residual drift: NONE at cycle end (manifest == tree).
- NEXT CYCLE: standard freshness check (r9 manifest vs tree) + lock scan.

### r9 final manifest — full member list + hashes (118 members)
85106d8e4c0c337edbc95eec2972d363c96f50f2d91c0d4404438dff386c4f27  configs/rl/qwen36_27b_fv_gspo_asi2.json
7b8bdc04fe2a6b41ba867facdebe04170bf7c864a2e09c2b446718764f060f18  evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt
0108c020f916b8dbf8ab16d08560d0057265ecaee0f5f37289620a7e0e8f0e54  evals/tasks/quantum/bell_pair_construction/candidate.py
9f6bf09c6019fb84748c9df10638291fd62bfcc90fa049642b980a1541b52403  evals/tasks/quantum/bell_pair_construction/tests.py
976677faa3f3138f9ac53c1435cbb8002ef380dabff6dc74f2f4fc4821620da1  evals/tasks/quantum/binary_measurement_decoder/task.json
114bd9cf91467960db9b629475aad730929625271b7ea76e453199b3b40b6690  evals/tasks/quantum/binary_measurement_decoder/tests.py
48d45ea9b46d7e54f23edbb62e94e7fb132884250506e342c460c7c9bba2d7db  evals/tasks/quantum/bitstring_maxcut_landscape/tests.py
4b4c0ea792f29454d0430a473cdaa778bc1432801c7f2c8c0d935520c89a29e5  evals/tasks/quantum/circuit_phase_repair/tests.py
6ee4de0769c7dd49dfa317d83035cc870c83020b9094cac23d5724f6f30fbdc6  evals/tasks/quantum/density_matrix_partial_trace/candidate.py
311688fed1cf708c6cbbe7854c724c422758526c1e6d13f12d1f1d1eb409e804  evals/tasks/quantum/error_detection_bit_flip/tests.py
18ed2cb56ee7c96529c53d65921deb4c44dcfdedce5d2bb275e36b714d59e6ae  evals/tasks/quantum/gate_alias_casefold_barrier/candidate.py
5feaa43a0f846f7d605e3b9ee6946ba4e4d53e61da07ed4ea7d40117218db661  evals/tasks/quantum/gate_alias_casefold_barrier/tests.py
f1cf1e1144aeef96acac9f527b6b3d96ea9c0c938121a48d9f2fc735599d9525  evals/tasks/quantum/gate_alias_normalization/task.json
4e17b821390f6916b8fd29d64061489a7bde5367a648b8227b26276a79b97143  evals/tasks/quantum/gate_alias_normalization/tests.py
fb4c96d30a8260ad6aa9895e3c2673d3dd7cc264d9f0958bfa0d9a163eb7760b  evals/tasks/quantum/gate_alias_registry_cleanup/candidate.py
d02d9e3673930d64c3dd1483d8ebf00c6b23764fa18fe542f16930313722100f  evals/tasks/quantum/gate_alias_registry_cleanup/tests.py
8cba17a29939f736e18e729a86fbbef83be4db9811890f2467dac666f805d931  evals/tasks/quantum/gate_token_canonicalizer/tests.py
7a6d4835c6cf027a323a720cd9698cf80560470c9c3aba7652965da3aeaac224  evals/tasks/quantum/ghz_state_witness/candidate.py
48db0b26936ba658f1f6e9bc61e416c07888d4cb5c17a1fbcd1bea8b4e30d464  evals/tasks/quantum/ghz_state_witness/tests.py
8b0496f1b2f2d671774a3ff5ae38bbd3a12764f64a187274b022eb1f0592a0e6  evals/tasks/quantum/grover_oracle_diffusion/candidate.py
eca1461b210a9e9244be9876e7c4cc2ae0648beb6eb167c59247987a2fcc922c  evals/tasks/quantum/grover_oracle_diffusion/tests.py
0b0ac2c05ac0ddbe685a4244e4e39fd315669e1cce18b3546496f3a65414a600  evals/tasks/quantum/maxcut_assignment_enumerator/tests.py
c2ca2881a761af3709496a1598360c4b545cc489822445e30cbd2e7afaf878e7  evals/tasks/quantum/maxcut_partition_ranker/candidate.py
23377a27912b10f10417748b130a25cefa7d84c08fe5f44e3ee49b21ec9da758  evals/tasks/quantum/maxcut_partition_ranker/tests.py
4d96a1e736f4b95157c39e7bba399786142ccd8f9889d49de4d5ef8e73af87a6  evals/tasks/quantum/measurement_bug_repair/tests.py
563553f63aa5bd957cc4e73e52cc787864567e1e479d3199300bda019962bf0b  evals/tasks/quantum/pauli_message_codec/tests.py
3cab7c4111f541c247ff98769efadb772b4f9ca7d9846ea13bce96d3d4137061  evals/tasks/quantum/pennylane_qml_iris_classification/task.json
8982efe7a2fdcde6fa723d77db797137a741508ebda8d2f4cc0610ebc25c4829  evals/tasks/quantum/pennylane_qml_iris_classification/tests.py
b8f8cd014abf677dd7f22e509043260db2e15ae2dc02f4bee0e6225bb44fd8b2  evals/tasks/quantum/pennylane_vqe_h2/candidate.py
18f1ff5d5dc2ee486e8a2f0faa6b2a00937cedbed8d967e7534b300eba93718e  evals/tasks/quantum/pennylane_vqe_h2/task.json
76a0106a456cea4652535dfe4ba9dadeac6825cae4ba3196e50e3a88ab4305b9  evals/tasks/quantum/pennylane_vqe_h2/tests.py
0ed7b78ecaaf776fbf8a0dc9e7709d58d17d4ea52c617b6ee3e164686fbd1121  evals/tasks/quantum/phase_estimation_circuit/candidate.py
9e4454a5be086d3484fe0f53fb63167e574baa04c9a632224bc25db34fd01fde  evals/tasks/quantum/phase_estimation_circuit/tests.py
06f85efba02647dc0c70e27450ece118df0ffc54d18d28df046ff319420547a9  evals/tasks/quantum/phase_measurement_register/tests.py
cef961ca651f7d14be1de207da598be883f1b3df1f1aadbec677c7f7ae724d8c  evals/tasks/quantum/phase_register_roundtrip/task.json
710ea354eb1d74d20d464f555428e2d78f77b1d0647cdfc6ab1543798335fe7c  evals/tasks/quantum/qaoa_maxcut/candidate.py
4bbfddd37158e6e2fc233b6feaeac391a929e0f34fcf6c4ce81f5ac9c1343e23  evals/tasks/quantum/qft_phase_pattern/candidate.py
ef7954bc50e7e39bd989a3d0feb0a6bea63b385aebc90c2d3d2215b9505b7b09  evals/tasks/quantum/qft_phase_pattern/tests.py
c7fdd0cdb37181a5d17ab9c2f9cbf2d7f41a877e45a58abed0bd89050cb280dd  evals/tasks/quantum/qiskit_qft_entangled/candidate.py
9847758ddba6fc2e70f1e6673787f0ab7ba3212dd218c4d003df54feec9dadac  evals/tasks/quantum/qiskit_qft_entangled/task.json
5fe817cf31b288e9ca3c1b481818a99a390498e15057f1da865fadcc1ecb169c  evals/tasks/quantum/qiskit_qft_entangled/tests.py
56828d0864714775e0c4d6bad5731e7fc1ba05d41bdb561c09030101a531612a  evals/tasks/quantum/quantum_bell_basis_discrimination/candidate.py
8ec6477bb5f1ad67655a1aad8120d4272f0e91eb11377958e17f83042ca1b764  evals/tasks/quantum/quantum_bell_basis_discrimination/task.json
0106c3e28e4406c38988bb6d99e253783e7b65194231471dd94623b6471caeaa  evals/tasks/quantum/quantum_bell_basis_discrimination/tests.py
a6dc2f09d5d1a26fa6a0a7c9bfee82f97277621c53e0cff451aa23148d2c53cc  evals/tasks/quantum/quantum_channel_depolarizing/candidate.py
e35912c10f0414dd665c50acf05ef5edd954aa2a7286177a8b50df8c8d5c207e  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/candidate.py
4b87bf5ec307d1fe6bbc2d06da8c31fe9102ca7dc36617075de3a309a9633784  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/task.json
16c446c9ff37b6000febfc411cfbb9b2afb966415473ac6d7aeeeb3d14019796  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/tests.py
704ae205c1689f1a422be5437f815d3f005cb3e6f9f18e14dce14108f0665bd2  evals/tasks/quantum/quantum_error_correction_shor_9qubit/candidate.py
53a4fca2a1d4bc50bbe1ae037365dfb4cb385867f86f17e43aac1826a49f942a  evals/tasks/quantum/quantum_qaoa_ring4_landscape/candidate.py
18c4c230851bea8b9a7c07e7e63a6c589a7aae0121c925c7464e9f5a169290a3  evals/tasks/quantum/quantum_qaoa_ring4_landscape/task.json
7b0edb9582b791f25e7f037ec2192e022a1aca156523c7a30b7e8b8323390ec0  evals/tasks/quantum/quantum_qaoa_ring4_landscape/tests.py
d120dacccc7a7e5275ae82e8fb51237633b30251f1b1630322d69a5c603ae8ab  evals/tasks/quantum/quantum_qft_periodic_state/candidate.py
ebd267d28641ee82b1ab3eb8cc1311a4404d9c2f4c396fc16e67f54d8f8b2590  evals/tasks/quantum/quantum_qft_periodic_state/task.json
1a5c67ea0d792acfb89b1f145a49f9e6a3b41ac1f5d01b2f2fcb794d67698b54  evals/tasks/quantum/quantum_qft_periodic_state/tests.py
da8a2df5ff111a370dce3dbc544fb0a94070e233d830e0209ae180196175c70a  evals/tasks/quantum/quantum_qml_variational_classifier/candidate.py
3797013aad4f4306494b05d6aaba2bcf58e9c0421399d98704c020004f8a15d7  evals/tasks/quantum/quantum_qml_variational_classifier/task.json
4ceb0643fe809c9d002605f18f949cbcc817ef46d73ee4d583fe6ab7ec99a814  evals/tasks/quantum/quantum_qml_variational_classifier/tests.py
cf077341049dda9bda626fea2988152c5578ed94019bf78f44b27a3004ce7494  evals/tasks/quantum/quantum_shor_phase_error_correction/candidate.py
924f62d00478418c0f8c050e9a5b1fa55d3dcc0c1ec33c2be275793849b99250  evals/tasks/quantum/quantum_shor_phase_error_correction/task.json
caa2f5ad530912bca05b7dc2fd653b545be269b4e2d04afb800316e27637a88d  evals/tasks/quantum/quantum_shor_phase_error_correction/tests.py
2fcbc2262b455b17fb03c676d706d815d17c00cfaeebb59f873860816a83beb4  evals/tasks/quantum/quantum_stabilizer_shor_generators/candidate.py
394cc88cf03ea9fa5455cbf6c5b70ee9322c303a64999ef730a0322765b12c5e  evals/tasks/quantum/quantum_stabilizer_shor_generators/task.json
4b624df712bace522ab885719fdf3c9d7f809a2ecf80332983302ce59c988714  evals/tasks/quantum/quantum_stabilizer_shor_generators/tests.py
94387663f339549e17e7140b689f21568c6aec325f998b43c7363a773d4f0e49  evals/tasks/quantum/quantum_three_qubit_entropy/candidate.py
b2b14d381a003e9b592ab7635309bb6dedf326cc4ee604f200862ee0e31a0216  evals/tasks/quantum/quantum_three_qubit_entropy/task.json
924589a11f316b781a2bcf859349605d26277616b50cd948d45858d67d53e160  evals/tasks/quantum/quantum_three_qubit_entropy/tests.py
4517812d3ba0b406e7d8c8bae538e6d8b98a2169315536e881e8d724567fb644  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/candidate.py
963bb4f6b79e121051a2d333653e000370aae6f3fc2cbf60b15039fc0204bb01  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/task.json
ea61dcafa29bff20cf30e0e9e5a3136f108849fdc60a66ff09ee00b3cadd0141  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/tests.py
20e155a60b412fa0567a163c6351b6ba1e65cd3aeb83aaca6c6d0faa3afe5f18  evals/tasks/quantum/quantum_vqe_heisenberg_energy/candidate.py
8509c851c68dff4c743dd3a7572579698ba9f382bb77f64bd7405dfdb49935fb  evals/tasks/quantum/quantum_vqe_heisenberg_energy/task.json
8a04b56c4c4ab367dc28bd579ad8a921fbca1ebc46270392fb9d89e5b32af16c  evals/tasks/quantum/quantum_vqe_heisenberg_energy/tests.py
7042529da93af3815df7941a9937a1476b1fd18d5571c0605acd617580b174f8  evals/tasks/quantum/stabilizer_tableau_update_repair/tests.py
e1bea2e227a012ae8b066f9cac0e3534a971b56a11270f3c40ca85d23d60a8cd  evals/tasks/quantum/superdense_coding/task.json
e3daa4ff10309b0044f6ed4fe5a707b6992fafcc180c30dd838af7bb906f9b7e  evals/tasks/quantum/superdense_identity_lookup/tests.py
fd6e10cad2e3c9c0d9176eefc5a165c2202b2c4ef97b3d513b64bfa922d3db59  evals/tasks/quantum/superdense_pauli_router/tests.py
dd4ff8fe03ad22e2d37a41683bd166ab787edc7f807dbef473babe54a0a96598  evals/tasks/quantum/teleportation_corrections/tests.py
c125239727ff913543e727979e7aa480341d99331b75f27324782c98793206c2  evals/tasks/quantum/vqe_energy_minimization/candidate.py
5f723b9e328abd5d08462d7dc0ccdb1c395eea31a89357c53e89ed07f16485a0  reports/sapo-holdout-enrichment-manifest-2026-08-24.json
ea5b263226494fa9a5831453e68c3f7a533ebfb2804e14094dc40d66fd890ff2  scripts/ai_launch_sapo_direct.sh
1a165df6e63597c2c89478bbfe431e269ba8a4d6bcb51eff5842cabbff67d9d4  scripts/asi2_launch_grpo_27b_selfeval.sh
63158871a80cfe275d168c0519149b88abdb707bae69b7b5a6e5036fff1159a9  scripts/asi2_watchdog_relaunch.sh
1d6e5b8078086bcd2bbcc6f463d314c23ad6d979d2b132bea519f742058853f4  scripts/asi3_launch_grpo_direct.sh
77bb097c26c6e3fbddb7911d92ed534f387eea7d1084b3da70efab32a9d3c94f  scripts/build_grpo_v8_manifest.py
c07351d46a03ae1669f6d5430dee7b966b8dce80ae6e23390220d7b32d482903  scripts/decide_sapo_promotion_gate.py
ecdd038db0502619cf97591ad53ea9a6dcbbe146b39fc27199fbc0c0f6d52433  scripts/fine_score.py
94274f251f762a8c5d7d9c4e3bcdfd1d482551729b6ee032f55105a3985bcc3e  scripts/fv_gspo_repair_sidecar.sh
5c769d6c9626f1551a48e4db0478ec4cae299140d740dcaafe251ba67970f989  scripts/run_hf_pass1_eval.py
8d630261dc6d5d0e51a147b304143fd6bd484568c9696014ec2af61809042f44  scripts/sapo_drift_watch.py
29defbe7f9fbb11e506352c27696cfafad0ceec1fd8959e3e2344429fafcb8c1  scripts/sapo_status_snapshot.py
7890847631dc903c6e07574aac47cb71f2dbf3c952527420ef6e22c768313f83  scripts/submit_asi2_grpo_27b_selfeval_task.sh
b3cacae4017cae68b74c9db162e20521a847a41a8ba622770f7a33b79e5063c2  tests/test_asi3_sapo_launcher_readiness.py
6354b5c4428627270d8a4b2da06aec2497f9880a307beedb57e81d4f19c612cc  tests/test_execute_run.py
627394e53c866af33e5f70c42224e2d1e79f635bb53da040701afe0c2bc9b954  tests/test_fine_score.py
a97649ef1227988886fd29ad7fd5388430ac66248de53927a20e1de0aa72f5ca  tests/test_grpo_train_pass_truncation.py
8054133605928a8f720c8c6bb5a1a06ca6751e99d206d3bec80e9df68ff2cf22  tests/test_grpo_trainer_breakers.py
c44fd773e1c799c310bc13c58211c83182cc2ab8438e61aefeca0dace399e207  tests/test_grpo_trainer_eval_results.py
c015446a3017307a63e1c3baef14a7e99803fc53a629baea8f3d8231a83170ef  tests/test_grpo_trainer_generation_stop.py
d0b8f6442d93c8fecfed3bed62531253c991f33734b26dff94cf158f7caba3e1  tests/test_grpo_trainer_loss_stats_router.py
6382597ecd430a1e301215bf33fa3eed081eed6adc73c15ed9c0400bc65df86c  tests/test_grpo_trainer_main_failclosed.py
9bf0a3c28b5dcde6dc456f0c45c7ae4001870ca6114103f89681ba3d40a1af80  tests/test_grpo_trainer_metrics.py
15bb6ca5d7394cb4273f7060c3b2cb36c3b38991fdc8cf0757a7b3aa9b07104b  tests/test_grpo_trainer_resume.py
181b1a4f15efe4c1bf31ff34dca28d814ec1b0e937d6ba464aad119ac6fb1a59  tests/test_grpo_trainer_self_eval.py
517980777e2e61acef6ed4cd869c38db93a50e75bf29628d73739855a3c2ff9f  tests/test_grpo_trainer_sigterm.py
0f9d1b0f62e9c9a825061fd54c6ae1f71fd902733fb592a0beac82a0cd6df803  tests/test_holdout_enrichment_invariance.py
6363e022f9c0d6a16200f385e9a5a845df5b0c93e66abcb9389c648fa4235a9c  tests/test_pennylane_vqe_h2_scorer_versions.py
caea3662eb1cb632fd4c7b881e0081b157cb7708325739e52a4f45dbbc5accdb  tests/test_prepare_prompts_coverage.py
f43b364994eb1dfcdceb7314127da94a7154d292907f9c781119b54dd5fa3824  tests/test_promotion_eval_adapter_merge.py
2bcdae7e8bc4407dd55d0be549b910c2305d80a4a9f7f3a8b59f7f58afa49c6d  tests/test_run_eval_scoring.py
7f37d88898c639d677eaeebd7c2a914f9710a6a71a9547cfa8956b16698a2b08  tests/test_sapo_curriculum_holdout_adjacent.py
9348eb35c72f1e5df7f9582cbcc8ebd2925455ce8a099429483eb411c02f52f6  tests/test_sapo_drift_watch.py
d79ae1884791178a1fd2902224055c3ba4939b531e4d28ba74ed18bd191e71f4  tests/test_sapo_loss.py
b7b4ad1b64e22d99c268d948583c00b419f6f0354d91e270d2146dab9ad94dbc  tests/test_sapo_promotion_pipeline_hardening.py
8799b1a8675580909b3a50cc8ebdb4cec268513ba3282776abb6ba9fa47a8927  tests/test_sapo_prompt_audit_cli.py
515845b85b41d3421e849816649d5fad7f07e22ed3e631c12727f6960f736ff7  tests/test_sapo_reward_audit_cli.py
fb2675d2466818350b9208e087e1bf45435670a745085ef509d9fe7502be8b3c  training/grpo_trainer.py
426edf9301b7349eeb6dddd5af8f811d88aeef20887993c96b2ab7140df0d297  training/grpo_utils.py

## CORRECTNESS REGISTER GATE (manager rule 2026-08-26 09:48 CST, applies r10+)
Before tarring ANY r10+ bundle, EVERY critical file must tick ALL register
items (STATUS.md:318-319; scope: training/grpo_trainer.py, training/grpo_utils.py,
eval runners/scorers, launchers/configs). ANY unticked item = NO BUNDLE.
Evidence sources (verified by this lane, not assumed):
1. TESTS GREEN — /tmp/sapo_tests_RED must be ABSENT (testorch removes on green)
   + testorch.md green record. RED present = block.
2. PY3.9 SCAN — this lane's grep gate over all bundled .py: `zip(.*strict=`,
   `strict=True/False` — any real call = fail. (strict= kwarg is py3.10-only,
   even strict=False.)
3. DEPMATRIX — depmatrix role-file status (.sapo-loop/depmatrix.md absent =
   UNTICKED; lane #24 must record box+local lib matrix GO).
4. CHANGE-REVIEWER — /tmp/sapo_review_BLOCK absent AND reviewer.md GO verdict
   for the wave (absence alone is NOT a pass).
5. DEBUG-LANE bundle-diff — debuglane.md verdict for the generation (rN
   diff-vs-previous review).
6. LAUNCH-SIMULATOR — /tmp/sapo_launchsim_BLOCK absent AND launchsim smoke
   evidence (tiny-model load→step→loss→save→SIGTERM→resume_state).
7. SHA-PINNED — manifest member hashes == tree at build (this lane).
Record the register table per generation below.

## REGISTER TABLE — r10 eligibility check (2026-08-26 09:5x CST, tree cfb22a83 wave)
Scope rows = critical files in register scope. Ticks: Y=evidence, N=unticked, B=blocked.
| critical file | tests-green | py39 | depmatrix | reviewer | debug-diff | launchsim | sha-pinned |
|---|---|---|---|---|---|---|---|
| training/grpo_trainer.py | N (RED marker) | Y | N | N | N | N | Y (at build) |
| training/grpo_utils.py | N (RED marker) | **B** (zip strict=False :534) | N | N | N | N | Y (at build) |
| scripts/run_hf_pass1_eval.py | N (RED marker) | Y | N | N | N | N | Y (at build) |
| scripts/fine_score.py | N (RED marker) | Y (QA fix held) | N | N | N | N | Y (at build) |
| launchers (asi2/asi3/ai_launch) | N (RED marker) | Y | N | N | N | N | Y (at build) |
| configs/rl/qwen36_27b_fv_gspo_asi2.json | n/a | n/a | N | N | N | N | Y (at build) |
VERDICT: **r10 NO BUNDLE** — 6/6 critical files unticked on ≥4 items; py3.9
gate FAILS on grpo_utils.py:534 (zip strict=False, py3.10-only kwarg; tree hash
cfb22a83…, added after r9 — r9 bundle itself verified clean). Tests RED marker
present (116 failed 23:05 CST; 2 actionable at write: fine_score:332 — since
FIXED (ecdd038d→7913e614, scan clean), + 2 reference candidates qiskit_qft_entangled/
pennylane_qml_iris_classification — QA wave reported fixed; marker NOT yet
removed by testorch). depmatrix role file MISSING. No reviewer/debug/launchsim
verdicts for this wave. Deployed reference stays r9 (verified both sides).
NEXT CYCLE: re-scan register; r10 tar allowed ONLY when table fully ticked.

## REGISTER RE-SCAN — r10 eligibility (2026-08-26 ~10:0x CST, post-QA 10:04 wave)
Coordinator re-invoke: re-tick every register item vs CURRENT tree.
Evidence re-verified this cycle:
- grpo_utils.py:534 zip(strict=False): FIXED (plain zip + length-guard note,
  source-guard test in tests/test_grpo_utils.py) — scan confirms only the
  :1392 comment remains.
- sapo_drift_watch.py: `from __future__ import annotations` at line 3 (F2
  resolved). eval_100_reeval.py: new, future-import landed (coordinator-named).
- Full critical-scope strict-zip scan: CLEAN. Remaining hits = holdout-contract
  evals/tasks/quantum/* baselines (13 files, zip(strict=False)) — SAFE on box
  py3.11.14 per depmatrix §2.4 (trainer/eval runners never run under .venv
  py3.9.6); recorded non-blocking baseline.
- depmatrix.md EXISTS (09:57, lane #24): matrix pinned both sides (local
  py3.9.6 vs box py3.11.14), 4 scorer shas verified deployed, F1-F4 documented.
  TICK: Y (no open blocker in scope; F1 latent).
- QA lane report (qa.md tail): 281 tests green across 24 suites; locks held +
  released (lock scan confirms empty); fine_score length guard restored;
  source guards extended (fine_score/model_judge/reward-audit/prompt-audit).
- testorch: /tmp/sapo_tests_RED STILL PRESENT (mtime 08-25 23:01, not cleared
  despite 281-green wave) — marker is this lane's evidence; NOT removed by me.

### r10 register table (re-scan 2026-08-26 10:0x CST)
| tick | status | evidence |
|---|---|---|
| 1 tests-green | **N** | /tmp/sapo_tests_RED present (testorch must clear; 281 green reported) |
| 2 py3.9 scan | Y | critical scope clean; baselines documented (depmatrix §2.4) |
| 3 depmatrix | Y | depmatrix.md pinned matrix + sweeps + deployed-sha verify |
| 4 change-reviewer | **N** | reviewer.md WAVE-F in progress (snapshot 09:50; verdict pending) |
| 5 debug bundle-diff | **N** | debuglane r9-era verdict only; r10 wave review pending |
| 6 launchsim smoke | **N** | /tmp/sapo_launchsim/ evidence complete (trainer_smoke.log 10:05, run_out: adapter/eval_results/grpo_metrics/resume_state/launch_config) — explicit PASS verdict not yet recorded |
| 7 sha-pinned | Y at build | manifest==tree; candidate hashes below |
VERDICT: r10 NOT buildable yet — 4 genuinely-unticked (exactly the
coordinator-expected set: testorch RED clearing, launchsim PASS, reviewer +
debug verdicts). NO TAR until all tick. r9 remains deployed reference.
### r10 prepared candidate (build-ready; final set confirmed by reviewer/
debug wave-release deltas at build time): 136 members = r9 manifest (118) +
18 wave files (scripts/sapo_reward_audit.py, scripts/calibrate_model_judge.py,
scripts/report_base_adapter_comprehensive.py, scripts/eval_100_reeval.py,
training/compat.py [imported by grpo_trainer.py — required],
evals/runner/seed_run_with_references.py, tests/{test_sapo_reward_audit,
test_sapo_status_snapshot,test_grpo_utils,test_sapo_eval_security,test_compat,
test_model_judge,test_report_base_adapter_comprehensive,
test_holdout_scorer_version_awareness,test_model_family_support,
test_single_candidate_eval,test_seed_run_with_references,
test_grpo_rollout_mix_entropy_floor}.py). EXCLUDED (legacy, out of loop path):
training/{qwen35b_benchmark_rlvr_grpo,agentic_grpo_trainer,artifact_scoring}.py
(zip-strict baseline; only used by non-bundled distill scripts),
scripts/{sapo_math_audit_step_records,repair_quantum_distillation_203,
teacher_question_generator,build_mixed_fast_mini}.py,
scripts/fixes_v3_round2/row_89.py, reports/*diversity_audit*.json.
### r10 candidate manifest (136 members, sha256)
85106d8e4c0c337edbc95eec2972d363c96f50f2d91c0d4404438dff386c4f27  configs/rl/qwen36_27b_fv_gspo_asi2.json
7b8bdc04fe2a6b41ba867facdebe04170bf7c864a2e09c2b446718764f060f18  evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt
a181cd994245f51a605cb20f69ae17da2f2cf3a06c648d2bcf066beec5d0dbe4  evals/runner/seed_run_with_references.py
0108c020f916b8dbf8ab16d08560d0057265ecaee0f5f37289620a7e0e8f0e54  evals/tasks/quantum/bell_pair_construction/candidate.py
9f6bf09c6019fb84748c9df10638291fd62bfcc90fa049642b980a1541b52403  evals/tasks/quantum/bell_pair_construction/tests.py
976677faa3f3138f9ac53c1435cbb8002ef380dabff6dc74f2f4fc4821620da1  evals/tasks/quantum/binary_measurement_decoder/task.json
114bd9cf91467960db9b629475aad730929625271b7ea76e453199b3b40b6690  evals/tasks/quantum/binary_measurement_decoder/tests.py
48d45ea9b46d7e54f23edbb62e94e7fb132884250506e342c460c7c9bba2d7db  evals/tasks/quantum/bitstring_maxcut_landscape/tests.py
4b4c0ea792f29454d0430a473cdaa778bc1432801c7f2c8c0d935520c89a29e5  evals/tasks/quantum/circuit_phase_repair/tests.py
6ee4de0769c7dd49dfa317d83035cc870c83020b9094cac23d5724f6f30fbdc6  evals/tasks/quantum/density_matrix_partial_trace/candidate.py
311688fed1cf708c6cbbe7854c724c422758526c1e6d13f12d1f1d1eb409e804  evals/tasks/quantum/error_detection_bit_flip/tests.py
18ed2cb56ee7c96529c53d65921deb4c44dcfdedce5d2bb275e36b714d59e6ae  evals/tasks/quantum/gate_alias_casefold_barrier/candidate.py
5feaa43a0f846f7d605e3b9ee6946ba4e4d53e61da07ed4ea7d40117218db661  evals/tasks/quantum/gate_alias_casefold_barrier/tests.py
f1cf1e1144aeef96acac9f527b6b3d96ea9c0c938121a48d9f2fc735599d9525  evals/tasks/quantum/gate_alias_normalization/task.json
4e17b821390f6916b8fd29d64061489a7bde5367a648b8227b26276a79b97143  evals/tasks/quantum/gate_alias_normalization/tests.py
fb4c96d30a8260ad6aa9895e3c2673d3dd7cc264d9f0958bfa0d9a163eb7760b  evals/tasks/quantum/gate_alias_registry_cleanup/candidate.py
d02d9e3673930d64c3dd1483d8ebf00c6b23764fa18fe542f16930313722100f  evals/tasks/quantum/gate_alias_registry_cleanup/tests.py
8cba17a29939f736e18e729a86fbbef83be4db9811890f2467dac666f805d931  evals/tasks/quantum/gate_token_canonicalizer/tests.py
7a6d4835c6cf027a323a720cd9698cf80560470c9c3aba7652965da3aeaac224  evals/tasks/quantum/ghz_state_witness/candidate.py
48db0b26936ba658f1f6e9bc61e416c07888d4cb5c17a1fbcd1bea8b4e30d464  evals/tasks/quantum/ghz_state_witness/tests.py
8b0496f1b2f2d671774a3ff5ae38bbd3a12764f64a187274b022eb1f0592a0e6  evals/tasks/quantum/grover_oracle_diffusion/candidate.py
eca1461b210a9e9244be9876e7c4cc2ae0648beb6eb167c59247987a2fcc922c  evals/tasks/quantum/grover_oracle_diffusion/tests.py
0b0ac2c05ac0ddbe685a4244e4e39fd315669e1cce18b3546496f3a65414a600  evals/tasks/quantum/maxcut_assignment_enumerator/tests.py
c2ca2881a761af3709496a1598360c4b545cc489822445e30cbd2e7afaf878e7  evals/tasks/quantum/maxcut_partition_ranker/candidate.py
23377a27912b10f10417748b130a25cefa7d84c08fe5f44e3ee49b21ec9da758  evals/tasks/quantum/maxcut_partition_ranker/tests.py
4d96a1e736f4b95157c39e7bba399786142ccd8f9889d49de4d5ef8e73af87a6  evals/tasks/quantum/measurement_bug_repair/tests.py
563553f63aa5bd957cc4e73e52cc787864567e1e479d3199300bda019962bf0b  evals/tasks/quantum/pauli_message_codec/tests.py
3cab7c4111f541c247ff98769efadb772b4f9ca7d9846ea13bce96d3d4137061  evals/tasks/quantum/pennylane_qml_iris_classification/task.json
8982efe7a2fdcde6fa723d77db797137a741508ebda8d2f4cc0610ebc25c4829  evals/tasks/quantum/pennylane_qml_iris_classification/tests.py
b8f8cd014abf677dd7f22e509043260db2e15ae2dc02f4bee0e6225bb44fd8b2  evals/tasks/quantum/pennylane_vqe_h2/candidate.py
18f1ff5d5dc2ee486e8a2f0faa6b2a00937cedbed8d967e7534b300eba93718e  evals/tasks/quantum/pennylane_vqe_h2/task.json
76a0106a456cea4652535dfe4ba9dadeac6825cae4ba3196e50e3a88ab4305b9  evals/tasks/quantum/pennylane_vqe_h2/tests.py
0ed7b78ecaaf776fbf8a0dc9e7709d58d17d4ea52c617b6ee3e164686fbd1121  evals/tasks/quantum/phase_estimation_circuit/candidate.py
9e4454a5be086d3484fe0f53fb63167e574baa04c9a632224bc25db34fd01fde  evals/tasks/quantum/phase_estimation_circuit/tests.py
06f85efba02647dc0c70e27450ece118df0ffc54d18d28df046ff319420547a9  evals/tasks/quantum/phase_measurement_register/tests.py
cef961ca651f7d14be1de207da598be883f1b3df1f1aadbec677c7f7ae724d8c  evals/tasks/quantum/phase_register_roundtrip/task.json
710ea354eb1d74d20d464f555428e2d78f77b1d0647cdfc6ab1543798335fe7c  evals/tasks/quantum/qaoa_maxcut/candidate.py
4bbfddd37158e6e2fc233b6feaeac391a929e0f34fcf6c4ce81f5ac9c1343e23  evals/tasks/quantum/qft_phase_pattern/candidate.py
ef7954bc50e7e39bd989a3d0feb0a6bea63b385aebc90c2d3d2215b9505b7b09  evals/tasks/quantum/qft_phase_pattern/tests.py
c7fdd0cdb37181a5d17ab9c2f9cbf2d7f41a877e45a58abed0bd89050cb280dd  evals/tasks/quantum/qiskit_qft_entangled/candidate.py
9847758ddba6fc2e70f1e6673787f0ab7ba3212dd218c4d003df54feec9dadac  evals/tasks/quantum/qiskit_qft_entangled/task.json
5fe817cf31b288e9ca3c1b481818a99a390498e15057f1da865fadcc1ecb169c  evals/tasks/quantum/qiskit_qft_entangled/tests.py
56828d0864714775e0c4d6bad5731e7fc1ba05d41bdb561c09030101a531612a  evals/tasks/quantum/quantum_bell_basis_discrimination/candidate.py
8ec6477bb5f1ad67655a1aad8120d4272f0e91eb11377958e17f83042ca1b764  evals/tasks/quantum/quantum_bell_basis_discrimination/task.json
0106c3e28e4406c38988bb6d99e253783e7b65194231471dd94623b6471caeaa  evals/tasks/quantum/quantum_bell_basis_discrimination/tests.py
a6dc2f09d5d1a26fa6a0a7c9bfee82f97277621c53e0cff451aa23148d2c53cc  evals/tasks/quantum/quantum_channel_depolarizing/candidate.py
e35912c10f0414dd665c50acf05ef5edd954aa2a7286177a8b50df8c8d5c207e  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/candidate.py
4b87bf5ec307d1fe6bbc2d06da8c31fe9102ca7dc36617075de3a309a9633784  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/task.json
16c446c9ff37b6000febfc411cfbb9b2afb966415473ac6d7aeeeb3d14019796  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/tests.py
704ae205c1689f1a422be5437f815d3f005cb3e6f9f18e14dce14108f0665bd2  evals/tasks/quantum/quantum_error_correction_shor_9qubit/candidate.py
53a4fca2a1d4bc50bbe1ae037365dfb4cb385867f86f17e43aac1826a49f942a  evals/tasks/quantum/quantum_qaoa_ring4_landscape/candidate.py
18c4c230851bea8b9a7c07e7e63a6c589a7aae0121c925c7464e9f5a169290a3  evals/tasks/quantum/quantum_qaoa_ring4_landscape/task.json
7b0edb9582b791f25e7f037ec2192e022a1aca156523c7a30b7e8b8323390ec0  evals/tasks/quantum/quantum_qaoa_ring4_landscape/tests.py
d120dacccc7a7e5275ae82e8fb51237633b30251f1b1630322d69a5c603ae8ab  evals/tasks/quantum/quantum_qft_periodic_state/candidate.py
ebd267d28641ee82b1ab3eb8cc1311a4404d9c2f4c396fc16e67f54d8f8b2590  evals/tasks/quantum/quantum_qft_periodic_state/task.json
1a5c67ea0d792acfb89b1f145a49f9e6a3b41ac1f5d01b2f2fcb794d67698b54  evals/tasks/quantum/quantum_qft_periodic_state/tests.py
da8a2df5ff111a370dce3dbc544fb0a94070e233d830e0209ae180196175c70a  evals/tasks/quantum/quantum_qml_variational_classifier/candidate.py
3797013aad4f4306494b05d6aaba2bcf58e9c0421399d98704c020004f8a15d7  evals/tasks/quantum/quantum_qml_variational_classifier/task.json
4ceb0643fe809c9d002605f18f949cbcc817ef46d73ee4d583fe6ab7ec99a814  evals/tasks/quantum/quantum_qml_variational_classifier/tests.py
cf077341049dda9bda626fea2988152c5578ed94019bf78f44b27a3004ce7494  evals/tasks/quantum/quantum_shor_phase_error_correction/candidate.py
924f62d00478418c0f8c050e9a5b1fa55d3dcc0c1ec33c2be275793849b99250  evals/tasks/quantum/quantum_shor_phase_error_correction/task.json
caa2f5ad530912bca05b7dc2fd653b545be269b4e2d04afb800316e27637a88d  evals/tasks/quantum/quantum_shor_phase_error_correction/tests.py
2fcbc2262b455b17fb03c676d706d815d17c00cfaeebb59f873860816a83beb4  evals/tasks/quantum/quantum_stabilizer_shor_generators/candidate.py
394cc88cf03ea9fa5455cbf6c5b70ee9322c303a64999ef730a0322765b12c5e  evals/tasks/quantum/quantum_stabilizer_shor_generators/task.json
4b624df712bace522ab885719fdf3c9d7f809a2ecf80332983302ce59c988714  evals/tasks/quantum/quantum_stabilizer_shor_generators/tests.py
94387663f339549e17e7140b689f21568c6aec325f998b43c7363a773d4f0e49  evals/tasks/quantum/quantum_three_qubit_entropy/candidate.py
b2b14d381a003e9b592ab7635309bb6dedf326cc4ee604f200862ee0e31a0216  evals/tasks/quantum/quantum_three_qubit_entropy/task.json
924589a11f316b781a2bcf859349605d26277616b50cd948d45858d67d53e160  evals/tasks/quantum/quantum_three_qubit_entropy/tests.py
4517812d3ba0b406e7d8c8bae538e6d8b98a2169315536e881e8d724567fb644  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/candidate.py
963bb4f6b79e121051a2d333653e000370aae6f3fc2cbf60b15039fc0204bb01  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/task.json
ea61dcafa29bff20cf30e0e9e5a3136f108849fdc60a66ff09ee00b3cadd0141  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/tests.py
20e155a60b412fa0567a163c6351b6ba1e65cd3aeb83aaca6c6d0faa3afe5f18  evals/tasks/quantum/quantum_vqe_heisenberg_energy/candidate.py
8509c851c68dff4c743dd3a7572579698ba9f382bb77f64bd7405dfdb49935fb  evals/tasks/quantum/quantum_vqe_heisenberg_energy/task.json
8a04b56c4c4ab367dc28bd579ad8a921fbca1ebc46270392fb9d89e5b32af16c  evals/tasks/quantum/quantum_vqe_heisenberg_energy/tests.py
7042529da93af3815df7941a9937a1476b1fd18d5571c0605acd617580b174f8  evals/tasks/quantum/stabilizer_tableau_update_repair/tests.py
e1bea2e227a012ae8b066f9cac0e3534a971b56a11270f3c40ca85d23d60a8cd  evals/tasks/quantum/superdense_coding/task.json
e3daa4ff10309b0044f6ed4fe5a707b6992fafcc180c30dd838af7bb906f9b7e  evals/tasks/quantum/superdense_identity_lookup/tests.py
fd6e10cad2e3c9c0d9176eefc5a165c2202b2c4ef97b3d513b64bfa922d3db59  evals/tasks/quantum/superdense_pauli_router/tests.py
dd4ff8fe03ad22e2d37a41683bd166ab787edc7f807dbef473babe54a0a96598  evals/tasks/quantum/teleportation_corrections/tests.py
c125239727ff913543e727979e7aa480341d99331b75f27324782c98793206c2  evals/tasks/quantum/vqe_energy_minimization/candidate.py
5f723b9e328abd5d08462d7dc0ccdb1c395eea31a89357c53e89ed07f16485a0  reports/sapo-holdout-enrichment-manifest-2026-08-24.json
ea5b263226494fa9a5831453e68c3f7a533ebfb2804e14094dc40d66fd890ff2  scripts/ai_launch_sapo_direct.sh
1a165df6e63597c2c89478bbfe431e269ba8a4d6bcb51eff5842cabbff67d9d4  scripts/asi2_launch_grpo_27b_selfeval.sh
63158871a80cfe275d168c0519149b88abdb707bae69b7b5a6e5036fff1159a9  scripts/asi2_watchdog_relaunch.sh
1d6e5b8078086bcd2bbcc6f463d314c23ad6d979d2b132bea519f742058853f4  scripts/asi3_launch_grpo_direct.sh
77bb097c26c6e3fbddb7911d92ed534f387eea7d1084b3da70efab32a9d3c94f  scripts/build_grpo_v8_manifest.py
c1b58907e9c3ff7175d52aceff347be335c7edbb35305cf4f343539c10288ac7  scripts/calibrate_model_judge.py
c07351d46a03ae1669f6d5430dee7b966b8dce80ae6e23390220d7b32d482903  scripts/decide_sapo_promotion_gate.py
ab65d0c448c21c71d293169c652c1e854d64dc31c76485ef274c4d495dd473da  scripts/eval_100_reeval.py
7913e6144a622b85eec53d00dac6e2ee9659dcc18bb697a20b99fb22889bb34c  scripts/fine_score.py
94274f251f762a8c5d7d9c4e3bcdfd1d482551729b6ee032f55105a3985bcc3e  scripts/fv_gspo_repair_sidecar.sh
e35703662de7eeff9e2119c905f2da8f75c2a49e73ffd51833eda16750add759  scripts/report_base_adapter_comprehensive.py
5c769d6c9626f1551a48e4db0478ec4cae299140d740dcaafe251ba67970f989  scripts/run_hf_pass1_eval.py
61c17c6529e12b9cc29ca2400618ea2112567c489508d2556e52607aec058a80  scripts/sapo_drift_watch.py
2eeea835761b1a3551ba7af517c2f19369ff20266310db4af1b4e9f2dfa1f95b  scripts/sapo_reward_audit.py
010e3d1dd1b22dbe4bc1b157abc838b82730afca5fbc5b1f1995b82ca184b925  scripts/sapo_status_snapshot.py
7890847631dc903c6e07574aac47cb71f2dbf3c952527420ef6e22c768313f83  scripts/submit_asi2_grpo_27b_selfeval_task.sh
b3cacae4017cae68b74c9db162e20521a847a41a8ba622770f7a33b79e5063c2  tests/test_asi3_sapo_launcher_readiness.py
938e97eb8f5af240b2653088e14da876497e001ae5d06aec3f1d93a5ab733178  tests/test_compat.py
6354b5c4428627270d8a4b2da06aec2497f9880a307beedb57e81d4f19c612cc  tests/test_execute_run.py
84b85e3d743de62e286b2b2f185cb9982151b1652bb80b59673c29869edb23f0  tests/test_fine_score.py
a1db3d0e545d9717e8cc80b0cf95adbe642adf83389d4d09e137a6a2a89268d7  tests/test_grpo_rollout_mix_entropy_floor.py
a97649ef1227988886fd29ad7fd5388430ac66248de53927a20e1de0aa72f5ca  tests/test_grpo_train_pass_truncation.py
97ec2387c5be9dccab1feccf3460371bbaadd559d4deda6280fb65949eeac939  tests/test_grpo_trainer_breakers.py
495b873f619754772bc55ad51d11a327271fe3e1ddce9d610211e473074da7d7  tests/test_grpo_trainer_eval_results.py
083ff7cbf7cdd89d8b95c1ecfc041d78ce35b7e4b44a48763ef04fef8effb168  tests/test_grpo_trainer_generation_stop.py
d0b8f6442d93c8fecfed3bed62531253c991f33734b26dff94cf158f7caba3e1  tests/test_grpo_trainer_loss_stats_router.py
83d4627a5ac171f406d00b87b2dacc74d67886bfb7d822e00589f4c93c201ffa  tests/test_grpo_trainer_main_failclosed.py
528ef0e1ef2799862eb3977a5c0d53f37ed653954886b5116098b10c9eac033e  tests/test_grpo_trainer_metrics.py
15bb6ca5d7394cb4273f7060c3b2cb36c3b38991fdc8cf0757a7b3aa9b07104b  tests/test_grpo_trainer_resume.py
b57d191b4ada2b97ad276ab609de74d1cbc129016563aea16f6134384a3350b3  tests/test_grpo_trainer_self_eval.py
59330ffb5a28ababb0934deb6b1f6e2ab7982c705152c4bc1ae8087cff1b79bf  tests/test_grpo_trainer_sigterm.py
0f079e6d24cd46f3b51c3d42b9d0882e0f86ecfbd9d81d4323f173a6455c96ee  tests/test_grpo_utils.py
0f9d1b0f62e9c9a825061fd54c6ae1f71fd902733fb592a0beac82a0cd6df803  tests/test_holdout_enrichment_invariance.py
9a8c71d22816dab414376030a60c77a7f232af2217e86d255df788c023b58b75  tests/test_holdout_scorer_version_awareness.py
1bd8105aa4b1ab4d3eecf0dd151969a86cac4ac4ccaf0d205b7c7adfe4e37ff7  tests/test_model_family_support.py
1b587b54f3acdedd50b733558ac7dbf80ba96b2d75384aa1119808750e8165d7  tests/test_model_judge.py
6363e022f9c0d6a16200f385e9a5a845df5b0c93e66abcb9389c648fa4235a9c  tests/test_pennylane_vqe_h2_scorer_versions.py
caea3662eb1cb632fd4c7b881e0081b157cb7708325739e52a4f45dbbc5accdb  tests/test_prepare_prompts_coverage.py
f43b364994eb1dfcdceb7314127da94a7154d292907f9c781119b54dd5fa3824  tests/test_promotion_eval_adapter_merge.py
60437d05c8fefac612d5e48f7105fc31907ec45925acfec28d7f22f55262ce8f  tests/test_report_base_adapter_comprehensive.py
2bcdae7e8bc4407dd55d0be549b910c2305d80a4a9f7f3a8b59f7f58afa49c6d  tests/test_run_eval_scoring.py
7f37d88898c639d677eaeebd7c2a914f9710a6a71a9547cfa8956b16698a2b08  tests/test_sapo_curriculum_holdout_adjacent.py
f68e2261ab1cef28df4cef65aaaaa815c6306d129bb2f0d17cae31e7c3da15db  tests/test_sapo_drift_watch.py
2c5d5a901992ca5f7e0cec39e268d71b2d0f157e4add6851a551aeeaee8fb9f9  tests/test_sapo_eval_security.py
d79ae1884791178a1fd2902224055c3ba4939b531e4d28ba74ed18bd191e71f4  tests/test_sapo_loss.py
b7b4ad1b64e22d99c268d948583c00b419f6f0354d91e270d2146dab9ad94dbc  tests/test_sapo_promotion_pipeline_hardening.py
78dd512c92ada912fa7487792d81bdf7899bd07c6b0c5d77fc0fe4bae2e53127  tests/test_sapo_prompt_audit_cli.py
cceee5cb5733a2dd06f251b6c8544fe06972be02d1032da7d14301fac0a7dbf4  tests/test_sapo_reward_audit_cli.py
974ee9324b55b608509e337a6e7eac01d13651c5a8c66bf40f87e5d32155a4a2  tests/test_sapo_reward_audit.py
ff59d248dfba4ea7fbbfbf40061b482c614613e2573c7f9b184e69bb975a5f9b  tests/test_sapo_status_snapshot.py
81863a1a6fef400243d3f7fabc7da6742b765e2a15b9280d498e0733fad6d832  tests/test_seed_run_with_references.py
1daa2c7e60bc461c57bb02117cd627846441d08e20835dd8c710cfd4b4e5cb85  tests/test_single_candidate_eval.py
9f65ba9acabdfa09ac425a22c778c5480f8dee8b61494412504b7948a9d59be5  training/compat.py
d77bc662fa2823b1998f32cfa0a0c8deb684431c37cf4d749b64377d83fef247  training/grpo_trainer.py
73de15500003ed8e7f9ea05d02146ac9b7f01c1444f3828c93a2625ba435ae1e  training/grpo_utils.py

## r10 DEPLOY — register-fully-ticked build (2026-08-26 ~11:0x-11:1x CST)
- Register re-verified at build (all markers checked, evidence-first):
  tests_RED REMOVED (10/10 green verified twice, reviewer re-review GO ~11:00),
  review_BLOCK removed (reviewer.md wave-F GO), launchsim_BLOCK absent,
  debuglane APPROVE (SWEEP 2 r10-wave; F-A implemented — asi2_launch:468-470
  wires --greedy-rollout-fraction/--entropy-floor-weight), depmatrix ticked
  (matrix pinned local py3.9.6/box py3.11.14), py3.9 critical-scope scan clean
  (only holdout-contract evals/tasks baselines + docstrings remain — recorded
  non-blocking per depmatrix §2.4), locks: none active on members.
- Build: fresh build-time hashes → tar (365600 B) → member-hash==manifest==tree
  verified (no stale members). 136 members (full list + hashes below).
- Deploy: 82x6000B chunks, 0 failures, chunk audit clean (81x6000+1468);
  box relaunch_r10.tgz sha 4f2e9315… == local, 365600 B both sides.
- Run tree refreshed: 5 critical files + compat.py + sapo_drift_watch match
  manifest; grpo_trainer.py ast-parses on box. run-6 (sapo-27b-ai-20260825T214849)
  noted DEAD by rollout-watch (r10 rescue NOT in r9) — r10 relaunch is the
  manager's call per STATUS.md; deploy integrity state is ready for it.
- Launchsim r10 smoke: SIGNALED via /tmp/sapo_launchsim_r10_TRIGGER (11:12 CST,
  bundle path+sha+members+scope recorded). Verdict expected in launchsim lane.
- NEXT CYCLE: standard freshness + lock + register scan; r11 when tree drifts.

### r10 manifest (136 members, sha256)
85106d8e4c0c337edbc95eec2972d363c96f50f2d91c0d4404438dff386c4f27  configs/rl/qwen36_27b_fv_gspo_asi2.json
7b8bdc04fe2a6b41ba867facdebe04170bf7c864a2e09c2b446718764f060f18  evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt
a181cd994245f51a605cb20f69ae17da2f2cf3a06c648d2bcf066beec5d0dbe4  evals/runner/seed_run_with_references.py
0108c020f916b8dbf8ab16d08560d0057265ecaee0f5f37289620a7e0e8f0e54  evals/tasks/quantum/bell_pair_construction/candidate.py
9f6bf09c6019fb84748c9df10638291fd62bfcc90fa049642b980a1541b52403  evals/tasks/quantum/bell_pair_construction/tests.py
976677faa3f3138f9ac53c1435cbb8002ef380dabff6dc74f2f4fc4821620da1  evals/tasks/quantum/binary_measurement_decoder/task.json
114bd9cf91467960db9b629475aad730929625271b7ea76e453199b3b40b6690  evals/tasks/quantum/binary_measurement_decoder/tests.py
48d45ea9b46d7e54f23edbb62e94e7fb132884250506e342c460c7c9bba2d7db  evals/tasks/quantum/bitstring_maxcut_landscape/tests.py
4b4c0ea792f29454d0430a473cdaa778bc1432801c7f2c8c0d935520c89a29e5  evals/tasks/quantum/circuit_phase_repair/tests.py
6ee4de0769c7dd49dfa317d83035cc870c83020b9094cac23d5724f6f30fbdc6  evals/tasks/quantum/density_matrix_partial_trace/candidate.py
311688fed1cf708c6cbbe7854c724c422758526c1e6d13f12d1f1d1eb409e804  evals/tasks/quantum/error_detection_bit_flip/tests.py
18ed2cb56ee7c96529c53d65921deb4c44dcfdedce5d2bb275e36b714d59e6ae  evals/tasks/quantum/gate_alias_casefold_barrier/candidate.py
5feaa43a0f846f7d605e3b9ee6946ba4e4d53e61da07ed4ea7d40117218db661  evals/tasks/quantum/gate_alias_casefold_barrier/tests.py
f1cf1e1144aeef96acac9f527b6b3d96ea9c0c938121a48d9f2fc735599d9525  evals/tasks/quantum/gate_alias_normalization/task.json
4e17b821390f6916b8fd29d64061489a7bde5367a648b8227b26276a79b97143  evals/tasks/quantum/gate_alias_normalization/tests.py
fb4c96d30a8260ad6aa9895e3c2673d3dd7cc264d9f0958bfa0d9a163eb7760b  evals/tasks/quantum/gate_alias_registry_cleanup/candidate.py
d02d9e3673930d64c3dd1483d8ebf00c6b23764fa18fe542f16930313722100f  evals/tasks/quantum/gate_alias_registry_cleanup/tests.py
8cba17a29939f736e18e729a86fbbef83be4db9811890f2467dac666f805d931  evals/tasks/quantum/gate_token_canonicalizer/tests.py
7a6d4835c6cf027a323a720cd9698cf80560470c9c3aba7652965da3aeaac224  evals/tasks/quantum/ghz_state_witness/candidate.py
48db0b26936ba658f1f6e9bc61e416c07888d4cb5c17a1fbcd1bea8b4e30d464  evals/tasks/quantum/ghz_state_witness/tests.py
8b0496f1b2f2d671774a3ff5ae38bbd3a12764f64a187274b022eb1f0592a0e6  evals/tasks/quantum/grover_oracle_diffusion/candidate.py
eca1461b210a9e9244be9876e7c4cc2ae0648beb6eb167c59247987a2fcc922c  evals/tasks/quantum/grover_oracle_diffusion/tests.py
0b0ac2c05ac0ddbe685a4244e4e39fd315669e1cce18b3546496f3a65414a600  evals/tasks/quantum/maxcut_assignment_enumerator/tests.py
c2ca2881a761af3709496a1598360c4b545cc489822445e30cbd2e7afaf878e7  evals/tasks/quantum/maxcut_partition_ranker/candidate.py
23377a27912b10f10417748b130a25cefa7d84c08fe5f44e3ee49b21ec9da758  evals/tasks/quantum/maxcut_partition_ranker/tests.py
4d96a1e736f4b95157c39e7bba399786142ccd8f9889d49de4d5ef8e73af87a6  evals/tasks/quantum/measurement_bug_repair/tests.py
563553f63aa5bd957cc4e73e52cc787864567e1e479d3199300bda019962bf0b  evals/tasks/quantum/pauli_message_codec/tests.py
3cab7c4111f541c247ff98769efadb772b4f9ca7d9846ea13bce96d3d4137061  evals/tasks/quantum/pennylane_qml_iris_classification/task.json
8982efe7a2fdcde6fa723d77db797137a741508ebda8d2f4cc0610ebc25c4829  evals/tasks/quantum/pennylane_qml_iris_classification/tests.py
b8f8cd014abf677dd7f22e509043260db2e15ae2dc02f4bee0e6225bb44fd8b2  evals/tasks/quantum/pennylane_vqe_h2/candidate.py
18f1ff5d5dc2ee486e8a2f0faa6b2a00937cedbed8d967e7534b300eba93718e  evals/tasks/quantum/pennylane_vqe_h2/task.json
76a0106a456cea4652535dfe4ba9dadeac6825cae4ba3196e50e3a88ab4305b9  evals/tasks/quantum/pennylane_vqe_h2/tests.py
0ed7b78ecaaf776fbf8a0dc9e7709d58d17d4ea52c617b6ee3e164686fbd1121  evals/tasks/quantum/phase_estimation_circuit/candidate.py
9e4454a5be086d3484fe0f53fb63167e574baa04c9a632224bc25db34fd01fde  evals/tasks/quantum/phase_estimation_circuit/tests.py
06f85efba02647dc0c70e27450ece118df0ffc54d18d28df046ff319420547a9  evals/tasks/quantum/phase_measurement_register/tests.py
cef961ca651f7d14be1de207da598be883f1b3df1f1aadbec677c7f7ae724d8c  evals/tasks/quantum/phase_register_roundtrip/task.json
710ea354eb1d74d20d464f555428e2d78f77b1d0647cdfc6ab1543798335fe7c  evals/tasks/quantum/qaoa_maxcut/candidate.py
4bbfddd37158e6e2fc233b6feaeac391a929e0f34fcf6c4ce81f5ac9c1343e23  evals/tasks/quantum/qft_phase_pattern/candidate.py
ef7954bc50e7e39bd989a3d0feb0a6bea63b385aebc90c2d3d2215b9505b7b09  evals/tasks/quantum/qft_phase_pattern/tests.py
c7fdd0cdb37181a5d17ab9c2f9cbf2d7f41a877e45a58abed0bd89050cb280dd  evals/tasks/quantum/qiskit_qft_entangled/candidate.py
9847758ddba6fc2e70f1e6673787f0ab7ba3212dd218c4d003df54feec9dadac  evals/tasks/quantum/qiskit_qft_entangled/task.json
5fe817cf31b288e9ca3c1b481818a99a390498e15057f1da865fadcc1ecb169c  evals/tasks/quantum/qiskit_qft_entangled/tests.py
56828d0864714775e0c4d6bad5731e7fc1ba05d41bdb561c09030101a531612a  evals/tasks/quantum/quantum_bell_basis_discrimination/candidate.py
8ec6477bb5f1ad67655a1aad8120d4272f0e91eb11377958e17f83042ca1b764  evals/tasks/quantum/quantum_bell_basis_discrimination/task.json
0106c3e28e4406c38988bb6d99e253783e7b65194231471dd94623b6471caeaa  evals/tasks/quantum/quantum_bell_basis_discrimination/tests.py
a6dc2f09d5d1a26fa6a0a7c9bfee82f97277621c53e0cff451aa23148d2c53cc  evals/tasks/quantum/quantum_channel_depolarizing/candidate.py
e35912c10f0414dd665c50acf05ef5edd954aa2a7286177a8b50df8c8d5c207e  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/candidate.py
4b87bf5ec307d1fe6bbc2d06da8c31fe9102ca7dc36617075de3a309a9633784  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/task.json
16c446c9ff37b6000febfc411cfbb9b2afb966415473ac6d7aeeeb3d14019796  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/tests.py
704ae205c1689f1a422be5437f815d3f005cb3e6f9f18e14dce14108f0665bd2  evals/tasks/quantum/quantum_error_correction_shor_9qubit/candidate.py
53a4fca2a1d4bc50bbe1ae037365dfb4cb385867f86f17e43aac1826a49f942a  evals/tasks/quantum/quantum_qaoa_ring4_landscape/candidate.py
18c4c230851bea8b9a7c07e7e63a6c589a7aae0121c925c7464e9f5a169290a3  evals/tasks/quantum/quantum_qaoa_ring4_landscape/task.json
7b0edb9582b791f25e7f037ec2192e022a1aca156523c7a30b7e8b8323390ec0  evals/tasks/quantum/quantum_qaoa_ring4_landscape/tests.py
d120dacccc7a7e5275ae82e8fb51237633b30251f1b1630322d69a5c603ae8ab  evals/tasks/quantum/quantum_qft_periodic_state/candidate.py
ebd267d28641ee82b1ab3eb8cc1311a4404d9c2f4c396fc16e67f54d8f8b2590  evals/tasks/quantum/quantum_qft_periodic_state/task.json
1a5c67ea0d792acfb89b1f145a49f9e6a3b41ac1f5d01b2f2fcb794d67698b54  evals/tasks/quantum/quantum_qft_periodic_state/tests.py
da8a2df5ff111a370dce3dbc544fb0a94070e233d830e0209ae180196175c70a  evals/tasks/quantum/quantum_qml_variational_classifier/candidate.py
3797013aad4f4306494b05d6aaba2bcf58e9c0421399d98704c020004f8a15d7  evals/tasks/quantum/quantum_qml_variational_classifier/task.json
4ceb0643fe809c9d002605f18f949cbcc817ef46d73ee4d583fe6ab7ec99a814  evals/tasks/quantum/quantum_qml_variational_classifier/tests.py
cf077341049dda9bda626fea2988152c5578ed94019bf78f44b27a3004ce7494  evals/tasks/quantum/quantum_shor_phase_error_correction/candidate.py
924f62d00478418c0f8c050e9a5b1fa55d3dcc0c1ec33c2be275793849b99250  evals/tasks/quantum/quantum_shor_phase_error_correction/task.json
caa2f5ad530912bca05b7dc2fd653b545be269b4e2d04afb800316e27637a88d  evals/tasks/quantum/quantum_shor_phase_error_correction/tests.py
2fcbc2262b455b17fb03c676d706d815d17c00cfaeebb59f873860816a83beb4  evals/tasks/quantum/quantum_stabilizer_shor_generators/candidate.py
394cc88cf03ea9fa5455cbf6c5b70ee9322c303a64999ef730a0322765b12c5e  evals/tasks/quantum/quantum_stabilizer_shor_generators/task.json
4b624df712bace522ab885719fdf3c9d7f809a2ecf80332983302ce59c988714  evals/tasks/quantum/quantum_stabilizer_shor_generators/tests.py
94387663f339549e17e7140b689f21568c6aec325f998b43c7363a773d4f0e49  evals/tasks/quantum/quantum_three_qubit_entropy/candidate.py
b2b14d381a003e9b592ab7635309bb6dedf326cc4ee604f200862ee0e31a0216  evals/tasks/quantum/quantum_three_qubit_entropy/task.json
924589a11f316b781a2bcf859349605d26277616b50cd948d45858d67d53e160  evals/tasks/quantum/quantum_three_qubit_entropy/tests.py
4517812d3ba0b406e7d8c8bae538e6d8b98a2169315536e881e8d724567fb644  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/candidate.py
963bb4f6b79e121051a2d333653e000370aae6f3fc2cbf60b15039fc0204bb01  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/task.json
ea61dcafa29bff20cf30e0e9e5a3136f108849fdc60a66ff09ee00b3cadd0141  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/tests.py
20e155a60b412fa0567a163c6351b6ba1e65cd3aeb83aaca6c6d0faa3afe5f18  evals/tasks/quantum/quantum_vqe_heisenberg_energy/candidate.py
8509c851c68dff4c743dd3a7572579698ba9f382bb77f64bd7405dfdb49935fb  evals/tasks/quantum/quantum_vqe_heisenberg_energy/task.json
8a04b56c4c4ab367dc28bd579ad8a921fbca1ebc46270392fb9d89e5b32af16c  evals/tasks/quantum/quantum_vqe_heisenberg_energy/tests.py
7042529da93af3815df7941a9937a1476b1fd18d5571c0605acd617580b174f8  evals/tasks/quantum/stabilizer_tableau_update_repair/tests.py
e1bea2e227a012ae8b066f9cac0e3534a971b56a11270f3c40ca85d23d60a8cd  evals/tasks/quantum/superdense_coding/task.json
e3daa4ff10309b0044f6ed4fe5a707b6992fafcc180c30dd838af7bb906f9b7e  evals/tasks/quantum/superdense_identity_lookup/tests.py
fd6e10cad2e3c9c0d9176eefc5a165c2202b2c4ef97b3d513b64bfa922d3db59  evals/tasks/quantum/superdense_pauli_router/tests.py
dd4ff8fe03ad22e2d37a41683bd166ab787edc7f807dbef473babe54a0a96598  evals/tasks/quantum/teleportation_corrections/tests.py
c125239727ff913543e727979e7aa480341d99331b75f27324782c98793206c2  evals/tasks/quantum/vqe_energy_minimization/candidate.py
5f723b9e328abd5d08462d7dc0ccdb1c395eea31a89357c53e89ed07f16485a0  reports/sapo-holdout-enrichment-manifest-2026-08-24.json
ea5b263226494fa9a5831453e68c3f7a533ebfb2804e14094dc40d66fd890ff2  scripts/ai_launch_sapo_direct.sh
fbabaa113e96d1529742debaabde4b93184a95d3d9864c1cb41dd61f8b09efd9  scripts/asi2_launch_grpo_27b_selfeval.sh
63158871a80cfe275d168c0519149b88abdb707bae69b7b5a6e5036fff1159a9  scripts/asi2_watchdog_relaunch.sh
85f1f99f4f28b888585df9ffe193925f9b003b3067520e0d4c063f1ba36e14ce  scripts/asi3_launch_grpo_direct.sh
77bb097c26c6e3fbddb7911d92ed534f387eea7d1084b3da70efab32a9d3c94f  scripts/build_grpo_v8_manifest.py
5ab1acc36c0f1be0668634962a7583d22023119d68030d4dc6e23353fdb2bf0a  scripts/calibrate_model_judge.py
c07351d46a03ae1669f6d5430dee7b966b8dce80ae6e23390220d7b32d482903  scripts/decide_sapo_promotion_gate.py
d49aaeea2d1c25ff09df418ba594037e14a573554ed8d57d6a7f6afa7c944de6  scripts/eval_100_reeval.py
766949e44a541db7ab9ddcdef50a5f9c60fcd53b66c992f80ed39e26197426c9  scripts/fine_score.py
94274f251f762a8c5d7d9c4e3bcdfd1d482551729b6ee032f55105a3985bcc3e  scripts/fv_gspo_repair_sidecar.sh
e35703662de7eeff9e2119c905f2da8f75c2a49e73ffd51833eda16750add759  scripts/report_base_adapter_comprehensive.py
5c769d6c9626f1551a48e4db0478ec4cae299140d740dcaafe251ba67970f989  scripts/run_hf_pass1_eval.py
61c17c6529e12b9cc29ca2400618ea2112567c489508d2556e52607aec058a80  scripts/sapo_drift_watch.py
2eeea835761b1a3551ba7af517c2f19369ff20266310db4af1b4e9f2dfa1f95b  scripts/sapo_reward_audit.py
010e3d1dd1b22dbe4bc1b157abc838b82730afca5fbc5b1f1995b82ca184b925  scripts/sapo_status_snapshot.py
7890847631dc903c6e07574aac47cb71f2dbf3c952527420ef6e22c768313f83  scripts/submit_asi2_grpo_27b_selfeval_task.sh
6edb98a84668f53471c786c1770bf9c392168f77de505ca3dcf96a075bb39498  tests/test_asi3_sapo_launcher_readiness.py
938e97eb8f5af240b2653088e14da876497e001ae5d06aec3f1d93a5ab733178  tests/test_compat.py
6354b5c4428627270d8a4b2da06aec2497f9880a307beedb57e81d4f19c612cc  tests/test_execute_run.py
84b85e3d743de62e286b2b2f185cb9982151b1652bb80b59673c29869edb23f0  tests/test_fine_score.py
98598a2a94576bfc42b0eb438cea588bce207202582167bdd8da800432a4975b  tests/test_grpo_rollout_mix_entropy_floor.py
a97649ef1227988886fd29ad7fd5388430ac66248de53927a20e1de0aa72f5ca  tests/test_grpo_train_pass_truncation.py
97ec2387c5be9dccab1feccf3460371bbaadd559d4deda6280fb65949eeac939  tests/test_grpo_trainer_breakers.py
495b873f619754772bc55ad51d11a327271fe3e1ddce9d610211e473074da7d7  tests/test_grpo_trainer_eval_results.py
083ff7cbf7cdd89d8b95c1ecfc041d78ce35b7e4b44a48763ef04fef8effb168  tests/test_grpo_trainer_generation_stop.py
d0b8f6442d93c8fecfed3bed62531253c991f33734b26dff94cf158f7caba3e1  tests/test_grpo_trainer_loss_stats_router.py
19b6cd0b8a628ec636ddca043b3de33de979883f19dfcbc9b6a6a6ea361e0902  tests/test_grpo_trainer_main_failclosed.py
528ef0e1ef2799862eb3977a5c0d53f37ed653954886b5116098b10c9eac033e  tests/test_grpo_trainer_metrics.py
15bb6ca5d7394cb4273f7060c3b2cb36c3b38991fdc8cf0757a7b3aa9b07104b  tests/test_grpo_trainer_resume.py
b57d191b4ada2b97ad276ab609de74d1cbc129016563aea16f6134384a3350b3  tests/test_grpo_trainer_self_eval.py
59330ffb5a28ababb0934deb6b1f6e2ab7982c705152c4bc1ae8087cff1b79bf  tests/test_grpo_trainer_sigterm.py
eb6b45cbdded0f936bdae02aa9e2fe3de22c6e4494071cb398436d49f2ca64a1  tests/test_grpo_utils.py
0f9d1b0f62e9c9a825061fd54c6ae1f71fd902733fb592a0beac82a0cd6df803  tests/test_holdout_enrichment_invariance.py
9a8c71d22816dab414376030a60c77a7f232af2217e86d255df788c023b58b75  tests/test_holdout_scorer_version_awareness.py
1bd8105aa4b1ab4d3eecf0dd151969a86cac4ac4ccaf0d205b7c7adfe4e37ff7  tests/test_model_family_support.py
1b587b54f3acdedd50b733558ac7dbf80ba96b2d75384aa1119808750e8165d7  tests/test_model_judge.py
6363e022f9c0d6a16200f385e9a5a845df5b0c93e66abcb9389c648fa4235a9c  tests/test_pennylane_vqe_h2_scorer_versions.py
caea3662eb1cb632fd4c7b881e0081b157cb7708325739e52a4f45dbbc5accdb  tests/test_prepare_prompts_coverage.py
f43b364994eb1dfcdceb7314127da94a7154d292907f9c781119b54dd5fa3824  tests/test_promotion_eval_adapter_merge.py
60437d05c8fefac612d5e48f7105fc31907ec45925acfec28d7f22f55262ce8f  tests/test_report_base_adapter_comprehensive.py
2bcdae7e8bc4407dd55d0be549b910c2305d80a4a9f7f3a8b59f7f58afa49c6d  tests/test_run_eval_scoring.py
7f37d88898c639d677eaeebd7c2a914f9710a6a71a9547cfa8956b16698a2b08  tests/test_sapo_curriculum_holdout_adjacent.py
f68e2261ab1cef28df4cef65aaaaa815c6306d129bb2f0d17cae31e7c3da15db  tests/test_sapo_drift_watch.py
2c5d5a901992ca5f7e0cec39e268d71b2d0f157e4add6851a551aeeaee8fb9f9  tests/test_sapo_eval_security.py
d79ae1884791178a1fd2902224055c3ba4939b531e4d28ba74ed18bd191e71f4  tests/test_sapo_loss.py
b7b4ad1b64e22d99c268d948583c00b419f6f0354d91e270d2146dab9ad94dbc  tests/test_sapo_promotion_pipeline_hardening.py
78dd512c92ada912fa7487792d81bdf7899bd07c6b0c5d77fc0fe4bae2e53127  tests/test_sapo_prompt_audit_cli.py
cceee5cb5733a2dd06f251b6c8544fe06972be02d1032da7d14301fac0a7dbf4  tests/test_sapo_reward_audit_cli.py
974ee9324b55b608509e337a6e7eac01d13651c5a8c66bf40f87e5d32155a4a2  tests/test_sapo_reward_audit.py
ff59d248dfba4ea7fbbfbf40061b482c614613e2573c7f9b184e69bb975a5f9b  tests/test_sapo_status_snapshot.py
81863a1a6fef400243d3f7fabc7da6742b765e2a15b9280d498e0733fad6d832  tests/test_seed_run_with_references.py
1daa2c7e60bc461c57bb02117cd627846441d08e20835dd8c710cfd4b4e5cb85  tests/test_single_candidate_eval.py
9f65ba9acabdfa09ac425a22c778c5480f8dee8b61494412504b7948a9d59be5  training/compat.py
4ab6f70e8d03b276c7a4de26ca7b38f8e976977bd53eca110f6d3d650e0c2594  training/grpo_trainer.py
73de15500003ed8e7f9ea05d02146ac9b7f01c1444f3828c93a2625ba435ae1e  training/grpo_utils.py

## r11 DEPLOY — closure-complete rebuild (2026-08-26 ~11:4x-11:5x CST)
- Launchsim CRITICAL on r10: training/generation.py missing (grpo_trainer.py:48
  import) — trainer dies at import on box; member-hash check was vacuous.
- FIX: permanent member-completeness gate (see procedure above); closure
  iteration: r10 136 → +26 → +2 (candidate_security, task_metadata) →
  CLOSURE OK at 164 members. New modules include grpo_trainer's other 7
  module-level imports (generation, model_backend, model_family_preflight,
  quantum_verifiers, qwen_sft_peft, research_plugins, teacher_free_repair,
  text_preprocessor_backend), run_hf_pass1_eval's imports (evals/runner/*,
  scripts/eval_base_vs_adapter, training/*), and test-imported modules.
- py3.9 scan on new members: 0 real hits. Locks: none. Markers clear.
- Build: fresh hashes → tar (460999 B) → member==manifest==tree verified.
- Deploy: 103x6000B chunks, 0 failures, audit clean (102x6000+2668); box sha
  e694bc55… == local, 460999 B both sides.
- Run tree refreshed; ON-BOX import checks: training.{generation, compat,
  grpo_utils, quantum_verifiers, model_backend, text_preprocessor_backend,
  runtime_overlay, teacher_free_repair} all OK; **GRPO_TRAINER IMPORT OK on
  box** — r10 launch-death class eliminated.
- Launchsim re-signaled: /tmp/sapo_launchsim_r11_TRIGGER (supersedes r10
  trigger). Rehearsal re-runs on r11; restart gates on ITS pass.
- NEXT CYCLE: standard freshness + lock + register + CLOSURE gate scans.

### r11 manifest (164 members, sha256)
85106d8e4c0c337edbc95eec2972d363c96f50f2d91c0d4404438dff386c4f27  configs/rl/qwen36_27b_fv_gspo_asi2.json
7b8bdc04fe2a6b41ba867facdebe04170bf7c864a2e09c2b446718764f060f18  evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt
18d8b065dd70c63dd55c3b4e6f229b2c741f77b39f8bd9ae409686aaa6b3ac65  evals/runner/candidate_sanitize.py
498c04c31b09dbd237d32f35839a2340b64e3da4420ab10467cd5a0962fb3336  evals/runner/candidate_security.py
4f149f9819df3c49ec57be9358a72463263343e17ddb3b648b7e13ac912ffa33  evals/runner/execute_run.py
8cdf777b630422df6bc3cd993353022b9719bc8df40657d058d6ab16b807c89b  evals/runner/frozen_contract.py
8216b8421947fe656731e0c26ff661bd341a3a7da977888babb27aa7d9d8831c  evals/runner/prepare_prompts.py
e26b9ade036c75993e4126acbe5f6e9b834c8e1173959226a3a78c9f25ab29af  evals/runner/public_task_spec.py
97b5186207302723f47281a4ed1e19e3406518537031dd243cdd162d24063093  evals/runner/run_eval.py
a181cd994245f51a605cb20f69ae17da2f2cf3a06c648d2bcf066beec5d0dbe4  evals/runner/seed_run_with_references.py
c4fa8bfa41c6edeecbb7816d3da3d7e6672772bafd4e2e4073047931ad350947  evals/runner/single_candidate_eval.py
618088bda4208f9ca8d84361ee4068b51cc36da67d82313e8a353846405d3076  evals/runner/task_metadata.py
0108c020f916b8dbf8ab16d08560d0057265ecaee0f5f37289620a7e0e8f0e54  evals/tasks/quantum/bell_pair_construction/candidate.py
9f6bf09c6019fb84748c9df10638291fd62bfcc90fa049642b980a1541b52403  evals/tasks/quantum/bell_pair_construction/tests.py
976677faa3f3138f9ac53c1435cbb8002ef380dabff6dc74f2f4fc4821620da1  evals/tasks/quantum/binary_measurement_decoder/task.json
114bd9cf91467960db9b629475aad730929625271b7ea76e453199b3b40b6690  evals/tasks/quantum/binary_measurement_decoder/tests.py
48d45ea9b46d7e54f23edbb62e94e7fb132884250506e342c460c7c9bba2d7db  evals/tasks/quantum/bitstring_maxcut_landscape/tests.py
4b4c0ea792f29454d0430a473cdaa778bc1432801c7f2c8c0d935520c89a29e5  evals/tasks/quantum/circuit_phase_repair/tests.py
6ee4de0769c7dd49dfa317d83035cc870c83020b9094cac23d5724f6f30fbdc6  evals/tasks/quantum/density_matrix_partial_trace/candidate.py
311688fed1cf708c6cbbe7854c724c422758526c1e6d13f12d1f1d1eb409e804  evals/tasks/quantum/error_detection_bit_flip/tests.py
18ed2cb56ee7c96529c53d65921deb4c44dcfdedce5d2bb275e36b714d59e6ae  evals/tasks/quantum/gate_alias_casefold_barrier/candidate.py
5feaa43a0f846f7d605e3b9ee6946ba4e4d53e61da07ed4ea7d40117218db661  evals/tasks/quantum/gate_alias_casefold_barrier/tests.py
f1cf1e1144aeef96acac9f527b6b3d96ea9c0c938121a48d9f2fc735599d9525  evals/tasks/quantum/gate_alias_normalization/task.json
4e17b821390f6916b8fd29d64061489a7bde5367a648b8227b26276a79b97143  evals/tasks/quantum/gate_alias_normalization/tests.py
fb4c96d30a8260ad6aa9895e3c2673d3dd7cc264d9f0958bfa0d9a163eb7760b  evals/tasks/quantum/gate_alias_registry_cleanup/candidate.py
d02d9e3673930d64c3dd1483d8ebf00c6b23764fa18fe542f16930313722100f  evals/tasks/quantum/gate_alias_registry_cleanup/tests.py
8cba17a29939f736e18e729a86fbbef83be4db9811890f2467dac666f805d931  evals/tasks/quantum/gate_token_canonicalizer/tests.py
7a6d4835c6cf027a323a720cd9698cf80560470c9c3aba7652965da3aeaac224  evals/tasks/quantum/ghz_state_witness/candidate.py
48db0b26936ba658f1f6e9bc61e416c07888d4cb5c17a1fbcd1bea8b4e30d464  evals/tasks/quantum/ghz_state_witness/tests.py
8b0496f1b2f2d671774a3ff5ae38bbd3a12764f64a187274b022eb1f0592a0e6  evals/tasks/quantum/grover_oracle_diffusion/candidate.py
eca1461b210a9e9244be9876e7c4cc2ae0648beb6eb167c59247987a2fcc922c  evals/tasks/quantum/grover_oracle_diffusion/tests.py
0b0ac2c05ac0ddbe685a4244e4e39fd315669e1cce18b3546496f3a65414a600  evals/tasks/quantum/maxcut_assignment_enumerator/tests.py
c2ca2881a761af3709496a1598360c4b545cc489822445e30cbd2e7afaf878e7  evals/tasks/quantum/maxcut_partition_ranker/candidate.py
23377a27912b10f10417748b130a25cefa7d84c08fe5f44e3ee49b21ec9da758  evals/tasks/quantum/maxcut_partition_ranker/tests.py
4d96a1e736f4b95157c39e7bba399786142ccd8f9889d49de4d5ef8e73af87a6  evals/tasks/quantum/measurement_bug_repair/tests.py
563553f63aa5bd957cc4e73e52cc787864567e1e479d3199300bda019962bf0b  evals/tasks/quantum/pauli_message_codec/tests.py
3cab7c4111f541c247ff98769efadb772b4f9ca7d9846ea13bce96d3d4137061  evals/tasks/quantum/pennylane_qml_iris_classification/task.json
8982efe7a2fdcde6fa723d77db797137a741508ebda8d2f4cc0610ebc25c4829  evals/tasks/quantum/pennylane_qml_iris_classification/tests.py
b8f8cd014abf677dd7f22e509043260db2e15ae2dc02f4bee0e6225bb44fd8b2  evals/tasks/quantum/pennylane_vqe_h2/candidate.py
18f1ff5d5dc2ee486e8a2f0faa6b2a00937cedbed8d967e7534b300eba93718e  evals/tasks/quantum/pennylane_vqe_h2/task.json
76a0106a456cea4652535dfe4ba9dadeac6825cae4ba3196e50e3a88ab4305b9  evals/tasks/quantum/pennylane_vqe_h2/tests.py
0ed7b78ecaaf776fbf8a0dc9e7709d58d17d4ea52c617b6ee3e164686fbd1121  evals/tasks/quantum/phase_estimation_circuit/candidate.py
9e4454a5be086d3484fe0f53fb63167e574baa04c9a632224bc25db34fd01fde  evals/tasks/quantum/phase_estimation_circuit/tests.py
06f85efba02647dc0c70e27450ece118df0ffc54d18d28df046ff319420547a9  evals/tasks/quantum/phase_measurement_register/tests.py
cef961ca651f7d14be1de207da598be883f1b3df1f1aadbec677c7f7ae724d8c  evals/tasks/quantum/phase_register_roundtrip/task.json
710ea354eb1d74d20d464f555428e2d78f77b1d0647cdfc6ab1543798335fe7c  evals/tasks/quantum/qaoa_maxcut/candidate.py
4bbfddd37158e6e2fc233b6feaeac391a929e0f34fcf6c4ce81f5ac9c1343e23  evals/tasks/quantum/qft_phase_pattern/candidate.py
ef7954bc50e7e39bd989a3d0feb0a6bea63b385aebc90c2d3d2215b9505b7b09  evals/tasks/quantum/qft_phase_pattern/tests.py
c7fdd0cdb37181a5d17ab9c2f9cbf2d7f41a877e45a58abed0bd89050cb280dd  evals/tasks/quantum/qiskit_qft_entangled/candidate.py
9847758ddba6fc2e70f1e6673787f0ab7ba3212dd218c4d003df54feec9dadac  evals/tasks/quantum/qiskit_qft_entangled/task.json
5fe817cf31b288e9ca3c1b481818a99a390498e15057f1da865fadcc1ecb169c  evals/tasks/quantum/qiskit_qft_entangled/tests.py
56828d0864714775e0c4d6bad5731e7fc1ba05d41bdb561c09030101a531612a  evals/tasks/quantum/quantum_bell_basis_discrimination/candidate.py
8ec6477bb5f1ad67655a1aad8120d4272f0e91eb11377958e17f83042ca1b764  evals/tasks/quantum/quantum_bell_basis_discrimination/task.json
0106c3e28e4406c38988bb6d99e253783e7b65194231471dd94623b6471caeaa  evals/tasks/quantum/quantum_bell_basis_discrimination/tests.py
a6dc2f09d5d1a26fa6a0a7c9bfee82f97277621c53e0cff451aa23148d2c53cc  evals/tasks/quantum/quantum_channel_depolarizing/candidate.py
e35912c10f0414dd665c50acf05ef5edd954aa2a7286177a8b50df8c8d5c207e  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/candidate.py
4b87bf5ec307d1fe6bbc2d06da8c31fe9102ca7dc36617075de3a309a9633784  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/task.json
16c446c9ff37b6000febfc411cfbb9b2afb966415473ac6d7aeeeb3d14019796  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/tests.py
704ae205c1689f1a422be5437f815d3f005cb3e6f9f18e14dce14108f0665bd2  evals/tasks/quantum/quantum_error_correction_shor_9qubit/candidate.py
53a4fca2a1d4bc50bbe1ae037365dfb4cb385867f86f17e43aac1826a49f942a  evals/tasks/quantum/quantum_qaoa_ring4_landscape/candidate.py
18c4c230851bea8b9a7c07e7e63a6c589a7aae0121c925c7464e9f5a169290a3  evals/tasks/quantum/quantum_qaoa_ring4_landscape/task.json
7b0edb9582b791f25e7f037ec2192e022a1aca156523c7a30b7e8b8323390ec0  evals/tasks/quantum/quantum_qaoa_ring4_landscape/tests.py
d120dacccc7a7e5275ae82e8fb51237633b30251f1b1630322d69a5c603ae8ab  evals/tasks/quantum/quantum_qft_periodic_state/candidate.py
ebd267d28641ee82b1ab3eb8cc1311a4404d9c2f4c396fc16e67f54d8f8b2590  evals/tasks/quantum/quantum_qft_periodic_state/task.json
1a5c67ea0d792acfb89b1f145a49f9e6a3b41ac1f5d01b2f2fcb794d67698b54  evals/tasks/quantum/quantum_qft_periodic_state/tests.py
da8a2df5ff111a370dce3dbc544fb0a94070e233d830e0209ae180196175c70a  evals/tasks/quantum/quantum_qml_variational_classifier/candidate.py
3797013aad4f4306494b05d6aaba2bcf58e9c0421399d98704c020004f8a15d7  evals/tasks/quantum/quantum_qml_variational_classifier/task.json
4ceb0643fe809c9d002605f18f949cbcc817ef46d73ee4d583fe6ab7ec99a814  evals/tasks/quantum/quantum_qml_variational_classifier/tests.py
cf077341049dda9bda626fea2988152c5578ed94019bf78f44b27a3004ce7494  evals/tasks/quantum/quantum_shor_phase_error_correction/candidate.py
924f62d00478418c0f8c050e9a5b1fa55d3dcc0c1ec33c2be275793849b99250  evals/tasks/quantum/quantum_shor_phase_error_correction/task.json
caa2f5ad530912bca05b7dc2fd653b545be269b4e2d04afb800316e27637a88d  evals/tasks/quantum/quantum_shor_phase_error_correction/tests.py
2fcbc2262b455b17fb03c676d706d815d17c00cfaeebb59f873860816a83beb4  evals/tasks/quantum/quantum_stabilizer_shor_generators/candidate.py
394cc88cf03ea9fa5455cbf6c5b70ee9322c303a64999ef730a0322765b12c5e  evals/tasks/quantum/quantum_stabilizer_shor_generators/task.json
4b624df712bace522ab885719fdf3c9d7f809a2ecf80332983302ce59c988714  evals/tasks/quantum/quantum_stabilizer_shor_generators/tests.py
94387663f339549e17e7140b689f21568c6aec325f998b43c7363a773d4f0e49  evals/tasks/quantum/quantum_three_qubit_entropy/candidate.py
b2b14d381a003e9b592ab7635309bb6dedf326cc4ee604f200862ee0e31a0216  evals/tasks/quantum/quantum_three_qubit_entropy/task.json
924589a11f316b781a2bcf859349605d26277616b50cd948d45858d67d53e160  evals/tasks/quantum/quantum_three_qubit_entropy/tests.py
4517812d3ba0b406e7d8c8bae538e6d8b98a2169315536e881e8d724567fb644  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/candidate.py
963bb4f6b79e121051a2d333653e000370aae6f3fc2cbf60b15039fc0204bb01  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/task.json
ea61dcafa29bff20cf30e0e9e5a3136f108849fdc60a66ff09ee00b3cadd0141  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/tests.py
20e155a60b412fa0567a163c6351b6ba1e65cd3aeb83aaca6c6d0faa3afe5f18  evals/tasks/quantum/quantum_vqe_heisenberg_energy/candidate.py
8509c851c68dff4c743dd3a7572579698ba9f382bb77f64bd7405dfdb49935fb  evals/tasks/quantum/quantum_vqe_heisenberg_energy/task.json
8a04b56c4c4ab367dc28bd579ad8a921fbca1ebc46270392fb9d89e5b32af16c  evals/tasks/quantum/quantum_vqe_heisenberg_energy/tests.py
7042529da93af3815df7941a9937a1476b1fd18d5571c0605acd617580b174f8  evals/tasks/quantum/stabilizer_tableau_update_repair/tests.py
e1bea2e227a012ae8b066f9cac0e3534a971b56a11270f3c40ca85d23d60a8cd  evals/tasks/quantum/superdense_coding/task.json
e3daa4ff10309b0044f6ed4fe5a707b6992fafcc180c30dd838af7bb906f9b7e  evals/tasks/quantum/superdense_identity_lookup/tests.py
fd6e10cad2e3c9c0d9176eefc5a165c2202b2c4ef97b3d513b64bfa922d3db59  evals/tasks/quantum/superdense_pauli_router/tests.py
dd4ff8fe03ad22e2d37a41683bd166ab787edc7f807dbef473babe54a0a96598  evals/tasks/quantum/teleportation_corrections/tests.py
c125239727ff913543e727979e7aa480341d99331b75f27324782c98793206c2  evals/tasks/quantum/vqe_energy_minimization/candidate.py
5f723b9e328abd5d08462d7dc0ccdb1c395eea31a89357c53e89ed07f16485a0  reports/sapo-holdout-enrichment-manifest-2026-08-24.json
ea5b263226494fa9a5831453e68c3f7a533ebfb2804e14094dc40d66fd890ff2  scripts/ai_launch_sapo_direct.sh
fbabaa113e96d1529742debaabde4b93184a95d3d9864c1cb41dd61f8b09efd9  scripts/asi2_launch_grpo_27b_selfeval.sh
63158871a80cfe275d168c0519149b88abdb707bae69b7b5a6e5036fff1159a9  scripts/asi2_watchdog_relaunch.sh
85f1f99f4f28b888585df9ffe193925f9b003b3067520e0d4c063f1ba36e14ce  scripts/asi3_launch_grpo_direct.sh
77bb097c26c6e3fbddb7911d92ed534f387eea7d1084b3da70efab32a9d3c94f  scripts/build_grpo_v8_manifest.py
5ab1acc36c0f1be0668634962a7583d22023119d68030d4dc6e23353fdb2bf0a  scripts/calibrate_model_judge.py
c07351d46a03ae1669f6d5430dee7b966b8dce80ae6e23390220d7b32d482903  scripts/decide_sapo_promotion_gate.py
d49aaeea2d1c25ff09df418ba594037e14a573554ed8d57d6a7f6afa7c944de6  scripts/eval_100_reeval.py
d97f9a7f7a018e4de774b59c3a0fb6e3622d03c61762f4cc5ba7f5abb1323fe8  scripts/eval_base_vs_adapter.py
766949e44a541db7ab9ddcdef50a5f9c60fcd53b66c992f80ed39e26197426c9  scripts/fine_score.py
94274f251f762a8c5d7d9c4e3bcdfd1d482551729b6ee032f55105a3985bcc3e  scripts/fv_gspo_repair_sidecar.sh
e35703662de7eeff9e2119c905f2da8f75c2a49e73ffd51833eda16750add759  scripts/report_base_adapter_comprehensive.py
2047b9a00169789ee8cbc851aeccd8e0de18805873a0022967b0886903cd2643  scripts/run_base_vs_adapter_eval.py
5c769d6c9626f1551a48e4db0478ec4cae299140d740dcaafe251ba67970f989  scripts/run_hf_pass1_eval.py
61c17c6529e12b9cc29ca2400618ea2112567c489508d2556e52607aec058a80  scripts/sapo_drift_watch.py
7a83b6c7d3ae2a3ccf11c19ca7ad1a2bde40ca8895d02a5455b0c1dd7a1fc048  scripts/sapo_math_audit_step_records.py
2eeea835761b1a3551ba7af517c2f19369ff20266310db4af1b4e9f2dfa1f95b  scripts/sapo_reward_audit.py
010e3d1dd1b22dbe4bc1b157abc838b82730afca5fbc5b1f1995b82ca184b925  scripts/sapo_status_snapshot.py
5607dbb49318f8f5106dad1eea253b23d65c7272da38999c21620e7f991319c5  scripts/serve_openai_chat_adapter.py
7890847631dc903c6e07574aac47cb71f2dbf3c952527420ef6e22c768313f83  scripts/submit_asi2_grpo_27b_selfeval_task.sh
6edb98a84668f53471c786c1770bf9c392168f77de505ca3dcf96a075bb39498  tests/test_asi3_sapo_launcher_readiness.py
938e97eb8f5af240b2653088e14da876497e001ae5d06aec3f1d93a5ab733178  tests/test_compat.py
6354b5c4428627270d8a4b2da06aec2497f9880a307beedb57e81d4f19c612cc  tests/test_execute_run.py
84b85e3d743de62e286b2b2f185cb9982151b1652bb80b59673c29869edb23f0  tests/test_fine_score.py
98598a2a94576bfc42b0eb438cea588bce207202582167bdd8da800432a4975b  tests/test_grpo_rollout_mix_entropy_floor.py
a97649ef1227988886fd29ad7fd5388430ac66248de53927a20e1de0aa72f5ca  tests/test_grpo_train_pass_truncation.py
97ec2387c5be9dccab1feccf3460371bbaadd559d4deda6280fb65949eeac939  tests/test_grpo_trainer_breakers.py
495b873f619754772bc55ad51d11a327271fe3e1ddce9d610211e473074da7d7  tests/test_grpo_trainer_eval_results.py
083ff7cbf7cdd89d8b95c1ecfc041d78ce35b7e4b44a48763ef04fef8effb168  tests/test_grpo_trainer_generation_stop.py
d0b8f6442d93c8fecfed3bed62531253c991f33734b26dff94cf158f7caba3e1  tests/test_grpo_trainer_loss_stats_router.py
19b6cd0b8a628ec636ddca043b3de33de979883f19dfcbc9b6a6a6ea361e0902  tests/test_grpo_trainer_main_failclosed.py
528ef0e1ef2799862eb3977a5c0d53f37ed653954886b5116098b10c9eac033e  tests/test_grpo_trainer_metrics.py
15bb6ca5d7394cb4273f7060c3b2cb36c3b38991fdc8cf0757a7b3aa9b07104b  tests/test_grpo_trainer_resume.py
b57d191b4ada2b97ad276ab609de74d1cbc129016563aea16f6134384a3350b3  tests/test_grpo_trainer_self_eval.py
59330ffb5a28ababb0934deb6b1f6e2ab7982c705152c4bc1ae8087cff1b79bf  tests/test_grpo_trainer_sigterm.py
eb6b45cbdded0f936bdae02aa9e2fe3de22c6e4494071cb398436d49f2ca64a1  tests/test_grpo_utils.py
0f9d1b0f62e9c9a825061fd54c6ae1f71fd902733fb592a0beac82a0cd6df803  tests/test_holdout_enrichment_invariance.py
9a8c71d22816dab414376030a60c77a7f232af2217e86d255df788c023b58b75  tests/test_holdout_scorer_version_awareness.py
1bd8105aa4b1ab4d3eecf0dd151969a86cac4ac4ccaf0d205b7c7adfe4e37ff7  tests/test_model_family_support.py
1b587b54f3acdedd50b733558ac7dbf80ba96b2d75384aa1119808750e8165d7  tests/test_model_judge.py
6363e022f9c0d6a16200f385e9a5a845df5b0c93e66abcb9389c648fa4235a9c  tests/test_pennylane_vqe_h2_scorer_versions.py
caea3662eb1cb632fd4c7b881e0081b157cb7708325739e52a4f45dbbc5accdb  tests/test_prepare_prompts_coverage.py
f43b364994eb1dfcdceb7314127da94a7154d292907f9c781119b54dd5fa3824  tests/test_promotion_eval_adapter_merge.py
60437d05c8fefac612d5e48f7105fc31907ec45925acfec28d7f22f55262ce8f  tests/test_report_base_adapter_comprehensive.py
2bcdae7e8bc4407dd55d0be549b910c2305d80a4a9f7f3a8b59f7f58afa49c6d  tests/test_run_eval_scoring.py
7f37d88898c639d677eaeebd7c2a914f9710a6a71a9547cfa8956b16698a2b08  tests/test_sapo_curriculum_holdout_adjacent.py
f68e2261ab1cef28df4cef65aaaaa815c6306d129bb2f0d17cae31e7c3da15db  tests/test_sapo_drift_watch.py
2c5d5a901992ca5f7e0cec39e268d71b2d0f157e4add6851a551aeeaee8fb9f9  tests/test_sapo_eval_security.py
d79ae1884791178a1fd2902224055c3ba4939b531e4d28ba74ed18bd191e71f4  tests/test_sapo_loss.py
b7b4ad1b64e22d99c268d948583c00b419f6f0354d91e270d2146dab9ad94dbc  tests/test_sapo_promotion_pipeline_hardening.py
78dd512c92ada912fa7487792d81bdf7899bd07c6b0c5d77fc0fe4bae2e53127  tests/test_sapo_prompt_audit_cli.py
cceee5cb5733a2dd06f251b6c8544fe06972be02d1032da7d14301fac0a7dbf4  tests/test_sapo_reward_audit_cli.py
974ee9324b55b608509e337a6e7eac01d13651c5a8c66bf40f87e5d32155a4a2  tests/test_sapo_reward_audit.py
ff59d248dfba4ea7fbbfbf40061b482c614613e2573c7f9b184e69bb975a5f9b  tests/test_sapo_status_snapshot.py
81863a1a6fef400243d3f7fabc7da6742b765e2a15b9280d498e0733fad6d832  tests/test_seed_run_with_references.py
1daa2c7e60bc461c57bb02117cd627846441d08e20835dd8c710cfd4b4e5cb85  tests/test_single_candidate_eval.py
b81877e0f9168cdf1f11c54b6d06f9c224a879df8bf2cebe2722edf54098f58e  training/acquire_public_qwen_snapshot.py
f1c5d2511d18f16445acf86e738de6680dae768b2115bf8935869522f6d4e62e  training/audit_model_source.py
9f65ba9acabdfa09ac425a22c778c5480f8dee8b61494412504b7948a9d59be5  training/compat.py
a0839dcb2cc41de87a3b2171609ecc8930fd4cd95a772fe3784dce60dd76cc87  training/generation.py
4ab6f70e8d03b276c7a4de26ca7b38f8e976977bd53eca110f6d3d650e0c2594  training/grpo_trainer.py
73de15500003ed8e7f9ea05d02146ac9b7f01c1444f3828c93a2625ba435ae1e  training/grpo_utils.py
4f24ff8bb7fd9058ff273971c0d2be5a66338eea75fde756a979fdc583c3b88a  training/huanxin_cpu_smoke.py
2b0dcb760f35449e68a921ac807229ffcff676ba8983b718efa35f09e421acfb  training/inspect_moe_target_modules.py
5eac8e4fa3f17106d9852f50bd50daf340bc7d72e4e918695e1b7ae5e0496e1b  training/model_backend.py
8887b0664c94cfec7ba5817868bc34835df26c607e9195e42a5f9bd7b8a32f5e  training/model_family_preflight.py
10b237931f9eed984af9db86307eb02212e59bf3125033eec54097a243965db2  training/quantum_verifiers.py
f69033af0f58e28e87e5399a5858da7ae9d775470b626bd21f9735771c0e6818  training/qwen_sft_peft.py
c3efeaff20d2ee0fba3bdf48b46259028906672fbde736671c16373c1677af9e  training/research_plugins.py
8a1132457a55687b195215abad027ee2c13051ae0907b092109540211e5feb73  training/runtime_overlay.py
1339972471e2aba8d95c420a9e9be2fb34cfeed5c2304c65435efa9578e23040  training/teacher_free_repair.py
2f8dfad36b8679e6ecc16d6f0fae9a1b6eea4230843e9c8b072bdb5b79eedda6  training/text_preprocessor_backend.py
dc619538b009e94bc22613256bc05b64a398a5af4d3e0f08d27923faa540e6cc  training/turboquant.py
e01b3e4050ff29184d0b630d6324bd368df984f1d531c19872bea1931394da46  training/verify_qwen_snapshot.py

## r12 DEPLOY — run-8 OOM fix (2026-08-26 ~13:4x-13:5x CST)
- INCIDENT note: local tmp/ was WIPED (~13:40 CST — all r0-r11 tgz+manifests
  gone). Recovered r11's 164-member list from the deploywatch.md record
  (recorded at r11 build) + box-side relaunch_r11.tgz; all 164 still present
  in tree. Box bundles unaffected (deployed state intact — the 10:27-class
  mandate holds: the DEPLOYED bundle + record are the recovery source).
- r12 = recovered 164 + tests/test_grpo_entropy_token_cap.py +
  tests/test_grpo_trainer_faulthandler.py = 166 members (fix: entropy_token_cap
  default 256 in grpo_trainer.py — OOM root cause: entropy-floor branch
  retained ~37 GiB, 43.58→80.94 GiB; capped at first 256 completion tokens,
  measured back to 49.21 GiB; TDD 5/5 + 293 focused green).
- Gates: closure CLOSURE OK (166, new tests import-clean), py3.9 0 real hits,
  locks none, markers clear; member==manifest==tree verified.
- Deploy: 104x6000B chunks, 0 failures, audit clean (103x6000+4680); box sha
  c0613c34… == local, 467009 B both sides.
- Run tree refreshed; on box: GRPO_TRAINER IMPORT OK; entropy_token_cap wired
  (arg :1863, cap logic :1947-1953); both new tests present.
- Launchsim slim rehearsal signaled: /tmp/sapo_launchsim_r12_TRIGGER.
  Executor relaunches on ITS pass.
- NEXT CYCLE: freshness + lock + register + closure scans.

### r12 manifest (166 members, sha256)
85106d8e4c0c337edbc95eec2972d363c96f50f2d91c0d4404438dff386c4f27  configs/rl/qwen36_27b_fv_gspo_asi2.json
7b8bdc04fe2a6b41ba867facdebe04170bf7c864a2e09c2b446718764f060f18  evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt
18d8b065dd70c63dd55c3b4e6f229b2c741f77b39f8bd9ae409686aaa6b3ac65  evals/runner/candidate_sanitize.py
498c04c31b09dbd237d32f35839a2340b64e3da4420ab10467cd5a0962fb3336  evals/runner/candidate_security.py
4f149f9819df3c49ec57be9358a72463263343e17ddb3b648b7e13ac912ffa33  evals/runner/execute_run.py
8cdf777b630422df6bc3cd993353022b9719bc8df40657d058d6ab16b807c89b  evals/runner/frozen_contract.py
8216b8421947fe656731e0c26ff661bd341a3a7da977888babb27aa7d9d8831c  evals/runner/prepare_prompts.py
e26b9ade036c75993e4126acbe5f6e9b834c8e1173959226a3a78c9f25ab29af  evals/runner/public_task_spec.py
97b5186207302723f47281a4ed1e19e3406518537031dd243cdd162d24063093  evals/runner/run_eval.py
a181cd994245f51a605cb20f69ae17da2f2cf3a06c648d2bcf066beec5d0dbe4  evals/runner/seed_run_with_references.py
c4fa8bfa41c6edeecbb7816d3da3d7e6672772bafd4e2e4073047931ad350947  evals/runner/single_candidate_eval.py
618088bda4208f9ca8d84361ee4068b51cc36da67d82313e8a353846405d3076  evals/runner/task_metadata.py
0108c020f916b8dbf8ab16d08560d0057265ecaee0f5f37289620a7e0e8f0e54  evals/tasks/quantum/bell_pair_construction/candidate.py
9f6bf09c6019fb84748c9df10638291fd62bfcc90fa049642b980a1541b52403  evals/tasks/quantum/bell_pair_construction/tests.py
976677faa3f3138f9ac53c1435cbb8002ef380dabff6dc74f2f4fc4821620da1  evals/tasks/quantum/binary_measurement_decoder/task.json
114bd9cf91467960db9b629475aad730929625271b7ea76e453199b3b40b6690  evals/tasks/quantum/binary_measurement_decoder/tests.py
48d45ea9b46d7e54f23edbb62e94e7fb132884250506e342c460c7c9bba2d7db  evals/tasks/quantum/bitstring_maxcut_landscape/tests.py
4b4c0ea792f29454d0430a473cdaa778bc1432801c7f2c8c0d935520c89a29e5  evals/tasks/quantum/circuit_phase_repair/tests.py
6ee4de0769c7dd49dfa317d83035cc870c83020b9094cac23d5724f6f30fbdc6  evals/tasks/quantum/density_matrix_partial_trace/candidate.py
311688fed1cf708c6cbbe7854c724c422758526c1e6d13f12d1f1d1eb409e804  evals/tasks/quantum/error_detection_bit_flip/tests.py
18ed2cb56ee7c96529c53d65921deb4c44dcfdedce5d2bb275e36b714d59e6ae  evals/tasks/quantum/gate_alias_casefold_barrier/candidate.py
5feaa43a0f846f7d605e3b9ee6946ba4e4d53e61da07ed4ea7d40117218db661  evals/tasks/quantum/gate_alias_casefold_barrier/tests.py
f1cf1e1144aeef96acac9f527b6b3d96ea9c0c938121a48d9f2fc735599d9525  evals/tasks/quantum/gate_alias_normalization/task.json
4e17b821390f6916b8fd29d64061489a7bde5367a648b8227b26276a79b97143  evals/tasks/quantum/gate_alias_normalization/tests.py
fb4c96d30a8260ad6aa9895e3c2673d3dd7cc264d9f0958bfa0d9a163eb7760b  evals/tasks/quantum/gate_alias_registry_cleanup/candidate.py
d02d9e3673930d64c3dd1483d8ebf00c6b23764fa18fe542f16930313722100f  evals/tasks/quantum/gate_alias_registry_cleanup/tests.py
8cba17a29939f736e18e729a86fbbef83be4db9811890f2467dac666f805d931  evals/tasks/quantum/gate_token_canonicalizer/tests.py
7a6d4835c6cf027a323a720cd9698cf80560470c9c3aba7652965da3aeaac224  evals/tasks/quantum/ghz_state_witness/candidate.py
48db0b26936ba658f1f6e9bc61e416c07888d4cb5c17a1fbcd1bea8b4e30d464  evals/tasks/quantum/ghz_state_witness/tests.py
8b0496f1b2f2d671774a3ff5ae38bbd3a12764f64a187274b022eb1f0592a0e6  evals/tasks/quantum/grover_oracle_diffusion/candidate.py
eca1461b210a9e9244be9876e7c4cc2ae0648beb6eb167c59247987a2fcc922c  evals/tasks/quantum/grover_oracle_diffusion/tests.py
0b0ac2c05ac0ddbe685a4244e4e39fd315669e1cce18b3546496f3a65414a600  evals/tasks/quantum/maxcut_assignment_enumerator/tests.py
c2ca2881a761af3709496a1598360c4b545cc489822445e30cbd2e7afaf878e7  evals/tasks/quantum/maxcut_partition_ranker/candidate.py
23377a27912b10f10417748b130a25cefa7d84c08fe5f44e3ee49b21ec9da758  evals/tasks/quantum/maxcut_partition_ranker/tests.py
4d96a1e736f4b95157c39e7bba399786142ccd8f9889d49de4d5ef8e73af87a6  evals/tasks/quantum/measurement_bug_repair/tests.py
563553f63aa5bd957cc4e73e52cc787864567e1e479d3199300bda019962bf0b  evals/tasks/quantum/pauli_message_codec/tests.py
3cab7c4111f541c247ff98769efadb772b4f9ca7d9846ea13bce96d3d4137061  evals/tasks/quantum/pennylane_qml_iris_classification/task.json
8982efe7a2fdcde6fa723d77db797137a741508ebda8d2f4cc0610ebc25c4829  evals/tasks/quantum/pennylane_qml_iris_classification/tests.py
b8f8cd014abf677dd7f22e509043260db2e15ae2dc02f4bee0e6225bb44fd8b2  evals/tasks/quantum/pennylane_vqe_h2/candidate.py
18f1ff5d5dc2ee486e8a2f0faa6b2a00937cedbed8d967e7534b300eba93718e  evals/tasks/quantum/pennylane_vqe_h2/task.json
76a0106a456cea4652535dfe4ba9dadeac6825cae4ba3196e50e3a88ab4305b9  evals/tasks/quantum/pennylane_vqe_h2/tests.py
0ed7b78ecaaf776fbf8a0dc9e7709d58d17d4ea52c617b6ee3e164686fbd1121  evals/tasks/quantum/phase_estimation_circuit/candidate.py
9e4454a5be086d3484fe0f53fb63167e574baa04c9a632224bc25db34fd01fde  evals/tasks/quantum/phase_estimation_circuit/tests.py
06f85efba02647dc0c70e27450ece118df0ffc54d18d28df046ff319420547a9  evals/tasks/quantum/phase_measurement_register/tests.py
cef961ca651f7d14be1de207da598be883f1b3df1f1aadbec677c7f7ae724d8c  evals/tasks/quantum/phase_register_roundtrip/task.json
710ea354eb1d74d20d464f555428e2d78f77b1d0647cdfc6ab1543798335fe7c  evals/tasks/quantum/qaoa_maxcut/candidate.py
4bbfddd37158e6e2fc233b6feaeac391a929e0f34fcf6c4ce81f5ac9c1343e23  evals/tasks/quantum/qft_phase_pattern/candidate.py
ef7954bc50e7e39bd989a3d0feb0a6bea63b385aebc90c2d3d2215b9505b7b09  evals/tasks/quantum/qft_phase_pattern/tests.py
c7fdd0cdb37181a5d17ab9c2f9cbf2d7f41a877e45a58abed0bd89050cb280dd  evals/tasks/quantum/qiskit_qft_entangled/candidate.py
9847758ddba6fc2e70f1e6673787f0ab7ba3212dd218c4d003df54feec9dadac  evals/tasks/quantum/qiskit_qft_entangled/task.json
5fe817cf31b288e9ca3c1b481818a99a390498e15057f1da865fadcc1ecb169c  evals/tasks/quantum/qiskit_qft_entangled/tests.py
56828d0864714775e0c4d6bad5731e7fc1ba05d41bdb561c09030101a531612a  evals/tasks/quantum/quantum_bell_basis_discrimination/candidate.py
8ec6477bb5f1ad67655a1aad8120d4272f0e91eb11377958e17f83042ca1b764  evals/tasks/quantum/quantum_bell_basis_discrimination/task.json
0106c3e28e4406c38988bb6d99e253783e7b65194231471dd94623b6471caeaa  evals/tasks/quantum/quantum_bell_basis_discrimination/tests.py
a6dc2f09d5d1a26fa6a0a7c9bfee82f97277621c53e0cff451aa23148d2c53cc  evals/tasks/quantum/quantum_channel_depolarizing/candidate.py
e35912c10f0414dd665c50acf05ef5edd954aa2a7286177a8b50df8c8d5c207e  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/candidate.py
4b87bf5ec307d1fe6bbc2d06da8c31fe9102ca7dc36617075de3a309a9633784  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/task.json
16c446c9ff37b6000febfc411cfbb9b2afb966415473ac6d7aeeeb3d14019796  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/tests.py
704ae205c1689f1a422be5437f815d3f005cb3e6f9f18e14dce14108f0665bd2  evals/tasks/quantum/quantum_error_correction_shor_9qubit/candidate.py
53a4fca2a1d4bc50bbe1ae037365dfb4cb385867f86f17e43aac1826a49f942a  evals/tasks/quantum/quantum_qaoa_ring4_landscape/candidate.py
18c4c230851bea8b9a7c07e7e63a6c589a7aae0121c925c7464e9f5a169290a3  evals/tasks/quantum/quantum_qaoa_ring4_landscape/task.json
7b0edb9582b791f25e7f037ec2192e022a1aca156523c7a30b7e8b8323390ec0  evals/tasks/quantum/quantum_qaoa_ring4_landscape/tests.py
d120dacccc7a7e5275ae82e8fb51237633b30251f1b1630322d69a5c603ae8ab  evals/tasks/quantum/quantum_qft_periodic_state/candidate.py
ebd267d28641ee82b1ab3eb8cc1311a4404d9c2f4c396fc16e67f54d8f8b2590  evals/tasks/quantum/quantum_qft_periodic_state/task.json
1a5c67ea0d792acfb89b1f145a49f9e6a3b41ac1f5d01b2f2fcb794d67698b54  evals/tasks/quantum/quantum_qft_periodic_state/tests.py
da8a2df5ff111a370dce3dbc544fb0a94070e233d830e0209ae180196175c70a  evals/tasks/quantum/quantum_qml_variational_classifier/candidate.py
3797013aad4f4306494b05d6aaba2bcf58e9c0421399d98704c020004f8a15d7  evals/tasks/quantum/quantum_qml_variational_classifier/task.json
4ceb0643fe809c9d002605f18f949cbcc817ef46d73ee4d583fe6ab7ec99a814  evals/tasks/quantum/quantum_qml_variational_classifier/tests.py
cf077341049dda9bda626fea2988152c5578ed94019bf78f44b27a3004ce7494  evals/tasks/quantum/quantum_shor_phase_error_correction/candidate.py
924f62d00478418c0f8c050e9a5b1fa55d3dcc0c1ec33c2be275793849b99250  evals/tasks/quantum/quantum_shor_phase_error_correction/task.json
caa2f5ad530912bca05b7dc2fd653b545be269b4e2d04afb800316e27637a88d  evals/tasks/quantum/quantum_shor_phase_error_correction/tests.py
2fcbc2262b455b17fb03c676d706d815d17c00cfaeebb59f873860816a83beb4  evals/tasks/quantum/quantum_stabilizer_shor_generators/candidate.py
394cc88cf03ea9fa5455cbf6c5b70ee9322c303a64999ef730a0322765b12c5e  evals/tasks/quantum/quantum_stabilizer_shor_generators/task.json
4b624df712bace522ab885719fdf3c9d7f809a2ecf80332983302ce59c988714  evals/tasks/quantum/quantum_stabilizer_shor_generators/tests.py
94387663f339549e17e7140b689f21568c6aec325f998b43c7363a773d4f0e49  evals/tasks/quantum/quantum_three_qubit_entropy/candidate.py
b2b14d381a003e9b592ab7635309bb6dedf326cc4ee604f200862ee0e31a0216  evals/tasks/quantum/quantum_three_qubit_entropy/task.json
924589a11f316b781a2bcf859349605d26277616b50cd948d45858d67d53e160  evals/tasks/quantum/quantum_three_qubit_entropy/tests.py
4517812d3ba0b406e7d8c8bae538e6d8b98a2169315536e881e8d724567fb644  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/candidate.py
963bb4f6b79e121051a2d333653e000370aae6f3fc2cbf60b15039fc0204bb01  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/task.json
ea61dcafa29bff20cf30e0e9e5a3136f108849fdc60a66ff09ee00b3cadd0141  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/tests.py
20e155a60b412fa0567a163c6351b6ba1e65cd3aeb83aaca6c6d0faa3afe5f18  evals/tasks/quantum/quantum_vqe_heisenberg_energy/candidate.py
8509c851c68dff4c743dd3a7572579698ba9f382bb77f64bd7405dfdb49935fb  evals/tasks/quantum/quantum_vqe_heisenberg_energy/task.json
8a04b56c4c4ab367dc28bd579ad8a921fbca1ebc46270392fb9d89e5b32af16c  evals/tasks/quantum/quantum_vqe_heisenberg_energy/tests.py
7042529da93af3815df7941a9937a1476b1fd18d5571c0605acd617580b174f8  evals/tasks/quantum/stabilizer_tableau_update_repair/tests.py
e1bea2e227a012ae8b066f9cac0e3534a971b56a11270f3c40ca85d23d60a8cd  evals/tasks/quantum/superdense_coding/task.json
e3daa4ff10309b0044f6ed4fe5a707b6992fafcc180c30dd838af7bb906f9b7e  evals/tasks/quantum/superdense_identity_lookup/tests.py
fd6e10cad2e3c9c0d9176eefc5a165c2202b2c4ef97b3d513b64bfa922d3db59  evals/tasks/quantum/superdense_pauli_router/tests.py
dd4ff8fe03ad22e2d37a41683bd166ab787edc7f807dbef473babe54a0a96598  evals/tasks/quantum/teleportation_corrections/tests.py
c125239727ff913543e727979e7aa480341d99331b75f27324782c98793206c2  evals/tasks/quantum/vqe_energy_minimization/candidate.py
5f723b9e328abd5d08462d7dc0ccdb1c395eea31a89357c53e89ed07f16485a0  reports/sapo-holdout-enrichment-manifest-2026-08-24.json
ea5b263226494fa9a5831453e68c3f7a533ebfb2804e14094dc40d66fd890ff2  scripts/ai_launch_sapo_direct.sh
b065121dd8df4de67fcf6e982f6a64eeda22c7d1cae2783a62e040d9c1718fb1  scripts/asi2_launch_grpo_27b_selfeval.sh
63158871a80cfe275d168c0519149b88abdb707bae69b7b5a6e5036fff1159a9  scripts/asi2_watchdog_relaunch.sh
8a0010e793f120aa6ba622a6f298e6869e748f66bbf47b61f550bc9e5df6e61a  scripts/asi3_launch_grpo_direct.sh
77bb097c26c6e3fbddb7911d92ed534f387eea7d1084b3da70efab32a9d3c94f  scripts/build_grpo_v8_manifest.py
5ab1acc36c0f1be0668634962a7583d22023119d68030d4dc6e23353fdb2bf0a  scripts/calibrate_model_judge.py
c07351d46a03ae1669f6d5430dee7b966b8dce80ae6e23390220d7b32d482903  scripts/decide_sapo_promotion_gate.py
d49aaeea2d1c25ff09df418ba594037e14a573554ed8d57d6a7f6afa7c944de6  scripts/eval_100_reeval.py
d97f9a7f7a018e4de774b59c3a0fb6e3622d03c61762f4cc5ba7f5abb1323fe8  scripts/eval_base_vs_adapter.py
766949e44a541db7ab9ddcdef50a5f9c60fcd53b66c992f80ed39e26197426c9  scripts/fine_score.py
94274f251f762a8c5d7d9c4e3bcdfd1d482551729b6ee032f55105a3985bcc3e  scripts/fv_gspo_repair_sidecar.sh
e35703662de7eeff9e2119c905f2da8f75c2a49e73ffd51833eda16750add759  scripts/report_base_adapter_comprehensive.py
2047b9a00169789ee8cbc851aeccd8e0de18805873a0022967b0886903cd2643  scripts/run_base_vs_adapter_eval.py
5c769d6c9626f1551a48e4db0478ec4cae299140d740dcaafe251ba67970f989  scripts/run_hf_pass1_eval.py
61c17c6529e12b9cc29ca2400618ea2112567c489508d2556e52607aec058a80  scripts/sapo_drift_watch.py
7a83b6c7d3ae2a3ccf11c19ca7ad1a2bde40ca8895d02a5455b0c1dd7a1fc048  scripts/sapo_math_audit_step_records.py
2eeea835761b1a3551ba7af517c2f19369ff20266310db4af1b4e9f2dfa1f95b  scripts/sapo_reward_audit.py
010e3d1dd1b22dbe4bc1b157abc838b82730afca5fbc5b1f1995b82ca184b925  scripts/sapo_status_snapshot.py
5607dbb49318f8f5106dad1eea253b23d65c7272da38999c21620e7f991319c5  scripts/serve_openai_chat_adapter.py
7890847631dc903c6e07574aac47cb71f2dbf3c952527420ef6e22c768313f83  scripts/submit_asi2_grpo_27b_selfeval_task.sh
6edb98a84668f53471c786c1770bf9c392168f77de505ca3dcf96a075bb39498  tests/test_asi3_sapo_launcher_readiness.py
938e97eb8f5af240b2653088e14da876497e001ae5d06aec3f1d93a5ab733178  tests/test_compat.py
6354b5c4428627270d8a4b2da06aec2497f9880a307beedb57e81d4f19c612cc  tests/test_execute_run.py
84b85e3d743de62e286b2b2f185cb9982151b1652bb80b59673c29869edb23f0  tests/test_fine_score.py
061137bcc408f24c9fd97d14bdb58fa04cb419cd2bdcc90cfc17218091010fde  tests/test_grpo_entropy_token_cap.py
98598a2a94576bfc42b0eb438cea588bce207202582167bdd8da800432a4975b  tests/test_grpo_rollout_mix_entropy_floor.py
a97649ef1227988886fd29ad7fd5388430ac66248de53927a20e1de0aa72f5ca  tests/test_grpo_train_pass_truncation.py
97ec2387c5be9dccab1feccf3460371bbaadd559d4deda6280fb65949eeac939  tests/test_grpo_trainer_breakers.py
495b873f619754772bc55ad51d11a327271fe3e1ddce9d610211e473074da7d7  tests/test_grpo_trainer_eval_results.py
2aa017cd3a07004d70f4a418bd6bc75c33161b7a520520ca4fd76f5a6cecd3a2  tests/test_grpo_trainer_faulthandler.py
083ff7cbf7cdd89d8b95c1ecfc041d78ce35b7e4b44a48763ef04fef8effb168  tests/test_grpo_trainer_generation_stop.py
d0b8f6442d93c8fecfed3bed62531253c991f33734b26dff94cf158f7caba3e1  tests/test_grpo_trainer_loss_stats_router.py
19b6cd0b8a628ec636ddca043b3de33de979883f19dfcbc9b6a6a6ea361e0902  tests/test_grpo_trainer_main_failclosed.py
528ef0e1ef2799862eb3977a5c0d53f37ed653954886b5116098b10c9eac033e  tests/test_grpo_trainer_metrics.py
15bb6ca5d7394cb4273f7060c3b2cb36c3b38991fdc8cf0757a7b3aa9b07104b  tests/test_grpo_trainer_resume.py
b57d191b4ada2b97ad276ab609de74d1cbc129016563aea16f6134384a3350b3  tests/test_grpo_trainer_self_eval.py
59330ffb5a28ababb0934deb6b1f6e2ab7982c705152c4bc1ae8087cff1b79bf  tests/test_grpo_trainer_sigterm.py
eb6b45cbdded0f936bdae02aa9e2fe3de22c6e4494071cb398436d49f2ca64a1  tests/test_grpo_utils.py
0f9d1b0f62e9c9a825061fd54c6ae1f71fd902733fb592a0beac82a0cd6df803  tests/test_holdout_enrichment_invariance.py
9a8c71d22816dab414376030a60c77a7f232af2217e86d255df788c023b58b75  tests/test_holdout_scorer_version_awareness.py
1bd8105aa4b1ab4d3eecf0dd151969a86cac4ac4ccaf0d205b7c7adfe4e37ff7  tests/test_model_family_support.py
1b587b54f3acdedd50b733558ac7dbf80ba96b2d75384aa1119808750e8165d7  tests/test_model_judge.py
6363e022f9c0d6a16200f385e9a5a845df5b0c93e66abcb9389c648fa4235a9c  tests/test_pennylane_vqe_h2_scorer_versions.py
caea3662eb1cb632fd4c7b881e0081b157cb7708325739e52a4f45dbbc5accdb  tests/test_prepare_prompts_coverage.py
f43b364994eb1dfcdceb7314127da94a7154d292907f9c781119b54dd5fa3824  tests/test_promotion_eval_adapter_merge.py
60437d05c8fefac612d5e48f7105fc31907ec45925acfec28d7f22f55262ce8f  tests/test_report_base_adapter_comprehensive.py
2bcdae7e8bc4407dd55d0be549b910c2305d80a4a9f7f3a8b59f7f58afa49c6d  tests/test_run_eval_scoring.py
7f37d88898c639d677eaeebd7c2a914f9710a6a71a9547cfa8956b16698a2b08  tests/test_sapo_curriculum_holdout_adjacent.py
f68e2261ab1cef28df4cef65aaaaa815c6306d129bb2f0d17cae31e7c3da15db  tests/test_sapo_drift_watch.py
2c5d5a901992ca5f7e0cec39e268d71b2d0f157e4add6851a551aeeaee8fb9f9  tests/test_sapo_eval_security.py
d79ae1884791178a1fd2902224055c3ba4939b531e4d28ba74ed18bd191e71f4  tests/test_sapo_loss.py
b7b4ad1b64e22d99c268d948583c00b419f6f0354d91e270d2146dab9ad94dbc  tests/test_sapo_promotion_pipeline_hardening.py
78dd512c92ada912fa7487792d81bdf7899bd07c6b0c5d77fc0fe4bae2e53127  tests/test_sapo_prompt_audit_cli.py
cceee5cb5733a2dd06f251b6c8544fe06972be02d1032da7d14301fac0a7dbf4  tests/test_sapo_reward_audit_cli.py
974ee9324b55b608509e337a6e7eac01d13651c5a8c66bf40f87e5d32155a4a2  tests/test_sapo_reward_audit.py
ff59d248dfba4ea7fbbfbf40061b482c614613e2573c7f9b184e69bb975a5f9b  tests/test_sapo_status_snapshot.py
81863a1a6fef400243d3f7fabc7da6742b765e2a15b9280d498e0733fad6d832  tests/test_seed_run_with_references.py
1daa2c7e60bc461c57bb02117cd627846441d08e20835dd8c710cfd4b4e5cb85  tests/test_single_candidate_eval.py
b81877e0f9168cdf1f11c54b6d06f9c224a879df8bf2cebe2722edf54098f58e  training/acquire_public_qwen_snapshot.py
f1c5d2511d18f16445acf86e738de6680dae768b2115bf8935869522f6d4e62e  training/audit_model_source.py
9f65ba9acabdfa09ac425a22c778c5480f8dee8b61494412504b7948a9d59be5  training/compat.py
a0839dcb2cc41de87a3b2171609ecc8930fd4cd95a772fe3784dce60dd76cc87  training/generation.py
a161f4b92cc712bac1c8dd810c6a21305a1dda0ef1c50bc9d86ecf5f03634bf3  training/grpo_trainer.py
7fa13ac448a609ea99834033bdb9e0d0eb4332ebaf4f647fe03050d67842af72  training/grpo_utils.py
4f24ff8bb7fd9058ff273971c0d2be5a66338eea75fde756a979fdc583c3b88a  training/huanxin_cpu_smoke.py
2b0dcb760f35449e68a921ac807229ffcff676ba8983b718efa35f09e421acfb  training/inspect_moe_target_modules.py
5eac8e4fa3f17106d9852f50bd50daf340bc7d72e4e918695e1b7ae5e0496e1b  training/model_backend.py
8887b0664c94cfec7ba5817868bc34835df26c607e9195e42a5f9bd7b8a32f5e  training/model_family_preflight.py
10b237931f9eed984af9db86307eb02212e59bf3125033eec54097a243965db2  training/quantum_verifiers.py
f69033af0f58e28e87e5399a5858da7ae9d775470b626bd21f9735771c0e6818  training/qwen_sft_peft.py
c3efeaff20d2ee0fba3bdf48b46259028906672fbde736671c16373c1677af9e  training/research_plugins.py
8a1132457a55687b195215abad027ee2c13051ae0907b092109540211e5feb73  training/runtime_overlay.py
1339972471e2aba8d95c420a9e9be2fb34cfeed5c2304c65435efa9578e23040  training/teacher_free_repair.py
2f8dfad36b8679e6ecc16d6f0fae9a1b6eea4230843e9c8b072bdb5b79eedda6  training/text_preprocessor_backend.py
dc619538b009e94bc22613256bc05b64a398a5af4d3e0f08d27923faa540e6cc  training/turboquant.py
e01b3e4050ff29184d0b630d6324bd368df984f1d531c19872bea1931394da46  training/verify_qwen_snapshot.py

## r13 BUILD BLOCKED — register item 1 (tests-green) UNTICKED (2026-08-26 ~15:1x CST)
- Coordinator directed r13 NOW (backward-OOM fix green: chunked-recompute,
  43.6→0.02 GiB retained; TDD 6/6, 348 focused green, stress rehearsal passed).
- BUT fresh /tmp/sapo_tests_RED (15:11 CST, testorch): 2 RED in
  tests/test_grpo_trainer_resume.py (resume next-step / resume-into-new-dir),
  root cause = unguarded faulthandler.enable() at training/grpo_trainer.py:3460
  (install_faulthandler_dumps) → io.UnsupportedOperation: fileno under capsys.
- INDEPENDENT VERIFICATION (this lane): code inspection confirms unguarded
  call (fix NOT landed); .venv pytest run of the 2 tests → FAILED with
  'fileno' error, exactly per marker. grpo_trainer.py is a register-scope
  critical file + test_grpo_trainer_resume.py is a bundle member → register
  item (1) UNTICKED → per "any unticked file = no bundle", r13 NOT tarred.
- Everything else READY: r13 list staged (167 = r12 166 +
  tests/test_grpo_chunked_recompute_backward.py), closure CLOSURE OK (167),
  py3.9 0 hits, locks none, review/launchsim markers clear. OOM fix itself
  green per marker (chunked-recompute RESOLVED, 21/21 with resume).
- UNBLOCK: one-line guard at grpo_trainer.py:3460 (try/except
  io.UnsupportedOperation/AttributeError/ValueError around
  faulthandler.enable(), or fileno check) — owner grpo_trainer rewrite lane;
  testorch clears RED. Then r13 builds+deploys immediately (staged).
- NEXT CYCLE: recheck RED + faulthandler guard presence every ~5 min.

## r13 DEPLOY — backward-OOM + faulthandler-guard fix (2026-08-26 ~15:2x-15:3x CST)
- r13 briefly BLOCKED by fresh /tmp/sapo_tests_RED (15:11): 2 resume tests red
  (unguarded faulthandler.enable() at grpo_trainer.py:3460 under capsys).
  Independently verified red (.venv run, 'fileno' error). Per register item
  (1) = NO TAR. Guard then landed (debug lane); independently re-verified:
  code guard present (try/except OSError/io.UnsupportedOperation) + 3 tests
  6/6 green incl. the 2 resume reds + faulthandler test. Marker file lags
  re-check (coordinator note) — direct verification is the evidence.
- r13 = r12 166 + tests/test_grpo_chunked_recompute_backward.py = 167 members.
  Changed: training/grpo_trainer.py (chunked-recompute backward + faulthandler
  guard), training/grpo_utils.py, scripts/asi2_launch_grpo_27b_selfeval.sh,
  scripts/sapo_status_snapshot.py, tests/test_asi3_sapo_launcher_readiness.py.
- Gates: closure CLOSURE OK (167), py3.9 0 hits, locks none, review/launchsim
  markers clear. member==manifest==tree verified (fresh build-time hashes).
- Deploy: 105x6000B chunks, 0 failures, audit clean (104x6000+4840); box sha
  ba72bfbd… == local, 471630 B both sides.
- Run tree refreshed; on box: GRPO_TRAINER IMPORT OK; faulthandler guard
  deployed (except clause present); both OOM-wave tests present.
- Launchsim signaled: /tmp/sapo_launchsim_r13_TRIGGER. Executor auto-relaunches
  on ITS rehearsal pass (gate IS the GO).
- NEXT CYCLE: freshness + lock + register + closure scans.

### r13 manifest (167 members, sha256)
85106d8e4c0c337edbc95eec2972d363c96f50f2d91c0d4404438dff386c4f27  configs/rl/qwen36_27b_fv_gspo_asi2.json
7b8bdc04fe2a6b41ba867facdebe04170bf7c864a2e09c2b446718764f060f18  evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt
18d8b065dd70c63dd55c3b4e6f229b2c741f77b39f8bd9ae409686aaa6b3ac65  evals/runner/candidate_sanitize.py
498c04c31b09dbd237d32f35839a2340b64e3da4420ab10467cd5a0962fb3336  evals/runner/candidate_security.py
4f149f9819df3c49ec57be9358a72463263343e17ddb3b648b7e13ac912ffa33  evals/runner/execute_run.py
8cdf777b630422df6bc3cd993353022b9719bc8df40657d058d6ab16b807c89b  evals/runner/frozen_contract.py
8216b8421947fe656731e0c26ff661bd341a3a7da977888babb27aa7d9d8831c  evals/runner/prepare_prompts.py
e26b9ade036c75993e4126acbe5f6e9b834c8e1173959226a3a78c9f25ab29af  evals/runner/public_task_spec.py
97b5186207302723f47281a4ed1e19e3406518537031dd243cdd162d24063093  evals/runner/run_eval.py
a181cd994245f51a605cb20f69ae17da2f2cf3a06c648d2bcf066beec5d0dbe4  evals/runner/seed_run_with_references.py
c4fa8bfa41c6edeecbb7816d3da3d7e6672772bafd4e2e4073047931ad350947  evals/runner/single_candidate_eval.py
618088bda4208f9ca8d84361ee4068b51cc36da67d82313e8a353846405d3076  evals/runner/task_metadata.py
0108c020f916b8dbf8ab16d08560d0057265ecaee0f5f37289620a7e0e8f0e54  evals/tasks/quantum/bell_pair_construction/candidate.py
9f6bf09c6019fb84748c9df10638291fd62bfcc90fa049642b980a1541b52403  evals/tasks/quantum/bell_pair_construction/tests.py
976677faa3f3138f9ac53c1435cbb8002ef380dabff6dc74f2f4fc4821620da1  evals/tasks/quantum/binary_measurement_decoder/task.json
114bd9cf91467960db9b629475aad730929625271b7ea76e453199b3b40b6690  evals/tasks/quantum/binary_measurement_decoder/tests.py
48d45ea9b46d7e54f23edbb62e94e7fb132884250506e342c460c7c9bba2d7db  evals/tasks/quantum/bitstring_maxcut_landscape/tests.py
4b4c0ea792f29454d0430a473cdaa778bc1432801c7f2c8c0d935520c89a29e5  evals/tasks/quantum/circuit_phase_repair/tests.py
6ee4de0769c7dd49dfa317d83035cc870c83020b9094cac23d5724f6f30fbdc6  evals/tasks/quantum/density_matrix_partial_trace/candidate.py
311688fed1cf708c6cbbe7854c724c422758526c1e6d13f12d1f1d1eb409e804  evals/tasks/quantum/error_detection_bit_flip/tests.py
18ed2cb56ee7c96529c53d65921deb4c44dcfdedce5d2bb275e36b714d59e6ae  evals/tasks/quantum/gate_alias_casefold_barrier/candidate.py
5feaa43a0f846f7d605e3b9ee6946ba4e4d53e61da07ed4ea7d40117218db661  evals/tasks/quantum/gate_alias_casefold_barrier/tests.py
f1cf1e1144aeef96acac9f527b6b3d96ea9c0c938121a48d9f2fc735599d9525  evals/tasks/quantum/gate_alias_normalization/task.json
4e17b821390f6916b8fd29d64061489a7bde5367a648b8227b26276a79b97143  evals/tasks/quantum/gate_alias_normalization/tests.py
fb4c96d30a8260ad6aa9895e3c2673d3dd7cc264d9f0958bfa0d9a163eb7760b  evals/tasks/quantum/gate_alias_registry_cleanup/candidate.py
d02d9e3673930d64c3dd1483d8ebf00c6b23764fa18fe542f16930313722100f  evals/tasks/quantum/gate_alias_registry_cleanup/tests.py
8cba17a29939f736e18e729a86fbbef83be4db9811890f2467dac666f805d931  evals/tasks/quantum/gate_token_canonicalizer/tests.py
7a6d4835c6cf027a323a720cd9698cf80560470c9c3aba7652965da3aeaac224  evals/tasks/quantum/ghz_state_witness/candidate.py
48db0b26936ba658f1f6e9bc61e416c07888d4cb5c17a1fbcd1bea8b4e30d464  evals/tasks/quantum/ghz_state_witness/tests.py
8b0496f1b2f2d671774a3ff5ae38bbd3a12764f64a187274b022eb1f0592a0e6  evals/tasks/quantum/grover_oracle_diffusion/candidate.py
eca1461b210a9e9244be9876e7c4cc2ae0648beb6eb167c59247987a2fcc922c  evals/tasks/quantum/grover_oracle_diffusion/tests.py
0b0ac2c05ac0ddbe685a4244e4e39fd315669e1cce18b3546496f3a65414a600  evals/tasks/quantum/maxcut_assignment_enumerator/tests.py
c2ca2881a761af3709496a1598360c4b545cc489822445e30cbd2e7afaf878e7  evals/tasks/quantum/maxcut_partition_ranker/candidate.py
23377a27912b10f10417748b130a25cefa7d84c08fe5f44e3ee49b21ec9da758  evals/tasks/quantum/maxcut_partition_ranker/tests.py
4d96a1e736f4b95157c39e7bba399786142ccd8f9889d49de4d5ef8e73af87a6  evals/tasks/quantum/measurement_bug_repair/tests.py
563553f63aa5bd957cc4e73e52cc787864567e1e479d3199300bda019962bf0b  evals/tasks/quantum/pauli_message_codec/tests.py
3cab7c4111f541c247ff98769efadb772b4f9ca7d9846ea13bce96d3d4137061  evals/tasks/quantum/pennylane_qml_iris_classification/task.json
8982efe7a2fdcde6fa723d77db797137a741508ebda8d2f4cc0610ebc25c4829  evals/tasks/quantum/pennylane_qml_iris_classification/tests.py
b8f8cd014abf677dd7f22e509043260db2e15ae2dc02f4bee0e6225bb44fd8b2  evals/tasks/quantum/pennylane_vqe_h2/candidate.py
18f1ff5d5dc2ee486e8a2f0faa6b2a00937cedbed8d967e7534b300eba93718e  evals/tasks/quantum/pennylane_vqe_h2/task.json
76a0106a456cea4652535dfe4ba9dadeac6825cae4ba3196e50e3a88ab4305b9  evals/tasks/quantum/pennylane_vqe_h2/tests.py
0ed7b78ecaaf776fbf8a0dc9e7709d58d17d4ea52c617b6ee3e164686fbd1121  evals/tasks/quantum/phase_estimation_circuit/candidate.py
9e4454a5be086d3484fe0f53fb63167e574baa04c9a632224bc25db34fd01fde  evals/tasks/quantum/phase_estimation_circuit/tests.py
06f85efba02647dc0c70e27450ece118df0ffc54d18d28df046ff319420547a9  evals/tasks/quantum/phase_measurement_register/tests.py
cef961ca651f7d14be1de207da598be883f1b3df1f1aadbec677c7f7ae724d8c  evals/tasks/quantum/phase_register_roundtrip/task.json
710ea354eb1d74d20d464f555428e2d78f77b1d0647cdfc6ab1543798335fe7c  evals/tasks/quantum/qaoa_maxcut/candidate.py
4bbfddd37158e6e2fc233b6feaeac391a929e0f34fcf6c4ce81f5ac9c1343e23  evals/tasks/quantum/qft_phase_pattern/candidate.py
ef7954bc50e7e39bd989a3d0feb0a6bea63b385aebc90c2d3d2215b9505b7b09  evals/tasks/quantum/qft_phase_pattern/tests.py
c7fdd0cdb37181a5d17ab9c2f9cbf2d7f41a877e45a58abed0bd89050cb280dd  evals/tasks/quantum/qiskit_qft_entangled/candidate.py
9847758ddba6fc2e70f1e6673787f0ab7ba3212dd218c4d003df54feec9dadac  evals/tasks/quantum/qiskit_qft_entangled/task.json
5fe817cf31b288e9ca3c1b481818a99a390498e15057f1da865fadcc1ecb169c  evals/tasks/quantum/qiskit_qft_entangled/tests.py
56828d0864714775e0c4d6bad5731e7fc1ba05d41bdb561c09030101a531612a  evals/tasks/quantum/quantum_bell_basis_discrimination/candidate.py
8ec6477bb5f1ad67655a1aad8120d4272f0e91eb11377958e17f83042ca1b764  evals/tasks/quantum/quantum_bell_basis_discrimination/task.json
0106c3e28e4406c38988bb6d99e253783e7b65194231471dd94623b6471caeaa  evals/tasks/quantum/quantum_bell_basis_discrimination/tests.py
a6dc2f09d5d1a26fa6a0a7c9bfee82f97277621c53e0cff451aa23148d2c53cc  evals/tasks/quantum/quantum_channel_depolarizing/candidate.py
e35912c10f0414dd665c50acf05ef5edd954aa2a7286177a8b50df8c8d5c207e  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/candidate.py
4b87bf5ec307d1fe6bbc2d06da8c31fe9102ca7dc36617075de3a309a9633784  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/task.json
16c446c9ff37b6000febfc411cfbb9b2afb966415473ac6d7aeeeb3d14019796  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/tests.py
704ae205c1689f1a422be5437f815d3f005cb3e6f9f18e14dce14108f0665bd2  evals/tasks/quantum/quantum_error_correction_shor_9qubit/candidate.py
53a4fca2a1d4bc50bbe1ae037365dfb4cb385867f86f17e43aac1826a49f942a  evals/tasks/quantum/quantum_qaoa_ring4_landscape/candidate.py
18c4c230851bea8b9a7c07e7e63a6c589a7aae0121c925c7464e9f5a169290a3  evals/tasks/quantum/quantum_qaoa_ring4_landscape/task.json
7b0edb9582b791f25e7f037ec2192e022a1aca156523c7a30b7e8b8323390ec0  evals/tasks/quantum/quantum_qaoa_ring4_landscape/tests.py
d120dacccc7a7e5275ae82e8fb51237633b30251f1b1630322d69a5c603ae8ab  evals/tasks/quantum/quantum_qft_periodic_state/candidate.py
ebd267d28641ee82b1ab3eb8cc1311a4404d9c2f4c396fc16e67f54d8f8b2590  evals/tasks/quantum/quantum_qft_periodic_state/task.json
1a5c67ea0d792acfb89b1f145a49f9e6a3b41ac1f5d01b2f2fcb794d67698b54  evals/tasks/quantum/quantum_qft_periodic_state/tests.py
da8a2df5ff111a370dce3dbc544fb0a94070e233d830e0209ae180196175c70a  evals/tasks/quantum/quantum_qml_variational_classifier/candidate.py
3797013aad4f4306494b05d6aaba2bcf58e9c0421399d98704c020004f8a15d7  evals/tasks/quantum/quantum_qml_variational_classifier/task.json
4ceb0643fe809c9d002605f18f949cbcc817ef46d73ee4d583fe6ab7ec99a814  evals/tasks/quantum/quantum_qml_variational_classifier/tests.py
cf077341049dda9bda626fea2988152c5578ed94019bf78f44b27a3004ce7494  evals/tasks/quantum/quantum_shor_phase_error_correction/candidate.py
924f62d00478418c0f8c050e9a5b1fa55d3dcc0c1ec33c2be275793849b99250  evals/tasks/quantum/quantum_shor_phase_error_correction/task.json
caa2f5ad530912bca05b7dc2fd653b545be269b4e2d04afb800316e27637a88d  evals/tasks/quantum/quantum_shor_phase_error_correction/tests.py
2fcbc2262b455b17fb03c676d706d815d17c00cfaeebb59f873860816a83beb4  evals/tasks/quantum/quantum_stabilizer_shor_generators/candidate.py
394cc88cf03ea9fa5455cbf6c5b70ee9322c303a64999ef730a0322765b12c5e  evals/tasks/quantum/quantum_stabilizer_shor_generators/task.json
4b624df712bace522ab885719fdf3c9d7f809a2ecf80332983302ce59c988714  evals/tasks/quantum/quantum_stabilizer_shor_generators/tests.py
94387663f339549e17e7140b689f21568c6aec325f998b43c7363a773d4f0e49  evals/tasks/quantum/quantum_three_qubit_entropy/candidate.py
b2b14d381a003e9b592ab7635309bb6dedf326cc4ee604f200862ee0e31a0216  evals/tasks/quantum/quantum_three_qubit_entropy/task.json
924589a11f316b781a2bcf859349605d26277616b50cd948d45858d67d53e160  evals/tasks/quantum/quantum_three_qubit_entropy/tests.py
4517812d3ba0b406e7d8c8bae538e6d8b98a2169315536e881e8d724567fb644  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/candidate.py
963bb4f6b79e121051a2d333653e000370aae6f3fc2cbf60b15039fc0204bb01  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/task.json
ea61dcafa29bff20cf30e0e9e5a3136f108849fdc60a66ff09ee00b3cadd0141  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/tests.py
20e155a60b412fa0567a163c6351b6ba1e65cd3aeb83aaca6c6d0faa3afe5f18  evals/tasks/quantum/quantum_vqe_heisenberg_energy/candidate.py
8509c851c68dff4c743dd3a7572579698ba9f382bb77f64bd7405dfdb49935fb  evals/tasks/quantum/quantum_vqe_heisenberg_energy/task.json
8a04b56c4c4ab367dc28bd579ad8a921fbca1ebc46270392fb9d89e5b32af16c  evals/tasks/quantum/quantum_vqe_heisenberg_energy/tests.py
7042529da93af3815df7941a9937a1476b1fd18d5571c0605acd617580b174f8  evals/tasks/quantum/stabilizer_tableau_update_repair/tests.py
e1bea2e227a012ae8b066f9cac0e3534a971b56a11270f3c40ca85d23d60a8cd  evals/tasks/quantum/superdense_coding/task.json
e3daa4ff10309b0044f6ed4fe5a707b6992fafcc180c30dd838af7bb906f9b7e  evals/tasks/quantum/superdense_identity_lookup/tests.py
fd6e10cad2e3c9c0d9176eefc5a165c2202b2c4ef97b3d513b64bfa922d3db59  evals/tasks/quantum/superdense_pauli_router/tests.py
dd4ff8fe03ad22e2d37a41683bd166ab787edc7f807dbef473babe54a0a96598  evals/tasks/quantum/teleportation_corrections/tests.py
c125239727ff913543e727979e7aa480341d99331b75f27324782c98793206c2  evals/tasks/quantum/vqe_energy_minimization/candidate.py
5f723b9e328abd5d08462d7dc0ccdb1c395eea31a89357c53e89ed07f16485a0  reports/sapo-holdout-enrichment-manifest-2026-08-24.json
ea5b263226494fa9a5831453e68c3f7a533ebfb2804e14094dc40d66fd890ff2  scripts/ai_launch_sapo_direct.sh
22b8784f4096f1a5e2589583aed560115d4941927f9838d65a635be0afbc507d  scripts/asi2_launch_grpo_27b_selfeval.sh
63158871a80cfe275d168c0519149b88abdb707bae69b7b5a6e5036fff1159a9  scripts/asi2_watchdog_relaunch.sh
8a0010e793f120aa6ba622a6f298e6869e748f66bbf47b61f550bc9e5df6e61a  scripts/asi3_launch_grpo_direct.sh
77bb097c26c6e3fbddb7911d92ed534f387eea7d1084b3da70efab32a9d3c94f  scripts/build_grpo_v8_manifest.py
5ab1acc36c0f1be0668634962a7583d22023119d68030d4dc6e23353fdb2bf0a  scripts/calibrate_model_judge.py
c07351d46a03ae1669f6d5430dee7b966b8dce80ae6e23390220d7b32d482903  scripts/decide_sapo_promotion_gate.py
d49aaeea2d1c25ff09df418ba594037e14a573554ed8d57d6a7f6afa7c944de6  scripts/eval_100_reeval.py
d97f9a7f7a018e4de774b59c3a0fb6e3622d03c61762f4cc5ba7f5abb1323fe8  scripts/eval_base_vs_adapter.py
766949e44a541db7ab9ddcdef50a5f9c60fcd53b66c992f80ed39e26197426c9  scripts/fine_score.py
94274f251f762a8c5d7d9c4e3bcdfd1d482551729b6ee032f55105a3985bcc3e  scripts/fv_gspo_repair_sidecar.sh
e35703662de7eeff9e2119c905f2da8f75c2a49e73ffd51833eda16750add759  scripts/report_base_adapter_comprehensive.py
2047b9a00169789ee8cbc851aeccd8e0de18805873a0022967b0886903cd2643  scripts/run_base_vs_adapter_eval.py
5c769d6c9626f1551a48e4db0478ec4cae299140d740dcaafe251ba67970f989  scripts/run_hf_pass1_eval.py
61c17c6529e12b9cc29ca2400618ea2112567c489508d2556e52607aec058a80  scripts/sapo_drift_watch.py
7a83b6c7d3ae2a3ccf11c19ca7ad1a2bde40ca8895d02a5455b0c1dd7a1fc048  scripts/sapo_math_audit_step_records.py
2eeea835761b1a3551ba7af517c2f19369ff20266310db4af1b4e9f2dfa1f95b  scripts/sapo_reward_audit.py
56472b5fc8592d828435f920a53a247e7a7300ba28b812a6b2f0095f505149de  scripts/sapo_status_snapshot.py
5607dbb49318f8f5106dad1eea253b23d65c7272da38999c21620e7f991319c5  scripts/serve_openai_chat_adapter.py
7890847631dc903c6e07574aac47cb71f2dbf3c952527420ef6e22c768313f83  scripts/submit_asi2_grpo_27b_selfeval_task.sh
670e7dba0dcffcdd89ed7219dcc26a1fae9c38498e2bedbd4c5cad3ecc1b8b25  tests/test_asi3_sapo_launcher_readiness.py
938e97eb8f5af240b2653088e14da876497e001ae5d06aec3f1d93a5ab733178  tests/test_compat.py
6354b5c4428627270d8a4b2da06aec2497f9880a307beedb57e81d4f19c612cc  tests/test_execute_run.py
84b85e3d743de62e286b2b2f185cb9982151b1652bb80b59673c29869edb23f0  tests/test_fine_score.py
58e6d6cae9f2d35cd73a588a97fc85166b160470ec1c167c76ee27945fd6f9e1  tests/test_grpo_chunked_recompute_backward.py
061137bcc408f24c9fd97d14bdb58fa04cb419cd2bdcc90cfc17218091010fde  tests/test_grpo_entropy_token_cap.py
98598a2a94576bfc42b0eb438cea588bce207202582167bdd8da800432a4975b  tests/test_grpo_rollout_mix_entropy_floor.py
a97649ef1227988886fd29ad7fd5388430ac66248de53927a20e1de0aa72f5ca  tests/test_grpo_train_pass_truncation.py
97ec2387c5be9dccab1feccf3460371bbaadd559d4deda6280fb65949eeac939  tests/test_grpo_trainer_breakers.py
495b873f619754772bc55ad51d11a327271fe3e1ddce9d610211e473074da7d7  tests/test_grpo_trainer_eval_results.py
2ac7da9b23c2f542ca3fc10a00f7225e327179ba66d50ef38a64f97fe0932f85  tests/test_grpo_trainer_faulthandler.py
083ff7cbf7cdd89d8b95c1ecfc041d78ce35b7e4b44a48763ef04fef8effb168  tests/test_grpo_trainer_generation_stop.py
d0b8f6442d93c8fecfed3bed62531253c991f33734b26dff94cf158f7caba3e1  tests/test_grpo_trainer_loss_stats_router.py
19b6cd0b8a628ec636ddca043b3de33de979883f19dfcbc9b6a6a6ea361e0902  tests/test_grpo_trainer_main_failclosed.py
528ef0e1ef2799862eb3977a5c0d53f37ed653954886b5116098b10c9eac033e  tests/test_grpo_trainer_metrics.py
15bb6ca5d7394cb4273f7060c3b2cb36c3b38991fdc8cf0757a7b3aa9b07104b  tests/test_grpo_trainer_resume.py
b57d191b4ada2b97ad276ab609de74d1cbc129016563aea16f6134384a3350b3  tests/test_grpo_trainer_self_eval.py
59330ffb5a28ababb0934deb6b1f6e2ab7982c705152c4bc1ae8087cff1b79bf  tests/test_grpo_trainer_sigterm.py
eb6b45cbdded0f936bdae02aa9e2fe3de22c6e4494071cb398436d49f2ca64a1  tests/test_grpo_utils.py
0f9d1b0f62e9c9a825061fd54c6ae1f71fd902733fb592a0beac82a0cd6df803  tests/test_holdout_enrichment_invariance.py
9a8c71d22816dab414376030a60c77a7f232af2217e86d255df788c023b58b75  tests/test_holdout_scorer_version_awareness.py
1bd8105aa4b1ab4d3eecf0dd151969a86cac4ac4ccaf0d205b7c7adfe4e37ff7  tests/test_model_family_support.py
1b587b54f3acdedd50b733558ac7dbf80ba96b2d75384aa1119808750e8165d7  tests/test_model_judge.py
6363e022f9c0d6a16200f385e9a5a845df5b0c93e66abcb9389c648fa4235a9c  tests/test_pennylane_vqe_h2_scorer_versions.py
caea3662eb1cb632fd4c7b881e0081b157cb7708325739e52a4f45dbbc5accdb  tests/test_prepare_prompts_coverage.py
f43b364994eb1dfcdceb7314127da94a7154d292907f9c781119b54dd5fa3824  tests/test_promotion_eval_adapter_merge.py
60437d05c8fefac612d5e48f7105fc31907ec45925acfec28d7f22f55262ce8f  tests/test_report_base_adapter_comprehensive.py
2bcdae7e8bc4407dd55d0be549b910c2305d80a4a9f7f3a8b59f7f58afa49c6d  tests/test_run_eval_scoring.py
7f37d88898c639d677eaeebd7c2a914f9710a6a71a9547cfa8956b16698a2b08  tests/test_sapo_curriculum_holdout_adjacent.py
f68e2261ab1cef28df4cef65aaaaa815c6306d129bb2f0d17cae31e7c3da15db  tests/test_sapo_drift_watch.py
2c5d5a901992ca5f7e0cec39e268d71b2d0f157e4add6851a551aeeaee8fb9f9  tests/test_sapo_eval_security.py
d79ae1884791178a1fd2902224055c3ba4939b531e4d28ba74ed18bd191e71f4  tests/test_sapo_loss.py
b7b4ad1b64e22d99c268d948583c00b419f6f0354d91e270d2146dab9ad94dbc  tests/test_sapo_promotion_pipeline_hardening.py
78dd512c92ada912fa7487792d81bdf7899bd07c6b0c5d77fc0fe4bae2e53127  tests/test_sapo_prompt_audit_cli.py
cceee5cb5733a2dd06f251b6c8544fe06972be02d1032da7d14301fac0a7dbf4  tests/test_sapo_reward_audit_cli.py
974ee9324b55b608509e337a6e7eac01d13651c5a8c66bf40f87e5d32155a4a2  tests/test_sapo_reward_audit.py
ff59d248dfba4ea7fbbfbf40061b482c614613e2573c7f9b184e69bb975a5f9b  tests/test_sapo_status_snapshot.py
81863a1a6fef400243d3f7fabc7da6742b765e2a15b9280d498e0733fad6d832  tests/test_seed_run_with_references.py
1daa2c7e60bc461c57bb02117cd627846441d08e20835dd8c710cfd4b4e5cb85  tests/test_single_candidate_eval.py
b81877e0f9168cdf1f11c54b6d06f9c224a879df8bf2cebe2722edf54098f58e  training/acquire_public_qwen_snapshot.py
f1c5d2511d18f16445acf86e738de6680dae768b2115bf8935869522f6d4e62e  training/audit_model_source.py
9f65ba9acabdfa09ac425a22c778c5480f8dee8b61494412504b7948a9d59be5  training/compat.py
a0839dcb2cc41de87a3b2171609ecc8930fd4cd95a772fe3784dce60dd76cc87  training/generation.py
e2d7023cdc43a518516a50a5decf62c52e056fc35f7ab1aa0d22dfcba126d025  training/grpo_trainer.py
ba8b0ec553d2ef2e12305c0ca49a21d4feebc23ad652d803685ecd8b8d2087e6  training/grpo_utils.py
4f24ff8bb7fd9058ff273971c0d2be5a66338eea75fde756a979fdc583c3b88a  training/huanxin_cpu_smoke.py
2b0dcb760f35449e68a921ac807229ffcff676ba8983b718efa35f09e421acfb  training/inspect_moe_target_modules.py
5eac8e4fa3f17106d9852f50bd50daf340bc7d72e4e918695e1b7ae5e0496e1b  training/model_backend.py
8887b0664c94cfec7ba5817868bc34835df26c607e9195e42a5f9bd7b8a32f5e  training/model_family_preflight.py
10b237931f9eed984af9db86307eb02212e59bf3125033eec54097a243965db2  training/quantum_verifiers.py
f69033af0f58e28e87e5399a5858da7ae9d775470b626bd21f9735771c0e6818  training/qwen_sft_peft.py
c3efeaff20d2ee0fba3bdf48b46259028906672fbde736671c16373c1677af9e  training/research_plugins.py
8a1132457a55687b195215abad027ee2c13051ae0907b092109540211e5feb73  training/runtime_overlay.py
1339972471e2aba8d95c420a9e9be2fb34cfeed5c2304c65435efa9578e23040  training/teacher_free_repair.py
2f8dfad36b8679e6ecc16d6f0fae9a1b6eea4230843e9c8b072bdb5b79eedda6  training/text_preprocessor_backend.py
dc619538b009e94bc22613256bc05b64a398a5af4d3e0f08d27923faa540e6cc  training/turboquant.py
e01b3e4050ff29184d0b630d6324bd368df984f1d531c19872bea1931394da46  training/verify_qwen_snapshot.py

## r14 DEPLOY — double-backward fix (2026-08-26 ~16:5x CST)
- Fix (debug lane): entropy-floor penalty value computed detached + penalty-first
  backward removed; each graph backpropped exactly once; TDD 2 tests incl. exact
  crash reproduction; 232 green; rehearsal passed with identity exact.
- tests_RED marker on disk is the STALE 15:11 file (faulthandler-era items,
  already resolved in r13). Independently re-verified this cycle: 10/10 green
  (.venv) = 2 resume tests + test_grpo_entropy_floor_backward_once + chunked
  recompute. Direct verification is the evidence (marker lag documented).
- r14 = r13 167 + tests/test_grpo_entropy_floor_backward_once.py = 168 members.
  Changed member: training/grpo_trainer.py (detached penalty :1000).
- Gates: closure CLOSURE OK (168), py3.9 0 hits, locks none, review/launchsim
  markers clear. member==manifest==tree (fresh build-time hashes).
- Deploy: 106x6000B chunks, 0 failures, audit clean (105x6000+1608); box sha
  b9c8b0b2… == local, 473705 B both sides.
- Run tree refreshed; on box: GRPO_TRAINER IMPORT OK; detached penalty :1000
  present; new test present (a183327e…).
- Rehearsal signaled: /tmp/sapo_launchsim_r14_TRIGGER. Executor auto-relaunches
  on ITS pass (gate IS the GO — the chain runs itself).
- NEXT CYCLE: freshness + lock + register + closure scans.

### r14 manifest (168 members, sha256)
85106d8e4c0c337edbc95eec2972d363c96f50f2d91c0d4404438dff386c4f27  configs/rl/qwen36_27b_fv_gspo_asi2.json
7b8bdc04fe2a6b41ba867facdebe04170bf7c864a2e09c2b446718764f060f18  evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt
18d8b065dd70c63dd55c3b4e6f229b2c741f77b39f8bd9ae409686aaa6b3ac65  evals/runner/candidate_sanitize.py
498c04c31b09dbd237d32f35839a2340b64e3da4420ab10467cd5a0962fb3336  evals/runner/candidate_security.py
4f149f9819df3c49ec57be9358a72463263343e17ddb3b648b7e13ac912ffa33  evals/runner/execute_run.py
8cdf777b630422df6bc3cd993353022b9719bc8df40657d058d6ab16b807c89b  evals/runner/frozen_contract.py
8216b8421947fe656731e0c26ff661bd341a3a7da977888babb27aa7d9d8831c  evals/runner/prepare_prompts.py
e26b9ade036c75993e4126acbe5f6e9b834c8e1173959226a3a78c9f25ab29af  evals/runner/public_task_spec.py
97b5186207302723f47281a4ed1e19e3406518537031dd243cdd162d24063093  evals/runner/run_eval.py
a181cd994245f51a605cb20f69ae17da2f2cf3a06c648d2bcf066beec5d0dbe4  evals/runner/seed_run_with_references.py
c4fa8bfa41c6edeecbb7816d3da3d7e6672772bafd4e2e4073047931ad350947  evals/runner/single_candidate_eval.py
618088bda4208f9ca8d84361ee4068b51cc36da67d82313e8a353846405d3076  evals/runner/task_metadata.py
0108c020f916b8dbf8ab16d08560d0057265ecaee0f5f37289620a7e0e8f0e54  evals/tasks/quantum/bell_pair_construction/candidate.py
9f6bf09c6019fb84748c9df10638291fd62bfcc90fa049642b980a1541b52403  evals/tasks/quantum/bell_pair_construction/tests.py
976677faa3f3138f9ac53c1435cbb8002ef380dabff6dc74f2f4fc4821620da1  evals/tasks/quantum/binary_measurement_decoder/task.json
114bd9cf91467960db9b629475aad730929625271b7ea76e453199b3b40b6690  evals/tasks/quantum/binary_measurement_decoder/tests.py
48d45ea9b46d7e54f23edbb62e94e7fb132884250506e342c460c7c9bba2d7db  evals/tasks/quantum/bitstring_maxcut_landscape/tests.py
4b4c0ea792f29454d0430a473cdaa778bc1432801c7f2c8c0d935520c89a29e5  evals/tasks/quantum/circuit_phase_repair/tests.py
6ee4de0769c7dd49dfa317d83035cc870c83020b9094cac23d5724f6f30fbdc6  evals/tasks/quantum/density_matrix_partial_trace/candidate.py
311688fed1cf708c6cbbe7854c724c422758526c1e6d13f12d1f1d1eb409e804  evals/tasks/quantum/error_detection_bit_flip/tests.py
18ed2cb56ee7c96529c53d65921deb4c44dcfdedce5d2bb275e36b714d59e6ae  evals/tasks/quantum/gate_alias_casefold_barrier/candidate.py
5feaa43a0f846f7d605e3b9ee6946ba4e4d53e61da07ed4ea7d40117218db661  evals/tasks/quantum/gate_alias_casefold_barrier/tests.py
f1cf1e1144aeef96acac9f527b6b3d96ea9c0c938121a48d9f2fc735599d9525  evals/tasks/quantum/gate_alias_normalization/task.json
4e17b821390f6916b8fd29d64061489a7bde5367a648b8227b26276a79b97143  evals/tasks/quantum/gate_alias_normalization/tests.py
fb4c96d30a8260ad6aa9895e3c2673d3dd7cc264d9f0958bfa0d9a163eb7760b  evals/tasks/quantum/gate_alias_registry_cleanup/candidate.py
d02d9e3673930d64c3dd1483d8ebf00c6b23764fa18fe542f16930313722100f  evals/tasks/quantum/gate_alias_registry_cleanup/tests.py
8cba17a29939f736e18e729a86fbbef83be4db9811890f2467dac666f805d931  evals/tasks/quantum/gate_token_canonicalizer/tests.py
7a6d4835c6cf027a323a720cd9698cf80560470c9c3aba7652965da3aeaac224  evals/tasks/quantum/ghz_state_witness/candidate.py
48db0b26936ba658f1f6e9bc61e416c07888d4cb5c17a1fbcd1bea8b4e30d464  evals/tasks/quantum/ghz_state_witness/tests.py
8b0496f1b2f2d671774a3ff5ae38bbd3a12764f64a187274b022eb1f0592a0e6  evals/tasks/quantum/grover_oracle_diffusion/candidate.py
eca1461b210a9e9244be9876e7c4cc2ae0648beb6eb167c59247987a2fcc922c  evals/tasks/quantum/grover_oracle_diffusion/tests.py
0b0ac2c05ac0ddbe685a4244e4e39fd315669e1cce18b3546496f3a65414a600  evals/tasks/quantum/maxcut_assignment_enumerator/tests.py
c2ca2881a761af3709496a1598360c4b545cc489822445e30cbd2e7afaf878e7  evals/tasks/quantum/maxcut_partition_ranker/candidate.py
23377a27912b10f10417748b130a25cefa7d84c08fe5f44e3ee49b21ec9da758  evals/tasks/quantum/maxcut_partition_ranker/tests.py
4d96a1e736f4b95157c39e7bba399786142ccd8f9889d49de4d5ef8e73af87a6  evals/tasks/quantum/measurement_bug_repair/tests.py
563553f63aa5bd957cc4e73e52cc787864567e1e479d3199300bda019962bf0b  evals/tasks/quantum/pauli_message_codec/tests.py
3cab7c4111f541c247ff98769efadb772b4f9ca7d9846ea13bce96d3d4137061  evals/tasks/quantum/pennylane_qml_iris_classification/task.json
8982efe7a2fdcde6fa723d77db797137a741508ebda8d2f4cc0610ebc25c4829  evals/tasks/quantum/pennylane_qml_iris_classification/tests.py
b8f8cd014abf677dd7f22e509043260db2e15ae2dc02f4bee0e6225bb44fd8b2  evals/tasks/quantum/pennylane_vqe_h2/candidate.py
18f1ff5d5dc2ee486e8a2f0faa6b2a00937cedbed8d967e7534b300eba93718e  evals/tasks/quantum/pennylane_vqe_h2/task.json
76a0106a456cea4652535dfe4ba9dadeac6825cae4ba3196e50e3a88ab4305b9  evals/tasks/quantum/pennylane_vqe_h2/tests.py
0ed7b78ecaaf776fbf8a0dc9e7709d58d17d4ea52c617b6ee3e164686fbd1121  evals/tasks/quantum/phase_estimation_circuit/candidate.py
9e4454a5be086d3484fe0f53fb63167e574baa04c9a632224bc25db34fd01fde  evals/tasks/quantum/phase_estimation_circuit/tests.py
06f85efba02647dc0c70e27450ece118df0ffc54d18d28df046ff319420547a9  evals/tasks/quantum/phase_measurement_register/tests.py
cef961ca651f7d14be1de207da598be883f1b3df1f1aadbec677c7f7ae724d8c  evals/tasks/quantum/phase_register_roundtrip/task.json
710ea354eb1d74d20d464f555428e2d78f77b1d0647cdfc6ab1543798335fe7c  evals/tasks/quantum/qaoa_maxcut/candidate.py
4bbfddd37158e6e2fc233b6feaeac391a929e0f34fcf6c4ce81f5ac9c1343e23  evals/tasks/quantum/qft_phase_pattern/candidate.py
ef7954bc50e7e39bd989a3d0feb0a6bea63b385aebc90c2d3d2215b9505b7b09  evals/tasks/quantum/qft_phase_pattern/tests.py
c7fdd0cdb37181a5d17ab9c2f9cbf2d7f41a877e45a58abed0bd89050cb280dd  evals/tasks/quantum/qiskit_qft_entangled/candidate.py
9847758ddba6fc2e70f1e6673787f0ab7ba3212dd218c4d003df54feec9dadac  evals/tasks/quantum/qiskit_qft_entangled/task.json
5fe817cf31b288e9ca3c1b481818a99a390498e15057f1da865fadcc1ecb169c  evals/tasks/quantum/qiskit_qft_entangled/tests.py
56828d0864714775e0c4d6bad5731e7fc1ba05d41bdb561c09030101a531612a  evals/tasks/quantum/quantum_bell_basis_discrimination/candidate.py
8ec6477bb5f1ad67655a1aad8120d4272f0e91eb11377958e17f83042ca1b764  evals/tasks/quantum/quantum_bell_basis_discrimination/task.json
0106c3e28e4406c38988bb6d99e253783e7b65194231471dd94623b6471caeaa  evals/tasks/quantum/quantum_bell_basis_discrimination/tests.py
a6dc2f09d5d1a26fa6a0a7c9bfee82f97277621c53e0cff451aa23148d2c53cc  evals/tasks/quantum/quantum_channel_depolarizing/candidate.py
e35912c10f0414dd665c50acf05ef5edd954aa2a7286177a8b50df8c8d5c207e  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/candidate.py
4b87bf5ec307d1fe6bbc2d06da8c31fe9102ca7dc36617075de3a309a9633784  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/task.json
16c446c9ff37b6000febfc411cfbb9b2afb966415473ac6d7aeeeb3d14019796  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/tests.py
704ae205c1689f1a422be5437f815d3f005cb3e6f9f18e14dce14108f0665bd2  evals/tasks/quantum/quantum_error_correction_shor_9qubit/candidate.py
53a4fca2a1d4bc50bbe1ae037365dfb4cb385867f86f17e43aac1826a49f942a  evals/tasks/quantum/quantum_qaoa_ring4_landscape/candidate.py
18c4c230851bea8b9a7c07e7e63a6c589a7aae0121c925c7464e9f5a169290a3  evals/tasks/quantum/quantum_qaoa_ring4_landscape/task.json
7b0edb9582b791f25e7f037ec2192e022a1aca156523c7a30b7e8b8323390ec0  evals/tasks/quantum/quantum_qaoa_ring4_landscape/tests.py
d120dacccc7a7e5275ae82e8fb51237633b30251f1b1630322d69a5c603ae8ab  evals/tasks/quantum/quantum_qft_periodic_state/candidate.py
ebd267d28641ee82b1ab3eb8cc1311a4404d9c2f4c396fc16e67f54d8f8b2590  evals/tasks/quantum/quantum_qft_periodic_state/task.json
1a5c67ea0d792acfb89b1f145a49f9e6a3b41ac1f5d01b2f2fcb794d67698b54  evals/tasks/quantum/quantum_qft_periodic_state/tests.py
da8a2df5ff111a370dce3dbc544fb0a94070e233d830e0209ae180196175c70a  evals/tasks/quantum/quantum_qml_variational_classifier/candidate.py
3797013aad4f4306494b05d6aaba2bcf58e9c0421399d98704c020004f8a15d7  evals/tasks/quantum/quantum_qml_variational_classifier/task.json
4ceb0643fe809c9d002605f18f949cbcc817ef46d73ee4d583fe6ab7ec99a814  evals/tasks/quantum/quantum_qml_variational_classifier/tests.py
cf077341049dda9bda626fea2988152c5578ed94019bf78f44b27a3004ce7494  evals/tasks/quantum/quantum_shor_phase_error_correction/candidate.py
924f62d00478418c0f8c050e9a5b1fa55d3dcc0c1ec33c2be275793849b99250  evals/tasks/quantum/quantum_shor_phase_error_correction/task.json
caa2f5ad530912bca05b7dc2fd653b545be269b4e2d04afb800316e27637a88d  evals/tasks/quantum/quantum_shor_phase_error_correction/tests.py
2fcbc2262b455b17fb03c676d706d815d17c00cfaeebb59f873860816a83beb4  evals/tasks/quantum/quantum_stabilizer_shor_generators/candidate.py
394cc88cf03ea9fa5455cbf6c5b70ee9322c303a64999ef730a0322765b12c5e  evals/tasks/quantum/quantum_stabilizer_shor_generators/task.json
4b624df712bace522ab885719fdf3c9d7f809a2ecf80332983302ce59c988714  evals/tasks/quantum/quantum_stabilizer_shor_generators/tests.py
94387663f339549e17e7140b689f21568c6aec325f998b43c7363a773d4f0e49  evals/tasks/quantum/quantum_three_qubit_entropy/candidate.py
b2b14d381a003e9b592ab7635309bb6dedf326cc4ee604f200862ee0e31a0216  evals/tasks/quantum/quantum_three_qubit_entropy/task.json
924589a11f316b781a2bcf859349605d26277616b50cd948d45858d67d53e160  evals/tasks/quantum/quantum_three_qubit_entropy/tests.py
4517812d3ba0b406e7d8c8bae538e6d8b98a2169315536e881e8d724567fb644  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/candidate.py
963bb4f6b79e121051a2d333653e000370aae6f3fc2cbf60b15039fc0204bb01  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/task.json
ea61dcafa29bff20cf30e0e9e5a3136f108849fdc60a66ff09ee00b3cadd0141  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/tests.py
20e155a60b412fa0567a163c6351b6ba1e65cd3aeb83aaca6c6d0faa3afe5f18  evals/tasks/quantum/quantum_vqe_heisenberg_energy/candidate.py
8509c851c68dff4c743dd3a7572579698ba9f382bb77f64bd7405dfdb49935fb  evals/tasks/quantum/quantum_vqe_heisenberg_energy/task.json
8a04b56c4c4ab367dc28bd579ad8a921fbca1ebc46270392fb9d89e5b32af16c  evals/tasks/quantum/quantum_vqe_heisenberg_energy/tests.py
7042529da93af3815df7941a9937a1476b1fd18d5571c0605acd617580b174f8  evals/tasks/quantum/stabilizer_tableau_update_repair/tests.py
e1bea2e227a012ae8b066f9cac0e3534a971b56a11270f3c40ca85d23d60a8cd  evals/tasks/quantum/superdense_coding/task.json
e3daa4ff10309b0044f6ed4fe5a707b6992fafcc180c30dd838af7bb906f9b7e  evals/tasks/quantum/superdense_identity_lookup/tests.py
fd6e10cad2e3c9c0d9176eefc5a165c2202b2c4ef97b3d513b64bfa922d3db59  evals/tasks/quantum/superdense_pauli_router/tests.py
dd4ff8fe03ad22e2d37a41683bd166ab787edc7f807dbef473babe54a0a96598  evals/tasks/quantum/teleportation_corrections/tests.py
c125239727ff913543e727979e7aa480341d99331b75f27324782c98793206c2  evals/tasks/quantum/vqe_energy_minimization/candidate.py
5f723b9e328abd5d08462d7dc0ccdb1c395eea31a89357c53e89ed07f16485a0  reports/sapo-holdout-enrichment-manifest-2026-08-24.json
ea5b263226494fa9a5831453e68c3f7a533ebfb2804e14094dc40d66fd890ff2  scripts/ai_launch_sapo_direct.sh
22b8784f4096f1a5e2589583aed560115d4941927f9838d65a635be0afbc507d  scripts/asi2_launch_grpo_27b_selfeval.sh
63158871a80cfe275d168c0519149b88abdb707bae69b7b5a6e5036fff1159a9  scripts/asi2_watchdog_relaunch.sh
8a0010e793f120aa6ba622a6f298e6869e748f66bbf47b61f550bc9e5df6e61a  scripts/asi3_launch_grpo_direct.sh
77bb097c26c6e3fbddb7911d92ed534f387eea7d1084b3da70efab32a9d3c94f  scripts/build_grpo_v8_manifest.py
5ab1acc36c0f1be0668634962a7583d22023119d68030d4dc6e23353fdb2bf0a  scripts/calibrate_model_judge.py
c07351d46a03ae1669f6d5430dee7b966b8dce80ae6e23390220d7b32d482903  scripts/decide_sapo_promotion_gate.py
d49aaeea2d1c25ff09df418ba594037e14a573554ed8d57d6a7f6afa7c944de6  scripts/eval_100_reeval.py
d97f9a7f7a018e4de774b59c3a0fb6e3622d03c61762f4cc5ba7f5abb1323fe8  scripts/eval_base_vs_adapter.py
766949e44a541db7ab9ddcdef50a5f9c60fcd53b66c992f80ed39e26197426c9  scripts/fine_score.py
94274f251f762a8c5d7d9c4e3bcdfd1d482551729b6ee032f55105a3985bcc3e  scripts/fv_gspo_repair_sidecar.sh
e35703662de7eeff9e2119c905f2da8f75c2a49e73ffd51833eda16750add759  scripts/report_base_adapter_comprehensive.py
2047b9a00169789ee8cbc851aeccd8e0de18805873a0022967b0886903cd2643  scripts/run_base_vs_adapter_eval.py
5c769d6c9626f1551a48e4db0478ec4cae299140d740dcaafe251ba67970f989  scripts/run_hf_pass1_eval.py
61c17c6529e12b9cc29ca2400618ea2112567c489508d2556e52607aec058a80  scripts/sapo_drift_watch.py
7a83b6c7d3ae2a3ccf11c19ca7ad1a2bde40ca8895d02a5455b0c1dd7a1fc048  scripts/sapo_math_audit_step_records.py
2eeea835761b1a3551ba7af517c2f19369ff20266310db4af1b4e9f2dfa1f95b  scripts/sapo_reward_audit.py
56472b5fc8592d828435f920a53a247e7a7300ba28b812a6b2f0095f505149de  scripts/sapo_status_snapshot.py
5607dbb49318f8f5106dad1eea253b23d65c7272da38999c21620e7f991319c5  scripts/serve_openai_chat_adapter.py
7890847631dc903c6e07574aac47cb71f2dbf3c952527420ef6e22c768313f83  scripts/submit_asi2_grpo_27b_selfeval_task.sh
670e7dba0dcffcdd89ed7219dcc26a1fae9c38498e2bedbd4c5cad3ecc1b8b25  tests/test_asi3_sapo_launcher_readiness.py
938e97eb8f5af240b2653088e14da876497e001ae5d06aec3f1d93a5ab733178  tests/test_compat.py
6354b5c4428627270d8a4b2da06aec2497f9880a307beedb57e81d4f19c612cc  tests/test_execute_run.py
84b85e3d743de62e286b2b2f185cb9982151b1652bb80b59673c29869edb23f0  tests/test_fine_score.py
58e6d6cae9f2d35cd73a588a97fc85166b160470ec1c167c76ee27945fd6f9e1  tests/test_grpo_chunked_recompute_backward.py
a183327eb29a33bf74eab69b4e5e5b7a1789bf5de37c751c769df5d9f2b91c2c  tests/test_grpo_entropy_floor_backward_once.py
061137bcc408f24c9fd97d14bdb58fa04cb419cd2bdcc90cfc17218091010fde  tests/test_grpo_entropy_token_cap.py
98598a2a94576bfc42b0eb438cea588bce207202582167bdd8da800432a4975b  tests/test_grpo_rollout_mix_entropy_floor.py
a97649ef1227988886fd29ad7fd5388430ac66248de53927a20e1de0aa72f5ca  tests/test_grpo_train_pass_truncation.py
97ec2387c5be9dccab1feccf3460371bbaadd559d4deda6280fb65949eeac939  tests/test_grpo_trainer_breakers.py
495b873f619754772bc55ad51d11a327271fe3e1ddce9d610211e473074da7d7  tests/test_grpo_trainer_eval_results.py
2ac7da9b23c2f542ca3fc10a00f7225e327179ba66d50ef38a64f97fe0932f85  tests/test_grpo_trainer_faulthandler.py
083ff7cbf7cdd89d8b95c1ecfc041d78ce35b7e4b44a48763ef04fef8effb168  tests/test_grpo_trainer_generation_stop.py
d0b8f6442d93c8fecfed3bed62531253c991f33734b26dff94cf158f7caba3e1  tests/test_grpo_trainer_loss_stats_router.py
19b6cd0b8a628ec636ddca043b3de33de979883f19dfcbc9b6a6a6ea361e0902  tests/test_grpo_trainer_main_failclosed.py
528ef0e1ef2799862eb3977a5c0d53f37ed653954886b5116098b10c9eac033e  tests/test_grpo_trainer_metrics.py
15bb6ca5d7394cb4273f7060c3b2cb36c3b38991fdc8cf0757a7b3aa9b07104b  tests/test_grpo_trainer_resume.py
b57d191b4ada2b97ad276ab609de74d1cbc129016563aea16f6134384a3350b3  tests/test_grpo_trainer_self_eval.py
59330ffb5a28ababb0934deb6b1f6e2ab7982c705152c4bc1ae8087cff1b79bf  tests/test_grpo_trainer_sigterm.py
eb6b45cbdded0f936bdae02aa9e2fe3de22c6e4494071cb398436d49f2ca64a1  tests/test_grpo_utils.py
0f9d1b0f62e9c9a825061fd54c6ae1f71fd902733fb592a0beac82a0cd6df803  tests/test_holdout_enrichment_invariance.py
9a8c71d22816dab414376030a60c77a7f232af2217e86d255df788c023b58b75  tests/test_holdout_scorer_version_awareness.py
1bd8105aa4b1ab4d3eecf0dd151969a86cac4ac4ccaf0d205b7c7adfe4e37ff7  tests/test_model_family_support.py
1b587b54f3acdedd50b733558ac7dbf80ba96b2d75384aa1119808750e8165d7  tests/test_model_judge.py
6363e022f9c0d6a16200f385e9a5a845df5b0c93e66abcb9389c648fa4235a9c  tests/test_pennylane_vqe_h2_scorer_versions.py
caea3662eb1cb632fd4c7b881e0081b157cb7708325739e52a4f45dbbc5accdb  tests/test_prepare_prompts_coverage.py
f43b364994eb1dfcdceb7314127da94a7154d292907f9c781119b54dd5fa3824  tests/test_promotion_eval_adapter_merge.py
60437d05c8fefac612d5e48f7105fc31907ec45925acfec28d7f22f55262ce8f  tests/test_report_base_adapter_comprehensive.py
2bcdae7e8bc4407dd55d0be549b910c2305d80a4a9f7f3a8b59f7f58afa49c6d  tests/test_run_eval_scoring.py
7f37d88898c639d677eaeebd7c2a914f9710a6a71a9547cfa8956b16698a2b08  tests/test_sapo_curriculum_holdout_adjacent.py
f68e2261ab1cef28df4cef65aaaaa815c6306d129bb2f0d17cae31e7c3da15db  tests/test_sapo_drift_watch.py
2c5d5a901992ca5f7e0cec39e268d71b2d0f157e4add6851a551aeeaee8fb9f9  tests/test_sapo_eval_security.py
d79ae1884791178a1fd2902224055c3ba4939b531e4d28ba74ed18bd191e71f4  tests/test_sapo_loss.py
b7b4ad1b64e22d99c268d948583c00b419f6f0354d91e270d2146dab9ad94dbc  tests/test_sapo_promotion_pipeline_hardening.py
78dd512c92ada912fa7487792d81bdf7899bd07c6b0c5d77fc0fe4bae2e53127  tests/test_sapo_prompt_audit_cli.py
cceee5cb5733a2dd06f251b6c8544fe06972be02d1032da7d14301fac0a7dbf4  tests/test_sapo_reward_audit_cli.py
974ee9324b55b608509e337a6e7eac01d13651c5a8c66bf40f87e5d32155a4a2  tests/test_sapo_reward_audit.py
ff59d248dfba4ea7fbbfbf40061b482c614613e2573c7f9b184e69bb975a5f9b  tests/test_sapo_status_snapshot.py
81863a1a6fef400243d3f7fabc7da6742b765e2a15b9280d498e0733fad6d832  tests/test_seed_run_with_references.py
1daa2c7e60bc461c57bb02117cd627846441d08e20835dd8c710cfd4b4e5cb85  tests/test_single_candidate_eval.py
b81877e0f9168cdf1f11c54b6d06f9c224a879df8bf2cebe2722edf54098f58e  training/acquire_public_qwen_snapshot.py
f1c5d2511d18f16445acf86e738de6680dae768b2115bf8935869522f6d4e62e  training/audit_model_source.py
9f65ba9acabdfa09ac425a22c778c5480f8dee8b61494412504b7948a9d59be5  training/compat.py
a0839dcb2cc41de87a3b2171609ecc8930fd4cd95a772fe3784dce60dd76cc87  training/generation.py
530a4efd4f9fce371cb211f6d1ddfeb65f9fc143223f7ba7b79a9f2e2c074e0b  training/grpo_trainer.py
ba8b0ec553d2ef2e12305c0ca49a21d4feebc23ad652d803685ecd8b8d2087e6  training/grpo_utils.py
4f24ff8bb7fd9058ff273971c0d2be5a66338eea75fde756a979fdc583c3b88a  training/huanxin_cpu_smoke.py
2b0dcb760f35449e68a921ac807229ffcff676ba8983b718efa35f09e421acfb  training/inspect_moe_target_modules.py
5eac8e4fa3f17106d9852f50bd50daf340bc7d72e4e918695e1b7ae5e0496e1b  training/model_backend.py
8887b0664c94cfec7ba5817868bc34835df26c607e9195e42a5f9bd7b8a32f5e  training/model_family_preflight.py
10b237931f9eed984af9db86307eb02212e59bf3125033eec54097a243965db2  training/quantum_verifiers.py
f69033af0f58e28e87e5399a5858da7ae9d775470b626bd21f9735771c0e6818  training/qwen_sft_peft.py
c3efeaff20d2ee0fba3bdf48b46259028906672fbde736671c16373c1677af9e  training/research_plugins.py
8a1132457a55687b195215abad027ee2c13051ae0907b092109540211e5feb73  training/runtime_overlay.py
1339972471e2aba8d95c420a9e9be2fb34cfeed5c2304c65435efa9578e23040  training/teacher_free_repair.py
2f8dfad36b8679e6ecc16d6f0fae9a1b6eea4230843e9c8b072bdb5b79eedda6  training/text_preprocessor_backend.py
dc619538b009e94bc22613256bc05b64a398a5af4d3e0f08d27923faa540e6cc  training/turboquant.py
e01b3e4050ff29184d0b630d6324bd368df984f1d531c19872bea1931394da46  training/verify_qwen_snapshot.py

## r15 DEPLOY — F5 double-add fix (2026-08-26 ~17:1x-17:4x CST)
- LAUNCHSIM r14 BLOCK (17:05): F5 — SAPO-mode entropy-floor penalty double-count
  (loss = recomputed + 2*penalty): SAPO branch :5251 adds penalty + unguarded
  common-tail :5367 adds again. Impact: inflated loss exactly during collapse
  episodes + math-auditor false alarms. Backward math unaffected (run-10 fix
  real — launchsim verified).
- r15 fix (debug lane, in tree + verified by this lane): testable helper
  add_entropy_floor_penalty_value (grpo_trainer.py:1006, guard loss_mode !=
  "sapo" at :1018) + common-tail guard at :5440. F5 regression tests 4/4
  venv-green (re-ran). Coordinator: 122 green; re-smoke floor-engaged exact-once
  in sapo AND gspo.
- r15 = r14 168 members (no new files); changed: training/grpo_trainer.py,
  tests/test_grpo_entropy_floor_backward_once.py.
- Gates: closure CLOSURE OK (168), py3.9 0 hits, locks none, review marker
  clear. member==manifest==tree (fresh build-time hashes).
- Deploy: 106x6000B chunks, 0 failures, audit clean (105x6000+2612); box sha
  74576ab9… == local, 474457 B both sides.
- Run tree refreshed; on box: GRPO_TRAINER IMPORT OK; guard at :1018 + :5440;
  manifest hashes match (grpo_trainer 21fe8174…, test fd69ac72…).
- Re-smoke signaled: /tmp/sapo_launchsim_r15_TRIGGER (floor engaged, exact-once
  identity in sapo AND gspo per launchsim's own requested procedure). Launchsim
  clears its BLOCK on pass; Executor auto-relaunches then.
- NEXT CYCLE: freshness + lock + register + closure scans.

### r15 manifest (168 members, sha256)
85106d8e4c0c337edbc95eec2972d363c96f50f2d91c0d4404438dff386c4f27  configs/rl/qwen36_27b_fv_gspo_asi2.json
7b8bdc04fe2a6b41ba867facdebe04170bf7c864a2e09c2b446718764f060f18  evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt
18d8b065dd70c63dd55c3b4e6f229b2c741f77b39f8bd9ae409686aaa6b3ac65  evals/runner/candidate_sanitize.py
498c04c31b09dbd237d32f35839a2340b64e3da4420ab10467cd5a0962fb3336  evals/runner/candidate_security.py
4f149f9819df3c49ec57be9358a72463263343e17ddb3b648b7e13ac912ffa33  evals/runner/execute_run.py
8cdf777b630422df6bc3cd993353022b9719bc8df40657d058d6ab16b807c89b  evals/runner/frozen_contract.py
8216b8421947fe656731e0c26ff661bd341a3a7da977888babb27aa7d9d8831c  evals/runner/prepare_prompts.py
e26b9ade036c75993e4126acbe5f6e9b834c8e1173959226a3a78c9f25ab29af  evals/runner/public_task_spec.py
97b5186207302723f47281a4ed1e19e3406518537031dd243cdd162d24063093  evals/runner/run_eval.py
a181cd994245f51a605cb20f69ae17da2f2cf3a06c648d2bcf066beec5d0dbe4  evals/runner/seed_run_with_references.py
c4fa8bfa41c6edeecbb7816d3da3d7e6672772bafd4e2e4073047931ad350947  evals/runner/single_candidate_eval.py
618088bda4208f9ca8d84361ee4068b51cc36da67d82313e8a353846405d3076  evals/runner/task_metadata.py
0108c020f916b8dbf8ab16d08560d0057265ecaee0f5f37289620a7e0e8f0e54  evals/tasks/quantum/bell_pair_construction/candidate.py
9f6bf09c6019fb84748c9df10638291fd62bfcc90fa049642b980a1541b52403  evals/tasks/quantum/bell_pair_construction/tests.py
976677faa3f3138f9ac53c1435cbb8002ef380dabff6dc74f2f4fc4821620da1  evals/tasks/quantum/binary_measurement_decoder/task.json
114bd9cf91467960db9b629475aad730929625271b7ea76e453199b3b40b6690  evals/tasks/quantum/binary_measurement_decoder/tests.py
48d45ea9b46d7e54f23edbb62e94e7fb132884250506e342c460c7c9bba2d7db  evals/tasks/quantum/bitstring_maxcut_landscape/tests.py
4b4c0ea792f29454d0430a473cdaa778bc1432801c7f2c8c0d935520c89a29e5  evals/tasks/quantum/circuit_phase_repair/tests.py
6ee4de0769c7dd49dfa317d83035cc870c83020b9094cac23d5724f6f30fbdc6  evals/tasks/quantum/density_matrix_partial_trace/candidate.py
311688fed1cf708c6cbbe7854c724c422758526c1e6d13f12d1f1d1eb409e804  evals/tasks/quantum/error_detection_bit_flip/tests.py
18ed2cb56ee7c96529c53d65921deb4c44dcfdedce5d2bb275e36b714d59e6ae  evals/tasks/quantum/gate_alias_casefold_barrier/candidate.py
5feaa43a0f846f7d605e3b9ee6946ba4e4d53e61da07ed4ea7d40117218db661  evals/tasks/quantum/gate_alias_casefold_barrier/tests.py
f1cf1e1144aeef96acac9f527b6b3d96ea9c0c938121a48d9f2fc735599d9525  evals/tasks/quantum/gate_alias_normalization/task.json
4e17b821390f6916b8fd29d64061489a7bde5367a648b8227b26276a79b97143  evals/tasks/quantum/gate_alias_normalization/tests.py
fb4c96d30a8260ad6aa9895e3c2673d3dd7cc264d9f0958bfa0d9a163eb7760b  evals/tasks/quantum/gate_alias_registry_cleanup/candidate.py
d02d9e3673930d64c3dd1483d8ebf00c6b23764fa18fe542f16930313722100f  evals/tasks/quantum/gate_alias_registry_cleanup/tests.py
8cba17a29939f736e18e729a86fbbef83be4db9811890f2467dac666f805d931  evals/tasks/quantum/gate_token_canonicalizer/tests.py
7a6d4835c6cf027a323a720cd9698cf80560470c9c3aba7652965da3aeaac224  evals/tasks/quantum/ghz_state_witness/candidate.py
48db0b26936ba658f1f6e9bc61e416c07888d4cb5c17a1fbcd1bea8b4e30d464  evals/tasks/quantum/ghz_state_witness/tests.py
8b0496f1b2f2d671774a3ff5ae38bbd3a12764f64a187274b022eb1f0592a0e6  evals/tasks/quantum/grover_oracle_diffusion/candidate.py
eca1461b210a9e9244be9876e7c4cc2ae0648beb6eb167c59247987a2fcc922c  evals/tasks/quantum/grover_oracle_diffusion/tests.py
0b0ac2c05ac0ddbe685a4244e4e39fd315669e1cce18b3546496f3a65414a600  evals/tasks/quantum/maxcut_assignment_enumerator/tests.py
c2ca2881a761af3709496a1598360c4b545cc489822445e30cbd2e7afaf878e7  evals/tasks/quantum/maxcut_partition_ranker/candidate.py
23377a27912b10f10417748b130a25cefa7d84c08fe5f44e3ee49b21ec9da758  evals/tasks/quantum/maxcut_partition_ranker/tests.py
4d96a1e736f4b95157c39e7bba399786142ccd8f9889d49de4d5ef8e73af87a6  evals/tasks/quantum/measurement_bug_repair/tests.py
563553f63aa5bd957cc4e73e52cc787864567e1e479d3199300bda019962bf0b  evals/tasks/quantum/pauli_message_codec/tests.py
3cab7c4111f541c247ff98769efadb772b4f9ca7d9846ea13bce96d3d4137061  evals/tasks/quantum/pennylane_qml_iris_classification/task.json
8982efe7a2fdcde6fa723d77db797137a741508ebda8d2f4cc0610ebc25c4829  evals/tasks/quantum/pennylane_qml_iris_classification/tests.py
b8f8cd014abf677dd7f22e509043260db2e15ae2dc02f4bee0e6225bb44fd8b2  evals/tasks/quantum/pennylane_vqe_h2/candidate.py
18f1ff5d5dc2ee486e8a2f0faa6b2a00937cedbed8d967e7534b300eba93718e  evals/tasks/quantum/pennylane_vqe_h2/task.json
76a0106a456cea4652535dfe4ba9dadeac6825cae4ba3196e50e3a88ab4305b9  evals/tasks/quantum/pennylane_vqe_h2/tests.py
0ed7b78ecaaf776fbf8a0dc9e7709d58d17d4ea52c617b6ee3e164686fbd1121  evals/tasks/quantum/phase_estimation_circuit/candidate.py
9e4454a5be086d3484fe0f53fb63167e574baa04c9a632224bc25db34fd01fde  evals/tasks/quantum/phase_estimation_circuit/tests.py
06f85efba02647dc0c70e27450ece118df0ffc54d18d28df046ff319420547a9  evals/tasks/quantum/phase_measurement_register/tests.py
cef961ca651f7d14be1de207da598be883f1b3df1f1aadbec677c7f7ae724d8c  evals/tasks/quantum/phase_register_roundtrip/task.json
710ea354eb1d74d20d464f555428e2d78f77b1d0647cdfc6ab1543798335fe7c  evals/tasks/quantum/qaoa_maxcut/candidate.py
4bbfddd37158e6e2fc233b6feaeac391a929e0f34fcf6c4ce81f5ac9c1343e23  evals/tasks/quantum/qft_phase_pattern/candidate.py
ef7954bc50e7e39bd989a3d0feb0a6bea63b385aebc90c2d3d2215b9505b7b09  evals/tasks/quantum/qft_phase_pattern/tests.py
c7fdd0cdb37181a5d17ab9c2f9cbf2d7f41a877e45a58abed0bd89050cb280dd  evals/tasks/quantum/qiskit_qft_entangled/candidate.py
9847758ddba6fc2e70f1e6673787f0ab7ba3212dd218c4d003df54feec9dadac  evals/tasks/quantum/qiskit_qft_entangled/task.json
5fe817cf31b288e9ca3c1b481818a99a390498e15057f1da865fadcc1ecb169c  evals/tasks/quantum/qiskit_qft_entangled/tests.py
56828d0864714775e0c4d6bad5731e7fc1ba05d41bdb561c09030101a531612a  evals/tasks/quantum/quantum_bell_basis_discrimination/candidate.py
8ec6477bb5f1ad67655a1aad8120d4272f0e91eb11377958e17f83042ca1b764  evals/tasks/quantum/quantum_bell_basis_discrimination/task.json
0106c3e28e4406c38988bb6d99e253783e7b65194231471dd94623b6471caeaa  evals/tasks/quantum/quantum_bell_basis_discrimination/tests.py
a6dc2f09d5d1a26fa6a0a7c9bfee82f97277621c53e0cff451aa23148d2c53cc  evals/tasks/quantum/quantum_channel_depolarizing/candidate.py
e35912c10f0414dd665c50acf05ef5edd954aa2a7286177a8b50df8c8d5c207e  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/candidate.py
4b87bf5ec307d1fe6bbc2d06da8c31fe9102ca7dc36617075de3a309a9633784  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/task.json
16c446c9ff37b6000febfc411cfbb9b2afb966415473ac6d7aeeeb3d14019796  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/tests.py
704ae205c1689f1a422be5437f815d3f005cb3e6f9f18e14dce14108f0665bd2  evals/tasks/quantum/quantum_error_correction_shor_9qubit/candidate.py
53a4fca2a1d4bc50bbe1ae037365dfb4cb385867f86f17e43aac1826a49f942a  evals/tasks/quantum/quantum_qaoa_ring4_landscape/candidate.py
18c4c230851bea8b9a7c07e7e63a6c589a7aae0121c925c7464e9f5a169290a3  evals/tasks/quantum/quantum_qaoa_ring4_landscape/task.json
7b0edb9582b791f25e7f037ec2192e022a1aca156523c7a30b7e8b8323390ec0  evals/tasks/quantum/quantum_qaoa_ring4_landscape/tests.py
d120dacccc7a7e5275ae82e8fb51237633b30251f1b1630322d69a5c603ae8ab  evals/tasks/quantum/quantum_qft_periodic_state/candidate.py
ebd267d28641ee82b1ab3eb8cc1311a4404d9c2f4c396fc16e67f54d8f8b2590  evals/tasks/quantum/quantum_qft_periodic_state/task.json
1a5c67ea0d792acfb89b1f145a49f9e6a3b41ac1f5d01b2f2fcb794d67698b54  evals/tasks/quantum/quantum_qft_periodic_state/tests.py
da8a2df5ff111a370dce3dbc544fb0a94070e233d830e0209ae180196175c70a  evals/tasks/quantum/quantum_qml_variational_classifier/candidate.py
3797013aad4f4306494b05d6aaba2bcf58e9c0421399d98704c020004f8a15d7  evals/tasks/quantum/quantum_qml_variational_classifier/task.json
4ceb0643fe809c9d002605f18f949cbcc817ef46d73ee4d583fe6ab7ec99a814  evals/tasks/quantum/quantum_qml_variational_classifier/tests.py
cf077341049dda9bda626fea2988152c5578ed94019bf78f44b27a3004ce7494  evals/tasks/quantum/quantum_shor_phase_error_correction/candidate.py
924f62d00478418c0f8c050e9a5b1fa55d3dcc0c1ec33c2be275793849b99250  evals/tasks/quantum/quantum_shor_phase_error_correction/task.json
caa2f5ad530912bca05b7dc2fd653b545be269b4e2d04afb800316e27637a88d  evals/tasks/quantum/quantum_shor_phase_error_correction/tests.py
2fcbc2262b455b17fb03c676d706d815d17c00cfaeebb59f873860816a83beb4  evals/tasks/quantum/quantum_stabilizer_shor_generators/candidate.py
394cc88cf03ea9fa5455cbf6c5b70ee9322c303a64999ef730a0322765b12c5e  evals/tasks/quantum/quantum_stabilizer_shor_generators/task.json
4b624df712bace522ab885719fdf3c9d7f809a2ecf80332983302ce59c988714  evals/tasks/quantum/quantum_stabilizer_shor_generators/tests.py
94387663f339549e17e7140b689f21568c6aec325f998b43c7363a773d4f0e49  evals/tasks/quantum/quantum_three_qubit_entropy/candidate.py
b2b14d381a003e9b592ab7635309bb6dedf326cc4ee604f200862ee0e31a0216  evals/tasks/quantum/quantum_three_qubit_entropy/task.json
924589a11f316b781a2bcf859349605d26277616b50cd948d45858d67d53e160  evals/tasks/quantum/quantum_three_qubit_entropy/tests.py
4517812d3ba0b406e7d8c8bae538e6d8b98a2169315536e881e8d724567fb644  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/candidate.py
963bb4f6b79e121051a2d333653e000370aae6f3fc2cbf60b15039fc0204bb01  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/task.json
ea61dcafa29bff20cf30e0e9e5a3136f108849fdc60a66ff09ee00b3cadd0141  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/tests.py
20e155a60b412fa0567a163c6351b6ba1e65cd3aeb83aaca6c6d0faa3afe5f18  evals/tasks/quantum/quantum_vqe_heisenberg_energy/candidate.py
8509c851c68dff4c743dd3a7572579698ba9f382bb77f64bd7405dfdb49935fb  evals/tasks/quantum/quantum_vqe_heisenberg_energy/task.json
8a04b56c4c4ab367dc28bd579ad8a921fbca1ebc46270392fb9d89e5b32af16c  evals/tasks/quantum/quantum_vqe_heisenberg_energy/tests.py
7042529da93af3815df7941a9937a1476b1fd18d5571c0605acd617580b174f8  evals/tasks/quantum/stabilizer_tableau_update_repair/tests.py
e1bea2e227a012ae8b066f9cac0e3534a971b56a11270f3c40ca85d23d60a8cd  evals/tasks/quantum/superdense_coding/task.json
e3daa4ff10309b0044f6ed4fe5a707b6992fafcc180c30dd838af7bb906f9b7e  evals/tasks/quantum/superdense_identity_lookup/tests.py
fd6e10cad2e3c9c0d9176eefc5a165c2202b2c4ef97b3d513b64bfa922d3db59  evals/tasks/quantum/superdense_pauli_router/tests.py
dd4ff8fe03ad22e2d37a41683bd166ab787edc7f807dbef473babe54a0a96598  evals/tasks/quantum/teleportation_corrections/tests.py
c125239727ff913543e727979e7aa480341d99331b75f27324782c98793206c2  evals/tasks/quantum/vqe_energy_minimization/candidate.py
5f723b9e328abd5d08462d7dc0ccdb1c395eea31a89357c53e89ed07f16485a0  reports/sapo-holdout-enrichment-manifest-2026-08-24.json
ea5b263226494fa9a5831453e68c3f7a533ebfb2804e14094dc40d66fd890ff2  scripts/ai_launch_sapo_direct.sh
22b8784f4096f1a5e2589583aed560115d4941927f9838d65a635be0afbc507d  scripts/asi2_launch_grpo_27b_selfeval.sh
63158871a80cfe275d168c0519149b88abdb707bae69b7b5a6e5036fff1159a9  scripts/asi2_watchdog_relaunch.sh
8a0010e793f120aa6ba622a6f298e6869e748f66bbf47b61f550bc9e5df6e61a  scripts/asi3_launch_grpo_direct.sh
77bb097c26c6e3fbddb7911d92ed534f387eea7d1084b3da70efab32a9d3c94f  scripts/build_grpo_v8_manifest.py
5ab1acc36c0f1be0668634962a7583d22023119d68030d4dc6e23353fdb2bf0a  scripts/calibrate_model_judge.py
c07351d46a03ae1669f6d5430dee7b966b8dce80ae6e23390220d7b32d482903  scripts/decide_sapo_promotion_gate.py
d49aaeea2d1c25ff09df418ba594037e14a573554ed8d57d6a7f6afa7c944de6  scripts/eval_100_reeval.py
d97f9a7f7a018e4de774b59c3a0fb6e3622d03c61762f4cc5ba7f5abb1323fe8  scripts/eval_base_vs_adapter.py
766949e44a541db7ab9ddcdef50a5f9c60fcd53b66c992f80ed39e26197426c9  scripts/fine_score.py
94274f251f762a8c5d7d9c4e3bcdfd1d482551729b6ee032f55105a3985bcc3e  scripts/fv_gspo_repair_sidecar.sh
e35703662de7eeff9e2119c905f2da8f75c2a49e73ffd51833eda16750add759  scripts/report_base_adapter_comprehensive.py
2047b9a00169789ee8cbc851aeccd8e0de18805873a0022967b0886903cd2643  scripts/run_base_vs_adapter_eval.py
5c769d6c9626f1551a48e4db0478ec4cae299140d740dcaafe251ba67970f989  scripts/run_hf_pass1_eval.py
61c17c6529e12b9cc29ca2400618ea2112567c489508d2556e52607aec058a80  scripts/sapo_drift_watch.py
7a83b6c7d3ae2a3ccf11c19ca7ad1a2bde40ca8895d02a5455b0c1dd7a1fc048  scripts/sapo_math_audit_step_records.py
2eeea835761b1a3551ba7af517c2f19369ff20266310db4af1b4e9f2dfa1f95b  scripts/sapo_reward_audit.py
56472b5fc8592d828435f920a53a247e7a7300ba28b812a6b2f0095f505149de  scripts/sapo_status_snapshot.py
5607dbb49318f8f5106dad1eea253b23d65c7272da38999c21620e7f991319c5  scripts/serve_openai_chat_adapter.py
7890847631dc903c6e07574aac47cb71f2dbf3c952527420ef6e22c768313f83  scripts/submit_asi2_grpo_27b_selfeval_task.sh
670e7dba0dcffcdd89ed7219dcc26a1fae9c38498e2bedbd4c5cad3ecc1b8b25  tests/test_asi3_sapo_launcher_readiness.py
938e97eb8f5af240b2653088e14da876497e001ae5d06aec3f1d93a5ab733178  tests/test_compat.py
6354b5c4428627270d8a4b2da06aec2497f9880a307beedb57e81d4f19c612cc  tests/test_execute_run.py
84b85e3d743de62e286b2b2f185cb9982151b1652bb80b59673c29869edb23f0  tests/test_fine_score.py
58e6d6cae9f2d35cd73a588a97fc85166b160470ec1c167c76ee27945fd6f9e1  tests/test_grpo_chunked_recompute_backward.py
fd69ac72580ab6ae21d9e8f41f7a4f9b7a2d0c82e1b99454cad89a1712b3bc3f  tests/test_grpo_entropy_floor_backward_once.py
061137bcc408f24c9fd97d14bdb58fa04cb419cd2bdcc90cfc17218091010fde  tests/test_grpo_entropy_token_cap.py
98598a2a94576bfc42b0eb438cea588bce207202582167bdd8da800432a4975b  tests/test_grpo_rollout_mix_entropy_floor.py
a97649ef1227988886fd29ad7fd5388430ac66248de53927a20e1de0aa72f5ca  tests/test_grpo_train_pass_truncation.py
97ec2387c5be9dccab1feccf3460371bbaadd559d4deda6280fb65949eeac939  tests/test_grpo_trainer_breakers.py
495b873f619754772bc55ad51d11a327271fe3e1ddce9d610211e473074da7d7  tests/test_grpo_trainer_eval_results.py
2ac7da9b23c2f542ca3fc10a00f7225e327179ba66d50ef38a64f97fe0932f85  tests/test_grpo_trainer_faulthandler.py
083ff7cbf7cdd89d8b95c1ecfc041d78ce35b7e4b44a48763ef04fef8effb168  tests/test_grpo_trainer_generation_stop.py
d0b8f6442d93c8fecfed3bed62531253c991f33734b26dff94cf158f7caba3e1  tests/test_grpo_trainer_loss_stats_router.py
19b6cd0b8a628ec636ddca043b3de33de979883f19dfcbc9b6a6a6ea361e0902  tests/test_grpo_trainer_main_failclosed.py
528ef0e1ef2799862eb3977a5c0d53f37ed653954886b5116098b10c9eac033e  tests/test_grpo_trainer_metrics.py
15bb6ca5d7394cb4273f7060c3b2cb36c3b38991fdc8cf0757a7b3aa9b07104b  tests/test_grpo_trainer_resume.py
b57d191b4ada2b97ad276ab609de74d1cbc129016563aea16f6134384a3350b3  tests/test_grpo_trainer_self_eval.py
59330ffb5a28ababb0934deb6b1f6e2ab7982c705152c4bc1ae8087cff1b79bf  tests/test_grpo_trainer_sigterm.py
eb6b45cbdded0f936bdae02aa9e2fe3de22c6e4494071cb398436d49f2ca64a1  tests/test_grpo_utils.py
0f9d1b0f62e9c9a825061fd54c6ae1f71fd902733fb592a0beac82a0cd6df803  tests/test_holdout_enrichment_invariance.py
9a8c71d22816dab414376030a60c77a7f232af2217e86d255df788c023b58b75  tests/test_holdout_scorer_version_awareness.py
1bd8105aa4b1ab4d3eecf0dd151969a86cac4ac4ccaf0d205b7c7adfe4e37ff7  tests/test_model_family_support.py
1b587b54f3acdedd50b733558ac7dbf80ba96b2d75384aa1119808750e8165d7  tests/test_model_judge.py
6363e022f9c0d6a16200f385e9a5a845df5b0c93e66abcb9389c648fa4235a9c  tests/test_pennylane_vqe_h2_scorer_versions.py
caea3662eb1cb632fd4c7b881e0081b157cb7708325739e52a4f45dbbc5accdb  tests/test_prepare_prompts_coverage.py
f43b364994eb1dfcdceb7314127da94a7154d292907f9c781119b54dd5fa3824  tests/test_promotion_eval_adapter_merge.py
60437d05c8fefac612d5e48f7105fc31907ec45925acfec28d7f22f55262ce8f  tests/test_report_base_adapter_comprehensive.py
2bcdae7e8bc4407dd55d0be549b910c2305d80a4a9f7f3a8b59f7f58afa49c6d  tests/test_run_eval_scoring.py
7f37d88898c639d677eaeebd7c2a914f9710a6a71a9547cfa8956b16698a2b08  tests/test_sapo_curriculum_holdout_adjacent.py
f68e2261ab1cef28df4cef65aaaaa815c6306d129bb2f0d17cae31e7c3da15db  tests/test_sapo_drift_watch.py
2c5d5a901992ca5f7e0cec39e268d71b2d0f157e4add6851a551aeeaee8fb9f9  tests/test_sapo_eval_security.py
d79ae1884791178a1fd2902224055c3ba4939b531e4d28ba74ed18bd191e71f4  tests/test_sapo_loss.py
b7b4ad1b64e22d99c268d948583c00b419f6f0354d91e270d2146dab9ad94dbc  tests/test_sapo_promotion_pipeline_hardening.py
78dd512c92ada912fa7487792d81bdf7899bd07c6b0c5d77fc0fe4bae2e53127  tests/test_sapo_prompt_audit_cli.py
cceee5cb5733a2dd06f251b6c8544fe06972be02d1032da7d14301fac0a7dbf4  tests/test_sapo_reward_audit_cli.py
974ee9324b55b608509e337a6e7eac01d13651c5a8c66bf40f87e5d32155a4a2  tests/test_sapo_reward_audit.py
ff59d248dfba4ea7fbbfbf40061b482c614613e2573c7f9b184e69bb975a5f9b  tests/test_sapo_status_snapshot.py
81863a1a6fef400243d3f7fabc7da6742b765e2a15b9280d498e0733fad6d832  tests/test_seed_run_with_references.py
1daa2c7e60bc461c57bb02117cd627846441d08e20835dd8c710cfd4b4e5cb85  tests/test_single_candidate_eval.py
b81877e0f9168cdf1f11c54b6d06f9c224a879df8bf2cebe2722edf54098f58e  training/acquire_public_qwen_snapshot.py
f1c5d2511d18f16445acf86e738de6680dae768b2115bf8935869522f6d4e62e  training/audit_model_source.py
9f65ba9acabdfa09ac425a22c778c5480f8dee8b61494412504b7948a9d59be5  training/compat.py
a0839dcb2cc41de87a3b2171609ecc8930fd4cd95a772fe3784dce60dd76cc87  training/generation.py
21fe81743f25464fbce9e599d52a235ff2449643af99d3d73007e49503d04dab  training/grpo_trainer.py
ba8b0ec553d2ef2e12305c0ca49a21d4feebc23ad652d803685ecd8b8d2087e6  training/grpo_utils.py
4f24ff8bb7fd9058ff273971c0d2be5a66338eea75fde756a979fdc583c3b88a  training/huanxin_cpu_smoke.py
2b0dcb760f35449e68a921ac807229ffcff676ba8983b718efa35f09e421acfb  training/inspect_moe_target_modules.py
5eac8e4fa3f17106d9852f50bd50daf340bc7d72e4e918695e1b7ae5e0496e1b  training/model_backend.py
8887b0664c94cfec7ba5817868bc34835df26c607e9195e42a5f9bd7b8a32f5e  training/model_family_preflight.py
10b237931f9eed984af9db86307eb02212e59bf3125033eec54097a243965db2  training/quantum_verifiers.py
f69033af0f58e28e87e5399a5858da7ae9d775470b626bd21f9735771c0e6818  training/qwen_sft_peft.py
c3efeaff20d2ee0fba3bdf48b46259028906672fbde736671c16373c1677af9e  training/research_plugins.py
8a1132457a55687b195215abad027ee2c13051ae0907b092109540211e5feb73  training/runtime_overlay.py
1339972471e2aba8d95c420a9e9be2fb34cfeed5c2304c65435efa9578e23040  training/teacher_free_repair.py
2f8dfad36b8679e6ecc16d6f0fae9a1b6eea4230843e9c8b072bdb5b79eedda6  training/text_preprocessor_backend.py
dc619538b009e94bc22613256bc05b64a398a5af4d3e0f08d27923faa540e6cc  training/turboquant.py
e01b3e4050ff29184d0b630d6324bd368df984f1d531c19872bea1931394da46  training/verify_qwen_snapshot.py

## r16 DEPLOY — JUDGE WAVE (2026-08-26 ~19:1x-19:2x CST)
- Launchsim r15 re-smoke PASSED (its r14 F5 BLOCK cleared — /tmp/sapo_launchsim_BLOCK
  gone this cycle; exact-once identity confirmed with floor engaged).
- Judge wave (rollout lane): judge path never ran before (tokenizer-call blocker —
  now tested); judge = FROZEN BASE model sharing the training model (no second 27B
  load); EOS backstop + cache releases (memory wall dead); 0.40/0.35/0.25 blend;
  verifier contract updated; launch flags wired + echo-verified (ai_launch_sapo_direct.sh
  exports AI_SAPO_MODEL_JUDGE_ENABLED/PATH + AI_SAPO_REWARD_MODE); 16 new TDD tests;
  322/322 green; E2E verified. Deploywatch re-ran judge-wave suite: 16/16 green.
- r16 = r15 168 + tests/test_grpo_judge_wave.py = 169 members. Changed: grpo_trainer.py,
  grpo_utils.py, ai_launch_sapo_direct.sh, asi2_launch_grpo_27b_selfeval.sh,
  asi3_launch_grpo_direct.sh, sapo_reward_audit.py.
- Gates: closure CLOSURE OK (169), py3.9 0 hits, locks none, review/launchsim markers
  clear. member==manifest==tree (fresh build-time hashes).
- Deploy: 108x6000B chunks, 0 failures, audit clean (107x6000+524); box sha
  456317a7… == local, 481892 B both sides.
- Run tree refreshed; on box: GRPO_TRAINER IMPORT OK; judge wiring present
  (AI_SAPO_MODEL_JUDGE x2 in ai_launch_sapo_direct.sh); manifest hashes match
  (grpo_trainer 3e9c40c0…, grpo_utils 18f0ffa8…, ai_launch 3a956eb6…, judge test e4bbe699…).
- Rehearsal signaled: /tmp/sapo_launchsim_r16_TRIGGER — battery MUST include a
  judge-inference step (frozen judge engaged, verify judge scores in step records,
  no second load, memory wall dead). Executor auto-relaunches on its pass with
  AI_SAPO_MODEL_JUDGE_ENABLED=1 AI_SAPO_MODEL_JUDGE_PATH=/root/work/filestorage/Qwen3.6-27B
  AI_SAPO_REWARD_MODE=comprehensive.
- NEXT CYCLE: freshness + lock + register + closure scans.

### r16 manifest (169 members, sha256)
85106d8e4c0c337edbc95eec2972d363c96f50f2d91c0d4404438dff386c4f27  configs/rl/qwen36_27b_fv_gspo_asi2.json
7b8bdc04fe2a6b41ba867facdebe04170bf7c864a2e09c2b446718764f060f18  evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt
18d8b065dd70c63dd55c3b4e6f229b2c741f77b39f8bd9ae409686aaa6b3ac65  evals/runner/candidate_sanitize.py
498c04c31b09dbd237d32f35839a2340b64e3da4420ab10467cd5a0962fb3336  evals/runner/candidate_security.py
4f149f9819df3c49ec57be9358a72463263343e17ddb3b648b7e13ac912ffa33  evals/runner/execute_run.py
8cdf777b630422df6bc3cd993353022b9719bc8df40657d058d6ab16b807c89b  evals/runner/frozen_contract.py
8216b8421947fe656731e0c26ff661bd341a3a7da977888babb27aa7d9d8831c  evals/runner/prepare_prompts.py
e26b9ade036c75993e4126acbe5f6e9b834c8e1173959226a3a78c9f25ab29af  evals/runner/public_task_spec.py
97b5186207302723f47281a4ed1e19e3406518537031dd243cdd162d24063093  evals/runner/run_eval.py
a181cd994245f51a605cb20f69ae17da2f2cf3a06c648d2bcf066beec5d0dbe4  evals/runner/seed_run_with_references.py
c4fa8bfa41c6edeecbb7816d3da3d7e6672772bafd4e2e4073047931ad350947  evals/runner/single_candidate_eval.py
618088bda4208f9ca8d84361ee4068b51cc36da67d82313e8a353846405d3076  evals/runner/task_metadata.py
0108c020f916b8dbf8ab16d08560d0057265ecaee0f5f37289620a7e0e8f0e54  evals/tasks/quantum/bell_pair_construction/candidate.py
9f6bf09c6019fb84748c9df10638291fd62bfcc90fa049642b980a1541b52403  evals/tasks/quantum/bell_pair_construction/tests.py
976677faa3f3138f9ac53c1435cbb8002ef380dabff6dc74f2f4fc4821620da1  evals/tasks/quantum/binary_measurement_decoder/task.json
114bd9cf91467960db9b629475aad730929625271b7ea76e453199b3b40b6690  evals/tasks/quantum/binary_measurement_decoder/tests.py
48d45ea9b46d7e54f23edbb62e94e7fb132884250506e342c460c7c9bba2d7db  evals/tasks/quantum/bitstring_maxcut_landscape/tests.py
4b4c0ea792f29454d0430a473cdaa778bc1432801c7f2c8c0d935520c89a29e5  evals/tasks/quantum/circuit_phase_repair/tests.py
6ee4de0769c7dd49dfa317d83035cc870c83020b9094cac23d5724f6f30fbdc6  evals/tasks/quantum/density_matrix_partial_trace/candidate.py
311688fed1cf708c6cbbe7854c724c422758526c1e6d13f12d1f1d1eb409e804  evals/tasks/quantum/error_detection_bit_flip/tests.py
18ed2cb56ee7c96529c53d65921deb4c44dcfdedce5d2bb275e36b714d59e6ae  evals/tasks/quantum/gate_alias_casefold_barrier/candidate.py
5feaa43a0f846f7d605e3b9ee6946ba4e4d53e61da07ed4ea7d40117218db661  evals/tasks/quantum/gate_alias_casefold_barrier/tests.py
f1cf1e1144aeef96acac9f527b6b3d96ea9c0c938121a48d9f2fc735599d9525  evals/tasks/quantum/gate_alias_normalization/task.json
4e17b821390f6916b8fd29d64061489a7bde5367a648b8227b26276a79b97143  evals/tasks/quantum/gate_alias_normalization/tests.py
fb4c96d30a8260ad6aa9895e3c2673d3dd7cc264d9f0958bfa0d9a163eb7760b  evals/tasks/quantum/gate_alias_registry_cleanup/candidate.py
d02d9e3673930d64c3dd1483d8ebf00c6b23764fa18fe542f16930313722100f  evals/tasks/quantum/gate_alias_registry_cleanup/tests.py
8cba17a29939f736e18e729a86fbbef83be4db9811890f2467dac666f805d931  evals/tasks/quantum/gate_token_canonicalizer/tests.py
7a6d4835c6cf027a323a720cd9698cf80560470c9c3aba7652965da3aeaac224  evals/tasks/quantum/ghz_state_witness/candidate.py
48db0b26936ba658f1f6e9bc61e416c07888d4cb5c17a1fbcd1bea8b4e30d464  evals/tasks/quantum/ghz_state_witness/tests.py
8b0496f1b2f2d671774a3ff5ae38bbd3a12764f64a187274b022eb1f0592a0e6  evals/tasks/quantum/grover_oracle_diffusion/candidate.py
eca1461b210a9e9244be9876e7c4cc2ae0648beb6eb167c59247987a2fcc922c  evals/tasks/quantum/grover_oracle_diffusion/tests.py
0b0ac2c05ac0ddbe685a4244e4e39fd315669e1cce18b3546496f3a65414a600  evals/tasks/quantum/maxcut_assignment_enumerator/tests.py
c2ca2881a761af3709496a1598360c4b545cc489822445e30cbd2e7afaf878e7  evals/tasks/quantum/maxcut_partition_ranker/candidate.py
23377a27912b10f10417748b130a25cefa7d84c08fe5f44e3ee49b21ec9da758  evals/tasks/quantum/maxcut_partition_ranker/tests.py
4d96a1e736f4b95157c39e7bba399786142ccd8f9889d49de4d5ef8e73af87a6  evals/tasks/quantum/measurement_bug_repair/tests.py
563553f63aa5bd957cc4e73e52cc787864567e1e479d3199300bda019962bf0b  evals/tasks/quantum/pauli_message_codec/tests.py
3cab7c4111f541c247ff98769efadb772b4f9ca7d9846ea13bce96d3d4137061  evals/tasks/quantum/pennylane_qml_iris_classification/task.json
8982efe7a2fdcde6fa723d77db797137a741508ebda8d2f4cc0610ebc25c4829  evals/tasks/quantum/pennylane_qml_iris_classification/tests.py
b8f8cd014abf677dd7f22e509043260db2e15ae2dc02f4bee0e6225bb44fd8b2  evals/tasks/quantum/pennylane_vqe_h2/candidate.py
18f1ff5d5dc2ee486e8a2f0faa6b2a00937cedbed8d967e7534b300eba93718e  evals/tasks/quantum/pennylane_vqe_h2/task.json
76a0106a456cea4652535dfe4ba9dadeac6825cae4ba3196e50e3a88ab4305b9  evals/tasks/quantum/pennylane_vqe_h2/tests.py
0ed7b78ecaaf776fbf8a0dc9e7709d58d17d4ea52c617b6ee3e164686fbd1121  evals/tasks/quantum/phase_estimation_circuit/candidate.py
9e4454a5be086d3484fe0f53fb63167e574baa04c9a632224bc25db34fd01fde  evals/tasks/quantum/phase_estimation_circuit/tests.py
06f85efba02647dc0c70e27450ece118df0ffc54d18d28df046ff319420547a9  evals/tasks/quantum/phase_measurement_register/tests.py
cef961ca651f7d14be1de207da598be883f1b3df1f1aadbec677c7f7ae724d8c  evals/tasks/quantum/phase_register_roundtrip/task.json
710ea354eb1d74d20d464f555428e2d78f77b1d0647cdfc6ab1543798335fe7c  evals/tasks/quantum/qaoa_maxcut/candidate.py
4bbfddd37158e6e2fc233b6feaeac391a929e0f34fcf6c4ce81f5ac9c1343e23  evals/tasks/quantum/qft_phase_pattern/candidate.py
ef7954bc50e7e39bd989a3d0feb0a6bea63b385aebc90c2d3d2215b9505b7b09  evals/tasks/quantum/qft_phase_pattern/tests.py
c7fdd0cdb37181a5d17ab9c2f9cbf2d7f41a877e45a58abed0bd89050cb280dd  evals/tasks/quantum/qiskit_qft_entangled/candidate.py
9847758ddba6fc2e70f1e6673787f0ab7ba3212dd218c4d003df54feec9dadac  evals/tasks/quantum/qiskit_qft_entangled/task.json
5fe817cf31b288e9ca3c1b481818a99a390498e15057f1da865fadcc1ecb169c  evals/tasks/quantum/qiskit_qft_entangled/tests.py
56828d0864714775e0c4d6bad5731e7fc1ba05d41bdb561c09030101a531612a  evals/tasks/quantum/quantum_bell_basis_discrimination/candidate.py
8ec6477bb5f1ad67655a1aad8120d4272f0e91eb11377958e17f83042ca1b764  evals/tasks/quantum/quantum_bell_basis_discrimination/task.json
0106c3e28e4406c38988bb6d99e253783e7b65194231471dd94623b6471caeaa  evals/tasks/quantum/quantum_bell_basis_discrimination/tests.py
a6dc2f09d5d1a26fa6a0a7c9bfee82f97277621c53e0cff451aa23148d2c53cc  evals/tasks/quantum/quantum_channel_depolarizing/candidate.py
e35912c10f0414dd665c50acf05ef5edd954aa2a7286177a8b50df8c8d5c207e  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/candidate.py
4b87bf5ec307d1fe6bbc2d06da8c31fe9102ca7dc36617075de3a309a9633784  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/task.json
16c446c9ff37b6000febfc411cfbb9b2afb966415473ac6d7aeeeb3d14019796  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/tests.py
704ae205c1689f1a422be5437f815d3f005cb3e6f9f18e14dce14108f0665bd2  evals/tasks/quantum/quantum_error_correction_shor_9qubit/candidate.py
53a4fca2a1d4bc50bbe1ae037365dfb4cb385867f86f17e43aac1826a49f942a  evals/tasks/quantum/quantum_qaoa_ring4_landscape/candidate.py
18c4c230851bea8b9a7c07e7e63a6c589a7aae0121c925c7464e9f5a169290a3  evals/tasks/quantum/quantum_qaoa_ring4_landscape/task.json
7b0edb9582b791f25e7f037ec2192e022a1aca156523c7a30b7e8b8323390ec0  evals/tasks/quantum/quantum_qaoa_ring4_landscape/tests.py
d120dacccc7a7e5275ae82e8fb51237633b30251f1b1630322d69a5c603ae8ab  evals/tasks/quantum/quantum_qft_periodic_state/candidate.py
ebd267d28641ee82b1ab3eb8cc1311a4404d9c2f4c396fc16e67f54d8f8b2590  evals/tasks/quantum/quantum_qft_periodic_state/task.json
1a5c67ea0d792acfb89b1f145a49f9e6a3b41ac1f5d01b2f2fcb794d67698b54  evals/tasks/quantum/quantum_qft_periodic_state/tests.py
da8a2df5ff111a370dce3dbc544fb0a94070e233d830e0209ae180196175c70a  evals/tasks/quantum/quantum_qml_variational_classifier/candidate.py
3797013aad4f4306494b05d6aaba2bcf58e9c0421399d98704c020004f8a15d7  evals/tasks/quantum/quantum_qml_variational_classifier/task.json
4ceb0643fe809c9d002605f18f949cbcc817ef46d73ee4d583fe6ab7ec99a814  evals/tasks/quantum/quantum_qml_variational_classifier/tests.py
cf077341049dda9bda626fea2988152c5578ed94019bf78f44b27a3004ce7494  evals/tasks/quantum/quantum_shor_phase_error_correction/candidate.py
924f62d00478418c0f8c050e9a5b1fa55d3dcc0c1ec33c2be275793849b99250  evals/tasks/quantum/quantum_shor_phase_error_correction/task.json
caa2f5ad530912bca05b7dc2fd653b545be269b4e2d04afb800316e27637a88d  evals/tasks/quantum/quantum_shor_phase_error_correction/tests.py
2fcbc2262b455b17fb03c676d706d815d17c00cfaeebb59f873860816a83beb4  evals/tasks/quantum/quantum_stabilizer_shor_generators/candidate.py
394cc88cf03ea9fa5455cbf6c5b70ee9322c303a64999ef730a0322765b12c5e  evals/tasks/quantum/quantum_stabilizer_shor_generators/task.json
4b624df712bace522ab885719fdf3c9d7f809a2ecf80332983302ce59c988714  evals/tasks/quantum/quantum_stabilizer_shor_generators/tests.py
94387663f339549e17e7140b689f21568c6aec325f998b43c7363a773d4f0e49  evals/tasks/quantum/quantum_three_qubit_entropy/candidate.py
b2b14d381a003e9b592ab7635309bb6dedf326cc4ee604f200862ee0e31a0216  evals/tasks/quantum/quantum_three_qubit_entropy/task.json
924589a11f316b781a2bcf859349605d26277616b50cd948d45858d67d53e160  evals/tasks/quantum/quantum_three_qubit_entropy/tests.py
4517812d3ba0b406e7d8c8bae538e6d8b98a2169315536e881e8d724567fb644  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/candidate.py
963bb4f6b79e121051a2d333653e000370aae6f3fc2cbf60b15039fc0204bb01  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/task.json
ea61dcafa29bff20cf30e0e9e5a3136f108849fdc60a66ff09ee00b3cadd0141  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/tests.py
20e155a60b412fa0567a163c6351b6ba1e65cd3aeb83aaca6c6d0faa3afe5f18  evals/tasks/quantum/quantum_vqe_heisenberg_energy/candidate.py
8509c851c68dff4c743dd3a7572579698ba9f382bb77f64bd7405dfdb49935fb  evals/tasks/quantum/quantum_vqe_heisenberg_energy/task.json
8a04b56c4c4ab367dc28bd579ad8a921fbca1ebc46270392fb9d89e5b32af16c  evals/tasks/quantum/quantum_vqe_heisenberg_energy/tests.py
7042529da93af3815df7941a9937a1476b1fd18d5571c0605acd617580b174f8  evals/tasks/quantum/stabilizer_tableau_update_repair/tests.py
e1bea2e227a012ae8b066f9cac0e3534a971b56a11270f3c40ca85d23d60a8cd  evals/tasks/quantum/superdense_coding/task.json
e3daa4ff10309b0044f6ed4fe5a707b6992fafcc180c30dd838af7bb906f9b7e  evals/tasks/quantum/superdense_identity_lookup/tests.py
fd6e10cad2e3c9c0d9176eefc5a165c2202b2c4ef97b3d513b64bfa922d3db59  evals/tasks/quantum/superdense_pauli_router/tests.py
dd4ff8fe03ad22e2d37a41683bd166ab787edc7f807dbef473babe54a0a96598  evals/tasks/quantum/teleportation_corrections/tests.py
c125239727ff913543e727979e7aa480341d99331b75f27324782c98793206c2  evals/tasks/quantum/vqe_energy_minimization/candidate.py
5f723b9e328abd5d08462d7dc0ccdb1c395eea31a89357c53e89ed07f16485a0  reports/sapo-holdout-enrichment-manifest-2026-08-24.json
3a956eb620980dacfd4ce553f24e26c569c9501e9a5e97c5dd70fc25cfd6ac5a  scripts/ai_launch_sapo_direct.sh
869654dded1a36ee42cac120272a1657c11b4ea12b5a22b6a59d31f6b56c0d69  scripts/asi2_launch_grpo_27b_selfeval.sh
63158871a80cfe275d168c0519149b88abdb707bae69b7b5a6e5036fff1159a9  scripts/asi2_watchdog_relaunch.sh
1d831fccf9c183f09f2a9ae2165bcbedf16de7fabaf7e3d2883921cde1455729  scripts/asi3_launch_grpo_direct.sh
77bb097c26c6e3fbddb7911d92ed534f387eea7d1084b3da70efab32a9d3c94f  scripts/build_grpo_v8_manifest.py
5ab1acc36c0f1be0668634962a7583d22023119d68030d4dc6e23353fdb2bf0a  scripts/calibrate_model_judge.py
c07351d46a03ae1669f6d5430dee7b966b8dce80ae6e23390220d7b32d482903  scripts/decide_sapo_promotion_gate.py
d49aaeea2d1c25ff09df418ba594037e14a573554ed8d57d6a7f6afa7c944de6  scripts/eval_100_reeval.py
d97f9a7f7a018e4de774b59c3a0fb6e3622d03c61762f4cc5ba7f5abb1323fe8  scripts/eval_base_vs_adapter.py
766949e44a541db7ab9ddcdef50a5f9c60fcd53b66c992f80ed39e26197426c9  scripts/fine_score.py
94274f251f762a8c5d7d9c4e3bcdfd1d482551729b6ee032f55105a3985bcc3e  scripts/fv_gspo_repair_sidecar.sh
e35703662de7eeff9e2119c905f2da8f75c2a49e73ffd51833eda16750add759  scripts/report_base_adapter_comprehensive.py
2047b9a00169789ee8cbc851aeccd8e0de18805873a0022967b0886903cd2643  scripts/run_base_vs_adapter_eval.py
5c769d6c9626f1551a48e4db0478ec4cae299140d740dcaafe251ba67970f989  scripts/run_hf_pass1_eval.py
61c17c6529e12b9cc29ca2400618ea2112567c489508d2556e52607aec058a80  scripts/sapo_drift_watch.py
7a83b6c7d3ae2a3ccf11c19ca7ad1a2bde40ca8895d02a5455b0c1dd7a1fc048  scripts/sapo_math_audit_step_records.py
2b94cfec3d24cd124fec79f66e7d07ff945e85080849a5704b2b52724d8abda2  scripts/sapo_reward_audit.py
56472b5fc8592d828435f920a53a247e7a7300ba28b812a6b2f0095f505149de  scripts/sapo_status_snapshot.py
5607dbb49318f8f5106dad1eea253b23d65c7272da38999c21620e7f991319c5  scripts/serve_openai_chat_adapter.py
7890847631dc903c6e07574aac47cb71f2dbf3c952527420ef6e22c768313f83  scripts/submit_asi2_grpo_27b_selfeval_task.sh
670e7dba0dcffcdd89ed7219dcc26a1fae9c38498e2bedbd4c5cad3ecc1b8b25  tests/test_asi3_sapo_launcher_readiness.py
938e97eb8f5af240b2653088e14da876497e001ae5d06aec3f1d93a5ab733178  tests/test_compat.py
6354b5c4428627270d8a4b2da06aec2497f9880a307beedb57e81d4f19c612cc  tests/test_execute_run.py
84b85e3d743de62e286b2b2f185cb9982151b1652bb80b59673c29869edb23f0  tests/test_fine_score.py
58e6d6cae9f2d35cd73a588a97fc85166b160470ec1c167c76ee27945fd6f9e1  tests/test_grpo_chunked_recompute_backward.py
fd69ac72580ab6ae21d9e8f41f7a4f9b7a2d0c82e1b99454cad89a1712b3bc3f  tests/test_grpo_entropy_floor_backward_once.py
061137bcc408f24c9fd97d14bdb58fa04cb419cd2bdcc90cfc17218091010fde  tests/test_grpo_entropy_token_cap.py
e4bbe6997c0ce655081a9f710cb0a7d7c8c8ad3bb646e4c3e2c8a454b82f141d  tests/test_grpo_judge_wave.py
98598a2a94576bfc42b0eb438cea588bce207202582167bdd8da800432a4975b  tests/test_grpo_rollout_mix_entropy_floor.py
a97649ef1227988886fd29ad7fd5388430ac66248de53927a20e1de0aa72f5ca  tests/test_grpo_train_pass_truncation.py
97ec2387c5be9dccab1feccf3460371bbaadd559d4deda6280fb65949eeac939  tests/test_grpo_trainer_breakers.py
495b873f619754772bc55ad51d11a327271fe3e1ddce9d610211e473074da7d7  tests/test_grpo_trainer_eval_results.py
2ac7da9b23c2f542ca3fc10a00f7225e327179ba66d50ef38a64f97fe0932f85  tests/test_grpo_trainer_faulthandler.py
083ff7cbf7cdd89d8b95c1ecfc041d78ce35b7e4b44a48763ef04fef8effb168  tests/test_grpo_trainer_generation_stop.py
d0b8f6442d93c8fecfed3bed62531253c991f33734b26dff94cf158f7caba3e1  tests/test_grpo_trainer_loss_stats_router.py
19b6cd0b8a628ec636ddca043b3de33de979883f19dfcbc9b6a6a6ea361e0902  tests/test_grpo_trainer_main_failclosed.py
528ef0e1ef2799862eb3977a5c0d53f37ed653954886b5116098b10c9eac033e  tests/test_grpo_trainer_metrics.py
15bb6ca5d7394cb4273f7060c3b2cb36c3b38991fdc8cf0757a7b3aa9b07104b  tests/test_grpo_trainer_resume.py
b57d191b4ada2b97ad276ab609de74d1cbc129016563aea16f6134384a3350b3  tests/test_grpo_trainer_self_eval.py
59330ffb5a28ababb0934deb6b1f6e2ab7982c705152c4bc1ae8087cff1b79bf  tests/test_grpo_trainer_sigterm.py
eb6b45cbdded0f936bdae02aa9e2fe3de22c6e4494071cb398436d49f2ca64a1  tests/test_grpo_utils.py
0f9d1b0f62e9c9a825061fd54c6ae1f71fd902733fb592a0beac82a0cd6df803  tests/test_holdout_enrichment_invariance.py
9a8c71d22816dab414376030a60c77a7f232af2217e86d255df788c023b58b75  tests/test_holdout_scorer_version_awareness.py
1bd8105aa4b1ab4d3eecf0dd151969a86cac4ac4ccaf0d205b7c7adfe4e37ff7  tests/test_model_family_support.py
1b587b54f3acdedd50b733558ac7dbf80ba96b2d75384aa1119808750e8165d7  tests/test_model_judge.py
6363e022f9c0d6a16200f385e9a5a845df5b0c93e66abcb9389c648fa4235a9c  tests/test_pennylane_vqe_h2_scorer_versions.py
caea3662eb1cb632fd4c7b881e0081b157cb7708325739e52a4f45dbbc5accdb  tests/test_prepare_prompts_coverage.py
f43b364994eb1dfcdceb7314127da94a7154d292907f9c781119b54dd5fa3824  tests/test_promotion_eval_adapter_merge.py
60437d05c8fefac612d5e48f7105fc31907ec45925acfec28d7f22f55262ce8f  tests/test_report_base_adapter_comprehensive.py
2bcdae7e8bc4407dd55d0be549b910c2305d80a4a9f7f3a8b59f7f58afa49c6d  tests/test_run_eval_scoring.py
7f37d88898c639d677eaeebd7c2a914f9710a6a71a9547cfa8956b16698a2b08  tests/test_sapo_curriculum_holdout_adjacent.py
f68e2261ab1cef28df4cef65aaaaa815c6306d129bb2f0d17cae31e7c3da15db  tests/test_sapo_drift_watch.py
2c5d5a901992ca5f7e0cec39e268d71b2d0f157e4add6851a551aeeaee8fb9f9  tests/test_sapo_eval_security.py
d79ae1884791178a1fd2902224055c3ba4939b531e4d28ba74ed18bd191e71f4  tests/test_sapo_loss.py
b7b4ad1b64e22d99c268d948583c00b419f6f0354d91e270d2146dab9ad94dbc  tests/test_sapo_promotion_pipeline_hardening.py
78dd512c92ada912fa7487792d81bdf7899bd07c6b0c5d77fc0fe4bae2e53127  tests/test_sapo_prompt_audit_cli.py
cceee5cb5733a2dd06f251b6c8544fe06972be02d1032da7d14301fac0a7dbf4  tests/test_sapo_reward_audit_cli.py
974ee9324b55b608509e337a6e7eac01d13651c5a8c66bf40f87e5d32155a4a2  tests/test_sapo_reward_audit.py
ff59d248dfba4ea7fbbfbf40061b482c614613e2573c7f9b184e69bb975a5f9b  tests/test_sapo_status_snapshot.py
81863a1a6fef400243d3f7fabc7da6742b765e2a15b9280d498e0733fad6d832  tests/test_seed_run_with_references.py
1daa2c7e60bc461c57bb02117cd627846441d08e20835dd8c710cfd4b4e5cb85  tests/test_single_candidate_eval.py
b81877e0f9168cdf1f11c54b6d06f9c224a879df8bf2cebe2722edf54098f58e  training/acquire_public_qwen_snapshot.py
f1c5d2511d18f16445acf86e738de6680dae768b2115bf8935869522f6d4e62e  training/audit_model_source.py
9f65ba9acabdfa09ac425a22c778c5480f8dee8b61494412504b7948a9d59be5  training/compat.py
a0839dcb2cc41de87a3b2171609ecc8930fd4cd95a772fe3784dce60dd76cc87  training/generation.py
3e9c40c006ed80d853cca49e686229b2c5e082544930fb15c699ef1b36f13b2a  training/grpo_trainer.py
18f0ffa8e17234c228a1d71838c5d115c42ce9a99877781351bbf7b46bca2a24  training/grpo_utils.py
4f24ff8bb7fd9058ff273971c0d2be5a66338eea75fde756a979fdc583c3b88a  training/huanxin_cpu_smoke.py
2b0dcb760f35449e68a921ac807229ffcff676ba8983b718efa35f09e421acfb  training/inspect_moe_target_modules.py
5eac8e4fa3f17106d9852f50bd50daf340bc7d72e4e918695e1b7ae5e0496e1b  training/model_backend.py
8887b0664c94cfec7ba5817868bc34835df26c607e9195e42a5f9bd7b8a32f5e  training/model_family_preflight.py
10b237931f9eed984af9db86307eb02212e59bf3125033eec54097a243965db2  training/quantum_verifiers.py
f69033af0f58e28e87e5399a5858da7ae9d775470b626bd21f9735771c0e6818  training/qwen_sft_peft.py
c3efeaff20d2ee0fba3bdf48b46259028906672fbde736671c16373c1677af9e  training/research_plugins.py
8a1132457a55687b195215abad027ee2c13051ae0907b092109540211e5feb73  training/runtime_overlay.py
1339972471e2aba8d95c420a9e9be2fb34cfeed5c2304c65435efa9578e23040  training/teacher_free_repair.py
2f8dfad36b8679e6ecc16d6f0fae9a1b6eea4230843e9c8b072bdb5b79eedda6  training/text_preprocessor_backend.py
dc619538b009e94bc22613256bc05b64a398a5af4d3e0f08d27923faa540e6cc  training/turboquant.py
e01b3e4050ff29184d0b630d6324bd368df984f1d531c19872bea1931394da46  training/verify_qwen_snapshot.py

## r17 DEPLOY — calibration-gate supersede (2026-08-26 ~19:4x-19:5x CST)
- Rollout lane: no calibration file => judge mass EXACTLY 0 + judge_reward=None
  records; masses 0.50/0.40/0.10 everywhere; audit contract updated; 323/323
  green; E2E verified. Launch default MODEL_JUDGE_ENABLED=0 (no calibration
  exists — judge machinery verified-ready but correctly inert until calibrated).
- Verified in tree: calibration-gated weight map (grpo_trainer.py:1187 empty
  weight map without calibration file), --judge-calibration arg, w_J=0.10 gate.
  Deploywatch re-ran wave tests: 21/21 green (judge-wave 16 + entropy 5).
- r17 = r16 169 members (NO new files). Changed: training/grpo_trainer.py,
  training/grpo_utils.py, scripts/{asi2_launch_grpo_27b_selfeval,
  asi3_launch_grpo_direct}.sh, scripts/sapo_reward_audit.py,
  tests/test_grpo_judge_wave.py.
- Gates: closure CLOSURE OK (169), py3.9 0 hits, locks none, review/launchsim
  markers clear (launchsim r16 rehearsal passed — no new BLOCK). member==
  manifest==tree (fresh build-time hashes).
- Deploy: 108x6000B chunks, 0 failures, audit clean (107x6000+1904); box sha
  2f2c2fc9… == local, 482926 B both sides.
- Run tree refreshed; on box: GRPO_TRAINER IMPORT OK; calibration refs x16 in
  deployed trainer; manifest hashes match (grpo_trainer 5ab8a662…,
  grpo_utils e523333b…, judge test 616f52d9…).
- Rehearsal signaled: /tmp/sapo_launchsim_r17_TRIGGER — judge-inference step
  INCLUDED (default MODEL_JUDGE_ENABLED=0: judge mass==0, judge_reward=None,
  0.50/0.40/0.10 blend + audit identity; plus enabled-path probe to confirm
  inert-until-calibrated). Executor auto-relaunches on its pass.
- NEXT CYCLE: freshness + lock + register + closure scans.

### r17 manifest (169 members, sha256)
85106d8e4c0c337edbc95eec2972d363c96f50f2d91c0d4404438dff386c4f27  configs/rl/qwen36_27b_fv_gspo_asi2.json
7b8bdc04fe2a6b41ba867facdebe04170bf7c864a2e09c2b446718764f060f18  evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt
18d8b065dd70c63dd55c3b4e6f229b2c741f77b39f8bd9ae409686aaa6b3ac65  evals/runner/candidate_sanitize.py
498c04c31b09dbd237d32f35839a2340b64e3da4420ab10467cd5a0962fb3336  evals/runner/candidate_security.py
4f149f9819df3c49ec57be9358a72463263343e17ddb3b648b7e13ac912ffa33  evals/runner/execute_run.py
8cdf777b630422df6bc3cd993353022b9719bc8df40657d058d6ab16b807c89b  evals/runner/frozen_contract.py
8216b8421947fe656731e0c26ff661bd341a3a7da977888babb27aa7d9d8831c  evals/runner/prepare_prompts.py
e26b9ade036c75993e4126acbe5f6e9b834c8e1173959226a3a78c9f25ab29af  evals/runner/public_task_spec.py
97b5186207302723f47281a4ed1e19e3406518537031dd243cdd162d24063093  evals/runner/run_eval.py
a181cd994245f51a605cb20f69ae17da2f2cf3a06c648d2bcf066beec5d0dbe4  evals/runner/seed_run_with_references.py
c4fa8bfa41c6edeecbb7816d3da3d7e6672772bafd4e2e4073047931ad350947  evals/runner/single_candidate_eval.py
618088bda4208f9ca8d84361ee4068b51cc36da67d82313e8a353846405d3076  evals/runner/task_metadata.py
0108c020f916b8dbf8ab16d08560d0057265ecaee0f5f37289620a7e0e8f0e54  evals/tasks/quantum/bell_pair_construction/candidate.py
9f6bf09c6019fb84748c9df10638291fd62bfcc90fa049642b980a1541b52403  evals/tasks/quantum/bell_pair_construction/tests.py
976677faa3f3138f9ac53c1435cbb8002ef380dabff6dc74f2f4fc4821620da1  evals/tasks/quantum/binary_measurement_decoder/task.json
114bd9cf91467960db9b629475aad730929625271b7ea76e453199b3b40b6690  evals/tasks/quantum/binary_measurement_decoder/tests.py
48d45ea9b46d7e54f23edbb62e94e7fb132884250506e342c460c7c9bba2d7db  evals/tasks/quantum/bitstring_maxcut_landscape/tests.py
4b4c0ea792f29454d0430a473cdaa778bc1432801c7f2c8c0d935520c89a29e5  evals/tasks/quantum/circuit_phase_repair/tests.py
6ee4de0769c7dd49dfa317d83035cc870c83020b9094cac23d5724f6f30fbdc6  evals/tasks/quantum/density_matrix_partial_trace/candidate.py
311688fed1cf708c6cbbe7854c724c422758526c1e6d13f12d1f1d1eb409e804  evals/tasks/quantum/error_detection_bit_flip/tests.py
18ed2cb56ee7c96529c53d65921deb4c44dcfdedce5d2bb275e36b714d59e6ae  evals/tasks/quantum/gate_alias_casefold_barrier/candidate.py
5feaa43a0f846f7d605e3b9ee6946ba4e4d53e61da07ed4ea7d40117218db661  evals/tasks/quantum/gate_alias_casefold_barrier/tests.py
f1cf1e1144aeef96acac9f527b6b3d96ea9c0c938121a48d9f2fc735599d9525  evals/tasks/quantum/gate_alias_normalization/task.json
4e17b821390f6916b8fd29d64061489a7bde5367a648b8227b26276a79b97143  evals/tasks/quantum/gate_alias_normalization/tests.py
fb4c96d30a8260ad6aa9895e3c2673d3dd7cc264d9f0958bfa0d9a163eb7760b  evals/tasks/quantum/gate_alias_registry_cleanup/candidate.py
d02d9e3673930d64c3dd1483d8ebf00c6b23764fa18fe542f16930313722100f  evals/tasks/quantum/gate_alias_registry_cleanup/tests.py
8cba17a29939f736e18e729a86fbbef83be4db9811890f2467dac666f805d931  evals/tasks/quantum/gate_token_canonicalizer/tests.py
7a6d4835c6cf027a323a720cd9698cf80560470c9c3aba7652965da3aeaac224  evals/tasks/quantum/ghz_state_witness/candidate.py
48db0b26936ba658f1f6e9bc61e416c07888d4cb5c17a1fbcd1bea8b4e30d464  evals/tasks/quantum/ghz_state_witness/tests.py
8b0496f1b2f2d671774a3ff5ae38bbd3a12764f64a187274b022eb1f0592a0e6  evals/tasks/quantum/grover_oracle_diffusion/candidate.py
eca1461b210a9e9244be9876e7c4cc2ae0648beb6eb167c59247987a2fcc922c  evals/tasks/quantum/grover_oracle_diffusion/tests.py
0b0ac2c05ac0ddbe685a4244e4e39fd315669e1cce18b3546496f3a65414a600  evals/tasks/quantum/maxcut_assignment_enumerator/tests.py
c2ca2881a761af3709496a1598360c4b545cc489822445e30cbd2e7afaf878e7  evals/tasks/quantum/maxcut_partition_ranker/candidate.py
23377a27912b10f10417748b130a25cefa7d84c08fe5f44e3ee49b21ec9da758  evals/tasks/quantum/maxcut_partition_ranker/tests.py
4d96a1e736f4b95157c39e7bba399786142ccd8f9889d49de4d5ef8e73af87a6  evals/tasks/quantum/measurement_bug_repair/tests.py
563553f63aa5bd957cc4e73e52cc787864567e1e479d3199300bda019962bf0b  evals/tasks/quantum/pauli_message_codec/tests.py
3cab7c4111f541c247ff98769efadb772b4f9ca7d9846ea13bce96d3d4137061  evals/tasks/quantum/pennylane_qml_iris_classification/task.json
8982efe7a2fdcde6fa723d77db797137a741508ebda8d2f4cc0610ebc25c4829  evals/tasks/quantum/pennylane_qml_iris_classification/tests.py
b8f8cd014abf677dd7f22e509043260db2e15ae2dc02f4bee0e6225bb44fd8b2  evals/tasks/quantum/pennylane_vqe_h2/candidate.py
18f1ff5d5dc2ee486e8a2f0faa6b2a00937cedbed8d967e7534b300eba93718e  evals/tasks/quantum/pennylane_vqe_h2/task.json
76a0106a456cea4652535dfe4ba9dadeac6825cae4ba3196e50e3a88ab4305b9  evals/tasks/quantum/pennylane_vqe_h2/tests.py
0ed7b78ecaaf776fbf8a0dc9e7709d58d17d4ea52c617b6ee3e164686fbd1121  evals/tasks/quantum/phase_estimation_circuit/candidate.py
9e4454a5be086d3484fe0f53fb63167e574baa04c9a632224bc25db34fd01fde  evals/tasks/quantum/phase_estimation_circuit/tests.py
06f85efba02647dc0c70e27450ece118df0ffc54d18d28df046ff319420547a9  evals/tasks/quantum/phase_measurement_register/tests.py
cef961ca651f7d14be1de207da598be883f1b3df1f1aadbec677c7f7ae724d8c  evals/tasks/quantum/phase_register_roundtrip/task.json
710ea354eb1d74d20d464f555428e2d78f77b1d0647cdfc6ab1543798335fe7c  evals/tasks/quantum/qaoa_maxcut/candidate.py
4bbfddd37158e6e2fc233b6feaeac391a929e0f34fcf6c4ce81f5ac9c1343e23  evals/tasks/quantum/qft_phase_pattern/candidate.py
ef7954bc50e7e39bd989a3d0feb0a6bea63b385aebc90c2d3d2215b9505b7b09  evals/tasks/quantum/qft_phase_pattern/tests.py
c7fdd0cdb37181a5d17ab9c2f9cbf2d7f41a877e45a58abed0bd89050cb280dd  evals/tasks/quantum/qiskit_qft_entangled/candidate.py
9847758ddba6fc2e70f1e6673787f0ab7ba3212dd218c4d003df54feec9dadac  evals/tasks/quantum/qiskit_qft_entangled/task.json
5fe817cf31b288e9ca3c1b481818a99a390498e15057f1da865fadcc1ecb169c  evals/tasks/quantum/qiskit_qft_entangled/tests.py
56828d0864714775e0c4d6bad5731e7fc1ba05d41bdb561c09030101a531612a  evals/tasks/quantum/quantum_bell_basis_discrimination/candidate.py
8ec6477bb5f1ad67655a1aad8120d4272f0e91eb11377958e17f83042ca1b764  evals/tasks/quantum/quantum_bell_basis_discrimination/task.json
0106c3e28e4406c38988bb6d99e253783e7b65194231471dd94623b6471caeaa  evals/tasks/quantum/quantum_bell_basis_discrimination/tests.py
a6dc2f09d5d1a26fa6a0a7c9bfee82f97277621c53e0cff451aa23148d2c53cc  evals/tasks/quantum/quantum_channel_depolarizing/candidate.py
e35912c10f0414dd665c50acf05ef5edd954aa2a7286177a8b50df8c8d5c207e  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/candidate.py
4b87bf5ec307d1fe6bbc2d06da8c31fe9102ca7dc36617075de3a309a9633784  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/task.json
16c446c9ff37b6000febfc411cfbb9b2afb966415473ac6d7aeeeb3d14019796  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/tests.py
704ae205c1689f1a422be5437f815d3f005cb3e6f9f18e14dce14108f0665bd2  evals/tasks/quantum/quantum_error_correction_shor_9qubit/candidate.py
53a4fca2a1d4bc50bbe1ae037365dfb4cb385867f86f17e43aac1826a49f942a  evals/tasks/quantum/quantum_qaoa_ring4_landscape/candidate.py
18c4c230851bea8b9a7c07e7e63a6c589a7aae0121c925c7464e9f5a169290a3  evals/tasks/quantum/quantum_qaoa_ring4_landscape/task.json
7b0edb9582b791f25e7f037ec2192e022a1aca156523c7a30b7e8b8323390ec0  evals/tasks/quantum/quantum_qaoa_ring4_landscape/tests.py
d120dacccc7a7e5275ae82e8fb51237633b30251f1b1630322d69a5c603ae8ab  evals/tasks/quantum/quantum_qft_periodic_state/candidate.py
ebd267d28641ee82b1ab3eb8cc1311a4404d9c2f4c396fc16e67f54d8f8b2590  evals/tasks/quantum/quantum_qft_periodic_state/task.json
1a5c67ea0d792acfb89b1f145a49f9e6a3b41ac1f5d01b2f2fcb794d67698b54  evals/tasks/quantum/quantum_qft_periodic_state/tests.py
da8a2df5ff111a370dce3dbc544fb0a94070e233d830e0209ae180196175c70a  evals/tasks/quantum/quantum_qml_variational_classifier/candidate.py
3797013aad4f4306494b05d6aaba2bcf58e9c0421399d98704c020004f8a15d7  evals/tasks/quantum/quantum_qml_variational_classifier/task.json
4ceb0643fe809c9d002605f18f949cbcc817ef46d73ee4d583fe6ab7ec99a814  evals/tasks/quantum/quantum_qml_variational_classifier/tests.py
cf077341049dda9bda626fea2988152c5578ed94019bf78f44b27a3004ce7494  evals/tasks/quantum/quantum_shor_phase_error_correction/candidate.py
924f62d00478418c0f8c050e9a5b1fa55d3dcc0c1ec33c2be275793849b99250  evals/tasks/quantum/quantum_shor_phase_error_correction/task.json
caa2f5ad530912bca05b7dc2fd653b545be269b4e2d04afb800316e27637a88d  evals/tasks/quantum/quantum_shor_phase_error_correction/tests.py
2fcbc2262b455b17fb03c676d706d815d17c00cfaeebb59f873860816a83beb4  evals/tasks/quantum/quantum_stabilizer_shor_generators/candidate.py
394cc88cf03ea9fa5455cbf6c5b70ee9322c303a64999ef730a0322765b12c5e  evals/tasks/quantum/quantum_stabilizer_shor_generators/task.json
4b624df712bace522ab885719fdf3c9d7f809a2ecf80332983302ce59c988714  evals/tasks/quantum/quantum_stabilizer_shor_generators/tests.py
94387663f339549e17e7140b689f21568c6aec325f998b43c7363a773d4f0e49  evals/tasks/quantum/quantum_three_qubit_entropy/candidate.py
b2b14d381a003e9b592ab7635309bb6dedf326cc4ee604f200862ee0e31a0216  evals/tasks/quantum/quantum_three_qubit_entropy/task.json
924589a11f316b781a2bcf859349605d26277616b50cd948d45858d67d53e160  evals/tasks/quantum/quantum_three_qubit_entropy/tests.py
4517812d3ba0b406e7d8c8bae538e6d8b98a2169315536e881e8d724567fb644  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/candidate.py
963bb4f6b79e121051a2d333653e000370aae6f3fc2cbf60b15039fc0204bb01  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/task.json
ea61dcafa29bff20cf30e0e9e5a3136f108849fdc60a66ff09ee00b3cadd0141  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/tests.py
20e155a60b412fa0567a163c6351b6ba1e65cd3aeb83aaca6c6d0faa3afe5f18  evals/tasks/quantum/quantum_vqe_heisenberg_energy/candidate.py
8509c851c68dff4c743dd3a7572579698ba9f382bb77f64bd7405dfdb49935fb  evals/tasks/quantum/quantum_vqe_heisenberg_energy/task.json
8a04b56c4c4ab367dc28bd579ad8a921fbca1ebc46270392fb9d89e5b32af16c  evals/tasks/quantum/quantum_vqe_heisenberg_energy/tests.py
7042529da93af3815df7941a9937a1476b1fd18d5571c0605acd617580b174f8  evals/tasks/quantum/stabilizer_tableau_update_repair/tests.py
e1bea2e227a012ae8b066f9cac0e3534a971b56a11270f3c40ca85d23d60a8cd  evals/tasks/quantum/superdense_coding/task.json
e3daa4ff10309b0044f6ed4fe5a707b6992fafcc180c30dd838af7bb906f9b7e  evals/tasks/quantum/superdense_identity_lookup/tests.py
fd6e10cad2e3c9c0d9176eefc5a165c2202b2c4ef97b3d513b64bfa922d3db59  evals/tasks/quantum/superdense_pauli_router/tests.py
dd4ff8fe03ad22e2d37a41683bd166ab787edc7f807dbef473babe54a0a96598  evals/tasks/quantum/teleportation_corrections/tests.py
c125239727ff913543e727979e7aa480341d99331b75f27324782c98793206c2  evals/tasks/quantum/vqe_energy_minimization/candidate.py
5f723b9e328abd5d08462d7dc0ccdb1c395eea31a89357c53e89ed07f16485a0  reports/sapo-holdout-enrichment-manifest-2026-08-24.json
3a956eb620980dacfd4ce553f24e26c569c9501e9a5e97c5dd70fc25cfd6ac5a  scripts/ai_launch_sapo_direct.sh
55f274abdd90eab7f4f6731774f2e2f2f8c92169623211055c20adcffe2b5f22  scripts/asi2_launch_grpo_27b_selfeval.sh
63158871a80cfe275d168c0519149b88abdb707bae69b7b5a6e5036fff1159a9  scripts/asi2_watchdog_relaunch.sh
a8cc1ff97e0ae0f029489e716a8f8fc34cc21c530227b0b624c760b731cbe892  scripts/asi3_launch_grpo_direct.sh
77bb097c26c6e3fbddb7911d92ed534f387eea7d1084b3da70efab32a9d3c94f  scripts/build_grpo_v8_manifest.py
5ab1acc36c0f1be0668634962a7583d22023119d68030d4dc6e23353fdb2bf0a  scripts/calibrate_model_judge.py
c07351d46a03ae1669f6d5430dee7b966b8dce80ae6e23390220d7b32d482903  scripts/decide_sapo_promotion_gate.py
d49aaeea2d1c25ff09df418ba594037e14a573554ed8d57d6a7f6afa7c944de6  scripts/eval_100_reeval.py
d97f9a7f7a018e4de774b59c3a0fb6e3622d03c61762f4cc5ba7f5abb1323fe8  scripts/eval_base_vs_adapter.py
766949e44a541db7ab9ddcdef50a5f9c60fcd53b66c992f80ed39e26197426c9  scripts/fine_score.py
94274f251f762a8c5d7d9c4e3bcdfd1d482551729b6ee032f55105a3985bcc3e  scripts/fv_gspo_repair_sidecar.sh
e35703662de7eeff9e2119c905f2da8f75c2a49e73ffd51833eda16750add759  scripts/report_base_adapter_comprehensive.py
2047b9a00169789ee8cbc851aeccd8e0de18805873a0022967b0886903cd2643  scripts/run_base_vs_adapter_eval.py
5c769d6c9626f1551a48e4db0478ec4cae299140d740dcaafe251ba67970f989  scripts/run_hf_pass1_eval.py
61c17c6529e12b9cc29ca2400618ea2112567c489508d2556e52607aec058a80  scripts/sapo_drift_watch.py
7a83b6c7d3ae2a3ccf11c19ca7ad1a2bde40ca8895d02a5455b0c1dd7a1fc048  scripts/sapo_math_audit_step_records.py
83e94502e042958d7eeee0e4b48473df39ad01632eca97e7ef7478f99c7ba80f  scripts/sapo_reward_audit.py
56472b5fc8592d828435f920a53a247e7a7300ba28b812a6b2f0095f505149de  scripts/sapo_status_snapshot.py
5607dbb49318f8f5106dad1eea253b23d65c7272da38999c21620e7f991319c5  scripts/serve_openai_chat_adapter.py
7890847631dc903c6e07574aac47cb71f2dbf3c952527420ef6e22c768313f83  scripts/submit_asi2_grpo_27b_selfeval_task.sh
670e7dba0dcffcdd89ed7219dcc26a1fae9c38498e2bedbd4c5cad3ecc1b8b25  tests/test_asi3_sapo_launcher_readiness.py
938e97eb8f5af240b2653088e14da876497e001ae5d06aec3f1d93a5ab733178  tests/test_compat.py
6354b5c4428627270d8a4b2da06aec2497f9880a307beedb57e81d4f19c612cc  tests/test_execute_run.py
84b85e3d743de62e286b2b2f185cb9982151b1652bb80b59673c29869edb23f0  tests/test_fine_score.py
58e6d6cae9f2d35cd73a588a97fc85166b160470ec1c167c76ee27945fd6f9e1  tests/test_grpo_chunked_recompute_backward.py
fd69ac72580ab6ae21d9e8f41f7a4f9b7a2d0c82e1b99454cad89a1712b3bc3f  tests/test_grpo_entropy_floor_backward_once.py
061137bcc408f24c9fd97d14bdb58fa04cb419cd2bdcc90cfc17218091010fde  tests/test_grpo_entropy_token_cap.py
616f52d9a4f43aa8bbcf4756f3f5c57434329c81cfbdeaa6b464911930e27ad8  tests/test_grpo_judge_wave.py
98598a2a94576bfc42b0eb438cea588bce207202582167bdd8da800432a4975b  tests/test_grpo_rollout_mix_entropy_floor.py
a97649ef1227988886fd29ad7fd5388430ac66248de53927a20e1de0aa72f5ca  tests/test_grpo_train_pass_truncation.py
97ec2387c5be9dccab1feccf3460371bbaadd559d4deda6280fb65949eeac939  tests/test_grpo_trainer_breakers.py
495b873f619754772bc55ad51d11a327271fe3e1ddce9d610211e473074da7d7  tests/test_grpo_trainer_eval_results.py
2ac7da9b23c2f542ca3fc10a00f7225e327179ba66d50ef38a64f97fe0932f85  tests/test_grpo_trainer_faulthandler.py
083ff7cbf7cdd89d8b95c1ecfc041d78ce35b7e4b44a48763ef04fef8effb168  tests/test_grpo_trainer_generation_stop.py
d0b8f6442d93c8fecfed3bed62531253c991f33734b26dff94cf158f7caba3e1  tests/test_grpo_trainer_loss_stats_router.py
19b6cd0b8a628ec636ddca043b3de33de979883f19dfcbc9b6a6a6ea361e0902  tests/test_grpo_trainer_main_failclosed.py
528ef0e1ef2799862eb3977a5c0d53f37ed653954886b5116098b10c9eac033e  tests/test_grpo_trainer_metrics.py
15bb6ca5d7394cb4273f7060c3b2cb36c3b38991fdc8cf0757a7b3aa9b07104b  tests/test_grpo_trainer_resume.py
b57d191b4ada2b97ad276ab609de74d1cbc129016563aea16f6134384a3350b3  tests/test_grpo_trainer_self_eval.py
59330ffb5a28ababb0934deb6b1f6e2ab7982c705152c4bc1ae8087cff1b79bf  tests/test_grpo_trainer_sigterm.py
eb6b45cbdded0f936bdae02aa9e2fe3de22c6e4494071cb398436d49f2ca64a1  tests/test_grpo_utils.py
0f9d1b0f62e9c9a825061fd54c6ae1f71fd902733fb592a0beac82a0cd6df803  tests/test_holdout_enrichment_invariance.py
9a8c71d22816dab414376030a60c77a7f232af2217e86d255df788c023b58b75  tests/test_holdout_scorer_version_awareness.py
1bd8105aa4b1ab4d3eecf0dd151969a86cac4ac4ccaf0d205b7c7adfe4e37ff7  tests/test_model_family_support.py
1b587b54f3acdedd50b733558ac7dbf80ba96b2d75384aa1119808750e8165d7  tests/test_model_judge.py
6363e022f9c0d6a16200f385e9a5a845df5b0c93e66abcb9389c648fa4235a9c  tests/test_pennylane_vqe_h2_scorer_versions.py
caea3662eb1cb632fd4c7b881e0081b157cb7708325739e52a4f45dbbc5accdb  tests/test_prepare_prompts_coverage.py
f43b364994eb1dfcdceb7314127da94a7154d292907f9c781119b54dd5fa3824  tests/test_promotion_eval_adapter_merge.py
60437d05c8fefac612d5e48f7105fc31907ec45925acfec28d7f22f55262ce8f  tests/test_report_base_adapter_comprehensive.py
2bcdae7e8bc4407dd55d0be549b910c2305d80a4a9f7f3a8b59f7f58afa49c6d  tests/test_run_eval_scoring.py
7f37d88898c639d677eaeebd7c2a914f9710a6a71a9547cfa8956b16698a2b08  tests/test_sapo_curriculum_holdout_adjacent.py
f68e2261ab1cef28df4cef65aaaaa815c6306d129bb2f0d17cae31e7c3da15db  tests/test_sapo_drift_watch.py
2c5d5a901992ca5f7e0cec39e268d71b2d0f157e4add6851a551aeeaee8fb9f9  tests/test_sapo_eval_security.py
d79ae1884791178a1fd2902224055c3ba4939b531e4d28ba74ed18bd191e71f4  tests/test_sapo_loss.py
b7b4ad1b64e22d99c268d948583c00b419f6f0354d91e270d2146dab9ad94dbc  tests/test_sapo_promotion_pipeline_hardening.py
78dd512c92ada912fa7487792d81bdf7899bd07c6b0c5d77fc0fe4bae2e53127  tests/test_sapo_prompt_audit_cli.py
cceee5cb5733a2dd06f251b6c8544fe06972be02d1032da7d14301fac0a7dbf4  tests/test_sapo_reward_audit_cli.py
974ee9324b55b608509e337a6e7eac01d13651c5a8c66bf40f87e5d32155a4a2  tests/test_sapo_reward_audit.py
ff59d248dfba4ea7fbbfbf40061b482c614613e2573c7f9b184e69bb975a5f9b  tests/test_sapo_status_snapshot.py
81863a1a6fef400243d3f7fabc7da6742b765e2a15b9280d498e0733fad6d832  tests/test_seed_run_with_references.py
1daa2c7e60bc461c57bb02117cd627846441d08e20835dd8c710cfd4b4e5cb85  tests/test_single_candidate_eval.py
b81877e0f9168cdf1f11c54b6d06f9c224a879df8bf2cebe2722edf54098f58e  training/acquire_public_qwen_snapshot.py
f1c5d2511d18f16445acf86e738de6680dae768b2115bf8935869522f6d4e62e  training/audit_model_source.py
9f65ba9acabdfa09ac425a22c778c5480f8dee8b61494412504b7948a9d59be5  training/compat.py
a0839dcb2cc41de87a3b2171609ecc8930fd4cd95a772fe3784dce60dd76cc87  training/generation.py
5ab8a662aa191e20d565ddf7f1763e49c320ed0b29ed06cac4b395eb5d2cc279  training/grpo_trainer.py
e523333be0360c15be29801b09a0e4fe5217366cc52fe213af43778a522de953  training/grpo_utils.py
4f24ff8bb7fd9058ff273971c0d2be5a66338eea75fde756a979fdc583c3b88a  training/huanxin_cpu_smoke.py
2b0dcb760f35449e68a921ac807229ffcff676ba8983b718efa35f09e421acfb  training/inspect_moe_target_modules.py
5eac8e4fa3f17106d9852f50bd50daf340bc7d72e4e918695e1b7ae5e0496e1b  training/model_backend.py
8887b0664c94cfec7ba5817868bc34835df26c607e9195e42a5f9bd7b8a32f5e  training/model_family_preflight.py
10b237931f9eed984af9db86307eb02212e59bf3125033eec54097a243965db2  training/quantum_verifiers.py
f69033af0f58e28e87e5399a5858da7ae9d775470b626bd21f9735771c0e6818  training/qwen_sft_peft.py
c3efeaff20d2ee0fba3bdf48b46259028906672fbde736671c16373c1677af9e  training/research_plugins.py
8a1132457a55687b195215abad027ee2c13051ae0907b092109540211e5feb73  training/runtime_overlay.py
1339972471e2aba8d95c420a9e9be2fb34cfeed5c2304c65435efa9578e23040  training/teacher_free_repair.py
2f8dfad36b8679e6ecc16d6f0fae9a1b6eea4230843e9c8b072bdb5b79eedda6  training/text_preprocessor_backend.py
dc619538b009e94bc22613256bc05b64a398a5af4d3e0f08d27923faa540e6cc  training/turboquant.py
e01b3e4050ff29184d0b630d6324bd368df984f1d531c19872bea1931394da46  training/verify_qwen_snapshot.py

## r18 DEPLOY — full-terms instrumentation wave (2026-08-26 ~19:5x-20:0x CST)
- QA lane: every term per candidate in the record + grep-able line (reward
  components + judge dims, advantage terms, SAPO terms, entropy + trust-region
  terms, stop reasons + token counts); TDD 11/11 new + 392 regression green;
  code-review 3 bugs fixed incl. a judge-path crash; 4 stale mass pins ->
  0.50/0.40/0.10. Deploywatch re-ran wave tests: 39/39 green (instrumentation +
  model_judge suites). py3.9 scan: 0 real hits (test_model_judge.py hits are
  docstring + source-guard assert — the judge-path regression guard).
- r18 = r17 169 + tests/test_grpo_trainer_step_instrumentation.py = 170 members.
  Changed: training/grpo_trainer.py, tests/test_model_judge.py.
- Gates: closure CLOSURE OK (170), py3.9 clean, locks none, review/launchsim
  markers clear (r17 rehearsal passed). member==manifest==tree (fresh hashes).
- Deploy: 110x6000B chunks, 0 failures, audit clean (109x6000+2420); box sha
  8740e4ab… == local, 492315 B both sides.
- Run tree refreshed; on box: GRPO_TRAINER IMPORT OK; manifest hashes match
  (grpo_trainer f01881e4…, test_model_judge a4726701…, instrumentation
  a6704164…).
- Rehearsal signaled: /tmp/sapo_launchsim_r18_TRIGGER — judge-step + full-terms
  verification (per-candidate terms + grep-able line; masses 0.50/0.40/0.10).
  Executor auto-relaunches on its pass — r18 supersedes r17 (newest verified
  bundle).
- NEXT CYCLE: freshness + lock + register + closure scans.

### r18 manifest (170 members, sha256)
85106d8e4c0c337edbc95eec2972d363c96f50f2d91c0d4404438dff386c4f27  configs/rl/qwen36_27b_fv_gspo_asi2.json
7b8bdc04fe2a6b41ba867facdebe04170bf7c864a2e09c2b446718764f060f18  evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt
18d8b065dd70c63dd55c3b4e6f229b2c741f77b39f8bd9ae409686aaa6b3ac65  evals/runner/candidate_sanitize.py
498c04c31b09dbd237d32f35839a2340b64e3da4420ab10467cd5a0962fb3336  evals/runner/candidate_security.py
4f149f9819df3c49ec57be9358a72463263343e17ddb3b648b7e13ac912ffa33  evals/runner/execute_run.py
8cdf777b630422df6bc3cd993353022b9719bc8df40657d058d6ab16b807c89b  evals/runner/frozen_contract.py
8216b8421947fe656731e0c26ff661bd341a3a7da977888babb27aa7d9d8831c  evals/runner/prepare_prompts.py
e26b9ade036c75993e4126acbe5f6e9b834c8e1173959226a3a78c9f25ab29af  evals/runner/public_task_spec.py
97b5186207302723f47281a4ed1e19e3406518537031dd243cdd162d24063093  evals/runner/run_eval.py
a181cd994245f51a605cb20f69ae17da2f2cf3a06c648d2bcf066beec5d0dbe4  evals/runner/seed_run_with_references.py
c4fa8bfa41c6edeecbb7816d3da3d7e6672772bafd4e2e4073047931ad350947  evals/runner/single_candidate_eval.py
618088bda4208f9ca8d84361ee4068b51cc36da67d82313e8a353846405d3076  evals/runner/task_metadata.py
0108c020f916b8dbf8ab16d08560d0057265ecaee0f5f37289620a7e0e8f0e54  evals/tasks/quantum/bell_pair_construction/candidate.py
9f6bf09c6019fb84748c9df10638291fd62bfcc90fa049642b980a1541b52403  evals/tasks/quantum/bell_pair_construction/tests.py
976677faa3f3138f9ac53c1435cbb8002ef380dabff6dc74f2f4fc4821620da1  evals/tasks/quantum/binary_measurement_decoder/task.json
114bd9cf91467960db9b629475aad730929625271b7ea76e453199b3b40b6690  evals/tasks/quantum/binary_measurement_decoder/tests.py
48d45ea9b46d7e54f23edbb62e94e7fb132884250506e342c460c7c9bba2d7db  evals/tasks/quantum/bitstring_maxcut_landscape/tests.py
4b4c0ea792f29454d0430a473cdaa778bc1432801c7f2c8c0d935520c89a29e5  evals/tasks/quantum/circuit_phase_repair/tests.py
6ee4de0769c7dd49dfa317d83035cc870c83020b9094cac23d5724f6f30fbdc6  evals/tasks/quantum/density_matrix_partial_trace/candidate.py
311688fed1cf708c6cbbe7854c724c422758526c1e6d13f12d1f1d1eb409e804  evals/tasks/quantum/error_detection_bit_flip/tests.py
18ed2cb56ee7c96529c53d65921deb4c44dcfdedce5d2bb275e36b714d59e6ae  evals/tasks/quantum/gate_alias_casefold_barrier/candidate.py
5feaa43a0f846f7d605e3b9ee6946ba4e4d53e61da07ed4ea7d40117218db661  evals/tasks/quantum/gate_alias_casefold_barrier/tests.py
f1cf1e1144aeef96acac9f527b6b3d96ea9c0c938121a48d9f2fc735599d9525  evals/tasks/quantum/gate_alias_normalization/task.json
4e17b821390f6916b8fd29d64061489a7bde5367a648b8227b26276a79b97143  evals/tasks/quantum/gate_alias_normalization/tests.py
fb4c96d30a8260ad6aa9895e3c2673d3dd7cc264d9f0958bfa0d9a163eb7760b  evals/tasks/quantum/gate_alias_registry_cleanup/candidate.py
d02d9e3673930d64c3dd1483d8ebf00c6b23764fa18fe542f16930313722100f  evals/tasks/quantum/gate_alias_registry_cleanup/tests.py
8cba17a29939f736e18e729a86fbbef83be4db9811890f2467dac666f805d931  evals/tasks/quantum/gate_token_canonicalizer/tests.py
7a6d4835c6cf027a323a720cd9698cf80560470c9c3aba7652965da3aeaac224  evals/tasks/quantum/ghz_state_witness/candidate.py
48db0b26936ba658f1f6e9bc61e416c07888d4cb5c17a1fbcd1bea8b4e30d464  evals/tasks/quantum/ghz_state_witness/tests.py
8b0496f1b2f2d671774a3ff5ae38bbd3a12764f64a187274b022eb1f0592a0e6  evals/tasks/quantum/grover_oracle_diffusion/candidate.py
eca1461b210a9e9244be9876e7c4cc2ae0648beb6eb167c59247987a2fcc922c  evals/tasks/quantum/grover_oracle_diffusion/tests.py
0b0ac2c05ac0ddbe685a4244e4e39fd315669e1cce18b3546496f3a65414a600  evals/tasks/quantum/maxcut_assignment_enumerator/tests.py
c2ca2881a761af3709496a1598360c4b545cc489822445e30cbd2e7afaf878e7  evals/tasks/quantum/maxcut_partition_ranker/candidate.py
23377a27912b10f10417748b130a25cefa7d84c08fe5f44e3ee49b21ec9da758  evals/tasks/quantum/maxcut_partition_ranker/tests.py
4d96a1e736f4b95157c39e7bba399786142ccd8f9889d49de4d5ef8e73af87a6  evals/tasks/quantum/measurement_bug_repair/tests.py
563553f63aa5bd957cc4e73e52cc787864567e1e479d3199300bda019962bf0b  evals/tasks/quantum/pauli_message_codec/tests.py
3cab7c4111f541c247ff98769efadb772b4f9ca7d9846ea13bce96d3d4137061  evals/tasks/quantum/pennylane_qml_iris_classification/task.json
8982efe7a2fdcde6fa723d77db797137a741508ebda8d2f4cc0610ebc25c4829  evals/tasks/quantum/pennylane_qml_iris_classification/tests.py
b8f8cd014abf677dd7f22e509043260db2e15ae2dc02f4bee0e6225bb44fd8b2  evals/tasks/quantum/pennylane_vqe_h2/candidate.py
18f1ff5d5dc2ee486e8a2f0faa6b2a00937cedbed8d967e7534b300eba93718e  evals/tasks/quantum/pennylane_vqe_h2/task.json
76a0106a456cea4652535dfe4ba9dadeac6825cae4ba3196e50e3a88ab4305b9  evals/tasks/quantum/pennylane_vqe_h2/tests.py
0ed7b78ecaaf776fbf8a0dc9e7709d58d17d4ea52c617b6ee3e164686fbd1121  evals/tasks/quantum/phase_estimation_circuit/candidate.py
9e4454a5be086d3484fe0f53fb63167e574baa04c9a632224bc25db34fd01fde  evals/tasks/quantum/phase_estimation_circuit/tests.py
06f85efba02647dc0c70e27450ece118df0ffc54d18d28df046ff319420547a9  evals/tasks/quantum/phase_measurement_register/tests.py
cef961ca651f7d14be1de207da598be883f1b3df1f1aadbec677c7f7ae724d8c  evals/tasks/quantum/phase_register_roundtrip/task.json
710ea354eb1d74d20d464f555428e2d78f77b1d0647cdfc6ab1543798335fe7c  evals/tasks/quantum/qaoa_maxcut/candidate.py
4bbfddd37158e6e2fc233b6feaeac391a929e0f34fcf6c4ce81f5ac9c1343e23  evals/tasks/quantum/qft_phase_pattern/candidate.py
ef7954bc50e7e39bd989a3d0feb0a6bea63b385aebc90c2d3d2215b9505b7b09  evals/tasks/quantum/qft_phase_pattern/tests.py
c7fdd0cdb37181a5d17ab9c2f9cbf2d7f41a877e45a58abed0bd89050cb280dd  evals/tasks/quantum/qiskit_qft_entangled/candidate.py
9847758ddba6fc2e70f1e6673787f0ab7ba3212dd218c4d003df54feec9dadac  evals/tasks/quantum/qiskit_qft_entangled/task.json
5fe817cf31b288e9ca3c1b481818a99a390498e15057f1da865fadcc1ecb169c  evals/tasks/quantum/qiskit_qft_entangled/tests.py
56828d0864714775e0c4d6bad5731e7fc1ba05d41bdb561c09030101a531612a  evals/tasks/quantum/quantum_bell_basis_discrimination/candidate.py
8ec6477bb5f1ad67655a1aad8120d4272f0e91eb11377958e17f83042ca1b764  evals/tasks/quantum/quantum_bell_basis_discrimination/task.json
0106c3e28e4406c38988bb6d99e253783e7b65194231471dd94623b6471caeaa  evals/tasks/quantum/quantum_bell_basis_discrimination/tests.py
a6dc2f09d5d1a26fa6a0a7c9bfee82f97277621c53e0cff451aa23148d2c53cc  evals/tasks/quantum/quantum_channel_depolarizing/candidate.py
e35912c10f0414dd665c50acf05ef5edd954aa2a7286177a8b50df8c8d5c207e  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/candidate.py
4b87bf5ec307d1fe6bbc2d06da8c31fe9102ca7dc36617075de3a309a9633784  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/task.json
16c446c9ff37b6000febfc411cfbb9b2afb966415473ac6d7aeeeb3d14019796  evals/tasks/quantum/quantum_depolarizing_entanglement_decay/tests.py
704ae205c1689f1a422be5437f815d3f005cb3e6f9f18e14dce14108f0665bd2  evals/tasks/quantum/quantum_error_correction_shor_9qubit/candidate.py
53a4fca2a1d4bc50bbe1ae037365dfb4cb385867f86f17e43aac1826a49f942a  evals/tasks/quantum/quantum_qaoa_ring4_landscape/candidate.py
18c4c230851bea8b9a7c07e7e63a6c589a7aae0121c925c7464e9f5a169290a3  evals/tasks/quantum/quantum_qaoa_ring4_landscape/task.json
7b0edb9582b791f25e7f037ec2192e022a1aca156523c7a30b7e8b8323390ec0  evals/tasks/quantum/quantum_qaoa_ring4_landscape/tests.py
d120dacccc7a7e5275ae82e8fb51237633b30251f1b1630322d69a5c603ae8ab  evals/tasks/quantum/quantum_qft_periodic_state/candidate.py
ebd267d28641ee82b1ab3eb8cc1311a4404d9c2f4c396fc16e67f54d8f8b2590  evals/tasks/quantum/quantum_qft_periodic_state/task.json
1a5c67ea0d792acfb89b1f145a49f9e6a3b41ac1f5d01b2f2fcb794d67698b54  evals/tasks/quantum/quantum_qft_periodic_state/tests.py
da8a2df5ff111a370dce3dbc544fb0a94070e233d830e0209ae180196175c70a  evals/tasks/quantum/quantum_qml_variational_classifier/candidate.py
3797013aad4f4306494b05d6aaba2bcf58e9c0421399d98704c020004f8a15d7  evals/tasks/quantum/quantum_qml_variational_classifier/task.json
4ceb0643fe809c9d002605f18f949cbcc817ef46d73ee4d583fe6ab7ec99a814  evals/tasks/quantum/quantum_qml_variational_classifier/tests.py
cf077341049dda9bda626fea2988152c5578ed94019bf78f44b27a3004ce7494  evals/tasks/quantum/quantum_shor_phase_error_correction/candidate.py
924f62d00478418c0f8c050e9a5b1fa55d3dcc0c1ec33c2be275793849b99250  evals/tasks/quantum/quantum_shor_phase_error_correction/task.json
caa2f5ad530912bca05b7dc2fd653b545be269b4e2d04afb800316e27637a88d  evals/tasks/quantum/quantum_shor_phase_error_correction/tests.py
2fcbc2262b455b17fb03c676d706d815d17c00cfaeebb59f873860816a83beb4  evals/tasks/quantum/quantum_stabilizer_shor_generators/candidate.py
394cc88cf03ea9fa5455cbf6c5b70ee9322c303a64999ef730a0322765b12c5e  evals/tasks/quantum/quantum_stabilizer_shor_generators/task.json
4b624df712bace522ab885719fdf3c9d7f809a2ecf80332983302ce59c988714  evals/tasks/quantum/quantum_stabilizer_shor_generators/tests.py
94387663f339549e17e7140b689f21568c6aec325f998b43c7363a773d4f0e49  evals/tasks/quantum/quantum_three_qubit_entropy/candidate.py
b2b14d381a003e9b592ab7635309bb6dedf326cc4ee604f200862ee0e31a0216  evals/tasks/quantum/quantum_three_qubit_entropy/task.json
924589a11f316b781a2bcf859349605d26277616b50cd948d45858d67d53e160  evals/tasks/quantum/quantum_three_qubit_entropy/tests.py
4517812d3ba0b406e7d8c8bae538e6d8b98a2169315536e881e8d724567fb644  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/candidate.py
963bb4f6b79e121051a2d333653e000370aae6f3fc2cbf60b15039fc0204bb01  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/task.json
ea61dcafa29bff20cf30e0e9e5a3136f108849fdc60a66ff09ee00b3cadd0141  evals/tasks/quantum/quantum_trotter_heisenberg_evolution/tests.py
20e155a60b412fa0567a163c6351b6ba1e65cd3aeb83aaca6c6d0faa3afe5f18  evals/tasks/quantum/quantum_vqe_heisenberg_energy/candidate.py
8509c851c68dff4c743dd3a7572579698ba9f382bb77f64bd7405dfdb49935fb  evals/tasks/quantum/quantum_vqe_heisenberg_energy/task.json
8a04b56c4c4ab367dc28bd579ad8a921fbca1ebc46270392fb9d89e5b32af16c  evals/tasks/quantum/quantum_vqe_heisenberg_energy/tests.py
7042529da93af3815df7941a9937a1476b1fd18d5571c0605acd617580b174f8  evals/tasks/quantum/stabilizer_tableau_update_repair/tests.py
e1bea2e227a012ae8b066f9cac0e3534a971b56a11270f3c40ca85d23d60a8cd  evals/tasks/quantum/superdense_coding/task.json
e3daa4ff10309b0044f6ed4fe5a707b6992fafcc180c30dd838af7bb906f9b7e  evals/tasks/quantum/superdense_identity_lookup/tests.py
fd6e10cad2e3c9c0d9176eefc5a165c2202b2c4ef97b3d513b64bfa922d3db59  evals/tasks/quantum/superdense_pauli_router/tests.py
dd4ff8fe03ad22e2d37a41683bd166ab787edc7f807dbef473babe54a0a96598  evals/tasks/quantum/teleportation_corrections/tests.py
c125239727ff913543e727979e7aa480341d99331b75f27324782c98793206c2  evals/tasks/quantum/vqe_energy_minimization/candidate.py
5f723b9e328abd5d08462d7dc0ccdb1c395eea31a89357c53e89ed07f16485a0  reports/sapo-holdout-enrichment-manifest-2026-08-24.json
3a956eb620980dacfd4ce553f24e26c569c9501e9a5e97c5dd70fc25cfd6ac5a  scripts/ai_launch_sapo_direct.sh
55f274abdd90eab7f4f6731774f2e2f2f8c92169623211055c20adcffe2b5f22  scripts/asi2_launch_grpo_27b_selfeval.sh
63158871a80cfe275d168c0519149b88abdb707bae69b7b5a6e5036fff1159a9  scripts/asi2_watchdog_relaunch.sh
a8cc1ff97e0ae0f029489e716a8f8fc34cc21c530227b0b624c760b731cbe892  scripts/asi3_launch_grpo_direct.sh
77bb097c26c6e3fbddb7911d92ed534f387eea7d1084b3da70efab32a9d3c94f  scripts/build_grpo_v8_manifest.py
5ab1acc36c0f1be0668634962a7583d22023119d68030d4dc6e23353fdb2bf0a  scripts/calibrate_model_judge.py
c07351d46a03ae1669f6d5430dee7b966b8dce80ae6e23390220d7b32d482903  scripts/decide_sapo_promotion_gate.py
d49aaeea2d1c25ff09df418ba594037e14a573554ed8d57d6a7f6afa7c944de6  scripts/eval_100_reeval.py
d97f9a7f7a018e4de774b59c3a0fb6e3622d03c61762f4cc5ba7f5abb1323fe8  scripts/eval_base_vs_adapter.py
766949e44a541db7ab9ddcdef50a5f9c60fcd53b66c992f80ed39e26197426c9  scripts/fine_score.py
94274f251f762a8c5d7d9c4e3bcdfd1d482551729b6ee032f55105a3985bcc3e  scripts/fv_gspo_repair_sidecar.sh
e35703662de7eeff9e2119c905f2da8f75c2a49e73ffd51833eda16750add759  scripts/report_base_adapter_comprehensive.py
2047b9a00169789ee8cbc851aeccd8e0de18805873a0022967b0886903cd2643  scripts/run_base_vs_adapter_eval.py
5c769d6c9626f1551a48e4db0478ec4cae299140d740dcaafe251ba67970f989  scripts/run_hf_pass1_eval.py
61c17c6529e12b9cc29ca2400618ea2112567c489508d2556e52607aec058a80  scripts/sapo_drift_watch.py
7a83b6c7d3ae2a3ccf11c19ca7ad1a2bde40ca8895d02a5455b0c1dd7a1fc048  scripts/sapo_math_audit_step_records.py
83e94502e042958d7eeee0e4b48473df39ad01632eca97e7ef7478f99c7ba80f  scripts/sapo_reward_audit.py
56472b5fc8592d828435f920a53a247e7a7300ba28b812a6b2f0095f505149de  scripts/sapo_status_snapshot.py
5607dbb49318f8f5106dad1eea253b23d65c7272da38999c21620e7f991319c5  scripts/serve_openai_chat_adapter.py
7890847631dc903c6e07574aac47cb71f2dbf3c952527420ef6e22c768313f83  scripts/submit_asi2_grpo_27b_selfeval_task.sh
670e7dba0dcffcdd89ed7219dcc26a1fae9c38498e2bedbd4c5cad3ecc1b8b25  tests/test_asi3_sapo_launcher_readiness.py
938e97eb8f5af240b2653088e14da876497e001ae5d06aec3f1d93a5ab733178  tests/test_compat.py
6354b5c4428627270d8a4b2da06aec2497f9880a307beedb57e81d4f19c612cc  tests/test_execute_run.py
84b85e3d743de62e286b2b2f185cb9982151b1652bb80b59673c29869edb23f0  tests/test_fine_score.py
58e6d6cae9f2d35cd73a588a97fc85166b160470ec1c167c76ee27945fd6f9e1  tests/test_grpo_chunked_recompute_backward.py
fd69ac72580ab6ae21d9e8f41f7a4f9b7a2d0c82e1b99454cad89a1712b3bc3f  tests/test_grpo_entropy_floor_backward_once.py
061137bcc408f24c9fd97d14bdb58fa04cb419cd2bdcc90cfc17218091010fde  tests/test_grpo_entropy_token_cap.py
616f52d9a4f43aa8bbcf4756f3f5c57434329c81cfbdeaa6b464911930e27ad8  tests/test_grpo_judge_wave.py
98598a2a94576bfc42b0eb438cea588bce207202582167bdd8da800432a4975b  tests/test_grpo_rollout_mix_entropy_floor.py
a97649ef1227988886fd29ad7fd5388430ac66248de53927a20e1de0aa72f5ca  tests/test_grpo_train_pass_truncation.py
97ec2387c5be9dccab1feccf3460371bbaadd559d4deda6280fb65949eeac939  tests/test_grpo_trainer_breakers.py
495b873f619754772bc55ad51d11a327271fe3e1ddce9d610211e473074da7d7  tests/test_grpo_trainer_eval_results.py
2ac7da9b23c2f542ca3fc10a00f7225e327179ba66d50ef38a64f97fe0932f85  tests/test_grpo_trainer_faulthandler.py
083ff7cbf7cdd89d8b95c1ecfc041d78ce35b7e4b44a48763ef04fef8effb168  tests/test_grpo_trainer_generation_stop.py
d0b8f6442d93c8fecfed3bed62531253c991f33734b26dff94cf158f7caba3e1  tests/test_grpo_trainer_loss_stats_router.py
19b6cd0b8a628ec636ddca043b3de33de979883f19dfcbc9b6a6a6ea361e0902  tests/test_grpo_trainer_main_failclosed.py
528ef0e1ef2799862eb3977a5c0d53f37ed653954886b5116098b10c9eac033e  tests/test_grpo_trainer_metrics.py
15bb6ca5d7394cb4273f7060c3b2cb36c3b38991fdc8cf0757a7b3aa9b07104b  tests/test_grpo_trainer_resume.py
b57d191b4ada2b97ad276ab609de74d1cbc129016563aea16f6134384a3350b3  tests/test_grpo_trainer_self_eval.py
59330ffb5a28ababb0934deb6b1f6e2ab7982c705152c4bc1ae8087cff1b79bf  tests/test_grpo_trainer_sigterm.py
a670416433a93c7b0840d8adcafabf90719b6ba0cb4aa94d76507026be109d3b  tests/test_grpo_trainer_step_instrumentation.py
eb6b45cbdded0f936bdae02aa9e2fe3de22c6e4494071cb398436d49f2ca64a1  tests/test_grpo_utils.py
0f9d1b0f62e9c9a825061fd54c6ae1f71fd902733fb592a0beac82a0cd6df803  tests/test_holdout_enrichment_invariance.py
9a8c71d22816dab414376030a60c77a7f232af2217e86d255df788c023b58b75  tests/test_holdout_scorer_version_awareness.py
1bd8105aa4b1ab4d3eecf0dd151969a86cac4ac4ccaf0d205b7c7adfe4e37ff7  tests/test_model_family_support.py
a4726701d47163735c8e186b23d6dcac399bfcdc644feccef7df15b211e876c4  tests/test_model_judge.py
6363e022f9c0d6a16200f385e9a5a845df5b0c93e66abcb9389c648fa4235a9c  tests/test_pennylane_vqe_h2_scorer_versions.py
caea3662eb1cb632fd4c7b881e0081b157cb7708325739e52a4f45dbbc5accdb  tests/test_prepare_prompts_coverage.py
f43b364994eb1dfcdceb7314127da94a7154d292907f9c781119b54dd5fa3824  tests/test_promotion_eval_adapter_merge.py
60437d05c8fefac612d5e48f7105fc31907ec45925acfec28d7f22f55262ce8f  tests/test_report_base_adapter_comprehensive.py
2bcdae7e8bc4407dd55d0be549b910c2305d80a4a9f7f3a8b59f7f58afa49c6d  tests/test_run_eval_scoring.py
7f37d88898c639d677eaeebd7c2a914f9710a6a71a9547cfa8956b16698a2b08  tests/test_sapo_curriculum_holdout_adjacent.py
f68e2261ab1cef28df4cef65aaaaa815c6306d129bb2f0d17cae31e7c3da15db  tests/test_sapo_drift_watch.py
2c5d5a901992ca5f7e0cec39e268d71b2d0f157e4add6851a551aeeaee8fb9f9  tests/test_sapo_eval_security.py
d79ae1884791178a1fd2902224055c3ba4939b531e4d28ba74ed18bd191e71f4  tests/test_sapo_loss.py
b7b4ad1b64e22d99c268d948583c00b419f6f0354d91e270d2146dab9ad94dbc  tests/test_sapo_promotion_pipeline_hardening.py
78dd512c92ada912fa7487792d81bdf7899bd07c6b0c5d77fc0fe4bae2e53127  tests/test_sapo_prompt_audit_cli.py
cceee5cb5733a2dd06f251b6c8544fe06972be02d1032da7d14301fac0a7dbf4  tests/test_sapo_reward_audit_cli.py
974ee9324b55b608509e337a6e7eac01d13651c5a8c66bf40f87e5d32155a4a2  tests/test_sapo_reward_audit.py
ff59d248dfba4ea7fbbfbf40061b482c614613e2573c7f9b184e69bb975a5f9b  tests/test_sapo_status_snapshot.py
81863a1a6fef400243d3f7fabc7da6742b765e2a15b9280d498e0733fad6d832  tests/test_seed_run_with_references.py
1daa2c7e60bc461c57bb02117cd627846441d08e20835dd8c710cfd4b4e5cb85  tests/test_single_candidate_eval.py
b81877e0f9168cdf1f11c54b6d06f9c224a879df8bf2cebe2722edf54098f58e  training/acquire_public_qwen_snapshot.py
f1c5d2511d18f16445acf86e738de6680dae768b2115bf8935869522f6d4e62e  training/audit_model_source.py
9f65ba9acabdfa09ac425a22c778c5480f8dee8b61494412504b7948a9d59be5  training/compat.py
a0839dcb2cc41de87a3b2171609ecc8930fd4cd95a772fe3784dce60dd76cc87  training/generation.py
f01881e4bf176bc15a80e9e6e1ff3d1e17ee3860795913547192a43ce613d1f4  training/grpo_trainer.py
e523333be0360c15be29801b09a0e4fe5217366cc52fe213af43778a522de953  training/grpo_utils.py
4f24ff8bb7fd9058ff273971c0d2be5a66338eea75fde756a979fdc583c3b88a  training/huanxin_cpu_smoke.py
2b0dcb760f35449e68a921ac807229ffcff676ba8983b718efa35f09e421acfb  training/inspect_moe_target_modules.py
5eac8e4fa3f17106d9852f50bd50daf340bc7d72e4e918695e1b7ae5e0496e1b  training/model_backend.py
8887b0664c94cfec7ba5817868bc34835df26c607e9195e42a5f9bd7b8a32f5e  training/model_family_preflight.py
10b237931f9eed984af9db86307eb02212e59bf3125033eec54097a243965db2  training/quantum_verifiers.py
f69033af0f58e28e87e5399a5858da7ae9d775470b626bd21f9735771c0e6818  training/qwen_sft_peft.py
c3efeaff20d2ee0fba3bdf48b46259028906672fbde736671c16373c1677af9e  training/research_plugins.py
8a1132457a55687b195215abad027ee2c13051ae0907b092109540211e5feb73  training/runtime_overlay.py
1339972471e2aba8d95c420a9e9be2fb34cfeed5c2304c65435efa9578e23040  training/teacher_free_repair.py
2f8dfad36b8679e6ecc16d6f0fae9a1b6eea4230843e9c8b072bdb5b79eedda6  training/text_preprocessor_backend.py
dc619538b009e94bc22613256bc05b64a398a5af4d3e0f08d27923faa540e6cc  training/turboquant.py
e01b3e4050ff29184d0b630d6324bd368df984f1d531c19872bea1931394da46  training/verify_qwen_snapshot.py

## r21 (2026-09-01 ~03:40 UTC) — built + integrity-verified, NOT deployed (channel down)
- **tmp/sapo-relaunch-r21.tgz** sha256 **a2494484376516333c381eec6e5d5fecaac0d8ea961522c710256f9e37bb72ed** — 176 members + MANIFEST; every member hash-matches the embedded manifest (INTEGRITY OK, no extras/missing).
- Delta vs r20 (6 members): training/grpo_trainer.py (vLLM seam fence-parity fix + _vllm_succeeded guard), training/generation.py (truncate_at_closing_fence), evals/tasks/quantum/quantum_three_qubit_entropy/tests.py (zip-strict py3.9 fix), evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt (contract hash regen), tests/test_vllm_generate_group_seam.py (new, 5 tests), tests/test_sapo_holdout_scorer_enrichment.py (QA-lane repair 45/20/0).
- STATUS: READY for the next launch; NOT deployed (19005 daemon SSO-booting). Box-side RUN-13 continues on the deployed r20-era tree — no divergence (no deploy in flight).

## r21 FINAL (2026-09-01 ~04:05 UTC) — 180 members, sha 6ed8ab9e605304077fa0571b82de8cbb1ef526c1d7a452a7156a5d09ae37a5f8
- Added (vs first r21): scripts/run_asi2_base_adapter_rubric_eval.py + evals/benchmarks/sapo_promotion_holdout_v1_18.txt
  (eval instrument complete), scripts/asi2_loop_eval.sh (frozen-holdout fix) + tests/test_asi2_loop_eval_frozen_holdout.py.
- INTEGRITY OK (180/180 hash-match, no extras/missing). READY for next launch/deploy.

## r21 FINAL v2 (2026-09-01 ~04:20 UTC) — 180 members, sha 05e6698e66e3f22a905ff0864119f9e512bb9f8816e7db76e020c17bb36f8dde
- Rebuilt after dry-run help block updated to show --benchmark. INTEGRITY OK (180/180).
- READY for next launch/deploy. Contents: eval-loop frozen-holdout fix + evaluator + holdout file + vLLM seam + eval-security fix + enrichment repair.

## DEPLOY-INTEGRITY AUDIT r21 → r22 (2026-09-01) — REBUILT: r21 was NOT launch-ready

Audit target: tmp/sapo-relaunch-r21.tgz (sha 05e6698e66e3f22a905ff0864119f9e512bb9f8816e7db76e020c17bb36f8dde, 180 members).

### r21 defects found
1. **STALE (2)** — bundle sha != current-tree sha:
   - `scripts/asi3_launch_grpo_direct.sh`: bundle carries LR default `2e-4` (the RUN-12 entropy-blowup trap); tree has the 2026-09-01 manager fix defaulting to `5e-5`. Any box-side relaunch without an explicit override would re-introduce the destructive LR.
   - `tests/test_asi3_sapo_launcher_readiness.py`: asserts the old `2e-4` default (would pass against the stale script and mask the defect).
2. **MISSING (54 files, launch-critical)** — all exist in tree, absent from r20+r21:
   - `training/vllm_rollout_client.py` (imported by grpo_trainer.py:2362 — box ImportError without it) + its TDD `tests/test_vllm_rollout_client.py` (7 tests)
   - `scripts/launch_vllm_rollout_server.sh` (box-side vLLM-ascend server launcher)
   - `evals/benchmarks/quantum_grpo_training_v9_rl_questions_v2.txt` (v9 12-task benchmark)
   - 12 v9 task dirs `evals/tasks/quantum/quantum_rl_v2_*/` (36 files, all 12 benchmark-referenced tasks fully populated)
   - 5 frozen-holdout task dirs (15 files): trotterized_hamiltonian_evolution, cirq_qaoa_line, braket_bell_state, qiskit_stabilizer_5qubit_code (all in the 18-task promotion holdout), circuit_depth_optimization (v8 holdout-adjacent). The box cannot run 4 of the 18 promotion-holdout tasks or 1 of 20 v8-adjacent tasks without them.
3. Nested-artifact check: **0** nested .tgz/.tar (PASS — no nested-bundle glob bug).
4. Token scan (py3.10 constructs, local gate): 4x `zip(..., strict=` in holdout task files (bell_pair_construction/tests.py:19, ghz_state_witness/candidate.py:40, grover_oracle_diffusion/tests.py:16, qft_phase_pattern/tests.py:44); 3x more in new member trotterized_hamiltonian_evolution/tests.py:18,26,29. Box runs py3.11 → fine box-side; frozen task text is intentionally outside the compat-guard scope (compat.py docstring). No real X|Y type unions without future import. INFORMATIONAL ONLY.
5. Runtime gate: PASS in r21 and r22 — training/compat.py (strict_zip shim) + both frozen holdout benchmarks present.
6. Watchers: `scripts/sapo_box_pull_watch.sh` and `scripts/asi3_exec.py` are Mac-side only, correctly NOT in the bundle (verified absent in both r21 and r22). CORRECT.

### r22 rebuild (r21 pattern: r21 member list + deltas, manifest embedded, integrity verified)
- **tmp/sapo-relaunch-r22.tgz** sha256 **1a5754ba8fb27a884f52a819bffa285b10ddd3a50c70b98b60eece393a43b82e** — 235 members + MANIFEST.
- Immutable audited copy: **tmp/sapo-relaunch-r22-deployintegrity-audited.tgz** (same sha). Sidecar: tmp/sapo-relaunch-r22.sha256 (235 lines).
- Delta vs r21 (55 files): 4 launcher/eval files + 36 v9 task files + 15 holdout task files; the 2 stale members refreshed to tree versions (LR default now 5e-5; test asserts 5e-5).
- Post-build verification: 235/235 bundle-extract == manifest; 235/235 tree == manifest (bundle==tree); 0 nested; all 15 launch-critical present; 12 v9 dirs complete; 5 holdout dirs complete; watchers excluded.
- NOTE: sibling lanes were actively editing the tree during the audit (grpo_trainer.py, grpo_utils.py, generation.py, sapo_reward_audit.py, asi3_launch_grpo_direct.sh, several tests, config). Final build+verify used a single tree snapshot after a quiet window; re-verify bundle==tree before deploy if more fixes land.
- VERDICT: **r21 = REBUILD (2 stale + 54 missing). r22 = LAUNCH-READY** (at build snapshot).
- Test counts in bundle (launch-relevant): test_asi3_sapo_launcher_readiness 22, test_sapo_eval_security 10, test_vllm_rollout_client 7, test_vllm_generate_group_seam 6, test_asi2_loop_eval_frozen_holdout 4 = 49 test functions.

## r22 FINAL v3 (2026-09-01 23:50) — 328 members, sha cb131d299892b8cea58975d7ff5de7bc7e8df956478527b5a8533505834cea3d
- CRITICAL FIX (did-we-miss audit): r22 v2 (1537a12d) had LOST the eval instrument — the member list never
  contained sapo_promotion_holdout_v1_18.txt + run_asi2_base_adapter_rubric_eval.py + the 5 holdout task dirs,
  so rebuilds silently dropped them (r21 had them). On the box the corrected eval loop would fire →
  missing evaluator → SystemExit("benchmark file not found") → burned verdict cycle. NOW PRESENT.
- Complete critical set verified: frozen holdout + rubric evaluator + asi2_loop_eval.sh + vLLM client +
  v9 manifest + 15 holdout task files + launcher + sentinel rules + sidecar liveness. INTEGRITY OK.
- DEPLOY-FIRST PROTOCOL (recorded): pin → deploy r22 (sha-verify) → verify box files (holdout + evaluator +
  vLLM client present) → THEN let the eval loop fire. The box-pull watch pulls trainer state on ready;
  the eval verdict needs the deploy first.

## r22 FINAL v4 (2026-09-01 23:58, fixer lane) — 349 members, sha b978a5626c30a770d3f4dcec1c7243fb05e9f1bff0c756201bdd3c997b651ff8
- REBUILD TRIGGER (did-we-miss audit): the on-disk r22 tgz (22c5a1a4, Aug 31 23:43)
  had 11 members drifted vs the committed tree (wave commits b5d0d12/4c5f70d:
  grpo_trainer TypeError fail-closed, zip-strict py3.9 fixes, launcher chain,
  coverage-lane tests) and the documented FINAL v3 (328/cb131d29) had NO matching
  tgz on disk. A deploy from either would have shipped stale trainer code.
- REBUILT from the CURRENT committed tree via tmp/build_r22_bundle.py (lineage =
  previous 349-member sha256 + deltas; MANIFEST embedded; holdout gate 18/18
  resolvable+gradable).
- VERIFIED: shasum -c 349/349 OK (tree==bundle); critical set present (frozen
  holdout + rubric evaluator + asi2_loop_eval.sh + vLLM client + v9 manifest +
  sentinel rules + sidecar liveness + wedge detector); MANIFEST.sha256.json in tgz.
- DEPLOY-FIRST PROTOCOL unchanged: pin → deploy r22 (sha-verify b5e0adbc) →
  verify box files → let the eval loop fire.

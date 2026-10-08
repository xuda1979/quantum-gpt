# Parallel R&D Execution Strategy — 2026-07-13

**Purpose:** Maximize throughput across all active R&D lines by running
independent tracks concurrently rather than serially.

## Parallelism Mechanisms (in order of reliability)

1. **In-session parallel tool calls** — multiple Bash/Read/Edit calls in a
   single assistant turn. Highest reliability; no quota issues. Use for
   short tasks (<30s each) with no inter-call dependencies.
2. **Background bash** (`run_in_background: true`) — for tasks >30s
   (test suites, S3 syncs, eval runs). Each writes to its own log under
   `tmp/parallel-rd-<date>/track<X>-*.log`. Check with `cat` / `tail`.
3. **5-min cron heartbeat** (`job_b599cb70a0da`) — periodic dispatcher.
   On each tick, reviews which track is ready and advances it. Backstop,
   not primary driver. (Note: 2026-07-12 journal reported `claude --print`
   403 quota exhaustion making cron-dispatched subagents non-viable;
   in-session parallelism + background bash don't hit that quota.)

## Active R&D Lines → Tier Mapping

| Line | Tier | Why |
|------|------|-----|
| 1. Iter-3 dataset build | 1 (local, no deps) | `prepare_iter3_distill_sft.py build --dry-run` runs locally in <5s |
| 2. DR-GRPO health | 1 (local test suite) | `tests/test_grpo_metrics_wiring.py` runs in <10s |
| 3. Trust-eval health | 1 (local test suite) | `evals/trust/tests/` runs in <15s |
| 4. Artifact-scoring + KL-loss health | 1 (local test suites) | `tests/test_artifact_scoring.py` + `tests/test_qwen_sft_peft_kl_loss.py` |
| 5. eval_gate wiring into RL configs | 1 (local edit + test) | `tests/test_eval_gate_logic.py` validates schema |
| 6. Iter-2 adapter materialization (27B 628MB, 35B 5.3GB) | 2 (blocked on S3) | Huanxin MinIO endpoint down per `docs/s3-endpoint-investigation-2026-07-12.md` |
| 7. Phase 5 per-artifact scoring control run | 2 (blocked on Huanxin transport) | Per `docs/per-artifact-scoring-phase5-runlist-2026-07-11.md` |

## Dependency Graph

```
[6 adapter materialize] ──► [iter-2 12-task eval re-run] ──► [iter-3 train] ──► [iter-3 eval]
                                                                  ▲
[1 iter-3 build dry-run] ────────────────────────────────────────┘ (rows ready, just needs adapter verdict)

[5 eval_gate wiring] ──► [first RL + soft-distill round with gate armed]  (independent of adapter)

[2,3,4 health suites] ──► (regression backstop for any code change above)
```

## What Can Run in Parallel Right Now

All Tier-1 tracks (1-5) are independent and can execute in a single
parallel batch. Tier-2 tracks (6-7) are blocked on Huanxin platform
issues and cannot be unblocked locally.

## Proven Result (2026-07-13 13:23 CST)

All 5 Tier-1 tracks ran in parallel and completed in <2 min wall-clock:

| Track | Test count | Result |
|-------|-----------:|:------:|
| A: iter-3 build dry-run | — | ✅ 181 train / 22 eval rows |
| B: DR-GRPO health | 5 | ✅ 5/5 pass |
| C: trust-eval | 30 | ✅ 30/30 pass |
| D: artifact-scoring + KL-loss | 50 | ✅ 50/50 pass |
| E: eval_gate wiring | 13 | ✅ 13/13 pass; yx_qite config wired (ASI1 already had it) |

**Total: 98 tests pass, 1 config wired, 1 dry-run validated — all in parallel.**

## Anti-Patterns to Avoid

- **Serial dispatch** of independent test suites (wastes wall-clock).
- **Using cron subagents** for tasks that fit in a single in-session
  parallel batch (hits 403 quota per 2026-07-12 journal).
- **Treating Tier-2 blockers as Tier-1** (can't be unblocked locally;
  don't waste cycles retrying S3/MinIO — escalate to platform team).

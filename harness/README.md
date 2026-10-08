# QG Goal Harness (qgh)

The manager is a **program**, not a session. `harness/qgh.py tick` runs every 10 minutes from
crontab (self-reinstalling), reconciles durable state, harvests/decomposes/respawns worker agents,
and renders a standup. It runs until `qgh done-check` proves the goal: **an adapter on
Qwen3.8-27B that passes 18/18 on the frozen 18-task holdout, fail-closed verified.**

## How it kills the four failure modes (user directive 2026-09-16)

| Failure mode we had | Harness mechanism |
|---|---|
| work silently stops | deterministic tick from crontab (self-checks + reinstalls its own cron line); state in JSON files; dead/overrun workers harvested + cards re-armed idempotently every tick; wedged tick lock auto-broken after 30 min (`heal`) |
| wrong priorities held too long | single goal; every card names its goal edge (`why`); claim = strictly top-of-queue by priority; hard `budget_min` timebox — overrun = kill + decompose, never extend; WIP limits per lane |
| long contexts (slow, costly, wrong) | workers get a composed brief <=80 lines (card + acceptance + gates + output contract), never the monolithic history; replies must end with `RESULT/EVIDENCE/NEXT`; the tick never reads raw logs — it reads structured state + <=10-line tails |
| messy code / messy work | mechanical gates (`tdd`, `review`, `eval-failclosed`, `sha-verified`) — no evidence in the log = bounced (max 2 re-arms, then dead); TDD-first in every brief; tree locks for shared dirs; lane role cards bound authority |

## State (durable, small, diffable)
- `state/GOAL.json` — objective + done criteria (loop retires only when met)
- `state/QUEUE.json` — priority queue of cards (the ONLY way work enters the fleet)
- `state/FLEET.json` — live worker agents (pid, card, deadline, log)
- `state/EVENTS.jsonl` — append-only event log (dispatched/reaped/bounced/gate_bounced)
- `state/standup/` — rendered standups (last 30 kept); `state/STATUS.md` — one line per tick
- `state/probes/` — box health probes (fail-stale-closed: >30 min = STALE)

## Commands
```
python3 harness/qgh.py init | goal | seed | card add | queue | fleet
python3 harness/qgh.py dispatch [--lane L] | reap | tick | standup | done-check
python3 harness/qgh.py install-cron | watch [--interval S] | heal
```

## Worker contract (headless `claude --print`)
Brief = goal line + card + acceptance + gates + budget + rules + output contract.
Terminal lines: `RESULT: <DONE|PARTIAL|BLOCKED> <verdict>` / `EVIDENCE: <=10 lines` /
`NEXT: <=3 bullets`. Gates check the LOG for evidence (RED/GREEN + counts, REVIEW: APPROVED,
adapter-applied + adapter-probe-differs, sha256), never the worker's say-so.

## Integration with the project
- Eval: `scripts/run_asi2_base_adapter_rubric_eval.py` (3 parallel task slices on ASI2).
- Training: `scripts/ai_launch_sapo_direct.sh` on ASI3 (Qwen3.8-27B only).
- The 10-min legacy standup cron (claude session reading `.sapo-loop`) is superseded by
  `qgh tick` — retire it once the harness proves out.

## Never-stop guarantees
1. **Two independent schedulers**: crontab line AND two launchd agents
   (`com.quantumgpt.qgh-tick` every 10 min, `com.quantumgpt.qgh-heal` every 30 min).
   Each survives reboots; a crontab rewrite cannot stop the loop because launchd keeps
   firing, and `tick` re-installs BOTH (`install-cron` + `install-launchd`) every fire.
2. A wedged tick is broken automatically after 30 min; `heal` forces it manually.
3. Every worker has a deadline; the next tick kills overruns and re-arms the card.
4. Queue empty => `auto_plan` files a planner card => the loop never idles.
5. **API/internet outage tolerance** (the ONLY accepted stop condition): a worker that
   dies producing nothing is classified ENVIRONMENTAL — it re-arms the card WITHOUT a
   bounce strike; 2 consecutive spawn failures trip a 15-min API backoff (no cards
   burned while the model API is down); the FIRST successful spawn clears it. Recovery
   is automatic — no human, no session.
6. tick.log and worker logs self-rotate (5 MB cap) — the harness cannot die of its own
   output.
7. Only `GOAL.json status=DONE` (fail-closed 18/18 verdict) retires the loop.
8. `qgh doctor` = one command "is the loop alive" (goal, backoff, cron, last tick,
   launchd, queue, fleet).

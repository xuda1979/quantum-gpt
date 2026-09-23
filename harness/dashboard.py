"""Comprehensive system-status dashboard with FULL detailed tables.

The harness publishes this every tick — NOT a human. Every table has ALL
available columns: per-task verdicts, per-category breakdowns, event
timelines, exact failure reasons, evidence gates, sha pins, heartbeat ages,
command counts, adapter vs base rubric scores, critical failure analysis.
"""

import json
import os
import time
from collections import Counter

from harness_lib import age_min, now_iso, pid_alive


def render_dashboard(
    goal, queue, fleet, tick_no, verdicts=None, probes=None, env_health=None, state_dir=None
):
    now = time.time()
    cards = queue["cards"]
    statuses = Counter(c.get("status", "?") for c in cards)
    live_agents = [a for a in fleet["agents"] if a.get("status") == "running"]
    ready_cards = [c for c in cards if c.get("status") == "ready"]
    running_cards = [c for c in cards if c.get("status") == "running"]
    bounced_cards = [c for c in cards if c.get("status") == "bounced"]
    blocked_cards = [c for c in cards if c.get("status") == "blocked"]
    dead_cards = [c for c in cards if c.get("status") == "dead"]
    done_cards = [c for c in cards if c.get("status") == "done"]

    best_pass, best_vf = 0, "?"
    if verdicts:
        for v in verdicts:
            if not isinstance(v, dict):
                continue
            pa = v.get("pass_adapter")
            try:
                pa_int = int(str(pa).split("/")[0]) if pa is not None else 0
            except (ValueError, TypeError):
                pa_int = 0
            if pa_int > best_pass:
                best_pass, best_vf = pa_int, v.get("_file", "?")

    sd = state_dir or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "harness", "state"
    )

    L = []
    L.append("# SYSTEM DASHBOARD - QG Goal Harness")
    L.append("")
    L.append(
        f"_Auto-published every tick by `qgh.py tick`. Last update: {now_iso()} (tick #{tick_no})_"
    )
    L.append("")

    # ---- CRITICAL SELF-REVIEW ----
    L.append("## CRITICAL SELF-REVIEW")
    L.append("| # | check | result | verdict | detail |")
    L.append("|---|---|---|---|---|")
    n = 0
    # tick health
    n += 1
    status_md = os.path.join(sd, "STATUS.md")
    if os.path.exists(status_md):
        sa = int(now - os.path.getmtime(status_md))
        if sa > 2400:
            L.append(f"| {n} | tick health | last_success={sa}s | **FAIL** | loop HALTED |")
        else:
            L.append(f"| {n} | tick health | last_success={sa}s | PASS | ticking |")
    else:
        L.append(f"| {n} | tick health | no STATUS.md | **FAIL** | never ticked |")
    # zombies
    n += 1
    zombies = [a for a in live_agents if not pid_alive(a.get("pid"))]
    if zombies:
        L.append(
            f"| {n} | fleet | {len(zombies)} zombies | **FAIL** | {','.join(a.get('card', '?') for a in zombies)} |"
        )
    else:
        L.append(f"| {n} | fleet | {len(live_agents)} live, 0 zombies | PASS | all alive |")
    # environments
    n += 1
    if env_health:
        down = [
            nm
            for nm in ("ASI1", "ASI2", "ASI3")
            if not env_health.get(nm) or not env_health.get(nm, {}).get("ready")
        ]
        if down:
            L.append(f"| {n} | environments | {','.join(down)} down | **FAIL** | eval blocked |")
        else:
            L.append(f"| {n} | environments | all ready | PASS | 3/3 up |")
    else:
        L.append(f"| {n} | environments | unknown | WARN | no probe |")
    # bounce rate
    n += 1
    total_finished = statuses.get("done", 0) + statuses.get("bounced", 0)
    if total_finished > 0:
        br = statuses.get("bounced", 0) / total_finished * 100
        if br > 30:
            L.append(
                f"| {n} | bounce rate | {br:.0f}% ({statuses.get('bounced', 0)}/{total_finished}) | **FAIL** | too many failures |"
            )
        else:
            L.append(
                f"| {n} | bounce rate | {br:.0f}% ({statuses.get('bounced', 0)}/{total_finished}) | PASS | acceptable |"
            )
    else:
        L.append(f"| {n} | bounce rate | n/a | WARN | no finished cards |")
    # goal progress
    n += 1
    if best_pass >= 18:
        L.append(f"| {n} | goal | {best_pass}/18 | **DONE** | goal achieved |")
    elif best_pass > 0:
        L.append(f"| {n} | goal | {best_pass}/18 | WIP | {18 - best_pass} tasks remaining |")
    else:
        L.append(f"| {n} | goal | 0/18 | **FAIL** | no passing eval yet |")
    L.append("")

    # ---- GOAL + DONE CRITERIA ----
    L.append("## GOAL")
    L.append(f"**{goal.get('objective', '?')}**")
    L.append(
        f"- status: **{goal.get('status', 'OPEN')}** | target: {goal.get('target_pass', '?')} | best: **{best_pass}/18** ({best_vf})"
    )
    dc = goal.get("done_criteria", [])
    if dc:
        L.append("- done criteria:")
        for d in dc:
            L.append(f"  - {d}")
    L.append("")

    # ---- ENVIRONMENTS (ALL fields) ----
    L.append("## ENVIRONMENTS (Huanxin)")
    L.append(
        "| env | port | ready | startup | uptime_s | cmds | busy | busy_ms | pending | browser | shell_ready | auth_drift | last_cmd | last_cmd_done | last_cmd_ms | pid | startup_error |"
    )
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    if env_health:
        for nm in ("ASI1", "ASI2", "ASI3"):
            d = env_health.get(nm)
            if not d:
                L.append(
                    f"| {nm} | - | DOWN | - | - | - | - | - | - | - | - | - | - | - | - | - | - |"
                )
            else:
                err = (d.get("startupError") or "")[:40]
                lc = str(d.get("lastCommand") or "")[:25]
                lcd = str(d.get("lastCommandCompletedAt") or "")[:20]
                L.append(
                    f"| {nm} | {d.get('port', '?')} | {d.get('ready', '?')} | "
                    f"{d.get('startupState', '?')} | {d.get('uptime', '?')} | "
                    f"{d.get('commandCount', '?')} | {d.get('busy', '?')} | "
                    f"{d.get('busyAgeMs', '?')} | {d.get('pendingRequestCount', '?')} | "
                    f"{d.get('browserMode', '?')} | {d.get('shellSurfaceReady', '?')} | "
                    f"{d.get('authDriftDetected', '?')} | {lc} | {lcd} | "
                    f"{d.get('lastCommandDurationMs', '?')} | {d.get('pid', '?')} | {err} |"
                )
    L.append("")

    # ---- LIVE AGENTS (ALL fields) ----
    L.append("## LIVE AGENTS")
    L.append(
        "| card | lane | pid | alive | age_min | deadline_min | log_bytes | heartbeat_age_s | has_RESULT | started_utc | deadline_utc |"
    )
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for a in live_agents:
        pid = a.get("pid")
        alive = "Y" if pid_alive(pid) else "N"
        ag = age_min(a.get("started_utc"))
        dl = age_min(a.get("deadline_utc"))
        log_path = os.path.join(sd, "agents", f"{a.get('card')}.log")
        log_sz = os.path.getsize(log_path) if os.path.exists(log_path) else 0
        hb_path = os.path.join(sd, "agents", f"{a.get('card')}.progress")
        hb_age = int(now - os.path.getmtime(hb_path)) if os.path.exists(hb_path) else 9999
        has_result = (
            "Y"
            if log_sz > 100
            and os.path.exists(log_path)
            and "RESULT:" in open(log_path, errors="replace").read()
            else "N"
        )
        L.append(
            f"| {a.get('card')} | {a.get('lane')} | {pid} | {alive} | "
            f"{ag if ag is not None else '?'} | {dl if dl is not None else '?'} | "
            f"{log_sz} | {hb_age} | {has_result} | {a.get('started_utc', '?')} | {a.get('deadline_utc', '?')} |"
        )
    if not live_agents:
        L.append("| _no live agents — loop may be halted_ |")
    L.append("")

    # ---- READY CARDS (ALL fields) ----
    L.append("## READY TO DISPATCH")
    L.append("| card | lane | priority | budget_min | deps | gates | bounce_count | title | why |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for c in sorted(ready_cards, key=lambda c: c.get("priority", 9))[:25]:
        deps = ",".join(c.get("deps", [])) or "-"
        gates = str(c.get("gates", []))[:30]
        L.append(
            f"| {c['id']} | {c.get('lane', '?')} | P{c.get('priority', 9)} | "
            f"{c.get('budget_min', '?')} | {deps} | {gates} | {c.get('bounce_count', 0)} | "
            f"{(c.get('title') or '')[:40]} | {(c.get('why') or '')[:40]} |"
        )
    if not ready_cards:
        L.append("| _no ready cards_ |")
    L.append("")

    # ---- RUNNING CARDS (ALL fields) ----
    L.append("## RUNNING CARDS")
    L.append(
        "| card | lane | priority | budget_min | deps | claimed_by | claimed_utc | deadline_utc | title |"
    )
    L.append("|---|---|---|---|---|---|---|---|---|")
    for c in running_cards:
        deps = ",".join(c.get("deps", [])) or "-"
        L.append(
            f"| {c['id']} | {c.get('lane', '?')} | P{c.get('priority', 9)} | "
            f"{c.get('budget_min', '?')} | {deps} | {c.get('claimed_by', '?')} | "
            f"{c.get('claimed_utc', '?')} | {c.get('deadline_utc', '?')} | {(c.get('title') or '')[:40]} |"
        )
    if not running_cards:
        L.append("| _no running cards_ |")
    L.append("")

    # ---- BOUNCED CARDS (ALL fields, failure analysis) ----
    L.append("## BOUNCED CARDS (failure analysis)")
    L.append("| card | lane | bounce_count | bounce_reason | result | title | why |")
    L.append("|---|---|---|---|---|---|---|")
    for c in sorted(bounced_cards, key=lambda c: c.get("bounce_count", 0), reverse=True)[:20]:
        br = (c.get("bounce_reason") or "")[:60]
        res = (c.get("result") or "")[:40]
        L.append(
            f"| {c['id']} | {c.get('lane', '?')} | {c.get('bounce_count', 0)} | "
            f"{br} | {res} | {(c.get('title') or '')[:35]} | {(c.get('why') or '')[:35]} |"
        )
    if not bounced_cards:
        L.append("| _no bounced cards_ |")
    L.append("")

    # ---- BLOCKED CARDS ----
    L.append("## BLOCKED CARDS")
    L.append("| card | lane | deps | deps_status | title | why |")
    L.append("|---|---|---|---|---|---|")
    by_id = {c["id"]: c for c in cards}
    for c in blocked_cards:
        deps = c.get("deps", [])
        deps_status = ",".join(f"{d}:{by_id.get(d, {}).get('status', '?')}" for d in deps) or "-"
        L.append(
            f"| {c['id']} | {c.get('lane', '?')} | {','.join(deps) or '-'} | "
            f"{deps_status} | {(c.get('title') or '')[:40]} | {(c.get('why') or '')[:40]} |"
        )
    if not blocked_cards:
        L.append("| _no blocked cards_ |")
    L.append("")

    # ---- DEAD CARDS ----
    L.append("## DEAD CARDS (exhausted retries)")
    L.append("| card | lane | bounce_count | result | title | why |")
    L.append("|---|---|---|---|---|---|")
    for c in dead_cards:
        L.append(
            f"| {c['id']} | {c.get('lane', '?')} | {c.get('bounce_count', 0)} | "
            f"{(c.get('result') or '')[:40]} | {(c.get('title') or '')[:40]} | {(c.get('why') or '')[:40]} |"
        )
    if not dead_cards:
        L.append("| _no dead cards_ |")
    L.append("")

    # ---- EVAL VERDICTS (FULL detail) ----
    L.append("## EVAL VERDICTS (full detail)")
    L.append(
        "| verdict_file | pass_adapt | pass_base | beats_base | sup | comp_adapt | comp_base | rub_adapt | rub_base | n_rec | sha16 | evidence_gate | sha_check | gains | losses | stale_reason |"
    )
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    if verdicts:
        for v in verdicts:
            if not isinstance(v, dict):
                continue
            vf = v.get("_file", "?")
            sr = (v.get("stale_reason") or "")[:35]
            eg = (v.get("evidence_gate") or "")[:25]
            sc = (v.get("box_side_candidate_sha_check") or "")[:25]
            gains = ",".join(v.get("gains") or []) or "-"
            losses = ",".join(v.get("losses") or []) or "-"
            L.append(
                f"| {vf} | {v.get('pass_adapter', '?')} | {v.get('pass_base', '?')} | "
                f"{v.get('beats_base', '?')} | {'YES' if v.get('superseded') else 'no'} | "
                f"{v.get('composite_adapter', '?')} | {v.get('composite_base', '?')} | "
                f"{v.get('rubric_adapter', '?')} | {v.get('rubric_base', '?')} | "
                f"{v.get('n_records', '?')} | {v.get('pulled_sha16', '?')} | {eg} | {sc} | "
                f"{gains} | {losses} | {sr} |"
            )
    else:
        L.append("| _no verdicts yet_ |")
    L.append("")

    # ---- PER-CATEGORY BREAKDOWN ----
    L.append("## PER-CATEGORY BREAKDOWN (best verdict)")
    if verdicts:
        best_v = max(
            (v for v in verdicts if isinstance(v, dict)),
            key=lambda v: (
                int(str(v.get("pass_adapter", "0")).split("/")[0]) if v.get("pass_adapter") else 0
            ),
            default=None,
        )
        if best_v:
            cats = best_v.get("by_category", [])
            if cats:
                L.append(
                    "| category | adapt_pass | base_pass | adapt_rubric | base_rubric | adapt_wins | n_tasks |"
                )
                L.append("|---|---|---|---|---|---|---|")
                for cat in cats:
                    L.append(
                        f"| {cat.get('category', '?')} | {cat.get('adapter_pass', '?')} | "
                        f"{cat.get('base_pass', '?')} | {cat.get('adapter_rubric', '?')} | "
                        f"{cat.get('base_rubric', '?')} | {cat.get('adapter_wins', '?')} | "
                        f"{cat.get('n_tasks', '?')} |"
                    )
            L.append("")
            # per-task wins
            L.append("## PER-TASK RESULTS (best verdict)")
            task_wins = best_v.get("by_task_wins", [])
            if task_wins:
                L.append("| task | adapter_wins |")
                L.append("|---|---|")
                for t in task_wins:
                    L.append(f"| {t} | YES |")
            L.append("")
            gains = best_v.get("gains", [])
            losses = best_v.get("losses", [])
            if gains or losses:
                L.append(f"- gains ({len(gains)}): {', '.join(gains)}")
                L.append(f"- losses ({len(losses)}): {', '.join(losses) if losses else 'none'}")
            L.append("")

    # ---- CRITICAL ANALYSIS: WHY ISN'T THE GOAL ACHIEVED? ----
    L.append("## CRITICAL ANALYSIS: WHY 3/18 NOT 18/18?")
    if best_pass < 18:
        L.append(f"Current best: **{best_pass}/18**. Remaining: **{18 - best_pass} tasks**.")
        L.append("")
        # diagnose blockers
        blockers = []
        if env_health:
            for nm in ("ASI1", "ASI2", "ASI3"):
                d = env_health.get(nm)
                if not d or not d.get("ready"):
                    blockers.append(f"{nm} not ready (eval cannot run on it)")
        # check for superseded verdicts
        if verdicts:
            all_sup = all(v.get("superseded") for v in verdicts if isinstance(v, dict))
            if all_sup:
                blockers.append(
                    "ALL verdicts are SUPERSEDED (sha_pin_violation) — no canonical eval has been run since the sha-pin requirement was added"
                )
        # check blocked cards
        if blocked_cards:
            for c in blocked_cards[:3]:
                blockers.append(f"card {c['id']} blocked: {(c.get('title') or '')[:50]}")
        if blockers:
            L.append("Root causes:")
            for b in blockers:
                L.append(f"  - **{b}**")
        else:
            L.append("No specific blockers detected — adapter may need more training.")
    else:
        L.append("**GOAL ACHIEVED! 18/18**")
    L.append("")

    # ---- RECENT EVENTS (timeline) ----
    L.append("## RECENT EVENTS (last 25)")
    L.append("| ts | kind | detail |")
    L.append("|---|---|---|")
    events_path = os.path.join(sd, "EVENTS.jsonl")
    if os.path.exists(events_path):
        lines = open(events_path, errors="replace").readlines()
        for line in lines[-25:]:
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            ts = ev.get("ts", "?")[:19]
            kind = ev.get("kind", "?")
            detail = str({k: v for k, v in ev.items() if k not in ("ts", "kind")})[:80]
            L.append(f"| {ts} | {kind} | {detail} |")
    L.append("")

    # ---- RECENT DONE CARDS ----
    L.append("## RECENT DONE CARDS (last 15)")
    L.append("| card | lane | result | title |")
    L.append("|---|---|---|---|")
    for c in done_cards[-15:]:
        L.append(
            f"| {c['id']} | {c.get('lane', '?')} | "
            f"{(c.get('result') or '')[:50]} | {(c.get('title') or '')[:40]} |"
        )
    if not done_cards:
        L.append("| _no done cards_ |")
    L.append("")

    # ---- FOOTER ----
    L.append("---")
    L.append(
        f"_Published by `qgh.py tick` #{tick_no}. Full events: `harness/state/EVENTS.jsonl`. "
        "Detailed whole-system report (every 3rd tick): `REPORT.md`._"
    )
    return "\n".join(L) + "\n"

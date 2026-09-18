"""Comprehensive system-status dashboard with detailed tables for every
component. Published to repo root every tick so the WHOLE system state is
visible. Non-negotiable: every table has the columns that show us what is
happening. Good DevOps/AI-DevOps practice: full observability."""

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

    L = []
    L.append("# SYSTEM DASHBOARD - QG Goal Harness")
    L.append("")
    L.append(f"_Auto-published every tick. Last update: {now_iso()} (tick #{tick_no})_")
    L.append("")

    # ---- GOAL TABLE ----
    L.append("## GOAL")
    L.append("| objective | status | target | best_eval | best_verdict |")
    L.append("|---|---|---|---|---|")
    obj = (goal.get("objective", "?") or "")[:80]
    L.append(
        f"| {obj} | **{goal.get('status', 'OPEN')}** | {goal.get('target_pass', '?')} | **{best_pass}/18** | {best_vf} |"
    )
    L.append("")

    # ---- QUEUE SUMMARY TABLE ----
    L.append("## QUEUE SUMMARY")
    L.append("| metric | value |")
    L.append("|---|---|")
    L.append(f"| total cards | {len(cards)} |")
    L.append(f"| done | {statuses.get('done', 0)} |")
    L.append(f"| running | {statuses.get('running', 0)} |")
    L.append(f"| ready | {statuses.get('ready', 0)} |")
    L.append(f"| bounced | {statuses.get('bounced', 0)} |")
    L.append(f"| blocked | {statuses.get('blocked', 0)} |")
    L.append(f"| dead | {statuses.get('dead', 0)} |")
    L.append(f"| superseded | {statuses.get('superseded', 0)} |")
    L.append(f"| live agents | {len(live_agents)} |")
    L.append("")

    # ---- ENVIRONMENTS TABLE ----
    L.append("## ENVIRONMENTS (Huanxin)")
    L.append(
        "| env | port | ready | startup | uptime_s | cmds | busy | pending | browser | shell_ready | pid |"
    )
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    if env_health:
        for name in ("ASI1", "ASI2", "ASI3"):
            d = env_health.get(name)
            if not d:
                L.append(f"| {name} | - | DOWN | - | - | - | - | - | - | - | - |")
            else:
                L.append(
                    f"| {name} | {d.get('port','?')} | {d.get('ready','?')} | "
                    f"{d.get('startupState','?')} | {d.get('uptime','?')} | "
                    f"{d.get('commandCount','?')} | {d.get('busy','?')} | "
                    f"{d.get('pendingRequestCount','?')} | {d.get('browserMode','?')} | "
                    f"{d.get('shellSurfaceReady','?')} | {d.get('pid','?')} |"
                )
    else:
        L.append("| _env_health not provided_ |")
    L.append("")

    # ---- LIVE AGENTS TABLE ----
    L.append("## LIVE AGENTS (workers working now)")
    L.append(
        "| card | lane | pid | alive | age_min | deadline_min | log_bytes | heartbeat_age_s | has_RESULT |"
    )
    L.append("|---|---|---|---|---|---|---|---|---|")
    for a in live_agents:
        pid = a.get("pid")
        alive = "Y" if pid_alive(pid) else "N"
        ag = age_min(a.get("started_utc"))
        dl = age_min(a.get("deadline_utc"))
        log_path = (
            os.path.join(state_dir or "", "agents", f"{a.get('card')}.log")
            if state_dir
            else f"harness/state/agents/{a.get('card')}.log"
        )
        log_sz = os.path.getsize(log_path) if os.path.exists(log_path) else 0
        hb_path = (
            os.path.join(state_dir or "", "agents", f"{a.get('card')}.progress")
            if state_dir
            else f"harness/state/agents/{a.get('card')}.progress"
        )
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
            f"{log_sz} | {hb_age} | {has_result} |"
        )
    if not live_agents:
        L.append("| _no live agents_ |")
    L.append("")

    # ---- READY CARDS TABLE ----
    L.append("## READY TO DISPATCH")
    L.append("| card | lane | priority | budget_min | deps | title |")
    L.append("|---|---|---|---|---|---|")
    for c in sorted(ready_cards, key=lambda c: c.get("priority", 9))[:25]:
        deps = ",".join(c.get("deps", [])) or "-"
        L.append(
            f"| {c['id']} | {c.get('lane','?')} | P{c.get('priority',9)} | "
            f"{c.get('budget_min','?')} | {deps} | {(c.get('title') or '')[:50]} |"
        )
    if not ready_cards:
        L.append("| _no ready cards_ |")
    L.append("")

    # ---- RUNNING CARDS TABLE ----
    L.append("## RUNNING CARDS")
    L.append("| card | lane | priority | budget_min | deps | title |")
    L.append("|---|---|---|---|---|---|")
    for c in running_cards:
        deps = ",".join(c.get("deps", [])) or "-"
        L.append(
            f"| {c['id']} | {c.get('lane','?')} | P{c.get('priority',9)} | "
            f"{c.get('budget_min','?')} | {deps} | {(c.get('title') or '')[:50]} |"
        )
    if not running_cards:
        L.append("| _no running cards_ |")
    L.append("")

    # ---- BOUNCED CARDS TABLE (failure signals) ----
    L.append("## BOUNCED CARDS (failure signals)")
    L.append("| card | lane | bounce_count | bounce_reason | title |")
    L.append("|---|---|---|---|---|")
    for c in sorted(bounced_cards, key=lambda c: c.get("bounce_count", 0), reverse=True)[:20]:
        L.append(
            f"| {c['id']} | {c.get('lane','?')} | {c.get('bounce_count',0)} | "
            f"{(c.get('bounce_reason') or '')[:70]} | {(c.get('title') or '')[:40]} |"
        )
    if not bounced_cards:
        L.append("| _no bounced cards_ |")
    L.append("")

    # ---- BLOCKED CARDS TABLE ----
    L.append("## BLOCKED CARDS")
    L.append("| card | lane | deps | title |")
    L.append("|---|---|---|---|")
    for c in blocked_cards:
        deps = ",".join(c.get("deps", [])) or "-"
        L.append(f"| {c['id']} | {c.get('lane','?')} | {deps} | {(c.get('title') or '')[:50]} |")
    if not blocked_cards:
        L.append("| _no blocked cards_ |")
    L.append("")

    # ---- DEAD CARDS TABLE ----
    L.append("## DEAD CARDS (exhausted retries)")
    L.append("| card | lane | bounce_count | title |")
    L.append("|---|---|---|---|")
    for c in dead_cards:
        L.append(
            f"| {c['id']} | {c.get('lane','?')} | {c.get('bounce_count',0)} | "
            f"{(c.get('title') or '')[:50]} |"
        )
    if not dead_cards:
        L.append("| _no dead cards_ |")
    L.append("")

    # ---- EVAL VERDICTS TABLE ----
    L.append("## EVAL VERDICTS (progress toward 18/18)")
    L.append(
        "| verdict_file | pass_adapter | pass_base | beats_base | superseded | composite_adapter | composite_base | rubric_adapter | rubric_base | gains | losses |"
    )
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    if verdicts:
        for v in verdicts:
            if not isinstance(v, dict):
                continue
            vf = v.get("_file", "?")
            pa = v.get("pass_adapter", "?")
            pb = v.get("pass_base", "?")
            bb = v.get("beats_base", "?")
            sup = "YES" if v.get("superseded") else "no"
            ca = v.get("composite_adapter", "?")
            cb = v.get("composite_base", "?")
            ra = v.get("rubric_adapter", "?")
            rb = v.get("rubric_base", "?")
            gains = len(v.get("gains", [])) if isinstance(v.get("gains"), list) else 0
            losses = len(v.get("losses", [])) if isinstance(v.get("losses"), list) else 0
            L.append(
                f"| {vf} | {pa} | {pb} | {bb} | {sup} | {ca} | {cb} | {ra} | {rb} | {gains} | {losses} |"
            )
    else:
        L.append("| _no verdicts yet_ |")
    L.append("")

    # ---- RECENT DONE CARDS TABLE ----
    L.append("## RECENT DONE CARDS (last 15)")
    L.append("| card | lane | title |")
    L.append("|---|---|---|")
    for c in done_cards[-15:]:
        L.append(f"| {c['id']} | {c.get('lane','?')} | {(c.get('title') or '')[:50]} |")
    if not done_cards:
        L.append("| _no done cards_ |")
    L.append("")

    # ---- FOOTER ----
    L.append("---")
    L.append("_Full standup: `harness/state/standup/`. Events: `harness/state/EVENTS.jsonl`._")
    return "\n".join(L) + "\n"

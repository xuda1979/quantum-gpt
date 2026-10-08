#!/usr/bin/env python3
"""status_render.py — render system status as human-readable text."""

from __future__ import annotations


def render_status(d: dict) -> str:
    """Render collected status dict as readable report."""
    lines = ["=" * 60, f"SYSTEM STATUS — {d['timestamp']}", "=" * 60]

    lines.append("\n--- BOXES ---")
    for box, info in d["boxes"].items():
        lines.append(f"  {box}: {info['status']}")

    lines.append("\n--- KEEPER ---")
    k = d["keeper"]
    lines.append(f"  pid={k.get('pid')} status={k.get('status')} daemons={k.get('daemons')}")

    lines.append("\n--- TRAINING ---")
    t = d["training"]
    flag = " ⚠️ STALE" if t["probe_stale"] else ""
    lines.append(f"  status: {t['probe_status']}{flag}")
    lines.append(f"  last_step: {t['last_step']}  loss: {t['last_loss']}")
    lines.append(f"  benchmark: {t['benchmark']}")
    lines.append(f"  v10_gate: {t['v10_gate']}")

    lines.append("\n--- QUEUE ---")
    q = d["queue"]
    lines.append(f"  total: {q['total_cards']}  by_status: {q['by_status']}")
    for c in q["running_cards"]:
        lines.append(f"  RUNNING: {c['id']} [{c['lane']}] {c['title']}")

    lines.append("\n--- EVAL ---")
    lines.append(f"  best_pass: {d['eval']['best_pass']}  verdicts: {d['eval']['total_verdicts']}")

    lines.append("\n--- ACTIVITY ---")
    lines.append(f"  commits_today: {d['commits_today']}")
    lines.append(f"  active_agents: {d['active_agents']}")
    lines.append("  recent_commits:")
    for c in d["recent_commits"]:
        lines.append(f"    {c}")

    lines.append("\n" + "=" * 60)
    all_alive = all(v["status"] == "ALIVE" for v in d["boxes"].values())
    verdict = "🟢 HEALTHY" if all_alive and not t["probe_stale"] else "🟡 DEGRADED"
    if not all_alive:
        verdict = "🔴 BOX DOWN"
    lines.append(f"VERDICT: {verdict}")
    lines.append("=" * 60)
    return "\n".join(lines)

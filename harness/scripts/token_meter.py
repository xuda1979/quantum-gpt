#!/usr/bin/env python3
"""token_meter.py — measure the tax: tokens per tick from the event ledger.

Turns "make it cheaper" from opinion into a number: reads EVENTS.jsonl, bins
events by kind, reports the top wasted-action classes (void legs, retries,
failed launches, re-reads). The #1 class becomes the next harness card.

Usage:
    python3 harness/scripts/token_meter.py            # top 10 kinds (all time)
    python3 harness/scripts/token_meter.py --days 7   # last 7 days only
    python3 harness/scripts/token_meter.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
LEDGER = REPO / "harness" / "state" / "EVENTS.jsonl"

WASTE_KINDS = {
    "redundant_install": ("launchd_installed", "installed", "rearm_spawned"),
    "reap_churn": ("reaped", "dispatched"),
    "stale": ("stale", "expire", "zombie", "dead"),
    "retry": ("retry", "rearm", "repush", "restart", "relaunch", "requeued"),
    "failed_launch": ("failed", "launch_failed", "boot_fail", "crash", "spawn_failed"),
    "watch_error": ("watch_error",),
    "void": ("void",),
}
KEEP_KINDS = {"card_added", "card_auto_retired", "auto_plan", "measured_eval_truth", "card_superseded"}


def load_events(days: int) -> list[dict]:
    """Events within window. <8 lines."""
    if not LEDGER.exists():
        return []
    cutoff = time.time() - days * 86400 if days else 0
    out = []
    for line in LEDGER.read_text().splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = e.get("ts", "")
        if days:
            try:
                t = time.mktime(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))
                if t < cutoff:
                    continue
            except ValueError:
                pass
        out.append(e)
    return out


def bin_kinds(events: list[dict]) -> Counter:
    """Count events by kind. <5 lines."""
    return Counter(e.get("kind", "unknown") for e in events)


def waste_classes(counter: Counter) -> list[tuple[str, int]]:
    """Aggregate counts into waste classes. <10 lines."""
    classes = Counter()
    for kind, n in counter.items():
        if kind in KEEP_KINDS:
            classes["progress"] += n
            continue
        kl = kind.lower()
        for cls, needles in WASTE_KINDS.items():
            if any(nd in kl for nd in needles):
                classes[cls] += n
                break
        else:
            classes["other"] += n
    return classes.most_common()


def main() -> None:
    """Report. <12 lines."""
    ap = argparse.ArgumentParser(description="Token/waste meter from event ledger")
    ap.add_argument("--days", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    events = load_events(args.days)
    counter = bin_kinds(events)
    if args.json:
        print(json.dumps({"total": len(events), "kinds": counter.most_common(), "waste": waste_classes(counter)}, indent=2))
        return
    print(f"TOTAL events: {len(events)} (days={args.days or 'all'})")
    print("\nTOP KINDS:")
    for kind, n in counter.most_common(10):
        print(f"  {n:6d}  {kind}")
    print("\nWASTE CLASSES:")
    for cls, n in waste_classes(counter):
        print(f"  {n:6d}  {cls}")
    worst = waste_classes(counter)
    if worst and worst[0][1] > 0 and worst[0][0] != "other":
        print(f"\nNEXT HARNESS CARD: reduce '{worst[0][0]}' ({worst[0][1]} events)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Manager-direct closure of C-10601 (precedent: C-10511/C-10452
manager-direct card_done closures).

C-10601 was the trainer-staleness watchdog feature card. Work completed
and verified live this session (commit f515681e0):

  - harness/scripts/c10601_trainer_staleness_watchdog.py: watchdog that
    classifies probes/trainer.json staleness (step age > 1800s or trainer
    positively not running), fires ONE idempotent trainer_stale_page per
    stale episode, and auto-mints ONE warm-continue ops card pinned to
    the best banked champion (BEST_CHECKPOINT.json adapter sha).
  - Fixed live bug found on first arming: the old dedupe matched any open
    card whose TITLE contained "warm-continue" — which suppressed the ops
    card forever because the C-10601 feature card itself says
    "auto-rearm warm-continue" in its title. Dedupe is now marker-scoped
    (kind == "warm-continue"), not title-scoped.
  - harness/tests/test_c10601_trainer_staleness_watchdog.py: 14/14 green
    (baseline 13/13, RED 13+1 fail, then GREEN).
  - Live smoke: --once fired the page and minted C-10606 (kind
    warm-continue, sha 373b6e6d, 18/18 epochs); second run quiet
    (idempotent). Champion-less stale fires the page but never mints a
    bogus card.

The card is closed manager-direct because the implementing session is
this manager session (no worker dispatch to bounce or claim it).
"""

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "harness"))

import qgh  # noqa: E402

STATE = qgh.STATE
CARD_ID = "C-10601"

EVIDENCE_FILES = [
    "harness/scripts/c10601_trainer_staleness_watchdog.py",
    "harness/tests/test_c10601_trainer_staleness_watchdog.py",
    "harness/state/EVENTS.jsonl",
]

RESULT_TEXT = (
    "Trainer staleness watchdog + auto-rearm warm-continue landed (commit "
    "f515681e0). classify_staleness: stale := step age > 1800s OR trainer "
    "positively not running; missing/unparseable probe is UNKNOWN and never "
    "pages (c10425 fire-storm doctrine); one idempotent trainer_stale_page "
    "per stale episode (recovery resets). Auto-mints ONE warm-continue ops "
    "card pinned to best banked champion (adapter sha from "
    "BEST_CHECKPOINT.json); champion-less stale pages loudly but mints "
    "nothing. Live bug fixed on first arming: old dedupe matched open cards "
    "by TITLE substring 'warm-continue', which forever suppressed the ops "
    "card because this feature card's own title says 'auto-rearm "
    "warm-continue' (watch state showed duplicate_card:true "
    "card_minted:false for ~47min); dedupe is now marker-scoped on "
    "kind=='warm-continue'. Tests 14/14 green (RED 13+1 fail first). Live "
    "smoke: --once fired page + minted C-10606 (sha 373b6e6d, 18/18); "
    "second run quiet. ruff clean. RED->GREEN evidence present."
)


def main() -> int:
    missing = [p for p in EVIDENCE_FILES if not os.path.isfile(os.path.join(REPO, p))]
    if missing:
        print("EVIDENCE MISSING:", missing)
        return 1

    lock = qgh.acquire_lock(qgh.QUEUE_LOCK, stale_s=qgh.QUEUE_STALE_SEC)
    if lock is None:
        print("queue busy: another qgh card op is mutating QUEUE.json")
        return 1
    try:
        queue = qgh.load_queue(STATE)
        card = qgh.find_card(queue, CARD_ID)
        if card is None:
            print("no such card:", CARD_ID)
            return 1
        if card["status"] != "ready":
            print(f"REFUSED: status is {card['status']!r}, not ready")
            return 1
        card["status"] = "done"
        card["result"] = RESULT_TEXT
        card["claimed_by"] = None
        card["claimed_utc"] = None
        card["deadline_utc"] = None
        card["done_utc"] = qgh.now_iso()
        qgh.save_json(os.path.join(STATE, "QUEUE.json"), queue)
    finally:
        qgh.release_lock(qgh.QUEUE_LOCK, lock)

    qgh.event(
        STATE,
        "card_done",
        {
            "card": CARD_ID,
            "lane": card["lane"],
            "by": "manager-direct (implementing session; work verified live)",
            "detail": (
                "C-10601 trainer staleness watchdog closed: watchdog + "
                "marker-scoped dedupe fix landed (f515681e0), tests 14/14 "
                "green, live mint of warm-continue C-10606 verified"
            ),
        },
    )
    print(
        f"CARD_DONE {CARD_ID} (manager-direct, bounce_count={card.get('bounce_count')} preserved)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""C-10601: trainer staleness watchdog + auto-rearm warm-continue.

The standup repeatedly flagged "Training NOT RUNNING (trainer UNKNOWN
step=3 age=1685707s)" yet nothing re-armed training — the trainer idled
for days (the empty-QUEUE livery alarm C-10570/C-10581 covers the queue,
not trainer staleness). This watchdog closes that gap:

  every tick:
    1. read probes/trainer.json (the same instrument the standup reads);
    2. classify staleness — stale when step age > STALE_STEP_AGE_S (1800)
       OR the trainer is NOT RUNNING (probe liveness term=process_state
       with process_found=False, or status not_running);
    3. on stale: fire ONE page (EVENTS.jsonl kind=trainer_stale_page,
       idempotent per stale episode — recovery resets the episode) and
       auto-mint ONE warm-continue successor card pinned to the best
       banked champion (BEST_CHECKPOINT.json adapter sha), so training
       never idles.

Fail-closed notes:
  - a missing/unparseable probe is UNKNOWN, never silently fresh: with
    no age evidence we do NOT fire (a dead transport must not page on
    every tick — that is the c10425 strikes doctrine), but the probe's
    own `age_s`/summary age is trusted when present.
  - no champion sha -> page still fires (loud) but NO card is minted
    (a bogus warm-continue pinned to nothing is worse than none).

State: harness/state/c10601_staleness_watchdog_state.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "harness"))
sys.path.insert(0, str(REPO / "harness" / "scripts"))

import qgh  # noqa: E402

STATE_DIR = REPO / "harness" / "state"
WATCH_STATE = STATE_DIR / "c10601_staleness_watchdog_state.json"
LOG = STATE_DIR / "logs" / "c10601_staleness_watchdog.log"
POLL_S = 300
STALE_STEP_AGE_S = 1800
PAGE_KIND = "trainer_stale_page"


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _emit(stage: str, **kw) -> None:
    line = json.dumps(dict(ts_utc=_now_iso(), stage=stage, **kw), ensure_ascii=False)
    print(line, flush=True)
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a") as f:
            f.write(line + "\n")
    except OSError:
        pass


# ----------------------------------------------------------------- classify
def _age_from_summary(summary: str):
    """Extract `age=<N>s` from the probe summary when age_s is absent."""
    m = re.search(r"age=(\d+)s", summary or "")
    return int(m.group(1)) if m else None


def classify_staleness(probe: dict, stale_age_s: int = STALE_STEP_AGE_S) -> dict:
    """Pure staleness classification of a trainer probe record.

    stale := step age > stale_age_s OR trainer positively not running.
    A probe with NO age evidence and no not-running evidence is UNKNOWN
    (not stale): a dead transport must not page forever (c10425).
    """
    status = str(probe.get("status") or "").lower()
    age_s = probe.get("age_s")
    if not isinstance(age_s, int) or age_s < 0:
        age_s = _age_from_summary(str(probe.get("summary") or ""))
    reasons = []
    not_running = False
    if status in ("not_running", "notrunning", "stopped", "dead"):
        not_running = True
        reasons.append(f"trainer not running (status={status})")
    liveness = probe.get("liveness") or {}
    if (
        isinstance(liveness, dict)
        and liveness.get("term") == "process_state"
        and liveness.get("process_found") is False
    ):
        not_running = True
        reasons.append("trainer not running (process_found=False)")
    if isinstance(age_s, int) and age_s > stale_age_s:
        reasons.append(f"step age {age_s}s > {stale_age_s}s")
    stale = bool(reasons)
    reason = "; ".join(reasons) if stale else "fresh"
    return {
        "stale": stale,
        "age_s": age_s if isinstance(age_s, int) else None,
        "not_running": not_running,
        "reason": reason,
    }


# ----------------------------------------------------------------- fire state
def _load_watch_state(path=None):
    path = Path(path or WATCH_STATE)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"episode": None, "fired": False, "last_verdict_stale": False, "last_ts_utc": None}


def _save_watch_state(path, st: dict) -> None:
    Path(path).write_text(json.dumps(st, indent=1, sort_keys=True), encoding="utf-8")


def _episode_key(verdict: dict) -> str:
    """Episode identity: a CONSTANT stale marker. The probe's age_s grows
    every refresh, so age must NOT key the episode (that re-pages every
    tick — the fire-storm the c10425 doctrine forbids). Recovery (a fresh
    read) resets the episode so a LATER stale event re-fires."""
    return "stale"


def _read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


# ----------------------------------------------------------------- card
def build_warm_continue_card(best: dict, verdict: dict, now=None) -> dict:
    """P1 trainer-ops warm-continue card pinned to the banked champion."""
    now = now or _now_iso()
    sha = str(best.get("adapter_sha256") or "")
    ckpt = str(best.get("checkpoint") or "")
    n = best.get("n_passes")
    title = (
        f"Warm-continue SFT from best banked champion (sha {sha[:8]}, {n}/18) "
        f"— trainer stale ({verdict.get('reason') or 'stale'})"
    )
    return {
        "id": None,
        "kind": "warm-continue",  # dedupe marker: title substrings lie (C-10601)
        "title": title,
        "lane": "trainer-ops",
        "priority": 1,
        "why": (
            f"C-10601 staleness watchdog fired: {verdict.get('reason') or 'stale'}. "
            "Best banked champion (BEST_CHECKPOINT.json) is the only safe resume "
            "point; re-arm warm-continue from it so training never idles."
        ),
        "acceptance": [
            f"warm-continue relaunched from checkpoint {ckpt} (adapter sha {sha})",
            f"trainer probe back to running with step age < {STALE_STEP_AGE_S}s for 2 consecutive ticks",
        ],
        "gates": [],
        "deps": [],
        "budget_min": 40,
        "status": "ready",
        "created_utc": now,
        "claimed_by": None,
        "claimed_utc": None,
        "deadline_utc": None,
        "result": None,
        "bounce_count": 0,
        "bounce_reason": None,
        "checkpoint": ckpt,
        "adapter_sha256": sha,
    }


def _dedupe_open_warm_continue(queue: dict) -> bool:
    for c in queue.get("cards", []):
        # Marker-scoped, not title-scoped: the C-10601 *feature* card itself
        # is lane trainer-ops and its title also says "auto-rearm
        # warm-continue" — a bare-title (or even title+lane) match would
        # forever suppress the ops card while the feature card sits open in
        # the live queue (the duplicate_card=true incident). The minted ops
        # card alone carries kind == "warm-continue"; only that counts.
        if c.get("kind") == "warm-continue" and c.get("status") in ("ready", "running", "claimed"):
            return True
    return False


# ----------------------------------------------------------------- cycle
def watchdog_once(state_dir=None, stale_age_s: int = STALE_STEP_AGE_S) -> dict:
    """One watchdog tick. Pure-ish (state on disk); never raises."""
    sd = Path(state_dir or STATE_DIR)
    probe = _read_json(sd / "probes" / "trainer.json")
    best = _read_json(sd / "BEST_CHECKPOINT.json")
    verdict = classify_staleness(probe, stale_age_s=stale_age_s)

    wpath = sd / WATCH_STATE.name
    st = _load_watch_state(wpath)
    fired = False
    card_minted = False
    card_mint_blocked = False
    duplicate_card = False

    if not verdict["stale"]:
        # recovery: reset the episode so a later stale re-fires (test:
        # recovery_rereads_after_trainer_healthy_again).
        if st.get("episode") is not None:
            st = {
                "episode": None,
                "fired": False,
                "last_verdict_stale": False,
                "last_ts_utc": _now_iso(),
            }
            _save_watch_state(wpath, st)
        return {
            "stale": False,
            "fired": False,
            "age_s": verdict["age_s"],
            "reason": verdict["reason"],
            "card_minted": False,
            "duplicate_card": False,
            "card_mint_blocked": False,
        }

    # stale: one page + one card per episode
    episode = _episode_key(verdict)
    if st.get("episode") != episode:
        # fresh stale episode (or first ever): fire page + mint card
        qgh.event(
            str(sd),
            PAGE_KIND,
            {
                "age_s": verdict["age_s"],
                "not_running": verdict["not_running"],
                "reason": verdict["reason"],
                "probe_summary": str(probe.get("summary") or "")[:200],
            },
        )
        fired = True
        if best.get("adapter_sha256") and best.get("checkpoint"):
            queue = qgh.load_queue(str(sd))
            if _dedupe_open_warm_continue(queue):
                duplicate_card = True
            else:
                card = build_warm_continue_card(best, verdict)
                qgh.add_card(queue, card, state_dir=str(sd))
                qgh.save_queue(str(sd), queue)
                card_minted = True
        else:
            card_mint_blocked = True  # no champion sha: loud page, no bogus card
        st = {
            "episode": episode,
            "fired": fired,
            "last_verdict_stale": True,
            "last_ts_utc": _now_iso(),
            "card_minted": card_minted,
            "card_mint_blocked": card_mint_blocked,
            "duplicate_card": duplicate_card,
        }
        _save_watch_state(wpath, st)
    else:
        st["last_ts_utc"] = _now_iso()
        st["last_verdict_stale"] = True
        _save_watch_state(wpath, st)

    return {
        "stale": True,
        "fired": fired,
        "age_s": verdict["age_s"],
        "reason": verdict["reason"],
        "card_minted": card_minted,
        "duplicate_card": duplicate_card,
        "card_mint_blocked": card_mint_blocked,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="C-10601 trainer staleness watchdog")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--interval-s", type=int, default=POLL_S)
    ap.add_argument("--stale-age-s", type=int, default=STALE_STEP_AGE_S)
    a = ap.parse_args(argv)
    _emit("watchdog_start", interval_s=a.interval_s, stale_age_s=a.stale_age_s)
    while True:
        try:
            rep = watchdog_once(stale_age_s=a.stale_age_s)
            _emit(
                "cycle",
                **{
                    k: rep[k]
                    for k in (
                        "stale",
                        "fired",
                        "age_s",
                        "card_minted",
                        "duplicate_card",
                        "card_mint_blocked",
                    )
                    if k in rep
                },
                reason=rep.get("reason"),
            )
        except Exception as exc:
            _emit("cycle_exc", error=repr(exc))
        if a.once:
            return 0
        time.sleep(a.interval_s)


if __name__ == "__main__":
    raise SystemExit(main())

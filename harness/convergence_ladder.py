"""Convergence ladder instrument (C-0070).

Owner-level instrument for the eval -> mine -> train -> eval round loop
that carries the QG goal (LoRA adapter on Qwen3.8-27B, 18/18 on the
frozen 18-task quantum holdout). Two halves:

1. LADDER -- the checked-in loop spec. Maps each round's stages to the
   existing card IDs that own them (eval leg C-0015/C-0052 class,
   mine C-0016, train C-0029/C-0066) and states entry/exit criteria per
   stage. A round is repeatable only if every stage's exit criteria hold;
   the next stage may only start when its entry criteria hold.

2. The no-progress detector. Given a round history (pass_adapter per
   round, e.g. from verdict files), detect_no_progress() reports a
   plateau when the last N rounds all failed to increase pass_adapter
   over the previous round. N rounds of history contain only N-1
   observable deltas, so at least N+1 rounds are required to fire.

REPORT-ONLY by contract (C-0070): the detector runs no training, runs no
eval, and never mutates QUEUE.json. Its only side channel is
emit_escalation(), which appends a single event to EVENTS.jsonl. The
escalation card itself is minted OUT OF BAND by an operator/tick with:

    python3 harness/qgh.py card add  # with escalation_card_spec() fields

Import-safe from the harness package dir; imports harness_lib as H.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_lib as H  # noqa: E402

SOURCE_CARD = "C-0070"
DEFAULT_PLATEAU_ROUNDS = 3

LADDER = {
    "objective": (
        "LoRA adapter on Qwen3.8-27B: 18/18 frozen 18-task holdout, "
        "fail-closed verified, beats base"
    ),
    "rounds": "unbounded until goal done-check passes; each round = eval, mine, train",
    "stages": [
        {
            "stage": "eval",
            "cards": ["C-0015", "C-0052"],
            "role": "fail-closed score of the newest adapter vs base on the frozen holdout",
            "entry": [
                "an unevaluated adapter checkpoint exists (or round 1: base baseline)",
                "asi2-eval.lock acquired via harness_lib.acquire_lock",
            ],
            "exit": [
                "verdict file with pass_adapter counted on the frozen 18 tasks",
                "fail-closed markers present: adapter-applied + adapter-probe-differs",
                "verdict recorded into the round history consumed by detect_no_progress",
            ],
        },
        {
            "stage": "mine",
            "cards": ["C-0016"],
            "role": "mine post-sanitize failure set into repair data for the next train",
            "entry": [
                "a completed eval verdict for the current round exists (eval exit met)",
                "failure set non-empty; if empty and pass_adapter == 18/18 the goal is done",
            ],
            "exit": [
                "repair dataset checked in and deduped against prior rounds",
                "mine report written with per-task failure counts",
            ],
        },
        {
            "stage": "train",
            "cards": ["C-0029", "C-0066"],
            "role": "relaunch LoRA training on ASI3 with the round's repair data",
            "entry": [
                "round repair data exists (mine exit met)",
                "box exec transport verified up (C-0066 fire-on-ready gate)",
            ],
            "exit": [
                "new adapter checkpoint landed and registered for the next eval stage",
                "launch preflight passed (sha/data/version checks per C-0029)",
            ],
        },
    ],
}


def detect_no_progress(history, n=DEFAULT_PLATEAU_ROUNDS):
    """Report a plateau: last N rounds with pass_adapter not increasing.

    history: list of round records in round order, each with keys
    "round" (int) and "pass_adapter" (int). A round "increases" only if
    its pass_adapter is strictly greater than the previous round's;
    equal or lower counts as no progress. Fires only when the last N
    observable deltas are all <= 0, which requires at least N+1 history
    entries; fewer never fires. Returns a dict; never raises on
    short/empty history.
    """
    entries = sorted(history, key=lambda r: r.get("round", 0))
    passes = [r.get("pass_adapter") for r in entries]
    last_pass = passes[-1] if passes else None
    record = {
        "plateau": False,
        "n": n,
        "rounds": [],
        "last_pass": last_pass,
        "rounds_observed": len(entries),
    }
    if len(passes) < n + 1:
        return record
    window = passes[-(n + 1) :]
    deltas = [b - a for a, b in zip(window, window[1:], strict=False)]
    record["rounds"] = [r.get("round") for r in entries[-n:]]
    if all(d <= 0 for d in deltas):
        record["plateau"] = True
        record["window_passes"] = window
    return record


def build_escalation_event(history, n=DEFAULT_PLATEAU_ROUNDS):
    """Build (not emit) the escalation event payload for a history."""
    rec = detect_no_progress(history, n=n)
    return {
        "kind": "no_progress_escalated",
        "card": SOURCE_CARD,
        "n": rec["n"],
        "rounds": rec["rounds"],
        "rounds_observed": rec["rounds_observed"],
        "last_pass": rec["last_pass"],
        "target_pass": "18/18",
        "history": list(history),
        "escalation_path": (
            "report-only event; mint the escalation card out of band with "
            "python3 harness/qgh.py card add (fields: escalation_card_spec)"
        ),
    }


def emit_escalation(state_dir, event_payload, check_history=True):
    """Append the escalation event to EVENTS.jsonl. REPORT-ONLY.

    Appends nothing unless the payload says no_progress_escalated and,
    when check_history is True, the referenced history actually shows a
    plateau (fail-closed against false escalation). Returns True if the
    event was appended. Never touches QUEUE.json.
    """
    if event_payload.get("kind") != "no_progress_escalated":
        return False
    if check_history:
        history = event_payload.get("history")
        if not history:
            return False
        n = event_payload.get("n", DEFAULT_PLATEAU_ROUNDS)
        if not detect_no_progress(history, n=n)["plateau"]:
            return False
    payload = dict(event_payload)
    payload.pop("history", None)
    H.event(state_dir, event_payload["kind"], payload)
    return True


def escalation_card_spec(history, n=DEFAULT_PLATEAU_ROUNDS):
    """Fields for the out-of-band escalation card (qgh.py card add).

    Not executed here: the operator/tick mints it. Kept out of the
    detector so this card stays report-only.
    """
    rec = detect_no_progress(history, n=n)
    last_pass = rec["last_pass"]
    return {
        "title": "Escalation: %d-round no-progress plateau at %s/18 (C-0070 detector)"
        % (n, last_pass),
        "lane": "planner",
        "why": (
            "pass_adapter did not increase for %d consecutive rounds; the "
            "eval-mine-train loop is idling short of 18/18" % n
        ),
        "acceptance": [
            "diagnose the stalled stage via LADDER entry/exit criteria",
            "file the corrective round card or declare the goal blocked",
        ],
    }

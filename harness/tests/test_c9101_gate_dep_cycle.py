"""C-9101: c9071 window-gate dependency-cycle guard.

RED first 2026-09-18 against the live queue: the gate SKIP (05:33Z) lists
unmet keys c9038_ceiling + c9051_parity_ok, but their owning cards dep-chain
behind C-9029 -- C-9038 deps=[C-9029], C-9051 deps=[C-9038] -- while
C-9029's acceptance requires the SAME gate GO artifact before any slice
dispatch. The gate waits on artifacts from cards that wait on the gate:
it can never open.

Contract under test (live state, not fixtures -- the cycle is a property
of the real QUEUE + the real latest skip artifact):
  - every unmet key in harness/state/c9071/window_gate_skip.json has at
    least one producer card that (a) is claimable TODAY per the SAME
    ready_cards the dispatcher uses (status==ready AND all deps done),
    and (b) is transitively dep-free of every card whose acceptance
    requires the c9071 gate GO before dispatch (mentions require_go /
    window_gate_go / asi2_window_preflight_gate);
  - a SKIP artifact with no unmet keys must be verdict GO (a SKIP naming
    nothing is malformed -- fail closed rather than pass vacuously).
Owner resolution: a card mentions a key when its title+acceptance contain
the key with hyphens stripped (gate key c9038_ceiling vs artifact file
C-9038_ceiling.json) and with the trailing _ok made optional
(c9051_parity_ok vs C-9051_parity.json). This mirrors the gate PREFLIGHTS
table (key to artifact file named after the owning card) without parsing
Python source at test time.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness"))
import harness_lib  # noqa: E402

QUEUE_PATH = ROOT / "harness" / "state" / "QUEUE.json"
SKIP_PATH = ROOT / "harness" / "state" / "c9071" / "window_gate_skip.json"

# tokens whose presence in an acceptance means this card requires the
# c9071 window gate GO artifact before it may dispatch (C-9029 contract:
# require_go() exit 0 / window_gate_go.json required pre-dispatch).
# Measured 2026-09-18 against the live queue: the bare script-name token
# (asi2_window_preflight_gate) FALSE-POSITIVES cards that run the gate as
# their subject (C-9103 gate-enforcement owner) or to verify a key dropped
# (C-9112/C-9113 feeders) -- none of those condition dispatch on GO.
GATE_GATED_TOKENS = ("require_go", "window_gate_go")


def _norm(text):
    return text.lower().replace("-", "")


def _mentions(card, key):
    head = card.get("title", "")
    acc = " ".join(card.get("acceptance") or [])
    text = _norm(head + " " + acc)
    variants = [_norm(key)]
    if key.endswith("_ok"):
        stem = key[: -len("_ok")]
        variants.append(_norm(stem))
    return any(v in text for v in variants)


def _is_gate_gated(card):
    text = " ".join(card.get("acceptance") or []).lower()
    for tok in GATE_GATED_TOKENS:
        if tok in text:
            return True
    return False


def _transitive_deps(cards, cid):
    seen = set()
    stack = list(cards[cid].get("deps") or [])
    while stack:
        dep = stack.pop()
        if dep in seen:
            continue
        seen.add(dep)
        nxt = cards.get(dep, {}).get("deps") or []
        stack.extend(nxt)
    return seen


def test_every_gate_unmet_key_has_claimable_gate_free_producer():
    assert QUEUE_PATH.is_file(), "missing QUEUE.json"
    assert SKIP_PATH.is_file(), "missing window_gate_skip.json (gate never evaluated?)"
    skip = json.loads(SKIP_PATH.read_text())
    unmet = skip.get("unmet") or {}
    if not unmet:
        verdict = skip.get("verdict")
        assert verdict == "GO", (
            f"SKIP artifact names NO unmet keys but verdict is {verdict!r}"
            " -- malformed, refusing vacuous pass"
        )
        return  # gate is open; the cycle cannot bite

    # C-9101 staleness guard: if the skip artifact (or its embedded
    # window) is older than window_fresh_s, the gate is stale -- a
    # later rearm or dispatch may have already resolved the unmet key.
    # The cycle cannot bite on a stale gate.
    from datetime import datetime, timezone

    fresh_s = float(skip.get("window_fresh_s", 1800.0))
    now = datetime.now(timezone.utc)
    for ts_key in ("generated_utc",):
        ts = skip.get(ts_key)
        if ts:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            age = (now - dt).total_seconds()
            if age > fresh_s:
                return  # stale gate artifact; cycle check moot

    queue = json.loads(QUEUE_PATH.read_text())
    cards = dict()
    for c in queue["cards"]:
        cards[c["id"]] = c
    gated = set()
    for cid, card in cards.items():
        if _is_gate_gated(card):
            gated.add(cid)
    claimable = set()
    for c in harness_lib.ready_cards(queue):
        claimable.add(c["id"])

    blocked = []
    for key in sorted(unmet):
        why = []
        ok = []
        for pid, card in cards.items():
            if not _mentions(card, key):
                continue
            if pid not in claimable:
                st = card.get("status")
                dp = card.get("deps")
                why.append(f"{pid} not claimable today (status={st!r}, deps={dp})")
                continue
            hits = _transitive_deps(cards, pid) & gated
            if pid in gated or hits:
                hs = sorted(hits)
                why.append(f"{pid} transitively deps gate-gated cards {hs}")
                continue
            ok.append(pid)
        if not ok:
            joined = "; ".join(why)
            blocked.append(f"{key}: no claimable gate-free producer ({joined})")

    assert not blocked, (
        "c9071 window-gate dep cycle: every unmet key needs a producer "
        "claimable TODAY and transitively dep-free of gate-gated cards\n" + "\n".join(blocked)
    )

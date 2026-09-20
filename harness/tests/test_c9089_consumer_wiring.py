"""C-9089 acceptance 4 guard: the C-9009/C-9016 consumers are WIRED to the
banked pin artifact, not free to guess a checkpoint at claim time.

RED-first (measured 2026-09-18 against the live QUEUE.json): the pin artifact
harness/state/probes/c9063_target_checkpoint.json existed (banked 10:26:03Z)
but neither consumer named it and neither depended on C-9089, so an evaluator
claiming C-9009/C-9016 could still pick a target ad hoc -- exactly the
bounce-dead hole this card re-files. The queue is the source of truth, so the
graph invariant is asserted against the real file (ledger-id guard idiom,
same as test_dep_graph_rebaseline.py).

Also re-verifies, independently, the banked pin another session produced:
re-runs the C-9089 selector on the LIVE C-9068 inventory + manifest and
compares every selection field, so DONE is never stamped on an unverified
claim.
"""

import json
import os
import re
import sys

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS_DIR = os.path.dirname(TEST_DIR)
REPO_DIR = os.path.dirname(HARNESS_DIR)
sys.path.insert(0, HARNESS_DIR)

import target_checkpoint as tc  # noqa: E402

QUEUE_PATH = os.path.join(HARNESS_DIR, "state", "QUEUE.json")
PIN_PATH = os.path.join(HARNESS_DIR, "state", "probes", "c9063_target_checkpoint.json")
PIN_REL = "harness/state/probes/c9063_target_checkpoint.json"
CONSUMERS = ("C-9009", "C-9016")


def _cards():
    with open(QUEUE_PATH, encoding="utf-8") as f:
        q = json.load(f)
    entries = q if isinstance(q, list) else q.get("cards", q.get("queue", []))
    return {c["id"]: c for c in entries if isinstance(c, dict) and "id" in c}


def test_consumers_dep_on_c9089_and_name_the_pin_path():
    """C-9009/C-9016 were the original consumer cards.  Once those cards
    are DONE/purged from QUEUE.json the wiring is proven by the pin
    artifact itself (test_live_pin_artifact_is_failclosed_valid) and by
    holdout_verdict._resolve_model_identity reading checkpoint_pin at
    compose time.  Skip the live-card assertion when the consumers are
    no longer active."""
    cards = _cards()
    active = {cid for cid in CONSUMERS if cid in cards}
    if not active:
        # Consumers completed and were purged; the pin artifact guard
        # (test_live_pin_artifact_is_failclosed_valid) covers the wiring.
        return
    for cid in CONSUMERS:
        c = cards.get(cid)
        if c is None:
            continue
        assert "C-9089" in (c.get("deps") or []), (
            cid + " must dep C-9089 so it cannot claim before the pin card is DONE, "
            "got deps=" + repr(c.get("deps"))
        )
        acc = " ".join(c.get("acceptance") or [])
        assert PIN_REL in acc, (
            cid + " acceptance must name the exact pin path " + PIN_REL + " as its target pin"
        )


def test_live_pin_artifact_is_failclosed_valid():
    assert os.path.isfile(PIN_PATH), "pin artifact missing: " + PIN_PATH
    with open(PIN_PATH, encoding="utf-8") as f:
        art = json.load(f)
    assert art.get("status") == "PINNED", repr(art.get("status"))
    for key in ("checkpoint_id", "sha256", "inventory_path", "selected_at_utc"):
        assert art.get(key), "pin missing required key " + key
    assert re.match(r"^[0-9a-f]{64}$", art["sha256"]), "pin sha256 malformed"
    assert art["checkpoint_id"].endswith("step_000097_adapter"), art["checkpoint_id"]
    assert set(art.get("consumer_cards") or ()) == set(CONSUMERS)
    assert art.get("selection_rule"), "pin must carry the stated deterministic rule"
    assert (
        art.get("weights_staged_mac_side") is False
    ), "weights are transport-blocked Mac-side; pin must say so, not guess"
    # the pin must cite REAL upstream artifacts, and the inventory must not be
    # a BLOCKED record (never guess a checkpoint when inventory says BLOCKED)
    inv_path = os.path.join(REPO_DIR, art["inventory_path"])
    man_path = os.path.join(REPO_DIR, art["manifest_path"])
    assert os.path.isfile(inv_path), "pin inventory_path missing: " + inv_path
    assert os.path.isfile(man_path), "pin manifest_path missing: " + man_path


def test_banked_pin_reproducible_from_live_c9068_artifacts():
    """Independent re-selection: the banked pin must equal a fresh run of the
    selector over the cited live artifacts (modulo selected_at_utc)."""
    with open(PIN_PATH, encoding="utf-8") as f:
        banked = json.load(f)
    sel = tc.select_target_from_c9068(
        os.path.join(REPO_DIR, banked["inventory_path"]),
        os.path.join(REPO_DIR, banked["manifest_path"]),
    )

    def _rel(p):
        return os.path.normpath(os.path.relpath(p, REPO_DIR))

    sel["inventory_path"] = _rel(sel["inventory_path"])
    sel["manifest_path"] = _rel(sel["manifest_path"])
    for key in (
        "checkpoint_id",
        "sha256",
        "box_path",
        "status",
        "card",
        "selection_rule",
        "staged_dir",
        "weights_sha_location",
        "weights_staged_mac_side",
        "inventory_path",
        "manifest_path",
        "candidates_considered",
    ):
        assert banked.get(key) == sel.get(
            key
        ), f"banked pin {key}={banked.get(key)!r} != fresh selection {sel.get(key)!r}"

"""Card C-10601: trainer staleness watchdog + auto-rearm warm-continue.

The standup repeatedly flagged "Training NOT RUNNING (trainer UNKNOWN
step=3 age=1685707s)" yet nothing re-armed training — the trainer idled for
days. This watchdog closes that gap: every tick it scans the trainer probe
(probes/trainer.json, the same instrument the standup reads); when the step
age exceeds STALE_STEP_AGE_S (1800s) or the trainer is NOT RUNNING, it
(1) fires ONE page (EVENTS.jsonl kind=trainer_stale_page, idempotent per
stale episode) and (2) auto-mints ONE warm-continue successor card per
stale episode pinned to the best banked champion sha
(BEST_CHECKPOINT.json), so training never idles.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

_HARNESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPTS = os.path.join(_HARNESS_DIR, "scripts")
_REPO_ROOT = os.path.dirname(_HARNESS_DIR)
for _p in (_HARNESS_DIR, _SCRIPTS, _REPO_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts import c10601_trainer_staleness_watchdog as W  # noqa: E402


def _write(path, obj):
    Path(path).write_text(json.dumps(obj, indent=1), encoding="utf-8")


class _Env:
    """Temp state dir with a trainer probe, events log, best-champion."""

    def __init__(self, probe=None, best=None, queue=None):
        self.dir = tempfile.mkdtemp(prefix="c10601_")
        self.state = Path(self.dir) / "state"
        self.state.mkdir(parents=True)
        (self.state / "probes").mkdir()
        _write(self.state / "probes" / "trainer.json", probe or {})
        _write(self.state / "BEST_CHECKPOINT.json", best or {})
        _write(self.state / "QUEUE.json", queue or {"seq": 10601, "cards": []})

    def events(self):
        p = self.state / "EVENTS.jsonl"
        return (
            [json.loads(ln) for ln in p.read_text().splitlines() if ln.strip()]
            if p.exists()
            else []
        )

    def queue(self):
        return json.loads((self.state / "QUEUE.json").read_text())


def _probe(status="unknown", summary="", age_s=None):
    return {
        "ts": "2026-11-01T00:00:00Z",
        "status": status,
        "summary": summary,
        "liveness": {"term": "eval_results_age"},
        **({"age_s": age_s} if age_s is not None else {}),
    }


def _best(sha="373b6e6dea3fa9e7b2a87fecb2b2fc455f4cdcc8d75ea59d554057b4992c2b3c", n_passes=18):
    return {
        "checkpoint": "/root/work/outputs/sft-27b-q38-v22-resume/checkpoints/step-1941/adapter",
        "n_passes": n_passes,
        "n_tasks": 18,
        "beats_base": True,
        "adapter_sha256": sha,
        "updated": "2026-10-26T06:55:00Z",
    }


class TriggerTests(unittest.TestCase):
    def test_fresh_running_trainer_no_fire(self):
        v = W.classify_staleness({"status": "running", "age_s": 100})
        self.assertFalse(v["stale"])

    def test_step_age_over_1800_fires(self):
        v = W.classify_staleness({"status": "running", "age_s": 1801})
        self.assertTrue(v["stale"])
        self.assertIn("step age", v["reason"])

    def test_not_running_fires_even_without_age(self):
        v = W.classify_staleness({"status": "not_running"})
        self.assertTrue(v["stale"])
        self.assertIn("not running", v["reason"])

    def test_unknown_with_huge_age_fires(self):
        v = W.classify_staleness({"status": "unknown", "age_s": 1685707})
        self.assertTrue(v["stale"])

    def test_fresh_unknown_does_not_fire(self):
        v = W.classify_staleness({"status": "unknown", "age_s": 60})
        self.assertFalse(v["stale"])

    def test_age_parsed_from_summary_when_field_absent(self):
        v = W.classify_staleness(
            {"status": "unknown", "summary": "UNKNOWN step=3 age=1685707s run=c9561-live-demo"}
        )
        self.assertTrue(v["stale"])
        self.assertEqual(v["age_s"], 1685707)


class WatchdogCycleTests(unittest.TestCase):
    def test_cycle_fires_page_and_mints_warm_continue_card(self):
        env = _Env(probe=_probe(status="unknown", age_s=1685707), best=_best())
        rep = W.watchdog_once(state_dir=str(env.state))
        self.assertTrue(rep["stale"])
        self.assertTrue(rep["fired"])
        # page landed in EVENTS with the stale evidence
        evs = [e for e in env.events() if e["kind"] == "trainer_stale_page"]
        self.assertEqual(len(evs), 1)
        self.assertEqual(evs[0]["age_s"], 1685707)
        # exactly one warm-continue card minted, pinned to champion sha
        cards = [c for c in env.queue()["cards"] if "warm-continue" in c.get("title", "").lower()]
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0]["adapter_sha256"], _best()["adapter_sha256"])
        self.assertEqual(cards[0]["lane"], "trainer-ops")
        self.assertEqual(cards[0]["status"], "ready")

    def test_idempotent_no_double_fire_within_same_stale_episode(self):
        env = _Env(probe=_probe(status="unknown", age_s=1685707), best=_best())
        W.watchdog_once(state_dir=str(env.state))
        rep2 = W.watchdog_once(state_dir=str(env.state))
        self.assertTrue(rep2["stale"])
        self.assertFalse(rep2["fired"])  # already fired this episode
        self.assertEqual(len([e for e in env.events() if e["kind"] == "trainer_stale_page"]), 1)
        self.assertEqual(len(env.queue()["cards"]), 1)

    def test_recovery_rereads_after_trainer_healthy_again(self):
        env = _Env(probe=_probe(status="unknown", age_s=1685707), best=_best())
        W.watchdog_once(state_dir=str(env.state))
        # trainer recovers: fresh, running
        _write(env.state / "probes" / "trainer.json", _probe(status="running", age_s=30))
        W.watchdog_once(state_dir=str(env.state))
        # stale again -> NEW episode fires again
        _write(env.state / "probes" / "trainer.json", _probe(status="unknown", age_s=999999))
        rep3 = W.watchdog_once(state_dir=str(env.state))
        self.assertTrue(rep3["fired"])
        self.assertEqual(len([e for e in env.events() if e["kind"] == "trainer_stale_page"]), 2)
        # C-10425 SKIP_DUPLICATE doctrine: the first warm-continue card is
        # still open (ready) -> no double-mint, flagged as duplicate instead.
        self.assertTrue(rep3["duplicate_card"])
        self.assertFalse(rep3["card_minted"])
        self.assertEqual(len(env.queue()["cards"]), 1)

    def test_new_card_mints_after_prior_card_resolved(self):
        env = _Env(probe=_probe(status="unknown", age_s=1685707), best=_best())
        W.watchdog_once(state_dir=str(env.state))
        # prior card gets resolved (reaped DONE)
        q = env.queue()
        q["cards"][0]["status"] = "done"
        _write(env.state / "QUEUE.json", q)
        # trainer recovers then goes stale again -> new episode, fresh mint
        _write(env.state / "probes" / "trainer.json", _probe(status="running", age_s=30))
        W.watchdog_once(state_dir=str(env.state))
        _write(env.state / "probes" / "trainer.json", _probe(status="unknown", age_s=888888))
        rep = W.watchdog_once(state_dir=str(env.state))
        self.assertTrue(rep["fired"])
        self.assertTrue(rep["card_minted"])
        self.assertEqual(len(env.queue()["cards"]), 2)

    def test_feature_card_title_with_warm_continue_does_not_block_mint(self):
        # RED (live-queue bug): the C-10601 *feature* card itself sits open in
        # the real QUEUE.json and its title contains "warm-continue" ("...
        # auto-rearm warm-continue from best champion ..."). The substring
        # dedupe falsely matched it, suppressing the ops card forever
        # (duplicate_card=true, card_minted=false). Its lane is trainer-ops
        # too, so the discriminator is the minted-card marker: only cards
        # carrying kind == "warm-continue" count as prior ops mints.
        feature_card = {
            "id": "C-10601",
            "title": "Trainer staleness watchdog: detect stale/absent "
            "SFT trainer (step age >1800s) and auto-rearm warm-continue from best "
            "champion so training never idles",
            "lane": "trainer-ops",
            "priority": 2,
            "status": "ready",
        }
        env = _Env(
            probe=_probe(status="unknown", age_s=1685707),
            best=_best(),
            queue={"seq": 10601, "cards": [feature_card]},
        )
        rep = W.watchdog_once(state_dir=str(env.state))
        self.assertTrue(rep["fired"])
        self.assertFalse(rep["duplicate_card"])
        self.assertTrue(rep["card_minted"])
        # the freshly minted ops card is the trainer-ops warm-continue, and
        # it coexists with the still-open feature card (queue grows 1 -> 2).
        wc = [
            c
            for c in env.queue()["cards"]
            if c.get("kind") == "warm-continue" and c.get("status") == "ready"
        ]
        self.assertEqual(len(wc), 1)
        self.assertEqual(len(env.queue()["cards"]), 2)

    def test_healthy_cycle_is_quiet(self):
        env = _Env(probe=_probe(status="running", age_s=45), best=_best())
        rep = W.watchdog_once(state_dir=str(env.state))
        self.assertFalse(rep["stale"])
        self.assertFalse(rep["fired"])
        self.assertEqual(env.events(), [])
        self.assertEqual(env.queue()["cards"], [])

    def test_missing_best_checkpoint_still_pages_but_flags_card_blocked(self):
        env = _Env(probe=_probe(status="unknown", age_s=1685707), best={})
        rep = W.watchdog_once(state_dir=str(env.state))
        self.assertTrue(rep["fired"])
        self.assertTrue(rep["card_mint_blocked"])
        self.assertEqual(env.queue()["cards"], [])  # no champion sha -> no bogus card


class CardContentTests(unittest.TestCase):
    def test_card_pins_champion_sha_and_checkpoint(self):
        env = _Env(probe=_probe(status="not_running"), best=_best())
        W.watchdog_once(state_dir=str(env.state))
        card = env.queue()["cards"][0]
        self.assertIn("warm-continue", card["title"].lower())
        self.assertEqual(card["adapter_sha256"], _best()["adapter_sha256"])
        self.assertEqual(card["checkpoint"], _best()["checkpoint"])
        self.assertTrue(card["acceptance"])
        self.assertEqual(card["priority"], 1)


if __name__ == "__main__":
    unittest.main()

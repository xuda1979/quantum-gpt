"""Unit tests: divide-and-conquer cards exist and are well-formed.

User mandate (2026-09-23): decompose the objective explicitly — by task
(14 zero-pass holdout tasks => per-task sub-cards), by file (682-file
200-line debt => tracked grinding card). Each sub-card must be real work
with a verifiable done-gate.
"""
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QUEUE = os.path.join(REPO, "harness", "state", "QUEUE.json")
HOLDOUT = os.path.join(REPO, "evals", "benchmarks", "sapo_promotion_holdout_v1_18.txt")


def _cards():
    q = json.load(open(QUEUE))
    return q if isinstance(q, list) else q.get("cards", [])


class TestDivideByTask:
    def test_per_task_cards_cover_ranked_zero_pass(self):
        cards = _cards()
        task_cards = [c for c in cards if str(c.get("id", "")).startswith("C-9640-")]
        assert len(task_cards) >= 14, "need one sub-card per zero-pass task"

    def test_each_task_card_has_done_gate(self):
        cards = _cards()
        for c in cards:
            if str(c.get("id", "")).startswith("C-9640-"):
                assert "done-gate" in c["title"], c["id"]
                assert "passes" in c["title"], c["id"]

    def test_task_cards_are_ready(self):
        cards = _cards()
        for c in cards:
            if str(c.get("id", "")).startswith("C-9640-"):
                assert c["status"] == "ready", c["id"]


class TestDivideByFile:
    def test_200line_debt_card_exists(self):
        cards = _cards()
        assert any(c.get("id") == "C-9641-200LINE-DEBT" for c in cards)

    def test_debt_card_gates_on_mandate_gate(self):
        cards = _cards()
        c = [c for c in cards if c.get("id") == "C-9641-200LINE-DEBT"][0]
        assert "sapo_mandate_gate.py" in c["title"]
        assert "Done-gate" in c["title"]


class TestQueueIntegrity:
    def test_no_duplicate_ids(self):
        ids = [c.get("id") for c in _cards()]
        assert len(ids) == len(set(ids))

    def test_holdout_file_still_18_tasks(self):
        lines = [l.strip() for l in open(HOLDOUT)
                 if l.strip() and not l.startswith("#")]
        assert len(lines) == 18

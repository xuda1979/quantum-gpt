"""Unit tests: compose_brief must not KeyError on cards missing acceptance.

Bug (2026-09-23): bare card["acceptance"] raised KeyError for every card
lacking the field — spawn_error 'acceptance' logged every tick, ZERO workers
spawned for hours. Fail-closed contract: malformed card -> brief carries a
MALFORMED note; well-formed card -> acceptance + gates rendered normally.
"""
import importlib.util
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QGH = os.path.join(REPO, "harness", "qgh.py")


def _load_qgh():
    spec = importlib.util.spec_from_file_location("qgh_under_test", QGH)
    m = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m


class TestComposeBriefFailClosed:
    def setup_method(self):
        self.qgh = _load_qgh()
        self.base = {
            "id": "X", "title": "t", "deps": [], "gates": [],
            "budget_min": 30, "lane": "fixer", "why": "because",
        }

    def test_missing_acceptance_does_not_raise(self):
        b = self.qgh.compose_brief("goal", dict(self.base))
        assert isinstance(b, str)

    def test_missing_acceptance_marks_malformed(self):
        b = self.qgh.compose_brief("goal", dict(self.base))
        assert "MALFORMED CARD" in b

    def test_empty_acceptance_marks_malformed(self):
        b = self.qgh.compose_brief("goal", dict(self.base, acceptance=[]))
        assert "MALFORMED CARD" in b

    def test_none_acceptance_marks_malformed(self):
        b = self.qgh.compose_brief("goal", dict(self.base, acceptance=None))
        assert "MALFORMED CARD" in b

    def test_normal_card_renders_acceptance(self):
        b = self.qgh.compose_brief(
            "goal", dict(self.base, acceptance=["criterion one", "criterion two"]))
        assert "- criterion one" in b
        assert "MALFORMED" not in b

    def test_normal_card_renders_gates(self):
        b = self.qgh.compose_brief(
            "goal", dict(self.base, acceptance=["c"], gates=["unit-tests"]))
        assert "unit-tests" in b

    def test_no_gates_shows_placeholder(self):
        b = self.qgh.compose_brief("goal", dict(self.base, acceptance=["c"]))
        assert "none (acceptance still required)" in b

    def test_gates_missing_key_no_keyerror(self):
        card = dict(self.base)
        card.pop("gates", None)
        card["acceptance"] = ["c"]
        b = self.qgh.compose_brief("goal", card)
        assert isinstance(b, str)

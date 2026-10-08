"""Unit tests: dp4 is the ONLY judge (user mandate 2026-09-22).

Covers the sapo_judge_mac_watcher change that removed the Zhipu GLM-5.3-Flash
fallback. The watcher must:
  1. never call any fallback model when dp4 fails (fail-closed instead),
  2. stage the dp4 error response so the failure is visible downstream,
  3. keep call_zhipu_fallback as a fail-closed stub (error, never a score).
"""
import importlib.util
import json
import os
from unittest import mock

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WATCHER = os.path.join(REPO, "scripts", "sapo_judge_mac_watcher.py")


def _load_watcher():
    spec = importlib.util.spec_from_file_location("sapo_watcher_under_test", WATCHER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestDp4OnlyJudge:
    """dp4-only judge mandate."""

    def setup_method(self):
        self.w = _load_watcher()

    def test_zhipu_fallback_is_fail_closed_stub(self):
        """The old fallback must return an explicit error, never a score."""
        resp = self.w.call_zhipu_fallback("{}")
        parsed = json.loads(resp)
        assert "error" in parsed
        assert "dp4" in parsed["error"]["message"]
        assert "content" not in parsed

    def test_watcher_source_has_no_zhipu_call_in_tick(self):
        """The tick loop must not route to a fallback judge on dp4 failure."""
        src = open(WATCHER).read()
        assert "call_zhipu_fallback(body)" not in src, (
            "tick() must not call the zhipu fallback; dp4 is the only judge"
        )
        assert "FAIL-CLOSED" in src

    def test_dp4_failure_stages_error_not_substitute(self):
        """End-to-end tick behavior: dp4 failure -> error response staged.

        Mocks the box transport so no daemon is needed. The staged response
        must be the dp4 error itself, and call_zhipu_fallback must NOT be
        invoked.
        """
        w = self.w
        staged = {}
        dp4_error = json.dumps({"error": {"message": "boom", "type": "x"}})

        with mock.patch.object(w, "list_requests", return_value=["/q/req_abc.json"]), \
             mock.patch.object(w, "has_resp", return_value=False), \
             mock.patch.object(w, "fetch", return_value='{"model":"dp4","messages":[]}'), \
             mock.patch.object(w, "call_dp4", return_value=dp4_error), \
             mock.patch.object(w, "call_zhipu_fallback", side_effect=AssertionError("must not be called")) as zf, \
             mock.patch.object(w, "stage", side_effect=lambda p, d: staged.__setitem__(p, d)), \
             mock.patch.object(w, "cleanup_orphans"):
            n = w.tick()

        assert n == 1
        expected = self.w.resp_for("/q/req_abc.json")
        assert staged[expected] == dp4_error
        zf.assert_not_called()

    def test_dp4_success_passes_through(self):
        """dp4 success still stages the dp4 response unchanged."""
        w = self.w
        staged = {}
        dp4_ok = json.dumps({"content": [{"type": "text", "text": "scores ok"}]})

        with mock.patch.object(w, "list_requests", return_value=["/q/req_1.json"]), \
             mock.patch.object(w, "has_resp", return_value=False), \
             mock.patch.object(w, "fetch", return_value='{"model":"dp4","messages":[]}'), \
             mock.patch.object(w, "call_dp4", return_value=dp4_ok), \
             mock.patch.object(w, "stage", side_effect=lambda p, d: staged.__setitem__(p, d)), \
             mock.patch.object(w, "cleanup_orphans"):
            n = w.tick()

        assert n == 1
        expected = self.w.resp_for("/q/req_1.json")
        assert staged[expected] == dp4_ok

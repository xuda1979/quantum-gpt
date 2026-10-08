"""TDD for the vLLM rollout client (CEO Tier-1)."""

from __future__ import annotations

import json
import sys
import urllib.error
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.vllm_rollout_client import (  # noqa: E402
    VllmRolloutClient,
    VllmUnavailable,
    generate_with_fallback,
)


class _FakeResp:
    def __init__(self, body: bytes, status: int = 200):
        self._body, self.status = body, status

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _patch_opener(monkeypatch, body):
    """Patch the client's opener construction so opener.open returns _FakeResp."""
    import training.vllm_rollout_client as mod

    class FakeOpener:
        def open(self, req, timeout=None):
            return _FakeResp(body)

    monkeypatch.setattr(mod.urllib.request, "build_opener", lambda handler=None: FakeOpener())


def test_generate_batch_returns_n_completions(monkeypatch):
    client = VllmRolloutClient("http://x")
    body = json.dumps({"choices": [{"text": "a"}, {"text": "b"}, {"text": "c"}]}).encode()
    calls = {}
    import training.vllm_rollout_client as mod

    class CaptureOpener:
        def open(self, req, timeout=None):
            calls["data"] = json.loads(req.data)
            return _FakeResp(body)

    monkeypatch.setattr(mod.urllib.request, "build_opener", lambda handler=None: CaptureOpener())
    outs = client.generate_batch("PROMPT", 3, 64, 1.0)
    assert outs == ["a", "b", "c"]
    assert calls["data"]["n"] == 3 and calls["data"]["prompt"] == "PROMPT"


def test_server_error_raises_unavailable(monkeypatch):
    client = VllmRolloutClient("http://x")

    import training.vllm_rollout_client as mod

    class FailOpener:
        def open(self, req, timeout=None):
            raise urllib.error.URLError("conn refused")

    monkeypatch.setattr(mod.urllib.request, "build_opener", lambda handler=None: FailOpener())
    with pytest.raises(VllmUnavailable):
        client.generate_batch("P", 1, 8, 1.0)


def test_wrong_count_raises(monkeypatch):
    client = VllmRolloutClient("http://x")
    body = json.dumps({"choices": [{"text": "only-one"}]}).encode()
    import training.vllm_rollout_client as mod

    class FakeOpener:
        def open(self, req, timeout=None):
            return _FakeResp(body)

    monkeypatch.setattr(mod.urllib.request, "build_opener", lambda handler=None: FakeOpener())
    with pytest.raises(VllmUnavailable):
        client.generate_batch("P", 3, 8, 1.0)


def test_fallback_used_when_vllm_down():
    client = VllmRolloutClient("http://x")
    client.is_up = lambda force=False: False
    outs, engine = generate_with_fallback(
        client, "P", 2, 8, 1.0, fallback_fn=lambda p, n, m, t: ["hf1", "hf2"]
    )
    assert engine == "hf" and outs == ["hf1", "hf2"]


def test_vllm_used_when_up(monkeypatch):
    client = VllmRolloutClient("http://x")
    client.is_up = lambda force=False: True
    body = json.dumps({"choices": [{"text": "v1"}, {"text": "v2"}]}).encode()
    import training.vllm_rollout_client as mod

    class FakeOpener:
        def open(self, req, timeout=None):
            return _FakeResp(body)

    monkeypatch.setattr(mod.urllib.request, "build_opener", lambda handler=None: FakeOpener())
    outs, engine = generate_with_fallback(
        client, "P", 2, 8, 1.0, fallback_fn=lambda p, n, m, t: ["hf1", "hf2"]
    )
    assert engine == "vllm" and outs == ["v1", "v2"]


def test_zero_n_short_circuits():
    client = VllmRolloutClient("http://x")
    assert client.generate_batch("P", 0, 8, 1.0) == []


def test_health_cache_holds_10s_force_bypasses_and_fails_closed(monkeypatch):
    """is_up health-cache semantics (audit 2026-09-01): result cached 10s;
    force re-probes; a probe failure is cached as False (fail-closed)."""
    import training.vllm_rollout_client as mod

    hits: list = []

    def ok_probe(req, timeout=None):
        hits.append(1)
        return _FakeResp(b"{}", status=200)

    class _FakeOpener:
        def open(self, req, timeout=None):
            return ok_probe(req, timeout=timeout)
    monkeypatch.setattr(mod, "opener_factory", lambda: _FakeOpener())
    t = {"now": 1000.0}
    monkeypatch.setattr(mod.time, "time", lambda: t["now"])

    client = VllmRolloutClient("http://x")
    assert client.is_up() is True
    assert client.is_up() is True
    assert client.is_up() is True
    assert len(hits) == 1  # two repeat calls within 10s hit the cache

    t["now"] = 1011.0  # cache expired
    assert client.is_up() is True
    assert len(hits) == 2

    def down_probe(req, timeout=None):
        hits.append(1)
        raise urllib.error.URLError("down")

    class _FakeOpener2:
        def open(self, req, timeout=None):
            return down_probe(req, timeout=timeout)
    monkeypatch.setattr(mod, "opener_factory", lambda: _FakeOpener2())
    t["now"] = 1021.0
    assert client.is_up() is False  # probe failure cached as False
    t["now"] = 1029.0  # still inside the 10s window after the failed probe
    assert client.is_up() is False
    assert len(hits) == 3

    t["now"] = 1032.0  # cache expired -> re-probe (still down)
    assert client.is_up() is False
    assert len(hits) == 4

    t["now"] = 1040.0
    monkeypatch.setattr(mod, "opener_factory", lambda: _FakeOpener())
    assert client.is_up(force=True) is True  # force bypasses the cache
    assert len(hits) == 5

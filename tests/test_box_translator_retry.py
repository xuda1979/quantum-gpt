"""TDD: box translator must retry transient dp4-upstream failures so a
squid/proxy blip becomes a retried success (NOT a 502 → dark step).

RED first: with a flaky upstream that fails twice then succeeds, the retry
helper must return the success and the caller (handler) must emit 200, not
502. Class-extinction for the recurring dark steps (s30/35/38/39/46)."""
import json
from unittest.mock import patch
from scripts import box_anthropic_translator as T

from http.server import BaseHTTPRequestHandler
import io


def _resp(status, payload):
    data = json.dumps(payload).encode()
    return (status, data)


class _FlakyOpener:
    """Mimics urllib opener that fails `fail_n` times then succeeds."""
    def __init__(self, fail_n=2):
        self.fail_n = fail_n
        self.calls = 0

    def open(self, req, timeout=None):
        self.calls += 1
        if self.calls <= self.fail_n:
            raise OSError("transient proxy CONNECT refused")
        class _R:
            def read(self):
                return json.dumps({"choices": [{"message": {"content": "ok"}}],
                                   "id": "x", "usage": {}}).encode()
            def __enter__(self):
                return self
            def __exit__(self, *exc):
                return False
        return _R()


def _make_handler(flaky):
    handler = T.Handler.__new__(T.Handler)
    handler.path = "/v1/messages"
    handler.headers = {"Content-Length": "0"}
    handler.rfile = io.BytesIO(b"{}")
    handler.wfile = io.BytesIO()
    handler.flaky = flaky
    return handler


def test_upstream_retry_recovers_transient_failure():
    """Two transient failures then success -> helper returns (200, success)."""
    opener = _FlakyOpener(fail_n=2)
    req_body = json.dumps({
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 8,
    }).encode()
    status, data, info = T._open_upstream_with_retry(
        url="http://x/v1/chat/completions",
        body=req_body,
        headers={},
        opener=opener,
        max_attempts=3,
        base_delay=0.001,
    )
    assert status == 200, f"expected 200 got {status}: {data}"
    parsed = json.loads(data)
    # _open_upstream_with_retry returns the RAW upstream (OpenAI) body:
    # {"choices":[{"message":{"content":"ok"}}]} — do_POST translates it.
    assert parsed["choices"][0]["message"]["content"] == "ok"
    assert info["retries"] == 3, f"expected 3 retries recorded, got {info}"
    assert info["last_error"] is None
    assert opener.calls == 3, f"expected 3 calls (2 fail + 1 ok), got {opener.calls}"


def test_upstream_retry_gives_up_then_502():
    """Persistent failure -> 502 after max_attempts (fail-closed, never a silent 0)."""
    opener = _FlakyOpener(fail_n=999)
    status, data, info = T._open_upstream_with_retry(
        url="http://x", body=b"{}", headers={}, opener=opener,
        max_attempts=2, base_delay=0.001,
    )
    assert status >= 500, f"expected 5xx got {status}"
    assert info["last_error"] is not None, f"expected last_error on 502, got {info}"
    assert opener.calls == 2, f"expected exactly 2 attempts, got {opener.calls}"


def test_no_failure_calls_once():
    """Healthy upstream -> success on first attempt (no extra latency)."""
    opener = _FlakyOpener(fail_n=0)
    status, data, info = T._open_upstream_with_retry(
        url="http://x", body=b"{}", headers={}, opener=opener,
        max_attempts=3, base_delay=0.001,
    )
    assert status == 200
    assert opener.calls == 1, f"expected 1 call, got {opener.calls}"

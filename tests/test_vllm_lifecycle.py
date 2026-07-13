"""Unit tests for scripts/vllm_lifecycle.py.

We stand up a tiny in-process HTTP server that emulates the vLLM lifecycle
endpoints (/v1/models, /v1/sleep, /v1/wake_up, /v1/load_lora_adapter) so the
helper can be exercised end-to-end without a real vLLM. We also test the
fallback path (endpoints returning 404) and transport errors.
"""

from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

import pytest

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "vllm_lifecycle.py"


class _FakeVLLM:
    """Minimal vLLM-like HTTP server with controllable endpoint support."""

    def __init__(
        self,
        *,
        supports_sleep: bool,
        supports_load_lora: bool,
        served_name: str = "qwen36-27b-rl-distill",
    ):
        self.supports_sleep = supports_sleep
        self.supports_load_lora = supports_load_lora
        self.served_name = served_name
        self.is_sleeping = False
        self.loaded_loras: dict[str, str] = {}
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.port = 0

    def start(self) -> None:
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a, **k):  # silence
                pass

            def _send(self, code: int, body: dict | None = None) -> None:
                data = b"{}" if body is None else json.dumps(body).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):  # noqa: N802
                path = urlparse(self.path).path
                if path == "/v1/models":
                    if outer.is_sleeping:
                        self._send(503, {"error": "sleeping"})
                        return
                    data = [{"id": outer.served_name, "object": "model"}]
                    for name in outer.loaded_loras:
                        data.append({"id": name, "object": "model"})
                    self._send(200, {"object": "list", "data": data})
                    return
                self._send(404)

            def do_POST(self):  # noqa: N802
                path = urlparse(self.path).path
                length = int(self.headers.get("Content-Length", "0") or "0")
                raw = self.rfile.read(length) if length else b"{}"
                try:
                    body = json.loads(raw or b"{}")
                except Exception:
                    body = {}
                if path == "/v1/sleep":
                    if not outer.supports_sleep:
                        self._send(404)
                        return
                    outer.is_sleeping = True
                    self._send(200, {"ok": True})
                    return
                if path == "/v1/wake_up":
                    if not outer.supports_sleep:
                        self._send(404)
                        return
                    outer.is_sleeping = False
                    self._send(200, {"ok": True})
                    return
                if path == "/v1/load_lora_adapter":
                    if not outer.supports_load_lora:
                        self._send(404)
                        return
                    name = body.get("lora_name", "")
                    path_ = body.get("lora_local_path", "")
                    if not name or not path_:
                        self._send(400, {"error": "missing fields"})
                        return
                    outer.loaded_loras[name] = path_
                    self._send(200, {"ok": True})
                    return
                self._send(404)

        self._server = HTTPServer(("127.0.0.1", 0), Handler)
        self.port = self._server.server_address[1]
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._server:
            self._server.shutdown()
            self._server.server_close()
        if self._thread:
            self._thread.join(timeout=5)

    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HELPER), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


@pytest.fixture
def fake_vllm_factory():
    created: list[_FakeVLLM] = []

    def _make(**kw):
        srv = _FakeVLLM(**kw)
        srv.start()
        created.append(srv)
        # tiny grace period so the socket is accepting
        time.sleep(0.05)
        return srv

    yield _make

    for srv in created:
        srv.stop()


def test_probe_detects_sleep_and_load_lora_support(fake_vllm_factory):
    srv = fake_vllm_factory(supports_sleep=True, supports_load_lora=True)
    r = _run("--base-url", srv.url(), "--api-key", "k", "probe")
    assert r.returncode == 0, r.stderr
    payload = json.loads(r.stdout)
    assert payload["supports_sleep"] is True
    assert payload["supports_load_lora"] is True


def test_probe_reports_unsupported_when_404(fake_vllm_factory):
    srv = fake_vllm_factory(supports_sleep=False, supports_load_lora=False)
    r = _run("--base-url", srv.url(), "--api-key", "k", "probe")
    assert r.returncode == 0, r.stderr
    payload = json.loads(r.stdout)
    assert payload["supports_sleep"] is False
    assert payload["supports_load_lora"] is False


def test_sleep_then_wake_roundtrip(fake_vllm_factory):
    srv = fake_vllm_factory(supports_sleep=True, supports_load_lora=True)
    r = _run(
        "--base-url", srv.url(), "--api-key", "k", "sleep", "--level", "1", "--settle-seconds", "0"
    )
    assert r.returncode == 0, r.stderr
    assert srv.is_sleeping is True
    # While sleeping, /v1/models returns 503 so wait-ready would fail; wake it.
    r2 = _run("--base-url", srv.url(), "--api-key", "k", "wake", "--timeout", "10")
    assert r2.returncode == 0, r2.stderr
    assert srv.is_sleeping is False


def test_sleep_unsupported_returns_fallback_exit_code(fake_vllm_factory):
    srv = fake_vllm_factory(supports_sleep=False, supports_load_lora=True)
    r = _run("--base-url", srv.url(), "--api-key", "k", "sleep", "--level", "1")
    assert r.returncode == 2, r.stderr


def test_load_lora_registers_adapter_name(fake_vllm_factory, tmp_path):
    srv = fake_vllm_factory(supports_sleep=True, supports_load_lora=True)
    adapter_dir = tmp_path / "adapter"
    adapter_dir.mkdir()
    r = _run(
        "--base-url",
        srv.url(),
        "--api-key",
        "k",
        "load-lora",
        "--lora-name",
        "rl_distill_latest",
        "--lora-path",
        str(adapter_dir),
    )
    assert r.returncode == 0, r.stderr
    payload = json.loads(r.stdout)
    assert payload["registered"] is True
    assert "rl_distill_latest" in srv.loaded_loras


def test_load_lora_unsupported_returns_fallback_exit_code(fake_vllm_factory, tmp_path):
    srv = fake_vllm_factory(supports_sleep=True, supports_load_lora=False)
    r = _run(
        "--base-url",
        srv.url(),
        "--api-key",
        "k",
        "load-lora",
        "--lora-name",
        "rl_distill_latest",
        "--lora-path",
        str(tmp_path),
    )
    assert r.returncode == 2, r.stderr


def test_wait_ready_succeeds_when_served_name_present(fake_vllm_factory):
    srv = fake_vllm_factory(
        supports_sleep=True, supports_load_lora=True, served_name="qwen36-35b-rl-distill"
    )
    r = _run(
        "--base-url",
        srv.url(),
        "--api-key",
        "k",
        "wait-ready",
        "--served-name",
        "qwen36-35b-rl-distill",
        "--poll-seconds",
        "0.2",
        "--timeout",
        "10",
    )
    assert r.returncode == 0, r.stderr


def test_wait_ready_times_out_when_served_name_absent(fake_vllm_factory):
    srv = fake_vllm_factory(
        supports_sleep=True, supports_load_lora=True, served_name="qwen36-35b-rl-distill"
    )
    r = _run(
        "--base-url",
        srv.url(),
        "--api-key",
        "k",
        "wait-ready",
        "--served-name",
        "not-the-real-name",
        "--poll-seconds",
        "0.1",
        "--timeout",
        "2",
    )
    assert r.returncode == 3, r.stderr


def test_transport_error_returns_exit_3():
    # Nothing listening on this port -> connection refused.
    r = _run("--base-url", "http://127.0.0.1:1", "--api-key", "k", "probe", "--timeout", "2")
    assert r.returncode == 3

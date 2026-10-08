"""TDD (2026-08-27, JUDGE BRIDGE lane): the training box has no route to the
Huanxin dp4 subscription (its DNS maps aihuanxin.cn to an internal gateway
without our route; the Mac's public route works). The bridge keeps the trainer
unchanged: --judge-dp4-endpoint points at the box-local bridge server, which
stages the trainer's Anthropic /v1/messages call as a request file; a Mac-side
watcher polls the queue via the daemon, calls the real dp4 proxy, and stages
the response file. Fail-closed: timeout -> Anthropic-shaped 504 (judge-absent).

Hermetic tests only (no network): localhost HTTP + tmp queue dirs.
"""

from __future__ import annotations

import json
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.sapo_judge_bridge import (
    Handler,
    parse_args,
    write_atomic,
)

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


class _BridgeServer(ThreadingHTTPServer):
    def __init__(self, queue_dir: Path, judge_timeout: float = 30.0):
        super().__init__(("127.0.0.1", 0), Handler)
        self.queue_dir = str(queue_dir)
        self.judge_timeout = judge_timeout


@pytest.fixture()
def bridge(tmp_path):
    queue = tmp_path / "queue"
    queue.mkdir()
    server = _BridgeServer(queue, judge_timeout=15.0)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    yield server
    server.shutdown()
    server.server_close()


def _post(port, body):
    import urllib.request

    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/v1/messages",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


# ---------------------------------------------------------------------------
# write_atomic
# ---------------------------------------------------------------------------


def test_write_atomic_replaces_file(tmp_path):
    p = tmp_path / "x.json"
    write_atomic(str(p), '{"a":1}')
    write_atomic(str(p), '{"a":2}')
    assert json.loads(p.read_text()) == {"a": 2}
    assert not (tmp_path / "x.json.tmp").exists()


# ---------------------------------------------------------------------------
# bridge server contract
# ---------------------------------------------------------------------------


def test_bridge_health(bridge):
    import urllib.request

    with urllib.request.urlopen(
        f"http://127.0.0.1:{bridge.server_address[1]}/health", timeout=5
    ) as r:
        body = json.loads(r.read().decode())
    assert body.get("ok") is True


def test_bridge_exchange_roundtrip(bridge):
    """POST /v1/messages stages a req file; when the watcher stages the resp
    file the bridge relays it verbatim and cleans both files."""
    port = bridge.server_address[1]
    payload = {"model": "dp4", "messages": [{"role": "user", "content": "x"}], "max_tokens": 8}

    def deliver_resp():
        # find the staged req file
        for _ in range(50):
            reqs = list(Path(bridge.queue_dir).glob("req_*.json"))
            if reqs:
                rid = reqs[0].stem[len("req_") :]
                resp = {
                    "id": "msg_x",
                    "content": [{"type": "text", "text": '{"candidate_1": {"correctness": 0.8}}'}],
                }
                write_atomic(str(Path(bridge.queue_dir) / (f"resp_{rid}.json")), json.dumps(resp))
                return
            time.sleep(0.1)

    t = threading.Thread(target=deliver_resp, daemon=True)
    t.start()
    status, body = _post(port, payload)
    assert status == 200
    assert body["id"] == "msg_x"
    assert body["content"][0]["text"].startswith('{"candidate_1"')
    # queue is clean after the exchange
    assert not list(Path(bridge.queue_dir).glob("req_*.json"))
    assert not list(Path(bridge.queue_dir).glob("resp_*.json"))


def test_bridge_timeout_fail_closed(tmp_path):
    """No watcher -> the bridge returns an Anthropic-shaped 504 after the
    judge_timeout and removes the staged request (fail-closed, no hang)."""
    queue = tmp_path / "queue"
    queue.mkdir()
    server = _BridgeServer(queue, judge_timeout=2.0)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        status, body = _post(server.server_address[1], {"model": "dp4"})
        assert status == 504
        assert body.get("error", {}).get("type") == "bridge_timeout"
    finally:
        server.shutdown()
        server.server_close()
    assert not list(queue.glob("req_*.json"))


def test_bridge_rejects_invalid_json(bridge):
    import urllib.request

    port = bridge.server_address[1]
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/v1/messages",
        data=b"not-json",
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=5)
        pytest.fail("expected HTTPError")
    except urllib.error.HTTPError as e:
        assert e.code == 400


# ---------------------------------------------------------------------------
# trainer dp4 client must bypass the box's env proxy (squid swallows localhost)
# ---------------------------------------------------------------------------


def test_dp4_client_bypasses_env_proxy(monkeypatch, tmp_path):
    """The trainer runs on the box where http_proxy is a squid that 403s
    localhost. _model_batch_dim_scores_dp4 must use a no-proxy opener so the
    box-local bridge is reachable. Pin it: set http_proxy to a dead port and
    serve a valid Anthropic batch-judge response on localhost -> the call must
    still succeed."""
    from training.grpo_trainer import _model_batch_dim_scores_dp4

    # dead proxy: if the client honors it, the call fails
    monkeypatch.setenv("http_proxy", "http://127.0.0.1:1")
    monkeypatch.setenv("https_proxy", "http://127.0.0.1:1")
    monkeypatch.setenv("no_proxy", "")  # no_proxy must NOT be required

    class _Fake(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):
            length = int(self.headers.get("Content-Length") or 0)
            self.rfile.read(length)
            resp = json.dumps(
                {
                    "id": "msg",
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {
                                    "candidate_1": {
                                        "correctness": 0.8,
                                        "runnability": 0.9,
                                        "result_correctness": 0.7,
                                        "efficiency": 0.6,
                                        "quality": 0.8,
                                    }
                                }
                            ),
                        }
                    ],
                }
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)

    server = ThreadingHTTPServer(("127.0.0.1", 0), _Fake)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        scores = _model_batch_dim_scores_dp4(
            ["def f(): pass", "def g(): pass"],
            ["tests passed: False; failures: none"] * 2,
            {"task_id": "t", "meta": {"description": "x"}},
            endpoint=f"http://127.0.0.1:{server.server_address[1]}",
            model="dp4",
            max_tokens=64,
        )
    finally:
        server.shutdown()
        server.server_close()
    assert scores is not None
    # candidate_1 scores 0.8, candidate_2 scores absent-dims (fail-closed);
    # presentation order is randomized per call (2026-09-01), so the parsed
    # 0.8 must land on the ORIGINAL index that held slot 1 — exactly one of
    # the two returned cells carries 0.8 and the other is judge-absent.
    scored = [v.get("correctness") for v in scores.values()]
    assert scored.count(0.8) == 1, "the single answered candidate must remap exactly once"
    assert scored.count(None) == 1, "the unanswered candidate stays judge-absent"


def test_bridge_parse_args_defaults():
    args = parse_args(["--queue-dir", "/tmp/q"])
    assert args.port == 56237
    assert args.judge_timeout == 290.0


# ---------------------------------------------------------------------------
# Mac watcher (scripts/sapo_judge_mac_watcher.py) — hermetic unit tests
# ---------------------------------------------------------------------------


def test_watcher_tick_processes_request(monkeypatch, tmp_path):
    """One tick: a req without resp is fetched, posted to dp4, and the resp is
    staged back — with the watcher error paths fail-closed."""
    import scripts.sapo_judge_mac_watcher as W

    calls = {"execs": [], "dp4_body": None}
    anthropic_resp = json.dumps(
        {"id": "m", "content": [{"type": "text", "text": '{"candidate_1": {"correctness": 0.9}}'}]}
    )

    def fake_daemon(script):
        calls["execs"].append(script)
        if script.startswith("ls "):
            import base64 as _b64

            return _b64.b64encode(b"/q/req_abc123.json\n").decode()
        if script.startswith("base64 -w0"):
            import base64 as _b64

            return _b64.b64encode(b'{"model":"dp4","messages":[]}').decode()
        if "[ -f " in script:
            return ""  # no resp yet
        if "echo " in script and "| base64 -d >" in script:
            return ""  # staging ok
        if script.startswith("cd "):
            return ""
        return ""

    def fake_dp4(body_text):
        calls["dp4_body"] = body_text
        return anthropic_resp

    monkeypatch.setattr(W, "BOX_QUEUE", "/q")
    monkeypatch.setattr(W, "daemon_exec", fake_daemon)
    monkeypatch.setattr(W, "call_dp4", fake_dp4)
    monkeypatch.setattr(W, "log", lambda *a: None)

    assert W.tick() == 1
    assert calls["dp4_body"] == '{"model":"dp4","messages":[]}'
    staged = [c for c in calls["execs"] if "base64 -d >" in c]
    assert len(staged) == 1
    assert "resp_abc123.json" in staged[0]


def test_watcher_skips_when_resp_exists(monkeypatch):
    import scripts.sapo_judge_mac_watcher as W

    def fake_daemon(script):
        if script.startswith("ls "):
            return "/q/req_abc.json\n"
        if "[ -f " in script:
            return "yes"
        if script.startswith("cd "):
            return ""
        return ""

    monkeypatch.setattr(W, "BOX_QUEUE", "/q")
    monkeypatch.setattr(W, "daemon_exec", fake_daemon)
    monkeypatch.setattr(W, "log", lambda *a: None)
    posted = []
    monkeypatch.setattr(W, "call_dp4", lambda b: posted.append(b) or "")
    assert W.tick() == 0
    assert posted == []


def test_watcher_call_dp4_fail_closed(monkeypatch):
    """An unreachable dp4 proxy must produce an Anthropic-shaped error body —
    never an empty string (empty resp = corrupt file on the box)."""
    import scripts.sapo_judge_mac_watcher as W

    monkeypatch.setattr(W, "DP4_PROXY", "http://127.0.0.1:1")  # dead port
    body = W.call_dp4('{"model":"dp4","messages":[]}', timeout_s=3)
    parsed = json.loads(body)
    assert isinstance(parsed.get("error"), dict)
    assert parsed["error"]["type"] == "watcher_error"

    # invalid request JSON is also fail-closed, not silent
    body2 = W.call_dp4("not json")
    assert json.loads(body2)["error"]["type"] == "watcher_error"


def test_watcher_fetch_survives_console_line_wrap(monkeypatch):
    """The huanxin console transport wraps long output lines mid-word; the
    fetch must recover exact bytes via base64 whitespace-stripping (the class
    that produced 'can\\ndidate_1' corruptions)."""
    import base64 as _b64

    import scripts.sapo_judge_mac_watcher as W

    original = '{"model": "dp4", "content": "Reply with ONLY: {\\"candidate_1\\": {\\"correctness\\": 0.9}}"}'
    b64 = _b64.b64encode(original.encode()).decode()
    wrapped = "\n".join(b64[i : i + 57] for i in range(0, len(b64), 57))  # sim wrap

    def fake_daemon(script):
        assert script.startswith("base64 -w0")
        return wrapped

    monkeypatch.setattr(W, "daemon_exec", fake_daemon)
    assert W.fetch("/q/req_x.json") == original


def test_watcher_list_requests_survives_console_wrap(monkeypatch):
    """2026-08-27 LIVE BUG: the console wrapped the 112-char ls path
    mid-filename and the old '.endswith(.json)' filter dropped every request —
    both step-1/step-2 judge calls timed out judge-absent. The listing must
    base64 round-trip and recover the exact paths from wrapped output."""
    import base64 as _b64

    import scripts.sapo_judge_mac_watcher as W

    paths = (
        "/root/work/software/quantum-gpt/outputs/sapo-27b-ai-20260827T153731Z/"
        "judge_bridge/req_ae6fa368abd240578b6321cef281d7af.json\n"
    )
    b64 = _b64.b64encode(paths.encode()).decode()
    wrapped = "\n".join(b64[i : i + 53] for i in range(0, len(b64), 53))  # sim wrap

    def fake_daemon(script):
        assert "| base64 -w0" in script
        return wrapped

    monkeypatch.setattr(W, "BOX_QUEUE", "/q")
    monkeypatch.setattr(W, "daemon_exec", fake_daemon)
    got = W.list_requests()
    assert len(got) == 1
    assert got[0].endswith("req_ae6fa368abd240578b6321cef281d7af.json")

    # empty queue -> []
    monkeypatch.setattr(W, "daemon_exec", lambda s: "")
    assert W.list_requests() == []

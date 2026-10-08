#!/usr/bin/env python3
"""Box-side Anthropic->dp4 translator (B-044, 2026-09-03).

The trainer speaks Anthropic /v1/messages; the dp4 subscription speaks
OpenAI /v1/chat/completions. This tiny box-local translator (127.0.0.1:56238)
converts between the two and calls dp4 DIRECTLY through the box squid proxy
with the JWT at /root/.dp4_jwt. Replaces the whole Mac bridge+watcher relay:
judge latency drops from minutes to the dp4 call itself."""
"""Box-side Anthropic->dp4 translator (B-044, 2026-09-03).

FIX B-TR (2026-09-07, class-extinction for recurring dark steps s30/35/38/39/46):
the dp4 upstream call now RETRIES transient squid/proxy failures with exponential
backoff (mirrors B-046 on the trainer side) so a single proxy blip becomes a
retried success instead of a 502 -> judge-absent -> dark step. JWT load at import
is also made resilient (no hard crash when the JWT is absent, e.g. local test env).
"""
import json
import os
import time
import urllib.request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

JWT_PATH = os.environ.get("DP4_JWT_PATH", "/root/.dp4_jwt")
try:
    with open(JWT_PATH) as _f:
        JWT = _f.read().strip()
except Exception:  # resilient import (local test / no JWT yet); main() re-checks
    JWT = ""
UPSTREAM = os.environ.get(
    "DP4_UPSTREAM",
    "https://aihuanxin.cn/kunlun/ingress/api/68b329/5c1bbb4620fc40eea9712a9771cece1b/"
    "ai-69be0918a51147689dc012f2d8b44fda/service-496501784fc44902b73b7bf90ddd88a4",
)

# B-TR: bounded retry for transient upstream failures (dp4 via squid proxy).
MAX_UPSTREAM_ATTEMPTS = int(os.environ.get("DP4_MAX_ATTEMPTS", "3"))
BASE_RETRY_DELAY = float(os.environ.get("DP4_RETRY_BASE_DELAY", "0.8"))
UPSTREAM_TIMEOUT = int(os.environ.get("DP4_UPSTREAM_TIMEOUT", "280"))


def _open_upstream_with_retry(url, headers, body, opener, *,
                              max_attempts=MAX_UPSTREAM_ATTEMPTS,
                              base_delay=BASE_RETRY_DELAY,
                              timeout=UPSTREAM_TIMEOUT):
    """Call dp4 upstream with bounded retry+exponential backoff on transient
    failures. Returns (status_int, body_bytes, info_dict) where info_dict has
    ``retries`` (attempts used), ``latency_s``, and ``last_error`` — the
    evidence needed to root-cause dark steps. On persistent failure returns
    502 (fail-closed: NEVER a silent success, NEVER a silent score of 0).

    `body` is the JSON-encoded OpenAI request bytes; `headers` is a dict;
    `opener` is a urllib opener for testability (defaults to the squid-opener).
    The opener is called as ``opener.open(req, timeout=timeout)`` with a
    pre-built ``urllib.request.Request`` (matches urllib's real interface AND
    simple test double fakes).
    """
    import time as _t
    import urllib.error
    last_err = None
    attempts_used = 0
    start = _t.monotonic()
    for attempt in range(1, max_attempts + 1):
        req = urllib.request.Request(url, data=body, headers=headers,
                                     method="POST")
        attempts_used = attempt
        try:
            with opener.open(req, timeout=timeout) as r:
                data = r.read()
            latency = _t.monotonic() - start
            info = {"retries": attempts_used, "latency_s": round(latency, 3),
                    "last_error": None}
            return 200, data, info
        except (urllib.error.URLError, OSError, Exception) as e:
            last_err = e
            if attempt < max_attempts:
                time.sleep(base_delay * (2 ** (attempt - 1)))
    # persistent failure: fail-closed 502
    latency = _t.monotonic() - start
    payload = json.dumps(
        {"error": {"message": repr(last_err or "unknown")[:200],
                   "type": "upstream_error"}}).encode()
    info = {"retries": attempts_used, "latency_s": round(latency, 3),
            "last_error": repr(last_err) if last_err else None}
    return HTTPStatus.BAD_GATEWAY, payload, info


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, status, payload):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/health", "/healthz"):
            self._json(HTTPStatus.OK, {"ok": True, "model": "dp4-box-translator"})
        else:
            self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def do_POST(self):
        if self.path != "/v1/messages":
            self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})
            return
        n = int(self.headers.get("Content-Length") or 0)
        try:
            req = json.loads(self.rfile.read(n).decode())
        except Exception:
            self._json(HTTPStatus.BAD_REQUEST, {"error": "bad json"})
            return
        parts = []
        for m in req.get("messages", []):
            c = m.get("content")
            if isinstance(c, str):
                parts.append(c)
            elif isinstance(c, list):
                parts.extend(b.get("text", "") for b in c if isinstance(b, dict))
        prompt = "\n\n".join(p for p in parts if p)
        up_body = json.dumps({
            "model": "deepseek_v4",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": int(req.get("max_tokens", 4096)),
            "temperature": float(req.get("temperature") or 0.0),
        }).encode()
        up_url = UPSTREAM.rstrip("/") + "/v1/chat/completions"
        up_headers = {"Content-Type": "application/json", "Authorization": "Bearer " + JWT}
        opener = urllib.request.build_opener()  # honors env http_proxy (squid)
        status, body, info = _open_upstream_with_retry(
            up_url, up_headers, up_body, opener,
            max_attempts=MAX_UPSTREAM_ATTEMPTS,
            base_delay=BASE_RETRY_DELAY,
            timeout=UPSTREAM_TIMEOUT,
        )
        # B-TR instrumentation: log every judge call with retries/latency/error to
        # /tmp/box_translator_judge.log so dark-step root-causing has evidence
        # (class-extinction for the recurring dark steps).
        _log_judge_call(success=(status == 200), info=info)
        if status != 200:
            self._json(status, json.loads(body))
            return
        d = json.loads(body.decode())
        text = d["choices"][0]["message"]["content"]
        self._json(HTTPStatus.OK, {
            "id": d.get("id"), "type": "message", "role": "assistant",
            "model": "dp4",
            "content": [{"type": "text", "text": text}],
            "stop_reason": "end_turn", "usage": d.get("usage", {}),
        })


def _log_judge_call(*, success: bool, info: dict) -> None:
    """Append a one-line JSON record for every judge call so the judge-health
    agent / loganalyst can correlate dark steps with translator retries/latency."""
    import datetime
    try:
        rec = {"ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "success": success, **info}
        with open("/tmp/box_translator_judge.log", "a") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass  # logging must never break a judge call


def main():
    with open(JWT_PATH) as f:
        jwt = f.read().strip()
    assert len(jwt.split(".")) == 3, f"JWT at {JWT_PATH} malformed"
    srv = ThreadingHTTPServer(("127.0.0.1", 56238), Handler)
    print("box anthropic translator on :56238 -> dp4 direct", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()

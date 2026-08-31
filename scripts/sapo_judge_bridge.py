#!/usr/bin/env python3
"""SAPO judge bridge — box-side server (2026-08-27, JUDGE BRIDGE lane).

Root cause (systematic debugging, evidence): the training box resolves
aihuanxin.cn to an INTERNAL gateway (192.168.140.4) without our dp4
subscription route ("subscription route not found"); the Mac resolves the
PUBLIC gateway (36.212.177.181) where the `claude -p huanxin -m dp4`
subscription works. The box has no other outbound path.

Design (architecture change after 3+ failed transport fixes): the trainer is
UNCHANGED — its --judge-dp4-endpoint points at this box-local server. The
server accepts the trainer's Anthropic /v1/messages judge call, stages it as
a request file in the queue dir; a Mac-side watcher
(scripts/sapo_judge_mac_watcher.sh) polls the queue via the daemon, calls the
real dp4 proxy on the Mac, and stages the response file. The bridge waits and
relays. Fail-closed: timeout -> Anthropic-shaped 504 (the trainer's dp4 client
then records judge-absent — never a silent score).
"""

from __future__ import annotations

import argparse
import json
import os
import time
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=56237)
    parser.add_argument("--queue-dir", required=True)
    parser.add_argument(
        "--judge-timeout",
        type=float,
        default=290.0,
        help="Seconds to wait for the Mac watcher to stage a response. Chain "
        "alignment (2026-08-28, live evidence: dp4 took ~200s): trainer client "
        "310 > bridge 290 > watcher dp4 call 250 + poll/overhead.",
    )
    return parser.parse_args(argv)


def write_atomic(path: str, data: str) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        handle.write(data)
    os.replace(tmp, path)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # silence default request logging
        pass

    def _json(self, status: int, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in {"/", "/health", "/healthz"}:
            self._json(HTTPStatus.OK, {"ok": True, "model": "dp4-bridge"})
            return
        self._json(
            HTTPStatus.NOT_FOUND,
            {"error": {"message": "not found", "type": "not_found_error"}},
        )

    def do_POST(self) -> None:  # noqa: N802
        if self.path not in {"/v1/messages", "/messages"}:
            self._json(
                HTTPStatus.NOT_FOUND,
                {"error": {"message": "not found", "type": "not_found_error"}},
            )
            return
        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = self.rfile.read(length).decode("utf-8")
            json.loads(body)
        except Exception:
            self._json(
                HTTPStatus.BAD_REQUEST,
                {"error": {"message": "invalid JSON", "type": "invalid_request_error"}},
            )
            return
        rid = uuid.uuid4().hex
        queue_dir = self.server.queue_dir  # type: ignore[attr-defined]
        req_path = os.path.join(queue_dir, f"req_{rid}.json")
        resp_path = os.path.join(queue_dir, f"resp_{rid}.json")
        write_atomic(req_path, body)
        deadline = time.time() + self.server.judge_timeout  # type: ignore[attr-defined]
        try:
            while time.time() < deadline:
                if os.path.exists(resp_path):
                    try:
                        with open(resp_path, encoding="utf-8") as handle:
                            resp = json.loads(handle.read())
                    except Exception:
                        # corrupt/empty response staged by a broken watcher:
                        # drop it so the watcher can retry, keep waiting
                        try:
                            os.remove(resp_path)
                        except OSError:
                            pass
                        time.sleep(1.0)
                        continue
                    try:
                        os.remove(resp_path)
                        os.remove(req_path)
                    except OSError:
                        pass
                    self._json(HTTPStatus.OK, resp)
                    return
                time.sleep(1.0)
        finally:
            # fail-closed: remove the staged request when the watcher never
            # answered; an orphan resp staged later is inert (watcher cleans).
            if os.path.exists(req_path) and not os.path.exists(resp_path):
                try:
                    os.remove(req_path)
                except OSError:
                    pass
        self._json(
            HTTPStatus.GATEWAY_TIMEOUT,
            {"error": {"message": "judge bridge timeout", "type": "bridge_timeout"}},
        )


def main() -> int:
    args = parse_args()
    os.makedirs(args.queue_dir, exist_ok=True)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.queue_dir = args.queue_dir  # type: ignore[attr-defined]
    server.judge_timeout = args.judge_timeout  # type: ignore[attr-defined]
    print(
        json.dumps(
            {
                "stage": "judge_bridge_up",
                "host": args.host,
                "port": args.port,
                "queue_dir": args.queue_dir,
                "judge_timeout": args.judge_timeout,
            }
        ),
        flush=True,
    )
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

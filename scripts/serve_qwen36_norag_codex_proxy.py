#!/usr/bin/env python3
"""Serve Qwen3.6 without RAG as a Codex-compatible local provider."""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantum_rag.generation import ChatCompletionsClient
from scripts.serve_qwen36_rag_codex_proxy import (
    chat_payload,
    extract_request_text,
    responses_payload,
    streaming_events,
)


DEFAULT_MODEL_ALIAS = "qwen3.6-27b-norag"


class NoRAGCodexState:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args

    def generate(self, payload: dict[str, Any]) -> str:
        query = extract_request_text(payload)
        if not query:
            raise ValueError("request contains no input text")
        requested_max_output_tokens = int(
            payload.get("max_output_tokens")
            or payload.get("max_tokens")
            or self.args.max_output_tokens
        )
        max_output_tokens = min(requested_max_output_tokens, self.args.max_output_tokens)
        temperature = float(payload.get("temperature", self.args.temperature))
        client = ChatCompletionsClient(
            base_url=self.args.backend_base_url,
            model=self.args.backend_model,
            api_key=self.args.backend_api_key,
            timeout_seconds=self.args.timeout_seconds,
            enable_thinking=False,
        )
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Qwen3.6-27B answering without retrieved documentation. "
                    "Answer directly from the model context only."
                ),
            },
            {"role": "user", "content": query},
        ]
        return client.generate(messages, max_output_tokens=max_output_tokens, temperature=temperature)


def make_handler(state: NoRAGCodexState) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "Qwen36NoRAGCodexProxy/0.1"

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            if not state.args.quiet:
                super().log_message(format, *args)

        def _send_json(self, status: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_sse(self, events: list[tuple[str, dict[str, Any]]]) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.end_headers()
            for event, payload in events:
                data = json.dumps(payload, ensure_ascii=False)
                self.wfile.write(f"event: {event}\ndata: {data}\n\n".encode("utf-8"))
                self.wfile.flush()
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()

        def _read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length) if length > 0 else b"{}"
            return json.loads(raw.decode("utf-8") or "{}")

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/health":
                self._send_json(
                    200,
                    {
                        "ok": True,
                        "model": state.args.model_alias,
                        "backend": state.args.backend_base_url,
                        "backend_model": state.args.backend_model,
                        "rag": False,
                    },
                )
                return
            if self.path == "/v1/models":
                self._send_json(
                    200,
                    {
                        "object": "list",
                        "data": [
                            {
                                "id": state.args.model_alias,
                                "object": "model",
                                "owned_by": "quantum-gpt",
                            }
                        ],
                    },
                )
                return
            self._send_json(404, {"error": {"message": f"unknown path: {self.path}"}})

        def do_POST(self) -> None:  # noqa: N802
            try:
                payload = self._read_json()
                answer = state.generate(payload)
                if self.path == "/v1/responses":
                    if payload.get("stream") is True:
                        self._send_sse(streaming_events(state.args.model_alias, answer))
                        return
                    self._send_json(200, responses_payload(state.args.model_alias, answer))
                    return
                if self.path == "/v1/chat/completions":
                    self._send_json(200, chat_payload(state.args.model_alias, answer))
                    return
                self._send_json(404, {"error": {"message": f"unknown path: {self.path}"}})
            except urllib.error.HTTPError as exc:
                raw = exc.read().decode("utf-8", errors="replace")
                self._send_json(exc.code, {"error": {"message": raw}})
            except Exception as exc:  # pragma: no cover - defensive HTTP boundary
                self._send_json(500, {"error": {"message": str(exc)}})

    return Handler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--model-alias", default=DEFAULT_MODEL_ALIAS)
    parser.add_argument("--backend-base-url", default="http://127.0.0.1:8012")
    parser.add_argument("--backend-model", default="qwen3.6-27b-rag")
    parser.add_argument("--backend-api-key", default="dummy")
    parser.add_argument("--max-output-tokens", type=int, default=256)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--timeout-seconds", type=float, default=900.0)
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    state = NoRAGCodexState(args)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(state))
    print(
        json.dumps(
            {
                "ok": True,
                "server": f"http://{args.host}:{args.port}",
                "model": args.model_alias,
                "backend": args.backend_base_url,
                "backend_model": args.backend_model,
                "rag": False,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

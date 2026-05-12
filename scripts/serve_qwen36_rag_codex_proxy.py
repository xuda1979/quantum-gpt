#!/usr/bin/env python3
"""Serve Qwen3.6 quantum RAG as a Codex-compatible local provider."""

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

from quantum_rag.generation import ChatCompletionsClient, ResponsesClient, build_rag_messages
from quantum_rag.index import QuantumRAGIndex
from quantum_rag.retrieval import QueryExpansionConfig, retrieve


DEFAULT_MODEL_ALIAS = "quantum-intelligence-v0.1.0"


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
                elif isinstance(item.get("input_text"), str):
                    parts.append(str(item["input_text"]))
        return "\n".join(part for part in parts if part)
    return ""


def extract_request_text(payload: dict[str, Any]) -> str:
    """Extract the user-facing prompt from Responses or Chat Completions payloads."""

    if isinstance(payload.get("messages"), list):
        messages = payload["messages"]
        user_parts = [
            _content_to_text(message.get("content"))
            for message in messages
            if isinstance(message, dict) and message.get("role") == "user"
        ]
        if user_parts:
            return "\n\n".join(part for part in user_parts if part).strip()
        return "\n\n".join(
            _content_to_text(message.get("content"))
            for message in messages
            if isinstance(message, dict)
        ).strip()

    input_payload = payload.get("input")
    if isinstance(input_payload, str):
        return input_payload.strip()
    if isinstance(input_payload, list):
        user_parts: list[str] = []
        all_parts: list[str] = []
        for item in input_payload:
            if isinstance(item, str):
                all_parts.append(item)
                continue
            if not isinstance(item, dict):
                continue
            text = _content_to_text(item.get("content"))
            if not text and isinstance(item.get("text"), str):
                text = str(item["text"])
            if text:
                all_parts.append(text)
                if item.get("role") == "user":
                    user_parts.append(text)
        if user_parts:
            return "\n\n".join(user_parts).strip()
        return "\n\n".join(all_parts).strip()
    return ""


def responses_payload(model: str, answer: str, *, created: int | None = None) -> dict[str, Any]:
    created = created or int(time.time())
    response_id = f"resp_qirag_{created}"
    message_id = f"msg_qirag_{created}"
    return {
        "id": response_id,
        "object": "response",
        "created_at": created,
        "model": model,
        "status": "completed",
        "output": [
            {
                "id": message_id,
                "type": "message",
                "status": "completed",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "text": answer,
                        "annotations": [],
                    }
                ],
            }
        ],
        "output_text": answer,
        "usage": {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        },
    }


def streaming_events(model: str, answer: str) -> list[tuple[str, dict[str, Any]]]:
    """Render a minimal OpenAI Responses SSE sequence for Codex CLI."""

    created = int(time.time())
    completed = responses_payload(model, answer, created=created)
    response_id = completed["id"]
    message = completed["output"][0]
    message_id = message["id"]
    content_part = message["content"][0]
    created_response = {
        **completed,
        "status": "in_progress",
        "output": [],
        "output_text": "",
    }
    in_progress_response = {
        **created_response,
        "status": "in_progress",
    }
    return [
        (
            "response.created",
            {
                "type": "response.created",
                "response": created_response,
            },
        ),
        (
            "response.in_progress",
            {
                "type": "response.in_progress",
                "response": in_progress_response,
            },
        ),
        (
            "response.output_item.added",
            {
                "type": "response.output_item.added",
                "response_id": response_id,
                "output_index": 0,
                "item": {**message, "status": "in_progress", "content": []},
            },
        ),
        (
            "response.content_part.added",
            {
                "type": "response.content_part.added",
                "response_id": response_id,
                "item_id": message_id,
                "output_index": 0,
                "content_index": 0,
                "part": {"type": "output_text", "text": "", "annotations": []},
            },
        ),
        (
            "response.output_text.delta",
            {
                "type": "response.output_text.delta",
                "response_id": response_id,
                "item_id": message_id,
                "output_index": 0,
                "content_index": 0,
                "delta": answer,
                "logprobs": [],
            },
        ),
        (
            "response.output_text.done",
            {
                "type": "response.output_text.done",
                "response_id": response_id,
                "item_id": message_id,
                "output_index": 0,
                "content_index": 0,
                "text": answer,
                "logprobs": [],
            },
        ),
        (
            "response.content_part.done",
            {
                "type": "response.content_part.done",
                "response_id": response_id,
                "item_id": message_id,
                "output_index": 0,
                "content_index": 0,
                "part": content_part,
            },
        ),
        (
            "response.output_item.done",
            {
                "type": "response.output_item.done",
                "response_id": response_id,
                "output_index": 0,
                "item": message,
            },
        ),
        (
            "response.completed",
            {
                "type": "response.completed",
                "response": completed,
            },
        ),
    ]


def chat_payload(model: str, answer: str) -> dict[str, Any]:
    created = int(time.time())
    return {
        "id": f"chatcmpl_qirag_{created}",
        "object": "chat.completion",
        "created": created,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": answer,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        },
    }


class RAGCodexState:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.index = QuantumRAGIndex.load(args.index)

    def generate(self, payload: dict[str, Any]) -> str:
        query = extract_request_text(payload)
        if not query:
            raise ValueError("request contains no input text")

        retrieved = retrieve(
            self.index,
            query,
            top_k=self.args.top_k,
            alpha=self.args.alpha,
            expansion=QueryExpansionConfig(enabled=not self.args.disable_query_expansion),
            max_chunks_per_source=self.args.max_chunks_per_source,
        )
        messages = build_rag_messages(
            query,
            retrieved,
            max_chars_per_chunk=self.args.max_context_chars,
        )
        max_output_tokens = int(
            payload.get("max_output_tokens")
            or payload.get("max_tokens")
            or self.args.max_output_tokens
        )
        temperature = float(payload.get("temperature", self.args.temperature))
        if self.args.backend_api_style == "responses":
            client = ResponsesClient(
                base_url=self.args.backend_base_url,
                model=self.args.backend_model,
                timeout_seconds=self.args.timeout_seconds,
            )
        else:
            client = ChatCompletionsClient(
                base_url=self.args.backend_base_url,
                model=self.args.backend_model,
                api_key=self.args.backend_api_key,
                timeout_seconds=self.args.timeout_seconds,
            )
        return client.generate(
            messages,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        )


def make_handler(state: RAGCodexState) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "Qwen36RAGCodexProxy/0.1"

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
                        "backend_model": state.args.backend_model,
                        "index": str(state.args.index),
                        "summary": state.index.summary(),
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
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--model-alias", default=DEFAULT_MODEL_ALIAS)
    parser.add_argument(
        "--index",
        type=Path,
        default=ROOT / "artifacts" / "quantum-rag" / "qwen36-quantum-docs-index.pkl.gz",
    )
    parser.add_argument("--backend-base-url", default="http://127.0.0.1:8011")
    parser.add_argument("--backend-model", default="qwen3.6-27b-rag")
    parser.add_argument("--backend-api-style", choices=["chat", "responses"], default="chat")
    parser.add_argument("--backend-api-key", default="dummy")
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--alpha", type=float, default=0.55)
    parser.add_argument("--max-chunks-per-source", type=int, default=2)
    parser.add_argument("--max-context-chars", type=int, default=1400)
    parser.add_argument("--max-output-tokens", type=int, default=900)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--timeout-seconds", type=float, default=900.0)
    parser.add_argument("--disable-query-expansion", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    state = RAGCodexState(args)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(state))
    print(
        json.dumps(
            {
                "ok": True,
                "server": f"http://{args.host}:{args.port}",
                "model": args.model_alias,
                "backend": args.backend_base_url,
                "backend_model": args.backend_model,
                "index": str(args.index),
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

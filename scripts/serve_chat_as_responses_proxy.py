#!/usr/bin/env python3
"""Translate OpenAI Responses requests to an upstream chat-completions service."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18092)
    parser.add_argument("--upstream-url", required=True)
    parser.add_argument("--upstream-model", required=True)
    parser.add_argument("--upstream-auth-header", default="Authorization")
    parser.add_argument("--upstream-auth-scheme", default="Bearer")
    parser.add_argument("--upstream-auth-token-env")
    parser.add_argument("--max-input-chars", type=int)
    parser.add_argument("--strip-reasoning-tags", action="store_true")
    return parser.parse_args()


def error_payload(message: str, error_type: str = "invalid_request_error") -> dict[str, Any]:
    return {"error": {"message": message, "type": error_type}}


def content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return str(content)
    parts: list[str] = []
    for item in content:
        if isinstance(item, str):
            parts.append(item)
        elif isinstance(item, dict):
            text = item.get("text")
            if isinstance(text, str):
                parts.append(text)
            elif item.get("type") in {"input_image", "image_url"}:
                parts.append("[image omitted]")
            elif item.get("type") == "input_file":
                parts.append("[file omitted]")
    return "\n".join(part for part in parts if part)


def convert_input_to_messages(body: dict[str, Any]) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    system_parts: list[str] = []
    instructions = body.get("instructions")
    if isinstance(instructions, str) and instructions.strip():
        system_parts.append(instructions)

    raw_input = body.get("input")
    if isinstance(raw_input, str):
        if system_parts:
            messages.append({"role": "system", "content": "\n\n".join(system_parts)})
        messages.append({"role": "user", "content": raw_input})
        return messages

    if isinstance(raw_input, list):
        for item in raw_input:
            if not isinstance(item, dict):
                continue
            role = item.get("role") or "user"
            if role == "developer":
                role = "system"
            if role not in {"system", "user", "assistant", "tool"}:
                role = "user"
            content = content_to_text(item.get("content", ""))
            if role == "system":
                if content:
                    system_parts.append(content)
            else:
                messages.append({"role": role, "content": content})
    elif isinstance(body.get("messages"), list):
        for item in body["messages"]:
            if isinstance(item, dict):
                role = item.get("role") or "user"
                if role == "developer":
                    role = "system"
                messages.append({"role": role, "content": content_to_text(item.get("content", ""))})

    if system_parts:
        messages.insert(0, {"role": "system", "content": "\n\n".join(system_parts)})
    return messages


def message_content_len(message: dict[str, Any]) -> int:
    content = message.get("content")
    return len(content) if isinstance(content, str) else 0


def compact_messages(
    messages: list[dict[str, Any]], max_input_chars: int | None
) -> list[dict[str, Any]]:
    if not max_input_chars:
        return messages
    compacted = [dict(message) for message in messages]
    while (
        sum(message_content_len(message) for message in compacted) > max_input_chars
        and len(compacted) > 1
    ):
        compacted.pop(0)
    total = sum(message_content_len(message) for message in compacted)
    if total > max_input_chars and compacted:
        marker = "\n\n[message truncated by local proxy]"
        content = str(compacted[0].get("content") or "")
        compacted[0]["content"] = content[: max(0, max_input_chars - len(marker))] + marker
    return compacted


def strip_reasoning_tags(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    if "</think>" in text:
        text = text.split("</think>", 1)[1]
    return text.lstrip()


def build_usage(upstream: dict[str, Any]) -> dict[str, int]:
    usage = upstream.get("usage")
    if not isinstance(usage, dict):
        return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    input_tokens = int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0)
    output_tokens = int(usage.get("completion_tokens") or usage.get("output_tokens") or 0)
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
    }


def build_response(
    body: dict[str, Any], upstream: dict[str, Any], *, strip_reasoning: bool
) -> dict[str, Any]:
    choices = upstream.get("choices")
    choice = (
        choices[0] if isinstance(choices, list) and choices and isinstance(choices[0], dict) else {}
    )
    message = choice.get("message") if isinstance(choice.get("message"), dict) else {}
    content = message.get("content") if isinstance(message.get("content"), str) else ""
    if strip_reasoning:
        content = strip_reasoning_tags(content)
    return {
        "id": upstream.get("id") or f"resp_{uuid.uuid4().hex}",
        "object": "response",
        "created_at": int(upstream.get("created") or time.time()),
        "status": "completed",
        "model": body.get("model") or upstream.get("model") or "unknown",
        "output": [
            {
                "type": "message",
                "id": f"msg_{uuid.uuid4().hex[:12]}",
                "role": "assistant",
                "content": [{"type": "output_text", "text": content}],
                "status": "completed",
            }
        ],
        "output_text": content,
        "usage": build_usage(upstream),
    }


def stream_events(response: dict[str, Any]) -> list[dict[str, Any]]:
    output = response.get("output")
    item = output[0] if isinstance(output, list) and output and isinstance(output[0], dict) else {}
    content = item.get("content")
    part = (
        content[0] if isinstance(content, list) and content and isinstance(content[0], dict) else {}
    )
    text = part.get("text") if isinstance(part.get("text"), str) else ""
    item_id = str(item.get("id") or f"msg_{uuid.uuid4().hex[:12]}")
    return [
        {
            "type": "response.created",
            "response": {**response, "status": "in_progress", "output": []},
        },
        {
            "type": "response.in_progress",
            "response": {**response, "status": "in_progress", "output": []},
        },
        {
            "type": "response.output_item.added",
            "output_index": 0,
            "item": {
                "id": item_id,
                "type": "message",
                "status": "in_progress",
                "role": "assistant",
                "content": [],
            },
        },
        {
            "type": "response.content_part.added",
            "item_id": item_id,
            "output_index": 0,
            "content_index": 0,
            "part": {"type": "output_text", "text": "", "annotations": []},
        },
        {
            "type": "response.output_text.delta",
            "item_id": item_id,
            "output_index": 0,
            "content_index": 0,
            "delta": text,
        },
        {
            "type": "response.output_text.done",
            "item_id": item_id,
            "output_index": 0,
            "content_index": 0,
            "text": text,
        },
        {
            "type": "response.content_part.done",
            "item_id": item_id,
            "output_index": 0,
            "content_index": 0,
            "part": {"type": "output_text", "text": text, "annotations": []},
        },
        {
            "type": "response.output_item.done",
            "output_index": 0,
            "item": {
                "id": item_id,
                "type": "message",
                "status": "completed",
                "role": "assistant",
                "content": [{"type": "output_text", "text": text, "annotations": []}],
            },
        },
        {"type": "response.completed", "response": response},
    ]


class Handler(BaseHTTPRequestHandler):
    server_version = "chat-as-responses-proxy/0.1"
    args: argparse.Namespace

    def send_json(self, status: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_sse(self, events: list[dict[str, Any]]) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()
        for event in events:
            payload = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
            self.wfile.write(f"data: {payload}\n\n".encode())
            self.wfile.flush()
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()

    def do_GET(self) -> None:  # noqa: N802
        if self.path in {"/health", "/healthz", "/"}:
            self.send_json(HTTPStatus.OK, {"ok": True, "upstream_model": self.args.upstream_model})
            return
        if self.path == "/v1/models":
            self.send_json(
                HTTPStatus.OK, {"object": "list", "data": [{"id": "quantum-intelligence-v0.1.0"}]}
            )
            return
        self.send_json(HTTPStatus.NOT_FOUND, error_payload("not found", "not_found_error"))

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/responses":
            self.send_json(HTTPStatus.NOT_FOUND, error_payload("not found", "not_found_error"))
            return
        try:
            body = json.loads(
                self.rfile.read(int(self.headers.get("Content-Length", "0") or "0")).decode("utf-8")
            )
            upstream = self.call_upstream(body)
            response = build_response(
                body, upstream, strip_reasoning=self.args.strip_reasoning_tags
            )
            if body.get("stream") is True:
                self.send_sse(stream_events(response))
                return
            self.send_json(HTTPStatus.OK, response)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = error_payload(raw or str(exc), "upstream_http_error")
            self.send_json(exc.code, payload)
        except Exception as exc:  # noqa: BLE001
            self.send_json(HTTPStatus.BAD_GATEWAY, error_payload(str(exc), "proxy_error"))

    def call_upstream(self, body: dict[str, Any]) -> dict[str, Any]:
        messages = compact_messages(convert_input_to_messages(body), self.args.max_input_chars)
        if not messages:
            raise ValueError("request input did not contain usable messages")
        token = ""
        if self.args.upstream_auth_token_env:
            token = os.environ.get(self.args.upstream_auth_token_env, "")
        if not token:
            token = self.headers.get("Authorization", "").removeprefix("Bearer ").strip()
        payload = {
            "model": self.args.upstream_model,
            "messages": messages,
            "stream": False,
            "max_tokens": int(body.get("max_output_tokens") or 512),
        }
        headers = {"Content-Type": "application/json"}
        if token:
            headers[self.args.upstream_auth_header] = (
                f"{self.args.upstream_auth_scheme} {token}".strip()
            )
        request = urllib.request.Request(
            self.args.upstream_url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=180) as response:
            return json.loads(response.read().decode("utf-8"))

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return


def main() -> int:
    Handler.args = parse_args()
    server = ThreadingHTTPServer((Handler.args.host, Handler.args.port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

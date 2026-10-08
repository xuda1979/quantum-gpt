#!/usr/bin/env python3
"""Expose a minimal OpenAI Responses-compatible proxy backed by Yunwu chat completions."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import time
import traceback
import urllib.error
import urllib.request
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8011)
    parser.add_argument(
        "--base-url", default=os.environ.get("YUNWU_PROXY_BASE_URL", "https://api.yunwu.ai/v1")
    )
    parser.add_argument(
        "--health-model", default=os.environ.get("YUNWU_PROXY_HEALTH_MODEL", "gpt-5.4")
    )
    parser.add_argument("--chunk-size", type=int, default=256)
    return parser.parse_args()


def normalize_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
                continue
            if not isinstance(item, dict):
                continue
            item_type = item.get("type")
            if item_type in {"text", "input_text", "output_text"}:
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
            elif item_type == "image_url":
                parts.append("[image omitted]")
        return "\n".join(part for part in parts if part)
    return str(content)


def normalize_role(role: Any) -> str:
    text = str(role or "user").strip().lower()
    if text in {"system", "developer"}:
        return "system"
    if text in {"assistant", "user"}:
        return text
    return "user"


def extract_messages(payload: dict[str, Any]) -> list[dict[str, Any]]:
    messages = payload.get("messages")
    if isinstance(messages, list):
        return [item for item in messages if isinstance(item, dict)]

    response_input = payload.get("input")
    if isinstance(response_input, str):
        return [{"role": "user", "content": response_input}]
    if isinstance(response_input, list):
        extracted: list[dict[str, Any]] = []
        for item in response_input:
            if not isinstance(item, dict):
                continue
            extracted.append(
                {
                    "role": normalize_role(item.get("role", "user")),
                    "content": normalize_content(item.get("content", "")),
                }
            )
        if extracted:
            return extracted

    raise ValueError("Request does not contain supported `messages` or `input` content")


def choose_upstream_api_key(model_name: str) -> str:
    generic = os.environ.get("YUNWU_API_KEY") or os.environ.get("YUNWU_OPENAI_API_KEY")
    claude = os.environ.get("YUNWU_CLAUDE_API_KEY")
    lower_model = model_name.strip().lower()
    if lower_model.startswith("claude") and generic:
        return generic
    if generic:
        return generic
    if lower_model.startswith("claude") and claude:
        return claude
    raise RuntimeError("Missing Yunwu API credentials in environment")


def chunk_text(content: str, chunk_size: int) -> list[str]:
    return [
        content[index : index + chunk_size] for index in range(0, len(content), chunk_size)
    ] or [""]


class UpstreamError(RuntimeError):
    def __init__(self, *, status: int, payload: Any) -> None:
        super().__init__(f"Upstream request failed with HTTP {status}")
        self.status = status
        self.payload = payload


class ProxyState:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.relay_s3_root = os.environ.get("YUNWU_RELAY_S3_ROOT", "").strip()
        self.relay_request_prefix = os.environ.get(
            "YUNWU_RELAY_REQUEST_PREFIX", "relay/yunwu/requests"
        ).strip("/")
        self.relay_response_prefix = os.environ.get(
            "YUNWU_RELAY_RESPONSE_PREFIX", "relay/yunwu/responses"
        ).strip("/")
        self.relay_timeout_seconds = float(os.environ.get("YUNWU_RELAY_TIMEOUT_SECONDS", "300"))
        self.relay_poll_seconds = float(os.environ.get("YUNWU_RELAY_POLL_SECONDS", "2"))
        self.rclone_bin = os.environ.get("RCLONE_BIN") or shutil.which("rclone")
        if not self.rclone_bin and Path("/Users/daxu/homebrew/bin/rclone").exists():
            self.rclone_bin = "/Users/daxu/homebrew/bin/rclone"

    def _call_chat_completions_direct(
        self, request_payload: dict[str, Any], model_name: str
    ) -> dict[str, Any]:
        request = urllib.request.Request(
            self.args.base_url.rstrip("/") + "/chat/completions",
            data=json.dumps(request_payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {choose_upstream_api_key(model_name)}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = {"error": {"message": raw, "type": "upstream_error"}}
            raise UpstreamError(status=exc.code, payload=payload) from exc

    def _rclone_run(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        if not self.rclone_bin:
            raise RuntimeError("rclone is required for YUNWU_RELAY_S3_ROOT mode")
        return subprocess.run(
            [self.rclone_bin, *args],
            capture_output=True,
            text=True,
            check=check,
        )

    def _relay_remote_path(self, prefix: str, request_id: str) -> str:
        return self.relay_s3_root.rstrip("/") + "/" + prefix.strip("/") + f"/{request_id}.json"

    def _call_chat_completions_via_s3(self, request_payload: dict[str, Any]) -> dict[str, Any]:
        request_id = uuid.uuid4().hex
        request_remote_path = self._relay_remote_path(self.relay_request_prefix, request_id)
        response_remote_path = self._relay_remote_path(self.relay_response_prefix, request_id)
        request_envelope = {
            "id": request_id,
            "created_at": int(time.time()),
            "request": request_payload,
        }
        with tempfile.TemporaryDirectory(prefix="yunwu-relay-") as tmp_dir:
            request_path = Path(tmp_dir) / f"{request_id}.json"
            request_path.write_text(
                json.dumps(request_envelope, ensure_ascii=False), encoding="utf-8"
            )
            upload = self._rclone_run(
                "copyto",
                str(request_path),
                request_remote_path,
                "--s3-no-check-bucket",
                check=False,
            )
            if upload.returncode != 0:
                raise RuntimeError(
                    f"relay request upload failed: {upload.stderr.strip() or upload.stdout.strip()}"
                )
            deadline = time.time() + self.relay_timeout_seconds
            last_error = ""
            while time.time() < deadline:
                result = self._rclone_run("cat", response_remote_path, check=False)
                if result.returncode == 0 and result.stdout.strip():
                    envelope = json.loads(result.stdout)
                    if envelope.get("ok", True):
                        response = envelope.get("response")
                        if not isinstance(response, dict):
                            raise RuntimeError("relay response missing `response` object")
                        return response
                    payload = envelope.get("payload")
                    status = int(envelope.get("status") or 502)
                    raise UpstreamError(
                        status=status,
                        payload=payload
                        if isinstance(payload, dict)
                        else {"error": {"message": str(payload)}},
                    )
                last_error = result.stderr.strip() or result.stdout.strip()
                time.sleep(self.relay_poll_seconds)
        raise TimeoutError(f"timed out waiting for relay response for {request_id}: {last_error}")

    def call_chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        model_name = str(payload.get("model") or self.args.health_model)
        request_payload = {
            "model": model_name,
            "messages": [
                {
                    "role": normalize_role(message.get("role", "user")),
                    "content": normalize_content(message.get("content", "")),
                }
                for message in extract_messages(payload)
            ],
            "stream": False,
        }
        max_tokens = payload.get("max_tokens")
        if max_tokens is None:
            max_tokens = payload.get("max_completion_tokens")
        if max_tokens is None:
            max_tokens = payload.get("max_output_tokens")
        if max_tokens is not None:
            request_payload["max_tokens"] = int(max_tokens)
        temperature = payload.get("temperature")
        if temperature is not None:
            request_payload["temperature"] = float(temperature)
        if self.relay_s3_root:
            return self._call_chat_completions_via_s3(request_payload)
        return self._call_chat_completions_direct(request_payload, model_name)


def make_handler(state: ProxyState):
    class Handler(BaseHTTPRequestHandler):
        @staticmethod
        def _log(entry: dict[str, Any]) -> None:
            print(json.dumps(entry, ensure_ascii=False), flush=True)

        def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _read_json(self) -> dict[str, Any]:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            if not raw_body:
                return {}
            return json.loads(raw_body.decode("utf-8"))

        @staticmethod
        def _extract_content(chat_payload: dict[str, Any]) -> str:
            choices = chat_payload.get("choices") or []
            if not choices:
                return ""
            message = choices[0].get("message") or {}
            content = message.get("content")
            if isinstance(content, str):
                return content
            return normalize_content(content)

        @staticmethod
        def _build_response_object(
            response_id: str, model_name: str, content: str, status: str
        ) -> dict[str, Any]:
            return {
                "id": response_id,
                "object": "response",
                "created_at": int(time.time()),
                "status": status,
                "error": None,
                "incomplete_details": None,
                "instructions": None,
                "max_output_tokens": None,
                "model": model_name,
                "output": [
                    {
                        "id": "msg_001",
                        "type": "message",
                        "status": "completed" if status == "completed" else "in_progress",
                        "role": "assistant",
                        "content": [
                            {
                                "type": "output_text",
                                "text": content if status == "completed" else "",
                                "annotations": [],
                            }
                        ],
                    }
                ],
                "parallel_tool_calls": True,
                "previous_response_id": None,
                "reasoning": {"effort": None, "summary": None},
                "store": False,
                "temperature": 0,
                "text": {"format": {"type": "text"}},
                "tool_choice": "auto",
                "tools": [],
                "top_p": 1,
                "truncation": "disabled",
                "usage": {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "output_tokens_details": {"reasoning_tokens": 0},
                    "total_tokens": 0,
                },
                "user": None,
                "metadata": {},
            }

        def _send_sse_chat_completion(self, content: str, model_name: str) -> None:
            completion_id = f"chatcmpl-{uuid.uuid4().hex}"
            created = int(time.time())
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()

            role_event = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model_name,
                "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}],
            }
            self.wfile.write(f"data: {json.dumps(role_event, ensure_ascii=False)}\n\n".encode())
            self.wfile.flush()

            for chunk in chunk_text(content, state.args.chunk_size):
                event = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model_name,
                    "choices": [{"index": 0, "delta": {"content": chunk}, "finish_reason": None}],
                }
                self.wfile.write(f"data: {json.dumps(event, ensure_ascii=False)}\n\n".encode())
                self.wfile.flush()

            final_event = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model_name,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            }
            self.wfile.write(f"data: {json.dumps(final_event, ensure_ascii=False)}\n\n".encode())
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()

        def _begin_sse_chat_completion(self, model_name: str) -> tuple[str, int]:
            completion_id = f"chatcmpl-{uuid.uuid4().hex}"
            created = int(time.time())
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
            role_event = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model_name,
                "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}],
            }
            self.wfile.write(f"data: {json.dumps(role_event, ensure_ascii=False)}\n\n".encode())
            self.wfile.flush()
            return completion_id, created

        def _finish_sse_chat_completion(
            self, completion_id: str, created: int, content: str, model_name: str
        ) -> None:
            for chunk in chunk_text(content, state.args.chunk_size):
                event = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model_name,
                    "choices": [{"index": 0, "delta": {"content": chunk}, "finish_reason": None}],
                }
                self.wfile.write(f"data: {json.dumps(event, ensure_ascii=False)}\n\n".encode())
                self.wfile.flush()
            final_event = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model_name,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            }
            self.wfile.write(f"data: {json.dumps(final_event, ensure_ascii=False)}\n\n".encode())
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()

        def _begin_sse_response(self, model_name: str) -> tuple[str, str]:
            response_id = f"resp_{uuid.uuid4().hex}"
            item_id = f"msg_{uuid.uuid4().hex}"
            sequence_number = 0

            def emit(event: dict[str, Any]) -> None:
                nonlocal sequence_number
                sequence_number += 1
                event.setdefault("sequence_number", sequence_number)
                self.wfile.write(f"data: {json.dumps(event, ensure_ascii=False)}\n\n".encode())
                self.wfile.flush()

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()

            emit(
                {
                    "type": "response.created",
                    "response": self._build_response_object(
                        response_id, model_name, "", "in_progress"
                    ),
                }
            )
            emit(
                {
                    "type": "response.in_progress",
                    "response": self._build_response_object(
                        response_id, model_name, "", "in_progress"
                    ),
                }
            )
            emit(
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
                }
            )
            emit(
                {
                    "type": "response.content_part.added",
                    "item_id": item_id,
                    "output_index": 0,
                    "content_index": 0,
                    "part": {"type": "output_text", "text": "", "annotations": []},
                }
            )
            return response_id, item_id

        def _finish_sse_response(
            self, response_id: str, item_id: str, content: str, model_name: str
        ) -> None:
            sequence_number = 4

            def emit(event: dict[str, Any]) -> None:
                nonlocal sequence_number
                sequence_number += 1
                event.setdefault("sequence_number", sequence_number)
                self.wfile.write(f"data: {json.dumps(event, ensure_ascii=False)}\n\n".encode())
                self.wfile.flush()

            for chunk in chunk_text(content, state.args.chunk_size):
                emit(
                    {
                        "type": "response.output_text.delta",
                        "response_id": response_id,
                        "item_id": item_id,
                        "output_index": 0,
                        "content_index": 0,
                        "delta": chunk,
                    }
                )
            emit(
                {
                    "type": "response.output_text.done",
                    "response_id": response_id,
                    "item_id": item_id,
                    "output_index": 0,
                    "content_index": 0,
                    "text": content,
                }
            )
            emit(
                {
                    "type": "response.content_part.done",
                    "item_id": item_id,
                    "output_index": 0,
                    "content_index": 0,
                    "part": {"type": "output_text", "text": content, "annotations": []},
                }
            )
            emit(
                {
                    "type": "response.output_item.done",
                    "output_index": 0,
                    "item": {
                        "id": item_id,
                        "type": "message",
                        "status": "completed",
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": content, "annotations": []}],
                    },
                }
            )
            emit(
                {
                    "type": "response.completed",
                    "response": self._build_response_object(
                        response_id, model_name, content, "completed"
                    ),
                }
            )
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/health":
                self._send_json(
                    {
                        "ok": True,
                        "upstream_base_url": state.args.base_url,
                        "model": state.args.health_model,
                    }
                )
                return
            if self.path == "/v1/models":
                self._send_json(
                    {
                        "object": "list",
                        "data": [
                            {
                                "id": state.args.health_model,
                                "object": "model",
                                "created": int(time.time()),
                                "owned_by": "yunwu-proxy",
                            }
                        ],
                    }
                )
                return
            self._send_json(
                {"error": f"Unsupported route: {self.path}"}, status=HTTPStatus.NOT_FOUND
            )

        def do_POST(self) -> None:  # noqa: N802
            try:
                payload = self._read_json()
                self._log(
                    {
                        "ts": int(time.time()),
                        "method": "POST",
                        "path": self.path,
                        "model": payload.get("model"),
                        "stream": payload.get("stream"),
                        "keys": sorted(payload.keys()),
                        "input_type": type(payload.get("input")).__name__
                        if "input" in payload
                        else None,
                        "has_messages": isinstance(payload.get("messages"), list),
                    }
                )
                if self.path == "/v1/chat/completions":
                    self._handle_chat_completions(payload)
                    return
                if self.path == "/v1/responses":
                    self._handle_responses(payload)
                    return
                self._send_json(
                    {"error": f"Unsupported route: {self.path}"}, status=HTTPStatus.NOT_FOUND
                )
            except UpstreamError as exc:
                self._log(
                    {
                        "ts": int(time.time()),
                        "path": self.path,
                        "error_type": "UpstreamError",
                        "status": exc.status,
                        "payload": exc.payload,
                    }
                )
                status = (
                    HTTPStatus(exc.status)
                    if exc.status in HTTPStatus._value2member_map_
                    else HTTPStatus.BAD_GATEWAY
                )
                self._send_json(
                    exc.payload
                    if isinstance(exc.payload, dict)
                    else {"error": {"message": str(exc.payload)}},
                    status=status,
                )
            except Exception as exc:  # noqa: BLE001
                self._log(
                    {
                        "ts": int(time.time()),
                        "path": self.path,
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                        "traceback": traceback.format_exc(),
                    }
                )
                self._send_json(
                    {"error": {"message": f"{type(exc).__name__}: {exc}", "type": "server_error"}},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR,
                )

        def _handle_chat_completions(self, payload: dict[str, Any]) -> None:
            model_name = str(payload.get("model") or state.args.health_model)
            upstream_payload = dict(payload)
            upstream_payload["model"] = model_name
            if bool(payload.get("stream")):
                completion_id, created = self._begin_sse_chat_completion(model_name)
                response_payload = state.call_chat_completions(upstream_payload)
                content = self._extract_content(response_payload)
                self._finish_sse_chat_completion(completion_id, created, content, model_name)
                return
            response_payload = state.call_chat_completions(upstream_payload)
            self._send_json(response_payload)

        def _handle_responses(self, payload: dict[str, Any]) -> None:
            model_name = str(payload.get("model") or state.args.health_model)
            upstream_payload = dict(payload)
            upstream_payload["model"] = model_name
            if bool(payload.get("stream")):
                response_id, item_id = self._begin_sse_response(model_name)
                chat_payload = state.call_chat_completions(upstream_payload)
                content = self._extract_content(chat_payload)
                self._finish_sse_response(response_id, item_id, content, model_name)
                return
            chat_payload = state.call_chat_completions(upstream_payload)
            content = self._extract_content(chat_payload)
            self._send_json(
                {
                    "id": f"resp-{uuid.uuid4().hex}",
                    "object": "response",
                    "created_at": int(time.time()),
                    "model": model_name,
                    "output": [
                        {
                            "id": f"msg-{uuid.uuid4().hex}",
                            "type": "message",
                            "role": "assistant",
                            "content": [
                                {"type": "output_text", "text": content, "annotations": []}
                            ],
                        }
                    ],
                    "output_text": content,
                    "status": "completed",
                }
            )

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return

    return Handler


def main() -> int:
    args = parse_args()
    state = ProxyState(args)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(state))
    print(
        json.dumps(
            {
                "stage": "proxy_ready",
                "host": args.host,
                "port": args.port,
                "base_url": args.base_url,
                "health_model": args.health_model,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

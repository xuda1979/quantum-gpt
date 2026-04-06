#!/usr/bin/env python3
"""Serve a local HF/PEFT model behind a small OpenAI-compatible chat API."""

from __future__ import annotations

import argparse
import inspect
import json
import sys
import time
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer, PreTrainedTokenizerFast

ROOT = Path(__file__).resolve().parents[1]
REQUEST_LOG_PATH = Path("/tmp/quantum_codex_server_requests.log")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evals.runner.candidate_sanitize import sanitize_candidate_text
from peft import PeftModel
from training.qwen_sft_peft import TextPreprocessorBackend, load_text_preprocessor_backend, resolve_device


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-model", type=Path, required=True)
    parser.add_argument("--adapter", type=Path, default=None)
    parser.add_argument("--model-name", default="quantum-gpt-omnicoder9b.1")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda", "npu"), default="auto")
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--enable-turboquant-cache", action="store_true")
    parser.add_argument("--turboquant-nbits", type=int, default=4)
    parser.add_argument("--turboquant-secondary-nbits", type=int, default=1)
    parser.add_argument("--turboquant-group-size", type=int, default=64)
    parser.add_argument("--turboquant-residual-length", type=int, default=128)
    parser.add_argument("--turboquant-axis-key", type=int, default=0)
    parser.add_argument("--turboquant-axis-value", type=int, default=0)
    parser.add_argument(
        "--turboquant-rotation",
        choices=("none", "hadamard", "random_hadamard"),
        default="hadamard",
    )
    parser.add_argument("--turboquant-seed", type=int, default=0)
    return parser.parse_args()


def _call_with_supported_kwargs(func: Any, kwargs: dict[str, Any]) -> Any:
    signature = inspect.signature(func)
    parameters = signature.parameters
    accepts_var_kwargs = any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in parameters.values()
    )
    if accepts_var_kwargs:
        filtered = kwargs
    else:
        filtered = {key: value for key, value in kwargs.items() if key in parameters}
    return func(**filtered)


def _build_turboquant_cache(args: argparse.Namespace, *, model: Any, device: Any) -> Any:
    try:
        import training.turboquant as turboquant  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "TurboQuant cache mode requested, but training.turboquant is missing. "
            "Add the TurboQuant runtime module first."
        ) from exc

    config = None
    config_kwargs = {
        "nbits": args.turboquant_nbits,
        "secondary_nbits": args.turboquant_secondary_nbits,
        "q_group_size": args.turboquant_group_size,
        "group_size": args.turboquant_group_size,
        "residual_length": args.turboquant_residual_length,
        "axis_key": args.turboquant_axis_key,
        "axis_value": args.turboquant_axis_value,
        "rotation": args.turboquant_rotation,
        "seed": args.turboquant_seed,
        "device": str(device),
        "compute_dtype": getattr(model, "dtype", None),
    }
    for config_name in ("TurboQuantConfig", "TurboQuantCacheConfig"):
        config_type = getattr(turboquant, config_name, None)
        if config_type is None:
            continue
        config = _call_with_supported_kwargs(config_type, config_kwargs)
        break

    build_kwargs = {
        "model": model,
        "device": str(device),
        "compute_dtype": getattr(model, "dtype", None),
        "config": config,
        "cache_config": config,
    }
    for builder_name in ("build_turboquant_cache", "create_turboquant_cache"):
        builder = getattr(turboquant, builder_name, None)
        if builder is None:
            continue
        return _call_with_supported_kwargs(builder, build_kwargs)

    for cache_name in ("TurboQuantCache", "TurboQuantKVCache"):
        cache_type = getattr(turboquant, cache_name, None)
        if cache_type is None:
            continue
        return _call_with_supported_kwargs(cache_type, build_kwargs)

    raise RuntimeError(
        "training.turboquant was found, but no compatible cache factory/class was exposed. "
        "Expected one of: build_turboquant_cache, create_turboquant_cache, "
        "TurboQuantCache, TurboQuantKVCache."
    )


def load_text_backend(model_path: Path) -> TextPreprocessorBackend:
    return load_text_preprocessor_backend(str(model_path), AutoTokenizer, AutoProcessor, PreTrainedTokenizerFast)


def load_model(model_path: Path, device: Any):
    model = AutoModelForCausalLM.from_pretrained(
        str(model_path),
        trust_remote_code=True,
        low_cpu_mem_usage=True,
        torch_dtype="auto",
    ).to(device)
    generation_config = getattr(model, "generation_config", None)
    if generation_config is not None:
        generation_config.do_sample = False
        generation_config.temperature = 1.0
        generation_config.top_p = 1.0
        generation_config.top_k = 50
    model.eval()
    return model


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


def render_prompt(backend: TextPreprocessorBackend, messages: list[dict[str, Any]]) -> str:
    normalized_messages = [
        {"role": normalize_role(message.get("role", "user")), "content": normalize_content(message.get("content", ""))}
        for message in messages
    ]
    render_backend = backend.render_backend
    if hasattr(render_backend, "apply_chat_template"):
        try:
            return render_backend.apply_chat_template(
                normalized_messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False,
            )
        except TypeError:
            return render_backend.apply_chat_template(
                normalized_messages,
                tokenize=False,
                add_generation_prompt=True,
            )
    return "\n\n".join(f"{item['role'].upper()}: {item['content']}" for item in normalized_messages)


def build_inputs(backend: TextPreprocessorBackend, prompt_text: str, device: Any) -> dict[str, Any]:
    tokens = backend.text_backend(prompt_text, return_tensors="pt")
    return {key: value.to(device) for key, value in tokens.items()}


class AdapterChatServer:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.device = resolve_device(torch, args.device)
        self.backend = load_text_backend(args.base_model)
        tokenizer = self.backend.text_backend
        if getattr(tokenizer, "pad_token", None) is None:
            tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"
        self.model = load_model(args.base_model, self.device)
        if args.adapter is not None:
            self.model = PeftModel.from_pretrained(self.model, str(args.adapter))
            self.model.eval()

    def generate_text(
        self,
        messages: list[dict[str, Any]],
        *,
        max_new_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        prompt_text = render_prompt(self.backend, messages)
        inputs = build_inputs(self.backend, prompt_text, self.device)
        prompt_len = inputs["input_ids"].shape[1]
        tokenizer = self.backend.text_backend
        token_limit = max_new_tokens if max_new_tokens is not None else self.args.max_new_tokens
        if token_limit <= 0:
            token_limit = self.args.max_new_tokens
        sample_temperature = self.args.temperature if temperature is None else temperature
        generation_kwargs = {
            "max_new_tokens": token_limit,
            "do_sample": sample_temperature > 0,
            "temperature": sample_temperature if sample_temperature > 0 else None,
            "pad_token_id": tokenizer.eos_token_id,
        }
        if self.args.enable_turboquant_cache:
            # Use a fresh cache per request to avoid cross-request KV state bleed.
            generation_kwargs["past_key_values"] = _build_turboquant_cache(
                self.args,
                model=self.model,
                device=self.device,
            )
        generation_kwargs = {key: value for key, value in generation_kwargs.items() if value is not None}
        with torch.inference_mode():
            output = self.model.generate(**inputs, **generation_kwargs)
        completion = output[0][prompt_len:]
        return sanitize_candidate_text(tokenizer.decode(completion, skip_special_tokens=True))


def append_request_log(entry: dict[str, Any]) -> None:
    line = json.dumps(entry, ensure_ascii=False)
    with REQUEST_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def make_handler(server_state: AdapterChatServer):
    class Handler(BaseHTTPRequestHandler):
        @staticmethod
        def _build_response_object(response_id: str, model_name: str, content: str, status: str) -> dict[str, Any]:
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

        def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

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
            self.wfile.write(f"data: {json.dumps(role_event, ensure_ascii=False)}\n\n".encode("utf-8"))
            self.wfile.flush()

            for chunk in self._chunk_text(content, 256):
                event = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model_name,
                    "choices": [{"index": 0, "delta": {"content": chunk}, "finish_reason": None}],
                }
                self.wfile.write(f"data: {json.dumps(event, ensure_ascii=False)}\n\n".encode("utf-8"))
                self.wfile.flush()

            final_event = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model_name,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            }
            self.wfile.write(f"data: {json.dumps(final_event, ensure_ascii=False)}\n\n".encode("utf-8"))
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()

        def _send_sse_response(self, content: str, model_name: str) -> None:
            response_id = f"resp_{uuid.uuid4().hex}"
            item_id = f"msg_{uuid.uuid4().hex}"
            sequence_number = 0

            def emit(event: dict[str, Any]) -> None:
                nonlocal sequence_number
                sequence_number += 1
                event.setdefault("sequence_number", sequence_number)
                self.wfile.write(f"data: {json.dumps(event, ensure_ascii=False)}\n\n".encode("utf-8"))
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
                    "response": self._build_response_object(response_id, model_name, "", "in_progress"),
                }
            )
            emit(
                {
                    "type": "response.in_progress",
                    "response": self._build_response_object(response_id, model_name, "", "in_progress"),
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
            for chunk in self._chunk_text(content, 256):
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
                    "response": self._build_response_object(response_id, model_name, content, "completed"),
                }
            )
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()

        @staticmethod
        def _chunk_text(content: str, chunk_size: int) -> list[str]:
            return [content[index : index + chunk_size] for index in range(0, len(content), chunk_size)] or [""]

        def _read_json(self) -> dict[str, Any]:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            if not raw_body:
                return {}
            return json.loads(raw_body.decode("utf-8"))

        def do_GET(self) -> None:  # noqa: N802
            append_request_log({"ts": int(time.time()), "method": "GET", "path": self.path})
            if self.path == "/health":
                self._send_json({"ok": True, "model": server_state.args.model_name})
                return
            if self.path == "/v1/models":
                self._send_json(
                    {
                        "object": "list",
                        "data": [
                            {
                                "id": server_state.args.model_name,
                                "object": "model",
                                "created": int(time.time()),
                                "owned_by": "quantum-gpt",
                            }
                        ],
                    }
                )
                return
            self._send_json({"error": f"Unsupported route: {self.path}"}, status=HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:  # noqa: N802
            try:
                payload = self._read_json()
                append_request_log(
                    {
                        "ts": int(time.time()),
                        "method": "POST",
                        "path": self.path,
                        "model": payload.get("model"),
                        "stream": payload.get("stream"),
                        "has_messages": isinstance(payload.get("messages"), list),
                        "has_input": payload.get("input") is not None,
                    }
                )
                if self.path == "/v1/chat/completions":
                    self._handle_chat_completions(payload)
                    return
                if self.path == "/v1/responses":
                    self._handle_responses(payload)
                    return
                self._send_json({"error": f"Unsupported route: {self.path}"}, status=HTTPStatus.NOT_FOUND)
            except Exception as exc:  # noqa: BLE001
                append_request_log(
                    {
                        "ts": int(time.time()),
                        "method": "POST",
                        "path": self.path,
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                    }
                )
                self._send_json(
                    {"error": {"message": f"{type(exc).__name__}: {exc}", "type": "server_error"}},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR,
                )

        def _extract_messages(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
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
                    role = normalize_role(item.get("role", "user"))
                    content = item.get("content", "")
                    extracted.append({"role": role, "content": content})
                if extracted:
                    return extracted
            raise ValueError("Request does not contain supported `messages` or `input` content")

        def _handle_chat_completions(self, payload: dict[str, Any]) -> None:
            model_name = str(payload.get("model") or server_state.args.model_name)
            messages = self._extract_messages(payload)
            max_new_tokens = payload.get("max_completion_tokens") or payload.get("max_tokens")
            temperature = payload.get("temperature")
            content = server_state.generate_text(
                messages,
                max_new_tokens=int(max_new_tokens) if max_new_tokens is not None else None,
                temperature=float(temperature) if temperature is not None else None,
            )
            if bool(payload.get("stream")):
                self._send_sse_chat_completion(content, model_name)
                return
            now = int(time.time())
            self._send_json(
                {
                    "id": f"chatcmpl-{uuid.uuid4().hex}",
                    "object": "chat.completion",
                    "created": now,
                    "model": model_name,
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": content},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                }
            )

        def _handle_responses(self, payload: dict[str, Any]) -> None:
            model_name = str(payload.get("model") or server_state.args.model_name)
            messages = self._extract_messages(payload)
            max_new_tokens = payload.get("max_output_tokens") or payload.get("max_completion_tokens")
            temperature = payload.get("temperature")
            content = server_state.generate_text(
                messages,
                max_new_tokens=int(max_new_tokens) if max_new_tokens is not None else None,
                temperature=float(temperature) if temperature is not None else None,
            )
            if bool(payload.get("stream")):
                self._send_sse_response(content, model_name)
                return
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
                            "content": [{"type": "output_text", "text": content, "annotations": []}],
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
    server_state = AdapterChatServer(args)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(server_state))
    print(
        json.dumps(
            {
                "stage": "server_ready",
                "host": args.host,
                "port": args.port,
                "model_name": args.model_name,
                "base_model": str(args.base_model),
                "adapter": str(args.adapter) if args.adapter else None,
                "device": str(server_state.device),
                "turboquant_cache": {
                    "enabled": bool(args.enable_turboquant_cache),
                    "nbits": args.turboquant_nbits,
                    "secondary_nbits": args.turboquant_secondary_nbits,
                    "group_size": args.turboquant_group_size,
                    "residual_length": args.turboquant_residual_length,
                    "axis_key": args.turboquant_axis_key,
                    "axis_value": args.turboquant_axis_value,
                    "rotation": args.turboquant_rotation,
                    "seed": args.turboquant_seed,
                },
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

#!/usr/bin/env python3
"""Minimal stdio MCP server exposing the hosted quantum-intelligence-v0.1.0 model.

Claude Code (the agent) decides *when* to call this tool. The remote service is a
RAG-backed Qwen3.6-27B endpoint, so retrieval over quantum SDK docs happens
automatically inside the tool. RAG is therefore "opted in" exactly when Claude
chooses to call `ask_quantum_intelligence`, and "opted out" otherwise.

No third-party dependencies: implements JSON-RPC 2.0 over stdio directly.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "quantum-intelligence"
SERVER_VERSION = "0.1.0"

URL = os.environ.get("QUANTUM_INTELLIGENCE_URL", "")
API_KEY = os.environ.get("QUANTUM_INTELLIGENCE_API_KEY", "")
MODEL_LABEL = "quantum-intelligence-v0.1.0"
DEFAULT_MAX_TOKENS = int(os.environ.get("QUANTUM_INTELLIGENCE_MAX_TOKENS", "1024"))
TIMEOUT_SECONDS = float(os.environ.get("QUANTUM_INTELLIGENCE_TIMEOUT", "180"))

TOOLS = [
    {
        "name": "ask_quantum_intelligence",
        "description": (
            "Ask quantum-intelligence-v0.1.0, a specialist model (Qwen3.6-27B) with "
            "built-in retrieval over quantum SDK documentation (Qiskit, PennyLane, "
            "Cirq, TKET/Quantinuum, TensorCircuit, etc.). Call this ONLY when the task "
            "needs authoritative quantum-computing knowledge, quantum SDK APIs, quantum "
            "algorithms, or hardware specifics. For general/non-quantum work, answer "
            "yourself instead of calling this tool. Retrieval (RAG) is performed "
            "automatically by the service for substantive questions."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The quantum-computing question or instruction to send.",
                },
                "system": {
                    "type": "string",
                    "description": "Optional system/role guidance for the specialist model.",
                },
                "max_tokens": {
                    "type": "integer",
                    "description": f"Max output tokens (default {DEFAULT_MAX_TOKENS}).",
                },
            },
            "required": ["question"],
        },
    }
]


def call_model(question: str, system: str | None, max_tokens: int) -> str:
    if not URL or not API_KEY:
        raise RuntimeError("QUANTUM_INTELLIGENCE_URL / QUANTUM_INTELLIGENCE_API_KEY are not set.")
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": question})
    body = json.dumps(
        {
            "model": MODEL_LABEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.2,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
    )
    # Bypass any local proxy for this direct HTTPS call.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=TIMEOUT_SECONDS) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    choice = data["choices"][0]["message"]
    text = choice.get("content") or ""
    usage = data.get("usage", {})
    pt = usage.get("prompt_tokens")
    rag_note = ""
    if isinstance(pt, int):
        rag_note = (
            f"\n\n[quantum-intelligence: prompt_tokens={pt}"
            f"{' (RAG context retrieved)' if pt > 300 else ' (no RAG context)'}]"
        )
    return text + rag_note


def make_result(text: str, is_error: bool = False) -> dict:
    return {
        "content": [{"type": "text", "text": text}],
        "isError": is_error,
    }


def handle(req: dict) -> dict | None:
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        }
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = req.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}
        if name != "ask_quantum_intelligence":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": make_result(f"Unknown tool: {name}", is_error=True),
            }
        try:
            text = call_model(
                question=args.get("question", ""),
                system=args.get("system"),
                max_tokens=int(args.get("max_tokens") or DEFAULT_MAX_TOKENS),
            )
            return {"jsonrpc": "2.0", "id": req_id, "result": make_result(text)}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:500]
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": make_result(
                    f"HTTP {exc.code} from quantum-intelligence service: {detail}",
                    is_error=True,
                ),
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": make_result(f"Error calling service: {exc}", is_error=True),
            }
    # Unknown method
    if req_id is not None:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }
    return None


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(req)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import importlib.util
from argparse import Namespace
from pathlib import Path
from typing import Any

from quantum_rag.corpus import DocumentChunk
from quantum_rag.index import QuantumRAGIndex


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "serve_qwen36_rag_codex_proxy.py"
SPEC = importlib.util.spec_from_file_location("serve_qwen36_rag_codex_proxy", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
proxy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(proxy)


def _make_index(path: Path) -> Path:
    chunks = [
        DocumentChunk(
            "arclight-install",
            "/docs/arclight-isq/install.md",
            "install.md",
            "Arclight ISQ install uses the isqc compiler and local setup commands.",
            0,
            70,
        ),
        DocumentChunk(
            "qiskit-bell",
            "/docs/qiskit/bell.md",
            "bell.md",
            "Qiskit can build a Bell pair with h, cx, measure, and counts.",
            0,
            66,
        ),
    ]
    index = QuantumRAGIndex.build(chunks, max_features=128, dense_components=2)
    index.save(path)
    return path


def test_extracts_user_text_from_responses_messages() -> None:
    payload = {
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": "system"}]},
            {"role": "user", "content": [{"type": "input_text", "text": "How do I install Arclight ISQ?"}]},
        ]
    }

    assert proxy.extract_request_text(payload) == "How do I install Arclight ISQ?"


def test_extracts_user_text_from_chat_messages() -> None:
    payload = {
        "messages": [
            {"role": "system", "content": "system"},
            {"role": "user", "content": "How do I build a Bell pair in Qiskit?"},
        ]
    }

    assert proxy.extract_request_text(payload) == "How do I build a Bell pair in Qiskit?"


def test_generate_injects_retrieved_context(monkeypatch: Any, tmp_path: Path) -> None:
    index_path = _make_index(tmp_path / "index.pkl.gz")
    captured: dict[str, Any] = {}

    class FakeChatClient:
        def __init__(self, **kwargs: Any) -> None:
            captured["client_kwargs"] = kwargs

        def generate(self, messages: list[dict[str, str]], *, max_output_tokens: int, temperature: float) -> str:
            captured["messages"] = messages
            captured["max_output_tokens"] = max_output_tokens
            captured["temperature"] = temperature
            return "Use isqc for the Arclight ISQ install [C1]."

    monkeypatch.setattr(proxy, "ChatCompletionsClient", FakeChatClient)
    state = proxy.RAGCodexState(
        Namespace(
            index=index_path,
            top_k=1,
            alpha=0.55,
            disable_query_expansion=False,
            max_chunks_per_source=1,
            max_context_chars=500,
            max_output_tokens=123,
            temperature=0.0,
            timeout_seconds=30.0,
            backend_api_style="chat",
            backend_base_url="http://127.0.0.1:8011",
            backend_model="qwen3.6-27b-rag",
            backend_api_key="dummy",
        )
    )

    answer = state.generate({"input": "How do I install the Arclight ISQ language?"})

    assert answer.startswith("Use isqc")
    rendered = "\n".join(message["content"] for message in captured["messages"])
    assert "Retrieved context" in rendered
    assert "Arclight ISQ install" in rendered
    assert "[C1]" in rendered
    assert captured["client_kwargs"]["model"] == "qwen3.6-27b-rag"
    assert captured["max_output_tokens"] == 123


def test_responses_payload_is_codex_parseable() -> None:
    payload = proxy.responses_payload("quantum-intelligence-v0.1.0", "OK")

    assert payload["model"] == "quantum-intelligence-v0.1.0"
    assert payload["output_text"] == "OK"
    assert payload["output"][0]["content"][0]["type"] == "output_text"


def test_streaming_events_include_response_completed() -> None:
    events = proxy.streaming_events("quantum-intelligence-v0.1.0", "OK")

    event_names = [event for event, _payload in events]
    assert "response.output_text.delta" in event_names
    assert event_names[-1] == "response.completed"
    assert events[-1][1]["response"]["output_text"] == "OK"

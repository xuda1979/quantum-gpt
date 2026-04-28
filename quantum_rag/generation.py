from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from .retrieval import RetrievedChunk


RAG_SYSTEM_PROMPT = (
    "You are a quantum computing and quantum software RAG assistant for the quantum-gpt project. "
    "Answer using only the provided retrieved context when making factual claims. "
    "If the context is insufficient, say what is missing. "
    "Prefer concrete implementation guidance for quantum SDKs, algorithms, and repo-specific workflows. "
    "Cite claims inline with [C1], [C2], etc."
)


@dataclass(frozen=True)
class ResponsesClient:
    base_url: str
    model: str
    timeout_seconds: float = 180.0

    def generate(self, messages: list[dict[str, Any]], *, max_output_tokens: int, temperature: float) -> str:
        payload = {
            "model": self.model,
            "input": messages,
            "stream": False,
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
        }
        request = urllib.request.Request(
            url=self.base_url.rstrip("/") + "/v1/responses",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer dummy",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Responses API error {exc.code}: {raw}") from exc

        output_text = body.get("output_text")
        if isinstance(output_text, str):
            return output_text

        output = body.get("output", [])
        if isinstance(output, list):
            parts: list[str] = []
            for item in output:
                if not isinstance(item, dict):
                    continue
                for content in item.get("content", []):
                    if not isinstance(content, dict):
                        continue
                    if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                        parts.append(content["text"])
            if parts:
                return "\n".join(parts).strip()

        raise RuntimeError("Responses API returned no parseable text output")


@dataclass(frozen=True)
class ChatCompletionsClient:
    """Client for OpenAI-compatible /v1/chat/completions endpoints."""

    base_url: str
    model: str
    timeout_seconds: float = 180.0
    api_key: str = "dummy"

    def generate(self, messages: list[dict[str, Any]], *, max_output_tokens: int, temperature: float) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_output_tokens,
            "temperature": temperature,
            "stream": False,
        }
        request = urllib.request.Request(
            url=self.base_url.rstrip("/") + "/v1/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"ChatCompletions API error {exc.code}: {raw}") from exc

        choices = body.get("choices", [])
        if choices and isinstance(choices[0], dict):
            message = choices[0].get("message", {})
            content = message.get("content")
            if isinstance(content, str):
                return content.strip()

        raise RuntimeError("ChatCompletions API returned no parseable text output")


def format_retrieved_context(chunks: list[RetrievedChunk]) -> str:
    sections: list[str] = []
    for item in chunks:
        sections.append(
            "\n".join(
                [
                    f"[C{item.rank}] source={item.chunk.source_path}",
                    f"[C{item.rank}] score={item.final_score:.4f} lexical={item.lexical_score:.4f} semantic={item.semantic_score:.4f}",
                    f"[C{item.rank}] text:",
                    item.chunk.text,
                ]
            )
        )
    return "\n\n".join(sections)


def build_rag_messages(query: str, chunks: list[RetrievedChunk]) -> list[dict[str, str]]:
    context = format_retrieved_context(chunks)
    user_prompt = (
        "Use the retrieved context below to answer the question.\n\n"
        f"Question:\n{query}\n\n"
        "Retrieved context:\n"
        f"{context}\n\n"
        "Return a grounded answer with inline citations like [C1]."
    )
    return [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

from __future__ import annotations

import json
import re
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


TOKEN_RE = re.compile(r"[A-Za-z0-9_./:+-]+")


def _query_terms(query: str | None) -> list[str]:
    if not query:
        return []
    terms = [token.lower() for token in TOKEN_RE.findall(query) if len(token) > 2]
    if "isq" in terms and "isqc" not in terms:
        terms.append("isqc")
    if "arclight" in terms and "isq" not in terms:
        terms.append("isq")
    return list(dict.fromkeys(terms))


def _best_context_window(text: str, max_chars: int, query: str | None) -> str:
    terms = _query_terms(query)
    if not terms:
        return text[:max_chars].rstrip()

    paragraphs: list[tuple[int, str]] = []
    cursor = 0
    for block in re.split(r"(\n\s*\n)", text):
        if not block:
            continue
        start = text.find(block, cursor)
        if start < 0:
            start = cursor
        cursor = start + len(block)
        stripped = block.strip()
        if not stripped or stripped.startswith("[source:"):
            continue
        paragraphs.append((start, stripped))

    best_start = 0
    best_score = -1
    for start, paragraph in paragraphs:
        lowered = paragraph.lower()
        score = sum(1 for term in terms if term in lowered)
        if "install" in lowered:
            score += 1
        if "isqc" in lowered:
            score += 2
        if score > best_score:
            best_score = score
            best_start = start

    window_start = max(0, best_start - max_chars // 5)
    window_end = min(len(text), window_start + max_chars)
    return text[window_start:window_end].strip()


def _trim_context_text(text: str, max_chars: int | None, *, query: str | None = None) -> str:
    if max_chars is None or max_chars <= 0 or len(text) <= max_chars:
        return text
    trimmed = _best_context_window(text, max_chars, query)
    return f"{trimmed}\n...[trimmed]"


def format_retrieved_context(
    chunks: list[RetrievedChunk],
    *,
    max_chars_per_chunk: int | None = None,
    query: str | None = None,
) -> str:
    sections: list[str] = []
    for item in chunks:
        sections.append(
            "\n".join(
                [
                    f"[C{item.rank}] source={item.chunk.source_path}",
                    f"[C{item.rank}] score={item.final_score:.4f} lexical={item.lexical_score:.4f} semantic={item.semantic_score:.4f}",
                    f"[C{item.rank}] text:",
                    _trim_context_text(item.chunk.text, max_chars_per_chunk, query=query),
                ]
            )
        )
    return "\n\n".join(sections)


def build_rag_messages(
    query: str,
    chunks: list[RetrievedChunk],
    *,
    max_chars_per_chunk: int | None = None,
) -> list[dict[str, str]]:
    context = format_retrieved_context(chunks, max_chars_per_chunk=max_chars_per_chunk, query=query)
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

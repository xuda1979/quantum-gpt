"""Lightweight disk-backed answer cache for quantum RAG.

The cache maps (query, index_summary_hash) → generated answer so that
repeated or near-identical queries against the same index do not trigger
redundant generation calls.

The design is deliberately simple:
- JSON-lines file on disk (one record per line)
- SHA-256 key over (normalized query + index summary hash)
- No eviction or TTL yet — the cache is append-only and cheap to rebuild
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CacheEntry:
    key: str
    query: str
    index_hash: str
    answer: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CacheEntry":
        return cls(
            key=str(data["key"]),
            query=str(data["query"]),
            index_hash=str(data["index_hash"]),
            answer=str(data["answer"]),
            metadata=data.get("metadata", {}),
        )


def _normalize_query(query: str) -> str:
    return " ".join(query.lower().split())


def make_cache_key(query: str, index_hash: str) -> str:
    normalized = _normalize_query(query)
    payload = f"{normalized}|{index_hash}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def index_summary_hash(summary: dict[str, object]) -> str:
    """Compute a stable hash of an index summary dict."""
    canonical = json.dumps(summary, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


class AnswerCache:
    """Append-only JSONL answer cache backed by a local file."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._entries: dict[str, CacheEntry] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                entry = CacheEntry.from_dict(data)
                self._entries[entry.key] = entry
            except (json.JSONDecodeError, KeyError, TypeError):
                continue

    def get(self, query: str, index_hash: str) -> CacheEntry | None:
        key = make_cache_key(query, index_hash)
        return self._entries.get(key)

    def put(
        self,
        query: str,
        index_hash: str,
        answer: str,
        metadata: dict[str, Any] | None = None,
    ) -> CacheEntry:
        key = make_cache_key(query, index_hash)
        entry = CacheEntry(
            key=key,
            query=query,
            index_hash=index_hash,
            answer=answer,
            metadata=metadata or {},
        )
        self._entries[key] = entry
        self._append(entry)
        return entry

    def _append(self, entry: CacheEntry) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, key: str) -> bool:
        return key in self._entries

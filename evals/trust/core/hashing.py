"""Canonical hashing helpers for the trustable evaluation subsystem.

All hashes are SHA-256, computed over a canonical serialization:

  - Files: raw bytes (no newline normalization, no path).
  - dicts:  ``json.dumps(obj, sort_keys=True, separators=(",", ":"))``.
  - strings: UTF-8 encoded bytes.
  - composite: a length-prefixed concatenation of the above.

The canonical-JSON rule is critical: it guarantees that two semantically
identical payloads produce the same hash even if key ordering differs.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable

HEX_LEN = 64
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()


def hash_bytes(data: bytes) -> str:
    """SHA-256 of raw bytes, hex-encoded."""
    return hashlib.sha256(data).hexdigest()


def hash_text(text: str) -> str:
    """SHA-256 of a string (UTF-8 encoded)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hash_file(path: str | os.PathLike[str]) -> str:
    """SHA-256 of a file's raw bytes. Raises FileNotFoundError if missing."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"cannot hash missing file: {p}")
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_json(obj: Any) -> str:
    """SHA-256 over canonical JSON (sorted keys, no whitespace)."""
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def hash_files(paths: Iterable[str | os.PathLike[str]]) -> str:
    """Aggregate SHA-256 over a sorted list of (relpath, hash) pairs.

    Used to produce a single content-address for a directory or task
    suite. The input is a list of paths; each path is hashed and the
    pair (basename, hash) is folded into the aggregate.
    """
    pairs: list[tuple[str, str]] = []
    for p in sorted(paths, key=lambda x: str(x)):
        rel = Path(p).name
        pairs.append((rel, hash_file(p)))
    return hash_json(pairs)


def short(h: str, n: int = 12) -> str:
    """Short-form hash for human display."""
    if len(h) < n:
        return h
    return h[:n]


def is_hash(s: str) -> bool:
    """True iff ``s`` looks like a 64-char hex SHA-256."""
    if len(s) != HEX_LEN:
        return False
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

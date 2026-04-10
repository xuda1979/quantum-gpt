#!/usr/bin/env python3
"""Audit a chosen model source before any local snapshot or Huanxin handoff.

Purpose:
- make the execution-source decision concrete
- verify whether a model id resolves from this machine via Hugging Face metadata
- emit a JSON artifact suitable for memory/logging/runbooks

This does not download weights. It is a lightweight source-truth check.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone


DEFAULT_HF_ENDPOINT = "https://huggingface.co"


def normalize_hf_endpoint(endpoint: str | None) -> str:
    value = (endpoint or os.environ.get("HF_ENDPOINT") or DEFAULT_HF_ENDPOINT).strip()
    return value.rstrip("/")


def resolve_model_info_url(model_id: str, endpoint: str | None = None) -> str:
    encoded = urllib.parse.quote(model_id, safe="/")
    return f"{normalize_hf_endpoint(endpoint)}/api/models/{encoded}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", required=True, help="Model id to audit, e.g. Qwen/Qwen2.5-1.5B-Instruct")
    parser.add_argument(
        "--expected-family-substring",
        default="qwen",
        help="Case-insensitive substring expected in returned metadata/tags/id",
    )
    parser.add_argument(
        "--out",
        help="Optional path to write the JSON report. Prints to stdout either way.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=20.0,
        help="HTTP timeout for the Hugging Face model metadata request",
    )
    parser.add_argument(
        "--hf-endpoint",
        help="Optional Hugging Face-compatible endpoint, for example https://hf-mirror.com",
    )
    return parser.parse_args()


def fetch_model_info(model_id: str, timeout_seconds: float, endpoint: str | None = None) -> dict:
    url = resolve_model_info_url(model_id, endpoint)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "quantum-rnd-source-audit/1.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        body = response.read().decode("utf-8")
    return json.loads(body)


def family_evidence(info: dict, expected: str) -> dict[str, object]:
    lowered_expected = expected.lower()
    tags = info.get("tags") or []
    architectures = info.get("config", {}).get("architectures") or []
    model_type = info.get("config", {}).get("model_type")
    searchable = [
        str(info.get("id", "")),
        str(info.get("author", "")),
        str(info.get("pipeline_tag", "")),
        str(model_type or ""),
        *[str(tag) for tag in tags],
        *[str(item) for item in architectures],
    ]
    hits = [item for item in searchable if lowered_expected in item.lower()]
    return {
        "expected_family_substring": expected,
        "matched": bool(hits),
        "hits": hits,
    }


def main() -> int:
    args = parse_args()
    summary: dict[str, object] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "model_id": args.model_id,
        "hf_endpoint": normalize_hf_endpoint(args.hf_endpoint),
        "status": "error",
    }

    try:
        info = fetch_model_info(args.model_id, args.timeout_seconds, args.hf_endpoint)
    except urllib.error.HTTPError as exc:
        summary.update(
            {
                "stage": "fetch_model_info",
                "error_type": type(exc).__name__,
                "http_status": exc.code,
                "error": str(exc),
            }
        )
        payload = json.dumps(summary, indent=2, ensure_ascii=False)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as handle:
                handle.write(payload + "\n")
        print(payload)
        return 1
    except Exception as exc:
        summary.update(
            {
                "stage": "fetch_model_info",
                "error_type": type(exc).__name__,
                "error": str(exc),
                "timeout_seconds": args.timeout_seconds,
            }
        )
        payload = json.dumps(summary, indent=2, ensure_ascii=False)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as handle:
                handle.write(payload + "\n")
        print(payload)
        return 1

    tags = info.get("tags") or []
    siblings = info.get("siblings") or []
    config = info.get("config") or {}
    family = family_evidence(info, args.expected_family_substring)

    summary.update(
        {
            "status": "ok",
            "resolved_id": info.get("id"),
            "private": info.get("private"),
            "disabled": info.get("disabled"),
            "gated": info.get("gated"),
            "downloads": info.get("downloads"),
            "likes": info.get("likes"),
            "pipeline_tag": info.get("pipeline_tag"),
            "library_name": info.get("library_name"),
            "tags_sample": tags[:20],
            "file_count": len(siblings),
            "config_model_type": config.get("model_type"),
            "config_architectures": config.get("architectures"),
            "family_evidence": family,
        }
    )

    payload = json.dumps(summary, indent=2, ensure_ascii=False)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(payload + "\n")
    print(payload)
    return 0 if family.get("matched") else 2


if __name__ == "__main__":
    raise SystemExit(main())

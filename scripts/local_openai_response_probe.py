#!/usr/bin/env python3
"""Minimal stdlib probe for the local OpenAI-compatible responses endpoint."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--model", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--max-output-tokens", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=120.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = {
        "model": args.model,
        "input": args.input,
        "stream": False,
        "max_output_tokens": args.max_output_tokens,
    }
    request = urllib.request.Request(
        url=args.base_url.rstrip("/") + "/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer dummy",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(
            json.dumps(
                {
                    "ok": False,
                    "status": exc.code,
                    "body": body,
                },
                ensure_ascii=False,
            )
        )
        return 1

    print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

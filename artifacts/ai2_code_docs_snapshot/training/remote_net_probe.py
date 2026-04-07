#!/usr/bin/env python3
import json
import socket
import sys
import urllib.request
from urllib.error import URLError, HTTPError

TARGETS = [
    "https://huggingface.co",
    "https://hf-mirror.com",
]


def check(url: str, timeout: float = 5.0) -> dict:
    socket.setdefaulttimeout(timeout)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return {
                "url": url,
                "status": "ok",
                "http_status": getattr(resp, "status", None),
                "final_url": getattr(resp, "url", url),
            }
    except HTTPError as e:
        return {
            "url": url,
            "status": "http_error",
            "error_type": type(e).__name__,
            "http_status": e.code,
            "reason": str(e),
        }
    except URLError as e:
        return {
            "url": url,
            "status": "url_error",
            "error_type": type(e).__name__,
            "reason": str(e.reason),
        }
    except Exception as e:
        return {
            "url": url,
            "status": "error",
            "error_type": type(e).__name__,
            "reason": str(e),
        }


def main() -> int:
    results = [check(url) for url in TARGETS]
    json.dump({"results": results}, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

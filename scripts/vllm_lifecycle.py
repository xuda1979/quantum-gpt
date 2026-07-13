#!/usr/bin/env python3
"""vLLM lifecycle helper: sleep / wake-up / hot-swap LoRA adapters.

This wraps vLLM's process-keeping-alive APIs so the RL+distill orchestrator
can pause vLLM (free NPU memory for the trainer burst) and resume it (reload
weights from host pinned memory) WITHOUT a full process restart on every
round. When the running vLLM does not support these endpoints, the helper
falls back gracefully so callers can degrade to the existing kill/restart
path.

API surface used (vLLM >= 0.6 for sleep/wake-up; >= 0.7 for load_lora_adapter):
  POST /v1/sleep            {"level": 1|2}   level=1 keeps weights in host mem
  POST /v1/wake_up          {}               reload weights onto NPU
  POST /v1/load_lora_adapter {"lora_name": str, "lora_local_path": str}
  GET  /v1/models                            health + capability probe

Usage (from bash orchestrator):
  python3 scripts/vllm_lifecycle.py probe   --base-url http://127.0.0.1:8007 --api-key K
  python3 scripts/vllm_lifecycle.py sleep   --base-url ... --level 1
  python3 scripts/vllm_lifecycle.py wake    --base-url ...
  python3 scripts/vllm_lifecycle.py load-lora --base-url ... --lora-name rl_distill_latest --lora-path /path/to/adapter
  python3 scripts/vllm_lifecycle.py wait-ready --base-url ... --served-name qwen36-27b-rl-distill --timeout 600

Exit codes:
  0  success
  2  endpoint not supported by this vLLM (caller should fall back)
  3  transport error / timeout / unexpected status
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from urllib.parse import urljoin

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None


def _client(base_url: str, api_key: str, timeout: float):
    if requests is None:
        raise SystemExit(3)
    sess = requests.Session()
    sess.headers.update({"Authorization": f"Bearer {api_key}"})
    return sess


def _post(sess, base_url, path, body, timeout):
    url = urljoin(base_url if base_url.endswith("/") else base_url + "/", path.lstrip("/"))
    try:
        r = sess.post(url, json=body, timeout=timeout)
    except Exception as exc:
        print(f"[vllm-lifecycle] transport error on {path}: {exc}", file=sys.stderr)
        return None, 3
    if r.status_code == 404:
        print(f"[vllm-lifecycle] {path} not supported (404)", file=sys.stderr)
        return None, 2
    if r.status_code >= 400:
        print(f"[vllm-lifecycle] {path} -> {r.status_code}: {r.text[:300]}", file=sys.stderr)
        return None, 3
    try:
        return r.json(), 0
    except Exception:
        return {"raw": r.text}, 0


def _get(sess, base_url, path, timeout):
    url = urljoin(base_url if base_url.endswith("/") else base_url + "/", path.lstrip("/"))
    try:
        r = sess.get(url, timeout=timeout)
    except Exception as exc:
        print(f"[vllm-lifecycle] transport error on {path}: {exc}", file=sys.stderr)
        return None, 3
    if r.status_code == 404:
        return None, 2
    if r.status_code >= 400:
        print(f"[vllm-lifecycle] {path} -> {r.status_code}: {r.text[:300]}", file=sys.stderr)
        return None, 3
    try:
        return r.json(), 0
    except Exception:
        return {"raw": r.text}, 0


def cmd_probe(args):
    sess = _client(args.base_url, args.api_key, args.timeout)
    data, rc = _get(sess, args.base_url, "/v1/models", args.timeout)
    if rc != 0:
        return rc
    caps = {"models": data, "supports_sleep": False, "supports_load_lora": False}
    # Probe sleep endpoint with a no-op-ish check: we do NOT actually sleep here,
    # we just check the route exists. Use an empty body HEAD-like POST; vLLM will
    # reject with 400/422 if the route exists but body is wrong, or 404 if missing.
    url = args.base_url.rstrip("/") + "/v1/sleep"
    try:
        r = sess.post(url, json={}, timeout=min(args.timeout, 5.0))
        # 400/422 means route exists but wants a proper level -> supported
        # 200 means it actually slept (we will wake it back up below)
        # 404 means unsupported
        if r.status_code != 404:
            caps["supports_sleep"] = True
            # If it actually slept (200), wake it back up so we leave vLLM ready.
            if 200 <= r.status_code < 300:
                sess.post(
                    args.base_url.rstrip("/") + "/v1/wake_up",
                    json={},
                    timeout=min(args.timeout, 10.0),
                )
        r2 = sess.post(
            args.base_url.rstrip("/") + "/v1/load_lora_adapter",
            json={},
            timeout=min(args.timeout, 5.0),
        )
        if r2.status_code != 404:
            caps["supports_load_lora"] = True
    except Exception as exc:
        print(f"[vllm-lifecycle] probe transport error: {exc}", file=sys.stderr)
        return 3
    print(json.dumps(caps, ensure_ascii=False))
    return 0


def cmd_sleep(args):
    sess = _client(args.base_url, args.api_key, args.timeout)
    body = {"level": int(args.level)}
    data, rc = _post(sess, args.base_url, "/v1/sleep", body, args.timeout)
    if rc == 2:
        # Unsupported: tell caller to fall back to kill/restart.
        print("[vllm-lifecycle] sleep unsupported; caller should kill vLLM", file=sys.stderr)
        return 2
    if rc != 0:
        return rc
    # Give the runtime a moment to actually release NPU memory.
    time.sleep(float(args.settle_seconds))
    print(json.dumps({"ok": True, "level": int(args.level)}, ensure_ascii=False))
    return 0


def cmd_wake(args):
    sess = _client(args.base_url, args.api_key, args.timeout)
    data, rc = _post(sess, args.base_url, "/v1/wake_up", {}, max(args.timeout, 120.0))
    if rc == 2:
        print("[vllm-lifecycle] wake_up unsupported; caller should relaunch vLLM", file=sys.stderr)
        return 2
    if rc != 0:
        return rc
    # Wait for /v1/models to come back healthy.
    deadline = time.time() + max(args.timeout, 120.0)
    while time.time() < deadline:
        m, _ = _get(sess, args.base_url, "/v1/models", 10.0)
        if m and isinstance(m, dict) and m.get("data"):
            print(json.dumps({"ok": True, "models": m}, ensure_ascii=False))
            return 0
        time.sleep(2.0)
    print("[vllm-lifecycle] wake_up timed out waiting for /v1/models", file=sys.stderr)
    return 3


def cmd_load_lora(args):
    sess = _client(args.base_url, args.api_key, args.timeout)
    body = {"lora_name": args.lora_name, "lora_local_path": args.lora_path}
    data, rc = _post(sess, args.base_url, "/v1/load_lora_adapter", body, max(args.timeout, 60.0))
    if rc == 2:
        print(
            "[vllm-lifecycle] load_lora_adapter unsupported; caller must restart vLLM with --lora-modules",
            file=sys.stderr,
        )
        return 2
    if rc != 0:
        return rc
    # Verify the adapter is now registered by listing models (vLLM exposes LoRA
    # adapters as served model names with the lora_name).
    m, _ = _get(sess, args.base_url, "/v1/models", 10.0)
    registered = False
    if m and isinstance(m, dict):
        for item in m.get("data", []) or []:
            if item.get("id") == args.lora_name:
                registered = True
                break
    print(
        json.dumps(
            {"ok": True, "lora_name": args.lora_name, "registered": registered}, ensure_ascii=False
        )
    )
    return 0 if registered else 3


def cmd_wait_ready(args):
    sess = _client(args.base_url, args.api_key, args.timeout)
    deadline = time.time() + args.timeout
    while time.time() < deadline:
        m, _ = _get(sess, args.base_url, "/v1/models", 10.0)
        if m and isinstance(m, dict):
            for item in m.get("data", []) or []:
                if args.served_name and item.get("id") == args.served_name:
                    print(
                        json.dumps(
                            {"ok": True, "served_name": args.served_name}, ensure_ascii=False
                        )
                    )
                    return 0
                if not args.served_name:
                    print(json.dumps({"ok": True, "models": m}, ensure_ascii=False))
                    return 0
        time.sleep(args.poll_seconds)
    print(
        f"[vllm-lifecycle] timed out waiting for {args.served_name or 'any model'}", file=sys.stderr
    )
    return 3


def build_parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base-url", required=True, help="e.g. http://127.0.0.1:8007")
    p.add_argument("--api-key", default="", help="Bearer token (can be 'dummy')")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("probe")
    sp.add_argument("--timeout", type=float, default=30.0, help="per-request timeout seconds")
    sp.set_defaults(func=cmd_probe)

    sp = sub.add_parser("sleep")
    sp.add_argument("--timeout", type=float, default=60.0, help="per-request timeout seconds")
    sp.add_argument(
        "--level",
        choices=["1", "2"],
        default="1",
        help="1=keep weights in host mem (fast wake); 2=free all",
    )
    sp.add_argument(
        "--settle-seconds", type=float, default=2.0, help="wait after sleep so NPU memory frees"
    )
    sp.set_defaults(func=cmd_sleep)

    sp = sub.add_parser("wake")
    sp.add_argument("--timeout", type=float, default=300.0, help="per-request timeout seconds")
    sp.set_defaults(func=cmd_wake)

    sp = sub.add_parser("load-lora")
    sp.add_argument("--timeout", type=float, default=60.0, help="per-request timeout seconds")
    sp.add_argument("--lora-name", required=True)
    sp.add_argument(
        "--lora-path", required=True, help="local filesystem path to the LoRA adapter dir"
    )
    sp.set_defaults(func=cmd_load_lora)

    sp = sub.add_parser("wait-ready")
    sp.add_argument("--timeout", type=float, default=300.0, help="total wait timeout seconds")
    sp.add_argument("--served-name", default="", help="model id to look for; empty = any model")
    sp.add_argument("--poll-seconds", type=float, default=5.0)
    sp.set_defaults(func=cmd_wait_ready)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

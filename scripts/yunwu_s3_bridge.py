#!/usr/bin/env python3
"""Bridge Yunwu chat-completions requests between S3 and the live local API."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--s3-root",
        default="nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main",
    )
    parser.add_argument("--request-prefix", default="relay/yunwu/requests")
    parser.add_argument("--response-prefix", default="relay/yunwu/responses")
    parser.add_argument(
        "--base-url", default=os.environ.get("YUNWU_PROXY_BASE_URL", "https://api.yunwu.ai/v1")
    )
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    parser.add_argument("--idle-sleep-seconds", type=float, default=3.0)
    parser.add_argument("--once", action="store_true")
    return parser.parse_args()


def choose_upstream_api_key(model_name: str) -> str:
    generic = os.environ.get("YUNWU_API_KEY") or os.environ.get("YUNWU_OPENAI_API_KEY")
    claude = os.environ.get("YUNWU_CLAUDE_API_KEY")
    lower_model = model_name.strip().lower()
    if lower_model.startswith("claude") and generic:
        return generic
    if generic:
        return generic
    if lower_model.startswith("claude") and claude:
        return claude
    raise RuntimeError("Missing Yunwu API credentials in environment")


class Relay:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.rclone_bin = os.environ.get("RCLONE_BIN") or shutil.which("rclone")
        if not self.rclone_bin and Path("/Users/daxu/homebrew/bin/rclone").exists():
            self.rclone_bin = "/Users/daxu/homebrew/bin/rclone"
        if not self.rclone_bin:
            raise RuntimeError("rclone is required for yunwu_s3_bridge.py")

    def _remote_dir(self, prefix: str) -> str:
        return self.args.s3_root.rstrip("/") + "/" + prefix.strip("/")

    def _remote_file(self, prefix: str, request_id: str) -> str:
        return self._remote_dir(prefix) + f"/{request_id}.json"

    def _rclone(self, *cmd: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [self.rclone_bin, *cmd],
            capture_output=True,
            text=True,
            check=check,
        )

    def list_ids(self, prefix: str) -> set[str]:
        result = self._rclone("lsf", self._remote_dir(prefix), check=False)
        if result.returncode != 0:
            text = (result.stderr or result.stdout).strip()
            if "directory not found" in text.lower() or "not found" in text.lower():
                return set()
            raise RuntimeError(text or f"rclone lsf failed for {prefix}")
        ids: set[str] = set()
        for line in result.stdout.splitlines():
            stripped = line.strip().rstrip("/")
            if stripped.endswith(".json"):
                ids.add(stripped[:-5])
        return ids

    def read_json(self, prefix: str, request_id: str) -> dict[str, Any]:
        result = self._rclone("cat", self._remote_file(prefix, request_id), check=False)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())
        return json.loads(result.stdout)

    def write_json(self, prefix: str, request_id: str, payload: dict[str, Any]) -> None:
        with tempfile.TemporaryDirectory(prefix="yunwu-s3-bridge-") as tmp_dir:
            local_path = Path(tmp_dir) / f"{request_id}.json"
            local_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            result = self._rclone(
                "copyto",
                str(local_path),
                self._remote_file(prefix, request_id),
                "--s3-no-check-bucket",
                check=False,
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip() or result.stdout.strip())

    def call_upstream(self, payload: dict[str, Any]) -> dict[str, Any]:
        model_name = str(payload.get("model") or "gpt-5.4")
        request = urllib.request.Request(
            self.args.base_url.rstrip("/") + "/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {choose_upstream_api_key(model_name)}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                return {
                    "ok": True,
                    "status": response.status,
                    "response": json.loads(response.read().decode("utf-8")),
                }
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = {"error": {"message": raw, "type": "upstream_error"}}
            return {"ok": False, "status": exc.code, "payload": payload}
        except Exception as exc:  # noqa: BLE001
            return {
                "ok": False,
                "status": 502,
                "payload": {
                    "error": {"message": f"{type(exc).__name__}: {exc}", "type": "relay_error"}
                },
            }

    def process_one(self, request_id: str) -> None:
        envelope = self.read_json(self.args.request_prefix, request_id)
        request_payload = envelope.get("request")
        if not isinstance(request_payload, dict):
            self.write_json(
                self.args.response_prefix,
                request_id,
                {
                    "ok": False,
                    "status": 400,
                    "payload": {
                        "error": {
                            "message": "request envelope missing `request` dict",
                            "type": "invalid_request",
                        }
                    },
                },
            )
            return
        response = self.call_upstream(request_payload)
        response["id"] = request_id
        response["handled_at"] = int(time.time())
        self.write_json(self.args.response_prefix, request_id, response)
        print(
            json.dumps(
                {
                    "stage": "request_handled",
                    "id": request_id,
                    "ok": response.get("ok", False),
                    "status": response.get("status"),
                    "model": request_payload.get("model"),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

    def run(self) -> int:
        print(
            json.dumps(
                {
                    "stage": "bridge_ready",
                    "s3_root": self.args.s3_root,
                    "request_prefix": self.args.request_prefix,
                    "response_prefix": self.args.response_prefix,
                    "base_url": self.args.base_url,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        while True:
            request_ids = self.list_ids(self.args.request_prefix)
            response_ids = self.list_ids(self.args.response_prefix)
            pending_ids = sorted(request_ids - response_ids)
            if pending_ids:
                for request_id in pending_ids:
                    self.process_one(request_id)
            elif self.args.once:
                return 0
            else:
                time.sleep(self.args.idle_sleep_seconds)
                continue
            if self.args.once:
                return 0
            time.sleep(self.args.poll_seconds)


def main() -> int:
    relay = Relay(parse_args())
    return relay.run()


if __name__ == "__main__":
    raise SystemExit(main())

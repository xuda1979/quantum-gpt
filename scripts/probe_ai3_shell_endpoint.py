#!/usr/bin/env python3
"""Summarize Huanxin shell endpoint failures from saved probe artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

_WS_NULL_RE = re.compile(r"wss://[^\"'\s]*/null")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "artifacts",
        nargs="+",
        type=Path,
        help="One or more saved Huanxin probe JSON artifacts to inspect.",
    )
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON output path.")
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def _parse_json_fragment(text: str) -> dict[str, Any] | None:
    try:
        payload = json.loads(text)
    except Exception:
        return None
    if isinstance(payload, dict):
        return payload
    return None


def _extract_response_preview_text(entry: dict[str, Any]) -> dict[str, Any] | None:
    for key in ("responsePreview", "body"):
        raw = entry.get(key)
        if isinstance(raw, str) and raw.strip():
            payload = _parse_json_fragment(raw)
            if payload is not None:
                return payload
    return None


def _scan_entries(container: Any) -> list[dict[str, Any]]:
    if isinstance(container, list):
        return [item for item in container if isinstance(item, dict)]
    return []


def _iter_response_like_entries(payload: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    entries.extend(_scan_entries(payload.get("responses")))
    final = payload.get("final")
    if isinstance(final, dict):
        entries.extend(_scan_entries(final.get("xhrCalls")))
    return entries


def summarize_probe_artifacts(paths: list[Path]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "artifacts": [],
        "env_id": None,
        "env_name": None,
        "pod_name": None,
        "requested_shell_type": None,
        "shell_visit_failures": [],
        "detail_payloads": [],
        "websocket_null_urls": [],
        "websocket_404_errors": [],
        "request_failed_urls": [],
        "shell_endpoint_failure": False,
        "websocket_null_fallback": False,
        "blocker_summary": "No shell endpoint failure detected.",
    }

    for path in paths:
        payload = _load_json(path)
        summary["artifacts"].append(str(path))

        for entry in _iter_response_like_entries(payload):
            url = str(entry.get("url") or "")
            if "getShellVisitUrl" in url:
                post_body = _parse_json_fragment(
                    str(entry.get("body") or entry.get("postData") or "")
                )
                response_payload = _extract_response_preview_text(entry)
                failure = {
                    "artifact": str(path),
                    "url": url,
                    "status": entry.get("status"),
                    "request": post_body,
                    "response": response_payload,
                }
                summary["shell_visit_failures"].append(failure)
                if isinstance(post_body, dict):
                    if summary["env_id"] is None:
                        summary["env_id"] = post_body.get("id")
                    if summary["pod_name"] is None:
                        summary["pod_name"] = post_body.get("podName")
                    if summary["requested_shell_type"] is None:
                        summary["requested_shell_type"] = post_body.get("type")
                if isinstance(response_payload, dict) and response_payload.get("code") == 170022:
                    summary["shell_endpoint_failure"] = True
            elif "/web/develop/v1/detail" in url:
                response_payload = _extract_response_preview_text(entry)
                if isinstance(response_payload, dict):
                    data = response_payload.get("data")
                    if isinstance(data, dict):
                        summary["detail_payloads"].append(
                            {
                                "artifact": str(path),
                                "id": data.get("id"),
                                "name": data.get("name"),
                                "jupyterUrl": data.get("jupyterUrl"),
                                "vscodeUrl": data.get("vscodeUrl"),
                                "failedMessage": data.get("failedMessage"),
                                "podInfoList": data.get("podInfoList"),
                            }
                        )
                        if summary["env_id"] is None:
                            summary["env_id"] = data.get("id")
                        if summary["env_name"] is None:
                            summary["env_name"] = data.get("name")
                        pod_list = data.get("podInfoList")
                        if summary["pod_name"] is None and isinstance(pod_list, list) and pod_list:
                            first_pod = pod_list[0]
                            if isinstance(first_pod, dict):
                                summary["pod_name"] = first_pod.get("podName")

        for entry in _scan_entries(payload.get("requestFailed")):
            url = str(entry.get("url") or "")
            if url:
                summary["request_failed_urls"].append(url)
            if _WS_NULL_RE.search(url):
                summary["websocket_null_urls"].append(url)

        for entry in _scan_entries(payload.get("websockets")):
            url = str(entry.get("url") or "")
            if _WS_NULL_RE.search(url):
                summary["websocket_null_urls"].append(url)

        for entry in _scan_entries(payload.get("console")):
            text = str(entry.get("text") or "")
            if _WS_NULL_RE.search(text):
                summary["websocket_null_fallback"] = True
            if "Unexpected response code: 404" in text and "WebSocket connection" in text:
                summary["websocket_404_errors"].append(text)

    if summary["shell_endpoint_failure"]:
        response = next(
            (
                item.get("response")
                for item in summary["shell_visit_failures"]
                if isinstance(item.get("response"), dict) and item["response"].get("code") == 170022
            ),
            None,
        )
        code = response.get("code") if isinstance(response, dict) else None
        msg = response.get("msg") if isinstance(response, dict) else None
        trace_id = response.get("traceId") if isinstance(response, dict) else None
        env_label = summary.get("env_name") or summary.get("env_id") or "environment"
        summary["blocker_summary"] = (
            f"Huanxin {env_label} shell endpoint provisioning failed: "
            f"getShellVisitUrl returned code={code} msg={msg!r} traceId={trace_id}; "
            "frontend then fell through to websocket null / 404."
        )
    elif summary["websocket_null_urls"] or summary["websocket_404_errors"]:
        summary["blocker_summary"] = (
            "Frontend fell through to websocket null / 404 after shell-open attempt."
        )

    summary["websocket_null_urls"] = sorted(set(summary["websocket_null_urls"]))
    summary["request_failed_urls"] = sorted(set(summary["request_failed_urls"]))
    summary["websocket_404_errors"] = list(dict.fromkeys(summary["websocket_404_errors"]))
    return summary


def main() -> int:
    args = parse_args()
    summary = summarize_probe_artifacts(args.artifacts)
    rendered = json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

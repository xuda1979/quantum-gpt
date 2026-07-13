#!/usr/bin/env python3
"""Serve the local agentic training dashboard and keep it fresh."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.render_agentic_training_dashboard import (  # noqa: E402
    build_research_system_status,
    build_source_contract,
    discover_runs,
    load_json,
    registry_decision_payload,
    registry_run_payload,
    render_dashboard,
    summarize_run,
)


class DashboardState:
    def __init__(
        self,
        *,
        outputs_dir: Path,
        limit: int,
        title: str,
        output_dir: Path,
        registry_output: Path,
        huanxin_status: Path,
        reports_dir: Path,
        data_dir: Path,
        evals_dir: Path,
        docs_dir: Path,
        remote_log_runs: list[str],
        remote_log_refresh_seconds: float,
        remote_log_timeout_sec: int,
    ) -> None:
        self.outputs_dir = outputs_dir
        self.limit = limit
        self.title = title
        self.output_dir = output_dir
        self.registry_output = registry_output
        self.huanxin_status = huanxin_status
        self.reports_dir = reports_dir
        self.data_dir = data_dir
        self.evals_dir = evals_dir
        self.docs_dir = docs_dir
        self.remote_log_runs = remote_log_runs
        self.remote_log_refresh_seconds = remote_log_refresh_seconds
        self.remote_log_timeout_sec = remote_log_timeout_sec
        self._lock = threading.Lock()
        self._html = ""
        self._registry: dict[str, Any] = {"runs": []}
        self._last_render: dict[str, Any] | None = None

    def render(self) -> dict[str, Any]:
        run_dirs = discover_runs(self.outputs_dir)[: max(self.limit, 1)]
        runs = [summarize_run(path) for path in run_dirs if path.exists()]
        huanxin_status = load_json(self.huanxin_status) or {}
        system_status = build_research_system_status(
            outputs_dir=self.outputs_dir,
            reports_dir=self.reports_dir,
            data_dir=self.data_dir,
            evals_dir=self.evals_dir,
            docs_dir=self.docs_dir,
        )
        source_contract = build_source_contract(runs, huanxin_status)
        html_text = render_dashboard(
            runs,
            title=self.title,
            huanxin_status=huanxin_status,
            system_status=system_status,
            source_contract=source_contract,
        )
        registry = {
            "runs": [registry_run_payload(run) for run in runs],
            "huanxin_environment_status": huanxin_status,
            "research_system_status": system_status,
            "source_contract": source_contract,
            "decision_summary": registry_decision_payload(runs, huanxin_status, source_contract),
        }
        payload = {
            "timestamp": time.time(),
            "runs": len(runs),
        }
        with self._lock:
            self._html = html_text
            self._registry = registry
            self._last_render = payload
            self.output_dir.parent.mkdir(parents=True, exist_ok=True)
            self.output_dir.write_text(html_text, encoding="utf-8")
            self.registry_output.parent.mkdir(parents=True, exist_ok=True)
            self.registry_output.write_text(
                json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
        return payload

    def snapshot(self) -> tuple[str, dict[str, Any], dict[str, Any] | None]:
        with self._lock:
            return self._html, self._registry, self._last_render


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--outputs-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"))
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--evals-dir", type=Path, default=Path("evals"))
    parser.add_argument("--docs-dir", type=Path, default=Path("docs"))
    parser.add_argument("--limit", type=int, default=16)
    parser.add_argument("--title", default="智能体训练状态")
    parser.add_argument(
        "--output", type=Path, default=Path("reports/agentic_training_dashboard.html")
    )
    parser.add_argument(
        "--registry-output", type=Path, default=Path("reports/agentic_training_run_registry.json")
    )
    parser.add_argument(
        "--huanxin-status", type=Path, default=Path("reports/huanxin_environment_status.json")
    )
    parser.add_argument("--poll-seconds", type=float, default=10.0)
    parser.add_argument("--refresh-huanxin-status", action="store_true")
    parser.add_argument("--huanxin-env", action="append", dest="huanxin_envs", default=[])
    parser.add_argument("--huanxin-refresh-seconds", type=float, default=120.0)
    parser.add_argument("--huanxin-timeout-sec", type=int, default=20)
    parser.add_argument(
        "--remote-log-run",
        action="append",
        default=[],
        help="Refresh one local run from a Huanxin training log as env:remote_output_dir:local_run_dir.",
    )
    parser.add_argument("--remote-log-refresh-seconds", type=float, default=30.0)
    parser.add_argument("--remote-log-timeout-sec", type=int, default=60)
    return parser.parse_args()


def make_handler(state: DashboardState) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return

        def _send(self, body: bytes, *, content_type: str = "text/html; charset=utf-8") -> None:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            if self.path in {"/", "/index.html"}:
                html_text, _, last_render = state.snapshot()
                if not html_text:
                    last_render = state.render()
                    html_text, _, _ = state.snapshot()
                body = html_text.encode("utf-8")
                self._send(body)
                return
            if self.path == "/status.json":
                _, registry, last_render = state.snapshot()
                payload = {
                    "ok": True,
                    "dashboard": str(state.output_dir),
                    "registry": str(state.registry_output),
                    "last_render": last_render,
                    "runs": registry.get("runs", []),
                    "huanxin_environment_status": registry.get("huanxin_environment_status", {}),
                    "research_system_status": registry.get("research_system_status", {}),
                    "source_contract": registry.get("source_contract", {}),
                    "decision_summary": registry.get("decision_summary", {}),
                }
                self._send(
                    json.dumps(payload, indent=2).encode("utf-8"),
                    content_type="application/json; charset=utf-8",
                )
                return
            self.send_error(404)

        def do_HEAD(self) -> None:  # noqa: N802
            if self.path in {"/", "/index.html"}:
                html_text, _, _ = state.snapshot()
                if not html_text:
                    state.render()
                    html_text, _, _ = state.snapshot()
                body = html_text.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return
            if self.path == "/status.json":
                _, registry, _ = state.snapshot()
                body = json.dumps(registry).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return
            self.send_error(404)

    return Handler


def main() -> int:
    args = parse_args()
    state = DashboardState(
        outputs_dir=args.outputs_dir,
        limit=args.limit,
        title=args.title,
        output_dir=args.output,
        registry_output=args.registry_output,
        huanxin_status=args.huanxin_status,
        reports_dir=args.reports_dir,
        data_dir=args.data_dir,
        evals_dir=args.evals_dir,
        docs_dir=args.docs_dir,
        remote_log_runs=args.remote_log_run,
        remote_log_refresh_seconds=args.remote_log_refresh_seconds,
        remote_log_timeout_sec=args.remote_log_timeout_sec,
    )
    state.render()

    server = ThreadingHTTPServer((args.host, args.port), make_handler(state))

    def refresher() -> None:
        while True:
            try:
                state.render()
            except Exception:
                pass
            time.sleep(max(args.poll_seconds, 1.0))

    thread = threading.Thread(target=refresher, daemon=True)
    thread.start()
    if args.refresh_huanxin_status:
        huanxin_envs = args.huanxin_envs or ["ASI1", "AI"]

        def huanxin_refresher() -> None:
            while True:
                cmd = [
                    sys.executable,
                    str(ROOT / "scripts" / "collect_huanxin_environment_status.py"),
                    "--timeout-sec",
                    str(max(args.huanxin_timeout_sec, 1)),
                    "--output",
                    str(args.huanxin_status),
                ]
                for env_name in huanxin_envs:
                    cmd.extend(["--env", env_name])
                subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
                time.sleep(max(args.huanxin_refresh_seconds, 10.0))

        huanxin_thread = threading.Thread(target=huanxin_refresher, daemon=True)
        huanxin_thread.start()
    if args.remote_log_run:

        def remote_log_refresher() -> None:
            while True:
                for spec in args.remote_log_run:
                    parts = spec.split(":", 2)
                    if len(parts) != 3:
                        continue
                    env_name, remote_output_dir, local_run_dir = parts
                    subprocess.run(
                        [
                            sys.executable,
                            str(ROOT / "scripts" / "refresh_huanxin_grpo_run_from_log.py"),
                            "--env",
                            env_name,
                            "--remote-output-dir",
                            remote_output_dir,
                            "--local-run-dir",
                            local_run_dir,
                            "--timeout-sec",
                            str(max(args.remote_log_timeout_sec, 1)),
                        ],
                        cwd=ROOT,
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                time.sleep(max(args.remote_log_refresh_seconds, 5.0))

        remote_log_thread = threading.Thread(target=remote_log_refresher, daemon=True)
        remote_log_thread.start()
    print(
        json.dumps(
            {
                "ok": True,
                "url": f"http://{args.host}:{args.port}",
                "output": str(args.output),
                "registry": str(args.registry_output),
            }
        )
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

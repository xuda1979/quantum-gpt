#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect and recover stale Huanxin daemon pid/port/ipc state."
    )
    parser.add_argument("command", choices=("inspect", "cleanup-stale"))
    parser.add_argument("env")
    parser.add_argument("--tmp-root", type=Path, default=Path("/tmp"))
    parser.add_argument("--health-timeout-seconds", type=float, default=1.5)
    return parser.parse_args(argv)


def state_paths(env: str, tmp_root: Path) -> dict[str, Path]:
    return {
        "pid_file": tmp_root / f"huanxin-daemon-{env}.pid",
        "port_file": tmp_root / f"huanxin-daemon-{env}.port",
        "ipc_dir": tmp_root / f"huanxin-daemon-{env}.ipc",
        "log_file": tmp_root / f"huanxin-daemon-{env}.log",
    }


def read_text(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def read_pid(path: Path) -> int | None:
    raw = read_text(path)
    if raw is None:
        return None
    try:
        return int(raw.strip())
    except Exception:
        return None


def read_port(path: Path) -> int | None:
    raw = read_text(path)
    if raw is None:
        return None
    try:
        return int(raw.strip())
    except Exception:
        return None


def process_alive(pid: int | None) -> bool:
    if pid is None:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def health_payload(port: int | None, timeout_seconds: float) -> dict[str, object] | None:
    if port is None:
        return None
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/health", timeout=timeout_seconds
        ) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return None


def collect_ipc(ipc_dir: Path) -> dict[str, list[Path]]:
    request_files: list[Path] = []
    processing_files: list[Path] = []
    response_files: list[Path] = []
    other_files: list[Path] = []
    if not ipc_dir.exists():
        return {
            "request_files": request_files,
            "processing_files": processing_files,
            "response_files": response_files,
            "other_files": other_files,
        }
    for child in sorted(ipc_dir.iterdir()):
        if not child.is_file():
            continue
        name = child.name
        if name.endswith(".request.json"):
            request_files.append(child)
        elif name.endswith(".processing.json"):
            processing_files.append(child)
        elif name.endswith(".response.json"):
            response_files.append(child)
        else:
            other_files.append(child)
    return {
        "request_files": request_files,
        "processing_files": processing_files,
        "response_files": response_files,
        "other_files": other_files,
    }


def inspect_state(env: str, tmp_root: Path, timeout_seconds: float) -> dict[str, object]:
    paths = state_paths(env, tmp_root)
    pid = read_pid(paths["pid_file"])
    port = read_port(paths["port_file"])
    alive = process_alive(pid)
    health = health_payload(port, timeout_seconds)
    ipc = collect_ipc(paths["ipc_dir"])
    stale_state_detected = (
        (
            paths["pid_file"].exists()
            or paths["port_file"].exists()
            or ipc["processing_files"]
            or ipc["request_files"]
        )
        and not alive
        and health is None
    )
    return {
        "env": env,
        "tmp_root": str(tmp_root),
        "pid": pid,
        "port": port,
        "daemon_process_alive": alive,
        "daemon_health_ok": health is not None,
        "daemon_health_payload": health,
        "pid_file_exists": paths["pid_file"].exists(),
        "port_file_exists": paths["port_file"].exists(),
        "ipc_dir_exists": paths["ipc_dir"].exists(),
        "request_files": [str(path) for path in ipc["request_files"]],
        "processing_files": [str(path) for path in ipc["processing_files"]],
        "response_files": [str(path) for path in ipc["response_files"]],
        "other_ipc_files": [str(path) for path in ipc["other_files"]],
        "stale_state_detected": stale_state_detected,
    }


def write_recovery_response(
    source_path: Path, env: str, request_payload: dict[str, object] | None
) -> Path:
    response_path = Path(
        str(source_path)
        .replace(".processing.json", ".response.json")
        .replace(".request.json", ".response.json")
    )
    payload = {
        "ok": False,
        "envName": env,
        "error": "stale_daemon_state_recovered",
        "message": (
            "Recovered stale Huanxin daemon state after the daemon died before completing this request. "
            "Please retry the command."
        ),
        "recoveredFrom": source_path.name,
        "command": (request_payload or {}).get("command"),
        "waitMs": (request_payload or {}).get("waitMs"),
    }
    response_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return response_path


def cleanup_stale(env: str, tmp_root: Path, timeout_seconds: float) -> dict[str, object]:
    snapshot = inspect_state(env, tmp_root, timeout_seconds)
    paths = state_paths(env, tmp_root)
    if not snapshot["stale_state_detected"]:
        return {
            **snapshot,
            "action": "noop",
            "backup_dir": None,
            "moved_files": [],
            "written_responses": [],
        }

    backup_dir = paths["ipc_dir"] / f".recovered-{int(time.time())}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    moved_files: list[str] = []
    written_responses: list[str] = []

    for label in ("pid_file", "port_file"):
        source_path = paths[label]
        if source_path.exists():
            target_path = backup_dir / source_path.name
            try:
                shutil.move(str(source_path), str(target_path))
                moved_files.append(str(target_path))
            except FileNotFoundError:
                # The state file can disappear between the stale snapshot and cleanup
                # if another recovery path already handled it. Treat that as benign.
                continue

    ipc = collect_ipc(paths["ipc_dir"])
    for source_path in ipc["processing_files"] + ipc["request_files"]:
        request_payload = None
        try:
            request_payload = json.loads(source_path.read_text(encoding="utf-8"))
        except Exception:
            request_payload = None
        response_path = write_recovery_response(source_path, env, request_payload)
        written_responses.append(str(response_path))
        target_path = backup_dir / source_path.name
        try:
            shutil.move(str(source_path), str(target_path))
            moved_files.append(str(target_path))
        except FileNotFoundError:
            continue

    return {
        **inspect_state(env, tmp_root, timeout_seconds),
        "action": "cleanup-stale",
        "backup_dir": str(backup_dir),
        "moved_files": moved_files,
        "written_responses": written_responses,
    }


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.command == "inspect":
        payload = inspect_state(args.env, args.tmp_root, args.health_timeout_seconds)
    else:
        payload = cleanup_stale(args.env, args.tmp_root, args.health_timeout_seconds)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(os.sys.argv[1:]))

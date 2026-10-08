#!/usr/bin/env python3
"""Resolve Huanxin environment URLs and daemon ports.

The defaults here are workspace-local conveniences. Other projects can provide
`.huanxin_envs.json` or set `HUANXIN_ENV_CONFIG_JSON` to avoid editing wrappers.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = (
    "https://aihuanxin.cn/kunlun/kl-web?"
    "poolId=6&projectId=21b4208dde424e96b159362ef49c9c96#/train-dev"
)
DEFAULT_ENV_IDS = {
    "AI": "dl-9a5a098accce31c28cf4c6ca23391341",
    "ASI1": "dl-9a5a098accce31c28cf4c6ca23391341",
    "ai3": "dl-c72bd81a96e33134bbe0ae4a478fbab0",
    "ASI3": "dl-c72bd81a96e33134bbe0ae4a478fbab0",
}
DEFAULT_FALLBACK_ENV_ID = DEFAULT_ENV_IDS["AI"]
DEFAULT_PORTS = {
    "AI": 19006,
    "ai1": 19001,
    "ai2": 19002,
    "ai3": 19003,
    "ASI1": 20646,
    "ASI2": 19004,
    "ASI3": 20653,
}


def default_port(env_name: str) -> int:
    return DEFAULT_PORTS.get(env_name) or deterministic_port(env_name)


def deterministic_port(env_name: str) -> int:
    return 20000 + (sum((index + 1) * ord(ch) for index, ch in enumerate(env_name)) % 1000)


def load_override_config(path: Path | None) -> dict[str, Any]:
    candidate = path
    if candidate is None:
        env_path = os.environ.get("HUANXIN_ENV_CONFIG_JSON")
        candidate = Path(env_path) if env_path else ROOT / ".huanxin_envs.json"
    if not candidate.exists():
        return {}
    payload = json.loads(candidate.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"Huanxin env config must be a JSON object: {candidate}")
    return payload


def resolve_env(env_name: str, *, config_path: Path | None = None) -> dict[str, Any]:
    config = load_override_config(config_path)
    envs = config.get("envs") or config.get("environments") or {}
    if not isinstance(envs, dict):
        raise SystemExit("Huanxin env config `envs` must be an object")

    override = envs.get(env_name) or {}
    if not isinstance(override, dict):
        raise SystemExit(f"Huanxin env config for {env_name!r} must be an object")

    base_url = str(
        override.get("train_dev_base_url")
        or config.get("train_dev_base_url")
        or os.environ.get("HUANXIN_TRAIN_DEV_BASE_URL")
        or DEFAULT_BASE_URL
    )
    env_id = (
        override.get("env_id")
        or config.get("default_env_id")
        or DEFAULT_ENV_IDS.get(env_name)
        or DEFAULT_FALLBACK_ENV_ID
    )
    train_dev_url = override.get("train_dev_url") or os.environ.get("HUANXIN_TRAIN_DEV_URL")
    if not train_dev_url:
        if env_id:
            train_dev_url = f"{base_url}/environment/{env_id}?name={env_name}"
        else:
            train_dev_url = base_url

    daemon_port = int(override.get("daemon_port") or default_port(env_name))

    return {
        "env_name": env_name,
        "env_id": env_id,
        "daemon_port": daemon_port,
        "train_dev_base_url": base_url,
        "train_dev_url": str(train_dev_url),
        "config_source": str(
            config_path or os.environ.get("HUANXIN_ENV_CONFIG_JSON") or ROOT / ".huanxin_envs.json"
        ),
        "config_loaded": bool(config),
    }


def shell_assignments(payload: dict[str, Any]) -> str:
    mapping = {
        "HUANXIN_ENV_NAME": payload["env_name"],
        "HUANXIN_ENV_ID": payload.get("env_id") or "",
        "HUANXIN_ENV_DAEMON_PORT": str(payload["daemon_port"]),
        "HUANXIN_ENV_TRAIN_DEV_BASE_URL": payload["train_dev_base_url"],
        "HUANXIN_ENV_TRAIN_DEV_URL": payload["train_dev_url"],
    }
    return "\n".join(f"{key}={shlex.quote(value)}" for key, value in mapping.items())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", required=True, help="Huanxin environment name.")
    parser.add_argument("--config", type=Path, default=None, help="Optional JSON config path.")
    parser.add_argument("--format", choices=("json", "shell"), default="json")
    parser.add_argument(
        "--field",
        choices=("env_id", "daemon_port", "train_dev_base_url", "train_dev_url"),
        default=None,
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = resolve_env(args.env, config_path=args.config)
    if args.field:
        print(payload.get(args.field) or "")
    elif args.format == "shell":
        print(shell_assignments(payload))
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

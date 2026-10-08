from __future__ import annotations

import json
from pathlib import Path

import scripts.huanxin_env_config as config


def test_resolve_default_asi1_config() -> None:
    payload = config.resolve_env("ASI1", config_path=Path("/tmp/does-not-exist-huanxin-envs.json"))

    assert payload["env_name"] == "ASI1"
    assert payload["env_id"] == "dl-9a5a098accce31c28cf4c6ca23391341"
    assert payload["daemon_port"] == 20646
    assert payload["train_dev_url"].endswith(
        "/environment/dl-9a5a098accce31c28cf4c6ca23391341?name=ASI1"
    )


def test_resolve_env_from_json_override(tmp_path: Path) -> None:
    config_path = tmp_path / "huanxin-envs.json"
    config_path.write_text(
        json.dumps(
            {
                "train_dev_base_url": "https://example.invalid/app#/train-dev",
                "envs": {
                    "EXP1": {
                        "env_id": "dl-exp",
                        "daemon_port": 27777,
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    payload = config.resolve_env("EXP1", config_path=config_path)

    assert payload["env_id"] == "dl-exp"
    assert payload["daemon_port"] == 27777
    assert (
        payload["train_dev_url"]
        == "https://example.invalid/app#/train-dev/environment/dl-exp?name=EXP1"
    )


def test_shell_assignments_are_quoted() -> None:
    text = config.shell_assignments(
        {
            "env_name": "EXP 1",
            "env_id": "dl-exp",
            "daemon_port": 27777,
            "train_dev_base_url": "https://example.invalid/app#/train-dev",
            "train_dev_url": "https://example.invalid/app#/train-dev/environment/dl-exp?name=EXP 1",
        }
    )

    assert "HUANXIN_ENV_NAME='EXP 1'" in text
    assert "HUANXIN_ENV_DAEMON_PORT=27777" in text

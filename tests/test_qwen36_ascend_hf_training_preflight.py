from __future__ import annotations

import json
import subprocess
from pathlib import Path

from scripts.preflight_qwen36_ascend_hf_training import (
    build_preflight_result,
    is_known_blocked_qwen36_w8a8_model,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "preflight_qwen36_ascend_hf_training.py"


def test_preflight_blocks_qwen36_35b_a3b_w8a8_on_npu() -> None:
    result = build_preflight_result("/root/work/filestorage/Qwen3.6-35B-A3B-W8A8", "npu")

    assert result["status"] == "blocked"
    assert result["blocked_by_name"] is True
    assert "aclnnMm" in str(result["message"])
    assert "Qwen3.6-35B-A3B-W8A8" in str(result["message"])


def test_preflight_allows_qwen36_27b_on_npu() -> None:
    result = build_preflight_result("/root/work/filestorage/Qwen3.6-27B", "npu")

    assert result["status"] == "ok"
    assert result["blocked_by_name"] is False


def test_preflight_cli_emits_json_and_nonzero_for_blocked_model() -> None:
    result = subprocess.run(
        [
            "python3",
            str(SCRIPT),
            "--model-name",
            "/root/work/filestorage/Qwen3.6-35B-A3B-W8A8",
            "--device",
            "npu",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["bypass"] == "ALLOW_KNOWN_QWEN36_W8A8_ASCEND_HF_BLOCKER=1"


def test_preflight_marker_accepts_qwen36_alias() -> None:
    assert is_known_blocked_qwen36_w8a8_model("models/qwen36-35b-a3b-w8a8")


def test_isq_split_default_path_is_v3() -> None:
    from scripts.prepare_isq_cot_sft_split import DEFAULT_OUTPUT_DIR

    assert str(DEFAULT_OUTPUT_DIR) == "data/generated/isq-cot-sft-80-20-v3"

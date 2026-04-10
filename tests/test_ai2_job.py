from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ai2_job.sh"
FIXTURE_JOB_ID = "omnicoder-8npu-fast-sft-20260409T065250Z"
FIXTURE_META = ROOT / ".huanxin_jobs" / f"{FIXTURE_JOB_ID}.json"


def _write_wrapper(path: Path) -> None:
    path.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "printf '%s\\n' \"$AI2_JOB_TEST_WRAPPER_JSON\"\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def _seed_meta(meta_dir: Path) -> None:
    meta_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(FIXTURE_META, meta_dir / FIXTURE_META.name)


def _run_status(tmp_path: Path, wrapper_json: dict[str, object]) -> dict[str, object]:
    wrapper = tmp_path / "fake_ai2_shell.sh"
    _write_wrapper(wrapper)
    meta_dir = tmp_path / "meta"
    _seed_meta(meta_dir)
    env = os.environ.copy()
    env["AI2_JOB_SHELL_WRAPPER"] = str(wrapper)
    env["AI2_JOB_META_DIR"] = str(meta_dir)
    env["AI2_JOB_TEST_WRAPPER_JSON"] = json.dumps(wrapper_json)
    result = subprocess.run(
        ["bash", str(SCRIPT), "status", FIXTURE_JOB_ID, "80"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_status_parses_marker_wrapped_transcript(tmp_path: Path) -> None:
    payload = {
        "transport": "daemon",
        "durationMs": 23,
        "output": "",
        "after": "\n".join(
            [
                "__OPENCLAW_JOB_STATUS_BEGIN__",
                "__OPENCLAW_JOB_STATUS__ running",
                "287095 Sl 42 python3 training/qwen_sft_peft.py --max-steps 12",
                "__OPENCLAW_JOB_STATUS_END__",
                "__OPENCLAW_JOB_LOG_BEGIN__",
                '{"stage":"first_loss_ready","loss":0.3238}',
                "__OPENCLAW_JOB_LOG_END__",
            ]
        ),
        "before": "",
    }
    parsed = _run_status(tmp_path=tmp_path, wrapper_json=payload)
    assert parsed["job_id"] == FIXTURE_JOB_ID
    assert parsed["status"] == "running"
    assert parsed["status_source"] == "status_markers"
    assert parsed["ps"] == ["287095 Sl 42 python3 training/qwen_sft_peft.py --max-steps 12"]
    assert "first_loss_ready" in parsed["log_tail"]


def test_status_falls_back_to_completed_transcript_without_status_markers(tmp_path: Path) -> None:
    payload = {
        "transport": "daemon",
        "durationMs": 31,
        "output": "",
        "after": "\n".join(
            [
                '{"stage":"first_loss_ready","loss":0.3238}',
                '{"stage":"first_backward_done","batch_index":1}',
                '{"stage":"final_eval_done","dt_final_eval_sec":12.7}',
                "{",
                '  "completed_steps": 12,',
                '  "final_eval": {"loss": 0.3863, "perplexity": 1.4715}',
                "}",
            ]
        ),
        "before": "",
    }
    parsed = _run_status(tmp_path=tmp_path, wrapper_json=payload)
    assert parsed["job_id"] == FIXTURE_JOB_ID
    assert parsed["status"] == "exited"
    assert parsed["status_source"] == "completion_marker_fallback"
    assert parsed["ps"] == []
    assert '"completed_steps": 12' in parsed["log_tail"]
    assert '"stage":"final_eval_done"' in parsed["log_tail"]


def test_status_falls_back_to_scorecard_summary_without_status_markers(tmp_path: Path) -> None:
    payload = {
        "transport": "daemon",
        "durationMs": 44,
        "output": "",
        "after": "\n".join(
            [
                "[PASS] software_workspace_runner_smoke - Workspace runner smoke (reference)",
                "Overall: 24/26 passed",
                "  quantum: 11/13 passed",
                "  software: 13/13 passed",
                "Scorecard written to: /root/root/work/quantum-gpt/evals/runs/omnicoder-fastiter/scorecard.json",
                "__OPENCLAW_JOB_LOG_END__",
                "__AI2_RUN_123__",
            ]
        ),
        "before": "",
    }
    parsed = _run_status(tmp_path=tmp_path, wrapper_json=payload)
    assert parsed["job_id"] == FIXTURE_JOB_ID
    assert parsed["status"] == "exited"
    assert parsed["status_source"] == "scorecard_summary_fallback"
    assert parsed["ps"] == []
    assert "Overall: 24/26 passed" in parsed["log_tail"]
    assert "Scorecard written to:" in parsed["log_tail"]

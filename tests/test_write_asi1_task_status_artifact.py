from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "write_asi1_task_status_artifact.py"


def test_write_asi1_failed_task_artifacts(tmp_path: Path) -> None:
    probe = tmp_path / "probe.json"
    probe.write_text(
        json.dumps(
            {
                "matchedTask": {
                    "id": "dt-test",
                    "name": "asi1-grpo-smoke",
                    "status": 6,
                    "submitTime": "2026-05-28 00:00:00",
                    "useTime": "00:00:00",
                },
                "bodyPreview": "/bin/bash: -c: line 2: syntax error near unexpected token `;&'",
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "run"

    result = subprocess.run(
        [
            str(SCRIPT),
            "--output-dir",
            str(output_dir),
            "--probe-json",
            str(probe),
            "--planned-steps",
            "1",
            "--remote-output-dir",
            "outputs/qwen36-smoke",
            "--log-path",
            "/tmp/qwen36-smoke.log",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    live = json.loads((output_dir / "live_status.json").read_text(encoding="utf-8"))
    failure = json.loads((output_dir / "failure_report.json").read_text(encoding="utf-8"))
    manifest = json.loads((output_dir / "run_manifest.json").read_text(encoding="utf-8"))

    assert live["status"] == "failed"
    assert live["planned_steps"] == 1
    assert live["online_eval_latest"] is None
    assert live["latest_checkpoint"] is None
    assert live["job_health"]["huanxin_task_id"] == "dt-test"
    assert live["alerts"][0]["kind"] == "asi1_task_failed_before_metrics"
    assert failure["failure_stage"] == "pre_python_task_startup"
    assert "syntax error" in failure["pod_log_excerpt"]
    assert (
        manifest["online_eval_benchmark_file"]
        == "evals/benchmarks/quantum_generalization_holdout_v1.txt"
    )


def test_write_asi1_submitted_task_does_not_fake_eval(tmp_path: Path) -> None:
    output_dir = tmp_path / "run"
    result = subprocess.run(
        [
            str(SCRIPT),
            "--output-dir",
            str(output_dir),
            "--task-name",
            "asi1-grpo-submitted",
            "--task-id",
            "dt-submitted",
            "--status",
            "starting",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    live = json.loads((output_dir / "live_status.json").read_text(encoding="utf-8"))

    assert live["status"] == "submitted"
    assert live["online_eval_latest"] is None
    assert not (output_dir / "failure_report.json").exists()
    assert live["alerts"][0]["kind"] == "asi1_task_submitted"


def test_write_asi1_submission_probe_derives_task_and_launch_artifacts(tmp_path: Path) -> None:
    probe = tmp_path / "submit.json"
    probe.write_text(
        json.dumps(
            {
                "taskName": "q36-27b-hi-0601",
                "launchSpec": {
                    "remote_root": "/workspace/quantum-gpt",
                    "remote_command": "\n".join(
                        [
                            "export ASI1_AGENTIC_TASK_MODEL_NAME=/root/work/filestorage/Qwen3.6-27B",
                            "export ASI1_AGENTIC_TASK_BENCHMARK_FILE=evals/benchmarks/quantum_grpo_training_v5_failure_shape_disjoint.txt",
                            "export ASI1_AGENTIC_TASK_OUTPUT_DIR=outputs/qwen36-27b-agentic-grpo-asi1-task-fast-20260601T073015Z",
                            "export ASI1_AGENTIC_TASK_LOG_PATH=/tmp/qwen36_27b_agentic_grpo_asi1_task_fast_20260601T073015Z.log",
                            "export ASI1_AGENTIC_TASK_GRPO_STEPS=512",
                            "export ASI1_AGENTIC_TASK_ONLINE_EVAL_BENCHMARK_FILE=evals/benchmarks/quantum_generalization_holdout_v2_hard.txt",
                        ]
                    ),
                },
                "networkEvents": [
                    {
                        "method": "POST",
                        "url": "https://aihuanxin.cn/kunlun/web/task/v1/list",
                        "status": 200,
                        "responsePreview": json.dumps(
                            {
                                "code": 0,
                                "data": {
                                    "list": [
                                        {
                                            "id": "dt-993d78ae676645198a37ff2cce6f142d",
                                            "name": "q36-27b-hi-0601",
                                            "status": 1,
                                            "submitTime": "2026-06-01 15:34:20",
                                            "useTime": "--",
                                            "resourceInfo": {"cpu": 128, "gpu": 8, "mem": 1920},
                                        }
                                    ]
                                },
                            }
                        ),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "q36-27b-hi-0601"

    result = subprocess.run(
        [
            str(SCRIPT),
            "--output-dir",
            str(output_dir),
            "--probe-json",
            str(probe),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    live = json.loads((output_dir / "live_status.json").read_text(encoding="utf-8"))
    job = json.loads((output_dir / "job_health.json").read_text(encoding="utf-8"))
    manifest = json.loads((output_dir / "run_manifest.json").read_text(encoding="utf-8"))
    fetch = json.loads((output_dir / "asi1_fetch_manifest.json").read_text(encoding="utf-8"))

    assert live["status"] == "submitted"
    assert live["planned_steps"] == 512
    assert live["latest_checkpoint"] is None
    assert live["online_eval_latest"] is None
    assert job["huanxin_task_id"] == "dt-993d78ae676645198a37ff2cce6f142d"
    assert job["huanxin_task_name"] == "q36-27b-hi-0601"
    assert job["huanxin_task_status"] == "queued"
    assert manifest["model_name"] == "/root/work/filestorage/Qwen3.6-27B"
    assert (
        manifest["benchmark_file"]
        == "evals/benchmarks/quantum_grpo_training_v5_failure_shape_disjoint.txt"
    )
    assert (
        manifest["online_eval_benchmark_file"]
        == "evals/benchmarks/quantum_generalization_holdout_v2_hard.txt"
    )
    assert (
        manifest["remote_output_dir"]
        == "outputs/qwen36-27b-agentic-grpo-asi1-task-fast-20260601T073015Z"
    )
    assert (
        fetch["remote_dir"]
        == "/workspace/quantum-gpt/outputs/qwen36-27b-agentic-grpo-asi1-task-fast-20260601T073015Z"
    )
    assert fetch["log_path"] == "/tmp/qwen36_27b_agentic_grpo_asi1_task_fast_20260601T073015Z.log"


def test_write_asi1_status_probe_reads_list_events_task_record(tmp_path: Path) -> None:
    probe = tmp_path / "status.json"
    probe.write_text(
        json.dumps(
            {
                "taskName": "q36-27b-lora-s3r-06031356",
                "taskId": "dt-78d0b3bcda4f4f0f9143082191416dee",
                "matchedTask": None,
                "launchSpec": {
                    "remote_root": "/root/work/quantum-gpt",
                    "output_dir": "outputs/q36-27b-lora-s3r-asi1-20260603T135646Z",
                    "log_path": "/tmp/q36_27b_lora_s3r_asi1_20260603T135646Z.log",
                    "remote_command": "export ASI1_AGENTIC_TASK_GRPO_STEPS=200000",
                },
                "listEvents": [
                    {
                        "method": "POST",
                        "url": "https://aihuanxin.cn/kunlun/web/task/v1/list",
                        "status": 200,
                        "responsePreview": json.dumps(
                            {
                                "code": 0,
                                "data": {
                                    "list": [
                                        {
                                            "id": "dt-78d0b3bcda4f4f0f9143082191416dee",
                                            "name": "q36-27b-lora-s3r-06031356",
                                            "status": 6,
                                            "submitTime": "2026-06-03 21:57:35",
                                            "startTime": "2026-06-03 21:57:43",
                                            "endTime": "2026-06-03 21:58:00",
                                            "useTime": "00:00:17",
                                            "resourceInfo": {"cpu": 160, "gpu": 8, "mem": 1920},
                                        }
                                    ]
                                },
                            }
                        ),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "q36-27b-lora-s3r"

    result = subprocess.run(
        [
            str(SCRIPT),
            "--output-dir",
            str(output_dir),
            "--probe-json",
            str(probe),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    live = json.loads((output_dir / "live_status.json").read_text(encoding="utf-8"))
    job = json.loads((output_dir / "job_health.json").read_text(encoding="utf-8"))
    failure = json.loads((output_dir / "failure_report.json").read_text(encoding="utf-8"))

    assert live["status"] == "failed"
    assert live["planned_steps"] == 200000
    assert live["job_health"]["npu_world_size"] == 8
    assert job["huanxin_task_status"] == "failed"
    assert job["huanxin_task_status_code"] == 6
    assert job["huanxin_use_time"] == "00:00:17"
    assert failure["failure_stage"] == "unknown_before_metrics"


def test_write_asi1_status_probe_can_match_list_event_by_task_id_override(tmp_path: Path) -> None:
    probe = tmp_path / "status.json"
    probe.write_text(
        json.dumps(
            {
                "taskName": "wrong-current-task",
                "taskId": "dt-78d0b3bcda4f4f0f9143082191416dee",
                "matchedTask": None,
                "listEvents": [
                    {
                        "method": "POST",
                        "url": "https://aihuanxin.cn/kunlun/web/task/v1/list",
                        "status": 200,
                        "responsePreview": json.dumps(
                            {
                                "code": 0,
                                "data": {
                                    "list": [
                                        {
                                            "id": "dt-78d0b3bcda4f4f0f9143082191416dee",
                                            "name": "q36-27b-lora-s3r-06031356",
                                            "status": 6,
                                            "submitTime": "2026-06-03 21:57:35",
                                            "useTime": "00:00:17",
                                            "resourceInfo": {"gpu": 8},
                                        }
                                    ]
                                },
                            }
                        ),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "q36-27b-lora-s3r"

    result = subprocess.run(
        [
            str(SCRIPT),
            "--output-dir",
            str(output_dir),
            "--probe-json",
            str(probe),
            "--task-name",
            "q36-27b-lora-s3r-06031356",
            "--task-id",
            "dt-78d0b3bcda4f4f0f9143082191416dee",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    job = json.loads((output_dir / "job_health.json").read_text(encoding="utf-8"))

    assert job["huanxin_task_name"] == "q36-27b-lora-s3r-06031356"
    assert job["huanxin_task_status"] == "failed"
    assert job["huanxin_task_status_code"] == 6
    assert job["npu_world_size"] == 8


def test_write_asi1_submit_failure_probe_records_create_blocker(tmp_path: Path) -> None:
    probe = tmp_path / "submit_failed.json"
    probe.write_text(
        json.dumps(
            {
                "taskName": "q36-lora-bundle-0603j",
                "launchSpec": {
                    "remote_root": "/root/work/quantum-gpt",
                    "output_dir": "outputs/q36-lora-bundle-asi1-20260603T1410Z",
                    "log_path": "/tmp/q36_lora_bundle_asi1_20260603T1410Z.log",
                    "remote_command": "export ASI1_AGENTIC_TASK_GRPO_STEPS=200000",
                },
                "networkEvents": [
                    {
                        "method": "POST",
                        "url": "https://aihuanxin.cn/kunlun/web/task/v1/create",
                        "status": 403,
                        "responsePreview": "RBAC: access denied",
                    }
                ],
                "submitResult": {
                    "submitted": False,
                    "blockedReason": "submit_transition_not_observed",
                    "createPayloadOverride": {
                        "source": "auto_large_execution_command",
                        "lines": 958,
                        "encodedBytes": 2564260,
                    },
                    "directSubmitFallback": {
                        "attempted": True,
                        "response": {"ok": False, "status": 403, "text": "RBAC: access denied"},
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "q36-lora-bundle-0603j"

    result = subprocess.run(
        [
            str(SCRIPT),
            "--output-dir",
            str(output_dir),
            "--probe-json",
            str(probe),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    live = json.loads((output_dir / "live_status.json").read_text(encoding="utf-8"))
    failure = json.loads((output_dir / "failure_report.json").read_text(encoding="utf-8"))
    job = json.loads((output_dir / "job_health.json").read_text(encoding="utf-8"))

    assert live["status"] == "failed"
    assert live["planned_steps"] == 200000
    assert live["online_eval_latest"] is None
    assert live["latest_checkpoint"] is None
    assert job["huanxin_task_status"] == "submit_failed"
    assert failure["failure_stage"] == "huanxin_task_create_failed"
    assert failure["create_payload_encoded_bytes"] == 2564260
    assert failure["direct_submit_status"] == 403
    assert "codeContents payload" in failure["startup_diagnosis"]


def test_write_asi1_submission_probe_falls_back_to_task_list_body_preview(tmp_path: Path) -> None:
    probe = tmp_path / "submit.json"
    probe.write_text(
        json.dumps(
            {
                "taskName": "q36-27b-hi-0601",
                "bodyPreview": (
                    "训练任务名称 所属资源组 创建人 任务状态 优先级 实例数 单实例资源配置 最近提交时间 服务时长 "
                    "q36-27b-hi-0601 公共huanxin-all-resource xuda2025 启动中 高 1 8加速卡 "
                    "128核CPU 1920GB内存 2026-06-01 15:34:20 --"
                ),
                "launchSpec": {
                    "remote_root": "/workspace/quantum-gpt",
                    "output_dir": "outputs/qwen36-27b-agentic-grpo-asi1-task-fast-20260601T073015Z",
                    "log_path": "/tmp/qwen36_27b_agentic_grpo_asi1_task_fast_20260601T073015Z.log",
                    "remote_command": "export ASI1_AGENTIC_TASK_GRPO_STEPS=512",
                },
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "q36-27b-hi-0601"

    result = subprocess.run(
        [
            str(SCRIPT),
            "--output-dir",
            str(output_dir),
            "--probe-json",
            str(probe),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    live = json.loads((output_dir / "live_status.json").read_text(encoding="utf-8"))
    job = json.loads((output_dir / "job_health.json").read_text(encoding="utf-8"))

    assert live["status"] == "submitted"
    assert live["planned_steps"] == 512
    assert job["huanxin_task_name"] == "q36-27b-hi-0601"
    assert job["huanxin_task_status"] == "starting"
    assert job["huanxin_task_status_code"] == 2
    assert job["huanxin_submit_time"] == "2026-06-01 15:34:20"


def test_write_asi1_status_code_zero_is_terminal_without_metrics(tmp_path: Path) -> None:
    probe = tmp_path / "probe.json"
    probe.write_text(
        json.dumps(
            {
                "matchedTask": {
                    "id": "dt-ended",
                    "name": "asi1-grpo-ended",
                    "status": 0,
                    "endTime": "2026-05-28 12:00:11",
                    "useTime": "00:00:11",
                },
                "bodyPreview": "Task ended before artifacts were fetched.",
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "run"

    result = subprocess.run(
        [
            str(SCRIPT),
            "--output-dir",
            str(output_dir),
            "--probe-json",
            str(probe),
            "--planned-steps",
            "1",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    live = json.loads((output_dir / "live_status.json").read_text(encoding="utf-8"))
    failure = json.loads((output_dir / "failure_report.json").read_text(encoding="utf-8"))

    assert live["status"] == "failed"
    assert live["summary"]["recorded_steps"] == 0
    assert live["online_eval_latest"] is None
    assert live["job_health"]["huanxin_task_status"] == "ended"
    assert live["job_health"]["huanxin_task_status_code"] == 0
    assert live["alerts"][0]["kind"] == "asi1_task_failed_before_metrics"
    assert failure["failure_stage"] == "unknown_before_metrics"


def test_write_asi1_done_marker_creates_compact_metrics(tmp_path: Path) -> None:
    probe = tmp_path / "probe.json"
    probe.write_text(
        json.dumps(
            {
                "matchedTask": {
                    "id": "dt-done",
                    "name": "asi1-rl-done",
                    "status": 0,
                    "endTime": "2026-05-29 16:25:52",
                    "useTime": "00:00:14",
                },
                "detailSummary": {
                    "podLogSummary": {
                        "bodyPreview": "\n".join(
                            [
                                "__ASI1_INLINE_RL_START__",
                                "device=npu:0",
                                'model_load={"attempted": false, "error": null, "model_class": null, "ok": false}',
                                "__ASI1_INLINE_RL_DONE__",
                                "output_dir=/tmp/qg-asi1-inline-rl-skipload-082316",
                                "final_pass_rate=0.666667",
                            ]
                        )
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "run"

    result = subprocess.run(
        [
            str(SCRIPT),
            "--output-dir",
            str(output_dir),
            "--probe-json",
            str(probe),
            "--planned-steps",
            "8",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    live = json.loads((output_dir / "live_status.json").read_text(encoding="utf-8"))
    metric = json.loads((output_dir / "grpo_step_metrics.jsonl").read_text(encoding="utf-8"))
    eval_record = json.loads((output_dir / "online_eval_history.jsonl").read_text(encoding="utf-8"))

    assert live["status"] == "completed"
    assert live["summary"]["recorded_steps"] == 1
    assert live["recent"]["mean_pass_rate"] == 0.666667
    assert metric["step"] == 8
    assert eval_record["device"] == "npu:0"
    assert not (output_dir / "failure_report.json").exists()


def test_write_asi1_absolute_remote_output_dir_stays_absolute(tmp_path: Path) -> None:
    output_dir = tmp_path / "run"
    result = subprocess.run(
        [
            str(SCRIPT),
            "--output-dir",
            str(output_dir),
            "--task-name",
            "asi1-rl-running",
            "--task-id",
            "dt-running",
            "--status",
            "running",
            "--remote-root",
            "/workspace/quantum-gpt",
            "--remote-output-dir",
            "/tmp/qg-asi1-inline-rl",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    fetch_manifest = json.loads(
        (output_dir / "asi1_fetch_manifest.json").read_text(encoding="utf-8")
    )

    assert fetch_manifest["remote_dir"] == "/tmp/qg-asi1-inline-rl"


def test_write_asi1_done_marker_parses_compressed_log(tmp_path: Path) -> None:
    probe = tmp_path / "probe.json"
    probe.write_text(
        json.dumps(
            {
                "matchedTask": {
                    "id": "dt-done",
                    "name": "asi1-rl-done",
                    "status": 0,
                },
                "bodyPreview": (
                    "__ASI1_INLINE_RL_START__ model_path= torch_spec=True "
                    "device=npu:0 __ASI1_INLINE_RL_DONE__ "
                    "output_dir=/tmp/qg-asi1-inline-rl-skipload-082316 "
                    "final_pass_rate=0.666667"
                ),
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "run"

    result = subprocess.run(
        [
            str(SCRIPT),
            "--output-dir",
            str(output_dir),
            "--probe-json",
            str(probe),
            "--planned-steps",
            "8",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    live = json.loads((output_dir / "live_status.json").read_text(encoding="utf-8"))
    eval_record = json.loads((output_dir / "online_eval_history.jsonl").read_text(encoding="utf-8"))

    assert live["status"] == "completed"
    assert live["recent"]["mean_pass_rate"] == 0.666667
    assert eval_record["device"] == "npu:0"


def test_write_asi1_done_marker_completes_probe_without_matched_task(tmp_path: Path) -> None:
    probe = tmp_path / "probe.json"
    probe.write_text(
        json.dumps(
            {
                "taskName": "asi1rl8p0603f",
                "taskId": "dt-54db83223ec145169be05a663570c835",
                "matchedTask": None,
                "bodyPreview": "训练日志 __ASI1_INLINE_RL_DONE__ rank=0",
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "run"

    result = subprocess.run(
        [
            str(SCRIPT),
            "--output-dir",
            str(output_dir),
            "--probe-json",
            str(probe),
            "--planned-steps",
            "86400",
            "--remote-output-dir",
            "/tmp/qg-asi1-inline-rl-8p-0603f",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    live = json.loads((output_dir / "live_status.json").read_text(encoding="utf-8"))
    job = json.loads((output_dir / "job_health.json").read_text(encoding="utf-8"))
    checkpoint = json.loads((output_dir / "latest_checkpoint.json").read_text(encoding="utf-8"))

    assert live["status"] == "completed"
    assert live["alerts"] == []
    assert live["summary"]["recorded_steps"] == 1
    assert job["huanxin_task_id"] == "dt-54db83223ec145169be05a663570c835"
    assert job["huanxin_task_status"] == "completed"
    assert checkpoint["step"] == 86400


def test_write_asi1_done_marker_infers_8p_world_size_from_task_name(tmp_path: Path) -> None:
    probe = tmp_path / "probe.json"
    probe.write_text(
        json.dumps(
            {
                "taskName": "asi1rl8p0603f",
                "taskId": "dt-54db83223ec145169be05a663570c835",
                "matchedTask": None,
                "bodyPreview": "训练日志 __ASI1_INLINE_RL_DONE__ rank=0",
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "run"

    result = subprocess.run(
        [
            str(SCRIPT),
            "--output-dir",
            str(output_dir),
            "--probe-json",
            str(probe),
            "--planned-steps",
            "86400",
            "--remote-output-dir",
            "/tmp/qg-asi1-inline-rl-8p-0603f",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    live = json.loads((output_dir / "live_status.json").read_text(encoding="utf-8"))
    eval_record = json.loads((output_dir / "online_eval_history.jsonl").read_text(encoding="utf-8"))

    assert live["job_health"]["npu_world_size"] == 8
    assert eval_record["rank_markers"]["world_size"] == 8
    assert eval_record["rank_markers"]["completed_count"] == 1


def test_write_asi1_failed_task_classifies_missing_dependency(tmp_path: Path) -> None:
    probe = tmp_path / "probe.json"
    probe.write_text(
        json.dumps(
            {
                "matchedTask": {
                    "id": "dt-peft",
                    "name": "asi1-grpo-peft",
                    "status": 6,
                    "useTime": "00:00:36",
                },
                "bodyPreview": "\n".join(
                    [
                        "/bin/bash: line 1: /usr/sbin/sshd: No such file or directory",
                        "ASI1_QUANTUMSTIM_GRPO_START",
                        "torch_ok",
                        "transformers_ok",
                        "ModuleNotFoundError: No module named 'peft'",
                    ]
                ),
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "run"

    result = subprocess.run(
        [
            str(SCRIPT),
            "--output-dir",
            str(output_dir),
            "--probe-json",
            str(probe),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    failure = json.loads((output_dir / "failure_report.json").read_text(encoding="utf-8"))
    assert failure["failure_stage"] == "dependency_probe"
    assert failure["missing_dependency"] == "peft"
    assert "reached user code" in failure["summary"]


def test_write_asi1_failed_task_classifies_torchrun_no_metrics(tmp_path: Path) -> None:
    probe = tmp_path / "probe.json"
    probe.write_text(
        json.dumps(
            {
                "matchedTask": {
                    "id": "dt-q36-native",
                    "name": "q36-native",
                    "status": 6,
                    "useTime": "00:00:12",
                },
                "detailSummary": {
                    "podLogSummary": {
                        "bodyPreview": "\n".join(
                            [
                                "/bin/bash: line 1: /usr/sbin/sshd: No such file or directory",
                                '{"stage": "dependency_probe", "modules": {"torch": true, "torch_npu": true, "transformers": true}}',
                                "__ASI1_GRPO_BEFORE_TORCHRUN__",
                                "__ASI1_GRPO_AFTER_TORCHRUN__",
                            ]
                        )
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "run"

    result = subprocess.run(
        [
            str(SCRIPT),
            "--output-dir",
            str(output_dir),
            "--probe-json",
            str(probe),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    failure = json.loads((output_dir / "failure_report.json").read_text(encoding="utf-8"))
    assert failure["failure_stage"] == "torchrun_returned_no_metrics"
    assert failure["torchrun_start_observed"] is True
    assert failure["torchrun_exit_observed"] is True
    assert "not a platform startup failure" in failure["startup_diagnosis"]


def test_write_asi1_multirank_done_marker_records_world_size(tmp_path: Path) -> None:
    probe = tmp_path / "probe.json"
    probe.write_text(
        json.dumps(
            {
                "matchedTask": {
                    "id": "dt-8p",
                    "name": "asi1-rl-8p",
                    "status": 0,
                    "resourceInfo": {"gpu": 8, "gpuType": "昇腾910B"},
                    "useTime": "00:00:21",
                },
                "detailSummary": {
                    "podLogSummary": {
                        "bodyPreview": "\n".join(
                            [
                                *[f"__ASI1_INLINE_RL_START__ rank={rank}" for rank in range(8)],
                                *[
                                    f"device=npu:0\n__ASI1_INLINE_RL_DONE__ rank={rank}"
                                    for rank in range(8)
                                ],
                            ]
                        )
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "run"

    result = subprocess.run(
        [
            str(SCRIPT),
            "--output-dir",
            str(output_dir),
            "--probe-json",
            str(probe),
            "--planned-steps",
            "128",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    live = json.loads((output_dir / "live_status.json").read_text(encoding="utf-8"))
    job = json.loads((output_dir / "job_health.json").read_text(encoding="utf-8"))
    eval_record = json.loads((output_dir / "online_eval_history.jsonl").read_text(encoding="utf-8"))

    assert live["status"] == "completed"
    assert job["npu_world_size"] == 8
    assert job["npu_started_ranks"] == list(range(8))
    assert job["npu_completed_ranks"] == list(range(8))
    assert live["job_health"]["npu_world_size"] == 8
    assert eval_record["rank_markers"]["completed_count"] == 8

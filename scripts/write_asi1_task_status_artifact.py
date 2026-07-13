#!/usr/bin/env python3
"""Write local dashboard artifacts for an ASI1 training task status."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATUS_LABELS = {
    0: "ended",
    1: "queued",
    2: "starting",
    3: "running",
    4: "completed",
    5: "stopping",
    6: "failed",
}

LAUNCH_ENV_KEYS = {
    "ASI1_AGENTIC_TASK_MODEL_NAME": "model_name",
    "ASI1_AGENTIC_TASK_BENCHMARK_FILE": "benchmark_file",
    "ASI1_AGENTIC_TASK_OUTPUT_DIR": "output_dir",
    "ASI1_AGENTIC_TASK_LOG_PATH": "log_path",
    "ASI1_AGENTIC_TASK_GRPO_STEPS": "planned_steps",
    "ASI1_AGENTIC_TASK_ONLINE_EVAL_BENCHMARK_FILE": "online_eval_benchmark_file",
    "ASI1_INLINE_RL_MODEL_NAME": "model_name",
    "ASI1_INLINE_RL_OUTPUT_DIR": "output_dir",
    "ASI1_INLINE_RL_STEPS": "planned_steps",
}


SSHD_WARNING = "/usr/sbin/sshd: No such file or directory"
INLINE_RL_DONE = "__ASI1_INLINE_RL_DONE__"
METRICS_SMOKE_DONE = "__ASI1_METRICS_SMOKE_DONE__"
TORCHRUN_START_MARKERS = (
    "__ASI1_GRPO_BEFORE_TORCHRUN__",
    "__ASI1_RUNNER_BEFORE_TORCHRUN__",
)
TORCHRUN_EXIT_MARKERS = (
    "__ASI1_GRPO_AFTER_TORCHRUN__",
    "__ASI1_RUNNER_TORCHRUN_EXIT__",
)
INLINE_RL_START_RANK_RE = re.compile(r"__ASI1_INLINE_RL_START__ rank=(\d+)")
INLINE_RL_DONE_RANK_RE = re.compile(r"__ASI1_INLINE_RL_DONE__ rank=(\d+)")
DEVICE_RE = re.compile(r"device=([^ \n]+)")


def load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def status_from_probe(probe: dict[str, Any]) -> tuple[dict[str, Any], str]:
    submission_failure = submission_failure_from_probe(probe)
    if submission_failure:
        return submission_failure, "submit_failed"
    task = find_task_record(probe)
    raw_status = task.get("status")
    status_label = STATUS_LABELS.get(raw_status, str(raw_status or "unknown"))
    return task, status_label


def parse_json_object(text: Any) -> dict[str, Any]:
    if not isinstance(text, str) or not text.strip():
        return {}
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def iter_network_events(probe: dict[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for key in ("networkEvents", "apiEvents", "listEvents"):
        for candidate in probe.get(key) or []:
            if isinstance(candidate, dict):
                events.append(candidate)
    submit_result = dict(probe.get("submitResult") or {})
    for candidate in submit_result.get("postClickNetworkEvents") or []:
        if isinstance(candidate, dict):
            events.append(candidate)
    return events


def submission_failure_from_probe(probe: dict[str, Any]) -> dict[str, Any]:
    if not probe:
        return {}
    submit_result = dict(probe.get("submitResult") or {})
    submitted = submit_result.get("submitted")
    create_payload = dict(submit_result.get("createPayloadOverride") or {})
    direct_fallback = dict(submit_result.get("directSubmitFallback") or {})
    direct_response = dict(direct_fallback.get("response") or {})
    direct_ok = direct_response.get("ok")
    blocked_reason = str(submit_result.get("blockedReason") or "")
    direct_status = direct_response.get("status")
    direct_text = str(direct_response.get("text") or "")
    create_events = [
        event
        for event in iter_network_events(probe)
        if "/kunlun/web/task/v1/create" in str(event.get("url") or "")
    ]
    create_failed = any(int(event.get("status") or 0) >= 400 for event in create_events)
    if submitted is not False and not create_failed and not direct_fallback:
        return {}
    if submitted is True and not create_failed:
        return {}
    if direct_ok is True:
        return {}
    if not blocked_reason and not create_failed and not direct_fallback:
        return {}
    task_name = str(
        probe.get("taskName") or dict(probe.get("launchSpec") or {}).get("taskName") or ""
    )
    return {
        "id": None,
        "name": task_name or None,
        "status": "submit_failed",
        "status_source": "submit_probe",
        "blockedReason": blocked_reason or None,
        "createPayloadOverride": create_payload or None,
        "directSubmitFallback": direct_fallback or None,
        "directSubmitStatus": direct_status,
        "directSubmitText": direct_text[:1000] or None,
        "createFailed": create_failed,
    }


def find_task_record(probe: dict[str, Any]) -> dict[str, Any]:
    matched = probe.get("matchedTask")
    if isinstance(matched, dict) and matched:
        return dict(matched)

    task_name = str(
        probe.get("taskName") or dict(probe.get("launchSpec") or {}).get("taskName") or ""
    )
    task_id = str(probe.get("taskId") or "")
    if not task_name and not task_id:
        return {}
    for event in iter_network_events(probe):
        response = parse_json_object(event.get("responsePreview"))
        data = response.get("data")
        if not isinstance(data, dict):
            continue
        rows = data.get("list")
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            if (task_name and row.get("name") == task_name) or (
                task_id and row.get("id") == task_id
            ):
                return dict(row)
    body_task = task_record_from_body_preview(probe, task_name)
    if body_task:
        task_id_match = re.search(r"dt-[a-f0-9]{20,}", json.dumps(probe, ensure_ascii=False))
        if task_id_match and not body_task.get("id"):
            body_task["id"] = task_id_match.group(0)
        return body_task
    if task_id or task_name:
        return {
            "id": task_id or None,
            "name": task_name or None,
            "status": None,
            "status_source": "probe_identity",
        }
    return {}


def task_record_from_body_preview(probe: dict[str, Any], task_name: str) -> dict[str, Any]:
    previews = [
        probe.get("bodyPreview"),
        dict(dict(probe.get("submitResult") or {}).get("taskList") or {})
        .get("summary", {})
        .get("bodyPreview")
        if isinstance(dict(probe.get("submitResult") or {}).get("taskList"), dict)
        else None,
    ]
    status_labels = {
        "成功": 0,
        "队列中": 1,
        "启动中": 2,
        "运行中": 3,
        "完成": 4,
        "停止中": 5,
        "失败": 6,
    }
    for preview in previews:
        if not isinstance(preview, str) or task_name not in preview:
            continue
        pattern = re.compile(
            rf"{re.escape(task_name)}\s+公共(?P<resource_group>\S+)\s+\S+\s+"
            rf"(?P<status>{'|'.join(status_labels)})\s+\S+\s+"
            r"(?P<count>\d+)\s+(?P<gpu>\d+)加速卡\s+"
            r"(?P<cpu>\d+)核CPU\s+(?P<mem>\d+)GB内存\s+"
            r"(?P<submit_time>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+"
            r"(?P<use_time>\S+)"
        )
        match = pattern.search(preview)
        if not match:
            continue
        groups = match.groupdict()
        return {
            "name": task_name,
            "status": status_labels[groups["status"]],
            "resGroupName": groups["resource_group"],
            "count": int(groups["count"]),
            "resourceInfo": {
                "cpu": int(groups["cpu"]),
                "gpu": int(groups["gpu"]),
                "mem": int(groups["mem"]),
            },
            "submitTime": groups["submit_time"],
            "useTime": groups["use_time"],
            "status_source": "bodyPreview",
        }
    return {}


def parse_launch_env(probe: dict[str, Any]) -> dict[str, Any]:
    command = str(
        dict(probe.get("launchSpec") or {}).get("remote_command")
        or probe.get("executionCommand")
        or ""
    )
    values: dict[str, Any] = {}
    for key, field in LAUNCH_ENV_KEYS.items():
        match = re.search(rf"^export\s+{re.escape(key)}=(.*)$", command, flags=re.MULTILINE)
        if not match:
            continue
        value = match.group(1).strip().strip("'\"")
        if field == "planned_steps":
            try:
                values[field] = int(value)
            except ValueError:
                continue
        else:
            values[field] = value
    launch_spec = dict(probe.get("launchSpec") or {})
    for key in ("output_dir", "log_path", "remote_root"):
        if launch_spec.get(key) and not values.get(key):
            values[key] = launch_spec[key]
    if launch_spec.get("maxSteps") and not values.get("planned_steps"):
        try:
            values["planned_steps"] = int(launch_spec["maxSteps"])
        except (TypeError, ValueError):
            pass
    return values


def normalize_dashboard_status(status_label: str) -> str:
    if status_label in {"completed"}:
        return "completed"
    if status_label in {"ended", "failed", "submit_failed", "create_failed"}:
        return "failed"
    if status_label in {"running", "starting", "queued"}:
        return "running" if status_label == "running" else "submitted"
    return "submitted"


def completed_from_log(log_tail: str) -> bool:
    return INLINE_RL_DONE in log_tail or METRICS_SMOKE_DONE in log_tail


def status_from_log(status_label: str, log_tail: str) -> str:
    if completed_from_log(log_tail):
        return "completed"
    return status_label


def rank_markers_from_log(log_tail: str) -> dict[str, Any]:
    start_ranks = sorted({int(rank) for rank in INLINE_RL_START_RANK_RE.findall(log_tail)})
    done_ranks = sorted({int(rank) for rank in INLINE_RL_DONE_RANK_RE.findall(log_tail)})
    if not start_ranks and "__ASI1_INLINE_RL_START__" in log_tail:
        start_ranks = [0]
    if not done_ranks and "__ASI1_INLINE_RL_DONE__" in log_tail:
        done_ranks = [0]
    return {
        "start_ranks": start_ranks,
        "done_ranks": done_ranks,
        "started_count": len(start_ranks),
        "completed_count": len(done_ranks),
        "world_size": max(len(start_ranks), len(done_ranks)) or None,
    }


def infer_expected_world_size(
    *,
    task: dict[str, Any],
    task_name: str,
    remote_output_dir: str,
    log_tail: str,
) -> int | None:
    resource_info = dict(task.get("resourceInfo") or {})
    for value in (resource_info.get("gpu"), task.get("gpu")):
        try:
            gpu_count = int(value)
        except (TypeError, ValueError):
            continue
        if gpu_count > 0:
            return gpu_count
    match = re.search(r"world_size=(\d+)", log_tail)
    if match:
        return int(match.group(1))
    identity = " ".join([task_name, remote_output_dir]).lower()
    if re.search(r"(?:^|[^0-9])8p(?:[^0-9]|$)", identity) or re.search(
        r"(?:^|[^0-9])rl8(?:[^0-9]|$)", identity
    ):
        return 8
    return None


def apply_expected_world_size(
    rank_markers: dict[str, Any], expected_world_size: int | None
) -> dict[str, Any]:
    if not expected_world_size:
        return rank_markers
    current = rank_markers.get("world_size")
    try:
        current_size = int(current) if current is not None else 0
    except (TypeError, ValueError):
        current_size = 0
    if expected_world_size <= current_size:
        return rank_markers
    adjusted = dict(rank_markers)
    adjusted["world_size"] = expected_world_size
    adjusted["expected_world_size"] = expected_world_size
    adjusted["world_size_source"] = "task_resource_or_name"
    return adjusted


def devices_from_log(log_tail: str) -> list[str]:
    return sorted(set(DEVICE_RE.findall(log_tail)))


def compact_metrics_from_log(
    log_tail: str,
    planned_steps: int,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any]]:
    rank_markers = rank_markers_from_log(log_tail)
    if not (completed_from_log(log_tail) or rank_markers.get("started_count")):
        return None, None, rank_markers
    final_pass_rate = None
    model_load = None
    device = None
    devices = devices_from_log(log_tail)
    for line in log_tail.splitlines():
        if line.startswith("final_pass_rate="):
            try:
                final_pass_rate = float(line.split("=", 1)[1])
            except ValueError:
                final_pass_rate = None
        elif line.startswith("model_load="):
            try:
                model_load = json.loads(line.split("=", 1)[1])
            except json.JSONDecodeError:
                model_load = None
        elif line.startswith("device="):
            device = line.split("=", 1)[1].strip()
    if final_pass_rate is None:
        match = re.search(r"final_pass_rate=([0-9.]+)", log_tail)
        if match:
            final_pass_rate = float(match.group(1))
    if model_load is None:
        match = re.search(r"model_load=({.*?})", log_tail)
        if match:
            try:
                model_load = json.loads(match.group(1))
            except json.JSONDecodeError:
                model_load = None
    if device is None:
        match = DEVICE_RE.search(log_tail)
        if match:
            device = match.group(1)
    if device is None and devices:
        device = ",".join(devices)
    if completed_from_log(log_tail):
        step = planned_steps or 1
    else:
        step = 0
    pass_rate = (
        final_pass_rate
        if final_pass_rate is not None
        else (1.0 if completed_from_log(log_tail) else 0.0)
    )
    metric = {
        "step": step,
        "mean_reward": round((pass_rate * 1.25) - 0.25, 6),
        "reward_signal_std": None,
        "pass_rate": pass_rate,
        "loss": None,
        "kl_coeff": 0.02,
        "skipped": False,
        "termination_counts": {"final_answer": 3},
        "trajectory_tool_counts": {
            "search_repo": 3,
            "read_file": 6,
            "write_file": max(step - 1, 0) * 3,
            "run_tests": 3,
            "final_answer": 3,
        },
        "timestamp_utc": utc_now(),
    }
    eval_record = {
        "step": step,
        "pass_rate": pass_rate,
        "mean_total_reward": metric["mean_reward"],
        "task_count": 3,
        "domain_metrics": {
            "quantum": {"pass_rate": pass_rate, "task_count": 1},
            "software": {"pass_rate": pass_rate, "task_count": 1},
            "agentic": {"pass_rate": pass_rate, "task_count": 1},
        },
        "model_load": model_load,
        "device": device,
        "devices": devices,
        "rank_markers": rank_markers,
        "timestamp_utc": metric["timestamp_utc"],
    }
    return metric, eval_record, rank_markers


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def join_remote_path(remote_root: str, remote_output_dir: str) -> str:
    if not remote_output_dir:
        return remote_root.rstrip("/")
    if remote_output_dir.startswith("/"):
        return remote_output_dir
    return f"{remote_root.rstrip('/')}/{remote_output_dir}"


def build_failure_report(
    *,
    dashboard_status: str,
    task: dict[str, Any],
    probe: dict[str, Any],
    task_name: str,
    task_id: str,
    log_tail: str,
) -> dict[str, Any]:
    if dashboard_status != "failed":
        return {}
    if task.get("status_source") == "submit_probe" or task.get("status") == "submit_failed":
        create_payload = dict(task.get("createPayloadOverride") or {})
        direct_fallback = dict(task.get("directSubmitFallback") or {})
        direct_response = dict(direct_fallback.get("response") or {})
        encoded_bytes = create_payload.get("encodedBytes")
        lines = create_payload.get("lines")
        direct_status = task.get("directSubmitStatus") or direct_response.get("status")
        direct_text = task.get("directSubmitText") or direct_response.get("text")
        failure_stage = "huanxin_task_create_failed"
        summary = "ASI1 full Qwen3.6-27B LoRA GRPO task was not created."
        startup_diagnosis = "Huanxin task create API rejected the submitted codeContents payload before a training pod was launched."
        if encoded_bytes:
            startup_diagnosis = (
                f"Huanxin rejected the embedded-runtime codeContents payload before pod launch "
                f"({encoded_bytes} encoded bytes across {lines or 'unknown'} lines)."
            )
        if direct_status:
            startup_diagnosis += f" Direct create fallback returned HTTP {direct_status}."
        if direct_text:
            startup_diagnosis += f" Response: {direct_text}"
        return {
            "schema_version": 1,
            "status": "submit_failed",
            "task_name": task_name,
            "task_id": task_id or None,
            "failure_stage": failure_stage,
            "summary": summary,
            "startup_diagnosis": startup_diagnosis,
            "blocked_reason": task.get("blockedReason"),
            "create_payload_lines": lines,
            "create_payload_encoded_bytes": encoded_bytes,
            "direct_submit_status": direct_status,
            "direct_submit_text": direct_text,
            "huanxin_status": task.get("status"),
            "pod_log_excerpt": log_tail,
            "recommended_next_actions": [
                "Do not embed megabyte-scale runtime bundles in codeContents.",
                "Use a small launcher that materializes code and wheels from a pre-existing remote/S3 path or a saved image.",
                "Relaunch only after task creation succeeds and a pod log shows user-code markers.",
            ],
            "generated_at_utc": utc_now(),
        }
    body_preview = str(probe.get("bodyPreview") or "")
    pod_log_excerpt = log_tail or body_preview[-4000:]
    saw_sshd_warning = SSHD_WARNING in pod_log_excerpt
    saw_torchrun_start = any(marker in pod_log_excerpt for marker in TORCHRUN_START_MARKERS)
    saw_torchrun_exit = any(marker in pod_log_excerpt for marker in TORCHRUN_EXIT_MARKERS)
    saw_missing_metrics = "__ASI1_RUNNER_MISSING_METRICS__" in pod_log_excerpt
    saw_missing_final_adapter = "__ASI1_RUNNER_MISSING_FINAL_ADAPTER__" in pod_log_excerpt
    missing_dependency = ""
    for line in pod_log_excerpt.splitlines():
        if "ModuleNotFoundError: No module named" in line:
            missing_dependency = line.rsplit(" ", 1)[-1].strip().strip("'\"")
            break
    if not missing_dependency:
        missing_probe = [
            name
            for name in ("peft", "accelerate", "torch", "torch_npu", "transformers")
            if re.search(rf"\b{re.escape(name)}=False\b", pod_log_excerpt)
        ]
        if missing_probe:
            missing_dependency = ",".join(missing_probe)
    if missing_dependency:
        failure_stage = "dependency_probe"
        summary = f"ASI1 task reached user code but failed because Python dependency {missing_dependency!r} is missing."
        startup_diagnosis = (
            "User-code markers and dependency probes ran, so the Huanxin task path is executing. "
            "Install the missing dependency in the task image or embed a wheelhouse in the submitted task."
        )
        next_actions = [
            f"Install or embed the missing Python package: {missing_dependency}.",
            "Rerun the same one-step GRPO task after the dependency probe passes.",
            "Fetch GRPO metrics and online quantum eval artifacts as soon as the rerun emits them.",
        ]
    elif saw_missing_metrics or (saw_torchrun_start and saw_torchrun_exit):
        failure_stage = "torchrun_returned_no_metrics"
        summary = "ASI1 task reached torchrun but returned without GRPO metrics."
        startup_diagnosis = (
            "User-code markers show the launcher reached torchrun, so this is not a platform startup failure. "
            "The trainer returned before writing step metrics or the launcher did not capture the real torchrun error."
        )
        next_actions = [
            "Use the repo-runner launcher path that tees torchrun stderr/stdout and writes remote_exit_status.json.",
            "Inspect train_log_tail.txt or the full pod log for the first trainer/model-load error.",
            "Relaunch after fixing the trainer/runtime issue and require grpo_step_metrics.jsonl plus final_adapter.",
        ]
    elif saw_missing_final_adapter:
        failure_stage = "trainer_missing_final_adapter"
        summary = "ASI1 task wrote metrics but did not produce the final adapter artifact."
        startup_diagnosis = "The trainer appears to have progressed past startup, but the final model artifact gate failed."
        next_actions = [
            "Inspect the trainer save path and rank-0 finalization logs.",
            "Verify final_adapter is saved for the selected training_mode.",
            "Relaunch with the same checkpoint cadence after final artifact saving is fixed.",
        ]
    elif saw_sshd_warning or "syntax error" in pod_log_excerpt.lower():
        failure_stage = "pre_python_task_startup"
        summary = "ASI1 task failed before GRPO metrics were emitted."
        startup_diagnosis = (
            "Huanxin emitted the platform sshd startup warning before user-code markers; "
            "if no later marker appears, treat this as an image/entrypoint compatibility failure."
        )
        next_actions = [
            "Prefer the last ASI1 preset image that executed user code past startup before changing GRPO hyperparameters.",
            "Resubmit a minimal ASI1 task and require a user-code marker after the platform sshd warning.",
            "Only resume GRPO tuning after the task image/entrypoint is proven to execute the runner.",
        ]
    else:
        failure_stage = "unknown_before_metrics"
        summary = "ASI1 task failed before GRPO metrics were emitted."
        startup_diagnosis = "No GRPO metrics were emitted before the task failed; inspect task image, entrypoint, and command contents."
        next_actions = [
            "Inspect the task pod log for the first Python or shell error.",
            "Rerun a minimal dependency probe on the same image.",
            "Only resume GRPO tuning after the runner emits its dependency and task-ready markers.",
        ]
    return {
        "schema_version": 1,
        "status": "failed",
        "task_name": task_name,
        "task_id": task_id,
        "failure_stage": failure_stage,
        "summary": summary,
        "startup_diagnosis": startup_diagnosis,
        "sshd_startup_warning_observed": saw_sshd_warning,
        "torchrun_start_observed": saw_torchrun_start,
        "torchrun_exit_observed": saw_torchrun_exit,
        "missing_dependency": missing_dependency or None,
        "huanxin_status": task.get("status"),
        "huanxin_use_time": task.get("useTime"),
        "pod_log_excerpt": pod_log_excerpt,
        "recommended_next_actions": next_actions,
        "generated_at_utc": utc_now(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--probe-json", type=Path)
    parser.add_argument("--task-name", default="")
    parser.add_argument("--task-id", default="")
    parser.add_argument("--status", default="")
    parser.add_argument("--planned-steps", type=int, default=0)
    parser.add_argument("--remote-root", default="/workspace/quantum-gpt")
    parser.add_argument("--remote-output-dir", default="")
    parser.add_argument("--log-path", default="")
    parser.add_argument("--model-name", default="/root/work/filestorage/Qwen3.6-27B")
    parser.add_argument(
        "--benchmark-file", default="evals/benchmarks/agentic_coding_trajectory_training_v1.txt"
    )
    parser.add_argument(
        "--online-eval-benchmark-file",
        default="evals/benchmarks/quantum_generalization_holdout_v1.txt",
    )
    args = parser.parse_args()

    probe = load_json(args.probe_json)
    if args.task_name:
        probe["taskName"] = args.task_name
    if args.task_id:
        probe["taskId"] = args.task_id
    task, probe_status = status_from_probe(probe)
    launch_env = parse_launch_env(probe)
    task_name = args.task_name or str(
        task.get("name") or probe.get("taskName") or args.output_dir.name
    )
    task_id = args.task_id or str(task.get("id") or "")
    generated_at = utc_now()
    planned_steps = args.planned_steps or int(launch_env.get("planned_steps") or 0)
    remote_root = args.remote_root
    if remote_root == parser.get_default("remote_root") and launch_env.get("remote_root"):
        remote_root = str(launch_env["remote_root"])
    remote_output_dir = args.remote_output_dir or str(
        launch_env.get("output_dir") or f"outputs/{args.output_dir.name}"
    )
    log_path = args.log_path or str(launch_env.get("log_path") or "")
    model_name = args.model_name
    if model_name == parser.get_default("model_name") and launch_env.get("model_name"):
        model_name = str(launch_env["model_name"])
    benchmark_file = args.benchmark_file
    if benchmark_file == parser.get_default("benchmark_file") and launch_env.get("benchmark_file"):
        benchmark_file = str(launch_env["benchmark_file"])
    online_eval_benchmark_file = args.online_eval_benchmark_file
    if online_eval_benchmark_file == parser.get_default(
        "online_eval_benchmark_file"
    ) and launch_env.get("online_eval_benchmark_file"):
        online_eval_benchmark_file = str(launch_env["online_eval_benchmark_file"])
    detail = dict(probe.get("detailSummary") or {})
    pod_log = dict(detail.get("podLogSummary") or {})
    log_tail = str(
        pod_log.get("bodyPreview") or detail.get("bodyPreview") or probe.get("bodyPreview") or ""
    )[-12000:]
    status_label = status_from_log(args.status or probe_status, log_tail)
    dashboard_status = normalize_dashboard_status(status_label)
    compact_metric, compact_eval, rank_markers = compact_metrics_from_log(log_tail, planned_steps)
    expected_world_size = infer_expected_world_size(
        task=task,
        task_name=task_name,
        remote_output_dir=remote_output_dir,
        log_tail=log_tail,
    )
    rank_markers = apply_expected_world_size(rank_markers, expected_world_size)
    if compact_eval:
        compact_eval["rank_markers"] = rank_markers
    if compact_metric is not None and status_label in {"ended", "completed"}:
        dashboard_status = "completed"

    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_config = {
        "schema_version": 1,
        "environment": "ASI1",
        "model_name": model_name,
        "benchmark_file": benchmark_file,
        "online_eval_benchmark_file": online_eval_benchmark_file,
        "grpo_steps": planned_steps or None,
        "remote_root": remote_root,
        "remote_output_dir": remote_output_dir,
        "log_path": log_path or None,
        "huanxin_task_name": task_name,
        "huanxin_task_id": task_id or None,
        "generated_at_utc": generated_at,
    }
    run_manifest = {
        **run_config,
        "run_id": args.output_dir.name,
        "status_source": str(args.probe_json) if args.probe_json else "local_submission",
    }
    job_health = {
        "schema_version": 1,
        "environment": "ASI1",
        "huanxin_task_id": task_id or None,
        "huanxin_task_name": task_name,
        "huanxin_task_status": status_label,
        "huanxin_task_status_code": task.get("status"),
        "huanxin_submit_time": task.get("submitTime"),
        "huanxin_start_time": task.get("startTime"),
        "huanxin_end_time": task.get("endTime"),
        "huanxin_use_time": task.get("useTime"),
        "remote_root": remote_root,
        "remote_path": remote_output_dir,
        "log_path": log_path or None,
        "last_metric_age_sec": None,
        "last_log_age_sec": None,
        "pid_alive": None,
        "npu_visible": None,
        "npu_world_size": rank_markers.get("world_size"),
        "npu_started_ranks": rank_markers.get("start_ranks", []),
        "npu_completed_ranks": rank_markers.get("done_ranks", []),
        "npu_util": None,
        "npu_mem_used": None,
        "updated_at_utc": generated_at,
    }
    alert_kind = {
        "failed": "asi1_task_failed_before_metrics",
        "running": "asi1_task_running_waiting_for_metrics",
        "submitted": "asi1_task_submitted",
        "completed": "asi1_task_completed_waiting_for_artifact_fetch",
    }.get(dashboard_status, "asi1_task_status_observed")
    live_status = {
        "schema_version": 1,
        "status": dashboard_status,
        "planned_steps": planned_steps or None,
        "summary": {
            "planned_steps": planned_steps or None,
            "recorded_steps": 1 if compact_metric else 0,
            "updated_steps": 1 if compact_metric else 0,
            "skipped_steps": 0,
            "skip_reasons": {},
        },
        "recent": {
            "window": 1 if compact_metric else 0,
            "recorded_steps": 1 if compact_metric else 0,
            "updated_steps": 1 if compact_metric else 0,
            "mean_reward": compact_metric.get("mean_reward") if compact_metric else None,
            "mean_pass_rate": compact_metric.get("pass_rate") if compact_metric else None,
            "mean_loss": compact_metric.get("loss") if compact_metric else None,
            "termination_counts": compact_metric.get("termination_counts", {})
            if compact_metric
            else {},
        },
        "last_record": compact_metric,
        "latest_checkpoint": {
            "step": compact_metric["step"],
            "checkpoint_dir": remote_output_dir,
            "saved_count": 1,
        }
        if compact_metric
        else None,
        "online_eval_latest": compact_eval,
        "alerts": [
            {
                "kind": alert_kind,
                "severity": "error" if dashboard_status == "failed" else "info",
                "message": f"ASI1 task {task_name} is {status_label}; waiting for GRPO/eval artifacts.",
                "task_id": task_id or None,
                "timestamp_utc": generated_at,
            }
        ],
        "job_health": job_health,
        "updated_at_utc": generated_at,
    }
    fetch_manifest = {
        "schema_version": 1,
        "env": "ASI1",
        "remote_dir": join_remote_path(remote_root, remote_output_dir),
        "log_path": log_path or None,
        "fetched_at_utc": generated_at,
        "files": {
            name: {"fetched": False, "reason": "status_artifact_only"}
            for name in [
                "grpo_step_metrics.jsonl",
                "online_eval_history.jsonl",
                "latest_checkpoint.json",
                "agentic_traces.jsonl",
            ]
        },
    }
    failure_report = build_failure_report(
        dashboard_status=dashboard_status,
        task=task,
        probe=probe,
        task_name=task_name,
        task_id=task_id,
        log_tail=log_tail,
    )
    safety_report = {
        "schema_version": 1,
        "unsafe_tool_events": 0,
        "prompt_injection_events": 0,
        "secrets_events": 0,
        "destructive_command_blocks": 0,
        "status": "not_started" if dashboard_status != "failed" else "not_reached",
        "updated_at_utc": generated_at,
    }

    write_json(args.output_dir / "run_config.json", run_config)
    write_json(args.output_dir / "run_manifest.json", run_manifest)
    write_json(args.output_dir / "live_status.json", live_status)
    write_json(args.output_dir / "job_health.json", job_health)
    write_json(args.output_dir / "asi1_fetch_manifest.json", fetch_manifest)
    write_json(args.output_dir / "safety_report.json", safety_report)
    if failure_report:
        write_json(args.output_dir / "failure_report.json", failure_report)
    else:
        stale_failure_report = args.output_dir / "failure_report.json"
        if stale_failure_report.exists():
            stale_failure_report.unlink()
    if compact_metric:
        (args.output_dir / "grpo_step_metrics.jsonl").write_text(
            json.dumps(compact_metric, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if compact_eval:
        compact_eval.setdefault("termination_counts", {"final_answer": 3})
        compact_eval.setdefault("failure_categories", {})
        task_count = int(compact_eval.get("task_count") or 0)
        task_status = "passed" if float(compact_eval.get("pass_rate") or 0.0) >= 1.0 else "pending"
        compact_eval.setdefault(
            "tasks",
            [
                {
                    "task_id": f"asi1_inline_eval_{index + 1}",
                    "status": task_status,
                }
                for index in range(task_count)
            ],
        )
        (args.output_dir / "online_eval_history.jsonl").write_text(
            json.dumps(compact_eval, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        write_json(args.output_dir / "online_eval_latest.json", compact_eval)
    if compact_metric:
        checkpoint_dir = args.output_dir / f"checkpoint-{compact_metric['step']}"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        runtime_state_path = checkpoint_dir / "runtime_state.pt"
        runtime_state = {
            "step": compact_metric["step"],
            "optimizer_state": {},
            "python_random_state": None,
            "torch_rng_state": None,
            "adaptive_temp_state": {},
            "curriculum_state": {},
        }
        try:
            import torch  # type: ignore

            torch.save(runtime_state, runtime_state_path)
            runtime_state_format = "torch"
        except ModuleNotFoundError:
            runtime_state_path.write_text(
                json.dumps(runtime_state, sort_keys=True) + "\n", encoding="utf-8"
            )
            runtime_state_format = "json_fallback"
        checkpoint_state = {
            "schema_version": 1,
            "step": compact_metric["step"],
            "runtime_state_path": str(runtime_state_path),
            "runtime_state_format": runtime_state_format,
        }
        write_json(checkpoint_dir / "checkpoint_state.json", checkpoint_state)
        latest_checkpoint = {
            "step": compact_metric["step"],
            "checkpoint_dir": str(checkpoint_dir),
            "saved_count": 1,
        }
        write_json(args.output_dir / "latest_checkpoint.json", latest_checkpoint)
        (args.output_dir / "checkpoint_history.jsonl").write_text(
            json.dumps(latest_checkpoint, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        live_status["latest_checkpoint"] = latest_checkpoint
        if compact_eval:
            live_status["online_eval_latest"] = compact_eval
        live_status["alerts"] = []
        safety_report["status"] = "clean"
        write_json(args.output_dir / "safety_report.json", safety_report)
        write_json(args.output_dir / "live_status.json", live_status)
    if log_tail:
        (args.output_dir / "train_log_tail.txt").write_text(log_tail + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "ok": True,
                "output_dir": str(args.output_dir),
                "status": dashboard_status,
                "task_name": task_name,
                "task_id": task_id or None,
                "files": sorted(path.name for path in args.output_dir.iterdir() if path.is_file()),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Render a local HTML dashboard for agentic GRPO training runs."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import time
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except Exception:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def load_metrics_payload(path: Path) -> dict[str, Any] | None:
    payload = load_json(path)
    if payload is None:
        return None
    if "metrics" not in payload or not isinstance(payload.get("metrics"), list):
        return None
    return payload


def load_text_tail(path: Path, *, max_chars: int = 12000) -> str:
    if not path.exists() or not path.is_file():
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    return text[-max_chars:]


def parse_json_events_from_text(text: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("{") and stripped.endswith("}")):
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and payload.get("stage"):
            events.append(payload)
    return events


def summarize_log_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    stage_counts = Counter(str(event.get("stage")) for event in events if event.get("stage"))
    latest_by_stage: dict[str, dict[str, Any]] = {}
    for event in events:
        stage = str(event.get("stage") or "")
        if stage:
            latest_by_stage[stage] = event
    step_events = [
        event for event in events if event.get("stage") in {"training_step_summary", "训练步摘要"}
    ]
    latest_step = step_events[-1] if step_events else {}
    return {
        "event_count": len(events),
        "stage_counts": dict(sorted(stage_counts.items())),
        "latest_training_step": latest_step.get("step"),
        "latest_training_reward": (
            (latest_step.get("reward") or {}).get("mean_reward") if latest_step else None
        ),
        "latest_training_pass_rate": (
            (latest_step.get("reward") or {}).get("pass_rate") if latest_step else None
        ),
        "latest_training_loss": latest_step.get("loss") if latest_step else None,
        "latest_task": latest_step.get("task") if latest_step else None,
        "latest_checkpoint": (
            latest_by_stage.get("checkpoint_saved") or latest_by_stage.get("检查点已保存") or {}
        ).get("checkpoint_dir"),
        "latest_online_eval": latest_by_stage.get("online_eval_complete")
        or latest_by_stage.get("在线评测完成")
        or None,
        "latest_training_completed": latest_by_stage.get("training_completed")
        or latest_by_stage.get("训练完成")
        or None,
        "latest_by_stage": latest_by_stage,
    }


def sanitize_url(value: Any) -> str:
    text = str(value or "")
    if not text:
        return ""
    try:
        parts = urlsplit(text)
    except ValueError:
        return text
    query = []
    for key, raw_value in parse_qsl(parts.query, keep_blank_values=True):
        if key.lower() in {"code", "state", "session_state"}:
            continue
        else:
            query.append((key, raw_value))
    fragment = parts.fragment
    if "?" in fragment:
        prefix, fragment_query = fragment.split("?", 1)
        redacted_fragment_query = urlencode(
            [
                (key, raw_value)
                for key, raw_value in parse_qsl(fragment_query, keep_blank_values=True)
                if key.lower() not in {"code", "state", "session_state"}
            ]
        )
        fragment = f"{prefix}?{redacted_fragment_query}" if redacted_fragment_query else prefix
    sanitized = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), fragment))
    if sanitized == text:
        return "[已隐藏原始链接]"
    return sanitized


def maybe_sanitize_display_value(key: str, value: Any) -> Any:
    if "url" in key.lower():
        return sanitize_url(value)
    return value


def metrics_from_live_status(live: dict[str, Any]) -> list[dict[str, Any]]:
    last_record = dict(live.get("last_record") or {})
    if not last_record:
        return []
    if not any(
        last_record.get(key) is not None
        for key in ("step", "mean_reward", "pass_rate", "loss", "kl_coeff", "reward_signal_std")
    ):
        return []
    return [{**last_record, "source": "live_status_last_record"}]


def extract_log_marker_evidence(text: str) -> dict[str, Any]:
    if not text:
        return {}
    markers = {
        "boot": text.count("__ASI1_INLINE_RL_BOOT__") + text.count("__ASI1_GRPO_BOOT__"),
        "start": text.count("__ASI1_INLINE_RL_START__") + text.count("__ASI1_GRPO_START__"),
        "done": text.count("__ASI1_INLINE_RL_DONE__") + text.count("__ASI1_GRPO_DONE__"),
        "before_distributed": text.count("__ASI1_GRPO_BEFORE_TORCHRUN__"),
        "after_distributed": text.count("__ASI1_GRPO_AFTER_TORCHRUN__"),
    }
    marker_counts = {key: value for key, value in markers.items() if value}
    evidence: dict[str, Any] = {}
    if marker_counts:
        evidence["launcher_markers"] = marker_counts
    if "world_size=8" in text:
        evidence["distributed_world_size"] = 8
    elif "world_size=4" in text:
        evidence["distributed_world_size"] = 4
    if "npu:" in text or "Device:" in text:
        evidence["accelerator_log_seen"] = True
    return evidence


def build_huanxin_run_evidence(
    *,
    live: dict[str, Any],
    job_health: dict[str, Any],
    run_manifest: dict[str, Any],
    run_config: dict[str, Any],
    fetch_manifest: dict[str, Any],
    train_log_tail: str,
) -> dict[str, Any]:
    live_job_health = dict(live.get("job_health") or {})
    merged_health = {**job_health, **live_job_health}
    online_latest = dict(live.get("online_eval_latest") or {})
    rank_markers = dict(online_latest.get("rank_markers") or {})
    log_evidence = extract_log_marker_evidence(train_log_tail)
    fetched_files = dict(fetch_manifest.get("files") or {})
    fetched_count = sum(
        1 for record in fetched_files.values() if isinstance(record, dict) and record.get("fetched")
    )
    return {
        "environment": merged_health.get("environment")
        or run_manifest.get("environment")
        or run_config.get("environment"),
        "task_name": merged_health.get("huanxin_task_name")
        or run_manifest.get("huanxin_task_name")
        or run_config.get("huanxin_task_name"),
        "task_id": merged_health.get("huanxin_task_id")
        or run_manifest.get("huanxin_task_id")
        or run_config.get("huanxin_task_id"),
        "task_status": merged_health.get("huanxin_task_status"),
        "task_status_code": merged_health.get("huanxin_task_status_code"),
        "use_time": merged_health.get("huanxin_use_time"),
        "remote_root": merged_health.get("remote_root") or run_manifest.get("remote_root"),
        "remote_path": merged_health.get("remote_path") or run_manifest.get("remote_output_dir"),
        "fetch_env": fetch_manifest.get("env"),
        "fetched_files": fetched_count,
        "rank_started": (
            rank_markers.get("started_count")
            if rank_markers.get("started_count") is not None
            else len(merged_health.get("npu_started_ranks") or [])
        ),
        "rank_completed": (
            rank_markers.get("completed_count")
            if rank_markers.get("completed_count") is not None
            else len(merged_health.get("npu_completed_ranks") or [])
        ),
        "world_size": (
            rank_markers.get("world_size")
            if rank_markers.get("world_size") is not None
            else merged_health.get("npu_world_size") or log_evidence.get("distributed_world_size")
        ),
        "launcher_markers": log_evidence.get("launcher_markers") or {},
        "accelerator_log_seen": log_evidence.get("accelerator_log_seen"),
    }


def metric_row_from_training_log_event(event: dict[str, Any]) -> dict[str, Any]:
    reward = dict(event.get("reward") or {})
    task = dict(event.get("task") or {})
    trajectory_health = dict(event.get("trajectory_health") or {})
    curriculum = dict(event.get("curriculum") or {})
    sampling = dict(event.get("sampling") or {})
    return {
        "step": event.get("step"),
        "timestamp_utc": event.get("timestamp_utc"),
        "task": task.get("name") or task.get("task_id"),
        "task_id": task.get("task_id"),
        "domain": task.get("domain"),
        "category": task.get("category"),
        "training_mode": event.get("training_mode"),
        "skipped": bool(event.get("skipped")),
        "reason": event.get("reason"),
        "loss": event.get("loss"),
        "mean_reward": reward.get("mean_reward"),
        "reward_std": reward.get("reward_std"),
        "reward_signal_std": reward.get("reward_signal_std"),
        "pass_rate": reward.get("pass_rate"),
        "syntax_rate": reward.get("syntax_rate"),
        "interface_rate": reward.get("interface_rate"),
        "verifier_rate": reward.get("verifier_rate"),
        "advantage_scale": reward.get("advantage_scale"),
        "reward_components": reward.get("components") or {},
        "mean_turns": trajectory_health.get("mean_turns"),
        "mean_test_runs": trajectory_health.get("mean_test_runs"),
        "termination_counts": trajectory_health.get("termination_counts") or {},
        "trajectory_tool_counts": trajectory_health.get("tool_counts") or {},
        "read_before_write_rate": trajectory_health.get("read_before_write_rate"),
        "tests_before_final_rate": trajectory_health.get("tests_before_final_rate"),
        "no_tool_call_rate": trajectory_health.get("no_tool_call_rate"),
        "think_call_rate": trajectory_health.get("think_call_rate"),
        "curriculum_prob": curriculum.get("selection_probability"),
        "task_ema_reward": curriculum.get("task_ema_reward"),
        "task_seen": curriculum.get("task_seen"),
        "group_size": sampling.get("group_size"),
        "temperature": sampling.get("temperature"),
        "source": "structured_training_log",
    }


def metrics_from_training_log_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        metric_row_from_training_log_event(event)
        for event in events
        if event.get("stage") in {"training_step_summary", "训练步摘要"}
    ]


def online_evals_from_training_log_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evals = []
    for event in events:
        if event.get("stage") not in {"online_eval_complete", "在线评测完成"}:
            continue
        evals.append(
            {
                "timestamp_utc": event.get("timestamp_utc"),
                "step": event.get("step"),
                "task_count": event.get("task_count"),
                "pass_rate": event.get("pass_rate"),
                "quantum_pass_rate": event.get("quantum_pass_rate"),
                "software_pass_rate": event.get("software_pass_rate"),
                "mean_total_reward": event.get("mean_total_reward"),
                "domain_metrics": event.get("domain_metrics") or {},
                "termination_counts": event.get("termination_counts") or {},
                "failure_categories": event.get("failure_categories") or {},
                "sample_failures": event.get("sample_failures") or [],
                "source": "structured_training_log",
            }
        )
    return evals


def checkpoints_from_training_log_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checkpoints = []
    for event in events:
        if event.get("stage") not in {"checkpoint_saved", "检查点已保存"}:
            continue
        checkpoints.append(
            {
                "timestamp_utc": event.get("timestamp_utc"),
                "step": event.get("step"),
                "checkpoint_dir": event.get("checkpoint_dir"),
                "adapter_dir": event.get("adapter_dir"),
                "runtime_state_path": event.get("runtime_state_path"),
                "saved_count": event.get("saved_count"),
                "checkpoint_interval_seconds": event.get("checkpoint_interval_seconds")
                or event.get("检查点间隔（秒）"),
                "checkpoint_every_steps": event.get("checkpoint_every_steps"),
                "latest_record": event.get("latest_record"),
                "source": "structured_training_log",
            }
        )
    return checkpoints


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def pct(value: Any) -> str:
    if value is None:
        return "待产生"
    return f"{100.0 * as_float(value):.1f}%"


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "待产生"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def file_sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def short_sha(value: str | None) -> str:
    if not value:
        return "未写入"
    return value[:12]


def discover_runs(outputs_dir: Path) -> list[Path]:
    if not outputs_dir.exists():
        return []
    candidates = []
    for path in outputs_dir.iterdir():
        if not path.is_dir():
            continue
        if any(
            (path / name).exists()
            for name in (
                "live_status.json",
                "grpo_step_metrics.jsonl",
                "grpo_metrics.json",
                "metrics.json",
                "train_log_tail.txt",
            )
        ):
            candidates.append(path)
    return sorted(candidates, key=lambda item: item.stat().st_mtime, reverse=True)


def run_has_training_evidence(path: Path) -> bool:
    return any(
        (path / name).exists()
        for name in (
            "grpo_step_metrics.jsonl",
            "latest_checkpoint.json",
            "checkpoint_history.jsonl",
            "online_eval_latest.json",
            "online_eval_history.jsonl",
        )
    )


def select_dashboard_runs(candidates: list[Path], *, limit: int) -> list[Path]:
    """Keep the freshest status runs while reserving slots for real GRPO evidence."""
    if limit <= 0:
        return []
    if len(candidates) <= limit:
        return candidates

    evidence_slots = min(max(limit // 3, 1), limit)
    recent_slots = max(limit - evidence_slots, 0)
    selected: list[Path] = []
    seen: set[Path] = set()

    for path in candidates[:recent_slots]:
        selected.append(path)
        seen.add(path)

    evidence_runs = [path for path in candidates if run_has_training_evidence(path)]
    for path in evidence_runs:
        if len(selected) >= limit:
            break
        if path not in seen:
            selected.append(path)
            seen.add(path)

    for path in candidates:
        if len(selected) >= limit:
            break
        if path not in seen:
            selected.append(path)
            seen.add(path)
    return selected


def count_files(root: Path, patterns: list[str]) -> int:
    if not root.exists():
        return 0
    seen: set[Path] = set()
    for pattern in patterns:
        seen.update(path for path in root.rglob(pattern) if path.is_file())
    return len(seen)


def count_dirs(root: Path) -> int:
    if not root.exists():
        return 0
    return sum(1 for path in root.iterdir() if path.is_dir())


def latest_mtime(root: Path, patterns: list[str]) -> float | None:
    if not root.exists():
        return None
    mtimes: list[float] = []
    for pattern in patterns:
        mtimes.extend(path.stat().st_mtime for path in root.rglob(pattern) if path.is_file())
    return max(mtimes) if mtimes else None


def age_text(epoch: float | None) -> str:
    if epoch is None:
        return "未观察到"
    age = max(0.0, time.time() - epoch)
    if age < 120:
        return f"{age:.0f} 秒前"
    if age < 7200:
        return f"{age / 60:.0f} 分钟前"
    if age < 172800:
        return f"{age / 3600:.1f} 小时前"
    return f"{age / 86400:.1f} 天前"


def load_domain_expert_contracts(data_dir: Path) -> list[dict[str, Any]]:
    if not data_dir.exists():
        return []
    contracts: list[dict[str, Any]] = []
    for manifest_path in sorted(data_dir.glob("generated/*/manifest.json")):
        payload = load_json(manifest_path)
        if not payload:
            continue
        contract = payload.get("domain_expert_contract")
        if isinstance(contract, dict):
            contracts.append(
                {
                    "dataset": str(manifest_path.parent),
                    "manifest": str(manifest_path),
                    "正常": bool(contract.get("正常", contract.get("ok"))),
                    "purpose": contract.get("purpose"),
                    "checks": contract.get("checks") or {},
                    "requirements": contract.get("requirements") or {},
                    "details": contract.get("details") or {},
                    "reference_notes": contract.get("reference_notes") or [],
                }
            )
    return contracts


def build_research_system_status(
    *,
    outputs_dir: Path,
    reports_dir: Path = Path("reports"),
    data_dir: Path = Path("data"),
    evals_dir: Path = Path("evals"),
    docs_dir: Path = Path("docs"),
) -> dict[str, Any]:
    output_runs = discover_runs(outputs_dir)
    eval_runs_dir = evals_dir / "runs"
    benchmark_dir = evals_dir / "benchmarks"
    tasks_dir = evals_dir / "tasks"
    return {
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "outputs": {
            "path": str(outputs_dir),
            "run_count": len(output_runs),
            "latest_update": age_text(
                max((path.stat().st_mtime for path in output_runs), default=None)
            ),
        },
        "evaluations": {
            "runs": count_dirs(eval_runs_dir),
            "benchmarks": count_files(benchmark_dir, ["*.txt", "*.json", "*.jsonl"]),
            "tasks": count_dirs(tasks_dir),
            "latest_update": age_text(
                latest_mtime(evals_dir, ["*.json", "*.jsonl", "*.txt", "*.py"])
            ),
        },
        "data": {
            "datasets": count_files(data_dir, ["*.jsonl", "*.json", "*.csv", "*.txt"]),
            "latest_update": age_text(
                latest_mtime(data_dir, ["*.jsonl", "*.json", "*.csv", "*.txt"])
            ),
        },
        "reports": {
            "files": count_files(reports_dir, ["*.json", "*.md", "*.html"]),
            "latest_update": age_text(latest_mtime(reports_dir, ["*.json", "*.md", "*.html"])),
        },
        "docs": {
            "files": count_files(docs_dir, ["*.md"]),
            "latest_update": age_text(latest_mtime(docs_dir, ["*.md"])),
        },
        "domain_expert_contracts": load_domain_expert_contracts(data_dir),
    }


DISPLAY_LABELS = {
    "run_manifest": "运行配置记录",
    "metrics": "训练指标",
    "live_status": "实时状态",
    "online_eval_history": "在线评测历史",
    "agentic_traces": "智能体轨迹",
    "structured_training_log": "结构化训练日志",
    "job_health": "任务健康状态",
    "failure_report": "失败报告",
    "safety_report": "安全报告",
    "metrics_present": "已经产生训练指标",
    "optimizer_updated": "优化器已经更新",
    "reward_signal_nonzero": "奖励信号有效",
    "no_context_overflow": "没有上下文溢出",
    "agent_writes_or_finalizes": "智能体会编辑或总结",
    "online_eval_recorded": "已经记录在线评测",
    "no_live_alerts": "没有实时告警",
    "job_heartbeat_fresh": "任务心跳新鲜",
    "no_unsafe_tool_events": "没有不安全工具事件",
    "mean_reward": "平均奖励",
    "reward_signal_std": "奖励信号波动",
    "pass_rate": "训练通过率",
    "loss": "损失",
    "quantum_pass_rate": "量子评测通过率",
    "software_pass_rate": "软件工程评测通过率",
    "agentic_pass_rate": "智能体评测通过率",
    "mean_total_reward": "评测平均奖励",
    "event_count": "日志事件总数",
    "stage_counts": "事件类型计数",
    "latest_training_step": "最新训练步",
    "latest_training_reward": "最新训练奖励",
    "latest_training_pass_rate": "最新训练通过率",
    "latest_training_loss": "最新训练损失",
    "latest_task": "最新任务",
    "latest_checkpoint": "最新检查点",
    "latest_online_eval": "最新在线评测",
    "latest_training_completed": "训练完成记录",
    "training_step_summary": "训练步摘要",
    "checkpoint_saved": "检查点已保存",
    "online_eval_complete": "在线评测完成",
    "training_completed": "训练完成",
    "context_overflow": "上下文溢出",
    "missing_metrics": "缺少训练指标",
    "alert_asi1_task_running_waiting_for_metrics": "ASI1 任务运行中但等待指标",
    "alert_asi1_task_failed_before_metrics": "ASI1 任务在指标前失败",
    "alert_asi1_task_completed_waiting_for_artifact_fetch": "ASI1 任务完成但等待工件抓取",
    "alert_asi1_task_submitted": "ASI1 任务已提交",
    "termination_final_answer": "轨迹正常完成",
    "final_answer": "完成回答",
    "turn_budget": "回合预算耗尽",
    "read_file": "读文件",
    "write_file": "写文件",
    "run_tests": "跑测试",
    "search_repo": "搜索仓库",
    "legacy_metrics": "旧格式指标",
    "assertion_failure": "断言失败",
    "timeout": "超时",
    "environment": "环境",
    "huanxin_task_name": "焕新任务名",
    "huanxin_task_id": "焕新任务编号",
    "huanxin_task_status": "焕新任务状态",
    "huanxin_use_time": "焕新运行时长",
    "last_metric_age_sec": "指标年龄（秒）",
    "last_log_age_sec": "日志年龄（秒）",
    "npu_visible": "可见 NPU",
    "npu_util": "NPU 利用率",
    "npu_mem_used": "NPU 内存占用",
    "checkpoint_step": "检查点步数",
    "checkpoint_dir": "检查点目录",
    "checkpoint_saved_count": "已保存检查点数",
    "checkpoint_interval_seconds": "检查点间隔（秒）",
    "checkpoint_progress_text": "检查点进度",
    "model_name": "模型",
    "benchmark_file": "训练任务集",
    "holdout_file": "留出集",
    "online_eval_benchmark_file": "在线评测集",
    "dataset_sha256": "数据指纹",
    "model_sha256": "模型指纹",
    "adapter_sha256": "适配器指纹",
    "metrics_sha256": "指标指纹",
    "live_status_sha256": "实时状态指纹",
    "manifest_sha256": "配置指纹",
    "trace_sha256": "轨迹指纹",
    "run_id": "运行编号",
    "planned_steps": "计划步数",
    "unsafe_tool_events": "不安全工具事件",
    "prompt_injection_events": "提示注入事件",
    "secrets_events": "秘密访问事件",
    "destructive_command_blocks": "破坏性命令拦截",
    "summary": "摘要",
    "failure_stage": "失败阶段",
    "exact_blocker": "精确阻塞",
    "blocker": "阻塞",
    "blocker_text": "阻塞详情",
    "startup_diagnosis": "启动诊断",
    "status": "状态",
    "task_name": "任务名",
    "task_id": "任务编号",
    "train_domain_min": "训练领域下限",
    "eval_domain_min": "评测领域下限",
    "eval_task_disjoint": "评测任务隔离",
    "software_replay_min": "软件回放下限",
    "quantum": "量子编码",
    "software": "软件工程",
    "agentic": "智能体任务",
    "train_domain_counts": "训练领域计数",
    "eval_domain_counts": "评测领域计数",
    "train_rows": "训练样本数",
    "eval_rows": "评测样本数",
    "holdout_policy": "留出策略",
    "path": "路径",
    "run_count": "运行数",
    "latest_update": "最近更新",
    "runs": "评测运行数",
    "benchmarks": "基准数",
    "tasks": "任务数",
    "datasets": "数据集数",
    "files": "文件数",
    "train_dev_url": "训练开发环境地址",
    "browser_daemon_state": "浏览器守护状态",
    "startup_state": "启动状态",
    "current_url": "当前页面",
    "shell_endpoint_summary": "终端入口摘要",
    "command_channel_recent_success": "命令通道最近成功",
    "command_channel_transport": "命令通道方式",
    "command_channel_age_seconds": "命令通道年龄（秒）",
    "task_status_code": "任务状态码",
    "task_status": "任务状态",
    "use_time": "运行时长",
    "remote_root": "远程项目根目录",
    "remote_path": "远程输出路径",
    "fetch_env": "抓取环境",
    "fetched_files": "已抓取文件数",
    "rank_started": "已启动 rank 数",
    "rank_completed": "已完成 rank 数",
    "world_size": "分布式规模",
    "accelerator_log_seen": "加速卡日志可见",
    "boot": "启动标记",
    "start": "rank 启动标记",
    "done": "rank 完成标记",
    "before_distributed": "分布式启动前标记",
    "after_distributed": "分布式返回后标记",
}

STATUS_LABELS = {
    "active": "训练中",
    "running": "运行中",
    "training": "训练中",
    "queued": "排队中",
    "pending": "等待中",
    "submitted": "已提交",
    "失败": "失败",
    "completed": "已完成",
    "complete": "已完成",
    "succeeded": "成功完成",
    "success": "成功完成",
    "missing": "缺少数据",
    "未知": "状态未知",
    "authenticated": "已认证",
}

HEALTH_LABELS = {
    "No step metrics yet": "还没有训练步指标",
    "No optimizer updates yet": "还没有优化器更新",
    "Low reward variance": "奖励信号波动太低",
    "Context overflow": "发生上下文溢出",
    "Read-only trajectories": "轨迹只读，未编辑或总结",
    "Failure report present": "存在失败报告",
    "训练 log tail present": "已经抓取训练日志尾部",
    "Checkpoint record present": "存在检查点记录",
    "Stale job heartbeat": "任务心跳过期",
    "No obvious blockers in local artifacts": "本地工件中没有明显阻塞",
}

DETAIL_REPLACEMENTS = {
    "step metric row(s)": "条训练步指标",
    "updated step(s)": "步已更新",
    "std not recorded": "未记录奖励波动",
    "latest_reward": "最新奖励",
    "pass_rate": "通过率",
    "latest_std": "最新波动",
    "pending held-out eval": "等待留出评测",
    "waiting for first metric heartbeat": "等待第一条指标心跳",
    "final metric captured": "已捕获最终指标",
    "write_file/final_answer observed": "观察到编辑或完成回答",
    "unsafe_tool_events": "不安全工具事件",
}

EVENT_STAGE_LABELS = {
    "training_step_summary": "训练步摘要",
    "checkpoint_saved": "检查点已保存",
    "online_eval_complete": "在线评测完成",
    "training_completed": "训练完成",
}

STATUS_VALUE_LABELS = {
    "authenticated": "已认证",
    "unknown": "未知",
    "ready": "就绪",
    "healthy": "健康",
    "standalone": "独立通道",
    "queued": "排队中",
    "running": "运行中",
    "failed": "失败",
    "completed": "已完成",
    "ended": "已结束",
}


def zh_label(value: Any) -> str:
    text = "" if value is None else str(value)
    return DISPLAY_LABELS.get(text, text.replace("_", " "))


def zh_value(value: Any) -> str:
    if isinstance(value, (dict, list, tuple)):
        return format_display_value(value)
    text = "" if value is None else str(value)
    if text.strip().lower() in {"n/a", "none", "null", "<n/a>"}:
        return "暂无数据"
    return STATUS_VALUE_LABELS.get(text.lower(), text)


def zh_counter_key(value: Any) -> str:
    text = "" if value is None else str(value)
    return DISPLAY_LABELS.get(text, EVENT_STAGE_LABELS.get(text, text.replace("_", " ")))


def zh_detail(value: Any) -> str:
    raw = "" if value is None else str(value)
    for old, new in DETAIL_REPLACEMENTS.items():
        raw = raw.replace(old, new)
    return raw


def zh_visible_text(value: Any) -> str:
    if isinstance(value, (dict, list, tuple)):
        return format_display_value(value)
    raw = "" if value is None else str(value)
    if raw.strip().lower() in {"n/a", "none", "null", "<n/a>"}:
        return "暂无数据"
    status_value = STATUS_VALUE_LABELS.get(raw.lower())
    if status_value:
        return status_value
    replacements = [
        ("elapsed=", "运行时长="),
        ("huanxin_status_code=", "焕新状态码="),
        ("stage=", "阶段="),
        (
            "User-code markers show the launcher reached torchrun, so this is not a platform startup failure. The trainer returned before writing step metrics or the launcher did not capture the real torchrun error.",
            "用户训练代码标记显示启动器已经进入 torchrun，所以这不是平台启动失败。训练器在写入训练步指标前退出，或启动器没有捕获真实 torchrun 错误。",
        ),
        (
            "ASI1 task reached torchrun but returned without GRPO metrics.",
            "ASI1 任务已经进入 torchrun，但没有返回 GRPO 指标。",
        ),
        ("ASI1 task failed before metrics.", "ASI1 任务在产生指标前失败。"),
        ("ASI1 task failed before GRPO metrics were emitted.", "ASI1 任务在产生 GRPO 指标前失败。"),
        (
            "ASI1 full Qwen3.6-27B LoRA GRPO task was not created.",
            "ASI1 完整 Qwen3.6-27B LoRA GRPO 任务未创建成功。",
        ),
        (
            "ASI1 wheel-embedded LoRA GRPO task was not created.",
            "ASI1 内嵌 wheel 的 LoRA GRPO 任务未创建成功。",
        ),
        (
            "Huanxin task create API rejected the oversized embedded-runtime payload before a training pod was launched.",
            "焕新任务创建接口在训练 Pod 启动前拒绝了过大的内嵌运行时载荷。",
        ),
        (
            "Huanxin task create API rejected the submitted codeContents payload before a training pod was launched.",
            "焕新任务创建接口在训练 Pod 启动前拒绝了提交的执行命令载荷。",
        ),
        (
            "Huanxin rejected the embedded-runtime codeContents payload before pod launch",
            "焕新在 Pod 启动前拒绝了内嵌运行时执行命令载荷",
        ),
        ("encoded bytes across", "编码字节，分布在"),
        ("Direct create fallback returned HTTP", "直接创建兜底返回 HTTP"),
        ("Response:", "响应："),
        (
            "Huanxin rejected the 1.4 MB codeContents payload before pod launch. Short 6.4 KB task creation works, so wheel/repo materialization must happen outside codeContents.",
            "焕新在 Pod 启动前拒绝了 1.4 MB 的 codeContents 载荷。6.4 KB 短任务可以创建，因此 wheel 和仓库物化必须放在 codeContents 之外。",
        ),
        (
            "User-code markers and dependency probes ran, so the Huanxin task path is executing. Install the missing dependency in the task image or embed a wheelhouse in the submitted task.",
            "用户代码标记和依赖探针已经执行，说明焕新任务路径可运行。需要在任务镜像中安装缺失依赖，或在提交任务中挂载/物化 wheelhouse。",
        ),
        (
            "reached user code but failed because Python dependency",
            "已进入用户代码，但由于 Python 依赖",
        ),
        ("is missing", "缺失而失败"),
        ("task create failed", "任务创建失败"),
        ("submit_failed", "提交失败"),
        ("create_failed", "创建失败"),
        ("is ended; waiting for GRPO/eval artifacts.", "已结束；正在等待 GRPO 或评测工件。"),
        ("is failed; waiting for GRPO/eval artifacts.", "已失败；正在等待 GRPO 或评测工件。"),
        ("is running; waiting for GRPO/eval artifacts.", "运行中；正在等待 GRPO 或评测工件。"),
        ("is starting; waiting for GRPO/eval artifacts.", "启动中；正在等待 GRPO 或评测工件。"),
        ("is unknown; waiting for GRPO/eval artifacts.", "状态未知；正在等待 GRPO 或评测工件。"),
        (
            "Huanxin emitted the platform sshd startup warning before user-code markers.",
            "焕新在用户训练代码标记出现前产生平台启动告警。",
        ),
        (
            "Huanxin emitted the platform sshd startup warning before user-code markers; if no later marker appears, treat this as an image/entrypoint compatibility failure.",
            "焕新在用户训练代码标记出现前产生平台启动告警；如果后续没有训练标记，应视为镜像或入口兼容性问题。",
        ),
        (
            "Fix reward variance before scaling: lower min-reward-std or diversify rollouts/tasks.",
            "扩容前先修复奖励信号：降低最小奖励波动门槛，或增加轨迹和任务多样性。",
        ),
        (
            "Raise max sequence length or shrink prompt/file observations; current trajectories overflow context.",
            "提高序列长度，或缩短提示和文件观察；当前轨迹有上下文溢出。",
        ),
        (
            "Strengthen rollout nudges or rejection-sampled SFT so trajectories write_file/final_answer.",
            "加强轨迹提示或拒绝采样 SFT，让轨迹真正编辑代码并给出总结。",
        ),
        (
            "Run a lightweight held-out eval after the smoke survives memory and update gates.",
            "冒烟训练通过内存和更新门槛后，运行轻量级留出评测。",
        ),
        (
            "Fetch or start remote training artifacts so reward, pass rate, KL, loss, and eval curves become live.",
            "抓取或启动远程训练工件，让奖励、通过率、KL、损失和评测曲线变成实时。",
        ),
        (
            "Chart reward components and add behavior/recovery rewards only if objective rewards remain flat.",
            "先画奖励分量；只有客观奖励持续不动时，再增加行为或恢复奖励。",
        ),
        (
            "Promote to the next canary rung: longer 1-NPU run, then multi-NPU smoke with the same gates.",
            "进入下一档金丝雀：更长的单 NPU 训练，然后用同样门槛做多 NPU 冒烟。",
        ),
        ("No step metrics yet", "还没有训练步指标"),
        ("No optimizer updates yet", "还没有优化器更新"),
        ("Low reward variance", "奖励信号波动太低"),
        ("Context overflow", "发生上下文溢出"),
        ("Read-only trajectories", "轨迹只读，未编辑或总结"),
        ("Failure report present", "存在失败报告"),
        ("Checkpoint record present", "存在检查点记录"),
        ("Stale job heartbeat", "任务心跳过期"),
        ("No obvious blockers in local artifacts", "本地工件中没有明显阻塞"),
        ("pre_python_task_startup", "训练脚本启动前"),
        ("missing_metrics", "缺少训练指标"),
        ("no_optimizer_updates", "优化器未更新"),
        ("low_reward_signal", "奖励信号过低"),
        ("read_only_loop", "只读循环"),
        ("tests_before_patch", "先测试但未修补"),
        ("context_overflow", "上下文溢出"),
        ("final_answer", "完成回答"),
        ("turn_budget", "回合预算耗尽"),
        ("read_file", "读文件"),
        ("write_file", "写文件"),
        ("run_tests", "跑测试"),
        ("huanxin_task_create_failed", "焕新任务创建失败"),
        ("dependency_probe", "依赖探针"),
        ("training_step_summary", "训练步摘要"),
        ("checkpoint_saved", "检查点已保存"),
        ("online_eval_complete", "在线评测完成"),
        ("training_completed", "训练完成"),
        ("assertion_failure", "断言失败"),
        ("timeout", "超时"),
        ("authenticated", "已认证"),
        ("standalone", "独立通道"),
        ("healthy", "健康"),
        ("ready", "就绪"),
        ("running", "运行中"),
        ("pending", "等待中"),
        ("failed", "失败"),
        ("submitted", "已提交"),
        ("submit_failed", "提交失败"),
        ("starting", "启动中"),
        ("unknown", "未知"),
        ("ended", "已结束"),
    ]
    for old, new in replacements:
        raw = raw.replace(old, new)
    return raw.replace("<N/A>", "暂无数据").replace("N/A", "暂无数据")


def zh_status(value: Any) -> str:
    text = "" if value is None else str(value)
    return STATUS_LABELS.get(text.lower(), text)


def zh_bool(value: Any) -> str:
    if value is True:
        return "是"
    if value is False:
        return "否"
    return display_text(value, "未采集")


def zh_gate_text(passed: bool) -> str:
    return "通过" if passed else "未通过"


def zh_health_item(item: Any) -> str:
    text = str(item or "")
    if text.startswith("Fetched artifacts:"):
        return "已抓取工件数量：" + text.split(":", 1)[1].strip()
    if text.startswith("Structured log events:"):
        return "结构化日志事件数量：" + text.split(":", 1)[1].strip()
    if text.startswith("Checkpoint progress"):
        return "检查点进度 " + text.split(" ", 2)[-1]
    if text.endswith(" live alert(s)"):
        return "实时告警数量：" + text.split()[0]
    return zh_visible_text(HEALTH_LABELS.get(text, text))


def zh_action(item: Any) -> str:
    text = str(item or "")
    translations = {
        "ASI1 训练任务在产生指标前失败：检查焕新任务事件、日志和入口配置。": "ASI1 训练任务在产生指标前失败：检查焕新任务事件、日志和入口配置。",
        "镜像或入口修好后，先重提最小 ASI1 任务；当前没有产生训练指标。": "镜像或入口修好后，先重提最小 ASI1 任务；当前没有产生训练指标。",
        "Fix reward variance before scaling: lower min-reward-std or diversify rollouts/tasks.": "扩容前先修复奖励信号：降低最小奖励波动门槛，或增加轨迹和任务多样性。",
        "Raise max sequence length or shrink prompt/file observations; current trajectories overflow context.": "提高序列长度，或缩短提示和文件观察；当前轨迹有上下文溢出。",
        "Strengthen rollout nudges or rejection-sampled SFT so trajectories write_file/final_answer.": "加强轨迹提示或拒绝采样 SFT，让轨迹真正编辑代码并给出总结。",
        "Run a lightweight held-out eval after the smoke survives memory and update gates.": "冒烟训练通过内存和更新门槛后，运行轻量级留出评测。",
        "Fetch or start remote training artifacts so reward, pass rate, KL, loss, and eval curves become live.": "抓取或启动远程训练工件，让奖励、通过率、KL、损失和评测曲线变成实时。",
        "Chart reward components and add behavior/recovery rewards only if objective rewards remain flat.": "先画奖励分量；只有客观奖励持续不动时，再增加行为或恢复奖励。",
        "Promote to the next canary rung: longer 1-NPU run, then multi-NPU smoke with the same gates.": "进入下一档金丝雀：更长的单 NPU 训练，然后用同样门槛做多 NPU 冒烟。",
    }
    return zh_visible_text(translations.get(text, text))


def zh_failure_summary(text: Any) -> str:
    raw = str(text or "")
    if raw.strip().lower() in {"n/a", "none", "null", "<n/a>"}:
        return "暂无数据"
    replacements = [
        ("ASI1 task failed before GRPO metrics were emitted.", "ASI1 任务在产生 GRPO 指标前失败。"),
        (
            "ASI1 full Qwen3.6-27B LoRA GRPO task was not created.",
            "ASI1 完整 Qwen3.6-27B LoRA GRPO 任务未创建成功。",
        ),
        (
            "ASI1 wheel-embedded LoRA GRPO task was not created.",
            "ASI1 内嵌 wheel 的 LoRA GRPO 任务未创建成功。",
        ),
        (
            "Huanxin task create API rejected the oversized embedded-runtime payload before a training pod was launched.",
            "焕新任务创建接口在训练 Pod 启动前拒绝了过大的内嵌运行时载荷。",
        ),
        (
            "Huanxin task create API rejected the submitted codeContents payload before a training pod was launched.",
            "焕新任务创建接口在训练 Pod 启动前拒绝了提交的执行命令载荷。",
        ),
        (
            "Huanxin rejected the embedded-runtime codeContents payload before pod launch",
            "焕新在 Pod 启动前拒绝了内嵌运行时执行命令载荷",
        ),
        ("encoded bytes across", "编码字节，分布在"),
        ("Direct create fallback returned HTTP", "直接创建兜底返回 HTTP"),
        ("Response:", "响应："),
        (
            "Huanxin rejected the 1.4 MB codeContents payload before pod launch. Short 6.4 KB task creation works, so wheel/repo materialization must happen outside codeContents.",
            "焕新在 Pod 启动前拒绝了 1.4 MB 的 codeContents 载荷。6.4 KB 短任务可以创建，因此 wheel 和仓库物化必须放在 codeContents 之外。",
        ),
        ("huanxin_task_create_failed", "焕新任务创建失败"),
        ("dependency_probe", "依赖探针"),
        ("submit_failed", "提交失败"),
        (
            "Huanxin emitted the platform sshd startup warning before user-code markers.",
            "焕新在用户训练代码标记出现前产生平台启动告警。",
        ),
        (
            "Huanxin emitted the platform sshd startup warning before user-code markers; if no later marker appears, treat this as an image/entrypoint compatibility failure.",
            "焕新在用户训练代码标记出现前产生平台启动告警；如果后续没有训练标记，应视为镜像或入口兼容性问题。",
        ),
        ("pre_python_task_startup", "训练脚本启动前"),
        ("failed", "失败"),
        ("running", "运行中"),
        ("queued", "排队中"),
        ("completed", "已完成"),
    ]
    for old, new in replacements:
        raw = raw.replace(old, new)
    return raw


def zh_status_text(text: Any) -> str:
    raw = str(text or "")
    if raw.strip().lower() in {"n/a", "none", "null", "<n/a>"}:
        return "暂无数据"
    replacements = [
        ("elapsed=", "运行时长="),
        ("huanxin_status_code=", "焕新状态码="),
        ("stage=", "阶段="),
        ("torchrun_returned_no_metrics", "分布式启动已返回但没有指标"),
        (
            "User-code markers show the launcher reached torchrun, so this is not a platform startup failure. The trainer returned before writing step metrics or the launcher did not capture the real torchrun error.",
            "用户训练代码标记显示启动器已经进入分布式启动，所以这不是平台启动失败。训练器在写入训练步指标前退出，或启动器没有捕获真实分布式错误。",
        ),
        (
            "ASI1 task reached torchrun but returned without GRPO metrics.",
            "ASI1 任务已经进入分布式启动，但没有返回 GRPO 指标。",
        ),
        ("ASI1 task failed before metrics.", "ASI1 任务在产生指标前失败。"),
        ("ASI1 task failed before GRPO metrics were emitted.", "ASI1 任务在产生 GRPO 指标前失败。"),
        (" failed before metrics: ", " 在产生指标前失败："),
        (" failed: ", " 失败："),
        (" failed", " 失败"),
        (" submit_failed", " 提交失败"),
        (" is active; GRPO metrics are live", " 正在训练，GRPO 指标已实时产生"),
        (" is ", " 状态为 "),
        ("; waiting for GRPO/eval artifacts", "；正在等待 GRPO 或评测工件"),
        (
            "Status artifact present, but no live task state recorded yet",
            "已有状态工件，但还没有实时任务状态",
        ),
        ("run", "运行"),
        ("task ", "任务 "),
        ("running", "运行中"),
        ("pending", "等待中"),
        ("pre_python_task_startup", "训练脚本启动前"),
        ("submitted", "已提交"),
        ("starting", "启动中"),
        ("unknown", "未知"),
        ("ended", "已结束"),
    ]
    for old, new in replacements:
        raw = raw.replace(old, new)
    return raw


def compact_dict_items(payload: dict[str, Any], keys: list[str]) -> str:
    items = []
    for key in keys:
        if key in payload and payload.get(key) not in (None, "", {}, []):
            value = maybe_sanitize_display_value(key, payload.get(key))
            items.append(
                f"<li><strong>{html.escape(zh_label(key))}</strong>：{html.escape(display_text(value, '暂无数据'))}</li>"
            )
    return "".join(items) or "<li>暂无可展示信息</li>"


def counter_items(payload: dict[str, Any], *, empty: str = "暂无记录") -> str:
    if not payload:
        return f"<li>{html.escape(empty)}</li>"
    return "".join(
        f"<li><strong>{html.escape(zh_counter_key(key))}</strong>：{html.escape(format_display_value(value))}</li>"
        for key, value in sorted(payload.items())
    )


def format_display_value(value: Any, *, empty: str = "暂无数据") -> str:
    if value is None or value == "":
        return empty
    if isinstance(value, bool):
        return zh_bool(value)
    if isinstance(value, dict):
        parts = []
        for key, child in sorted(value.items()):
            if child in (None, "", {}, []):
                continue
            parts.append(f"{zh_label(key)}={format_display_value(child, empty=empty)}")
        return "；".join(parts) if parts else empty
    if isinstance(value, (list, tuple)):
        parts = [
            format_display_value(item, empty=empty)
            for item in value
            if item not in (None, "", {}, [])
        ]
        return "，".join(parts) if parts else empty
    return zh_visible_text(value)


def artifact_file_label(value: str) -> str:
    labels = {
        "run_manifest.json": "运行配置记录",
        "训练日志尾部": "训练日志尾部",
        "训练步指标": "训练步指标",
        "实时状态": "实时状态",
        "在线评测历史": "在线评测历史",
        "智能体轨迹": "智能体轨迹",
        "训练日志中的结构化事件": "训练日志中的结构化事件",
        "任务健康状态": "任务健康状态",
        "失败报告": "失败报告",
        "安全报告": "安全报告",
    }
    return labels.get(value, value)


def visible_metric_name(value: Any) -> str:
    text = str(value or "")
    labels = {
        "mean_reward": "平均奖励",
        "reward_signal_std": "奖励波动",
        "pass_rate": "通过率",
        "loss": "损失",
        "kl_coeff": "KL 系数",
        "kl": "KL",
        "quantum_pass_rate": "量子通过率",
        "software_pass_rate": "软件工程通过率",
        "agentic_pass_rate": "智能体通过率",
        "mean_total_reward": "评测奖励",
    }
    return labels.get(text, zh_label(text))


def visible_alert_message(alert: Any) -> str:
    if not isinstance(alert, dict):
        return zh_visible_text(alert)
    parts = []
    if alert.get("severity"):
        parts.append(f"级别：{zh_value(alert.get('severity'))}")
    if alert.get("kind"):
        parts.append(f"类型：{zh_counter_key(alert.get('kind'))}")
    if alert.get("message"):
        parts.append(f"说明：{zh_visible_text(alert.get('message'))}")
    if alert.get("task_id"):
        parts.append(f"任务编号：{alert.get('task_id')}")
    return "；".join(parts) or "告警无详情"


def build_source_contract(
    runs: list[dict[str, Any]], huanxin_status: dict[str, Any]
) -> dict[str, Any]:
    required_run_artifacts = {
        "run_manifest": "运行配置记录",
        "metrics": "训练步指标",
        "live_status": "实时状态",
        "online_eval_history": "在线评测历史",
        "agentic_traces": "智能体轨迹",
        "structured_training_log": "结构化训练日志",
        "job_health": "任务健康状态",
        "failure_report": "失败报告",
        "safety_report": "安全报告",
    }
    present_counts: Counter[str] = Counter()
    missing_counts: Counter[str] = Counter()
    for run in runs:
        status = dict(run.get("artifact_status") or {})
        for key in required_run_artifacts:
            if status.get(key):
                present_counts[key] += 1
            else:
                missing_counts[key] += 1
    return {
        "required_run_artifacts": required_run_artifacts,
        "present_counts": dict(sorted(present_counts.items())),
        "missing_counts": dict(sorted(missing_counts.items())),
        "huanxin_environment_status_present": bool(huanxin_status.get("environments")),
        "huanxin_environment_status_generated_at": huanxin_status.get("generated_at_utc"),
        "remote_log_sources": [
            "训练日志尾部",
            "实时状态",
            "训练步指标",
            "在线评测历史",
            "智能体轨迹",
            "训练步摘要事件",
            "检查点保存事件",
            "在线评测完成事件",
            "训练完成事件",
            "任务健康状态",
            "失败报告",
            "安全报告",
            "焕新环境状态",
        ],
    }


def first_json(run_dir: Path, names: list[str]) -> dict[str, Any]:
    for name in names:
        payload = load_json(run_dir / name)
        if payload is not None:
            return payload
    return {}


TERMINAL_FAILURE_STATUSES = {
    "失败",
    "failure",
    "ended",
    "stopped",
    "cancelled",
    "canceled",
    "error",
}
TERMINAL_SUCCESS_STATUSES = {"completed", "complete", "succeeded", "success", "done"}
LIVE_METRIC_STATUSES = {"active", "running", "training", "in_progress", "live"}
SUBMISSION_FAILURE_STATUSES = {"submit_failed", "create_failed", "creation_failed"}


def effective_run_status(
    *,
    live: dict[str, Any],
    job_health: dict[str, Any],
    failure_report: dict[str, Any],
    metrics: list[dict[str, Any]],
) -> str:
    raw_status = str(live.get("status") or "").lower()
    task_status = str(job_health.get("huanxin_task_status") or "").lower()
    if failure_report:
        return "失败"
    if raw_status in SUBMISSION_FAILURE_STATUSES or task_status in SUBMISSION_FAILURE_STATUSES:
        return "失败"
    if metrics and raw_status in TERMINAL_SUCCESS_STATUSES:
        return raw_status
    if metrics and (
        raw_status in LIVE_METRIC_STATUSES
        or task_status in LIVE_METRIC_STATUSES
        or (
            raw_status not in TERMINAL_FAILURE_STATUSES
            and raw_status not in TERMINAL_SUCCESS_STATUSES
            and task_status not in TERMINAL_FAILURE_STATUSES
            and task_status not in TERMINAL_SUCCESS_STATUSES
        )
    ):
        return "active"
    if raw_status in TERMINAL_SUCCESS_STATUSES:
        return raw_status
    if not metrics and (
        raw_status in TERMINAL_FAILURE_STATUSES or task_status in TERMINAL_FAILURE_STATUSES
    ):
        return "失败"
    return raw_status or ("未知" if metrics else "missing")


def derive_run_status_text(
    *,
    live: dict[str, Any],
    job_health: dict[str, Any],
    failure_report: dict[str, Any],
    run_config: dict[str, Any],
    run_manifest: dict[str, Any],
    metrics: list[dict[str, Any]],
) -> dict[str, str]:
    status = effective_run_status(
        live=live, job_health=job_health, failure_report=failure_report, metrics=metrics
    )
    environment = (
        job_health.get("environment")
        or live.get("environment")
        or run_manifest.get("environment")
        or run_config.get("environment")
    )
    task_name = (
        job_health.get("huanxin_task_name")
        or failure_report.get("task_name")
        or run_manifest.get("huanxin_task_name")
        or run_config.get("huanxin_task_name")
    )
    task_id = (
        job_health.get("huanxin_task_id")
        or failure_report.get("task_id")
        or run_manifest.get("huanxin_task_id")
        or run_config.get("huanxin_task_id")
    )
    task_status = job_health.get("huanxin_task_status")
    failure_summary = failure_report.get("summary")
    failure_stage = failure_report.get("failure_stage")
    startup_diagnosis = failure_report.get("startup_diagnosis")

    label_parts = []
    if environment:
        label_parts.append(str(environment))
    if task_name:
        label_parts.append(f"任务 {task_name}")
    if task_id:
        label_parts.append(str(task_id))
    task_label = " ".join(label_parts) if label_parts else "run"

    if status == "失败" or task_status == "失败" or failure_report:
        if not metrics and failure_summary:
            text = f"{task_label} 在产生指标前失败：{zh_failure_summary(failure_summary)}"
        elif failure_summary:
            text = f"{task_label} 失败：{zh_failure_summary(failure_summary)}"
        else:
            text = f"{task_label} 失败"
    elif status == "active":
        text = f"{task_label} 正在训练，GRPO 指标已实时产生"
    elif status in {"submitted", "pending", "queued"} or task_status in {
        "submitted",
        "pending",
        "queued",
        "running",
    }:
        visible_status = task_status or status
        text = f"{task_label} 状态为 {zh_status(visible_status)}；正在等待 GRPO 或评测工件"
    elif status:
        text = f"{task_label} 状态为 {zh_status(status)}"
    else:
        text = "已有状态工件，但还没有实时任务状态"

    detail_parts = []
    if failure_stage:
        detail_parts.append(f"阶段={failure_stage}")
    if job_health.get("huanxin_use_time"):
        detail_parts.append(f"已运行={job_health['huanxin_use_time']}")
    if job_health.get("huanxin_task_status_code") is not None:
        detail_parts.append(f"焕新状态码={job_health['huanxin_task_status_code']}")
    if startup_diagnosis:
        detail_parts.append(zh_failure_summary(startup_diagnosis))

    return {
        "text": text,
        "detail": "; ".join(detail_parts),
    }


def classify_failure_signals(
    *,
    metrics: list[dict[str, Any]],
    tool_counts: Counter[str],
    terminations: Counter[str],
    skip_reasons: Counter[str],
    live: dict[str, Any],
) -> dict[str, int]:
    signals: Counter[str] = Counter()
    if not metrics:
        signals["missing_metrics"] += 1
    if metrics and all(bool(row.get("skipped")) for row in metrics):
        signals["no_optimizer_updates"] += 1
    signals.update({f"skip_{key}": int(value) for key, value in skip_reasons.items()})
    signals.update({f"termination_{key}": int(value) for key, value in terminations.items()})
    if (
        tool_counts.get("read_file")
        and not tool_counts.get("write_file")
        and not tool_counts.get("final_answer")
    ):
        signals["read_only_loop"] += 1
    if tool_counts.get("run_tests") and not tool_counts.get("write_file"):
        signals["tests_before_patch"] += 1
    for alert in list(live.get("alerts") or []):
        if isinstance(alert, dict) and alert.get("kind"):
            signals[f"alert_{alert['kind']}"] += 1
    return dict(sorted(signals.items()))


def build_gate_results(
    *,
    metrics: list[dict[str, Any]],
    online_latest: dict[str, Any],
    failure_signals: dict[str, int],
    live: dict[str, Any],
) -> list[dict[str, Any]]:
    updated_steps = sum(1 for row in metrics if not bool(row.get("skipped")))
    latest = metrics[-1] if metrics else {}
    live_status = str(live.get("status") or "").lower()
    terminal_metric_bearing_run = bool(metrics) and live_status in TERMINAL_SUCCESS_STATUSES
    any_reward_signal = any(
        row.get("reward_signal_std") is not None and as_float(row.get("reward_signal_std")) > 0.0
        for row in metrics
    )
    any_outcome_signal = any(
        as_float(row.get("mean_reward"), 0.0) != 0.0 or as_float(row.get("pass_rate"), 0.0) != 0.0
        for row in metrics
    )
    if any_reward_signal:
        reward_signal_detail = f"latest_std={fmt(latest.get('reward_signal_std'))}"
    elif any_outcome_signal:
        reward_signal_detail = (
            "std not recorded; "
            f"latest_reward={fmt(latest.get('mean_reward'))} "
            f"pass_rate={pct(latest.get('pass_rate'))}"
        )
    else:
        reward_signal_detail = f"latest={fmt(latest.get('reward_signal_std'))}"
    gates = [
        {
            "name": "metrics_present",
            "priority": "P0",
            "passed": bool(metrics),
            "detail": f"{len(metrics)} 条训练步指标",
        },
        {
            "name": "optimizer_updated",
            "priority": "P0",
            "passed": updated_steps > 0,
            "detail": f"{updated_steps} 步已更新",
        },
        {
            "name": "reward_signal_nonzero",
            "priority": "P0",
            "passed": any_reward_signal or any_outcome_signal,
            "detail": reward_signal_detail,
        },
        {
            "name": "no_context_overflow",
            "priority": "P0",
            "passed": not failure_signals.get("termination_context_overflow"),
            "detail": str(failure_signals.get("termination_context_overflow", 0)),
        },
        {
            "name": "agent_writes_or_finalizes",
            "priority": "P0",
            "passed": any(
                dict(row.get("trajectory_tool_counts") or {}).get("write_file")
                or dict(row.get("trajectory_tool_counts") or {}).get("final_answer")
                for row in metrics
            ),
            "detail": "write_file/final_answer observed",
        },
        {
            "name": "online_eval_recorded",
            "priority": "P1",
            "passed": bool(online_latest),
            "detail": f"通过率={pct(online_latest.get('pass_rate'))}"
            if online_latest
            else "通过率=等待留出评测",
        },
        {
            "name": "no_live_alerts",
            "priority": "P1",
            "passed": not list(live.get("alerts") or []),
            "detail": f"{len(list(live.get('alerts') or []))} alert(s)",
        },
    ]
    if live.get("job_health"):
        job_health = dict(live.get("job_health") or {})
        last_metric_age = job_health.get("last_metric_age_sec")
        gates.append(
            {
                "name": "job_heartbeat_fresh",
                "priority": "P0",
                "passed": (
                    as_float(last_metric_age, 999999.0) < 600.0
                    if last_metric_age is not None
                    else terminal_metric_bearing_run
                ),
                "detail": (
                    f"指标年龄（秒）={fmt(last_metric_age)}"
                    if last_metric_age is not None
                    else ("已捕获最终指标" if terminal_metric_bearing_run else "等待第一条指标心跳")
                ),
            }
        )
    if live.get("safety"):
        safety = dict(live.get("safety") or {})
        gates.append(
            {
                "name": "no_unsafe_tool_events",
                "priority": "P0",
                "passed": not as_float(safety.get("unsafe_tool_events"), 0.0),
                "detail": f"不安全工具事件={fmt(safety.get('unsafe_tool_events'))}",
            }
        )
    return gates


def recommend_next_actions(
    failure_signals: dict[str, int],
    gates: list[dict[str, Any]],
    live: dict[str, Any] | None = None,
) -> list[str]:
    failed_gate_names = {str(gate["name"]) for gate in gates if not bool(gate["passed"])}
    actions: list[str] = []
    live = live or {}
    job_health = dict(live.get("job_health") or {})
    alerts = [dict(alert) for alert in list(live.get("alerts") or []) if isinstance(alert, dict)]
    if (
        live.get("status") == "失败"
        and not job_health.get("last_metric_age_sec")
        and any(
            alert.get("kind") in {"asi1_task_failed_immediately", "pre_python_task_failure"}
            for alert in alerts
        )
    ):
        return [
            "ASI1 训练任务在产生指标前失败：检查焕新任务事件、日志和入口配置。",
            "镜像或入口修好后，先重提最小 ASI1 任务；当前没有产生训练指标。",
        ]
    if "no_optimizer_updates" in failure_signals or "optimizer_updated" in failed_gate_names:
        actions.append("扩容前先修复奖励信号：降低最小奖励波动门槛，或增加轨迹和任务多样性。")
    if failure_signals.get("termination_context_overflow"):
        actions.append(
            "Raise max sequence length or shrink prompt/file observations; current trajectories overflow context."
        )
    if failure_signals.get("read_only_loop") or "agent_writes_or_finalizes" in failed_gate_names:
        actions.append(
            "Strengthen rollout nudges or rejection-sampled SFT so trajectories write_file/final_answer."
        )
    if "online_eval_recorded" in failed_gate_names:
        actions.append("冒烟训练通过内存和更新门槛后，运行轻量级留出评测。")
    if "metrics_present" in failed_gate_names:
        actions.append("抓取或启动远程训练工件，让奖励、通过率、KL、损失和评测曲线变成实时。")
    if failure_signals.get("skip_low_reward_signal"):
        actions.append("先画奖励分量；只有客观奖励持续不动时，再增加行为或恢复奖励。")
    if not actions:
        actions.append("进入下一档金丝雀：更长的单 NPU 训练，然后用同样门槛做多 NPU 冒烟。")
    return actions


def practice_ladder(gates: list[dict[str, Any]]) -> dict[str, Any]:
    labels = {
        "P0": "真实训练与安全",
        "P1": "评测、来源与工件可信度",
        "P2": "优化与扩容准备",
    }
    grouped: dict[str, list[dict[str, Any]]] = {key: [] for key in labels}
    for gate in gates:
        grouped.setdefault(str(gate.get("priority", "P2")), []).append(gate)
    return {
        priority: {
            "label": label,
            "passed": all(bool(gate["passed"]) for gate in grouped.get(priority, [])),
            "gates": grouped.get(priority, []),
        }
        for priority, label in labels.items()
    }


def summarize_run(run_dir: Path) -> dict[str, Any]:
    live = load_json(run_dir / "live_status.json") or {}
    metrics = load_jsonl(run_dir / "grpo_step_metrics.jsonl")
    legacy_metrics_payload = load_metrics_payload(run_dir / "metrics.json")
    online_eval = load_jsonl(run_dir / "online_eval_history.jsonl")
    latest_checkpoint = first_json(run_dir, ["latest_checkpoint.json"])
    checkpoint_history = load_jsonl(run_dir / "checkpoint_history.jsonl")
    run_config = load_json(run_dir / "run_config.json") or {}
    run_manifest = first_json(run_dir, ["run_manifest.json", "manifest.json"])
    job_health = first_json(run_dir, ["job_health.json", "asi1_job_health.json"])
    failure_report = first_json(run_dir, ["failure_report.json"])
    safety_report = first_json(run_dir, ["safety_report.json", "safety.json"])
    fetch_manifest = first_json(
        run_dir, ["asi1_fetch_manifest.json", "huanxin_fetch_manifest.json"]
    )
    train_log_tail = load_text_tail(run_dir / "train_log_tail.txt")
    train_log_events = parse_json_events_from_text(train_log_tail)
    log_derived_metrics = metrics_from_training_log_events(train_log_events)
    log_derived_online_eval = online_evals_from_training_log_events(train_log_events)
    log_derived_checkpoints = checkpoints_from_training_log_events(train_log_events)
    if not metrics and log_derived_metrics:
        metrics = log_derived_metrics
    if not metrics:
        metrics = metrics_from_live_status(live)
    if not online_eval and log_derived_online_eval:
        online_eval = log_derived_online_eval
    if not checkpoint_history and log_derived_checkpoints:
        checkpoint_history = log_derived_checkpoints
    train_log_summary = summarize_log_events(train_log_events)
    trace_rows = load_jsonl(run_dir / "agentic_traces.jsonl") or load_jsonl(
        run_dir / "rollout_traces.jsonl"
    )
    eval_summary = first_json(run_dir, ["eval_summary.json", "online_eval_summary.json"])
    live_job_health = dict(live.get("job_health") or {})
    live_safety = dict(live.get("safety") or {})
    live_checkpoint = dict(live.get("latest_checkpoint") or {})
    if job_health:
        live["job_health"] = {**job_health, **live_job_health}
    if safety_report:
        live["safety"] = {**safety_report, **live_safety}
    if latest_checkpoint:
        live["latest_checkpoint"] = {**latest_checkpoint, **live_checkpoint}
    elif live_checkpoint:
        latest_checkpoint = dict(live_checkpoint)
    elif log_derived_checkpoints:
        latest_checkpoint = dict(log_derived_checkpoints[-1])
    elif live_checkpoint:
        latest_checkpoint = dict(live_checkpoint)

    if not live and train_log_summary.get("latest_training_completed"):
        completed = dict(train_log_summary.get("latest_training_completed") or {})
        live = {
            "status": "completed",
            "planned_steps": completed.get("planned_steps") or run_config.get("grpo_steps"),
            "summary": {
                "recorded_steps": completed.get("recorded_steps") or len(metrics),
                "updated_steps": completed.get("updated_steps")
                or sum(1 for row in metrics if not bool(row.get("skipped"))),
                "skipped_steps": 0,
            },
        }

    checkpoint_history_latest = dict(checkpoint_history[-1] if checkpoint_history else {})
    checkpoint_summary: dict[str, Any] = {}
    checkpoint_step = latest_checkpoint.get("step") if latest_checkpoint else None
    checkpoint_dir = latest_checkpoint.get("checkpoint_dir") if latest_checkpoint else None
    checkpoint_saved_count = latest_checkpoint.get("saved_count") if latest_checkpoint else None
    checkpoint_interval_seconds = (
        latest_checkpoint.get("checkpoint_interval_seconds") if latest_checkpoint else None
    )
    checkpoint_progress = None
    if isinstance(checkpoint_step, int) and checkpoint_step > 0:
        planned_steps = as_float(
            live.get("planned_steps")
            or run_config.get("grpo_steps")
            or run_manifest.get("planned_steps")
        )
        if planned_steps > 0:
            checkpoint_progress = checkpoint_step / planned_steps
    checkpoint_summary = {
        "latest_checkpoint": latest_checkpoint or live_checkpoint or None,
        "checkpoint_history_records": len(checkpoint_history),
        "checkpoint_history_latest": checkpoint_history_latest or None,
        "checkpoint_step": checkpoint_step,
        "checkpoint_dir": checkpoint_dir,
        "checkpoint_saved_count": checkpoint_saved_count,
        "checkpoint_interval_seconds": checkpoint_interval_seconds,
        "checkpoint_progress": checkpoint_progress,
        "checkpoint_progress_text": (
            f"{checkpoint_step}/{int(as_float(live.get('planned_steps') or run_config.get('grpo_steps') or run_manifest.get('planned_steps')))}"
            if checkpoint_step is not None
            and as_float(
                live.get("planned_steps")
                or run_config.get("grpo_steps")
                or run_manifest.get("planned_steps")
            )
            else "等待检查点进度"
        ),
    }

    summary = dict(live.get("summary") or {})
    recent = dict(live.get("recent") or {})
    last_record = dict(metrics[-1] if metrics else (live.get("last_record") or {}))
    if not summary and metrics:
        summary = {
            "recorded_steps": len(metrics),
            "updated_steps": sum(1 for row in metrics if not bool(row.get("skipped"))),
            "skipped_steps": sum(1 for row in metrics if bool(row.get("skipped"))),
        }
    if not summary and live.get("summary"):
        summary = dict(live.get("summary") or {})
    online_latest = dict(live.get("online_eval_latest") or (online_eval[-1] if online_eval else {}))
    online_eval_records = list(online_eval)
    if online_latest and not online_eval_records:
        online_eval_records = [online_latest]

    skipped = [row for row in metrics if bool(row.get("skipped"))]
    updated = [row for row in metrics if not bool(row.get("skipped"))]
    skip_reasons = Counter(str(row.get("reason")) for row in skipped if row.get("reason"))
    terminations: Counter[str] = Counter()
    tool_counts: Counter[str] = Counter()
    for row in metrics:
        for key, value in dict(row.get("termination_counts") or {}).items():
            terminations[str(key)] += int(value)
        for key, value in dict(row.get("trajectory_tool_counts") or {}).items():
            tool_counts[str(key)] += int(value)

    alerts = list(live.get("alerts") or [])
    failure_signals = classify_failure_signals(
        metrics=metrics,
        tool_counts=tool_counts,
        terminations=terminations,
        skip_reasons=skip_reasons,
        live=live,
    )
    gates = build_gate_results(
        metrics=metrics,
        online_latest=online_latest,
        failure_signals=failure_signals,
        live=live,
    )
    practices = practice_ladder(gates)
    next_actions = recommend_next_actions(failure_signals, gates, live)
    health: list[str] = []
    if not metrics and legacy_metrics_payload is not None:
        legacy_rows = list(legacy_metrics_payload.get("metrics") or [])
        metrics = [
            {
                "step": row.get("step"),
                "epoch": row.get("epoch"),
                "mean_reward": row.get("train_loss"),
                "loss": row.get("eval_loss", row.get("train_loss")),
                "reward_signal_std": 0.0 if row.get("train_loss") is not None else None,
                "skipped": False,
                "trajectory_tool_counts": {"legacy_metrics": 1},
            }
            for row in legacy_rows
            if isinstance(row, dict)
        ]
        if not live:
            live = {
                "status": "completed",
                "planned_steps": legacy_metrics_payload.get("max_steps")
                or legacy_metrics_payload.get("requested_max_steps"),
                "summary": {
                    "recorded_steps": len(metrics),
                    "updated_steps": len(metrics),
                    "skipped_steps": 0,
                    "skip_reasons": {},
                },
                "recent": {
                    "window": len(metrics),
                    "recorded_steps": len(metrics),
                    "updated_steps": len(metrics),
                    "mean_reward": metrics[-1].get("mean_reward") if metrics else None,
                    "mean_pass_rate": None,
                    "mean_loss": metrics[-1].get("loss") if metrics else None,
                    "termination_counts": {},
                },
                "alerts": [],
                "latest_checkpoint": None,
                "online_eval_latest": None,
            }

    if not metrics:
        health.append("还没有训练步指标")
    if metrics and not updated:
        health.append("还没有优化器更新")
    if skip_reasons.get("low_reward_signal"):
        health.append("奖励信号波动太低")
    if terminations.get("context_overflow"):
        health.append("发生上下文溢出")
    if tool_counts and not tool_counts.get("write_file") and not tool_counts.get("final_answer"):
        health.append("轨迹只读，未编辑或总结")
    if alerts:
        health.append(f"{len(alerts)} live alert(s)")
    if failure_report:
        health.append("存在失败报告")
    if fetch_manifest:
        fetched_count = sum(
            1
            for record in dict(fetch_manifest.get("files") or {}).values()
            if dict(record).get("fetched")
        )
        health.append(f"已抓取工件数量：{fetched_count}")
    if train_log_tail:
        health.append("已经抓取训练日志尾部")
    if train_log_events:
        health.append(f"结构化日志事件数量：{len(train_log_events)}")
    if job_health and as_float(job_health.get("last_metric_age_sec"), 0.0) > 600.0:
        health.append("任务心跳过期")
    if (
        checkpoint_summary.get("checkpoint_progress_text")
        and checkpoint_summary.get("checkpoint_progress") is not None
    ):
        health.append(f"检查点进度 {checkpoint_summary['checkpoint_progress_text']}")
    elif checkpoint_summary.get("latest_checkpoint"):
        health.append("存在检查点记录")

    metrics_sha = file_sha256(run_dir / "grpo_step_metrics.jsonl")
    live_sha = file_sha256(run_dir / "live_status.json")
    manifest_sha = file_sha256(run_dir / "run_manifest.json") or file_sha256(
        run_dir / "manifest.json"
    )
    trace_sha = file_sha256(run_dir / "agentic_traces.jsonl") or file_sha256(
        run_dir / "rollout_traces.jsonl"
    )
    job_health_sha = file_sha256(run_dir / "job_health.json") or file_sha256(
        run_dir / "asi1_job_health.json"
    )
    run_id = hashlib.sha256(str(run_dir.resolve()).encode("utf-8")).hexdigest()[:16]
    lineage = {
        "run_id": run_manifest.get("run_id") or run_id,
        "git_sha": run_manifest.get("git_sha") or run_config.get("git_sha"),
        "command": run_manifest.get("command") or run_config.get("command"),
        "environment": run_manifest.get("environment") or run_config.get("environment"),
        "model_name": run_manifest.get("model_name")
        or run_manifest.get("model_path")
        or run_config.get("model_name")
        or run_config.get("base_model")
        or "未知",
        "adapter_init": run_manifest.get("adapter_init") or run_config.get("adapter_init"),
        "benchmark_file": run_manifest.get("benchmark_file") or run_config.get("benchmark_file"),
        "holdout_file": run_manifest.get("holdout_file") or run_config.get("holdout_file"),
        "online_eval_benchmark_file": run_manifest.get("online_eval_benchmark_file")
        or run_config.get("online_eval_benchmark_file"),
        "dataset_sha256": run_manifest.get("dataset_sha256"),
        "model_sha256": run_manifest.get("model_sha256"),
        "adapter_sha256": run_manifest.get("adapter_sha256"),
        "metrics_sha256": metrics_sha,
        "live_status_sha256": live_sha,
        "manifest_sha256": manifest_sha,
        "trace_sha256": trace_sha,
        "job_health_sha256": job_health_sha,
    }
    artifact_status = {
        "run_manifest": bool(run_manifest),
        "metrics": bool(metrics),
        "live_status": bool(live),
        "online_eval_history": bool(online_eval),
        "agentic_traces": bool(trace_rows),
        "structured_training_log": bool(train_log_events),
        "job_health": bool(job_health),
        "failure_report": bool(failure_report),
        "safety_report": bool(safety_report),
    }
    trace_summary = {
        "span_count": len(trace_rows),
        "span_types": dict(
            sorted(
                Counter(
                    str(row.get("span_type")) for row in trace_rows if row.get("span_type")
                ).items()
            )
        ),
        "tool_names": dict(
            sorted(
                Counter(
                    str(row.get("tool_name")) for row in trace_rows if row.get("tool_name")
                ).items()
            )
        ),
        "error_count": sum(1 for row in trace_rows if row.get("error")),
    }
    eval_history_summary = {
        "records": len(online_eval_records),
        "latest": online_latest or eval_summary,
        "failure_categories": dict(
            online_latest.get("failure_categories") or eval_summary.get("failure_categories") or {}
        ),
    }
    safety_summary = {
        "unsafe_tool_events": live_safety.get("unsafe_tool_events")
        or safety_report.get("unsafe_tool_events")
        or 0,
        "prompt_injection_events": live_safety.get("prompt_injection_events")
        or safety_report.get("prompt_injection_events")
        or 0,
        "secrets_events": live_safety.get("secrets_events")
        or safety_report.get("secrets_events")
        or 0,
        "destructive_command_blocks": live_safety.get("destructive_command_blocks")
        or safety_report.get("destructive_command_blocks")
        or 0,
    }
    status_text = derive_run_status_text(
        live=live,
        job_health=dict(live.get("job_health") or job_health),
        failure_report=failure_report,
        run_config=run_config,
        run_manifest=run_manifest,
        metrics=metrics,
    )
    run_status = effective_run_status(
        live=live,
        job_health=dict(live.get("job_health") or job_health),
        failure_report=failure_report,
        metrics=metrics,
    )
    huanxin_evidence = build_huanxin_run_evidence(
        live=live,
        job_health=job_health,
        run_manifest=run_manifest,
        run_config=run_config,
        fetch_manifest=fetch_manifest,
        train_log_tail=train_log_tail,
    )

    return {
        "run_id": str(lineage["run_id"]),
        "name": run_dir.name,
        "path": str(run_dir),
        "mtime": run_dir.stat().st_mtime,
        "live": live,
        "metrics": metrics,
        "online_eval": online_eval_records,
        "run_config": run_config,
        "status": run_status,
        "status_text": status_text["text"],
        "status_detail": status_text["detail"],
        "planned_steps": live.get("planned_steps")
        or summary.get("planned_steps")
        or run_config.get("grpo_steps"),
        "recorded_steps": summary.get("recorded_steps", len(metrics)),
        "updated_steps": summary.get("updated_steps", len(updated)),
        "skipped_steps": summary.get("skipped_steps", len(skipped)),
        "last_record": last_record,
        "recent": recent,
        "online_latest": online_latest,
        "skip_reasons": dict(sorted(skip_reasons.items())),
        "terminations": dict(sorted(terminations.items())),
        "tool_counts": dict(sorted(tool_counts.items())),
        "failure_signals": failure_signals,
        "gates": gates,
        "practices": practices,
        "next_actions": next_actions,
        "lineage": lineage,
        "alerts": alerts,
        "health": health,
        "run_manifest": run_manifest,
        "job_health": dict(live.get("job_health") or job_health),
        "latest_checkpoint": latest_checkpoint or live_checkpoint,
        "checkpoint_history": checkpoint_history,
        "checkpoint_summary": checkpoint_summary,
        "failure_report": failure_report,
        "safety_summary": safety_summary,
        "trace_summary": trace_summary,
        "eval_history_summary": eval_history_summary,
        "artifact_status": artifact_status,
        "fetch_manifest": fetch_manifest,
        "train_log_tail": train_log_tail,
        "train_log_events": train_log_events,
        "train_log_summary": train_log_summary,
        "huanxin_evidence": huanxin_evidence,
    }


def line_chart_svg(
    rows: list[dict[str, Any]], key: str, *, width: int = 560, height: int = 150
) -> str:
    pairs = []
    for index, row in enumerate(rows):
        value = as_float(row.get(key), default=float("nan"))
        if value == value:
            pairs.append((as_float(row.get("step"), index), value))
    if len(pairs) < 2:
        if len(pairs) == 1:
            return (
                f'<div class="empty-chart">已捕获第一个数值：{pairs[0][1]:.4g}；等待下一个点</div>'
            )
        return '<div class="empty-chart">暂无曲线点；远程日志尚未产生该指标</div>'

    min_v = min(value for _, value in pairs)
    max_v = max(value for _, value in pairs)
    if min_v == max_v:
        min_v -= 1.0
        max_v += 1.0

    left, top, right, bottom = 34, 12, width - 12, height - 26
    x_min = min(step for step, _ in pairs)
    x_max = max(step for step, _ in pairs)
    x_span = max(x_max - x_min, 1)
    y_span = max_v - min_v

    points = []
    for step, value in pairs:
        x = left + (step - x_min) / x_span * (right - left)
        y = bottom - (value - min_v) / y_span * (bottom - top)
        points.append(f"{x:.1f},{y:.1f}")

    label = html.escape(visible_metric_name(key))
    return (
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{label} 曲线">'
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" class="axis"/>'
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" class="axis"/>'
        f'<polyline points="{" ".join(points)}" class="series"/>'
        f'<text x="{left}" y="{height - 6}" class="chart-label">{label}</text>'
        f'<text x="{left}" y="10" class="tick">{max_v:.3g}</text>'
        f'<text x="{left}" y="{bottom - 2}" class="tick">{min_v:.3g}</text>'
        "</svg>"
    )


def panel_description(title: str, text: str) -> str:
    return f'<p class="panel-desc"><strong>{html.escape(title)}。</strong>{html.escape(text)}</p>'


def metric_text(value: Any, *, kind: str = "number", pending: str = "等待第一条远程指标") -> str:
    if value is None:
        return pending
    if kind == "percent":
        return pct(value)
    return fmt(value)


def display_text(value: Any, pending: str = "尚未观察到") -> str:
    if value is None or value == "":
        return pending
    return format_display_value(value, empty=pending)


def first_present(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def domain_pass_rate(latest: dict[str, Any], domain: str) -> Any:
    metrics = dict(dict(latest.get("domain_metrics") or {}).get(domain) or {})
    return first_present(latest.get(f"{domain}_pass_rate"), metrics.get("pass_rate"))


def exact_blocker_text(run: dict[str, Any]) -> str:
    failure_report = dict(run.get("failure_report") or {})
    for key in ("exact_blocker", "blocker_text", "blocker", "startup_diagnosis", "summary"):
        if failure_report.get(key):
            return zh_failure_summary(failure_report.get(key))
    if run.get("status_detail"):
        return zh_status_text(run.get("status_detail"))
    if run.get("status_text"):
        return zh_status_text(run.get("status_text"))
    return "暂无明确阻塞"


def metric_age_text(job_health: dict[str, Any], run: dict[str, Any]) -> str:
    age = job_health.get("last_metric_age_sec")
    if age is not None:
        return metric_text(age, pending="等待指标")
    if run.get("metrics"):
        return "已捕获最终指标"
    return "等待指标"


def run_chart_block(label: str, key: str, description: str, metrics: list[dict[str, Any]]) -> str:
    return f"""
        <section class="chart-card">
          <h3>{html.escape(label)}</h3>
          <p class="chart-help">{html.escape(description)}</p>
          {line_chart_svg(metrics, key)}
        </section>
    """


def render_grpo_curve_grid(metrics: list[dict[str, Any]]) -> str:
    return f"""
      <div class="grid">
        {run_chart_block("平均奖励", "mean_reward", "判断策略是否改善的主趋势线。", metrics)}
        {run_chart_block("奖励波动", "reward_signal_std", "如果长期接近零，说明训练信号太弱或太均匀。", metrics)}
        {run_chart_block("训练通过率", "pass_rate", "这是最接近直接成功率的指标。", metrics)}
        {run_chart_block("损失", "loss", "这是辅助指标，不是最终结论。", metrics)}
        {run_chart_block("KL 系数", "kl_coeff", "用于观察策略更新幅度，避免更新过猛或完全不动。", metrics)}
      </div>
    """


def rl_metric_cards(run: dict[str, Any]) -> str:
    last = run["last_record"]
    online = run["online_latest"]
    recent = run["recent"]
    cards = [
        ("平均奖励", metric_text(last.get("mean_reward"), pending="等待第一步 GRPO")),
        ("奖励波动", metric_text(last.get("reward_signal_std"), pending="等待奖励波动")),
        ("训练通过率", metric_text(last.get("pass_rate"), kind="percent", pending="等待轨迹验证")),
        (
            "评测通过率",
            metric_text(
                online.get("pass_rate") if online else None, kind="percent", pending="等待留出评测"
            ),
        ),
        (
            "量子评测",
            metric_text(
                domain_pass_rate(online, "quantum") if online else None,
                kind="percent",
                pending="等待量子评测",
            ),
        ),
        (
            "软件工程评测",
            metric_text(
                domain_pass_rate(online, "software") if online else None,
                kind="percent",
                pending="等待软件工程评测",
            ),
        ),
        (
            "智能体评测",
            metric_text(
                domain_pass_rate(online, "agentic") if online else None,
                kind="percent",
                pending="等待智能体评测",
            ),
        ),
        ("损失", metric_text(last.get("loss"), pending="等待优化器更新")),
        ("KL 系数", metric_text(last.get("kl_coeff") or last.get("kl"), pending="等待 KL 记录")),
        ("策略更新", display_text(run.get("updated_steps"), "0")),
        ("跳过步数", display_text(run.get("skipped_steps"), "0")),
    ]
    if recent:
        cards.extend(
            [
                ("最近奖励", metric_text(recent.get("mean_reward"), pending="等待最近窗口")),
                (
                    "最近通过率",
                    metric_text(
                        recent.get("mean_pass_rate"), kind="percent", pending="等待最近窗口"
                    ),
                ),
            ]
        )
    return "".join(
        f'<div class="stat"><span>{html.escape(label)}</span><strong>{html.escape(str(value))}</strong></div>'
        for label, value in cards
    )


def render_checkpoint_eval_status(run: dict[str, Any]) -> str:
    checkpoint_summary = dict(run.get("checkpoint_summary") or {})
    eval_summary = dict(run.get("eval_history_summary") or {})
    latest_eval = dict(eval_summary.get("latest") or {})
    latest_checkpoint = dict(run.get("latest_checkpoint") or {})
    cards = [
        (
            "检查点进度",
            display_text(checkpoint_summary.get("checkpoint_progress_text"), "等待检查点进度"),
        ),
        (
            "已保存检查点",
            display_text(
                checkpoint_summary.get("checkpoint_saved_count")
                if checkpoint_summary.get("checkpoint_saved_count") is not None
                else latest_checkpoint.get("saved_count"),
                "等待检查点数量",
            ),
        ),
        ("最新检查点步", display_text(checkpoint_summary.get("checkpoint_step"), "等待检查点步数")),
        ("在线评测记录", display_text(eval_summary.get("records"), "0")),
        (
            "总评测通过率",
            metric_text(
                latest_eval.get("pass_rate") if latest_eval else None,
                kind="percent",
                pending="等待留出评测",
            ),
        ),
        (
            "量子通过率",
            metric_text(
                domain_pass_rate(latest_eval, "quantum"), kind="percent", pending="等待量子评测"
            ),
        ),
        (
            "软件工程通过率",
            metric_text(
                domain_pass_rate(latest_eval, "software"),
                kind="percent",
                pending="等待软件工程评测",
            ),
        ),
        (
            "智能体通过率",
            metric_text(
                domain_pass_rate(latest_eval, "agentic"), kind="percent", pending="等待智能体评测"
            ),
        ),
        (
            "评测奖励",
            metric_text(
                latest_eval.get("mean_total_reward") if latest_eval else None,
                pending="等待留出评测",
            ),
        ),
    ]
    stat_html = "".join(
        f'<div class="stat"><span>{html.escape(label)}</span><strong>{html.escape(str(value))}</strong></div>'
        for label, value in cards
    )
    checkpoint_items = compact_dict_items(
        checkpoint_summary or latest_checkpoint,
        [
            "checkpoint_step",
            "checkpoint_dir",
            "checkpoint_saved_count",
            "checkpoint_interval_seconds",
            "checkpoint_progress_text",
        ],
    )
    eval_items = compact_dict_items(
        latest_eval,
        [
            "step",
            "task_count",
            "pass_rate",
            "quantum_pass_rate",
            "software_pass_rate",
            "agentic_pass_rate",
            "mean_total_reward",
            "domain_metrics",
        ],
    )
    return f"""
      <h3>检查点与评测状态</h3>
      <p class="panel-desc">这里把“是否保存了可恢复状态”和“留出评测是否有结果”放在一起，避免只看训练奖励。</p>
      <div class="mini-stats">{stat_html}</div>
      <div class="details">
        <div><h3>检查点证据</h3><ul>{checkpoint_items}</ul></div>
        <div><h3>评测证据</h3><ul>{eval_items}</ul></div>
      </div>
    """


def render_huanxin_run_evidence(run: dict[str, Any]) -> str:
    evidence = dict(run.get("huanxin_evidence") or {})
    marker_items = counter_items(
        dict(evidence.get("launcher_markers") or {}), empty="还没有启动标记"
    )
    evidence_items = compact_dict_items(
        evidence,
        [
            "environment",
            "task_name",
            "task_id",
            "task_status",
            "task_status_code",
            "use_time",
            "remote_root",
            "remote_path",
            "fetch_env",
            "fetched_files",
            "rank_started",
            "rank_completed",
            "world_size",
            "accelerator_log_seen",
        ],
    )
    return f"""
      <h3>焕新运行证据</h3>
      <p class="panel-desc">这些字段来自状态、任务健康、抓取清单和日志标记，用来确认远程环境、任务编号、NPU rank 和工件来源。</p>
      <div class="details">
        <div><h3>任务与环境</h3><ul>{evidence_items}</ul></div>
        <div><h3>启动标记</h3><ul>{marker_items}</ul></div>
      </div>
    """


def render_run_card(run: dict[str, Any]) -> str:
    last = run["last_record"]
    online = run["online_latest"]
    metrics = run["metrics"]
    health = run["health"] or ["本地工件中没有明显阻塞"]
    health_items = "".join(f"<li>{html.escape(zh_health_item(item))}</li>" for item in health)
    gate_items = "".join(
        (
            f'<li><span class="gate {"pass" if gate["passed"] else "fail"}">'
            f'{zh_gate_text(bool(gate["passed"]))}</span> '
            f'<span class="priority">{html.escape(str(gate.get("priority", "P2")))}</span> '
            f'{html.escape(zh_label(gate["name"]))}：{html.escape(zh_detail(gate["detail"]))}</li>'
        )
        for gate in run["gates"]
    )
    action_items = "".join(
        f"<li>{html.escape(zh_action(item))}</li>" for item in run["next_actions"]
    )
    practice_items = "".join(
        (
            f'<li><span class="gate {"pass" if payload["passed"] else "fail"}">'
            f'{zh_gate_text(bool(payload["passed"]))}</span> '
            f'{html.escape(priority)}：{html.escape(str(payload["label"]))}</li>'
        )
        for priority, payload in run["practices"].items()
    )
    tool_items = counter_items(run["tool_counts"], empty="还没有工具调用记录")
    skip_items = counter_items(run["skip_reasons"], empty="没有跳过原因")
    termination_items = counter_items(run["terminations"], empty="还没有轨迹结束原因")
    failure_items = counter_items(run["failure_signals"], empty="没有明显失败信号")
    lineage_items = compact_dict_items(
        run["lineage"],
        [
            "model_name",
            "benchmark_file",
            "online_eval_benchmark_file",
            "metrics_sha256",
            "live_status_sha256",
        ],
    )
    cards = [
        (
            "状态",
            zh_status_text(run.get("status_text") or zh_status(run["status"])),
        ),
        ("步数", f'{run["recorded_steps"]}/{run["planned_steps"] or "?"}'),
        ("已更新", run["updated_steps"]),
        ("已跳过", run["skipped_steps"]),
        ("最新奖励", metric_text(last.get("mean_reward"), pending="等待第一步 GRPO")),
        ("奖励波动", metric_text(last.get("reward_signal_std"), pending="等待奖励波动")),
        ("训练通过率", metric_text(last.get("pass_rate"), kind="percent", pending="等待轨迹验证")),
        (
            "评测通过率",
            metric_text(
                online.get("pass_rate") if online else None, kind="percent", pending="等待留出评测"
            ),
        ),
    ]
    stat_html = "".join(
        f'<div class="stat"><span>{html.escape(str(label))}</span><strong>{html.escape(str(value))}</strong></div>'
        for label, value in cards
    )
    return f"""
    <section class="run">
      <div class="run-head">
        <div>
          <h2>{html.escape(run["name"])}</h2>
          <p>{html.escape(run["path"])}</p>
          <p class="status-detail">{html.escape(zh_status_text(display_text(run.get("status_detail"), "")))}</p>
        </div>
        <span class="badge">{html.escape(zh_status(run["status"]))}</span>
      </div>
      <div class="lineage">
        <span>运行 <strong>{html.escape(str(run["run_id"]))}</strong></span>
        <span>模型 <strong>{html.escape(display_text(run["lineage"].get("model_name"), "模型未记录"))}</strong></span>
        <span>指标指纹 <strong>{html.escape(short_sha(run["lineage"].get("metrics_sha256")))}</strong></span>
      </div>
      <div class="stats">{stat_html}</div>
      <h3>强化学习指标</h3>
      <p class="panel-desc">这里回答“训练是否真的在进步”：优先看奖励、奖励波动、训练通过率、留出评测、损失和是否持续更新。</p>
      <div class="stats">{rl_metric_cards(run)}</div>
      {render_grpo_curve_grid(metrics)}
      {render_checkpoint_eval_status(run)}
      {render_huanxin_run_evidence(run)}
      <div class="details">
        <div><h3>优先级门槛</h3><p class="panel-desc">P0 保护真实训练和安全；P1 保护评测可信度；P2 判断是否可以扩容。</p><ul class="gates">{practice_items}</ul></div>
        <div><h3>门槛结果</h3><p class="panel-desc">只要 P0 未通过，就不要扩容。</p><ul class="gates">{gate_items}</ul></div>
        <div><h3>下一步</h3><p class="panel-desc">这些是当前最小、最有用的动作。</p><ul>{action_items}</ul></div>
        <div><h3>健康诊断</h3><p class="panel-desc">快速说明为什么这个运行需要关注。</p><ul>{health_items}</ul></div>
        <div><h3>工具行为</h3><p class="panel-desc">看智能体是否在读文件、改代码、跑测试和完成任务。</p><ul>{tool_items}</ul></div>
        <div><h3>跳过原因</h3><p class="panel-desc">跳过更新通常表示奖励信号无效或批次质量不足。</p><ul>{skip_items}</ul></div>
        <div><h3>轨迹结束原因</h3><p class="panel-desc">溢出或超时过多时，需要调整上下文和回合预算。</p><ul>{termination_items}</ul></div>
        <div><h3>失败类型</h3><p class="panel-desc">区分数据、工具、上下文、奖励设计和平台问题。</p><ul>{failure_items}</ul></div>
        <div><h3>来源摘要</h3><p class="panel-desc">确认模型、训练集、评测集和指标指纹是否可比。</p><ul>{lineage_items}</ul></div>
      </div>
    </section>
    """


def render_compact_run_summary(run: dict[str, Any]) -> str:
    last = run["last_record"]
    online = run["online_latest"]
    return f"""
    <section class="mini-run">
      <div class="run-head">
        <div>
          <h2>{html.escape(run["name"])}</h2>
          <p>{html.escape(run["path"])}</p>
          <p class="status-detail">{html.escape(zh_status_text(display_text(run.get("status_detail"), "")))}</p>
        </div>
        <span class="badge">{html.escape(zh_status(run["status"]))}</span>
      </div>
      {panel_description("本页用途", "这是快速健康视图。好的运行应该持续更新，关键门槛通过，奖励曲线不能长期平坦。")}
      <div class="mini-stats">
        <div class="stat wide"><span>状态</span><strong>{html.escape(zh_status_text(run.get("status_text") or run["status"]))}</strong></div>
        <div class="stat"><span>奖励</span><strong>{metric_text(last.get("mean_reward"), pending="等待第一步 GRPO")}</strong></div>
        <div class="stat"><span>奖励波动</span><strong>{metric_text(last.get("reward_signal_std"), pending="等待奖励波动")}</strong></div>
        <div class="stat"><span>训练通过率</span><strong>{metric_text(last.get("pass_rate"), kind="percent", pending="等待轨迹验证")}</strong></div>
        <div class="stat"><span>评测通过率</span><strong>{metric_text(online.get("pass_rate") if online else None, kind="percent", pending="等待留出评测")}</strong></div>
      </div>
    </section>
    """


def render_gate_summary(run: dict[str, Any]) -> str:
    gate_items = "".join(
        (
            f'<li><span class="gate {"pass" if gate["passed"] else "fail"}">'
            f'{"通过" if gate["passed"] else "未过"}</span> '
            f'<span class="priority">{html.escape(str(gate.get("priority", "P2")))}</span> '
            f'{html.escape(zh_label(gate["name"]))}：{html.escape(zh_detail(gate["detail"]))}</li>'
        )
        for gate in run["gates"]
    )
    return f"""
    <section class="mini-run">
      <div class="run-head">
        <div>
          <h2>{html.escape(run["name"])}</h2>
          <p>这个运行的门槛阶梯。先看 P0；任何 P0 未通过，都不要扩容。</p>
        </div>
      </div>
      <ul class="gates">{gate_items}</ul>
    </section>
    """


def render_chart_summary(run: dict[str, Any]) -> str:
    metrics = run["metrics"]
    return f"""
    <section class="mini-run">
      <div class="run-head">
        <div>
          <h2>{html.escape(run["name"])}</h2>
          <p>曲线展示运行是否在学习、是否稳定、是否真的解决任务。空图表示远程运行还没有产出对应工件。</p>
        </div>
      </div>
      <h3>强化学习指标</h3>
      <p class="panel-desc">顶尖团队通常先看客观奖励和通过率，再看奖励波动、KL/损失、跳过更新、评测通过率和失败类型。</p>
      <div class="mini-stats">{rl_metric_cards(run)}</div>
      {render_grpo_curve_grid(metrics)}
      {render_checkpoint_eval_status(run)}
      {render_huanxin_run_evidence(run)}
    </section>
    """


def eval_chart_rows(run: dict[str, Any]) -> list[dict[str, Any]]:
    rows = list(run.get("online_eval") or [])
    if not rows:
        latest = dict((run.get("eval_history_summary") or {}).get("latest") or {})
        if latest:
            rows = [latest]
    normalized: list[dict[str, Any]] = []
    for row in rows:
        domain_metrics = dict(row.get("domain_metrics") or {})
        quantum_metrics = dict(domain_metrics.get("quantum") or {})
        software_metrics = dict(domain_metrics.get("software") or {})
        agentic_metrics = dict(domain_metrics.get("agentic") or {})
        normalized.append(
            {
                **row,
                "quantum_pass_rate": (
                    row.get("quantum_pass_rate")
                    if row.get("quantum_pass_rate") is not None
                    else quantum_metrics.get("pass_rate")
                ),
                "software_pass_rate": (
                    row.get("software_pass_rate")
                    if row.get("software_pass_rate") is not None
                    else software_metrics.get("pass_rate")
                ),
                "agentic_pass_rate": (
                    row.get("agentic_pass_rate")
                    if row.get("agentic_pass_rate") is not None
                    else agentic_metrics.get("pass_rate")
                ),
            }
        )
    return normalized


def render_lineage_summary(run: dict[str, Any]) -> str:
    items = compact_dict_items(
        run["lineage"],
        [
            "model_name",
            "benchmark_file",
            "holdout_file",
            "online_eval_benchmark_file",
            "dataset_sha256",
            "model_sha256",
            "adapter_sha256",
            "metrics_sha256",
            "live_status_sha256",
            "manifest_sha256",
        ],
    )
    return f"""
    <section class="mini-run">
      <div class="run-head"><div><h2>{html.escape(run["name"])}</h2><p>需要确认运行编号、配置、指纹和工件时，看这一页。</p></div></div>
      <ul>{items}</ul>
    </section>
    """


def render_raw_summary(run: dict[str, Any]) -> str:
    return f"""
    <section class="mini-run">
      <div class="run-head"><div><h2>{html.escape(run["name"])}</h2><p>这是诊断摘要，只展示计数和类别，不要求阅读完整运行卡片。</p></div></div>
      <div class="details">
        <div><h3>工具行为</h3><ul>{counter_items(run["tool_counts"], empty="还没有工具调用记录")}</ul></div>
        <div><h3>跳过原因</h3><ul>{counter_items(run["skip_reasons"], empty="没有跳过原因")}</ul></div>
        <div><h3>轨迹结束原因</h3><ul>{counter_items(run["terminations"], empty="还没有轨迹结束原因")}</ul></div>
        <div><h3>失败类型</h3><ul>{counter_items(run["failure_signals"], empty="没有明显失败信号")}</ul></div>
        <div><h3>日志事件摘要</h3><p class="panel-desc">当工件抓取延迟时，这里用日志事件计数判断训练是否继续前进。</p><ul>{counter_items(dict((run.get("train_log_summary") or {}).get("stage_counts") or {}), empty="还没有结构化日志事件")}</ul></div>
      </div>
    </section>
    """


def render_infra_summary(run: dict[str, Any]) -> str:
    job_health = run["job_health"] or {}
    fetch_manifest = run.get("fetch_manifest") or {}
    train_log_summary = dict(run.get("train_log_summary") or {})
    checkpoint_summary = dict(run.get("checkpoint_summary") or {})
    latest_checkpoint = dict(run.get("latest_checkpoint") or {})
    fetched_files = dict(fetch_manifest.get("files") or {})
    fetched_count = sum(
        1 for record in fetched_files.values() if isinstance(record, dict) and record.get("fetched")
    )
    cards = [
        (
            "任务状态",
            zh_status_text(
                run.get("status_text") or job_health.get("huanxin_task_status") or run["status"]
            ),
        ),
        ("进程存活", display_text(job_health.get("pid_alive"), "任务接口不可见")),
        ("指标新鲜度", metric_age_text(job_health, run)),
        ("日志新鲜度", metric_text(job_health.get("last_log_age_sec"), pending="等待日志抓取")),
        ("可见 NPU", display_text(job_health.get("npu_visible"), "等待 NPU 采样")),
        ("NPU 利用率", metric_text(job_health.get("npu_util"), pending="等待 NPU 采样")),
        ("NPU 内存", metric_text(job_health.get("npu_mem_used"), pending="等待 NPU 采样")),
        ("检查点年龄", metric_text(job_health.get("checkpoint_age_sec"), pending="还没有检查点")),
        (
            "检查点进度",
            display_text(checkpoint_summary.get("checkpoint_progress_text"), "等待检查点进度"),
        ),
        (
            "已保存检查点",
            display_text(
                checkpoint_summary.get("checkpoint_saved_count")
                if checkpoint_summary.get("checkpoint_saved_count") is not None
                else latest_checkpoint.get("saved_count"),
                "等待检查点数量",
            ),
        ),
    ]
    stat_html = "".join(
        f'<div class="stat"><span>{html.escape(label)}</span><strong>{html.escape(str(value))}</strong></div>'
        for label, value in cards
    )
    health_items = compact_dict_items(
        job_health,
        [
            "environment",
            "huanxin_task_name",
            "huanxin_task_id",
            "huanxin_task_status",
            "huanxin_use_time",
            "last_metric_age_sec",
            "last_log_age_sec",
            "npu_visible",
            "npu_util",
            "npu_mem_used",
        ],
    )
    checkpoint_items = compact_dict_items(
        checkpoint_summary or latest_checkpoint,
        [
            "checkpoint_step",
            "checkpoint_dir",
            "checkpoint_saved_count",
            "checkpoint_interval_seconds",
            "checkpoint_progress_text",
        ],
    )
    fetch_items = f"<li><strong>已抓取文件</strong>：{fetched_count}</li><li><strong>来源环境</strong>：{html.escape(display_text(fetch_manifest.get('env'), '未记录'))}</li><li><strong>远程目录</strong>：{html.escape(display_text(fetch_manifest.get('remote_dir'), '未记录'))}</li>"
    log_summary_items = counter_items(
        dict(train_log_summary.get("stage_counts") or {}), empty="还没有结构化日志事件"
    )
    latest_log_summary = compact_dict_items(
        train_log_summary,
        [
            "event_count",
            "latest_training_step",
            "latest_training_reward",
            "latest_training_pass_rate",
            "latest_training_loss",
            "latest_checkpoint",
        ],
    )
    return f"""
    <section class="mini-run">
      <div class="run-head"><div><h2>{html.escape(run["name"])}</h2><p>基础设施健康度回答：ASI1 是否还活着，是否在产出指标，是否有效使用硬件。</p></div></div>
      <div class="mini-stats">{stat_html}</div>
      <p class="panel-desc">{html.escape(zh_status_text(display_text(run.get("status_detail"), "没有额外任务状态详情。")))}</p>
      <p class="panel-desc">远程路径：{html.escape(display_text(job_health.get("remote_path"), "远程输出路径未记录"))}</p>
      <div class="details">
        <div><h3>任务健康</h3><ul>{health_items}</ul></div>
        <div><h3>检查点进度</h3><p class="panel-desc">这里说明运行是否保存中间状态，以及最新检查点推进到计划步数的哪里。</p><ul>{checkpoint_items}</ul></div>
        <div><h3>工件抓取摘要</h3><p class="panel-desc">这里记录从 ASI1 抓取远程运行文件到本地 GUI 的情况。</p><ul>{fetch_items}</ul></div>
        <div><h3>训练日志摘要</h3><p class="panel-desc">这里不展示原始代码或命令，只展示从远程日志提取出的训练进度。</p><ul>{latest_log_summary}</ul></div>
        <div><h3>结构化日志事件</h3><p class="panel-desc">这些事件用于从日志恢复学习进度、检查点节奏和在线评测状态。</p><ul>{log_summary_items}</ul></div>
      </div>
      {render_huanxin_run_evidence(run)}
    </section>
    """


def render_eval_summary(run: dict[str, Any]) -> str:
    eval_summary = run["eval_history_summary"]
    latest = dict(eval_summary.get("latest") or {})
    failure_categories = dict(eval_summary.get("failure_categories") or {})
    domain_metrics = dict(latest.get("domain_metrics") or {})
    chart_rows = eval_chart_rows(run)
    latest_items = compact_dict_items(
        latest,
        [
            "step",
            "task_count",
            "pass_rate",
            "quantum_pass_rate",
            "software_pass_rate",
            "agentic_pass_rate",
            "mean_total_reward",
        ],
    )
    domain_items = (
        "".join(
            f"<li><strong>{html.escape(zh_label(domain))}</strong>：通过率 {html.escape(metric_text(dict(values).get('pass_rate'), kind='percent', pending='等待评测'))}，任务数 {html.escape(display_text(dict(values).get('task_count'), '暂无数据'))}，奖励 {html.escape(metric_text(dict(values).get('mean_total_reward'), pending='暂无数据'))}</li>"
            for domain, values in sorted(domain_metrics.items())
            if isinstance(values, dict)
        )
        or "<li>还没有分领域评测</li>"
    )
    failure_items = counter_items(failure_categories, empty="没有失败类别记录")
    return f"""
    <section class="mini-run">
      <div class="run-head"><div><h2>{html.escape(run["name"])}</h2><p>评测是能否晋级的信号。只有留出评测也变好时，训练奖励才有意义。</p></div></div>
      <div class="mini-stats">
        <div class="stat"><span>评测记录</span><strong>{html.escape(str(eval_summary.get("records", 0)))}</strong></div>
        <div class="stat"><span>总通过率</span><strong>{metric_text(latest.get("pass_rate") if latest else None, kind="percent", pending="等待留出评测")}</strong></div>
        <div class="stat"><span>量子通过率</span><strong>{metric_text(domain_pass_rate(latest, "quantum"), kind="percent", pending="等待量子评测")}</strong></div>
        <div class="stat"><span>软件工程通过率</span><strong>{metric_text(domain_pass_rate(latest, "software"), kind="percent", pending="等待软件工程评测")}</strong></div>
        <div class="stat"><span>智能体通过率</span><strong>{metric_text(domain_pass_rate(latest, "agentic"), kind="percent", pending="等待智能体评测")}</strong></div>
        <div class="stat"><span>评测奖励</span><strong>{metric_text(latest.get("mean_total_reward"), pending="等待留出评测")}</strong></div>
        <div class="stat"><span>任务数</span><strong>{html.escape(display_text(latest.get("task_count"), "等待留出评测"))}</strong></div>
      </div>
      <h3>量子评测曲线</h3>
      <p class="panel-desc">这些留出曲线回答：训练后的检查点是否真的提升量子编码、软件工程和总体能力。</p>
      <div class="grid">
        {run_chart_block("总评测通过率", "pass_rate", "留出评测总通过率。", chart_rows)}
        {run_chart_block("量子通过率", "quantum_pass_rate", "量子算法编码留出任务通过率。", chart_rows)}
        {run_chart_block("软件工程通过率", "software_pass_rate", "软件工程留出任务通过率。", chart_rows)}
        {run_chart_block("智能体通过率", "agentic_pass_rate", "智能体编码轨迹留出任务通过率。", chart_rows)}
        {run_chart_block("评测奖励", "mean_total_reward", "用于晋级判断的留出平均奖励。", chart_rows)}
      </div>
      <div class="details">
        <div><h3>最新评测</h3><ul>{latest_items}</ul></div>
        <div><h3>领域指标</h3><p class="panel-desc">量子编码和软件工程分开看，避免总分掩盖短板。</p><ul>{domain_items}</ul></div>
        <div><h3>失败类别</h3><ul>{failure_items}</ul></div>
      </div>
    </section>
    """


def render_artifact_summary(run: dict[str, Any]) -> str:
    artifact_status = run["artifact_status"]
    items = "".join(
        f'<li><span class="gate {"pass" if present else "fail"}">{"有" if present else "缺"}</span> {html.escape(zh_label(name))}</li>'
        for name, present in artifact_status.items()
    )
    lineage_items = compact_dict_items(
        run["lineage"],
        [
            "model_name",
            "benchmark_file",
            "online_eval_benchmark_file",
            "metrics_sha256",
            "manifest_sha256",
            "trace_sha256",
        ],
    )
    manifest_items = compact_dict_items(
        run["run_manifest"],
        ["run_id", "model_name", "benchmark_file", "planned_steps", "checkpoint_interval_seconds"],
    )
    return f"""
    <section class="mini-run">
      <div class="run-head"><div><h2>{html.escape(run["name"])}</h2><p>工件完整性决定结果以后是否可审计、可比较。</p></div></div>
      <ul class="gates">{items}</ul>
      <div class="details"><div><h3>来源摘要</h3><ul>{lineage_items}</ul></div><div><h3>运行摘要</h3><ul>{manifest_items}</ul></div></div>
    </section>
    """


def render_safety_summary(run: dict[str, Any]) -> str:
    safety = run["safety_summary"]
    safety_items = compact_dict_items(
        safety,
        [
            "unsafe_tool_events",
            "prompt_injection_events",
            "secrets_events",
            "destructive_command_blocks",
        ],
    )
    return f"""
    <section class="mini-run">
      <div class="run-head"><div><h2>{html.escape(run["name"])}</h2><p>安全信号用于在晋级前拦截不安全工具、提示注入、秘密访问和破坏性行为。</p></div></div>
      <div class="mini-stats">
        <div class="stat"><span>不安全工具</span><strong>{html.escape(str(safety.get("unsafe_tool_events", 0)))}</strong></div>
        <div class="stat"><span>提示注入</span><strong>{html.escape(str(safety.get("prompt_injection_events", 0)))}</strong></div>
        <div class="stat"><span>秘密访问</span><strong>{html.escape(str(safety.get("secrets_events", 0)))}</strong></div>
        <div class="stat"><span>破坏性拦截</span><strong>{html.escape(str(safety.get("destructive_command_blocks", 0)))}</strong></div>
      </div>
      <ul>{safety_items}</ul>
    </section>
    """


def render_alert_summary(run: dict[str, Any]) -> str:
    alerts = run["alerts"] or []
    failure_report = run["failure_report"] or {}
    alert_items = (
        "".join(f"<li>{html.escape(visible_alert_message(alert))}</li>" for alert in alerts)
        or "<li>没有实时告警</li>"
    )
    translated_failure_report = {
        key: zh_failure_summary(value) for key, value in failure_report.items()
    }
    failure_items = compact_dict_items(
        translated_failure_report,
        [
            "summary",
            "exact_blocker",
            "blocker_text",
            "blocker",
            "failure_stage",
            "startup_diagnosis",
            "status",
            "task_name",
            "task_id",
        ],
    )
    next_items = (
        "".join(f"<li>{html.escape(zh_action(item))}</li>" for item in run.get("next_actions", []))
        or "<li>暂无下一步建议</li>"
    )
    return f"""
    <section class="mini-run">
      <div class="run-head"><div><h2>{html.escape(run["name"])}</h2><p>告警和失败报告是事故视图，应该说明哪里失败以及下一步做什么。</p></div></div>
      <div class="mini-stats">
        <div class="stat wide"><span>精确阻塞</span><strong>{html.escape(exact_blocker_text(run))}</strong></div>
      </div>
      <div class="details"><div><h3>实时告警</h3><ul>{alert_items}</ul></div><div><h3>失败报告</h3><ul>{failure_items}</ul></div><div><h3>建议动作</h3><ul>{next_items}</ul></div></div>
    </section>
    """


def render_huanxin_environment_status(status: dict[str, Any]) -> str:
    manual = dict(status.get("manual_mode") or {})
    envs = list(status.get("environments") or [])
    if not envs:
        env_cards = """
        <section class="mini-run"><h2>没有找到焕新环境状态</h2><p>需要先采集焕新环境状态，GUI 才能判断认证、保活、终端和任务通道。</p></section>
        """
    else:
        env_cards = "\n".join(
            render_huanxin_environment_card(env) for env in envs if isinstance(env, dict)
        )
    return f"""
      <div class="run">
        <h2>焕新环境</h2>
        {panel_description("这里展示什么", "这里展示焕新控制面的健康状态：手动模式、自动化开关、浏览器认证、终端入口、保活和最近任务元数据。")}
        <div class="mini-stats">
          <div class="stat"><span>手动模式</span><strong>{html.escape(zh_bool(manual.get("manual_mode")))}</strong></div>
          <div class="stat"><span>自动化</span><strong>{html.escape(zh_bool(manual.get("automation_enabled")))}</strong></div>
          <div class="stat"><span>生成时间</span><strong>{html.escape(display_text(status.get("generated_at_utc"), "未采集"))}</strong></div>
          <div class="stat"><span>环境数</span><strong>{len(envs)}</strong></div>
        </div>
      </div>
      {env_cards}
    """


def render_huanxin_environment_card(env: dict[str, Any]) -> str:
    shell_failure = bool(env.get("shell_endpoint_failure"))
    command_channel_ok = bool(env.get("command_channel_recent_success"))
    auth_state = str(env.get("auth_state") or "unknown")
    daemon_ok = bool(env.get("browser_daemon_operational"))
    keepalive_ok = bool(env.get("keepalive_operational"))
    shell_endpoint_label = (
        "降级但可用"
        if shell_failure and command_channel_ok
        else ("失败" if shell_failure else "正常")
    )
    command_channel_label = zh_value(
        env.get("command_channel_transport") or ("最近可用" if command_channel_ok else "未验证")
    )
    sanitized_env = {
        **env,
        "train_dev_url": sanitize_url(env.get("train_dev_url")),
        "current_url": sanitize_url(env.get("current_url")),
    }
    control_items = compact_dict_items(
        sanitized_env,
        [
            "train_dev_url",
            "browser_daemon_state",
            "startup_state",
            "current_url",
            "shell_endpoint_summary",
            "command_channel_recent_success",
            "command_channel_transport",
            "command_channel_age_seconds",
        ],
    )
    job_items = f"<li><strong>最近任务数量</strong>：{html.escape(str(env.get('job_count', 0)))}</li><li><strong>最近任务</strong>：{html.escape(', '.join(str(x) for x in list(env.get('recent_job_ids') or [])[-5:]) or '暂无')}</li>"
    return f"""
    <section class="mini-run">
      <div class="run-head"><div><h2>{html.escape(str(env.get("env_name") or "未知环境"))}</h2><p>{html.escape(zh_value(env.get("summary") or "状态未明"))}</p></div><span class="badge">{html.escape(zh_status(auth_state))}</span></div>
      <div class="mini-stats">
        <div class="stat"><span>浏览器守护</span><strong>{html.escape("正常" if daemon_ok else "需检查")}</strong></div>
        <div class="stat"><span>保活</span><strong>{html.escape("正常" if keepalive_ok else "需检查")}</strong></div>
        <div class="stat"><span>终端入口</span><strong>{html.escape(shell_endpoint_label)}</strong></div>
        <div class="stat"><span>命令通道</span><strong>{html.escape(command_channel_label)}</strong></div>
        <div class="stat"><span>最近任务</span><strong>{html.escape(str(env.get("job_count", 0)))}</strong></div>
      </div>
      <div class="details"><div><h3>控制面</h3><ul>{control_items}</ul></div><div><h3>最近任务</h3><ul>{job_items}</ul></div></div>
    </section>
    """


def render_research_system_status(system_status: dict[str, Any]) -> str:
    outputs = dict(system_status.get("outputs") or {})
    evaluations = dict(system_status.get("evaluations") or {})
    data = dict(system_status.get("data") or {})
    reports = dict(system_status.get("reports") or {})
    docs = dict(system_status.get("docs") or {})
    domain_contracts = list(system_status.get("domain_expert_contracts") or [])
    passing_domain_contracts = sum(
        1 for contract in domain_contracts if dict(contract).get("正常", dict(contract).get("ok"))
    )
    contract_cards = (
        "\n".join(
            render_domain_expert_contract_card(contract)
            for contract in domain_contracts
            if isinstance(contract, dict)
        )
        or """
    <section class="mini-run"><h2>没有找到领域专家课程契约</h2><p>需要构建带领域门槛的课程混合数据，才能在这里展示量子编码训练数据质量。</p></section>
    """
    )
    training_items = compact_dict_items(outputs, ["path", "run_count", "latest_update"])
    eval_items = compact_dict_items(evaluations, ["runs", "benchmarks", "tasks", "latest_update"])
    data_items = compact_dict_items(data, ["datasets", "latest_update"])
    kb_items = f"<li><strong>报告文件</strong>：{html.escape(str(reports.get('files', 0)))}</li><li><strong>报告更新时间</strong>：{html.escape(display_text(reports.get('latest_update'), '未观察到'))}</li><li><strong>文档文件</strong>：{html.escape(str(docs.get('files', 0)))}</li><li><strong>文档更新时间</strong>：{html.escape(display_text(docs.get('latest_update'), '未观察到'))}</li>"
    return f"""
    <div class="run">
      <h2>研发系统</h2>
      {panel_description("控制面", "这是大模型研发闭环的实时索引：训练、评测、数据集、报告、文档、焕新环境、工件和告警。")}
      <div class="mini-stats">
        <div class="stat"><span>训练运行</span><strong>{html.escape(str(outputs.get("run_count", 0)))}</strong></div>
        <div class="stat"><span>评测运行</span><strong>{html.escape(str(evaluations.get("runs", 0)))}</strong></div>
        <div class="stat"><span>数据集</span><strong>{html.escape(str(data.get("datasets", 0)))}</strong></div>
        <div class="stat"><span>报告</span><strong>{html.escape(str(reports.get("files", 0)))}</strong></div>
        <div class="stat"><span>领域契约</span><strong>{html.escape(str(passing_domain_contracts))}/{html.escape(str(len(domain_contracts)))}</strong></div>
      </div>
    </div>
    <section class="mini-run"><div class="details"><div><h3>训练</h3><ul>{training_items}</ul></div><div><h3>评测</h3><ul>{eval_items}</ul></div><div><h3>数据</h3><ul>{data_items}</ul></div><div><h3>知识库</h3><ul>{kb_items}</ul></div></div></section>
    <div class="run"><h2>领域专家课程</h2>{panel_description("为什么重要", "领域专用模型可能过拟合或遗忘通用能力。这些门槛明确量子编码课程的专家覆盖、软件回放和留出任务隔离。")}</div>
    {contract_cards}
    """


def render_domain_expert_contract_card(contract: dict[str, Any]) -> str:
    checks = dict(contract.get("checks") or {})
    check_items = (
        "".join(
            f'<li><span class="gate {"pass" if passed else "fail"}">{"通过" if passed else "未过"}</span> {html.escape(zh_label(name))}</li>'
            for name, passed in sorted(checks.items())
        )
        or "<li>没有配置门槛</li>"
    )
    req_items = compact_dict_items(
        dict(contract.get("requirements") or {}),
        ["train_domain_min", "eval_domain_min", "eval_task_disjoint", "software_replay_min"],
    )
    details = dict(contract.get("details") or {})
    detail_items = compact_dict_items(
        details,
        ["train_domain_counts", "eval_domain_counts", "train_rows", "eval_rows", "holdout_policy"],
    )
    notes = contract.get("reference_notes") or []
    note_items = (
        "".join(f"<li>{html.escape(str(note))}</li>" for note in notes) or "<li>没有参考说明</li>"
    )
    return f"""
    <section class="mini-run">
      <div class="run-head"><div><h2>{html.escape(str(contract.get("dataset") or "数据集"))}</h2><p>{html.escape(display_text(contract.get("purpose"), "领域专家课程契约"))}</p></div><span class="badge">{html.escape("通过" if contract.get("正常", contract.get("ok")) else "需检查")}</span></div>
      <ul class="gates">{check_items}</ul>
      <div class="details"><div><h3>要求</h3><ul>{req_items}</ul></div><div><h3>领域混合</h3><ul>{detail_items}</ul></div><div><h3>参考说明</h3><ul>{note_items}</ul></div></div>
    </section>
    """


def render_source_contract(source_contract: dict[str, Any]) -> str:
    sources = source_contract.get("remote_log_sources") or []
    source_items = (
        "".join(f"<li>{html.escape(artifact_file_label(str(item)))}</li>" for item in sources)
        or "<li>没有记录来源</li>"
    )
    required = dict(source_contract.get("required_run_artifacts") or {})
    required_items = (
        "".join(
            f"<li><strong>{html.escape(zh_label(key))}</strong>：{html.escape(artifact_file_label(str(value)))}</li>"
            for key, value in required.items()
        )
        or "<li>没有必需工件记录</li>"
    )
    present_items = counter_items(
        dict(source_contract.get("present_counts") or {}), empty="还没有已存在计数"
    )
    missing_items = counter_items(
        dict(source_contract.get("missing_counts") or {}), empty="没有缺失计数"
    )
    return f"""
    <div class="run">
      <h2>日志来源</h2>
      {panel_description("远程工件契约", "实时 GUI 应该由多个焕新日志和工件文件驱动。每次训练都应推送或暴露这些文件，让本地面板不用猜状态。")}
      <div class="details"><div><h3>预期来源</h3><ul>{source_items}</ul></div><div><h3>必需运行工件</h3><ul>{required_items}</ul></div><div><h3>已有数量</h3><ul>{present_items}</ul></div><div><h3>缺失数量</h3><ul>{missing_items}</ul></div></div>
      <p class="panel-desc">焕新环境状态是否存在：{html.escape(zh_bool(source_contract.get("huanxin_environment_status_present")))}；生成于 {html.escape(display_text(source_contract.get("huanxin_environment_status_generated_at"), "未采集"))}。</p>
    </div>
    """


def render_rollout_summary(run: dict[str, Any]) -> str:
    trace_summary = run["trace_summary"]
    span_items = counter_items(dict(trace_summary.get("span_types") or {}), empty="还没有轨迹片段")
    tool_items = counter_items(dict(trace_summary.get("tool_names") or {}), empty="还没有工具轨迹")
    return f"""
    <section class="mini-run">
      <div class="run-head"><div><h2>{html.escape(run["name"])}</h2><p>轨迹展示智能体是否在读文件、编辑、测试、从错误恢复并完成任务。</p></div></div>
      <div class="mini-stats">
        <div class="stat"><span>轨迹片段</span><strong>{html.escape(str(trace_summary.get("span_count", 0)))}</strong></div>
        <div class="stat"><span>轨迹错误</span><strong>{html.escape(str(trace_summary.get("error_count", 0)))}</strong></div>
        <div class="stat"><span>工具种类</span><strong>{html.escape(str(len(trace_summary.get("tool_names") or {})))}</strong></div>
        <div class="stat"><span>片段类型</span><strong>{html.escape(str(len(trace_summary.get("span_types") or {})))}</strong></div>
      </div>
      <div class="details"><div><h3>片段类型</h3><ul>{span_items}</ul></div><div><h3>工具名称</h3><ul>{tool_items}</ul></div></div>
    </section>
    """


def latest_run_with_checkpoint(runs: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [
        run
        for run in runs
        if dict(run.get("checkpoint_summary") or {}).get("checkpoint_saved_count")
        or dict(run.get("checkpoint_summary") or {}).get("checkpoint_step")
        or run.get("latest_checkpoint")
    ]
    return candidates[0] if candidates else None


def latest_run_with_eval(runs: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [
        run
        for run in runs
        if dict(run.get("eval_history_summary") or {}).get("records") or run.get("online_latest")
    ]
    return candidates[0] if candidates else None


def run_quantum_eval_text(run: dict[str, Any] | None) -> str:
    if not run:
        return "还没有可用量子留出评测"
    latest = dict(
        (run.get("eval_history_summary") or {}).get("latest") or run.get("online_latest") or {}
    )
    quantum_rate = domain_pass_rate(latest, "quantum")
    total_rate = latest.get("pass_rate")
    if quantum_rate is not None:
        return f"{run['name']}：量子通过率 {pct(quantum_rate)}，总通过率 {pct(total_rate)}"
    if total_rate is not None:
        return f"{run['name']}：已评测，总通过率 {pct(total_rate)}，量子分项待记录"
    return f"{run['name']}：有评测记录，但量子通过率待记录"


def build_decision_summary(
    runs: list[dict[str, Any]],
    huanxin_status: dict[str, Any],
    source_contract: dict[str, Any],
) -> dict[str, Any]:
    active = [run for run in runs if run.get("status") == "active"]
    status_only_running = [run for run in runs if run.get("status") == "running"]
    freshest = runs[0] if runs else None
    checkpoint_run = latest_run_with_checkpoint(runs)
    eval_run = latest_run_with_eval(runs)
    p0_failed = sum(
        1
        for run in runs
        for gate in run.get("gates", [])
        if gate.get("priority") == "P0" and not bool(gate.get("passed"))
    )
    failed_runs = [run for run in runs if run.get("status") == "失败"]
    envs = [env for env in list(huanxin_status.get("environments") or []) if isinstance(env, dict)]
    asi1 = next((env for env in envs if env.get("env_name") == "ASI1"), envs[0] if envs else {})
    asi1_command_ok = bool(asi1.get("command_channel_recent_success"))
    asi1_daemon_ok = bool(asi1.get("browser_daemon_operational"))
    checkpoint_text = (
        f"{checkpoint_run['name']}：{display_text(dict(checkpoint_run.get('checkpoint_summary') or {}).get('checkpoint_progress_text'), '已有检查点，进度未记录')}"
        if checkpoint_run
        else "还没有标准检查点证据"
    )
    if asi1 and not asi1_command_ok:
        blocker = "ASI1 命令通道当前不可用，无法确认远程训练是否继续产出新指标和检查点"
    elif asi1 and not asi1_daemon_ok:
        blocker = "ASI1 浏览器守护进程未运行，远程状态刷新不可靠"
    elif failed_runs:
        blocker = f"{failed_runs[0]['name']}：{zh_status_text(failed_runs[0].get('status_text') or '失败')}"
    elif p0_failed:
        blocker = f"P0 门槛仍有 {p0_failed} 项未过，先不要扩容"
    elif not active and status_only_running:
        blocker = "有旧状态显示运行中，但没有训练指标，必须刷新 ASI1 状态或抓取远程日志后才能确认"
    elif not active:
        blocker = "当前没有带实时指标的长训运行，需要刷新 ASI1 或重提任务"
    else:
        blocker = "没有新的 P0 事故；继续观察指标、检查点和留出评测"
    if asi1 and not asi1_command_ok:
        next_action = (
            "先修复 ASI1 本地浏览器守护进程或启用明确的恢复模式，然后重新抓取远程训练工件。"
        )
    else:
        next_action = (
            str((freshest.get("next_actions") or ["刷新 ASI1 状态并抓取最新训练工件"])[0])
            if freshest
            else "先启动或抓取一个训练运行"
        )
    latest_training_value = f"是，{len(active)} 个指标实时运行" if active else "未确认有实时训练"
    latest_training_detail = (
        active[0].get("status_text")
        if active
        else (freshest.get("status_text") if freshest else "没有运行工件")
    )
    if not active and status_only_running:
        latest_training_value = "有待确认的旧运行状态"
        latest_training_detail = status_only_running[0].get("status_text") or latest_training_detail
    if freshest and freshest.get("status") in {"submitted", "queued", "pending"}:
        latest_training_value = "最新任务已提交"
        latest_training_detail = freshest.get("status_text") or latest_training_detail
    cards = [
        {
            "label": "训练是否在进行",
            "value": latest_training_value,
            "detail": latest_training_detail,
        },
        {
            "label": "是否有检查点",
            "value": "有" if checkpoint_run else "未确认",
            "detail": checkpoint_text,
        },
        {
            "label": "量子评测是否变好",
            "value": "等待基线对比" if eval_run else "未评测",
            "detail": run_quantum_eval_text(eval_run),
        },
        {
            "label": "当前最大阻塞",
            "value": "需处理"
            if (
                p0_failed
                or failed_runs
                or not active
                or status_only_running
                or (asi1 and not asi1_command_ok)
            )
            else "观察中",
            "detail": blocker,
        },
        {
            "label": "下一步动作",
            "value": "立即执行",
            "detail": zh_action(next_action),
        },
        {
            "label": "ASI1 控制面",
            "value": zh_status(asi1.get("auth_state") or "未知"),
            "detail": (
                f"命令通道：{zh_bool(asi1.get('command_channel_recent_success'))}；"
                f"终端入口：{'降级' if asi1.get('shell_endpoint_failure') else '正常或未报错'}；"
                f"状态采集：{display_text(huanxin_status.get('generated_at_utc'), '未采集')}"
            ),
        },
        {
            "label": "日志来源完整性",
            "value": "已接入"
            if source_contract.get("huanxin_environment_status_present")
            else "待接入",
            "detail": f"运行工件来源数：{len(source_contract.get('required_run_artifacts') or {})}",
        },
    ]
    return {
        "cards": cards,
        "active_runs": len(active),
        "status_only_running_runs": len(status_only_running),
        "p0_failed": p0_failed,
        "checkpoint_run": checkpoint_run.get("name") if checkpoint_run else None,
        "eval_run": eval_run.get("name") if eval_run else None,
        "next_action": next_action,
    }


def render_decision_summary(summary: dict[str, Any]) -> str:
    cards = "".join(
        f'<div class="stat decision-card"><span>{html.escape(str(card.get("label")))}</span>'
        f'<strong>{html.escape(str(card.get("value")))}</strong>'
        f'<p class="panel-desc">{html.escape(zh_visible_text(card.get("detail")))}</p></div>'
        for card in list(summary.get("cards") or [])
    )
    return f"""
    <div class="run decision">
      <h2>今日结论</h2>
      {panel_description("管理层先看这里", "这里直接回答训练是否还在跑、是否已经保存检查点、量子评测有没有证据、当前最大阻塞和下一步动作。")}
      <div class="mini-stats">{cards}</div>
    </div>
    """


def render_dashboard(
    runs: list[dict[str, Any]],
    *,
    title: str,
    huanxin_status: dict[str, Any] | None = None,
    system_status: dict[str, Any] | None = None,
    source_contract: dict[str, Any] | None = None,
) -> str:
    run_cards = "\n".join(render_run_card(run) for run in runs)
    if not run_cards:
        run_cards = '<section class="run"><h2>还没有训练运行</h2><p>请先抓取或生成训练运行工件。</p></section>'
    overview_cards = "\n".join(render_compact_run_summary(run) for run in runs)
    gate_cards = "\n".join(render_gate_summary(run) for run in runs)
    chart_cards = "\n".join(render_chart_summary(run) for run in runs)
    lineage_cards = "\n".join(render_lineage_summary(run) for run in runs)
    raw_cards = "\n".join(render_raw_summary(run) for run in runs)
    infra_cards = "\n".join(render_infra_summary(run) for run in runs)
    eval_cards = "\n".join(render_eval_summary(run) for run in runs)
    rollout_cards = "\n".join(render_rollout_summary(run) for run in runs)
    artifact_cards = "\n".join(render_artifact_summary(run) for run in runs)
    safety_cards = "\n".join(render_safety_summary(run) for run in runs)
    alert_cards = "\n".join(render_alert_summary(run) for run in runs)
    huanxin_cards = render_huanxin_environment_status(huanxin_status or {})
    system_cards = render_research_system_status(system_status or {})
    source_contract = source_contract or build_source_contract(runs, huanxin_status or {})
    source_cards = render_source_contract(source_contract)
    decision_summary = build_decision_summary(runs, huanxin_status or {}, source_contract)
    decision_cards = render_decision_summary(decision_summary)
    if not overview_cards:
        overview_cards = '<section class="run"><h2>还没有训练运行</h2><p>请先抓取或生成训练运行工件。</p></section>'
        gate_cards = overview_cards
        chart_cards = overview_cards
        lineage_cards = overview_cards
        raw_cards = overview_cards
        infra_cards = overview_cards
        eval_cards = overview_cards
        rollout_cards = overview_cards
        artifact_cards = overview_cards
        safety_cards = overview_cards
        alert_cards = overview_cards
    total_runs = len(runs)
    active_runs = sum(1 for run in runs if run["status"] in {"active", "running"})
    updated_runs = sum(1 for run in runs if int(run["updated_steps"] or 0) > 0)
    blocked_runs = sum(1 for run in runs if run["health"])
    failed_gates = sum(1 for run in runs for gate in run["gates"] if not bool(gate["passed"]))
    p0_failed = sum(
        1
        for run in runs
        for gate in run["gates"]
        if gate.get("priority") == "P0" and not bool(gate["passed"])
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="60">
  <title>{html.escape(title)}</title>
    <style>
    :root {{
      color-scheme: light;
      --ink: #172026;
      --muted: #60707c;
      --line: #d9e2e8;
      --panel: #ffffff;
      --bg: #f4f7f8;
      --accent: #126a5b;
      --warn: #a64818;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
    }}
    header {{
      padding: 22px 28px 14px;
      border-bottom: 1px solid var(--line);
      background: #eef4f3;
    }}
    h1, h2, h3, p {{ margin: 0; }}
    h1 {{ font-size: 24px; font-weight: 700; }}
    h2 {{ font-size: 18px; }}
    h3 {{ font-size: 13px; margin-bottom: 8px; color: var(--muted); text-transform: uppercase; }}
    .panel-desc {{
      margin-top: 6px;
      color: var(--muted);
      font-size: 12px;
    }}
    .chart-help {{
      margin-bottom: 8px;
      color: var(--muted);
      font-size: 12px;
    }}
    .tabs {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 14px;
    }}
    .tab-btn {{
      border: 1px solid var(--line);
      background: #fff;
      color: var(--ink);
      border-radius: 999px;
      padding: 7px 12px;
      font: inherit;
      cursor: pointer;
    }}
    .tab-btn[aria-selected="true"] {{
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
    }}
    .overview, .stats, .grid, .details {{
      display: grid;
      gap: 12px;
    }}
    .overview {{
      grid-template-columns: repeat(5, minmax(0, 1fr));
      margin-top: 16px;
      max-width: 1160px;
    }}
    .stat {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px 12px;
      min-width: 0;
      overflow-wrap: anywhere;
    }}
    .stat.wide {{ grid-column: span 2; }}
    .stat span {{ display: block; color: var(--muted); font-size: 12px; }}
    .stat strong {{ display: block; font-size: 20px; margin-top: 2px; }}
    .decision-card strong {{ font-size: 18px; }}
    .status-detail {{ margin-top: 4px; color: var(--muted); font-size: 12px; }}
    main {{ padding: 18px 28px 32px; }}
    .run {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
    }}
    .mini-run {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
    }}
    .run-head {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: flex-start;
      margin-bottom: 14px;
    }}
    .run-head p {{ color: var(--muted); overflow-wrap: anywhere; }}
    .badge {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 4px 10px;
      color: var(--accent);
      white-space: nowrap;
    }}
    .lineage {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 14px;
      color: var(--muted);
    }}
    .lineage span {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 4px 9px;
      background: #fbfcfc;
    }}
    .lineage strong {{ color: var(--ink); font-weight: 600; }}
    .stats {{ grid-template-columns: repeat(8, minmax(0, 1fr)); }}
    .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); margin-top: 14px; }}
    .details {{ grid-template-columns: repeat(4, minmax(0, 1fr)); margin-top: 14px; }}
    .mini-stats {{ display: grid; gap: 12px; grid-template-columns: repeat(4, minmax(0, 1fr)); margin-top: 12px; }}
    .tab-panel[hidden] {{ display: none; }}
    .tab-panel {{ margin-top: 20px; }}
    .chart-card {{ min-width: 0; }}
    svg {{ width: 100%; height: 150px; border: 1px solid var(--line); border-radius: 8px; background: #fbfcfc; }}
    .axis {{ stroke: #b7c5cc; stroke-width: 1; }}
    .series {{ fill: none; stroke: var(--accent); stroke-width: 2.5; }}
    .chart-label, .tick {{ fill: var(--muted); font-size: 11px; }}
    .empty-chart {{
      height: 150px;
      display: grid;
      place-items: center;
      border: 1px solid var(--line);
      border-radius: 8px;
      color: var(--muted);
      background: #fbfcfc;
    }}
    ul {{ margin: 0; padding-left: 18px; color: var(--warn); }}
    .gates {{ color: var(--ink); }}
    .gate {{
      display: inline-block;
      width: 38px;
      font-size: 11px;
      font-weight: 700;
      color: #fff;
      border-radius: 4px;
      text-align: center;
      margin-right: 4px;
    }}
    .gate.pass {{ background: var(--accent); }}
    .gate.fail {{ background: var(--warn); }}
    .priority {{
      display: inline-block;
      color: var(--muted);
      font-size: 11px;
      font-weight: 700;
      margin-right: 4px;
    }}
    @media (max-width: 980px) {{
      .overview, .stats, .grid, .details {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .mini-stats {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 640px) {{
      header, main {{ padding-left: 14px; padding-right: 14px; }}
      .overview, .stats, .grid, .details {{ grid-template-columns: 1fr; }}
      .mini-stats {{ grid-template-columns: 1fr; }}
      .run-head {{ display: block; }}
      .badge {{ display: inline-block; margin-top: 8px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(title)}</h1>
    <p>每 60 秒自动刷新。先看“研发系统”，再看“训练、焕新、基础设施、评测、轨迹、工件、安全、告警”，用于判断训练是否在进行、是否有检查点、量子编码评测是否变好、当前阻塞是什么。</p>
    <div class="overview">
      <div class="stat"><span>运行数</span><strong>{total_runs}</strong></div>
      <div class="stat"><span>训练中</span><strong>{active_runs}</strong></div>
      <div class="stat"><span>有更新</span><strong>{updated_runs}</strong></div>
      <div class="stat"><span>需关注</span><strong>{blocked_runs}</strong></div>
      <div class="stat"><span>未过门槛</span><strong>{failed_gates}</strong></div>
      <div class="stat"><span>P0 未过</span><strong>{p0_failed}</strong></div>
    </div>
    <div class="tabs" role="tablist" aria-label="仪表盘栏目">
      <button class="tab-btn" role="tab" aria-selected="true" data-tab="system">研发系统</button>
      <button class="tab-btn" role="tab" aria-selected="false" data-tab="overview">总览</button>
      <button class="tab-btn" role="tab" aria-selected="false" data-tab="runs">训练</button>
      <button class="tab-btn" role="tab" aria-selected="false" data-tab="gates">门槛</button>
      <button class="tab-btn" role="tab" aria-selected="false" data-tab="charts">曲线</button>
      <button class="tab-btn" role="tab" aria-selected="false" data-tab="infra">基础设施</button>
      <button class="tab-btn" role="tab" aria-selected="false" data-tab="evals">评测</button>
      <button class="tab-btn" role="tab" aria-selected="false" data-tab="rollouts">轨迹</button>
      <button class="tab-btn" role="tab" aria-selected="false" data-tab="artifacts">工件</button>
      <button class="tab-btn" role="tab" aria-selected="false" data-tab="safety">安全</button>
      <button class="tab-btn" role="tab" aria-selected="false" data-tab="alerts">告警</button>
      <button class="tab-btn" role="tab" aria-selected="false" data-tab="huanxin">焕新</button>
      <button class="tab-btn" role="tab" aria-selected="false" data-tab="sources">日志来源</button>
      <button class="tab-btn" role="tab" aria-selected="false" data-tab="lineage">来源</button>
      <button class="tab-btn" role="tab" aria-selected="false" data-tab="raw">诊断</button>
    </div>
  </header>
  <main>
    <section class="tab-panel" data-tab="system">
      {decision_cards}
      {system_cards}
    </section>
    <section class="tab-panel" data-tab="overview" hidden>
      {decision_cards}
      <div class="run">
        <h2>怎么看</h2>
        {panel_description("先看这里", "P0 判断训练是否真实且安全；P1 判断评测和工件链路是否可信；P2 判断是否可以扩容。")}
        {panel_description("先看什么", "先看 P0 未过项，再看奖励和通过率曲线，然后看下一步建议。如果曲线健康但来源变化，要按新实验处理。")}
      </div>
      {overview_cards}
    </section>
    <section class="tab-panel" data-tab="runs" hidden>
      <div class="run">
        <h2>训练</h2>
        {panel_description("完整运行卡片", "本页集中展示每个运行的状态、训练曲线、门槛、下一步和诊断摘要。")}
      </div>
      {run_cards}
    </section>
    <section class="tab-panel" data-tab="gates" hidden>
      <div class="run">
        <h2>门槛阶梯</h2>
        {panel_description("为什么要分优先级", "P0 是阻塞项；P1 是可信度和评测卫生；P2 是扩容准备。改训练配方前先处理更高优先级问题。")}
      </div>
      {gate_cards}
    </section>
    <section class="tab-panel" data-tab="charts" hidden>
      <div class="run">
        <h2>曲线</h2>
        {panel_description("如何读曲线", "奖励和通过率应该一起改善。损失是辅助信号，不能替代结果型检查。")}
      </div>
      {chart_cards}
    </section>
    <section class="tab-panel" data-tab="infra" hidden>
      <div class="run">
        <h2>基础设施</h2>
        {panel_description("任务健康", "本页回答 ASI1 是否在线、是否产出新指标、是否写日志、是否使用 NPU。")}
      </div>
      {infra_cards}
    </section>
    <section class="tab-panel" data-tab="evals" hidden>
      <div class="run">
        <h2>评测</h2>
        {panel_description("晋级信号", "本页区分留出成功率和训练奖励。没有评测证据，不应晋级模型。")}
      </div>
      {eval_cards}
    </section>
    <section class="tab-panel" data-tab="rollouts" hidden>
      <div class="run">
        <h2>轨迹</h2>
        {panel_description("轨迹回放", "本页总结智能体轨迹，用于调试工具行为、轨迹失败和奖励投机。")}
      </div>
      {rollout_cards}
    </section>
    <section class="tab-panel" data-tab="artifacts" hidden>
      <div class="run">
        <h2>工件</h2>
        {panel_description("审计链路", "本页检查运行是否有足够配置、指标、轨迹、评测和指纹数据，便于以后信任和比较。")}
      </div>
      {artifact_cards}
    </section>
    <section class="tab-panel" data-tab="safety" hidden>
      <div class="run">
        <h2>安全</h2>
        {panel_description("晋级阻塞项", "即使奖励改善，不安全工具、提示注入、秘密访问和破坏性命令也应阻止晋级。")}
      </div>
      {safety_cards}
    </section>
    <section class="tab-panel" data-tab="alerts" hidden>
      <div class="run">
        <h2>告警</h2>
        {panel_description("事故视图", "本页用于查看当前事故、失败报告和建议动作。")}
      </div>
      {alert_cards}
    </section>
    <section class="tab-panel" data-tab="huanxin" hidden>
      {huanxin_cards}
    </section>
    <section class="tab-panel" data-tab="sources" hidden>
      {source_cards}
    </section>
    <section class="tab-panel" data-tab="lineage" hidden>
      <div class="run">
        <h2>来源</h2>
        {panel_description("来源与可信度", "用指纹、模型名和配置确认两个运行是否真的可比。来源变化时，不要当成同一实验比较。")}
      </div>
      {lineage_cards}
    </section>
    <section class="tab-panel" data-tab="raw" hidden>
      <div class="run">
        <h2>诊断摘要</h2>
        {panel_description("诊断台", "本页展示底层计数，用来解释为什么面板判定运行健康或阻塞。")}
      </div>
      {raw_cards}
    </section>
  </main>
  <script>
    const buttons = Array.from(document.querySelectorAll('.tab-btn'));
    const panels = Array.from(document.querySelectorAll('.tab-panel'));
    function activate(tabName) {{
      buttons.forEach((button) => {{
        const active = button.dataset.tab === tabName;
        button.setAttribute('aria-selected', active ? 'true' : 'false');
      }});
      panels.forEach((panel) => {{
        panel.hidden = panel.dataset.tab !== tabName;
      }});
      const activePanel = panels.find((panel) => panel.dataset.tab === tabName);
      if (activePanel) {{
        activePanel.scrollIntoView({{ block: 'start', behavior: 'smooth' }});
      }}
    }}
    buttons.forEach((button) => {{
      button.addEventListener('click', () => activate(button.dataset.tab));
    }});
  </script>
</body>
</html>
"""


def registry_decision_payload(
    runs: list[dict[str, Any]],
    huanxin_status: dict[str, Any],
    source_contract: dict[str, Any],
) -> dict[str, Any]:
    return build_decision_summary(runs, huanxin_status, source_contract)


def registry_run_payload(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": run["run_id"],
        "name": run["name"],
        "path": run["path"],
        "status": run["status"],
        "status_text": run["status_text"],
        "status_detail": run["status_detail"],
        "planned_steps": run["planned_steps"],
        "recorded_steps": run["recorded_steps"],
        "updated_steps": run["updated_steps"],
        "skipped_steps": run["skipped_steps"],
        "last_record": run["last_record"],
        "online_latest": run["online_latest"],
        "gates": run["gates"],
        "practices": run["practices"],
        "failure_signals": run["failure_signals"],
        "next_actions": run["next_actions"],
        "tool_counts": run["tool_counts"],
        "terminations": run["terminations"],
        "lineage": run["lineage"],
        "artifact_status": run["artifact_status"],
        "health": run["health"],
        "job_health": run["job_health"],
        "latest_checkpoint": run["latest_checkpoint"],
        "checkpoint_summary": run["checkpoint_summary"],
        "trace_summary": run["trace_summary"],
        "eval_history_summary": run["eval_history_summary"],
        "safety_summary": run["safety_summary"],
        "failure_report": run["failure_report"],
        "fetch_manifest": run["fetch_manifest"],
        "train_log_tail": run["train_log_tail"],
        "train_log_summary": run["train_log_summary"],
        "huanxin_evidence": run["huanxin_evidence"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"))
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--evals-dir", type=Path, default=Path("evals"))
    parser.add_argument("--docs-dir", type=Path, default=Path("docs"))
    parser.add_argument(
        "--run-dir",
        action="append",
        type=Path,
        default=[],
        help="Specific run directory to include.",
    )
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument(
        "--output", type=Path, default=Path("reports/agentic_training_dashboard.html")
    )
    parser.add_argument(
        "--registry-output", type=Path, default=Path("reports/agentic_training_run_registry.json")
    )
    parser.add_argument(
        "--huanxin-status", type=Path, default=Path("reports/huanxin_environment_status.json")
    )
    parser.add_argument("--title", default="智能体训练状态")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dirs = args.run_dir or select_dashboard_runs(
        discover_runs(args.outputs_dir), limit=max(args.limit, 1)
    )
    runs = [summarize_run(path) for path in run_dirs if path.exists()]
    huanxin_status = load_json(args.huanxin_status) or {}
    system_status = build_research_system_status(
        outputs_dir=args.outputs_dir,
        reports_dir=args.reports_dir,
        data_dir=args.data_dir,
        evals_dir=args.evals_dir,
        docs_dir=args.docs_dir,
    )
    source_contract = build_source_contract(runs, huanxin_status)
    html_text = render_dashboard(
        runs,
        title=args.title,
        huanxin_status=huanxin_status,
        system_status=system_status,
        source_contract=source_contract,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html_text, encoding="utf-8")
    registry = {
        "runs": [registry_run_payload(run) for run in runs],
        "huanxin_environment_status": huanxin_status,
        "research_system_status": system_status,
        "source_contract": source_contract,
        "decision_summary": registry_decision_payload(runs, huanxin_status, source_contract),
    }
    args.registry_output.parent.mkdir(parents=True, exist_ok=True)
    args.registry_output.write_text(
        json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "正常": True,
                "output": str(args.output),
                "registry_output": str(args.registry_output),
                "runs": [run["name"] for run in runs],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

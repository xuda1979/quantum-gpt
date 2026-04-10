#!/usr/bin/env python3
"""Generate and optionally execute one autonomous R&D cycle plan."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import os

ROOT = Path(__file__).resolve().parents[1]
import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.runtime_python import resolve_python_interpreter

REPORTS_DIR = ROOT / "reports"
ARTIFACTS_DIR = ROOT / "artifacts"
PAPERS_INDEX = ROOT / "research" / "papers" / "index.json"
DOWNLOAD_ACTIVE_WINDOW_SECONDS = 300
GEMMA_LOCAL_MIN_PYTHON = "3.10"


@dataclass(frozen=True)
class TargetSpec:
    target_id: str
    model_id: str
    audit_artifact: str
    local_model_dir: str
    train_file: str
    eval_file: str
    manifest_file: str
    benchmark_file: str
    eval_run_dir: str
    expected_family_substring: str
    readiness_note: str
    fallback_target_id: str | None = None


TARGETS: dict[str, TargetSpec] = {
    "gemma4-26b-a4b-it": TargetSpec(
        target_id="gemma4-26b-a4b-it",
        model_id="google/gemma-4-26B-A4B-it",
        audit_artifact="artifacts/model-source-audit-gemma4-26b-a4b-it.json",
        local_model_dir="models/gemma-4-26B-A4B-it",
        train_file="data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl",
        eval_file="data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl",
        manifest_file="data/generated/omnicoder-quantum-generalization-holdout-v1/manifest.json",
        benchmark_file="evals/benchmarks/quantum_generalization_holdout_v1.txt",
        eval_run_dir="evals/runs/omnicoder-quantum-generalization-holdout-v1-clean",
        expected_family_substring="gemma",
        readiness_note="Gemma 4 26B-A4B-it MoE is now the preferred weekend-demo target because it is smaller and better aligned with expert-specific tuning than the abandoned 31B path.",
        fallback_target_id="omnicoder9b",
    ),
    "gemma4-31b-it": TargetSpec(
        target_id="gemma4-31b-it",
        model_id="google/gemma-4-31B-it",
        audit_artifact="artifacts/model-source-audit-gemma4-31b-it.json",
        local_model_dir="models/gemma-4-31B-it",
        train_file="data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl",
        eval_file="data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl",
        manifest_file="data/generated/omnicoder-quantum-generalization-holdout-v1/manifest.json",
        benchmark_file="evals/benchmarks/quantum_generalization_holdout_v1.txt",
        eval_run_dir="evals/runs/omnicoder-quantum-generalization-holdout-v1-clean",
        expected_family_substring="gemma",
        readiness_note="Gemma 4 31B-it is now the preferred next finetuning target, but remote training remains gated on runtime, conditional-generation backend readiness, and a verified transfer/download path.",
        fallback_target_id="omnicoder9b",
    ),
    "gemma4-e2b-it": TargetSpec(
        target_id="gemma4-e2b-it",
        model_id="google/gemma-4-E2B-it",
        audit_artifact="artifacts/model-source-audit-gemma4-e2b-it.json",
        local_model_dir="models/gemma-4-E2B-it",
        train_file="data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl",
        eval_file="data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl",
        manifest_file="data/generated/omnicoder-quantum-generalization-holdout-v1/manifest.json",
        benchmark_file="evals/benchmarks/quantum_generalization_holdout_v1.txt",
        eval_run_dir="evals/runs/omnicoder-quantum-generalization-holdout-v1-clean",
        expected_family_substring="gemma",
        readiness_note="Gemma 4 is the next finetuning target, but remote training remains gated on runtime and conditional-generation backend readiness.",
        fallback_target_id="omnicoder9b",
    ),
    "gemma4-e4b-it": TargetSpec(
        target_id="gemma4-e4b-it",
        model_id="google/gemma-4-E4B-it",
        audit_artifact="artifacts/model-source-audit-gemma4-e4b-it.json",
        local_model_dir="models/gemma-4-E4B-it",
        train_file="data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl",
        eval_file="data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl",
        manifest_file="data/generated/omnicoder-quantum-generalization-holdout-v1/manifest.json",
        benchmark_file="evals/benchmarks/quantum_generalization_holdout_v1.txt",
        eval_run_dir="evals/runs/omnicoder-quantum-generalization-holdout-v1-clean",
        expected_family_substring="gemma",
        readiness_note="Gemma 4 E4B-it is the larger next-target variant, but it is still blocked by local runtime/backend readiness.",
        fallback_target_id="omnicoder9b",
    ),
    "omnicoder9b": TargetSpec(
        target_id="omnicoder9b",
        model_id="Tesslate/OmniCoder-9B",
        audit_artifact="artifacts/model-source-audit-omnicoder9b.json",
        local_model_dir="models/OmniCoder-9B",
        train_file="data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl",
        eval_file="data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl",
        manifest_file="data/generated/omnicoder-quantum-generalization-holdout-v1/manifest.json",
        benchmark_file="evals/benchmarks/quantum_generalization_holdout_v1.txt",
        eval_run_dir="evals/runs/omnicoder-quantum-generalization-holdout-v1-clean",
        expected_family_substring="qwen",
        readiness_note="OmniCoder 9B is the current verified fallback lane for productive ai2 iteration while Gemma 4 remains transfer- or backend-blocked.",
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=sorted(TARGETS), default="omnicoder9b")
    parser.add_argument("--report-prefix", default="autonomous_rd_cycle")
    parser.add_argument("--run-local-gates", action="store_true")
    parser.add_argument("--run-gemma-audit", action="store_true")
    parser.add_argument("--run-gemma-runtime-bootstrap", action="store_true")
    parser.add_argument("--run-gemma-smoke", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=REPORTS_DIR)
    parser.add_argument("--artifact-dir", type=Path, default=ARTIFACTS_DIR)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def path_exists(path_str: str) -> bool:
    return (ROOT / path_str).exists()


def _format_size(num_bytes: int) -> str:
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024.0 or unit == "TB":
            if unit == "B":
                return f"{int(value)}{unit}"
            return f"{value:.1f}{unit}"
        value /= 1024.0
    return f"{num_bytes}B"


def _format_percent(ratio: float) -> str:
    return f"{ratio * 100.0:.1f}%"


def run_command(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    return {
        "command": command,
        "ok": completed.returncode == 0,
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def inspect_snapshot_state(target: TargetSpec) -> dict[str, Any]:
    snapshot_dir = ROOT / target.local_model_dir
    if not snapshot_dir.exists():
        return {
            "exists": False,
            "has_any_files": False,
            "has_weight_files": False,
            "has_incomplete_weight_files": False,
            "present_files": [],
            "incomplete_weight_files": [],
            "snapshot_dir": target.local_model_dir,
        }

    present_files = sorted(
        path.relative_to(snapshot_dir).as_posix()
        for path in snapshot_dir.iterdir()
        if path.is_file()
    )
    weight_files = [
        item for item in present_files if item.endswith((".safetensors", ".bin", ".pt", ".pth"))
    ]
    incomplete_weight_files: list[dict[str, Any]] = []
    incomplete_total_bytes = 0
    most_recent_incomplete_mtime: float | None = None
    download_dir = snapshot_dir / ".cache" / "huggingface" / "download"
    if download_dir.exists():
        for path in sorted(download_dir.glob("*.incomplete")):
            try:
                stat_result = path.stat()
                size_bytes = stat_result.st_size
                mtime = stat_result.st_mtime
            except OSError:
                size_bytes = 0
                mtime = None
            incomplete_total_bytes += size_bytes
            if mtime is not None:
                if most_recent_incomplete_mtime is None or mtime > most_recent_incomplete_mtime:
                    most_recent_incomplete_mtime = mtime
            incomplete_weight_files.append(
                {
                    "path": path.relative_to(snapshot_dir).as_posix(),
                    "size_bytes": size_bytes,
                    "size_human": _format_size(size_bytes),
                    "modified_at_utc": datetime.fromtimestamp(
                        mtime or 0, timezone.utc
                    ).isoformat(),
                }
            )

    total_bytes = 0
    file_count = 0
    for dirpath, _dirnames, filenames in os.walk(snapshot_dir):
        for filename in filenames:
            file_count += 1
            try:
                total_bytes += (Path(dirpath) / filename).stat().st_size
            except OSError:
                continue

    indexed_weight_total_bytes = None
    observed_weight_bytes = incomplete_total_bytes
    index_path = snapshot_dir / "model.safetensors.index.json"
    if index_path.exists():
        try:
            index_payload = json.loads(index_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            index_payload = {}
        metadata = index_payload.get("metadata")
        if isinstance(metadata, dict):
            total_size = metadata.get("total_size")
            if isinstance(total_size, int) and total_size > 0:
                indexed_weight_total_bytes = total_size
    for weight_file in weight_files:
        try:
            observed_weight_bytes += (snapshot_dir / weight_file).stat().st_size
        except OSError:
            continue

    observed_weight_progress_ratio = None
    observed_weight_progress_percent = None
    if indexed_weight_total_bytes:
        observed_weight_progress_ratio = min(1.0, observed_weight_bytes / indexed_weight_total_bytes)
        observed_weight_progress_percent = _format_percent(observed_weight_progress_ratio)

    recent_download_activity = False
    latest_incomplete_age_seconds = None
    if most_recent_incomplete_mtime is not None:
        latest_incomplete_age_seconds = max(
            0.0, datetime.now(timezone.utc).timestamp() - most_recent_incomplete_mtime
        )
        recent_download_activity = latest_incomplete_age_seconds <= DOWNLOAD_ACTIVE_WINDOW_SECONDS

    return {
        "exists": True,
        "has_any_files": bool(present_files),
        "has_weight_files": bool(weight_files),
        "has_incomplete_weight_files": bool(incomplete_weight_files),
        "present_files": present_files,
        "weight_files": weight_files,
        "incomplete_weight_files": incomplete_weight_files,
        "snapshot_dir": target.local_model_dir,
        "total_file_count": file_count,
        "total_size_bytes": total_bytes,
        "total_size_human": _format_size(total_bytes),
        "incomplete_total_bytes": incomplete_total_bytes,
        "incomplete_total_human": _format_size(incomplete_total_bytes),
        "indexed_weight_total_bytes": indexed_weight_total_bytes,
        "indexed_weight_total_human": _format_size(indexed_weight_total_bytes) if indexed_weight_total_bytes else None,
        "observed_weight_bytes": observed_weight_bytes,
        "observed_weight_human": _format_size(observed_weight_bytes),
        "observed_weight_progress_ratio": observed_weight_progress_ratio,
        "observed_weight_progress_percent": observed_weight_progress_percent,
        "recent_download_activity": recent_download_activity,
        "latest_incomplete_age_seconds": latest_incomplete_age_seconds,
    }


def build_subsystem_status(target: TargetSpec) -> list[dict[str, Any]]:
    paper_router_plan = load_paper_router_plan(target)
    default_paper_router_paths = _default_paper_router_paths(target)
    return [
        {
            "name": "dataset_generation",
            "ready": all(
                path_exists(path)
                for path in [
                    "scripts/build_large_template_dataset.py",
                    "scripts/build_mixed_fast_mini.py",
                ]
            ),
            "paths": [
                "scripts/build_large_template_dataset.py",
                "scripts/build_mixed_fast_mini.py",
            ],
        },
        {
            "name": "holdout_integrity",
            "ready": all(path_exists(path) for path in [target.train_file, target.eval_file, target.manifest_file]),
            "paths": [target.train_file, target.eval_file, target.manifest_file, "scripts/verify_holdout_dataset.py"],
        },
        {
            "name": "paper_router_warmup",
            "ready": bool(paper_router_plan is not None and paper_router_plan.get("paper_dataset_ready")),
            "paths": [
                paper_router_plan["command_sheet"] if paper_router_plan is not None else default_paper_router_paths["command_sheet"],
                paper_router_plan["paper_train_file"] if paper_router_plan is not None else default_paper_router_paths["train_file"],
                paper_router_plan["paper_eval_file"] if paper_router_plan is not None else default_paper_router_paths["eval_file"],
                "scripts/build_paper_sft_dataset.py",
                "scripts/render_timeboxed_scaleup_commands.py",
            ],
        },
        {
            "name": "local_eval_gate",
            "ready": path_exists("evals/runner/run_eval.py"),
            "paths": ["evals/runner/run_eval.py"],
        },
        {
            "name": "remote_transport",
            "ready": all(
                path_exists(path)
                for path in [
                    "scripts/push_to_s3.sh",
                    "scripts/ai2_sync_from_s3.sh",
                    "scripts/ai2_push_results_to_s3.sh",
                    "scripts/pull_from_s3.sh",
                    "scripts/ai2_sync_model_from_s3.sh",
                ]
            ),
            "paths": [
                "scripts/push_to_s3.sh",
                "scripts/ai2_sync_from_s3.sh",
                "scripts/ai2_push_results_to_s3.sh",
                "scripts/pull_from_s3.sh",
                "scripts/ai2_sync_model_from_s3.sh",
            ],
        },
        {
            "name": "remote_job_control",
            "ready": all(
                path_exists(path)
                for path in [
                    "scripts/ai2_job.sh",
                    "scripts/queue_ai2_timeboxed_pipeline.sh",
                    "scripts/timeboxed_8npu_pipeline.sh",
                ]
            ),
            "paths": [
                "scripts/ai2_job.sh",
                "scripts/queue_ai2_timeboxed_pipeline.sh",
                "scripts/timeboxed_8npu_pipeline.sh",
            ],
        },
        {
            "name": "research_papers",
            "ready": PAPERS_INDEX.exists(),
            "paths": ["research/papers/index.json", "research/papers/README.md"],
        },
        {
            "name": "gemma_targeting",
            "ready": all(
                path_exists(path)
                for path in [
                    "training/acquire_public_qwen_snapshot.py",
                    "training/verify_qwen_snapshot.py",
                    "research/papers/gemma4_text_path_enablement/paper.md",
                ]
            ),
            "paths": [
                "training/acquire_public_qwen_snapshot.py",
                "training/verify_qwen_snapshot.py",
                "research/papers/gemma4_text_path_enablement/paper.md",
            ],
        },
    ]


def build_stakeholder_questions(target: TargetSpec) -> list[dict[str, str]]:
    questions = [
        {
            "question": "How do we know the eval set is not leaking into training?",
            "answer": "The cycle requires holdout-integrity verification on example_id, task_id, and prompt_family before any remote launch.",
        },
        {
            "question": "What exactly is the next model target?",
            "answer": f"The next target is {target.model_id}, but it is gated by runtime and backend readiness before remote finetuning.",
        },
        {
            "question": "Can the system explain why a direction was abandoned?",
            "answer": "The control plane records explicit blocker, regression, and stop-condition sections in each iteration report.",
        },
        {
            "question": "Where is the evidence for claims made in papers or leadership reports?",
            "answer": "The cycle emits a report, a command sheet, and references to run artifacts and paper files for each iteration.",
        },
        {
            "question": "What is the current blocker to Gemma 4 finetuning?",
            "answer": "ai2 access is repaired, but the local stack still blocks Gemma 4 at runtime bootstrap plus trainer/backend preflight: the newer Transformers runtime must install cleanly, and the current text-only AutoModelForCausalLM path still needs a processor-aware conditional-generation backend.",
        },
        {
            "question": "How much of a large Gemma snapshot is actually present right now?",
            "answer": "The cycle-state artifact now reports indexed total weight bytes, observed downloaded bytes, a progress percentage, and whether incomplete shard activity still looks live or stale.",
        },
        {
            "question": "What is the concrete next MoE-specific run once the Gemma snapshot is verified?",
            "answer": "The controller now tracks a paper-router warmup stage that points at the exact router-adaptation warmup command sheet and the prepared paper-derived dataset counts.",
        },
    ]
    if target.fallback_target_id:
        fallback_target = TARGETS[target.fallback_target_id]
        questions.append(
        {
            "question": "What happens if Gemma stays blocked but we still want productive remote iteration?",
            "answer": f"The control plane can recommend the verified fallback lane `{fallback_target.target_id}` targeting {fallback_target.model_id}, and the fast-iteration launcher profile now keeps that loop short once local eval and holdout integrity have passed.",
        }
    )
    return questions


def build_commands(target: TargetSpec) -> dict[str, str]:
    paper_router_plan = load_paper_router_plan(target)
    default_paper_router_paths = _default_paper_router_paths(target)
    gemma_python_probe_command = (
        "python3 scripts/resolve_python_interpreter.py "
        f"--min-version {GEMMA_LOCAL_MIN_PYTHON}"
    )
    gemma_python_prefix = (
        "PYTHON_BIN=\"$(python3 scripts/resolve_python_interpreter.py "
        f"--min-version {GEMMA_LOCAL_MIN_PYTHON} --print-path)\" && "
    )
    commands = {
        "local_eval_gate": "python3 evals/runner/run_eval.py",
        "holdout_integrity": (
            "python3 scripts/verify_holdout_dataset.py "
            f"--train-file {target.train_file} "
            f"--eval-file {target.eval_file} "
            f"--manifest {target.manifest_file} "
            "--min-eval-count 500 "
            "--require-task-disjoint "
            "--require-prompt-family-disjoint"
        ),
        "gemma_audit": (
            "python3 training/audit_model_source.py "
            f"--model-id {target.model_id} "
            f"--expected-family-substring {target.expected_family_substring}"
        ),
        "gemma_snapshot_acquire": (
            "python3 training/acquire_public_qwen_snapshot.py "
            f"--target {target.target_id} "
            f"--local-dir {target.local_model_dir}"
        ),
        "gemma_snapshot_verify": (
            "python3 training/verify_qwen_snapshot.py "
            f"{target.local_model_dir} "
            f"--expected-substring {Path(target.local_model_dir).name} "
            f"--expected-family-substring {target.expected_family_substring}"
        ),
        "gemma_snapshot_relay": f"scripts/relay_model_snapshot_to_s3.sh {Path(target.local_model_dir).name}",
        "paper_router_plan": default_paper_router_paths["plan_command"],
        "paper_dataset": (
            paper_router_plan["paper_dataset_command"]
            if paper_router_plan is not None
            else build_default_paper_dataset_command(target)
        ),
        "paper_router_warmup": (
            paper_router_plan["paper_router_warmup_command"]
            if paper_router_plan is not None
            else build_default_paper_router_warmup_command(target)
        ),
        "gemma_python_probe": gemma_python_probe_command,
        "gemma_runtime_bootstrap": (
            gemma_python_prefix +
            "\"$PYTHON_BIN\" -m pip install -r training/requirements-gemma4-runtime.txt"
        ),
        "gemma_smoke": (
            gemma_python_prefix +
            "\"$PYTHON_BIN\" training/huanxin_cpu_smoke.py "
            f"--model-name {target.local_model_dir} "
            "--dataset data/seed/splits-auto-seed/train.jsonl "
            "--max-samples 1"
        ),
        "code_sync": "scripts/push_to_s3.sh scripts training evals research data",
        "remote_code_sync": "scripts/ai2_sync_from_s3.sh",
        "remote_model_sync": f"scripts/ai2_sync_model_from_s3.sh {Path(target.local_model_dir).name}",
        "remote_job_queue": (
            "scripts/queue_ai2_timeboxed_pipeline.sh "
            f"--target {target.target_id} "
            "--iteration-profile fast "
            "--visible-devices 6,7 "
            "--nproc-per-node 2 "
            "--required-idle-npus 2 "
            "--stage-only"
        ),
    }
    if target.fallback_target_id:
        commands["fallback_remote_job_queue"] = (
            "scripts/queue_ai2_timeboxed_pipeline.sh "
            f"--target {target.fallback_target_id} "
            "--iteration-profile fast "
            "--visible-devices 6,7 "
            "--nproc-per-node 2 "
            "--required-idle-npus 2 "
            "--stage-only"
        )
    return commands


def build_gates(target: TargetSpec) -> list[dict[str, str]]:
    return [
        {
            "gate": "local_quality_gate",
            "required": "local eval suite green before any remote training action",
            "command_key": "local_eval_gate",
        },
        {
            "gate": "dataset_integrity_gate",
            "required": "train/eval disjointness and size thresholds verified",
            "command_key": "holdout_integrity",
        },
        {
            "gate": "gemma_source_gate",
            "required": f"{target.model_id} auditable from local machine",
            "command_key": "gemma_audit",
        },
        {
            "gate": "gemma_snapshot_gate",
            "required": "Gemma local snapshot exists and is verified before any remote model sync",
            "command_key": "gemma_snapshot_verify",
        },
        {
            "gate": "paper_router_warmup_gate",
            "required": "paper-derived router warmup dataset and exact warmup command are prepared after snapshot verification",
            "command_key": "paper_router_warmup",
        },
        {
            "gate": "gemma_local_python_gate",
            "required": f"local Python >= {GEMMA_LOCAL_MIN_PYTHON} resolved before Gemma runtime/bootstrap smoke",
            "command_key": "gemma_python_probe",
        },
        {
            "gate": "gemma_runtime_bootstrap_gate",
            "required": "Gemma runtime dependencies install cleanly on the resolved local Python path before smoke",
            "command_key": "gemma_runtime_bootstrap",
        },
        {
            "gate": "gemma_trainer_backend_gate",
            "required": "Gemma trainer/backend preflight passes locally before any Huanxin launch",
            "command_key": "gemma_smoke",
        },
        {
            "gate": "remote_launcher_gate",
            "required": "Remote launcher is target-aware for the active Gemma target and guards against premature launch with a concrete preflight blocker",
            "command_key": "remote_job_queue",
        },
    ]


def load_paper_registry() -> list[dict[str, Any]]:
    if not PAPERS_INDEX.exists():
        return []
    return load_json(PAPERS_INDEX).get("papers", [])


def _load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return load_json(path)
    except (OSError, json.JSONDecodeError):
        return None


def _count_jsonl_rows(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as handle:
            return sum(1 for _ in handle)
    except OSError:
        return None


def _default_paper_router_paths(target: TargetSpec) -> dict[str, str]:
    dataset_dir = "data/generated/quantum-paper-router-warmup-v1"
    dataset_name = "quantum_paper_router_warmup"
    return {
        "command_sheet": f"artifacts/{target.target_id}-paper-router-command-sheet.txt",
        "plan_command": (
            "python3 scripts/render_timeboxed_scaleup_commands.py "
            f"--target {target.target_id} "
            f"--output artifacts/{target.target_id}-paper-router-command-sheet.txt"
        ),
        "dataset_dir": dataset_dir,
        "dataset_name": dataset_name,
        "train_file": f"{dataset_dir}/messages/{dataset_name}_messages_train.jsonl",
        "eval_file": f"{dataset_dir}/messages/{dataset_name}_messages_valid.jsonl",
        "output_dir": f"outputs/{target.target_id}-quantum-paper-router-warmup",
    }


def _paper_router_command_sheet_candidates(target: TargetSpec) -> list[str]:
    candidates = [f"artifacts/{target.target_id}-paper-router-command-sheet.txt"]
    if target.target_id.endswith("-it"):
        candidates.append(f"artifacts/{target.target_id[:-3]}-paper-router-command-sheet.txt")
    return candidates


def build_default_paper_dataset_command(target: TargetSpec) -> str:
    paths = _default_paper_router_paths(target)
    return (
        "python3 scripts/build_paper_sft_dataset.py "
        f"paper --output-dir {paths['dataset_dir']} --dataset-name {paths['dataset_name']}"
    )


def build_default_paper_router_warmup_command(target: TargetSpec) -> str:
    paths = _default_paper_router_paths(target)
    return (
        "PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256 "
        "TOKENIZERS_PARALLELISM=false "
        "ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 "
        "torchrun --nproc_per_node=8 training/qwen_sft_peft.py "
        f"--model-name {target.local_model_dir} "
        f"--train-file {paths['train_file']} "
        f"--eval-file {paths['eval_file']} "
        f"--output-dir {paths['output_dir']} "
        "--device npu "
        "--max-length 1024 "
        "--per-device-batch-size 1 "
        "--gradient-accumulation-steps 2 "
        "--learning-rate 1e-4 "
        "--num-epochs 1 "
        "--max-steps 20 "
        "--eval-steps 1000 "
        "--log-steps 5 "
        "--train-on-completions-only "
        "--target-module-regex '(?:^|\\.)(?:router|gate)(?:$|\\.)' "
        "--trainable-param-regex 'lora_'"
    )


def load_paper_router_plan(target: TargetSpec) -> dict[str, Any] | None:
    defaults = _default_paper_router_paths(target)
    command_sheet_rel = None
    command_sheet_path = None
    for candidate in _paper_router_command_sheet_candidates(target):
        candidate_path = ROOT / candidate
        if candidate_path.exists():
            command_sheet_rel = candidate
            command_sheet_path = candidate_path
            break
    if command_sheet_rel is None or command_sheet_path is None:
        return None

    try:
        command_sheet_text = command_sheet_path.read_text(encoding="utf-8")
    except OSError:
        return None

    json_marker = "\n## JSON\n"
    json_payload: dict[str, Any] | None = None
    if json_marker in command_sheet_text:
        raw_json = command_sheet_text.split(json_marker, 1)[1].strip()
        try:
            parsed = json.loads(raw_json)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            json_payload = parsed

    resolved_config = json_payload.get("resolved_config") if isinstance(json_payload, dict) else {}
    if not isinstance(resolved_config, dict):
        resolved_config = {}

    train_file = str(resolved_config.get("paper_train_file") or defaults["train_file"])
    eval_file = str(resolved_config.get("paper_eval_file") or defaults["eval_file"])
    train_rows = _count_jsonl_rows(ROOT / train_file)
    eval_rows = _count_jsonl_rows(ROOT / eval_file)

    return {
        "command_sheet": command_sheet_rel,
        "plan_command": defaults["plan_command"],
        "paper_dataset_command": (
            str(json_payload.get("paper_dataset"))
            if isinstance(json_payload, dict) and json_payload.get("paper_dataset")
            else build_default_paper_dataset_command(target)
        ),
        "paper_router_warmup_command": (
            str(json_payload.get("paper_router_warmup"))
            if isinstance(json_payload, dict) and json_payload.get("paper_router_warmup")
            else build_default_paper_router_warmup_command(target)
        ),
        "paper_dataset_dir": str(resolved_config.get("paper_output_dir") or defaults["dataset_dir"]),
        "paper_train_file": train_file,
        "paper_eval_file": eval_file,
        "paper_train_rows": train_rows,
        "paper_eval_rows": eval_rows,
        "paper_dataset_ready": train_rows is not None and train_rows > 0 and eval_rows is not None and eval_rows > 0,
        "resolved_config": resolved_config,
    }


def build_moe_expert_routing_prep(target: TargetSpec) -> dict[str, Any]:
    snapshot_state = inspect_snapshot_state(target)
    cached_snapshot_verify = load_cached_snapshot_verify_summary(target)
    inspect_output = f"artifacts/{target.target_id}_moe_module_scan.json"
    manifest_output = f"artifacts/{target.target_id}_moe_target_manifest.json"
    paper_router_plan = load_paper_router_plan(target)
    default_router_paths = _default_paper_router_paths(target)
    paper_router_command_sheet = (
        paper_router_plan["command_sheet"] if paper_router_plan is not None else default_router_paths["command_sheet"]
    )
    paper_router_dataset_dir = (
        paper_router_plan["paper_dataset_dir"] if paper_router_plan is not None else default_router_paths["dataset_dir"]
    )
    inspect_output_path = ROOT / inspect_output
    manifest_output_path = ROOT / manifest_output
    inspection_command = (
        "python3 training/inspect_moe_target_modules.py "
        f"--model-name {target.local_model_dir} "
        f"--out {inspect_output} "
        f"--manifest-out {manifest_output}"
    )
    manifest_payload = _load_json_if_exists(manifest_output_path)
    inspect_payload = _load_json_if_exists(inspect_output_path)

    prep = {
        "strategy": "router_warmup_then_frequency_guided_esft",
        "phases": [
            {
                "name": "router_warmup",
                "objective": "Use raw paper-derived domain data to adapt routing before touching experts.",
            },
            {
                "name": "expert_selection",
                "objective": "Use routing-frequency evidence to choose the first bounded expert subset.",
            },
            {
                "name": "expert_refinement",
                "objective": "Run ESFT-style expert-only or expert-priority refinement on curated QA/coding data.",
            },
        ],
        "inspection_command": inspection_command,
        "inspection_output": inspect_output,
        "manifest_output": manifest_output,
        "snapshot_dir": target.local_model_dir,
        "snapshot_state": snapshot_state,
        "paper_router_command_sheet": paper_router_command_sheet,
        "paper_router_dataset_dir": paper_router_dataset_dir,
        "paper_router_ready": bool(
            paper_router_plan is not None
            and paper_router_plan.get("paper_dataset_ready")
            and (ROOT / paper_router_command_sheet).exists()
        ),
    }
    if paper_router_plan is not None:
        prep["paper_router_plan"] = {
            "command_sheet": paper_router_plan["command_sheet"],
            "paper_train_file": paper_router_plan["paper_train_file"],
            "paper_eval_file": paper_router_plan["paper_eval_file"],
            "paper_train_rows": paper_router_plan["paper_train_rows"],
            "paper_eval_rows": paper_router_plan["paper_eval_rows"],
            "plan_command": paper_router_plan["plan_command"],
        }

    if manifest_payload is not None:
        prep.update(
            {
                "state": "manifest_recorded",
                "ready": True,
                "reason": "A MoE target manifest with exact router/expert module names is already recorded for this target.",
                "manifest_summary": {
                    "selection_mode": manifest_payload.get("selection_mode"),
                    "router_module_count": len(manifest_payload.get("router_module_names") or []),
                    "expert_index_pool_size": len(manifest_payload.get("expert_index_pool") or []),
                    "first_pass_expert_budget": manifest_payload.get("first_pass_expert_budget"),
                },
            }
        )
        return prep

    if not snapshot_state["exists"]:
        prep.update(
            {
                "state": "waiting_for_snapshot",
                "ready": False,
                "reason": "The local Gemma snapshot does not exist yet, so MoE router/expert inspection cannot start.",
            }
        )
        return prep

    indexed_weight_total = snapshot_state.get("indexed_weight_total_bytes")
    observed_weight = snapshot_state.get("observed_weight_bytes")
    snapshot_complete = bool(
        snapshot_state["has_weight_files"]
        and indexed_weight_total
        and observed_weight is not None
        and observed_weight >= indexed_weight_total
    )
    if snapshot_complete:
        prep.update(
            {
                "state": "ready_for_inspection",
                "ready": True,
                "reason": "The local Gemma snapshot appears complete enough for exact router/expert name inspection and manifest capture.",
            }
        )
        if cached_snapshot_verify is not None:
            prep["snapshot_verify_evidence"] = cached_snapshot_verify
    elif snapshot_state["has_incomplete_weight_files"]:
        prep.update(
            {
                "state": "waiting_for_snapshot_completion",
                "ready": False,
                "reason": "The local Gemma snapshot is still incomplete, so router/expert inspection should wait for the missing weight shards to finish.",
            }
        )
    elif snapshot_state["has_weight_files"]:
        prep.update(
            {
                "state": "pending_snapshot_verification",
                "ready": False,
                "reason": "Local Gemma weights are present, but the full snapshot still needs offline verification before MoE target inspection is treated as authoritative.",
            }
        )
    else:
        prep.update(
            {
                "state": "waiting_for_weights",
                "ready": False,
                "reason": "Gemma config/tokenizer files are present, but the model weight shards needed for MoE inspection are still missing.",
            }
        )

    if inspect_payload is not None:
        prep["inspection_summary"] = {
            "matched_module_count": inspect_payload.get("matched_module_count"),
            "suggested_router_suffixes": inspect_payload.get("suggested_router_suffixes"),
            "suggested_expert_suffixes": inspect_payload.get("suggested_expert_suffixes"),
        }
    return prep


def remote_launcher_supports_target(target: TargetSpec) -> bool:
    launcher_path = ROOT / "scripts" / "queue_ai2_timeboxed_pipeline.sh"
    if not launcher_path.exists():
        return False
    launcher_text = launcher_path.read_text(encoding="utf-8")
    target_markers = (target.model_id, Path(target.local_model_dir).name)
    if any(marker in launcher_text for marker in target_markers):
        return True
    # The current launcher is still OmniCoder-specific; do not infer Gemma readiness.
    return "OmniCoder-9B" not in launcher_text


def remote_launcher_has_gemma_guard(target: TargetSpec) -> bool:
    launcher_path = ROOT / "scripts" / "queue_ai2_timeboxed_pipeline.sh"
    if not launcher_path.exists():
        return False
    launcher_text = launcher_path.read_text(encoding="utf-8")
    local_name = Path(target.local_model_dir).name
    return (
        local_name in launcher_text
        and "if [[ \"$TARGET\" == gemma4-* ]]; then" in launcher_text
        and "conditional-generation backend" in launcher_text
    )


def summarize_result(result: dict[str, Any]) -> dict[str, Any]:
    summary = {
        "ok": result["ok"],
        "exit_code": result["exit_code"],
    }
    stdout = str(result.get("stdout") or "").strip()
    stderr = str(result.get("stderr") or "").strip()
    if stdout:
        summary["stdout_preview"] = stdout[:240]
    if stderr:
        summary["stderr_preview"] = stderr[:240]
    return summary


def load_cached_audit_summary(target: TargetSpec) -> dict[str, Any] | None:
    audit_path = ROOT / target.audit_artifact
    if not audit_path.exists():
        return None
    try:
        payload = load_json(audit_path)
    except (OSError, json.JSONDecodeError):
        return None
    if payload.get("status") != "ok":
        return None
    if payload.get("model_id") != target.model_id:
        return None
    family_evidence = payload.get("family_evidence")
    if isinstance(family_evidence, dict) and family_evidence.get("matched") is False:
        return None
    return {
        "audit_artifact": target.audit_artifact,
        "timestamp_utc": payload.get("timestamp_utc"),
        "model_id": payload.get("model_id"),
        "config_model_type": payload.get("config_model_type"),
        "config_architectures": payload.get("config_architectures"),
        "pipeline_tag": payload.get("pipeline_tag"),
    }


def load_cached_snapshot_verify_summary(target: TargetSpec) -> dict[str, Any] | None:
    handoff_path = ROOT / f"artifacts/{target.target_id}-local-snapshot-handoff.json"
    if not handoff_path.exists():
        return None
    try:
        payload = load_json(handoff_path)
    except (OSError, json.JSONDecodeError):
        return None
    if payload.get("status") != "ok":
        return None
    if payload.get("model_id") != target.model_id:
        return None
    verify_summary = payload.get("verify_summary")
    if not isinstance(verify_summary, dict):
        return None
    if verify_summary.get("status") != "ok":
        return None
    return {
        "handoff_manifest": handoff_path.relative_to(ROOT).as_posix(),
        "model_id": payload.get("model_id"),
        "snapshot_dir": verify_summary.get("snapshot_dir"),
        "present_weight_files": verify_summary.get("present_weight_files"),
        "indexed_weight_shards": verify_summary.get("indexed_weight_shards"),
        "config_model_type": verify_summary.get("config_model_type"),
        "config_architectures": verify_summary.get("config_architectures"),
        "requires_processor_artifacts": verify_summary.get("requires_processor_artifacts"),
    }


def derive_cycle_state(
    target: TargetSpec,
    commands: dict[str, str],
    execution_results: list[dict[str, Any]],
) -> dict[str, Any]:
    execution_by_name = {result["name"]: result for result in execution_results}
    stages: list[dict[str, Any]] = []
    snapshot_state = inspect_snapshot_state(target)
    paper_router_plan = load_paper_router_plan(target)
    local_python_resolution = resolve_python_interpreter()

    def append_command_stage(name: str, *, blocking_reason: str, success_note: str) -> None:
        result = execution_by_name.get(name)
        if result is None:
            stages.append(
                {
                    "stage": name,
                    "status": "pending",
                    "blocking": True,
                    "command": commands[name],
                    "next_action": commands[name],
                    "reason": blocking_reason,
                }
            )
            return
        status = "passed" if result["ok"] else "blocked"
        stage_payload = {
            "stage": name,
            "status": status,
            "blocking": status != "passed",
            "command": commands[name],
            "result": summarize_result(result),
        }
        if status == "passed":
            stage_payload["reason"] = success_note
        else:
            stage_payload["next_action"] = commands[name]
            stage_payload["reason"] = blocking_reason
        stages.append(stage_payload)

    append_command_stage(
        "local_eval_gate",
        blocking_reason="The full local eval suite must pass before remote Gemma work is credible.",
        success_note="Local eval gate passed in this iteration.",
    )
    append_command_stage(
        "holdout_integrity",
        blocking_reason="Holdout integrity is still unverified for this iteration.",
        success_note="Holdout integrity was verified for this iteration.",
    )
    cached_audit_summary = load_cached_audit_summary(target)
    cached_snapshot_verify_summary = load_cached_snapshot_verify_summary(target)
    gemma_audit_result = execution_by_name.get("gemma_audit")
    if gemma_audit_result is not None and gemma_audit_result["ok"]:
        stages.append(
            {
                "stage": "gemma_audit",
                "status": "passed",
                "blocking": False,
                "command": commands["gemma_audit"],
                "result": summarize_result(gemma_audit_result),
                "reason": "Gemma source audit succeeded for this iteration.",
            }
        )
    elif cached_audit_summary is not None:
        stage_payload = {
            "stage": "gemma_audit",
            "status": "passed",
            "blocking": False,
            "command": commands["gemma_audit"],
            "reason": "Gemma source audit is satisfied by a cached verified local artifact for this target.",
            "evidence": cached_audit_summary,
        }
        if gemma_audit_result is not None:
            stage_payload["result"] = summarize_result(gemma_audit_result)
            stage_payload["reason"] = (
                "Gemma source audit is satisfied by a cached verified local artifact for this target; "
                "the live refresh path failed in this iteration."
            )
        stages.append(stage_payload)
    else:
        append_command_stage(
            "gemma_audit",
            blocking_reason="Gemma source audit has not yet succeeded for this iteration.",
            success_note="Gemma source audit succeeded for this iteration.",
        )

    snapshot_verify = execution_by_name.get("gemma_snapshot_verify")
    if snapshot_verify is not None:
        snapshot_status = "passed" if snapshot_verify["ok"] else "blocked"
        snapshot_stage = {
            "stage": "gemma_snapshot_verify",
            "status": snapshot_status,
            "blocking": snapshot_status != "passed",
            "command": commands["gemma_snapshot_verify"],
            "result": summarize_result(snapshot_verify),
        }
        if snapshot_status != "passed":
            snapshot_stage["next_action"] = commands["gemma_snapshot_verify"]
            snapshot_stage["reason"] = "Local Gemma snapshot exists but verification did not pass."
        else:
            snapshot_stage["reason"] = "Local Gemma snapshot exists and verified."
        stages.append(snapshot_stage)
    elif cached_snapshot_verify_summary is not None:
        stages.append(
            {
                "stage": "gemma_snapshot_verify",
                "status": "passed",
                "blocking": False,
                "command": commands["gemma_snapshot_verify"],
                "reason": "Local Gemma snapshot verification is satisfied by a cached successful handoff artifact for this target.",
                "evidence": cached_snapshot_verify_summary,
            }
        )
    elif snapshot_state["exists"] and snapshot_state["has_weight_files"]:
        stages.append(
            {
                "stage": "gemma_snapshot_verify",
                "status": "pending",
                "blocking": True,
                "command": commands["gemma_snapshot_verify"],
                "next_action": commands["gemma_snapshot_verify"],
                "reason": "Local Gemma snapshot is present but still needs offline verification.",
                "evidence": snapshot_state,
            }
        )
    elif snapshot_state["exists"]:
        reason = "Local Gemma snapshot metadata is present, but model weights are still missing."
        if snapshot_state["has_incomplete_weight_files"]:
            progress = snapshot_state.get("observed_weight_progress_percent")
            if snapshot_state.get("recent_download_activity"):
                reason = (
                    "Local Gemma snapshot acquisition is in flight with recent shard activity, "
                    "but model weights are not fully present or verified yet."
                )
            else:
                reason = (
                    "Local Gemma snapshot acquisition is only partially materialized and recent shard activity is stale, "
                    "so the downloader likely needs a resume/retry before remote sync."
                )
            if progress:
                reason += f" Observed indexed-weight progress is {progress}."
        stage_payload = {
            "stage": "gemma_snapshot_acquire",
            "status": "blocked",
            "blocking": True,
            "command": commands["gemma_snapshot_acquire"],
            "next_action": commands["gemma_snapshot_acquire"],
            "reason": reason,
            "evidence": snapshot_state,
        }
        if snapshot_state["has_incomplete_weight_files"]:
            stage_payload["parallel_action"] = commands["gemma_snapshot_relay"]
        stages.append(stage_payload)
    else:
        stages.append(
            {
                "stage": "gemma_snapshot_acquire",
                "status": "blocked",
                "blocking": True,
                "command": commands["gemma_snapshot_acquire"],
                "next_action": commands["gemma_snapshot_acquire"],
                "reason": "Local Gemma snapshot is missing, so remote sync cannot start yet.",
                "evidence": snapshot_state,
            }
        )

    if target.target_id.startswith("gemma4-"):
        local_python_stage = {
            "stage": "gemma_local_python_gate",
            "command": commands["gemma_python_probe"],
            "evidence": local_python_resolution,
        }
        if local_python_resolution.get("selected_path"):
            local_python_stage["status"] = "passed"
            local_python_stage["blocking"] = False
            local_python_stage["reason"] = (
                "A local Python interpreter meeting the Gemma runtime floor is available."
            )
        else:
            local_python_stage["status"] = "blocked"
            local_python_stage["blocking"] = True
            local_python_stage["next_action"] = commands["gemma_python_probe"]
            reason = (
                f"No local Python >= {GEMMA_LOCAL_MIN_PYTHON} interpreter was found for Gemma runtime bootstrap."
            )
            install_command = local_python_resolution.get("install_command")
            if install_command:
                reason += f" Suggested install command: {install_command}."
            local_python_stage["reason"] = reason
        stages.append(local_python_stage)

        runtime_bootstrap_result = execution_by_name.get("gemma_runtime_bootstrap")
        if runtime_bootstrap_result is None:
            stages.append(
                {
                    "stage": "gemma_runtime_bootstrap",
                    "status": "pending",
                    "blocking": True,
                    "command": commands["gemma_runtime_bootstrap"],
                    "next_action": commands["gemma_runtime_bootstrap"],
                    "reason": "Gemma runtime bootstrap has not yet succeeded on the resolved local Python path.",
                }
            )
        elif runtime_bootstrap_result["ok"]:
            stages.append(
                {
                    "stage": "gemma_runtime_bootstrap",
                    "status": "passed",
                    "blocking": False,
                    "command": commands["gemma_runtime_bootstrap"],
                    "result": summarize_result(runtime_bootstrap_result),
                    "reason": "Gemma runtime bootstrap succeeded on the resolved local Python path.",
                }
            )
        else:
            combined_output = "\n".join(
                part.strip()
                for part in (
                    str(runtime_bootstrap_result.get("stdout") or ""),
                    str(runtime_bootstrap_result.get("stderr") or ""),
                )
                if part and part.strip()
            )
            reason = "Gemma runtime bootstrap failed on the resolved local Python path."
            if "Could not resolve host: github.com" in combined_output:
                reason = (
                    "Gemma runtime bootstrap failed while cloning Hugging Face Transformers from GitHub: "
                    "github.com could not be resolved."
                )
            elif "Empty reply from server" in combined_output:
                reason = (
                    "Gemma runtime bootstrap reached GitHub, but cloning Hugging Face Transformers still failed "
                    "with an empty reply from the server."
                )
            stages.append(
                {
                    "stage": "gemma_runtime_bootstrap",
                    "status": "blocked",
                    "blocking": True,
                    "command": commands["gemma_runtime_bootstrap"],
                    "next_action": commands["gemma_runtime_bootstrap"],
                    "reason": reason,
                    "result": summarize_result(runtime_bootstrap_result),
                }
            )

    append_command_stage(
        "gemma_smoke",
        blocking_reason="Gemma trainer/backend preflight has not yet passed on the local stack.",
        success_note="Gemma trainer/backend preflight passed on the local stack.",
    )

    if target.target_id.startswith("gemma4-"):
        if paper_router_plan is None:
            stages.append(
                {
                    "stage": "paper_router_warmup",
                    "status": "blocked",
                    "blocking": True,
                    "command": commands["paper_router_warmup"],
                    "next_action": commands["paper_router_plan"],
                    "reason": "The paper-router warmup command sheet is not recorded yet for this target, so the next MoE-specific run is not concrete enough to launch.",
                    "evidence": {
                        "command_sheet": _default_paper_router_paths(target)["command_sheet"],
                        "plan_command": commands["paper_router_plan"],
                    },
                }
            )
        elif not paper_router_plan.get("paper_dataset_ready"):
            stages.append(
                {
                    "stage": "paper_router_warmup",
                    "status": "blocked",
                    "blocking": True,
                    "command": commands["paper_router_warmup"],
                    "next_action": commands["paper_dataset"],
                    "reason": "The paper-router warmup dataset is not fully materialized yet, so the raw-paper router adaptation step cannot launch.",
                    "evidence": paper_router_plan,
                }
            )
        else:
            stages.append(
                {
                    "stage": "paper_router_warmup",
                    "status": "pending",
                    "blocking": True,
                    "command": commands["paper_router_warmup"],
                    "next_action": commands["paper_router_warmup"],
                    "reason": "The paper-router warmup command and dataset are ready; after local Gemma runtime preflight clears, S3 code/model sync can launch this exact ai2 router adaptation step.",
                    "evidence": paper_router_plan,
                    "prerequisites": [
                        commands["code_sync"],
                        commands["remote_code_sync"],
                        commands["remote_model_sync"],
                    ],
                }
            )

    remote_ready = remote_launcher_supports_target(target)
    remote_guarded = remote_launcher_has_gemma_guard(target)
    remote_stage = {
        "stage": "remote_launcher_gate",
        "status": "passed" if remote_ready else "blocked",
        "blocking": not remote_ready,
        "command": commands["remote_job_queue"],
        "reason": (
            "Remote launcher is target-aware for Gemma and now exits early with a concrete preflight blocker instead of pretending launch readiness."
            if remote_ready and remote_guarded
            else "Remote launcher is parameterized for the active target."
            if remote_ready
            else "Remote launcher still points at OmniCoder-specific commands, so Gemma remote launch must stay blocked."
        ),
        "evidence": {
            "launcher_path": "scripts/queue_ai2_timeboxed_pipeline.sh",
            "gemma_guard_present": remote_guarded,
        },
    }
    if not remote_ready:
        remote_stage["next_action"] = commands["remote_job_queue"]
    stages.append(remote_stage)

    first_blocking = next((stage for stage in stages if stage["blocking"]), None)
    passed_stages = [stage["stage"] for stage in stages if stage["status"] == "passed"]
    cycle_state = {
        "status": "ready_for_remote_finetune" if first_blocking is None else "blocked",
        "current_stage": first_blocking["stage"] if first_blocking else "complete",
        "last_completed_stage": passed_stages[-1] if passed_stages else None,
        "next_action": first_blocking.get("next_action") if first_blocking else None,
        "stop_reason": first_blocking["reason"] if first_blocking else "All current local preflight stages passed.",
        "ready_for_remote_finetune": first_blocking is None,
        "stages": stages,
    }
    if (
        target.fallback_target_id
        and first_blocking is not None
        and first_blocking["stage"] in {
            "gemma_snapshot_acquire",
            "gemma_snapshot_verify",
            "gemma_local_python_gate",
            "gemma_runtime_bootstrap",
            "gemma_smoke",
        }
        and {"local_eval_gate", "holdout_integrity"} <= set(passed_stages)
    ):
        fallback_target = TARGETS[target.fallback_target_id]
        cycle_state["fallback_ready"] = True
        cycle_state["fallback_target"] = {
            "target_id": fallback_target.target_id,
            "model_id": fallback_target.model_id,
        }
        cycle_state["fallback_next_action"] = commands.get("fallback_remote_job_queue")
        cycle_state["fallback_reason"] = (
            f"{target.model_id} remains blocked at {first_blocking['stage']}, but the verified "
            f"{fallback_target.model_id} lane can keep ai2 iteration moving in parallel."
        )
    else:
        cycle_state["fallback_ready"] = False
    return cycle_state


def evaluate_readiness(target: TargetSpec, cycle_state: dict[str, Any]) -> dict[str, Any]:
    gemma_paper = ROOT / "research" / "papers" / "gemma4_text_path_enablement" / "paper.md"
    autonomous_paper = ROOT / "research" / "papers" / "autonomous_rd_cycle_system" / "paper.md"
    blocker = cycle_state["stop_reason"]
    if cycle_state["current_stage"] == "remote_launcher_gate":
        blocker = "Gemma 4 remote finetuning remains blocked because the remote launcher is still OmniCoder-specific."
    elif cycle_state["current_stage"] == "paper_router_warmup":
        blocker = (
            "The verified Gemma snapshot, paper-router dataset, and warmup command are in place; "
            "sync code/model to ai2 and launch the recorded router warmup."
        )
    return {
        "target": target.target_id,
        "ready_for_remote_finetune": cycle_state["ready_for_remote_finetune"],
        "status": cycle_state["status"],
        "blocker": blocker,
        "current_stage": cycle_state["current_stage"],
        "next_action": cycle_state["next_action"],
        "fallback_ready": cycle_state.get("fallback_ready", False),
        "fallback_next_action": cycle_state.get("fallback_next_action"),
        "evidence_paths": [
            str(gemma_paper.relative_to(ROOT)) if gemma_paper.exists() else "research/papers/gemma4_text_path_enablement/paper.md",
            str(autonomous_paper.relative_to(ROOT)) if autonomous_paper.exists() else "research/papers/autonomous_rd_cycle_system/paper.md",
            "scripts/queue_ai2_timeboxed_pipeline.sh",
            _default_paper_router_paths(target)["command_sheet"],
        ],
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# Autonomous R&D Cycle Report - {payload['timestamp_utc'][:10]}",
        "",
        "## Summary",
        f"- target: `{payload['target']['model_id']}`",
        f"- status: `{payload['readiness']['status']}`",
        f"- current_stage: `{payload['cycle_state']['current_stage']}`",
        f"- blocker: {payload['readiness']['blocker']}",
        f"- next_action: `{payload['cycle_state']['next_action']}`" if payload["cycle_state"]["next_action"] else "- next_action: none",
        f"- fallback_next_action: `{payload['cycle_state']['fallback_next_action']}`"
        if payload["cycle_state"].get("fallback_next_action")
        else "- fallback_next_action: none",
        f"- note: {payload['target']['readiness_note']}",
        "",
        "## Cycle State",
    ]
    for stage in payload["cycle_state"]["stages"]:
        line = f"- `{stage['stage']}`: `{stage['status']}`"
        if stage.get("reason"):
            line += f" - {stage['reason']}"
        lines.append(line)
        if stage.get("next_action"):
            lines.append(f"  next_action: `{stage['next_action']}`")
        evidence = stage.get("evidence")
        if isinstance(evidence, dict):
            if evidence.get("command_sheet"):
                lines.append(f"  evidence_command_sheet: `{evidence['command_sheet']}`")
            if evidence.get("plan_command"):
                lines.append(f"  evidence_plan_command: `{evidence['plan_command']}`")
            if evidence.get("paper_train_file"):
                lines.append(f"  evidence_paper_train_file: `{evidence['paper_train_file']}`")
            if evidence.get("paper_eval_file"):
                lines.append(f"  evidence_paper_eval_file: `{evidence['paper_eval_file']}`")
            if evidence.get("paper_train_rows") is not None:
                lines.append(f"  evidence_paper_train_rows: `{evidence['paper_train_rows']}`")
            if evidence.get("paper_eval_rows") is not None:
                lines.append(f"  evidence_paper_eval_rows: `{evidence['paper_eval_rows']}`")
            if evidence.get("present_files"):
                lines.append(f"  evidence_present_files: `{', '.join(evidence['present_files'])}`")
            if evidence.get("weight_files"):
                lines.append(f"  evidence_weight_files: `{', '.join(evidence['weight_files'])}`")
            if evidence.get("incomplete_weight_files"):
                incomplete_paths = ", ".join(item["path"] for item in evidence["incomplete_weight_files"])
                lines.append(f"  evidence_incomplete_files: `{incomplete_paths}`")
            if evidence.get("total_size_human"):
                lines.append(f"  evidence_total_size: `{evidence['total_size_human']}`")
            if evidence.get("audit_artifact"):
                lines.append(f"  evidence_audit_artifact: `{evidence['audit_artifact']}`")
            if evidence.get("selected_path"):
                lines.append(f"  evidence_selected_python: `{evidence['selected_path']}`")
            if evidence.get("selected_version"):
                lines.append(f"  evidence_selected_python_version: `{evidence['selected_version']}`")
            if evidence.get("install_command"):
                lines.append(f"  evidence_install_command: `{evidence['install_command']}`")
            if evidence.get("timestamp_utc"):
                lines.append(f"  evidence_timestamp_utc: `{evidence['timestamp_utc']}`")
            if evidence.get("indexed_weight_total_human"):
                lines.append(f"  evidence_indexed_weight_total: `{evidence['indexed_weight_total_human']}`")
            if evidence.get("observed_weight_human"):
                lines.append(f"  evidence_observed_weight: `{evidence['observed_weight_human']}`")
            if evidence.get("observed_weight_progress_percent"):
                lines.append(f"  evidence_weight_progress: `{evidence['observed_weight_progress_percent']}`")
            if evidence.get("recent_download_activity") is not None:
                lines.append(
                    f"  evidence_recent_download_activity: `{str(bool(evidence['recent_download_activity'])).lower()}`"
                )
            if evidence.get("latest_incomplete_age_seconds") is not None:
                lines.append(
                    "  evidence_latest_incomplete_age_seconds: "
                    f"`{int(evidence['latest_incomplete_age_seconds'])}`"
                )
        if stage.get("prerequisites"):
            lines.append(
                "  prerequisites: "
                + " | ".join(f"`{command}`" for command in stage["prerequisites"])
            )
        if stage.get("parallel_action"):
            lines.append(f"  parallel_action: `{stage['parallel_action']}`")
    if payload["cycle_state"].get("fallback_ready"):
        lines.extend(
            [
                "",
                "## Fallback Continuation",
                f"- fallback_target: `{payload['cycle_state']['fallback_target']['model_id']}`",
                f"- fallback_reason: {payload['cycle_state']['fallback_reason']}",
                f"- fallback_next_action: `{payload['cycle_state']['fallback_next_action']}`",
            ]
        )
    lines.extend([
        "",
        "## Stakeholder Questions",
    ])
    for item in payload["stakeholder_questions"]:
        lines.append(f"- Q: {item['question']}")
        lines.append(f"  A: {item['answer']}")
    lines.extend(["", "## Subsystems"])
    for subsystem in payload["subsystems"]:
        lines.append(
            f"- `{subsystem['name']}`: {'ready' if subsystem['ready'] else 'missing'} "
            f"({', '.join(subsystem['paths'])})"
        )
    lines.extend(["", "## MoE Expert Routing Prep"])
    moe_prep = payload["moe_expert_routing_prep"]
    lines.append(f"- strategy: `{moe_prep['strategy']}`")
    lines.append(f"- state: `{moe_prep['state']}`")
    lines.append(f"- ready: `{str(bool(moe_prep['ready'])).lower()}`")
    lines.append(f"- reason: {moe_prep['reason']}")
    lines.append(f"- inspection_command: `{moe_prep['inspection_command']}`")
    lines.append(f"- inspection_output: `{moe_prep['inspection_output']}`")
    lines.append(f"- manifest_output: `{moe_prep['manifest_output']}`")
    lines.append(f"- paper_router_dataset_dir: `{moe_prep['paper_router_dataset_dir']}`")
    lines.append(f"- paper_router_command_sheet: `{moe_prep['paper_router_command_sheet']}`")
    lines.append(f"- paper_router_ready: `{str(bool(moe_prep.get('paper_router_ready'))).lower()}`")
    if moe_prep.get("manifest_summary"):
        lines.append(
            f"- manifest_router_module_count: `{moe_prep['manifest_summary'].get('router_module_count')}`"
        )
        lines.append(
            f"- manifest_expert_index_pool_size: `{moe_prep['manifest_summary'].get('expert_index_pool_size')}`"
        )
        lines.append(
            f"- manifest_first_pass_expert_budget: `{moe_prep['manifest_summary'].get('first_pass_expert_budget')}`"
        )
    if moe_prep.get("inspection_summary"):
        lines.append(
            f"- inspection_matched_module_count: `{moe_prep['inspection_summary'].get('matched_module_count')}`"
        )
    if moe_prep.get("paper_router_plan"):
        lines.append(f"- paper_router_train_file: `{moe_prep['paper_router_plan'].get('paper_train_file')}`")
        lines.append(f"- paper_router_eval_file: `{moe_prep['paper_router_plan'].get('paper_eval_file')}`")
        lines.append(f"- paper_router_train_rows: `{moe_prep['paper_router_plan'].get('paper_train_rows')}`")
        lines.append(f"- paper_router_eval_rows: `{moe_prep['paper_router_plan'].get('paper_eval_rows')}`")
    lines.extend(["", "## Gating Commands"])
    for key, command in payload["commands"].items():
        lines.append(f"- `{key}`: `{command}`")
    lines.extend(["", "## Gate Definitions"])
    for gate in payload["gates"]:
        lines.append(f"- `{gate['gate']}`: {gate['required']} (`{gate['command_key']}`)")
    lines.extend(["", "## Research Papers"])
    for paper in payload["papers"]:
        lines.append(f"- `{paper['paper_id']}`: {paper['title']}")
    if payload["execution_results"]:
        lines.extend(["", "## Executed Checks"])
        for result in payload["execution_results"]:
            lines.append(f"- `{result['name']}`: {'ok' if result['ok'] else 'failed'}")
            lines.append(f"  - command: `{result['command']}`")
            if result.get("exit_code") is not None:
                lines.append(f"  - exit_code: `{result['exit_code']}`")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.artifact_dir.mkdir(parents=True, exist_ok=True)

    target = TARGETS[args.target]
    timestamp = datetime.now(timezone.utc).isoformat()
    commands = build_commands(target)
    execution_results: list[dict[str, Any]] = []

    if args.run_local_gates:
        for name in ("local_eval_gate", "holdout_integrity"):
            command = ["bash", "-lc", commands[name]]
            result = run_command(command)
            execution_results.append({"name": name, **result, "command": commands[name]})

    if args.run_gemma_audit:
        result = run_command(["bash", "-lc", commands["gemma_audit"]])
        execution_results.append({"name": "gemma_audit", **result, "command": commands["gemma_audit"]})

    if args.run_gemma_runtime_bootstrap:
        result = run_command(["bash", "-lc", commands["gemma_runtime_bootstrap"]])
        execution_results.append(
            {"name": "gemma_runtime_bootstrap", **result, "command": commands["gemma_runtime_bootstrap"]}
        )

    if args.run_gemma_smoke:
        result = run_command(["bash", "-lc", commands["gemma_smoke"]])
        execution_results.append({"name": "gemma_smoke", **result, "command": commands["gemma_smoke"]})

    cycle_state = derive_cycle_state(target, commands, execution_results)
    payload = {
        "timestamp_utc": timestamp,
        "target": {
            "target_id": target.target_id,
            "model_id": target.model_id,
            "local_model_dir": target.local_model_dir,
            "readiness_note": target.readiness_note,
        },
        "cycle_state": cycle_state,
        "subsystems": build_subsystem_status(target),
        "moe_expert_routing_prep": build_moe_expert_routing_prep(target),
        "stakeholder_questions": build_stakeholder_questions(target),
        "commands": commands,
        "gates": build_gates(target),
        "papers": load_paper_registry(),
        "readiness": evaluate_readiness(target, cycle_state),
        "execution_results": execution_results,
    }

    stem = f"{args.report_prefix}_{target.target_id}_{timestamp[:10]}"
    json_path = args.output_dir / f"{stem}.json"
    md_path = args.output_dir / f"{stem}.md"
    state_path = args.output_dir / f"{stem}_state.json"
    command_sheet_path = args.artifact_dir / f"{stem}_commands.txt"

    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    state_path.write_text(json.dumps(cycle_state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    command_sheet_path.write_text(
        "\n".join(
            [
                "# Autonomous R&D Cycle Command Sheet",
                f"# target: {target.model_id}",
                "",
                *[f"{name}: {command}" for name, command in commands.items()],
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "report_json": str(json_path.resolve()),
                "report_markdown": str(md_path.resolve()),
                "cycle_state_json": str(state_path.resolve()),
                "command_sheet": str(command_sheet_path.resolve()),
                "target": target.model_id,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

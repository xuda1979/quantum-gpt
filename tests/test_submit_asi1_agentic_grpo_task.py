from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "submit_asi1_agentic_grpo_task.sh"


def _dry_run(*args: str) -> list[str]:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return shlex.split(result.stdout.strip())


def test_asi1_agentic_grpo_task_defaults_to_fill_only() -> None:
    command = _dry_run("--artifact-stem", "asi1-grpo-fast-test")

    assert command[:2] == ["node", str(ROOT / "browser-automation" / "huanxin_submit_task_run.js")]
    assert "--submit" not in command

    by_flag = dict(zip(command, command[1:], strict=False))
    assert "name=ASI1" in by_flag["--url"]
    assert by_flag["--task-name"] == "asi1-grpo-fast"
    assert by_flag["--image-name"] == "qwen3.5-27B-35B-122B-397B-031626-zx"
    assert by_flag["--remote-root"] == "/workspace/quantum-gpt"
    assert by_flag["--launcher-script"] == str(SCRIPT)
    assert by_flag["--launcher-arg"] == "__launch-spec"
    assert by_flag["--output-dir"].startswith("outputs/qwen36-35b-a3b-agentic-grpo-asi1-task-fast-")
    assert by_flag["--log-path"].startswith("/tmp/qwen36_35b_a3b_agentic_grpo_asi1_task_fast_")


def test_asi1_agentic_grpo_task_only_submits_when_requested() -> None:
    command = _dry_run("--submit")
    assert "--submit" in command


def test_submit_task_runner_can_disable_auto_codecontents_override() -> None:
    runner = ROOT / "browser-automation" / "huanxin_submit_task_run.js"
    script = (
        "const m = require('./browser-automation/huanxin_submit_task_run.js');"
        "const args = process.argv.slice(1);"
        "const parsed = (() => {"
        "  const out = { autoOverrideCodeContents: process.env.HUANXIN_AUTO_OVERRIDE_CODECONTENTS !== '0' };"
        "  for (let i=0; i<args.length; i++) {"
        "    if (args[i] === '--no-auto-codecontents-override') out.autoOverrideCodeContents = false;"
        "  }"
        "  return out;"
        "})();"
        "console.log(JSON.stringify({"
        "  moduleLoaded: Boolean(m.shouldAutoOverrideCodeContents),"
        "  autoOverrideCodeContents: parsed.autoOverrideCodeContents"
        "}));"
    )
    result = subprocess.run(
        ["node", "-e", script, "--", "--no-auto-codecontents-override"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload == {"moduleLoaded": True, "autoOverrideCodeContents": False}


def test_asi1_agentic_grpo_task_forwards_no_auto_codecontents_override() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={"HUANXIN_AUTO_OVERRIDE_CODECONTENTS": "0"},
    )

    assert result.returncode == 0, result.stderr
    command = shlex.split(result.stdout.strip())
    assert "--no-auto-codecontents-override" in command


def test_asi1_agentic_grpo_task_launch_spec_is_fast_35b_a3b_training() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "ASI1_AGENTIC_TASK_TIMESTAMP": "20260526T000000Z",
            "ASI1_AGENTIC_TASK_REMOTE_ROOT": "/workspace/quantum-gpt",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["remote_root"] == "/workspace/quantum-gpt"
    assert (
        payload["output_dir"]
        == "outputs/qwen36-35b-a3b-agentic-grpo-asi1-task-fast-20260526T000000Z"
    )
    assert (
        payload["log_path"]
        == "/tmp/qwen36_35b_a3b_agentic_grpo_asi1_task_fast_20260526T000000Z.log"
    )
    assert payload["job_name"] == "asi1-agentic-grpo-fast"
    assert payload["compact_command"] == "inline"

    command = payload["remote_command"]
    assert payload["bootstrap_s3"] is False
    assert payload["bootstrap_wheelhouse"] is False
    assert "test -d /root/work/filestorage/Qwen3.6-35B-A3B" in command
    assert "--model-name /root/work/filestorage/Qwen3.6-35B-A3B" in command
    assert "__ASI1_GRPO_BEFORE_TORCHRUN__" in command
    assert "--group-size 8" in command
    assert "--grpo-steps 128" in command
    assert "--max-new-tokens 4096" in command
    assert "--max-seq-length 32768" in command
    assert "--checkpoint-interval-seconds 3600" in command
    assert "--checkpoint-every-steps 0" in command
    assert (
        "--online-eval-benchmark-file evals/benchmarks/quantum_generalization_holdout_v2_hard.txt"
        in command
    )
    assert "--online-eval-every-steps 8" in command
    assert "--online-eval-max-tasks 8" in command

    execution_command = payload["execution_command"]
    assert execution_command.startswith("set -euo pipefail\n")
    assert "python3 -c" in execution_command
    assert "asi1_agentic_grpo_run_inline.b64" in execution_command
    assert "asi1_agentic_grpo_run_inline.sh" in execution_command
    assert "base64.b64decode" in execution_command
    assert "subprocess" not in execution_command
    assert execution_command.endswith("bash /tmp/asi1_agentic_grpo_run_inline.sh")
    assert ">" not in execution_command
    assert "&&" not in execution_command
    assert "," not in execution_command
    assert max(len(line) for line in execution_command.splitlines()) < 430
    assert payload["remote_script_path"] == "/tmp/asi1_agentic_grpo_run_inline.sh"
    assert payload["remote_b64_path"] == "/tmp/asi1_agentic_grpo_run_inline.b64"


def test_asi1_agentic_grpo_task_can_bootstrap_repo_and_wheels() -> None:
    result = subprocess.run(
        [
            "bash",
            str(SCRIPT),
            "--dry-run",
            "__launch-spec",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "ASI1_AGENTIC_TASK_TIMESTAMP": "20260527T000000Z",
            "ASI1_AGENTIC_TASK_REMOTE_ROOT": "/workspace/quantum-gpt",
            "ASI1_AGENTIC_TASK_BOOTSTRAP_S3": "1",
            "ASI1_AGENTIC_TASK_BOOTSTRAP_WHEELHOUSE": "1",
            "ASI1_AGENTIC_TASK_COMPACT_COMMAND": "repo-runner",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["compact_command"] == "repo-runner"
    assert payload["bootstrap_s3"] is True
    assert payload["bootstrap_wheelhouse"] is True
    assert payload["single_line_execution"] is True
    assert payload["execution_command"].startswith("set -euo pipefail\n")
    assert (
        "rclone sync iner:jtdlp-21b4208dde424e96b159362ef49c9c96/software/quantum-gpt /workspace/quantum-gpt"
        not in payload["execution_command"]
    )
    assert "bash scripts/run_asi1_agentic_grpo_from_env.sh" not in payload["execution_command"]
    assert "&&" not in payload["execution_command"]
    assert "," not in payload["execution_command"]
    assert len(payload["execution_command"].splitlines()) > 1
    assert payload["multi_line_execution_command"].startswith("set -euo pipefail\n")
    assert "asi1_agentic_grpo_run.b64" in payload["multi_line_execution_command"]
    assert max(len(line) for line in payload["multi_line_execution_command"].splitlines()) < 2000

    command = payload["remote_command"]
    assert "__ASI1_REPO_RUNNER_BOOT__" in command
    assert "__ASI1_REPO_RUNNER_BEFORE_SYNC__" in command
    assert "__ASI1_REPO_RUNNER_AFTER_SYNC__" in command
    assert "python3 -c" in command
    assert "base64.b64decode" in command
    assert "/tmp/iner-rclone.conf" in command
    assert "mkdir -p /workspace/quantum-gpt" in command
    assert "tools/preseed/rclone-linux-arm64" in command
    assert "downloads.rclone.org/rclone-current-linux-arm64.zip" in command
    assert command.index("downloads.rclone.org/rclone-current-linux-arm64.zip") < command.index(
        "apt-get install -y --no-install-recommends rclone"
    )
    assert (
        "apt-get update && apt-get install -y --no-install-recommends rclone || echo rclone_apt_install_failed"
        in command
    )
    assert "elif command -v apt-get" not in command
    assert "missing_rclone_after_all_bootstraps" in command
    assert "command -v rclone" in command
    assert (
        "rclone sync iner:jtdlp-21b4208dde424e96b159362ef49c9c96/software/quantum-gpt /workspace/quantum-gpt"
        in command
    )
    assert "--exclude 'outputs/**'" in command
    assert "export ASI1_AGENTIC_TASK_BOOTSTRAP_WHEELHOUSE=1" in command
    assert (
        "export ASI1_AGENTIC_TASK_ONLINE_EVAL_BENCHMARK_FILE=evals/benchmarks/quantum_generalization_holdout_v2_hard.txt"
        in command
    )
    assert "export ASI1_AGENTIC_TASK_CHECKPOINT_INTERVAL_SECONDS=3600" in command
    assert "export ASI1_AGENTIC_TASK_RESEARCH_METHODS=" in command
    assert "clause_aware_verifier_reward" in command
    assert "bash scripts/run_asi1_agentic_grpo_from_env.sh" in command


def test_asi1_agentic_grpo_task_can_embed_runtime_bundle_without_network() -> None:
    result = subprocess.run(
        [
            "bash",
            str(SCRIPT),
            "--dry-run",
            "__launch-spec",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "ASI1_AGENTIC_TASK_TIMESTAMP": "20260603T120000Z",
            "ASI1_AGENTIC_TASK_REMOTE_ROOT": "/root/work/quantum-gpt",
            "ASI1_AGENTIC_TASK_COMPACT_COMMAND": "repo-runner",
            "ASI1_AGENTIC_TASK_BOOTSTRAP_S3": "0",
            "ASI1_AGENTIC_TASK_EMBED_RUNTIME_BUNDLE": "1",
            "ASI1_AGENTIC_TASK_GRPO_STEPS": "1",
            "ASI1_AGENTIC_TASK_MAX_NEW_TOKENS": "32",
            "ASI1_AGENTIC_TASK_MAX_SEQ_LENGTH": "512",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["compact_command"] == "repo-runner"
    assert payload["embed_runtime_bundle"] is True
    assert payload["single_line_execution"] is True
    assert "curl -fL" not in payload["remote_command"]
    assert "rclone sync" not in payload["remote_command"]
    assert "downloads.rclone.org" not in payload["remote_command"]
    assert "apt-get install" not in payload["remote_command"]
    assert "__ASI1_REPO_RUNNER_EMBEDDED_BUNDLE_RESTORE__" in payload["remote_command"]
    assert "__ASI1_REPO_RUNNER_AFTER_SYNC__" in payload["remote_command"]
    assert "tar -xzf /tmp/qg_asi1_agentic_grpo_minibundle.tar.gz" in payload["remote_command"]
    assert "bash scripts/run_asi1_agentic_grpo_from_env.sh" in payload["remote_command"]
    assert "," not in payload["execution_command"]
    assert "&&" not in payload["execution_command"]
    assert max(len(line) for line in payload["execution_command"].splitlines()) < 2000


def test_asi1_agentic_grpo_task_can_launch_quantum_first_hard_eval() -> None:
    result = subprocess.run(
        [
            "bash",
            str(SCRIPT),
            "--dry-run",
            "__launch-spec",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "ASI1_AGENTIC_TASK_TIMESTAMP": "20260601T000000Z",
            "ASI1_AGENTIC_TASK_REMOTE_ROOT": "/workspace/quantum-gpt",
            "ASI1_AGENTIC_TASK_BENCHMARK_FILE": "evals/benchmarks/quantum_grpo_training_v5_failure_shape_disjoint.txt",
            "ASI1_AGENTIC_TASK_DOMAIN_FILTER": "quantum",
            "ASI1_AGENTIC_TASK_ONLINE_EVAL_BENCHMARK_FILE": "evals/benchmarks/quantum_generalization_holdout_v2_hard.txt",
            "ASI1_AGENTIC_TASK_CHECKPOINT_INTERVAL_SECONDS": "180",
            "ASI1_AGENTIC_TASK_CHECKPOINT_EVERY_STEPS": "4",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    command = payload["remote_command"]
    assert "--model-name /root/work/filestorage/Qwen3.6-35B-A3B" in command
    assert (
        "--benchmark-file evals/benchmarks/quantum_grpo_training_v5_failure_shape_disjoint.txt"
        in command
    )
    assert "--domain-filter quantum" in command
    assert (
        "--online-eval-benchmark-file evals/benchmarks/quantum_generalization_holdout_v2_hard.txt"
        in command
    )
    assert "--checkpoint-interval-seconds 180" in command
    assert "--checkpoint-every-steps 4" in command
    assert "--training-mode lora" in command
    assert "--lora-rank 64" in command
    assert "--lora-alpha 128" in command
    assert "--target-modules q_proj k_proj v_proj o_proj gate_proj up_proj down_proj" in command


def test_asi1_agentic_grpo_task_can_push_results_to_s3() -> None:
    result = subprocess.run(
        [
            "bash",
            str(SCRIPT),
            "--dry-run",
            "__launch-spec",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "ASI1_AGENTIC_TASK_TIMESTAMP": "20260527T010000Z",
            "ASI1_AGENTIC_TASK_REMOTE_ROOT": "/workspace/quantum-gpt",
            "ASI1_AGENTIC_TASK_PUSH_RESULTS_S3": "1",
            "ASI1_AGENTIC_TASK_COMPACT_COMMAND": "repo-runner",
            "ASI1_AGENTIC_TASK_BOOTSTRAP_S3": "1",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["compact_command"] == "repo-runner"
    assert payload["push_results_s3"] is True
    assert payload["single_line_execution"] is True
    assert payload["execution_command"].startswith("set -euo pipefail\n")
    assert (
        "rclone sync iner:jtdlp-21b4208dde424e96b159362ef49c9c96/software/quantum-gpt /workspace/quantum-gpt"
        not in payload["execution_command"]
    )
    assert "bash scripts/run_asi1_agentic_grpo_from_env.sh" not in payload["execution_command"]
    assert "&&" not in payload["execution_command"]
    assert "," not in payload["execution_command"]
    assert len(payload["execution_command"].splitlines()) > 1
    assert "asi1_agentic_grpo_run.b64" in payload["multi_line_execution_command"]

    command = payload["remote_command"]
    assert "__ASI1_REPO_RUNNER_BOOT__" in command
    assert "tools/preseed/rclone-linux-arm64" in command
    assert "downloads.rclone.org/rclone-current-linux-arm64.zip" in command
    assert command.index("downloads.rclone.org/rclone-current-linux-arm64.zip") < command.index(
        "apt-get install -y --no-install-recommends rclone"
    )
    assert (
        "apt-get update && apt-get install -y --no-install-recommends rclone || echo rclone_apt_install_failed"
        in command
    )
    assert "elif command -v apt-get" not in command
    assert "missing_rclone_after_all_bootstraps" in command
    assert "python3 -c" in command
    assert "base64.b64decode" in command
    assert "/tmp/iner-rclone.conf" in command
    assert "export ASI1_AGENTIC_TASK_PUSH_RESULTS_S3=1" in command
    assert "export ASI1_AGENTIC_TASK_CHECKPOINT_EVERY_STEPS=0" in command
    assert (
        "export ASI1_AGENTIC_TASK_S3_ROOT=iner:jtdlp-21b4208dde424e96b159362ef49c9c96/software/quantum-gpt"
        in command
    )
    assert "bash scripts/run_asi1_agentic_grpo_from_env.sh" in command


def test_asi1_agentic_grpo_task_full_command_keeps_readable_execution_script() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "ASI1_AGENTIC_TASK_TIMESTAMP": "20260527T020000Z",
            "ASI1_AGENTIC_TASK_REMOTE_ROOT": "/workspace/quantum-gpt",
            "ASI1_AGENTIC_TASK_COMPACT_COMMAND": "0",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["compact_command"] == "shell-b64"
    assert payload["execution_command"].startswith("python3 -c ")
    assert "__import__('\"'\"'subprocess'\"'\"')" in payload["execution_command"]
    assert "," not in payload["execution_command"]
    assert "&&" not in payload["execution_command"]
    assert "printf %s " not in payload["execution_command"]
    assert "torchrun --nproc_per_node=8" in payload["remote_command"]


def test_asi1_agentic_grpo_task_raw_command_uses_unwrapped_torchrun() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "ASI1_AGENTIC_TASK_TIMESTAMP": "20260603T000000Z",
            "ASI1_AGENTIC_TASK_REMOTE_ROOT": "/workspace/quantum-gpt",
            "ASI1_AGENTIC_TASK_COMPACT_COMMAND": "raw",
            "ASI1_AGENTIC_TASK_TRAINING_MODE": "native",
            "ASI1_AGENTIC_TASK_GRPO_STEPS": "1",
            "ASI1_AGENTIC_TASK_MAX_NEW_TOKENS": "32",
            "ASI1_AGENTIC_TASK_MAX_SEQ_LENGTH": "512",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["compact_command"] == "raw"
    assert payload["execution_command"].startswith("set -euo pipefail\ncd /workspace/quantum-gpt\n")
    assert "torchrun --nproc_per_node=8" in payload["execution_command"]
    assert "base64.b64decode" not in payload["execution_command"]
    assert len(payload["execution_command"]) < 10000


def test_asi1_agentic_grpo_full_native_command_avoids_huanxin_comma_split() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "ASI1_AGENTIC_TASK_TIMESTAMP": "20260528T140000Z",
            "ASI1_AGENTIC_TASK_REMOTE_ROOT": "/root/work/quantum-gpt",
            "ASI1_AGENTIC_TASK_COMPACT_COMMAND": "0",
            "ASI1_AGENTIC_TASK_TRAINING_MODE": "native",
            "ASI1_AGENTIC_TASK_GRPO_STEPS": "1",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    command = payload["execution_command"]
    assert payload["compact_command"] == "shell-b64"
    assert command.startswith("python3 -c ")
    assert "__import__('\"'\"'subprocess'\"'\"')" in command
    assert "," not in command
    assert "&&" not in command
    assert payload["remote_script_path"] == "/tmp/asi1_agentic_grpo_run_full.sh"
    remote_command = payload["remote_command"]
    assert "__ASI1_GRPO_BEFORE_TORCHRUN__" in remote_command
    assert "__ASI1_GRPO_AFTER_TORCHRUN__" in remote_command
    assert "grpo_step_metrics.jsonl" in remote_command
    assert "final_adapter" in remote_command
    assert "__ASI1_GRPO_METRICS_AND_ARTIFACTS_OK__" in remote_command
    assert "__ASI1_GRPO_AFTER_TORCHRUN__" not in command
    assert ";&&" not in command
    assert ";&" not in command


def test_asi1_agentic_grpo_task_can_embed_wheelhouse_before_training() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "ASI1_AGENTIC_TASK_TIMESTAMP": "20260528T120000Z",
            "ASI1_AGENTIC_TASK_REMOTE_ROOT": "/root/work/quantum-gpt",
            "ASI1_AGENTIC_TASK_IMAGE_NAME": "quantumstim",
            "ASI1_AGENTIC_TASK_EMBED_WHEELHOUSE": "1",
            "ASI1_AGENTIC_TASK_GRPO_STEPS": "1",
            "ASI1_AGENTIC_TASK_MAX_NEW_TOKENS": "64",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["compact_command"] == "embedded-wheelhouse"
    assert payload["bootstrap_wheelhouse"] is True
    assert payload["embed_wheelhouse"] is True
    assert payload["remote_root"] == "/root/work/quantum-gpt"

    command = payload["execution_command"]
    assert command.startswith("set -euo pipefail\ncd /root/work/quantum-gpt\n")
    assert "ASI1_EMBEDDED_WHEELHOUSE_GRPO_START" in command
    assert "accelerate-1.4.0-py3-none-any.whl" in command
    assert "peft-0.14.0-py3-none-any.whl" in command
    assert "python3 scripts/append_text_file.py" in command
    assert "python3 scripts/decode_base64_file.py" in command
    assert "python3 -m zipfile -t" in command
    assert "python3 -m pip install --no-cache-dir --no-input --no-index" in command
    assert "import accelerate; import peft" in command
    assert "bash scripts/run_asi1_agentic_grpo_from_env.sh" in command
    assert "export ASI1_AGENTIC_TASK_GRPO_STEPS=1" in command
    assert "export ASI1_AGENTIC_TASK_MAX_NEW_TOKENS=64" in command
    assert ">" not in command
    assert ">>" not in command


def test_asi1_agentic_grpo_task_native_mode_skips_peft_dependency_gate() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run", "__launch-spec"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "ASI1_AGENTIC_TASK_TIMESTAMP": "20260528T130000Z",
            "ASI1_AGENTIC_TASK_REMOTE_ROOT": "/root/work/quantum-gpt",
            "ASI1_AGENTIC_TASK_TRAINING_MODE": "native",
            "ASI1_AGENTIC_TASK_GRPO_STEPS": "1",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    command = payload["remote_command"]
    assert "--training-mode native" in command
    assert "__ASI1_GRPO_BEFORE_TORCHRUN__" in command
    assert "peft_ok" not in command


def test_asi1_agentic_grpo_full_command_honors_remote_root_override() -> None:
    result = subprocess.run(
        [
            "bash",
            str(SCRIPT),
            "--dry-run",
            "__launch-spec",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "ASI1_AGENTIC_TASK_TIMESTAMP": "20260530T130000Z",
            "ASI1_AGENTIC_TASK_REMOTE_ROOT": "/root/work/quantum-gpt",
            "ASI1_AGENTIC_TASK_COMPACT_COMMAND": "0",
            "ASI1_AGENTIC_TASK_TRAINING_MODE": "native",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["remote_root"] == "/root/work/quantum-gpt"
    assert payload["execution_command"].startswith("python3 -c ")
    assert "&&" not in payload["execution_command"]
    assert "test -d /root/work/quantum-gpt" in payload["remote_command"]
    assert "test -d /workspace/quantum-gpt" not in payload["remote_command"]
    assert "grpo_step_metrics.jsonl" in payload["remote_command"]
    assert "final_adapter" in payload["remote_command"]

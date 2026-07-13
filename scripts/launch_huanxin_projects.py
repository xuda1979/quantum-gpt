#!/usr/bin/env python3
"""Run local gates, then sync and launch remote Huanxin jobs for both projects."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from training.runtime_python import detect_python_version, resolve_python_interpreter

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
ALPHAQUBIT_ROOT = Path("/Users/daxu/software/ALPHAQUBIT")
BROWSER_AUTOMATION_ROOT = WORKSPACE_ROOT / "browser-automation"
DEFAULT_ALPHAQUBIT_PYTHON = ALPHAQUBIT_ROOT / ".venv" / "bin" / "python"
DEFAULT_ALPHAQUBIT_REQUIREMENTS = ALPHAQUBIT_ROOT / "requirements.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--projects",
        nargs="*",
        choices=["quantum", "alphaqubit"],
        default=["quantum", "alphaqubit"],
    )
    parser.add_argument("--alphaqubit-python", default=str(DEFAULT_ALPHAQUBIT_PYTHON))
    parser.add_argument("--huanxin-headless", default=os.environ.get("HUANXIN_HEADLESS", "1"))
    parser.add_argument(
        "--quantum-model-name",
        default=os.environ.get("QWEN_BASE_MODEL", "Qwen/Qwen3.6-27B"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=WORKSPACE_ROOT / "artifacts" / "huanxin-launch-summary.json",
    )
    return parser.parse_args()


def run_local_command(command: list[str], cwd: Path) -> dict:
    started = time.time()
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    return {
        "command": command,
        "cwd": str(cwd),
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "duration_seconds": round(time.time() - started, 3),
        "ok": completed.returncode == 0,
    }


def resolve_node_binary() -> str:
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Could not find 'node' on PATH")
    return node


def resolve_alphaqubit_base_python() -> str:
    resolution = resolve_python_interpreter()
    selected_path = resolution.get("selected_path")
    if selected_path:
        return str(selected_path)

    brew = resolution.get("brew_binary") or shutil.which("brew") or "/Users/daxu/homebrew/bin/brew"
    if Path(brew).exists():
        install_result = run_local_command([str(brew), "install", "python@3.11"], WORKSPACE_ROOT)
        if install_result["ok"]:
            for prefix in [Path("/Users/daxu/homebrew/bin"), Path("/opt/homebrew/bin")]:
                binary = prefix / "python3.11"
                if binary.exists():
                    return str(binary)

    raise RuntimeError("Could not find or install a Python 3.10+ interpreter for ALPHAQUBIT")


def ensure_alphaqubit_python(python_path: str) -> tuple[str, list[dict]]:
    interpreter = Path(python_path)
    bootstrap_results: list[dict] = []
    if interpreter.exists():
        version = detect_python_version(str(interpreter))
        if version and version >= (3, 10):
            return str(interpreter), bootstrap_results
        shutil.rmtree(interpreter.parent.parent, ignore_errors=True)

    base_python = resolve_alphaqubit_base_python()

    venv_dir = interpreter.parent.parent
    bootstrap_results.append(
        run_local_command([base_python, "-m", "venv", str(venv_dir)], ALPHAQUBIT_ROOT)
    )
    if not bootstrap_results[-1]["ok"]:
        return str(interpreter), bootstrap_results

    bootstrap_results.append(
        run_local_command(
            [str(interpreter), "-m", "pip", "install", "--upgrade", "pip"], ALPHAQUBIT_ROOT
        )
    )
    if not bootstrap_results[-1]["ok"]:
        return str(interpreter), bootstrap_results

    bootstrap_results.append(
        run_local_command(
            [str(interpreter), "-m", "pip", "install", "-r", str(DEFAULT_ALPHAQUBIT_REQUIREMENTS)],
            ALPHAQUBIT_ROOT,
        )
    )
    return str(interpreter), bootstrap_results


def run_node_script(
    script_name: str, script_args: list[str], cwd: Path, profile_copy_name: str, headless: str
) -> dict:
    env = {
        **os.environ,
        "HUANXIN_PROFILE_COPY_NAME": profile_copy_name,
        "HUANXIN_HEADLESS": headless,
    }
    command = [resolve_node_binary(), str(BROWSER_AUTOMATION_ROOT / script_name), *script_args]
    completed = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
    return {
        "command": command,
        "cwd": str(cwd),
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "ok": completed.returncode == 0,
    }


def project_configs(args: argparse.Namespace) -> dict[str, dict]:
    alpha_python = args.alphaqubit_python
    quantum_command = (
        "cd /root/work/quantum-gpt && "
        "python3 evals/runner/run_eval.py && "
        "python3 data/seed/build_seed_dataset.py && "
        "python3 data/seed/convert_to_chat.py && "
        "python3 data/seed/create_splits.py --auto-policy && "
        "mkdir -p logs outputs/qwen-sft && "
        f"nohup python3 training/qwen_sft_peft.py --train-file data/seed/splits/train.jsonl --eval-file data/seed/splits/val.jsonl --output-dir outputs/qwen-sft --model-name {args.quantum_model_name} --max-steps 10 --per-device-batch-size 1 --gradient-accumulation-steps 8 --learning-rate 2e-4 --device auto > logs/qwen-sft.log 2>&1 < /dev/null & "
        "echo QUANTUM_TRAIN_PID:$! && sleep 3 && (tail -n 20 logs/qwen-sft.log || true)"
    )
    alpha_command = (
        "cd /root/work/alphaqubit && "
        "mkdir -p logs outputs/ion-trap && "
        "nohup python3 run_ion_trap_pipeline.py --config configs/si1000_ion.yaml --train-samples 1000000 --test-samples 20000 --epochs 20 --batch-size 64 --output-dir outputs/ion-trap --device auto > logs/ion-trap.log 2>&1 < /dev/null & "
        "echo ALPHAQUBIT_TRAIN_PID:$! && sleep 3 && (tail -n 20 logs/ion-trap.log || true)"
    )

    return {
        "quantum": {
            "env": "ai2",
            "local_root": WORKSPACE_ROOT,
            "remote_dir": "/root/work/quantum-gpt",
            "sources": [
                "AGENTS.md",
                "PROJECT.md",
                "USER.md",
                "HEARTBEAT.md",
                "TOOLS.md",
                "data",
                "evals",
                "research",
                "scripts",
                "training",
            ],
            "local_checks": [
                ["python3", "evals/runner/run_eval.py"],
                ["python3", "data/seed/build_seed_dataset.py"],
                ["python3", "data/seed/convert_to_chat.py"],
                ["python3", "data/seed/create_splits.py", "--auto-policy"],
                [
                    "python3",
                    "-m",
                    "py_compile",
                    "training/qwen_sft_peft.py",
                    "scripts/launch_huanxin_projects.py",
                ],
            ],
            "remote_command": quantum_command,
        },
        "alphaqubit": {
            "env": "ai1",
            "local_root": ALPHAQUBIT_ROOT,
            "remote_dir": "/root/work/alphaqubit",
            "sources": [
                "README.md",
                "requirements.txt",
                "configs",
                "ai_models",
                "simulator",
                "train_from_npz.py",
                "run_ion_trap_pipeline.py",
            ],
            "local_checks": [
                [alpha_python, "-c", "import torch, stim, yaml; print('alphaqubit-local-deps-ok')"],
                [alpha_python, "-m", "py_compile", "run_ion_trap_pipeline.py"],
                [
                    alpha_python,
                    "run_ion_trap_pipeline.py",
                    "--quick-test",
                    "--train-samples",
                    "64",
                    "--test-samples",
                    "16",
                    "--epochs",
                    "1",
                    "--batch-size",
                    "8",
                    "--device",
                    "cpu",
                    "--output-dir",
                    "artifacts/local-ion-smoke",
                ],
            ],
            "remote_command": alpha_command,
        },
    }


def launch_project(name: str, config: dict, headless: str) -> dict:
    result = {
        "project": name,
        "env": config["env"],
        "bootstrap": [],
        "local_checks": [],
    }
    if name == "alphaqubit":
        resolved_python, bootstrap_steps = ensure_alphaqubit_python(config["local_checks"][0][0])
        result["bootstrap"] = bootstrap_steps
        for command in config["local_checks"]:
            if command and command[0] == config["local_checks"][0][0]:
                command[0] = resolved_python
        for step in result["bootstrap"]:
            if not step["ok"]:
                result["ok"] = False
                result["blocked_at"] = "bootstrap"
                return result

    for command in config["local_checks"]:
        check_result = run_local_command(command, config["local_root"])
        result["local_checks"].append(check_result)
        if not check_result["ok"]:
            result["ok"] = False
            result["blocked_at"] = "local_checks"
            return result

    profile_copy_name = f"{name}-{int(time.time())}"
    sync_args = [config["env"], "--remote-dir", config["remote_dir"]]
    for source in config["sources"]:
        sync_args.extend(["--source", source])
    result["sync"] = run_node_script(
        "huanxin_shell_sync.js", sync_args, config["local_root"], profile_copy_name, headless
    )
    if not result["sync"]["ok"]:
        result["ok"] = False
        result["blocked_at"] = "sync"
        return result

    result["remote_exec"] = run_node_script(
        "huanxin_shell_exec.js",
        [config["env"], "--command", config["remote_command"]],
        config["local_root"],
        profile_copy_name,
        headless,
    )
    result["ok"] = result["remote_exec"]["ok"]
    if not result["ok"]:
        result["blocked_at"] = "remote_exec"
    return result


def main() -> int:
    args = parse_args()
    configs = project_configs(args)
    selected = {name: configs[name] for name in args.projects}

    with ThreadPoolExecutor(max_workers=len(selected)) as executor:
        futures = {
            name: executor.submit(launch_project, name, config, args.huanxin_headless)
            for name, config in selected.items()
        }
        results = {name: future.result() for name, future in futures.items()}

    summary = {
        "ok": all(result.get("ok") for result in results.values()),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "projects": results,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Upload ASI2 distillation seed artifacts through bounded shell chunks."""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import os
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REMOTE_ROOT = "/vllm-workspace/quantum-gpt"
FILES = [
    Path("scripts/build_quantum_distillation_seed_questions.py"),
    Path("scripts/generate_distillation_teacher_responses.py"),
    Path("scripts/convert_dataset_v0_to_chat_sft.py"),
    Path("scripts/filter_distillation_question_quality.py"),
    Path("scripts/prepare_distillation_sft_split.py"),
    Path("scripts/render_asi2_distillation_lora_sft_command.py"),
    Path("scripts/validate_dataset_v0.py"),
    Path("scripts/validate_distillation_teacher_responses.py"),
    Path("tests/test_build_quantum_distillation_seed_questions.py"),
    Path("tests/test_generate_distillation_teacher_responses.py"),
    Path("tests/test_convert_dataset_v0_to_chat_sft.py"),
    Path("tests/test_filter_distillation_question_quality.py"),
    Path("tests/test_render_asi2_distillation_lora_sft_command.py"),
    Path("tests/test_validate_distillation_teacher_responses.py"),
    Path("data/seed/quantum_distillation_seed_questions_asi2_v1.jsonl"),
    Path("data/seed/quantum_distillation_seed_questions_asi2_v1_manifest.json"),
    Path("data/generated/quantum_distillation_teacher_responses_asi2_v1.jsonl"),
    Path("data/generated/quantum_distillation_teacher_responses_asi2_v1_chatml.jsonl"),
    Path("data/generated/quantum_distillation_teacher_responses_asi2_v1_rejected_quality.jsonl"),
    Path("data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality.jsonl"),
    Path("data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_chatml.jsonl"),
    Path("data/generated/quantum_distillation_teacher_responses_asi2_v1_question_rejected.jsonl"),
    Path(
        "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft/train_chatml.jsonl"
    ),
    Path(
        "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft/eval_chatml.jsonl"
    ),
    Path(
        "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft/manifest.json"
    ),
    Path("reports/quantum_distillation_teacher_responses_asi2_v1_validation.json"),
    Path("reports/quantum_distillation_teacher_responses_asi2_v1_quality.json"),
    Path("reports/quantum_distillation_teacher_responses_asi2_v1_question_quality.json"),
    Path("artifacts/asi2-distillation-lora-sft-command.json"),
    Path("artifacts/asi2-distillation-qlora-sft-command.json"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", default="ASI2")
    parser.add_argument("--remote-root", default=DEFAULT_REMOTE_ROOT)
    parser.add_argument("--file", dest="files", action="append", type=Path, default=None)
    parser.add_argument("--chunk-size", type=int, default=3200)
    parser.add_argument("--chunks-per-command", type=int, default=18)
    parser.add_argument("--wait-ms", type=int, default=90000)
    return parser.parse_args()


def run_remote(env_name: str, command: str, wait_ms: int) -> dict:
    shell_env = os.environ.copy()
    shell_env.setdefault(
        "HUANXIN_BROWSER_EXECUTABLE_PATH",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    )
    shell_env["HUANXIN_WAIT_MS"] = str(wait_ms)
    proc = subprocess.run(
        ["bash", "scripts/huanxin_env_shell.sh", "--env", env_name, command],
        cwd=ROOT,
        env=shell_env,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(proc.stdout + proc.stderr)
    payload = json.loads(proc.stdout[proc.stdout.find("{") :])
    if not payload.get("ok") or not payload.get("commandOk"):
        raise SystemExit(json.dumps(payload, indent=2))
    return payload


def shell_append_command(tmp_path: str, chunks: list[str], *, truncate: bool = False) -> str:
    parts = ["set -euo pipefail", "mkdir -p /tmp/asi2-distill-upload"]
    if truncate:
        parts.append(f": > {shlex.quote(tmp_path)}")
    for chunk in chunks:
        parts.append(f"printf '%s' {shlex.quote(chunk)} >> {shlex.quote(tmp_path)}")
    return "\n".join(parts)


def upload_file(
    env_name: str,
    rel_path: Path,
    remote_root: str,
    chunk_size: int,
    chunks_per_command: int,
    wait_ms: int,
) -> dict:
    raw = (ROOT / rel_path).read_bytes()
    encoded = base64.b64encode(gzip.compress(raw, compresslevel=9)).decode("ascii")
    chunks = [encoded[index : index + chunk_size] for index in range(0, len(encoded), chunk_size)]
    safe_name = hashlib.sha256(str(rel_path).encode()).hexdigest()[:16]
    tmp_path = f"/tmp/asi2-distill-upload/{safe_name}.b64"
    remote_path = f"{remote_root.rstrip('/')}/{rel_path.as_posix()}"
    sha256 = hashlib.sha256(raw).hexdigest()

    for start in range(0, len(chunks), chunks_per_command):
        batch = chunks[start : start + chunks_per_command]
        run_remote(
            env_name,
            shell_append_command(tmp_path, batch, truncate=(start == 0)),
            wait_ms,
        )

    decode_command = "\n".join(
        [
            "set -euo pipefail",
            f"mkdir -p {shlex.quote(str(Path(remote_path).parent))}",
            "python3 - <<'PYDECODE'",
            "import base64, gzip, hashlib, pathlib",
            f"src = pathlib.Path({tmp_path!r})",
            f"dst = pathlib.Path({remote_path!r})",
            "data = gzip.decompress(base64.b64decode(src.read_text()))",
            "dst.write_bytes(data)",
            f"expected = {sha256!r}",
            "actual = hashlib.sha256(data).hexdigest()",
            "assert actual == expected, (actual, expected)",
            f"print('__ASI2_UPLOAD_FILE_OK__ {rel_path.as_posix()} ' + actual)",
            "PYDECODE",
        ]
    )
    run_remote(env_name, decode_command, wait_ms)
    return {"path": rel_path.as_posix(), "bytes": len(raw), "sha256": sha256, "chunks": len(chunks)}


def main() -> int:
    args = parse_args()
    files = args.files if args.files else FILES
    uploaded = [
        upload_file(
            args.env,
            rel_path,
            args.remote_root,
            args.chunk_size,
            args.chunks_per_command,
            args.wait_ms,
        )
        for rel_path in files
    ]
    verify_command = "\n".join(
        [
            "set -euo pipefail",
            f"cd {shlex.quote(args.remote_root)}",
            "python3 - <<'PYVERIFY'",
            "import json",
            "from pathlib import Path",
            "jsonl = Path('data/seed/quantum_distillation_seed_questions_asi2_v1.jsonl')",
            "teacher = Path('data/generated/quantum_distillation_teacher_responses_asi2_v1.jsonl')",
            "chat = Path('data/generated/quantum_distillation_teacher_responses_asi2_v1_chatml.jsonl')",
            "high = Path('data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality.jsonl')",
            "high_chat = Path('data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_chatml.jsonl')",
            "sft_train = Path('data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft/train_chatml.jsonl')",
            "sft_eval = Path('data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft/eval_chatml.jsonl')",
            "manifest = Path('data/seed/quantum_distillation_seed_questions_asi2_v1_manifest.json')",
            "rows = sum(1 for line in jsonl.read_text(encoding='utf-8').splitlines() if line.strip())",
            "teacher_rows = sum(1 for line in teacher.read_text(encoding='utf-8').splitlines() if line.strip())",
            "chat_rows = sum(1 for line in chat.read_text(encoding='utf-8').splitlines() if line.strip())",
            "high_rows = sum(1 for line in high.read_text(encoding='utf-8').splitlines() if line.strip())",
            "high_chat_rows = sum(1 for line in high_chat.read_text(encoding='utf-8').splitlines() if line.strip())",
            "sft_train_rows = sum(1 for line in sft_train.read_text(encoding='utf-8').splitlines() if line.strip())",
            "sft_eval_rows = sum(1 for line in sft_eval.read_text(encoding='utf-8').splitlines() if line.strip())",
            "payload = json.loads(manifest.read_text(encoding='utf-8'))",
            "assert rows == 480, rows",
            "assert teacher_rows >= 200, teacher_rows",
            "assert chat_rows == teacher_rows, (chat_rows, teacher_rows)",
            "assert high_rows >= 150, high_rows",
            "assert high_chat_rows == high_rows, (high_chat_rows, high_rows)",
            "assert sft_train_rows + sft_eval_rows == high_rows, (sft_train_rows, sft_eval_rows, high_rows)",
            "assert sft_eval_rows >= 16, sft_eval_rows",
            "assert payload['summary']['target_env'] == 'ASI2'",
            "report = {'ok': True, 'rows': rows, 'teacher_rows': teacher_rows, 'chat_rows': chat_rows, 'high_quality_rows': high_rows, 'sft_train_rows': sft_train_rows, 'sft_eval_rows': sft_eval_rows, 'target_env': payload['summary']['target_env'], 'remote_root': str(Path.cwd())}",
            "Path('reports').mkdir(exist_ok=True)",
            "Path('reports/asi2_distill_shell_upload_seed_v1.json').write_text(json.dumps(report, indent=2) + '\\n', encoding='utf-8')",
            "print('__ASI2_DISTILL_SHELL_UPLOAD_DONE__ ' + json.dumps(report, sort_keys=True))",
            "PYVERIFY",
        ]
    )
    run_remote(args.env, verify_command, args.wait_ms)
    print(
        json.dumps(
            {"ok": True, "env": args.env, "remote_root": args.remote_root, "uploaded": uploaded},
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

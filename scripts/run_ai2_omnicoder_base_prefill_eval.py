#!/usr/bin/env python3
"""Local orchestrator for ai2 OmniCoder base eval with local tokenization."""

from __future__ import annotations

import argparse
import base64
import json
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=ROOT
        / "evals/runs/omnicoder-quantum-generalization-holdout-base-omnicoder9b-20260410",
    )
    parser.add_argument("--base-model", type=Path, default=ROOT / "models/OmniCoder-9B")
    parser.add_argument(
        "--local-python",
        default=str(ROOT / ".venv-gemma4-smoke-py311/bin/python"),
    )
    parser.add_argument("--device", default="npu")
    parser.add_argument("--visible-devices", default="6")
    parser.add_argument("--token-budget-preset", default="quantum_heavy")
    parser.add_argument("--poll-interval", type=float, default=10.0)
    parser.add_argument("--remote-log", default="/tmp/omnicoder_base_prefill_eval.log")
    parser.add_argument("--remote-prefill-json", default="/tmp/omnicoder_base_prefill_payload.json")
    parser.add_argument("--remote-output-json", default="/tmp/omnicoder_base_prefill_outputs.json")
    parser.add_argument("--remote-eval-py", default="/tmp/omnicoder_base_prefill_eval.py")
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    return parser.parse_args()


def run_local(cmd: list[str], *, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), check=True, text=True, capture_output=True)


def ai2_exec(command: str, *, wait_ms: int = 30000, timeout_ms: int = 45000) -> dict:
    result = run_local(
        [
            "node",
            str(ROOT / "browser-automation/huanxin_shell_exec.js"),
            "ai2",
            "--require-daemon",
            "--wait-ms",
            str(wait_ms),
            "--command",
            command,
        ]
    )
    return json.loads(result.stdout)


def ensure_ok(response: dict) -> dict:
    if not response.get("ok"):
        raise RuntimeError(json.dumps(response, ensure_ascii=False, indent=2))
    return response


def extract_ai2_output(response: dict) -> str:
    after = response.get("after")
    if isinstance(after, str):
        matches = list(
            re.finditer(
                r"(?ms)^(__OC_[A-Za-z0-9_]+_START__)\n(.*?)\n^(__OC_[A-Za-z0-9_]+_END__)$",
                after,
            )
        )
        if matches:
            return matches[-1].group(2).strip()
    direct_output = response.get("output")
    if isinstance(direct_output, str) and direct_output.strip():
        return direct_output.strip()
    return ""


def ai2_exec_output(command: str, *, wait_ms: int = 30000, timeout_ms: int = 45000) -> str:
    return extract_ai2_output(ensure_ok(ai2_exec(command, wait_ms=wait_ms, timeout_ms=timeout_ms)))


def upload_file_b64_in_chunks(
    local_path: Path, remote_path: str, *, chunk_size: int = 8000
) -> None:
    payload_b64 = base64.b64encode(local_path.read_bytes()).decode("ascii")
    ai2_exec_output(f": > {shlex.quote(remote_path)}.b64", wait_ms=15000, timeout_ms=30000)
    for start in range(0, len(payload_b64), chunk_size):
        chunk = payload_b64[start : start + chunk_size]
        append_cmd = (
            f"python3 -c \"from pathlib import Path; "
            f"Path({(remote_path + '.b64')!r}).open('a', encoding='ascii').write({chunk!r})\""
        )
        ai2_exec_output(append_cmd, wait_ms=15000, timeout_ms=30000)
    decode_cmd = (
        "python3 -c \"import base64; from pathlib import Path; "
        f"src=Path({(remote_path + '.b64')!r}); "
        f"dst=Path({remote_path!r}); "
        "dst.write_bytes(base64.b64decode(src.read_text(encoding='ascii'))); "
        "print(dst.stat().st_size)\""
    )
    size_output = ai2_exec_output(decode_cmd, wait_ms=15000, timeout_ms=30000)
    if str(local_path.stat().st_size) not in size_output:
        raise RuntimeError(
            f"Remote write size mismatch for {remote_path}: expected {local_path.stat().st_size}, got {size_output!r}"
        )


def main() -> int:
    args = parse_args()

    local_prefill_json = Path("/private/tmp/omnicoder_base_prefill_local.json")
    local_remote_outputs_json = Path("/private/tmp/omnicoder_base_prefill_outputs_remote.json")
    local_remote_eval_py = Path("/private/tmp/omnicoder_base_prefill_eval_remote.py")
    remote_eval_pyc = f"{args.remote_eval_py}c"
    remote_runtime_overlay = "/root/work/quantum-gpt/training/runtime_overlay.py"

    prepare = run_local(
        [
            args.local_python,
            str(ROOT / "scripts/prepare_prefill_eval_inputs.py"),
            "--run-dir",
            str(args.run_dir),
            "--base-model",
            str(args.base_model),
            "--output",
            str(local_prefill_json),
        ]
    )
    print(prepare.stdout.strip())

    upload_file_b64_in_chunks(ROOT / "training/runtime_overlay.py", remote_runtime_overlay)
    upload_file_b64_in_chunks(local_prefill_json, args.remote_prefill_json)
    verify_payload_cmd = (
        'python3 -c "import json; '
        f"obj=json.load(open({args.remote_prefill_json!r}, encoding='utf-8')); "
        "print(obj['pad_token_id'], obj['eos_token_id'], len(obj['records']))\""
    )
    print(ai2_exec_output(verify_payload_cmd, wait_ms=15000, timeout_ms=30000))

    remote_eval_code = f"""
import json
import time
from pathlib import Path
from training.runtime_overlay import configure_runtime_overlay_from_env
configure_runtime_overlay_from_env()
import torch
from transformers import AutoConfig, AutoModelForCausalLM
payload = json.loads(Path({args.remote_prefill_json!r}).read_text(encoding='utf-8'))
print(json.dumps({{'stage': 'payload_loaded', 'records': len(payload['records'])}}, ensure_ascii=False), flush=True)
AutoConfig.from_pretrained('models/OmniCoder-9B', trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    'models/OmniCoder-9B',
    trust_remote_code=True,
    low_cpu_mem_usage=True,
    torch_dtype='auto',
).to({args.device!r})
model.eval()
print(json.dumps({{'stage': 'model_loaded', 'class': model.__class__.__name__, 'device': {args.device!r}}}, ensure_ascii=False), flush=True)
pad_token_id = int(payload.get('pad_token_id') or payload['eos_token_id'])
started_at = time.time()
outputs = []
for index, record in enumerate(payload['records'], start=1):
    print(json.dumps({{'stage': 'generate', 'index': index, 'total': len(payload['records']), 'task_id': record['task_id']}}, ensure_ascii=False), flush=True)
    input_ids = torch.tensor([record['input_ids']], dtype=torch.long, device={args.device!r})
    attention_mask = torch.tensor([record['attention_mask']], dtype=torch.long, device={args.device!r})
    with torch.inference_mode():
        generated = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens={512 if args.token_budget_preset == 'quantum_heavy' else 192},
            do_sample=False,
            pad_token_id=pad_token_id,
        )
    prompt_len = input_ids.shape[1]
    outputs.append({{
        'task_id': record['task_id'],
        'candidate_file': record['candidate_file'],
        'completion_ids': generated[0][prompt_len:].tolist(),
    }})
Path({args.remote_output_json!r}).write_text(
    json.dumps({{'outputs': outputs, 'duration_seconds': time.time() - started_at}}, ensure_ascii=False, indent=2),
    encoding='utf-8',
)
print(json.dumps({{'stage': 'done', 'output_json': {args.remote_output_json!r}}}, ensure_ascii=False), flush=True)
"""
    local_remote_eval_py.write_text(remote_eval_code, encoding="utf-8")
    upload_file_b64_in_chunks(local_remote_eval_py, args.remote_eval_py)

    launch_cmd = (
        "cd /root/work/quantum-gpt && "
        f"rm -f {shlex.quote(args.remote_log)} {shlex.quote(args.remote_output_json)} {shlex.quote(remote_eval_pyc)} && "
        "export QUANTUM_TRANSFORMERS_RUNTIME_SRC=/root/work/quantum-gpt/artifacts/runtime-bundles/omnicoder-qwen35-runtime-c585eea/transformers-src/src && "
        "export QUANTUM_HF_HUB_COMPAT_VERSION=1.8.0 && "
        "export QUANTUM_RUNTIME_HTTPX_STUB=0 && "
        f"export ASCEND_RT_VISIBLE_DEVICES={args.visible_devices} && "
        f"nohup python3 {shlex.quote(args.remote_eval_py)} "
        f"> {shlex.quote(args.remote_log)} 2>&1 < /dev/null & "
        "echo PID:$!"
    )
    print(ai2_exec_output(launch_cmd, wait_ms=15000, timeout_ms=45000))

    started = time.time()
    while True:
        status_cmd = (
            "cd /root/work/quantum-gpt && "
            f"if [ -f {shlex.quote(args.remote_output_json)} ]; then echo OUTPUT_READY; fi; "
            f"tail -n 80 {shlex.quote(args.remote_log)} 2>/dev/null || echo NO_LOG"
        )
        status_output = ai2_exec_output(status_cmd, wait_ms=15000, timeout_ms=45000)
        print(status_output.strip())
        if "OUTPUT_READY" in status_output and '"stage": "done"' in status_output:
            break
        if (
            "Traceback" in status_output
            or "ERR99999" in status_output
            or "Exception:" in status_output
        ):
            raise RuntimeError(status_output)
        if time.time() - started > args.timeout_seconds:
            raise TimeoutError(f"Timed out waiting for remote eval after {args.timeout_seconds}s")
        time.sleep(args.poll_interval)

    fetch_cmd = f"cat {shlex.quote(args.remote_output_json)}"
    local_remote_outputs_json.write_text(
        ai2_exec_output(fetch_cmd, wait_ms=15000, timeout_ms=45000),
        encoding="utf-8",
    )

    decode = run_local(
        [
            args.local_python,
            str(ROOT / "scripts/decode_prefill_eval_outputs.py"),
            "--run-dir",
            str(args.run_dir),
            "--base-model",
            str(args.base_model),
            "--outputs-json",
            str(local_remote_outputs_json),
        ]
    )
    print(decode.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

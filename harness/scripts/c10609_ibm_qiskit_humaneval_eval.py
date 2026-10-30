#!/usr/bin/env python3
"""C-10609 — fail-closed eval runner for the FROZEN IBM Qiskit HumanEval 139
benchmark (qiskit-community/qiskit-human-eval, IBM; arXiv 2406.14712), dual
prompt style.

WHAT IT DOES
  For each of the 139 tasks in a frozen style file (qhe_completion or
  hard_instruction):
    1. build the chat prompt (system + user),
    2. generate ONE candidate with base model or base+LoRA adapter on the
       ASI2 NPU (single process, balanced-layers),
    3. exec the candidate against the task's frozen `test` body with a hard
       per-task timeout, qiskit>=2.6 runtime,
    4. score pass/fail; fail-closed: generation error or exec error = FAIL,
       never a guess.

FAIL-CLOSED RULES
  - benchmark sha256 verified against MANIFEST.json before anything runs,
  - missing qiskit / qiskit_aer -> abort (never score silently),
  - per-task exec timeout -> FAIL for that task (recorded),
  - crash before scoring -> exit nonzero, no partial envelope claimed done,
  - envelope carries benchmark sha, adapter sha, per-task verdicts, and
    the exact prompt style.

USAGE (on the box, NPU):
  python3 harness/scripts/c10609_ibm_qiskit_humaneval_eval.py \
      --base-model /root/work/filestorage/Qwen3.8-27B \
      --adapter /path/to/adapter  (optional; omit for base-only) \
      --style qhe_completion \
      --out-dir outputs/ibm_qiskit_eval_c10609

  (add --dry-run to verify freeze + qiskit + prompt build without NPU work)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BENCH_DIR = ROOT / "evals" / "benchmarks" / "ibm_qiskit"
MANIFEST = BENCH_DIR / "MANIFEST.json"
STYLE_FILES = {
    "qhe_completion": "qiskit_humaneval_139_qhe_completion.jsonl",
    "hard_instruction": "qiskit_humaneval_139_hard_instruction.jsonl",
}
PER_TASK_TIMEOUT_S = 180  # box CPU measured: slowest canonical (task 100,
# EfficientSU2 Optimize1qGates) needs ~60-120s; 180s gives headroom without
# letting pathological hangs dominate a 139-task sweep.
GENERATION_MAX_NEW_TOKENS = 1024

SYS_PROMPT = (
    "You are an expert quantum computing programmer. Write correct, "
    "idiomatic Python using the Qiskit SDK. Return only the final Python "
    "code unless the task explicitly asks for an explanation."
)


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_freeze(style: str) -> list[dict]:
    man = json.loads(MANIFEST.read_text())
    fn = STYLE_FILES[style]
    p = BENCH_DIR / fn
    expect = man["files"][fn]["sha256"]
    actual = sha256_file(p)
    if actual != expect:
        raise SystemExit(f"FREEZE DRIFT {fn}: manifest {expect} != disk {actual}")
    rows = [json.loads(ln) for ln in open(p) if ln.strip()]
    if len(rows) != man["tasks"]:
        raise SystemExit(f"FREEZE DRIFT {fn}: manifest tasks {man['tasks']} != rows {len(rows)}")
    return rows


def require_qiskit() -> None:
    try:
        import qiskit  # noqa: F401
        import qiskit_aer  # noqa: F401
    except ImportError as e:
        raise SystemExit(f"qiskit runtime missing on box: {e}")


def build_user_prompt(row: dict, style: str) -> str:
    if style == "qhe_completion":
        # HumanEval style: the prompt is code; ask for the completed function.
        return (
            "Complete the following Python function for a Qiskit quantum "
            "computing task. Return the COMPLETE function definition "
            "(including any needed imports and the original signature).\n\n"
            "```python\n" + row["prompt"] + "\n```\n\n"
            "Return only the final Python code."
        )
    return row["prompt"] + "\n\nReturn only the final Python code, in a ```python code block."


def extract_code(text: str, row: dict, style: str) -> str:
    """Extract the candidate code from raw generation."""
    # prefer fenced blocks
    fences = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if fences:
        return max(fences, key=len).strip()
    # qhe_completion: model may return bare code completion
    return text.strip()


def exec_candidate(code: str, row: dict, style: str, workdir: Path) -> dict:
    """Write candidate + frozen test to a temp dir and exec with timeout."""
    t0 = time.time()
    entry = row["entry_point"]
    task_id = row["task_id"]
    safe = re.sub(r"[^A-Za-z0-9_]", "_", task_id)
    if style == "qhe_completion":
        # HumanEval protocol: `prompt` is the code PREFIX (imports +
        # signature); the candidate is the function BODY. Test defines
        # check() but does NOT call it (verified: 139/139 no call), so we
        # append the call ourselves.
        program = (
            row["prompt"]
            + "\n"
            + code
            + "\n\n"
            + row["test"]
            + f"\ncheck({entry})\nprint('PASS_OK')"
        )
    else:
        # Standalone protocol: candidate is a complete program defining the
        # entry function; test both defines and CALLS check(entry)
        # (verified: 139/139 include the call), then we add the PASS marker.
        program = code + "\n\n" + row["test"] + "\nprint('PASS_OK')"
    prog = workdir / f"prog_{safe}.py"
    prog.write_text(program)
    try:
        r = subprocess.run(
            [sys.executable, str(prog)],
            capture_output=True,
            text=True,
            timeout=PER_TASK_TIMEOUT_S,
            cwd=str(workdir),
        )
        passed = (r.returncode == 0) and ("PASS_OK" in r.stdout)
        return {
            "passed": passed,
            "returncode": r.returncode,
            "stderr_tail": (r.stderr or "")[-400:],
            "dt_s": round(time.time() - t0, 2),
        }
    except subprocess.TimeoutExpired:
        return {
            "passed": False,
            "returncode": None,
            "stderr_tail": "EXEC_TIMEOUT",
            "dt_s": round(time.time() - t0, 2),
        }


def main() -> int:
    ap = argparse.ArgumentParser(description="C-10609 IBM Qiskit HumanEval eval")
    ap.add_argument("--base-model", required=True)
    ap.add_argument("--adapter", default=None, help="LoRA adapter dir; omit for base-only eval")
    ap.add_argument("--style", required=True, choices=list(STYLE_FILES))
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--max-new-tokens", type=int, default=GENERATION_MAX_NEW_TOKENS)
    ap.add_argument("--task-start", type=int, default=0)
    ap.add_argument("--task-count", type=int, default=0, help="0 = all")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--device", default="npu")
    ap.add_argument("--npu-max-memory-gib", type=int, default=54)
    args = ap.parse_args()

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    emit = lambda **kw: print(  # noqa: E731
        json.dumps(dict(ts_utc=now_utc(), **kw), ensure_ascii=False), flush=True
    )

    # 1) freeze verify + runtime check
    rows = verify_freeze(args.style)
    require_qiskit()
    emit(stage="freeze_ok", style=args.style, tasks=len(rows))

    # 2) slice
    n = len(rows)
    start = args.task_start
    count = n if args.task_count == 0 else min(args.task_count, n - start)
    sl = rows[start : start + count]

    adapter_sha = None
    if args.adapter:
        ad = Path(args.adapter)
        adapter_sha = sha256_file(ad / "adapter_model.safetensors")
    base_sha_note = "base_only" if not args.adapter else "adapter"

    # 3) dry-run: build all prompts, exec all canonical solutions as sanity
    if args.dry_run:
        workdir = out_dir / "_dryrun_work"
        workdir.mkdir(exist_ok=True)
        canon_pass = 0
        canon_fail = []
        for row in sl:
            res = exec_candidate(row["canonical_solution"], row, args.style, workdir)
            if res["passed"]:
                canon_pass += 1
            else:
                canon_fail.append((row["task_id"], res["stderr_tail"][:120]))
        emit(
            stage="dry_run_done",
            style=args.style,
            slice=(start, count),
            canonical_pass=canon_pass,
            canonical_fail=len(canon_fail),
            fails=canon_fail[:10],
        )
        return 0 if canon_pass == len(sl) else 1

    # 4) load model (NPU) — heavy import done only now
    emit(
        stage="model_load_start",
        base_model=args.base_model,
        adapter=args.adapter,
        device=args.device,
    )
    import torch  # noqa: F401 (torch dtype used at load time)
    from peft import PeftModel  # noqa: F401 (used when adapter present)
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(args.base_model)
    config = AutoConfig.from_pretrained(args.base_model)
    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        config=config,
        torch_dtype=torch.bfloat16,
        device_map="balanced",
        max_memory={i: f"{args.npu_max_memory_gib}GiB" for i in range(8)},
    )
    if args.adapter:
        model = PeftModel.from_pretrained(model, args.adapter)
        model.eval()
        emit(stage="adapter_applied", adapter_sha256=adapter_sha)
    model.eval()
    emit(stage="model_load_done", dt_s=round(time.time() - t0, 1))

    # fail-closed probe: adapter must produce tokens (8-token probe)
    if args.adapter:
        probe_msgs = [
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": build_user_prompt(sl[0], args.style)},
        ]
        enc = tok.apply_chat_template(
            probe_msgs,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=False,
        ).to(model.device)
        model.generate(enc, max_new_tokens=8, do_sample=False, pad_token_id=tok.eos_token_id)
        emit(stage="adapter_probe_generated")

    # 5) per-task generate + exec
    results = []
    pass_count = 0
    t_start = time.time()
    workdir = out_dir / "_exec_work"
    workdir.mkdir(exist_ok=True)
    for i, row in enumerate(sl):
        user_prompt = build_user_prompt(row, args.style)
        msgs = [
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        enc = tok.apply_chat_template(
            msgs,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=False,
        ).to(model.device)
        t_gen = time.time()
        gen = model.generate(
            enc,
            max_new_tokens=args.max_new_tokens,
            do_sample=False,
            pad_token_id=tok.eos_token_id,
        )
        text = tok.decode(gen[0][enc.shape[1] :], skip_special_tokens=True)
        dt_gen = round(time.time() - t_gen, 1)
        code = extract_code(text, row, args.style)
        res = exec_candidate(code, row, args.style, workdir)
        passed = res["passed"]
        pass_count += int(passed)
        rec = {
            "task_id": row["task_id"],
            "entry_point": row["entry_point"],
            "difficulty": row["difficulty_scale"],
            "passed": passed,
            "returncode": res["returncode"],
            "stderr_tail": res["stderr_tail"],
            "dt_gen_s": dt_gen,
            "dt_exec_s": res["dt_s"],
            "gen_chars": len(text),
            "code_chars": len(code),
        }
        results.append(rec)
        emit(
            stage="task_done",
            idx=i + 1,
            of=len(sl),
            task_id=row["task_id"],
            passed=passed,
            running_pass=pass_count,
        )

    # 6) envelope (fail-closed: only written when the loop completes)
    elapsed = round(time.time() - t_start, 1)
    envelope = {
        "card": "C-10609",
        "kind": "ibm_qiskit_humaneval_eval",
        "created_utc": now_utc(),
        "style": args.style,
        "benchmark_file": STYLE_FILES[args.style],
        "benchmark_sha256": sha256_file(BENCH_DIR / STYLE_FILES[args.style]),
        "tasks_total": len(sl),
        "task_slice": [start, start + count],
        "base_model": args.base_model,
        "adapter": args.adapter,
        "adapter_sha256": adapter_sha,
        "mode": base_sha_note,
        "max_new_tokens": args.max_new_tokens,
        "pass_count": pass_count,
        "fail_count": len(sl) - pass_count,
        "elapsed_s": elapsed,
        "per_task": results,
        "no_fabrication": True,
    }
    env_path = out_dir / (f"ibm_eval_{args.style}_{'adapter' if args.adapter else 'base'}.json")
    env_path.write_text(json.dumps(envelope, indent=1) + "\n")
    emit(stage="envelope_written", path=str(env_path), pass_count=pass_count, total=len(sl))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Evaluate base Qwen3.6 vs a LoRA adapter on the held-out 495 eval prompts.

For each eval example we feed the system+user messages to the model, greedily
generate a completion, extract the Python code block, execute it in a subprocess
with a timeout, and record pass@1 (exit code 0, no exception). We report overall
and per-framework pass@1 for both the base model and the base+adapter model.

Designed to run INSIDE the Huanxin ASI1 NPU env. Single NPU is fine (generation
is not memory-heavy like training-time full-logits CE).

Usage:
  python3 scripts/eval_base_vs_adapter.py \
      --base /root/work/filestorage/Qwen3.6-27B \
      --adapter /root/work/.../checkpoints/step-162/adapter \
      --eval-file data/generated/quantum_finetune_verified_chat_sft_dedup_1k/eval_chatml.jsonl \
      --out /root/work/software/quantum-gpt/outputs/eval_base_vs_adapter.json \
      --max-new-tokens 768 --limit 0
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, tempfile, time
from collections import defaultdict

CODE_FENCE = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_code(text: str) -> str:
    blocks = CODE_FENCE.findall(text or "")
    if blocks:
        # take the longest fenced block (usually the full script)
        return max(blocks, key=len).strip()
    # no fence: assume the whole thing is code if it looks like python
    return (text or "").strip()


def run_code(code: str, timeout: int = 60) -> dict:
    if not code.strip():
        return {"passed": False, "reason": "empty_code"}
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(code)
        path = fh.name
    try:
        proc = subprocess.run(
            [sys.executable, path],
            capture_output=True, text=True, timeout=timeout,
            env=dict(os.environ, MPLBACKEND="Agg"),
        )
        ok = proc.returncode == 0
        return {
            "passed": ok,
            "returncode": proc.returncode,
            "stderr_tail": (proc.stderr or "")[-500:],
        }
    except subprocess.TimeoutExpired:
        return {"passed": False, "reason": "timeout"}
    except Exception as e:  # noqa: BLE001
        return {"passed": False, "reason": f"runner_error: {e}"}
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def load_examples(path: str, limit: int) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
            if limit and len(rows) >= limit:
                break
    return rows


def build_model(base: str, adapter: str | None, device: str):
    import torch
    try:
        import torch_npu  # noqa: F401  # registers the NPU backend
    except Exception:
        pass
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(base, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        base,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        attn_implementation="eager",  # NPU: flash-attn kernels are unsupported
    )
    if adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter)
    model = model.to(device)
    model.eval()
    return tok, model


def generate(tok, model, messages: list[dict], max_new_tokens: int, device: str) -> str:
    import torch
    prompt = tok.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tok(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        out = model.generate(
            **inputs, max_new_tokens=max_new_tokens, do_sample=False,
            temperature=None, top_p=None, pad_token_id=tok.eos_token_id,
        )
    gen = out[0][inputs["input_ids"].shape[1]:]
    return tok.decode(gen, skip_special_tokens=True)


def eval_model(tag, base, adapter, examples, device, max_new_tokens, exec_timeout):
    tok, model = build_model(base, adapter, device)
    per_fw = defaultdict(lambda: [0, 0])  # framework -> [passed, total]
    passed_total = 0
    details = []
    t0 = time.time()
    for i, ex in enumerate(examples, 1):
        msgs = [m for m in ex["messages"] if m["role"] in ("system", "user")]
        fw = ex.get("metadata", {}).get("framework", "unknown")
        try:
            text = generate(tok, model, msgs, max_new_tokens, device)
        except Exception as e:  # noqa: BLE001
            text = ""
            gen_err = str(e)
        else:
            gen_err = None
        code = extract_code(text)
        res = run_code(code, timeout=exec_timeout)
        ok = bool(res.get("passed"))
        per_fw[fw][0] += int(ok)
        per_fw[fw][1] += 1
        passed_total += int(ok)
        details.append({
            "example_id": ex.get("example_id"),
            "framework": fw,
            "passed": ok,
            "gen_err": gen_err,
            "exec": {k: v for k, v in res.items() if k != "stderr_tail"},
        })
        if i % 20 == 0 or i == len(examples):
            elapsed = time.time() - t0
            print(f"[{tag}] {i}/{len(examples)} pass={passed_total} "
                  f"({passed_total/i:.1%}) elapsed={elapsed:.0f}s", flush=True)
    summary = {
        "tag": tag,
        "adapter": adapter,
        "total": len(examples),
        "passed": passed_total,
        "pass_at_1": passed_total / max(len(examples), 1),
        "per_framework": {k: {"passed": v[0], "total": v[1],
                              "pass_at_1": v[0] / max(v[1], 1)}
                          for k, v in sorted(per_fw.items())},
    }
    del model
    try:
        import torch
        if getattr(torch, "npu", None) and hasattr(torch.npu, "empty_cache"):
            torch.npu.empty_cache()
    except Exception:
        pass
    return summary, details


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--eval-file", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="npu:0")
    ap.add_argument("--max-new-tokens", type=int, default=768)
    ap.add_argument("--exec-timeout", type=int, default=60)
    ap.add_argument("--limit", type=int, default=0, help="0 = all")
    args = ap.parse_args()

    examples = load_examples(args.eval_file, args.limit)
    print(f"loaded {len(examples)} eval examples", flush=True)

    base_summary, base_details = eval_model(
        "base", args.base, None, examples, args.device,
        args.max_new_tokens, args.exec_timeout)
    adpt_summary, adpt_details = eval_model(
        "adapter", args.base, args.adapter, examples, args.device,
        args.max_new_tokens, args.exec_timeout)

    report = {
        "base": base_summary,
        "adapter": adpt_summary,
        "delta_pass_at_1": adpt_summary["pass_at_1"] - base_summary["pass_at_1"],
        "config": vars(args),
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    with open(args.out.replace(".json", "_details.json"), "w", encoding="utf-8") as fh:
        json.dump({"base": base_details, "adapter": adpt_details}, fh, indent=2)

    print("\n===== RESULT =====")
    print(f"BASE    pass@1 = {base_summary['pass_at_1']:.1%} "
          f"({base_summary['passed']}/{base_summary['total']})")
    print(f"ADAPTER pass@1 = {adpt_summary['pass_at_1']:.1%} "
          f"({adpt_summary['passed']}/{adpt_summary['total']})")
    print(f"DELTA          = {report['delta_pass_at_1']:+.1%}")
    print(f"report -> {args.out}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""eval_10_comp.py — 10-sample comprehensive-score eval: base vs 27B adapter (ASI3).

Modes:
  gen   --which base|adapter --devices 0,1,2,3 [--n 10] [--out partial.jsonl]
        Loads the model on the given (visible) NPUs, generates on the same
        10-sample subset as the earlier evals10 runs (seed 42, sorted), executes
        the extracted code, and writes per-sample records (response, exec
        evidence) to a JSONL.
  judge --devices 0,1,2,3 --base-partial a.jsonl --adapter-partial b.jsonl --out report.json
        Loads the FROZEN base model (per FV-GSPO design the judge is never the
        training policy) and scores every sample on the five comprehensive
        dimensions (correctness, runnability, result_correctness, efficiency,
        quality), evidence-anchored. Blends each sample into the comprehensive
        reward R = 0.40*P + 0.35*S + 0.25*J (mode="comprehensive" in
        training/grpo_utils.py) and writes the final report.

NPU notes (Ascend / Huanxin ASI3):
  * ASCEND_RT_VISIBLE_DEVICES must be set before torch_npu initializes, so it
    is applied from --devices at the very top of this file.
  * accelerate 1.14's get_max_memory() does not accept npu: keys; we monkeypatch
    it so device_map="auto" can spread the model across the visible NPUs.
"""

import argparse
import ast
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time

BASE = "/root/work/filestorage/Qwen3.8-27B"
ADAPTER = "/root/work/quantum-gpt/outputs/qg-27b-sft-formal-27b-sft-formal-20260803T153806Z/checkpoints/step-22/adapter"
EVAL_FILE = "/root/work/quantum-gpt/data/generated/quantum_dedup_1k_glm52_soft_distill_v3/eval_sft_questions_code.jsonl"
N_DEFAULT = 10
MAX_NEW_TOKENS = 384
JUDGE_MAX_TOKENS = 640
EXEC_TIMEOUT = 60
CODE_FENCE = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)

FORCE_CODE_SYSTEM = (
    "You are a careful quantum software engineering assistant. The user's task requires a "
    "complete, self-contained Python program. Produce ONLY a fenced Python code block:\n"
    "```python\n<full program>\n```\n"
    "Do not include thinking processes, explanations, markdown beyond the code block, or "
    "surrounding commentary. The program must run as-is and print its results."
)

COMPREHENSIVE_JUDGE_PROMPT = """You are a strict code evaluator. Score the candidate solution on five dimensions, each a float 0.0-1.0. Use the executable evidence below as the authoritative anchor — do not contradict it.

Dimensions:
- correctness: does the algorithm's logic produce the right result (0.0 if tests fail)?
- runnability: would the code execute without syntax/import/runtime errors?
- result_correctness: do the actual outputs match the expected values?
- efficiency: is runtime / circuit depth / gate count / resource use reasonable for the problem?
- quality: is the code well-structured, readable, and maintainable?

CODE TO EVALUATE:
```python
{code}
```

EXECUTABLE EVIDENCE (authoritative):
{evidence}

TASK CONTEXT:
{task_context}

Output ONLY a JSON object:
{{"correctness": 0.0-1.0, "runnability": 0.0-1.0, "result_correctness": 0.0-1.0, "efficiency": 0.0-1.0, "quality": 0.0-1.0, "evidence": "one line"}}"""

DIMENSIONS = ("correctness", "runnability", "result_correctness", "efficiency", "quality")
P_MASS, S_MASS, J_MASS = 0.40, 0.35, 0.25


def main():
    args = parse_args()
    os.environ.setdefault("ASCEND_RT_VISIBLE_DEVICES", args.devices)
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    # Must be set before torch_npu initializes.
    os.environ["ASCEND_RT_VISIBLE_DEVICES"] = args.devices

    # --- accelerate 1.14 cannot parse npu: keys in max_memory; patch it so
    # device_map="auto" spreads the model over the visible NPUs. Two bindings
    # must be patched: accelerate.utils.modeling.get_max_memory (used by
    # accelerate's own get_balanced_memory) and the accelerate.utils
    # re-export (used by transformers/integrations/accelerate.py via a
    # function-local `from accelerate.utils import get_max_memory`).
    import accelerate.utils as acc_utils
    import accelerate.utils.modeling as acc_modeling
    import torch
    import torch_npu  # noqa: F401  (registers the npu device backend)

    _orig_get_max_memory = acc_modeling.get_max_memory

    def _size_to_bytes(value):
        """Convert '56GiB'-style values to bytes; pass numbers through."""
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        text = str(value).strip().upper()
        for unit, mult in (
            ("TIB", 1024**4),
            ("GIB", 1024**3),
            ("MIB", 1024**2),
            ("KIB", 1024),
            ("TB", 10**12),
            ("GB", 10**9),
            ("MB", 10**6),
            ("KB", 10**3),
            ("B", 1),
        ):
            if text.endswith(unit):
                return float(text[: -len(unit)].strip()) * mult
        return float(text)

    def _patched_get_max_memory(max_memory=None):
        # accelerate 1.14 counts npu devices but its whitelist only admits
        # int/mps/cpu/disk keys; accept npu: keys and convert sizes to bytes
        # (the original also does that conversion).
        if max_memory is not None and any(str(k).startswith("npu") for k in max_memory):
            return {k: _size_to_bytes(v) for k, v in max_memory.items()}
        return _orig_get_max_memory(max_memory)

    acc_modeling.get_max_memory = _patched_get_max_memory
    acc_utils.get_max_memory = _patched_get_max_memory

    from transformers import AutoModelForCausalLM, AutoTokenizer

    if args.mode == "judge":
        return judge_mode(args, torch, AutoModelForCausalLM, AutoTokenizer)
    return gen_mode(args, torch, AutoModelForCausalLM, AutoTokenizer)


def parse_args():
    p = argparse.ArgumentParser(description="10-sample comprehensive-score eval (ASI3)")
    p.add_argument("--mode", choices=["gen", "judge"], required=True)
    p.add_argument("--which", choices=["base", "adapter"], default=None)
    p.add_argument("--devices", default="0,1,2,3")
    p.add_argument("--n", type=int, default=N_DEFAULT)
    p.add_argument(
        "--sys-prompt",
        choices=["standard", "force-code", "few-shot"],
        default="standard",
        help="force-code: replace the system prompt to demand a fenced ```python``` block; "
        "few-shot: prepend two code-only exemplars (reference solutions from non-eval samples)",
    )
    p.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="sampling temperature (default greedy); use with --k for pass@k",
    )
    p.add_argument("--k", type=int, default=1, help="number of samples per question (pass@k)")
    p.add_argument(
        "--best-trial",
        action="store_true",
        help="judge mode: score only the exec-best trial per sample "
        "(pass > has-code > first); pass@k still from all trials",
    )
    p.add_argument("--out", default=None)
    p.add_argument("--base-partial", default=None)
    p.add_argument("--adapter-partial", default=None)
    args = p.parse_args()
    if args.mode == "gen" and args.which is None:
        p.error("--which base|adapter required in gen mode")
    if args.mode == "judge" and (not args.base_partial or not args.adapter_partial):
        p.error("--base-partial and --adapter-partial required in judge mode")
    return args


# --------------------------------------------------------------------------
# shared helpers
# --------------------------------------------------------------------------


def load_examples(path, limit):
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


def select_subset(examples, n):
    random.seed(42)
    chosen = sorted(random.sample(range(len(examples)), min(n, len(examples))))
    return chosen, [examples[i] for i in chosen]


def extract_code(text):
    blocks = CODE_FENCE.findall(text or "")
    return blocks[0].strip() if blocks else ""


def run_code(code, timeout=EXEC_TIMEOUT):
    """Execute extracted code; return exec evidence for the judge."""
    start = time.monotonic()
    if not code.strip():
        return {
            "passed": False,
            "reason": "empty_code",
            "syntax_ok": False,
            "runtime_ms": 0,
            "stdout": "",
            "stderr": "",
        }
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return {
            "passed": False,
            "reason": "syntax_error",
            "error": f"{exc.msg} (line {exc.lineno})",
            "syntax_ok": False,
            "runtime_ms": 0,
            "stdout": "",
            "stderr": "",
        }
    substantive = (
        ast.Assign,
        ast.AnnAssign,
        ast.AugAssign,
        ast.ClassDef,
        ast.For,
        ast.AsyncFunctionDef,
        ast.FunctionDef,
        ast.Import,
        ast.ImportFrom,
        ast.Try,
        ast.While,
        ast.With,
    )
    if not any(isinstance(node, substantive) for node in ast.walk(tree)):
        return {
            "passed": False,
            "reason": "trivial_code",
            "syntax_ok": True,
            "runtime_ms": 0,
            "stdout": "",
            "stderr": "",
        }
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(code)
        path = fh.name
    try:
        proc = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "MPLBACKEND": "Agg"},
        )
        return {
            "passed": proc.returncode == 0,
            "returncode": proc.returncode,
            "syntax_ok": True,
            "runtime_ms": int((time.monotonic() - start) * 1000),
            "stdout": (proc.stdout or "")[:600],
            "stderr": (proc.stderr or "")[:400],
        }
    except subprocess.TimeoutExpired:
        return {
            "passed": False,
            "reason": "timeout",
            "syntax_ok": True,
            "runtime_ms": int((time.monotonic() - start) * 1000),
            "stdout": "",
            "stderr": f"timeout after {timeout}s",
        }
    except Exception as e:  # noqa: BLE001
        return {
            "passed": False,
            "reason": f"runner_error: {e}",
            "syntax_ok": True,
            "runtime_ms": int((time.monotonic() - start) * 1000),
            "stdout": "",
            "stderr": "",
        }
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def build_evidence(exec_res):
    lines = [
        f"passed={exec_res.get('passed', False)}",
        f"returncode={exec_res.get('returncode', 'n/a')}",
        f"runtime_ms={exec_res.get('runtime_ms', 'n/a')}",
        f"stdout={exec_res.get('stdout', '')[:600]!r}",
        f"stderr={exec_res.get('stderr', '')[:400]!r}",
    ]
    return "\n".join(lines)


def load_model(tok, which, torch, AutoModelForCausalLM):
    n_visible = len(os.environ["ASCEND_RT_VISIBLE_DEVICES"].split(","))
    # int bytes (not "56GiB" strings): transformers 5.2's _get_device_map mixes
    # the raw max_memory dict with the converted one (`min(raw, converted)`),
    # so strings would crash there.
    max_memory = {f"npu:{i}": int(56 * 1024**3) for i in range(n_visible)}
    model = AutoModelForCausalLM.from_pretrained(
        BASE,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        low_cpu_mem_usage=True,
        max_memory=max_memory,
    )
    if which == "adapter":
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, ADAPTER)
    model.eval()
    print(f"Loaded {which} on {getattr(model, 'hf_device_map', 'npu')}", flush=True)
    return model


def generate(model, tok, messages, max_tokens, torch, temperature=None):
    prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tok(prompt, return_tensors="pt")
    inputs = {k: v.to(model.get_input_embeddings().weight.device) for k, v in inputs.items()}
    gen_kwargs = {"max_new_tokens": max_tokens, "pad_token_id": tok.eos_token_id}
    if temperature is not None:
        gen_kwargs.update(do_sample=True, temperature=temperature, top_p=0.95)
    else:
        gen_kwargs["do_sample"] = False
    with torch.no_grad():
        out = model.generate(**inputs, **gen_kwargs)
    return tok.decode(out[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True)


def task_context(ex):
    for m in ex.get("messages", []):
        if m.get("role") == "user":
            return (m.get("content") or "")[:400]
    return ex.get("example_id", "unknown")


# --------------------------------------------------------------------------
# gen mode
# --------------------------------------------------------------------------


def gen_mode(args, torch, AutoModelForCausalLM, AutoTokenizer):
    examples = load_examples(EVAL_FILE, 0)
    chosen, sel = select_subset(examples, args.n)
    print(f"Selected {len(sel)} samples (indices {chosen})", flush=True)

    tok = AutoTokenizer.from_pretrained(BASE, trust_remote_code=True)
    model = load_model(tok, args.which, torch, AutoModelForCausalLM)

    def build_few_shot(ex):
        """Prepend two code-only exemplars (reference solutions) from samples
        outside the selected subset, then the target user message."""
        chosen_ids = {e["example_id"] for e in sel}
        pool = [e for e in examples if e["example_id"] not in chosen_ids]
        exs = pool[:2]
        msgs = []
        for m in ex["messages"]:
            if m["role"] == "system":
                msgs.append(
                    dict(
                        m,
                        content=(m.get("content") or "")
                        + "\n\nThe expected output format is ONLY a complete, runnable Python program "
                        "in a fenced ```python``` block. Two examples of the expected format follow.",
                    )
                )
                break
        for e in exs:
            for m in e["messages"]:
                if m["role"] in ("user", "assistant"):
                    content = m.get("content") or ""
                    if m["role"] == "assistant":
                        content = content[:700]
                    msgs.append({"role": m["role"], "content": content})
        for m in ex["messages"]:
            if m["role"] == "user":
                msgs.append(m)
        return msgs

    records = []
    total = len(sel) * max(1, args.k)
    done = 0
    for i, ex in enumerate(sel, 1):
        msgs = [m for m in ex["messages"] if m["role"] in ("system", "user")]
        if args.sys_prompt == "force-code":
            msgs = [
                dict(m, content=FORCE_CODE_SYSTEM) if m["role"] == "system" else m for m in msgs
            ]
        elif args.sys_prompt == "few-shot":
            msgs = build_few_shot(ex)
        for trial in range(max(1, args.k)):
            try:
                text = generate(model, tok, msgs, MAX_NEW_TOKENS, torch, args.temperature)
                gen_err = None
            except Exception as e:  # noqa: BLE001
                text, gen_err = "", str(e)
            code = extract_code(text)
            res = run_code(code)
            records.append(
                {
                    "example_id": ex["example_id"],
                    "sample_idx": i,
                    "trial": trial,
                    "which": args.which,
                    "response": text,
                    "extracted_code": code,
                    "gen_err": gen_err,
                    "exec": res,
                    "task_context": task_context(ex),
                }
            )
            done += 1
            passed = sum(1 for r in records if r["exec"].get("passed", False))
            print(
                f"[{args.which}] {done}/{total} (sample {i} trial {trial}) pass={passed} "
                f"elapsed={int(time.monotonic())}s",
                flush=True,
            )

    out = args.out or f"/root/work/quantum-gpt/outputs/eval10_{args.which}_partial.jsonl"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")
    print(f"Partial report saved to {out}", flush=True)
    return 0


# --------------------------------------------------------------------------
# judge mode
# --------------------------------------------------------------------------


def _clamp_score(raw):
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return None
    return min(1.0, max(0.0, v))


def parse_dim_scores(text):
    """Parse the judge's response into per-dimension scores (0-1).

    Tries (1) every ``{...}`` chunk as JSON, then (2) prose forms like
    "Correctness: 0.0 Runnability: 0.0 ..." (the base judge often emits
    scores in prose and runs out of tokens before reaching JSON).
    """
    raw_text = text or ""
    # (1) JSON chunks — try all of them, in order
    for match in re.finditer(r"\{[^{}]*\}", raw_text):
        try:
            data = json.loads(match.group(0))
        except (json.JSONDecodeError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        scores = {dim: _clamp_score(data.get(dim)) for dim in DIMENSIONS}
        if any(v is not None for v in scores.values()):
            return scores
    # (2) prose fallback — per-dimension "Name: <float>" patterns.
    # "result[ _]correctness" must be consumed before plain "correctness"
    # (which would otherwise also match inside "Result Correctness").
    scores = {}
    m = re.search(r"result[ _]correctness\s*[:=]\s*([0-9]*\.?[0-9]+)", raw_text, re.IGNORECASE)
    if m:
        scores["result_correctness"] = _clamp_score(m.group(1))
    else:
        scores["result_correctness"] = None
    plain = re.search(
        r"(?<!result[ _])correctness\s*[:=]\s*([0-9]*\.?[0-9]+)", raw_text, re.IGNORECASE
    )
    if plain:
        scores["correctness"] = _clamp_score(plain.group(1))
    else:
        scores["correctness"] = None
    for dim in ("runnability", "efficiency", "quality"):
        m = re.search(rf"{dim}\s*[:=]\s*([0-9]*\.?[0-9]+)", raw_text, re.IGNORECASE)
        scores[dim] = _clamp_score(m.group(1)) if m else None
    if all(v is None for v in scores.values()):
        return None
    return scores


def judge_one(model, tok, record, torch):
    code = record.get("extracted_code", "") or ""
    if not code.strip():
        # No code block extracted (e.g. the model answered in prose). Give the
        # judge the response text so quality/grammar dims still have material,
        # while exec evidence (passed=False) keeps runnability/correctness low.
        code = (
            f"(no code block extracted)\n\nRESPONSE TEXT:\n{(record.get('response') or '')[:800]}"
        )
    evidence = build_evidence(record.get("exec", {}))
    prompt = COMPREHENSIVE_JUDGE_PROMPT.format(
        code=code, evidence=evidence, task_context=record.get("task_context", "unknown")
    )
    messages = [{"role": "user", "content": prompt}]
    try:
        text = generate(model, tok, messages, JUDGE_MAX_TOKENS, torch)
    except Exception as e:  # noqa: BLE001
        return None, f"judge_gen_error: {e}"
    scores = parse_dim_scores(text)
    return scores, text


def judge_mode(args, torch, AutoModelForCausalLM, AutoTokenizer):
    tok = AutoTokenizer.from_pretrained(BASE, trust_remote_code=True)
    model = load_model(tok, "base", torch, AutoModelForCausalLM)

    def load_partial(path):
        rows = []
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    def exec_pass_at_k(rows):
        groups = {}
        for r in rows:
            key = r.get("sample_idx", r["example_id"])
            groups.setdefault(key, []).append(r)
        if not groups:
            return 0.0
        ok = sum(1 for g in groups.values() if any(r["exec"].get("passed", False) for r in g))
        return ok / len(groups)

    def pick_best_trial(rows):
        groups = {}
        for r in rows:
            key = r.get("sample_idx", r["example_id"])
            groups.setdefault(key, []).append(r)
        chosen = []
        for key in sorted(groups):
            g = groups[key]
            best = (
                next((r for r in g if r["exec"].get("passed", False)), None)
                or next((r for r in g if (r.get("extracted_code") or "").strip()), None)
                or g[0]
            )
            chosen.append(best)
        return chosen

    base_all = load_partial(args.base_partial)
    adapter_all = load_partial(args.adapter_partial)
    pass_at_k = {"base": exec_pass_at_k(base_all), "adapter": exec_pass_at_k(adapter_all)}
    base_rows = pick_best_trial(base_all) if args.best_trial else base_all
    adapter_rows = pick_best_trial(adapter_all) if args.best_trial else adapter_all
    assert len(base_rows) == len(adapter_rows) > 0, "partial files must have equal length"

    out = {}
    for tag, rows in (("base", base_rows), ("adapter", adapter_rows)):
        details = []
        for i, rec in enumerate(rows, 1):
            dims, raw = judge_one(model, tok, rec, torch)
            p = 1.0 if rec.get("exec", {}).get("passed", False) else 0.0
            s = 1.0 if rec.get("exec", {}).get("syntax_ok", False) else 0.0
            if dims is not None:
                j = sum(v for v in dims.values() if v is not None) / max(1, len(dims))
                comprehensive = P_MASS * p + S_MASS * s + J_MASS * j
            else:
                j, comprehensive = None, None
            details.append(
                {
                    "example_id": rec["example_id"],
                    "response": rec.get("response", ""),
                    "gen_err": rec.get("gen_err"),
                    "exec": rec.get("exec", {}),
                    "judge_dims": dims,
                    "judge_raw": raw,
                    "P": p,
                    "S": s,
                    "J": j,
                    "comprehensive": comprehensive,
                }
            )
            print(f"[judge:{tag}] {i}/{len(rows)}", flush=True)
        passed = sum(1 for d in details if d["P"] == 1.0)
        dim_means = {dim: None for dim in DIMENSIONS}
        for dim in DIMENSIONS:
            vals = [
                d["judge_dims"][dim]
                for d in details
                if d["judge_dims"] is not None and d["judge_dims"][dim] is not None
            ]
            if vals:
                dim_means[dim] = sum(vals) / len(vals)
        comp_vals = [d["comprehensive"] for d in details if d["comprehensive"] is not None]
        j_vals = [d["J"] for d in details if d["J"] is not None]
        summary = {
            "n": len(details),
            "pass_at_1": passed / len(details),
            "pass_at_k": pass_at_k[tag],
            "mean_comprehensive": (sum(comp_vals) / len(comp_vals)) if comp_vals else None,
            "mean_J": (sum(j_vals) / len(j_vals)) if j_vals else None,
            "dim_means": dim_means,
        }
        out[tag] = {"summary": summary, "samples": details}
        print(f"[judge:{tag}] summary={json.dumps(summary)}", flush=True)

    out["delta"] = None
    b, a = out["base"]["summary"], out["adapter"]["summary"]
    if b["mean_comprehensive"] is not None and a["mean_comprehensive"] is not None:
        out["delta"] = {
            "mean_comprehensive": a["mean_comprehensive"] - b["mean_comprehensive"],
            "pass_at_1": a["pass_at_1"] - b["pass_at_1"],
        }
        for dim in DIMENSIONS:
            bv, av = b["dim_means"].get(dim), a["dim_means"].get(dim)
            if bv is not None and av is not None:
                out["delta"].setdefault("dim_deltas", {})[dim] = av - bv

    # per-dimension base-vs-adapter table (also printed below)
    def fmt(v):
        return f"{v:.3f}" if v is not None else "n/a"

    rows = []
    header = f"| {'dimension':<20} | {'base':>8} | {'adapter':>8} | {'delta':>8} |"
    sep = f"| {'-' * 20} | {'-' * 8} | {'-' * 8} | {'-' * 8} |"
    rows.append(header)
    rows.append(sep)
    for dim in DIMENSIONS:
        bv, av = b["dim_means"].get(dim), a["dim_means"].get(dim)
        dv = (av - bv) if (bv is not None and av is not None) else None
        rows.append(f"| {dim:<20} | {fmt(bv):>8} | {fmt(av):>8} | {fmt(dv):>8} |")
    rows.append(
        f"| {'pass@1':<20} | {fmt(b['pass_at_1']):>8} | {fmt(a['pass_at_1']):>8} | {fmt(a['pass_at_1'] - b['pass_at_1']):>8} |"
    )
    if "pass_at_k" in b and "pass_at_k" in a:
        rows.append(
            f"| {'pass@k':<20} | {fmt(b['pass_at_k']):>8} | {fmt(a['pass_at_k']):>8} | {fmt(a['pass_at_k'] - b['pass_at_k']):>8} |"
        )
    rows.append(
        f"| {'mean_comprehensive':<20} | {fmt(b['mean_comprehensive']):>8} | {fmt(a['mean_comprehensive']):>8} | {fmt(a['mean_comprehensive'] - b['mean_comprehensive']) if b['mean_comprehensive'] is not None and a['mean_comprehensive'] is not None else 'n/a':>8} |"
    )
    table = "\n".join(rows)
    out["table"] = table
    print(table, flush=True)
    out["meta"] = {
        "mode": "comprehensive",
        "formula": "R = 0.40*P + 0.35*S + 0.25*J (comprehensive blend, FV-GSPO)",
        "n_samples": len(base_rows),
        "base_partial": args.base_partial,
        "adapter_partial": args.adapter_partial,
        "best_trial": args.best_trial,
    }
    path = args.out or "/root/work/quantum-gpt/outputs/eval10_comprehensive_report.json"
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"Comprehensive report saved to {path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

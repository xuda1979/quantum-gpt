#!/usr/bin/env python3
"""eval_100_reeval.py — 100-sample re-eval with robust code extraction (ASI2, 4 NPUs).

Replaces the eval10 methodology that treated "response contains text" as
useless. This version:

  * generates with a real token budget (default 2048 new tokens) so the model
    can actually reach code after its thinking preamble,
  * extracts code robustly — fenced blocks of ANY language tag (or none),
    then an AST-validated line-span fallback for unfenced text+code mixes,
  * records how the code was extracted (extract_method) per sample,
  * checkpoints per sample to JSONL with resume support,
  * shards the 100-sample subset across --shard-total processes so all 4
    ASI2 NPUs are used,
  * judge mode reuses the FROZEN base model (FV-GSPO: judge is never the
    training policy) with exec evidence as the authoritative anchor.

Modes:
  gen    --which base|adapter --devices 0,1,2,3 --n 100
         [--shard-idx 0 --shard-total 1] [--max-new-tokens 2048] [--out ...]
  judge  --devices 0,1,2,3 --base-partial b.jsonl --adapter-partial a.jsonl
         [--start 0 --end 100] [--out judge_shard.json]
  report --base-pattern ... --adapter-pattern ... [--judge ...]
         prints the cumulative per-10-sample temporary report.

NPU notes (Ascend / Huanxin ASI2): ASCEND_RT_VISIBLE_DEVICES is applied at
the very top; accelerate's get_max_memory is patched to accept npu: keys.
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
import textwrap
import time

BASE = "/root/work/filestorage/Qwen3.6-27B"
ADAPTER = "/root/work/quantum-gpt/outputs/qg-27b-sft-formal-27b-sft-formal-20260803T153806Z/checkpoints/step-22/adapter"
EVAL_FILE = "/root/work/quantum-gpt/data/generated/quantum_dedup_1k_glm52_soft_distill_v3/eval_sft_questions_code.jsonl"
N_DEFAULT = 100
MAX_NEW_TOKENS = 1536
BATCH_SIZE = 4
JUDGE_MAX_TOKENS = 640
EXEC_TIMEOUT = 60
OUT_DIR = "/root/work/quantum-gpt/outputs"

FENCE_RE = re.compile(r"```([a-zA-Z0-9_+-]*)\s*\n(.*?)```", re.DOTALL)
THINK_PREFIX_RE = re.compile(
    r"^(here'?s (a|my|the) (thinking|reasoning)|thinking( process)?:)", re.IGNORECASE
)
BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
CODE_START_RE = re.compile(
    r"^\s*(?:import |from |def |class |if |for |while |with |print\(|import$|#|\S+\s*=)"
)
SPAN_CAP = 300  # max candidate lines for unfenced span search

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


def parse_args():
    p = argparse.ArgumentParser(description="100-sample re-eval with robust code extraction (ASI2)")
    p.add_argument("--mode", choices=["gen", "judge", "report"], required=True)
    p.add_argument("--which", choices=["base", "adapter"], default=None)
    p.add_argument("--devices", default="0,1,2,3")
    p.add_argument("--n", type=int, default=N_DEFAULT)
    p.add_argument("--shard-idx", type=int, default=0)
    p.add_argument("--shard-total", type=int, default=1)
    p.add_argument("--max-new-tokens", type=int, default=MAX_NEW_TOKENS)
    p.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    p.add_argument("--out", default=None)
    p.add_argument("--base-partial", default=None)
    p.add_argument("--adapter-partial", default=None)
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--end", type=int, default=100)
    args = p.parse_args()
    if args.mode == "gen" and args.which is None:
        p.error("--which base|adapter required in gen mode")
    if args.mode == "judge" and (not args.base_partial or not args.adapter_partial):
        p.error("--base-partial and --adapter-partial required in judge mode")
    return args


# --------------------------------------------------------------------------
# selection / data
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


def my_shard_idxs(n, shard_idx, shard_total):
    """Round-robin shard of 0..n-1 — keeps per-shard progress even."""
    return list(range(shard_idx, n, shard_total))


def task_context(ex):
    for m in ex.get("messages", []):
        if m.get("role") == "user":
            return (m.get("content") or "")[:400]
    return ex.get("example_id", "unknown")


def reference_code(ex):
    """The row's assistant message is the reference solution (if any)."""
    for m in ex.get("messages", []):
        if m.get("role") == "assistant":
            return (m.get("content") or "").strip()
    return ""


def load_reference_map():
    """example_id -> reference exec evidence (cached, executed once each)."""
    out = {}
    refs = {}
    for ex in load_examples(EVAL_FILE, 0):
        code = reference_code(ex)
        if code:
            refs[ex["example_id"]] = code
    for eid, code in refs.items():
        out[eid] = {"code": code, "exec": run_code(code, timeout=90)}
    return out


def read_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def append_jsonl(path, rec):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


# --------------------------------------------------------------------------
# robust code extraction
# --------------------------------------------------------------------------


def _strip_thinking(resp):
    """Drop the model's 'Here's a thinking process:' preamble and markdown
    bullets so unfenced code that follows can be found."""
    lines = (resp or "").splitlines()
    out = []
    started = False
    for ln in lines:
        if not started:
            if THINK_PREFIX_RE.search(ln.strip()):
                continue  # skip the thinking banner line
            if BULLET_RE.match(ln) or ln.strip().startswith("**") or not ln.strip():
                # bullets / bold labels are preamble; but once real code
                # lines appear (started=True) we keep everything.
                continue
            started = True
        out.append(ln)
    return "\n".join(out)


def _valid_python(text):
    try:
        ast.parse(text)
        return True
    except SyntaxError:
        return False


def _longest_span(lines):
    """Find the longest contiguous run of lines that ast.parse accepts.

    Tries candidate starts (code-looking lines) and grows each window to the
    end, backtracking on syntax errors; returns the longest valid window.
    """
    n = len(lines)
    if n == 0:
        return ""
    # candidate start lines: code-looking or just after blank lines
    candidates = []
    for i, ln in enumerate(lines):
        if CODE_START_RE.match(ln) or (ln.strip() and (i == 0 or not lines[i - 1].strip())):
            candidates.append(i)
    if not candidates:
        candidates = [0]
    best = ""
    for start in candidates:
        if n - start <= len(best.splitlines()):
            continue
        window = lines[start:]
        for end in range(len(window), max(0, len(window) - SPAN_CAP), -1):
            cand = "\n".join(window[:end])
            if len(cand.splitlines()) <= len(best.splitlines()):
                break
            if _valid_python(cand):
                if len(cand) > len(best):
                    best = cand
                break
    return best.strip()


def extract_code_robust(resp):
    """Return (code, method) — code is the best candidate, method explains how."""
    if not (resp or "").strip():
        return "", "none"
    # 1) fenced blocks (any language tag or none), longest valid wins.
    #    Blocks inside markdown lists carry list indentation — dedent first.
    blocks = [(lang or "", textwrap.dedent(body.strip())) for lang, body in FENCE_RE.findall(resp)]
    if blocks:
        valid = [b for b in blocks if _valid_python(b[1])]
        pool = valid or blocks
        best = max(pool, key=lambda b: len(b[1]))
        return best[1], f"fence[{best[0] or 'none'}]" + ("" if valid else "[unparsed]")
    # 2) unfenced: strip thinking preamble, dedent, then AST-validated longest span
    body = _strip_thinking(resp)
    lines = [ln.rstrip() for ln in textwrap.dedent(body).splitlines()]
    span = _longest_span(lines)
    if span.strip():
        return span, "span"
    # 3) last resort: any contiguous chunk that even parses as expression
    return "", "none"


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


# --------------------------------------------------------------------------
# model loading (Ascend)
# --------------------------------------------------------------------------


def setup_ascend(devices):
    os.environ["ASCEND_RT_VISIBLE_DEVICES"] = devices
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    import accelerate.utils as acc_utils
    import accelerate.utils.modeling as acc_modeling
    import torch  # noqa: F401
    import torch_npu  # noqa: F401  (registers the npu device backend)

    _orig = acc_modeling.get_max_memory

    def _size_to_bytes(value):
        if isinstance(value, int | float) and not isinstance(value, bool):
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

    def _patched(max_memory=None):
        if max_memory is not None and any(str(k).startswith("npu") for k in max_memory):
            return {k: _size_to_bytes(v) for k, v in max_memory.items()}
        return _orig(max_memory)

    acc_modeling.get_max_memory = _patched
    acc_utils.get_max_memory = _patched
    return torch


def load_model(tok, which, torch, AutoModelForCausalLM):
    n_visible = len(os.environ["ASCEND_RT_VISIBLE_DEVICES"].split(","))
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


def generate_batch(model, tok, messages_list, max_tokens, torch, temperature=None):
    """Generate for a list of message sets in one padded batch (decode-bound
    NPU work amortizes across the batch). Returns list of decoded texts.

    IMPORTANT: decoder-only models must be LEFT-padded (right padding corrupts
    generation — transformers warns about this explicitly). With left padding,
    every row's generation starts right after the padded input, so the uniform
    slice o[input_len:] is correct for all rows.
    """
    if tok.padding_side != "left":
        tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token_id = tok.eos_token_id
    prompts = [
        tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True)
        for m in messages_list
    ]
    enc = tok(prompts, return_tensors="pt", padding=True)
    inputs = {k: v.to(model.get_input_embeddings().weight.device) for k, v in enc.items()}
    gen_kwargs = {"max_new_tokens": max_tokens, "pad_token_id": tok.pad_token_id}
    if temperature is not None:
        gen_kwargs.update(do_sample=True, temperature=temperature, top_p=0.95)
    else:
        gen_kwargs["do_sample"] = False
    with torch.no_grad():
        out = model.generate(**inputs, **gen_kwargs)
    texts = []
    for o in out:
        n_in = inputs["input_ids"].shape[1]
        texts.append(tok.decode(o[n_in:], skip_special_tokens=True))
    return texts


# --------------------------------------------------------------------------
# gen mode
# --------------------------------------------------------------------------


def gen_mode(args, torch, AutoModelForCausalLM, AutoTokenizer):
    examples = load_examples(EVAL_FILE, 0)
    chosen, sel = select_subset(examples, args.n)
    idxs = my_shard_idxs(len(sel), args.shard_idx, args.shard_total)
    out = args.out or f"{OUT_DIR}/eval100_{args.which}_shard{args.shard_idx}.jsonl"
    done_ids = {r["example_id"] for r in read_jsonl(out)} if os.path.exists(out) else set()
    todo = [(sel[i], i + 1) for i in idxs if sel[i]["example_id"] not in done_ids]
    print(
        f"[{args.which}] shard {args.shard_idx}/{args.shard_total}: {len(todo)} to do "
        f"({len(done_ids)} done) out={out}",
        flush=True,
    )

    tok = AutoTokenizer.from_pretrained(BASE, trust_remote_code=True)
    model = load_model(tok, args.which, torch, AutoModelForCausalLM)

    bs = max(1, args.batch_size)
    for start in range(0, len(todo), bs):
        chunk = todo[start : start + bs]
        msgs_list = [
            [m for m in ex["messages"] if m["role"] in ("system", "user")] for ex, _ in chunk
        ]
        try:
            texts = generate_batch(model, tok, msgs_list, args.max_new_tokens, torch)
            errs = [None] * len(texts)
        except Exception as e:  # noqa: BLE001
            texts, errs = [], []
            for ex, _ in chunk:
                try:
                    texts.append(
                        generate(
                            model,
                            tok,
                            [m for m in ex["messages"] if m["role"] in ("system", "user")],
                            args.max_new_tokens,
                            torch,
                        )
                    )
                    errs.append(None)
                except Exception as e2:  # noqa: BLE001
                    texts.append("")
                    errs.append(str(e2))
            print(f"[{args.which}] batch fallback after {e}", flush=True)
        for (ex, sample_idx), text, gen_err in zip(chunk, texts, errs, strict=False):
            code, method = extract_code_robust(text)
            res = run_code(code)
            rec = {
                "example_id": ex["example_id"],
                "sample_idx": sample_idx,
                "which": args.which,
                "response": text,
                "extracted_code": code,
                "extract_method": method,
                "gen_err": gen_err,
                "exec": res,
                "task_context": task_context(ex),
            }
            append_jsonl(out, rec)
            passed = sum(1 for r in read_jsonl(out) if r["exec"].get("passed", False))
            n_done = len(done_ids) + sum(
                1 for r in read_jsonl(out) if r["example_id"] not in done_ids
            )
            print(
                f"[{args.which}] shard{args.shard_idx} sample {sample_idx}/100 "
                f"done={n_done} pass={passed} method={method} "
                f"reason={res.get('reason', '')}",
                flush=True,
            )
    print(f"[{args.which}] shard{args.shard_idx} complete: {out}", flush=True)
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
    raw_text = text or ""
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
    scores = {}
    m = re.search(r"result[ _]correctness\s*[:=]\s*([0-9]*\.?[0-9]+)", raw_text, re.IGNORECASE)
    scores["result_correctness"] = _clamp_score(m.group(1)) if m else None
    plain = re.search(
        r"(?<!result[ _])correctness\s*[:=]\s*([0-9]*\.?[0-9]+)", raw_text, re.IGNORECASE
    )
    scores["correctness"] = _clamp_score(plain.group(1)) if plain else None
    for dim in ("runnability", "efficiency", "quality"):
        m = re.search(rf"{dim}\s*[:=]\s*([0-9]*\.?[0-9]+)", raw_text, re.IGNORECASE)
        scores[dim] = _clamp_score(m.group(1)) if m else None
    if all(v is None for v in scores.values()):
        return None
    return scores


def judge_one(model, tok, record, torch, ref_info=None):
    code = record.get("extracted_code", "") or ""
    if not code.strip():
        code = (
            f"(no code block extracted)\n\nRESPONSE TEXT:\n{(record.get('response') or '')[:800]}"
        )
    evidence = build_evidence(record.get("exec", {}))
    if ref_info and ref_info.get("exec", {}).get("passed", False):
        evidence += (
            "\nREFERENCE SOLUTION OUTPUT (expected):\n" + (ref_info["exec"].get("stdout", "")[:400])
        )
    prompt = COMPREHENSIVE_JUDGE_PROMPT.format(
        code=code, evidence=evidence, task_context=record.get("task_context", "unknown")
    )
    messages = [{"role": "user", "content": prompt}]
    try:
        text = generate(model, tok, messages, JUDGE_MAX_TOKENS, torch)
    except Exception as e:  # noqa: BLE001
        return None, f"judge_gen_error: {e}"
    return parse_dim_scores(text), text


def result_match(rec, ref_info):
    """Compare model stdout vs reference stdout when both ran cleanly."""
    if not ref_info or not ref_info.get("exec", {}).get("passed", False):
        return None
    if not rec.get("exec", {}).get("passed", False):
        return False
    a = (rec.get("exec", {}).get("stdout") or "").strip()
    b = (ref_info["exec"].get("stdout") or "").strip()
    if not a or not b:
        return None
    return a == b


def judge_mode(args, torch, AutoModelForCausalLM, AutoTokenizer):
    base_rows = read_jsonl(args.base_partial)
    adapter_rows = read_jsonl(args.adapter_partial)
    by_id = {f"base_{r['example_id']}": r for r in base_rows}
    by_id.update({f"adapter_{r['example_id']}": r for r in adapter_rows})
    ordered = []
    for i in range(1, 101):  # sample_idx 1..100
        b = next((r for r in base_rows if r["sample_idx"] == i), None)
        a = next((r for r in adapter_rows if r["sample_idx"] == i), None)
        if b is not None or a is not None:
            ordered.append((i, b, a))
    out = args.out or f"{OUT_DIR}/eval100_judge_shard{args.shard_idx}.jsonl"
    done = {json.loads(line)["sample_idx"] for line in open(out)} if os.path.exists(out) else set()
    todo = [(i, b, a) for i, b, a in ordered if i not in done and args.start <= i < args.end]
    print(f"[judge] shard {args.shard_idx}: {len(todo)} samples to judge", flush=True)

    tok = AutoTokenizer.from_pretrained(BASE, trust_remote_code=True)
    model = load_model(tok, "base", torch, AutoModelForCausalLM)
    refs = load_reference_map()

    def build_prompt(row, ref):
        code = row.get("extracted_code", "") or ""
        if not code.strip():
            code = (
                f"(no code block extracted)\n\nRESPONSE TEXT:\n{(row.get('response') or '')[:800]}"
            )
        evidence = build_evidence(row.get("exec", {}))
        if ref and ref.get("exec", {}).get("passed", False):
            evidence += (
                "\nREFERENCE SOLUTION OUTPUT (expected):\n" + (ref["exec"].get("stdout", "")[:400])
            )
        return COMPREHENSIVE_JUDGE_PROMPT.format(
            code=code, evidence=evidence, task_context=row.get("task_context", "unknown")
        )

    for i, b, a in todo:
        rec = {"sample_idx": i}
        ref = refs.get((b or a or {}).get("example_id", ""))
        rows = [("base", b), ("adapter", a)]
        # batched judge: generate the base+adapter prompts together (decoder
        # work amortizes; left padding keeps every row's slice correct)
        prompts = [build_prompt(row, ref) for tag, row in rows if row is not None]
        tags = [tag for tag, row in rows if row is not None]
        texts = generate_batch(
            model, tok, [[{"role": "user", "content": p}] for p in prompts], JUDGE_MAX_TOKENS, torch
        )
        for tag, row, text in zip(tags, [r for _, r in rows if r is not None], texts, strict=False):
            dims, raw = parse_dim_scores(text), text
            p = 1.0 if row.get("exec", {}).get("passed", False) else 0.0
            s = 1.0 if row.get("exec", {}).get("syntax_ok", False) else 0.0
            if dims is not None:
                j = sum(v for v in dims.values() if v is not None) / max(1, len(dims))
                comprehensive = P_MASS * p + S_MASS * s + J_MASS * j
            else:
                j, comprehensive = None, None
            rec[tag] = {
                "P": p,
                "S": s,
                "J": j,
                "comprehensive": comprehensive,
                "judge_dims": dims,
                "judge_raw": raw,
                "exec": row.get("exec", {}),
                "extract_method": row.get("extract_method"),
                "result_match": result_match(row, ref),
            }
        append_jsonl(out, rec)
        print(f"[judge] shard{args.shard_idx} sample {i}/100 done", flush=True)
    print(f"[judge] shard{args.shard_idx} complete: {out}", flush=True)
    return 0


# --------------------------------------------------------------------------
# report mode
# --------------------------------------------------------------------------


def report_mode(args):
    def load_which(pattern):
        import glob

        rows = []
        for f in sorted(glob.glob(pattern)):
            rows.extend(read_jsonl(f))
        by_idx = {}
        for r in rows:
            by_idx.setdefault(r["sample_idx"], r)
        return by_idx

    base = load_which(args.base_partial or f"{OUT_DIR}/eval100_base_shard*.jsonl")
    adapter = load_which(args.adapter_partial or f"{OUT_DIR}/eval100_adapter_shard*.jsonl")

    print("| samples | base done/pass | adapter done/pass |")
    print("|---------|-----------------|--------------------|")
    for cutoff in range(10, 101, 10):
        nb = sum(1 for i in range(1, cutoff + 1) if i in base)
        pb = sum(1 for i in range(1, cutoff + 1) if base.get(i, {}).get("exec", {}).get("passed"))
        na = sum(1 for i in range(1, cutoff + 1) if i in adapter)
        pa = sum(
            1 for i in range(1, cutoff + 1) if adapter.get(i, {}).get("exec", {}).get("passed")
        )
        print(f"| {cutoff:>7} | {nb:>4}/{pb:<4} | {na:>4}/{pa:<4} |")
    print()
    for tag, rows in (("base", base), ("adapter", adapter)):
        methods = {}
        reasons = {}
        for i in sorted(rows):
            r = rows[i]
            methods[r.get("extract_method", "?")] = methods.get(r.get("extract_method", "?"), 0) + 1
            reasons[r["exec"].get("reason", "?")] = reasons.get(r["exec"].get("reason", "?"), 0) + 1
        print(f"{tag}: done={len(rows)} methods={methods} exec_reasons={reasons}")
    return 0


def main():
    args = parse_args()
    if args.mode == "report":
        return report_mode(args)
    torch = setup_ascend(args.devices)
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if args.mode == "judge":
        return judge_mode(args, torch, AutoModelForCausalLM, AutoTokenizer)
    return gen_mode(args, torch, AutoModelForCausalLM, AutoTokenizer)


if __name__ == "__main__":
    sys.exit(main())

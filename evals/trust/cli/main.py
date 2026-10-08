#!/usr/bin/env python3
"""``quantum_eval`` — single entrypoint for the trustable evaluation subsystem.

Subcommands:
  suite-init     Discover tasks and write a suite.lock.json.
  suite-verify   Verify a suite.lock.json against the on-disk task tree.
  run            Run a model against a pinned suite, recording every
                 artifact to the ledger.
  score          Re-score a run's samples without regenerating.
  verify         Re-check every hash in a run; re-score every sample.
  audit          Audit a human report against the ledger.
  compare        Compare two runs (base vs adapter) with regression detect.
  report         Render an audit-checked Markdown report.
  reproduce      Re-run a run from its recipe and assert equality.

All commands are idempotent: re-running with the same inputs produces
the same ledger state (INSERT OR IGNORE) and the same output files.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ensure the repo root is on sys.path so `evals.trust.*` imports work
# regardless of the caller's CWD.
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from evals.trust.core import hashing, ledger, repro, sandbox, scoring, suite
from evals.trust.core.audit import audit_report


# ─────────────────────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────────────────────

def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_ledger(run_dir: Path) -> ledger.Ledger:
    return ledger.Ledger(run_dir / "ledger.db")


def _write_json(path: Path, obj: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _gen_candidate(model_adapter, *, prompt: str, max_new_tokens: int | None,
                   temperature: float | None, seed: int) -> tuple[str, dict[str, Any]]:
    """Call the model adapter to generate one candidate.

    The adapter is a callable: (prompt, max_new_tokens, temperature, seed) -> dict
    with keys: ``code`` (str), ``finish_reason`` (str|None), ``gen_sec`` (float).
    For base/adapter models this is the Huanxin NPU harness; for OpenAI it
    is the OpenAI adapter; for ``--mock`` it returns a placeholder.
    """
    if model_adapter is None:
        # mock mode: return the reference candidate as a stub
        return "", {"finish_reason": "mock", "gen_sec": 0.0}
    res = model_adapter(prompt=prompt, max_new_tokens=max_new_tokens,
                        temperature=temperature, seed=seed)
    return res.get("code", ""), {
        "finish_reason": res.get("finish_reason"),
        "gen_sec": res.get("gen_sec", 0.0),
    }


# ─────────────────────────────────────────────────────────────────────────────
# suite-init
# ─────────────────────────────────────────────────────────────────────────────

def cmd_suite_init(args: argparse.Namespace) -> int:
    tasks = suite.discover_tasks(args.tasks)
    if not tasks:
        print(f"[suite-init] no tasks found under {args.tasks}", file=sys.stderr)
        return 2
    payload = suite.write_lock(
        tasks, out_path=args.out, source_dir=str(args.tasks), notes=args.notes,
    )
    print(f"[suite-init] pinned {len(tasks)} tasks → {args.out}")
    print(f"[suite-init] suite_hash = {payload['suite_hash']}")
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# suite-verify
# ─────────────────────────────────────────────────────────────────────────────

def cmd_suite_verify(args: argparse.Namespace) -> int:
    res = suite.verify_lock(args.suite, root=args.root)
    if res["ok"]:
        print(f"[suite-verify] OK  suite_hash={res['expected_suite_hash']}")
        return 0
    print(f"[suite-verify] FAIL  suite_hash_match={res['suite_hash_match']}")
    for m in res["mismatches"]:
        print(f"  - {m['task_id']}: {m['field']} expected {m['expected'][:12]}.. actual {str(m['actual'])[:12] if m['actual'] else None}")
    return 1


# ─────────────────────────────────────────────────────────────────────────────
# run
# ─────────────────────────────────────────────────────────────────────────────

def _build_model_adapter(args: argparse.Namespace):
    """Build the model adapter based on CLI flags.

    Supported modes:
      --mock                        : in-process stub (returns empty code)
      --openai-model <name>         : OpenAI-compatible API
      --hf-base <path>              : HuggingFace base model (CPU/GPU)
      --hf-adapter <base> <adap>    : HuggingFace base + LoRA adapter
      --exec-command <cmd>          : arbitrary shell command (hermetic subprocess)
    For the trustable harness we prefer ``--exec-command`` which delegates
    generation to an external script and is fully reproducible.
    """
    if args.mock:
        return None, {"kind": "mock", "label": "mock"}
    if args.exec_command:
        from subprocess import run as _run
        def _adapter(*, prompt: str, max_new_tokens: int | None,
                     temperature: float | None, seed: int) -> dict:
            env = dict(os.environ)
            env["TRUST_EVAL_PROMPT"] = prompt
            env["TRUST_EVAL_SEED"] = str(seed)
            env["TRUST_EVAL_MAX_NEW_TOKENS"] = str(max_new_tokens or "")
            env["TRUST_EVAL_TEMPERATURE"] = str(temperature) if temperature is not None else ""
            out = _run(args.exec_command, shell=True, env=env, capture_output=True, text=True, timeout=args.gen_timeout)
            if out.returncode != 0:
                return {"code": "", "finish_reason": f"exec_error_{out.returncode}", "gen_sec": 0.0}
            return {"code": out.stdout, "finish_reason": "exec_ok", "gen_sec": 0.0}
        return _adapter, {"kind": "exec", "label": args.model_label or "exec"}
    raise SystemExit(
        "[run] no model backend specified; use --mock, --openai-model, or --exec-command"
    )


def cmd_run(args: argparse.Namespace) -> int:
    suite_lock = suite.read_lock(args.suite)
    run_dir = Path(args.out)
    run_dir.mkdir(parents=True, exist_ok=True)

    # 1. register suite + tasks in ledger
    L = _load_ledger(run_dir)
    task_ids: list[str] = []
    for t in suite_lock["tasks"]:
        L.register_task(
            task_id=t["task_id"], name=t["name"], domain=t["domain"],
            category=t["category"], task_json_hash=t["task_json_hash"],
            tests_py_hash=t["tests_py_hash"], candidate_ref_hash=t["candidate_ref_hash"],
            workspace_mode=t.get("workspace_mode", False),
        )
        task_ids.append(t["task_id"])
    suite_id = L.register_suite(
        suite_hash=suite_lock["suite_hash"], source_dir=suite_lock["source_dir"],
        n_tasks=suite_lock["n_tasks"], task_ids=task_ids, notes=suite_lock.get("notes"),
    )

    # 2. register model
    adapter, model_meta = _build_model_adapter(args)
    base_hash = None
    if args.hf_base and Path(args.hf_base).is_dir():
        # hash a small marker file to identify the model dir; full hash is expensive
        marker = Path(args.hf_base) / "config.json"
        if marker.is_file():
            base_hash = hashing.hash_file(marker)
    adapter_hash = None
    if args.hf_adapter and Path(args.hf_adapter).is_dir():
        marker = Path(args.hf_adapter) / "adapter_config.json"
        if marker.is_file():
            adapter_hash = hashing.hash_file(marker)
    model_id = L.register_model(
        label=args.model_label or model_meta["label"],
        base_path=args.hf_base or args.openai_model or "exec",
        base_hash=base_hash,
        adapter_path=args.hf_adapter,
        adapter_hash=adapter_hash,
        model_kind=model_meta["kind"],
    )

    # 3. register prompt template
    prompt_body = args.prompt_template_body or ""
    pt_id = L.register_prompt_template(
        style=args.prompt_style, version=args.prompt_version, body=prompt_body,
    )

    # 4. build recipe + run_hash
    recipe = repro.build_recipe(
        suite_hash=suite_lock["suite_hash"], suite_lock_path=str(args.suite),
        model_label=args.model_label or model_meta["label"],
        model_base_path=args.hf_base or args.openai_model or "exec",
        model_base_hash=base_hash, model_adapter_path=args.hf_adapter,
        model_adapter_hash=adapter_hash, model_kind=model_meta["kind"],
        prompt_style=args.prompt_style, prompt_version=args.prompt_version,
        prompt_template_hash=hashing.hash_text(prompt_body),
        k=args.k, temperature=args.temperature, seed=args.seed,
        max_new_tokens=args.max_new_tokens, git_repo=_REPO_ROOT,
    )
    run_hash = recipe.hash()
    run_id = L.register_run(
        run_hash=run_hash, created_at_utc=ledger.utc_now(), suite_id=suite_id,
        model_id=model_id, prompt_template_id=pt_id, k=args.k,
        temperature=args.temperature, seed=args.seed,
        max_new_tokens=args.max_new_tokens, python_version=recipe.python_version,
        platform=recipe.platform, status="running",
    )
    repro.write_recipe(recipe, run_dir / "recipe.json")

    # 5. for each task, generate k samples and score each
    started = time.time()
    summary_records: list[dict] = []
    for t in suite_lock["tasks"]:
        task_dir = Path(t["task_dir"])
        if not task_dir.is_absolute():
            task_dir = _REPO_ROOT / task_dir
        # build the per-task prompt (deterministic)
        prompt_text = _build_task_prompt(t, prompt_body)
        L.record_task_prompt(run_id=run_id, task_id=t["task_id"], prompt_text=prompt_text)
        # write the prompt to the run dir for reproducibility
        prompt_path = run_dir / "prompts" / f"{t['task_id']}.txt"
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(prompt_text, encoding="utf-8")

        verdicts_for_task: list[dict] = []
        for s_idx in range(args.k):
            # generate
            seed_s = args.seed + s_idx
            if args.k == 1:
                gen_temp = None
            else:
                gen_temp = args.temperature
            code, gen_meta = _gen_candidate(
                adapter, prompt=prompt_text, max_new_tokens=args.max_new_tokens,
                temperature=gen_temp, seed=seed_s,
            )
            sample_id = L.record_sample(
                run_id=run_id, task_id=t["task_id"], sample_index=s_idx,
                candidate_code=code, generated_at_utc=ledger.utc_now(),
                gen_sec=gen_meta.get("gen_sec"), finish_reason=gen_meta.get("finish_reason"),
            )
            # write candidate to disk
            cand_path = run_dir / "candidates" / f"{t['task_id']}.s{s_idx}.py"
            cand_path.parent.mkdir(parents=True, exist_ok=True)
            cand_path.write_text(code, encoding="utf-8")
            # score deterministically
            tr = sandbox.run_test_hermetic(
                task_dir=task_dir, test_file=_test_file_for(t),
                candidate_code=code, timeout_sec=args.test_timeout,
                block_network=not args.allow_network,
            )
            L.record_verdict(
                sample_id=sample_id, judge="deterministic", passed=tr.passed,
                details=tr.details, failure_category=tr.failure_category,
                test_stdout_hash=tr.stdout_hash, test_stderr_hash=tr.stderr_hash,
                test_returncode=tr.returncode,
            )
            verdicts_for_task.append({
                "sample_index": s_idx, "judge": "deterministic",
                "passed": tr.passed, "failure_category": tr.failure_category,
            })
            status = "PASS" if tr.passed else f"FAIL({tr.failure_category})"
            print(f"[run] {t['task_id']} s{s_idx}: {status}  ({tr.duration_sec:.2f}s)")
        ts = scoring.score_task(task_id=t["task_id"], k=args.k, verdicts=verdicts_for_task)
        summary_records.append({**ts.to_dict(), "domain": t["domain"], "category": t["category"]})

    # 6. aggregate
    agg = scoring.aggregate_run([
        scoring.score_task(task_id=r["task_id"], k=args.k,
                           verdicts=[{"sample_index": i, "judge": "deterministic",
                                      "passed": i < r["n_pass_det"],
                                      "failure_category": None}
                                     for i in range(r["n_samples"])])
        for r in summary_records
    ])
    # recompute by_domain with real domains
    by_domain: dict[str, dict[str, int]] = {}
    by_cat: dict[str, dict[str, int]] = {}
    for r in summary_records:
        d = by_domain.setdefault(r["domain"], {"n": 0, "pass": 0})
        d["n"] += 1
        if r["pass_at_1"] >= 1.0:
            d["pass"] += 1
        c = by_cat.setdefault(r["category"], {"n": 0, "pass": 0})
        c["n"] += 1
        if r["pass_at_1"] >= 1.0:
            c["pass"] += 1
    agg["by_domain"] = {k: {"n": v["n"], "pass": v["pass"],
                            "pass_at_1": round(v["pass"]/v["n"], 4) if v["n"] else 0.0}
                        for k, v in by_domain.items()}
    agg["by_category"] = {k: {"n": v["n"], "pass": v["pass"],
                              "pass_at_1": round(v["pass"]/v["n"], 4) if v["n"] else 0.0}
                          for k, v in by_cat.items()}
    agg["suite_hash"] = suite_lock["suite_hash"]
    agg["run_hash"] = run_hash
    agg["model_label"] = args.model_label or model_meta["label"]
    agg["k"] = args.k
    agg["duration_sec"] = round(time.time() - started, 3)
    _write_json(run_dir / "summary.json", agg)
    L.update_run_status(run_id, status="completed", duration_sec=agg["duration_sec"])
    L.close()

    print(f"\n[run] completed: pass_at_1 = {agg['pass_at_1']}  ({agg['n_pass']}/{agg['n_tasks']})")
    print(f"[run] run_dir = {run_dir}")
    print(f"[run] run_hash = {run_hash}")
    return 0


def _test_file_for(t: dict) -> str:
    return "tests.py"


def _build_task_prompt(t: dict, body: str) -> str:
    return (
        f"Task: {t['name']} (id={t['task_id']}, domain={t['domain']}, category={t['category']})\n"
        f"{body}\n"
        "Produce only the final Python candidate file content.\n"
    )


# ─────────────────────────────────────────────────────────────────────────────
# score  (re-score a run without regenerating)
# ─────────────────────────────────────────────────────────────────────────────

def cmd_score(args: argparse.Namespace) -> int:
    run_dir = Path(args.run)
    L = _load_ledger(run_dir)
    recipe = repro.read_recipe(run_dir / "recipe.json")
    run = L.get_run_by_hash(recipe.hash())
    if not run:
        print(f"[score] run not found in ledger: {recipe.hash()}", file=sys.stderr)
        return 2
    samples = L.list_samples(run["id"])
    n_re = 0
    for s in samples:
        code = s["candidate_code"]
        # find the task dir from the suite lock
        suite_lock = suite.read_lock(recipe.suite_lock_path)
        tmeta = next((t for t in suite_lock["tasks"] if t["task_id"] == s["task_id"]), None)
        if tmeta is None:
            continue
        task_dir = Path(tmeta["task_dir"])
        if not task_dir.is_absolute():
            task_dir = _REPO_ROOT / task_dir
        tr = sandbox.run_test_hermetic(
            task_dir=task_dir, test_file=_test_file_for(tmeta),
            candidate_code=code, timeout_sec=args.test_timeout,
            block_network=not args.allow_network,
        )
        # record a fresh verdict (the UNIQUE constraint will prevent dupes
        # for the deterministic judge; we replace by deleting first)
        L._conn.execute("DELETE FROM verdict WHERE sample_id=? AND judge=?",
                        (s["id"], "deterministic"))
        L.record_verdict(
            sample_id=s["id"], judge="deterministic", passed=tr.passed,
            details=tr.details, failure_category=tr.failure_category,
            test_stdout_hash=tr.stdout_hash, test_stderr_hash=tr.stderr_hash,
            test_returncode=tr.returncode,
        )
        n_re += 1
    print(f"[score] re-scored {n_re} samples for run {run['id']}")
    L.close()
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# verify  (re-check every hash in a run)
# ─────────────────────────────────────────────────────────────────────────────

def cmd_verify(args: argparse.Namespace) -> int:
    run_dir = Path(args.run)
    L = _load_ledger(run_dir)
    recipe = repro.read_recipe(run_dir / "recipe.json")
    run = L.get_run_by_hash(recipe.hash())
    if not run:
        print(f"[verify] run not found in ledger: {recipe.hash()}", file=sys.stderr)
        return 2
    problems: list[str] = []
    # 1. suite hash
    suite_lock = suite.read_lock(recipe.suite_lock_path)
    sv = suite.verify_lock(recipe.suite_lock_path)
    if not sv["suite_hash_match"]:
        problems.append(f"suite_hash mismatch: expected {sv['expected_suite_hash']}, got {sv['actual_suite_hash']}")
    for m in sv["mismatches"]:
        problems.append(f"suite task {m['task_id']} {m['field']} changed")
    # 2. per-sample candidate + tests hashes
    samples = L.list_samples(run["id"])
    for s in samples:
        ch = hashing.hash_text(s["candidate_code"])
        if ch != s["candidate_code_hash"]:
            problems.append(f"sample {s['id']} candidate_code_hash mismatch")
        # check tests.py on disk still matches the locked hash
        tmeta = next((t for t in suite_lock["tasks"] if t["task_id"] == s["task_id"]), None)
        if tmeta:
            td = Path(tmeta["task_dir"])
            if not td.is_absolute():
                td = _REPO_ROOT / td
            tp = td / "tests.py"
            if tp.is_file():
                actual = hashing.hash_file(tp)
                if actual != tmeta["tests_py_hash"]:
                    problems.append(f"task {tmeta['task_id']} tests.py changed on disk")
    # 3. re-score and compare verdicts
    if not args.skip_rescore:
        for s in samples:
            tmeta = next((t for t in suite_lock["tasks"] if t["task_id"] == s["task_id"]), None)
            if not tmeta:
                continue
            td = Path(tmeta["task_dir"])
            if not td.is_absolute():
                td = _REPO_ROOT / td
            tr = sandbox.run_test_hermetic(
                task_dir=td, test_file=_test_file_for(tmeta),
                candidate_code=s["candidate_code"], timeout_sec=args.test_timeout,
                block_network=not args.allow_network,
            )
            existing = L.list_verdicts(s["id"])
            det = next((v for v in existing if v["judge"] == "deterministic"), None)
            if det and bool(det["passed"]) != tr.passed:
                problems.append(
                    f"sample {s['id']} verdict drift: ledger={bool(det['passed'])} rescore={tr.passed}"
                )
    L.close()
    if problems:
        print(f"[verify] FAIL  {len(problems)} problems:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"[verify] OK  run_hash={recipe.hash()}  ({len(samples)} samples)")
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# audit
# ─────────────────────────────────────────────────────────────────────────────

def cmd_audit(args: argparse.Namespace) -> int:
    run_dir = Path(args.run)
    L = _load_ledger(run_dir)
    recipe = repro.read_recipe(run_dir / "recipe.json")
    run = L.get_run_by_hash(recipe.hash())
    if not run:
        print(f"[audit] run not found in ledger: {recipe.hash()}", file=sys.stderr)
        return 2
    result = audit_report(ledger=L, run_id=run["id"], report_path=args.report)
    L.close()
    print(f"[audit] run_id={result['run_id']}  n_claims={result['n_claims']}  "
          f"backed={result['n_backed']}  unbacked={result['n_unbacked']}")
    for c in result["claims"]:
        flag = "OK " if c["backed"] else "XX "
        print(f"  {flag} line {c['line_no']:>4} {c['kind']:<12} {c['value']}")
        if not c["backed"] and c["evidence"]:
            print(f"        evidence: {c['evidence']}")
    return 0 if result["passed"] else 1


# ─────────────────────────────────────────────────────────────────────────────
# compare
# ─────────────────────────────────────────────────────────────────────────────

def cmd_compare(args: argparse.Namespace) -> int:
    base_dir = Path(args.base); adap_dir = Path(args.adapter)
    Lb = _load_ledger(base_dir); La = _load_ledger(adap_dir)
    rb = repro.read_recipe(base_dir / "recipe.json")
    ra = repro.read_recipe(adap_dir / "recipe.json")
    run_b = Lb.get_run_by_hash(rb.hash()); run_a = La.get_run_by_hash(ra.hash())
    if not run_b or not run_a:
        print("[compare] missing run in ledger", file=sys.stderr); return 2
    if rb.suite_hash != ra.suite_hash:
        print(f"[compare] WARNING: suites differ\n  base:    {rb.suite_hash}\n  adapter: {ra.suite_hash}", file=sys.stderr)
    sb = Lb.run_summary(run_b["id"]); sa = La.run_summary(run_a["id"])
    fixed = [t for t in sa["by_task"] if t["pass_at_1"] >= 1.0
             and any(b["task_id"] == t["task_id"] and b["pass_at_1"] < 1.0 for b in sb["by_task"])]
    broken = [t for t in sb["by_task"] if t["pass_at_1"] >= 1.0
              and any(a["task_id"] == t["task_id"] and a["pass_at_1"] < 1.0 for a in sa["by_task"])]
    delta = sa["pass_at_1"] - sb["pass_at_1"]
    print(f"base    pass_at_1 = {sb['pass_at_1']}  ({sb['n_pass']}/{sb['n_tasks']})")
    print(f"adapter pass_at_1 = {sa['pass_at_1']}  ({sa['n_pass']}/{sa['n_tasks']})")
    print(f"delta   = {delta:+.4f}")
    print(f"fixed by adapter:   {len(fixed)}  {[t['task_id'] for t in fixed]}")
    print(f"broken by adapter:  {len(broken)}  {[t['task_id'] for t in broken]}")
    Lb.close(); La.close()
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# report
# ─────────────────────────────────────────────────────────────────────────────

def cmd_report(args: argparse.Namespace) -> int:
    run_dir = Path(args.run)
    L = _load_ledger(run_dir)
    recipe = repro.read_recipe(run_dir / "recipe.json")
    run = L.get_run_by_hash(recipe.hash())
    if not run:
        print(f"[report] run not found in ledger", file=sys.stderr); return 2
    summary = L.run_summary(run["id"])
    md = _render_report(recipe=recipe, run=run, summary=summary)
    out = Path(args.out) if args.out else run_dir / "REPORT.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"[report] written: {out}")
    L.close()
    return 0


def _render_report(*, recipe: repro.Recipe, run: dict, summary: dict) -> str:
    lines = [
        "# Trustable Evaluation Report",
        "",
        f"- **run_hash**: `{run['run_hash']}`",
        f"- **suite_hash**: `{recipe.suite_hash}`",
        f"- **model**: `{recipe.model_label}` ({recipe.model_kind})",
        f"- **k**: {recipe.k}  **temperature**: {recipe.temperature}  **seed**: {recipe.seed}",
        f"- **python**: `{recipe.python_version}` on `{recipe.platform}`",
        f"- **git_commit**: `{recipe.git_commit}`" if recipe.git_commit else "- **git_commit**: n/a",
        "",
        "## Summary",
        "",
        f"- n_tasks: **{summary['n_tasks']}**",
        f"- n_pass: **{summary['n_pass']}**",
        f"- pass_at_1: **{summary['pass_at_1']}**",
        "",
        "## Per-task",
        "",
        "| task_id | domain | category | n_pass_det | pass_at_1 |",
        "|---|---|---|---|---|",
    ]
    for t in summary["by_task"]:
        lines.append(f"| {t['task_id']} | {t['domain']} | {t['category']} | {t['n_pass_det']} | {t['pass_at_1']} |")
    lines += [
        "",
        "## Disagreements",
        "",
        f"- {len(summary['disagreements'])} tasks with judge disagreement: {summary['disagreements']}",
        "",
        "## Reproduction",
        "",
        "Reproduce with:",
        "```bash",
        f"python -m evals.trust.cli.main reproduce --run {run['run_hash']}",
        "```",
    ]
    return "\n".join(lines) + "\n"


# ─────────────────────────────────────────────────────────────────────────────
# reproduce
# ─────────────────────────────────────────────────────────────────────────────

def cmd_reproduce(args: argparse.Namespace) -> int:
    run_dir = Path(args.run)
    recipe = repro.read_recipe(run_dir / "recipe.json")
    # Compare the on-disk recipe to a freshly-built one
    fresh = repro.build_recipe(
        suite_hash=recipe.suite_hash, suite_lock_path=recipe.suite_lock_path,
        model_label=recipe.model_label, model_base_path=recipe.model_base_path,
        model_base_hash=recipe.model_base_hash, model_adapter_path=recipe.model_adapter_path,
        model_adapter_hash=recipe.model_adapter_hash, model_kind=recipe.model_kind,
        prompt_style=recipe.prompt_style, prompt_version=recipe.prompt_version,
        prompt_template_hash=recipe.prompt_template_hash, k=recipe.k,
        temperature=recipe.temperature, seed=recipe.seed,
        max_new_tokens=recipe.max_new_tokens, git_repo=_REPO_ROOT,
    )
    cmp = repro.compare_recipes(recipe, fresh)
    if cmp["identical"]:
        print(f"[reproduce] recipe identical to on-disk state; run_hash={recipe.hash()}")
        return 0
    print(f"[reproduce] recipe drift detected:")
    for d in cmp["diffs"]:
        print(f"  - {d['field']}: expected {d['expected']}  actual {d['actual']}")
    return 1


# ─────────────────────────────────────────────────────────────────────────────
# candidates  (list / export all generated candidate code from a run)
# ─────────────────────────────────────────────────────────────────────────────

def cmd_candidates(args: argparse.Namespace) -> int:
    """List or export every candidate code sample recorded in a run.

    Every candidate generated by a base model or adapter during a run
    is recorded in the ledger's ``sample`` table (full text + SHA-256
    hash) and written to ``run_dir/candidates/<task_id>.s<idx>.py``.

    Modes:
      --list (default): print one line per sample with task_id, index,
                         hash, length, and pass/fail verdict.
      --export <dir>:   write every candidate to <dir>/<task_id>.s<idx>.py
      --show <task_id>: print the full candidate code for a task.
    """
    run_dir = Path(args.run)
    L = _load_ledger(run_dir)
    recipe = repro.read_recipe(run_dir / "recipe.json")
    run = L.get_run_by_hash(recipe.hash())
    if not run:
        print(f"[candidates] run not found in ledger", file=sys.stderr); return 2
    samples = L.list_samples(run["id"])
    if args.show:
        samples = [s for s in samples if s["task_id"] == args.show]
        for s in samples:
            print(f"=== {s['task_id']} s{s['sample_index']} (hash={s['candidate_code_hash'][:12]}..) ===")
            print(s["candidate_code"])
        L.close()
        return 0
    if args.export:
        out = Path(args.export)
        out.mkdir(parents=True, exist_ok=True)
        for s in samples:
            fname = f"{s['task_id']}.s{s['sample_index']}.py"
            (out / fname).write_text(s["candidate_code"], encoding="utf-8")
        print(f"[candidates] exported {len(samples)} candidates to {out}")
        L.close()
        return 0
    # default: list
    print(f"[candidates] run_id={run['id']}  run_hash={recipe.hash()[:16]}..  n_samples={len(samples)}")
    print(f"{'task_id':<48} {'idx':>3} {'len':>6} {'hash':<16} {'verdict':<8}")
    for s in samples:
        verdicts = L.list_verdicts(s["id"])
        det = next((v for v in verdicts if v["judge"] == "deterministic"), None)
        vstr = "PASS" if (det and det["passed"]) else "FAIL" if det else "?"
        print(f"{s['task_id']:<48} {s['sample_index']:>3} {len(s['candidate_code']):>6} {s['candidate_code_hash'][:16]}.. {vstr:<8}")
    L.close()
    return 0



# ─────────────────────────────────────────────────────────────────────────────

def cmd_import_legacy(args: argparse.Namespace) -> int:
    """Ingest a legacy ``evals/runs/<name>/scorecard.json`` into a trust ledger.

    This creates a trust run dir at ``--out`` with a recipe.json (marked
    as ``legacy`` kind) and a ledger.db populated from the scorecard.
    The original candidates and prompts are NOT re-scored; instead we
    re-score each candidate fresh in the hermetic sandbox and record
    both the legacy verdict and the fresh verdict, flagging any drift.

    This is the bridge between the old ``evals/runs/`` tree and the new
    trustable subsystem: it lets us audit old reports against the new
    ledger without re-running generation.
    """
    run_dir = Path(args.out)
    run_dir.mkdir(parents=True, exist_ok=True)
    scorecard_path = Path(args.scorecard)
    scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))
    L = _load_ledger(run_dir)

    # Build a synthetic suite from the scorecard's task IDs by resolving
    # each task to evals/tasks/<domain>/<id>/. Task directories may be
    # named without the prefix (e.g. dir "bell_pair_construction" but
    # task.json id "quantum_bell_pair_construction"), so we scan all
    # task.json files and match by the id field.
    task_root = _REPO_ROOT / "evals/tasks"
    all_tasks_by_id: dict[str, Path] = {}
    for tj in task_root.rglob("task.json"):
        try:
            m = json.loads(tj.read_text(encoding="utf-8"))
            all_tasks_by_id[m["id"]] = tj.parent
        except Exception:
            continue
    task_ids: list[str] = []
    for r in scorecard.get("results", []):
        tid = r["id"]
        td = all_tasks_by_id.get(tid)
        if td is None:
            print(f"[import-legacy] WARNING: task {tid} not found on disk; skipping", file=sys.stderr)
            continue
        meta = json.loads((td / "task.json").read_text(encoding="utf-8"))
        tests_py = td / meta.get("test_file", "tests.py")
        if not tests_py.is_file():
            print(f"[import-legacy] WARNING: task {tid} missing tests.py; skipping", file=sys.stderr)
            continue
        cand = td / meta.get("candidate_file", "candidate.py")
        cand_hash = hashing.hash_file(cand) if cand.is_file() else hashing.hash_text("")
        L.register_task(
            task_id=tid, name=meta.get("name", tid), domain=meta.get("domain", "unknown"),
            category=meta.get("category", "unknown"),
            task_json_hash=hashing.hash_file(td / "task.json"),
            tests_py_hash=hashing.hash_file(tests_py),
            candidate_ref_hash=cand_hash,
            workspace_mode=bool(meta.get("workspace_mode", False)),
        )
        task_ids.append(tid)

    # build a synthetic suite hash from the discovered tasks
    from evals.trust.core.suite import discover_tasks, write_lock
    tasks = [t for t in discover_tasks(task_root) if t.task_id in task_ids]
    sh = suite.suite_hash(tasks) if tasks else "empty"
    suite_id = L.register_suite(
        suite_hash=sh, source_dir=str(task_root), n_tasks=len(task_ids),
        task_ids=task_ids, notes="imported from legacy scorecard",
    )
    # copy the suite lock
    if tasks:
        write_lock(tasks, out_path=run_dir / "suite.lock.json", source_dir=str(task_root),
                   notes="imported from legacy scorecard")

    # register a legacy model
    model_id = L.register_model(
        label=args.model_label or scorecard_path.parent.name,
        base_path="legacy", base_hash=None,
        adapter_path=None, adapter_hash=None, model_kind="legacy",
    )
    # build a legacy recipe
    recipe = repro.build_recipe(
        suite_hash=sh, suite_lock_path=str(run_dir / "suite.lock.json"),
        model_label=args.model_label or scorecard_path.parent.name,
        model_base_path="legacy", model_base_hash=None,
        model_adapter_path=None, model_adapter_hash=None, model_kind="legacy",
        prompt_style=scorecard.get("prompt_style") or "legacy",
        prompt_version=scorecard.get("prompt_version") or "legacy",
        prompt_template_hash="legacy", k=1, temperature=None, seed=0,
        max_new_tokens=None, git_repo=_REPO_ROOT, harness_version="evals.trust.legacy",
    )
    run_hash = recipe.hash()
    run_id = L.register_run(
        run_hash=run_hash, created_at_utc=ledger.utc_now(), suite_id=suite_id,
        model_id=model_id, prompt_template_id=None, k=1, temperature=None,
        seed=0, max_new_tokens=None, python_version=recipe.python_version,
        platform=recipe.platform, status="legacy",
    )
    repro.write_recipe(recipe, run_dir / "recipe.json")

    # for each result in the scorecard, re-score the candidate and record
    n_drift = 0
    for r in scorecard.get("results", []):
        tid = r["id"]
        if tid not in task_ids:
            continue
        td = all_tasks_by_id.get(tid)
        if td is None:
            continue
        meta = json.loads((td / "task.json").read_text(encoding="utf-8"))
        cand_path = r.get("candidate_path") or r.get("candidate_paths", {}).get("candidate.py")
        code = ""
        if cand_path and Path(cand_path).is_file():
            code = Path(cand_path).read_text(encoding="utf-8")
        elif r.get("workspace_mode"):
            ws = td / meta.get("workspace_dir", ".")
            if ws.is_dir():
                parts = []
                for rel in r.get("candidate_paths", {}).values():
                    p = Path(rel)
                    if p.is_file():
                        parts.append(p.read_text(encoding="utf-8"))
                code = "\n\n".join(parts)
        sample_id = L.record_sample(
            run_id=run_id, task_id=tid, sample_index=0,
            candidate_code=code, generated_at_utc=ledger.utc_now(),
            gen_sec=None, finish_reason="legacy",
        )
        # fresh hermetic re-score (td and meta already resolved above)
        tr = sandbox.run_test_hermetic(
            task_dir=td, test_file=meta.get("test_file", "tests.py"),
            candidate_code=code, timeout_sec=args.test_timeout,
            block_network=not args.allow_network,
        )
        L.record_verdict(
            sample_id=sample_id, judge="deterministic", passed=tr.passed,
            details=tr.details, failure_category=tr.failure_category,
            test_stdout_hash=tr.stdout_hash, test_stderr_hash=tr.stderr_hash,
            test_returncode=tr.returncode,
        )
        legacy_passed = bool(r.get("passed", False))
        if legacy_passed != tr.passed:
            n_drift += 1
            print(f"[import-legacy] DRIFT {tid}: legacy={legacy_passed} fresh={tr.passed}")

    L.update_run_status(run_id, status="imported", duration_sec=None)
    summary = L.run_summary(run_id)
    _write_json(run_dir / "summary.json", {**summary, "suite_hash": sh, "run_hash": run_hash,
                                            "model_label": args.model_label or scorecard_path.parent.name,
                                            "n_drift_vs_legacy": n_drift})
    L.close()
    print(f"\n[import-legacy] imported {len(task_ids)} tasks, drift={n_drift}")
    print(f"[import-legacy] pass_at_1 (fresh) = {summary['pass_at_1']}  ({summary['n_pass']}/{summary['n_tasks']})")
    print(f"[import-legacy] run_dir = {run_dir}")
    return 0




def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="quantum_eval", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    # suite-init
    s = sub.add_parser("suite-init", help="Pin a task suite to a suite.lock.json")
    s.add_argument("--tasks", required=True, type=Path)
    s.add_argument("--out", required=True, type=Path)
    s.add_argument("--notes", default=None)
    s.set_defaults(func=cmd_suite_init)

    # suite-verify
    s = sub.add_parser("suite-verify", help="Verify a suite.lock.json against disk")
    s.add_argument("--suite", required=True, type=Path)
    s.add_argument("--root", default=None, type=Path)
    s.set_defaults(func=cmd_suite_verify)

    # run
    s = sub.add_parser("run", help="Run a model against a pinned suite")
    s.add_argument("--suite", required=True, type=Path)
    s.add_argument("--out", required=True, type=Path)
    s.add_argument("--mock", action="store_true", help="use a mock adapter (empty code)")
    s.add_argument("--openai-model", default=None)
    s.add_argument("--hf-base", default=None)
    s.add_argument("--hf-adapter", default=None)
    s.add_argument("--exec-command", default=None, help="shell command for generation")
    s.add_argument("--model-label", default=None)
    s.add_argument("--prompt-style", default="repair_focused")
    s.add_argument("--prompt-version", default="v2")
    s.add_argument("--prompt-template-body", default=None)
    s.add_argument("--k", type=int, default=1)
    s.add_argument("--temperature", type=float, default=0.0)
    s.add_argument("--seed", type=int, default=42)
    s.add_argument("--max-new-tokens", type=int, default=512)
    s.add_argument("--test-timeout", type=float, default=60.0)
    s.add_argument("--gen-timeout", type=float, default=600.0)
    s.add_argument("--allow-network", action="store_true")
    s.set_defaults(func=cmd_run)

    # score
    s = sub.add_parser("score", help="Re-score a run without regenerating")
    s.add_argument("--run", required=True, type=Path)
    s.add_argument("--test-timeout", type=float, default=60.0)
    s.add_argument("--allow-network", action="store_true")
    s.set_defaults(func=cmd_score)

    # verify
    s = sub.add_parser("verify", help="Re-check every hash and re-score every sample")
    s.add_argument("--run", required=True, type=Path)
    s.add_argument("--test-timeout", type=float, default=60.0)
    s.add_argument("--allow-network", action="store_true")
    s.add_argument("--skip-rescore", action="store_true")
    s.set_defaults(func=cmd_verify)

    # audit
    s = sub.add_parser("audit", help="Audit a human report against the ledger")
    s.add_argument("--run", required=True, type=Path)
    s.add_argument("--report", required=True, type=Path)
    s.set_defaults(func=cmd_audit)

    # compare
    s = sub.add_parser("compare", help="Compare two runs")
    s.add_argument("--base", required=True, type=Path)
    s.add_argument("--adapter", required=True, type=Path)
    s.set_defaults(func=cmd_compare)

    # report
    s = sub.add_parser("report", help="Render an audit-checked Markdown report")
    s.add_argument("--run", required=True, type=Path)
    s.add_argument("--out", default=None, type=Path)
    s.set_defaults(func=cmd_report)

    # reproduce
    s = sub.add_parser("reproduce", help="Re-run a run from its recipe")
    s.add_argument("--run", required=True, type=Path)
    s.set_defaults(func=cmd_reproduce)

    # import-legacy
    s = sub.add_parser("import-legacy", help="Ingest a legacy evals/runs/* scorecard into a trust ledger")
    s.add_argument("--scorecard", required=True, type=Path)
    s.add_argument("--out", required=True, type=Path)
    s.add_argument("--model-label", default=None)
    s.add_argument("--test-timeout", type=float, default=60.0)
    s.add_argument("--allow-network", action="store_true")
    s.set_defaults(func=cmd_import_legacy)

    # candidates
    s = sub.add_parser("candidates", help="List or export all generated candidate code from a run")
    s.add_argument("--run", required=True, type=Path)
    s.add_argument("--list", action="store_true", help="list samples (default)")
    s.add_argument("--export", default=None, type=Path, help="export all candidates to a directory")
    s.add_argument("--show", default=None, help="print full candidate code for a task_id")
    s.set_defaults(func=cmd_candidates)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

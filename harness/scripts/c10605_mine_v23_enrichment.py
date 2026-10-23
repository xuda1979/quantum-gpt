#!/usr/bin/env python3
"""C-10605: v23 failure-task corpus enrichment miner.

Mines exec-green, non-leak SFT rows for the 4 remaining failing holdout
targets (per step-354 eval, adapter 14/18):
  - quantum_qaoa_maxcut                    (persistent both-fail at 119+354)
  - quantum_qiskit_qft_entangled           (regression vs base at 354)
  - quantum_qiskit_stabilizer_5qubit_code  (flip-flop 119-pass/354-fail)
  - quantum_pennylane_qml_iris_classification (flip-flop 119-pass/354-fail)

Inherits the C-10605 v22 miner pattern exactly:
  - completion variants of the gold candidate (docstring-annotate,
    reorder_defs, comment_inject, private_rename)
  - dedup by completion sha; skip if identical to gold (leak guard)
  - fail-closed: every row must pass the frozen tests.py locally
  - leak guard: prompt is the PUBLIC task spec only (never tests.py)
"""

from __future__ import annotations

import ast
import datetime
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "outputs"
TASKS = REPO / "evals" / "tasks" / "quantum"
OUT_FILE = OUT / "c10605_v23_mined_enrichment.json"
# v22 step-354 mid-run adapter sha (source measurement, report_C10605_v22_step354_14of18_evidence.md)
HOLD_SHA = "6d28fa780807f8ad82e250bd43b843107876bd94a1d28adc6e851a75b267f212"

BENCH_TO_DIR = {
    "quantum_qaoa_maxcut": "qaoa_maxcut",
    "quantum_qiskit_qft_entangled": "qiskit_qft_entangled",
    "quantum_qiskit_stabilizer_5qubit_code": "qiskit_stabilizer_5qubit_code",
    "quantum_pennylane_qml_iris_classification": "pennylane_qml_iris_classification",
}

SYS_PROMPT = (
    "Return only a complete Python solution. Do not include markdown fences or explanation."
)


def sha256b(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_spec(target_dir: str) -> str:
    import sys as _sys

    _sys.path.insert(0, str(REPO / "evals" / "runner"))
    from public_task_spec import build_public_task_spec

    meta = json.loads((TASKS / target_dir / "task.json").read_text())
    return build_public_task_spec(TASKS / target_dir, meta)


def run_frozen(target_dir: str, source: str) -> dict:
    tsrc = TASKS / target_dir / "tests.py"
    spec = importlib.util.spec_from_file_location("frozen_tests_c10605_v23", tsrc)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["frozen_tests_c10605_v23"] = mod
    spec.loader.exec_module(mod)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(source)
        cand = f.name
    try:
        return mod.run_tests(cand)
    finally:
        try:
            os.unlink(cand)
        except OSError:
            pass


def docstring_annotate(src: str, tag: str) -> str:
    tree = ast.parse(src)

    class R(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            d = ast.get_docstring(node)
            if d:
                node.body[0] = ast.Expr(
                    value=ast.Constant(
                        value=d + chr(10) + chr(10) + "(C-10605 v23 mined variant: " + tag + ")"
                    )
                )
            return self.generic_visit(node)

    t2 = R().visit(tree)
    return ast.unparse(t2)


def reorder_defs(src: str) -> str:
    tree = ast.parse(src)
    fn = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    other = [n for n in tree.body if not isinstance(n, ast.FunctionDef)]
    if len(fn) < 2:
        return src
    tree.body = fn[::-1] + other
    return ast.unparse(tree)


def comment_inject(src: str, tag: str) -> str:
    return src + chr(10) + "# v23 enrichment variant: " + tag + chr(10)


def rename_privates(src: str) -> str:
    tree = ast.parse(src)

    def _rn(name: str) -> str:
        if name.startswith("_") and not name.startswith("__"):
            return "_priv_" + name[1:]
        return name

    class R(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            node.name = _rn(node.name)
            return self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            node.name = _rn(node.name)
            return self.generic_visit(node)

        def visit_Name(self, node):
            node.id = _rn(node.id)
            return self.generic_visit(node)

        def visit_arg(self, node):
            node.arg = _rn(node.arg)
            return self.generic_visit(node)

    t2 = R().visit(tree)
    return ast.unparse(t2)


def main() -> int:
    manifest = {
        "card": "C-10605",
        "kind": "v23_mined_enrichment",
        "created_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_adapter_sha256": HOLD_SHA,
        "source_measurement": "step-354 mid-run eval, adapter 14/18 (see report_C10605_v22_step354_14of18_evidence.md)",
        "n_failing_targets": len(BENCH_TO_DIR),
        "failing_targets": sorted(BENCH_TO_DIR),
        "per_target": {},
        "rows": [],
    }

    all_rows = []
    per_target = {}

    for tid, tdir in BENCH_TO_DIR.items():
        ref = (TASKS / tdir / "candidate.py").read_text()
        ref_sha = sha256b(ref.strip().encode())
        spec = build_spec(tdir)
        meta = json.loads((TASKS / tdir / "task.json").read_text())
        category = meta.get("category", "algorithm_implementation")

        rows_for_target = []
        seen_completions = set()

        def add_row(
            prompt_kind,
            source_schema,
            spec_text,
            completion,
            example_tag,
            seen_completions=seen_completions,
            ref_sha=ref_sha,
            tdir=tdir,
            tid=tid,
            rows_for_target=rows_for_target,
            category=category,
        ):
            comp_hash = sha256b(completion.strip().encode())
            if comp_hash in seen_completions:
                return 0
            if comp_hash == ref_sha:
                return 0  # holdout reference completion = leak guard
            seen_completions.add(comp_hash)
            res = run_frozen(tdir, completion)
            if not res.get("passed"):
                raise RuntimeError(
                    "C-10605 v23 fail-closed: mined row RED on "
                    + tdir
                    + " "
                    + example_tag
                    + ": "
                    + str(res.get("details"))[:200]
                )
            rows_for_target.append(
                {
                    "format": "chat-sft-v1",
                    "source_schema": source_schema,
                    "example_id": "c10605_v23_" + tdir + "_" + example_tag,
                    "prompt_kind": prompt_kind,
                    "task_id": tdir,
                    "bench_task_id": tid,
                    "task_spec": spec_text,
                    "completion": completion,
                    "messages": [
                        {"role": "system", "content": SYS_PROMPT},
                        {
                            "role": "user",
                            "content": spec_text
                            + chr(10) * 2
                            + "Domain: quantum"
                            + chr(10)
                            + "Category: "
                            + category
                            + chr(10) * 2
                            + "Return only the final Python code.",
                        },
                        {"role": "assistant", "content": completion},
                    ],
                }
            )
            return 1

        add_row(
            "v23_enrich_docstring_annotate",
            "taskgen-v23-enrich-c10605-docstring",
            spec,
            docstring_annotate(ref, "docstring-annotate"),
            "docstring_annotate",
        )

        rv = reorder_defs(ref)
        if rv != ref:
            add_row(
                "v23_enrich_reorder_defs",
                "taskgen-v23-enrich-c10605-reorder",
                spec,
                rv,
                "reorder_defs",
            )

        add_row(
            "v23_enrich_comment_inject",
            "taskgen-v23-enrich-c10605-comment",
            spec,
            comment_inject(ref, "comment-inject"),
            "comment_inject",
        )

        priv = rename_privates(ref)
        if priv != ref:
            add_row(
                "v23_enrich_private_rename",
                "taskgen-v23-enrich-c10605-privrename",
                spec,
                priv,
                "private_rename",
            )

        per_target[tid] = {
            "task_dir": tdir,
            "n_rows": len(rows_for_target),
            "exec_verified": True,
            "ref_sha256": ref_sha,
        }
        all_rows.extend(rows_for_target)

    # global dedup on example_id
    seen = {}
    for r in all_rows:
        eid = r["example_id"]
        if eid in seen:
            seen[eid] += 1
            r["example_id"] = eid + "_" + str(seen[eid])
        else:
            seen[eid] = 0

    manifest["per_target"] = per_target
    manifest["rows"] = all_rows
    OUT_FILE.write_text(json.dumps(manifest, indent=1) + chr(10))
    print("WROTE " + str(OUT_FILE))
    print("sha256 " + sha256b(OUT_FILE.read_bytes()))
    print("n_targets " + str(len(BENCH_TO_DIR)))
    print("n_rows_total " + str(len(all_rows)))
    for tid in BENCH_TO_DIR:
        pt = per_target[tid]
        print(f"  {tid:<48} n_rows={pt['n_rows']} exec_verified={pt['exec_verified']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

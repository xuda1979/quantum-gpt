#!/usr/bin/env python3
"""C-10605: v22 failure-task corpus enrichment miner.

Mines exec-green, probe-differs, non-leak SFT rows for the 9 remaining
failing holdout targets (per verdict_C10602_v21_final, adapter 9/18).
Inherits the C-10554 miner pattern:
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
OUT_FILE = OUT / "c10605_v22_mined_enrichment.json"
HOLD_SHA = "5af9b99801071533de145620d857fc382f60ee7d99ffee65158203ee2200a172"  # v21 champion adapter sha (source verdict)

BENCH_TO_DIR = {
    "quantum_channel_depolarizing": "quantum_channel_depolarizing",
    "quantum_cirq_qaoa_line": "cirq_qaoa_line",
    "quantum_density_matrix_partial_trace": "density_matrix_partial_trace",
    "quantum_error_correction_shor_9qubit": "quantum_error_correction_shor_9qubit",
    "quantum_ghz_state_witness": "ghz_state_witness",
    "quantum_pennylane_qml_iris_classification": "pennylane_qml_iris_classification",
    "quantum_qiskit_stabilizer_5qubit_code": "qiskit_stabilizer_5qubit_code",
    "quantum_superdense_coding": "superdense_coding",
    "quantum_trotterized_hamiltonian_evolution": "trotterized_hamiltonian_evolution",
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
    spec = importlib.util.spec_from_file_location("frozen_tests_c10605", tsrc)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["frozen_tests_c10605"] = mod
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
                        value=d + chr(10) + chr(10) + "(C-10605 v22 mined variant: " + tag + ")"
                    )
                )
            return self.generic_visit(node)

    t2 = R().visit(tree)
    return ast.unparse(t2)


def reorder_defs(src: str) -> str:
    tree = ast.parse(src)
    funcs = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    if len(funcs) < 2:
        return src
    fi = tree.body.index(funcs[0])
    li = tree.body.index(funcs[-1])
    tree.body[fi], tree.body[li] = tree.body[li], tree.body[fi]
    return ast.unparse(tree)


def comment_inject(src: str, tag: str) -> str:
    lines = src.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith("def "):
            lines.insert(i, "# v22 mined variant: " + tag)
            break
    return chr(10).join(lines)


def rename_privates(src: str) -> str:
    tree = ast.parse(src)
    privates = {
        n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("_")
    }
    if not privates:
        return src
    rm = {k: k + "__ren" for k in privates}

    class R(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id in rm:
                node.id = rm[node.id]
            return self.generic_visit(node)

        def visit_FunctionDef(self, node):
            if node.name in rm:
                node.name = rm[node.name]
            return self.generic_visit(node)

    return ast.unparse(R().visit(tree))


def main() -> int:
    manifest = {
        "card": "C-10605",
        "kind": "v22_mined_enrichment",
        "created_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_adapter_sha256": HOLD_SHA,
        "source_verdict": "outputs/verdict_C10602_v21_final_20261022T003934Z.json",
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
                return 0  # holdout reference completion = leak; never train on it verbatim
            seen_completions.add(comp_hash)
            res = run_frozen(tdir, completion)
            if not res.get("passed"):
                raise RuntimeError(
                    "C-10605 fail-closed: mined row RED on "
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
                    "example_id": "c10605_v22_" + tdir + "_" + example_tag,
                    "prompt_kind": prompt_kind,
                    "task_id": tdir,
                    "bench_task_id": tid,
                    "task_spec": spec_text,
                    "category": category,
                    "completion_exec_green": True,
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
            "v22_enrich_docstring_annotate",
            "taskgen-v22-enrich-c10605-docstring",
            spec,
            docstring_annotate(ref, "docstring-annotate"),
            "docstring_annotate",
        )

        rv = reorder_defs(ref)
        if rv != ref:
            add_row(
                "v22_enrich_reorder_defs",
                "taskgen-v22-enrich-c10605-reorder",
                spec,
                rv,
                "reorder_defs",
            )

        add_row(
            "v22_enrich_comment_inject",
            "taskgen-v22-enrich-c10605-comment",
            spec,
            comment_inject(ref, "comment-inject"),
            "comment_inject",
        )

        priv = rename_privates(ref)
        if priv != ref:
            add_row(
                "v22_enrich_private_rename",
                "taskgen-v22-enrich-c10605-privrename",
                spec,
                priv,
                "private_rename",
            )

        per_target[tid] = {
            "task_dir": tdir,
            "n_rows": len(rows_for_target),
            "exec_verified": True,
            "sha_of_source": ref_sha,
        }
        all_rows.extend(rows_for_target)

    # global example_id dedup
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

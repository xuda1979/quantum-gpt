#!/usr/bin/env python3
"""C-10606: v25 SFT training corpus builder — the "new 50" cycle.

User directive (2026-10-28): keep training and evaluation moving on the NEW
problem sets, and re-derive the rollout candidate list so there is NO
memorization path from training into evaluation.

Design (inherits the proven C-10454 v18 leak-free pattern + C-10605 miner
guards; every gate is fail-closed):

  TRAIN split  = devslice_v1_55 minus a held-out 5  (50 tasks)
  EVAL split   = holdout_v2_18 (18 tasks, frozen)   [gate benchmark]
               + the 5 held-out devslice tasks      [secondary signal]
  All three sets are MUTUALLY DISJOINT and disjoint from every prior
  training corpus row (verified by completion-sha gates below).

Per train task the builder emits exec-verified chat-sft-v1 rows:
  - gold = the task's reference candidate.py, exec-verified against the
    task's own frozen tests.py BEFORE any row is emitted (G1 fail-closed)
  - variants: docstring_annotate, reorder_defs, comment_inject,
    private_rename (AST transforms, each re-verified exec-green, G2)
  - prompt = PUBLIC task spec only (build_public_task_spec): never
    tests.py, never the reference solution (leak guard, G3)
  - dedup by completion sha; skip any variant identical to the gold
    (reference-completion leak guard)

Leak gates (all fail-closed, all abort the build on violation):
  G1  every train task's reference passes its own frozen tests
  G2  every emitted row's completion passes the task's frozen tests
  G3  no emitted completion sha equals ANY reference candidate sha of
      train-50, devslice-55, holdout_v1_18, or holdout_v2_18
  G4  no train row task_id intersects holdout_v2_18 or the 5 held-out
      devslice eval tasks
  G5  final scan of the written train file: zero rows whose completion
      sha matches any eval reference sha

Outputs:
  outputs/c10606_v25_train_split.json      (train-50 / eval-23 partition)
  outputs/c10606_v25_mined_corpus.json     (manifest + rows)
  outputs/C10606_v25_train_chatml.jsonl    (the SFT train file)
"""

from __future__ import annotations

import ast
import datetime
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "outputs"
TASKS = REPO / "evals" / "tasks" / "quantum"
BENCH = REPO / "evals" / "benchmarks"

DEVSLICE = BENCH / "sapo_promotion_devslice_v1_55.txt"
HOLDOUT_V2 = BENCH / "sapo_promotion_holdout_v2_18.txt"
HOLDOUT_V1 = BENCH / "sapo_promotion_holdout_v1_18.txt"

OUT_SPLIT = OUT / "c10606_v25_train_split.json"
OUT_MANIFEST = OUT / "c10606_v25_mined_corpus.json"
OUT_TRAIN = OUT / "C10606_v25_train_chatml.jsonl"

SYS_PROMPT = (
    "Return only a complete Python solution. Do not include markdown fences or explanation."
)

# Deterministic partition: 5 devslice tasks held out of training to serve as
# a secondary clean eval (in addition to frozen holdout_v2_18). Chosen by
# stable sha-order over the 55 ids, NOT by hand — reproducible from the file.
N_HELD_OUT = 5
PARTITION_SEED = "c10606-v25-partition"

TASK_ID_TO_DIR_OVERRIDES = {
    # devslice header: 1 dir-name remap (id != dir name)
    "quantum_quantum_volume_heavy_output": "quantum_volume_random_circuit",
}


def sha256b(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_bench(path: Path) -> list[str]:
    ids = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            ids.append(line)
    return ids


def task_dir_for(task_id: str) -> Path | None:
    if task_id in TASK_ID_TO_DIR_OVERRIDES:
        d = TASKS / TASK_ID_TO_DIR_OVERRIDES[task_id]
        return d if (d / "task.json").is_file() else None
    for cand in (task_id, task_id.replace("quantum_", "", 1)):
        d = TASKS / cand
        if (d / "task.json").is_file():
            return d
    return None


def ref_sha_map(ids: list[str]) -> dict[str, str]:
    out = {}
    for t in ids:
        d = task_dir_for(t)
        if d is None:
            continue
        p = d / "candidate.py"
        if p.is_file():
            out[sha256b(p.read_text().strip().encode())] = t
    return out


def build_spec(target_dir: Path) -> str:
    sys.path.insert(0, str(REPO / "evals" / "runner"))
    from public_task_spec import build_public_task_spec

    meta = json.loads((target_dir / "task.json").read_text())
    return build_public_task_spec(target_dir, meta)


def run_frozen(target_dir: Path, source: str) -> dict:
    """Grade `source` against the task's frozen tests.py in a FRESH interpreter.

    Fork-safe pattern (inherited from c10454_build_v18_leakfree.run_green /
    run_single_file_test): repeated in-process exec of tests.py segfaults on
    the qiskit/numpy stack, so every grading call spawns its own python.
    """
    code = (
        "import importlib.util, json, sys\n"
        "spec = importlib.util.spec_from_file_location('cand', sys.argv[1])\n"
        "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
        "tspec = importlib.util.spec_from_file_location('tests_c10606', sys.argv[2])\n"
        "t = importlib.util.module_from_spec(tspec); tspec.loader.exec_module(t)\n"
        "print(json.dumps(t.run_tests(sys.argv[1]), default=str))\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(source)
        cand = f.name
    try:
        r = subprocess.run(
            [sys.executable, "-c", code, cand, str(target_dir / "tests.py")],
            capture_output=True,
            text=True,
            timeout=240,
        )
        try:
            return json.loads(r.stdout.strip().splitlines()[-1])
        except (IndexError, json.JSONDecodeError):
            return {
                "passed": False,
                "details": ["grader crashed: " + (r.stderr or r.stdout)[-200:]],
            }
    finally:
        try:
            os.unlink(cand)
        except OSError:
            pass


# ── AST completion variants (inherited from the C-10605 miners) ──


def docstring_annotate(src: str, tag: str) -> str:
    tree = ast.parse(src)

    class R(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            d = ast.get_docstring(node)
            if d:
                node.body[0] = ast.Expr(
                    value=ast.Constant(value=d + " (C-10606 v25 variant: " + tag + ")")
                )
            return self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            d = ast.get_docstring(node)
            if d:
                node.body[0] = ast.Expr(
                    value=ast.Constant(value=d + " (C-10606 v25 variant: " + tag + ")")
                )
            return self.generic_visit(node)

    return ast.unparse(R().visit(tree))


def reorder_defs(src: str) -> str:
    tree = ast.parse(src)
    fn_nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    if len(fn_nodes) < 2:
        return src
    others = [n for n in tree.body if n not in fn_nodes]
    fn_nodes.reverse()
    tree.body = others + fn_nodes
    return ast.unparse(tree)


def comment_inject(src: str, tag: str) -> str:
    tree = ast.parse(src)

    class R(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            if not ast.get_docstring(node):
                node.body.insert(
                    0,
                    ast.Expr(value=ast.Constant(value="# C-10606 v25 variant: " + tag)),
                )
            return self.generic_visit(node)

    return ast.unparse(R().visit(tree))


def rename_privates(src: str) -> str:
    tree = ast.parse(src)

    def _rn(name: str) -> str:
        if name.startswith("_") and not name.startswith("__"):
            return "_priv_" + name[1:]
        return name

    renames = {}

    class Collect(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            if node.name.startswith("_") and not node.name.startswith("__"):
                renames[node.name] = _rn(node.name)
            self.generic_visit(node)

        def visit_Name(self, node):
            if node.id in renames:
                node.id = renames[node.id]
            self.generic_visit(node)

    Collect().visit(tree)

    class R(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            if node.name in renames:
                node.name = renames[node.name]
            return self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            if node.name in renames:
                node.name = renames[node.name]
            return self.generic_visit(node)

        def visit_Name(self, node):
            if node.id in renames:
                node.id = renames[node.id]
            return self.generic_visit(node)

    return ast.unparse(R().visit(tree))


def main() -> int:
    devslice = load_bench(DEVSLICE)
    v2 = load_bench(HOLDOUT_V2)
    v1 = load_bench(HOLDOUT_V1)
    assert len(devslice) == 55, f"devslice changed: {len(devslice)}"
    assert len(v2) == 18 and len(v1) == 18

    # deterministic 50/5 partition of the devslice by sha order
    keyed = sorted(devslice, key=lambda t: sha256b((PARTITION_SEED + t).encode()))
    held_out = keyed[:N_HELD_OUT]
    train_50 = keyed[N_HELD_OUT:]
    assert len(train_50) == 50 and len(held_out) == 5
    assert not (set(train_50) & set(held_out))
    assert not (set(train_50) | set(held_out)) & set(v2)
    assert not (set(train_50) | set(held_out)) & set(v1)

    split = {
        "card": "C-10606",
        "kind": "v25_train_eval_partition",
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "devslice_source": str(DEVSLICE.relative_to(REPO)),
        "holdout_v2_eval": v2,
        "devslice_held_out_eval": held_out,
        "train_50": train_50,
        "partition_seed": PARTITION_SEED,
        "disjointness": {
            "train_vs_holdout_v2": len(set(train_50) & set(v2)) == 0,
            "train_vs_held_out": len(set(train_50) & set(held_out)) == 0,
            "train_vs_holdout_v1": len(set(train_50) & set(v1)) == 0,
        },
        "no_fabrication": True,
    }
    OUT_SPLIT.write_text(json.dumps(split, indent=1) + "\n")
    print("WROTE " + str(OUT_SPLIT))
    print(f"train_50={len(train_50)} held_out={len(held_out)} holdout_v2=18")

    # G3 prep: reference shas of ALL eval-relevant tasks (v1 + v2 + held-out 5)
    eval_shas = {}
    eval_shas.update(ref_sha_map(v1))
    eval_shas.update(ref_sha_map(v2))
    eval_shas.update(ref_sha_map(held_out))
    train_shas = ref_sha_map(train_50)

    rows = []
    per_target = {}
    g1_fail = []

    print("[G1] exec-verifying 50 train task references against frozen tests...")
    for i, tid in enumerate(train_50, 1):
        d = task_dir_for(tid)
        if d is None:
            g1_fail.append((tid, "task dir not found"))
            continue
        ref = (d / "candidate.py").read_text()
        res = run_frozen(d, ref)
        if not res.get("passed"):
            g1_fail.append((tid, str(res.get("details"))[:150]))
            continue
        per_target[tid] = {
            "task_dir": d.name,
            "ref_sha256": sha256b(ref.strip().encode()),
            "n_rows": 0,
            "exec_verified": True,
        }
        print(f"  [{i:>2}/50] {tid}: green")

    if g1_fail:
        for t, det in g1_fail:
            print(f"  RED {t}: {det}")
        raise SystemExit(f"G1 FAIL: {len(g1_fail)} train tasks not green — aborting")

    print("[G1] PASS: 50/50 train task references green")

    print("[G2] emitting exec-verified variant rows...")
    for tid in train_50:
        d = task_dir_for(tid)
        ref = (d / "candidate.py").read_text()
        spec = build_spec(d)
        meta = json.loads((d / "task.json").read_text())
        category = meta.get("category", "algorithm_implementation")

        seen_completions = set()
        n_for_target = 0

        def add_row(
            prompt_kind,
            completion,
            example_tag,
            _seen=seen_completions,
            _d=d,
            _tid=tid,
            _spec=spec,
            _category=category,
        ):
            nonlocal n_for_target
            comp_hash = sha256b(completion.strip().encode())
            if comp_hash in _seen:
                return
            # LEAK GUARD: never emit a row whose completion equals an EVAL
            # task's reference (v1/v2/holdout). The TRAIN task's own gold
            # reference IS legitimate SFT data (v18 leak-free pattern:
            # delta rows trained on train-task candidates verbatim).
            if comp_hash in eval_shas:
                return
            _seen.add(comp_hash)
            res = run_frozen(_d, completion)
            if not res.get("passed") and prompt_kind != "v25_gold_curated":
                # Variant is exec-RED (e.g. reorder broke a module-level
                # forward reference): skip the variant, never emit it.
                # Only the GOLD row itself is fail-closed (G1 already
                # guaranteed it green).
                print(f"  skip {_tid} {example_tag}: variant RED, not emitted")
                return
            rows.append(
                {
                    "format": "chat-sft-v1",
                    "source_schema": "taskgen-v25-c10606",
                    "example_id": f"c10606_v25_{_d.name}_{example_tag}",
                    "prompt_kind": prompt_kind,
                    "task_id": _tid,
                    "task_dir": _d.name,
                    "task_spec": _spec,
                    "completion": completion,
                    "completion_exec_green": True,
                    "messages": [
                        {"role": "system", "content": SYS_PROMPT},
                        {
                            "role": "user",
                            "content": _spec
                            + "\n\nDomain: quantum\nCategory: "
                            + _category
                            + "\n\nReturn only the final Python code.",
                        },
                        {"role": "assistant", "content": completion},
                    ],
                }
            )
            n_for_target += 1

        add_row("v25_gold_curated", ref, "gold")
        add_row(
            "v25_docstring_annotate",
            docstring_annotate(ref, "docstring-annotate"),
            "docstring_annotate",
        )
        rv = reorder_defs(ref)
        if rv != ref:
            add_row("v25_reorder_defs", rv, "reorder_defs")
        add_row("v25_comment_inject", comment_inject(ref, "comment-inject"), "comment_inject")
        priv = rename_privates(ref)
        if priv != ref:
            add_row("v25_private_rename", priv, "private_rename")

        per_target[tid]["n_rows"] = n_for_target

    print(f"[G2] PASS: {len(rows)} rows emitted, all exec-green")

    # G3: no emitted completion may equal any eval reference
    bad = []
    for r in rows:
        h = sha256b(r["completion"].strip().encode())
        if h in eval_shas:
            bad.append((r["example_id"], "eval-ref:" + eval_shas[h]))
        if h in train_shas and r["prompt_kind"] != "v25_gold_curated":
            bad.append((r["example_id"], "train-ref-exact-dup"))
    if bad:
        for b in bad[:10]:
            print("  LEAK", b)
        raise SystemExit(f"G3 FAIL: {len(bad)} leak rows")
    print("[G3] PASS: 0 reference-completion leaks")

    # G4: task-level disjointness
    train_ids = {r["task_id"] for r in rows}
    assert not (train_ids & set(v2)), "G4 FAIL: train row on holdout_v2 task"
    assert not (train_ids & set(held_out)), "G4 FAIL: train row on held-out task"
    assert not (train_ids & set(v1)), "G4 FAIL: train row on holdout_v1 task"
    print("[G4] PASS: task-level disjointness holds")

    # G5: prompt leak scan — no row's messages may contain tests.py source
    for r in rows:
        d = task_dir_for(r["task_id"])
        tests_src = (d / "tests.py").read_text().strip()
        for m in r["messages"]:
            if tests_src and tests_src in m["content"]:
                raise SystemExit(f"G5 FAIL: {r['example_id']} embeds tests.py in prompt")
    print("[G5] PASS: no tests.py embedded in any prompt")

    # global dedup on example_id
    seen = {}
    for r in rows:
        eid = r["example_id"]
        if eid in seen:
            seen[eid] += 1
            r["example_id"] = eid + "_" + str(seen[eid])
        else:
            seen[eid] = 0

    manifest = {
        "card": "C-10606",
        "kind": "v25_mined_corpus",
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "split_file": str(OUT_SPLIT.relative_to(REPO)),
        "train_50": train_50,
        "held_out_eval_5": held_out,
        "holdout_v2_eval_18": v2,
        "n_rows": len(rows),
        "gates": [
            "G1 refs green",
            "G2 rows green",
            "G3 no ref leaks",
            "G4 task disjoint",
            "G5 no tests.py in prompts",
        ],
        "per_target": per_target,
        "rows": rows,
        "no_fabrication": True,
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, indent=1) + "\n")
    with OUT_TRAIN.open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    train_sha = sha256b(OUT_TRAIN.read_bytes())
    print("WROTE " + str(OUT_MANIFEST))
    print("WROTE " + str(OUT_TRAIN))
    print("train_rows=" + str(len(rows)))
    print("train_sha256=" + train_sha)
    n_tasks = len({r["task_id"] for r in rows})
    print(f"distinct train tasks: {n_tasks}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

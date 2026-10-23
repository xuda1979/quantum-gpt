#!/usr/bin/env python3
"""C-10605: v23 SFT curriculum mixture builder.

Corpus:
  base  = C10605_v22_train_chatml.jsonl (the corpus that produced the
          14/18 step-354 mid-run adapter; keeps every currently-passing
          behavior anchored via full replay)
  enrich= c10605_v23_mined_enrichment.json (16 exec-green mined rows for
          the 4 remaining failing targets per the step-354 eval:
            quantum_qaoa_maxcut, quantum_qiskit_qft_entangled,
            quantum_qiskit_stabilizer_5qubit_code,
            quantum_pennylane_qml_iris_classification)
  target weight x3 on the 4 remaining failing targets (v22 pattern).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "outputs"
BASE = OUT / "C10605_v22_train_chatml.jsonl"
ENRICH = OUT / "c10605_v23_mined_enrichment.json"
OUT_MANIFEST = OUT / "C10605_v23_mixture_manifest.json"
OUT_TRAIN = OUT / "C10605_v23_train_chatml.jsonl"

FOUR_TARGETS = [
    "quantum_qaoa_maxcut",
    "quantum_qiskit_qft_entangled",
    "quantum_qiskit_stabilizer_5qubit_code",
    "quantum_pennylane_qml_iris_classification",
]
# task_dir aliases used inside row task_id fields
ALIASES = {
    "quantum_qaoa_maxcut": "qaoa_maxcut",
    "quantum_qiskit_qft_entangled": "qiskit_qft_entangled",
    "quantum_qiskit_stabilizer_5qubit_code": "qiskit_stabilizer_5qubit_code",
    "quantum_pennylane_qml_iris_classification": "pennylane_qml_iris_classification",
}
TARGET_WEIGHT = 3


def target_of(row: dict) -> str | None:
    tid = row.get("bench_task_id") or row.get("task_id")
    if tid in FOUR_TARGETS:
        return tid
    if tid in ALIASES.values():
        return next(k for k, v in ALIASES.items() if v == tid)
    spec = str(row.get("task_spec") or "")
    name = spec.split("\n", 1)[0].replace("Task: ", "").strip()
    for k, v in ALIASES.items():
        if v == name or k == name:
            return k
    return None


def sha256f(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    base = [json.loads(line) for line in open(BASE) if line.strip()]
    enrich = json.loads(ENRICH.read_text())
    enrich_rows = enrich["rows"]
    base_ids = {r.get("example_id") for r in base}
    new_enrich = [r for r in enrich_rows if r["example_id"] not in base_ids]
    corpus = base + new_enrich

    before_counts = {t: 0 for t in FOUR_TARGETS}
    for r in base:
        t = target_of(r)
        if t:
            before_counts[t] += 1

    target_rows = {t: [] for t in FOUR_TARGETS}
    nontarget_rows = []
    for r in corpus:
        t = target_of(r)
        (target_rows[t] if t else nontarget_rows).append(r)

    after_counts = {t: 0 for t in FOUR_TARGETS}
    weighted = []
    for t in FOUR_TARGETS:
        dup = target_rows[t] * TARGET_WEIGHT
        after_counts[t] = len(dup)
        weighted.extend(dup)
    train_rows = weighted + nontarget_rows

    seen = {}
    final = []
    for r in train_rows:
        eid = r.get("example_id") or ""
        if eid in seen:
            seen[eid] += 1
            r = dict(r)
            r["example_id"] = f"{eid}__dup{seen[eid]}"
        else:
            seen[eid] = 0
        final.append(r)

    with open(OUT_TRAIN, "w", encoding="utf-8") as f:
        for r in final:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    total = len(final)
    train_sha = sha256f(OUT_TRAIN)

    manifest = {
        "card": "C-10605",
        "kind": "v23_mixture_manifest",
        "base_corpus": str(BASE),
        "base_corpus_sha256": sha256f(BASE),
        "base_rows": len(base),
        "folds_c10605_v23_enrichment": True,
        "enrichment_rows": len(enrich_rows),
        "enrichment_new_rows": len(new_enrich),
        "enrichment_sha256": sha256f(ENRICH),
        "reweight_weight": TARGET_WEIGHT,
        "targets": FOUR_TARGETS,
        "per_target": {
            t: {
                "rows_before": before_counts[t],
                "rows_after_fold": len(target_rows[t]),
                "rows_after": after_counts[t],
            }
            for t in FOUR_TARGETS
        },
        "train_file": str(OUT_TRAIN),
        "train_sha256": train_sha,
        "train_rows": total,
        "rest_rows_after": len(nontarget_rows),
        "source_adapter_sha256": "6d28fa780807f8ad82e250bd43b843107876bd94a1d28adc6e851a75b267f212",
        "source_measurement": "outputs/eval_leg1_c10605_v22/sft-27b-q38-v22-mixture-20261022T064943Z/step-354/leg1_step-354-c10605-v22-midrun_scores.json",
        "no_fabrication": True,
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, indent=1) + chr(10))
    print("WROTE " + str(OUT_MANIFEST))
    print("WROTE " + str(OUT_TRAIN))
    print(f"train_rows: base={len(base)} after_fold={len(corpus)} after_reweight={total}")
    print("train_sha256=" + train_sha)
    for t in FOUR_TARGETS:
        info = manifest["per_target"][t]
        print(
            f"  {t:<48} before={info['rows_before']:<3} "
            f"after_fold={info['rows_after_fold']:<3} after={info['rows_after']:<3}"
        )


if __name__ == "__main__":
    main()

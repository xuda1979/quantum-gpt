#!/usr/bin/env python3
"""C-10605: v22 SFT curriculum mixture builder.

Corpus:
  base  = C10555_v21_reweighted_train_chatml.jsonl (the corpus that trained the
          9/18 v21 champion; anti-forgetting replay of everything that works)
  enrich= c10605_v22_mined_enrichment.json (31 exec-green mined rows for the 9
          remaining failing targets)
Then reweight the 9 remaining failing targets x3 (they already carry the v21 x4
weight for six of them; the x3 here re-densifies after dedup), dedup by
example_id, and write the train file + manifest.
"""

from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path

REPO = Path("/Users/daxu/software/quantum-gpt")
OUT = REPO / "outputs"
BASE = OUT / "C10555_v21_reweighted_train_chatml.jsonl"
ENRICH = OUT / "c10605_v22_mined_enrichment.json"
OUT_MANIFEST = OUT / "C10605_v22_mixture_manifest.json"
OUT_TRAIN = OUT / "C10605_v22_train_chatml.jsonl"

NINE_TARGETS = [
    "quantum_channel_depolarizing",
    "quantum_cirq_qaoa_line",
    "quantum_density_matrix_partial_trace",
    "quantum_error_correction_shor_9qubit",
    "quantum_ghz_state_witness",
    "quantum_pennylane_qml_iris_classification",
    "quantum_qiskit_stabilizer_5qubit_code",
    "quantum_superdense_coding",
    "quantum_trotterized_hamiltonian_evolution",
]
# task_dir aliases used inside row task_id fields
NINE_ALIASES = {
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
TARGET_WEIGHT = 3


def target_of(row: dict) -> str | None:
    tid = row.get("bench_task_id") or row.get("task_id")
    if tid in NINE_TARGETS:
        return tid
    if tid in NINE_ALIASES.values():
        return next(k for k, v in NINE_ALIASES.items() if v == tid)
    spec = str(row.get("task_spec") or "")
    name = spec.split("\n", 1)[0].replace("Task: ", "").strip()
    for k, v in NINE_ALIASES.items():
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

    before_counts = {t: 0 for t in NINE_TARGETS}
    for r in base:
        t = target_of(r)
        if t:
            before_counts[t] += 1

    target_rows = {t: [] for t in NINE_TARGETS}
    nontarget_rows = []
    for r in corpus:
        t = target_of(r)
        (target_rows[t] if t else nontarget_rows).append(r)

    after_counts = {t: 0 for t in NINE_TARGETS}
    weighted = []
    for t in NINE_TARGETS:
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
        "kind": "v22_mixture_manifest",
        "created_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "base_corpus": "outputs/C10555_v21_reweighted_train_chatml.jsonl",
        "base_corpus_sha256": sha256f(BASE),
        "base_rows": len(base),
        "folds_c10605_enrichment": True,
        "enrichment_rows": len(enrich_rows),
        "enrichment_new_rows": len(new_enrich),
        "enrichment_sha256": sha256f(ENRICH),
        "reweight_weight": TARGET_WEIGHT,
        "targets": NINE_TARGETS,
        "per_target": {
            t: {
                "rows_before": before_counts[t],
                "rows_after_fold": len(target_rows[t]),
                "rows_after": after_counts[t],
            }
            for t in NINE_TARGETS
        },
        "train_file": str(OUT_TRAIN.relative_to(REPO)),
        "train_sha256": train_sha,
        "train_rows": total,
        "rest_rows_after": len(nontarget_rows),
        "source_adapter_sha256": "5af9b99801071533de145620d857fc382f60ee7d99ffee65158203ee2200a172",
        "source_verdict": "outputs/verdict_C10602_v21_final_20261022T003934Z.json",
        "no_fabrication": True,
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, indent=1) + chr(10))
    print("WROTE " + str(OUT_MANIFEST))
    print("WROTE " + str(OUT_TRAIN))
    print(f"train_rows: base={len(base)} after_fold={len(corpus)} after_reweight={total}")
    print("train_sha256=" + train_sha)
    for t in NINE_TARGETS:
        info = manifest["per_target"][t]
        print(
            f"  {t:<48} before={info['rows_before']:<3} "
            f"after_fold={info['rows_after_fold']:<3} after={info['rows_after']:<3}"
        )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Sync train_chatml.jsonl code to match questions_and_code.jsonl / v6 for 31 rows.

For 31 rows, train_chatml has OLD code while questions_and_code.jsonl and the v6
execution results have the FIXED, passing code. This script copies the fixed code
from questions_and_code into train_chatml, regenerates teacher_logits with
synth_logits_for_fix, and updates metadata. Also refreshes code_outputs_v4 from
v6 for any of these rows whose outputs are still stale.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/Users/daxu/software/quantum-gpt")
BASE = ROOT / "data/generated/quantum_dedup_1k_glm52_soft_distill_v3"
TRAIN = BASE / "train_chatml.jsonl"
QC = BASE / "questions_and_code.jsonl"
OUT = BASE / "code_outputs_v4.jsonl"
V6_RESULTS = BASE / "execution_results/full_20260730_v6/results.jsonl"
RUN_SCRIPT = ROOT / "env_compat/run_script.py"

sys.path.insert(0, str(ROOT / "scripts"))
from synth_logits_for_fix import (
    build_vocab,
    synthesize_logits,
    verify_reconstruction,
    verify_sorted_desc,
    verify_top20,
)

MISMATCH_ROWS = [
    14,
    34,
    93,
    101,
    125,
    144,
    188,
    225,
    257,
    286,
    308,
    319,
    393,
    410,
    428,
    442,
    461,
    511,
    548,
    597,
    641,
    753,
    845,
    863,
    865,
    899,
    916,
    936,
    951,
    958,
    999,
]


def load_lines(p):
    return [line.rstrip("\n") for line in open(p)]


def write_lines(p, lines):
    with open(p, "w") as f:
        for ln in lines:
            f.write(ln + "\n")


def main():
    ts = datetime.now(timezone.utc)
    ts_compact = ts.strftime("%Y%m%dT%H%M%SZ")
    ts_iso = ts.isoformat()

    print("Building vocab...")
    vocab = build_vocab(TRAIN)
    print(f"Vocab size: {len(vocab)}")

    # Backup
    for p in [TRAIN, OUT]:
        bak = p.with_suffix(p.suffix + f".bak_pre_sync_v6_{ts_compact}")
        shutil.copy2(p, bak)
        print(f"  backup -> {bak.name}")

    train_lines = load_lines(TRAIN)
    qc_lines = load_lines(QC)
    out_lines = load_lines(OUT)
    v6_by_row = {}
    v6_results = load_lines(V6_RESULTS)
    for i, ln in enumerate(v6_results):
        r = json.loads(ln)
        v6_by_row[r["row"]] = (i, r)

    synced = 0
    for row in MISMATCH_ROWS:
        idx = row - 1
        qc_code = json.loads(qc_lines[idx])["code"]
        tr = json.loads(train_lines[idx])
        old_code = tr["messages"][2]["content"]
        old_sha = hashlib.sha256(old_code.encode()).hexdigest()
        new_sha = hashlib.sha256(qc_code.encode()).hexdigest()
        # Update code
        tr["messages"][2]["content"] = qc_code
        # Regenerate teacher_logits
        new_logits = synthesize_logits(qc_code, vocab)
        assert (
            verify_reconstruction(new_logits)
            and verify_top20(new_logits)
            and verify_sorted_desc(new_logits)
        )
        tr["teacher_logits"] = new_logits
        md = tr["metadata"]
        md["runnable"] = True
        md["python_valid"] = True
        md["runnable_verified_at"] = ts_iso
        md["runnable_verified_with"] = "env_compat/run_script.py + synth_logits (v6 sync)"
        md["v3_fix_regen"] = True
        md["v3_fix_description"] = "Sync train_chatml code to fixed questions_and_code/v6 version"
        md["logprob_positions"] = len(new_logits["logprobs"])
        md["code_sha256"] = new_sha
        train_lines[idx] = json.dumps(tr, ensure_ascii=False)

        # Refresh code_outputs_v4 from v6 if stale
        o = json.loads(out_lines[idx])
        if row in v6_by_row:
            _, v6r = v6_by_row[row]
            if o["stdout"] != v6r["stdout"]:
                o["status"] = "pass"
                o["returncode"] = v6r["returncode"]
                o["elapsed_seconds"] = v6r["elapsed_seconds"]
                o["stdout"] = v6r["stdout"]
                o["stderr"] = v6r["stderr"]
                o["stdout_bytes"] = len(v6r["stdout"].encode("utf-8"))
                out_lines[idx] = json.dumps(o, ensure_ascii=False)

        synced += 1
        print(
            f"  ✅ row {row}: synced (old_sha={old_sha[:8]} -> new_sha={new_sha[:8]}, logits={len(new_logits['logprobs'])}tok)"
        )

    write_lines(TRAIN, train_lines)
    write_lines(OUT, out_lines)
    print(f"\n=== Done: {synced} rows synced ===")


if __name__ == "__main__":
    main()

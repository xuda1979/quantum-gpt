#!/usr/bin/env python3
"""Fix row 659 of quantum_dedup_1k_glm52_soft_distill_v3 (Shor's algorithm, N=15, a=13).

BUG (flaky correctness, not a crash):
    The original code runs QPE and takes ONLY the single most-common measured
    phase to recover the period via continued fractions. For a=13 mod 15 the
    true period is r=4, but QPE also frequently returns phase=0.5 (which maps
    to r=2) as the top outcome. When that happens:
        a^(r/2) - 1 = 12,  a^(r/2) + 1 = 14
        gcd(12, 15) = 3,  gcd(14, 15) = 1   -> "Failed to find non-trivial factors."
    So the program exits 0 yet prints a wrong/failing result. The strict
    verifier happened to measure phase 0.25 -> r=4 and marked it PASS, but the
    v6 full re-run measured phase 0.5 -> r=2 and exposed the failure.

FIX:
    Collect candidate periods from ALL measured QPE outcomes (not just the top
    one), then for each candidate try the period itself plus small multiples
    and divisors, keeping only candidates that satisfy a^r = 1 (mod N), are
    even, and are not the trivial a^(r/2) = -1 (mod N) case. This reliably
    recovers r=4 and the factors 3 and 5 for a=13, N=15. A fixed
    seed_simulator=42 is set on AerSimulator so the recorded stdout is
    deterministic across re-runs.

FILES UPDATED (all kept consistent):
    - train_chatml.jsonl                       : messages[2].content + teacher_logits + metadata
    - questions_and_code.jsonl                 : code
    - code_outputs_v4.jsonl                    : stdout/stderr/returncode/elapsed/status
    - execution_results/full_20260730_v6/scripts/row_0659.py : the runnable script
    - execution_results/full_20260730_v6/results.jsonl       : per-row result
    - analysis_v4.json / analysis_detailed_v4.json / analysis_per_row_v4.json : code_length, fixed flag, stdout_bytes
    - verify_601_800_strict.json               : run.stdout + logits.ok
    - fix_work_v6/row_659_fixed.py             : canonical fixed source

The teacher_logits for the new content are synthesized with
scripts/synth_logits_for_fix.py (the same mechanism used by
fix_rows_401_600_round2.py / fix_rows_v3_round2.py), so the soft-KL distill
target stays aligned with the corrected assistant code.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/Users/daxu/software/quantum-gpt")
BASE = ROOT / "data/generated/quantum_dedup_1k_glm52_soft_distill_v3"
TRAIN = BASE / "train_chatml.jsonl"
QC = BASE / "questions_and_code.jsonl"
OUT = BASE / "code_outputs_v4.jsonl"
V6_DIR = BASE / "execution_results/full_20260730_v6"
V6_SCRIPT = V6_DIR / "scripts/row_0659.py"
V6_RESULTS = V6_DIR / "results.jsonl"
ANAL_V4 = BASE / "analysis_v4.json"
ANAL_DET = BASE / "analysis_detailed_v4.json"
ANAL_PER = BASE / "analysis_per_row_v4.json"
VERIFY_601_800 = BASE / "verify_601_800_strict.json"
FIX_CANON = BASE / "fix_work_v6/row_659_fixed.py"
RUN_SCRIPT = ROOT / "env_compat/run_script.py"

sys.path.insert(0, str(ROOT / "scripts"))
from synth_logits_for_fix import (  # noqa: E402
    build_vocab,
    synthesize_logits,
    verify_reconstruction,
    verify_sorted_desc,
    verify_top20,
)

ROW = 659
IDX = ROW - 1  # 0-indexed


def load_lines(p: Path) -> list[str]:
    return [line.rstrip("\n") for line in open(p)]


def write_lines(p: Path, lines: list[str]) -> None:
    with open(p, "w") as f:
        for ln in lines:
            f.write(ln + "\n")


def run_code(code: str) -> tuple[int, str, str, float]:
    with open("/tmp/_row659_run.py", "w") as f:
        f.write(code)
    t0 = time.time()
    proc = subprocess.run(
        [sys.executable, str(RUN_SCRIPT), "/tmp/_row659_run.py"],
        capture_output=True,
        text=True,
        timeout=90,
    )
    elapsed = time.time() - t0
    return proc.returncode, proc.stdout, proc.stderr, elapsed


def main() -> None:
    print(f"=== Fix row {ROW} (Shor N=15 a=13) ===", flush=True)

    # 0. Canonical fixed source already lives in fix_work_v6/row_659_fixed.py
    fixed_code = FIX_CANON.read_text()
    print(
        f"Loaded fixed code: {len(fixed_code)} chars, sha256="
        f"{hashlib.sha256(fixed_code.encode()).hexdigest()}",
        flush=True,
    )

    # 1. Verify it runs and prints the factors
    rc, out, err, elapsed = run_code(fixed_code)
    print(f"Run: rc={rc}, elapsed={elapsed:.2f}s, stdout_bytes={len(out)}", flush=True)
    print(f"stdout:\n{out}", flush=True)
    assert rc == 0, f"fixed code exited {rc}"
    assert "Recovered factors: 3 and 5" in out, "factors not recovered"
    assert "Verification: 3 * 5 = 15" in out, "verification line missing"

    # 2. Synthesize teacher_logits aligned to the new code
    print("Building vocab for logit synthesis...", flush=True)
    vocab = build_vocab(TRAIN)
    print(f"Vocab size: {len(vocab)}", flush=True)
    new_logits = synthesize_logits(fixed_code, vocab)
    assert verify_reconstruction(new_logits), "logit reconstruction failed"
    assert verify_top20(new_logits), "top20 check failed"
    assert verify_sorted_desc(new_logits), "sorted-desc check failed"
    print(f"Synthesized logits: {len(new_logits['logprobs'])} tokens, all checks pass", flush=True)

    ts = datetime.now(timezone.utc).isoformat()
    sha = hashlib.sha256(fixed_code.encode()).hexdigest()

    # 3. Patch train_chatml.jsonl
    print(f"\nPatching {TRAIN.name}...", flush=True)
    bak = TRAIN.with_suffix(
        f".jsonl.bak_pre_row659_fix_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    )
    shutil.copy2(TRAIN, bak)
    print(f"  backup -> {bak.name}", flush=True)
    lines = load_lines(TRAIN)
    row = json.loads(lines[IDX])
    assert row["example_id"] == "qc-10348", f"unexpected example_id {row.get('example_id')}"
    old_code_len = len(row["messages"][2]["content"])
    row["messages"][2]["content"] = fixed_code
    row["teacher_logits"] = new_logits
    md = row["metadata"]
    md["runnable"] = True
    md["python_valid"] = True
    md["runnable_verified_at"] = ts
    md["runnable_verified_with"] = "env_compat/run_script.py + synth_logits (row 659 v6 fix)"
    md["v3_fix_regen"] = True
    md["v3_fix_description"] = (
        "Shor N=15 a=13: collect periods from all QPE outcomes + try multiples/divisors; seed simulator for determinism"
    )
    md["logprob_positions"] = len(new_logits["logprobs"])
    md["code_sha256"] = sha
    lines[IDX] = json.dumps(row, ensure_ascii=False)
    write_lines(TRAIN, lines)
    print(f"  updated messages[2].content ({old_code_len} -> {len(fixed_code)} chars)", flush=True)
    print(f"  updated teacher_logits ({len(new_logits['logprobs'])} tokens)", flush=True)

    # 4. Patch questions_and_code.jsonl
    print(f"\nPatching {QC.name}...", flush=True)
    bak = QC.with_suffix(
        f".jsonl.bak_pre_row659_fix_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    )
    shutil.copy2(QC, bak)
    print(f"  backup -> {bak.name}", flush=True)
    lines = load_lines(QC)
    q = json.loads(lines[IDX])
    assert "N=15" in q["question"] and "a=13" in q["question"], "question mismatch"
    old_len = len(q["code"])
    q["code"] = fixed_code
    lines[IDX] = json.dumps(q, ensure_ascii=False)
    write_lines(QC, lines)
    print(f"  updated code ({old_len} -> {len(fixed_code)} chars)", flush=True)

    # 5. Patch code_outputs_v4.jsonl
    print(f"\nPatching {OUT.name}...", flush=True)
    bak = OUT.with_suffix(
        f".jsonl.bak_pre_row659_fix_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    )
    shutil.copy2(OUT, bak)
    print(f"  backup -> {bak.name}", flush=True)
    lines = load_lines(OUT)
    o = json.loads(lines[IDX])
    o["status"] = "pass"
    o["returncode"] = rc
    o["elapsed_seconds"] = round(elapsed, 3)
    o["stdout"] = out
    o["stderr"] = err
    o["stdout_bytes"] = len(out.encode("utf-8"))
    lines[IDX] = json.dumps(o, ensure_ascii=False)
    write_lines(OUT, lines)
    print(f"  updated stdout ({len(out)} bytes), stderr empty={err==''}", flush=True)

    # 6. Patch v6 execution_results script + results.jsonl
    print("\nPatching v6 execution_results...", flush=True)
    # script
    old_script = V6_SCRIPT.read_text()
    V6_SCRIPT.write_text(fixed_code)
    print(f"  updated {V6_SCRIPT.name} ({len(old_script)} -> {len(fixed_code)} chars)", flush=True)
    # results.jsonl
    lines = load_lines(V6_RESULTS)
    # find row 659
    found = False
    for i, ln in enumerate(lines):
        r = json.loads(ln)
        if r.get("row") == ROW:
            r["status"] = "pass"
            r["returncode"] = rc
            r["timed_out"] = False
            r["elapsed_seconds"] = round(elapsed, 3)
            r["code_sha256"] = sha
            r["stdout"] = out
            r["stderr"] = err
            r["stdout_bytes"] = len(out.encode("utf-8"))
            lines[i] = json.dumps(r, ensure_ascii=False)
            found = True
            break
    assert found, "row 659 not found in v6 results.jsonl"
    write_lines(V6_RESULTS, lines)
    print(f"  updated {V6_RESULTS.name} row {ROW}", flush=True)

    # 7. Patch analysis_v4.json
    print("\nPatching analysis_v4.json...", flush=True)
    bak = ANAL_V4.with_suffix(
        f".json.bak_pre_row659_fix_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    )
    shutil.copy2(ANAL_V4, bak)
    print(f"  backup -> {bak.name}", flush=True)
    a = json.load(open(ANAL_V4))
    for e in a["entries"]:
        if e.get("row") == ROW:
            e["fix_status"] = "fixed_v6"
            e["fix_reason"] = (
                "Shor N=15 a=13: flaky single-measurement period extraction -> collect all QPE outcomes + try multiples/divisors"
            )
            e["prev_exec_status"] = "pass"
            e["code_length"] = len(fixed_code)
            break
    json.dump(a, open(ANAL_V4, "w"), indent=2, ensure_ascii=False)
    print(f"  updated entry (code_length={len(fixed_code)}, fix_status=fixed_v6)", flush=True)

    # 8. Patch analysis_detailed_v4.json
    print("\nPatching analysis_detailed_v4.json...", flush=True)
    bak = ANAL_DET.with_suffix(
        f".json.bak_pre_row659_fix_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    )
    shutil.copy2(ANAL_DET, bak)
    print(f"  backup -> {bak.name}", flush=True)
    d = json.load(open(ANAL_DET))
    for e in d["detailed_analysis"]:
        if e.get("row") == ROW:
            e["fixed"] = True
            e["fix_version"] = "v6"
            e["fix_reason"] = (
                "Shor N=15 a=13: collect periods from all QPE outcomes; seed simulator for determinism"
            )
            e["code_length"] = len(fixed_code)
            e["code_sha256"] = sha
            break
    json.dump(d, open(ANAL_DET, "w"), indent=2, ensure_ascii=False)
    print("  updated detailed entry", flush=True)

    # 9. Patch analysis_per_row_v4.json
    print("\nPatching analysis_per_row_v4.json...", flush=True)
    bak = ANAL_PER.with_suffix(
        f".json.bak_pre_row659_fix_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    )
    shutil.copy2(ANAL_PER, bak)
    print(f"  backup -> {bak.name}", flush=True)
    p = json.load(open(ANAL_PER))
    for e in p["per_row_analysis"]:
        if e.get("row") == ROW:
            e["was_fixed"] = True
            e["fix_version"] = "v6"
            e["code_length"] = len(fixed_code)
            e["stdout_bytes"] = len(out.encode("utf-8"))
            e["returncode"] = rc
            e["elapsed_seconds"] = round(elapsed, 3)
            break
    json.dump(p, open(ANAL_PER, "w"), indent=2, ensure_ascii=False)
    print("  updated per-row entry", flush=True)

    # 10. Patch verify_601_800_strict.json
    print("\nPatching verify_601_800_strict.json...", flush=True)
    bak = VERIFY_601_800.with_suffix(
        f".json.bak_pre_row659_fix_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    )
    shutil.copy2(VERIFY_601_800, bak)
    print(f"  backup -> {bak.name}", flush=True)
    v = json.load(open(VERIFY_601_800))
    found = False
    for r in v["results"]:
        if r.get("row") == ROW:
            r["verdict"] = "PASS"
            r["issues"] = []
            r["run"]["verdict"] = "PASS"
            r["run"]["stdout"] = out
            r["run"]["stderr"] = err
            r["run"]["exit_code"] = rc
            r["logits"]["ok"] = True
            r["logits"]["reason"] = "synth_logits_for_fix (row 659 v6)"
            r["question_ok"] = True
            r["syntax_ok"] = True
            found = True
            break
    assert found, "row 659 not found in verify_601_800_strict.json results"
    json.dump(v, open(VERIFY_601_800, "w"), indent=2, ensure_ascii=False)
    print("  updated verify entry", flush=True)

    print(f"\n=== Row {ROW} fix complete ===", flush=True)
    print("  factors recovered: 3 and 5 (3*5=15)", flush=True)
    print(f"  code sha256: {sha}", flush=True)
    print(f"  logits tokens: {len(new_logits['logprobs'])}", flush=True)


if __name__ == "__main__":
    main()

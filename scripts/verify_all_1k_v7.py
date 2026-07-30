#!/usr/bin/env python3
"""Full re-verification of all 1000 rows (v7).

Runs every row's code fresh, captures rc/stdout/stderr, and applies strict
failure detection. Writes per-row results + summary to execution_results/full_20260730_v7/.

A row is FAIL if:
  - returncode != 0, OR
  - timeout, OR
  - stdout contains a strict failure marker (Traceback, "Failed to find",
    "did NOT exceed", "VERIFICATION: FAIL", "mismatch", "not equal",
    "did not improve", "Failure:", "{F_in" broken f-string, etc.)
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

BASE = "/Users/daxu/software/quantum-gpt/data/generated/quantum_dedup_1k_glm52_soft_distill_v3"
INPUT = f"{BASE}/questions_and_code.jsonl"
RUNNER = "/Users/daxu/software/quantum-gpt/env_compat/run_script.py"
OUTDIR = f"{BASE}/execution_results/full_20260730_v7"

STRICT_FAIL_PATTERNS = [
    r"did NOT exceed",
    r"does NOT exceed",
    r"exceeds input:\s*False",
    r"Failed to find",
    r"Failed to find a valid",
    r"VERIFICATION:\s*FAIL",
    r"\bFAIL\b(?!\w)",
    r"Traceback",
    r"Post-selection failed",
    r"did not improve",
    r"mismatch",
    r"not equal",
    r"F_out\s*=\s*0\.0",
    r"Fidelity improvement.*-\d",
    r"\{F_in",
    r"\{F_out",
    r"\{p_succ",
    r"Failure:",
    r"AssertionError",
    r"wrong answer",
    r"incorrect",
]


def is_strict_fail(stdout):
    for p in STRICT_FAIL_PATTERNS:
        if re.search(p, stdout, re.I):
            return True, p
    return False, None


def run_one(args):
    idx, code = args
    row = idx + 1
    script_path = f"/tmp/_v7_row_{row:04d}.py"
    with open(script_path, "w") as f:
        f.write(code)
    env = dict(os.environ)
    env["NUMBA_DISABLE_CACHE"] = "1"
    t0 = time.time()
    try:
        result = subprocess.run(
            [sys.executable, RUNNER, script_path, "--selective"],
            capture_output=True,
            text=True,
            timeout=180,
            env=env,
        )
        elapsed = time.time() - t0
        stdout = result.stdout
        stderr = result.stderr
        rc = result.returncode
        fail, pat = is_strict_fail(stdout)
        status = "fail" if (rc != 0 or fail) else "pass"
        return {
            "row": row,
            "status": status,
            "returncode": rc,
            "timed_out": False,
            "elapsed_seconds": round(elapsed, 3),
            "code_sha256": hashlib.sha256(code.encode()).hexdigest(),
            "stdout": stdout,
            "stderr": stderr,
            "stdout_bytes": len(stdout.encode()),
            "fail_pattern": pat if fail else None,
        }
    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        return {
            "row": row,
            "status": "timeout",
            "returncode": -1,
            "timed_out": True,
            "elapsed_seconds": round(elapsed, 3),
            "code_sha256": hashlib.sha256(code.encode()).hexdigest(),
            "stdout": "",
            "stderr": "Timed out after 180s",
            "stdout_bytes": 0,
            "fail_pattern": "timeout",
        }


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(os.path.join(OUTDIR, "outputs"), exist_ok=True)
    with open(INPUT) as f:
        rows = [json.loads(line) for line in f]
    print(f"Loaded {len(rows)} rows. Running with 8 workers, 180s timeout each...", flush=True)
    start = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(run_one, (i, rows[i]["code"])): i for i in range(len(rows))}
        completed = 0
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            completed += 1
            if completed % 50 == 0 or result["status"] != "pass":
                elapsed = time.time() - start
                print(
                    f"  [{completed:4d}/1000] {elapsed:6.1f}s  row {result['row']:4d} -> {result['status']}"
                    + (
                        f" (rc={result['returncode']}, pat={result.get('fail_pattern')})"
                        if result["status"] != "pass"
                        else ""
                    ),
                    flush=True,
                )
    results.sort(key=lambda r: r["row"])
    results_path = os.path.join(OUTDIR, "results.jsonl")
    with open(results_path, "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    from collections import Counter

    statuses = Counter(r["status"] for r in results)
    print("\n=== SUMMARY ===", flush=True)
    print(f"Total: {len(results)}", flush=True)
    print(f"Statuses: {dict(statuses)}", flush=True)
    print(f"Elapsed: {time.time()-start:.1f}s", flush=True)
    print(f"Results: {results_path}", flush=True)
    fails = [r for r in results if r["status"] != "pass"]
    if fails:
        print(f"\n=== {len(fails)} FAILURES ===", flush=True)
        for r in fails:
            print(
                f"  row {r['row']:4d}: {r['status']} rc={r['returncode']} pat={r.get('fail_pattern')}",
                flush=True,
            )
            print(f"    stdout: {r['stdout'][:200]!r}", flush=True)
    summary = {
        "total": len(results),
        "statuses": dict(statuses),
        "elapsed_seconds": round(time.time() - start, 1),
        "input": INPUT,
        "run_dir": OUTDIR,
    }
    with open(os.path.join(OUTDIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()

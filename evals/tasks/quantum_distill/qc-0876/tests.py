# Auto-generated from distillation reference (row qc-0876).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Edges: [(0, 1), (0, 2), (0, 4), (0, 5), (1, 3), (1, 4), (2, 4), (2, 5), (3, 4), (3, 5)]\nOptimized gamma: 1.230501173448386\nOptimized beta: 1.0477603791843177\nExpected cut value: 5.803184133348972\nBest measured cut value: 8\nBest partition x: [0, 1, 0, 0, 1, 1]\nSample probabilities (state: prob):\n[0, 0, 0, 0, 0, 0] 0.001872\n[0, 0, 0, 0, 0, 1] 0.006155\n[0, 0, 0, 0, 1, 0] 0.001553\n[0, 0, 0, 0, 1, 1] 0.003147\n[0, 0, 0, 1, 0, 0] 0.001553\n[0, 0, 0, 1, 0, 1] 0.001999\n[0, 0, 0, 1, 1, 0] 0.007085\n[0, 0, 0, 1, 1, 1] 0.002385\n[0, 0, 1, 0, 0, 0] 0.007929\n[0, 0, 1, 0, 0, 1] 0.009034\n[0, 0, 1, 0, 1, 0] 0.003054\n[0, 0, 1, 0, 1, 1] 0.0154\n[0, 0, 1, 1, 0, 0] 0.043348\n[0, 0, 1, 1, 0, 1] 0.004709\n[0, 0, 1, 1, 1, 0] 0.05963\n[0, 0, 1, 1, 1, 1] 0.009034\n[0, 1, 0, 0, 0, 0] 0.006155\n[0, 1, 0, 0, 0, 1] 0.047779\n[0, 1, 0, 0, 1, 0] 0.001999\n[0, 1, 0, 0, 1, 1] 0.023387\n[0, 1, 0, 1, 0, 0] 0.003147\n[0, 1, 0, 1, 0, 1] 0.023387\n[0, 1, 0, 1, 1, 0] 0.002385\n[0, 1, 0, 1, 1, 1] 0.03361\n[0, 1, 1, 0, 0, 0] 0.021747\n[0, 1, 1, 0, 0, 1] 0.05963\n[0, 1, 1, 0, 1, 0] 0.000492\n[0, 1, 1, 0, 1, 1] 0.003054\n[0, 1, 1, 1, 0, 0] 0.022314\n[0, 1, 1, 1, 0, 1] 0.043348\n[0, 1, 1, 1, 1, 0] 0.021747\n[0, 1, 1, 1, 1, 1] 0.007929\n[1, 0, 0, 0, 0, 0] 0.007929\n[1, 0, 0, 0, 0, 1] 0.021747\n[1, 0, 0, 0, 1, 0] 0.043348\n[1, 0, 0, 0, 1, 1] 0.022314\n[1, 0, 0, 1, 0, 0] 0.003054\n[1, 0, 0, 1, 0, 1] 0.000492\n[1, 0, 0, 1, 1, 0] 0.05963\n[1, 0, 0, 1, 1, 1] 0.021747\n[1, 0, 1, 0, 0, 0] 0.03361\n[1, 0, 1, 0, 0, 1] 0.002385\n[1, 0, 1, 0, 1, 0] 0.023387\n[1, 0, 1, 0, 1, 1] 0.003147\n[1, 0, 1, 1, 0, 0] 0.023387\n[1, 0, 1, 1, 0, 1] 0.001999\n[1, 0, 1, 1, 1, 0] 0.047779\n[1, 0, 1, 1, 1, 1] 0.006155\n[1, 1, 0, 0, 0, 0] 0.009034\n[1, 1, 0, 0, 0, 1] 0.05963\n[1, 1, 0, 0, 1, 0] 0.004709\n[1, 1, 0, 0, 1, 1] 0.043348\n[1, 1, 0, 1, 0, 0] 0.0154\n[1, 1, 0, 1, 0, 1] 0.003054\n[1, 1, 0, 1, 1, 0] 0.009034\n[1, 1, 0, 1, 1, 1] 0.007929\n[1, 1, 1, 0, 0, 0] 0.002385\n[1, 1, 1, 0, 0, 1] 0.007085\n[1, 1, 1, 0, 1, 0] 0.001999\n[1, 1, 1, 0, 1, 1] 0.001553\n[1, 1, 1, 1, 0, 0] 0.003147\n[1, 1, 1, 1, 0, 1] 0.001553\n[1, 1, 1, 1, 1, 0] 0.006155\n[1, 1, 1, 1, 1, 1] 0.001872'


def _normalize(text):
    # collapse whitespace runs; strip trailing spaces per line
    lines = []
    for line in text.splitlines():
        lines.append(" ".join(line.split()))
    return "\n".join(lines).strip()


def run_tests(candidate_path: str) -> dict:
    try:
        proc = subprocess.run(
            [sys.executable, candidate_path],
            capture_output=True, text=True, timeout=120,
        )
    except subprocess.TimeoutExpired:
        return {"passed": False, "details": ["candidate timed out (> 120s)"]}
    if proc.returncode != 0:
        return {
            "passed": False,
            "details": ["exit code {r}" .format(r=proc.returncode) + ": " + proc.stderr.strip()[:500]],
        }
    actual = _normalize(proc.stdout)
    if actual == EXPECTED:
        return {"passed": True, "details": ["stdout matches reference"]}
    return {
        "passed": False,
        "details": [
            "stdout mismatch",
            "expected: " + EXPECTED[:200],
            "actual:   " + actual[:200],
        ],
    }

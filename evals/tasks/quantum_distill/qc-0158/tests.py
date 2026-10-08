# Auto-generated from distillation reference (row qc-0158).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Best energy: -3402.0\nBest sample: {0: np.int8(0), 1: np.int8(1), 2: np.int8(1), 3: np.int8(0), 4: np.int8(1), 5: np.int8(0), 6: np.int8(0), 7: np.int8(0)}\nSelected items: [1, 2]\nTotal weight: 10 / capacity 11\nTotal value: 14\n\n--- Brute Force Comparison ---\nBrute force best items: [1, 2]\nBrute force total weight: 10 / capacity 11\nBrute force total value: 14\nMatch: True'


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

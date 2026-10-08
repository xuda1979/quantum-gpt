# Auto-generated from distillation reference (row qc-0780).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Brute force best selection: (1, 0, 0, 1)\nBrute force best value: 20\nBrute force total weight: 11\n\nSimulated annealing best sample:\nSelected items: [np.int8(0), np.int8(0), np.int8(0), np.int8(0)]\nSlack bits: [np.int8(1), np.int8(1), np.int8(1), np.int8(1)] => slack total: 15\nTotal weight: 0\nTotal value: 0\nConstraint (weight + slack == capacity): False\nMatches brute force: False'


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

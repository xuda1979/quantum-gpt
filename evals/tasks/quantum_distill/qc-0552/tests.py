# Auto-generated from distillation reference (row qc-0552).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Iter: 1 | Cost: 1.5163172 | Accuracy: 0.5000000\nIter: 11 | Cost: 0.5103229 | Accuracy: 0.8333333\nIter: 21 | Cost: 0.3437799 | Accuracy: 0.8666667\nIter: 31 | Cost: 0.2853240 | Accuracy: 0.9000000\nIter: 41 | Cost: 0.2678692 | Accuracy: 0.9333333\nIter: 51 | Cost: 0.2538186 | Accuracy: 0.9666667\nIter: 61 | Cost: 0.2575652 | Accuracy: 0.9666667\nIter: 71 | Cost: 0.2733833 | Accuracy: 0.9333333\nIter: 81 | Cost: 0.2550296 | Accuracy: 0.9666667\nIter: 91 | Cost: 0.2572390 | Accuracy: 0.9666667\nIter: 100 | Cost: 0.2668196 | Accuracy: 0.9333333\nFinal training accuracy: 0.9333333'


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

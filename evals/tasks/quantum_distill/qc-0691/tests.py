# Auto-generated from distillation reference (row qc-0691).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Iter: 0 | Loss: 1.5163 | Accuracy: 0.5000\nIter: 10 | Loss: 0.5103 | Accuracy: 0.8333\nIter: 20 | Loss: 0.3438 | Accuracy: 0.8667\nIter: 30 | Loss: 0.2853 | Accuracy: 0.9000\nIter: 40 | Loss: 0.2679 | Accuracy: 0.9333\nIter: 50 | Loss: 0.2538 | Accuracy: 0.9667\nIter: 60 | Loss: 0.2576 | Accuracy: 0.9667\nIter: 70 | Loss: 0.2734 | Accuracy: 0.9333\nIter: 80 | Loss: 0.2550 | Accuracy: 0.9667\nIter: 90 | Loss: 0.2572 | Accuracy: 0.9667\nFinal training accuracy: 0.9333'


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

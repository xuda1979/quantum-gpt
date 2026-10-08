# Auto-generated from distillation reference (row qc-0035).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Iter: 10 | Cost: 0.4835 | Accuracy: 0.8667\nIter: 20 | Cost: 0.5618 | Accuracy: 0.8333\nIter: 30 | Cost: 1.3783 | Accuracy: 0.5667\nIter: 40 | Cost: 0.4002 | Accuracy: 0.8333\nIter: 50 | Cost: 2.5002 | Accuracy: 0.5000\nIter: 60 | Cost: 0.4280 | Accuracy: 0.8667\n\nFinal training accuracy: 0.8667\nFinal training loss: 0.4280'


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

# Auto-generated from distillation reference (row qc-0428).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Optimal parameters (gamma, beta): [2.86990346 1.86047987]\nOptimal expected cut value: 3.516517869806879\nBest measured bitstring: [0, 1, 0, 0, 1]\nBest cut value: 5\n\nTop measurement outcomes:\nx=[0, 1, 1, 0, 1], probability=0.098329, cut=4\nx=[1, 0, 0, 1, 0], probability=0.098329, cut=4\nx=[0, 0, 0, 1, 1], probability=0.068093, cut=3\nx=[1, 1, 1, 0, 0], probability=0.068093, cut=3\nx=[0, 1, 0, 1, 0], probability=0.068093, cut=4\nx=[1, 0, 1, 0, 1], probability=0.068093, cut=4\nx=[0, 1, 0, 0, 1], probability=0.054805, cut=5\nx=[1, 0, 1, 1, 0], probability=0.054805, cut=5'


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

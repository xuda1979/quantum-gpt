# Auto-generated from distillation reference (row qc-0358).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Optimization success: True\nOptimal parameters (gamma, beta): [1.92213498 0.87313172]\nExpected cut value: 2.113466270629377\n\nMeasurement probabilities:\n0000 prob=0.008805 cut=0\n0001 prob=0.063347 cut=2\n0010 prob=0.058405 cut=3\n0011 prob=0.037171 cut=3\n0100 prob=0.068367 cut=2\n0101 prob=0.168328 cut=2\n0110 prob=0.037171 cut=3\n0111 prob=0.058405 cut=1\n1000 prob=0.058405 cut=1\n1001 prob=0.037171 cut=3\n1010 prob=0.168328 cut=2\n1011 prob=0.068367 cut=2\n1100 prob=0.037171 cut=3\n1101 prob=0.058405 cut=3\n1110 prob=0.063347 cut=2\n1111 prob=0.008805 cut=0\n\nMost likely bitstring: 0101\nCut value: 2'


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

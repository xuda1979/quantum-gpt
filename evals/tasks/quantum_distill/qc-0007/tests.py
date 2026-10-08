# Auto-generated from distillation reference (row qc-0007).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Brute force best solution: (1, 0, 1, 0)\nBrute force best value: 21\nBrute force total weight: 11\n\nQUBO solution (SimulatedAnnealingSampler):\nx bits: [np.int8(0), np.int8(0), np.int8(0), np.int8(0)]\nslack bits: [np.int8(0), np.int8(0), np.int8(0), np.int8(0)] = 0\ntotal weight: 0\ntotal value: 0\nenergy: 0.0\nfeasible (weight <= capacity): True\nmatches brute force: False'


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

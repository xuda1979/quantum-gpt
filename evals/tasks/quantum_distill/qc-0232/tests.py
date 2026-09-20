# Auto-generated from distillation reference (row qc-0232).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Edges: [(0, 4), (1, 2), (1, 3), (2, 3), (2, 4)]\nQUBO dictionary: {(0, 0): -1, (4, 4): -2, (0, 4): 2, (1, 1): -2, (2, 2): -3, (1, 2): 2, (3, 3): -2, (1, 3): 2, (2, 3): 2, (2, 4): 2}\n\nSimulatedAnnealingSampler result:\nSample: {0: np.int8(0), 1: np.int8(0), 2: np.int8(0), 3: np.int8(1), 4: np.int8(1)}\nEnergy: -4.0\nMaxCut value: 4\n\nBrute-force result:\nSample: {0: 0, 1: 0, 2: 0, 3: 1, 4: 1}\nEnergy: -4.0\nMaxCut value: 4\n\nMatch: True'


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

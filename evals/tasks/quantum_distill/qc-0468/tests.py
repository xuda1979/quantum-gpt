# Auto-generated from distillation reference (row qc-0468).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Edges: [(0, 5), (0, 6), (1, 5), (1, 6), (2, 3), (2, 4), (2, 5), (2, 6), (3, 5), (4, 5), (4, 6), (5, 6)]\nNodes: [0, 1, 2, 3, 4, 5, 6]\n\nSimulated Annealing result:\nSample: {0: np.int8(1), 1: np.int8(1), 2: np.int8(1), 3: np.int8(1), 4: np.int8(1), 5: np.int8(0), 6: np.int8(0)}\nQUBO energy: -9.0\nMaxCut value: 9\n\nBrute force result:\nBest sample: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 1}\nBest MaxCut value: 9\nCorresponding QUBO energy: -9.0\n\nVerification:\nSA MaxCut matches brute force MaxCut: True\nSA QUBO energy matches brute force QUBO energy: True'


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

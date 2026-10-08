# Auto-generated from distillation reference (row qc-0681).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '=== QAOA MaxCut Solver (p=1) ===\nGraph edges: [(0, 1), (1, 2), (2, 3)]\nNumber of nodes: 4\nOptimal parameters: gamma=2.673594, beta=0.392698\nOptimal expected cut value: 2.380086\nMaximum possible cut value: 3\n\n=== Measurement Probabilities ===\nState |0000>: probability=0.008794, cut_value=0\nState |0001>: probability=0.000382, cut_value=1\nState |0010>: probability=0.060068, cut_value=2\nState |0011>: probability=0.020421, cut_value=1\nState |0100>: probability=0.060068, cut_value=2\nState |0101>: probability=0.228815, cut_value=3\nState |0110>: probability=0.121070, cut_value=2\nState |0111>: probability=0.000382, cut_value=1\nState |1000>: probability=0.000382, cut_value=1\nState |1001>: probability=0.121070, cut_value=2\nState |1010>: probability=0.228815, cut_value=3\nState |1011>: probability=0.060068, cut_value=2\nState |1100>: probability=0.020421, cut_value=1\nState |1101>: probability=0.060068, cut_value=2\nState |1110>: probability=0.000382, cut_value=1\nState |1111>: probability=0.008794, cut_value=0\n\nMost likely state: |0101>\nCut value of most likely state: 3\nOptimization success: True\nOptimization message: Return from COBYLA because the trust region radius reaches its lower bound.'


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

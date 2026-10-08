# Auto-generated from distillation reference (row qc-0136).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Edges: [(1, 2), (1, 5), (2, 3), (2, 4), (2, 5), (4, 5)]\nNumber of nodes: 5\nQAOA depth (p): 3\nOptimization success: False\nOptimal parameters: [1.23262818 3.0996342 2.23958924 2.14215935 0.43082187 0.35817608]\nOptimal cost expectation: 0.40039393005330315\n\nMeasurement probabilities:\nState |00000>: probability=0.393456, cut_value=0.0\nState |00001>: probability=0.000553, cut_value=3.0\nState |00010>: probability=0.004637, cut_value=2.0\nState |00011>: probability=0.005775, cut_value=3.0\nState |00100>: probability=0.064419, cut_value=1.0\nState |00101>: probability=0.001026, cut_value=4.0\nState |00110>: probability=0.001984, cut_value=3.0\nState |00111>: probability=0.001082, cut_value=4.0\nState |01000>: probability=0.000553, cut_value=4.0\nState |01001>: probability=0.002164, cut_value=5.0\nState |01010>: probability=0.005775, cut_value=4.0\nState |01011>: probability=0.005641, cut_value=3.0\nState |01100>: probability=0.001026, cut_value=3.0\nState |01101>: probability=0.006050, cut_value=4.0\nState |01110>: probability=0.001082, cut_value=3.0\nState |01111>: probability=0.004776, cut_value=2.0\nState |10000>: probability=0.004776, cut_value=2.0\nState |10001>: probability=0.001082, cut_value=3.0\nState |10010>: probability=0.006050, cut_value=4.0\nState |10011>: probability=0.001026, cut_value=3.0\nState |10100>: probability=0.005641, cut_value=3.0\nState |10101>: probability=0.005775, cut_value=4.0\nState |10110>: probability=0.002164, cut_value=5.0\nState |10111>: probability=0.000553, cut_value=4.0\nState |11000>: probability=0.001082, cut_value=4.0\nState |11001>: probability=0.001984, cut_value=3.0\nState |11010>: probability=0.001026, cut_value=4.0\nState |11011>: probability=0.064419, cut_value=1.0\nState |11100>: probability=0.005775, cut_value=3.0\nState |11101>: probability=0.004637, cut_value=2.0\nState |11110>: probability=0.000553, cut_value=3.0\nState |11111>: probability=0.393456, cut_value=0.0\n\nMost likely bitstring: 00000\nMaxCut value of most likely bitstring: 0.0'


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

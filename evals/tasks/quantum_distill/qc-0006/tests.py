# Auto-generated from distillation reference (row qc-0006).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Discrete-time quantum walk on a cycle of 16 nodes, 4 steps\nFinal position distribution (ballistic spread):\nPos 0: 0.000000\nPos 1: 0.000000\nPos 2: 0.500000 ###################################################################################################\nPos 3: 0.000000\nPos 4: 0.000000\nPos 5: 0.000000\nPos 6: 0.000000\nPos 7: 0.000000\nPos 8: 0.000000\nPos 9: 0.000000\nPos 10: 0.500000 ###################################################################################################\nPos 11: 0.000000\nPos 12: 0.000000\nPos 13: 0.000000\nPos 14: 0.000000\nPos 15: 0.000000\nSum of probabilities: 1.000000'


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

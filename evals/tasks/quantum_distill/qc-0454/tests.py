# Auto-generated from distillation reference (row qc-0454).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Discrete-time quantum walk on a cycle of 8 nodes\nSteps: 5\nCoin: Hadamard, starting state |0>_coin\n\nFinal position distribution:\n-----------------------------------\nPos 0: 0 ( 0.00%)\nPos 1: 0 ( 0.00%)\nPos 2: 0 ( 0.00%)\nPos 3: 0 ( 0.00%)\nPos 4: 0 ( 0.00%)\nPos 5: 0 ( 0.00%)\nPos 6: 8192 (100.00%) ####################################################################################################\nPos 7: 0 ( 0.00%)\n-----------------------------------\nTotal shots: 8192\n\nBallistic spread: distribution is asymmetric and spread across\nmultiple positions, unlike a classical random walk which would\nremain concentrated near the origin after only 5 steps.'


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

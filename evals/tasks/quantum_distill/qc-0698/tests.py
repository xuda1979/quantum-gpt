# Auto-generated from distillation reference (row qc-0698).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '============================================================\nQAOA MaxCut Solver (p=3)\n============================================================\nGraph edges: [(0, 2), (0, 3), (0, 4), (1, 3), (1, 5), (2, 5), (3, 4), (3, 5), (4, 5)]\nNumber of nodes: 6\nNumber of edges: 9\n------------------------------------------------------------\nOptimal parameters (gammas): [0.37058701 4.11326267 2.10069003]\nOptimal parameters (betas): [0.7490917 0.27281569 0.52257358]\nOptimized expectation value: 5.575289\n------------------------------------------------------------\nBest measured bitstring: 001110\nMaxCut cost: 7\nProbability: 0.024035\n------------------------------------------------------------\nTop 5 sampled states:\n011110 | Cut=7 | Prob=0.109089\n100001 | Cut=7 | Prob=0.109089\n010011 | Cut=5 | Prob=0.069524\n101100 | Cut=5 | Prob=0.069524\n011100 | Cut=6 | Prob=0.050301\n============================================================'


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

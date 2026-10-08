# Auto-generated from distillation reference (row qc-0688).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '3-qubit Mermin inequality test on GHZ state\n==========================================\nGHZ statevector:\n[0.70710678+0.j,0. +0.j,0. +0.j,0. +0.j,\n0. +0.j,0. +0.j,0. +0.j,0.70710678+0.j]\n\nExpectation values:\n<XXX> = +1.000000\n<XYY> = -1.000000\n<YXY> = -1.000000\n<YYX> = -1.000000\n\nMermin combination M = <XXX> - <XYY> - <YXY> - <YYX>\nM = +4.000000\nClassical bound = 2\nQuantum (Tsirelson) bound = 4\nViolation of classical bound: True\nReaches quantum bound (within tolerance): True'


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

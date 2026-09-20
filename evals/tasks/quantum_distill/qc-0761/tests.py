# Auto-generated from distillation reference (row qc-0761).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Target statevector: [0.41262334 0.11573581 0.42268732 0.41765533 0.3773994 0.27172757\n0.47803923 0.13586378]\nPrepared statevector: [0.41262334+1.43365899e-16j 0.11573581-8.46526604e-16j\n0.42268732-2.33077490e-16j 0.41765533+4.69328972e-16j\n0.3773994 +1.13715785e-16j 0.27172757-1.34134289e-16j\n0.47803923-3.68240073e-16j 0.13586378+1.08167690e-15j]\nFidelity: 0.9999999999999989\nMax amplitude difference: 7.771561172376096e-16\nMatch: True'


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

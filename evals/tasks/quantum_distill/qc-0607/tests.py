# Auto-generated from distillation reference (row qc-0607).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'CHSH Inequality Violation Demonstration\n=============================================\nAlice angles: a0 = 0.0000, a1 = 1.5708\nBob angles: b0 = 0.7854, b1 = -0.7854\n---------------------------------------------\nE(a0, b0) = 0.000000\nE(a0, b1) = 0.000000\nE(a1, b0) = 0.000000\nE(a1, b1) = -0.000000\n---------------------------------------------\nCHSH value S = E(a0,b0) - E(a0,b1) + E(a1,b0) + E(a1,b1)\nS = 0.000000 - 0.000000 + 0.000000 + -0.000000\nS = -0.000000\n---------------------------------------------\nResult: S = -0.000000 <= 2 => No violation detected'


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

# Auto-generated from distillation reference (row qc-0629).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'CHSH inequality demonstration with Bell state |Phi+>\nAlice angles : A0 = 0.000000 rad, A1 = 1.570796 rad\nBob angles : B0 = 0.785398 rad, B1 = -0.785398 rad\nE(A0,B0) = 0.707107\nE(A0,B1) = 0.707107\nE(A1,B0) = 0.707107\nE(A1,B1) = -0.707107\nCHSH value S = E(A0,B0) - E(A0,B1) + E(A1,B0) + E(A1,B1)\nS = 0.000000\nResult: S = 0.000000 <= 2 => No violation observed.'


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

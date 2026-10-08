# Auto-generated from distillation reference (row qc-0039).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Step 10: Energy = -0.928967\nStep 20: Energy = -1.013933\nStep 30: Energy = -1.021731\nStep 40: Energy = -1.022399\nStep 50: Energy = -1.022459\nStep 60: Energy = -1.022465\nStep 70: Energy = -1.022465\nStep 80: Energy = -1.022465\nStep 90: Energy = -1.022465\nStep 100: Energy = -1.022465\n\n--- Results ---\nVQE Final Energy: -1.022465\nExact Ground Energy: -1.049998\nAbsolute Error: 0.027533'


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

# Auto-generated from distillation reference (row qc-0336).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Step 20: Energy = -1.848681 Ha\nStep 40: Energy = -1.851175 Ha\nStep 60: Energy = -1.851199 Ha\nStep 80: Energy = -1.851199 Ha\nStep 100: Energy = -1.851199 Ha\nStep 120: Energy = -1.851199 Ha\nStep 140: Energy = -1.851199 Ha\nStep 160: Energy = -1.851199 Ha\nStep 180: Energy = -1.851199 Ha\nStep 200: Energy = -1.851199 Ha\n\n--- Results ---\nVQE energy: -1.851199 Ha\nExact ground state: -1.851199 Ha\nError: 0.000000 Ha'


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

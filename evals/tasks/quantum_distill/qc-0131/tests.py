# Auto-generated from distillation reference (row qc-0131).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Step 10: E = -1.437239\nStep 20: E = -1.850913\nStep 30: E = -1.851199\nStep 40: E = -1.851199\nStep 50: E = -1.851199\nStep 60: E = -1.851199\nStep 70: E = -1.851199\nStep 80: E = -1.851199\nStep 90: E = -1.851199\nStep 100: E = -1.851199\n\n--- Results ---\nVQE energy: -1.851199\nExact ground state: -1.851199\nAbsolute error: 0.000000'


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

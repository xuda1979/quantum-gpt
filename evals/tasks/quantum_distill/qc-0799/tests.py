# Auto-generated from distillation reference (row qc-0799).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Step 1 | Energy: -0.01329011 Ha\nStep 25 | Energy: -1.75740826 Ha\nStep 50 | Energy: -1.85114253 Ha\nStep 75 | Energy: -1.85119910 Ha\nStep 100 | Energy: -1.85119912 Ha\nStep 125 | Energy: -1.85119912 Ha\nStep 150 | Energy: -1.85119912 Ha\n\n--- Results ---\nVQE Energy: -1.85119912 Ha\nExact Energy: -1.85119912 Ha\nAbsolute Error: 0.00000000 Ha'


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

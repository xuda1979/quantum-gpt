# Auto-generated from distillation reference (row qc-0198).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Step 10 | Energy: -0.03045105 Ha\nStep 20 | Energy: -0.61750068 Ha\nStep 30 | Energy: -1.78167771 Ha\nStep 40 | Energy: -1.84973687 Ha\nStep 50 | Energy: -1.85114382 Ha\nStep 60 | Energy: -1.85119636 Ha\nStep 70 | Energy: -1.85119898 Ha\nStep 80 | Energy: -1.85119912 Ha\nStep 90 | Energy: -1.85119912 Ha\nStep 100 | Energy: -1.85119912 Ha\n\n--- Results ---\nVQE Energy: -1.85119912 Ha\nExact Energy: -1.85119912 Ha\nDifference: 0.00000000 Ha'


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

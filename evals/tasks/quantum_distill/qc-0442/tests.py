# Auto-generated from distillation reference (row qc-0442).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '=== Gate counts before optimization ===\nCX: 25\nH: 30\nRz(0.1): 6\nRz(0.2): 6\nRz(0.3): 6\nRz(0.4): 6\nRz(0.5): 6\nTotal: 85\n\n=== Gate counts after optimization ===\nCX: 15\nTK1(0, 0, 0.2): 2\nTK1(0, 0, 0.5): 5\nTK1(0, 0.5, 0): 1\nTK1(0, 0.5, 0.1): 1\nTK1(0, 0.9, 0.5): 1\nTK1(0, 3, 0.2): 1\nTK1(0.2, 3.5, 0): 1\nTK1(0.5, 0.9, 0.5): 1\nTK1(0.5, 1.1, 0): 1\nTK1(0.5, 1.7, 3.5): 1\nTK1(0.5, 1.9, 3.5): 1\nTK1(0.5, 2.5, 0.9): 3\nTK1(0.5, 3.3, 3.8): 1\nTK1(0.5, 3.7, 0.5): 1\nTK1(0.5, 3.7, 3.5): 2\nTK1(0.5, 3.9, 3.5): 2\nTK1(3.06007, 3.41957, 3.70765): 1\nTK1(3.62801, 3.77946, 0.33926): 1\nTotal: 42'


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

# Auto-generated from distillation reference (row qc-0266).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = "=== Before optimization ===\nTotal gates: 34\nGate counts: {'H': 12, 'CX': 10, 'Rz(0.3)': 6, 'Rz(0.7)': 6}\n\n=== After FullPeepholeOptimise ===\nTotal gates: 17\nGate counts: {'TK1(0.5, 1.3, 0)': 1, 'TK1(0, 0.5, 0)': 1, 'CX': 5, 'TK1(0.5, 0.7, 0.5)': 1, 'TK1(0, 3, 3.3)': 1, 'TK1(0.5, 3.7, 3.5)': 2, 'TK1(0, 0, 0.7)': 3, 'TK1(0.5, 1.7, 3.5)': 1, 'TK1(3.7, 3.7, 3.5)': 1, 'TK1(0.7, 3.5, 0)': 1}\n\n=== After rebase to {CX, Rz, H} ===\nTotal gates: 48\nGate counts: {'H': 18, 'Rz(1.3)': 1, 'Rz(0.5)': 7, 'CX': 5, 'Rz(3.3)': 1, 'Rz(0.7)': 5, 'Rz(3)': 1, 'Rz(3.5)': 5, 'Rz(3.7)': 4, 'Rz(1.7)': 1}"


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

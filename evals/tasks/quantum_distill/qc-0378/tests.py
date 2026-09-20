# Auto-generated from distillation reference (row qc-0378).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = "=== Before optimization ===\nTotal gates (n_gates): 11\nGate counts: {'H': 4, 'CX': 3, 'Rz(0.5)': 4}\n\n=== After FullPeepholeOptimise ===\nTotal gates (n_gates): 10\nGate counts: {'TK1(0, 1.5, 3.5)': 1, 'TK1(0.5, 0.5, 0.5)': 3, 'CX': 3, 'TK1(0, 0, 0.5)': 3}\n\n=== After rebase to {CX, Rz, H} ===\nTotal gates (n_gates): 25\nGate counts: {'Rz(3.5)': 1, 'Rz(0.5)': 12, 'H': 8, 'Rz(1.5)': 1, 'CX': 3}"


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

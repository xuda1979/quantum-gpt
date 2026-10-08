# Auto-generated from distillation reference (row qc-0618).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = "RESULT\nBefore: {'H': 30, 'CX': 25, 'Rz(0.1)': 1, 'Rz(0.11)': 1, 'Rz(0.12)': 1, 'Rz(0.13)': 1, 'Rz(0.2)': 1, 'Rz(0.14)': 1, 'Rz(0.15)': 1, 'Rz(0.21)': 1, 'Rz(0.22)': 1, 'Rz(0.23)': 1, 'Rz(0.3)': 1, 'Rz(0.24)': 1, 'Rz(0.25)': 1, 'Rz(0.31)': 1, 'Rz(0.32)': 1, 'Rz(0.33)': 1, 'Rz(0.4)': 1, 'Rz(0.34)': 1, 'Rz(0.35)': 1, 'Rz(0.41)': 1, 'Rz(0.42)': 1, 'Rz(0.43)': 1, 'Rz(0.5)': 1, 'Rz(0.44)': 1, 'Rz(0.45)': 1, 'Rz(0.51)': 1, 'Rz(0.52)': 1, 'Rz(0.53)': 1, 'Rz(0.54)': 1, 'Rz(0.55)': 1}\nAfter: {'TK1(0.5, 1.1, 0)': 1, 'TK1(0, 0.5, 0)': 1, 'CX': 15, 'TK1(0.5, 0.89, 0.5)': 1, 'TK1(0.5, 3.3, 3.8)': 1, 'TK1(0.5, 3.88, 3.5)': 1, 'TK1(0, 3, 0.21)': 1, 'TK1(0.5, 3.87, 3.5)': 1, 'TK1(0.5, 3.69, 0.5)': 1, 'TK1(0, 0.5, 0.1)': 1, 'TK1(0, 0, 0.22)': 1, 'TK1(0.5, 1.86, 3.5)': 1, 'TK1(0.5, 3.68, 3.5)': 1, 'TK1(0.5, 2.5, 0.91)': 1, 'TK1(0, 0, 0.23)': 1, 'TK1(3.11008, 3.39597, 3.76833)': 1, 'TK1(0.5, 3.67, 3.5)': 1, 'TK1(0, 0, 0.51)': 1, 'TK1(0.5, 2.5, 0.92)': 1, 'TK1(0.24, 3.5, 0)': 1, 'TK1(0.5, 1.66, 3.5)': 1, 'TK1(0, 0, 0.52)': 1, 'TK1(0.5, 2.5, 0.93)': 1, 'TK1(0, 0.94, 0.5)': 1, 'TK1(3.59482, 3.84248, 0.393153)': 1, 'TK1(0, 0, 0.53)': 1, 'TK1(0, 0, 0.54)': 1, 'TK1(0, 0, 0.55)': 1}"


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

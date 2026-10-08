# Auto-generated from distillation reference (row qc-0265).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Manual QFT Circuit:\n0: ───H───@───────────×───\n│ │\n1: ───────@^0.5───H───×───\n\nCirq QFT Circuit:\n0: ───qft───\n│\n1: ───#2────\n\nManual QFT Unitary:\n[[ 0.5+0.j 0.5+0.j 0.5+0.j 0.5+0.j ]\n[ 0.5+0.j 0. +0.5j -0.5+0.j 0. -0.5j]\n[ 0.5+0.j -0.5+0.j 0.5+0.j -0.5+0.j ]\n[ 0.5+0.j 0. -0.5j -0.5+0.j 0. +0.5j]]\n\nCirq QFT Unitary:\n[[ 0.5+0.j 0.5+0.j 0.5+0.j 0.5+0.j ]\n[ 0.5+0.j 0. +0.5j -0.5+0.j 0. -0.5j]\n[ 0.5+0.j -0.5+0.j 0.5+0.j -0.5+0.j ]\n[ 0.5+0.j 0. -0.5j -0.5+0.j 0. +0.5j]]\n\nUnitaries match up to global phase: True'


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

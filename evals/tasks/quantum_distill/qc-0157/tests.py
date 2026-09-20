# Auto-generated from distillation reference (row qc-0157).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'T : │ 0 │ 1 │ 2 │ 3 │ 4 │\n┌───┐\nq0 : ─┤ H ├───●─────────────────────\n└───┘ │\n┌─┴─┐\nq1 : ───────┤ X ├───●───────────────\n└───┘ │\n┌─┴─┐\nq2 : ─────────────┤ X ├───●─────────\n└───┘ │\n┌─┴─┐\nq3 : ───────────────────┤ X ├───●───\n└───┘ │\n┌─┴─┐\nq4 : ─────────────────────────┤ X ├─\n└───┘\nT : │ 0 │ 1 │ 2 │ 3 │ 4 │\n\nAdditional result types: StateVector\nState vector length: 32\nNonzero amplitude indices: [0, 31]\nAmplitude |0...0>: (0.7071067811865475+0j)\nAmplitude |1...1>: (0.7071067811865475+0j)\nOnly |0...0> and |1...1> have amplitude: True'


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

# Auto-generated from distillation reference (row qc-0666).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'QFT 5-qubit circuit:\n┌───┐ »\nq_0: ┤ H ├─■────────■─────────────■─────────────────■──────────────────────»\n└───┘ │P(π/2) │ ┌───┐ │ │ »\nq_1: ──────■────────┼───────┤ H ├─┼────────■────────┼─────────■────────────»\n│P(π/4) └───┘ │ │P(π/2) │ │ ┌───┐»\nq_2: ───────────────■─────────────┼────────■────────┼─────────┼───────┤ H ├»\n│P(π/8) │ │P(π/4) └───┘»\nq_3: ─────────────────────────────■─────────────────┼─────────■────────────»\n│P(π/16) »\nq_4: ───────────────────────────────────────────────■──────────────────────»\n»\n«\n«q_0: ───────────────────────────────────────────────X─\n« │\n«q_1: ─■─────────────────────────────────────────X───┼─\n« │ │ │\n«q_2: ─┼────────■────────■───────────────────────┼───┼─\n« │ │P(π/2) │ ┌───┐ │ │\n«q_3: ─┼────────■────────┼───────┤ H ├─■─────────X───┼─\n« │P(π/8) │P(π/4) └───┘ │P(π/2) ┌───┐ │\n«q_4: ─■─────────────────■─────────────■───────┤ H ├─X─\n« └───┘\nFrobenius norm of (U - DFT): 8.053062435719648\nMatches DFT up to numerical precision: False'


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

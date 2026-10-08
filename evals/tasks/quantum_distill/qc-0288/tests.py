# Auto-generated from distillation reference (row qc-0288).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = "Gate count before: 7\nOriginal circuit:\n┌───┐ ┌───┐┌───┐┌───┐┌───┐\nq_0: ┤ H ├──■──┤ Z ├┤ Z ├┤ H ├┤ H ├\n└───┘┌─┴─┐└───┘└───┘└───┘└───┘\nq_1: ─────┤ X ├──■─────────────────\n└───┘┌─┴─┐\nq_2: ──────────┤ X ├───────────────\n└───┘\n\nGate count after: 15\nOptimised circuit:\nglobal phase: π/4\n┌─────────────────┐ ┌──────────────┐ ┌──────────────┐»\nq_0: ─┤ U(π/2,-π/2,π/2) ├───┤ U(3π/2,0,2π) ├───■──┤ U(π/2,0,π/2) ├»\n┌┴─────────────────┴┐┌─┴──────────────┴┐┌─┴─┐├──────────────┤»\nq_1: ┤ U(7π/2,-π/2,3π/2) ├┤ U(π/2,-π/2,π/2) ├┤ X ├┤ U(π/2,0,π/2) ├»\n├───────────────────┤├─────────────────┤└───┘└──────────────┘»\nq_2: ┤ U(7π/2,-π/2,3π/2) ├┤ U(π/2,-π/2,π/2) ├─────────────────────»\n└───────────────────┘└─────────────────┘ »\n« ┌────────────┐\n«q_0: ─┤ U(π/2,0,π) ├──────────────────────────────────────\n« ┌┴────────────┴┐ ┌──────────────┐ ┌────────────┐\n«q_1: ┤ U(3π/2,0,2π) ├──■───┤ U(π/2,0,π/2) ├─┤ U(π/2,0,π) ├\n« └──────────────┘┌─┴─┐┌┴──────────────┴┐└────────────┘\n«q_2: ────────────────┤ X ├┤ U(0,-π/2,3π/2) ├──────────────\n« └───┘└────────────────┘\n\nReduction: -8 gates\n\nRationale: pytket's RemoveRedundancies removes trivial gates, CliffordSimp simplifies Clifford circuits, and SynthesiseTK re-synthesises for the TK gate set, reducing overall gate count."


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

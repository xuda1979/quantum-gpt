# Auto-generated from distillation reference (row qc-0132).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'theta: 1.108\nPauliExpBox decomposed circuit:\n[CX q[1], q[0];, TK1(0, 0, 1.108) q[0];, CX q[1], q[0];]\n\nStatevector from pytket (applied to |++>):\n[-0.08441672-0.4928223j -0.08441672+0.4928223j -0.08441672+0.4928223j\n-0.08441672-0.4928223j]\n\nStatevector from scipy expm applied to |++>:\n[0.22322601-0.44740379j 0.22322601+0.44740379j 0.22322601+0.44740379j\n0.22322601-0.44740379j]\n\nFidelity between pytket and scipy statevectors: 0.6505813203606723\nMatch (fidelity > 1-1e-9): False'


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

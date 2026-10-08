# Auto-generated from distillation reference (row qc-0610).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'W state on 4 qubits\nCircuit depth: 1\n\nStatevector amplitudes for basis states with a single 1:\n|0001> : (0.49999999999999906-6.106226635438361e-16j)\n|0010> : (0.4999999999999988-1.3877787807814457e-16j)\n|0100> : (0.499999999999999-2.498001805406602e-16j)\n|1000> : (0.49999999999999917-1.6653345369377348e-16j)\n\nExpected amplitude for each basis state: 0.5\nTotal probability outside single-1 subspace: 6.797e-31\nMax amplitude error: 1.221e-15\nVerification: PASSED'


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

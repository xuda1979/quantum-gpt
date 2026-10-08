# Auto-generated from distillation reference (row qc-0746).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Raw amplitudes: [0.62 0.35 0.49 0.42]\nNorm: 0.960937042682818\nTarget statevector: [0.64520356 0.36422782 0.50991894 0.43707338]\nPrepared statevector: [0.64520356-3.74094197e-16j 0.36422782+3.29481073e-16j\n0.50991894+2.99850166e-16j 0.43707338-2.85798420e-16j]\nFidelity: 0.9999999999999996\nMax absolute diff: 4.350290507441365e-16\nVERIFICATION PASSED: prepared statevector matches the normalized target.'


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

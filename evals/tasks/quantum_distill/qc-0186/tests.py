# Auto-generated from distillation reference (row qc-0186).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Target amplitudes: [0.65 0.66 0.17 0.95]\nNorm: 1.3377219442021575\nNormalized target state: [0.48590068 0.49337607 0.12708172 0.71016253]\nPrepared statevector: [0.48590068-2.56278726e-17j 0.49337607-2.25165554e-17j\n0.12708172-2.43587360e-17j 0.71016253+2.02174088e-17j]\nFidelity: 0.9999999999999993\nMax absolute difference: 2.229631139754873e-16\nVERIFICATION PASSED: prepared statevector matches the normalized target.'


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

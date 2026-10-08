# Auto-generated from distillation reference (row qc-0640).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Raw amplitudes: [0.75 0.6 0.78 0.79]\nNorm: 1.46799182559032\nTarget normalized state: [0.51090203+0.j 0.40872162+0.j 0.53133811+0.j 0.53815014+0.j]\nPrepared statevector: [0.51090203-5.39381770e-16j 0.40872162+3.55019506e-16j\n0.53133811+5.20577784e-16j 0.53815014-3.96975655e-16j]\nFidelity: 0.9999999999999996\nMax absolute difference: 8.454203028078464e-16\nVerification PASSED: prepared state matches normalized target.'


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

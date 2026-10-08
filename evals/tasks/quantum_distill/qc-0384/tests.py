# Auto-generated from distillation reference (row qc-0384).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Raw amplitudes: [0.36 0.43 0.25 0.99]\nNorm: 1.164946350696031\nNormalized target statevector: [0.30902711 0.36911571 0.21460216 0.84982454]\nPrepared statevector: [0.30902711-9.78677031e-17j 0.36911571-1.25853458e-17j\n0.21460216-4.29295951e-18j 0.84982454+5.85605971e-17j]\nAbsolute difference: [1.48000132e-16 1.25853458e-17 2.80856098e-17 1.25520099e-16]\nMax absolute difference: 1.4800013162196423e-16\nMatch (within 1e-10): True'


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

# Auto-generated from distillation reference (row qc-0304).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Target amplitudes: [0.16, 0.86, 0.67, 0.34, 0.89, 0.65, 0.97, 0.39]\nNormalized target statevector:\n[0.08389391 0.45092975 0.35130574 0.17827455 0.46665986 0.340819\n0.50860681 0.2044914 ]\n\nPrepared statevector:\n[0.08389391-6.19279048e-16j 0.45092975+6.88501986e-17j\n0.35130574-8.09039905e-17j 0.17827455-6.64487098e-16j\n0.46665986-5.45415110e-16j 0.340819 -5.03445017e-16j\n0.50860681+3.97391640e-16j 0.2044914 +2.72181199e-16j]\n\nAbsolute differences:\n[6.23154366e-16 3.94630533e-16 5.06108661e-16 7.43287742e-16\n9.04571224e-16 6.35963673e-16 9.73026732e-16 2.93953324e-16]\n\nMax absolute difference: 9.730267319080159e-16\nState preparation verified: True'


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

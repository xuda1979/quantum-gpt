# Auto-generated from distillation reference (row qc-0789).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Target statevector:\n[0.39196423 0.4713494 0.48127254 0.07938516 0.34234851 0.22327077\n0.10419302 0.45646468]\n\nPrepared statevector:\n[0.39196423-1.48239260e-15j 0.4713494 +2.24820941e-15j\n0.48127254+6.72077340e-17j 0.07938516-1.75850287e-15j\n0.34234851-1.27508813e-15j 0.22327077+1.00211657e-15j\n0.10419302+1.82586475e-15j 0.45646468-3.02250900e-16j]\n\nFidelity: 0.9999999999999998\nMax absolute difference: 2.76513596333184e-15\n\nVerification PASSED: prepared statevector matches the normalized target.'


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

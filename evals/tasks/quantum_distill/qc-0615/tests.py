# Auto-generated from distillation reference (row qc-0615).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '=== QuTiP T1/T2 relaxation & dephasing simulation ===\nInput T1 = 15.0000, T2 = 12.2500\nDerived gamma1 = 0.066667, gamma2_phi = 0.048299, gamma2 = 0.081633\nInitial state |+>: <sx>=1.0000, <sy>=0.0000, <sz>=0.0000\nFit <sigma_x>(t) -> T2_eff = 12.2500 (expected 12.2500)\nFit P_e(t) -> T1_eff = 15.0000 (expected 15.0000)\nFinal <sx>=0.001458, P_e=0.997586\n=== Done ==='


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

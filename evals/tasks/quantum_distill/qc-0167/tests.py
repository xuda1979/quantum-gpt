# Auto-generated from distillation reference (row qc-0167).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '============================================================\nQubit relaxation and dephasing simulation (QuTiP)\n============================================================\nInput parameters:\nT1 = 13.5\nT2 = 11.94\ngamma_1 = 1/T1 = 0.074074\ngamma_2 = 1/T2 = 0.083752\ngamma_phi = 1/T2 - 1/(2*T1) = 0.046715\n\nInitial state: |+> = (|0> + |1>)/sqrt(2)\nTime grid: 1601 points from 0 to 80.0\n\nFitted results:\n<sigma_x>(t) fit: A = 1.000000, T2_eff = 7.664773\npop_e(t) fit: A = 0.083994, T1_eff = 0.001026\n\nComparison with input:\nT1_eff / T1 = 0.000076 (should be ~1.0)\nT2_eff / T2 = 0.641941 (should be ~1.0)\n\nSanity checks:\n<sigma_x>(0) = 1.000000 (should be 1.0)\npop_e(0) = 0.500000 (should be 0.5)\n<sigma_x>(end) = 2.932575e-05 (should be ~0)\npop_e(end) = 0.001335 (should be ~0.5)\n============================================================'


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

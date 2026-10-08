# Auto-generated from distillation reference (row qc-0332).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Raw amplitudes: [0.55, 0.89, 0.94, 0.97, 0.65, 0.12, 0.19, 0.72]\nNorm: 1.9774984197212395\nTarget normalized state: [0.2781291729565738, 0.450063570784274, 0.4753480410530534, 0.49051872321432105, 0.3286981134941327, 0.06068272864507065, 0.09608098702136186, 0.3640963718704239]\nPrepared statevector (real parts): [0.27812917295657424, 0.45006357078427445, 0.4753480410530527, 0.4905187232143203, 0.3286981134941319, 0.0606827286450706, 0.09608098702136195, 0.36409637187042426]\nPrepared statevector (imag parts): [1.1116699851583624e-16, -6.656507391885808e-16, 5.713530337927489e-16, 8.77089639013183e-17, 1.7417679905418041e-16, 2.0785180974650284e-16, -1.8631956771293778e-16, 4.1829604158151434e-17]\nFidelity: 0.9999999999999991\nMax absolute difference: 9.20443233549189e-16\nVERIFICATION PASSED: prepared statevector matches the normalized target.'


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

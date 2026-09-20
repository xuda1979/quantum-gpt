# Auto-generated from distillation reference (row qc-0500).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Target statevector: [0.51928862 0.5299956 0.44969323 0.20343265 0.18201869 0.08565585\n0.39080484 0.11242331]\nPrepared statevector: [0.51928862-8.66121393e-16j 0.5299956 +2.49393081e-16j\n0.44969323-1.83289663e-16j 0.20343265-1.19140223e-16j\n0.18201869+7.76614778e-18j 0.08565585-1.32709705e-16j\n0.39080484+5.50551123e-17j 0.11242331+5.07258428e-17j]\nFidelity: 1.0\nMax absolute difference: 9.279546498128636e-16\nMatch (fidelity > 1e-10): True'


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

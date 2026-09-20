# Auto-generated from distillation reference (row qc-0584).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Optimal parameters (gamma, beta): [0.31997283 0.45567558]\nOptimal expected cost: 2.343992966518838\n\nTop measured bitstrings:\n000000 prob=0.1765 cut=0\n111111 prob=0.1765 cut=0\n011110 prob=0.0442 cut=3\n100001 prob=0.0442 cut=3\n010000 prob=0.0394 cut=2\n101111 prob=0.0394 cut=2\n000001 prob=0.0340 cut=2\n111110 prob=0.0340 cut=2\n011001 prob=0.0286 cut=4\n100110 prob=0.0286 cut=4'


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

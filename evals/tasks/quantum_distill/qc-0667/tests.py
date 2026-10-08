# Auto-generated from distillation reference (row qc-0667).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '6-qubit GHZ circuit built with pytket\nOriginal qubit count: 6\nRe-imported qubit count: 6\nOriginal gate count: 6\nRe-imported gate count: 6\nStatevector dimension (original): 64\nStatevector dimension (re-imported): 64\nRound-trip state fidelity: 1.0000000000000004\nMax element-wise difference (normalized): 0.0\nQASM preview (first 300 chars):\nOPENQASM 2.0;\ninclude "hqslib1.inc";\n\nqreg q[6];\nh q[0];\ncx q[0],q[1];\ncx q[1],q[2];\ncx q[2],q[3];\ncx q[3],q[4];\ncx q[4],q[5];\n\nROUND TRIP PRESERVED: statevectors match.'


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

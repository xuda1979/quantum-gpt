# Auto-generated from distillation reference (row qc-0494).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '=== pytket PauliExpBox exp(-i*1.011*Z@Z) verification ===\nAngle (task): 1.011000\nPauliExpBox parameter (t): 0.643623\n\nDecomposed circuit commands:\nH q[0];\nH q[1];\nCX q[1], q[0];\nRz(0.643623) q[0];\nCX q[1], q[0];\n\npytket statevector: [0.265507-0.423682j 0.265507+0.423682j 0.265507+0.423682j\n0.265507-0.423682j]\nscipy statevector: [0.265507-0.423682j 0.265507+0.423682j 0.265507+0.423682j\n0.265507-0.423682j]\nStatevectors match: True\n\nUnitaries match: True'


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

# Auto-generated from distillation reference (row qc-0178).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Discrete-time quantum walk on a cycle of 8 nodes (8 steps)\nFinal position distribution:\nNode 0: 8192 counts (1.0000) ####################################################################################################\nNode 1: 0 counts (0.0000)\nNode 2: 0 counts (0.0000)\nNode 3: 0 counts (0.0000)\nNode 4: 0 counts (0.0000)\nNode 5: 0 counts (0.0000)\nNode 6: 0 counts (0.0000)\nNode 7: 0 counts (0.0000)'


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

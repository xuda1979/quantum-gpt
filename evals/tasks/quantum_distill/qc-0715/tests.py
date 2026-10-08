# Auto-generated from distillation reference (row qc-0715).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Graph state stabilizer verification\nEdges: [(0, 4), (0, 5), (1, 2), (1, 4), (1, 5), (2, 5), (3, 5)]\n\nK_0 = ZZIIIX -> <K_0> = 1.000000000000 (PASS)\nK_1 = ZZIZXI -> <K_1> = 1.000000000000 (PASS)\nK_2 = ZIIXZI -> <K_2> = 1.000000000000 (PASS)\nK_3 = ZIXIII -> <K_3> = 1.000000000000 (PASS)\nK_4 = IXIIZZ -> <K_4> = 1.000000000000 (PASS)\nK_5 = XIZZZZ -> <K_5> = 1.000000000000 (PASS)\n\nAll stabilizers have expectation +1: True'


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

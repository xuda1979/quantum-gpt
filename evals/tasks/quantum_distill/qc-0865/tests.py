# Auto-generated from distillation reference (row qc-0865).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Cat state (|alpha> + |-alpha>)/norm, alpha=2.13, N=30\nCoarse Wigner grid (11x11), x,y in [-5,5]\nInterference fringes appear near x=0 as alternating +/- Wigner values\n\ny\\x -5.00 -4.00 -3.00 -2.00 -1.00 0.00 1.00 2.00 3.00 4.00 5.00\n-5.00 -0.000 -0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000 -0.000 -0.000\n-4.00 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000\n-3.00 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000\n-2.00 0.000 0.001 0.003 0.001 0.002 0.005 0.002 0.001 0.003 0.001 0.000\n-1.00 0.001 0.022 0.059 0.023 0.043 0.113 0.043 0.023 0.059 0.022 0.001\n0.00 0.003 0.060 0.159 0.063 0.120 0.318 0.120 0.063 0.159 0.060 0.003\n1.00 0.001 0.022 0.059 0.023 0.043 0.113 0.043 0.023 0.059 0.022 0.001\n2.00 0.000 0.001 0.003 0.001 0.002 0.005 0.002 0.001 0.003 0.001 0.000\n3.00 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000\n4.00 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000\n5.00 -0.000 -0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000 -0.000 -0.000\n\nInterference fringe identification (x=0 column):\ny W(0,y)\n-5.00 0.0000\n-4.00 0.0000\n-3.00 0.0000\n-2.00 0.0051\n-1.00 0.1132 <-- fringe\n0.00 0.3183 <-- fringe\n1.00 0.1132 <-- fringe\n2.00 0.0051\n3.00 0.0000\n4.00 0.0000\n5.00 0.0000\n\nFringe sign changes along x=0:\nTotal sign changes: 0'


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

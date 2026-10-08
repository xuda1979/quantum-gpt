# Auto-generated from distillation reference (row qc-0702).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Cat state (|alpha> + |-alpha>)/norm, alpha = 2.05, N = 25\nWigner grid: 21 x 21 (y x x)\n\nCoarse Wigner values W(y, x) (subsampled):\ny\\x -5.00 -4.00 -3.00 -2.00 -1.00 0.00 1.00 2.00 3.00 4.00 5.00\n-5.00 0.000 0.000 -0.000 -0.000 0.000 0.000 0.000 -0.000 -0.000 0.000 0.000\n-4.00 0.000 0.000 -0.000 -0.000 -0.000 -0.000 -0.000 -0.000 -0.000 0.000 0.000\n-3.00 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000\n-2.00 0.000 0.001 0.003 0.001 0.001 0.003 0.001 0.001 0.003 0.001 0.000\n-1.00 0.001 0.017 0.058 0.028 0.040 0.104 0.040 0.028 0.058 0.017 0.001\n0.00 0.002 0.047 0.158 0.077 0.121 0.318 0.121 0.077 0.158 0.047 0.002\n1.00 0.001 0.017 0.058 0.028 0.040 0.104 0.040 0.028 0.058 0.017 0.001\n2.00 0.000 0.001 0.003 0.001 0.001 0.003 0.001 0.001 0.003 0.001 0.000\n3.00 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000 0.000\n4.00 0.000 0.000 -0.000 -0.000 -0.000 -0.000 -0.000 -0.000 -0.000 0.000 0.000\n5.00 0.000 0.000 -0.000 -0.000 0.000 0.000 0.000 -0.000 -0.000 0.000 0.000\n\nInterference fringes along x=0 (sign changes in W(0,y)):\ny=-4.50 W(0,y)= 0.0000\nSign change near y=-4.00\nSign change near y=-3.50\ny=-3.00 W(0,y)= 0.0000\nSign change near y=-2.50\nSign change near y=-2.00\nSign change near y=-1.50\nSign change near y=-1.00\nSign change near y=-0.50\nSign change near y=0.00\nSign change near y=0.50\nSign change near y=1.00\nSign change near y=1.50\nSign change near y=2.00\nSign change near y=2.50\nSign change near y=3.00\ny= 3.50 W(0,y)= 0.0000\nSign change near y=4.00\nSign change near y=4.50\ny= 5.00 W(0,y)= 0.0000\n\nTotal sign changes along x=0: 16\nThese oscillations are the interference fringes of the cat state.\n\nPeak Wigner values at the two coherent-state lobes:\nMax W = 0.3183 at (x=0.00, y=0.00)\nMin W = -0.2405 at (x=0.00, y=-0.50)'


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

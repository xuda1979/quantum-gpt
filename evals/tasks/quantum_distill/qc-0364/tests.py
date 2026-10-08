# Auto-generated from distillation reference (row qc-0364).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '=== Grover Search for |0000> (4 qubits) ===\nQ# algorithm structure (simulated in pure Python/numpy):\n- Oracle: phase flip on |0000> (diagonal matrix with -1 at index 0)\n- Diffusion: within/apply pattern -> 2|s><s| - I\n- Iterations: 3\nShots: 500\nMeasurement counts:\n|0000>: 486\n|0001>: 1\n|0010>: 1\n|0011>: 1\n|0100>: 2\n|0101>: 1\n|0110>: 1\n|1000>: 3\n|1010>: 1\n|1101>: 1\n|1110>: 1\n|1111>: 1\nSuccess rate for |0000>: 0.9720 (486 / 500)\nTheoretical success probability: 0.9613\nRESULT: Grover search for |0000> completed with success rate 0.9720 over 500 shots'


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

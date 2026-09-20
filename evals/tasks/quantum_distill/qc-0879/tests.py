# Auto-generated from distillation reference (row qc-0879).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '5-qubit W state amplitudes for basis states with a single 1:\n|10000> : amplitude = +0.447214+0.000000j, probability = 0.200000\n|01000> : amplitude = +0.447214+0.000000j, probability = 0.200000\n|00100> : amplitude = +0.447214+0.000000j, probability = 0.200000\n|00010> : amplitude = +0.447214+0.000000j, probability = 0.200000\n|00001> : amplitude = +0.447214+0.000000j, probability = 0.200000\n\nSum of probabilities for single-1 states: 1.000000'


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

# Auto-generated from distillation reference (row qc-0557).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '4-qubit W-state amplitudes for basis states with a single 1:\n|0001> : amplitude = 0.000000+0.000000j, probability = 0.000000\n|0010> : amplitude = 0.000000+0.000000j, probability = 0.000000\n|0100> : amplitude = 0.191342+0.000000j, probability = 0.036612\n|1000> : amplitude = 0.000000+0.000000j, probability = 0.000000\n\nFull statevector:\n|0000> : 0.000000+0.000000j\n|0001> : 0.000000+0.000000j\n|0010> : 0.191342+0.000000j\n|0011> : 0.000000+0.000000j\n|0100> : -0.461940+0.000000j\n|0101> : 0.000000+0.000000j\n|0110> : 0.000000+0.000000j\n|0111> : 0.000000+0.000000j\n|1000> : 0.866025+0.000000j\n|1001> : 0.000000+0.000000j\n|1010> : 0.000000+0.000000j\n|1011> : 0.000000+0.000000j\n|1100> : 0.000000+0.000000j\n|1101> : 0.000000+0.000000j\n|1110> : 0.000000+0.000000j\n|1111> : 0.000000+0.000000j'


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

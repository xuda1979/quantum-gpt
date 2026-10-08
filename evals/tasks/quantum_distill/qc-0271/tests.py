# Auto-generated from distillation reference (row qc-0271).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '=== Quantum Teleportation (Pure Python Simulation of Q# Algorithm) ===\nMessage state: Ry(1.043)|0>\nShots: 1000\n\nBell measurement outcomes (m, n) on sender qubits:\nm=0, n=0: 238\nm=0, n=1: 241\nm=1, n=0: 260\nm=1, n=1: 261\n\nReceiver qubit statistics after teleportation + corrections:\n|0> count: 763 (empirical 0.7630, theory 0.7518)\n|1> count: 237 (empirical 0.2370, theory 0.2482)\n\nRESULT: receiver_0=763 receiver_1=237 theory_0=0.751815 theory_1=0.248185'


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

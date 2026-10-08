# Auto-generated from distillation reference (row qc-0816).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = "Number of qubits: 3\nNumber of gates: 16\nNumber of symbols: 12\nSymbols: ['rx_0_0', 'rz_0_0', 'rx_0_1', 'rz_0_1', 'rx_0_2', 'rz_0_2', 'rx_1_0', 'rz_1_0', 'rx_1_1', 'rz_1_1', 'rx_1_2', 'rz_1_2']\nCircuit commands:\nRx(rx_0_0) [q[0]]\nRx(rx_0_1) [q[1]]\nRx(rx_0_2) [q[2]]\nRz(rz_0_0) [q[0]]\nRz(rz_0_1) [q[1]]\nRz(rz_0_2) [q[2]]\nCX [q[0], q[1]]\nRx(rx_1_0) [q[0]]\nCX [q[1], q[2]]\nRz(rz_1_0) [q[0]]\nRx(rx_1_1) [q[1]]\nRx(rx_1_2) [q[2]]\nRz(rz_1_1) [q[1]]\nRz(rz_1_2) [q[2]]\nCX [q[0], q[1]]\nCX [q[1], q[2]]"


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

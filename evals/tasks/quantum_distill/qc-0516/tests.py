# Auto-generated from distillation reference (row qc-0516).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'QASM circuit:\n\nOPENQASM 3.0;\ninclude "stdgates.inc";\n\nqubit[5] q;\nqubit[1] ancilla;\nbit[5] c;\n\n// Prepare ancilla in |-> state\nx ancilla[0];\nh ancilla[0];\n\n// Apply Hadamard to input register\nh q[0];\nh q[1];\nh q[2];\nh q[3];\nh q[4];\n\n// Oracle: cx from each qubit to ancilla where hidden bit is 1\ncx q[0], ancilla[0];\ncx q[2], ancilla[0];\ncx q[4], ancilla[0];\n\n// Apply Hadamard to input register again\nh q[0];\nh q[1];\nh q[2];\nh q[3];\nh q[4];\n\n// Measure\nc[0] = measure q[0];\nc[1] = measure q[1];\nc[2] = measure q[2];\nc[3] = measure q[3];\nc[4] = measure q[4];\n\nHidden string: 10101\nMeasured counts: {\'10101\': 1024}\nRecovered string: 10101\nMatch: True'


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

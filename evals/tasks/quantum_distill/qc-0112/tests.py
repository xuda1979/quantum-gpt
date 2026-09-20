# Auto-generated from distillation reference (row qc-0112).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '=== OpenQASM 2 ===\nOPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[4];\nh q[0];\ncp(pi/2) q[1],q[0];\ncp(pi/4) q[2],q[0];\ncp(pi/8) q[3],q[0];\nbarrier q[0],q[1],q[2],q[3];\nh q[1];\ncp(pi/2) q[2],q[1];\ncp(pi/4) q[3],q[1];\nbarrier q[0],q[1],q[2],q[3];\nh q[2];\ncp(pi/2) q[3],q[2];\nbarrier q[0],q[1],q[2],q[3];\nh q[3];\nbarrier q[0],q[1],q[2],q[3];\nswap q[0],q[3];\nswap q[1],q[2];\n\n=== OpenQASM 3 ===\nOPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[4] q;\nh q[0];\ncp(pi/2) q[1], q[0];\ncp(pi/4) q[2], q[0];\ncp(pi/8) q[3], q[0];\nbarrier q[0], q[1], q[2], q[3];\nh q[1];\ncp(pi/2) q[2], q[1];\ncp(pi/4) q[3], q[1];\nbarrier q[0], q[1], q[2], q[3];\nh q[2];\ncp(pi/2) q[3], q[2];\nbarrier q[0], q[1], q[2], q[3];\nh q[3];\nbarrier q[0], q[1], q[2], q[3];\nswap q[0], q[3];\nswap q[1], q[2];\n\n\nVerification: SUCCESS - The re-imported QASM 3 circuit is operator-equivalent to the original.'


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

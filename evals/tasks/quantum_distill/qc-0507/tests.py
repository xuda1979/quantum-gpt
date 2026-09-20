# Auto-generated from distillation reference (row qc-0507).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Original circuit:\n[H q[0];, CX q[0], q[1];, CX q[1], q[2];, CX q[2], q[3];]\n\nOpenQASM 2 export:\nOPENQASM 2.0;\ninclude "hqslib1.inc";\n\nqreg q[4];\nh q[0];\ncx q[0],q[1];\ncx q[1],q[2];\ncx q[2],q[3];\n\nRe-imported circuit:\n[H q[0];, CX q[0], q[1];, CX q[1], q[2];, CX q[2], q[3];]\n\nStatevector fidelity (round trip): 1.0\nRound trip preserves statevector: True'


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

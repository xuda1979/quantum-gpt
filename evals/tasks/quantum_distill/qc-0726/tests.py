# Auto-generated from distillation reference (row qc-0726).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Step 10 | Energy: -0.54497463 | Params: [0.3961 0.7963 1.4531 0.057 ]\nStep 20 | Energy: -1.79871842 | Params: [ 0.6049 0.6315 2.5719 -0.7088]\nStep 30 | Energy: -1.84229429 | Params: [ 0.4948 0.7353 2.7511 -0.7917]\nStep 40 | Energy: -1.84878617 | Params: [ 0.4257 0.7777 2.8124 -0.8206]\nStep 50 | Energy: -1.85045525 | Params: [ 0.3893 0.7978 2.8442 -0.8346]\nStep 60 | Energy: -1.85095471 | Params: [ 0.3692 0.8083 2.862 -0.8421]\nStep 70 | Energy: -1.85111603 | Params: [ 0.3577 0.8142 2.8723 -0.8462]\nStep 80 | Energy: -1.85117033 | Params: [ 0.3509 0.8176 2.8783 -0.8485]\nStep 90 | Energy: -1.85118903 | Params: [ 0.347 0.8195 2.8818 -0.8499]\nStep 100 | Energy: -1.85119557 | Params: [ 0.3447 0.8207 2.8839 -0.8507]\n\nFinal VQE energy after 100 steps: -1.85119592\nExact ground state energy: -1.85119912\nAbsolute error: 0.00000321'


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

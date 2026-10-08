# Auto-generated from distillation reference (row qc-0904).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Starting VQE optimization...\nInitial parameters: [0.1 0.1 0.1 0.1]\nInitial energy: -0.004791 Ha\n--------------------------------------------------\nStep 10 | Energy: -0.074698 Ha\nStep 20 | Energy: -1.106516 Ha\nStep 30 | Energy: -1.829526 Ha\nStep 40 | Energy: -1.850567 Ha\nStep 50 | Energy: -1.851167 Ha\nStep 60 | Energy: -1.851197 Ha\nStep 70 | Energy: -1.851199 Ha\nStep 80 | Energy: -1.851199 Ha\nStep 90 | Energy: -1.851199 Ha\nStep 100 | Energy: -1.851199 Ha\n--------------------------------------------------\nFinal VQE Energy: -1.851199 Ha\nExact Ground State: -1.851199 Ha\nAbsolute Error: 0.000000 Ha'


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

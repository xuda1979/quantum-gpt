# Auto-generated from distillation reference (row qc-0204).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '=== QAOA MaxCut (p=1) ===\nEdges: [(0, 1), (0, 2), (0, 5), (1, 2), (1, 4), (1, 5), (3, 5), (4, 5)]\nOptimal gamma: 0.277297\nOptimal beta: 2.838034\nMaxCut expectation: 4.803870\n\nMeasurement outcomes (probabilities):\n000000 : 0.002477 (cut=0)\n000001 : 0.000217 (cut=4)\n000010 : 0.003521 (cut=2)\n000011 : 0.024589 (cut=4)\n000100 : 0.001787 (cut=1)\n000101 : 0.002306 (cut=3)\n000110 : 0.007746 (cut=3)\n000111 : 0.005142 (cut=3)\n001000 : 0.002977 (cut=2)\n001001 : 0.002962 (cut=6)\n001010 : 0.017758 (cut=4)\n001011 : 0.053423 (cut=6)\n001100 : 0.000086 (cut=3)\n001101 : 0.012045 (cut=5)\n001110 : 0.031189 (cut=5)\n001111 : 0.007746 (cut=5)\n010000 : 0.000735 (cut=4)\n010001 : 0.019514 (cut=6)\n010010 : 0.011586 (cut=4)\n010011 : 0.024355 (cut=4)\n010100 : 0.004636 (cut=5)\n010101 : 0.024355 (cut=5)\n010110 : 0.016567 (cut=5)\n010111 : 0.000884 (cut=3)\n011000 : 0.000152 (cut=4)\n011001 : 0.044624 (cut=6)\n011010 : 0.024355 (cut=4)\n011011 : 0.040326 (cut=4)\n011100 : 0.024355 (cut=5)\n011101 : 0.054547 (cut=5)\n011110 : 0.031460 (cut=5)\n011111 : 0.001579 (cut=3)\n100000 : 0.001579 (cut=3)\n100001 : 0.031460 (cut=5)\n100010 : 0.054547 (cut=5)\n100011 : 0.024355 (cut=5)\n100100 : 0.040326 (cut=4)\n100101 : 0.024355 (cut=4)\n100110 : 0.044624 (cut=6)\n100111 : 0.000152 (cut=4)\n101000 : 0.000884 (cut=3)\n101001 : 0.016567 (cut=5)\n101010 : 0.024355 (cut=5)\n101011 : 0.004636 (cut=5)\n101100 : 0.024355 (cut=4)\n101101 : 0.011586 (cut=4)\n101110 : 0.019514 (cut=6)\n101111 : 0.000735 (cut=4)\n110000 : 0.007746 (cut=5)\n110001 : 0.031189 (cut=5)\n110010 : 0.012045 (cut=5)\n110011 : 0.000086 (cut=3)\n110100 : 0.053423 (cut=6)\n110101 : 0.017758 (cut=4)\n110110 : 0.002962 (cut=6)\n110111 : 0.002977 (cut=2)\n111000 : 0.005142 (cut=3)\n111001 : 0.007746 (cut=3)\n111010 : 0.002306 (cut=3)\n111011 : 0.001787 (cut=1)\n111100 : 0.024589 (cut=4)\n111101 : 0.003521 (cut=2)\n111110 : 0.000217 (cut=4)\n111111 : 0.002477 (cut=0)\n\nMost likely bitstring: 011101\nCut value: 5'


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

# Auto-generated from distillation reference (row qc-0291).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Kernel matrix K:\n[[1.00000000e+00 3.21955362e-04 7.11016711e-02 1.89750613e-02\n1.88235627e-05]\n[3.21955362e-04 1.00000000e+00 9.25323525e-09 2.38533608e-02\n1.26779835e-02]\n[7.11016711e-02 9.25323525e-09 1.00000000e+00 2.68626198e-02\n5.24875156e-06]\n[1.89750613e-02 2.38533608e-02 2.68626198e-02 1.00000000e+00\n7.50299693e-02]\n[1.88235627e-05 1.26779835e-02 5.24875156e-06 7.50299693e-02\n1.00000000e+00]]\n\nSymmetric check (max |K - K.T|): 8.326672684688674e-17\nUnit diagonal check (max |diag(K) - 1|): 8.881784197001252e-16'


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

# Auto-generated from distillation reference (row qc-0840).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'iter GD_energy QNG_energy\n1 1.986601 1.986601\n2 1.984180 1.975691\n3 1.981297 1.955395\n4 1.977863 1.917609\n5 1.973770 1.847725\n6 1.968891 1.720727\n7 1.963074 1.497910\n8 1.956139 1.130919\n9 1.947875 0.586613\n10 1.938029 -0.102119\n11 1.926308 -0.804068\n12 1.912369 -1.355627\n13 1.895811 -1.691317\n14 1.876174 -1.861312\n15 1.852931 -1.939275\n16 1.825486 -1.973491\n17 1.793171 -1.988294\n18 1.755252 -1.994715\n19 1.710937 -1.997537\n20 1.659390 -1.998806\n21 1.599756 -1.999394\n22 1.531197 -1.999678\n23 1.452935 -1.999821\n24 1.364304 -1.999896\n25 1.264817 -1.999938\n26 1.154225 -1.999962\n27 1.032574 -1.999976\n28 0.900257 -1.999985\n29 0.758034 -1.999990\n30 0.607033 -1.999994\n31 0.448725 -1.999996\n32 0.284867 -1.999997\n33 0.117435 -1.999998\n34 -0.051465 -1.999999\n35 -0.219681 -1.999999\n36 -0.385097 -2.000000\n37 -0.545722 -2.000000\n38 -0.699752 -2.000000\n39 -0.845640 -2.000000\n40 -0.982145 -2.000000'


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

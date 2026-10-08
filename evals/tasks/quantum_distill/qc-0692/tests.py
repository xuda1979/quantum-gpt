# Auto-generated from distillation reference (row qc-0692).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Iter | GD Energy | QNG Energy\n------------------------------------------\n1 | 1.396735 | 1.396735\n2 | 1.243160 | 1.040166\n3 | 1.065717 | 0.528089\n4 | 0.867640 | -0.095189\n5 | 0.653576 | -0.725954\n6 | 0.428002 | -1.265841\n7 | 0.193680 | -1.642231\n8 | -0.048742 | -1.847172\n9 | -0.299349 | -1.938410\n10 | -0.556278 | -1.974958\n11 | -0.813276 | -1.989210\n12 | -1.059439 | -1.994902\n13 | -1.281957 | -1.997322\n14 | -1.470535 | -1.998449\n15 | -1.620638 | -1.999034\n16 | -1.733788 | -1.999369\n17 | -1.815506 | -1.999577\n18 | -1.872735 | -1.999712\n19 | -1.912021 | -1.999802\n20 | -1.938690 | -1.999864\n21 | -1.956721 | -1.999906\n22 | -1.968933 | -1.999935\n23 | -1.977257 | -1.999955\n24 | -1.982992 | -1.999969\n25 | -1.987000 | -1.999978\n26 | -1.989852 | -1.999985\n27 | -1.991922 | -1.999990\n28 | -1.993457 | -1.999993\n29 | -1.994622 | -1.999995\n30 | -1.995525 | -1.999997\n31 | -1.996240 | -1.999998\n32 | -1.996816 | -1.999998\n33 | -1.997287 | -1.999999\n34 | -1.997678 | -1.999999\n35 | -1.998006 | -1.999999\n36 | -1.998283 | -2.000000\n37 | -1.998519 | -2.000000\n38 | -1.998720 | -2.000000\n39 | -1.998893 | -2.000000\n40 | -1.999042 | -2.000000\n------------------------------------------\nFinal GD energy : -1.999170\nFinal QNG energy: -2.000000'


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

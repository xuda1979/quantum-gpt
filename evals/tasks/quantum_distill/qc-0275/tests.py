# Auto-generated from distillation reference (row qc-0275).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'iter GD_energy QNG_energy\n1 1.763333 1.801376\n2 1.683856 1.776065\n3 1.581787 1.747698\n4 1.454499 1.716000\n5 1.301775 1.680703\n6 1.127217 1.641557\n7 0.938946 1.598349\n8 0.748671 1.550913\n9 0.568906 1.499157\n10 0.409417 1.443077\n11 0.274733 1.382779\n12 0.163813 1.318496\n13 0.071445 1.250599\n14 -0.009864 1.179596\n15 -0.088422 1.106134\n16 -0.172518 1.030974\n17 -0.269908 0.954968\n18 -0.387203 0.879016\n19 -0.528810 0.804031\n20 -0.695390 0.730889\n21 -0.882369 0.660387\n22 -1.079568 0.593212\n23 -1.273017 0.529915\n24 -1.448807 0.470901\n25 -1.597126 0.416422\n26 -1.714245 0.366592\n27 -1.801809 0.321400\n28 -1.864589 0.280730\n29 -1.908270 0.244385\n30 -1.938059 0.212108\n31 -1.958128 0.183604\n32 -1.971565 0.158557\n33 -1.980544 0.136642\n34 -1.986555 0.117543\n35 -1.990598 0.100951\n36 -1.993335 0.086580\n37 -1.995205 0.074163\n38 -1.996497 0.063457\n39 -1.997402 0.054244\n40 -1.998043 0.046326'


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

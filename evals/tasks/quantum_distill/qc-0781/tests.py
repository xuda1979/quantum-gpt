# Auto-generated from distillation reference (row qc-0781).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Iter | GD Energy | QNG Energy\n----------------------------------------\n0 | 1.105978 | 1.105978\n1 | 0.791352 | 0.953682\n2 | 0.412859 | 0.781191\n3 | -0.008896 | 0.589103\n4 | -0.438234 | 0.379651\n5 | -0.834486 | 0.156983\n6 | -1.166534 | -0.072929\n7 | -1.421982 | -0.302863\n8 | -1.605737 | -0.525351\n9 | -1.731994 | -0.733830\n10 | -1.816537 | -0.923529\n11 | -1.872624 | -1.091834\n12 | -1.909945 | -1.238128\n13 | -1.935063 | -1.363298\n14 | -1.952256 | -1.469167\n15 | -1.964258 | -1.557993\n16 | -1.972813 | -1.632129\n17 | -1.979037 | -1.693803\n18 | -1.983651 | -1.745020\n19 | -1.987131 | -1.787524\n20 | -1.989794 | -1.822796\n21 | -1.991859 | -1.852080\n22 | -1.993475 | -1.876410\n23 | -1.994752 | -1.896644\n24 | -1.995767 | -1.913486\n25 | -1.996578 | -1.927522\n26 | -1.997229 | -1.939229\n27 | -1.997753 | -1.949005\n28 | -1.998176 | -1.957176\n29 | -1.998519 | -1.964012\n30 | -1.998796 | -1.969736\n31 | -1.999021 | -1.974533\n32 | -1.999204 | -1.978556\n33 | -1.999352 | -1.981932\n34 | -1.999473 | -1.984768\n35 | -1.999571 | -1.987151\n36 | -1.999651 | -1.989156\n37 | -1.999716 | -1.990842\n38 | -1.999768 | -1.992262\n39 | -1.999811 | -1.993459\n40 | -1.999846 | -1.994467\n41 | -1.999875 | -1.995317\n42 | -1.999898 | -1.996035\n43 | -1.999917 | -1.996640\n44 | -1.999932 | -1.997152\n45 | -1.999945 | -1.997584\n46 | -1.999955 | -1.997949\n47 | -1.999964 | -1.998258\n48 | -1.999970 | -1.998519\n49 | -1.999976 | -1.998740\n50 | -1.999980 | -1.998928'


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

# Auto-generated from distillation reference (row qc-0161).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'iter | GD energy | QNG energy\n----------------------------------------\n0 | 1.39673497 | 1.39673497\n1 | 1.24316029 | 1.33096073\n2 | 1.06571650 | 1.25832608\n3 | 0.86764044 | 1.17849754\n4 | 0.65357650 | 1.09125397\n5 | 0.42800187 | 0.99651656\n6 | 0.19367950 | 0.89437394\n7 | -0.04874190 | 0.78509840\n8 | -0.29934924 | 0.66915049\n9 | -0.55627764 | 0.54717062\n10 | -0.81327615 | 0.41995892\n11 | -1.05943882 | 0.28844674\n12 | -1.28195731 | 0.15366478\n13 | -1.47053485 | 0.01671256\n14 | -1.62063762 | -0.12126751\n15 | -1.73378771 | -0.25911089\n16 | -1.81550611 | -0.39564837\n17 | -1.87273543 | -0.52972392\n18 | -1.91202070 | -0.66021615\n19 | -1.93868966 | -0.78606538\n20 | -1.95672090 | -0.90630564\n21 | -1.96893256 | -1.02009845\n22 | -1.97725669 | -1.12676395\n23 | -1.98299175 | -1.22580442\n24 | -1.98700032 | -1.31691681\n25 | -1.98985192 | -1.39999222\n26 | -1.99192175 | -1.47510323\n27 | -1.99345722 | -1.54248105\n28 | -1.99462204 | -1.60248610\n29 | -1.99552521 | -1.65557560\n30 | -1.99623992 | -1.70227146\n31 | -1.99681588 | -1.74313095\n32 | -1.99728736 | -1.77872185\n33 | -1.99767837 | -1.80960258\n34 | -1.99800609 | -1.83630754\n35 | -1.99828307 | -1.85933707\n36 | -1.99851869 | -1.87915137\n37 | -1.99872012 | -1.89616769\n38 | -1.99889297 | -1.91075980\n39 | -1.99904173 | -1.92325926'


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

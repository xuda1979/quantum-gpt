# Auto-generated from distillation reference (row qc-0773).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = '=== Qubit relaxation & dephasing simulation (QuTiP) ===\nInput T1 = 13.2 | Input T2 = 23.11 | Derived Tphi = 185.441945\nInitial state |+> = (|0> + |1>)/sqrt(2)\n\nFitted results:\nEffective T1 from excited-state population fit : 3.652834\nEffective T2 from <sigma_x>(t) fit : 3.652599\n\nFit parameters:\n<sigma_x>(t) ~ A*exp(-t/T2) + off -> A=0.365097, T2=3.652599, off=0.730131\nP_e(t) ~ Pinf + (P0-Pinf)*exp(-t/T1) -> P0=0.602076, T1=3.652834, Pinf=0.210691\n\nSample values:\nt= 0.000 <sx>=+1.000000 <sy>=+0.000000 <sz>=+0.000000 P_e=0.500000\nt= 20.013 <sx>=+0.643527 <sy>=-0.041414 <sz>=-0.764303 P_e=0.117849\nt= 40.025 <sx>=+0.945472 <sy>=+0.303998 <sz>=-0.116912 P_e=0.441544\nt= 60.038 <sx>=+0.650685 <sy>=-0.125202 <sz>=-0.748955 P_e=0.125522\nt= 80.000 <sx>=+0.841067 <sy>=+0.420104 <sz>=-0.340763 P_e=0.329619'


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

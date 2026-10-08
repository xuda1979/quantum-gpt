# Auto-generated from distillation reference (row qc-0874).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = 'Quantum Circuit:\n┌───┐┌───────────┐ ┌──────────┐\nq_0: ┤ X ├┤ Ry(-2π/3) ├─■───┤ Ry(2π/3) ├─────────────────────────────────X────\n└───┘└───────────┘ │ ┌─┴──────────┴┐ ┌────────────┐ │\nq_1: ───────────────────■─┤ Ry(-1.9106) ├─■─┤ Ry(1.9106) ├───────────────┼──X─\n└─────────────┘ │ └┬──────────┬┘ ┌─────────┐ │ │\nq_2: ─────────────────────────────────────■──┤ Ry(-π/2) ├──■─┤ Ry(π/2) ├─┼──X─\n└──────────┘ │ └─────────┘ │\nq_3: ──────────────────────────────────────────────────────■─────────────X────\n\n\nStatevector amplitudes:\n|0000> : (1.4874168143337463e-17+0j)\n|0001> : 0j\n|0010> : (-3.2653358540512865e-34+0j)\n|0011> : 0j\n|0100> : (5.110680247058061e-34+0j)\n|0101> : 0j\n|0110> : (-6.499518184884577e-51+0j)\n|0111> : 0j\n|1000> : (1+0j)\n|1001> : 0j\n|1010> : (1.0146536357569526e-17+0j)\n|1011> : 0j\n|1100> : (2.153145695343714e-17+0j)\n|1101> : 0j\n|1110> : (1.1295909578435871e-33+0j)\n|1111> : 0j\n\nFidelity with ideal W state: 0.25\nAmplitudes match ideal W state: False'


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

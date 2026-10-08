# Auto-generated from distillation reference (row qc-0679).
# run_tests executes the candidate as a standalone script and compares
# normalized stdout against the verified reference output.
import subprocess
import sys

EXPECTED = "[JobShopQAOA] Initializing QAOA for 5-Job Job-Shop...\n[JobShopQAOA] Qubits: 10, Depth (p): 2\n[JobShopQAOA] CPU Simulator acquired: AerSimulator('aer_simulator_statevector')\n[JobShopQAOA] Baseline Expected Cost: 14.7375\n\n--- QAOA Intermediate Plan Result ---\nstatus: intermediate_plan_built\nnum_qubits: 10\nbaseline_cost: 14.73746806706881\ncircuit_depth: 33\nnpu_boundary: Strictly CPU (Statevector/Aer-CPU)"


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

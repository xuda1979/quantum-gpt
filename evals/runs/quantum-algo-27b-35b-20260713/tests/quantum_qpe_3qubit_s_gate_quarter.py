import os, subprocess, sys
def run_tests(workspace_root: str) -> dict:
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-27b-35b-20260713", "reference", "quantum_qpe_3qubit_s_gate_quarter.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=60)
    expected = ['Counting qubits = 3', 'Phase estimate = 0.2500', 'Exact phase = 0.2500', 'Correct: True']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

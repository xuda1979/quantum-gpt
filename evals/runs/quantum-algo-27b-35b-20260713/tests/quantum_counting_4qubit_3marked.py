import os, subprocess, sys
def run_tests(workspace_root: str) -> dict:
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-27b-35b-20260713", "reference", "quantum_counting_4qubit_3marked.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=180)
    expected = ['N = 16', 'True M = 3', 'Counting qubits = 4', 'Estimated M = ', 'Rounded M = 3', 'Correct: True']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

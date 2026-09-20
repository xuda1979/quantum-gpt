import os, subprocess, sys
def run_tests(workspace_root: str) -> dict:
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-27b-35b-20260713", "reference", "quantum_graph_state_path5.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=60)
    expected = ['Graph state: 5 qubits, path graph', 'All stabilizers +1: True', 'Single-qubit purity = 0.5000', 'Entangled: True', 'Valid graph state: True']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

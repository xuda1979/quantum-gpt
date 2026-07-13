def run_tests(workspace_root: str) -> dict:
    import os
    import subprocess
    import sys
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-22q-20260711", "reference", "quantum_graph_state_5qubit_path.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=240)
    expected = ['stab_eigenvalue = 5', 'graph_state: True']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

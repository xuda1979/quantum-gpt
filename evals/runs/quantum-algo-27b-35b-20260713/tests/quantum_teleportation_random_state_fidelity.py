import os, subprocess, sys
def run_tests(workspace_root: str) -> dict:
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-27b-35b-20260713", "reference", "quantum_teleportation_random_state_fidelity.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=120)
    expected = ['Teleported state: random pure 1-qubit', 'Average fidelity = 1.0000', 'Classical limit = 0.6667', 'Beats classical: True', 'Perfect teleport: True']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

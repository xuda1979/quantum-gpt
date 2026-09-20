import os, subprocess, sys
def run_tests(workspace_root: str) -> dict:
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-27b-35b-20260713", "reference", "quantum_random_walk_cycle4_2step.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=60)
    expected = ['Cycle nodes = 4', 'Steps = 2', 'Quantum total = 1.0000', 'TVD vs classical = ', 'Different from classical: True']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

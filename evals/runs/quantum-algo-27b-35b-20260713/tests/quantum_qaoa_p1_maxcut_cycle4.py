import os, subprocess, sys
def run_tests(workspace_root: str) -> dict:
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-27b-35b-20260713", "reference", "quantum_qaoa_p1_maxcut_cycle4.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=180)
    expected = ['QAOA max-cut value = ', 'Optimal max-cut = 4', 'Approx ratio = ', 'Converged: True']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

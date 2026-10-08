import os, subprocess, sys
def run_tests(workspace_root: str) -> dict:
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-27b-35b-20260713", "reference", "quantum_shor_n15_a7_qpe_order.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=180)
    expected = ['a = 7', 'N = 15', 'Measured order r = ', 'Valid order: True', 'Factor found: 3']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

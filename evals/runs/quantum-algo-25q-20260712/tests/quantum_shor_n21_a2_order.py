def run_tests(workspace_root: str) -> dict:
    import os
    import subprocess
    import sys
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-25q-20260712", "reference", "quantum_shor_n21_a2_order.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=300)
    expected = ['order r = 6', 'factors = 3,7']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

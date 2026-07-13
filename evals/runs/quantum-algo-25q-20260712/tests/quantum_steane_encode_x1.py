def run_tests(workspace_root: str) -> dict:
    import os
    import subprocess
    import sys
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-25q-20260712", "reference", "quantum_steane_encode_x1.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=240)
    expected = ['Z_L eigenvalue: -1.000', 'encoded: True']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

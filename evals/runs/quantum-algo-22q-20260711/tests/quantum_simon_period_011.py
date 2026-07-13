def run_tests(workspace_root: str) -> dict:
    import os
    import subprocess
    import sys
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-22q-20260711", "reference", "quantum_simon_period_011.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=240)
    expected = ['period = 011']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

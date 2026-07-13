def run_tests(workspace_root: str) -> dict:
    import os
    import subprocess
    import sys
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-22q-20260711", "reference", "quantum_steane_xerror_syndrome.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=240)
    expected = ['syndrome = 001', 'error_qubit = 3']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

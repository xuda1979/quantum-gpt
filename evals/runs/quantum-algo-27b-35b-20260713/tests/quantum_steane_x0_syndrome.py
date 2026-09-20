import os, subprocess, sys
def run_tests(workspace_root: str) -> dict:
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-27b-35b-20260713", "reference", "quantum_steane_x0_syndrome.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=120)
    expected = ['Steane [[7,1,3]] code', 'Logical state = |1>_L', 'Error = X on qubit 0', 'Decoded error qubit = 0', 'Correct: True']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

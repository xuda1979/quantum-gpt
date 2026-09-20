import os, subprocess, sys
def run_tests(workspace_root: str) -> dict:
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-27b-35b-20260713", "reference", "quantum_kernel_zz_featuremap_2d.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=120)
    expected = ['Training points = 4', 'Feature dim = 2', 'Kernel diagonal = [1.0, 1.0, 1.0, 1.0]', 'Test predictions = [1, -1]', 'Test accuracy = 1.0000', 'Correct: True']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

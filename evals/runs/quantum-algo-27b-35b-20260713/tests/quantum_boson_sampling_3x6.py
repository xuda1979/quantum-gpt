import os, subprocess, sys
def run_tests(workspace_root: str) -> dict:
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-27b-35b-20260713", "reference", "quantum_boson_sampling_3x6.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=120)
    expected = ['Boson sampling: 3 photons in 6 modes', 'Input modes = [0, 1, 2]', 'Collision-free outputs = 20', 'Sum of collision-free probs = ', 'Most likely output = ', 'Valid: True']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

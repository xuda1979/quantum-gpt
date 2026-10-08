import os, subprocess, sys
def run_tests(workspace_root: str) -> dict:
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-27b-35b-20260713", "reference", "quantum_simon_period_011.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=120)
    expected = ['n = 3', 'Hidden period s = 011', 'Recovered s = 011', 'Non-trivial: True', 'Correct: True']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

def run_tests(workspace_root: str) -> dict:
    import os
    import subprocess
    import sys
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-25q-20260712", "reference", "quantum_amplitude_damping_channel.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=120)
    expected = ['gamma = 0.3', 'P(0) = 0.300', 'P(1) = 0.700', 'trace_preserving: True', 'correct: True']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

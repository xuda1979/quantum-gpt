import re


def run_tests(workspace_root: str) -> dict:
    import os
    import subprocess
    import sys
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-25q-20260712", "reference", "quantum_phase_kickback_cnot.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=240)
    expected = ['P(control=1) = ', 'kickback: True']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    if ok:
        m = re.search(r'P\(control=1\) = ([\d.]+)', out.stdout)
        if m:
            v = float(m.group(1))
            if v < 0.9:
                return {"pass": False, "detail": f"P(control=1) too low: {v}"}
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

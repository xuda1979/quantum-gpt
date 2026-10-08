import re


def run_tests(workspace_root: str) -> dict:
    import os
    import subprocess
    import sys
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-25q-20260712", "reference", "quantum_teleportation_across_network.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=240)
    expected = ['fidelity = ', 'teleported: True']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    if ok:
        m = re.search(r'fidelity = ([\d.]+)', out.stdout)
        if m:
            v = float(m.group(1))
            if v < 0.95:
                return {"pass": False, "detail": f"fidelity too low: {v}"}
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

import re


def run_tests(workspace_root: str) -> dict:
    import os
    import subprocess
    import sys
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-25q-20260712", "reference", "quantum_grover_4qubit_marked_1101.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=240)
    expected = ['Top measurement: 1101', 'Iterations: 3']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    if ok:
        m = re.search(r'P\(marked=1101\) = ([\d.]+)', out.stdout)
        if m:
            v = float(m.group(1))
            if v < 0.9:
                return {"pass": False, "detail": f"P(marked) too low: {v}"}
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

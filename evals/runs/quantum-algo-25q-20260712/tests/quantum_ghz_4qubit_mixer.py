import re


def run_tests(workspace_root: str) -> dict:
    import os
    import subprocess
    import sys
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-25q-20260712", "reference", "quantum_ghz_4qubit_mixer.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=240)
    expected = ['P(0000) = ', 'P(1111) = ', 'P(GHZ) = ']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    if ok:
        m = re.search(r'P\(GHZ\) = ([\d.]+)', out.stdout)
        if m:
            v = float(m.group(1))
            if v < 0.99:
                return {"pass": False, "detail": f"P(GHZ) too low: {v}"}
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

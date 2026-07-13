import re


def run_tests(workspace_root: str) -> dict:
    import os
    import subprocess
    import sys
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-22q-20260711", "reference", "quantum_chsh_violation.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=240)
    expected = ['S = ', 'violation: True']
    _ranges = []
    _ranges.append(('S = ([\\d.]+)', 2.5, 3.0))
    for pat, lo, hi in _ranges:
        m = re.search(pat, out.stdout)
        if m:
            try:
                val = float(m.group(1))
                if not (lo <= val <= hi):
                    return {"pass": False, "detail": f"numeric check failed: {pat} got {val} not in [{lo},{hi}]"}
            except ValueError:
                pass

    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

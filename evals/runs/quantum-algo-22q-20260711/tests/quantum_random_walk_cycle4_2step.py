import re


def run_tests(workspace_root: str) -> dict:
    import os
    import subprocess
    import sys
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-22q-20260711", "reference", "quantum_random_walk_cycle4_2step.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=240)
    expected = ['P(node=0) = ', 'P(node=2) = ']
    _ranges = []
    _ranges.append(('P\\(node=0\\) = ([\\d.]+)', 0.45, 0.55))
    _ranges.append(('P\\(node=2\\) = ([\\d.]+)', 0.45, 0.55))
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

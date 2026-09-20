import os, subprocess, sys
def run_tests(workspace_root: str) -> dict:
    ref = os.path.join(workspace_root, "evals", "runs", "quantum-algo-27b-35b-20260713", "reference", "quantum_chsh_game_win_probability.py")
    out = subprocess.run([sys.executable, ref], capture_output=True, text=True, timeout=60)
    expected = ['CHSH quantum win prob = 0.8536', 'Classical best = 0.7500', 'Tsirelson S = 2.8284', 'Tsirelson bound = 2.8284', 'Saturates Tsirelson: True', 'Beats classical: True']
    ok = out.returncode == 0 and all(s in out.stdout for s in expected)
    return {"pass": bool(ok), "detail": out.stdout[-500:] + out.stderr[-300:]}

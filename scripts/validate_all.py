"""Final validation: for every *_case.md, (1) extract the python code block and
run it, (2) run render-rule checks on the markdown. Reports any failures."""

import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qcase_gen import core

OUT_DIR = os.path.join(core.ROOT, "模版与数据", "生成的数据")
PYEXE = sys.executable
ENV = dict(os.environ)
ENV.update(
    {
        k: "1"
        for k in [
            "OMP_NUM_THREADS",
            "OPENBLAS_NUM_THREADS",
            "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS",
            "VECLIB_MAXIMUM_THREADS",
            "RAYON_NUM_THREADS",
        ]
    }
)


def extract_code(md):
    m = re.search(r"```python\n(.*?)```", md, re.S)
    return m.group(1) if m else None


def main():
    files = sorted(f for f in os.listdir(OUT_DIR) if f.endswith("_case.md"))
    run_fail, render_fail, ok = [], [], 0
    for f in files:
        path = os.path.join(OUT_DIR, f)
        md = open(path, encoding="utf-8").read()
        rerrs = core.check_render(md)
        if rerrs:
            render_fail.append((f, rerrs))
        code = extract_code(md)
        if not code:
            run_fail.append((f, "no code block"))
            continue
        tmp = "/tmp/qcase_validate.py"
        open(tmp, "w").write(code)
        try:
            p = subprocess.run([PYEXE, tmp], capture_output=True, text=True, timeout=300, env=ENV)
            if p.returncode != 0:
                run_fail.append((f, p.stderr[-200:]))
            else:
                ok += 1
        except subprocess.TimeoutExpired:
            run_fail.append((f, "TIMEOUT"))
        print(
            f"checked {f}: run={'OK' if (not run_fail or run_fail[-1][0]!=f) else 'FAIL'} render={'OK' if not rerrs else rerrs}",
            flush=True,
        )

    print("\n===== SUMMARY =====")
    print(f"total files: {len(files)}  run_ok: {ok}")
    print(f"run failures ({len(run_fail)}):")
    for f, e in run_fail:
        print(f"  {f}: {e}")
    print(f"render failures ({len(render_fail)}):")
    for f, e in render_fail:
        print(f"  {f}: {e}")


if __name__ == "__main__":
    main()

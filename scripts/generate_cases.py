"""Main driver: generate, verify, and write quantum SFT cases.

For each catalog entry:
  1. build spec (narrative + runnable code)
  2. execute code -> RESULT_JSON (verified numbers)
  3. enforce acceptance criteria per family
  4. inject verified numbers, render Markdown
  5. run render-rule checks
  6. write <fname>_case.md and append to manifest

Usage: python scripts/generate_cases.py [N]
"""

import json
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qcase_gen import core
from qcase_gen.catalog import build_catalog

OUT_DIR = os.path.join(core.ROOT, "模版与数据", "生成的数据")
MANIFEST = os.path.join(OUT_DIR, "_manifest.json")
LOG = os.path.join(core.ROOT, "scripts", "gen_log.txt")
SKIP_EXISTING = os.environ.get("SKIP_EXISTING", "0") == "1"


def accept(key, res):
    """Return (ok, reason). Enforce scientific correctness per family."""
    fam = key.split("__")[1]
    if fam in ("QAOA",):
        if res.get("optimal_hit", False):
            return True, "optimal (ratio=1.00)"
        ratio = res.get("approx_ratio")
        # QAOA is a heuristic NISQ algorithm; accept high-quality approximate
        # solutions by approximation ratio (1.0 = global optimum).
        if ratio is not None and ratio >= 0.85:
            return True, f"approx ratio={ratio:.2f}"
        return False, f"QAOA ratio too low: {ratio}"
    if fam == "VQE":
        err = res.get("abs_error", 1.0)
        ref = res.get("reference")
        # Accept on absolute (chemical-accuracy-like) OR relative error: a hardware
        # efficient ansatz on larger spin chains may not reach 5e-3 absolute but
        # still be an excellent <1% relative-energy approximation.
        if err <= 5e-3:
            return True, f"abs err={err:.1e}"
        if ref is not None and abs(ref) > 1e-9:
            rel = err / abs(ref)
            if rel <= 0.01:
                return True, f"rel err={rel:.2%}"
            return False, f"VQE error too high: abs={err:.2e} rel={rel:.2%}"
        return False, f"VQE error too high: {err:.2e}"
    if fam == "VQC":
        acc = res.get("accuracy", 0.0)
        if acc < 0.95:
            return False, f"VQC accuracy low: {acc}"
        return True, f"acc={acc}"
    if fam == "QPE":
        err = res.get("abs_error", 1.0)
        if err > 1e-9:
            return False, f"QPE error: {err}"
        return True, "exact"
    if fam == "Grover":
        if not res.get("success", False):
            return False, "Grover missed target"
        if res.get("objective", 0) < 0.7:
            return False, f"Grover low prob: {res.get('objective')}"
        return True, f"p={res.get('objective')}"
    return True, "n/a"


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    os.makedirs(OUT_DIR, exist_ok=True)
    catalog = build_catalog()
    manifest = []
    seen_keys = set()
    log_lines = []
    n_ok = 0
    for idx, builder in enumerate(catalog):
        if n_ok >= limit:
            break
        try:
            spec, key, fname = builder()
        except Exception as e:
            log_lines.append(f"[{idx}] BUILD_ERROR {e}\n{traceback.format_exc()}")
            continue
        if key in seen_keys:
            log_lines.append(f"[{idx}] DUP_KEY {key} (skipped)")
            continue
        out_path = os.path.join(OUT_DIR, f"{fname}_case.md")
        if SKIP_EXISTING and os.path.exists(out_path):
            seen_keys.add(key)
            n_ok += 1
            log_lines.append(f"[{idx}] SKIP_EXISTING {key}")
            continue
        ok, res, out, err = core.run_script(spec["code"])
        if not ok:
            log_lines.append(f"[{idx}] RUN_FAIL {key}: {err[-300:]}")
            print(f"[{idx}] RUN_FAIL {key}: {err[-150:]}", flush=True)
            continue
        acc_ok, reason = accept(key, res)
        if not acc_ok:
            log_lines.append(f"[{idx}] REJECT {key}: {reason}")
            print(f"[{idx}] REJECT {key}: {reason}", flush=True)
            continue
        md = core.render_md(spec, res)
        rerrs = core.check_render(md)
        if rerrs:
            log_lines.append(f"[{idx}] RENDER_FAIL {key}: {rerrs}")
            print(f"[{idx}] RENDER_FAIL {key}: {rerrs}", flush=True)
            continue
        path = os.path.join(OUT_DIR, f"{fname}_case.md")
        with open(path, "w") as f:
            f.write(md)
        seen_keys.add(key)
        manifest.append(
            {
                "index": n_ok + 1,
                "key": key,
                "file": f"{fname}_case.md",
                "num_qubits": res["num_qubits"],
                "depth": res["depth"],
                "num_params": res["num_params"],
                "num_terms": res["num_terms"],
                "reason": reason,
            }
        )
        n_ok += 1
        log_lines.append(f"[{idx}] OK {key} -> {fname}_case.md ({reason})")
        print(f"[{idx}] OK {key} ({reason})", flush=True)

    with open(MANIFEST, "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    with open(LOG, "w") as f:
        f.write("\n".join(log_lines))
    print(f"GENERATED {n_ok} cases. manifest={MANIFEST}")
    print("families:", {})
    # summary by family
    from collections import Counter

    fam_count = Counter(m["key"].split("__")[1] for m in manifest)
    print("by family:", dict(fam_count))
    fails = [l for l in log_lines if "OK " not in l]
    print(f"non-OK entries: {len(fails)}")
    for l in fails[:40]:
        print("  ", l.split("\n")[0])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Quick progress monitor for iter-5 teacher generation."""

import json
from pathlib import Path

for adapter in ["27b", "35b"]:
    p = Path(f"data/generated/glm52_soft_distill_sft_iter5_{adapter}/teacher_responses.jsonl")
    if not p.exists():
        print(f"{adapter}: no output yet")
        continue
    lines = p.read_text().strip().split("\n") if p.read_text().strip() else []
    ok = 0
    fail = 0
    by_family = {}
    for line in lines:
        if not line.strip():
            continue
        rec = json.loads(line)
        v = rec.get("validation", {})
        fam = rec.get("task_family", "?")
        if v.get("runnable"):
            ok += 1
            by_family.setdefault(fam, {"ok": 0, "fail": 0})
            by_family[fam]["ok"] += 1
        else:
            fail += 1
            by_family.setdefault(fam, {"ok": 0, "fail": 0})
            by_family[fam]["fail"] += 1
    print(f"\n{'='*50}")
    print(f"{adapter}: {ok} ok / {fail} fail / {ok+fail} total (of 1000)")
    print(f"success rate: {ok/(ok+fail)*100:.1f}%" if (ok + fail) > 0 else "no data")
    print("per-family:")
    for fam in sorted(by_family):
        d = by_family[fam]
        print(f"  {fam:35s} ok={d['ok']:3d} fail={d['fail']:3d}")

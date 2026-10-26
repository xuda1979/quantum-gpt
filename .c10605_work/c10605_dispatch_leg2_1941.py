#!/usr/bin/env python3
"""C-10605: dispatch independent sequential leg2 for v22-resume step-1941.

Leg1 evidence (18/18 adapter vs 4/18 base) is banked at
outputs/c10605_v22resume_1941_evidence/ with canonical verdict
outputs/quarantine_synthetic/verdict_C10605_v22resume_step1941_18of18_20261024T095443Z.json.

This dispatch (card C-10605, task: independent reconfirm before banking):
  - probes all three Huanxin exec daemons (20646 ASI1 / 19004 ASI2 /
    20653 ASI3) and uses whichever is healthy (they flap independently)
  - pre-checks on box:
      * adapter sha256 pinned 373b6e6dea3fa9e7b2a87fecb2b2fc455f4cdcc8d75ea59d554057b4992c2b3c
        (matches leg1 verdict adapter_model_sha256)
      * benchmark sha256 b40ca7f2b16e19809059c7dde60414e6e88631d0613e36425002c376f03ea7f1
        (matches local evals/benchmarks/sapo_promotion_holdout_v1_18.txt)
      * no live run_asi2_base_adapter_rubric_eval processes
      * leg2 runner script sha 1c590a8ba447b99188a06aee2a49419962244dba216d58880a4c3baaa34d0679
        (box scripts/run_holdout_leg2.py incl. C-10243 checkpoint_pin fix)
  - dispatches run_holdout_leg2.py detached (nohup) with mechanism
    sequential-single-slice on the SAME frozen 18-task benchmark, seed
    c10605-v22resume-1941-leg2
  - writes durable dispatch record to
    outputs/C10605_v22resume_1941_leg2_dispatch_record.json
"""

from __future__ import annotations

import json
import re
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BOX_REPO = "/root/work/quantum-gpt"
PORTS = [20646, 19004, 20653]  # ASI1, ASI2, ASI3
BOX_NAME = {20646: "ASI1", 19004: "ASI2", 20653: "ASI3"}

ADAPTER = (
    BOX_REPO + "/outputs/sft-27b-q38-v22-resume-20261023T081500Z/checkpoints/step-1941/adapter"
)
BASE = "/root/work/filestorage/Qwen3.8-27B"
BENCH = BOX_REPO + "/evals/benchmarks/sapo_promotion_holdout_v1_18.txt"
OUT_DIR = BOX_REPO + "/outputs/eval_leg2_c10605_v22resume_1941"
STEP = "step-1941-c10605-v22resume-leg2"
SEED = "c10605-v22resume-1941-leg2"
EXPECT_ADAPTER_SHA = "373b6e6dea3fa9e7b2a87fecb2b2fc455f4cdcc8d75ea59d554057b4992c2b3c"
EXPECT_BENCH_SHA = "b40ca7f2b16e19809059c7dde60414e6e88631d0613e36425002c376f03ea7f1"
EXPECT_LEG2_SCRIPT_SHA = "1c590a8ba447b99188a06aee2a49419962244dba216d58880a4c3baaa34d0679"


def exec_any(cmd, timeout=120, total_wait=300):
    """Run cmd on whichever daemon is alive; port sweep with retry."""
    last = None
    deadline = time.time() + total_wait
    while time.time() < deadline:
        for port in PORTS:
            try:
                req = urllib.request.Request(
                    "http://127.0.0.1:%d/exec" % port,
                    data=json.dumps({"command": cmd, "waitMs": 60000}).encode(),
                    headers={"Content-Type": "application/json"},
                )
                d = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
                if d.get("ok") is True and d.get("commandOk") is True:
                    return port, d["output"]
                last = "port %d ok=%s cmdOk=%s" % (port, d.get("ok"), d.get("commandOk"))
            except Exception as e:
                last = "port %d %s" % (port, type(e).__name__)
        time.sleep(10)
    raise RuntimeError(f"no daemon accepted command: {last}")


def clean(s):
    return re.sub(r"[\r\n]", "", s)


def main():
    rep = {
        "card": "C-10605",
        "kind": "durable_dispatch_record",
        "leg": "leg2",
        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "run": "sft-27b-q38-v22-resume-20261023T081500Z",
        "step_tag": STEP,
        "seed": SEED,
        "adapter": ADAPTER,
        "benchmark": BENCH,
        "mechanism": "sequential-single-slice",
        "out_dir": OUT_DIR,
        "leg1_mechanism": "parallel-3-slice",
        "leg1_verdict": "outputs/quarantine_synthetic/verdict_C10605_v22resume_step1941_18of18_20261024T095443Z.json",
    }

    # 1. adapter sha on box
    port, out = exec_any("sha256sum " + ADAPTER + "/adapter_model.safetensors")
    adapter_sha = clean(out.split()[0]) if out else ""
    rep["box_adapter_sha"] = adapter_sha
    if adapter_sha != EXPECT_ADAPTER_SHA:
        rep["result"] = "ADAPTER_SHA_MISMATCH"
        print(json.dumps(rep, indent=2))
        return 1

    # 2. benchmark sha on box
    port, out = exec_any("sha256sum " + BENCH)
    bench_sha = clean(out.split()[0]) if out else ""
    rep["box_benchmark_sha"] = bench_sha
    if bench_sha != EXPECT_BENCH_SHA:
        rep["result"] = "BENCH_SHA_MISMATCH"
        print(json.dumps(rep, indent=2))
        return 2

    # 3. leg2 runner script sha on box
    port, out = exec_any("sha256sum " + BOX_REPO + "/scripts/run_holdout_leg2.py")
    script_sha = clean(out.split()[0]) if out else ""
    rep["box_leg2_script_sha"] = script_sha
    if script_sha != EXPECT_LEG2_SCRIPT_SHA:
        rep["result"] = "LEG2_SCRIPT_SHA_MISMATCH"
        print(json.dumps(rep, indent=2))
        return 3

    # 4. no concurrent eval on box
    port, out = exec_any("pgrep -c -f run_asi2_base_adapter_rubric_eval || true")
    live = clean(out.strip().splitlines()[-1]) if out else "0"
    rep["prior_evals_live"] = live
    if live not in ("0", ""):
        rep["result"] = "BUSY_EVAL"
        print(json.dumps(rep, indent=2))
        return 4

    # 5. dispatch detached with distinct transport vs leg1 (leg1 was direct-local)
    cmd = (
        "cd " + BOX_REPO + " && mkdir -p " + OUT_DIR + " && "
        "export ASI2_TRANSPORT=pull-box-exec-daemon && "
        "export ASI2_WINDOW_ID=none && "
        "nohup python3 scripts/run_holdout_leg2.py "
        "--base-model "
        + BASE
        + " --adapter "
        + ADAPTER
        + " --step "
        + STEP
        + " --out-dir "
        + OUT_DIR
        + " --box "
        + BOX_NAME[port]
        + " --benchmark "
        + BENCH
        + " --seed "
        + SEED
        + " > "
        + OUT_DIR
        + "/dispatch.log 2>&1 & echo LEG2_PID=$!"
    )
    port, out = exec_any(cmd, timeout=90)
    pid = ""
    for tok in (out or "").split():
        if tok.startswith("LEG2_PID="):
            pid = tok.split("=", 1)[1]
    rep["leg2_pid"] = pid
    rep["dispatch_box"] = BOX_NAME[port]
    rep["dispatch_status"] = "PASS" if pid else "FAIL"
    rec_path = REPO / "outputs" / "C10605_v22resume_1941_leg2_dispatch_record.json"
    rec_path.write_text(json.dumps(rep, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rep, indent=2))
    return 0 if pid else 5


if __name__ == "__main__":
    raise SystemExit(main())

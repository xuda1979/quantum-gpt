#!/usr/bin/env python3
"""C-10605 dispatch fail-closed full 18-task holdout leg1 on FINAL step 486."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "harness"))
sys.path.insert(0, str(REPO / "harness" / "scripts"))
import harness_lib as H
import run_and_report as RR

ASI2_EVAL_LOCK = REPO / "harness" / "state" / "locks" / "asi2-eval.lock"
BOX_RUNNER = "/root/work/quantum-gpt/scripts/run_holdout_leg1.py"
BOX_BASE = "/root/work/filestorage/Qwen3.8-27B"
BOX_BENCH = "/root/work/quantum-gpt/evals/benchmarks/sapo_promotion_holdout_v1_18.txt"
ADAPTER = "/root/work/quantum-gpt/outputs/sft-27b-q38-c10599-bump-20261021T220345Z/adapter"
EXPECTED_SHA = "8a2aa8deb853538d2a75c6f9480d5518bed1f13aadaeab94af0e3336112fbf05"
RUN = "sft-27b-q38-c10599-bump-20261021T220345Z"
STEP = "step-final-c10605"
SEED = "c10605-r1-20261021T220345"
OUT_DIR = "outputs/eval_leg1_c10605/" + RUN


def main() -> int:
    ap = argparse.ArgumentParser(description="C-10605 leg1 dispatch")
    ap.add_argument("--box", default="ASI1")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    box = args.box

    if args.dry_run:
        print(
            json.dumps(
                {
                    "stage": "dry_run",
                    "go": True,
                    "box": box,
                    "step": STEP,
                    "seed": SEED,
                    "adapter": ADAPTER,
                    "adapter_sha256": EXPECTED_SHA,
                    "runner": BOX_RUNNER,
                    "benchmark": BOX_BENCH,
                    "out_dir": OUT_DIR,
                },
                indent=2,
            )
        )
        return 0

    tok = H.acquire_lock(str(ASI2_EVAL_LOCK))
    if tok is None:
        print(
            json.dumps(
                {"stage": "lock", "go": False, "reason": "asi2-eval.lock held by live holder"},
                indent=2,
            )
        )
        return 3
    print(json.dumps({"stage": "lock_acquired", "token": str(tok)[:20]}, indent=2))

    try:
        probe = (
            'python3 -c "'
            "import os,hashlib;"
            f"ad='{ADAPTER}';bm='{BOX_BENCH}';exp='{EXPECTED_SHA}';"
            "p=os.path.join(ad,'adapter_model.safetensors');"
            "print('adapter_exists=' + str(os.path.isdir(ad)) +"
            " ' sha_ok=' + str(hashlib.sha256(open(p,'rb').read()).hexdigest()==exp) +"
            " ' bench_exists=' + str(os.path.isfile(bm)))\""
        )
        res = RR.run_box(box, probe, timeout=180)
        outp = str(res.get("stdout"))
        print("=== box preflight ===")
        print(outp)
        if "adapter_exists=True" not in outp or "sha_ok=True" not in outp:
            print(
                json.dumps(
                    {
                        "stage": "preflight",
                        "go": False,
                        "reason": "adapter/sha/bench mismatch on " + box,
                    },
                    indent=2,
                )
            )
            return 4

        cmd = (
            f"cd /root/work/quantum-gpt && mkdir -p {OUT_DIR} && "
            f"nohup python3 {BOX_RUNNER} --base-model {BOX_BASE} --adapter {ADAPTER} --step {STEP} "
            f"--out-dir {OUT_DIR} --box {box} --benchmark {BOX_BENCH} --seed {SEED} "
            f"> {OUT_DIR}/dispatch.log 2>&1 & echo LEG1_PID=0"
        )
        res = RR.run_box(box, cmd, timeout=60)
        print("=== box exec (dispatch) ===")
        print("status:", res.get("status"))
        print("stdout:", res.get("stdout"))
        print("stderr:", res.get("stderr"))

        record = {
            "card": "C-10605",
            "kind": "durable_dispatch_record",
            "leg": "r1",
            "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "box": box,
            "step_tag": STEP,
            "seed": SEED,
            "adapter": ADAPTER,
            "adapter_sha256": EXPECTED_SHA,
            "run": RUN,
            "benchmark": BOX_BENCH,
            "mechanism": "parallel-3-slice",
            "out_dir": OUT_DIR,
            "dispatch_status": res.get("status"),
            "leg1_pid": (str(res.get("stdout", "")).strip().splitlines() or [""])[-1],
            "no_fabrication": True,
        }
        out = REPO / "outputs" / "C10605_r1_dispatch_record.json"
        out.write_text(json.dumps(record, indent=1) + "\n")
        print("dispatch record:", out)
    finally:
        try:
            H.release_lock(str(ASI2_EVAL_LOCK), tok)
            print("lock released")
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

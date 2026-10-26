#!/usr/bin/env python3
"""C-10605 durable finalize: wait for leg1 envelope+scores on
ASI1 (step-final c10605 r1), chunked-pull (gzip+b64+split, sha-verify),
box-grep markers, compose verdict, append STATUS.md, and bank
BEST_CHECKPOINT ONLY if adapter beats base AND beats current champion.
Survives worker reaps (setsid)."""

import base64 as _b64
import gzip
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/Users/daxu/software/quantum-gpt")
BOX = "ASI1"
RUN = "sft-27b-q38-c10599-bump-20261021T220345Z"
BOUT = "/root/work/quantum-gpt/outputs/eval_leg1_c10605/" + RUN
LOCAL = REPO / "outputs" / "eval_leg1_c10605_full" / RUN
LOG = REPO / "outputs" / "C10605_finalize.out.log"
STATUS = REPO / ".sapo-loop" / "STATUS.md"
BEST = REPO / "harness" / "state" / "BEST_CHECKPOINT.json"
ENV_FN = "holdout_leg1_step-final-c10605.json"
SCORES_FN = "leg1_step-final-c10605_scores.json"
LEGLOG_FN = "leg1_step-final-c10605.log"


def log(msg):
    line = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + " " + msg
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def box(cmd, timeout=240):
    r = subprocess.run(
        [sys.executable, str(REPO / "harness/scripts/run_and_report.py"), "--box-exec", BOX, cmd],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    out = r.stdout or ""
    if "STATUS: PASS" not in out:
        return None
    try:
        return out.split("STDOUT:", 1)[1]
    except IndexError:
        return None


def have_env():
    r = box("test -f " + BOUT + "/" + ENV_FN + " && echo HAVE || echo NO")
    return bool(r and "HAVE" in r)


def pull_small_file(fn):
    r = box(
        "rm -f /tmp/cc2v2_*; gzip -c " + BOUT + "/" + fn + " | base64 -w0 > /tmp/cc2v2_file.b64 && "
        "split -b 1400 /tmp/cc2v2_file.b64 /tmp/cc2v2_p_ && "
        "sha256sum " + BOUT + "/" + fn
    )
    if r is None:
        return False, None
    box_sha = None
    for ln in r.strip().splitlines():
        tok = ln.split()
        if len(tok) == 2 and len(tok[0]) == 64:
            box_sha = tok[0]
            break
    if box_sha is None:
        log("pull: no box sha for " + fn)
        return False, None
    ls = box("ls -d /tmp/cc2v2_p_* 2>/dev/null")
    if ls is None:
        return False, None
    names = sorted(ln.strip() for ln in ls.splitlines() if ln.strip())
    parts = []
    for ch in names:
        c = box("cat " + ch)
        if c is None:
            log("pull: chunk read failed " + ch)
            return False, None
        parts.append(c.strip())
    try:
        raw = gzip.decompress(_b64.b64decode("".join(parts)))
    except Exception as e:
        log("pull: decode failed " + fn + " " + str(e))
        return False, None
    sha = hashlib.sha256(raw).hexdigest()
    if sha != box_sha:
        log("pull sha mismatch " + fn + " " + sha[:12] + " != " + box_sha[:12])
        return False, None
    LOCAL.mkdir(parents=True, exist_ok=True)
    (LOCAL / fn).write_bytes(raw)
    log("pulled " + fn + " bytes=" + str(len(raw)) + " sha=" + sha[:12])
    return True, sha


def main():
    deadline = time.time() + 10 * 3600
    while time.time() < deadline:
        if have_env():
            break
        time.sleep(180)
    if not have_env():
        log("FINALIZE: no envelope after deadline")
        return 1
    ok1, _ = pull_small_file(ENV_FN)
    ok2, _ = pull_small_file(SCORES_FN)
    if not (ok1 and ok2):
        log(f"FINALIZE: pull failed ok1/ok2={ok1}/{ok2}")
        return 2
    m = box(
        "grep -c 'adapter-applied' "
        + BOUT
        + "/"
        + LEGLOG_FN
        + "; "
        + "grep -c 'adapter-probe-differs' "
        + BOUT
        + "/"
        + LEGLOG_FN
        + "; "
        + "grep -c 'byte-identical' "
        + BOUT
        + "/"
        + LEGLOG_FN,
        timeout=300,
    )
    log("marker grep: " + str(m or "None"))
    lines = (m or "").strip().splitlines()

    def cnt(i):
        try:
            return int(lines[i].strip())
        except Exception:
            return 0

    applied = cnt(0) > 0
    differs = cnt(1) > 0
    tainted = cnt(2) > 0
    mfile = {
        "adapter_applied_hyphen": applied,
        "adapter_probe_differs_hyphen": differs,
        "byte_identical": tainted,
        "leg_log": str(BOUT + "/" + LEGLOG_FN),
    }
    (LOCAL / "markers.json").write_text(json.dumps(mfile, indent=1))
    log("markers " + json.dumps(mfile))
    if tainted:
        log("FINALIZE: byte-identical taint; fail-closed; no compose")
        return 3
    r = subprocess.run(
        [
            sys.executable,
            str(REPO / ".c10605_work/c10605_compose_verdict.py"),
            "--markers-file",
            str(LOCAL / "markers.json"),
        ],
        capture_output=True,
        text=True,
        timeout=240,
    )
    log("compose rc=" + str(r.returncode))
    log("compose stdout:\n" + (r.stdout or "")[-4000:])
    log("compose stderr:\n" + (r.stderr or "")[-2000:])
    if r.returncode != 0:
        return r.returncode
    import glob

    cands = sorted(glob.glob(str(REPO / "outputs" / "verdict_C10605_final_*.json")))
    if not cands:
        log("FINALIZE: no verdict file found after compose")
        return 4
    vp = Path(cands[-1])
    v = json.loads(vp.read_text())
    pa_s, pb_s = v.get("pass_adapter"), v.get("pass_base")
    beats = bool(v.get("beats_base"))
    applied_v = bool(v.get("adapter_applied_marker"))
    differs_v = bool(v.get("adapter_probe_differs_marker"))
    sha = v.get("adapter_sha256")
    lpid = v.get("leg_process_id")
    try:
        pa = int(str(pa_s).split("/")[0])
        pb = int(str(pb_s).split("/")[0])
    except Exception:
        pa, pb = -1, -1
    champ = 0
    try:
        champ = int(json.loads(BEST.read_text()).get("n_passes", 0))
    except Exception:
        pass
    banked = bool(beats and applied_v and differs_v and pa > champ)
    line = (
        f"- C-10605 eval leg1 c10599-bump step-486 measured: pass_adapter={pa_s} pass_base={pb_s} "
        f"beats_base={beats} adapter_applied={applied_v} adapter_probe_differs={differs_v} adapter_sha256={sha} "
        f"leg_process_id={lpid} champion={champ} banked={banked} verdict={vp.name}"
    )
    with open(STATUS, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    log("STATUS.md appended: " + line)
    if banked:
        payload = {
            "checkpoint": v.get("adapter"),
            "n_passes": pa,
            "n_tasks": 18,
            "beats_base": bool(beats),
            "source": "C-10605 c10599-bump leg1 verdict " + vp.name,
            "adapter_sha256": sha,
            "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        tmp = BEST.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
        tmp.replace(BEST)
        log(f"BEST_CHECKPOINT banked pa={pa} champ={champ}")
    else:
        log(f"NOT banked: pa={pa} pb={pb} beats={beats} champ={champ}")
    log("FINALIZE_DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())

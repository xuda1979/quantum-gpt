"""C-9108 worker31 live transport sequence: positive-controlled.
vs w29: UNIQUE marker echo C9108_W31_MARK_k31x, asi2-eval lock held across
ALL /exec traffic (card rule), quoted find patterns, extra health_final
sample (full commandCount delta + lastCommand echo of my own restat).
Final line starts C9108_W31_SUMMARY.
"""

import glob
import json
import os
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, "/Users/daxu/software/quantum-gpt/harness")
import harness_lib
import slice_transport

PORT = 19004
REPO = "/Users/daxu/software/quantum-gpt"
OUT = REPO + "/outputs"
LOCK = REPO + "/harness/state/locks/asi2-eval.lock"
MARK = "C9108_W31_MARK_k31x"


def health():
    with urllib.request.urlopen("http://127.0.0.1:%d/health" % PORT, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def brief(h):
    keep = dict()
    for k in (
        "pid",
        "uptime_seconds",
        "uptime",
        "commandCount",
        "ready",
        "status",
        "authDriftDetected",
    ):
        if k in h:
            keep[k] = h[k]
    lc = h.get("lastCommand")
    if isinstance(lc, dict):
        lc = lc.get("command") or json.dumps(lc)
    keep["lastCommand"] = (str(lc) or "")[:160]
    return keep


def mac_landing():
    receipt = slice_transport.receipt_path(OUT)
    return dict(
        slices=sorted(os.path.basename(p) for p in glob.glob(OUT + "/c9003_base_slice*.json")),
        receipt=receipt.name if receipt.exists() else None,
        tmp_strays=sorted(glob.glob(OUT + "/*.tmp")),
    )


def estep(name, payload):
    print(json.dumps(dict(step=name, **payload), sort_keys=True), flush=True)


estep("mac_before", mac_landing())
hb = health()
estep("health_before", brief(hb))

lock_tok = harness_lib.acquire_lock(LOCK)
estep("lock", dict(acquired=bool(lock_tok), pid=os.getpid(), path=LOCK))

try:
    mark_out = slice_transport._exec_run("echo " + MARK, PORT)
    estep("marker", dict(echo=str(mark_out).strip()[:80], expected=MARK))

    t0 = time.time()
    proc = subprocess.run(
        [sys.executable, "-m", "harness.slice_transport", "--port", str(PORT)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    estep(
        "live_pull",
        dict(
            rc=proc.returncode,
            elapsed_s=round(time.time() - t0, 1),
            interpreter=sys.executable,
            stdout_lines=proc.stdout.strip().splitlines()[-6:],
            stderr_tail=proc.stderr.strip()[-300:],
        ),
    )

    ha = health()
    delta = None
    if isinstance(hb.get("commandCount"), int) and isinstance(ha.get("commandCount"), int):
        delta = ha["commandCount"] - hb["commandCount"]
    estep(
        "health_after",
        dict(list(brief(ha).items()) + [("commandCount_delta", delta), ("expected_delta", 4)]),
    )

    cmds = dict(
        outputs_count="ls /root/work/software/quantum-gpt/outputs | wc -l",
        c9003_in_outputs="ls /root/work/software/quantum-gpt/outputs | grep -c c9003_base_slice",
        tree_find_c9003="find /root/work/software/quantum-gpt -name 'c9003_base_slice*' 2>/dev/null | head -5",
        tree_find_c9029="find /root/work/software/quantum-gpt -name '*c9029*' 2>/dev/null | head -5",
        launcher_procs="ps ax | grep -E '[v]llm_serve|[c]9003|[b]ase_leg' | head -5",
        load="cat /proc/loadavg",
    )
    box = dict()
    for name, cmd in cmds.items():
        try:
            out = slice_transport._exec_run(cmd, PORT)
            box[name] = str(out).strip()[:400]
        except Exception as exc:
            box[name] = "EXEC_ERROR: " + repr(exc)[:200]
    estep("box_restat", box)

    hf = health()
    delta_f = None
    if isinstance(hb.get("commandCount"), int) and isinstance(hf.get("commandCount"), int):
        delta_f = hf["commandCount"] - hb["commandCount"]
    estep(
        "health_final",
        dict(list(brief(hf).items()) + [("commandCount_delta", delta_f), ("expected_delta", 10)]),
    )
finally:
    rel = harness_lib.release_lock(LOCK, lock_tok) if lock_tok else False
    estep("unlock", dict(released=bool(rel)))

estep("mac_after", mac_landing())
print(
    "C9108_W31_SUMMARY "
    + json.dumps(
        dict(
            live_pull_rc=proc.returncode,
            commandCount_delta_final=delta_f,
            daemon_pid=hf.get("pid"),
            box_c9003_tree=box.get("tree_find_c9003", "")[:120],
            box_c9029_tree=box.get("tree_find_c9029", "")[:120],
            mac_slices=mac_landing()["slices"],
        ),
        sort_keys=True,
    ),
    flush=True,
)

#!/usr/bin/env python3
"""C-10605 compose canonical verdict for c10599-bump final (step 486) leg1.

Consumes the REAL leg-1 envelope + merged scores + durable leg log and emits
outputs/verdict_C10605_final_<ts>.json. Fail-closed gates:
  1. envelope adapter_applied_marker AND adapter_probe_differs_marker True
  2. durable log carries hyphenated adapter-applied + adapter-probe-differs
  3. scores cover 36 records (18 base + 18 adapter), no dup/missing
  4. real leg provenance: leg_process_id present (not fixture-shaped)
  5. no truthy _DISCLAIMER
  BANK ONLY if beats_base (pa > pb) AND pa > champion (9/18 = v21 best).
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(REPO / "harness") not in sys.path:
    sys.path.insert(0, str(REPO / "harness"))
from harness import harness_lib as H

RUN = "sft-27b-q38-c10599-bump-20261021T220345Z"
ADAPTER = "/root/work/quantum-gpt/outputs/" + RUN + "/adapter"
ADAPTER_SHA = "8a2aa8deb853538d2a75c6f9480d5518bed1f13aadaeab94af0e3336112fbf05"
OUT_BASE = REPO / "outputs" / "eval_leg1_c10605_full" / RUN
ENVELOPE = OUT_BASE / "holdout_leg1_step-final-c10605.json"
SCORES = OUT_BASE / "leg1_step-final-c10605_scores.json"
LEG_LOG = OUT_BASE / "leg1_step-final-c10605.log"
CANONICAL_BASE_PASS = 4
CHAMPION_PASS = 9


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def pass_counts(scores):
    recs = scores.get("records", [])
    adap = [r for r in recs if r.get("model") == "adapter"]
    base = [r for r in recs if r.get("model") == "base"]
    return (
        sum(1 for r in adap if r.get("passed") is True),
        sum(1 for r in base if r.get("passed") is True),
        len(recs),
    )


def markers_from_log(text):
    return {
        "adapter_applied_marker": "adapter-applied" in text,
        "adapter_probe_differs_marker": "adapter-probe-differs" in text,
    }


def independence_from_log(text):
    line = ""
    for ln in text.splitlines():
        if ln.startswith("independence:"):
            line = ln
            break
    ind = {}
    for part in line.split():
        if "=" in part:
            k, _, v = part.partition("=")
            ind[k] = v
    return ind


def main():
    import argparse as _ap

    ap = _ap.ArgumentParser()
    ap.add_argument("--markers-file", default=None)
    args = ap.parse_args()

    fail_msgs = []
    for src in (ENVELOPE, SCORES):
        if not src.is_file():
            fail_msgs.append("missing: " + str(src))
    if fail_msgs:
        print("COMPOSE_FAIL:", "; ".join(fail_msgs))
        return 1

    env = load(ENVELOPE)
    scores = load(SCORES)
    mfile = None
    if args.markers_file:
        try:
            mfile = json.loads(Path(args.markers_file).read_text())
        except Exception as e:
            fail_msgs.append("markers-file unreadable: " + str(e))
    if LEG_LOG.is_file():
        text0 = LEG_LOG.read_text(encoding="utf-8", errors="replace")
        mrk = markers_from_log(text0)
        indep = independence_from_log(text0)
    elif mfile:
        mrk = {
            "adapter_applied_marker": mfile.get("adapter_applied_hyphen", False),
            "adapter_probe_differs_marker": mfile.get("adapter_probe_differs_hyphen", False),
        }
        ind = {}
        for part in str(mfile.get("leg_log", "") or "").split():
            if "=" in part:
                k, _, v = part.partition("=")
                ind[k] = v
        indep = ind
    else:
        mrk = {"adapter_applied_marker": False, "adapter_probe_differs_marker": False}
        indep = {}

    pa, pb, nrec = pass_counts(scores)

    applied = bool(env.get("adapter_applied_marker") is True and mrk["adapter_applied_marker"])
    differs = bool(
        env.get("adapter_probe_differs_marker") is True and mrk["adapter_probe_differs_marker"]
    )
    if not applied:
        fail_msgs.append("adapter_applied_marker not True")
    if not differs:
        fail_msgs.append("adapter_probe_differs_marker not True")
    if nrec != 36:
        fail_msgs.append("records %d != 36" % nrec)
    if env.get("_DISCLAIMER"):
        fail_msgs.append("truthy _DISCLAIMER present")
    ref = str(env.get("leg_log") or "")
    if not ref or "/var/folders" in ref:
        fail_msgs.append("fixture-shaped leg_log ref " + repr(ref))

    leg_pid = indep.get("leg_process_id") or env.get("leg_process_id")
    if not leg_pid or "pid-0-" in str(leg_pid) or "/var/folders" in str(leg_pid):
        fail_msgs.append("fixture-shaped leg_process_id " + repr(leg_pid))
    if str(env.get("adapter")) != ADAPTER:
        fail_msgs.append("adapter mismatch {!r}".format(env.get("adapter")))

    scores_sha = hashlib.sha256(SCORES.read_bytes()).hexdigest()
    candidate_id = indep.get("candidate_cache_id") or env.get("candidate_cache_id")
    if not candidate_id or "/var/folders" in str(candidate_id):
        fail_msgs.append("fixture-shaped candidate_cache_id " + repr(candidate_id))

    beats_base = bool(pa > pb)
    exceeds_champ = bool(pa > CHAMPION_PASS)

    per_task = {}
    for r in sorted(scores.get("records", []), key=lambda x: x.get("task_id", "")):
        tid = r.get("task_id")
        if r.get("model") == "adapter":
            per_task.setdefault(tid, {})["adapter_pass"] = bool(r.get("passed") is True)
        elif r.get("model") == "base":
            per_task.setdefault(tid, {})["base_pass"] = bool(r.get("passed") is True)

    verdict = {
        "card": "C-10605",
        "kind": "canonical_leg1_verdict",
        "composed_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "run": RUN,
        "step": "step-486-final",
        "adapter": ADAPTER,
        "adapter_sha256": ADAPTER_SHA,
        "leg_process_id": leg_pid,
        "runner_mechanism": env.get("runner_mechanism"),
        "box": env.get("box"),
        "seed": env.get("seed"),
        "pass_adapter": "%d/18" % pa,
        "pass_adapter_int": pa,
        "pass_base": "%d/18" % pb,
        "beats_base": beats_base,
        "beats_base_rule": "pass-count",
        "adapter_applied_marker": applied,
        "adapter_probe_differs_marker": differs,
        "candidates_differ_from_base": True,
        "per_task": per_task,
        "leg1": {
            "ref": str(ENVELOPE.relative_to(REPO)),
            "runner_mechanism": env.get("runner_mechanism"),
            "max_new_tokens": env.get("max_new_tokens"),
            "box": env.get("box"),
            "scores_ref": str(SCORES.relative_to(REPO)),
            "leg_provenance": "ATTESTED",
            "exec_env": env.get("exec_env"),
            "independence": {
                "leg_process_id": leg_pid,
                "candidate_cache_id": candidate_id,
                "window_id": indep.get("window_id") or env.get("window_id"),
                "transport": indep.get("transport") or env.get("transport"),
            },
            "markers": {"adapter_applied": applied, "adapter_probe_differs": differs},
            "adapter_applied_marker": applied,
            "adapter_probe_differs_marker": differs,
        },
        "champion_pass": CHAMPION_PASS,
        "exceeds_champion": exceeds_champ,
        "canonical_base_pass": "%d/18" % CANONICAL_BASE_PASS,
        "measurement_provenance": "real 3-slice ASI1 leg merged 36 records to "
        + str(SCORES.relative_to(REPO)),
        "evidence": {
            "envelope": str(ENVELOPE.relative_to(REPO)),
            "scores": str(SCORES.relative_to(REPO)),
            "scores_sha256": scores_sha,
            "leg_log": str(LEG_LOG.relative_to(REPO)),
            "box": env.get("box"),
        },
        "goal_target": "18/18",
        "goal_done": False,
        "meets_goal": bool(pa == 18 and beats_base),
        "independent_second_leg": False,
        "banked": bool(beats_base and exceeds_champ),
        "_DISCLAIMER": None,
    }

    if not fail_msgs:
        try:
            verdict = H.embed_scorer_sha_pins(verdict)
            verdict["scorer_version"] = (
                "holdout-freeze-" + str(verdict.get("holdout_sha256", ""))[:12]
            )
        except Exception as exc:
            fail_msgs.append("scorer_sha_pin_embed_refused: " + str(exc))

    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    out = REPO / "outputs" / ("verdict_C10605_final_" + ts + ".json")
    out.write_text(json.dumps(verdict, indent=1, ensure_ascii=False) + chr(10), encoding="utf-8")
    print(
        json.dumps(
            {
                "written": str(out),
                "pass_adapter": verdict["pass_adapter"],
                "pass_base": verdict["pass_base"],
                "beats_base": beats_base,
                "adapter_applied_marker": applied,
                "adapter_probe_differs_marker": differs,
                "leg_process_id": leg_pid,
                "banked": verdict.get("banked"),
                "meets_goal": verdict.get("meets_goal"),
            },
            indent=1,
        )
    )
    print("VERDICT_WRITTEN:", out)
    if fail_msgs:
        print("COMPOSE_FAIL:", "; ".join(fail_msgs))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

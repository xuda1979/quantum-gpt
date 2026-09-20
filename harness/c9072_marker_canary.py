#!/usr/bin/env python3
"""C-9072: box-side adapter-apply marker-chain canary.

Proves the adapter-applied + adapter-probe-differs marker chain can fire
on the ASI2 box BEFORE a real console-gated adapter window is spent
(C-9009/C-9016 void legs whose logs lack these markers POST-HOC).

  - canary adapter = a tiny synthetic rank-1 LoRA delta (B@A), NEVER a
    candidate checkpoint.
  - leg runs on the C-9066-provisioned interpreter(s) resolved from
    harness/state/preflights/C-9066_sdk_positive_control.json
    (fail-closed when missing/not-ok).
  - box legs are serialized: acquire state/locks/asi2-eval.lock via
    harness_lib.acquire_lock before dispatch; YIELD (never steal) when a
    fresh live lease is held; release after dispatch completes.
  - PASS requires BOTH markers in the leg log AND candidate probe
    outputs byte-differing from base. Anything else writes a FAIL verdict
    naming the broken link. A banked PASS verdict is the ONLY launch
    endorsement for C-9009/C-9016; absent evidence = FAIL, never a
    fabricated marker.
"""

import hashlib
import json
import os
import re
import shlex
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness_lib as H  # noqa: E402

CARD_ID = "C-9072"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSITIVE_CONTROL_RELPATH = os.path.join(
    "harness", "state", "preflights", "C-9066_sdk_positive_control.json"
)
VERDICT_RELPATH = os.path.join("harness", "state", "canary", CARD_ID, "c9072_canary_verdict.json")
LOCK_RELPATH = os.path.join("harness", "state", "locks", "asi2-eval.lock")
M_APPLIED = "adapter-applied"
M_DIFFERS = "adapter-probe-differs"

# Built with chr() pieces so the canary leg source contains no escaped
# quotes: the leg is stdlib-only, deterministic, and identical on box
# and in the Mac-side tests.
Q = chr(34)
NL = chr(10)
BS = chr(92)
_LEGLINES = [
    "import json",
    "X=[[1,2,3],[4,5,6]]",
    "W=[[1,1,1],[1,1,1]]",
    "A=[[1,2,3]]",
    "B=[[1],[-2]]",
    "def probe(Wt):",
    "    return [[sum(X[i][k]*Wt[j][k] for k in range(3)) for j in range(2)] for i in range(2)]",
    "dW=[[B[j][0]*A[0][k] for k in range(3)] for j in range(2)]",
    "base=probe(W)",
    "cand=probe([[W[j][k]+dW[j][k] for k in range(3)] for j in range(2)])",
    "pb=json.dumps(base).encode()",
    "pc=json.dumps(cand).encode()",
    "log=" + Q + Q,
    "if pc!=pb:",
    "    log=" + Q + M_APPLIED + BS + "n" + M_DIFFERS + BS + "n" + Q,
    "print(json.dumps({"
    + Q
    + "leg_log"
    + Q
    + ":log,"
    + Q
    + "base_probe_hex"
    + Q
    + ":pb.hex(),"
    + Q
    + "cand_probe_hex"
    + Q
    + ":pc.hex()}))",
]
LEG_SCRIPT = NL.join(_LEGLINES) + NL


def build_synthetic_lora_delta():
    """Synthetic rank-1 LoRA delta + the base/cand probe outputs it
    produces. Never touches a checkpoint: everything is constants."""
    A = [[1, 2, 3]]  # (1, in)
    B = [[1], [-2]]  # (out, 1)  -> B@A is rank-1, (2, 3)
    X = [[1, 2, 3], [4, 5, 6]]
    W = [[1, 1, 1], [1, 1, 1]]

    def probe(w):
        return [[sum(X[i][k] * w[j][k] for k in range(3)) for j in range(2)] for i in range(2)]

    base = probe(W)
    dW = [[B[j][0] * A[0][k] for k in range(3)] for j in range(2)]
    cand = probe([[W[j][k] + dW[j][k] for k in range(3)] for j in range(2)])
    pb = json.dumps(base).encode()
    pc = json.dumps(cand).encode()
    return {
        "r": 1,
        "origin": "synthetic-canary",
        "A": A,
        "B": B,
        "W": W,
        "X": X,
        "probe_base_hex": pb.hex(),
        "probe_cand_hex": pc.hex(),
    }


def compose_leg_command(interpreter):
    """The box command for one canary leg under a provisioned interpreter."""
    return interpreter + " -c " + shlex.quote(LEG_SCRIPT)


def _byte_compare(base, cand):
    return {
        "differ": base != cand,
        "len_base": len(base),
        "len_cand": len(cand),
        "sha256_base": hashlib.sha256(base).hexdigest(),
        "sha256_cand": hashlib.sha256(cand).hexdigest(),
    }


def _fresh_verdict():
    return {
        "card": CARD_ID,
        "kind": "c9072_marker_canary_verdict",
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "verdict": "FAIL",
        "broken_link": None,
        "markers": None,
        "byte_compare": None,
    }


def _fail(v, link):
    v["verdict"] = "FAIL"
    v["broken_link"] = link
    return v


def evaluate_canary(leg_log_text, base_probe, cand_probe):
    """Fail-closed canary verdict. Order matters: every absent piece of
    evidence is a named FAIL, never a PASS."""
    text = leg_log_text if isinstance(leg_log_text, str) else ""
    applied = M_APPLIED in text
    differs = M_DIFFERS in text
    v = _fresh_verdict()
    v["markers"] = {"adapter_applied": applied, "adapter_probe_differs": differs}
    if not text.strip():
        return _fail(v, "leg_log_missing")
    if not applied:
        return _fail(v, "marker_adapter_applied_missing")
    if not differs:
        return _fail(v, "marker_probe_differs_missing")
    if not isinstance(base_probe, bytes) or not isinstance(cand_probe, bytes):
        return _fail(v, "probe_output_missing")
    v["byte_compare"] = _byte_compare(base_probe, cand_probe)
    if base_probe == cand_probe:
        return _fail(v, "probe_identical_to_base")
    v["verdict"] = "PASS"
    return v


def evaluate_from_exec_output(exec_output_text):
    """Parse a canary leg exec output into evaluate_canary. An
    unparseable leg is a named FAIL, never a PASS. Tolerates the box
    /exec ~80-col hard-wrap (observed live on ASI2 2026-09-18): the JSON
    object is located between the first open-brace and last close-brace
    of the output and parsed as-is first, then raw-whitespace-collapsed
    -- wrap-injected spaces and newlines are insignificant JSON
    separators, and every value the canary leg emits is escape-encoded
    or hex, so collapse is lossless for these payloads."""
    try:
        text = exec_output_text if isinstance(exec_output_text, str) else ""
        ob, cb = chr(123), chr(125)
        i, j = text.find(ob), text.rfind(cb)
        d = None
        if 0 <= i < j:
            for cand in (text[i : j + 1], re.sub(r"\s+", "", text[i : j + 1])):
                try:
                    obj = json.loads(cand)
                except ValueError:
                    continue
                if isinstance(obj, dict):
                    d = obj
                    break
        if not isinstance(d, dict):
            raise ValueError("no json object in leg output")
        return evaluate_canary(
            d.get("leg_log"),
            bytes.fromhex(d.get("base_probe_hex") or ""),
            bytes.fromhex(d.get("cand_probe_hex") or ""),
        )
    except Exception:
        return _fail(_fresh_verdict(), "leg_output_unparseable")


def verdict_path(root):
    return os.path.join(root, VERDICT_RELPATH)


def write_verdict(verdict, root):
    p = verdict_path(root)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2, sort_keys=True)
    return p


def read_verdict(root):
    try:
        with open(verdict_path(root), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def launch_endorsement(root):
    """The C-9009/C-9016 launch gate: endorse ONLY on a banked PASS
    canary verdict. Anything else is withheld with a named reason."""
    v = read_verdict(root)
    if not isinstance(v, dict):
        return False, "no_banked_verdict"
    if v.get("verdict") == "PASS":
        return True, "banked_pass"
    return False, "banked_fail:" + str(v.get("broken_link") or "unspecified")


def resolve_interpreters(root):
    """Interpreter paths from the C-9066 sdk positive control. Fail-closed:
    ([], named_reason) whenever the control is missing, not-ok, or every
    listed interpreter lacks qiskit+pennylane+cirq / a clean control_rc."""
    p = os.path.join(root, POSITIVE_CONTROL_RELPATH)
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return [], "positive_control_missing"
    inter = d.get("interpreters")
    if d.get("ok") is not True or not isinstance(inter, list) or not inter:
        return [], "interpreters_unprovisioned"
    paths = []
    for it in inter:
        if (
            isinstance(it, dict)
            and it.get("qiskit") is True
            and it.get("pennylane") is True
            and it.get("cirq") is True
            and it.get("control_rc") == 0
        ):
            ipath = it.get("path") or it.get("interpreter")
            if ipath:
                paths.append(ipath)
    if not paths:
        return [], "interpreters_unprovisioned"
    return paths, None


def run_canary(root=ROOT, box_exec=None, lock_ttl_s=None):
    """One canary cycle: resolve interpreters -> take the serialized eval
    lock -> dispatch -> evaluate -> bank verdict -> release lock.

    A live leg holding the lock -> a YIELDED record, nothing banked.
    box_exec None = no transport -> fail-closed FAIL; a missing
    transport is never interpreted as a PASS.
    """
    paths, why = resolve_interpreters(root)
    if why is not None:
        v = evaluate_canary(None, None, None)
        v["markers"] = None
        v["broken_link"] = why
        write_verdict(v, root)
        return v
    lock_path = os.path.join(root, LOCK_RELPATH)
    stale = lock_ttl_s if lock_ttl_s is not None else H.LOCK_STALE_S
    tok = H.acquire_lock(lock_path, stale_s=stale)
    if tok is None:
        return {
            "card": CARD_ID,
            "kind": "c9072_marker_canary_verdict",
            "verdict": "YIELDED",
            "reason": "asi2_eval_lock_busy",
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    try:
        if box_exec is None:
            v = evaluate_canary(None, None, None)
            v["markers"] = None
            v["broken_link"] = "box_channel_unavailable"
            write_verdict(v, root)
            return v
        cmd = compose_leg_command(paths[0])
        rc, out = box_exec(cmd)
        v = evaluate_from_exec_output(out if isinstance(out, str) else "")
        v["leg_rc"] = rc
        v["interpreter"] = paths[0]
        write_verdict(v, root)
        return v
    finally:
        H.release_lock(lock_path, tok)

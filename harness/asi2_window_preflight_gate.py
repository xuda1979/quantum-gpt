#!/usr/bin/env python3
"""C-9071: ASI2 window preflight gate -- go/no-go artifact, fail-closed.

The C-9061 sentinel is detect-only BY DESIGN (window_open.json names the
C-9029 requeue path as its fire side). That fire side had NO preflight
gate: the 07:58:46Z window-open requeue burned the scarce console-gated
window with 0 slices (07:39Z exit 1 pre-dispatch; c9029_sdk_diag 07:46Z:
qiskit/pennylane/cirq absent from EVERY ASI2 interpreter). This module is
the gate the fire side was missing -- and NOTHING more:

  - judge only, never measure: the SDK positive control belongs to
    C-9066, box parity to C-9051, the truncation ceiling to C-9038. This
    gate never runs interpreters, never probes the box, never imports
    transport machinery -- it reads their banked artifacts.
  - GO requires window_open.json (artifact=="window_open", fresh within
    WINDOW_FRESH_S) PLUS all three named preflight artifacts green; the
    C-9038 check re-hashes the runner the box will execute and demands
    its CURRENT sha256+mtime equal the proven pins (B-223: proven in a
    different file is not proven).
  - any missing/malformed/stale input -> SKIP artifact naming EVERY unmet
    preflight; the consuming card then keeps the leg WAITING (requeued),
    never bounced. The gate itself never writes the queue and never
    starts anything.
  - every verdict (SKIP and GO) lands one EVENTS.jsonl event
    (kind="c9071_window_gate") via harness_lib.event.
  - require_go(ctx) is the dispatch seam: the C-9029 launch path calls it
    before any slice dispatch; GateSkip carries the named unmet map.

Artifact convention (preflight_dir):
  C-9066_sdk_positive_control.json  artifact="sdk_positive_control",
                                    ok=true, interpreters[*] all import
                                    qiskit/pennylane/cirq + control_rc==0
  C-9051_parity.json                artifact="parity",
                                    verdict="PARITY-OK", runner_sha256 pins
  C-9038_ceiling.json               artifact="ceiling", max_new_tokens>0,
                                    proven_pass=true, runner=<repo-relpath>,
                                    runner_sha256, runner_mtime

Gate artifacts (gate_dir): window_gate_go.json | window_gate_skip.json.
CLI: --evaluate; exit 0=GO, 5=SKIP (distinct, never a launch).
Complement to C-9067 (rehearses the launch sequence Mac-side against a
mock window; never gates this one).
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_lib as H  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CARD_ID = "C-9071"
WINDOW_FRESH_S = 1800.0  # measured: ASI2 windows degraded ~13 min after open
RC_GO, RC_SKIP = 0, 5
GO_NAME = "window_gate_go.json"
SKIP_NAME = "window_gate_skip.json"


class GateSkip(Exception):
    """Dispatch seam refusal: .unmet maps every unmet preflight to reason."""

    def __init__(self, unmet):
        self.unmet = dict(unmet)
        super().__init__(CARD_ID + " SKIP: " + json.dumps(self.unmet, sort_keys=True))


def make_ctx(
    window_dir,
    preflight_dir,
    gate_dir,
    state_dir,
    runner_root=None,
    clock=time.time,
    window_fresh_s=WINDOW_FRESH_S,
):
    """All I/O and time injected; the suite never touches live state."""
    return dict(
        window_dir=str(window_dir),
        preflight_dir=str(preflight_dir),
        gate_dir=str(gate_dir),
        state_dir=str(state_dir),
        runner_root=str(runner_root) if runner_root else str(ROOT),
        clock=clock,
        window_fresh_s=float(window_fresh_s),
    )


def _load(path):
    """(doc, None) | (None, "artifact_missing" | "unreadable"). Fail closed."""
    try:
        return json.loads(Path(path).read_text()), None
    except FileNotFoundError:
        return None, "artifact_missing"
    except Exception:
        return None, "unreadable"


def _parse_iso(ts):
    try:
        return (
            datetime.strptime(str(ts), "%Y-%m-%dT%H:%M:%SZ")
            .replace(tzinfo=timezone.utc)
            .timestamp()
        )
    except Exception:
        return None


# --------------------------------------------------------- preflight judges
# Named reasons ONLY; every reason string is asserted by the C-9071 suite.


def _check_c9066(doc):
    """SDK positive control (artifact OWNED by C-9066): every holdout
    interpreter imports qiskit+pennylane+cirq and the control round-trip
    succeeded."""
    if not isinstance(doc, dict):
        return "malformed"
    if doc.get("artifact") != "sdk_positive_control":
        return "artifact_mismatch"
    if doc.get("ok") is not True:
        return "ok_not_true"
    inter = doc.get("interpreters")
    if not isinstance(inter, list) or not inter:
        return "interpreters_missing"
    for it in inter:
        if not isinstance(it, dict):
            return "interpreter_malformed"
        if not (
            it.get("qiskit") is True
            and it.get("pennylane") is True
            and it.get("cirq") is True
            and it.get("control_rc") == 0
        ):
            return "interpreter_control_failed"
    return None


def _check_c9051(doc):
    """Box parity (artifact OWNED by C-9051): verdict must be the literal
    PARITY-OK and carry runner sha pins."""
    if not isinstance(doc, dict):
        return "malformed"
    if doc.get("artifact") != "parity":
        return "artifact_mismatch"
    if doc.get("verdict") != "PARITY-OK":
        return "verdict_not_PARITY-OK"
    pins = doc.get("runner_sha256")
    if not isinstance(pins, dict) or not pins:
        return "sha_pins_missing"
    return None


def _check_c9038(doc, ctx):
    """Truncation ceiling (artifact OWNED by C-9038) + B-223 drift check:
    the proven runner pins must still describe the file on disk NOW."""
    if not isinstance(doc, dict):
        return "malformed"
    if doc.get("artifact") != "ceiling":
        return "artifact_mismatch"
    cap = doc.get("max_new_tokens")
    if not isinstance(cap, int) or cap <= 0:
        return "ceiling_missing"
    if doc.get("proven_pass") is not True:
        return "not_proven"
    rel = doc.get("runner")
    if not isinstance(rel, str) or not rel.strip():
        return "runner_unnamed"
    sha = doc.get("runner_sha256")
    if not isinstance(sha, str) or len(sha) != 64:
        return "runner_sha_missing"
    mtime = doc.get("runner_mtime")
    if not isinstance(mtime, (int, float)):
        return "runner_mtime_missing"
    path = Path(ctx["runner_root"]) / rel
    if not path.is_file():
        return "runner_missing"
    import hashlib as _h

    got_sha = _h.sha256(path.read_bytes()).hexdigest()
    if got_sha.lower() != sha.lower():
        return "runner_sha_drift"
    if abs(path.stat().st_mtime - float(mtime)) > 1e-6:
        return "runner_mtime_drift"
    return None


PREFLIGHTS = (
    (
        "c9066_sdk_positive_control",
        "C-9066_sdk_positive_control.json",
        lambda doc, ctx: _check_c9066(doc),
    ),
    ("c9051_parity_ok", "C-9051_parity.json", lambda doc, ctx: _check_c9051(doc)),
    ("c9038_ceiling", "C-9038_ceiling.json", _check_c9038),
)


# --------------------------------------------------------------- evaluate


def evaluate(ctx):
    """One pass -> (verdict, artifact_path|None, detail). Never raises for
    an unmet input; SKIP names EVERY unmet preflight."""
    unmet = {}
    window_summary = dict(generated_utc=None, pid=None, artifact=None)
    wdoc, err = _load(Path(ctx["window_dir"]) / "window_open.json")
    if err == "artifact_missing":
        unmet["window"] = "window_open_missing"
    elif err:
        unmet["window"] = "window_open_unreadable"
    elif not isinstance(wdoc, dict) or wdoc.get("artifact") != "window_open":
        unmet["window"] = "window_not_open"
    else:
        window_summary["artifact"] = "window_open"
        window_summary["generated_utc"] = wdoc.get("generated_utc")
        bar = wdoc.get("bar") if isinstance(wdoc.get("bar"), dict) else {}
        window_summary["pid"] = bar.get("pid")
        ts = _parse_iso(wdoc.get("generated_utc"))
        if ts is None:
            unmet["window"] = "window_open_ts_unparsable"
        elif ctx["clock"]() - ts > ctx["window_fresh_s"]:
            unmet["window"] = "window_open_stale"
    pins = {}
    for key, fname, checker in PREFLIGHTS:
        doc, err = _load(Path(ctx["preflight_dir"]) / fname)
        if err:
            unmet[key] = err
            continue
        pins[key] = doc
        reason = checker(doc, ctx)
        if reason:
            unmet[key] = reason
    verdict = "SKIP" if unmet else "GO"
    art_name = GO_NAME if verdict == "GO" else SKIP_NAME
    payload = dict(
        card=CARD_ID,
        artifact="window_gate",
        verdict=verdict,
        generated_utc=H.now_iso(),
        window=window_summary,
        window_fresh_s=ctx["window_fresh_s"],
        unmet=dict(unmet),
        preflights=pins if verdict == "GO" else {},
        consumer=dict(
            card="C-9029",
            action="require_go-before-dispatch",
            note=(
                "GO = dispatch may proceed; SKIP = leg stays WAITING/"
                "requeued until preflights turn green -- never bounced;"
                " this gate measures nothing and starts nothing"
            ),
        ),
    )
    out = Path(ctx["gate_dir"])
    out.mkdir(parents=True, exist_ok=True)
    path = out / art_name
    path.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
    H.event(
        ctx["state_dir"],
        "c9071_window_gate",
        dict(
            verdict=verdict,
            unmet=dict(unmet),
            window_pid=window_summary.get("pid"),
            artifact=str(path),
        ),
    )
    return verdict, str(path), dict(unmet=unmet, payload=payload)


def require_go(ctx):
    """Dispatch seam for the C-9029 launch path: GO artifact dict, or
    GateSkip(unmet). NEVER starts anything itself."""
    verdict, _path, detail = evaluate(ctx)
    if verdict != "GO":
        raise GateSkip(detail["unmet"])
    return detail["payload"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=CARD_ID + " ASI2 window preflight gate (judge-only)")
    ap.add_argument("--window-dir", default=str(ROOT / "harness/state/c9061"))
    ap.add_argument("--preflight-dir", default=str(ROOT / "harness/state/preflights"))
    ap.add_argument("--gate-dir", default=str(ROOT / "harness/state/c9071"))
    ap.add_argument("--state-dir", default=str(ROOT / "harness/state"))
    ap.add_argument("--runner-root", default=str(ROOT))
    ap.add_argument("--window-fresh-s", type=float, default=WINDOW_FRESH_S)
    args = ap.parse_args(argv)
    ctx = make_ctx(
        args.window_dir,
        args.preflight_dir,
        args.gate_dir,
        args.state_dir,
        runner_root=args.runner_root,
        window_fresh_s=args.window_fresh_s,
    )
    verdict, path, detail = evaluate(ctx)
    print("c9071: {} {} unmet={}".format(verdict, path, json.dumps(detail["unmet"], sort_keys=True)))
    return RC_GO if verdict == "GO" else RC_SKIP


if __name__ == "__main__":
    sys.exit(main())

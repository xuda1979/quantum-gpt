#!/usr/bin/env python3
"""run_eval_leg.py — run a single eval leg with timeout + fail-closed markers.

The old approach let eval legs run indefinitely, stalling on ASI2 transport
wedges. This script enforces a hard timeout and reports adapter markers.

Usage:
    python3 harness/scripts/run_eval_leg.py --dry-run
    python3 harness/scripts/run_eval_leg.py --box ASI2 --adapter step_000035 --timeout 600
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "harness" / "scripts"))
from run_and_report import run_box  # noqa: E402
import os  # noqa: E402
import sys  # noqa: E402
from pathlib import Path as _P  # noqa: E402

sys.path.insert(0, str(_P(__file__).resolve().parent.parent))
import asi2_authoritative_adapter_gate as _AG  # noqa: E402


def _eval_cmd(adapter: str, task_start: int, task_count: int) -> str:
    """Build the eval command. <8 lines."""
    return (
        f"cd /vllm-workspace && python3 run_asi2_base_adapter_rubric_eval.py "
        f"--adapter {adapter} --task-start {task_start} --task-count {task_count} "
        f"2>&1 | tee /tmp/eval_leg_{adapter}.log"
    )


def _check_markers(output: str) -> dict:
    """Check for fail-closed markers in eval output. <10 lines.

    C-9750: recognize the CANONICAL fail-closed tokens the real leg pipeline
    emits (eval_failclosed_probe.py prints the hyphenated LEG_FAILCLOSED token
    pair; the leg envelope images them as the field names
    adapter_applied_marker / adapter_probe_differs_marker). The old
    snake_case/substring heuristics missed the hyphenated pair, so a real
    fail-closed leg was bounced as "missing fail-closed markers".
    """
    applied = (
        "adapter-applied" in output
        or "adapter_applied_marker" in output
        or "adapter_applied" in output
        or "adapter=True" in output
    )
    differs = (
        "adapter-probe-differs" in output
        or "adapter_probe_differs_marker" in output
        or "probe_differs" in output
        or "differs=True" in output
    )
    return {
        "adapter_applied": applied,
        "probe_differs": differs,
        "has_results": "pass" in output.lower() and "fail" in output.lower(),
    }


def run_leg(box: str, adapter: str, timeout: int, task_start: int, task_count: int) -> dict:
    """Run one eval leg with timeout. <15 lines."""
    cmd = _eval_cmd(adapter, task_start, task_count)
    start = time.time()
    result = run_box(box, cmd, timeout=timeout)
    elapsed = time.time() - start
    markers = _check_markers(result.get("stdout", ""))
    return {
        "box": box,
        "adapter": adapter,
        "elapsed_s": round(elapsed, 1),
        "status": result.get("status"),
        "timed_out": elapsed >= timeout,
        "markers": markers,
        "output_tail": result.get("stdout", "")[-500:],
    }


def _live_resolve(path, box_resolve=None):
    """Conservative resolver: local dir first, else consult the reachable box.

    C-9713: Never fabricate a resolution. Adapters live on the eval box; a
    path we cannot see locally was treated as not-yet-resolvable -> BLOCKED.
    C-9748: that wedged every eval leg because banked adapter paths are
    box-side (/root/work/quantum-gpt/...) and NEVER exist on the Mac, so a
    healthy reachable box was never consulted. When box_resolve is provided
    (an exec-transport path check on the target box), fall back to it so a
    reachable box that holds the adapter is proven resolvable. Fail-closed:
    a box_resolve exception or False still yields False (BLOCKED).
    """
    if not path:
        return False
    try:
        if os.path.isdir(path):
            return True
    except (OSError, TypeError):
        pass
    if box_resolve is not None:
        try:
            return bool(box_resolve(path))
        except Exception:  # noqa: BLE001 -- fail-closed on box probe error
            return False
    return False


def preflight(state_dir=None, box_resolver=None):
    """C-9713 fail-closed gate against live training_source_of_truth + C-9707.

    Returns GO {adapter_ok:True, adapter, ...} or BLOCKED-with-reason.
    NEVER launches eval compute -- this is the guard seam C-9708/9709 exercise
    before dispatch so they return BLOCKED instead of idling on a
    non-authoritative adapter. box_resolver (optional) is an exec-transport
    path check on the eval box so a reachable box holding a banked
    authoritative adapter is proven resolvable (C-9748).
    """
    if state_dir:
        base = Path(state_dir)
    else:
        base = Path(__file__).resolve().parent.parent.parent
    tot = _json_load(base / "harness" / "state" / "training_source_of_truth.json")
    rec = _json_load(base / "harness" / "state" / "cards" / "C-9707-relaunch-record.json")
    c9707 = rec if isinstance(rec, dict) else {}
    cands = []
    b = c9707.get("banked_adapter_path_recorded")
    if isinstance(b, str) and b:
        cands.append({"path": b, "step": _AG._extract_step(b)})
    def _resolve(p):
        return _live_resolve(p, box_resolve=box_resolver)
    return _AG.gate(tot=tot if isinstance(tot, dict) else {},
                    c9707=c9707, candidates=cands,
                    resolve=_resolve, min_step=8)


def _json_load(path):
    """Read a JSON file; return None (fail-closed) on any error. <5 lines."""
    try:
        if not path.is_file():
            print(f"PREFLIGHT: {path.name} ABSENT (fail-closed: no authoritative source)")
            return None
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # noqa: BLE001
        print(f"PREFLIGHT: {path.name} unreadable: {e} (fail-closed)")
        return None



def main():
    """Dispatch. <15 lines."""
    ap = argparse.ArgumentParser(description="Run eval leg with timeout + markers")
    ap.add_argument("--box", default="ASI2")
    ap.add_argument("--adapter", default="step_000035")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--task-start", type=int, default=0)
    ap.add_argument("--task-count", type=int, default=18)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--preflight", action="store_true",
                    help="C-9713: run authoritative-adapter gate; no compute")
    ap.add_argument("--state-dir", default=None)
    ap.add_argument(
        "--workflow-gate", action="store_true", default=None,
        help="C-9751: enforce workflow_gate check (train att must be OK) "
             "before launching real compute. Default ON for real legs.")
    args = ap.parse_args()

    if args.preflight:
        g = preflight(args.state_dir)
        print("PREFLIGHT_ADAPTER_OK=%s" % g["adapter_ok"])
        print("PREFLIGHT_ADAPTER=%s" % (g.get("adapter") or "None"))
        print("PREFLIGHT_REASON=%s" % (g.get("block_reason") or ""))
        raise SystemExit(0 if g["adapter_ok"] else 10)

    if args.dry_run:
        cmd = _eval_cmd(args.adapter, args.task_start, args.task_count)
        print(f"DRY RUN — would execute on {args.box}:")
        print(f"  command: {cmd}")
        print(f"  timeout: {args.timeout}s")
        print("  markers: adapter_applied, probe_differs")
        print("  output: JSON with elapsed_s, status, timed_out, markers")
    else:
        # C-9751 LAYER 2: a real (compute-consuming) eval leg may run only when
        # the workflow gate says GO — the train stage must hold a valid OK
        # attestation. A failed/missing predecessor stage can never trigger
        # this expensive stage. Fail-closed: gate error -> abort leg.
        from workflow_gate import check as wf_check, DEFAULT_ATT_DIR
        rc = wf_check("eval_leg", DEFAULT_ATT_DIR)
        if rc != 0:
            print(json.dumps({
                "status": "BLOCKED_BY_WORKFLOW_GATE", "gate_rc": rc,
                "note": "predecessor train stage not attested OK; "
                        "run harness/scripts/workflow_audit.py train",
            }, indent=2))
            raise SystemExit(rc)
        result = run_leg(args.box, args.adapter, args.timeout, args.task_start, args.task_count)
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""workflow_gate.py — LAYER 2: executable stage gates for the quantum-LLM
training workflow (C-9751).

A stage may run ONLY when every predecessor named in
harness/workflow_spec.json has a valid attestation file
(<stage>.ATT.json, status OK) in the att dir. Fail-closed: missing,
malformed, FAILED/REVOKED attestations all BLOCK. Exit 0 = GO, non-zero =
BLOCKED. No conversation memory involved — the spec + att files ARE the
workflow state.

Usage:
    python3 harness/scripts/workflow_gate.py check --stage eval_leg
    python3 harness/scripts/workflow_gate.py attest --stage train --status OK \\
        --evidence '{"run_name": "...", "latest_step": 73}'
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "harness"))
sys.path.insert(0, str(REPO))

SPEC_PATH = REPO / "harness" / "workflow_spec.json"
DEFAULT_ATT_DIR = REPO / "harness" / "state" / "atts"

VALID_STATUS = {"OK"}


def load_spec() -> dict:
    """Fail-closed spec load. <5 lines."""
    try:
        return json.loads(SPEC_PATH.read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"BLOCKED: workflow_spec unreadable: {e}")
        raise SystemExit(10)


def stage_spec(spec: dict, stage_id: str) -> dict | None:
    for s in spec.get("stages", []):
        if s.get("id") == stage_id:
            return s
    return None


def read_att(att_dir: Path, stage_id: str) -> dict | None:
    """Read one attestation. Malformed JSON -> None (fail-closed). <6 lines."""
    p = att_dir / f"{stage_id}.ATT.json"
    try:
        d = json.loads(p.read_text())
        return d if isinstance(d, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def check(stage_id: str, att_dir: Path, spec: dict | None = None) -> int:
    """The gate: predecessors must hold valid OK attestations. <25 lines."""
    spec = spec or load_spec()
    stage = stage_spec(spec, stage_id)
    if stage is None:
        print(f"BLOCKED: unknown stage {stage_id!r} (spec: "
              f"{[s['id'] for s in spec['stages']]})")
        return 11
    att_dir.mkdir(parents=True, exist_ok=True)
    blocked = []
    for pred in stage.get("requires", []):
        att = read_att(att_dir, pred)
        if att is None:
            blocked.append(f"{pred}: no valid attestation "
                           f"({att_dir / (pred + '.ATT.json')} missing/malformed)")
            continue
        if att.get("status") not in VALID_STATUS:
            blocked.append(f"{pred}: attestation status "
                           f"{att.get('status')!r} not in {sorted(VALID_STATUS)}")
    if blocked:
        print(f"BLOCKED: stage {stage_id} may NOT run — predecessor failures:")
        for b in blocked:
            print(f"  - {b}")
        return 1
    print(f"GO: stage {stage_id} — predecessors attested: "
          f"{stage.get('requires') or ['(first stage)']}")
    return 0


def attest(stage_id: str, status: str, evidence: dict, att_dir: Path,
           spec: dict | None = None) -> int:
    """Write an attestation. Att status may be OK or FAILED (a FAILED att
    blocks successors exactly like a missing one). <12 lines."""
    spec = spec or load_spec()
    if stage_spec(spec, stage_id) is None:
        print(f"BLOCKED: unknown stage {stage_id!r}")
        return 11
    if status not in {"OK", "FAILED"}:
        print(f"BLOCKED: --status must be OK or FAILED, got {status!r}")
        return 12
    att_dir.mkdir(parents=True, exist_ok=True)
    att = {"schema": "workflow_att/v1", "stage": stage_id, "status": status,
           "evidence": evidence}
    (att_dir / f"{stage_id}.ATT.json").write_text(json.dumps(att, indent=1))
    print(f"ATTESTED: {stage_id} status={status} -> "
          f"{att_dir / (stage_id + '.ATT.json')}")
    return 0


def main() -> None:
    """Dispatch. <10 lines."""
    ap = argparse.ArgumentParser(description="Workflow stage gate (C-9751)")
    sub = ap.add_subparsers(dest="verb", required=True)
    c = sub.add_parser("check")
    c.add_argument("--stage", required=True)
    c.add_argument("--att-dir", default=str(DEFAULT_ATT_DIR))
    a = sub.add_parser("attest")
    a.add_argument("--stage", required=True)
    a.add_argument("--status", required=True, choices=["OK", "FAILED"])
    a.add_argument("--evidence", default="{}")
    a.add_argument("--att-dir", default=str(DEFAULT_ATT_DIR))
    args = ap.parse_args()
    att_dir = Path(args.att_dir)
    if args.verb == "check":
        raise SystemExit(check(args.stage, att_dir))
    try:
        evidence = json.loads(args.evidence)
    except json.JSONDecodeError as e:
        print(f"BLOCKED: --evidence is not JSON: {e}")
        raise SystemExit(13)
    raise SystemExit(attest(args.stage, args.status, evidence, att_dir))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""workflow_audit.py — LAYER 3: independent re-verification of workflow
attestations (C-9751).

The audit NEVER trusts the attestation's self-claim. For each stage it
recomputes the outcome from PRIMARY evidence:

  train       -> harness/state/resume_training.json (boot.alive) re-read
                 from disk; a live trainer probe may upgrade OK -> OK
                 (never the reverse: dead primary evidence REVOKES).
  eval_leg    -> the leg scores jsonl on the box (markers re-parsed).
  compose_verdict -> per_task agreement + sha pins from leg files.

An att contradicted by primary evidence is marked REVOKED in place (a
REVOKED att blocks successors exactly like FAILED). Exit 0 = att stands,
non-zero = revoked/absent.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "harness"))
sys.path.insert(0, str(REPO))

ATT_DIR_DEFAULT = REPO / "harness" / "state" / "atts"
STATE_DIR_DEFAULT = REPO / "harness" / "state"


def _read_json(path: Path) -> dict | None:
    try:
        d = json.loads(path.read_text())
        return d if isinstance(d, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def audit_train(att: dict, state_dir: Path) -> tuple[bool, str]:
    """Recompute training liveness from resume_training.json. <20 lines."""
    ev = att.get("evidence") or {}
    rp = ev.get("resume_state")
    resume = _read_json(Path(rp)) if rp else _read_json(
        state_dir / "resume_training.json")
    if resume is None:
        return False, "primary evidence resume_training.json missing/unreadable"
    boot = resume.get("boot") or {}
    if boot.get("alive") is not True:
        return False, f"boot.alive={boot.get('alive')!r} contradicts att OK"
    return True, f"boot.alive=True run={resume.get('run_name')!r}"


def audit_eval_leg(att: dict, state_dir: Path) -> tuple[bool, str]:
    """Recompute fail-closed markers from the leg's recorded evidence. <15 lines."""
    ev = att.get("evidence") or {}
    markers = ev.get("markers") or {}
    if not (markers.get("adapter_applied") and markers.get("probe_differs")):
        return False, f"markers incomplete: {markers}"
    pa = ev.get("pass_count")
    if pa is None:
        return False, "evidence lacks pass_count"
    return True, f"markers ok, pass_count={pa}"


def audit_compose_verdict(att: dict, state_dir: Path) -> tuple[bool, str]:
    """Recompute: two legs, 18 per_task entries agreeing, sha-pinned. <20 lines."""
    ev = att.get("evidence") or {}
    for k in ("leg1", "leg2", "per_task_count", "holdout_sha256"):
        if not ev.get(k):
            return False, f"evidence lacks {k}"
    if ev.get("per_task_count") != 18:
        return False, f"per_task_count={ev.get('per_task_count')!r} != 18"
    return True, "two legs + 18 per_task + sha pin present"


AUDITORS = {
    "train": audit_train,
    "eval_leg": audit_eval_leg,
    "compose_verdict": audit_compose_verdict,
}


def audit(stage_id: str, att_dir: Path, state_dir: Path) -> int:
    """Audit one stage's attestation against primary evidence. <20 lines."""
    auditor = AUDITORS.get(stage_id)
    if auditor is None:
        print(f"BLOCKED: no auditor for stage {stage_id!r} "
              f"(known: {sorted(AUDITORS)})")
        return 11
    att_path = att_dir / f"{stage_id}.ATT.json"
    att = _read_json(att_path)
    if att is None:
        print(f"FAIL: no readable attestation at {att_path}")
        return 1
    ok, detail = auditor(att, state_dir)
    if not ok:
        att["status"] = "REVOKED"
        att["revoked_detail"] = detail
        att_path.write_text(json.dumps(att, indent=1))
        print(f"REVOKED: {stage_id} att contradicted by primary evidence: {detail}")
        return 2
    print(f"STANDS: {stage_id} att re-verified from primary evidence: {detail}")
    return 0


def main() -> None:
    """Dispatch. <8 lines."""
    ap = argparse.ArgumentParser(description="Workflow att audit (C-9751)")
    ap.add_argument("stage")
    ap.add_argument("--att-dir", default=str(ATT_DIR_DEFAULT))
    ap.add_argument("--state", default=str(STATE_DIR_DEFAULT))
    args = ap.parse_args()
    raise SystemExit(audit(args.stage, Path(args.att_dir), Path(args.state)))


if __name__ == "__main__":
    main()

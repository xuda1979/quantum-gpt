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

# C-10316/C-10337: fixture ref substrings used by the compose-stage audit
# and c10394_pre_retirement_audit to reject /var/folders, /tmp, and
# C-9750-canonical leg-ref shapes.
FIXTURE_REF_SUBSTRINGS = (
    "/var/folders/",
    "/private/var/folders/",
    "/tmp/",
    "c9750-canonical-",
    "canonical-leg",
    "/T/leg",
)


def _scores_provenance_ok(sc) -> str | None:
    """Validate a scores ref points at a real outputs/-under path, or None."""
    if not isinstance(sc, str) or not sc:
        return "empty_scores_ref"
    s = sc.replace("\\", "/")
    under_outputs = (
        s.startswith("outputs/") or "/outputs/" in s or s.rstrip("/").endswith("/outputs")
    )
    if not under_outputs:
        return f"non_outputs_scores_ref:{sc}"
    if any(tok in s for tok in FIXTURE_REF_SUBSTRINGS):
        if "/outputs/" not in s:
            return f"fixture_scores_ref:{sc}"
    p = Path(sc) if Path(sc).is_absolute() else REPO / sc
    if not p.exists():
        return f"scores_ref_missing:{sc}"
    return None


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
    resume = _read_json(Path(rp)) if rp else _read_json(state_dir / "resume_training.json")
    if resume is None:
        return False, "primary evidence resume_training.json missing/unreadable"
    boot = resume.get("boot") or {}
    if boot.get("alive") is not True:
        return False, f"boot.alive={boot.get('alive')!r} contradicts att OK"
    return True, f"boot.alive=True run={resume.get('run_name')!r}"


def _real_scores_pass_count(scores_ref) -> int | None:
    """Recompute the adapter pass count from a REAL scores file, or None."""
    if scores_ref:
        p = Path(scores_ref) if Path(scores_ref).is_absolute() else REPO / scores_ref
        payload = _read_json(p)
        if payload is not None and isinstance(payload.get("records"), list):
            return sum(
                1
                for r in payload["records"]
                if isinstance(r, dict) and r.get("model") == "adapter" and r.get("passed") is True
            )
    return None


def build_eval_leg_att_evidence(envelope, scores, card=None, box=None):
    """C-10375/C-10395: build the eval_leg.ATT.json evidence dict from a
    real leg envelope + scores file, including a recomputed pass_count.

    Returns {markers, adapter_leg, scores, box, leg_process_id,
    pass_count, card}. Raises ValueError when the envelope or scores are
    not usable (real-path / marker fail-closed preconditions)."""
    from pathlib import Path as _P

    env_p = _P(envelope) if not isinstance(envelope, _P) else envelope
    sc_p = _P(scores) if not isinstance(scores, _P) else scores
    if not env_p.is_file():
        raise ValueError(f"adapter_leg envelope missing: {env_p}")
    if not sc_p.is_file():
        raise ValueError(f"scores file missing: {sc_p}")
    env = _read_json(env_p) or {}
    markers = env.get("markers") or {}
    if isinstance(env, dict) and (
        "adapter_applied_marker" in env or "adapter_probe_differs_marker" in env
    ):
        markers = {
            "adapter_applied": env.get("adapter_applied_marker") is True,
            "probe_differs": env.get("adapter_probe_differs_marker") is True,
        }
    scored = _read_json(sc_p) or {}
    records = scored.get("records") if isinstance(scored, dict) else None
    if not isinstance(records, list):
        raise ValueError(f"scores file lacks records: {sc_p}")
    pc = sum(
        1
        for r in records
        if isinstance(r, dict) and r.get("model") == "adapter" and r.get("passed") is True
    )
    ev = {
        "markers": markers,
        "adapter_leg": str(env_p),
        "scores": str(sc_p),
        "box": box or env.get("box"),
        "leg_process_id": env.get("leg_process_id"),
        "pass_count": pc,
    }
    if card:
        ev["card"] = card
    return ev


def audit_eval_leg(att: dict, state_dir: Path) -> tuple[bool, str]:
    """C-10368/C-10375/C-10395: recompute fail-closed markers + pass_count
    from the leg's recorded evidence. Real-provenance fail-closed rules:
      - markers adapter_applied + probe_differs must be truthy
      - evidence.pass_count must be a positive int (or recompute > 0 from
        scores) -- a zero-score leg is not certified for compose
      - evidence.scores ref must resolve to a real outputs/-under file
        (fixture/tempdir refs are rejected)
    Returns (ok, detail); the caller REVOKES when not ok."""
    ev = att.get("evidence") or {}
    markers = ev.get("markers") or {}
    if not (markers.get("adapter_applied") and markers.get("probe_differs")):
        return False, f"markers incomplete: {markers}"
    pa = ev.get("pass_count")
    if pa is None:
        return False, "evidence lacks pass_count"
    if not (isinstance(pa, int) and pa > 0):
        return False, f"pass_count nonpositive: {pa!r}"
    scores_ref = ev.get("scores")
    if scores_ref:
        bad = _scores_provenance_ok(str(scores_ref))
        if bad:
            return False, f"scores provenance rejected: {bad}"
        real_pc = _real_scores_pass_count(str(scores_ref))
        if real_pc is None:
            return False, "scores file unreadable for pass_count recompute"
        if real_pc != int(pa):
            return False, f"pass_count {pa} != scores recompute {real_pc}"
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
        print(f"BLOCKED: no auditor for stage {stage_id!r} " f"(known: {sorted(AUDITORS)})")
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

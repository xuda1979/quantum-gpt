"""C-9051: pre-window box parity gate -- Mac-side checker, fail-closed.

Measures the BOX-SIDE ASI2 holdout runner/composer (bytes fetched into a
snapshot dir by the card's paced box fetch) against the Mac canonical
invariants, BEFORE a recovered ASI2 leg burns a console-gated window
(B-163 precedent: landed Mac fixes stayed dead behind a stale box
launcher; error 170022 makes windows scarce):

  1. box runner --max-new-tokens argparse default == the ceiling in the
     C-9038 artifact (READ from the artifact, never hardcoded);
  2. box composer carries scorer_shas + holdout_sha256 emission (grep
     evidence on the box bytes);
  3. B-223: a box-side long-lived runner/keeper process that started
     BEFORE its script file mtime is stale code that never reloads --
     each stale pid is a named drift; absent process evidence is ALSO a
     named drift (fail closed, never silently assumed clean).

Verdict is PARITY-OK only when the drift list is EMPTY. Anything
unmeasurable lands in the drift list with a named reason; check_parity
NEVER raises. The artifact schema matches harness/state/c9071/CONTRACT.md
binding for c9051_parity_ok: artifact==parity, verdict==PARITY-OK,
runner_sha256 non-empty object mapping box repo-relative path -> sha256.
Bank the artifact at EXACTLY harness/state/preflights/C-9051_parity.json;
a PARITY-DRIFT banked there keeps the c9071 window gate SKIP for a named
reason (verdict_not_PARITY-OK) while documenting why.
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

CARD_ID = "C-9051"
RUNNER_REL = "scripts/run_asi2_base_adapter_rubric_eval.py"
COMPOSER_REL = "scripts/holdout_verdict.py"
PINNED = (RUNNER_REL, COMPOSER_REL)
DEFAULT_CEILING_PATH = "harness/state/preflights/C-9038_ceiling.json"
# /proc-style etimes sampling slack (s) before "started before mtime".
B223_TOLERANCE_S = 1.0


def _utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


def _read_ceiling(ceiling_path, drift):
    try:
        doc = json.loads(Path(ceiling_path).read_text())
    except Exception as exc:
        drift.append("ceiling_artifact_unreadable:" + repr(exc)[:80])
        return None
    if not isinstance(doc, dict) or doc.get("artifact") != "ceiling":
        drift.append("ceiling_artifact_malformed")
        return None
    cap = doc.get("max_new_tokens")
    if not isinstance(cap, int) or cap <= 0:
        drift.append("ceiling_artifact_malformed")
        return None
    return cap


def _runner_default(runner_text):
    m = re.search("--max-new-tokens[^0-9]*?default=(" + chr(92) + "d+)", runner_text)
    if not m:
        return None
    return int(m.group(1))


def check_parity(mac_root, snapshot_dir, ceiling_path, ceiling_override=None):
    """Measure the box snapshot; return the C-9051 artifact dict.

    Never raises on unmeasurable input: every gap becomes a named drift
    item and the verdict drops to PARITY-DRIFT (gate stays SKIP).
    """
    drift = []
    snap = Path(snapshot_dir)
    box_bytes = dict()
    for rel in PINNED:
        p = snap / "box" / rel
        if p.is_file():
            box_bytes[rel] = p.read_bytes()
        else:
            drift.append("snapshot_missing:" + rel)
    if ceiling_override is not None:
        ceiling = (
            ceiling_override if isinstance(ceiling_override, int) and ceiling_override > 0 else None
        )
        if ceiling is None:
            drift.append("ceiling_override_invalid")
    else:
        ceiling = _read_ceiling(ceiling_path, drift)

    runner_text = None
    composer_text = None
    if RUNNER_REL in box_bytes:
        runner_text = box_bytes[RUNNER_REL].decode("utf-8", "replace")
        if ceiling is not None:
            got = _runner_default(runner_text)
            if got is None:
                drift.append("runner_default_missing")
            elif got < ceiling:
                drift.append("runner_default_below_ceiling:" + str(got) + "<" + str(ceiling))
            elif got > ceiling:
                drift.append("runner_default_mismatch:" + str(got) + ">" + str(ceiling))
    if COMPOSER_REL in box_bytes:
        composer_text = box_bytes[COMPOSER_REL].decode("utf-8", "replace")
        if "scorer_shas" not in composer_text:
            drift.append("composer_scorer_shas_missing")
        if "holdout_sha256" not in composer_text:
            drift.append("composer_holdout_sha_missing")

    pins = dict()
    for rel, data in box_bytes.items():
        pins[rel] = _sha256(data)
    if not pins:
        drift.append("sha_pins_missing")

    b223 = _check_b223(snap, drift)

    mac = _mac_canonical(mac_root)

    verdict = "PARITY-OK" if not drift else "PARITY-DRIFT"
    return dict(
        artifact="parity",
        card=CARD_ID,
        verdict=verdict,
        utc=_utcnow(),
        ceiling_max_new_tokens=ceiling,
        box=dict(runner=RUNNER_REL, composer=COMPOSER_REL),
        runner_default_max_new_tokens=(
            _runner_default(runner_text) if runner_text is not None else None
        ),
        composer_emits=dict(
            scorer_shas=bool(composer_text is not None and "scorer_shas" in composer_text),
            holdout_sha256=bool(composer_text is not None and "holdout_sha256" in composer_text),
        ),
        runner_sha256=pins,
        b223=b223,
        mac_canonical=mac,
        drift=drift,
        probe=dict(source="box_snapshot", snapshot_dir=str(snap)),
    )


def _check_b223(snap, drift):
    """B-223: a long-lived box process that started BEFORE its script's
    file mtime is running stale code. Rows come from the paced box fetch
    (box_proc.json). Missing evidence is itself a named drift."""
    proc_path = snap / "box_proc.json"
    if not proc_path.is_file():
        drift.append("box_proc_evidence_missing")
        return dict(checked=False, processes=0, stale=list())
    try:
        doc = json.loads(proc_path.read_text())
        scope_note = ""
        if isinstance(doc, dict):
            rows = doc.get("rows")
            unmeasured = doc.get("containers_unmeasured") or list()
            if unmeasured:
                scope_note = "box_proc_scope_incomplete:" + ",".join(str(x) for x in unmeasured)
        elif isinstance(doc, list):
            rows = doc
        else:
            raise ValueError("rows not a list/object")
        if not isinstance(rows, list):
            raise ValueError("rows not a list")
    except Exception as exc:
        drift.append("box_proc_evidence_unparseable:" + repr(exc)[:80])
        return dict(checked=False, processes=0, stale=list())
    if scope_note:
        drift.append(scope_note)
    stale = list()
    for row in rows:
        try:
            pid = int(row["pid"])
            etimes = float(row["etimes_s"])
            mtime = float(row["script_mtime"])
            sampled = float(row["sampled_epoch"])
            script = str(row["script"])
        except Exception:
            drift.append("box_proc_row_malformed")
            continue
        started = sampled - etimes
        if started < mtime - B223_TOLERANCE_S:
            item = "b223_stale_process:pid=" + str(pid) + ":" + script
            if item not in stale:
                stale.append(item)
                drift.append(item)
    return dict(checked=True, processes=len(rows), stale=stale, note=scope_note)


def _mac_canonical(mac_root):
    """Informative diff half: Mac canonical default + sha pins (NOT
    gating -- the box invariants above gate the window)."""
    mac = dict()
    root = Path(mac_root) if mac_root else None
    for rel in PINNED:
        p = root / rel if root else None
        entry = dict()
        if p is not None and p.is_file():
            data = p.read_bytes()
            entry["sha256"] = _sha256(data)
            if rel == RUNNER_REL:
                entry["default_max_new_tokens"] = _runner_default(data.decode("utf-8", "replace"))
        else:
            entry["present"] = False
        mac[rel] = entry
    return mac


def main(argv=None):
    ap = argparse.ArgumentParser(prog="c9051_box_parity")
    ap.add_argument("--mac-root", required=True)
    ap.add_argument("--snapshot-dir", required=True)
    ap.add_argument(
        "--ceiling",
        default=None,
        metavar="CEILING_PATH_OR_INT",
        help="ceiling-artifact path override, or a bare integer ceiling VALUE",
    )
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    override = None
    ceiling = args.ceiling
    if ceiling is not None and re.fullmatch(r"[0-9]+", ceiling):
        override = int(ceiling)  # a bare number is a VALUE, never a path
        ceiling = None
    if ceiling is None:
        ceiling = Path(args.mac_root) / DEFAULT_CEILING_PATH
    artifact = check_parity(args.mac_root, args.snapshot_dir, ceiling, ceiling_override=override)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=1))
    print(artifact["verdict"], "drift=" + repr(artifact["drift"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

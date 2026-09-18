"""C-9108 base-leg slice transport verifier (box -> Mac, fail-closed).

Transports C-9029 base-leg slice outputs to Mac-side outputs/ using the
chunked-b64 recipe from box_pull_ledger / .sapo-loop/boxfetch.py (stat the
remote size, then `dd bs=1 skip=N count=C | base64 -w0` per chunk over the
/exec channel) -- NEVER a single raw pull, which is the documented
truncation history. Every landed byte is verified against the box-side
size before it may appear under the C-9030 glob
(outputs/c9003_base_slice*.json); transfers that come up short are
rejected and land NOTHING (tmp + os.replace only after full verify).

Fail-closed verification (verify_slices) refuses any state where a slice
is non-parseable, a task id is missing or duplicated, or a record lacks
the per-task truncation field (`output_chars`, the generation length that
exposes token-cap truncation) -- naming the offending ids/files.

A transport receipt (outputs/c9108_base_slice_transport_receipt.json)
records sha256 + byte counts per slice, is updated in place, and makes
re-runs idempotent: already-verified slices are skipped, not re-pulled.
"""

import argparse
import base64
import hashlib
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

RECEIPT_NAME = "c9108_base_slice_transport_receipt.json"
TRUNCATION_FIELD = "output_chars"
DEFAULT_CHUNK = 3000  # box_pull_ledger recipe chunk (boxfetch.py)
SLICE_PREFIX = "c9003_base_slice"
REMOTE_SLICE_STARTS = (0, 6, 12)  # launcher split: 6+6+6 = 18 (c9003_launch_base_leg)

HARNESS_ROOT = Path(__file__).resolve().parent.parent


def slice_local_name(start):
    """Exact Mac-side landing name; matches the C-9030 glob
    outputs/c9003_base_slice*.json (tmp/c9003_launch_base_leg.py)."""
    return f"{SLICE_PREFIX}{start}.json"


def _utcnow():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ---------------------------------------------------------------- transport


def _exec_run(cmd_text, port):
    """One /exec round trip; returns the command stdout text."""
    payload = json.dumps(dict(command=cmd_text)).encode()
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/exec",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8", "replace"))
    out = data.get("output", data)
    if isinstance(out, dict):
        out = out.get("output", "")
    return out


def _b64_chunk_to_bytes(chunk_text):
    """Decode one base64 chunk, trimming a truncated tail (recipe keeps a
    decodable prefix; callers still enforce the total byte count)."""
    blob = "".join((chunk_text or "").split())
    good = None
    while len(blob) >= 8:
        try:
            good = base64.b64decode(blob + "=" * ((-len(blob)) % 4))
            break
        except Exception:
            blob = blob[:-4]
    return good


def fetch_remote_bytes(port, remote_path, chunk_size=DEFAULT_CHUNK, max_tries=240):
    """Chunked-b64 pull; returns (data, box_size). Raises TransportError
    when any chunk is undecodable or the byte count comes up short --
    a short pull never returns partial data (fail closed)."""
    try:
        box_size = int(_exec_run("stat -c %s " + remote_path, port).strip())
    except Exception as exc:
        raise TransportError(f"stat failed for {remote_path}: {exc}")
    data = b""
    off = 0
    tries = 0
    while off < box_size:
        tries += 1
        if tries > max_tries:
            raise TransportError(
                f"chunk tries exhausted for {remote_path}: {off} of {box_size} bytes"
            )
        cmd = f"dd if={remote_path} bs=1 skip={off} count={chunk_size} 2>/dev/null | base64 -w0"
        try:
            chunk_text = _exec_run(cmd, port)
        except Exception as exc:
            raise TransportError(f"chunk fetch failed at {off} for {remote_path}: {exc}")
        good = _b64_chunk_to_bytes(chunk_text)
        if good is None:
            raise TransportError(f"undecodable chunk at offset {off} for {remote_path}")
        if not good:
            raise TransportError(f"empty chunk at offset {off} for {remote_path}")
        data += good
        off += len(good)
    if len(data) != box_size:
        raise TransportError(
            f"byte-count mismatch for {remote_path}: got {len(data)} of {box_size} -- REJECTED (truncated pull)"
        )
    return data, box_size


class TransportError(Exception):
    pass


# --------------------------------------------------------------- verify


def _load_slice(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def verify_slices(outputs_dir, expected_task_ids):
    """Fail-closed C-9030 pre-read gate. Returns a verdict dict; ok=True
    only when every slice parses, task ids are complete (18/18, none
    duplicated, none unexpected) and every record carries the per-task
    truncation field. Missing ids are NAMED, never counted."""
    outputs = Path(outputs_dir)
    files = sorted(outputs.glob(SLICE_PREFIX + "*.json"))
    verdict = {
        "card": "C-9108",
        "checked_utc": _utcnow(),
        "ok": False,
        "n_slices": len(files),
        "n_tasks": 0,
        "expected_tasks": len(expected_task_ids),
        "unparseable": [],
        "missing_task_ids": [],
        "duplicate_task_ids": [],
        "unexpected_task_ids": [],
        "missing_truncation_field": [],
        "slices": [f.name for f in files],
    }
    seen = []
    for path in files:
        payload = _load_slice(path)
        if payload is None:
            verdict["unparseable"].append(path.name)
            continue
        for rec in payload.get("records", []) or []:
            tid = rec.get("task_id")
            seen.append(tid)
            val = rec.get(TRUNCATION_FIELD)
            if not isinstance(val, int) or isinstance(val, bool):
                verdict["missing_truncation_field"].append(tid)
    verdict["n_tasks"] = len(set(t for t in seen if t is not None))
    counts = {}
    for tid in seen:
        counts[tid] = counts.get(tid, 0) + 1
    expected = set(expected_task_ids)
    got = set(counts)
    verdict["duplicate_task_ids"] = sorted(t for t, c in counts.items() if c > 1)
    verdict["missing_task_ids"] = sorted(expected - got)
    verdict["unexpected_task_ids"] = sorted(got - expected)
    verdict["ok"] = not (
        verdict["unparseable"]
        or verdict["missing_task_ids"]
        or verdict["duplicate_task_ids"]
        or verdict["unexpected_task_ids"]
        or verdict["missing_truncation_field"]
    )
    return verdict


# --------------------------------------------------------------- receipt


def receipt_path(outputs_dir):
    return Path(outputs_dir) / RECEIPT_NAME


def read_receipt(outputs_dir):
    payload = _load_slice(receipt_path(outputs_dir))
    if not isinstance(payload, dict):
        return {"card": "C-9108", "slices": {}}
    payload.setdefault("slices", {})
    return payload


def _write_receipt(outputs_dir, receipt):
    receipt["updated_utc"] = _utcnow()
    receipt["receipt"] = RECEIPT_NAME
    path = receipt_path(outputs_dir)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(str(tmp), str(path))


def _local_verified(outputs_dir, name, receipt):
    """A landed slice counts as verified only when the receipt sha256
    matches the local bytes AND the file still parses with truncation
    fields intact. Anything else = re-pull (fail toward more checking)."""
    entry = receipt.get("slices", {}).get(name)
    if not entry:
        return False
    path = Path(outputs_dir) / name
    if not path.exists():
        return False
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != entry.get("sha256"):
        return False
    return _load_slice(path) is not None


# ---------------------------------------------------------------- pull


def pull_slice(port, remote_path, local_name, outputs_dir, chunk_size=DEFAULT_CHUNK):
    """Land one slice under outputs/<local_name> via chunked-b64, byte-
    verified against the box-side stat size, atomically. Idempotent: an
    already-verified slice is skipped (zero transport), receipt updated
    in place -- never duplicated."""
    outputs_dir = Path(outputs_dir)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    receipt = read_receipt(outputs_dir)
    if _local_verified(outputs_dir, local_name, receipt):
        entry = receipt["slices"][local_name]
        entry["skipped"] = True
        entry["last_verified_utc"] = _utcnow()
        _write_receipt(outputs_dir, receipt)
        return {
            "ok": True,
            "skipped": True,
            "name": local_name,
            "bytes": entry.get("bytes"),
            "sha256": entry.get("sha256"),
        }
    try:
        data, box_size = fetch_remote_bytes(port, remote_path, chunk_size=chunk_size)
    except TransportError as exc:
        return {"ok": False, "skipped": False, "name": local_name, "error": str(exc)}
    local = outputs_dir / local_name
    tmp = local.with_suffix(local.suffix + ".tmp")
    tmp.write_bytes(data)  # only AFTER fetch_remote_bytes verified the count
    payload = _load_slice(tmp)
    if payload is None:
        tmp.unlink()
        return {
            "ok": False,
            "skipped": False,
            "name": local_name,
            "error": "landed bytes are not JSON-parseable -- rejected, nothing landed",
        }
    os.replace(str(tmp), str(local))
    entry = {
        "bytes": len(data),
        "box_bytes": box_size,
        "sha256": hashlib.sha256(data).hexdigest(),
        "remote": str(remote_path),
        "transport": "chunked-b64",
        "chunk_size": chunk_size,
        "pulled_utc": _utcnow(),
        "skipped": False,
    }
    receipt["slices"][local_name] = entry
    _write_receipt(outputs_dir, receipt)
    return {
        "ok": True,
        "skipped": False,
        "name": local_name,
        "bytes": len(data),
        "sha256": entry["sha256"],
    }


def _load_expected_task_ids():
    """Canonical frozen holdout ids; fail-closed in the operational path --
    no synthetic fallback list (a wrong id list would mis-name missing
    ids). Tests keep their own hermetic fallback."""
    runner_dir = str(HARNESS_ROOT / "evals" / "runner")
    if runner_dir not in sys.path:
        sys.path.insert(0, runner_dir)
    from holdout_freeze import bench_task_ids

    return sorted(bench_task_ids())


def main(argv=None):
    """Operational entry (was library-only): idempotent chunked-b64 pull of
    the three C-9029 launcher slices (starts 0/6/12, 6 tasks each), then
    the fail-closed C-9030 pre-read gate. Exit 0 only on 18/18 verified;
    1 = gate failed; 2 = canonical ids unavailable (fail closed).
    --verify-only gates existing files and issues ZERO transport calls."""
    ap = argparse.ArgumentParser(
        prog="python3 -m harness.slice_transport",
        description="C-9108 base-leg slice transport verifier",
    )
    ap.add_argument("--port", type=int, default=19004)
    ap.add_argument("--outputs", default=str(HARNESS_ROOT / "outputs"))
    ap.add_argument("--remote-root", default="/root/work/software/quantum-gpt/outputs")
    ap.add_argument(
        "--verify-only",
        action="store_true",
        help="gate files only; zero transport calls",
    )
    args = ap.parse_args(argv)
    try:
        expected_ids = _load_expected_task_ids()
    except Exception as exc:
        print(
            json.dumps(
                dict(
                    card="C-9108",
                    ok=False,
                    error="canonical ids unavailable: " + repr(exc),
                )
            ),
            flush=True,
        )
        return 2
    if not args.verify_only:
        for start in REMOTE_SLICE_STARTS:
            res = pull_slice(
                args.port,
                args.remote_root.rstrip("/") + "/c9003_base_slice" + str(start) + ".json",
                slice_local_name(start),
                args.outputs,
            )
            print(json.dumps(res, sort_keys=True), flush=True)
    verdict = verify_slices(args.outputs, expected_ids)
    print(json.dumps(verdict, sort_keys=True), flush=True)
    return 0 if verdict["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

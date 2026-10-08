"""C-9063: fail-closed validator for the C-9009 claim-time artifact
target_checkpoint.json.

The artifact is either a PINNED, sha-verified adapter-checkpoint selection
(newest registered checkpoint; step_000097_adapter only as an explicitly
labeled fallback) or an UNRESOLVED_FAIL_CLOSED record that names the blocking
edge. Anything else -- malformed json, missing sha256, unknown step names, a
pinned target inside an unresolved record -- is refused, never defaulted.
"""

import json
import os
import re

CARD_ID = "C-9063"
ARTIFACT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "state", "probes", "target_checkpoint.json"
)
STEP_NAME_RE = re.compile(r"^step_\d{6}_adapter$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SOURCES = ("C-9036-inventory", "C-9050-registration")
STATUSES = ("PINNED", "UNRESOLVED_FAIL_CLOSED")


class TargetCheckpointError(RuntimeError):
    """Fail-closed refusal with a named reason (never a silent default)."""


def _fail(msg):
    raise TargetCheckpointError(CARD_ID + " fail-closed: " + msg)


def _validate_pinned_target(target, where):
    if not isinstance(target, dict):
        _fail(where + " pinned target not an object")
    step = target.get("step")
    if not isinstance(step, str) or not STEP_NAME_RE.match(step):
        _fail(where + f" unknown step name {step!r} (need step_NNNNNN_adapter)")
    path = target.get("path")
    if not isinstance(path, str) or not path.strip():
        _fail(where + " checkpoint path missing/empty")
    sha = target.get("sha256")
    if not isinstance(sha, str) or not SHA256_RE.match(sha):
        _fail(where + f" sha256 missing/malformed (need 64 lowercase hex chars), got {sha!r}")
    if target.get("source") not in SOURCES:
        _fail(where + " source must be one of " + ", ".join(SOURCES))
    return target


def validate_target_checkpoint(art):
    """Validate an artifact dict; return it unchanged or fail closed."""
    if not isinstance(art, dict):
        _fail("artifact not an object")
    status = art.get("status")
    if status not in STATUSES:
        _fail("status must be one of " + ", ".join(STATUSES) + f", got {status!r}")
    target = art.get("target_checkpoint")
    if status == "PINNED":
        _validate_pinned_target(target, "PINNED artifact")
    else:
        if target is not None:
            _fail("UNRESOLVED_FAIL_CLOSED artifact must not carry a pinned target")
        edge = art.get("blocking_edge")
        if not isinstance(edge, dict) or not edge.get("artifacts") or not edge.get("edge"):
            _fail("UNRESOLVED_FAIL_CLOSED requires blocking_edge{artifacts,edge}")
    fallback = art.get("fallback_s97")
    if fallback is not None:
        if not isinstance(fallback, dict) or fallback.get("labeled") != "fallback":
            _fail("fallback_s97 must be explicitly labeled as fallback")
        if not isinstance(fallback.get("beats_base_arithmetic"), dict):
            _fail("fallback_s97 must carry beats_base_arithmetic vs the canonical base")
    return art


def validate_target_checkpoint_file(path):
    """Load + validate the artifact file; fail closed on absent/unparseable."""
    if not os.path.isfile(path):
        _fail("target_checkpoint.json absent: " + path)
    try:
        with open(path, encoding="utf-8") as f:
            art = json.load(f)
    except (OSError, ValueError) as e:
        _fail("target_checkpoint.json unparseable: " + path + ": " + repr(e))
    return validate_target_checkpoint(art)


# --- C-9089 (re-file of C-9063): fail-closed selection from C-9068 inventory -

SELECTION_RULE = (
    "newest mtime_utc first, checkpoint_id asc tie-break, among C-9068-manifest "
    "staged checkpoints that have BOTH a 64-hex sha-verified adapter weights "
    "identity AND >=1 sha-verified staged file; unstaged or unhashed entries are "
    "rejected, never guessed"
)
_CONSUMER_CARDS = ("C-9009", "C-9016")


def _load_json_blocked(path, what):
    if not os.path.isfile(path):
        _fail(f"BLOCKED: {what} missing: {path}")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        _fail(f"BLOCKED: {what} malformed: {path}: {e!r}")


def _is_sha(s):
    return isinstance(s, str) and bool(SHA256_RE.match(s))


def _weights_sha(man):
    for section in ("blocked", "staged_verified"):
        for ent in man.get(section) or []:
            if isinstance(ent, dict) and "adapter_model" in str(ent.get("name", "")):
                if _is_sha(ent.get("sha256")):
                    return ent["sha256"], section
    return None, None


def _candidate_from_manifest_checkpoint(man):
    ck = man.get("checkpoint")
    if not isinstance(ck, dict):
        return None
    weights_sha, where = _weights_sha(man)
    verified_files = [e for e in man.get("staged_verified") or [] if _is_sha(e.get("sha256"))]
    if weights_sha is None or not verified_files:
        return None
    return {
        "checkpoint_id": "{}/{}".format(ck.get("run_dir", ""), ck.get("step_dir", "")),
        "box_path": ck.get("box_path"),
        "mtime_utc": ck.get("mtime_utc"),
        "sha256": weights_sha,
        "weights_sha_location": where,
        "staged_dir": man.get("staged_dir"),
        "staged_verified": verified_files,
        "weights_staged_mac_side": where == "staged_verified",
    }


def select_target_from_c9068_artifacts(inv, man):
    """Pure selection from parsed C-9068 inventory + s97 manifest dicts."""
    rejected = []
    for _key, val in inv.items():
        if isinstance(val, dict) and "adapter_model_sha" in val:
            if _is_sha(val.get("adapter_model_sha")):
                rejected.append(
                    "alt {} rejected: unstaged ({})".format(val.get("path"), val.get("note", ""))
                )
            else:
                rejected.append("alt {} rejected: unhashed".format(val.get("path")))
    candidates = []
    primary = _candidate_from_manifest_checkpoint(man)
    if primary is not None:
        candidates.append(primary)
    for extra in man.get("other_staged") or []:
        files = [e for e in extra.get("staged_verified") or [] if _is_sha(e.get("sha256"))]
        if _is_sha(extra.get("sha256")) and files:
            candidates.append(
                dict(
                    extra,
                    staged_verified=files,
                    weights_sha_location="staged",
                    weights_staged_mac_side=True,
                )
            )
        else:
            rejected.append(
                "staged candidate {} rejected: unstaged or unhashed".format(
                    extra.get("checkpoint_id")
                )
            )
    if not candidates:
        _fail(
            "BLOCKED: zero sha-verified staged checkpoints in C-9068 manifest "
            "(weights sha-verified AND >=1 sha-verified staged file required)"
        )
    # deterministic: mtime_utc desc, then checkpoint_id asc (stable two-pass sort)
    candidates.sort(key=lambda c: c["checkpoint_id"])
    candidates.sort(key=lambda c: c.get("mtime_utc") or "", reverse=True)
    sel = dict(candidates[0])
    sel.update(
        {
            "status": "PINNED",
            "card": "C-9089",
            "selection_rule": SELECTION_RULE,
            "rejected": rejected,
            "candidates_considered": len(candidates),
        }
    )
    return sel


def select_target_from_c9068(inventory_path, manifest_path):
    inv = _load_json_blocked(inventory_path, "C-9068 inventory")
    man = _load_json_blocked(manifest_path, "C-9068 s97 manifest")
    sel = select_target_from_c9068_artifacts(inv, man)
    sel["inventory_path"] = inventory_path
    sel["manifest_path"] = manifest_path
    return sel


def bank_target_checkpoint(selection, out_path):
    import time

    art = dict(selection)
    art["selected_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    art["consumer_cards"] = list(_CONSUMER_CARDS)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(art, f, indent=1, sort_keys=True)
        f.write("\n")
    return art

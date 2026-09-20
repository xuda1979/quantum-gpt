"""C-9109: checkpoint inventory refresh loop.

Re-runs the C-9068 inventory scan consume step after every new sha-verified
adapter so the C-9089-style pin + C-9009 eval target never go stale. The
refresh consumes the prior C-9068 inventory artifact and:
- excludes any checkpoint lacking config.json + adapter_config.json + sha256,
- fails closed BLOCKED when the prior inventory is missing/malformed,
- rewrites the inventory artifact + c9063_target_checkpoint.json only from
  sha-verified entries, carrying selected_at_utc + the prior pin for diff,
- is idempotent: a no-change refresh updates refreshed_at only,
- never selects an unstaged or box-only entry Mac-side; absent box transport
  leaves the inventory as-is with a named BLOCKED note,
- BLOCKED is non-destructive: the named note goes to c9109_refresh_status.json
  and an existing pin file is left byte-identical (full prior pin carried).
"""

import json
import os
import re
import time

import harness_lib

CARD_ID = "C-9109"
_HARNESS_DIR = os.path.dirname(os.path.abspath(__file__))
PROBES_DIR = os.path.join(_HARNESS_DIR, "state", "probes")
INVENTORY_PATH = os.path.join(PROBES_DIR, "C-9068_lora_checkpoint_inventory.json")
PIN_PATH = os.path.join(PROBES_DIR, "c9063_target_checkpoint.json")
STATUS_NAME = "c9109_refresh_status.json"
REQUIRED_FILES = ("config.json", "adapter_config.json")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
STEP_NAME_RE = re.compile(r"^step_\d{6}_adapter$")
SELECTION_RULE = (
    "newest staged sha-verified checkpoint carrying "
    "config.json + adapter_config.json; never an unstaged or "
    "box-only entry Mac-side"
)


def _utcnow():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _complete(entry):
    """A checkpoint is selectable only with 64-hex sha256 AND both required
    config files named in its file list."""
    sha = entry.get("sha256")
    if not isinstance(sha, str) or not SHA256_RE.match(sha):
        return False
    files = entry.get("files")
    names = set(files) if isinstance(files, (list, tuple, set)) else set()
    return all(req in names for req in REQUIRED_FILES)


def _load_pin(path):
    try:
        with open(path, encoding="utf-8") as f:
            pin = json.load(f)
    except (OSError, ValueError):
        return None
    return pin if isinstance(pin, dict) else None


def _pinned_target(pin):
    if isinstance(pin, dict) and pin.get("status") == "PINNED":
        return pin.get("target")
    return None


def _blocked(pin_path, reason, now, note=None, status_path=None):
    """Fail closed WITHOUT touching the pin: a BLOCKED never overwrites the
    pin file (which may be a banked foreign-schema pin, e.g. C-9089's) — the
    named BLOCKED note goes to a separate c9109_refresh_status.json artifact
    carrying the FULL prior pin for diff."""
    if status_path is None:
        status_path = os.path.join(os.path.dirname(os.path.abspath(pin_path)), STATUS_NAME)
    prior = _load_pin(pin_path)
    rec = {
        "card": CARD_ID,
        "goal_card": "C-9009",
        "kind": "c9063_target_checkpoint_refresh",
        "status": "BLOCKED",
        "blocked_reason": reason,
        "blocked_utc": now,
        "refreshed_at": now,
        "prior_pin": _pinned_target(prior),
        "prior_pin_full": prior,
        "pin_path": pin_path,
        "pin_untouched": True,
    }
    if note:
        rec["note"] = note
    harness_lib.save_json(status_path, rec)
    return rec


def refresh_inventory(
    inventory_path=INVENTORY_PATH, pin_path=PIN_PATH, now_utc=None, box_transport_available=False
):
    """One refresh cycle. Returns a status record; never raises for
    expected fail-closed conditions (those come back as status BLOCKED)."""
    now = now_utc or _utcnow()

    if not os.path.isfile(inventory_path):
        return _blocked(pin_path, f"prior inventory missing: {inventory_path}", now)
    try:
        with open(inventory_path, encoding="utf-8") as f:
            prior = json.load(f)
    except ValueError:
        return _blocked(
            pin_path, f"prior inventory malformed (unparseable json): {inventory_path}", now
        )
    if not isinstance(prior, dict) or not isinstance(prior.get("checkpoints"), list):
        return _blocked(
            pin_path, f"prior inventory malformed (no checkpoints list): {inventory_path}", now
        )

    entries = prior["checkpoints"]
    verified = [e for e in entries if isinstance(e, dict) and _complete(e)]
    excluded = [
        e.get("path") if isinstance(e, dict) else repr(e)
        for e in entries
        if not (isinstance(e, dict) and _complete(e))
    ]
    if not verified:
        return _blocked(
            pin_path,
            f"no sha-verified complete checkpoint entries (need config.json + "
            f"adapter_config.json + sha256) in {inventory_path}",
            now,
            note=f"excluded {len(excluded)} incomplete entries",
        )

    staged = [e for e in verified if e.get("staged") is True]
    box_only = [e.get("path") for e in verified if e.get("staged") is not True]
    if not staged:
        reason = (
            f"sha-verified candidates are box-only (never selected "
            f"Mac-side) and no staged copy exists: "
            f"{chr(44).join(str(p) for p in box_only)}"
        )  # chr(44) == comma
        if not box_transport_available:
            reason += "; box transport ABSENT so inventory stays as-is"
        return _blocked(pin_path, reason, now)

    sel = max(staged, key=lambda e: (str(e.get("mtime_utc") or ""), str(e.get("path") or "")))
    step = os.path.basename(str(sel.get("path") or "").rstrip("/"))
    target = {
        "step": step if STEP_NAME_RE.match(step) else None,
        "path": sel["path"],
        "sha256": sel["sha256"],
        "source": "C-9068-inventory",
        "staged": True,
        "mtime_utc": sel.get("mtime_utc"),
    }

    prior_pin = _load_pin(pin_path)
    prior_target = _pinned_target(prior_pin)
    if prior_target and all(prior_target.get(k) == target.get(k) for k in ("path", "sha256")):
        prior_pin["refreshed_at"] = now
        prior_pin["refresh_count"] = int(prior_pin.get("refresh_count") or 1) + 1
        harness_lib.save_json(pin_path, prior_pin)
        return {"card": CARD_ID, "status": "UNCHANGED", "refreshed_at": now, "target": target}

    carried_prior = None
    if prior_target:
        carried_prior = dict(prior_target)
        carried_prior["selected_at_utc"] = prior_pin.get("selected_at_utc")
    pin = {
        "card": CARD_ID,
        "goal_card": "C-9009",
        "kind": "c9063_target_checkpoint_refresh",
        "status": "PINNED",
        "selection_rule": SELECTION_RULE,
        "target": target,
        "selected_at_utc": now,
        "prior_pin": carried_prior,
        "prior_pin_full": prior_pin,
        "refreshed_at": now,
        "refresh_count": 1,
        "excluded_incomplete_paths": excluded,
        "box_only_not_selected": box_only,
    }
    harness_lib.save_json(pin_path, pin)

    refreshed = dict(prior)
    refreshed["refreshed_by"] = CARD_ID
    refreshed["refreshed_utc"] = now
    refreshed["checkpoints"] = verified
    refreshed["excluded_incomplete_paths"] = excluded
    refreshed["box_only_not_selected"] = box_only
    harness_lib.save_json(inventory_path, refreshed)
    return {
        "card": CARD_ID,
        "status": "PINNED",
        "selected_at_utc": now,
        "target": target,
        "prior_pin": carried_prior,
    }


if __name__ == "__main__":
    print(json.dumps(refresh_inventory(), indent=1))

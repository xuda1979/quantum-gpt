# C-9090: bounced-card disposition sweep parser - fail-closed enumeration
# over the harness card queue.
#
# Contract (pinned by tests/test_c9090_bounced_disposition_sweep.py):
# - one row per bounced card: id|priority|bounce_count|disposition
# - missing QUEUE -> QueueMissingError; malformed card -> QueueParseError
#   (both named, both fail closed - a parser bug must never look like an
#   empty bounce list)
# - every P0/P1 disposition must be refiled|superseded-by|closed with a
#   non-empty payload; assert_complete raises naming the offender
# - P2 bounces may stay pending (listed, not fatal)
#
# Stdlib-only; never imports qgh (cannot touch live state via the
# QGH_STATE_DIR seam). Disposition DECISIONS live in a data file
# (state/probes/bounced_dispositions.json), not in this module.

import datetime
import json
import os
import re
import sys

DISPOSITION_RE = re.compile(r"^(refiled|superseded-by|closed):\s*\S")


class QueueMissingError(RuntimeError):
    pass


class QueueParseError(RuntimeError):
    pass


class SweepIncompleteError(RuntimeError):
    pass


def load_queue(path):
    if not os.path.exists(path):
        raise QueueMissingError("QUEUE not found: " + str(path))
    try:
        with open(path) as fh:
            data = json.load(fh)
    except OSError as exc:
        raise QueueParseError("QUEUE unreadable at " + str(path) + ": " + str(exc))
    except ValueError as exc:
        raise QueueParseError("QUEUE unparseable at " + str(path) + ": " + str(exc))
    if not isinstance(data, dict) or not isinstance(data.get("cards"), list):
        raise QueueParseError(
            "QUEUE malformed at " + str(path) + ": top-level cards must be a list"
        )
    return data


def collect_bounced(queue):
    # Fail closed on ANY malformed card, not just bounced ones: a parser
    # bug that silently skips cards would under-report the rot.
    bounced = []
    for i, c in enumerate(queue.get("cards", [])):
        if not isinstance(c, dict):
            raise QueueParseError("QUEUE card[" + str(i) + "] is not a dict")
        cid = c.get("id")
        if not cid:
            raise QueueParseError("QUEUE card[" + str(i) + "] missing id")
        missing_fields = [f for f in ("priority", "status") if f not in c]
        if missing_fields:
            raise QueueParseError(
                "card " + str(cid) + " missing fields: " + ",".join(missing_fields)
            )
        if c.get("status") == "bounced":
            bounced.append(c)
    return bounced


def render_row(c, disposition=None):
    cid = str(c["id"])
    pr = str(c["priority"])
    bc = str(c.get("bounce_count", 0))
    disp = disposition if disposition else "pending"
    return cid + "|P" + pr + "|" + bc + "|" + disp


def valid_disposition(disp):
    return isinstance(disp, str) and bool(DISPOSITION_RE.match(disp))


def build_sweep(queue, dispositions, now_utc=None):
    bounced = collect_bounced(queue)
    rows = []
    p0p1_missing = []
    p2_pending = []
    for c in bounced:
        cid = str(c["id"])
        disp = dispositions.get(cid)
        ok = valid_disposition(disp)
        rows.append(
            dict(
                id=cid,
                priority=c["priority"],
                bounce_count=c.get("bounce_count", 0),
                title=c.get("title", ""),
                disposition=disp if ok else None,
                disposition_ok=ok,
                row=render_row(c, disp if ok else None),
            )
        )
        if c["priority"] in (0, 1):
            if not ok:
                p0p1_missing.append(cid)
        elif not ok:
            p2_pending.append(cid)
    return dict(
        card="C-9090",
        generated_utc=now_utc,
        total_bounced=len(rows),
        rows=rows,
        p0p1_undispositioned=p0p1_missing,
        p2_pending=p2_pending,
        all_p0p1_dispositioned=(len(p0p1_missing) == 0),
    )


def assert_complete(artifact):
    missing = artifact.get("p0p1_undispositioned") or []
    if missing:
        raise SweepIncompleteError(
            "undispositioned P0/P1 bounces: " + ", ".join(str(m) for m in missing)
        )
    return True


def write_sweep(path, artifact):
    with open(path, "w") as fh:
        json.dump(artifact, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return path


def main(argv):
    if len(argv) < 3:
        print("usage: bounced_sweep.py QUEUE.json DISPOSITIONS.json OUT.json")
        return 64
    queue_path, disp_path, out_path = argv[0], argv[1], argv[2]
    queue = load_queue(queue_path)
    dispositions = dict()
    if os.path.exists(disp_path):
        with open(disp_path) as fh:
            dispositions = json.load(fh)
    if not isinstance(dispositions, dict):
        raise QueueParseError("dispositions file must be a JSON object")
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    artifact = build_sweep(queue, dispositions, now_utc=now)
    write_sweep(out_path, artifact)
    for r in artifact["rows"]:
        print(r["row"])
    complete = artifact["all_p0p1_dispositioned"]
    print(
        "total_bounced="
        + str(artifact["total_bounced"])
        + " p0p1_undispositioned="
        + str(len(artifact["p0p1_undispositioned"]))
        + " p2_pending="
        + str(len(artifact["p2_pending"]))
        + " complete="
        + str(complete)
    )
    # Fail closed: exit 0 ONLY when zero P0/P1 bounces lack a disposition.
    if complete:
        assert_complete(artifact)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

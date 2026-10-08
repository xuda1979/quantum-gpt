#!/usr/bin/env python3
"""push_until_success.py — keep pushing files to box until success.

Handles flaky daemons that cycle up/down every ~2 min. Retries each file
until verified on box. Writes progress to a state file for fast feedback.

Usage:
    python3 harness/scripts/push_until_success.py ASI3 <manifest_json> &
    # manifest: [{"local": "...", "remote": "..."}, ...]
    # check progress: cat harness/state/push_progress.json
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "harness" / "scripts"))
from push_to_box import push  # noqa: E402

PROGRESS = REPO / "harness" / "state" / "push_progress.json"


def write_progress(state: dict) -> None:
    """<4 lines."""
    PROGRESS.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS.write_text(json.dumps(state, indent=2))


def main() -> None:
    """<15 lines."""
    box = sys.argv[1]
    manifest = json.loads(Path(sys.argv[2]).read_text())
    state = {"started": time.strftime("%H:%M:%S"), "files": {}}
    write_progress(state)
    for entry in manifest:
        name = entry["remote"].split("/")[-1]
        for attempt in range(1, 13):  # max 12 attempts = ~24 min
            state["files"][name] = {"attempt": attempt, "status": "pushing"}
            write_progress(state)
            result = push(box, entry["local"], entry["remote"])
            if result["status"] == "PASS":
                state["files"][name] = {
                    "attempt": attempt,
                    "status": "DONE",
                    "bytes": result.get("total_bytes"),
                }
                write_progress(state)
                break
            state["files"][name] = {
                "attempt": attempt,
                "status": "RETRY",
                "error": str(result.get("error", ""))[:100],
            }
            write_progress(state)
            time.sleep(60)  # wait for daemon cycle
    state["finished"] = time.strftime("%H:%M:%S")
    write_progress(state)


if __name__ == "__main__":
    main()

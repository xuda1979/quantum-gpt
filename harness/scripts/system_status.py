#!/usr/bin/env python3
"""system_status.py — one-shot full system status. Reusable.

Usage: python3 harness/scripts/system_status.py [--json]
Timeout: 30s (box exec is the only slow part, 3s each = ~9s total).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

# Import collectors — each is short and focused
sys.path.insert(0, str(REPO / "harness" / "scripts"))
from status_collectors import (  # noqa: E402
    collect_activity,
    collect_boxes,
    collect_eval,
    collect_keeper,
    collect_queue,
    collect_training,
)
from status_render import render_status  # noqa: E402


def collect() -> dict:
    """Orchestrate all collectors. Each collector is <30 lines."""
    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "boxes": collect_boxes(),
        "keeper": collect_keeper(),
        "training": collect_training(),
        "queue": collect_queue(),
        "eval": collect_eval(),
        **collect_activity(),
    }


def main():
    d = collect()
    if "--json" in sys.argv:
        print(json.dumps(d, indent=2, default=str))
    else:
        print(render_status(d))


if __name__ == "__main__":
    main()

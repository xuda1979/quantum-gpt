"""C-9821: box-side eval-leg serialization via a POSIX flock.

The ASI2 eval factory is a shared NPU pool. Multiple concurrent
run_asi2_base_adapter_rubric_eval legs (watcher + agent legs launched via
nohup on the box) racing that pool slow generation ~10x and blow their
900s timeouts, dying mid-run with VOID rows.

The Mac-side lease (harness/state/locks/asi2-eval.lock) is only enforced by
callers that go through the Mac dispatch path; box-launched legs bypass it.
The authoritative guard is therefore a POSIX flock taken inside the eval
script's entry path BEFORE any model load.

This module is deliberately LIGHTWEIGHT (standard library only, no torch /
transformers / training.* imports) so that tests exercising the flock acquire
fast and deterministically instead of paying a multi-second heavy import.

flock(2) is held on an open fd for the life of the process; it auto-releases
when the fd is closed or the process exits, so a crashed leg cannot wedge the
box and there is no stale-lease takeover race (unlike a pid/timestamp lease).
"""

from __future__ import annotations

import fcntl
import os

# Canonical box-side flock path for eval legs. Held (LOCK_EX) for the full
# duration of a leg; a concurrent second leg finds it held and exits non-zero
# LOCKED without touching the model.
BOX_EVAL_LEG_LOCK = "/tmp/asi2_eval_leg.lock"

# Non-zero, distinct sentinel exit code for a refused (LOCKED) leg so callers
# can distinguish "busy, another serialized leg is running" (120) from other
# failures.
BOX_EVAL_LEG_LOCKED_EC = 120


def acquire_box_leg_flock(lock_path: str = BOX_EVAL_LEG_LOCK):
    """Take an exclusive non-blocking POSIX flock on lock_path.

    Returns (fh, True) on first acquisition and (None, False) when a concurrent
    holder already owns the lock. The caller must keep the returned file handle
    (fh) open for the leg duration; calling fh.close() (or fcntl.flock(fh.fileno(),
    LOCK_UN)) releases it. flock auto-releases on process exit.
    """
    fh = open(lock_path, "w")
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (BlockingIOError, OSError):
        fh.close()
        return None, False
    try:
        fh.write("pid=%d\n" % os.getpid())
        fh.flush()
    except OSError:
        pass
    return fh, True

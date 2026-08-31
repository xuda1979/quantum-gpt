"""TDD: the trainer installs faulthandler at startup so a crash or a live
SIGUSR1 "stall dump" signal produces an all-thread stack file in the run log.

2026-08-26 (debug-lane tooling mandate — the gdb/pdb analogue for a wedged
trainer): run-6 died silently enough that root-causing needed log archaeology.
The installed machinery:
  - ``faulthandler.enable()`` — fatal signals (SIGSEGV/SIGFPE/SIGABRT/SIGBUS/
    SIGILL) dump all-thread stacks to the run log before the process dies;
  - ``faulthandler.register(SIGUSR1, ...)`` — the live dump signal: send it
    to a STALLED trainer PID and the log receives every thread's stack while
    the process keeps running (the operator-side py-spy analogue, built in);
  - SIGABRT is covered by ``enable()`` itself (CPython refuses a separate
    ``register(SIGABRT, ...)`` — "use enable() instead" — and enable()'s
    fatal dump goes to the same target).

The test drives the real signal path: install with a temp file, SIGUSR1
ourselves, and assert a stack file appeared and the process survived.
"""

from __future__ import annotations

import os
import signal
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.grpo_trainer import install_faulthandler_dumps  # noqa: E402

pytestmark = pytest.mark.skipif(
    not hasattr(signal, "SIGUSR1"), reason="SIGUSR1 not available on this platform"
)


def test_sigusr1_produces_stack_file_and_process_survives(tmp_path) -> None:
    """The mandate's core behavior: a signal produces a stack file (the run
    log) and the trainer process is NOT killed by the dump signal."""
    dump_file = tmp_path / "stacks.log"
    with dump_file.open("w") as fh:
        install_faulthandler_dumps(log_file=fh)
        try:
            os.kill(os.getpid(), signal.SIGUSR1)
            # The faulthandler handler writes the dump and returns — we are
            # still alive and the next line executes.
            alive = True
        finally:
            # Never leave a live SIGUSR1 dump handler in the pytest process.
            import faulthandler

            faulthandler.unregister(signal.SIGUSR1)
    assert alive
    text = dump_file.read_text()
    assert "Stack" in text or "Current thread" in text or 'File "' in text
    assert str(Path(__file__)) in text  # our own frame is in the dump


def test_install_degrades_gracefully_on_captured_stderr() -> None:
    """2026-08-26 canary RED: under pytest's fd-capture the trainer's stderr
    has no real fileno — the unguarded faulthandler.enable() raised
    io.UnsupportedOperation: fileno, killing main() before its abort path
    (2 resume tests failed). The dumps must degrade gracefully: no raise,
    and the returned target is still the passed file."""
    import io

    captured = io.StringIO()  # a stream without a fileno (captured stderr)
    try:
        returned = install_faulthandler_dumps(log_file=captured)
    finally:
        import faulthandler

        faulthandler.unregister(signal.SIGUSR1)
    assert returned is captured


def test_install_returns_the_log_file() -> None:
    dump_file = Path("__faulthandler_probe__.log")
    try:
        with dump_file.open("w") as fh:
            returned = install_faulthandler_dumps(log_file=fh)
            assert returned is fh
    finally:
        import faulthandler

        faulthandler.unregister(signal.SIGUSR1)
        dump_file.unlink(missing_ok=True)


def test_install_is_idempotent(tmp_path) -> None:
    """main() may call the installer once; a second call (e.g. re-entry in a
    smoke) must not raise or corrupt the registrations."""
    dump_file = tmp_path / "stacks2.log"
    try:
        with dump_file.open("w") as fh:
            install_faulthandler_dumps(log_file=fh)
            install_faulthandler_dumps(log_file=fh)
    finally:
        import faulthandler

        faulthandler.unregister(signal.SIGUSR1)

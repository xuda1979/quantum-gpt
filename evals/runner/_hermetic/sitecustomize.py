"""Auto-imported hermetic bootstrap for the eval verification sandbox.

CPython imports any module named ``sitecustomize`` found on ``sys.path`` at
interpreter startup, before the candidate script's own code runs. ``execute_run.py``
puts this directory on ``PYTHONPATH`` (only when ``--hermetic`` is passed) so that
verification runs are reproducible and cannot silently reach the network.

Two guarantees:
  1. Deterministic RNG seeding (stdlib ``random``, NumPy, PyTorch) so an
     S-tier "code passed" label is not flaky across re-runs.
  2. Outbound network is blocked (loopback + AF_UNIX still allowed for local
     IPC such as DataLoader workers) so a candidate cannot fetch hidden state
     or make a verification result depend on an external service.

Controlled entirely via environment variables set by execute_run.py:
  EVAL_SEED            integer seed (default 0)
  EVAL_BLOCK_NETWORK   "1" to block outbound network (default off)
"""

from __future__ import annotations

import os
import random


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except (TypeError, ValueError):
        return default


def _seed_torch(torch_mod, seed: int) -> None:
    try:
        torch_mod.manual_seed(seed)
        if torch_mod.cuda.is_available():
            torch_mod.cuda.manual_seed_all(seed)
        try:
            torch_mod.use_deterministic_algorithms(True, warn_only=True)
        except Exception:
            pass
    except Exception:
        pass


def _install_seeding(seed: int) -> None:
    """Seed RNGs now, and hook future imports so heavy libs are seeded on first use."""
    import builtins
    import sys

    random.seed(seed)

    seeders = {
        "numpy": lambda m: m.random.seed(seed),
        "torch": lambda m: _seed_torch(m, seed),
    }
    seeded: set[str] = set()

    def _maybe_seed(top: str) -> None:
        if top in seeders and top not in seeded and top in sys.modules:
            try:
                seeders[top](sys.modules[top])
            except Exception:
                pass
            seeded.add(top)

    # Seed anything already imported at startup.
    for top in list(seeders):
        _maybe_seed(top)

    # Seed numpy/torch the first time the candidate imports them, without
    # forcing a heavy import for candidates that never use them.
    real_import = builtins.__import__

    def _patched_import(name, globals=None, locals=None, fromlist=(), level=0):
        module = real_import(name, globals, locals, fromlist, level)
        _maybe_seed(name.split(".")[0] if name else "")
        return module

    builtins.__import__ = _patched_import


def _install_network_block() -> None:
    import socket

    msg = (
        "network access is disabled in the hermetic eval sandbox "
        "(run without --hermetic, or pass --allow-network, to enable)"
    )
    local_hosts = {"127.0.0.1", "::1", "localhost", "0.0.0.0"}

    real_connect = socket.socket.connect
    real_connect_ex = socket.socket.connect_ex
    real_create_connection = socket.create_connection

    def _is_local(sock: socket.socket, address) -> bool:
        if getattr(sock, "family", None) == getattr(socket, "AF_UNIX", object()):
            return True
        try:
            host = address[0]
        except (TypeError, IndexError):
            return False
        return host in local_hosts

    def connect(self, address, *args, **kwargs):
        if _is_local(self, address):
            return real_connect(self, address, *args, **kwargs)
        raise RuntimeError(msg)

    def connect_ex(self, address, *args, **kwargs):
        if _is_local(self, address):
            return real_connect_ex(self, address, *args, **kwargs)
        raise RuntimeError(msg)

    def create_connection(address, *args, **kwargs):
        host = address[0] if isinstance(address, tuple) else address
        if host in local_hosts:
            return real_create_connection(address, *args, **kwargs)
        raise RuntimeError(msg)

    socket.socket.connect = connect
    socket.socket.connect_ex = connect_ex
    socket.create_connection = create_connection


def _bootstrap() -> None:
    _install_seeding(_int_env("EVAL_SEED", 0))
    if os.environ.get("EVAL_BLOCK_NETWORK", "0") == "1":
        try:
            _install_network_block()
        except Exception:
            # Never let hardening crash a verification run.
            pass


_bootstrap()

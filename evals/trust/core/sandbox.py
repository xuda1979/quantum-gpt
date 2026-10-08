"""Hermetic test-execution sandbox.

Runs a candidate's ``tests.py`` against a candidate file in a per-task
temporary directory with:

  - frozen ``PYTHONHASHSEED=0``
  - ``PYTHONPATH`` restricted to the sandbox (no host site-packages leak
    unless explicitly allowlisted)
  - optional network block (via ``sitecustomize.py`` shim)
  - per-task timeout
  - stdout/stderr captured to files and hashed

The sandbox never imports the host's ``sitecustomize``; it injects its
own that (a) blocks network if requested and (b) seeds ``random`` and
``numpy.random`` if those modules are imported.

Returns a ``TestResult`` dataclass with all hashes needed for ledger
provenance.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import hashing

# A minimal sitecustomize that blocks network and seeds RNGs.
_SITECUSTOMIZE = '''\
"""Hermetic sitecustomize injected by evals.trust.core.sandbox."""
import os
import sys
import random as _random

_random.seed(0)

try:
    import numpy as _np
    _np.random.seed(0)
except Exception:
    pass

_BLOCK_NET = os.environ.get("TRUST_EVAL_BLOCK_NETWORK", "0") == "1"

if _BLOCK_NET:
    import socket as _socket

    class _BlockingSocket(_socket.socket):
        def __init__(self, *a, **kw):
            raise _socket.SocketError("network blocked by trust-eval sandbox")

    _socket.socket = _BlockingSocket

    try:
        import urllib.request as _ur
        _ur.urlopen = lambda *a, **k: (_ for _ in ()).throw(
            RuntimeError("network blocked by trust-eval sandbox"))
    except Exception:
        pass
'''


@dataclass
class TestResult:
    passed: bool
    details: list[str]
    failure_category: str | None
    stdout: str
    stderr: str
    returncode: int | None
    stdout_hash: str
    stderr_hash: str
    duration_sec: float
    sandbox_dir: str | None = None  # set only if keep_dir requested

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "details": self.details,
            "failure_category": self.failure_category,
            "returncode": self.returncode,
            "stdout_hash": self.stdout_hash,
            "stderr_hash": self.stderr_hash,
            "duration_sec": round(self.duration_sec, 4),
        }


def classify_failure(details: list[str], stderr: str) -> str | None:
    if not any(d.strip() for d in details) and not stderr.strip():
        return "empty"
    combined = "\n".join(details) + "\n" + stderr
    low = combined.lower()
    if "syntaxerror" in low or "indentationerror" in low:
        return "syntax"
    if "modulenotfounderror" in low or "importerror" in low:
        return "import"
    if "timeout" in low or "timed out" in low:
        return "timeout"
    if "assertion" in low:
        return "assertion"
    return "runtime"


def load_test_module(tests_path: Path):
    """Load a tests.py module in-process (used by the in-proc runner)."""
    spec = importlib.util.spec_from_file_location(tests_path.stem, tests_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load test module: {tests_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_test_hermetic(
    *,
    task_dir: Path,
    test_file: str,
    candidate_code: str,
    candidate_filename: str = "candidate.py",
    timeout_sec: float = 60.0,
    block_network: bool = True,
    keep_dir: bool = False,
    extra_pythonpath: list[str] | None = None,
) -> TestResult:
    """Run ``test_file`` against ``candidate_code`` in a hermetic subprocess.

    The candidate code is written to a fresh temp dir along with the
    task's ``tests.py`` (copied). A dedicated subprocess runs the test
    with a frozen environment and the injected ``sitecustomize.py``.

    The test module must expose ``run_tests(candidate_path: str) -> dict``
    with keys ``passed`` (bool) and ``details`` (list[str]). This is the
    contract used by the existing ``evals/tasks/`` tree.
    """
    import time

    started = time.time()
    keep = keep_dir
    with tempfile.TemporaryDirectory(prefix="trust-eval-") as tmp:
        tmp_path = Path(tmp)
        # write candidate
        (tmp_path / candidate_filename).write_text(candidate_code, encoding="utf-8")
        # copy tests
        src_tests = task_dir / test_file
        if not src_tests.is_file():
            raise FileNotFoundError(f"missing tests file: {src_tests}")
        dst_tests = tmp_path / test_file
        shutil.copy2(src_tests, dst_tests)
        # copy any sibling files the test might need (e.g. workspace assets)
        for sibling in task_dir.iterdir():
            if sibling.name in (test_file, "task.json", candidate_filename):
                continue
            if sibling.is_file():
                shutil.copy2(sibling, tmp_path / sibling.name)
        # inject sitecustomize
        (tmp_path / "sitecustomize.py").write_text(_SITECUSTOMIZE, encoding="utf-8")
        # build a tiny driver that imports the test and calls run_tests
        driver = tmp_path / "__trust_eval_driver.py"
        driver.write_text(
            "import importlib.util, sys, json\n"
            f"TEST_FILE = {test_file!r}\n"
            f"CANDIDATE = {candidate_filename!r}\n"
            "spec = importlib.util.spec_from_file_location(TEST_FILE[:-3], TEST_FILE)\n"
            "mod = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(mod)\n"
            "fn = getattr(mod, 'run_tests', None)\n"
            "if fn is None:\n"
            "    print(json.dumps({'passed': False, 'details': ['run_tests() not defined in tests.py']}))\n"
            "    sys.exit(0)\n"
            "res = fn(CANDIDATE)\n"
            "print(json.dumps({'passed': bool(res.get('passed')), 'details': res.get('details', [])}))\n",
            encoding="utf-8",
        )
        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": os.environ.get("HOME", "/tmp"),
            "PYTHONHASHSEED": "0",
            "PYTHONPATH": str(tmp_path) + (os.pathsep + os.pathsep.join(extra_pythonpath or [])),
            "PYTHONNOUSERSITE": "1",
            "TRUST_EVAL_BLOCK_NETWORK": "1" if block_network else "0",
        }
        # strip PYTHONSTARTUP / PYTHONHOME to avoid leaks
        for k in ("PYTHONSTARTUP", "PYTHONHOME", "PYTHONPATH"):
            env.pop(k, None)
        env["PYTHONPATH"] = str(tmp_path) + (os.pathsep + os.pathsep.join(extra_pythonpath or []))
        try:
            completed = subprocess.run(
                [sys.executable, "-I", "-S", str(driver)],
                cwd=str(tmp_path),
                env=env,
                capture_output=True,
                timeout=timeout_sec,
                text=True,
            )
            stdout, stderr, rc = completed.stdout, completed.stderr, completed.returncode
        except subprocess.TimeoutExpired as e:
            stdout = e.stdout.decode("utf-8", "replace") if e.stdout else ""
            stderr = (e.stderr.decode("utf-8", "replace") if e.stderr else "") + f"\n[trust-eval] timeout after {timeout_sec}s\n"
            rc = -1

        import json as _json
        details: list[str] = []
        passed = False
        try:
            payload = _json.loads(stdout.strip().splitlines()[-1])
            passed = bool(payload.get("passed"))
            details = list(payload.get("details", []))
        except Exception:
            details = [f"[trust-eval] failed to parse test output: {stdout[:300]!r}"]
            if stderr.strip():
                details.append(f"stderr: {stderr[:300]!r}")

        result = TestResult(
            passed=passed,
            details=details,
            failure_category=classify_failure(details, stderr) if not passed else None,
            stdout=stdout,
            stderr=stderr,
            returncode=rc,
            stdout_hash=hashing.hash_text(stdout),
            stderr_hash=hashing.hash_text(stderr),
            duration_sec=time.time() - started,
            sandbox_dir=str(tmp_path) if keep else None,
        )
        if keep:
            # we're inside a `with` context; copy out
            kept = Path(tempfile.mkdtemp(prefix="trust-eval-kept-"))
            for p in tmp_path.iterdir():
                shutil.copy2(p, kept / p.name)
            result.sandbox_dir = str(kept)
        return result

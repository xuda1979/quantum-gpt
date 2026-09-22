"""Tests for deterministic acceptance gate — verdicts checked by script, not vibes."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "harness" / "scripts" / "acceptance_gate.py"


def run_script(*args, timeout=15):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(REPO),
    )


def _make_verdict(tmpdir: str, **overrides) -> str:
    v = {
        "card": "C-TEST",
        "pass_adapter": "4/18",
        "pass_base": "4/18",
        "adapter_applied": True,
        "probe_differs": True,
        "candidates_differ_from_base": True,
        "beats_base": False,
        "n_pass": 4,
        "n_total": 18,
    }
    v.update(overrides)
    p = Path(tmpdir) / "verdict.json"
    p.write_text(json.dumps(v))
    return str(p)


def test_gate_exists():
    assert SCRIPT.exists()


def test_gate_rejects_missing_markers():
    """A verdict without adapter_applied+probe_differs is VOID — rejected."""
    with tempfile.TemporaryDirectory() as td:
        v = _make_verdir = _make_verdict(td, adapter_applied=False)
        r = run_script(v)
        assert r.returncode != 0, "must reject missing adapter marker"
        assert "REJECT" in r.stdout


def test_gate_accepts_complete_verdict():
    with tempfile.TemporaryDirectory() as td:
        v = _make_verdict(td)
        r = run_script(v)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "ACCEPT" in r.stdout


def test_gate_rejects_fabricated_beats_base():
    """beats_base=true with pass<=base is fabricated — rejected."""
    with tempfile.TemporaryDirectory() as td:
        v = _make_verdict(td, pass_adapter="4/18", pass_base="4/18", beats_base=True)
        r = run_script(v)
        assert r.returncode != 0
        assert "REJECT" in r.stdout

"""Coverage backlog (2026-08-26): reward-audit daemon transport + CLI main.

The daemon pull (base64 chunked transport with truncation retries) and the
CLI mains of sapo_reward_audit.py (weight resolution from argv/config, JSON
report mode, fail-loud argument errors). The chunk transport is the box-side
metrics lifeline for the monitoring fleet — its retry/fail-closed semantics
are pinned here.
"""

from __future__ import annotations

import base64
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import sapo_reward_audit as audit  # noqa: E402


def test_audit_module_has_future_annotations() -> None:
    """r10 depmatrix F2: PEP 604 annotations require the future import for
    py3.9-safe imports."""
    source = Path(audit.__file__).read_text(encoding="utf-8")
    assert "from __future__ import annotations" in source


# ---------------------------------------------------------------------------
# daemon transport
# ---------------------------------------------------------------------------


def _fake_daemon(source: Path, *, truncate_first_chunk: bool = False, stuck: bool = False):
    """A fake _daemon_exec: serves 'wc -c' + base64 chunk probes from a local
    file. Returns (fake_fn, call_log)."""
    calls: list[str] = []
    attempts = {"n": 0}

    def _exec(url: str, command: str) -> str:
        calls.append(command)
        if "wc -c" in command:
            return f"{source.stat().st_size}\n"
        m = re.search(r"read\(\)\[(\d+):(\d+)\]", command)
        assert m, command
        start, end = int(m.group(1)), int(m.group(2))
        block = source.read_bytes()[start:end]
        if stuck:
            return base64.b64encode(block[: max(1, len(block) // 2)]).decode()
        if truncate_first_chunk and attempts["n"] == 0:
            attempts["n"] += 1
            return base64.b64encode(block[: max(1, len(block) - 1)]).decode()
        return base64.b64encode(block).decode()

    return _exec, calls


def test_pull_metrics_via_daemon_chunked_roundtrip(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "metrics.jsonl"
    payload = "".join(f'{{"step": {i}, "loss": 0.1}}\n' for i in range(1, 40))
    source.write_text(payload, encoding="utf-8")
    fake, calls = _fake_daemon(source)
    monkeypatch.setattr(audit, "_daemon_exec", fake)
    out = tmp_path / "pulled.jsonl"
    written = audit.pull_metrics_via_daemon("http://d", str(source), out, chunk_bytes=500)
    assert written == len(payload.encode())
    assert out.read_bytes() == source.read_bytes()
    assert len(calls) > 2  # size + at least two chunks


def test_pull_metrics_via_daemon_retries_truncated_chunk(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "m.jsonl"
    source.write_text("x" * 1000, encoding="utf-8")
    fake, _ = _fake_daemon(source, truncate_first_chunk=True)
    monkeypatch.setattr(audit, "_daemon_exec", fake)
    out = tmp_path / "out.jsonl"
    written = audit.pull_metrics_via_daemon("http://d", str(source), out, chunk_bytes=600)
    assert written == 1000
    assert out.read_bytes() == source.read_bytes()


def test_pull_metrics_via_daemon_fails_loud_on_stuck_chunk(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "m.jsonl"
    source.write_text("y" * 700, encoding="utf-8")
    fake, _ = _fake_daemon(source, stuck=True)
    monkeypatch.setattr(audit, "_daemon_exec", fake)
    with pytest.raises(RuntimeError, match="could not fetch bytes"):
        audit.pull_metrics_via_daemon(
            "http://d", str(source), tmp_path / "o.jsonl", chunk_bytes=300
        )


def test_pull_metrics_via_daemon_fails_loud_on_empty_box(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "empty.jsonl"
    source.write_text("", encoding="utf-8")
    fake, _ = _fake_daemon(source)
    monkeypatch.setattr(audit, "_daemon_exec", fake)
    with pytest.raises(RuntimeError, match="size 0"):
        audit.pull_metrics_via_daemon("http://d", str(source), tmp_path / "o.jsonl")


def test_daemon_exec_raises_on_error_payload(monkeypatch) -> None:
    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({"ok": False, "error": "boom"}).encode()

    def _fake_urlopen(req, timeout=120):
        return _Resp()

    monkeypatch.setattr(audit.urllib.request, "urlopen", _fake_urlopen)
    with pytest.raises(RuntimeError, match="daemon exec failed: boom"):
        audit._daemon_exec("http://d", "echo hi")


# ---------------------------------------------------------------------------
# weight resolution
# ---------------------------------------------------------------------------


def test_resolve_weights_from_argv_overrides() -> None:
    weights = audit.resolve_weights_from_argv(
        [
            "--reward-pass-weight",
            "0.6",
            "--reward-mode",
            "tiered",
            "--advantage-clip",
            "0.7",
            "--reward-judge-mass",
            "0.3",
        ]
    )
    assert weights["shaped"] == pytest.approx(0.6)
    assert weights["mode"] == "tiered"
    assert weights["clip"] == pytest.approx(0.7)
    assert weights["judge_mass"] == pytest.approx(0.3)
    # absent flags keep documented defaults
    weights2 = audit.resolve_weights_from_argv([])
    assert weights2["shaped"] == audit.DEFAULT_WEIGHTS["shaped"]


def test_resolve_weights_from_config_training_section(tmp_path: Path) -> None:
    cfg = tmp_path / "cfg.json"
    cfg.write_text(
        json.dumps(
            {
                "training": {
                    "reward_pass_weight": 0.5,
                    "reward_import_hygiene_weight": 0.1,
                    "reward_mode": "tiered",
                    "advantage_clip": 0.9,
                },
                "other": 1,
            }
        ),
        encoding="utf-8",
    )
    weights = audit.resolve_weights_from_config(cfg)
    assert weights["shaped"] == pytest.approx(0.5)
    assert weights["hygiene"] == pytest.approx(0.1)
    assert weights["mode"] == "tiered"
    assert weights["clip"] == pytest.approx(0.9)


# ---------------------------------------------------------------------------
# CLI main
# ---------------------------------------------------------------------------


def _clean_record() -> dict:
    """A passing single-candidate record that audits clean (G=1 -> a gap,
    never an error, so exit code stays 0)."""
    return {
        "step": 1,
        "task": "t1",
        "domain": "q",
        "mean_reward": 1.0,
        "advantage_scale": 0.53,
        "rollout_rewards": [
            {
                "index": 0,
                "pass": True,
                "pass_reward": 1.0,
                "shaped_reward": 1.0,
                "syntax_reward": 1.0,
                "interface_reward": 1.0,
                "verifier_reward": 1.0,
                "brevity_reward": 0.0,
                "import_hygiene_reward": 1.0,
                "total_reward": 1.0,
                "advantage": 0.0,
                "n_tokens": 10,
            },
        ],
    }


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "sapo_reward_audit.py"), *args],
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_cli_json_report_clean_record(tmp_path: Path) -> None:
    metrics = tmp_path / "grpo_step_metrics.jsonl"
    metrics.write_text(json.dumps(_clean_record()) + "\n", encoding="utf-8")
    proc = _run_cli("--metrics", str(metrics), "--json")
    assert proc.returncode == 0, proc.stderr
    report = json.loads(proc.stdout)
    assert report["steps_audited"] == 1
    assert report["errors"] == 0
    assert report["ok"] is True


def test_cli_violation_exits_2(tmp_path: Path) -> None:
    record = _clean_record()
    record["rollout_rewards"][0]["pass"] = False  # pass flag vs pass_reward mismatch
    metrics = tmp_path / "bad.jsonl"
    metrics.write_text(json.dumps(record) + "\n", encoding="utf-8")
    proc = _run_cli("--metrics", str(metrics))
    assert proc.returncode == 2
    assert "VIOLATION" in proc.stdout


def test_cli_missing_metrics_exits_2(tmp_path: Path) -> None:
    proc = _run_cli("--metrics", str(tmp_path / "nope.jsonl"))
    assert proc.returncode == 2
    assert "--metrics file required" in proc.stderr


def test_cli_daemon_url_requires_box_path() -> None:
    proc = _run_cli("--metrics", "/tmp/x.jsonl", "--daemon-url", "http://d")
    assert proc.returncode == 2
    assert "--box-path required" in proc.stderr

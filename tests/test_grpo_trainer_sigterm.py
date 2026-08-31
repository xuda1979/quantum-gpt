"""TDD: SIGTERM must run the final-save path, not die instantly (2026-08-25).

The launcher's stop sequence TERMs the trainer and KILLs survivors after 3s.
With no handler the TERM killed the process instantly, risking a missing or
partial final adapter save (no step_*_adapter at the current boundary, no
'adapter' dir refresh). The handler runs the SAME final-save path as the
loop exit and then exits. SIGKILL cannot be caught — unchanged (and
untestable by construction).

Tests simulate the handler directly on a tiny trainer harness (fake model +
fake text-preprocessor backend with save_pretrained), exactly as the handler
is wired in main(): handler -> termination_save(step=stop.step) -> os._exit.
"""

from __future__ import annotations

import json
import os
import signal
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.grpo_trainer import GracefulStop, termination_save  # noqa: E402


class TinyBackend:
    """Stand-in for the text-preprocessor backend (save_pretrained only)."""

    def __init__(self) -> None:
        self.saved: list[Path] = []

    def save_pretrained(self, path: Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        (path / "backend.marker").write_text("ok")
        self.saved.append(path)


class TinyModel:
    """'Tiny trainer harness' model: save_pretrained writes the PEFT files
    the trainer's completeness rule checks for (adapter_config.json +
    adapter_model.safetensors)."""

    def __init__(self) -> None:
        self.saved: list[Path] = []

    def save_pretrained(self, path: Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        (path / "adapter_config.json").write_text(json.dumps({"r": 64, "lora_alpha": 64}))
        (path / "adapter_model.safetensors").write_text("fake-tensors")
        self.saved.append(path)


class TinyPreprocessor:
    """Mimics the trainer's text_preprocessor: .save_backend.save_pretrained."""

    def __init__(self) -> None:
        self.save_backend = TinyBackend()


def _harness(tmp_path: Path) -> tuple[Path, TinyModel, TinyPreprocessor]:
    out = tmp_path / "run"
    out.mkdir()
    return out, TinyModel(), TinyPreprocessor()


# ---------------------------------------------------------------------------
# termination_save — the final-save path the handler triggers
# ---------------------------------------------------------------------------


def test_termination_save_writes_step_checkpoint_and_adapter(tmp_path: Path) -> None:
    out, model, preproc = _harness(tmp_path)
    adapter_dir = termination_save(
        model,
        preproc,
        out,
        step=5,
        distributed=False,
        rank=0,
        metrics=[{"step": 5, "loss": -0.1}],
        planned_steps=20,
    )
    assert adapter_dir == out / "adapter"
    # step_*_adapter at the current boundary, complete via the atomic save
    ckpt = out / "step_000005_adapter"
    assert (ckpt / "adapter_config.json").is_file()
    assert (ckpt / "adapter_model.safetensors").is_file()
    # the loop-exit adapter dir + backend files
    assert (out / "adapter" / "adapter_config.json").is_file()
    assert (out / "adapter" / "adapter_model.safetensors").is_file()
    assert (out / "adapter" / "backend.marker").is_file()
    # the metrics summary mirrors the loop-exit save
    summary = json.loads((out / "grpo_metrics.json").read_text())
    assert summary is not None
    assert len(model.saved) == 2  # step checkpoint + adapter dir


def test_termination_save_noops_for_non_rank0_and_none_model(tmp_path: Path) -> None:
    out, model, preproc = _harness(tmp_path)
    assert termination_save(model, preproc, out, step=5, distributed=False, rank=1) is None
    assert not (out / "step_000005_adapter").exists()
    assert not (out / "adapter").exists()
    # TERM during model load: model still None -> clean no-op, no crash
    assert termination_save(None, preproc, out, step=5, distributed=False, rank=0) is None
    assert not (out / "step_000005_adapter").exists()
    assert not (out / "adapter").exists()


def test_termination_save_respects_distributed_module_wrapper(tmp_path: Path) -> None:
    out, model, preproc = _harness(tmp_path)

    class Wrapped:
        def __init__(self, inner: TinyModel) -> None:
            self.module = inner

    termination_save(
        Wrapped(model),
        preproc,
        out,
        step=3,
        distributed=True,
        rank=0,
    )
    assert (out / "step_000003_adapter" / "adapter_config.json").is_file()
    assert (out / "adapter" / "adapter_config.json").is_file()


# ---------------------------------------------------------------------------
# the handler itself — called directly, exactly as a TERM mid-loop does
# ---------------------------------------------------------------------------


def test_handler_runs_save_then_exits(tmp_path: Path, monkeypatch, capsys) -> None:
    out, model, preproc = _harness(tmp_path)
    stop = GracefulStop(
        save_fn=lambda: termination_save(
            model,
            preproc,
            out,
            step=stop.step,
            distributed=False,
            rank=0,
        )
    )
    stop.step = 7  # main() keeps this at the current step boundary
    exits: list[int] = []

    def _fake_exit(code: int) -> None:
        exits.append(code)
        raise SystemExit(code)

    monkeypatch.setattr(os, "_exit", _fake_exit)
    with pytest.raises(SystemExit) as excinfo:
        stop.handler(signal.SIGTERM, None)
    assert excinfo.value.code == 0
    assert exits == [0]
    assert stop.requested is True
    # the save ran: current-boundary step checkpoint + adapter dir
    ckpt = out / "step_000007_adapter"
    assert (ckpt / "adapter_config.json").is_file()
    assert (out / "adapter" / "adapter_config.json").is_file()
    # the same final-save print the loop exit emits + the graceful-stop stage
    captured = capsys.readouterr().out
    assert "Saved adapter to" in captured
    assert "sigterm_graceful_stop" in captured


def test_handler_is_idempotent_no_double_save(tmp_path: Path, monkeypatch) -> None:
    out, model, preproc = _harness(tmp_path)
    calls: list[int] = []

    def save_fn() -> None:
        calls.append(1)
        termination_save(model, preproc, out, step=9, distributed=False, rank=0)

    stop = GracefulStop(save_fn=save_fn)
    stop.step = 9
    monkeypatch.setattr(os, "_exit", lambda code: (_ for _ in ()).throw(SystemExit(code)))
    with pytest.raises(SystemExit):
        stop.handler(signal.SIGTERM, None)
    # a second TERM is a defensive no-op: it returns without re-running the
    # save (in production the first handler ends in os._exit, so this is only
    # reachable when the exit is intercepted)
    stop.handler(signal.SIGTERM, None)
    assert calls == [1]


def test_real_sigterm_delivery_runs_save(tmp_path: Path) -> None:
    """End-to-end: a REAL SIGTERM to a subprocess running the handler must
    run the save and exit 0 — the exact launcher-stop scenario."""
    import subprocess

    script = f"""
import os, signal, sys
from pathlib import Path
sys.path.insert(0, {str(ROOT)!r})
from training.grpo_trainer import GracefulStop, termination_save

out = Path({str(tmp_path)!r})

class FakeModel:
    def save_pretrained(self, path):
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        (path / "adapter_config.json").write_text("{{}}")
        (path / "adapter_model.safetensors").write_text("x")

class FakeBackend:
    def save_pretrained(self, path):
        Path(path).mkdir(parents=True, exist_ok=True)
        (Path(path) / "backend.marker").write_text("ok")

class FakePreprocessor:
    save_backend = FakeBackend()

stop = GracefulStop(save_fn=lambda: termination_save(
    FakeModel(), FakePreprocessor(), out, step=4, distributed=False, rank=0,
))
stop.step = 4
signal.signal(signal.SIGTERM, stop.handler)
os.kill(os.getpid(), signal.SIGTERM)  # never reached: handler os._exit(0)s
print("HANDLER-DID-NOT-EXIT")
"""
    proc = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=60
    )
    assert proc.returncode == 0, proc.stderr
    assert "HANDLER-DID-NOT-EXIT" not in proc.stdout
    ckpt = tmp_path / "step_000004_adapter"
    assert (ckpt / "adapter_config.json").is_file()
    assert (ckpt / "adapter_model.safetensors").is_file()
    assert (tmp_path / "adapter" / "adapter_config.json").is_file()


def test_handler_save_failure_exits_nonzero_not_hang(tmp_path: Path, monkeypatch, capsys) -> None:
    """A failing save must exit promptly (the launcher KILLs after 3s) with a
    visible error — never hang inside the handler."""
    exits: list[int] = []

    def _boom() -> None:
        raise RuntimeError("simulated save failure")

    stop = GracefulStop(save_fn=_boom)
    monkeypatch.setattr(
        os, "_exit", lambda code: exits.append(code) or (_ for _ in ()).throw(SystemExit(code))
    )
    with pytest.raises(SystemExit) as excinfo:
        stop.handler(signal.SIGTERM, None)
    assert excinfo.value.code == 1
    assert exits == [1]
    assert "sigterm_save_failed" in capsys.readouterr().out


def test_sigterm_payload_step_matches_inflight_boundary() -> None:
    """F2 (code-review wave): the SIGTERM resume_state payload step must be
    the IN-FLIGHT step (the checkpoint dir being written), so a relaunch
    resumes at step+1 — never replaying a step whose weights already
    absorbed its update."""
    from training.grpo_trainer import _sigterm_payload_step

    assert _sigterm_payload_step(5, 4) == 5  # in-flight wins
    assert _sigterm_payload_step(None, 4) == 4  # pre-loop TERM -> last completed
    assert _sigterm_payload_step(0, 0) == 0

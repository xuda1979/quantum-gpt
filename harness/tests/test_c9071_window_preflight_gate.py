"""C-9071: ASI2 window preflight gate -- go/no-go artifact, fail-closed.

RED first 2026-09-17: no harness/asi2_window_preflight_gate.py existed.
The C-9061 sentinel is detect-only BY DESIGN; its fire side (the C-9029
requeue) had NO preflight gate and the 07:58:46Z window burned with 0
slices (launch exit 1 pre-dispatch; SDKs absent from EVERY ASI2
interpreter). Contract under test:
  - GO requires NAMED preflight evidence: C-9066 SDK positive-control
    (every interpreter imports qiskit+pennylane+cirq, control rc==0);
    C-9051 PARITY-OK artifact; C-9038 ceiling artifact whose proven
    runner sha256+mtime STILL match the file on disk (B-223);
  - any missing/malformed/stale input writes SKIP listing ALL unmet
    preflights by name -- never a partial GO, never a raise;
  - stale window_open.json (age > window_fresh_s) never gates GO;
  - the gate NEVER launches, NEVER requeues/bounces (QUEUE.json
    byte-identical after evaluate), NEVER implements SDK/parity/ceiling;
  - every SKIP (and GO) lands an EVENTS.jsonl event
    (kind="c9071_window_gate");
  - require_go() is the consumer seam for the C-9029 dispatch path;
  - module imports no subprocess/urllib/socket.
All paths and time injected; suite never touches live harness state.
Complement to C-9067 (launch rehearsal) and C-9066/C-9051/C-9038
(artifact OWNERS; this gate only judges their artifacts).
"""

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness"))
import asi2_window_preflight_gate as G  # noqa: E402

NOW = 1_800_000_000.0
TS = "2027-09-14T05:20:00Z"  # == NOW in UTC


def _iso(t):
    import datetime

    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")
    return path


def _sdk_ok():
    return dict(
        card="C-9066",
        artifact="sdk_positive_control",
        ok=True,
        interpreters=[
            dict(
                interpreter="/usr/bin/python3", qiskit=True, pennylane=True, cirq=True, control_rc=0
            )
        ],
    )


def _parity_ok():
    return dict(
        card="C-9051",
        artifact="parity",
        verdict="PARITY-OK",
        runner_sha256={"evals/foo.py": "a" * 64},
    )


def _ceiling_ok(tmp, sha="b" * 64, mtime=None):
    import hashlib
    import os

    if mtime is None:
        mtime = NOW - 60.0
    runner = tmp / "box" / "run_asi2_base_adapter_rubric_eval.py"
    runner.parent.mkdir(parents=True, exist_ok=True)
    runner.write_text("# canonical runner\n")
    os.utime(runner, (mtime, mtime))
    real = hashlib.sha256(runner.read_bytes()).hexdigest()
    return dict(
        card="C-9038",
        artifact="ceiling",
        max_new_tokens=384,
        proven_pass=True,
        runner="box/run_asi2_base_adapter_rubric_eval.py",
        runner_sha256=real if sha == "b" * 64 else sha,
        runner_mtime=mtime,
    ), runner


def _window_open(tmp, ts=TS):
    return _write(
        tmp / "c9061" / "window_open.json",
        dict(
            card="C-9061",
            artifact="window_open",
            generated_utc=ts,
            bar=dict(pid=4242),
            consumer=dict(card="C-9029", action="requeue"),
        ),
    )


def _ctx(tmp, **kw):
    cfg = dict(
        window_dir=str(tmp / "c9061"),
        preflight_dir=str(tmp / "preflights"),
        gate_dir=str(tmp / "c9071"),
        state_dir=str(tmp / "state"),
        runner_root=str(tmp),
        clock=lambda: NOW,
    )
    cfg.update(kw)
    return G.make_ctx(**cfg)


def _all_preflights(tmp, **kw):
    _write(tmp / "preflights" / "C-9066_sdk_positive_control.json", _sdk_ok())
    _write(tmp / "preflights" / "C-9051_parity.json", _parity_ok())
    art, _ = _ceiling_ok(tmp, **kw)
    _write(tmp / "preflights" / "C-9038_ceiling.json", art)


# --------------------------------------------------------------------- GO


def test_go_when_window_open_and_all_preflights_green(tmp_path):
    _window_open(tmp_path)
    _all_preflights(tmp_path)
    verdict, art, detail = G.evaluate(_ctx(tmp_path))
    assert verdict == "GO", detail
    assert art is not None and Path(art).name == "window_gate_go.json"
    saved = json.loads(Path(art).read_text())
    assert saved["verdict"] == "GO"
    assert saved["window"]["pid"] == 4242
    assert saved["preflights"]["c9066_sdk_positive_control"]["ok"] is True
    assert saved["preflights"]["c9038_ceiling"]["runner_sha256"]


def test_go_skipped_when_window_artifact_missing(tmp_path):
    _all_preflights(tmp_path)
    verdict, art, detail = G.evaluate(_ctx(tmp_path))
    assert verdict == "SKIP"
    assert detail["unmet"]["window"] == "window_open_missing"
    assert art is not None and Path(art).name == "window_gate_skip.json"


# ------------------------------------------------------------- SKIP family


def test_skip_lists_every_unmet_preflight_not_just_first(tmp_path):
    _window_open(tmp_path)  # preflights dir left EMPTY: all three unmet
    verdict, _art, detail = G.evaluate(_ctx(tmp_path))
    assert verdict == "SKIP"
    assert set(detail["unmet"]) == {
        "c9066_sdk_positive_control",
        "c9051_parity_ok",
        "c9038_ceiling",
    }, detail["unmet"]


def test_skip_on_window_not_open_artifact(tmp_path):
    _write(
        tmp_path / "c9061" / "window_open.json",
        dict(card="C-9061", artifact="window_not_open", generated_utc=TS),
    )
    _all_preflights(tmp_path)
    verdict, _a, detail = G.evaluate(_ctx(tmp_path))
    assert verdict == "SKIP"
    assert detail["unmet"]["window"] == "window_not_open"


def test_skip_on_unparsable_window_json(tmp_path):
    p = tmp_path / "c9061" / "window_open.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{not json")
    _all_preflights(tmp_path)
    verdict, _a, detail = G.evaluate(_ctx(tmp_path))
    assert verdict == "SKIP"
    assert detail["unmet"]["window"] == "window_open_unreadable"


def test_skip_on_stale_window_open(tmp_path):
    _window_open(tmp_path, ts=_iso(NOW - 10_000.0))
    _all_preflights(tmp_path)
    verdict, _a, detail = G.evaluate(_ctx(tmp_path))
    assert verdict == "SKIP" and detail["unmet"]["window"] == "window_open_stale"


def test_skip_when_sdk_control_not_ok(tmp_path):
    _window_open(tmp_path)
    _write(
        tmp_path / "preflights" / "C-9066_sdk_positive_control.json",
        dict(card="C-9066", artifact="sdk_positive_control", ok=False),
    )
    _write(tmp_path / "preflights" / "C-9051_parity.json", _parity_ok())
    art, _ = _ceiling_ok(tmp_path)
    _write(tmp_path / "preflights" / "C-9038_ceiling.json", art)
    verdict, _a, detail = G.evaluate(_ctx(tmp_path))
    assert verdict == "SKIP"
    assert detail["unmet"]["c9066_sdk_positive_control"] == "ok_not_true"


def test_skip_when_parity_verdict_not_parity_ok(tmp_path):
    _window_open(tmp_path)
    _write(tmp_path / "preflights" / "C-9066_sdk_positive_control.json", _sdk_ok())
    _write(
        tmp_path / "preflights" / "C-9051_parity.json",
        dict(card="C-9051", artifact="parity", verdict="PARITY-DRIFT"),
    )
    art, _ = _ceiling_ok(tmp_path)
    _write(tmp_path / "preflights" / "C-9038_ceiling.json", art)
    verdict, _a, detail = G.evaluate(_ctx(tmp_path))
    assert verdict == "SKIP"
    assert detail["unmet"]["c9051_parity_ok"] == "verdict_not_PARITY-OK"


def test_skip_when_c9038_runner_sha_drifted_on_disk(tmp_path):
    """B-223: proven-in-a-different-file is not proven."""
    _window_open(tmp_path)
    _write(tmp_path / "preflights" / "C-9066_sdk_positive_control.json", _sdk_ok())
    _write(tmp_path / "preflights" / "C-9051_parity.json", _parity_ok())
    art, runner = _ceiling_ok(tmp_path)
    runner.write_text("# canonical runner\n# EDITED AFTER THE PROOF\n")
    _write(tmp_path / "preflights" / "C-9038_ceiling.json", art)
    verdict, _a, detail = G.evaluate(_ctx(tmp_path))
    assert verdict == "SKIP"
    assert detail["unmet"]["c9038_ceiling"] in ("runner_sha_drift", "runner_mtime_drift"), detail[
        "unmet"
    ]


def test_skip_when_c9038_runner_missing_on_disk(tmp_path):
    _window_open(tmp_path)
    _write(tmp_path / "preflights" / "C-9066_sdk_positive_control.json", _sdk_ok())
    _write(tmp_path / "preflights" / "C-9051_parity.json", _parity_ok())
    art, runner = _ceiling_ok(tmp_path)
    runner.unlink()
    _write(tmp_path / "preflights" / "C-9038_ceiling.json", art)
    verdict, _a, detail = G.evaluate(_ctx(tmp_path))
    assert verdict == "SKIP"
    assert detail["unmet"]["c9038_ceiling"] == "runner_missing"


# ------------------------------------------------ EVENTS + no-launch/bounce


def test_every_skip_lands_event_and_go_does_too(tmp_path):
    _window_open(tmp_path)
    _all_preflights(tmp_path)
    G.evaluate(_ctx(tmp_path))
    (tmp_path / "preflights" / "C-9066_sdk_positive_control.json").unlink()
    G.evaluate(_ctx(tmp_path))  # SKIPping pass
    lines = [
        json.loads(x)
        for x in (tmp_path / "state" / "EVENTS.jsonl").read_text().splitlines()
        if x.strip()
    ]
    kinds = [x["kind"] for x in lines]
    assert kinds.count("c9071_window_gate") == 2, lines
    got = [x["verdict"] for x in lines if x["kind"] == "c9071_window_gate"]
    assert got == ["GO", "SKIP"], got
    skip_ev = [x for x in lines if x.get("verdict") == "SKIP"][0]
    assert "c9066_sdk_positive_control" in skip_ev["unmet"]


def test_gate_never_bounces_queue_or_launches(tmp_path):
    """SKIP leaves the leg REQUEUED, not bounced: QUEUE.json untouched; the
    module carries no launch/requeue/transport machinery at all."""
    q = tmp_path / "state" / "QUEUE.json"
    _write(q, {"cards": [{"id": "C-9029", "status": "ready"}]})
    before = q.read_bytes()
    _window_open(tmp_path)  # preflights empty -> SKIP path
    G.evaluate(_ctx(tmp_path))
    assert q.read_bytes() == before
    src = (ROOT / "harness" / "asi2_window_preflight_gate.py").read_text()
    tree = ast.parse(src)
    forbidden = {"subprocess", "urllib", "socket", "http", "requests"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(a.name.split(".")[0] not in forbidden for a in node.names), node.names
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden, node.module
    for sym in ("save_queue", "requeue_card", "Popen", "os.system", "launch_leg"):
        assert sym not in src, sym


# ------------------------------------------------------------ consumer seam


def test_require_go_returns_artifact_on_go_and_raises_gateskip_on_skip(tmp_path):
    _window_open(tmp_path)
    _all_preflights(tmp_path)
    got = G.require_go(_ctx(tmp_path))
    assert got["verdict"] == "GO"
    (tmp_path / "preflights" / "C-9051_parity.json").unlink()
    try:
        G.require_go(_ctx(tmp_path))
        raise AssertionError("require_go must raise GateSkip on SKIP")
    except G.GateSkip as exc:
        assert "c9051_parity_ok" in exc.unmet

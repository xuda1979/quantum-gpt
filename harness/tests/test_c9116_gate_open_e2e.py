"""C-9116: c9071 window gate OPEN-direction end-to-end proof.

RED-basis 2026-09-18: live EVENTS.jsonl held ZERO GO rows for kind
c9071_window_gate since the SKIP loop began 05:31Z -- the gate's open
decision direction was never observed. Live-verified FIRST (evidence
precedes these tests): 2026-09-18T07:26:07Z EVENTS carried the first
SKIP->GO transition -- PASS A on the fully live dirs rc=5 unmet=
c9051_parity_ok:artifact_missing, PASS B with real fresh window_open +
sandbox preflights rc=0 GO, artifact path recorded in the GO event.
No production change was needed: the implementation already satisfied
the contract; these tests pin it so it cannot regress.

Contract under test (hermetic: tmp dirs, injected clock -- the suite
never touches live state or the network):
  - through the REAL CLI main(): SKIP exits 5, GO exits 0, and the
    printed line names the verdict + artifact;
  - every pass lands exactly one c9071_window_gate EVENTS row whose
    artifact path EXISTS on disk and whose file verdict matches the row
    (artifact/event divergence can never pass silently);
  - negative control: corrupting EACH preflight artifact one at a time
    (unreadable JSON) keeps the gate SKIP naming exactly that one unmet
    key -- never a partial GO, never a crash.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness"))
import asi2_window_preflight_gate as G  # noqa: E402

NOW = 1_800_000_000.0
TS = "2027-09-14T05:20:00Z"  # == NOW in UTC
KEYS = (
    ("C-9066_sdk_positive_control.json", "c9066_sdk_positive_control"),
    ("C-9051_parity.json", "c9051_parity_ok"),
    ("C-9038_ceiling.json", "c9038_ceiling"),
)


def _write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")
    return path


def _sdk():
    return dict(
        card="C-9066",
        artifact="sdk_positive_control",
        ok=True,
        utc=TS,
        interpreters=[
            dict(
                interpreter="/usr/bin/python3", qiskit=True, pennylane=True, cirq=True, control_rc=0
            )
        ],
    )


def _parity():
    return dict(
        card="C-9051",
        artifact="parity",
        verdict="PARITY-OK",
        runner_sha256=dict([("evals/foo.py", "a" * 64)]),
        note="C-9116 fixture doc",
    )


def _ceiling(tmp):
    import hashlib
    import os

    runner = tmp / "box" / "run_asi2_base_adapter_rubric_eval.py"
    runner.parent.mkdir(parents=True, exist_ok=True)
    runner.write_text("# canonical runner\n")
    mt = NOW - 60.0
    os.utime(runner, (mt, mt))
    sha = hashlib.sha256(runner.read_bytes()).hexdigest()
    return dict(
        card="C-9038",
        artifact="ceiling",
        max_new_tokens=1536,
        proven_pass=True,
        runner="box/run_asi2_base_adapter_rubric_eval.py",
        runner_sha256=sha,
        runner_mtime=mt,
    )


def _window(tmp):
    return _write(
        tmp / "c9061" / "window_open.json",
        dict(
            card="C-9061",
            artifact="window_open",
            generated_utc=TS,
            bar=dict(pid=4242),
            consumer=dict(card="C-9029", action="requeue"),
        ),
    )


def _all_preflights(tmp):
    _write(tmp / "preflights" / "C-9066_sdk_positive_control.json", _sdk())
    _write(tmp / "preflights" / "C-9051_parity.json", _parity())
    _write(tmp / "preflights" / "C-9038_ceiling.json", _ceiling(tmp))


def _ctx(tmp):
    return G.make_ctx(
        window_dir=str(tmp / "c9061"),
        preflight_dir=str(tmp / "preflights"),
        gate_dir=str(tmp / "c9071"),
        state_dir=str(tmp / "state"),
        runner_root=str(tmp),
        clock=lambda: NOW,
    )


def _argv(tmp):
    return [
        "--window-dir",
        str(tmp / "c9061"),
        "--preflight-dir",
        str(tmp / "preflights"),
        "--gate-dir",
        str(tmp / "c9071"),
        "--state-dir",
        str(tmp / "state"),
        "--runner-root",
        str(tmp),  # fixture runner lives under tmp, not ROOT
    ]


def _events(tmp):
    p = tmp / "state" / "EVENTS.jsonl"
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]


def _gate_rows(tmp):
    return [e for e in _events(tmp) if e.get("kind") == "c9071_window_gate"]


# ------------------------------------------------------- CLI end-to-end


def test_cli_skip_then_go_transition_records_existing_artifact_paths(tmp_path, capsys):
    _window(tmp_path)  # preflights dir absent -> all three unmet
    rc_skip = G.main(_argv(tmp_path))
    first = capsys.readouterr().out
    assert rc_skip == G.RC_SKIP == 5, rc_skip
    assert "SKIP" in first, first
    _all_preflights(tmp_path)
    rc_go = G.main(_argv(tmp_path))
    second = capsys.readouterr().out
    assert rc_go == G.RC_GO == 0, rc_go
    assert "GO" in second, second
    rows = _gate_rows(tmp_path)
    assert [r["verdict"] for r in rows] == ["SKIP", "GO"], rows
    for row in rows:
        art = Path(row["artifact"])
        assert art.exists(), row  # event path must be a real artifact
        assert json.loads(art.read_text())["verdict"] == row["verdict"], row
    skip_row, go_row = rows
    assert set(skip_row["unmet"]) == set(k for _f, k in KEYS), skip_row
    assert go_row["unmet"] == dict(), go_row
    assert Path(go_row["artifact"]).name == "window_gate_go.json", go_row
    assert go_row["window_pid"] == 4242, go_row


# --------------------------------------------------- negative controls


def test_negative_control_each_artifact_corrupted_one_at_a_time(tmp_path):
    _window(tmp_path)
    for fname, key in KEYS:
        p = tmp_path / "preflights" / fname
        if p.exists():
            p.unlink()
        _all_preflights(tmp_path)
        p.write_text("not-json-at-all")  # corrupt ONE artifact
        verdict, art, detail = G.evaluate(_ctx(tmp_path))
        assert verdict == "SKIP", (fname, detail)
        assert Path(art).name == "window_gate_skip.json", art
        assert set(detail["unmet"]) == set([key]), (fname, detail["unmet"])
        assert detail["unmet"][key] == "unreadable", (fname, detail["unmet"])


def test_negative_control_go_never_partial_when_one_preflight_missing(tmp_path):
    _window(tmp_path)
    _all_preflights(tmp_path)
    (tmp_path / "preflights" / "C-9051_parity.json").unlink()  # the live-missing key
    verdict, _art, detail = G.evaluate(_ctx(tmp_path))
    assert verdict == "SKIP"
    assert detail["unmet"] == dict(c9051_parity_ok="artifact_missing"), detail["unmet"]


# ------------------------------------------ GO artifact + event contract


def test_go_artifact_records_preflights_window_and_event_path(tmp_path):
    _window(tmp_path)
    _all_preflights(tmp_path)
    rc = G.main(_argv(tmp_path))
    assert rc == 0, rc
    go = tmp_path / "c9071" / "window_gate_go.json"
    saved = json.loads(go.read_text())
    assert saved["verdict"] == "GO"
    assert saved["window"]["pid"] == 4242
    assert saved["preflights"]["c9051_parity_ok"]["verdict"] == "PARITY-OK"
    assert saved["preflights"]["c9038_ceiling"]["max_new_tokens"] == 1536
    assert saved["consumer"]["card"] == "C-9029"
    rows = [e for e in _gate_rows(tmp_path) if e["verdict"] == "GO"]
    assert len(rows) == 1, rows
    assert rows[0]["artifact"] == str(go), rows[0]

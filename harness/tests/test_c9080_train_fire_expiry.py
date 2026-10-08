"""C-9080: ASI3 train-fire state expiry must be LOUD, never read armed.

Covers:
  1. expiry_status: an expired cutoff with fired=false classifies EXPIRED
     (never ARMED); a future cutoff is ARMED; fired is FIRED; a zombie-tagged
     file is ZOMBIE; an unparseable cutoff fails closed to UNKNOWN.
  2. rearm() clears the zombie tag (a new window is not a zombie).
  3. resource_probes.probe_train_fire surfaces the verdict in the standup
     resource line (probes/train_fire.json via run_all), EXPIRED/ZOMBIE loud.
  4. qgh._probe_results includes the train_fire line.
All state paths are injected; no test touches live harness state.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness"))

import asi3_train_fire_on_ready as w  # noqa: E402
import resource_probes as RP  # noqa: E402

PAST = "2026-09-16T23:59:00Z"
FUTURE = "2099-01-01T00:00:00Z"
NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)


def test_expired_cutoff_is_EXPIRED_not_armed():
    st = dict(pid=1, cutoff=PAST, fired=False, cycle=1)
    assert w.expiry_status(st, now=NOW) == "EXPIRED"


def test_future_cutoff_is_ARMED():
    st = dict(pid=1, cutoff=FUTURE, fired=False, cycle=1)
    assert w.expiry_status(st, now=NOW) == "ARMED"


def test_fired_is_FIRED_even_when_cutoff_past():
    st = dict(pid=1, cutoff=PAST, fired=True, cycle=1)
    assert w.expiry_status(st, now=NOW) == "FIRED"


def test_zombie_tag_is_ZOMBIE_even_when_cutoff_future():
    st = dict(pid=1, cutoff=FUTURE, fired=False, cycle=1, zombie=True, zombie_reason="census")
    assert w.expiry_status(st, now=NOW) == "ZOMBIE"


def test_unparseable_cutoff_fails_closed_to_UNKNOWN():
    st = dict(pid=1, cutoff="garbage", fired=False, cycle=1)
    assert w.expiry_status(st, now=NOW) == "UNKNOWN"


def test_rearm_clears_zombie_tag_and_stamps_new_cutoff(tmp_path):
    state = tmp_path / "st.json"
    state.write_text(json.dumps(dict(pid=9, cutoff=PAST, fired=False, cycle=1, zombie=True)))
    st = w.rearm(str(state), pid=4242, cutoff_iso=FUTURE)
    assert "zombie" not in st and "zombie_reason" not in st
    assert w.expiry_status(st, now=NOW) == "ARMED"


def test_rearm_without_new_cutoff_stays_EXPIRED_fail_closed(tmp_path):
    state = tmp_path / "st.json"
    state.write_text(json.dumps(dict(pid=9, cutoff=PAST, fired=False, cycle=1)))
    st = w.rearm(str(state), pid=4242)
    assert w.expiry_status(st, now=NOW) == "EXPIRED"


def _probe(tmp_path, state_dict):
    path = tmp_path / "asi3_train_fire_state.json"
    if state_dict is not None:
        path.write_text(json.dumps(state_dict))
    return RP.probe_train_fire(
        state_path=str(path),
        now=NOW,
        pid_alive_fn=lambda pid: False,
    )


def test_probe_train_fire_absent_state(tmp_path):
    assert _probe(tmp_path, None)["status"] == "ABSENT"


def test_probe_train_fire_expired_is_loud(tmp_path):
    st = dict(pid=81128, cutoff=PAST, fired=False, cycle=1)
    p = _probe(tmp_path, st)
    assert p["status"] == "EXPIRED"
    assert "armed" not in p["summary"].lower()
    assert "81128" in p["summary"]  # dead pid cited


def test_probe_train_fire_zombie_carries_reason(tmp_path):
    st = dict(
        pid=81128, cutoff=PAST, fired=False, cycle=1, zombie=True, zombie_reason="no-live-consumer"
    )
    p = _probe(tmp_path, st)
    assert p["status"] == "ZOMBIE"
    assert "no-live-consumer" in p["summary"]


def test_run_all_writes_train_fire_probe(tmp_path, monkeypatch):
    state = tmp_path / "asi3_train_fire_state.json"
    state.write_text(json.dumps(dict(pid=81128, cutoff=PAST, fired=False, cycle=1)))

    monkeypatch.setattr(
        RP,
        "probe_daemon",
        lambda name, port, health_fn=None, exec_probe_fn=None: dict(
            status="ok", summary="injected"
        ),
    )
    monkeypatch.setattr(
        RP, "probe_trainer", lambda port, exec_fn=None: dict(status="ok", summary="injected")
    )
    payloads = RP.run_all(str(tmp_path), train_fire_state_path=str(state))
    assert payloads["train_fire"]["status"] == "EXPIRED"
    rec = json.loads((tmp_path / "probes" / "train_fire.json").read_text())
    assert rec["summary"].startswith("EXPIRED")


def test_qgh_probe_results_includes_train_fire(tmp_path, monkeypatch):
    import qgh

    d = tmp_path / "probes"
    d.mkdir()
    (d / "train_fire.json").write_text(
        json.dumps(
            dict(ts=qgh.now_iso(), status="EXPIRED", summary="EXPIRED cutoff=2026-09-16T23:59:00Z")
        )
    )
    monkeypatch.setattr(qgh, "STATE", str(tmp_path))
    out = qgh._probe_results()
    assert "train_fire" in out
    assert out["train_fire"].startswith("EXPIRED")

"""C-9386 RED: qgh.py card commands must serialize QUEUE.json mutation under a
file lock.  A concurrent writer holding the QUEUE lock must make a card command
fail-closed (refuse to race) instead of doing a lost-update read-modify-write;
and a successful command must release the lock so a later one proceeds."""
import argparse
import importlib
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "harness"))
QGH_PATH = os.path.join(REPO, "harness", "qgh.py")
_counter = [0]


def _load_qgh(state_dir, monkeypatch):
    monkeypatch.setenv("QGH_STATE_DIR", str(state_dir))
    _counter[0] += 1
    spec = importlib.util.spec_from_file_location("qgh_c9386_%d" % _counter[0], QGH_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.cmd_init(None)
    return mod


def _read_queue(state_dir):
    with open(os.path.join(str(state_dir), "QUEUE.json"), encoding="utf-8") as f:
        return json.load(f)


def test_card_command_fails_closed_when_queue_lock_held(tmp_path, monkeypatch):
    """A live QUEUE lock held by a concurrent writer must block a card command."""
    mod = _load_qgh(tmp_path, monkeypatch)
    mod.H.save_json(os.path.join(str(tmp_path), "QUEUE.json"),
                    {"cards": [], "seq": 0})

    # A concurrent writer holds the QUEUE lock (live, not stale).
    tok = mod.H.acquire_lock(mod.QUEUE_LOCK)
    assert tok is not None, "precondition: must acquire QUEUE lock"

    args = argparse.Namespace(ids=["C-9999"])
    try:
        mod.cmd_card_requeue(args)
    except RuntimeError as e:
        assert "queue busy" in str(e)
    else:
        raise AssertionError("card command must NOT proceed while QUEUE lock is held")

    # Fail-closed: lock still held by the concurrent writer.
    assert os.path.exists(mod.QUEUE_LOCK), "lock must still be held"
    assert mod.H.release_lock(mod.QUEUE_LOCK, tok), "owner must be able to release"


def test_card_command_releases_lock_after_success(tmp_path, monkeypatch):
    """After a successful (lock-free) card command, the QUEUE lock must be gone."""
    mod = _load_qgh(tmp_path, monkeypatch)
    mod.H.save_json(os.path.join(str(tmp_path), "QUEUE.json"),
                    {"cards": [], "seq": 0})
    assert not os.path.exists(mod.QUEUE_LOCK), "precondition: queue lock absent"

    mod.cmd_card_requeue(argparse.Namespace(ids=["C-9999"]))
    assert not os.path.exists(mod.QUEUE_LOCK), "command must release the queue lock"
    q = _read_queue(tmp_path)
    assert q["seq"] == 0

import importlib.util
import json
import os

QGH_PATH = os.path.join(os.path.dirname(__file__), "..", "harness", "qgh.py")
_counter = [0]


def _load_qgh(state_dir, monkeypatch):
    monkeypatch.setenv("QGH_STATE_DIR", str(state_dir))
    _counter[0] += 1
    spec = importlib.util.spec_from_file_location(f"qgh_double_event_{_counter[0]!s}", QGH_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.cmd_init(None)
    return mod


def _card(mod, title, lane, **over):
    c = mod.H.new_card(title, lane, "goal edge", ["acceptance"], budget_min=5)
    for k, v in over.items():
        c[k] = v
    return c


def _write_queue(mod, state_dir, cards, seq=None):
    q = {"cards": cards, "seq": seq if seq is not None else len(cards)}
    mod.H.save_json(os.path.join(str(state_dir), "QUEUE.json"), q)
    return q


class _FakeProc:
    def __init__(self):
        self.pid = 999001

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    returncode = 0
    args = []

    def communicate(self, *a, **k):
        return "", ""

    def poll(self):
        return self.returncode


def _fake_popen(monkeypatch, mod, spawned):
    def fake_popen(*a, **k):
        cmd = a[0]
        if isinstance(cmd, list) and cmd and cmd[0] == "/bin/bash":
            spawned.append(cmd)
        return _FakeProc()

    monkeypatch.setattr(mod.subprocess, "Popen", fake_popen)


def test_spawn_worker_emits_single_dispatched_event(tmp_path, monkeypatch):
    mod = _load_qgh(tmp_path, monkeypatch)
    card = _card(mod, "fixer work", "fixer", id="C-0001")
    _write_queue(mod, tmp_path, [card])
    spawned = []
    _fake_popen(monkeypatch, mod, spawned)

    goal = dict(
        objective="test",
        model="test",
        target_pass="1/1",
        status="OPEN",
        created_utc="2026-09-20T00:00:00Z",
        done_criteria=list(),
    )
    mod.H.save_json(os.path.join(str(tmp_path), "GOAL.json"), goal)
    mod.H.save_json(os.path.join(str(tmp_path), "OPS.json"), dict())
    mod.H.save_json(os.path.join(str(tmp_path), "FLEET.json"), dict(agents=list()))

    brief_dir = os.path.join(str(tmp_path), "briefs")
    os.makedirs(brief_dir, exist_ok=True)
    with open(os.path.join(brief_dir, "C-0001.md"), "w") as f:
        f.write("# C-0001" + chr(10) + "Test brief" + chr(10))

    mod.cmd_dispatch(type("Args", (), dict(lane=None))())

    events_path = os.path.join(str(tmp_path), "EVENTS.jsonl")
    with open(events_path) as f:
        lines = f.readlines()

    dispatched = []
    for line in lines:
        if not line.strip():
            continue
        ev = json.loads(line)
        if ev.get("kind") == "dispatched" and ev.get("card") == "C-0001":
            dispatched.append(ev)

    msg = f"spawn_worker emitted {len(dispatched)} dispatched events for C-0001, expected 1"
    assert len(dispatched) == 1, msg

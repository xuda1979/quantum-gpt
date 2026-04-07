import copy
import importlib.util


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


EVENTS = [
    {"type": "start", "session_id": "s1", "user": "alice", "ts": 10},
    {"type": "message", "session_id": "s1", "ts": 12},
    {"type": "start", "session_id": "s2", "user": "bob", "ts": 13},
    {"type": "message", "session_id": "s1", "ts": 14},
    {"type": "message", "session_id": "s2", "ts": 15},
    {"type": "end", "session_id": "s1", "ts": 16},
]

EXPECTED = {
    "active": {
        "s2": {"user": "bob", "started_at": 13, "last_seen": 15, "messages": 1}
    },
    "history": [
        {"session_id": "s1", "user": "alice", "started_at": 10, "ended_at": 16, "messages": 2}
    ],
}


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures = []

    events = copy.deepcopy(EVENTS)
    actual = module.apply_events(events)
    if actual != EXPECTED:
        failures.append(f"apply_events returned {actual!r}, expected {EXPECTED!r}")
    if events != EVENTS:
        failures.append("apply_events mutated input events")

    for bad_events in [
        [{"type": "message", "session_id": "missing", "ts": 1}],
        [
            {"type": "start", "session_id": "dup", "user": "a", "ts": 1},
            {"type": "start", "session_id": "dup", "user": "a", "ts": 2},
        ],
        [{"type": "weird", "session_id": "x", "ts": 1}],
    ]:
        try:
            module.apply_events(copy.deepcopy(bad_events))
        except ValueError:
            continue
        except Exception as exc:
            failures.append(f"apply_events({bad_events!r}) raised {type(exc).__name__}, expected ValueError")
        else:
            failures.append(f"apply_events({bad_events!r}) did not raise ValueError")

    return {
        "passed": not failures,
        "details": failures or ["Session event log preserves state transitions and error handling"],
    }

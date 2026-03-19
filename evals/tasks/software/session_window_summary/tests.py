import copy
import importlib.util


EVENTS = [
    {"session_id": "s1", "ts": 1, "kind": "open"},
    {"session_id": "s1", "ts": 2, "kind": "message"},
    {"session_id": "s2", "ts": 3, "kind": "open"},
    {"session_id": "s2", "ts": 5, "kind": "message"},
    {"session_id": "s1", "ts": 6, "kind": "close"},
    {"session_id": "s3", "ts": 7, "kind": "open"},
    {"session_id": "s3", "ts": 8, "kind": "message"},
]

EXPECTED = {
    "active_sessions": ["s3"],
    "closed_sessions": ["s1"],
    "message_counts": {"s1": 1, "s2": 1, "s3": 1},
    "timeline": [
        "1:s1:open",
        "2:s1:message",
        "3:s2:open",
        "5:s2:message",
        "6:s1:close",
        "7:s3:open",
        "8:s3:message",
    ],
}



def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module



def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures = []

    events = copy.deepcopy(EVENTS)
    actual = module.summarize_sessions(events, active_window=1)
    if actual != EXPECTED:
        failures.append(f"summarize_sessions returned {actual!r}, expected {EXPECTED!r}")
    if events != EVENTS:
        failures.append("summarize_sessions mutated input events")

    empty = module.summarize_sessions([], active_window=3)
    if empty != {
        "active_sessions": [],
        "closed_sessions": [],
        "message_counts": {},
        "timeline": [],
    }:
        failures.append(f"empty input handling incorrect: {empty!r}")

    for bad_events in [
        ([{"session_id": "x", "ts": 1, "kind": "message"}], 1),
        ([
            {"session_id": "dup", "ts": 1, "kind": "open"},
            {"session_id": "dup", "ts": 2, "kind": "open"},
        ], 1),
        ([{"session_id": "x", "ts": 1, "kind": "close"}], 1),
        ([{"session_id": "x", "ts": 1, "kind": "weird"}], 1),
        ([], -1),
    ]:
        payload, window = bad_events
        try:
            module.summarize_sessions(copy.deepcopy(payload), active_window=window)
        except ValueError:
            continue
        except Exception as exc:
            failures.append(
                f"summarize_sessions({payload!r}, active_window={window}) raised {type(exc).__name__}, expected ValueError"
            )
        else:
            failures.append(
                f"summarize_sessions({payload!r}, active_window={window}) did not raise ValueError"
            )

    return {
        "passed": not failures,
        "details": failures or ["Session window summary preserves ordering, state transitions, and validation"],
    }

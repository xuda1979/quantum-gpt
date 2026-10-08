def summarize_sessions(events: list[dict], *, active_window: int) -> dict:
    """Summarize session activity without mutating the input event list.

    Each event has keys: session_id, ts, kind.
    Supported kinds: open, message, close.

    Output format:
    {
        "active_sessions": [sorted session ids whose latest event is within active_window of max ts and not closed],
        "closed_sessions": [sorted session ids that were explicitly closed],
        "message_counts": {session_id: count_of_message_events},
        "timeline": ["<ts>:<session_id>:<kind>", ... in original order],
    }

    Rules:
    - A message before open is invalid.
    - Opening an already-open session is invalid.
    - Closing a missing or already-closed session is invalid.
    - Unsupported kinds are invalid.
    """
    if active_window < 0:
        raise ValueError("active_window must be non-negative")

    open_sessions = {}
    closed_sessions = set()
    message_counts = {}
    timeline = []
    max_ts = None

    for event in events:
        session_id = event["session_id"]
        ts = event["ts"]
        kind = event["kind"]
        timeline.append(f"{ts}:{session_id}:{kind}")
        max_ts = ts if max_ts is None else max(max_ts, ts)

        if kind == "open":
            if session_id in open_sessions:
                raise ValueError("session already open")
            open_sessions[session_id] = ts
            message_counts.setdefault(session_id, 0)
            closed_sessions.discard(session_id)
        elif kind == "message":
            if session_id not in open_sessions:
                raise ValueError("message for inactive session")
            message_counts[session_id] = message_counts.get(session_id, 0) + 1
            open_sessions[session_id] = ts
        elif kind == "close":
            if session_id not in open_sessions:
                raise ValueError("close for inactive session")
            del open_sessions[session_id]
            closed_sessions.add(session_id)
            message_counts.setdefault(session_id, 0)
        else:
            raise ValueError("unsupported event kind")

    if max_ts is None:
        active = []
    else:
        active = sorted(
            session_id
            for session_id, last_seen in open_sessions.items()
            if max_ts - last_seen <= active_window
        )

    return {
        "active_sessions": active,
        "closed_sessions": sorted(closed_sessions),
        "message_counts": dict(sorted(message_counts.items())),
        "timeline": timeline,
    }

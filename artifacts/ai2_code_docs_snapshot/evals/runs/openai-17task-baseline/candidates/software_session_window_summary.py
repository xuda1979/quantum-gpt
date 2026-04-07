def summarize_sessions(events: list[dict], *, active_window: int) -> dict:
    """Summarize session activity while preserving input order.

    Each event must contain:
    - session_id
    - ts
    - kind: "open", "message", or "close"

    Returns:
        {
            "active_sessions": [sorted session ids that are still open and whose
                                latest activity is within active_window of max ts],
            "closed_sessions": [sorted session ids explicitly closed],
            "message_counts": {session_id: number_of_message_events},
            "timeline": ["<ts>:<session_id>:<kind>", ...],
        }
    """
    if active_window < 0:
        raise ValueError("active_window must be non-negative")

    open_sessions: dict = {}
    closed_sessions: set = set()
    message_counts: dict = {}
    timeline: list[str] = []
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
            if session_id in closed_sessions:
                closed_sessions.remove(session_id)

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
        active_sessions = []
    else:
        active_sessions = sorted(
            session_id
            for session_id, last_seen in open_sessions.items()
            if max_ts - last_seen <= active_window
        )

    return {
        "active_sessions": active_sessions,
        "closed_sessions": sorted(closed_sessions),
        "message_counts": dict(sorted(message_counts.items())),
        "timeline": timeline,
    }

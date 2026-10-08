def apply_events(events):
    state = {"active": {}, "history": []}

    for event in events:
        kind = event["type"]
        session_id = event["session_id"]

        if kind == "start":
            if session_id in state["active"]:
                raise ValueError(f"session already active: {session_id}")
            state["active"][session_id] = {
                "user": event["user"],
                "started_at": event["ts"],
                "last_seen": event["ts"],
                "messages": 0,
            }
            continue

        if session_id not in state["active"]:
            raise ValueError(f"session not active: {session_id}")

        if kind == "message":
            active = state["active"][session_id]
            active["messages"] += 1
            active["last_seen"] = event["ts"]
            continue

        if kind == "end":
            active = state["active"].pop(session_id)
            state["history"].append(
                {
                    "session_id": session_id,
                    "user": active["user"],
                    "started_at": active["started_at"],
                    "ended_at": event["ts"],
                    "messages": active["messages"],
                }
            )
            continue

        raise ValueError(f"unknown event type: {kind}")

    state["history"].sort(key=lambda item: (item["started_at"], item["session_id"]))
    return state

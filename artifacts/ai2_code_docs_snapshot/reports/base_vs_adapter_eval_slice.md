# Base vs Adapter Eval Slice Plan

Purpose: fixed 5-example comparison slice for qualitative base-vs-adapter checks on the local fast-mini eval set.

## Examples
### 1. `template_session_window_summary_10_ab155b35`
**Prompt**
```text
Please solve this coding task in Python:

Task: Session window summary with ordered history
```
**Reference answer prefix**
```python
# Implementation
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
```

### 2. `template_measurement_bug_repair_17_9fa09a1c`
**Prompt**
```text
Write a Python solution for the following task:

Task: Measurement mapping bug repair

Return the solution as Python code only.
```
**Reference answer prefix**
```python
# Solution
def measurement_mapping(bitstring: str) -> dict[str, int]:
    """Map q0/q1 to integer measurement results from a two-bit string.

    Input ordering is q1q0, so the rightmost bit is q0.
    """
    if len(bitstring) != 2 or any(ch not in "01" for ch in bitstring):
        raise ValueError("expected a two-bit measurement string")
    return {"q0": int(bitstring[1]), "q1": int(bitstring[0])}
```

### 3. `template_stabilizer_tableau_update_repair_9_24ca0492`
**Prompt**
```text
Write a Python solution for the following task:

Task: Stabilizer tableau single-qubit update repair
```
**Reference answer prefix**
```python
# Solution
def _normalize_pauli(label: str) -> str:
    normalized = label.strip().upper()
    if normalized not in {"I", "X", "Y", "Z"}:
        raise ValueError(f"unsupported Pauli operator: {label!r}")
    return normalized


_CONJUGATION_RULES = {
    "H": {
        "I": (1, "I"),
        "X": (1, "Z"),
        "Y": (-1, "Y"),
        "Z": (1, "X"),
    },
    "S": {
        "I": (1, "I"),
        "X": (1, "Y"),
        "Y": (-1, "X"),
        "Z": (1, "Z"),
```

### 4. `template_session_event_log_5_ba6d5385`
**Prompt**
```text
Please solve this coding task in Python:

Task: Session event log state machine

Return the solution as Python code only.
```
**Reference answer prefix**
```python
# Solution
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
```

### 5. `template_session_window_summary_18_3c89bcaf`
**Prompt**
```text
Please solve this coding task in Python:

Task: Session window summary with ordered history

Return only the code, no explanations.
```
**Reference answer prefix**
```python
# Implementation
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
```

## Suggested manual comparison rubric

For each example, compare base model output vs adapter output on:
- correct required function/class names
- presence of obvious input validation
- adherence to code-only output
- semantic proximity to the reference solution
- obvious test-likely failures (wrong return type, missing helper, wrong field names)

## Next command candidates

Base model generation and adapter-loaded generation should both be run against exactly these prompts to keep comparisons stable.

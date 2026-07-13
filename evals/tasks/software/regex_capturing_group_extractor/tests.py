import importlib.util


def _load(path: str):
    spec = importlib.util.spec_from_file_location("candidate", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def run_tests(candidate_path: str) -> dict:
    failures: list[str] = []
    try:
        mod = _load(candidate_path)
    except Exception as e:  # noqa: BLE001
        return {"passed": False, "details": [f"import failed: {e}"]}

    # 1. Basic named-group extraction
    pat = r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
    out = mod.extract(pat, "2026-07-07")
    if out != {"year": 2026, "month": 7, "day": 7}:
        failures.append(f"extract date: {out!r}, expected coerced ints")

    # 2. No match returns None
    if mod.extract(pat, "not a date") is not None:
        failures.append("extract on non-match should return None")

    # 3. coerce_int=False keeps strings
    out_str = mod.extract(pat, "2026-07-07", coerce_int=False)
    if out_str != {"year": "2026", "month": "07", "day": "07"}:
        failures.append(f"coerce_int=False: {out_str!r}")

    # 4. extract_many handles mixed match/no-match
    many = mod.extract_many(pat, ["2026-07-07", "nope", "2025-01-02"])
    if many[0] != {"year": 2026, "month": 7, "day": 7} or many[1] is not None:
        failures.append(f"extract_many mixed: {many!r}")

    # 5. parse_log_line on a realistic line
    line = "2026-07-07T18:30:00 ERROR auth: login failed for user=alice"
    rec = mod.parse_log_line(line)
    if rec is None:
        failures.append("parse_log_line returned None for a valid line")
    else:
        if rec.get("level") != "ERROR":
            failures.append(f"level = {rec.get('level')!r}, expected 'ERROR'")
        if rec.get("component") != "auth":
            failures.append(f"component = {rec.get('component')!r}, expected 'auth'")
        if "message" not in rec or "failed" not in rec["message"]:
            failures.append(f"message not extracted correctly: {rec.get('message')!r}")

    # 6. None for missing group inside an alternation
    pat2 = r"(?P<a>\d+)|(?P<b>[a-z]+)"
    out_a = mod.extract(pat2, "123", coerce_int=False)
    out_b = mod.extract(pat2, "abc", coerce_int=False)
    if out_a.get("a") != "123" or out_a.get("b") is not None:
        failures.append(f"alternation a: {out_a!r}")
    if out_b.get("b") != "abc" or out_b.get("a") is not None:
        failures.append(f"alternation b: {out_b!r}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "regex named-group extraction, int coercion, no-match handling, alternation all correct"
        ],
    }

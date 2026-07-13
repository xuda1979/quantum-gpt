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

    lines = [
        "2026-07-07T18:00:00 INFO auth: login ok",
        "2026-07-07T18:00:05 WARN auth: rate limit near",
        "2026-07-07T18:00:10 ERROR db: connection lost",
        "2026-07-07T18:01:00 INFO auth: login ok",
        "2026-07-07T18:01:03 WARNING cache: evicting key",  # alternate spelling
        "this is not a log line",
        "2026-07-07T18:02:00 DEBUG net: ping",
    ]

    # 1. parse_line correctness
    rec = mod.parse_line(lines[0])
    if rec is None or rec["level"] != "INFO" or rec["component"] != "auth":
        failures.append(f"parse_line(INFO) = {rec!r}")

    # 2. WARNING -> WARN normalization
    rec_w = mod.parse_line(lines[4])
    if rec_w is None or rec_w["level"] != "WARN":
        failures.append(f"WARNING normalization failed: {rec_w!r}")

    # 3. parse_lines returns (parsed, bad)
    parsed, bad = mod.parse_lines(lines)
    if len(parsed) != 6 or len(bad) != 1:
        failures.append(f"parse_lines: parsed={len(parsed)} bad={len(bad)}")

    # 4. count_by_level
    counts = mod.count_by_level(parsed)
    if counts.get("INFO") != 2 or counts.get("WARN") != 2 or counts.get("ERROR") != 1:
        failures.append(f"count_by_level = {counts!r}")

    # 5. group_by_window with 60s windows
    windows = mod.group_by_window(parsed, 60)
    # Expect 3 distinct windows: 18:00:00, 18:01:00, 18:02:00
    distinct_windows = sorted({w for w, _, _ in windows})
    if len(distinct_windows) != 3:
        failures.append(f"expected 3 windows, got {len(distinct_windows)}")
    # 18:00 window should contain INFO, WARN, ERROR
    win0_levels = sorted({lvl for w, lvl, _ in windows if w == distinct_windows[0]})
    if win0_levels != ["ERROR", "INFO", "WARN"]:
        failures.append(f"first window levels = {win0_levels!r}")

    # 6. Invalid window raises
    try:
        mod.group_by_window(parsed, 0)
        failures.append("group_by_window(0) did not raise")
    except ValueError:
        pass

    # 7. summarize integration
    s = mod.summarize(lines, window_seconds=60)
    if s["total_lines"] != 7 or s["parsed"] != 6 or s["unparseable"] != 1:
        failures.append(f"summarize counts wrong: {s!r}")

    return {
        "passed": not failures,
        "details": failures
        or ["log parsing, level normalization, aggregation, time-window grouping all correct"],
    }

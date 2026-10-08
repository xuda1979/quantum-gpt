"""Parse log lines, aggregate by level, and group into fixed time windows.

Line format (one per line):
    YYYY-MM-DDTHH:MM:SS LEVEL component: message

Levels are normalized to {DEBUG, INFO, WARN, ERROR}. Time windows are
expressed in whole seconds. The aggregator returns:
- a per-level count,
- a list of (window_start, level, count) tuples for the requested window size,
- the list of unparseable lines.
"""

import re
from collections import Counter, defaultdict
from datetime import datetime

LINE_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>DEBUG|INFO|WARN|WARNING|ERROR)\s+"
    r"(?P<component>[\w.-]+):\s+(?P<message>.*)$"
)

LEVEL_NORMALIZE = {"WARNING": "WARN"}


def parse_line(line: str) -> dict | None:
    m = LINE_RE.match(line.strip())
    if m is None:
        return None
    level = LEVEL_NORMALIZE.get(m.group("level"), m.group("level"))
    return {
        "ts": datetime.fromisoformat(m.group("ts")),
        "level": level,
        "component": m.group("component"),
        "message": m.group("message"),
    }


def parse_lines(lines: list[str]) -> tuple[list[dict], list[str]]:
    parsed, bad = [], []
    for ln in lines:
        rec = parse_line(ln)
        if rec is None:
            bad.append(ln)
        else:
            parsed.append(rec)
    return parsed, bad


def count_by_level(parsed: list[dict]) -> dict[str, int]:
    c: Counter = Counter(r["level"] for r in parsed)
    return dict(c)


def group_by_window(parsed: list[dict], window_seconds: int) -> list[tuple[datetime, str, int]]:
    """Return (window_start, level, count) tuples, sorted by window_start then level."""
    if window_seconds <= 0:
        raise ValueError("window_seconds must be positive")
    buckets: dict[tuple[datetime, str], int] = defaultdict(int)
    for r in parsed:
        epoch = r["ts"].timestamp()
        window_start_ts = int(epoch - (epoch % window_seconds))
        window_start = datetime.fromtimestamp(window_start_ts)
        buckets[(window_start, r["level"])] += 1
    return [
        (w, lvl, cnt)
        for (w, lvl), cnt in sorted(buckets.items(), key=lambda kv: (kv[0][0], kv[0][1]))
    ]


def summarize(lines: list[str], window_seconds: int = 60) -> dict:
    parsed, bad = parse_lines(lines)
    return {
        "total_lines": len(lines),
        "parsed": len(parsed),
        "unparseable": len(bad),
        "by_level": count_by_level(parsed),
        "windows": group_by_window(parsed, window_seconds),
        "unparseable_lines": bad,
    }

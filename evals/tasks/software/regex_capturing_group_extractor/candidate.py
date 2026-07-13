"""Extract named capturing groups from a regex against lines.

Useful for turning ad-hoc log lines into structured records without
resorting to a full parsing library. The extractor must:
- compile a regex with named groups
- return None for non-matches
- return a dict {name: str} for matches, with all named groups present
- coerce integer-looking values to int when `coerce_int=True`
"""

import re


def compile_pattern(pattern: str) -> re.Pattern:
    return re.compile(pattern)


def extract(pattern: str, line: str, coerce_int: bool = True) -> dict | None:
    """Match `pattern` against `line`. Return a dict of named groups or None."""
    m = compile_pattern(pattern).search(line)
    if m is None:
        return None
    out = {}
    for k, v in m.groupdict().items():
        if v is None:
            out[k] = None
        elif coerce_int and re.fullmatch(r"-?\d+", v):
            out[k] = int(v)
        else:
            out[k] = v
    return out


def extract_many(pattern: str, lines: list[str], coerce_int: bool = True) -> list[dict | None]:
    return [extract(pattern, ln, coerce_int=coerce_int) for ln in lines]


# A common log-line pattern used as the reference example.
LOG_PATTERN = r"(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\s+(?P<level>INFO|WARN|ERROR)\s+(?P<component>\w+):\s+(?P<message>.*)"


def parse_log_line(line: str) -> dict | None:
    return extract(LOG_PATTERN, line, coerce_int=False)

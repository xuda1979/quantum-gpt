#!/usr/bin/env python3
"""log_to_table.py — deterministic log → structured table parser.

The harness uses this to extract structured data from log files instead of
having agents read logs conversationally. Every agent that needs log analysis
runs THIS script, not their own eyeballing.

Usage:
    python3 harness/scripts/log_to_table.py <log_file> [--format json|md|csv]
    python3 harness/scripts/log_to_table.py --status-md     # parse STATUS.md tail
    python3 harness/scripts/log_to_table.py --verdicts      # parse verdict files
    python3 harness/scripts/log_to_table.py --train-probe   # parse train probe json
    python3 harness/scripts/log_to_table.py --suite-log <file>  # parse test suite log

Outputs deterministic tables. Never guesses. Missing data = "N/A".
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
STATE = REPO / "harness" / "state"


def parse_status_md(path: Path, tail_lines: int = 2000) -> list[dict]:
    """Parse STATUS.md timestamped entries into structured rows.

    2026-09-23 fix: default tail was 50 lines — the log's tail is usually
    daemon-flap noise (BOX-EXEC lines), so the parser returned NO DATA while
    hundreds of timestamped entries sat just above the window. Window is now
    2000 lines and every '- <date> <time> <TZ>' line parses (not just the
    'tick #' format)."""
    rows = []
    lines = path.read_text(errors="replace").splitlines()
    for line in lines[-tail_lines:]:
        if not line.startswith("- 20"):
            continue
        m = re.match(r"- (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) (\S+) — tick #(\d+): (.*)", line)
        if m:
            rows.append(
                {
                    "timestamp": m.group(1),
                    "tz": m.group(2),
                    "tick": int(m.group(3)),
                    "summary": m.group(4)[:120],
                }
            )
            continue
        # General timestamped entry (not tick-formatted): keep the first 120 chars
        m = re.match(r"- (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) (\S+) — (.*)", line)
        if m:
            rows.append(
                {
                    "timestamp": m.group(1),
                    "tz": m.group(2),
                    "summary": m.group(3)[:120],
                }
            )
    return rows


def parse_verdicts(verdicts_dir: Path) -> list[dict]:
    """Parse all verdict JSON files into a table."""
    rows = []
    if not verdicts_dir.exists():
        return rows
    for f in sorted(verdicts_dir.glob("*.json")):
        try:
            d = json.loads(f.read_text())
            rows.append(
                {
                    "file": f.name,
                    "card": d.get("card", "N/A"),
                    "pass_adapter": d.get("pass_adapter", "N/A"),
                    "adapter_applied": d.get("adapter_applied", "N/A"),
                    "probe_differs": d.get("probe_differs", "N/A"),
                    "n_pass": d.get("n_pass", "N/A"),
                    "n_total": d.get("n_total", "N/A"),
                    "verdict": d.get("verdict", "N/A"),
                }
            )
        except (json.JSONDecodeError, KeyError):
            rows.append({"file": f.name, "error": "parse_failed"})
    return rows


def parse_train_probe(probe_path: Path) -> dict:
    """Parse the training probe JSON into a flat dict."""
    if not probe_path.exists():
        return {"status": "NO_PROBE_FILE"}
    try:
        d = json.loads(probe_path.read_text())
        return {
            "status": d.get("status", "N/A"),
            "step": d.get("step", "N/A"),
            "loss": d.get("loss", "N/A"),
            "reward": d.get("reward", "N/A"),
            "rms_for_update": d.get("rms_for_update", "N/A"),
            "last_update_step": d.get("last_update_step", "N/A"),
            "uptime_s": d.get("uptime_s", "N/A"),
            "pid": d.get("pid", "N/A"),
        }
    except (json.JSONDecodeError, FileNotFoundError):
        return {"status": "PARSE_FAILED"}


def parse_suite_log(path: Path) -> list[dict]:
    """Parse a pytest/suite log into pass/fail per-test rows."""
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(errors="replace").splitlines():
        m = re.match(r"^(PASSED|FAILED|ERROR|SKIPPED)\s+(.+)", line.strip())
        if m:
            rows.append({"status": m.group(1), "test": m.group(2)})
        # Also catch pytest format: "test_file.py::test_name PASSED"
        m2 = re.match(r"^(.+::\S+)\s+(PASSED|FAILED|ERROR|SKIPPED)", line.strip())
        if m2:
            rows.append({"test": m2.group(1), "status": m2.group(2)})
    return rows


def render_table(rows: list[dict], fmt: str = "md") -> str:
    """Render rows as markdown/json/csv table."""
    if not rows:
        return "NO DATA"
    if fmt == "json":
        return json.dumps(rows, indent=2)
    if fmt == "csv":
        buf = []
        buf.append(",".join(rows[0].keys()))
        for r in rows:
            buf.append(",".join(str(r.get(k, "")) for k in rows[0].keys()))
        return "\n".join(buf)
    # markdown
    cols = list(rows[0].keys())
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(c, "N/A")) for c in cols) + " |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Deterministic log → table parser")
    ap.add_argument("log_file", nargs="?", help="log file to parse")
    ap.add_argument("--format", choices=["md", "json", "csv"], default="md")
    ap.add_argument("--status-md", action="store_true", help="parse .sapo-loop/STATUS.md")
    ap.add_argument("--verdicts", action="store_true", help="parse verdict files")
    ap.add_argument("--train-probe", action="store_true", help="parse train probe JSON")
    ap.add_argument("--suite-log", action="store_true", help="parse test suite log")
    args = ap.parse_args()

    if args.status_md:
        rows = parse_status_md(REPO / ".sapo-loop" / "STATUS.md")
        print(render_table(rows, args.format))
    elif args.verdicts:
        rows = parse_verdicts(STATE / "verdicts")
        print(render_table(rows, args.format))
    elif args.train_probe:
        d = parse_train_probe(STATE / "probes" / "train.json")
        print(render_table([d], args.format))
    elif args.suite_log and args.log_file:
        rows = parse_suite_log(Path(args.log_file))
        print(render_table(rows, args.format))
    elif args.log_file:
        # generic: try to parse key=value lines
        rows = []
        for line in Path(args.log_file).read_text(errors="replace").splitlines():
            m = re.findall(r"(\w+)=([^\s,]+)", line)
            if m:
                rows.append(dict(m))
        print(render_table(rows if rows else [{"line": "no key=value pairs found"}], args.format))
    else:
        ap.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

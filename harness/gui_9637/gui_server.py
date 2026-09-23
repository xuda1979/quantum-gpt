#!/usr/bin/env python3
"""gui_9637/gui_server.py — script-driven real-time system GUI (C-9637).
Serves a single-page dashboard polling /api/items every 5s. Pure stdlib;
reads ONLY harness ledgers via gui_9637.collector. ZERO LLM/API calls."""

from __future__ import annotations

import argparse
import json
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import collector  # noqa: E402  (sys.path seam must precede import)

REFRESH_MS = 5000
DASHBOARD_JS = (_HERE / "dashboard.js").read_text()


def _serialize(v):
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    return str(v)


def api_payload():
    """Build JSON payload with sectioned labeled items."""
    items = collector.collect_all()
    secs = collector.split_sections(items)
    sections = []
    total = 0
    for s in secs:
        slist = [{"label": lbl, "value": _serialize(val)} for lbl, val in s["items"]]
        total += len(slist)
        sections.append({"name": s["name"], "count": len(slist), "items": slist})
    return {
        "refresh_ms": REFRESH_MS,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "sections": sections,
        "total_items": total,
    }


_CSS = [
    "body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#0f1420;color:#e6ecf5}",
    ".tabs{display:flex;flex-wrap:wrap;gap:6px;padding:10px}",
    ".tab{padding:6px 12px;border-radius:14px;background:#1c2440;cursor:pointer;font-size:13px}",
    ".tab.active{background:#3b82f6;color:#fff}",
    ".card{background:#171e30;border:1px solid #26324d;border-radius:10px;padding:10px;margin:12px}",
    ".card h3{margin:0 0 8px;color:#93c5fd;font-size:15px}",
    "ul{margin:0;padding-left:0;list-style:none}",
    "li{display:flex;justify-content:space-between;padding:3px 4px;border-bottom:1px solid #1f2a45;font-size:13px}",
    "li .k{color:#cbd5e1;margin-right:12px}",
    "li .v{color:#86efac;word-break:break-word;max-width:60%;text-align:right}",
    "#top{display:flex;align-items:center;gap:14px;padding:8px 12px;background:#0b0f1a;position:sticky;top:0}",
    "#count{color:#fbbf24}",
    "#recon{padding:12px;color:#64748b;font-size:13px}",
]
_CSS = "".join(_CSS)


def build_index_html():
    """Single-page HTML dashboard embedding inline CSS + external JS."""
    return (
        "<!doctype html><html><head><meta charset=utf-8>"
        "<title>QG Harness — Live System GUI</title><style>" + _CSS + "</style></head>"
        "<body>"
        "<div id=top><h1>QG Goal Harness — Live System Dashboard</h1>"
        "<span id=count></span> <span id=gen></span></div>"
        "<div class=tabs id=tabs></div>"
        "<div id=sec-title style=color:#93c5fd;font-weight:bold;margin-left:12px></div>"
        "<div id=items-here style=margin-left:12px;color:#64748b></div>"
        "<div id=recon></div>"
        "<div id=out></div>"
        "<script src=/dashboard.js></script>"
        "</body></html>"
    )


class Handler(BaseHTTPRequestHandler):
    def _ok(self, body, ctype):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            self._ok(build_index_html().encode("utf-8"), "text/html; charset=utf-8")
        elif path == "/dashboard.js":
            self._ok(DASHBOARD_JS.encode("utf-8"), "application/javascript; charset=utf-8")
        elif path == "/api/items":
            self._ok(json.dumps(api_payload()).encode("utf-8"), "application/json; charset=utf-8")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):
        pass


def main(argv):
    ap = argparse.ArgumentParser(description="QG harness live GUI")
    ap.add_argument("--port", type=int, default=8960)
    ap.add_argument("--host", default="127.0.0.1")
    a = ap.parse_args(argv)
    n = api_payload()["total_items"]
    print(f"QG live GUI: http://{a.host}:{a.port}  refresh={REFRESH_MS}ms  total_items={n}")
    srv = ThreadingHTTPServer((a.host, a.port), Handler)
    srv.serve_forever()


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])

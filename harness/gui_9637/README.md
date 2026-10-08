# QG Harness - Live System GUI (Card C-9637)

Script-driven real-time system dashboard showing 500+ human-readable items from the
harness ledgers, refreshed live every 5 seconds. Zero LLM/API calls - pure stdlib
Python reading the ledgers (EVENTS.jsonl, QUEUE.json, FLEET.json, GOAL.json, OPS.json,
probes, verdict files, STATUS.md, REPORT.md, DASHBOARD.md).

Files in this directory:
- collector.py : harvests 500+ labeled (label, value) items into 9 sections.
- gui_server.py : stdlib http.server single-page dashboard + /api/items + /dashboard.js.
- dashboard.js : client JS polling /api/items every 5 s (setInterval 5000ms).
- tests: ../tests/test_gui_9637_*.py (TDD: item count>=500, labels readable, server).

Data sections (9) covered: Goal; Queue / Fleet; Training; System Testing; Evaluation;
Unit Testing; Errors / Events; Operations; Ledgers.

How to launch:
   python3 harness/gui_9637/gui_server.py --port 8960
Then open http://127.0.0.1:8960 (single page, auto-refresh every 5 s).

Live instance / verification URL:
   Server runs at http://127.0.0.1:8960 (single page, human-readable)
   JSON API: http://127.0.0.1:8960/api/items returns total_items + labeled sections.
   Live serving check (server started, HTTP GET /, /dashboard.js, /api/items 200):
   total_items = 665, refresh_ms = 5000, 9 sections covered.

JSON API: GET http://127.0.0.1:8960/api/items returns total_items, refresh_ms, and
sections[].{name, count, items[]}.{label, value}.

Run the TDD tests:
   python3 -m pytest harness/tests/test_gui_9637_item_count.py harness/tests/test_gui_9637_labels_readable.py harness/tests/test_gui_9637_server.py -q

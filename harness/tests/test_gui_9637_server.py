import os
import sys

import conftest  # noqa: F401

p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gui_9637")
sys.path.insert(0, p)


def test_api_items_at_least_500():
    import gui_server

    data = gui_server.api_payload()
    assert data["total_items"] >= 500, f"expected >=500 items, got {data['total_items']}"


def test_api_at_least_six_sections():
    import gui_server

    data = gui_server.api_payload()
    assert len(data["sections"]) >= 6, f"got {len(data['sections'])} sections"


def test_api_required_sections_present():
    import gui_server

    data = gui_server.api_payload()
    names = [s["name"] for s in data["sections"]]
    for req in (
        "Training",
        "Evaluation",
        "Unit Testing",
        "System Testing",
        "Queue / Fleet",
        "Errors / Events",
    ):
        assert req in names, f"missing section {req}"


def test_page_refreshes_every_5s_via_js():
    import gui_server

    js = gui_server.DASHBOARD_JS
    assert "setInterval" in js
    assert "fetchItems" in js
    # auto-refresh must be <= 5000 ms
    assert "5000" in js or "4000" in js or "3000" in js
    assert "/api/items" in js


def test_page_serves_single_page_and_api():
    import gui_server

    html = gui_server.build_index_html()
    assert "<!doctype html>" in html.lower()
    assert "/dashboard.js" in html
    assert "/api/items" in html or "dashboard" in html
    assert "id=tabs" in html and "id=out" in html


def test_api_item_labels_are_strings():
    import gui_server

    for sec in gui_server.api_payload()["sections"]:
        for it in sec["items"]:
            assert isinstance(it["label"], str) and it["label"].strip()

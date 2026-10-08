import os
import sys

# ensure conftest seam is not bypassed
import conftest  # noqa: F401

p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gui_9637")
sys.path.insert(0, p)
import collector


def test_item_count_at_least_500():
    items = collector.collect_all()
    # strip Section markers
    data = [it for it in items if it[0] != "Section"]
    assert len(data) >= 500, f"expected >=500 labeled data items, got {len(data)}"


def test_at_least_six_sections():
    secs = collector.split_sections(collector.collect_all())
    assert len(secs) >= 6, f"expected >=6 sections, got {len(secs)}"


def test_required_sections_present():
    secs = collector.split_sections(collector.collect_all())
    names = set(s["name"] for s in secs)
    for req in (
        "Training",
        "Evaluation",
        "Unit Testing",
        "System Testing",
        "Queue / Fleet",
        "Errors / Events",
    ):
        assert req in names, f"missing required section {req}"

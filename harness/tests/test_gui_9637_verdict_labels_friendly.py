"""TDD RED test for C-9637: verdict labels must not leak raw file names like
'c9072_canary_verdict.json' or 'c9030_base_verdict_blocked_20260919T002404Z.json'.
Acceptance #4 requires human-readable display names - no raw variable/file names.
"""

import os
import re
import sys

import conftest  # noqa: F401

p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gui_9637")
sys.path.insert(0, p)
import collector


def test_no_raw_verdict_filenames_in_labels():
    """Verdict labels carrying the raw <card>_<...>_verdict.json token are cryptic
    and must be re-labelled to a friendly display name."""
    items = collector.collect_all()
    bad = []
    for label, _v in items:
        label = str(label)
        if label == "Section":
            continue
        if re.search(r"(?:^|[/ ])c\d+_[A-Za-z0-9_]*verdict", label):
            bad.append(label)
        if ".json" in label and "current json" not in label.lower():
            bad.append(label)
    assert not bad, f"raw verdict filenames leaked into labels: {bad[:10]}"


def test_no_id_timestamp_verdict_names():
    """Verification tag for verdict items should be friendly (e.g. card id + label),
    not the raw base_verdict_blocked_<UTC> filename."""
    items = collector.collect_all()
    bad = [
        label
        for label, v in items
        if str(label) != "Section"
        and re.search(r"verdict_blocked|_base_verdict|_canary_verdict", str(label))
    ]
    assert not bad, f"cryptic verdict filename still present: {bad[:10]}"

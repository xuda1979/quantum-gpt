import os
import re
import sys

import conftest  # noqa: F401

p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gui_9637")
sys.path.insert(0, p)
import collector


def _is_cryptic(label):
    # cryptic = raw var names like c9148_probe_refresh, bare snake_case keys,
    # or ids like ASI2 without a friendly prefix context
    if re.search(r"c\d+", label):
        return True
    # bare snake_case word (all lowercase with underscores) that is not a
    # numeral/known safe token and not part of a friendly phrase
    if re.fullmatch(r"[a-z0-9_]+(?:_[a-z0-9_]+)+", label):
        return True
    return False


def test_all_labels_human_readable():
    items = collector.collect_all()
    cryptic = [str(label) for label, v in items if label != "Section" and _is_cryptic(str(label))]
    assert not cryptic, f"cryptic labels: {cryptic[:20]}"


def test_no_raw_variable_examples():
    # the acceptance explicitly forbids raw keys like "c9148_probe_refresh" or
    # bare keys; ensure none of the harness raw keys leak as labels
    items = collector.collect_all()
    bad = [label for label, v in items if re.search(r"_probe_refresh|c9148", str(label))]
    assert not bad, f"raw variable names leaked: {bad}"


def test_labels_have_values():
    items = collector.collect_all()
    for label, v in items:
        if label == "Section":
            continue
        assert v is not None, f"label {label} has None value"

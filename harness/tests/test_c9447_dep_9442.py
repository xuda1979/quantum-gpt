import json


def test_c9394_depends_on_c9442():
    """C-9447: C-9394 (s97 re-eval) must depend on C-9442 (leg script deploy)."""
    q = json.load(open("harness/state/QUEUE.json"))
    card = [c for c in q["cards"] if c["id"] == "C-9394"][0]
    assert "C-9442" in card["deps"], "C-9394 missing dep C-9442"

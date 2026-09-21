"""C-9590 lesson: dead eval cards must not block fresh checkpoint evals."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.qgh import auto_eval_on_checkpoint


def _card(cid, title, status, lane="evaluator"):
    return {"id": cid, "title": title, "status": status, "lane": lane}


def test_dead_eval_card_does_not_block():
    queue = {"cards": [_card("C-9590", "Auto-eval checkpoint step_000035_adapter from run", "dead")]}
    card = auto_eval_on_checkpoint(queue, "step_000035_adapter", "run")
    assert card is not None, "dead card must not block fresh eval"


def test_live_eval_card_blocks():
    queue = {"cards": [_card("C-9615", "Auto-eval checkpoint step_000035_adapter from run", "running")]}
    assert auto_eval_on_checkpoint(queue, "step_000035_adapter", "run") is None


def test_bounced_eval_card_does_not_block():
    queue = {"cards": [_card("C-9551", "Auto-eval checkpoint step_000031_adapter from run", "bounced")]}
    assert auto_eval_on_checkpoint(queue, "step_000031_adapter", "run") is not None

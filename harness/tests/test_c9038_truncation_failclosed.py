"""Card C-9038: truncation fail-closed (P0 ceiling).

NOTE: test_slice_record_truncated_true_on_cap_hit imports the runner
module (torch + transformers + peft = ~14s), so it needs a 120s timeout.

The canonical 18-task runner capped completions at --max-new-tokens
(default 384) with NO truncation evidence in the slice records and NO
scorer handling: a cap-cut completion could bank a pass, so 18/18 was
arithmetically unreachable while every downstream verdict looked
honest. Contract pinned here (RED first):

  - the runner records truncated=true when generation emits the FULL
    max_new_tokens budget (cap hit == finish reason "length") and
    truncated=false on an EOS stop; every slice record carries the
    field.
  - the verdict scorer treats truncated=true as NOT-pass fail-closed
    even when the grader said passed, and a record with NO usable
    truncation field is NOT-pass too -- UNKNOWN is never silently read
    as untruncated.
  - the NEXT-leg launcher wrappers (run_holdout_leg1/2.py) carry the
    banked ceiling budget from
    harness/state/preflights/C-9038_ceiling.json.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "harness"))

import scripts.holdout_verdict as hv  # noqa: E402

ART = ROOT / "harness/state/preflights/C-9038_ceiling.json"
RUNNER_REL = "scripts/run_asi2_base_adapter_rubric_eval.py"
CANDIDATE_SRC = "def encode_bits(b):\n    return b + '0'\n"


def _runner_module():
    spec = importlib.util.spec_from_file_location("c9038_canon_runner", ROOT / RUNNER_REL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------- stubs
class _FakeRender:
    @staticmethod
    def apply_chat_template(messages, **kw):
        return "PROMPT"


class _FakeText:
    eos_token_id = 1

    def __call__(self, prompt_text, return_tensors=None, **kw):
        import torch

        return {"input_ids": torch.tensor([[2, 3]])}  # prompt_len = 2

    def decode(self, ids, skip_special_tokens=True):
        return CANDIDATE_SRC


class _FakeBackend:
    text_backend = _FakeText()
    render_backend = _FakeRender()


class _FakeModel:
    """Greedy cap semantics: at most max_new_tokens NEW ids, then stop."""

    def __init__(self, solution_len):
        import torch

        self._torch = torch
        self.solution_len = solution_len

    def generate(self, input_ids=None, max_new_tokens=0, **kw):
        budget = min(int(max_new_tokens), self.solution_len)
        full = input_ids[0].tolist() + [7] * budget
        return self._torch.tensor([full])


def _run_one(tmp_path, budget, solution_len=8):
    """run_model over one synthetic task with a stub grader."""
    runner = _runner_module()
    orig = runner.run_single_file_test
    runner.run_single_file_test = (  # grader stub: keep the unit hermetic
        lambda *a, **k: {"passed": True, "details": ["stub-grader"]}
    )
    try:
        task_json = tmp_path / "task.json"
        meta = {"id": "task_a", "name": "t", "domain": "d", "category": "c"}
        task_json.write_text(json.dumps(meta))
        args = argparse.Namespace(
            output=tmp_path / "scores.json",
            device="cpu",
            max_new_tokens=budget,
            harness_timeout=30,
        )
        records = runner.run_model(
            "adapter", _FakeModel(solution_len), _FakeBackend(), [(task_json, meta)], args
        )
    finally:
        runner.run_single_file_test = orig
    assert len(records) == 1
    return records[0]


# ---------------------------------------------------------------- tests
def test_slice_record_truncated_true_on_cap_hit(tmp_path):
    """A completion cut at max_new_tokens records truncated=true."""
    rec = _run_one(tmp_path, budget=4, solution_len=8)
    assert rec["truncated"] is True, rec


def test_slice_record_truncated_false_on_eos_stop(tmp_path):
    """A completion finishing inside the budget records truncated=false."""
    rec = _run_one(tmp_path, budget=16, solution_len=8)
    assert rec["truncated"] is False, rec


def test_scorer_marks_truncated_record_not_pass():
    """truncated=true is NOT-pass fail-closed even with passed=true."""
    scores = {
        "records": [
            {"model": "adapter", "task_id": "task_a", "passed": True, "truncated": True},
            {"model": "base", "task_id": "task_a", "passed": False, "truncated": False},
        ]
    }
    adapter, base, _recs, marks = hv._passes_from_scores(scores, ["task_a"], "legX")
    assert adapter["task_a"] is False, "a cap-cut completion must never bank a pass"
    reason = " ".join(marks["adapter"].get("task_a", []))
    assert hv.TRUNCATED_NOT_PASS in reason, marks


def test_scorer_marks_missing_truncation_info_not_pass():
    """A record with NO truncation field is NOT-pass, never silently zero."""
    scores = {
        "records": [
            {"model": "adapter", "task_id": "task_a", "passed": True},
            {"model": "base", "task_id": "task_a", "passed": False},
        ]
    }
    adapter, base, _recs, marks = hv._passes_from_scores(scores, ["task_a"], "legX")
    assert adapter["task_a"] is False, "missing truncation info is NOT-pass fail-closed"
    reason = " ".join(marks["adapter"].get("task_a", []))
    assert hv.TRUNCATION_INFO_MISSING_NOT_PASS in reason, marks


def test_wrapper_budget_matches_banked_ceiling():
    """The NEXT-leg wrappers carry the banked ceiling budget, not 384."""
    doc = json.loads(ART.read_text())
    assert doc.get("artifact") == "ceiling"
    ceiling = doc.get("max_new_tokens")
    assert isinstance(ceiling, int) and not isinstance(ceiling, bool)
    assert ceiling > 0

    def _load(rel, name):
        spec = importlib.util.spec_from_file_location(name, ROOT / rel)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    leg1 = _load("scripts/run_holdout_leg1.py", "c9038_leg1")
    leg2 = _load("scripts/run_holdout_leg2.py", "c9038_leg2")
    assert (
        leg1.DEFAULT_MAX_NEW_TOKENS == ceiling
    ), "leg1 wrapper budget must equal the banked ceiling"
    assert (
        leg2.DEFAULT_MAX_NEW_TOKENS == ceiling
    ), "leg2 wrapper budget must equal the banked ceiling"

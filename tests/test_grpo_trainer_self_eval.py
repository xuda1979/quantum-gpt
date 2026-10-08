"""Coverage backlog #3 (2026-08-25): the self-eval / frozen-judge path.

_self_evaluate_code / _model_comprehensive_scores / _parse_self_eval_score /
_parse_model_dim_scores — the trainer's model-as-judge reward components.
These tests pin the parse contracts (score normalization, dimension clamping,
None semantics) and the fail-closed behavior of the judge calls (unusable
backend / crashing generation -> 0.0 / None, never a step-killing exception).
"""

from __future__ import annotations

import sys
from argparse import Namespace
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.grpo_trainer import (  # noqa: E402
    _model_comprehensive_scores,
    _parse_model_dim_scores,
    _parse_self_eval_score,
    _self_evaluate_code,
)

# ---------------------------------------------------------------------------
# _parse_self_eval_score — 0-10 -> 0-1 normalization
# ---------------------------------------------------------------------------


def test_parse_self_eval_score_json_block() -> None:
    assert _parse_self_eval_score('{"score": 8}') == pytest.approx(0.8)
    assert _parse_self_eval_score('thinking\n{"score": 6.5}\nend') == pytest.approx(0.65)
    assert _parse_self_eval_score('{"score": 10}') == pytest.approx(1.0)
    # JSON present but no score key -> the documented 5.0 default
    assert _parse_self_eval_score('{"other": 1}') == pytest.approx(0.5)


def test_parse_self_eval_score_text_fallbacks() -> None:
    assert _parse_self_eval_score("score: 7") == pytest.approx(0.7)
    assert _parse_self_eval_score("7/10") == pytest.approx(0.7)
    assert _parse_self_eval_score("the answer is 3 out of 10") == pytest.approx(0.3)
    assert _parse_self_eval_score("I rate it 9/10 overall") == pytest.approx(0.9)


def test_parse_self_eval_score_clamps_and_neutral() -> None:
    assert _parse_self_eval_score('{"score": 12}') == pytest.approx(1.0)
    assert _parse_self_eval_score('{"score": -3}') == pytest.approx(0.0)
    assert _parse_self_eval_score("no numbers here at all") == pytest.approx(0.5)
    assert _parse_self_eval_score("") == pytest.approx(0.5)
    assert _parse_self_eval_score("{broken json") == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# _parse_model_dim_scores — per-dimension parse + clamp + None semantics
# ---------------------------------------------------------------------------


def test_parse_model_dim_scores_valid_and_clamped() -> None:
    parsed = _parse_model_dim_scores(
        '{"correctness": 0.9, "runnability": 1.0, "result_correctness": 0.4,'
        ' "efficiency": 1.5, "quality": -0.2, "evidence": "x"}'
    )
    assert parsed is not None
    assert parsed["correctness"] == pytest.approx(0.9)
    assert parsed["runnability"] == pytest.approx(1.0)
    assert parsed["result_correctness"] == pytest.approx(0.4)
    assert parsed["efficiency"] == pytest.approx(1.0)  # clamped
    assert parsed["quality"] == pytest.approx(0.0)  # clamped


def test_parse_model_dim_scores_none_semantics() -> None:
    # missing dims -> None; all-None -> None
    parsed = _parse_model_dim_scores('{"correctness": 0.5}')
    assert parsed is not None
    assert parsed["runnability"] is None
    # bools are NOT scores (the isinstance guard excludes them)
    assert _parse_model_dim_scores('{"correctness": true}') is None
    # unparseable -> None
    assert _parse_model_dim_scores("no json") is None
    assert _parse_model_dim_scores("") is None
    assert _parse_model_dim_scores('{"correctness": "high"}') is None


# ---------------------------------------------------------------------------
# judge call paths — fake model + fake tokenizer harness
# ---------------------------------------------------------------------------


class _FakeTokenizer:
    pad_token_id = 0

    def __init__(self, response_text: str) -> None:
        self.response_text = response_text

    def apply_chat_template(
        self, messages, tokenize=True, return_tensors="pt", add_generation_prompt=True
    ):
        # a 4-token prompt; the response tokens follow at ids 10+
        return torch.tensor([[1, 2, 3, 4]])

    def decode(self, token_ids, skip_special_tokens=True):
        return "".join(
            self.response_text[int(i) - 10]
            for i in token_ids
            if 10 <= int(i) < 10 + len(self.response_text)
        )


class _FakeModel:
    def __init__(self, response_text: str, input_len: int = 4) -> None:
        self.response_text = response_text
        self.input_len = input_len
        self.generate_calls = 0

    def generate(self, input_ids=None, **kwargs):
        self.generate_calls += 1
        ids = list(range(1, self.input_len + 1)) + [10 + i for i in range(len(self.response_text))]
        return torch.tensor([ids])


def _args() -> Namespace:
    return Namespace(
        self_eval_judge_max_tokens=64,
        self_eval_judge_temperature=0.7,
        model_judge_max_tokens=64,
        model_judge_temperature=0.0,
    )


def test_self_evaluate_code_end_to_end_with_tokenizer() -> None:
    model = _FakeModel('{"score": 7.5}')
    backend = Namespace(tokenizer=_FakeTokenizer('{"score": 7.5}'))
    score = _self_evaluate_code(
        "def solve(): return 1",
        {"meta": {"description": "demo"}},
        model,
        backend,
        _args(),
        "cpu",
    )
    assert score == pytest.approx(0.75)
    assert model.generate_calls == 1


def test_self_evaluate_code_encode_chat_backend() -> None:
    model = _FakeModel("score: 6")
    response_text = "score: 6"
    backend = Namespace(
        encode_chat=lambda messages, add_generation_prompt=True: [1, 2, 3, 4],
        decode=lambda ids: "".join(
            response_text[int(i) - 10] for i in ids if 10 <= int(i) < 10 + len(response_text)
        ),
        pad_token_id=0,
    )
    score = _self_evaluate_code(
        "x = 1",
        {"meta": {}},
        model,
        backend,
        _args(),
        "cpu",
    )
    assert score == pytest.approx(0.6)


def test_self_evaluate_code_fails_closed() -> None:
    # backend without tokenizer or encode_chat -> 0.0
    score = _self_evaluate_code(
        "x = 1",
        {"meta": {}},
        _FakeModel("anything"),
        Namespace(),
        _args(),
        "cpu",
    )
    assert score == 0.0
    # crashing generation -> 0.0, never an exception

    class _Boom:
        def generate(self, **kwargs):
            raise RuntimeError("judge died")

    score = _self_evaluate_code(
        "x = 1",
        {"meta": {}},
        _Boom(),
        Namespace(tokenizer=_FakeTokenizer("x")),
        _args(),
        "cpu",
    )
    assert score == 0.0


def test_model_comprehensive_scores_dispatch_and_fail_closed() -> None:
    dims_json = '{"correctness": 0.8, "runnability": 0.9, "result_correctness": 0.5, "efficiency": 0.7, "quality": 0.6, "evidence": "ok"}'
    model = _FakeModel(dims_json)
    backend = Namespace(tokenizer=_FakeTokenizer(dims_json))
    parsed = _model_comprehensive_scores(
        "x = 1",
        {"meta": {"description": "demo"}},
        "tests passed",
        model,
        backend,
        _args(),
        "cpu",
    )
    assert parsed is not None
    assert parsed["correctness"] == pytest.approx(0.8)
    # unusable judge output -> None
    model2 = _FakeModel("no json here")
    backend2 = Namespace(tokenizer=_FakeTokenizer("no json here"))
    assert (
        _model_comprehensive_scores(
            "x = 1",
            {"meta": {}},
            "evidence",
            model2,
            backend2,
            _args(),
            "cpu",
        )
        is None
    )
    # backend without tokenizer/encode_chat -> None
    assert (
        _model_comprehensive_scores(
            "x = 1",
            {"meta": {}},
            "evidence",
            model2,
            Namespace(),
            _args(),
            "cpu",
        )
        is None
    )


def test_model_comprehensive_scores_encode_chat_path() -> None:
    dims_json = '{"correctness": 0.5, "runnability": 0.5, "result_correctness": 0.5, "efficiency": 0.5, "quality": 0.5}'
    model = _FakeModel(dims_json)
    backend = Namespace(
        encode_chat=lambda messages, add_generation_prompt=True: [1, 2, 3, 4],
        decode=lambda ids: "".join(
            dims_json[int(i) - 10] for i in ids if 10 <= int(i) < 10 + len(dims_json)
        ),
        pad_token_id=0,
    )
    parsed = _model_comprehensive_scores(
        "x = 1",
        {"meta": {}},
        "evidence",
        model,
        backend,
        _args(),
        "cpu",
    )
    assert parsed is not None
    assert parsed["correctness"] == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# code-review wave (2026-08-26) findings
# ---------------------------------------------------------------------------


def test_parse_self_eval_score_brace_inside_string_value() -> None:
    r"""F6: the JSON extraction regex `\{[^}]+\}` stopped at the FIRST '}' —
    a '}' inside a string value (e.g. "state {|0>,|1>}") truncated the match
    and json.loads failed -> 0.5 neutral instead of the real score."""
    assert _parse_self_eval_score(
        '{"score": 8, "analysis": "state {|0>,|1>} matches"}'
    ) == pytest.approx(0.8)
    assert _parse_self_eval_score('nested {"score": 7} with {braces} around') == pytest.approx(0.7)


def test_parse_model_dim_scores_brace_inside_string_value() -> None:
    """F6 for the frozen-judge path: a '}' inside an evidence string must not
    null out all five dimension scores."""
    parsed = _parse_model_dim_scores(
        '{"correctness": 0.9, "runnability": 0.8, "result_correctness": 0.7,'
        ' "efficiency": 0.6, "quality": 0.5, "evidence": "state {|0>,|1>}"}'
    )
    assert parsed is not None
    assert parsed["correctness"] == pytest.approx(0.9)


def test_parse_self_eval_score_prose_prefers_scaled_or_score_form() -> None:
    """F7: the fallback grabbed the FIRST bare number in prose — "3 compile
    errors; I score it 7/10" scored 0.3 instead of 0.7. The scaled form and
    the score: form must win; an ambiguous bare number is neutral."""
    assert _parse_self_eval_score(
        "The solution has 3 compile errors; I score it 7/10"
    ) == pytest.approx(0.7)
    assert _parse_self_eval_score(
        "There were 2 failures, I give this 6 out of 10"
    ) == pytest.approx(0.6)  # scaled form wins over the bare 2
    assert _parse_self_eval_score("score: 7") == pytest.approx(0.7)
    assert _parse_self_eval_score("I rate it 9/10 overall") == pytest.approx(0.9)
    # ambiguous bare number (no scale, no score:) -> neutral, not the
    # first number grabbed
    assert _parse_self_eval_score("There were 2 syntax errors") == pytest.approx(0.5)


def test_repair_generate_requests_dict_return() -> None:
    """F1 (code-review wave): the teacher-free repair generate call must pass
    return_dict_in_generate=True — without it, generate returns a plain
    Tensor and `outputs.sequences` raises AttributeError, which
    teacher_free_self_repair's broad except swallows: self-repair silently
    never repairs (each attempt only burns a generation)."""
    from argparse import Namespace
    from types import SimpleNamespace

    from training.grpo_trainer import _self_repair_failing_candidate

    class _RepairModel:
        def generate(self, **kwargs):
            assert kwargs.get(
                "return_dict_in_generate"
            ), "repair generate must request the dict form"
            return SimpleNamespace(sequences=torch.zeros((1, 8), dtype=torch.long))

    class _TextBackend:
        def __call__(self, text, return_tensors="pt"):
            return {
                "input_ids": torch.zeros((1, 4), dtype=torch.long),
                "attention_mask": torch.ones((1, 4)),
            }

        def decode(self, ids, skip_special_tokens=True):
            return "def solve():\n    return 1\n"

    class _RenderBackend:
        def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=True):
            return "fix the code"

    backend = SimpleNamespace(text_backend=_TextBackend(), render_backend=_RenderBackend())
    task_dir = Path(__file__).resolve().parents[1] / "evals" / "tasks"
    tests_py = Path(__file__).resolve().parents[1] / "evals" / "runner" / "single_candidate_eval.py"
    task = {
        "tests_py": tests_py,
        "task_dir": task_dir,
        "meta": {"candidate_file": "candidate.py"},
        "required_interface": [],
        "behavior_hints": [],
    }
    args = Namespace(max_new_tokens=16, harness_timeout_seconds=30)
    out = _self_repair_failing_candidate(
        model=_RepairModel(),
        text_preprocessor=backend,
        device="cpu",
        test_harness=None,
        task=task,
        code="def solve():\n    return 1\n",
        task_prompt="fix it",
        result={"passed": False, "details": ["boom"]},
        args=args,
        max_rounds=1,
        temperature=1.0,
    )
    # the attempt must NOT have died on the missing dict flag
    attempted = out.get("attempted") or []
    assert attempted, out
    failures = attempted[0].get("failures") or []
    assert not any("return_dict_in_generate" in str(f) for f in failures), failures

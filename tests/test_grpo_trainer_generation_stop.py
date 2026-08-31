"""TDD: rollout generation must STOP at the closing code fence or the first
EOS — whichever comes first — with max-new-tokens only as backstop.

2026-08-25 (generation-efficiency finding): every step's generation ran the
FULL 2048-token cap (eos_termination_rate 0.0 on all steps; 60-110 min/step;
~1 step/hour -> the 500-step budget is ~3 weeks). Two root causes, both
trainer-side:
  (a) `configured_eos_token_ids` resolved EOS from the MODEL config only —
      a base config without eos_token_id meant generate never stopped on EOS
      and the diagnostic rate was a permanent 0.0 artifact;
  (b) the fence-stop regex required `````python\n```` with NO whitespace —
      fast tokenizers insert spaces on decode ("``` python \n"), so the
      closing-fence criterion never fired.

Tests (a) synthetic generation logit patterns (tiny GPT2 + forced token
sequences) that emit a fence/EOS early -> the candidate stops there; (b) no
regression in code extraction (extracted_code_chars == the fenced region);
(c) the resolution fallback + diagnostics count tokenizer-EOS terminations
(train-pass cap untouched — covered by the existing suites).

2026-08-26 (r10 rollout wave, lane #22 ROLLOUT WATCH + debug-lane findings):
  (d) 3-way stop-reason breakdown (eos / fence / cap) in diagnostics —
      `fence_terminated` + `fence_termination_rate` make fence-stops
      observable separately from EOS and from truncation; a fence closed at
      the max-token cap is COMPLETE, not truncated;
  (e) `cap_run_with_fence_opener` diagnostic — a cap-truncated completion
      containing any "```" opener is a fence-stop-regression class (same-line
      opener "```python x=1" or a versioned tag): observed live in run-6 S1
      (2048-token cap run with a fenced region, extracted 323/5459 chars);
  (f) extraction consistency with the (IGNORECASE, any-tag) fence opener —
      "```Python" and "```python3" must extract the code, not leak the tag;
  (g) tail-only decode in StopAfterClosedCodeFence (O(N) instead of O(N^2)
      per completion — the 2048-cap worst case paid ~4.2M decode-tokens);
  (h) SYNTHETIC STOP MARKER at the fence (r10 lever, run-6 evidence: S1-S5
      eos_termination_rate 0.0 — the model NEVER samples EOS, so it is never
      trained to terminate; the marker appends the resolved EOS id after a
      fence-closed completion so the fence-close position trains the model
      to emit the real end token). Old-policy and train-pass log-probs both
      consume the SAME augmented ids, so the importance ratio stays exact;
      the train-pass cap drops the marker tail when the cap cuts.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest
import torch
from tokenizers import Tokenizer, models
from transformers import (
    GPT2Config,
    GPT2LMHeadModel,
    LogitsProcessor,
    LogitsProcessorList,
    PreTrainedTokenizerFast,
    StoppingCriteriaList,
)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# has_closed_code_fence is a generation-module primitive (module boundary);
# grpo_trainer does not re-export it (importing it here from the trainer
# breaks collection whenever the trainer's import list is normalized).
from training.generation import has_closed_code_fence  # noqa: E402
from training.grpo_trainer import (  # noqa: E402
    SYSTEM_PROMPT,
    StopAfterClosedCodeFence,
    append_fence_stop_markers,
    build_generation_diagnostics,
    build_prompt,
    configured_eos_token_ids,
    extract_code,
    generate_group,
    render_generation_prompt,
)
from training.grpo_utils import build_grpo_step_record  # noqa: E402
from training.text_preprocessor_backend import TextPreprocessorBackend  # noqa: E402

VOCAB = {
    "```": 0,
    "python": 1,
    "\n": 2,
    "x": 3,
    " = ": 4,
    "1": 5,
    "trailing": 6,
    "<|endoftext|>": 60,
    "<pad>": 61,
    "<s>": 62,
    "<unk>": 63,
}
EOS_ID = 60


def make_tokenizer() -> PreTrainedTokenizerFast:
    t = Tokenizer(models.WordLevel(VOCAB, unk_token="<unk>"))
    tok = PreTrainedTokenizerFast(
        tokenizer_object=t,
        eos_token="<|endoftext|>",
        pad_token="<pad>",
        bos_token="<s>",
        unk_token="<unk>",
    )
    return tok


def make_model_without_eos() -> GPT2LMHeadModel:
    """A tiny causal LM whose config OMITS eos_token_id — the base-model
    config class behind the 0.0 eos_termination_rate artifact."""
    cfg = GPT2Config(n_layer=1, n_head=1, n_embd=16, vocab_size=64)
    cfg.eos_token_id = None
    cfg.bos_token_id = None
    cfg.pad_token_id = None
    model = GPT2LMHeadModel(cfg)
    model.eval()
    return model


class _ForcedTokens(LogitsProcessor):
    """Force exact token ids at absolute positions (version-stable)."""

    def __init__(self, forced: dict[int, int]) -> None:
        self.forced = dict(forced)

    def __call__(self, input_ids: torch.Tensor, scores: torch.Tensor) -> torch.Tensor:
        pos = int(input_ids.shape[1])
        if pos in self.forced:
            tok = self.forced[pos]
            scores = scores.clone()
            scores.fill_(-1000.0)
            scores[:, tok] = 1000.0
        return scores


# ---------------------------------------------------------------------------
# (c) EOS resolution: model config -> tokenizer fallback
# ---------------------------------------------------------------------------


def test_configured_eos_token_ids_falls_back_to_tokenizer() -> None:
    model = make_model_without_eos()
    tokenizer = make_tokenizer()
    # model config omits EOS -> tokenizer's eos_token_id must be resolved
    assert configured_eos_token_ids(model, tokenizer) == {EOS_ID}
    # without the tokenizer (legacy callers) -> empty, unchanged
    assert configured_eos_token_ids(model) == set()
    # model config WITH eos + tokenizer -> union
    model.config.eos_token_id = 5
    assert configured_eos_token_ids(model, tokenizer) == {5, EOS_ID}
    # neither -> empty
    model.config.eos_token_id = None
    tokenizer.eos_token_id = None
    assert configured_eos_token_ids(model, tokenizer) == set()


# ---------------------------------------------------------------------------
# (a) synthetic generation: EOS early -> candidate stops there
# ---------------------------------------------------------------------------


def test_generation_stops_at_forced_eos_early() -> None:
    model = make_model_without_eos()
    tokenizer = make_tokenizer()
    inputs = tokenizer("<s>", return_tensors="pt")
    stop_ids = configured_eos_token_ids(model, tokenizer)
    assert stop_ids == {EOS_ID}
    # forced sequence: x, ' = ', 1, EOS at position 3 of the generation
    out = model.generate(
        **inputs,
        max_new_tokens=32,
        do_sample=False,
        eos_token_id=sorted(stop_ids),
        logits_processor=LogitsProcessorList([_ForcedTokens({1: 3, 2: 4, 3: 5, 4: EOS_ID})]),
        return_dict_in_generate=True,
    )
    gen = out.sequences[0, 1:]
    assert gen.numel() == 4, gen  # stopped at EOS, not at the 32 cap
    assert int(gen[-1]) == EOS_ID
    # the synthetic WordLevel fast tokenizer inserts spaces on decode —
    # compare spacing-insensitively; the stop semantics are what matter
    assert " ".join(tokenizer.decode(gen, skip_special_tokens=True).split()) == "x = 1"


def test_generation_without_stop_ids_runs_to_cap() -> None:
    """The bug class: no resolved EOS + no fence -> full cap (the 2048-token
    steps). Contrast for the fix above."""
    model = make_model_without_eos()
    tokenizer = make_tokenizer()
    inputs = tokenizer("<s>", return_tensors="pt")
    out = model.generate(
        **inputs,
        max_new_tokens=32,
        do_sample=False,
        logits_processor=LogitsProcessorList([_ForcedTokens({1: 3, 2: 4, 3: 5, 4: EOS_ID})]),
        return_dict_in_generate=True,
    )
    gen = out.sequences[0, 1:]
    assert gen.numel() == 32  # EOS ignored, cap reached


# ---------------------------------------------------------------------------
# (a) synthetic generation: closing fence early -> candidate stops there
# ---------------------------------------------------------------------------


def test_generation_stops_at_closing_code_fence_before_trailing() -> None:
    """Fast tokenizers insert spaces on decode ("``` python \n") — the fence
    regex must still fire (space-tolerant) and stop BEFORE trailing prose."""
    model = make_model_without_eos()
    tokenizer = make_tokenizer()
    inputs = tokenizer("<s>", return_tensors="pt")
    out = model.generate(
        **inputs,
        max_new_tokens=32,
        do_sample=False,
        logits_processor=LogitsProcessorList(
            [_ForcedTokens({1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 2, 8: 0, 9: 6})]
        ),
        stopping_criteria=StoppingCriteriaList(
            [StopAfterClosedCodeFence(tokenizer, prompt_length=1)]
        ),
        return_dict_in_generate=True,
    )
    gen = out.sequences[0, 1:]
    assert gen.numel() == 8, gen  # stops at the closing fence (token 0)
    decoded = tokenizer.decode(gen, skip_special_tokens=True)
    assert "trailing" not in decoded
    assert has_closed_code_fence(decoded)


def test_has_closed_code_fence_is_space_tolerant() -> None:
    # the space-inserting fast-tokenizer decode form (previously unmatched)
    assert has_closed_code_fence("``` python \n x = 1 \n ```")
    # the canonical no-space form
    assert has_closed_code_fence("```python\nx = 1\n```")
    # bare fence (no language tag), both forms
    assert has_closed_code_fence("```\nx = 1\n```")
    assert has_closed_code_fence("``` \n x = 1 \n ```")
    # opening fence only -> NOT closed
    assert not has_closed_code_fence("```python\nx = 1")
    assert not has_closed_code_fence("no fence here")


# ---------------------------------------------------------------------------
# (b) code extraction: the fence-stopped response still extracts exactly
# ---------------------------------------------------------------------------


def test_fence_stop_response_extraction_matches_fenced_region() -> None:
    response = "```python\nx = 1\n```"
    assert has_closed_code_fence(response)
    assert extract_code(response) == "x = 1"
    # diagnostics: extracted_code_chars == the fenced region, and a
    # tokenizer-EOS-terminated completion counts as eos-terminated (the
    # measurement-artifact fix: rate was a permanent 0.0). The raw response
    # is a NON-fence text here so the EOS is a natural model EOS, not a
    # fence-stop marker (marker-augmented completions are fence-class).
    diag = build_generation_diagnostics(
        raw_responses=["x = 1"],
        codes=[extract_code(response)],
        completion_token_ids=[torch.tensor([3, 4, 5, EOS_ID])],
        max_new_tokens=2048,
        eos_token_ids={EOS_ID},
    )
    assert diag["extracted_code_chars"] == [len("x = 1")]
    assert diag["eos_terminated"] == [True]
    assert diag["eos_termination_rate"] == 1.0
    assert diag["truncation_rate"] == 0.0


# ---------------------------------------------------------------------------
# (f) extraction consistency with the IGNORECASE / any-tag fence opener
# ---------------------------------------------------------------------------


def test_extract_code_is_case_insensitive_for_python_tag() -> None:
    # the stop regex is IGNORECASE; extraction must not leak the "Python" tag
    response = "```Python\nx = 1\n```"
    assert has_closed_code_fence(response)
    assert extract_code(response) == "x = 1"


def test_extract_code_accepts_versioned_language_tag() -> None:
    # "```python3\n" — the r9 regex only allowed python|py|bare; a versioned
    # tag must still open a fence AND extract only the code (not "3\nx = 1")
    response = "```python3\nx = 1\n```"
    assert has_closed_code_fence(response)
    assert extract_code(response) == "x = 1"


def test_closed_fence_detected_with_versioned_and_cased_tags() -> None:
    assert has_closed_code_fence("```python3\nx = 1\n```")
    assert has_closed_code_fence("```Python \n x = 1 \n ```")
    assert has_closed_code_fence("```qsharp\nq = 1\n```")
    # conservative: same-line opener still NOT a fence (documented below)
    assert not has_closed_code_fence("```python x=1\n```")


def test_extract_code_matches_fence_stop_region_with_nested_fence() -> None:
    # a closing "```" inside the code block closes the fence EARLY; the stop
    # region and the extracted region must be the SAME fragment (the
    # extraction invariant the fence-stop relies on)
    response = "```python\ndef f():\n    return '```'\nx = 1\n```"
    assert has_closed_code_fence(response)
    assert extract_code(response) == "def f():\n    return '"


# ---------------------------------------------------------------------------
# (d) diagnostics: 3-way stop-reason breakdown + cap-with-fence observable
# ---------------------------------------------------------------------------


def test_diagnostics_separate_eos_fence_and_cap_stop_reasons() -> None:
    fence_stopped = torch.tensor([0, 1, 2, 3, 4, 5, 7, 0])  # ends at "```"
    eos_natural = torch.tensor([3, 4, 5, EOS_ID])
    cap_run = torch.tensor([3, 4, 5, 6])  # length == cap, no fence, no EOS
    diag = build_generation_diagnostics(
        raw_responses=[
            "```python\nx = 1\n```",
            "x = 1",
            "x = 1 trailing prose without a fence",
        ],
        codes=["x = 1", "x = 1", "x = 1 trailing prose without a fence"],
        completion_token_ids=[fence_stopped, eos_natural, cap_run],
        max_new_tokens=4,
        eos_token_ids={EOS_ID},
    )
    assert diag["eos_terminated"] == [False, True, False]
    assert diag["fence_terminated"] == [True, False, False]
    assert diag["truncated"] == [False, False, True]
    assert diag["eos_termination_rate"] == pytest.approx(1 / 3)
    assert diag["fence_termination_rate"] == pytest.approx(1 / 3)
    assert diag["truncation_rate"] == pytest.approx(1 / 3)


def test_diagnostics_fence_closed_at_cap_is_complete_not_truncated() -> None:
    # a fence closing EXACTLY at max_new_tokens is complete: cap + fence but
    # no EOS must NOT count as truncation (debug-lane follow-up 2)
    response = "```python\nx = 1\n```"
    diag = build_generation_diagnostics(
        raw_responses=[response],
        codes=[extract_code(response)],
        completion_token_ids=[torch.tensor([0, 1, 2, 3, 4, 5, 2, 0])],
        max_new_tokens=8,
        eos_token_ids={EOS_ID},
    )
    assert diag["truncated"] == [False]
    assert diag["truncation_rate"] == 0.0
    assert diag["fence_terminated"] == [True]


def test_diagnostics_flag_truncated_cap_run_with_fence_opener() -> None:
    # cap-run whose raw text contains ANY "```" opener (same-line opener or a
    # tag the conservative regex misses) — the fence-stop-regression class
    # observed live in run-6 S1 (2048-cap run, fenced region 323/5459 chars)
    diag = build_generation_diagnostics(
        raw_responses=["```python x=1\n```\ntrailing prose to the cap"],
        codes=["x=1\n```\ntrailing prose to the cap"],
        completion_token_ids=[torch.tensor([0] * 32)],
        max_new_tokens=32,
        eos_token_ids={EOS_ID},
    )
    assert diag["truncated"] == [True]
    assert diag["cap_run_with_fence_opener"] == [True]
    assert diag["cap_run_with_fence_opener_rate"] == 1.0
    diag_clean = build_generation_diagnostics(
        raw_responses=["plain prose without any fence to the cap"],
        codes=["plain prose without any fence to the cap"],
        completion_token_ids=[torch.tensor([6] * 32)],
        max_new_tokens=32,
        eos_token_ids={EOS_ID},
    )
    assert diag_clean["cap_run_with_fence_opener"] == [False]


def test_diagnostics_marker_appended_completion_counts_as_terminated() -> None:
    # the r10 synthetic-stop-marker form: ids end in the EOS id, raw has a
    # closed fence -> the completion is a FENCE stop, never truncated. The
    # synthetic marker is the fence-close training target, NOT a natural
    # model EOS: it must not double-count as eos_terminated (the three stop
    # reasons partition completions: fence + eos + truncated == 1).
    response = "```python\nx = 1\n```"
    diag = build_generation_diagnostics(
        raw_responses=[response],
        codes=[extract_code(response)],
        completion_token_ids=[torch.tensor([0, 1, 2, 3, 4, 5, 2, 0, EOS_ID])],
        max_new_tokens=2048,
        eos_token_ids={EOS_ID},
    )
    assert diag["eos_terminated"] == [False]
    assert diag["fence_terminated"] == [True]
    assert diag["truncated"] == [False]


def test_stop_reason_identity_holds_per_completion() -> None:
    # Production shape (marker path): fence-closed completions carry the
    # appended EOS id in the ids while the raw text closes a code fence.
    # The three stop reasons must partition the completion set exactly once
    # (fence + eos + truncated == 1 per completion); before the r18 identity
    # fix, the marker-augmented completion counted as BOTH eos and fence
    # (sum == 2) and eos_termination_rate could no longer reveal "model
    # never samples EOS" (the run-6 diagnostic the rates were built for).
    fence_with_marker = torch.tensor([0, 1, 2, 3, 4, 5, 2, 0, EOS_ID])
    eos_natural = torch.tensor([3, 4, 5, EOS_ID])
    cap_run = torch.tensor([3, 4, 5, 6])
    diag = build_generation_diagnostics(
        raw_responses=[
            "```python\nx = 1\n```",
            "x = 1",
            "x = 1 trailing prose without a fence",
        ],
        codes=["x = 1", "x = 1", "x = 1 trailing prose without a fence"],
        completion_token_ids=[fence_with_marker, eos_natural, cap_run],
        max_new_tokens=4,
        eos_token_ids={EOS_ID},
    )
    for i in range(3):
        identity = sum(
            bool(diag[key][i]) for key in ("eos_terminated", "fence_terminated", "truncated")
        )
        assert identity == 1, f"stop-reason identity broken at {i}: eos+fence+truncated={identity}"
    assert diag["eos_terminated"] == [False, True, False]
    assert diag["fence_terminated"] == [True, False, False]
    assert diag["truncated"] == [False, False, True]


def test_step_record_carries_fence_termination_rates() -> None:
    record = build_grpo_step_record(
        step=1,
        task_name="quantum_demo",
        domain="quantum",
        mean_reward=0.0,
        signal_stats={"signal_std": 0.0, "reward_std": 0.0},
        pass_rate=0.0,
        syntax_rate=0.0,
        interface_rate=0.0,
        verifier_rate=0.0,
        task_prob=1.0,
        task_state={"ema_reward": 0.0, "seen": 1},
        fence_termination_rate=0.5,
        cap_run_with_fence_opener_rate=0.25,
    )
    assert record["fence_termination_rate"] == 0.5
    assert record["cap_run_with_fence_opener_rate"] == 0.25


# ---------------------------------------------------------------------------
# (g) tail-only decode in the fence stopping criterion (O(N) per step)
# ---------------------------------------------------------------------------


def test_stop_criterion_tail_decode_stops_at_fence_after_long_prefix() -> None:
    # regression pin: a fence closing after a long non-fence prefix must
    # still stop generation at the closing fence
    model = make_model_without_eos()
    tokenizer = make_tokenizer()
    inputs = tokenizer("<s>", return_tensors="pt")
    forced = {i: 6 for i in range(1, 121)}  # 120 trailing tokens
    forced.update({121: 0, 122: 1, 123: 2, 124: 3, 125: 4, 126: 5, 127: 2, 128: 0, 129: 6})
    out = model.generate(
        **inputs,
        max_new_tokens=200,
        do_sample=False,
        logits_processor=LogitsProcessorList([_ForcedTokens(forced)]),
        stopping_criteria=StoppingCriteriaList(
            [StopAfterClosedCodeFence(tokenizer, prompt_length=1)]
        ),
        return_dict_in_generate=True,
    )
    gen = out.sequences[0, 1:]
    assert gen.numel() == 128, gen  # stops at the closing fence, not the cap
    decoded = tokenizer.decode(gen, skip_special_tokens=True)
    assert has_closed_code_fence(decoded)
    assert decoded.strip().endswith("```")


def test_same_line_fence_opener_does_not_stop_generation() -> None:
    # DOCUMENTED conservative behavior (debug-lane follow-up 4): the opener
    # requires a newline after the optional language tag, so "```python x=1"
    # never fires the stop and the candidate runs to the cap. The
    # cap_run_with_fence_opener diagnostic makes this class observable.
    model = make_model_without_eos()
    tokenizer = make_tokenizer()
    inputs = tokenizer("<s>", return_tensors="pt")
    # forced: ``` python x=1 \n ``` trailing  (same-line code)
    out = model.generate(
        **inputs,
        max_new_tokens=32,
        do_sample=False,
        logits_processor=LogitsProcessorList(
            [_ForcedTokens({1: 0, 2: 1, 3: 3, 4: 4, 5: 5, 6: 2, 7: 0, 8: 6})]
        ),
        stopping_criteria=StoppingCriteriaList(
            [StopAfterClosedCodeFence(tokenizer, prompt_length=1)]
        ),
        return_dict_in_generate=True,
    )
    gen = out.sequences[0, 1:]
    assert gen.numel() == 32, gen  # runs to the cap (no fence-stop)


# ---------------------------------------------------------------------------
# (h) synthetic stop marker: fence-closed completions learn to emit EOS
# ---------------------------------------------------------------------------


def test_append_fence_stop_markers_appends_preferred_eos() -> None:
    ids = [torch.tensor([0, 1, 2, 3, 4, 5, 2, 0])]  # ends at the closing "```"
    raw = ["```python\nx = 1\n```"]
    augmented, fence_stopped = append_fence_stop_markers(ids, raw, {EOS_ID})
    assert fence_stopped == [True]
    assert augmented[0].tolist() == [0, 1, 2, 3, 4, 5, 2, 0, EOS_ID]


def test_append_fence_stop_markers_prefers_tokenizer_eos_id() -> None:
    tokenizer = make_tokenizer()
    ids = [torch.tensor([0, 1, 2, 3, 4, 5, 2, 0])]
    raw = ["```python\nx = 1\n```"]
    augmented, _ = append_fence_stop_markers(ids, raw, {7, EOS_ID}, tokenizer=tokenizer)
    # tokenizer.eos_token_id (60) is in the stop set -> preferred over 7
    assert augmented[0].tolist()[-1] == EOS_ID


def test_append_fence_stop_markers_keeps_natural_eos_untouched() -> None:
    ids = [torch.tensor([3, 4, 5, EOS_ID])]
    raw = ["```python\nx = 1\n```"]
    augmented, fence_stopped = append_fence_stop_markers(ids, raw, {EOS_ID})
    assert fence_stopped == [False]
    assert augmented[0].tolist() == [3, 4, 5, EOS_ID]


def test_append_fence_stop_markers_keeps_unfenced_completions_untouched() -> None:
    ids = [torch.tensor([3, 4, 5, 6])]  # cap-run, no fence
    raw = ["x = 1 without any fence"]
    augmented, fence_stopped = append_fence_stop_markers(ids, raw, {EOS_ID})
    assert fence_stopped == [False]
    assert augmented[0].tolist() == [3, 4, 5, 6]


def test_append_fence_stop_markers_noop_without_stop_ids() -> None:
    ids = [torch.tensor([0, 1, 2, 3, 4, 5, 2, 0])]
    raw = ["```python\nx = 1\n```"]
    augmented, fence_stopped = append_fence_stop_markers(ids, raw, set())
    assert fence_stopped == [False]
    assert augmented[0].tolist() == [0, 1, 2, 3, 4, 5, 2, 0]


class _FakeRenderBackend:
    """Records the chat-template call (v8 prompt no-regression spy)."""

    def __init__(self) -> None:
        self.called_with = None

    def apply_chat_template(
        self, messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
    ):  # noqa: ARG002
        self.called_with = messages
        return "TASK: " + messages[-1]["content"]


def _fake_backend_and_args() -> (
    tuple[TextPreprocessorBackend, types.SimpleNamespace, _FakeRenderBackend]
):
    render = _FakeRenderBackend()
    backend = TextPreprocessorBackend(
        render_backend=render,
        text_backend=make_tokenizer(),
        save_backend=make_tokenizer(),
        backend_kind="test",
    )
    args = types.SimpleNamespace(
        temperature=1.0,
        top_p=1.0,
        group_size=1,
        max_new_tokens=64,
        device=torch.device("cpu"),
        fence_stop_marker=True,
    )
    return backend, args, render


def test_generate_group_end_to_end_appends_fence_stop_marker() -> None:
    # v8-manifest-style task record -> build_prompt -> generate_group on the
    # tiny model with a forced fence -> the completion ids end in the EOS
    # marker while the raw text (harness view) stays fence-stopped
    model = make_model_without_eos()
    real_generate = model.generate
    forced = LogitsProcessorList(
        [_ForcedTokens({1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 2, 8: 0, 9: 6})]
    )

    def forced_generate(*args, **kwargs):
        kwargs["logits_processor"] = forced
        kwargs["do_sample"] = False
        return real_generate(*args, **kwargs)

    model.generate = forced_generate  # type: ignore[method-assign]
    backend, args, render = _fake_backend_and_args()
    task = {
        "task_id": "quantum_v8_demo",
        "task_dir": types.SimpleNamespace(name="quantum_v8_demo"),
        "behavior_hints": ["Implement solve() returning a float."],
        "meta": {
            "id": "quantum_v8_demo",
            "name": "quantum_v8_demo",
            "domain": "quantum",
            "category": "circuit",
            "task_prompt": "Implement solve() for the v8 manifest.",
            "single_file_expected": True,
        },
    }
    prompt = build_prompt(task)
    raw, rendered_text, prompt_ids, prompt_mask, completion_ids = generate_group(
        model,
        backend,
        prompt,
        args,
        count=1,
        max_new_tokens=64,
        return_token_ids=True,
    )
    assert len(raw) == 1
    assert has_closed_code_fence(raw[0])
    assert "trailing" not in raw[0]
    # the v8 prompt handling: rendered text is the chat-template output and
    # the system message is the exact rollout system prompt
    assert rendered_text == "TASK: " + prompt
    assert render.called_with[0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert "v8 manifest" in render.called_with[1]["content"]
    assert prompt_ids.shape[0] == 1
    assert prompt_mask.shape[0] == 1
    # the synthetic stop marker: ids end with the resolved EOS id
    assert int(completion_ids[0][-1]) == EOS_ID
    assert int(completion_ids[0][-2]) == 0  # closing fence is the 2nd-to-last


def test_generate_group_disabled_marker_leaves_ids_untouched() -> None:
    model = make_model_without_eos()
    real_generate = model.generate
    forced = LogitsProcessorList(
        [_ForcedTokens({1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 2, 8: 0, 9: 6})]
    )

    def forced_generate(*args, **kwargs):
        kwargs["logits_processor"] = forced
        kwargs["do_sample"] = False
        return real_generate(*args, **kwargs)

    model.generate = forced_generate  # type: ignore[method-assign]
    backend, args, _ = _fake_backend_and_args()
    args.fence_stop_marker = False
    raw, _, _, _, completion_ids = generate_group(
        model,
        backend,
        "Implement solve().",
        args,
        count=1,
        max_new_tokens=64,
        return_token_ids=True,
    )
    assert has_closed_code_fence(raw[0])
    assert int(completion_ids[0][-1]) != EOS_ID  # no marker when disabled


def test_train_pass_cap_interplay_with_fence_marker() -> None:
    # the marker lives in the SAME ids both log-prob passes consume; the
    # train-pass cap drops the tail (marker included) without breaking the
    # exact-id path (debug-lane consistency requirement)
    from training import grpo_trainer

    class _FakeLogitModel(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.emb = torch.nn.Embedding(64, 16)
            self.head = torch.nn.Linear(16, 64)

        def forward(self, input_ids, attention_mask=None, **kwargs):
            return types.SimpleNamespace(logits=self.head(self.emb(input_ids)))

    model = _FakeLogitModel()
    prompt_ids = torch.tensor([[62, 63, 63]])
    marker_ids = torch.tensor([3, 4, 5, EOS_ID]).reshape(1, -1)
    # no cap: the marker position participates in the log-prob computation
    log_prob, token_count, _ = grpo_trainer.compute_completion_log_prob(
        model,
        None,
        "",
        "",
        torch.device("cpu"),
        max_seq_length=0,
        logit_clip=50.0,
        return_entropy=True,
        prompt_token_ids=prompt_ids,
        prompt_attention_mask=torch.ones_like(prompt_ids),
        completion_token_ids=marker_ids,
    )
    assert int(token_count) == 4  # x = 1 + the marker
    assert torch.isfinite(log_prob)
    # cap cuts the tail: marker dropped, only the first 2 completion tokens
    _, capped_count, _ = grpo_trainer.compute_completion_log_prob(
        model,
        None,
        "",
        "",
        torch.device("cpu"),
        max_seq_length=0,
        logit_clip=50.0,
        return_entropy=True,
        train_seq_cap=5,
        prompt_token_ids=prompt_ids,
        prompt_attention_mask=torch.ones_like(prompt_ids),
        completion_token_ids=marker_ids,
    )
    assert int(capped_count) == 2


def test_render_generation_prompt_requires_no_thinking_but_falls_back() -> None:
    # the v8 rollout prompt path: apply_chat_template is called with
    # enable_thinking=False; a template without that kwarg falls back cleanly
    class _NoThinking:
        def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=True):  # noqa: ARG002
            return "R[" + messages[-1]["content"] + "]"

    assert render_generation_prompt(_NoThinking(), "impl") == "R[impl]"
    rendered = render_generation_prompt(_FakeRenderBackend(), "impl")
    assert rendered == "TASK: impl"

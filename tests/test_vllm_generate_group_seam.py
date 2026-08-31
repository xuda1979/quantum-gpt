"""TDD (2026-09-01, Lane A closure): the vLLM rollout seam in generate_group.

STANDUP #236b claimed "TDD 2/2" for the SAPO_VLLM_URL seam but no test file
covered it — the seam branch (env set -> vLLM texts -> re-tokenized ids ->
model.generate SKIPPED; VllmUnavailable -> loud stage line -> transformers
fallback) was untested launch-path code. This file is that missing coverage:
RED first (seam behavior must actually hold), then the smallest fix, GREEN.

Contract under test:
1. SAPO_VLLM_URL set + server up -> generate_group returns the client's
   completions WITHOUT calling model.generate (decoded ids == re-tokenized
   client texts; prompt ids returned for logprob path).
2. SAPO_VLLM_URL set + server unreachable -> "vllm_rollout_unavailable"
   stage line printed and the transformers path runs (model.generate called).
3. SAPO_VLLM_URL unset -> byte-identical cold path (no client import).
"""

from __future__ import annotations

import io
import sys
import types
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import torch
from tokenizers import Tokenizer, models
from transformers import (
    GPT2Config,
    GPT2LMHeadModel,
    LogitsProcessor,
    LogitsProcessorList,
    PreTrainedTokenizerFast,
)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.compat import strict_zip  # noqa: E402
from training.generation import has_closed_code_fence  # noqa: E402
from training.grpo_trainer import generate_group  # noqa: E402
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
# Seam is enabled by SAPO_VLLM_URL; the same env dict sets it in every test.
VLLM_ENV = {"SAPO_VLLM_URL": "http://127.0.0.1:8355"}


def make_tokenizer() -> PreTrainedTokenizerFast:
    t = Tokenizer(models.WordLevel(VOCAB, unk_token="<unk>"))
    return PreTrainedTokenizerFast(
        tokenizer_object=t,
        eos_token="<|endoftext|>",
        pad_token="<pad>",
        bos_token="<s>",
        unk_token="<unk>",
    )


class _Render:
    def apply_chat_template(
        self, messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
    ):  # noqa: ARG002
        return "TASK: " + messages[-1]["content"]


def _backend() -> TextPreprocessorBackend:
    return TextPreprocessorBackend(
        render_backend=_Render(),
        text_backend=make_tokenizer(),
        save_backend=make_tokenizer(),
        backend_kind="test",
    )


def _args(**overrides) -> types.SimpleNamespace:
    base = dict(
        temperature=1.0,
        top_p=1.0,
        group_size=3,
        max_new_tokens=64,
        device=torch.device("cpu"),
        fence_stop_marker=True,
        greedy_rollout_fraction=0.0,
    )
    base.update(overrides)
    return types.SimpleNamespace(**base)


def _make_model() -> GPT2LMHeadModel:
    cfg = GPT2Config(n_layer=1, n_head=1, n_embd=16, vocab_size=64)
    cfg.eos_token_id = None
    cfg.bos_token_id = None
    cfg.pad_token_id = None
    model = GPT2LMHeadModel(cfg)
    model.eval()
    return model


class _FakeVllmClient:
    """Stand-in for VllmRolloutClient with controllable availability."""

    def __init__(self, up: bool, completions: list[str] | None = None):
        self.up = up
        self.completions = completions or ["```python\nx = 1\n```", "x = 1", "x"]

    def is_up(self, *, force: bool = False) -> bool:
        return self.up

    def generate_batch(self, prompt, n, max_tokens, temperature, seed=None, stop=None):
        return self.completions[:n]


class _ForcedTokens(LogitsProcessor):
    """Deterministic token forcing so the tiny GPT2 emits a fenced answer."""

    def __init__(self, forced: dict[int, int]) -> None:
        self.forced = dict(forced)

    def __call__(self, input_ids: torch.Tensor, scores: torch.Tensor) -> torch.Tensor:
        pos = int(input_ids.shape[1])
        if pos in self.forced:
            scores = scores.clone()
            scores.fill_(-1000.0)
            scores[:, self.forced[pos]] = 1000.0
        return scores


def test_vllm_seam_returns_client_texts_without_model_generate() -> None:
    """SAPO_VLLM_URL set + server up: client texts are used, model.generate
    is NEVER called, and completion ids re-tokenize the client texts."""
    model = _make_model()
    generate_calls: list = []

    def spy(*a, **k):
        generate_calls.append(k)
        raise AssertionError("model.generate must not run on the vLLM path")

    model.generate = spy  # type: ignore[method-assign]

    fake = _FakeVllmClient(up=True, completions=["```python\nx = 1\n```", "x = 1", "x"])
    with (
        mock.patch.dict("os.environ", VLLM_ENV, clear=False),
        mock.patch("training.vllm_rollout_client.VllmRolloutClient", return_value=fake),
    ):
        raw, text, prompt_ids, _, completion_ids = generate_group(
            model,
            _backend(),
            "Implement solve().",
            _args(group_size=3),
            count=3,
            max_new_tokens=64,
            return_token_ids=True,
        )
    assert generate_calls == []
    assert len(raw) == 3
    assert len(completion_ids) == 3
    # decoded completion ids equal the re-tokenized client texts; fence-closed
    # completions additionally carry the EOS marker (r10 fence contract —
    # the fence-close position trains the real end token), exactly like the
    # transformers path. The fixture's first completion is fence-closed, the
    # other two are plain text (no marker).
    tok = make_tokenizer()
    for text_i, ids in strict_zip(raw, completion_ids):
        expected = tok(text_i, return_tensors="pt")["input_ids"][0].detach().cpu()
        if has_closed_code_fence(text_i):
            assert torch.equal(ids[:-1], expected)  # marker appended
            assert int(ids.reshape(-1)[-1].item()) == EOS_ID
        else:
            assert torch.equal(ids, expected)
    # the prompt ids are the rendered prompt's token ids (logprob path intact)
    assert prompt_ids.numel() >= 1


def test_vllm_seam_falls_back_to_transformers_when_unavailable() -> None:
    """SAPO_VLLM_URL set but server unreachable: loud unavailable stage line,
    then the transformers decode path runs (model.generate called)."""
    model = _make_model()
    forced = LogitsProcessorList(
        [_ForcedTokens({1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 2, 8: 0, 9: 6})]
    )
    generate_calls: list = []
    real_generate = model.generate

    def spy(*a, **k):
        generate_calls.append(k)
        k["logits_processor"] = forced
        k["do_sample"] = False
        return real_generate(*a, **k)

    model.generate = spy  # type: ignore[method-assign]

    from training.vllm_rollout_client import VllmUnavailable

    fake = _FakeVllmClient(up=True)
    fake.generate_batch = lambda *a, **k: (_ for _ in ()).throw(VllmUnavailable("down"))
    buf = io.StringIO()
    with (
        mock.patch.dict("os.environ", VLLM_ENV, clear=False),
        mock.patch("training.vllm_rollout_client.VllmRolloutClient", return_value=fake),
        redirect_stdout(buf),
    ):
        raw, text = generate_group(
            model,
            _backend(),
            "Implement solve().",
            _args(group_size=3),
            count=3,
            max_new_tokens=64,
        )
    assert "vllm_rollout_unavailable" in buf.getvalue()
    assert len(generate_calls) == 1  # one batched sampled call on fallback
    assert len(raw) == 3


def test_vllm_seam_truncates_at_closing_fence_and_appends_eos_marker() -> None:
    """Distribution parity with the transformers path (r10 fence contract):

    a vLLM completion that closes a code fence then keeps generating must be
    cut at the closing fence (the transformers StoppingCriteria stops there),
    and the EOS marker must be appended to the truncated ids so the
    fence-close position trains the real end token. Without this, enabling
    SAPO_VLLM_URL silently changes the rollout distribution (trailing prose
    past the fence + no termination target) — the exact bug class §5.9 names.
    """
    model = _make_model()
    generate_calls: list = []

    def spy(*a, **k):
        generate_calls.append(k)
        raise AssertionError("model.generate must not run on the vLLM path")

    model.generate = spy  # type: ignore[method-assign]

    # The vLLM server returns a completion that runs PAST the closing fence
    # (it stops only on EOS/cap, not on the fence) — like a model that never
    # samples EOS (run-6 S1-S5 eos_termination_rate 0.0).
    trailing_text = "```python\nx = 1\n```\n\n# trailing prose the fence stopper would cut"
    fake = _FakeVllmClient(up=True, completions=[trailing_text, trailing_text, trailing_text])
    with (
        mock.patch.dict("os.environ", VLLM_ENV, clear=False),
        mock.patch("training.vllm_rollout_client.VllmRolloutClient", return_value=fake),
    ):
        raw, _, _, _, completion_ids = generate_group(
            model,
            _backend(),
            "Implement solve().",
            _args(group_size=3),
            count=3,
            max_new_tokens=64,
            return_token_ids=True,
        )
    assert generate_calls == []
    tok = make_tokenizer()
    for text_i, ids in strict_zip(raw, completion_ids):
        # 1) raw text must be cut at the closing fence (no trailing prose)
        assert text_i.rstrip().endswith("```"), f"trailing prose not cut: {text_i!r}"
        assert "# trailing prose" not in text_i
        # 2) the completion ids must end with the EOS marker (fence-close
        #    position trains the real end token)
        assert int(ids.reshape(-1)[-1].item()) == EOS_ID
        # 3) ids minus the marker re-tokenize the truncated text exactly
        assert torch.equal(ids[:-1], tok(text_i, return_tensors="pt")["input_ids"][0])


def test_vllm_seam_greedy_sampled_mix_batch_splits() -> None:
    """greedy_rollout_fraction through vLLM: greedy subset requested at temp 0,
    sampled subset at the effective temp (matches the transformers path's
    two-call split — same group composition contract)."""
    model = _make_model()
    model.generate = lambda *a, **k: (_ for _ in ()).throw(  # type: ignore[method-assign]
        AssertionError("model.generate must not run on the vLLM path")
    )

    class _RecordingFake(_FakeVllmClient):
        def __init__(self) -> None:
            super().__init__(up=True)
            self.calls: list[tuple[int, float]] = []

        def generate_batch(self, prompt, n, max_tokens, temperature, seed=None, stop=None):
            self.calls.append((n, temperature))
            return ["```python\nx = 1\n```"] * n

    fake = _RecordingFake()
    with (
        mock.patch.dict("os.environ", VLLM_ENV, clear=False),
        mock.patch("training.vllm_rollout_client.VllmRolloutClient", return_value=fake),
    ):
        raw, _ = generate_group(
            model,
            _backend(),
            "Implement solve().",
            _args(group_size=5, greedy_rollout_fraction=0.4),
            count=5,
            max_new_tokens=64,
        )
    assert fake.calls == [(2, 0.0), (3, 1.0)], fake.calls
    assert len(raw) == 5


def test_vllm_seam_missing_client_module_falls_back() -> None:
    """SAPO_VLLM_URL set but training.vllm_rollout_client is MISSING (e.g.
    the deployed bundle predates the client module): the seam must degrade
    exactly like any other vLLM failure — loud unavailable stage line, then
    the transformers path runs — NOT crash the trainer with an uncaught
    ImportError. Fail-closed means the rollout never dies because the
    accelerator is absent."""
    model = _make_model()
    forced = LogitsProcessorList(
        [_ForcedTokens({1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 2, 8: 0, 9: 6})]
    )
    generate_calls: list = []
    real_generate = model.generate

    def spy(*a, **k):
        generate_calls.append(k)
        k["logits_processor"] = forced
        k["do_sample"] = False
        return real_generate(*a, **k)

    model.generate = spy  # type: ignore[method-assign]
    buf = io.StringIO()
    # None in sys.modules makes the `from training.vllm_rollout_client import`
    # in the seam raise ImportError (exactly what a bundle without the file
    # produces).
    with (
        mock.patch.dict("os.environ", VLLM_ENV, clear=False),
        mock.patch.dict(sys.modules, {"training.vllm_rollout_client": None}),
        redirect_stdout(buf),
    ):
        raw, _ = generate_group(
            model,
            _backend(),
            "Implement solve().",
            _args(group_size=3),
            count=3,
            max_new_tokens=64,
        )
    assert "vllm_rollout_unavailable" in buf.getvalue()
    assert len(generate_calls) == 1  # transformers fallback ran (batched)
    assert len(raw) == 3


def test_vllm_seam_unset_env_is_cold_path() -> None:
    """SAPO_VLLM_URL unset: the client module is never imported; the
    transformers path runs exactly once (batched)."""
    model = _make_model()
    generate_calls: list = []
    real_generate = model.generate

    def spy(*a, **k):
        generate_calls.append(k)
        k["do_sample"] = False
        return real_generate(*a, **k)

    model.generate = spy  # type: ignore[method-assign]

    with mock.patch.dict("os.environ", {}, clear=False):
        raw, text = generate_group(
            model,
            _backend(),
            "Implement solve().",
            _args(group_size=3),
            count=3,
            max_new_tokens=64,
        )
    assert len(generate_calls) == 1
    assert len(raw) == 3

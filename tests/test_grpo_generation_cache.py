from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

import torch

from training.grpo_trainer import compute_completion_log_prob, extract_code, generate_group


class _Tokenizer:
    def __call__(self, _text: str, *, return_tensors: str) -> dict[str, torch.Tensor]:
        assert return_tensors == "pt"
        return {"input_ids": torch.tensor([[10, 11]])}

    def decode(self, _tokens: torch.Tensor, *, skip_special_tokens: bool) -> str:
        assert skip_special_tokens
        return "```python\ndef answer():\n    return 42\n```"


class _RenderBackend:
    def apply_chat_template(self, _messages, **_kwargs) -> str:
        return "prompt"


class _Model:
    def __init__(self) -> None:
        self.config = SimpleNamespace(use_cache=False)
        self.calls = 0
        self.max_new_tokens = []

    def generate(self, **kwargs):
        assert self.config.use_cache is True
        assert kwargs["use_cache"] is True
        assert kwargs["output_scores"] is False
        self.max_new_tokens.append(kwargs["max_new_tokens"])
        self.calls += 1
        # 2026-08-28 (architect, batched-rollout speedup): the batched path
        # issues ONE generate call per (greedy/sampled) subset returning all
        # rows; the mock returns 2 candidate rows (one padded EOS each).
        kwargs.get("num_return_sequences", 1)
        return SimpleNamespace(sequences=torch.tensor([[10, 11, 12, 13, 2], [10, 11, 12, 13, 2]]))


def test_rollout_temporarily_enables_kv_cache_without_retaining_scores() -> None:
    model = _Model()
    backend = SimpleNamespace(text_backend=_Tokenizer(), render_backend=_RenderBackend())
    args = Namespace(
        device=torch.device("cpu"),
        temperature=1.0,
        group_size=2,
        max_new_tokens=64,
        top_p=1.0,
    )

    (
        raw_responses,
        _prompt,
        prompt_ids,
        prompt_attention_mask,
        completion_ids,
    ) = generate_group(model, backend, "task", args, return_token_ids=True)

    assert raw_responses == ["```python\ndef answer():\n    return 42\n```"] * 2
    assert [extract_code(response) for response in raw_responses] == [
        "def answer():\n    return 42"
    ] * 2
    assert torch.equal(prompt_ids, torch.tensor([10, 11]))
    assert torch.equal(prompt_attention_mask, torch.tensor([1, 1]))
    assert all(torch.equal(ids, torch.tensor([12, 13, 2])) for ids in completion_ids)
    # 2026-08-28 (batched speedup): ONE generate call returns both candidates
    # (parallel across devices), not 2 serial calls.
    assert model.calls == 1
    assert model.max_new_tokens == [64]
    assert model.config.use_cache is False


def test_rollout_can_override_base_generation_budget_per_task() -> None:
    model = _Model()
    backend = SimpleNamespace(text_backend=_Tokenizer(), render_backend=_RenderBackend())
    args = Namespace(
        device=torch.device("cpu"),
        temperature=1.0,
        group_size=1,
        max_new_tokens=512,
        top_p=1.0,
    )

    generate_group(model, backend, "task", args, max_new_tokens=896)

    assert model.max_new_tokens == [896]


class _RoundTripAdversarialTokenizer:
    def __call__(self, *_args, **_kwargs):
        raise AssertionError("exact-ID policy path must not re-tokenize decoded text")


class _ForwardCaptureModel:
    def __init__(self) -> None:
        self.input_ids = None

    def __call__(self, **kwargs):
        self.input_ids = kwargs["input_ids"].detach().cpu().clone()
        batch, seq = kwargs["input_ids"].shape
        return SimpleNamespace(logits=torch.zeros(batch, seq, 128))


def test_exact_rollout_ids_bypass_decode_retokenize_and_preserve_eos() -> None:
    model = _ForwardCaptureModel()
    prompt_ids = torch.tensor([10, 11])
    generated_ids = torch.tensor([12, 13, 2])

    seq_log_prob, token_count, token_log_probs = compute_completion_log_prob(
        model,
        _RoundTripAdversarialTokenizer(),
        "decoded prompt would tokenize differently",
        "decoded response omits EOS and would tokenize differently",
        torch.device("cpu"),
        max_seq_length=32,
        logit_clip=50.0,
        return_token_log_probs=True,
        prompt_token_ids=prompt_ids,
        prompt_attention_mask=torch.tensor([1, 1]),
        completion_token_ids=generated_ids,
    )

    assert torch.equal(model.input_ids, torch.tensor([[10, 11, 12, 13, 2]]))
    assert token_count.item() == 3
    assert token_log_probs.numel() == 3
    assert torch.isfinite(seq_log_prob)


def test_trainer_scores_extracted_code_but_uses_raw_response_for_policy_math() -> None:
    trainer = (Path(__file__).resolve().parents[1] / "training/grpo_trainer.py").read_text(
        encoding="utf-8"
    )

    assert "codes = [extract_code(response) for response in raw_responses]" in trainer
    assert "return_token_ids=True" in trainer
    assert "for idx, raw_response in enumerate(raw_responses):" in trainer
    assert "prompt_token_ids=rollout_prompt_token_ids" in trainer
    assert "completion_token_ids=rollout_completion_token_ids[idx]" in trainer

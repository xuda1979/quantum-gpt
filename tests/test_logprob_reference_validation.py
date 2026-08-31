"""Rollout logprob reference validation (2026-08-29, CEO directive):
computed policy logprobs must match an INDEPENDENT reference recompute
(autograd-free, per-token sum) within 1e-4 before any training step consumes them.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.grpo_trainer import compute_completion_log_prob  # noqa: E402


class _Tok:
    def __call__(self, _t, *, return_tensors):
        assert return_tensors == "pt"
        return {"input_ids": torch.tensor([[7, 8, 9]])}

    def decode(self, _x, *, skip_special_tokens):
        return "irrelevant"


def _reference_logprob(model, ids: torch.Tensor) -> torch.Tensor:
    """Independent recompute: full-sequence forward, manual shift + gather,
    log_softmax summed over completion positions. No shared code with the
    producer beyond the model itself."""
    with torch.no_grad():
        logits = model(input_ids=ids.unsqueeze(0)).logits[0]
        logp = torch.log_softmax(logits.float(), dim=-1)
        # completion tokens are positions 2..end; their probs come from logits at 1..end-1
        total = torch.zeros(())
        for t in range(1, ids.numel()):
            total = total + logp[t - 1, ids[t]]
        return total


def test_completion_logprob_matches_reference_within_tolerance() -> None:
    torch.manual_seed(11)
    cfg = __import__("transformers").GPT2Config(n_layer=1, n_head=1, n_embd=16, vocab_size=32)
    model = __import__("transformers").GPT2LMHeadModel(cfg).eval()
    prompt_ids = torch.tensor([5, 6])
    completion_ids = torch.tensor([7, 9, 11, 3])
    prompt_attn = torch.tensor([1, 1])

    computed, _, _ = compute_completion_log_prob(
        model,
        _Tok(),
        "unused prompt text",
        "unused completion text",
        torch.device("cpu"),
        max_seq_length=64,
        logit_clip=50.0,
        return_token_log_probs=True,
        prompt_token_ids=prompt_ids,
        prompt_attention_mask=prompt_attn,
        completion_token_ids=completion_ids,
    )
    full = torch.cat([prompt_ids, completion_ids])
    reference = _reference_logprob(model, full)
    # completion positions only (prompt positions excluded): reference sums
    # t in [1..end]; subtract the last prompt-position term (t=1)
    with torch.no_grad():
        logits = model(input_ids=full.unsqueeze(0)).logits[0]
        lp = torch.log_softmax(logits.float(), dim=-1)
        prompt_term = lp[0, full[1]]
    reference_completion = reference - prompt_term
    assert torch.isfinite(computed)
    assert float(computed) == pytest.approx(float(reference_completion), abs=1e-4)

"""2026-08-25 run-4 OOM fix: train-pass sequence truncation (option a).

Run-4 (sapo-27b-ai-20260825T052636) OOM'd in the TRAIN logprob pass
(grpo_utils.py:1542, grad-enabled) when every candidate hit the 2048-token
completion cap (truncation_rate 1.0): the grad-enabled train forward's
activation peak on the lm_head card exceeded 60.96 GiB (59.90 GiB already
live, 38 MiB attempted). Run-3 survived 41 steps on the same stack because
its completions were ~100-1300 tokens.

Fix: the SAPO loss/logprobs are computed on at most the first
``train_pass_max_seq_length`` tokens of each candidate FOR THE TRAIN PASS
ONLY. Rollout log-prob stats (old policy), eval and rewards stay on the full
sequence. The truncation never cuts the prompt; it only drops completion-tail
tokens from the current-policy token loss. Per-token identity on the kept
region is preserved exactly (the capped pass returns the same token
log-probs as the full pass on the shared prefix), so a masked/padding tail in
the full pass yields the SAME loss as the truncated pass.
"""

from __future__ import annotations

import types

import pytest
import torch

from training import grpo_trainer
from training.grpo_utils import sapo_loss_metrics

VOCAB = 64
HIDDEN = 16


class _FakeLogitModel(torch.nn.Module):
    """Deterministic CPU model exposing outputs.logits for the exact-id path."""

    def __init__(self, vocab: int = VOCAB, hidden: int = HIDDEN) -> None:
        super().__init__()
        self.emb = torch.nn.Embedding(vocab, hidden)
        self.head = torch.nn.Linear(hidden, vocab)

    def forward(self, input_ids, attention_mask=None, **kwargs):
        hidden = self.emb(input_ids)
        return types.SimpleNamespace(logits=self.head(hidden))


def _call(
    model,
    prompt_ids: torch.Tensor,
    completion_ids: torch.Tensor,
    *,
    prompt_mask: torch.Tensor | None = None,
    train_seq_cap: int | None = None,
    return_entropy: bool = False,
    return_token_log_probs: bool = True,
):
    return grpo_trainer.compute_completion_log_prob(
        model,
        None,  # tokenizer unused in exact-id mode
        "",  # prompt_text unused
        "",  # completion_text unused
        torch.device("cpu"),
        max_seq_length=0,  # no max-seq-length truncation in these tests
        logit_clip=50.0,
        return_entropy=return_entropy,
        return_token_log_probs=return_token_log_probs,
        train_seq_cap=train_seq_cap,
        prompt_token_ids=prompt_ids,
        prompt_attention_mask=prompt_mask,
        completion_token_ids=completion_ids,
    )


def test_train_pass_cap_returns_exact_prefix_of_full_pass() -> None:
    """The capped train pass returns EXACTLY the first K completion-token
    log-probs of the uncapped pass — truncation only drops tail tokens, it
    never changes the math on the kept region (token count, prefix sum, and
    every per-token value agree)."""
    torch.manual_seed(3)
    model = _FakeLogitModel().train()
    prompt_ids = torch.randint(0, VOCAB, (1, 8))
    completion_ids = torch.randint(0, VOCAB, (1, 48))
    cap = 8 + 24  # prompt + first 24 completion tokens

    with torch.enable_grad():
        full_lp, full_count, full_tokens = _call(
            model, prompt_ids, completion_ids, train_seq_cap=None
        )
        capped_lp, capped_count, capped_tokens = _call(
            model, prompt_ids, completion_ids, train_seq_cap=cap
        )

    assert int(full_count.item()) == 48
    assert int(capped_count.item()) == 24
    # Kept-region identity: capped token lps == first 24 of the full pass.
    assert capped_tokens.shape == (24,)
    assert torch.allclose(capped_tokens, full_tokens[:24])
    # Prefix-sum identity: the capped sequence log-prob == sum of the kept
    # prefix from the full pass.
    assert torch.allclose(capped_lp, full_tokens[:24].sum())


def test_train_pass_capped_loss_equals_full_loss_with_masked_tail() -> None:
    """A completion whose tail beyond the cap is padding (attention-masked
    out of the full pass's loss) yields the SAME SAPO loss as the truncated
    train pass: the kept token sets are identical and the per-token loss
    terms match, so the full-sequence loss == train-pass loss.

    The completion attention mask is generated inside the exact-id path as
    all-ones (the rollout completion is never padded), so this test applies
    the padding-mask semantics the way the trainer's loss path does —
    ``completion_mask &= attention_mask[:, 1:]`` (grpo_trainer.py) — over the
    token log-probs: a right-masked tail drops the last ``tail_len`` tokens
    from the masked select, leaving exactly the first ``kept_len``."""
    torch.manual_seed(7)
    model = _FakeLogitModel().train()
    prompt_len, kept_len, tail_len = 6, 24, 24
    prompt_ids = torch.randint(0, VOCAB, (1, prompt_len))
    completion_ids = torch.randint(0, VOCAB, (1, kept_len + tail_len))
    prompt_mask = torch.ones(1, prompt_len, dtype=torch.long)
    cap = prompt_len + kept_len

    with torch.enable_grad():
        # Full pass: computes all 48 completion positions, keeps 24 (masked tail).
        _full_lp, _full_count, full_tokens = _call(
            model,
            prompt_ids,
            completion_ids,
            prompt_mask=prompt_mask,
            train_seq_cap=None,
        )
        # Capped train pass: keeps the same 24 tokens by construction.
        capped_lp, capped_count, capped_tokens = _call(
            model,
            prompt_ids,
            completion_ids,
            prompt_mask=prompt_mask,
            train_seq_cap=cap,
        )

    assert int(_full_count.item()) == kept_len + tail_len
    assert int(capped_count.item()) == kept_len
    # Padding tail semantics: the full pass's masked select keeps only the
    # first kept_len tokens (the attention-masked tail contributes nothing).
    full_kept = full_tokens[:kept_len]
    assert torch.allclose(capped_tokens, full_kept)

    advantage = torch.tensor([0.7])
    kwargs = dict(tau_pos=1.0, tau_neg=1.05, kl_coeff=0.01, numerical_log_ratio_clip=8.0)
    loss_full, stats_full = sapo_loss_metrics(
        [full_kept], [(full_kept.detach() + 0.01)], advantage, **kwargs
    )
    loss_capped, stats_capped = sapo_loss_metrics(
        [capped_tokens], [(capped_tokens.detach() + 0.01)], advantage, **kwargs
    )
    assert float(loss_full.item()) == float(loss_capped.item())
    assert stats_full["n_tokens"] == stats_capped["n_tokens"] == float(kept_len)
    assert torch.allclose(
        torch.as_tensor(loss_full.detach().clone()), torch.as_tensor(loss_capped.detach().clone())
    )


def test_rollout_logprob_stats_unaffected_without_cap() -> None:
    """Rollout (old-policy) log-prob stats keep the FULL sequence: with the
    cap disabled (None or 0) the function behaves exactly as before — full
    token count, full token lps, and the entropy variant still works."""
    torch.manual_seed(11)
    model = _FakeLogitModel().train()
    prompt_ids = torch.randint(0, VOCAB, (1, 8))
    completion_ids = torch.randint(0, VOCAB, (1, 48))

    with torch.enable_grad():
        base_lp, base_count, base_tokens = _call(
            model, prompt_ids, completion_ids, train_seq_cap=None
        )
        zero_lp, zero_count, zero_tokens = _call(model, prompt_ids, completion_ids, train_seq_cap=0)
        ent_lp, ent_count, entropy, ent_tokens = _call(
            model,
            prompt_ids,
            completion_ids,
            train_seq_cap=None,
            return_entropy=True,
        )

    assert int(base_count.item()) == 48
    assert int(zero_count.item()) == 48
    assert torch.allclose(base_tokens, zero_tokens)
    assert torch.allclose(base_lp, zero_lp)
    # Entropy variant unaffected: same count, finite entropy in [0, log V].
    assert int(ent_count.item()) == 48
    assert torch.isfinite(entropy).item()
    assert 0.0 <= float(entropy.item()) <= float(torch.log(torch.tensor(VOCAB)))


def test_train_pass_truncation_breakdown_documented() -> None:
    """The loss-reduction documentation reports the truncation honestly: the
    breakdown carries the cap and the fraction of candidates whose train pass
    was truncated (0 when disabled), so the auditor can see the update used a
    prefix of each completion."""
    full = grpo_trainer.train_pass_truncation_breakdown(seq_cap=2048, n_truncated=3, n_total=4)
    assert full["train_pass_seq_cap"] == 2048
    assert full["train_pass_truncation_rate"] == pytest.approx(0.75)
    disabled = grpo_trainer.train_pass_truncation_breakdown(seq_cap=0, n_truncated=0, n_total=4)
    assert disabled["train_pass_seq_cap"] == 0
    assert disabled["train_pass_truncation_rate"] == 0.0

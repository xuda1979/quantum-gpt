"""TDD: run-8 OOM root cause — the differentiable entropy-floor branch of
chunked_log_probs_and_entropy retains per-chunk fp32 tensors ([1,S,8192]:
clamp/exp/p/log_p) in the autograd graph over the FULL ~1700-token sequence.
Measured on the 27B contract: ~37 GiB of retained bytes for a 4-candidate
train pass (80.94 GiB with the branch vs 43.58 GiB without) — the run-8
59.8 GiB NPU-0 peak (run-4 mechanism, no cap engagement: completions were
below the train-pass cap).

FIX (smallest correct): the entropy branch computes only the first
``entropy_pos_cap`` positions (a floor needs a rough mean, not the full
sequence). The log_z / token-log-prob path is untouched — lps are
bit-identical; the weight-0 path (return_entropy off) is byte-identical.
The trainer threads ``--entropy-token-cap`` (completion tokens after the
prompt) into the train pass only; rollout entropy (degenerate alarm) stays
full-sequence.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.grpo_utils import (  # noqa: E402
    chunked_log_probs_and_entropy,
    resolve_entropy_pos_cap,
)


def _saved_bytes(fn) -> int:
    """Bytes the autograd graph retains between forward and backward
    (saved_tensors_hooks fires on every save during forward)."""
    total = 0

    def pack(t):
        nonlocal total
        total += t.numel() * t.element_size()
        return t

    with torch.autograd.graph.saved_tensors_hooks(pack, lambda t: t):
        fn()
    return total


@pytest.fixture()
def fixture():
    torch.manual_seed(3)
    S, V, CS = 40, 2048, 512
    logits = torch.randn(1, S, V, requires_grad=True) * 0.5
    target_ids = torch.randint(0, V, (1, S))
    return logits, target_ids, CS


# ---------------------------------------------------------------------------
# 1. Semantics: the capped branch equals the full branch's prefix
# ---------------------------------------------------------------------------


def test_entropy_pos_cap_matches_full_prefix(fixture) -> None:
    logits, target_ids, CS = fixture
    _, full_ent = chunked_log_probs_and_entropy(
        logits, target_ids, 5.0, chunk_size=CS, return_entropy=True
    )
    _, capped_ent = chunked_log_probs_and_entropy(
        logits,
        target_ids,
        5.0,
        chunk_size=CS,
        return_entropy=True,
        entropy_pos_cap=10,
    )
    # prefix is exact; beyond the cap is zero
    assert torch.allclose(capped_ent[:, :10], full_ent[:, :10])
    assert bool((capped_ent[:, 10:] == 0).all())


def test_token_log_probs_unchanged_by_entropy_cap(fixture) -> None:
    """The fix must not touch the SAPO loss path: lps are bit-identical."""
    logits, target_ids, CS = fixture
    full_lps, _ = chunked_log_probs_and_entropy(
        logits, target_ids, 5.0, chunk_size=CS, return_entropy=True
    )
    capped_lps, _ = chunked_log_probs_and_entropy(
        logits,
        target_ids,
        5.0,
        chunk_size=CS,
        return_entropy=True,
        entropy_pos_cap=10,
    )
    assert torch.equal(full_lps, capped_lps)


# ---------------------------------------------------------------------------
# 2. Memory: the cap shrinks the retained graph (the run-8 mechanism)
# ---------------------------------------------------------------------------


def test_entropy_cap_reduces_saved_graph_bytes() -> None:
    S, V, CS = 1700, 24576, 8192  # run-8-like: ~1700 tokens, 3 chunks

    def make_fwd(cap, entropy):
        def run():
            torch.manual_seed(5)  # fresh, identical fixture per call
            logits = torch.randn(1, S, V, requires_grad=True) * 0.5
            target_ids = torch.randint(0, V, (1, S))
            out = chunked_log_probs_and_entropy(
                logits,
                target_ids,
                5.0,
                chunk_size=CS,
                return_entropy=entropy,
                entropy_pos_cap=cap,
            )
            if entropy:
                loss = out[0].sum() + out[1].sum()
            else:
                loss = out.sum()
            loss.backward()

        return run

    noentropy = _saved_bytes(make_fwd(None, False))
    uncapped = _saved_bytes(make_fwd(None, True))
    capped = _saved_bytes(make_fwd(256, True))
    entropy_addition = uncapped - noentropy
    # The cap must remove a substantial part of the entropy branch's retained
    # bytes (measured at 27B scale: 80.94 -> 49.21 GiB, the run-8 59.8 GiB
    # peak mechanism) and must never inflate anything.
    assert capped < uncapped
    assert (uncapped - capped) >= 0.3 * entropy_addition, (
        f"cap must cut the entropy branch's retained graph: "
        f"noentropy {noentropy} uncapped {uncapped} capped {capped}"
    )


# ---------------------------------------------------------------------------
# 3. Caller-level (compute_completion_log_prob): the cap counts COMPLETION
#    tokens after the prompt AND never touches the SAPO token-lps
# ---------------------------------------------------------------------------


class _KwargForwardModel(torch.nn.Module):
    """Mini LM accepting the trainer's ``model(**inputs)`` call shape."""

    def __init__(self, vocab: int = 64, hidden: int = 16) -> None:
        super().__init__()
        self.emb = torch.nn.Embedding(vocab, hidden)
        self.head = torch.nn.Linear(hidden, vocab)

    def forward(self, input_ids, attention_mask=None, **kwargs):
        return types.SimpleNamespace(logits=self.head(self.emb(input_ids)))


def test_entropy_cap_counts_completion_tokens_and_leaves_lps_full() -> None:
    from training import grpo_trainer
    from training.grpo_utils import chunked_log_probs_and_entropy

    vocab, hidden = 64, 16
    model = _KwargForwardModel(vocab, hidden).train()

    def call(cap):
        return grpo_trainer.compute_completion_log_prob(
            model,
            None,
            "",
            "",
            torch.device("cpu"),
            max_seq_length=0,
            logit_clip=50.0,
            return_entropy=True,
            return_token_log_probs=True,
            entropy_token_cap=cap,
            prompt_token_ids=prompt_ids,
            prompt_attention_mask=None,
            completion_token_ids=completion_ids,
        )

    torch.manual_seed(9)
    vocab_s = vocab
    prompt_ids = torch.randint(0, vocab_s, (1, 10))
    completion_ids = torch.randint(0, vocab_s, (1, 40))
    with torch.enable_grad():
        lp_full, count_full, ent_full, tokens_full = call(None)
        lp_capped, count_capped, ent_capped, tokens_capped = call(8)
    # The SAPO loss path is untouched by the cap: full-length token lps,
    # identical sequence log-prob, identical count.
    assert int(count_full.item()) == 40
    assert int(count_capped.item()) == 40
    assert tokens_capped.shape == (40,)
    assert torch.equal(tokens_capped, tokens_full)
    assert torch.equal(lp_capped, lp_full)
    # Exact entropy contract: capped == mean over the first 8 COMPLETION
    # tokens (target positions 9..16) of the uncapped per-position entropy.
    with torch.enable_grad():
        full_ids = torch.cat([prompt_ids, completion_ids], dim=1)
        logits = model(full_ids).logits[:, :-1, :]  # shift like the caller
        target_ids = full_ids[:, 1:]
        _, ent_per_pos = chunked_log_probs_and_entropy(
            logits, target_ids, 50.0, return_entropy=True
        )
    ref = ent_per_pos[:, 9:17].mean()
    assert torch.allclose(ent_capped, ref, atol=1e-6)
    assert not torch.allclose(ent_full, ref, atol=1e-6)  # cap actually bites


# ---------------------------------------------------------------------------
# 4. Position-bound helper
# ---------------------------------------------------------------------------


def test_resolve_entropy_pos_cap_boundaries() -> None:
    # prompt 20 tokens, cap 256 -> completion starts at target pos 19
    assert resolve_entropy_pos_cap(prompt_len=20, entropy_token_cap=256, seq_len=500) == 275
    # cap larger than the sequence -> whole sequence (identical to uncapped)
    assert resolve_entropy_pos_cap(prompt_len=20, entropy_token_cap=256, seq_len=100) == 100
    # no cap -> None (legacy full behavior)
    assert resolve_entropy_pos_cap(prompt_len=20, entropy_token_cap=None, seq_len=500) is None
    assert resolve_entropy_pos_cap(prompt_len=20, entropy_token_cap=0, seq_len=500) is None
    # completion starts at target position 0 (empty prompt edge)
    assert resolve_entropy_pos_cap(prompt_len=1, entropy_token_cap=10, seq_len=500) == 10

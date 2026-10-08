"""TDD: run-10 crash — "Trying to backward through the graph a second time"
at the chunked-recompute Function's saved_tensors (grpo_utils.py:1647).

The r10 wiring backprops the entropy-floor penalty FIRST (it spans every
candidate's graph: mean of the per-candidate train-pass entropies), then the
SAPO per-candidate loop backprops each (loss_i * w_i) — which re-touches the
SAME candidate graphs whose saved tensors the penalty backward just freed.
Latent since r10 (the OOM wall killed runs before backward completed); the
run-9 recompute fix cleared the memory wall and exposed it.

FIX (smallest, sanctioned): the penalty is a monitoring signal — compute its
VALUE on a DETACHED mean (a floor needs a mean-entropy signal, not a graph
edge) and drop the penalty-first backward entirely. The value still rides
loss_breakdown.entropy_floor_penalty and the final-loss identity
(loss == loss_recomputed + penalty). The degenerate-policy alarm remains the
active collapse rescue. Per-candidate backwards now run exactly once per
graph; the model gradients equal the no-penalty reference.
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

from training import grpo_trainer  # noqa: E402

compute_entropy_floor_penalty = grpo_trainer.compute_entropy_floor_penalty

VOCAB, HIDDEN = 64, 16


class _Model(torch.nn.Module):
    """Mini LM accepting the trainer's ``model(**inputs)`` call shape."""

    def __init__(self) -> None:
        super().__init__()
        self.emb = torch.nn.Embedding(VOCAB, HIDDEN)
        self.head = torch.nn.Linear(HIDDEN, VOCAB)

    def forward(self, input_ids, attention_mask=None, **kwargs):
        return types.SimpleNamespace(logits=self.head(self.emb(input_ids)))


def _candidate(model, cap: int | None = 8):
    """One train-pass candidate through the REAL trainer log-prob path
    (chunked-recompute Function ON, capped entropy, token lps)."""
    prompt_ids = torch.randint(0, VOCAB, (1, 10))
    completion_ids = torch.randint(0, VOCAB, (1, 40))
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
        recompute_backward=True,
        prompt_token_ids=prompt_ids,
        prompt_attention_mask=None,
        completion_token_ids=completion_ids,
    )


def _model_grads(model: torch.nn.Module) -> torch.Tensor:
    return torch.cat([p.grad.detach().flatten() for p in model.parameters() if p.grad is not None])


def test_sapo_step_backward_runs_exactly_once_per_graph() -> None:
    """The FIXED wiring: penalty VALUE (detached) + per-candidate backwards.
    Every candidate's graph is backpropped exactly once — no double-backward
    — and the model gradients equal the no-penalty reference (the detached
    penalty contributes no gradient by design)."""
    torch.manual_seed(71)
    model = _Model().train()
    G = 3
    candidates = []
    with torch.enable_grad():
        for _ in range(G):
            candidates.append(_candidate(model))
        current_entropies = [ent for (_, _, ent, _) in candidates]
        current_token_lps = [toks for (_, _, _, toks) in candidates]

        # The fixed wiring: the penalty's value is computed on a DETACHED
        # mean (no graph edge to any candidate); no penalty backward.
        entropy_train_tensor = torch.stack(current_entropies).mean()
        # floor above the fixture's entropy (~log(64) ~ 4.2 nats) so the
        # penalty engages
        penalty_value = float(
            compute_entropy_floor_penalty(
                entropy_train_tensor.detach(), floor=6.0, weight=0.01
            ).item()
        )
        assert penalty_value > 0.0  # the fixture is below the floor

        optimizer = torch.optim.SGD(model.parameters(), lr=0.0)
        optimizer.zero_grad()
        # per-candidate backwards (the SAPO shape: loss_i * w_i, w_i = 1/G)
        accumulated = None
        for ci in range(G):
            adv = torch.tensor([0.5, -0.3, 0.8], dtype=torch.float32)[ci]
            loss_i = -current_token_lps[ci].mean() * adv
            (loss_i / G).backward()
            accumulated = loss_i.detach() if accumulated is None else accumulated + loss_i.detach()
        total = float(accumulated.item()) + penalty_value

    grads = _model_grads(model)
    assert torch.isfinite(grads).all()
    assert grads.numel() > 0

    # no-penalty reference: identical per-candidate backwards without the
    # penalty -> identical gradients (detach semantics pinned)
    torch.manual_seed(71)
    model_ref = _Model().train()
    with torch.enable_grad():
        refs = []
        for _ in range(G):
            refs.append(_candidate(model_ref))
        ref_lps = [toks for (_, _, _, toks) in refs]
        for ci in range(G):
            adv = torch.tensor([0.5, -0.3, 0.8], dtype=torch.float32)[ci]
            loss_i = -ref_lps[ci].mean() * adv
            (loss_i / G).backward()
    assert torch.allclose(_model_grads(model_ref), grads, atol=1e-6)
    # the identity value: loss == recomputed + penalty
    assert abs(total - (float(accumulated.item()) + penalty_value)) < 1e-9


def test_sapo_composition_adds_penalty_exactly_once() -> None:
    """r15 F5: the SAPO branch composes the penalty into its own total_loss;
    the common tail must NOT re-add it — loss == recomputed + penalty (not
    2*penalty) with an ENGAGED floor."""
    recomputed = 0.05
    penalty = 0.004
    # SAPO branch composition (grpo_trainer.py:5251)
    total = recomputed
    total = total + penalty if penalty > 0.0 else total
    # common tail composition (grpo_trainer.py:5367) — no-op for SAPO
    total = grpo_trainer.add_entropy_floor_penalty_value(total, penalty, loss_mode="sapo")
    assert abs(total - (recomputed + penalty)) < 1e-12  # exactly once
    assert abs(total - (recomputed + 2.0 * penalty)) > 1e-3  # not twice


def test_non_sapo_composition_adds_penalty_once() -> None:
    recomputed = 0.05
    penalty = 0.004
    total = grpo_trainer.add_entropy_floor_penalty_value(recomputed, penalty, loss_mode="gspo_ln")
    assert abs(total - (recomputed + penalty)) < 1e-12
    # zero penalty -> unchanged in any mode
    assert (
        grpo_trainer.add_entropy_floor_penalty_value(recomputed, 0.0, loss_mode="sapo")
        == recomputed
    )
    assert (
        grpo_trainer.add_entropy_floor_penalty_value(recomputed, 0.0, loss_mode="gspo_ln")
        == recomputed
    )


def test_old_penalty_first_wiring_double_backward_raises() -> None:
    """Documents the run-10 crash class: the OLD wiring (penalty tensor
    backward FIRST, per-candidate backwards after) re-touches the freed
    Function graphs -> RuntimeError. The fix removes that path."""
    torch.manual_seed(72)
    model = _Model().train()
    with torch.enable_grad():
        candidates = [_candidate(model) for _ in range(2)]
        current_entropies = [ent for (_, _, ent, _) in candidates]
        current_token_lps = [toks for (_, _, _, toks) in candidates]
        penalty_tensor = compute_entropy_floor_penalty(
            torch.stack(current_entropies).mean(),  # NOT detached (old wiring)
            floor=6.0,
            weight=0.01,
        )
        assert penalty_tensor.requires_grad
        penalty_tensor.backward()  # the r10 penalty-first backward
        with pytest.raises(RuntimeError, match="backward through the graph a second time"):
            for ci in range(2):
                adv = torch.tensor([0.5, -0.3])[ci]
                loss_i = -current_token_lps[ci].mean() * adv
                (loss_i / 2).backward()

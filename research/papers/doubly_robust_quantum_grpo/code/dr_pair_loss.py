"""Pairwise DPO loss for the doubly_robust_quantum_grpo research method.

This helper implements the DPO half of the doubly-robust estimator
described in ../paper.md. It is intended to be called by
`training/grpo_trainer.py` after the existing PPO backward, only when
the `doubly_robust_quantum_grpo` research method is enabled.

The function is deliberately framework-agnostic about where the
log-probs come from: the trainer already computes per-candidate
`log_probs` and `old_log_probs` for the PPO step, and the reference
log-probs can be either:

- the same `old_log_probs` (cheap, default; the LoRA-off reference is
  approximated by the snapshot taken at the start of the step), or
- a frozen reference model's log-probs (passed in via
  `ref_log_probs` when available).

Usage
-----

    from research.papers.doubly_robust_quantum_grpo.code.dr_pair_loss import (
        build_dr_pairs,
        dr_pair_loss,
    )

    pairs = build_dr_pairs(
        rewards=rewards_tensor,           # shape [group_size]
        codes=codes_list,                  # shape [group_size]
        min_reward_gap=0.4,
        max_pairs=1,
    )
    if pairs:
        loss = dr_pair_loss(
            log_probs=log_probs_tensor,    # shape [group_size]
            ref_log_probs=old_log_probs_tensor,  # shape [group_size]
            pairs=pairs,
            beta=0.07,
            device=device,
        )
        total_loss = ppo_loss + 0.3 * loss

The pair indices refer to positions inside the group tensor, so the
trainer does not need to materialize a separate pair batch.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass(frozen=True)
class DrPair:
    """A (chosen, rejected) pair mined from the same GRPO group.

    Attributes
    ----------
    chosen_idx : int
        Position of the chosen (higher-reward) candidate inside the
        group tensor.
    rejected_idx : int
        Position of the rejected (lower-reward) candidate inside the
        group tensor.
    reward_gap : float
        Absolute reward difference between chosen and rejected. Used
        by the trainer for logging and for the fast-abandon check
        (gaps > 1.0 are suspicious and should be logged).
    """

    chosen_idx: int
    rejected_idx: int
    reward_gap: float


def build_dr_pairs(
    *,
    rewards: torch.Tensor,
    codes: list[str] | None = None,
    min_reward_gap: float = 0.4,
    max_pairs: int = 1,
) -> list[DrPair]:
    """Mine at most `max_pairs` (chosen, rejected) pairs from a group.

    The mining rule is:

    1. Pick the highest-reward candidate as `chosen` and the
       lowest-reward candidate as `rejected`.
    2. Skip the pair if the reward gap is < `min_reward_gap` (near-tied
       pairs inject noise).
    3. Skip the pair if `chosen` and `rejected` have identical code
       (when `codes` is provided). This guards against the degenerate
       case where the group produces the same completion twice.
    4. Return at most `max_pairs` pairs, sorted by descending reward
       gap.

    The function is device-agnostic: it operates on the CPU copy of
    the rewards tensor. The trainer should pass `rewards.detach().cpu()`
    if the rewards tensor lives on NPU.
    """
    if rewards is None or rewards.numel() < 2:
        return []
    if max_pairs <= 0:
        return []

    # Detach and move to CPU for safe indexing.
    rewards_cpu = rewards.detach().to(torch.device("cpu"), dtype=torch.float32)
    n = int(rewards_cpu.numel())
    if n < 2:
        return []

    # Rank candidates by reward (descending).
    order = torch.argsort(rewards_cpu, descending=True).tolist()
    top_idx = int(order[0])
    bottom_idx = int(order[-1])
    chosen_reward = float(rewards_cpu[top_idx].item())
    rejected_reward = float(rewards_cpu[bottom_idx].item())
    gap = abs(chosen_reward - rejected_reward)
    if gap < min_reward_gap:
        return []

    if codes is not None:
        if top_idx >= len(codes) or bottom_idx >= len(codes):
            return []
        if str(codes[top_idx]) == str(codes[bottom_idx]):
            return []

    return [DrPair(chosen_idx=top_idx, rejected_idx=bottom_idx, reward_gap=gap)]


def dr_pair_loss(
    *,
    log_probs: torch.Tensor,
    ref_log_probs: torch.Tensor,
    pairs: list[DrPair],
    beta: float = 0.07,
    device: torch.device | None = None,
) -> torch.Tensor:
    """Compute the DPO pairwise loss for a list of in-group pairs.

    Parameters
    ----------
    log_probs : torch.Tensor
        Per-candidate log p_theta(y|x), shape [group_size]. This is
        the same tensor used by the PPO loss.
    ref_log_probs : torch.Tensor
        Per-candidate log p_ref(y|x), shape [group_size]. By default
        this is the `old_log_probs` snapshot, which approximates the
        LoRA-off reference. Pass a frozen reference model's log-probs
        for the strict DPO formulation.
    pairs : list[DrPair]
        Pairs mined by `build_dr_pairs`. Indices refer to positions in
        `log_probs` / `ref_log_probs`.
    beta : float
        DPO inverse temperature. Default 0.07 matches
        `configs/dpo/qwen36_35b_a3b_dpo_v1.json`.
    device : torch.device | None
        Device for the output loss tensor. Defaults to the device of
        `log_probs`.

    Returns
    -------
    torch.Tensor
        Scalar loss = -mean( log sigmoid( beta * (s_chosen - s_rejected) ) ),
        where s(y) = log_probs[y] - ref_log_probs[y]. Returns a zero
        tensor on `device` if `pairs` is empty.
    """
    if not pairs:
        if device is None:
            device = log_probs.device if log_probs is not None else torch.device("cpu")
        return torch.zeros((), device=device, dtype=torch.float32)

    log_probs = log_probs.detach() * 0.0 + log_probs  # keep grad
    ref_log_probs = ref_log_probs.detach()

    chosen_idx = torch.tensor(
        [p.chosen_idx for p in pairs], dtype=torch.long, device=log_probs.device
    )
    rejected_idx = torch.tensor(
        [p.rejected_idx for p in pairs], dtype=torch.long, device=log_probs.device
    )

    chosen_logp = log_probs[chosen_idx]
    rejected_logp = log_probs[rejected_idx]
    chosen_ref = ref_log_probs[chosen_idx]
    rejected_ref = ref_log_probs[rejected_idx]

    chosen_scores = chosen_logp - chosen_ref
    rejected_scores = rejected_logp - rejected_ref
    logits = beta * (chosen_scores - rejected_scores)
    # -log sigmoid(logits) = log(1 + exp(-logits)) = softplus(-logits)
    loss = torch.nn.functional.softplus(-logits).mean()
    return loss


def dr_variance_correction(
    *,
    ppo_loss: torch.Tensor,
    ppo_ratio: torch.Tensor,
    advantages: torch.Tensor,
    psi: float = 0.5,
) -> torch.Tensor:
    """Doubly-robust variance-correction term for the PPO loss.

    The DR estimator is

        L_DR = L_PPO + psi * E[ (r - 1) * A ]

    where `r = ppo_ratio` and `A = advantages`. The correction term
    has zero mean under the behavior policy but reduces variance when
    the behavior policy is close to the target.

    This helper is provided for trainers that want the full DR
    estimator (not just the DPO pair loss). The default `psi = 0.5`
    is the midpoint of the DR range; tune after warmup.
    """
    if psi == 0.0:
        return ppo_loss
    correction = psi * ((ppo_ratio - 1.0) * advantages.detach()).mean()
    return ppo_loss + correction


__all__ = [
    "DrPair",
    "build_dr_pairs",
    "dr_pair_loss",
    "dr_variance_correction",
]

"""Tests for the doubly_robust_quantum_grpo research-method plugin.

Covers:
- plugin discovery via load_research_methods
- reward-breakdown augmentation
- prompt augmentation
- task-weight adjustment
- dr_pair_loss helper (build_dr_pairs + dr_pair_loss + dr_variance_correction)
- compute_dr_pair_loss trainer hook (no-op for base GRPO, active when plugin enabled)
"""

from __future__ import annotations

import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.grpo_trainer import compute_dr_pair_loss, compute_dr_variance_correction
from training.research_plugins import load_research_methods


def test_plugin_discovery() -> None:
    methods = load_research_methods(["doubly_robust_quantum_grpo"])
    assert len(methods) == 1
    m = methods[0]
    assert m.method_id == "doubly_robust_quantum_grpo"
    assert m.paper_title == "Doubly-Robust GRPO for Quantum Code Generation"


def test_extra_run_config_has_dr_hyperparameters() -> None:
    m = load_research_methods(["doubly_robust_quantum_grpo"])[0]
    cfg = m.extra_run_config()["doubly_robust_quantum_grpo"]
    assert cfg["enabled"] is True
    assert cfg["dr_dpo_beta"] == 0.07
    assert cfg["dr_psi_init"] == 0.5
    assert cfg["dr_pair_min_reward_gap"] == 0.4
    assert cfg["dr_pair_loss_weight"] == 0.3
    assert cfg["dr_pair_max_per_step"] == 1


def test_augment_grpo_prompt_adds_suffix_only_for_grpo() -> None:
    m = load_research_methods(["doubly_robust_quantum_grpo"])[0]
    out_grpo = m.augment_grpo_prompt("def foo():", task={}, stage="grpo")
    assert "verifier" in out_grpo.lower()
    assert out_grpo != "def foo():"
    # SFT stage should be untouched
    out_sft = m.augment_grpo_prompt("def foo():", task={}, stage="sft")
    assert out_sft == "def foo():"


def test_adjust_task_weight_boosts_rich_tasks_only() -> None:
    m = load_research_methods(["doubly_robust_quantum_grpo"])[0]
    rich = m.adjust_task_weight(
        1.0,
        task={"behavior_hints": ["a", "b"], "required_interface": ["x"]},
        stage="grpo",
    )
    assert rich == 1.12
    poor = m.adjust_task_weight(
        1.0,
        task={"behavior_hints": [], "required_interface": []},
        stage="grpo",
    )
    assert poor == 1.0
    # SFT stage should be untouched
    sft = m.adjust_task_weight(
        1.0,
        task={"behavior_hints": ["a", "b"], "required_interface": ["x"]},
        stage="sft",
    )
    assert sft == 1.0


def test_adjust_reward_breakdown_adds_dr_defaults() -> None:
    m = load_research_methods(["doubly_robust_quantum_grpo"])[0]
    r = m.adjust_reward_breakdown(
        {"total_reward": 0.5, "pass_reward": 1.0},
        code="x",
        result=None,
        task={},
        stage="grpo",
    )
    assert r["dr_dpo_beta"] == 0.07
    assert r["dr_psi_init"] == 0.5
    assert r["dr_pair_min_reward_gap"] == 0.4
    assert r["dr_pair_loss_weight"] == 0.3
    assert r["dr_pair_max_per_step"] == 1
    assert r["dr_pair_role"] is None
    assert r["dr_pair_partner_idx"] == -1
    assert r["dr_pair_reward_gap"] == 0.0
    # SFT stage should be untouched (no dr_ keys added)
    r_sft = m.adjust_reward_breakdown(
        {"total_reward": 0.5, "pass_reward": 1.0},
        code="x",
        result=None,
        task={},
        stage="sft",
    )
    assert "dr_dpo_beta" not in r_sft


def test_build_dr_pairs_mines_clear_pair() -> None:
    from research.papers.doubly_robust_quantum_grpo.code.dr_pair_loss import build_dr_pairs

    rewards = torch.tensor([0.9, 0.1, 0.5, 0.3])
    codes = ["def a(): pass", "def b(): pass", "def c(): pass", "def d(): pass"]
    pairs = build_dr_pairs(rewards=rewards, codes=codes, min_reward_gap=0.4, max_pairs=1)
    assert len(pairs) == 1
    assert pairs[0].chosen_idx == 0
    assert pairs[0].rejected_idx == 1
    assert abs(pairs[0].reward_gap - 0.8) < 1e-6


def test_build_dr_pairs_skips_tied_rewards() -> None:
    from research.papers.doubly_robust_quantum_grpo.code.dr_pair_loss import build_dr_pairs

    rewards = torch.tensor([0.5, 0.5, 0.5, 0.5])
    codes = ["a", "b", "c", "d"]
    pairs = build_dr_pairs(rewards=rewards, codes=codes, min_reward_gap=0.4, max_pairs=1)
    assert pairs == []


def test_build_dr_pairs_skips_identical_codes() -> None:
    from research.papers.doubly_robust_quantum_grpo.code.dr_pair_loss import build_dr_pairs

    rewards = torch.tensor([0.9, 0.1, 0.5, 0.3])
    codes_same = ["def a(): pass"] * 4
    pairs = build_dr_pairs(rewards=rewards, codes=codes_same, min_reward_gap=0.4, max_pairs=1)
    assert pairs == []


def test_build_dr_pairs_respects_max_pairs() -> None:
    from research.papers.doubly_robust_quantum_grpo.code.dr_pair_loss import build_dr_pairs

    rewards = torch.tensor([0.9, 0.1])
    codes = ["def a(): pass", "def b(): pass"]
    # max_pairs=0 should return no pairs
    pairs = build_dr_pairs(rewards=rewards, codes=codes, min_reward_gap=0.4, max_pairs=0)
    assert pairs == []


def test_dr_pair_loss_returns_zero_for_empty_pairs() -> None:
    from research.papers.doubly_robust_quantum_grpo.code.dr_pair_loss import dr_pair_loss

    lp = torch.tensor([-1.0, -2.0], requires_grad=True)
    ref = torch.tensor([-1.0, -2.0])
    loss = dr_pair_loss(log_probs=lp, ref_log_probs=ref, pairs=[], beta=0.07)
    assert float(loss) == 0.0


def test_dr_pair_loss_has_gradient_on_chosen_and_rejected() -> None:
    from research.papers.doubly_robust_quantum_grpo.code.dr_pair_loss import (
        build_dr_pairs,
        dr_pair_loss,
    )

    rewards = torch.tensor([0.9, 0.1, 0.5, 0.3])
    codes = ["a", "b", "c", "d"]
    pairs = build_dr_pairs(rewards=rewards, codes=codes, min_reward_gap=0.4, max_pairs=1)
    lp = torch.tensor([-1.0, -2.0, -1.5, -1.8], requires_grad=True)
    ref = torch.tensor([-1.1, -1.9, -1.4, -1.7])
    loss = dr_pair_loss(log_probs=lp, ref_log_probs=ref, pairs=pairs, beta=0.07)
    loss.backward()
    # Chosen (idx 0) and rejected (idx 1) should have non-zero grad
    assert lp.grad is not None
    assert abs(float(lp.grad[0])) > 0
    assert abs(float(lp.grad[1])) > 0
    # Other candidates should have zero grad from the pair loss
    assert float(lp.grad[2]) == 0.0
    assert float(lp.grad[3]) == 0.0


def test_dr_variance_correction_zero_when_psi_zero() -> None:
    from research.papers.doubly_robust_quantum_grpo.code.dr_pair_loss import dr_variance_correction

    ppo_loss = torch.tensor(0.5)
    ppo_ratio = torch.tensor([1.1, 0.9, 1.0, 1.2])
    advantages = torch.tensor([0.2, -0.1, 0.0, 0.3])
    out = dr_variance_correction(
        ppo_loss=ppo_loss, ppo_ratio=ppo_ratio, advantages=advantages, psi=0.0
    )
    assert float(out) == 0.5


def test_dr_variance_correction_adds_term_when_psi_nonzero() -> None:
    from research.papers.doubly_robust_quantum_grpo.code.dr_pair_loss import dr_variance_correction

    ppo_loss = torch.tensor(0.5)
    ppo_ratio = torch.tensor([1.1, 0.9, 1.0, 1.2])
    advantages = torch.tensor([0.2, -0.1, 0.0, 0.3])
    out = dr_variance_correction(
        ppo_loss=ppo_loss, ppo_ratio=ppo_ratio, advantages=advantages, psi=0.5
    )
    assert abs(float(out) - 0.5) > 0  # the correction shifted the loss


def test_compute_dr_pair_loss_no_op_without_methods() -> None:
    rewards = torch.tensor([0.9, 0.1, 0.5, 0.3])
    codes = ["a", "b", "c", "d"]
    lp = [
        torch.tensor(-1.0, requires_grad=True),
        torch.tensor(-2.0, requires_grad=True),
        torch.tensor(-1.5, requires_grad=True),
        torch.tensor(-1.8, requires_grad=True),
    ]
    ref = [torch.tensor(-1.1), torch.tensor(-1.9), torch.tensor(-1.4), torch.tensor(-1.7)]
    loss, info = compute_dr_pair_loss(
        research_methods=[],
        rewards=rewards,
        codes=codes,
        current_log_probs=lp,
        old_log_probs=ref,
    )
    assert float(loss) == 0.0
    assert info["dr_pair_mined"] is False


def test_compute_dr_pair_loss_active_with_plugin() -> None:
    methods = load_research_methods(["doubly_robust_quantum_grpo"])
    rewards = torch.tensor([0.9, 0.1, 0.5, 0.3])
    codes = ["a", "b", "c", "d"]
    lp = [
        torch.tensor(-1.0, requires_grad=True),
        torch.tensor(-2.0, requires_grad=True),
        torch.tensor(-1.5, requires_grad=True),
        torch.tensor(-1.8, requires_grad=True),
    ]
    ref = [torch.tensor(-1.1), torch.tensor(-1.9), torch.tensor(-1.4), torch.tensor(-1.7)]
    loss, info = compute_dr_pair_loss(
        research_methods=methods,
        rewards=rewards,
        codes=codes,
        current_log_probs=lp,
        old_log_probs=ref,
    )
    assert info["dr_pair_mined"] is True
    assert info["dr_pair_reward_gap"] > 0.4
    assert info["dr_pair_loss_weight"] == 0.3
    assert float(loss) > 0.0


def test_compute_dr_pair_loss_no_op_with_non_dr_method() -> None:
    methods = load_research_methods(["clause_aware_verifier_reward"])
    rewards = torch.tensor([0.9, 0.1, 0.5, 0.3])
    codes = ["a", "b", "c", "d"]
    lp = [
        torch.tensor(-1.0, requires_grad=True),
        torch.tensor(-2.0, requires_grad=True),
        torch.tensor(-1.5, requires_grad=True),
        torch.tensor(-1.8, requires_grad=True),
    ]
    ref = [torch.tensor(-1.1), torch.tensor(-1.9), torch.tensor(-1.4), torch.tensor(-1.7)]
    loss, info = compute_dr_pair_loss(
        research_methods=methods,
        rewards=rewards,
        codes=codes,
        current_log_probs=lp,
        old_log_probs=ref,
    )
    assert float(loss) == 0.0
    assert info["dr_pair_mined"] is False


def test_compute_dr_variance_correction_no_op_without_methods() -> None:
    log_probs = torch.tensor([-1.0, -2.0, -1.5, -1.8], requires_grad=True)
    old_log_probs = torch.tensor([-1.1, -1.9, -1.4, -1.7])
    advantages = torch.tensor([0.4, -0.3, 0.1, -0.2])
    loss, info = compute_dr_variance_correction(
        research_methods=[],
        log_probs=log_probs,
        old_log_probs=old_log_probs,
        advantages=advantages,
        ratio_clip_log_delta=10.0,
    )
    assert float(loss) == 0.0
    assert info["dr_psi"] == 0.0
    assert info["dr_variance_correction_value"] == 0.0


def test_compute_dr_variance_correction_no_op_with_non_dr_method() -> None:
    methods = load_research_methods(["clause_aware_verifier_reward"])
    log_probs = torch.tensor([-1.0, -2.0, -1.5, -1.8], requires_grad=True)
    old_log_probs = torch.tensor([-1.1, -1.9, -1.4, -1.7])
    advantages = torch.tensor([0.4, -0.3, 0.1, -0.2])
    loss, info = compute_dr_variance_correction(
        research_methods=methods,
        log_probs=log_probs,
        old_log_probs=old_log_probs,
        advantages=advantages,
        ratio_clip_log_delta=10.0,
    )
    assert float(loss) == 0.0


def test_compute_dr_variance_correction_active_with_plugin() -> None:
    methods = load_research_methods(["doubly_robust_quantum_grpo"])
    # log_probs slightly higher than old_log_probs => ratio > 1 for idx0 only
    log_probs = torch.tensor([-0.9, -1.9, -1.4, -1.7], requires_grad=True)
    old_log_probs = torch.tensor([-1.1, -1.9, -1.4, -1.7])
    advantages = torch.tensor([0.4, -0.3, 0.1, -0.2])
    loss, info = compute_dr_variance_correction(
        research_methods=methods,
        log_probs=log_probs,
        old_log_probs=old_log_probs,
        advantages=advantages,
        ratio_clip_log_delta=10.0,
    )
    # Default dr_psi_init = 0.5
    assert info["dr_psi"] == 0.5
    # correction = 0.5 * E[(r-1)*A]. idx0: r=exp(0.2)>1, A=0.4 => +;
    # idx1/2/3: r=1 => 0. So correction > 0.
    assert float(loss) > 0.0
    assert info["dr_variance_correction_value"] > 0.0
    # Gradient must flow back to log_probs
    loss.backward()
    assert log_probs.grad is not None
    assert abs(float(log_probs.grad[0])) > 0.0


def test_compute_dr_variance_correction_psi_zero_returns_zero() -> None:
    # Build a method with dr_psi_init = 0.0 to confirm the zero-psi
    # fast path returns a zero tensor.
    methods = load_research_methods(["doubly_robust_quantum_grpo"])
    m = methods[0]
    original = m.dr_psi_init
    m.dr_psi_init = 0.0
    try:
        log_probs = torch.tensor([-0.9, -1.9, -1.4, -1.7], requires_grad=True)
        old_log_probs = torch.tensor([-1.1, -1.9, -1.4, -1.7])
        advantages = torch.tensor([0.4, -0.3, 0.1, -0.2])
        loss, info = compute_dr_variance_correction(
            research_methods=methods,
            log_probs=log_probs,
            old_log_probs=old_log_probs,
            advantages=advantages,
            ratio_clip_log_delta=10.0,
        )
        assert float(loss) == 0.0
        assert info["dr_psi"] == 0.0
    finally:
        m.dr_psi_init = original


def test_compute_dr_variance_correction_psi_warmup_linear() -> None:
    """Linear psi warmup: psi ramps 0 -> psi_init over the first
    `dr_psi_warmup_steps` steps, then holds at psi_init.
    """
    methods = load_research_methods(["doubly_robust_quantum_grpo"])
    m = methods[0]
    original_psi = m.dr_psi_init
    original_extra = m.extra_run_config
    try:
        m.dr_psi_init = 0.5
        # Inject a warmup_steps config via extra_run_config override.
        base_extra = m.extra_run_config()
        warmup_extra = dict(base_extra)
        warmup_extra["doubly_robust_quantum_grpo"] = dict(
            warmup_extra.get("doubly_robust_quantum_grpo", {})
        )
        warmup_extra["doubly_robust_quantum_grpo"]["dr_psi_init"] = 0.5
        warmup_extra["doubly_robust_quantum_grpo"]["dr_psi_warmup_steps"] = 10
        m.extra_run_config = lambda: warmup_extra  # type: ignore[method-assign]

        log_probs = torch.tensor([-0.9, -1.9, -1.4, -1.7], requires_grad=True)
        old_log_probs = torch.tensor([-1.1, -1.9, -1.4, -1.7])
        advantages = torch.tensor([0.4, -0.3, 0.1, -0.2])

        # Step 0 -> psi = 0.0 (start of warmup)
        _, info_0 = compute_dr_variance_correction(
            research_methods=methods,
            log_probs=log_probs,
            old_log_probs=old_log_probs,
            advantages=advantages,
            ratio_clip_log_delta=10.0,
            current_step=0,
        )
        assert info_0["dr_psi"] == 0.0
        assert info_0["dr_psi_init"] == 0.5
        assert info_0["dr_psi_warmup_steps"] == 10
        assert info_0["dr_psi_current_step"] == 0

        # Step 5 -> psi = 0.25 (midpoint of warmup)
        _, info_5 = compute_dr_variance_correction(
            research_methods=methods,
            log_probs=log_probs,
            old_log_probs=old_log_probs,
            advantages=advantages,
            ratio_clip_log_delta=10.0,
            current_step=5,
        )
        assert abs(info_5["dr_psi"] - 0.25) < 1e-6

        # Step 10 -> psi = 0.5 (end of warmup, full psi)
        _, info_10 = compute_dr_variance_correction(
            research_methods=methods,
            log_probs=log_probs,
            old_log_probs=old_log_probs,
            advantages=advantages,
            ratio_clip_log_delta=10.0,
            current_step=10,
        )
        assert abs(info_10["dr_psi"] - 0.5) < 1e-6

        # Step 20 -> psi = 0.5 (post-warmup, holds at psi_init)
        _, info_20 = compute_dr_variance_correction(
            research_methods=methods,
            log_probs=log_probs,
            old_log_probs=old_log_probs,
            advantages=advantages,
            ratio_clip_log_delta=10.0,
            current_step=20,
        )
        assert abs(info_20["dr_psi"] - 0.5) < 1e-6
    finally:
        m.dr_psi_init = original_psi
        m.extra_run_config = original_extra  # type: ignore[method-assign]


def test_compute_dr_variance_correction_no_warmup_when_steps_zero() -> None:
    """When dr_psi_warmup_steps == 0 (default), psi is constant —
    preserves the pre-warmup behavior regardless of current_step.
    """
    methods = load_research_methods(["doubly_robust_quantum_grpo"])
    m = methods[0]
    original_psi = m.dr_psi_init
    try:
        m.dr_psi_init = 0.5
        log_probs = torch.tensor([-0.9, -1.9, -1.4, -1.7], requires_grad=True)
        old_log_probs = torch.tensor([-1.1, -1.9, -1.4, -1.7])
        advantages = torch.tensor([0.4, -0.3, 0.1, -0.2])

        # Default config has dr_psi_warmup_steps = 0 -> no warmup.
        _, info_a = compute_dr_variance_correction(
            research_methods=methods,
            log_probs=log_probs,
            old_log_probs=old_log_probs,
            advantages=advantages,
            ratio_clip_log_delta=10.0,
            current_step=0,
        )
        _, info_b = compute_dr_variance_correction(
            research_methods=methods,
            log_probs=log_probs,
            old_log_probs=old_log_probs,
            advantages=advantages,
            ratio_clip_log_delta=10.0,
            current_step=100,
        )
        # Both should report the full psi_init (no warmup applied).
        assert abs(info_a["dr_psi"] - 0.5) < 1e-6
        assert abs(info_b["dr_psi"] - 0.5) < 1e-6
        assert info_a["dr_psi_warmup_steps"] == 0
    finally:
        m.dr_psi_init = original_psi


def test_compute_dr_variance_correction_current_step_none_no_warmup() -> None:
    """When current_step is None (back-compat for callers that don't
    pass it), psi is constant at psi_init even if warmup_steps > 0.
    This protects any older call path that hasn't been updated.
    """
    methods = load_research_methods(["doubly_robust_quantum_grpo"])
    m = methods[0]
    original_psi = m.dr_psi_init
    original_extra = m.extra_run_config
    try:
        m.dr_psi_init = 0.5
        base_extra = m.extra_run_config()
        warmup_extra = dict(base_extra)
        warmup_extra["doubly_robust_quantum_grpo"] = dict(
            warmup_extra.get("doubly_robust_quantum_grpo", {})
        )
        warmup_extra["doubly_robust_quantum_grpo"]["dr_psi_init"] = 0.5
        warmup_extra["doubly_robust_quantum_grpo"]["dr_psi_warmup_steps"] = 10
        m.extra_run_config = lambda: warmup_extra  # type: ignore[method-assign]

        log_probs = torch.tensor([-0.9, -1.9, -1.4, -1.7], requires_grad=True)
        old_log_probs = torch.tensor([-1.1, -1.9, -1.4, -1.7])
        advantages = torch.tensor([0.4, -0.3, 0.1, -0.2])

        _, info = compute_dr_variance_correction(
            research_methods=methods,
            log_probs=log_probs,
            old_log_probs=old_log_probs,
            advantages=advantages,
            ratio_clip_log_delta=10.0,
            current_step=None,
        )
        # current_step is None -> no warmup applied -> full psi_init.
        assert abs(info["dr_psi"] - 0.5) < 1e-6
        assert info["dr_psi_current_step"] is None
    finally:
        m.dr_psi_init = original_psi
        m.extra_run_config = original_extra  # type: ignore[method-assign]

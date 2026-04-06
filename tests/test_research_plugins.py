from __future__ import annotations

from training.research_plugins import load_research_methods


def test_load_research_methods_finds_plugin_modules() -> None:
    methods = load_research_methods(
        [
            "verifier_guided_repair_curriculum",
            "clause_aware_verifier_reward",
            "ast_anchor_interface_grounding",
            "self_consistency_verifier_routing",
            "uncertainty_triggered_repair_replay",
            "behavior_anchor_coverage_reward",
        ]
    )
    assert [method.method_id for method in methods] == [
        "verifier_guided_repair_curriculum",
        "clause_aware_verifier_reward",
        "ast_anchor_interface_grounding",
        "self_consistency_verifier_routing",
        "uncertainty_triggered_repair_replay",
        "behavior_anchor_coverage_reward",
    ]


def test_clause_aware_plugin_adds_clause_reward() -> None:
    method = load_research_methods(["clause_aware_verifier_reward"])[0]
    reward = method.adjust_reward_breakdown(
        {
            "total_reward": 0.5,
            "syntax_reward": 1.0,
            "interface_reward": 0.5,
        },
        code="def solve(x):\n    return x\n",
        result={"details": ["phase output mismatch on final register"]},
        task={"behavior_hints": ["Return the phase output on the final register"]},
        stage="grpo",
    )
    assert "clause_reward" in reward
    assert 0.0 <= float(reward["clause_reward"]) <= 1.0


def test_new_plugins_expose_run_config_and_reward_fields() -> None:
    self_consistency, replay = load_research_methods(
        [
            "self_consistency_verifier_routing",
            "uncertainty_triggered_repair_replay",
        ]
    )
    routed_reward = self_consistency.adjust_reward_breakdown(
        {
            "total_reward": 0.4,
            "pass_reward": 0.0,
            "syntax_reward": 1.0,
            "interface_reward": 0.8,
            "verifier_reward": 0.6,
        },
        code="def solve(x):\n    return x\n",
        result={"passed": False},
        task={"behavior_hints": ["Preserve the interface"], "required_interface": ["solve(x)"]},
        stage="grpo",
    )
    replay_reward = replay.adjust_reward_breakdown(
        {
            "total_reward": 0.35,
            "syntax_reward": 1.0,
            "interface_reward": 0.5,
            "verifier_reward": 0.4,
        },
        code="def solve(x):\n    return x\n",
        result={"passed": False},
        task={
            "difficulty": "hard",
            "behavior_hints": ["Preserve the interface", "Handle edge cases", "Return a stable value"],
            "required_interface": ["solve(x)"],
            "detail_budget": 4,
        },
        stage="grpo",
    )
    assert "self_consistency_routing_bonus" in routed_reward
    assert "uncertainty_replay_credit" in replay_reward
    assert self_consistency.extra_run_config()["self_consistency_routing"]["enabled"] is True
    assert replay.extra_run_config()["repair_prompt_policy"] == "preserve-interface-minimal-repair"


def test_behavior_anchor_plugin_adds_anchor_reward_and_spread() -> None:
    import torch

    from training.grpo_utils import reward_signal_stats

    method = load_research_methods(["behavior_anchor_coverage_reward"])[0]
    task = {
        "behavior_hints": [
            "Apply syndrome measurement and corrected logical state mapping",
            "Return syndrome bits and corrected state",
        ],
        "required_interface": ["bit_flip_code(initial_state, error_qubit)"],
    }
    baseline_rewards = [
        {"total_reward": 0.28, "syntax_reward": 1.0, "interface_reward": 0.6, "verifier_reward": 0.2},
        {"total_reward": 0.28, "syntax_reward": 1.0, "interface_reward": 0.6, "verifier_reward": 0.2},
        {"total_reward": 0.28, "syntax_reward": 1.0, "interface_reward": 0.6, "verifier_reward": 0.2},
    ]
    codes = [
        "def bit_flip_code(initial_state, error_qubit):\n    syndrome_bits = [1, 0]\n    corrected_state = initial_state\n    return {'syndrome': syndrome_bits, 'corrected_state': corrected_state}\n",
        "def bit_flip_code(initial_state, error_qubit):\n    return {'syndrome': [0, 0], 'corrected_state': initial_state}\n",
        "def bit_flip_code(initial_state, error_qubit):\n    return {'value': initial_state}\n",
    ]
    adjusted = [
        method.adjust_reward_breakdown(dict(reward), code=code, result={"passed": False}, task=task, stage="grpo")
        for reward, code in zip(baseline_rewards, codes)
    ]

    anchor_rewards = [float(item["behavior_anchor_reward"]) for item in adjusted]
    assert anchor_rewards[0] > anchor_rewards[1] > anchor_rewards[2]
    assert all(0.0 <= value <= 1.0 for value in anchor_rewards)
    assert all(0.0 <= float(item["total_reward"]) <= 1.0 for item in adjusted)

    baseline_signal = reward_signal_stats(
        torch.tensor([item["total_reward"] for item in baseline_rewards]),
        torch.tensor([0.0, 0.0, 0.0]),
        torch.tensor([1.0, 1.0, 1.0]),
        torch.tensor([0.6, 0.6, 0.6]),
        torch.tensor([0.2, 0.2, 0.2]),
    )["signal_std"]
    adjusted_signal = reward_signal_stats(
        torch.tensor([float(item["total_reward"]) for item in adjusted]),
        torch.tensor([0.0, 0.0, 0.0]),
        torch.tensor([1.0, 1.0, 1.0]),
        torch.tensor([0.6, 0.6, 0.6]),
        torch.tensor([0.2, 0.2, 0.2]),
    )["signal_std"]
    assert adjusted_signal > baseline_signal

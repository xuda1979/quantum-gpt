from __future__ import annotations

from training.grpo_utils import (
    TaskCurriculum,
    build_reward_breakdown,
    estimate_detail_budget,
    interface_match_score,
    summarize_python_interface,
)


def test_summarize_python_interface_extracts_signatures() -> None:
    code = """
class BellPair:
    pass

def phase_estimation(phase: float, n_bits: int) -> int:
    return 0
"""
    lines = summarize_python_interface(code)
    assert "class BellPair" in lines
    assert "phase_estimation(phase: float, n_bits: int) -> int" in lines


def test_interface_match_score_rewards_exact_match() -> None:
    required = [
        "phase_estimation(phase: float, n_bits: int) -> int",
        "phase_from_measurement(measurement: int, n_bits: int) -> float",
    ]
    candidate = list(required)
    assert interface_match_score(required, candidate) == 1.0


def test_build_reward_breakdown_adds_partial_verifier_credit() -> None:
    reward = build_reward_breakdown(
        code="def solve(x: int) -> int:\n    return x + 1\n",
        result={"passed": False, "details": ["case a failed"]},
        required_interface=["solve(x: int) -> int"],
        detail_budget=4,
        pass_weight=0.6,
        syntax_weight=0.1,
        interface_weight=0.15,
        verifier_weight=0.15,
    )
    assert reward["passed"] is False
    assert reward["syntax_reward"] == 1.0
    assert reward["interface_reward"] == 1.0
    assert reward["verifier_reward"] == 0.75
    assert 0.0 < float(reward["total_reward"]) < 1.0


def test_estimate_detail_budget_counts_test_markers() -> None:
    source = """
# Test one
failures.append("a")
details.append("b")
"""
    assert estimate_detail_budget(source, cap=8) == 3


def test_task_curriculum_prioritizes_harder_quantum_tasks() -> None:
    curriculum = TaskCurriculum(quantum_priority=1.5, uncertainty_bonus=0.2)
    curriculum.record("easy_quantum", 0.95)
    curriculum.record("easy_quantum", 0.95)
    hard_weight = curriculum.weight("hard_quantum", "quantum")
    easy_weight = curriculum.weight("easy_quantum", "quantum")
    software_weight = curriculum.weight("hard_software", "software")
    assert hard_weight > easy_weight
    assert hard_weight > software_weight

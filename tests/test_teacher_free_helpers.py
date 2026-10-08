"""Unit tests for the Teacher-Free FV-GSPO grpo_utils helpers.

Covers the three deliverables from the plan's code-change checklist
(Teacher-Free-FV-GSPO-Final-Plan-ZH.docx, table 30):
    * tiered_teacher_free_reward   (pass-dominant hierarchical reward, table 16)
    * cluster_adjusted_advantages  (structural-cluster down-weighting, table 22)
    * teacher_free_route           (task routing incl. self-repair, table 18)
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402

from training.grpo_utils import (  # noqa: E402
    cluster_adjusted_advantages,
    teacher_free_route,
    tiered_teacher_free_reward,
)


def _reward(**overrides):
    kw = dict(
        passed_flags=[True, True, False, False],
        syntax_scores=[1.0, 1.0, 1.0, 0.5],
        interface_scores=[1.0, 1.0, 1.0, 0.5],
        semantic_scores=[1.0, 0.8, 0.9, 0.1],
        import_scores=[1.0, 1.0, 1.0, 1.0],
    )
    kw.update(overrides)
    return kw


def test_tiered_reward_pass_dominant_invariant():
    r = tiered_teacher_free_reward(**_reward())
    # Passing candidates have reward >= 1.00.
    assert r[0] >= 1.0 and r[1] >= 1.0
    # Failing candidates are capped at 0.95.
    assert r[2] <= 0.95 and r[3] <= 0.95
    # The pass tier strictly dominates the fail tier.
    assert min(r[:2]) > max(r[2:])


def test_tiered_reward_passing_differentiates_efficiency_and_diversity():
    r = tiered_teacher_free_reward(
        passed_flags=[True, True],
        syntax_scores=[1.0, 1.0],
        interface_scores=[1.0, 1.0],
        semantic_scores=[1.0, 1.0],
        import_scores=[1.0, 1.0],
        efficiency_scores=[1.0, 0.0],
        diversity_scores=[1.0, 0.0],
    )
    assert r[0] == 1.05
    assert r[1] == 1.00


def test_tiered_reward_uncalibrated_judge_zero_weight():
    # Judge is uncalibrated by default -> judge scores ignored (weight 0), and
    # the semantic weight is bumped to 0.70 so failed groups still learn.
    r1 = tiered_teacher_free_reward(**_reward(), judge_scores=[0.0, 0.0, 0.0, 0.0])
    r2 = tiered_teacher_free_reward(**_reward(), judge_scores=[0.0, 0.0, 1.0, 1.0])
    assert r1[2] == r2[2]  # judge has no effect while uncalibrated


def test_tiered_reward_all_fail_keeps_partial_progress_signal():
    r = tiered_teacher_free_reward(
        passed_flags=[False, False],
        syntax_scores=[0.9, 0.5],
        interface_scores=[0.9, 0.5],
        semantic_scores=[0.9, 0.1],
        import_scores=[1.0, 1.0],
    )
    # A candidate with high semantic progress gets a higher (but still <=0.95)
    # reward than one with no progress.
    assert r[0] > r[1]
    assert r[1] >= 0.0 and r[0] <= 0.95


def test_cluster_adjusted_penalizes_duplicate_clusters():
    adv = cluster_adjusted_advantages([3.0, 1.0, 0.0], ["c1", "c1", "c2"])
    # Two candidates share c1: each advantage is halved.
    assert adv[0] == pytest.approx(1.5)
    assert adv[1] == pytest.approx(0.5)
    # Unique cluster keeps its advantage untouched.
    assert adv[2] == pytest.approx(0.0)


def test_cluster_adjusted_preserves_ratio_within_cluster():
    adv = cluster_adjusted_advantages([1.0, 0.5, -1.0, 0.0], ["a", "a", "b", "b"])
    assert adv[0] == pytest.approx(0.5)
    assert adv[1] == pytest.approx(0.25)


def test_cluster_adjusted_requires_alignment():
    with pytest.raises(ValueError):
        cluster_adjusted_advantages([1.0, 2.0], ["a"])


def test_route_frontier_when_some_pass():
    assert (
        teacher_free_route(pass_count=3, group_size=8, reward_range=0.2, max_semantic_progress=0.5)
        == "frontier_rl"
    )


def test_route_partial_repair_when_progress_without_pass():
    # No candidate passes but geometric reward range is wide enough.
    assert (
        teacher_free_route(pass_count=0, group_size=8, reward_range=0.3, max_semantic_progress=0.0)
        == "partial_repair_rl"
    )
    # Or semantic progress is high enough even with a narrow reward range.
    assert (
        teacher_free_route(pass_count=0, group_size=8, reward_range=0.05, max_semantic_progress=0.5)
        == "partial_repair_rl"
    )


def test_route_self_repair_when_no_progress():
    assert (
        teacher_free_route(pass_count=0, group_size=8, reward_range=0.05, max_semantic_progress=0.1)
        == "self_repair"
    )


def test_route_mastered_replay_after_two_consecutive():
    assert (
        teacher_free_route(
            pass_count=8,
            group_size=8,
            reward_range=0.0,
            max_semantic_progress=1.0,
            consecutive_mastered=2,
        )
        == "mastered_replay"
    )


def test_route_quarantine_when_unstable():
    assert (
        teacher_free_route(
            pass_count=0,
            group_size=8,
            reward_range=0.0,
            max_semantic_progress=0.0,
            unstable=True,
        )
        == "quarantine"
    )

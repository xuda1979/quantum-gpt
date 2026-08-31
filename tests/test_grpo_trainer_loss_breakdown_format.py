"""TDD (coverage lane, PASS 16): format_compact_loss_breakdown — the
grep-able per-step train-log line (2026-08-26 r18 "the training log must
carry ALL information").

Before this suite the function had 1/120 statements covered (0.8%) — only an
import-trace. These tests pin the exact render contract: the field order,
the NA placeholders for missing fields (legacy/resume records stay
printable), the per-candidate arrays (rewards/advantages/every reward
component/SAPO terms/tokens), the judge dimension block, the entropy-floor
and trust-region blocks, and the zero-change alarm.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.grpo_trainer import format_compact_loss_breakdown  # noqa: E402


def _full_record() -> dict:
    """One honest instrumented step (2 candidates) with every optional block."""
    return {
        "step": 7,
        "skipped": False,
        "route": "frontier_rl",
        "loss": -0.5340091,
        "loss_breakdown": {
            "loss_recomputed": -0.5340091,
            "entropy_floor": 1.5,
            "entropy_train_mean": 0.42,
            "entropy_floor_penalty": 0.001,
            "entropy_floor_weight": 0.5,
        },
        "per_candidate_losses": [
            {"index": 0, "n_tokens": 29, "weight": 0.5, "loss": -0.5340091},
            {"index": 1, "n_tokens": 31, "weight": 0.5, "loss": None},
        ],
        "rollout_rewards": [
            {
                "index": 0,
                "total_reward": 0.4,
                "pass": True,
                "shaped_reward": 0.4,
                "syntax_reward": 1.0,
                "interface_reward": 1.0,
                "verifier_reward": 0.8,
                "import_hygiene_reward": 1.0,
                "judge_reward": 0.0,
                "judge_dim_scores": {"clarity": 0.6, "correctness": 0.8},
                "advantage": 0.2666667,
                "mean_other": 0.2666667,
                "adv_scale": 0.5,
                "loo_raw": 0.1333333,
                "ratio_mean": 1.02,
                "sapo_gate_mean": 2.0,
                "seq_kl": 3.1e-5,
                "clip_total_fraction": 0.0,
                "stop_reason": "eos",
                "n_tokens": 29,
            },
            {
                "index": 1,
                "total_reward": 0.0,
                "pass": False,
                "shaped_reward": 0.0,
                "syntax_reward": 1.0,
                "interface_reward": 0.0,
                "verifier_reward": None,
                "import_hygiene_reward": 1.0,
                "judge_reward": None,
                "judge_dim_scores": {"correctness": 0.2},
                "advantage": -0.8,
                "mean_other": 0.2666667,
                "adv_scale": 0.5,
                "loo_raw": -0.4,
                "ratio_mean": 0.9,
                "sapo_gate_mean": 1.5,
                "seq_kl": 1.2e-4,
                "clip_total_fraction": 0.1,
                "stop_reason": "fence",
                "n_tokens": 31,
            },
        ],
        "seq_kl_after": 4.2e-5,
        "ratio_after_update": 0.995,
        "clip_fraction_after_update": 0.02,
        "trust_region_violation_count": 1,
        "lr": 1.5e-5,
        "zero_change_alarm": False,
    }


def test_breakdown_line_prefix_and_step() -> None:
    line = format_compact_loss_breakdown(_full_record())
    assert line.startswith("loss_breakdown=step:7")
    assert "skipped:0" in line
    assert "route:frontier_rl" in line
    assert "loss:-0.534009" in line  # .6g
    assert "recomputed:-0.534009" in line


def test_breakdown_per_candidate_and_token_arrays() -> None:
    line = format_compact_loss_breakdown(_full_record())
    # per-candidate losses with NA placeholder for the missing second loss
    assert "per_candidate:[-0.534,NA]" in line
    assert "n_tokens:[29,31]" in line


def test_breakdown_reward_components_per_candidate() -> None:
    line = format_compact_loss_breakdown(_full_record())
    assert "rewards:[0.4,0]" in line
    assert "advantages:[0.2667,-0.8]" in line
    assert "pass:[1,0]" in line
    assert "shaped:[0.4,0]" in line
    assert "syntax:[1,1]" in line
    assert "interface:[1,0]" in line
    # verifier None for candidate 1 -> NA placeholder
    assert "verifier:[0.8,NA]" in line
    assert "hygiene:[1,1]" in line
    assert "judge:[0,NA]" in line


def test_breakdown_judge_dimension_block() -> None:
    line = format_compact_loss_breakdown(_full_record())
    assert "judge_dims:{clarity:[0.6,NA] correctness:[0.8,0.2]}" in line


def test_breakdown_advantage_and_sapo_terms() -> None:
    line = format_compact_loss_breakdown(_full_record())
    assert "scale:0.5" in line
    assert "loo_raw:[0.1333,-0.4]" in line
    assert "sapo:{ratio:[1.02,0.9] gate:[2,1.5] kl:[3.1e-05,0.00012] clip:[0,0.1]}" in line


def test_breakdown_stops_and_tokens() -> None:
    line = format_compact_loss_breakdown(_full_record())
    assert "stops:[eos,fence]" in line
    assert "tokens:[29,31]" in line


def test_breakdown_entropy_floor_block() -> None:
    line = format_compact_loss_breakdown(_full_record())
    assert "entropy:{train:0.42 floor:1.5 pen:0.001 w:0.5}" in line


def test_breakdown_trust_region_block() -> None:
    line = format_compact_loss_breakdown(_full_record())
    assert (
        "tr:{violations:1 seq_kl_after:4.2e-05 ratio_after:0.995 "
        "clip_after:0.02 lr:1.5e-05}" in line
    )
    assert "zero_change_alarm:false" in line


def test_breakdown_legacy_minimal_record_stays_printable() -> None:
    """A legacy/resume record with only step must not crash and render NA."""
    line = format_compact_loss_breakdown({"step": 3})
    assert line == "loss_breakdown=step:3 skipped:0 loss:NA"


def test_breakdown_zero_change_alarm_truthy_rendering() -> None:
    record = _full_record()
    record["zero_change_alarm"] = True
    line = format_compact_loss_breakdown(record)
    assert "zero_change_alarm:true" in line


def test_breakdown_skipped_flag_rendering() -> None:
    record = _full_record()
    record["skipped"] = True
    line = format_compact_loss_breakdown(record)
    assert "skipped:1" in line


def test_breakdown_no_route_omits_route_field() -> None:
    record = _full_record()
    del record["route"]
    line = format_compact_loss_breakdown(record)
    assert "route:" not in line


def test_breakdown_sapo_block_omitted_when_terms_absent() -> None:
    record = _full_record()
    for entry in record["rollout_rewards"]:
        for key in ("ratio_mean", "sapo_gate_mean", "seq_kl", "clip_total_fraction"):
            entry.pop(key, None)
    line = format_compact_loss_breakdown(record)
    assert "sapo:" not in line

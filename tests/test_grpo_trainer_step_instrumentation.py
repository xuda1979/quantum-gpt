"""TDD (r18, 2026-08-26, QA lane #6): the step record + compact per-step log
line carry EVERY training term value, per candidate.

User directive: the training log must carry ALL information for easy
debugging. This suite pins, on a synthetic step:
  (1) all reward components individually (pass, shaped, syntax, interface,
      verifier, import_hygiene, judge dims + judge composite) per candidate;
  (2) all advantage terms (raw rewards, mean_other, MAD scale, raw + final
      LOO advantage) per candidate;
  (3) SAPO terms (ratio_mean, gate_mean, seq_kl, clip_fraction) merged into
      the per-candidate records at emit time;
  (4) entropy terms (train entropy mean, floor, penalty value, weight);
  (5) trust-region terms (seq_kl_after, ratio_after_update, LR scale state);
  (6) stop-reason + token counts per candidate.

The jsonl stays parseable line-by-line and the compact log line stays a
single grep-able ``loss_breakdown=...`` line.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training import grpo_trainer  # noqa: E402
from training.grpo_utils import (  # noqa: E402
    append_grpo_metric_jsonl,
    build_grpo_step_record,
)

# ── synthetic step fixtures ────────────────────────────────────────────────


def _synthetic_evaluations() -> list[dict[str, object]]:
    """Four candidates exercising every reward component + judge dims."""
    return [
        {
            "total_reward": 0.4,
            "shaped_reward": 0.4,
            "pass_reward": 0.0,
            "syntax_reward": 0.8,
            "interface_reward": 0.6,
            "verifier_reward": 0.4,
            "brevity_reward": 0.5,
            "import_hygiene_reward": 0.9,
            "model_dim_scores": {
                "correctness": 0.6,
                "runnability": 0.7,
                "result_correctness": 0.5,
                "efficiency": 0.4,
                "quality": 0.8,
            },
            "judge_reward": 0.62,
        },
        {
            "total_reward": 0.3,
            "shaped_reward": 0.3,
            "pass_reward": 0.0,
            "syntax_reward": 0.7,
            "interface_reward": 0.5,
            "verifier_reward": 0.3,
            "brevity_reward": 0.4,
            "import_hygiene_reward": 0.8,
            "model_dim_scores": {
                "correctness": 0.5,
                "runnability": 0.6,
                "result_correctness": 0.4,
                "efficiency": 0.3,
                "quality": 0.7,
            },
            "judge_reward": 0.52,
        },
        {
            "total_reward": 0.0,
            "shaped_reward": 0.0,
            "pass_reward": 0.0,
            "syntax_reward": 0.2,
            "interface_reward": 0.1,
            "verifier_reward": 0.0,
            "brevity_reward": 0.1,
            "import_hygiene_reward": 0.3,
        },
        {
            "total_reward": 0.5,
            "shaped_reward": 0.5,
            "pass_reward": 1.0,
            "syntax_reward": 1.0,
            "interface_reward": 0.9,
            "verifier_reward": 0.5,
            "brevity_reward": 0.6,
            "import_hygiene_reward": 1.0,
            "model_dim_scores": {
                "correctness": 0.9,
                "runnability": 0.8,
                "result_correctness": 0.7,
                "efficiency": 0.6,
                "quality": 0.95,
            },
            "judge_reward": 0.82,
        },
    ]


def _synthetic_diagnostics() -> dict[str, object]:
    """Generation diagnostics with all four stop-reason classes + zero-token."""
    return {
        "completion_token_lengths": [512, 300, 2048, 2048, 0, 128],
        "eos_terminated": [True, False, False, False, False, False],
        "fence_terminated": [False, True, False, False, False, False],
        "truncated": [False, False, True, True, False, False],
        "cap_run_with_fence_opener": [False, False, False, True, False, False],
        "raw_response_chars": [2000, 900, 6000, 6000, 0, 400],
        "extracted_code_chars": [1500, 700, 5000, 5000, 0, 300],
    }


def _synthetic_per_candidate_losses() -> list[dict[str, object]]:
    return [
        {
            "index": 0,
            "n_tokens": 512,
            "weight": 0.25,
            "loss": 0.11,
            "advantage": 0.05,
            "sapo_gate_mean": 2.0,
            "seq_kl": 0.001,
            "ratio_mean": 1.02,
            "clip_total_fraction": 0.1,
        },
        {
            "index": 1,
            "n_tokens": 480,
            "weight": 0.25,
            "loss": 0.09,
            "advantage": -0.02,
            "sapo_gate_mean": 1.905,
            "seq_kl": 0.002,
            "ratio_mean": 0.98,
            "clip_total_fraction": 0.05,
        },
        {
            "index": 2,
            "n_tokens": 0,
            "weight": None,
            "loss": None,
            "advantage": -0.1,
            "excluded_reason": "zero_token_completion",
        },
        {
            "index": 3,
            "n_tokens": 301,
            "weight": 0.25,
            "loss": 0.14,
            "advantage": 0.1,
            "sapo_gate_mean": 2.003,
            "seq_kl": 0.0005,
            "ratio_mean": 1.1,
            "clip_total_fraction": 0.2,
        },
    ]


def _step_ctx(**overrides: object) -> dict[str, object]:
    evaluations = _synthetic_evaluations()
    stop_reasons = grpo_trainer.per_candidate_stop_reasons(
        {
            "completion_token_lengths": [512, 480, 0, 301],
            "eos_terminated": [True, False, False, False],
            "fence_terminated": [False, True, False, False],
            "truncated": [False, False, False, False],
            "cap_run_with_fence_opener": [False, False, False, False],
        }
    )
    advantages = torch.tensor([0.05, -0.02, -0.1, 0.1])
    rollout = grpo_trainer.build_rollout_rewards(
        evaluations,
        advantages,
        completion_token_lengths=[512, 480, 0, 301],
        adv_scale=0.31,
        stop_reasons=stop_reasons,
    )
    ctx: dict[str, object] = {
        "step": 1,
        "task_name": "quantum_qaoa_maxcut",
        "domain": "quantum",
        "mean_reward": 0.3,
        "signal_stats": {"reward_std": 0.12, "signal_std": 0.12},
        "task_prob": 0.5,
        "task_state": {"ema_reward": 0.3, "seen": 1.0},
        "rollout_rewards": rollout,
        "loss_reduction": (
            "per-candidate token-mean SAPO losses, equal per-candidate weights "
            "w_i = 1/G (length-neutral; NOT n_i/N token weighting), gradients "
            "accumulated via per-candidate backward"
        ),
        "generation_tokens": 1293,
        "entropy_mean": 0.87,
        "group_size": 4,
        "greedy_count": 1,
        "advantage_scale": 0.31,
    }
    ctx.update(overrides)
    return ctx


# ── (6) stop-reason derivation ─────────────────────────────────────────────


def test_per_candidate_stop_reasons_derivation() -> None:
    """The six stop-reason classes derive exactly from the diagnostics arrays:
    eos, fence, truncated, cap_run_fence_opener, empty (zero tokens), unknown."""
    diagnostics = _synthetic_diagnostics()
    assert grpo_trainer.per_candidate_stop_reasons(diagnostics) == [
        "eos",
        "fence",
        "truncated",
        "cap_run_fence_opener",
        "empty",
        "unknown",
    ]
    # A cap-run with a fence opener is its own class, never masked as plain
    # truncated (precedence: eos > fence > cap_run_fence_opener > truncated).
    assert grpo_trainer.per_candidate_stop_reasons(
        {
            "completion_token_lengths": [2048],
            "eos_terminated": [False],
            "fence_terminated": [False],
            "truncated": [True],
            "cap_run_with_fence_opener": [True],
        }
    ) == ["cap_run_fence_opener"]


# ── (1)+(2) per-candidate reward components + advantage terms ──────────────


def test_build_rollout_rewards_records_every_component_per_candidate() -> None:
    """Every reward component (pass, shaped, syntax, interface, verifier,
    import_hygiene, judge dims + composite) is recorded per candidate with
    the exact values the blend used."""
    stop_reasons = ["eos", "fence", "truncated", "cap_run_fence_opener"]
    records = grpo_trainer.build_rollout_rewards(
        _synthetic_evaluations(),
        torch.tensor([0.05, -0.02, -0.1, 0.1]),
        completion_token_lengths=[512, 480, 0, 301],
        adv_scale=0.31,
        stop_reasons=stop_reasons,
    )
    assert len(records) == 4
    first = records[0]
    assert first["pass"] is False
    assert first["shaped_reward"] == pytest.approx(0.4)
    assert first["syntax_reward"] == pytest.approx(0.8)
    assert first["interface_reward"] == pytest.approx(0.6)
    assert first["verifier_reward"] == pytest.approx(0.4)
    assert first["brevity_reward"] == pytest.approx(0.5)
    assert first["import_hygiene_reward"] == pytest.approx(0.9)
    assert first["judge_reward"] == pytest.approx(0.62)
    # judge dims: the exact per-dimension scores, keyed like the step-level
    # model_dim_scores contract.
    assert first["judge_dim_scores"] == {
        "correctness": 0.6,
        "runnability": 0.7,
        "result_correctness": 0.5,
        "efficiency": 0.4,
        "quality": 0.8,
    }
    # Candidate without judge scores: dims absent (None-tolerant emit).
    assert records[2].get("judge_dim_scores") is None
    assert records[2].get("judge_reward") is None
    # Candidate 3: passing.
    assert records[3]["pass"] is True
    assert records[3]["judge_reward"] == pytest.approx(0.82)
    assert records[3]["judge_dim_scores"]["quality"] == pytest.approx(0.95)


def test_build_rollout_rewards_advantage_terms() -> None:
    """Per candidate: raw reward (total_reward), mean_other = (Σr − rᵢ)/(G−1),
    loo_raw = rᵢ − mean_other, the MAD scale used, and the final advantage
    (post-scale, post-clamp) actually applied."""
    evaluations = _synthetic_evaluations()
    group_total = sum(float(e["total_reward"]) for e in evaluations)  # 1.2
    final_advantages = torch.tensor([0.15, -0.06, -0.35, 0.26])  # /0.31 then clamp
    records = grpo_trainer.build_rollout_rewards(
        evaluations,
        final_advantages,
        completion_token_lengths=[512, 480, 0, 301],
        adv_scale=0.31,
        stop_reasons=["eos", "fence", "truncated", "empty"],
    )
    raw = [float(records[i]["total_reward"]) for i in range(4)]
    assert raw == pytest.approx([0.4, 0.3, 0.0, 0.5])
    expected_other = [(group_total - value) / 3.0 for value in raw]
    assert [float(records[i]["mean_other"]) for i in range(4)] == pytest.approx(expected_other)
    assert [float(records[i]["loo_raw"]) for i in range(4)] == pytest.approx(
        [value - other for value, other in zip(raw, expected_other, strict=False)]
    )
    # mean_other(0) = (1.2 - 0.4)/3 = 0.2667; loo_raw(0) = 0.4 - 0.2667 = 0.1333;
    # loo_raw/0.31 = 0.43 -> clamped by the trainer to 0.15 in this fixture.
    assert records[0]["mean_other"] == pytest.approx(0.8 / 3, abs=1e-9)
    assert records[0]["loo_raw"] == pytest.approx(0.4 - 0.8 / 3, abs=1e-9)
    assert records[0]["adv_scale"] == pytest.approx(0.31)
    # final advantage is recorded exactly as the trainer passed it
    assert [float(records[i]["advantage"]) for i in range(4)] == pytest.approx(
        [0.15, -0.06, -0.35, 0.26]
    )


def test_build_rollout_rewards_single_candidate_mean_other_zero() -> None:
    """G=1 groups have no 'other' — mean_other = 0 and loo_raw = 0, mirroring
    leave_one_out_advantages' numel<=1 zero behavior (the ACTUAL pre-scale LOO
    is 0; the auditor's advantage == clamp(loo_raw/adv_scale) identity must
    hold for G=1 too). Never a div-by-zero."""
    records = grpo_trainer.build_rollout_rewards(
        [{"total_reward": 0.7, "shaped_reward": 0.7, "pass_reward": 1.0}],
        torch.tensor([0.0]),
        completion_token_lengths=[512],
        adv_scale=None,
        stop_reasons=["eos"],
    )
    assert records[0]["mean_other"] == 0.0
    assert records[0]["loo_raw"] == 0.0
    assert records[0]["adv_scale"] is None


def test_build_rollout_rewards_tolerates_partial_judge_dims() -> None:
    """Review finding (requesting-code-review, 2026-08-26): a judge response
    that parses SOME dims records None for the missing ones
    (_parse_model_dim_scores) — a live path with --model-judge-enabled. The
    per-candidate record must preserve those None dims, never crash the step
    with float(None)."""
    records = grpo_trainer.build_rollout_rewards(
        [
            {
                "total_reward": 0.4,
                "shaped_reward": 0.4,
                "pass_reward": 0.0,
                "model_dim_scores": {"correctness": 0.6, "runnability": None},
                "judge_reward": 0.6,
            }
        ],
        torch.tensor([0.05]),
        completion_token_lengths=[512],
    )
    assert records[0]["judge_dim_scores"]["correctness"] == pytest.approx(0.6)
    assert records[0]["judge_dim_scores"]["runnability"] is None


def test_build_rollout_rewards_stop_reason_and_tokens_per_candidate() -> None:
    """(6) stop-reason label + token count ride the per-candidate record,
    aligned 1:1 with candidate order."""
    records = grpo_trainer.build_rollout_rewards(
        _synthetic_evaluations(),
        torch.tensor([0.05, -0.02, -0.1, 0.1]),
        completion_token_lengths=[512, 480, 0, 301],
        adv_scale=None,
        stop_reasons=["eos", "fence", "truncated", "empty"],
    )
    assert [records[i]["stop_reason"] for i in range(4)] == [
        "eos",
        "fence",
        "truncated",
        "empty",
    ]
    assert [records[i]["n_tokens"] for i in range(4)] == [512, 480, 0, 301]
    # callers without the diagnostics keep a None-tolerant record
    legacy = grpo_trainer.build_rollout_rewards(
        [{"total_reward": 0.4, "shaped_reward": 0.4, "pass_reward": 0.0}],
        torch.tensor([0.05]),
        completion_token_lengths=[512],
    )
    assert legacy[0]["stop_reason"] is None


# ── (3) SAPO terms merged per candidate at emit time ───────────────────────


def test_emit_step_record_merges_sapo_terms_into_rollout_records(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """(3) ratio_mean, gate_mean, seq_kl, clip_fraction land in the aligned
    per-candidate rollout record; excluded zero-token candidates keep no
    terms; the values match the per_candidate_losses exactly (auditor can
    cross-check the identity from either array)."""
    metrics: list[dict[str, object]] = []
    path = tmp_path / "grpo_step_metrics.jsonl"
    # Train-pass truncation scenario: the loss-side n_tokens (300) diverges
    # from the completion count (512) BEFORE the emit runs — the merge must
    # NOT overwrite the rollout record's completion count.
    per_candidate = _synthetic_per_candidate_losses()
    per_candidate[0]["n_tokens"] = 300
    record = grpo_trainer.emit_step_record(
        rank=0,
        metrics=metrics,
        step_metrics_path=path,
        log_steps=5,
        ctx=_step_ctx(),
        skipped=False,
        loss=0.085,
        per_candidate_losses=per_candidate,
        loss_breakdown={
            "loss_mode": "sapo",
            "loss_recomputed": 0.085,
            "entropy_floor_penalty": 0.0012,
            "entropy_train_mean": 0.87,
            "entropy_floor": 1.5,
            "entropy_floor_weight": 0.01,
        },
    )
    assert record is not None
    rollout = record["rollout_rewards"]
    per_candidate_record = record["per_candidate_losses"]
    assert len(rollout) == 4
    merged = {int(entry["index"]): entry for entry in rollout}
    for candidate in per_candidate_record:
        entry = merged[int(candidate["index"])]
        for key in ("ratio_mean", "sapo_gate_mean", "seq_kl", "clip_total_fraction"):
            if candidate.get(key) is None:
                assert key not in entry
            else:
                assert entry[key] == pytest.approx(candidate[key])
    assert merged[0]["sapo_gate_mean"] == pytest.approx(2.0)
    assert merged[0]["ratio_mean"] == pytest.approx(1.02)
    assert merged[0]["seq_kl"] == pytest.approx(0.001)
    assert merged[0]["clip_total_fraction"] == pytest.approx(0.1)
    assert merged[3]["ratio_mean"] == pytest.approx(1.1)
    # the zero-token excluded candidate carries its own marker, not SAPO terms
    assert "sapo_gate_mean" not in merged[2]
    assert merged[2]["excluded_reason"] == "zero_token_completion"
    # contract pin: rollout n_tokens is the COMPLETION-token count (512) and
    # is NOT overwritten by the train-pass count (300) from the loss side.
    assert merged[0]["n_tokens"] == 512
    # jsonl row is the enriched record
    rows = [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    assert len(rows) == 1
    assert rows[0]["rollout_rewards"][0]["sapo_gate_mean"] == pytest.approx(2.0)
    assert rows[0]["rollout_rewards"][0]["stop_reason"] == "eos"


def test_emit_skipped_step_without_losses_keeps_rollout_terms_intact(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Skipped steps (no per_candidate_losses) must not drop or corrupt the
    per-candidate record fields; the compact line stays printable."""
    metrics: list[dict[str, object]] = []
    path = tmp_path / "grpo_step_metrics.jsonl"
    record = grpo_trainer.emit_step_record(
        rank=0,
        metrics=metrics,
        step_metrics_path=path,
        log_steps=5,
        ctx=_step_ctx(),
        skipped=True,
        reason="low_reward_signal",
    )
    assert record is not None
    rollout = record["rollout_rewards"]
    assert rollout[0]["stop_reason"] == "eos"
    assert rollout[0]["mean_other"] == pytest.approx(0.8 / 3, abs=1e-9)
    assert "sapo_gate_mean" not in rollout[0]
    out = capsys.readouterr().out
    compact = next(line for line in out.splitlines() if line.startswith("loss_breakdown="))
    assert "stops:[eos,fence,empty,unknown]" in compact


# ── (4)+(5) entropy + trust-region terms in the compact line ───────────────


def test_compact_line_carries_every_term_per_candidate(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The compact grep-able line reports, per candidate: pass/shaped/syntax/
    interface/verifier/hygiene/judge(+dims), rewards, mean_other, loo_raw,
    scale, final advantages, SAPO ratio/gate/kl/clip, stops, tokens — plus
    the step-level entropy and trust-region terms."""
    metrics: list[dict[str, object]] = []
    path = tmp_path / "grpo_step_metrics.jsonl"
    grpo_trainer.emit_step_record(
        rank=0,
        metrics=metrics,
        step_metrics_path=path,
        log_steps=5,
        ctx=_step_ctx(),
        skipped=False,
        loss=0.085,
        per_candidate_losses=_synthetic_per_candidate_losses(),
        loss_breakdown={
            "loss_mode": "sapo",
            "loss_recomputed": 0.085,
            "entropy_floor_penalty": 0.0012,
            "entropy_train_mean": 0.87,
            "entropy_floor": 1.5,
            "entropy_floor_weight": 0.01,
        },
        lora_b_max_delta=1e-4,
        zero_change_alarm=False,
        trust_region_violated=False,
        trust_region_violation_count=0,
        seq_kl_after=0.0003,
        ratio_after_update=1.02,
        clip_fraction_after_update=0.01,
        lr=2e-05,
    )
    out = capsys.readouterr().out
    compact = next(line for line in out.splitlines() if line.startswith("loss_breakdown="))
    assert "pass:[0,0,0,1]" in compact
    assert "shaped:[0.4,0.3,0,0.5]" in compact
    assert "syntax:[0.8,0.7,0.2,1]" in compact
    assert "interface:[0.6,0.5,0.1,0.9]" in compact
    assert "verifier:[0.4,0.3,0,0.5]" in compact
    assert "hygiene:[0.9,0.8,0.3,1]" in compact
    assert "judge:[0.62,0.52,NA,0.82]" in compact
    # judge dims: one array per dimension across candidates
    assert "judge_dims:{correctness:[0.6,0.5,NA,0.9]" in compact
    assert "quality:[0.8,0.7,NA,0.95]}" in compact
    assert "mean_other:[0.2667,0.3,0.4,0.2333]" in compact
    assert "scale:0.31" in compact
    assert "loo_raw:[0.1333,0,-0.4,0.2667]" in compact
    assert "advantages:[0.05,-0.02,-0.1,0.1]" in compact
    assert "sapo:{ratio:[1.02,0.98,NA,1.1]" in compact
    assert "gate:[2,1.905,NA,2.003]" in compact
    assert "kl:[0.001,0.002,NA,0.0005]" in compact
    assert "clip:[0.1,0.05,NA,0.2]}" in compact
    assert "stops:[eos,fence,empty,unknown]" in compact
    assert "tokens:[512,480,0,301]" in compact
    assert "entropy:{train:0.87 floor:1.5 pen:0.0012 w:0.01}" in compact
    assert (
        "tr:{violations:0 seq_kl_after:0.0003 ratio_after:1.02 clip_after:0.01 lr:2e-05}" in compact
    )
    assert "zero_change_alarm:false" in compact


# ── record contract / parseability ─────────────────────────────────────────


def test_step_record_jsonl_roundtrip_with_new_fields(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The enriched record stays jsonl-parseable line-by-line and every new
    field survives the round-trip with exact values."""
    path = tmp_path / "grpo_step_metrics.jsonl"
    record = grpo_trainer.emit_step_record(
        rank=0,
        metrics=[],
        step_metrics_path=path,
        log_steps=5,
        ctx=_step_ctx(),
        skipped=False,
        loss=0.085,
        per_candidate_losses=_synthetic_per_candidate_losses(),
        loss_breakdown={
            "loss_mode": "sapo",
            "loss_recomputed": 0.085,
            "entropy_floor_penalty": 0.0012,
            "entropy_train_mean": 0.87,
            "entropy_floor": 1.5,
            "entropy_floor_weight": 0.01,
        },
        trust_region_violated=False,
        trust_region_violation_count=0,
        seq_kl_after=0.0003,
        ratio_after_update=1.02,
        clip_fraction_after_update=0.01,
        lr=2e-05,
    )
    assert record is not None
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["step"] == 1
    first = parsed["rollout_rewards"][0]
    assert first["judge_dim_scores"]["correctness"] == pytest.approx(0.6)
    assert first["judge_reward"] == pytest.approx(0.62)
    assert first["mean_other"] == pytest.approx(0.8 / 3, abs=1e-9)
    assert first["adv_scale"] == pytest.approx(0.31)
    assert first["stop_reason"] == "eos"
    assert first["sapo_gate_mean"] == pytest.approx(2.0)
    assert first["ratio_mean"] == pytest.approx(1.02)
    assert first["seq_kl"] == pytest.approx(0.001)
    assert first["clip_total_fraction"] == pytest.approx(0.1)
    assert parsed["rollout_rewards"][3]["judge_dim_scores"]["quality"] == pytest.approx(0.95)
    assert parsed["loss_breakdown"]["entropy_floor"] == pytest.approx(1.5)
    assert parsed["seq_kl_after"] == pytest.approx(0.0003)
    assert parsed["lr"] == pytest.approx(2e-05)
    # the step-level aggregated record keeps its documented fields
    assert parsed["advantage_scale"] == pytest.approx(0.31)
    assert parsed["entropy_mean"] == pytest.approx(0.87)
    assert parsed["generation_tokens"] == 1293


def test_legacy_records_without_new_fields_stay_printable(tmp_path: Path) -> None:
    """Records built without the new kwargs (legacy/resume rows, skipped
    emits) must render NA, never crash the compact line or the jsonl emit."""
    record = build_grpo_step_record(
        step=2,
        task_name="quantum_ghz",
        domain="quantum",
        mean_reward=0.0,
        signal_stats={"reward_std": 0.0, "signal_std": 0.0},
        pass_rate=0.0,
        syntax_rate=0.0,
        interface_rate=0.0,
        verifier_rate=0.0,
        task_prob=0.25,
        task_state={"ema_reward": 0.0, "seen": 2.0},
        skipped=True,
        reason="repair_sft_queued",
        loss_reduction="batched GSPO sequence-level clipped surrogate",
        rollout_rewards=[
            {
                "index": 0,
                "total_reward": 0.4,
                "shaped_reward": 0.4,
                "pass": False,
                "pass_reward": 0.0,
                "advantage": 0.05,
                "n_tokens": 512,
            }
        ],
    )
    compact = grpo_trainer.format_compact_loss_breakdown(record)
    assert compact.startswith("loss_breakdown=step:2 skipped:1")
    assert "rewards:[0.4]" in compact
    assert "advantages:[0.05]" in compact
    append_grpo_metric_jsonl(tmp_path / "legacy.jsonl", record)
    lines = [
        line
        for line in (tmp_path / "legacy.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(lines) == 1
    assert json.loads(lines[0])["step"] == 2

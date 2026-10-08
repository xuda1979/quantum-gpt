"""Launch-simulator (lane #25) step-record verifier tests.

The launch simulator must verify, for EVERY completed smoke step, that the
instrumented step record is complete (all documented fields present) and that
the loss_breakdown identity holds (loss == loss_recomputed, pre-DR). This
module pins the pure verification logic in .sapo-loop/launchsim_verify.py.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY_PATH = ROOT / ".sapo-loop" / "launchsim_verify.py"


def _load_verify():
    spec = importlib.util.spec_from_file_location("launchsim_verify", str(VERIFY_PATH))
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {VERIFY_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verify_step_records = _load_verify().verify_step_records
verify_full_terms = _load_verify().verify_full_terms


def _good_record(step: int = 1) -> dict:
    return {
        "step": step,
        "task": "quantum_gate_alias_casefold_barrier",
        "loss": 0.123,
        "loss_reduction": "per-candidate token-mean SAPO losses",
        "per_candidate_losses": [
            {"index": 0, "n_tokens": 29, "weight": 0.5, "loss": 0.246, "advantage": 0.1}
        ],
        "rollout_rewards": [{"index": 0, "total_reward": 0.0, "pass": False}],
        "lora_b_max_delta": 1.0e-5,
        "zero_change_alarm": False,
        "loss_breakdown": {
            "loss_recomputed": 0.123,
            "loss_candidate_count": 1,
            "train_pass_seq_cap": 360,
            "train_pass_truncation_rate": 0.5,
        },
        "update_signal_magnitude": 0.01,
    }


def test_good_record_passes() -> None:
    assert verify_step_records([_good_record()]) == []


def test_empty_records_fail() -> None:
    problems = verify_step_records([])
    assert problems and any("no records" in p for p in problems)


def test_missing_loss_breakdown_field_flagged() -> None:
    record = _good_record()
    del record["loss_breakdown"]["train_pass_seq_cap"]
    problems = verify_step_records([record])
    assert any("train_pass_seq_cap" in p for p in problems)


def test_missing_top_level_field_flagged() -> None:
    record = _good_record()
    del record["rollout_rewards"]
    problems = verify_step_records([record])
    assert any("rollout_rewards" in p for p in problems)


def test_loss_identity_broken_flagged() -> None:
    record = _good_record()
    record["loss_breakdown"]["loss_recomputed"] = 0.999
    problems = verify_step_records([record])
    assert any("identity" in p for p in problems)


def test_loss_identity_with_engaged_entropy_floor_penalty() -> None:
    """r14 (run-10 double-backward fix): the entropy-floor penalty is a
    DETACHED monitoring value that still rides the final loss identity —
    loss == loss_recomputed + entropy_floor_penalty when engaged."""
    record = _good_record()
    record["loss"] = 0.127  # recomputed 0.123 + penalty 0.004
    record["loss_breakdown"]["loss_recomputed"] = 0.123
    record["loss_breakdown"]["entropy_floor_penalty"] = 0.004
    problems = verify_step_records([record])
    assert problems == []


def test_loss_identity_penalty_mismatch_flagged() -> None:
    record = _good_record()
    record["loss"] = 0.130  # recomputed 0.123 + penalty 0.004 = 0.127, not 0.130
    record["loss_breakdown"]["entropy_floor_penalty"] = 0.004
    problems = verify_step_records([record])
    assert any("identity" in p for p in problems)


def test_skipped_empty_mask_flagged() -> None:
    """A step skipped because the train-pass cap dropped every completion
    token (cap below prompt) is NOT a completed training step — the smoke
    must flag it, not silently pass."""
    record = _good_record()
    record.update({"skipped": True, "reason": "empty_completion_mask", "loss": None})
    problems = verify_step_records([record])
    assert any("empty_completion_mask" in p for p in problems)


def test_per_candidate_loss_entry_checked() -> None:
    record = _good_record()
    del record["per_candidate_losses"][0]["weight"]
    problems = verify_step_records([record])
    assert any("per-candidate" in p for p in problems)


# ── r18 full-terms wave (QA lane): every term per candidate in the record ──


def _full_terms_record() -> dict:
    record = _good_record()
    record["rollout_rewards"] = [
        {
            "index": 0,
            "total_reward": 0.5,
            "shaped_reward": 0.4,
            "pass": False,
            "pass_reward": 0.0,
            "advantage": 0.25,
            "n_tokens": 48,
            "syntax_reward": 0.8,
            "interface_reward": 0.6,
            "verifier_reward": 0.4,
            "brevity_reward": 0.5,
            "import_hygiene_reward": 0.9,
            "judge_reward": 0.62,
            "judge_dim_scores": {"correctness": 0.7, "efficiency": 0.5},
            "mean_other": 0.25,
            "loo_raw": 0.25,
            "adv_scale": 1.0,
            "stop_reason": "eos",
        }
    ]
    return record


def test_full_terms_complete_record_passes() -> None:
    problems = verify_full_terms([_full_terms_record()], judge_enabled=True)
    assert problems == []


def test_full_terms_missing_component_flagged() -> None:
    record = _full_terms_record()
    del record["rollout_rewards"][0]["syntax_reward"]
    problems = verify_full_terms([record], judge_enabled=True)
    assert any("syntax_reward" in p for p in problems)


def test_full_terms_missing_advantage_term_flagged() -> None:
    record = _full_terms_record()
    del record["rollout_rewards"][0]["mean_other"]
    problems = verify_full_terms([record], judge_enabled=True)
    assert any("mean_other" in p for p in problems)


def test_full_terms_missing_stop_reason_flagged() -> None:
    record = _full_terms_record()
    del record["rollout_rewards"][0]["stop_reason"]
    problems = verify_full_terms([record], judge_enabled=True)
    assert any("stop_reason" in p for p in problems)


def test_full_terms_judge_fields_required_when_enabled() -> None:
    record = _full_terms_record()
    del record["rollout_rewards"][0]["judge_dim_scores"]
    problems = verify_full_terms([record], judge_enabled=True)
    assert any("judge_dim_scores" in p for p in problems)


def test_full_terms_judge_fields_not_required_when_disabled() -> None:
    record = _full_terms_record()
    del record["rollout_rewards"][0]["judge_reward"]
    del record["rollout_rewards"][0]["judge_dim_scores"]
    problems = verify_full_terms([record], judge_enabled=False)
    assert problems == []

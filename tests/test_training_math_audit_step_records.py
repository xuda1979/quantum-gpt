"""Step-record math audit — independent recomputation of the NEW training-log
instrumentation fields (2026-08-25 training-math-auditor role).

Every expected value below is hand-derived from the published formulas
(arXiv:2511.20347, the documented loss-reduction contract, and the field
contract in reports/sapo-training-log-instrumentation-2026-08-25.md) — NOT
from the implementation under audit. The harness under test is
``scripts/sapo_math_audit_step_records.py`` (itself an independent
recomputation); the trainer's helpers are exercised only where noted.

Properties pinned:
  * aggregate identity: loss_recomputed == Σ w_i·loss_i (w_i = 1/G), and
    loss == loss_recomputed + DR terms when the DR flags fired;
  * per-candidate identity: loss_i == -A_i·gate_mean_i + kl·seq_kl_i with one
    kl per step (cross-candidate consistency) and physical gate bands;
  * rollout alignment: 1:1 candidate order, mean identities, LOO
    proportionality A_i = clamp((r_i - mean_other)/scale, ±clip);
  * zero-change gate: alarm ⟺ max|Δlora_B| == 0.0 exactly;
  * token-level SAPO reference math matches the trainer's sapo_loss_metrics;
  * legacy (run-3-era) records: loss identity + Cauchy bounds + RunningMAD
    EMA bounds + flat-group exact invariance.
"""

from __future__ import annotations

import json
import math

import pytest
import torch

from scripts.sapo_math_audit_step_records import (
    audit_jsonl,
    audit_legacy_step_record,
    audit_step_record_instrumented,
    gate_ratio_bound,
    gate_ratio_residual,
    recompute_aggregate_sapo_loss,
    sapo_gate,
    sapo_per_token_loss_reference,
)
from training.grpo_utils import sapo_loss_metrics

TAU_POS = 1.0
TAU_NEG = 1.05
KL = 0.01
CLIP = 2.5


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


# ---------------------------------------------------------------------------
# Fixture: one honest instrumented step (4 candidates, hand-computed math)
# ---------------------------------------------------------------------------

# Rewards and LOO advantages (scale 0.5, no clamping needed):
#   r = [0.4, 0.3, 0.0, 0.5]
#   l_0 = 0.4 - 0.2666667 = 0.1333333;  l_1 = 0.3 - 0.3 = 0.0
#   l_2 = 0.0 - 0.4 = -0.4;             l_3 = 0.5 - 0.2333333 = 0.2666667
#   A = l / 0.5 = [0.2666667, 0.0, -0.8, 0.5333333]
REWARDS = [0.4, 0.3, 0.0, 0.5]
ADVANTAGES = [2.0 / 7.5, 0.0, -0.8, 0.8 / 1.5]  # 0.2666...7, 0.0, -0.8, 0.5333...3
SCALE = 0.5

# Per-candidate token data and hand-derived stats.
# cand0 (A>0, tau=1.0): cur [0.01,-0.005], old [0,0]
#   r=[e^.01, e^-.005]; gate=[4σ(0.01005), 4σ(-0.00499)] -> mean 2.0025340
#   k3=[5.0167e-5, 1.25e-5] -> seq_kl 3.1333e-5
#   loss = -2.0025340*0.26666667 + 0.01*3.1333e-5 = -0.5340091 + 3.13e-7
CAND0 = dict(
    cur=[0.01, -0.005],
    old=[0.0, 0.0],
    gate_mean=(4.0 * _sigmoid(math.exp(0.01) - 1.0) + 4.0 * _sigmoid(math.exp(-0.005) - 1.0)) / 2.0,
    seq_kl=((math.expm1(0.01) - 0.01) + (math.expm1(-0.005) + 0.005)) / 2.0,
    ratio_mean=(math.exp(0.01) + math.exp(-0.005)) / 2.0,
)

# cand1 (A==0 -> tau_neg): cur [0,0], old [0,0] -> r=1, gate=(4/1.05)σ(0),
#   k3=0, loss=0.
CAND1 = dict(
    cur=[0.0, 0.0],
    old=[0.0, 0.0],
    gate_mean=(4.0 / TAU_NEG) * _sigmoid(0.0),
    seq_kl=0.0,
    ratio_mean=1.0,
)

# cand2 (A<0, tau=1.05): cur [-0.01, 0.005], old [0,0]
#   gate = (4/1.05)σ(1.05(e^z - 1)); mean = 1.9022896
#   k3 same as cand0 -> seq_kl 3.1333e-5
#   loss = -1.9022896*(-0.8) + 0.01*3.1333e-5 = 1.5218317
CAND2 = dict(
    cur=[-0.01, 0.005],
    old=[0.0, 0.0],
    gate_mean=(
        (4.0 / TAU_NEG) * _sigmoid(TAU_NEG * (math.exp(-0.01) - 1.0))
        + (4.0 / TAU_NEG) * _sigmoid(TAU_NEG * (math.exp(0.005) - 1.0))
    )
    / 2.0,
    seq_kl=((math.expm1(-0.01) + 0.01) + (math.expm1(0.005) - 0.005)) / 2.0,
    ratio_mean=(math.exp(-0.01) + math.exp(0.005)) / 2.0,
)

# cand3 (A>0, tau=1.0): cur [0.02, 0.0], old [0,0]
#   gate = [4σ(0.0202), 4σ(0)] -> mean 2.0100504
#   k3 = [2.0134e-4, 0] -> seq_kl 1.0067e-4
#   loss = -2.0100504*0.53333333 + 0.01*1.0067e-4 = -1.0720269
CAND3 = dict(
    cur=[0.02, 0.0],
    old=[0.0, 0.0],
    gate_mean=(4.0 * _sigmoid(math.exp(0.02) - 1.0) + 4.0 * _sigmoid(0.0)) / 2.0,
    seq_kl=((math.expm1(0.02) - 0.02) + 0.0) / 2.0,
    ratio_mean=(math.exp(0.02) + 1.0) / 2.0,
)


def _candidate_loss(cand: dict, advantage: float) -> float:
    return -(cand["gate_mean"] * advantage) + KL * cand["seq_kl"]


CAND_LOSSES = [
    _candidate_loss(CAND0, ADVANTAGES[0]),
    _candidate_loss(CAND1, ADVANTAGES[1]),
    _candidate_loss(CAND2, ADVANTAGES[2]),
    _candidate_loss(CAND3, ADVANTAGES[3]),
]
AGG_LOSS = 0.25 * sum(CAND_LOSSES)  # w = 1/G = 1/4


def _n_tokens(cand: dict) -> int:
    return len(cand["cur"])


def build_honest_record(step: int = 7) -> dict:
    """One internally consistent instrumented step record (per the contract)."""
    per_candidate_losses = [
        {
            "index": i,
            "n_tokens": _n_tokens(cand),
            "weight": 0.25,
            "loss": CAND_LOSSES[i],
            "advantage": ADVANTAGES[i],
            "sapo_gate_mean": cand["gate_mean"],
            "seq_kl": cand["seq_kl"],
            "ratio_mean": cand["ratio_mean"],
            "clip_total_fraction": 0.0,
        }
        for i, cand in enumerate([CAND0, CAND1, CAND2, CAND3])
    ]
    rollout_rewards = [
        {
            "index": i,
            "total_reward": REWARDS[i],
            "shaped_reward": REWARDS[i],
            "pass": i == 3,
            "pass_reward": 1.0 if i == 3 else 0.0,
            "advantage": ADVANTAGES[i],
            "n_tokens": _n_tokens([CAND0, CAND1, CAND2, CAND3][i]),
            "syntax_reward": 1.0,
            "verifier_reward": 0.75,
        }
        for i in range(4)
    ]
    return {
        "step": step,
        "skipped": False,
        "group_size": 4,
        "mean_reward": sum(REWARDS) / 4.0,
        "mean_shaped_reward": sum(REWARDS) / 4.0,
        "pass_rate": 0.25,
        "loo_advantage_rms": math.sqrt(sum(a * a for a in ADVANTAGES) / 4.0),
        "loo_advantage_mean_abs": sum(abs(a) for a in ADVANTAGES) / 4.0,
        "advantage_scale": SCALE,
        "update_signal_kind": "loo_advantage_rms",
        "update_signal_magnitude": math.sqrt(sum(a * a for a in ADVANTAGES) / 4.0),
        "loss": AGG_LOSS,
        "rollout_rewards": rollout_rewards,
        "per_candidate_losses": per_candidate_losses,
        "loss_breakdown": {
            "loss_mode": "sapo",
            "loss": AGG_LOSS,
            "loss_recomputed": AGG_LOSS,
            "candidate_count": 4,
            "loss_candidate_count": 4,
            "weighted_token_total": float(sum(_n_tokens(c) for c in [CAND0, CAND1, CAND2, CAND3])),
            "reduction": "per_candidate_1_over_g",
            "dr_pair_loss_added": False,
            "dr_variance_correction_added": False,
        },
        "loss_reduction": (
            "per-candidate token-mean SAPO losses (loss_i = -mean_t[g(r_t)*A_i] + "
            "kl_coeff*mean_t[k3], r_t = exp(cur-old), g = (4/tau)*sigmoid(tau*(r-1))), "
            "aggregated with equal per-candidate weights w_i = 1/G over the loss candidates"
        ),
        "lora_b_max_delta": 1.2e-4,
    }


def _findings(record: dict) -> list:
    return audit_step_record_instrumented(
        record, tau_pos=TAU_POS, tau_neg=TAU_NEG, advantage_clip=CLIP, kl_coeff=KL
    )


def _errors(record: dict) -> list:
    return [f for f in _findings(record) if f.severity == "ERROR"]


# ---------------------------------------------------------------------------
# 1. Aggregate identity (Σ w_i·loss_i == loss_recomputed == loss)
# ---------------------------------------------------------------------------


def test_recompute_aggregate_matches_hand_derived_sum() -> None:
    record = build_honest_record()
    recomputed = recompute_aggregate_sapo_loss(record["per_candidate_losses"])
    assert recomputed == pytest.approx(AGG_LOSS, abs=1e-9)


def test_aggregate_identity_holds_on_honest_record() -> None:
    assert _errors(build_honest_record()) == []


def test_aggregate_identity_detects_tampered_loss_recomputed() -> None:
    record = build_honest_record()
    record["loss_breakdown"]["loss_recomputed"] = AGG_LOSS + 0.01
    record["loss_breakdown"]["loss"] = AGG_LOSS + 0.01
    errs = _errors(record)
    assert any("loss_recomputed" in e.message for e in errs)


def test_aggregate_identity_detects_tampered_per_candidate_loss() -> None:
    record = build_honest_record()
    record["per_candidate_losses"][0]["loss"] = CAND_LOSSES[0] + 0.05
    errs = _errors(record)
    assert any("Σ w_i·loss_i" in e.message for e in errs)


def test_aggregate_identity_detects_wrong_weight_not_1_over_g() -> None:
    record = build_honest_record()
    record["per_candidate_losses"][0]["weight"] = 0.2
    errs = _errors(record)
    assert any("1/G" in e.message for e in errs)


def test_aggregate_identity_detects_candidate_count_mismatch() -> None:
    record = build_honest_record()
    record["loss_breakdown"]["candidate_count"] = 3
    errs = _errors(record)
    assert any("candidate_count" in e.message for e in errs)


def test_aggregate_token_total_and_zero_token_marking() -> None:
    record = build_honest_record()
    record["per_candidate_losses"].append(
        {
            "index": 4,
            "n_tokens": 0,
            "weight": None,
            "loss": None,
            "advantage": -0.1,
            "excluded_reason": "zero_token_completion",
        }
    )
    record["rollout_rewards"].append(
        {
            "index": 4,
            "total_reward": 0.0,
            "shaped_reward": 0.0,
            "pass": False,
            "pass_reward": 0.0,
            "advantage": -0.1,
            "n_tokens": 0,
        }
    )
    # Contract: G counts loss candidates only; the zero-token entry contributes 0.
    assert recompute_aggregate_sapo_loss(record["per_candidate_losses"]) == pytest.approx(
        AGG_LOSS, abs=1e-9
    )
    # A zero-token candidate carrying a loss is a contract violation.
    bad = build_honest_record()
    bad["per_candidate_losses"].append(
        {"index": 4, "n_tokens": 0, "weight": 0.25, "loss": 0.5, "advantage": -0.1}
    )
    assert any("zero-token candidate" in e.message for e in _errors(bad))


def test_final_loss_identity_with_dr_pair_term() -> None:
    # DR pair mined: loss = loss_recomputed + weight·dr_pair_loss_value.
    record = build_honest_record()
    record["loss_breakdown"]["dr_pair_loss_added"] = True
    record["dr_pair_loss_weight"] = 0.3
    record["dr_pair_loss_value"] = 0.02
    record["loss"] = AGG_LOSS + 0.3 * 0.02
    record["loss_breakdown"]["loss"] = record["loss"]
    assert _errors(record) == []
    # ... and fails when the logged final loss ignores the added term.
    record["loss"] = AGG_LOSS
    record["loss_breakdown"]["loss"] = AGG_LOSS
    errs = _errors(record)
    assert any("final_loss" in e.check for e in errs)


def test_final_loss_identity_detects_unexplained_drift() -> None:
    record = build_honest_record()
    record["loss"] = AGG_LOSS + 0.01
    record["loss_breakdown"]["loss"] = AGG_LOSS + 0.01
    errs = _errors(record)
    assert any("final_loss" in e.check for e in errs)


# ---------------------------------------------------------------------------
# 2. Per-candidate loss identity (loss_i = -A_i·gate_mean_i + kl·seq_kl_i)
# ---------------------------------------------------------------------------


def test_per_candidate_losses_match_hand_derived_formula() -> None:
    for i, cand in enumerate([CAND0, CAND1, CAND2, CAND3]):
        expected = -(cand["gate_mean"] * ADVANTAGES[i]) + KL * cand["seq_kl"]
        assert CAND_LOSSES[i] == pytest.approx(expected, abs=1e-9)


def test_kl_consistency_holds_when_all_candidates_share_one_kl() -> None:
    assert _errors(build_honest_record()) == []


def test_kl_inconsistency_detects_fabricated_loss() -> None:
    # A fabricated per-candidate loss (perturbed by an absolute amount well
    # above the fp32 noise floor) must be caught by the kl identity.
    record = build_honest_record()
    record["per_candidate_losses"][0]["loss"] = CAND_LOSSES[0] + 0.05
    errs = _errors(record)
    assert any("kl" in e.message.lower() for e in errs)


def test_fp32_noise_level_kl_spread_passes_live_record_1() -> None:
    """Golden regression: run-4 (sapo-27b-ai-20260825T070339) step-1
    per-candidate stats. The inferred kl values (0.00973 / 0.01002 / 0.01063)
    spread ~6% around the configured 0.01 purely from fp32 rounding of the
    recorded loss/A/gate/seq_kl (absolute residuals 1e-7..2.5e-7) — the
    noise-aware audit must PASS these, not flag them."""
    live_candidates = [
        # (loss, A, gate_mean, seq_kl, ratio_mean, n_tokens)
        (-1.5879948139190674, 0.7939974069595337, 2.0, 0.0, 1.0, 1306),
        (
            3.8111274242401123,
            -2.0,
            1.905561923980713,
            0.0003673649625852704,
            1.0008031129837036,
            1690,
        ),
        (
            -0.320882648229599,
            0.16029375791549683,
            2.001871109008789,
            0.00047866825480014086,
            1.0018752813339233,
            1690,
        ),
        (
            -2.0922088623046875,
            1.0457088947296143,
            2.000760555267334,
            0.0003993963182438165,
            1.0007612705230713,
            1690,
        ),
    ]
    agg = 0.25 * sum(c[0] for c in live_candidates)
    # Reconstruct per-candidate rewards consistent with the recorded
    # advantages under the recorded scale: A_i = (r_i - mean_other)/scale.
    # Solve r_i = l_i + (S - r_i)/3 -> r_i = (3·l_i + S)/4 with S = 4·mean_reward.
    scale = 0.3531379997730255
    loo_raw = [c[1] * scale for c in live_candidates]
    S = 4 * 0.5297070145606995
    rewards = [(3 * v + S) / 4 for v in loo_raw]
    record = {
        "step": 1,
        "skipped": False,
        "group_size": 4,
        "mean_reward": 0.5297070145606995,
        "pass_rate": 0.0,
        "mean_shaped_reward": 0.5772894620895386,
        "loo_advantage_rms": 1.198919653892517,
        "loo_advantage_mean_abs": 1.0,
        "advantage_scale": scale,
        "loss": agg,
        "rollout_rewards": [
            {
                "index": i,
                "total_reward": rewards[i],
                "shaped_reward": 0.5772894620895386,
                "pass": False,
                "pass_reward": 0.0,
                "advantage": c[1],
                "n_tokens": c[5],
            }
            for i, c in enumerate(live_candidates)
        ],
        "per_candidate_losses": [
            {
                "index": i,
                "n_tokens": c[5],
                "weight": 0.25,
                "loss": c[0],
                "advantage": c[1],
                "sapo_gate_mean": c[2],
                "seq_kl": c[3],
                "ratio_mean": c[4],
                "clip_total_fraction": 0.0,
            }
            for i, c in enumerate(live_candidates)
        ],
        "loss_breakdown": {
            "loss_mode": "sapo",
            "loss": agg,
            "loss_recomputed": agg,
            "candidate_count": 4,
            "loss_candidate_count": 4,
            "weighted_token_total": 6376.0,
            "reduction": "per_candidate_1_over_g",
            "dr_pair_loss_added": False,
            "dr_variance_correction_added": False,
        },
        "loss_reduction": "per-candidate token-mean SAPO losses ...",
        "lora_b_max_delta": 1e-4,
    }
    findings = audit_step_record_instrumented(
        record, tau_pos=TAU_POS, tau_neg=TAU_NEG, advantage_clip=CLIP, kl_coeff=0.01
    )
    errs = [f for f in findings if f.severity == "ERROR"]
    assert errs == [], [e.render() for e in errs]


def test_gate_mean_outside_physical_band_detected() -> None:
    record = build_honest_record()
    record["per_candidate_losses"][1]["sapo_gate_mean"] = 5.0
    errs = _errors(record)
    assert any("physical band" in e.message for e in errs)


def test_gate_ratio_recomputation_detects_fabricated_gate() -> None:
    # |gate_mean - g(ratio_mean)| must be <= sqrt(2·seq_kl) under the tau
    # selected by the recorded advantage sign. A gate that cannot be recomputed
    # from the logged ratio/KL stats is a defect.
    record = build_honest_record()
    record["per_candidate_losses"][0]["sapo_gate_mean"] = 2.5  # true value 2.002534
    errs = _errors(record)
    assert any("√(2·seq_kl)" in e.message for e in errs)


def test_gate_identity_holds_on_honest_fixtures() -> None:
    """Positive pin (2026-08-31 algorithm-vigilance): the SAPO gate identity
    |gate_mean - g(ratio_mean)| <= sqrt(2·seq_kl) must HOLD for every honest
    step-record fixture candidate, under the audit's tau-by-advantage-sign
    selection. The negative direction is pinned by
    test_gate_ratio_recomputation_detects_fabricated_gate."""
    record = build_honest_record()
    for entry in record["per_candidate_losses"]:
        tau = TAU_POS if entry["advantage"] > 0.0 else TAU_NEG
        residual = gate_ratio_residual(
            entry["sapo_gate_mean"], entry["ratio_mean"], entry["seq_kl"], tau
        )
        bound = gate_ratio_bound(entry["seq_kl"])
        assert residual <= bound, (
            f"candidate {entry['index']}: |gate_mean - g(ratio_mean)| = {residual:.6g} "
            f"> √(2·seq_kl) = {bound:.6g}"
        )
    # The hand-derived token stats (CAND0..CAND3) satisfy the identity with
    # margin: the residual (mean vs pointwise sigmoid nonlinearity + fp
    # rounding) is far below the bound; the bound is strictly positive for
    # every candidate with seq_kl > 0.
    assert (
        gate_ratio_residual(CAND0["gate_mean"], CAND0["ratio_mean"], CAND0["seq_kl"], TAU_POS)
        < 0.001
    )
    assert gate_ratio_bound(CAND0["seq_kl"]) > 0.0


def test_gate_identity_holds_on_fp32_live_record_fixture() -> None:
    """Positive pin on the run-4 fp32 noise fixture: real logged stats also
    satisfy |gate_mean - g(ratio_mean)| <= sqrt(2·seq_kl) under the audit's
    tau selection — fp32 rounding never violates the recomputation bound."""
    live_candidates = [
        (0.7939974069595337, 2.0, 0.0, 1.0),
        (-2.0, 1.905561923980713, 0.0003673649625852704, 1.0008031129837036),
        (0.16029375791549683, 2.001871109008789, 0.00047866825480014086, 1.0018752813339233),
        (1.0457088947296143, 2.000760555267334, 0.0003993963182438165, 1.0007612705230713),
    ]
    for adv, gate, sk, rm in live_candidates:
        tau = TAU_POS if adv > 0.0 else TAU_NEG
        assert gate_ratio_residual(gate, rm, sk, tau) <= gate_ratio_bound(
            sk
        ), f"A={adv}: |gate - g(r̄)| > √(2·seq_kl)"


def test_ratio_mean_band_detects_impossible_ratio() -> None:
    record = build_honest_record()
    record["per_candidate_losses"][0]["ratio_mean"] = 3.0
    errs = _errors(record)
    assert any("ratio_mean" in e.message for e in errs)


def test_zero_kl_candidate_loss_must_equal_minus_a_gate() -> None:
    # Candidate 1 has seq_kl == 0: loss_i must be exactly -A·gate.
    record = build_honest_record()
    assert CAND_LOSSES[1] == pytest.approx(0.0, abs=1e-12)
    record["per_candidate_losses"][1]["loss"] = 0.2
    errs = _errors(record)
    assert any("seq_kl≈0" in e.message for e in errs)


# ---------------------------------------------------------------------------
# 3. Rollout-reward alignment (1:1 order + mean identities + LOO)
# ---------------------------------------------------------------------------


def test_rollout_rewards_align_with_candidate_order() -> None:
    record = build_honest_record()
    assert [e["index"] for e in record["rollout_rewards"]] == [0, 1, 2, 3]
    assert _errors(record) == []


def test_rollout_reorder_detected() -> None:
    record = build_honest_record()
    rr = record["rollout_rewards"]
    rr[1], rr[3] = rr[3], rr[1]  # swap candidates 1 and 3 in place
    errs = _errors(record)
    assert any("1:1" in e.message for e in errs)


def test_mean_reward_identity_detects_fabricated_mean() -> None:
    record = build_honest_record()
    record["mean_reward"] = 0.9
    errs = _errors(record)
    assert any("mean(total_reward)" in e.message for e in errs)


def test_pass_rate_identity_and_pass_flag_consistency() -> None:
    record = build_honest_record()
    record["pass_rate"] = 0.75
    errs = _errors(record)
    assert any("pass_rate" in e.message for e in errs)
    # pass=false with pass_reward>0 is impossible under the documented builder.
    bad = build_honest_record()
    bad["rollout_rewards"][0]["pass"] = False
    bad["rollout_rewards"][0]["pass_reward"] = 1.0
    assert any("pass=false" in e.message for e in _errors(bad))


def test_loo_proportionality_holds_for_scale_0_5() -> None:
    record = build_honest_record()
    assert _errors(record) == []
    # Hand check: l = [0.1333333, 0.0, -0.4, 0.2666667]; A = l/0.5.
    loo = [0.4 - 0.8 / 3, 0.3 - 0.9 / 3, 0.0 - 1.2 / 3, 0.5 - 0.7 / 3]
    for v, a in zip(loo, ADVANTAGES):  # noqa: B905
        assert v / 0.5 == pytest.approx(a, abs=1e-9)


def test_loo_proportionality_detects_fabricated_advantage() -> None:
    record = build_honest_record()
    record["rollout_rewards"][0]["advantage"] = 0.31  # true value 0.2666667
    record["per_candidate_losses"][0]["advantage"] = 0.31
    errs = _errors(record)
    assert any("scale" in e.message or "proportional" in e.message for e in errs)


def test_loo_proportionality_with_clamped_advantages() -> None:
    # scale 1.0, l = [-3.0, 1.0, 0.5, 1.5] -> A = clamp([-3,1,0.5,1.5], ±2.5)
    #   = [-2.5, 1.0, 0.5, 1.5]  (candidate 0 clamped at the clip).
    record = build_honest_record()
    rewards = [1.0, 3.0, 2.0, 2.0]  # l = [1-7/3, 3-5/3, 2-2, 2-2] = [-1.3333, 1.3333, 0, 0]
    loo = [r - (sum(rewards) - r) / 3 for r in rewards]
    advs = [max(-CLIP, min(CLIP, v / 0.5)) for v in loo]
    rr = record["rollout_rewards"]
    for i, a in enumerate(advs):
        rr[i]["total_reward"] = rewards[i]
        rr[i]["shaped_reward"] = rewards[i]
        rr[i]["advantage"] = a
        rr[i]["pass"] = rewards[i] >= 2.5
        rr[i]["pass_reward"] = 1.0 if rewards[i] >= 2.5 else 0.0
    record["mean_reward"] = sum(rewards) / 4
    record["mean_shaped_reward"] = sum(rewards) / 4
    record["pass_rate"] = 0.25
    record["loo_advantage_rms"] = math.sqrt(sum(a * a for a in advs) / 4)
    record["loo_advantage_mean_abs"] = sum(abs(a) for a in advs) / 4
    assert _errors(record) == []


def test_rms_and_mean_abs_advantage_identities() -> None:
    record = build_honest_record()
    record["loo_advantage_rms"] = 9.9  # RMS(recorded advs) = 0.4989
    errs = _errors(record)
    assert any("RMS(advantages)" in e.message for e in errs)


# ---------------------------------------------------------------------------
# 4. Zero-change gate
# ---------------------------------------------------------------------------


def test_zero_change_gate_alarm_requires_exact_zero_delta() -> None:
    record = build_honest_record()
    record["lora_b_max_delta"] = 0.0
    record["zero_change_alarm"] = True
    record["zero_change_recommend_stop"] = True
    assert _errors(record) == []
    record["zero_change_alarm"] = True
    record["lora_b_max_delta"] = 1e-9  # alarm with non-zero delta is a lie
    errs = _errors(record)
    assert any("zero_change" in e.check for e in errs)


def test_zero_change_exact_zero_without_alarm_is_note() -> None:
    record = build_honest_record()
    record["lora_b_max_delta"] = 0.0
    notes = [f for f in _findings(record) if f.severity == "NOTE"]
    assert any("zero_change" in n.check for n in notes)


# ---------------------------------------------------------------------------
# 5. Token-level SAPO reference math vs the trainer implementation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cur,old,adv",
    [
        ([0.01, -0.005], [0.0, 0.0], 0.26666667),
        ([0.0, 0.0], [0.0, 0.0], 0.0),
        ([-0.01, 0.005], [0.0, 0.0], -0.8),
        ([0.02, 0.0], [0.0, 0.0], 0.53333333),
        ([10.0, -10.0], [0.0, 0.0], 1.0),  # clamp exercise
    ],
)
def test_token_level_sapo_recompute_matches_trainer(cur, old, adv) -> None:
    ref = sapo_per_token_loss_reference(
        cur, old, adv, tau_pos=TAU_POS, tau_neg=TAU_NEG, kl_coeff=KL, numerical_log_ratio_clip=8.0
    )
    loss, stats = sapo_loss_metrics(
        [torch.tensor(cur, dtype=torch.float32)],
        [torch.tensor(old, dtype=torch.float32)],
        torch.tensor([adv], dtype=torch.float32),
        tau_pos=TAU_POS,
        tau_neg=TAU_NEG,
        kl_coeff=KL,
        numerical_log_ratio_clip=8.0,
    )
    assert ref["loss"] == pytest.approx(loss.item(), abs=1e-5)
    assert ref["gate_mean"] == pytest.approx(stats["sapo_gate_mean"], abs=1e-5)
    # fp32 trainer vs fp64 reference: relative tolerance for large-magnitude k3.
    assert ref["seq_kl"] == pytest.approx(stats["seq_kl"], rel=1e-5)
    assert ref["n_tokens"] == pytest.approx(stats["n_tokens"], abs=1e-5)


def test_gate_hand_formula_agrees_with_sigmoid_form() -> None:
    assert sapo_gate(1.0, TAU_NEG) == pytest.approx((4.0 / TAU_NEG) * 0.5, abs=1e-12)
    assert sapo_gate(1.0, TAU_POS) == pytest.approx(2.0, abs=1e-12)


# ---------------------------------------------------------------------------
# 6. Legacy (run-3-era) records — existing-method recomputation
# ---------------------------------------------------------------------------

LEGACY_GATES = [CAND0["gate_mean"], CAND1["gate_mean"], CAND2["gate_mean"], CAND3["gate_mean"]]
LEGACY_SKS = [CAND0["seq_kl"], CAND1["seq_kl"], CAND2["seq_kl"], CAND3["seq_kl"]]


def _legacy_record(
    loss_value: float, rms: float, scale: float = 0.31, prev_scale: float = 0.30
) -> dict:
    return {
        "step": 36,
        "skipped": False,
        "loss": loss_value,
        "loo_advantage_rms": rms,
        "loo_advantage_mean_abs": 0.3 * rms,
        "advantage_scale": scale,
        "update_signal_kind": "loo_advantage_rms",
        "update_signal_magnitude": rms,
        "sapo_per_candidate_stats": [
            {"sapo_gate_mean": g, "seq_kl": sk, "ratio_mean": 1.0, "clip_total_fraction": 0.0}
            for g, sk in zip(LEGACY_GATES, LEGACY_SKS)  # noqa: B905
        ],
    }


def test_legacy_loss_identity_recomputes_from_stats() -> None:
    # m = mean(gate·A) = 0.0210573, loss = -m + kl·mean(seq_kl).
    mean_sk = sum(LEGACY_SKS) / 4
    m = 0.02105733
    loss = -m + KL * mean_sk
    rms = math.sqrt(sum(a * a for a in ADVANTAGES) / 4)  # 0.498888
    findings, _, _ = audit_legacy_step_record(_legacy_record(loss, rms), kl_coeff=KL)
    assert [f for f in findings if f.severity == "ERROR"] == []
    assert abs(loss - (-m + KL * mean_sk)) < 1e-12


def test_legacy_loss_identity_detects_fabricated_loss() -> None:
    rms = math.sqrt(sum(a * a for a in ADVANTAGES) / 4)  # 0.498888
    mean_gate = sum(LEGACY_GATES) / 4  # ~1.9545
    max_gate = max(LEGACY_GATES)  # ~2.0101
    # |m| past the audit-consistency bound mean(gate)·RMS -> NOTE (rigorous bound holds).
    loss_note = mean_gate * rms + 0.01
    findings, _, _ = audit_legacy_step_record(_legacy_record(loss_note, rms), kl_coeff=KL)
    assert [f for f in findings if f.severity == "ERROR"] == []
    assert any(f.severity == "NOTE" and "audit-consistency" in f.message for f in findings)
    # |m| past the RIGOROUS max(gate)·RMS bound -> ERROR.
    loss_error = max_gate * rms + 0.01
    findings, _, _ = audit_legacy_step_record(_legacy_record(loss_error, rms), kl_coeff=KL)
    assert any(f.severity == "ERROR" and "loss_identity" in f.check for f in findings)


def test_legacy_gate_physical_bands() -> None:
    record = _legacy_record(0.0, 0.5)
    record["sapo_per_candidate_stats"][2]["sapo_gate_mean"] = 6.0
    findings, _, _ = audit_legacy_step_record(record, kl_coeff=KL)
    assert any("gate_band" in f.check for f in findings)


def test_legacy_signal_magnitude_identity() -> None:
    record = _legacy_record(0.0, 0.5)
    record["update_signal_magnitude"] = 0.7
    findings, _, _ = audit_legacy_step_record(record, kl_coeff=KL)
    assert any("signal" in f.check for f in findings)


def test_legacy_first_non_flat_batch_initializes_scale_directly() -> None:
    """Run-3's step 3: the first non-flat batch after flat steps 1-2 sets the
    scale to the batch MAD directly (init bypasses the EMA — code-pinned in
    RunningMAD.update). scale 0.3667 from prev 1.0 must PASS."""
    rec = _legacy_record(0.0, rms=0.5, scale=0.3667, prev_scale=1.0)
    findings, _, initialized = audit_legacy_step_record(
        rec, kl_coeff=KL, prev_scale=1.0, mad_initialized=False
    )
    assert [f for f in findings if f.severity == "ERROR"] == []
    assert initialized is True
    # A first-batch scale outside the batch-MAD band is impossible.
    bad = _legacy_record(0.0, rms=0.5, scale=6.0, prev_scale=1.0)
    findings, _, _ = audit_legacy_step_record(
        bad, kl_coeff=KL, prev_scale=1.0, mad_initialized=False
    )
    assert any("batch-MAD band" in f.message for f in findings)


def test_legacy_flat_then_ema_chain_round_trips_run3() -> None:
    """Run-3's real chain: 1.0 (flat) -> 1.0 (flat) -> 0.3667 (first non-flat,
    direct init) -> 0.3634 (EMA) -> 0.3617 (EMA) ... all pass."""
    flat_loss = KL * sum(LEGACY_SKS) / 4  # flat group: loss == kl·mean(seq_kl) (m≈0)
    chain = [
        (1, 0.0, 1.0, flat_loss),
        (2, 5.96e-08, 1.0, flat_loss),
        (3, 0.5, 0.3667, 0.0),
        (4, 0.5, 0.3634, 0.0),
        (5, 0.5, 0.3617, 0.0),
    ]
    prev = None
    initialized = False
    for step, rms, scale, loss in chain:
        rec = _legacy_record(loss, rms=rms, scale=scale, prev_scale=prev if prev else 1.0)
        findings, prev, initialized = audit_legacy_step_record(
            rec, kl_coeff=KL, prev_scale=prev, mad_initialized=initialized
        )
        assert [f for f in findings if f.severity == "ERROR"] == [], f"step {step}: {findings}"
    # EMA bounds: 0.99·0.3667 = 0.36303 <= 0.3634 <= 0.36303 + 0.05 ✓


def test_legacy_mad_scale_ema_bounds() -> None:
    # scale_prev 0.30, decay 0.99, MAD already initialized: bounds [0.297, 0.347].
    ok = _legacy_record(0.0, 0.5, scale=0.31, prev_scale=0.30)
    findings, _, _ = audit_legacy_step_record(
        ok, kl_coeff=KL, prev_scale=0.30, mad_initialized=True
    )
    assert [f for f in findings if f.severity == "ERROR"] == []
    bad = _legacy_record(0.0, 0.5, scale=0.50, prev_scale=0.30)
    findings, _, _ = audit_legacy_step_record(
        bad, kl_coeff=KL, prev_scale=0.30, mad_initialized=True
    )
    assert any("mad_scale" in f.check for f in findings)


def test_legacy_flat_group_scale_exact_invariance() -> None:
    flat_loss = KL * sum(LEGACY_SKS) / 4
    record = _legacy_record(flat_loss, rms=0.0, scale=0.35, prev_scale=0.30)
    findings, _, _ = audit_legacy_step_record(record, kl_coeff=KL, prev_scale=0.30)
    assert any("flat group" in f.message for f in findings)


def test_legacy_rms_ge_mean_abs() -> None:
    record = _legacy_record(0.0, rms=0.2)
    record["loo_advantage_mean_abs"] = 0.3
    findings, _, _ = audit_legacy_step_record(record, kl_coeff=KL)
    assert any("mean|·|" in f.message for f in findings)


# ---------------------------------------------------------------------------
# 7. Skipped records + jsonl driver
# ---------------------------------------------------------------------------


def test_skipped_records_audit_clean() -> None:
    skipped = {
        "step": 2,
        "skipped": True,
        "reason": "repair_sft_queued",
        "route": "repair_sft",
        "loss_reduction": "per-candidate token-mean SAPO losses ... [skipped: no loss computed this step]",
        "rollout_rewards": [
            {
                "index": i,
                "total_reward": 0.0,
                "shaped_reward": 0.0,
                "pass": False,
                "pass_reward": 0.0,
                "advantage": 0.0,
                "n_tokens": 100 + i,
            }
            for i in range(4)
        ],
    }
    findings = audit_step_record_instrumented(
        skipped, tau_pos=TAU_POS, tau_neg=TAU_NEG, advantage_clip=CLIP
    )
    assert [f for f in findings if f.severity == "ERROR"] == []
    # A skipped record that somehow logged a loss must be flagged.
    bad = dict(skipped, loss_reduction="no marker here")
    assert any(
        f.severity == "ERROR"
        for f in audit_step_record_instrumented(
            bad, tau_pos=TAU_POS, tau_neg=TAU_NEG, advantage_clip=CLIP
        )
    )


def test_jsonl_driver_counts_errors_and_exit_codes(tmp_path) -> None:
    path = tmp_path / "steps.jsonl"
    with open(path, "w") as fh:
        for step in (1, 2, 3):
            rec = build_honest_record(step=step)
            if step == 2:
                rec["loss_breakdown"]["loss_recomputed"] += 0.1
            fh.write(json.dumps(rec) + "\n")
    findings, n_error, n_note = audit_jsonl(
        path,
        mode="instrumented",
        tau_pos=TAU_POS,
        tau_neg=TAU_NEG,
        kl_coeff=KL,
        advantage_clip=CLIP,
    )
    assert n_error >= 1
    assert n_error == sum(1 for f in findings if f.severity == "ERROR")


def test_report_sample_record_is_caught_as_inconsistent() -> None:
    """The illustrative sample in the instrumentation report (2026-08-25 §3)
    does NOT round-trip: Σ 0.3333·loss = 0.1133 != 0.085, and mean_reward
    0.3333 != (0.4+0.3+0+0.5)/4 = 0.3. The harness must flag it — the code
    contract (w=1/G over loss candidates) is the authority."""
    sample = {
        "step": 1,
        "skipped": False,
        "mean_reward": 0.3333,
        "group_size": 4,
        "rollout_rewards": [
            {
                "index": 0,
                "total_reward": 0.4,
                "shaped_reward": 0.4,
                "pass": False,
                "pass_reward": 0.0,
                "advantage": 0.05,
                "n_tokens": 512,
            },
            {
                "index": 1,
                "total_reward": 0.3,
                "shaped_reward": 0.3,
                "pass": False,
                "pass_reward": 0.0,
                "advantage": -0.02,
                "n_tokens": 480,
            },
            {
                "index": 2,
                "total_reward": 0.0,
                "shaped_reward": 0.0,
                "pass": False,
                "pass_reward": 0.0,
                "advantage": -0.1,
                "n_tokens": 0,
            },
            {
                "index": 3,
                "total_reward": 0.5,
                "shaped_reward": 0.5,
                "pass": True,
                "pass_reward": 1.0,
                "advantage": 0.1,
                "n_tokens": 301,
            },
        ],
        "per_candidate_losses": [
            {
                "index": 0,
                "n_tokens": 512,
                "weight": 0.3333,
                "loss": 0.11,
                "advantage": 0.05,
                "sapo_gate_mean": 2.0,
                "seq_kl": 1.1e-6,
                "ratio_mean": 1.0,
                "clip_total_fraction": 0.0,
            },
            {
                "index": 1,
                "n_tokens": 480,
                "weight": 0.3333,
                "loss": 0.09,
                "advantage": -0.02,
                "sapo_gate_mean": 1.905,
                "seq_kl": 1.0e-6,
                "ratio_mean": 1.0,
                "clip_total_fraction": 0.0,
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
                "weight": 0.3333,
                "loss": 0.14,
                "advantage": 0.1,
                "sapo_gate_mean": 2.003,
                "seq_kl": 1.2e-6,
                "ratio_mean": 1.0,
                "clip_total_fraction": 0.0,
            },
        ],
        "loss_breakdown": {
            "loss_mode": "sapo",
            "loss": 0.085,
            "loss_recomputed": 0.085,
            "candidate_count": 3,
            "loss_candidate_count": 3,
            "weighted_token_total": 1293.0,
            "reduction": "per_candidate_1_over_g",
            "dr_pair_loss_added": False,
            "dr_variance_correction_added": False,
        },
        "loss_reduction": "per-candidate token-mean SAPO losses ...",
        "lora_b_max_delta": 1.2e-4,
    }
    errs = _errors(sample)
    # The sample's own math is inconsistent with the documented w=1/G reduction.
    assert any("Σ w_i·loss_i" in e.message for e in errs)
    assert any("mean(total_reward)" in e.message for e in errs)

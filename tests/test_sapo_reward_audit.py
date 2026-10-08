"""TDD suite for scripts/sapo_reward_audit.py — the reward-path verifier.

The audit recomputes every candidate's reward from the recorded components
(and, when raw harness outputs are supplied, from the harness result) and
recomputes the LOO/shared-MAD advantage normalization, so a wrong-reward bug
cannot hide behind clean loss identities.

Contract under audit (run-4-R2 launch, configs/rl/qwen36_27b_fv_gspo_asi2.json
+ launch argv, verified 2026-08-25):
  - weights: pass/shaped 0.45, syntax 0.05, interface 0.10, verifier 0.10,
    brevity 0.0, import-hygiene 0.05  ->  renormalized total weight 0.75
  - reward-mode p_dominant (pass 0.40 / shaped 0.35 / judge 0.25), judge
    disabled ->  total = clamp01(P + (1-P) * progress_reward)
  - shaped = shaped_reward_from_details: 1.0 on pass; failing -> 0.0 (crash /
    no numeric evidence) or 0.5..0.9 (near-miss tiers); pass_reward binary
  - advantages: LOO (r_i - mean_other_i), scaled by shared running MAD
    (recorded as step advantage_scale), clamped to +-2.5
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import sapo_reward_audit as audit  # noqa: E402

WEIGHTS = audit.DEFAULT_WEIGHTS


def cand(**overrides):
    base = {
        "index": 0,
        "total_reward": 0.5,
        "shaped_reward": 0.6,
        "pass": False,
        "pass_reward": 0.0,
        "advantage": 0.0,
        "n_tokens": 100,
        "syntax_reward": 1.0,
        "verifier_reward": 0.5,
    }
    for key, value in overrides.items():
        base[key] = value
    return base


def loo_adv(rewards, scale, clip=2.5):
    """Production LOO + shared-MAD + clip advantage values."""
    s = sum(rewards)
    g = len(rewards)
    raw = [r - (s - r) / (g - 1) for r in rewards]
    return [max(-clip, min(clip, v / scale)) for v in raw]


def step_record(rewards, advantages, **overrides):
    """Composition-consistent synthetic step: failing candidates with a
    nonzero total use shaped 0.6 / syntax 1 / verifier 0.5 (feasible band
    [0.4933, 0.6933]); r == 0.0 candidates are hard fails (all components 0)."""
    g = len(rewards)
    rollout = []
    for i, r in enumerate(rewards):
        passed = r >= 1.0
        rollout.append(
            {
                "index": i,
                "total_reward": r,
                "shaped_reward": 1.0 if passed else (0.6 if r > 0.0 else 0.0),
                "pass": passed,
                "pass_reward": 1.0 if passed else 0.0,
                "advantage": advantages[i],
                "n_tokens": 100,
                "syntax_reward": 1.0 if r > 0.0 else 0.0,
                "verifier_reward": 1.0 if passed else (0.5 if r > 0.0 else 0.0),
            }
        )
    shaped_vals = [c["shaped_reward"] for c in rollout]
    mean_r = sum(rewards) / g
    record = {
        "step": 1,
        "task": "quantum_synth_task",
        "domain": "quantum",
        "group_size": g,
        "pass_rate": sum(1.0 for c in rollout if c["pass"]) / g,
        "mean_reward": mean_r,
        "mean_shaped_reward": sum(shaped_vals) / g,
        "reward_std": math.sqrt(sum((r - mean_r) ** 2 for r in rewards) / g),
        "advantage_scale": 0.53,
        "rollout_rewards": rollout,
    }
    record.update(overrides)
    return record


# ── pass-dominant composition ──────────────────────────────────────────────


def test_pass_candidate_total_is_exactly_one():
    """p_dominant with judge disabled: a full pass must yield total == 1.0."""
    c = cand(**{"pass": True}, pass_reward=1.0, shaped_reward=1.0, total_reward=1.0)
    checks = audit.audit_candidate(c, WEIGHTS)
    assert not [e for e in checks if not e["ok"]], checks


def test_near_miss_shaped_band_ok():
    """Failing candidate with near-miss shaped: total must sit in the band
    implied by the recorded components (interface/hygiene free in [0,1])."""
    c = cand(shaped_reward=0.9, verifier_reward=0.75, total_reward=0.8)
    checks = audit.audit_candidate(c, WEIGHTS)
    errors = [e for e in checks if not e["ok"]]
    assert not errors, errors
    # band is [0.7067, 0.9067] for these components
    lo, hi = audit.total_band(c, WEIGHTS)
    # total weight 0.80 since the 2026-08-27 brevity counterweight (0.05)
    assert lo == pytest.approx(0.53 / 0.80, abs=1e-9)
    assert hi == pytest.approx(0.68 / 0.80, abs=1e-9)


def test_shaped_contract_violation_mid_band_fails():
    """shaped_reward_from_details returns 0.0 or 0.5..0.9 for failures —
    0.3 is impossible and must be flagged."""
    c = cand(shaped_reward=0.3, total_reward=0.3)
    errors = [e for e in audit.audit_candidate(c, WEIGHTS) if not e["ok"]]
    assert any("shaped" in e["check"] for e in errors), errors


def test_pass_but_total_not_one_fails():
    """A passing candidate whose recorded total is not 1.0 is a composition
    bug: expected 1.0, recorded 0.95."""
    c = cand(**{"pass": True}, pass_reward=1.0, shaped_reward=1.0, total_reward=0.95)
    errors = [e for e in audit.audit_candidate(c, WEIGHTS) if not e["ok"]]
    assert any("total" in e["check"] for e in errors), errors
    failing = [e for e in errors if e["check"].startswith("total")][0]
    assert failing["expected"] == pytest.approx(1.0, abs=1e-9)
    assert failing["recorded"] == pytest.approx(0.95)


def test_fail_total_outside_band_fails():
    """All executable components zero (interface+hygiene free) caps a failing
    total at 0.15/0.75 = 0.2; a recorded 0.6 is impossible."""
    c = cand(
        shaped_reward=0.0,
        syntax_reward=0.0,
        verifier_reward=0.0,
        total_reward=0.6,
    )
    errors = [e for e in audit.audit_candidate(c, WEIGHTS) if not e["ok"]]
    assert any("band" in e["check"] for e in errors), errors


def test_pass_flag_pass_reward_mismatch_fails():
    """pass=true with pass_reward=0.0 cannot happen under build_reward_breakdown."""
    c = cand(**{"pass": True}, pass_reward=0.0, shaped_reward=1.0)
    errors = [e for e in audit.audit_candidate(c, WEIGHTS) if not e["ok"]]
    assert any("pass" in e["check"] for e in errors), errors


def test_syntax_reward_must_be_binary():
    c = cand(syntax_reward=0.37)
    errors = [e for e in audit.audit_candidate(c, WEIGHTS) if not e["ok"]]
    assert any("syntax" in e["check"] for e in errors), errors


def test_composition_crosscheck_against_production_blend():
    """The audit's recomputed total must equal the production
    compose_policy_training_reward/blend_comprehensive_reward math."""
    from training.grpo_utils import blend_comprehensive_reward

    shaped, syntax, interface, verifier, hygiene = 0.8, 1.0, 0.5, 0.7, 0.9
    progress = audit.progress_reward(shaped, syntax, interface, verifier, 0.0, hygiene, WEIGHTS)
    total = audit.compose_total(0.0, shaped, syntax, interface, verifier, 0.0, hygiene, WEIGHTS)
    prod = blend_comprehensive_reward(
        pass_reward=0.0,
        shaped_reward=progress,
        model_dim_scores={},
        dim_weights={},
        mode="p_dominant",
        pass_mass=0.50,
        shaped_mass=0.40,
        judge_mass=0.10,
    )
    assert total == pytest.approx(prod, abs=1e-12)
    # total weight 0.80 with the brevity counterweight (brevity 0 here)
    assert total == pytest.approx(0.575 / 0.80, abs=1e-9)


# ── advantage normalization (LOO + shared MAD) ─────────────────────────────


def test_advantage_recomputation_matches():
    """LOO advantages recomputed from recorded rewards + recorded
    advantage_scale (shared MAD) + clamp +-2.5 must equal recorded."""
    rewards = [1.0, 0.6406, 0.0, 0.6]
    s = sum(rewards)
    mean_others = [(s - r) / 3.0 for r in rewards]
    raw_loo = [r - m for r, m in zip(rewards, mean_others, strict=False)]
    scale = 0.53
    expected = loo_adv(rewards, scale)
    record = step_record(rewards, expected)
    result = audit.audit_step(record, WEIGHTS)
    assert result["ok"], result
    assert result["mean_other"] == pytest.approx(mean_others, abs=1e-12)
    assert result["raw_loo"] == pytest.approx(raw_loo, abs=1e-12)
    assert result["scale"] == pytest.approx(0.53)


def test_advantage_mismatch_fails():
    rewards = [1.0, 0.6406, 0.0, 0.6]
    record = step_record(rewards, loo_adv(rewards, 0.53))
    record["rollout_rewards"][2]["advantage"] = 1.2345  # tamper
    result = audit.audit_step(record, WEIGHTS)
    assert not result["ok"]
    assert any("advantage" in e["check"] for e in result["errors"]), result["errors"]


def test_group_stats_consistency():
    rewards = [1.0, 0.6406, 0.0, 0.6]
    record = step_record(rewards, loo_adv(rewards, 0.53))
    record["pass_rate"] = 0.5  # tamper: true pass rate is 0.25
    result = audit.audit_step(record, WEIGHTS)
    assert not result["ok"]
    assert any("pass_rate" in e["check"] for e in result["errors"])


def test_skipped_all_fail_step_ok():
    """A skipped repair-routed all-fail step (all rewards equal, shaped 0.0)
    is not a reward-path violation."""
    rewards = [0.0, 0.0, 0.0, 0.0]
    record = step_record(rewards, [0.0, 0.0, 0.0, 0.0], skipped=True)
    # flat group: raw LOO all zero -> scale stays 1.0; recorded adv 0
    record["advantage_scale"] = 1.0
    for c in record["rollout_rewards"]:
        c["shaped_reward"] = 0.0
        c["total_reward"] = 0.0
        c["verifier_reward"] = 0.0
        c["syntax_reward"] = 0.0
    result = audit.audit_step(record, WEIGHTS)
    assert result["ok"], result["errors"]


def test_missing_advantage_scale_reported_not_failed():
    """Without advantage_scale the advantage check is skipped (not silently
    green) and reported as a gap."""
    rewards = [1.0, 0.6406, 0.0, 0.6]
    record = step_record(rewards, [0.0] * 4)
    del record["advantage_scale"]
    result = audit.audit_step(record, WEIGHTS)
    assert result["ok"] or result["errors"]
    assert any(
        "scale" in str(e.get("gap", e.get("check", ""))) for e in result.get("gaps", [])
    ) or any("advantage" in e.get("check", "") and not e["ok"] for e in result.get("errors", []))


# ── harness-level verification (raw scorer outputs) ────────────────────────


def test_harness_details_shaped_recomputation():
    """With raw harness outputs supplied, recorded shaped must equal
    shaped_reward_from_details(harness.passed, harness.details)."""
    harness = [
        {
            "step": 1,
            "index": 2,
            "passed": False,
            "details": ["vqe: energy=-1.48250 need<=-1.50000"],
        },  # near miss -> 0.9
        {
            "step": 1,
            "index": 3,
            "passed": False,
            "details": ["Traceback (most recent call last):", "TypeError: ..."],
        },  # crash -> 0.0
    ]
    rewards = [1.0, 0.6406, 0.7, 0.2667]
    record = step_record(rewards, loo_adv(rewards, 0.53))
    # candidate 2 recorded shaped must equal the recomputed near-miss 0.9
    record["rollout_rewards"][2]["shaped_reward"] = 0.9
    record["rollout_rewards"][3]["shaped_reward"] = 0.0
    record["mean_shaped_reward"] = (1.0 + 0.6 + 0.9 + 0.0) / 4.0
    result = audit.audit_step(record, WEIGHTS, harness_details=harness)
    assert result["ok"], result["errors"]


def test_harness_shaped_mismatch_fails():
    harness = [
        {"step": 1, "index": 2, "passed": False, "details": ["energy=-1.48250 need<=-1.50000"]},
    ]
    rewards = [1.0, 0.6406, 0.7, 0.2667]
    record = step_record(rewards, loo_adv(rewards, 0.53))
    record["rollout_rewards"][2]["shaped_reward"] = 0.6  # recorded != recomputed 0.9
    result = audit.audit_step(record, WEIGHTS, harness_details=harness)
    assert not result["ok"]
    assert any("shaped" in e["check"] for e in result["errors"]), result["errors"]


def test_harness_pass_verdict_mismatch_fails():
    harness = [
        {"step": 1, "index": 0, "passed": True, "details": []},
    ]
    rewards = [1.0, 0.6406, 0.7, 0.2667]
    record = step_record(rewards, loo_adv(rewards, 0.53))
    record["rollout_rewards"][0]["pass"] = False  # harness says PASS
    result = audit.audit_step(record, WEIGHTS, harness_details=harness)
    assert not result["ok"]
    assert any("verdict" in e["check"] for e in result["errors"]), result["errors"]


# ── records / weights resolution / robustness ──────────────────────────────


def test_argv_weight_resolution_matches_launch():
    argv = [
        "training/grpo_trainer.py",
        "--reward-pass-weight",
        "0.45",
        "--reward-syntax-weight",
        "0.05",
        "--reward-interface-weight",
        "0.10",
        "--reward-verifier-weight",
        "0.10",
        "--reward-import-hygiene-weight",
        "0.05",
        "--reward-mode",
        "p_dominant",
        "--reward-pass-mass",
        "0.40",
        "--reward-shaped-mass",
        "0.35",
        "--reward-judge-mass",
        "0.25",
        "--advantage-mode",
        "loo",
        "--loo-advantage-scale",
        "shared_mad",
    ]
    w = audit.resolve_weights_from_argv(argv)
    assert w["shaped"] == pytest.approx(0.45)
    assert w["syntax"] == pytest.approx(0.05)
    assert w["interface"] == pytest.approx(0.10)
    assert w["verifier"] == pytest.approx(0.10)
    # 2026-08-27 (research-audit P5): brevity 0.0 -> 0.05 counterweight
    # (run-5 prompt-echo = brevity-like degenerate output; small positive
    # weight breaks flat-reward deadlocks); total weight 0.75 -> 0.80
    assert w["brevity"] == pytest.approx(0.05)
    assert w["hygiene"] == pytest.approx(0.05)
    assert w["total"] == pytest.approx(0.80)


def test_brevity_counterweight_enters_progress_renormalization() -> None:
    # with brevity 0.05 the progress denominator is 0.80; a brevity-1.0
    # candidate gets 0.05/0.80 of progress credit
    weights = dict(audit.DEFAULT_WEIGHTS)
    total = audit.compose_total(0.0, 0.5, 0.0, 0.0, 0.0, 1.0, 0.0, weights)
    # progress = (0.45*0.5 + 0.05*1.0)/0.80 = 0.34375; p_dominant with P=0
    assert total == pytest.approx(0.34375)
    # a verbose (brevity 0) candidate loses the counterweight
    total_verbose = audit.compose_total(0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, weights)
    assert total_verbose == pytest.approx(0.45 * 0.5 / 0.80)


def test_brevity_counterweight_pinned_in_config_and_trainer() -> None:
    import json as _json

    cfg = _json.loads(
        (ROOT / "configs" / "rl" / "qwen36_27b_fv_gspo_asi2.json").read_text(encoding="utf-8")
    )
    assert float(cfg["training"]["reward_brevity_weight"]) == 0.05
    import sys as _sys

    from training.grpo_trainer import parse_args

    _sys.argv = ["grpo_trainer.py", "--model-name", "m"]
    ns = parse_args()
    assert ns.reward_brevity_weight == 0.05
    assert ns.entropy_floor_weight == 0.03  # T1c: entropy floor 0.01 -> 0.03


def test_record_without_rollout_rewards_is_a_gap_not_a_crash():
    record = {"step": 99, "task": "t", "skipped": True}
    result = audit.audit_step(record, WEIGHTS)
    assert result["ok"]
    assert any(g.get("gap") == "no_rollout_rewards" for g in result.get("gaps", []))


def test_corrupt_line_skipped_and_rest_audited(tmp_path):
    p = tmp_path / "metrics.jsonl"
    p.write_text(
        json.dumps(step_record([1.0, 0.6406, 0.0, 0.6], loo_adv([1.0, 0.6406, 0.0, 0.6], 0.53)))
        + "\nNOT_JSON\n"
        + json.dumps(step_record([1.0, 1.0, 1.0, 1.0], [0.0] * 4))
        + "\n",
        encoding="utf-8",
    )
    report = audit.audit_metrics_file(p, WEIGHTS)
    assert report["steps_audited"] == 2
    assert report["lines_skipped"] == 1


def test_load_step_records_and_run_full_report(tmp_path):
    p = tmp_path / "metrics.jsonl"
    records = [
        step_record([1.0, 0.6406, 0.0, 0.6], loo_adv([1.0, 0.6406, 0.0, 0.6], 0.53)),
        step_record([0.0, 0.0, 0.0, 0.0], [0.0] * 4, skipped=True),
    ]
    p.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    report = audit.audit_metrics_file(p, WEIGHTS)
    assert report["steps_audited"] == 2
    assert report["candidates_audited"] == 8
    assert report["errors"] == 0
    assert report["ok"]


# ── eval_results.jsonl full-schema mode (r9 wave, G1 resolved) ─────────────


def eval_row(step=1, index=0, **overrides):
    row = {
        "step": step,
        "index": index,
        "passed": False,
        "details": ["fidelity=0.8765 need>=0.9"],
        "detail_budget": 8,
        "code_hash": "deadbeef" * 8,
        "syntax": 1.0,
        "interface": 0.75,
        "verifier": 0.875,
        "import_hygiene": 1.0,
    }
    row.update(overrides)
    return row


def test_eval_schema_exact_composition_matches():
    """With the full eval_results.jsonl row (syntax/interface/verifier/
    import_hygiene persisted), the failing candidate's total must equal the
    exact composition clamp01(P + (1-P)*progress), not just a band."""
    rewards = [1.0, 0.6406, 0.7, 0.2667]
    record = step_record(rewards, loo_adv(rewards, 0.53))
    row = eval_row(
        step=1,
        index=2,
        passed=False,
        details=["energy=-1.48250 need<=-1.50000"],  # 1 failure, budget 8 -> verifier 0.875
        syntax=1.0,
        interface=0.75,
        verifier=0.875,
        import_hygiene=1.0,
    )
    # shaped recomputed from the near-miss detail = 0.9 (cap)
    # exact total: (0.45*0.9 + 0.05*1 + 0.10*0.75 + 0.10*0.875 + 0.05*1)/0.80
    # (brevity weight 0.05 in the denominator; the row carries no brevity -> 0)
    expected_total = (0.45 * 0.9 + 0.05 * 1.0 + 0.10 * 0.75 + 0.10 * 0.875 + 0.05 * 1.0) / 0.80
    final_rewards = [1.0, 0.6406, expected_total, 0.2667]
    record = step_record(final_rewards, loo_adv(final_rewards, 0.53))
    record["rollout_rewards"][2]["shaped_reward"] = 0.9
    record["rollout_rewards"][2]["verifier_reward"] = 0.875
    # cand3 (0.2667) is a hard fail: shaped 0.0 keeps its composition band valid
    record["rollout_rewards"][3]["shaped_reward"] = 0.0
    record["mean_shaped_reward"] = (1.0 + 0.6 + 0.9 + 0.0) / 4.0
    result = audit.audit_step(record, WEIGHTS, harness_details=[row])
    assert result["ok"], result["errors"]
    exact = [e for e in result.get("exact", []) if e.get("candidate") == 2]
    assert any(e["check"] == "total_exact_composition" for e in exact), result


def test_eval_schema_tampered_total_fails():
    """A total that contradicts the persisted components must be flagged
    exactly (this is the check the band could not do)."""
    rewards = [1.0, 0.6406, 0.6, 0.2667]
    record = step_record(rewards, loo_adv(rewards, 0.53))
    row = eval_row(step=1, index=2, interface=0.75, verifier=0.5, import_hygiene=1.0)
    record["rollout_rewards"][2]["shaped_reward"] = 0.9
    record["rollout_rewards"][2]["verifier_reward"] = 0.5
    record["rollout_rewards"][2]["total_reward"] = 0.3  # impossible: exact total 0.8
    result = audit.audit_step(record, WEIGHTS, harness_details=[row])
    assert not result["ok"]
    assert any("total" in e["check"] for e in result["errors"]), result["errors"]


def test_eval_schema_component_mismatch_fails():
    """Persisted verifier/syntax must equal the recorded per-candidate values."""
    rewards = [1.0, 0.6406, 0.6, 0.2667]
    record = step_record(rewards, loo_adv(rewards, 0.53))
    row = eval_row(step=1, index=1, syntax=1.0, verifier=0.875)
    record["rollout_rewards"][1]["verifier_reward"] = 0.5  # row says 0.875
    result = audit.audit_step(record, WEIGHTS, harness_details=[row])
    assert not result["ok"]
    assert any("verifier" in e["check"] for e in result["errors"]), result["errors"]


def test_eval_schema_detail_budget_verifier_exact():
    """detail_budget in the row enables the exact verifier recomputation
    1 - min(failures, budget)/budget on fail."""
    # cand3 (index 3) becomes a near-miss fail: shaped 0.9, verifier 0.875,
    # exact total from the full component set (interface=1.0, hygiene=1.0)
    expected_total = (0.45 * 0.9 + 0.05 * 1.0 + 0.10 * 1.0 + 0.10 * 0.875 + 0.05 * 1.0) / 0.80
    final_rewards = [1.0, 0.6406, 0.6, expected_total]
    record = step_record(final_rewards, loo_adv(final_rewards, 0.53))
    row = eval_row(
        step=1,
        index=3,
        passed=False,
        details=["fidelity=0.8765 need>=0.9"],  # 1 failure, budget 8 -> 0.875
        interface=1.0,
        verifier=0.875,
        import_hygiene=1.0,
    )
    record["rollout_rewards"][3]["verifier_reward"] = 0.875
    record["rollout_rewards"][3]["shaped_reward"] = 0.9  # recomputed from detail
    record["mean_shaped_reward"] = (1.0 + 0.6 + 0.6 + 0.9) / 4.0
    result = audit.audit_step(record, WEIGHTS, harness_details=[row])
    assert result["ok"], result["errors"]


def test_runtime_failure_verifier_zero_rule():
    """Production zeroes verifier_reward on a runtime failure (crash) even
    when details/budget would imply 1 - failures/budget. The audit's
    details-based recompute must mirror that rule (2026-08-26: run-6 flagged
    30 false positives because it was omitted)."""
    row = eval_row(
        step=1,
        index=1,
        passed=False,
        details=["AttributeError: module 'candidate' has no attribute 'shor_encode'"],
        interface=0.25,
        verifier=0.0,
    )
    # cand1 (crash): shaped 0.0 (crash rule), verifier 0.0 (crash rule)
    # exact total with row components (interface 0.25, hygiene 1.0):
    # (0.45*0 + 0.05*1 + 0.10*0.25 + 0.10*0 + 0.05*1)/0.80
    crash_total = (0.45 * 0.0 + 0.05 * 1.0 + 0.10 * 0.25 + 0.10 * 0.0 + 0.05 * 1.0) / 0.80
    final_rewards = [1.0, crash_total, 0.6, 0.2667]
    record = step_record(final_rewards, loo_adv(final_rewards, 0.53))
    record["rollout_rewards"][1]["shaped_reward"] = 0.0
    record["rollout_rewards"][1]["verifier_reward"] = 0.0
    # cand3 (0.2667) is a hard fail too: shaped 0.0 keeps its band valid
    record["rollout_rewards"][3]["shaped_reward"] = 0.0
    record["mean_shaped_reward"] = (1.0 + 0.0 + 0.6 + 0.0) / 4.0
    result = audit.audit_step(record, WEIGHTS, harness_details=[row])
    assert result["ok"], result["errors"]
    exact = [e for e in result.get("exact", []) if e.get("candidate") == 1]
    assert any(e["check"] == "total_exact_composition" for e in exact), result


def test_runtime_failure_marker_set_matches_production():
    """The audit's local crash-marker set must agree with the production
    _has_runtime_failure so crash detection can never drift."""
    from training.grpo_utils import _has_runtime_failure as prod

    samples = [
        "AttributeError: module 'candidate' has no attribute 'shor_encode'",
        "SyntaxError: invalid syntax",
        "NameError: name 'apply_error' is not defined",
        "ImportError: cannot import name 'qiskit'",
        "TypeError: unsupported operand type(s) for +: 'int' and 'str'",
        "ModuleNotFoundError: No module named 'pennylane'",
        "IndentationError: unexpected indent",
        "TabError: inconsistent use of tabs",
        "fidelity=0.8765 need>=0.9",  # numeric near-miss, not a crash
        "phase_estimation(0.25, 3) -> 3, expected 2",
        "harness subprocess timed out after 300s",  # timeout is not in the marker set
    ]
    for sample in samples:
        mine = audit._has_runtime_failure([sample])
        theirs = prod([sample])
        assert mine == theirs, f"marker mismatch for {sample!r}: audit={mine} prod={theirs}"


def test_p_dominant_judge_active_band_includes_judge_term():
    """2026-09-01 (reward-verifier): p_dominant with the frozen judge ACTIVE —
    production blends w*J into the shaped term (w = min(weight_sum, 0.05),
    grpo_utils.blend_comprehensive_reward), so a judge-scored candidate's
    recorded total sits in the [w=0, w=0.05] band, NOT at the judge-absent
    point. The audit must accept the healthy judged candidate and reject a
    tampered total outside the band (was false-failing every judged step)."""
    from types import SimpleNamespace

    import torch

    from training.grpo_trainer import (
        build_eval_result_row,
        build_rollout_rewards,
        compose_policy_training_reward,
    )
    from training.grpo_utils import MODEL_JUDGE_DIMENSIONS, judge_composite_score

    jw = {d: 0.05 for d in MODEL_JUDGE_DIMENSIONS}
    jdims = {
        "correctness": 0.8,
        "runnability": 0.6,
        "result_correctness": 0.7,
        "efficiency": 0.5,
        "quality": 0.9,
    }
    j = judge_composite_score(jdims, jw)  # 0.7
    entry = {
        "passed": False,
        "pass_reward": 0.0,
        "shaped_reward": 0.9,
        "syntax_reward": 1.0,
        "interface_reward": 0.75,
        "verifier_reward": 0.875,
        "brevity_reward": 1.0,
        "import_hygiene_reward": 1.0,
        "self_eval_reward": 0.0,
        "model_dim_scores": jdims,
        "judge_reward": j,
        "details": ["fidelity=0.8765 need>=0.9"],
    }
    args = SimpleNamespace(
        reward_pass_weight=0.45,
        reward_syntax_weight=0.05,
        reward_interface_weight=0.10,
        reward_verifier_weight=0.10,
        reward_brevity_weight=0.05,
        reward_import_hygiene_weight=0.05,
        reward_mode="p_dominant",
        reward_pass_mass=0.50,
        reward_shaped_mass=0.40,
        reward_judge_mass=0.10,
    )
    entry["total_reward"] = compose_policy_training_reward(
        entry, args, model_dim_scores=jdims, judge_weights=jw
    )
    row = build_eval_result_row(step=1, index=0, code="x", entry=entry, detail_budget=8)
    cand = build_rollout_rewards([entry], torch.zeros(1))[0]
    weights = audit.resolve_weights_from_config(
        ROOT / "configs" / "rl" / "qwen36_27b_fv_gspo_asi2.json"
    )
    checks = audit.audit_candidate(cand, weights, harness=row)
    errors = [e for e in checks if not e["ok"]]
    assert not errors, errors
    # the production total differs from the judge-absent point by w*J*(1-P)
    lo = audit.compose_total(0.0, 0.9, 1.0, 0.75, 0.875, 1.0, 1.0, weights)
    assert abs(lo - 0.896875) < 1e-9
    assert abs(float(entry["total_reward"]) - 0.88703125) < 1e-6  # judge term present
    # tamper: a total BELOW the w=0 lo is impossible (judge term can only
    # subtract w*J from the shaped term) -> must be flagged
    tampered = dict(cand, total_reward=lo - 0.05)
    errs = [e for e in audit.audit_candidate(tampered, weights, harness=row) if not e["ok"]]
    assert any("total" in e["check"] for e in errs), errs


def test_harness_exact_mode_applies_crash_zeroing_rule():
    """F16 (code-review wave): the H2 exact-mode verifier recompute must apply
    the production runtime-failure zeroing — a crashing candidate (SyntaxError:
    marker) has verifier 0.0 in the row; the audit must NOT recompute
    1 - failures/budget and false-fail the healthy step."""
    import torch

    from tests.test_grpo_trainer_eval_results import _entry  # noqa: F401

    details = ["SyntaxError: bad token"]
    entry = _entry(False, details, verifier=0.0)
    # exact composition with the crash zeroing (shaped 0.0, verifier 0.0)
    from scripts.sapo_reward_audit import compose_total

    weights = dict(audit.DEFAULT_WEIGHTS)
    entry["total_reward"] = compose_total(
        pass_reward=0.0,
        shaped=float(audit.recompute_shaped_from_details(False, details)),
        syntax=1.0,
        interface=0.5,
        verifier=0.0,
        brevity=0.5,
        hygiene=1.0,
        weights=weights,
    )
    from training.grpo_trainer import build_eval_result_row, build_rollout_rewards

    row = build_eval_result_row(step=1, index=0, code="x", entry=entry, detail_budget=8)
    cand = build_rollout_rewards([entry], torch.zeros(1))[0]
    record = {"step": 1, "task": "t", "rollout_rewards": [cand]}
    result = audit.audit_step(record, WEIGHTS, harness_details=[row])
    assert result["ok"], result["errors"]
    assert not [e for e in result["errors"] if "verifier" in e.get("check", "")], result["errors"]

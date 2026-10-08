#!/usr/bin/env python3
"""SAPO step-record MATH AUDIT — independent recomputation of every logged
loss value, the loss reduction, and all rollout rewards from a training step
record (training-math auditor role, 2026-08-25).

Two modes:
  * ``instrumented`` (default) — records with the 2026-08-25 instrumentation
    fields: ``per_candidate_losses``, ``loss_breakdown.loss_recomputed``,
    ``loss_reduction``, ``rollout_rewards``, ``lora_b_max_delta``/
    ``zero_change_alarm``. The documented identities:
        loss_recomputed  == Σ_i w_i·loss_i            (w_i = 1/G, G = loss-candidate count)
        loss             == loss_recomputed + DR terms (when DR flags fired)
        loss_i           == -A_i·sapo_gate_mean_i + kl·seq_kl_i
                            (kl is one scalar per step -> cross-candidate consistent)
        rollout_rewards   aligned 1:1 with candidate order; mean(total_reward)
                           == mean_reward; LOO advantages proportional to
                           (r_i - mean_other_i)/scale, clamped at ±clip
        zero_change_alarm ⟺ lora_b_max_delta == 0.0 EXACTLY
  * ``legacy`` — pre-instrumentation records (run-3 era, sapo_per_candidate_stats
    with gate_mean/seq_kl/ratio_mean but no per-candidate losses/advantages):
        loss == -mean(gate_i·A_i) + kl·mean(seq_kl_i)  with the inferred
        mean(gate·A) inside the rigorous bound |m| ≤ max_gate·loo_advantage_rms
        (max_gate = 4/τ_pos over the τ band), plus the prior audit's tighter
        |m| ≤ mean(gate)·RMS(A) as a NOTE-level check; gate/ratio physical
        bands; signal-magnitude identity; RunningMAD EMA bounds
        (0.99·scale_prev ≤ scale ≤ 0.99·scale_prev + 0.01·2·clip) and the
        flat-step exact invariance.

All recomputation here is HAND-DERIVED from the published formulas
(arXiv:2511.20347 + the documented reduction contract); this module does NOT
call the trainer's own helpers. A disagreement between this recomputation and
a logged value is a defect (ERROR) — that is the point of the audit.

CLI:
    python scripts/sapo_math_audit_step_records.py --jsonl FILE [--mode ...]
    python scripts/sapo_math_audit_step_records.py --record FILE.json [--mode ...]
Exit: 0 clean | 1 NOTE-only findings | 2 ERROR findings.
"""
# ruff: noqa: UP038  # (X | Y) isinstance is py3.10-only; py3.9 .venv gate (precedent: training/grpo_trainer.py)

from __future__ import annotations

import argparse
import json
import math
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Independent reference math (hand-derived; NOT the trainer's helpers)
# ---------------------------------------------------------------------------

CLIP_LOWER = math.exp(-8.0)  # ratio floor under the ±8 log-ratio clamp
CLIP_UPPER = math.exp(8.0)  # ratio ceiling


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def sapo_gate(r: float, tau: float) -> float:
    """g(r) = (4/tau)·sigmoid(tau·(r-1)) — SAPO smooth gate (per token)."""
    return (4.0 / tau) * _sigmoid(tau * (r - 1.0))


def sapo_per_token_loss_reference(
    cur: Sequence[float],
    old: Sequence[float],
    advantage: float,
    *,
    tau_pos: float,
    tau_neg: float,
    kl_coeff: float,
    numerical_log_ratio_clip: float = 8.0,
) -> dict[str, float]:
    """Per-candidate SAPO loss recomputed TOKEN BY TOKEN.

    r_t = exp(clamp(cur_t - old_t, ±clip)); tau = tau_pos if A > 0 else tau_neg;
    loss = -mean_t[g(r_t)·A] + kl·mean_t[k3(r_t)] with k3 = expm1(z) - z clamped
    to >= 0. Returns loss, gate_mean, seq_kl, ratio_mean — the exact stats the
    trainer logs per candidate.
    """
    tokens = min(len(cur), len(old))
    if tokens == 0:
        return {
            "loss": float("nan"),
            "gate_mean": 0.0,
            "seq_kl": 0.0,
            "ratio_mean": 0.0,
            "n_tokens": 0,
        }
    tau = tau_pos if advantage > 0.0 else tau_neg
    gates: list[float] = []
    k3s: list[float] = []
    ratios: list[float] = []
    for ct, ot in zip(cur[:tokens], old[:tokens]):  # noqa: B905
        if not (math.isfinite(ct) and math.isfinite(ot)):
            continue
        z = max(-numerical_log_ratio_clip, min(numerical_log_ratio_clip, ct - ot))
        r = math.exp(z)
        gates.append(sapo_gate(r, tau))
        k3s.append(max(math.expm1(z) - z, 0.0))
        ratios.append(r)
    if not gates:
        return {
            "loss": float("nan"),
            "gate_mean": 0.0,
            "seq_kl": 0.0,
            "ratio_mean": 0.0,
            "n_tokens": 0,
        }
    n = float(len(gates))
    gate_mean = sum(gates) / n
    seq_kl = sum(k3s) / n
    ratio_mean = sum(ratios) / n
    loss = -(gate_mean * advantage) + kl_coeff * seq_kl
    return {
        "loss": loss,
        "gate_mean": gate_mean,
        "seq_kl": seq_kl,
        "ratio_mean": ratio_mean,
        "n_tokens": n,
    }


def recompute_aggregate_sapo_loss(per_candidate_losses: Sequence[Mapping[str, Any]]) -> float:
    """Σ w_i·loss_i over the loss candidates (zero-token entries contribute 0)."""
    total = 0.0
    for entry in per_candidate_losses:
        loss_value = entry.get("loss")
        weight = entry.get("weight")
        if loss_value is None or weight is None:
            continue
        total += float(weight) * float(loss_value)
    return total


def leave_one_out_raw(rewards: Sequence[float]) -> list[float]:
    """A_i = r_i - mean(other group members)."""
    n = len(rewards)
    if n < 2:
        return [0.0] * n
    total = sum(rewards)
    return [r - (total - r) / (n - 1) for r in rewards]


def gate_physical_bounds(tau: float) -> tuple[float, float]:
    """Per-token gate bounds under the ±8 log-ratio clamp, for one tau."""
    lower = sapo_gate(CLIP_LOWER, tau)
    upper = sapo_gate(CLIP_UPPER, tau)
    return lower * (1.0 - 1e-6), upper * (1.0 + 1e-6)


def gate_ratio_residual(gate_mean: float, ratio_mean: float, seq_kl: float, tau: float) -> float:
    """|gate_mean - g(r̄)| — the recomputation residual of the recorded gate mean
    from the recorded mean ratio. Rigorous bound: |gate(r) - g(r̄)| <= |r - r̄|
    (|g'| <= 1) and RMS(r - 1) <= sqrt(2·seq_kl) because (r-1)^2 <= 2·k3(r)
    holds for every r > 0 (k3 = r - 1 - ln r)."""
    return abs(gate_mean - sapo_gate(ratio_mean, tau))


def gate_ratio_bound(seq_kl: float) -> float:
    return math.sqrt(2.0 * max(0.0, seq_kl)) * (1.0 + 1e-6) + 1e-6


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    step: int
    check: str
    severity: str  # "ERROR" | "NOTE" | "OK"
    message: str

    def render(self) -> str:
        return f"[{self.severity:>5}] step {self.step:<3} {self.check}: {self.message}"


# ---------------------------------------------------------------------------
# Instrumented-record checks (2026-08-25 field contract)
# ---------------------------------------------------------------------------


def _loss_candidates(per_candidate_losses: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return [e for e in per_candidate_losses if e.get("loss") is not None]


def audit_aggregate_identity(record: Mapping[str, Any]) -> list[Finding]:
    step = int(record.get("step", -1))
    if record.get("skipped"):
        return []
    pcl = record.get("per_candidate_losses")
    bd = record.get("loss_breakdown")
    if not isinstance(pcl, list) or not isinstance(bd, dict):
        return [
            Finding(
                step, "schema", "ERROR", "updated step lacks per_candidate_losses/loss_breakdown"
            )
        ]
    # Batched-path records (gspo/gspo_ln/grpo) carry no per-candidate values
    # by contract — the aggregate identity applies only to per-candidate paths.
    if bd.get("reduction") == "batched":
        return []
    findings: list[Finding] = []
    loss_cands = _loss_candidates(pcl)
    g_from_entries = len(loss_cands)
    g_from_breakdown = bd.get("candidate_count")
    recomputed = recompute_aggregate_sapo_loss(pcl)
    recorded = bd.get("loss_recomputed")
    if recorded is None:
        findings.append(
            Finding(step, "aggregate", "ERROR", "loss_breakdown.loss_recomputed missing")
        )
    else:
        tol = 1e-6 * max(1.0, abs(recomputed))
        if abs(recomputed - float(recorded)) > tol:
            findings.append(
                Finding(
                    step,
                    "aggregate",
                    "ERROR",
                    f"Σ w_i·loss_i = {recomputed:.9g} != loss_recomputed {recorded:.9g} (Δ={recomputed - float(recorded):.3g})",
                )
            )
    if g_from_breakdown is not None and int(g_from_breakdown) != g_from_entries:
        findings.append(
            Finding(
                step,
                "aggregate",
                "ERROR",
                f"candidate_count {g_from_breakdown} != loss candidates {g_from_entries}",
            )
        )
    if bd.get("reduction") == "per_candidate_1_over_g" and g_from_entries > 0:
        expected_w = 1.0 / g_from_entries
        for entry in loss_cands:
            w = entry.get("weight")
            if w is None:
                findings.append(Finding(step, "aggregate", "ERROR", "loss candidate lacks weight"))
                continue
            if abs(float(w) - expected_w) > 1e-9:
                findings.append(
                    Finding(
                        step,
                        "aggregate",
                        "ERROR",
                        f"candidate {entry.get('index')}: w={w} != 1/G={expected_w:.9g}",
                    )
                )
    recorded_loss_count = bd.get("loss_candidate_count")
    if recorded_loss_count is not None and int(recorded_loss_count) != g_from_entries:
        findings.append(
            Finding(
                step,
                "aggregate",
                "ERROR",
                f"loss_candidate_count {recorded_loss_count} != {g_from_entries}",
            )
        )
    recorded_tokens = bd.get("weighted_token_total")
    if recorded_tokens is not None:
        token_sum = sum(float(e.get("n_tokens") or 0.0) for e in loss_cands)
        if abs(token_sum - float(recorded_tokens)) > 1e-6 * max(1.0, token_sum):
            findings.append(
                Finding(
                    step,
                    "aggregate",
                    "ERROR",
                    f"weighted_token_total {recorded_tokens} != Σ n_i {token_sum}",
                )
            )
    # Zero-token entries must be marked, not silently dropped.
    rollout = record.get("rollout_rewards")
    if isinstance(rollout, list) and len(rollout) != len(pcl):
        findings.append(
            Finding(
                step,
                "aggregate",
                "ERROR",
                f"per_candidate_losses ({len(pcl)}) != rollout_rewards ({len(rollout)}) — candidate coverage mismatch",
            )
        )
    for entry in pcl:
        if float(entry.get("n_tokens") or 0.0) == 0.0:
            if entry.get("loss") is not None or entry.get("weight") is not None:
                findings.append(
                    Finding(
                        step,
                        "aggregate",
                        "ERROR",
                        f"zero-token candidate {entry.get('index')} has loss/weight (must be null)",
                    )
                )
            if not entry.get("excluded_reason"):
                findings.append(
                    Finding(
                        step,
                        "aggregate",
                        "NOTE",
                        f"zero-token candidate {entry.get('index')} lacks excluded_reason",
                    )
                )
    return findings


def audit_final_loss_identity(record: Mapping[str, Any]) -> list[Finding]:
    """loss == loss_recomputed + entropy-floor penalty + (DR terms added).

    2026-08-26 (r10, entropy floor): the entropy-floor term
    (``loss_breakdown.entropy_floor_penalty``) is part of the final loss
    value (0 when disabled or above the floor) — the identity includes it.
    """
    step = int(record.get("step", -1))
    if record.get("skipped"):
        return []
    bd = record.get("loss_breakdown")
    if not isinstance(bd, dict):
        return []
    findings: list[Finding] = []
    recomputed = bd.get("loss_recomputed")
    final = bd.get("loss")
    if recomputed is None or final is None:
        return []
    added = 0.0
    added += float(bd.get("entropy_floor_penalty") or 0.0)
    if bd.get("dr_pair_loss_added"):
        weight = float(record.get("dr_pair_loss_weight") or 0.0)
        value = float(record.get("dr_pair_loss_value") or 0.0)
        added += weight * value
    if bd.get("dr_variance_correction_added"):
        added += float(record.get("dr_variance_correction_value") or 0.0)
    expected = float(recomputed) + added
    tol = 1e-5 * max(1.0, abs(expected))
    if abs(float(final) - expected) > tol:
        findings.append(
            Finding(
                step,
                "final_loss",
                "ERROR",
                f"loss {final:.9g} != loss_recomputed + entropy-floor/DR terms {expected:.9g} (Δ={float(final) - expected:.3g})",
            )
        )
    return findings


def audit_per_candidate_loss_identity(
    record: Mapping[str, Any],
    *,
    tau_pos: float,
    tau_neg: float,
    kl_coeff: float | None = None,
    kl_max: float = 0.5,
) -> list[Finding]:
    """loss_i == -A_i·gate_mean_i + kl·seq_kl_i with one kl per step.

    kl is not logged per record, so it is (a) checked against the EXPECTED
    kl — the record's ``kl_beta`` when adaptive KL is live, else the caller's
    ``kl_coeff`` (the launch config value) — via the ABSOLUTE residual
    |loss_i + A_i·gate_mean_i - kl·seq_kl_i|, and (b) inferred per candidate
    and required to be consistent across candidates.

    Noise model (fp32): loss_i, A_i, gate_mean_i, seq_kl_i are fp32-rounded
    (half-ULP ~6e-8 relative; measured residuals on live records <= 1.2e-7
    absolute per unit magnitude). The inference kl_i = (loss_i + A_i·g_i)/sk_i
    amplifies the numerator noise by 1/sk_i, so the cross-candidate tolerance
    is noise-aware: 5e-6·(M_i/sk_i + M_j/sk_j) with M = max(|loss|, |A·g|).
    """
    step = int(record.get("step", -1))
    if record.get("skipped"):
        return []
    pcl = record.get("per_candidate_losses")
    if not isinstance(pcl, list):
        return []
    findings: list[Finding] = []
    loss_cands = _loss_candidates(pcl)
    if not loss_cands:
        return []
    kl_expected = record.get("kl_beta")
    if not isinstance(kl_expected, (int, float)):
        kl_expected = kl_coeff
    kls: list[tuple[int, float, float]] = []  # (index, inferred kl, M)
    for entry in loss_cands:
        idx = entry.get("index")
        loss_i = float(entry["loss"])
        adv = float(entry.get("advantage") or 0.0)
        gate = float(entry.get("sapo_gate_mean") or 0.0)
        sk = float(entry.get("seq_kl") or 0.0)
        num = loss_i + adv * gate  # == kl·seq_kl_i per the identity
        magnitude = max(abs(loss_i), abs(adv * gate), 1e-9)
        tol = 5e-6 * magnitude + 1e-7
        if sk <= 1e-9:
            # No KL term: loss_i must be -A·gate_mean within fp noise.
            if abs(num) > tol:
                findings.append(
                    Finding(
                        step,
                        "per_candidate_loss",
                        "ERROR",
                        f"candidate {idx}: seq_kl≈0 but loss_i + A·gate = {num:.6g} (loss_i {loss_i:.6g}, A {adv:.4g}, gate {gate:.5g})",
                    )
                )
        else:
            kls.append((idx, num / sk, magnitude))
            if kl_expected is not None and abs(num - kl_expected * sk) > tol:
                findings.append(
                    Finding(
                        step,
                        "per_candidate_loss",
                        "ERROR",
                        f"candidate {idx}: loss_i + A·gate - kl·seq_kl = {num - kl_expected * sk:.3e} "
                        f"exceeds fp noise {tol:.1e} for kl={kl_expected} (loss_i {loss_i:.6g}, A {adv:.4g}, gate {gate:.5g}, seq_kl {sk:.3e})",
                    )
                )
        # Physical gate band: tau by advantage sign.
        tau = tau_pos if adv > 0.0 else tau_neg
        lo, hi = gate_physical_bounds(tau)
        if not (lo <= gate <= hi):
            findings.append(
                Finding(
                    step,
                    "per_candidate_loss",
                    "ERROR",
                    f"candidate {idx}: gate_mean {gate:.6g} outside physical band [{lo:.4g},{hi:.4g}] for τ={tau} (A={adv:.4g})",
                )
            )
        # Gate-vs-ratio recomputation: |gate_mean - g(r̄)| <= sqrt(2·seq_kl).
        ratio_mean = float(entry.get("ratio_mean") or 1.0)
        residual = gate_ratio_residual(gate, ratio_mean, sk, tau)
        bound = gate_ratio_bound(sk)
        if residual > bound:
            findings.append(
                Finding(
                    step,
                    "per_candidate_loss",
                    "ERROR",
                    f"candidate {idx}: |gate_mean - g(ratio_mean)| = {residual:.6g} > √(2·seq_kl) = {bound:.6g} — gate cannot be recomputed from the logged ratio/KL stats",
                )
            )
        if abs(ratio_mean - 1.0) > bound:
            findings.append(
                Finding(
                    step,
                    "per_candidate_loss",
                    "ERROR",
                    f"candidate {idx}: |ratio_mean - 1| = {abs(ratio_mean - 1.0):.6g} > √(2·seq_kl) = {bound:.6g}",
                )
            )
        if sk < -1e-9 or ratio_mean < CLIP_LOWER - 1e-6 or ratio_mean > CLIP_UPPER + 1e-6:
            findings.append(
                Finding(
                    step,
                    "per_candidate_loss",
                    "ERROR",
                    f"candidate {idx}: seq_kl/ratio_mean outside physical bands (sk={sk:.3g}, rm={entry.get('ratio_mean')})",
                )
            )
    if len(kls) >= 2:
        # Cross-candidate consistency with noise-aware tolerance: the inferred
        # kl_i = num_i/sk_i carries absolute error ~5e-6·M_i/sk_i (M = max
        # magnitude of the numerator terms), so small seq_kl values loosen the
        # pair tolerance proportionally — fp32 rounding, not a fabrication.
        sk_by_index = {int(e.get("index")): float(e.get("seq_kl") or 0.0) for e in loss_cands}
        for a in range(len(kls)):
            for b in range(a + 1, len(kls)):
                idx_a, kla, ma = kls[a]
                idx_b, klb, mb = kls[b]
                sk_a = sk_by_index.get(int(idx_a), 0.0)
                sk_b = sk_by_index.get(int(idx_b), 0.0)
                tol_pair = 5e-6 * (ma / max(sk_a, 1e-9) + mb / max(sk_b, 1e-9)) + 1e-6
                if abs(kla - klb) > tol_pair:
                    findings.append(
                        Finding(
                            step,
                            "per_candidate_loss",
                            "ERROR",
                            f"inferred kl inconsistent: candidate {idx_a} kl={kla:.6g} vs candidate {idx_b} kl={klb:.6g} (noise-aware tol {tol_pair:.3g})",
                        )
                    )
    if kls:
        kl_min = min(v for _, v, _ in kls)
        kl_max_i = max(v for _, v, _ in kls)
        if kl_min < -1e-3:
            findings.append(
                Finding(
                    step,
                    "per_candidate_loss",
                    "ERROR",
                    f"negative inferred kl {kl_min:.5g} (kl is a non-negative penalty coefficient)",
                )
            )
        if kl_max_i > kl_max + 0.001:
            findings.append(
                Finding(
                    step,
                    "per_candidate_loss",
                    "NOTE",
                    f"inferred kl {kl_max_i:.5g} above plausible ceiling {kl_max} — check adaptive-KL config",
                )
            )
    return findings


def audit_rollout_alignment(
    record: Mapping[str, Any], *, advantage_clip: float = 2.5
) -> list[Finding]:
    step = int(record.get("step", -1))
    rollout = record.get("rollout_rewards")
    findings: list[Finding] = []
    if not isinstance(rollout, list) or not rollout:
        return [Finding(step, "rollout", "ERROR", "rollout_rewards missing/empty")]
    n = len(rollout)
    # 1:1 index alignment.
    indices = [int(e.get("index", -1)) for e in rollout]
    if indices != list(range(n)):
        findings.append(
            Finding(
                step,
                "rollout",
                "ERROR",
                f"indices {indices} != 0..{n - 1} (1:1 candidate order violated)",
            )
        )
    group_size = record.get("group_size")
    if group_size is not None and int(group_size) != n:
        findings.append(
            Finding(
                step,
                "rollout",
                "NOTE",
                f"rollout_rewards count {n} != group_size {group_size} (repair-lane candidates may extend the rollout)",
            )
        )
    rewards = [float(e.get("total_reward") or 0.0) for e in rollout]
    advs = [e.get("advantage") for e in rollout]
    # mean_reward identity.
    mean_reward = record.get("mean_reward")
    if mean_reward is not None:
        recomputed_mean = sum(rewards) / n
        if abs(recomputed_mean - float(mean_reward)) > 1e-6 * max(1.0, abs(float(mean_reward))):
            findings.append(
                Finding(
                    step,
                    "rollout",
                    "ERROR",
                    f"mean(total_reward) {recomputed_mean:.9g} != mean_reward {mean_reward}",
                )
            )
    mean_shaped = record.get("mean_shaped_reward")
    if mean_shaped is not None:
        shaped = [float(e.get("shaped_reward") or 0.0) for e in rollout]
        recomputed_shaped = sum(shaped) / n
        if abs(recomputed_shaped - float(mean_shaped)) > 1e-6 * max(1.0, abs(float(mean_shaped))):
            findings.append(
                Finding(
                    step,
                    "rollout",
                    "ERROR",
                    f"mean(shaped_reward) {recomputed_shaped:.9g} != mean_shaped_reward {mean_shaped}",
                )
            )
    pass_rate = record.get("pass_rate")
    if pass_rate is not None:
        pass_rewards = [float(e.get("pass_reward") or 0.0) for e in rollout]
        recomputed_pass = sum(pass_rewards) / n
        if abs(recomputed_pass - float(pass_rate)) > 1e-6 * max(1.0, abs(float(pass_rate))):
            findings.append(
                Finding(
                    step,
                    "rollout",
                    "ERROR",
                    f"mean(pass_reward) {recomputed_pass:.9g} != pass_rate {pass_rate}",
                )
            )
    # Pass-flag consistency with the documented builder semantics.
    for e in rollout:
        passed = bool(e.get("pass"))
        pass_reward = float(e.get("pass_reward") or 0.0)
        if not passed and pass_reward > 0.0:
            findings.append(
                Finding(
                    step,
                    "rollout",
                    "ERROR",
                    f"candidate {e.get('index')}: pass=false but pass_reward={pass_reward:.4g} (builder sets pass when pass_reward>0)",
                )
            )
        if passed and pass_reward == 0.0:
            findings.append(
                Finding(
                    step,
                    "rollout",
                    "NOTE",
                    f"candidate {e.get('index')}: pass=true with pass_reward=0 (only explainable by the unrecorded 'passed' flag)",
                )
            )
    # LOO proportionality: A_i == clamp((r_i - mean_other_i)/scale, ±clip).
    if all(a is not None for a in advs):
        adv_values = [float(a) for a in advs]  # type: ignore[misc]
        loo = leave_one_out_raw(rewards)
        max_abs_r = max(1.0, max(abs(r) for r in rewards))
        flat = all(abs(v) <= 1e-6 * max_abs_r for v in loo)
        if flat:
            if any(abs(a) > 1e-4 for a in adv_values):
                findings.append(
                    Finding(
                        step,
                        "rollout",
                        "ERROR",
                        f"flat reward group (LOO≈0) but recorded advantages {adv_values} are non-zero",
                    )
                )
        else:
            scale: float | None = None
            scale_ref: int | None = None
            for i, (v, a) in enumerate(zip(loo, adv_values)):  # noqa: B905
                if abs(a) == advantage_clip or abs(a) >= advantage_clip * (1 - 1e-9):
                    # Clamped class: sign must match, magnitude exactly clip, raw non-zero.
                    if v == 0.0:
                        findings.append(
                            Finding(
                                step,
                                "rollout",
                                "ERROR",
                                f"candidate {i}: clamped advantage {a} but raw LOO = 0",
                            )
                        )
                        continue
                    if (a > 0) != (v > 0):
                        findings.append(
                            Finding(
                                step,
                                "rollout",
                                "ERROR",
                                f"candidate {i}: clamped advantage {a} sign mismatches raw LOO {v:.5g}",
                            )
                        )
                    if scale is not None and scale > abs(v) / advantage_clip * (1 + 1e-6):
                        findings.append(
                            Finding(
                                step,
                                "rollout",
                                "ERROR",
                                f"candidate {i}: |LOO|/clip {abs(v) / advantage_clip:.6g} < inferred scale {scale:.6g} — clamp impossible",
                            )
                        )
                    continue
                # Unclamped class.
                if v == 0.0:
                    if abs(a) > 1e-6:
                        findings.append(
                            Finding(
                                step,
                                "rollout",
                                "ERROR",
                                f"candidate {i}: raw LOO 0 but advantage {a} != 0",
                            )
                        )
                    continue
                if a == 0.0:
                    findings.append(
                        Finding(
                            step,
                            "rollout",
                            "ERROR",
                            f"candidate {i}: raw LOO {v:.5g} != 0 but advantage 0 (infinite scale impossible)",
                        )
                    )
                    continue
                this_scale = v / a
                if this_scale <= 0.0:
                    findings.append(
                        Finding(
                            step,
                            "rollout",
                            "ERROR",
                            f"candidate {i}: LOO/advantage scale {this_scale:.6g} <= 0",
                        )
                    )
                    continue
                if scale is None:
                    scale = this_scale
                    scale_ref = i
                elif abs(this_scale - scale) > 1e-4 * max(1.0, abs(scale)):
                    findings.append(
                        Finding(
                            step,
                            "rollout",
                            "ERROR",
                            f"candidate {i}: LOO/advantage scale {this_scale:.6g} != {scale:.6g} from candidate {scale_ref} — advantages not proportional to raw LOO",
                        )
                    )
            if scale is None:
                findings.append(
                    Finding(
                        step,
                        "rollout",
                        "NOTE",
                        "all candidates clamped (or zero) — LOO proportionality unverifiable from this record",
                    )
                )
        # RMS / mean-abs identities.
        rms_rec = record.get("loo_advantage_rms")
        if rms_rec is not None:
            rms = math.sqrt(sum(a * a for a in adv_values) / n)
            if abs(rms - float(rms_rec)) > 1e-6 * max(1.0, abs(float(rms_rec))):
                findings.append(
                    Finding(
                        step,
                        "rollout",
                        "ERROR",
                        f"RMS(advantages) {rms:.9g} != loo_advantage_rms {rms_rec}",
                    )
                )
        mean_abs_rec = record.get("loo_advantage_mean_abs")
        if mean_abs_rec is not None:
            mean_abs = sum(abs(a) for a in adv_values) / n
            if abs(mean_abs - float(mean_abs_rec)) > 1e-6 * max(1.0, abs(float(mean_abs_rec))):
                findings.append(
                    Finding(
                        step,
                        "rollout",
                        "ERROR",
                        f"mean|advantages| {mean_abs:.9g} != loo_advantage_mean_abs {mean_abs_rec}",
                    )
                )
    return findings


def audit_zero_change_gate(record: Mapping[str, Any]) -> list[Finding]:
    step = int(record.get("step", -1))
    findings: list[Finding] = []
    delta = record.get("lora_b_max_delta")
    alarm = record.get("zero_change_alarm")
    if alarm is not None and bool(alarm):
        if delta is None or float(delta) != 0.0:
            findings.append(
                Finding(
                    step,
                    "zero_change",
                    "ERROR",
                    f"zero_change_alarm=true but lora_b_max_delta={delta} (must be 0.0 EXACTLY)",
                )
            )
        if not bool(record.get("zero_change_recommend_stop")):
            findings.append(
                Finding(
                    step,
                    "zero_change",
                    "ERROR",
                    "zero_change_alarm=true but recommend_stop missing/false",
                )
            )
    elif delta is not None and float(delta) == 0.0:
        findings.append(
            Finding(
                step,
                "zero_change",
                "NOTE",
                "lora_b_max_delta==0.0 exactly but zero_change_alarm absent (trust-region reject on step 1 is the legit case)",
            )
        )
    return findings


def audit_reduction_string(record: Mapping[str, Any]) -> list[Finding]:
    step = int(record.get("step", -1))
    red = record.get("loss_reduction")
    findings: list[Finding] = []
    if not isinstance(red, str):
        return [Finding(step, "reduction", "ERROR", "loss_reduction missing")]
    if record.get("skipped"):
        if "[skipped: no loss computed this step]" not in red:
            findings.append(
                Finding(
                    step,
                    "reduction",
                    "ERROR",
                    "skipped record lacks the skipped marker in loss_reduction",
                )
            )
    else:
        if "[skipped:" in red:
            findings.append(
                Finding(step, "reduction", "ERROR", "updated record carries the skipped marker")
            )
    return findings


def audit_step_record_instrumented(
    record: Mapping[str, Any],
    *,
    tau_pos: float,
    tau_neg: float,
    advantage_clip: float,
    kl_coeff: float | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    findings += audit_aggregate_identity(record)
    findings += audit_final_loss_identity(record)
    findings += audit_per_candidate_loss_identity(
        record, tau_pos=tau_pos, tau_neg=tau_neg, kl_coeff=kl_coeff
    )
    findings += audit_rollout_alignment(record, advantage_clip=advantage_clip)
    findings += audit_zero_change_gate(record)
    findings += audit_reduction_string(record)
    return findings


# ---------------------------------------------------------------------------
# Legacy-record checks (run-3 era: sapo_per_candidate_stats, no new fields)
# ---------------------------------------------------------------------------


def audit_legacy_step_record(
    record: Mapping[str, Any],
    *,
    kl_coeff: float = 0.01,
    tau_pos: float = 1.0,
    tau_neg: float = 1.05,
    advantage_clip: float = 2.5,
    mad_decay: float = 0.99,
    prev_scale: float | None = None,
    mad_initialized: bool = False,
) -> tuple[list[Finding], float | None, bool]:
    """Existing-method recomputation for pre-instrumentation records."""
    step = int(record.get("step", -1))
    findings: list[Finding] = []
    rms = record.get("loo_advantage_rms")
    scale = record.get("advantage_scale")
    # The RunningMAD update runs on EVERY step (skipped included — the
    # advantage block precedes routing), so the scale chain must track through
    # skipped records too.
    if record.get("skipped"):
        if scale is not None and prev_scale is not None:
            chain_findings, mad_initialized = _check_scale_chain(
                step,
                float(scale),
                float(prev_scale),
                rms,
                mad_decay,
                advantage_clip,
                mad_initialized,
            )
            findings.extend(chain_findings)
        return findings, (float(scale) if scale is not None else prev_scale), mad_initialized
    stats = record.get("sapo_per_candidate_stats")
    loss = record.get("loss")
    if not isinstance(stats, list) or not stats or loss is None or rms is None:
        return (
            [
                Finding(
                    step,
                    "schema",
                    "ERROR",
                    "legacy updated record lacks sapo_per_candidate_stats/loss/loo_advantage_rms",
                )
            ],
            prev_scale,
            mad_initialized,
        )
    gates = [float(s.get("sapo_gate_mean") or 0.0) for s in stats]
    seq_kls = [float(s.get("seq_kl") or 0.0) for s in stats]
    ratio_means = [float(s.get("ratio_mean") or 1.0) for s in stats]
    g_count = len(stats)
    mean_gate = sum(gates) / g_count
    mean_sk = sum(seq_kls) / g_count
    loss_v = float(loss)
    # Loss identity: loss = -mean(gate·A) + kl·mean(seq_kl)  ->  m = kl·mean(sk) - loss.
    m = kl_coeff * mean_sk - loss_v
    rms_v = float(rms)
    # Rigorous bound with the RECORDED gates: |mean(g·A)| <= max_i(g_i)·RMS(A)
    # (|Σ g_i A_i|/G <= max_i g_i · mean|A| <= max_i g_i · RMS).
    max_gate = max(gates)
    if abs(m) > max_gate * rms_v * (1 + 1e-6):
        findings.append(
            Finding(
                step,
                "loss_identity",
                "ERROR",
                f"|mean(gate·A)| = |{m:.6g}| > max(gate)·RMS(A) = {max_gate * rms_v:.6g} — loss cannot be recomputed from recorded stats",
            )
        )
    elif abs(m) > mean_gate * rms_v * (1 + 1e-6):
        findings.append(
            Finding(
                step,
                "loss_identity",
                "NOTE",
                f"|mean(gate·A)| = {abs(m):.6g} exceeds the audit-consistency bound mean(gate)·RMS(A) = {mean_gate * rms_v:.6g} but inside the rigorous max(gate)·RMS bound",
            )
        )
    # Physical bands + gate-vs-ratio recomputation per candidate. The
    # advantage sign (which selects τ) is NOT recorded in legacy records, so
    # the gate must be recomputable from the logged ratio/KL stats under AT
    # LEAST ONE of the two configured taus (τ_pos for A>0, τ_neg for A<0);
    # a candidate fitting neither cannot be a real SAPO gate.
    lo_union, hi_union = (
        min(gate_physical_bounds(tau_pos)[0], gate_physical_bounds(tau_neg)[0]),
        max(gate_physical_bounds(tau_pos)[1], gate_physical_bounds(tau_neg)[1]),
    )
    for i, (g, sk, rm) in enumerate(zip(gates, seq_kls, ratio_means)):  # noqa: B905
        if not (lo_union <= g <= hi_union):
            findings.append(
                Finding(
                    step,
                    "gate_band",
                    "ERROR",
                    f"candidate {i}: gate_mean {g:.6g} outside [{lo_union:.4g},{hi_union:.4g}]",
                )
            )
        if sk < -1e-9 or not (CLIP_LOWER - 1e-6 <= rm <= CLIP_UPPER + 1e-6):
            findings.append(
                Finding(
                    step,
                    "gate_band",
                    "ERROR",
                    f"candidate {i}: seq_kl {sk:.3g} / ratio_mean {rm:.4g} outside physical bands",
                )
            )
        bound = gate_ratio_bound(sk)
        fits_pos = gate_ratio_residual(g, rm, sk, tau_pos) <= bound
        fits_neg = gate_ratio_residual(g, rm, sk, tau_neg) <= bound
        if not (fits_pos or fits_neg):
            findings.append(
                Finding(
                    step,
                    "gate_ratio",
                    "ERROR",
                    f"candidate {i}: gate_mean {g:.6g} not recomputable from ratio_mean {rm:.6g}/seq_kl {sk:.3g} under either τ (residual τ_pos {gate_ratio_residual(g, rm, sk, tau_pos):.5g}, τ_neg {gate_ratio_residual(g, rm, sk, tau_neg):.5g}, bound {bound:.5g})",
                )
            )
        if abs(rm - 1.0) > bound:
            findings.append(
                Finding(
                    step,
                    "gate_band",
                    "ERROR",
                    f"candidate {i}: |ratio_mean - 1| = {abs(rm - 1.0):.6g} > √(2·seq_kl) = {bound:.6g}",
                )
            )
    # Signal-magnitude identity (loo mode).
    kind = record.get("update_signal_kind")
    mag = record.get("update_signal_magnitude")
    if (
        kind == "loo_advantage_rms"
        and mag is not None
        and abs(float(mag) - rms_v) > 1e-9 * max(1.0, rms_v)
    ):
        findings.append(
            Finding(
                step,
                "signal",
                "ERROR",
                f"update_signal_magnitude {mag} != loo_advantage_rms {rms_v} for kind 'loo_advantage_rms'",
            )
        )
    mean_abs = record.get("loo_advantage_mean_abs")
    if mean_abs is not None and float(mean_abs) > rms_v * (1 + 1e-9):
        findings.append(
            Finding(
                step,
                "signal",
                "ERROR",
                f"loo_advantage_mean_abs {mean_abs} > loo_advantage_rms {rms_v} (RMS ≥ mean|·| always)",
            )
        )
    # RunningMAD EMA bounds (shared_mad update-first path).
    if scale is not None and prev_scale is not None:
        chain_findings, mad_initialized = _check_scale_chain(
            step, float(scale), float(prev_scale), rms, mad_decay, advantage_clip, mad_initialized
        )
        findings.extend(chain_findings)
    return findings, (float(scale) if scale is not None else prev_scale), mad_initialized


def _check_scale_chain(
    step: int,
    scale: float,
    prev_scale: float,
    rms: Any,
    mad_decay: float,
    advantage_clip: float,
    mad_initialized: bool,
) -> bool:
    """RunningMAD chain bounds for one step.

    Code-pinned semantics (training/grpo_utils.py RunningMAD):
      * flat group (batch MAD <= 0)  -> scale EXACTLY unchanged (the 2026-08-24
        flat-group fix), at any point in the chain;
      * first NON-flat batch (count==0) -> scale is set to the batch MAD
        DIRECTLY (initialization bypasses the EMA — documented in the class
        docstring: flat batches carry no evidence for first-batch init);
      * later non-flat batches -> EMA: decay·prev <= scale <= decay·prev +
        (1-decay)·2·clip (batch MAD <= 2·clip for ±clip-clamped advantages).
    Returns (findings, updated ``mad_initialized`` state).
    """
    findings: list[Finding] = []
    rms_v = 0.0 if rms is None else float(rms)
    # Flat-group test: the trainer's flatness is mad==0 (all LOO values
    # IDENTICAL), which leaves a sub-ULP rms ~1e-7 on fp32 reward tensors
    # (run-3 step 2: rms 5.96e-8 with scale byte-identical 1.0). Any real
    # signal sits far above the 1e-6 noise floor (update gate 0.05).
    if rms_v <= 1e-6:
        if scale != prev_scale:
            findings.append(
                Finding(
                    step,
                    "mad_scale",
                    "ERROR",
                    f"flat group (loo_advantage_rms {rms_v:.3g} at noise floor) but advantage_scale moved {prev_scale:.9g} -> {scale:.9g} (must be exact)",
                )
            )
        return findings, mad_initialized
    if not mad_initialized:
        # First non-flat batch: scale = batch MAD directly, bounded by the
        # reward dispersion (<= 2·clip). Cannot pin further from the record.
        if not (0.0 <= scale <= 2 * advantage_clip * (1 + 1e-9)):
            findings.append(
                Finding(
                    step,
                    "mad_scale",
                    "ERROR",
                    f"first non-flat batch: advantage_scale {scale:.9g} outside batch-MAD band [0, {2 * advantage_clip}]",
                )
            )
        return findings, True
    lower = mad_decay * prev_scale * (1 - 1e-9)
    upper = mad_decay * prev_scale + (1 - mad_decay) * (2 * advantage_clip) * (1 + 1e-9)
    if scale < lower or scale > upper:
        findings.append(
            Finding(
                step,
                "mad_scale",
                "ERROR",
                f"advantage_scale {scale:.9g} outside EMA bounds [{lower:.9g},{upper:.9g}] from prev {prev_scale:.9g}",
            )
        )
    return findings, True


# ---------------------------------------------------------------------------
# Batch drivers
# ---------------------------------------------------------------------------


def audit_jsonl(
    path: Path,
    *,
    mode: str,
    tau_pos: float,
    tau_neg: float,
    kl_coeff: float,
    advantage_clip: float,
) -> tuple[list[Finding], int, int]:
    findings: list[Finding] = []
    prev_scale: float | None = None
    mad_initialized = False
    records = 0
    updated = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            findings.append(Finding(-1, "jsonl", "ERROR", f"unparseable line: {exc}"))
            continue
        records += 1
        if not record.get("skipped"):
            updated += 1
        if mode == "legacy":
            rec_findings, prev_scale, mad_initialized = audit_legacy_step_record(
                record,
                kl_coeff=kl_coeff,
                tau_pos=tau_pos,
                tau_neg=tau_neg,
                advantage_clip=advantage_clip,
                prev_scale=prev_scale,
                mad_initialized=mad_initialized,
            )
        else:
            rec_findings = audit_step_record_instrumented(
                record,
                tau_pos=tau_pos,
                tau_neg=tau_neg,
                advantage_clip=advantage_clip,
                kl_coeff=kl_coeff,
            )
        findings.extend(rec_findings)
    n_error = sum(1 for f in findings if f.severity == "ERROR")
    n_note = sum(1 for f in findings if f.severity == "NOTE")
    return findings, n_error, n_note


def render_report(findings: Sequence[Finding], path: Path, mode: str, records: int) -> str:
    errors = [f for f in findings if f.severity == "ERROR"]
    notes = [f for f in findings if f.severity == "NOTE"]
    lines = [
        f"SAPO step-record math audit — {path} (mode={mode}, records={records})",
        f"ERRORS: {len(errors)} | NOTES: {len(notes)} | OK: {len(findings) - len(errors) - len(notes)}",
        "",
    ]
    for f in findings:
        if f.severity != "OK":
            lines.append(f.render())
    lines.append("")
    if not errors and not notes:
        lines.append("VERDICT: CLEAN — every logged loss/reduction/reward recomputes exactly.")
    elif errors:
        lines.append(
            "VERDICT: VIOLATION — recomputation disagrees with logged values (see ERRORS)."
        )
    else:
        lines.append(
            "VERDICT: CLEAN-with-notes — recomputation agrees; NOTE items are unverifiable-by-record."
        )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jsonl", type=Path, help="grpo_step_metrics.jsonl to audit")
    parser.add_argument("--record", type=Path, help="single step-record JSON to audit")
    parser.add_argument("--mode", choices=["instrumented", "legacy"], default="instrumented")
    parser.add_argument("--tau-pos", type=float, default=1.0)
    parser.add_argument("--tau-neg", type=float, default=1.05)
    parser.add_argument("--kl", type=float, default=0.01, help="fixed kl_coeff for legacy mode")
    parser.add_argument("--advantage-clip", type=float, default=2.5)
    parser.add_argument("--json-out", type=Path, default=None, help="write findings as JSON")
    args = parser.parse_args(argv)
    if not args.jsonl and not args.record:
        parser.error("need --jsonl or --record")
    if args.record:
        record = json.loads(args.record.read_text(encoding="utf-8"))
        if args.mode == "legacy":
            findings, _, _ = audit_legacy_step_record(
                record,
                kl_coeff=args.kl,
                tau_pos=args.tau_pos,
                tau_neg=args.tau_neg,
                advantage_clip=args.advantage_clip,
            )
        else:
            findings = audit_step_record_instrumented(
                record,
                tau_pos=args.tau_pos,
                tau_neg=args.tau_neg,
                advantage_clip=args.advantage_clip,
                kl_coeff=args.kl,
            )
        n_error = sum(1 for f in findings if f.severity == "ERROR")
        n_note = sum(1 for f in findings if f.severity == "NOTE")
        print(render_report(findings, args.record, args.mode, 1))
    else:
        findings, n_error, n_note = audit_jsonl(
            args.jsonl,
            mode=args.mode,
            tau_pos=args.tau_pos,
            tau_neg=args.tau_neg,
            kl_coeff=args.kl,
            advantage_clip=args.advantage_clip,
        )
        records = sum(1 for _ in open(args.jsonl, encoding="utf-8"))
        print(render_report(findings, args.jsonl, args.mode, records))
    if args.json_out:
        args.json_out.write_text(
            json.dumps(
                [
                    {"step": f.step, "check": f.check, "severity": f.severity, "message": f.message}
                    for f in findings
                ],
                indent=1,
            )
        )
    return 2 if n_error else (1 if n_note else 0)


if __name__ == "__main__":
    sys.exit(main())

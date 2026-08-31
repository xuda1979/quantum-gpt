from __future__ import annotations

import json
import re
from pathlib import Path

import torch

from training.grpo_trainer import annotate_self_repair_diagnostics, scale_optimizer_lr
from training.grpo_utils import (
    chunked_log_probs_and_entropy,
    old_sampled_kl,
    sapo_loss_metrics,
    sequence_ratio_stats,
)

ROOT = Path(__file__).resolve().parents[1]


def _loss(cur, old, advantages, *, kl=0.0):
    return sapo_loss_metrics(
        cur,
        old,
        torch.tensor(advantages, dtype=torch.float32),
        tau_pos=1.0,
        tau_neg=1.05,
        kl_coeff=kl,
        numerical_log_ratio_clip=8.0,
    )


def test_sapo_uses_sample_mean_not_length_weighted_token_mean() -> None:
    short = torch.tensor([-1.8], requires_grad=True)
    long = torch.tensor([-2.0] * 9, requires_grad=True)
    old_short = torch.tensor([-2.0])
    old_long = torch.tensor([-2.0] * 9)

    batch_loss, _ = _loss([short, long], [old_short, old_long], [1.0, -1.0])
    short_loss, _ = _loss([short], [old_short], [1.0])
    long_loss, _ = _loss([long], [old_long], [-1.0])

    assert torch.allclose(batch_loss, (short_loss + long_loss) / 2, atol=1e-7)


def test_sapo_per_candidate_backward_matches_batch_gradient() -> None:
    batch_cur = [
        torch.tensor([-2.1, -1.9], requires_grad=True),
        torch.tensor([-1.7, -2.2, -2.0], requires_grad=True),
    ]
    old = [torch.tensor([-2.0, -2.0]), torch.tensor([-2.0, -2.0, -2.0])]
    batch_loss, _ = _loss(batch_cur, old, [0.75, -0.25], kl=0.01)
    batch_loss.backward()
    batch_grads = [value.grad.clone() for value in batch_cur]

    split_cur = [value.detach().clone().requires_grad_(True) for value in batch_cur]
    for index, advantage in enumerate((0.75, -0.25)):
        candidate_loss, _ = _loss([split_cur[index]], [old[index]], [advantage], kl=0.01)
        (candidate_loss / 2).backward()

    # py3.9-compat strict zip (the local evaluator venv is python 3.9).
    assert len(split_cur) == len(batch_grads)
    for actual, expected in zip(split_cur, batch_grads, strict=False):
        assert torch.allclose(actual.grad, expected, atol=1e-7)


def test_sapo_kl_penalty_is_non_negative_and_increases_loss() -> None:
    cur = [torch.tensor([-1.2, -2.8], requires_grad=True)]
    old = [torch.tensor([-2.0, -2.0])]
    without_kl, _ = _loss(cur, old, [0.5], kl=0.0)
    with_kl, stats = _loss(cur, old, [0.5], kl=0.1)

    assert stats["seq_kl"] >= 0.0
    assert with_kl >= without_kl


def test_rollout_log_probs_follow_behavior_temperature() -> None:
    logits = torch.tensor([[[0.2, 1.2, -0.7], [2.0, -1.0, 0.5]]])
    targets = torch.tensor([[1, 2]])
    temperature = 1.7
    actual = chunked_log_probs_and_entropy(
        logits,
        targets,
        logit_clip=20.0,
        chunk_size=2,
        policy_temperature=temperature,
    )
    expected = (
        torch.log_softmax(logits.float() / temperature, dim=-1)
        .gather(-1, targets.unsqueeze(-1))
        .squeeze(-1)
    )
    assert torch.allclose(actual, expected, atol=1e-6)
    trainer = (ROOT / "training/grpo_trainer.py").read_text(encoding="utf-8")
    assert trainer.count("policy_temperature=effective_temperature") >= 2
    assert 'call_kwargs["policy_temperature"] = effective_temperature' in trainer


def test_sapo_k3_uses_current_over_old_for_old_policy_samples() -> None:
    old = torch.tensor([0.0])
    current = torch.tensor([torch.log(torch.tensor(2.0)).item()])

    kl = old_sampled_kl(current, old)
    expected = 1.0 - torch.log(torch.tensor(2.0))

    assert torch.allclose(kl, expected, atol=1e-7)
    _, stats = _loss([current], [old], [0.0], kl=1.0)
    assert abs(stats["seq_kl"] - float(expected)) < 1e-7


def test_sapo_has_nonzero_on_policy_gradient_with_one_inner_epoch() -> None:
    old = torch.tensor([-2.0, -1.0])
    current = old.clone().requires_grad_(True)

    loss, _ = _loss([current], [old], [1.0])
    loss.backward()

    assert current.grad is not None
    assert torch.count_nonzero(current.grad).item() == current.numel()
    assert torch.all(current.grad < 0)


def test_sequence_trust_kl_is_nonnegative_when_current_probability_increases() -> None:
    old = torch.tensor([-2.0, -2.0])
    current = torch.tensor([-1.0, -1.0])

    stats = sequence_ratio_stats(
        current,
        old,
        clip_low=0.1,
        clip_high=0.2,
    )

    # Signed mean(old-current) was -1 here and could never trip a positive
    # threshold. The old-sampled k3 distance must remain positive.
    assert stats["seq_kl_after"] > 0.0
    assert abs(stats["seq_kl_after"] - (torch.exp(torch.tensor(1.0)) - 2.0).item()) < 1e-6


def test_successful_self_repair_never_overwrites_original_rollout_reward() -> None:
    original = {
        "pass_reward": 0.0,
        "shaped_reward": 0.2,
        "total_reward": 0.25,
    }
    repaired = {
        "pass_reward": 1.0,
        "shaped_reward": 1.0,
        "total_reward": 1.0,
    }

    result = annotate_self_repair_diagnostics(original, repaired, {"best_round": 1})

    assert result["pass_reward"] == 0.0
    assert result["shaped_reward"] == 0.2
    assert result["total_reward"] == 0.25
    assert result["self_repair_passed"] is True
    assert result["self_repair_reward_applied"] is False
    assert result["self_repair_candidate_total_reward"] == 1.0


def test_trust_region_lr_scaling_respects_floor() -> None:
    param = torch.nn.Parameter(torch.tensor(1.0))
    optimizer = torch.optim.AdamW([param], lr=2e-6)

    assert scale_optimizer_lr(optimizer, factor=0.5, min_lr=1e-6) == (2e-6, 1e-6)
    assert scale_optimizer_lr(optimizer, factor=0.5, min_lr=1e-6) == (1e-6, 1e-6)


def test_trainer_gates_nonfinite_gradients_before_optimizer_step() -> None:
    trainer = (ROOT / "training/grpo_trainer.py").read_text(encoding="utf-8")
    guard = trainer.index("if not math.isfinite(grad_norm):")
    step = trainer.index("optimizer.step()", guard)

    assert guard < step
    assert "optimizer.zero_grad(set_to_none=True)" in trainer[guard:step]
    assert 'inner_skip_reason = "non_finite_gradient"' in trainer[guard:step]


def test_partial_inner_epoch_failure_keeps_completed_update_and_trust_check() -> None:
    trainer = (ROOT / "training/grpo_trainer.py").read_text(encoding="utf-8")

    assert "completed_inner_epochs += 1" in trainer
    assert "optimizer_substeps_per_rollout=completed_inner_epochs" in trainer
    assert "inner_early_stop_reason=inner_early_stop_reason" in trainer
    assert "and last_normalized_old_log_probs" in trainer
    assert "torch.stack(last_normalized_old_log_probs)" in trainer


def test_27b_sapo_config_matches_launcher_defaults() -> None:
    config = json.loads(
        (ROOT / "configs/rl/qwen36_27b_fv_gspo_asi2.json").read_text(encoding="utf-8")
    )
    launcher = (ROOT / "scripts/asi2_launch_grpo_27b_selfeval.sh").read_text(encoding="utf-8")

    assert config["training"]["loss_mode"] == "sapo"
    assert config["fv_gspo"]["loss_mode"] == "sapo"
    assert config["training"]["sapo_tau_pos"] == 1.0
    assert config["training"]["sapo_tau_neg"] == 1.05
    assert re.search(r'LOSS_MODE="\$\{LOSS_MODE:-sapo\}"', launcher)
    assert re.search(r'SAPO_TAU_POS="\$\{SAPO_TAU_POS:-1\.0\}"', launcher)
    assert re.search(r'SAPO_TAU_NEG="\$\{SAPO_TAU_NEG:-1\.05\}"', launcher)


def test_asi3_launcher_cannot_inherit_stale_generic_training_overrides() -> None:
    launcher = (ROOT / "scripts/asi3_launch_grpo_direct.sh").read_text(encoding="utf-8")

    required = {
        "NUM_NPU": "8",
        "LOSS_MODE": "sapo",
        # 2026-09-01 (manager, entropy-blowup fix): RUN-12 at LR 2e-4 caused
        # CAPABILITY EROSION (entropy 0.055 -> 1.59, 16 trust-region windows);
        # RUN-13 relaunched at LR 5e-5 with the working judge + entropy floor
        # + recalibrated clips (STANDUP #227b/#233, launcher comment). The
        # default is the calibrated 5e-5 so ANY relaunch without an explicit
        # ASI3_SAPO_LR override gets the safe stack — see
        # test_asi3_sapo_launcher_readiness.py for the pin rationale.
        "LR": "5e-5",
        "KL_COEFF": "0.01",
        "INNER_EPOCHS": "1",
        "LORA_RANK": "16",
        "LORA_ALPHA": "64",
        # 2048/2048/3072 are the proven generation-budget and max-seq-length
        # defaults (run 9 + 08-23 fence-stop run: 0% truncation at 2048; seq
        # length must clear prompt+completion or the SAPO token gate drops the
        # completion tail — 2026-08-24 audit).
        "MAX_NEW_TOKENS": "2048",
        "MAX_ADAPTIVE_NEW_TOKENS": "2048",
        "MAX_SEQ_LENGTH": "3072",
        "LOGIT_CLIP": "50.0",
        "BENCHMARK_FILE": "evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt",
        "SELF_REPAIR_ROUNDS": "0",
    }
    for name, default in required.items():
        if name in {"NUM_NPU", "LOSS_MODE", "SELF_REPAIR_ROUNDS"}:
            assert f'export {name}="{default}"' in launcher
        else:
            assert re.search(
                rf'export {name}="\$\{{ASI3_SAPO_[A-Z_]+:-{re.escape(default)}\}}"',
                launcher,
            ), name
        assert f'export {name}="${{{name}:-' not in launcher

    assert 'export CHECKPOINT_INTERVAL_SECONDS="${ASI3_SAPO_CHECKPOINT_SECONDS:-1800}"' in launcher
    assert '--max-adaptive-new-tokens "$MAX_ADAPTIVE_NEW_TOKENS"' in (
        ROOT / "scripts/asi2_launch_grpo_27b_selfeval.sh"
    ).read_text(encoding="utf-8")


def test_asi3_warm_adapter_must_match_requested_lora_shape() -> None:
    launcher = (ROOT / "scripts/asi3_launch_grpo_direct.sh").read_text(encoding="utf-8")
    assert 'config.get("r", -1)' in launcher
    assert 'config.get("lora_alpha", -1)' in launcher
    assert "warm adapter LoRA mismatch" in launcher


def test_trainer_persists_complete_launch_contract_before_model_load() -> None:
    trainer = (ROOT / "training/grpo_trainer.py").read_text(encoding="utf-8")
    assert 'launch_config_path = output_dir / "launch_config.json"' in trainer
    assert '"stage": "launch_config_written"' in trainer
    for field in (
        "inner_epochs",
        "sapo_tau_pos",
        "sapo_tau_neg",
        "lora_rank",
        "lora_alpha",
        "checkpoint_interval_seconds",
        "npu_device_map",
        "visible_npus_env",
    ):
        assert f'"{field}"' in trainer


def test_targeted10_launch_token_budget_is_flat_512_for_all_tasks() -> None:
    """2026-08-24 data-efficiency audit: the next-launch manifest
    (quantum_grpo_training_v7_targeted_integrity.txt) declares a .txt lineage
    (quantum_grpo_training_v4_targeted_disjoint.txt), so
    load_reference_code_char_counts() returns {} and
    adaptive_generation_token_budget() falls back to the flat 512-token base
    for EVERY task.  The adaptive headroom it would grant the longest task is
    lost: circuit_depth_optimization's 1343-char reference implies ~540 tokens
    at 2.5 chars/token (the adaptive formula), i.e. its solutions sit at/over
    the 512 cap once fences/comments/imports are included — a guaranteed
    mid-code truncation whenever the model answers verbosely.
    """
    from training.grpo_trainer import (
        adaptive_generation_token_budget,
        load_reference_code_char_counts,
    )

    manifest = ROOT / "evals/benchmarks/quantum_grpo_training_v7_targeted_integrity.txt"
    counts = load_reference_code_char_counts(manifest)
    assert counts == {}  # txt lineage => no hidden reference lengths

    task_ids = [
        "quantum_bitstring_maxcut_landscape",
        "quantum_circuit_depth_optimization",
        "quantum_circuit_phase_repair",
        "quantum_error_detection_bit_flip",
        "quantum_gate_alias_casefold_barrier",
        "quantum_measurement_bug_repair",
        "quantum_phase_measurement_register",
        "quantum_stabilizer_tableau_update_repair",
        "quantum_superdense_pauli_router",
        "quantum_teleportation_corrections",
    ]
    # Defect lock: every task currently gets the flat base budget.
    for task_id in task_ids:
        assert (
            adaptive_generation_token_budget(None, base_tokens=512, max_tokens=1024) == 512
        ), task_id
    # The headroom that is LOST: the adaptive formula on the longest reference.
    ref_chars = {
        "quantum_circuit_depth_optimization": 1343,
        "quantum_stabilizer_tableau_update_repair": 1202,
        "quantum_bitstring_maxcut_landscape": 1111,
    }
    for task_id, chars in ref_chars.items():
        adaptive = adaptive_generation_token_budget(chars, base_tokens=512, max_tokens=1024)
        assert adaptive >= 512, task_id
    # The FIX (trainer-side, see .sapo-loop/dataeff.md) must make the budget
    # path consult per-task lengths for txt-lineage manifests; once applied,
    # flip this assertion to expect 640 for circuit_depth_optimization.
    assert adaptive_generation_token_budget(1343, base_tokens=512, max_tokens=1024) > 512


def test_config_json_matches_launcher_defaults_on_critical_keys() -> None:
    """2026-08-24 bug-hunt (three-layer cross-check): the config json is a
    lineage/document artifact (not consumed by the trainer, which takes CLI
    args), but its values drifted stale (max_new_tokens 512, seq 2048, ckpt
    600, lr 1e-4, alpha 64, loo none) and would mislead any reader into
    believing the OOM-era settings were canonical. Aligned to the launcher
    defaults and locked here. 2026-08-25: lr escalated to 2e-4 (relaunch
    stack). 2026-09-01: lr de-escalated to 5e-5 — RUN-12 at 2e-4 caused
    entropy blowup/capability erosion; RUN-13's calibrated default is 5e-5
    (STANDUP #227b/#233, test_asi3_sapo_launcher_readiness.py)."""
    config = json.loads(
        (ROOT / "configs/rl/qwen36_27b_fv_gspo_asi2.json").read_text(encoding="utf-8")
    )
    launcher = (ROOT / "scripts/asi3_launch_grpo_direct.sh").read_text(encoding="utf-8")
    expected = {
        "lr": "5e-5",
        "kl_coeff": "0.01",
        "inner_epochs": "1",
        "max_new_tokens": "2048",
        "max_seq_length": "3072",
        "checkpoint_interval_seconds": "1800",
        "loss_mode": "sapo",
        "sapo_tau_pos": "1.0",
        "sapo_tau_neg": "1.05",
        "lora_rank": "16",
        "lora_alpha": "64",
        "group_size": "4",
        "max_adaptive_group": "4",
        "gspo_clip_low": "0.1",
        "gspo_clip_high": "0.2",
        "advantage_mode": "loo",
        "loo_advantage_scale": "shared_mad",
        "temperature": "1.0",
        "top_p": "1.0",
        "logit_clip": "50.0",
    }
    envs = {
        "lr": "LR",
        "kl_coeff": "KL_COEFF",
        "inner_epochs": "INNER_EPOCHS",
        "max_new_tokens": "MAX_NEW_TOKENS",
        "max_seq_length": "MAX_SEQ_LENGTH",
        "checkpoint_interval_seconds": "CHECKPOINT_INTERVAL_SECONDS",
        "loss_mode": "LOSS_MODE",
        "sapo_tau_pos": "SAPO_TAU_POS",
        "sapo_tau_neg": "SAPO_TAU_NEG",
        "lora_rank": "LORA_RANK",
        "lora_alpha": "LORA_ALPHA",
        "group_size": "GROUP_SIZE",
        "max_adaptive_group": "MAX_ADAPTIVE_GROUP",
        "gspo_clip_low": "GSPO_CLIP_LOW",
        "gspo_clip_high": "GSPO_CLIP_HIGH",
        "advantage_mode": "ADVANTAGE_MODE",
        "loo_advantage_scale": "LOO_ADVANTAGE_SCALE",
        "temperature": "TEMPERATURE",
        "top_p": "TOP_P",
        "logit_clip": "LOGIT_CLIP",
    }
    cfg = {**config.get("training", {}), **config.get("fv_gspo", {})}
    for key, env in envs.items():
        m = re.search(rf'export {env}="\$\{{ASI3_SAPO_[A-Z_]+:-([^}}]*)\}}"', launcher)
        if m is None:  # pinned without an override slot (e.g. LOSS_MODE="sapo")
            m = re.search(rf'export {env}="([^"\n]+)"', launcher)
        assert m, env
        launcher_value = m.group(1)
        # Numeric keys compare by value (config stores 2e-05, launcher "2e-5").
        try:
            cfg_matches = float(cfg.get(key)) == float(expected[key])
        except (TypeError, ValueError):
            cfg_matches = str(cfg.get(key)) == expected[key]
        assert cfg_matches, f"config {key}={cfg.get(key)}"
        assert launcher_value == expected[key], f"launcher {env}={launcher_value}"

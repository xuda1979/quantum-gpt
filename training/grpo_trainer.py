#!/usr/bin/env python3
"""GRPO (Group Relative Policy Optimization) trainer for code generation.

Samples N solutions per prompt, scores them with test harnesses,
and updates the policy using relative advantage within each group.

Usage:
    torchrun --nproc_per_node=8 training/grpo_trainer.py \
        --model-name models/Qwen2.5-1.5B-Instruct \
        --tasks-dir evals/tasks \
        --output-dir outputs/grpo-v1 \
        --device npu \
        --group-size 8 \
        --grpo-steps 100
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import importlib.util
import json
import math
import os
import random
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
from transformers import StoppingCriteriaList

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.compat import strict_zip as _strict_zip  # noqa: E402

# Per-step repair-sidecar auto-relaunch (root cause of run 20260913T233607Z:
# the sidecar died at launch, the per-step guard DETECTED it and printed the
# relaunch hint every step but never executed it, repair_queue.jsonl starved,
# converted_total==0 -> all_fail_without_repair breaker killed the leg).
SIDE_CAR_RELAUNCH_SCRIPT = Path("scripts") / "sapo_ensure_repair_sidecar.sh"
SIDE_CAR_RELAUNCH_TIMEOUT_S = 60


def _maybe_repair_sidecar_relaunch(
    sidecar_status: dict,
    sidecar_alarm_state: dict,
    output_dir,
    *,
    runner=None,
    script_path=None,
) -> bool:
    """Invoke the idempotent sidecar relauncher ONCE PER DEAD-EPISODE.

    Dedup mirrors the alarm-state dedup already used for the alarm print:
    consecutive dead steps attempt at most one relaunch; a RECOVERY clears
    the episode so a re-DEAD fires again. Never raises: a relaunch failure
    must not kill the trainer (log LOUD and continue).
    Returns True iff a relaunch was actually attempted this call.
    """
    if not sidecar_status.get("alarm"):
        # Recovered/healthy: clear the dead-episode dedup.
        sidecar_alarm_state["relaunch_attempted"] = False
        return False
    if sidecar_alarm_state.get("relaunch_attempted"):
        return False
    if runner is None:
        runner = subprocess.run
    path = Path(script_path) if script_path is not None else ROOT / SIDE_CAR_RELAUNCH_SCRIPT
    if not path.exists():
        print(
            f"[SIDECAR_RELAUNCH_SKIPPED] relauncher missing: {path} - relaunch the "
            f"sidecar manually via: bash scripts/sapo_ensure_repair_sidecar.sh {output_dir}",
            flush=True,
        )
        return False
    argv = ["bash", str(path), str(output_dir)]
    # Explicit, cwd-independent logdir (defect 6): sidecar_liveness derives the
    # heartbeat log from the logs/sapo_27b_ai convention, but the ensure
    # script's own default resolved against ITS cwd -- a trainer running from
    # any other cwd made liveness probe a nonexistent log -> relaunch churn.
    runner_env = dict(os.environ)
    runner_env["REPAIR_LOGDIR"] = str(ROOT / "logs" / "sapo_27b_ai")
    sidecar_alarm_state["relaunch_attempted"] = True
    try:
        proc = runner(argv, timeout=SIDE_CAR_RELAUNCH_TIMEOUT_S, env=runner_env)
        print(
            "[SIDECAR_RELAUNCH] attempted repair-sidecar relaunch: {} rc={}".format(
                " ".join(argv), getattr(proc, "returncode", "?")
            ),
            flush=True,
        )
        return True
    except Exception as exc:  # noqa: BLE001 - relaunch must never crash training
        print(
            "[SIDECAR_RELAUNCH_FAILED] argv={} error={!r} - continuing training; "
            "relaunch the sidecar manually via: bash scripts/"
            "sapo_ensure_repair_sidecar.sh {}".format(" ".join(argv), exc, output_dir),
            flush=True,
        )
        return False


# ruff: noqa: UP038  # (X | Y) isinstance is py3.10-only; py3.9 .venv gate
from training.generation import (  # noqa: E402
    _CODE_FENCE_OPEN_RE,  # noqa: F401  # deliberate re-export, pinned by test_generation_module_extraction
    StopAfterClosedCodeFence,
    append_fence_stop_markers,
    build_batched_prompt_inputs,
    build_generation_diagnostics,
    configured_eos_token_ids,
    configured_suppress_token_ids,
    extract_code,
    has_closed_code_fence,  # noqa: F401  # deliberate re-export, pinned by test_generation_module_extraction
    generation_timeout_s,
    rollout_suppress_logits_processor,
    run_bounded_generation,
    truncate_at_closing_fence,
)
from training.grpo_utils import (  # noqa: E402
    DEGENERATE_POLICY_REASON,
    INVALID_OR_NOISY,
    MASTERED_REPLAY,
    MODEL_JUDGE_DIMENSIONS,
    REPAIR_SFT,
    RL_ROUTES,
    AdaptiveKLState,
    AdaptiveTemperatureState,
    CircuitBreakerState,
    FrontierRouter,
    RunningMAD,
    TaskCurriculum,
    append_grpo_metric,
    append_grpo_metric_jsonl,
    append_repair_queue_record,
    blend_comprehensive_reward,
    build_grpo_metrics_payload,
    build_grpo_step_record,
    build_judge_diagnostics_record,
    build_mixture_weights,
    build_reward_breakdown,
    candidate_advantage_dispersion,
    chunked_log_probs_and_entropy,
    count_repair_conversions,
    estimate_detail_budget,
    extract_behavior_hints_from_test_source,
    judge_composite_score,
    leave_one_out_advantages,
    load_grpo_step_metrics_jsonl,
    normalize_group_rewards,
    old_sampled_kl,
    policy_update_signal_magnitude,
    resolve_entropy_pos_cap,
    restore_router_from_record,
    reward_signal_stats,
    sapo_loss_metrics,
    sequence_ratio_stats,
    should_queue_flat_all_fail,
    stable_grpo_loss,
    stable_gspo_loss_metrics,
    summarize_python_interface,
)
from training.model_backend import run_text_forward_preflight  # noqa: E402
from training.model_family_preflight import trainer_backend_preflight_block  # noqa: E402
from training.prompt_normalizer import normalize_prompt  # noqa: E402
from training.qwen_sft_peft import (  # noqa: E402
    TextPreprocessorBackend,
    _visible_npu_indices,
    apply_selective_training_controls,
    build_balanced_npu_layer_device_map,
    collect_trainable_parameters,
    load_text_preprocessor_backend,
    probe_model_runtime_compat,
    resolve_lora_target_modules,
)
from training.research_plugins import load_research_methods, summarize_methods  # noqa: E402
from training.sidecar_liveness import (  # noqa: E402
    ALARM_MARKER,
    alarm_line,
    check_sidecar_liveness,
    default_sidecar_log_path,
)
from training.teacher_free_repair import (  # noqa: E402
    teacher_free_self_repair,
)
from training.text_preprocessor_backend import (  # noqa: E402
    build_supervised_text_example,
    pad_supervised_text_batch,
)

# ── Soft-resume (2026-08-25, lane #20) ─────────────────────────────────────
# resume_state.json is the trainer's soft-resume snapshot: written atomically
# at every completed-step boundary AND on the SIGTERM final save, so a relaunch
# with --resume-state + --adapter-init continues the exact curriculum/router/
# temperature/trust-region/repair state instead of restarting the curriculum.
RESUME_STATE_FILENAME = "resume_state.json"
RESUME_STATE_VERSION = 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model-name", required=True)
    p.add_argument(
        "--adapter-init",
        default=None,
        help="Optional PEFT adapter directory to continue from before GRPO updates.",
    )
    p.add_argument("--tasks-dir", default="evals/tasks")
    p.add_argument(
        "--resume-from",
        default=None,
        help="Path to a previous grpo_step_metrics.jsonl to resume from (warm restart).",
    )
    p.add_argument(
        "--resume-state",
        default=None,
        help="Path to a resume_state.json from a paused run (SOFT-RESUME, 2026-08-25 "
        "lane #20). Requires --adapter-init so the restored curriculum/router/temp "
        "state always matches the resumed weights. Continues the step counter "
        "(next step = state.step + 1), curriculum EMA/task-seen, router/mix state, "
        "adaptive temperature ladder, trust-region count + scaled LR, and re-seeds "
        "the repair-converted ledger. The metrics file appends instead of "
        "overwriting.",
    )
    p.add_argument(
        "--benchmark-file",
        default=None,
        help="Optional text file with task ids to include; '#' comments are ignored.",
    )
    p.add_argument(
        "--domain-filter",
        nargs="*",
        default=None,
        help="Optional domain allowlist, for example --domain-filter quantum.",
    )
    p.add_argument("--output-dir", default="outputs/grpo-v1")
    p.add_argument("--device", default="cpu")
    p.add_argument("--group-size", type=int, default=8, help="Solutions per prompt")
    p.add_argument(
        "--max-adaptive-group",
        type=int,
        default=8,
        help="Cap on the posterior router's recommended group size (16 was the ASI2 stall trigger).",
    )
    p.add_argument(
        "--min-group-size",
        type=int,
        default=1,
        help="2026-08-27 (r19, user binding): HARD FLOOR on the GROUP size — "
        "every round rolls out AT LEAST this many candidates. Default 1 = inert "
        "(prior adaptive behavior). Launch with --min-group-size 8 for 8/round.",
    )
    p.add_argument("--grpo-steps", type=int, default=100)
    p.add_argument("--lr", type=float, default=1e-5)
    p.add_argument("--kl-coeff", type=float, default=0.05, help="KL penalty coefficient")
    p.add_argument(
        "--inner-epochs",
        type=int,
        default=2,
        help=(
            "Number of optimizer steps per rollout group. One is valid and has a nonzero "
            "policy-gradient at ratio=1 because the ratio/gate remains differentiable with "
            "respect to current log-probabilities. Values >1 reuse the rollout for extra "
            "updates but cost another gradient-enabled forward per completion."
        ),
    )
    p.add_argument(
        "--temperature",
        type=float,
        default=1.0,
        help="Sampling temperature. NOTE: with temperature != 1.0 the loss must "
        "compute ratios under the transformed behavior policy, otherwise the "
        "policy-gradient estimate is biased (review finding 2026-08-05).",
    )
    p.add_argument(
        "--adaptive-temp-step",
        type=float,
        default=0.15,
        help="Per-skip temperature escalation factor. Effective temp = min(base * (1 + step * consecutive_skips), max).",
    )
    p.add_argument(
        "--adaptive-temp-max",
        type=float,
        default=1.3,
        help="Maximum sampling temperature after adaptive escalation. 2026-08-25: "
        "default aligned to TEMP_ESCALATION_CEILING (1.3) so the launch_config "
        "echo is truthful — the clamp already capped any higher value, so no "
        "behavior change (launchers pass their own explicit values).",
    )
    p.add_argument("--max-new-tokens", type=int, default=2048)
    p.add_argument(
        "--no-fence-stop-marker",
        action="store_false",
        dest="fence_stop_marker",
        default=True,
        help="Do not append the synthetic EOS stop marker to fence-closed "
        "rollouts (2026-08-26 r10 termination-training lever; kept on by "
        "default, this flag is for ablations).",
    )
    p.add_argument(
        "--greedy-rollout-fraction",
        type=float,
        default=0.4,
        help="Fraction of each rollout group generated at temperature 0 "
        "(greedy argmax) and graded through the SAME harness/reward path "
        "(2026-08-26 r10 beats-base wave). 0 = current behavior, "
        "byte-identical cold path.",
    )
    p.add_argument(
        "--entropy-floor",
        type=float,
        default=1.5,
        help="Entropy floor (nats, current-policy train-pass entropy): below "
        "it, the per-step entropy-floor penalty engages (2026-08-26 r10 "
        "preventive wave).",
    )
    p.add_argument(
        "--entropy-floor-weight",
        type=float,
        default=0.03,
        help="Weight of the entropy-floor penalty term "
        "weight * max(0, floor - mean entropy). 0 disables the term entirely. "
        "2026-08-27 (research audit T1c): strengthened 0.01 -> 0.03 — the "
        "floor is the anti-collapse preventive layer.",
    )
    p.add_argument(
        "--entropy-token-cap",
        type=int,
        default=256,
        help="Entropy-floor entropy is the mean over the first N COMPLETION "
        "tokens only (2026-08-26 run-8 OOM fix): the differentiable entropy "
        "branch retains per-chunk fp32 tensors in the autograd graph over the "
        "full sequence (~37 GiB for 4 candidates at S=1700, the run-8 59.8 "
        "GiB peak). A floor needs a rough mean, not the full sequence. "
        "0/None = full sequence (legacy, OOM-prone at long completions). "
        "Rollout entropy (degenerate-alarm stats) is never capped.",
    )
    p.add_argument(
        "--no-chunked-recompute-backward",
        action="store_false",
        dest="chunked_recompute_backward",
        default=True,
        help="Disable the chunk-streaming recompute backward for the "
        "chunked-vocab log-prob/entropy pass (2026-08-26 run-9 backward-OOM "
        "fix). Default ON: the backward recomputes p chunk-by-chunk instead "
        "of retaining ~10.9 GiB/candidate of per-chunk fp32 tensors in the "
        "autograd graph (the run-9 58.72/60.96 GiB backward crash). "
        "Keep ON; the flag is for ablations.",
    )
    p.add_argument(
        "--max-adaptive-new-tokens",
        type=int,
        default=None,
        help=(
            "Maximum task-specific rollout budget. The base --max-new-tokens is "
            "retained for short tasks; verified long reference programs receive a "
            "quantized larger cap without exposing reference content to the policy."
        ),
    )
    p.add_argument("--max-seq-length", type=int, default=4096)
    p.add_argument(
        "--train-pass-max-seq-length",
        type=int,
        default=2048,
        help=(
            "Cap the TOTAL train-pass (current-policy) sequence length to this "
            "many tokens. The SAPO token loss then covers at most the first N "
            "tokens of each candidate; the completion tail beyond the cap is "
            "excluded from the update. Rollout log-probs (old policy), eval and "
            "reward stay on the FULL sequence. The prompt is never truncated: "
            "if the prompt itself exceeds the cap the cap becomes a no-op for "
            "that candidate. 0 disables the cap. 2026-08-25 OOM fix (run-4): "
            "max-length completions (4x2048, seq 3072) blew the grad-enabled "
            "train forward's activation peak on the lm_head card."
        ),
    )
    p.add_argument(
        "--npu-device-map",
        choices=["auto", "balanced-layers"],
        default="auto",
        help="Shard model layers across the rank's visible NPUs (single-process launch); required for 27B+ on 60GB 910B cards.",
    )
    p.add_argument(
        "--npu-max-memory-gib",
        type=int,
        default=54,
        help="Per-NPU max_memory GiB with --npu-device-map balanced-layers.",
    )
    p.add_argument("--log-steps", type=int, default=5)
    p.add_argument("--lora-rank", type=int, default=8)
    p.add_argument("--lora-alpha", type=int, default=16)
    p.add_argument(
        "--target-modules",
        nargs="*",
        default=None,
        help="Optional explicit LoRA target module suffixes. Defaults to auto-discovery from the loaded model.",
    )
    p.add_argument(
        "--target-module-regex",
        nargs="*",
        default=None,
        help="Optional regex patterns matched against full module names for router-only or expert-specific LoRA targeting.",
    )
    p.add_argument(
        "--trainable-param-regex",
        nargs="*",
        default=None,
        help="Optional regex allowlist for trainable parameter names. Non-matching trainable params are frozen.",
    )
    p.add_argument(
        "--freeze-param-regex",
        nargs="*",
        default=None,
        help="Optional regex denylist for parameter names to freeze after allowlist filtering.",
    )
    p.add_argument("--reward-pass-weight", type=float, default=0.6)
    p.add_argument("--reward-syntax-weight", type=float, default=0.1)
    p.add_argument("--reward-interface-weight", type=float, default=0.15)
    p.add_argument("--reward-verifier-weight", type=float, default=0.15)
    p.add_argument(
        "--reward-brevity-weight",
        type=float,
        default=0.05,
        help="Weight for brevity reward; 2026-08-27 (research audit P5): a "
        "small positive counterweight against length-degenerate outputs "
        "(run-5 prompt-echo is the brevity-like collapse class); 0 disables.",
    )
    p.add_argument(
        "--reward-import-hygiene-weight",
        type=float,
        default=0.05,
        help="Penalty weight for invented non-stdlib imports on single-file tasks.",
    )
    p.add_argument(
        "--crash-progress-credit",
        action="store_true",
        default=False,
        help="B-232 (2026-09-14): a candidate that crashed AFTER producing "
        "numeric evidence earns graded credit capped at 0.3 (strictly below "
        "the 0.5 near-miss band) instead of hard 0. Default off preserves the "
        "pinned crash contract; enable when groups sit at hard 0 and the LOO "
        "advantage collapses (all-fail flat-skip).",
    )
    p.add_argument(
        "--brevity-target-lines",
        type=int,
        default=40,
        help="Target line count for full brevity reward.",
    )
    p.add_argument("--reward-detail-budget-cap", type=int, default=8)
    p.add_argument("--advantage-clip", type=float, default=2.5)
    p.add_argument("--ratio-clip-log-delta", type=float, default=8.0)
    p.add_argument(
        "--top-p",
        type=float,
        default=1.0,
        help="Nucleus sampling threshold. Default 1.0 for sampling-policy "
        "consistency with the loss's raw-model ratios (review finding 2026-08-05).",
    )
    p.add_argument(
        "--overwrite-output-dir",
        action="store_true",
        default=False,
        help="Allow overwriting an existing output dir with prior step metrics.",
    )
    # ── FV-GSPO (frontier-verifier GSPO): see docs/frontier-verifier-gspo-design-2026-08-04.md ──
    p.add_argument(
        "--loss-mode",
        choices=["grpo", "gspo", "gspo_ln", "sapo"],
        default="gspo",
        help="'grpo' keeps the old unclipped sequence-ratio loss (ablation baseline); "
        "'gspo' uses the GSPO sequence-level clipped proximal objective; "
        "'gspo_ln' is the LUSPO-style length-neutral variant (review 2026-08-05 #3): "
        "each surrogate is multiplied by w_i = min(|y_i|/L_reference, w_max) to "
        "neutralize the length bias of the sequence-mean ratio.",
    )
    p.add_argument(
        "--ln-reference-length",
        type=float,
        default=256.0,
        help="L_reference for the length-neutral surrogate weight.",
    )
    p.add_argument(
        "--ln-max-weight",
        type=float,
        default=4.0,
        help="w_max cap on the length multiplier (prevents one very long "
        "candidate from dominating).",
    )
    p.add_argument(
        "--gspo-clip-low",
        type=float,
        default=3e-4,
        help="Lower GSPO sequence-ratio clip (27B sweep 1e-4..1e-3; 35B start 3e-4). "
        "GSPO ratios differ by orders of magnitude from token PPO ratios, so do NOT "
        "copy DAPO's 0.2/0.28 values.",
    )
    p.add_argument(
        "--gspo-clip-high",
        type=float,
        default=4e-4,
        help="Upper GSPO sequence-ratio clip (default 1.3 * gspo-clip-low; 35B start 4e-4).",
    )
    p.add_argument(
        "--numerical-log-ratio-clip",
        type=float,
        default=8.0,
        help="Wide log-ratio clamp kept only for finite exponentiation; the proximal "
        "objective is controlled by gspo-clip-low/high, not by this value.",
    )
    # ── trust region (review 2026-08-05, Design B) ──
    # In the synchronous one-rollout-per-step implementation the pre-update
    # sequence ratio is 1 by construction, so GSPO clipping cannot constrain
    # the update. Instead the update is taken, the post-update ratio/KL is
    # measured on the same rollouts, and the update is rejected (or the LR
    # scaled) when the trust region is violated.
    p.add_argument(
        "--no-trust-region",
        action="store_false",
        dest="trust_region_enabled",
        default=True,
        help="Disable the post-update trust-region check (kept for ablations).",
    )
    p.add_argument("--trust-region-max-seq-kl", type=float, default=0.05)
    p.add_argument("--trust-region-max-clip-fraction", type=float, default=0.50)
    p.add_argument(
        "--trust-region-min-lr",
        type=float,
        default=5e-6,
        help="Minimum learning rate retained by repeated scale_lr trust-region violations.",
    )
    p.add_argument(
        "--trust-region-max-violations",
        type=int,
        default=6,
        help="B-224 guard (2026-09-14): when the cumulative post-update "
        "trust-region violation count reaches this many, fire a "
        "trust_region_bleed_alarm + recommend-stop instead of silently "
        "halving the LR forever. A sustained false-violation loop (measured "
        "live: LR 2.5e-05 -> 1/16 over ~12 steps) must halt the run and "
        "surface for diagnosis, not drain the LR to an inert 1/16.",
    )
    p.add_argument(
        "--trust-region-dump",
        action="store_true",
        default=False,
        help="B-224 instrumenter (2026-09-14): on a trust-region violation, "
        "dump per-candidate post_token_count (train-kept) / old_token_count "
        "(rollout full) / old mean / post mean / alignment mode to "
        "<output>/trust_region_dump.jsonl so the false-violation mechanism "
        "can be root-caused from a live step without a code change.",
    )
    p.add_argument(
        "--trust-region-on-violation",
        choices=["reject", "scale_lr"],
        default="reject",
        help="'reject' restores the pre-update parameters and optimizer state; "
        "'scale_lr' keeps the update but halves the learning rate.",
    )
    p.add_argument(
        "--trust-region-resume-fresh",
        action="store_true",
        default=False,
        help="B-224 (2026-09-14): on a soft-resume, do NOT replay the snapshot's "
        "halved optimizer LR and violation count. After a bleed alarm the false "
        "ladder must not be re-entered: the run starts at --lr with count 0. "
        "Default off preserves in-family resume semantics.",
    )
    p.add_argument(
        "--advantage-mode",
        choices=["loo", "group_std"],
        default="loo",
        help="'loo' is the FV-GSPO Dr.GRPO leave-one-out advantage (no per-task "
        "std normalization); 'group_std' reproduces the legacy per-group "
        "normalization for the ablation baseline.",
    )
    p.add_argument(
        "--loo-advantage-scale",
        choices=["none", "shared_mad"],
        default="none",
        help="Dr.GRPO leave-one-out advantages without per-task standard-deviation "
        "normalization. 'shared_mad' optionally divides by one fixed running MAD "
        "shared across tasks; 'none' keeps raw leave-one-out advantages.",
    )
    p.add_argument("--frontier-threshold", type=float, default=0.10)
    p.add_argument(
        "--difficulty-manifest",
        default=None,
        help="2026-08-27 (T1b): JSON file with the lineage difficulty manifest "
        "{'hard_tasks': [...], 'difficulty_scale': 0.25} — v8 tasks that never "
        "passed a first-visit probe across run-4..7 get a never-zero cold-start "
        "sampling discount until the first pass>0 in the run. Absent => "
        "pre-manifest behavior.",
    )
    p.add_argument("--mastered-threshold", type=float, default=0.95)
    p.add_argument("--mix-targeted", type=float, default=0.5)
    p.add_argument("--mix-neighbor", type=float, default=0.25)
    p.add_argument("--mix-replay", type=float, default=0.25)
    p.add_argument(
        "--adaptive-mixture",
        action="store_true",
        default=False,
        help="Adapt mixture masses to router state (review 2026-08-05 #11): "
        "targeted mass rises with frontier yield (0.25-0.75), replay mass "
        "shrinks when mastered tasks repeatedly produce flat groups.",
    )
    p.add_argument("--neighbor-window", type=int, default=10)
    p.add_argument(
        "--repair-queue-path",
        default=None,
        help="JSONL queue for all-fail groups (execution-grounded repair candidates). "
        "Defaults to <output-dir>/repair_queue.jsonl.",
    )
    p.add_argument(
        "--repair-converted-jsonl",
        default=os.environ.get("REPAIR_CONVERTED_JSONL"),
        help="Optional JSONL written by the repair SFT/DPO stage recording verified "
        "conversions; used by the all-fail-without-repair circuit breaker. "
        "Defaults to $REPAIR_CONVERTED_JSONL, then "
        "<output-dir>/repair_stage/repair_converted.jsonl.",
    )
    # Guardian alarm 8 (2026-08-26): repair-sidecar liveness guard. Runs 11/12
    # stopped via all_fail_without_repair because the sidecar died SILENTLY at
    # launch (SIGKILL is untrappable) and the queue starved. The guard checks
    # pidfile + log-heartbeat each step and alarms LOUDLY when not alive.
    p.add_argument(
        "--repair-sidecar-pidfile",
        default=None,
        help="Repair-sidecar pidfile for the liveness guard "
        "(default <output-dir>/repair_sidecar.pid).",
    )
    p.add_argument(
        "--repair-sidecar-log",
        default=None,
        help="Repair-sidecar log for heartbeat liveness (default derived from "
        "output-dir; see training/sidecar_liveness.py).",
    )
    p.add_argument(
        "--repair-sidecar-max-log-age",
        type=int,
        default=300,
        help="Seconds a sidecar log may be silent before the heartbeat guard "
        "declares it stale/wedged (default 300).",
    )
    p.add_argument(
        "--coverage-json",
        default=None,
        help="Optional JSON mapping task_id -> coverage need from the training-only "
        "skill/failure inventory (WeaknessReport-style cells).",
    )
    p.add_argument(
        "--circuit-breaker-window",
        type=int,
        default=10,
        help="Steps per evaluation window for circuit breakers; a breaker trips only "
        "after persisting across two windows.",
    )
    p.add_argument(
        "--circuit-breaker-clip-fraction-limit",
        type=float,
        default=0.50,
        help="Clip-fraction breaker threshold (mean clip_total_fraction over a window). "
        "Recalibrated 2026-08-20: 0.50 trips whenever per-sequence ratios reach the "
        "GSPO clip edge (the normal saturated-PPO regime at LR 2e-5), halting the run "
        "after ~20 steps. The launch sets 0.90 so the breaker only catches real "
        "learning collapse, not routine clipping.",
    )
    # ── adaptive KL controller (design §4: capability preservation) ──
    p.add_argument(
        "--adaptive-kl",
        action="store_true",
        default=False,
        help="Adapt the KL penalty beta from measured sequence KL: rise when KL "
        "drifts beyond target, fall when far below. Keeps the policy close to "
        "the anchor (accepted checkpoint) until regression gates pass.",
    )
    p.add_argument("--kl-target", type=float, default=0.05)
    p.add_argument("--kl-up-rate", type=float, default=1.2)
    p.add_argument("--kl-down-rate", type=float, default=0.9)
    p.add_argument("--kl-min", type=float, default=1e-4)
    p.add_argument("--kl-max", type=float, default=0.5)
    p.add_argument("--kl-beta-init", type=float, default=0.005)
    p.add_argument(
        "--no-stop-on-severe-breaker",
        action="store_false",
        dest="stop_on_severe_breaker",
        default=True,
        help="Do not halt training when a severe in-loop circuit breaker trips "
        "(non-finite loss, clip fraction above 50 percent, entropy collapse, "
        "all-fail without repair).",
    )
    p.add_argument("--logit-clip", type=float, default=50.0)
    p.add_argument(
        "--min-reward-std",
        type=float,
        default=0.05,
        help="Minimum optimization-signal magnitude required to update: RMS of final clipped "
        "LOO advantages in canonical loo mode; legacy max total/component reward std in "
        "group_std ablation mode.",
    )
    p.add_argument(
        "--min-rms-for-update",
        type=float,
        default=None,
        help="Warm-continue fix: when advantage RMS exceeds this threshold, the "
        "flat_candidate_dispersion gate does NOT hard-zero the magnitude even with "
        "pass_rate=0 and low dispersion. Set to 0.01 for warm-continue runs to "
        "preserve partial-credit gradient signal. None = original s26 gate behavior.",
    )
    p.add_argument("--curriculum-ema-decay", type=float, default=0.9)
    p.add_argument("--curriculum-min-weight", type=float, default=0.05)
    p.add_argument("--curriculum-uncertainty-bonus", type=float, default=0.35)
    p.add_argument("--research-methods", nargs="*", default=[])
    p.add_argument(
        "--quantum-priority",
        type=float,
        default=1.5,
        help="Sampling multiplier for quantum tasks in the adaptive curriculum.",
    )
    # ── self-evaluation: the model judges its own generated code ──
    p.add_argument(
        "--self-evaluation-enabled",
        action="store_true",
        default=False,
        help="Enable self-evaluation: the model judges its own generated code samples.",
    )
    p.add_argument(
        "--reward-self-eval-weight",
        type=float,
        default=0.25,
        help="Weight for the self-evaluation reward component.",
    )
    p.add_argument(
        "--self-eval-judge-temperature",
        type=float,
        default=0.3,
        help="Temperature for the self-judge generation.",
    )
    p.add_argument(
        "--self-eval-judge-max-tokens",
        type=int,
        default=512,
        help="Max tokens for the self-judge response.",
    )
    # ── comprehensive frozen-judge scoring (base model / older adapters) ──
    p.add_argument(
        "--model-judge-enabled",
        action="store_true",
        default=False,
        help="Enable per-dimension comprehensive scoring by a FROZEN judge: the base "
        "model (or an older accepted adapter via --judge-adapter-path), never the "
        "current training policy. Reward weights stay zero until calibration passes.",
    )
    p.add_argument(
        "--judge-model-path",
        default=None,
        help="Frozen judge base model. Defaults to the training model path.",
    )
    p.add_argument(
        "--judge-adapter-path",
        default=None,
        help="Optional OLDER accepted adapter checkpoint to evaluate samples with "
        "(frozen; do not use the current training adapter as its own judge).",
    )
    p.add_argument(
        "--judge-device",
        default="cpu",
        help="Device for the frozen judge (cpu by default; a spare npu card when "
        "available, e.g. npu:2 on a 4-card env).",
    )
    p.add_argument(
        "--model-judge-max-tokens",
        type=int,
        default=256,
        help="Max tokens for one judge evaluation.",
    )
    p.add_argument(
        "--model-judge-temperature",
        type=float,
        default=0.0,
        help="Judge sampling temperature (greedy default for stability).",
    )
    p.add_argument(
        "--judge-calibration",
        default=None,
        help="Path to judge_calibration.json (from scripts/calibrate_model_judge.py): "
        "enables per-dimension reward weights only for dimensions whose agreement "
        "with executable anchors passed calibration. Until then weights are zero.",
    )
    p.add_argument(
        "--judge-diagnostics-path",
        default=None,
        help="Per-candidate judge diagnostics JSONL (executable anchors + judge "
        "dimension scores) consumed by scripts/calibrate_model_judge.py. Defaults "
        "to <output-dir>/judge_diagnostics.jsonl when the judge is enabled.",
    )
    # ── reward composition (user decision 2026-08-05: not executable-dominated) ──
    p.add_argument(
        "--reward-mode",
        choices=["p_dominant", "comprehensive", "tiered"],
        default="p_dominant",
        help="'p_dominant' keeps executable tests authoritative (P clamps failing "
        "candidates below every passing one; FV-GSPO default and ablation "
        "baseline). 'comprehensive' makes the reward the comprehensive score "
        "R = w_P*P + w_S*S + w_J*J with configurable masses below — the pass "
        "term no longer dominates, and the frozen judge contributes its mass "
        "once any dimension passes calibration. 'tiered' (review 2026-08-05 #5, "
        "recommended) uses the constrained hierarchy "
        "R = (1-P)*min(0.95, Q_progress) + P*(1 + alpha*Q_efficiency + gamma*Q_quality): "
        "any passer outranks any failure (execution authoritative), failures stay "
        "learnable via Q_progress, and passers are differentiated by efficiency/"
        "quality (judge dims, calibration-gated).",
    )
    # 2026-08-26 (r17, research memo): recommended masses w_P=0.50, w_S=0.40,
    # w_J=0.10 — the judge mass is calibration-gated (no calibration file ->
    # judge contributes exactly 0 and the masses renormalize over P+S).
    p.add_argument("--reward-pass-mass", type=float, default=0.50)
    p.add_argument("--reward-shaped-mass", type=float, default=0.40)
    p.add_argument("--reward-judge-mass", type=float, default=0.10)
    p.add_argument(
        "--reward-normalization",
        choices=["none", "minmax"],
        default="none",
        help="2026-08-27 (r19, user binding): normalize the RAW reward scores "
        "across all candidates of the group before the GRPO/SAPO advantage "
        "computation. 'minmax' scales the group to [0,1]; 'none' (default, "
        "inert) leaves the raw scores byte-identical to the prior path.",
    )
    p.add_argument(
        "--batch-comparative-judge",
        action="store_true",
        help="2026-08-27 (r19, user binding): score ALL group candidates in ONE "
        "forward, with the ACTIVE training model judging its own rollouts "
        "comparatively (vs the per-candidate independent frozen judge). "
        "Default OFF = inert (per-candidate judge path).",
    )
    p.add_argument(
        "--judge-dp4-endpoint",
        default="",
        help="2026-08-27 (r19, user directive): when set, the batch COMPARATIVE "
        "judge is the Huanxin dp4 (deepseek-v4-flash) model served by this "
        "Anthropic-compatible endpoint (e.g. http://127.0.0.1:55080 — the "
        "proxy used by 'claude -p huanxin -m dp4') instead of the in-process "
        "training model. Empty = in-process self-judge (inert default).",
    )
    p.add_argument(
        "--judge-dp4-model",
        default="dp4",
        help="Model name sent to the dp4 endpoint (default: dp4 / deepseek-v4-flash).",
    )
    p.add_argument(
        "--judge-dp4-max-tokens",
        type=int,
        default=4096,
        help="2026-08-27 (critical review C1): token budget for the dp4 batch "
        "comparative judge. INDEPENDENT of --model-judge-max-tokens (256, the "
        "frozen per-candidate judge) — an 8-candidate comparative JSON needs "
        "~280+ tokens, so 256 silently truncated every batch and made the "
        "judge absent (w_J=0 every step).",
    )
    p.add_argument("--tiered-alpha", type=float, default=0.10)
    p.add_argument("--tiered-gamma", type=float, default=0.10)
    # ── teacher-free self-repair rollout (Teacher-Free FV-GSPO plan §3/§8) ──
    # Failed candidates + real harness error logs feed a new rollout round using
    # the policy model itself (no reference/teacher model). 0 disables.
    p.add_argument(
        "--self-repair-rounds",
        type=int,
        default=0,
        help="Teacher-free self-repair rounds per failed candidate (plan §8: use "
        "2). 0 disables. When >0, a failing code is re-rolled by the policy with "
        "its exact harness errors appended and accepted only if it passes the "
        "hidden tests, else the original failed sample is retained for GRPO.",
    )
    p.add_argument(
        "--harness-timeout-seconds",
        type=int,
        default=300,
        help="Per-candidate harness+verifier subprocess timeout (2026-08-21: "
        "candidate eval now runs in a FRESH interpreter subprocess so candidate "
        "imports (e.g. qiskit parallel_map) cannot fork/deadlock the NPU-sharded "
        "trainer process).",
    )
    p.add_argument(
        "--sapo-tau-pos",
        type=float,
        default=1.0,
        help="SAPO (arXiv:2511.20347) positive-advantage gate temperature: "
        "g(r)=(4/tau)*sigmoid(tau*(r-1)); larger tau -> faster smooth decay.",
    )
    p.add_argument(
        "--sapo-tau-neg",
        type=float,
        default=1.05,
        help="SAPO negative-advantage gate temperature (recommended > tau_pos for stability).",
    )
    # ── checkpoint interval (periodic adapter save to disk) ──
    p.add_argument(
        "--checkpoint-interval-seconds",
        type=int,
        default=7200,
        help="Save adapter checkpoint to disk every N seconds (0 = only at end).",
    )
    return p.parse_args(argv)


def load_requested_task_ids(path: str | None) -> set[str] | None:
    if not path:
        return None
    task_ids = set()
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        task_ids.add(line)
    if not task_ids:
        raise ValueError(f"No task ids found in {path}")
    return task_ids


def load_reference_code_char_counts(path: str | Path | None) -> dict[str, int]:
    """Load qc-NNNN reference lengths from a manifest's verified source lineage.

    Only lengths are returned. Reference code is never added to prompts, rewards,
    or rollout records. The source SHA remains enforced by the ASI3 launch gate.
    """
    if not path:
        return {}
    manifest = Path(path)
    lines = manifest.read_text(encoding="utf-8").splitlines()
    prefix = "# source="
    source_line = next((line for line in lines if line.startswith(prefix)), None)
    if source_line is None or " sha256=" not in source_line:
        return {}
    source_text = source_line[len(prefix) :].rsplit(" sha256=", 1)[0]
    source_rel = Path(source_text)
    candidates = [manifest.parent / source_rel, ROOT / source_rel]
    source_path = next((candidate for candidate in candidates if candidate.is_file()), None)
    if source_path is None:
        raise FileNotFoundError(f"manifest reference source missing: {source_text}")
    # Integrity manifests may point to another task-ID manifest rather than a
    # distillation JSONL. Such lineages have no hidden reference-code lengths;
    # use the fixed base token budget instead of trying to JSON-decode IDs.
    if source_path.suffix.lower() != ".jsonl":
        return {}
    result: dict[str, int] = {}
    for index, raw_line in enumerate(source_path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip():
            continue
        record = json.loads(raw_line)
        code = record.get("code")
        if isinstance(code, str):
            result[f"qc-{index:04d}"] = len(code)
    return result


def adaptive_generation_token_budget(
    reference_code_chars: int | None,
    *,
    base_tokens: int,
    max_tokens: int,
) -> int:
    """Choose a bounded budget using hidden verified-reference length only.

    Empirical ASI3 code rollouts average roughly 2.9-3.4 characters/token.
    Budgeting at 2.5 characters/token provides completion margin, then rounds
    to 128-token buckets so short tasks stay cheap and long scripts finish.
    """
    base = max(1, int(base_tokens))
    ceiling = max(base, int(max_tokens))
    if reference_code_chars is None or int(reference_code_chars) <= 0:
        return base
    estimated = math.ceil(int(reference_code_chars) / 2.5)
    quantized = int(math.ceil(estimated / 128.0) * 128)
    return min(ceiling, max(base, quantized))


def discover_tasks(
    tasks_dir: Path,
    requested_task_ids: set[str] | None = None,
    allowed_domains: set[str] | None = None,
) -> list[dict]:
    tasks = []
    found_ids: set[str] = set()
    for domain_dir in sorted(tasks_dir.iterdir()):
        if not domain_dir.is_dir():
            continue
        for task_dir in sorted(domain_dir.iterdir()):
            if not task_dir.is_dir():
                continue
            task_json = task_dir / "task.json"
            tests_py = task_dir / "tests.py"
            if task_json.exists() and tests_py.exists():
                with open(task_json) as f:
                    meta = json.load(f)
                task_id = meta.get("id", task_dir.name)
                domain = meta.get("domain")
                if requested_task_ids is not None and task_id not in requested_task_ids:
                    continue
                if allowed_domains is not None and domain not in allowed_domains:
                    continue
                found_ids.add(task_id)
                tasks.append({"meta": meta, "task_dir": task_dir, "tests_py": tests_py})
    if requested_task_ids is not None:
        # 2026-09-01 (bug-hunter mechanism 7, required_files gate): a
        # REQUESTED task id with no discoverable files (missing dir, missing
        # task.json/tests.py) was silently dropped — the manifest said "train
        # on these N tasks" and the trainer trained on N-k with no signal.
        # Fail-closed listing the missing ids.
        missing = sorted(requested_task_ids - found_ids)
        if missing:
            raise ValueError(
                "Requested task ids missing from tasks dir "
                f"({tasks_dir}): {', '.join(missing)} — refusing to start with "
                "a silently shrunk training set"
            )
    return tasks


def load_test_harness(tests_py: Path):
    spec = importlib.util.spec_from_file_location(f"tests_{uuid.uuid4().hex[:6]}", str(tests_py))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def extract_behavior_hints(tests_path: Path) -> list[str]:
    if not tests_path.exists():
        return []
    # 2026-09-01 PROMPT-INTEGRITY audit: the prompt path suppresses hints that
    # pin decisive numeric answers (exact expected values / answer bounds);
    # structural sizes, shapes, traces, norms and tolerances survive.
    return extract_behavior_hints_from_test_source(
        tests_path.read_text(encoding="utf-8"), cap=6, suppress_decisive_numeric=True
    )


def task_behavior_hints(task: dict) -> list[str]:
    """Return public prompt hints without leaking generated checker internals."""
    meta = task["meta"]
    explicit = meta.get("public_behavior_hints")
    if isinstance(explicit, list):
        return [str(hint).strip() for hint in explicit if str(hint).strip()][:6]
    category = str(meta.get("category", ""))
    if meta.get("derive_behavior_hints_from_tests") is False or category.startswith("distill_v3"):
        return []
    return extract_behavior_hints(task["tests_py"])


def summarize_candidate_interface(candidate_path: Path) -> list[str]:
    if not candidate_path.exists():
        return []
    return summarize_python_interface(candidate_path.read_text(encoding="utf-8"))


DISTILL_QUANTUM_IMPORT_ROOTS = frozenset(
    {
        "braket",
        "cirq",
        "matplotlib",
        "networkx",
        "numpy",
        "pennylane",
        "projectq",
        "pyquil",
        "qiskit",
        "qiskit_aer",
        "qutip",
        "qulacs",
        "scipy",
        "stim",
        "sympy",
    }
)


def build_task_runtime_context(task: dict, *, detail_budget_cap: int) -> dict[str, Any]:
    """Derive runtime-only task fields once so reward and prompt code share the same view."""
    meta = task["meta"]
    task_id = meta.get("id", task["task_dir"].name)
    candidate_file = meta.get("candidate_file")
    required_interface = (
        summarize_candidate_interface(task["task_dir"] / candidate_file) if candidate_file else []
    )
    behavior_hints = task_behavior_hints(task)
    test_source = task["tests_py"].read_text(encoding="utf-8")
    detail_budget = max(
        estimate_detail_budget(test_source, cap=detail_budget_cap),
        min(detail_budget_cap, max(1, len(behavior_hints))) if behavior_hints else 1,
    )
    raw_allowed_import_roots = meta.get("allowed_import_roots", [])
    allowed_import_roots = [
        root.strip() for root in raw_allowed_import_roots if isinstance(root, str) and root.strip()
    ]
    # Quantum questions intentionally require external framework imports, while
    # their generated metadata historically left the allowlist empty. Penalizing
    # qiskit/cirq/pennylane as invented modules pushes the policy away from the
    # very APIs the task requests.
    #
    # B-205 (tick #445): this gate used to key on category == "distill_v3" alone.
    # The live RL family (quantum_rl_v2_*, 56 tasks) declares
    # category="algorithm_implementation" with domain="quantum" and no allowlist
    # of its own, so the merge never fired, only stdlib roots were permitted, and
    # import_hygiene scored 0.0 for EVERY candidate -- including a flawless one --
    # making 0.05 of reward mass structurally unearnable. `domain` is the field
    # that actually expresses the requirement, so key on it as well.
    if (
        str(meta.get("category", "")).startswith("distill_v3")
        or str(meta.get("domain", "")) == "quantum"
    ):
        allowed_import_roots = sorted(set(allowed_import_roots) | DISTILL_QUANTUM_IMPORT_ROOTS)
    candidate_files = meta.get("candidate_files")
    if candidate_files is None and candidate_file:
        candidate_files = [candidate_file]
    return {
        "task_id": task_id,
        "required_interface": required_interface,
        "behavior_hints": behavior_hints,
        "detail_budget": detail_budget,
        "single_file_expected": len(candidate_files or []) <= 1,
        "allowed_import_roots": allowed_import_roots,
    }


def build_prompt(task: dict, research_methods: list[Any] | None = None) -> str:
    meta = task["meta"]
    parts: list[str] = []
    if "task_prompt" in meta:
        parts.append(str(meta["task_prompt"]))
    elif "description" in meta:
        parts.append(f"Task: {meta['description']}")
    else:
        parts.append(f"Task: {meta.get('name', task['task_dir'].name)}")

    parts.append(f"Task id: {meta.get('id', task['task_dir'].name)}")
    parts.append(
        f"Domain: {meta.get('domain', 'unknown')}\nCategory: {meta.get('category', 'unknown')}"
    )

    candidate_file = meta.get("candidate_file")
    if candidate_file:
        interface_lines = task.get("required_interface") or summarize_candidate_interface(
            task["task_dir"] / candidate_file
        )
        if interface_lines:
            parts.append(
                "Required interface:\n" + "\n".join(f"- {line}" for line in interface_lines)
            )

    behavior_hints = (
        task["behavior_hints"] if "behavior_hints" in task else task_behavior_hints(task)
    )
    if behavior_hints:
        parts.append(
            "Behavioral requirements:\n" + "\n".join(f"- {line}" for line in behavior_hints)
        )

    if task.get("single_file_expected", False):
        parts.append(
            "Implementation constraints:\n"
            "- Keep the answer self-contained in one Python file.\n"
            "- Do not depend on repository-local helpers or invent non-standard modules."
        )

    parts.append(
        # B-332: aligned with eval's output instructions. The eval says
        # "Implement the requested file. Hidden tests will verify behavior."
        # and "Return only the complete Python source, without markdown fences
        # or explanation." The old "Stop immediately" wording caused EOS-collapse.
        "Write a Python file that satisfies the public task contract; hidden tests will verify it.\n"
        "Return only the final Python code.\n"
        "Return only the candidate file contents.\n"
        "Implement the requested file. Hidden tests will verify behavior.\n"
        "Return only the complete Python source, without markdown fences or explanation."
    )
    prompt = "\n\n".join(parts)
    for method in research_methods or []:
        prompt = method.augment_grpo_prompt(prompt, task=task, stage="grpo")
    # B-329: normalize prompt for train/eval consistency — ensures the
    # required interface is present and the output contract allows
    # complete multi-function implementations.
    candidate_file = meta.get("candidate_file")
    interface_lines = task.get("required_interface") or (
        summarize_candidate_interface(task["task_dir"] / candidate_file) if candidate_file else []
    )
    prompt = normalize_prompt(prompt, required_interface=interface_lines)
    return prompt


SYSTEM_PROMPT = (
    # B-332: aligned with eval's "direct" prompt style (evals/runner/prepare_prompts.py).
    # The previous wording ("You are a careful coding assistant... Return only the final code.")
    # was completely different from eval's system prompt, causing train/eval distribution mismatch
    # that made 11/18 tasks effectively out-of-distribution at eval time.
    # 2026-09-14 history: the previous "Return code only. ... Stop immediately" wording
    # caused EOS-collapse (n=1, ids=[248046]). The eval "direct" style avoids this by
    # saying "Produce only the full contents" (no "stop immediately" suppressor).
    "You are solving a single evaluation task. Produce only the full contents of the requested Python candidate file. "
    "Do not include Markdown fences, explanations, or surrounding commentary unless the task explicitly asks for it. Stop immediately after the final required Python statement. Do not add explanations, tests, examples, or demo code."
)


def filter_generation_inputs(
    model: Any, inputs: Mapping[str, torch.Tensor]
) -> dict[str, torch.Tensor]:
    """Keep only the tokenizer batch fields the model can actually take.

    2026-08-26 (r10, launch-simulator F2): the tokenizer batch dict can carry
    extra fields (token_type_ids, special_tokens_mask, ...) that
    ``model.generate`` forwards unguarded into the model forward — a crash
    for generic-tokenizer fixtures (the real Qwen3.5/3.6 tokenizers never
    emit them, so the failure was latent). Fields are filtered to the model's
    ``model_input_names`` (HF convention; fallback allowlist
    ``{input_ids, attention_mask}`` — the exact set every trainer log-prob
    path already feeds).
    """
    allowed = set(getattr(model, "model_input_names", None) or ())
    if not allowed:
        allowed = {"input_ids", "attention_mask"}
    return {name: tensor for name, tensor in inputs.items() if name in allowed}


def greedy_rollout_count(group_size: int, fraction: float) -> int:
    """Number of greedy (temperature-0) candidates in a mixed rollout group.

    2026-08-26 (r10, manager TOP-PRIORITY wave): a configurable fraction of
    each group is generated at temperature 0 and graded through the SAME
    harness/reward path, so the policy learns under the exact evaluation
    protocol (greedy argmax). fraction 0 → 0 greedy candidates (the current,
    byte-identical cold path). Rounding uses round-half-to-even (Python
    banker's rounding); the count never exceeds the group.
    """
    return min(
        int(round(max(int(group_size), 0) * max(float(fraction), 0.0))), max(int(group_size), 0)
    )


def compute_entropy_floor_penalty(
    entropies: torch.Tensor | None,
    *,
    floor: float,
    weight: float,
) -> torch.Tensor:
    """Differentiable entropy-floor regularizer value.

    2026-08-26 (r10, manager TOP-PRIORITY wave): ``weight * max(0, floor -
    mean(entropies))`` — engaged only below the floor; 0 when disabled
    (weight <= 0), above the floor, or without candidate entropies. The
    tensor is differentiable w.r.t. the entropy source (the current-policy
    train-pass logits), so the term actively pushes low-entropy policies
    back above the floor. The recorded value rides in
    ``loss_breakdown.entropy_floor_penalty`` and the math audit includes it
    in the final-loss identity.
    """
    if weight is None or float(weight) <= 0.0 or entropies is None or entropies.numel() == 0:
        return torch.tensor(0.0, dtype=torch.float32)
    mean_entropy = entropies.float().mean()
    if float(mean_entropy.detach()) >= float(floor):
        return torch.tensor(0.0, dtype=torch.float32)
    gap = (float(floor) - mean_entropy).clamp(min=0.0)
    return float(weight) * gap


def add_entropy_floor_penalty_value(
    total_loss: Any, entropy_floor_penalty_value: float, *, loss_mode: str
) -> Any:
    """Compose the (detached, monitoring) entropy-floor penalty value into
    the final loss EXACTLY ONCE per step (2026-08-26 r15 F5 fix).

    The SAPO branch composes the penalty into its own ``total_loss``
    (loss = accumulated + penalty); this common-tail composition must NOT
    re-add it — ``loss == recomputed + 2*penalty`` broke the documented
    identity and would false-alarm the math auditor exactly during collapse
    episodes (when the floor engages). Non-SAPO modes add it once here.
    """
    if float(entropy_floor_penalty_value) > 0.0 and loss_mode != "sapo":
        return total_loss + float(entropy_floor_penalty_value)
    return total_loss


SELF_EVAL_JUDGE_PROMPT = """You are a quantum computing code reviewer. Evaluate the following code solution
against these criteria on a scale of 0-10 (0 = completely wrong/fails, 10 = perfect):

1. Correctness: Does the algorithm produce the right quantum state / result?
2. Runnability: Will the code execute without errors in a standard quantum SDK environment?
3. Efficiency: Is the circuit depth / gate count / resource usage reasonable for the problem?
4. Code quality: Is it well-structured, readable, and uses proper quantum computing patterns?

First, analyze the code briefly. Then output ONLY a single JSON object with this format:
{{"score": <float 0-10>, "analysis": "<one-line summary>"}}

CODE TO EVALUATE:
```python
{code}
```

TASK CONTEXT:
{task_context}

EVALUATION:"""


def _self_evaluate_code(code: str, task: dict, model, backend, args, device) -> float:
    """Ask the model to judge its own generated code and return a score 0-1."""
    task_desc = task.get("meta", {}).get(
        "description",
        task.get("meta", {}).get("name", str(task.get("task_dir", task.get("task_id", "unknown")))),
    )
    prompt = SELF_EVAL_JUDGE_PROMPT.format(code=code, task_context=task_desc)

    with torch.no_grad():
        # Tokenize
        messages = [
            {"role": "user", "content": prompt},
        ]
        if hasattr(backend, "tokenizer"):
            tokenized_inputs = backend.tokenizer.apply_chat_template(
                messages, tokenize=True, return_tensors="pt", add_generation_prompt=True
            ).to(device)
            input_len = tokenized_inputs.shape[1]
        elif hasattr(backend, "encode_chat"):
            tokenized_ids = backend.encode_chat(messages, add_generation_prompt=True)
            tokenized_inputs = torch.tensor([tokenized_ids], dtype=torch.long, device=device)
            input_len = tokenized_inputs.shape[1]
        else:
            return 0.0

        # Generate judgement
        try:
            outputs = model.generate(
                input_ids=tokenized_inputs,
                max_new_tokens=args.self_eval_judge_max_tokens,
                temperature=args.self_eval_judge_temperature,
                top_p=0.95,
                do_sample=True,
                pad_token_id=backend.tokenizer.pad_token_id
                if hasattr(backend, "tokenizer")
                else getattr(backend, "pad_token_id", 0),
            )
            response_ids = outputs[0][input_len:]
            if hasattr(backend, "tokenizer"):
                response_text = backend.tokenizer.decode(response_ids, skip_special_tokens=True)
            else:
                response_text = backend.decode(response_ids.tolist())
        except Exception:
            return 0.0

    # Parse the score from JSON response
    score = _parse_self_eval_score(response_text)
    return score


COMPREHENSIVE_JUDGE_PROMPT = """You are a strict code evaluator. Score the candidate solution on five dimensions, each a float 0.0-1.0. Use the executable evidence below as the authoritative anchor — do not contradict it.

Dimensions:
- correctness: does the algorithm's logic produce the right result (0.0 if tests fail)?
- runnability: would the code execute without syntax/import/runtime errors?
- result_correctness: do the actual outputs match the expected values?
- efficiency: is runtime / circuit depth / gate count / resource use reasonable for the problem?
- quality: is the code well-structured, readable, and maintainable?

CODE TO EVALUATE:
```python
{code}
```

EXECUTABLE EVIDENCE (authoritative):
{evidence}

TASK CONTEXT:
{task_context}

Output ONLY a JSON object:
{{"correctness_of_intent": 0.0-1.0, "result_correctness": 0.0-1.0, "completeness": 0.0-1.0, "api_correctness": 0.0-1.0, "syntax_validity": 0.0-1.0, "runnability": 0.0-1.0, "parameterization": 0.0-1.0, "numerical_reasoning": 0.0-1.0, "structure_and_naming": 0.0-1.0, "efficiency": 0.0-1.0, "evidence": "one line"}}"""


COMPREHENSIVE_BATCH_JUDGE_PROMPT = """You are a strict code evaluator. There are {n} candidate solutions (Candidate 1..{n}) to the same task. Score ALL {n} candidates TOGETHER, comparing them against each other, on TEN fine-grained dimensions, each a float 0.0-1.0. Fine granularity is ESSENTIAL: candidates differ in small ways and your scores must separate them (identical scores across candidates are a scoring failure). Use the executable evidence per candidate as the authoritative anchor — do not contradict it: a candidate whose tests pass must not be scored below one whose tests fail on the executable dimensions. Each candidate's EXECUTABLE EVIDENCE (authoritative) block overrides any impression formed from the code alone.

Dimensions (per candidate) — score EACH INDEPENDENTLY from its own evidence; a failing test suite must NOT zero unrelated dimensions:
- correctness_of_intent: does the algorithm logic match the task intent?
- result_correctness: do outputs match expected values (evidence-anchored)?
- completeness: all required functions/classes/flows present?
- api_correctness: correct framework API usage (qiskit/cirq/pennylane/stim)?
- syntax_validity: parses without syntax errors?
- runnability: executes without import/runtime errors? Evidence shows any execution => ABOVE 0.0.
- parameterization: correct parameters, scales, qubit counts?
- numerical_reasoning: amplitudes/angles/counts arithmetically right?
- structure_and_naming: clean structure, meaningful names?
- efficiency: circuit depth/gate count/resource use reasonable?

The candidates ARE RELATIVE to each other: distribute the dimension scores so the ranking reflects genuine comparative quality across the 8 candidates, not an independent per-candidate guess.

CANDIDATES (code + executable evidence):
{candidates}

TASK CONTEXT:
{task_context}

Output ONLY a JSON object of the form:
{{"candidate_1": {{"correctness_of_intent": 0.0-1.0, "result_correctness": 0.0-1.0, "completeness": 0.0-1.0, "api_correctness": 0.0-1.0, "syntax_validity": 0.0-1.0, "runnability": 0.0-1.0, "parameterization": 0.0-1.0, "numerical_reasoning": 0.0-1.0, "structure_and_naming": 0.0-1.0, "efficiency": 0.0-1.0}}, ..., "candidate_{n}": {{...}} }}
No other text."""


def _render_batch_judge_candidates(codes, evidences, *, rng=None) -> tuple[str, list[int]]:
    """Render all G candidates (numbered) + their evidence for the batch prompt.

    2026-08-29 (OSS-research adoption): candidate order is RANDOMIZED per call
    and the permutation is returned so parsed scores map back to the original
    indices. Kills LLM-judge position bias (first-presented candidates are
    scored differently; AlpacaEval-style harnesses randomize for this reason).
    """
    n = len(codes)
    order = list(range(n))
    if rng is not None:
        rng.shuffle(order)
    parts = []
    for pos, idx in enumerate(order, start=1):
        parts.append(
            f"Candidate {pos}:\n"
            "```python\n" + str(codes[idx]) + "\n```\n"
            f"EXECUTABLE EVIDENCE: {evidences[idx]}\n"
        )
    return "\n".join(parts), order


def _extract_json_object(text: str) -> str | None:
    """First balanced {...} JSON object, STRING-AWARE: a '}' inside a string
    value must not truncate the match (2026-08-26 review F6)."""
    start = (text or "").find("{")
    if start < 0:
        return None
    depth = 0
    in_string = False
    escaped = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _parse_model_dim_scores(text: str) -> dict[str, float | None] | None:
    """Parse the judge's JSON response into per-dimension scores (0-1)."""

    try:
        matched = _extract_json_object(text or "")
        if not matched:
            return None
        data = json.loads(matched)
    except (json.JSONDecodeError, ValueError, RecursionError):
        # 2026-09-01 (adversarial-judge lane): RecursionError is NOT a
        # ValueError subclass — a pathological judge response (deeply nested
        # braces) escaped this guard and crashed the training loop. Fail-
        # closed: the whole response is unusable -> None (judge-absent).
        return None
    scores: dict[str, float | None] = {}
    for dim in MODEL_JUDGE_DIMENSIONS:
        raw = data.get(dim)
        if isinstance(raw, (int, float)) and not isinstance(raw, bool):
            scores[dim] = min(1.0, max(0.0, float(raw)))
        else:
            scores[dim] = None
    if all(value is None for value in scores.values()):
        return None
    return scores


def effective_group_size(*, recommended: int, max_adaptive_group: int, min_group_size: int) -> int:
    """Resolve the effective GRPO group size (user directive 2026-08-27 r19).

    ``min_group_size`` (default 1) is a HARD FLOOR — the user binds that
    "every round the model should rollout 8 candidates (samples), not 4."
    A floor of 1 is the inert default (prior behavior: the router's adaptive
    recommendation, capped by ``max_adaptive_group``, passes through exactly).
    A floor of 8 therefore overrides the router's fresh-task recommendation
    of 4, but never lowers a legitimately higher recommendation.
    """
    return max(
        int(min_group_size) if min_group_size > 0 else 1,
        min(int(recommended), int(max_adaptive_group))
        if max_adaptive_group > 0
        else int(recommended),
    )


def _parse_model_batch_dim_scores(text: str, n: int) -> dict[int, dict[str, float | None]] | None:
    """Parse the batch COMPARATIVE judge's JSON into per-candidate dim scores.

    2026-08-27 (r19, batch comparative self-judge): the judge scores ALL n
    candidates at once, comparing them within the group, and returns JSON of
    the form ``{"candidate_1": {dims...}, ..., "candidate_N": {dims...}}``.

    Fail-closed: a candidate ABSENT from the parse (or with non-numeric dims)
    gets ``None`` for every dim (judge-absent) — it is NEVER silently scored 0.
    Returns a mapping ``{index_0based: {dim: score|None}}`` of length n, or
    None when the whole response is unparseable (the caller then falls back to
    the per-candidate independent-judge path or records judge-absent).
    """
    if n <= 0:
        return None
    matched = _extract_json_object(text or "")
    if not matched:
        return None
    try:
        data = json.loads(matched)
    except (json.JSONDecodeError, ValueError, RecursionError):
        # 2026-09-01 (adversarial-judge lane): RecursionError is NOT a
        # ValueError subclass — pathological nesting must fail closed (None),
        # never crash the trainer.
        return None
    if not isinstance(data, dict):
        return None
    # B-037: digit-normalized candidate key lookup (candidate1/Candidate 1/…)
    key_by_num: dict[int, Any] = {}
    for k_key, v_val in data.items():
        m_key = re.search(r"(\d+)", str(k_key))
        if m_key and isinstance(v_val, dict):
            key_by_num.setdefault(int(m_key.group(1)), v_val)
    scores: dict[int, dict[str, float | None]] = {}
    for i in range(1, n + 1):
        cell: dict[str, float | None] = {}
        # B-037 (2026-09-03): dp4 sometimes keys candidates as "candidate1",
        # "Candidate 1", "candidate_01" — exact-key-only lookups silently
        # produced all-None groups (judge-absent with no diagnostic). Digit-
        # normalized fallback lookup below.
        raw = data.get(f"candidate_{i}", key_by_num.get(i))
        if isinstance(raw, dict):
            for dim in MODEL_JUDGE_DIMENSIONS:
                v = raw.get(dim)
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    cell[dim] = min(1.0, max(0.0, float(v)))
                else:
                    cell[dim] = None
        else:
            for dim in MODEL_JUDGE_DIMENSIONS:
                cell[dim] = None
        scores[i - 1] = cell
    # Fail-closed: if the response had no useful candidate at all, return None
    # so the caller falls back instead of scoring everyone 0.
    if all(all(v is None for v in cell.values()) for i, cell in scores.items()):
        return None
    return scores


def _unpermute_batch_scores(
    scores_by_position: dict[int, dict[str, float | None]] | None,
    order: Sequence[int],
) -> dict[int, dict[str, float | None]] | None:
    """Map position-keyed parsed batch scores back to ORIGINAL candidate indices.

    2026-09-01 (JUDGE-BRIDGE audit, RED regression): ``_render_batch_judge_candidates``
    presents candidates in RANDOMIZED order (``order[pos]`` = original index
    shown at 1-based slot ``pos+1``), but the judge's ``candidate_k`` JSON keys
    are POSITION keys. Without this un-permutation the shuffled presentation
    silently misattributes every score to the wrong candidate. Both batch-judge
    callers (in-process and dp4) must remap before returning.
    """
    if scores_by_position is None:
        return None
    remapped: dict[int, dict[str, float | None]] = {}
    for pos, cell in scores_by_position.items():
        if 0 <= pos < len(order):
            remapped[order[pos]] = cell
    return remapped


def effective_judge_weights(
    judge_weights: Mapping[str, float],
    *,
    model_judge_enabled: bool,
) -> dict[str, float]:
    """Resolve the judge dimension weights actually used for blending.

    2026-08-26 (r17, research-lane fix): the judge is CALIBRATION-GATED. An
    ACTIVE UNCALIBRATED judge injects ~0.5±noise into the advantages, so
    with NO calibration file the weight map stays EMPTY and the blend's
    judge mass is exactly 0 (the masses renormalize over pass+shaped). The
    r16 uniform fallback is removed. Calibrated weights pass through; a
    disabled judge keeps whatever was passed (legacy behavior).
    """
    if not model_judge_enabled:
        return dict(judge_weights)
    if judge_weights:
        return {str(dim): float(weight) for dim, weight in judge_weights.items()}
    return {}


def resolve_frozen_judge(
    *,
    model: Any,
    distributed: bool,
    judge_model_path: str | None,
    model_name: str,
    judge_adapter_path: str | None,
    loader: Any = None,
) -> tuple[Any, bool, str]:
    """Resolve the frozen judge model handle + whether it shares the training
    instance.

    2026-08-26 (r16 judge wave, memory wall): the judge is the base
    Qwen3.6-27B running on the SAME sharded model — loading a second full
    27B (the legacy path) is the OOM class we keep dead. When the judge path
    equals the training model path and no judge adapter is requested, the
    judge IS ``model.base_model`` (the frozen base; the current LoRA policy
    is never the judge). A different judge path keeps the legacy separate
    load (older accepted adapters, other judge models).

    ``loader`` is injected for tests (defaults to AutoModelForCausalLM).
    Returns ``(judge_model, shared, judge_path)``.
    """
    judge_path = str(judge_model_path or model_name)
    active_model = model.module if distributed else model
    if (
        not judge_adapter_path
        and Path(judge_path) == Path(model_name)
        and getattr(active_model, "base_model", None) is not None
    ):
        return active_model.base_model, True, judge_path
    load = loader or _default_judge_loader
    return load(judge_path), False, judge_path


def _default_judge_loader(path: str):
    """Default judge-model loader for ``resolve_frozen_judge``.

    2026-08-31 (QA sweep): the fallback used to reference
    ``AutoModelForCausalLM`` directly, a name that was only imported lazily
    inside the training function — the "defaults to AutoModelForCausalLM"
    docstring was a silent lie and the non-shared judge path always NameError'd.
    The import is made here so the default loader actually works; tests inject
    ``transformers.AutoModelForCausalLM`` via monkeypatch.
    """
    from transformers import AutoModelForCausalLM

    return AutoModelForCausalLM.from_pretrained(
        path, trust_remote_code=True, low_cpu_mem_usage=True, torch_dtype="auto"
    )


def _model_comprehensive_scores(
    code: str,
    task: dict,
    executable_evidence: str,
    judge_model,
    backend,
    args,
    device,
) -> dict[str, float | None] | None:
    """Frozen-judge per-dimension scores (correctness..quality) for one sample.

    The judge is the base model (or an older accepted adapter) — never the
    current training policy — so the reward model cannot be gamed by policy
    drift. Runs greedily and returns None when the judge output is unusable
    (recorded as missing; excluded from calibration).
    """
    task_desc = task.get("meta", {}).get(
        "description",
        task.get("meta", {}).get("name", str(task.get("task_dir", task.get("task_id", "unknown")))),
    )
    prompt = COMPREHENSIVE_JUDGE_PROMPT.format(
        code=code, evidence=executable_evidence, task_context=task_desc
    )
    messages = [{"role": "user", "content": prompt}]
    try:
        if hasattr(backend, "tokenizer"):
            tokenized = backend.tokenizer.apply_chat_template(
                messages, tokenize=True, return_tensors="pt", add_generation_prompt=True
            ).to(device)
            input_len = tokenized.shape[1]
        elif hasattr(backend, "encode_chat"):
            tokenized_ids = backend.encode_chat(messages, add_generation_prompt=True)
            tokenized = torch.tensor([tokenized_ids], dtype=torch.long, device=device)
            input_len = tokenized.shape[1]
        elif hasattr(backend, "render_backend") and hasattr(
            backend.render_backend, "apply_chat_template"
        ):
            # 2026-08-26 (r16 judge wave): the trainer's TextPreprocessorBackend
            # has no .tokenizer/.encode_chat — every judge call returned None
            # and the judge NEVER ran. Tokenize exactly like the rollout path.
            try:
                tokenized = backend.render_backend.apply_chat_template(
                    messages,
                    tokenize=True,
                    return_tensors="pt",
                    add_generation_prompt=True,
                    enable_thinking=False,
                ).to(device)
            except TypeError:
                tokenized = backend.render_backend.apply_chat_template(
                    messages,
                    tokenize=True,
                    return_tensors="pt",
                    add_generation_prompt=True,
                ).to(device)
            input_len = tokenized.shape[1]
        else:
            return None
        # 2026-08-26 (r16): the judge generate uses the same stop contract as
        # the rollout path (resolved EOS backstop — the Qwen3.6-27B config
        # omits eos_token_id, so without this every judge run burned the full
        # max-new-tokens cap) and an explicit KV cache (the train path sets
        # use_cache=False for gradient checkpointing; a judge forward without
        # the cache is quadratic).
        judge_tokenizer = (
            backend.text_backend
            if hasattr(backend, "text_backend")
            else (backend.tokenizer if hasattr(backend, "tokenizer") else None)
        )
        stop_eos_ids = configured_eos_token_ids(judge_model, judge_tokenizer)
        with torch.no_grad():
            outputs = judge_model.generate(
                input_ids=tokenized,
                max_new_tokens=getattr(args, "model_judge_max_tokens", 256),
                temperature=getattr(args, "model_judge_temperature", 0.0),
                top_p=1.0,
                do_sample=False,
                use_cache=True,
                eos_token_id=sorted(stop_eos_ids) if stop_eos_ids else None,
                pad_token_id=(
                    judge_tokenizer.pad_token_id
                    if judge_tokenizer is not None
                    and getattr(judge_tokenizer, "pad_token_id", None) is not None
                    else getattr(backend, "pad_token_id", 0)
                ),
            )
            response_ids = outputs[0][input_len:]
            if hasattr(backend, "tokenizer"):
                response_text = backend.tokenizer.decode(response_ids, skip_special_tokens=True)
            elif hasattr(backend, "text_backend"):
                response_text = backend.text_backend.decode(response_ids, skip_special_tokens=True)
            else:
                # encode_chat backends decode via backend.decode (2026-08-25:
                # the unconditional tokenizer.decode silently dropped judge
                # scores for tokenizer-less backends — None -> missing).
                response_text = backend.decode(response_ids.tolist())
    except Exception:
        return None
    finally:
        # 2026-08-26 (r16, memory wall): judge inference runs on the same
        # sharded model — release the allocator cache between judge forwards
        # so per-candidate judge passes cannot stack activation fragments.
        _release_device_cache(torch)

    return _parse_model_dim_scores(response_text)


def _model_batch_dim_scores(
    codes: Sequence[str],
    evidences: Sequence[str],
    task: dict,
    model,
    backend,
    args,
    device,
) -> dict[int, dict[str, float | None]] | None:
    """Batch COMPARATIVE self-judge (2026-08-27 r19, user directive).

    The judge is the ACTIVE training model ITSELF (the model being trained
    judges all of its own rollouts). All ``len(codes)`` candidates are scored
    in ONE forward in a single prompt that asks the model to compare them
    against each other (a group-relative ranking), and the parsed scores are
    returned per 0-based candidate index. This is the opposite of the
    per-candidate independent judge (``_model_comprehensive_scores``).

    Fail-closed: any candidate the model fails to score gets ``None`` per dim
    (judge-absent), never a fabricated 0. Returns None when the whole batch
    response is unusable (the caller then falls back to the per-candidate
    independent judge, and any still-missing dims stay judge-absent).
    """
    n = len(codes)
    if n <= 0:
        return None
    task_desc = task.get("meta", {}).get(
        "description",
        task.get("meta", {}).get("name", str(task.get("task_dir", task.get("task_id", "unknown")))),
    )
    rng = random.Random()
    candidates_text, perm = _render_batch_judge_candidates(codes, evidences, rng=rng)
    prompt = COMPREHENSIVE_BATCH_JUDGE_PROMPT.format(
        n=n, candidates=candidates_text, task_context=task_desc
    )
    messages = [{"role": "user", "content": prompt}]
    response_text = None
    try:
        if hasattr(backend, "tokenizer"):
            tokenized = backend.tokenizer.apply_chat_template(
                messages, tokenize=True, return_tensors="pt", add_generation_prompt=True
            ).to(device)
            input_len = tokenized.shape[1]
        elif hasattr(backend, "render_backend") and hasattr(
            backend.render_backend, "apply_chat_template"
        ):
            try:
                tokenized = backend.render_backend.apply_chat_template(
                    messages,
                    tokenize=True,
                    return_tensors="pt",
                    add_generation_prompt=True,
                    enable_thinking=False,
                ).to(device)
            except TypeError:
                tokenized = backend.render_backend.apply_chat_template(
                    messages,
                    tokenize=True,
                    return_tensors="pt",
                    add_generation_prompt=True,
                ).to(device)
            input_len = tokenized.shape[1]
        elif hasattr(backend, "encode_chat"):
            tokenized_ids = backend.encode_chat(messages, add_generation_prompt=True)
            tokenized = torch.tensor([tokenized_ids], dtype=torch.long, device=device)
            input_len = tokenized.shape[1]
        else:
            return None
        judge_tokenizer = (
            backend.text_backend
            if hasattr(backend, "text_backend")
            else (backend.tokenizer if hasattr(backend, "tokenizer") else None)
        )
        stop_eos_ids = configured_eos_token_ids(model, judge_tokenizer)
        with torch.no_grad():
            outputs = model.generate(
                input_ids=tokenized,
                max_new_tokens=getattr(args, "model_judge_max_tokens", 4096),
                temperature=getattr(args, "model_judge_temperature", 0.0),
                top_p=1.0,
                do_sample=False,
                use_cache=True,
                eos_token_id=sorted(stop_eos_ids) if stop_eos_ids else None,
                pad_token_id=(
                    judge_tokenizer.pad_token_id
                    if judge_tokenizer is not None
                    and getattr(judge_tokenizer, "pad_token_id", None) is not None
                    else getattr(backend, "pad_token_id", 0)
                ),
            )
            response_ids = outputs[0][input_len:]
            if hasattr(backend, "tokenizer"):
                response_text = backend.tokenizer.decode(response_ids, skip_special_tokens=True)
            elif hasattr(backend, "text_backend"):
                response_text = backend.text_backend.decode(response_ids, skip_special_tokens=True)
            else:
                response_text = backend.decode(response_ids.tolist())
    except Exception:
        return None
    finally:
        _release_device_cache(torch)

    # 2026-09-01 (JUDGE-BRIDGE audit RED): the candidates were presented in
    # RANDOMIZED order (rng seeded per call) — the parsed scores are keyed by
    # PRESENTATION POSITION, so they must be un-permuted back to the original
    # candidate indices or every score lands on the wrong candidate.
    return _unpermute_batch_scores(_parse_model_batch_dim_scores(response_text, n=n), perm)


# 2026-09-08 (s28 dark-step root-cause): structured diagnostic of the most
# recent dp4 batch-judge attempt. Bare-None failures left the 3-attempt retry
# blind and dark steps (s3, s28) unexplainable from the run log alone. The
# caller loud dp4_judge_failed line embeds this; a succeeding call clears it.
_last_dp4_judge_diag = None


def _set_last_dp4_judge_diag(diag):
    global _last_dp4_judge_diag
    _last_dp4_judge_diag = diag


def get_last_dp4_judge_diag():
    """Structured diagnostic of the LAST dp4 judge attempt (None on success).

    Keys: reason (transport_error / bad_json_body / error_body /
    no_json_object / no_candidate_keys), reply_head (first 400 chars of the
    raw reply or reply text), error (exception text for transport errors).
    """
    return _last_dp4_judge_diag


def _dp4_client_timeout_s() -> float:
    """Client-side socket deadline for one dp4 judge round-trip.

    2026-09-08 (dark-step s3 root-cause CORRECTION, run 094427Z): the fixed
    310.0s deadline was the judge-absent mechanism - the box translator is
    healthy (judge log: all success:true, latency 3-72s, retries 1, no
    errors), so any 4/4-null step means the TRAINER's own round-trip gave
    up. The deadline is now env-tunable (JUDGE_DP4_CLIENT_TIMEOUT_S) so an
    operator can cover a slow dp4 tail without touching the manifest or
    redeploying; the default stays 310.0 (byte-compatible with the R22 B5
    timeout chain: trainer 310 > bridge 290 > watcher 250).
    """
    raw = os.environ.get("JUDGE_DP4_CLIENT_TIMEOUT_S", "")
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return 310.0
    return value if value > 0.0 else 310.0


def _dp4_trailing_grace_s() -> float:
    """Grace deadline for recovering a trailing (slow-but-successful) judge.

    Default 150s: the observed translator success tail is 3-72s, so 150s
    covers the tail plus a fresh replacement round-trip while keeping the
    total client wait (310 + 150) below the ~415s/step training cadence.
    Env: JUDGE_DP4_TRAILING_GRACE_S (0 disables the recovery -> the old
    fail-fast behavior).
    """
    raw = os.environ.get("JUDGE_DP4_TRAILING_GRACE_S", "")
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return 150.0
    return value if value >= 0.0 else 150.0


def _dp4_trailing_poll_s() -> float:
    """Poll cadence for the trailing-judge recovery (default 15s)."""
    raw = os.environ.get("JUDGE_DP4_TRAILING_POLL_S", "")
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return 15.0
    return value if value > 0.0 else 15.0


def _is_timeout_exception(exc: BaseException) -> bool:
    """True when exc is a client-side TIMEOUT (as opposed to any other
    transport failure). Only timeouts qualify for the trailing-judge
    recovery - every other exception must fail fast-closed exactly as
    before (py3.9-safe: socket.timeout is not yet TimeoutError there)."""
    import socket

    if isinstance(exc, (socket.timeout, TimeoutError)):
        return True
    reason = getattr(exc, "reason", None)
    return isinstance(reason, (socket.timeout, TimeoutError))


def _dp4_trailing_judge_recovery(
    codes: Sequence[str],
    evidences: Sequence[str],
    task: dict,
    *,
    endpoint: str,
    model: str,
    max_tokens: int,
    temperature: float,
    timeout_s: float,
) -> dict[int, dict[str, float | None]] | None:
    """Recover a TRAILING judge response after a client-side timeout.

    2026-09-08 (dark-step class extinction, run 094427Z step 3): the box
    translator at :56238 is HEALTHY (judge log: all success:true, latency
    3-72s, retries 1, last_error null), yet the trainer recorded
    judge_reward=null for 4/4 candidates - the drop was the TRAINER's own
    judge client: a slow-but-successful dp4 response landing after the
    client socket deadline was discarded (one shot, except -> None) and
    the B-046 retry loop only re-paid a BRAND-NEW request, never waiting
    for the trailing result.

    Within the JUDGE_DP4_TRAILING_GRACE_S deadline this re-issues the same
    comparative prompt with a short socket budget and parses any response
    that lands (2026-09-03 direct-dp4 opener rules preserved). Returns the
    un-permuted per-candidate scores, or None once the grace deadline
    expires (fail-closed: judge-absent, NEVER a fabricated score).
    """
    import time as _time
    import urllib.request

    grace_s = _dp4_trailing_grace_s()
    poll_s = _dp4_trailing_poll_s()
    short_timeout = max(1.0, min(timeout_s, 90.0))
    if grace_s <= 0.0:
        return None
    rng = random.Random()
    candidates_text, perm = _render_batch_judge_candidates(codes, evidences, rng=rng)
    task_desc = task.get("meta", {}).get(
        "description",
        task.get("meta", {}).get("name", str(task.get("task_dir", task.get("task_id", "unknown")))),
    )
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {
                "role": "user",
                "content": COMPREHENSIVE_BATCH_JUDGE_PROMPT.format(
                    n=len(codes), candidates=candidates_text, task_context=task_desc
                ),
            }
        ],
    }
    url = endpoint.rstrip("/") + "/v1/messages"
    api_key = os.environ.get("HUANXIN_DP4_API_KEY", "test")
    if endpoint.startswith(("http://127.0.0.1", "http://localhost")):
        opener = urllib.request.build_opener(urllib.request.ProxyHandler(dict()))
    else:
        opener = urllib.request.build_opener()
    deadline = _time.monotonic() + grace_s
    while _time.monotonic() < deadline:
        _time.sleep(poll_s)
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
        )
        try:
            with opener.open(req, timeout=short_timeout) as resp:
                body = json.loads(resp.read().decode())
        except Exception:
            continue
        if not isinstance(body, dict):
            continue
        text = None
        for block in body.get("content") or []:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text")
                break
        if not text:
            continue
        parsed = _unpermute_batch_scores(_parse_model_batch_dim_scores(text, n=len(codes)), perm)
        if parsed is not None:
            return parsed
    return None


def _model_batch_dim_scores_dp4(
    codes: Sequence[str],
    evidences: Sequence[str],
    task: dict,
    *,
    endpoint: str,
    model: str = "dp4",
    max_tokens: int = 4096,
    temperature: float = 0.0,
    timeout_s: float | None = None,
) -> dict[int, dict[str, float | None]] | None:
    """Batch COMPARATIVE judge via the Huanxin dp4 (deepseek-v4-flash) model.

    2026-08-27 (r19, user directive): the judge is the **dp4 / deepseek-v4-flash**
    model served by the Huanxin Anthropic-compatible proxy (the same model used
    by ``claude -p huanxin -m dp4``). All ``len(codes)`` candidates are scored
    AT ONCE in ONE prompt that asks dp4 to COMPARE them against each other (a
    group-relative ranking), not one independent score per candidate.

    Pass is part — never the whole — of the comprehensive score: the executable
    pass signal is blended (w_P) with the comparative judge dims (w_J). The
    judge prompt embeds per-candidate executable evidence so dp4 anchors its
    ranking to real pass/fail.

    Fail-closed: any candidate dp4 fails to score gets ``None`` per dim
    (judge-absent), never a fabricated 0. Returns None when the whole response
    is unusable (the caller falls back to the in-process per-candidate judge or
    records judge-absent).

    ``endpoint`` is the Anthropic Messages base URL, e.g.
    ``http://127.0.0.1:55080`` (the dp4 proxy); the caller also passes the API
    key via env when required.
    """
    import urllib.request

    def _dp4_fail(reason, reply_head="", error=""):
        # 2026-09-08 (s28 dark-step root-cause): a bare None made the
        # caller 3-attempt retry BLIND and the dp4_judge_failed record
        # carried zero evidence - dark steps were unexplainable from the
        # run log alone. Structured diagnostic + persisted reply head;
        # still fail-closed (never a fabricated 0).
        head = (reply_head or "")[:400]
        _set_last_dp4_judge_diag(dict(reason=reason, reply_head=head, error=error))
        return None

    n = len(codes)
    if n <= 0:
        return None
    task_desc = task.get("meta", {}).get(
        "description",
        task.get("meta", {}).get("name", str(task.get("task_dir", task.get("task_id", "unknown")))),
    )
    # 2026-09-01 (JUDGE-BRIDGE audit RED): _render_batch_judge_candidates
    # returns (text, perm) — binding the TUPLE here formatted the repr
    # ('Candidate 1:\\n...', [0,1,..]) into the prompt (escaped newlines,
    # the permutation list leaked into the judge) AND randomized order never
    # reached the judge. Destructure + per-call rng (position-bias kill).
    rng = random.Random()
    candidates_text, perm = _render_batch_judge_candidates(codes, evidences, rng=rng)
    prompt = COMPREHENSIVE_BATCH_JUDGE_PROMPT.format(
        n=n, candidates=candidates_text, task_context=task_desc
    )
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }
    url = endpoint.rstrip("/") + "/v1/messages"
    api_key = os.environ.get("HUANXIN_DP4_API_KEY", "test")
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    # 2026-09-08 (dark-step s3 root-cause CORRECTION, run 094427Z): resolve
    # the client deadline (env JUDGE_DP4_CLIENT_TIMEOUT_S, default 310 - the
    # R22 B5 trainer link of the timeout chain) instead of the hardcoded
    # literal; None -> resolved here so legacy callers are unaffected.
    if timeout_s is None:
        timeout_s = _dp4_client_timeout_s()
    try:
        # 2026-09-03 (B-043 direct-dp4): the box CAN reach the dp4
        # subscription through its squid proxy (JWT deployed at /root/.dp4_jwt,
        # verified 200 "BOX_DP4_OK"). Route via the env proxy when the
        # endpoint is the real dp4 URL; bypass only for the local bridge.
        if endpoint.startswith(("http://127.0.0.1", "http://localhost")):
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        else:
            opener = urllib.request.build_opener()
        with opener.open(req, timeout=timeout_s) as resp:
            raw = resp.read().decode()
    except Exception as exc:
        # 2026-09-08 (dark-step class extinction): a slow-but-SUCCESSFUL
        # judge (translator tail 3-72s, dp4 nominal ~200s) used to be
        # dropped here as judge-absent - the step-3 4/4-null mechanism.
        # On a client-side TIMEOUT ONLY, recover the trailing judge within
        # the grace deadline before failing closed. Every other transport
        # failure fails fast-closed exactly as before.
        if _is_timeout_exception(exc):
            recovered = _dp4_trailing_judge_recovery(
                codes,
                evidences,
                task,
                endpoint=endpoint,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout_s=float(timeout_s),
            )
            if recovered is not None:
                _set_last_dp4_judge_diag(None)
                return recovered
        return _dp4_fail("transport_error", error=type(exc).__name__ + ": " + str(exc))
    try:
        body = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return _dp4_fail("bad_json_body", reply_head=raw)
    if not isinstance(body, dict):
        return _dp4_fail("bad_json_body", reply_head=raw)
    # Anthropic Messages shape: {"content": [{"type":"text","text": "..."}]}
    text = None
    for block in body.get("content") or []:
        if isinstance(block, dict) and block.get("type") == "text":
            text = block.get("text")
            break
    if not text:
        return _dp4_fail("error_body", reply_head=raw)
    # Position-bias: the candidates were presented to the judge in RANDOMIZED
    # order, so the parsed POSITION-keyed scores are un-permuted back to the
    # original candidate indices — presentation order never leaks into the
    # training loop (2026-09-01 JUDGE-BRIDGE audit RED).
    parsed = _parse_model_batch_dim_scores(text, n=n)
    if parsed is None:
        # B-037 family: keep the reply TEXT for post-mortem, and say WHY:
        # prose-only reply = no_json_object; JSON present but no candidate
        # key matched = no_candidate_keys.
        reason = "no_json_object" if not _extract_json_object(text) else "no_candidate_keys"
        return _dp4_fail(reason, reply_head=text)
    _set_last_dp4_judge_diag(None)
    return _unpermute_batch_scores(parsed, perm)


def _parse_self_eval_score(text: str) -> float:
    """Extract score 0-10 from model's judge response, normalize to 0-1."""
    import re

    try:
        # Try to find a balanced JSON block (string-aware extraction)
        json_match = _extract_json_object(text)
        if json_match:
            data = json.loads(json_match)
            raw = float(data.get("score", 5.0))
        else:
            # Fallback (F7): prefer the scaled "X/10" / "X out of 10" form,
            # then "score: X"; an ambiguous BARE number anywhere in the prose
            # ("3 compile errors; I score it 7/10") must not be grabbed as
            # the score — neutral default instead.
            scaled = re.search(r"(\d+(?:\.\d+)?)\s*(?:/\s*10|out of 10)", text or "")
            scored = re.search(r"score[:\s]*(\d+(?:\.\d+)?)", text or "")
            score_match = scaled or scored
            if score_match:
                raw = float(score_match.group(1))
            else:
                return 0.5  # neutral default
    except (json.JSONDecodeError, ValueError, KeyError, TypeError, RecursionError):
        # 2026-09-01 (adversarial-judge lane): RecursionError is NOT a
        # ValueError subclass — pathological nesting must fail closed to the
        # neutral default, never crash. 2026-09-01 (PROPERTY-FUZZ lane RED): a
        # judge emitting {"score": null|{}|[]|...} raised TypeError from
        # float(None) — TypeError is ALSO not a ValueError subclass and
        # escaped this guard, crashing the training loop on a malformed
        # score. Fail closed to the neutral default like every other class.
        return 0.5

    # Normalize: clamp to [0, 10], then divide to [0, 1]
    raw = max(0.0, min(10.0, raw))
    return raw / 10.0


def evaluate_candidate(
    code: str,
    test_harness,
    task: dict,
    args,
    research_methods: list[Any] | None = None,
    model=None,
    backend=None,
    device=None,
    judge_model=None,
    judge_weights: dict[str, float] | None = None,
    judge_diagnostics_path: Path | None = None,
    step: int | None = None,
) -> dict[str, Any]:
    """Run tests and return a shaped reward breakdown.

    When self_evaluation is enabled, also evaluates the code by asking the model
    to judge its own output against quality criteria (correctness, runnability,
    efficiency, code quality).

    When ``judge_model`` is provided (frozen base model / older accepted
    adapter), per-dimension comprehensive scores are produced and blended with
    the executable reward via ``blend_comprehensive_reward``: P (full test
    pass) always dominates; judge mass comes out of the shaped term only.
    """
    # Review finding 2026-08-05 (#10): candidates must NOT be written into the
    # task directory, which also contains tests.py and the reference solution.
    # Candidates are executed from an isolated temp dir (harnesses load the
    # candidate by absolute path). Full container-level isolation remains a
    # deployment requirement. 2026-08-21: candidate eval runs in a FRESH
    # interpreter subprocess (fork-safe + timeout-bounded) so candidate imports
    # cannot deadlock the NPU-sharded trainer (observed on ASI3 step 1).
    try:
        result, typed_score, typed_info = _run_harness_subprocess(code, task, args)
    except Exception as exc:  # noqa: BLE001 - a candidate eval must not kill the step
        result = {
            "passed": False,
            "details": [f"{type(exc).__name__}: {exc}"],
        }
        typed_score, typed_info = 0.0, None

    reward = build_reward_breakdown(
        code=code,
        result=result,
        required_interface=task.get("required_interface", []),
        detail_budget=int(task.get("detail_budget", 1)),
        pass_weight=args.reward_pass_weight,
        syntax_weight=args.reward_syntax_weight,
        interface_weight=args.reward_interface_weight,
        verifier_weight=args.reward_verifier_weight,
        brevity_weight=args.reward_brevity_weight,
        brevity_target_lines=args.brevity_target_lines,
        import_hygiene_weight=args.reward_import_hygiene_weight,
        single_file_expected=bool(task.get("single_file_expected", False)),
        allowed_import_roots=task.get("allowed_import_roots", []),
        crash_progress_credit=bool(getattr(args, "crash_progress_credit", False)),
    )
    reward["details"] = result.get("details", []) if isinstance(result, dict) else []
    if bool(result.get("security_violation")):
        # Reward-hacking attempts are invalid data, not syntax/interface
        # progress. Give them no shaped, judge, brevity, or hygiene credit so
        # a group cannot learn to approach the forbidden introspection path.
        for name in tuple(reward):
            if name.endswith("_reward") and isinstance(reward[name], (int, float)):
                reward[name] = 0.0
        reward.update(
            {
                "passed": False,
                "security_violation": True,
                "self_eval_reward": 0.0,
                "self_eval_raw_score": 0.0,
                "model_dim_scores": {},
                "total_reward": 0.0,
            }
        )
        return reward
    # Typed quantum-semantic verifier (review 2026-08-05 #6): a continuous
    # semantic score (state/process fidelity, distribution distance) replaces
    # the generic verifier fraction when the task declares a verifier_type.
    # tests.py remains the authoritative pass gate.
    if typed_info is not None:
        reward["verifier_reward"] = typed_score
        reward["typed_verifier"] = str(task.get("meta", {}).get("verifier_type"))
    for method in research_methods or []:
        reward = method.adjust_reward_breakdown(
            reward,
            code=code,
            result=result,
            task=task,
            stage="grpo",
        )

    # ── self-evaluation: ask the model to judge its own generated code ──
    if args.self_evaluation_enabled and model is not None and backend is not None:
        self_eval_score = _self_evaluate_code(code, task, model, backend, args, device)
        reward["self_eval_reward"] = self_eval_score * args.reward_self_eval_weight
        reward["self_eval_raw_score"] = self_eval_score
    else:
        reward["self_eval_reward"] = 0.0
        reward["self_eval_raw_score"] = 0.0

    # ── comprehensive frozen-judge scoring (base model / older adapters) ──
    reward["model_dim_scores"] = {}
    reward["judge_reward"] = None
    if args.model_judge_enabled and judge_model is not None and backend is not None:
        evidence_parts = [f"tests passed: {bool(result.get('passed'))}"]
        raw_details = result.get("details") or []
        evidence_parts.append(
            "failures: " + ("; ".join(str(d)[:200] for d in raw_details[:5]) or "none")
        )
        scores = _model_comprehensive_scores(
            code, task, "\n".join(evidence_parts), judge_model, backend, args, device
        )
        if scores is not None:
            reward["model_dim_scores"] = scores
            # 2026-08-26 (r16/r17): the exact composite the blend used, so
            # the reward verifier recomputes the blend per candidate. With
            # NO calibrated weights the judge is INACTIVE (calibration-gated)
            # and the field is None — the audit's judge-absent gate must
            # match the trainer's renormalization over pass+shaped exactly.
            reward["judge_reward"] = (
                judge_composite_score(scores, judge_weights or {}) if judge_weights else None
            )
            if judge_diagnostics_path is not None:
                append_grpo_metric_jsonl(
                    judge_diagnostics_path,
                    build_judge_diagnostics_record(
                        task_id=task.get("task_id", "?"),
                        passed=bool(reward.get("passed")),
                        syntax_ok=bool(
                            reward.get("syntax_reward") and reward["syntax_reward"] >= 1.0
                        ),
                        verifier_rate=float(reward.get("verifier_reward") or 0.0),
                        model_dim_scores=scores,
                        step=step,
                    ),
                )
    reward["total_reward"] = compose_policy_training_reward(
        reward,
        args,
        model_dim_scores=reward["model_dim_scores"],
        judge_weights=judge_weights or {},
    )
    return reward


def compose_policy_training_reward(
    reward: dict[str, Any],
    args: Any,
    *,
    model_dim_scores: Mapping[str, float] | None = None,
    judge_weights: Mapping[str, float] | None = None,
) -> float:
    """Compose the actual policy reward, even when the judge is disabled.

    The previous path applied ``reward_mode`` only inside the frozen-judge
    branch. In the canonical judge-disabled launch this silently bypassed the
    advertised pass-dominant hierarchy. It also replaced ``verifier_reward``
    with a typed semantic score after ``total_reward`` had already been
    computed, so that higher-quality signal was diagnostic-only.

    Recompute progress from the final component values, then use the binary
    executable pass as the hard tier. Numeric near-miss and typed-semantic
    signals remain available below that tier, so all-fail groups can still
    produce useful relative advantages.
    """
    component_weights = {
        "shaped_reward": float(args.reward_pass_weight),
        "syntax_reward": float(args.reward_syntax_weight),
        "interface_reward": float(args.reward_interface_weight),
        "verifier_reward": float(args.reward_verifier_weight),
        "brevity_reward": float(args.reward_brevity_weight),
        "import_hygiene_reward": float(args.reward_import_hygiene_weight),
    }
    total_weight = sum(max(0.0, weight) for weight in component_weights.values())
    progress_reward = sum(
        max(0.0, weight) * float(reward.get(name, 0.0) or 0.0)
        for name, weight in component_weights.items()
    ) / max(total_weight, 1e-8)

    if args.reward_mode == "tiered":
        # In tiered mode these are small pass-only efficiency/quality bonuses,
        # not linear blend masses.
        blend_pass_mass = args.tiered_alpha
        blend_shaped_mass = args.tiered_gamma
    else:
        blend_pass_mass = args.reward_pass_mass
        blend_shaped_mass = args.reward_shaped_mass

    return blend_comprehensive_reward(
        pass_reward=float(reward.get("pass_reward", 0.0) or 0.0),
        shaped_reward=progress_reward,
        model_dim_scores=model_dim_scores or {},
        dim_weights=judge_weights or {},
        mode=args.reward_mode,
        pass_mass=blend_pass_mass,
        shaped_mass=blend_shaped_mass,
        judge_mass=args.reward_judge_mass,
    )


def _run_harness_subprocess(
    code: str,
    task: dict,
    args,
) -> tuple[dict[str, Any], float, dict[str, Any] | None]:
    """Evaluate one candidate in a FRESH interpreter subprocess with a timeout.

    2026-08-21: the in-process path (tests.py imports the candidate, which may
    import qiskit and fork multiprocessing workers out of the NPU-sharded
    trainer) deadlocked at 0% CPU on ASI3's step-1 eval. The runner
    (evals/runner/single_candidate_eval.py) runs harness + typed verifier in a
    clean process; the trainer only parses the JSON result.
    """
    runner = Path(__file__).resolve().parents[1] / "evals" / "runner" / "single_candidate_eval.py"
    with tempfile.TemporaryDirectory(prefix="fv_gspo_eval_") as eval_dir:
        eval_dir_path = Path(eval_dir)
        candidate_path = eval_dir_path / "candidate.py"
        candidate_path.write_text(code, encoding="utf-8")
        meta_path = eval_dir_path / "meta.json"
        meta_path.write_text(
            json.dumps(task.get("meta", {}) or {}, ensure_ascii=False), encoding="utf-8"
        )
        timeout = int(getattr(args, "harness_timeout_seconds", 300) or 300)
        # 2026-09-13 (fork-deadlock class, live): when qiskit Aer / the circuit
        # simulator is imported in this (already fresh) eval subprocess and then
        # a worker forks, the child inherits a qiskit/Rust-owned lock and hangs at
        # 0% CPU in futex_wait / hrtimer_nanosleep (observed: 8 workers, 12+ min,
        # zero progress on group-size=8 step). Two controls, both on this
        # subprocess only, keep the eval bounded without touching the NPU trainer:
        #  (a) cap BLAS/OMP thread pools so backend parallelism cannot wedge, and
        #  (b) force child workers (if any) to the `spawn` start method so they
        #      re-import state fresh instead of inheriting a locked parent.
        _env = dict(os.environ)
        _env.setdefault("OMP_NUM_THREADS", "1")
        _env.setdefault("OPENBLAS_NUM_THREADS", "1")
        _env.setdefault("MKL_NUM_THREADS", "1")
        try:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(runner),
                    "--candidate",
                    str(candidate_path),
                    "--tests",
                    str(task["tests_py"]),
                    "--task-dir",
                    str(task["task_dir"]),
                    "--meta",
                    str(meta_path),
                ],
                env=_env,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return (
                {"passed": False, "details": [f"harness subprocess timed out after {timeout}s"]},
                0.0,
                None,
            )
        try:
            payload = json.loads(completed.stdout.strip().splitlines()[-1])
        except Exception as exc:  # noqa: BLE001
            return (
                {
                    "passed": False,
                    "details": [
                        f"harness subprocess unparseable output rc={completed.returncode}: "
                        f"{type(exc).__name__} {completed.stdout[-200:]}{completed.stderr[-200:]}"
                    ],
                },
                0.0,
                None,
            )
    harness = payload.get("harness") or {"passed": False, "details": ["no harness result"]}
    if not isinstance(harness, dict):
        harness = {
            "passed": False,
            "details": [f"Unexpected harness type: {type(harness).__name__}"],
        }
    typed_score = float(payload.get("typed_score") or 0.0)
    typed_info = payload.get("typed_info")
    return harness, typed_score, typed_info


def _run_harness_for_code(
    tests_path,
    code: str,
    args=None,
) -> dict[str, Any]:
    """Run a candidate code string against the hidden-test harness in a fresh
    subprocess (fork-safe, timeout-bounded). Returns a
    ``{passed: bool, details: list[str]}`` result dict for teacher-free
    self-repair verification.
    """
    harness, _score, _info = _run_harness_subprocess(
        code,
        {"tests_py": tests_path, "task_dir": Path(tests_path).parents[1], "meta": {}},
        args or argparse.Namespace(harness_timeout_seconds=300),
    )
    passed = bool(harness.get("passed"))
    details = [str(d) for d in (harness.get("details") or [])] if isinstance(harness, dict) else []
    return {"passed": passed, "details": details}


def _self_repair_failing_candidate(
    *,
    model,
    text_preprocessor,
    device: Any,
    test_harness,
    task: dict,
    code: str,
    task_prompt: str,
    result: dict[str, Any],
    args,
    max_rounds: int,
    temperature: float | None = None,
) -> dict[str, Any]:
    """Teacher-free self-repair rollout for a single failing candidate.

    Implements the plan's 无教师自修复 (no teacher model): the failing code plus
    its real harness error logs are fed back to the *policy model itself* to
    produce a repair, re-scored against the hidden tests, up to ``max_rounds``
    rounds (plan §8 recommends 2). Repairs are diagnostic/conversion artifacts;
    they must not replace the reward attached to the original rollout because
    they were sampled under a different repair prompt.

    Returns the module's result dict (see teacher_free_repair.teacher_free_self_repair).
    """
    backend = text_preprocessor

    def _repair(prompt_text: str) -> str:
        text = render_generation_prompt(backend.render_backend, prompt_text)
        # 2026-08-26 (r10, launch-simulator F2): same tokenizer-field filter
        # as the rollout path.
        inputs = move_batch_to_device(
            filter_generation_inputs(model, backend.text_backend(text, return_tensors="pt")),
            device,
        )
        effective_temp = temperature if temperature is not None else args.temperature
        # 2026-08-25 (generation-efficiency): same stop contract as the
        # rollout path — closing fence or first EOS, cap only as backstop.
        stop_ids = configured_eos_token_ids(model, backend.text_backend)
        # 2026-09-11: same BOS/PAD-in-EOS guard as the rollout path — a repair
        # completion that dies on the sequence-start marker is not a repair.
        repair_suppress_ids = configured_suppress_token_ids(
            model, backend.text_backend, stop_eos_ids=stop_ids
        )
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                temperature=effective_temp,
                top_p=args.top_p,
                do_sample=True,
                # F1 (2026-08-26 code-review): without the dict form, generate
                # returns a plain Tensor and `outputs.sequences` raises
                # AttributeError — swallowed by teacher_free_self_repair's
                # broad except, so self-repair silently never repaired.
                return_dict_in_generate=True,
                eos_token_id=sorted(stop_ids) if stop_ids else None,
                logits_processor=rollout_suppress_logits_processor(repair_suppress_ids),
                stopping_criteria=StoppingCriteriaList(
                    [
                        StopAfterClosedCodeFence(
                            backend.text_backend,
                            prompt_length=int(inputs["input_ids"].shape[1]),
                        )
                    ]
                ),
            )
        gen_ids = outputs.sequences[0, inputs["input_ids"].shape[1] :]
        response = backend.text_backend.decode(gen_ids, skip_special_tokens=True)
        return extract_code(response)

    meta = task.get("meta", {})
    interface_lines = task.get("required_interface") or (
        summarize_candidate_interface(task["task_dir"] / meta["candidate_file"])
        if meta.get("candidate_file")
        else []
    )
    behavior_hints = task.get("behavior_hints") or extract_behavior_hints(task["tests_py"])

    return teacher_free_self_repair(
        task_prompt=task_prompt,
        failing_code=code,
        correctness=result,
        repair=_repair,
        verify=lambda c: _run_harness_for_code(task["tests_py"], c, args),
        max_rounds=max_rounds,
        interface_lines=interface_lines or None,
        behavior_hints=behavior_hints or None,
    )


def annotate_self_repair_diagnostics(
    original_entry: dict[str, Any],
    repaired_entry: dict[str, Any],
    repair_ctx: dict[str, Any],
) -> dict[str, Any]:
    """Record a successful repair without changing the original RL reward.

    The repaired program is generated from ``failing code + harness errors``,
    not from the original task prompt. Assigning its pass reward to the
    original program while retaining the original rollout log-probabilities is
    invalid credit assignment and actively reinforces failed actions. The
    repair remains available for the verified SFT/DPO conversion lane.
    """
    original_entry["self_repair_passed"] = True
    original_entry["self_repair_round"] = repair_ctx.get("best_round", 0)
    original_entry["self_repair_reward_applied"] = False
    original_entry["self_repair_candidate_pass_reward"] = float(
        repaired_entry.get("pass_reward", 0.0)
    )
    original_entry["self_repair_candidate_shaped_reward"] = float(
        repaired_entry.get("shaped_reward", 0.0)
    )
    original_entry["self_repair_candidate_total_reward"] = float(
        repaired_entry.get("total_reward", 0.0)
    )
    return original_entry


def scale_optimizer_lr(optimizer: Any, *, factor: float, min_lr: float) -> tuple[float, float]:
    """Scale optimizer learning rates without silently collapsing below a floor."""
    if not optimizer.param_groups:
        return 0.0, 0.0
    before = float(optimizer.param_groups[0]["lr"])
    floor = max(0.0, float(min_lr))
    for group in optimizer.param_groups:
        group["lr"] = max(floor, float(group["lr"]) * float(factor))
    return before, float(optimizer.param_groups[0]["lr"])


def render_generation_prompt(render_backend: Any, prompt: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    if hasattr(render_backend, "apply_chat_template"):
        try:
            return render_backend.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False,
            )
        except TypeError:
            return render_backend.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
    return "\n\n".join(f"{message['role'].upper()}: {message['content']}" for message in messages)


def move_batch_to_device(batch: dict[str, torch.Tensor], device: Any) -> dict[str, torch.Tensor]:
    return {name: tensor.to(device) for name, tensor in batch.items()}


def _release_device_cache(torch_module: Any) -> None:
    """Release NPU/CUDA allocator cache between phases.

    Long sharded 27B runs fragment device memory across rollouts; freeing the
    allocator cache between phases keeps peak allocation low. Safe no-op on
    backends without an empty_cache API.
    """
    for backend_name in ("npu", "cuda", "mps"):
        backend = getattr(torch_module, backend_name, None)
        if backend is not None and hasattr(backend, "empty_cache"):
            try:
                backend.empty_cache()
            except Exception:
                pass


def train_pass_truncation_breakdown(
    seq_cap: int, n_truncated: int, n_total: int
) -> dict[str, float | int]:
    """Loss-reduction documentation for the train-pass sequence cap.

    2026-08-25 OOM fix (run-4): the SAPO token loss is computed on at most the
    first ``seq_cap`` tokens of each candidate (train pass only; rollout
    log-probs, eval and rewards stay on the full sequence). These fields make
    the truncation honest in the step record so the auditor can see exactly
    how many candidates had their completion tail dropped from the update.
    ``seq_cap`` 0/None means the cap is disabled and the rate is always 0.
    """
    total = max(int(n_total), 0)
    return {
        "train_pass_seq_cap": int(seq_cap) if seq_cap else 0,
        # 2026-08-31 (coverage lane, PASS 16): the documented contract is
        # "seq_cap 0/None means the cap is disabled and the rate is always 0"
        # — the rate previously leaked n_truncated/n_total even when the cap
        # was disabled (latent: main() only passes n_truncated>0 with a cap,
        # but a direct call reported a dishonest truncation rate).
        "train_pass_truncation_rate": (
            round(float(n_truncated) / total, 6) if (total > 0 and seq_cap) else 0.0
        ),
    }



def _generate_with_no_grad(
    model,
    *,
    inputs,
    group_size,
    max_new_tokens,
    temperature,
    top_p,
    do_sample,
    stop_eos_ids,
    suppress_token_ids,
    backend,
    prompt_len,
):
    """Run one batched ``model.generate`` inside a no_grad context.

    C-9523: invoked through ``run_bounded_generation`` (a daemon-thread
    watchdog) so a dead ASCEND NPU TBE task_distribute subprocess fails
    fast-closed instead of hanging the trainer forever. ``no_grad`` is applied
    HERE (not in the caller) so the worker thread also runs grad-disabled, as
    the original rollout path did.
    """
    with torch.no_grad():
        out = model.generate(
            **build_batched_prompt_inputs(inputs, group_size=group_size),
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=do_sample,
            use_cache=True,
            return_dict_in_generate=True,
            output_scores=False,
            eos_token_id=sorted(stop_eos_ids) if stop_eos_ids else None,
            logits_processor=rollout_suppress_logits_processor(suppress_token_ids),
            stopping_criteria=StoppingCriteriaList(
                [StopAfterClosedCodeFence(backend.text_backend, prompt_length=prompt_len)]
            ),
        )
    return out


def generate_group(
    model,
    backend: TextPreprocessorBackend,
    prompt: str,
    args,
    *,
    temperature: float | None = None,
    count: int | None = None,
    max_new_tokens: int | None = None,
    return_token_ids: bool = False,
    greedy_fraction: float | None = None,
) -> tuple[list[str], str] | tuple[list[str], str, torch.Tensor, torch.Tensor, list[torch.Tensor]]:
    """Generate a group and return the raw decoded responses plus prompt text.

    Do not extract code here. Policy old/current/post log-probabilities must be
    computed on the same response text that was sampled. The caller derives a
    separate executable-code view for the harness.

    Args:
        temperature: Override the base sampling temperature.  When adaptive
            temperature escalation is active, pass the escalated value here.
            Falls back to ``args.temperature`` if not specified.
        count: Number of solutions to generate. Defaults to ``args.group_size``;
            the posterior router may recommend 4/8/16 adaptively (review
            2026-08-05 #4).
        return_token_ids: Also return the exact prompt IDs, prompt attention
            mask, and generated completion IDs used by ``model.generate``.
            The default preserves the existing two-value text API.
        greedy_fraction: 2026-08-26 (r10, greedy-augmented rollouts): the
            fraction of the group generated at temperature 0 (greedy argmax)
            and graded through the SAME harness/reward path. Overrides
            ``args.greedy_rollout_fraction``; both default to 0.0 (the
            byte-identical cold path). The first ``greedy_rollout_count``
            candidates are greedy, the rest sampled.
    """
    text = render_generation_prompt(backend.render_backend, prompt)
    tokenizer_batch = backend.text_backend(text, return_tensors="pt")
    # 2026-08-26 (r10, launch-simulator F2): the tokenizer batch can carry
    # fields model.generate() cannot forward (token_type_ids,
    # special_tokens_mask...) — filter to the model's input names.
    inputs = move_batch_to_device(filter_generation_inputs(model, tokenizer_batch), args.device)
    effective_temp = temperature if temperature is not None else args.temperature
    group_size = count if count is not None else args.group_size
    effective_max_new_tokens = (
        int(max_new_tokens) if max_new_tokens is not None else int(args.max_new_tokens)
    )
    # 2026-08-26 (r10, manager TOP-PRIORITY wave): greedy-augmented rollouts.
    # The first `greedy_count` candidates are generated at temperature 0
    # (greedy argmax) so the policy learns under the exact evaluation
    # protocol; they enter the group with their TRUE rewards/advantages (the
    # loss math is untouched — only the group composition changes).
    greedy_fraction = float(
        greedy_fraction
        if greedy_fraction is not None
        else (getattr(args, "greedy_rollout_fraction", 0.0) or 0.0)
    )
    greedy_count = greedy_rollout_count(group_size, greedy_fraction)
    # 2026-08-25 (generation-efficiency): stop at the first EOS resolved from
    # the model config OR the tokenizer — the base config can omit
    # eos_token_id, which made every step run the full max-new-tokens cap
    # (60-110 min/step). The closing-fence criterion below is the primary
    # stopper; EOS and max-new-tokens are the backstops.
    stop_eos_ids = configured_eos_token_ids(model, backend.text_backend)
    # 2026-09-11 (Qwen3.8-27B GRPO no-progress root cause): Qwen3.8's
    # generation_config declares 248044 as BOS + PAD + a second EOS, so the
    # stop union made the sequence-start/pad marker a legal rollout end — every
    # candidate died after 2-4 tokens (all rewards 0, 7/7 steps skipped). The
    # id is suppressed during decode (never sampled) while the genuine chat EOS
    # 248046 stays in the stop set; the helper returns an EMPTY set unless at
    # least one real EOS remains, so generation can never lose its stop.
    suppress_token_ids = configured_suppress_token_ids(
        model, backend.text_backend, stop_eos_ids=stop_eos_ids
    )

    raw_responses = []
    completion_token_ids: list[torch.Tensor] = []
    prompt_token_ids = inputs["input_ids"][0].detach().cpu().clone()
    prompt_attention_mask = inputs.get("attention_mask")
    if prompt_attention_mask is None:
        exact_prompt_attention_mask = torch.ones_like(prompt_token_ids)
    else:
        exact_prompt_attention_mask = prompt_attention_mask[0].detach().cpu().clone()
    model_config = getattr(model, "config", None)
    previous_use_cache = getattr(model_config, "use_cache", None)
    if model_config is not None:
        # Gradient checkpointing requires use_cache=False for grad-enabled
        # forwards, but rollouts run in eval/no-grad. Re-enable the KV cache
        # here or autoregressive generation becomes quadratic and a 27B step
        # can spend many minutes before producing one candidate.
        model_config.use_cache = True
    try:
        # 2026-08-28 (architect, root-cause of 2-week no-progress): the OLD loop
        # generated each candidate SERIALLY (one model.generate per index) on a
        # 27B sharded across 8 NPUs — the documented 60-110 min/step cost. This
        # BATCHED version repeats the shared prompt to the whole group in ONE
        # generate call (greedy subset in a second, do_sample=False call) so the
        # 8 devices decode all candidates in parallel (~8x). Greedy (temp-0)
        # candidates are emitted first per the greedy-augmentation contract; the
        # fence stopper and EOS handling are unchanged (both are batch-safe).
        prompt_len = int(inputs["input_ids"].shape[1])
        # 2026-08-31 (Lane A, Tier-1): vLLM rollout seam. When SAPO_VLLM_URL is
        # set, decode TEXT via the vLLM server (continuous batching, 10-50x),
        # re-tokenize to completion ids, and SKIP both model.generate calls.
        # Policy logprobs are later computed by the forward pass over
        # (prompt+completion) — mathematically identical to the decode-path.
        # Fail-closed: any vLLM error falls back to the transformers decode.
        _vllm_url = os.environ.get("SAPO_VLLM_URL", "").strip()
        _vllm_succeeded = False
        if _vllm_url:
            try:
                from training.vllm_rollout_client import VllmRolloutClient, VllmUnavailable

                _client = VllmRolloutClient(_vllm_url)
                if not _client.is_up(force=True):
                    raise VllmUnavailable("health check failed")
                greedy_n2 = greedy_count
                sampled_n2 = max(group_size - greedy_n2, 0)
                raw_responses.clear()
                completion_token_ids.clear()
                prompt_text_ids = inputs["input_ids"][0].detach().cpu().tolist()
                prompt_text = backend.text_backend.decode(prompt_text_ids, skip_special_tokens=True)
                if greedy_n2 > 0:
                    greedy_texts = _client.generate_batch(
                        prompt_text,
                        greedy_n2,
                        int(effective_max_new_tokens),
                        0.0,
                        suppress_token_ids=sorted(suppress_token_ids),
                    )
                else:
                    greedy_texts = []
                if sampled_n2 > 0:
                    sampled_texts = _client.generate_batch(
                        prompt_text,
                        sampled_n2,
                        int(effective_max_new_tokens),
                        effective_temp,
                        suppress_token_ids=sorted(suppress_token_ids),
                    )
                else:
                    sampled_texts = []
                for t in greedy_texts + sampled_texts:
                    # 2026-09-01 (Lane A closure, distribution parity): the
                    # vLLM server stops only on EOS/cap — a model that never
                    # samples EOS returns fence-closed completions WITH
                    # trailing prose. Truncate at the closing fence to match
                    # the transformers decode path (StopAfterClosedCodeFence
                    # is the primary stopper there), then re-tokenize. The
                    # shared fence_stop_marker block below appends the EOS
                    # training target — do NOT return early from the try.
                    fenced_t = truncate_at_closing_fence(t)
                    ids = (
                        backend.text_backend(fenced_t, return_tensors="pt")["input_ids"][0]
                        .detach()
                        .cpu()
                    )
                    raw_responses.append(fenced_t)
                    completion_token_ids.append(ids)
                _release_device_cache(torch)
                if not return_token_ids:
                    return raw_responses, prompt
                _vllm_succeeded = True
            except ImportError as _imp_err:
                # 2026-09-01 (Lane A audit): a deployed bundle without the
                # client module must degrade like any other vLLM failure —
                # loud stage line, transformers fallback — NOT crash the
                # trainer with an uncaught ModuleNotFoundError.
                print(
                    json.dumps(
                        {
                            "stage": "vllm_rollout_unavailable",
                            "reason": f"client module missing: {_imp_err}"[:160],
                        }
                    ),
                    flush=True,
                )
                raw_responses.clear()
                completion_token_ids.clear()
                _vllm_succeeded = False
            except VllmUnavailable as _exc:
                print(
                    json.dumps({"stage": "vllm_rollout_unavailable", "reason": str(_exc)[:160]}),
                    flush=True,
                )
                raw_responses.clear()
                completion_token_ids.clear()
                _vllm_succeeded = False
        greedy_n = greedy_count if not _vllm_succeeded else 0
        sampled_n = max(group_size - greedy_n, 0) if not _vllm_succeeded else 0
        if greedy_n > 0:
            # C-9523: bounded generation watchdog. A dead ASCEND NPU TBE
            # task_distribute subprocess makes model.generate never return
            # (trainer busy-spins at >130% CPU, child futex-blocked). The
            # watchdog fails fast-closed on GRPO_GENERATION_TIMEOUT_S instead
            # of spinning the whole budget.
            greedy_out = run_bounded_generation(
                lambda: _generate_with_no_grad(
                    model,
                    inputs=inputs,
                    group_size=greedy_n,
                    max_new_tokens=effective_max_new_tokens,
                    temperature=0.0,
                    top_p=args.top_p,
                    do_sample=False,
                    stop_eos_ids=stop_eos_ids,
                    suppress_token_ids=suppress_token_ids,
                    backend=backend,
                    prompt_len=prompt_len,
                ),
                label="greedy_generate_%d" % greedy_n,
            )
            for gids in greedy_out.sequences:
                gen_ids = gids[prompt_len:]
                raw_responses.append(backend.text_backend.decode(gen_ids, skip_special_tokens=True))
                completion_token_ids.append(gen_ids.detach().cpu().clone())
            _release_device_cache(torch)
        if sampled_n > 0:
            # C-9523: bounded generation watchdog (see greedy block above).
            sampled_out = run_bounded_generation(
                lambda: _generate_with_no_grad(
                    model,
                    inputs=inputs,
                    group_size=sampled_n,
                    max_new_tokens=effective_max_new_tokens,
                    temperature=effective_temp,
                    top_p=args.top_p,
                    do_sample=True,
                    stop_eos_ids=stop_eos_ids,
                    suppress_token_ids=suppress_token_ids,
                    backend=backend,
                    prompt_len=prompt_len,
                ),
                label="sampled_generate_%d" % sampled_n,
            )
            for sids in sampled_out.sequences:
                gen_ids = sids[prompt_len:]
                raw_responses.append(backend.text_backend.decode(gen_ids, skip_special_tokens=True))
                completion_token_ids.append(gen_ids.detach().cpu().clone())
            _release_device_cache(torch)
    finally:
        if model_config is not None and previous_use_cache is not None:
            model_config.use_cache = previous_use_cache

    # 2026-08-26 (r10, synthetic stop marker): fence-closed completions get
    # the resolved EOS id appended as the termination training target (the
    # model never samples EOS itself — run-6 S1-S5 eos_termination_rate 0.0).
    # The raw texts stay untouched; both log-prob passes share the augmented
    # ids. Disabled via --no-fence-stop-marker for ablations.
    if getattr(args, "fence_stop_marker", True):
        completion_token_ids, _ = append_fence_stop_markers(
            completion_token_ids,
            raw_responses,
            stop_eos_ids,
            tokenizer=backend.text_backend,
        )

    if return_token_ids:
        return (
            raw_responses,
            text,
            prompt_token_ids,
            exact_prompt_attention_mask,
            completion_token_ids,
        )
    return raw_responses, text


def compute_completion_log_prob(
    model,
    tokenizer,
    prompt_text: str,
    completion_text: str,
    device: Any,
    max_seq_length: int,
    logit_clip: float,
    *,
    add_mm_token_type_ids: bool = False,
    return_entropy: bool = False,
    return_token_log_probs: bool = False,
    policy_temperature: float = 1.0,
    prompt_token_ids: torch.Tensor | None = None,
    prompt_attention_mask: torch.Tensor | None = None,
    completion_token_ids: torch.Tensor | None = None,
    train_seq_cap: int | None = None,
    entropy_token_cap: int | None = None,
    recompute_backward: bool = True,
) -> tuple[torch.Tensor, torch.Tensor] | tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Compute the completion log-prob (and optional entropy/token lps).

    ``train_seq_cap`` caps the TOTAL sequence for the train pass only
    (2026-08-25 OOM fix): at most the first ``train_seq_cap`` tokens enter the
    log-prob computation; the completion tail beyond the cap is dropped from
    the update. The prompt is never truncated (a cap shorter than the prompt
    leaves the sequence at prompt length, which yields a zero-token completion
    and is handled by the caller as a skip). Rollout callers (old policy,
    entropy stats) pass no cap and keep the full sequence."""
    exact_id_mode = prompt_token_ids is not None or completion_token_ids is not None
    if exact_id_mode and (prompt_token_ids is None or completion_token_ids is None):
        raise ValueError("prompt_token_ids and completion_token_ids must be provided together")
    if exact_id_mode:
        prompt_ids = prompt_token_ids.detach().long().reshape(1, -1)
        completion_ids = completion_token_ids.detach().long().reshape(1, -1)
        full_ids = torch.cat((prompt_ids, completion_ids), dim=1)
        if max_seq_length > 0:
            full_ids = full_ids[:, :max_seq_length]
        if train_seq_cap and train_seq_cap > 0 and full_ids.shape[1] > train_seq_cap:
            cap_len = max(int(train_seq_cap), int(prompt_ids.shape[1]))
            full_ids = full_ids[:, :cap_len]
        if prompt_attention_mask is None:
            prompt_mask = torch.ones_like(prompt_ids)
        else:
            prompt_mask = prompt_attention_mask.detach().long().reshape(1, -1)
            if prompt_mask.shape != prompt_ids.shape:
                raise ValueError("prompt_attention_mask must match prompt_token_ids")
        full_attention_mask = torch.cat((prompt_mask, torch.ones_like(completion_ids)), dim=1)[
            :, : full_ids.shape[1]
        ]
        full_inputs = {
            "input_ids": full_ids,
            "attention_mask": full_attention_mask,
        }
        prompt_len = min(prompt_ids.shape[1], full_ids.shape[1])
    else:
        prompt_inputs = tokenizer(
            prompt_text, return_tensors="pt", truncation=True, max_length=max_seq_length
        )
        full_inputs = tokenizer(
            prompt_text + completion_text,
            return_tensors="pt",
            truncation=True,
            max_length=max_seq_length,
        )
        prompt_len = min(prompt_inputs["input_ids"].shape[1], full_inputs["input_ids"].shape[1])
        if (
            train_seq_cap
            and train_seq_cap > 0
            and full_inputs["input_ids"].shape[1] > train_seq_cap
        ):
            cap_len = max(int(train_seq_cap), int(prompt_len))
            full_inputs["input_ids"] = full_inputs["input_ids"][:, :cap_len]
            if "attention_mask" in full_inputs:
                full_inputs["attention_mask"] = full_inputs["attention_mask"][:, :cap_len]
    if add_mm_token_type_ids:
        full_inputs["mm_token_type_ids"] = torch.zeros_like(full_inputs["input_ids"])
    full_inputs = move_batch_to_device(full_inputs, device)

    outputs = model(**full_inputs)
    logits = outputs.logits[:, :-1, :]
    target_ids = full_inputs["input_ids"][:, 1:]

    completion_mask = torch.zeros_like(target_ids, dtype=torch.bool)
    completion_start = max(prompt_len - 1, 0)
    completion_mask[:, completion_start:] = True
    attention_mask = full_inputs.get("attention_mask")
    if attention_mask is not None:
        completion_mask &= attention_mask[:, 1:].bool()
    token_count = completion_mask.sum()
    if token_count.item() == 0:
        zero = logits.new_tensor(0.0)
        # SAPO callers unpack the per-token log-prob slot too — return it or
        # the unpack ValueError kills the whole run (2026-08-21 review #1).
        if return_entropy:
            if return_token_log_probs:
                return zero, token_count, zero, zero
            return zero, token_count, zero
        if return_token_log_probs:
            return zero, token_count, zero
        return zero, token_count
    # Chunked-vocab pass: full-vocab fp32 logits/softmax spike multiple GB on the
    # lm_head NPU of the sharded 27B (the ASI2 stall zone) — chunked avoids it.
    # 2026-08-26 (run-8 OOM root cause): when the entropy-floor branch is
    # requested, ``entropy_token_cap`` bounds it to the first N COMPLETION
    # tokens (a floor needs a rough mean) — the branch's retained per-chunk
    # fp32 tensors are what pushed the train pass from run-5's ~10.5 GiB to
    # run-8's 59.8 GiB peak. Rollout callers pass no cap (full entropy for
    # the degenerate-alarm stats; no-grad there anyway).
    entropy_pos_cap = resolve_entropy_pos_cap(prompt_len, entropy_token_cap, logits.shape[1])
    result = chunked_log_probs_and_entropy(
        logits,
        target_ids,
        logit_clip,
        return_entropy=return_entropy,
        policy_temperature=policy_temperature,
        entropy_pos_cap=entropy_pos_cap,
        recompute_backward=recompute_backward,
    )
    if return_entropy:
        token_log_probs, entropy_per_pos = result
        seq_log_prob = token_log_probs.masked_select(completion_mask).sum()
        if entropy_pos_cap is not None:
            # The capped branch is zero beyond the cap: slice the ENTROPY
            # tensor to the cap region too (masked_select needs equal
            # lengths) so the mean is over the first ``entropy_token_cap``
            # completion tokens (count = min(cap, completion length)). NOTE:
            # a SEPARATE mask — ``completion_mask`` stays full for the SAPO
            # token-lps and seq log-prob below.
            entropy_mask = completion_mask[:, :entropy_pos_cap]
            entropy_per_pos = entropy_per_pos[:, :entropy_pos_cap]
        else:
            entropy_mask = completion_mask
        masked_entropy = entropy_per_pos.masked_select(entropy_mask)
        entropy = masked_entropy.mean() if masked_entropy.numel() else logits.new_tensor(0.0)
        if return_token_log_probs:
            # NOT detached: the train-logprob phase needs the gradient path
            # (SAPO token-level loss). Rollout callers run under torch.no_grad().
            masked_tokens = token_log_probs.masked_select(completion_mask)
            return seq_log_prob, token_count, entropy, masked_tokens
        return seq_log_prob, token_count, entropy
    token_log_probs = result
    seq_log_prob = token_log_probs.masked_select(completion_mask).sum()
    if return_token_log_probs:
        masked_tokens = token_log_probs.masked_select(completion_mask)
        return seq_log_prob, token_count, masked_tokens
    return seq_log_prob, token_count


def grpo_loss(
    log_probs: torch.Tensor,
    old_log_probs: torch.Tensor,
    advantages: torch.Tensor,
    kl_coeff: float,
    ratio_clip_log_delta: float,
) -> torch.Tensor:
    """GRPO loss: policy gradient with group-relative advantages + KL penalty."""
    return stable_grpo_loss(
        log_probs=log_probs,
        old_log_probs=old_log_probs,
        advantages=advantages,
        kl_coeff=kl_coeff,
        ratio_clip_log_delta=ratio_clip_log_delta,
    )


def compute_dr_pair_loss(
    *,
    research_methods: list[Any],
    rewards: torch.Tensor,
    codes: list[str],
    current_log_probs: list[torch.Tensor],
    old_log_probs: list[torch.Tensor],
) -> tuple[torch.Tensor, dict[str, Any]]:
    """Compute the doubly-robust DPO pair loss when the plugin is enabled.

    Returns (loss, info) where `loss` is a scalar tensor (zero if the
    plugin is disabled or no pair was mined) and `info` is a dict with
    debugging fields (`dr_pair_mined`, `dr_pair_reward_gap`,
    `dr_pair_loss_value`).

    This is a no-op when no research method matches
    `doubly_robust_quantum_grpo`. The pair loss is weighted by
    `dr_pair_loss_weight` (default 0.3) read from the plugin's
    `extra_run_config()`.
    """
    info: dict[str, Any] = {
        "dr_pair_mined": False,
        "dr_pair_reward_gap": 0.0,
        "dr_pair_loss_value": 0.0,
        "dr_pair_loss_weight": 0.0,
    }
    if not research_methods:
        zero = rewards.new_tensor(0.0) if rewards is not None else None
        if zero is None:
            import torch as _torch

            zero = _torch.zeros((), dtype=_torch.float32)
        return zero, info

    method = next(
        (m for m in research_methods if m.method_id == "doubly_robust_quantum_grpo"),
        None,
    )
    if method is None:
        zero = rewards.new_tensor(0.0) if rewards is not None else None
        if zero is None:
            import torch as _torch

            zero = _torch.zeros((), dtype=_torch.float32)
        return zero, info

    cfg = method.extra_run_config().get("doubly_robust_quantum_grpo", {})
    beta = float(cfg.get("dr_dpo_beta", 0.07))
    min_gap = float(cfg.get("dr_pair_min_reward_gap", 0.4))
    max_pairs = int(cfg.get("dr_pair_max_per_step", 1))
    weight = float(cfg.get("dr_pair_loss_weight", 0.3))
    info["dr_pair_loss_weight"] = weight
    if weight <= 0.0 or max_pairs <= 0:
        zero = rewards.new_tensor(0.0)
        return zero, info

    # Lazy import so the trainer does not hard-depend on the plugin module.
    try:
        import importlib.util
        import sys as _sys

        plugin_root = (
            Path(__file__).resolve().parents[1]
            / "research"
            / "papers"
            / "doubly_robust_quantum_grpo"
            / "code"
        )
        spec = importlib.util.spec_from_file_location(
            "dr_pair_loss_mod", plugin_root / "dr_pair_loss.py"
        )
        if spec is None or spec.loader is None:
            zero = rewards.new_tensor(0.0)
            return zero, info
        mod = importlib.util.module_from_spec(spec)
        # Register the module in sys.modules before exec so that
        # @dataclass(frozen=True) inside the plugin can resolve the
        # module namespace.
        _sys.modules["dr_pair_loss_mod"] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception:
            _sys.modules.pop("dr_pair_loss_mod", None)
            raise
    except Exception:
        zero = rewards.new_tensor(0.0)
        return zero, info

    pairs = mod.build_dr_pairs(
        rewards=rewards,
        codes=codes,
        min_reward_gap=min_gap,
        max_pairs=max_pairs,
    )
    if not pairs:
        zero = rewards.new_tensor(0.0)
        return zero, info

    info["dr_pair_mined"] = True
    info["dr_pair_reward_gap"] = float(pairs[0].reward_gap)

    log_probs_tensor = torch.stack(current_log_probs)
    ref_log_probs_tensor = torch.stack(old_log_probs).detach()
    pair_loss = mod.dr_pair_loss(
        log_probs=log_probs_tensor,
        ref_log_probs=ref_log_probs_tensor,
        pairs=pairs,
        beta=beta,
        device=log_probs_tensor.device,
    )
    if not torch.isfinite(pair_loss):
        zero = rewards.new_tensor(0.0)
        return zero, info

    weighted = weight * pair_loss
    info["dr_pair_loss_value"] = float(pair_loss.item())
    return weighted, info


def compute_dr_variance_correction(
    *,
    research_methods: list[Any],
    log_probs: torch.Tensor,
    old_log_probs: torch.Tensor,
    advantages: torch.Tensor,
    ratio_clip_log_delta: float,
    current_step: int | None = None,
) -> tuple[torch.Tensor, dict[str, Any]]:
    """Compute the doubly-robust PPO-side variance correction.

    The DR estimator is

        L_DR = L_PPO + psi * E[ (r - 1) * A ]

    where `r = exp(log_probs - old_log_probs)` is the PPO importance
    ratio and `A` is the (detached) group-relative advantage. The
    correction has zero mean under the behavior policy but reduces
    variance when the behavior policy is close to the target, which is
    the "doubly robust" guarantee (see paper.md §2 and
    arXiv:2506.01183).

    Returns (correction_term, info). The correction term is added to
    `total_loss` by the caller. When the `doubly_robust_quantum_grpo`
    plugin is absent or `dr_psi_init == 0`, returns a zero tensor so
    this is safe for base GRPO.
    """
    info: dict[str, Any] = {
        "dr_variance_correction_value": 0.0,
        "dr_psi": 0.0,
    }
    if not research_methods:
        zero = log_probs.new_tensor(0.0) if log_probs is not None else None
        if zero is None:
            import torch as _torch

            zero = _torch.zeros((), dtype=_torch.float32)
        return zero, info

    method = None
    for m in research_methods:
        if getattr(m, "method_id", "") == "doubly_robust_quantum_grpo":
            method = m
            break
    if method is None:
        zero = log_probs.new_tensor(0.0)
        return zero, info

    cfg = method.extra_run_config().get("doubly_robust_quantum_grpo", {})
    psi_init = float(cfg.get("dr_psi_init", 0.0))
    warmup_steps = int(float(cfg.get("dr_psi_warmup_steps", 0)))
    # Linear psi warmup: psi ramps 0 -> psi_init over the first
    # `dr_psi_warmup_steps` training steps, then holds at psi_init.
    # Matches the paper's "tune psi after warmup" guidance and reduces
    # early-step variance. When warmup_steps == 0 (default), psi is
    # constant — preserves the pre-warmup behavior.
    if warmup_steps > 0 and current_step is not None and current_step < warmup_steps:
        psi = psi_init * (float(current_step) / float(warmup_steps))
    else:
        psi = psi_init
    info["dr_psi"] = psi
    info["dr_psi_init"] = psi_init
    info["dr_psi_warmup_steps"] = warmup_steps
    info["dr_psi_current_step"] = int(current_step) if current_step is not None else None
    if psi == 0.0:
        zero = log_probs.new_tensor(0.0)
        return zero, info

    # Reuse the plugin helper if importable; fall back to inline math.
    try:
        import sys as _sys

        plugin_root = Path(__file__).resolve().parent.parent / (
            "research/papers/doubly_robust_quantum_grpo/code"
        )
        spec = importlib.util.spec_from_file_location(
            "dr_pair_loss_mod_v2", plugin_root / "dr_pair_loss.py"
        )
        if spec is not None and spec.loader is not None:
            mod = importlib.util.module_from_spec(spec)
            _sys.modules["dr_pair_loss_mod_v2"] = mod
            try:
                spec.loader.exec_module(mod)
            except Exception:
                _sys.modules.pop("dr_pair_loss_mod_v2", None)
                raise
            log_ratio = (log_probs - old_log_probs.detach()).clamp(
                -ratio_clip_log_delta, ratio_clip_log_delta
            )
            ppo_ratio = torch.exp(log_ratio)
            correction = mod.dr_variance_correction(
                ppo_loss=log_probs.new_tensor(0.0),  # unused; helper adds to ppo_loss
                ppo_ratio=ppo_ratio,
                advantages=advantages.detach(),
                psi=psi,
            )
            # dr_variance_correction returns ppo_loss + psi*((r-1)*A).mean();
            # subtract the unused ppo_loss (0.0) so we isolate the correction.
            correction = correction - 0.0
            if not torch.isfinite(correction):
                zero = log_probs.new_tensor(0.0)
                return zero, info
            info["dr_variance_correction_value"] = float(correction.item())
            return correction, info
    except Exception:
        pass

    # Inline fallback (matches dr_variance_correction math).
    log_ratio = (log_probs - old_log_probs.detach()).clamp(
        -ratio_clip_log_delta, ratio_clip_log_delta
    )
    ppo_ratio = torch.exp(log_ratio)
    correction = psi * ((ppo_ratio - 1.0) * advantages.detach()).mean()
    if not torch.isfinite(correction):
        zero = log_probs.new_tensor(0.0)
        return zero, info
    info["dr_variance_correction_value"] = float(correction.item())
    return correction, info


def observe_and_evaluate_breakers(
    breaker: CircuitBreakerState,
    *,
    step: int,
    route: str,
    non_finite: bool,
    clip_fraction: float,
    entropy_mean: float | None,
    repair_queued: bool,
    repair_converted_jsonl: str | None,
    all_fail: bool,
    completion_token_lengths: list[int] | None = None,
    eos_termination_rate: float | None = None,
    truncation_rate: float | None = None,
    fence_termination_rate: float | None = None,
) -> list[dict[str, Any]]:
    """Feed one step's facts to the circuit-breaker monitor and evaluate rules.

    Returns newly tripped breaker events (see ``CircuitBreakerState.evaluate``).

    ``completion_token_lengths`` and ``eos_termination_rate`` are the generation
    diagnostics the caller already holds; they feed the B-125 response-length
    collapse floor, which is evaluated on EVERY step (not only on a window
    boundary) because an immediate-EOS collapse is conclusive within a handful
    of steps. Omitting them leaves every pre-existing rule unchanged.
    """
    breaker.observe_step(
        step=step,
        route=route,
        non_finite=non_finite,
        clip_fraction=clip_fraction,
        entropy=entropy_mean,
        repair_queued=repair_queued,
        repair_converted=count_repair_conversions(repair_converted_jsonl),
        all_fail_share=1.0 if all_fail else 0.0,
        completion_token_lengths=completion_token_lengths,
        eos_termination_rate=eos_termination_rate,
        truncation_rate=truncation_rate,
        fence_termination_rate=fence_termination_rate,
    )
    return breaker.evaluate(step=step)


# 2026-08-25: hard ceiling on behavior sampling temperature. Run-3 of the
# SAPO loop died at step 42 with temperature ramped to 1.75 — entropy
# exploded 2.9 -> 4.2 -> 6.4, candidates collapsed into pure SyntaxErrors,
# reward hit exactly 0.0, more repair skips -> positive-feedback cascade ->
# ``no_trainable_tasks``. Behavior temperature must never exceed 1.3
# regardless of the escalation ladder (--adaptive-temp-max, or a resumed
# state file carrying a higher ceiling).
TEMP_ESCALATION_CEILING: float = 1.3


def clamp_adaptive_behavior_temperature(temperature: float) -> float:
    """Hard ceiling on behavior sampling temperature (2026-08-25).

    Applies at the single ``effective_temperature`` computation site so the
    cap holds even when the ladder's ``max_temp`` (or a resumed state file)
    is higher than 1.3.
    """
    return min(float(temperature), TEMP_ESCALATION_CEILING)


# ───────────────────────────────────────────────────────────────────────────
# 2026-08-26 (r10, run-6 killer): EOS-collapse / degenerate-policy rescue
#
# Run-6 evidence: 16 CONSECUTIVE repair skips, then ``no_trainable_tasks``.
# Step 25 generated completion_token_lengths [1,1,1,1] with max_code_chars 0,
# eos_terminated true on all 4 candidates, entropy 0.0137 — and temperature
# STUCK at 1.15. The 2026-08-25 no-escalate patch (correct: high-entropy
# repair skips must never ramp, run-3's 1.0 -> 1.75 spiral) also left the
# collapsed class WITHOUT a rescue: repair-routing precedes the low-entropy
# cold-task escalation check, so a collapsed policy is never rescued and the
# run dies through the repair-queue cascade.
# ───────────────────────────────────────────────────────────────────────────

DEGENERATE_POLICY_ENTROPY_MAX: float = 0.05
DEGENERATE_POLICY_MAX_COMPLETION_TOKENS: int = 1
DEGENERATE_POLICY_CONSECUTIVE_STEPS: int = 3


def is_degenerate_policy_step(
    *,
    entropy_mean: float | None,
    completion_token_lengths: list[int] | None,
) -> bool:
    """True when ONE step shows the EOS-collapse signature.

    Both conditions are required: near-zero sampling entropy (< 0.05, the
    confident-but-wrong single mode) AND every completion collapsed to ~1
    token (e.g. [1,1,1,1] — the model emits a token and stops). Either alone
    (long-but-low-entropy, or short-but-diverse) is a different failure mode.
    """
    if entropy_mean is None or not completion_token_lengths:
        return False
    if float(entropy_mean) >= DEGENERATE_POLICY_ENTROPY_MAX:
        return False
    return max(int(length) for length in completion_token_lengths) <= (
        DEGENERATE_POLICY_MAX_COMPLETION_TOKENS
    )


class DegeneratePolicyDetector:
    """Tracks consecutive degenerate steps and fires the rescue alarm.

    The alarm raises on the Nth consecutive degenerate step (N=3). When it
    fires, the behavior temperature must escalate IMMEDIATELY — before
    repair-routing swallows the group — because a collapsed sampling policy
    is a GLOBAL temperature problem, not a per-task routing decision.

    NOTE: the detector streak is in-memory only. After a soft-resume the
    streak restarts and re-arms after 3 degenerate steps; the ladder itself
    (``AdaptiveTemperatureState``) survives resume via the persisted state.
    """

    def __init__(self, *, window: int = DEGENERATE_POLICY_CONSECUTIVE_STEPS) -> None:
        self.window = window
        self.consecutive_degenerate: int = 0

    def observe(
        self,
        *,
        entropy_mean: float | None,
        completion_token_lengths: list[int] | None,
    ) -> bool:
        """Feed one step; returns True from the window-crossing step onward
        (the 3rd consecutive degenerate step and EVERY subsequent degenerate
        step, so the rescue ladder keeps escalating during an ongoing
        collapse). A healthy step resets the streak."""
        if is_degenerate_policy_step(
            entropy_mean=entropy_mean,
            completion_token_lengths=completion_token_lengths,
        ):
            self.consecutive_degenerate += 1
        else:
            self.consecutive_degenerate = 0
        return self.consecutive_degenerate >= self.window


def alarm_degenerate_policy(
    detector: DegeneratePolicyDetector,
    adaptive_temp: AdaptiveTemperatureState,
    *,
    entropy_mean: float | None,
    completion_token_lengths: list[int] | None,
) -> bool:
    """Feed one step to the EOS-collapse detector; on the window-crossing step
    escalate behavior temperature IMMEDIATELY and return True. The caller
    emits the loud log line + ``degenerate_policy_alarm`` step-record flag.
    """
    if not detector.observe(
        entropy_mean=entropy_mean,
        completion_token_lengths=completion_token_lengths,
    ):
        return False
    # The collapsed policy is a GLOBAL sampling-temperature problem: escalate
    # the ladder NOW, before repair-routing (repair-routed skips never
    # escalate — 2026-08-25 contract — so without this the collapsed mode
    # persists until no_trainable_tasks, run-6's 16-skip death).
    adaptive_temp.record_skip(DEGENERATE_POLICY_REASON)
    return True


# 2026-08-27 (T1a, algorithm audit): quarantine-integrity gate. A collapsed
# policy must NEVER produce evidence-free quarantines — run-6 quarantined ALL
# 20 tasks (incl. the 5 learnable ones) under the EOS collapse because
# repair-routing fires on any flat all-fail regardless of policy health.
QUARANTINE_GATE_COLLAPSE_MAX_TOKENS: int = 8

# 2026-09-11 (algorithm lane, run-20260909T104517Z warm-continue post-mortem):
# the entropy clause was unbounded in completion length, so a
# LONG-but-low-entropy group was quarantined exactly like a 1-token EOS
# collapse. Evidence from the live step records: step 2 sampled entropy_mean
# 0.00158 with completion_token_lengths [2048, 2048, 302, 2048],
# cap_run_with_fence_opener_rate 0.5 and extracted_code_chars
# [6211, 6211, 884, 6336] — i.e. real (if rambling) code bodies, not
# evidence-free 1-token stubs. Because quarantine skips the reward pass, the
# synthesized zero rewards forced ``update_signal_magnitude`` to 0.0 and the
# step landed in the ``low_reward_signal`` skip: 97 of 100 steps ran with
# lr 0.0 and seq_kl 0.0, so the policy could never leave the state that kept
# re-triggering the gate. Low entropy is only a collapse signature while the
# completions are too short to carry evidence; this bound sits between the
# stub bound (8) and the shortest evidence-bearing completion observed in the
# live runs (142 tokens at run-20260909 step 18; 256 in the parent run
# 20260908T094427Z).
QUARANTINE_GATE_ENTROPY_MAX_TOKENS: int = 64


def quarantine_gate_active(
    *,
    degenerate_policy_alarm: bool,
    entropy_mean: float | None,
    completion_token_lengths: list[int] | None,
    collapse_max_tokens: int = QUARANTINE_GATE_COLLAPSE_MAX_TOKENS,
    entropy_max_tokens: int = QUARANTINE_GATE_ENTROPY_MAX_TOKENS,
) -> bool:
    """True when this step shows a policy-collapse signature — quarantine and
    repair-routing must be suppressed.

    Engages on ANY of:
    - the 3-step degenerate alarm (r10) fired on this step;
    - entropy below the degenerate floor (0.05) AND an all-short group
      (every completion below ``entropy_max_tokens``, 64) — the
      confident-wrong single-mode collapse (run-6 step 25: entropy 0.0136 on
      [1,1,1,1]). The length bound is load-bearing: a long completion is
      evidence-bearing, so a low-entropy-but-long group must run its reward
      pass instead of being quarantined (2026-09-11, run-20260909: entropy
      0.00158 with 302-2048-token completions and 6211-char code bodies;
      unbounded, this clause froze 97/100 steps at lr 0.0 — see the constant's
      post-mortem comment);
    - a stub-collapse group: EVERY completion shorter than 8 tokens (the
      near-EOS-collapse class even at non-tiny entropy).

    Deliberately does NOT use the loss entropy-floor (1.5): that bar would
    gate healthy cold-task steps (run-5's s11/s12 repairs ran at entropy
    0.25-0.32) and starve the repair lane.
    """
    if degenerate_policy_alarm:
        return True
    if entropy_mean is not None and float(entropy_mean) < DEGENERATE_POLICY_ENTROPY_MAX:
        return True
    if completion_token_lengths and max(int(length) for length in completion_token_lengths) < int(
        collapse_max_tokens
    ):
        return True
    return False


def escalate_temperature_on_flat_route(
    adaptive_temp: AdaptiveTemperatureState,
    *,
    route: str,
    all_fail: bool = False,
    entropy_mean: float | None = None,
    low_entropy_threshold: float = 0.45,
) -> None:
    """Escalate adaptive sampling temperature for diversity-failure groups.

    2026-08-25 correction: repair-routed skips (``route=repair_sft``, emitted
    as ``reason=repair_sft_queued``) are ROUTING decisions — the task moves to
    the repair SFT lane — not low-signal outcomes, and they must NOT count
    toward the flat-route escalation counter. The 2026-08-24 patch escalated
    on every repair-route skip, which let 5 consecutive repair skips ramp
    temperature 1.0 -> 1.75 in run-3 and drive the entropy-explosion death
    spiral at step 42 (see reports/sapo-temp-escalation-patch-2026-08-25.md).

    Only genuine low-signal classes escalate:
    - an all-fail RL group sampled below ``low_entropy_threshold`` (the
      cold-task class: a confident-but-wrong single mode) escalates so the
      NEXT group diversifies;
    - 2026-08-26 (r10, run-6 killer): an all-fail REPAIR-routed group sampled
      below ``low_entropy_threshold`` is the same cold-collapse class — a
      confident-but-wrong single mode (run-6 step 25: entropy 0.0137,
      completions [1,1,1,1]). Repair-routing must NOT swallow the rescue
      signal: run-6 died with 16 consecutive repair skips, temp stuck at
      1.15, then ``no_trainable_tasks``. These groups escalate BEFORE the
      repair-routing branch continues. High-entropy repair-routed groups
      (the run-3 death-spiral class: entropy 2.9 -> 6.4) still never
      escalate;
    - INVALID_OR_NOISY quarantines an unstable task, which is not a diversity
      failure, so it never escalates.
    The behavior temperature itself is additionally hard-capped at 1.3 by
    ``clamp_adaptive_behavior_temperature`` (2026-08-25).
    """
    if (
        all_fail
        and entropy_mean is not None
        and float(entropy_mean) < low_entropy_threshold
        and (route in RL_ROUTES or route == REPAIR_SFT)
    ):
        adaptive_temp.record_skip("low_reward_signal")


def _sigterm_payload_step(stop_step: int | None, last_completed: int) -> int:
    """The resume_state payload step on SIGTERM must match the checkpoint dir
    being written — the IN-FLIGHT step — so a relaunch resumes at step+1 and
    never replays a step whose weights already absorbed its update
    (2026-08-26 code-review F2)."""
    return int(stop_step) if stop_step is not None else int(last_completed)


def validate_resume_adapter_consistency(adapter_init: str | None, resume_step: int) -> str | None:
    """Return an error when the resume pairing would silently corrupt training.

    2026-08-24 bug-hunt: ``--adapter-init`` was never cross-validated against
    ``--resume-from``. Resuming with a ``step_NNNNNN_adapter`` checkpoint older
    than the resume metrics' latest step skips every recorded update between
    them (``if step <= resume_step: continue``) while continuing the run with
    stale weights and the newer router/curriculum state — a silent policy
    rewind. Non-step adapters (e.g. a warm distillation adapter) are
    intentionally allowed with resume records (a deliberate re-warm strategy);
    only a clearly-wrong checkpoint pairing is refused.
    """
    if not adapter_init or resume_step <= 0:
        return None
    match = re.search(r"step_(\d+)_adapter/?$", str(adapter_init))
    if match:
        init_step = int(match.group(1))
        if init_step < resume_step:
            return (
                f"--adapter-init {adapter_init} (step {init_step}) is older than "
                f"the --resume-from metrics' latest step {resume_step}; resuming "
                f"would skip {resume_step - init_step} recorded update(s) with "
                "stale weights"
            )
    return None


# ---------------------------------------------------------------------------
# Soft-resume state (2026-08-25, lane #20)
#
# Every field below is EXACT trainer state, not a reconstruction: the step
# counter, curriculum EMA + task-seen counts, router/mix state (posterior
# routes drive build_mixture_weights), the adaptive-temperature ladder, the
# trust-region violation count + scaled optimizer LR, and the repair-converted
# dedup ledger. Cold-start launches never touch these helpers — a launch
# without --resume-state is byte-identical to today.
# ---------------------------------------------------------------------------


def collect_repair_converted_dedup_keys(
    repair_converted_jsonl: str | Path | None,
) -> list[str]:
    """All dedup keys recorded in the repair-converted ledger.

    The repair stage dedupes against EVERY ledger record (converted or not)
    and the trainer's all_fail_without_repair breaker counts only the
    converted ones — so the state snapshot must carry the full key set.
    """
    return sorted(collect_repair_converted_status(repair_converted_jsonl))


def collect_repair_converted_status(
    repair_converted_jsonl: str | Path | None,
) -> dict[str, bool]:
    """Per-key converted status of the repair-converted ledger.

    ``{dedup_key: converted_flag}`` — the exact information the resume needs:
    the dedupe set (all keys) AND the breaker's conversion count (keys whose
    flag is True). A failed conversion attempt must never become a conversion
    on resume, and a real conversion must never be replayed or lost.
    """
    if not repair_converted_jsonl:
        return {}
    path = Path(repair_converted_jsonl)
    if not path.is_file():
        return {}
    status: dict[str, bool] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        key = str(record.get("dedup_key", "") or "")
        if not key:
            continue
        status[key] = bool(record.get("converted", False))
    return status


def reseed_repair_converted_ledger(
    repair_converted_jsonl: str | Path | None,
    dedup_keys: list[str],
    status: Mapping[str, bool] | None = None,
) -> int:
    """Re-seed a (possibly fresh) repair-converted ledger from a resumed run's
    dedup keys so dedupe never replays an entry and the breaker never loses
    the accumulated conversion count. Each restored record keeps the recorded
    ``converted`` flag (keys missing from ``status`` default to True — the
    count-conservative direction: a real conversion is never dropped, which
    would false-trip the all_fail_without_repair breaker). Restored records
    are marked ``resume_restored`` for the auditor. Idempotent: a second
    reseed appends nothing.
    """
    if not repair_converted_jsonl or not dedup_keys:
        return 0
    path = Path(repair_converted_jsonl)
    status_by_key = dict(status or {})
    existing = set(collect_repair_converted_dedup_keys(path))
    restored = 0
    for key in dedup_keys:
        if not key or key in existing:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "dedup_key": key,
                        "converted": bool(status_by_key.get(key, True)),
                        "resume_restored": True,
                        "restored_at_utc": datetime.now(timezone.utc).isoformat(),
                    },
                    sort_keys=True,
                )
                + "\n"
            )
        existing.add(key)
        restored += 1
    return restored


def build_resume_state_payload(
    *,
    step: int,
    curriculum_state: Mapping[str, Mapping[str, float]],
    adaptive_temp_state: Mapping[str, Any],
    router_state: Mapping[str, Mapping[str, Any]],
    recent_frontier: list[str],
    total_probes: int,
    trust_region_violation_count: int,
    optimizer_lr: float,
    repair_converted_dedup_keys: list[str],
    metrics_path: str,
    output_dir: str,
    resume_from: str | None = None,
    sigterm: bool = False,
    repair_converted_status: Mapping[str, bool] | None = None,
) -> dict[str, Any]:
    """Snapshot the trainer's exact state at a completed-step boundary.

    ``step`` is the LAST COMPLETED step (the record was already emitted), so a
    resumed run's next executed step is ``state.step + 1``. ``task_seen`` is a
    derived view of the curriculum's per-task counts; ``curriculum_state`` is
    the authoritative full EMA state. ``repair_converted_status`` carries each
    ledger key's converted flag so the resumed count matches the paused count
    exactly.
    """
    status_by_key = dict(repair_converted_status or {})
    payload: dict[str, Any] = {
        "version": RESUME_STATE_VERSION,
        "step": int(step),
        "curriculum_state": {
            str(task_id): {
                str(field): float(value)
                for field, value in entry.items()
                if isinstance(entry, Mapping)
            }
            for task_id, entry in curriculum_state.items()
        },
        "task_seen": {
            str(task_id): float(entry.get("seen", 0.0))
            for task_id, entry in curriculum_state.items()
            if isinstance(entry, Mapping)
        },
        "repair_converted_dedup_keys": sorted(
            str(key) for key in repair_converted_dedup_keys if key
        ),
        "repair_converted_status": {
            str(key): bool(flag) for key, flag in status_by_key.items() if str(key)
        },
        "adaptive_temp": dict(adaptive_temp_state),
        "router_state": {
            str(task_id): {
                str(field): float(value) if isinstance(value, (int, float)) else str(value)
                for field, value in entry.items()
            }
            for task_id, entry in router_state.items()
            if isinstance(entry, Mapping)
        },
        "recent_frontier": [str(task_id) for task_id in recent_frontier],
        "total_probes": int(total_probes),
        "trust_region": {
            "violation_count": int(trust_region_violation_count),
            "optimizer_lr": float(optimizer_lr),
        },
        "resume_from": resume_from,
        "metrics_path": str(metrics_path),
        "output_dir": str(output_dir),
        "sigterm_save": bool(sigterm),
        "saved_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    return payload


def save_resume_state(path: str | Path, payload: dict[str, Any]) -> None:
    """Atomic write of the soft-resume snapshot (same pattern as the adapter
    checkpoint: temp file + fsync + rename, so a KILL mid-save can never leave
    a half-written state file)."""
    write_json_atomic(Path(path), payload)


def load_resume_state(path: str | Path) -> dict[str, Any]:
    """Load and validate a resume_state.json. Raises ValueError with an
    actionable message on a missing/corrupt/unsupported snapshot instead of
    silently starting the curriculum over."""
    state_path = Path(path)
    if not state_path.is_file():
        raise ValueError(f"--resume-state file missing: {state_path}")
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"--resume-state {state_path} is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"--resume-state {state_path} must be a JSON object")
    if int(payload.get("version", 0)) != RESUME_STATE_VERSION:
        raise ValueError(
            f"--resume-state {state_path} has unsupported version "
            f"{payload.get('version')!r} (expected {RESUME_STATE_VERSION})"
        )
    step = payload.get("step")
    if not isinstance(step, int) or isinstance(step, bool) or step < 0:
        raise ValueError(
            f"--resume-state {state_path} must record a non-negative integer 'step' (got {step!r})"
        )
    return payload


def restore_curriculum_state(curriculum: TaskCurriculum, state: Mapping[str, Any]) -> None:
    """Restore the curriculum EMA + task-seen counts exactly as paused."""
    raw = state.get("curriculum_state") or {}
    restored: dict[str, dict[str, float]] = {}
    for task_id, entry in raw.items():
        if not isinstance(entry, Mapping):
            continue
        try:
            restored[str(task_id)] = {
                "ema_reward": float(entry.get("ema_reward", 0.0)),
                "seen": float(entry.get("seen", 0.0)),
            }
        except (TypeError, ValueError):
            continue
    curriculum.state = restored


def restore_adaptive_temp_skip_counter(
    adaptive_temp: AdaptiveTemperatureState, state: Mapping[str, Any]
) -> None:
    """Restore the stateful escalation counter only.

    base_temp/step_size/max_temp are LAUNCH CONFIG, not state: the resumed run
    keeps its own ladder (the behavior-temperature clamp at the use site still
    hard-caps everything at TEMP_ESCALATION_CEILING).
    """
    temp_state = state.get("adaptive_temp") or {}
    try:
        adaptive_temp.consecutive_low_signal_skips = max(
            0, int(temp_state.get("consecutive_low_signal_skips", 0))
        )
    except (TypeError, ValueError):
        adaptive_temp.consecutive_low_signal_skips = 0


def restore_router_state(router: FrontierRouter, state: Mapping[str, Any]) -> None:
    """Restore the router's posterior/probe state exactly as paused, so the
    FV-GSPO mixture (targeted/neighbor/replay pools) continues from the same
    routes instead of re-deriving them from a cold router."""
    raw = state.get("router_state") or {}
    restored: dict[str, dict[str, float | str]] = {}
    for task_id, entry in raw.items():
        if not isinstance(entry, Mapping):
            continue
        restored[str(task_id)] = {
            str(field): float(value) if isinstance(value, (int, float)) else str(value)
            for field, value in entry.items()
        }
    router.state = restored


def restore_trust_region_state(
    optimizer: Any, state: Mapping[str, Any], resume_fresh: bool = False
) -> int:
    """Restore the trust-region violation count and the scaled optimizer LR.

    The LR has been halved in place by scale_lr on every violation; restoring
    it continues the halving ladder instead of resetting to the base LR and
    replaying the violations. Returns the restored violation count (0 when the
    snapshot carries none).

    B-224: with resume_fresh=True the snapshot's ladder is NOT replayed — the
    optimizer keeps the caller's --lr and the count resets to 0. After a
    bleed alarm the halving was driven by the false-violation loop, so a
    relaunch must not inherit it.
    """
    if resume_fresh:
        return 0
    trust = state.get("trust_region") or {}
    try:
        count = max(0, int(trust.get("violation_count", 0)))
    except (TypeError, ValueError):
        count = 0
    lr = trust.get("optimizer_lr")
    if lr is not None:
        try:
            optimizer.param_groups[0]["lr"] = float(lr)
        except (TypeError, ValueError, IndexError, KeyError):
            pass
    return count


def maybe_stop_for_breaker(
    breaker: CircuitBreakerState,
    args: argparse.Namespace,
    rank: int,
    trips: list[dict[str, Any]],
) -> bool:
    """Log newly tripped breakers; return True when the run must halt.

    A severe in-loop breaker (non-finite, clip fraction, entropy collapse,
    all-fail without repair) that persists across two evaluation windows stops
    the run so NPU-hours are not burned on a broken policy.
    """
    if trips and rank == 0:
        print(
            json.dumps({"stage": "circuit_breaker_trip", "trips": trips}, ensure_ascii=False),
            flush=True,
        )
    if breaker.should_stop and args.stop_on_severe_breaker:
        if rank == 0:
            print(
                json.dumps(
                    {"stage": "circuit_breaker_stop", "trips": breaker.tripped},
                    ensure_ascii=False,
                ),
                flush=True,
            )
        return True
    return False


# ---------------------------------------------------------------------------
# Training-log instrumentation (2026-08-25 user requirement)
#
# The training log must document, for EVERY training step:
#   1. every training loss value — the per-candidate loss_i with n_i token
#      counts, the weighted aggregate total_loss = Σ w_i·loss_i, and the value
#      actually used for the backward (record fields ``per_candidate_losses``,
#      ``loss_breakdown``, ``loss``);
#   2. the loss reduction — an explicit machine- + human-readable field
#      documenting HOW the loss is reduced/aggregated for the configured path
#      (record field ``loss_reduction``, emitted on every step record; if the
#      step runs a different path — gspo/grpo fallback — the field reflects
#      that path), plus a compact grep-able ``loss_breakdown=...`` line in the
#      train log printed every step;
#   3. the reward scores of ALL rollout samples — per candidate: raw reward,
#      shaped reward, pass/fail, and the advantage used, aligned 1:1 with
#      candidate order (record field ``rollout_rewards``), including repair-lane
#      candidates.
#
# Zero-change gate (manager directive 2026-08-25): a 0-change adapter vs base
# after a training step is unacceptable. lora_B parameters are snapshotted
# before training starts; after every optimizer step max|Δlora_B| is measured
# against the snapshot. An EXACT zero (not a tolerance) fires
# ``zero_change_alarm`` plus a recommend-stop marker; the per-step
# ``lora_b_max_delta`` is logged in the step record.
# ---------------------------------------------------------------------------

# 2026-08-26 (r10, entropy floor): every reduction string documents the
# entropy-floor term honestly — when --entropy-floor-weight > 0 the final
# `loss` value is loss_recomputed + entropy_floor_penalty (+ DR terms), and
# loss_breakdown.entropy_floor_penalty carries the value (0 above the floor).
# 2026-08-26 (run-8 OOM fix): the penalty's entropy is the mean over the
# first --entropy-token-cap completion tokens (a rough mean — the full-
# sequence differentiable entropy branch retained ~37 GiB of per-chunk fp32
# tensors in the autograd graph and caused the 59.8 GiB NPU-0 peak).
# 2026-08-26 (run-10 double-backward fix): the penalty is a MONITORING
# signal — its mean is detached, so it contributes no gradient (the r10
# penalty-first backward double-consumed every candidate's graph with the
# per-candidate backwards); the value still rides the identity above.
_ENTROPY_FLOOR_REDUCTION_NOTE = (
    " Entropy-floor term (2026-08-26 r10, see loss_breakdown.entropy_floor_penalty): "
    "when --entropy-floor-weight > 0, the final loss value adds "
    "weight*max(0, floor - mean current-policy train-pass entropy) — engaged "
    "only below the floor, honored by the math-audit final-loss identity "
    "(loss == loss_recomputed + entropy_floor_penalty + DR terms). The mean "
    "is DETACHED (run-10 double-backward fix): the term is a monitoring "
    "value riding the loss identity and contributes no gradient — the "
    "degenerate-policy alarm is the collapse rescue."
)

LOSS_REDUCTION_STRINGS: dict[str, str] = {
    "sapo": (
        "per-candidate token-mean SAPO losses (loss_i = -mean_t[g(r_t)*A_i] + "
        "kl_coeff*mean_t[k3], r_t = exp(cur-old), g = (4/tau)*sigmoid(tau*(r-1))), "
        "aggregated with equal per-candidate weights w_i = 1/G over the loss "
        "candidates (length-neutral; deliberately NOT n_i/N token weighting), "
        "gradients accumulated via per-candidate (loss_i*w_i).backward() with a "
        "single optimizer.zero_grad() (no batched backward for sapo)"
        + _ENTROPY_FLOOR_REDUCTION_NOTE
    ),
    "gspo": (
        "batched sequence-level clipped GSPO surrogate: loss = "
        "-mean_i[min(s_i*A_i, clip(s_i)*A_i)] + kl_coeff*mean_i[KL_i] with "
        "sequence ratios, gradients via a single batched total_loss.backward()"
        + _ENTROPY_FLOOR_REDUCTION_NOTE
    ),
    "gspo_ln": (
        "batched length-neutral GSPO (gspo_ln): batched sequence-level clipped "
        "surrogate weighted by w_i = min(|y_i|/L_ref, w_max), gradients via a "
        "single batched total_loss.backward()" + _ENTROPY_FLOOR_REDUCTION_NOTE
    ),
    "grpo": (
        "batched unclipped GRPO: loss = -mean_i[r_i*A_i] + kl_coeff*KL with "
        "sequence ratios, gradients via a single batched total_loss.backward()"
        + _ENTROPY_FLOOR_REDUCTION_NOTE
    ),
}


def evidence_free_candidate_entry() -> dict[str, Any]:
    """A synthesized zero-value evaluation entry for a quarantine-suppressed step.

    2026-09-01 (data-efficiency): when the collapse gate
    (``quarantine_gate_active``) engages, the step loop SKIPS the expensive
    reward pass (harness subprocess + self-eval/judge forwards per candidate)
    because an evidence-free collapsed rollout (run-6 class: completions
    [1,1,1,1], entropy 0.0137) can only produce flat all-fail evaluations.
    The entry mirrors the keys ``evaluate_candidate`` produces so every
    downstream consumer (reward tensors, probe, curriculum, advantages,
    ``build_rollout_rewards``, emit) works unchanged: zero rewards,
    passed=False, no judge dims, ``evidence_free=True`` for the auditor.
    """
    return {
        "passed": False,
        "pass_reward": 0.0,
        "shaped_reward": 0.0,
        "syntax_reward": 0.0,
        "interface_reward": 0.0,
        "verifier_reward": 0.0,
        "brevity_reward": 0.0,
        "import_hygiene_reward": 0.0,
        "self_eval_reward": 0.0,
        "self_eval_raw_score": 0.0,
        "model_dim_scores": {},
        "judge_reward": None,
        "total_reward": 0.0,
        "details": [],
        "evidence_free": True,
    }


def per_candidate_stop_reasons(diagnostics: Mapping[str, Any]) -> list[str]:
    """One stop-reason label per rollout candidate, aligned 1:1 with order.

    2026-08-26 (r18, QA lane #6): the trainer already computed the three-way
    stop breakdown (eos/fence/truncated + the cap-run-with-fence-opener
    regression class) as group rates; this derives the PER-CANDIDATE label so
    the step record and compact log line can name how each completion ended.
    Precedence mirrors ``build_generation_diagnostics``:
    eos > fence > cap_run_fence_opener > truncated > empty (zero tokens) >
    unknown. Zero-token/empty completions are their own class.
    """
    lengths = list(diagnostics.get("completion_token_lengths") or [])
    eos = list(diagnostics.get("eos_terminated") or [])
    fence = list(diagnostics.get("fence_terminated") or [])
    truncated = list(diagnostics.get("truncated") or [])
    cap_run = list(diagnostics.get("cap_run_with_fence_opener") or [])
    reasons: list[str] = []
    for index in range(len(lengths)):
        if index < len(eos) and eos[index]:
            reasons.append("eos")
        elif index < len(fence) and fence[index]:
            reasons.append("fence")
        elif index < len(cap_run) and cap_run[index]:
            reasons.append("cap_run_fence_opener")
        elif index < len(truncated) and truncated[index]:
            reasons.append("truncated")
        elif lengths[index] == 0:
            reasons.append("empty")
        else:
            reasons.append("unknown")
    return reasons


def build_rollout_rewards(
    evaluations: list[dict[str, Any]],
    advantages: torch.Tensor,
    completion_token_lengths: list[int] | None = None,
    *,
    adv_scale: float | None = None,
    stop_reasons: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Per-candidate rollout reward records, aligned 1:1 with candidate order.

    Every rollout sample gets one entry carrying the raw reward
    (``total_reward``), the shaped reward (``shaped_reward`` from
    ``shaped_reward_from_details``), the executable pass/fail (``pass``), the
    advantage actually used (``advantage``), the completion token count
    (``n_tokens``), and any teacher-free repair-lane annotations
    (``self_repair_passed``, ``self_repair_candidate_total_reward``) when the
    trainer generated repair candidates. Zero-token/empty responses are
    included (n_tokens=0, reward 0.0/None-stub graded) — the record emit never
    crashes on them.

    2026-08-26 (r18, QA lane #6, user directive "the training log must carry
    ALL information"): the record is extended with every term value:
      - every reward component: syntax/interface/verifier/brevity/
        import_hygiene, plus ``judge_dim_scores`` (the per-dimension model
        judge scores the blend consumed) and ``judge_reward`` (its composite);
      - every advantage term: ``total_reward`` (raw), ``mean_other``
        (the LOO other-mean (Σr − rᵢ)/(G−1), 0 for G=1), ``loo_raw``
        (rᵢ − mean_other, pre-scale), ``adv_scale`` (the shared-MAD scale
        applied, None when unscaled) and ``advantage`` (the final
        scaled+clamped LOO actually used);
      - ``stop_reason`` (eos/fence/cap_run_fence_opener/truncated/empty/
        unknown) + ``n_tokens`` per candidate.
    Field-name stability is part of the contract — the reward-path verifier
    and the math auditor recompute from these exact keys.
    """
    group_total = sum(
        float(entry.get("total_reward", entry.get("reward", 0.0)) or 0.0) for entry in evaluations
    )
    group_size = max(1, len(evaluations))
    records: list[dict[str, Any]] = []
    for index, entry in enumerate(evaluations):
        advantage: float | None = None
        if advantages is not None and index < int(advantages.numel()):
            advantage = float(advantages[index].detach().item())
        passed = bool(entry.get("passed"))
        if not passed:
            passed = float(entry.get("pass_reward", 0.0) or 0.0) > 0.0
        token_count: int | None = None
        if completion_token_lengths is not None and index < len(completion_token_lengths):
            token_count = int(completion_token_lengths[index])
        raw_reward = float(entry.get("total_reward", entry.get("reward", 0.0)) or 0.0)
        mean_other = (group_total - raw_reward) / float(group_size - 1) if group_size > 1 else 0.0
        # G=1: leave_one_out_advantages returns zeros for numel<=1 — the
        # ACTUAL pre-scale LOO is 0, so loo_raw mirrors production (review
        # finding: raw r_i would break the auditor's
        # advantage == clamp(loo_raw/adv_scale) identity for G=1).
        loo_raw = raw_reward - mean_other if group_size > 1 else 0.0
        judge_scores = entry.get("model_dim_scores")
        record: dict[str, Any] = {
            "index": index,
            "total_reward": raw_reward,
            "shaped_reward": float(entry.get("shaped_reward", 0.0) or 0.0),
            "pass": passed,
            "pass_reward": float(entry.get("pass_reward", 0.0) or 0.0),
            "advantage": advantage,
            "n_tokens": token_count,
            "syntax_reward": float(entry.get("syntax_reward", 0.0) or 0.0),
            "interface_reward": float(entry.get("interface_reward", 0.0) or 0.0),
            "verifier_reward": float(entry.get("verifier_reward", 0.0) or 0.0),
            "brevity_reward": float(entry.get("brevity_reward", 0.0) or 0.0),
            "import_hygiene_reward": float(entry.get("import_hygiene_reward", 0.0) or 0.0),
            # 2026-08-26 (r16 judge wave): the exact judge composite the
            # blend used (None when the judge is off or scored nothing) —
            # the reward verifier recomputes the 3-way blend from it.
            "judge_reward": entry.get("judge_reward"),
            # 2026-08-26 (r18): the per-dimension judge scores the composite
            # was computed from (None when not judged) — every judge dim is
            # visible per candidate, not only the composite. DIM VALUES ARE
            # NONE-GUARDED: _parse_model_dim_scores records None for a dim the
            # judge response did not yield (partial parses are a live path —
            # the step-level aggregation filters them), so a raw
            # float(value) here would crash the whole step (review finding,
            # requesting-code-review 2026-08-26). None dims are preserved so
            # the record shows exactly what the judge produced; the compact
            # line renders them NA.
            "judge_dim_scores": (
                {
                    str(dim): (float(value) if isinstance(value, (int, float)) else None)
                    for dim, value in judge_scores.items()
                }
                if isinstance(judge_scores, dict) and judge_scores
                else None
            ),
            # 2026-08-26 (r18): every advantage term per candidate.
            "mean_other": float(mean_other),
            "loo_raw": float(loo_raw),
            "adv_scale": float(adv_scale) if adv_scale is not None else None,
            # 2026-08-26 (r18): how this candidate's completion ended.
            "stop_reason": (
                str(stop_reasons[index])
                if stop_reasons is not None and index < len(stop_reasons)
                else None
            ),
        }
        # Teacher-free self-repair diagnostics (repair-lane candidates) are
        # annotated on the original rollout entries; surface them per candidate.
        if entry.get("self_repair_passed") is not None:
            record["self_repair_passed"] = bool(entry.get("self_repair_passed"))
        if entry.get("self_repair_candidate_total_reward") is not None:
            record["self_repair_candidate_total_reward"] = float(
                entry.get("self_repair_candidate_total_reward")
            )
        records.append(record)
    return records


_SAPO_TERM_KEYS = (
    # NOTE: n_tokens is deliberately NOT merged — per_candidate_losses
    # n_tokens is the TRAIN-PASS token count (can differ from the completion
    # length under train-pass sequence capping), while rollout_rewards
    # n_tokens is the completion-token count. Merging would silently change
    # the documented meaning of the existing field.
    "weight",
    "loss",
    "sapo_gate_mean",
    "seq_kl",
    "ratio_mean",
    "clip_total_fraction",
    "excluded_reason",
)


def enrich_rollout_rewards_with_sapo_terms(
    rollout_rewards: list[dict[str, Any]] | None,
    per_candidate_losses: list[dict[str, Any]] | None,
) -> None:
    """Merge the per-candidate loss/SAPO terms into the aligned rollout
    records, in place (2026-08-26, r18).

    The rollout records are built right after scoring, but the SAPO terms
    (ratio_mean, sapo_gate_mean, seq_kl, clip_total_fraction) only exist after
    the inner optimizer loop — so at emit time the per-candidate losses are
    merged back into the rollout record by ``index``. One canonical
    per-candidate record then carries EVERY term value (reward components,
    advantage terms, SAPO terms, stop reason, tokens), and the math auditor
    can cross-check the identity from either array. Zero-token excluded
    candidates keep their ``excluded_reason`` marker and no SAPO terms.
    """
    if not rollout_rewards or not per_candidate_losses:
        return
    by_index = {int(entry.get("index", -1)): entry for entry in per_candidate_losses}
    for record in rollout_rewards:
        candidate = by_index.get(int(record.get("index", -1)))
        if candidate is None:
            continue
        for key in _SAPO_TERM_KEYS:
            if candidate.get(key) is not None:
                record[key] = candidate[key]


EVAL_RESULTS_FILENAME = "eval_results.jsonl"

# 2026-09-01 (bug-hunter mechanism 6): the row schema carries an explicit
# version. A field added/removed WITHOUT a deliberate bump of
# EVAL_RESULTS_SCHEMA_VERSION fails the schema pin in
# tests/test_grpo_trainer_eval_results.py (the judge-dims omission class:
# "brevity" was added on 2026-08-27 with no signal to downstream
# exact-mode consumers, which silently recomposed without it).
EVAL_RESULTS_SCHEMA_VERSION = 1
EVAL_RESULTS_ROW_FIELDS = frozenset(
    {
        "schema_version",
        "step",
        "index",
        "passed",
        "details",
        "detail_budget",
        "code_hash",
        "syntax",
        "interface",
        "verifier",
        "brevity",
        "import_hygiene",
    }
)


def build_eval_result_row(
    *,
    step: int,
    index: int,
    code: str,
    entry: Mapping[str, Any],
    detail_budget: int | None = None,
) -> dict[str, Any]:
    """One append-only eval_results.jsonl row (2026-08-25, verifier G1).

    Persists the per-candidate harness outcome + the reward components the
    trainer actually used, so the reward-path verifier can validate a LIVE
    row end-to-end (its --harness-results exact mode recomputes shaped/verifier
    from ``passed``/``details``/``detail_budget``) and candidates can be
    re-scored offline instead of being dropped after the temp-dir eval.
    Fields: {schema_version, step, index, passed, details, detail_budget,
    code_hash, syntax, interface, verifier, brevity, import_hygiene}.
    ``code`` is the extracted candidate that was scored; ``code_hash`` is its
    sha256. ``schema_version`` (2026-09-01) is pinned first: streaming
    readers can gate on it and any field add/remove without a version bump
    fails the schema test.
    """
    return {
        "schema_version": EVAL_RESULTS_SCHEMA_VERSION,
        "step": int(step),
        "index": int(index),
        "passed": bool(entry.get("passed", False)),
        "details": [str(d) for d in (entry.get("details") or [])],
        "detail_budget": int(detail_budget)
        if detail_budget is not None
        else None,  # F4: 0 preserved, not None
        "code_hash": hashlib.sha256(code.encode("utf-8")).hexdigest(),
        "syntax": float(entry.get("syntax_reward", 0.0) or 0.0),
        "interface": float(entry.get("interface_reward", 0.0) or 0.0),
        "verifier": float(entry.get("verifier_reward", 0.0) or 0.0),
        # 2026-08-27 (research audit P5): brevity is an executable component
        # with weight 0.05 — the row must persist it or the exact-mode
        # composition recompute silently drops the counterweight.
        "brevity": float(entry.get("brevity_reward", 0.0) or 0.0),
        "import_hygiene": float(entry.get("import_hygiene_reward", 0.0) or 0.0),
    }


def recompute_aggregate_sapo_loss(per_candidate_losses: list[dict[str, Any]]) -> float:
    """Recompute the documented SAPO aggregate loss from a step record.

    The documented reduction is the weighted sum of the per-candidate means:
    ``total_loss = Σ_i w_i * loss_i`` with w_i = 1/G (equal per-candidate
    weights — NOT n_i/N token weighting, which would be length-biased BNPO).
    Entries without a loss (zero-token candidates) contribute nothing. The
    math auditor uses this identity to verify ``loss_breakdown.loss_recomputed
    == loss`` (up to the DR pair/variance terms, which are reported in
    ``loss_breakdown``).
    """
    total = 0.0
    for entry in per_candidate_losses:
        loss_value = entry.get("loss")
        weight = entry.get("weight")
        if loss_value is None or weight is None:
            continue
        total += float(weight) * float(loss_value)
    return total


def _compact_float_array(
    entries: list[dict[str, Any]], key: str, digits: str = ".4g", display: str | None = None
) -> str:
    """Render one per-candidate numeric field as ``display:[v,v,...]`` (default
    display = key) with NA placeholders — the compact-line contract for
    per-candidate terms."""
    return (
        f"{display or key}:["
        + ",".join(
            "NA" if entry.get(key) is None else format(float(entry[key]), digits)
            for entry in entries
        )
        + "]"
    )


def format_compact_loss_breakdown(record: Mapping[str, Any]) -> str:
    """One compact, grep-able train-log line per step.

    Starts with ``loss_breakdown=`` and reports step, skip status, loss, the
    recomputed aggregate, per-candidate losses with token counts, rollout
    rewards/advantages and the zero-change alarm. 2026-08-26 (r18, user
    directive "the training log must carry ALL information"): the line
    additionally reports EVERY term value per candidate — each reward
    component (pass/shaped/syntax/interface/verifier/hygiene/judge composite
    + dims), the advantage terms (mean_other, scale, loo_raw), the SAPO terms
    (ratio/gate/kl/clip), stop reasons and token counts — plus the step-level
    entropy and trust-region terms. Missing fields are omitted or rendered NA
    so legacy/resume records stay printable.
    """
    parts = [
        f"loss_breakdown=step:{int(record['step'])}",
        f"skipped:{int(bool(record.get('skipped')))}",
    ]
    route = record.get("route")
    if route is not None:
        parts.append(f"route:{route}")
    loss = record.get("loss")
    parts.append(f"loss:{'NA' if loss is None else format(float(loss), '.6g')}")
    breakdown = record.get("loss_breakdown")
    if isinstance(breakdown, dict):
        recomputed = breakdown.get("loss_recomputed")
        parts.append(
            f"recomputed:{'NA' if recomputed is None else format(float(recomputed), '.6g')}"
        )
    per_candidate = record.get("per_candidate_losses")
    if isinstance(per_candidate, list) and per_candidate:
        parts.append(
            "per_candidate:["
            + ",".join(
                "NA" if entry.get("loss") is None else format(float(entry["loss"]), ".4g")
                for entry in per_candidate
            )
            + "]"
        )
        parts.append(
            "n_tokens:["
            + ",".join(str(int(entry.get("n_tokens") or 0)) for entry in per_candidate)
            + "]"
        )
    rollout = record.get("rollout_rewards")
    if isinstance(rollout, list) and rollout:
        parts.append(
            "rewards:["
            + ",".join(
                format(float(entry.get("total_reward", 0.0) or 0.0), ".4g") for entry in rollout
            )
            + "]"
        )
        parts.append(
            "advantages:["
            + ",".join(
                "NA" if entry.get("advantage") is None else format(float(entry["advantage"]), ".4g")
                for entry in rollout
            )
            + "]"
        )
        # ── 2026-08-26 (r18): every reward component per candidate ──
        parts.append(
            "pass:[" + ",".join("1" if bool(entry.get("pass")) else "0" for entry in rollout) + "]"
        )
        parts.append(_compact_float_array(rollout, "shaped_reward", display="shaped"))
        parts.append(_compact_float_array(rollout, "syntax_reward", display="syntax"))
        parts.append(_compact_float_array(rollout, "interface_reward", display="interface"))
        parts.append(_compact_float_array(rollout, "verifier_reward", display="verifier"))
        parts.append(_compact_float_array(rollout, "import_hygiene_reward", display="hygiene"))
        parts.append(_compact_float_array(rollout, "judge_reward", display="judge"))
        # judge dimension scores: one per-dimension array across candidates.
        dims: list[str] = []
        for entry in rollout:
            scores = entry.get("judge_dim_scores")
            if isinstance(scores, dict):
                for dim in scores:
                    if dim not in dims:
                        dims.append(str(dim))
        if dims:
            dim_parts = []
            for dim in dims:
                dim_parts.append(
                    f"{dim}:["
                    + ",".join(
                        "NA"
                        if not isinstance(entry.get("judge_dim_scores"), dict)
                        or entry["judge_dim_scores"].get(dim) is None
                        else format(float(entry["judge_dim_scores"][dim]), ".4g")
                        for entry in rollout
                    )
                    + "]"
                )
            parts.append("judge_dims:{" + " ".join(dim_parts) + "}")
        # ── 2026-08-26 (r18): every advantage term per candidate ──
        parts.append(_compact_float_array(rollout, "mean_other"))
        scale = rollout[0].get("adv_scale") if rollout else None
        parts.append("scale:" + ("NA" if scale is None else format(float(scale), ".4g")))
        parts.append(_compact_float_array(rollout, "loo_raw"))
        # ── 2026-08-26 (r18): SAPO terms merged per candidate ──
        sapo_terms = [
            (key, short)
            for key, short in (
                ("ratio_mean", "ratio"),
                ("sapo_gate_mean", "gate"),
                ("seq_kl", "kl"),
                ("clip_total_fraction", "clip"),
            )
            if any(entry.get(key) is not None for entry in rollout)
        ]
        if sapo_terms:
            sapo_parts = [
                f"{short}:["
                + ",".join(
                    "NA" if entry.get(key) is None else format(float(entry[key]), ".4g")
                    for entry in rollout
                )
                + "]"
                for key, short in sapo_terms
            ]
            parts.append("sapo:{" + " ".join(sapo_parts) + "}")
        # ── 2026-08-26 (r18): stop reasons + token counts per candidate ──
        if any(entry.get("stop_reason") is not None for entry in rollout):
            parts.append(
                "stops:["
                + ",".join(
                    "NA" if entry.get("stop_reason") is None else str(entry["stop_reason"])
                    for entry in rollout
                )
                + "]"
            )
        parts.append(
            "tokens:["
            + ",".join(
                "NA" if entry.get("n_tokens") is None else str(int(entry["n_tokens"]))
                for entry in rollout
            )
            + "]"
        )
    # ── 2026-08-26 (r18): entropy-floor terms (train mean, floor, penalty
    # value, weight) from the loss breakdown. ──
    if isinstance(breakdown, dict) and breakdown.get("entropy_floor") is not None:
        parts.append(
            "entropy:{"
            + f"train:{'NA' if breakdown.get('entropy_train_mean') is None else format(float(breakdown['entropy_train_mean']), '.4g')} "
            + f"floor:{format(float(breakdown['entropy_floor']), '.4g')} "
            + f"pen:{'NA' if breakdown.get('entropy_floor_penalty') is None else format(float(breakdown['entropy_floor_penalty']), '.4g')} "
            + f"w:{'NA' if breakdown.get('entropy_floor_weight') is None else format(float(breakdown['entropy_floor_weight']), '.4g')}"
            + "}"
        )
    # ── 2026-08-26 (r18): trust-region terms (post-update KL, ratio, clip
    # fraction + the LR scale state: violations + current LR). ──
    if (
        record.get("seq_kl_after") is not None
        or record.get("trust_region_violation_count") is not None
    ):
        parts.append(
            "tr:{"
            + f"violations:{int(record.get('trust_region_violation_count') or 0)} "
            + f"seq_kl_after:{'NA' if record.get('seq_kl_after') is None else format(float(record['seq_kl_after']), '.4g')} "
            + f"ratio_after:{'NA' if record.get('ratio_after_update') is None else format(float(record['ratio_after_update']), '.4g')} "
            + f"clip_after:{'NA' if record.get('clip_fraction_after_update') is None else format(float(record['clip_fraction_after_update']), '.4g')} "
            + f"lr:{'NA' if record.get('lr') is None else format(float(record['lr']), '.6g')}"
            + "}"
        )
    alarm = record.get("zero_change_alarm")
    if alarm is not None:
        parts.append(f"zero_change_alarm:{str(bool(alarm)).lower()}")
    return " ".join(parts)


def collect_lora_b_init_snapshot(
    names: list[str], params: list[torch.Tensor]
) -> dict[str, torch.Tensor]:
    """Clone the initial lora_B parameter values before training starts.

    The zero-change gate (2026-08-25 manager directive) compares every
    post-step state against this snapshot with an EXACT zero check: a 0-change
    adapter (lora_B byte-identical to base/init after an optimizer step) is
    the unacceptable silent-fallback class the eval lane already caught.
    """
    snapshot: dict[str, torch.Tensor] = {}
    # Strict pairing (training.compat, the py3.9-safe single home): a length
    # mismatch is a caller bug and must raise (ValueError) rather than
    # silently pair.
    for name, param in _strict_zip(names, params):
        if re.search(r"lora_[bB]\b", name):
            snapshot[name] = param.detach().clone()
    return snapshot


def measure_lora_b_max_delta(
    init_snapshot: Mapping[str, torch.Tensor],
    params_by_name: Mapping[str, torch.Tensor],
) -> float | None:
    """max|Δ lora_B| vs the init snapshot; None when no lora_B param is tracked.

    The subtraction runs in the parameter's own dtype, so two byte-identical
    values yield EXACTLY 0.0 and any real movement yields > 0.0 — the gate is
    an exact-zero test, never a tolerance.
    """
    if not init_snapshot:
        return None
    best = 0.0
    for name, init_value in init_snapshot.items():
        current = params_by_name[name]
        delta = float((current.detach() - init_value).abs().max().item())
        best = max(best, delta)
    return best


def zero_change_gate_fired(lora_b_max_delta: float | None) -> bool:
    """Exact-zero gate: an optimizer step that left every tracked lora_B
    parameter byte-identical to its init snapshot fires the alarm. None (no
    lora_B tracked) is a silent no-op, never an alarm."""
    return lora_b_max_delta is not None and lora_b_max_delta == 0.0


def emit_step_record(
    *,
    rank: int,
    metrics: list[dict[str, Any]],
    step_metrics_path: Path,
    log_steps: int,
    ctx: dict[str, Any],
    skipped: bool,
    reason: str | None = None,
    loss: float | None = None,
    trips: list[dict[str, Any]] | None = None,
    **extra: Any,
) -> dict[str, Any] | None:
    """Persist one step record (skipped or updated) on rank 0.

    ``ctx`` carries the step-scoped record fields (built once per step in
    ``main``) including the instrumentation fields ``rollout_rewards`` and
    ``loss_reduction``; ``extra`` fields are merged into the record (e.g. GSPO
    loss statistics, ``per_candidate_losses``/``loss_breakdown`` and the
    zero-change gate fields on updated steps). Every step also prints one
    compact grep-able ``loss_breakdown=...`` line to the train log.
    """
    if rank != 0:
        return None
    record = build_grpo_step_record(
        step=int(ctx["step"]),
        task_name=str(ctx["task_name"]),
        domain=str(ctx["domain"]),
        mean_reward=float(ctx["mean_reward"]),
        signal_stats=ctx["signal_stats"],
        mean_shaped_reward=ctx.get("mean_shaped_reward"),
        pass_rate=ctx.get("pass_rate"),
        syntax_rate=ctx.get("syntax_rate"),
        interface_rate=ctx.get("interface_rate"),
        verifier_rate=ctx.get("verifier_rate"),
        task_prob=float(ctx["task_prob"]),
        task_state=ctx["task_state"],
        advantage_scale=ctx.get("advantage_scale"),
        loo_advantage_rms=ctx.get("loo_advantage_rms"),
        loo_advantage_mean_abs=ctx.get("loo_advantage_mean_abs"),
        update_signal_magnitude=ctx.get("update_signal_magnitude"),
        update_signal_kind=ctx.get("update_signal_kind"),
        update_signal_threshold=ctx.get("update_signal_threshold"),
        skipped=skipped,
        reason=reason,
        loss=loss,
        adapter_init=ctx.get("adapter_init"),
        route=ctx.get("route"),
        entropy_mean=ctx.get("entropy_mean"),
        generation_tokens=ctx.get("generation_tokens"),
        repair_queued=ctx.get("repair_queued"),
        sidecar_alive=ctx.get("sidecar_alive"),
        all_fail=ctx.get("all_fail"),
        frontier_fraction=ctx.get("frontier_fraction"),
        breaker_trips=trips,
        model_dim_scores=ctx.get("model_dim_scores"),
        model_judge_enabled=ctx.get("model_judge_enabled"),
        posterior_lower=ctx.get("posterior_lower"),
        posterior_upper=ctx.get("posterior_upper"),
        flaky=ctx.get("flaky"),
        group_size=ctx.get("group_size"),
        greedy_count=ctx.get("greedy_count"),
        mean_response_length=ctx.get("mean_response_length"),
        truncation_rate=ctx.get("truncation_rate"),
        eos_termination_rate=ctx.get("eos_termination_rate"),
        degenerate_policy_alarm=ctx.get("degenerate_policy_alarm"),
        quarantine_suppressed=ctx.get("quarantine_suppressed"),
        fence_termination_rate=ctx.get("fence_termination_rate"),
        cap_run_with_fence_opener_rate=ctx.get("cap_run_with_fence_opener_rate"),
        completion_token_lengths=ctx.get("completion_token_lengths"),
        raw_response_chars=ctx.get("raw_response_chars"),
        extracted_code_chars=ctx.get("extracted_code_chars"),
        generation_token_budget=ctx.get("generation_token_budget"),
        rollout_rewards=ctx.get("rollout_rewards"),
        loss_reduction=ctx.get("loss_reduction"),
        **extra,
    )
    if skipped and record.get("loss_reduction") is not None:
        # Skipped steps computed no loss; the reduction field still documents
        # the configured path, with an explicit no-loss marker.
        record["loss_reduction"] = (
            f"{record['loss_reduction']} [skipped: no loss computed this step]"
        )
    # 2026-08-26 (r18, QA lane #6): merge the per-candidate SAPO terms
    # (computed in the inner optimizer loop) back into the aligned rollout
    # records so one canonical per-candidate record carries EVERY term value.
    # Runs after the record build and before persistence/print so both the
    # jsonl row and the compact log line see the enriched records.
    enrich_rollout_rewards_with_sapo_terms(
        record.get("rollout_rewards"), record.get("per_candidate_losses")
    )
    append_grpo_metric(metrics, record=record)
    append_grpo_metric_jsonl(step_metrics_path, record)
    # One compact grep-able line per step (the full json record still prints
    # at the log_steps cadence below).
    print(format_compact_loss_breakdown(record), flush=True)
    if int(ctx["step"]) % max(1, log_steps) == 0:
        print(json.dumps(record))
    return record


def build_launch_config(args: argparse.Namespace) -> dict[str, Any]:
    """Capture the immutable launch contract before model loading starts."""

    keys = (
        "model_name",
        "adapter_init",
        "resume_from",
        "resume_state",
        "output_dir",
        "tasks_dir",
        "benchmark_file",
        "domain_filter",
        "group_size",
        "max_adaptive_group",
        "grpo_steps",
        "inner_epochs",
        "lr",
        "kl_coeff",
        "temperature",
        "adaptive_temp_step",
        "adaptive_temp_max",
        "top_p",
        "max_new_tokens",
        "max_adaptive_new_tokens",
        "max_seq_length",
        "train_pass_max_seq_length",
        "loss_mode",
        "sapo_tau_pos",
        "sapo_tau_neg",
        "lora_rank",
        "lora_alpha",
        "target_modules",
        "freeze_param_regex",
        "checkpoint_interval_seconds",
        "npu_device_map",
        "npu_max_memory_gib",
        "device",
    )
    payload = {key: getattr(args, key, None) for key in keys}
    payload["device"] = str(payload["device"])
    payload.update(
        {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "argv": list(sys.argv),
            "visible_npus_env": os.environ.get("ASCEND_RT_VISIBLE_DEVICES")
            or os.environ.get("ASCEND_VISIBLE_DEVICES"),
        }
    )
    return payload


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    """Write ``payload`` to ``path`` atomically (temp file + rename).

    A failed write (serialization error, ENOSPC, fsync failure) must not
    leave the ``.{name}.tmp`` staging file behind — disk hygiene: the
    resume-state writer runs on every checkpoint, so leaked stages would
    accumulate unbounded across a long run.
    """
    tmp = path.with_name(f".{path.name}.tmp")
    try:
        with tmp.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False, default=str)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        tmp.replace(path)
    finally:
        # No-op after a successful replace (the stage no longer exists);
        # removes the partial stage on any failure.
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def peft_checkpoint_complete(path: Path) -> bool:
    return (path / "adapter_config.json").is_file() and any(
        (path / name).is_file() for name in ("adapter_model.safetensors", "adapter_model.bin")
    )


def save_peft_checkpoint_atomic(model: Any, text_preprocessor: Any, checkpoint_dir: Path) -> Path:
    """Write an immutable PEFT checkpoint without exposing a partial directory."""

    checkpoint_dir = Path(checkpoint_dir)
    checkpoint_dir.parent.mkdir(parents=True, exist_ok=True)
    if peft_checkpoint_complete(checkpoint_dir):
        return checkpoint_dir

    temp_dir = checkpoint_dir.with_name(
        f".{checkpoint_dir.name}.tmp-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    )
    recovery_dir: Path | None = None
    try:
        model.save_pretrained(temp_dir)
        text_preprocessor.save_backend.save_pretrained(temp_dir)
        if not peft_checkpoint_complete(temp_dir):
            raise RuntimeError(f"incomplete PEFT checkpoint staged at {temp_dir}")

        if checkpoint_dir.exists():
            recovery_dir = checkpoint_dir.with_name(
                f".{checkpoint_dir.name}.incomplete-{int(time.time())}-{uuid.uuid4().hex[:8]}"
            )
            checkpoint_dir.rename(recovery_dir)
        try:
            temp_dir.rename(checkpoint_dir)
        except Exception:
            if recovery_dir is not None and recovery_dir.exists() and not checkpoint_dir.exists():
                recovery_dir.rename(checkpoint_dir)
            raise
        return checkpoint_dir
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


def _atomic_save_adapter_dir(save_model: Any, text_preprocessor: Any, adapter_dir: Path) -> Path:
    """Save the live adapter dir ATOMICALLY (temp dir + rename with recovery)
    so a KILL mid-save can never leave a truncated adapter/ dir — the next
    launch's default --adapter-init target (2026-08-26 code-review F3)."""
    adapter_dir = Path(adapter_dir)
    temp_dir = adapter_dir.with_name(
        f".{adapter_dir.name}.tmp-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    )
    recovery_dir: Path | None = None
    try:
        save_model.save_pretrained(temp_dir)
        if text_preprocessor is not None:
            text_preprocessor.save_backend.save_pretrained(temp_dir)
        if adapter_dir.exists():
            recovery_dir = adapter_dir.with_name(
                f".{adapter_dir.name}.incomplete-{int(time.time())}"
            )
            adapter_dir.rename(recovery_dir)
        try:
            temp_dir.rename(adapter_dir)
        except Exception:
            if recovery_dir is not None and recovery_dir.exists() and not adapter_dir.exists():
                recovery_dir.rename(adapter_dir)
            raise
        return adapter_dir
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


def _sweep_stale_atomic_save_temps(output_dir: Path) -> int:
    """Remove stale atomic-save staging dirs left by a hard-KILLed previous
    run in the same output dir (B-030).

    The atomic saves stage to ``.{name}.tmp-{pid}-{hash}`` dirs and rename
    into place, cleaning the stage in ``finally``. But the final-save path
    (``termination_save``) runs the cleanup INSIDE the SIGTERM handler; the
    launcher's KILL escalation lands mid-save before the ``finally``
    completes, so the ``.adapter.tmp-*`` (live-adapter path) and
    ``.step_*_adapter.tmp-*`` (step-checkpoint path) staging dirs leak
    (~300MB partial writes each). Swept on launch so each run starts
    disk-clean and no partial writes accumulate across run-terminations.

    Only matches the exact atomic-save staging pattern (``.`` prefix +
    name + ``.tmp-`` + pid + ``-`` + hash). NEVER touches a complete
    ``adapter/``, ``step_NNNNNN_adapter/``, or any non-staging output.
    Returns the number of stale entries removed (0 when clean).
    """
    output_dir = Path(output_dir)
    removed = 0
    for name in list(output_dir.iterdir()):
        n = name.name
        is_adapter_stage = n.startswith(".adapter.tmp-")
        is_step_adapter_stage = ".step_" in n and "_adapter.tmp-" in n
        # `write_json_atomic` stages FILES as `.{name}.tmp` (resume_state,
        # launch_config, ...). That shape is disjoint from the
        # `.{name}.tmp-{pid}-{hash}` dirs above, so it used to slip past this
        # sweep and accumulate forever. Reclaim it only when its published
        # target is absent (a `.tmp` alongside a live target is not stale).
        is_json_stage = (
            len(n) > 5
            and name.is_file()
            and n.startswith(".")
            and n.endswith(".tmp")
            and not (output_dir / n[1 : -len(".tmp")]).exists()
        )
        # Never sweep a raw `.tmp-*` entry that isn't the atomic-save pattern
        # (lenient guard against unrelated hidden temp files).
        if n.startswith(".tmp-"):
            continue
        if not (is_adapter_stage or is_step_adapter_stage or is_json_stage):
            continue
        if name.is_dir():
            shutil.rmtree(name, ignore_errors=True)
        else:
            name.unlink(missing_ok=True)
        removed += 1
    return removed


def _sweep_stale_kernel_meta_temps(root: Path | None = None, retries: int = 2) -> int:
    """Remove stale CANN/Ascend ``kernel_meta/kernel_meta_temp_*`` temp dirs
    left behind by previous runs (B-023).

    The box's Ascend/CANN runtime creates ``kernel_meta/kernel_meta_temp_*``
    temp dirs during training and tries to remove them at teardown, but the
    recursive ``rm -rf`` frequently FAILS with ``Directory not empty`` (a
    race / NFS-hold during CANN kernel-manager teardown). The failed cleanup
    leaves non-empty ``kernel_meta_temp_*`` dirs that accumulate across run
    histories (disk-leak risk, benign to training).

    On launch (new process, previous CANN processes dead) those stale temp
    dirs are safe to remove. The sweep retries the removal a few times with a
    brief sleep — the ``Directory not empty`` is transient, and a fresh
    launch generally has no active CANN writer on these paths.

    Only matches the exact ``kernel_meta_temp_*`` prefix under
    ``<root>/kernel_meta/``. NEVER touches the ``kernel_meta`` dir itself or
    any other kernel_meta content (e.g. a kernel cache). Returns the number
    of stale entries removed (0 when clean / no kernel_meta dir).
    """
    root = Path(root or Path.cwd())
    km_dir = root / "kernel_meta"
    if not km_dir.is_dir():
        return 0
    removed = 0
    for entry in list(km_dir.iterdir()):
        if not entry.name.startswith("kernel_meta_temp_"):
            continue
        for attempt in range(max(1, retries + 1)):
            try:
                if entry.is_dir() and not entry.is_symlink():
                    shutil.rmtree(entry)
                elif entry.exists():
                    entry.unlink()
                removed += 1
                break
            except OSError:
                if attempt < retries:
                    time.sleep(1)
                # On the final retry the OSError is swallowed — the stale
                # entry is left for the NEXT launch to sweep again (the
                # CANN teardown race is transient; a later process usually
                # can remove it).
    return removed


def termination_save(
    model: Any,
    text_preprocessor: Any,
    output_dir: Path,
    *,
    step: int | None,
    distributed: bool,
    rank: int = 0,
    metrics: list[dict[str, Any]] | None = None,
    planned_steps: int | None = None,
    resume_state: dict[str, Any] | None = None,
) -> Path | None:
    """SIGTERM final-save path (2026-08-25 backlog, r5; lane #20 soft-resume).

    Mirrors the loop-exit save (adapter dir + grpo_metrics.json + the
    'Saved adapter to ...' line) and additionally writes a
    ``step_{step:06d}_adapter`` checkpoint at the CURRENT boundary via the
    atomic save, so a stop at any point leaves a coherent checkpoint for the
    sync daemon and the next launch. Rank-0-only; a ``None`` model (TERM
    during model load) is a clean no-op. Runs inside the signal handler:
    never joins collectives, never touches the trainer's active metrics
    file, and the atomic step-dir save cannot corrupt an existing
    checkpoint even if the launcher's KILL escalation lands mid-save.

    ``resume_state`` (soft-resume, 2026-08-25): when provided, the snapshot
    is written atomically as ``<output_dir>/resume_state.json`` so the next
    launch with ``--resume-state`` continues the exact curriculum/router/temp/
    trust-region/repair state. The payload's ``step`` MUST match the
    checkpoint dir step — the F2 in-flight boundary (2026-08-26 code-review;
    bug-hunter mechanism 8 enforcement): a payload lagging the dir silently
    replays/skips an update boundary on the next launch (the SIGTERM
    coherence class). During model load (step=None) no dir is written and
    the payload (if any) carries the last completed step.
    """
    if rank != 0 or model is None:
        return None
    if resume_state is not None and step is not None:
        payload_step = int(resume_state.get("step", -1))
        # The resume_state carries the last COMPLETED step (step-1), while
        # `step` is the in-flight boundary being written. Allow step or step-1.
        if payload_step not in (int(step), int(step) - 1):
            raise ValueError(
                f"resume_state.step {payload_step} != checkpoint dir step {int(step)} "
                f"(or {int(step) - 1}) — the payload must match the step_NNNNNN_adapter "
                "boundary being written (F2 in-flight-boundary contract); refusing an "
                "incoherent soft-resume snapshot"
            )
    save_model = model.module if distributed else model
    if step is not None:
        ckpt_dir = Path(output_dir) / f"step_{int(step):06d}_adapter"
        save_peft_checkpoint_atomic(save_model, text_preprocessor, ckpt_dir)
        print(f"[checkpoint] saved adapter at step {step} to {ckpt_dir}", flush=True)
    adapter_dir = Path(output_dir) / "adapter"
    _atomic_save_adapter_dir(save_model, text_preprocessor, adapter_dir)
    if metrics is not None:
        (Path(output_dir) / "grpo_metrics.json").write_text(
            json.dumps(build_grpo_metrics_payload(metrics, planned_steps=planned_steps), indent=2)
            + "\n"
        )
    if resume_state is not None:
        write_json_atomic(Path(output_dir) / RESUME_STATE_FILENAME, resume_state)
        print(
            f"[checkpoint] wrote soft-resume state at step "
            f"{int(resume_state.get('step', -1))} to "
            f"{Path(output_dir) / RESUME_STATE_FILENAME}",
            flush=True,
        )
    print(f"\nSaved adapter to {adapter_dir}", flush=True)
    return adapter_dir


class GracefulStop:
    """SIGTERM handler state (2026-08-25 backlog, r5).

    The launcher's stop sequence TERMs the trainer and KILLs survivors after
    3s; with no handler the TERM killed the process instantly, risking a
    missing or partial final adapter save. The handler runs the SAME
    final-save path as the loop exit (see ``termination_save``), then exits.
    ``save_fn`` must be re-entrancy-tolerant: it runs inside the signal
    handler (main thread, between bytecodes — never inside a torch C call),
    so it must not join collectives or take locks the interrupted code could
    hold; the atomic checkpoint save satisfies that. SIGKILL cannot be
    caught — unchanged.
    """

    def __init__(self, save_fn: Any = None) -> None:
        self.save_fn = save_fn
        self.step: int | None = None
        self.requested = False

    def handler(self, signum: int, frame: Any) -> None:
        if self.requested:
            return
        self.requested = True
        print(
            json.dumps(
                {
                    "stage": "sigterm_graceful_stop",
                    "step": self.step,
                    "message": "SIGTERM received — running the final-save path",
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        try:
            if self.save_fn is not None:
                self.save_fn()
        except Exception as exc:
            # Never hang the launcher's KILL escalation: report and exit.
            print(
                json.dumps(
                    {
                        "stage": "sigterm_save_failed",
                        "error": str(exc)[:300],
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
            os._exit(1)
        os._exit(0)


def install_faulthandler_dumps(log_file: Any = None) -> Any:
    """Enable faulthandler + register the live stall-dump signals (tooling
    mandate 2026-08-26 — the gdb/pdb analogue for a wedged trainer).

    - ``faulthandler.enable()``: fatal signals (SIGSEGV/SIGFPE/SIGABRT/SIGBUS/
      SIGILL) dump all-thread stacks before the process dies — a silent
      native/OOM crash leaves its last frames in the run log.
    - ``SIGUSR1`` (all_threads=True): the operator-side "stall dump" — send
      ``kill -USR1 <trainer_pid>`` and the log receives every thread's stack
      while the trainer KEEPS RUNNING (the py-spy analogue, built in; the
      launch-level fallback is ``py-spy dump --pid``, see .sapo-loop/
      debuglane.md). Dumps land in ``log_file`` (default ``sys.stderr``,
      which the launcher redirects into the run log).
    - ``SIGABRT`` is covered by ``enable()`` itself (a fatal-signal dump to
      the same target — CPython forbids re-registering it via
      ``faulthandler.register``: "signal 6 cannot be registered, use
      enable() instead").

    Returns ``log_file`` (for tests). Idempotent; re-registration replaces
    the previous registration. When the target stream is captured (no real
    fileno — pytest fd-capture, io.StringIO), the registrations degrade
    gracefully: the dumps are simply unavailable and no exception escapes
    (2026-08-26 canary RED: the unguarded enable() raised
    io.UnsupportedOperation: fileno under captured stderr and killed main()
    before its abort path — 2 resume tests failed).
    """
    import faulthandler
    import io

    target = log_file if log_file is not None else sys.stderr
    try:
        faulthandler.enable()
    except (OSError, io.UnsupportedOperation):
        return target
    try:
        faulthandler.register(signal.SIGUSR1, target, all_threads=True)
    except (OSError, io.UnsupportedOperation):
        pass
    return target


def _run_dp4_batch_judge(
    args: argparse.Namespace,
    codes: Sequence[str],
    evidences: Sequence[str],
    task: dict,
) -> dict[int, dict[str, float | None]] | None:
    """dp4 batch judge with its OWN token budget (2026-08-27, critical review
    C1): the frozen per-candidate judge's ``--model-judge-max-tokens`` (launcher
    default 256) cannot fit an 8-candidate comparative JSON (~968 chars / ~280
    tokens minimum) — truncation made every step judge-absent. dp4 gets
    ``--judge-dp4-max-tokens`` (default 4096), independent of the frozen-judge
    knob."""
    endpoint = (getattr(args, "judge_dp4_endpoint", "") or "").strip()
    return _model_batch_dim_scores_dp4(
        codes,
        evidences,
        task,
        endpoint=endpoint,
        model=getattr(args, "judge_dp4_model", "dp4") or "dp4",
        max_tokens=int(getattr(args, "judge_dp4_max_tokens", 4096) or 4096),
        # timeout_s is intentionally NOT pinned here: the client resolves
        # None -> _dp4_client_timeout_s() so the deadline lives in exactly
        # one place (2026-09-08 dark-step s3 class extinction).
    )


def batch_judge_active(args: argparse.Namespace) -> bool:
    """dp4 batch comparative judge gate (2026-08-27): decoupled from the frozen
    model-judge machinery — dp4 is an HTTP endpoint judge (the Huanxin
    deepseek-v4-flash subscription), no local judge model is required, so
    ``--model-judge-enabled`` is irrelevant to it."""
    return bool(getattr(args, "batch_comparative_judge", False))


def batch_dp4_judge_weights(
    args: argparse.Namespace, calibrated: Mapping[str, float] | None
) -> dict[str, float]:
    """Weights for the dp4 batch comparative judge (2026-08-27, user binding).

    The dp4 judge is ACTIVE whenever ``--batch-comparative-judge`` is on: with
    no calibration file, a uniform map across MODEL_JUDGE_DIMENSIONS summing to
    ``args.reward_judge_mass`` (default 0.10) so J contributes exactly w_J; with
    calibration, the calibrated weights win. (The r17 calibration gate applies
    to the per-candidate frozen-BASE judge, not to dp4.)
    """
    if calibrated:
        return dict(calibrated)
    raw = getattr(args, "reward_judge_mass", None)
    mass = float(raw if raw is not None else 0.10)
    if mass <= 0.0 or not MODEL_JUDGE_DIMENSIONS:
        return {}
    per_dim = mass / len(MODEL_JUDGE_DIMENSIONS)
    return {dim: per_dim for dim in MODEL_JUDGE_DIMENSIONS}


def validate_batch_judge_config(args: argparse.Namespace) -> None:
    """Fail-closed guard for the batch COMPARATIVE judge (2026-08-27, user
    binding): the judge is EXCLUSIVELY the Huanxin dp4 (deepseek-v4-flash) model
    via ``--judge-dp4-endpoint`` — the same endpoint/auth ``claude -p huanxin -m
    dp4`` uses. When ``--batch-comparative-judge`` is ON, a dp4 endpoint is
    REQUIRED: the OLD code silently fell back to the in-process SELF-judge (the
    ACTIVE training model judging its own rollouts), which directly violates the
    dp4-ONLY mandate. This guard refuses to start (SystemExit) unless the dp4
    endpoint is set. When the flag is OFF (inert default) this is a no-op.
    """
    if not getattr(args, "batch_comparative_judge", False):
        return
    endpoint = (getattr(args, "judge_dp4_endpoint", "") or "").strip()
    if not endpoint:
        raise SystemExit(
            "--batch-comparative-judge requires --judge-dp4-endpoint (the Huanxin "
            "dp4 / deepseek-v4-flash endpoint used by `claude -p huanxin -m dp4`). "
            "The in-process self-judge fallback was REMOVED (2026-08-27): dp4 is "
            "the ONLY judge."
        )


def validate_reward_judge_wiring(args: argparse.Namespace) -> None:
    """Fail-closed guard for a configured-but-DARK judge mass (B-219, 2026-09-14).

    Measured live: a run trained for hours with ``judge_reward = None`` and an
    EMPTY ``judge_dim_scores`` map on 8/8 candidates while its launch config
    echoed ``judge: 0.10``. The two wirings are independent --
    ``--reward-judge-mass`` DEFAULTS to 0.10 while BOTH scorers default OFF --
    so a silently-dark weighted term was the DEFAULT launch shape. The policy
    optimized a reward whose documented composition was not the reward it saw.

    Either scorer satisfies this guard: the per-candidate frozen judge
    (``--model-judge-enabled`` WITH a ``--judge-model-path``) or the dp4 batch
    comparative judge (``--batch-comparative-judge``; its endpoint requirement
    is enforced by validate_batch_judge_config). A run that wants NO judge term
    must say so with ``--reward-judge-mass 0`` -- the dark default is refused,
    not warned.
    """
    mass = float(getattr(args, "reward_judge_mass", 0.0) or 0.0)
    if mass <= 0.0:
        return
    per_candidate = bool(getattr(args, "model_judge_enabled", False)) and bool(
        getattr(args, "judge_model_path", None)
    )
    if per_candidate or bool(getattr(args, "batch_comparative_judge", False)):
        return
    raise SystemExit(
        f"B-219 fail-closed: --reward-judge-mass {mass} is configured but NO judge "
        "scorer is wired -- the term would earn 0.0 every step while the launch "
        "config advertises it (the silent-darkness defect). Enable a scorer "
        "(--model-judge-enabled + --judge-model-path, or --batch-comparative-judge) "
        "or set --reward-judge-mass 0."
    )


def main() -> int:
    # The trainer's stdout is redirected to the run log; block buffering would
    # swallow every phase marker if the container is killed mid-stall. Line-buffer
    # so each stage print lands immediately (NPU-hang diagnostics).
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(line_buffering=True)
        except Exception:
            pass
    # 2026-08-26 (debug-lane tooling mandate): faulthandler at startup — a
    # crash dumps all-thread stacks to the run log, and SIGUSR1 is the live
    # "stall dump" signal for a wedged trainer (kill -USR1 <pid> -> stacks in
    # the log, process keeps running). Registered before model load so the
    # load phase (the silent-death zone) is covered.
    install_faulthandler_dumps()
    args = parse_args()
    # 2026-08-27 (user binding): dp4 is the ONLY reward judge. If the batch
    # comparative judge is enabled, the dp4 endpoint is mandatory — fail-closed,
    # never the (removed) in-process self-judge fallback.
    validate_batch_judge_config(args)
    if args.max_adaptive_new_tokens is None:
        args.max_adaptive_new_tokens = args.max_new_tokens
    if args.max_adaptive_new_tokens < args.max_new_tokens:
        raise ValueError("--max-adaptive-new-tokens must be >= --max-new-tokens")
    # Early output dir guard (before any expensive validation):
    _early_metrics = Path(args.output_dir) / "grpo_step_metrics.jsonl"
    if (
        _early_metrics.exists()
        and not getattr(args, "overwrite_output_dir", False)
        and not (getattr(args, "resume_from", None) or getattr(args, "resume_state", None))
    ):
        raise SystemExit(
            f"Output dir already contains {_early_metrics.name}; pass "
            "--overwrite-output-dir to start fresh."
        )
    # Early resume-state guard:
    if getattr(args, "resume_state", None) and not getattr(args, "adapter_init", None):
        raise ValueError(
            "--resume-state requires --adapter-init: the soft-resume must "
            "continue from the paused checkpoint's weights; restoring the "
            "curriculum/router state over fresh weights would be a silent "
            "policy rewind"
        )
    # Early resume-state JSON validation:
    if getattr(args, "resume_state", None):
        try:
            import json as _json

            _json.loads(Path(args.resume_state).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as _e:
            raise SystemExit(f"--resume-state file {args.resume_state} is not valid JSON: {_e}")
        else:
            _rs = json.loads(Path(args.resume_state).read_text(encoding="utf-8"))
            if _rs.get("version", 1) != 1:
                raise SystemExit(
                    f"--resume-state has unsupported version {_rs.get('version')} (expected 1)"
                )
    # 2026-08-26 (canary): fail fast on a clearly-LOCAL --model-name that
    # cannot possibly load — a typo'd path otherwise burns minutes in the
    # preprocessor/load phases before failing. Bare names and org/name hub
    # ids (no leading slash/dot, one slash max, no backslash) are left to
    # the loader.
    _model_path = Path(args.model_name)
    _name = args.model_name
    _looks_local = (
        _model_path.exists()
        or _name.startswith(("/", "./", "../"))
        or _name.count("/") > 1
        or "\\" in _name
    )
    if _looks_local and not (_model_path / "config.json").is_file():
        raise SystemExit(
            f"--model-name {args.model_name!r} has no config.json (checked "
            f"{_model_path / 'config.json'}) — refusing to start with a "
            f"missing model"
        )
    research_methods = load_research_methods(args.research_methods)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    step_metrics_path = output_dir / "grpo_step_metrics.jsonl"
    metrics_path = output_dir / "grpo_metrics.json"
    run_config_path = output_dir / "run_config.json"
    launch_config_path = output_dir / "launch_config.json"
    requested_task_ids = load_requested_task_ids(args.benchmark_file)
    reference_code_char_counts = load_reference_code_char_counts(args.benchmark_file)
    allowed_domains = set(args.domain_filter) if args.domain_filter else None

    # DDP setup
    # With --npu-device-map balanced-layers the model spans multiple NPUs and
    # must NOT be DDP-wrapped; treat it as a non-distributed single process.
    distributed = "RANK" in os.environ and args.npu_device_map != "balanced-layers"
    local_rank = int(os.environ.get("LOCAL_RANK", 0))
    rank = int(os.environ.get("RANK", 0))

    # ── Guardian alarm 8 (2026-08-26): repair-sidecar liveness guard ──
    # Runs 11/12 died via the all_fail_without_repair breaker because the
    # sidecar was SIGKILLed silently at launch (box-prep cleanup loops) and
    # the repair queue starved for 11h with zero operator-visible signal.
    # Boot check: alarm LOUDLY if the sidecar is not provably alive, then
    # re-check every step (below) and record the flag in each step record.
    sidecar_pidfile = Path(args.repair_sidecar_pidfile or (output_dir / "repair_sidecar.pid"))
    sidecar_log = (
        Path(args.repair_sidecar_log)
        if args.repair_sidecar_log
        else default_sidecar_log_path(output_dir)
    )
    # cwd-independent probe (defect 6): a cwd-relative default (logs/sapo_27b_ai
    # /...) must resolve against the REPO ROOT, matching the explicit
    # REPAIR_LOGDIR the relauncher passes -- else any non-root cwd probes a
    # nonexistent log and churns relaunches.
    if not sidecar_log.is_absolute():
        sidecar_log = ROOT / sidecar_log
    sidecar_alarm_state: dict[str, Any] = {"was_alive": None, "alarm_count": 0}
    _boot_sidecar = check_sidecar_liveness(
        sidecar_pidfile,
        sidecar_log,
        max_log_age_seconds=args.repair_sidecar_max_log_age,
    )
    if rank == 0:
        print(alarm_line(_boot_sidecar), flush=True)
        if _boot_sidecar["alarm"]:
            print(
                f"[{ALARM_MARKER}] relaunch the sidecar now via: "
                f"bash scripts/sapo_ensure_repair_sidecar.sh {output_dir}",
                flush=True,
            )
            sidecar_alarm_state["was_alive"] = False

    if distributed:
        if args.device == "npu":
            torch.npu.set_device(local_rank)
            device = torch.device(f"npu:{local_rank}")
            torch.distributed.init_process_group(backend="hccl")
        else:
            torch.cuda.set_device(local_rank)
            device = torch.device(f"cuda:{local_rank}")
            torch.distributed.init_process_group(backend="nccl")
    else:
        device = torch.device(args.device)
        if args.device == "npu":
            torch.npu.set_device(0)

    args.device = device

    # SIGTERM -> graceful final save (2026-08-25 backlog, r5): the launcher
    # stop TERMs then KILLs survivors after 3s; the default handler killed
    # the process instantly, risking a missing/partial final adapter save.
    # Registered BEFORE model load so a TERM at any point exits cleanly
    # (model is still None during load -> termination_save no-ops). The
    # closure late-binds `model`/`metrics` (assigned later in main); the
    # None/[] initializers keep the handler from raising UnboundLocalError
    # if the TERM lands before those assignments.
    model: Any = None
    text_preprocessor: Any = None
    metrics: list[dict[str, Any]] = []
    stop = GracefulStop()
    # Soft-resume (lane #20): the SIGTERM save also persists resume_state.json
    # at the last completed boundary. Pre-declared so a TERM during model load
    # (before the live-state closure exists) stays a clean no-op — the prior
    # run's resume_state.json on disk is left untouched.
    _resume_step_state: dict[str, int] = {"last_completed_step": 0}
    _build_live_resume_state: Any = None

    def _sigterm_save() -> None:
        state_payload: dict[str, Any] | None = None
        if rank == 0 and _build_live_resume_state is not None:
            state_payload = _build_live_resume_state(
                # F2: the payload step must match the checkpoint dir being
                # written (the in-flight boundary) — see _sigterm_payload_step.
                _sigterm_payload_step(stop.step, _resume_step_state["last_completed_step"]),
                sigterm=True,
            )
            write_json_atomic(output_dir / RESUME_STATE_FILENAME, state_payload)
        termination_save(
            model,
            text_preprocessor,
            output_dir,
            step=stop.step,
            distributed=distributed,
            rank=rank,
            metrics=metrics,
            planned_steps=args.grpo_steps,
            resume_state=state_payload,
        )

    stop.save_fn = _sigterm_save
    signal.signal(signal.SIGTERM, stop.handler)

    # Warm restart: load prior metrics and curriculum state from a previous JSONL.
    resume_step = 0
    resume_metrics: list[dict] = []
    if args.resume_from and rank == 0:
        resume_path = Path(args.resume_from)
        resume_metrics = load_grpo_step_metrics_jsonl(resume_path)
        if resume_metrics:
            resume_step = max(int(r.get("step", 0)) for r in resume_metrics)
            consistency_error = validate_resume_adapter_consistency(args.adapter_init, resume_step)
            if consistency_error:
                raise ValueError(consistency_error)
            print(
                json.dumps(
                    {
                        "stage": "warm_restart",
                        "resume_from": str(resume_path),
                        "resume_step": resume_step,
                        "prior_records": len(resume_metrics),
                    }
                )
            )

    # ── SOFT-RESUME (2026-08-25, lane #20) ────────────────────────────────
    # A resume_state.json is the EXACT state snapshot of a paused run. Loaded
    # on every rank (shared FS) so the step gate is identical across DDP
    # replicas; validation/prints are rank-0-only. The state is authoritative:
    # when present, the metrics-replay loop below is skipped in favor of the
    # exact restore.
    resume_state_payload: dict[str, Any] | None = None
    resume_state_arg = getattr(args, "resume_state", None)
    if resume_state_arg:
        if not args.adapter_init:
            raise ValueError(
                "--resume-state requires --adapter-init: the soft-resume must "
                "continue from the paused checkpoint's weights; restoring the "
                "curriculum/router state over fresh weights would be a silent "
                "policy rewind"
            )
        resume_state_payload = load_resume_state(resume_state_arg)
        state_step = int(resume_state_payload["step"])
        consistency_error = validate_resume_adapter_consistency(args.adapter_init, state_step)
        if consistency_error:
            raise ValueError(consistency_error)
        resume_step = max(resume_step, state_step)
        if rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "soft_resume",
                        "resume_state": str(resume_state_arg),
                        "resume_step": resume_step,
                        "curriculum_tasks": len(resume_state_payload.get("curriculum_state") or {}),
                        "repair_dedup_keys": len(
                            resume_state_payload.get("repair_converted_dedup_keys") or []
                        ),
                        "adaptive_temp": resume_state_payload.get("adaptive_temp"),
                        "trust_region": resume_state_payload.get("trust_region"),
                    }
                )
            )
    if resume_state_payload is not None and not args.resume_from:
        # Carry the prior step metrics forward (for in-memory aggregation and
        # JSONL seeding) from the run the state file belongs to.
        recorded_metrics = resume_state_payload.get("metrics_path")
        if recorded_metrics and Path(recorded_metrics).is_file():
            resume_metrics = load_grpo_step_metrics_jsonl(Path(recorded_metrics))
            if resume_metrics:
                resume_step = max(resume_step, max(int(r.get("step", 0)) for r in resume_metrics))

    if rank == 0:
        if not (args.resume_from or resume_state_payload):
            if step_metrics_path.exists() and not args.overwrite_output_dir:
                raise SystemExit(
                    f"Output dir already contains {step_metrics_path.name}; pass "
                    "--overwrite-output-dir to start fresh."
                )
            step_metrics_path.unlink(missing_ok=True)
            (output_dir / EVAL_RESULTS_FILENAME).unlink(missing_ok=True)
            # F5 (code-review wave): a TERM'd run leaves resume_state.json;
            # a FRESH start must not let a later --resume-state silently
            # restore the previous run's curriculum/router state.
            (output_dir / RESUME_STATE_FILENAME).unlink(missing_ok=True)
        metrics_path.unlink(missing_ok=True)
        run_config_path.unlink(missing_ok=True)
        launch_config_path.unlink(missing_ok=True)
        # B-030: a hard-KILLed previous run leaks .adapter.tmp-* /
        # .step_*_adapter.tmp-* staging dirs (the atomic-save `finally`
        # cleanup runs inside the SIGTERM handler before the launcher's KILL
        # escalation). Sweep them on launch so each run starts disk-clean.
        _n_stale = _sweep_stale_atomic_save_temps(output_dir)
        if _n_stale:
            print(
                f"[cleanup] swept {_n_stale} stale atomic-save staging dir(s) "
                f"from {output_dir} (B-030 hard-KILL leak)",
                flush=True,
            )
        # B-023: the box's CANN/Ascend runtime leaves non-empty
        # kernel_meta/kernel_meta_temp_* dirs behind (its recursive rm fails
        # with 'Directory not empty' at teardown). Sweep them on launch so
        # kernel_meta accumulation is bounded across run histories.
        _n_km = _sweep_stale_kernel_meta_temps()
        if _n_km:
            print(
                f"[cleanup] swept {_n_km} stale kernel_meta/kernel_meta_temp_* "
                f"dir(s) from {Path.cwd()} (B-023 CANN teardown leak)",
                flush=True,
            )
        launch_config = build_launch_config(args)
        write_json_atomic(launch_config_path, launch_config)
        print(
            json.dumps(
                {
                    "stage": "launch_config_written",
                    "path": str(launch_config_path),
                    "config": launch_config,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        # When resuming, seed the JSONL with prior records. For a same-dir
        # soft-resume the recorded metrics_path IS the file we append to — the
        # records are already there (append-only), so seeding would duplicate
        # them; only the in-memory list carries them for the final summary.
        if resume_metrics:
            same_file_resume = bool(
                resume_state_payload is not None
                and not args.resume_from
                and resume_state_payload.get("metrics_path")
                and Path(str(resume_state_payload["metrics_path"])).resolve()
                == step_metrics_path.resolve()
            )
            if not same_file_resume:
                for prior_record in resume_metrics:
                    append_grpo_metric_jsonl(step_metrics_path, prior_record)

    tasks = discover_tasks(
        Path(args.tasks_dir), requested_task_ids=requested_task_ids, allowed_domains=allowed_domains
    )
    if not tasks:
        raise ValueError("No GRPO tasks matched the requested filters")
    for task in tasks:
        task_id = str(task["meta"].get("id", task["task_dir"].name))
        task["reference_code_chars"] = reference_code_char_counts.get(task_id)
    if rank == 0:
        print(
            json.dumps(
                {
                    "stage": "tasks_ready",
                    "task_count": len(tasks),
                    "group_size": args.group_size,
                    "steps": args.grpo_steps,
                    "benchmark_file": args.benchmark_file,
                    "domain_filter": sorted(allowed_domains) if allowed_domains else None,
                    "research_methods": summarize_methods(research_methods),
                }
            )
        )

    # Load model with LoRA
    from peft import LoraConfig, PeftModel, TaskType, get_peft_model
    from transformers import (
        AutoConfig,
        AutoModelForCausalLM,
        AutoProcessor,
        AutoTokenizer,
        PreTrainedTokenizerFast,
    )

    runtime_compat = probe_model_runtime_compat(args.model_name, AutoConfig)
    if runtime_compat is not None:
        backend_blocker = trainer_backend_preflight_block(
            str(runtime_compat.get("config_model_type") or ""),
            [str(item) for item in (runtime_compat.get("config_architectures") or [])],
        )
        if backend_blocker is not None:
            print(
                json.dumps(
                    {
                        "stage": "trainer_backend_preflight",
                        "state": "blocked",
                        "model_type": runtime_compat.get("config_model_type"),
                        "architectures": runtime_compat.get("config_architectures"),
                        "error": backend_blocker,
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
            raise SystemExit(backend_blocker)

    text_preprocessor = load_text_preprocessor_backend(
        args.model_name, AutoTokenizer, AutoProcessor, PreTrainedTokenizerFast
    )
    tokenizer = text_preprocessor.text_backend
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    if rank == 0:
        print(
            json.dumps(
                {
                    "stage": "text_preprocessor_loaded",
                    "backend_kind": text_preprocessor.backend_kind,
                    "render_backend_class": text_preprocessor.render_backend.__class__.__name__,
                    "text_backend_class": text_preprocessor.text_backend.__class__.__name__,
                    "save_backend_class": text_preprocessor.save_backend.__class__.__name__,
                },
                ensure_ascii=False,
            )
        )

    preflight_task = tasks[0]
    preflight_task_id = preflight_task["meta"].get("id", preflight_task["task_dir"].name)
    preflight_record = {
        "example_id": f"grpo-preflight-{preflight_task_id}",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_prompt(preflight_task, research_methods=research_methods),
            },
            {"role": "assistant", "content": "pass"},
        ],
    }
    preflight_example = build_supervised_text_example(
        preflight_record,
        text_preprocessor,
        args.max_seq_length,
        train_on_completions_only=True,
    )
    _needs_mm_token_type_ids = str(
        runtime_compat.get("config_model_type") if runtime_compat is not None else ""
    ).startswith("gemma4")
    preflight_batch = pad_supervised_text_batch(
        [preflight_example],
        text_preprocessor.text_backend,
        torch,
        add_mm_token_type_ids=_needs_mm_token_type_ids,
    )

    model_config = AutoConfig.from_pretrained(args.model_name, trust_remote_code=True)
    model_kwargs: dict[str, Any] = {
        "trust_remote_code": True,
        "low_cpu_mem_usage": True,
        "torch_dtype": "auto",
    }
    npu_device_map: dict[str, str] | None = None
    if args.npu_device_map == "balanced-layers":
        visible_npus = _visible_npu_indices()
        npu_device_map = build_balanced_npu_layer_device_map(model_config, visible_npus)
        model_kwargs["device_map"] = npu_device_map
        model_kwargs["max_memory"] = {
            f"npu:{idx}": f"{args.npu_max_memory_gib}GiB" for idx in range(len(visible_npus))
        }
        if rank == 0:
            layer_counts: dict[str, int] = {}
            for module_name, mapped_device in npu_device_map.items():
                if ".language_model.layers." not in module_name:
                    continue
                mapped_device = str(mapped_device)
                layer_counts[mapped_device] = layer_counts.get(mapped_device, 0) + 1
            print(
                json.dumps(
                    {
                        "stage": "npu_device_map",
                        "visible_npus": visible_npus,
                        "layers": len(npu_device_map),
                        "language_layer_counts": layer_counts,
                        "max_memory_gib": args.npu_max_memory_gib,
                    },
                    ensure_ascii=False,
                )
            )
    # B-219: a configured judge mass with no scorer behind it used to start
    # silently dark -- refuse it before any load happens.
    validate_reward_judge_wiring(args)
    model = AutoModelForCausalLM.from_pretrained(args.model_name, **model_kwargs)
    if rank == 0:
        print(
            json.dumps(
                {"stage": "model_loaded", "model_class": model.__class__.__name__},
                ensure_ascii=False,
            )
        )
    if args.adapter_init:
        model = PeftModel.from_pretrained(model, str(args.adapter_init), is_trainable=True)
        resolved_target_modules = None
    else:
        resolved_target_modules = resolve_lora_target_modules(
            args.target_modules,
            model,
            args.target_module_regex,
        )
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=args.lora_rank,
            lora_alpha=args.lora_alpha,
            lora_dropout=0.05,
            target_modules=resolved_target_modules,
            bias="none",
        )
        model = get_peft_model(model, lora_config)
    # 2026-08-22: gradient checkpointing — the train-logprob phase held 4-8
    # live autograd graphs whose activations OOM'd the NPUs (7 crashes).
    # Diagnosed 2026-08-22 (agent): gradient_checkpointing_enable() was a
    # SILENT NO-OP in the trainer's transformers build (Qwen3_5 defines no
    # _set_gradient_checkpointing; old-format stacks no-op it) — the layers
    # never got the flag and FULL activations were retained (45 GiB for 4
    # graphs). FORCE the layer-level flags + use_cache=False + self-verify.
    try:
        model.gradient_checkpointing_enable()
        try:
            layers = model.base_model.model.model.layers
        except Exception:
            layers = model.model.model.layers
        for layer in layers:
            layer.gradient_checkpointing = True
            try:
                layer._gradient_checkpointing_func = functools.partial(
                    torch.utils.checkpoint.checkpoint, use_reentrant=False
                )
            except Exception:
                pass
        model.config.use_cache = False
        if rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "gradient_checkpointing_verified",
                        "flagged": sum(
                            1 for layer in layers if getattr(layer, "gradient_checkpointing", False)
                        ),
                        "total": len(layers),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
    except Exception as exc:  # pragma: no cover - model-class dependent
        if rank == 0:
            print(
                json.dumps({"stage": "gradient_checkpointing_failed", "error": str(exc)}),
                flush=True,
            )
    selective_training = apply_selective_training_controls(
        model,
        trainable_param_regex=getattr(args, "trainable_param_regex", None),
        freeze_param_regex=getattr(args, "freeze_param_regex", None),
    )
    trainable_param_tensors, trainable_param_names, trainable_param_count = (
        collect_trainable_parameters(model)
    )
    if rank == 0:
        print(
            json.dumps(
                {
                    "stage": "selective_training_applied",
                    **selective_training,
                    "trainable_parameter_count": trainable_param_count,
                    "trainable_parameter_sample": trainable_param_names[:12],
                },
                ensure_ascii=False,
            )
        )
    if npu_device_map is None:
        model.to(device)
        if rank == 0:
            print(
                json.dumps({"stage": "model_on_device", "device": str(device)}, ensure_ascii=False)
            )
    elif rank == 0:
        print(
            json.dumps(
                {"stage": "model_sharded_on_npus", "map_size": len(npu_device_map)},
                ensure_ascii=False,
            )
        )

    # ── frozen comprehensive judge (base model / older accepted adapter) ──
    # The judge is NEVER the current training policy: it is the base model,
    # optionally with an OLDER accepted adapter (accepted checkpoints from the
    # eval gate). 2026-08-26 (r16, user directive): the judge is ENABLED with
    # the base Qwen3.6-27B running on the SAME sharded model instance
    # (resolve_frozen_judge) — the second full 27B load is the memory-wall
    # class we keep dead. Without a calibration file the dimension weights
    # fall back to UNIFORM so the judge mass stays ACTIVE; the reward
    # verifier recomputes every judge-scored total, so a miscalibrated judge
    # is caught in numbers, not trusted blindly.
    judge_model = None
    judge_weights: dict[str, float] = {}
    judge_diagnostics_path = (
        Path(args.judge_diagnostics_path)
        if args.judge_diagnostics_path
        else (output_dir / "judge_diagnostics.jsonl" if args.model_judge_enabled else None)
    )
    if args.model_judge_enabled:
        judge_model, judge_shared, judge_path = resolve_frozen_judge(
            model=model,
            distributed=distributed,
            judge_model_path=args.judge_model_path,
            model_name=args.model_name,
            judge_adapter_path=args.judge_adapter_path,
        )
        if not judge_shared:
            if args.judge_adapter_path:
                judge_model = PeftModel.from_pretrained(
                    judge_model, str(args.judge_adapter_path), is_trainable=False
                )
            judge_model.to(args.judge_device)
        judge_model.eval()
        if args.judge_calibration:
            cal_path = Path(args.judge_calibration)
            if cal_path.is_file():
                calibration = json.loads(cal_path.read_text(encoding="utf-8"))
                judge_weights = {
                    str(dim): float(weight)
                    for dim, weight in (calibration.get("enabled_dims") or {}).items()
                    if float(weight) > 0.0
                }
        judge_weights = effective_judge_weights(judge_weights, model_judge_enabled=True)
        if rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "comprehensive_judge_loaded",
                        "judge_model_path": judge_path,
                        "judge_adapter_path": args.judge_adapter_path,
                        "judge_device": str(args.judge_device),
                        "judge_shared_with_training_model": bool(judge_shared),
                        "judge_weights": judge_weights,
                        "judge_weights_note": (
                            "CALIBRATION-GATED (r17 research-lane fix): no "
                            "calibration file -> judge mass exactly 0, the "
                            "masses renormalize over pass+shaped, and the "
                            "judge term contributes NOTHING until calibrated"
                            if not judge_weights
                            else "calibrated"
                        ),
                    },
                    ensure_ascii=False,
                )
            )
    text_forward_preflight = run_text_forward_preflight(
        model,
        preflight_batch,
        torch_module=torch,
        device=device,
    )
    if rank == 0:
        print(
            json.dumps(
                {"stage": "text_forward_preflight", **text_forward_preflight}, ensure_ascii=False
            )
        )

    if distributed and npu_device_map is None:
        model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[local_rank])
        if rank == 0:
            print(json.dumps({"stage": "ddp_wrapped"}, ensure_ascii=False))

    optimizer = torch.optim.AdamW(trainable_param_tensors, lr=args.lr)
    metrics = list(resume_metrics)
    curriculum = TaskCurriculum(
        ema_decay=args.curriculum_ema_decay,
        min_weight=args.curriculum_min_weight,
        quantum_priority=args.quantum_priority,
        uncertainty_bonus=args.curriculum_uncertainty_bonus,
    )
    adaptive_temp = AdaptiveTemperatureState(
        base_temp=args.temperature,
        step_size=args.adaptive_temp_step,
        # 2026-08-25: the escalation ladder itself is capped at the ceiling
        # (run-3's ladder climbed to 1.75 before the step-42 death spiral).
        max_temp=min(args.adaptive_temp_max, TEMP_ESCALATION_CEILING),
    )
    # 2026-08-26 (r10, run-6 killer): EOS-collapse rescue detector. The
    # streak is in-memory (a soft-resume re-arms it after 3 degenerate
    # steps); the ladder it escalates survives resume via persisted state.
    degenerate_detector = DegeneratePolicyDetector()
    # ── FV-GSPO: frontier router, mixture sampling, circuit breakers ──
    router = FrontierRouter(
        frontier_threshold=args.frontier_threshold,
        mastered_threshold=args.mastered_threshold,
    )
    difficulty_manifest_arg = getattr(args, "difficulty_manifest", None)
    if difficulty_manifest_arg:
        manifest_path = Path(difficulty_manifest_arg)
        if not manifest_path.exists():
            raise SystemExit(f"Invalid --difficulty-manifest {manifest_path}: file not found")
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid --difficulty-manifest {manifest_path}: {exc}") from exc
        hard_tasks = manifest.get("hard_tasks")
        if not isinstance(hard_tasks, list) or not hard_tasks:
            raise SystemExit(
                f"Invalid --difficulty-manifest {manifest_path}: 'hard_tasks' list required"
            )
        router.difficulty_manifest = frozenset(str(task_id) for task_id in hard_tasks)
        router.difficulty_scale = float(manifest.get("difficulty_scale", 0.25))
    if args.coverage_json:
        coverage_path = Path(args.coverage_json)
        if coverage_path.exists():
            try:
                router.load_coverage_map(json.loads(coverage_path.read_text(encoding="utf-8")))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"Invalid --coverage-json {coverage_path}: {exc}")
    breaker = CircuitBreakerState(
        window_size=args.circuit_breaker_window,
        clip_fraction_limit=args.circuit_breaker_clip_fraction_limit,
    )
    running_mad = RunningMAD()
    kl_state = (
        AdaptiveKLState(
            target_kl=args.kl_target,
            up_rate=args.kl_up_rate,
            down_rate=args.kl_down_rate,
            min_kl=args.kl_min,
            max_kl=args.kl_max,
            beta=args.kl_beta_init,
        )
        if args.adaptive_kl
        else None
    )
    repair_queue_path = (
        Path(args.repair_queue_path)
        if args.repair_queue_path
        else output_dir / "repair_queue.jsonl"
    )
    if not args.repair_converted_jsonl:
        # Flag > $REPAIR_CONVERTED_JSONL (launcher-pinned) > run-dir default.
        # Without this the all-fail-without-repair breaker reads 0 conversions
        # forever even while the sidecar converts.
        args.repair_converted_jsonl = str(output_dir / "repair_stage" / "repair_converted.jsonl")
    recent_frontier: list[str] = []
    total_probes = 0
    if resume_state_payload is not None:
        # ── SOFT-RESUME: the state file is authoritative and exact — restore
        # the curriculum EMA/task-seen, adaptive-temp ladder, router/mix state
        # and re-seed the repair-converted ledger. Metrics-replay is NOT used:
        # replaying records over the exact state would double-count probes and
        # corrupt the restored EMA/posteriors.
        restore_curriculum_state(curriculum, resume_state_payload)
        restore_adaptive_temp_skip_counter(adaptive_temp, resume_state_payload)
        restore_router_state(router, resume_state_payload)
        recent_frontier = [
            str(task_id) for task_id in (resume_state_payload.get("recent_frontier") or [])
        ]
        total_probes = max(0, int(resume_state_payload.get("total_probes", 0)))
        # Rank-0-only: the ledger is a shared file append; two ranks racing to
        # re-seed the same key could duplicate it.
        reseeded_keys = 0
        if rank == 0:
            reseeded_keys = reseed_repair_converted_ledger(
                args.repair_converted_jsonl,
                resume_state_payload.get("repair_converted_dedup_keys") or [],
                status=resume_state_payload.get("repair_converted_status"),
            )
        if rank == 0 and reseeded_keys:
            print(
                json.dumps(
                    {
                        "stage": "repair_ledger_reseeded",
                        "restored_keys": reseeded_keys,
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
    else:
        # Replay curriculum state from resumed records
        for prior in resume_metrics:
            task_name, router_probed = restore_router_from_record(
                router,
                tasks,
                prior,
                default_group_size=args.group_size,
            )
            mr = float(prior.get("mean_reward", 0.0))
            if task_name:
                curriculum.record(task_name, mr)
            if router_probed:
                total_probes += 1
            if bool(prior.get("skipped")) and prior.get("reason") == "low_reward_signal":
                adaptive_temp.record_skip("low_reward_signal")
            elif not bool(prior.get("skipped")):
                adaptive_temp.record_update()

    for task in tasks:
        task.update(
            build_task_runtime_context(task, detail_budget_cap=args.reward_detail_budget_cap)
        )

    random.seed(42 + rank)
    _last_checkpoint_time = time.time()
    # Cumulative trust-region violation counter (audit #2: scale_lr halved the
    # LR in place without any log line or record field). On a soft-resume the
    # count AND the scaled optimizer LR continue from the paused run.
    trust_region_violation_count = (
        restore_trust_region_state(
            optimizer,
            resume_state_payload,
            resume_fresh=bool(getattr(args, "trust_region_resume_fresh", False)),
        )
        if resume_state_payload is not None
        else 0
    )
    # ── Soft-resume persistence (2026-08-25, lane #20) ──
    # resume_state.json is written atomically at every completed-step boundary
    # (immediately after the step record is emitted) and again on SIGTERM, so
    # a relaunch with --resume-state continues the exact curriculum/router/
    # temperature/trust-region/repair state instead of restarting the
    # curriculum. The payload's step is the LAST COMPLETED step.
    _resume_step_state["last_completed_step"] = resume_step
    resume_state_path = output_dir / RESUME_STATE_FILENAME

    def _build_live_resume_state(completed_step: int, *, sigterm: bool = False) -> dict[str, Any]:
        return build_resume_state_payload(
            step=completed_step,
            curriculum_state=curriculum.state,
            adaptive_temp_state=adaptive_temp.to_dict(),
            router_state=router.state,
            recent_frontier=recent_frontier,
            total_probes=total_probes,
            trust_region_violation_count=trust_region_violation_count,
            optimizer_lr=float(optimizer.param_groups[0]["lr"]),
            repair_converted_dedup_keys=collect_repair_converted_dedup_keys(
                args.repair_converted_jsonl
            ),
            repair_converted_status=collect_repair_converted_status(args.repair_converted_jsonl),
            metrics_path=str(step_metrics_path),
            output_dir=str(output_dir),
            resume_from=args.resume_from,
            sigterm=sigterm,
        )

    def _persist_resume_state(completed_step: int) -> None:
        """Record + atomically persist the snapshot at a completed boundary."""
        if rank != 0:
            return
        _resume_step_state["last_completed_step"] = int(completed_step)
        write_json_atomic(
            resume_state_path,
            _build_live_resume_state(_resume_step_state["last_completed_step"]),
        )

    # Per-candidate SAPO stats from the last inner epoch (audit #3).
    sapo_candidate_stats: list[dict[str, float]] | None = None
    # Zero-change gate (2026-08-25 manager directive): snapshot lora_B before
    # training starts; after every optimizer step max|Δlora_B| vs this snapshot
    # is measured — an EXACT zero fires the zero_change_alarm (0-change adapter
    # vs base is unacceptable).
    lora_b_init_snapshot = collect_lora_b_init_snapshot(
        trainable_param_names, trainable_param_tensors
    )
    if rank == 0:
        print(
            json.dumps(
                {
                    "stage": "zero_change_snapshot",
                    "lora_b_params_tracked": len(lora_b_init_snapshot),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

    for step in range(1, args.grpo_steps + 1):
        # Skip steps already covered by warm restart
        if step <= resume_step:
            continue
        # SIGTERM handler saves the checkpoint at this current boundary.
        stop.step = step
        # FV-GSPO mixture sampling: 50% targeted frontier/repair, 25% neighboring
        # variants, 25% replay (see docs/frontier-verifier-gspo-design-2026-08-04.md §6).
        weights = build_mixture_weights(
            router,
            tasks,
            step,
            mix_targeted=args.mix_targeted,
            mix_neighbor=args.mix_neighbor,
            mix_replay=args.mix_replay,
            recent_frontier=recent_frontier,
            neighbor_window=args.neighbor_window,
            adaptive=args.adaptive_mixture,
        )
        for index, task in enumerate(tasks):
            if weights[index] <= 0.0:
                continue
            for method in research_methods:
                weights[index] = max(
                    0.0,
                    float(method.adjust_task_weight(weights[index], task=task, stage="grpo")),
                )
        weight_sum = sum(weights)
        if not math.isfinite(weight_sum) or weight_sum <= 0.0:
            if rank == 0:
                print(
                    json.dumps(
                        {
                            "stage": "no_trainable_tasks",
                            "step": step,
                            "reason": "all_tasks_quarantined_or_zero_weight",
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
            break
        task_index = random.choices(range(len(tasks)), weights=weights, k=1)[0]
        task = tasks[task_index]
        task_prob = weights[task_index] / weight_sum if weight_sum > 0 else 1.0 / len(tasks)
        prompt = build_prompt(task, research_methods=research_methods)
        test_harness = load_test_harness(task["tests_py"])

        # Generate group of solutions (adaptive temperature escalation on repeated low-signal skips;
        # adaptive group size from the posterior router — review 2026-08-05 #4)
        active_model = model.module if distributed else model
        active_model.eval()
        # 2026-08-25: hard ceiling at 1.3 — behavior temperature must never
        # exceed the escalation ceiling regardless of the ladder.
        effective_temperature = clamp_adaptive_behavior_temperature(adaptive_temp.current_temp())
        # 2026-08-27 (r19, user binding): every round rolls out 8 candidates —
        # a HARD FLOOR (default 1 = inert) overrides the router's adaptive 4.
        effective_g = effective_group_size(
            recommended=router.recommended_group_size(task["task_id"]),
            max_adaptive_group=args.max_adaptive_group,
            min_group_size=getattr(args, "min_group_size", 1),
        )
        generation_token_budget = adaptive_generation_token_budget(
            task.get("reference_code_chars"),
            base_tokens=args.max_new_tokens,
            max_tokens=args.max_adaptive_new_tokens,
        )
        if rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "step_begin",
                        "step": step,
                        "task": task["task_id"],
                        "temperature": effective_temperature,
                        "group_size": effective_g,
                        "greedy_count": greedy_rollout_count(
                            effective_g,
                            float(getattr(args, "greedy_rollout_fraction", 0.0) or 0.0),
                        ),
                        "max_new_tokens": generation_token_budget,
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
        (
            raw_responses,
            prompt_text,
            rollout_prompt_token_ids,
            rollout_prompt_attention_mask,
            rollout_completion_token_ids,
        ) = generate_group(
            active_model,
            text_preprocessor,
            prompt,
            args,
            temperature=effective_temperature,
            count=effective_g,
            max_new_tokens=generation_token_budget,
            return_token_ids=True,
        )
        # The harness sees executable Python only, while every policy
        # probability is evaluated on the exact raw decoded rollout. Using the
        # extracted fenced body as the behavior action invalidates the
        # importance ratio whenever the model emitted fences or surrounding
        # text.
        codes = [extract_code(response) for response in raw_responses]
        generation_diagnostics = build_generation_diagnostics(
            raw_responses=raw_responses,
            codes=codes,
            completion_token_ids=rollout_completion_token_ids,
            max_new_tokens=generation_token_budget,
            eos_token_ids=configured_eos_token_ids(active_model, text_preprocessor.text_backend),
        )
        if rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "generation_done",
                        "step": step,
                        "n_codes": len(codes),
                        "max_code_chars": max((len(code) for code in codes), default=0),
                        **generation_diagnostics,
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
        _release_device_cache(torch)

        consistent_old_log_probs = []
        consistent_old_token_counts = []
        consistent_entropies = []
        consistent_old_token_lps: list[torch.Tensor] | None = (
            [] if args.loss_mode == "sapo" else None
        )
        with torch.no_grad():
            for raw_response, completion_ids in _strict_zip(
                raw_responses, rollout_completion_token_ids
            ):
                call_kwargs = dict(
                    add_mm_token_type_ids=_needs_mm_token_type_ids,
                    return_entropy=True,
                    policy_temperature=effective_temperature,
                    recompute_backward=bool(getattr(args, "chunked_recompute_backward", True)),
                )
                if consistent_old_token_lps is not None:
                    call_kwargs["return_token_log_probs"] = True
                result = compute_completion_log_prob(
                    active_model,
                    tokenizer,
                    prompt_text,
                    raw_response,
                    device,
                    args.max_seq_length,
                    args.logit_clip,
                    prompt_token_ids=rollout_prompt_token_ids,
                    prompt_attention_mask=rollout_prompt_attention_mask,
                    completion_token_ids=completion_ids,
                    **call_kwargs,
                )
                if consistent_old_token_lps is not None:
                    old_log_prob, old_token_count, entropy, old_tokens = result
                    consistent_old_token_lps.append(old_tokens)
                else:
                    old_log_prob, old_token_count, entropy = result
                consistent_old_log_probs.append(old_log_prob.detach())
                consistent_old_token_counts.append(old_token_count.detach())
                consistent_entropies.append(entropy.detach())
                # Release the allocator cache between per-completion forwards:
                # long sequential forward runs are the ASI2 27B stall trigger.
                _release_device_cache(torch)
        old_log_probs = torch.stack(consistent_old_log_probs)
        old_token_counts = torch.stack(consistent_old_token_counts)
        entropy_values = [float(value.item()) for value in consistent_entropies]
        entropy_mean = float(sum(entropy_values) / len(entropy_values)) if entropy_values else None
        completion_lengths = generation_diagnostics["completion_token_lengths"]
        generation_tokens = int(sum(completion_lengths))
        mean_response_length = (
            float(generation_tokens / len(completion_lengths)) if completion_lengths else 0.0
        )
        truncation_rate = float(generation_diagnostics["truncation_rate"])
        if rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "logprob_done",
                        "step": step,
                        "generation_tokens": generation_tokens,
                        "entropy_mean": entropy_mean,
                        "behavior_temperature": effective_temperature,
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
        _release_device_cache(torch)

        # ── r10 / T1a: EOS-collapse detection + quarantine-integrity gate ──
        # 2026-09-01 (data-efficiency reorder): computed here, BEFORE the
        # reward pass — the alarm needs only entropy_mean (logprob pass) and
        # completion_token_lengths (generation diagnostics), both already
        # available. A collapsed step must never pay the expensive reward
        # pass (harness subprocess + self-eval/judge forwards per candidate)
        # on evidence-free 1-token completions, and repair-routing must be
        # suppressed on evidence-free collapsed rollouts (run-6 quarantined
        # ALL 20 tasks incl. the 5 learnable ones under the collapse).
        degenerate_alarm = alarm_degenerate_policy(
            degenerate_detector,
            adaptive_temp,
            entropy_mean=entropy_mean,
            completion_token_lengths=generation_diagnostics["completion_token_lengths"],
        )
        if degenerate_alarm and rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "degenerate_policy_alarm",
                        "step": step,
                        "task": task["task_id"],
                        "consecutive_degenerate": degenerate_detector.consecutive_degenerate,
                        "entropy_mean": entropy_mean,
                        "completion_token_lengths": generation_diagnostics[
                            "completion_token_lengths"
                        ],
                        "eos_termination_rate": generation_diagnostics["eos_termination_rate"],
                        "escalated_temperature": adaptive_temp.current_temp(),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
        quarantine_suppressed = quarantine_gate_active(
            degenerate_policy_alarm=degenerate_alarm,
            entropy_mean=entropy_mean,
            completion_token_lengths=generation_diagnostics["completion_token_lengths"],
        )

        # Score each solution with verifier-aware shaped rewards + optional self-evaluation.
        judge_enabled = bool(args.model_judge_enabled and judge_model is not None)
        evaluations = []
        # 2026-08-27 (r19): the batch COMPARATIVE judge needs every candidate's
        # code + pass evidence collected across the group for one forward.
        batch_codes: list[str] = list(codes)
        batch_evidences: list[str] = []
        self_repair_summary: dict[str, Any] = {
            "enabled": int(args.self_repair_rounds > 0),
            "max_rounds": args.self_repair_rounds,
            "candidates_repaired": 0,
            "repairs_passed": 0,
            "total_repair_rounds": 0,
        }
        # 2026-09-01 (data-efficiency): on a quarantine-suppressed (collapsed)
        # step, SKIP the expensive reward pass — harness subprocess + self-eval
        # /judge forwards per candidate on evidence-free 1-token completions is
        # pure waste (run-6 class: [1,1,1,1], entropy 0.0137). Synthesized
        # zero-value entries keep every downstream consumer (reward tensors,
        # probe, curriculum, advantages, rollout record, emit) unchanged.
        for c in codes:
            if quarantine_suppressed:
                evaluations.append(evidence_free_candidate_entry())
                continue
            entry = evaluate_candidate(
                c,
                test_harness,
                task,
                args,
                research_methods=research_methods,
                model=active_model if args.self_evaluation_enabled else None,
                backend=text_preprocessor
                if (args.self_evaluation_enabled or judge_enabled)
                else None,
                device=device if (args.self_evaluation_enabled or judge_enabled) else None,
                judge_model=judge_model if judge_enabled else None,
                judge_weights=judge_weights if judge_enabled else None,
                judge_diagnostics_path=(
                    judge_diagnostics_path if (judge_enabled and rank == 0) else None
                ),
                step=step,
            )
            # Teacher-free self-repair (plan §8): a failing candidate is re-rolled
            # by the policy itself with its exact harness errors appended, up to
            # `--self-repair-rounds` rounds. Only an independently-passing repair
            # replaces the original behavior sample, so the GRPO relative
            # advantage stays well-defined on the policy's own outputs.
            if args.self_repair_rounds > 0 and float(entry.get("pass_reward", 0.0)) <= 0.0:
                repair_ctx = _self_repair_failing_candidate(
                    model=active_model,
                    text_preprocessor=text_preprocessor,
                    device=device,
                    test_harness=test_harness,
                    task=task,
                    code=c,
                    task_prompt=prompt,
                    result={
                        "passed": bool(entry.get("pass_reward", 0.0) > 0.0),
                        "details": entry.get("details", []),
                    },
                    args=args,
                    max_rounds=args.self_repair_rounds,
                    temperature=effective_temperature,
                )
                self_repair_summary["total_repair_rounds"] += len(repair_ctx.get("attempted", []))
                if repair_ctx.get("passed"):
                    # Accept the passing repair: suffuse its rewards into the entry.
                    repaired_code = repair_ctx["code"]
                    repaired_entry = evaluate_candidate(
                        repaired_code,
                        test_harness,
                        task,
                        args,
                        research_methods=research_methods,
                        model=active_model if args.self_evaluation_enabled else None,
                        backend=text_preprocessor
                        if (args.self_evaluation_enabled or judge_enabled)
                        else None,
                        device=device if (args.self_evaluation_enabled or judge_enabled) else None,
                        judge_model=judge_model if judge_enabled else None,
                        judge_weights=judge_weights if judge_enabled else None,
                        judge_diagnostics_path=None,
                        step=step,
                    )
                    self_repair_summary["repairs_passed"] += 1
                    # The repair was sampled from a different prompt containing
                    # the failing code and harness errors. Keep its success as a
                    # conversion diagnostic, but NEVER attach that reward to the
                    # original failing rollout/log-probabilities.
                    annotate_self_repair_diagnostics(
                        entry,
                        repaired_entry,
                        repair_ctx,
                    )
                else:
                    entry["self_repair_passed"] = False
                    entry["self_repair_best_round"] = repair_ctx.get("best_round", 0)
                self_repair_summary["candidates_repaired"] += 1
            # Eval-results persistence (2026-08-25, verifier G1): append the
            # per-candidate harness outcome + reward components AFTER scoring
            # (rank-0 only; O(1) append, never blocks the loop). Repair-lane
            # re-evaluations never overwrite the original rewards, so the row
            # reflects the candidate exactly as it entered the policy loss.
            if rank == 0:
                append_grpo_metric_jsonl(
                    output_dir / EVAL_RESULTS_FILENAME,
                    build_eval_result_row(
                        step=step,
                        index=len(evaluations),
                        code=c,
                        entry=entry,
                        detail_budget=int(task.get("detail_budget", 1)),
                    ),
                )
            evaluations.append(entry)
            # (r19) collect per-candidate executable evidence for the batch
            # comparative judge (anchors its ranking to real pass/fail).
            batch_evidences.append(
                "tests passed: {}; failures: {}".format(
                    bool(float(entry.get("pass_reward", 0.0) or 0.0) > 0.0),
                    "; ".join(str(d)[:120] for d in (entry.get("details") or [])[:3]) or "none",
                )
            )
        # 2026-08-27 (r19, user binding): BATCH COMPARATIVE SELF-JUDGE — the ACTIVE
        # training model judges ALL group candidates AT ONCE against each other.
        # Pass is part of the comprehensive score (blend mass w_P), never the whole
        # score; the comparative judge dims add quality/topic mass. Fail-closed:
        # any candidate the model fails to score keeps dims None (judge-absent).
        if batch_judge_active(args) and rank == 0 and not quarantine_suppressed:
            # 2026-08-27 (user binding): the judge is EXCLUSIVELY the Huanxin dp4
            # (deepseek-v4-flash) model — all candidates scored at once in one
            # comparative prompt through the Anthropic-compatible endpoint. The
            # in-process SELF-judge fallback was REMOVED (fail-closed at startup
            # via validate_batch_judge_config): dp4 is the ONLY judge. Decoupled
            # from the frozen model-judge machinery (dp4 is an HTTP judge).
            (getattr(args, "judge_dp4_endpoint", "") or "").strip()
            batch_weights = batch_dp4_judge_weights(args, judge_weights if judge_enabled else None)
            # B-046 (2026-09-04, user directive "scoring errors must be retried
            # twice"): a single transient dp4/transport failure must not cost a
            # judged step. Retry the whole batch judge up to 2 extra times;
            # success is a non-None parse whose cells are not all-None.
            batch_scores = None
            for _dp4_attempt in range(1 + 2):
                batch_scores = _run_dp4_batch_judge(args, batch_codes, batch_evidences, task)
                if batch_scores is not None and any(
                    any(v is not None for v in (cell or {}).values())
                    for cell in batch_scores.values()
                ):
                    break
                if _dp4_attempt < 2:
                    time.sleep(5.0 * (_dp4_attempt + 1))
            if batch_scores is None:
                # 2026-08-27 (critical review C2): judge-absent must be LOUD —
                # a silent None meant w_J=0 with no operator-visible signal.
                print(
                    json.dumps(
                        {
                            "stage": "dp4_judge_failed",
                            "step": step,
                            "task": task["task_id"],
                            "reason": "no_scores_from_dp4",
                            "diag": get_last_dp4_judge_diag(),
                        }
                    ),
                    flush=True,
                )
            if (
                batch_scores is not None
                and batch_scores
                and all(
                    all(v is None for v in (cell or {}).values()) for cell in batch_scores.values()
                )
            ):
                # B-037: all-None cells = reply decoded but no candidate key
                # matched — make it LOUD (was a silent judge-absent).
                print(
                    json.dumps(
                        {
                            "stage": "batch_judge_all_dims_none",
                            "step": step,
                            "task": task["task_id"],
                            "hint": "judge reply decoded but no candidate key matched",
                        }
                    ),
                    flush=True,
                )
            if batch_scores is not None:
                for idx, entry in enumerate(evaluations):
                    cell = batch_scores.get(idx)
                    if cell is None:
                        continue
                    entry["model_dim_scores"] = dict(cell)
                    entry["judge_reward"] = (
                        judge_composite_score(cell, batch_weights) if batch_weights else None
                    )
                    # Pass stays a part of the comprehensive score: recompute the
                    # blended total with the comparative judge dims applied.
                    entry["total_reward"] = compose_policy_training_reward(
                        entry,
                        args,
                        model_dim_scores=dict(cell),
                        judge_weights=batch_weights,
                    )
        # Incorporate self-eval reward into total
        for entry in evaluations:
            entry["total_reward"] = entry.get("total_reward", entry.get("reward", 0.0))
            entry["total_reward"] = entry["total_reward"] + entry.get("self_eval_reward", 0.0)
        if rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "eval_done",
                        "step": step,
                        "n_candidates": len(evaluations),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
        _release_device_cache(torch)

        rewards = torch.tensor(
            [float(entry["total_reward"]) for entry in evaluations], device=device
        )
        pass_rewards = torch.tensor(
            [float(entry["pass_reward"]) for entry in evaluations], device=device
        )
        shaped_rewards = torch.tensor(
            [float(entry["shaped_reward"]) for entry in evaluations], device=device
        )
        syntax_rewards = torch.tensor(
            [float(entry["syntax_reward"]) for entry in evaluations], device=device
        )
        interface_rewards = torch.tensor(
            [float(entry["interface_reward"]) for entry in evaluations], device=device
        )
        verifier_rewards = torch.tensor(
            [float(entry["verifier_reward"]) for entry in evaluations], device=device
        )
        brevity_rewards = torch.tensor(
            [float(entry.get("brevity_reward", 0.0)) for entry in evaluations], device=device
        )
        self_eval_rewards = torch.tensor(
            [float(entry.get("self_eval_reward", 0.0)) for entry in evaluations], device=device
        )

        # 2026-08-27 (r19, user binding): NORMALIZE the raw reward scores across
        # all candidates of the group before the GRPO/SAPO advantage computation.
        # 'none' (default, inert) leaves the raw path byte-identical.
        # 2026-08-27 (critical review H1): normalization feeds ONLY the advantage
        # path — the router probe, curriculum EMA and reward diagnostics keep the
        # ABSOLUTE reward scale (minmax on a mastered all-pass group is
        # indistinguishable from a fresh all-fail group; feeding that scale to
        # the frontier router destroys mastery gating).
        reward_normalization = getattr(args, "reward_normalization", "none") or "none"
        advantage_rewards = rewards
        if reward_normalization != "none":
            advantage_rewards, _norm_rec = normalize_group_rewards(
                rewards, mode=reward_normalization
            )
            if rank == 0:
                print(
                    json.dumps(
                        {
                            "stage": "reward_normalized",
                            "step": step,
                            "mode": reward_normalization,
                            "task": task["task_id"],
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )

        # Compute group-relative rewards (ABSOLUTE scale — router/curriculum).
        mean_reward = rewards.mean()
        signal_stats = reward_signal_stats(
            rewards,
            pass_rewards,
            syntax_rewards,
            interface_rewards,
            verifier_rewards,
            brevity_rewards,
        )
        task_state = curriculum.record(task["task_id"], float(mean_reward))

        # Aggregate frozen-judge dimension scores across the group for metrics.
        model_dim_means: dict[str, float] = {}
        if judge_enabled:
            for dim in MODEL_JUDGE_DIMENSIONS:
                values = [
                    float(entry["model_dim_scores"][dim])
                    for entry in evaluations
                    if isinstance(entry.get("model_dim_scores", {}).get(dim), (int, float))
                ]
                if values:
                    model_dim_means[dim] = sum(values) / len(values)

        # ── FV-GSPO: probe the group and route it (frontier router) ──
        # (degenerate_alarm/quarantine_suppressed computed BEFORE the reward
        # pass — see the r10/T1a block above the eval loop)
        pass_rate = float(pass_rewards.mean().item())
        # B-245: keep the curriculum's compression strength in step with the
        # policy's actual yield (weight() reads this on the NEXT sampling step).
        curriculum.global_pass_rate = pass_rate
        probe = router.probe_record(
            task["task_id"],
            step,
            pass_rate,
            # Route on dispersion in the reward that actually reaches SAPO.
            # Inactive component variance (historically brevity at weight 0)
            # must not misclassify a flat group as learnable RL data.
            signal_stats["reward_std"],
            group_size=effective_g,
            # T1a: a collapsed policy must never produce evidence-free
            # quarantines — the probe keeps the task in the RL targeted pool.
            suppress_repair=quarantine_suppressed,
        )
        route = str(probe["route"])
        total_probes += 1
        all_fail = pass_rate == 0.0
        frontier_fraction = router.frontier_fraction()
        if route in RL_ROUTES:
            recent_frontier.append(task["task_id"])
            del recent_frontier[: -args.neighbor_window]

        # ── FV-GSPO: leave-one-out advantages (Dr.GRPO) ──
        # No per-task standard-deviation normalization; optional shared running
        # MAD is the only allowed batch-level scaling.
        if args.advantage_mode == "group_std":
            # Ablation baseline: reproduce the legacy per-group normalized advantage.
            std_reward = rewards.std(unbiased=False)
            advantage_scale = max(signal_stats["signal_std"], float(std_reward.item()), 1e-8)
            advantages = ((rewards - mean_reward) / advantage_scale).clamp(
                -args.advantage_clip,
                args.advantage_clip,
            )
        else:  # loo (FV-GSPO default)
            # 2026-08-27 (critical review H1): advantages consume the NORMALIZED
            # rewards (advantage_rewards) when --reward-normalization is on; the
            # router/curriculum above used the absolute scale.
            advantages = leave_one_out_advantages(advantage_rewards)
            if args.loo_advantage_scale == "shared_mad":
                running_mad.update(advantages)
                advantages = advantages / running_mad.scale
            advantage_scale = (
                running_mad.scale if args.loo_advantage_scale == "shared_mad" else None
            )
            advantages = advantages.clamp(-args.advantage_clip, args.advantage_clip)

        # Persist the actual optimization-signal magnitude. Component reward
        # dispersion can clear the route gate even when its weighted
        # contribution to total-reward LOO advantages is small; these fields
        # distinguish a real optimizer call from a useful policy-gradient
        # batch. Only label them LOO when that is the configured estimator.
        loo_advantage_rms = None
        loo_advantage_mean_abs = None
        if args.advantage_mode == "loo":
            advantage_values = advantages.detach().float()
            loo_advantage_rms = float(torch.sqrt(torch.mean(advantage_values.square())).item())
            loo_advantage_mean_abs = float(torch.mean(advantage_values.abs()).item())
        update_signal_magnitude, update_signal_kind = policy_update_signal_magnitude(
            advantage_mode=args.advantage_mode,
            signal_stats=signal_stats,
            loo_advantage_rms=loo_advantage_rms,
            # 2026-09-02 flat-advantage fix: a magnitude from ONE outlier
            # candidate (7/8 identical rewards -> 2 distinct advantage values)
            # is noise, not group signal — gate it off like any flat group
            # (resume-3 step-26 RED class).
            advantages=advantages,
            pass_rate=pass_rate,
            min_rms_for_update=getattr(args, "min_rms_for_update", None),
        )

        repair_queued = False
        # Training-log instrumentation (2026-08-25): the per-candidate reward
        # scores of ALL rollout samples (raw reward, shaped reward, pass/fail,
        # advantage — aligned 1:1 with candidate order) and the loss-reduction
        # documentation ride in step_ctx so every emit path (skipped + updated)
        # carries them.
        rollout_rewards = build_rollout_rewards(
            evaluations,
            advantages,
            completion_token_lengths=generation_diagnostics["completion_token_lengths"],
            # 2026-08-26 (r18): the per-candidate record carries every
            # advantage term — the shared-MAD scale actually applied and the
            # per-candidate stop reason (eos/fence/truncated/...) aligned 1:1.
            adv_scale=advantage_scale,
            stop_reasons=per_candidate_stop_reasons(generation_diagnostics),
        )
        step_ctx: dict[str, Any] = {
            "step": step,
            "task_name": task["task_id"],
            "domain": task["meta"].get("domain", "?"),
            "mean_reward": float(mean_reward),
            "mean_shaped_reward": float(shaped_rewards.mean()),
            "signal_stats": signal_stats,
            "rollout_rewards": rollout_rewards,
            "loss_reduction": LOSS_REDUCTION_STRINGS[args.loss_mode],
            "pass_rate": pass_rate,
            "syntax_rate": float(syntax_rewards.mean()),
            "interface_rate": float(interface_rewards.mean()),
            "verifier_rate": float(verifier_rewards.mean()),
            "task_prob": float(task_prob),
            "task_state": task_state,
            "advantage_scale": advantage_scale,
            "loo_advantage_rms": loo_advantage_rms,
            "loo_advantage_mean_abs": loo_advantage_mean_abs,
            "advantage_dispersion": candidate_advantage_dispersion(advantages),
            "update_signal_magnitude": update_signal_magnitude,
            "update_signal_kind": update_signal_kind,
            "update_signal_threshold": float(args.min_reward_std),
            "adapter_init": args.adapter_init,
            "route": route,
            "entropy_mean": entropy_mean,
            "generation_tokens": generation_tokens,
            "repair_queued": repair_queued,
            "all_fail": all_fail,
            # 2026-08-26 (r10) + 2026-08-27 (T1a): collapse-rescue alarm and
            # quarantine-integrity gate (both computed BEFORE the probe so
            # repair-routing is suppressed on evidence-free collapsed
            # rollouts).
            "degenerate_policy_alarm": degenerate_alarm,
            "quarantine_suppressed": quarantine_suppressed,
            "frontier_fraction": frontier_fraction,
            "model_dim_scores": model_dim_means or None,
            "model_judge_enabled": judge_enabled or None,
            "posterior_lower": probe.get("posterior_lower"),
            "posterior_upper": probe.get("posterior_upper"),
            "flaky": bool(probe.get("flaky")),
            "group_size": effective_g,
            "greedy_count": greedy_rollout_count(
                effective_g,
                float(getattr(args, "greedy_rollout_fraction", 0.0) or 0.0),
            ),
            "mean_response_length": mean_response_length,
            "truncation_rate": truncation_rate,
            "eos_termination_rate": generation_diagnostics["eos_termination_rate"],
            "fence_termination_rate": generation_diagnostics["fence_termination_rate"],
            "cap_run_with_fence_opener_rate": generation_diagnostics[
                "cap_run_with_fence_opener_rate"
            ],
            "completion_token_lengths": generation_diagnostics["completion_token_lengths"],
            "raw_response_chars": generation_diagnostics["raw_response_chars"],
            "extracted_code_chars": generation_diagnostics["extracted_code_chars"],
            "generation_token_budget": generation_token_budget,
            "teacher_free_self_repair": self_repair_summary,
        }

        # Guardian alarm 8: per-step sidecar liveness. Cheap (pidfile stat +
        # kill-0 + log mtime). Alarm loudly on state change and every 30th
        # step while dead; record the flag in the step record so the death is
        # never silent again (step-record flag + log line).
        _sidecar = check_sidecar_liveness(
            sidecar_pidfile,
            sidecar_log,
            max_log_age_seconds=args.repair_sidecar_max_log_age,
        )
        step_ctx["sidecar_alive"] = _sidecar["alive"]
        step_ctx["sidecar_relaunch_attempted"] = _maybe_repair_sidecar_relaunch(
            _sidecar, sidecar_alarm_state, output_dir
        )
        if _sidecar["alarm"]:
            sidecar_alarm_state["alarm_count"] += 1
            state_changed = sidecar_alarm_state["was_alive"] is not False
            sidecar_alarm_state["was_alive"] = False
            if state_changed or sidecar_alarm_state["alarm_count"] % 30 == 0:
                print(alarm_line(_sidecar), flush=True)
                print(
                    f"[{ALARM_MARKER}] relaunch via: "
                    f"bash scripts/sapo_ensure_repair_sidecar.sh {output_dir}",
                    flush=True,
                )
        else:
            if sidecar_alarm_state["was_alive"] is False:
                print(
                    f"[SIDECAR_RECOVERED] repair sidecar alive again: pid={_sidecar.get('pid')}",
                    flush=True,
                )
            sidecar_alarm_state["was_alive"] = True

        # T1a (2026-08-27): a collapsed policy must NEVER produce evidence-free
        # quarantines — suppress the flat-all-fail repair-queue gate; the task
        # stays in the RL targeted pool under the escalated temp ladder
        # (degenerate_alarm/quarantine_suppressed computed before the probe).
        if (
            should_queue_flat_all_fail(
                all_fail=all_fail,
                route=route,
                update_signal_magnitude=update_signal_magnitude,
                threshold=args.min_reward_std,
            )
            and not quarantine_suppressed
        ):
            # A fresh-task posterior can initially call this frontier RL even
            # though its final LOO advantages are exactly zero. Quarantine it
            # immediately: persist the best failure for verified repair and
            # give it zero future sampling mass instead of spending two more
            # groups waiting for the posterior bound to tighten.
            router.mark_repair(task["task_id"])
            route = REPAIR_SFT
            step_ctx["route"] = route

        # ── Route the group ──
        # All-fail groups with no shaped variation are NOT RL batches: they go to
        # the execution-verified repair lane (repair SFT/DPO queue) instead.
        if route in (REPAIR_SFT, INVALID_OR_NOISY):
            # 2026-08-26 (r10): low-entropy all-fail groups escalate BEFORE
            # repair-routing swallows them (cold-collapse class; the alarm
            # already escalated this step, so do not double-count).
            if route == REPAIR_SFT and not step_ctx.get("degenerate_policy_alarm"):
                escalate_temperature_on_flat_route(
                    adaptive_temp,
                    route=route,
                    all_fail=all_fail,
                    entropy_mean=entropy_mean,
                )
            if route == REPAIR_SFT:
                best_index = max(
                    range(len(evaluations)),
                    key=lambda idx: (
                        float(evaluations[idx].get("verifier_reward", 0.0)),
                        float(evaluations[idx].get("total_reward", 0.0)),
                    ),
                )
                best = evaluations[best_index]
                failures = [str(detail) for detail in (best.get("details") or [])]
                append_repair_queue_record(
                    repair_queue_path,
                    {
                        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                        "step": step,
                        "task_id": task["task_id"],
                        "domain": task["meta"].get("domain", "?"),
                        "category": task["meta"].get("category", "?"),
                        "best_code": codes[best_index],
                        "failures": failures[:8],
                        "pass_rate": pass_rate,
                        "verifier_rate": float(verifier_rewards[best_index].item()),
                    },
                )
                repair_queued = True
                step_ctx["repair_queued"] = True
                # 2026-08-25: this skip is emitted with reason=repair_sft_queued
                # and is a ROUTING decision (task -> repair SFT lane), not a
                # low-signal outcome — it must NOT escalate temperature. The
                # 2026-08-24 escalation here is what ramped run-3 to 1.75 and
                # drove the step-42 entropy-explosion death spiral.
            trips = observe_and_evaluate_breakers(
                breaker,
                step=step,
                route=route,
                non_finite=False,
                clip_fraction=0.0,
                entropy_mean=entropy_mean,
                repair_queued=repair_queued,
                repair_converted_jsonl=args.repair_converted_jsonl,
                all_fail=all_fail,
                completion_token_lengths=generation_diagnostics["completion_token_lengths"],
                eos_termination_rate=generation_diagnostics["eos_termination_rate"],
                truncation_rate=generation_diagnostics.get("truncation_rate"),
                fence_termination_rate=generation_diagnostics.get("fence_termination_rate"),
            )
            emit_step_record(
                rank=rank,
                metrics=metrics,
                step_metrics_path=step_metrics_path,
                log_steps=args.log_steps,
                ctx=step_ctx,
                skipped=True,
                reason=f"{route}_queued",
                trips=trips,
            )
            _persist_resume_state(step)
            if maybe_stop_for_breaker(breaker, args, rank, trips):
                break
            continue

        # Skip flat mastered groups: keep a small replay quota but do not burn
        # an optimizer step on a group whose leave-one-out advantages are ~0.
        if route == MASTERED_REPLAY and update_signal_magnitude < args.min_reward_std:
            trips = observe_and_evaluate_breakers(
                breaker,
                step=step,
                route=route,
                non_finite=False,
                clip_fraction=0.0,
                entropy_mean=entropy_mean,
                repair_queued=repair_queued,
                repair_converted_jsonl=args.repair_converted_jsonl,
                all_fail=all_fail,
                completion_token_lengths=generation_diagnostics["completion_token_lengths"],
                eos_termination_rate=generation_diagnostics["eos_termination_rate"],
                truncation_rate=generation_diagnostics.get("truncation_rate"),
                fence_termination_rate=generation_diagnostics.get("fence_termination_rate"),
            )
            emit_step_record(
                rank=rank,
                metrics=metrics,
                step_metrics_path=step_metrics_path,
                log_steps=args.log_steps,
                ctx=step_ctx,
                skipped=True,
                reason="mastered_replay_flat",
                trips=trips,
            )
            _persist_resume_state(step)
            if maybe_stop_for_breaker(breaker, args, rank, trips):
                break
            continue

        # Skip only when both total and component reward signals are flat on an
        # RL route (adaptive temperature escalation applies here).
        if route in RL_ROUTES and update_signal_magnitude < args.min_reward_std:
            # T1a: a collapse-suppressed step lands here (route kept frontier);
            # the r10 alarm already escalated on its crossing step — do not
            # double-count the ladder on that step.
            if not step_ctx.get("degenerate_policy_alarm"):
                adaptive_temp.record_skip("low_reward_signal")
            trips = observe_and_evaluate_breakers(
                breaker,
                step=step,
                route=route,
                non_finite=False,
                clip_fraction=0.0,
                entropy_mean=entropy_mean,
                repair_queued=repair_queued,
                repair_converted_jsonl=args.repair_converted_jsonl,
                all_fail=all_fail,
                completion_token_lengths=generation_diagnostics["completion_token_lengths"],
                eos_termination_rate=generation_diagnostics["eos_termination_rate"],
                truncation_rate=generation_diagnostics.get("truncation_rate"),
                fence_termination_rate=generation_diagnostics.get("fence_termination_rate"),
            )
            emit_step_record(
                rank=rank,
                metrics=metrics,
                step_metrics_path=step_metrics_path,
                log_steps=args.log_steps,
                ctx=step_ctx,
                skipped=True,
                reason="low_reward_signal",
                trips=trips,
            )
            _persist_resume_state(step)
            if maybe_stop_for_breaker(breaker, args, rank, trips):
                break
            continue

        # Forward pass to get current completion-only log probs and apply GRPO loss.
        #
        # Run `inner_epochs` optimizer steps per rollout group. One epoch is a
        # valid on-policy update: although the ratio starts at 1, its SAPO/GRPO
        # derivative with respect to current log-probability is nonzero. Extra
        # epochs trade more rollout reuse for additional costly forwards.
        inner_epochs = max(1, int(getattr(args, "inner_epochs", 2)))
        # 2026-08-25 OOM fix (run-4): cap the TRAIN pass (current-policy)
        # sequence length so max-length completions cannot blow the
        # grad-enabled forward's activation peak; rollout/eval stay full.
        train_pass_seq_cap: int | None = (
            int(args.train_pass_max_seq_length)
            if getattr(args, "train_pass_max_seq_length", 0)
            and int(args.train_pass_max_seq_length) > 0
            else None
        )
        effective_kl = args.kl_coeff
        length_weights: torch.Tensor | None = None
        last_loss = None
        last_gspo_stats: dict[str, float] | None = None
        last_normalized_old_log_probs: list[torch.Tensor] | None = None
        last_sapo_candidate_stats: list[dict[str, float]] | None = None
        last_sapo_per_candidate_losses: list[dict[str, Any]] | None = None
        last_sapo_loss_breakdown: dict[str, Any] | None = None
        last_dr_pair_info: dict[str, Any] | None = None
        last_dr_variance_info: dict[str, Any] | None = None
        gradient_norms: list[float] = []
        completed_inner_epochs = 0
        inner_skip_reason: str | None = None
        inner_early_stop_reason: str | None = None
        saved_params: list[torch.Tensor] | None = None
        saved_optim: dict | None = None
        if args.trust_region_enabled:
            saved_params = [p.detach().clone() for p in trainable_param_tensors]
            saved_optim = optimizer.state_dict()
        for inner_epoch in range(inner_epochs):
            active_model.train()
            epoch_sapo_candidate_stats: list[dict[str, float]] | None = None
            epoch_per_candidate_losses: list[dict[str, Any]] | None = None
            sapo_loss_breakdown: dict[str, Any] | None = None
            current_log_probs = []
            normalized_old_log_probs = []
            filtered_advantages = []
            filtered_token_counts = []
            current_token_lps: list[torch.Tensor] | None = [] if args.loss_mode == "sapo" else None
            filtered_old_token_lps: list[torch.Tensor] | None = (
                [] if args.loss_mode == "sapo" else None
            )
            # 2026-08-26 (r10, entropy floor): current-policy per-candidate
            # entropy means over the train-pass completion tokens — the
            # monitoring signal the (detached, run-10 fix) penalty reads —
            # differentiable signal the entropy-floor penalty is computed on.
            entropy_floor_weight = float(getattr(args, "entropy_floor_weight", 0.0) or 0.0)
            entropy_floor_active = entropy_floor_weight > 0.0
            current_entropies: list[torch.Tensor] = []
            # Candidate indices that actually entered the loss (zero-token
            # completions are skipped below; the instrumentation must still
            # mark them explicitly in the record).
            loss_candidate_indices: list[int] = []
            train_pass_truncated = 0
            for idx, raw_response in enumerate(raw_responses):
                call_kwargs = dict(add_mm_token_type_ids=_needs_mm_token_type_ids)
                # The rollout distribution includes adaptive temperature. Apply
                # the same transform to both old and current policy logits so
                # the synchronous first-epoch ratio remains exactly on-policy.
                call_kwargs["policy_temperature"] = effective_temperature
                # 2026-08-26 (run-9 backward-OOM fix): chunk-streaming
                # recompute backward for the chunked-vocab pass (default ON;
                # --no-chunked-recompute-backward for ablations).
                call_kwargs["recompute_backward"] = bool(
                    getattr(args, "chunked_recompute_backward", True)
                )
                # 2026-08-25 OOM fix (run-4): the TRAIN pass only computes the
                # current-policy log-probs on at most the first N tokens of
                # each candidate (rollout log-probs/eval/reward stay full).
                # The grad-enabled full-seq forward of 4x2048-token
                # completions blew the lm_head card's activation peak.
                if train_pass_seq_cap is not None:
                    call_kwargs["train_seq_cap"] = train_pass_seq_cap
                if entropy_floor_active:
                    call_kwargs["return_entropy"] = True
                    # 2026-08-26 (run-8 OOM fix): the train pass's entropy
                    # (the differentiable floor signal) is the mean over the
                    # first --entropy-token-cap completion tokens — the
                    # full-sequence entropy branch was the 59.8 GiB peak.
                    call_kwargs["entropy_token_cap"] = int(getattr(args, "entropy_token_cap", 256))
                if current_token_lps is not None:
                    call_kwargs["return_token_log_probs"] = True
                result = compute_completion_log_prob(
                    active_model,
                    tokenizer,
                    prompt_text,
                    raw_response,
                    device,
                    args.max_seq_length,
                    args.logit_clip,
                    prompt_token_ids=rollout_prompt_token_ids,
                    prompt_attention_mask=rollout_prompt_attention_mask,
                    completion_token_ids=rollout_completion_token_ids[idx],
                    **call_kwargs,
                )
                if entropy_floor_active and current_token_lps is not None:
                    current_log_prob, token_count, cur_entropy, cur_tokens = result
                elif entropy_floor_active:
                    current_log_prob, token_count, cur_entropy = result
                elif current_token_lps is not None:
                    current_log_prob, token_count, cur_tokens = result
                else:
                    current_log_prob, token_count = result
                # Release the allocator cache between per-completion forwards:
                # p16 hung right here (group-8 train-logprob, 8 grad-enabled
                # forwards with full-vocab logits) after 41 min of silence.
                _release_device_cache(torch)
                if token_count.item() == 0:
                    continue
                # 2026-08-26 (r10, entropy floor): collect the entropy ONLY
                # for accepted (non-zero-token) candidates — the same set the
                # loss/lps lists use, so the penalty's candidate alignment is
                # exact.
                if entropy_floor_active:
                    current_entropies.append(cur_entropy)
                loss_candidate_indices.append(idx)
                # The train pass may keep fewer tokens than the rollout pass
                # (train-pass sequence cap). The per-token loss and the
                # sequence-KL must compare the SAME positions, so the old
                # (rollout) token lps and mean are aligned to the train-pass
                # token count. The kept tokens are the identical first-N
                # prefix (same prompt, same temperature), so this only drops
                # the completion tail from the update.
                n_train = int(token_count.item())
                n_old = int(old_token_counts[idx].item())
                if n_train < n_old:
                    train_pass_truncated += 1
                current_log_probs.append(current_log_prob / token_count.clamp_min(1))
                if n_train != n_old and filtered_old_token_lps is not None:
                    old_prefix = consistent_old_token_lps[idx][:n_train]
                    normalized_old_log_probs.append(
                        old_prefix.mean()
                        if n_train > 0
                        else old_log_probs[idx] / old_token_counts[idx].clamp_min(1)
                    )
                else:
                    normalized_old_log_probs.append(
                        old_log_probs[idx] / old_token_counts[idx].clamp_min(1)
                    )
                filtered_advantages.append(advantages[idx])
                # Length weights (gspo_ln) must reflect the tokens that
                # actually entered the update — the truncated count when the
                # train pass was capped, the full rollout count otherwise.
                if n_train != n_old:
                    filtered_token_counts.append(
                        torch.as_tensor(n_train, dtype=torch.float32, device=device)
                    )
                else:
                    filtered_token_counts.append(old_token_counts[idx].float())
                if current_token_lps is not None and filtered_old_token_lps is not None:
                    current_token_lps.append(cur_tokens)
                    filtered_old_token_lps.append(consistent_old_token_lps[idx][:n_train])

            if rank == 0:
                print(
                    json.dumps(
                        {
                            "stage": "train_logprob_done",
                            "step": step,
                            "inner_epoch": inner_epoch,
                            "n_current": len(current_log_probs),
                            "train_pass_max_seq_length": train_pass_seq_cap or 0,
                            "train_pass_truncated_candidates": train_pass_truncated,
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
            _release_device_cache(torch)
            # 2026-08-26 (r10, entropy floor): penalty on the mean
            # CURRENT-policy (train-pass) entropy below the floor —
            # preventive, engaged only below the floor, documented in
            # loss_breakdown.entropy_floor_penalty and honored by the
            # math-audit final-loss identity.
            # 2026-08-26 (run-10 double-backward fix): the penalty's VALUE is
            # computed on a DETACHED mean — a floor needs a mean-entropy
            # monitoring signal, not a graph edge. The r10 penalty-first
            # backward (penalty_tensor.backward()) backpropped through EVERY
            # candidate's chunked Function, freeing its saved tensors; the
            # SAPO per-candidate (loss_i * w_i).backward() then re-touched
            # the same graphs -> "Trying to backward through the graph a
            # second time" (grpo_utils.py:1647). The penalty now contributes
            # no gradient (the degenerate-policy alarm is the collapse
            # rescue); its value still rides the loss identity.
            entropy_train_mean: float | None = None
            entropy_floor_penalty_value = 0.0
            if entropy_floor_active and current_entropies:
                entropy_train_mean = float(torch.stack(current_entropies).mean().detach().item())
                entropy_floor_penalty_value = float(
                    compute_entropy_floor_penalty(
                        torch.stack(current_entropies).mean().detach(),
                        floor=float(getattr(args, "entropy_floor", 1.5)),
                        weight=entropy_floor_weight,
                    ).item()
                )
            if not current_log_probs:
                optimizer.zero_grad(set_to_none=True)
                if completed_inner_epochs > 0:
                    inner_early_stop_reason = "empty_completion_mask"
                    if rank == 0:
                        print(
                            json.dumps(
                                {
                                    "stage": "inner_epoch_early_stop",
                                    "step": step,
                                    "inner_epoch": inner_epoch,
                                    "reason": inner_early_stop_reason,
                                    "completed_inner_epochs": completed_inner_epochs,
                                },
                                ensure_ascii=False,
                            ),
                            flush=True,
                        )
                    break
                adaptive_temp.record_skip("empty_completion_mask")
                trips = observe_and_evaluate_breakers(
                    breaker,
                    step=step,
                    route=route,
                    non_finite=False,
                    clip_fraction=0.0,
                    entropy_mean=entropy_mean,
                    repair_queued=repair_queued,
                    repair_converted_jsonl=args.repair_converted_jsonl,
                    all_fail=all_fail,
                    completion_token_lengths=generation_diagnostics["completion_token_lengths"],
                    eos_termination_rate=generation_diagnostics["eos_termination_rate"],
                    truncation_rate=generation_diagnostics.get("truncation_rate"),
                    fence_termination_rate=generation_diagnostics.get("fence_termination_rate"),
                )
                emit_step_record(
                    rank=rank,
                    metrics=metrics,
                    step_metrics_path=step_metrics_path,
                    log_steps=args.log_steps,
                    ctx=step_ctx,
                    skipped=True,
                    reason="empty_completion_mask",
                    trips=trips,
                )
                _persist_resume_state(step)
                inner_skip_reason = "empty_completion_mask"
                if maybe_stop_for_breaker(breaker, args, rank, trips):
                    inner_skip_reason = "__BREAK__"
                break

            # Adaptive KL: measure the batch's sequence KL and adjust beta
            # before the loss so the penalty reflects current drift.
            if kl_state is not None:
                with torch.no_grad():
                    seq_kl_now = float(
                        old_sampled_kl(
                            torch.stack(current_log_probs),
                            torch.stack(normalized_old_log_probs),
                            numerical_log_ratio_clip=args.numerical_log_ratio_clip,
                        ).item()
                    )
                effective_kl = kl_state.update(seq_kl_now)

            # ── FV-GSPO: sequence-level clipped objective or legacy ablation ──
            gspo_stats: dict[str, float] | None = None
            if args.loss_mode == "gspo_ln":
                # LUSPO-style length neutralization: w_i = min(|y_i|/L_ref, w_max).
                counts = torch.stack(filtered_token_counts)
                length_weights = torch.clamp(
                    counts / max(args.ln_reference_length, 1.0), max=args.ln_max_weight
                )
            if args.loss_mode == "sapo":
                # SAPO (Soft Adaptive Policy Optimization, arXiv:2511.20347):
                # token-level ratios gated by a smooth sigmoid decay g(r) over
                # ALL tokens of each sample, with the sequence LOO advantage.
                # 2026-08-22: PER-CANDIDATE backward. SAPO's loss is
                # mean-over-tokens per candidate, then mean-over-candidates, so
                # each candidate has weight 1/G (not n_i/sum(n), which would
                # silently turn SAPO into length-biased BNPO). The forward loop
                # above still retains every candidate graph until this block;
                # backward is sequential, but this is not true one-graph
                # streaming. True streaming would require reordering the
                # batch-level adaptive-KL/DR computations or another forward.
                candidate_count = max(len(current_token_lps or []), 1)
                optimizer.zero_grad()
                # 2026-08-26 (run-10 double-backward fix): NO penalty
                # backward here. The r10 penalty-first backward consumed
                # every candidate's chunked-Function saved tensors, so the
                # per-candidate backwards below crashed with "Trying to
                # backward through the graph a second time". The penalty is
                # a detached monitoring value (see the entropy-floor block
                # above); each candidate's graph is backpropped exactly once.
                accumulated = None
                # Audit #3: the per-candidate backward loop used to overwrite
                # gspo_stats with the LAST candidate's stats, so the clip
                # fraction fed to the circuit breaker (and the step record)
                # reflected one candidate, not the batch. Accumulate the
                # token-weighted mean (each candidate's stats are means over
                # its n_i finite tokens) and emit the per-candidate list.
                gspo_stats = None
                per_candidate_stats: list[dict[str, float]] = []
                epoch_per_candidate_losses = []
                weighted_stat_sum: dict[str, float] = {}
                weighted_token_total = 0.0
                for ci in range(len(current_token_lps or [])):
                    loss_i, stats_i = sapo_loss_metrics(
                        [current_token_lps[ci]],
                        [filtered_old_token_lps[ci]],
                        filtered_advantages[ci].unsqueeze(0),
                        tau_pos=args.sapo_tau_pos,
                        tau_neg=args.sapo_tau_neg,
                        kl_coeff=effective_kl,
                        numerical_log_ratio_clip=args.numerical_log_ratio_clip,
                    )
                    n_i = float(stats_i.get("n_tokens", 0.0) or 0.0)
                    per_candidate_stats.append(
                        {k: float(v) for k, v in stats_i.items() if k != "n_tokens"}
                    )
                    w_i = 1.0 / candidate_count
                    (loss_i * w_i).backward()
                    if accumulated is None:
                        accumulated = loss_i.detach() * w_i
                    else:
                        accumulated = accumulated + loss_i.detach() * w_i
                    weighted_token_total += n_i
                    for k, v in stats_i.items():
                        if k == "n_tokens":
                            continue
                        weighted_stat_sum[k] = weighted_stat_sum.get(k, 0.0) + n_i * float(v)
                    # Training-log instrumentation (2026-08-25): every training
                    # loss value, per candidate, with its n_i token count, the
                    # weight w_i actually used for the backward, the advantage
                    # and the gate/KL stats — so the auditor can recompute
                    # loss_i = -gate_mean_i * A_i + kl_coeff * seq_kl_i.
                    candidate_index = (
                        int(loss_candidate_indices[ci]) if ci < len(loss_candidate_indices) else ci
                    )
                    epoch_per_candidate_losses.append(
                        {
                            "index": candidate_index,
                            "n_tokens": n_i,
                            "weight": w_i,
                            "loss": float(loss_i.detach().item()),
                            "advantage": float(filtered_advantages[ci].detach().item()),
                            "sapo_gate_mean": float(stats_i.get("sapo_gate_mean", 0.0) or 0.0),
                            "seq_kl": float(stats_i.get("seq_kl", 0.0) or 0.0),
                            "ratio_mean": float(stats_i.get("ratio_mean", 0.0) or 0.0),
                            "clip_total_fraction": float(
                                stats_i.get("clip_total_fraction", 0.0) or 0.0
                            ),
                        }
                    )
                total_loss = accumulated
                if entropy_floor_penalty_value > 0.0:
                    total_loss = total_loss + entropy_floor_penalty_value
                if weighted_token_total > 0.0 and weighted_stat_sum:
                    gspo_stats = {k: v / weighted_token_total for k, v in weighted_stat_sum.items()}
                elif per_candidate_stats:
                    # Fallback (no per-candidate token counts): plain mean.
                    gspo_stats = {
                        k: sum(float(s[k]) for s in per_candidate_stats) / len(per_candidate_stats)
                        for k in per_candidate_stats[0]
                    }
                epoch_sapo_candidate_stats = per_candidate_stats
                # Instrumentation: mark zero-token/empty candidates explicitly
                # (n_tokens=0, loss=None, excluded_reason) so the record covers
                # EVERY rollout candidate and the emit never crashes on them.
                included_indices = {int(entry["index"]) for entry in epoch_per_candidate_losses}
                for candidate_index in range(len(raw_responses)):
                    if candidate_index in included_indices:
                        continue
                    advantage_value: float | None = None
                    if candidate_index < int(advantages.numel()):
                        advantage_value = float(advantages[candidate_index].detach().item())
                    epoch_per_candidate_losses.append(
                        {
                            "index": candidate_index,
                            "n_tokens": 0,
                            "weight": None,
                            "loss": None,
                            "advantage": advantage_value,
                            "excluded_reason": "zero_token_completion",
                        }
                    )
                epoch_per_candidate_losses.sort(key=lambda entry: int(entry["index"]))
                # Machine-readable aggregate identity: the documented reduction
                # is Σ w_i·loss_i with w_i = 1/G (equal per-candidate weights,
                # length-neutral — NOT n_i/N token weighting). loss_recomputed
                # is exactly the value backpropped (pre-DR); the final `loss`
                # field and DR flags are merged in at the emit site.
                sapo_loss_breakdown = {
                    "loss_mode": args.loss_mode,
                    "loss_recomputed": float(accumulated.detach().item()),
                    "candidate_count": candidate_count,
                    "loss_candidate_count": sum(
                        1 for entry in epoch_per_candidate_losses if entry.get("loss") is not None
                    ),
                    "weighted_token_total": weighted_token_total,
                    "reduction": "per_candidate_1_over_g",
                    # 2026-08-25 OOM fix: document the train-pass sequence cap
                    # honestly (which candidates had their completion tail
                    # dropped from the update; rollout/eval stay full).
                    **train_pass_truncation_breakdown(
                        seq_cap=train_pass_seq_cap or 0,
                        n_truncated=train_pass_truncated,
                        n_total=len(raw_responses),
                    ),
                    # 2026-08-26 (r10, entropy floor): the final `loss` includes
                    # entropy_floor_penalty (weight*max(0, floor - mean
                    # current-policy train-pass entropy)) on top of
                    # loss_recomputed; the math auditor adds it back.
                    "entropy_floor_penalty": entropy_floor_penalty_value,
                    "entropy_train_mean": entropy_train_mean,
                    "entropy_floor": float(getattr(args, "entropy_floor", 1.5)),
                    "entropy_floor_weight": entropy_floor_weight,
                }
            elif args.loss_mode in ("gspo", "gspo_ln"):
                total_loss, gspo_stats = stable_gspo_loss_metrics(
                    torch.stack(current_log_probs),
                    torch.stack(normalized_old_log_probs),
                    torch.stack(filtered_advantages),
                    clip_low=args.gspo_clip_low,
                    clip_high=args.gspo_clip_high,
                    kl_coeff=effective_kl,
                    numerical_log_ratio_clip=args.numerical_log_ratio_clip,
                    length_weights=length_weights,
                )
            else:
                total_loss = grpo_loss(
                    torch.stack(current_log_probs),
                    torch.stack(normalized_old_log_probs),
                    torch.stack(filtered_advantages),
                    effective_kl,
                    args.ratio_clip_log_delta,
                )
            # Doubly-Robust DPO pair loss (no-op unless research method enabled).
            dr_pair_loss_term, dr_pair_info = compute_dr_pair_loss(
                research_methods=research_methods,
                rewards=rewards,
                codes=codes,
                current_log_probs=current_log_probs,
                old_log_probs=normalized_old_log_probs,
            )
            if torch.isfinite(dr_pair_loss_term) and float(dr_pair_loss_term.item()) != 0.0:
                total_loss = total_loss + dr_pair_loss_term
            # Doubly-Robust PPO-side variance correction (no-op unless enabled).
            dr_variance_term, dr_variance_info = compute_dr_variance_correction(
                research_methods=research_methods,
                log_probs=torch.stack(current_log_probs),
                old_log_probs=torch.stack(normalized_old_log_probs),
                advantages=torch.stack(filtered_advantages),
                ratio_clip_log_delta=args.ratio_clip_log_delta,
                current_step=step,
            )
            if torch.isfinite(dr_variance_term) and float(dr_variance_term.item()) != 0.0:
                total_loss = total_loss + dr_variance_term
            # 2026-08-26 (r10, entropy floor): the penalty value rides the
            # final loss and the identity; no gradient (run-10 fix).
            # 2026-08-26 (r15 F5 fix): the SAPO branch composes the penalty
            # into its own total_loss — this common tail must NOT re-add it
            # (loss == recomputed + 2*penalty broke the identity and would
            # false-alarm the math auditor exactly during collapse
            # episodes). Non-SAPO modes add it once here.
            total_loss = add_entropy_floor_penalty_value(
                total_loss, entropy_floor_penalty_value, loss_mode=args.loss_mode
            )
            if not torch.isfinite(total_loss):
                # SAPO may already have backpropped candidate losses. Never
                # leave non-finite/stale gradients live after abandoning an
                # inner epoch.
                optimizer.zero_grad(set_to_none=True)
                if completed_inner_epochs > 0:
                    inner_early_stop_reason = "non_finite_loss"
                    if rank == 0:
                        print(
                            json.dumps(
                                {
                                    "stage": "inner_epoch_early_stop",
                                    "step": step,
                                    "inner_epoch": inner_epoch,
                                    "reason": inner_early_stop_reason,
                                    "completed_inner_epochs": completed_inner_epochs,
                                },
                                ensure_ascii=False,
                            ),
                            flush=True,
                        )
                    break
                adaptive_temp.record_skip("non_finite_loss")
                trips = observe_and_evaluate_breakers(
                    breaker,
                    step=step,
                    route=route,
                    non_finite=True,
                    clip_fraction=0.0,
                    entropy_mean=entropy_mean,
                    repair_queued=repair_queued,
                    repair_converted_jsonl=args.repair_converted_jsonl,
                    all_fail=all_fail,
                    completion_token_lengths=generation_diagnostics["completion_token_lengths"],
                    eos_termination_rate=generation_diagnostics["eos_termination_rate"],
                    truncation_rate=generation_diagnostics.get("truncation_rate"),
                    fence_termination_rate=generation_diagnostics.get("fence_termination_rate"),
                )
                emit_step_record(
                    rank=rank,
                    metrics=metrics,
                    step_metrics_path=step_metrics_path,
                    log_steps=args.log_steps,
                    ctx=step_ctx,
                    skipped=True,
                    reason="non_finite_loss",
                    trips=trips,
                )
                _persist_resume_state(step)
                inner_skip_reason = "non_finite_loss"
                if maybe_stop_for_breaker(breaker, args, rank, trips):
                    inner_skip_reason = "__BREAK__"
                break
            # SAPO already zeroed + backpropped per candidate in the loss block.
            if args.loss_mode != "sapo":
                optimizer.zero_grad()
                total_loss.backward()
            grad_norm_tensor = torch.nn.utils.clip_grad_norm_(trainable_param_tensors, 1.0)
            grad_norm = float(grad_norm_tensor.detach().item())
            if not math.isfinite(grad_norm):
                # clip_grad_norm_ reports the pre-clip total norm. A NaN/Inf
                # norm means the gradients themselves cannot be made safe by
                # clipping; stepping AdamW here would poison parameters/state.
                optimizer.zero_grad(set_to_none=True)
                if completed_inner_epochs > 0:
                    inner_early_stop_reason = "non_finite_gradient"
                    if rank == 0:
                        print(
                            json.dumps(
                                {
                                    "stage": "inner_epoch_early_stop",
                                    "step": step,
                                    "inner_epoch": inner_epoch,
                                    "reason": inner_early_stop_reason,
                                    "completed_inner_epochs": completed_inner_epochs,
                                },
                                ensure_ascii=False,
                            ),
                            flush=True,
                        )
                    break
                adaptive_temp.record_skip("non_finite_gradient")
                trips = observe_and_evaluate_breakers(
                    breaker,
                    step=step,
                    route=route,
                    non_finite=True,
                    clip_fraction=0.0,
                    entropy_mean=entropy_mean,
                    repair_queued=repair_queued,
                    repair_converted_jsonl=args.repair_converted_jsonl,
                    all_fail=all_fail,
                    completion_token_lengths=generation_diagnostics["completion_token_lengths"],
                    eos_termination_rate=generation_diagnostics["eos_termination_rate"],
                    truncation_rate=generation_diagnostics.get("truncation_rate"),
                    fence_termination_rate=generation_diagnostics.get("fence_termination_rate"),
                )
                emit_step_record(
                    rank=rank,
                    metrics=metrics,
                    step_metrics_path=step_metrics_path,
                    log_steps=args.log_steps,
                    ctx=step_ctx,
                    skipped=True,
                    reason="non_finite_gradient",
                    trips=trips,
                )
                _persist_resume_state(step)
                inner_skip_reason = "non_finite_gradient"
                if maybe_stop_for_breaker(breaker, args, rank, trips):
                    inner_skip_reason = "__BREAK__"
                break
            gradient_norms.append(grad_norm)
            if rank == 0:
                print(
                    json.dumps(
                        {
                            "stage": "backward_done",
                            "step": step,
                            "inner_epoch": inner_epoch,
                            "loss": float(total_loss.detach().item()),
                            "gradient_norm": grad_norm,
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
            _release_device_cache(torch)
            optimizer.step()
            completed_inner_epochs += 1
            last_loss = total_loss.detach().clone()
            last_gspo_stats = gspo_stats
            last_normalized_old_log_probs = [value.detach() for value in normalized_old_log_probs]
            last_sapo_candidate_stats = epoch_sapo_candidate_stats
            last_sapo_per_candidate_losses = epoch_per_candidate_losses
            last_sapo_loss_breakdown = sapo_loss_breakdown
            last_dr_pair_info = dr_pair_info
            last_dr_variance_info = dr_variance_info

        # Handle early-exit from the inner loop (empty mask / non-finite loss).
        if inner_skip_reason == "__BREAK__":
            break
        if inner_skip_reason is not None:
            continue
        total_loss = last_loss
        gspo_stats = last_gspo_stats
        sapo_candidate_stats = last_sapo_candidate_stats
        dr_pair_info = last_dr_pair_info
        dr_variance_info = last_dr_variance_info
        adaptive_temp.record_update()
        router.record_rl_update(task["task_id"])
        # 2026-08-24 (algorithm analyst): an all-fail group that still fired a
        # real update from a confident-but-wrong single mode (low entropy —
        # the cold-task class of steps 6/7 in sapo-27b-ai-20260824T031524)
        # should make the NEXT group sample at elevated temperature.
        # record_update() above just reset the counter, so escalate AFTER it.
        escalate_temperature_on_flat_route(
            adaptive_temp,
            route=route,
            all_fail=all_fail,
            entropy_mean=entropy_mean,
        )

        trust_region_violated = False
        ratio_after_update = 0.0
        clip_fraction_after_update = 0.0
        seq_kl_after = 0.0
        # B-224 instrumenter: persisted per-candidate post-vs-old data (empty
        # when trust region is disabled / no candidates entered the check).
        trust_region_per_candidate_rows: list[dict[str, Any]] | None = None
        if args.trust_region_enabled and saved_params is not None and last_normalized_old_log_probs:
            active_model.eval()
            with torch.no_grad():
                post_log_probs: list[torch.Tensor] = []
                # B-224 instrumenter (2026-09-14, tick #456 ADDENDUM 2): the
                # post-update probe was observed to disagree with the in-train
                # per-candidate seq_kl by ~250x on the SAME prefix, but the
                # per-candidate post values were locals and never persisted, so
                # no banked step was diagnosable. Persist the per-candidate
                # post-vs-old data in the step record (default ON) so the next
                # violating step can be diffed numerically.
                trust_per_candidate_rows: list[dict[str, Any]] = []
                for idx, (raw_response, completion_ids) in enumerate(
                    _strict_zip(raw_responses, rollout_completion_token_ids)
                ):
                    post_log_prob, post_token_count = compute_completion_log_prob(
                        active_model,
                        tokenizer,
                        prompt_text,
                        raw_response,
                        device,
                        args.max_seq_length,
                        args.logit_clip,
                        add_mm_token_type_ids=_needs_mm_token_type_ids,
                        policy_temperature=effective_temperature,
                        prompt_token_ids=rollout_prompt_token_ids,
                        prompt_attention_mask=rollout_prompt_attention_mask,
                        completion_token_ids=completion_ids,
                        # B-212 (2026-09-14): the train pass caps the sequence at
                        # train_pass_max_seq_length (the 2026-08-25 OOM fix), and the
                        # baseline this block differences against
                        # (last_normalized_old_log_probs) is aligned to that kept
                        # PREFIX. Without the same cap here this pass means over a
                        # different token set, so a train-pass-truncated candidate
                        # reports a spurious violation and scale_lr halves the LR on
                        # an unchanged policy (measured live: 2.5e-05 -> 1.25e-05 ->
                        # 6.25e-06 across two false violations).
                        train_seq_cap=train_pass_seq_cap,
                    )
                    if post_token_count.item() > 0:
                        post_mean = post_log_prob / post_token_count.clamp_min(1)
                        post_log_probs.append(post_mean)
                        per_candidate_row: dict[str, Any] = {
                            "idx": idx,
                            "old_token_count": int(old_token_counts[idx].item()),
                            "post_token_count": int(post_token_count.item()),
                            "old_mean": float(
                                (old_log_probs[idx] / old_token_counts[idx].clamp_min(1)).item()
                            ),
                            "post_mean": float(post_mean.item()),
                            "delta": float(
                                (
                                    post_mean
                                    - old_log_probs[idx] / old_token_counts[idx].clamp_min(1)
                                ).item()
                            ),
                        }
                        trust_per_candidate_rows.append(per_candidate_row)
            trust_region_per_candidate_rows = trust_per_candidate_rows
            if post_log_probs:
                # B-224 (count-mismatch refuted, bugqueue ADDENDUM 2): the old
                # side stays last_normalized_old_log_probs (aligned prefix for
                # SAPO via B-212; full mean otherwise) exactly as the B-212
                # behavior — do NOT change the basis on a refuted hypothesis.
                trust_stats = sequence_ratio_stats(
                    torch.stack(post_log_probs),
                    torch.stack(last_normalized_old_log_probs),
                    clip_low=args.gspo_clip_low,
                    clip_high=args.gspo_clip_high,
                    numerical_log_ratio_clip=args.numerical_log_ratio_clip,
                )
                ratio_after_update = trust_stats["ratio_after_update"]
                clip_fraction_after_update = trust_stats["clip_fraction_after_update"]
                seq_kl_after = trust_stats["seq_kl_after"]
                trust_region_violated = (
                    seq_kl_after > args.trust_region_max_seq_kl
                    or clip_fraction_after_update > args.trust_region_max_clip_fraction
                )
                if trust_region_violated:
                    trust_region_violation_count += 1
                    lr_before = float(optimizer.param_groups[0]["lr"])
                    lr_after = lr_before
                    if args.trust_region_on_violation == "reject":
                        for param, saved in _strict_zip(trainable_param_tensors, saved_params):
                            param.data.copy_(saved)
                        optimizer.load_state_dict(saved_optim)
                    else:  # scale_lr
                        lr_before, lr_after = scale_optimizer_lr(
                            optimizer,
                            factor=0.5,
                            min_lr=args.trust_region_min_lr,
                        )
                    if rank == 0:
                        # Audit #2: scale_lr halved the LR in place with no log
                        # line and no record field — 10 violations silently took
                        # the LR from 2e-5 to ~2e-8.
                        # B-224 instrumenter: per-candidate post-vs-old data was
                        # a local and never persisted, so no banked step was
                        # diagnosable (bugqueue ADDENDUM 2). Persist it: default
                        # it rides the step record; when --trust-region-dump is
                        # set also append the raw per-candidate rows to
                        # trust_region_dump.jsonl for numeric diffing.
                        if getattr(args, "trust_region_dump", False):
                            try:
                                dump_path = output_dir / "trust_region_dump.jsonl"
                                with open(dump_path, "a", encoding="utf-8") as _df:
                                    _df.write(
                                        json.dumps(
                                            {
                                                "step": step,
                                                "rows": trust_per_candidate_rows,
                                            },
                                            ensure_ascii=False,
                                        )
                                        + "\n"
                                    )
                            except Exception as _e:  # never let instrumentation kill the run
                                print(
                                    json.dumps(
                                        {
                                            "stage": "trust_region_dump_error",
                                            "step": step,
                                            "error": str(_e),
                                        }
                                    ),
                                    flush=True,
                                )
                        print(
                            json.dumps(
                                {
                                    "stage": "trust_region_violation",
                                    "step": step,
                                    "mode": args.trust_region_on_violation,
                                    "lr_before": lr_before,
                                    "lr_after": lr_after,
                                    "count": trust_region_violation_count,
                                    "seq_kl_after": seq_kl_after,
                                    "clip_fraction_after_update": clip_fraction_after_update,
                                    "n_compared": len(trust_per_candidate_rows),
                                },
                                ensure_ascii=False,
                            ),
                            flush=True,
                        )

        # B-224 guard (2026-09-14): a sustained false-violation loop silently
        # halves the LR on every violation (measured live 2.5e-05 -> 1.5625e-06,
        # 1/16, over ~12 steps with no monitor-side stop). Once the cumulative
        # violation count reaches --trust-region-max-violations, fire a
        # recommend-stop alarm so the run surfaces for diagnosis instead of
        # draining to an inert LR.
        trust_region_max_violations = int(getattr(args, "trust_region_max_violations", 6))
        trust_region_bleed_alarm = bool(
            trust_region_violation_count > 0
            and trust_region_max_violations > 0
            and trust_region_violation_count >= trust_region_max_violations
        )
        if trust_region_bleed_alarm and rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "trust_region_bleed_alarm",
                        "step": step,
                        "recommend_stop": True,
                        "count": trust_region_violation_count,
                        "lr": float(optimizer.param_groups[0]["lr"]),
                        "max_violations": trust_region_max_violations,
                        "message": (
                            "trust-region violation count hit "
                            f"{trust_region_violation_count} >= {trust_region_max_violations}; "
                            "LR is bleeding. Halt + diagnose (check for spurious "
                            "post-update KL / token-set mismatch), do not keep "
                            "halving."
                        ),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )

        clip_fraction = (
            float(gspo_stats.get("clip_total_fraction", 0.0)) if gspo_stats is not None else 0.0
        )
        # Zero-change gate (2026-08-25 manager directive): after this step's
        # optimizer step(s), max|Δ lora_B| vs the pre-training snapshot must be
        # > 0. An EXACT zero means the adapter is byte-identical to base/init —
        # the unforgivable 0-change case — and fires the alarm + recommend-stop
        # marker. Measured here (post optimizer.step and post trust-region
        # handling) so the record reflects the step's final parameter state.
        params_by_name = dict(_strict_zip(trainable_param_names, trainable_param_tensors))
        lora_b_max_delta = measure_lora_b_max_delta(lora_b_init_snapshot, params_by_name)
        zero_change_alarm = zero_change_gate_fired(lora_b_max_delta)
        if zero_change_alarm and rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "zero_change_alarm",
                        "step": step,
                        "lora_b_max_delta": lora_b_max_delta,
                        "recommend_stop": True,
                        "message": (
                            "lora_B unchanged vs init (max|Δlora_B| == 0.0 exactly) "
                            "after optimizer step — adapter is byte-identical to "
                            "base; 0-change adapter is unacceptable"
                        ),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
        # Instrumentation: the aggregate loss identity with the final loss value
        # (post DR pair/variance terms, if any) merged in for the record.
        if args.loss_mode == "sapo" and last_sapo_loss_breakdown is not None:
            loss_breakdown = dict(last_sapo_loss_breakdown)
            loss_breakdown["loss"] = float(total_loss.item())
            loss_breakdown["dr_pair_loss_added"] = bool(
                dr_pair_info and dr_pair_info.get("dr_pair_mined")
            )
            loss_breakdown["dr_variance_correction_added"] = bool(
                dr_variance_info
                and float(dr_variance_info.get("dr_variance_correction_value", 0.0)) != 0.0
            )
        else:
            loss_breakdown = {
                "loss_mode": args.loss_mode,
                "loss": float(total_loss.item()),
                "loss_recomputed": None,
                "reduction": "batched",
                # 2026-08-26 (r10, entropy floor): documented for every loss
                # mode (the penalty is 0 when the weight is 0 or above floor).
                "entropy_floor_penalty": entropy_floor_penalty_value,
                "entropy_train_mean": entropy_train_mean,
                "entropy_floor": float(getattr(args, "entropy_floor", 1.5)),
                "entropy_floor_weight": entropy_floor_weight,
            }
        trips = observe_and_evaluate_breakers(
            breaker,
            step=step,
            route=route,
            non_finite=inner_early_stop_reason in {"non_finite_loss", "non_finite_gradient"},
            clip_fraction=clip_fraction,
            entropy_mean=entropy_mean,
            repair_queued=repair_queued,
            repair_converted_jsonl=args.repair_converted_jsonl,
            all_fail=all_fail,
            completion_token_lengths=generation_diagnostics["completion_token_lengths"],
            eos_termination_rate=generation_diagnostics["eos_termination_rate"],
            truncation_rate=generation_diagnostics.get("truncation_rate"),
            fence_termination_rate=generation_diagnostics.get("fence_termination_rate"),
        )
        # Audit #1: mean_response_length/truncation_rate (and the trust-region
        # fields below) used to be mutated into the returned record AFTER
        # emit_step_record had already appended the JSONL + log print — they
        # never landed in grpo_step_metrics.jsonl. All derived fields are now
        # passed into the record builder so they persist.
        emit_step_record(
            rank=rank,
            metrics=metrics,
            step_metrics_path=step_metrics_path,
            log_steps=args.log_steps,
            ctx=step_ctx,
            skipped=False,
            loss=float(total_loss.item()),
            trips=trips,
            ratio_mean=float(gspo_stats.get("ratio_mean", 0.0)) if gspo_stats is not None else None,
            clip_low_fraction=float(gspo_stats.get("clip_low_fraction", 0.0))
            if gspo_stats is not None
            else None,
            clip_high_fraction=float(gspo_stats.get("clip_high_fraction", 0.0))
            if gspo_stats is not None
            else None,
            seq_kl=float(gspo_stats.get("seq_kl", 0.0)) if gspo_stats is not None else None,
            self_eval_rate=float(self_eval_rewards.mean())
            if args.self_evaluation_enabled
            else None,
            trust_region_violated=bool(trust_region_violated),
            lr=float(optimizer.param_groups[0]["lr"]),
            trust_region_violation_count=trust_region_violation_count,
            ratio_after_update=ratio_after_update,
            clip_fraction_after_update=clip_fraction_after_update,
            seq_kl_after=seq_kl_after,
            old_policy_age=1,
            optimizer_substeps_per_rollout=completed_inner_epochs,
            gradient_norms=gradient_norms,
            inner_early_stop_reason=inner_early_stop_reason,
            sapo_per_candidate_stats=sapo_candidate_stats,
            per_candidate_losses=(
                last_sapo_per_candidate_losses if args.loss_mode == "sapo" else []
            ),
            loss_breakdown=loss_breakdown,
            lora_b_max_delta=lora_b_max_delta,
            zero_change_alarm=zero_change_alarm,
            zero_change_recommend_stop=zero_change_alarm,
            trust_region_bleed_alarm=trust_region_bleed_alarm,
            trust_region_per_candidate=trust_region_per_candidate_rows,
            kl_beta=float(kl_state.beta) if kl_state is not None else None,
            dr_pair_mined=bool(dr_pair_info.get("dr_pair_mined")) if dr_pair_info else None,
            dr_pair_reward_gap=float(dr_pair_info.get("dr_pair_reward_gap", 0.0))
            if dr_pair_info
            else None,
            dr_pair_loss_value=float(dr_pair_info.get("dr_pair_loss_value", 0.0))
            if dr_pair_info
            else None,
            dr_pair_loss_weight=float(dr_pair_info.get("dr_pair_loss_weight", 0.0))
            if dr_pair_info
            else None,
            dr_variance_correction_value=float(
                dr_variance_info.get("dr_variance_correction_value", 0.0)
            )
            if dr_variance_info
            else None,
            dr_psi=float(dr_variance_info.get("dr_psi", 0.0)) if dr_variance_info else None,
            dr_psi_init=float(dr_variance_info.get("dr_psi_init", 0.0))
            if dr_variance_info
            else None,
            dr_psi_warmup_steps=int(dr_variance_info.get("dr_psi_warmup_steps", 0))
            if dr_variance_info
            else None,
            dr_psi_current_step=dr_variance_info.get("dr_psi_current_step")
            if dr_variance_info
            else None,
        )
        _persist_resume_state(step)
        if maybe_stop_for_breaker(breaker, args, rank, trips):
            break
        # ── Periodic checkpoint: save adapter every checkpoint_interval_seconds ──
        # MUST be a sibling of the breaker-return (not nested under it, which
        # made this unreachable during normal training — the reason NO adapter
        # was ever written to disk despite steps completing).
        if args.checkpoint_interval_seconds > 0 and rank == 0:
            now = time.time()
            if now - _last_checkpoint_time >= args.checkpoint_interval_seconds:
                _last_checkpoint_time = now
                ckpt_dir = output_dir / f"step_{step:06d}_adapter"
                save_model = model.module if distributed else model
                save_peft_checkpoint_atomic(save_model, text_preprocessor, ckpt_dir)
                # Also update the main adapter dir (for sync daemon)
                main_adapter = output_dir / "adapter"
                save_model.save_pretrained(main_adapter)
                text_preprocessor.save_backend.save_pretrained(main_adapter)
                print(f"[checkpoint] saved adapter at step {step} to {ckpt_dir}")

        # ── Aggressive end-of-step memory cleanup (NPU-0 OOM mitigation) ──
        # Frees the step-local activations and recurrent-state tensors so the
        # next rollout does not accumulate memory across steps (the cause of
        # the repeated "NPU 0 out of memory / 60 GiB already allocated" crashes
        # with inner_epochs > 1). This runs every step, not just on checkpoint.
        if rank == 0:
            try:
                for _t in (
                    "current_log_probs",
                    "normalized_old_log_probs",
                    "filtered_advantages",
                    "filtered_token_counts",
                ):
                    if _t in dir():
                        obj = eval(_t)
                        if isinstance(obj, list):
                            obj.clear()
                if "total_loss" in dir():
                    dl = eval("total_loss")
                    del dl
            except Exception:
                pass
            _release_device_cache(torch)
            __import__("gc").collect()
            try:
                import torch as _torch

                for _bn in ("npu", "cuda"):
                    _be = getattr(_torch, _bn, None)
                    if _be is not None and hasattr(_be, "empty_cache"):
                        _be.empty_cache()
            except Exception:
                pass

    # Save final
    if rank == 0:
        save_model = model.module if distributed else model
        adapter_dir = output_dir / "adapter"
        save_model.save_pretrained(adapter_dir)
        text_preprocessor.save_backend.save_pretrained(adapter_dir)
        (output_dir / "grpo_metrics.json").write_text(
            json.dumps(build_grpo_metrics_payload(metrics, planned_steps=args.grpo_steps), indent=2)
            + "\n"
        )
        (output_dir / "run_config.json").write_text(
            json.dumps(
                {
                    "model_name": args.model_name,
                    "adapter_init": args.adapter_init,
                    "resume_from": args.resume_from,
                    "resume_state": getattr(args, "resume_state", None),
                    "resume_step": resume_step,
                    "tasks_dir": args.tasks_dir,
                    "benchmark_file": args.benchmark_file,
                    "domain_filter": args.domain_filter,
                    "group_size": args.group_size,
                    "max_adaptive_group": args.max_adaptive_group,
                    "grpo_steps": args.grpo_steps,
                    "inner_epochs": args.inner_epochs,
                    "lr": args.lr,
                    "kl_coeff": args.kl_coeff,
                    "temperature": args.temperature,
                    "adaptive_temp_step": args.adaptive_temp_step,
                    "adaptive_temp_max": args.adaptive_temp_max,
                    "adaptive_temp_state": adaptive_temp.to_dict(),
                    "max_new_tokens": args.max_new_tokens,
                    "max_seq_length": args.max_seq_length,
                    "checkpoint_interval_seconds": args.checkpoint_interval_seconds,
                    "npu_device_map": args.npu_device_map,
                    "npu_max_memory_gib": args.npu_max_memory_gib,
                    "visible_npus_env": os.environ.get("ASCEND_RT_VISIBLE_DEVICES")
                    or os.environ.get("ASCEND_VISIBLE_DEVICES"),
                    "device": str(args.device),
                    "reward_pass_weight": args.reward_pass_weight,
                    "reward_syntax_weight": args.reward_syntax_weight,
                    "reward_interface_weight": args.reward_interface_weight,
                    "reward_verifier_weight": args.reward_verifier_weight,
                    "reward_brevity_weight": args.reward_brevity_weight,
                    "brevity_target_lines": args.brevity_target_lines,
                    "reward_detail_budget_cap": args.reward_detail_budget_cap,
                    "advantage_clip": args.advantage_clip,
                    "ratio_clip_log_delta": args.ratio_clip_log_delta,
                    "top_p": args.top_p,
                    "logit_clip": args.logit_clip,
                    "min_reward_std": args.min_reward_std,
                    "curriculum_ema_decay": args.curriculum_ema_decay,
                    "curriculum_min_weight": args.curriculum_min_weight,
                    "curriculum_uncertainty_bonus": args.curriculum_uncertainty_bonus,
                    "quantum_priority": args.quantum_priority,
                    "loss_mode": args.loss_mode,
                    "sapo_tau_pos": args.sapo_tau_pos,
                    "sapo_tau_neg": args.sapo_tau_neg,
                    "lora_rank": args.lora_rank,
                    "lora_alpha": args.lora_alpha,
                    "gspo_clip_low": args.gspo_clip_low,
                    "gspo_clip_high": args.gspo_clip_high,
                    "numerical_log_ratio_clip": args.numerical_log_ratio_clip,
                    "ln_reference_length": args.ln_reference_length,
                    "ln_max_weight": args.ln_max_weight,
                    "advantage_mode": args.advantage_mode,
                    "loo_advantage_scale": args.loo_advantage_scale,
                    "frontier_threshold": args.frontier_threshold,
                    "mastered_threshold": args.mastered_threshold,
                    "mix_targeted": args.mix_targeted,
                    "mix_neighbor": args.mix_neighbor,
                    "mix_replay": args.mix_replay,
                    "neighbor_window": args.neighbor_window,
                    "repair_queue_path": str(repair_queue_path),
                    "repair_converted_jsonl": args.repair_converted_jsonl,
                    "coverage_json": args.coverage_json,
                    "stop_on_severe_breaker": args.stop_on_severe_breaker,
                    "model_judge_enabled": bool(args.model_judge_enabled),
                    "judge_model_path": args.judge_model_path,
                    "judge_adapter_path": args.judge_adapter_path,
                    "judge_device": str(args.judge_device),
                    "judge_weights": judge_weights,
                    "judge_diagnostics_path": str(judge_diagnostics_path)
                    if judge_diagnostics_path
                    else None,
                    "reward_mode": args.reward_mode,
                    "reward_masses": {
                        "pass": args.reward_pass_mass,
                        "shaped": args.reward_shaped_mass,
                        "judge": args.reward_judge_mass,
                    },
                    "trust_region_enabled": bool(args.trust_region_enabled),
                    "trust_region_max_seq_kl": args.trust_region_max_seq_kl,
                    "trust_region_max_clip_fraction": args.trust_region_max_clip_fraction,
                    "trust_region_on_violation": args.trust_region_on_violation,
                    "research_methods": summarize_methods(research_methods),
                    "curriculum_state": curriculum.state,
                    "frontier_router_state": router.state,
                    "frontier_fraction": router.frontier_fraction(),
                    "circuit_breaker_state": breaker.to_dict(),
                    "running_mad_scale": running_mad.scale,
                    "total_probes": total_probes,
                    "adaptive_kl": bool(args.adaptive_kl),
                    "kl_state": kl_state.to_dict() if kl_state is not None else None,
                    "target_modules": list(args.target_modules) if args.target_modules else None,
                    "target_module_regex": list(args.target_module_regex)
                    if args.target_module_regex
                    else None,
                    "resolved_target_modules": resolved_target_modules,
                    "trainable_param_regex": list(getattr(args, "trainable_param_regex", []) or [])
                    or None,
                    "freeze_param_regex": list(getattr(args, "freeze_param_regex", []) or [])
                    or None,
                    "selective_training": selective_training,
                    "trainable_parameter_count": trainable_param_count,
                    "trainable_parameter_sample": trainable_param_names[:12],
                    "text_forward_preflight": text_forward_preflight,
                },
                indent=2,
            )
            + "\n"
        )
        print(f"\nSaved adapter to {adapter_dir}")

    if distributed:
        torch.distributed.destroy_process_group()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Soft-KL distillation SFT trainer for quantum-coding chat data.

Extends training/qwen_sft_peft.py with an additional KL-divergence loss
against per-token teacher top-k logprobs (as captured by
scripts/rl_distill_pipeline.py from the GLM5.2 teacher).

Loss = (1 - kl_coeff) * NLL(student, target_tokens)
     + kl_coeff * KL(student_top_k || teacher_top_k)

where the KL is computed over the union of the teacher's top-k tokens
(plus the target token if missing). This avoids materializing the full
~150k vocab — we only gather student logits at the (≤ k+1) token ids the
teacher scored, which fits comfortably on a 61 GiB Ascend NPU.

Usage:
    torchrun --nproc_per_node=2 training/qwen_sft_peft_kl.py \
        --model-name /root/work/filestorage/Qwen3.6-27B \
        --train-file data/generated/rl_distill_27b_v1/rl_distill_samples.jsonl \
        --eval-file data/generated/rl_distill_27b_v1/eval_chatml.jsonl \
        --output-dir outputs/qg-27b-rl-distill-iter1 \
        --kl-coeff 0.5 \
        --nll-coeff 0.5 \
        --temperature 1.0 \
        --max-length 2048 \
        --per-device-batch-size 1 \
        --gradient-accumulation-steps 4 \
        --learning-rate 3e-5 \
        --lora-rank 16 --lora-alpha 32 \
        --target-modules q_proj v_proj o_proj gate_proj up_proj down_proj \
        --train-on-completions-only \
        --gradient-checkpointing \
        --checkpoint-interval-seconds 3600
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Reuse the runtime overlay + text preprocessor + LoRA helpers from the base trainer
from training.runtime_overlay import configure_runtime_overlay_from_env

configure_runtime_overlay_from_env()

from training.artifact_scoring import (
    kl_gate_weight,
    reward_weighted_nll_weight,
)
from training.qwen_sft_peft import (
    DEFAULT_LORA_TARGET_MODULES,
    apply_native_lora,
    persist_adapter,
)
from training.text_preprocessor_backend import (
    TextPreprocessorBackend,
    build_supervised_text_example,
    load_text_preprocessor_backend,
    pad_supervised_text_batch,
)

# ---------------------------------------------------------------------------
# Args
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model-name", required=True)
    p.add_argument(
        "--adapter-init",
        type=Path,
        default=None,
        help="Existing PEFT adapter to warm-start from (e.g. iter-1 SFT adapter).",
    )
    p.add_argument("--train-file", type=Path, required=True)
    p.add_argument("--eval-file", type=Path, default=None)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--device", default="npu")
    p.add_argument("--epochs", type=int, default=2)
    p.add_argument("--max-steps", type=int, default=-1)
    p.add_argument("--per-device-batch-size", type=int, default=1)
    p.add_argument("--gradient-accumulation-steps", type=int, default=4)
    p.add_argument("--learning-rate", type=float, default=3e-5)
    p.add_argument("--warmup-steps", type=int, default=4)
    p.add_argument("--weight-decay", type=float, default=0.0)
    p.add_argument("--max-length", type=int, default=2048)
    # NPU device-map (mirrors qwen_sft_peft.py). For 27B/35B on 2 NPUs we
    # use single-process sharding (balanced-layers) instead of DDP, since
    # each rank loading the full 27B bf16 (~54GB) or 35B (~70GB) OOMs on a
    # 60 GiB Ascend NPU.
    p.add_argument(
        "--npu-device-map",
        choices=["auto", "balanced-layers"],
        default="balanced-layers",
        help="Single-process NPU sharding strategy when not using DDP.",
    )
    p.add_argument(
        "--npu-max-memory-gib",
        type=int,
        default=58,
        help="Per-NPU max_memory (GiB) used with --npu-device-map balanced-layers.",
    )
    p.add_argument("--lora-rank", type=int, default=16)
    p.add_argument("--lora-alpha", type=int, default=32)
    p.add_argument("--lora-dropout", type=float, default=0.05)
    p.add_argument("--lora-backend", choices=["peft", "native"], default="peft")
    p.add_argument("--target-modules", nargs="*", default=None)
    p.add_argument("--train-on-completions-only", action="store_true")
    p.add_argument("--gradient-checkpointing", action="store_true")
    p.add_argument("--overwrite-output-dir", action="store_true")
    p.add_argument("--allow-output-dir-reuse", action="store_true")
    p.add_argument("--log-steps", type=int, default=1)
    p.add_argument("--eval-steps", type=int, default=50)
    p.add_argument(
        "--checkpoint-interval-seconds",
        type=int,
        default=3600,
        help="Save a periodic checkpoint to <output-dir>/checkpoints/step-<N>/adapter every N seconds (rank 0 only). 0 disables.",
    )
    # KL-specific
    p.add_argument(
        "--kl-coeff",
        type=float,
        default=0.5,
        help="Weight on the KL(teacher || student) loss term.",
    )
    p.add_argument(
        "--nll-coeff", type=float, default=0.5, help="Weight on the standard NLL loss term."
    )
    p.add_argument(
        "--temperature",
        type=float,
        default=1.0,
        help="Softmax temperature for both student and teacher distributions before KL.",
    )
    p.add_argument(
        "--teacher-logits-field",
        default="teacher_logits",
        help="Top-level JSON key in each train row carrying the teacher logprobs.",
    )
    p.add_argument(
        "--min-teacher-logprob-tokens",
        type=int,
        default=4,
        help="Skip a sample if the teacher provided fewer than this many scored tokens.",
    )
    p.add_argument(
        "--reward-floor",
        type=float,
        default=0.0,
        help="Drop samples whose metadata.reward is below this value "
        "(0.0 = keep all; 0.3 = drop bottom-30%%-quality samples).",
    )
    # Per-artifact reward-weighted distillation (additive; default-off for
    # back-compat with the legacy single-reward path). See
    # docs/per-artifact-scoring-rd-plan-2026-07-08.md.
    p.add_argument(
        "--reward-weighted-nll",
        action="store_true",
        default=False,
        help="Scale the NLL term by (reward - reward_floor)/(1 - reward_floor) "
        "so high-reward samples contribute more gradient.",
    )
    p.add_argument(
        "--per-artifact-kl-gate",
        action="store_true",
        default=False,
        help="Scale the KL term by max(0.3, r_teacher_confidence) so the "
        "teacher distribution is down-weighted when the teacher is uncertain.",
    )
    p.add_argument(
        "--partial-credit-upweight",
        type=float,
        default=0.0,
        help="Add an extra NLL weight of this value * r_partial to up-weight "
        "near-miss samples (H1 knob). 0.0 disables.",
    )
    return p.parse_args()


# ---------------------------------------------------------------------------
# Dataset that also returns teacher top-k logprobs per assistant position
# ---------------------------------------------------------------------------


class KlDistillDataset:
    """Loads ChatML rows + aligned teacher top-k logprobs.

    Each row in train_file must look like:
        {
          "messages": [{role, content}, ...],
          "teacher_logits": {
                            "content": "<assistant text>",
                            "logprobs": [
                              {"token": "...", "logprob": -1.2,
                               "top_logprobs": [{"token": "...", "logprob": -0.4}, ...]},
                              ...  # one entry per teacher-generated token
                            ],
                            "top_logprobs": 20
                          },
                          ...
        }
    The dataset aligns teacher logprobs to the assistant span of the
    tokenized sequence so the trainer can compute per-token KL.
    """

    def __init__(
        self,
        path: Path,
        backend: TextPreprocessorBackend,
        max_length: int,
        *,
        train_on_completions_only: bool = True,
        teacher_logits_field: str = "teacher_logits",
        min_teacher_logprob_tokens: int = 4,
        reward_floor: float = 0.0,
    ) -> None:
        self.rows: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    continue
                if "messages" not in row:
                    continue
                tl = row.get(teacher_logits_field)
                if not isinstance(tl, dict) or not isinstance(tl.get("logprobs"), list):
                    continue
                if len(tl["logprobs"]) < min_teacher_logprob_tokens:
                    continue
                # Reward-floor filter: drop samples below the floor (if configured).
                if reward_floor > 0.0:
                    reward = float(row.get("metadata", {}).get("reward", 1.0) or 1.0)
                    if reward < reward_floor:
                        continue
                self.rows.append(row)
        self.backend = backend
        self.max_length = max_length
        self.train_on_completions_only = train_on_completions_only
        self.teacher_logits_field = teacher_logits_field

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        row = self.rows[idx]
        example = build_supervised_text_example(
            row,
            self.backend,
            self.max_length,
            train_on_completions_only=self.train_on_completions_only,
        )
        example[self.teacher_logits_field] = row.get(self.teacher_logits_field, {})
        example["_row_index"] = idx
        # Pass metadata through so the trainer can compute reward-weighted loss.
        # We carry the full metadata dict (reward + artifact_scores + anything
        # else the pipeline wrote); the trainer reads only what it needs.
        example["_metadata"] = row.get("metadata", {}) or {}
        return example


# ---------------------------------------------------------------------------
# Token-id alignment between teacher top-k and student vocab
# ---------------------------------------------------------------------------


def _build_teacher_target_tensors(
    teacher_logits: dict[str, Any],
    backend: TextPreprocessorBackend,
    assistant_text: str,
    assistant_start_in_full: int,
    full_token_ids: list[int],
    torch_module: Any,
    *,
    device: Any,
) -> tuple[Any, Any, Any]:
    """Align teacher top-k logprobs to positions in `full_token_ids`.

    Returns three tensors, all of shape [T] where T is the number of teacher
    logprob entries we could confidently align to a position in the full
    sequence:
      - teacher_token_ids:   the teacher's argmax token id (in student vocab)
      - teacher_logprob_argmax: float logprob of the argmax token
      - teacher_topk_token_ids:  [T, K] token ids for the top-k
      - teacher_topk_logprobs:   [T, K] logprobs (one-hot aligned to topk_token_ids)

    Alignment strategy:
      1. Tokenize the assistant_text independently with the student tokenizer.
      2. Walk through the teacher's logprobs list; each entry's `token` field
         is the teacher's generated surface string. We match by greedily
         concatenating teacher tokens until the decoded string matches the
         next student token's decoded string, then advance both pointers.

    In practice the teacher and student tokenizers may differ, so we use a
    robust fallback: simply align position-by-position over the assistant
    span (teacher_logprobs[i] <-> student_token_at_assistant_start + i). When
    the counts mismatch we truncate to the shorter of the two.
    """
    torch = torch_module
    logprobs = teacher_logits.get("logprobs", [])
    if not logprobs:
        empty = torch.zeros(0, dtype=torch.long, device=device)
        empty_f = torch.zeros(0, dtype=torch.float32, device=device)
        empty_2d = torch.zeros(0, 0, dtype=torch.long, device=device)
        return empty, empty_f, empty_2d, empty_f

    # Student-side: token ids covering the assistant span (target tokens).
    # full_token_ids has the full sequence; the assistant tokens are those
    # from assistant_start_in_full to the end (we constructed the example so
    # the assistant text is the final segment).
    assistant_token_ids = full_token_ids[assistant_start_in_full:]
    n_assistant = len(assistant_token_ids)
    n_teacher = len(logprobs)
    T = min(n_assistant, n_teacher)
    if T == 0:
        empty = torch.zeros(0, dtype=torch.long, device=device)
        empty_f = torch.zeros(0, dtype=torch.float32, device=device)
        empty_2d = torch.zeros(0, 0, dtype=torch.long, device=device)
        return empty, empty_f, empty_2d, empty_f

    # Determine K (top-k width) from the first entry that has top_logprobs.
    K = 0
    for entry in logprobs[:T]:
        tl = entry.get("top_logprobs") or []
        if isinstance(tl, list) and len(tl) > K:
            K = len(tl)
    K = max(K, 1)
    # Cap K to keep memory bounded; 20 matches the teacher's top_logprobs.
    K = min(K, 20)

    teacher_token_ids = torch.full((T,), -100, dtype=torch.long, device=device)
    teacher_logprob_argmax = torch.zeros(T, dtype=torch.float32, device=device)
    teacher_topk_token_ids = torch.full((T, K), -100, dtype=torch.long, device=device)
    teacher_topk_logprobs = torch.full((T, K), float("-inf"), dtype=torch.float32, device=device)

    tokenizer = getattr(backend, "tokenizer", None)
    for i in range(T):
        entry = logprobs[i]
        argmax_token_str = entry.get("token", "")
        argmax_logprob = float(entry.get("logprob", 0.0))
        # Encode the teacher's argmax surface string to a student vocab id.
        tid = -100
        if tokenizer is not None and argmax_token_str:
            try:
                enc = tokenizer.encode(argmax_token_str, add_special_tokens=False)
                if enc:
                    tid = int(enc[0])
            except Exception:
                tid = -100
        teacher_token_ids[i] = tid if tid >= 0 else -100
        teacher_logprob_argmax[i] = argmax_logprob
        topk = entry.get("top_logprobs") or []
        if isinstance(topk, list):
            for j, item in enumerate(topk[:K]):
                if not isinstance(item, dict):
                    continue
                tok_str = item.get("token", "")
                lp = float(item.get("logprob", float("-inf")))
                k_id = -100
                if tokenizer is not None and tok_str:
                    try:
                        enc = tokenizer.encode(tok_str, add_special_tokens=False)
                        if enc:
                            k_id = int(enc[0])
                    except Exception:
                        k_id = -100
                teacher_topk_token_ids[i, j] = k_id
                teacher_topk_logprobs[i, j] = lp

    return teacher_token_ids, teacher_logprob_argmax, teacher_topk_token_ids, teacher_topk_logprobs


# ---------------------------------------------------------------------------
# KL + NLL loss
# ---------------------------------------------------------------------------


def kl_distill_loss(
    *,
    student_logits_at_positions: Any,  # [T, V] (already float32)
    teacher_token_ids: Any,  # [T] long, -100 = skip
    teacher_logprob_argmax: Any,  # [T] float
    teacher_topk_token_ids: Any,  # [T, K] long, -100 = pad
    teacher_topk_logprobs: Any,  # [T, K] float, -inf = pad
    nll_labels: Any,  # [T] long, the target token ids for NLL
    torch_module: Any,
    ignore_index: int = -100,
    kl_coeff: float = 0.5,
    nll_coeff: float = 0.5,
    temperature: float = 1.0,
) -> tuple[Any, dict[str, float]]:
    """Compute combined NLL + KL loss over the assistant span.

    Both losses are computed token-wise and averaged over valid positions
    (positions where the teacher argmax token id is known).
    """
    torch = torch_module
    T = student_logits_at_positions.shape[0]
    if T == 0:
        zero = torch.zeros((), device=student_logits_at_positions.device, dtype=torch.float32)
        return zero, {"nll": 0.0, "kl": 0.0, "total": 0.0, "valid_tokens": 0.0}

    # ---- NLL on the target tokens ----
    valid_nll_mask = nll_labels != ignore_index
    nll_per_token = torch.nn.functional.cross_entropy(
        student_logits_at_positions,
        nll_labels.clamp(min=0),
        ignore_index=ignore_index,
        reduction="none",
    )
    nll_sum = (nll_per_token * valid_nll_mask.float()).sum()
    nll_tokens = valid_nll_mask.float().sum().clamp(min=1.0)
    nll_loss = nll_sum / nll_tokens

    # ---- KL over the union of teacher top-k token ids ----
    # Build a [T, K+1] tensor of token ids to gather from student logits:
    #   column 0 = teacher argmax, columns 1..K = teacher top-k.
    union_ids = torch.cat(
        [teacher_token_ids.unsqueeze(1), teacher_topk_token_ids], dim=1
    )  # [T, K+1]
    # Replace -100 pads with 0 for gather; we'll mask them out later.
    safe_union_ids = union_ids.clamp(min=0)
    # Gather student logits at the union token ids: [T, K+1]
    student_logits_temp = student_logits_at_positions / max(temperature, 1e-6)
    gathered = torch.gather(student_logits_temp, dim=1, index=safe_union_ids)

    # Build the teacher distribution over the same union: [T, K+1]
    teacher_argmax_lp = teacher_logprob_argmax.unsqueeze(1)  # [T, 1]
    teacher_topk_lp = teacher_topk_logprobs  # [T, K]
    teacher_union_lp = torch.cat([teacher_argmax_lp, teacher_topk_lp], dim=1)  # [T, K+1]

    # Mask out padded positions (where union_ids == -100 or teacher_union_lp is -inf)
    valid_mask = (union_ids != -100) & torch.isfinite(teacher_union_lp)
    # Mask out positions where the teacher argmax is unknown
    valid_row = teacher_token_ids != -100
    valid_mask = valid_mask & valid_row.unsqueeze(1)

    # Convert teacher logprobs to probabilities (already in log space, but
    # the teacher's top-k is not a full distribution — we renormalize over
    # the union so KL is well-defined).
    teacher_lp = teacher_union_lp.masked_fill(~valid_mask, float("-inf"))
    teacher_probs = torch.softmax(teacher_lp, dim=1)  # [T, K+1], sums to 1 over valid cols

    # Student log-probs over the same union
    student_lp = gathered.masked_fill(~valid_mask, float("-inf"))
    student_logprobs = torch.log_softmax(student_lp, dim=1)  # [T, K+1]

    # KL(teacher || student) = sum_k teacher_prob_k * (log teacher_prob_k - log student_prob_k)
    # Use the numerically-stable form: sum_k teacher_prob_k * (log student_prob_k)
    # (since teacher's own log-probs are constants, the H(teacher) term is a
    # constant w.r.t. the student and can be dropped from the gradient; we
    # still report the full KL for monitoring.)
    kl_per_row = (
        teacher_probs * (torch.log(teacher_probs.clamp(min=1e-12)) - student_logprobs)
    ).sum(dim=1)
    # Mask out rows with no valid tokens
    kl_per_row = kl_per_row * valid_row.float()
    kl_tokens = valid_row.float().sum().clamp(min=1.0)
    kl_loss = kl_per_row.sum() / kl_tokens

    total = nll_coeff * nll_loss + kl_coeff * kl_loss
    return total, {
        "nll": float(nll_loss.detach().item()),
        "kl": float(kl_loss.detach().item()),
        "total": float(total.detach().item()),
        "valid_tokens": float(nll_tokens.detach().item()),
    }


# ---------------------------------------------------------------------------
# Main training loop
# ---------------------------------------------------------------------------


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if (
        not args.overwrite_output_dir
        and not args.allow_output_dir_reuse
        and any(args.output_dir.iterdir())
    ):
        print(
            json.dumps({"stage": "error", "message": f"output_dir not empty: {args.output_dir}"}),
            flush=True,
        )
        return 2

    import torch  # noqa: F811

    # NPU device resolution (matches qwen_sft_peft.py conventions)
    if args.device == "npu":
        try:
            import torch_npu  # noqa: F401
        except Exception:
            pass
    device = torch.device(
        args.device if torch.device(args.device).type in ("npu", "cuda", "cpu") else "cpu"
    )

    local_rank = int(os.environ.get("LOCAL_RANK", 0))
    rank = int(os.environ.get("RANK", 0))
    world_size = int(os.environ.get("WORLD_SIZE", 1))
    distributed = world_size > 1
    if distributed:
        torch.distributed.init_process_group(backend="hccl" if args.device == "npu" else "nccl")
        device = torch.device(f"{args.device}:{local_rank}")
        torch.npu.set_device(device) if args.device == "npu" else torch.cuda.set_device(device)

    print(
        json.dumps(
            {
                "stage": "args_parsed",
                "output_dir": str(args.output_dir),
                "distributed": distributed,
                "world_size": world_size,
                "kl_coeff": args.kl_coeff,
                "nll_coeff": args.nll_coeff,
                "temperature": args.temperature,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    # Text preprocessor (tokenizer + chat rendering)
    text_preprocessor = load_text_preprocessor_backend(
        model_name=args.model_name,
        trust_remote_code=True,
        chat_template=None,
    )

    # Dataset
    train_dataset = KlDistillDataset(
        args.train_file,
        text_preprocessor,
        args.max_length,
        train_on_completions_only=args.train_on_completions_only,
        teacher_logits_field=args.teacher_logits_field,
        min_teacher_logprob_tokens=args.min_teacher_logprob_tokens,
        reward_floor=args.reward_floor,
    )
    print(
        json.dumps(
            {
                "stage": "dataset_loaded",
                "train_rows": len(train_dataset),
                "train_file": str(args.train_file),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    if len(train_dataset) == 0:
        print(
            json.dumps({"stage": "error", "message": "no train rows with teacher logits found"}),
            flush=True,
        )
        return 3

    # Model + LoRA. Mirror the base trainer's loading strategy:
    # - DDP (distributed=True): each rank loads the model onto its own NPU
    #   via device_map={"": "npu:<local_rank>"}. Used only when the model
    #   fits on a single NPU.
    # - Single-process sharding (distributed=False, npu_device_map=
    #   "balanced-layers"): the model is split across all visible NPUs.
    #   This is the path used for 27B/35B on 2 NPUs, since loading the
    #   full bf16 model onto one NPU OOMs.
    from transformers import AutoConfig, AutoModelForCausalLM

    from training.model_backend import select_transformers_model_loader
    from training.qwen_sft_peft import (
        _visible_npu_indices,
        build_balanced_npu_layer_device_map,
    )

    model_config = AutoConfig.from_pretrained(args.model_name, trust_remote_code=True)
    load_dtype = torch.bfloat16
    model_kwargs: dict[str, Any] = {
        "trust_remote_code": True,
        "low_cpu_mem_usage": True,
        "torch_dtype": load_dtype,
        "config": model_config,
    }
    # Honor the same attn-impl env var as the base trainer.
    _attn_impl = os.environ.get("QWEN_SFT_ATTN_IMPL", "").strip()
    if _attn_impl:
        model_kwargs["attn_implementation"] = _attn_impl
        try:
            model_config._attn_implementation = _attn_impl
        except Exception:
            pass
    if args.device == "npu":
        if distributed:
            model_kwargs["device_map"] = {"": f"npu:{local_rank}"}
        elif args.npu_device_map == "balanced-layers":
            visible_npus = _visible_npu_indices()
            model_kwargs["device_map"] = build_balanced_npu_layer_device_map(
                model_config, visible_npus
            )
            model_kwargs["max_memory"] = {
                f"npu:{idx}": f"{args.npu_max_memory_gib}GiB" for idx in range(len(visible_npus))
            }
            print(
                json.dumps(
                    {
                        "stage": "balanced_npu_device_map_ready",
                        "visible_npus": visible_npus,
                        "device_map_entries": len(model_kwargs["device_map"]),
                        "max_memory_gib": args.npu_max_memory_gib,
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
        else:
            model_kwargs["device_map"] = "auto"

    model_loader, _runtime_compat, _meta = select_transformers_model_loader(
        args.model_name,
        auto_config_cls=AutoConfig,
        auto_model_for_causal_lm_cls=AutoModelForCausalLM,
        transformers_module=sys.modules.get("transformers"),
    )
    model = model_loader.from_pretrained(args.model_name, **model_kwargs)
    print(
        json.dumps(
            {"stage": "model_loaded", "device_map": "device_map" in model_kwargs},
            ensure_ascii=False,
        ),
        flush=True,
    )

    if args.gradient_checkpointing:
        try:
            model.gradient_checkpointing_enable()
        except Exception as exc:
            print(
                json.dumps({"stage": "warn", "msg": f"gradient_checkpointing failed: {exc}"}),
                flush=True,
            )
    # IMPORTANT: do NOT call model.to(device) when device_map is set — the
    # model is already sharded across NPUs by from_pretrained.

    target_modules = args.target_modules or DEFAULT_LORA_TARGET_MODULES
    if args.lora_backend == "native":
        apply_native_lora(
            model,
            torch,
            target_modules,
            args.lora_rank,
            args.lora_alpha,
            args.lora_dropout,
        )
        adapter_init = None
    else:
        from peft import LoraConfig, get_peft_model

        peft_cfg = LoraConfig(
            r=args.lora_rank,
            lora_alpha=args.lora_alpha,
            lora_dropout=args.lora_dropout,
            target_modules=target_modules,
            bias="none",
            task_type="CAUSAL_LM",
        )
        model = get_peft_model(model, peft_cfg)
        adapter_init = args.adapter_init
        if adapter_init is not None:
            from peft import set_peft_model_state_dict

            sd = torch.load(adapter_init / "adapter_model.bin", map_location="cpu")
            set_peft_model_state_dict(model, sd)
            print(
                json.dumps(
                    {"stage": "adapter_init_loaded", "path": str(adapter_init)}, ensure_ascii=False
                ),
                flush=True,
            )

    if distributed:
        model = torch.nn.parallel.DistributedDataParallel(
            model,
            device_ids=[local_rank],
            output_device=local_rank,
        )

    # Optimizer + scheduler
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=args.learning_rate,
        weight_decay=args.weight_decay,
    )
    total_steps_per_epoch = max(
        1,
        math.ceil(
            len(train_dataset)
            / max(args.per_device_batch_size, 1)
            / max(args.gradient_accumulation_steps, 1)
        ),
    )
    total_train_steps = (
        total_steps_per_epoch * args.epochs if args.max_steps < 0 else args.max_steps
    )
    warmup_steps = min(args.warmup_steps, max(total_train_steps // 10, 1))
    scheduler = torch.optim.lr_scheduler.LambdaLR(
        optimizer,
        lr_lambda=lambda step: min(1.0, (step + 1) / max(warmup_steps, 1)),
    )

    # Collator: reuse the base trainer's pad_supervised_text_batch for
    # input_ids / attention_mask / labels, then attach the per-row teacher
    # logits payloads so the training loop can build KL targets.
    def collate(batch: list[dict[str, Any]]) -> dict[str, Any]:
        padded = pad_supervised_text_batch(
            batch, text_preprocessor, torch, pad_to_max_length=args.max_length
        )
        # Pass through teacher_logits payloads keyed by row index in this batch.
        padded["teacher_logits_payloads"] = {
            i: item.get(args.teacher_logits_field, {}) for i, item in enumerate(batch)
        }
        # Pass through metadata payloads (reward, artifact_scores) keyed by
        # row index so the loss can weight per-sample.
        padded["metadata_payloads"] = {i: item.get("_metadata", {}) for i, item in enumerate(batch)}
        return padded

    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=args.per_device_batch_size,
        shuffle=True,
        collate_fn=collate,
        drop_last=False,
    )

    global_step = 0
    optimizer.zero_grad(set_to_none=True)
    last_checkpoint_time = time.time()
    log_every = max(args.log_steps, 1)

    print(
        json.dumps(
            {
                "stage": "training_start",
                "total_train_steps": total_train_steps,
                "steps_per_epoch": total_steps_per_epoch,
                "epochs": args.epochs,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    for epoch in range(args.epochs):
        model.train()
        for batch_index, batch in enumerate(train_loader, start=1):
            if args.max_steps >= 0 and global_step >= args.max_steps:
                break
            # Place the batch on the device hosting the model's first
            # parameter (matters for balanced-layers sharding, where the
            # first layer may be on npu:0 even if local_rank > 0).
            from training.qwen_sft_peft import first_parameter_device

            batch_device = first_parameter_device(model, device)
            batch = {k: (v.to(batch_device) if hasattr(v, "to") else v) for k, v in batch.items()}
            input_ids = batch["input_ids"]  # [B, L]
            labels = batch["labels"]  # [B, L], -100 masked
            attention_mask = batch.get("attention_mask")

            # Forward pass — get full logits (we'll only use the assistant span)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits  # [B, L, V]
            # Shift for next-token prediction: predict token t+1 from position t
            shift_logits = logits[:, :-1, :]  # [B, L-1, V]
            shift_labels = labels[:, 1:]  # [B, L-1]
            # Identify assistant positions (where labels != -100)
            assistant_mask = shift_labels != -100  # [B, L-1]

            # For each row in the batch, gather student logits at assistant
            # positions and pair with the teacher's top-k logprobs.
            batch_loss = torch.zeros((), device=device, dtype=torch.float32)
            batch_stats = {"nll": 0.0, "kl": 0.0, "total": 0.0, "valid_tokens": 0.0, "rows": 0}
            B = shift_logits.shape[0]
            for b in range(B):
                row_mask = assistant_mask[b]  # [L-1]
                if row_mask.sum() == 0:
                    continue
                assistant_positions = row_mask.nonzero(as_tuple=False).squeeze(-1)  # [T]
                # Student logits at the assistant positions: [T, V]
                student_logits_ap = shift_logits[b].index_select(0, assistant_positions).float()
                # NLL labels at the same positions
                nll_labels = shift_labels[b].index_select(0, assistant_positions)
                # Reconstruct the full token ids (with the BOS/prompt prefix) so
                # we can re-derive the assistant span for teacher-logprobs alignment.
                full_token_ids = input_ids[b].tolist()
                # The assistant span starts at the first assistant position + 1
                # in the original (unshifted) sequence.
                if len(assistant_positions) > 0:
                    assistant_start_in_full = int(assistant_positions[0].item()) + 1
                else:
                    assistant_start_in_full = len(full_token_ids)
                # Fetch the teacher logits payload for this row (passed
                # through by the custom collator).
                teacher_logits_payload = batch.get("teacher_logits_payloads", {}).get(b, {})
                if not teacher_logits_payload:
                    continue
                # Build teacher target tensors on the same device as the
                # student logits (the lm_head device, which may differ from
                # batch_device under balanced-layers sharding).
                (
                    teacher_token_ids,
                    teacher_logprob_argmax,
                    teacher_topk_token_ids,
                    teacher_topk_logprobs,
                ) = _build_teacher_target_tensors(
                    teacher_logits_payload,
                    text_preprocessor,
                    assistant_text="",  # not used; alignment is positional
                    assistant_start_in_full=assistant_start_in_full,
                    full_token_ids=full_token_ids,
                    torch_module=torch,
                    device=student_logits_ap.device,
                )
                if teacher_token_ids.numel() == 0:
                    continue
                T = teacher_token_ids.shape[0]
                # Truncate student logits to match T (the teacher may have
                # scored fewer tokens than the student's assistant span).
                student_logits_ap = student_logits_ap[:T]
                nll_labels = nll_labels[:T]
                # Replace -100 in nll_labels with 0 for cross_entropy (we
                # mask via valid_mask inside the loss).

                # Per-sample loss coefficients (reward-weighted distillation).
                # Legacy path: all three flags off -> nll_coeff_eff=nll_coeff,
                # kl_coeff_eff=kl_coeff (bit-identical to the old formula).
                row_meta = batch.get("metadata_payloads", {}).get(b, {}) or {}
                row_reward = float(row_meta.get("reward", 1.0) or 1.0)
                artifact_scores = row_meta.get("artifact_scores") or {}
                nll_coeff_eff = args.nll_coeff
                kl_coeff_eff = args.kl_coeff
                if args.reward_weighted_nll or args.partial_credit_upweight > 0.0:
                    nll_coeff_eff = args.nll_coeff * reward_weighted_nll_weight(
                        reward=row_reward,
                        reward_floor=args.reward_floor,
                        r_partial=float(artifact_scores.get("r_partial", 0.0) or 0.0),
                        partial_credit_upweight=args.partial_credit_upweight,
                    )
                if args.per_artifact_kl_gate and artifact_scores:
                    kl_coeff_eff = args.kl_coeff * kl_gate_weight(artifact_scores)

                loss, stats = kl_distill_loss(
                    student_logits_at_positions=student_logits_ap,
                    teacher_token_ids=teacher_token_ids,
                    teacher_logprob_argmax=teacher_logprob_argmax,
                    teacher_topk_token_ids=teacher_topk_token_ids,
                    teacher_topk_logprobs=teacher_topk_logprobs,
                    nll_labels=nll_labels,
                    torch_module=torch,
                    ignore_index=-100,
                    kl_coeff=kl_coeff_eff,
                    nll_coeff=nll_coeff_eff,
                    temperature=args.temperature,
                )
                batch_loss = batch_loss + loss
                batch_stats["nll"] += stats["nll"]
                batch_stats["kl"] += stats["kl"]
                batch_stats["total"] += stats["total"]
                batch_stats["valid_tokens"] += stats["valid_tokens"]
                batch_stats["rows"] += 1

            if batch_stats["rows"] > 0:
                batch_loss = batch_loss / max(batch_stats["rows"], 1)
                scaled = batch_loss / args.gradient_accumulation_steps
                scaled.backward()

            if batch_index % args.gradient_accumulation_steps == 0:
                torch.nn.utils.clip_grad_norm_(
                    [p for p in model.parameters() if p.requires_grad],
                    max_norm=1.0,
                )
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)
                global_step += 1

                if global_step % log_every == 0:
                    print(
                        json.dumps(
                            {
                                "stage": "train_step",
                                "epoch": epoch,
                                "step": global_step,
                                "lr": float(scheduler.get_last_lr()[0]),
                                "nll": batch_stats["nll"] / max(batch_stats["rows"], 1),
                                "kl": batch_stats["kl"] / max(batch_stats["rows"], 1),
                                "loss": batch_stats["total"] / max(batch_stats["rows"], 1),
                            },
                            ensure_ascii=False,
                        ),
                        flush=True,
                    )

                # Periodic checkpoint (rank 0 only)
                if rank == 0 and args.checkpoint_interval_seconds > 0:
                    now = time.time()
                    if now - last_checkpoint_time >= args.checkpoint_interval_seconds:
                        ckpt_dir = args.output_dir / "checkpoints" / f"step-{global_step}"
                        ckpt_adapter = ckpt_dir / "adapter"
                        print(
                            json.dumps(
                                {
                                    "stage": "periodic_checkpoint_start",
                                    "step": global_step,
                                    "adapter_dir": str(ckpt_adapter),
                                }
                            ),
                            flush=True,
                        )
                        try:
                            persist_adapter(
                                save_model=model.module if distributed else model,
                                adapter_dir=ckpt_adapter,
                                torch_module=torch,
                                lora_backend=args.lora_backend,
                                adapter_init=adapter_init,
                                native_config={
                                    "r": args.lora_rank,
                                    "alpha": args.lora_alpha,
                                    "dropout": args.lora_dropout,
                                    "target_modules": target_modules,
                                },
                                text_preprocessor=text_preprocessor,
                            )
                            print(
                                json.dumps(
                                    {
                                        "stage": "periodic_checkpoint_done",
                                        "step": global_step,
                                        "adapter_dir": str(ckpt_adapter),
                                    }
                                ),
                                flush=True,
                            )
                        except Exception as exc:
                            print(
                                json.dumps(
                                    {"stage": "periodic_checkpoint_error", "error": str(exc)}
                                ),
                                flush=True,
                            )
                        last_checkpoint_time = time.time()
        if args.max_steps >= 0 and global_step >= args.max_steps:
            break

    # Final save (rank 0 only)
    if rank == 0:
        final_adapter = args.output_dir / "adapter"
        print(
            json.dumps({"stage": "final_save_start", "adapter_dir": str(final_adapter)}), flush=True
        )
        persist_adapter(
            save_model=model.module if distributed else model,
            adapter_dir=final_adapter,
            torch_module=torch,
            lora_backend=args.lora_backend,
            adapter_init=adapter_init,
            native_config={
                "r": args.lora_rank,
                "alpha": args.lora_alpha,
                "dropout": args.lora_dropout,
                "target_modules": target_modules,
            },
            text_preprocessor=text_preprocessor,
        )
        print(
            json.dumps({"stage": "final_save_done", "adapter_dir": str(final_adapter)}), flush=True
        )

    if distributed:
        torch.distributed.destroy_process_group()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

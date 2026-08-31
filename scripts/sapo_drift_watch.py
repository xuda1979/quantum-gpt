#!/usr/bin/env python3
# ruff: noqa: UP038  # (X | Y) isinstance is py3.10-only; py3.9 .venv gate (precedent: training/grpo_trainer.py)
from __future__ import annotations  # py3.9-safe (PEP 604) annotations

"""SAPO drift watch — alarm on zero-change / flat RL checkpoints within minutes.

Watches a training run's output dir (e.g. outputs/sapo-27b-ai-<ts>/) for NEW
`step_*_adapter` PEFT checkpoints. For each new checkpoint it runs the proven
clone-based merged-delta precheck (the method from reports/sapo-precheck-run3-
step13-2026-08-24.{md,json} and tmp/precheck_fixed.py):

  Phase 1 (seconds, no model load): inspect the adapter safetensors. If every
  tensor is a LoRA A/B matrix and no module has both a nonzero A and a nonzero
  B, the merged weights are bit-identical to base by construction ->
  max_abs_diff = 0.0.
  Phase 2 (minutes, CPU merge): load the base model, CLONE its parameters
  BEFORE PeftModel.from_pretrained(...).merge_and_unload() (merge mutates base
  in place — holding references made every comparison report 0.0), then report
  max_abs_diff across all shared tensors plus a per-tensor bf16 ULP activity
  check (ULP = 2^floor(log2(max_w)) - 7).

Alarm tiers (every measurement -> drift.jsonl; alarms also -> alarms.jsonl and
a one-line grep-able ALARM entry in drift_alarms.log + stderr):

  TIER-0 ZERO_CHANGE          max_abs_diff == 0.0 EXACTLY at ANY checkpoint ->
                              the adapter is byte-identical to base. Stop the
                              run. Fires at the very first checkpoint too.
  TIER-1 FLAT_AT_NOISE_FLOOR  delta unchanged across 2 consecutive checkpoints
                              while below the bf16 noise boundary (~1.2e-4).
  TIER-2 PLATEAU              delta growth <5% across 2 consecutive
                              checkpoints, above noise but below the ACTIVE
                              bar (1e-3).
  TIER-3 ACTIVE               healthy growth (>=5%) or delta >= ACTIVE bar —
                              info only, no alarm.

The watcher only READS the run dir (plus writes its own drift.* files in the
run dir root); it never touches the trainer's active files or checkpoint dirs.

Usage:
  python3 scripts/sapo_drift_watch.py --run-dir outputs/sapo-27b-ai-<ts> \
      --base <base-model-path>            # --watch (default): loop forever
  python3 scripts/sapo_drift_watch.py --run-dir ... --base ... --once \
      # check the newest checkpoint and exit (cron/manual)
"""

import argparse
import json
import math
import os
import re
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# constants / defaults (all tunable via CLI)
# ---------------------------------------------------------------------------

DEFAULT_POLL_SECONDS = 120.0
NOISE_FLOOR_DEFAULT = 1.2e-4  # upper edge of the observed bf16 ULP band (6.1e-5-1.2e-4)
ACTIVE_BAR_DEFAULT = 1e-3  # merged-delta bar for a genuinely working adapter
FLAT_REL_TOL_DEFAULT = 0.01  # relative change that still counts as "unchanged"
PLATEAU_MAX_GROWTH_DEFAULT = 0.05  # growth below this (over 2 checkpoints) = plateau
MAX_RETRIES_DEFAULT = 10  # consecutive failures before an error record

ALARM_TIERS = ("ZERO_CHANGE", "FLAT_AT_NOISE_FLOOR", "PLATEAU")
ALARM_ACTIONS = {
    "ZERO_CHANGE": "STOP_THE_RUN_NOW adapter byte-identical to base; do not continue training",
    "FLAT_AT_NOISE_FLOOR": "delta flat at bf16 noise floor; inspect LR/loads/warm-start",
    "PLATEAU": "delta growth <5% below ACTIVE bar AND LoRA-B flat; review LR/window; strong update needed",
    "QUANTIZATION_STAIR": "no action (merged diff flat at bf16 ULP scale while LoRA-B moves — staircase, not plateau)",
    "ACTIVE": "no action",
    "ERROR": "precheck failed; inspect drift_watch.log",
}

_REPO_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = Path(os.environ.get("QG_ROOT", str(_REPO_ROOT)))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_STEP_RE = re.compile(r"^step_(\d+)_adapter$")


class DriftCheckError(Exception):
    """Raised for transient/mid-save conditions; the watcher retries."""


class WatchState:
    """In-memory progress for --watch mode (processed steps + retry counts)."""

    def __init__(self, processed=None, retries=None):
        self.processed = set(processed or ())
        self.retries = dict(retries or {})


# ---------------------------------------------------------------------------
# checkpoint discovery (read-only on the run dir)
# ---------------------------------------------------------------------------


def parse_step(path) -> int | None:
    m = _STEP_RE.match(Path(path).name)
    return int(m.group(1)) if m else None


def discover_steps(run_dir) -> list[int]:
    """All step_*_adapter steps in the run dir, ascending by step number."""
    run_dir = Path(run_dir)
    if not run_dir.is_dir():
        return []
    steps = []
    for p in run_dir.iterdir():
        if p.is_dir():
            s = parse_step(p)
            if s is not None:
                steps.append(s)
    return sorted(steps)


def newest_step(run_dir) -> int | None:
    steps = discover_steps(run_dir)
    return max(steps) if steps else None


def checkpoint_dir(run_dir, step: int) -> Path:
    return Path(run_dir) / f"step_{step:06d}_adapter"


def drift_jsonl(run_dir) -> Path:
    return Path(run_dir) / "drift.jsonl"


def checkpoint_complete(ckpt_dir) -> bool:
    """Same completeness rule the trainer uses for its atomic saves:
    adapter_config.json + (adapter_model.safetensors | adapter_model.bin)."""
    ckpt_dir = Path(ckpt_dir)
    return (ckpt_dir / "adapter_config.json").is_file() and any(
        (ckpt_dir / name).is_file() for name in ("adapter_model.safetensors", "adapter_model.bin")
    )


# ---------------------------------------------------------------------------
# history (drift.jsonl) handling
# ---------------------------------------------------------------------------


def read_history(path) -> tuple[list[dict], set[int]]:
    """(lines, processed_steps). Tolerates a corrupt tail (crashed mid-append)."""
    lines: list[dict] = []
    processed: set[int] = set()
    path = Path(path)
    if path.is_file():
        for ln in path.read_text().splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                rec = json.loads(ln)
            except Exception:
                continue
            lines.append(rec)
            step = rec.get("step")
            if isinstance(step, int):
                processed.add(step)
    return lines, processed


def adopt_processed_steps(history: list[dict]) -> set[int]:
    """Steps to treat as already-processed when (re)starting a watcher:
    only records carrying a NUMERIC max_abs_diff (a real measurement). Error
    records (max_abs_diff None) must NOT be adopted — their step is re-checked
    once its checkpoint becomes measurable."""
    return {
        rec["step"]
        for rec in history
        if isinstance(rec.get("step"), int) and isinstance(rec.get("max_abs_diff"), (int, float))
    }


def last_prev_line(history: list[dict], step: int) -> dict | None:
    """Most recent recorded line for a DIFFERENT step (consecutive checkpoint
    in step order, even if the run skipped steps in between)."""
    for rec in reversed(history):
        if rec.get("step") != step and isinstance(rec.get("max_abs_diff"), (int, float)):
            return rec
    return None


# ---------------------------------------------------------------------------
# alarm tiering (pure, unit-testable)
# ---------------------------------------------------------------------------


def classify_tier(
    delta: float,
    prev_delta: float | None,
    noise_floor: float = NOISE_FLOOR_DEFAULT,
    active_bar: float = ACTIVE_BAR_DEFAULT,
    flat_rel: float = FLAT_REL_TOL_DEFAULT,
    plateau_max_growth: float = PLATEAU_MAX_GROWTH_DEFAULT,
    cur_lora_b: float | None = None,
    prev_lora_b: float | None = None,
):
    """Return (tier, alarm, growth).

    TIER-0: delta == 0.0 exactly (byte-identical adapter) — fires even with no
    history (the very first checkpoint).
    TIER-1: flat (<= flat_rel relative change) and below the bf16 noise floor.
    TIER-2: below the ACTIVE bar, growth < plateau_max_growth, AND LoRA-B flat
    too (the merged bf16 diff is QUANTIZED at ULP steps — a flat merged diff
    with GROWING LoRA-B is a quantization staircase, not a drift freeze; see
    QUANTIZATION_STAIR). Includes exact-flat above the noise floor and
    regression/shrinking deltas.
    TIER-3: healthy growth or delta >= ACTIVE bar; also the info-only
    QUANTIZATION_STAIR label when only the merged diff is flat.
    """
    if not math.isfinite(delta):
        # NaN/Inf is a BROKEN measurement, not a healthy ACTIVE state —
        # misreporting it as ACTIVE would silently under-alarm on garbage.
        return ("TIER-3", "ERROR", None)
    if delta == 0.0:
        return ("TIER-0", "ZERO_CHANGE", None)
    if prev_delta is None:
        return ("TIER-3", "ACTIVE", None)
    if prev_delta == 0.0:
        growth = 0.0 if delta == 0.0 else float("inf")
    else:
        growth = (delta - prev_delta) / abs(prev_delta)
    flat = abs(delta - prev_delta) <= flat_rel * max(abs(prev_delta), abs(delta))
    if flat and delta < noise_floor:
        return ("TIER-1", "FLAT_AT_NOISE_FLOOR", growth)
    if delta < active_bar and growth < plateau_max_growth:
        if cur_lora_b is not None and prev_lora_b is not None:
            if prev_lora_b == 0.0:
                lb_flat = cur_lora_b == 0.0
            else:
                lb_flat = abs(cur_lora_b - prev_lora_b) <= flat_rel * max(
                    abs(prev_lora_b), abs(cur_lora_b)
                )
            if not lb_flat:
                # Merged diff pinned at a bf16 ULP boundary while LoRA-B keeps
                # moving -> quantization staircase, NOT a plateau (info only).
                return ("TIER-3", "QUANTIZATION_STAIR", growth)
        # Missing LoRA-B history stays conservative: no staircase evidence.
        return ("TIER-2", "PLATEAU", growth)
    return ("TIER-3", "ACTIVE", growth)


def _sanitize_growth(growth: float | None) -> float | None:
    if growth is None:
        return None
    if math.isinf(growth) or math.isnan(growth):
        return None
    return growth


# ---------------------------------------------------------------------------
# the proven clone-based merged-delta precheck (ported from tmp/precheck_fixed.py)
# ---------------------------------------------------------------------------


def load_tensors(adapter_dir):
    """All tensors from *.safetensors (or *.bin) in the adapter dir, on CPU."""
    from safetensors import safe_open  # lazy: import-safe module

    files = sorted(
        p
        for p in Path(adapter_dir).iterdir()
        if p.is_file() and p.suffix in (".safetensors", ".bin")
    )
    tensors = {}
    try:
        for f in files:
            if f.suffix == ".safetensors":
                with safe_open(str(f), framework="pt", device="cpu") as h:
                    for k in h.keys():
                        tensors[k] = h.get_tensor(k)
            else:
                import torch

                tensors.update(torch.load(f, map_location="cpu", weights_only=True))
    except Exception as exc:
        raise DriftCheckError(f"failed to load adapter tensors from {adapter_dir}: {exc}") from exc
    return tensors


def phase1(tensors):
    """Fast structural check: lora-only? any module with nonzero A AND nonzero B?"""
    import torch  # lazy: the module must import without torch

    for name, t in tensors.items():
        if not bool(torch.isfinite(t).all()):
            # NaN/Inf weights make every `> 0.0` check False, which would
            # fabricate an 'inert' 0.0 -> false TIER-0 ZERO_CHANGE stop on a
            # corrupted adapter (2026-08-26 code-review F9).
            raise DriftCheckError(f"adapter tensor {name} contains NaN/Inf — corrupt checkpoint")
    pairs = {}
    lora_only = True
    for name, t in tensors.items():
        if "lora_A" in name:
            pairs.setdefault(name.split("lora_A")[0], {})["A"] = t
        elif "lora_B" in name:
            pairs.setdefault(name.split("lora_B")[0], {})["B"] = t
        else:
            lora_only = False
    max_abs_all = max((t.abs().max().item() for t in tensors.values()), default=0.0)
    max_abs_b = max(
        (p["B"].abs().max().item() for p in pairs.values() if p.get("B") is not None),
        default=0.0,
    )
    possible = any(
        p.get("A") is not None
        and p.get("B") is not None
        and p["A"].abs().max().item() > 0.0
        and p["B"].abs().max().item() > 0.0
        for p in pairs.values()
    )
    return {
        "lora_only": lora_only,
        "max_abs_lora": float(max_abs_all),
        "max_abs_lora_b": float(max_abs_b),
        "nonzero_pair_possible": possible,
    }


def read_scaling(adapter_dir) -> float | None:
    try:
        cfg = json.loads((Path(adapter_dir) / "adapter_config.json").read_text())
        r = int(cfg.get("r", 0) or 0)
        alpha = float(cfg.get("lora_alpha", r or 1))
        return (alpha / r) if r else 1.0
    except Exception:
        return None


def _load_base_model(base_path, device):
    """Load the base causal LM. Prefers the training-package preflight loader
    (proven on the box), falls back to plain transformers."""
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM

    try:
        from training.model_backend import load_causal_lm_with_text_backend_preflight
        from training.qwen_sft_peft import resolve_device
        from training.runtime_overlay import configure_runtime_overlay_from_env

        configure_runtime_overlay_from_env()
        dev = resolve_device(torch, device)
        model = load_causal_lm_with_text_backend_preflight(
            base_path,
            auto_config_cls=AutoConfig,
            auto_model_for_causal_lm_cls=AutoModelForCausalLM,
            model_kwargs={
                "trust_remote_code": True,
                "low_cpu_mem_usage": True,
                "torch_dtype": "auto",
            },
        ).to(dev)
    except Exception:
        dev = device
        model = AutoModelForCausalLM.from_pretrained(
            base_path,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            torch_dtype="auto",
        ).to(dev)
    model.eval()
    return model


def _phase2_merge_diff(adapter_dir, base_path, device="cpu"):
    """Clone-based merged-delta (the definitive check; ~2 min for 851 tensors
    on CPU). CRITICAL: merge_and_unload() mutates the base params IN PLACE —
    holding references made every comparison report max_abs_diff=0. Clone
    BEFORE merging."""
    from peft import PeftModel

    model = _load_base_model(base_path, device)
    base_params = {n: p.detach().clone() for n, p in model.named_parameters()}
    merged = PeftModel.from_pretrained(model, str(adapter_dir)).merge_and_unload()
    max_diff = 0.0
    max_ulp = 0.0
    max_abs_weight = 0.0
    any_active = False
    compared = 0
    for name, p in merged.named_parameters():
        if name in base_params:
            compared += 1
            p_f = p.detach().float()
            b_f = base_params[name].detach().float()
            diff = (p_f - b_f).abs().max().item()
            max_w = max(p_f.abs().max().item(), b_f.abs().max().item())
            if max_w > 0.0:
                ulp = 2.0 ** (math.floor(math.log2(max_w)) - 7)
                max_ulp = max(max_ulp, ulp)
                if diff > ulp:
                    any_active = True
            max_abs_weight = max(max_abs_weight, max_w)
            if diff > max_diff:
                max_diff = diff
    return {
        "max_abs_diff": float(max_diff),
        "tensors_compared": compared,
        "max_abs_weight": float(max_abs_weight),
        "max_ulp": float(max_ulp),
        "any_active": any_active,
    }


def compute_delta(adapter_dir, base_path, device="cpu", merge_fn=None):
    """Full precheck for one adapter dir: phase-1 fast path first, then the
    clone-based CPU merge. Returns a JSON-able record dict; raises
    DriftCheckError for transient/mid-save conditions (caller retries)."""
    adapter_dir = Path(adapter_dir)
    checked_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    scaling = read_scaling(adapter_dir)
    if scaling is None:
        raise DriftCheckError(f"adapter_config.json unreadable in {adapter_dir}")
    tensors = load_tensors(adapter_dir)
    if not tensors:
        raise DriftCheckError(f"no tensors found in {adapter_dir}")
    p1 = phase1(tensors)
    if p1["lora_only"] and not p1["nonzero_pair_possible"]:
        # No A*B pair can be nonzero -> merged weights bit-identical to base.
        return {
            "adapter": str(adapter_dir),
            "base": base_path,
            "checked_at_utc": checked_at,
            "phase": 1,
            "scaling": scaling,
            "max_abs_diff": 0.0,
            "verdict": "inert",
            "tensors_compared": len(tensors),
            "max_abs_lora": p1["max_abs_lora"],
            "max_abs_lora_b": p1["max_abs_lora_b"],
            "lora_only": True,
            "nonzero_pair_possible": False,
            "max_abs_weight": None,
            "max_ulp": None,
            "any_active": False,
        }
    p2 = (merge_fn or _phase2_merge_diff)(adapter_dir, base_path, device)
    if not p2.get("tensors_compared"):
        # A 0-tensor comparison means the merged names didn't match the base
        # (loader/prefix divergence) — max_abs_diff of 0.0 is then MEANINGLESS
        # and would fabricate a TIER-0 ZERO_CHANGE stop on a healthy run.
        raise DriftCheckError(
            f"phase-2 merge compared 0 tensors for {adapter_dir} "
            f"(base/adapter name mismatch) — refusing to report 0.0"
        )
    max_abs_diff = float(p2.get("max_abs_diff", 0.0))
    # Audit #6 verdicts: inert -> diff == 0; active -> some tensor moved > 1
    # bf16 ULP at its own weight scale; else inert_at_precision.
    if max_abs_diff == 0.0:
        verdict = "inert"
    elif p2.get("any_active"):
        verdict = "active"
    else:
        verdict = "inert_at_precision"
    return {
        "adapter": str(adapter_dir),
        "base": base_path,
        "checked_at_utc": checked_at,
        "phase": 2,
        "scaling": scaling,
        "max_abs_diff": max_abs_diff,
        "verdict": verdict,
        "tensors_compared": p2.get("tensors_compared"),
        "max_abs_weight": p2.get("max_abs_weight"),
        "max_ulp": p2.get("max_ulp"),
        "any_active": bool(p2.get("any_active")),
        "max_abs_lora": p1["max_abs_lora"],
        "max_abs_lora_b": p1["max_abs_lora_b"],
        "lora_only": p1["lora_only"],
        "nonzero_pair_possible": p1["nonzero_pair_possible"],
    }


# ---------------------------------------------------------------------------
# record building + emission (the watcher's own files only — never the
# trainer's active files)
# ---------------------------------------------------------------------------


def build_record(
    step: int,
    adapter,
    delta: dict,
    prev: dict | None,
    noise_floor: float = NOISE_FLOOR_DEFAULT,
    active_bar: float = ACTIVE_BAR_DEFAULT,
    flat_rel: float = FLAT_REL_TOL_DEFAULT,
    plateau_max_growth: float = PLATEAU_MAX_GROWTH_DEFAULT,
    checked_at_utc: str | None = None,
) -> dict:
    max_abs_diff = float(delta.get("max_abs_diff"))
    if not math.isfinite(max_abs_diff):
        # A non-finite measurement is an ERROR record, never a numeric value:
        # adopt_processed_steps would adopt it forever and last_prev_line
        # would use it as a valid prev, poisoning every later tier comparison
        # (2026-08-26 code-review F8).
        return build_error_record(step, adapter, f"non-finite max_abs_diff {max_abs_diff}")
    prev_delta = prev.get("max_abs_diff") if prev else None
    if isinstance(prev_delta, (int, float)):
        prev_delta = float(prev_delta)
    tier, alarm, growth = classify_tier(
        max_abs_diff,
        prev_delta,
        noise_floor=noise_floor,
        active_bar=active_bar,
        flat_rel=flat_rel,
        plateau_max_growth=plateau_max_growth,
        cur_lora_b=delta.get("max_abs_lora_b"),
        prev_lora_b=prev.get("max_abs_lora_b") if prev else None,
    )
    return {
        "ts": checked_at_utc or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "step": int(step),
        "adapter": str(adapter),
        "base": delta.get("base"),
        "phase": delta.get("phase"),
        "scaling": delta.get("scaling"),
        "max_abs_diff": max_abs_diff,
        "max_abs_lora": delta.get("max_abs_lora"),
        "max_abs_lora_b": delta.get("max_abs_lora_b"),
        "nonzero_pair_possible": delta.get("nonzero_pair_possible"),
        "lora_only": delta.get("lora_only"),
        "tensors_compared": delta.get("tensors_compared"),
        "max_abs_weight": delta.get("max_abs_weight"),
        "max_ulp": delta.get("max_ulp"),
        "any_active": bool(delta.get("any_active")),
        "verdict": delta.get("verdict", "unknown"),
        "prev_step": prev.get("step") if prev else None,
        "prev_max_abs_diff": prev_delta,
        "growth": _sanitize_growth(growth),
        "tier": tier,
        "alarm": alarm,
        "action": ALARM_ACTIONS.get(alarm, ""),
        "status": "ok",
    }


def build_error_record(step: int, adapter, error: str, checked_at_utc: str | None = None) -> dict:
    return {
        "ts": checked_at_utc or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "step": int(step),
        "adapter": str(adapter),
        "max_abs_diff": None,
        "verdict": "unknown",
        "tier": "TIER-3",
        "alarm": "ERROR",
        "action": ALARM_ACTIONS["ERROR"],
        "status": "error",
        "error": str(error)[:300],
        "prev_step": None,
        "prev_max_abs_diff": None,
        "growth": None,
    }


def alarm_line(record: dict) -> str:
    growth = record.get("growth")
    g = f"{growth:.3g}" if isinstance(growth, (int, float)) else "n/a"
    d = record.get("max_abs_diff")
    d_str = f"{d:.6g}" if isinstance(d, (int, float)) else "n/a"
    return (
        "ALARM {tier} {alarm} step={step} max_abs_diff={d} verdict={v} "
        "growth={g} prev_step={ps} adapter={a} ts={t} {action}"
    ).format(
        tier=record.get("tier"),
        alarm=record.get("alarm"),
        step=record.get("step"),
        d=d_str,
        v=record.get("verdict"),
        g=g,
        ps=record.get("prev_step"),
        a=record.get("adapter"),
        t=record.get("ts"),
        action=record.get("action"),
    )


def write_json_atomic(path, record: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(record, indent=2, default=str) + "\n")
    tmp.replace(path)


def append_jsonl(path, record: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(record, default=str) + "\n")
        f.flush()
        try:
            os.fsync(f.fileno())
        except Exception:
            pass


def log_msg(run_dir, msg: str) -> None:
    line = f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] {msg}"
    print(line, file=sys.stderr, flush=True)
    try:
        p = Path(run_dir) / "drift_watch.log"
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def emit_record(run_dir, record: dict) -> dict:
    """Write the record to the watcher-owned files; alarm side-effects for
    alarm tiers. Never touches trainer files."""
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    step = record.get("step")
    if isinstance(step, int):
        write_json_atomic(run_dir / f"drift_step_{step:06d}.json", record)
    write_json_atomic(run_dir / "drift.json", record)  # latest snapshot
    append_jsonl(run_dir / "drift.jsonl", record)
    if record.get("alarm") in ALARM_TIERS:
        append_jsonl(run_dir / "alarms.jsonl", record)
        line = alarm_line(record)
        with (run_dir / "drift_alarms.log").open("a") as f:
            f.write(line + "\n")
            f.flush()
        print(line, file=sys.stderr, flush=True)
    return record


# ---------------------------------------------------------------------------
# --once mode and the --watch poll core
# ---------------------------------------------------------------------------


def run_once(
    run_dir,
    base_path,
    device="cpu",
    precheck_fn=None,
    noise_floor: float = NOISE_FLOOR_DEFAULT,
    active_bar: float = ACTIVE_BAR_DEFAULT,
    flat_rel: float = FLAT_REL_TOL_DEFAULT,
    plateau_max_growth: float = PLATEAU_MAX_GROWTH_DEFAULT,
) -> dict | None:
    """Measure every not-yet-measured step_*_adapter (ascending step order).

    Uses the same poll semantics as --watch: a step created between two
    --once ticks must not be skipped just because it is no longer the newest
    (its ZERO_CHANGE would be invisible and the prev chain would silently
    widen past it — 2026-08-26 code-review F10). Returns the newest emitted
    record, or None when nothing new was measurable (no checkpoints / all
    incomplete / all failed)."""
    run_dir = Path(run_dir)
    if not discover_steps(run_dir):
        log_msg(run_dir, f"no step_*_adapter checkpoints found in {run_dir}")
        return None
    history, _ = read_history(drift_jsonl(run_dir))
    # numeric-only adoption: an error record for a step must NOT block its
    # re-measurement (same contract as watch_loop; 2026-08-26 review F10).
    state = WatchState(processed=adopt_processed_steps(history))
    emitted = poll_run(
        run_dir,
        base_path,
        state,
        device=device,
        precheck_fn=precheck_fn,
        noise_floor=noise_floor,
        active_bar=active_bar,
        flat_rel=flat_rel,
        plateau_max_growth=plateau_max_growth,
    )
    return emitted[-1] if emitted else None


def poll_run(
    run_dir,
    base_path,
    state: WatchState,
    device="cpu",
    precheck_fn=None,
    noise_floor: float = NOISE_FLOOR_DEFAULT,
    active_bar: float = ACTIVE_BAR_DEFAULT,
    flat_rel: float = FLAT_REL_TOL_DEFAULT,
    plateau_max_growth: float = PLATEAU_MAX_GROWTH_DEFAULT,
    max_retries: int = MAX_RETRIES_DEFAULT,
) -> list[dict]:
    """Process all not-yet-processed checkpoints (ascending step order).
    Partial/corrupt dirs are skipped and retried on later polls; after
    max_retries consecutive failures one error record is emitted (no crash, no
    infinite error spam). A failed step is NEVER marked processed: if its
    checkpoint becomes readable later (slow save, fs hiccup, re-save), it is
    measured then — a permanently unmeasured step could be a silent
    ZERO_CHANGE. Returns the records emitted this poll."""
    run_dir = Path(run_dir)
    emitted: list[dict] = []
    for step in discover_steps(run_dir):
        if step in state.processed:
            continue
        adapter = checkpoint_dir(run_dir, step)
        if not checkpoint_complete(adapter):
            state.retries[step] = state.retries.get(step, 0) + 1
            log_msg(
                run_dir,
                f"[step {step}] checkpoint incomplete (mid-save) — retry {state.retries[step]}/{max_retries}",
            )
            if state.retries[step] == max_retries + 1:  # crossed the limit once
                rec = build_error_record(
                    step, adapter, f"checkpoint incomplete after {max_retries} retries"
                )
                emit_record(run_dir, rec)
                emitted.append(rec)
            continue
        try:
            delta = (precheck_fn or compute_delta)(adapter, base_path, device)
            if not delta.get("tensors_compared"):
                # Injected/alternate prechecks bypass compute_delta's guard: a
                # 0-tensor comparison must never masquerade as byte-identical.
                raise DriftCheckError(
                    f"phase-2 merge compared 0 tensors for {adapter.name} "
                    f"(base/adapter name mismatch) — refusing to report 0.0"
                )
        except Exception as exc:
            state.retries[step] = state.retries.get(step, 0) + 1
            log_msg(
                run_dir,
                f"[step {step}] precheck failed ({type(exc).__name__}: {exc}) — retry {state.retries[step]}/{max_retries}",
            )
            if state.retries[step] == max_retries + 1:  # crossed the limit once
                rec = build_error_record(step, adapter, str(exc))
                emit_record(run_dir, rec)
                emitted.append(rec)
            continue
        history, _ = read_history(drift_jsonl(run_dir))
        prev = last_prev_line(history, step)
        rec = build_record(
            step,
            adapter,
            delta,
            prev,
            noise_floor=noise_floor,
            active_bar=active_bar,
            flat_rel=flat_rel,
            plateau_max_growth=plateau_max_growth,
        )
        emit_record(run_dir, rec)
        state.processed.add(step)
        state.retries.pop(step, None)
        emitted.append(rec)
    return emitted


def watch_loop(
    run_dir,
    base_path,
    poll_seconds: float = DEFAULT_POLL_SECONDS,
    device="cpu",
    precheck_fn=None,
    noise_floor: float = NOISE_FLOOR_DEFAULT,
    active_bar: float = ACTIVE_BAR_DEFAULT,
    flat_rel: float = FLAT_REL_TOL_DEFAULT,
    plateau_max_growth: float = PLATEAU_MAX_GROWTH_DEFAULT,
    max_retries: int = MAX_RETRIES_DEFAULT,
) -> int:
    run_dir = Path(run_dir)
    log_msg(
        run_dir,
        f"drift-watch pid={os.getpid()} watching {run_dir} base={base_path} poll={poll_seconds}s",
    )
    state = WatchState()
    while True:
        try:
            # Re-adopt processed steps written by other instances/restarts
            # (successfully measured steps only — error records are re-checked).
            history_now, _ = read_history(drift_jsonl(run_dir))
            state.processed |= adopt_processed_steps(history_now)
            emitted = poll_run(
                run_dir,
                base_path,
                state,
                device=device,
                precheck_fn=precheck_fn,
                noise_floor=noise_floor,
                active_bar=active_bar,
                flat_rel=flat_rel,
                plateau_max_growth=plateau_max_growth,
                max_retries=max_retries,
            )
            if emitted:
                log_msg(
                    run_dir,
                    f"poll: {len(emitted)} checkpoint(s) processed: {[r['step'] for r in emitted]}",
                )
        except KeyboardInterrupt:
            log_msg(run_dir, "drift-watch stopped by signal")
            return 0
        except Exception as exc:
            # Never die on a transient failure (trainer untouched — read-only).
            log_msg(run_dir, f"poll error (continuing): {type(exc).__name__}: {exc}")
        try:
            time.sleep(poll_seconds)
        except KeyboardInterrupt:
            log_msg(run_dir, "drift-watch stopped by signal")
            return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="SAPO drift watch — alarm on zero-change/flat RL checkpoints "
        "(TIER-0 ZERO_CHANGE / TIER-1 FLAT_AT_NOISE_FLOOR / TIER-2 PLATEAU).",
    )
    ap.add_argument(
        "--run-dir", required=True, help="training run output dir (e.g. outputs/sapo-27b-ai-<ts>)"
    )
    ap.add_argument("--base", required=True, help="base model path on the box")
    ap.add_argument("--device", default="cpu", help="device for the merge (cpu)")
    ap.add_argument(
        "--poll",
        type=float,
        default=DEFAULT_POLL_SECONDS,
        help=f"watch poll interval in seconds (default {DEFAULT_POLL_SECONDS:g})",
    )
    ap.add_argument(
        "--once", action="store_true", help="check the newest checkpoint and exit (cron/manual)"
    )
    ap.add_argument(
        "--watch",
        action="store_true",
        help="watch-loop mode (default); explicit flag for launch scripts",
    )
    ap.add_argument(
        "--noise-floor",
        type=float,
        default=NOISE_FLOOR_DEFAULT,
        help=f"bf16 noise boundary (default {NOISE_FLOOR_DEFAULT:g})",
    )
    ap.add_argument(
        "--active-bar",
        type=float,
        default=ACTIVE_BAR_DEFAULT,
        help=f"ACTIVE bar (default {ACTIVE_BAR_DEFAULT:g})",
    )
    ap.add_argument(
        "--flat-rel",
        type=float,
        default=FLAT_REL_TOL_DEFAULT,
        help=f"relative change counting as 'unchanged' (default {FLAT_REL_TOL_DEFAULT:g})",
    )
    ap.add_argument(
        "--plateau-growth",
        type=float,
        default=PLATEAU_MAX_GROWTH_DEFAULT,
        help=f"growth below this = plateau (default {PLATEAU_MAX_GROWTH_DEFAULT:g})",
    )
    ap.add_argument(
        "--max-retries",
        type=int,
        default=MAX_RETRIES_DEFAULT,
        help=f"consecutive failures before an error record (default {MAX_RETRIES_DEFAULT})",
    )
    args = ap.parse_args(argv)
    if args.once:
        run_once(
            args.run_dir,
            args.base,
            device=args.device,
            noise_floor=args.noise_floor,
            active_bar=args.active_bar,
            flat_rel=args.flat_rel,
            plateau_max_growth=args.plateau_growth,
        )
        return 0
    return watch_loop(
        args.run_dir,
        args.base,
        poll_seconds=args.poll,
        device=args.device,
        noise_floor=args.noise_floor,
        active_bar=args.active_bar,
        flat_rel=args.flat_rel,
        plateau_max_growth=args.plateau_growth,
        max_retries=args.max_retries,
    )


if __name__ == "__main__":
    raise SystemExit(main())

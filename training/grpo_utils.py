from __future__ import annotations

import ast
import json
import math
import re
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch


def _build_grpo_metric_record(
    *,
    step: int,
    task: str,
    domain: str,
    mean_reward: float,
    reward_std: float,
    reward_signal_std: float,
    curriculum_prob: float,
    task_ema_reward: float,
    task_seen: int,
    skipped: bool,
    pass_rate: float | None = None,
    syntax_rate: float | None = None,
    interface_rate: float | None = None,
    verifier_rate: float | None = None,
    pass_std: float | None = None,
    syntax_std: float | None = None,
    interface_std: float | None = None,
    verifier_std: float | None = None,
    advantage_scale: float | None = None,
    reason: str | None = None,
    loss: float | None = None,
    adapter_init: str | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "step": step,
        "task": task,
        "domain": domain,
        "mean_reward": mean_reward,
        "reward_std": reward_std,
        "reward_signal_std": reward_signal_std,
        "curriculum_prob": curriculum_prob,
        "task_ema_reward": task_ema_reward,
        "task_seen": task_seen,
    }
    if skipped:
        record["skipped"] = True
    optional_fields = {
        "pass_rate": pass_rate,
        "syntax_rate": syntax_rate,
        "interface_rate": interface_rate,
        "verifier_rate": verifier_rate,
        "pass_std": pass_std,
        "syntax_std": syntax_std,
        "interface_std": interface_std,
        "verifier_std": verifier_std,
        "advantage_scale": advantage_scale,
        "reason": reason,
        "loss": loss,
        "adapter_init": adapter_init,
    }
    for key, value in optional_fields.items():
        if value is not None:
            record[key] = value
    return record


def append_grpo_metric(
    metrics: list[dict[str, Any]],
    record: Mapping[str, Any] | None = None,
    **record_kwargs: Any,
) -> dict[str, Any]:
    persisted = dict(record) if record is not None else _build_grpo_metric_record(**record_kwargs)
    metrics.append(persisted)
    return persisted


def append_grpo_metric_jsonl(path: Path, record: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(record), sort_keys=True) + "\n")


def load_grpo_step_metrics_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        records.append(json.loads(line))
    return records


def build_grpo_metrics_payload_from_jsonl(path: Path, *, planned_steps: int) -> dict[str, Any]:
    return build_grpo_metrics_payload(load_grpo_step_metrics_jsonl(path), planned_steps=planned_steps)


def build_grpo_step_record(
    *,
    step: int,
    task_name: str,
    domain: str,
    mean_reward: float,
    signal_stats: dict[str, float],
    pass_rate: float | None,
    syntax_rate: float | None,
    interface_rate: float | None,
    verifier_rate: float | None,
    task_prob: float,
    task_state: dict[str, float],
    advantage_scale: float | None = None,
    skipped: bool = False,
    reason: str | None = None,
    loss: float | None = None,
    adapter_init: str | None = None,
) -> dict[str, float | int | bool | str]:
    record: dict[str, float | int | bool | str] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "step": step,
        "task": task_name,
        "domain": domain,
        "mean_reward": mean_reward,
        "reward_std": float(signal_stats["reward_std"]),
        "reward_signal_std": float(signal_stats["signal_std"]),
        "curriculum_prob": task_prob,
        "task_ema_reward": float(task_state["ema_reward"]),
        "task_seen": int(task_state["seen"]),
    }
    if pass_rate is not None:
        record["pass_rate"] = pass_rate
    if syntax_rate is not None:
        record["syntax_rate"] = syntax_rate
    if interface_rate is not None:
        record["interface_rate"] = interface_rate
    if verifier_rate is not None:
        record["verifier_rate"] = verifier_rate
    if "pass_std" in signal_stats:
        record["pass_std"] = float(signal_stats["pass_std"])
    if "syntax_std" in signal_stats:
        record["syntax_std"] = float(signal_stats["syntax_std"])
    if "interface_std" in signal_stats:
        record["interface_std"] = float(signal_stats["interface_std"])
    if "verifier_std" in signal_stats:
        record["verifier_std"] = float(signal_stats["verifier_std"])
    if advantage_scale is not None:
        record["advantage_scale"] = advantage_scale
    if skipped:
        record["skipped"] = True
        if reason is not None:
            record["reason"] = reason
    if loss is not None:
        record["loss"] = loss
    if adapter_init is not None:
        record["adapter_init"] = adapter_init
    return record


def build_grpo_metrics_payload(records: list[dict[str, Any]], *, planned_steps: int) -> dict[str, Any]:
    skipped_records = [record for record in records if bool(record.get("skipped"))]
    skip_reasons = Counter(str(record.get("reason")) for record in skipped_records if record.get("reason"))
    updated_steps = sum(1 for record in records if not bool(record.get("skipped")))
    last_recorded_step = records[-1].get("step") if records else None
    return {
        "metrics": records,
        "summary": {
            "planned_steps": planned_steps,
            "recorded_steps": len(records),
            "updated_steps": updated_steps,
            "skipped_steps": len(skipped_records),
            "last_recorded_step": last_recorded_step,
            "skip_reasons": dict(sorted(skip_reasons.items())),
        },
    }


def build_grpo_metrics_payload_from_jsonl(path: Path, *, planned_steps: int) -> dict[str, Any]:
    return build_grpo_metrics_payload(load_grpo_step_metrics_jsonl(path), planned_steps=planned_steps)


def summarize_python_interface(source: str) -> list[str]:
    if not source.strip():
        return []
    try:
        tree = ast.parse(source)
    except Exception:
        return []

    lines: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            args: list[str] = []
            total_args = list(node.args.posonlyargs) + list(node.args.args)
            defaults = list(node.args.defaults)
            default_offset = len(total_args) - len(defaults)
            for index, arg in enumerate(total_args):
                arg_text = arg.arg
                if arg.annotation is not None:
                    arg_text += f": {ast.unparse(arg.annotation)}"
                if index >= default_offset:
                    arg_text += f" = {ast.unparse(defaults[index - default_offset])}"
                args.append(arg_text)
            if node.args.vararg is not None:
                args.append(f"*{node.args.vararg.arg}")
            if node.args.kwonlyargs:
                if node.args.vararg is None:
                    args.append("*")
                for kwarg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
                    kwarg_text = kwarg.arg
                    if kwarg.annotation is not None:
                        kwarg_text += f": {ast.unparse(kwarg.annotation)}"
                    if default is not None:
                        kwarg_text += f" = {ast.unparse(default)}"
                    args.append(kwarg_text)
            if node.args.kwarg is not None:
                args.append(f"**{node.args.kwarg.arg}")
            signature = f"{node.name}({', '.join(args)})"
            if node.returns is not None:
                signature += f" -> {ast.unparse(node.returns)}"
            lines.append(signature)
        elif isinstance(node, ast.ClassDef):
            lines.append(f"class {node.name}")
    return lines


def estimate_detail_budget(test_source: str, cap: int = 8) -> int:
    if not test_source.strip():
        return 1
    count = 0
    for raw_line in test_source.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# Test "):
            count += 1
            continue
        if "failures.append(" in line or "details.append(" in line:
            count += 1
    return max(1, min(cap, count or 1))


def _normalize_signature(signature: str) -> str:
    return re.sub(r"\s+", "", signature.strip().lower())


def _extract_symbol_name(signature: str) -> str:
    text = signature.strip()
    if text.startswith("class "):
        return text[len("class "):].split("(", 1)[0].split(":", 1)[0].strip().lower()
    return text.split("(", 1)[0].strip().lower()


def interface_match_score(required_interface: list[str], candidate_interface: list[str]) -> float:
    if not required_interface:
        return 1.0
    if not candidate_interface:
        return 0.0

    required_exact = {_normalize_signature(line) for line in required_interface}
    candidate_exact = {_normalize_signature(line) for line in candidate_interface}
    required_names = {_extract_symbol_name(line) for line in required_interface}
    candidate_names = {_extract_symbol_name(line) for line in candidate_interface}

    exact_overlap = len(required_exact & candidate_exact) / max(1, len(required_exact))
    name_overlap = len(required_names & candidate_names) / max(1, len(required_names))
    return 0.5 * exact_overlap + 0.5 * name_overlap


def _safe_details(result: dict | None) -> list[str]:
    if not isinstance(result, dict):
        return []
    raw_details = result.get("details") or []
    if not isinstance(raw_details, list):
        raw_details = [raw_details]
    details: list[str] = []
    for item in raw_details:
        text = str(item).strip()
        if text:
            details.append(text)
    return details


def brevity_reward(code: str, target_lines: int = 40) -> float:
    """Reward concise solutions: 1.0 at target_lines, decaying for longer code.

    This creates within-group variance even when all completions fail tests,
    breaking the flat-reward deadlock that causes GRPO steps to be skipped.
    """
    lines = code.strip().splitlines()
    n = len(lines)
    if n == 0:
        return 0.0
    if n <= target_lines:
        return 1.0
    # Smooth decay: halves reward every target_lines lines over the target
    return max(0.0, math.exp(-0.7 * (n - target_lines) / max(target_lines, 1)))


def build_reward_breakdown(
    *,
    code: str,
    result: dict | None,
    required_interface: list[str],
    detail_budget: int,
    pass_weight: float,
    syntax_weight: float,
    interface_weight: float,
    verifier_weight: float,
    brevity_weight: float = 0.0,
    brevity_target_lines: int = 40,
) -> dict[str, float | int | bool]:
    syntax_ok = False
    if code.strip():
        try:
            ast.parse(code)
            syntax_ok = True
        except Exception:
            syntax_ok = False

    candidate_interface = summarize_python_interface(code) if syntax_ok else []
    interface_reward = interface_match_score(required_interface, candidate_interface) if syntax_ok else 0.0

    passed = bool(result.get("passed")) if isinstance(result, dict) else False
    details = _safe_details(result)
    failure_count = 0 if passed else max(1, len(details))
    capped_budget = max(1, detail_budget)
    verifier_reward = 1.0 if passed else max(0.0, 1.0 - min(failure_count, capped_budget) / capped_budget)
    pass_reward = 1.0 if passed else 0.0
    syntax_reward = 1.0 if syntax_ok else 0.0
    brevity_score = brevity_reward(code, target_lines=brevity_target_lines) if syntax_ok else 0.0

    weight_sum = pass_weight + syntax_weight + interface_weight + verifier_weight + brevity_weight
    total_reward = (
        pass_weight * pass_reward
        + syntax_weight * syntax_reward
        + interface_weight * interface_reward
        + verifier_weight * verifier_reward
        + brevity_weight * brevity_score
    ) / max(weight_sum, 1e-8)

    return {
        "passed": passed,
        "pass_reward": pass_reward,
        "syntax_reward": syntax_reward,
        "interface_reward": interface_reward,
        "verifier_reward": verifier_reward,
        "brevity_reward": brevity_score,
        "failure_count": failure_count,
        "detail_budget": capped_budget,
        "total_reward": total_reward,
    }


@dataclass
class TaskCurriculum:
    ema_decay: float = 0.9
    min_weight: float = 0.05
    quantum_priority: float = 1.5
    uncertainty_bonus: float = 0.35
    state: dict[str, dict[str, float]] = field(default_factory=dict)

    def get_state(self, task_id: str) -> dict[str, float]:
        current = self.state.get(task_id)
        if current is None:
            current = {"ema_reward": 0.0, "seen": 0.0}
            self.state[task_id] = current
        return current

    def weight(self, task_id: str, domain: str | None) -> float:
        current = self.get_state(task_id)
        ema_reward = float(current["ema_reward"])
        seen = float(current["seen"])
        difficulty = max(0.05, 1.0 - ema_reward)
        uncertainty = self.uncertainty_bonus / math.sqrt(seen + 1.0)
        domain_scale = self.quantum_priority if domain == "quantum" else 1.0
        return max(self.min_weight, domain_scale * (difficulty + uncertainty))

    def record(self, task_id: str, observed_reward: float) -> dict[str, float]:
        current = self.get_state(task_id)
        ema_reward = float(current["ema_reward"])
        seen = float(current["seen"]) + 1.0
        updated = self.ema_decay * ema_reward + (1.0 - self.ema_decay) * observed_reward
        current["ema_reward"] = updated
        current["seen"] = seen
        return current


def stable_grpo_loss(
    log_probs: torch.Tensor,
    old_log_probs: torch.Tensor,
    advantages: torch.Tensor,
    kl_coeff: float,
    ratio_clip_log_delta: float,
) -> torch.Tensor:
    finite_mask = torch.isfinite(log_probs) & torch.isfinite(old_log_probs) & torch.isfinite(advantages)
    if not finite_mask.any():
        return log_probs.new_tensor(float("nan"))

    safe_log_probs = log_probs[finite_mask]
    safe_old_log_probs = old_log_probs[finite_mask].detach()
    safe_advantages = advantages[finite_mask].detach()

    log_ratio = (safe_log_probs - safe_old_log_probs).clamp(
        -ratio_clip_log_delta,
        ratio_clip_log_delta,
    )
    ratio = torch.exp(log_ratio)
    pg_loss = -(ratio * safe_advantages).mean()

    kl = (safe_old_log_probs - safe_log_probs).clamp(
        -ratio_clip_log_delta,
        ratio_clip_log_delta,
    ).mean()
    total = pg_loss + kl_coeff * kl
    if not torch.isfinite(total):
        return log_probs.new_tensor(float("nan"))
    return total


def stable_token_log_probs(
    logits: torch.Tensor,
    target_ids: torch.Tensor,
    logit_clip: float,
) -> torch.Tensor:
    safe_logits = torch.nan_to_num(
        logits.float(),
        nan=0.0,
        posinf=logit_clip,
        neginf=-logit_clip,
    ).clamp(-logit_clip, logit_clip)
    safe_targets = target_ids.long()
    log_probs = torch.log_softmax(safe_logits, dim=-1)
    vocab_size = log_probs.shape[-1]
    flat_log_probs = log_probs.reshape(-1, vocab_size)
    flat_targets = safe_targets.reshape(-1, 1)
    flat_selected = flat_log_probs.gather(1, flat_targets)
    return flat_selected.reshape(safe_targets.shape)


def reward_signal_stats(
    rewards: torch.Tensor,
    pass_rewards: torch.Tensor,
    syntax_rewards: torch.Tensor,
    interface_rewards: torch.Tensor,
    verifier_rewards: torch.Tensor,
    brevity_rewards: torch.Tensor | None = None,
) -> dict[str, float]:
    reward_std = float(rewards.std(unbiased=False).item())
    pass_std = float(pass_rewards.std(unbiased=False).item())
    syntax_std = float(syntax_rewards.std(unbiased=False).item())
    interface_std = float(interface_rewards.std(unbiased=False).item())
    verifier_std = float(verifier_rewards.std(unbiased=False).item())
    brevity_std = float(brevity_rewards.std(unbiased=False).item()) if brevity_rewards is not None else 0.0
    signal_std = max(reward_std, pass_std, syntax_std, interface_std, verifier_std, brevity_std)
    result = {
        "reward_std": reward_std,
        "pass_std": pass_std,
        "syntax_std": syntax_std,
        "interface_std": interface_std,
        "verifier_std": verifier_std,
        "signal_std": signal_std,
    }
    if brevity_rewards is not None:
        result["brevity_std"] = brevity_std
    return result


# ---------------------------------------------------------------------------
# Adaptive temperature escalation
# ---------------------------------------------------------------------------

@dataclass
class AdaptiveTemperatureState:
    """Tracks consecutive low-reward-signal skips and escalates sampling temperature.

    When all completions in a group score similarly (reward_std < min_reward_std),
    GRPO steps are skipped.  Raising sampling temperature forces more diverse
    completions in the next step, increasing the chance of at least one correct
    answer and breaking the flat-reward deadlock.

    Temperature formula:
        current_temp = min(base_temp * (1 + step_size * consecutive_skips), max_temp)

    Temperature resets to base_temp after any successful gradient update.
    """

    base_temp: float = 0.8
    step_size: float = 0.15
    max_temp: float = 1.4
    consecutive_low_signal_skips: int = 0

    _LOW_SIGNAL_REASON: str = "low_reward_signal"

    def current_temp_at_count(self, count: int) -> float:
        """Return the escalated temperature for a given consecutive-skip count."""
        raw = self.base_temp * (1.0 + self.step_size * count)
        return min(raw, self.max_temp)

    def current_temp(self) -> float:
        """Return the effective sampling temperature given the current skip count."""
        return self.current_temp_at_count(self.consecutive_low_signal_skips)

    def record_skip(self, reason: str) -> None:
        """Update state after a skipped GRPO step.

        Only increments the escalation counter for *low_reward_signal* skips.
        Other skip reasons (empty mask, non-finite loss) do not indicate a
        temperature-diversity problem and should not escalate sampling.
        """
        if reason == self._LOW_SIGNAL_REASON:
            self.consecutive_low_signal_skips += 1

    def record_update(self) -> None:
        """Reset the escalation counter after a successful gradient update."""
        self.consecutive_low_signal_skips = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "base_temp": self.base_temp,
            "step_size": self.step_size,
            "max_temp": self.max_temp,
            "consecutive_low_signal_skips": self.consecutive_low_signal_skips,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AdaptiveTemperatureState":
        return cls(
            base_temp=float(data.get("base_temp", 0.8)),
            step_size=float(data.get("step_size", 0.15)),
            max_temp=float(data.get("max_temp", 1.4)),
            consecutive_low_signal_skips=int(data.get("consecutive_low_signal_skips", 0)),
        )

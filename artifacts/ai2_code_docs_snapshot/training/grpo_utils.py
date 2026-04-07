from __future__ import annotations

import ast
import math
import re
from dataclasses import dataclass, field

import torch


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

    weight_sum = pass_weight + syntax_weight + interface_weight + verifier_weight
    total_reward = (
        pass_weight * pass_reward
        + syntax_weight * syntax_reward
        + interface_weight * interface_reward
        + verifier_weight * verifier_reward
    ) / max(weight_sum, 1e-8)

    return {
        "passed": passed,
        "pass_reward": pass_reward,
        "syntax_reward": syntax_reward,
        "interface_reward": interface_reward,
        "verifier_reward": verifier_reward,
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

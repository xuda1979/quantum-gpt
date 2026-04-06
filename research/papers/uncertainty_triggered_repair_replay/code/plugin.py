from __future__ import annotations

from typing import Any

from training.research_plugins import BaseResearchMethod, merge_reward_overrides


def _stage_is_training(stage: str) -> bool:
    return stage in {"sft", "sft_train", "grpo"}


def _metadata(task: dict[str, Any]) -> dict[str, Any]:
    meta = task.get("metadata")
    if isinstance(meta, dict):
        return meta
    return task


def _numeric(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bounded(value: float, *, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def _difficulty_score(meta: dict[str, Any]) -> float:
    difficulty_map = {
        "easy": 0.1,
        "medium": 0.45,
        "hard": 0.8,
        "extreme": 1.0,
    }
    score = difficulty_map.get(str(meta.get("difficulty", "")).lower(), 0.35)

    category = str(meta.get("category", "")).lower()
    if category in {"debug_repair", "multifile_repair", "stateful_logic", "test_writing"}:
        score += 0.15
    elif category in {"algorithm_implementation", "circuit_optimization", "api_normalization"}:
        score += 0.08

    prompt_family = str(meta.get("prompt_family", "")).lower()
    if prompt_family in {"acceptance_gate", "audit_followup", "maintainer_check", "spec_translation"}:
        score += 0.05

    return _bounded(score)


def _structural_uncertainty(task: dict[str, Any]) -> float:
    meta = _metadata(task)
    required_interface = task.get("required_interface") or []
    behavior_hints = task.get("behavior_hints") or []
    detail_budget = _numeric(task.get("detail_budget"), 1.0)

    score = 0.0
    if len(required_interface) >= 2:
        score += 0.12
    elif len(required_interface) == 1:
        score += 0.05

    if len(behavior_hints) >= 4:
        score += 0.18
    elif len(behavior_hints) >= 2:
        score += 0.1

    if detail_budget >= 5:
        score += 0.12
    elif detail_budget >= 3:
        score += 0.06

    if meta.get("candidate_file") or meta.get("candidate_files"):
        score += 0.05

    return _bounded(score)


def _explicit_uncertainty(meta: dict[str, Any]) -> float:
    direct_fields = (
        "uncertainty",
        "uncertainty_score",
        "hardness",
        "hardness_score",
        "difficulty_score",
        "failure_rate",
        "replay_count",
        "attempt_count",
    )
    values = [_numeric(meta.get(name), 0.0) for name in direct_fields if meta.get(name) is not None]
    if not values:
        return 0.0
    return _bounded(max(values))


def _hardness(task: dict[str, Any]) -> float:
    meta = _metadata(task)
    score = max(
        _difficulty_score(meta),
        _structural_uncertainty(task),
        _explicit_uncertainty(meta),
    )
    return _bounded(score)


def _repair_prompt(hardness: float) -> str:
    if hardness >= 0.8:
        level = "high"
    elif hardness >= 0.5:
        level = "moderate"
    else:
        level = "light"

    return (
        f"Uncertainty-triggered repair replay ({level} hardness):\n"
        "- Preserve the requested interface.\n"
        "- Make the smallest change that can pass tests.\n"
        "- If multiple fixes are possible, choose the simplest one that is stable.\n"
        "- Do not add extra abstraction unless the task clearly needs it."
    )


class UncertaintyTriggeredRepairReplayMethod(BaseResearchMethod):
    method_id = "uncertainty_triggered_repair_replay"
    paper_title = "Uncertainty-Triggered Repair Replay for SFT and GRPO"

    def augment_sft_record(self, record: dict[str, Any], *, stage: str) -> dict[str, Any]:
        if not _stage_is_training(stage):
            return record

        meta = _metadata(record)
        hardness = _hardness(record)
        if hardness < 0.45:
            return record

        messages = list(record.get("messages") or [])
        if not messages:
            return record

        system_message = {"role": "system", "content": _repair_prompt(hardness)}
        if messages[0].get("role") != "system":
            messages.insert(0, system_message)
        else:
            messages[0] = {
                **messages[0],
                "content": str(messages[0].get("content", "")) + "\n\n" + system_message["content"],
            }

        record["messages"] = messages
        record["uncertainty_triggered_replay"] = {
            "hardness": hardness,
            "task_id": meta.get("task_id"),
            "prompt_family": meta.get("prompt_family"),
        }
        return record

    def augment_grpo_prompt(self, prompt: str, *, task: dict[str, Any], stage: str) -> str:
        if stage != "grpo":
            return prompt

        hardness = _hardness(task)
        if hardness < 0.35:
            return prompt

        extra = _repair_prompt(hardness)
        if hardness >= 0.7:
            extra += (
                "\n- Treat the first valid repair as the default replay target.\n"
                "- Spend extra effort on near-miss failures that are structurally close to the reference."
            )
        return prompt + "\n\n" + extra

    def adjust_task_weight(self, weight: float, *, task: dict[str, Any], stage: str) -> float:
        if stage != "grpo":
            return weight

        hardness = _hardness(task)
        if hardness < 0.25:
            return weight

        replay_boost = 1.0 + 0.65 * hardness
        if _numeric(task.get("detail_budget"), 1.0) >= 4:
            replay_boost += 0.05
        if len(task.get("behavior_hints") or []) >= 3:
            replay_boost += 0.05
        return weight * replay_boost

    def adjust_reward_breakdown(
        self,
        reward: dict[str, Any],
        *,
        code: str,
        result: dict[str, Any] | None,
        task: dict[str, Any],
        stage: str,
    ) -> dict[str, Any]:
        if stage != "grpo":
            return reward

        hardness = _hardness(task)
        if hardness < 0.35:
            return reward

        passed = bool(result.get("passed")) if isinstance(result, dict) else False
        syntax_reward = float(reward.get("syntax_reward", 0.0))
        interface_reward = float(reward.get("interface_reward", 0.0))
        verifier_reward = float(reward.get("verifier_reward", 0.0))
        near_miss_signal = 0.5 * syntax_reward + 0.35 * interface_reward + 0.15 * verifier_reward
        replay_credit = hardness * near_miss_signal * (0.04 if passed else 0.12)
        total_reward = min(1.0, float(reward.get("total_reward", 0.0)) + replay_credit)
        return merge_reward_overrides(
            reward,
            {
                "uncertainty_replay_credit": replay_credit,
                "total_reward": total_reward,
            },
        )

    def extra_run_config(self) -> dict[str, Any]:
        return {
            "hardness_threshold_sft": 0.45,
            "hardness_threshold_grpo": 0.35,
            "repair_prompt_policy": "preserve-interface-minimal-repair",
            "task_weight_boost_max": 1.65,
            "near_miss_reward_credit_max": 0.12,
        }


def build_method() -> UncertaintyTriggeredRepairReplayMethod:
    return UncertaintyTriggeredRepairReplayMethod()

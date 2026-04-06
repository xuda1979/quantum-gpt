from __future__ import annotations

from typing import Any

from training.research_plugins import BaseResearchMethod, merge_reward_overrides


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class SelfConsistencyVerifierRoutingMethod(BaseResearchMethod):
    method_id = "self_consistency_verifier_routing"
    paper_title = "Self-Consistency Verifier Routing for Code SFT and GRPO"

    def augment_sft_record(self, record: dict[str, Any], *, stage: str) -> dict[str, Any]:
        messages = list(record.get("messages") or [])
        if not messages:
            return record
        system_message = {
            "role": "system",
            "content": (
                "Before answering, compare a few candidate implementations mentally and choose the one "
                "most likely to satisfy tests, preserve the required interface, and avoid syntax errors. "
                "Return only the final selected solution."
            ),
        }
        if messages[0].get("role") == "system":
            messages[0] = {
                "role": "system",
                "content": str(messages[0].get("content", "")).strip() + "\n\n" + system_message["content"],
            }
        else:
            messages.insert(0, system_message)
        record["messages"] = messages
        return record

    def augment_grpo_prompt(self, prompt: str, *, task: dict[str, Any], stage: str) -> str:
        routing_hint = (
            "Self-consistency routing:\n"
            "- Consider multiple candidate implementations mentally before writing code.\n"
            "- Prefer the candidate most likely to pass the verifier on the first try.\n"
            "- Break ties in favor of correct interface shape, simpler control flow, and fewer moving parts.\n"
            "- Return only the final selected Python code."
        )
        return prompt + "\n\n" + routing_hint

    def adjust_task_weight(self, weight: float, *, task: dict[str, Any], stage: str) -> float:
        behavior_hints = len(task.get("behavior_hints") or [])
        interface_lines = len(task.get("required_interface") or [])
        if behavior_hints >= 3 or interface_lines >= 2:
            return weight * 1.1
        return weight

    def adjust_reward_breakdown(
        self,
        reward: dict[str, Any],
        *,
        code: str,
        result: dict[str, Any] | None,
        task: dict[str, Any],
        stage: str,
    ) -> dict[str, Any]:
        pass_reward = _as_float(reward.get("pass_reward"))
        syntax_reward = _as_float(reward.get("syntax_reward"))
        interface_reward = _as_float(reward.get("interface_reward"))
        verifier_reward = _as_float(reward.get("verifier_reward"))
        base_total = _as_float(reward.get("total_reward"))

        consistency_score = (
            0.4 * verifier_reward
            + 0.25 * interface_reward
            + 0.2 * syntax_reward
            + 0.15 * pass_reward
        )
        routing_bonus = 0.08 * consistency_score
        blended_total = min(1.0, 0.92 * base_total + routing_bonus)

        return merge_reward_overrides(
            reward,
            {
                "self_consistency_score": consistency_score,
                "self_consistency_routing_bonus": routing_bonus,
                "total_reward": blended_total,
            },
        )

    def extra_run_config(self) -> dict[str, Any]:
        return {
            "self_consistency_routing": {
                "enabled": True,
                "reward_blend": {
                    "verifier": 0.4,
                    "interface": 0.25,
                    "syntax": 0.2,
                    "pass": 0.15,
                },
                "total_reward_mix": {
                    "base_total": 0.92,
                    "routing_bonus_scale": 0.08,
                },
            }
        }


def build_method() -> SelfConsistencyVerifierRoutingMethod:
    return SelfConsistencyVerifierRoutingMethod()

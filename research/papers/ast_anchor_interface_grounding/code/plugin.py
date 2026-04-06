from __future__ import annotations

from typing import Any

from training.research_plugins import BaseResearchMethod, merge_reward_overrides


class AstAnchorInterfaceGroundingMethod(BaseResearchMethod):
    method_id = "ast_anchor_interface_grounding"
    paper_title = "AST-Anchor Reranking for Interface-Grounded Code Synthesis"

    def augment_grpo_prompt(self, prompt: str, *, task: dict[str, Any], stage: str) -> str:
        required_interface = task.get("required_interface") or []
        if not required_interface:
            return prompt
        emphasis = (
            "Interface grounding:\n"
            "Match the required exported symbols and signatures exactly before optimizing secondary details."
        )
        return prompt + "\n\n" + emphasis

    def adjust_task_weight(self, weight: float, *, task: dict[str, Any], stage: str) -> float:
        if task.get("required_interface"):
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
        syntax_reward = float(reward.get("syntax_reward", 0.0))
        interface_reward = float(reward.get("interface_reward", 0.0))
        total_reward = float(reward.get("total_reward", 0.0))
        boost = 0.05 * syntax_reward * interface_reward
        return merge_reward_overrides(
            reward,
            {
                "interface_anchor_bonus": boost,
                "total_reward": min(1.0, total_reward + boost),
            },
        )


def build_method() -> AstAnchorInterfaceGroundingMethod:
    return AstAnchorInterfaceGroundingMethod()

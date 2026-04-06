from __future__ import annotations

import re
from typing import Any

from training.research_plugins import BaseResearchMethod, merge_reward_overrides

_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "into",
    "must",
    "that",
    "this",
    "then",
    "when",
    "return",
    "returns",
    "value",
    "values",
    "should",
    "using",
    "write",
    "final",
    "preserve",
    "requested",
    "required",
    "python",
    "code",
    "file",
    "tests",
    "test",
    "candidate",
    "function",
    "class",
}


def _split_identifier(token: str) -> list[str]:
    pieces = re.split(r"[_\W]+", token)
    expanded: list[str] = []
    for piece in pieces:
        if not piece:
            continue
        camel_parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|\d+", piece)
        expanded.extend(camel_parts or [piece])
    return expanded


def _tokens(text: str) -> set[str]:
    raw = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text)
    result: set[str] = set()
    for item in raw:
        for piece in _split_identifier(item):
            normalized = piece.strip().lower()
            if len(normalized) < 3 or normalized in _STOPWORDS:
                continue
            result.add(normalized)
    return result


def _interface_name_tokens(required_interface: list[str]) -> set[str]:
    names: set[str] = set()
    for line in required_interface:
        text = str(line).strip()
        if not text:
            continue
        if text.startswith("class "):
            name = text[len("class "):].split("(", 1)[0].split(":", 1)[0].strip()
        else:
            name = text.split("(", 1)[0].strip()
        names.update(_tokens(name))
    return names


def _behavior_anchor_tokens(task: dict[str, Any]) -> set[str]:
    behavior_hints = task.get("behavior_hints") or []
    anchors: set[str] = set()
    for hint in behavior_hints:
        anchors.update(_tokens(str(hint)))
    interface_tokens = _interface_name_tokens(task.get("required_interface") or [])
    if interface_tokens:
        anchors.update(interface_tokens)
    return anchors


class BehaviorAnchorCoverageRewardMethod(BaseResearchMethod):
    method_id = "behavior_anchor_coverage_reward"
    paper_title = "Behavior-Anchor Coverage Reward for Low-Signal Code GRPO"

    def augment_grpo_prompt(self, prompt: str, *, task: dict[str, Any], stage: str) -> str:
        anchors = sorted(_behavior_anchor_tokens(task))
        if not anchors:
            return prompt
        preview = ", ".join(anchors[:8])
        extra = (
            "Behavior-anchor coverage:\n"
            "- Keep the key operational anchors from the task visible in the solution.\n"
            "- Prefer code that reflects the intended behavioral vocabulary, not just the outer signature.\n"
            f"- Important anchors: {preview}"
        )
        return prompt + "\n\n" + extra

    def adjust_task_weight(self, weight: float, *, task: dict[str, Any], stage: str) -> float:
        anchors = _behavior_anchor_tokens(task)
        if len(anchors) >= 8:
            return weight * 1.1
        if len(anchors) >= 4:
            return weight * 1.05
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
        anchors = _behavior_anchor_tokens(task)
        if not anchors:
            return reward

        code_tokens = _tokens(code)
        coverage = len(anchors & code_tokens) / max(len(anchors), 1)
        base_total = float(reward.get("total_reward", 0.0))
        bonus = 0.08 * coverage
        blended_total = min(1.0, 0.94 * base_total + bonus)

        return merge_reward_overrides(
            reward,
            {
                "behavior_anchor_reward": coverage,
                "behavior_anchor_bonus": bonus,
                "total_reward": blended_total,
            },
        )

    def extra_run_config(self) -> dict[str, Any]:
        return {
            "behavior_anchor_coverage_reward": {
                "enabled": True,
                "task_weight_boost": {
                    "rich_anchor_threshold": 8,
                    "medium_anchor_threshold": 4,
                    "rich_anchor_scale": 1.1,
                    "medium_anchor_scale": 1.05,
                },
                "reward_blend": {
                    "base_total": 0.94,
                    "anchor_bonus_scale": 0.08,
                },
            }
        }


def build_method() -> BehaviorAnchorCoverageRewardMethod:
    return BehaviorAnchorCoverageRewardMethod()

from __future__ import annotations

import re
from typing import Any

from training.research_plugins import BaseResearchMethod, merge_reward_overrides


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z_]+", text.lower()) if len(token) >= 4}


class ClauseAwareVerifierRewardMethod(BaseResearchMethod):
    method_id = "clause_aware_verifier_reward"
    paper_title = "Clause-Aware Verifier Reward for Code RL"

    def adjust_reward_breakdown(
        self,
        reward: dict[str, Any],
        *,
        code: str,
        result: dict[str, Any] | None,
        task: dict[str, Any],
        stage: str,
    ) -> dict[str, Any]:
        behavior_hints = task.get("behavior_hints") or []
        if not behavior_hints:
            return reward

        details = result.get("details", []) if isinstance(result, dict) else []
        detail_tokens = _tokens(" ".join(str(item) for item in details))
        satisfied = 0
        for hint in behavior_hints:
            hint_tokens = _tokens(str(hint))
            if not hint_tokens or hint_tokens.isdisjoint(detail_tokens):
                satisfied += 1
        clause_reward = satisfied / max(len(behavior_hints), 1)
        blended_total = 0.9 * float(reward["total_reward"]) + 0.1 * clause_reward
        return merge_reward_overrides(
            reward,
            {
                "clause_reward": clause_reward,
                "total_reward": blended_total,
            },
        )


def build_method() -> ClauseAwareVerifierRewardMethod:
    return ClauseAwareVerifierRewardMethod()

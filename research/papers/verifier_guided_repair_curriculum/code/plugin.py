from __future__ import annotations

from typing import Any

from training.research_plugins import BaseResearchMethod


class VerifierGuidedRepairCurriculumMethod(BaseResearchMethod):
    method_id = "verifier_guided_repair_curriculum"
    paper_title = "Verifier-Guided Near-Miss Repair Curriculum for Quantum Code Generalization"

    def augment_sft_record(self, record: dict[str, Any], *, stage: str) -> dict[str, Any]:
        messages = list(record.get("messages") or [])
        if not messages:
            return record
        prefix = {
            "role": "system",
            "content": (
                "Favor minimal repairs that preserve the required interface. "
                "When multiple implementations are possible, keep the smallest correct fix."
            ),
        }
        if messages[0].get("role") != "system":
            messages.insert(0, prefix)
        record["messages"] = messages
        return record

    def augment_grpo_prompt(self, prompt: str, *, task: dict[str, Any], stage: str) -> str:
        extra = (
            "Repair-first policy:\n"
            "- Preserve the requested function/class interface.\n"
            "- Fix the smallest failing behavior before adding extra structure.\n"
            "- Prefer simple code that is easy for tests to validate."
        )
        return prompt + "\n\n" + extra

    def adjust_task_weight(self, weight: float, *, task: dict[str, Any], stage: str) -> float:
        behavior_hint_count = len(task.get("behavior_hints") or [])
        detail_budget = int(task.get("detail_budget") or 1)
        if behavior_hint_count >= 3 or detail_budget >= 4:
            return weight * 1.15
        return weight


def build_method() -> VerifierGuidedRepairCurriculumMethod:
    return VerifierGuidedRepairCurriculumMethod()

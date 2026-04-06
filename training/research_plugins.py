from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PAPERS_ROOT = ROOT / "research" / "papers"


class BaseResearchMethod:
    method_id = "base"
    paper_title = "Base Research Method"

    def augment_sft_record(self, record: dict[str, Any], *, stage: str) -> dict[str, Any]:
        return record

    def augment_grpo_prompt(self, prompt: str, *, task: dict[str, Any], stage: str) -> str:
        return prompt

    def adjust_task_weight(self, weight: float, *, task: dict[str, Any], stage: str) -> float:
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
        return reward

    def extra_run_config(self) -> dict[str, Any]:
        return {}

    def summary(self) -> dict[str, Any]:
        return {
            "method_id": self.method_id,
            "paper_title": self.paper_title,
            "extra_run_config": self.extra_run_config(),
        }


def clone_record(record: dict[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(record)


def merge_reward_overrides(base_reward: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base_reward)
    merged.update(overrides)
    return merged


def load_research_methods(method_names: list[str] | None) -> list[BaseResearchMethod]:
    loaded: list[BaseResearchMethod] = []
    for method_name in method_names or []:
        plugin_path = PAPERS_ROOT / method_name / "code" / "plugin.py"
        if not plugin_path.exists():
            raise FileNotFoundError(f"Research method plugin not found: {plugin_path}")
        module_name = f"research_plugin_{method_name}"
        spec = importlib.util.spec_from_file_location(module_name, plugin_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Unable to load research method plugin spec: {plugin_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "build_method"):
            instance = module.build_method()
        elif hasattr(module, "METHOD"):
            instance = module.METHOD
        else:
            raise AttributeError(
                f"Research method plugin must expose build_method() or METHOD: {plugin_path}"
            )
        if not isinstance(instance, BaseResearchMethod):
            raise TypeError(
                f"Research method plugin returned {type(instance).__name__}, "
                f"expected BaseResearchMethod: {plugin_path}"
            )
        loaded.append(instance)
    return loaded


def summarize_methods(methods: list[BaseResearchMethod]) -> list[dict[str, Any]]:
    return [method.summary() for method in methods]


def write_methods_manifest(path: Path, methods: list[BaseResearchMethod]) -> None:
    payload = {"methods": summarize_methods(methods)}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

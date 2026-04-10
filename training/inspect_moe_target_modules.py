#!/usr/bin/env python3
"""Inspect router/expert module names for a local checkpoint.

This helper exists for MoE weekend-demo work:
- load a local checkpoint with the first compatible transformers auto class
- list module names that look like routers / gates / experts
- summarize suffix frequencies so LoRA / ESFT target selection is evidence-based
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from typing import Any


DEFAULT_KEYWORDS = ["router", "gate", "expert", "moe"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-name", required=True, help="Local model path or HF id")
    parser.add_argument(
        "--keywords",
        nargs="*",
        default=DEFAULT_KEYWORDS,
        help="Case-insensitive substrings used to flag MoE-related modules.",
    )
    parser.add_argument("--max-hits", type=int, default=200)
    parser.add_argument("--out", help="Optional JSON output path.")
    parser.add_argument("--manifest-out", help="Optional JSON output path for a full-name router/expert target manifest.")
    parser.add_argument(
        "--first-pass-expert-budget",
        type=int,
        default=8,
        help="Suggested expert-budget ceiling for the first ESFT pass after routing evidence is collected.",
    )
    parser.add_argument(
        "--max-router-modules",
        type=int,
        default=32,
        help="Maximum number of router/gate modules to include in the exact-name regex manifest.",
    )
    return parser.parse_args()


def module_parameter_count(module: Any) -> int:
    parameter_iter = getattr(module, "parameters", None)
    if parameter_iter is None:
        return 0
    try:
        return int(sum(int(parameter.numel()) for parameter in module.parameters(recurse=False)))
    except TypeError:
        return int(sum(int(parameter.numel()) for parameter in module.parameters()))


def extract_expert_index(module_name: str) -> str | None:
    match = re.search(r"(?:^|\.)(?:experts?|expert_layers?)\.(\d+)(?:\.|$)", module_name)
    if match:
        return match.group(1)
    return None


def try_load_model(model_name: str) -> tuple[Any, str]:
    from transformers import AutoModel, AutoModelForCausalLM

    candidates: list[tuple[str, Any]] = [
        ("AutoModelForCausalLM", AutoModelForCausalLM),
        ("AutoModel", AutoModel),
    ]

    try:
        from transformers import AutoModelForImageTextToText  # type: ignore[attr-defined]

        candidates.insert(0, ("AutoModelForImageTextToText", AutoModelForImageTextToText))
    except Exception:
        pass

    errors: list[str] = []
    for loader_name, loader_cls in candidates:
        try:
            model = loader_cls.from_pretrained(
                model_name,
                trust_remote_code=True,
                low_cpu_mem_usage=True,
                torch_dtype="auto",
            )
            return model, loader_name
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{loader_name}: {type(exc).__name__}: {exc}")
    raise SystemExit("Unable to load model for module inspection. " + " | ".join(errors))


def build_target_manifest(
    model_name: str,
    matched_details: list[dict[str, Any]],
    *,
    first_pass_expert_budget: int = 8,
    max_router_modules: int = 32,
) -> dict[str, Any]:
    router_module_names: list[str] = []
    expert_module_names_by_index: dict[str, list[str]] = {}

    for detail in matched_details:
        module_name = str(detail["module_name"])
        keyword_hits = [str(hit).lower() for hit in detail.get("keyword_hits", [])]
        expert_index = detail.get("expert_index")
        if any(hit in {"router", "gate"} for hit in keyword_hits):
            router_module_names.append(module_name)
        if expert_index is not None:
            expert_module_names_by_index.setdefault(str(expert_index), []).append(module_name)

    router_module_names = list(dict.fromkeys(router_module_names))
    for expert_index, module_names in expert_module_names_by_index.items():
        expert_module_names_by_index[expert_index] = sorted(dict.fromkeys(module_names))

    expert_index_pool = sorted(
        expert_module_names_by_index,
        key=lambda item: int(item) if item.isdigit() else item,
    )
    router_target_module_regex = [
        f"^{re.escape(module_name)}$" for module_name in router_module_names[:max_router_modules]
    ]

    return {
        "model_name": model_name,
        "selection_mode": "structural-discovery-only",
        "strategy": "router_warmup_then_frequency_guided_esft",
        "notes": [
            "Router modules are recorded with exact full names so the first LoRA router warmup is reproducible.",
            "Expert modules are grouped by expert index, but no expert is structurally preferred before routing-frequency evidence exists.",
            "Use routing-frequency evidence from the router-warmup phase to choose the first-pass expert subset.",
        ],
        "router_module_names": router_module_names,
        "router_target_module_regex": router_target_module_regex,
        "expert_index_pool": expert_index_pool,
        "first_pass_expert_budget": max(1, int(first_pass_expert_budget)),
        "expert_module_names_by_index": expert_module_names_by_index,
    }


def main() -> int:
    args = parse_args()
    normalized_keywords = [keyword.lower() for keyword in args.keywords]
    model, loader_name = try_load_model(args.model_name)

    matched_names: list[str] = []
    matched_details: list[dict[str, Any]] = []
    suffix_counter: Counter[str] = Counter()
    keyword_counter: Counter[str] = Counter()
    expert_index_counter: Counter[str] = Counter()

    for module_name, _module in model.named_modules():
        if not module_name:
            continue
        lowered = module_name.lower()
        hits = [keyword for keyword in normalized_keywords if keyword in lowered]
        if not hits:
            continue
        matched_names.append(module_name)
        parameter_count = module_parameter_count(_module)
        expert_index = extract_expert_index(module_name)
        matched_details.append(
            {
                "module_name": module_name,
                "parameter_count": parameter_count,
                "keyword_hits": hits,
                "expert_index": expert_index,
            }
        )
        suffix_counter[module_name.rsplit(".", 1)[-1]] += 1
        for hit in hits:
            keyword_counter[hit] += 1
        if expert_index is not None:
            expert_index_counter[expert_index] += 1

    result = {
        "model_name": args.model_name,
        "loader": loader_name,
        "keywords": normalized_keywords,
        "matched_module_count": len(matched_names),
        "matched_module_samples": matched_names[: args.max_hits],
        "matched_module_details": matched_details[: args.max_hits],
        "total_matched_parameter_count": sum(item["parameter_count"] for item in matched_details),
        "keyword_hit_counts": dict(keyword_counter),
        "suffix_histogram_top20": suffix_counter.most_common(20),
        "expert_index_histogram_top20": expert_index_counter.most_common(20),
        "suggested_router_suffixes": [
            name for name, _count in suffix_counter.most_common() if any(key in name.lower() for key in ("router", "gate"))
        ][:10],
        "suggested_expert_suffixes": [
            name for name, _count in suffix_counter.most_common() if "expert" in name.lower()
        ][:10],
    }
    target_manifest = build_target_manifest(
        args.model_name,
        matched_details,
        first_pass_expert_budget=args.first_pass_expert_budget,
        max_router_modules=args.max_router_modules,
    )
    result["target_manifest"] = target_manifest
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(payload + "\n")
    if args.manifest_out:
        with open(args.manifest_out, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(target_manifest, indent=2, ensure_ascii=False) + "\n")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

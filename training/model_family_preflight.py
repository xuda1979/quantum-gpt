from __future__ import annotations


def _gemma_conditional_generation_block(
    model_type: str,
    architectures: list[str],
    *,
    path_description: str,
) -> str | None:
    normalized_model_type = str(model_type or "")
    normalized_architectures = [str(item) for item in architectures or []]
    if normalized_model_type == "gemma4" and any("ConditionalGeneration" in item for item in normalized_architectures):
        return (
            "Gemma 4 checkpoints still require a conditional-generation trainer/backend. "
            f"{path_description} "
            "Stop here until a processor-aware conditional-generation backend is implemented."
        )
    return None


def trainer_backend_preflight_block(model_type: str, architectures: list[str]) -> str | None:
    return _gemma_conditional_generation_block(
        model_type,
        architectures,
        path_description=(
            "This runner remains a text-only AutoModelForCausalLM + TaskType.CAUSAL_LM path,"
        ),
    )


def inference_backend_preflight_block(model_type: str, architectures: list[str]) -> str | None:
    return _gemma_conditional_generation_block(
        model_type,
        architectures,
        path_description=(
            "This entrypoint still serves and evaluates through a text-only AutoModelForCausalLM path,"
        ),
    )

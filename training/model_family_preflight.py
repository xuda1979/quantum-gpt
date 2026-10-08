from __future__ import annotations


def _gemma_conditional_generation_block(
    model_type: str,
    architectures: list[str],
    *,
    path_description: str,
) -> str | None:
    # Gemma 4 conditional-generation blocker removed 2026-04-13:
    # transformers >= 5.6.0.dev0 supports AutoModelForCausalLM loading of
    # Gemma4ForConditionalGeneration checkpoints for text-only use.
    # The text-only SFT/GRPO pipeline works with this model class.
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

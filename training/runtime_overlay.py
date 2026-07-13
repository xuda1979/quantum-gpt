from __future__ import annotations

import importlib
import importlib.metadata as importlib_metadata
import importlib.util
import os
import sys
import tempfile
import types
from dataclasses import MISSING, field
from pathlib import Path
from typing import Any

_OVERLAY_STATE: dict[str, Any] | None = None
_MOE_DENSE_PATCHED = False


def _patch_qwen35_moe_dense_experts() -> bool:
    """Replace Qwen3_5MoeExperts.forward with a dense, loop-free implementation.

    The stock forward iterates experts in a Python loop and uses
    ``nonzero``/``torch.where``/``index_add_`` plus the ``ArgSort`` underlying
    ``torch.topk``. On Ascend NPU those data-dependent ops fall back to AiCpu and
    force host-device syncs every layer; on a single-CPU-core host this stalls the
    backward pass indefinitely. The dense version below computes all experts with
    batched einsum + scatter (no loop, no nonzero/where/index_add_), so every op
    stays on AiCore. Verified numerically equivalent (fwd + grad) to the stock
    forward in training/tests; see scripts/test_moe_dense_experts.py.
    """
    global _MOE_DENSE_PATCHED
    if _MOE_DENSE_PATCHED:
        return True
    import torch
    from transformers.models.qwen3_5_moe import modeling_qwen3_5_moe as _mod

    def dense_experts_forward(self, hidden_states, top_k_index, top_k_weights):
        num_tokens = hidden_states.shape[0]
        full_weights = hidden_states.new_zeros(num_tokens, self.num_experts)
        full_weights = full_weights.scatter(1, top_k_index, top_k_weights.to(hidden_states.dtype))
        gate_up = torch.einsum("th,eih->eti", hidden_states, self.gate_up_proj)
        gate, up = gate_up.chunk(2, dim=-1)
        intermediate = self.act_fn(gate) * up
        out = torch.einsum("eti,ehi->eth", intermediate, self.down_proj)
        weights = full_weights.t().unsqueeze(-1).to(out.dtype)
        return (out * weights).sum(dim=0).to(hidden_states.dtype)

    _mod.Qwen3_5MoeExperts.forward = dense_experts_forward
    _MOE_DENSE_PATCHED = True
    return True


def register_qwen35_moe_runtime(
    transformers_module: Any | None = None,
    *,
    auto_config_cls: Any | None = None,
    auto_model_for_causal_lm_cls: Any | None = None,
    auto_model_cls: Any | None = None,
) -> dict[str, str]:
    if transformers_module is None:
        import transformers as transformers_module  # type: ignore[no-redef]
    if _OVERLAY_STATE is not None:
        runtime_src = Path(str(_OVERLAY_STATE.get("runtime_src", "")))
        transformers_overlay = runtime_src / "transformers"
        models_overlay = transformers_overlay / "models"
        if transformers_overlay.exists():
            package_path = getattr(transformers_module, "__path__", None)
            if package_path is not None:
                while str(transformers_overlay) in package_path:
                    package_path.remove(str(transformers_overlay))
                package_path.insert(0, str(transformers_overlay))
        if models_overlay.exists():
            import transformers.models as transformers_models

            models_path = getattr(transformers_models, "__path__", None)
            if models_path is not None:
                while str(models_overlay) in models_path:
                    models_path.remove(str(models_overlay))
                models_path.insert(0, str(models_overlay))
        for module_name, module_path in {
            "transformers.modeling_rope_utils": transformers_overlay / "modeling_rope_utils.py",
            "transformers.initialization": transformers_overlay / "initialization.py",
        }.items():
            if not module_path.exists():
                if module_name == "transformers.initialization":
                    import torch.nn.init as torch_init

                    module = types.ModuleType(module_name)
                    module.ones_ = torch_init.ones_
                    module.copy_ = lambda tensor, src: tensor.data.copy_(src)
                    module.zeros_ = torch_init.zeros_
                    module.normal_ = torch_init.normal_
                    sys.modules[module_name] = module
                    transformers_module.initialization = module
                continue
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec is not None and spec.loader is not None:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                short_name = module_name.rsplit(".", 1)[-1]
                setattr(transformers_module, short_name, module)
        try:
            import transformers.utils as transformers_utils
            import transformers.utils.auto_docstring as auto_docstring_module

            def auto_docstring(*args, **kwargs):
                if args and len(args) == 1 and callable(args[0]) and not kwargs:
                    return args[0]

                def wrap(obj):
                    return obj

                return wrap

            auto_docstring_module.auto_docstring = auto_docstring
            transformers_utils.auto_docstring = auto_docstring
            if not hasattr(transformers_utils, "torch_compilable_check"):

                def torch_compilable_check(*args, **kwargs):
                    if args and len(args) == 1 and callable(args[0]) and not kwargs:
                        return args[0]

                    def wrap(obj):
                        return obj

                    return wrap

                transformers_utils.torch_compilable_check = torch_compilable_check
            try:
                import contextlib

                import transformers.utils.generic as generic_utils

                if not hasattr(generic_utils, "is_flash_attention_requested"):
                    generic_utils.is_flash_attention_requested = lambda config=None: False
                if not hasattr(generic_utils, "maybe_autocast"):
                    generic_utils.maybe_autocast = lambda *args, **kwargs: contextlib.nullcontext()
                if not hasattr(generic_utils, "merge_with_config_defaults"):
                    generic_utils.merge_with_config_defaults = lambda obj: obj
                try:
                    import transformers.utils.output_capturing as output_capturing
                except ModuleNotFoundError:
                    output_capturing = types.ModuleType("transformers.utils.output_capturing")
                    sys.modules["transformers.utils.output_capturing"] = output_capturing

                if not hasattr(output_capturing, "OutputRecorder"):

                    class OutputRecorder:
                        def __init__(self, *args, **kwargs):
                            self.args = args
                            self.kwargs = kwargs

                        def __enter__(self):
                            return self

                        def __exit__(self, exc_type, exc, tb):
                            return False

                        def __call__(self, *args, **kwargs):
                            return self

                        def __repr__(self):
                            return f"OutputRecorder(args={self.args!r}, kwargs={self.kwargs!r})"

                    output_capturing.OutputRecorder = OutputRecorder
                if not hasattr(output_capturing, "capture_outputs"):
                    output_capturing.capture_outputs = (
                        lambda *args, **kwargs: contextlib.nullcontext()
                    )
            except Exception:
                pass
        except Exception:
            pass
        try:
            import transformers.integrations as integrations

            if not hasattr(integrations, "use_experts_implementation"):
                integrations.use_experts_implementation = lambda obj: obj
            if not hasattr(integrations, "use_kernelized_func"):
                integrations.use_kernelized_func = lambda fallback=None, *args, **kwargs: (
                    lambda obj: obj
                )
        except Exception:
            pass
    if auto_config_cls is None:
        auto_config_cls = transformers_module.AutoConfig
    if auto_model_for_causal_lm_cls is None:
        auto_model_for_causal_lm_cls = transformers_module.AutoModelForCausalLM
    if auto_model_cls is None:
        auto_model_cls = getattr(transformers_module, "AutoModel", None)

    from transformers.models.qwen3_5_moe.configuration_qwen3_5_moe import (
        Qwen3_5MoeConfig,
        Qwen3_5MoeTextConfig,
    )
    from transformers.models.qwen3_5_moe.modeling_qwen3_5_moe import (
        Qwen3_5MoeForCausalLM,
        Qwen3_5MoeForConditionalGeneration,
        Qwen3_5MoeModel,
    )

    if os.environ.get("QWEN_MOE_DENSE_EXPERTS", "1") not in ("0", "false", "False"):
        _patch_qwen35_moe_dense_experts()

    auto_config_cls.register("qwen3_5_moe", Qwen3_5MoeConfig, exist_ok=True)
    auto_config_cls.register("qwen3_5_moe_text", Qwen3_5MoeTextConfig, exist_ok=True)

    def _safe_register(auto_cls, config_cls, model_cls):
        # With the full native transformers source these mappings already exist,
        # and auto_factory.register() raises ValueError when a model's
        # config_class does not match the passed config (e.g. CausalLM ->
        # Qwen3_5MoeTextConfig, not the composite Qwen3_5MoeConfig). Tolerate
        # both so registration is idempotent across overlay and full-source runtimes.
        try:
            auto_cls.register(config_cls, model_cls, exist_ok=True)
        except (ValueError, TypeError):
            pass

    if auto_model_cls is not None:
        _safe_register(auto_model_cls, Qwen3_5MoeConfig, Qwen3_5MoeModel)
    _safe_register(auto_model_for_causal_lm_cls, Qwen3_5MoeConfig, Qwen3_5MoeForCausalLM)
    _safe_register(auto_model_for_causal_lm_cls, Qwen3_5MoeTextConfig, Qwen3_5MoeForCausalLM)
    auto_model_for_image_text_to_text_cls = getattr(
        transformers_module, "AutoModelForImageTextToText", None
    )
    if auto_model_for_image_text_to_text_cls is not None:
        _safe_register(
            auto_model_for_image_text_to_text_cls,
            Qwen3_5MoeConfig,
            Qwen3_5MoeForConditionalGeneration,
        )

    for name, value in {
        "Qwen3_5MoeConfig": Qwen3_5MoeConfig,
        "Qwen3_5MoeTextConfig": Qwen3_5MoeTextConfig,
        "Qwen3_5MoeForConditionalGeneration": Qwen3_5MoeForConditionalGeneration,
        "Qwen3_5MoeForCausalLM": Qwen3_5MoeForCausalLM,
        "Qwen3_5MoeModel": Qwen3_5MoeModel,
    }.items():
        if not hasattr(transformers_module, name):
            setattr(transformers_module, name, value)

    return {
        "qwen3_5_moe_config": Qwen3_5MoeConfig.__name__,
        "qwen3_5_moe_text_config": Qwen3_5MoeTextConfig.__name__,
        "qwen3_5_moe_conditional_generation": Qwen3_5MoeForConditionalGeneration.__name__,
        "qwen3_5_moe_causal_lm": Qwen3_5MoeForCausalLM.__name__,
    }


def _install_httpx_stub(stub_root: Path) -> None:
    stub_root.mkdir(parents=True, exist_ok=True)
    (stub_root / "httpx.py").write_text(
        "\n".join(
            [
                "class HTTPError(Exception):",
                "    pass",
                "",
                "class Request:",
                "    pass",
                "",
                "class RequestError(HTTPError):",
                "    pass",
                "",
                "class NetworkError(HTTPError):",
                "    pass",
                "",
                "class ConnectError(NetworkError):",
                "    pass",
                "",
                "class TimeoutException(RequestError):",
                "    pass",
                "",
                "class ReadTimeout(TimeoutException):",
                "    pass",
                "",
                "class ConnectTimeout(TimeoutException):",
                "    pass",
                "",
                "class TransportError(RequestError):",
                "    pass",
                "",
                "class RemoteProtocolError(TransportError):",
                "    pass",
                "",
                "class DecodingError(RequestError):",
                "    pass",
                "",
                "class TooManyRedirects(RequestError):",
                "    pass",
                "",
                "class HTTPStatusError(HTTPError):",
                "    pass",
                "",
                "class Response:",
                "    content = b''",
                "    status_code = 200",
                "",
                "    def json(self):",
                "        return {}",
                "",
                "class Client:",
                "    def __init__(self, *args, **kwargs):",
                "        pass",
                "",
                "    def __enter__(self):",
                "        return self",
                "",
                "    def __exit__(self, exc_type, exc, tb):",
                "        return False",
                "",
                "    def get(self, *args, **kwargs):",
                "        raise NetworkError('stubbed httpx.Client.get should not be used by the local runtime overlay')",
                "",
                "    def post(self, *args, **kwargs):",
                "        raise NetworkError('stubbed httpx.Client.post should not be used by the local runtime overlay')",
                "",
                "    def stream(self, *args, **kwargs):",
                "        raise NetworkError('stubbed httpx.Client.stream should not be used by the local runtime overlay')",
                "",
                "    def close(self):",
                "        pass",
                "",
                "class AsyncClient(Client):",
                "    async def __aenter__(self):",
                "        return self",
                "",
                "    async def __aexit__(self, exc_type, exc, tb):",
                "        return False",
                "",
                "def get(*args, **kwargs):",
                "    raise NetworkError('stubbed httpx.get should not be used by the local runtime overlay')",
                "",
                "def post(*args, **kwargs):",
                "    raise NetworkError('stubbed httpx.post should not be used by the local runtime overlay')",
                "",
                "class _Stream:",
                "    def __enter__(self):",
                "        return self",
                "",
                "    def __exit__(self, exc_type, exc, tb):",
                "        return False",
                "",
                "    def iter_lines(self):",
                "        return iter(())",
                "",
                "def stream(*args, **kwargs):",
                "    raise NetworkError('stubbed httpx.stream should not be used by the local runtime overlay')",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _patch_huggingface_hub_compat(hub_version: str) -> None:
    original_version = importlib_metadata.version

    def patched_version(name: str) -> str:
        normalized = name.replace("_", "-")
        if normalized == "huggingface-hub":
            return hub_version
        return original_version(name)

    importlib_metadata.version = patched_version

    import huggingface_hub as hub

    try:
        import huggingface_hub.dataclasses as hub_dataclasses
    except ModuleNotFoundError:
        hub_dataclasses = types.ModuleType("huggingface_hub.dataclasses")
        sys.modules["huggingface_hub.dataclasses"] = hub_dataclasses

    if not hasattr(hub, "is_offline_mode"):
        hub.is_offline_mode = lambda: False
    if not hasattr(hub_dataclasses, "strict"):

        def strict(cls=None, *, accept_kwargs: bool = False):
            """Compatibility no-op for older huggingface_hub.dataclasses.strict."""

            def wrap(inner):
                return inner

            return wrap(cls) if cls is not None else wrap

        hub_dataclasses.strict = strict
    if not hasattr(hub_dataclasses, "validate_typed_dict"):

        def validate_typed_dict(*args, **kwargs):
            """Compatibility no-op for older huggingface_hub typed-dict validation."""

            return None

        hub_dataclasses.validate_typed_dict = validate_typed_dict
    if not hasattr(hub_dataclasses, "validated_field"):

        def validated_field(
            validator,
            default=MISSING,
            default_factory=MISSING,
            init: bool = True,
            repr: bool = True,
            hash=None,
            compare: bool = True,
            metadata=None,
            **kwargs,
        ):
            """Compatibility validated dataclass field builder for older huggingface_hub."""

            validator_list = validator if isinstance(validator, list) else [validator]
            metadata = dict(metadata or {})
            metadata["validator"] = validator_list
            return field(
                default=default,
                default_factory=default_factory,
                init=init,
                repr=repr,
                hash=hash,
                compare=compare,
                metadata=metadata,
                **kwargs,
            )

        hub_dataclasses.validated_field = validated_field
    if not hasattr(hub_dataclasses, "as_validated_field"):

        def as_validated_field(validator):
            """Compatibility decorator that converts a validator into a field factory."""

            def _inner(
                default=MISSING,
                default_factory=MISSING,
                init: bool = True,
                repr: bool = True,
                hash=None,
                compare: bool = True,
                metadata=None,
                **kwargs,
            ):
                return hub_dataclasses.validated_field(
                    validator,
                    default=default,
                    default_factory=default_factory,
                    init=init,
                    repr=repr,
                    hash=hash,
                    compare=compare,
                    metadata=metadata,
                    **kwargs,
                )

            return _inner

        hub_dataclasses.as_validated_field = as_validated_field
    if not hasattr(hub_dataclasses, "type_validator"):

        def type_validator(name, value, expected_type):
            """Compatibility no-op type validator for older huggingface_hub."""

            return None

        hub_dataclasses.type_validator = type_validator
    if not hasattr(hub_dataclasses, "_create_type_validator"):

        def _create_type_validator(field):
            """Compatibility no-op validator factory for older huggingface_hub."""

            def validator(value):
                hub_dataclasses.type_validator(
                    getattr(field, "name", "field"), value, getattr(field, "type", None)
                )

            return validator

        hub_dataclasses._create_type_validator = _create_type_validator


def apply_transformers_peft_compat_shims(transformers_module: Any | None = None) -> Any:
    if transformers_module is None:
        import transformers as transformers_module  # type: ignore[no-redef]

    # Monkey-patch caching_allocator_warmup to prevent massive OOM allocations on resource-constrained setups
    try:
        import transformers.modeling_utils as modeling_utils

        if hasattr(modeling_utils, "caching_allocator_warmup"):
            print(
                "[INFO] Monkey-patching transformers.modeling_utils.caching_allocator_warmup to be a no-op"
            )
            modeling_utils.caching_allocator_warmup = lambda *args, **kwargs: None
    except Exception as e:
        print(f"[WARN] Failed to monkey-patch caching_allocator_warmup: {e}")

    cache_utils = importlib.import_module("transformers.cache_utils")

    if not hasattr(cache_utils, "HybridCache") and hasattr(cache_utils, "DynamicCache"):
        cache_utils.HybridCache = cache_utils.DynamicCache

    hybrid_cache = getattr(cache_utils, "HybridCache", None)
    if hybrid_cache is not None and not hasattr(transformers_module, "HybridCache"):
        transformers_module.HybridCache = hybrid_cache

    import_structure = getattr(transformers_module, "_import_structure", None)
    if isinstance(import_structure, dict):
        cache_exports = import_structure.setdefault("cache_utils", [])
        if "HybridCache" not in cache_exports and hybrid_cache is not None:
            cache_exports.append("HybridCache")

    exported_names = getattr(transformers_module, "__all__", None)
    if (
        isinstance(exported_names, list)
        and hybrid_cache is not None
        and "HybridCache" not in exported_names
    ):
        exported_names.append("HybridCache")

    return transformers_module


def configure_runtime_overlay_from_env() -> dict[str, Any] | None:
    global _OVERLAY_STATE

    runtime_src_raw = os.environ.get("QUANTUM_TRANSFORMERS_RUNTIME_SRC", "").strip()
    if not runtime_src_raw:
        return None
    if _OVERLAY_STATE is not None:
        return _OVERLAY_STATE

    runtime_src = Path(runtime_src_raw).expanduser()
    if not runtime_src.is_absolute():
        runtime_src = (Path.cwd() / runtime_src).resolve()
    if not runtime_src.exists():
        raise FileNotFoundError(f"QUANTUM_TRANSFORMERS_RUNTIME_SRC not found: {runtime_src}")

    state: dict[str, Any] = {
        "runtime_src": str(runtime_src),
    }

    sys.path.insert(0, str(runtime_src))

    if os.environ.get("QUANTUM_RUNTIME_HTTPX_STUB", "1") != "0":
        stub_root = Path(tempfile.mkdtemp(prefix="quantum-runtime-httpx-stub-"))
        _install_httpx_stub(stub_root)
        sys.path.insert(0, str(stub_root))
        state["httpx_stub_root"] = str(stub_root)

    hub_version = os.environ.get("QUANTUM_HF_HUB_COMPAT_VERSION", "").strip()
    if hub_version:
        _patch_huggingface_hub_compat(hub_version)
        state["hub_compat_version"] = hub_version

    try:
        import transformers.configuration_utils as configuration_utils

        if not hasattr(configuration_utils, "PreTrainedConfig") and hasattr(
            configuration_utils, "PretrainedConfig"
        ):
            configuration_utils.PreTrainedConfig = configuration_utils.PretrainedConfig
            state["pretrained_config_alias"] = "PreTrainedConfig->PretrainedConfig"
    except Exception:
        pass

    _OVERLAY_STATE = state
    return state

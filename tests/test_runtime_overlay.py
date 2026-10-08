from __future__ import annotations

import os
import subprocess
import sys
import types
from pathlib import Path

from training.runtime_overlay import register_qwen35_moe_runtime


def test_apply_transformers_peft_compat_shims_exports_hybrid_cache() -> None:
    python_bin = Path(".venv-omnicoder-qwen35-py311/bin/python")
    if not python_bin.exists():
        python_bin = Path(".venv-gemma4-smoke-py311/bin/python")
    assert python_bin.exists()

    env = os.environ.copy()
    env["QUANTUM_TRANSFORMERS_RUNTIME_SRC"] = (
        "artifacts/runtime-bundles/omnicoder-qwen35-runtime-c585eea/transformers-src/src"
    )
    env["QUANTUM_HF_HUB_COMPAT_VERSION"] = "1.8.0"

    result = subprocess.run(
        [
            str(python_bin),
            "-c",
            "\n".join(
                [
                    "import sys, types, importlib.machinery",
                    "class TorchMock:",
                    "    __version__ = '2.6.0'",
                    "    __spec__ = importlib.machinery.ModuleSpec('torch', None)",
                    "    def __getattr__(self, name):",
                    "        class Dummy:",
                    "            def __init__(self, *args, **kwargs): pass",
                    "        return Dummy",
                    "mock_instance = TorchMock()",
                    "sys.modules['torch'] = mock_instance",
                    "sys.modules['torch.nn'] = mock_instance",
                    "sys.modules['torch.nn.functional'] = mock_instance",
                    "from training.runtime_overlay import configure_runtime_overlay_from_env, apply_transformers_peft_compat_shims",
                    "configure_runtime_overlay_from_env()",
                    "import transformers",
                    "apply_transformers_peft_compat_shims(transformers)",
                    "import transformers.cache_utils as cache_utils",
                    "assert transformers.HybridCache is cache_utils.DynamicCache",
                    "assert cache_utils.HybridCache is cache_utils.DynamicCache",
                    "assert 'HybridCache' in transformers._import_structure['cache_utils']",
                ]
            ),
        ],
        cwd=Path.cwd(),
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_register_qwen35_moe_runtime_registers_image_text_loader(monkeypatch) -> None:
    for name in list(sys.modules):
        if name.startswith("transformers.models.qwen3_5_moe"):
            monkeypatch.delitem(sys.modules, name, raising=False)

    config_module = types.ModuleType("transformers.models.qwen3_5_moe.configuration_qwen3_5_moe")
    modeling_module = types.ModuleType("transformers.models.qwen3_5_moe.modeling_qwen3_5_moe")

    class Qwen3_5MoeConfig:
        pass

    class Qwen3_5MoeTextConfig:
        pass

    class Qwen3_5MoeForConditionalGeneration:
        pass

    class Qwen3_5MoeForCausalLM:
        pass

    class Qwen3_5MoeModel:
        pass

    config_module.Qwen3_5MoeConfig = Qwen3_5MoeConfig
    config_module.Qwen3_5MoeTextConfig = Qwen3_5MoeTextConfig
    modeling_module.Qwen3_5MoeForConditionalGeneration = Qwen3_5MoeForConditionalGeneration
    modeling_module.Qwen3_5MoeForCausalLM = Qwen3_5MoeForCausalLM
    modeling_module.Qwen3_5MoeModel = Qwen3_5MoeModel
    monkeypatch.setitem(sys.modules, config_module.__name__, config_module)
    monkeypatch.setitem(sys.modules, modeling_module.__name__, modeling_module)

    class Registry:
        def __init__(self) -> None:
            self.calls = []

        def register(self, *args, **kwargs) -> None:
            self.calls.append((args, kwargs))

    auto_config = Registry()
    auto_causal = Registry()
    auto_model = Registry()
    auto_image_text = Registry()
    fake_transformers = types.SimpleNamespace(
        AutoConfig=auto_config,
        AutoModelForCausalLM=auto_causal,
        AutoModel=auto_model,
        AutoModelForImageTextToText=auto_image_text,
    )

    registration = register_qwen35_moe_runtime(fake_transformers)

    assert (
        registration["qwen3_5_moe_conditional_generation"] == "Qwen3_5MoeForConditionalGeneration"
    )
    assert auto_image_text.calls == [
        ((Qwen3_5MoeConfig, Qwen3_5MoeForConditionalGeneration), {"exist_ok": True})
    ]
    assert (
        fake_transformers.Qwen3_5MoeForConditionalGeneration is Qwen3_5MoeForConditionalGeneration
    )

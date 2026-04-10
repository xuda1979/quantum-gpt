from __future__ import annotations

import os
import subprocess
from pathlib import Path


def test_apply_transformers_peft_compat_shims_exports_hybrid_cache() -> None:
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

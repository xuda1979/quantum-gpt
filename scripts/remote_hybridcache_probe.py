#!/usr/bin/env python3
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

print(f"root_in_path={sys.path[0]}")

from training.runtime_overlay import apply_transformers_peft_compat_shims, configure_runtime_overlay_from_env

configure_runtime_overlay_from_env()

import transformers

cache_utils = importlib.import_module("transformers.cache_utils")
apply_transformers_peft_compat_shims(transformers)

print(f"transformers_type={type(transformers).__name__}")
print(f"transformers_has_dynamic={hasattr(transformers, 'DynamicCache')}")
print(f"transformers_has_hybrid={hasattr(transformers, 'HybridCache')}")
print(f"transformers_dict_hybrid={'HybridCache' in getattr(transformers, '__dict__', {})}")
print(f"cache_utils_has_hybrid={hasattr(cache_utils, 'HybridCache')}")
print(f"cache_exports={getattr(transformers, '_import_structure', {}).get('cache_utils', [])}")

try:
    from transformers import HybridCache

    print(f"from_import_hybrid={HybridCache}")
except Exception as exc:  # noqa: BLE001
    print(f"from_import_hybrid_error={type(exc).__name__}:{exc}")

try:
    import peft.peft_model as peft_model

    print(f"peft_model_import_ok={peft_model.__file__}")
except Exception as exc:  # noqa: BLE001
    print(f"peft_model_import_error={type(exc).__name__}:{exc}")

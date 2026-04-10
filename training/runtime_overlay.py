from __future__ import annotations

import importlib.metadata as importlib_metadata
import importlib
import os
import sys
import tempfile
import types
from pathlib import Path
from typing import Any

_OVERLAY_STATE: dict[str, Any] | None = None


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
        hub_dataclasses.strict = lambda *args, **kwargs: (lambda fn: fn)
    if not hasattr(hub_dataclasses, "validate_typed_dict"):
        hub_dataclasses.validate_typed_dict = (
            lambda cls=None, **kwargs: cls if cls is not None else (lambda inner: inner)
        )
    hub_dataclasses._create_type_validator = lambda field: (lambda value: None)


def apply_transformers_peft_compat_shims(transformers_module: Any | None = None) -> Any:
    if transformers_module is None:
        import transformers as transformers_module  # type: ignore[no-redef]

    cache_utils = importlib.import_module("transformers.cache_utils")

    if not hasattr(cache_utils, "HybridCache") and hasattr(cache_utils, "DynamicCache"):
        cache_utils.HybridCache = cache_utils.DynamicCache

    hybrid_cache = getattr(cache_utils, "HybridCache", None)
    if hybrid_cache is not None and not hasattr(transformers_module, "HybridCache"):
        setattr(transformers_module, "HybridCache", hybrid_cache)

    import_structure = getattr(transformers_module, "_import_structure", None)
    if isinstance(import_structure, dict):
        cache_exports = import_structure.setdefault("cache_utils", [])
        if "HybridCache" not in cache_exports and hybrid_cache is not None:
            cache_exports.append("HybridCache")

    exported_names = getattr(transformers_module, "__all__", None)
    if isinstance(exported_names, list) and hybrid_cache is not None and "HybridCache" not in exported_names:
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

    _OVERLAY_STATE = state
    return state

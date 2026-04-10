#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.metadata as importlib_metadata
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-name", default="models/OmniCoder-9B")
    parser.add_argument(
        "--runtime-src",
        default="artifacts/runtime-bundles/omnicoder-qwen35-runtime-c585eea/transformers-src/src",
    )
    parser.add_argument(
        "--hub-version",
        default="1.8.0",
        help="Compatibility version reported to the runtime bundle for huggingface-hub.",
    )
    return parser.parse_args()


def install_httpx_stub(stub_root: Path) -> None:
    stub_root.mkdir(parents=True, exist_ok=True)
    (stub_root / "httpx.py").write_text(
        "\n".join(
            [
                "class HTTPError(Exception):",
                "    pass",
                "",
                "class NetworkError(HTTPError):",
                "    pass",
                "",
                "class ConnectError(NetworkError):",
                "    pass",
                "",
                "class Response:",
                "    content = b''",
                "",
                "    def json(self):",
                "        return {}",
                "",
                "def get(*args, **kwargs):",
                "    raise NetworkError('stubbed httpx.get should not be used in local-path overlay probe')",
                "",
                "def post(*args, **kwargs):",
                "    raise NetworkError('stubbed httpx.post should not be used in local-path overlay probe')",
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
                "    raise NetworkError('stubbed httpx.stream should not be used in local-path overlay probe')",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    runtime_src = (ROOT / args.runtime_src).resolve()
    model_name = str((ROOT / args.model_name).resolve()) if not Path(args.model_name).is_absolute() else args.model_name

    summary: dict[str, object] = {
        "model_name": model_name,
        "runtime_src": str(runtime_src),
        "compat_hub_version": args.hub_version,
    }

    if not runtime_src.exists():
        summary["status"] = "error"
        summary["stage"] = "runtime_src"
        summary["error"] = f"runtime source tree not found: {runtime_src}"
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 1

    with tempfile.TemporaryDirectory(prefix="qwen35-httpx-stub-") as temp_dir:
        stub_root = Path(temp_dir)
        install_httpx_stub(stub_root)
        sys.path.insert(0, str(stub_root))
        sys.path.insert(0, str(runtime_src))

        original_version = importlib_metadata.version

        def patched_version(name: str) -> str:
            normalized = name.replace("_", "-")
            if normalized == "huggingface-hub":
                return args.hub_version
            return original_version(name)

        importlib_metadata.version = patched_version
        try:
            import huggingface_hub as hub
            import huggingface_hub.dataclasses as hub_dataclasses

            if not hasattr(hub, "is_offline_mode"):
                hub.is_offline_mode = lambda: False
            if not hasattr(hub_dataclasses, "validate_typed_dict"):
                hub_dataclasses.validate_typed_dict = (
                    lambda cls=None, **kwargs: cls if cls is not None else (lambda inner: inner)
                )
            hub_dataclasses._create_type_validator = lambda field: (lambda value: None)

            from transformers import AutoConfig, AutoTokenizer, PreTrainedTokenizerFast

            from training.text_preprocessor_backend import load_text_preprocessor_backend

            class DummyAutoProcessor:
                @classmethod
                def from_pretrained(cls, *args, **kwargs):
                    raise RuntimeError("processor intentionally skipped for tokenizer fallback probe")

            config = AutoConfig.from_pretrained(model_name, trust_remote_code=True)
            backend = load_text_preprocessor_backend(
                model_name,
                AutoTokenizer,
                DummyAutoProcessor,
                PreTrainedTokenizerFast,
            )
        except Exception as exc:  # noqa: BLE001
            summary["status"] = "error"
            summary["stage"] = "overlay_probe"
            summary["error_type"] = type(exc).__name__
            summary["error"] = str(exc)
            print(json.dumps(summary, indent=2, ensure_ascii=False))
            return 1
        finally:
            importlib_metadata.version = original_version

    summary.update(
        {
            "status": "ok",
            "runtime_config_class": type(config).__name__,
            "model_type": getattr(config, "model_type", None),
            "text_preprocessor_backend_kind": backend.backend_kind,
            "render_backend_class": backend.render_backend.__class__.__name__,
            "text_backend_class": backend.text_backend.__class__.__name__,
            "save_backend_class": backend.save_backend.__class__.__name__,
        }
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

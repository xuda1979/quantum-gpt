#!/usr/bin/env python3
from __future__ import annotations

import argparse
import runpy
import sys
import types


def _patch_huggingface_hub_strict() -> None:
    try:
        import huggingface_hub.dataclasses as hub_dataclasses
    except Exception:
        hub_dataclasses = types.ModuleType("huggingface_hub.dataclasses")
        sys.modules["huggingface_hub.dataclasses"] = hub_dataclasses

    if not hasattr(hub_dataclasses, "strict"):
        hub_dataclasses.strict = lambda *args, **kwargs: (lambda fn: fn)
    if not hasattr(hub_dataclasses, "validate_typed_dict"):
        hub_dataclasses.validate_typed_dict = (
            lambda cls=None, **kwargs: cls if cls is not None else (lambda inner: inner)
        )
    if not hasattr(hub_dataclasses, "_create_type_validator"):
        hub_dataclasses._create_type_validator = lambda field: (lambda value: None)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply runtime overlay compatibility shims, then execute a target script."
    )
    parser.add_argument("--script", required=True, help="Path to the target Python script to execute.")
    parser.add_argument(
        "script_args",
        nargs=argparse.REMAINDER,
        help="Arguments for the target script. Prefix with -- before target args.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    forward_args = list(args.script_args)
    if forward_args and forward_args[0] == "--":
        forward_args = forward_args[1:]

    _patch_huggingface_hub_strict()
    sys.argv = [args.script] + forward_args
    runpy.run_path(args.script, run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

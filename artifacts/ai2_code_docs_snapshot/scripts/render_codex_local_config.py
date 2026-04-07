#!/usr/bin/env python3
"""Render a minimal Codex config for a local OpenAI-compatible provider."""

from __future__ import annotations

import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--provider-id", default="quantum_local")
    parser.add_argument("--profile-id", default="local")
    parser.add_argument("--env-key", default="LOCAL_CODEX_API_KEY")
    parser.add_argument("--wire-api", choices=("v1", "responses"), default="responses")
    parser.add_argument("--supports-websockets", choices=("true", "false"), default="false")
    parser.add_argument("--sandbox-mode", default="workspace-write")
    parser.add_argument("--approval-policy", default="never")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(f'model = "{args.model_name}"')
    print()
    print(f"[model_providers.{args.provider_id}]")
    print('name = "Local Quantum GPT"')
    print(f'base_url = "{args.base_url}"')
    print(f'env_key = "{args.env_key}"')
    print(f'wire_api = "{args.wire_api}"')
    print(f'supports_websockets = {args.supports_websockets}')
    print()
    print(f"[profiles.{args.profile_id}]")
    print(f'model_provider = "{args.provider_id}"')
    print(f'model = "{args.model_name}"')
    print(f'approval_policy = "{args.approval_policy}"')
    print(f'sandbox_mode = "{args.sandbox_mode}"')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

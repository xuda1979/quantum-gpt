#!/usr/bin/env python3
"""Render a Codex config for the local provider, optionally with Yunwu profiles."""

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
    parser.add_argument("--personality")
    parser.add_argument("--workspace-root")
    parser.add_argument("--trust-root", action="append", default=[])
    parser.add_argument("--include-yunwu", action="store_true")
    parser.add_argument("--yunwu-base-url", default="https://api.yunwu.ai/v1")
    parser.add_argument("--yunwu-env-key", default="YUNWU_API_KEY")
    parser.add_argument("--yunwu-wire-api", choices=("v1", "responses"), default="responses")
    parser.add_argument("--yunwu-claude-env-key", default="YUNWU_CLAUDE_API_KEY")
    parser.add_argument("--yunwu-claude-wire-api", choices=("v1", "responses"), default="responses")
    parser.add_argument("--yunwu-gemini-env-key", default="YUNWU_GEMINI_API_KEY")
    parser.add_argument("--yunwu-gemini-wire-api", choices=("v1", "responses"), default="responses")
    parser.add_argument("--yunwu-claude-provider-id", default="yunwu_claude")
    parser.add_argument("--yunwu-gemini-provider-id", default="yunwu_gemini")
    parser.add_argument("--yunwu-claude-profile-id", default="yunwu-claude")
    parser.add_argument("--yunwu-gemini-profile-id", default="yunwu-gemini")
    parser.add_argument("--yunwu-model", default="gpt-5.4")
    parser.add_argument("--yunwu-claude-model", default="claude-opus-4-7")
    parser.add_argument("--yunwu-gemini-model", default="gemini-3.1-pro-preview")
    parser.add_argument("--yunwu-reasoning-effort", default="high")
    parser.add_argument("--yunwu-service-tier", default="fast")
    parser.add_argument("--include-huanxin-glm52-claude", action="store_true")
    parser.add_argument(
        "--include-huanxin-glm52",
        action="store_true",
        dest="include_huanxin_glm52_claude",
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--huanxin-glm52-base-url", default="http://127.0.0.1:18105/v1")
    parser.add_argument("--huanxin-glm52-env-key", default="HUANXIN_GLM52_API_KEY")
    parser.add_argument("--huanxin-glm52-provider-id", default="yunwu_claude")
    parser.add_argument("--huanxin-glm52-profile-id", default="yunwu-claude")
    parser.add_argument("--huanxin-glm52-model", default="glm5.2")
    parser.add_argument(
        "--huanxin-glm52-wire-api", choices=("v1", "responses"), default="responses"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    trusted_roots: list[str] = []
    for trust_root in [args.workspace_root, *args.trust_root]:
        if trust_root and trust_root not in trusted_roots:
            trusted_roots.append(trust_root)
    claude_provider_name = "Yunwu Claude API"
    claude_base_url = args.yunwu_base_url
    claude_env_key = args.yunwu_claude_env_key
    claude_wire_api = args.yunwu_claude_wire_api
    claude_model = args.yunwu_claude_model
    if args.include_huanxin_glm52_claude:
        claude_provider_name = "Huanxin GLM5.2 Claude API"
        claude_base_url = args.huanxin_glm52_base_url
        claude_env_key = args.huanxin_glm52_env_key
        claude_wire_api = args.huanxin_glm52_wire_api
        claude_model = args.huanxin_glm52_model

    print(f'model = "{args.model_name}"')
    if args.personality:
        print(f'personality = "{args.personality}"')
    print()
    print(f"[model_providers.{args.provider_id}]")
    print('name = "Local Quantum GPT"')
    print(f'base_url = "{args.base_url}"')
    print(f'env_key = "{args.env_key}"')
    print(f'wire_api = "{args.wire_api}"')
    print(f"supports_websockets = {args.supports_websockets}")
    print()
    print(f"[profiles.{args.profile_id}]")
    print(f'model_provider = "{args.provider_id}"')
    print(f'model = "{args.model_name}"')
    print(f'approval_policy = "{args.approval_policy}"')
    print(f'sandbox_mode = "{args.sandbox_mode}"')
    for trust_root in trusted_roots:
        print()
        print(f'[projects."{trust_root}"]')
        print('trust_level = "trusted"')

    if args.include_yunwu:
        print()
        print("[model_providers.yunwu]")
        print('name = "Yunwu API"')
        print(f'base_url = "{args.yunwu_base_url}"')
        print(f'env_key = "{args.yunwu_env_key}"')
        print(f'wire_api = "{args.yunwu_wire_api}"')
        print()
        print(f"[model_providers.{args.yunwu_claude_provider_id}]")
        print(f'name = "{claude_provider_name}"')
        print(f'base_url = "{claude_base_url}"')
        print(f'env_key = "{claude_env_key}"')
        print(f'wire_api = "{claude_wire_api}"')
        print()
        print(f"[model_providers.{args.yunwu_gemini_provider_id}]")
        print('name = "Yunwu Gemini API"')
        print(f'base_url = "{args.yunwu_base_url}"')
        print(f'env_key = "{args.yunwu_gemini_env_key}"')
        print(f'wire_api = "{args.yunwu_gemini_wire_api}"')
        print()
        print("[profiles.yunwu]")
        print('model_provider = "yunwu"')
        print(f'model = "{args.yunwu_model}"')
        print(f'model_reasoning_effort = "{args.yunwu_reasoning_effort}"')
        print(f'approval_policy = "{args.approval_policy}"')
        print(f'sandbox_mode = "{args.sandbox_mode}"')
        print(f'service_tier = "{args.yunwu_service_tier}"')
        print()
        print(f"[profiles.{args.yunwu_claude_profile_id}]")
        print(f'model_provider = "{args.yunwu_claude_provider_id}"')
        print(f'model = "{claude_model}"')
        print(f'model_reasoning_effort = "{args.yunwu_reasoning_effort}"')
        print(f'approval_policy = "{args.approval_policy}"')
        print(f'sandbox_mode = "{args.sandbox_mode}"')
        print(f'service_tier = "{args.yunwu_service_tier}"')
        print()
        print(f"[profiles.{args.yunwu_gemini_profile_id}]")
        print(f'model_provider = "{args.yunwu_gemini_provider_id}"')
        print(f'model = "{args.yunwu_gemini_model}"')
        print(f'model_reasoning_effort = "{args.yunwu_reasoning_effort}"')
        print(f'approval_policy = "{args.approval_policy}"')
        print(f'sandbox_mode = "{args.sandbox_mode}"')
        print()
        print("[profiles.yunwu.features]")
        print("js_repl = true")
        print("apps = true")
        print("guardian_approval = true")
        print("tui_app_server = false")
        print("prevent_idle_sleep = true")
        print()
        print(f"[profiles.{args.yunwu_claude_profile_id}.features]")
        print("js_repl = true")
        print("apps = false")
        print("guardian_approval = true")
        print("tui_app_server = false")
        print("prevent_idle_sleep = true")
        print()
        print(f"[profiles.{args.yunwu_gemini_profile_id}.features]")
        print("js_repl = false")
        print("apps = false")
        print("guardian_approval = false")
        print("tui_app_server = false")
        print("prevent_idle_sleep = false")

    if args.include_huanxin_glm52_claude and not args.include_yunwu:
        print()
        print(f"[model_providers.{args.huanxin_glm52_provider_id}]")
        print('name = "Huanxin GLM5.2 Claude API"')
        print(f'base_url = "{args.huanxin_glm52_base_url}"')
        print(f'env_key = "{args.huanxin_glm52_env_key}"')
        print(f'wire_api = "{args.huanxin_glm52_wire_api}"')
        print("supports_websockets = false")
        print()
        print(f"[profiles.{args.huanxin_glm52_profile_id}]")
        print(f'model_provider = "{args.huanxin_glm52_provider_id}"')
        print(f'model = "{args.huanxin_glm52_model}"')
        print(f'approval_policy = "{args.approval_policy}"')
        print(f'sandbox_mode = "{args.sandbox_mode}"')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

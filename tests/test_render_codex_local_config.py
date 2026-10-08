from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "render_codex_local_config.py"


def render(*args: str) -> str:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def test_renders_minimal_local_provider_config() -> None:
    output = render("--model-name", "demo-model")
    assert 'model = "demo-model"' in output
    assert "[model_providers.quantum_local]" in output
    assert 'wire_api = "responses"' in output
    assert "[profiles.local]" in output
    assert 'model_provider = "quantum_local"' in output


def test_renders_yunwu_profiles_with_responses_wire_api() -> None:
    output = render(
        "--model-name",
        "demo-model",
        "--personality",
        "pragmatic",
        "--workspace-root",
        "/root/work/david/software/quantum-gpt",
        "--trust-root",
        "/root/work",
        "--trust-root",
        "/",
        "--include-yunwu",
    )
    assert 'personality = "pragmatic"' in output
    assert '[projects."/root/work/david/software/quantum-gpt"]' in output
    assert '[projects."/root/work"]' in output
    assert '[projects."/"]' in output
    assert "[model_providers.yunwu]" in output
    assert 'env_key = "YUNWU_API_KEY"' in output
    assert output.count('wire_api = "responses"') >= 4
    assert "[profiles.yunwu]" in output
    assert 'model = "gpt-5.4"' in output
    assert "[profiles.yunwu-claude]" in output
    assert 'model = "claude-opus-4-7"' in output


def test_deduplicates_workspace_root_from_trust_roots() -> None:
    output = render(
        "--model-name",
        "demo-model",
        "--workspace-root",
        "/root/software/quantum-gpt",
        "--trust-root",
        "/root/software/quantum-gpt",
    )

    assert output.count('[projects."/root/software/quantum-gpt"]') == 1


def test_renders_huanxin_glm52_in_claude_provider_slot() -> None:
    output = render(
        "--model-name",
        "demo-model",
        "--include-yunwu",
        "--include-huanxin-glm52-claude",
    )

    assert output.count("[model_providers.yunwu_claude]") == 1
    assert 'name = "Huanxin GLM5.2 Claude API"' in output
    assert 'base_url = "http://127.0.0.1:18105/v1"' in output
    assert 'env_key = "HUANXIN_GLM52_API_KEY"' in output
    assert output.count("[profiles.yunwu-claude]") == 1
    assert 'model_provider = "yunwu_claude"' in output
    assert 'model = "glm5.2"' in output

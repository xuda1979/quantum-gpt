from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "asi3_secure_python_s3_pull.py"


def load_module():
    spec = importlib.util.spec_from_file_location("asi3_secure_s3_pull", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_remote_bundle_command_uses_allowlisted_connect_tunnel() -> None:
    module = load_module()
    signed_url = (
        "https://iner.aihuanxin.cn/bucket/bundle.tgz?"
        "X-Amz-Credential=redacted&X-Amz-Signature=redacted"
    )
    command = module.build_remote_command(signed_url=signed_url, bundle_sha256="a" * 64)

    assert "--connect-to iner.aihuanxin.cn:443:nm.aihuanxin.cn:443" in command
    assert signed_url in command
    assert "--noproxy" not in command
    assert "requests.Session" not in command
    assert "sha256sum -c -" in command
    assert "tar -xzf" in command


def test_bundle_request_is_sensitive_and_redacts_signed_url() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    assert '"sensitive": True' in source
    assert '"redactValues": [access_key, secret_key, signed_url]' in source


def test_probe_command_is_temporary_and_uses_same_proxy_route() -> None:
    module = load_module()
    command = module.build_remote_probe_command(
        signed_url="https://iner.aihuanxin.cn/bucket/probe?signature=redacted"
    )

    assert module.CONNECT_TO in command
    assert "__ASI3_INER_ROUTE_PROBE_OK__" in command
    assert "sha256sum" in command
    assert "trap 'rm -f" in command
    assert "tar -xzf" not in command

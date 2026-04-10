from __future__ import annotations

from pathlib import Path

import training.runtime_python as runtime_python
from training.runtime_python import parse_min_version, resolve_python_interpreter


def _write_fake_python(path: Path, version: str) -> None:
    path.write_text(
        "#!/bin/sh\n"
        f"echo {version}\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def test_parse_min_version_accepts_major_minor_only() -> None:
    assert parse_min_version("3.10") == (3, 10)


def test_resolve_python_interpreter_prefers_first_matching_candidate_on_path(
    tmp_path: Path, monkeypatch
) -> None:
    python311 = tmp_path / "python3.11"
    python310 = tmp_path / "python3.10"
    _write_fake_python(python311, "3.11.9")
    _write_fake_python(python310, "3.10.14")
    monkeypatch.setattr(runtime_python, "WORKSPACE_ROOT", tmp_path)
    monkeypatch.setenv("PATH", str(tmp_path))

    resolved = resolve_python_interpreter()

    assert resolved["status"] == "ok"
    assert resolved["selected_path"] == str(python311)
    assert resolved["selected_version"] == "3.11.9"


def test_resolve_python_interpreter_reports_missing_minimum(tmp_path: Path, monkeypatch) -> None:
    python39 = tmp_path / "python3"
    _write_fake_python(python39, "3.9.6")
    monkeypatch.setattr(runtime_python, "WORKSPACE_ROOT", tmp_path)
    monkeypatch.setenv("PATH", str(tmp_path))

    resolved = resolve_python_interpreter()

    assert resolved["status"] == "error"
    assert resolved["selected_path"] is None
    assert resolved["error"].startswith("No local Python interpreter meeting >=")


def test_resolve_python_interpreter_prefers_workspace_bootstrap_candidate(
    tmp_path: Path, monkeypatch
) -> None:
    workspace_python = tmp_path / ".local-python" / "cpython-3.11.15" / "bin" / "python3.11"
    workspace_python.parent.mkdir(parents=True, exist_ok=True)
    _write_fake_python(workspace_python, "3.11.15")
    monkeypatch.setattr(runtime_python, "WORKSPACE_ROOT", tmp_path)
    monkeypatch.setenv("PATH", "")

    resolved = resolve_python_interpreter()

    assert resolved["status"] == "ok"
    assert resolved["selected_path"] == str(workspace_python)
    assert resolved["candidates"][0]["source"] == "workspace_local"


def test_resolve_python_interpreter_suggests_workspace_bootstrap_script_when_cache_exists(
    tmp_path: Path, monkeypatch
) -> None:
    downloads_dir = tmp_path / "Library" / "Caches" / "Homebrew" / "downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)
    (downloads_dir / "dummy--Python-3.11.15.tgz").write_text("x", encoding="utf-8")
    openssl_prefix = tmp_path / "homebrew" / "opt" / "openssl"
    (openssl_prefix / "include" / "openssl").mkdir(parents=True, exist_ok=True)
    (openssl_prefix / "include" / "openssl" / "ssl.h").write_text("", encoding="utf-8")
    (openssl_prefix / "lib").mkdir(parents=True, exist_ok=True)
    (openssl_prefix / "lib" / "libssl.dylib").write_text("", encoding="utf-8")
    bootstrap_script = tmp_path / "scripts" / "bootstrap_local_python311_from_cache.sh"
    bootstrap_script.parent.mkdir(parents=True, exist_ok=True)
    bootstrap_script.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setattr(runtime_python, "WORKSPACE_ROOT", tmp_path)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(runtime_python.Path, "home", lambda: tmp_path)

    resolved = resolve_python_interpreter()

    assert resolved["status"] == "error"
    assert resolved["install_command"] == "bash scripts/bootstrap_local_python311_from_cache.sh"

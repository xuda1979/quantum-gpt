from __future__ import annotations

import json
from pathlib import Path

from quantum_rag.corpus import DocumentChunk
from quantum_rag.index import QuantumRAGIndex
from scripts.check_qwen36_rag_local import parse_env_file, run_preflight


def _write_executable(path: Path) -> None:
    path.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    path.chmod(0o755)


def _write_env(root: Path, *, model_path: Path, llama_server: Path) -> Path:
    env_file = root / ".qwen36-rag-local.env"
    env_file.write_text(
        "\n".join(
            [
                f'QWEN36_RAG_ROOT="{root}"',
                f'QWEN36_RAG_VENV="{root / ".venv-qwen36-rag"}"',
                'QWEN36_RAG_MODEL_REPO="unsloth/Qwen3.6-27B-GGUF"',
                'QWEN36_RAG_MODEL_FILE="Qwen3.6-27B-Q4_K_M.gguf"',
                f'QWEN36_RAG_MODEL_PATH="{model_path}"',
                f'QWEN36_RAG_INDEX="{root / "artifacts/quantum-rag/qwen36-quantum-docs-index.pkl.gz"}"',
                f'QWEN36_RAG_DOCS_DIR="{root / "docs/external/quantum-sdk-docs-latest"}"',
                f'QWEN36_RAG_SUMMARY_JSON="{root / "artifacts/quantum-rag/qwen36-quantum-docs-summary.json"}"',
                f'QWEN36_RAG_FETCH_MANIFEST="{root / "artifacts/quantum-rag/qwen36-docs-fetch-manifest.json"}"',
                f'QWEN36_RAG_LLAMA_SERVER="{llama_server}"',
                'QWEN36_RAG_HOST="127.0.0.1"',
                'QWEN36_RAG_PORT="8011"',
                'QWEN36_RAG_CTX_SIZE="8192"',
                'QWEN36_RAG_MODEL_ALIAS="qwen3.6-27b-rag"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    return env_file


def _make_install_tree(tmp_path: Path, *, include_model: bool = True) -> tuple[Path, Path]:
    root = tmp_path / "repo"
    (root / ".venv-qwen36-rag/bin").mkdir(parents=True)
    _write_executable(root / ".venv-qwen36-rag/bin/python")

    docs_dir = root / "docs/external/quantum-sdk-docs-latest/arclight-isq"
    docs_dir.mkdir(parents=True)
    (docs_dir / "install.md").write_text(
        "Arclight ISQ install docs mention isqc and local compiler setup.",
        encoding="utf-8",
    )

    artifacts = root / "artifacts/quantum-rag"
    artifacts.mkdir(parents=True)
    chunks = [
        DocumentChunk(
            "c1",
            (docs_dir / "install.md").as_posix(),
            "install.md",
            "Arclight ISQ install docs mention isqc and local compiler setup.",
            0,
            64,
        )
    ]
    index = QuantumRAGIndex.build(chunks, max_features=128, dense_components=2)
    index_path = artifacts / "qwen36-quantum-docs-index.pkl.gz"
    index.save(index_path)
    summary = {"output": index_path.as_posix(), "profile": "test", **index.summary()}
    (artifacts / "qwen36-quantum-docs-summary.json").write_text(
        json.dumps(summary),
        encoding="utf-8",
    )
    manifest = {"source_count": 1, "total_written": 1, "results": [{"id": "arclight-isq"}]}
    (artifacts / "qwen36-docs-fetch-manifest.json").write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )

    model_path = root / "models/Qwen3.6-27B-GGUF/model.gguf"
    model_path.parent.mkdir(parents=True)
    if include_model:
        model_path.write_bytes(b"gguf")

    llama_server = root / "bin/llama-server"
    llama_server.parent.mkdir(parents=True)
    _write_executable(llama_server)

    env_file = _write_env(root, model_path=model_path, llama_server=llama_server)
    return root, env_file


def test_parse_env_file_handles_shell_quoting(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        'QWEN36_RAG_ROOT="/tmp/path with spaces"\n'
        'EMPTY=""\n'
        "BROKEN_LINE\n",
        encoding="utf-8",
    )
    env, errors = parse_env_file(env_file)
    assert env["QWEN36_RAG_ROOT"] == "/tmp/path with spaces"
    assert env["EMPTY"] == ""
    assert errors == ["line 3: missing '='"]


def test_preflight_passes_for_complete_install_tree(tmp_path: Path) -> None:
    _, env_file = _make_install_tree(tmp_path)
    payload = run_preflight(
        env_file=env_file,
        min_model_bytes=1,
        context_query="How do I install Arclight ISQ?",
    )
    assert payload["ok"] is True
    statuses = {check["name"]: check["status"] for check in payload["checks"]}
    assert statuses["model_file"] == "pass"
    assert statuses["index_load"] == "pass"
    assert statuses["context_query"] == "pass"
    assert payload["retrieval_results"][0]["source_path"].endswith("install.md")


def test_preflight_can_warn_for_smoke_install_without_model(tmp_path: Path) -> None:
    _, env_file = _make_install_tree(tmp_path, include_model=False)
    payload = run_preflight(
        env_file=env_file,
        allow_missing_model=True,
        min_model_bytes=1,
    )
    assert payload["ok"] is True
    model_check = next(check for check in payload["checks"] if check["name"] == "model_file")
    assert model_check["status"] == "warn"


def test_preflight_fails_when_model_is_required_but_missing(tmp_path: Path) -> None:
    _, env_file = _make_install_tree(tmp_path, include_model=False)
    payload = run_preflight(env_file=env_file, min_model_bytes=1)
    assert payload["ok"] is False
    model_check = next(check for check in payload["checks"] if check["name"] == "model_file")
    assert model_check["status"] == "fail"

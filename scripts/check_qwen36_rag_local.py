#!/usr/bin/env python3
"""Preflight-check a local Qwen3.6 + quantum RAG installation.

This intentionally does not start llama-server or generate tokens. It verifies
that the generated environment file points at a usable model, RAG index, docs
corpus, and local server binary, then can optionally run a context-only
retrieval query against the index.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantum_rag.index import QuantumRAGIndex
from quantum_rag.retrieval import QueryExpansionConfig, retrieve


DEFAULT_ENV_FILE = ROOT / ".qwen36-rag-local.env"
DEFAULT_SUMMARY_JSON = ROOT / "artifacts" / "quantum-rag" / "qwen36-quantum-docs-summary.json"
DEFAULT_FETCH_MANIFEST = ROOT / "artifacts" / "quantum-rag" / "qwen36-docs-fetch-manifest.json"


@dataclass(frozen=True)
class PreflightCheck:
    name: str
    status: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


def parse_env_file(path: Path) -> tuple[dict[str, str], list[str]]:
    env: dict[str, str] = {}
    errors: list[str] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            errors.append(f"line {line_number}: missing '='")
            continue
        key, raw_value = line.split("=", 1)
        key = key.strip()
        if not key:
            errors.append(f"line {line_number}: empty key")
            continue
        try:
            parts = shlex.split(raw_value.strip(), posix=True)
        except ValueError as exc:
            errors.append(f"line {line_number}: {exc}")
            continue
        env[key] = parts[0] if parts else ""
    return env, errors


def _resolve_path(value: str, *, base: Path) -> Path:
    expanded = os.path.expandvars(os.path.expanduser(value))
    path = Path(expanded)
    if not path.is_absolute():
        path = base / path
    return path


def _add(
    checks: list[PreflightCheck],
    name: str,
    ok: bool,
    message: str,
    *,
    required: bool = True,
    details: dict[str, Any] | None = None,
) -> None:
    status = "pass" if ok else ("fail" if required else "warn")
    checks.append(PreflightCheck(name=name, status=status, message=message, details=details or {}))


def _count_files(path: Path) -> int:
    if not path.exists() or not path.is_dir():
        return 0
    return sum(1 for child in path.rglob("*") if child.is_file())


def _check_executable(command: str) -> tuple[bool, str | None]:
    if not command:
        return False, None
    if "/" in command or "\\" in command:
        path = Path(command).expanduser()
        return path.exists() and os.access(path, os.X_OK), path.as_posix()
    resolved = shutil.which(command)
    return resolved is not None, resolved


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(payload, dict):
        return None, "top-level JSON value is not an object"
    return payload, None


def run_preflight(
    *,
    env_file: Path = DEFAULT_ENV_FILE,
    allow_missing_model: bool = False,
    allow_missing_llama_server: bool = False,
    skip_index_load: bool = False,
    context_query: str | None = None,
    top_k: int = 3,
    min_chunks: int = 1,
    min_sources: int = 1,
    min_doc_files: int = 1,
    min_model_bytes: int = 1_000_000,
) -> dict[str, Any]:
    checks: list[PreflightCheck] = []
    loaded_index: QuantumRAGIndex | None = None
    env: dict[str, str] = {}
    env_errors: list[str] = []

    if not env_file.exists():
        _add(checks, "env_file", False, f"missing environment file: {env_file}")
        return {
            "ok": False,
            "env_file": env_file.as_posix(),
            "checks": [asdict(check) for check in checks],
        }

    env, env_errors = parse_env_file(env_file)
    _add(
        checks,
        "env_file",
        not env_errors,
        f"loaded {len(env)} variables from {env_file}",
        details={"parse_errors": env_errors},
    )

    root = _resolve_path(env.get("QWEN36_RAG_ROOT", ROOT.as_posix()), base=env_file.parent)
    _add(checks, "root", root.exists(), f"root exists: {root}", details={"path": root.as_posix()})

    required_vars = [
        "QWEN36_RAG_VENV",
        "QWEN36_RAG_MODEL_PATH",
        "QWEN36_RAG_INDEX",
        "QWEN36_RAG_DOCS_DIR",
        "QWEN36_RAG_LLAMA_SERVER",
    ]
    missing_vars = [key for key in required_vars if not env.get(key)]
    _add(
        checks,
        "required_env",
        not missing_vars,
        "required QWEN36_RAG_* variables are present",
        details={"missing": missing_vars},
    )

    venv_path = _resolve_path(env.get("QWEN36_RAG_VENV", ""), base=root)
    venv_python = venv_path / "bin" / "python"
    _add(
        checks,
        "venv_python",
        venv_python.exists(),
        f"venv python exists: {venv_python}",
        details={"path": venv_python.as_posix()},
    )

    model_path = _resolve_path(env.get("QWEN36_RAG_MODEL_PATH", ""), base=root)
    model_exists = model_path.exists()
    model_size = model_path.stat().st_size if model_exists else 0
    model_ok = model_exists and model_size >= min_model_bytes
    _add(
        checks,
        "model_file",
        model_ok,
        f"model file exists and is at least {min_model_bytes} bytes: {model_path}",
        required=not allow_missing_model,
        details={"path": model_path.as_posix(), "size_bytes": model_size},
    )

    llama_ok, llama_resolved = _check_executable(env.get("QWEN36_RAG_LLAMA_SERVER", ""))
    _add(
        checks,
        "llama_server",
        llama_ok,
        "llama-server executable is resolvable",
        required=not allow_missing_llama_server,
        details={
            "configured": env.get("QWEN36_RAG_LLAMA_SERVER", ""),
            "resolved": llama_resolved,
        },
    )

    docs_dir = _resolve_path(env.get("QWEN36_RAG_DOCS_DIR", ""), base=root)
    doc_file_count = _count_files(docs_dir)
    _add(
        checks,
        "docs_corpus",
        docs_dir.exists() and doc_file_count >= min_doc_files,
        f"docs corpus has at least {min_doc_files} files: {docs_dir}",
        details={"path": docs_dir.as_posix(), "file_count": doc_file_count},
    )

    index_path = _resolve_path(env.get("QWEN36_RAG_INDEX", ""), base=root)
    _add(
        checks,
        "index_file",
        index_path.exists(),
        f"RAG index exists: {index_path}",
        details={"path": index_path.as_posix(), "size_bytes": index_path.stat().st_size if index_path.exists() else 0},
    )

    index_summary: dict[str, Any] | None = None
    if index_path.exists() and not skip_index_load:
        try:
            loaded_index = QuantumRAGIndex.load(index_path)
            index_summary = loaded_index.summary()
            index_ok = (
                int(index_summary["chunk_count"]) >= min_chunks
                and int(index_summary["source_count"]) >= min_sources
            )
            _add(
                checks,
                "index_load",
                index_ok,
                f"loaded index with at least {min_chunks} chunks and {min_sources} sources",
                details=index_summary,
            )
        except Exception as exc:  # pragma: no cover - defensive for corrupted local indexes
            _add(checks, "index_load", False, f"failed to load index: {exc}")

    summary_path = _resolve_path(env.get("QWEN36_RAG_SUMMARY_JSON", DEFAULT_SUMMARY_JSON.as_posix()), base=root)
    if summary_path.exists():
        summary_payload, summary_error = _read_json(summary_path)
        summary_ok = summary_payload is not None
        details = summary_payload or {"error": summary_error}
        if summary_payload is not None and index_summary is not None:
            expected = {
                "chunk_count": index_summary["chunk_count"],
                "source_count": index_summary["source_count"],
            }
            actual = {
                "chunk_count": summary_payload.get("chunk_count"),
                "source_count": summary_payload.get("source_count"),
            }
            summary_ok = actual == expected
            details = {**summary_payload, "expected": expected}
        _add(
            checks,
            "summary_json",
            summary_ok,
            f"summary JSON is readable and matches loaded index: {summary_path}",
            details=details,
        )
    else:
        _add(
            checks,
            "summary_json",
            False,
            f"summary JSON is missing: {summary_path}",
            required=False,
        )

    manifest_path = _resolve_path(
        env.get("QWEN36_RAG_FETCH_MANIFEST", DEFAULT_FETCH_MANIFEST.as_posix()),
        base=root,
    )
    if manifest_path.exists():
        manifest_payload, manifest_error = _read_json(manifest_path)
        total_written = int(manifest_payload.get("total_written", 0)) if manifest_payload else 0
        _add(
            checks,
            "fetch_manifest",
            manifest_payload is not None and total_written >= min_doc_files,
            f"fetch manifest is readable and records at least {min_doc_files} docs: {manifest_path}",
            details=manifest_payload or {"error": manifest_error},
        )
    else:
        _add(
            checks,
            "fetch_manifest",
            False,
            f"fetch manifest is missing: {manifest_path}",
            required=False,
        )

    retrieval_results: list[dict[str, Any]] = []
    if context_query:
        if loaded_index is None and not skip_index_load and index_path.exists():
            loaded_index = QuantumRAGIndex.load(index_path)
        if loaded_index is None:
            _add(checks, "context_query", False, "cannot run context query without a loaded index")
        else:
            results = retrieve(
                loaded_index,
                context_query,
                top_k=top_k,
                expansion=QueryExpansionConfig(enabled=True),
                max_chunks_per_source=2,
            )
            retrieval_results = [
                {
                    "rank": item.rank,
                    "source_path": item.chunk.source_path,
                    "score": item.final_score,
                    "preview": item.chunk.text[:240],
                }
                for item in results
            ]
            _add(
                checks,
                "context_query",
                bool(results),
                f"context-only retrieval returned {len(results)} chunks",
                details={"query": context_query, "top_results": retrieval_results},
            )

    failed_required = [check for check in checks if check.status == "fail"]
    return {
        "ok": not failed_required,
        "env_file": env_file.as_posix(),
        "checks": [asdict(check) for check in checks],
        "retrieval_results": retrieval_results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_FILE)
    parser.add_argument("--allow-missing-model", action="store_true")
    parser.add_argument("--allow-missing-llama-server", action="store_true")
    parser.add_argument("--skip-index-load", action="store_true")
    parser.add_argument("--context-query", default=None)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--min-chunks", type=int, default=1)
    parser.add_argument("--min-sources", type=int, default=1)
    parser.add_argument("--min-doc-files", type=int, default=1)
    parser.add_argument("--min-model-bytes", type=int, default=1_000_000)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def print_text_report(payload: dict[str, Any]) -> None:
    status = "PASS" if payload["ok"] else "FAIL"
    print(f"Qwen3.6 RAG preflight: {status}")
    print(f"env: {payload['env_file']}")
    for check in payload["checks"]:
        label = check["status"].upper()
        print(f"[{label}] {check['name']}: {check['message']}")
    if payload.get("retrieval_results"):
        print("\nTop retrieved sources:")
        for item in payload["retrieval_results"]:
            print(f"  C{item['rank']}: {item['source_path']} ({item['score']:.4f})")


def main() -> int:
    args = parse_args()
    payload = run_preflight(
        env_file=args.env_file,
        allow_missing_model=args.allow_missing_model,
        allow_missing_llama_server=args.allow_missing_llama_server,
        skip_index_load=args.skip_index_load,
        context_query=args.context_query,
        top_k=args.top_k,
        min_chunks=args.min_chunks,
        min_sources=args.min_sources,
        min_doc_files=args.min_doc_files,
        min_model_bytes=args.min_model_bytes,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_text_report(payload)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Fail-closed admission for LLM-generated executable coding tasks.

Task harnesses/reference programs are executable untrusted code. Run admission
ONLY in a dedicated sandbox with no credentials, network, or writable host mounts.
A subprocess timeout is an availability limit, not a security sandbox.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

VERSION = 1
_MARKER = "__QUANTUM_TASK_ADMISSION_RESULT__="
_RUNNER = r'''
import importlib.util, json, sys
try:
    spec = importlib.util.spec_from_file_location("admission_harness", sys.argv[1])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.run_tests(sys.argv[2])
    passed = isinstance(result, dict) and result.get("passed") is True
    print("__QUANTUM_TASK_ADMISSION_RESULT__=" + json.dumps({"passed": passed, "valid": isinstance(result, dict)}))
except BaseException as exc:
    print("__QUANTUM_TASK_ADMISSION_RESULT__=" + json.dumps({"passed": False, "valid": False, "error": type(exc).__name__}))
'''


class AdmissionError(ValueError):
    """Task evidence is absent, ambiguous, stale, or inconsistent."""


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prompt_text(meta: dict[str, Any]) -> str:
    value = meta.get("task_prompt") or meta.get("description")
    if not isinstance(value, str) or not value.strip():
        raise AdmissionError("missing_nonempty_task_prompt")
    return value.strip()


def prompt_hash(prompt: str) -> str:
    canonical = re.sub(r"\s+", " ", prompt).strip().casefold()
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _safe_file(task_dir: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or not relative or ".." in path.parts:
        raise AdmissionError("unsafe_reference_path")
    candidate = (task_dir / path).resolve()
    if not candidate.is_relative_to(task_dir.resolve()) or not candidate.is_file():
        raise AdmissionError("missing_or_external_reference")
    return candidate


def _run(tests: Path, candidate: Path, timeout: float) -> bool:
    try:
        process = subprocess.run(
            [sys.executable, "-c", _RUNNER, str(tests), str(candidate)],
            cwd=str(tests.parent), text=True, capture_output=True,
            timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise AdmissionError("harness_timeout") from exc
    if process.returncode != 0:
        raise AdmissionError("harness_subprocess_failure")
    for line in reversed(process.stdout.splitlines()):
        if line.startswith(_MARKER):
            try:
                payload = json.loads(line[len(_MARKER):])
            except ValueError as exc:
                raise AdmissionError("malformed_harness_result") from exc
            return payload.get("passed") is True and payload.get("valid") is True
    raise AdmissionError("missing_harness_result")


def _mutant(code: str) -> str:
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        raise AdmissionError("reference_syntax_error") from exc

    class ReplaceReturn(ast.NodeTransformer):
        changed = False

        def visit_Return(self, node: ast.Return) -> ast.AST:
            if not self.changed:
                self.changed = True
                node.value = ast.Constant(value="__admission_wrong_answer__")
            return node

    transformer = ReplaceReturn()
    tree = transformer.visit(tree)
    if not transformer.changed:
        raise AdmissionError("reference_has_no_mutatable_return")
    ast.fix_missing_locations(tree)
    mutant = ast.unparse(tree)
    if mutant.strip() == code.strip():
        raise AdmissionError("mutation_no_effect")
    return mutant


def _temp_candidate(task_dir: Path, source: str) -> Path:
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".py", prefix="admission_",
        dir=str(task_dir), delete=False,
    ) as handle:
        handle.write(source)
        return Path(handle.name)


def admit_task(task: dict[str, Any], root: Path, *, timeout: float = 15.0,
               allow_candidate_reference: bool = False) -> dict[str, Any]:
    """Accept only a stable task with passing oracle and failing negative controls."""
    task_dir = Path(task["task_dir"]).resolve()
    meta_file, tests = task_dir / "task.json", task_dir / "tests.py"
    if not meta_file.is_file() or not tests.is_file():
        raise AdmissionError("missing_task_contract")
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    task_id = meta.get("id")
    if not isinstance(task_id, str) or not task_id.strip():
        raise AdmissionError("missing_task_id")
    if not isinstance(meta.get("domain"), str) or not meta["domain"].strip():
        raise AdmissionError("missing_domain")
    prompt = prompt_text(meta)
    ref = meta.get("reference_file")
    if ref is None and allow_candidate_reference:
        ref = "candidate.py"
    if not isinstance(ref, str):
        raise AdmissionError("reference_file_required")
    reference = _safe_file(task_dir, ref)
    recorded = (file_hash(meta_file), file_hash(tests), file_hash(reference))
    source = reference.read_text(encoding="utf-8")
    mutated = _mutant(source)
    tmp_mutant = _temp_candidate(task_dir, mutated)
    tmp_empty = _temp_candidate(task_dir, "")
    try:
        if not _run(tests, reference, timeout) or not _run(tests, reference, timeout):
            raise AdmissionError("reference_not_reliably_correct")
        if _run(tests, tmp_mutant, timeout):
            raise AdmissionError("mutant_passes_tests")
        if _run(tests, tmp_empty, timeout):
            raise AdmissionError("empty_program_passes_tests")
    finally:
        tmp_mutant.unlink(missing_ok=True)
        tmp_empty.unlink(missing_ok=True)
    if recorded != (file_hash(meta_file), file_hash(tests), file_hash(reference)):
        raise AdmissionError("contract_changed_during_verification")
    return {
        "id": task_id,
        "domain": meta["domain"],
        "path": str(task_dir.relative_to(root.resolve())),
        "task_sha256": recorded[0],
        "tests_sha256": recorded[1],
        "reference_file": str(reference.relative_to(task_dir)),
        "reference_sha256": recorded[2],
        "prompt_sha256": prompt_hash(prompt),
        "status": "verified",
        "positive_runs": 2,
        "negative_mutant_rejected": True,
        "negative_empty_rejected": True,
    }


def read_manifest(path: str | Path) -> dict[str, dict[str, Any]]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("version") != VERSION:
        raise AdmissionError("unsupported_verified_task_manifest")
    items = raw.get("tasks")
    if not isinstance(items, list) or not items:
        raise AdmissionError("empty_verified_task_manifest")
    by_id: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise AdmissionError("malformed_verified_task_entry")
        if (item.get("status") != "verified" or item.get("positive_runs") != 2
                or item.get("negative_mutant_rejected") is not True
                or item.get("negative_empty_rejected") is not True):
            raise AdmissionError("unverified_task_in_manifest")
        if item["id"] in by_id:
            raise AdmissionError("duplicate_manifest_task_id")
        by_id[item["id"]] = item
    return by_id


def verify_task_integrity(task: dict[str, Any], entry: dict[str, Any], root: Path) -> None:
    """Recheck hashes both before model load and at each rollout step."""
    task_dir = Path(task["task_dir"]).resolve()
    root = root.resolve()
    meta = task["meta"]
    if str(meta.get("id", "")) != entry.get("id"):
        raise AdmissionError("task_id_drift")
    if not task_dir.is_relative_to(root) or str(task_dir.relative_to(root)) != entry.get("path"):
        raise AdmissionError("task_location_drift")
    source = task_dir / "task.json"
    tests = task_dir / "tests.py"
    ref = _safe_file(task_dir, str(entry.get("reference_file", "")))
    if (file_hash(source) != entry.get("task_sha256")
            or file_hash(tests) != entry.get("tests_sha256")
            or file_hash(ref) != entry.get("reference_sha256")):
        raise AdmissionError("verified_task_hash_mismatch")
    if prompt_hash(prompt_text(meta)) != entry.get("prompt_sha256"):
        raise AdmissionError("verified_prompt_drift")


def discover_task_contracts(root: Path) -> list[dict[str, Any]]:
    return [
        {"task_dir": task_dir}
        for domain in sorted(root.iterdir()) if domain.is_dir()
        for task_dir in sorted(domain.iterdir()) if task_dir.is_dir()
        if (task_dir / "task.json").is_file() and (task_dir / "tests.py").is_file()
    ]


def holdout_keys(path: Path | None) -> tuple[set[str], set[str]]:
    if path is None:
        return set(), set()
    ids, prompts = set(), set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.lstrip().startswith("{"):
            record = json.loads(line)
            task_id = record.get("task_id") or record.get("id")
            prompt = record.get("task_prompt") or record.get("prompt")
            if isinstance(task_id, str):
                ids.add(task_id)
            if isinstance(prompt, str) and prompt.strip():
                prompts.add(prompt_hash(prompt))
        else:
            ids.add(line.strip())
    return ids, prompts


def build_manifest(root: Path, *, timeout: float = 15.0,
                   allow_candidate_reference: bool = False,
                   holdout: Path | None = None,
                   allowed_ids: set[str] | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    ids, prompt_hashes = holdout_keys(holdout)
    seen_ids, seen_prompts = set(), set()
    accepted, rejected = [], []
    for task in discover_task_contracts(root):
        task_dir = task["task_dir"]
        try:
            meta = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
            task_id = str(meta.get("id", ""))
            if allowed_ids is not None and task_id not in allowed_ids:
                continue
            ph = prompt_hash(prompt_text(meta))
            if task_id in ids or ph in prompt_hashes:
                raise AdmissionError("holdout_overlap")
            if task_id in seen_ids or ph in seen_prompts:
                raise AdmissionError("duplicate_task_or_prompt")
            entry = admit_task(task, root, timeout=timeout,
                               allow_candidate_reference=allow_candidate_reference)
            accepted.append(entry)
            seen_ids.add(task_id)
            seen_prompts.add(ph)
        except (AdmissionError, OSError, ValueError, SyntaxError) as exc:
            rejected.append({"path": str(task_dir.relative_to(root)), "reason": str(exc)})
    manifest = {"version": VERSION, "tasks": accepted}
    report = {"accepted": len(accepted), "rejected": len(rejected), "rejections": rejected}
    return manifest, report

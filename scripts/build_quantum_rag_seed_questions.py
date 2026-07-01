#!/usr/bin/env python3
"""Build doc-grounded quantum coding seed questions from local RAG markdown."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCS_DIR = ROOT / "docs" / "quantum_libraries"
DEFAULT_OUTPUT = ROOT / "data" / "seed" / "quantum_rag_seed_questions.jsonl"
DEFAULT_MANIFEST = ROOT / "data" / "seed" / "quantum_rag_seed_questions_manifest.json"

FORMAT = "chat-sft-v1"
SOURCE_SCHEMA = "quantum-rag-seed-questions-v1"
SOURCE_NAME = "docs_quantum_libraries"

SYSTEM_PROMPT = (
    "You are a careful quantum coding assistant. Use the provided local quantum "
    "library documentation as grounding. Prefer executable Python or precise "
    "algorithmic steps, and do not invent measurement counts, optimal parameters, "
    "fidelities, or energies."
)

HOLDOUT_PATH_PARTS = {"evals", "benchmarks", "runs", "tasks"}

FRAMEWORK_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("qiskit", ("qiskit", "QuantumCircuit", "AerSimulator", "Statevector")),
    ("cirq", ("cirq", "LineQubit")),
    ("pennylane", ("pennylane", "qml.", "QNode")),
    ("braket", ("braket", "AwsDevice", "LocalSimulator")),
    ("numpy", ("numpy", "np.", "NumPy")),
)

CATEGORY_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("circuit_construction", ("circuit", "bell", "ghz", "teleport", "superdense")),
    ("algorithm_implementation", ("grover", "qaoa", "vqe", "phase estimation", "qft", "trotter")),
    ("state_simulation", ("state vector", "density matrix", "partial trace", "channel", "kraus")),
    ("debug_repair", ("pitfall", "repair", "alias", "gotcha", "measurement")),
    ("error_correction", ("error correction", "stabilizer", "syndrome", "shor")),
    ("library_api_grounding", ("qiskit", "cirq", "pennylane", "braket")),
)


@dataclass(frozen=True)
class MarkdownSection:
    heading: str
    body: str


@dataclass(frozen=True)
class QuantumDoc:
    path: Path
    title: str
    sections: tuple[MarkdownSection, ...]
    code_blocks: tuple[str, ...]
    sha256: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs-dir", type=Path, default=DEFAULT_DOCS_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--max-records", type=int, default=None)
    return parser.parse_args()


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "quantum_doc"


def read_markdown_doc(path: Path) -> QuantumDoc:
    text = path.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+?)\s*$", text, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else path.stem.replace("_", " ").title()

    section_matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE))
    sections: list[MarkdownSection] = []
    for index, match in enumerate(section_matches):
        start = match.end()
        end = section_matches[index + 1].start() if index + 1 < len(section_matches) else len(text)
        body = text[start:end].strip()
        if body:
            sections.append(MarkdownSection(match.group(1).strip(), body))

    code_blocks = tuple(match.group(1).strip() for match in re.finditer(r"```(?:[a-zA-Z0-9_+-]+)?\n(.*?)```", text, re.DOTALL))
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return QuantumDoc(path=path, title=title, sections=tuple(sections), code_blocks=code_blocks, sha256=digest)


def iter_markdown_docs(docs_dir: Path) -> list[QuantumDoc]:
    docs: list[QuantumDoc] = []
    for path in sorted(docs_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        reject_holdout_path(path)
        docs.append(read_markdown_doc(path))
    return docs


def reject_holdout_path(path: Path) -> None:
    parts = set(path.parts)
    if parts & HOLDOUT_PATH_PARTS:
        raise ValueError(f"refusing to build seed data from holdout/eval path: {path}")


def detect_framework(doc: QuantumDoc) -> str | None:
    haystack = "\n".join([doc.path.stem, doc.title, *(section.heading for section in doc.sections), *doc.code_blocks])
    for framework, needles in FRAMEWORK_PATTERNS:
        if any(needle.lower() in haystack.lower() for needle in needles):
            return framework
    return None


def detect_category(doc: QuantumDoc) -> str:
    haystack = " ".join([doc.path.stem.replace("_", " "), doc.title, *(section.heading for section in doc.sections)]).lower()
    for category, needles in CATEGORY_PATTERNS:
        if any(needle in haystack for needle in needles):
            return category
    return "quantum_concept_grounding"


def detect_task_type(doc: QuantumDoc) -> str:
    lower = " ".join([doc.path.stem, doc.title]).lower()
    if any(word in lower for word in ("repair", "pitfall", "gotcha", "alias")):
        return "repair"
    if doc.code_blocks:
        return "implementation"
    if any(word in lower for word in ("workflow", "protocol", "concept")):
        return "decomposition"
    return "explanation"


def section_by_name(doc: QuantumDoc, *needles: str) -> MarkdownSection | None:
    lowered = tuple(needle.lower() for needle in needles)
    for section in doc.sections:
        if any(needle in section.heading.lower() for needle in lowered):
            return section
    return doc.sections[0] if doc.sections else None


def compact_text(text: str, *, max_chars: int = 900) -> str:
    cleaned = re.sub(r"\n{3,}", "\n\n", text.strip())
    if len(cleaned) <= max_chars:
        return cleaned
    truncated = cleaned[:max_chars].rsplit(" ", 1)[0].rstrip()
    return truncated + "..."


def build_user_prompt(doc: QuantumDoc, framework: str | None, task_type: str) -> str:
    framework_text = f" in {framework}" if framework else ""
    if task_type == "repair":
        return (
            f"Create a compact quantum coding repair task from the local documentation topic "
            f"'{doc.title}'{framework_text}. Include the expected corrected behavior and the "
            "main pitfalls the model should avoid."
        )
    if task_type == "implementation":
        return (
            f"Using the local quantum library documentation for '{doc.title}', write a seed "
            f"coding task{framework_text}. Ask for executable Python or pseudocode grounded "
            "in the documented API, with no fabricated run results."
        )
    if task_type == "decomposition":
        return (
            f"Turn the local documentation topic '{doc.title}' into a concise algorithmic "
            "planning task for a quantum coding model. Keep the answer grounded in the doc."
        )
    return (
        f"Write a doc-grounded quantum coding question and answer about '{doc.title}'. "
        "Focus on precise semantics that would help a model implement the concept later."
    )


def build_assistant_answer(doc: QuantumDoc) -> str:
    concept = section_by_name(doc, "concept", "definition", "protocol", "workflow")
    reference = section_by_name(doc, "evaluation", "reference", "building", "library", "snippet")
    pitfalls = section_by_name(doc, "pitfall", "gotcha", "common")

    lines = [f"Seed task: implement or explain `{doc.title}` using the local documentation."]
    if concept:
        lines.append("")
        lines.append("Grounding:")
        lines.append(compact_text(concept.body, max_chars=650))
    if reference and reference is not concept:
        lines.append("")
        lines.append("Implementation target:")
        lines.append(compact_text(reference.body, max_chars=850))
    elif doc.code_blocks:
        lines.append("")
        lines.append("Implementation target:")
        lines.append(f"```python\n{compact_text(doc.code_blocks[0], max_chars=850)}\n```")
    if pitfalls:
        lines.append("")
        lines.append("Pitfalls to avoid:")
        lines.append(compact_text(pitfalls.body, max_chars=500))
    lines.append("")
    lines.append(
        "Numeric boundary: do not fabricate measurements, fidelities, energies, or optimal parameters; "
        "return code, symbolic formulas, or reproducible procedures instead."
    )
    return "\n".join(lines).rstrip() + "\n"


def build_record(doc: QuantumDoc) -> dict[str, Any]:
    framework = detect_framework(doc)
    category = detect_category(doc)
    task_type = detect_task_type(doc)
    rel_path = doc.path.relative_to(ROOT).as_posix() if doc.path.is_absolute() and doc.path.is_relative_to(ROOT) else doc.path.as_posix()
    task_slug = slugify(doc.path.stem)
    headings = [section.heading for section in doc.sections]
    tags = sorted(set([task_slug, category, task_type, *(framework and [framework] or [])]))
    metadata = {
        "domain": "quantum",
        "category": category,
        "task_type": task_type,
        "difficulty": "medium",
        "language": "python" if doc.code_blocks else "text",
        "framework": framework,
        "target_framework": framework,
        "tags": tags,
        "source": SOURCE_NAME,
        "source_path": rel_path,
        "source_doc_sha256": doc.sha256,
        "source_title": doc.title,
        "source_headings": headings,
        "task_id": f"rag_doc_{task_slug}",
        "task_name": doc.title,
        "output_type": "code" if doc.code_blocks else "structured_text",
        "numeric_boundary": "doc_grounded_no_fabricated_results",
        "workflow": "rag_doc_to_seed_question",
        "holdout_policy": "source_docs_only_no_eval_holdout_files",
    }
    return {
        "format": FORMAT,
        "source_schema": SOURCE_SCHEMA,
        "example_id": f"rag_seed_{task_slug}_001",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(doc, framework, task_type)},
            {"role": "assistant", "content": build_assistant_answer(doc)},
        ],
        "metadata": metadata,
    }


def validate_records(records: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    for record in records:
        example_id = record.get("example_id")
        if not isinstance(example_id, str) or not example_id:
            raise ValueError("record missing example_id")
        if example_id in seen:
            raise ValueError(f"duplicate example_id: {example_id}")
        seen.add(example_id)
        if record.get("format") != FORMAT:
            raise ValueError(f"{example_id}: unexpected format")
        if record.get("source_schema") != SOURCE_SCHEMA:
            raise ValueError(f"{example_id}: unexpected source_schema")
        messages = record.get("messages")
        if not isinstance(messages, list) or [message.get("role") for message in messages] != ["system", "user", "assistant"]:
            raise ValueError(f"{example_id}: messages must be system/user/assistant")
        if any(not isinstance(message.get("content"), str) or not message["content"].strip() for message in messages):
            raise ValueError(f"{example_id}: messages must have non-empty content")
        metadata = record.get("metadata")
        if not isinstance(metadata, dict):
            raise ValueError(f"{example_id}: missing metadata")
        source_path = metadata.get("source_path")
        if not isinstance(source_path, str) or not source_path.startswith("docs/quantum_libraries/"):
            raise ValueError(f"{example_id}: source_path must remain inside docs/quantum_libraries")
        if any(part in Path(source_path).parts for part in HOLDOUT_PATH_PARTS):
            raise ValueError(f"{example_id}: source_path points at holdout/eval data")
        if metadata.get("holdout_policy") != "source_docs_only_no_eval_holdout_files":
            raise ValueError(f"{example_id}: missing holdout policy marker")


def build_records(docs_dir: Path = DEFAULT_DOCS_DIR, *, max_records: int | None = None) -> list[dict[str, Any]]:
    docs = iter_markdown_docs(docs_dir)
    if max_records is not None:
        docs = docs[:max_records]
    records = [build_record(doc) for doc in docs]
    validate_records(records)
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=True, sort_keys=True) + "\n")


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_category = Counter(record["metadata"]["category"] for record in records)
    by_task_type = Counter(record["metadata"]["task_type"] for record in records)
    by_framework = Counter(str(record["metadata"]["target_framework"]) for record in records)
    return {
        "count": len(records),
        "category": dict(sorted(by_category.items())),
        "task_type": dict(sorted(by_task_type.items())),
        "target_framework": dict(sorted(by_framework.items())),
        "source_paths": sorted(record["metadata"]["source_path"] for record in records),
    }


def write_manifest(path: Path, output_path: Path, docs_dir: Path, records: list[dict[str, Any]]) -> dict[str, Any]:
    manifest = {
        "manifest_version": SOURCE_SCHEMA,
        "format": FORMAT,
        "output": str(output_path),
        "docs_dir": str(docs_dir),
        "holdout_policy": "source_docs_only_no_eval_holdout_files",
        "summary": summarize(records),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=True, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    args = parse_args()
    records = build_records(args.docs_dir, max_records=args.max_records)
    write_jsonl(args.output, records)
    manifest = write_manifest(args.manifest, args.output, args.docs_dir, records)
    print(json.dumps(manifest, indent=2, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

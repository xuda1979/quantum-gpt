#!/usr/bin/env python3
"""Build ASI2-ready quantum distillation seed questions from local RAG docs."""

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
DEFAULT_DOC_ROOTS = (
    ROOT / "docs" / "quantum_libraries",
    ROOT / "docs" / "external" / "quantum-sdk-docs-latest",
)
DEFAULT_OUTPUT = ROOT / "data" / "seed" / "quantum_distillation_seed_questions_asi2_v1.jsonl"
DEFAULT_MANIFEST = (
    ROOT / "data" / "seed" / "quantum_distillation_seed_questions_asi2_v1_manifest.json"
)

SCHEMA_VERSION = "dataset-v0"
MANIFEST_VERSION = "quantum-distillation-seed-questions-asi2-v1"
SOURCE_NAME = "rag_docs_quantum_distillation_seed"
STUDENT_MODEL = "Qwen/Qwen3.6-35B-A3B"
TEACHER_MODEL = "DeepSeek-v4-pro"
TARGET_ENV = "ASI2"
HOLDOUT_PATH_PARTS = {"evals", "benchmarks", "runs", "tasks"}

FRAMEWORK_HINTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("qiskit", ("qiskit", "quantumcircuit", "ibm")),
    ("cirq", ("cirq", "linequbit", "google")),
    ("pennylane", ("pennylane", "qml.", "qnode")),
    ("braket", ("braket", "awdevice", "localsimulator", "amazon")),
    ("cuda-quantum", ("cuda", "cuda-q")),
    ("qutip", ("qutip",)),
    ("pyquil", ("pyquil", "quil")),
    ("openfermion", ("openfermion",)),
    ("mitiq", ("mitiq", "error mitigation")),
    ("pyzx", ("pyzx", "zx")),
    ("pytket", ("pytket", "tket")),
    ("qsharp", ("q#", "qsharp", "azure quantum")),
    ("isq", ("isq", "arclight")),
)

VARIANTS: tuple[dict[str, str], ...] = (
    # NOTE: the first four entries are pinned by tests and downstream task-type
    # expectations; append new task styles, do not reorder these four.
    {
        "kind": "implementation",
        "difficulty": "medium",
        "constraint": "Produce executable Python or precise pseudocode grounded only in the cited documentation.",
    },
    {
        "kind": "repair",
        "difficulty": "hard",
        "constraint": "Include a realistic failure mode, an error symptom, and a corrected implementation plan.",
    },
    {
        "kind": "agentic_trajectory",
        "difficulty": "hard",
        "constraint": "Frame this as a multi-turn agent task with a compile or simulator failure followed by self-repair.",
    },
    {
        "kind": "optimization",
        "difficulty": "hard",
        "constraint": "Provide a detailed strategy or code to optimize gate count, circuit depth, or compile physical qubits to a target hardware topology.",
    },
    {
        "kind": "unit_testing",
        "difficulty": "medium",
        "constraint": "Ask for pytest-style unit tests and at least one property-based or invariant check (e.g. unitarity, normalization, or known statevector) for the documented routine; tests must be runnable without fabricated expected numbers.",
    },
    {
        "kind": "benchmark_harness",
        "difficulty": "hard",
        "constraint": "Ask for a reproducible micro-benchmark or profiling harness that measures depth, gate count, or wall-clock for a documented operation; the harness must compute metrics at runtime and must not hardcode or invent benchmark numbers.",
    },
    {
        "kind": "noise_modeling",
        "difficulty": "hard",
        "constraint": "Ask for construction of a noise model or quantum channel (Kraus/depolarizing/amplitude-damping as supported) and a simulation that reports the resulting fidelity or distribution, grounded in the cited API.",
    },
    {
        "kind": "hardware_mapping",
        "difficulty": "hard",
        "constraint": "Ask for transpilation/routing of a logical circuit onto a concrete backend coupling map and basis gate set, reporting the post-mapping depth and added SWAP/2-qubit gate cost.",
    },
    {
        "kind": "api_grounded_qa",
        "difficulty": "medium",
        "constraint": "Ask a precise API-usage question answerable only from the cited documentation, requiring a short runnable example that calls the documented classes/methods with correct signatures.",
    },
    {
        "kind": "multi_framework_port",
        "difficulty": "hard",
        "constraint": "Ask to port the documented circuit or routine to a second quantum framework while preserving semantics, and to state one equivalence check (e.g. matching statevector or unitary) between the two implementations.",
    },
    {
        "kind": "error_mitigation",
        "difficulty": "hard",
        "constraint": "Ask for application of an error-mitigation technique (zero-noise extrapolation, probabilistic error cancellation, or measurement-error mitigation) with code, and a description of how the mitigated estimate is obtained at runtime.",
    },
    {
        "kind": "verification_plan",
        "difficulty": "hard",
        "constraint": "Ask for static/assertion checks plus a simulator smoke test that validate correctness of the documented routine, and a concise verification plan listing the properties checked.",
    },
)


@dataclass(frozen=True)
class DocChunk:
    path: Path
    title: str
    text: str
    sha256: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--doc-root", type=Path, action="append", default=None)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--max-source-docs", type=int, default=1000)
    parser.add_argument("--variants-per-doc", type=int, default=len(VARIANTS))
    return parser.parse_args()


def reject_holdout_path(path: Path) -> None:
    if set(path.parts) & HOLDOUT_PATH_PARTS:
        raise ValueError(f"refusing holdout/eval source path: {path}")


def compact_text(text: str, *, max_chars: int = 1800) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[:max_chars].rsplit(" ", 1)[0].rstrip() + "..."


def title_from_markdown(path: Path, text: str) -> str:
    match = re.search(r"^#\s+(.+?)\s*$", text, flags=re.MULTILINE)
    if match:
        return match.group(1).strip()
    stem = re.sub(r"-[0-9a-f]{8,}\.md$", "", path.name)
    stem = re.sub(r"\.html?|\.(md)$", "", stem)
    return stem.replace("_", " ").replace("-", " ").strip().title()


def read_doc_chunk(path: Path) -> DocChunk | None:
    if path.name == "README.md" or ".css-" in path.name:
        return None
    path_text = path.as_posix()
    if "_static" in path_text or "_modules" in path_text or ".js-" in path.name:
        return None
    reject_holdout_path(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    body = compact_text(text)
    if len(body.split()) < 40:
        return None
    return DocChunk(
        path=path,
        title=title_from_markdown(path, text),
        text=body,
        sha256=hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest(),
    )


def group_key(root: Path, path: Path) -> str:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return "_external"
    if root.name == "quantum_libraries":
        return "_curated_local"
    return relative.parts[0] if len(relative.parts) > 1 else "_external"


def iter_docs(doc_roots: tuple[Path, ...], *, max_source_docs: int) -> list[DocChunk]:
    grouped: dict[str, list[DocChunk]] = {}
    for root in doc_roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.md")):
            chunk = read_doc_chunk(path)
            if chunk is None:
                continue
            grouped.setdefault(group_key(root, path), []).append(chunk)

    docs: list[DocChunk] = list(grouped.pop("_curated_local", [])[:max_source_docs])
    if len(docs) >= max_source_docs:
        return docs[:max_source_docs]
    keys = sorted(grouped, key=lambda key: (key != "_curated_local", key))
    while len(docs) < max_source_docs:
        appended = False
        for key in keys:
            bucket = grouped[key]
            if not bucket:
                continue
            docs.append(bucket.pop(0))
            appended = True
            if len(docs) >= max_source_docs:
                break
        if not appended:
            break
    return docs


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_") or "quantum_doc"


def rel_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def detect_framework(doc: DocChunk) -> str | None:
    haystack = f"{rel_path(doc.path)}\n{doc.title}\n{doc.text[:1200]}".lower()
    for framework, needles in FRAMEWORK_HINTS:
        if any(needle in haystack for needle in needles):
            return framework
    return None


def detect_category(doc: DocChunk) -> str:
    haystack = f"{doc.title} {doc.text[:1400]}".lower()
    if any(term in haystack for term in ("error correction", "stabilizer", "syndrome", "qec")):
        return "error_correction"
    if any(
        term in haystack for term in ("transpil", "native gate", "topology", "compile", "routing")
    ):
        return "hardware_compilation"
    if any(term in haystack for term in ("noise", "mitigation", "channel", "kraus")):
        return "noise_and_mitigation"
    if any(
        term in haystack for term in ("qaoa", "vqe", "grover", "phase estimation", "hamiltonian")
    ):
        return "algorithm_implementation"
    if any(term in haystack for term in ("api", "class", "method", "function")):
        return "library_api_grounding"
    return "quantum_engineering"


def build_instruction(doc: DocChunk, variant: dict[str, str]) -> str:
    framework = detect_framework(doc)
    framework_text = f" using {framework}" if framework else ""
    return (
        f"From the RAG documentation topic `{doc.title}`{framework_text}, generate one complex "
        f"quantum software engineering task for a teacher model to solve. "
        f"Task style: {variant['kind']}. Constraint: {variant['constraint']} "
        "The generated instruction must explicitly ask for a complete standalone runnable code solution, "
        "including imports or module setup, a clear entry point or execution block, and a minimal self-check or printout that proves the code runs. "
        "It must be practical for agentic coding distillation and must not ask for fabricated benchmark numbers."
    )


def build_response_contract(doc: DocChunk, variant: dict[str, str]) -> str:
    return (
        "Teacher-response contract:\n"
        f"- Use `{TEACHER_MODEL}` as a black-box teacher and keep this as hard SFT data for `{STUDENT_MODEL}`.\n"
        "- Answer with a concise rationale summary, then final code or steps; do not require hidden chain-of-thought text.\n"
        "- Ground every API or hardware claim in the supplied RAG excerpt.\n"
        "- Prefer code that can be linted, unit-tested, simulated, or statically checked.\n"
        "- Reject or regenerate answers that fail syntax, import-surface, simulator, or static-consistency checks.\n\n"
        f"RAG excerpt from `{rel_path(doc.path)}`:\n{doc.text}\n\n"
        f"Evolution hint: {variant['kind']} / {variant['difficulty']}."
    )


def build_record(doc: DocChunk, variant: dict[str, str], variant_index: int) -> dict[str, Any]:
    framework = detect_framework(doc)
    source_path = rel_path(doc.path)
    # Include a short per-doc hash so docs that share a filename across the doc
    # tree cannot collide on example_id when many source docs are used.
    doc_tag = doc.sha256[:8]
    task_slug = slugify(f"{Path(source_path).stem}_{doc_tag}_{variant['kind']}")
    metadata = {
        "task_id": f"distill_seed_{task_slug}",
        "source_path": source_path,
        "source_doc_sha256": doc.sha256,
        "source_title": doc.title,
        "student_model": STUDENT_MODEL,
        "teacher_model": TEACHER_MODEL,
        "target_env": TARGET_ENV,
        "distillation_strategy": "hard_sft_black_box_teacher",
        "distillation_phase": "rag_seed_generation",
        "evolution_kind": variant["kind"],
        "holdout_policy": "rag_docs_only_no_eval_holdout_files",
    }
    tags = sorted(
        {
            "rag",
            "distillation",
            "asi2",
            variant["kind"],
            detect_category(doc),
            *(framework and [framework] or []),
        }
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "example_id": f"asi2_distill_{task_slug}_{variant_index:02d}",
        "domain": "quantum",
        "category": detect_category(doc),
        "task_type": variant["kind"],
        "source": SOURCE_NAME,
        "difficulty": variant["difficulty"],
        "language": "python",
        "framework": framework,
        "tags": tags,
        "instruction": build_instruction(doc, variant),
        "response": build_response_contract(doc, variant),
        "artifacts": {
            "rag_excerpt": doc.text,
            "teacher_prompt_policy": "concise_rationale_summary_plus_final_answer",
            "verification_targets": [
                "python_syntax",
                "unit_tests_when_available",
                "quantum_simulator_smoke",
                "static_api_consistency",
            ],
        },
        "metadata": metadata,
    }


def build_records(
    doc_roots: tuple[Path, ...] = DEFAULT_DOC_ROOTS,
    *,
    max_source_docs: int = 120,
    variants_per_doc: int = 4,
) -> list[dict[str, Any]]:
    if variants_per_doc < 1 or variants_per_doc > len(VARIANTS):
        raise ValueError(f"variants_per_doc must be between 1 and {len(VARIANTS)}")
    records: list[dict[str, Any]] = []
    for doc in iter_docs(doc_roots, max_source_docs=max_source_docs):
        for index, variant in enumerate(VARIANTS[:variants_per_doc], start=1):
            records.append(build_record(doc, variant, index))
    validate_records(records)
    return records


def validate_records(records: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    for record in records:
        example_id = record.get("example_id")
        if not isinstance(example_id, str) or not example_id:
            raise ValueError("record missing example_id")
        if example_id in seen:
            raise ValueError(f"duplicate example_id: {example_id}")
        seen.add(example_id)
        source_path = record["metadata"]["source_path"]
        if any(part in Path(source_path).parts for part in HOLDOUT_PATH_PARTS):
            raise ValueError(f"{example_id}: source_path points at holdout/eval data")
        if record["metadata"]["target_env"] != TARGET_ENV:
            raise ValueError(f"{example_id}: target_env must be {TARGET_ENV}")
        if record["metadata"]["distillation_strategy"] != "hard_sft_black_box_teacher":
            raise ValueError(f"{example_id}: unexpected distillation strategy")
        if "<think>" in record["response"].lower():
            raise ValueError(f"{example_id}: response contract must not require hidden CoT markers")


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=True, sort_keys=True) + "\n")


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "count": len(records),
        "category": dict(sorted(Counter(record["category"] for record in records).items())),
        "framework": dict(sorted(Counter(str(record["framework"]) for record in records).items())),
        "task_type": dict(sorted(Counter(record["task_type"] for record in records).items())),
        "source_doc_count": len({record["metadata"]["source_doc_sha256"] for record in records}),
        "source_paths": sorted({record["metadata"]["source_path"] for record in records}),
        "target_env": TARGET_ENV,
        "student_model": STUDENT_MODEL,
        "teacher_model": TEACHER_MODEL,
        "distillation_strategy": "hard_sft_black_box_teacher",
    }


def write_manifest(path: Path, output_path: Path, records: list[dict[str, Any]]) -> dict[str, Any]:
    manifest = {
        "manifest_version": MANIFEST_VERSION,
        "format": SCHEMA_VERSION,
        "output": str(output_path),
        "doc_roots": [str(path) for path in DEFAULT_DOC_ROOTS],
        "holdout_policy": "rag_docs_only_no_eval_holdout_files",
        "summary": summarize(records),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    args = parse_args()
    doc_roots = tuple(args.doc_root) if args.doc_root else DEFAULT_DOC_ROOTS
    records = build_records(
        doc_roots,
        max_source_docs=args.max_source_docs,
        variants_per_doc=args.variants_per_doc,
    )
    write_jsonl(args.output, records)
    manifest = write_manifest(args.manifest, args.output, records)
    print(json.dumps(manifest, indent=2, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

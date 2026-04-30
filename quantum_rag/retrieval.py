from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .corpus import DocumentChunk
from .index import QuantumRAGIndex


TOKEN_RE = re.compile(r"[A-Za-z0-9_./:+-]+")

TERM_EXPANSIONS = {
    "vqe": ["variational quantum eigensolver", "ground state", "ansatz"],
    "qaoa": ["quantum approximate optimization algorithm", "mixer hamiltonian", "cost hamiltonian"],
    "qpe": ["quantum phase estimation", "eigenphase"],
    "qft": ["quantum fourier transform", "phase pattern"],
    "ghz": ["greenberger h-orne zeilinger", "entanglement"],
    "qiskit": ["transpile", "aer", "quantum circuit"],
    "braket": ["amazon braket", "local simulator"],
    "pennylane": ["qml", "variational circuit"],
    "cirq": ["google cirq", "moment"],
    "lo_ra": ["adapter", "peft"],
    "grpo": ["policy optimization", "reward model", "group relative"],
    "rag": ["retrieval augmented generation", "hybrid retrieval", "citation"],
    "superdense": ["superdense coding", "bell pair", "two classical bits"],
    "teleportation": ["quantum teleportation", "bell measurement", "corrections"],
    "shor": ["shor code", "9-qubit", "error correction"],
    "grover": ["grover search", "oracle", "diffusion operator"],
    "arclight": ["isq", "isq compiler", "isqc"],
    "isq": ["arclight", "isq compiler", "isqc"],
}

SOURCE_PRIORITY_RULES: list[tuple[str, float]] = [
    ("evals/tasks/quantum/", 1.35),
    ("evals/benchmarks/", 1.25),
    ("AGENTS.md", 1.2),
    ("HEARTBEAT.md", 1.2),
    ("PROJECT.md", 1.15),
    ("TOOLS.md", 1.15),
    ("research/quantum_rag_low_compute.md", 1.15),
]

QUERY_AWARE_RULES: list[tuple[tuple[str, ...], tuple[str, ...], float]] = [
    (("qiskit", "quantumcircuit", "quantum circuit"), ("qiskit", "qiskit_basics"), 1.8),
    (("cirq",), ("cirq", "cirq_basics"), 1.8),
    (("pennylane", "qml"), ("pennylane", "pennylane_basics"), 1.8),
    (("braket", "amazon braket"), ("amazon-braket", "braket_basics"), 1.8),
    (("cuda-q", "cuda quantum"), ("cuda-quantum",), 1.8),
    (("qutip",), ("qutip",), 1.8),
    (("pyquil", "rigetti"), ("pyquil",), 1.8),
    (("openfermion",), ("openfermion",), 1.8),
    (("mitiq",), ("mitiq",), 1.8),
    (("pyzx",), ("pyzx",), 1.8),
    (("tket", "pytket", "quantinuum"), ("pytket",), 1.8),
    (("define", "defined", "definition", "task", "contract"), ("task.json",), 1.35),
    (("implement", "implementation", "reference", "candidate"), ("candidate.py",), 1.25),
    (("test", "tests", "verification"), ("tests.py",), 1.15),
    (("benchmark", "benchmark file", "training tasks", "grpo"), ("evals/benchmarks/",), 1.35),
    (("support", "supports", "gaps", "current", "low-compute", "rag"), ("research/quantum_rag_low_compute.md",), 1.5),
    (("grpo", "training command", "verified", "training workflow", "launch"), ("HEARTBEAT.md",), 1.4),
    (("arclight", "isq", "isqc"), ("arclight-isq", "isq-docs"), 2.0),
]


@dataclass(frozen=True)
class QueryExpansionConfig:
    enabled: bool = True
    include_original: bool = True


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: DocumentChunk
    rank: int
    final_score: float
    lexical_score: float
    semantic_score: float


def source_priority_multiplier(source_path: str) -> float:
    multiplier = 1.0
    for pattern, value in SOURCE_PRIORITY_RULES:
        if pattern in source_path:
            multiplier = max(multiplier, value)
    return multiplier


def query_aware_multiplier(query: str, source_path: str) -> float:
    lowered_query = query.lower()
    multiplier = 1.0
    for query_terms, source_patterns, value in QUERY_AWARE_RULES:
        if not any(term in lowered_query for term in query_terms):
            continue
        if any(pattern in source_path for pattern in source_patterns):
            multiplier = max(multiplier, value)
    return multiplier


def _query_tokens(query: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(query)}


def _filename_role_score(query: str, source_path: str) -> float:
    lowered_query = query.lower()
    filename = Path(source_path).name.lower()
    score = 0.0
    if any(term in lowered_query for term in ("define", "defined", "definition", "contract", "task")):
        if filename == "task.json":
            score += 0.8
        if filename == "candidate.py":
            score += 0.4
        if filename == "tests.py":
            score -= 0.35
    if any(term in lowered_query for term in ("implement", "implementation", "reference", "candidate")):
        if filename.endswith("_eval_api.md") or "eval_api" in source_path.lower():
            score += 1.1
        if filename == "candidate.py":
            score += 0.8
        if filename == "task.json":
            score += 0.2
        if filename == "tests.py":
            score -= 0.2
    if any(term in lowered_query for term in ("support", "supports", "gaps", "low-compute", "rag")):
        if "research/quantum_rag_low_compute.md" in source_path:
            score += 1.0
        if filename in {"agents.md", "heartbeat.md", "project.md"}:
            score -= 0.1
    if any(term in lowered_query for term in ("benchmark", "benchmark file")):
        if "evals/benchmarks/" in source_path:
            score += 0.7
        # Prefer the specific benchmark mentioned in operational docs
        if any(term in lowered_query for term in ("grpo", "training")):
            if "grpo_training" in source_path.lower():
                score += 0.6
            if filename == "heartbeat.md":
                score += 0.5
    if any(term in lowered_query for term in ("evaluate", "evaluation", "holdout", "before training")):
        if filename in {"project.md"}:
            score += 0.6
        if "research/quantum_rag_low_compute.md" in source_path:
            score += 0.4
        # Generic task.json files should not rank for evaluation policy queries
        if filename == "task.json":
            score -= 0.6
    if any(term in lowered_query for term in ("training command", "verified", "training workflow", "launch command")):
        if filename == "heartbeat.md":
            score += 1.2
        # Benchmark listing files should not dominate for command queries
        if "evals/benchmarks/" in source_path and filename.endswith(".txt"):
            score -= 0.5
    if any(term in lowered_query for term in ("install", "installation", "verify", "available", "isqc")):
        if "install" in source_path.lower():
            score += 1.0
        if "usage" in source_path.lower():
            score += 0.3
    if any(term in lowered_query for term in ("grpo",)):
        if filename == "heartbeat.md":
            score += 0.4
        if "evals/benchmarks/" in source_path:
            score += 0.3
    if any(term in lowered_query for term in ("arclight", "isq", "isqc")):
        if "arclight-isq" in source_path or "isq-docs" in source_path:
            score += 2.2
        elif "mitiq" in source_path:
            score -= 1.5
    return score


TASK_NAME_KEYWORDS: dict[str, list[str]] = {
    "qft": ["qft", "fourier"],
    "vqe": ["vqe", "eigensolver", "variational quantum eigensolver"],
    "qaoa": ["qaoa", "maxcut"],
    "ghz": ["ghz", "greenberger"],
    "grover": ["grover", "oracle", "diffusion"],
    "teleportation": ["teleportation", "teleport"],
    "shor": ["shor", "9-qubit", "9 qubit"],
    "superdense": ["superdense"],
    "error_detection": ["error detection", "bit flip", "bit-flip"],
    "phase_estimation": ["phase estimation"],
    "phase_register": ["phase register"],
    "density_matrix": ["density matrix", "partial trace"],
    "gate_alias": ["gate alias", "normalization"],
}


def _path_specificity_score(query: str, source_path: str) -> float:
    """Boost chunks whose source path matches a task name mentioned in the query.

    Penalise task.json chunks from *other* tasks that don't match the query,
    preventing generic task files from acting as universal attractors.
    """
    lowered_query = query.lower()
    path_lower = source_path.lower()

    # Identify which task families the query is about
    query_task_families: set[str] = set()
    for family, keywords in TASK_NAME_KEYWORDS.items():
        if any(kw in lowered_query for kw in keywords):
            query_task_families.add(family)

    if not query_task_families:
        return 0.0

    # Check if this chunk's path matches any of those families
    path_matches = any(family in path_lower for family in query_task_families)

    if path_matches:
        return 0.6  # bonus for path-specific match
    elif "/task.json" in path_lower or "/candidate.py" in path_lower:
        # Penalise task artifacts from unrelated tasks
        return -0.9
    return 0.0


def rerank_score(query: str, chunk: DocumentChunk, retrieved: RetrievedChunk) -> float:
    tokens = _query_tokens(query)
    chunk_tokens = {token.lower() for token in TOKEN_RE.findall(chunk.text)}
    lexical_overlap = len(tokens & chunk_tokens)
    normalized_overlap = lexical_overlap / max(len(tokens), 1)
    path_text = chunk.source_path.lower()
    path_overlap = sum(1 for token in tokens if token in path_text) / max(len(tokens), 1)
    role_score = _filename_role_score(query, chunk.source_path)
    specificity_score = _path_specificity_score(query, chunk.source_path)

    # Penalise benchmark/eval JSON files that contain literal query text
    # (self-referencing retrieval benchmark)
    benchmark_penalty = 0.0
    if "quantum_rag_retrieval" in path_text:
        benchmark_penalty = -1.5

    return (
        retrieved.final_score
        + 0.45 * normalized_overlap
        + 0.2 * path_overlap
        + role_score
        + specificity_score
        + benchmark_penalty
    )


def expand_query(query: str, config: QueryExpansionConfig | None = None) -> str:
    config = config or QueryExpansionConfig()
    if not config.enabled:
        return query

    lowered_query = query.lower()
    expanded_terms: list[str] = [query] if config.include_original else []
    tokens = set(TOKEN_RE.findall(lowered_query))
    for token in tokens:
        for candidate in TERM_EXPANSIONS.get(token, []):
            expanded_terms.append(candidate)

    for acronym, expansions in TERM_EXPANSIONS.items():
        if acronym in lowered_query:
            expanded_terms.extend(expansions)
            continue
        for expansion in expansions:
            if expansion in lowered_query:
                expanded_terms.append(acronym)
                break

    return "\n".join(dict.fromkeys(term for term in expanded_terms if term.strip()))


def retrieve(
    index: QuantumRAGIndex,
    query: str,
    *,
    top_k: int = 6,
    rerank_pool_size: int = 20,
    alpha: float = 0.55,
    expansion: QueryExpansionConfig | None = None,
    max_chunks_per_source: int | None = None,
    exclude_source_substrings: list[str] | None = None,
) -> list[RetrievedChunk]:
    expanded_query = expand_query(query, expansion)
    lexical_scores, semantic_scores, final_scores = index.hybrid_scores(expanded_query, alpha=alpha)
    adjusted_scores = final_scores.copy()
    for index_position, chunk in enumerate(index.chunks):
        adjusted_scores[index_position] *= source_priority_multiplier(chunk.source_path)
        adjusted_scores[index_position] *= query_aware_multiplier(query, chunk.source_path)
    ranked_indices = adjusted_scores.argsort()[::-1]
    candidate_results: list[RetrievedChunk] = []
    source_counts: dict[str, int] = {}
    exclude_patterns = exclude_source_substrings or []
    for chunk_index in ranked_indices:
        chunk = index.chunks[int(chunk_index)]
        if any(pattern in chunk.source_path for pattern in exclude_patterns):
            continue
        source_count = source_counts.get(chunk.source_path, 0)
        if max_chunks_per_source is not None and source_count >= max_chunks_per_source:
            continue
        source_counts[chunk.source_path] = source_count + 1
        candidate_results.append(
            RetrievedChunk(
                chunk=chunk,
                rank=len(candidate_results) + 1,
                final_score=float(adjusted_scores[int(chunk_index)]),
                lexical_score=float(lexical_scores[int(chunk_index)]),
                semantic_score=float(semantic_scores[int(chunk_index)]),
            )
        )
        if len(candidate_results) >= max(top_k, rerank_pool_size):
            break

    reranked = sorted(
        candidate_results,
        key=lambda item: rerank_score(query, item.chunk, item),
        reverse=True,
    )[:top_k]

    return [
        RetrievedChunk(
            chunk=item.chunk,
            rank=rank,
            final_score=rerank_score(query, item.chunk, item),
            lexical_score=item.lexical_score,
            semantic_score=item.semantic_score,
        )
        for rank, item in enumerate(reranked, start=1)
    ]

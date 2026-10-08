"""Lightweight RAG generation evaluation (RAGAS-lite).

Provides simple automated metrics for evaluating RAG answer quality
without requiring an external evaluation model. The metrics focus on:

- **Faithfulness**: Does the answer cite retrieved chunks?
- **Relevance**: Does the answer address the query?
- **Groundedness**: Are citations actually backed by chunk content?

These are intentionally simple lexical/heuristic metrics, not
model-graded. They are designed to flag obvious regressions and give
a coarse quality signal during development.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from .retrieval import RetrievedChunk


CITATION_RE = re.compile(r"\[C(\d+)\]")
TOKEN_RE = re.compile(r"[A-Za-z0-9_./:+-]+")


@dataclass(frozen=True)
class AnswerEvalResult:
    query: str
    answer: str
    num_citations: int
    num_valid_citations: int
    num_retrieved: int
    faithfulness_score: float
    relevance_score: float
    groundedness_score: float
    composite_score: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _token_set(text: str) -> set[str]:
    return {t.lower() for t in TOKEN_RE.findall(text)}


def _citation_ranks(answer: str) -> list[int]:
    """Extract all [C<n>] citation ranks from an answer."""
    return [int(m) for m in CITATION_RE.findall(answer)]


def faithfulness_score(answer: str, num_retrieved: int) -> float:
    """Fraction of retrieved chunks that are cited in the answer.

    A perfect score means every retrieved chunk was referenced.
    A zero score means no citations at all.
    """
    if num_retrieved == 0:
        return 0.0
    cited_ranks = set(_citation_ranks(answer))
    valid_cited = {r for r in cited_ranks if 1 <= r <= num_retrieved}
    return len(valid_cited) / num_retrieved


def relevance_score(query: str, answer: str) -> float:
    """Lexical overlap between query tokens and answer tokens.

    This is a crude proxy for whether the answer addresses the query.
    """
    query_tokens = _token_set(query)
    answer_tokens = _token_set(answer)
    if not query_tokens:
        return 0.0
    return len(query_tokens & answer_tokens) / len(query_tokens)


def groundedness_score(
    answer: str,
    chunks: list[RetrievedChunk],
) -> float:
    """Check how many cited chunks actually contain answer-specific tokens.

    For each cited chunk [C<n>], we check whether the answer text near the
    citation shares significant token overlap with the chunk content. The
    score is the fraction of citations that are grounded.
    """
    cited_ranks = _citation_ranks(answer)
    if not cited_ranks:
        return 0.0

    chunk_by_rank = {c.rank: c for c in chunks}
    grounded_count = 0

    for rank in cited_ranks:
        chunk = chunk_by_rank.get(rank)
        if chunk is None:
            continue
        chunk_tokens = _token_set(chunk.chunk.text)
        answer_tokens = _token_set(answer)
        # A citation is grounded if the chunk and answer share meaningful overlap
        overlap = len(chunk_tokens & answer_tokens)
        if overlap >= 3:
            grounded_count += 1

    return grounded_count / len(cited_ranks)


def evaluate_answer(
    query: str,
    answer: str,
    chunks: list[RetrievedChunk],
    *,
    faithfulness_weight: float = 0.3,
    relevance_weight: float = 0.4,
    groundedness_weight: float = 0.3,
) -> AnswerEvalResult:
    """Run all evaluation metrics and return a composite result."""
    cited_ranks = _citation_ranks(answer)
    num_retrieved = len(chunks)
    valid_citations = [r for r in cited_ranks if 1 <= r <= num_retrieved]

    faith = faithfulness_score(answer, num_retrieved)
    relev = relevance_score(query, answer)
    ground = groundedness_score(answer, chunks)

    composite = (
        faithfulness_weight * faith
        + relevance_weight * relev
        + groundedness_weight * ground
    )

    return AnswerEvalResult(
        query=query,
        answer=answer,
        num_citations=len(cited_ranks),
        num_valid_citations=len(valid_citations),
        num_retrieved=num_retrieved,
        faithfulness_score=faith,
        relevance_score=relev,
        groundedness_score=ground,
        composite_score=composite,
    )

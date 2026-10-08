from __future__ import annotations

import gzip
import math
import pickle
import re
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

from .corpus import DocumentChunk


TOKEN_RE = re.compile(r"[A-Za-z0-9_./:+-]+")


def tokenize_for_bm25(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


@dataclass
class BM25Index:
    document_lengths: np.ndarray
    average_document_length: float
    vocabulary: dict[str, int]
    idf: np.ndarray
    term_frequencies: np.ndarray
    k1: float = 1.5
    b: float = 0.75

    @classmethod
    def fit(cls, texts: list[str], *, k1: float = 1.5, b: float = 0.75) -> "BM25Index":
        tokenized_docs = [tokenize_for_bm25(text) for text in texts]
        vocabulary: dict[str, int] = {}
        for tokens in tokenized_docs:
            for token in tokens:
                if token not in vocabulary:
                    vocabulary[token] = len(vocabulary)

        term_frequencies = np.zeros((len(texts), len(vocabulary)), dtype=np.float32)
        document_frequencies = np.zeros(len(vocabulary), dtype=np.float32)
        document_lengths = np.zeros(len(texts), dtype=np.float32)

        for doc_index, tokens in enumerate(tokenized_docs):
            document_lengths[doc_index] = len(tokens)
            seen: set[int] = set()
            for token in tokens:
                token_index = vocabulary[token]
                term_frequencies[doc_index, token_index] += 1.0
                seen.add(token_index)
            for token_index in seen:
                document_frequencies[token_index] += 1.0

        document_count = max(len(texts), 1)
        idf = np.log1p((document_count - document_frequencies + 0.5) / (document_frequencies + 0.5))
        average_document_length = float(document_lengths.mean()) if len(document_lengths) else 0.0
        return cls(
            document_lengths=document_lengths,
            average_document_length=average_document_length,
            vocabulary=vocabulary,
            idf=idf.astype(np.float32),
            term_frequencies=term_frequencies,
            k1=k1,
            b=b,
        )

    def score(self, query: str) -> np.ndarray:
        scores = np.zeros(len(self.document_lengths), dtype=np.float32)
        query_terms = tokenize_for_bm25(query)
        if not query_terms.any if isinstance(query_terms, np.ndarray) else not query_terms:
            return scores

        average_document_length = self.average_document_length or 1.0
        for token in query_terms:
            token_index = self.vocabulary.get(token)
            if token_index is None:
                continue
            tf = self.term_frequencies[:, token_index]
            numerator = tf * (self.k1 + 1.0)
            denominator = tf + self.k1 * (
                1.0 - self.b + self.b * (self.document_lengths / average_document_length)
            )
            scores += self.idf[token_index] * np.divide(
                numerator,
                denominator,
                out=np.zeros_like(numerator),
                where=denominator != 0,
            )
        return scores


def _normalize_rows(matrix: np.ndarray) -> np.ndarray:
    if matrix.size == 0:
        return matrix
    matrix = np.nan_to_num(matrix, nan=0.0, posinf=0.0, neginf=0.0)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    normalized = matrix / norms
    return np.nan_to_num(normalized, nan=0.0, posinf=0.0, neginf=0.0)


def _minmax(scores: np.ndarray, *, clip_percentile: float = 95.0) -> np.ndarray:
    """Normalize scores to [0, 1] with percentile clipping for outlier robustness.

    Plain min-max normalization is highly sensitive to outlier scores (e.g. a
    benchmark file that contains the literal query text).  Clipping at the
    *clip_percentile*-th value before computing the range prevents a single
    high-scoring outlier from crushing all other scores to near-zero.
    """
    if scores.size == 0:
        return scores
    minimum = float(scores.min())
    # Use percentile as the effective maximum so outliers don't dominate
    clip_max = float(np.percentile(scores, clip_percentile))
    if math.isclose(minimum, clip_max):
        maximum = float(scores.max())
        if math.isclose(minimum, maximum):
            return np.zeros_like(scores)
        clip_max = maximum
    clipped = np.clip(scores, minimum, clip_max)
    return (clipped - minimum) / (clip_max - minimum)


@dataclass
class QuantumRAGIndex:
    chunks: list[DocumentChunk]
    vectorizer: TfidfVectorizer
    dense_transform: TruncatedSVD | None
    tfidf_matrix: object
    dense_matrix: np.ndarray
    bm25: BM25Index

    @classmethod
    def build(
        cls,
        chunks: list[DocumentChunk],
        *,
        max_features: int = 50000,
        dense_components: int = 192,
    ) -> "QuantumRAGIndex":
        texts = [chunk.text for chunk in chunks]
        vectorizer = TfidfVectorizer(
            lowercase=True,
            analyzer="word",
            ngram_range=(1, 2),
            max_features=max_features,
            token_pattern=r"(?u)\b[\w./:+-]+\b",
            sublinear_tf=True,
        )
        tfidf_matrix = vectorizer.fit_transform(texts)

        dense_transform: TruncatedSVD | None = None
        if tfidf_matrix.shape[0] > 2 and tfidf_matrix.shape[1] > 2:
            max_valid_components = min(
                dense_components,
                tfidf_matrix.shape[0] - 1,
                tfidf_matrix.shape[1] - 1,
            )
            if max_valid_components >= 2:
                candidate_transform = TruncatedSVD(
                    n_components=max_valid_components,
                    random_state=42,
                )
                with warnings.catch_warnings(record=True) as caught_warnings:
                    warnings.simplefilter("always", RuntimeWarning)
                    candidate_dense_matrix = candidate_transform.fit_transform(tfidf_matrix)
                has_runtime_warning = any(
                    issubclass(item.category, RuntimeWarning) for item in caught_warnings
                )
                if has_runtime_warning or not np.isfinite(candidate_dense_matrix).all():
                    dense_matrix = tfidf_matrix.toarray()
                else:
                    dense_transform = candidate_transform
                    dense_matrix = candidate_dense_matrix
            else:
                dense_matrix = tfidf_matrix.toarray()
        else:
            dense_matrix = tfidf_matrix.toarray()

        dense_matrix = _normalize_rows(np.asarray(dense_matrix, dtype=np.float32))
        bm25 = BM25Index.fit(texts)
        return cls(
            chunks=chunks,
            vectorizer=vectorizer,
            dense_transform=dense_transform,
            tfidf_matrix=tfidf_matrix,
            dense_matrix=dense_matrix,
            bm25=bm25,
        )

    def summary(self) -> dict[str, object]:
        unique_sources = len({chunk.source_path for chunk in self.chunks})
        return {
            "chunk_count": len(self.chunks),
            "source_count": unique_sources,
            "vectorizer_features": len(self.vectorizer.vocabulary_),
            "dense_dimensions": int(self.dense_matrix.shape[1]) if self.dense_matrix.ndim == 2 else 0,
        }

    def semantic_scores(self, query: str) -> np.ndarray:
        if not query.strip():
            return np.zeros(len(self.chunks), dtype=np.float32)
        query_tfidf = self.vectorizer.transform([query])
        if self.dense_transform is not None:
            query_dense = self.dense_transform.transform(query_tfidf)
        else:
            query_dense = query_tfidf.toarray()
        query_dense = np.asarray(query_dense, dtype=np.float32)
        query_dense = _normalize_rows(query_dense)
        if query_dense.size == 0:
            return np.zeros(len(self.chunks), dtype=np.float32)
        safe_dense_matrix = np.nan_to_num(self.dense_matrix, nan=0.0, posinf=0.0, neginf=0.0)
        safe_query = np.nan_to_num(query_dense[0], nan=0.0, posinf=0.0, neginf=0.0)
        with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
            scores = safe_dense_matrix @ safe_query
        return np.nan_to_num(scores, nan=0.0, posinf=0.0, neginf=0.0)

    def hybrid_scores(self, query: str, *, alpha: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        lexical = self.bm25.score(query)
        semantic = self.semantic_scores(query)
        combined = alpha * _minmax(lexical) + (1.0 - alpha) * _minmax(semantic)
        return lexical, semantic, combined

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": 1,
            "chunks": self.chunks,
            "vectorizer": self.vectorizer,
            "dense_transform": self.dense_transform,
            "tfidf_matrix": self.tfidf_matrix,
            "dense_matrix": self.dense_matrix,
            "bm25": self.bm25,
        }
        with gzip.open(path, "wb") as handle:
            pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, path: Path) -> "QuantumRAGIndex":
        # Index artifacts may be built with NumPy 2.x and loaded in an
        # environment pinned to NumPy 1.x.  NumPy 2 pickles can reference
        # numpy._core.*, while NumPy 1 exposes the same modules under
        # numpy.core.*.
        sys.modules.setdefault("numpy._core", np.core)
        sys.modules.setdefault("numpy._core.numeric", np.core.numeric)
        sys.modules.setdefault("numpy._core.multiarray", np.core.multiarray)
        with gzip.open(path, "rb") as handle:
            payload = pickle.load(handle)
        return cls(
            chunks=payload["chunks"],
            vectorizer=payload["vectorizer"],
            dense_transform=payload["dense_transform"],
            tfidf_matrix=payload["tfidf_matrix"],
            dense_matrix=payload["dense_matrix"],
            bm25=payload["bm25"],
        )

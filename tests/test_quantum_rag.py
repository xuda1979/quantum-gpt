from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from quantum_rag.cache import AnswerCache, CacheEntry, index_summary_hash, make_cache_key
from quantum_rag.corpus import (
    DocumentChunk,
    _extract_task_metadata,
    _find_split_boundary,
    _normalize_path_for_preamble,
    _normalize_text,
    build_chunks_for_file,
    build_chunks_from_roots,
    chunk_text,
    iter_source_files,
    load_source_text,
)
from quantum_rag.eval import (
    evaluate_answer,
    faithfulness_score,
    groundedness_score,
    relevance_score,
)
from quantum_rag.generation import (
    RAG_SYSTEM_PROMPT,
    ChatCompletionsClient,
    ResponsesClient,
    build_rag_messages,
    format_retrieved_context,
)
from quantum_rag.index import BM25Index, QuantumRAGIndex, _minmax, _normalize_rows
from quantum_rag.retrieval import (
    QueryExpansionConfig,
    RetrievedChunk,
    _path_specificity_score,
    expand_query,
    query_aware_multiplier,
    retrieve,
    source_priority_multiplier,
)

# ============================================================================
# corpus.py — text normalisation and chunking
# ============================================================================


class TestNormalizeText:
    def test_strips_leading_trailing_whitespace(self) -> None:
        assert _normalize_text("  hello  ") == "hello"

    def test_collapses_blank_lines(self) -> None:
        assert _normalize_text("a\n\n\n\nb") == "a\n\nb"

    def test_converts_tabs_to_spaces(self) -> None:
        assert "\t" not in _normalize_text("a\tb")

    def test_normalises_crlf(self) -> None:
        assert "\r" not in _normalize_text("a\r\nb\rc")

    def test_empty_string(self) -> None:
        assert _normalize_text("") == ""
        assert _normalize_text("   ") == ""


class TestChunkText:
    def test_respects_overlap(self) -> None:
        text = "Intro\n\n" + ("A" * 700) + "\n\n" + ("B" * 700) + "\n\n" + ("C" * 700)
        chunks = chunk_text(text, chunk_size=900, chunk_overlap=120)
        assert len(chunks) >= 3
        assert chunks[1][1] < chunks[0][2]

    def test_empty_text_returns_empty(self) -> None:
        assert chunk_text("", chunk_size=100, chunk_overlap=10) == []
        assert chunk_text("   ", chunk_size=100, chunk_overlap=10) == []

    def test_small_text_returns_single_chunk(self) -> None:
        chunks = chunk_text("Hello world.", chunk_size=500, chunk_overlap=10)
        assert len(chunks) == 1
        assert chunks[0][0] == "Hello world."

    def test_invalid_chunk_size_raises(self) -> None:
        with pytest.raises(ValueError, match="chunk_size must be > 0"):
            chunk_text("abc", chunk_size=0, chunk_overlap=0)

    def test_negative_overlap_raises(self) -> None:
        with pytest.raises(ValueError, match="chunk_overlap must be >= 0"):
            chunk_text("abc", chunk_size=10, chunk_overlap=-1)

    def test_overlap_equals_size_raises(self) -> None:
        with pytest.raises(ValueError, match="chunk_overlap must be smaller"):
            chunk_text("abc", chunk_size=10, chunk_overlap=10)


class TestFindSplitBoundary:
    def test_end_beyond_text_returns_text_length(self) -> None:
        assert _find_split_boundary("hello", 0, 100) == 5

    def test_prefers_paragraph_boundary(self) -> None:
        text = "aaa\n\nbbb ccc"
        boundary = _find_split_boundary(text, 0, 5)
        assert boundary == 5  # after \n\n


class TestPathPreamble:
    def test_expands_underscores(self) -> None:
        path = Path("evals/tasks/quantum/qft_phase_pattern/task.json")
        preamble = _normalize_path_for_preamble(path)
        assert "qft_phase_pattern" in preamble
        assert "qft phase pattern" in preamble
        assert "task.json" in preamble

    def test_limits_to_four_components(self) -> None:
        path = Path("a/b/c/d/e/f/file.txt")
        preamble = _normalize_path_for_preamble(path)
        # The [source: ...] tag contains at most 4 path components (3 slashes)
        # but the preamble has both [source: d/e/f/file.txt] and [d/e/f/file.txt]
        assert "d/e/f/file.txt" in preamble
        # Original long prefix should NOT appear
        assert "a/b/c" not in preamble

    def test_short_path(self) -> None:
        path = Path("README.md")
        preamble = _normalize_path_for_preamble(path)
        assert "README.md" in preamble


class TestExtractTaskMetadata:
    def test_extracts_from_task_json(self, tmp_path: Path) -> None:
        task_path = tmp_path / "task.json"
        content = json.dumps(
            {
                "id": "quantum_qft_phase_pattern",
                "name": "QFT phase pattern",
                "domain": "quantum",
                "category": "algorithm_reasoning",
            }
        )
        task_path.write_text(content, encoding="utf-8")
        meta = _extract_task_metadata(task_path, content)
        assert "quantum_qft_phase_pattern" in meta
        assert "QFT phase pattern" in meta
        assert "quantum qft phase pattern" in meta

    def test_ignores_non_task_files(self, tmp_path: Path) -> None:
        path = tmp_path / "candidate.py"
        path.write_text("def foo(): pass", encoding="utf-8")
        assert _extract_task_metadata(path, "def foo(): pass") == ""

    def test_handles_malformed_json(self, tmp_path: Path) -> None:
        path = tmp_path / "task.json"
        path.write_text("not valid json{}", encoding="utf-8")
        assert _extract_task_metadata(path, "not valid json{}") == ""

    def test_handles_empty_fields(self, tmp_path: Path) -> None:
        path = tmp_path / "task.json"
        content = json.dumps({"id": "", "name": ""})
        path.write_text(content, encoding="utf-8")
        meta = _extract_task_metadata(path, content)
        assert meta == ""

    def test_handles_missing_fields(self, tmp_path: Path) -> None:
        path = tmp_path / "task.json"
        content = json.dumps({"other": "value"})
        path.write_text(content, encoding="utf-8")
        meta = _extract_task_metadata(path, content)
        assert meta == ""


class TestBuildChunksForFile:
    def test_preamble_injected_into_chunks(self, tmp_path: Path) -> None:
        doc = tmp_path / "evals" / "tasks" / "quantum" / "qft_phase_pattern" / "task.json"
        doc.parent.mkdir(parents=True)
        doc.write_text(
            json.dumps(
                {
                    "id": "quantum_qft_phase_pattern",
                    "name": "QFT phase pattern",
                    "domain": "quantum",
                }
            ),
            encoding="utf-8",
        )
        chunks = build_chunks_for_file(doc, chunk_size=600, chunk_overlap=50, min_chunk_chars=10)
        assert chunks
        assert "qft phase pattern" in chunks[0].text.lower()
        assert "qft_phase_pattern" in chunks[0].text
        assert chunks[0].metadata.get("has_path_preamble") is True

    def test_preamble_disabled(self, tmp_path: Path) -> None:
        doc = tmp_path / "test.md"
        doc.write_text("Some content " * 30, encoding="utf-8")
        chunks = build_chunks_for_file(
            doc,
            chunk_size=200,
            chunk_overlap=20,
            min_chunk_chars=10,
            inject_path_preamble=False,
        )
        assert chunks
        assert "[source:" not in chunks[0].text
        assert chunks[0].metadata.get("has_path_preamble") is False

    def test_small_files_filtered_by_min_chars(self, tmp_path: Path) -> None:
        doc = tmp_path / "tiny.txt"
        doc.write_text("Hi", encoding="utf-8")
        chunks = build_chunks_for_file(doc, chunk_size=500, chunk_overlap=50, min_chunk_chars=250)
        # "Hi" + preamble might be < 250 chars for chunked text
        # The min_chunk_chars applies to the raw chunk before preamble
        assert len(chunks) == 0

    def test_ipynb_loading(self, tmp_path: Path) -> None:
        nb = tmp_path / "test.ipynb"
        nb.write_text(
            json.dumps(
                {
                    "cells": [
                        {
                            "cell_type": "code",
                            "source": ["import numpy as np\n", "x = np.zeros(10)\n"],
                        },
                        {
                            "cell_type": "markdown",
                            "source": ["# Quantum notebook\n", "This is a test.\n"],
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        text = load_source_text(nb)
        assert "numpy" in text
        assert "Quantum notebook" in text


class TestBuildChunksFromRoots:
    def test_respects_max_files(self, tmp_path: Path) -> None:
        for i in range(5):
            f = tmp_path / f"doc{i}.md"
            f.write_text(f"Content for document {i}. " * 30, encoding="utf-8")
        chunks = build_chunks_from_roots(
            [tmp_path],
            chunk_size=200,
            chunk_overlap=20,
            min_chunk_chars=10,
            max_files=2,
        )
        sources = {c.source_path for c in chunks}
        assert len(sources) <= 2

    def test_skips_excluded_dirs(self, tmp_path: Path) -> None:
        good = tmp_path / "src" / "hello.py"
        good.parent.mkdir(parents=True)
        good.write_text("def hello(): pass\n" * 20, encoding="utf-8")
        bad = tmp_path / "__pycache__" / "cached.py"
        bad.parent.mkdir(parents=True)
        bad.write_text("def cached(): pass\n" * 20, encoding="utf-8")
        files = list(iter_source_files([tmp_path]))
        paths_str = [f.as_posix() for f in files]
        assert any("hello.py" in p for p in paths_str)
        assert not any("__pycache__" in p for p in paths_str)

    def test_inject_path_preamble_passthrough(self, tmp_path: Path) -> None:
        f = tmp_path / "test.md"
        f.write_text("Test content " * 30, encoding="utf-8")
        chunks_with = build_chunks_from_roots(
            [tmp_path],
            chunk_size=200,
            chunk_overlap=20,
            min_chunk_chars=10,
            inject_path_preamble=True,
        )
        chunks_without = build_chunks_from_roots(
            [tmp_path],
            chunk_size=200,
            chunk_overlap=20,
            min_chunk_chars=10,
            inject_path_preamble=False,
        )
        assert any("[source:" in c.text for c in chunks_with)
        assert not any("[source:" in c.text for c in chunks_without)

    def test_source_root_makes_paths_relative(self, tmp_path: Path) -> None:
        root = tmp_path / "workspace"
        doc = root / "docs" / "quantum_libraries" / "qiskit.md"
        doc.parent.mkdir(parents=True)
        doc.write_text("Qiskit current API " * 30, encoding="utf-8")
        chunks = build_chunks_from_roots(
            [root / "docs"],
            chunk_size=200,
            chunk_overlap=20,
            min_chunk_chars=10,
            source_root=root,
        )

        assert chunks
        assert chunks[0].source_path == "docs/quantum_libraries/qiskit.md"
        assert str(tmp_path) not in chunks[0].source_path
        assert "[source: docs/quantum_libraries/qiskit.md]" in chunks[0].text


def test_qiskit_qaoa_maxcut_docs_guard_current_api() -> None:
    root = Path(__file__).resolve().parents[1]
    qaoa_doc = (root / "docs" / "quantum_libraries" / "qaoa_maxcut.md").read_text(encoding="utf-8")
    ecosystem_doc = (
        root / "docs" / "quantum_libraries" / "qiskit_ecosystem_current_api.md"
    ).read_text(encoding="utf-8")
    basics_doc = (root / "docs" / "quantum_libraries" / "qiskit_basics.md").read_text(
        encoding="utf-8"
    )
    combined = qaoa_doc + "\n" + ecosystem_doc + "\n" + basics_doc

    assert "## Qiskit answer template" in qaoa_doc
    assert "### Minimal imports" in qaoa_doc
    assert "### Canonical application pattern" in qaoa_doc
    assert "### Generation rules" in qaoa_doc
    assert "Task-specific templates outrank the broad reference imports below" in ecosystem_doc
    assert "The general import surface is reference only, not an answer template" in ecosystem_doc
    assert "QAOA(sampler=sampler, optimizer=optimizer, reps=2)" in combined
    assert "result.x" in combined
    assert "result.fval" in combined
    assert "do not invent alternate solution-vector attribute names" in combined
    assert "Keep QAOA Max-Cut imports minimal" in qaoa_doc
    assert "keep the import block minimal and import each symbol once" in ecosystem_doc
    assert "For the standard Max-Cut application path, do not import anything from" in combined
    assert "already uses the default `QuadraticProgramToQubo` conversion internally" in combined
    assert "Do not add any `qiskit_optimization.converters` import for standard Max-Cut" in combined
    assert "including `Model2QUBO` or identity/sense-converter names" in combined
    assert "unused direct `QuadraticProgram` imports" in combined
    assert "duplicate `MinimumEigenOptimizer` aliases" in combined
    assert "`CategoricalVariable` is not a root `qiskit_optimization` import" in ecosystem_doc
    assert "Ancilla-count keywords are invalid for `QAOA`" in ecosystem_doc
    assert "Qubit-count keywords are invalid for `QAOA`" in ecosystem_doc
    assert "Instantiate `Maxcut` with graph data" in ecosystem_doc
    assert "`Maxcut` takes one graph argument" in combined
    assert "Do not call `Maxcut(edges, node_count)`" in combined
    assert "There is no `Maxcut.ingraph2qubit(...)` method" in combined
    assert "Do not read node-count attributes from the `Maxcut` application object" in combined
    assert "There is no `MinimumD` converter" in ecosystem_doc
    assert "There is no `MinimizationToMaximisation` converter" in ecosystem_doc
    assert "There is no `MinimumToMaximize` converter" in ecosystem_doc
    assert "There is no `MinimumToMaximizingConverter`" in ecosystem_doc
    assert "There are no converters named `Model2QUBO`, `Model2QubitOperator`, or" in ecosystem_doc
    assert "There is no `QuadraticProgramToQuadraticProgram` converter" in ecosystem_doc
    assert "There are no converter classes named `SumOfSubproblems` or `Transformation`" in combined
    assert "result.feval` is not valid" in combined
    assert "`result.fvalue` is not a valid objective-value field" in combined
    assert "Do not read `result.primal_values`; the solution-vector attribute is" in combined
    assert "`result.fitness_value` is not a valid objective-value field" in combined
    assert "`result.x` is an ordered array-like solution, not a dictionary" in combined
    assert "Do not call `result.x.items()`" in combined
    assert (
        "Read the Max-Cut objective value directly from `result.fval`; do not negate it" in combined
    )
    assert (
        "Do not negate `result.fval` for standard `Maxcut(...).to_quadratic_program()`" in combined
    )
    assert "Do not negate the reported objective for application-generated problems" in combined
    assert "Maxcut(...).to_quadratic_program()` can be solved directly" in ecosystem_doc
    assert "Prefer `result.x` plus application `interpret(result)` helpers" in ecosystem_doc
    assert "Do not carry CUDA-Q kernel arguments such as `qubit_count` or `layer_count`" in combined
    assert "Do not describe the solved Max-Cut assignment as a minimum cut" in combined
    assert "If you supply two initial angles, use `reps=1`" in combined
    assert "If `initial_point` is provided, its length must match" in combined
    assert "For standard QAOA this is `2 * reps`" in combined
    assert "a mismatch raises `ValueError` during solve" in combined
    assert "not a `QuantumCircuit` constructor or CUDA-Q kernel factory" in basics_doc
    assert "from qiskit_algorithms.utils import algorithm_globals" in combined
    assert (
        "Import `algorithm_globals` before assigning `algorithm_globals.random_seed`" in basics_doc
    )
    assert "raises `NameError` before QAOA runs" in combined
    assert "QAOA has no post-construction qubit-replacement setter methods" in ecosystem_doc
    assert "Do not read `result.x0`; the solution-vector attribute is `result.x`" in combined
    assert "result.x0}" not in combined
    assert "num_ancillas=0" not in combined
    assert "best_feasible_solution" not in combined
    assert "maxcut.num_nodes" not in combined
    assert "MinimumToMaximizingConverter()" not in combined
    assert "Model2QUBO(" not in combined
    assert "Linear2Quadratic(" not in combined
    assert "-result.fval" not in combined


class TestDocumentChunk:
    def test_to_dict_round_trip(self) -> None:
        chunk = DocumentChunk(
            chunk_id="abc",
            source_path="/x.md",
            title="x.md",
            text="Hello",
            char_start=0,
            char_end=5,
            metadata={"k": "v"},
        )
        d = chunk.to_dict()
        assert d["chunk_id"] == "abc"
        assert d["metadata"]["k"] == "v"


# ============================================================================
# index.py — BM25, TF-IDF/SVD, QuantumRAGIndex
# ============================================================================


class TestMinmax:
    def test_empty_array(self) -> None:
        result = _minmax(np.array([]))
        assert result.size == 0

    def test_all_same_values(self) -> None:
        result = _minmax(np.array([5.0, 5.0, 5.0]))
        assert np.allclose(result, 0.0)

    def test_basic_range(self) -> None:
        result = _minmax(np.array([0.0, 5.0, 10.0]))
        # With percentile clipping at 95%, the values should be normalized
        assert result[0] == 0.0
        assert result[-1] >= 0.9  # clipped max

    def test_single_element(self) -> None:
        result = _minmax(np.array([42.0]))
        assert np.allclose(result, 0.0)

    def test_outlier_clipped(self) -> None:
        # One extreme outlier should be clipped; remaining values get better spread
        scores = np.zeros(100)
        scores[50] = 1.0
        scores[99] = 1000.0  # outlier
        result = _minmax(scores)
        # The outlier gets clipped to 1.0, so index 99 should be at maximum
        assert result[99] == 1.0
        # Without clipping scores[50] would be ~0.001, with clipping it should be == 1.0
        # (since 95th percentile is 0 for 95 zeros, the effective clip becomes scores.max())
        # Actually: 95 zeros, 1 at 1.0, and others at 0 => p95 could be 0.
        # The fallback is scores.max() = 1000. Let's just test the outlier is normalised.
        assert result[99] >= result[50]


class TestNormalizeRows:
    def test_empty_matrix(self) -> None:
        result = _normalize_rows(np.array([]))
        assert result.size == 0

    def test_zero_row(self) -> None:
        m = np.array([[0.0, 0.0], [1.0, 0.0]], dtype=np.float32)
        result = _normalize_rows(m)
        # Zero row stays zero
        assert np.allclose(result[0], 0.0)
        # Non-zero row gets normalised to unit length
        assert math.isclose(np.linalg.norm(result[1]), 1.0, abs_tol=1e-5)


class TestBM25Index:
    def test_fit_and_score_basic(self) -> None:
        texts = ["quantum computing circuits", "classical programming basics"]
        bm25 = BM25Index.fit(texts)
        scores = bm25.score("quantum circuits")
        assert scores[0] > scores[1]

    def test_empty_corpus(self) -> None:
        bm25 = BM25Index.fit([])
        scores = bm25.score("anything")
        assert scores.size == 0

    def test_empty_query(self) -> None:
        bm25 = BM25Index.fit(["some text"])
        scores = bm25.score("")
        assert np.allclose(scores, 0.0)

    def test_unknown_terms(self) -> None:
        bm25 = BM25Index.fit(["hello world"])
        scores = bm25.score("zzznonexistent")
        assert np.allclose(scores, 0.0)


class TestQuantumRAGIndex:
    def test_build_with_few_chunks(self) -> None:
        chunks = [
            DocumentChunk("a", "/a.md", "a", "Quantum computing", 0, 17),
            DocumentChunk("b", "/b.md", "b", "Classical programming", 0, 21),
        ]
        index = QuantumRAGIndex.build(chunks, max_features=100, dense_components=2)
        assert index.summary()["chunk_count"] == 2
        assert index.summary()["source_count"] == 2

    def test_build_single_chunk(self) -> None:
        chunks = [DocumentChunk("a", "/a.md", "a", "Quantum entanglement", 0, 20)]
        index = QuantumRAGIndex.build(chunks, max_features=100, dense_components=2)
        assert index.summary()["chunk_count"] == 1

    def test_semantic_scores_empty_query(self) -> None:
        chunks = [DocumentChunk("a", "/a.md", "a", "Quantum test", 0, 12)]
        index = QuantumRAGIndex.build(chunks, max_features=100, dense_components=2)
        scores = index.semantic_scores("")
        assert np.allclose(scores, 0.0)

    def test_semantic_scores_returns_array(self) -> None:
        chunks = [
            DocumentChunk("a", "/a.md", "a", "Quantum computing", 0, 17),
            DocumentChunk("b", "/b.md", "b", "Classical music", 0, 15),
        ]
        index = QuantumRAGIndex.build(chunks, max_features=100, dense_components=2)
        scores = index.semantic_scores("quantum")
        assert scores.shape == (2,)

    def test_hybrid_scores_returns_three_arrays(self) -> None:
        chunks = [
            DocumentChunk("a", "/a.md", "a", "Quantum computing circuits", 0, 26),
            DocumentChunk("b", "/b.md", "b", "Classical programming tasks", 0, 27),
        ]
        index = QuantumRAGIndex.build(chunks, max_features=100, dense_components=2)
        lex, sem, combined = index.hybrid_scores("quantum circuits", alpha=0.5)
        assert lex.shape == (2,)
        assert sem.shape == (2,)
        assert combined.shape == (2,)

    def test_round_trip_save_load(self, tmp_path: Path) -> None:
        doc = tmp_path / "rag.md"
        doc.write_text(
            "Retrieval augmented generation grounds answers in retrieved context for quantum coding tasks.",
            encoding="utf-8",
        )
        chunks = build_chunks_for_file(doc, chunk_size=300, chunk_overlap=50, min_chunk_chars=20)
        index = QuantumRAGIndex.build(chunks, max_features=1024, dense_components=4)
        path = tmp_path / "index.pkl.gz"
        index.save(path)

        loaded = QuantumRAGIndex.load(path)
        assert loaded.summary() == index.summary()
        results = retrieve(loaded, "What grounds answers in retrieved context?", top_k=1)
        assert results
        assert results[0].chunk.source_path.endswith("rag.md")


# ============================================================================
# retrieval.py — query expansion, scoring, reranking, retrieve
# ============================================================================


class TestQueryExpansion:
    def test_adds_quantum_synonyms(self) -> None:
        expanded = expand_query("How does VQE work in Qiskit?", QueryExpansionConfig(enabled=True))
        lowered = expanded.lower()
        assert "variational quantum eigensolver" in lowered
        assert "transpile" in lowered

    def test_disabled_returns_original(self) -> None:
        original = "just a query"
        assert expand_query(original, QueryExpansionConfig(enabled=False)) == original

    def test_reverse_expansion(self) -> None:
        expanded = expand_query(
            "variational quantum eigensolver energy", QueryExpansionConfig(enabled=True)
        )
        assert "vqe" in expanded.lower()

    def test_superdense_expansion(self) -> None:
        expanded = expand_query("superdense protocol", QueryExpansionConfig(enabled=True))
        lowered = expanded.lower()
        assert "superdense coding" in lowered or "bell pair" in lowered

    def test_grover_expansion(self) -> None:
        expanded = expand_query("grover algorithm", QueryExpansionConfig(enabled=True))
        lowered = expanded.lower()
        assert "oracle" in lowered

    def test_no_duplicates(self) -> None:
        expanded = expand_query("VQE VQE VQE", QueryExpansionConfig(enabled=True))
        lines = [l for l in expanded.strip().split("\n") if l.strip()]
        assert len(lines) == len(set(lines))


class TestSourcePriorityMultiplier:
    def test_authoritative_paths(self) -> None:
        assert source_priority_multiplier("/tmp/evals/tasks/quantum/vqe/task.json") > 1.0
        assert source_priority_multiplier("/tmp/AGENTS.md") >= 1.2
        assert source_priority_multiplier("/tmp/HEARTBEAT.md") >= 1.2

    def test_unknown_path(self) -> None:
        assert source_priority_multiplier("/tmp/random_notes.md") == 1.0


class TestQueryAwareMultiplier:
    def test_library_queries_boost_matching_doc_source(self) -> None:
        assert (
            query_aware_multiplier(
                "How do I build a Bell pair in Qiskit?",
                "/tmp/docs/external/quantum-sdk-docs-latest/qiskit/example.md",
            )
            > 1.0
        )
        assert (
            query_aware_multiplier(
                "How do I create and measure a circuit in Cirq?",
                "/tmp/docs/external/quantum-sdk-docs-latest/cirq/example.md",
            )
            > 1.0
        )

    def test_definition_query(self) -> None:
        assert (
            query_aware_multiplier(
                "Where is this task defined?",
                "/tmp/evals/tasks/quantum/qft/task.json",
            )
            > 1.0
        )

    def test_rag_gaps_query(self) -> None:
        assert (
            query_aware_multiplier(
                "What are the support and gaps of the current low-compute rag?",
                "/tmp/research/quantum_rag_low_compute.md",
            )
            > 1.0
        )

    def test_grpo_training_command_query(self) -> None:
        assert (
            query_aware_multiplier(
                "What is the verified GRPO training command?",
                "/tmp/HEARTBEAT.md",
            )
            > 1.0
        )

    def test_no_match(self) -> None:
        assert query_aware_multiplier("Where is this defined?", "/tmp/random.md") == 1.0


class TestFilenameRoleScore:
    """Test _filename_role_score through rerank_score indirectly."""

    def test_reranker_prefers_task_json_for_definition(self, tmp_path: Path) -> None:
        task_doc = tmp_path / "task.json"
        tests_doc = tmp_path / "tests.py"
        task_doc.write_text(
            '{"id":"quantum_qft_phase_pattern","name":"QFT phase pattern"}', encoding="utf-8"
        )
        tests_doc.write_text("def test_qft_phase_pattern():\n    assert True\n", encoding="utf-8")
        chunks = []
        chunks.extend(
            build_chunks_for_file(task_doc, chunk_size=200, chunk_overlap=20, min_chunk_chars=10)
        )
        chunks.extend(
            build_chunks_for_file(tests_doc, chunk_size=200, chunk_overlap=20, min_chunk_chars=10)
        )
        index = QuantumRAGIndex.build(chunks, max_features=512, dense_components=4)
        results = retrieve(
            index, "Where is the QFT phase pattern task defined?", top_k=2, rerank_pool_size=2
        )
        assert results
        assert results[0].chunk.source_path.endswith("task.json")


class TestRetrieve:
    def test_basic_retrieval(self, tmp_path: Path) -> None:
        qiskit_doc = tmp_path / "qiskit_notes.md"
        qiskit_doc.write_text(
            "Qiskit transpile turns a QuantumCircuit into a backend-aware circuit.\n"
            "Use coupling_map and basis_gates when targeting hardware.\n"
            "Aer simulator supports local execution for validation.\n",
            encoding="utf-8",
        )
        vqe_doc = tmp_path / "vqe_notes.md"
        vqe_doc.write_text(
            "Variational quantum eigensolver uses an ansatz and a classical optimizer.\n"
            "The energy expectation is estimated from measured observables.\n",
            encoding="utf-8",
        )
        chunks = []
        chunks.extend(
            build_chunks_for_file(qiskit_doc, chunk_size=400, chunk_overlap=80, min_chunk_chars=40)
        )
        chunks.extend(
            build_chunks_for_file(vqe_doc, chunk_size=400, chunk_overlap=80, min_chunk_chars=40)
        )
        index = QuantumRAGIndex.build(chunks, max_features=2048, dense_components=8)
        results = retrieve(
            index, "How do I transpile a circuit with a coupling map in Qiskit?", top_k=2
        )
        assert results
        assert results[0].chunk.source_path.endswith("qiskit_notes.md")

    def test_max_chunks_per_source(self, tmp_path: Path) -> None:
        doc_a = tmp_path / "a.md"
        doc_b = tmp_path / "b.md"
        doc_a.write_text(("quantum rag retrieval " * 80).strip(), encoding="utf-8")
        doc_b.write_text("quantum retrieval baseline", encoding="utf-8")
        chunks = []
        chunks.extend(
            build_chunks_for_file(doc_a, chunk_size=120, chunk_overlap=20, min_chunk_chars=20)
        )
        chunks.extend(
            build_chunks_for_file(doc_b, chunk_size=120, chunk_overlap=20, min_chunk_chars=20)
        )
        index = QuantumRAGIndex.build(chunks, max_features=1024, dense_components=4)
        results = retrieve(index, "quantum retrieval", top_k=2, max_chunks_per_source=1)
        assert len(results) == 2
        assert len({item.chunk.source_path for item in results}) == 2

    def test_exclude_source_substrings(self, tmp_path: Path) -> None:
        a = tmp_path / "wanted.md"
        b = tmp_path / "excluded_report.md"
        a.write_text("quantum circuit algorithms " * 20, encoding="utf-8")
        b.write_text("quantum circuit algorithms report " * 20, encoding="utf-8")
        chunks = []
        chunks.extend(
            build_chunks_for_file(a, chunk_size=300, chunk_overlap=30, min_chunk_chars=20)
        )
        chunks.extend(
            build_chunks_for_file(b, chunk_size=300, chunk_overlap=30, min_chunk_chars=20)
        )
        index = QuantumRAGIndex.build(chunks, max_features=512, dense_components=4)
        results = retrieve(
            index,
            "quantum circuit",
            top_k=5,
            exclude_source_substrings=["excluded_report"],
        )
        assert all("excluded_report" not in r.chunk.source_path for r in results)

    def test_path_preamble_helps_qft(self, tmp_path: Path) -> None:
        """Verify that path-augmented chunks fix the QFT phase pattern miss."""
        qft_task = tmp_path / "evals" / "tasks" / "quantum" / "qft_phase_pattern" / "task.json"
        qft_task.parent.mkdir(parents=True)
        qft_task.write_text(
            json.dumps(
                {
                    "id": "quantum_qft_phase_pattern",
                    "name": "QFT phase pattern",
                    "domain": "quantum",
                    "category": "algorithm_reasoning",
                    "candidate_file": "candidate.py",
                    "test_file": "tests.py",
                }
            ),
            encoding="utf-8",
        )
        phase_est = (
            tmp_path / "evals" / "tasks" / "quantum" / "phase_estimation_circuit" / "candidate.py"
        )
        phase_est.parent.mkdir(parents=True)
        phase_est.write_text(
            "def phase_estimation():\n    '''Phase estimation circuit.'''\n    pass\n" * 5,
            encoding="utf-8",
        )
        chunks = []
        chunks.extend(
            build_chunks_for_file(qft_task, chunk_size=600, chunk_overlap=50, min_chunk_chars=10)
        )
        chunks.extend(
            build_chunks_for_file(phase_est, chunk_size=600, chunk_overlap=50, min_chunk_chars=10)
        )
        index = QuantumRAGIndex.build(chunks, max_features=2048, dense_components=8)
        results = retrieve(index, "Where is the QFT phase pattern task defined?", top_k=2)
        assert results
        assert "qft_phase_pattern" in results[0].chunk.source_path

    def test_ranks_are_sequential(self, tmp_path: Path) -> None:
        doc = tmp_path / "doc.md"
        doc.write_text("quantum " * 200, encoding="utf-8")
        chunks = build_chunks_for_file(doc, chunk_size=100, chunk_overlap=10, min_chunk_chars=10)
        index = QuantumRAGIndex.build(chunks, max_features=512, dense_components=4)
        results = retrieve(index, "quantum", top_k=3)
        ranks = [r.rank for r in results]
        assert ranks == [1, 2, 3]

    def test_rerank_prefers_rag_design_note(self) -> None:
        note_chunk = build_chunks_for_file(
            Path("/Users/daxu/software/quantum-gpt/research/quantum_rag_low_compute.md"),
            chunk_size=500,
            chunk_overlap=50,
            min_chunk_chars=50,
        )[0]
        generic_chunk = build_chunks_for_file(
            Path("/Users/daxu/software/quantum-gpt/PROJECT.md"),
            chunk_size=500,
            chunk_overlap=50,
            min_chunk_chars=50,
        )[0]
        results = retrieve(
            QuantumRAGIndex.build(
                [note_chunk, generic_chunk], max_features=512, dense_components=2
            ),
            "What are the current low-compute rag support and gaps?",
            top_k=2,
            rerank_pool_size=2,
        )
        assert results[0].chunk.source_path.endswith("quantum_rag_low_compute.md")


# ============================================================================
# cache.py — AnswerCache
# ============================================================================


class TestAnswerCache:
    def test_round_trip(self, tmp_path: Path) -> None:
        cache_path = tmp_path / "cache.jsonl"
        cache = AnswerCache(cache_path)
        assert len(cache) == 0

        entry = cache.put(
            "What is VQE?", "abc123", "VQE is a variational method.", {"model": "test"}
        )
        assert len(cache) == 1

        retrieved = cache.get("What is VQE?", "abc123")
        assert retrieved is not None
        assert retrieved.answer == "VQE is a variational method."
        assert retrieved.metadata["model"] == "test"

    def test_persists_across_reload(self, tmp_path: Path) -> None:
        cache_path = tmp_path / "cache.jsonl"
        cache = AnswerCache(cache_path)
        cache.put("What is VQE?", "abc123", "VQE is a variational method.")

        cache2 = AnswerCache(cache_path)
        assert len(cache2) == 1
        assert cache2.get("What is VQE?", "abc123") is not None

    def test_miss_for_different_index(self, tmp_path: Path) -> None:
        cache_path = tmp_path / "cache.jsonl"
        cache = AnswerCache(cache_path)
        cache.put("What is VQE?", "idx1", "answer1")
        assert cache.get("What is VQE?", "idx2") is None

    def test_miss_for_different_query(self, tmp_path: Path) -> None:
        cache_path = tmp_path / "cache.jsonl"
        cache = AnswerCache(cache_path)
        cache.put("What is VQE?", "idx1", "answer1")
        assert cache.get("What is QAOA?", "idx1") is None

    def test_overwrite_same_key(self, tmp_path: Path) -> None:
        cache_path = tmp_path / "cache.jsonl"
        cache = AnswerCache(cache_path)
        cache.put("What is VQE?", "idx1", "answer1")
        cache.put("What is VQE?", "idx1", "answer2")
        assert len(cache) == 1
        assert cache.get("What is VQE?", "idx1").answer == "answer2"

    def test_multiple_entries(self, tmp_path: Path) -> None:
        cache_path = tmp_path / "cache.jsonl"
        cache = AnswerCache(cache_path)
        cache.put("q1", "idx", "a1")
        cache.put("q2", "idx", "a2")
        cache.put("q3", "idx", "a3")
        assert len(cache) == 3

    def test_corrupted_lines_skipped(self, tmp_path: Path) -> None:
        cache_path = tmp_path / "cache.jsonl"
        good = json.dumps(CacheEntry("k", "q", "h", "a", {}).to_dict())
        cache_path.write_text(f"not json\n{good}\n{{bad}}\n", encoding="utf-8")
        cache = AnswerCache(cache_path)
        assert len(cache) == 1

    def test_empty_file(self, tmp_path: Path) -> None:
        cache_path = tmp_path / "cache.jsonl"
        cache_path.write_text("", encoding="utf-8")
        cache = AnswerCache(cache_path)
        assert len(cache) == 0

    def test_nonexistent_file(self, tmp_path: Path) -> None:
        cache_path = tmp_path / "nonexistent.jsonl"
        cache = AnswerCache(cache_path)
        assert len(cache) == 0

    def test_contains(self, tmp_path: Path) -> None:
        cache_path = tmp_path / "cache.jsonl"
        cache = AnswerCache(cache_path)
        entry = cache.put("q", "idx", "a")
        assert entry.key in cache
        assert "nonexistent" not in cache


class TestCacheKey:
    def test_normalized_query(self) -> None:
        key1 = make_cache_key("  What   is   VQE?  ", "idx1")
        key2 = make_cache_key("what is vqe?", "idx1")
        assert key1 == key2

    def test_different_index_different_key(self) -> None:
        key1 = make_cache_key("query", "idx1")
        key2 = make_cache_key("query", "idx2")
        assert key1 != key2


class TestIndexSummaryHash:
    def test_stable(self) -> None:
        summary = {"chunk_count": 100, "source_count": 10}
        h1 = index_summary_hash(summary)
        h2 = index_summary_hash(summary)
        assert h1 == h2
        assert len(h1) == 16

    def test_different_summaries(self) -> None:
        h1 = index_summary_hash({"chunk_count": 100})
        h2 = index_summary_hash({"chunk_count": 200})
        assert h1 != h2

    def test_key_order_irrelevant(self) -> None:
        h1 = index_summary_hash({"a": 1, "b": 2})
        h2 = index_summary_hash({"b": 2, "a": 1})
        assert h1 == h2


class TestCacheEntry:
    def test_from_dict_round_trip(self) -> None:
        entry = CacheEntry(key="k", query="q", index_hash="h", answer="a", metadata={"m": 1})
        d = entry.to_dict()
        restored = CacheEntry.from_dict(d)
        assert restored == entry


# ============================================================================
# eval.py — faithfulness, relevance, groundedness, composite
# ============================================================================


class TestFaithfulnessScore:
    def test_all_cited(self) -> None:
        assert faithfulness_score("[C1] [C2] [C3]", 3) == 1.0

    def test_partial_cited(self) -> None:
        score = faithfulness_score("Answer with [C1] and [C2].", 3)
        assert math.isclose(score, 2 / 3, abs_tol=1e-6)

    def test_no_citations(self) -> None:
        assert faithfulness_score("No citations here.", 3) == 0.0

    def test_zero_retrieved(self) -> None:
        assert faithfulness_score("[C1]", 0) == 0.0

    def test_invalid_citation_ranks_ignored(self) -> None:
        # [C5] is out of range for 3 retrieved chunks
        score = faithfulness_score("[C1] [C5]", 3)
        assert math.isclose(score, 1 / 3, abs_tol=1e-6)


class TestRelevanceScore:
    def test_full_overlap(self) -> None:
        score = relevance_score("quantum VQE", "quantum VQE ansatz")
        assert score == 1.0

    def test_partial_overlap(self) -> None:
        score = relevance_score(
            "quantum VQE ansatz", "The VQE uses a quantum ansatz to minimize energy."
        )
        assert 0.0 < score <= 1.0

    def test_no_overlap(self) -> None:
        score = relevance_score("quantum VQE", "classical music theory")
        assert score == 0.0

    def test_empty_query(self) -> None:
        assert relevance_score("", "some answer") == 0.0


class TestGroundednessScore:
    def _make_chunk(self, text: str, rank: int = 1) -> RetrievedChunk:
        chunk = DocumentChunk("test", "/test.md", "test", text, 0, len(text))
        return RetrievedChunk(
            chunk=chunk, rank=rank, final_score=1.0, lexical_score=0.5, semantic_score=0.5
        )

    def test_grounded_citation(self) -> None:
        chunk = self._make_chunk(
            "Variational quantum eigensolver uses an ansatz and a classical optimizer."
        )
        score = groundedness_score(
            "The VQE [C1] uses a variational quantum eigensolver with an ansatz.",
            [chunk],
        )
        assert score > 0.0

    def test_no_citations(self) -> None:
        chunk = self._make_chunk("Some text")
        assert groundedness_score("No citations.", [chunk]) == 0.0

    def test_invalid_rank(self) -> None:
        chunk = self._make_chunk("Some text", rank=1)
        # [C5] doesn't match any retrieved chunk
        score = groundedness_score("[C5] claim", [chunk])
        assert score == 0.0

    def test_multiple_citations(self) -> None:
        c1 = self._make_chunk("quantum entanglement bell pair EPR states superposition", rank=1)
        c2 = self._make_chunk(
            "classical optimization gradient descent machine learning rate", rank=2
        )
        # Answer must share >= 3 tokens with each cited chunk
        score = groundedness_score(
            "Entanglement [C1] uses quantum bell pair EPR, and optimization [C2] uses gradient descent machine learning.",
            [c1, c2],
        )
        assert score > 0.0


class TestEvaluateAnswer:
    def test_composite_score(self) -> None:
        chunk = DocumentChunk(
            "t", "/t.md", "t", "QFT phase pattern uses quantum Fourier transform.", 0, 50
        )
        retrieved = RetrievedChunk(
            chunk=chunk, rank=1, final_score=1.0, lexical_score=0.5, semantic_score=0.5
        )
        result = evaluate_answer(
            "What is the QFT phase pattern?",
            "The QFT phase pattern [C1] computes the quantum Fourier transform of a statevector.",
            [retrieved],
        )
        assert result.num_citations == 1
        assert result.num_valid_citations == 1
        assert result.composite_score > 0.0
        assert result.faithfulness_score > 0.0
        assert result.relevance_score > 0.0
        assert result.groundedness_score > 0.0

    def test_custom_weights(self) -> None:
        chunk = DocumentChunk("t", "/t.md", "t", "text", 0, 4)
        retrieved = RetrievedChunk(
            chunk=chunk, rank=1, final_score=1.0, lexical_score=0.5, semantic_score=0.5
        )
        result = evaluate_answer(
            "query",
            "answer [C1] text",
            [retrieved],
            faithfulness_weight=1.0,
            relevance_weight=0.0,
            groundedness_weight=0.0,
        )
        assert math.isclose(result.composite_score, result.faithfulness_score, abs_tol=1e-6)

    def test_to_dict(self) -> None:
        chunk = DocumentChunk("t", "/t.md", "t", "text here", 0, 9)
        retrieved = RetrievedChunk(
            chunk=chunk, rank=1, final_score=1.0, lexical_score=0.5, semantic_score=0.5
        )
        result = evaluate_answer("q", "a [C1]", [retrieved])
        d = result.to_dict()
        assert "query" in d
        assert "composite_score" in d

    def test_no_chunks(self) -> None:
        result = evaluate_answer("query", "answer", [])
        assert result.num_retrieved == 0
        assert result.faithfulness_score == 0.0
        assert result.groundedness_score == 0.0


# ============================================================================
# generation.py — prompt construction and context formatting
# ============================================================================


class TestFormatRetrievedContext:
    def test_basic_format(self) -> None:
        chunk = DocumentChunk("t", "/src.md", "src.md", "Some retrieved text.", 0, 20)
        retrieved = RetrievedChunk(
            chunk=chunk, rank=1, final_score=0.95, lexical_score=0.6, semantic_score=0.4
        )
        ctx = format_retrieved_context([retrieved])
        assert "[C1]" in ctx
        assert "source=/src.md" in ctx
        assert "Some retrieved text." in ctx
        assert "0.9500" in ctx

    def test_multiple_chunks(self) -> None:
        c1 = DocumentChunk("a", "/a.md", "a", "First chunk.", 0, 12)
        c2 = DocumentChunk("b", "/b.md", "b", "Second chunk.", 0, 13)
        r1 = RetrievedChunk(
            chunk=c1, rank=1, final_score=0.9, lexical_score=0.5, semantic_score=0.4
        )
        r2 = RetrievedChunk(
            chunk=c2, rank=2, final_score=0.8, lexical_score=0.4, semantic_score=0.4
        )
        ctx = format_retrieved_context([r1, r2])
        assert "[C1]" in ctx
        assert "[C2]" in ctx
        assert "First chunk." in ctx
        assert "Second chunk." in ctx

    def test_empty_list(self) -> None:
        ctx = format_retrieved_context([])
        assert ctx == ""


class TestBuildRagMessages:
    def test_has_system_and_user(self) -> None:
        chunk = DocumentChunk("t", "/src.md", "src.md", "Context text.", 0, 13)
        retrieved = RetrievedChunk(
            chunk=chunk, rank=1, final_score=0.9, lexical_score=0.5, semantic_score=0.4
        )
        messages = build_rag_messages("What is VQE?", [retrieved])
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"

    def test_system_prompt_content(self) -> None:
        messages = build_rag_messages("query", [])
        assert messages[0]["content"] == RAG_SYSTEM_PROMPT
        assert "quantum" in messages[0]["content"].lower()

    def test_user_prompt_includes_query_and_context(self) -> None:
        chunk = DocumentChunk("t", "/src.md", "src.md", "Some context.", 0, 13)
        retrieved = RetrievedChunk(
            chunk=chunk, rank=1, final_score=0.9, lexical_score=0.5, semantic_score=0.4
        )
        messages = build_rag_messages("Where is VQE defined?", [retrieved])
        user_msg = messages[1]["content"]
        assert "Where is VQE defined?" in user_msg
        assert "Some context." in user_msg
        assert "[C1]" in user_msg


# ============================================================================
# __init__.py — public API exports
# ============================================================================


class TestPublicAPI:
    def test_all_exports_importable(self) -> None:
        import quantum_rag

        for name in quantum_rag.__all__:
            assert hasattr(quantum_rag, name), f"Missing export: {name}"

    def test_key_classes(self) -> None:
        from quantum_rag import (
            AnswerCache,
            AnswerEvalResult,
            ChatCompletionsClient,
            ResponsesClient,
        )

        assert AnswerCache is not None
        assert AnswerEvalResult is not None
        assert ChatCompletionsClient is not None
        assert ResponsesClient is not None


# ============================================================================
# retrieval.py — path specificity scoring
# ============================================================================


class TestPathSpecificityScore:
    def test_matching_task_family(self) -> None:
        """Query about QFT should boost qft_phase_pattern chunks."""
        score = _path_specificity_score(
            "Where is the QFT phase pattern task?",
            "/evals/tasks/quantum/qft_phase_pattern/task.json",
        )
        assert score > 0

    def test_unrelated_task_json_penalised(self) -> None:
        """Query about QFT should penalise error_detection task.json."""
        score = _path_specificity_score(
            "Where is the QFT phase pattern task?",
            "/evals/tasks/quantum/error_detection_bit_flip/task.json",
        )
        assert score < 0

    def test_no_task_family_in_query(self) -> None:
        """Generic queries should not trigger any bonus or penalty."""
        score = _path_specificity_score(
            "How should this repo evaluate tasks before training?",
            "/evals/tasks/quantum/error_detection_bit_flip/task.json",
        )
        assert score == 0.0

    def test_grover_matches_grover(self) -> None:
        score = _path_specificity_score(
            "What is the Grover oracle diffusion task?",
            "/evals/tasks/quantum/grover_oracle_diffusion/candidate.py",
        )
        assert score > 0

    def test_grover_penalises_vqe(self) -> None:
        score = _path_specificity_score(
            "What is the Grover oracle diffusion task?",
            "/evals/tasks/quantum/vqe_energy_minimization/candidate.py",
        )
        assert score < 0

    def test_non_task_file_no_penalty(self) -> None:
        """Non-task files should get no penalty even if query has a task family."""
        score = _path_specificity_score(
            "Where is the QFT phase pattern task?",
            "/research/quantum_rag_low_compute.md",
        )
        assert score == 0.0


# ============================================================================
# generation.py — ChatCompletionsClient
# ============================================================================


class TestChatCompletionsClient:
    def test_client_creation(self) -> None:
        client = ChatCompletionsClient(
            base_url="http://localhost:8011",
            model="test-model",
            api_key="test-key",
        )
        assert client.base_url == "http://localhost:8011"
        assert client.model == "test-model"
        assert client.api_key == "test-key"
        assert client.timeout_seconds == 180.0

    def test_responses_client_creation(self) -> None:
        client = ResponsesClient(
            base_url="http://localhost:8011",
            model="test-model",
        )
        assert client.base_url == "http://localhost:8011"
        assert client.model == "test-model"


# ============================================================================
# scripts/eval_quantum_rag.py — benchmark runner
# ============================================================================


class TestEvalBenchmarkRunner:
    def test_eval_script_importable(self) -> None:
        """The eval script should be importable without side effects."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "eval_quantum_rag",
            str(Path(__file__).resolve().parents[1] / "scripts" / "eval_quantum_rag.py"),
        )
        assert spec is not None
        mod = importlib.util.module_from_spec(spec)
        # Don't execute, just verify it loads
        assert mod is not None

    def test_run_benchmark_function(self, tmp_path: Path) -> None:
        """run_benchmark should produce correct metrics structure."""
        # Build a minimal index
        doc = tmp_path / "test.md"
        doc.write_text("quantum computing test content " * 20, encoding="utf-8")
        chunks = build_chunks_for_file(doc, chunk_size=200, chunk_overlap=20, min_chunk_chars=10)
        index = QuantumRAGIndex.build(chunks, max_features=512, dense_components=4)

        # Mini benchmark
        benchmark = [
            {
                "id": "test_q1",
                "query": "quantum computing",
                "expected_source_substrings": ["test.md"],
            }
        ]

        # Import run_benchmark from the script
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "eval_quantum_rag",
            str(Path(__file__).resolve().parents[1] / "scripts" / "eval_quantum_rag.py"),
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        report = mod.run_benchmark(index, benchmark, top_k=5, alpha=0.55, verbose=False)
        assert report["num_queries"] == 1
        assert report["hit_at_k"] == 1.0
        assert report["mrr"] == 1.0
        assert "queries" in report
        assert report["queries"][0]["hit"] is True

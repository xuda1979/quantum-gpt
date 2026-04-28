# Quantum Computing Documentation Corpus

This directory contains compact, RAG-friendly documentation for quantum
computing algorithms and the major Python quantum software libraries
(Qiskit, Cirq, PennyLane, Amazon Braket) plus pure-NumPy state vector
simulation patterns.

The documents here are intentionally short (1-2 pages each) so the
chunker in `quantum_rag.corpus.build_chunks_from_roots` produces a
small number of tightly scoped chunks per topic. They are indexed by
`scripts/build_quantum_rag.py --profile docs_only` (or the bundled
"broad" profile if combined with the project corpus).

Each document follows the same skeleton:

1. **Concept** - one-paragraph definition
2. **Math** - the relevant equations / state amplitudes
3. **Reference circuit / pseudocode**
4. **Library snippets** - how to express it in each major SDK
5. **Common pitfalls / aliases** - useful for repair tasks

Use these as authoritative references when grounding answers about
quantum algorithms, gates, channels, or library APIs.

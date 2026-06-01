# ISQ training COT RAG corpus: gate_decomposition shard 17

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3337

- task_id: `isqTrain/3337`
- task_type: `code_generation`
- category: `gate_decomposition`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5609`

### Prompt

I need an isQ program to an isQ program: apply gate chain H-S-T to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply gate chain H-S-T to a single qubit initialized to |0⟩ and measure.

One qubit is needed (`q[0]`), which is measured at the end.

State evolution:
- Initial: |0⟩
- After H: |+⟩ = (1/√2)(|0⟩ + |1⟩)
- After S: (1/√2)(|0⟩ + i|1⟩)
- After T: (1/√2)(|0⟩ + e^(i3π/4)|1⟩)

Expected probabilities: Both S and T only add relative phases, which do not change measurement magnitudes. Since H creates equal amplitudes of 1/√2, we get P(|0⟩) = |1/√2|² = 0.5 and P(|1⟩) = |e^(i3π/4)/√2|² = 0.5.

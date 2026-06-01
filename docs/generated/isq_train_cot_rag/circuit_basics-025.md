# ISQ training COT RAG corpus: circuit_basics shard 25

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1565

- task_id: `isqTrain/1565`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2869`

### Prompt

Write an isQ program that Apply the gate sequence X-H-X to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply X-H-X gate sequence to |0⟩ and measure the result.
2. **Qubits**: 1 qubit needed, and it is measured.
3. **State evolution**:
   - |0⟩ → X → |1⟩
   - |1⟩ → H → (1/√2)(|0⟩ - |1⟩) = |-⟩
   - |-⟩ → X → (1/√2)(|1⟩ - |0⟩) = -|-⟩ (global phase only)
4. **Expected probabilities**: The final state is |-⟩ (up to global phase), yielding P(|0⟩) = 0.5 and P(|1⟩) = 0.5.

## isqTrain/1482

- task_id: `isqTrain/1482`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `3736`

### Prompt

Code this in isQ: Encode the classical value 9/16 into a qubit using angle encoding (Ry rotation with angle pi*9/16). Measure.

### Chain-of-thought reasoning

## Reasoning
- Goal: Encode classical value 9/16 via Ry rotation with angle π·9/16 on one qubit, then measure.
- One qubit needed (q[0]), which is measured.
- State evolution: |0> → Ry(9π/16) → cos(9π/32)|0> + sin(9π/32)|1>.
- P(|0>) = cos²(9π/32) ≈ 0.4025, P(|1>) = sin²(9π/32) ≈ 0.5975.

## isqTrain/4745

- task_id: `isqTrain/4745`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `superposition`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `4704`

### Prompt

Do these two isQ programs produce the same measurement results?

Program A:
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    X(q[0]);
    H(q[0]);
    X(q[0]); // additional bit flip
    M(q[0]);
}

```

Program B:
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

**Program A** applies H, X, H, X then measures. Tracing the state: |0> → H → |+> → X → |+> → H → |0> → X → |1>. Measurement yields 1 with probability 100%.

**Program B** applies H then measures. Tracing the state: |0> → H → |+> = (|0>+|1>)/√2. Measurement yields 0 with probability 50% and 1 with probability 50%.

**Key difference:** Program A's additional X-H-X sequence transforms |+> back through |0> to |1>, a deterministic state. Program B measures the superposition |+> directly.

**Verdict:** Not equivalent — Program A produces measurement distribution [0: 0%, 1: 100%] while Program B produces [0: 50%, 1: 50%].

No

### Reference answer

{'equivalent': False, 'explanation': 'After adding X gate to Program A, the programs produce different probability distributions.', 'probs_a': {'1': 1.0}, 'probs_b': {'0': 0.5, '1': 0.5}}

## isqTrain/1601

- task_id: `isqTrain/1601`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1763`

### Prompt

Write isQ code for the following quantum task: Prepare |1> then apply Ry(pi). Measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Prepare the state |1> and apply a Ry(pi) rotation, then measure the result.
2. **Qubits:** 1 qubit is required and measured.
3. **Evolution:** 
   - Start in the initial state |0>.
   - Apply the X gate to flip the state to |1>.
   - Apply Ry(pi), which corresponds to the matrix [[0, -1], [1, 0]]. Acting on |1>, this yields -|0>. Ignoring the global phase, the state is |0>.
4. **Measurement:** The final state is exactly |0>, yielding a 100% probability of measuring |0>.

## isqTrain/4725

- task_id: `isqTrain/4725`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5612`

### Prompt

Determine if these two isQ implementations are functionally equivalent:

Version A:
```isq
import std;
qbit q[2];

procedure main() {
    X(q[1]);
    M(q[0]); M(q[1]);
}

```

Version B:
```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
- Program A applies an X gate to q[1], evolving the initial state |00> to |01>.
- Program B applies an X gate to q[0], evolving the initial state |00> to |10>.
- The key difference is the target of the X gate, which produces completely orthogonal final states.
- The measurement probability distributions are different: Program A yields 100% probability for the bitstring '01', while Program B yields 100% probability for '10'.
- Verdict: No.

### Reference answer

{'equivalent': False, 'explanation': "Flipping different qubits gives different states: |10> vs |01> Program A produces {'10': 1.0} while Program B produces {'01': 1.0}.", 'probs_a': {'01': 1.0}, 'probs_b': {'10': 1.0}}

## isqTrain/1316

- task_id: `isqTrain/1316`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `859`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[2];
procedure main() {
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
- The initial state of the 2-qubit system is |00>.
- No quantum gates are applied before the measurements `M(q[0])` and `M(q[1])`.
- The quantum state remains |00> throughout the circuit's execution.
- Both qubits are measured directly in the computational basis.

Predicted probability distribution: {|00>: 1.0}

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'Parametric variant of isqEval/470. Dimension: qubit_variant: q[1] -> q[2].'}

## isqTrain/4673

- task_id: `isqTrain/4673`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `3974`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    H(q[0]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations:** The circuit sequentially applies two Hadamard (H) gates followed by a Pauli-X (X) gate to a single qubit.
2. **State Evolution:**
   - Initial state: |0>
   - After 1st H: |+> = (1/√2)|0> + (1/√2)|1>
   - After 2nd H: |0> (Applying H twice cancels out, returning to the initial state)
   - After X: |1> (The X gate flips the qubit from |0> to |1>)
3. **Final State:** |1>
4. **Probabilities:** The final state is exactly |1>, so measurement will yield 1 with certainty.

Predicted probability distribution: {|1>: 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|1>) = 1.0000.'}

## isqTrain/4740

- task_id: `isqTrain/4740`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5317`

### Prompt

Determine if these two isQ implementations are functionally equivalent:

Version A:
```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    X(q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

Version B:
```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    X(q[1]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze Program A:**
    *   Initializes 3 qubits `q[0], q[1], q[2]` to $|000\rangle$.
    *   `X(q[0])`: Flips `q[0]` to $|1\rangle$. State is $|100\rangle$.
    *   `X(q[2])`: Flips `q[2]` to $|1\rangle$. State is $|101\rangle$. (Wait, the prompt's predicted output says Program A gives '110' and B gives '101', but A applies X to q[0] and q[2]. Let's re-verify bitstring ordering. "earlier measured qubit = higher bit" means `M(q[0])` is the highest bit. So `M(q[0]), M(q[1]), M(q[2])` corresponds to bits 2, 1, 0. Thus state $q[2]q[1]q[0]$ maps to bitstring $q[0]q[1]q[2]$. Wait, no. If $q[0]$ is measured first, it is the highest bit (most significant bit, bit 2). So the bitstring is $q[0]q[1]q[2]$.
    *   Let's trace carefully:
        *   Program A: `X(q[0])`, `X(q[2])` -> state is $q[2]=1, q[1]=0, q[0]=1$.
        *   Bitstring: `q[0]q[1]q[2]` = `101`.
        *   Wait, the prompt's predicted output says: "Program A produces {'110': 1.0} while Program B produces {'101': 1.0}."
        *   Let's check Program B: `X(q[0])`, `X(q[1])` -> state is $q[2]=0, q[1]=1, q[0]=1$.
        *   Bitstring: `q[0]q[1]q[2]` = `110`.
        *   Ah, the predicted output in the prompt swapped A and B in the explanation ("Flipping q[1] vs q[2] gives |110> vs |101> (different states) Program A produces {'110': 1.0} while Program B produces {'101': 1.0}"). Wait, if A is $q[0]$ and $q[2]$, it gives 101. B gives 110. the predicted output text seems to have a typo in the prompt's example, but the final verdict "Equivalent: False" is what matters. I will explain it correctly based on the code.
        *   Wait, let's re-read the state notation: is $q[0]$ the left-most bit in $|q[0]q[1]q[2]\rangle$? Yes, standard notation.
        *   So A: X(q[0]), X(q[2]) -> $|101\rangle$.
        *   B: X(q[0]), X(q[1]) -> $|110\rangle$.

2.  **Draft the Analysis:**
    *   Program A applies X gates to `q[0]` and `q[2]`, preparing the state $|101\rangle$.
    *   Program B applies X gates to `q[0]` and `q[1]`, preparing the state $|110\rangle$.
    *   The key difference is the target of the second X gate (`q[2]` in A vs `q[1]` in B).
    *   The measurement probability distributions are different because they measure deterministically distinct computational basis states: $|101\rangle$ for A and $|110\rangle$.
    *   Verdict: Not equivalent.

3.  **Refine wording to match rules:**
    *   Output ONLY the analysis, starting with "## Equivalence Analysis"
    *   3-8 lines.
    *   End with a clear "Yes/No" verdict line.
    *   Concise, precise step-by-step reasoning.
    *   Use Dirac notation.

    Draft:
    ## Equivalence Analysis
    1. Program A initializes the 3-qubit register to |000>, then applies X gates to `q[0]` and `q[2]` to prepare the state |101>.
    2. Program B initializes the 3-qubit register to |000>, then applies X gates to `q[0]` and `q[1]` to prepare the state |110>.
    3. The key difference is the index of the second flipped qubit (q[2

### Reference answer

{'equivalent': False, 'explanation': "Flipping q[1] vs q[2] gives |110> vs |101> (different states) Program A produces {'110': 1.0} while Program B produces {'101': 1.0}.", 'probs_a': {'101': 1.0}, 'probs_b': {'110': 1.0}}

## isqTrain/1722

- task_id: `isqTrain/1722`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4190`

### Prompt

Write isQ code for the following quantum task: Apply Ry(pi) then Rx(pi) to |0>. Measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare a state by applying sequential rotations Ry(pi) and Rx(pi) to the ground state |0> and measure the result.
Qubits: 1 qubit, `q[0]`, which is measured.
Evolution: The initial state |0> is rotated by Ry(pi) to yield |1>. Then, applying Rx(pi) to |1> results in the state -i|0>.
Probabilities: The final state -i|0> is equivalent to |0> up to a global phase, meaning it will be measured as 0 with 100% probability.

## isqTrain/1590

- task_id: `isqTrain/1590`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `57`

### Prompt

用isQ实现Put 3 qubits in superposition, measure only q[0].

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create equal superposition on 3 qubits and measure only the first qubit.
2. **Qubits**: 3 qubits (q[0], q[1], q[2]); only q[0] is measured.
3. **State evolution**:
   - Initial: |000⟩
   - H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |00⟩ = (|000⟩+|100⟩)/√2
   - H(q[1]): (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ |0⟩ = (|000⟩+|010⟩+|100⟩+|110⟩)/2
   - H(q[2]): (|000⟩+|001⟩+|010⟩+|011⟩+|100⟩+|101⟩+|110⟩+|111⟩)/(2√2)
4. **Measurement**: Tracing out q[1], q[2], states with q[0]=|0⟩ contribute probability 4/8=0.5, and q[0]=|1⟩ also 4/8=0.5, yielding {|0⟩: 0.5, |1⟩: 0.5}.

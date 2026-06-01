# ISQ training COT RAG corpus: circuit_basics shard 24

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1819

- task_id: `isqTrain/1819`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `660`

### Prompt

I need an isQ program to Apply Ry(pi*9/6) to |0> and measure.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task type: code_generation (Reasoning generation based on the prompt/reference).
    *   Goal: Explain the step-by-step reasoning for applying $R_y(9\pi/6)$ to $|0\rangle$ and measuring.
    *   Output: ONLY the reasoning section starting with "## Reasoning".
    *   Constraint: Concise (3-8 lines), use Dirac notation, precise state evolution.

2.  **Analyze the Circuit / Math:**
    *   Initial state: $|0\rangle$
    *   Gate: $R_y(9\pi/6) = R_y(3\pi/2)$.
    *   Matrix of $R_y(\theta) = \begin{pmatrix} \cos(\theta/2) & -\sin(\theta/2) \\ \sin(\theta/2) & \cos(\theta/2) \end{pmatrix}$.
    *   Here $\theta/2 = 3\pi/4$.
    *   $\cos(3\pi/4) = -1/\sqrt{2}$.
    *   $\sin(3\pi/4) = 1/\sqrt{2}$.
    *   Resulting state: $\cos(3\pi/4)|0\rangle + \sin(3\pi/4)|1\rangle = -\frac{1}{\sqrt{2}}|0\rangle + \frac{1}{\sqrt{2}}|1\rangle$.
    *   Alternatively, $R_y(3\pi/2) = R_y(\pi + \pi/2)$. Up to global phase, it's equivalent to $R_y(\pi/2)$. Let's check: $R_y(\pi) X_2P |0\rangle = Y |0\rangle = i|1\rangle$. Wait, no. $R_y(\pi/2)|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
    *   $R_y(3\pi/2)|0\rangle = R_y(4\pi/2 - \pi/2)|0\rangle = R_y(-\pi/2)|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
    *   Let's re-evaluate:
        *   $R_y(3\pi/4 \times 2) = R_y(3\pi/2)$.
        *   Wait, $\theta = 9\pi/6 = 3\pi/2$.
        *   $\theta/2 = 3\pi/4$.
        *   $\cos(3\pi/4) = -\frac{1}{\sqrt{2}}$.
        *   $\sin(3\pi/4) = \frac{1}{\sqrt{2}}$.
        *   So $R_y(3\pi/2)|0\rangle = -\frac{1}{\sqrt{2}}|0\rangle + \frac{1}{\sqrt{2}}|1\rangle$.
    *   Probabilities: $P(0) = |-1/\sqrt{2}|^2 = 0.5$. $P(1) = |1/\sqrt{2}|^2 = 0.5$.

3.  **Draft the Reasoning:**
    *   *Goal:* Apply an $R_y$ gate with angle $9\pi/6$ ($3\pi/2$) to a single qubit initialized to $|0\rangle$ and measure it.
    *   *Qubits:* 1 qubit is needed, and 1 is measured.
    *   *Evolution:*
        1.  Initial state: $|0\rangle$
        2.  Apply $R_y(3\pi/2)$: The state evolves to $\cos(3\pi/4)|0\rangle + \sin(3\pi/4)|1\rangle = -\frac{1}{\sqrt{2}}|0\rangle + \frac{1}{\sqrt{2}}|1\rangle$.
        *   (Alternative phrasing: Up to global phase, this is $|-\rangle$, but keeping the exact amplitudes is better.)
    *   *Probabilities:* The magnitude squared of the amplitudes is $| -1/\sqrt{2} |^2 = 0.5$ and $| 1/\sqrt{2} |^2 = 0.5$, giving an equal 50/50 split.

4.  **Refine and Format:**
    *   Ensure constraints: Only

## isqTrain/1758

- task_id: `isqTrain/1758`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3554`

### Prompt

Implement a quantum circuit in isQ: Start with |1000000> and use CNOT fan-out (q[0] controls all others) on 7 qubits. All should become |1>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply CNOT fan-out from q[0] to all other qubits, converting |1000000⟩ to |1111111⟩.
2. **Qubits**: 7 qubits (q[0]–q[6]), all measured.
3. **State evolution**:
   - Initial: |0000000⟩
   - X(q[0]): |1000000⟩ — flips q[0] to |1⟩
   - CNOT(q[0],q[1]): q[0]=|1⟩, so q[1] flips → |1100000⟩
   - CNOT(q[0],q[2]): → |1110000⟩
   - CNOT(q[0],q[3]): → |1111000⟩
   - CNOT(q[0],q[4]): → |1111100⟩
   - CNOT(q[0],q[5]): → |1111110⟩
   - CNOT(q[0],q[6]): → |1111111⟩
4. **Result**: Final state is |1111111⟩ with probability 1.0, since each CNOT deterministically flips its target when the control (q[0]) is |1⟩.

## isqTrain/1719

- task_id: `isqTrain/1719`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5167`

### Prompt

Implement a quantum circuit in isQ: Apply H then Rz(pi/4) to |0>. Measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Initialize a qubit to |0>, apply a Hadamard (H) gate followed by an Rz(pi/4) rotation, and measure the result.
Qubits: 1 qubit is needed and measured.
Evolution:
1. Initial state is |0>.
2. H gate transforms |0> to |+> = (1/√2)(|0> + |1>).
3. Rz(π/4) applies a phase shift: |0> picks up e^(-iπ/8) and |1> picks up e^(iπ/8). The state becomes (e^(-iπ/8)/√2)|0> + (e^(iπ/8)/√2)|1>.
Probabilities: Measurement probabilities are determined by the squared magnitudes of the amplitudes. Both |0> and |1> have an amplitude magnitude of 1/√2, resulting in a 50% probability for each outcome.

## isqTrain/1576

- task_id: `isqTrain/1576`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5086`

### Prompt

Help me write isQ code that On 3 qubits, set q[2]=|1> and apply CNOT with control=q[2], target=q[1]. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Initialize the third qubit to |1> and use it to flip the second qubit via a CNOT gate.
2. Qubits: Requires 3 qubits (q[0], q[1], q[2]), all of which are measured.
3. Evolution:
   - All qubits start in the ground state |000>.
   - `X(q[2])` flips the third qubit, changing the state to |001>.
   - `CNOT(q[2], q[1])` targets the second qubit; since the control q[2] is |1>, the target flips to |1>. The state becomes |011>.
4. Probabilities: The final quantum state is deterministically |011>, so the measurement yields exactly |011> with 100% probability.

## isqTrain/4736

- task_id: `isqTrain/4736`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `1864`

### Prompt

Are these two quantum circuits equivalent in terms of measurement output?

Circuit 1:
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    T(q[0]);
    H(q[0]);
    M(q[0]);
}

```

Circuit 2:
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    S(q[0]);
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

1.  **Analyze Program A**:
    *   Initial state: $|0\rangle$
    *   Apply $H$: $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
    *   Apply $T$: $\frac{1}{\sqrt{2}}(|0\rangle + e^{i\pi/4}|1\rangle)$
    *   Apply $H$: $H \cdot T \cdot H |0\rangle$
    *   Wait, let's just look at the resulting matrix or state directly.
    *   State after $T$: $\frac{1}{\sqrt{2}}(|0\rangle + e^{i\pi/4}|1\rangle)$.
    *   Apply $H$:
        *   $H |0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
        *   $H |1\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$
        *   Resulting state: $\frac{1}{\sqrt{2}} \left[ \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) + \frac{e^{i\pi/4}}{\sqrt{2}}(|0\rangle - |1\rangle) \right]$
        *   $= \frac{1}{2} \left[ (1+e^{i\pi/4})|0\rangle + (1-e^{i\pi/4})|1\rangle \right]$
    *   Probability of 0: $\frac{1}{4} |1+e^{i\pi/4}|^2 = \frac{1}{4} (1 + \cos(\pi/4) \cdot 2 + 1) = \frac{1}{4}(2 + \sqrt{2}) \approx \frac{3.414}{4} \approx 0.8535$
    *   Probability of 1: $\frac{1}{4} |1-e^{i\pi/4}|^2 = \frac{1}{4} (1 - \cos(\pi/4) \cdot 2 + 1) = \frac{1}{4}(2 - \sqrt{2}) \approx 0.1464$
    *   Wait, the prompt says Program A produces {'0': 0.5, '1': 0.5}. Let me re-read.
    *   Ah! $H T H |0\rangle$:
        *   Wait, $H S H = R_x(\pi/2)$ ? No.
        *   Let's check the prompt: "Program A produces {'0': 0.5, '1': 0.5} while Program B produces {'0': 0.853553, '1': 0.146447}."
        *   Wait, did I mess up the states?
        *   Wait, no. Let's do the math carefully.
        *   $H = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$, $T = \begin{pmatrix} 1 & 0 \\ 0 & e^{i\pi/4} \end{pmatrix}$.
        *   $H T H = \frac{1}{2} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix} \begin{pmatrix} 1 & 0 \\ 0 & e^{i\pi/4} \end{pmatrix} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix} = \frac{1}{2} \begin{pmatrix} 1 & e^{i\pi/4} \\ 1 & -e^{i\pi/4} \end{pmatrix} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix} = \frac{1}{2} \begin{pmatrix} 1+e^{i\pi/4} & 1-e^{i\pi/4} \\ 1-e^{i\pi/4} & 1+e^{i\pi/4} \end{pmatrix}$.
        *   Applying to $|0\rangle = \begin{pmatrix} 1 \\ 0 \end{pmatrix}$ gives $\frac{1}{2} \begin{pmatrix} 1+e^{i\pi/4} \\ 1-e^{i\pi/4} \end

### Reference answer

{'equivalent': False, 'explanation': "H*S*H and H*T*H give different measurement probabilities Program A produces {'0': 0.5, '1': 0.5} while Program B produces {'0': 0.853553, '1': 0.146447}.", 'probs_a': {'0': 0.853553, '1': 0.146447}, 'probs_b': {'0': 0.5, '1': 0.5}}

## isqTrain/4707

- task_id: `isqTrain/4707`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4495`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    Rz(pi/2.0, q[0]);
    H(q[0]);
    M(q[0]);
}

```

Second program:
```isq
import std;
qbit q[1];

procedure main() {
    H(q[0]);
    S(q[0]);
    H(q[0]);
    H(q[0]); // add superposition
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

**Program A** applies: H → Rz(π/2) → H to |0⟩. The Rz(π/2) gate is equivalent to the S gate (up to global phase), so the sequence is H → S → H.

Starting from |0⟩:
- After H: (1/√2)(|0⟩ + |1⟩)
- After Rz(π/2): (1/√2)(|0⟩ + i|1⟩)

### Reference answer

{'equivalent': True, 'explanation': 'After adding H gate to Program B, the programs produce the same probability distributions.', 'probs_a': {'0': 0.5, '1': 0.5}, 'probs_b': {'0': 0.5, '1': 0.5}}

## isqTrain/1846

- task_id: `isqTrain/1846`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `172`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[2];
procedure main() {
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes two qubits, q[0] and q[1], to the ground state |00>.
2. A CNOT gate is applied with q[0] as the control and q[1] as the target.
3. Since the control qubit q[0] is in the |0> state, the target qubit q[1] is not flipped.
4. The quantum state remains |00> throughout the computation.
5. Measurement of both qubits will deterministically yield the bitstring 00.

Predicted probability distribution: {'00': 1.0}

### Reference answer

{'predicted_probs': {'00': 1.0}, 'explanation': 'CNOT on |00⟩ does nothing. P(|00⟩) = 1.0 at index 0.'}

## isqTrain/1317

- task_id: `isqTrain/1317`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5047`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes two qubits, `q[0]` and `q[1]`, in the state |00>.
2. An `X` gate is applied to `q[0]`, flipping its state from |0> to |1>.
3. The system evolves into the unentangled state |10>.
4. Both qubits are measured in the computational basis, yielding deterministic outcomes.

Predicted probability distribution: {|10>: 1.0}

### Reference answer

{'predicted_probs': {'2': 1.0}, 'explanation': 'Parametric variant of isqEval/471. Dimension: qubit_variant: q[1] -> q[2].'}

## isqTrain/1756

- task_id: `isqTrain/1756`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1823`

### Prompt

Write isQ code for the following quantum task: Start with |10000> and use CNOT fan-out (q[0] controls all others) on 5 qubits. All should become |1>.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply CNOT fan-out to entangle q[0] with all other qubits, initializing the 5-qubit state to |11111>.
2. **Qubits:** 5 qubits are used, and all 5 are measured.
3. **Evolution:**
   - Initial state: |00000>
   - `X(q[0])` flips qubit 0, transitioning the state to |10000>
   - `CNOT(q[0], q[1])` sees q[0]=|1> and flips q[1], evolving the state to |11000>
   - `CNOT(q[0], q[2])` sees q[0]=|1> and flips q[2], evolving the state to |11100>
   - `CNOT(q[0], q[3])` sees q[0]=|1> and flips q[3], evolving the state to |11110>
   - `CNOT(q[0], q[4])` sees q[0]=|1> and flips q[4], evolving the state to |11111>
4. **Outcome:** Since the final quantum state is exactly the basis state |11111>, a full measurement of all 5 qubits yields the classical bitstring `11111` with a probability of 1.0.

## isqTrain/1603

- task_id: `isqTrain/1603`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4297`

### Prompt

Write isQ code for the following quantum task: Apply Ry(pi*1/8) to each of 2 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply Ry(π/8) to two qubits and measure both.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Initial state: |00⟩
   - After Ry(π/8) on q[0]: (cos(π/16)|0⟩ + sin(π/16)|1⟩) ⊗ |0⟩
   - After Ry(π/8) on q[1]: (cos(π/16)|0⟩ + sin(π/16)|1⟩)⊗²
4. **Expected probabilities**: Since the final state is a product, P(00)=cos⁴(π/16)≈0.925, P(01)=P(10)=cos²(π/16)sin²(π/16)≈0.037, P(11)=sin⁴(π/16)≈0.0015.

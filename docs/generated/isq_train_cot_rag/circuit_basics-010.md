# ISQ training COT RAG corpus: circuit_basics shard 10

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1721

- task_id: `isqTrain/1721`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4909`

### Prompt

Implement the following in isQ: Apply Rx(pi) then Ry(pi) to |0>. Measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply Rx(π) followed by Ry(π) to |0⟩ and measure the resulting state.
2. **Qubits**: 1 qubit allocated, 1 measured.
3. **State evolution**:
   - Start: |0⟩
   - After Rx(π): Rx(π)|0⟩ = -i|1⟩ (flips |0⟩ to |1⟩ with phase -i)
   - After Ry(π): Ry(π)(-i|1⟩) = i|0⟩ (flips |1⟩ back to |0⟩ with global phase i)
4. **Expected result**: Final state is i|0⟩ ≡ |0⟩ (up to global phase), so measurement yields 0 with probability 1.

## isqTrain/1745

- task_id: `isqTrain/1745`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4350`

### Prompt

Implement the following in isQ: Apply CZ to |00>. Measure both qubits. (CZ only adds phase to |11>, invisible in Z-basis.)

### Chain-of-thought reasoning

## Reasoning
- Goal: Prepare |00>, apply a CZ gate, and measure both qubits.
- Qubits: 2 global qubits `q[2]`, both measured.
- State evolution: Start in |00>. CZ applies a -1 phase only to |11⟩, leaving |00⟩ unchanged, so CZ|00⟩ = |00⟩.
- Probabilities: Measuring |00⟩ in the Z-basis yields |00⟩ with certainty, giving P={|00⟩: 1.0}.

## isqTrain/1623

- task_id: `isqTrain/1623`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2440`

### Prompt

Create an isQ quantum circuit that Apply SWAP(q[1],q[2]) twice (identity) on 4 qubits with q[1]=|1>. Measure all.

### Chain-of-thought reasoning

## Reasoning
The circuit initializes 4 qubits in |0000> and prepares q[1] in the |1> state before applying a double swap (three-CNOT decomposition) identity operation between q[1] and q[2].
1. Initial state: |0000>
2. X(q[1]): Flips q[1] to |1>, changing the state to |0100>.
3. swap (three-CNOT decomposition)(q[1], q[2]): Swaps q[1] and q[2], evolving the state to |0010>.
4. swap (three-CNOT decomposition)(q[1], q[2]): Swaps them back, reverting the state to |0100>.
Because the double swap (three-CNOT decomposition) acts as an identity operation, the system remains deterministically in the |0100> state. Measuring all qubits yields the bitstring 0100 with a probability of 1.0.

## isqTrain/1562

- task_id: `isqTrain/1562`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3899`

### Prompt

I need an isQ program to Apply Z then H to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Apply Z followed by H to |0>, then measure.
Qubits: 1 qubit (q[0]) is allocated and measured.
State evolution:
- Initial: |0⟩
- After Z: |0⟩ (Z leaves |0⟩ unchanged)
- After H: |+⟩ = (|0⟩ + |1⟩)/√2
Expected probabilities: {|0⟩: 0.5, |1⟩: 0.5}, since |+⟩ is an equal superposition.

## isqTrain/1842

- task_id: `isqTrain/1842`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1125`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[3];
procedure main() {
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Three qubits are initialized in the ground state |000>.
2. No quantum gates are applied, so the quantum state remains |000>.
3. The measurements M(q[0]), M(q[1]), and M(q[2]) act directly on the |000> state.
4. Since the state is exactly |000>, all qubits will collapse to |0> with certainty.

Predicted probability distribution: {'000': 1.0}

### Reference answer

{'predicted_probs': {'000': 1.0}, 'explanation': 'No gates applied, all qubits in |0⟩. P(|000⟩) = 1.0 at index 0.'}

## isqTrain/1485

- task_id: `isqTrain/1485`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `5229`

### Prompt

Write isQ code for the following quantum task: Encode the classical value 12/16 into a qubit using angle encoding (Ry rotation with angle pi*12/16). Measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Encode classical value 12/16 = 3/4 into a qubit via Ry rotation and measure.
2. **Qubits**: 1 qubit (q[0]), which is measured.
3. **State evolution**:
   - Initial state: |0>
   - Apply Ry(3π/4, q[0]): state becomes cos(3π/8)|0> + sin(3π/8)|1>
   - Where Ry(θ) rotates around Y-axis: cos(θ/2)|0> + sin(θ/2)|1>
4. **Probabilities**: 
   - P(|0>) = cos²(3π/8) = cos²(67.5°) ≈ 0.1464
   - P(|1>) = sin²(3π/8) = sin²(67.5°) ≈ 0.8536

## isqTrain/1614

- task_id: `isqTrain/1614`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5136`

### Prompt

Code this in isQ: Apply Ry(pi*4/8) to each of 3 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply rotation Ry(π/2) to each of 3 qubits, preparing them in the |+⟩ state, then measure all.
2. **Qubits**: 3 qubits are allocated, and all are measured.
3. **State evolution**: 
   - Start in the initial state |000⟩.
   - Apply Ry(π/2) to q[0]: cos(π/4)|0⟩ + sin(π/4)|1⟩ = |+⟩. State becomes |+00⟩.
   - Apply Ry(π/2) to q[1] and q[2] similarly. Final state is |+++⟩ = (|0⟩+|1⟩)⊗³ / (2√2).
4. **Probabilities**: Measuring |+++⟩ yields an equal 1/8 probability for all 8 possible basis states (000, 001, ..., 111).

## isqTrain/1656

- task_id: `isqTrain/1656`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2264`

### Prompt

用isQ实现Apply Rz(pi/2) to a qubit in state |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply an Rz rotation of π/2 to a qubit initialized to |0> and measure the result.
2. Qubits: 1 qubit is needed, and it is measured.
3. Evolution: The qubit starts in the ground state |0>. Applying Rz(π/2) adds a global phase of e^(-iπ/4) to the |0> state, resulting in the state e^(-iπ/4)|0>. Since global phase is physically unobservable, the state remains effectively |0>.
4. Probabilities: Measurement collapses the state to |0> with a probability of 1.0 (100%).

## isqTrain/4583

- task_id: `isqTrain/4583`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1666`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    Rx(pi/4.0, q[0]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise step-by-step analysis of an isQ quantum program, ending with the predicted probability distribution of the measurement outcomes. The analysis should use Dirac notation.

2.  **Analyze the Circuit:**
    *   Initial state: $|00\rangle$
    *   `H(q[0])`: Applies Hadamard to qubit 0. State becomes $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle) = |+0\rangle$.
    *   `CNOT(q[0], q[1])`: Control q0, target q1. Flips q1 if q0 is 1. State becomes $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$ (Bell state).
    *   `Rx(pi/4.0, q[0])`: Applies $R_x(\pi/4)$ to q0.
        *   $R_x(\theta) = \cos(\theta/2)I - i\sin(\theta/2)X$.
        *   $R_x(\pi/4) = \cos(\pi/8)I - i\sin(\pi/8)X$.
        *   Let $c = \cos(\pi/8)$ and $s = \sin(\pi/8)$.
        *   State: $\frac{1}{\sqrt{2}} [ (c|0\rangle - is|1\rangle)|0\rangle + (-is|0\rangle + c|1\rangle)|1\rangle ]$
        *   $= \frac{1}{\sqrt{2}} [ c|00\rangle - is|10\rangle - is|01\rangle + c|11\rangle ]$.
    *   `X(q[0])`: Applies X gate to q0. Swaps $|0\rangle$ and $|1\rangle$ for q0.
        *   State: $\frac{1}{\sqrt{2}} [ c|10\rangle - is|00\rangle - is|11\rangle + c|01\rangle ]$.
        *   $= \frac{1}{\sqrt{2}} [ -is|00\rangle + c|01\rangle + c|10\rangle - is|11\rangle ]$.
    *   `M(q[0]); M(q[1]);`: Measure both.
        *   Probabilities are the squared magnitudes of the amplitudes.
        *   $P(00) = |-is/\sqrt{2}|^2 = 0.5 s^2 = 0.5 \sin^2(\pi/8) \approx 0.5 \times 0.1464466 = 0.0732233$.
        *   $P(01) = |c/\sqrt{2}|^2 = 0.5 c^2 = 0.5 \cos^2(\pi/8) \approx 0.5 \times 0.853553 = 0.426776$.
        *   $P(10) = |c/\sqrt{2}|^2 = 0.5 c^2 \approx 0.426776$.
        *   $P(11) = |-is/\sqrt{2}|^2 = 0.5 s^2 \approx 0.0732233$.

3.  **Format the Output:**
    *   Must start with "## Circuit Analysis"
    *   3-8 lines for simple, up to 15 for complex. This is relatively simple, so ~6-8 lines.
    *   End with the predicted probability distribution matching the required format.

4.  **Drafting the text:**
    ## Circuit Analysis
    1. **Initial state:** $|00\rangle$.
    2. **H(q[0])**: Creates superposition, evolving state to $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
    3. **CNOT(q[0], q[1])**: Entangles qubits, resulting in the Bell state $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$.
    4. **Rx(pi/4, q[0])**: Rotates qubit 0 around X-axis by $\pi/4$. The state becomes $\frac{1}{\sqrt{2}}[\cos(\pi/8)|00\rangle - i\sin(\pi/8)|10\rangle - i\sin(\pi/8)|01\rangle + \cos(\pi/8)|11\rangle]$.
    5. **X(q

### Reference answer

{'predicted_probs': {'00': 0.073223, '01': 0.426777, '10': 0.426777, '11': 0.073223}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.0732, P(|01>) = 0.4268, P(|10>) = 0.4268, P(|11>) = 0.0732.'}

## isqTrain/4687

- task_id: `isqTrain/4687`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1500`

### Prompt

判断以下两段isQ代码是否产生相同的测量结果：

代码1：
```isq
import std;
qbit q[1];

procedure main() {
    Y(q[0]);
    M(q[0]);
}

```

代码2：
```isq
import std;
qbit q[1];

procedure main() {
    X(q[0]);
    H(q[0]); // add superposition
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** initializes qubit q[0] in |0>, applies a Y gate to transition it to i|1>, and measures the qubit. 
2. **Program B** initializes qubit q[0] in |0>, applies an X gate to flip it to |1>, and then applies an H gate to put it into the |-> state.
3. The key difference is that Program A results in a deterministic state (i|1>), while Program B creates a superposition (|->).
4. Measurement probabilities are different: Program A yields 100% probability of measuring 1, whereas Program B yields a 50/50 distribution for measuring 0 and 1.
5. Verdict: Not equivalent

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'1': 1.0}, 'probs_b': {'0': 0.5, '1': 0.5}}

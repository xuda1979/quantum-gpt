# ISQ training COT RAG corpus: circuit_basics shard 16

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1592

- task_id: `isqTrain/1592`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3507`

### Prompt

请用isQ语言编写一个量子电路：Put 3 qubits in superposition, measure only q[2].

### Chain-of-thought reasoning

## Reasoning
1. The goal is to initialize 3 qubits into a uniform superposition and measure the state of a single target qubit.
2. We initialize 3 qubits in the ground state $|000\rangle$.
3. Applying a Hadamard gate (H) to each qubit independently creates the product state $|+\rangle \otimes |+\rangle \otimes |+\rangle = \frac{1}{2\sqrt{2}}\sum_{x=0}^{7} |x\rangle$.
4. Because q[2] is

## isqTrain/4680

- task_id: `isqTrain/4680`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4552`

### Prompt

Are these two quantum circuits equivalent in terms of measurement output?

Circuit 1:
```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    X(q[1]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

Circuit 2:
```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    H(q[0]); // add superposition
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

1. **Program A**: Applies X to q[0] and q[1], then CNOT(q[0], q[1]).
   - |00⟩ →X→ |11⟩ →CNOT→ |10⟩
   - Measurement always yields q[0]=1, q[1]=0 (bitstring 10).

2. **Program B**: Applies X to q[0], then H(q[0]).
   - |00⟩ →X(q[0])→ |10⟩ →H(q[0])→ (1/√2)(|00⟩ − |10⟩) = |−⟩⊗|0⟩
   - Measurement yields 00 or 10, each with 50% probability.

3. **Key difference**: Program A produces a deterministic outcome (always |10⟩), while Program B creates superposition on q[0], yielding probabilistic outcomes (50% |00⟩, 50% |10⟩).

4. **Measurement probabilities differ**: Program A → P(10)=1; Program B → P(00)=0.5, P(10)=0.5.

**Verdict: Not equivalent (No)**

### Reference answer

{'equivalent': False, 'explanation': 'After adding H gate to Program B, the programs produce different probability distributions.', 'probs_a': {'10': 1.0}, 'probs_b': {'00': 0.5, '10': 0.5}}

## isqTrain/4759

- task_id: `isqTrain/4759`
- task_type: `code_equivalence`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4646`

### Prompt

Determine if these two isQ implementations are functionally equivalent:

Version A:
```isq
import std;
qbit q[2];

procedure main() {
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

Version B:
```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** starts in the default state |00> and applies a CNOT gate with q[0] as the control and q[1] as the target. Since the control qubit q[0] is |0>, the target remains unchanged, leaving the state as |00>.
2. **Program B** starts in |00>, but first applies an X gate to q[0], changing the state to |10>. It then applies the same CNOT gate. With q[0] in the |1> state, the CNOT flips the target q[1] to |1>, resulting in the final state |11>.
3. **The key difference** is the initial X gate applied to the control qubit in Program B, which activates the CNOT operation to flip the target qubit.
4. The measurement probabilities are different. Program A will always yield the bitstring '00' (probability 1.0), whereas Program B will always yield the bitstring '11' (probability 1.0).
5. **Verdict:** No

### Reference answer

{'equivalent': False, 'explanation': "CNOT with control=1 flips target to get |11>, control=0 does nothing Program A produces {'11': 1.0} while Program B produces {'00': 1.0}.", 'probs_a': {'00': 1.0}, 'probs_b': {'11': 1.0}}

## isqTrain/1617

- task_id: `isqTrain/1617`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5697`

### Prompt

实现以下量子计算任务（使用isQ）：Apply Ry(pi*7/8) to each of 3 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
- Goal: Apply the rotation gate Ry(7π/8) independently to 3 qubits and measure them.
- Qubits: 3 qubits are initialized to |000⟩, and all are measured at the end.
- State evolution: Applying Ry(7π/8) to each qubit maps |0⟩ → cos(7π/16)|0⟩ + sin(7π/16)|1⟩.
- The resulting 3-qubit entangled-free state is (cos(7π/16)|0⟩ + sin(7π/16)|1⟩)⊗3.
- Measurement probabilities: The probability of measuring '1' for any individual qubit is p = sin2(7π/16). The final bitstring probabilities are the product of independent Bernoulli trials (e.g., P(011) = (1-p)p2).

## isqTrain/4754

- task_id: `isqTrain/4754`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `multi_controlled_logic`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `5723`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);
    X(q[1]);
    H(q[1]);
    CNOT(q[0], q[1]);
    H(q[1]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a circuit analysis of an isQ program, predicting the measurement outcome probabilities. The output must follow a specific format and length constraints (3-15 lines, concise, step-by-step).

2.  **Analyze the isQ Code**:
    *   `X(q[0]); X(q[1]);`: Initialize `q[0]` and `q[1]` to |1>. State: |11>
    *   `H(q[1]);`: Apply H to `q[1]`. State: 1/sqrt(2)(|10> - |11>)
    *   `CNOT(q[0], q[1]);`: Control is `q[0]`, target is `q[1]`.
        *   |10> -> |11>
        *   |11> -> |10>
        *   State becomes: 1/sqrt(2)(|11> - |10>) = -1/sqrt(2)(|10> - |11>)
    *   `H(q[1]);`: Apply H to `q[1]` again.
        *   H(|0>) = |+>, H(|1>) = |->
        *   H(|10>) = 1/sqrt(2)(|10> + |11>)
        *   H(|11>) = 1/sqrt(2)(|10> - |11>)
        *   H(1/sqrt(2)(|11> - |10>)) = H(-1/sqrt(2)(|10> - |11>)) = -1/sqrt(2)(1/sqrt(2)(|10>+|11>) - 1/sqrt(2)(|10>-|11>)) = -1/2 (2|11>) = -|11>
        *   State is -|11>. (Global phase doesn't matter, it's equivalent to |11>)
    *   `X(q[0]);`: Apply X to `q[0]`. State: Flips `q[0]` from 1 to 0. State becomes -|01> (or simply |01>).
    *   `M(q[0]); M(q[1]);`: Measurement.
        *   Probability of |01> is 1.0 (100%).

3.  **Format the Output**:
    *   Start with "## Circuit Analysis"
    *   Explain operations (X, X, H, CNOT, H, X).
    *   Step-by-step state evolution using Dirac notation.
    *   Final state: |01>
    *   Predicted probability distribution: {|01>: 1.0}

4.  **Draft the text (aiming for conciseness)**:
    ## Circuit Analysis
    1. **Operations**: The circuit applies X to both qubits, followed by H on q[1], CNOT(q[0], q[1]), H on q[1], and finally X on q[0].
    2. **State Evolution**:
       - Initial state: |00>
       - After `X(q[0]); X(q[1]);`: |11>
       - After `H(q[1]);`: 1/√2 (|10⟩ - |11⟩)
       - After `CNOT(q[0], q[1]);`: 1/√2 (|11⟩ - |10⟩)
       - After `H(q[1]);`: -|11⟩ ≡ |11⟩
       - After `X(q[0]);`: |01⟩
    3. **Final State**: The system is deterministically in the |01⟩ state before measurement.
    4. **Probabilities**: {|01>: 1.0}

5.  **Review against constraints**:
    *   3-8 lines for simple circuits (this is simple).
    *   Dirac notation used.
    *   Starts with "## Circuit Analysis".
    *   no code blocks.
    *   Ends with probability distribution.

    Let's refine the step-by-step to be slightly more compact.
    ## Circuit Analysis
    1. **Operations**: X and X gates initialize the qubits to |11>. Then H, CNOT, and H are applied to create a phase kickback, followed by a final X gate.
    2. **State Evolution**:
       - Start: |00⟩
       - `X(q[0]), X(q[1])`: |11⟩
       - `H(q[1])`: 1/√2 (|10⟩ - |11⟩)
       - `CNOT(q[0], q[1])`: 1/√2 (|11⟩ - |10⟩)
       - `H(q[1])`: -|11⟩
       - `

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|01>) = 1.0000.'}

## isqTrain/1487

- task_id: `isqTrain/1487`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `2159`

### Prompt

Create an isQ quantum circuit that Encode the classical value 14/16 into a qubit using angle encoding (Ry rotation with angle pi*14/16). Measure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Encode classical value 14/16 into a qubit via Ry rotation and measure the resulting state.
2. One qubit is needed (q[0]), and it is measured.
3. Starting from |0⟩, apply Ry(7π/8, q[0]). The Ry gate transforms |0⟩ → cos(7π/16)|0⟩ + sin(7π/16)|1⟩.
4. The measurement probabilities are P(|0⟩) = cos²(7π/16) ≈ 0.0381 and P(|1⟩) = sin²(7π/16) ≈ 0.9619, which matches the predicted output since sin(7π/16) ≈ 0.9808 is close to 1.

## isqTrain/1624

- task_id: `isqTrain/1624`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5462`

### Prompt

帮我写一个isQ程序：Apply SWAP(q[0],q[2]) twice (identity) on 4 qubits with q[0]=|1>. Measure all.

### Chain-of-thought reasoning

## Reasoning
The circuit initializes a 4-qubit register to |1000> and applies two swap (three-CNOT decomposition) gates between q[0] and q[2], effectively acting as an identity operation, before measuring all qubits.
4 qubits are used, and all are measured.
Initial state |0000> transitions to |1000> after the X gate on q[0].
The first swap (three-CNOT decomposition)(q[0], q[2]) exchanges the states of q[0] and q[2], changing the global state to |0010>.
The second swap (three-CNOT decomposition)(q[0], q[2]) swaps them back, restoring the state to |1000>.
Because the final quantum state is exactly |1000>, measuring the register yields the bitstring '1000' with a probability of 1.0.

## isqTrain/4669

- task_id: `isqTrain/4669`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `188`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[2];

procedure main() {
    X(q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit starts in the initial state |00>. The first gate `X(q[1])` flips the second qubit, evolving the state to |01>.
2. `CNOT(q[0], q[1])` applies an X gate to q[1] if q[0] is |1>. Since q[0] is |0>, the state remains |01>.
3. `CNOT(q[1], q[0])` applies an X gate to q[0] if q[1] is |1>. Since q[1] is |1>, q[0] flips to |1>, changing the state to |11>.

### Reference answer

{'predicted_probs': {'00': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 1.0000.'}

## isqTrain/1589

- task_id: `isqTrain/1589`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4630`

### Prompt

Help me write isQ code that Put 2 qubits in superposition, measure only q[1].

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a reasoning section for a specific quantum circuit described in the prompt.
    *   Input prompt: "Put 2 qubits in superposition, measure only q[1]." with reference code.
    *   predicted output: A concise reasoning section starting with "## Reasoning". No isQ code blocks.
    *   Content requirements:
        *   Goal of circuit (1 line)
        *   Qubit count and measurement specifics
        *   Step-by-step state evolution (Dirac notation)
        *   Justification of expected probabilities.
    *   Length constraint: 3-8 lines (simple circuit).

2.  **Analyze the Circuit:**
    *   Initial state: 2 qubits, `q[0]` and `q[1]`. State is $|00\rangle$.
    *   Gate 1: `H(q[0])`. State becomes $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
    *   Gate 2: `H(q[1])`. State becomes $\frac{1}{\sqrt{2}} \otimes \frac{1}{\sqrt{2}} (|00\rangle + |01\rangle + |10\rangle + |11\rangle) = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
    *   Measurement: `M(q[1])`. We trace out or measure the second qubit (if standard notation `q[0]q[1]`, index 1 is the second qubit, usually the right-most or second tensor factor depending on convention. Wait, `q[1]` is measured. Let's write it as $|q_0 q_1\rangle$).
    *   State: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
    *   Measuring `q[1]`:
        *   Probability of $|0\rangle$ for `q[1]` is $|1/2|^2 + |1/2|^2 = 0.5$.
        *   Probability of $|1\rangle` for `q[1]` is $|1/2|^2 + |1/2|^2 = 0.5$.
    *   Output format constraint: "Expected measurement probabilities: {|0>: 0.5, |1>: 0.5}". "Number of qubits measured: 1".

3.  **Draft the Reasoning:**
    *   *Goal:* The goal is to put two qubits into an equal superposition of all computational basis states and measure just one of them.
    *   *Setup:* 2 qubits (`q[0]`, `q[1]`) are initialized to $|00\rangle$; only `q[1]` is measured.
    *   *Evolution:*
        *   Initial: $|00\rangle$
        *   After `H(q[0])`: $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$
        *   After `H(q[1])`: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
    *   *Probabilities:* Measuring `q[1]` yields $|0\rangle$ (from $|00\rangle, |10\rangle$) with probability $|\frac{1}{2}|^2 + |\frac{1}{2}|^2 = 0.5$, and $|1\rangle$ (from $|01\rangle, |11\rangle$) with probability $0.5$.

4.  **Refine and Format (Concise):**
    ## Reasoning
    *   The goal is to prepare two qubits in a uniform superposition and measure a single qubit to observe its 50/50 probability distribution.
    *   We need 2 qubits; only `q[1]` is measured.
    *   Starting in $|00\rangle$, applying `H` to `q[0]` creates $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
    *   Applying `H` to `q[1]` entangles them into the full superposition $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
    *   Measuring `q[1]` gives $|0\rangle$ (from $|00\rangle, |10\rangle$) or $|1

## isqTrain/1580

- task_id: `isqTrain/1580`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2429`

### Prompt

Write isQ code for the following quantum task: On 4 qubits, set q[1]=|1> and apply CNOT with control=q[1], target=q[2]. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Initialize qubit 1 to |1> and perform a CNOT gate to entangle/copy its state to qubit 2.
2. **Qubits:** 4 qubits are used (q[0] to q[3]), and all are measured at the end.
3. **State evolution:**
   - Initial state: |0000>
   - Apply X(q[1]): flips q[1] from |0> to |1>, resulting in state |0100>.
   - Apply CNOT(q[1], q[2]): q[1] is the control (in |1>) and q[2] is the target, so q[2] flips from |0> to |1>. The state becomes |0110>.
4. **Measurement probabilities:** Since the final state is exactly |0110> with no superposition, measuring all qubits deterministically yields the bitstring '0110' with a probability of 1.0.

# ISQ training COT RAG corpus: quantum_algorithms shard 104

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/960

- task_id: `isqTrain/960`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `hamiltonian_simulation`, `isq_syntax_ctrl_nctrl`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2775`

### Prompt

Create an isQ quantum circuit that implements a variant of the pauli_evolution pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The task asks me to write an isQ program that implements a variant of the pauli_evolution pattern using q[2] -> q[3]. This means I need to use qubits q[2] and q[3] instead of q[0] and q[1] as In the implementation.

Analyzing the circuit requirements:
- It uses q[0] and q[1] for the ZZ evolution
- It prepares |01> by applying X to q[1]
- It does CNOT(q[0], q[1]), Rz(pi/2, q[1]), CNOT(q[0], q[1])
- It measures q[0], q[1], q[2]

For the variant using q[2] -> q[3], I need:
- A qubit register that can hold q[2] and q[3], so at least 4 qubits
- Prepare eigenstate |...01..> of ZZ where the 01 is on q[2] and q[3]
- Apply the same circuit but with q[2] and q[3]

Let me trace through the state evolution:

1. Initial state: |0000>
2. X(q[3]): |0001> (flip q[3])
3. CNOT(q[2], q[3]): Since q[2] is |0>, no change: |0001>
4. Rz(pi/2, q[3]): |0001> gets phase e^(-i*pi/4), so it becomes e^(-i*pi/4)|0001>
5. CNOT(q[2], q[3]): No change: e^(-i*pi/4)|0001>
6. Measurement: {|0001>: 1.0}

Wait, let me reconsider the indexing. In isQ, q[0] is typically the least significant bit. Let me check The implementation again.

Actually, looking at the predicted output {|010>: 1.0}, this suggests that the measurement bitstring "010" corresponds to q[0]=0, q[1]=1, q[2]=0 in the notation where earlier measured qubit = higher bit.

Let me re-trace The implementation:
1. |00> for q[0], q[1]
2. X(q[1]): |01>
3. CNOT(q[0], q[1]): Since q[0]=0, target unchanged: |01>
4. Rz(pi/2, q[1]): Global phase added (since |01> is eigenstate of Z on q[1])
5. CNOT(q[0], q[1]): Unchanged: |01>

The measurement order is M(q[0]), M(q[1]), M(q[2]). With "earlier measured qubit = higher bit", q[0] is the highest bit. So |010> means q[0]=0, q[1]=1, q[2]=0.

For my variant using q[2] and q[3]:
- Need at least 4 qubits (q[0] through q[3])
- Prepare eigenstate of ZZ on q[2] and q[3] by applying X(q[3])
- Apply CNOT(q[2], q[3]), Rz(pi/2, q[3]), CNOT(q[2], q[3])
- Measure all qubits

State evolution:
1. |0000>
2. X(q[3]): |0001> (but this depends on bit ordering - let me think more carefully)

Actually, I think the bit ordering in the state is:
- |q[0]q[1]q[2]q[3]>

So:
1. |0000>
2. X(q[3]): |0001>
3. CNOT(q[2], q[3]): |0001> (control q[2]=0, no flip)
4. Rz(pi/2, q[3]): e^(-i*pi/4)|0001>
5. CNOT(q[2], q[3]): e^(-i*pi/4)|0001>

Measurement order: M(q[0]), M(q[1]), M(q[2]), M(q[3])
With earlier measured = higher bit:
- q[0] = bit 3 (highest)
- q[1] = bit 2
- q[2] = bit 1
- q[3] = bit 0 (lowest)

So the bitstring would be 0001 in decimal = 1 in the probs array.

Actually wait, I need to double-check the "earlier measured qubit = higher bit" convention. If I measure q[0], q[1], q[2], q[3] in that order, and the first measured is the highest bit:

## isqTrain/2074

- task_id: `isqTrain/2074`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3182`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[2];
procedure main() {
    Ry(1.04719755119660, q[0]);
    Ry(0.62831853071796, q[1]);
    CNOT(q[0], q[1]);
    Rz(0.78539816339745, q[0]);
    Rx(0.52359877559830, q[1]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

The program applies the following operations:
1. Ry(1.04719755119660, q[0]) - rotation around Y-axis by π/3 radians on qubit 0
2. Ry(0.62831853071796, q[1]) - rotation around Y-axis by 0.2π radians on qubit 1
3. CNOT(q[0], q[1]) - controlled-NOT with q[0] as control, q[1] as target
4. Rz(0.78539816339745, q[0]) - rotation around Z-axis by π/4 radians on qubit 0
5. Rx(0.52359877559830, q[1]) - rotation around X-axis by π/6 radians on qubit 1
6. CNOT(q[0], q[1]) - another controlled-NOT
7. Measurements on both qubits

Let me compute the final state. The initial state is |00⟩.

After Ry(π/3) on q[0]:
cos(π/6)|0⟩ + sin(π/6)|1⟩ = (√3/2)|0⟩ + (1/2)|1⟩

After Ry(0.2π) on q[1]:
cos(0.1π)|0⟩ + sin(0.1π)|1⟩

The state is now:
[(√3/2)|0⟩ + (1/2)|1⟩] ⊗ [cos(0.1π)|0⟩ + sin(0.1π)|1⟩]

= (√3/2)cos(0.1π)|00⟩ + (√3/2)sin(0.1π)|01⟩ + (1/2)cos(0.1π)|10⟩ + (1/2)sin(0.1π)|11⟩

Let me compute numerical values:
cos(0.1π) ≈ 0.9511
sin(0.1π) ≈ 0.3090
√3/2 ≈ 0.8660

So state is approximately:
0.8235|00⟩ + 0.2676|01⟩ + 0.4755|10⟩ + 0.1545|11⟩

After CNOT(q[0], q[1]):
0.8235|00⟩ + 0.2676|01⟩ + 0.4755|11⟩ + 0.1545|10⟩

After Rz(π/4) on q[0]:
0.8235|00⟩ + 0.2676|01⟩ + 0.4755*e^(iπ/4)|11⟩ + 0.1545*e^(iπ/4)|10⟩

Wait, let me be more careful. Rz(θ) applies:
|0⟩ → |0⟩
|1⟩ → e^(iθ)|1⟩

So on q[0], when q[0] is |1⟩, we multiply by e^(iπ/4).

State becomes:
0.8235|00⟩ + 0.2676|01⟩ + 0.1545·e^(iπ/4)|10⟩ + 0.4755·e^(iπ/4)|11⟩

After Rx(π/6) on q[1]:
This transforms |0⟩ → cos(π/12)|0⟩ - i·sin(π/12)|1⟩ and |1⟩ → -i·sin(π/12)|0⟩ + cos(π/12)|1⟩

cos(π/12) ≈ 0.9659
sin(π/12) ≈ 0.2588

This gets complex. Let me use matrices.

Let me define:
α = 0.8235 (|00⟩ coefficient)
β = 0.2676 (|01⟩ coefficient)
γ = 0.1545·e^(iπ/4) (|10⟩ coefficient)
δ = 0.4755·e^(iπ/4) (|11⟩ coefficient)

Now Rx(π/6) acts on q[1]:
|00⟩ → cos(π/12)|00⟩ - i·sin(π/12)|01⟩
|01⟩ → -i·sin(π/12)|00⟩ + cos(π/12)|01⟩
|10⟩ → cos(π/12)|10⟩ - i·sin(π/12)|11⟩
|11⟩ → -i·sin(π/12)|10⟩ + cos(π/12)|11⟩

So new

### Reference answer

{'predicted_probs': {'00': 0.6377, '01': 0.1123, '10': 0.2126, '11': 0.0374}, 'explanation': 'Quantum volume 2-qubit circuit with 2 SU(4)-like layers.'}

## isqTrain/2040

- task_id: `isqTrain/2040`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3687`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[2];
procedure main() {
    X(q[0]);
    Rx(1.57079632679490, q[0]);
    Rx(1.57079632679490, q[1]);
    CNOT(q[0], q[1]);
    Rz(1.57079632679490, q[1]);
    CNOT(q[0], q[1]);
    Rx(-1.57079632679490, q[0]);
    Rx(-1.57079632679490, q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise, step-by-step analysis of a 2-qubit isQ quantum program to determine the probability distribution of the measurement outcomes. The output must be exactly in the format requested, using Dirac notation.

2.  **Analyze the isQ code:**
    *   `X(q[0])`: Applies X gate to q[0]. Initial state |00> -> |10>.
    *   `Rx(pi/2, q[0])`: Applies $R_x(\pi/2)$ to q[0]. $\pi/2 \approx 1.570796...$
        *   Matrix: $\frac{1}{\sqrt{2}} \begin{pmatrix} 1 & -i \\ -i & 1 \end{pmatrix}$.
        *   $R_x(\pi/2)|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle - i|1\rangle)$
        *   $R_x(\pi/2)|1\rangle = \frac{1}{\sqrt{2}}(-i|0\rangle + |1\rangle)$
        *   State so far: $|10\rangle \xrightarrow{R_x(\pi/2) \otimes I} \frac{1}{\sqrt{2}}(-i|00\rangle + |10\rangle)$.
    *   `Rx(pi/2, q[1])`: Applies $R_x(\pi/2)$ to q[1].
        *   State: $\frac{1}{\sqrt{2}}(-i|0\rangle + |1\rangle) \otimes \frac{1}{\sqrt{2}}(|0\rangle - i|1\rangle) = \frac{1}{2}(-i|00\rangle - |01\rangle + |10\rangle - i|11\rangle)$.
    *   `CNOT(q[0], q[1])`: Control q[0], target q[1].
        *   $|00\rangle \to |00\rangle$, $|01\rangle \to |01\rangle$, $|10\rangle \to |11\rangle$, $|11\rangle \to |10\rangle$.
        *   State: $\frac{1}{2}(-i|00\rangle - |01\rangle + |11\rangle - i|10\rangle) = \frac{1}{2}(-i|00\rangle - |01\rangle - i|10\rangle + |11\rangle)$.
    *   `Rz(pi/2, q[1])`: Applies $R_z(\pi/2)$ to q[1]. Matrix: $\begin{pmatrix} e^{-i\pi/4} & 0 \\ 0 & e^{i\pi/4} \end{pmatrix}$.
        *   $|0\rangle \to e^{-i\pi/4}|0\rangle = \frac{1}{\sqrt{2}}(1-i)|0\rangle$
        *   $|1\rangle \to e^{i\pi/4}|1\rangle = \frac{1}{\sqrt{2}}(1+i)|1\rangle$
        *   Applying to the second qubit of the state:
            *   Coeff of $|00\rangle$: $-i \times e^{-i\pi/4} = e^{-i\pi/2} e^{-i\pi/4} = e^{-3i\pi/4}$
            *   Coeff of $|10\rangle$: $-i \times e^{-i\pi/4} = e^{-3i\pi/4}$
            *   Coeff of $|01\rangle$: $-1 \times e^{i\pi/4} = -e^{i\pi/4}$
            *   Coeff of $|11\rangle$: $1 \times e^{i\pi/4} = e^{i\pi/4}$
        *   State: $\frac{1}{2}(e^{-3i\pi/4}|00\rangle - e^{i\pi/4}|01\rangle + e^{-3i\pi/4}|10\rangle + e^{i\pi/4}|11\rangle)$
            Wait, $e^{i\pi/4} = \frac{1}{\sqrt{2}}(1+i)$, $e^{-3i\pi/4} = \frac{1}{\sqrt{2}}(-1-i)$. Let's just keep exponential form.
    *   `CNOT(q[0], q[1])`: Control q[0], target q[1].

### Reference answer

{'predicted_probs': {'01': 0.5, '10': 0.5}, 'explanation': 'YY evolution on |10>: generates P(|01>)=0.5, P(|10>)=0.5.'}

## isqTrain/774

- task_id: `isqTrain/774`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1252`

### Prompt

请用isQ语言编写一个量子电路：implements the weighted_adder pattern. Include explicit identity operations in the circuit (H-H pair before M(q[3])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

The circuit implements a weighted adder summing three input qubits into a 2-bit result (sum q[3], carry q[4]).

**State evolution:** |00000⟩ → X on q[0..2] → |11100⟩ → CNOT(q[0],q[3]) → |11110⟩ → Toffoli(q[1],q[3],q[4]) → |11111⟩ → CNOT(q[1],q[3]) → |11101⟩ → Toffoli(q[2],q[3],q[4]) → |11101⟩ → CNOT(q[2],q[3]) → |11111⟩ → H(q[3])·H(q[3]) = I → |11111⟩

**Key observations:** The adder computes 1+1+1=3 (binary 11). The Toffoli gates handle carry propagation while CNOTs compute the sum bit. The H-H pair cancels (H²=I), demonstrating gate cancellation awareness while having no net effect.

**Measurement:** M(q[3])=1 (sum bit), M(q[4])=1 (carry bit) → bitstring |11⟩ with probability 1.0, since q[3] is the higher-order measured bit and q[4] is the lower-order bit.

## isqTrain/1264

- task_id: `isqTrain/1264`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `data_encoding_qml`, `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `56`

### Prompt

Write an isQ program that implements the data_encoding pattern with modified rotation parameters (num_pi3_to_pi4). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit implements a ZZ feature map data encoding pattern with 2 qubits.

Initial state: |00>

Layer 1:
- H(q[0]); H(q[1]) → (|00> + |01> + |10> + |11>)/2
- Rz(0.78539816339745, q[0]) = Rz(π/4, q[0]) → applies phase e^{-iπ/8} to |0> and e^{iπ/8} to |1> on q[0]
- Rz(0.52359877559830, q[1]) = Rz(π/6, q[1]) → applies phase e^{-iπ/12} to |0> and e^{iπ/12} to |1> on q[1]
- CNOT(q[0], q[1])
- Rz(0.54831135561608, q[1]) ≈ Rz(π/3 * π/6, q[1]) - this is the ZZ interaction term
- CNOT(q[0], q[1])

Layer 2:
- H(q[0]); H(q[1])
- Rz(0.78539816339745, q[0])
- Rz(0.52359877559830, q[1])
- M(q[0]); M(q[1])

Let me trace through more carefully.

After H on both: |+⟩|+⟩ = (|00> + |01> + |10> + |11>)/2

After Rz(π/4) on q[0] and Rz(π/6) on q[1]:
The state becomes:
|00>: e^{-iπ/8} * e^{-iπ/12} = e^{-i5π/24}
|01>: e^{-iπ/8} * e^{iπ/12} = e^{-iπ/24}
|10>: e^{iπ/8} * e^{-iπ/12} = e^{iπ/24}
|11>: e^{iπ/8} * e^{iπ/12} = e^{i5π/24}

Actually, let me be more careful. Rz(θ)|0⟩ = e^{-iθ/2}|0⟩ and Rz(θ)|1⟩ = e^{iθ/2}|1⟩.

So after H⊗H: |ψ⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

After Rz(π/4) on q[0]:
|00⟩ → e^{-iπ/8}|00⟩
|10⟩ → e^{iπ/8}|10⟩
|01⟩ stays |01⟩
|11⟩ stays |11⟩

After Rz(π/6) on q[1]:
|00⟩ → e^{-iπ/8} * e^{-iπ/12}|00⟩ = e^{-i5π/24}|00⟩
|01⟩ → e^{-iπ/12}|01⟩  (wait, no, q[1] of |01⟩ is |1⟩, so e^{iπ/12}|01⟩)

Hmm, let me be more careful. Rz(θ) on q[1]:
|00⟩ → e^{-iθ/2}|00⟩
|01⟩ → e^{iθ/2}|01⟩
|10⟩ → e^{-iθ/2}|10⟩
|11⟩ → e^{iθ/2}|11⟩

With θ = π/6:
|00⟩ → e^{-iπ/12}|00⟩
|01⟩ → e^{iπ/12}|01⟩
|10⟩ → e^{-iπ/12}|10⟩
|11⟩ → e^{iπ/12}|11⟩

Combining both Rz:
|00⟩: e^{-iπ/8} * e^{-iπ/12} = e^{-i5π/24}
|01⟩: e^{-iπ/8} * e^{iπ/12} = e^{-iπ/24}
|10⟩: e^{iπ/8} * e^{-iπ/12} = e^{iπ/24}
|11⟩: e^{iπ/8} * e^{iπ/12} = e^{i5π/24}

Now CNOT(q[0], q[1]):
|00⟩ → |00⟩
|01⟩ → |01⟩
|10⟩ → |11⟩
|11⟩ → |10⟩

So state becomes:
e^{-i5π/24}|

## isqTrain/2728

- task_id: `isqTrain/2728`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `4749`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[4];
procedure main() {
    H (q[0]);
    for i in 1:4 {

        CNOT (q[i-1], q[i]);
    }
    for i in 0:4{
        M(q[i]);
    }
}
```

### Chain-of-thought reasoning

## Circuit Analysis

1. **Operations applied:**
   - H(q[0]) — Hadamard on qubit 0
   - CNOT(q[0], q[1]) — control=0, target=1
   - CNOT(q[1], q[2]) — control=1, target=2
   - CNOT(q[2], q[3]) — control=2, target=3

2. **State evolution:**
   - Initial: |0000⟩
   - After H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |000⟩ = (|0000⟩ + |1000⟩)/√2
   - After CNOT(q[0], q[1]): (|0000⟩ + |1100⟩)/√2
   - After CNOT(q[1], q[2]): (|0000⟩ + |1110⟩)/√2
   - After CNOT(q[2], q[3]): (|0000⟩ + |1111⟩)/√2

3. **Final state before measurement:** (|0000⟩ + |1111⟩)/√2 — a 4-qubit GHZ state.

4. **Probability distribution:** Each basis state has amplitude 1/√2, giving probability |1/√2|² = 0.5.

Predicted probabilities: {'0000': 0.5, '1111': 0.5}

### Reference answer

{'predicted_probs': {'0000': 0.5, '1111': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/2989

- task_id: `isqTrain/2989`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1054`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[2];
procedure main() {
    X(q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Gates applied**:
   - `X(q[1])` flips qubit q[1].
   - `CNOT(q[0], q[1])` applies CNOT with control q[0] and target q[1].
   - `CNOT(q[1], q[0])` applies CNOT with control q[1] and target q[0].
   - `CNOT(q[0], q[1])` applies CNOT with control q[0] and target q[1].
2. **State evolution** (using |q[1], q[0]>):
   - Initial state: |0,0>
   - `X(q[1])`: |0,0> → |1,0>
   - `CNOT(q[0], q[1])`: q[0] is |0>, target unchanged: |1,0> → |1,0>
   - `CNOT(q[1], q[0])`: q[1] is |1>, target q[0] flips: |1,0> → |1,1>
   - `CNOT(q[0], q[1])`: q[0] is |1>, target q[1] flips: |1,1> → |0,1>
3. **Final state before measurement**: |q[1]=0, q[0]=1>
4. **Probability distribution**: M(q[0]) yields 1 (higher bit), M(q[

### Reference answer

{'predicted_probs': {'10': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/62

- task_id: `isqTrain/62`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4824`

### Prompt

请用isQ语言编写一个量子电路：implements the phase_kickback pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Goal: Create a "Reasoning" section explaining the given isQ code (Phase Kickback pattern with explicit identity `H-H` pair).
    *   Task Type: Code generation (although I'm providing reasoning, the prompt structure dictates this).
    *   Specific constraints:
        *   Use Dirac notation.
        *   Concise: 3-15 lines.
        *   Explain: goal, qubits measured, state evolution step-by-step, probability outcome justification.
        *   Output ONLY the "## Reasoning" section (no code blocks).
    *   Circuit to analyze:
        1.  Initialize 2 qubits `|00>`
        2.  `X(q[1])`, `H(q[1])` -> `|0>|->`
        3.  `H(q[0])` -> `|+>|->`
        4.  `CNOT(q[0], q[1])` -> Phase kickback: `CNOT |+>|-> = -|+>|->` (up to global phase, actually it's `(-|+>)|->`). Wait: `CNOT(|0>-|1>)|->` -> let's trace carefully.
            *   State before CNOT: `(1/2)(|0> + |1>)(|0> - |1>)`
            *   CNOT flips target when control is 1: `(1/2)(|0>(|0>-|1>) + |1>(|1>-|0>))`
            *   Factor out: `(1/2)(|0> - |1>)(|0> - |1>)`? No, that's not right.
            *   `|1>(|1>-|0>) = -|1>(|0>-|1>) = -|1>|->`.
            *   So state is `(1/2)(|0>|-> - |1>|->) = (1/2)(|0>-|1>)|-> = |->|->`.
        5.  `H(q[0])` -> `H|-> = -|1>`. State: `-|1>|->`
        6.  `H(q[0])` -> `H(-|1>) = -|->`.
        7.  `H(q[0])` -> `H(-|->) = |1>`. State: `|1>|->`
        8.  Measure both.
            *   `q[0]` is `|1>`, so P(`q[0]=1`) = 1.
            *   `q[1]` is `|->`, so P(`q[1]=0`) = 0.5, P(`q[1]=1`) = 0.5.
            *   Combined probabilities: `|10>` and `|11>`, each 0.5.
    *   Wait, let me double-check the bit order. "earlier measured qubit = higher bit".
        *   Measurement: `M(q[0]); M(q[1]);`
        *   Higher bit is `q[0]`. Lower bit is `q[1]`.
        *   If `q[0]` = 1, `q[1]` = 0, bitstring is `10`.
        *   If `q[0]` = 1, `q[1]` = 1, bitstring is `11`.

2.  **Drafting the Reasoning:**
    *   *Goal*: Implement the phase kickback circuit with an explicit H-H identity pair to demonstrate gate cancellation awareness.
    *   *Qubits*: Uses 2 qubits (`q[0]`, `q[1]`), both are measured.
    *   *State evolution*:
        *   Start: `|00>`
        *   `X(q[1]); H(q[1]);`: `|0>(XH|0>) = |0>|->`
        *   `H(q[0])`: `|+>|->`
        *   `CNOT(q[0], q[1])`: Transforms to `|->|->` (kickback phase).
        *   `H(q[0])`: Changes `|->` to `-|1>`, yielding `-|1>|->`.
        *   `H-H` pair on `q[0]`: Acts as identity, canceling out (or shifting state: `-|-> -> |1>`).
        *   Resulting state before measurement: `|1>|->`.
    *   *Probabilities*: Measuring `|1>|->` yields 50% `|10>` and 50% `|11>` (since `|-> = 1

## isqTrain/750

- task_id: `isqTrain/750`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1070`

### Prompt

帮我写一个isQ程序：implements the modular_adder pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a modular adder computing (a + b) mod 3, encoding a=2, adding b=1, yielding 0 with overflow flag set.

2. **Qubits**: 3 qubits (q[0]=LSB, q[1]=MSB of result, q[2]=overflow flag); only q[0] and q[1] are measured.

3. **State evolution**:
   - |000⟩ → X(q[1]) → |010⟩ (encode a=2)
   - → X(q[0]) → |110⟩ (add 1, now 3=11₂)
   - → Toffoli(q[0],q[1],q[2]) → |111⟩ (flag overflow since ≥3)
   - → CNOT(q[2],q[0]) → |101⟩ (subtract 3: flip q[0])
   - → CNOT(q[2],q[1]) → |001⟩ (subtract 3: flip q[1]; result q[1:0]=00)
   - → H(q[0]) → (|001⟩+|101⟩)/√2 (superposition on q[0])
   - → H(q[0]) → |001⟩ (H-H cancels, identity demonstrated)
   - → M(q[0])=0, M(q[1])=0

4. **Expected probabilities

## isqTrain/3644

- task_id: `isqTrain/3644`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `3842`

### Prompt

Code this in isQ: the 3-qubit inverse Quantum Fourier Transform (QFT†) on input |011>. Use bit-reversal swaps first, then apply inverse rotation stages with negative angles. Measure all qubits.

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

1. Start with |000⟩
2. Apply X(q[1]) and X(q[2]) → |011⟩

Now we need to apply inverse QFT on 3 qubits.

The QFT on 3 qubits maps |j⟩ to (1/√8) Σ_k e^{2πijk/8} |k⟩

The inverse QFT maps |k⟩ to (1/√8) Σ_j e^{-2πijk/8} |j⟩

For input |011⟩ = |3⟩:
QFT†|3⟩ = (1/√8) Σ_j e^{-2πi·3·j/8} |j⟩

= (1/√8)(|0⟩ + e^{-2πi·3/8}|1⟩ + e^{-2πi·6/8}|2⟩ + e^{-2πi·9/8}|3⟩ + e^{-2πi·12/8}|4⟩ + e^{-2πi·15/8}|5⟩ + e^{-2πi·18/8}|6⟩ + e^{-2πi·21/8}|7⟩)

This is a uniform superposition over all 8 states! Each coefficient has magnitude 1/√8, so the probability of measuring each state is 1/8 = 0.125.

Let me verify: the phases don't matter for measurement probabilities, all amplitudes have equal magnitude |1/√8|² = 1/8.

Now let me trace through the circuit:

Starting: |000⟩
After X(q[1]), X(q[2]): |011⟩

Now bit-reversal swaps: swap q[0] and q[2]
Using CNOT swaps: |011⟩ → swap q[0] and q[2] → |110⟩

Now inverse rotation stages (applied from high to low qubit index):

Stage for q[2]:
H(q[2]): |110⟩ → |11+⟩ = |11⟩(|0⟩+|1⟩)/√2 = (|110⟩+|111⟩)/√2

Stage for q[1]:
ctrl Rz(-2π/4, q[2], q[1]): applies Rz(-π/2) on q[1] controlled by q[2]
H(q[1]): Hadamard on q[1]

Stage for q[0]:
ctrl Rz(-2π/8, q[2], q[0]): applies Rz(-π/4) on q[0] controlled by q[2]
ctrl Rz(-2π/4, q[1], q[0]): applies Rz(-π/2) on q[0] controlled by q[1]
H(q[0]): Hadamard on q[0]

Actually, let me think about this more carefully. The inverse QFT circuit with bit-reversal applied first.

The standard QFT circuit on 3 qubits (q[0] is most significant):
1. H on q[2], then controlled R_k gates
2. H on q[1], then controlled R_k gates  
3. H on q[0]
4. Swap q[0] and q[2]

The inverse QFT reverses this:
1. Swap q[0] and q[2] (bit-reversal first)
2. H on q[0], then inverse controlled R_k gates (with negative angles)
3. H on q[1], then inverse controlled R_k gates
4. H on q[2]

Wait, let me look at the code more carefully. The circuit does:
1. Prepare |011⟩
2. CNOT swaps (swap q[0] and q[2]) → |110⟩
3. H(q[2])
4. ctrl Rz(-2π/4, q[2], q[1])
5. H(q[1])
6. ctrl Rz(-2π/8, q[2], q[0])
7. ctrl Rz(-2π/4, q[1], q[0])
8. H(q[0])
9. Measure all

So the inverse QFT is applied from q[2] down to q[0], with the bit-reversal swap first.

This is the standard inverse QFT. The result should be uniform superposition since input is |3⟩ = |011⟩ and after bit reversal becomes |110⟩ = |6⟩, and QFT† on any computational basis state gives a uniform superposition (in terms of probabilities).

Wait, that's not right. QFT† on a computational basis state doesn't necessarily give uniform probabilities. Let me reconsider.

Actually, QFT†|j⟩ = (1/√N) Σ

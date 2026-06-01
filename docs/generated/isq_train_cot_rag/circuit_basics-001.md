# ISQ training COT RAG corpus: circuit_basics shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1570

- task_id: `isqTrain/1570`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5570`

### Prompt

用isQ实现Apply the gate sequence H-H-H to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply three consecutive Hadamard gates to an initial |0> state and measure the result.
2. Needs 1 qubit, initialized to |0>, which is measured at the end.
3. State evolution:
   - Start: |0>
   - First H: (|0> + |1>)/√2 = |+>
   - Second H: |0> (since H² = I)
   - Third H: (|0> + |1>)/√2 = |+>
4. The final state is |+>, resulting in an equal superposition with measurement probabilities P(|0>) = 0.5 and P(|1>) = 0.5.

## isqTrain/1586

- task_id: `isqTrain/1586`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3134`

### Prompt

Help me write isQ code that On 4 qubits, set q[3]=|1> and apply CNOT with control=q[3], target=q[1]. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Initialize q[3] to |1>, apply a CNOT with q[3] as control and q[1] as target, then measure all qubits.
2. **Qubits**: 4 qubits (q[0] to q[3]) are allocated, and all are measured.
3. **State Evolution**:
   - Initial state: |0000>
   - `X(q[3])` flips q[3] to |1>: state becomes |0001>
   - `CNOT(q[3], q[1])` flips the target q[1] because the control q[3] is |1>: state becomes |0101>
4. **Expected Probabilities**: The final quantum state is deterministically |0101> (where q[3]=1, q[2]=0, q[1]=1, q[0]=0). Therefore, the measurement outcome is strictly 0101 with a probability of 1.0.

## isqTrain/1595

- task_id: `isqTrain/1595`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `334`

### Prompt

Help me write isQ code that Put 4 qubits in superposition, measure only q[2].

### Chain-of-thought reasoning

## Reasoning
The goal is to put 4 qubits into an equal superposition and measure only one of them.
The circuit requires 4 qubits, all initialized to the ground state |0000⟩.
Applying Hadamard (H) gates to all 4 qubits transforms the state to an equal superposition over all 16 possible combinations: (1/4) * Σ|x⟩ for x in {0,1}^4.
Because the global state is completely uniform, tracing out the other qubits leaves q[2] in a completely mixed local state.
Consequently, measuring only q[2] yields an exact 50% probability for |0⟩ and a 50% probability for |1⟩.

## isqTrain/1605

- task_id: `isqTrain/1605`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5378`

### Prompt

用isQ实现Apply Ry(pi*3/8) to each of 2 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply Ry(3π/8) rotation to each of 2 qubits independently, then measure both.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Initial: |00⟩
   - After Ry(3π/8) on q[0]: [cos(3π/16)|0⟩ + sin(3π/16)|1⟩] ⊗ |0⟩
   - After Ry(3π/8) on q[1]: [cos(3π/16)|0⟩ + sin(3π/16)|1⟩] ⊗ [cos(3π/16)|0⟩ + sin(3π/16)|1⟩]
4. **Measurement probabilities**: Since the qubits are independent and identically rotated:
   - P(00) = cos⁴(3π/16) ≈ 0.478
   - P(01) = cos²(3π/16)·sin²(3π/16) ≈ 0.214
   - P(10) = sin²(3π/16)·cos²(3π/16) ≈ 0.214
   - P(11) = sin⁴(3π/16) ≈ 0.095

## isqTrain/1588

- task_id: `isqTrain/1588`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4827`

### Prompt

Help me write isQ code that Put 2 qubits in superposition, measure only q[0].

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create superposition on 2 qubits and measure only q[0].
2. **Qubits**: 2 qubits (q[0], q[1]); only q[0] is measured.
3. **State evolution**:
   - Initial: |00⟩
   - After H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2
   - After H(q[1]): (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
4. **Measurement**: Since q[0] is in state (|0⟩ + |1⟩)/√2, measuring it yields P(|0⟩) = 0.5 and P(|1⟩) = 0.5.

## isqTrain/1483

- task_id: `isqTrain/1483`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `intermediate`
- concept_tags: `data_encoding_qml`
- source: `isq_train_cot`
- dataset_index: `5293`

### Prompt

Write an isQ program that Encode the classical value 10/16 into a qubit using angle encoding (Ry rotation with angle pi*10/16). Measure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Encode classical value 10/16 into a qubit via Ry rotation with angle π·10/16, then measure.
2. **Qubits**: 1 qubit (q[0]), which is measured.
3. **State evolution**:
   - Initial state: |0⟩
   - Apply Ry(10π/16) to q[0]: Ry(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩ = cos(5π/16)|0⟩ + sin(5π/16)|1⟩
4. **Measurement probabilities**: P(|0⟩) = cos²(5π/16) ≈ 0.3087, P(|1⟩) = sin²(5π/16) ≈ 0.6913, matching expected values.

## isqTrain/4585

- task_id: `isqTrain/4585`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4670`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[2];

procedure main() {
    X(q[0]);  // replaced H with X
    CNOT(q[0], q[1]);
    Rx(pi/4.0, q[0]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict probability distribution of measurement outcomes for an isQ program.
    *   Program:
        
    *   Constraints: Use Dirac notation, concise (3-8 lines for simple), start with "## Circuit Analysis", end with the predicted probability distribution. Do not use code blocks.

2.  **Step-by-step State Evolution:**
    *   Initial state: $|00\rangle$
    *   $X(q[0])$: Flips $q[0]$ to $|1\rangle$. State becomes $|10\rangle$.
    *   $CNOT(q[0], q[1])$: Control $q[0]$, target $q[1]$. Since $q[0]$ is $|1\rangle$, it flips $q[1]$. State becomes $|11\rangle$. (Wait, let's check bit ordering. Usually $|q_1 q_0\rangle$ or $|q_0 q_1\rangle$. Let's stick to standard $|q_0 q_1\rangle$ where $q_0$ is higher bit if measured first, but in Dirac notation I'll just write $|q_0, q_1\rangle$. Let's trace: $X$ on $q_0$ -> $|1, 0\rangle$. CNOT($q_0$, $q_1$) -> $|1, 1\rangle$.
    *   $Rx(\pi/4, q[0])$: Applies $Rx(\pi/4)$ to $q_0$.
        $Rx(\theta) = \begin{pmatrix} \cos(\theta/2) & -i\sin(\theta/2) \\ -i\sin(\theta/2) & \cos(\theta/2) \end{pmatrix}$.
        Here $\theta = \pi/4$, so $\theta/2 = \pi/8$.
        $\cos(\pi/8) = \frac{\sqrt{2+\sqrt{2}}}{2} \approx 0.9239$.
        $\sin(\pi/8) = \frac{\sqrt{2-\sqrt{2}}}{2} \approx 0.3827$.
        Applying to $q_0$ in state $|1, 1\rangle$:
        $q_0$ state is $|1\rangle$.
        $Rx(\pi/4)|1\rangle = -i\sin(\pi/8)|0\rangle + \cos(\pi/8)|1\rangle$.
        So the 2-qubit state is $-i\sin(\pi/8)|0, 1\rangle + \cos(\pi/8)|1, 1\rangle$.
    *   Let's check the squares of amplitudes.
        Prob of $q_0=0, q_1=1$ (i.e., $|01\rangle$ where $q_0$ is higher bit? The prompt says "earlier measured qubit = higher bit" so $q[0]$ is bit 1, $q[1]$ is bit 0. So state $q_0=0, q_1=1$ is $01$ in binary? No, wait.
        Let's carefully read: "indexed by measurement bitstring (earlier measured qubit = higher bit)".
        $q[0]$ is measured first. So $q[0]$ is the 1s place (bit 0) or higher bit (bit 1)? "higher bit" means bit 1 (value 2).
        So $q[0]$ corresponds to bit 1, $q[1]$ corresponds to bit 0.
        Wait, The predicted output `{|01>: 0.1464..., |11>: 0.8535...}`.
        Let's look at the values: $0.1464 \approx \sin^2(\pi/8) = \frac{1 - \cos(\pi/4)}{2} = \frac{1 - 1/\sqrt{2}}{2} \approx \frac{0.29289}{2} \approx 0.1464466$.
        $0.8535 \approx \cos^2(\pi/8) = \frac{1 + \cos(\pi/4)}{2} \approx 0.85355$.
        Since $q[0]$ is $|0\rangle$ in the first

### Reference answer

{'predicted_probs': {'01': 0.146447, '11': 0.853553}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|01>) = 0.1464, P(|11>) = 0.8536.'}

## isqTrain/1569

- task_id: `isqTrain/1569`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1526`

### Prompt

帮我写一个isQ程序：Apply the gate sequence X-X-X to |0> and measure.

### Chain-of-thought reasoning

## Reasoning
1. Apply three X gates to initial state |0> and measure.
2. Requires 1 qubit, which is measured at the end.
3. Evolution: |0> ->(X)-> |1> ->(X)-> |0> ->(X)-> |1>.
4. The final state is exactly |1>, so measurement yields |1> with probability 1.0.

## isqTrain/4657

- task_id: `isqTrain/4657`
- task_type: `output_prediction`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4558`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[1];

procedure main() {
    X(q[0]);
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes one qubit, `q[0]`, to the ground state |0>.
2. The first X gate (Pauli-X) is applied, acting as a bit-flip to change the state to |1>.
3. The second X gate is applied, which flips the state back to |0> (since X^2 equals the identity matrix).
4. The final state before measurement is exactly |0>.
5. A measurement in the computational basis will deterministically yield the 0 state.

Predicted probability distribution: {|0>: 1.0, |1>: 0.0}

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 1.0000.'}

## isqTrain/1747

- task_id: `isqTrain/1747`
- task_type: `code_generation`
- category: `circuit_basics`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2242`

### Prompt

请用isQ语言编写一个量子电路：Apply CZ to |10>. Measure both qubits. (CZ only adds phase to |11>, invisible in Z-basis.)

### Chain-of-thought reasoning

## Reasoning
1. Goal: Prepare the state |10>, apply a CZ gate, and measure to demonstrate its effect on computational basis states.
2. Qubits: 2 qubits are used, and both are measured.
3. Evolution: Starting from |00>, an X gate on q[0] flips the state to |10>.
4. Applying CZ(q[0], q[1]) introduces a phase factor only if both qubits are |1>. Since the state is |10>, it remains unchanged.
5. Probabilities: The final state is exactly |10>, so measurement yields the bitstring 10 with a probability of 1.0.

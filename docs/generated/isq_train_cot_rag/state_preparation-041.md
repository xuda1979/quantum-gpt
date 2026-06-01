# ISQ training COT RAG corpus: state_preparation shard 41

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3743

- task_id: `isqTrain/3743`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `49`

### Prompt

请用isQ语言编写一个量子电路：Prepare a 2-qubit product state by applying Ry(0.0) to q[0] and Ry(0.5) to q[1]. Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare a 2-qubit product state via Y-rotations and measure both qubits.
Qubits: Requires 2 qubits (q[0], q[1]), both of which are measured.
State Evolution:
1. Initial state is |00>.
2. Ry(0.0) on q[0] is an identity operation, leaving q[0] in |0>.
3. Ry(0.5) on q[1] transforms it from |0> to cos(0.25)|0> + sin(0.25)|1>.
4. The combined 2-qubit state is cos(0.25)|00> + sin(0.25)|01>.
Probabilities: P

## isqTrain/1750

- task_id: `isqTrain/1750`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `expert`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1524`

### Prompt

Write an isQ program that an equal superposition on 8 qubits by applying Hadamard to each. Measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare an equal superposition over all 8-qubit basis states and measure them.
2. **Qubits**: 8 qubits (`q[0]` to `q[7]`), all are measured.
3. **Evolution**: The system starts in the $|00000000\rangle$ state. Applying the Hadamard gate $H$ to each qubit individually transforms each $|0\rangle$ into the superposition $(|0\rangle + |1\rangle)/\sqrt{2}$ (the $|+\rangle$ state). 
4. **Final State**: The joint state becomes $\frac{1}{\sqrt{2^8}} \sum_{x=0}^{255} |x\rangle = \frac{1}{16} (|00000000\rangle + \dots + |11111111\rangle)$.
5. **Probabilities**: Measuring this state collapses it into one of the $256$ possible computational basis states. Since the amplitude for each state has an absolute value squared of $(1/16)^2 = 1/256$, every outcome from $|00000000\rangle$ to $|11111111\rangle$ has an equal probability of exactly $0.00390625$.

## isqTrain/399

- task_id: `isqTrain/399`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `330`

### Prompt

Write isQ code for the following quantum task: implements the ghz_state_preparation pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

## Reasoning
1.  **Goal**: Prepare a 4-qubit GHZ state, $\frac{1}{\sqrt{2}}(|0000\rangle + |1111\rangle)$, using the gate decomposition CNOT = H CZ H.
2.  **Qubits**: 4 global qubits `q[4]`, all measured at the end.
3.  **State Evolution**:
    *   Start with $|0000\rangle$.
    *   Apply `H(q[0])` $\rightarrow \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)|000\rangle$.
    *   Implement `CNOT(q[0], q[1])` via `H(q[1])`, `CZ(q[0], q[1])`, `H(q[1])` $\rightarrow \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)|00\rangle$.
    *   Implement `CNOT(q[1], q[2])` via `H(q[2])`, `CZ(q[1], q[2])`, `H(q[2])` $\rightarrow \frac{1}{\sqrt{2}}(|000\rangle +

## isqTrain/3200

- task_id: `isqTrain/3200`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5412`

### Prompt

Code this in isQ: an isQ program: apply Ry(3*pi/16) to a qubit and measure.

### Chain-of-thought reasoning

## Reasoning
The goal is to initialize a single qubit in the |0> state, apply an Ry(3*pi/16) rotation, and measure the resulting state.
One qubit is needed, and it is the only qubit measured at the end of the circuit.
Starting from the initial state |0>, the Ry(3*pi/16) gate rotates the state around the Y-axis of the Bloch sphere.
The resulting quantum state is cos(3*pi/32)|0> + sin(3*pi/32)|1>.
The measurement probabilities follow directly from the state amplitudes: the probability of measuring |0> is cos²(3*pi/32) ≈ 0.9157, and the probability of measuring |1> is sin²(3*pi/32) ≈ 0.0843.

## isqTrain/1952

- task_id: `isqTrain/1952`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `2653`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[2];
procedure main() {
    X(q[0]);
    H(q[0]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations:** `X` gate on q[0], `H` gate on q[0], `CNOT` with q[0] as control and q[1] as target.
2. **State Evolution:**
   - Start with |00>.
   - `X(q[0])`: Flips q[0] to |1>, resulting in |10>.
   - `H(q[0])`: Applies Hadamard to q[0], changing |1> to |->. The state is (|00> - |10>) / sqrt(2).
   - `CNOT(q[0], q[1])`: Entangles the qubits. |00> remains |00>, while |10> becomes |11>. The state becomes (|00> - |11>) / sqrt(2).
3. **Final State:** (|00> - |11>) / sqrt(2), a Bell state.
4. **Measurement Probabilities:** Measuring yields |00> with probability |1/sqrt(2)|^2 = 0.5 and |11> with probability |-1/sqrt(2)|^2 = 0.5.

Predicted measurement probabilities: {'00': 0.5, '11': 0.5}

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'Bell state Phi-'}

## isqTrain/1465

- task_id: `isqTrain/1465`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3135`

### Prompt

Code this in isQ: Prepare the computational basis state |01011> on 5 qubits by applying X gates to the appropriate qubits, then measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Prepare the 5-qubit computational basis state |01011⟩ by flipping specific qubits from |0⟩ to |1⟩.
2. **Qubits:** 5 qubits (q[0]–q[4]), all measured.
3. **State evolution:**
   - Start: |00000⟩
   - X(q[1]) → |01000⟩
   - X(q[3]) → |01010⟩
   - X(q[4]) → |01011⟩
4. **Expected probabilities:** Since the final state is exactly |01011⟩ (a computational basis state with no superposition), measurement yields |01011⟩ with probability 1.0.

## isqTrain/3189

- task_id: `isqTrain/3189`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `176`

### Prompt

Help me write isQ code that an isQ program: apply Ry(5*pi/9) to one qubit, then CNOT to a second qubit, creating partial entanglement.

### Chain-of-thought reasoning

## Reasoning
The goal is to create a partially entangled two-qubit state.
Two qubits are required, initialized to |00>, and both are measured at the end.
Applying Ry(5π/9) to the first qubit rotates it, yielding the product state cos(5π/18)|00> + sin(5π/18)|10>.
App

## isqTrain/146

- task_id: `isqTrain/146`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `2802`

### Prompt

Help me write isQ code that implements the state_preparation pattern with modified rotation parameters (pi3_to_pi4). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

## Reasoning

The goal is to prepare a single-qubit state by applying an Rx rotation with angle π/4 to an initial |0⟩ state.

**Qubits:** 1 qubit (q[0]) is used and measured.

**State evolution:**
1. Initial state: |0⟩
2. After Rx(π/4, q[0]): cos(π/8)|0⟩ - i·sin(π/8)|1⟩

**Expected probabilities:**
- P(|0⟩) = |cos(π/8)|² = cos²(π/8) ≈ 0.8536
- P(|1⟩) = |-i·sin(π/8)|² = sin²(π/8) ≈ 0.1464

The Rx(π/4) gate rotates the state around the X-axis by π/4 radians, creating a superposition heavily weighted toward |0⟩ since the rotation angle is small (less than π/2).

## isqTrain/1549

- task_id: `isqTrain/1549`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4494`

### Prompt

Code this in isQ: Apply H gate to each of 4 qubits and measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a uniform superposition over all 4-qubit basis states by applying H to each qubit, then measure all.
2. **Qubits**: 4 qubits (q[0]–q[3]), all measured.
3. **State evolution**:
   - Initial: |0000⟩
   - After H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |000⟩ = |+⟩|000⟩
   - After H(q[1]): |+⟩|+⟩|00⟩
   - After H(q[2]): |+⟩|+⟩|+⟩|0⟩
   - After H(q[3]): |++++⟩ = (1/4)∑_{x∈{0,1}⁴} |x⟩
4. **Probabilities**: The final state is an equal superposition of all 16 basis states, so each has probability |1/4|² = 1/16 = 0.0625.

## isqTrain/567

- task_id: `isqTrain/567`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `849`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[5];

procedure main() {
    X(q[0]);
    X(q[2]);
    X(q[3]);
    M(q);
}
```

### Chain-of-thought reasoning

The user wants an analysis of the given isQ program.
The program initializes 5 qubits: `q[0]`, `q[1]`, `q[2]`, `q[3]`, `q[4]` in the state |00000>.
Then applies X gate to `q[0]`, `q[2]`, `q[3]`.
Then measures all qubits `M(q)`.

Initial state: |00000>
After X(q[0]): |10000>
After X(q[2]): |10100>
After X(q[3]): |10110>

Wait, isQ output string format: `--probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit).`
Let's trace carefully.
If measured array is `q` with indices 0, 1, 2, 3, 4.
Typically, earlier measured qubit is higher bit. So q[0] is the highest bit (bit 4, value 16), q[1] is bit 3 (value 8), q[2] is bit 2 (value 4), q[3] is bit 1 (value 2), q[4] is bit 0 (value 1).
Wait, if `q[0]` is the highest bit, then |q[0] q[1] q[2] q[3] q[4]> = |1 0 1 1 0>.
Wait, wait. In the predicted output, the example says: "Expected measurement probabilities: {|01101>: 1.0}"
Wait, if `q[0]` is 1, `q[1]` is 0, `q[2]` is 1, `q[3]` is 1, `q[4]` is 0.
Wait, `X(q[0])`, `X(q[2])`, `X(q[3])`.
If the state is |q[4] q[3] q[2] q[1] q[0]>, then it would be |01101>.
Let's re-read the rule: "earlier measured qubit = higher bit".
When you measure `q` which is `q[0]` to `q[4]`, earlier measured qubit is `q[0]`.
So `q[0]` is the highest bit.
Then the bitstring is `q[0] q[1] q[2] q[3] q[4]`.
Since `q[0]=1`, `q[1]=0`, `q[2]=1`, `q[3]=1`, `q[4]=0`, the string should be `10110`.
Why does the reference say `{|01101>: 1.0}`? Wait, did I copy the reference correctly?
Ah, let's look at the reference:
Wait, `Expected measurement probabilities: {|01101>: 1.0}` is what the prompt gave.
Wait, if `q[0]=0`, `q[1]=1`, `q[2]=1`, `q[3]=0`, `q[4]=1`. That would mean X was applied to q[1], q[2], q[4]. But the code says `X(q[0])`, `X(q[2])`, `X(q[3])`.
Is it possible the bitstring is reversed? "earlier measured qubit = higher bit" -> if it's reversed, maybe earlier measured is lowest bit?
No, wait! Is there a chance the "earlier measured qubit = higher bit" is just standard convention, but the bitstring is written with highest bit on the left?
Yes, so highest bit on the left is q[0].
Let's write out `10110`. But wait, the prompt's circuit implementation says `{|01101>: 1.0}`?
Wait, in the prompt:
"circuit implementation / circuit code:
...
Expected measurement probabilities: {|01101>: 1.0}"
Oh, wait! If The implementation says `{|01101>: 1.0}`, it might be a typo in my reading or the reference.
Let me check the code:
`X(q[0]); X(q[2]); X(q[3]);`
If `q[0]` is leftmost, it's `10110`.
Wait, if `q[0]` is rightmost (lowest bit), it's `01101`.
`q[0]` is bit 0. `q[1]` is bit 1, `q[2]` is bit 2, `q[3]` is bit 3, `q[4]` is bit 4.
If earlier measured is higher bit, then

### Reference answer

{'predicted_probs': {'13': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/186. Dimension: predict probabilities for reference circuit.'}

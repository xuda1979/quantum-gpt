# ISQ training COT RAG corpus: isq_control_flow shard 1

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1645

- task_id: `isqTrain/1645`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `basic`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `3696`

### Prompt

Write isQ code for the following quantum task: Use an int variable to control a for loop that applies X gate 3 times to a qubit. Measure the result. (3 X gates = X, since X^2 = I).

### Chain-of-thought reasoning

## Reasoning
The goal is to apply the X gate three times to a single qubit and measure the result.
One qubit is required, which is initialized to the ground state |0>.
Step-by-step state evolution:
1. Initial state: |0>
2. After 1st X gate: |1>
3. After 2nd X gate: |0>
4. After 3rd X gate: |1>
Because the final quantum state is deterministically |1>, measurement yields the outcome |1> with probability 1.0.

## isqTrain/1647

- task_id: `isqTrain/1647`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `basic`
- concept_tags: `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `3768`

### Prompt

请用isQ语言编写一个量子电路：Apply Hadamard gate 2 times using a for loop. Since H^2=I, an even number of H applications yields identity.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Apply the Hadamard (H) gate twice to a single qubit initialized to |0>.
2. **Qubits:** 1 qubit is used and measured.
3. **State evolution:**
   - Initial state: |0>
   - Apply 1st H: transforms |0> to (|0> + |1>)/√2 = |+>
   - Apply 2nd H: transforms |+> back to |0>, since H² = I
4. **Measurement:** The final state is exactly |0>, yielding a 100% probability of measuring 0.

## isqTrain/1688

- task_id: `isqTrain/1688`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_for_loop`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5007`

### Prompt

请用isQ语言编写一个量子电路：Use a for loop to apply a CNOT chain on 3 qubits starting from |100>. Each qubit controls the next.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply a CNOT chain starting from |100⟩, where each qubit controls the next, propagating the |1⟩ state.
2. Three qubits (q[0], q[1], q[2]) are used and all are measured.
3. State evolution:
   - Initial: |000⟩ → X(q[0]) → |100⟩
   - CNOT(q[0], q[1]): control q[0]=|1⟩ flips q[1] → |110⟩
   - CNOT(q[1], q[2]): control q[1]=|1⟩ flips q[2] → |111⟩
4. Final state |111⟩ is a computational basis state, so measurement yields |111⟩ with probability 1.0.

## isqTrain/248

- task_id: `isqTrain/248`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_while_loop`
- source: `isq_train_cot`
- dataset_index: `1253`

### Prompt

实现以下量子计算任务（使用isQ）：implements a compact variant of the arithmetic_circuit pattern using q[2] -> q[1]. The circuit should use a reduced qubit register.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a compact arithmetic-style circuit using a reduced 1-qubit register that accumulates rotation via a counted loop.

2. **Qubits**: 1 qubit (`q[0]`) is used and measured.

3. **State evolution**:
   - Initialize: |0⟩
   - Loop iteration 1: Rx(π/6) → cos(π/12)|0⟩ - i·sin(π/12)|1⟩
   - Loop iteration 2: Rx(π/6) → cos(π/6)|0⟩ - i·sin(π/6)|1⟩
   - Loop iteration 3: Rx(π/6) → cos(π/4)|0⟩ - i·sin(π/4)|1⟩ = (1/√2)|0⟩ - i(1/√2)|1⟩

4. **Expected probabilities**: The cumulative rotation of 3 × π/6 = π/2 yields P(|0⟩) = cos²(π/4) = 0.5 and P(|1⟩) = sin²(π/4) = 0.5.

## isqTrain/1740

- task_id: `isqTrain/1740`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `basic`
- concept_tags: `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `3884`

### Prompt

Create an isQ quantum circuit that Use a for loop from 1 to 4 (exclusive) applying X each iteration. 3 iterations means X^3.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply X gate three times to a single qubit starting in |0⟩.
2. **Qubits**: 1 qubit (q[0]), which is measured.
3. **State evolution**:
   - Initial state: |0⟩
   - After 1st X: X|0⟩ = |1⟩
   - After 2nd X: X|1⟩ = |0⟩
   - After 3rd X: X|0⟩ = |1⟩
4. **Expected probabilities**: Since X³ = X (as X² = I), the final state is |1⟩, giving measurement probability {|1⟩: 1.0}.

## isqTrain/252

- task_id: `isqTrain/252`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_while_loop`
- source: `isq_train_cot`
- dataset_index: `2971`

### Prompt

Implement the following in isQ: implements the arithmetic_circuit pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

The user is asking me to generate a reasoning section for an isQ quantum program that implements the arithmetic_circuit pattern.
The specific pattern includes:
1. A counted while loop applying `Rx(pi/6)` three times to `q[0]`.
2. A pair of Hadamard gates `H(q[0])` followed by `H(q[0])` acting as an explicit identity operation.
3. Measurements of `q[0]` and `q[1]`.

Wait, the prompt says: "Generate a reasoning section that explains... Output ONLY the reasoning section, starting with "## Reasoning". Do NOT include the isQ code... Be precise with state evolution using Dirac notation. Keep concise..."

Let's trace the state evolution:
Initial state: |00>
While loop applies Rx(pi/6) to q[0] three times.
Total rotation = pi/2.
State of q[0] after loop: cos(pi/4)|0> - i sin(pi/4)|1> = (1/sqrt(2))|0> - (i/sqrt(2))|1>
Next, H(q[0]) is applied.
State of q[0] after first H:
H [(1/sqrt(2))|0> - (i/sqrt(2))|1>] = (1/sqrt(2)) [ (1/sqrt(2))(|0> + |1>) ] - (i/sqrt(2)) [ (1/sqrt(2))(|0> - |1>) ]
= 0.5|0> + 0.5|1> - 0.5i|0> + 0.5i|1>
= (0.5 - 0.5i)|0> + (0.5 + 0.5i)|1>
Next, H(q[0]) is applied again. Since H^2 = I, the state goes back to (1/sqrt(2))|0> - (i/sqrt(2))|1>.
Wait, P(|0>) is |1/sqrt(2)|^2 = 0.5.
P(|1>) is |-i/sqrt(2)|^2 = 0.5.
So P(|0>) = 0.5, P(|1>) = 0.5.
Since q[1] is never touched, it remains |0>.
Thus, measurement probabilities: |00> with 0.5, |10> with 0.5.
Wait, let me double check the H-H pair reasoning.
The prompt mentions: "Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness."
The reasoning should mention this gate cancellation.

Let's structure the reasoning:
1. Goal: Implement an arithmetic-style circuit using a loop to apply rotations and demonstrate identity via H-H pair.
2. Qubits: 2 qubits `q[0]` and `q[1]`, both measured.
3. State evolution:
- Start at |00>.
- `while` loop applies `Rx(pi/6)` 3 times to `q[0]`, which is equivalent to `Rx(pi/2)`, evolving the state to `cos(pi/4)|0> - i sin(pi/4)|1>` on `q[0]` (so overall `(1/√2)|0> - (i/√2)|1>` times `|0>` for `q[1]`).
- The `H(q[0])` followed by `H(q[0])` demonstrates gate cancellation, acting as an identity operation and leaving the state unchanged as `(1/√2)(|0> - i|1>) |0>`.
4. Probabilities: The probability of `q[0]` being |0> is |1/√2|² = 0.5, and |1> is |-i/√2|² = 0.5. Since `q[1]` is |0>, the final measurement probabilities are P(|00>) = 0.5 and P(|10>) = 0.5.

Let's refine to ensure it fits within the length constraints (3-8 lines usually, up to 15 for complex. This is moderately complex, 6-8 lines is perfect).
Checking the gate matrices:
Rx(θ) = [[cos(θ/2), -i sin(θ/2)], [-i sin(θ/2), cos(θ/2)]]
So Rx(pi/2) applied to |0> gives cos(pi/4)|0> - i sin(pi/4)|1> = (1/√2)|0> - (i/√2)|1>.
Probability of |0> is (1/√2)*(1/√2)* = 0.5.
Probability of |1> is

## isqTrain/284

- task_id: `isqTrain/284`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_print`
- source: `isq_train_cot`
- dataset_index: `4780`

### Prompt

Help me write isQ code that implements the gate_decomposition pattern but with a different initial state preparation (flip q[[0, 2]] -> q[3]).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare the state |0001⟩ by flipping qubit 3, then measure all qubits.
2. **Qubits**: 4 qubits (q[0]-q[3]), all measured at the end.
3. **State evolution**:
   - Initial state: |0000⟩ (all qubits in |0⟩)
   - After `X(q[3])`: |0001⟩ (q[3] flipped to |1⟩)
4. **Expected probabilities**: The final state is |0001⟩ with certainty (probability 1.0). Measurement yields a=0, b=0, c=0, d=1, corresponding to bitstring 0001 (q[0] as highest bit, q[3] as lowest).

## isqTrain/1692

- task_id: `isqTrain/1692`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_for_loop`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4419`

### Prompt

Create an isQ quantum circuit that Use a for loop to apply a CNOT chain on 5 qubits starting from |10000>. Each qubit controls the next.

### Chain-of-thought reasoning

## Reasoning
- Goal: Implement a CNOT chain on 5 qubits to propagate the initial |1> state across all qubits.
- Qubits: 5 qubits (q[0] to q[4]), all measured.
- Evolution:
  - Initial state: |00000>
  - After X(q[0]): |10000>
  - After CNOT(q[0], q[1]): |11000>
  - After CNOT(q[1], q[2]): |11100>
  - After CNOT(q[2], q[3]): |11110>
  - After CNOT(q[3], q[4]): |11111>
- Expected probabilities: Because the final state is exactly |11111>, measuring all qubits yields 11111 with 100% probability.

## isqTrain/1916

- task_id: `isqTrain/1916`
- task_type: `output_prediction`
- category: `isq_control_flow`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3348`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[4];
procedure main() {
    for i in 0:4 {
        H(q[i]);
    }
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Input: An isQ quantum program applying `H` gates to 4 qubits `q[0]...q[3]`, followed by measurements.
    *   Output format: "## Circuit Analysis" section, concise step-by-step reasoning using Dirac notation, predicted probability distribution. Max 8-15 lines.
    *   Task: Predict measurement outcomes probability distribution.

2.  **Analyze the Circuit:**
    *   4 qubits initialized to $|0000\rangle$.
    *   Loop `for i in 0:4` applies `H` to `q[0]`, `q[1]`, `q[2]`, `q[3]`.
    *   State evolves from $|0000\rangle$ to $(|0\rangle + |1\rangle)/\sqrt{2} \otimes (|0\rangle + |1\rangle)/\sqrt{2} \otimes (|0\rangle + |1\rangle)/\sqrt{2} \otimes (|0\rangle + |1\rangle)/\sqrt{2}$.
    *   Expanded state: $\frac{1}{4} \sum_{x \in \{0,1\}^4} |x\rangle$.
    *   All 16 basis states have equal probability $(1/4)^2 = 1/16 = 0.0625$.

3.  **Draft the Circuit Analysis:**
    *   *Step 1: Initialization.* Start in $|0000\rangle$.
    *   *Step 2: H gates.* Apply $H$ to all 4 qubits.
    *   *Step 3: State evolution.* $|0000\rangle \xrightarrow{H^{\otimes 4}} |+++\rangle = \frac{1}{4}\sum_{x=0}^{15}|x\rangle$.
    *   *Step 4: Measurement.* Measure all qubits. Each of the $2^4 = 16$ outcomes has probability $|1/4|^2 = 0.0625$.
    *   *Step 5: Output format.* Provide the final dict.

4.  **Refine and Format:**
    *   Keep it concise and use Dirac notation.
    *   Ensure the "## Circuit Analysis" header is present.
    *   Ensure the final probability dictionary matches standard formatting (earlier measured qubit = higher bit, but wait, the isQ syntax is `M(q[0])` first, so `q[0]` is the highest bit. Wait, in isQ --probs output, "earlier measured qubit = higher bit". Thus `q[0]` is the MSB).

    *Let's check the dict keys:*
    0000, 0001, ..., 1111. Each maps to 0.0625.

5.  **Finalizing the text:**
    ## Circuit Analysis
    1.  **Initial State:** The 4-qubit system starts in the ground state $|0000\rangle$.
    2.  **Gate Applications:** The circuit applies a Hadamard gate ($H$) to each of the 4 qubits.
    3.  **State Evolution:** Applying $H^{\otimes 4}$ creates an equal superposition over all 16 possible computational basis states:
        $|0000\rangle \xrightarrow{H^{\otimes 4}} \frac{1}{\sqrt{2^4}} \sum_{x=0}^{15} |x\rangle = \frac{1}{4} (|0000\rangle + |0001\rangle + \dots + |1111\rangle)$.
    4.  **Probabilities:** Because the amplitude of each basis state is $1/4$, the probability of measuring any specific 4-bit string is $|1/4|^2 = 1/16 = 0.0625$.

    Predicted probability distribution: {'0000': 0.0625, '0001': 0.0625, '0010': 0.0625, '0011': 0.0625, '0100': 0.0625, '0101': 0.0625, '0110': 0.0625, '0111': 0.0625, '1000': 0.0625, '1001': 0.0625, '1010': 0.0625, '1011': 0.0625, '1100': 0.0625, '1101':

### Reference answer

{'predicted_probs': {'0000': 0.0625, '0001': 0.0625, '0010': 0.0625, '0011': 0.0625, '0100': 0.0625, '0101': 0.0625, '0110': 0.0625, '0111': 0.0625, '1000': 0.0625, '1001': 0.0625, '1010': 0.0625, '1011': 0.0625, '1100': 0.0625, '1101': 0.0625, '1110': 0.0625, '1111': 0.0625}, 'explanation': 'for loop.'}

## isqTrain/1709

- task_id: `isqTrain/1709`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `2269`

### Prompt

Write isQ code for the following quantum task: Prepare a 6-qubit GHZ state using a for loop for the CNOT gates.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Prepare a 6-qubit GHZ state, an equal superposition of all qubits in |0> and all in |1>.
2. **Qubits**: 6 qubits are used (q[0] to q[5]), and all 6 are measured.
3. **Evolution**:
   - Start in the ground state |000000>.
   - Apply H to q[0], creating the state (|000000> + |100000>) / √2.
   - The for loop applies CNOT(q[0], q[i]) for i from 1 to 5.
   - Because the control q[0] is in a superposition, the CNOTs propagate its state, generating entanglement across all target qubits: (|000000> + |110000>)/√2 -> ... -> (|000000> + |111111>) / √2.
4. **Probabilities**: The final state is an equal superposition of exactly two basis states. Thus, measuring all qubits yields |000000> with probability 0.5 and |111111> with probability 0.5.

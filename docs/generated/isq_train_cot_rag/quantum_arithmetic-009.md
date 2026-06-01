# ISQ training COT RAG corpus: quantum_arithmetic shard 9

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3690

- task_id: `isqTrain/3690`
- task_type: `code_generation`
- category: `quantum_arithmetic`
- difficulty: `difficult`
- concept_tags: `reversible_computing`, `ancilla_usage`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4233`

### Prompt

帮我写一个isQ程序：a quantum full adder for a=0, b=1, cin=0.
Use q[0]=a, q[1]=b, q[2]=cin, q[3]=sum, q[4]=carry-out.
Use Toffoli gates for AND, CNOT for XOR.
Measure all 5 qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement a quantum full adder computing sum and carry-out for inputs a=0, b=1, cin=0 using Toffoli and CNOT gates.
Five qubits are used: q[0] (a), q[1] (b), q[2] (cin), q[3] (sum), q[4] (carry-out). All are measured at the end.
1. Initial state: |00000⟩
2. X(q[1]): Sets b=1, state becomes |01000⟩
3. Toffoli(q[0], q[1], q[4]): Computes a AND b into carry-out; since a=0, q[4] stays 0: |01000⟩
4. CNOT(q[0], q[3]): XORs a into sum register (q[3]): |01000⟩
5. CNOT(q[1], q[3]): XORs b into sum register: |01010⟩ (q[3]=1)
6. Toffoli(q[3], q[2], q[4]): Computes (a XOR b) AND cin into carry-out; since cin=0, q[4] stays 0: |01010⟩
7. CNOT(q[2], q[3]): XORs cin into sum: |01010⟩
The final deterministic state |01010⟩ yields expected measurement probability 1.0 for outcome 01010, confirming 0+1+0=1 with carry-out 0.

## isqTrain/3707

- task_id: `isqTrain/3707`
- task_type: `code_generation`
- category: `quantum_arithmetic`
- difficulty: `expert`
- concept_tags: `reversible_computing`, `ancilla_usage`, `multi_controlled_logic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `5039`

### Prompt

Write an isQ program that a 2-bit quantum ripple-carry adder computing 3 + 0 = 3. Use registers a[2], b[2], c[3] where the sum appears in b[] (low bits) and c[0] (carry-out). Use Toffoli and CNOT gates for the ripple-carry logic. Measure all 7 qubits.

### Chain-of-thought reasoning

The user wants a 2-bit quantum ripple-carry adder computing 3 + 0 = 3.

Let me trace through this step by step:
- Registers: a[2], b[2], c[3]
- a encodes value A (3 in binary = 11, so a[0]=1, a[1]=1)
- b encodes value B (0 in binary = 00, so b[0]=0, b[1]=0)
- c is the carry chain

For a 2-bit ripple-carry adder:
- Bit 0 (LSB): a[1] + b[1] (half adder)
  - Toffoli(a[1], b[1], c[1]) - carry out
  - CNOT(a[1], b[1]) - sum
  
- Bit 1: a[0] + b[0] + c[1] (full adder)
  - Toffoli(a[0], b[0], c[0]) - partial carry
  - CNOT(a[0], b[0]) - partial sum
  - Toffoli(b[0], c[1], c[0]) - final carry
  - CNOT(c[1], b[0]) - final sum

Initial state: |a[1], a[0], b[1], b[0], c[2], c[1], c[0]> = |1100000>
After X(a[0]), X(a[1]): |1110000> wait no...

Let me be more careful. The qubits are:
- a[0], a[1] - input A
- b[0], b[1] - input B  
- c[0], c[1], c[2] - carry chain

Wait, I need to check the bit ordering. In the implementation:
- A = 3 means a[0] and a[1] are both set to 1
- B = 0 means b[0] and b[1] are both 0

The reference uses a[1] as the LSB of A and a[0] as the MSB. Let me verify:
- "Bit 0: half adder a[1] + b[1]"
- "Bit 1: full adder a[0] + b[0] + c[1]"

So a[1] is the LSB of A, a[0] is the MSB of A.

For 3 + 0:
- 3 in binary is 11, so a[0]=1 (MSB), a[1]=1 (LSB)
- 0 in binary is 00, so b[0]=0 (MSB), b[1]=0 (LSB)

Let me trace the state:
Initial: |0000000> (all 7 qubits)

After X(a[0]): a[0] flips to 1
After X(a[1]): a[1] flips to 1
State: |a[1]=1, a[0]=1, b[1]=0, b[0]=0, c[2]=0, c[1]=0, c[0]=0>

Hmm, but the order depends on how we arrange the qubits. Let me just track each qubit individually.

After initialization:
a = |11>, b = |00>, c = |000>

Bit 0 (half adder): a[1] + b[1] = 1 + 0
- Toffoli(a[1], b[1], c[1]): Since b[1]=0, this does nothing. c[1] stays |0>
- CNOT(a[1], b[1]): a[1]=1, so b[1] flips. b[1] becomes |1>

After bit 0: a = |11>, b = |01>, c = |000>
Sum bit 0 = b[1] = 1, carry c[1] = 0

Bit 1 (full adder): a[0] + b[0] + c[1] = 1 + 0 + 0
- Toffoli(a[0], b[0], c[0]): b[0]=0, so nothing. c[0] stays |0>
- CNOT(a[0], b[0]): a[0]=1, so b[0] flips. b[0] becomes |1>
- Toffoli(b[0], c[1], c[0]): c[1]=0, so nothing. c[0] stays |0>
- CNOT(c[1], b[0]): c[1]=0, so nothing. b[0] stays |1>

After

## isqTrain/4440

- task_id: `isqTrain/4440`
- task_type: `output_prediction`
- category: `quantum_arithmetic`
- difficulty: `difficult`
- concept_tags: `finite_field_arithmetic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5467`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;

qbit q[2];

procedure main() {
    // Input: element 3 = |11>
    X(q[0]);
    X(q[1]);
    // Inversion: map 3 -> 2
    // Flip q[1]: |11> -> |10>
    X(q[1]);
    // Result: |10> = element 2
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit starts with two qubits in the initial state |00>.
2. Applying `X(q[0])` flips the first qubit, changing the state to |10>.
3. Applying `X(q[1])` flips the second qubit, changing the state to |11>.
4. Applying `X(q[1])` again flips the second qubit back, changing the state to |10>.
5. Applying `X(q[0])` again flips the first qubit back, returning the system to the final state |00> before measurement.

Predicted probability distribution: {|00>: 1.0}

### Reference answer

{'predicted_probs': {'00': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 1.0000.'}

## isqTrain/4163

- task_id: `isqTrain/4163`
- task_type: `output_prediction`
- category: `quantum_arithmetic`
- difficulty: `difficult`
- concept_tags: `reversible_computing`, `ancilla_usage`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3272`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[5];

procedure main() {
    X(q[1]);
    X(q[2]);
    Toffoli(q[0], q[1], q[4]);
    CNOT(q[0], q[3]);
    CNOT(q[1], q[3]);
    Toffoli(q[3], q[2], q[4]);
    CNOT(q[2], q[3]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants to predict the measurement outcome of an isQ circuit. I need to provide a step-by-step analysis, explain the state evolution in Dirac notation, and conclude with the probability distribution.

2.  **Analyze the Circuit**:
    *   `qbit q[5];` -> Initial state: $|00000\rangle$ (q[0] to q[4])
    *   `X(q[1]); X(q[2]);` -> State: $|q_0 q_1 q_2 q_3 q_4\rangle = |01100\rangle$
    *   `Toffoli(q[0], q[1], q[4]);` -> q[0]=0, q[1]=1. Since q[0]=0, Toffoli does nothing. State: $|01100\rangle$
    *   `CNOT(q[0], q[3]);` -> q[0]=0. Does nothing. State: $|01100\rangle$
    *   `CNOT(q[1], q[3]);` -> q[1]=1. Flips q[3]. State: $|01110\rangle$
    *   `Toffoli(q[3], q[2], q[4]);` -> q[3]=1, q[2]=1. Both are 1. Flips q[4]. State: $|01111\rangle$
    *   `CNOT(q[2], q[3]);` -> q[2]=1. Flips q[3]. State: $|01101\rangle$

3.  **Final State Before Measurement**:
    *   $|01101\rangle$
    *   Qubit mapping: q[0]=0, q[1]=1, q[2]=1, q[3]=0, q[4]=1.

4.  **Calculate Measurement Outcome**:
    *   Measurements are `M(q[0])`, `M(q[1])`, `M(q[2])`, `M(q[3])`, `M(q[4])`.
    *   Outcomes: q[0]=0, q[1]=1, q[2]=1, q[3]=0, q[4]=1.
    *   Binary string: `01101` (assuming standard ordering, usually q[0] is the highest bit or vice versa depending on the specific isQ simulator output, but the prompt says "earlier measured qubit = higher bit", so q[0] is the MSB. Wait, let's verify standard isQ output. The instruction says: "--probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit)." Thus, q[0] is bit 4, q[1] is bit 3, ..., q[4] is bit 0. So `01101` -> binary 13.
    *   Probability distribution: 100% for `01101` (or 13).

5.  **Draft the Analysis (adhering to constraints)**:
    *   *Initial state*: $|q_4 q_3 q_2 q_1 q_0\rangle = |00000\rangle$
    *   *After X(q[1]), X(q[2])*: $|00100\rangle$ (using standard q_0 as right-most bit) -> wait, let's just write it as $|q_0 q_1 q_2 q_3 q_4\rangle = |01100\rangle$.
    *   *Toffoli(q[0], q[1], q[4])*: q[0]=0, so no change -> $|01100\rangle$.
    *   *CNOT(q[0], q[3])*: q[0]=0, so no change -> $|01100\rangle$.
    *   *CNOT(q[1], q[3])*: q[1]=1, flips q[3] -> $|01110\rangle$.
    *   *Toffoli(q[3], q[2], q[4])*: q[3]=1, q[2]=1. Flips q[4] -> $|01111\rangle$.
    *   *CNOT(q[2], q[3])*: q[2]=1, flips q[3] -> $|01101\rangle$.
    *   *Probability distribution*: 100% probability of measuring 01101 (13 in decimal). Qubits q[0..4] measure to 0, 1, 1, 0, 1 respectively.

6.  **Refine constraints

### Reference answer

Deterministic output: state |01101> with probability ~1.00

## isqTrain/4167

- task_id: `isqTrain/4167`
- task_type: `output_prediction`
- category: `quantum_arithmetic`
- difficulty: `difficult`
- concept_tags: `reversible_computing`, `ancilla_usage`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5390`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[5];

procedure main() {
    X(q[0]);
    X(q[1]);
    X(q[2]);
    Toffoli(q[0], q[1], q[4]);
    CNOT(q[0], q[3]);
    CNOT(q[1], q[3]);
    Toffoli(q[3], q[2], q[4]);
    CNOT(q[2], q[3]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise, precise step-by-step reasoning for the given isQ circuit, ending with the predicted measurement output and probability distribution.

2.  **Analyze the Circuit:**
    *   `qbit q[5]` -> Initial state: $|00000\rangle$ (q[0] to q[4])
    *   `X(q[0]); X(q[1]); X(q[2]);` -> State becomes $|11100\rangle$
    *   `Toffoli(q[0], q[1], q[4])` -> q[0]=1, q[1]=1, so flip q[4]. State becomes $|11101\rangle$
    *   `CNOT(q[0], q[3])` -> q[0]=1, so flip q[3]. State becomes $|11111\rangle$
    *   `CNOT(q[1], q[3])` -> q[1]=1, so flip q[3]. q[3] is 1, so it becomes 0. State becomes $|11101\rangle$
    *   `Toffoli(q[3], q[2], q[4])` -> q[3]=0, q[2]=1. Only one control is 1. q[4] remains 1. State is $|11101\rangle$
    *   `CNOT(q[2], q[3])` -> q[2]=1, so flip q[3]. q[3] becomes 1. State becomes $|11111\rangle$
    *   Measure all qubits.

3.  **Compute Final State:**
    *   The circuit is completely classical (no superposition).
    *   Final state is $|11111\rangle$.
    *   In binary string format for measurement (q[0] is highest bit if read out in order, wait, standard is lower index = higher bit? The prompt says "array indexed by measurement bitstring (earlier measured qubit = higher bit)". So `M(q[0]); M(q[1]); ... M(q[4])` gives bitstring `q[0] q[1] q[2] q[3] q[4]` which is 11111.

4.  **Draft the Explanation:**
    *   Initial state: $|00000\rangle$
    *   X gates on q[0], q[1], q[2] flip them to $|1\rangle$, yielding $|11100\rangle$.
    *   Toffoli(q[0], q[1], q[4]): both controls are 1, so target q[4] flips to 1 ($|11101\rangle$).
    *   CNOT(q[0], q[3]): q[0] is 1, q[3] flips to 1 ($|11111\rangle$).
    *   CNOT(q[1], q[3]): q[1] is 1, q[3] flips to 0 ($|11101\rangle$).
    *   Toffoli(q[3], q[2], q[4]): q[3] is 0, so target q[4] remains 1 ($|11101\rangle$).
    *   CNOT(q[2], q[3]): q[2] is 1, q[3] flips to 1 ($|11111\rangle$).
    *   Measurement output: 11111 with probability 1.

5.  **Refine for constraints:** "Be concise: 3-8 lines for simple circuits... Output ONLY the analysis, starting with '## Circuit Analysis'... End with the predicted probability distribution".

6.  **Final Polish:**
    ## Circuit Analysis
    - Initial state: $|00000\rangle$. X gates on q[0], q[1], and q[2] change the state to $|11100\rangle$.
    - Toffoli(q[0], q[1], q[4]) flips q[4] to $|1\rangle$ since q[0] and q[1] are $|1\rangle$, yielding $|11101\rangle$.
    - CNOT(q[0], q[3]) flips q[3] to $|1\rangle$, changing the state to $|11111\rangle$.
    - CNOT(q[1], q[3]) flips q[3] back to $|0\rangle$, resulting in $|11101\rangle$.
    - Toffoli(q[3], q[2], q[4]) leaves q[4] unchanged because q[3] is $|0\rangle$, so state remains $|111

### Reference answer

Deterministic output: state |11111> with probability ~1.00

# ISQ training COT RAG corpus: isq_control_flow shard 2

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/258

- task_id: `isqTrain/258`
- task_type: `output_prediction`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1588`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;

qbit q[4];

procedure main() {
    for i in 0:4 {
        Ry(pi/4.0, q[i]);
    }
    for i in 0:3 {
        CNOT(q[i], q[i+1]);
    }
    for i in 0:4 {
        Rz(pi/3.0, q[i]);
    }
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

The user wants to analyze an isQ program and predict its measurement probability distribution.
The program applies gates to a 4-qubit register `q[0..3]`.

Let's trace the circuit:
1. `Ry(pi/4.0, q[i])` for all i in 0:4.
Wait, isQ `for i in 0:4` includes 4? Yes, range is 0, 1, 2, 3, 4? No, wait. `0:4` usually means 0, 1, 2, 3 in isQ (upper bound is exclusive). Wait, is it inclusive or exclusive?
Let me check The implementation. It has 4 qubits, so `0:4` means 0, 1, 2, 3.
Wait! `qbit q[4];` implies 4 qubits. `for i in 0:4` iterates over 0, 1, 2, 3.
Let's assume `0:4` means i = 0, 1, 2, 3.
Wait! "for i in 0:3" means i = 0, 1, 2.
Let's list the operations:
- Ry(pi/4) on q[0], q[1], q[2], q[3].
State after Ry(pi/4) on |0> is cos(pi/8)|0> + sin(pi/8)|1>.
Let c = cos(pi/8), s = sin(pi/8).
c ≈ 0.92388, s ≈ 0.38268.
Since they are independent, the state is (c|0> + s|1>)^{\otimes 4}.

2. CNOT(q[i], q[i+1]) for i in 0:3. So i=0,1,2.
Wait, CNOT(0,1), CNOT(1,2), CNOT(2,3).
This is a sequence of CNOTs.
Let's apply them to the product state:
(c|0> + s|1>)_0 (c|0> + s|1>)_1 (c|0> + s|1>)_2 (c|0> + s|1>)_3
= c^4 |0000> + c^3 s |0001> + ... + s^4 |1111>

Wait, let's apply CNOT(0,1) to (c|0> + s|1>)_0 (c|0> + s|1>)_1:
c|0>(c|0>+s|1>) + s|1>(c|1>+s|0>) = c^2|00> + cs|01> + sc|11> + s^2|10>.

Let's trace this completely.
Actually, the CNOT cascade entangles the qubits.
Let the initial state be \sum_{x \in \{0,1\}^4} c^{4-wt(x)} s^{wt(x)} |x>
where wt(x) is the Hamming weight.
When we apply CNOT(i, i+1), it XORs bit i+1 with bit i.
Let's apply CNOT(0,1), then CNOT(1,2), then CNOT(2,3).
Let's denote the initial bits as x_0, x_1, x_2, x_3.
CNOT(0,1) maps x_1 -> x_1 \oplus x_0.
Then CNOT(1,2) maps x_2 -> x_2 \oplus x_1 \oplus x_0.
Then CNOT(2,3) maps x_3 -> x_3 \oplus x_2 \oplus x_1 \oplus x_0.
Let y_0 = x_0
Let y_1 = x_1 \oplus x_0
Let y_2 = x_2 \oplus x_1 \oplus x_0
Let y_3 = x_3 \oplus x_2 \oplus x_1 \oplus x_0
The basis states transform as |x_0 x_1 x_2 x_3> -> |y_0 y_1 y_2 y_3>
But the coefficients remain the same, just re-ordered.
So the state is \sum_{y \in \{0,1\}^4} c^{4 - wt(x(y))} s^{wt(x(y))} |y>
where x_0 = y_0
x_1 = y_0 \oplus y_1
x_2 = y_0 \oplus y_1 \opl

### Reference answer

{'predicted_probs': {'0': 0.5307900429449554, '1': 0.09106917382415923, '2': 0.015625000000000003, '3': 0.09106917382415923, '4': 0.015625000000000003, '5': 0.0026808261758407806, '6': 0.015625000000000003, '7': 0.09106917382415923, '8': 0.015625000000000003, '9': 0.0026808261758407806, '11': 0.0026808261758407806, '12': 0.01562500000000001, '13': 0.0026808261758407806, '14': 0.015625000000000003, '15': 0.09106917382415923}, 'explanation': 'Parametric variant of isqHumanEval/87. Dimension: predict probabilities for reference circuit.'}

## isqTrain/251

- task_id: `isqTrain/251`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_while_loop`
- source: `isq_train_cot`
- dataset_index: `192`

### Prompt

Write an isQ program that implements the arithmetic_circuit pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Implement an arithmetic circuit using a counted while loop to apply iterative Rx rotations, demonstrate gate cancellation with an X-X identity pair, and measure the result.

**Qubits:** 2 qubits (q[0], q[1]), both measured.

**State evolution:**
1. Initial state: |00⟩
2. While loop applies Rx(π/6) to q[0] three times, composing to Rx(π/2): |00⟩ → cos(π/4)|00⟩ - i·sin(π/4)|10⟩ = (|00⟩ - i|10⟩)/√2
3. First X(q[0]) flips q[0]: (|10⟩ - i|00⟩)/√2
4. Second X(q[0]) cancels the first (identity pair): (|00⟩ - i|10⟩)/√2 — state restored
5. q[1] remains |0⟩ throughout (no gates applied)

**Expected probabilities:** P(|00⟩) = |1/√2|² = 0.5, P(|10⟩) = |-i/√2|² = 0.5. The X-X pair demonstrates gate cancellation awareness—it leaves the post-loop state unchanged.

## isqTrain/1694

- task_id: `isqTrain/1694`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_for_loop`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5762`

### Prompt

I need an isQ program to Use a for loop to apply a CNOT chain on 6 qubits starting from |100000>. Each qubit controls the next.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Propagate a |1⟩ state through a 6-qubit CNOT chain starting from |100000⟩.
2. **Qubits**: 6 qubits (q[0]–q[5]), all measured.
3. **State evolution**: Initial |000000⟩ → X(q[0]) → |100000⟩ → CNOT(q[0],q[1]) → |110000⟩ → CNOT(q[1],q[2]) → |111000⟩ → CNOT(q[2],q[3]) → |111100⟩ → CNOT(q[3],q[4]) → |111110⟩ → CNOT(q[4],q[5]) → |111111⟩.
4. Each CNOT flips the target when the control is |1⟩, so the |1⟩ propagates sequentially through all qubits.
5. Final state |111111⟩ yields measurement probability {|111111⟩: 1.0}.

## isqTrain/535

- task_id: `isqTrain/535`
- task_type: `output_prediction`
- category: `isq_control_flow`
- difficulty: `expert`
- concept_tags: `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4753`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;

oracle A(4,1) = [0,1,1,0,0,0,0,0,0,0,1,1,0,1,0,1];
oracle g(2,1) = [0,1,1,0]; 

int a;
qbit q[4], p[3];

procedure hadamard_layer(int k){
    H(q[2*k]);
    H(q[2*k+1]);
}

procedure recursive_fourier_sampling(int k){
    if (k == 2){
        A(q[0], q[1], q[2], q[3], p[2]);
    }else{
        hadamard_layer(k);
        X(p[k+1]);
        H(p[k+1]);

        recursive_fourier_sampling(k+1);

        hadamard_layer(k);
        g(q[2*k],q[2*k+1], p[k]);
        hadamard_layer(k);

        recursive_fourier_sampling(k+1);

        hadamard_layer(k);
        H(p[k+1]);
        X(p[k+1]);
    }
}

procedure main(){
    a = 0;
    recursive_fourier_sampling(a);
    int g = M(p[0]);    
    print g;
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants an analysis of a specific isQ program, which is an implementation of Recursive Fourier Sampling. I need to predict the probability distribution of measuring qubit `p[0]`, provide a step-by-step reasoning using Dirac notation, and state the final probability distribution.

2.  **Analyze the Circuit (Recursive Fourier Sampling):**
    *   **Inputs:** `q` (4 qubits), `p` (3 qubits). All initialized to $|0\rangle$.
    *   **`oracle A`**: 4-to-1 oracle. $A[0,1,1,0,0,0,0,0,0,0,1,1,0,1,0,1]$. This acts on `q[0], q[1], q[2], q[3]` and `p[2]`. It's a controlled phase or an X gate on `p[2]` based on the input. Wait, standard oracles in isQ of arity $(n,1)$ map $|x\rangle|y\rangle \to |x\rangle|y \oplus f(x)\rangle$. The array `[0,1,1,0,0,0,0,0,0,0,1,1,0,1,0,1]` indicates $f(x)$. $f(1)=1, f(2)=1, f(10)=1, f(11)=1, f(13)=1, f(15)=1$. Wait, the array is 16 elements. $f(0001)=1$, $f(0010)=1$, $f(1010)=1$, $f(1011)=1$, $f(1101)=1$, $f(1111)=1$.
    *   **`oracle g`**: 2-to-1 oracle. `g[0,1,1,0]`. $f_g(01)=1, f_g(10)=1$. (XOR function).
    *   **`recursive_fourier_sampling(k)`**:
        *   `k=0`:
            *   `hadamard_layer(0)`: `H(q[0])`, `H(q[1])`. State of `q[0..1]` is $|+\rangle|+\rangle$.
            *   `X(p[1])`, `H(p[1])`. State of `p[1]` is $|-\rangle$.
            *   Call `recursive_fourier_sampling(1)`.
            *   `hadamard_layer(0)`: `H(q[0])`, `H(q[1])`.
            *   `g(q[0], q[1], p[0])`: Applies oracle `g`.
            *   `hadamard_layer(0)`: `H(q[0])`, `H(q[1])`.
            *   Call `recursive_fourier_sampling(1)`.
            *   `hadamard_layer(0)`: `H(q[0])`, `H(q[1])`.
            *   `H(p[1])`, `X(p[1])`.
        *   `k=1`:
            *   `hadamard_layer(1)`: `H(q[2])`, `H(q[3])`.
            *   `X(p[2])`, `H(p[2])`. State of `p[2]` is $|-\rangle$.
            *   Call `recursive_fourier_sampling(2)`.
            *   `hadamard_layer(1)`: `H(q[2])`, `H(q[3])`.
            *   `g(q[2], q[3], p[1])`: Oracle `g`.
            *   `hadamard_layer(1)`: `H(q[2])`, `H(q[3])`.
            *   Call `recursive_fourier_sampling(2)`.
            *   `hadamard_layer(1)`: `H(q[2])`, `H(q[3])`.
            *   `H(p[2])`, `X(p[2])`.
        *   `k=2`:
            *   `A(q[0], q[1], q[2], q[3], p[2])`.
    *   Wait, let's trace the exact state evolution. This is a specific query for a specific hidden shift or function.
    *   Actually, the program implements the Recursive Fourier Sampling algorithm. The structure of this algorithm guarantees that measuring `p[0]` yields a deterministic bit related to the recursive problem.
    *   Since it's a specific instance, let's see what The predicted output: `Expected measurement probabilities: {|1>: 1.0}`.

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/162. Dimension: predict probabilities for reference circuit.'}

## isqTrain/242

- task_id: `isqTrain/242`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4443`

### Prompt

Implement a quantum circuit in isQ: implements the ghz_state_preparation pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
**Goal**: Prepare a 4-qubit GHZ state (|0000⟩+|1111⟩)/√2, demonstrating H-H identity cancellation.

**Qubits**: 4 qubits declared (q[0]-q[3]), all measured.

**State evolution**:
1. |0000⟩ → H(q[0]) → (|0000⟩+|1000⟩)/√2
2. CNOT(q[0],q[1]) → (|0000⟩+|1100⟩)/√2
3. CNOT(q[1],q[2]) → (|0000⟩+|1110⟩)/√2
4. CNOT(q[2],q[3]) → (|0000⟩+|1111⟩)/√2 = GHZ state
5. H(q[0]) transforms to (|0000⟩+|1000⟩+|0111⟩-|1111⟩)/2
6. H(q[0]) again: H·H=I, cancels → returns to (|0000⟩+|1111⟩)/√2

**Probabilities**: The final GHZ state has equal amplitude 1/√2 for |0000⟩ and |1111⟩, yielding P(|0000⟩)=0.5 and P(|1111⟩)=0.5.

## isqTrain/1742

- task_id: `isqTrain/1742`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `basic`
- concept_tags: `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4637`

### Prompt

Create an isQ quantum circuit that Use a for loop from 2 to 6 (exclusive) applying X each iteration. 4 iterations means X^4.

### Chain-of-thought reasoning

## Reasoning
The goal is to apply the X gate four times to a single qubit using a for loop.
One qubit is needed, initialized to |0>, and it is the only qubit measured.
The loop runs for values 2, 3, 4, and 5, applying X each time: |0> → |1> → |0> → |1> → |0>.
Since X^4 is equivalent to the Identity operation, the qubit returns to its initial state.
Therefore, the final state is |0>, resulting in a 100% measurement probability for |0>.

## isqTrain/249

- task_id: `isqTrain/249`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_while_loop`
- source: `isq_train_cot`
- dataset_index: `2774`

### Prompt

Write an isQ program that implements a variant of the arithmetic_circuit pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement an arithmetic-style circuit using a counted while loop to apply cumulative Rx rotations on q[0], with qubits q[1]-q[3] left idle in the ground state.
2. **Qubits**: 4-qubit register (q[0]–q[3]); all are measured but only q[0] undergoes operations.
3. **State evolution**:
   - Initialize: |ψ⟩ = |0000⟩
   - Each loop iteration applies Rx(π/6) to q[0]; after 3 iterations, total rotation = Rx(π/2)
   - Rx(π/2)|0⟩ = cos(π/4)|0⟩ − i·sin(π/4)|1⟩ = (1/√2)(|0⟩ − i|1⟩)
   - Final state: |ψ⟩ = (1/√2)(|0000⟩ − i|1000⟩)
4. **Measurement probabilities**: |⟨0000|ψ⟩|² = 0.5, |⟨1000|ψ⟩|² = 0.5; qubits q[1], q[2], q[3] remain |0⟩ with certainty, yielding P(|0000⟩) = 0.5 and P(|1000⟩) = 0.5.

## isqTrain/1738

- task_id: `isqTrain/1738`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `basic`
- concept_tags: `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `5730`

### Prompt

Write isQ code for the following quantum task: Use a for loop from 0 to 2 (exclusive) applying X each iteration. 2 iterations means X^2.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply the X gate twice to a single qubit using a for loop with 2 iterations.
2. **Qubits**: 1 qubit (`q[0]`), which is measured.
3. **State evolution**:
   - Initialize: `|0>`
   - Iteration 0 (`X`): `|0>` → `|1>` (X flips the qubit)
   - Iteration 1 (`X`): `|1>` → `|0>` (X flips the qubit back)
4. **Expected probabilities**: Since X² = I (identity), two consecutive X gates return the qubit to `|0>`. Thus, P(`|0>`) = 1.0.

## isqTrain/1708

- task_id: `isqTrain/1708`
- task_type: `code_generation`
- category: `isq_control_flow`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4679`

### Prompt

Code this in isQ: Prepare a 5-qubit GHZ state using a for loop for the CNOT gates.

### Chain-of-thought reasoning

We are asked to generate reasoning for a 5-qubit GHZ state preparation using a for loop for CNOT gates. The implementation is given, but we need to produce only the reasoning section, not the code. The reasoning should be concise, precise, step-by-step, using Dirac notation. It should explain the goal, number of qubits, state evolution, and why expected probabilities follow.

We must follow the rules: output ONLY the reasoning section starting with "## Reasoning". No code blocks. Concise: 3-8 lines for simple circuits, up to 15 for complex ones.

The circuit is simple: 5 qubits. Initialize all |0>. Apply H to q[0] -> (|0>+|1>)/√2 on q0, others |0>. Then for i=1 to 4 (since loop is 1:5 exclusive? Actually isQ loop: for i in 1:5 { ... } meaning i=1,2,3,4? Actually typical isQ syntax: for i in a:b { ... } includes both ends? The circuit should for i in 1:5 { CNOT(q[0], q[i]); }. Since q has indices 0..4, that would try to access q[5] out of bounds. Wait, q[5] is declared qbit q[5]; indices 0-4. So loop should be i from 1 to 4 inclusive. The reference says for i in 1:5, maybe they treat as 1 to 4? Actually in isQ, the range a:b includes a and b? The reference is probably correct for their syntax: for i in 1:5 { ... } would iterate i=1,2,3,4? Or i=1,2,3,4,5? Usually in Python-like range, 1:5 would be 1..4 inclusive? But they wrote "for i in 1:5". We need to produce reasoning, not code. The expected state is a GHZ state: (|00000>+|11111>)/√2. So the CNOTs should entangle q0 with all others. So loop should apply CNOT(q0, qi) for i=1,2,3,4. So the final state is as expected.

We need to write reasoning.

Goal: Prepare a 5-qubit GHZ state (|00000>+|11111>)/√2.

Number of qubits: 5, all measured.

State evolution:
- Initial: |0>^5
- After H on q0: (|0>+|1>)/√2 ⊗ |0000> = (|00000>+|10000>)/√2 (but careful ordering: q0 is first, then q1,q2,q3,q4? In notation, we can write as |0> for all qubits; after H on q0 we get (|0>+|1>)/√2 on q0, others remain |0>. So state: (|00000>+|10000>)/√2. However typical bit ordering: earlier measured qubit = higher bit. But for state evolution we can just list qubits in order q0...q4.
- Then apply CNOT(q0, q1): flips q1 if q0=1. So state becomes (|00000>+|11000>)/√2.
- Then CNOT(q0, q2): (|00000>+|11100>)/√2.
- Then CNOT(q0, q3): (|00000>+|11110>)/√2.
- Then CNOT(q0, q4): (|00000>+|11111>)/√2.

Thus final state is 5-qubit GHZ.

Measurements: each qubit measured yields 0 or 1. Since state is equal superposition of all zeros and all ones, measurement outcomes are either 00000 or 11111 with equal probability 0.5 each. All other bitstrings have zero probability.

So reasoning should include these steps.

We need to keep concise, maybe 6-8 lines. Let's write.

## Reasoning
- Goal: Prepare a 5-qubit GHZ state (|00000>+|11111>)/√2.
- Qubits: 5 (q[0]...q[4]), all measured.
- Evolution: Start |0>^5.
  - H(q0) -> (|0>+|1>)/√2 ⊗ |0>^4 = (|00000>+|10000>)/√2.
  - CNOT(q0,q1) -> (|00000>+|11000>)/√2.
  - CNOT(q0,q2) -> (|00000>+|11100>)/√2.
  -

## isqTrain/238

- task_id: `isqTrain/238`
- task_type: `output_prediction`
- category: `isq_control_flow`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3364`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

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

## Circuit Analysis
1. Initial state of the 4 qubits is |0000>.
2. The `for` loop applies a Hadamard (H) gate to each qubit.
3. Each H gate puts its respective qubit into an equal superposition, |+> = (|0> + |1>) / sqrt(2).
4. The joint 4-qubit state becomes a uniform superposition of all 16 possible basis states: (1/4) * sum_{x=0}^{15} |x>.
5. Because the amplitudes of all 16 states are equal (1/4), the probability of measuring any specific state is (1/4)^2 = 1/16.

Predicted probability distribution: {|0000>: 0.0625, |0001>: 0.0625, |0010>: 0.0625, |0011>: 0.0625, |0100>: 0.0625, |0101>: 0.0625, |0110>: 0.0625, |0111>: 0.0625, |1000>: 0.0625, |1001>: 0.0625, |1010>: 0.0625, |1011>: 0.0625, |1100>: 0.0625, |1101>: 0.0625, |1110>: 0.0625, |1111>: 0.0625}

### Reference answer

{'predicted_probs': {'0': 0.06250000000000001, '1': 0.06250000000000001, '2': 0.06250000000000001, '3': 0.06250000000000001, '4': 0.06250000000000001, '5': 0.06250000000000001, '6': 0.06250000000000001, '7': 0.06250000000000001, '8': 0.06250000000000001, '9': 0.06250000000000001, '10': 0.06250000000000001, '11': 0.06250000000000001, '12': 0.06250000000000001, '13': 0.06250000000000001, '14': 0.06250000000000001, '15': 0.06250000000000001}, 'explanation': 'Parametric variant of isqHumanEval/83. Dimension: predict probabilities for reference circuit.'}

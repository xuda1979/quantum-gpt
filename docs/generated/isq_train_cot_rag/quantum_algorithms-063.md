# ISQ training COT RAG corpus: quantum_algorithms shard 63

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/847

- task_id: `isqTrain/847`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `finite_field_arithmetic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1630`

### Prompt

实现以下量子计算任务（使用isQ）：implements a variant of the finite_field_inversion pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement GF(2) multiplicative inversion (where 1⁻¹ = 1) using a 4-qubit register, with extra qubits idle in |0⟩.
2. **Qubits/Measurements**: 4 qubits (q[0]–q[3]); measure q[1], q[2], q[3] (3 measured bits).
3. **State evolution**:
   - Initial: |0000⟩
   - X(q[0]) → |1000⟩ (set input to 1, the only invertible element in GF(2))
   - CNOT(q[0], q[1]) → |1100⟩ (copy input to inverse register; GF(2) inversion of 1 is 1)
   - q[2], q[3] remain untouched in |0⟩
4. **Final state**: |1100⟩, so measuring q[1]=1, q[2]=0, q[3]=0 yields bitstring |100⟩ with probability 1.0.

## isqTrain/2020

- task_id: `isqTrain/2020`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `finite_field_arithmetic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `652`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[2];
procedure main() {
    X(q[0]);
    CNOT(q[0], q[1]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes two qubits, q[0] and q[1], to the state |00⟩.
2. The X gate is applied to q[0], flipping its state from |0⟩ to |1⟩. The system state becomes |10⟩.
3. The CNOT gate is applied with q[0] as the control and q[1] as the target. Since q[0] is in the |1⟩ state, q[1] is flipped from |0⟩ to |1⟩. The system evolves to the entangled state |11⟩.
4. Finally, q[1] is measured. Because q[1] is deterministically in the |1⟩ state, the measurement outcome is guaranteed to be 1.

Predicted probability distribution: {'1': 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'GF(2) inversion: 1^(-1)=1, result=1 with P=1.0.'}

## isqTrain/4545

- task_id: `isqTrain/4545`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4510`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[3];

procedure main() {
    
    H(q[0]);
    H(q[1]);
    
    CNOT(q[1], q[2]);
    
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants an analysis of an isQ quantum program to predict its measurement probability distribution. The output must be concise, use Dirac notation, and start with "## Circuit Analysis". It should list operations, trace the state evolution, and end with the predicted probability distribution.

2.  **Analyze the Code:**
    *   3 qubits initialized to $|000\rangle$.
    *   `H(q[0])`: Applies Hadamard to q[0]. State: $|+\rangle|00\rangle = \frac{1}{\sqrt{2}}(|000\rangle + |100\rangle)$.
    *   `H(q[1])`: Applies Hadamard to q[1]. State: $|+\rangle|+\rangle|0\rangle = \frac{1}{2}(|000\rangle + |010\rangle + |100\rangle + |110\rangle)$.
    *   `CNOT(q[1], q[2])`: Control q[1], target q[2]. Flips q[2] when q[1] is 1. State: $\frac{1}{2}(|000\rangle + |011\rangle + |100\rangle + |111\rangle)$. Note: this entangles q[1] and q[2], leaving q[0] independent.
    *   `H(q[0]); Z(q[0]); H(q[0]);`: Equivalent to $HZH = X$ on q[0]. This flips q[0] ($|0\rangle \to |1\rangle, |1\rangle \to |0\rangle$).
    *   Let's trace $X$ on q[0] applied to $\frac{1}{2}(|000\rangle + |011\rangle + |100\rangle + |111\rangle)$:
        *   $|000\rangle \to |100\rangle$
        *   $|011\rangle \to |111\rangle$
        *   $|100\rangle \to |000\rangle$
        *   $|111\rangle \to |011\rangle$
    *   Final state: $\frac{1}{2}(|100\rangle + |111\rangle + |000\rangle + |011\rangle) = \frac{1}{2}(|000\rangle + |011\rangle + |100\rangle + |111\rangle)$. (Wait, the X gate just swapped the terms, the sum is the same!).
    *   Let's double check.
        Initial: $|000\rangle$
        H(q0): $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |00\rangle$
        H(q1): $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle) \otimes |0\rangle$
        CNOT(1,2): $\frac{1}{2}(|000\rangle + |011\rangle + |100\rangle + |111\rangle)$
        HZH on q0: $X$ on q0.
        $X_0 \frac{1}{2}(|000\rangle + |011\rangle + |100\rangle + |111\rangle) = \frac{1}{2}(|100\rangle + |111\rangle + |000\rangle + |011\rangle)$. Correct, the superposition has exactly the same basis vectors, just re-ordered.
    *   `M(q[2])`: Measures q[2].
    *   Wait, the prompt asks for the probability distribution of measurement outcomes. Usually, `M(q[2])` collapses the state, but the prompt says "Expected measurement probabilities: {|000>: 0.5, |001>: 0.5}" (Wait, The implementation in the prompt says `{|000>: 0.5, |001>: 0.5}`, but let's look at the bitstring indexing).
    *   Wait! Look at the bitstring indexing in the prompt: "Expected measurement probabilities: {|000>: 0.5, |001>: 0.5}"
    *   Let's re-read the isQ syntax: "--probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit)."
    *   Ah! The final measurement only measures `q[2]`. It returns 0 or 1.
    *   Wait, `M(q[2])` measures only `q[2]`.
    *   BUT the prompt reference says `Expected measurement probabilities: {|000>: 0.5, |001>: 0.5}` and `Number of qubits measured:

### Reference answer

{'predicted_probs': {'000': 0.5, '001': 0.5}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.5000, P(|001>) = 0.5000.'}

## isqTrain/3055

- task_id: `isqTrain/3055`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_multi_register`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `1728`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```isq
import std;
qbit q[3];
// Initialize to |010>
procedure main() {
    X(q[1]);
    M(q[0]);
    M(q[1]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: The third measurement `M(q[0])` measures q[0] again instead of q[2]. Since the array has 3 qubits and the intent is to measure all three, this is a wrong qubit index.
2. **Fix**: Change `M(q[0])` → `M(q[2])` on the last measurement line.
3. **State evolution**: Initial state |000⟩ → X(q[1]) → |010⟩. Measuring q[0]=0, q[1]=1, q[2]=0 confirms the |010⟩ state with probability 1.0.

## isqExpand/algo/82

- task_id: `isqExpand/algo/82`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `grover`, `multi_solution`, `amplitude_amplification`, `oracle`
- source: `isq_expansion`
- dataset_index: `1918`

### Prompt

请用isQ语言编写一个量子电路：implementing Grover's algorithm on 3 qubits with two marked states: |010> and |101>. Apply one iteration. With M=2 solutions out of N=8, a single iteration achieves perfect amplification (total probability 1.0 on the two marked states, 0.5 each).

### Chain-of-thought reasoning

## 推理
目标：3比特Grover搜索|010>和|101>。

### Oracle
1. 标记|010> (q0=0,q1=1,q2=0): X(q[0]); X(q[2]); CCZ; X(q[0]); X(q[2]);
2. 标记|101> (q0=1,q1=0,q2=1): X(q[1]); CCZ; X(q[1]);

注意|010>和|101>互为比特翻转（补码关系），但oracle需要分别标记。

### 概率
N=8, M=2: theta = arcsin(1/2) = pi/6
1次迭代: sin^2(3*pi/6) = sin^2(pi/2) = 1.0
|010>(index 2) = 0.5, |101>(index 5) = 0.5, 其余 = 0.0

## isqTrain/3938

- task_id: `isqTrain/3938`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2033`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```
import std;
// QAOA MaxCut p=1 on 4-node path graph
// gamma=0.500, beta=0.500
qbit q[4];

procedure main() {
    // Superposition
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    // Cost unitary
    // Edge (0,1)
    CNOT(q[0], q[1]);
    Rz(2.0 * 2.0 * 0.500, q[1]);
    CNOT(q[0], q[1]);
    // Edge (1,2)
    CNOT(q[1], q[2]);
    Rz(2.0 * 0.500, q[2]);
    CNOT(q[1], q[2]);
    // Edge (2,3)
    CNOT(q[2], q[3]);
    Rz(2.0 * 0.500, q[3]);
    CNOT(q[2], q[3]);
    // Mixer
    Rx(2.0 * 0.500, q[0]);
    Rx(2.0 * 0.500, q[1]);
    Rx(2.0 * 0.500, q[2]);
    Rx(2.0 * 0.500, q[3]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug location**: The `Rz` gate for Edge (0,1) in the cost unitary has an extra `2.0` multiplier:
   - Buggy: `Rz(2.0 * 2.0 * 0.500, q[1])` → rotation angle = 2.0
   - Correct: `Rz(2.0 * 0.500, q[1])` → rotation angle = 1.0

2. **Fix**: Remove the extra `2.0` so all three edges get the same rotation `Rz(2*γ) = Rz(1.0)`.

3. **Corrected circuit state evolution** (γ=0.5, β=0.5):
   - **Initialization**: |0000⟩
   - **Hadamards**: |++++⟩ (uniform superposition)
   - **Cost unitary** (CNOT-Rz(1.0)-CNOT per edge): Each edge applies a controlled-Z rotation exp(-iγZ_iZ_j). The three edges (0,1), (1,2), (2,3) each contribute phase factors creating entanglement. Bitstrings with cuts on more edges accumulate different phases.
   - **Mixer** (Rx(1.0) on each qubit): Rotates each qubit around X-axis by 2β = 1.0 rad, mixing computational basis states.
   - **Result**: Non-uniform distribution peaked at |0000⟩ and |1111⟩ (~22.4% each), with symmetric structure reflecting the path graph topology and MaxCut structure (e.g., |0011⟩ and |1100⟩ at ~10.5% correspond to optimal cuts).

## isqTrain/3061

- task_id: `isqTrain/3061`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_multi_register`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `5359`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```isq
import std;
qbit q[3];
// Initialize to |101>
procedure main() {
    X(q[0]);
    X(q[2]);
    M(q[0]);
    M(q[0]);
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The second measurement `M(q[0])` measures qubit q[0] again instead of measuring q[1]. This means q[1] is never measured, and q[0] is measured twice, which doesn't match the intended state verification for |101⟩.

2. **Fix**: Change the second `M(q[0])` to `M(q[1])` so that all three qubits (q[0], q[1], q[2]) are measured exactly once.

3. **State evolution of corrected circuit**:
   - Initial state: |000⟩
   - After X(q[0]): |100⟩
   - After X(q[2]): |101⟩
   - Measurements: M(q[0])→1, M(q[1])→0, M(q[2])→1
   - Result confirms state |101⟩ with probability 1.0

## isqTrain/2672

- task_id: `isqTrain/2672`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `30`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[2];

procedure main(){
    H(q[0]);
    ctrl X(q[0],q[1]);

    int a = M(q[0]);
    int b = M(q[1]);
    print a - b;
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Gates applied**: `H(q[0])`, `CNOT(q[0], q[1])` (via `ctrl X`)
2. **State evolution**:
   - Initial: |00>
   - `H(q[0])`: (|00> + |10>)/√2
   - `CNOT(q[0], q[1])`: (|00> + |11>)/√2
3. **Final state**: (|00> + |11>)/√2 (Bell state)
4. **Probabilities**: Equal probability of measuring both qubits in the same state (correlated qubits).

Predicted probability distribution: [0.5, 0.0, 0.0, 0.5]

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/2007

- task_id: `isqTrain/2007`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`, `phase_manipulation`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `1842`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[2];
procedure main() {
    X(q[0]);
    H(q[1]);
    ctrl S(q[0], q[1]);
    H(q[0]);
    Rz(3.14159265358979, q[0]);
    Rz(1.57079632679490, q[1]);
    H(q[0]);
    ctrl inv S(q[0], q[1]);
    H(q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

Initial state: |00⟩

1. X(q[0]): |00⟩ → |10⟩

2. H(q[1]): |10⟩ → (|10⟩ + |11⟩)/√2 = |1⟩⊗(|0⟩ + |1⟩)/√2

3. ctrl S(q[0], q[1]): When q[0]=|1⟩, apply S to q[1]. S|0⟩ = |0⟩, S|1⟩ = i|1⟩
   → |1⟩⊗(|0⟩ + i|1⟩)/√2

4. H(q[0]): → (|0⟩ + |1⟩)/√2 ⊗ (|0⟩ + i|1⟩)/√2

5. Rz(π, q[0]): Rz(π)|0⟩ = -i|0⟩... wait, let me be more careful.

Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]

Rz(π, q[0]): |0⟩ → e^{-iπ/2}|0⟩ = -i|0⟩, |1⟩ → e^{iπ/2}|1⟩ = i|1⟩

So the state becomes: (−i|0⟩ + i|1⟩)/√2 ⊗ (|0⟩ + i|1⟩)/√2

6. Rz(π/2, q[1]): |0⟩ → e^{-iπ/4}|0⟩, |1⟩ → e^{iπ/4}|1⟩

State: (−i|0⟩ + i|1⟩)/√2 ⊗ (e^{-iπ/4}|0⟩ + i·e^{iπ/4}|1⟩)/√2

7. H(q[0]): |0⟩ → (|0⟩+|1⟩)/√2, |1⟩ → (|0⟩−|1⟩)/√2

(−i|0⟩ + i|1⟩)/√2 → H gives: −i(|0⟩+|1⟩)/√2 + i(|0⟩−|1⟩)/√2 all divided by √2
= (−i|0⟩ − i|1⟩ + i|0⟩ − i|1⟩)/2 = (−2i|1⟩)/2 = −i|1⟩

So after H(q[0]): −i|1⟩ ⊗ (e^{-iπ/4}|0⟩ + i·e^{iπ/4}|1⟩)/√2

8. ctrl inv S(q[0], q[1]): When q[0]=|1⟩, apply S† to q[1]. S†|0⟩ = |0⟩, S†|1⟩ = -i|1⟩

State: −i|1⟩ ⊗ (e^{-iπ/4}|0⟩ + i·e^{iπ/4}·(−i)|1⟩)/√2
= −i|1⟩ ⊗ (e^{-iπ/4}|0⟩ + e^{iπ/4}|1⟩)/√2

9. H(q[1]): 
(|0⟩ + |1⟩)/√2 coefficient: e^{-iπ/4}/√2
(|0⟩ − |1⟩)/√2 coefficient: e^{iπ/4}/√2

|0⟩ coefficient: (e^{-iπ/4} + e^{iπ/4})/2 = cos(π/4) = 1/√2
|1⟩ coefficient: (e^{-iπ/4} − e^{iπ/4})/2 = −i·sin(π/4) = −i/√2

So state: −i|1⟩ ⊗ (|0⟩/√2 − i|1⟩/√2) = −i|1⟩ ⊗ (|0⟩ − i|1⟩)/2

10. CNOT(q[0], q[1]): q[0] is control, q[1] is target. Since q[0]=|1⟩, flip q[1].
(|0⟩ → |1⟩, |1⟩ → |0⟩)

State: −i|1⟩ ⊗ (|1⟩ − i|0⟩)/2 = −i(|11⟩ − i|10⟩)/2

= −i|11⟩/2 − |10⟩/2... wait let me redo.

−i|1⟩⊗(|0⟩−i|1⟩)/2 = (−i|10⟩ + i²|11⟩)/2 = (−i|10⟩ − |11⟩)/2

CNOT(q[

### Reference answer

{'predicted_probs': {'10': 1.0}, 'explanation': 'Draper QFT adder: 1+1=2. Index 2 has P=1.0.'}

## isqTrain/4426

- task_id: `isqTrain/4426`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4874`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[2];

procedure main() {
    // 1. Initial state
    H(q[0]); H(q[1]);
    
    // 2. Cost Unitary (gamma = pi/4)
    // Rz(2*gamma) = Rz(pi/2)
    CNOT(q[0], q[1]);
    Rz(pi/2.0, q[1]);
    CNOT(q[0], q[1]);
    
    // 3. Mixing Unitary (beta = pi/8)
    // Rx(2*beta) = Rx(pi/4)
    Rx(pi/4.0, q[0]);
    Rx(pi/4.0, q[1]);
    
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Output prediction for an isQ program.
    *   Input: isQ program with a 2-qubit circuit.
    *   Output: "## Circuit Analysis" section with step-by-step reasoning, ending with the predicted probability distribution.
    *   Constraints: Concise (3-15 lines), use Dirac notation, no code blocks.

2.  **Analyze the isQ Code:**
    *   `qbit q[2];` -> 2 qubits, $|00\rangle$ initial state.
    *   `H(q[0]); H(q[1]);` -> Apply H to both. State: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
    *   `CNOT(q[0], q[1]); Rz(pi/2.0, q[1]); CNOT(q[0], q[1]);` -> This is the standard $ZZ$-interaction (cost unitary) for $\gamma = \pi/4$. Equivalent to applying $Rz(\pi/2)$ to $q[1]$ controlled by $q[0]$, which adds a phase based on $Z \otimes Z$.
        *   $|00\rangle \to |00\rangle$
        *   $|01\rangle \to |01\rangle$
        *   $|10\rangle \to e^{-i\pi/4} |10\rangle$
        *   $|11\rangle \to e^{i\pi/4} |11\rangle$  *(Wait, let's be careful. CNOT, Rz(pi/2), CNOT. If control is |0>, target is unaffected by Rz. If control is |1>, target gets flipped. E.g. |10> -> |11> -> Rz(pi/2)|11> = e^{-i\pi/4}|11> -> |10>. So |10> gets e^{-i\pi/4}. What about |11>? |11> -> |10> -> Rz|10> = e^{i\pi/4}|10> -> |11>. So |11> gets e^{i\pi/4}. Correct.)*
        *   State after step 2: $\frac{1}{2}(|00\rangle + |01\rangle + e^{-i\pi/4}|10\rangle + e^{i\pi/4}|11\rangle)$.
    *   `Rx(pi/4.0, q[0]); Rx(pi/4.0, q[1]);` -> Apply $R_x(\pi/4)$ to both qubits. $R_x(\theta) = e^{-i\theta X/2}$.
        *   This mixes the states. Let's evaluate it term by term or tensor product $R_x(\pi/4) \otimes R_x(\pi/4)$.
    *   `H(q[0]); Z(q[0]); H(q[0]);` -> This applies $HZH = X$ to $q[0]$.
    *   `M(q[0]); M(q[1]);` -> Measure both.

3.  **Detailed State Evolution:**
    *   Let's represent $R_x(\pi/4)$.
        *   $R_x(\pi/4)|0\rangle = \cos(\pi/8)|0\rangle - i\sin(\pi/8)|1\rangle$
        *   $R_x(\pi/4)|1\rangle = -i\sin(\pi/8)|0\rangle + \cos(\pi/8)|1\rangle$
    *   State before Rx: $|\psi_2\rangle = \frac{1}{2} (|00\rangle + |01\rangle + e^{-i\pi/4}|10\rangle + e^{i\pi/4}|11\rangle)$.
    *   Let's factor it: $|\psi_2\rangle = \frac{1}{2} [ |0\rangle(|0\rangle + |1\rangle) + e^{-i\pi/4}|1\rangle(|0\rangle + e^{i\pi/2}|1\rangle) ]$.
    *   Wait, $e^{-i\pi/4} \times e^{i\pi/4}$? No.
    *   Let's just compute the amplitudes of the 4 states after $R_x^{\otimes 2}(\pi/4)$.
        *   Let $c = \cos(\pi/8)$, $s = \sin(\pi/8)$. Note: $c=\frac{\sqrt{2+\sqrt{

### Reference answer

{'predicted_probs': {'01': 0.5, '10': 0.5}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|01>) = 0.5000, P(|10>) = 0.5000.'}

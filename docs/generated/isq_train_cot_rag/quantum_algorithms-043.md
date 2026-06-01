# ISQ training COT RAG corpus: quantum_algorithms shard 43

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3070

- task_id: `isqTrain/3070`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_multi_register`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `423`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```isq
import std;
qbit q[4];
// Initialize to |0010>
procedure main() {
    // X(q[2]); // BUG: missing initialization
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. The bug is a missing initialization gate where `X(q[2])` is commented out. This prevents `q[2]` from flipping to |1>, leaving the system in the |0000> state instead of the target |0010> state.
2. The fix is to uncomment `X(q[2])` to properly apply the Pauli-X gate to the third qubit.
3. State evolution of the corrected circuit:
   - Begin with the 4-qubit initial state |0000>.
   - Apply the X gate to `q[2]`, which flips it from |0> to |1>.
   - The system transitions to the |0010> state.
   - Subsequent measurements deterministically yield the bitstring 0010 with a probability of 1.0.

## isqTrain/3902

- task_id: `isqTrain/3902`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `167`

### Prompt

下面的量子程序运行结果不对，请帮我debug：

```
import std;
// QAOA MaxCut p=1 on 4-node path graph
// gamma=0.785, beta=0.393
qbit q[4];

procedure main() {
    // Superposition
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    // Cost unitary
    // Edge (0,1)
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.785, q[1]);
    CNOT(q[0], q[1]);
    // Edge (1,2)
    CNOT(q[1], q[2]);
    Rz(2.0 * 0.785, q[2]);
    CNOT(q[1], q[2]);
    // Edge (2,3)
    CNOT(q[2], q[3]);
    // BUG: missing gate here
    CNOT(q[2], q[3]);
    // Mixer
    Rx(2.0 * 0.393, q[0]);
    Rx(2.0 * 0.393, q[1]);
    Rx(2.0 * 0.393, q[2]);
    Rx(2.0 * 0.393, q[3]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **What the bug is**: The Edge (2,3) cost unitary is missing the `Rz(2.0 * 0.785, q[3])` gate between the two CNOT gates. The QAOA cost unitary for each edge requires a CNOT-Rz-CNOT sequence to implement the $e^{-i\gamma Z_i Z_j}$ interaction, but edge (2,3) only has CNOT-CNOT (which is identity), effectively skipping the ZZ interaction for that edge entirely.

2. **What the fix is**: Add `Rz(2.0 * 0.785, q[3])` between the two CNOT gates in the Edge (2,3) section, matching the pattern used for edges (0,1) and (1,2).

3. **Brief state evolution of the corrected circuit**:
   - **Superposition**: H on all qubits → $|+\rangle^{\otimes 4}$
   - **Cost unitary (corrected)**: Each edge (0,1), (1,2), (2,3) applies CNOT-Rz(2γ, target)-CNOT, implementing $e^{-i\gamma Z_i Z_j}$:
     - Edge (0,1): entangles q[0], q[1] with phase rotation 1.57 rad
     - Edge (1,2): entangles q[1], q[2] with phase rotation 1.57 rad
     - Edge (2,3): entangles q[2], q[3] with phase rotation 1.57 rad
   - **Mixer**: Rx(2β) = Rx(0.786) on all qubits rotates each qubit around X-axis
   - **Measurement**: Produces expected distribution with maxima at |0000⟩ (0.156), |0011⟩ (0.156), |1100⟩ (0.156), |1111⟩ (0.156) corresponding to maximal and minimal cuts of the path graph

## isqTrain/2974

- task_id: `isqTrain/2974`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2619`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[4];
procedure main() {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    CNOT(q[3], q[0]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    CNOT(q[3], q[0]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}
```

### Chain-of-thought reasoning

Step 1: Initialize state to |0000>.
Step 2: Apply H to q[0], q[1], q[2], q[3]. State becomes an equal superposition of all 16 basis states: 1/4 (|0000> + |0001> + ... + |1111>).
Step 3: Apply CNOT(q[0], q[1]).
Step 4: Apply CNOT(q[1], q[2]).
Step 5: Apply CNOT(q[2], q[3]).
Step 6: Apply CNOT(q[3], q[0]).
This sequence of CNOTs acts as a cyclic parity generator.
Let's trace the effect:
Initial state before CNOTs is sum_{x3x2x1x0} |x3x2x1x0> / 4.
Let's represent the state as 1/4 sum_{x \in {0,1}^4} |x>.
The CNOTs in order:
C01: x1 -> x1 ^ x0
C12: x2 -> x2 ^ (x1 ^ x0) = x2 ^ x1 ^ x0
C23: x3 -> x3 ^ (x2 ^ x1 ^ x0) = x3 ^ x2 ^ x1 ^ x0
C30: x0 -> x0 ^ (x3 ^ x2 ^ x1 ^ x0) = x3 ^ x2 ^ x1
Let's denote the initial string as (x3, x2, x1, x0).
After C01: (x3, x2, x1^x0, x0)
After C12: (x3, x2^x1^x0, x1^x0, x0)
After C23: (x3^x2^x1^x0, x2^x1^x0, x1^x0, x0)
After C30: (x3^x2^x1^x0, x2^x1^x0, x1^x0, x0 ^ (x3^x2^x1^x0)) = (x3^x2^x1^x0, x2^x1^x0, x1^x0, x3^x2^x1).
Since this is a permutation of the basis states (bijective mapping from x to x'), the state is still an equal superposition of all 16 basis states.
Step 7: Apply H to all 4 qubits.
H^{\otimes 4} (1/4 sum_x |x>) = 1/4 * 1/4 sum_y (sum_x (-1)^{x \cdot y}) |y> = sum_y \delta_{y,0} |y> = |0000>.
Wait, let me double check this.
The state after the CNOTs is an equal superposition of all 16 basis states.
Applying H^{\otimes 4} to an equal superposition gives |0000>.
Yes, 1/4 sum_x H^{\otimes 4} |x> = 1/4 sum_y (1/4 sum_x (-1)^{x \cdot y}) |y> = |0000>.
Step 8: Apply the same sequence of CNOTs to |0000>.
CNOTs applied to |0000> do nothing, as all qubits are |0>. So the state remains |0000>.
Step 9: Measurement of all qubits yields |0000> with probability 1.0.
The sequence is H^4 * CNOTs * H^4 * CNOTs.
Since H^4 * CNOTs * H^4 is a Clifford circuit, let's see:
H CNOT H is CZ.
Wait, CNOT control=0, target=1.
H(1) CNOT(0,1) H(1) = CZ(0,1).
Here we have H^4 * CNOTs * H^4.
If we apply H to the target before CNOT and H after CNOT, we get CZ.
But here H is applied to ALL qubits.
Let's trace:
Initial: |0000>
H^4: equal superposition
CNOTs: equal superposition
H^4: |0000>
CNOTs: |0000>
Final state: |0000>.
This is very straightforward.

Let's do a quick sanity check.
Start with |0000>
H H H H -> 1/4 sum |x>
CNOT(0,1) -> permutes states
CNOT(1,2) -> permutes states
CNOT(2,3) -> permutes states
CNOT(3,0) -> perm

### Reference answer

{'predicted_probs': {'0000': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3474

- task_id: `isqTrain/3474`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2641`

### Prompt

I need an isQ program to Grover for 3 qubits searching for |010> in isQ.
Oracle: X(q[0]), X(q[2]), ctrl ctrl Z, X(q[0]), X(q[2]).
2 iterations. Declare 3 qubits, measure all.

### Chain-of-thought reasoning

## Reasoning
**Goal**: Grover's algorithm searching for |010⟩ on 3 qubits with 2 iterations.

**Qubits**: 3 qubits declared globally, all measured at the end.

**State evolution**:
1. **H on all**: |000⟩ → |+++⟩ = (1/2√2)∑|x⟩, each amplitude = 1/2√2 ≈ 0.177
2. **Oracle**: X(q[0]);X(q[2]) maps |010⟩↔|111⟩, then `ctrl ctrl Z` phases |111⟩, then uncompute X gates → flips phase of |010⟩ only
3. **Diffusion** (H,X,double-controlled-Z (ctrl @[c1, c2] Z(target)),X,H): reflects amplitudes about the mean, amplifying |010⟩
4. **After iteration 1**: |010⟩ amplitude ≈ 0.685, others ≈ 0.088
5. **Iteration 2**: Oracle + Diffusion again further amplifies |010⟩
6. **Final state**: |010⟩ has amplitude ≈ 0.972, all others ≈ -0.088

**Expected probabilities**: |010⟩ probability = (0.972)² ≈ 0.945312; each of 7 other states = (0.088)² ≈ 0.007812. This matches optimal Grover amplification for N=8 with target item at angle θ = arcsin(1/√8) after 2 iterations giving sin²(5θ) ≈ 0.945.

## isqTrain/2001

- task_id: `isqTrain/2001`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `417`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[3];
procedure main() {
    X(q[0]);
    X(q[1]);
    CNOT(q[1], q[2]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations**: The circuit initializes 3 qubits to |000>. It applies an X gate to `q[0]` and `q[1]`, followed by a CNOT gate with `q[1]` as control and `q[2]` as target. Finally, it measures `q[2]`.
2. **State Evolution**:
   - Initial state: |000>
   - After `X(q[0])`: |100>
   - After `X(q[1])`: |110>
   - After `CNOT(q[1], q[2])`: The target `q[2]` flips because the control `q[1]` is in the |1> state. The state becomes |111>.
3. **Final State**: The quantum state of the system before measurement is |111>. 
4. **Measurement Probabilities**: Measuring `q[2]` will deterministically yield the state |1>.

Predicted probabilities: {'1': 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Comparator a=3 >= 2: result=1 with P=1.0.'}

## isqTrain/868

- task_id: `isqTrain/868`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3230`

### Prompt

帮我写一个isQ程序：implements the quantum_logic_gate pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning

**Goal**: Compute OR(a=1, b=0) = 1 using De Morgan's law: OR(a,b) = NOT(NOT(a) AND NOT(b)), with reversed measurement ordering.

**Qubits**: 3 qubits — q[0] (input a), q[1] (input b), q[2] (output); all measured in reverse order (q[2] first → highest bit).

**State evolution**:
1. |000⟩ → X(q[0]) → |100⟩ (set a=1, b=0)
2. X(q[0]), X(q[1]) → |010⟩ (negate both inputs)
3. Toffoli(q[0],q[1],q[2]) → |010⟩ (AND of negated inputs: 0 AND 1 = 0, no flip)
4. X(q[0]), X(q[1]) → |100⟩ (restore original inputs)
5. X(q[2]) → |101⟩ (negate AND result → OR = 1)

**Result**: Final state |101⟩ has q[2]=1 (OR=1), q[1]=0 (b), q[0]=1 (a). With reversed measurement M(q[2]), M(q[1]), M(q[0]), the bitstring is |q[2]q[1]q[0]⟩ = |101⟩ at index 5, giving P(|101⟩) = 1.0.

## isqExpand/algo/69

- task_id: `isqExpand/algo/69`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `vqe`, `hardware_efficient_ansatz`, `3_qubit`, `linear_entangling`
- source: `isq_expansion`
- dataset_index: `344`

### Prompt

Implement the following in isQ: implementing a 3-qubit VQE hardware-efficient ansatz with one layer. Apply Ry(pi/4) to all three qubits, then apply a linear CNOT entangling chain: CNOT(q[0], q[1]) followed by CNOT(q[1], q[2]). Measure all three qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: 3-qubit VQE hardware-efficient ansatz.

Circuit: Ry(pi/4) on all 3 qubits, then CNOT(0,1), CNOT(1,2).

After Ry(pi/4) on each:
- Each qubit: cos(pi/8)|0> + sin(pi/8)|1>
- cos(pi/8) ≈ 0.9239, sin(pi/8) ≈ 0.3827

The 3-qubit product state has 8 amplitudes before CNOT chain.
CNOT(0,1) flips q[1] when q[0]=1.
CNOT(1,2) flips q[2] when q[1]=1 (after the first CNOT).

This creates a non-trivial 3-qubit entangled state. The linear CNOT chain is a common hardware-efficient entangling pattern.

Numerical: P(000)=0.6219, P(001)=0.1067, P(010)=0.0183, P(011)=0.1067, P(100)=0.0183, P(101)=0.0031, P(110)=0.0183, P(111)=0.1067.

## isqTrain/3501

- task_id: `isqTrain/3501`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `basis_change`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4989`

### Prompt

分析以下isQ程序的测量概率分布：

```
import std;

qbit q[1];

procedure main() {
    X(q[0]);
    H(q[0]);
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial state**: The qubit starts in the state |0>.
2. **X gate**: Flips the state from |0> to |1>.
3. **First H gate**: Applies a Hadamard gate, changing the state from |1> to |-> (H|1> = |->).
4. **Second H gate**: Applies another Hadamard gate. Since H is its own inverse, it reverses the previous superposition, changing the state from |-> back to |1> (H|-> = |1>).
5. **Final state**: The quantum state before measurement is exactly |1>.

**Predicted probability distribution:**
- State `1` (|1>): 100%
- State `0` (|0>): 0%

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'The output is |1> with probability 1.0'}

## isqTrain/1419

- task_id: `isqTrain/1419`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_ctrl_nctrl`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4280`

### Prompt

实现以下量子计算任务（使用isQ）：Apply the 3-qubit Quantum Fourier Transform to the input state |010> and measure all qubits.

### Chain-of-thought reasoning

Let me analyze the 3-qubit Quantum Fourier Transform applied to the input state |010>.

1. The goal is to apply the 3-qubit QFT to the state |010> and measure all qubits.

2. We need 3 qubits (q[0], q[1], q[2]), all of which are measured.

3. Step-by-step evolution:

Initial state: |000>

After X(q[1]): |010>

Now applying QFT on 3 qubits:

The QFT on 3 qubits transforms the computational basis states as follows:
QFT |j⟩ = (1/√8) Σ_k e^(2πijk/8) |k⟩

For |010⟩ = |2⟩:
QFT |2⟩ = (1/√8) Σ_k e^(4πik/8) |k⟩
= (1/√8) Σ_k e^(πik/2) |k⟩

Let me compute this:
- k=0: e^0 = 1
- k=1: e^(iπ/2) = i
- k=2: e^(iπ) = -1
- k=3: e^(3iπ/2) = -i
- k=4: e^(2iπ) = 1
- k=5: e^(5iπ/2) = i
- k=6: e^(3iπ) = -1
- k=7: e^(7iπ/2) = -i

So QFT |2⟩ = (1/√8)(|0⟩ + i|1⟩ - |2⟩ - i|3⟩ + |4⟩ + i|5⟩ - |6⟩ - i|7⟩)

The probability of measuring each basis state is |1/√8|² = 1/8 = 0.125 for all states.

This matches the predicted output: {|000>: 0.125, |001>: 0.125, |010>: 0.125, |011>: 0.125, |100>: 0.125, |101>: 0.125, |110>: 0.125, |111>: 0.125}

Now let me trace through the circuit step by step:

After X(q[1]): |010⟩ = |q[0]=0, q[1]=1, q[2]=0⟩

The QFT circuit for 3 qubits:
1. H(q[2])
2. ctrl S(q[1], q[2])
3. ctrl T(q[0], q[2])
4. H(q[1])
5. ctrl S(q[0], q[1])
6. H(q[0])
7. swap (three-CNOT decomposition)(q[0], q[2])

Let me trace this more carefully. Starting with |010⟩ = |0⟩|1⟩|0⟩ (in order q[0], q[1], q[2])

Step 1: H(q[2]) on |0⟩ → (|0⟩ + |1⟩)/√2
State: |0⟩|1⟩(|0⟩ + |1⟩)/√2 = (|010⟩ + |011⟩)/√2

Step 2: ctrl S(q[1], q[2]) - S gate on q[2] controlled by q[1]
When q[1]=|1⟩, apply S to q[2]
S|0⟩ = |0⟩, S|1⟩ = i|1⟩
So |010⟩ → |010⟩ and |011⟩ → i|011⟩
State: (|010⟩ + i|011⟩)/√2

Step 3: ctrl T(q[0], q[2]) - T gate on q[2] controlled by q[0]
When q[0]=|0⟩ (which is always the case here), nothing happens
State: (|010⟩ + i|011⟩)/√2

Step 4: H(q[1]) on |1⟩ → (|0⟩ - |1⟩)/√2
State: (|0⟩(|0⟩-|1⟩)|0⟩ + i|0⟩(|0⟩-|1⟩)|1⟩)/2
= (|000⟩ - |010⟩ + i|001⟩ - i|011⟩)/2

Step 5: ctrl S(q[0], q[1]) - S gate on q[1] controlled by q[0]
When q[0]=|0⟩, nothing happens
State unchanged: (|000⟩ - |010⟩ + i|001⟩ - i|011⟩)/2

Step 6: H(q[0]) on |0⟩ → (|0⟩ + |1⟩)/

## isqTrain/714

- task_id: `isqTrain/714`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `boolean_logic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5611`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[3];

procedure main() {
    // Encode a = 3: both bits are 1
    X(q[0]);
    X(q[1]);
    // Equality check: a == 3 when both bits are 1
    // Toffoli gate acts as AND on the two input bits
    Toffoli(q[0], q[1], q[2]);
    // Measure the equality flag
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial State**: The 3-qubit system starts in the basis state |000>.
2. **State Preparation**: The X gates applied to q[0] and q[1] flip these qubits from |0> to |1>, evolving the state to |110>.
3. **Equality Check**: The Toffoli gate acts as a classical AND gate, flipping the target q[2] if and only if both control qubits (q[0] and q[1]) are in the |1> state.
4. **Final State**: Since both controls evaluate to true (|1>), the target q[2] is flipped from |0> to |1>. The system evolves to the final state |111>.
5. **Measurement**: Measuring q[2] collapses the state. Since q[2] is deterministically in the |1> state, the outcome is entirely predictable.

Expected measurement probabilities: {|1>: 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqEval/275. Dimension: predict probabilities for reference circuit.'}

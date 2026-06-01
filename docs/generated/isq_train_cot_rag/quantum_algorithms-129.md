# ISQ training COT RAG corpus: quantum_algorithms shard 129

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/algo/217

- task_id: `isqExpand/algo/217`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ghz_state`, `superposition`, `entanglement`, `cnot_chain`, `bell_state_generalization`
- source: `isq_expansion`
- dataset_index: `1812`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[5];
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    CNOT(q[3], q[4]);
}
```

### Chain-of-thought reasoning

Step 1: The initial state is |00000⟩ (all 5 qubits in |0⟩).

Step 2: H(q[0]) puts qubit 0 into superposition: (|0⟩+|1⟩)/√2 ⊗ |0000⟩ = (|00000⟩ + |10000⟩)/√2.

Step 3: CNOT(q[0], q[1]) entangles qubits 0 and 1. When q[0]=|0⟩, q[1] stays |0⟩. When q[0]=|1⟩, q[1] flips to |1⟩. State: (|00000⟩ + |11000⟩)/√2.

Step 4: CNOT(q[1], q[2]) propagates the entanglement. State: (|00000⟩ + |11100⟩)/√2.

Step 5: CNOT(q[2], q[3]) further propagates. State: (|00000⟩ + |11110⟩)/√2.

Step 6: CNOT(q[3], q[4]) completes the chain. Final state: (|00000⟩ + |11111⟩)/√2.

This is the 5-qubit GHZ state, a maximally entangled state where all qubits are perfectly correlated. Measurement yields |00000⟩ with probability |1/√2|² = 0.5, and |11111⟩ with probability |1/√2|² = 0.5. All other 30 bitstrings have probability 0.

### Reference answer

{'predicted_probs': {'00000': 0.5, '11111': 0.5}, 'explanation': 'The circuit starts with all qubits in |0⟩, giving |00000⟩. Applying H(q[0]) creates (|0⟩+|1⟩)/√2 ⊗ |0000⟩ = (|00000⟩+|10000⟩)/√2. Each CNOT in the chain copies the control bit to the target: CNOT(0,1) → (|00000⟩+|11000⟩)/√2, CNOT(1,2) → (|00000⟩+|11100⟩)/√2, CNOT(2,3) → (|00000⟩+|11110⟩)/√2, CNOT(3,4) → (|00000⟩+|11111⟩)/√2. This is the 5-qubit GHZ state. Measurement yields either 00000 or 11111, each with probability 0.5.'}

## isqTrain/1084

- task_id: `isqTrain/1084`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2479`

### Prompt

Create an isQ quantum circuit that implements a variant of the deutsch_jozsa pattern using anc[1] -> anc[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement a Deutsch-Jozsa variant with a balanced oracle f(x)=x[0]⊕x[1] using a 5-qubit register (2 input + 3 ancilla), with anc[1]-anc[2] left in |0⟩.

Only q[0] and q[1] are measured; ancilla qubits are not measured.

State evolution:
1. Initialize: |00⟩|000⟩
2. X(anc[0]), H(anc[0]): |00⟩(|0⟩-|1⟩)/√2 |00⟩
3. H(q[0]), H(q[1]): (|00⟩+|01⟩+|10⟩+|11⟩)/2 ⊗ (|0⟩-|1⟩)/√2 |00⟩
4. Oracle f(q,anc): Phase kickback from balanced oracle flips signs for |01⟩,|10⟩: (|00⟩-|01⟩-|10⟩+|11⟩)/2 ⊗ (|0⟩-|1⟩)/√2 |00⟩
5. H(q[0]), H(q[1]): |11⟩ ⊗ (|0⟩-|1⟩)/√2 |00⟩

The balanced oracle produces orthogonal state to |00⟩ after final Hadamards. Since f(x)=x[0]⊕x[1] is balanced (returns 1 for exactly half of inputs), interference yields |11⟩ with certainty: measurement probability {|11⟩: 1.0}.

## isqTrain/1389

- task_id: `isqTrain/1389`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `734`

### Prompt

实现以下量子计算任务（使用isQ）：the Bernstein-Vazirani algorithm to find the secret string s = 010 (MSB first). Use 3 input qubits and 1 ancilla.

### Chain-of-thought reasoning

## Reasoning

**Goal**: Implement Bernstein-Vazirani to find secret string s=010 using a single oracle query.

**Qubits**: 4 qubits total (q[0,1,2] input, anc[0] ancilla); measure q[0], q[1], q[2].

**State evolution**:
1. Initialize |0000⟩; X(anc[0]) → |0001⟩; H(anc[0]) → |000⟩|−⟩
2. H(q[0,1,2]) → (1/√8)Σ|x⟩|−⟩ where x ∈ {0,1}³ (uniform superposition over input)
3. CNOT(q[1],anc[0]) — oracle for s=010: flips ancilla when q[1]=|1⟩. Since X|−⟩=−|−⟩, this applies phase (−1)^(s·x): →

## isqTrain/3554

- task_id: `isqTrain/3554`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `474`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should Full adder: 0+1+1=10.

### Chain-of-thought reasoning

Let me analyze the buggy code and the fix.

The full adder computes: sum = a XOR b XOR cin, carry = (a AND b) OR (cin AND (a XOR b))

The buggy code has:

The fixed code has:

Wait, let me re-read. The buggy code has `CNOT(q[1], q[0])` and the corrected version has `CNOT(q[0], q[1])`. 

Actually, let me look more carefully at the full adder circuit.

In the buggy code:

The fix changes `CNOT(q[1], q[0])` to `CNOT(q[0], q[1])`.

Let me trace through the corrected circuit:

Initial: q[0]=|0⟩ (a), q[1]=|1⟩ (b), q[2]=|1⟩ (cin), q[3]=|0⟩ (carry)
State: |0110⟩ (q[3]q[2]q[1]q[0])

Wait, let me use the qubit ordering as given: q[0], q[1], q[2], q[3].

State: |0⟩|1⟩|1⟩|0⟩

Step 1: ctrl ctrl X(q[0], q[1], q[3]) - Toffoli with q[0] and q[1] as controls, q[3] as target.
q[0]=|0⟩, so q[3] is NOT flipped.
State: |0⟩|1⟩|1⟩|0⟩

Step 2 (fixed): CNOT(q[0], q[1]) - q[0] is control, q[1] is target.
q[0]=|0⟩, so q[1] is NOT flipped.
State: |0⟩|1⟩|1⟩|0⟩

Step 3: ctrl ctrl X(q[1], q[2], q[3]) - Toffoli with q[1] and q[2] as controls, q[3] as target.
q[1]=|1⟩, q[2]=|1⟩, so q[3] IS flipped.
State: |0⟩|1⟩|1⟩|1⟩

Step 4: CNOT(q[2], q[1]) - q[2] is control, q[1] is target.
q[2]=|1⟩, so q[1] IS flipped.
State: |0⟩|0⟩|1⟩|1⟩

So final state: q[0]=0, q[1]=0, q[2]=1, q[3]=1

Binary string: 0011 which means 0+1+1 = sum=0, carry=1. ✓

Now let me verify with the buggy CNOT(q[1], q[0]):

Step 1: ctrl ctrl X(q[0], q[1], q[3])
q[0]=|0⟩, q[1]=|1⟩ → q[3] NOT flipped
State: |0⟩|1⟩|1⟩|0⟩

Step 2 (buggy): CNOT(q[1], q[0]) - q[1] is control, q[0] is target.
q[1]=|1⟩, so q[0] IS flipped to |1⟩.
State: |1⟩|1⟩|1⟩|0⟩

Step 3: ctrl ctrl X(q[1], q[2], q[3]) - Toffoli with q[1] and q[2] as controls.
q[1]=|1⟩, q[2]=|1⟩ → q[3] IS flipped.
State: |1⟩|1⟩|1⟩|1⟩

Step 4: CNOT(q[2], q[1]) - q[2] control, q[1] target.
q[2]=|1⟩ → q[1] flipped to |0⟩.
State: |

## isqTrain/4464

- task_id: `isqTrain/4464`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2174`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[4];

procedure main() {
    // Set both input qubits to |1>
    X(q[0]);
    X(q[1]);
    // Weight 1 contribution: add x0 to sum bit 0
    CNOT(q[0], q[2]);
    // Weight 2 contribution: add x1 to sum bit 1
    CNOT(q[1], q[3]);
    // Measure the 2-bit sum output
    X(q[0]); // flip qubit 0 before measurement
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants an analysis of an isQ quantum program predicting the probability distribution of measurement outcomes, following specific formatting and length constraints.

2.  **Analyze the isQ code**:
    *   `qbit q[4];`: 4 qubits initialized to $|0000\rangle$.
    *   `X(q[0]); X(q[1]);`: Apply X gate to q0 and q1. State becomes $|1100\rangle$.
    *   `CNOT(q[0], q[2]);`: Control q0, target q2. q0 is $|1\rangle$, so q2 flips to 1. State becomes $|1110\rangle$.
    *   `CNOT(q[1], q[3]);`: Control q1, target q3. q1 is $|1\rangle$, so q3 flips to 1. State becomes $|1111\rangle$.
    *   `X(q[0]);`: Apply X gate to q0. q1 flips to 0. State becomes $|0111\rangle$.
    *   `M(q[2]); M(q[3]);`: Measurements are typically returned as a bitstring. The problem mentions "Number of qubits measured: 4" and "Expected measurement probabilities: {|0011>: 1.0}". Wait, let's look at the output format for `--probs`. The instructions say "array indexed by measurement bitstring (earlier measured qubit = higher bit)". But wait, only q[2] and q[3] are measured in the code `M(q[2]); M(q[3]);`. However, the prompt says "Expected measurement probabilities: {|0011>: 1.0}". Oh! Wait. The implementation says `Expected measurement probabilities: {|0011>: 1.0}`. This implies the output bitstring might just be for all qubits or specifically the measured ones? Let's trace carefully.
    *   Actually, let's re-read the state. $q_0, q_1$ are inputs, $q_2, q_3$ are outputs.
    *   $q_0=1, q_1=1 \implies$ weights. $q_2=1, q_3=1$.
    *   The state right before measurement is $|0111\rangle$ where $q_0=0, q_1=1, q_2=1, q_3=1$.
    *   Wait, is it `|0011>`? If only $q_2$ and $q_3$ are measured, the measurement outcome of $q_2$ and $q_3$ is `11`. But `--probs` mode in some simulators measures all qubits or only the measured ones? The reference explicitly says `{0011: 1.0}` for 4 qubits. If the output bitstring represents $q_0, q_1, q_2, q_3$, wait, $q_0=0, q_1=1, q_2=1, q_3=1$ would be `0111` in binary (assuming $q_0$ is highest bit).
    *   Let's re-read: "Earlier measured qubit = higher bit". So if M(q[2]) and M(q[3]) are the *only* measurements, maybe $q_2$ is the higher bit, $q_3$ is the lower bit? Then `11`.
    *   But the reference says `Expected measurement probabilities: {|0011>: 1.0}`. Wait, if the whole state is $q_0=0, q_1=1, q_2=1, q_3=1$, wait. `q[0]` was flipped to 0. `q[1]` was left as 1. `q[2]`=1, `q[3]`=1. So the full state is `0111` (reading $q_0q_1q_2q_3$). But the expected measurement is `0011`. Let me re-read the isQ code. Maybe the predicted output in the prompt is `{0111>: 1.0}` but typoed as `0011`? Or maybe $q_1$ was also flipped? No `X(q[1])` at the end.
    *   Let's just trace the state accurately. The reference says `{|0011>: 1.0}`. Let me re-read the circuit.
    *   `X(q[0]); X(q[1]);` -> `|1100>`
    *   `CNOT(q[0], q[2]);` -> `|1110

### Reference answer

{'predicted_probs': {'0011': 1.0}, 'explanation': 'This isQ program operates on 4 qubit(s). The measurement probability distribution is: P(|0011>) = 1.0000.'}

## isqTrain/3954

- task_id: `isqTrain/3954`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4547`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```
import std;
// Deutsch-Jozsa for 3-input balanced oracle
oracle f(3, 1) = [0, 0, 0, 0, 1, 1, 1, 1];
qbit q[4];  // 3 input + 1 output

procedure main() {
    // Output in |->
    X(q[3]);
    H(q[3]);
    // Hadamard on all inputs
    for i in 0:3 {
        X(q[i]);
    }
    // Apply oracle
    f(q[0], q[1], q[2], q[3]);
    // Hadamard
    for i in 0:3 {
        H(q[i]);
    }
    // Measure
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

Let me analyze the buggy code and the fix.

The Deutsch-Jozsa algorithm for a 3-input balanced oracle should work as follows:
1. Initialize 3 input qubits to |0⟩ and 1 output qubit to |-⟩
2. Apply Hadamard gates to all input qubits
3. Apply the oracle
4. Apply Hadamard gates to all input qubits
5. Measure the input qubits

The buggy code has:

This applies X gates to all qubits instead of H gates. The X gate flips the qubit from |0⟩ to |1⟩, which is wrong.

The corrected version:

This applies Hadamard gates to put the input qubits in superposition, which is correct for the Deutsch-Jozsa algorithm.

Let me verify the state evolution of the corrected circuit:

1. Initial state: |0000⟩

2. After X(q[3]) and H(q[3]): |000⟩ ⊗ |-⟩ = |000-⟩

3. After H on all inputs (H on q[0], q[1], q[2]):
|+++⟩ ⊗ |-⟩

4. After oracle f (which is a balanced oracle with f(0)=0, f(1)=0, f(2)=0, f(3)=0, f(4)=1, f(5)=1, f(6)=1, f(7)=1):
The oracle applies a phase based on f(x), so the state becomes:
1/√8 Σ_x (-1)^f(x) |x⟩ ⊗ |-⟩

For the balanced oracle f = [0,0,0,0,1,1,1,1]:
- f(0) = 0, f(1) = 0, f(2) = 0, f(3) = 0 (positive phase)
- f(4) = 1, f(5) = 1, f(6) = 1, f(7) = 1 (negative phase)

So the state is: 1/√8 (|000⟩ + |001⟩ + |010⟩ + |011⟩ - |100⟩ - |101⟩ - |110⟩ - |111⟩) ⊗ |-⟩

5. After H on all 4 qubits (H on q[0], q[1], q[2], q[3]):

Actually wait, the loop is `for i in 0:3` which means i goes from 0 to 2 (inclusive of 0, exclusive of 3), so it applies H to q[0], q[1], q[2].

Let me recalculate:

After H on q[0], q[1], q[2]:

The state before H on inputs is:
1/√8 (|000⟩ + |001⟩ + |010⟩ + |011⟩ - |100⟩ - |101⟩ - |110⟩ - |111⟩) ⊗ |-⟩

This can be written as:
1/√8 Σ_x (-1)^f(x) |x⟩ ⊗ |-⟩

After applying H⊗3 to the first 3 qubits:

For balanced oracle, the result should be |1⟩ on the first qubit (or some measurement that distinguishes balanced from constant).

Actually, for DJ algorithm, if the oracle is balanced, we should measure a non-zero result on the input qubits.

Let me think more carefully. The balanced oracle has f(x) = x[2] (the most significant bit), so it's balanced.

The state after oracle and before final H is:
1/√8 Σ_x (-1)^(x[2]) |x⟩ ⊗ |-⟩
= 1/√8 (|000⟩ + |001⟩ + |010⟩ + |011⟩ - |100⟩ - |101⟩ - |110⟩ - |111⟩) ⊗ |-⟩

This can be factored as:
1/√8 (|0⟩ + |1⟩ + |0⟩ + |1⟩ + |0⟩ + |1⟩ + |0⟩ + |1⟩) for q[0]... wait, let me think more systematically.

Actually:
= 1/√8 (|0⟩_2 + |1⟩_2 - |0⟩_2 - |1⟩_2) ⊗ (some superposition for q[1], q[0])

Wait, that doesn't look right. Let me just compute H⊗3 on the state.

The state is:
|ψ⟩ = 1/√8 Σ_x (-1)^(x[2]) |x⟩

where x[2] is the most

## isqQA/quantum_algorithms/96_hardware_limitations

- task_id: `isqQA/quantum_algorithms/96_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `hardware_limitations`, `algorithm`, `Grover算法的扩散算子`
- source: `qa_pipeline`
- dataset_index: `5625`

### Prompt

在含噪中等规模量子（NISQ）设备上实现Grover算法时，其核心组件扩散算子（Diffusion Operator）通常需要通过多控门分解为基础单、双量子比特门来实现。请详细解释硬件的退相干现象和有限的相干时间如何影响扩散算子的保真度，并探讨如何利用相对相位实现技术来优化多控门以降低电路深度。此外，请提供一个使用isQ语言实现的4量子比特Grover扩散算子代码示例，要求在代码中体现出使用相对相位分解多控门以适应NISQ硬件的优化策略。

### Reference answer

在当前的含噪中等规模量子（NISQ）时代，硬件设备面临着严峻的物理局限性，其中最主要的两个挑战是有限的量子比特相干时间（T1和T2时间）以及较高的双比特门（如CNOT）错误率。Grover算法的扩散算子，其标准数学形式为 $2|\psi\rangle\langle\psi| - I$（其中 $|\psi\rangle$ 是均匀叠加态），在量子电路中通常通过包裹Hadamard门和X门的多控Z门（或等效的多控X门）来实现。然而，物理硬件层面并不直接存在原生多控门，必须将其分解为单比特门和CNOT门。

对于NISQ设备而言，当量子比特数量 $N$ 增加时，标准多控门分解所需的CNOT门数量和电路深度会急剧上升。当电路的执行时间接近或超过量子比特的退相干时间时，量子态会因为环境耦合（纵向弛豫T1）和相位散射（横向弛豫T2）而发生严重退化。扩散算子的本质是利用量子干涉原理反转目标态的概率幅，但退相干会破坏维持这种干涉所需的相位关系，导致概率幅反转失败，最终使得计算结果表现为经典随机噪声，算法彻底失效。

为了缓解退相干的影响，必须在硬件层面极大限度地压缩扩散算子的门深度。一种针对NISQ架构极为有效的策略是采用“相对相位多控门”实现技术。传统的绝对相位多控门分解为了保证所有计算基态的绝对相位正确，往往需要引入大量的辅助量子比特或极深的CNOT级联。而相对相位多控门允许在非目标基态上引入相位偏移，由于Grover算法的Oracle和扩散算子在结构上的高度对称性，这些相对相位偏移通常可以在随后的操作中被抵消，从而并不影响最终的正确计算结果。这种优化能够将多控门分解的CNOT数量大幅削减，并且在无需额外辅助量子比特的情况下显著降低电路深度，从而有效“跑赢”退相干过程。

以下是在isQ语言中实现的4量子比特Grover扩散算子示例代码，其中展示了如何利用相对相位分解技术（借鉴了Margolus门等降阶逻辑）来实现无辅助比特的三控X门，以最大程度适应NISQ设备的硬件局限：```isq
import std;

qbit q[4];

procedure main() {
    // 假设前置Oracle已经对目标态进行了相位翻转
    // 开始执行针对4比特系统的扩散算子

    // 第一步：将多控Z转化为多控X的包裹操作
    for i in 0:4 {
        H(q[i]);
        X(q[i]);
    }

    // 第二步：实现相对相位优化的三控X门（Toffoli降阶逻辑）
    // 这种结构不需要额外的辅助比特，且显著降低了双比特门的深度
    H(q[3]);
    T(q[3]);
    ctrl @[q[0]] X(q[3]);
    inv T(q[3]);
    ctrl @[q[1]] X(q[3]);
    T(q[3]);
    ctrl @[q[0]] X(q[3]);
    inv T(q[3]);
    ctrl @[q[1]] X(q[3]);
    T(q[3]);
    ctrl @[q[2]] X(q[3]);
    inv T(q[3]);
    Toffoli(q[0], q[1], q[3]);
    inv T(q[3]);
    ctrl @[q[2]] X(q[3]);
    H(q[3]);

    // 第三步：恢复包裹操作
    for i in 0:4 {
        X(q[i]);
        H(q[i]);
    }
}
```

## isqTrain/716

- task_id: `isqTrain/716`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2075`

### Prompt

Code this in isQ: implements a variant of the ripple_carry_adder pattern using q[5] -> q[7]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze this problem step by step.

The task is to implement a variant of the ripple_carry_adder pattern using q[5] -> q[7], meaning we have 7 qubits total (q[0] through q[6]).

Analyzing the circuit requirements:
- We have 7 qubits: q[0] through q[6]
- We encode a=1 (binary 01) using q[0], q[1] and b=1 (binary 01) using q[2], q[3]
- q[4] is used as carry qubit
- q[5] and q[6] are additional qubits left in ground state

The circuit performs:
1. X(q[0]) - sets a0 = 1
2. X(q[2]) - sets b0 = 1
3. Toffoli(q[0], q[2], q[4]) - carry0 = a0 AND b0 = 1 AND 1 = 1
4. CNOT(q[0], q[2]) - sum0 = a0 XOR b0 = 1 XOR 1 = 0
5. CNOT(q[1], q[3]) - propagate a1 to b1 (a1=0, b1=0, result b1=0)
6. CNOT(q[4], q[3]) - propagate carry0 to b1 (carry0=1, b1=0, result b1=1)
7. M(q[2]) - measures sum0 = 0
8. M(q[3]) - measures sum1 = 1
9. M(q[5]) - measures q[5] = 0
10. M(q[6]) - measures q[6] = 0

So the measurement result should be |0100> (q[2]=0, q[3]=1, q[5]=0, q[6]=0)

Wait, let me check the bitstring ordering. The problem says "earlier measured qubit = higher bit". So:
- M(q[2]) is the highest bit
- M(q[3]) is next
- M(q[5]) is next
- M(q[6]) is the lowest bit

So the bitstring is: q[2] q[3] q[5] q[6]
With q[2]=0, q[3]=1, q[5]=0, q[6]=0
That gives us 0100 in binary, which matches the predicted output.

Now let me trace through the quantum state evolution:

Initial state: |0000000>

After X(q[0]): |1000000>
After X(q[2]): |1010000>

After Toffoli(q[0], q[2], q[4]): Both q[0] and q[2] are |1>, so q[4] flips to |1>: |1011000>

After CNOT(q[0], q[2]): q[0]=1, so q[2] flips from |1> to |0>: |1001000>

After CNOT(q[1], q[3]): q[1]=0, so no flip: |1001000>

After CNOT(q[4], q[3]): q[4]=1, so q[3] flips from |0> to |1>: |1001100>

Wait, I'm indexing wrong. Let me redo this properly.

Let me label the qubits as q6 q5 q4 q3 q2 q1 q0 (from left to right, high bit to low bit)

Initial: |0000000> (all zeros)

After X(q[0]): |0000001> (q0 = 1)
After X(q[2]): |0000101> (q2 = 1)

After Toffoli(q[0], q[2], q[4]): Since q0=1 and q2=1, q4 flips: |0010101> (q4 = 1)

After CNOT(q[0], q[2]): Since q0=1, q2 flips from 1 to 0: |0010001> (q2 = 0)

After CNOT(q[1], q[3]): Since q1=0, no change: |0010001>

After CNOT(q[4], q[3]): Since q4=1, q3 flips from 0 to 1: |0011001> (q3 = 1)

Wait, let me reconsider the indexing. In isQ, q[0] is the first qubit. The state |q6 q5 q4 q3 q2 q1 q0> where q0 is the rightmost (least significant) bit.

Initial: |000000

## isqExpand/algo/20

- task_id: `isqExpand/algo/20`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `qft`, `controlled_rotation`, `bug_fix`
- source: `isq_expansion`
- dataset_index: `4480`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]);
    ctrl S(q[1], q[0]);
    ctrl S(q[2], q[0]);
    H(q[1]);
    ctrl S(q[2], q[1]);
    H(q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Bug Analysis

In the 3-qubit QFT, the controlled rotations should be:
- Between q[0] and q[1]: controlled-S (phase pi/2) — correct
- Between q[0] and q[2]: controlled-T (phase pi/4) — BUG: uses S instead of T
- Between q[1] and q[2]: controlled-S (phase pi/2) — correct

The QFT controlled rotation between qubit j and qubit k uses R_k with angle 2π/2^(k-j). For q[0] controlled by q[2] (distance 2): angle = 2π/4 = π/4, which is the T gate.

Fix: Change `ctrl @[q[2]] S(q[0])` to `ctrl @[q[2]] T(q[0])`.

With correct QFT applied to |000>, the output is uniform over all 8 states.

## isqTrain/3465

- task_id: `isqTrain/3465`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `data_encoding_qml`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3409`

### Prompt

Implement a quantum circuit in isQ: angle encoding of classical data into a quantum state in isQ.

Encode the values [pi/4, pi/2, pi] into 3 qubits using Ry rotations.
Each qubit's state encodes one value: Ry(value, q[i]).

This is a common data encoding technique in quantum machine learning.

Declare 3 qubits, measure all.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Encode classical data [π/4, π/2, π] into 3 qubits using angle encoding via Ry rotations.
2. **Qubits**: 3 qubits declared (q[0], q[1], q[2]), all measured.
3. **State evolution**:
   - Initial state: |000>
   - Ry(π/4, q[0]): cos(π/8)|0⟩ + sin(π/8)|1⟩ for q[0] → (cos(π/8)|0⟩ + sin(π/8)|1⟩) |00⟩
   - Ry(π/2, q[1]): (|0⟩ + |1⟩)/√2 for q[1] → (cos(π/8)|0⟩ + sin(π/8)|1⟩) ((|0⟩ + |1⟩)/√2) |0⟩
   - Ry(π, q[2]): |1⟩ for q[2] → (cos(π/8)|0⟩ + sin(π/8)|1⟩) ((|0⟩ + |1⟩)/√2) |1⟩
4. **Final state**: (cos(π/8)/√2)|001⟩ + (cos(π/8)/√2)|011⟩ + (sin(π/8)/√2)|101⟩ + (sin(π/8)/√2)|111⟩
5. **Probabilities**: P(001)=P(011)=cos²(π/8)/2≈0.426777, P(101)=P(111)=sin²(π/8)/2≈0.073223, matching predicted output.

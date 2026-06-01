# ISQ training COT RAG corpus: quantum_algorithms shard 172

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2884

- task_id: `isqTrain/2884`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_ctrl_nctrl`, `measurement_order`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1041`

### Prompt

Write an isQ program that implementing a 4-controlled X gate. Set all 4 control qubits to |1>, then apply the multi-controlled X gate. Measure all 5 qubits.

Requirements:
- Declare `qbit q[5];` at global scope.
- Use `procedure main()` as entry point.
- Measure all 5 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a 4-controlled X gate to flip a target qubit when all four control qubits are |1>.
2. **Qubits**: 5 qubits declared (q[0]-q[3] as controls, q[4] as target); all 5 are measured.
3. **State evolution**:
   - Initial state: |00000⟩
   - After X(q[0]), X(q[1]), X(q[2]), X(q[3]): |11110⟩
   - After ctrl ctrl ctrl ctrl X(q[0], q[1], q[2], q[3], q[4]): All controls are |1⟩, so X flips q[4] → |11111⟩
4. **Expected probabilities**: Final state is |11111⟩ with probability 1.0, so measuring yields bitstring 11111 (all ones) with certainty.

## isqQA/quantum_algorithms/91_principle_advantage

- task_id: `isqQA/quantum_algorithms/91_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `principle_advantage`, `algorithm`, `BV算法的不同隐藏字符串实现`
- source: `qa_pipeline`
- dataset_index: `789`

### Prompt

伯恩斯坦-瓦济拉尼（Bernstein-Vazirani, BV）算法是展示量子并行性和干涉现象的典型量子算法。请详细阐述BV算法解决隐藏字符串问题的宏观原理，将其时间复杂度与经典算法进行对比，并深入剖析其实现量子加速的根本来源。在此基础上，请使用isQ语言编写一个完整的量子程序，用于求解隐藏字符串为 s = 1011 的BV问题。

### Reference answer

伯恩斯坦-瓦济拉尼（BV）算法旨在解决这样一个黑盒问题：给定一个黑盒函数 $f:\{0,1\}^n \rightarrow \{0,1\}$，该函数的计算规则为 $f(x) = s \cdot x \pmod 2$，其中 $s$ 是一个未知的 $n$ 比特二进制字符串，算法的目标是通过最少的查询来确定隐藏字符串 $s$。

**宏观原理与量子加速来源：**
BV算法的量子实现主要分为四个步骤：
1. 初始化：将 $n$ 个输入量子比特初始化为 $|0\rangle^{\otimes n}$，将1个输出辅助量子比特初始化为 $|1\rangle$。
2. 施加Hadamard变换：对所有 $n+1$ 个量子比特施加Hadamard门。输入寄存器将进入等概率的叠加态，而辅助量子比特进入 $| - \rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$ 状态。由于辅助比特的相位特性，函数 $f(x)$ 的作用将转化为对输入寄存器对应状态的相位翻转。
3. 调用黑盒预言机：量子预言机实现了 $U_f |x\rangle |y\rangle = |x\rangle |y \oplus f(x)\rangle$。在辅助比特为 $| - \rangle$ 的巧妙设置下，这等价于对那些满足 $s \cdot x = 1$ 的计算基态 $|x\rangle$ 进行了 $Z$ 门的相位翻转（即乘以 -1）。
4. 再次施加Hadamard变换：对输入寄存器进行第二次Hadamard变换。根据量子干涉原理，由于之前预言机造成的特定相位翻转，所有的干涉项会相互抵消或增强，最终输入寄存器的量子态会坍缩为 $|s\rangle$。测量后即可直接获得隐藏字符串 $s$。

**时间复杂度对比：**
在经典计算模型中，每一次对黑盒函数的查询只能获取 $s$ 中一个比特位的信息（例如输入 $0001$ 获取最低位，输入 $0010$ 获取次低位等）。因此，为了完全确定长度为 $n$ 的隐藏字符串 $s$ ，经典算法必须进行 $n$ 次独立的查询，其查询复杂度为 $O(n)$。
而量子BV算法利用量子叠加态，在单次调用预言机 $U_f$ 的过程中，实际上同时计算了所有 $2^n$ 个可能输入 $x$ 对应的函数值。随后通过量子干涉将隐藏信息提取到振幅中。因此，BV算法的查询复杂度仅为 $O(1)$。这种指数级的查询加速，其根本来源正是量子态的**叠加性**（允许并行计算）和量子门的**干涉效应**（将相位差转化为可测量的概率差）。

**isQ代码实现：**
针对隐藏字符串 $s = 1011$ （即 $s_0=1, s_1=1, s_2=0, s_3=1$），我们需要 4 个输入比特和 1 个辅助比特。预言机的实现通过受辅助比特控制的 CNOT 门来完成，仅当 $s$ 的对应位为 1 时，才在相应的输入比特与辅助比特之间作用 CNOT 门。

```isq
import std;

qbit q[4]; // 输入寄存器，对应x
qbit anc;  // 辅助寄存器，初始化为|1>并转为|->

procedure main() {
    // 1. 辅助比特初始化为 |1>
    X(anc);
    
    // 2. 对所有量子比特施加Hadamard门
    for i in 0:4 {
        H(q[i]);
    }
    H(anc);
    
    // 3. 实现黑盒预言机 U_f
    // 隐藏字符串 s = 1011
    // CNOT(q[i], anc) 的作用是：当 q[i] 为 1 时，翻转辅助比特的相位
    CNOT(q[0], anc); // s_0 = 1
    CNOT(q[1], anc); // s_1 = 1
    // s_2 = 0，不作用CNOT
    CNOT(q[3], anc); // s_3 = 1
    
    // 4. 对输入寄存器再次施加Hadamard变换进行逆傅里叶变换
    for i in 0:4 {
        H(q[i]);
    }
    
    // 5. 测量输入寄存器，预期结果应以 100% 概率坍缩为 1011
    for i in 0:4 {
        int r = M(q[i]);
    }
}
```

## isqTrain/1190

- task_id: `isqTrain/1190`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_inv`, `isq_syntax_multi_register`, `phase_manipulation`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `1869`

### Prompt

Code this in isQ: implements a variant of the phase_estimation pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The task is to write a reasoning section for a phase estimation circuit implemented in isQ.

Let me analyze The implementation:

1. Goal: Estimate the phase of the T gate using quantum phase estimation on 3 ancilla qubits.

2. The circuit uses 4 qubits total:
   - 3 ancilla qubits (anc[0], anc[1], anc[2]) for phase readout
   - 1 target qubit (target[0]) holding the eigenstate

3. State evolution:
   - Initial state: |0000>
   - X(target[0]): |0001> (prepare eigenstate |1> of T)
   - H on ancilla: (|0>+|1>)^3 ⊗ |1> / 2√2 = 1/(2√2)(|000>+|001>+|010>+|011>+|100>+|101>+|110>+|111>) ⊗ |1>
   - ctrl T(anc[0], target[0]): applies T^(2^0) = T when anc[0]=|1>
   - ctrl S(anc[1], target[0]): applies T^(2^1) = S when anc[1]=|1>
   - ctrl Z(anc[2], target[0]): applies T^(2^2) = Z when anc[2]=|1>
   
   The T gate has eigenvalue e^(iπ/4) for |1>. The phase is θ = 1/8.
   
   After controlled operations: 1/(2√2)(|000> + e^(iπ/4)|001> + e^(iπ/2)|010> + e^(i3π/4)|011> + e^(iπ)|100> + e^(i5π/4)|101> + e^(i3π/2)|110> + e^(i7π/4)|111>) ⊗ |1>

   Wait, I need to be careful about the bit ordering. In the reference, anc[0] controls T^1, anc[1] controls T^2=S, anc[2] controls T^4=Z.

   If I interpret anc[0] as the least significant bit, then state |k> (where k = 4*anc[2] + 2*anc[1] + anc[0]) picks up phase e^(2πi·k·θ) where θ = 1/8.

   So the state becomes: 1/(2√2) Σ_k e^(2πik/8) |k> ⊗ |1>

   This is the QFT of |1/8>, and applying inverse QFT should give |1> in binary = |100>.

4. The inverse QFT extracts the phase, yielding |100> with probability 1.

Now let me write the reasoning:

Actually, let me re-examine the qft_inv_3 procedure. It swaps q[0] and q[2], then does the standard inverse QFT. The procedure takes qbit q[5] but only uses q[0], q[1], q[2] (the first 3 elements of a 5-element array). Wait, actually it's called on anc which is anc[3], so it uses anc[0], anc[1], anc[2].

The swap (three-CNOT decomposition) at the beginning reverses the qubit order. Then the inverse QFT is applied.

After inverse QFT, the measurement should give |100> (which is 4 in decimal = binary 100).

The predicted output {|100>: 1.0}, meaning the measured bitstring is "100" which corresponds to anc[2]=1, anc[1]=0, anc[0]=0.

Let me reconsider the bit ordering for --probs mode. "earlier measured qubit = higher bit" means if we measure anc[0], anc[1], anc[2] in that order, then anc[0] is the highest bit. So |100> means anc[0]=1, anc[1]=0, anc[2]=0.

Hmm, but the phase of T gate on |1> is e^(iπ/4), so θ = 1/8. In 3-bit binary, 1/8 = 0.001. So we should measure 001, not 100.

Wait, but The predicted output {|100>: 1.0}. Let me reconsider.

The inverse QFT procedure includes a swap (three-CNOT decomposition) to reverse qubit order. This is standard in QFT implementations.

Actually, let me think more carefully. The QFT maps |k> → 1/√N Σ_j e^(2πijk/N) |j>. The inverse QFT does the reverse.

If the state after controlled operations is 1/√8 Σ_k

## isqTrain/2954

- task_id: `isqTrain/2954`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4270`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```isq
import std;
qbit q[2];
// 1-layer H+CNOT circuit on 2 qubits
procedure main() {
    H(q[0]);
    H(q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[1]);
    M(q[0]);
    M(q[1]);
}

```

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The second CNOT gate `CNOT(q[0], q[1])` has swapped control and target arguments. Both CNOT gates incorrectly use the same control (q[0]) and target (q[1]), when the second should have q[1] as control and q[0] as target to create a ring topology.

2. **Fix**: Change the second CNOT from `CNOT(q[0], q[1])` to `CNOT(q[1], q[0])`, swapping the control and target qubits.

3. **State evolution (corrected)**:
   - Initial: |00⟩
   - After H(q[0]), H(q[1]): (|00⟩+|01⟩+|10⟩+|11⟩)/2
   - After CNOT(q[0],q[1]): control=q[0

## isqTrain/4284

- task_id: `isqTrain/4284`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `98`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[3];

procedure main() {
    // Encode a = 2 (binary 10)
    X(q[1]);
    // Add constant 1: flip the LSB
    X(q[0]);
    // Now register = 3 (binary 11)
    // Overflow detection: set flag if both bits are 1 (value >= 3)
    Toffoli(q[0], q[1], q[2]);
    // Modular correction: subtract 3 by flipping both bits
    CNOT(q[2], q[0]);
    CNOT(q[2], q[1]);
    // Measure the 2-bit result: should be 0
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]);
    M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a concise step-by-step analysis of an isQ quantum program, predicting the measurement outcome probability distribution and explaining the state evolution. The output must start with "## Circuit Analysis".

2.  **Analyze the isQ program**:
    *   `qbit q[3];` -> 3 qubits initialized to $|000\rangle$ (q[0] is LSB, q[2] is MSB).
    *   `X(q[1]);` -> flips q[1]. State becomes $|010\rangle$ (binary 2).
    *   `X(q[0]);` -> flips q[0]. State becomes $|011\rangle$ (binary 3).
    *   `Toffoli(q[0], q[1], q[2]);` -> if q[0]==1 and q[1]==1, flip q[2]. Since q[0]=1 and q[1]=1, q[2] flips to 1. State becomes $|111\rangle$.
    *   `CNOT(q[2], q[0]);` -> if q[2]==1, flip q[0]. q[2]=1, so q[0] flips to 0. State becomes $|110\rangle$.
    *   `CNOT(q[2], q[1]);` -> if q[2]==1, flip q[1]. q[2]=1, so q[1] flips to 0. State becomes $|100\rangle$.
    *   `X(q[0]);` -> flips q[0]. State becomes $|101\rangle$.
    *   `M(q[0]); M(q[1]);` -> Measuring q[0] and q[1] gives 0 for both, but q[2] is still 1 (and implicitly measured or part of the output state since the system has 3 qubits).
    Wait, let's look at the "Expected measurement probabilities" in the prompt: `{|010>: 1.0}`? The predicted measurement probabilities says `{|010>: 1.0}` in the prompt's hidden reference. Let me re-read carefully.
    Wait, `Expected measurement probabilities: {|010>: 1.0}` - Wait, no. The reference says `Expected measurement probabilities: {|010>: 1.0}`.
    Let's re-evaluate the state carefully.
    Initial: `|000>`
    `X(q[1])` -> `|010>`
    `X(q[0])` -> `|011>`
    `Toffoli(q[0], q[1], q[2])` -> controls are q[0] and q[1], target is q[2]. Since q[0]=1, q[1]=1, q[2] flips to 1. -> `|111>`
    `CNOT(q[2], q[0])` -> control is q[2]=1, target is q[0]=1 -> q[0] flips to 0 -> `|110>`
    `CNOT(q[2], q[1])` -> control is q[2]=1, target is q[1]=1 -> q[1] flips to 0 -> `|100>`
    `X(q[0])` -> target q[0]=0 flips to 1 -> `|101>`.
    Wait. The reference says `{|010>: 1.0}`? Let me check if q[0] is MSB or LSB in the bitstring. In isQ, `M(q[0])` typically corresponds to bit 0. But in the prompt it says `M(q[0]); M(q[1]);`. If only `q[0]` and `q[1]` are measured, why is it `|010>`? Oh, maybe the reference text in the prompt is a generic template and `{|010>: 1.0}` was a typo or for a different version? No, the reference says "Expected measurement probabilities: {|010>: 1.0}".
    Wait. Let me trace it again.
    Start: 000
    X(q[1]) -> q[1] is 1. State: 010
    X(q[0]) -> q[0] is 1. State: 011
    Toffoli(q[0], q[1], q[2]) -> q[0]=1, q[1]=1, so q[2] flips. State: 111
    CNOT(q[2], q[0]) -> q[2]=1, so q[0] flips. q[0] was 1, now 0. State: 110
    CNOT(q[2

### Reference answer

{'predicted_probs': {'010': 1.0}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|010>) = 1.0000.'}

## isqTrain/2845

- task_id: `isqTrain/2845`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3073`

### Prompt

实现以下量子计算任务（使用isQ）：creates a entangled state with X on target. Use the appropriate sequence of gates on 2 qubits and measure both.

Requirements:
- Declare `qbit q[2];` at global scope.
- Use `procedure main()` as entry point.
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1.  **Goal**: Create a two-qubit entangled state, specifically the Bell state $\frac{1}{\sqrt{2}}(|01\rangle + |10\rangle)$, by applying an X gate to the target qubit after standard entanglement.
2.  **Qubits**: 2 qubits (`q[0]` and `q[1]`), both measured.
3.  **Evolution**:
    *   Start in $|00\rangle$.
    *   `H(q[0])`: Creates superposition $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
    *   `CNOT(q[0], q[1])`: Entangles qubits into $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$.
    *   `X(q[1])`: Flips the second qubit, resulting in $\frac{1}{\sqrt{2}}(|01\rangle + |10\rangle)$.
4.  **Probabilities**: Measurement yields 0.5 probability for $|01\rangle$ (decimal 1) and 0.5 for $|10\rangle$ (decimal 2).

## isqTrain/3595

- task_id: `isqTrain/3595`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `basis_change`
- source: `isq_train_cot`
- dataset_index: `3731`

### Prompt

Fix the bug in the following isQ program.

Bug description: Missing Hadamard gate

The program should Teleportation of |1> with correction gates.

### Chain-of-thought reasoning

The buggy code is missing the Hadamard gate on q[0] after the CNOT(q[0], q[1]) in the Bell measurement section. This H gate is necessary to complete the Bell basis measurement.

Let me trace through the corrected circuit:

1. Initial state: |000>
2. X(q[0]): |100>
3. H(q[1]): 1/√2(|100> + |110>)
4. CNOT(q[1], q[2]): 1/√2(|100> + |111>)

This is the state where q[0]=|1> and q[1],q[2] are in a Bell pair.

5. CNOT(q[0], q[1]): 1/√2(|110> + |101>)
6. H(q[0]): 1/√2(1/√2(|010> + |110>) + 1/√2(|001> - |101>))
   = 1/2(|010> + |110> + |001> - |101>)

7. CNOT(q[1], q[2]): 
   - |010> → |010> (q[1]=1, flips q[2]=0→1... wait, q[1] is the middle qubit)
   
   Wait, let me be more careful. Let me use the order q[0], q[1], q[2].

   State after H(q[0]): 1/2(|010> + |110> + |001> - |101>)
   
   where |q[0]q[1]q[2]>

   CNOT(q[1], q[2]): control=q[1], target=q[2]
   - |010>: q[1]=1, flip q[2]: |011>
   - |110>: q[1]=1, flip q[2]: |111>
   - |001>: q[1]=0, no flip: |001>
   - |101>: q[1]=0, no flip: |101>
   
   State: 1/2(|011> + |111> + |001> - |101>)

8. CZ(q[0], q[2]): control=q[0], target=q[2], applies Z to q[2] when q[0]=1
   - |011>: q[0]=0, no change: |011>
   - |111>: q[0]=1, Z on q[2]: -|111>
   - |001>: q[0]=0, no change: |001>
   - |101>: q[0]=1, Z on q[2]: -|101>
   
   State: 1/2(|011> - |111> + |001> + |101>)
   
   Hmm, let me reconsider. Wait, let me reconsider the CZ. CZ applies Z to the target when control is |1>. Z|0> = |0>, Z|1> = -|1>.
   
   - |011>: q[0]=0, no phase: |011>
   - |111>: q[0]=1, Z on q[2]=1: -|111>
   - |001>: q[0]=0, no phase: |001>
   - |101>: q[0]=1, Z on q[2]=1: -|101>
   
   State: 1/2(|011> - |111> + |001> - |101>)
   
   Hmm, that gives me 4 terms with equal magnitude 1/4 probability each. But The predicted output {|001>: 0.25, |011>: 0.25, |101>: 0.25, |111>: 0.25}.

   Let me recheck. The amplitudes have phases but the measurement probabilities are 0.25 each since |amplitude|^2 = (1/2)^2 = 1/4 for each term.

   Wait, but we have 4 terms each with amplitude 1/2, so probability = 1/4 each. That matches!

   Now, the measurement order: M(q[0]), M(q[1]), M(q[2]). Earlier measured qubit = higher bit.
   So the bitstring is q[0]q[1]q[2] where q[0] is the highest bit.
   
   The states |001>, |011>, |101>, |111> in binary where the first digit is q[0]:
   
   Wait, I need to think about what |abc> means. If I write |q[0]q[1]q[2]>, then:
   - |001>: q[0]=0, q[1]=0,

## isqTrain/550

- task_id: `isqTrain/550`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `entanglement`, `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_if_else`, `isq_syntax_multi_register`, `isq_syntax_print`, `mid_circuit_measurement`
- source: `isq_train_cot`
- dataset_index: `748`

### Prompt

帮我写一个isQ程序：implements a variant of the bell_state_preparation pattern using pool[3] -> pool[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Analyzing the circuit requirements, I need to understand what this circuit does:

1. We have a 5-qubit register `pool[5]` and a 3-qubit register `q[3]`
2. The circuit operates on `q[0]`, `q[1]`, `q[2]`
3. The `pool` qubits are never used - they're left in the ground state

Let me trace through the state evolution:

Initial state: |000⟩ for q[0], q[1], q[2]

After X(q[0]): |100⟩

After H(q[1]): |100⟩ ⊗ (|0⟩ + |1⟩)/√2 = (|100⟩ + |110⟩)/√2

After CNOT(q[1], q[2]): 
- When q[1] = |0⟩, q[2] stays |0⟩
- When q[1] = |1⟩, q[2] flips to |1⟩
So: (|100⟩ + |111⟩)/√2

After CNOT(q[0], q[1]):
- When q[0] = |1⟩ (both terms), q[1] flips
- |100⟩ → |110⟩
- |111⟩ → |101⟩
So: (|110⟩ + |101⟩)/√2

After H(q[0]):
H|1⟩ = |−⟩ = (|0⟩ - |1⟩)/√2

So:
(|010⟩ + |110⟩)/2 + (|001⟩ - |101⟩)/2

Hmm, let me reconsider. H(q[0]) acts on q[0]:
|110⟩ = |1⟩₀ ⊗ |1⟩₁ ⊗ |0⟩₂
After H on q[0]: (|0⟩₀ - |1⟩₀)/√2 ⊗ |1⟩₁ ⊗ |0⟩₂ = (|010⟩ - |110⟩)/√2

Wait, I'm getting confused with the bit ordering. Let me be more careful.

Let me use the notation |q[0], q[1], q[2]⟩

Initial: |0,0,0⟩

X(q[0]): |1,0,0⟩

H(q[1]): |1,0,0⟩ → |1⟩ ⊗ (|0⟩+|1⟩)/√2 ⊗ |0⟩ = (|1,0,0⟩ + |1,1,0⟩)/√2

CNOT(q[1], q[2]): 
- |1,0,0⟩ → |1,0,0⟩ (q[1]=0, no flip)
- |1,1,0⟩ → |1,1,1⟩ (q[1]=1, flip q[2])
Result: (|1,0,0⟩ + |1,1,1⟩)/√2

CNOT(q[0], q[1]):
Both terms have q[0]=1, so q[1] flips:
- |1,0,0⟩ → |1,1,0⟩
- |1,1,1⟩ → |1,0,1⟩
Result: (|1,1,0⟩ + |1,0,1⟩)/√2

H(q[0]):
H|1⟩ = (|0⟩ - |1⟩)/√2
So:
- |1,1,0⟩ → (|0,1,0⟩ - |1,1,0⟩)/√2
- |1,0,1⟩ → (|0,0,1⟩ - |1,0,1⟩)/√2

Result: (|0,1,0⟩ - |1,1,0⟩ + |0,0,1⟩ - |1,0,1⟩)/2

Now measure q[0] and q[1], with classical corrections on q[2]:

m1 = M(q[0])
m2 = M(q[1])

the predicted output given are for |000⟩, |011⟩, |100⟩, |111⟩. But wait, this is measuring 3 qubits according to the problem.

Looking at the predicted output: {|000>: 0.25, |011>: 0.25, |100>: 0.25, |111>: 0.25}

These are 3-bit strings. The circuit measures q[0] and q[1], then does corrections on q[2], then measures q[2].

Let me trace through the corrections:

State after H(q[0]): (|0,1,0⟩ - |1,1,0⟩ + |0,0,1⟩ - |1,0,1⟩)/2

Possible measurement outcomes for

## isqTrain/817

- task_id: `isqTrain/817`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3143`

### Prompt

Write isQ code for the following quantum task: implements a variant of the quadratic_form pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The goal is to implement a variant of the quadratic_form pattern using q[3] as the target instead of q[2], with an expanded qubit register of 5 qubits.

Analyzing the circuit requirements:
- q[0] and q[1] are put in superposition with H gates
- Toffoli gate computes AND of q[0] and q[1] into q[2]
- Measurements are on q[2], q[3], q[4]

But the task says "using q[3] -> q[5]", which means the Toffoli target should be q[3] instead of q[2], and we measure qubits q[3], q[4], q[5]... wait, no. Let me re-read.

Actually, looking at the predicted output: {|000>: 0.75, |100>: 0.25}

This means:
- 75% chance of measuring |000⟩
- 25% chance of measuring |100⟩

The measurement is on 3 qubits. In the reference, they measure q[2], q[3], q[4].

With the AND function (Toffoli on q[0], q[1], q[2]):
- |00⟩ on q[0],q[1] → q[2] = 0 (25%)
- |01⟩ on q[0],q[1] → q[2] = 0 (25%)
- |10⟩ on q[0],q[1] → q[2] = 0 (25%)
- |11⟩ on q[0],q[1] → q[2] = 1 (25%)

So measuring q[2] gives 0 with 75% and 1 with 25%. q[3] and q[4] are always 0.

The measurement bitstring has q[2] as the highest bit (measured first), so:
- |000⟩: 75%
- |100⟩: 25%

This matches the predicted output.

Now the task says "using q[3] -> q[5]". I think this means the Toffoli target should be q[3], and we measure q[3], q[4], and maybe q[5]... but wait, we only have 5 qubits (q[0] to q[4]).

Let me re-read: "q[3] -> q[5]" might mean using qubits from q[3] to q[5], i.e., 3 additional qubits. Or it could mean the Toffoli target is q[3].

Actually, looking more carefully at The implementation, it already has 5 qubits and measures q[2], q[3], q[4]. The task says "variant... using q[3] -> q[5]" which I interpret as: the Toffoli target should be q[3] instead of q[2], and measure q[3], q[4], and possibly q[5] or q[2].

Hmm, but if we change the target to q[3], and measure q[3], q[4], and q[2] (or some other ordering), we need to get {|000>: 0.75, |100>: 0.25}.

Wait, The predicted output the same. So the measurement probabilities should remain the same. Let me think about this differently.

If the Toffoli targets q[3] instead of q[2]:
- q[0], q[1] in superposition
- Toffoli(q[0], q[1], q[3]) computes AND into q[3]
- Measure q[3], q[4], and... what?

We need 3 measured qubits. If we measure q[2], q[3], q[4]:
- q[2] is always 0
- q[3] has the AND result
- q[4] is always 0

The bitstring would be: q[2] is highest bit, q[3] middle, q[4] lowest.

So measuring q[2]=0, q[3]=0, q[4]=0 → |000⟩ with prob... let me calculate.

After H(q[0]), H(q[1]):
State is |00⟩/2 + |01⟩/2 + |10⟩/2 + |11⟩/2 (unnormalized, with q[2]=q[3]=q[4]=0)

After Toffoli(q[0], q[1], q[3]):
- |00⟩|0⟩|0⟩ → |00000⟩ (q[0]=0, q[1]=0, q[2]=0, q[3]=0, q[4]=0)
- |01⟩|

## isqTrain/2681

- task_id: `isqTrain/2681`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_deriving_gate`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2524`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
defgate U0 = [
    1, 0, 0, 0, 0, 0, 0, 0;
    0, -1, 0, 0, 0, 0, 0, 0;
    0, 0, -1, 0, 0, 0, 0, 0;
    0, 0, 0, -1, 0, 0, 0, 0;
    0, 0, 0, 0, -1, 0, 0, 0;
    0, 0, 0, 0, 0, -1, 0, 0;
    0, 0, 0, 0, 0, 0, -1, 0;
    0, 0, 0, 0, 0, 0, 0, -1
];
oracle U_omega(3,1) = [0,1,0,0,0,0,0,0];
qbit q[3];
qbit anc;
int grover_search() {
    H(q);
    X(anc);
    H(anc);
    for i in 0:2 {
        U_omega(q[2], q[1], q[0], anc);
        H(q);
        U0(q[2], q[1], q[0]);
        H(q);
    }
    H(anc);
    X(anc);
    return M(q);
}
procedure main(){
    print grover_search();
}
```

### Chain-of-thought reasoning

The user wants to analyze an isQ quantum program and predict its measurement probability distribution.

The circuit applies Grover's search algorithm.
Number of qubits: 3 (plus 1 ancilla).
Oracle: `oracle U_omega(3,1) = [0,1,0,0,0,0,0,0];`
This means the marked state is the second element, which is |1> in binary (q[2]=0, q[1]=0, q[0]=1). Or simply |001> (which is 1).

Wait, isQ oracle syntax: `oracle U_omega(3,1) = [0,1,0,0,0,0,0,0];`
The first argument is number of qubits (3), second is number of marked states (1). The vector specifies the marked states. Here it's index 1.
So the target state is |001>.

Wait, the loop runs for 3 iterations: `for i in 0:2` (which means 0, 1, 2).
Wait, the optimal number of iterations for N=3 (8 states) is approximately pi/4 * sqrt(N/s) = pi/4 * sqrt(8) ≈ 2.2.
3 iterations is slightly too many.
Let's trace the state.

Initial state: |000>|1>
Ancilla: X(anc) -> H(anc) -> |->.
Main qubits: H(q) -> (|0>+|1>)^3 / sqrt(8) = |+>|+>|+> = uniform superposition.

Each Grover iteration:
1. Oracle U_omega. Flips the sign of |001>|-> to -|001>|->.
2. Diffusion operator: H(q), U0(q), H(q). U0 has 1 on 000, and -1 on everything else. Wait!
   U0 is:
   [1, 0, 0, 0, 0, 0, 0, 0;
    0, -1 ...
    0, 0, 0, 0, 0, 0, 0, -1]
   So U0 applies 1 to |000> and -1 to everything else.
   Wait, H U0 H is the standard Grover diffusion operator. It inverts about the average.
   Since U0 has +1 on 000 and -1 elsewhere, it's exactly the diffusion operator.

The algorithm runs 3 iterations.
Let angle theta = arcsin(1/sqrt(8)) ≈ 20.7 degrees.
After k iterations, the amplitude of the target state is sin((2k+1)theta).
For k=3, (2*3+1)theta = 7 * 20.7 = 144.9 degrees.
Wait, let's calculate exactly.
N = 8, M = 1.
theta = arcsin(1/sqrt(8)).
Amplitude of |001> = sin(7*theta).
Let's find cos(theta) = sqrt(7/8).

sin(2*theta) = 2 * 1/sqrt(8) * sqrt(7/8) = sqrt(14)/8.
cos(2*theta) = 7/8 - 1/8 = 6/8 = 3/4.

sin(3*theta) = sin(2*theta)cos(theta) + cos(2*theta)sin(theta)
= (sqrt(14)/8) * sqrt(7)/sqrt(8) + (3/4) * 1/sqrt(8)
= (7*sqrt(2) / 16) + 3 / sqrt(32) ?? Wait.
sqrt(14) * sqrt(7) = 7 * sqrt(2).
So it's 7*sqrt(2) / (8 * 2*sqrt(2)) + 3 / 4*sqrt(2) = 7/16 + 3/4*sqrt(2)
= 7/16 + 3*sqrt(2)/8. Wait, let me be precise.
sin(3*theta) = sqrt(14)/8 * sqrt(7/8) + 3/4 * sqrt(1/8) = 7/sqrt(64) / sqrt(8) + 3/4 / sqrt(8)
= 7/(16*sqrt(2)) + 3/(4*sqrt(8)) = 7/sqrt(128) + 3/sqrt(128) = 10/sqrt(128) = 10 / (8*sqrt(2)) = 5 / (4*sqrt(2)).
Wait, let me recalculate.
sin(3*theta) = 3*sin(theta) - 4*sin^

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

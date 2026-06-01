# ISQ training COT RAG corpus: quantum_algorithms shard 159

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1423

- task_id: `isqTrain/1423`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_ctrl_nctrl`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2556`

### Prompt

Implement the following in isQ: Apply the 3-qubit Quantum Fourier Transform to the input state |110> and measure all qubits.

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

Initial state: |000>

After X(q[0]) and X(q[1]):
State becomes |110> (q[0]=1, q[1]=1, q[2]=0)

Now apply 3-qubit QFT. The QFT acts on qubits in reverse order typically, but let me trace through the given gates:

Step 1: H(q[2])
|110> → |11+> = |11>(|0>+|1>)/√2 = (|110>+|111>)/√2

Step 2: ctrl S(q[1], q[2]) - controlled-S with q[1] as control, q[2] as target
Since q[1] is |1>, this applies S to q[2].
S|0>=|0>, S|1>=i|1>
So: (|110>+i|111>)/√2

Step 3: ctrl T(q[0], q[2]) - controlled-T with q[0] as control, q[2] as target
Since q[0] is |1>, this applies T to q[2].
T|0>=|0>, T|1>=e^(iπ/4)|1>
So: (|110>+i·e^(iπ/4)|111>)/√2 = (|110>+e^(iπ/4+iπ/2)|111>)/√2 = (|110>+e^(3iπ/4)|111>)/√2

Step 4: H(q[1])
This applies H to q[1].
|10> = |2>, |11> = |3> on qubits [1,2]
H on q[1]: |1> → (|0>-|1>)/√2

Let me be more careful. After step 3, the state is:
(|110>+e^(3iπ/4)|111>)/√2

= (1/√2)|1>|1>|0> + (e^(3iπ/4)/√2)|1>|1>|1>

H on q[1]: |1> → (|0>-|1>)/√2

= (1/√2)|1>[(|0>-|1>)/√2]|0> + (e^(3iπ/4)/√2)|1>[(|0>-|1>)/√2]|1>

= (1/2)|1>(|0>-|1>)|0> + (e^(3iπ/4)/2)|1>(|0>-|1>)|1>

= (1/2)(|100>-|110>+e^(3iπ/4)|101>-e^(3iπ/4)|111>)

Step 5: ctrl S(q[0], q[1]) - controlled-S with q[0] as control, q[1] as target
Since q[0] is always |1>, this applies S to q[1].
S|0>=|0>, S|1>=i|1>

State: (1/2)(|100>-i|110>+e^(3iπ/4)|101>-i·e^(3iπ/4)|111>)

Step 6: H(q[0])
H|1> = (|0>-|1>)/√2

State: (1/(2√2))(|0>-|1>)(|00>-i|10>+e^(3iπ/4)|01>-i·e^(3iπ/4)|11>)

Hmm, this is getting complex. Let me reconsider.

Actually, wait. The predicted output equal probability for all 8 states. That's |ψ> = (1/√8)Σ|x> for x in {0,...,7}.

The 3-qubit QFT of |110> = |6> should give:
QFT|6> = (1/√8)Σ_{k=0}^{7} e^(2πi·6·k/8)|k>

Let me compute the phases:
k=0: e^0 = 1
k=1: e^(2πi·6/8) = e^(3πi/2) = -i
k=2: e^(2πi·12/8) = e^(3πi) = -1
k=3: e^(2πi·18/8) = e^(9πi/2) = i
k=4: e^(2πi·24/8) = e^(6πi) = 1
k=5: e^(2πi·30/8) = e^(15πi/2) = -i

## isqTrain/4580

- task_id: `isqTrain/4580`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5376`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[5];

procedure main() {
    
    X(q[0]);
    
    X(q[2]);
    
    Toffoli(q[0], q[1], q[3]);
    
    Toffoli(q[0], q[2], q[4]);
    
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[3]);
    M(q[4]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Output prediction for an isQ program.
    *   Output format: "## Circuit Analysis" followed by step-by-step reasoning in Dirac notation, strictly 3-15 lines, ending with the predicted probability distribution.
    *   no code blocks. End with the exact distribution format expected.

2.  **Analyze the isQ Program:**
    *   `qbit q[5];` -> Initial state |00000>
    *   `X(q[0]);` -> Flips q[0]. State: |10000>
    *   `X(q[2]);` -> Flips q[2]. State: |10100>
    *   `Toffoli(q[0], q[1], q[3]);` -> Flips q[3] if q[0]=1 and q[1]=1. Here q[0]=1, q[1]=0. So no flip. State remains |10100>.
    *   `Toffoli(q[0], q[2], q[4]);` -> Flips q[4] if q[0]=1 and q[2]=1. Here q[0]=1, q[2]=1. So q[4] flips to 1. State: |10101>.
    *   `H(q[0]); Z(q[0]); H(q[0]);` -> Applies HZH to q[0]. Since HZH = X, this applies X to q[0]. q[0] was 1, flips to 0. State: |00101>.
    *   `M(q[3]); M(q[4]);` -> Measures q[3] and q[4].
    *   Since the state is purely |00101>, the measurement outcome is deterministic.
    *   Wait, is the final state |00101>? Let's trace carefully.
        *   qubits: q[0], q[1], q[2], q[3], q[4]
        *   init: 0, 0, 0, 0, 0
        *   X(q0): 1, 0, 0, 0, 0
        *   X(q2): 1, 0, 1, 0, 0
        *   Toffoli(q0, q1, q3): q0=1, q1=0 -> no change. 1, 0, 1, 0, 0
        *   Toffoli(q0, q2, q4): q0=1, q2=1 -> q4 flips. 1, 0, 1, 0, 1
        *   HZH = X on q0: q0 flips. 0, 0, 1, 0, 1.
        *   Final state: |00101>

3.  **Check Output Format Requirements:**
    *   "Expected measurement probabilities: {|00001>: 1.0} Number of qubits measured: 5" (Wait, the prompt says `Expected measurement probabilities: {|00001>: 1.0}` but wait, is the bitstring backwards or normal?)
    *   Let's read the prompt's circuit implementation closely:
        `Expected measurement probabilities: {|00001>: 1.0}`
        Number of qubits measured: 5.
        Wait, let's look at the qubit indexing in isQ. `q[0]` is usually the highest bit in bitstring `|q[4] q[3] q[2] q[1] q[0]>`?
        Let's check standard isQ or standard QC notation.
        In the prompt: "earlier measured qubit = higher bit".
        Wait, the prompt says:
        `--probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit).`
        Wait, `M(q[3]); M(q[4]);` - but the prompt implies all 5 qubits are measured in the global array? Or just the ones measured?
        Ah! "Number of qubits measured: 5" means the entire `qbit q[5]` register is tracked, but `M` is called on `q[3]` and `q[4]`. Wait, typically if only `M(q[3])` and `M(q[4])` are called, only 2 qubits are measured. But the reference says `{|00001>: 1.0}` which is a 5-qubit state.
        Actually, if `M(q[3])` and `M(q[4])` are measured, why does it say 5 qubits measured? Oh, `--probs` mode might simulate the

### Reference answer

{'predicted_probs': {'00001': 1.0}, 'explanation': 'This isQ program operates on 5 qubit(s). The measurement probability distribution is: P(|00001>) = 1.0000.'}

## isqTrain/3633

- task_id: `isqTrain/3633`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4812`

### Prompt

请用isQ语言编写一个量子电路：the 4-qubit QFT applied to input state |0000>. The circuit should use Hadamard gates, controlled-Rz rotations with angles 2π/2^k, and final bit-reversal swaps. Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Implement the 4-qubit Quantum Fourier Transform (QFT) on the initial state |0000> to generate a uniform superposition.
2. **Qubits & Measurement:** The circuit uses 4 qubits, all of which are measured to observe the final probability distribution.
3. **State Evolution:** Starting from |0000>, the Hadamard gates and controlled-Rz rotations generate the QFT state in bit-reversed order: $\frac{1}{4}(|0\rangle + |8\rangle + |4\rangle + \dots + |15\rangle)$. 
4. **Bit-Reversal:** The sequence of CNOT swaps between q[0]-q[3] and q[1]-q[2]

## isqTrain/99

- task_id: `isqTrain/99`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `320`

### Prompt

Write isQ code for the following quantum task: implements a variant of the bell_state_preparation pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants to implement a variant of the `bell_state_preparation` pattern using q[3] and q[5] (which means a 6-qubit register, or specifically involving q[3] and q[5], but the reference uses `qbit q[6]` maybe? Wait, the prompt says "using q[3] -> q[5]". Let's look at The implementation carefully. Reference: `qbit q[5];` Wait, the prompt says "q[3] -> q[5]". Actually, Analyzing the, the prompt might literally just want me to explaIn the implementation provided. The reference uses `qbit q[5];` and does quantum teleportation. Wait, The implementation explicitly has `qbit q[5]` and involves teleporting `|1>` on `q[0]` using EPR pair `q[1], q[2]`, and does a controlled Z from `q[0]` to `q[2]`. The reference output says `Expected measurement probabilities: {|00100>: 0.25, |01100>: 0.25, |10100>: 0.25, |11100>: 0.25}`. Wait, if it's teleporting `|1>`, and standard teleportation does Z then X, but this reference does CNOT then ctrl Z? Actually, the reference does `CNOT(q[1], q[2])` and `ctrl my_z(q[0], q[2])` (which is CZ(q[0], q[2])). Let's trace The implementation exactly, because the task is "Task type: code_generation" and the prompt is asking me to generate reasoning for the *circuit implementation*. Wait, usually I generate the reasoning that matches the predicted output, which is exactly The implementation.
    Wait, The implementation measures `q[0], q[1], q[2], q[3], q[4]` and The resulting probabilities should be `{|00100>: 0.25, |01100>: 0.25, |10100>: 0.25, |11100>: 0.25}`. Wait, if `q[0]` and `q[1]` are measured, `q[2]` is the teleported state. But the reference does `CNOT(q[1], q[2])` and `ctrl my_z(q[0], q[2])`. In standard teleportation, Bob does CNOT then CZ. Wait, the reference does `CNOT(q[1], q[2])` then `ctrl my_z(q[0], q[2])` which means CZ(q[0], q[2]).
    Let's trace The implementation state:
    Initial: |00000>
    X(q[0]) -> |10000>
    H(q[1]) -> |1>(q[0]) |+>(q[1]) |000>
    CNOT(q[1], q[2]) -> |100+00> = 1/sqrt(2) (|10000> + |10100>)
    CNOT(q[0], q[1]) -> 1/sqrt(2) (|11000> + |10100>)
    H(q[0]) -> 1/sqrt(2) (1/sqrt(2)(|010> + |110>) |000> + 1/sqrt(2)(|001> - |101>) |100>)
            = 1/2 (|01000> + |11000> + |00100> - |10100>)
    CNOT(q[1], q[2]) -> CNOT acts on q[1], q[2]. Let's write out the terms:
        |01000> -> |01100>
        |11000> -> |11100>
        |00100> -> |00100>
        |10100> -> |10100>
    So after CNOT(q[1], q[2]): 1/2 (|01100> + |11100> + |00100> - |10100>)
    ctrl my_z(q[0], q[2]) -> CZ on q[0], q[2]. Applies a phase of -1 if both are 1.
        |01100> -> q[0]=0, so no change.
        |11100> -> q[0]=1, q[2]=1 -> |11100> becomes -|11100>
        |00100> -> q[0]=0, no change.
        |10100> -> q[0]=1, q[2]=1 -> -|10100> becomes |10100>
    So the state is 1/2 (|01100

## isqQA/quantum_algorithms/127_optimization_variant

- task_id: `isqQA/quantum_algorithms/127_optimization_variant`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `optimization_variant`, `algorithm`, `量子隐形传态`
- source: `qa_pipeline`
- dataset_index: `3363`

### Prompt

量子隐形传态算法有哪些重要的改进版本或变体？请以受控量子隐形传态为例，说明其工作原理并给出核心电路的isQ代码实现。

### Reference answer

标准的量子隐形传态协议是量子信息学的基础，但它假设通信双方共享完美的最大纠缠态，且通常在两方之间进行。为了适应更复杂的现实应用场景，研究人员提出了多种重要的改进版本和变体。主要包括：1. 概率性隐形传态：当共享的非最大纠缠态时，通过引入辅助粒子和正定算符值测量（POVM），以一定的概率成功实现量子态的传输；2. 广义隐形传态：将信道从贝尔态扩展到任意维度的多粒子纠缠态，如使用GHZ态或W态作为量子信道；3. 受控量子隐形传态：在多方网络中引入控制方，只有在控制方同意并进行相应操作时，接收方才能成功恢复出传输的未知量子态。这种变体在量子秘密共享和量子安全通信中具有极高的应用价值。

以受控量子隐形传态为例，其工作原理在传统的三方模型中可以这样理解：Alice希望将一个未知量子态传给Bob，但他们共享的贝尔对是由第三方Charlie准备的。Charlie不仅可以准备纠缠对，还可以向系统中注入自己的控制粒子。在实际协议中，Alice完成Bell基测量后，并不会直接让Bob进行操作。Charlie必须先测量自己的控制粒子，并将经典结果发送给Bob。Bob只有在收到Charlie的“许可”指令后，结合Alice发来的经典信息，才能对目标粒子施加相应的Pauli门恢复原始态。如果没有Charlie的经典协助，Bob的粒子将保持混合态。

为了展示这一变体的核心逻辑，以下使用isQ语言实现一个简化的受控隐形传态量子电路模型。在这个模型中，我们用量子比特来等效模拟经典控制的延迟和条件执行。Charlie控制一个额外的量子比特，只有当该控制比特为1时，Bob端的恢复操作才会被执行。

import std;

qbit q[4]; // q[0]: Alice的未知态, q[1]: Alice的纠缠半比特, q[2]: Bob的纠缠半比特, q[3]: Charlie的控制比特

procedure main() {
    // 初始化待传输的未知量子态 (此处以 |1> 态为例)
    X(q[0]);
    
    // 初始化 Charlie 的控制比特，表示同意传输
    X(q[3]);
    
    // 创建 Alice 和 Bob 之间的 Bell 态纠缠信道
    H(q[1]);
    CNOT(q[1], q[2]);
    
    // Alice 端执行 Bell 基测量的等效酉操作
    CNOT(q[0], q[1]);
    H(q[0]);
    
    // Bob 端根据测量结果进行恢复，但这必须在 Charlie 的控制下进行
    // 使用 ctrl 语法，仅当 q[3] 处于 |1> 状态时，Bob 才执行恢复门操作
    ctrl @[q[3]] {
        CNOT(q[1], q[2]);
        CZ(q[0], q[2]);
    }
}

## isqTrain/2675

- task_id: `isqTrain/2675`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1907`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[2];

procedure main(){
    H(q[0]);
    CNOT(q[0],q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes two qubits, $q_0$ and $q_1$, to the state $|00\rangle$.
2. A Hadamard gate is applied to $q_0$, creating the superposition $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |0\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
3. A CNOT gate is applied with $q_0$ as the control and $q_1$ as the target. This entangles the qubits, flipping $q_1$ when $q_0$ is $|1\rangle$.
4. The final quantum state before measurement is the Bell state $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$.
5. Measurement of both qubits yields $|00\rangle$ with probability $0.5$ and $|11\rangle$ with probability $0.5$.

Probability distribution: [0.5, 0.0, 0.0, 0.5]

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/1198

- task_id: `isqTrain/1198`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1568`

### Prompt

Write an isQ program that implements a variant of the qaoa pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Step 1: Analyze the Request
- Goal: Write a QAOA variant using q[2] to q[4], requiring an expanded qubit register. The circuit should a 4-qubit register (q[4]), applying QAOA p=1 to q[0] and q[1] (for MaxCut on 2 nodes) and leaving q[2] and q[3] in the |0> state.
- Wait, the prompt says "using q[2] -> q[4]". This usually implies declaring `qbit q[5];` if 0-indexed, or maybe it means using q[2] up to q[4] *inclusive*, which is 3 qubits. But the prompt says "using q[2] -> q[4]". Let me re-read carefully: "variant of the qaoa pattern using q[2] -> q[4]". If it means indices 2, 3, 4, then I need `qbit q[5];` and apply gates to q[2] and q[3], and leave q[0], q[1], q[4] in |0>?
- Let's look at the "circuit implementation". The circuit should `qbit q[4];` and applies QAOA to q[0] and q[1].
- Wait! "The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state."
- If the prompt implies an adaptation of The implementation, maybe I need to apply QAOA to q[2] and q[3], and declare `qbit q[5];` (so indices 0,1,2,3,4). Then I measure all qubits. But wait, the predicted output for The implementation are `|0000>: 0.073...`, meaning 4 qubits are measured.
- Ah, the task is *code generation* but the output I need to generate is ONLY the reasoning section.
- Let's check the predicted output for the *target* circuit.
- Wait, the prompt says: "Generate a reasoning section that explains: ... 1. The goal... 2. How many qubits... 3. Step-by-step... 4. Why expected probs...". I just need to generate the reasoning section based on the prompt and circuit implementation. Wait, the prompt provides the circuit implementation! "circuit implementation (isQ code): ... Expected measurement probabilities: ... Number of qubits measured: 4".
- Wait, the prompt specifically asks me to write a reasoning section that explains the *circuit implementation*? Or a reasoning section for the requested circuit ("Write an isQ program that implements a variant of the qaoa pattern using q[2] -> q[4]").
- Let me read the prompt again: "Generate a reasoning section that explains...".
- If The implementation is for a 4-qubit system (indices 0, 1, 2, 3), where QAOA is applied to q[0] and q[1], but the *prompt* asks for "a variant of the qaoa pattern using q[2] -> q[4]", this might mean a 5-qubit system (indices 0, 1, 2, 3, 4) where QAOA is applied to q[2] and q[3].
- Wait, if it's 5 qubits, then `|00000>: ...`.
- Let me look closely at the "Expected measurement probabilities: {|0000>: 0.073..., |0100>: 0.426...}". This is exactly 4 qubits. The bitstring is big-endian (earlier measured qubit = higher bit).
- If the prompt asks me to "Write an isQ program that implements a variant...", but then gives me The implementation and expected probabilities for a *4-qubit register*, maybe The implementation *is* the answer to the prompt? No, The circuit should QAOA to q[0], q[1]. The prompt asked for "using q[2] -> q[4]".
- Wait, maybe the prompt means "using `qbit q[2]` to `q[4]`"? No, "q[2] -> q[4]".
- Let's assume the circuit in the circuit implementation is what I'm supposed to explain, because the Expected Probabilities exactly match the circuit implementation!
  - In circuit implementation:
  - `H(q[0]); H(q[1]);` -> state is `|+>|+>|0>|0>`
  - `CNOT(q[0], q[1]); Rz(-pi/4, q[1]); CNOT(q[0], q[1]);`
  - `

## isqExpand/algo/13

- task_id: `isqExpand/algo/13`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `qft`, `fourier_transform`, `quantum_speedup`
- source: `qa_pipeline`
- dataset_index: `1505`

### Prompt

什么是量子傅里叶变换（QFT）？它和经典的离散傅里叶变换有什么关系？为什么QFT可以在量子计算机上高效实现？

### Chain-of-thought reasoning

## 推理
目标：解释QFT的定义、与DFT的关系、以及高效性原因。

关键点：
1. QFT是DFT的量子版本，作用在量子态振幅上
2. 经典DFT：O(N log N), QFT：O((log N)²)——指数加速
3. 高效性来自于可分解为O(n²)个基本门
4. 不能直接读取傅里叶系数，但作为子程序极其重要

### Reference answer

## 量子傅里叶变换（QFT）

### 定义
QFT是经典离散傅里叶变换（DFT）在量子态上的对应。对n-qubit态：

QFT|j> = (1/√N) Σ_k e^(2πijk/N) |k>,  其中 N=2^n

### 与经典DFT的关系
- DFT作用在长度N的向量上，复杂度O(N log N)（FFT）
- QFT作用在N维量子态的振幅上，复杂度O(n²) = O((log N)²)
- 两者执行相同的数学变换，但QFT是指数级加速

### 为什么QFT高效

关键在于**量子并行性和可分解性**：

1. QFT可以分解为逐比特操作：
   - 对第j个qubit应用H门
   - 对第j和第k个qubit应用受控旋转 R_k (角度 2π/2^k)
2. 总共需要 n个H门 + n(n-1)/2个受控旋转 = O(n²)个门
3. 每个门操作同时作用于所有2^n个振幅（量子并行性）

### 注意事项
- QFT本身不直接给出傅里叶系数（测量会塌缩）
- 它的价值在于作为子程序：QPE、Shor算法等都依赖QFT
- 逆QFT (QFT†) 通过反转门序列并取共轭实现

### isQ中的2-qubit QFT
```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]);
    ctrl @[q[1]] S(q[0]);
    H(q[1]);
    M(q[0]); M(q[1]);
}
```

## isqTrain/1392

- task_id: `isqTrain/1392`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5160`

### Prompt

Write isQ code for the following quantum task: the Bernstein-Vazirani algorithm to find the secret string s = 101 (MSB first). Use 3 input qubits and 1 ancilla.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement Bernstein-Vazirani to find secret string s=101 via phase oracle and Hadamard transforms.
Qubits: 3 input (q[0-2]) + 1 ancilla (anc[0]); measure only input qubits.

State evolution:
1. Initial |000>|0> → X(anc[0]) → |000>|1>
2. H(anc[0]) → |000>|-> (phase kickback target ready)
3. H(q[0,1,2]) → 1/√8 Σ_x |x>|-> where x ∈ {0,1}³
4. Oracle CNOT(q[0],anc[0])·CNOT(q[2],anc[0]) applies (-1)^(s·x) phase since ancilla is |->, yielding 1/√8 Σ_x (-1)^(101·x)|x>|-> (bits s₀=1,s₁=0,s₂=1)
5. H(q[0,1,2]) on input register: H^⊗n Σ_x (-1)^(s·x)|x> = |s> = |101>|->

Expected: {|101>: 1.0} because H^⊗n transforms the phase-encoded secret string into the computational basis state |s>.

## isqTrain/4094

- task_id: `isqTrain/4094`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4737`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[4];

unit grover_oracle(qbit q[4]) {
    X(q[1]);
    ctrl<2> CZ(q[0], q[1], q[2], q[3]);
    X(q[1]);
} deriving gate

unit grover_diffusion(qbit q[4]) {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    X(q[3]);
    ctrl<2> CZ(q[0], q[1], q[2], q[3]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    X(q[3]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
} deriving gate

procedure main() {
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    for i in 0:3 {
        grover_oracle(q);
        grover_diffusion(q);
    }
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

Let me analyze this Grover's algorithm circuit step by step.

First, let me understand the oracle. The oracle marks a specific state by flipping its phase. Let's trace what state it marks:

The oracle does:
1. X(q[1]) - flips qubit 1
2. ctrl<2> CZ(q[0], q[1], q[2], q[3]) - this is a multi-controlled Z gate with 2 control qubits and 2 target qubits. Wait, let me re-read the syntax.

Actually, `ctrl<2> CZ(q[0], q[1], q[2], q[3])` - this syntax with `ctrl<2>` means apply CZ with 2 additional control qubits. So q[0] and q[1] are controls, and CZ is applied to q[2] and q[3]. This means: when q[0]=1 AND q[1]=1, apply CZ to q[2] and q[3].

The CZ gate applies a -1 phase when both target qubits are |1>. So the full condition is: q[0]=1, q[1]=1, q[2]=1, q[3]=1.

But wait, there's X(q[1]) before and after. So when q[1]=0 originally, after X(q[1]) it becomes 1. So the oracle flips the phase of states where q[0]=1, q[1]=0, q[2]=1, q[3]=1.

So the marked state is |1011⟩.

Now let me think about Grover's algorithm with 4 qubits and 1 marked state.

With N = 2^4 = 16 states and M = 1 marked state, the optimal number of iterations is approximately π/4 * sqrt(N/M) = π/4 * 4 = π ≈ 3.14.

The circuit runs 4 iterations (for i in 0:3 means i = 0, 1, 2, 3, so 4 iterations).

After 4 iterations, the probability of measuring the marked state won't be exactly 1, but it will be close. Let me calculate more precisely.

The Grover angle θ satisfies sin(θ) = 1/√N = 1/4.

After k iterations, the probability of measuring the marked state is sin²((2k+1)θ).

With k=4 iterations:
- θ = arcsin(1/4) ≈ 0.2527 rad
- (2k+1)θ = 9 × 0.2527 ≈ 2.274 rad
- sin²(2.274) ≈ sin²(2.274)

sin(2.274) ≈ 0.7568
sin²(2.274) ≈ 0.5727

So about 57.3% probability of measuring |1011⟩.

Wait, let me recalculate more carefully.

θ = arcsin(1/√16) = arcsin(1/4)

Let me compute this more precisely:
arcsin(0.25) ≈ 0.25268 rad

After k=4 iterations:
(2×4+1) × θ = 9 × 0.25268 ≈ 2.2741 rad

sin(2.2741) ≈ sin(2.2741)
2.2741 rad ≈ 130.28°
sin(130.28°) = sin(180° - 130.28°) = sin(49.72°) ≈ 0.7629

sin²(2.2741) ≈ 0.5820

So approximately 58.2% probability of measuring the marked state |1011⟩.

The remaining ~41.8% is distributed uniformly among the other 15 states, each with probability ≈ 41.8%/15 ≈ 2.79%.

So the most likely measurement outcome is |1011⟩, which in bitstring form (with q[0] as the highest bit) would be 1011 = 11 in decimal.

Wait, let me reconsider the `ctrl<2> CZ` syntax. In isQ, `ctrl<2>` means adding 2 control qubits. The CZ gate takes 2 qubits (control and target). With `ctrl<2>`, we add 2 more controls, making it 4 qubits total. The original CZ has q[2] as control and q[3] as target (or both as targets of Z?). 

Actually, CZ is a two-qubit gate. With `ctrl<2>`, we add 2 control qubits. So q[0] and q

### Reference answer

Deterministic output: state |1011> with probability ~0.96

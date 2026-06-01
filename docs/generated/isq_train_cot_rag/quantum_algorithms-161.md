# ISQ training COT RAG corpus: quantum_algorithms shard 161

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/665

- task_id: `isqTrain/665`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `multi_controlled_logic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4810`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;

qbit q[2];

procedure main() {
    H(q[0]);
    ctrl X(q[0], q[1]);
    nctrl X(q[0], q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial State:** The circuit begins with 2 qubits in the state $|00\rangle$.
2. **Hadamard (H(q[0])):** Applies a Hadamard gate to $q[0]$, evolving the state to an equal superposition: $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
3. **Controlled-X (ctrl X(q[0], q[1])):** Flips $q[1]$ from $|0\rangle$ to $|1\rangle$ only when $q[0]$ is $|1\rangle$. This creates a Bell state: $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$.
4. **Negative-Controlled-X (nctrl X(q[0], q[1])):** Flips $q[1]$ from $|0\rangle$ to $|1\rangle$ only when $q[0]$ is $|0\rangle$. The state evolves to: $\frac{1}{\sqrt{2}}(|01\rangle + |11\rangle)$. 
5. **Measurement:** The qubits are measured, collapsing the superposition.

Predicted probability distribution: {|01>: 0.5, |11>: 0.5}

### Reference answer

{'predicted_probs': {'1': 0.5, '3': 0.5}, 'explanation': 'Parametric variant of isqHumanEval/218. Dimension: predict probabilities for reference circuit.'}

## isqTrain/954

- task_id: `isqTrain/954`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `hamiltonian_simulation`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4612`

### Prompt

请用isQ语言编写一个量子电路：implements the pauli_evolution pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement Pauli-Z evolution on a qubit, sandwiched between Hadamards, with an explicit X-X identity pair before measurement.
2. **Qubits**: 1 qubit (`q[0]`), measured at the end.
3. **State evolution**:
   - Initialize: `|0⟩`
   - `H(q[0])`: `|0⟩ → |+⟩ = (1/√2)(|0⟩ + |1⟩)`
   - `Rz(π/2, q[0])`: Applies `e^(-iπ/4)` to `|0⟩` and `e^(iπ/4)` to `|1⟩`, yielding `(1/√2)(e^{-iπ/4}|0⟩ + e^{iπ/4}|1⟩)`
   - `H(q[0])`: Converts phase difference to amplitude: `→ (1/√2)|0⟩ - (i/√2)|1⟩`
   - `X(q[0])` twice: X·X = I (identity), state unchanged
4. **Expected probabilities**: `P(|0⟩) = |1/√2|² = 0.5`, `P(|1⟩) = |-i/√2|² = 0.5` — the X-X pair cancels to identity, leaving an equal superposition.

## isqTrain/2923

- task_id: `isqTrain/2923`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5318`

### Prompt

Create an isQ quantum circuit that applies a controlled Rz rotation of 1*pi/8 radians. Put the control qubit in superposition with H, set the target to |1>, apply controlled Rz, then H on the control. Measure both.

Requirements:
- Declare `qbit q[2];` at global scope.
- Use `procedure main()` as entry point.
- Measure both qubits.

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

Initial state: |00⟩

1. H(q[0]): Puts q[0] in superposition
   State: (|00⟩ + |10⟩)/√2

2. X(q[1]): Flips q[1]
   State: (|01⟩ + |11⟩)/√2

3. ctrl Rz(π/8, q[0], q[1]): Applies Rz(π/8) to q[1] when q[0] is |1⟩
   Rz(θ) = [[1, 0], [0, e^(iθ)]]
   Rz(π/8) = [[1, 0], [0, e^(iπ/8)]]
   
   State: (|01⟩ + e^(iπ/8)|11⟩)/√2

4. H(q[0]): Apply H to q[0]
   |01⟩ → (|01⟩ + |11⟩)/√2
   |11⟩ → (|01⟩ - |11⟩)/√2
   
   So: (1/√2) × [(|01⟩ + |11⟩)/√2 + e^(iπ/8)(|01⟩ - |11⟩)/√2]
   = (1/2)[(1 + e^(iπ/8))|01⟩ + (1 - e^(iπ/8))|11⟩]

5. Probabilities:
   P(|01⟩) = |(1 + e^(iπ/8))/2|² = (1/4)|1 + e^(iπ/8)|²
   P(|11⟩) = |(1 - e^(iπ/8))/2|² = (1/4)|1 - e^(iπ/8)|²

   |1 + e^(iπ/8)|² = (1 + cos(π/8))² + sin²(π/8) = 1 + 2cos(π/8) + cos²(π/8) + sin²(π/8) = 2 + 2cos(π/8)
   
   P(|01⟩) = (2 + 2cos(π/8))/4 = (1 + cos(π/8))/2 = cos²(π/16)
   
   cos(π/16) ≈ 0.980785
   cos²(π/16) ≈ 0.96194
   
   Hmm, Let me verify the output: {|01>: 0.9903926441862724, |11>: 0.00960735581372758}

   0.9903926441862724 ≈ cos²(π/16)? No, that's about 0.9619.

   Let me recalculate. π/8 = 0.392699...
   
   Wait, let me check: 1 + cos(π/8) = 1 + cos(22.5°) = 1 + 0.92388 = 1.92388
   P(|01⟩) = 1.92388/2 = 0.96194

   But expected is 0.9903926...

   Let me check if maybe the Rz angle should be pi/16 or something else.

   cos²(π/16) = cos²(11.25°) = 0.980785² = 0.96194
   
   Hmm, 0.9903926441862724... Let me check cos²(π/32):
   cos(π/32) ≈ cos(5.625°) ≈ 0.99518
   cos²(π/32) ≈ 0.99039

   So the angle seems to be π/16, not π/8.

   But the problem says "1*pi/8 radians" and the code says Rz(0.392699, q[0], q[1]).

   0.392699 ≈ π/8

   Let me recalculate more carefully.

   Actually wait. Let me re-analyze the output. It says:
   {|01>: 0.9903926441862724, |11>: 0.00960735581372758}

   And these sum to 1.0.

   Let me check: cos²(π/16) = ?
   π/16 = 0.1963495...
   cos(0.1963495) = 0.980785...
   cos²(

## isqTrain/3520

- task_id: `isqTrain/3520`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `basis_change`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1333`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```
import std;

qbit q[1];

procedure main() {
    H(q[0]);
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes a single qubit q[0] to the ground state |0>.
2. The first Hadamard gate (H) evolves the state into an equal superposition: |+> = (1/sqrt(2))|0> + (1/sqrt(2))|1>.
3. The second Hadamard gate is applied. Since H is its own inverse (H*H = I), it maps the |+> state back to the original basis state |0>. 
4. The measurement M(q[0]) measures the qubit in the computational basis. Since the final state is exactly |0>, the result is deterministic.

Predicted probability distribution: {|0>: 1.0}

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'The output is |0> with probability 1.0'}

## isqQA/quantum_algorithms/88_hardware_limitations

- task_id: `isqQA/quantum_algorithms/88_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `hardware_limitations`, `algorithm`, `DJ算法的Oracle构造`
- source: `qa_pipeline`
- dataset_index: `262`

### Prompt

在Deutsch-Jozsa (DJ) 算法中，理论上只需一次Oracle查询就能以100%的概率完美区分常数函数和平衡函数。然而，在当前的含噪声中等规模量子 (NISQ) 设备上运行时，算法的成功率往往会随着输入比特数 $n$ 的增加而急剧下降。请从硬件局限性（特别是退相干时间和量子门保真度）的角度，深入分析导致DJ算法在真实物理设备上失效的根本原因。此外，请使用isQ语言编写一个针对3比特输入的DJ算法完整程序，其中包含一个特定的平衡Oracle，并结合该代码进一步讨论在实际硬件执行时可能面临的误差累积问题。

### Reference answer

<think />

1. **理论背景与数学分析**：
理想情况下，DJ算法将 $n$ 个输入量子比特初始化为 $|0\rangle^{\otimes n}$，辅助比特初始化为 $|1\rangle$。经过 $H^{\otimes n+1}$ 变换后，系统进入叠加态。接着调用Oracle $U_f$，其作用为 $|x\rangle|y\rangle \rightarrow |x\rangle|y \oplus f(x)\rangle$。对于平衡函数，相位反转导致随后的 $H^{\otimes n}$ 变换使得 $|0\rangle^{\otimes n}$ 的概率幅为0。因此，测量输入比特全为0的概率为0，必定能识别出平衡函数。

2. **NISQ硬件局限性与退相干影响**：
在实际的超导或离子阱量子计算机中，量子比特并非完全孤立，而是与环境发生耦合。
*   **退相干时间（$T_1, T_2$）**：量子态存在能量弛豫时间 $T_1$ 和相位退相干时间 $T_2$。DJ算法在执行前需要大量的Hadamard门，执行中需要深度的Oracle电路，执行后还需要一层Hadamard门。如果整个电路的执行时间接近甚至超过 $T_1$ 和 $T_2$，完美干涉所需的相位信息就会丢失，导致计算结果退化为随机噪声。
*   **量子门保真度与串扰**：特别是双比特门（如CNOT或CZ），其错误率通常是单比特门的10到100倍。构造复杂的平衡Oracle往往需要多个受控非门（控制比特随着 $n$ 的增加而增多）。这些双比特门不仅自身带有操作误差，还会在并发的量子操作中引发寄生耦合（串扰），导致计算结果严重失真。这就是为什么在真实硬件上，随着 $n$ 增大，测量结果中 $|000\rangle$ 的概率不会是0，而是被噪声基底大幅抬升。

3. **isQ代码实现与分析**：
构造一个3比特输入的平衡Oracle（例如 $f(x) = x_0 \oplus x_1$），这意味着只有当第0位和第1位比特异或为1时，辅助比特翻转。等效于对前两个比特执行CNOT操作。
</think />

在理论上，Deutsch-Jozsa算法利用了量子态的叠加与干涉原理，展现出相对于经典算法的指数级加速。然而，这种完美的确定性结果建立在封闭量子系统理想幺正演化的前提之上。在当前NISQ（含噪声中等规模量子）设备上，算法的失效主要源于硬件的物理局限性与噪声的干扰：

首先，**退相干效应**是最大的物理阻碍。量子比特极其脆弱，其相干状态会随时间指数级衰减。能量弛豫时间（$T_1$）限制了量子比特保持 $|1\rangle$ 状态的时长，而相位退相干时间（$T_2$）限制了不同能级之间相对相位关系的保持能力。DJ算法要求系统在执行初始Hadamard门、深层Oracle门以及最终Hadamard门的整个过程中保持完美的相位相干。一旦电路深度过大导致运行时间接近 $T_1$ 或 $T_2$，量子态的干涉条纹就会被抹平，原本应该发生相消干涉（全0状态概率为0）的平衡函数，其测量结果会退化为均匀分布的随机噪声，从而使得算法失去确定性的判别能力。

其次，**量子门保真度不足**是直接推手。NISQ设备中的双比特量子门（如CNOT、CZ）错误率通常远高于单比特门。随着输入规模 $n$ 的增加，Oracle的构造往往需要引入更多的多控门或级联的双比特门。这些高错误率的门级联后，会导致误差呈指数级累积。此外，多个量子比特同时操作时还会引发量子的串扰误差，进一步破坏本就脆弱的量子态。

以下展示如何在isQ语言中实现一个3比特输入的DJ算法及其平衡Oracle。该Oracle被设计为平衡函数 $f(x) = x_0 \oplus x_1$，即输入的前两位异或值为1时，辅助比特翻转：

```isq
import std;

// 声明4个全局量子比特，前3个(q[0]-q[2])为输入，最后1个(q[3])为辅助比特
qbit q[4];

procedure main() {
    // 1. 初始化辅助比特为 |1⟩
    X(q[3]);
    
    // 2. 对所有量子比特应用Hadamard门，进入叠加态
    for i in 0:4 {
        H(q[i]);
    }
    
    // 3. 构造并应用平衡 Oracle (f(x) = x0 XOR x1)
    // 这里利用两个CNOT门实现异或逻辑并写入辅助比特
    CNOT(q[0], q[3]);
    CNOT(q[1], q[3]);
    
    // 4. 对输入比特再次应用Hadamard门进行干涉
    for i in 0:3 {
        H(q[i]);
    }
    
    // 5. 测量前3个输入比特
    // 在理想情况下，因为是平衡函数，这3个比特的测量结果绝对不可能全为 '000'
    for i in 0:3 {
        M(q[i]);
    }
}
```

在上述isQ代码的实际硬件执行中，我们面临着严重的**误差累积问题**。在这个看似简单的3比特电路中，包含了初始化X门、8个Hadamard门以及2个CNOT门。虽然逻辑上CNOT门是并发的概念，但在硬件拓扑结构中往往需要通过额外的SWAP操作来连接非相邻的物理比特。假设每个双比特CNOT门的保真度为98%，两个CNOT就会将整体的成功率降低到约96%。加上退相干带来的热噪声衰减，最终测量结果中“000”状态的概率会被噪声基底（Noise Floor）显著抬高。当输入规模扩展到几十个比特时，所需的Oracle电路深度将导致整个系统退相干，这就是为什么DJ算法在NISQ时代主要作为理论验证，而难以在复杂任务中发挥实际效用的根本原因。

## isqTrain/3048

- task_id: `isqTrain/3048`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_if_else`, `measurement_order`, `mid_circuit_measurement`
- source: `isq_train_cot`
- dataset_index: `5461`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
bool flag;
qbit q[2];
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    flag = M(q[0]);
    if (flag) {
        X(q[1]);
    }
    M(q[1]);
}
```

### Chain-of-thought reasoning

Step 1: H(q[0]) creates superposition |+0> = (|00> + |10>)/sqrt(2).
Step 2: CNOT(q[0], q[1]) entangles them into the Bell state (|00> + |11>)/sqrt(2).
Step 3: M(q[0]) collapses the state. If q[0] is |0>, q[1] is |0>. If q[0] is |1>, q[1] is |1>.
Step 4: The classical flag stores the outcome.
Step 5: If flag is 1 (true), X(q[1]) flips q[1] from |1> to |0>.
Step 6: Regardless of the initial collapse, q[1] is now in state |0>.
Step 7: M(q[1]) always yields 0.
Step 8: The final 2-bit string is always 00 (flag=0, M(q[1])=0) or 10 (flag=1, M(q[1])=0).
Wait, let me re-read the rules for `--probs` output.
"--probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit)."
So the first measured qubit (`flag=M(q[0])`) is the higher bit, and the second (`M(q[1])`) is the lower bit.
The program has two measurements: `flag = M(q[0]);` and `M(q[1]);`.
If `q[0]` measures 0 (probability 0.5), the state is |00>. No X gate. M(q[1]) is 0. The bitstring is "00".
If `q[0]` measures 1 (probability 0.5), the state is |11>. X gate is applied to q[1]. q[1] becomes |0>. M(q[1]) is 0. The bitstring is "10".
So the probabilities are:
00: 0.5
01: 0.0
10: 0.5
11: 0.0
Wait, The implementation says: "Expected measurement probabilities: {'00': 0.5, '11': 0.5}"
Let me re-read The implementation. Is it possible it doesn't support mid-circuit measurement in the reference or is a trick?
"Expected measurement probabilities: {'00': 0.5, '11': 0.5}"
Wait, if `M(q[0])` is the *only* measurement considered for the final output, or perhaps `M(q[1])` at the end is ignored? Or if all measurements are concatenated, but `M(q[1])` wasn't measured?
Ah, wait. If the output is for 2 qubits, and M(q[1]) is 0.
Let's look at the reference: `{'00': 0.5, '11': 0.5}`. This means the final state measured is 00 or 11.
But the code applies X(q[1]) if flag is true!
Why would it be 00 and 11?
Could `flag = M(q[0]);` just be a classical variable and does NOT collapse the state? No, `M(q[i])` is a measurement.
Wait, what if The implementation assumes the measurement `M(q[1])` is NOT happening or not considered?
If `M(q[1])` is not considered, the bitstring is just `M(q[0])`.
But it has two qubits, so bitstring is 00 or 11? That makes no sense.
Let's carefully trace:
Initial: |00>
H(q[0]) -> (|00> + |10>)/sqrt(2)
CNOT(q[0], q[1]) -> (|00> + |11>)/sqrt(2)
M(q[0]) -> 0 with prob 0.5 (state |00>), 1 with prob 0.5 (state |11>)
if flag: X(q[1])
If 0: state is |00>. X is not applied.
If 1: state is |11>. X is applied to q[1]. State becomes |10>.
So the state before M(q[1]) is |00> or |10>.
Then M(q[1]) yields 0. The bitstrings are 00 and 10.
Why does the reference say `{'00': 0.5, '11': 0.5}`?
Wait. The reference says: `Expected measurement probabilities: {'00': 0.5, '11': 0.5}`.
Did the reference accidentally not include the X(q[1])? Or maybe `M(q[1])` is the *only*

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3534

- task_id: `isqTrain/3534`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `basis_change`, `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `3639`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```
import std;

qbit q[8];
qbit r[1];

procedure main() {
    CNOT(q[0], q[3]);
    CNOT(q[0], q[6]);
    H(q[0]); H(q[3]); H(q[6]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    CNOT(q[3], q[4]);
    CNOT(q[3], q[5]);
    CNOT(q[6], q[7]);
    CNOT(q[6], r[0]);

    CNOT(q[6], r[0]);
    CNOT(q[6], q[7]);
    CNOT(q[3], q[5]);
    CNOT(q[3], q[4]);
    CNOT(q[0], q[2]);
    CNOT(q[0], q[1]);
    H(q[6]); H(q[3]); H(q[0]);
    CNOT(q[0], q[6]);
    CNOT(q[0], q[3]);

    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]); M(q[5]); M(q[6]); M(q[7]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis

1. **Operations**: The circuit performs a Steane code encode-decode cycle. It encodes via CNOT(q[0],q[3]), CNOT(q[0],q[6]), H on q[0],q[3],q[6], then fan-out CNOTs: q[0]→q[1],q[2]; q[3]→q[4],q[5]; q[6]→q[7],r[0]. It then exactly inverts all operations.

2. **State evolution**: Starting from |0⟩⁸|0⟩:
   - After encoding: the state is the Steane logical |0⟩_L = (1/√8)∑_{c∈C} |c⟩, a uniform superposition over the [7,4,3] Hamming codewords (even-weight combinations).
   - The decoding layer is the exact inverse of the encoding layer.

3. **Final state**: Since decoding perfectly reverses encoding, the system returns to |0⟩⁸ for q[0]–q[7] (r[0] also returns to |0⟩ but is not measured).

4. **Predicted distribution**: Only one outcome with probability 1:
   - |00000000⟩ (probability 1.0)

**Predicted probability distribution**: {|00000000⟩: 1.0}

### Reference answer

{'predicted_probs': {'00000000': 1.0}, 'explanation': 'The output is |00000000> with probability 1.0'}

## isqTrain/2027

- task_id: `isqTrain/2027`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `interference`, `isq_syntax_deriving_gate`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2957`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[2];
procedure my_z(qbit a) {
    Z(a);
} deriving gate
procedure main() {
    H(q[0]); H(q[1]);
    X(q[1]);
    ctrl my_z(q[0], q[1]);
    X(q[1]);
    H(q[0]); H(q[1]);
    X(q[0]); X(q[1]);
    ctrl my_z(q[0], q[1]);
    X(q[0]); X(q[1]);
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants an analysis of an isQ quantum program to predict the probability distribution of measurement outcomes. The output must be a concise step-by-step reasoning starting with "## Circuit Analysis" and ending with the predicted probabilities.

2.  **Analyze the isQ Code**:
    *   `qbit q[2];`: 2 qubits, initialized to $|00\rangle$.
    *   `H(q[0]); H(q[1]);`: Apply Hadamard to both. State becomes $|+\rangle|+\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
    *   `X(q[1]);`: Apply X to q[1]. State becomes $\frac{1}{2}(|01\rangle + |00\rangle + |11\rangle + |10\rangle) = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$. Wait, X swaps the amplitudes of $|0\rangle$ and $|1\rangle$. So $|+\rangle$ becomes $|+\rangle$. Yes, $X|+\rangle = |+\rangle$.
    *   `ctrl my_z(q[0], q[1]);`: This is CZ(q[0], q[1]). State becomes $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle) = \frac{1}{\sqrt{2}}(|0\rangle|+\rangle + |1\rangle|-\rangle)$.
    *   `X(q[1]);`: X on q[1]. State becomes $\frac{1}{\sqrt{2}}(|0\rangle|+\rangle + |1\rangle|+\rangle) = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$ wait... $X|-\rangle = -|-\rangle$. Let's re-evaluate.
        Let's track full 2-qubit state step by step.
        Initial: $|00\rangle$.
        $H \otimes H$: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
        $I \otimes X$: $\frac{1}{2}(|01\rangle + |00\rangle + |11\rangle + |10\rangle) = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
        CZ: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle)$.
        $I \otimes X$: $\frac{1}{2}(|01\rangle + |00\rangle + |11\rangle - |10\rangle) = \frac{1}{2}(|00\rangle + |01\rangle - |10\rangle + |11\rangle)$.
        $H \otimes H$: Apply H to both.
        Basis change $H^{\otimes 2}$ on $|00\rangle \to |++\rangle$, $|01\rangle \to |+-\rangle$, $|10\rangle \to |-+\rangle$, $|11\rangle \to |--\rangle$.
        Actually, $H^{\otimes 2}$ maps $\frac{1}{2}(|00\rangle + |01\rangle - |10\rangle + |11\rangle)$.
        Let's use $|0\rangle = \frac{1}{\sqrt{2}}(|+\rangle + |-\rangle)$, $|1\rangle = \frac{1}{\sqrt{2}}(|+\rangle - |-\rangle)$.
        $|00\rangle + |01\rangle - |10\rangle + |11\rangle = |0\rangle(|0\rangle+|1\rangle) - |1\rangle(|0\rangle-|1\rangle) = \sqrt{2}|0\rangle|+\rangle - \sqrt{2}|1\rangle|-\rangle$.
        Apply H to qubit 0: $H|0\rangle = |+\rangle$, $H|1\rangle = |-\rangle$.
        Apply H to qubit 1: $H|+\rangle = |0\rangle$, $H|-\rangle = |1\rangle$.
        So it becomes $\sqrt{2}|+\rangle|0\rangle - \sqrt{2}|-\rangle|1\rangle = \sqrt{2}\frac{|0\rangle+|1\rangle}{\sqrt{2}}

### Reference answer

{'predicted_probs': {'10': 1.0}, 'explanation': 'Grover search for |10>: P(|10>)=1.0 after one iteration.'}

## isqTrain/2703

- task_id: `isqTrain/2703`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3683`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit w[5];
procedure main() {
    for i in 0:3{
        X2P(w[i]);
        Y2P(w[i+1]);
        CNOT(w[i], w[i+1]);
    }
    for i in 0:3{
        for j in 0:3{
            for k in 0:3{
                H(w[(i+j+k) % 5]);
            }
        }
    }
    for i in 0:5{
        M(w[i]);
    }
}
```

### Chain-of-thought reasoning

Step 1: Analyze the first loop for state preparation.
The loop `for i in 0:3 { X2P(w[i]); Y2P(w[i+1]); CNOT(w[i], w[i+1]); }` runs for i=0, 1, 2, 3.
X2P = Rx(pi/2), Y2P = Ry(pi/2).
Let's track the state starting from |00000>.
i=0:
X2P(w0) -> w0 becomes X2P|0> = i|1>
Y2P(w1) -> w1 becomes Y2P|0> = (|0>+|1>)/sqrt(2)
CNOT(w0, w1) -> control w0 (i|1>), target w1 ((|0>+|1>)/sqrt(2)).
Wait, if w0 is i|1>, CNOT flips w1. So w1 becomes (|1>+|0>)/sqrt(2) = (|0>+|1>)/sqrt(2). It doesn't change w1's state in the Z basis (just applies X to the superposition). Also, w0 remains i|1>.
Wait, let's write the exact state: X2P|0> = (|0> - i|1>)/sqrt(2). Actually X2P = e^{-i X pi/4} = cos(pi/4) - i sin(pi/4) X = (1/sqrt(2))(I - iX).
So X2P|0> = (|0> - i|1>)/sqrt(2).
Y2P|0> = (|0> + |1>)/sqrt(2).
State after i=0: [(|0> - i|1>)_0 / sqrt(2)] * [(|0> + |1>)_1 / sqrt(2)] * |000>_{234}.
Apply CNOT(0,1): Since qubit 0 is not in the Z basis, let's apply CNOT to the state:
(|00> - i|11> + |01> - i|10>) / 2.
CNOT(0,1) gives: |01> - i|11> + |00> - i|10> = |00> - i|10> + |01> - i|11>.
This equals (|0> - i|1>)_0 * (|0> + |1>)_1 / sqrt(2). Same thing.

i=1:
X2P(w1) on w1=(|0>+|1>)/sqrt(2).
X2P(|0>+|1>) = (1/sqrt(2))(X2P|0> + X2P|1>) = (1/sqrt(2)) ((|0>-i|1>) + (-i|0>+|1>)) / sqrt(2) = (1-i)/2 |0> + (1-i)/2 |1> = (1-i)/sqrt(2) * (|0>+|1>)/sqrt(2).
Y2P(w2) on w2=|0> -> (|0>+|1>)/sqrt(2).
CNOT(w1, w2): target w2 is in superposition, w1 is not in Z basis. The combined state is a product of w1 and w2. Since they are unentangled, let's see:
w1 is (|0>+|1>)/sqrt(2), w2 is (|0>+|1>)/sqrt(2).
CNOT leaves them in the same state (up to phase) because target is |+> and control is |+>. Specifically, CNOT(|+>|+>) = |+>|+>.
Wait, let's trace all qubits carefully.
Actually, Y2P is a Clifford gate. Y2P = (H Z). Wait, Ry(pi/2) = (1/sqrt(2))[[1, -1], [1, 1]] ... no, Ry(pi/2)|0> = cos(pi/4)|0> + sin(pi/4)|1> = |+>.
Is there entanglement?
Let's simulate exactly.
Initial state: |00000>
i=0:
w0: X2P|0> = (|0> - i|1>)/sqrt(2).
w1: Y2P|0> = |+> = (|0>+|1>)/sqrt(2).
w0, w1: CNOT. (|00> - i|11> + |01> - i|10>) / 2 = |0>|+> - i|1>|->.
i=1:
w1: X2P.
X2P

### Reference answer

{'predicted_probs': {'00000': 0.12500000000000003, '00100': 0.12499999999999986, '01000': 0.1250000000000001, '01100': 0.12500000000000003, '10000': 0.12499999999999997, '10100': 0.12499999999999994, '11000': 0.12500000000000006, '11100': 0.12499999999999994}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/1122

- task_id: `isqTrain/1122`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3676`

### Prompt

帮我写一个isQ程序：implements the superdense_coding pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

Let me trace through the superdense coding circuit step by step.

1. Initial state: |00>

2. H(q[0]): |+0> = (1/√2)(|00> + |10>)

3. CNOT(q[0], q[1]): (1/√2)(|00> + |11>) = |Φ+> (Bell state)

4. Z(q[0]): (1/√2)(|00> - |11>) = |Ψ->... wait, let me recalculate.
   Z|0> = |0>, Z|1> = -|1>
   So Z on q[0]: (1/√2)(|00> - |11>)

5. X(q[0]): X|0> = |1>, X|1> = |0>
   (1/√2)(|10> - |01>) = |Ψ+>

   Wait, for superdense coding message '11', Alice applies X then Z (or Z then X).
   
   Let me check: Standard superdense coding for message '11' is X·Z applied to qubit 0.
   
   Actually, the order matters. Let me trace again:
   
   After Bell state: (1/√2)(|00> + |11>)
   
   Z(q[0]): (1/√2)(|00> - |11>)
   
   X(q[0]): (1/√2)(|10> - |01>)
   
   This is |Ψ+>... Hmm, but for message '11', typically we apply XZ which gives -|Ψ-> or ZX which gives |Ψ+>.
   
   Let me continue:
   
6. CNOT(q[0], q[1]): 
   |10> -> |11>
   |01> -> |00>
   So (1/√2)(|11> - |00>)

7. H(q[0]):
   H|1> = |-> = (1/√2)(|0> - |1>)
   H|0> = |+> = (1/√2)(|0> + |1>)
   
   So (1/√2)((1/√2)(|0> - |1>)|1> - (1/√2)(|0> + |1>)|0>)
   = (1/2)(|01> - |11> - |00> - |10>)
   = -(1/2)(|00> + |01> + |10> + |11>)
   
   Hmm, that doesn't seem right. Let me be more careful.
   
   Actually, let me re-examine. After step 5, the state is (1/√2)(|10> - |01>).

6. CNOT(q[0], q[1]):
   |10> → CNOT → |11>
   |01> → CNOT → |00>
   State: (1/√2)(|11> - |00>)

7. H(q[0]):
   |11> → (H⊗I) → ((|0>-|1>)/√2)|1> = (|01>-|11>)/√2
   |00> → (H⊗I) → ((|0>+|1>)/√2)|0> = (|00>+|10>)/√2
   
   So overall: (1/√2)((|01>-|11>)/√2 - (|00>+|10>)/√2)
   = (1/2)(|01> - |11> - |00> - |10>)
   = -(1/2)(|00> + |01> + |10> + |11>)
   
   That's not right for superdense coding. Let me reconsider.

   Wait, for message '11' in superdense coding, Alice applies X first, then Z (i.e., iY up to phase). Let me try ZX:
   
   ZX|0> = Z|1> = -|1>
   ZX|1> = Z|0> = |0>
   
   So applying ZX to q[0] of (1/√2)(|00> + |11>):
   = (1/√2)(-|10> + |01>)
   = (1/√2)(|01> - |10>)
   
   Then CNOT(q[0], q[1]):
   |01> → |00>
   |10> → |11>
   = (1/√2)(|00> - |11>)
   
   H(q[0]):
   |00> → (|00>+|10>)/√2
   |11> → (|01>-|11>)/√2
   = (1/2)(|00>+|10

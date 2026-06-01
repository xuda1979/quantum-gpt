# ISQ training COT RAG corpus: quantum_algorithms shard 98

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1939

- task_id: `isqTrain/1939`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `24`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[3];
procedure main() {
    X(q[1]);
    H(q[2]);
    ctrl S(q[1], q[2]);
    ctrl T(q[0], q[2]);
    H(q[1]);
    ctrl S(q[0], q[1]);
    H(q[0]);
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

Let me trace through the circuit step by step.

Initial state: |000>

Step 1: X(q[1]) → |010>

Step 2: H(q[2]) → |01+> = |01>(|0>+|1>)/√2 = (|010> + |011>)/√2

Step 3: ctrl S(q[1], q[2]) → S on q[2] controlled by q[1]. When q[1]=|1>, apply S to q[2].
State: (|010> + i|011>)/√2

Step 4: ctrl T(q[0], q[2]) → T on q[2] controlled by q[0]. When q[0]=|0> (which is always the case here), this does nothing.
State: (|010> + i|011>)/√2

Step 5: H(q[1]) → Apply H to q[1].
|010> → |0>|1>|0> → |0>(|0>-|1>)/√2 |0> = (|000> - |010>)|0>/√2
i|011> → i|0>(|0>-|1>)/√2 |1> = i(|001> - |011>)/√2

State: (|000> - |010> + i|001> - i|011>)/2

Step 6: ctrl S(q[0], q[1]) → S on q[1] controlled by q[0]. When q[0]=|0> (always here), this does nothing.
State: (|000> - |010> + i|001> - i|011>)/2

Step 7: H(q[0]) → Apply H to q[0].
|000> → (|000> + |100>)/√2
|010> → (|010> + |110>)/√2
|001> → (|001> + |101>)/√2
|011> → (|011> + |111>)/√2

State: ((|000> + |100>)/√2 - (|010> + |110>)/√2 + i(|001> + |101>)/√2 - i(|011> + |111>)/√2)/2
= ((|000> - |010> + i|001> - i|011>) + (|100> - |110> + i|101> - i|111>)) / (2√2)

Step 8: CNOT(q[0], q[2]) → flip q[2] when q[0]=1.
|000> → |000>
|010> → |010>
|001> → |001>
|011> → |011>
|100> → |101>
|110> → |111>
|101> → |100>
|111> → |110>

State: (|000> - |010> + i|001> - i|011> + |101> - |111> + i|100> - i|110>) / (2√2)

Step 9: CNOT(q[2], q[0]) → flip q[0] when q[2]=1.
|000> → |000>
|010> → |010>
|001> → |101>
|011> → |111>
|101> → |001>
|111> → |011>
|100> → |100>
|110> → |110>

State: (|000> - |010> + i|101> - i|111> + |001> - |011> + i|100> - i|110>) / (2√2)

Step 10: CNOT(q[0], q[2]) → flip q[2] when q[0]=1.
Let me relabel each term:
|000> → |000>
|010> → |010>
|101> → |100>
|111> → |110>
|001> → |001>
|011> → |011>
|100> → |101>
|110> → |111>

State: (|000> - |010> + i|100> - i|110> + |001> - |011> + i|101> - i|111>) / (2√2)

Let me factor this:
= ((1 + i)|000> + (1 + i)|001> - (1 + i)|010> - (1 + i)|011> + i(1 + i)|100> + i(1 + i)|101> - i(1 + i)|110> - i(

### Reference answer

{'predicted_probs': {'000': 0.125, '001': 0.125, '010': 0.125, '011': 0.125, '100': 0.125, '101': 0.125, '110': 0.125, '111': 0.125}, 'explanation': 'QFT on |010>'}

## isqTrain/1193

- task_id: `isqTrain/1193`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_classical_vars`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_inv`, `isq_syntax_multi_register`, `phase_manipulation`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `1631`

### Prompt

用isQ实现implements the phase_estimation pattern. Include explicit identity operations in the circuit (X-X pair before M(anc[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for the isQ quantum program that implements phase estimation with explicit identity operations (X-X pair before M(anc[0])).

Let me trace through the circuit step by step:

1. **Goal**: Implement quantum phase estimation to estimate the phase of the T gate (π/4), with an X-X pair to demonstrate gate cancellation.

2. **Qubits**: 3 ancilla qubits (anc[0], anc[1], anc[2]) for phase readout + 1 target qubit for eigenstate. The 3 ancilla qubits are measured.

3. **State evolution**:
   - Initial state: |000⟩⊗|0⟩ (ancilla ⊗ target)
   - X(target[0]): |000⟩⊗|1⟩ - target is prepared in eigenstate |1⟩ of T gate
   - H(anc[0]), H(anc[1]), H(anc[2]): (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ |1⟩
     = 1/√8 Σ_{k=0}^{7} |k⟩⊗|1⟩
   - The T gate has eigenstate |1⟩ with eigenvalue e^{iπ/4}
   - ctrl T(anc[0], target[0]): applies T when anc[0]=|1⟩, phase e^{iπ/4}
   - ctrl S(anc[1], target[0]): applies S=T² when anc[1]=|1⟩, phase e^{iπ/2}
   - ctrl Z(anc[2], target[0]): applies Z=T⁴ when anc[2]=|1⟩, phase e^{iπ}
   
   After controlled operations:
   1/√8 Σ_{k=0}^{7} e^{iφ_k}|k⟩⊗|1⟩
   
   where φ_k depends on the binary representation of k. For the T gate with phase π/4:
   - k=0 (000): φ=0
   - k=1 (001): φ=π/4
   - k=2 (010): φ=π/2
   - k=3 (011): φ=3π/4
   - k=4 (100): φ=π
   - k=5 (101): φ=5π/4
   - k=6 (110): φ=3π/2
   - k=7 (111): φ=7π/4
   
   So the state is: 1/√8 Σ_{k=0}^{7} e^{i·k·π/4}|k⟩⊗|1⟩

   This is |ψ⟩ = 1/√8 Σ_{k} e^{i·k·π/4}|k⟩ ⊗ |1⟩

   The phase is π/4 = 0.001 in binary. In phase estimation, the binary representation of the phase is encoded. Actually, wait - let me reconsider.

   For phase estimation, if the phase is θ, then after the controlled-U operations we get:
   1/√8 Σ_{k=0}^{7} e^{2πi·k·θ}|k⟩⊗|u⟩

   But here, the controlled operations apply U^{2^j} to the j-th ancilla qubit. The T gate has eigenvalue e^{iπ/4} = e^{2πi·(1/8)}.

   So θ = 1/8 = 0.001 in binary.

   After the controlled operations:
   |ψ⟩ = 1/√8 Σ_{k} e^{2πi·k/8}|k⟩ ⊗ |1⟩

   This is exactly the QFT of |1/8⟩ in the computational basis!

   Applying inverse QFT to this gives |001⟩ (which is 1 in decimal, but wait... let me reconsider the bit ordering).

   Actually, the phase θ = 1/8 in binary is 0.001. In phase estimation with 3 qubits, the ancilla qubits encode this as:
   - anc[0] (most significant): bit 0 (the one that comes after the decimal point)
   - anc[1]: bit 1
   - anc[2] (least significant): bit 2

   So the phase 0.001 would give |100⟩ in the ancilla register? No wait, let me be more careful.

   In standard phase estimation:
   - anc[0] controls U^{2^0} = U
   - anc[1] controls U^{2^1} = U²
   - anc[2] controls

## isqExpand/algo/125

- task_id: `isqExpand/algo/125`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `interference`, `basis_change`
- source: `isq_expansion_qa`
- dataset_index: `2354`

### Prompt

量子信号处理（Quantum Signal Processing, QSP）和量子奇异值变换（Quantum Singular Value Transformation, QSVT）是什么？请解释它们如何统一了大多数已知的量子算法。

### Chain-of-thought reasoning

## 推理
目标：解释QSP和QSVT。

核心：
1. QSP实现参数的多项式变换
2. QSVT推广到矩阵奇异值
3. 统一Grover、QPE、HHL等算法

### Reference answer

## 量子信号处理与量子奇异值变换

### QSP
QSP通过交替应用信号算子和信号处理算子来实现对量子态中某个参数的多项式变换。

给定信号酉算子 W(a)，通过交替施加 W(a) 和相位门，可以实现：
  P(a)|good> + Q(a)|bad>
其中 P(a) 是由相位序列决定的多项式。

### QSVT
QSVT将QSP从标量推广到矩阵。对于块编码的矩阵A，QSVT可以对每个奇异值独立施加多项式变换 P(sigma_i)。

### 统一量子算法
QSVT框架统一了大量已知算法：
- Grover搜索：P(a)是放大小信号的多项式
- QPE：P(a)近似阶梯函数
- HHL算法：P(a) ≈ 1/a
- 哈密顿量模拟：P(a) ≈ e^{iat}
- 固定点振幅放大：P(a)单调递增到1

### 核心优势
1. 最优查询复杂度
2. 统一框架：将算法设计归结为多项式近似 + 相位序列计算
3. 局限性：需要有效的块编码，电路深度对NISQ设备可能过大

## isqQA/quantum_algorithms/94_isq_implementation

- task_id: `isqQA/quantum_algorithms/94_isq_implementation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_implementation`, `algorithm`, `Grover搜索算法基本原理`
- source: `qa_pipeline`
- dataset_index: `5781`

### Prompt

请详细讲解Grover搜索算法的基本原理，并给出一个在3个量子比特上搜索特定目标态|101⟩的完整isQ代码实现。要求包含逐行详细注释，并解释Oracle和扩散算子的作用。

### Reference answer

<think>
解答此问题需分理论推导和代码实现两步走。首先，明确Grover算法的理论框架：在N=2^n的搜索空间中，通过Hadamard门构造均匀叠加态，再交替施加Oracle（翻转目标态相位）和扩散算子（关于均值反射振幅），将状态向量不断向目标态旋转。对于n=3（N=8）的情况，通过sin(θ)=1/√8计算出旋转角θ≈20.7°，进而推导出最优迭代次数k≈2，这是算法核心参数。其次，在代码实现层面，需构建针对|101⟩的Oracle——通过控制相位翻转实现，并利用H⊗H⊗H·X⊗X⊗X的结构构造扩散算子。最后，在isQ语言中按初始化、叠加态构造、两次Grover迭代、测量的顺序组织代码，并添加详细注释解释每步对应的物理操作。
</think>

<antml:think>我们来推导Grover算法的核心数学原理。假设有N=2^n个元素的搜索空间，其中有M=1个目标元素。首先，对n个初始为|0⟩的量子比特应用Hadamard门，构造均匀叠加态：
|s⟩ = H^{⊗n} |0⟩^{⊗n} = (1/√N) Σ_x |x⟩
Grover迭代由两个主要步骤组成：
1. Oracle作用：O = I - 2|w⟩⟨w|。它将目标态|w⟩的相位翻转180度（即振幅乘以-1），其他态保持不变。
2. 扩散算子作用：D = 2|s⟩⟨s| - I。它将各基态的振幅关于平均值进行反射。
Grover迭代算子 G = D O 将状态向量在由|w⟩和|s'⟩（|s⟩中去除|w⟩的归一化叠加）张成的二维子空间中，向目标态|w⟩旋转。每次旋转的角度为 2θ，其中 sin(θ) = 1/√N。
经过 k 次迭代后，测量得到目标态的概率为 sin^2((2k+1)θ)。
当N=8 (n=3)时，sin(θ) = 1/√8 ≈ 0.3535，θ ≈ 20.7°。
最优迭代次数 k ≈ π/(4θ) ≈ 2.16，因此取 k=2 次迭代可使成功率接近100%。
对于目标态|101⟩，我们需要构造一个Oracle：先对第二位(q[1])应用X门（将|101⟩变为|111⟩），然后对|111⟩执行相位翻转，最后再用X门恢复。
扩散算子的实现等价于：H^{⊗n} (2|0⟩⟨0| - I) H^{⊗n} = H^{⊗n} X^{⊗n} (C...CZ) X^{⊗n} H^{⊗n}。
</antml:think>
Grover搜索算法是量子计算中最经典的算法之一，它为无结构数据库的搜索问题提供了相较于经典算法的二次加速。在经典计算中，从N个无序列表中寻找1个特定目标，平均需要N/2次查询，最坏情况需要N次。而Grover算法只需要约√N次查询。

算法的核心在于巧妙地利用量子叠加和干涉现象，如同在水面上通过波峰与波峰的相遇来放大特定位置的振幅，同时通过波峰与波谷的相遇来抵消非目标位置的振幅。算法主要包含三个阶段：初始化均匀叠加态、反复执行Oracle相位翻转和扩散算子振幅放大、最后进行测量。

下面是在3个量子比特系统中搜索目标态|101⟩的完整isQ代码实现及逐行详细注释：

```isq
import std; // 引入标准库，提供基础量子门和测量等内置函数

qbit q[3]; // 全局声明3个量子比特，索引从0到2，分别代表二进制态的低位到高位

// 定义Oracle算子，用于识别并翻转目标态 |101> 的相位
procedure oracle_101() {
    // 目标态 |101> 意味着 q[0]=1, q[1]=0, q[2]=1
    // 我们需要将非1的对应位翻转，使得 |101> 变成 |111>
    X(q[1]); 
    
    // 对 |111> 执行相位翻转。
    // 因为 isQ 支持多控门和基础门，我们可以利用 Toffoli 门配合 Hadamard 门来实现多控 Z 门
    // H Z H 等价于 X 门的性质，因此 H 控制X H 等价于 控制-Z
    // 在 |111> 状态下对目标比特施加相位翻转 -1
    H(q[2]); // 对高位施加H门，将Z基转为X基
    Toffoli(q[0], q[1], q[2]); // 当q[0]和q[1]均为1时，对q[2]执行X门
    H(q[2]); // 再次施加H门，整体效果等效于多控 CZ 门
    
    // 恢复之前的 X 门操作，保证非目标态不受影响
    X(q[1]);
}

// 定义扩散算子，用于放大目标态振幅，缩小非目标态振幅
procedure diffuser() {
    // 扩散算子公式为 2|s><s| - I，可转换为门序列：H X (多控Z) X H
    for i in 0:3 {
        H(q[i]); // 对所有量子比特施加 Hadamard 门
    }
    
    for i in 0:3 {
        X(q[i]); // 对所有量子比特施加 X 门
    }
    
    // 此时 |000> 态变成了 |111>，我们需要对 |111> 执行相位翻转
    H(q[2]);
    Toffoli(q[0], q[1], q[2]); // 使用 Toffoli 等效实现多控 Z 门
    H(q[2]);
    
    for i in 0:3 {
        X(q[i]); // 再次对所有量子比特施加 X 门恢复
    }
    
    for i in 0:3 {
        H(q[i]); // 再次对所有量子比特施加 Hadamard 门
    }
}

// 主程序入口
procedure main() {
    // 第一步：初始化。将所有量子比特制备为均匀叠加态 |s> = (1/√8)Σ|x>
    for i in 0:3 {
        H(q[i]); // 对每个量子比特施加 Hadamard 门
    }
    
    // 第二步：Grover 迭代放大。
    // 搜索空间 N = 2^3 = 8。最优迭代次数约为 floor(π/4 * √8) = 2 次
    for iter in 0:2 {
        oracle_101(); // 1. Oracle 作用：标记目标态
        diffuser();   // 2. 扩散算子作用：振幅放大
    }
    
    // 第三步：测量。此时量子态以极高的概率坍缩到目标态 |101>
    for i in 0:3 {
        M(q[i]); // 对所有量子比特执行测量
    }
}
```

上述代码中，`oracle_101` 子过程首先使用 `X` 门将特定条件位（这里是 `q[1]`）翻转，巧妙地将识别目标态 `|101>` 的问题转换为识别 `|111>` 的问题。随后利用 `Toffoli` 门结合 `H` 门构造出受控相位翻转，完成对目标态振幅的“标记”操作。`diffuser` 子过程则实现了关于平均值的翻转操作，它将被 Oracle 标记的负振幅反向放大为突出的正振幅，同时将其他态的振幅压缩。整个系统在经过2次完整的迭代后，目标态 `|101>` 的概率振幅将达到接近100%，此时执行测量即可得到搜索结果。

## isqExpand/algo/10

- task_id: `isqExpand/algo/10`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `teleportation`, `bell_state`, `mid_circuit_measurement`, `classical_feedforward`
- source: `isq_expansion`
- dataset_index: `4979`

### Prompt

帮我写一个isQ程序：implements quantum teleportation. Alice has a qubit in state |1> that she wants to teleport to Bob using a shared Bell pair. Use mid-circuit measurement and classical feedforward.

### Chain-of-thought reasoning

## Reasoning
Goal: Teleport |1> from q[0] to q[2] using Bell pair q[1]-q[2].

1. X(q[0]): prepare Alice's qubit in |1>
2. Create Bell pair: H(q[1]), CNOT(q[1],q[2]) -> (|00>+|11>)/sqrt(2) on q[1],q[2]
3. Bell measurement on Alice's side:
   - CNOT(q[0],q[1]): entangle Alice's qubit with her half
   - H(q[0]): complete Bell basis measurement
4. Measure q[0], q[1] classically
5. Corrections on q[2]:
   - If m1=1: apply X(q[2])
   - If m0=1: apply Z(q[2])
6. q[2] is now in state |1> regardless of measurement outcomes

Note: uses stdout_match mode since mid-circuit measurement makes --probs unreliable for this pattern.

## isqTrain/2821

- task_id: `isqTrain/2821`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_for_loop`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5291`

### Prompt

用isQ实现creates a 3-qubit GHZ state. Apply H to the first qubit, then chain CNOT gates to entangle all 3 qubits. Measure all qubits.

Requirements:
- Declare `qbit q[3];` at global scope.
- Use `procedure main()` as entry point.
- Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a 3-qubit Greenberger–Horne–Zeilinger (GHZ) state.
2. **Qubits**: 3 qubits `q[0]`, `q[1]`, and `q[2]` are measured.
3. **State Evolution**: 
   - Start in state $|000\rangle$.
   - Apply `H(q[0])` to get $\frac{1}{\sqrt{2}}(|000\rangle + |100\rangle)$.
   - Apply `CNOT(q[0], q[1])` to entangle the first two qubits: $\frac{1}{\sqrt{2}}(|000\rangle + |110\rangle)$.
   - Apply `CNOT(q[1], q[2])` to entangle the third qubit: $\frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)$.
4. **Probabilities**: The final state is an equal superposition of $|000\rangle$ and $|111\rangle$, so measuring yields `000` and `111` each with 50% probability.

## isqTrain/2671

- task_id: `isqTrain/2671`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_classical_vars`, `isq_syntax_if_else`, `isq_syntax_multi_register`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3770`

### Prompt

用isQ实现implements quantum teleportation. Prepare a Bell pair between two qubits, then teleport the state of a source qubit to the destination using Bell measurement and conditional corrections (X and Z gates based on measurement results).

Requirements:
- Use 3 qubit(s) total.
- Measure 3 qubit(s) at the end.
- The program must start with `import std;`, declare qubits at global scope (or procedure scope as appropriate), define `procedure main()` as the entry point, and include explicit `M()` calls for all measured qubits.

### Chain-of-thought reasoning

Let me analyze the quantum teleportation protocol step by step.

The program uses 3 qubits:
- q_1: source qubit (initialized to |1⟩ by X gate)
- q_2: ancilla qubit (for Bell pair)
- q_3: destination qubit

The protocol:
1. Initialize q_1 to |1⟩ with X gate: state is |1⟩|0⟩|0⟩

2. Create Bell pair between q_2 and q_3:
   - H(q_2): |1⟩ ⊗ (|0⟩+|1⟩)/√2 ⊗ |0⟩
   - CNOT(q_2, q_3): |1⟩ ⊗ (|00⟩+|11⟩)/√2

3. Entangle source with ancilla:
   - CNOT(q_1, q_2): (|100⟩ + |111⟩)/√2... wait let me be more careful.

Let me trace through with q_1 = source, q_2 = ancilla, q_3 = dest.

Initial: |000⟩
After X(q_1): |100⟩

Teleport procedure:
- H(q_2): |100⟩ → |1⟩⊗(|0⟩+|1⟩)/√2⊗|0⟩ = (|100⟩+|110⟩)/√2
- CNOT(q_2, q_3): (|100⟩+|111⟩)/√2
- CNOT(q_1, q_2): (|100⟩+|111⟩)/√2... wait

Let me be more careful with ordering. q_1 is bit position 2 (leftmost), q_2 is bit position 1 (middle), q_3 is bit position 0 (rightmost).

State |q_1 q_2 q_3⟩

Initial: |000⟩
X(q_1): |100⟩

H(q_2): |1⟩⊗(|0⟩+|1⟩)/√2⊗|0⟩ = (|100⟩+|110⟩)/√2

CNOT(q_2, q_3): q_2 controls q_3
(|100⟩+|111⟩)/√2

CNOT(q_1, q_2): q_1 controls q_2
(|100⟩+|111⟩)/√2... hmm, when q_1=1 and q_2=0, q_2 flips to 1. When q_1=1 and q_2=1, q_2 flips to 0.
So: (|110⟩+|101⟩)/√2

H(q_1): Apply H to q_1.
|1⟩⊗(|0⟩+|1⟩)/√2 for first term → |1⟩ becomes (|0⟩-|1⟩)/√2
|1⟩⊗(|1⟩+|0⟩)/√2 for second term → |1⟩ becomes (|0⟩-|1⟩)/√2

Wait, let me just apply H to q_1 in each term:

(|110⟩+|101⟩)/√2

H on q_1:
|110⟩: q_1=1 → (|0⟩-|1⟩)/√2, so → (|010⟩-|110⟩)/√2
|101⟩: q_1=1 → (|0⟩-|1⟩)/√2, so → (|001⟩-|101⟩)/√2

Total: (|010⟩-|110⟩+|001⟩-|101⟩)/2

Now measure q_1 (m1) and q_2 (m2):

m1=0, m2=0: |010⟩ → q_3=0, apply nothing → |010⟩, measure q_3 = 0. Actually wait, q_1 is the source and gets measured.

Hmm, but the measurements collapse the state. Let me think about what states result:

After H(q_1), the state is (|010⟩-|110⟩+|001⟩-|101⟩)/2

Wait, I need to double-check. Let me redo more carefully.

State before H(q_1): (|110⟩+|101⟩)/√2

H(q_1): |0⟩→(|0⟩+|1⟩)/√2, |1⟩→(|0⟩-|1⟩)/√2

|110⟩ → (|010⟩-|110⟩)/√2
|101⟩ → (|001⟩-|101⟩)/√2

Total: (|010⟩-|110⟩+|001⟩-|101⟩)/(√2·√2) = (|010⟩-|110⟩+|001⟩-|101⟩)/2

Group by q_1,

## isqTrain/2719

- task_id: `isqTrain/2719`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3952`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
oracle g(3, 1) = [0, 0, 1, 1, 1, 1, 0, 0];
qbit q[3], anc;
procedure main(){
    for i in 0:3{
        H(q[i]);
    }
    X(anc);
    H(anc);
    g(q[0], q[1], q[2], anc);
    for i in 0:3{
        H(q[i]);
        int a = M(q[i]);
        print a;
    }
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The objective is to trace the given isQ program, analyze the quantum state step-by-step, and output the probability of each measurement outcome in a specific format.

2.  **Analyze the isQ Code**:
    *   `oracle g(3, 1) = [0, 0, 1, 1, 1, 1, 0, 0];`: A phase oracle acting on 4 qubits (3 inputs, 1 output). Wait, let me read the syntax carefully. `oracle g(3, 1)` means it takes 3 input qubits and 1 output qubit. But in standard phase oracle definitions in isQ, the array specifies the phase shift for each computational basis state of the *input* qubits, or it's a standard classical oracle implemented as a phase oracle?
    Wait, `oracle g(3, 1) = [0, 0, 1, 1, 1, 1, 0, 0];`. For `oracle` with an array of numbers, these represent the phase shifts (often $0$ or $\pi$ corresponding to $+1$ or $-1$ eigenvalues). The array has 8 elements, corresponding to the $2^3 = 8$ states of the 3 input qubits.
    Values: `0` for $|000\rangle$, `0` for $|001\rangle$, `1` for $|010\rangle$, `1` for $|011\rangle$, `1` for $|100\rangle$, `1` for $|101\rangle$, `0` for $|110\rangle$, `0` for $|111\rangle$.
    Wait, `1` means a phase of $\pi$ (since $e^{i\pi} = -1$). So the oracle applies a phase of $-1$ to states where the middle qubit is $|1\rangle$?
    Let's check the array indices:
    idx 0: 000 -> 0
    idx 1: 001 -> 0
    idx 2: 010 -> 1
    idx 3: 011 -> 1
    idx 4: 100 -> 0
    idx 5: 101 -> 0
    idx 6: 110 -> 1
    idx 7: 111 -> 1
    Wait! The array is `[0, 0, 1, 1, 1, 1, 0, 0]`.
    Let's list them properly:
    0: 000 -> 0
    1: 001 -> 0
    2: 010 -> 1
    3: 011 -> 1
    4: 100 -> 1
    5: 101 -> 1
    6: 110 -> 0
    7: 111 -> 0
    So the oracle applies $Z$ (phase of $\pi$) to states where (q1 XOR q0) is 1? No.
    Let's map indices:
    0 (000) -> 0
    1 (001) -> 0
    2 (010) -> 1
    3 (011) -> 1
    4 (100) -> 1
    5 (101) -> 1
    6 (110) -> 0
    7 (111) -> 0
    This corresponds to $f(x) = 1$ for $x \in \{010, 011, 100, 101\}$.
    Notice that $010, 011$ have the second bit (from MSB? No, 010 is q2=0, q1=1, q0=0).
    Let's just write it as a phase operator: $O_g |x\rangle = (-1)^{f(x)} |x\rangle$.
    $f(x) = 1$ for $x_2 x_1 x_0 \in \{010, 011, 100, 101\}$.
    Notice that $f(x)$ depends ONLY on $x_2$ and $x_1$! It is 1 if $x_2 \neq x_1$, and 0 if $x_2 == x_1$.
    Wait:
    00x -> 000, 001 -> 0
    01x -> 010, 011 -> 1
    10x -> 100, 101 -> 1
    11x -> 110, 111 -> 0
    Yes! $f(x_2, x_1

### Reference answer

{'predicted_probs': {'110': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/1117

- task_id: `isqTrain/1117`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1470`

### Prompt

实现以下量子计算任务（使用isQ）：implements a variant of the superdense_coding pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Write reasoning for an isQ program implementing a superdense coding variant.
    *   Specific constraint: Uses `q[2] -> q[3]` (Wait, The implementation says `qbit q[3];` which is an array of size 3, but the prompt says "q[2] -> q[3]"? Oh, actually, `q[2]` means expanding the register, but the reference uses `q[3]` array but only uses `q[0]` and `q[1]` for the main protocol, plus `q[2]` is just measured). Actually, Analyzing the circuit requirements, it uses `qbit q[3];`. The prompt says `superdense_coding pattern using q[2] -> q[3]`. Wait, The implementation is a Python-like generated code or standard template. Let's look at The implementation carefully: `qbit q[3];` and uses `q[0]`, `q[1]`, `q[2]` (just measured).
    *   I need to generate ONLY the reasoning section, starting with "## Reasoning", following the state evolution.

2.  **Analyze the circuit implementation:**
    *   `qbit q[3];` -> Qubits are `q[0]`, `q[1]`, `q[2]`.
    *   Initial state: `|000>`
    *   `H(q[0])` -> `1/sqrt(2)(|0> + |1>)|00>`
    *   `CNOT(q[0], q[1])` -> `1/sqrt(2)(|00> + |11>)|0>` (Bell state `Φ+`)
    *   `Z(q[0])` -> `1/sqrt(2)(|00> - |11>)|0>` (Bell state `Ψ-` wait, Z on `|00>+|11>` is `|00>-|11>`, which is `Φ-`)
    *   `X(q[0])` -> `1/sqrt(2)(|10> - |01>)|0>` (Bell state `Ψ-`)
    *   `CNOT(q[0], q[1])` -> `1/sqrt(2)(|10> - |01>)` -> wait, CNOT on `1/sqrt(2)(|10>-|01>)`:
        *   `CNOT(|10>) = |11>`
        *   `CNOT(|01>) = |01>`
        *   Result: `1/sqrt(2)(|11> - |01>) = 1/sqrt(2)(|1> - |0>)|1>` -> `-1/sqrt(2)(|0> - |1>)|1>`
    *   `H(q[0])` -> `-1/sqrt(2) * 1/sqrt(2) (|0> + |1> - (|0> - |1>)) |1> = -1/2 (2|1>) |1> = -|11>`. Phase doesn't matter, state is `|11>` for `q[0], q[1]`. Since `q[2]` is untouched, the overall state is `-|110>`.
    *   Measurement yields `|110>` with probability 1.0.

3.  **Draft the Reasoning:**
    *   **Goal:** Implement superdense coding to transmit the message '11' using 3 qubits.
    *   **Qubits:** 3 qubits (`q[0]`, `q[1]`, `q[2]`), all are measured.
    *   **Evolution:**
        *   Init: `|000>`
        *   `H(q[0])`, `CNOT(q[0], q[1])` creates the Bell state `(|00> + |11>)/√2 ⊗ |0>`.
        *   Alice applies `Z(q[0])` then `X(q[0])`, transforming the state to `(|10> - |01>)/√2 ⊗ |0>`.
        *   Bob decodes using `CNOT(q[0], q[1])` then `H(q[0])`, yielding the state `-|11> ⊗ |0> = -|110>`.
    *   **Probabilities:** The final state is `-|110>`, a pure state with a global phase, guaranteeing a 100% probability of measuring `|110>`.

4.  **Refine to constraints:**
    *   "3-8 lines for simple circuits"
    *   "Output ONLY the reasoning section, starting with "## Reason

## isqTrain/1247

- task_id: `isqTrain/1247`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `phase_manipulation`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `2866`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;

// R gate: controlled phase rotation for QFT
procedure R(int k, qbit q) {
    double phase = 3.14159265358979 / 2 ** (k - 1);
    ctrl GPhase(phase, q);
} deriving gate

// 3-qubit QFT
procedure qft_3(qbit q[3]) {
    // Process qubits from MSB to LSB
    // q[2]: H then controlled rotations
    H(q[2]);
    ctrl R(2, q[1], q[2]);
    ctrl R(3, q[0], q[2]);
    // q[1]: H then controlled rotation
    H(q[1]);
    ctrl R(2, q[0], q[1]);
    // q[0]: just H
    H(q[0]);
    // Swap to reverse output order
    SWAP(q[0], q[2]);
} deriving gate

// Register for QFT
qbit q[3];

procedure main() {
    // Prepare input state |101> (decimal 5)
    X(q[0]); X(q[2]);
    // Apply 3-qubit QFT
    qft_3(q);
    // QFT of basis state gives uniform distribution
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Output prediction for an isQ program (QFT of |101>).
    *   Input: isQ code.
    *   Goal: Generate a concise, precise step-by-step reasoning using Dirac notation. Length constraints: 3-15 lines.
    *   Format: Start with "## Circuit Analysis", end with predicted probability distribution.
    *   Constraints: Output ONLY the analysis, NO code blocks.

2.  **Analyze the isQ Code:**
    *   Initialization: `X(q[0]); X(q[2]);` prepares the state |101> (assuming q[0] is LSB, q[2] is MSB. State is |q2 q1 q0> = |101>). Let's represent this as $|5\rangle = |101\rangle$.
    *   QFT Circuit (`qft_3`):
        *   Processes q[2] (MSB):
            *   `H(q[2])`: Transforms MSB. $|101\rangle \to \frac{1}{\sqrt{2}}(|001\rangle + e^{i 5\pi/4}|101\rangle)$ wait, no. $H|x\rangle = \frac{1}{\sqrt{2}}(|0\rangle + (-1)^x |1\rangle)$. For $x=1$, $|1\rangle \to |-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
            *   `ctrl R(2, q[1], q[2])`: Phase $\pi/2$ on q[2] if q[1]=1. Since q[1]=0, no effect.
            *   `ctrl R(3, q[0], q[2])`: Phase $\pi/4$ on q[2] if q[0]=1. Since q[0]=1, applies phase. $\frac{1}{\sqrt{2}}(|001\rangle - e^{i\pi/4}|101\rangle)$.
        *   Processes q[1]:
            *   `H(q[1])`: Since q[1]=0, $|0\rangle \to |+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
            *   `ctrl R(2, q[0], q[1])`: Phase $\pi/2$ if q[0]=1. Applies phase.
        *   Processes q[0]:
            *   `H(q[0])`: Since q[0]=1, $|1\rangle \to |-\rangle$.
        *   Actually, doing this explicitly is tedious. Let's use the standard QFT property: $\text{QFT}|j\rangle = \frac{1}{\sqrt{N}} \sum_{k=0}^{N-1} e^{2\pi i j k / N} |k\rangle$.
        *   For $j=5$, $N=8$: $e^{2\pi i 5 k / 8} = e^{i \pi 5 k / 4}$.
        *   Magnitude of each $|k\rangle$ is $1/\sqrt{8}$. Probability of each is $1/8 = 0.125$.
        *   Code includes `swap (three-CNOT decomposition)(q[0], q[2])` at the end of `qft_3`, which restores the correct bit order if we tracked the whole tensor product, but the magnitude probabilities remain exactly uniform.
    *   Wait, the comment in the code literally says: `// QFT of basis state gives uniform distribution`.
    *   The output should state this and confirm the probability is 0.125 for all outcomes.

3.  **Draft the step-by-step reasoning:**
    *   Step 1: Initial state preparation with X gates on q[0] and q[2] yields the computational basis state $|101\rangle$ (decimal 5).
    *   Step 2: The `qft_3` procedure applies the 3-qubit Quantum Fourier Transform (QFT). The mathematical definition of QFT on a basis state $|j\rangle$ (where $j=5$ and $N=8$) is $\frac{1}{\sqrt{N}} \sum_{k=0}^{N-1} e^{2\pi i jk / N} |k\rangle$.
    *   Step 3: The QFT circuit decomposes this into Hadamards and controlled phase rotations, followed by a `swap (three-CNOT decomposition)` of q[0] and q[2] to reverse the qubit order and match the standard little-endian output

### Reference answer

{'predicted_probs': {'0': 0.125, '1': 0.125, '2': 0.125, '3': 0.125, '4': 0.12499999999999994, '5': 0.12499999999999994, '6': 0.125, '7': 0.125}, 'explanation': 'Parametric variant of isqEval/457. Dimension: predict probabilities for reference circuit.'}

# ISQ training COT RAG corpus: quantum_algorithms shard 77

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1414

- task_id: `isqTrain/1414`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_ctrl_nctrl`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `304`

### Prompt

帮我写一个isQ程序：Apply the 2-qubit Quantum Fourier Transform to the input state |01> and measure all qubits.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Apply 2-qubit QFT to |01> and measure both qubits.

**Qubits:** 2 qubits (q[0], q[1]), both measured.

**State evolution:**
1. Initialize |q[1]q[0]> = |00⟩; apply X(q[1]) → |10⟩
2. H(q[1]): |10⟩ → (|00⟩ − |10⟩)/√2
3. ctrl S(q[0], q[1]): controlled-S applies S to q[1] when q[0]=|1⟩; both terms have q[0]=0, so no change → (|00⟩ − |10⟩)/√2
4. H(q[0]): |0⟩→|+⟩ on q[0] → (|00⟩ + |01⟩ − |10⟩ − |11⟩)/2
5. swap (three-CNOT decomposition)(q[0], q[1]): exchanges qubit roles → (|00⟩ + |10⟩ − |01⟩ − |11⟩)/2

**Measurement probabilities:** Each computational basis state has amplitude magnitude |±1

## isqExpand/algo/116

- task_id: `isqExpand/algo/116`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `reversible_computing`, `multi_controlled_logic`, `ancilla_usage`
- source: `isq_expansion_qa`
- dataset_index: `2197`

### Prompt

量子乘法器的基本原理是什么？请解释如何用量子加法器和受控操作构建量子乘法电路，并讨论其与经典长乘法的类比关系以及Shor算法中的角色。

### Chain-of-thought reasoning

## 推理
目标：解释量子乘法器的原理。

关键点：
1. 量子乘法器基于经典长乘法的可逆版本
2. 核心组件是受控量子加法器
3. 门复杂度O(nm)，与经典相同
4. Shor算法中用于模幂运算

### Reference answer

## 量子乘法器原理

### 与经典长乘法的类比
经典二进制长乘法计算 A × B 的步骤是：对B的每一位b_j，如果b_j=1则将A左移j位后累加到结果寄存器。量子乘法器遵循相同的逻辑，但所有操作必须是可逆的。

### 基本构造
给定n-bit数A和m-bit数B，量子乘法器需要：
- 输入寄存器：n+m个量子比特
- 输出寄存器：n+m个量子比特存储乘积P
- 辅助比特：用于进位传播

核心步骤：
1. 对B的每一位b_j，执行受控加法：如果b_j=1，将A加到P的适当位置
2. 每次受控加法使用量子ripple-carry加法器，但所有CNOT/Toffoli门都以b_j为额外控制比特
3. 受控CNOT变为Toffoli门

### 门复杂度
O(n·m)个Toffoli门。量子优势不在乘法本身，而在于作为Shor算法中模幂运算的子程序时，能在叠加态上并行计算。

### isQ示例
```isq
import std;
qbit a[2];
qbit b[1];
qbit p[3];
procedure main() {
    X(a[0]); X(a[1]); X(b[0]);
    Toffoli(b[0], a[0], p[0]);
    Toffoli(b[0], a[1], p[1]);
    M(p[0]); M(p[1]); M(p[2]);
}
```

## isqTrain/1252

- task_id: `isqTrain/1252`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `ancilla_usage`, `entanglement`, `isq_syntax_arrays`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1094`

### Prompt

Help me write isQ code that implements a variant of the error_correction_syndrome pattern using syndrome[2] -> syndrome[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement 3-qubit bit-flip error correction with syndrome extraction to detect a bit-flip error on data[1].
2. **Qubits**: 6 total (data[3] + syndrome[3]); syndrome[0..2] are measured, yielding 3-bit output.
3. **State evolution**:
   - Init: |000⟩|000⟩; X(data[0]) → |100⟩|000⟩
   - CNOT(d0,d1), CNOT(d0,d2) → |111⟩|000⟩ (logical |1⟩)
   - X(data[1]) error → |101⟩|000⟩
   - CNOT(d0,s0), CNOT(d1,s0): s0 = 1⊕0 = 1 → |101⟩|100⟩
   - CNOT(d1,s1), CNOT(d2,s1): s1 = 0⊕1 = 1 → |101⟩|110⟩
4. **Final state**: |101⟩|110⟩ with syndrome[2]=0, syndrome[1]=1, syndrome[0]=1.
5. **Expected probabilities**: Measurement of syndrome[0..2] yields bitstring |110⟩ with probability 1.0, indicating error on data[1] via the parity syndrome pattern syndrome[2]→syndrome[3] generalization.

## isqQA/quantum_algorithms/129_principle_advantage

- task_id: `isqQA/quantum_algorithms/129_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `principle_advantage`, `algorithm`, `纠缠交换`
- source: `qa_pipeline`
- dataset_index: `1741`

### Prompt

请详细解释量子纠缠交换的宏观物理原理，并从时间复杂度与资源消耗的角度对比经典直接传输与纠缠交换在长距离量子通信中的表现，深入阐述其量子加速的来源。此外，请提供相应的数学推导，并使用isQ语言编写代码演示如何通过对两个独立的纠缠对进行贝尔基测量实现纠缠交换。

### Reference answer

纠缠交换是分布式量子计算和长距离量子通信（如量子中继）的核心技术。其宏观原理在于：即使两个量子比特在空间上相距甚远且从未发生过直接相互作用，通过在一个中间节点对它们分别所属的纠缠对进行联合贝尔态测量，可以让这两个远端比特瞬间建立起纠缠关联。由于贝尔态测量将中间两个比特投影到了最大纠缠态，系统的整体波函数发生坍缩，远端比特的状态也随之被纯化并绑定。

在时间复杂度与资源消耗方面，纠缠交换展现出了颠覆性的优势。在经典通信或直接传输量子比特的过程中，信号在光纤中的衰减呈指数级增长。如果要在距离 $L$ 上直接传输，由于信道损耗，所需的资源或重复次数的时间复杂度大约为 $O(e^{\alpha L})$，其中 $\alpha$ 是光纤衰减系数。这意味着随着距离增加，成本呈指数爆炸。而采用基于纠缠交换的量子中继方案，我们将总距离 $L$ 分成 $N$ 个短段，先在局部生成纠缠，再逐级进行纠缠交换。由于短段内的损耗可控，且纠缠交换的成功率可以通过量子存储器进行确定性或近确定性提升，最终构建全长 $L$ 的纠缠所需的时间和资源复杂度被大大降低，理论上演化为多项式级别 $O(L \log L)$ 或 $O(\text{poly}(L))$。

这种“量子加速”的根本来源并非计算速度的提升，而是量子纠缠的非局域性以及量子测量的投影特性。它利用了量子态叠加与不可克隆定理，克服了经典物理中信号放化的噪声累积缺陷。量子中继通过纠缠交换避免了直接传输带来的指数级概率损耗，从而在空间维度上实现了对信息传递损耗的指数级“加速”克服。

数学推导如下：假设粒子 A 和 B 处于贝尔态 $|\Phi^+\rangle_{AB} = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$，粒子 C 和 D 处于相同的贝尔态 $|\Phi^+\rangle_{CD} = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$。系统的整体状态为：
$|\Psi\rangle = |\Phi^+\rangle_{AB} \otimes |\Phi^+\rangle_{CD} = \frac{1}{2}(|00\rangle_{AB} + |11\rangle_{AB}) \otimes (|00\rangle_{CD} + |11\rangle_{CD})$
展开并将中间的 B 和 C 粒子用贝尔态基重新组合，可以得到：
$|\Psi\rangle = \frac{1}{2} [ |\Phi^+\rangle_{BC}|\Phi^+\rangle_{AD} + |\Phi^-\rangle_{BC}|\Phi^-\rangle_{AD} + |\Psi^+\rangle_{BC}|\Psi^+\rangle_{AD} + |\Psi^-\rangle_{BC}|\Psi^-\rangle_{AD} ]$
由此显见，当对 B 和 C 进行贝尔态测量并得到结果时（如得到 $|\Phi^+\rangle_{BC}$），远端的 A 和 D 必然塌缩到对应的纠缠态（如 $|\Phi^+\rangle_{AD}$），完成了纠缠的转移。

以下是使用isQ语言实现的纠缠交换代码：
import std;

qbit q[4]; // q[0]: A, q[1]: B, q[2]: C, q[3]: D

procedure main() {
    // 1. 制备 A 和 B 的纠缠对
    H(q[0]);
    CNOT(q[0], q[1]);

    // 2. 制备 C 和 D 的纠缠对
    H(q[2]);
    CNOT(q[2], q[3]);

    // 3. 在中间节点对 B (q[1]) 和 C (q[2]) 进行逆向贝尔基测量
    CNOT(q[1], q[2]);
    H(q[1]);

    // 测量中间粒子
    int r1 = M(q[1]);
    int r2 = M(q[2]);

    // 4. 经典通信与纠正：根据测量结果对远端粒子 A (q[0]) 和 D (q[3]) 进行相应的 Pauli 操作
    // 若测得 r2 == 1，相当于结果对应于含有 X 门的贝尔态，对 D 施加 X 门
    if (r2 == 1) {
        X(q[3]);
    }
    // 若测得 r1 == 1，相当于结果对应于含有 Z 门的贝尔态，对 A 施加 Z 门
    if (r1 == 1) {
        Z(q[0]);
    }
    // 至此，无论中间测量结果如何，A 和 D 均被纠正并锁定为标准的 |Phi+> 态
}

## isqTrain/2848

- task_id: `isqTrain/2848`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2963`

### Prompt

Implement a quantum circuit in isQ: creates a two-qubit state using H+CZ. Use the appropriate sequence of gates on 2 qubits and measure both.

Requirements:
- Declare `qbit q[2];` at global scope.
- Use `procedure main()` as entry point.
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a two-qubit entangled state using H and CZ gates, then measure both qubits.
2. **Qubits**: 2 qubits (q[0], q[1]), both measured.
3. **State evolution**:
   - Start: |00⟩
   - After H(q[0]): (|00⟩ + |10⟩)/√2
   - After H(q[1]): (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
   - After CZ(q[0], q[1]): (|00⟩ + |01⟩ + |10⟩ − |11⟩)/2 — CZ flips the phase of |11⟩
4. **Probabilities**: All four basis states have amplitude magnitude 1/2, so P = |1/2|² = 0.25 each, yielding {|00⟩: 0.25, |01⟩: 0.25, |10⟩: 0.25, |11⟩: 0.25}.

## isqTrain/2937

- task_id: `isqTrain/2937`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `620`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```isq
import std;
qbit q[4];
// Apply H to all 4 qubits (uniform superposition)
procedure main() {
    for i in 0:4 {
        H(q[i]);
    }
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. The bug is in the last measurement statement `M(q[0]);`. Instead of measuring the fourth qubit `q[3]`, it incorrectly remeasures `q[0]` a second time.
2. The fix is to replace the final `M(q[0])` with `M(q[3])` so that all 4 qubits are measured.
3. In the corrected circuit, applying H to all 4 qubits evolves the initial state $|0000\rangle$ into a uniform superposition of all 16 basis states, $\frac{1}{4} \sum_{x=0}^{15} |x\rangle$. Measuring all qubits yields a uniform probability of $1/16$ (0.0625) for each of the states from $|0000\rangle$ to $|1111\rangle$.

## isqTrain/4082

- task_id: `isqTrain/4082`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `339`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[3];

unit grover_oracle(qbit q[3]) {
    X(q[1]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[1]);
} deriving gate

unit grover_diffusion(qbit q[3]) {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
} deriving gate

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    grover_oracle(q);
    grover_diffusion(q);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict measurement output of a given isQ circuit.
    *   Circuit: 3-qubit Grover's algorithm (1 iteration).
    *   Format Requirements: Step-by-step reasoning using Dirac notation, concise (3-15 lines), specific section header "## Circuit Analysis", NO code blocks, end with probability distribution.

2.  **Analyze the Circuit:**
    *   `qbit q[3];` (3 qubits initialized to $|000\rangle$)
    *   `H(q[0]); H(q[1]); H(q[2]);` -> State becomes $|+++\rangle = \frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle$.
    *   `grover_oracle(q)`:
        *   `X(q[1])`
        *   `ctrl CZ(q[0], q[1], q[2])` (Toffoli-like CZ, applies Z to q[2] if q[0]=1 and q[1]=1). Actually, wait. `ctrl CZ` is a triple-qubit gate?
        *   Let's check `ctrl CZ(q[0], q[1], q[2])`. Wait, `CZ` is a 2-qubit gate: `CZ(control, target)`. So `ctrl @ CZ` applies CZ with a control. Wait, isQ syntax allows `ctrl CZ(q[0], q[1], q[2])` without `@`. Let's assume it means `q[0]` and `q[1]` are controls for `Z` on `q[2]`? Wait, no. If CZ is `CZ(control, target)`, then `ctrl CZ` means an additional control? Or `ctrl` applies to the first qubit?
        *   Ah, standard isQ: `ctrl CZ(q[0], q[1], q[2])` is a controlled-CZ? No, `ctrl` modifier adds controls. Usually, `ctrl CZ(c1, c2, target)` where CZ takes 2 args, so `ctrl` adds 1 arg. So `q[0]` and `q[1]` control `Z` on `q[2]`?
        *   Wait, let's re-read carefully: "Two-qubit gates: CNOT(control, target), CZ(control, target)". If I write `ctrl CZ(q0, q1, q2)`, it implies `q0` controls `CZ(q1, q2)`. So `q0` and `q1` control `Z` on `q2`. Wait! Toffoli gate flips the target. Here it's a controlled-Z. So phase -1 is applied if $q_0=1, q_1=1, q_2=1$? No, CZ applies Z to target if control is 1. So if $q_1=1$ and $q_2=1$, Z applies -1. If $q_0$ controls this, the overall phase is -1 if $q_0=1, q_1=1, q_2=1$. BUT `X(q[1])` before and after flips the sign of $q_1$ in the condition!
        *   Let's trace the oracle:
            *   Start: $\sum |x_0 x_1 x_2\rangle$
            *   X(q[1]) changes basis of q[1]. $|0\rangle \leftrightarrow |1\rangle$.
            *   `ctrl CZ(q[0], q[1], q[2])` with `q[0]` controlling `CZ(q[1], q[2])`. CZ(q[1], q[2]) applies a -1 phase if $x_1=1$ and $x_2=1$. If controlled by $q_0$, it only applies if $x_0=1$.
            *   Therefore, the phase -1 is applied to the state $|1 1 1\rangle$ (after X(q[1]) this was $|1 0 1\rangle$).
            *   So the oracle marks the state $|101\rangle$.
        *   Let's double check `ctrl CZ` syntax. In `isQ`, `CZ(control, target)` is a built-in gate. `ctrl` modifier adds a control qubit. So `ctrl CZ(q[0], q[1], q[2])` is $double-controlled-Z (ctrl @[c1, c2] Z(target))(q[0], q[1], q[2])$. It applies Z to q[2] if q[0] and q[1] are both 1.
        *   Wait,

### Reference answer

Dominant output states: |101> with probability ~0.78 each

## isqTrain/2880

- task_id: `isqTrain/2880`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `measurement_order`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1304`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```isq
import std;
qbit q[3];
// Multi-controlled X with 2 controls
procedure main() {
    X(q[0]);
    X(q[1]);
    ctrl ctrl X(q[0], q[1], q[2]);
    M(q[0]);
    M(q[0]);
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: The second `M(q[0])` measures qubit 0 twice instead of measuring qubit 1. This means qubit 1 is never measured, and the output bitstring only reflects two qubits instead of three.
2. **Fix**: Change the second `M(q[0])` to `M(q[1])` so that all three qubits (q[0], q[1], q[2]) are measured once each.
3. **State evolution**: |000⟩ → X(q[0]) → |100⟩ → X(q[1]) → |110⟩ → ctrl ctrl X (Toffoli, both controls are |1⟩, flips target) → |111⟩. Measuring all three qubits yields |111⟩ with probability 1.0.

## isqQA/quantum_algorithms/130_comparison

- task_id: `isqQA/quantum_algorithms/130_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `comparison`, `algorithm`, `门隐形传态`
- source: `qa_pipeline`
- dataset_index: `4344`

### Prompt

在容错量子计算中，门隐形传态与基础的量子状态隐形传态有何本质区别？请将其与直接在物理线路上执行量子门的传统方法进行对比分析，阐述两者的优缺点及适用场景，并使用isQ语言编写代码，演示如何通过门隐形传态机制非直接地实现一个非克利福德T门。

### Reference answer

<skip>
首先推导门隐形传态实现T门的核心逻辑：
1. 假设目标数据比特状态为 |psi> = a|0> + b|1>。
2. 准备一个辅助比特，并将其初始化为魔术态 |T> = T|+> = (|0> + e^{i*pi/4}|1>) / sqrt(2)。
3. 对数据比特和辅助比特执行 CNOT(q_data, q_ancilla)，其中数据比特为控制端，辅助比特为目标端。
联合状态演化为：(a|0> + b*e^{i*pi/4}|1>)|0> + e^{i*pi/4}(a|0> + b*e^{-i*pi/4}|1>)|1>。
4. 对辅助比特进行Z基测量：
- 若测量结果为0，数据比特坍缩为 a|0> + b*e^{i*pi/4}|1>，这正是 T|psi>。无需额外校正。
- 若测量结果为1，数据比特坍缩为 a|0> + b*e^{-i*pi/4}|1>，这相当于作用了 T的共轭转置 T^\dagger。为了得到T|psi>，需要施加校正门 S，因为矩阵乘积 S * T^\dagger 恰好等于 T。
</skip>

**本质区别：状态隐形传态 vs 门隐形传态**
基础的量子状态隐形传态旨在将一个未知的量子态从发送方传输到接收方，其核心转移的是“量子信息”本身；而门隐形传态则是通过消耗特定的纠缠资源（如魔术态），将一个量子逻辑门的作用效果“投射”到目标量子态上，其核心转移的是“量子操作”。门隐形传态不直接在目标比特上物理施加耗时或高错误率的门，而是通过贝尔测量和经典通信来完成计算。

**门隐形传态 vs 直接门合成的对比分析**
1. **直接门合成**
- **优点**：无需消耗额外的辅助比特，量子线路深度浅，资源开销极小。
- **缺点**：在NISQ（含噪声中等规模量子）时代，物理层面直接构造高保真度的非克利福德门（如T门、Toffoli门）极其困难，往往伴随着不可忽视的物理失真。
- **适用场景**：对保真度要求不极致的浅层线路，或者可以直接通过微波脉冲精确实现的简单门。

2. **门隐形传态**
- **优点**：彻底将物理层面的难度转化为资源准备的难度。在容错量子计算（如表面码架构）中，由于克利福德门可以极其高效地容错执行，而非克利福德门（T门）不能直接容错，利用门隐形传态结合魔术态蒸馏，能够以极高的保真度实现T门。此外，它将量子纠错的开销转化为经典的测量与前馈操作。
- **缺点**：需要消耗大量的辅助量子比特（魔术态），且由于蒸馏工厂的存在，会带来巨大的量子比特数量和时间延迟开销。
- **适用场景**：大规模容错量子计算（FTQC），特别是基于 Clifford+T 门集的架构中，作为实现通用量子计算的必由之路。

**isQ代码演示：通过门隐形传态实现T门**

以下代码展示了如何绕过直接的T门物理操作，通过准备魔术态、CNOT门、测量和经典前馈控制，间接实现高保真的T门操作：

import std;

qbit data[1];
qbit ancilla[1];
int measure_result;

procedure main() {
    // 假设 data[0] 中已经包含了我们想要施加 T 门的任意初始态

    // 1. 准备辅助魔术态 |T> = (|0> + e^{i*pi/4}|1>) / sqrt(2)
    // 容错架构中，这一步由昂贵的魔术态蒸馏工厂提供
    H(ancilla[0]);
    T(ancilla[0]);

    // 2. 执行门隐形传态的核心纠缠操作
    // 数据比特作为控制端，辅助比特（魔术态）作为目标端
    CNOT(data[0], ancilla[0]);

    // 3. 在Z基下测量辅助比特
    measure_result = M(ancilla[0]);

    // 4. 经典前馈：根据测量结果决定是否施加 Clifford 校正门
    // 根据理论推导，若测量结果为1，则等效于对数据比特作用了 T的共轭转置
    // 此时需要施加 S 门进行纠正，因为 S * T的共轭转置 == T
    if (measure_result == 1) {
        S(data[0]);
    }

    // 此时，data[0] 的状态已经成功应用了 T 门演化，全程未对 data 直接使用非Clifford的T门
}

## isqTrain/3986

- task_id: `isqTrain/3986`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `575`

### Prompt

Something is wrong with this isQ circuit. Identify the error and provide the corrected code.

```
import std;
// QFT on 4 qubits with input state |0000>
qbit q[4];

procedure main() {
    // Prepare input state |0000>

    // QFT stage for qubit 0
    H(q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 16.0, q[3], q[0]);
    // QFT stage for qubit 1
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[3], q[1]);
    // QFT stage for qubit 2
    H(q[2]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[3], q[2]);
    // QFT stage for qubit 3
    H(q[3]);
    // Swap q[0] and q[3]
    CNOT(q[0], q[3]);
    CNOT(q[0], q[3]);
    CNOT(q[0], q[3]);
    // Swap q[1] and q[2]
    CNOT(q[1], q[2]);
    CNOT(q[2], q[1]);
    CNOT(q[1], q[2]);
    // Measure after QFT
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

Let me analyze this bug carefully.

The task is a 4-qubit QFT on |0000>. Let me look at the buggy code and the corrected version.

The bug is in the swap operation (three-CNOT decomposition) between q[0] and q[3].

Buggy code for swap (three-CNOT decomposition)(q[0], q[3]):

Fixed code:

The swap operation (three-CNOT decomposition) is implemented as: CNOT(a,b); CNOT(b,a); CNOT(a,b). The second CNOT should have the control and target swapped from the first and third. In the buggy code, all three CNOTs have the same control and target, which doesn't implement a swap.

Let me verify the QFT stages are correct:

For QFT on 4 qubits starting from |0000>:
- H on q[0], then controlled Rz from q[1] to q[0] with angle π/2, from q[2] to q[0] with angle π/4, from q[3] to q[0] with angle π/8
- H on q[1], then controlled Rz from q[2] to q[1] with angle π/2, from q[3] to q[1] with angle π/4
- H on q[2], then controlled Rz from q[3] to q[2] with angle π/2
- H on q[3]
- swap (three-CNOT decomposition) q[0]↔q[3], swap (three-CNOT decomposition) q[1]↔q[2]

Wait, let me check the Rz angles. In QFT, the controlled rotation from qubit j to qubit k has angle 2π/2^(|j-k|+1). But wait, let me reconsider.

Actually, looking at the code more carefully:

The rotation angles are:
- ctrl Rz(2π * 2 / 4, ...) = ctrl Rz(π, ...) for distance 1
- ctrl Rz(2π * 2 / 8, ...) = ctrl Rz(π/2, ...) for distance 2
- ctrl Rz(2π * 2 / 16, ...) = ctrl Rz(π/4, ...) for distance 3

Wait, `2.0 * 3.14159265358979 / 4.0` = π/2, `2.0 * π / 8.0` = π/4, `2.0 * π / 16.0` = π/8.

Hmm, so for QFT the standard rotations are R_k = diag(1, e^{2πi/2^k}).

For stage 0 (qubit 0):
- H(q[0])
- CR_2(q[1], q[0]): angle 2π/2^2 = π/2 → `2π/4` ✓
- CR_3(q[2], q[0]): angle 2π/2^3 = π/4 → `2π/8` ✓
- CR_4(q[3], q[0]): angle 2π/2^4 = π/8 → `2π/16` ✓

Wait but `2.0 * π / 4.0` = π/2, which is the angle for Rz. So Rz(π/2, q[0]) applies the rotation e^{-iπ/4} to |1> state... 

Hmm, actually the convention matters. In some conventions, Rz(θ) applies diag(e^{-iθ/2}, e^{iθ/2}), and the controlled version applies diag(1, 1, 1, e^{iθ}) to the two-qubit space (up to global phase). So ctrl Rz(π/2, q[1], q[0]) would apply a phase of e^{iπ/2} = i when both are |1>.

For QFT, we need R_k gates where R_k = diag(1, e^{2πi/2^k}).

Stage 0: 
- CR_2: need phase e^{2πi/4} = e^{iπ/2} = i, so angle = π/2 = 2π/4 ✓
- CR_3: need phase e^{2πi/8} = e^{iπ/4}, angle = π/4 = 2π/8 ✓

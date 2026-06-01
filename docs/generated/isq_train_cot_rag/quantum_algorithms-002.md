# ISQ training COT RAG corpus: quantum_algorithms shard 2

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1140

- task_id: `isqTrain/1140`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5670`

### Prompt

请用isQ语言编写一个量子电路：implements the graph_state_preparation pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit prepares a 3-qubit linear graph state and then measures in the X basis, with an explicit X-X pair before measurement on q[0] to demonstrate gate cancellation.

Starting state: |000⟩

After H on all qubits: (1/√8)(|0⟩+|1⟩)⊗3 = |+++⟩

After CZ(q[0], q[1]): This creates entanglement between q[0] and q[1]. The graph state has edges (0,1).
The state becomes: (1/2)(|0++⟩ + |1-+⟩) ... let me think more carefully.

|+++⟩ = (1/√8)Σ|x₁x₂x₃⟩ for xᵢ ∈ {0,1}

CZ(q[0], q[1]) applies Z to q[1] when q[0]=|1⟩:
(1/√8)(|000⟩+|001⟩+|010⟩+|011⟩ + |100⟩-|101⟩+|110⟩-|111⟩)

Then CZ(q[1], q[2]) applies Z to q[2] when q[1]=|1⟩:
(1/√8)(|000⟩+|001⟩+|010⟩-|011⟩ + |100⟩-|101⟩-|110⟩+|111⟩)

Now apply H on all three qubits. Let me compute this.

After H⊗H⊗H, the state transforms. Let me compute:

The graph state is |G⟩ = (1/√8)Σ_z (-1)^z·Ez |z⟩ where Ez counts edges where both endpoints are 1.

For the linear graph 0-1-2:
- E_{000} = 0 edges active → (+1)
- E_{001} = 0 edges → (+1)  
- E_{010} = edge (0,1) not active (q0=0), edge (1,2) not active (q2=0) → wait, let me reconsider.

Actually, for graph state, the sign is (-1)^{number of edges where both endpoints are in state |1⟩}.

For bitstring x₀x₁x₂:
- 000: no edges → +1
- 001: no edges → +1
- 010: edge (0,1): q0=0, not both 1; edge (1,2): q2=0, not both 1 → +1
- 011: edge (0,1): q0=0; edge (1,2): q1=1,q2=1 → 1 edge → -1
- 100: edge (0,1): q0=1,q1=0 → no; → +1
- 101: same → +1
- 110: edge (0,1): q0=1,q1=1 → 1 edge; edge (1,2): q2=0 → no → -1
- 111: edge (0,1): 1; edge (1,2): 1 → 2 edges → +1

So |G⟩ = (1/√8)(|000⟩+|001⟩+|010⟩-|011⟩+|100⟩+|101⟩-|110⟩+|111⟩)

Now apply H⊗3. H|0⟩ = |+⟩, H|1⟩ = |−⟩.

H⊗3|G⟩ = H⊗3 · ∏CZ · H⊗3 |000⟩

Actually, since H⊗3 · CZ · H⊗3 transforms CZ to CNOT... but let me just compute directly.

H⊗3 applied to |G⟩:

Let me use the fact that H⊗n Σ_x f(x)|x⟩ = Σ_y (1/2^n) Σ_x (-1)^{x·y} f(x) |y⟩

f(x) = (-1)^{g(x)} where g(x) counts active edges.

For y=000: (1/8)(1+1+1-1+1+1-1+1) = (1/8)(4) = 1/2
For y=001: (1/8)(1+1+1+1+1+1+1+1) = 1
Wait, let me redo this.

f(000)=+1, f(001)=+1, f(010)=+1, f(011)=-1, f(100)=+1, f(101)=+1, f(110)=-1, f(111)=+1

For y₁y₂y₃, coefficient = (1/√8) Σ_x

## isqTrain/1941

- task_id: `isqTrain/1941`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `3617`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit c[1];
qbit p[2];
procedure DEC(qbit p0, qbit p1) {
    X(p0);
    CNOT(p0, p1);
} deriving gate
procedure INC(qbit p0, qbit p1) {
    CNOT(p0, p1);
    X(p0);
} deriving gate
procedure main() {
    H(c[0]);
    ctrl INC(c[0], p[0], p[1]);
    nctrl DEC(c[0], p[0], p[1]);
    M(p[0]); M(p[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ program:**
    *   `qbit c[1]` (1 control qubit)
    *   `qbit p[2]` (2 data qubits)
    *   Gate `DEC(p0, p1)`: `X(p0); CNOT(p0, p1);` -> Matrix for p0,p1: applies X to p0, then CNOT. If state is $a|00\rangle + b|01\rangle + c|10\rangle + d|11\rangle$, `X(p0)` makes it $a|10\rangle + b|11\rangle + c|00\rangle + d|01\rangle$. `CNOT(p0,p1)` makes it $a|11\rangle + b|10\rangle + c|00\rangle + d|01\rangle$.
    *   Gate `INC(p0, p1)`: `CNOT(p0, p1); X(p0);` -> If state is $a|00\rangle + b|01\rangle + c|10\rangle + d|11\rangle$, `CNOT` makes it $a|00\rangle + b|01\rangle + c|11\rangle + d|10\rangle$. `X(p0)` makes it $a|10\rangle + b|11\rangle + c|01\rangle + d|00\rangle$.
    *   Initial state: $|0_c\rangle \otimes |00_{p0p1}\rangle = |000\rangle$
    *   `H(c[0])`: applies H to c[0]. State becomes $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)_c \otimes |00_{p0p1}\rangle = \frac{1}{\sqrt{2}}(|000\rangle + |100\rangle)$
    *   `ctrl INC(c[0], p[0], p[1])`: applies INC to p[0], p[1] IF c[0] is |1>.
        *   When c=0: $|000\rangle$
        *   When c=1: $|1\rangle \otimes |00\rangle \xrightarrow{INC} |1\rangle \otimes INC(|00\rangle) = |1\rangle \otimes |10\rangle = |110\rangle$
        *   State after this step: $\frac{1}{\sqrt{2}}(|000\rangle + |110\rangle)$
    *   `nctrl DEC(c[0], p[0], p[1])`: applies DEC to p[0], p[1] IF c[0] is |0>. (nctrl means negative control).
        *   When c=0: $|0\rangle \otimes |00\rangle \xrightarrow{DEC} |0\rangle \otimes DEC(|00\rangle)$
            *   $DEC(|00\rangle)$: $X(p0)$ makes $|10\rangle$. `CNOT(p0,p1)` makes $|11\rangle$. So $DEC(|00\rangle) = |11\rangle$.
            *   Thus, $|0\rangle \otimes |11\rangle = |011\rangle$.
        *   When c=1: $|1\rangle \otimes |10\rangle \xrightarrow{DEC} |1\rangle \otimes |10\rangle$ (unaffected).
        *   State after this step: $\frac{1}{\sqrt{2}}(|011\rangle + |110\rangle)$
    *   `M(p[0]); M(p[1]);`: measure p[0] and p[1].
        *   Note: p[0] is measured first, then p[1].
        *   So the output bitstring is `p[0]p[1]`.
        *   Looking at the state $\frac{1}{\sqrt{2}}(|011\rangle + |110\rangle)$:
            *   $|0_c 1_{p0} 1_{p1}\rangle$
            *   $|1_c 1_{p0} 0_{p1}\rangle$
        *   Let's trace out `c[0]` to find the reduced density matrix of `p[0], p[1]`.
        *   The overall state is $\frac{1}{\sqrt{2}}(|11\rangle_{p0p1} |0\rangle_c + |10\rangle_{p0p1} |1\rangle_c)$.
        *   Since this is an entangled state between `c` and `p`, measuring `p` yields:

### Reference answer

{'predicted_probs': {'10': 0.5, '11': 0.5}, 'explanation': 'Quantum walk 1 step'}

## isqTrain/26

- task_id: `isqTrain/26`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2234`

### Prompt

Code this in isQ: implements the qft_subcircuit pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

Let me analyze this QFT circuit step by step.

The circuit implements a 3-qubit QFT with reversed measurement order.

**Initial state:**
- q[0] = |0⟩, q[1] = |0⟩, q[2] = |0⟩
- After X(q[2]): |0⟩|0⟩|1⟩

**QFT3 on q[0], q[1], q[2]:**

The qft3 procedure performs:
1. H(a=q[0])
2. ctrl Rz(π/2, b=q[1], a=q[0]) — controlled phase on q[0] with q[1] as control
3. ctrl Rz(π/4, c=q[2], a=q[0]) — controlled phase on q[0] with q[2] as control
4. H(b=q[1])
5. ctrl Rz(π/2, c=q[2], b=q[1]) — controlled phase on q[1] with q[2] as control
6. H(c=q[2])
7. swap (three-CNOT decomposition) q[0] and q[2]

Starting state: |001⟩ (in order q[0], q[1], q[2])

Step 1: H(q[0]) on |001⟩
= (|0⟩+|1⟩)/√2 ⊗ |0⟩ ⊗ |1⟩ = (|001⟩ + |101⟩)/√2

Step 2: ctrl Rz(π/2, q[1], q[0]) — if q[1]=|1⟩, apply Rz(π/2) to q[0]
q[1] is |0⟩ in both terms, so no change.

Step 3: ctrl Rz(π/4, q[2], q[0]) — if q[2]=|1⟩, apply Rz(π/4) to q[0]
q[2] is |1⟩ in both terms, so apply Rz(π/4) to q[0]:
Rz(π/4) |+⟩ = e^{-iπ/8}|0⟩ + e^{iπ/8}|1⟩)/√2

State: (e^{-iπ/8}|001⟩ + e^{iπ/8}|101⟩)/√2

Step 4: H(q[1]) on q[1] (which is |0⟩):
= (e^{-iπ/8}(|001⟩ + |011⟩) + e^{iπ/8}(|101⟩ + |111⟩))/2

Step 5: ctrl Rz(π/2, q[2], q[1]) — if q[2]=|1⟩, apply Rz(π/2) to q[1]
q[2] is |1⟩ in all terms, so apply Rz(π/2) to q[1]:
For |001⟩: q[1]=|0⟩, Rz(π/2)|0⟩ = e^{-iπ/4}|0⟩ → coefficient gets e^{-iπ/4}
For |011⟩: q[1]=|1⟩, Rz(π/2)|1⟩ = e^{iπ/4}|1⟩ → coefficient gets e^{iπ/4}
For |101⟩: q[1]=|0⟩, Rz(π/2)|0⟩ = e^{-iπ/4}|0⟩ → coefficient gets e^{-iπ/4}
For |111⟩: q[1]=|1⟩, Rz(π/2)|1⟩ = e^{iπ/4}|1⟩ → coefficient gets e^{iπ/4}

State: (e^{-iπ/8}·e^{-iπ/4}|001⟩ + e^{-iπ/8}·e^{iπ/4}|011⟩ + e^{iπ/8}·e^{-iπ/4}|101⟩ + e^{iπ/8}·e^{iπ/4}|111⟩)/2
= (e^{-3iπ/8}|001⟩ + e^{iπ/8}|011⟩ + e^{-iπ/8}|101⟩ + e^{3iπ/8}|111⟩)/2

Step 6: H(q[2])
H|1⟩ = (|0⟩ - |1⟩)/√2

Let me redo this more carefully. After step 5, the state in order (q[0], q[1], q[2]):
= (e^{-3iπ/8}|0⟩|0⟩|1⟩ + e^{iπ/8}|0⟩|1⟩|1⟩ + e^{-iπ/8}|1⟩|

## isqTrain/2926

- task_id: `isqTrain/2926`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `476`

### Prompt

Implement the following in isQ: applies a controlled Rz rotation of 3*pi/8 radians. Put the control qubit in superposition with H, set the target to |1>, apply controlled Rz, then H on the control. Measure both.

Requirements:
- Declare `qbit q[2];` at global scope.
- Use `procedure main()` as entry point.
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning

**Goal**: Apply a controlled-Rz(3π/8) gate with control in superposition, then measure both qubits.

**Qubits**: 2 qubits (q[0] control, q[1] target), both measured.

**State evolution**:
1. Initial: |00⟩
2. H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |0⟩ = (|00⟩+|10⟩)/√2
3. X(q[1]): (|01⟩+|11⟩)/√2
4. ctrl Rz(3π/8): When control=|1⟩, target |1⟩ → e^(i·3π/16)|1⟩ → state = (|01⟩ + e^(i3π/16)|11⟩)/√2
5. H(q[0]): = ½(

## isqTrain/1159

- task_id: `isqTrain/1159`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4923`

### Prompt

I need an isQ program to implements the mcmt_gate pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a multi-controlled multi-target X gate (MCMT) with 2 controls and 2 targets, including an identity H-H pair to demonstrate gate cancellation.

2. **Qubits**: 4 qubits (q[0], q[1] as controls; q[2], q[3] as targets); all 4 measured.

3. **State evolution**:
   - |0000⟩ → X(q[0]), X(q[1]) → |1100⟩
   - ctrl ctrl X(q[0],q[1],q[2]) flips q[2] since both controls are |1⟩ → |1110⟩
   - ctrl ctrl X(q[0],q[1],q[3]) flips q[3] since both controls are |1⟩ → |1111⟩
   - H(q[0]) → (|0111⟩ + |1111⟩)/√2
   - H(q[0]) → cancels the previous H, restoring |1111⟩ (identity demonstrated)

4. **Expected probabilities**: The H-H pair is identity, leaving the state as |1111⟩ before measurement, so P(|1111⟩) = 1.0.

## isqQA/quantum_algorithms/100_isq_implementation

- task_id: `isqQA/quantum_algorithms/100_isq_implementation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_implementation`, `algorithm`, `Grover自适应搜索`
- source: `qa_pipeline`
- dataset_index: `3246`

### Prompt

在量子算法中，Grover自适应搜索是如何通过动态调整来寻找优化问题的最优解的？请使用isQ语言编写一个完整的量子子程序，展示在特定阈值下执行单次Grover搜索的过程（包括自适应Oracle和扩散算子的构造），并对代码进行逐行注释与原理解析。

### Reference answer

<think>
首先，需要将Grover自适应搜索（GAS）的宏观理论拆解为经典-量子混合的迭代逻辑：即经典端负责动态更新优化阈值，量子端则负责在给定阈值下搜索更优解。明确了这一交互机制后，即可聚焦于量子端单次搜索过程的实现。

其次，设计单次Grover迭代的量子线路骨架，这必须包含三个核心模块：初态制备、自适应Oracle和扩散算子。接着，根据isQ语言的语法规范进行代码映射：第一步是声明量子寄存器，必须区分搜索寄存器与用于Oracle相位翻转的辅助比特；第二步在主程序中应用Hadamard门构建均匀叠加态；第三步构造核心的“自适应Oracle”，利用多控X（MCX）门结合辅助比特，将当前阈值条件转化为对特定目标态（如|01⟩）的相位翻转；第四步构造扩散算子，通过H门、X门与MCX门的组合实现概率振幅放大。最后，将上述逻辑整合进isQ代码结构，并对每行代码的物理数学意义进行注释解析，完成从算法原理到工程代码的完整推演。
</think>

Grover自适应搜索是一种主要用于解决组合优化问题（如寻找无序数据库中的最小值）的经典-量子混合算法。其核心思想是通过经典计算机与量子处理器的迭代交互来实现“自适应”。在每一轮迭代中，经典计算机会设定一个当前的阈值，量子部分则利用该阈值动态构造Oracle，通过标准的Grover搜索在所有候选解中寻找使得目标函数值小于（或优于）该阈值的解。如果量子搜索成功找到了更优的解，经典计算机便将其作为新的阈值进行下一轮搜索；如果未能找到，则说明当前阈值已经是全局最优。此外，算法的“自适应”还体现在动态选择最优的Grover迭代次数上，以克服未知解数量带来的挑战。以下是在isQ语言中实现的Grover自适应搜索量子子程序，我们以2个量子比特（搜索空间大小 $N=4$）为例，假设当前阈值要求我们寻找特定的目标态 $|01
angle$：

```isq
import std;

qbit q[2]; // 申请2个搜索用的量子比特
qbit anc[1]; // 申请1个辅助量子比特，用于Oracle的相位翻转

procedure main() {
    // 1. 初始化：将搜索寄存器制备为均匀叠加态 |s> = (|00>+|01>+|10>+|11>)/2
    // H门作用后，每个态出现的概率幅均为1/2
    H(q[0]);
    H(q[1]);

    // 2. 准备辅助比特：将其初始化为 |-> = (|0>-|1>)/sqrt(2)
    // 这是一种相位反冲技巧，当多控X门作用时，会将目标态的相位翻转记录在幅度上
    X(anc[0]);
    H(anc[0]);

    // 3. 执行Grover迭代。在自适应搜索中，迭代次数 R 是根据当前估计的解的数量自适应确定的
    // 假设经过自适应参数计算，当前阶段最佳的迭代次数 R = 1
    int R = 1;
    for i in 0:R {
        // --- 构造自适应 Oracle ---
        // Oracle的作用是给满足条件的态（这里是 |01>，即 q[1]=0, q[0]=1）打上负相位。
        // 为了使用Toffoli门进行多控X操作，我们需要将状态 |01> 转换为全1控制条件。
        // 因此对 q[1] 执行 X 门，使其在目标态下变为1
        X(q[1]);
        
        // 执行多控X门（Toffoli），当q[0]和q[1]（翻转后）均为1时，翻转辅助比特
        // 由于辅助比特处于|->态，这实际上在数学上等价于对 |01> 态施加了 -1 的相位
        Toffoli(q[1], q[0], anc[0]);
        
        // 恢复 q[1] 的状态（再次应用 X 门），以免影响后续的叠加态演化
        X(q[1]);

        // --- 构造扩散算子 ---
        // 扩散算子的作用是放大被Oracle标记的目标态的概率幅，同时缩小非目标态的概率幅
        // 其数学形式为 U_s = 2|s><s| - I。可以通过 H - X - 多控Z - X - H 的序列实现
        
        // 首先对搜索寄存器应用Hadamard门，回到计算基
        H(q[0]);
        H(q[1]);
        
        // 应用X门，为了后续构造条件相位翻转
        X(q[0]);
        X(q[1]);
        
        // 实现多控Z门（即围绕Z轴的相位翻转）
        // 在isQ中可以利用恒等式 CZ = (I ⊗ H) CNOT (I ⊗ H) 结合CNOT门来实现
        H(q[1]);
        CNOT(q[0], q[1]); // 此处相当于当q[0]为1时对q[1]执行X操作
        H(q[1]);
        
        // 恢复X门操作
        X(q[0]);
        X(q[1]);
        
        // 再次应用Hadamard门，完成扩散算子的构造
        H(q[0]);
        H(q[1]);
    }

    // 4. 测量：对量子比特进行测量，概率幅最大的结果即为当前搜索到的最优解
    // 在GAS框架中，这个测量结果将被返回给经典外层循环
    // 如果结果优于已知阈值，则更新阈值；若未找到，则可能需要增加迭代次数或终止算法
    int r0 = M(q[0]);
    int r1 = M(q[1]);
}
```

在上述代码中，`for` 循环内部完整实现了一次Grover迭代。在真实的Grover自适应搜索运行中，这段量子代码是被经典代码驱动的：经典代码负责调整 `R` 的值以及动态修改 `X(q[1])` 等反映当前阈值判断逻辑的电路结构。每次执行完毕后，通过测量得到新的候选解，进而不断逼近并最终锁定全局最优解。

## isqTrain/3813

- task_id: `isqTrain/3813`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_deriving_gate`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5009`

### Prompt

Write isQ code for the following quantum task: the swap test to compare states |0> vs |+>. Use:
1. q[0] as ancilla, q[1] for state A, q[2] for state B
2. A controlled-SWAP (Fredkin) gate via CNOT+Toffoli
3. Hadamard on ancilla before and after CSWAP
4. Measure all 3 qubits. P(ancilla=0) = (1+|<A|B>|²)/2.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement swap test to compare |0⟩ (q[1]) vs |+⟩ (q[2]) using ancilla q[0], measuring all 3 qubits.

State evolution:
1. **Prepare |+⟩ on q[2]:** |000⟩ → |0⟩|0⟩|+⟩ = (1/√2)(|000⟩ + |001⟩)
2. **H(q[0]):** (1/2)(|0⟩+|1⟩)(|00⟩+|01⟩) = (1/√2)(|00+⟩ + |10+⟩)
3. **CSW

## isqTrain/4040

- task_id: `isqTrain/4040`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `2895`

### Prompt

这段isQ代码有bug，帮我找出并修复：

```
import std;
// Phase kickback with Rz(3pi/2)
qbit q[2];

procedure main() {
    // Control in superposition
    X(q[0]);
    // Target in |1> eigenstate
    X(q[1]);
    // Controlled Rz
    ctrl Rz(3.14159265358979 * 6.0 / 4.0, q[0], q[1]);
    // Detect phase on control
    H(q[0]);
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

The buggy code uses `X(q[0])` to put the control qubit in the |1> state instead of superposition. For phase kickback to be detected, the control needs to be in superposition (|+> state), which requires `H(q[0])`.

Let me trace through the corrected circuit:

1. H(q[0]): |00> → (|0> + |1>)/√2 ⊗ |0> = (|00> + |10>)/√2
2. X(q[1]): → (|01> + |11>)/√2
3. ctrl Rz(3π/2, q[0], q[1]): Rz applies a phase when target is |1>. Since q[1] is already |1>, the controlled operation applies Rz(3π/2) to q[1] when q[0]=|1>. But wait - phase kickback means the phase kicks back to the control.

Actually, let me reconsider. Rz(θ) = [[1,0],[0,e^(iθ)]]. When applied controlled with control q[0] and target q[1], and q[1] is in |1>, the phase kicks back to the control.

State before controlled Rz: (|01> + |11>)/√2

For ctrl Rz(3π/2): when q[0]=|1> and q[1]=|1>, we get phase e^(i*3π/2). So:
→ (|01> + e^(i*3π/2)|11>)/√2 = (|01> - i|11>)/√2

This is equivalent to (|0> - i|1>)/√2 ⊗ |1>

4. H(q[0]): Apply H to the first qubit:
H(|0> - i|1>) = (1/√2)|0>(1-i)/√2 ... wait let me be more careful.

(|0> - i|1>)/√2, applying H to first qubit:
H(|0>) = (|0>+|1>)/√2
H(|1>) = (|0>-|1>)/√2

So H((|0> - i|1>)/√2) = (1/√2)[(|0>+|1>)/√2 - i(|0>-|1>)/√2]
= (1/√2)(1/√2)[|0>(1-i) + |1>(1+i)]
= (1/2)[(1-i)|0> + (1+i)|1>] ⊗ |1>

P(|0>) = |1-i|²/4 = (1+1)/4 = 1/2
P(|1>) = |1+i|²/4 = (1+1)/4 = 1/2

Hmm, that gives equal probabilities. But expected is {|01>: 0.146447, |11>: 0.853553}.

Wait, let me reconsider. the predicted output suggest a different phase.

0.146447 ≈ (2-√2)/4 and 0.853553 ≈ (2+√2)/4

Hmm, let me think about what Rz(3π/2) does more carefully. Rz(θ) = e^{-iθ/2}[[e^{iθ/2}, 0], [0, e^{-iθ/2}]] = [[1,0],[0,e^{-iθ}]]... no.

Actually in many frameworks: Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]] or Rz(θ) = [[1,0],[0,e^{iθ}]].

Let me verify the output. If we get phase kickback of e^{iφ} on control when in |+> state:

State after kickback: (|0> + e^{iφ}|1>)/√2 ⊗ |1>

After H on control: (|0>(1+e^{iφ}) + |1>(1-e^{iφ}))/(2) ⊗ |1>

P(|01>) = |1+e^{iφ}|²/4 = (1+cos(φ))/2... wait

|1+e^{iφ}|² = 2+2cos(φ), so P(|01>) = (2+2cos(φ))/4 = (1+cos(φ))/2

0.146447 = (1+cos(φ))/2 → cos(φ) = -0.707106 ≈ -1/√2

So φ ≈ 3π/4 or 5π/

## isqTrain/4469

- task_id: `isqTrain/4469`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `ancilla_usage`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2299`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;

qbit q[4];

procedure main() {
    // Ancilla in |-> state
    X(q[3]);
    H(q[3]);
    // Inputs in superposition
    H(q[0]);
    H(q[1]);
    H(q[2]);
    // Balanced oracle: f(x) = x[0]
    CNOT(q[0], q[3]);
    // Decode
    H(q[0]);
    H(q[1]);
    H(q[2]);
    // Measure: expect |100> (balanced)
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise circuit analysis of an isQ program representing a modified Deutsch-Jozsa algorithm (3 inputs, 1 ancilla). I need to explain the state evolution and predict the measurement probability distribution. The output must follow strict formatting rules.

2.  **Analyze the isQ Code:**
    *   `qbit q[4];`: 4 qubits initialized to $|0000\rangle$.
    *   `X(q[3]); H(q[3]);`: Ancilla q[3] becomes $|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$.
    *   `H(q[0]); H(q[1]); H(q[2]);`: Input qubits become $\frac{|0\rangle + |1\rangle}{\sqrt{2}}$ each.
    *   State so far: $\frac{1}{2\sqrt{2}} \sum_{x=0}^{7} |x\rangle \otimes (|0\rangle - |1\rangle)$. (Actually, it's $\frac{1}{\sqrt{8}}(|0\rangle+|1\rangle)^{\otimes 3} \otimes \frac{|0\rangle-|1\rangle}{\sqrt{2}}$).
    *   `CNOT(q[0], q[3]);`: Oracle for $f(x) = x_0$. The ancilla phase flips for $x$ where $x_0=1$.
        *   State: $\frac{1}{2\sqrt{2}} \sum_{x=0}^{7} (-1)^{x_0} |x\rangle \otimes (|0\rangle - |1\rangle)$.
    *   `H(q[0]); H(q[1]); H(q[2]);`: Hadamard transform on inputs.
        *   Standard Deutsch-Jozsa dictates that applying $H^{\otimes 3}$ to $\sum (-1)^{f(x)}|x\rangle$ yields $|100\rangle$ for this balanced function. Let's verify:
        *   $f(x)=x_0$.
        *   $H^{\otimes 3} \sum_{x} (-1)^{x_0} |x\rangle = |100\rangle$.
        *   Why? The state before the last H's is $\frac{1}{\sqrt{8}} \sum_{x} (-1)^{x_0} |x\rangle$.
        *   $H^{\otimes 3}$ maps this to $|z\rangle$ where $z = 0$ for constant, $z \neq 0$ for balanced. For $f(x) = x_0$, the oracle is just a CNOT on q[0], which effectively computes $z_0 = x_0 \oplus \dots$ wait.
        *   Let's trace it manually:
            *   Start with $|0000\rangle$.
            *   $X(q_3) \to |0001\rangle$
            *   $H(q_3) \to |000\rangle \otimes |-\rangle$
            *   $H(q_0)H(q_1)H(q_2) \to |+++\rangle|-\rangle$
            *   $CNOT(q_0, q_3) \to (|0\rangle_0|-\rangle_3 + |1\rangle_0|+\rangle_3) |++\rangle_{1,2}$. Wait, $|-\rangle$ with control 1 gets phase flip, so it stays $|-\rangle$. Wait!
            *   CNOT control q0, target q3.
            *   If q0 is $|0\rangle$, q3 is $|-\rangle$.
            *   If q0 is $|1\rangle$, q3 is $-|-\rangle$.
            *   So state is $\frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)_0 \otimes |+\rangle_1 \otimes |+\rangle_2 \otimes |-\rangle_3$.
            *   Apply $H(q_0)$: $|1\rangle_0$.
            *   Apply $H(q_1)$: $|0\rangle_1$.
            *   Apply $H(q_2)$: $|0\rangle_2$.
            *   So before the final X gate, the input state is exactly $|100\rangle$.
    *   `X(q[0]);`: Applies $X$ gate to q[0], flipping $|1\rangle$ to $|

### Reference answer

{'predicted_probs': {'0000': 1.0}, 'explanation': 'This isQ program operates on 4 qubit(s). The measurement probability distribution is: P(|0000>) = 1.0000.'}

## isqExpand/algo/121

- task_id: `isqExpand/algo/121`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `superposition`, `entanglement`, `phase_manipulation`
- source: `isq_expansion`
- dataset_index: `1660`

### Prompt

Write an isQ program that implementing a CNOT-efficient 3-qubit VQE hardware-efficient ansatz that uses only 2 CNOT gates (linear entanglement: q0->q1->q2) instead of a full ring. Apply Ry(0.7854, q[i]) (pi/4) to each qubit, then CNOT(q[0],q[1]) and CNOT(q[1],q[2]), then Ry(1.0472, q[i]) (pi/3) to each qubit. Measure all 3 qubits. Note: in isQ, rotation gates use syntax Ry(angle, qubit).

### Chain-of-thought reasoning

## Reasoning
Goal: CNOT-efficient VQE ansatz with linear entanglement.

Uses 2 CNOTs instead of 3, reducing depth for NISQ devices.
Circuit: Ry(pi/4) -> CNOT chain -> Ry(pi/3) -> measure.
The dominant state is |111> with probability ~0.402.

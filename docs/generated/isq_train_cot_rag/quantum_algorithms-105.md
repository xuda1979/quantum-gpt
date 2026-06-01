# ISQ training COT RAG corpus: quantum_algorithms shard 105

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/748

- task_id: `isqTrain/748`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1266`

### Prompt

Write isQ code for the following quantum task: implements the modular_adder pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for the given isQ quantum program.

Let me trace through the circuit:

1. Initial state: |000⟩ (3 qubits)
2. X(q[1]): |010⟩ - encodes a = 2
3. X(q[0]): |011⟩ - adds 1, now register = 3
4. Toffoli(q[0], q[1], q[2]): |111⟩ - overflow flag set when both bits are 1
5. Now we need to subtract 3 (modular correction for mod 3)

The CNOT gate can be decomposed as H-CZ-H on the target qubit.
CNOT = (I ⊗ H) CZ (I ⊗ H)

So the circuit is using H-CZ-H decomposition instead of CNOT.

Analyzing the circuit requirements:
- After Toffoli, state is |111⟩
- We need to subtract 3 (flip both q[0] and q[1]) controlled by q[2]

For q[0]:
6. H(q[0]): |1⟩→|−⟩ on q[0], state = 1/√2 (|110⟩ - |111⟩) ... wait, let me recalculate

Actually, let me be more careful with the state.

After step 4: |111⟩

5. H(q[0]): H|1⟩ = |−⟩ = (|0⟩ - |1⟩)/√2
State: |1⟩₁ ⊗ |−⟩₀ ⊗ |1⟩₂ = 1/√2 (|110⟩ - |111⟩) ... wait, ordering is q[2], q[1], q[0] or q[0], q[1], q[2]?

Let me use the ordering q[0], q[1], q[2]:

After Toffoli: |1⟩₀ ⊗ |1⟩₁ ⊗ |1⟩₂ = |111⟩ (in the order q[0]q[1]q[2])

H(q[0]): |−⟩₀ ⊗ |1⟩₁ ⊗ |1⟩₂ = 1/√2(|011⟩ - |111⟩) in q[0]q[1]q[2] ordering

CZ(q[2], q[0]): applies Z to q[0] when q[2]=1
Both terms have q[2]=1, so Z is applied to q[0]:
|0⟩₀ → |0⟩₀, |1⟩₀ → -|1⟩₀
So: 1/√2(|011⟩ - (-|111⟩)) = 1/√2(|011⟩ + |111⟩)

Wait, that doesn't seem right. Let me reconsider.

CZ(q[2], q[0]): when q[2]=1, apply Z to q[0].
Z|0⟩ = |0⟩, Z|1⟩ = -|1⟩

State before: 1/√2(|011⟩ - |111⟩) where I write as q[0]q[1]q[2]

Hmm, let me re-examine. In my notation |abc⟩, a=q[0], b=q[1], c=q[2].

After H(q[0]): |−⟩|1⟩|1⟩ = 1/√2(|0⟩|1⟩|1⟩ - |1⟩|1⟩|1⟩) = 1/√2(|011⟩ - |111⟩)

CZ(q[2], q[0]): control=q[2], target=q[0]. When q[2]=1, flip phase of q[0] if q[0]=1.
|011⟩: q[2]=1, q[0]=0 → no change
|111⟩: q[2]=1, q[0]=1 → flip phase → -|111⟩

Result: 1/√2(|011⟩ - (-|111⟩)) = 1/√2(|011⟩ + |111⟩)

H(q[0]): 
H on q[0] for |011⟩: |0⟩ → |+⟩, so |+⟩|1⟩|1⟩ = 1/√2(|011⟩ + |111⟩)
H on q[0] for |111⟩: |1⟩ → |−⟩, so |−⟩|1⟩|1⟩ = 1/√2(|011⟩ - |111⟩)

Result: 1/√2 · 1/√2 [(|011⟩ + |111⟩) + (|011⟩ - |111⟩)]
= 1/2 · 2|011⟩ = |011⟩

Wait, that

## isqTrain/3566

- task_id: `isqTrain/3566`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `hamiltonian_simulation`
- source: `isq_train_cot`
- dataset_index: `391`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should QAOA MaxCut on K4 (complete graph).

### Chain-of-thought reasoning

## Bug Analysis

**1. Bug identification:** The first ZZ interaction for edge (q[0], q[1]) has mismatched CNOT directions. The buggy code uses `CNOT(q[1], q[0]); Rz(0.5, q[1]); CNOT(q[0], q[1])` — the first CNOT targets q[0] but the second targets q[1], and the Rz is on q[1] (the control of the first CNOT). This breaks the standard CNOT-Rz-CNOT decomposition for a ZZ(γ) gate, which requires both CNOTs to share the same control and target.

**2. Fix:** Change the first CNOT from `CNOT(q[1], q[0])` to `CNOT(q[0], q[1])`, making it consistent with the rest: `CNOT(q[0], q[1]); Rz(0.5, q[1]); CNOT(q[0], q[1])`. This correctly implements ZZ(0.5) on the edge.

**3. State evolution (corrected):**
- Start: |0000⟩
- After H⊗4: |++++⟩ = equal superposition of all 16 basis states
- ZZ(0.5) on each of the 6 edges: for each pair (i,j), accumulates phase exp(∓iγ/2) depending on whether zi⊕zj = 0 or 1. States with more cut edges (disagreements) receive more positive phase, biasing toward MaxCut solutions.
- Rx(0.8) on each qubit: mixer rotation mixes computational basis states.
- Measurement yields |0000⟩ and |1111⟩ (trivial cuts) with highest probability ~0.303, while balanced cuts (|0011⟩, |0101⟩, |0110⟩, etc.) get ~0.027, consistent with QAOA p=1 for K4.

## isqTrain/3037

- task_id: `isqTrain/3037`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `measurement_order`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `950`

### Prompt

下面的量子程序运行结果不对，请帮我debug：

```isq
import std;
qbit q[2];
// nctrl H circuit
procedure main() {
    nctrl H(q[0], q[1]);
    M(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **The bug** is in the second measurement statement `M(q[0])`, which incorrectly measures the first qubit (`q[0]`) a second time instead of measuring the second qubit (`q[1]`).
2. **The fix** is to change the second `M(q[0])` to `M(q[1])` so that both qubits used in the circuit are properly measured.
3. **State evolution**: The system begins in $|00\rangle$. The `nctrl H(q[0], q[1])` gate applies an H gate to `q[1]` because the control `q[0]` is in the $|0\rangle$ state, evolving the state to $\frac{1}{\sqrt{2}}(|00\rangle + |01\rangle)$. Measuring both qubits then correctly yields the expected 50/50 probability distribution across the $|00\rangle$ and $|01\rangle$ states.

## isqTrain/3519

- task_id: `isqTrain/3519`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `ancilla_usage`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `4167`

### Prompt

Predict the output probabilities of the following quantum circuit:

```
import std;

qbit q[3];
qbit anc[2];

procedure main() {
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);

    X(q[0]);

    CNOT(q[0], anc[0]);
    CNOT(q[1], anc[0]);
    CNOT(q[0], anc[1]);
    CNOT(q[2], anc[1]);

    ctrl ctrl X(anc[0], anc[1], q[0]);

    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a step-by-step analysis of an isQ quantum program, predicting the probability distribution of the measured qubits.
2.  **Analyze the isQ Code:**
    *   Initialization: `qbit q[3]; qbit anc[2];` - 5 qubits total. Initial state |00000>.
    *   `CNOT(q[0], q[1]); CNOT(q[0], q[2]);` -> state is |00000> (q[0] is 0, so no flip).
    *   `X(q[0]);` -> state is |10000> (assuming standard bit ordering, e.g., q0, q1, q2, anc0, anc1). Wait, let's trace the bit values:
        *   q[0]=1, q[1]=0, q[2]=0, anc[0]=0, anc[1]=0. State: |10000>.
    *   `CNOT(q[0], anc[0]);` -> anc[0] becomes 1 XOR 0 = 1. State: |10100>.
    *   `CNOT(q[1], anc[0]);` -> anc[0] becomes 1 XOR 0 = 1. State: |10100>.
    *   `CNOT(q[0], anc[1]);` -> anc[1] becomes 0 XOR 1 = 1. State: |10101>.
    *   `CNOT(q[2], anc[1]);` -> anc[1] becomes 1 XOR 0 = 1. State: |10101>.
    *   `ctrl ctrl X(anc[0], anc[1], q[0]);` -> Toffoli gate. If anc[0]==1 and anc[1]==1, flip q[0].
        *   anc[0] = 1, anc[1] = 1. So flip q[0].
        *   q[0] becomes 1 XOR 1 = 0. State: |00101>.
    *   Measurement: `M(q[0]); M(q[1]); M(q[2]);` -> We only measure `q[0], q[1], q[2]`.
    *   Wait, the task asks for "output probability distribution" and "List all basis states with non-zero probability." In isQ --probs mode, usually only the *measured* qubits are returned, or the specific format might just be the measured qubits. Let me double check standard practices. "Predict the output probability distribution... List all basis states with non-zero probability." Since only `q[0], q[1], q[2]` are measured, the outcome is over 3 qubits. The ancillas are left unmeasured or their measurement is discarded if we only care about `q`.
    *   Let's re-read the state before Toffoli: |q0=1, q1=0, q2=0, anc0=1, anc1=1>.
    *   After Toffoli: |q0=0, q1=0, q2=0, anc0=1, anc1=1>.
    *   Measurement of q[0,1,2] yields 0, 0, 0.
    *   Basis state is |000>.
3.  **Step-by-step evolution:**
    *   Initial: |00000> (q[0], q[1], q[2], anc[0], anc[1])
    *   CNOT(q0, q1), CNOT(q0, q2) -> |00000> (q0 is 0)
    *   X(q0) -> |10000>
    *   CNOT(q0, anc0) -> |10100>
    *   CNOT(q1, anc0) -> |10100> (q1 is 0)
    *   CNOT(q0, anc1) -> |10101>
    *   CNOT(q2, anc1) -> |10101> (q2 is 0)
    *   ctrl ctrl X(anc0, anc1, q0) -> Toffoli(anc0, anc1, q0). Both anc0 and anc1 are 1. Flips q0. -> |00101>.
    *   Measure q[0,1,2] -> yields 000. So probability of |000> is 1.0.
4.  **Formatting:**
    *   Must start with "## Circuit Analysis".
    *   Must explain operations, step-by-step evolution, final state, and distribution.
    *   Must NOT include isq code blocks.
    *   Dirac notation required.
    *   Concise

### Reference answer

{'predicted_probs': {'000': 1.0}, 'explanation': 'The output is |000> with probability 1.0'}

## isqTrain/3978

- task_id: `isqTrain/3978`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `2844`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```
import std;
// Phase kickback with Rz(pi)
qbit q[2];

procedure main() {
    // Control in superposition
    H(q[0]);
    // Target in |1> eigenstate
    X(q[1]);
    // Controlled Rz
    ctrl Rz(3.14159265358979 * 4.0 / 4.0, q[0], q[1]);
    // Detect phase on control
    X(q[0]);
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: Line `X(q[0])` is incorrect. After phase kickback, the control qubit carries a relative phase (|0⟩ + i|1⟩)/√2 ⊗ |1⟩. The X gate merely flips computational basis states—it cannot convert phase information into measurable probabilities.

2. **Fix**: Replace `X(q[0])` with `H(q[0])`. The Hadamard gate transforms the phase-encoded state back into the computational basis for measurement.

3. **State evolution (corrected)**:
   - After H(q[0]), X(q[1]): (|0⟩ + |1⟩)|1⟩/√2
   - After ctrl Rz(π): (|0⟩ + i|1⟩)|1⟩/√2 — phase kickback onto control
   - After H(q[0]): ((1+i)|0⟩ + (1-i)|1⟩)|1⟩/2 — probabilities |1±i|²/4 = 0.5 each
   - Result: 50% |01⟩, 50% |11⟩ ✓

## isqTrain/976

- task_id: `isqTrain/976`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `456`

### Prompt

I need an isQ program to implements the lie_trotter pattern with modified rotation parameters (num_pi2_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

The task is to write an isQ program for a Lie-Trotter pattern with modified rotation parameters. Let me analyze The implementation.

The circuit should a Heisenberg model Trotter decomposition with H = XX + YY + ZZ. The time parameter is t = π/16, and 2t = π/8 ≈ 0.392699081698724.

The key modification mentioned is "num_pi2_to_pi3" which suggests the Rx basis change rotations use π/3 instead of π/2. Indeed, in the reference code, the Rx rotations use 1.04719755119660 which is π/3.

Standard YY evolution uses Rx(π/2) and Rx(-π/2) to rotate to the Y-basis. But here, they use Rx(π/3) which is a modification.

Wait, let me re-read the problem. It says "Write an isQ program that implements the lie_trotter pattern with modified rotation parameters (num_pi2_to_pi3). Adjust the angle values while preserving the overall circuit structure."

So the modification is changing from π/2 to π/3 for certain parameters. Analyzing the code:
- Rz uses 0.392699081698724 (which is 2t = π/8)
- Rx uses 1.04719755119660 (which is π/3)

The π/3 ≈ 1.04719755119660 is already present in the reference. So the modification has already been applied - the standard would be π/2 but they changed it to π/3.

I need to write an isQ program that matches The implementation with these parameters.

Let me trace through the state evolution:

Initial state: |00>
After X(q[0]): |10>

Term 1: e^(-i*t*ZZ)
- CNOT(q[0], q[1]): |10>
- Rz(0.392699081698724, q[1]): |10> (q[1] is |0>, Rz doesn't affect |0>... wait, Rz(θ)|0⟩ = e^(-iθ/2)|0⟩, Rz(θ)|1⟩ = e^(iθ/2)|1⟩)
  
Actually let me be more careful. Rz(θ) = diag(e^(-iθ/2), e^(iθ/2))

So Rz(2t)|0⟩ = e^(-it)|0⟩ and Rz(2t)|1⟩ = e^(it)|1⟩

State |10⟩: q[0]=|1⟩, q[1]=|0⟩
After CNOT(q[0], q[1]): q[0]=|1⟩, q[1]=|1⟩ → |11⟩
After Rz(2t, q[1]): q[1] is |1⟩, so it becomes e^(it)|1⟩ → e^(it)|11⟩
After CNOT(q[0], q[1]): |11⟩ → |10⟩ with phase e^(it)

So after Term 1: e^(iπ/16)|10⟩

Wait, that's a global phase. Let me redo more carefully.

Actually, for ZZ evolution: e^(-it*ZZ)|ab⟩ = e^(-it*(-1)^(a⊕b))|ab⟩

For |10⟩: a=1, b=0, a⊕b=1, so phase = e^(-it*(-1)^1) = e^(it) = e^(iπ/16)

So after Term 1: e^(iπ/16)|10⟩ (global phase, can ignore)

Term 2: e^(-i*t*XX) 
H|10⟩ = |−⟩|+⟩ where |+⟩ = (|0⟩+|1⟩)/√2, |−⟩ = (|0⟩-|1⟩)/√2

Hmm, let me be more careful.
H|0⟩ = |+⟩ = (|0⟩+|1⟩)/√2
H|1⟩ = |−⟩ = (|0⟩-|1⟩)/√2

H(q[0])H(q[1])|10⟩ = |−⟩|+⟩ = (|0⟩-|1⟩)(|0⟩+|1⟩)/2 = (|00⟩+|01⟩-|10⟩-|11⟩)/2

CNOT(q[0], q[1]) on this: CNOT swaps |10⟩↔|11⟩
(|00⟩+|01⟩-|11⟩-|10⟩)/2 = (|00⟩+|01⟩-|10⟩-

## isqQA/quantum_algorithms/123_hardware_limitations

- task_id: `isqQA/quantum_algorithms/123_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `hardware_limitations`, `algorithm`, `连续时间量子行走`
- source: `qa_pipeline`
- dataset_index: `1970`

### Prompt

在NISQ（含噪声中等规模量子）设备上实现连续时间量子行走（CTQW）算法时，退相干噪声和有限的量子门保真度是主要瓶颈。请深入分析退相干对量子行走演化动态及算法保真度的具体破坏机制，并探讨在硬件局限下如何通过降低线路深度来缓解噪声影响。此外，请提供一个基于一阶Trotter-Suzuki分解的浅层4节点环形图连续时间量子行走的isQ代码实现。

### Reference answer

在NISQ设备上实现连续时间量子行走（CTQW）面临着严峻的硬件局限挑战。CTQW的动力学由薛定谔方程支配，其时间演化算符为 U(t) = exp(-iHt)，其中H通常对应图的邻接矩阵。在物理实现上，由于难以直接构建连续的复杂多体哈密顿量演化，我们通常通过Trotter-Suzuki分解将其离散化为数字量子线路。然而，这种离散化引入了极深的电路深度和大量的双比特门。

退相干对CTQW的破坏机制主要体现在以下两个方面：
1. 相干性丧失：量子行走的计算优势（如相较于经典随机行走的指数级加速传播和碰撞概率差异）完全依赖于量子态的相干叠加与干涉效应。NISQ设备的相位阻尼（T2过程）会直接破坏不同计算基矢之间的相对相位关系，使得量子干涉图案消失，最终导致量子行走的概率分布退化为经典的随机扩散过程。
2. 振幅耗散与门误差累积：T1弛豫过程会导致激发态概率幅的耗散，改变行走者的总量。同时，长演化时间 t 要求更多的Trotter步数，使得CNOT等双比特门的误差呈指数级累积。在超过所谓的“噪声极限深度”后，量子线路的输出将变成纯粹的随机噪声。

为了在NISQ设备上缓解这些问题，必须极大地压缩线路深度。除了采用变分量子行走等混合量子-经典算法外，在数字量子模拟中，可以通过优化哈密顿量各项的排序（如边缘着色技术，使不相邻的边共享同一层CNOT），在单步Trotter演化中最大化线路的并行性，从而将深度降至最低。

以下是使用isQ语言编写的针对4节点环形图（环面上的跃迁）的浅层连续时间量子行走代码。为了适应NISQ设备的短相干时间，代码仅执行单步一阶Trotter近似演化，利用自定义的RXX和RYY门来模拟边上的跃迁哈密顿量：

import std;

qbit q[4];

// 定义双比特RXX旋转门，用于模拟X_i X_j相互作用
deriving gate RXX(theta) = [
    [cos(theta/2), 0, 0, -1i*sin(theta/2)],
    [0, cos(theta/2), -1i*sin(theta/2), 0],
    [0, -1i*sin(theta/2), cos(theta/2), 0],
    [-1i*sin(theta/2), 0, 0, cos(theta/2)]
];

// 定义双比特RYY旋转门，用于模拟Y_i Y_j相互作用
deriving gate RYY(theta) = [
    [cos(theta/2), 0, 0, 1i*sin(theta/2)],
    [0, cos(theta/2), -1i*sin(theta/2), 0],
    [0, -1i*sin(theta/2), cos(theta/2), 0],
    [1i*sin(theta/2), 0, 0, cos(theta/2)]
];

procedure main() {
    // 初始化：将行走者置于节点0（即|1000>态）
    X(q[0]);

    // 演化时间参数设定
    real t = 0.5;

    // 4节点环形图的边为 (0,1), (1,2), (2,3), (3,0)
    // 采用并行化的一阶Trotter分解以降低线路深度
    // 第一层：同时演化不相交的边 (0,1) 和 (2,3)
    RXX(t)(q[0], q[1]);
    RXX(t)(q[2], q[3]);
    RYY(t)(q[0], q[1]);
    RYY(t)(q[2], q[3]);

    // 第二层：同时演化不相交的边 (1,2) 和 (3,0)
    RXX(t)(q[1], q[2]);
    RXX(t)(q[3], q[0]);
    RYY(t)(q[1], q[2]);
    RYY(t)(q[3], q[0]);

    // 测量所有量子比特以获取行走者的位置概率分布
    for i in 0:4 {
        M(q[i]);
    }
}

## isqTrain/3609

- task_id: `isqTrain/3609`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `713`

### Prompt

I need an isQ program to a 3-qubit Grover search algorithm that finds the target state |100> using 1 Grover iteration. The circuit should:
1. Initialize 3 qubits in uniform superposition with Hadamard gates
2. Apply an oracle that marks state |100> with a phase flip
3. Apply the Grover diffusion operator
4. Measure all 3 qubits
Use `deriving gate` for oracle and diffusion procedures.

### Chain-of-thought reasoning

The user wants a reasoning section for a 3-qubit Grover search algorithm that finds the target state |100> using 1 Grover iteration.

1.  **Goal**: Find the target state $|100\rangle$ using a single Grover iteration on 3 qubits.
2.  **Qubits**: 3 qubits are needed, all are measured.
3.  **State Evolution**:
    *   **Initialization**: $|000\rangle$
    *   **Hadamards**: $H^{\otimes 3} |000\rangle = \frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle = \frac{1}{2\sqrt{2}}(|000\rangle + |001\rangle + |010\rangle + |011\rangle + |100\rangle + |101\rangle + |110\rangle + |111\rangle)$
    *   **Oracle**: Marks $|100\rangle$ with a phase flip. The oracle applies CZ controlled by $q_0, q_1, q_2$. To flip the phase of $|100\rangle$, we first apply X to $q_1, q_2$ to map $|100\rangle$ to $|111\rangle$. The controlled-Z applies a phase of -1 to $|111\rangle$. Then we revert with X on $q_1, q_2$.
        State becomes: $\frac{1}{2\sqrt{2}}(|000\rangle + |001\rangle + |010\rangle + |011\rangle - |100\rangle + |101\rangle + |110\rangle + |111\rangle)$
    *   **Diffusion**: Inversion about the mean.
        *   Apply $H^{\otimes 3}$.
        *   Apply X to all.
        *   Apply controlled-Z (on all 3). This flips the phase of $|111\rangle$.
        *   Apply X to all.
        *   Apply $H^{\otimes 3}$.
        The diffusion operator reflects the state vector about the mean amplitude. The mean amplitude before diffusion is $(1/2\sqrt{2}) \times 7 - (1/2\sqrt{2}) / 8 = (6/8) / (2\sqrt{2}) = 3 / (4\sqrt{2})$.
        Actually, let's calculate the exact amplitudes.
        Let initial amplitude be $a = 1/(2\sqrt{2})$. Target amplitude is $-a$. Non-target is $a$.
        Mean = $(7a - a)/8 = 6a/8 = 3a/4$.
        New amplitude for non-target = $2 \times mean - a = 2(3a/4) - a = 1.5a - a = 0.5a = a/2$.
        New amplitude for target = $2 \times mean - (-a) = 1.5a + a = 2.5a = 5a/4$.
        Let's check: $(7 \times (a/2)^2) + (5a/4)^2 = 7a^2/4 + 25a^2/16 = 28a^2/16 + 25a^2/16 = 53/16 \times 1/8 = 53/128 \neq 1$.
        Wait. $H^{\otimes 3}$ matrix applied to a vector.
        Vector is $v = [a, a, a, a, -a, a, a, a]^T$.
        $H^{\otimes 3} v = \frac{1}{2\sqrt{2}} \times \dots$
        Let's compute $H^{\otimes 3} v$.
        Sum of elements of $v$ = $6a = 6 / (2\sqrt{2}) = 3/\sqrt{2}$.
        $H^{\otimes 3} v = \frac{1}{\sqrt{8}} \times [\sum \pm v_i]$
        For $|000\rangle$, it's $(1/\sqrt{8}) (a+a+a+a-a+a+a+a) = (1/\sqrt{8}) (6a) = 6a/\sqrt{8} = 6/(2\sqrt{2}\sqrt{8}) = 6/4\sqrt{4} = 3/4$.
        Then X maps $|000\rangle$ to $|111\rangle$. CZ flips $|111\rangle$ to $-3/4$. X maps back to $-3/4 |000\rangle$.

## isqTrain/3068

- task_id: `isqTrain/3068`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`
- source: `isq_train_cot`
- dataset_index: `741`

### Prompt

用isQ实现initializes 4 qubits to the state |0010> using X gates and measures all.

Requirements:
- Declare `qbit q[4];` at global scope.
- Apply X to qubits that should be |1>.
- Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Initialize a 4-qubit register to the basis state |0010> and measure all qubits.
2. **Qubits**: 4 qubits (`q[0]` to `q[3]`), all of which are measured.
3. **State Evolution**:
   - The system begins in the default ground state |0000>.
   - Applying the X gate to `q[2]` flips its state from |0> to |1>, updating the full system state to |0010>.
4. **Probabilities**: Since no superposition is created, the final state is deterministically |0010>. Measuring all qubits yields the bitstring `0010` (where `q[0]` is the most significant bit) with a probability of 1.0.

## isqTrain/1211

- task_id: `isqTrain/1211`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5491`

### Prompt

帮我写一个isQ程序：implements the quantum_random_walk pattern. Include explicit identity operations in the circuit (H-H pair before M(p[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Implement one step of a discrete quantum walk on a 4-node cycle using a coin qubit and 2-bit position register.

**Qubits:** 3 total (c[0] coin, p[0], p[1] position); only p[0] and p[1] are measured.

**State evolution:**
1. Initial: |0,00⟩
2. H(c[0]): (|0⟩+|1⟩)/√2 ⊗ |00⟩ = (|0,00⟩+|1,00⟩)/√2
3. ctrl CNOT(c[0

# ISQ training COT RAG corpus: quantum_frontier shard 6

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/front/132

- task_id: `isqExpand/front/132`
- task_type: `output_prediction`
- category: `quantum_frontier`
- difficulty: `basic`
- concept_tags: `angle_encoding`, `rotation_gates`, `product_state`, `probability_calculation`
- source: `isq_expansion`
- dataset_index: `3606`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[2];
procedure main() {
    Ry(pi/2, q[0]);
    Ry(pi/4, q[1]);
}
```

### Chain-of-thought reasoning

Step 1: Analyze Ry(π/2) on q[0] starting from |0⟩. Ry(π/2)|0⟩ = cos(π/4)|0⟩ + sin(π/4)|1⟩ = (1/√2)|0⟩ + (1/√2)|1⟩. So P(q[0]=0) = 0.5 and P(q[0]=1) = 0.5. Step 2: Analyze Ry(π/4) on q[1] starting from |0⟩. Ry(π/4)|0⟩ = cos(π/8)|0⟩ + sin(π/8)|1⟩. cos(π/8) ≈ 0.9239, sin(π/8) ≈ 0.3827. P(q[1]=0) = cos²(π/8) = (1+cos(π/4))/2 = (1+1/√2)/2 ≈ 0.8536. P(q[1]=1) = sin²(π/8) = (1-cos(π/4))/2 = (1-1/√2)/2 ≈ 0.1464. Step 3: Since there is no entanglement (no multi-qubit gates), the joint probabilities factorize. Using isQ bit ordering where q[0] is LSB: P(00)=P(q[0]=0)×P(q[1]=0)=0.5×0.8536=0.4268, P(01)=P(q[0]=1)×P(q[1]=0)=0.5×0.8536=0.4268, P(10)=P(q[0]=0)×P(q[1]=1)=0.5×0.1464=0.0732, P(11)=P(q[0]=1)×P(q[1]=1)=0.5×0.1464=0.0732. Verification: 0.4268+0.4268+0.0732+0.0732=1.0 ✓

### Reference answer

{'predicted_probs': {'00': 0.4268, '01': 0.4268, '10': 0.0732, '11': 0.0732}, 'explanation': 'Ry(π/2)|0⟩ = (|0⟩+|1⟩)/√2 giving equal probability 0.5 for q[0]. Ry(π/4)|0⟩ = cos(π/8)|0⟩ + sin(π/8)|1⟩ giving P(0)=cos²(π/8)≈0.8536 and P(1)=sin²(π/8)≈0.1464 for q[1]. With no entanglement the joint probabilities factor: P(q0,q1)=P(q0)×P(q1).'}

## isqExpand/front/48

- task_id: `isqExpand/front/48`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `quantum_chemistry`, `givens_rotation`, `single_excitation`
- source: `isq_expansion`
- dataset_index: `1773`

### Prompt

Code this in isQ: implements a single excitation gate (Givens rotation) in a VQE context.

A single excitation from orbital i to orbital a is implemented as a Givens rotation:
G(theta) on qubits i and a, which is equivalent to:
Ry(theta) applied in the {|01⟩, |10⟩} subspace.

This can be decomposed as:
CNOT(q[0], q[1]), Ry(theta, q[0]), CNOT(q[0], q[1]).

Demonstrate exciting one electron from orbital 0 to orbital 1 with theta=pi/3.

Requirements:
- Declare global `qbit q[2];`
- Start from |10⟩ (electron in orbital 0).
- Apply the Givens rotation.
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. Start |10⟩. X(q[0]) sets q[0]=|1⟩.
2. CNOT(q[0],q[1]): q[0]=1 flips q[1] -> |11⟩.
3. Ry(pi/3, q[0]): Ry(pi/3)|1⟩ = -sin(pi/6)|0⟩+cos(pi/6)|1⟩ = -0.5|0⟩+(sqrt(3)/2)|1⟩.
4. State: (-0.5|0⟩+(sqrt(3)/2)|1⟩)|1⟩ = -0.5|01⟩+(sqrt(3)/2)|11⟩.
5. CNOT(q[0],q[1]): |0⟩ branch: no flip -> |01⟩. |1⟩ branch: flip q[1] -> |10⟩.
6. State: -0.5|01⟩+(sqrt(3)/2)|10⟩.
7. P(|01⟩)=0.25, P(|10⟩)=0.75.

## isqExpand/front/151

- task_id: `isqExpand/front/151`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `ramsey_interferometry`, `superposition`, `phase_rotation`, `hadamard_interference`, `rz_gate`
- source: `isq_expansion`
- dataset_index: `4354`

### Prompt

Write an isQ program that implements a Ramsey interferometry circuit on a single qubit. The circuit should: (1) Apply a Hadamard gate to prepare an equal superposition, (2) Apply a phase rotation Rz(theta) with theta = pi/3, (3) Apply another Hadamard gate to cause interference, and (4) measure the qubit. Print the measurement result. The circuit starts in the |0⟩ state.

### Chain-of-thought reasoning

Ramsey interferometry involves three steps on a single qubit: superposition preparation, phase accumulation, and interference readout. Starting from |0⟩, after the first H we get (|0⟩+|1⟩)/√2. The Rz(θ) gate with θ=π/3 introduces a relative phase: the state becomes (|0⟩+e^{iπ/3}|1⟩)/√2 (up to global phase). The second H gate maps this to ((1+e^{iπ/3})|0⟩+(1-e^{iπ/3})|1⟩)/2. Computing probabilities: P(|0⟩)=|1+e^{iπ/3}|²/4=(2+2cos(π/3))/4=(2+1)/4=3/4=0.75. P(|1⟩)=|1-e^{iπ/3}|²/4=(2-2cos(π/3))/4=(2-1)/4=1/4=0.25. So the expected probability distribution is [0.75, 0.25]. The isQ code uses global qbit declaration, H, Rz with numeric angle π/3≈1.0471975511965976, another H, then measurement.

## isqExpand/front/46

- task_id: `isqExpand/front/46`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `basic`
- concept_tags: `quantum_chemistry`, `hartree_fock`, `jordan_wigner`
- source: `isq_expansion`
- dataset_index: `4535`

### Prompt

Write isQ code for the following quantum task: prepares the Hartree-Fock state for a 2-electron, 4-orbital system.

In the Jordan-Wigner mapping, the Hartree-Fock state for 2 electrons in the lowest 2 orbitals is simply |1100⟩ (first two orbitals occupied).

Requirements:
- Declare global `qbit q[4];`
- Prepare |1100⟩ by applying X to q[0] and q[1].
- Measure all qubits.
- Expected: |1100⟩ with probability 1.

### Chain-of-thought reasoning

## Reasoning
1. Start |0000⟩.
2. X(q[0]) -> |1000⟩. X(q[1]) -> |1100⟩.
3. |1100⟩ = 1*8+1*4+0*2+0 = 12.
4. P(|1100⟩) = 1.0 at index 12.

## isqExpand/front/14

- task_id: `isqExpand/front/14`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `molecular_hamiltonian`, `second_quantization`, `fermion_to_qubit`, `quantum_chemistry`
- source: `isq_expansion_qa`
- dataset_index: `2452`

### Prompt

解释量子化学中分子哈密顿量的概念。如何从二次量子化表示转换为qubit算符？为什么这一步对量子计算模拟分子至关重要？

### Chain-of-thought reasoning

## 推理
目标：解释分子哈密顿量和费米子-qubit映射。

逻辑链：分子电子结构→二次量子化表示（产生/湮灭算符）→费米子反对易性→需要映射到qubit→JW变换→Pauli分解→量子电路可测量。
H2作为最简单的例子说明完整流程。

### Reference answer

## 分子哈密顿量与二次量子化

### 分子哈密顿量
分子的电子结构问题可以用哈密顿算符描述：

H = Σ_{pq} h_{pq} a†_p a_q + (1/2) Σ_{pqrs} h_{pqrs} a†_p a†_q a_s a_r + E_{nuc}

其中：
- a†_p, a_q 是费米子产生/湮灭算符
- h_{pq} 是单体积分（动能+电子-核势能）
- h_{pqrs} 是双体积分（电子-电子排斥）
- E_{nuc} 是核-核排斥能（常数）

### 二次量子化
二次量子化用**占据数表示**描述量子态：
- 每个分子轨道用一个费米模式表示
- a†_p|0⟩ = |1_p⟩（在轨道p创建一个电子）
- a_p|1_p⟩ = |0_p⟩（从轨道p移除一个电子）
- 费米子反对易关系：{a_p, a†_q} = δ_{pq}

### 从费米子到qubit的映射
量子计算机使用qubit而非费米子，因此需要映射：

**Jordan-Wigner变换**：
- a†_j → (1/2)(X_j - iY_j) ⊗ Z_{j-1} ⊗ ... ⊗ Z_0
- 每个费米模式对应一个qubit
- 占据数直接映射：|n_0 n_1 ...⟩
- 反对易性通过Z串（parity string）实现

**Bravyi-Kitaev变换**：
- 使用部分和编码，Z串长度降为O(log n)
- 更高效但结构更复杂

### 为什么重要
1. 量子计算机只能处理qubit算符（Pauli矩阵的线性组合）
2. 映射后，H = Σ_i c_i P_i（P_i是Pauli串，如X_0Z_1Y_2）
3. 每个Pauli项可以在量子电路上测量
4. VQE等算法通过测量各Pauli项来计算能量期望值 ⟨ψ|H|ψ⟩

### H2分子示例
最小基组下H2只有2个分子轨道（4个自旋轨道），经JW变换后：
H = c_0 I + c_1 Z_0 + c_2 Z_1 + c_3 Z_0Z_1 + c_4 X_0X_1 + c_5 Y_0Y_1

这个6项Pauli分解可以在2-qubit量子电路上高效测量。

## isqExpand/front/18

- task_id: `isqExpand/front/18`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `quantum_kernel`, `feature_map`, `data_encoding`, `quantum_ml`
- source: `isq_expansion`
- dataset_index: `4549`

### Prompt

请用isQ语言编写一个量子电路：implements a quantum kernel feature map circuit for 2 qubits.

In quantum kernel methods, data is mapped to a quantum feature space using a feature map circuit. The overlap between feature states defines the kernel function. A common feature map applies Hadamard gates, then Z-rotations encoding data, followed by entanglement.

Requirements:
- Declare global `qbit q[2];`
- Apply H(q[0]) and H(q[1]) to create superposition.
- Apply Rz(pi/3.0, q[0]) and Rz(pi/3.0, q[1]) to encode data.
- Apply H(q[0]) and H(q[1]) again (basis change back).
- Apply CNOT(q[0], q[1]) for entanglement.
- Measure both qubits.

Note: The sequence H-Rz(theta)-H is equivalent to Rx(theta), which rotates around the X-axis on the Bloch sphere.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement quantum kernel feature map circuit.

H-Rz(theta)-H is equivalent to Rx(theta).
Rx(pi/3)|0> = cos(pi/6)|0> - i*sin(pi/6)|1>.
P(0) = cos^2(pi/6) = 3/4, P(1) = sin^2(pi/6) = 1/4.

Before CNOT: product state with P(q0=0)=3/4, P(q0=1)=1/4, same for q1.
After CNOT(q[0],q[1]): flips q[1] when q[0]=1.

P(00) = P(q0=0)*P(q1=0) = 9/16 = 0.5625
P(01) = P(q0=0)*P(q1=1) = 3/16 = 0.1875
P(10) = P(q0=1)*P(q1_flipped=1) = 1/4 * 1/4 = 0.0625
P(11) = P(q0=1)*P(q1_flipped=0) = 1/4 * 3/4 = 0.1875

Note: This works because Rx only introduces imaginary phase, so CNOT on the computational basis amplitudes gives these clean fractions.

## isqExpand/front/123

- task_id: `isqExpand/front/123`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `expert`
- concept_tags: `quantum_error_correction`, `Knill-Laflamme_condition`, `code_distance`, `QEC`, `quantum_information_theory`
- source: `qa_pipeline`
- dataset_index: `5074`

### Prompt

什么是量子纠错的Knill-Laflamme条件？它给出了量子码纠错能力的充要条件是什么？

### Chain-of-thought reasoning

首先回顾量子纠错的基本框架：一个量子码需要能在错误发生后恢复原始编码信息。Knill和Laflamme在1997年给出了判断一个码能否纠正特定错误集的充要条件。推导思路如下：(1) 纠错过程等价于存在一个恢复算子R，使得对所有码字|ψ⟩和错误E_a，有R·E_a|ψ⟩ ∝ |ψ⟩；(2) 通过Fuchs–van de Graaf不等式和No-cloning定理的约束，可以证明这等价于要求⟨ψ_i|E_a†E_b|ψ_j⟩ = δ_{ij}·c_{ab}；(3) 直观理解：δ_{ij}保证不同码字不被错误混淆，c_{ab}仅依赖错误类型保证恢复操作不依赖具体码字。该条件既适用于一般错误模型，也适用于Pauli错误（此时简化为检查Pauli算子在码空间上的矩阵元）。码距d≥2t+1的判据是该条件在t-量子比特错误集上的直接推论。

### Reference answer

Knill-Laflamme条件是量子纠错理论中最核心的数学判据之一，由Emanuel Knill和Raymond Laflamme于1997年提出。

**数学表述：**
设量子码的码空间C由正交基{|ψ_i⟩}张成，{E_a}为一组可能的错误算子。该码能够纠正错误集{E_a}的充要条件是：

⟨ψ_i| E_a† E_b |ψ_j⟩ = δ_{ij} · c_{ab}

对所有码字|ψ_i⟩、|ψ_j⟩和所有错误算子E_a、E_b成立。其中δ_{ij}是Kronecker delta，c_{ab}是与码字无关（仅依赖于错误下标a,b）的常数，E_a†是E_a的厄米共轭。

**充要条件的物理含义：**
该条件可以分解为两个要求：
1. **正交性（可区分性）：** 不同错误将码空间映射到相互正交的子空间，使得我们可以通过测量来识别发生了哪个错误（对应off-diagonal部分i≠j时必须为零）。
2. **保距性（可恢复性）：** 同一个错误对码空间中所有态的作用方式相同（不依赖于i=j的具体取值，仅由c_{aa}决定），使得我们可以在不破坏编码信息的前提下施加恢复操作。

**与码距的关系：**
若码距为d，则码能纠正任意t个量子比特上的错误，条件为d ≥ 2t + 1。Knill-Laflamme条件对此提供了严格的数学刻画：对所有权重不超过t的Pauli错误P_a、P_b，验证上述条件即可确认码的纠错能力。

**重要性：**
该条件将量子纠错码的设计从物理直觉提升为可系统验证的数学框架，是构造和分析所有量子纠错码（如Steane码、Surface码等）的基础工具。

## isqExpand/front/106

- task_id: `isqExpand/front/106`
- task_type: `output_prediction`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `qaoa`, `output_prediction`, `phase_manipulation`, `interference`
- source: `isq_expansion`
- dataset_index: `230`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[2];

procedure main() {
    // QAOA-style circuit
    H(q[0]); H(q[1]);
    // Cost layer: ZZ with gamma = pi/4
    CNOT(q[0], q[1]);
    Rz(pi/2.0, q[1]);
    CNOT(q[0], q[1]);
    // Mixer layer: Rx with beta = pi/6
    Rx(pi/3.0, q[0]);
    Rx(pi/3.0, q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. |00> -> H,H -> (|00>+|01>+|10>+|11>)/2
2. ZZ(pi/4) via CNOT-Rz(pi/2)-CNOT:
   - |00>: eigenvalue Z0Z1 = +1, phase e^{-i*pi/4}
   - |01>: eigenvalue -1, phase e^{+i*pi/4}
   - |10>: eigenvalue -1, phase e^{+i*pi/4}
   - |11>: eigenvalue +1, phase e^{-i*pi/4}
3. After ZZ: (e^{-i*pi/4}|00> + e^{i*pi/4}|01> + e^{i*pi/4}|10> + e^{-i*pi/4}|11>)/2
4. Rx(pi/3) on each qubit (product rotation):
   The mixer with beta=pi/6 is relatively weak. Numerical computation yields:
   P(|00>) = P(|11>) = 0.4665
   P(|01>) = P(|10>) = 0.0335

The circuit concentrates probability on same-parity states, showing these QAOA parameters are suboptimal for Max-Cut.

### Reference answer

{'predicted_probs': {'0': 0.4665, '1': 0.0335, '2': 0.0335, '3': 0.4665}, 'explanation': 'This is a 1-layer QAOA circuit with gamma=pi/4 and beta=pi/6 for Max-Cut on a single edge.\n\n1. H on both qubits: uniform superposition (1/2, 1/2, 1/2, 1/2).\n2. Cost layer ZZ(pi/4): same-parity states |00>,|11> get phase e^{-i*pi/4}, anti-aligned |01>,|10> get e^{+i*pi/4}.\n3. Mixer Rx(pi/3): with beta=pi/6 (weak mixer), the phase difference is only partially converted to amplitude difference.\n\nResult: P(|00>)=P(|11>)=0.4665, P(|01>)=P(|10>)=0.0335. The weak mixer (small beta) combined with moderate gamma actually amplifies the WRONG states (same-parity). This demonstrates that QAOA parameter optimization is crucial -- not all (gamma, beta) values produce good Max-Cut solutions.'}

## isqExpand/front/38

- task_id: `isqExpand/front/38`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `hamiltonian_simulation`, `zz_interaction`, `gate_decomposition`
- source: `isq_expansion`
- dataset_index: `1377`

### Prompt

Write isQ code for the following quantum task: implements the ZZ interaction gate e^{-i*theta*Z⊗Z} using CNOT and Rz gates.

The decomposition is:
CNOT(q[0], q[1]) -> Rz(2*theta, q[1]) -> CNOT(q[0], q[1])

Demonstrate with theta = pi/4 on the state |+⟩|+⟩.

Requirements:
- Declare global `qbit q[2];`
- Prepare |++⟩ with H gates.
- Apply ZZ(pi/4).
- Measure both qubits.
- The ZZ gate introduces a relative phase between |00⟩,|11⟩ and |01⟩,|10⟩ components.

### Chain-of-thought reasoning

## Reasoning
1. |++⟩ = (|00⟩+|01⟩+|10⟩+|11⟩)/2.
2. ZZ gate applies phases: e^{-i*pi/4} to |00⟩ and |11⟩ (eigenvalue +1), e^{+i*pi/4} to |01⟩ and |10⟩ (eigenvalue -1).
3. State becomes (e^{-i*pi/4}|00⟩+e^{i*pi/4}|01⟩+e^{i*pi/4}|10⟩+e^{-i*pi/4}|11⟩)/2.
4. Measurement probabilities: |amplitude|² = 1/4 for each, so uniform distribution P=0.25 each.

## isqExpand/front/40

- task_id: `isqExpand/front/40`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `hamiltonian_simulation`, `trotter_decomposition`, `symmetric_trotter`
- source: `isq_expansion`
- dataset_index: `369`

### Prompt

I need an isQ program to implements a second-order (symmetric) Trotter step for H = X₀ + Z₀Z₁.

The second-order Trotter formula for H = A + B is:
e^{-iHt} ≈ e^{-iAt/2} e^{-iBt} e^{-iAt/2}

Let A = X₀ (field term) and B = Z₀Z₁ (interaction term), with t = pi/4.

Requirements:
- Declare global `qbit q[2];`
- Half-step of X₀: Rx(pi/4.0, q[0]).
- Full step of Z₀Z₁: CNOT(q[0],q[1]), Rz(pi/2.0, q[1]), CNOT(q[0],q[1]).
- Half-step of X₀: Rx(pi/4.0, q[0]).
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. Start |00⟩.
2. Rx(pi/4, q[0]): rotates q[0] slightly. State: (cos(pi/8)|0⟩ - i*sin(pi/8)|1⟩)|0⟩.
3. ZZ gate: CNOT-Rz(pi/2)-CNOT applies phase based on ZZ eigenvalue.
4. Second Rx(pi/4, q[0]): completes the symmetric step.
5. The symmetric arrangement cancels first-order Trotter error.

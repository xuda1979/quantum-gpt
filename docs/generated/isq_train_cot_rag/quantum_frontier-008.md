# ISQ training COT RAG corpus: quantum_frontier shard 8

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/front/44

- task_id: `isqExpand/front/44`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `quantum_chemistry`, `vqe`, `hardware_efficient_ansatz`
- source: `isq_expansion`
- dataset_index: `3808`

### Prompt

I need an isQ program to implements a simple VQE ansatz for a 2-qubit system.

The hardware-efficient ansatz consists of:
1. Single-qubit Ry rotations (trainable parameters).
2. CNOT entangling gate.
3. Another layer of Ry rotations.

Use parameter values theta = [pi/3, pi/4, pi/6, pi/5] for the four Ry gates.

Requirements:
- Declare global `qbit q[2];`
- Apply Ry(pi/3.0, q[0]), Ry(pi/4.0, q[1]).
- CNOT(q[0], q[1]).
- Apply Ry(pi/6.0, q[0]), Ry(pi/5.0, q[1]).
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
The hardware-efficient ansatz uses alternating layers of single-qubit rotations and entangling gates. With the given parameter values, the circuit creates an entangled state whose measurement probabilities depend on the interplay of rotation angles and the CNOT gate.

## isqExpand/front/111

- task_id: `isqExpand/front/111`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `quantum_reservoir`, `fixed_entanglement`, `data_encoding`, `quantum_ml`
- source: `isq_expansion`
- dataset_index: `5719`

### Prompt

Write an isQ program that implements a simple quantum reservoir computing circuit.

Quantum reservoir computing uses a fixed (non-trainable) entangled quantum system as a reservoir, with classical data encoded via rotation gates. Only the readout (measurement) is trained classically.

Requirements:
- Declare global `qbit q[3];`
- Build the fixed reservoir: H(q[0]), CNOT(q[0], q[1]), CNOT(q[1], q[2]) to create entanglement.
- Encode classical data via rotation gates: Ry(pi/4.0, q[0]) and Ry(pi/3.0, q[1]).
- Measure all three qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement a quantum reservoir computing circuit.

1. Reservoir layer (fixed, non-trainable):
   - H(q[0]): creates superposition
   - CNOT(q[0],q[1]): entangles q[0] and q[1]
   - CNOT(q[1],q[2]): propagates entanglement to q[2]
   After reservoir: (|000⟩+|111⟩)/√2 (GHZ-like state)

2. Data encoding:
   - Ry(pi/4, q[0]): encodes first data feature
   - Ry(pi/3, q[1]): encodes second data feature
   The reservoir entanglement ensures data features interact through quantum correlations.

3. Measurement: all 3 qubits measured for classical readout.

Probabilities: [0.3201, 0.0183, 0.1067, 0.0549, 0.0549, 0.1067, 0.0183, 0.3201].

## isqExpand/front/94

- task_id: `isqExpand/front/94`
- task_type: `bug_fix`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `trotter_decomposition`, `bug_fix`, `wrong_angle`, `zz_decomposition`
- source: `isq_expansion`
- dataset_index: `1485`

### Prompt

Something is wrong with this isQ circuit. Identify the error and provide the corrected code.

```isq
import std;
qbit q[2];

procedure main() {
    // Half-step X
    Rx(pi/4.0, q[0]);
    Rx(pi/4.0, q[1]);
    // Full ZZ step (BUG: wrong Rz angle)
    CNOT(q[0], q[1]);
    Rz(pi/4.0, q[1]);
    CNOT(q[0], q[1]);
    // Half-step X
    Rx(pi/4.0, q[0]);
    Rx(pi/4.0, q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
The second-order Trotter formula for H = ZZ + X0 + X1, t = pi/4:
S2(t) = e^{-i(X)(t/2)} e^{-i(ZZ)t} e^{-i(X)(t/2)}

For the ZZ decomposition: e^{-i(Z0Z1)t} = CNOT Rz(2t, q1) CNOT
With t = pi/4, the Rz angle should be 2t = pi/2.

The bug: Rz(pi/4.0) instead of Rz(pi/2.0). This halves the effective ZZ coupling, making the simulation inaccurate.

Buggy result: approximately [0.3598, 0.2134, 0.2134, 0.2134] (equivalent to weaker ZZ coupling)
Correct result: [0.625, 0.125, 0.125, 0.125]

Fix: Change Rz(pi/4.0, q[1]) to Rz(pi/2.0, q[1]).

## isqExpand/front/130

- task_id: `isqExpand/front/130`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `feature_map`, `quantum_kernel`, `parameterized_circuit`, `Rz_encoding`, `CNOT_entanglement`
- source: `isq_expansion`
- dataset_index: `2153`

### Prompt

Create an isQ quantum circuit that a quantum kernel feature map circuit in isQ using 2 qubits. The circuit applies: H on both qubits, Rz(x1) on q[0], Rz(x2) on q[1], CNOT(q[0], q[1]), then Rz(x1*x2) on q[1]. Use x1 = 0.5 and x2 = 0.3 as concrete parameters. Declare qubits at global scope and implement inside procedure main().

### Chain-of-thought reasoning

Step 1: Start with |00⟩. After H⊗H we get (|00⟩+|01⟩+|10⟩+|11⟩)/2, all amplitudes equal 1/2.
Step 2: Rz(0.5) on q[0] adds phase e^{-i*0.25} to |0⟩_0 and e^{+i*0.25} to |1⟩_0. This only changes relative phases.
Step 3: Rz(0.3) on q[1] adds phase e^{-i*0.15} to |0⟩_1 and e^{+i*0.15} to |1⟩_1. Again only phases change.
Step 4: CNOT(q[0],q[1]) swaps |10⟩↔|11⟩. Each amplitude magnitude stays 1/2.
Step 5: Rz(0.15) on q[1] adds phases to |0⟩_1 vs |1⟩_1 components. Still only phases, magnitudes unchanged.
Result: All four computational basis states have amplitude magnitude |1/2|, so P(00)=P(01)=P(10)=P(11)=0.25. Rz gates and CNOT are phase/permuation operations that never change amplitude magnitudes from the H⊗H initialization.

## isqExpand/front/104

- task_id: `isqExpand/front/104`
- task_type: `bug_fix`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `qaoa`, `entanglement`, `phase_manipulation`
- source: `isq_expansion`
- dataset_index: `5779`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```isq
import std;
qbit q[2];

procedure main() {
    H(q[0]); H(q[1]);
    // Cost layer: ZZ interaction (BUG: missing second CNOT)
    CNOT(q[0], q[1]);
    Rz(2.0*pi/3.0, q[1]);
    // Missing: CNOT(q[0], q[1]);
    // Mixer layer
    Rx(2.0*pi/3.0, q[0]);
    Rx(2.0*pi/3.0, q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
The ZZ interaction requires three gates: CNOT-Rz-CNOT. The first CNOT computes parity (XOR) into the target qubit, Rz applies the phase based on parity, and the second CNOT uncomputes the parity.

Buggy behavior:
1. H|00> -> |++>
2. CNOT(0,1): creates entanglement (|00>+|01>+|11>+|10>)/2 in parity basis
3. Rz(2pi/3, q[1]): applies phase to q[1]
4. Without 2nd CNOT, q[1] remains entangled with q[0] in the wrong way
5. Mixer then acts on this incorrectly entangled state

Buggy output: [0.4375, 0.0625, 0.4375, 0.0625]
Correct output (with 2nd CNOT): [0.0625, 0.4375, 0.4375, 0.0625]

The fix amplifies |01> and |10> (Max-Cut solutions) instead of |00> and |10>.

## isqExpand/front/128

- task_id: `isqExpand/front/128`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `basic`
- concept_tags: `angle_encoding`, `ry_rotation`, `feature_encoding`, `data_embedding`
- source: `isq_expansion`
- dataset_index: `3803`

### Prompt

Implement a quantum circuit in isQ: implementing angle encoding for 2 features (x1=pi/4, x2=pi/3) using Ry rotations on 2 qubits. The program should apply Ry(pi/4) to qubit 0 and Ry(pi/3) to qubit 1, then measure both qubits.

### Chain-of-thought reasoning

For angle encoding, each feature value is encoded as a rotation angle on a separate qubit. With x1=pi/4 on qubit 0 and x2=pi/3 on qubit 1, we apply Ry(pi/4,q[0]) and Ry(pi/3,q[1]). The Ry(theta) gate transforms |0> to cos(theta/2)|0> + sin(theta/2)|1>. For qubit 0: Ry(pi/4)|0> gives P(0)=cos^2(pi/8)=0.8536, P(1)=sin^2(pi/8)=0.1464. For qubit 1: Ry(pi/3)|0> gives P(0)=cos^2(pi/6)=0.75, P(1)=sin^2(pi/6)=0.25. Since the qubits are independent, joint probabilities are products: P(00)=0.6402, P(01)=0.2134, P(10)=0.1098, P(11)=0.0366.

## isqExpand/front/116

- task_id: `isqExpand/front/116`
- task_type: `bug_fix`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `qcnn`, `convolutional_layer`, `missing_gate`, `quantum_neural_network`
- source: `isq_expansion`
- dataset_index: `5659`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```isq
import std;
qbit q[3];

procedure main() {
    // Prepare superposition input
    H(q[0]); H(q[1]); H(q[2]);
    // Convolutional layer: CNOT + Ry on adjacent pairs
    CNOT(q[0], q[1]);
    Ry(pi/4.0, q[1]);
    CNOT(q[1], q[2]);
    // BUG: missing Ry(pi/4.0, q[2]) here
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
The QCNN convolutional layer should apply the same filter (CNOT+Ry) to adjacent pairs:
- Pair (q[0], q[1]): CNOT(q[0],q[1]) then Ry(pi/4, q[1]) -- correct
- Pair (q[1], q[2]): CNOT(q[1],q[2]) then Ry(pi/4, q[2]) -- missing Ry!

Buggy probs: [0.037, 0.037, 0.213, 0.213, 0.037, 0.037, 0.213, 0.213] -- more uniform.
Correct probs: [0.011, 0.063, 0.063, 0.364, 0.011, 0.063, 0.063, 0.364] -- Ry shifts probability.

Fix: Add Ry(pi/4.0, q[2]) after CNOT(q[1], q[2]).

## isqExpand/front/152

- task_id: `isqExpand/front/152`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `quantum_repeater`, `entanglement_swapping`, `entanglement_purification`, `quantum_communication`, `quantum_internet`, `LOCC`
- source: `qa_pipeline`
- dataset_index: `1460`

### Prompt

什么是量子中继器？它如何利用纠缠交换和纠缠纯化实现远距离量子通信？

### Chain-of-thought reasoning

首先明确问题涉及三个核心概念：量子中继器、纠缠交换和纠缠纯化。需要从以下几个层面组织答案：（1）量子中继器的定义和存在动机——为什么不能直接放大量子信号（量子不可克隆定理），而需要全新的中继方案；（2）纠缠纯化的原理——如何从多对低质量纠缠对中提取高质量纠缠对，这是LOCC操作的典型应用；（3）纠缠交换的原理——Bell态测量如何将两段独立纠缠连接为一段远程纠缠，这是量子中继器逐层扩展距离的核心机制；（4）嵌套协议的整体工作流程——先在短段建立纠缠、纯化提升质量、交换扩展距离、再纯化、再交换，逐层递推；（5）实验现状与未来展望。答案需要涵盖数学直觉和物理图像，同时保持中文表述的准确性和专业性。

### Reference answer

量子中继器（Quantum Repeater）是量子通信网络中的核心设备，用于解决光子在长距离传输中因信道损耗和退相干导致的量子态衰减问题。其基本思想由Sangouard等人系统化，借鉴了经典通信中中继器的理念，但由于量子不可克隆定理的限制，不能简单地进行信号放大，而是通过纠缠分发、纠缠纯化和纠缠交换三个关键步骤来逐步建立远距离的高质量纠缠。

一、基本架构
量子中继器将一段长距离信道分为若干个较短的子段（elementary links）。在每个子段内，通过光纤或自由空间分别建立纠缠对。由于子段较短，纠缠对的保真度可以维持在一个可接受的水平。量子中继器网络中的节点配备量子存储器，能够存储纠缠态并在适当时机执行量子操作。

二、纠缠纯化（Entanglement Purification）
在实际信道中，由于噪声和损耗，分发的纠缠对的保真度会降低。纠缠纯化 protocol（如Deutsch协议、Bennett协议）通过消耗多对低保真度纠缠对，利用本地量子操作和经典通信（LOCC），概率性地获得较少的高保真度纠缠对。其基本原理是：对两对共享的纠缠态进行受控量子门操作和测量，根据测量结果保留或舍弃剩余的纠缠对，从而提升保真度。随着纯化轮次的增加，纠缠对的保真度可以无限趋近于理想的最大纠缠态。

三、纠缠交换（Entanglement Swapping）
纠缠交换是实现远距离纠缠连接的核心操作。假设Alice与中间节点共享纠缠对|Φ+⟩_A1,B1，中间节点与Bob共享纠缠对|Φ+⟩_B2,C1。中间节点对其持有的两个粒子B1和B2进行Bell态测量，则Alice的粒子A1和Bob的粒子C1将投影为纠缠态，尽管它们从未直接发生过相互作用。这就是纠缠交换。数学上，四个Bell态的张量积可以在另一组基下展开，使得Bell测量将远端粒子关联起来。

四、嵌套式工作流程
量子中继器采用嵌套（nested）协议：第一层，在所有相邻节点间建立纠缠对并进行纯化；第二层，通过纠缠交换将相邻的两个短段纠缠连接成一个较长的纠缠对，再对新获得的长距离纠缠对进行纯化；如此递推，逐层扩展纠缠距离，最终在最远的两个端点之间建立高保真度纠缠。每一层都先纯化再交换，确保纠缠质量不会在扩展过程中退化。

五、关键资源与性能指标
量子中继器的性能取决于量子存储器的存储时间、读出效率、纠缠分发速率以及纯化协议的成功概率。近期实验已在固态色心（NV中心）、囚禁离子、稀土掺杂晶体等平台上演示了量子中继器的基本单元操作。未来的量子互联网将依赖量子中继器网络来实现全球范围的量子密钥分发、分布式量子计算和量子传感等应用。

## isqExpand/front/33

- task_id: `isqExpand/front/33`
- task_type: `code_generation`
- category: `quantum_frontier`
- difficulty: `intermediate`
- concept_tags: `quantum_ml`, `quantum_convolution`, `translational_invariance`
- source: `isq_expansion`
- dataset_index: `591`

### Prompt

Implement a quantum circuit in isQ: implements a simple quantum convolutional layer on 4 qubits.

A quantum convolutional layer applies the same 2-qubit unitary to pairs of adjacent qubits (with periodic boundary):
- Apply Ry(pi/4) + CNOT to (q[0],q[1])
- Apply Ry(pi/4) + CNOT to (q[2],q[3])

This mimics the translational invariance of classical convolution.

Requirements:
- Declare global `qbit q[4];`
- Initialize q[0] to |1⟩ with X(q[0]).
- Apply the convolutional layer.
- Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
1. X(q[0]) -> |1000⟩.
2. conv_unit(q[0],q[1]): Ry(pi/4) on q[0] (which is |1⟩): Ry(pi/4)|1⟩ = -sin(pi/8)|0⟩+cos(pi/8)|1⟩. Then CNOT(q[0],q[1]) entangles them.
3. conv_unit(q[2],q[3]): Ry(pi/4) on q[2] (which is |0⟩): Ry(pi/4)|0⟩ = cos(pi/8)|0⟩+sin(pi/8)|1⟩. Then CNOT.
4. The probabilities depend on the full state evolution.

## isqExpand/front/103

- task_id: `isqExpand/front/103`
- task_type: `qa_concept`
- category: `quantum_frontier`
- difficulty: `difficult`
- concept_tags: `qaoa`, `phase_manipulation`, `entanglement`, `reversible_computing`
- source: `qa_pipeline`
- dataset_index: `1791`

### Prompt

解释如何将组合优化问题编码为Ising模型哈密顿量，特别是ZZ相互作用项在量子电路中的实现方式。为什么CNOT-Rz-CNOT分解能实现 e^{-i*theta*Z_i Z_j} 的演化？请从数学上推导。

### Chain-of-thought reasoning

## 推理
目标：从数学上推导CNOT-Rz-CNOT分解实现ZZ演化。

关键洞察：CNOT将两体ZZ算符共轭变换为单体Z算符。

推导路径：
1. CNOT作用：|a,b> -> |a, a XOR b>
2. Z_0 Z_1 的本征值 = (-1)^a * (-1)^b = (-1)^{a+b}
3. CNOT后，Z_1 的本征值 = (-1)^{a XOR b} = (-1)^{a+b mod 2}
4. 所以 CNOT^dag Z_1 CNOT = Z_0 Z_1
5. 共轭关系意味着：CNOT * f(Z_1) * CNOT = f(Z_0 Z_1)
6. 取 f = exp(-i*theta*·) 就得到 CNOT * Rz(2theta,q1) * CNOT = exp(-i*theta*Z0Z1)

### Reference answer

## 问题哈密顿量编码与ZZ分解

### Ising模型编码
通用Ising哈密顿量：
H = sum_{i<j} J_{ij} Z_i Z_j + sum_i h_i Z_i

常见编码示例：
- **Max-Cut**: H_C = sum_{(i,j) in E} Z_i Z_j，边对应ZZ耦合
- **调度问题**: 冲突作业对编码为ZZ项，时间约束编码为局部Z场
- **QUBO到Ising**: 二次无约束二元优化 x_i ∈ {0,1} 通过 x_i = (1-Z_i)/2 映射到 Z_i ∈ {-1,+1}

### ZZ演化的CNOT-Rz-CNOT分解

目标：实现 U = e^{-i*theta*Z_0 Z_1}

**数学推导**：

1. CNOT(0,1) 将 Z_0 Z_1 变换到 Z_1 的局部算符：
   CNOT^dagger (Z_0 Z_1) CNOT = Z_1
   这是因为 CNOT 将 |a,b> 映射为 |a, a⊕b>，而 Z_0 Z_1 测量两个比特的奇偶性。

2. 因此：
   CNOT * e^{-i*theta*Z_1} * CNOT = e^{-i*theta*Z_0 Z_1}

3. 而 e^{-i*theta*Z_1} 正是 Rz(2*theta) 作用在 q[1] 上（忽略全局相位）：
   Rz(2*theta) = e^{-i*theta*Z}

4. 完整证明：
   CNOT * Rz(2*theta, q[1]) * CNOT
   = CNOT * e^{-i*theta*Z_1} * CNOT
   = e^{-i*theta * CNOT^dagger Z_1 CNOT}
   = e^{-i*theta * Z_0 Z_1}

### isQ 中的实现
```isq
import std;
qbit q[2];
procedure zz_interact(double theta) {
    CNOT(q[0], q[1]);
    Rz(2.0*theta, q[1]);
    CNOT(q[0], q[1]);
}
procedure main() {
    H(q[0]); H(q[1]);
    zz_interact(pi/4.0);
    M(q[0]); M(q[1]);
}
```

### 注意事项
- Rz 的参数是 2*theta（不是 theta），因为 Rz(phi) = e^{-i*phi/2*Z}
- 对于多条边，各ZZ项按顺序施加（它们互相对易，所以顺序无关）
- 局部Z场 h_i Z_i 直接用 Rz(2*h_i, q[i]) 实现，无需CNOT

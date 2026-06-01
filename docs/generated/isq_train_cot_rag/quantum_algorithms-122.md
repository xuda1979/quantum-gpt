# ISQ training COT RAG corpus: quantum_algorithms shard 122

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2686

- task_id: `isqTrain/2686`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3512`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[5];

procedure main(){
    X(q[4]);
    for i in 0:5{ 
        H(q[i]);
    }
    CNOT(q[0], q[4]);
    CNOT(q[1], q[4]);
    CNOT(q[3], q[4]);
    for i in 0:5{ 
        H(q[i]); 
    }
    for i in 0:5{
        M(q[i]); 
    }
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a step-by-step reasoning for a given isQ quantum program.
    *   Format: "## Circuit Analysis", max 15 lines, Dirac notation, precise state evolution, end with probability distribution.
    *   Program:
        

2.  **Analyze the Circuit & State Evolution:**
    *   Initial state: $|00000\rangle$. Indices: $q_0, q_1, q_2, q_3, q_4$.
    *   `X(q[4])`: Flips $q_4$. State: $|00001\rangle$.
    *   `H(q[0:5])`: Apply Hadamard to all 5 qubits. State: $\frac{1}{\sqrt{32}} \sum_{x=0}^{31} (-1)^{x_4} |x\rangle$, where $x_4$ is the 4th bit of $x$. Alternatively: $|+\rangle|+\rangle|+\rangle|+\rangle|-\rangle$.
    *   `CNOT(q[0], q[4])`, `CNOT(q[1], q[4])`, `CNOT(q[3], q[4])`: These CNOTs target $q_4$. Flipping $q_4$ (which is $|-\rangle$) based on $q_0, q_1, q_3$ introduces phases.
        *   CNOT in the Hadamard basis acts like a controlled-Z (or phase kickback).
        *   Target $q_4$ is $|-\rangle$. Control $q_i$ toggles $|-\rangle \leftrightarrow -|-\rangle$. Thus, each CNOT flips the phase of the control qubit's $|1\rangle$ state (wait, let's trace exactly).
        *   State before CNOTs: $|+\rangle|+\rangle|+\rangle|+\rangle|-\rangle$.
        *   `CNOT(q[0], q[4])`: $|+\rangle \to |-\rangle$ if control was ... no, $|+\rangle|-\rangle \to |-\rangle|-\rangle$ is wrong.
        *   Let's use bitwise math: $|x_0 x_1 x_2 x_3 x_4\rangle \to (-1)^{x_4} |x_0 x_1 x_2 x_3 x_4\rangle$.
        *   Apply `CNOT(q[0], q[4])`: flips $x_4$ if $x_0=1$. Phase becomes $(-1)^{x_4 \oplus x_0}$.
        *   Apply `CNOT(q[1], q[4])`: phase becomes $(-1)^{x_4 \oplus x_0 \oplus x_1}$.
        *   Apply `CNOT(q[3], q[4])`: phase becomes $(-1)^{x_4 \oplus x_0 \oplus x_1 \oplus x_3}$.
        *   So the state is $\frac{1}{\sqrt{32}} \sum (-1)^{x_4 \oplus x_0 \oplus x_1 \oplus x_3} |x\rangle$.
        *   Let's separate this: $\frac{1}{\sqrt{2}} \sum_{x_4} (-1)^{x_4} |x_4\rangle \otimes \frac{1}{\sqrt{16}} \sum_{x_0,x_1,x_2,x_3} (-1)^{x_0 \oplus x_1 \oplus x_3} |x_0 x_1 x_2 x_3\rangle$.
        *   The $q_4$ part is $|-\rangle$.
        *   The $q_0,q_1,q_2,q_3$ part is $|-\rangle|-\rangle|+\rangle|-\rangle$.
        *   Let's check this: $|-\rangle|-\rangle|+\rangle|-\rangle = \frac{1}{4} \sum (-1)^{

### Reference answer

{'predicted_probs': {'11011': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/906

- task_id: `isqTrain/906`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_oracle`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `322`

### Prompt

Implement a quantum circuit in isQ: implements the bit_flip_oracle pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a bit-flip oracle for f(x) = x[0] XOR x[1] with input |10>, storing the result in an ancillary qubit.
2. **Qubits**: 3 qubits (q[0], q[1] as input; q[2] as output target); all measured.
3. **State evolution**:
   - Initial: |000⟩ → X(q[0]) → |100⟩
   - CNOT(q[0], q[2]) flips q[2] since q[0]=|1⟩ → |101⟩
   - CNOT(q[1], q[2]) no flip since q[1]=|0⟩ → |101⟩
   - H(q[0]) transforms q[0] from |1⟩ to |−⟩ = (|0⟩−|1⟩)/√2 → (|001⟩−|101⟩)/√2
   - H(q[0]) again: H∘H = I (identity), reverts q[0] to |1⟩ → |101⟩
4. **Expected result**: Final state |101⟩ yields measurement probability {|101⟩: 1.0}, demonstrating that f(1,0)=1 flipped the ancilla and the H-H pair canceled.

## isqTrain/2864

- task_id: `isqTrain/2864`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `multi_controlled_logic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1089`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[3];
procedure main() {
    X(q[0]);
    H(q[0]);
    CNOT(q[0], q[1]);
    H(q[0]);
    CNOT(q[0], q[2]);
    CNOT(q[2], q[1]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

Analyzing the isQ program step-by-step:
Initial state: |000⟩
X(q[0]): |100⟩
H(q[0]): 1/√2(|100⟩ + |000⟩) = 1/√2(|0⟩ + |1⟩)|00⟩₁₂
CNOT(q[0], q[1]): 1/√2(|110⟩ + |000⟩) = 1/√2(|0⟩|00⟩ + |1⟩|11⟩)₁₂
H(q[0]): 1/2(|0⟩(|00⟩-|11⟩) + |1⟩(|00⟩+|11⟩))₁₂
CNOT(q[0], q[2]): 1/2(|00⟩(|0⟩-|1⟩) + |10⟩(|0⟩+|1⟩))₀₂ + ... wait.
Let's trace carefully.
State is |q₀ q₂ q₁⟩ or standard order |q₀ q₁ q₂⟩. Let's stick to standard |q₂ q₁ q₀⟩ (qubit 2 is highest bit).
Initial: |000⟩
X(q[0]): |001⟩
H(q[0]): 1/√2(|001⟩ + |000⟩)
CNOT(q[0], q[1]): 1/√2(|011⟩ + |000⟩)
H(q[0]): 1/2 (|011⟩ - |010⟩ + |001⟩ + |000⟩)
CNOT(q[0], q[2]): 1/2 (|111⟩ - |110⟩ + |001⟩ + |000⟩)
CNOT(q[2], q[1]): 1/2 (|101⟩ - |110⟩ + |011⟩ + |000⟩)
Let's recheck CNOT(q[2], q[1]):
|111⟩ -> |101⟩
|110⟩ -> |100⟩ ... wait!
Wait, if control is q[2] and target is q[1].
Let's re-evaluate.
State before CNOT(q[2], q[1]) is 1/2(|000⟩ + |001⟩ + |111⟩ - |110⟩) (in order q₂ q₁ q₀)
Wait:
CNOT(q[0], q[2]):
State was 1/2(|000⟩ + |001⟩ - |010⟩ + |011⟩)
Apply CNOT(q[0], q[2]) (control=0, target=2):
|000⟩ -> |100⟩ (target is 2, wait. Qubit 0 is control, Qubit 2 is target. So |q₂ q₁ q₀⟩. q₀=1 means target q₂ is flipped.)
Let's write states in order q₀, q₁, q₂.
Initial: |0⟩|0⟩|0⟩
X(q[0]): |1⟩|0⟩|0⟩
H(q[0]): 1/√2(|0⟩+|1⟩)|0⟩|0⟩
CNOT(q[0], q[1]): 1/√2(|0⟩|0⟩|0⟩ + |1⟩|1⟩|0⟩)
H(q[0]): 1/2 (|0⟩|0⟩|0⟩ + |1⟩|0⟩|0⟩ + |0⟩|1⟩|0⟩ - |1⟩|1⟩|0⟩)
CNOT(q[0], q[2]):
1/2 (|0⟩|0⟩|0⟩ + |1⟩|0⟩|1⟩ + |0⟩|1⟩|0⟩ - |1⟩|1⟩|1⟩)
CNOT(q[2], q[1]):
1/2 (|0⟩|0⟩|0⟩ + |1⟩|0⟩|1⟩ + |0⟩|1⟩|0⟩ - |1⟩|1⟩|1⟩)
Wait, q[2] is the control, q[1] is the target.
In |0⟩|0⟩|0⟩ (q₀ q₁ q₂), q₂=0, so no flip.
In |1⟩|0⟩|1⟩, q₂=1, so q₁ (target) is flipped. |1⟩|1⟩|1⟩
In |0⟩|1⟩|0⟩, q₂=0, no flip. |0⟩|1⟩|0⟩
In |1⟩|1⟩|1⟩, q₂=1, target q₁ is flipped. |1⟩|0⟩|1⟩
So the state after CNOT(q[2], q[1]) is:
1/2 (|0⟩|0⟩|0⟩ + |1⟩|1⟩|1⟩

### Reference answer

{'predicted_probs': {'000': 0.25000000000000006, '010': 0.24999999999999994, '101': 0.24999999999999994, '111': 0.25000000000000006}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3656

- task_id: `isqTrain/3656`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `1173`

### Prompt

Implement a quantum circuit in isQ: 2-bit quantum phase estimation (QPE) to estimate the phase 3*pi/4 of a Rz rotation gate. Use:
1. Two precision qubits and one eigenstate qubit
2. Prepare eigenstate |1> on the target qubit
3. Apply controlled-Rz operations
4. Apply inverse QFT on precision register
5. Measure all qubits

### Chain-of-thought reasoning

Let me analyze this 2-bit QPE circuit step by step.

The goal is to estimate the phase 3π/4 of a Rz rotation gate using 2-bit quantum phase estimation.

Let me trace through the state evolution:

**Initial state:** |000⟩

**After X(q[2]):** |001⟩

**After H(q[0]), H(q[1]):** (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ |1⟩ = 1/2(|001⟩+|011⟩+|101⟩+|111⟩)

**Controlled-Rz operations:**

Rz(θ) applies phase e^{iθ/2} to |1⟩ and e^{-iθ/2} to |0⟩.

Wait, let me reconsider. The Rz gate is:
Rz(θ) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]

So Rz(θ)|1⟩ = e^{iθ/2}|1⟩

The phase we want to estimate is φ such that U|1⟩ = e^{iφ}|1⟩.

For Rz(2π·3/4) = Rz(3π/2):
Rz(3π/2)|1⟩ = e^{i·3π/4}|1⟩

So the phase is φ = 3π/4.

In binary, 3/4 = 0.11₂, so the 2-bit estimate should give 11.

Let me trace:

After H(q[0]), H(q[1]): 1/2(|001⟩+|011⟩+|101⟩+|111⟩)

**Controlled-Rz(2π·3/4, q[0], q[2]):**
When q[0]=|1⟩, apply Rz(3π/2) to q[2]. Since q[2]=|1⟩, this adds phase e^{i·3π/4}.

State: 1/2(|001⟩+|011⟩+e^{i3π/4}|101⟩+e^{i3π/4}|111⟩)

**Controlled-Rz(2π·3/4·2, q[1], q[2]):**
When q[1]=|1⟩, apply Rz(3π) to q[2]. Since q[2]=|1⟩, this adds phase e^{i·3π/2}.

State: 1/2(|001⟩+e^{i3π/2}|011⟩+e^{i3π/4}|101⟩+e^{i3π/4}·e^{i3π/2}|111⟩)
= 1/2(|001⟩+e^{i3π/2}|011⟩+e^{i3π/4}|101⟩+e^{i9π/4}|111⟩)

Note: e^{i9π/4} = e^{iπ/4}

So: 1/2(|001⟩-i|011⟩+e^{i3π/4}|101⟩+e^{iπ/4}|111⟩)

Now the precision qubits q[0], q[1] encode: 1/2(|00⟩|1⟩ + e^{i3π/2}|01⟩|1⟩ + e^{i3π/4}|10⟩|1⟩ + e^{iπ/4}|11⟩|1⟩)

Wait, let me be more careful with the bit ordering. The precision register is q[0] (LSB) and q[1] (MSB).

After controlled operations:
1/2(|00⟩ + e^{i2π·0·3/4}|10⟩ + e^{i2π·1·3/4}|01⟩ + e^{i2π·(3/4)(1+2)}|11⟩) ⊗ |1⟩

Hmm, let me reconsider the standard QPE formulation.

In QPE, if the eigenvalue is e^{2πiφ}, then after the controlled unitaries:
- For precision qubit j (counting from 0), we apply U^{2^j}
- The state becomes: 1/2^t Σ_k |k⟩ ⊗ e^{2πiφk}|ψ⟩

where k is the computational basis state of the precision register.

With q[0] as the least significant bit:
- q[0] controls U^1 (Rz(2π·3/4·1))
- q[1] controls U^2 (Rz(2π·3/4·2))

After Hadamards and controlled unitaries:
1/2(|0⟩_

## isqQA/quantum_algorithms/130_application_scenario

- task_id: `isqQA/quantum_algorithms/130_application_scenario`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `application_scenario`, `algorithm`, `门隐形传态`
- source: `qa_pipeline`
- dataset_index: `4986`

### Prompt

门隐形传态作为量子计算中的一种高级协议，不仅具有理论价值，在实际系统中也有着不可替代的作用。能否详细阐述门隐形传态在容错量子计算（特别是非克利福德门的实现）以及分布式量子网络中的具体应用场景与前景？并请使用isQ语言编写一段代码，演示如何通过门隐形传态机制将一个非克利福德门（如T门）应用到目标量子比特上。

### Reference answer

<thinking>
门隐形传态是将量子逻辑门的操作转化为纠缠资源的消耗和经典前馈控制的过程。在容错量子计算中，最重要的应用是“魔态注入”。由于可横向实现的通用量子门集往往不包括T门等非克利福德门，我们需要离线制备高保真度的“魔态”（例如T|+⟩），然后利用门隐形传态将T门“注入”到目标逻辑比特上。

数学推导：
假设目标态为 |ψ⟩ = α|0⟩ + β|1⟩。
辅助比特制备为魔态 |A⟩ = T|+⟩ = |0⟩ + e^{iπ/4}|1⟩。
整体状态为 (α|0⟩ + β|1⟩) ⊗ (|0⟩ + e^{iπ/4}|1⟩)。
作用 CNOT(目标比特, 辅助比特) 后，状态变为：
α|0⟩(|0⟩ + e^{iπ/4}|1⟩) + β|1⟩(|1⟩ + e^{iπ/4}|0⟩)
= (α|0⟩ + β e^{iπ/4}|1⟩)|0⟩ + (α e^{iπ/4}|0⟩ + β|1⟩)|1⟩。
测量辅助比特：
若结果为0：目标比特坍缩为 α|0⟩ + β e^{iπ/4}|1⟩ = T|ψ⟩。无需校正。
若结果为1：目标比特坍缩为 α e^{iπ/4}|0⟩ + β|1⟩ = e^{iπ/4} T^†|ψ⟩。由于 T = S T^†，且全局相位可忽略，我们需要对目标比特施加 S 门进行校正，即可得到 T|ψ⟩。

isQ代码编写：
1. 声明2个量子比特：q[0]为目标，q[1]为辅助。
2. 初始化q[0]为任意态，以模拟实际计算过程。
3. 在q[1]上准备魔态：H(q[1]); T(q[1]);
4. 执行纠缠：CNOT(q[0], q[1]);
5. 测量q[1]：r = M(q[1]);
6. 经典前馈：if(r==1) { S(q[0]); }
</thinking>

门隐形传态是将量子逻辑门的应用转化为消耗特定纠缠态（或魔态）并结合经典前馈控制的协议。在应用场景和未来前景方面，它主要解决了量子计算中的两大核心痛点：容错实现昂贵逻辑门以及分布式系统中的非局域操作。

1. 容错量子计算与魔态注入
在现代容错量子计算（如表面码架构）中，存在一个著名的“Eastin-Knill定理”，指出任何容错量子编码都无法横向实现通用量子门集。通常，克利福德门（如H, S, CNOT）可以很容易地横向实现且天然容错，但非克利福德门（如T门或Toffoli门）却无法直接容错实现。为了突破这一瓶颈，研究者利用门隐形传态技术结合魔态蒸馏。具体应用中，系统会“离线”消耗大量低质量纠缠态，制备出极少量但高保真度的T门魔态（即 T|+⟩ 态）。在实际算法需要执行T门时，只需将目标逻辑比特与魔态进行纠缠和测量，通过门隐形传态将T门“注入”到逻辑线路中。这种应用场景极大地降低了容错计算的在线门错误率，是目前实现通用容错量子计算机最可行的方案。

2. 分布式量子网络中的非局域门
随着量子计算机向模块化、集群化发展，未来的计算能力扩展依赖于将多个小型量子处理器连接成量子网络。在这些分布式节点之间传递量子态以实现两比特或多比特逻辑门面临极大的退相干风险。门隐形传态提供了一种优秀的替代方案：在分布式量子计算中，不同节点间的CNOT等双比特门可以通过门隐形传态技术，结合节点间的纠缠分发和经典的测量前馈来实现。这使得未来的量子云计算能够像经典分布式计算一样，跨越物理空间界限组合算力。

以下isQ代码演示了如何通过门隐形传态机制（即魔态注入方式）将一个非克利福德T门应用到目标量子比特上：

```isq
import std;

// 声明量子比特数组
qbit q[2];
int r;

procedure main() {
    // 假设 q[0] 是运行算法的目标比特
    // 初始化目标比特为一个任意叠加态，模拟复杂计算中间态
    Rx(0.6, q[0]);
    Ry(1.2, q[0]);

    // 【门隐形传态过程】
    // 1. 准备辅助态（魔态 |A> = T|+>）
    // q[1] 作为辅助比特
    H(q[1]);
    T(q[1]);

    // 2. 执行纠缠操作（目标比特作为控制，辅助比特作为目标）
    CNOT(q[0], q[1]);

    // 3. 测量辅助比特 q[1]
    // 注意：此时辅助比特的测量相当于在隐形传态中提取门操作的“隐变量信息”
    r = M(q[1]);

    // 4. 经典前馈与 Pauli 校正
    // 如果测量结果为 1，则系统坍缩为 T^†|ψ⟩ 等效状态，需要通过施加 S 门将其修正为 T|ψ⟩
    // 如果结果为 0，则已经成功应用了 T 门，无需操作
    if (r == 1) {
        S(q[0]);
    }

    // 此时，目标比特 q[0] 的状态精确等同于直接对其施加 T 门的结果
    // 成功在无需直接对目标比特调用 T 门的情况下，实现了非克利福德逻辑
}
```

## isqTrain/3784

- task_id: `isqTrain/3784`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4644`

### Prompt

Implement a quantum circuit in isQ: the Deutsch-Jozsa algorithm for a 2-input balanced oracle with truth table [0, 1, 1, 0]. Use the oracle keyword, prepare output in |-> state, apply Hadamard-oracle-Hadamard, measure input qubits. Result should be non-zero (balanced).

### Chain-of-thought reasoning

Let me trace through the Deutsch-Jozsa algorithm for a 2-input balanced oracle with truth table [0, 1, 1, 0].

1. **Goal**: Determine if the oracle f(x) is balanced or constant using Deutsch-Jozsa algorithm.

2. **Qubits**: 3 qubits - q[0], q[1] are inputs, q[2] is the output qubit. All 3 are measured.

3. **Step-by-step state evolution**:

**Initial state**: |000⟩

**After X(q[2])**: |001⟩

**After H(q[2])**: |01⟩ ⊗ |−⟩ where |−⟩ = (|0⟩ - |1⟩)/√2

**After H(q[0]) and H(q[1])**: 
|+⟩|+⟩|−⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩) ⊗ |−⟩

**Oracle f with truth table [0, 1, 1, 0]**:
f(00) = 0, f(01) = 1, f(10) = 1, f(11) = 0

The oracle transforms |x⟩|y⟩ → |x⟩|y ⊕ f(x)⟩

For |x⟩|−⟩, this becomes |x⟩(−1)^f(x)|−⟩ because:
|y ⊕ f(x)⟩ when y is in |−⟩ state gives (−1)^f(x)|−⟩

So after oracle:
(1/2)[(−1)^0|00⟩ + (−1)^1|01⟩ + (−1)^1|10⟩ + (−1)^0|11⟩] ⊗ |−⟩
= (1/2)[|00⟩ − |01⟩ − |10⟩ + |11⟩] ⊗ |−⟩

**After H(q[0]) and H(q[1])**:
H⊗2 applied to (1/2)[|00⟩ − |01⟩ − |10⟩ + |11⟩]

Let me compute this:
H⊗2|00⟩ = |++⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)
H⊗2|01⟩ = |+−⟩ = (1/2)(|00⟩ − |01⟩ + |10⟩ − |11⟩)
H⊗2|10⟩ = |−+⟩ = (1/2)(|00⟩ + |01⟩ − |10⟩ − |11⟩)
H⊗2|11⟩ = |−−⟩ = (1/2)(|00⟩ − |01⟩ − |10⟩ + |11⟩)

So H⊗2 applied to (1/2)[|00⟩ − |01⟩ − |10⟩ + |11⟩]:
= (1/2)[(1/2)(|00⟩+|01⟩+|10⟩+|11⟩) - (1/2)(|00⟩-|01⟩+|10⟩-|11⟩) - (1/2)(|00⟩+|01⟩-|10⟩-|11⟩) + (1/2)(|00⟩-|01⟩-|10⟩+|11⟩)]
= (1/4)[|00⟩+|01⟩+|10⟩+|11⟩ - |00⟩+|01⟩-|10⟩+|11⟩ - |00⟩-|01⟩+|10⟩+|11⟩ + |00⟩-|01⟩-|10⟩+|11⟩]

Let me collect terms for each basis state:

|00⟩: 1 - 1 - 1 + 1 = 0
|01⟩: 1 + 1 - 1 - 1 = 0
|10⟩: 1 - 1 + 1 - 1 = 0
|11⟩: 1 + 1 + 1 + 1 = 4

So the result is (1/4)(4)|11⟩ = |11⟩

Wait, but The predicted output {|110⟩: 0.5, |111⟩: 0.5}. Let me reconsider.

The output qubit q[2] is still in |−⟩ state after the oracle. So the full state after H on inputs:
|11⟩ ⊗ |−⟩ = |11⟩ ⊗ (1/√2)(|0⟩ - |1⟩)
= (1/√2)(|110⟩ - |111⟩)

So when we measure:
- |110⟩ with probability 0.5
- |111⟩ with probability 0.5

The measurement bitstring: earlier measured qubit = higher bit.
If we measure q

## isqTrain/1396

- task_id: `isqTrain/1396`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `97`

### Prompt

Write isQ code for the following quantum task: the Bernstein-Vazirani algorithm to find the secret string s = 0011 (MSB first). Use 4 input qubits and 1 ancilla.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Find the 4-bit secret string s = 0011 using the Bernstein-Vazirani algorithm.

**Qubits:** 4 input qubits (q[0..3]) and 1 ancilla (anc[0]); only input qubits are measured.

**State evolution:**
1. Initialize ancilla: X then H on anc[0] yields |0000⟩|−⟩
2. Superpose inputs: H⊗4 on q[0..3] yields (1/4)∑_x |x⟩|−⟩ = |++++⟩|−⟩
3. Oracle phase kickback: CNOT(q[2],anc[0]) and CNOT(q[3],anc[0]) encode s·x, mapping |x⟩|−⟩ → (−1)^(s·x)|x⟩|−⟩, giving (1/4)∑_x (−1)^(s·x)|x⟩|−⟩
4. Final Hadamard: H⊗4 transforms ∑_x (−1)^(s·x)|x⟩ → |s⟩ = |0011⟩ via inverse QFT identity

**Result:** The input register collapses to |0011⟩ with probability 1.0, revealing the secret string.

## isqTrain/4853

- task_id: `isqTrain/4853`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `boolean_logic`
- source: `isq_train_cot`
- dataset_index: `5130`

### Prompt

用isQ实现for HLF on 3 qubits with complete graph (all edges). H, CZ(0,1), CZ(0,2), CZ(1,2), H. Measure.

### Chain-of-thought reasoning

We need to generate a reasoning section for the given isQ program. The program implements the Hadamard-Layer-F (HLF) algorithm on 3 qubits with complete graph (all edges). The steps: H on all qubits, then CZ on all pairs (0,1), (0,2), (1,2), then H on all qubits, then measure. The expected measurement probabilities are {|001>: 0.25, |010>: 0.25, |100>: 0.25, |111>: 0.25}. So we need to explain the goal, number of qubits, state evolution, and why those probabilities arise.

The reasoning should be concise, 3-8 lines for simple circuits, up to 15 for complex. This is fairly simple.

Goal: Implement HLF on K3 to produce specific parity-based output distribution.

Number of qubits: 3 qubits, all measured.

State evolution:

1. Initial state |000>.
2. Apply H to each: becomes 1/√8 (|0>+|1>)^3 = 1/√8 ∑_{x∈{0,1}^3} |x>. (Uniform superposition over 8 basis states.)
3. Apply CZ on all edges (3 edges). CZ(x,y) applies phase -1 if both are 1. Equivalent to applying Z on each pair controlled by the other. The overall effect: for each basis state |x>, multiply by (-1)^{(x1*x2 + x1*x3 + x2*x3)}. Actually CZ(0,1) gives factor (-1)^{x0 x1}, CZ(0,2): (-1)^{x0 x2}, CZ(1,2): (-1)^{x1 x2}. So total phase = (-1)^{x0 x1 + x0 x2 + x1 x2}.
4. Apply H again. H on each qubit transforms basis states. The final state before measurement is H^{⊗3} * (phase state). The result is that only states with odd parity? Actually we can compute: After H, we get a state that is a superposition over all basis states with amplitudes given by the Hadamard transform of the phase vector. For HLF, it's known that the output is uniform over states with odd weight? Let's compute: The Hadamard transform of a function f(x) = (-1)^{x0 x1 + x0 x2 + x1 x2} yields amplitudes A(y) = 1/8 ∑_{x} (-1)^{x·y + x0 x1 + x0 x2 + x1 x2}. We can evaluate: For 3 qubits, the function is a quadratic form. The result is that A(y) = 0 unless y is in the set {001,010,100,111}? And those have amplitude 1/4? Actually probabilities 0.25 each, so amplitudes ±0.5. So indeed the final state is equal superposition of those four states. So we can describe: After second Hadamard, the state becomes (1/2)(|001> + |010> + |100> + |111>) up to phases. This yields equal probabilities 0.25 for each.

But need to reason step-by-step succinctly. We'll write:

- After H: state = |+>|+>|+> = (1/√8)∑_{x∈{0,1}^3}|x>.
- After CZ on all pairs: state = (1/√8)∑_x (-1)^{x0 x1 + x0 x2 + x1 x2}|x>.
- After second H: H⊗3 maps |x> to (1/√8)∑_y (-1)^{x·y}|y>. So final amplitude for |y> = (1/8)∑_x (-1)^{x·y + x0 x1 + x0 x2 + x1 x2}. This sum is 0 except for y = 001,010,100,111, where it equals ±1/2. Thus probabilities 0.25 each.

But we should keep it short. Could also argue using properties of HLF: the circuit implements the parity function measurement.

Given constraints: reasoning section must start with "## Reasoning". Output only the reasoning section, no code.

We need to produce a text block. Let's craft:

## Reasoning
Goal: Implement HLF on 3 qubits with complete graph K3 to produce uniform superposition over states with odd parity.
Qubits: 3 qubits, all measured.
State evolution:
- Start |000>.
- H⊗3 → |+⟩⊗3 = 1/√8 ∑_{x∈{0,

## isqExpand/algo/184

- task_id: `isqExpand/algo/184`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `vqe`, `hardware_efficient_ansatz`, `parameterized_circuit`, `entangling_layer`, `ry_gate`, `cnot`
- source: `isq_expansion`
- dataset_index: `345`

### Prompt

Implement a quantum circuit in isQ: a 2-qubit VQE hardware-efficient ansatz with Ry(1.0000) on q[0], Ry(0.5000) on q[1], followed by CNOT entangling layer and measurement.

### Chain-of-thought reasoning

Step 1: Compute state after Ry(1.0) on q[0] and Ry(0.5) on q[1]. Ry(theta)|0> = cos(theta/2)|0> + sin(theta/2)|1>. For q[0]: cos(0.5)|0> + sin(0.5)|1>. For q[1]: cos(0.25)|0> + sin(0.25)|1>. Product state amplitudes: a00=cos(0.5)*cos(0.25)=0.85048, a01=cos(0.5)*sin(0.25)=0.21713, a10=sin(0.5)*cos(0.25)=0.46439, a11=sin(0.5)*sin(0.25)=0.11862. Step 2: Apply CNOT(q[0],q[1]) which maps |00>->|00>, |01>->|01>, |10>->|11>, |11>->|10>. So final amplitudes become: |00>=0.85048, |01>=0.21713, |10>=0.11862, |11>=0.46439. Step 3: Compute probabilities by squaring: P(00)=0.85048^2=0.7230, P(01)=0.21713^2=0.0471, P(10)=0.11862^2=0.0141, P(11)=0.46439^2=0.2158. Sum=1.0000 verified.

## isqTrain/3798

- task_id: `isqTrain/3798`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `2756`

### Prompt

Implement a quantum circuit in isQ: the Bernstein-Vazirani algorithm to find secret string s=110. Use the oracle keyword with truth table encoding f(x) = s·x mod 2. Measure input qubits to recover s.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for the Bernstein-Vazirani algorithm.
The secret string is $s = 110$. This corresponds to a 3-bit string.
The oracle $f(x) = s \cdot x \mod 2$.
Truth table for $f(x)$ where $x \in \{000, 001, 010, 011, 100, 101, 110, 111\}$:
s=110:
000: 0
001: 0
010: 1
011: 1
100: 1
101: 1
110: 0
111: 0
Wait, s is 110. Let's check the dot product:
s[0]=1, s[1]=1, s[2]=0.
x=010: 1*0 + 1*1 + 0*0 = 1.
x=011: 1*0 + 1*1 + 0*1 = 1.
x=100: 1*1 + 1*0 + 0*0 = 1.
x=101: 1*1 + 1*0 + 0*1 = 1.
x=110: 1*1 + 1*1 + 0*0 = 0 mod 2.
x=111: 1*1 + 1*1 + 0*1 = 0 mod 2.
So the truth table is [0, 0, 1, 1, 1, 1, 0, 0]. This matches the reference.

Let's trace the state.
Initial state: $|0000\rangle$ (q[0] to q[3] where q[3] is the output qubit)
1. X(q[3]) -> $|0001\rangle$
2. H on all 4 qubits -> $\frac{1}{2^2} \sum_{x \in \{0,1\}^3} |x\rangle \otimes \frac{|0\rangle - |1\rangle}{\sqrt{2}} = \frac{1}{2^2} \sum_{x} |x\rangle (-1)^{f(x)} \frac{|0\rangle - |1\rangle}{\sqrt{2}}$
Wait, the phase kickback gives $(-1)^{f(x)}$ for the input qubits.
3. Apply f(q[0], q[1], q[2], q[3]):
State becomes $\frac{1}{2^2} \sum_{x} (-1)^{s \cdot x} |x\rangle \otimes \frac{|0\rangle - |1\rangle}{\sqrt{2}}$
4. Apply H on input qubits (q[0], q[1], q[2]):
The output qubit remains in $|-\rangle$.
The input qubits transform as $H^{\otimes 3} \left( \frac{1}{2^{3/2}} \sum_x (-1)^{s \cdot x} |x\rangle \right) = |s\rangle = |110\rangle$.
Wait, the reference code has a bug or a trick:
`for i in 0:3` applies H to q[0], q[1], q[2], and also q[3].
Wait, `0:3` means 0, 1, 2. It doesn't include 3.
Wait! In Python `range(3)` is 0, 1, 2. In isQ `for i in 0:3` means `0, 1, 2`.
So H is applied to q[0], q[1], q[2].
Let's re-read the reference:

If `0:3` is 0, 1, 2, then H is applied to q[0], q[1], q[2].
The output qubit q[3] is initialized to $|-\rangle$.
After the oracle, q[3] is still $|-\rangle$.
The second Hadamard loop `for i in 0:3 { H(q[i]); }` applies H to q[0], q[1], q[2].
So the input qubits become $|110\rangle$.
The output qubit remains $|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$.
So the final state is $|110\rangle \otimes \frac{|0\rangle - |1\rangle}{\sqrt{2}}$.
When we measure all 4 qubits, we get

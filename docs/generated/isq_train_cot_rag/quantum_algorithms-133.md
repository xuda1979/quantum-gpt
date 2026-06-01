# ISQ training COT RAG corpus: quantum_algorithms shard 133

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1154

- task_id: `isqTrain/1154`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3824`

### Prompt

Help me write isQ code that implements a variant of the mcmt_gate pattern using q[4] -> q[5]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a multi-controlled multi-target X gate with 2 controls and 2 targets on an expanded 5-qubit register.
2. **Qubits**: 5 qubits (q[0]-q[4]) declared globally; all are measured to verify the operation.
3. **State evolution**:
   - |00000⟩ → X(q[0])

## isqTrain/2920

- task_id: `isqTrain/2920`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2225`

### Prompt

Implement a quantum circuit in isQ: applies a controlled Rz rotation of 1*pi/4 radians. Put the control qubit in superposition with H, set the target to |1>, apply controlled Rz, then H on the control. Measure both.

Requirements:
- Declare `qbit q[2];` at global scope.
- Use `procedure main()` as entry point.
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Apply a controlled-Rz(π/4) with control in superposition and target in |1⟩, then interfere the control via H, creating a phase-kickback circuit.

2. **Qubits**: 2 qubits (`q[0]` control, `q[1]` target), both measured.

3. **State evolution**:
   - **Initial**: |00⟩
   - **H(q[0])**: (1/√2)(|00⟩ + |10⟩)
   - **X(q[1])**: (1/√2)(|01⟩ + |11⟩)
   - **ctrl Rz(π/4)**: applies exp(iπ/8) phase to |11⟩ component →

## isqTrain/2834

- task_id: `isqTrain/2834`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1977`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[1];
procedure main() {
    H(q[0]);
    Z(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state of q[0] is |0>.
2. H(q[0]) puts the state into superposition: (1/√2)|0> + (1/√2)|1> = |+>.
3. Z(q[0]) applies a phase flip to the |1> component, changing the state to (1/√2)|0> - (1/√2)|1> = |->.
4. Measuring the state |-> yields equal probabilities for both basis states.

Predicted probability distribution:
|0>: 0.5
|1>: 0.5

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqQA/quantum_algorithms/98_isq_implementation

- task_id: `isqQA/quantum_algorithms/98_isq_implementation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_implementation`, `algorithm`, `Grover算法的几何解释`
- source: `qa_pipeline`
- dataset_index: `1450`

### Prompt

请详细阐述Grover量子搜索算法的几何解释，并结合二维子空间中的态矢量旋转原理，给出在4个元素（2个量子比特）的数据库中搜索目标态|11>的完整isQ代码实现。

### Reference answer

<think>
本题的推理分为理论计算与代码结构设计两步。首先，从几何角度分析：Grover算法将量子态演化限制在由目标态和正交叠加态张成的二维子空间内。初始叠加态与正交态的夹角为$\theta/2$（其中$\sin(\theta/2) = 1/\sqrt{N}$）。每次Grover迭代（Oracle和扩散算子）等效于在平面内将态矢量向目标态旋转 $2\theta$ 角度。

其次，针对具体任务（$N=4$，目标态$|11\rangle$）推导参数：由于$N=4$，得出$\sin(\theta/2) = 1/2$，即$\theta/2 = \pi/4$。要使态矢量旋转至目标态（与目标态夹角为0），只需旋转$\pi/2$。因此，仅需1次Grover迭代即可达到100%的搜索成功率。

最后，基于理论结论映射isQ代码逻辑：1. 对2个量子比特应用Hadamard门构造均匀叠加；2. 利用受控Z门或组合门实现翻转$|11\rangle$相位的Oracle；3. 构建扩散算子（在H门基下等效于对$|00\rangle$的相位翻转）；4. 仅执行这唯一一次迭代后对两量子比特进行测量即可得出最终解答。
</think>

~-~-Grover算法的几何解释核心在于将复杂的量子态演化过程投影到一个二维平面中进行直观理解。假设在包含$N=2^n$个元素的数据库中搜索目标态$|w\rangle$。算法初始通过Hadamard门生成均匀叠加态：$|s\rangle = \frac{1}{\sqrt{N}}\sum_{x}|x\rangle$。此时，我们定义一个与目标态$|w\rangle$正交的态$|s'\rangle = \frac{1}{\sqrt{N-1}}\sum_{x \neq w}|x\rangle$。

初始态$|s\rangle$位于$|w\rangle$和$|s'\rangle$张成的二维平面内，可以表示为：
$|s\rangle = \sin(\theta/2)|w\rangle + \cos(\theta/2)|s'\rangle$
其中$\sin(\theta/2) = \frac{1}{\sqrt{N}}$，即初始态与$|s'\rangle$的夹角为$\theta/2$，与目标态的夹角为$\pi/2 - \theta/2$。

Grover迭代由两部分组成：
1. **Oracle操作**：$U_w = I - 2|w\rangle\langle w|$。几何上，这相当于将态矢量关于$|s'\rangle$轴进行反射。
2. **扩散操作**：$U_s = 2|s\rangle\langle s| - I$。几何上，这相当于将态矢量关于初始叠加态$|s\rangle$进行反射。

根据几何光学，两次连续的反射等价于一次旋转。每次Grover迭代都会使二维平面内的态矢量向目标态$|w\rangle$方向旋转$\theta$角度。经过大约$O(\sqrt{N})$次迭代后，态矢量将与$|w\rangle$几乎重合。

对于2量子比特系统（$N=4$），$\sin(\theta/2) = 1/2$，即$\theta/2 = 30^\circ$。初始态$|s\rangle$距离目标态$|11\rangle$（即$|w\rangle$）的角度为$60^\circ$。由于每次迭代旋转$\theta = 60^\circ$，因此只需要恰好1次迭代即可精准到达目标态。

以下是在isQ量子编程语言中实现该2比特Grover搜索算法的完整代码：~-~-

```isQ
// 引入标准库
import std;

// 全局声明两个量子比特，代表包含4个元素的搜索空间
qbit q[2];

// 程序主入口
procedure main() {
    // 步骤1：初始化均匀叠加态 |s>
    // 对所有量子比特施加Hadamard门，制备出 (|00>+|01>+|10>+|11>)/2
    H(q[0]);
    H(q[1]);

    // 步骤2：Grover迭代（对于N=4，仅需1次即可完成搜索）

    // (a) Oracle操作 U_w，几何上对应关于 |s'> 的反射
    // 对于目标态 |11>，相当于当且仅当q[0]和q[1]均为|1>时引入-1的相位
    // CZ门的作用正是如此，它给 |11> 态加上一个全局相位(-1)
    CZ(q[0], q[1]);

    // (b) 扩散操作 U_s，几何上对应关于 |s> 的反射
    // 将|s>反射操作转换到计算基下，等价于 H -> 翻转非|0>态相位 -> H
    // 再次应用Hadamard门，回到计算基
    H(q[0]);
    H(q[1]);

    // 对所有量子比特施加X门，使|0>态变成我们需要标记的态
    X(q[0]);
    X(q[1]);

    // 在计算基下，对|11>态（即原始的|00>态）施加相位反转
    CZ(q[0], q[1]);

    // 恢复量子比特状态
    X(q[0]);
    X(q[1]);

    // 再次应用Hadamard门，回到操作前的基
    H(q[0]);
    H(q[1]);

    // 步骤3：测量
    // 经过几何平面内60度的精准旋转，此时系统的态矢量已与 |11> 完全重合
    // 测量将以100%的概率坍缩到目标态
    M(q[0]);
    M(q[1]);
}
```
上述代码严格遵循了Grover算法的几何内涵，通过两次反射操作（CZ构成的Oracle以及H-X-CZ-X-H构成的Diffuser）实现了对目标态的精确概率放大。

## isqTrain/3434

- task_id: `isqTrain/3434`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1233`

### Prompt

Help me write isQ code that one Trotter step of the 2-qubit transverse-field Ising model H = -J*Z_0*Z_1 - h*(X_0 + X_1) in isQ.

One Trotter step decomposes as:
1. ZZ interaction: CNOT, Rz(2*J*dt), CNOT
2. Transverse field: Rx(2*h*dt) on each qubit

Use J=1.0, h=0.5, dt=0.5. Start from |00>.

Declare 2 qubits, measure both.

### Chain-of-thought reasoning

Let me analyze this step by step.

The goal is to implement one Trotter step of the transverse-field Ising model H = -J*Z_0*Z_1 - h*(X_0 + X_1).

Parameters: J=1.0, h=0.5, dt=0.5

The Trotter decomposition gives:
exp(-iHdt) ≈ exp(-i*J*dt*Z_0*Z_1) * exp(-i*h*dt*X_0) * exp(-i*h*dt*X_1)

Wait, actually for H = -J*Z_0*Z_1 - h*(X_0 + X_1):
exp(-iHdt) = exp(iJdt*Z_0*Z_1 + ihdt*X_0 + ihdt*X_1)

So we need:
exp(-iHdt) ≈ exp(iJdt*Z_0*Z_1) * exp(ihdt*X_0) * exp(ihdt*X_1)

For the ZZ interaction:
- CNOT, Rz(2*J*dt), CNOT implements exp(-i*J*dt*Z_0*Z_1) or exp(i*J*dt*Z_0*Z_1)?

Let me think more carefully. The CNOT-Rz-CNOT sequence implements:
CNOT(0,1) * (I⊗Rz(θ)) * CNOT(0,1)

When control is |0>, target gets Rz(θ) applied.
When control is |1>, target gets Rz(θ) applied (after CNOT flips it back).

Actually, this sequence implements:
exp(-iθ/2 * Z_0*Z_1) I think...

Let me recalculate. The standard result is that CNOT-Rz(2θ)-CNOT implements exp(-iθZ_1) when control is in |1>, and exp(-iθZ_1) when control is in |0>.

Actually, let me think again:
- For |00>: CNOT does nothing, Rz(2θ) on q1 gives e^{-iθ}|0> for |0> state, CNOT does nothing → e^{-iθ}|00>
- For |01>: CNOT flips q1 to |0>, Rz(2θ) gives e^{-iθ}|0>, CNOT flips back → e^{-iθ}|01>
- For |10>: CNOT flips q1 to |1>, Rz(2θ) on |1> gives e^{iθ}|1>, CNOT flips back → e^{iθ}|10>
- For |11>: CNOT flips q1 to |0>, Rz(2θ) gives e^{-iθ}|0>, CNOT flips back → e^{-iθ}|11>

Wait, that's not right either. Let me be more careful.

Rz(2θ) = [[e^{-iθ}, 0], [0, e^{iθ}]]

So Rz(2θ)|0> = e^{-iθ}|0>
Rz(2θ)|1> = e^{iθ}|1>

For CNOT-Rz(2θ)-CNOT on |00>:
- CNOT: |00> → |00>
- Rz(2θ) on q1: |00> → e^{-iθ}|00>
- CNOT: e^{-iθ}|00>

For |01>:
- CNOT: |01> → |01> (control is 0, target doesn't flip)
- Rz(2θ) on q1: |01> → e^{iθ}|01>
- CNOT: e^{iθ}|01>

For |10>:
- CNOT: |10> → |11>
- Rz(2θ) on q1: |11> → e^{iθ}|11>
- CNOT: e^{iθ}|10>

For |11>:
- CNOT: |11> → |10>
- Rz(2θ) on q1: |10> → e^{-iθ}|10>
- CNOT: e^{-iθ}|11>

So the matrix is:
|00> → e^{-iθ}|00>
|01> → e^{iθ}|01>
|10> → e^{iθ}|10>
|11> → e^{-iθ}|11>

This is exp(-iθ) * diag(1, e^{2iθ}, e^{2iθ}, 1) = e^{-iθ} * (I⊗I + e^{2iθ}|01><01| + e^{2iθ}|10><10|)

Hmm, let me think of this differently. The operator is:
U = diag(e^{-iθ}, e^{iθ},

## isqTrain/548

- task_id: `isqTrain/548`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `entanglement`, `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_if_else`, `isq_syntax_multi_register`, `isq_syntax_print`, `mid_circuit_measurement`
- source: `isq_train_cot`
- dataset_index: `4992`

### Prompt

Code this in isQ: implements a variant of the bell_state_preparation pattern using pool[3] -> pool[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The user wants to understand the quantum circuit described by the provided isQ code.

1.  **Goal:** The circuit implements state preparation and quantum teleportation-like operations on a 3-qubit register `q`, plus a dummy 4-qubit register `pool` to meet the "expanded qubit register" and "pool[3] -> pool[4]" requirements of the prompt (though the logic only uses `q`).
    Wait, looking at the code, it doesn't actually use `pool`. It just declares it.
    Wait, the prompt says: "Write an isQ program that implements a variant of the bell_state_preparation pattern using pool[3] -> pool[4]."
    But The implementation provided in the prompt does:
    
    This is standard Quantum Teleportation, but the initial state of the sender's qubit `q[0]` is prepared as $X|0\rangle = |1\rangle$, instead of an arbitrary state $|\psi\rangle$. The receiver's qubit is `q[2]`.
    The predicted measurement probabilities are for $|000\rangle$, $|011\rangle$, $|100\rangle$, $|111\rangle$? That makes no sense for the output of the whole program if `q` is the register.
    Let's trace the state of `q`.
    Initially: $|000\rangle$.
    `X(q[0])`: $|100\rangle$.
    `H(q[1])`: $\frac{1}{\sqrt{2}}(|10\rangle + |11\rangle) \otimes |0\rangle = \frac{1}{\sqrt{2}}(|100\rangle + |110\rangle)$.
    `CNOT(q[1], q[2])`: $\frac{1}{\sqrt{2}}(|100\rangle + |111\rangle)$.
    `CNOT(q[0], q[1])`: $\frac{1}{\sqrt{2}}(|110\rangle + |101\rangle)$.
    `H(q[0])`: $\frac{1}{\sqrt{2}}[ \frac{1}{\sqrt{2}}(|010\rangle - |110\rangle) + \frac{1}{\sqrt{2}}(|001\rangle + |101\rangle) ] = \frac{1}{2}(|010\rangle - |110\rangle + |001\rangle + |101\rangle)$.
    If we measure `q[0]`, `q[1]`, `q[2]`:
    Probabilities:
    `q[0]=0, q[1]=0, q[2]=1` -> `|001\rangle`: $1/4$ (which is $1$ in binary).
    `q[0]=0, q[1]=1, q[2]=0` -> `|010\rangle`: $1/4$ (which is $2$ in binary).
    `q[0]=1, q[1]=0, q[2]=1` -> `|101\rangle`: $1/4$ (which is $5$ in binary).
    `q[0]=1, q[1]=1, q[2]=0` -> `|110\rangle`: $1/4$ (which is $6$ in binary).
    The resulting probabilities should be $|000\rangle: 0.25$, $|011\rangle: 0.25$, $|100\rangle: 0.25$, $|111\rangle: 0.25$.
    Wait! Let's re-read the predicted output.
    $|000\rangle$, $|011\rangle$, $|100\rangle$, $|111\rangle$.
    This implies the state is $\frac{1}{2}(|000\rangle + |011\rangle + |100\rangle + |111\rangle) = \frac{1}{2}(|0\rangle + |1\rangle) \otimes (|00\rangle + |11\rangle)$.
    Let's check the code again.
    Maybe `X(q[0])` is not in the reference? No, it's there

## isqTrain/1121

- task_id: `isqTrain/1121`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `223`

### Prompt

Write an isQ program that implements the superdense_coding pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

The user wants me to generate reasoning for a superdense coding circuit in isQ.

Let me trace through the circuit step by step:

1. Start with |00⟩
2. H(q[0]) → (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2
3. CNOT(q[0], q[1]) → (|00⟩ + |11⟩)/√2 (Bell state |Φ+⟩)
4. Z(q[0]) → (|00⟩ - |11⟩)/√2 (Bell state |Φ-⟩)
5. X(q[0]) → (|10⟩ - |01⟩)/√2 = -( |01⟩ - |10⟩)/√2 = -|Ψ-⟩
6. CNOT(q[0], q[1]) → 
   Let me compute: CNOT on (|10⟩ - |01⟩)/√2
   |10⟩ → |11⟩
   |01⟩ → |00⟩
   So result: (|11⟩ - |00⟩)/√2
7. H(q[0]) → 
   H on first qubit:
   |11⟩ → |+1⟩ = (|01⟩ + |11⟩)/√2
   |00⟩ → |+0⟩ = (|00⟩ + |10⟩)/√2
   So: (|01⟩ + |11⟩ - |00⟩ - |10⟩)/2
8. X(q[0]) → flips first qubit
   |01⟩ → |11⟩
   |11⟩ → |01⟩
   |00⟩ → |10⟩
   |10⟩ → |00⟩
   Result: (|11⟩ + |01⟩ - |10⟩ - |00⟩)/2
9. X(q[0]) again → identity pair, should cancel
   Flips back: (|01⟩ + |11⟩ - |00⟩ - |10⟩)/2

Hmm, that doesn't give |11⟩ with probability 1. Let me reconsider.

Wait, let me re-examine the superdense coding protocol more carefully.

For superdense coding to transmit '11':
- After Bell state creation and encoding, Alice applies X then Z (or Z then X)

Actually, let me check: the standard encoding is:
- 00: I
- 01: X
- 10: Z
- 11: XZ (or ZX, depending on convention)

The decoding is:
1. CNOT(q[0], q[1])
2. H(q[0])

Let me trace with the standard approach for message '11':

Start: |00⟩
H(q[0]): (|00⟩ + |10⟩)/√2
CNOT(q[0], q[1]): (|00⟩ + |11⟩)/√2 = |Φ+⟩

For message '11', Alice applies X then Z (or Z then X depending on convention).

Convention 1: X then Z
X(q[0]): (|10⟩ + |01⟩)/√2 = |Ψ+⟩
Z(q[0]): (|10⟩ - |01⟩)/√2 = -|Ψ-⟩

Decoding:
CNOT(q[0], q[1]): 
|10⟩ → |11⟩
|01⟩ → |00⟩
Result: (|11⟩ - |00⟩)/√2

H(q[0]):
|11⟩ → (|01⟩ + |11⟩)/√2
|00⟩ → (|00⟩ + |10⟩)/√2
Result: (|01⟩ + |11⟩ - |00⟩ - |10⟩)/2

This is not |11⟩. So Z then X is wrong for this convention.

Let me try Z then X:
Z(q[0]): (|00⟩ - |11⟩)/√2 = |Φ-⟩
X(q[0]): (|10⟩ - |01⟩)/√2 = -|Ψ-⟩... wait
Actually: X|0⟩ = |1⟩, X|1⟩ = |0⟩
X(q[0]) on (|00⟩ - |11⟩)/√2 = (|10⟩ - |01⟩)/√2 = -( |01⟩ - |10⟩)/√2 = -|Ψ-⟩

Same thing. Hmm.

Let me try X then Z:
X(q[0]) on (|00⟩ + |11⟩)/√2 = (|10⟩ + |01⟩)/√2 = |Ψ+⟩
Z(q[0]) on |Ψ+⟩ = (|10⟩ - |01⟩)/√2 = -|Ψ-⟩

Same result either way. The issue is in the decoding.

Let me recheck with

## isqTrain/1000

- task_id: `isqTrain/1000`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `isq_syntax_for_loop`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4256`

### Prompt

帮我写一个isQ程序：implements a variant of the qdrift pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The user wants me to analyze the isQ program that implements a qdrift pattern variant. Let me understand what this program does.

The program uses a 4-qubit register q[4] and applies operations to q[0] and q[1] primarily. The key operations are:
1. Initialize q[0] to |1> with X gate, starting state is |10> for q[0], q[1]
2. Apply a qdrift sequence with ZZ, XX, ZZ, XX terms
3. q[2] and q[3] are unused and stay in |0>

Wait, let me re-read. The task says "qdrift pattern using q[2] -> q[4]" but looking at the code, the operations are on q[0] and q[1]. The register has 4 qubits (q[0] to q[3]), and q[2] and q[3] are never touched, staying in |0>.

Let me trace through the circuit:

Initial state: |0000>

After X(q[0]): |1000>

Now the qdrift sequence on q[0] and q[1]:

Sample 1: ZZ term (CNOT-Rz-CNOT)
- CNOT(q[0], q[1]): |1000> (control is |1>, target is |0>, so target becomes |1>) → |1100>
- Rz(pi/2, q[1]): applies Rz to q[1], phase rotation
- CNOT(q[0], q[1]): |1000> (flips back)

Wait, let me be more careful. CNOT(q[0], q[1]) with q[0]=|1>, q[1]=|0>:
|10> → |11>

So after first CNOT: |1100>

Rz(pi/2) on q[1]: this applies phase to |1> state of q[1]
Rz(θ)|0> = |0>
Rz(θ)|1> = e^{-iθ/2}|1>

So Rz(π/2)|1> = e^{-iπ/4}|1>

After Rz: e^{-iπ/4}|1100>

CNOT(q[0], q[1]): since q[0]=|1>, flips q[1]: |10> again
After CNOT: e^{-iπ/4}|1000>

Hmm, but this doesn't seem right for a qdrift implementation. Let me reconsider.

Actually, for qdrift, the ZZ interaction is implemented as exp(-i θ ZZ/2), which in circuit form is:
CNOT - Rz(θ) - CNOT on one qubit

The full operation on |10> would be:
ZZ|10> = -|10> (since Z⊗Z|10> = Z|1> ⊗ Z|0> = (-1)(1)|10> = -|10>)

So exp(-i θ ZZ/2)|10> = exp(iθ/2)|10>

Let me trace more carefully:

After X(q[0]): |1000>

ZZ term (sample 1):
CNOT(q[0], q[1]): |10> → |11>, so state is |1100>
Rz(π/2, q[1]): phase on q[1]'s |1>, so e^{-iπ/4}|1100>
CNOT(q[0], q[1]): |1100> → |1000>, state is e^{-iπ/4}|1000>

XX term (sample 2):
H(q[0]); H(q[1]): |10> → H⊗H|10> = (1/√2)(|0>-|1>) ⊗ (1/√2)(|0>+|1>) = (1/2)(|00>+|01>-|10>-|11>)

Wait, H|0> = |+> = (|0>+|1>)/√2, H|1> = |-> = (|0>-|1>)/√2

So H⊗H|10> = H|1> ⊗ H|0> = |-> ⊗ |+> = (1/√2)(|0>-|1>) ⊗ (1/√2)(|0>+|1>)
= (1/2)(|00>+|01>-|10>-|11>)

The state is now e^{-iπ/4} * (1/2)(|00>+|01>-|10>-|11>) ⊗ |00>

CNOT(q[0], q[1]): flips q[1] when q[0]=|1>
|00> → |00>
|01> → |01>
|10> →

## isqTrain/1390

- task_id: `isqTrain/1390`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1078`

### Prompt

Write isQ code for the following quantum task: the Bernstein-Vazirani algorithm to find the secret string s = 011 (MSB first). Use 3 input qubits and 1 ancilla.

### Chain-of-thought reasoning

## Reasoning
Goal: Find secret string s=011 using Bernstein-Vazirani algorithm with phase kickback.

Qubits: 3 input (q[0-2]) + 1 ancilla (anc[0]); measure only input register.

State evolution:
1. Initialize ancilla: X|0⟩=|1⟩, then H|1⟩=|−⟩=(|0⟩−|1⟩)/√2
2. Apply H to input register: |000⟩|−⟩ → |+++⟩|−⟩ = (1/√8)∑ₓ|x⟩|−⟩
3. Oracle for s=011 (bits at positions 1,2): CNOT(q[1],anc[0]) and CNOT(q[2],anc[0]) apply phase kickback, yielding (1/√8)∑ₓ(−1)^(x₁⊕x₂)|x⟩|−⟩ = (1/√8)∑ₓ(−1)^(s·x)|x⟩|−⟩
4. Apply H⊗³ to input register: H⊗ⁿ[∑ₓ(−1)^(s·x)|x⟩/√2ⁿ] = |s⟩ = |011⟩

Final state: |011⟩|−⟩, so measuring input qubits yields 011 with probability 1.0.

## isqTrain/3811

- task_id: `isqTrain/3811`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_deriving_gate`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2799`

### Prompt

I need an isQ program to the swap test to compare states |0> vs |1>. Use:
1. q[0] as ancilla, q[1] for state A, q[2] for state B
2. A controlled-SWAP (Fredkin) gate via CNOT+Toffoli
3. Hadamard on ancilla before and after CSWAP
4. Measure all 3 qubits. P(ancilla=0) = (1+|<A|B>|²)/2.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task type: reasoning generation for an isQ code (swap test comparing |0> and |1>).
    *   Input: isQ code for swap test, expected probs.
    *   Output: ONLY the "## Reasoning" section, concise (3-15 lines), using Dirac notation.

2.  **Analyze the Circuit (Swap Test):**
    *   Qubits: q[0] (ancilla), q[1] (state A), q[2] (state B).
    *   Initial state: |000>
    *   State Prep: q[1] = |0>, q[2] = |1> (via X). State becomes |0>_a ⊗ |0>_A ⊗ |1>_B = |001>.
    *   Swap Test Steps:
        1.  H(q[0]): Creates (|0>+|1>)/√2 ⊗ |0> ⊗ |1> = 1/√2 (|001> + |101>).
        2.  Controlled-swap (three-CNOT decomposition) (cswap): swaps q[1] and q[2] if q[0] is |1>.
            |0>_a ⊗ |0>_A ⊗ |1>_B + |1>_a ⊗ |0>_A ⊗ |1>_B
            becomes |0>_a ⊗ |0>_A ⊗ |1>_B + |1>_a ⊗ |1>_A ⊗ |0>_B.
            So state is 1/√2 (|001> + |110>).
        3.  H(q[0]): Applied to ancilla.
            |0>_a becomes (|0>+|1>)/√2.
            |1>_a becomes (|0>-|1>)/√2.
            State = 1/2 (|001> + |101> + |110> - |010>).
    *   Measurement: Probability of ancilla (q[0]) being |0> comes from terms |001> and |010>.
        Amplitude of |001> is 1/2. Amplitude of |010> is -1/2.
        Total probability P(q[0]=0) = |1/2|^2 + |-1/2|^2 = 1/4 + 1/4 = 1/2.
        P(|001>) = 0.25, P(|010>) = 0.25, P(|101>) = 0.25, P(|110>) = 0.25.

3.  **Draft the Reasoning:**
    *   Line 1: Goal. (Implement swap test to compare |0> and |1>, measuring overlap).
    *   Line 2: Qubits. (3 qubits: q[0] ancilla, q[1] state |0>, q[2] state |1>. All measured).
    *   Line 3-4: Evolution.
        *   Start: |000>. State prep (X on q[2]) -> |001>.
        *   H on ancilla: 1/√2 (|001> + |101>).
        *   Cswap (three-CNOT decomposition): 1/√2 (|001> + |110>).
        *   H on ancilla: 1/2 (|001> - |010> + |101> + |110>).
    *   Line 5: Probability breakdown. (Since <0|1>=0, ancilla=0 and 1 have equal 50% chance).
    *   Line 6: Final expected probabilities: {|001>: 0.25, |010>: 0.25, |101>: 0.25, |110>: 0.25}.

4.  **Refine and Format:**
    *   Check constraints: 3-15 lines, concise, precise Dirac notation.
    *   "## Reasoning" header.
    *   Check Toffoli cswap decomposition? (Just mention Cswap (three-CNOT decomposition) applies controlled swap). The prompt mentions the decomposition but for reasoning we can treat it as Cswap (three-CNOT decomposition). Let's state the effect: swaps q[1] and q[2] when q[0]=|1>.
    *   Wait, is the sign correct?
        1/√2 (|0>|01> + |1>|01>) -> Cswap (three-CNOT decomposition) -> 1/√2 (|0>|01> + |1>|10>)
        H on q[0]:
        1/2 [ (|0>+|1>)|01> + (|0>-|1>)|10> ]
        = 1/2 [ |001> + |101> + |010> - |110> ].

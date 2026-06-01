# ISQ training COT RAG corpus: quantum_algorithms shard 115

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3549

- task_id: `isqTrain/3549`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `phase_manipulation`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1358`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should 3-qubit Ising chain, 1 Trotter step.

### Chain-of-thought reasoning

## Bug Analysis

**1. Bug Identification**
The bug is in line 10 of the buggy code: `CNOT(q[1], q[0]);` — the first CNOT of the ZZ coupling between qubits 0 and 1 has reversed control/target. The two CNOTs in a ZZ coupling must share the same control and target to correctly implement $e^{-i\theta Z_0 Z_1}$.

**2. Fix**
Change `CNOT(q[1], q[0])` to `CNOT(q[0], q[1])` so both CNOTs use q[0] as control and q[1] as target.

**3. State Evolution (corrected)**
- Initial state: |000⟩
- After CNOT(q[0],q[1]) → Rz(0.6, q[1]) → CNOT(q[0],q[1]): applies $e^{-i0.3 Z_0 Z_1}$, state acquires phase on |000⟩ and |011⟩ relative to |010⟩ and |001⟩
- After CNOT(q[1],q[2]) → Rz(0.6, q[2]) → CNOT(q[1],q[2]): applies $e^{-i0.3 Z_1 Z_2}$, further phase accumulation
- After Rx(0.3) on all qubits: transverse field rotation creates small X-mixing, spreading amplitude across all basis states
- Final probabilities peak at |000⟩ ≈ 0.934, with small weights on single-excitation states ≈ 0.021, matching predicted output.

## isqTrain/971

- task_id: `isqTrain/971`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2508`

### Prompt

Write isQ code for the following quantum task: implements the lie_trotter pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for a quantum circuit implementing the Lie-Trotter pattern with an X-X pair before measurement to demonstrate gate cancellation.

Let me trace through the circuit:

1. Initial state: |00⟩
2. After X(q[0]): |10⟩
3. CNOT(q[0], q[1]): |11⟩ (control is 1, so target flips)
4. Rz(0.785398163397448, q[1]): This is Rz(π/4) on q[1]
   - |11⟩ → e^(-iπ/8)|11⟩
5. CNOT(q[0], q[1]): |11⟩ (control is still 1, target flips back) → Actually wait, let me think again.
   - After step 4, state is e^(-iπ/8)|11⟩
   - CNOT(q[0], q[1]): control q[0]=1, so flip q[1]. q[1] was |1⟩, now |0⟩
   - State: e^(-iπ/8)|10⟩

6. H(q[0]); H(q[1]):
   - |10⟩ → H⊗H → (|0⟩+|1⟩)/√2 ⊗ (|0⟩-|1⟩)/√2 = (|00⟩-|01⟩+|10⟩-|11⟩)/2

7. CNOT(q[0], q[1]):
   - |00⟩ → |00⟩
   - |01⟩ → |01⟩
   - |10⟩ → |11⟩
   - |11⟩ → |10⟩
   - State: (|00⟩-|01⟩+|11⟩-|10⟩)/2 = (|00⟩-|01⟩-|10⟩+|11⟩)/2

8. Rz(0.785398163397448, q[1]):
   - This applies phase to |*1⟩ components
   - |00⟩ → |00⟩
   - |01⟩ → e^(-iπ/8)|01⟩
   - |10⟩ → |10⟩
   - |11⟩ → e^(-iπ/8)|11⟩
   - State: (|00⟩ - e^(-iπ/8)|01⟩ - |10⟩ + e^(-iπ/8)|11⟩)/2

9. CNOT(q[0], q[1]):
   - |00⟩ → |00⟩
   - |01⟩ → |01⟩
   - |10⟩ → |11⟩
   - |11⟩ → |10⟩
   - State: (|00⟩ - e^(-iπ/8)|01⟩ - |11⟩ + e^(-iπ/8)|10⟩)/2

10. H(q[0]); H(q[1]):
   Let me apply H⊗H to each component:
   - H⊗H|00⟩ = (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 = (|00⟩+|01⟩+|10⟩+|11⟩)/2
   - H⊗H|01⟩ = (|0⟩+|1⟩)/√2 ⊗ (|0⟩-|1⟩)/√2 = (|00⟩-|01⟩+|10⟩-|11⟩)/2
   - H⊗H|10⟩ = (|0⟩-|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 = (|00⟩+|01⟩-|10⟩-|11⟩)/2
   - H⊗H|11⟩ = (|0⟩-|1⟩)/√2 ⊗ (|0⟩-|1⟩)/√2 = (|00⟩-|01⟩-|10⟩+|11⟩)/2

   State = [1/2] * [(|00⟩+|01⟩+|10⟩+|11⟩)/2 - e^(-iπ/8)(|00⟩-|01⟩+|10⟩-|11⟩)/2 - (|00⟩+|01⟩-|10⟩-|11⟩)/2 + e^(-iπ/8)(|00⟩-|01⟩-|10⟩+|11⟩)/2]

   Collecting terms:
   |00⟩: [1 + 1 + 1 + 1 - e^(-iπ/8)(1 - 1 + 1 - 1) - (1 + 1 - 1 - 1) + e^(-iπ/8)(1 - 1 - 1 +

## isqTrain/4107

- task_id: `isqTrain/4107`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `714`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[4];

procedure main() {
    X(q[2]);
    X(q[3]);

    H(q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 16.0, q[3], q[0]);
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[3], q[1]);
    H(q[2]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[3], q[2]);
    H(q[3]);
    CNOT(q[0], q[3]);
    CNOT(q[3], q[0]);
    CNOT(q[0], q[3]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[1]);
    CNOT(q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict the measurement output of an isQ circuit.
    *   Input: isQ code preparing a state with H, controlled-Rz, H, and CNOTs (swap gates).
    *   Format: "## Circuit Analysis\n..." ending with predicted probability distribution.
    *   Constraint: Concise reasoning, Dirac notation.

2.  **Analyze the Circuit:**
    *   Initial state: $|0000\rangle$ for q[0..3].
    *   `X(q[2]); X(q[3]);` -> State becomes $|0011\rangle$. (q[0] is MSB, q[3] is LSB, so q[3]=1, q[2]=1 -> |0011> = |3>).
    *   Wait, the controlled phase gates form a Quantum Fourier Transform (QFT) circuit.
    *   Let's check the structure:
        *   `H(q[0])`
        *   `ctrl Rz(pi/4, q[1], q[0])` -> wait, `ctrl Rz(2*pi/8, q[1], q[0])` = controlled phase $S$ (or $R_2$).
        *   `ctrl Rz(2*pi/16, q[2], q[0])` = controlled phase $T$ (or $R_3$).
        *   `ctrl Rz(2*pi/32, q[3], q[0])` = controlled phase $R_4$.
        *   `H(q[1])`, `CRz(pi/4, q[2], q[1])`, `CRz(pi/8, q[3], q[1])`.
        *   `H(q[2])`, `CRz(pi/4, q[3], q[2])`.
        *   `H(q[3])`.
    *   This is exactly the QFT matrix applied to the state $|0011\rangle$.
    *   After the QFT part, there are CNOT swaps:
        *   `CNOT(q[0], q[3]); CNOT(q[3], q[0]); CNOT(q[0], q[3]);` -> swap (three-CNOT decomposition)(q[0], q[3]).
        *   `CNOT(q[1], q[2]); CNOT(q[2], q[1]); CNOT(q[1], q[2]);` -> swap (three-CNOT decomposition)(q[1], q[2]).
    *   This is the standard bit-reversal at the end of QFT to correct the order!
    *   So the whole block from `H(q[0])` down to the CNOTs is exactly the standard QFT.
    *   Initial state before QFT: $|q_3 q_2 q_1 q_0\rangle = |1 1 0 0\rangle$ which corresponds to integer $j = 12$.
    *   Let's verify qubit ordering. q[0] is typically the most significant bit or least significant?
        *   In standard Qiskit/isQ notation, QFT on $|j\rangle$ where $j = \sum j_k 2^k$.
        *   If `X(q[2]); X(q[3]);` then $q_2=1, q_3=1$. So the state is $|q_3 q_2 q_1 q_0\rangle = |1100\rangle$.
        *   In integer representation (q[0] is $2^0$), $|1100\rangle = 1\cdot 8 + 1\cdot 4 = 12$. So $j=12$.
        *   QFT of $|12\rangle$ is $\frac{1}{\sqrt{N}} \sum_{k=0}^{N-1} e^{2\pi i j k / N} |k\rangle$.
        *   Since QFT is unitary and maps $|j\rangle$ to a uniform superposition of all states with different phases, the probability of measuring any basis state $|k\rangle$ is $|\frac{1}{\sqrt{N}}|^2 = \frac{1}{16}$.
    *   Let's double check this.
        *   QFT($|j\rangle$) = $\frac{1}{\sqrt{N}} \sum_{k=0}^{N-1} e^{2\pi i j k / N} |k\rangle$.
        *   The magnitude of every amplitude is exactly $1/\sqrt{N}$.
        *   The number of qubits $n=4$, so $N=16$

### Reference answer

Uniform distribution across 16 states

## isqTrain/938

- task_id: `isqTrain/938`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `194`

### Prompt

Help me write isQ code that implements the reversible_logic pattern but with a different initial state preparation (flip q[[0, 1]] -> q[2]).

### Chain-of-thought reasoning

## Reasoning

1. **Goal:** Implement a controlled-swap (three-CNOT decomposition) (controlled-swap operation (three-CNOT decomposition)) circuit where only q[2] is flipped to |1⟩ initially (instead of flipping q[0] and q[1]).

2. **Qubits:** 3 qubits (q[0], q[1], q[2]), all measured.

3. **State evolution:**
   - Initial: |000⟩
   - X(q[2]): |001⟩ (q[2] flipped to |1⟩)
   - ctrl swap_gate(q[0], q[1], q[2]): Control q[0] = |0⟩, so the swap (three-CNOT decomposition) is **not** activated
   - State remains |001⟩

4. **Why |001⟩ with probability 1:** Since the control qubit q[0] is |0⟩, the controlled-swap operation (three-CNOT decomposition) acts as identity. The prepared state |001⟩ is unchanged, so measurement deterministically yields |001⟩.

## isqTrain/3433

- task_id: `isqTrain/3433`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4668`

### Prompt

Implement the following in isQ: a single Trotter step of the 2-qubit Ising ZZ interaction exp(-i * theta * Z_0 Z_1) in isQ.

The ZZ interaction is decomposed as:
  CNOT(q[0], q[1]); Rz(2*theta, q[1]); CNOT(q[0], q[1])

Apply to |00> with theta = pi/4.
Then apply H to both qubits before measurement to probe the phase.

Declare 2 qubits, measure both.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a Trotter step of exp(-iθZ₀Z₁) with θ=π/4 on |00⟩, then probe the resulting phase via Hadamard measurements.
2. **Qubits**: 2 qubits declared (q[0], q[1]), both measured.
3. **State evolution**:
   - Start: |00⟩
   - CNOT(q[0], q[1]): |00⟩ (control=|0⟩, no flip)
   - Rz(π/2, q[1]): e^{-iπ/4}|00⟩ (global phase only, since target=|0⟩)
   - CNOT(q[0], q[1]): e^{-iπ/4}|00⟩ (no change)
   - H(q[0]): e^{-iπ/4} · (1/√2)(|00⟩ + |10⟩)
   - H(q[1]): e^{-iπ/4} · (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)
4. **Expected probabilities**: The final state is an equal superposition with global phase e^{-iπ/4}, giving uniform probabilities {|00⟩: 0.25, |01⟩: 0.25, |10⟩: 0.25, |11⟩: 0.25}.

## isqTrain/87

- task_id: `isqTrain/87`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `206`

### Prompt

实现以下量子计算任务（使用isQ）：implements the amplitude_amplification pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for an isQ quantum program that implements amplitude amplification with identity operations (X-X pair before measurement).

Let me analyze the circuit:

1. Initial state: |00>
2. After H(q[0]), H(q[1]): |++> = (|00> + |01> + |10> + |11>)/2
3. Oracle for |11>: my_cz applies CZ, which flips the phase of |11>
   State becomes: (|00> + |01> + |10> - |11>)/2
4. Diffuser:
   - H(q[0]), H(q[1]): transforms back to computational basis
   - X(q[0]), X(q[1]): flips all qubits
   - my_cz (CZ): applies controlled-Z
   - X(q[0]), X(q[1]): flips back
   - H(q[0]), H(q[1]): transforms again
   
The diffuser reflects about the mean/uniform superposition.

5. X(q[0]) followed by X(q[0]) = Identity (gate cancellation)
6. M(q[0]), M(q[1]): measurement

The amplitude amplification should amplify the |11> state to probability 1.

Let me trace through more carefully:

Initial: |00>
After H⊗H: |++> = (1/2)(|00> + |01> + |10> + |11>)

Oracle marks |11> with -1 phase:
State: (1/2)(|00> + |01> + |10> - |11>)

Diffuser:
The diffuser is 2H⊗2 - I, applied as:
H⊗H → X⊗X → CZ → X⊗X → H⊗H

Let me compute step by step:
After H⊗H on (1/2)(|00> + |01> + |10> - |11>):

H|0> = |+>, H|1> = |->
H⊗H applied:
|00> → |++>
|01> → |+->
|10> → |-+>
|11> → |-->

So the state becomes:
(1/2)(|++> + |+-> + |-+> - |-->)

Let me compute this in computational basis:
|++> = (|00> + |01> + |10> + |11>)/2
|+-> = (|00> - |01> + |10> - |11>)/2
|-+> = (|00> + |01> - |10> - |11>)/2
|--> = (|00> - |01> - |10> + |11>)/2

(1/2)(|++> + |+-> + |-+> - |-->) = (1/2) * (1/2) * (|00> + |01> + |10> + |11> + |00> - |01> + |10> - |11> + |00> + |01> - |10> - |11> - |00> + |01> + |10> - |11>)
= (1/4) * (2|00> + 2|01> + 2|10> - 4|11>)
= (1/2)(|00> + |01> + |10>) - |11>

Hmm, let me redo this calculation more carefully.

State after oracle: |ψ> = (1/2)(|00> + |01> + |10> - |11>)

Apply H⊗H:
Coefficient of |00>: (1/2)(1 + 1 + 1 + 1)/2 = 1
Coefficient of |01>: (1/2)(1 - 1 + 1 - 1)/2 = 0
Coefficient of |10>: (1/2)(1 + 1 - 1 - 1)/2 = 0
Coefficient of |11>: (1/2)(1 - 1 - 1 + 1)/2 = 0

So after H⊗H: |00>

Apply X⊗X: |11>

Apply CZ: -|11> (phase flip on |11>)

Apply X⊗X: -|00>

Apply H⊗H: -|++> = -(1/2)(|00> + |01> + |10> + |11>)

Wait, this doesn't seem right. Let me reconsider the diffuser.

The standard Grover diffuser is: 2|s><s| - I where |s> = |++>

In matrix form for 2 qubits:
H⊗H (2|0><0| - I) H⊗H = H⊗H X⊗2 (

## isqExpand/algo/72

- task_id: `isqExpand/algo/72`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `vqe`, `ansatz_design`, `hardware_efficient`, `uccsd`, `adapt_vqe`
- source: `qa_pipeline`
- dataset_index: `822`

### Prompt

VQE中的拟设（Ansatz）设计有哪些主要类型？请比较硬件高效拟设（Hardware-Efficient Ansatz）和问题启发拟设（Problem-Inspired Ansatz）的优缺点。

### Chain-of-thought reasoning

## 推理
目标：比较VQE中的拟设设计类型。

关键点：
1. HEA：Ry+CNOT交替层，硬件友好但可能产生贫瘠高原
2. 问题启发拟设（UCCSD等）：保持物理对称性，精度高但电路深
3. ADAPT-VQE：自适应构建，避免固定结构缺点
4. 核心权衡：表达能力 vs 可训练性 vs 硬件适配性
5. NISQ时代HEA更实用，容错时代问题启发拟设更有前景

### Reference answer

VQE的拟设设计直接决定了算法的表达能力和可训练性，是VQE成功的关键。

## 拟设类型

### 1. 硬件高效拟设（Hardware-Efficient Ansatz, HEA）

结构：交替的单量子比特旋转层和双量子比特纠缠层

```
[Ry层] → [CNOT层] → [Ry层] → [CNOT层] → ...
```

**优点**：
- 直接匹配硬件连接拓扑，门数少，适合NISQ设备
- 通用性强，不依赖特定问题结构
- 电路深度可控

**缺点**：
- 容易产生贫瘠高原
- 参数空间中大部分区域与目标态无关
- 对于化学模拟等特定问题效率不高

### 2. 问题启发拟设

#### UCCSD（酉耦合簇）
用于量子化学，基于经典耦合簇理论：
- 拟设形式：exp(T - T†)|HF>，T为激发算符
- 保持粒子数守恒和自旋对称性
- 电路深度大，门数多

#### 对称性保持拟设
利用问题的对称性约束参数空间：
- 粒子数守恒
- 自旋对称性
- 空间对称性

### 3. 自适应拟设（ADAPT-VQE）

从算符池中逐步选择梯度最大的算符构建拟设：
- 避免固定结构的浪费
- 自动确定电路深度
- 计算梯度选择过程开销大

## 比较总结

| 特性 | HEA | 问题启发 |
|------|-----|----------|
| 电路深度 | 浅 | 深 |
| NISQ适用性 | 高 | 低 |
| 表达能力 | 通用但低效 | 针对性强 |
| 贫瘠高原风险 | 高 | 低 |
| 化学精度 | 难以达到 | 可达到 |

## isQ示例（HEA）

```isq
import std;
qbit q[2];

procedure main() {
    // Layer 1
    Ry(pi/3.0, q[0]);
    Ry(pi/4.0, q[1]);
    CNOT(q[0], q[1]);
    // Layer 2
    Ry(pi/6.0, q[0]);
    Ry(pi/5.0, q[1]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

## isqTrain/3546

- task_id: `isqTrain/3546`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1809`

### Prompt

Fix the bug in the following isQ program.

Bug description: Missing Hadamard gate

The program should iSWAP decomposition, test on |10>.

### Chain-of-thought reasoning

The buggy code is missing an H gate on q[0] after the S gates and before the CNOT gates.

The buggy code has:

The fixed code adds `H(q[0]);` after the S gates:

Let me verify this is the correct iSWAP (custom gate) decomposition.

The iSWAP (custom gate) gate is:
$$iSWAP (custom gate) = \begin{pmatrix} 1 & 0 & 0 & 0 \\ 0 & 0 & i & 0 \\ 0 & i & 0 & 0 \\ 0 & 0 & 0 & 1 \end{pmatrix}$$

So iSWAP (custom gate) |10⟩ = i|01⟩.

Let me check the decomposition with the H gate included:

Starting with |10⟩.

After S(q[0]) and S(q[1]):
- S ⊗ S |10⟩ = S|1⟩ ⊗ S|0⟩ = i|1⟩ ⊗ |0⟩ = i|10⟩

After H(q[0]):
- H ⊗ I on i|10⟩ = i (H|1⟩ ⊗ |0⟩) = i (|−⟩ ⊗ |0⟩) = i/√2 (|0⟩ − |1⟩) ⊗ |0⟩ = i/√2 (|00⟩ − |10⟩)

After CNOT(q[0], q[1]) with q[0] as control, q[1] as target:
- CNOT |00⟩ = |00⟩
- CNOT |10⟩ = |11⟩
- Result: i/√2 (|00⟩ − |11⟩)

After CNOT(q[1], q[0]) with q[1] as control, q[0] as target:
- CNOT|00⟩ = |00⟩
- CNOT|11⟩ = |01⟩ (q[1]=1 controls q[0], flipping q[0] from 1 to 0)
- Wait, let me think more carefully. |11⟩ means q[1]=1, q[0]=1. CNOT(q[1], q[0]) flips q[0] when q[1]=1. So q[0] goes from 1 to 0: |11⟩ → |01⟩
- Result: i/√2 (|00⟩ − |01⟩)

After H(q[1]):
- H on q[1]: |0⟩ → |+⟩ = (|0⟩+|1⟩)/√2, |1⟩ → |−⟩ = (|0⟩−|1⟩)/√2
- |00⟩ → (|0⟩+|1⟩)/√2 ⊗ |0⟩ = (|00⟩+|10⟩)/√2

Wait, I'm getting confused about the qubit ordering. Let me be careful.

In the state |ab⟩, which qubit is which? Conventionally, |ab⟩ means q[0]=a, q[1]=b... or does it?

Actually, in isQ and most quantum computing frameworks, q[0] is the first qubit. When we write |10⟩ for the state after X(q[0]), it means q[0]=1 and q[1]=0.

Let me redo this carefully.

State: |q[0], q[1]⟩

Starting: |00⟩
After X(q[0]): |10⟩ (q[0]=1, q[1]=0)

After S(q[0]): S|1⟩ = i|1⟩, so state becomes i|10⟩
After S(q[1]): S|0⟩ = |0⟩, so state stays i|10⟩

After H(q[0]): H|1⟩ = |−⟩ = (|0⟩-|1⟩)/√2
State: i/√2 (|00⟩ - |10⟩)

After CNOT(q[0], q[1]): q[0] is control, q[1] is target
- |00⟩ → |00⟩ (control=0, no flip)
- |10⟩ → |11⟩ (control=1, flip target)
State: i/√2 (|00⟩ - |11⟩)

After CNOT(q[1], q[0]): q[1] is control, q[0] is target
- |00⟩ → |00⟩ (control=0, no flip)
- |11⟩ →

## isqTrain/2786

- task_id: `isqTrain/2786`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2389`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```isq
import std;

qbit q[2];

procedure main(){
    H(q[0]);
    CNOT(q[1], q[0]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: In the CNOT gate call `CNOT(q[1], q[0])`, the control and target qubits are swapped. `q[1]` is used as control and `q[0]` as target, but for Bell state preparation, `q[0]` (the Hadamard-applied qubit in superposition) must be the control and `q[1]` the target.

2. **Fix**: Change `CNOT(q[1], q[0])` to `CNOT(q[0], q[1])`.

3. **State evolution (corrected)**:
   - |00⟩ → H(q[0]) → (|00⟩ + |10⟩)/√2
   - → CNOT(q[0], q[1]) → (|00⟩ + |11⟩)/√2
   - Measurement yields {|00⟩: 0.5, |11⟩: 0.5} ✓

## isqExpand/algo/9

- task_id: `isqExpand/algo/9`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `qpe`, `shor`, `phase_estimation`, `order_finding`
- source: `qa_pipeline`
- dataset_index: `2806`

### Prompt

什么是量子相位估计（QPE）？它在Shor算法中起什么作用？

### Chain-of-thought reasoning

## 推理
目标：解释QPE原理及在Shor算法中的角色。

关键概念：
1. QPE解决的是相位估计问题：U|ψ> = e^(2πiφ)|ψ>，找φ
2. 电路：H → 受控U^(2^k) → 逆QFT → 测量
3. Shor算法的关键步骤是找阶r，QPE通过估计相位k/r来找r
4. 连分数算法从近似的k/r中恢复精确的r

### Reference answer

## 量子相位估计（QPE）

量子相位估计是一个核心子程序，用于估计酉算子U的本征值。

### 问题
给定酉算子U和其本征态|ψ>，其中 U|ψ> = e^(2πiφ)|ψ>，QPE的目标是估计未知相位φ。

### 电路结构
1. **t个计数量子比特**（精度比特）：初始化为|0>，经过H门变为均匀叠加
2. **受控U操作**：第k个计数比特控制 U^(2^k) 操作
3. **逆QFT**：对计数比特应用逆量子傅里叶变换
4. **测量**：计数比特的测量结果给出φ的t-bit近似

### 在Shor算法中的作用

Shor算法的核心是**求阶问题**（Order Finding）：找到最小正整数r使得 a^r ≡ 1 (mod N)。

1. 构造酉算子 U|x> = |ax mod N>
2. U的本征态 |u_k> 对应本征值 e^(2πik/r)
3. QPE估计相位 k/r
4. 通过连分数算法从 k/r 的近似中提取 r
5. 知道 r 后，用 gcd(a^(r/2)±1, N) 分解 N

### 关键点
- QPE的精度取决于计数量子比特数t：需要 t ≈ 2log(N) + 几个额外比特
- QPE是许多量子算法（Shor、HHL、量子模拟）的核心组件

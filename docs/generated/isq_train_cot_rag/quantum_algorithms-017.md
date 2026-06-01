# ISQ training COT RAG corpus: quantum_algorithms shard 17

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1160

- task_id: `isqTrain/1160`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3434`

### Prompt

实现以下量子计算任务（使用isQ）：implements the mcmt_gate pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a multi-controlled multi-target X gate with 2 controls and 2 targets, measuring in reversed order.
2. **Qubits**: 4 qubits total — q[0], q[1] as controls, q[2], q[3] as targets; all measured in reverse order (q[3] first, q[0] last).
3. **State evolution**:
   - |0000⟩ → X(q[0])X(q[1]) → |1100⟩ (both controls set to |1⟩)
   - → ctrl ctrl X(q[0],q[1],q[2]) → |1110⟩ (first target flipped)
   - → ctrl ctrl X(q[0],q[1],q[3]) → |1111⟩ (second target flipped)
4. **Probability**: Final state is |1111⟩ with certainty; reversed measurement order maps q[3]=MSB down to q[0]=LSB, yielding {|1111⟩: 1.0}.

## isqExpand/algo/111

- task_id: `isqExpand/algo/111`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `reversible_computing`, `multi_controlled_logic`, `ancilla_usage`
- source: `isq_expansion`
- dataset_index: `1307`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```isq
import std;
qbit q[4];

procedure main() {
    X(q[0]); X(q[1]);
    Toffoli(q[0], q[1], q[2]);
    CNOT(q[0], q[3]);
    CNOT(q[1], q[3]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
Buggy: Toffoli -> q[2] (carry there), CNOTs -> q[3] (sum there). Swapped.
Fix: CNOTs -> q[2] (sum), Toffoli -> q[3] (carry).

A=1, B=1: Sum = 1 XOR 1 = 0, Carry = 1 AND 1 = 1.
Final: q[0]=1, q[1]=1, q[2]=0, q[3]=1 = |1101> = index 13.
Expected: 16-entry array, 1.0 at index 13.

## isqTrain/3664

- task_id: `isqTrain/3664`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `260`

### Prompt

实现以下量子计算任务（使用isQ）：3-bit quantum phase estimation for phase angle 7*pi/4 (in multiples of 2π/8). Use 3 precision qubits, controlled-Rz rotations, and a 3-qubit inverse QFT. Measure all 4 qubits (3 precision + 1 eigenstate).

### Chain-of-thought reasoning

Let me trace through this quantum phase estimation circuit carefully.

The goal is to implement 3-bit QPE for phase angle φ = 7π/4 = 7/8 × 2π.

We use 4 qubits: q[0], q[1], q[2] are precision qubits, q[3] is the eigenstate qubit.

**Step 1: Initialize**
All qubits start in |0⟩⊗4.

**Step 2: Prepare eigenstate**
X(q[3]) → |0001⟩

**Step 3: Hadamard on precision qubits**
H(q[0])H(q[1])H(q[2]) → (1/2√2)(|0⟩+|1⟩)(|0⟩+|1⟩)(|0⟩+|1⟩)|1⟩

**Step 4: Controlled-Rz rotations**

The unitary U = Rz(2π × 7/8) has eigenvalue e^(i×7π/4) for |1⟩ (since Rz(θ)|1⟩ = e^(-iθ/2)|1⟩, wait let me be more careful).

Actually, Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]

So Rz(2π × 7/8)|1⟩ = e^(i × 2π × 7/8 / 2)|1⟩ = e^(i × 7π/8)|1⟩

Hmm wait, but the phase should be 7/8 = 0.875. Let me think about this differently.

The eigenvalue of U on |1⟩ is e^(iφ) where we need to figure out what φ is.

U = Rz(2π × 7/8), so U|1⟩ = e^(i × 2π × 7/8 × 1/2)|1⟩ = e^(i × 7π/8)|1⟩

The phase is φ = 7π/8 = 0.875π. In units of 2π, this is 7/16 = 0.4375.

Hmm, but the problem says phase angle 7π/4 in multiples of 2π/8. So the phase φ = 7π/4 would mean the eigenvalue is e^(i×7π/4) = e^(i×7/8 × 2π), so in binary that's 0.111.

But with Rz, the eigenvalue on |1⟩ is e^(iθ/2) where θ = 2π × 7/8. So the eigenvalue is e^(i×7π/8), which corresponds to phase 7π/8, or in units of 2π, that's 7/16 = 0.0111 in binary.

Wait, but there's also a global phase. Rz(θ)|0⟩ = e^(-iθ/2)|0⟩. So there's a relative phase between the two eigenstates.

Actually, let me think about this differently. The controlled-Rz gate applies Rz(θ) to the target qubit when the control is |1⟩. 

For the eigenstate |1⟩:
- Controlled-Rz(θ) with control |1⟩ applies Rz(θ) to |1⟩
- Rz(θ)|1⟩ = e^(iθ/2)|1⟩
- But there's also the global phase factor e^(-iθ/2) from the other branch

Hmm, actually the controlled-Rz as implemented in isQ might behave differently. Let me think about what controlled Rz(θ, control, target) does.

If the control is |1⟩, it applies Rz(θ) to the target. So:
|0⟩_c|1⟩_t → |0⟩_c|1⟩_t
|1⟩_c|1⟩_t → e^(iθ/2)|1⟩_c|1⟩_t (up to global phase on the controlled branch)

Actually, controlled-Rz in most implementations only adds the phase to |1⟩|1⟩:
CRz(θ)|11⟩ = e^(iθ/2)|11⟩ (approximately, depends on implementation)

Let me just trace through the circuit and see what happens.

After Hadamards: state is (1/2√2) Σ_{k=0}^{7} |k⟩|1⟩ where k is a 3-bit number.

Then controlled-Rz rotations:
- q[0] controls Rz(2π × 7/8 × 1) on q[3]
- q[1] controls Rz(2π × 7/8 × 2) on

## isqTrain/4495

- task_id: `isqTrain/4495`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `reversible_computing`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1076`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;

qbit q[3];

procedure main() {
    
    X(q[2]);
    
    H(q[0]);
    
    ctrl CNOT(q[0], q[1], q[2]);
    ctrl CNOT(q[0], q[2], q[1]);
    ctrl CNOT(q[0], q[1], q[2]);
    
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ program:**
    *   `X(q[2]);` -> Initial state is $|q_0 q_1 q_2\rangle = |000\rangle$. Apply X to q[2] -> state becomes $|001\rangle$.
    *   `H(q[0]);` -> Apply H to q[0]. State becomes $\frac{1}{\sqrt{2}}(|001\rangle + |101\rangle)$. (Note: I will use qubit ordering $q_0$ is the leftmost/most significant, $q_2$ is rightmost/least significant).
    *   `ctrl CNOT(q[0], q[1], q[2]);` -> This is a Toffoli gate. The control qubits are $q_0$ and $q_1$, target is $q_2$.
    *   `ctrl CNOT(q[0], q[2], q[1]);` -> Toffoli gate. Controls: $q_0, q_2$, target: $q_1$.
    *   `ctrl CNOT(q[0], q[1], q[2]);` -> Toffoli gate. Controls: $q_0, q_1$, target: $q_2$.
    *   `H(q[0]); Z(q[0]); H(q[0]);` -> This is equivalent to X on $q_0$.
    *   `M(q[0]); M(q[1]); M(q[2]);` -> Measurement.

2.  **Trace the state evolution:**
    *   Initial: $|000\rangle$
    *   After `X(q[2])`: $|001\rangle$
    *   After `H(q[0])`: $\frac{1}{\sqrt{2}}(|001\rangle + |101\rangle)$
    *   Analyze the three Toffoli gates on the basis states:
        *   For $|001\rangle$: $q_0=0, q_1=0, q_2=1$.
            *   1st Toffoli (controls $q_0, q_1$, target $q_2$): $q_0, q_1$ are 0, so no change. State remains $|001\rangle$.
            *   2nd Toffoli (controls $q_0, q_2$, target $q_1$): $q_0=0, q_2=1$, so no change. State remains $|001\rangle$.
            *   3rd Toffoli: State remains $|001\rangle$.
            Wait, let's re-evaluate. The state is a superposition of $|001\rangle$ and $|101\rangle$. Let's trace each component independently.
        *   Component 1: $|001\rangle$ ($q_0=0$)
            *   1st Toffoli (c: $q_0, q_1$, t: $q_2$) -> target unchanged ($0 \land 0 = 0$) -> $|001\rangle$
            *   2nd Toffoli (c: $q_0, q_2$, t: $q_1$) -> target unchanged ($0 \land 1 = 0$) -> $|001\rangle$
            *   3rd Toffoli -> target unchanged -> $|001\rangle$
            So $|001\rangle \to |001\rangle$.
        *   Component 2: $|101\rangle$ ($q_0=1$)
            *   1st Toffoli (c: $q_0, q_1$, t: $q_2$) -> $1 \land 0 = 0$, target unchanged -> $|101\rangle$
            *   2nd Toffoli (c: $q_0, q_2$, t: $q_1$) -> $1 \land 1 = 1$, target $q_1$ flips (0 to 1) -> $|111\rangle$
            *   3rd Toffoli (c: $q_0, q_1$, t: $q_2$) -> $1 \land 1 = 1$, target $q_2$ flips (1 to 0) -> $|110\rangle$
            So $|101\rangle \to |110\rangle$.
    *   State after the three Toffoli gates: $\frac{1}{\sqrt{2}}(|001\rangle + |110\rangle)$.
    *   Apply `H(q[0]); Z(q[0]); H(q[

### Reference answer

{'predicted_probs': {'010': 0.5, '101': 0.5}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|010>) = 0.5000, P(|101>) = 0.5000.'}

## isqTrain/4548

- task_id: `isqTrain/4548`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `693`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[3];

procedure main() {
    
    H(q[2]);  // target different qubit
    H(q[1]);
    
    CNOT(q[1], q[2]);
    
    M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ program:**
    *   Initialization: 3 qubits `q[0], q[1], q[2]` initialized to $|000\rangle$.
    *   `H(q[2]);`: Apply Hadamard to qubit 2 (the third qubit). State: $|0\rangle \otimes |0\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = \frac{1}{\sqrt{2}}(|000\rangle + |001\rangle)$.
    *   `H(q[1]);`: Apply Hadamard to qubit 1 (the second qubit). State: $\frac{1}{\sqrt{2}} |0\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = \frac{1}{2}(|000\rangle + |001\rangle + |010\rangle + |011\rangle)$.
    *   `CNOT(q[1], q[2]);`: Apply CNOT with control=q[1] and target=q[2].
        *   $|000\rangle \to |000\rangle$
        *   $|001\rangle \to |001\rangle$
        *   $|010\rangle \to |011\rangle$
        *   $|011\rangle \to |010\rangle$
        Final state: $\frac{1}{2}(|000\rangle + |001\rangle + |011\rangle + |010\rangle) = \frac{1}{2}(|000\rangle + |001\rangle + |010\rangle + |011\rangle)$. Wait, no.
        Let's trace carefully.
        Initial: $|000\rangle$
        H(q[2]): $|00\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
        H(q[1]): $|0\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
        CNOT(q[1], q[2]):
        Control is q[1], target is q[2].
        $|000\rangle \to |000\rangle$
        $|001\rangle \to |001\rangle$
        $|010\rangle \to |011\rangle$
        $|011\rangle \to |010\rangle$
        Sum is $\frac{1}{2}(|000\rangle + |001\rangle + |011\rangle + |010\rangle)$.
        Reordering standard basis: $\frac{1}{2}(|000\rangle + |001\rangle + |010\rangle + |011\rangle)$. It's the same state! So $q[1]$ and $q[2]$ are in the $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$ state. They are unentangled. Wait, yes.
        Let's re-verify:
        CNOT(|+>|+>) = |+>|+> (actually).
        Control is $|+\rangle$, target is $|+\rangle$.
        $|+\rangle|+\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
        CNOT: $\frac{1}{2}(|00\rangle + |01\rangle + |11\rangle + |10\rangle) = |+\rangle|+\rangle$.
        So the state before measurement is $\frac{1}{2}(|000\rangle + |001\rangle + |010\rangle + |011\rangle)$.
    *   Measurement: Only `M(q[2])` is explicitly called in the code.
    *   Wait, the prompt says: "Expected measurement probabilities: {|000>: 0.5, |001>: 0.5}". Wait, why?
    *   Let me re-read the CNOT and the order of H gates.
    *   Wait! Is it `H(q[2])` then `H(q[1])` then `CNOT(q[1], q[2])`?
    *   Let's check The implementation provided in the prompt text!
    *   "Expected measurement probabilities: {|000>: 0.5, |001>: 0.5}"
    *   Wait, why is it

### Reference answer

{'predicted_probs': {'000': 0.5, '001': 0.5}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.5000, P(|001>) = 0.5000.'}

## isqTrain/3638

- task_id: `isqTrain/3638`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4162`

### Prompt

Code this in isQ: the 4-qubit QFT applied to input state |1010>. The circuit should use Hadamard gates, controlled-Rz rotations with angles 2π/2^k, and final bit-reversal swaps. Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Implement 4-qubit QFT on input state |1010⟩, measure all qubits.

**Qubits:** 4 qubits q[0..3], all measured.

**State evolution:**
1. Initialize |0000⟩, apply X(q[0]) and X(q[2]) → |1010⟩ (decimal 10, little-endian)
2. QFT qubit 0: H(q[0]) creates superposition, controlled-Rz(q[1]→q[0], π/2), Rz(q[2]→q[0], π/4), Rz(q[3]→q[0], π/8) add phase kicks
3. QFT qubit 1: H(q[1]) + Rz(q[2]→q[1], π/2) + Rz(q[3]→q[1], π/4)
4. QFT qubit 2: H(q[2]) + Rz(q[3]→q[2], π/2)
5. QFT qubit 3: H(q[3]) → produces QFT|10⟩ = (1/4)Σ_j exp(2πi·10·j/16)|j⟩
6. Bit-reversal swaps (q[0]↔q[3], q[1]↔q[2]) reorder output to standard ordering

**Probabilities:** QFT of computational basis state |k⟩ produces uniform superposition over all 2^n basis states with equal magnitude |1/2^n|. For n=4, all 16 outcomes have probability (1/4)² = 1/16 = 0.0625, regardless of the phase factors.

## isqTrain/2953

- task_id: `isqTrain/2953`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1231`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]);
    H(q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis

1. **Operations applied:**
   - H(q[0]) and H(q[1]): Hadamard on both qubits
   - CNOT(q[0], q[1]): q[0] controls q[1]
   - CNOT(q[1], q[0]): q[1] controls q[0]

2. **State evolution:**
   - Initial: |00⟩
   - After H⊗H: (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
   - After CNOT(q[0],q[1]): (|00⟩ + |01⟩ + |11⟩ + |10⟩)/2 (swaps |10⟩↔|11⟩)
   - After CNOT(q[1],q[0]): (|00⟩ + |11⟩ + |10⟩ + |01⟩)/2 (swaps |01⟩↔|11⟩)

3. **Final state:** (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2 — an equal superposition of all basis states.

4. **Probability distribution:** Each computational basis state has equal probability of 1/4.

Predicted probabilities: [0.25, 0.25, 0.25, 0.25]

### Reference answer

{'predicted_probs': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqQA/quantum_algorithms/104_math_derivation

- task_id: `isqQA/quantum_algorithms/104_math_derivation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `math_derivation`, `algorithm`, `Shor算法的周期查找`
- source: `qa_pipeline`
- dataset_index: `5169`

### Prompt

在Shor算法中，周期查找是实现大数质因数分解的核心步骤。假设我们需要寻找函数 f(x) = a^x \pmod N 的周期 r。请详细推导在量子Oracle作用后，第一寄存器（输入寄存器）的量子态演化过程，并进一步严密推导在经过量子傅里叶变换（QFT）后，第一寄存器的量子态表达式，解释为何此时进行测量能以极高的概率获得周期 r 的相关信息。

### Reference answer

<think>
Shor算法周期查找的推理核心在于利用量子叠加与相长干涉来提取隐藏的周期信息。推导过程可分为四个关键逻辑步骤：

1. **构建纠缠**：对输入寄存器施加Hadamard门生成均匀叠加态，随后通过Oracle计算模幂函数，使输入与输出寄存器产生紧密纠缠。
2. **引入周期坍缩**：测量输出寄存器得到特定结果。由于模幂函数具有周期 $r$，输入寄存器会相应坍缩为间隔严格等于 $r$ 的离散态叠加，形成空间上的周期性“梳状”分布。
3. **频域转换**：对该周期性态施加量子傅里叶变换（QFT）。数学上，QFT将空间域的周期结构映射为频域的概率幅峰值。计算求和时，非整数周期的相位会相消抵消，而满足 $c \approx kQ/r$ 的相位则发生相长干涉，使得概率幅高度集中。
4. **测量提取**：此时测量输入寄存器，系统将以极高的概率坍缩到这些干涉增强的峰值态 $c$ 上。由于 $c/Q$ 近似于 $k/r$，后续只需借助经典的连分数算法处理测量结果，即可高精度反推出目标周期 $r$。
</think>

<thinking>
为了推导Shor算法中周期查找的量子态演化，我们需要分步进行数学推导：
1. **初始化与Oracle作用**：
假设第一寄存器有 $n$ 个量子比特，大小 $Q = 2^n > N^2$。初始态为 $|0\rangle|0\rangle$。
经过Hadamard门后，第一寄存器处于均匀叠加态：$\frac{1}{\sqrt{Q}} \sum_{x=0}^{Q-1} |x\rangle |0\rangle$。
接着应用量子Oracle $U_f$，计算 $f(x) = a^x \pmod N$，量子态演化为：
$|\psi_1\rangle = \frac{1}{\sqrt{Q}} \sum_{x=0}^{Q-1} |x\rangle |f(x)\rangle$。

2. **测量第二寄存器与态坍缩**：
由于 $f(x)$ 具有周期 $r$，存在多个 $x$ 映射到同一个 $f(x)$ 值。假设我们测量第二寄存器，得到结果 $y = a^{x_0} \pmod N$。此时第一寄存器会坍缩到所有满足 $x \equiv x_0 \pmod r$ 的 $x$ 的叠加态。
设满足条件的 $x$ 的个数大约为 $A \approx Q/r$，则第一寄存器的态变为：
$|\psi_2\rangle = \frac{1}{\sqrt{A}} \sum_{k=0}^{A-1} |x_0 + kr\rangle$。

3. **量子傅里叶变换（QFT）**：
QFT 的作用定义为 $U_{QFT}|x\rangle = \frac{1}{\sqrt{Q}} \sum_{c=0}^{Q-1} e^{2\pi i x c / Q} |c\rangle$。
将 $U_{QFT}$ 作用于 $|\psi_2\rangle$，得到最终的态 $|\psi_3\rangle$：
$|\psi_3\rangle = \frac{1}{\sqrt{A}} \sum_{k=0}^{A-1} \left( \frac{1}{\sqrt{Q}} \sum_{c=0}^{Q-1} e^{2\pi i (x_0 + kr) c / Q} |c\rangle \right)$
$= \frac{1}{\sqrt{AQ}} \sum_{c=0}^{Q-1} e^{2\pi i x_0 c / Q} \left( \sum_{k=0}^{A-1} e^{2\pi i k r c / Q} \right) |c\rangle$。

4. **概率分析**：
观察括号内的等比数列求和 $\sum_{k=0}^{A-1} (e^{2\pi i r c / Q})^k$。
当 $c$ 使得 $\frac{rc}{Q}$ 接近某个整数 $m$ 时，即 $\frac{rc}{Q} \approx m$，这意味着 $c \approx \frac{mQ}{r}$。
此时 $e^{2\pi i r c / Q} \approx 1$，各项干涉相长，求和结果大小约为 $A$，振幅达到最大值。
测量第一寄存器将以高概率得到某个整数 $c$，满足 $\left| \frac{c}{Q} - \frac{m}{r} \right| < \frac{1}{2Q}$。
因为 $Q > N^2$，通过经典连分数算法可以唯一且高精度地还原出分母 $r$。
</thinking>

在Shor算法中，周期查找通过将代数问题转化为量子态的相位干涉问题来实现，其核心推导如下：

**1. 初始叠加与Oracle演化**
假设第一寄存器长度为 $n$ 个量子比特，其状态空间维度 $Q = 2^n$（要求 $N^2 < Q < 2N^2$）。初态经过Hadamard变换后变为等概率叠加态：
$$|\psi_0\rangle = \frac{1}{\sqrt{Q}} \sum_{x=0}^{Q-1} |x\rangle |0\rangle$$
接着我们调用量子Oracle计算模幂函数 $f(x) = a^x \pmod N$，系统整体演化为：
$$|\psi_1\rangle = \frac{1}{\sqrt{Q}} \sum_{x=0}^{Q-1} |x\rangle |f(x)\rangle$$

**2. 测量辅助寄存器与态坍缩**
由于 $f(x)$ 是周期为 $r$ 的函数，我们在第二寄存器上进行测量，假设观测值为 $y = a^{x_0} \pmod N$。因为周期性的存在，在第一寄存器中满足 $x = x_0 + kr$（$k$为整数）的基态将发生坍缩相干叠加。若设满足条件的状态数约包含 $A \approx Q/r$ 项，则第一寄存子系统的量子态演化为：
$$|\psi_2\rangle = \frac{1}{\sqrt{A}} \sum_{k=0}^{A-1} |x_0 + kr\rangle$$

**3. 量子傅里叶变换（QFT）的数学推导**
对上述状态施加量子傅里叶变换，定义 $U_{QFT}|x\rangle = \frac{1}{\sqrt{Q}} \sum_{c=0}^{Q-1} e^{2\pi i xc / Q} |c\rangle$。代入 $|\psi_2\rangle$，得：
$$|\psi_3\rangle = \frac{1}{\sqrt{AQ}} \sum_{c=0}^{Q-1} \left( \sum_{k=0}^{A-1} e^{2\pi i (x_0 + kr) c / Q} \right) |c\rangle$$
提取公因式，$|c\rangle$ 的概率振幅为 $A_c = \frac{1}{\sqrt{AQ}} e^{2\pi i x_0 c / Q} \sum_{k=0}^{A-1} \left(e^{2\pi i r c / Q}\right)^k$。

**4. 干涉放大与周期提取**
当 $e^{2\pi i r c / Q} \approx 1$ 时，求和项内发生相长干涉。这意味着 $\frac{rc}{Q}$ 非常接近某个整数 $m$，即 $c \approx \frac{mQ}{r}$。此时振幅大小 $|A_c| \approx \frac{A}{\sqrt{AQ}} = \sqrt{\frac{A}{Q}}$ 达到峰值。
因此，对 $|\psi_3\rangle$ 进行测量时，将以极高的概率测得整数 $c$，满足 $\left| \frac{c}{Q} - \frac{m}{r} \right| < \frac{1}{2Q}$。由于我们一开始设定了 $Q > N^2$，必然可以通过经典的连分数算法从 $c/Q$ 中唯一精确地提取出分母 $r$。

**isQ语言量子电路实现示例：**
以下为展示Shor算法中QFT电路结构的简化isQ代码：

```isq
import std;

const N = 3; // 定义用于演示的量子比特数
qbit q[N];
qbit ancilla[2]; // 辅助比特，模拟第二寄存器

// 自定义受控相位门
deriving gate CRk = [[1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, exp(i * pi / 2)]];

procedure qft() {
    for i in 0:N {
        H(q[i]);
        int d = 2;
        for j in (i+1):N {
            double angle = -M_PI / d;
            // 施加受控相位旋转门
            ctrl @[q[j]] Rz(angle, q[i]);
            d = d * 2;
        }
    }
    // 实际应用中通常还需要在此处加入SWAP翻转比特顺序
    // 由于isQ限制直接使用SWAP，可通过三次CNOT实现：
    // CNOT(q[0], q[2]); CNOT(q[2], q[0]); CNOT(q[0], q[2]);
}

procedure main() {
    // 初始化第一寄存器为叠加态
    for i in 0:N {
        H(q[i]);
    }
    
    // --- 此处应插入模幂Oracle Uf ---
    // 为了演示QFT，我们省略具体的模幂操作，它将结果存入ancilla中
    
    // 应用QFT提取周期信息
    qft();

    // 测量获取包含周期信息的状态
    for i in 0:N {
        M(q[i]);
    }
}
```

## isqExpand/algo/0

- task_id: `isqExpand/algo/0`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `grover`, `amplitude_amplification`, `oracle`
- source: `isq_expansion`
- dataset_index: `5011`

### Prompt

请用isQ语言编写一个量子电路：implements Grover's algorithm to search for the state |11> in a 2-qubit system. Apply the oracle (marks |11>) and the diffusion operator for one iteration.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement Grover's search for |11> in a 2-qubit system.
Qubits: 2, both measured.

1. Initialize: H(q[0]), H(q[1]) creates uniform superposition (|00>+|01>+|10>+|11>)/2
2. Oracle: CZ(q[0],q[1]) flips the phase of |11> -> (|00>+|01>+|10>-|11>)/2
3. Diffusion operator (2|s><s|-I): reflects about the mean
   - H on both: maps back to computational basis
   - X on both: flips all bits
   - CZ: adds phase to |11> (which was |00> before X)
   - X, H reverse the mapping
4. For N=4 states, one Grover iteration gives probability 1.0 for the marked state |11>.

Expected: {|11>: 1.0}

## isqTrain/2696

- task_id: `isqTrain/2696`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3588`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
oracle bool[4] g(bool a[4]) {
    bool res[] = [a[0], a[1], a[2], false];
    return res;
}
qbit q[4], res[4];

procedure main(){
    H(q);
    g(q, res);
    H(q); 
    print M(q);
}
```

### Chain-of-thought reasoning

The isQ program does the following:
1.  Applies H to all 4 qubits `q`.
2.  Applies an oracle `g` to `q` and `res`.
3.  Applies H to all 4 qubits `q`.
4.  Measures `q`.

Let's look at the oracle `g`:

This computes the function $f(x)$ where $x$ is the input state of `q`.
Wait, the output of the boolean function is `[a[0], a[1], a[2], false]`.
Wait, in `g(q, res);`, `g` is an oracle. It maps `q` to `q` and `res` to `res`?
No, `res` is an array of 4 qubits, but it is not measured.
Actually, wait: `q` has 4 qubits. `res` has 4 qubits.
The function signature is `oracle bool[4] g(bool a[4])`.
Wait, is it a phase oracle or a bit oracle?
In isQ, `oracle bool[N] g(bool a[N])` usually means it's a reversible classical function acting as a bit oracle:
$|x, y\rangle \to |x, y \oplus f(x)\rangle$.
But wait, the `res` qubits are initialized to $|0\rangle$?
Ah, `qbit q[4], res[4];` means they are initialized to $|0\rangle$.
The bit oracle $|x\rangle|y\rangle \to |x\rangle|y \oplus f(x)\rangle$.
Here $x$ is the state of `q` (4 qubits), $y$ is the state of `res` (4 qubits).
Wait, the `g` function takes `bool a[4]` and returns `bool[4]`.
Does it mean `g` acts as a permutation on the input `a`, and since it's `oracle`, it flips the output bits?
Actually, if it's defined as `g(q, res)`, it likely computes $|x\rangle|y\rangle \to |x\rangle|y \oplus f(x)\rangle$.
If `res` is initialized to $|0\rangle$, then `res` ends up in $|f(x)\rangle$.
Wait, what is the function $f(x)$?
$f(x) = x_0 x_1 x_2 0$.
Since the last bit of the return is `false`, the 4th qubit of `res` is always $0 \oplus 0 = 0$.
But `res` is NOT measured. The measured qubits are `q`!
Let's trace `q`.
The state of `q` is affected by `g(q, res)` if `g` entangles `q` and `res`.
Does it entangle them? Yes, $|x\rangle|0\rangle \to |x\rangle|f(x)\rangle$.
After `H(q)`, the state is $\frac{1}{4} \sum_{x=0}^{15} |x\rangle|0\rangle$.
Then `g(q, res)` changes it to $\frac{1}{4} \sum_{x=0}^{15} |x\rangle|f(x)\rangle$.
Then `H(q)` is applied to the `q` qubits.
The state becomes $\frac{1}{4} \sum_{x=0}^{15} \sum_{z=0}^{15} (-1)^{x \cdot z} |z\rangle|f(x)\rangle$.
Wait, if we measure `q` only, the probability of outcome $z$ is:
$P(z) = \left| \frac{1}{4} \sum_{x=0}^{15} (-1)^{x \cdot z} |f(x)\rangle \right|^2$
Wait, $|f(x)\rangle$ is a basis state, so it's a sum of orthogonal states!
Therefore, the norm squared of the sum is the sum of the norm squareds.
$P(z) = \sum_{x=0}^{15} \left| \frac{1}{4} (-1)^{x \cdot z} \right|^2 = 16 \times \frac{1}{16} = 1$?
Wait, $1/4$ for each state? No, 4 qubits means amplitude is $1/\sqrt{16} = 1/4$.
So $P(z) =

### Reference answer

{'predicted_probs': {'0000': 0.12500000000000003, '0001': 0.12500000000000003, '0010': 0.12500000000000003, '0011': 0.12500000000000003, '0100': 0.12500000000000003, '0101': 0.12500000000000003, '0110': 0.12500000000000003, '0111': 0.12500000000000003}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

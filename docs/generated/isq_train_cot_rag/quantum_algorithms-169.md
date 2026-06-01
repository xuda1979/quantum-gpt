# ISQ training COT RAG corpus: quantum_algorithms shard 169

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4087

- task_id: `isqTrain/4087`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `3003`

### Prompt

Predict the output probabilities of the following quantum circuit:

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
    grover_oracle(q);
    grover_diffusion(q);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. This is a Grover's search algorithm on 3 qubits with 2 iterations.
2. The oracle marks target state |101> (|5>) using X(q[1]) to convert |101> to |111>, applying Toffoli (ctrl CZ), then undoing X.
3. The diffusion operator reflects states about the uniform superposition mean.
4. For 3 qubits, there are 8 total states, giving amplitude θ ≈ 0.3637 radians.
5. After 2 iterations, the amplitude for |101> is sin(5θ) ≈ 0.9723.
6. The probability of measuring |101> is approximately 94.5%.
7. All other states share the remaining ~5.5% probability.

**Predicted probability distribution:** |101> with ~94.5% probability, with small probabilities for other states (|000>, |001>, |010>, |011>, |100>, |110>, |111> each ~0.8%).

### Reference answer

Deterministic output: state |101> with probability ~0.95

## isqTrain/3836

- task_id: `isqTrain/3836`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1796`

### Prompt

Write isQ code for the following quantum task: Demonstrate phase kickback with controlled-Rz(3pi/2). Control qubit starts in |+>, target in |1>. After controlled-Rz and Hadamard, measure to observe the kicked-back phase.

### Chain-of-thought reasoning

Let me analyze this quantum circuit step by step.

**Goal:** Demonstrate phase kickback where a controlled-Rz gate kicks back a phase to the control qubit.

**Qubits:** 2 qubits needed, q[0] is control, q[1] is target, both measured.

**State evolution:**

1. Initial state: |00⟩

2. After H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2

3. After X(q[1]): (|01⟩ + |11⟩)/√2

4. After ctrl Rz(3π/2, q[0], q[1]):
   - Rz(θ) = [[1, 0], [0, e^(iθ)]]
   - Rz(3π/2) applies e^(i3π/2) phase to |1⟩ of target
   - When control is |1⟩ and target is |1⟩, we get phase e^(i3π/2)
   - State becomes: (|01⟩ + e^(i3π/2)|11⟩)/√2
   - e^(i3π/2) = -i
   - State: (|01⟩ - i|11⟩)/√2

5. After H(q[0]):
   - |0⟩ → (|0⟩ + |1⟩)/√2
   - |1⟩ → (|0⟩ - |1⟩)/√2
   
   State becomes:
   (|0⟩(|1⟩) + |1⟩(|1⟩))/2 - i(|0⟩(|1⟩) - |1⟩(|1⟩))/2
   = ((1-i)|0⟩|1⟩ + (1+i)|1⟩|1⟩)/2

Let me recalculate:
State before H on q[0]: (|01⟩ - i|11⟩)/√2
= (1/√2)|01⟩ + (-i/√2)|11⟩

After H on q[0]:
|01⟩ → (|0⟩ + |1⟩)/√2 ⊗ |1⟩ = (|01⟩ + |11⟩)/√2
|11⟩ → (|0⟩ - |1⟩)/√2 ⊗ |1⟩ = (|01⟩ - |11⟩)/√2

So:
(1/√2)(|01⟩ + |11⟩)/√2 + (-i/√2)(|01⟩ - |11⟩)/√2
= (1/2)|01⟩ + (1/2)|11⟩ - (i/2)|01⟩ + (i/2)|11⟩
= ((1-i)/2)|01⟩ + ((1+i)/2)|11⟩

Probabilities:
P(|01⟩) = |(1-i)/2|² = |1-i|²/4 = 2/4 = 1/2
P(|11⟩) = |(1+i)/2|² = |1+i|²/4 = 2/4 = 1/2

Wait, that gives equal probabilities, but The predicted output {|01⟩: 0.146447, |11⟩: 0.853553}.

Let me reconsider. The issue might be with how Rz is defined. In some conventions, Rz(θ) = e^(-iθ/2)Z, and in others it's different.

Let me check the standard definition:
Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]

So for Rz(3π/2):
Rz(3π/2) = [[e^(-i3π/4), 0], [0, e^(i3π/4)]]

When applied to |1⟩ (eigenstate of Z with eigenvalue -1):
Rz(3π/2)|1⟩ = e^(i3π/4)|1⟩

But wait, |1⟩ is indeed an eigenstate of Rz, so phase kickback should work.

Actually, let me reconsider the phase kickback mechanism. When we have ctrl-Rz applied to |+⟩|1⟩:

|+⟩|1⟩ = (|0⟩ + |1⟩)/√2 ⊗ |1⟩ = (|01⟩ + |11⟩)/√2

The controlled-Rz applies Rz(3π/2) to q[1] only when q[0] is |1⟩.

Rz(3π/2)|1⟩ = e^(i3π/4)|1⟩

So after ctrl-Rz:
(|0⟩|1⟩ + e^(i3π/4)|1⟩|

## isqTrain/4460

- task_id: `isqTrain/4460`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `5574`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[3];
procedure my_z(qbit a) {
    Z(a);
} deriving gate
procedure main() {
    // State to teleport: |1>
    X(q[0]);
    // EPR pair
    H(q[1]); CNOT(q[1], q[2]);
    // Alice's operations
    CNOT(q[0], q[1]);
    H(q[0]);
    // Bob's operations (using quantum control instead of classical)
    CNOT(q[1], q[2]);
    ctrl my_z(q[0], q[2]);
    
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a step-by-step analysis of an isQ quantum program that implements a variation of quantum teleportation using quantum control instead of classical control. I need to provide the evolution of the quantum state and predict the final measurement probabilities.

2.  **Analyze the Code:**
    *   `qbit q[3];` -> Three qubits: q[0], q[1], q[2]. Initial state is $|000\rangle$.
    *   `X(q[0]);` -> Prepares q[0] in $|1\rangle$. State is $|100\rangle$.
    *   `H(q[1]); CNOT(q[1], q[2]);` -> Creates EPR pair between q[1] and q[2]. State is $|1\rangle \otimes \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle) = \frac{1}{\sqrt{2}}(|100\rangle + |111\rangle)$.
    *   `CNOT(q[0], q[1]);` -> Alice's CNOT. State becomes $\frac{1}{\sqrt{2}}(|100\rangle + |111\rangle) \xrightarrow{CNOT} \frac{1}{\sqrt{2}}(|110\rangle + |101\rangle)$. Wait, wait.
        Let's re-evaluate carefully.
        Initial EPR prep: q[0] is $|1\rangle$, q[1] and q[2] are $|00\rangle$.
        State: $|1\rangle_{q0} \otimes |0\rangle_{q1} \otimes |0\rangle_{q2} = |100\rangle$.
        Apply `H(q[1])`: $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)_{q1}$. State: $\frac{1}{\sqrt{2}}(|100\rangle + |110\rangle)$.
        Apply `CNOT(q[1], q[2])`: $\frac{1}{\sqrt{2}}(|100\rangle + |111\rangle)$.
        Apply `CNOT(q[0], q[1])`: Control is q[0], target is q[1].
        $|100\rangle \to |110\rangle$
        $|111\rangle \to |101\rangle$
        New state: $\frac{1}{\sqrt{2}}(|110\rangle + |101\rangle)$.
    *   `H(q[0]);` -> Alice's Hadamard.
        $H$ on q[0] (first qubit in $|110\rangle$ and $|101\rangle$):
        $H|1\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$
        State:
        $\frac{1}{\sqrt{2}} [ \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)|10\rangle + \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)|01\rangle ]$
        $= \frac{1}{2} [ |010\rangle - |110\rangle + |001\rangle - |101\rangle ]$.
    *   `CNOT(q[1], q[2]);` -> Bob's CNOT. Control is q[1], target is q[2].
        $|010\rangle \xrightarrow{CNOT} |011\rangle$
        $|110\rangle \xrightarrow{CNOT} |111\rangle$
        $|001\rangle \xrightarrow{CNOT} |001\rangle$
        $|101\rangle \xrightarrow{CNOT} |101\rangle$
        New state: $\frac{1}{2} [ |011\rangle - |111\rangle + |001\rangle - |101\rangle ]$.
    *   `ctrl my_z(q[0], q[2]);` -> Controlled-Z. Control is q[0], target is q[2].
        Apply Z to q[2] if q[0] is $|1\rangle$.
        Terms with q[0]=$|1\rangle$ are $|111\rangle$ and $|101\rangle$.
        Z applied to q[2] flips the sign of $|1\rangle$ on q[2].
        $|111\rangle \to -|111\rangle$
        $|101\rangle \to -|101\rangle$
        New state: $\frac{1}{2} [ |011\rangle - (-|111\rangle) + |001\rangle -

### Reference answer

{'predicted_probs': {'001': 0.25, '011': 0.25, '101': 0.25, '111': 0.25}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|001>) = 0.2500, P(|011>) = 0.2500, P(|101>) = 0.2500, P(|111>) = 0.2500.'}

## isqQA/quantum_algorithms/36_principle_advantage

- task_id: `isqQA/quantum_algorithms/36_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `principle_advantage`, `algorithm`, `Bernstein-Vazirani算法`
- source: `qa_pipeline`
- dataset_index: `1790`

### Prompt

请详细解释Bernstein-Vazirani（伯恩斯坦-瓦兹拉尼）算法的核心原理，并对比它在经典计算与量子计算中的查询复杂度。此外，从量子计算理论的角度深入剖析，该算法实现量子加速的根本来源是什么？

### Reference answer

Bernstein-Vazirani（简称BV）算法是量子计算早期的一个里程碑式算法，它完美展示了量子并行性和量子干涉如何突破经典计算的极限。该算法的核心原理是为了解决一个特定的“黑盒查询”问题：假设有一个隐藏的比特串 $s$（例如 $s=1011$，长度为 $n$），存在一个黑盒函数 $f(x) = s \cdot x \pmod 2$（即 $x$ 和 $s$ 的按位内积模2）。我们的目标是找出这个未知的隐藏串 $s$。

在**时间复杂度与查询对比**上，经典计算与量子计算展现出了显著的差异：
1. **经典计算**：为了确定 $n$ 个比特的 $s$，我们必须提取 $n$ 个独立的方程。这意味着我们至少需要对黑盒进行 $n$ 次查询（例如依次输入 $100...0$，$010...0$，直到 $000...1$ 来单独提取 $s$ 的每一位）。因此，经典查询复杂度为 $O(n)$。
2. **量子计算（BV算法）**：通过巧妙的线路设计，BV算法仅需要 **1次** 对黑盒的量子查询，就能100%确定隐藏串 $s$。其整体量子查询复杂度为 $O(1)$，即使考虑到输入输出和量子门操作，总的量子时间复杂度也仅为 $O(n)$，相比经典查询次数实现了指数级加速。

**BV算法的量子加速根本来源**主要归结于以下两个量子力学特性的完美结合：

首先是**量子叠加与并行计算**。在BV算法中，我们将 $n$ 个量子比特初始化为 $|0\rangle$ 并施加Hadamard门，使其进入所有可能状态的等权叠加态 $\frac{1}{\sqrt{2^n}} \sum_{x=0}^{2^n-1} |x\rangle$。通过将这个叠加态输入量子黑盒，我们仅用一次查询，就同时计算了所有 $2^n$ 个输入 $x$ 对应的函数值 $f(x)$。这就是所谓的“量子并行性”。

其次是**量子相位干涉**。单纯依靠叠加态无法直接读取所有结果，因为一旦测量，波函数就会随机坍缩到某一个态上。BV算法的精妙之处在于，黑盒计算 $f(x)$ 的结果被转化为相对相位 $(-1)^{f(x)}$ 存储于量子态中（即 $\frac{1}{\sqrt{2^n}} \sum_{x} (-1)^{s\cdot x} |x\rangle$）。虽然相位包含信息，但无法直接测量。此时，算法再次对所有量子比特施加Hadamard门，这起到了**逆量子傅里叶变换**的作用。这一步是产生干涉的关键：它使得相位信息转化为概率幅信息。经过干涉，所有与目标隐藏串 $s$ 正交的状态发生相消干涉（概率幅变为0），而目标状态 $|s\rangle$ 发生相长干涉（概率幅放大为1）。因此，最后测量时，必将100%得到隐藏串 $s$。

综上所述，BV算法的加速并非单纯因为量子计算机“算得快”，而是因为其利用叠加态以1次查询提取了全局信息，并借助量子干涉机制将隐藏的相位特征提取到了可直接测量的计算基上。这种原理也是后续更高级算法（如Shor算法和Grover算法）的重要基石。

## isqTrain/3072

- task_id: `isqTrain/3072`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`
- source: `isq_train_cot`
- dataset_index: `1177`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[4];
procedure main() {
    X(q[2]);
    X(q[3]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes 4 qubits (q[0] to q[3]) in the ground state |0>, yielding the initial state |0000>.
2. An X gate is applied to q[2], flipping its state from |0> to |1>. The system state becomes |0010>.
3. An X gate is applied to q[3], flipping its state from |0> to |1>. The system state becomes |0011>.
4. All qubits are measured in the computational basis.
5. Since the system is deterministically in the |0011> state, the measurement yields '0011' (where q[0] is the highest-order bit) with 100% probability.

Predicted measurement probabilities: {'0011': 1.0}

### Reference answer

{'predicted_probs': {'0011': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/4571

- task_id: `isqTrain/4571`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `multi_controlled_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1563`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[4];

procedure my_z(qbit a) {
    Z(a);
} deriving gate

procedure diffuser() {
    H(q[0]); H(q[1]); H(q[2]);
    X(q[0]); X(q[1]); X(q[2]);
    ctrl ctrl my_z(q[0], q[1], q[2]);
    
    X(q[0]); X(q[1]); X(q[2]);
    H(q[0]); H(q[1]); H(q[2]);
}

procedure main() {
    
    X(q[3]); H(q[3]);
    
    H(q[0]); H(q[1]); H(q[2]);
    
    
    ctrl ctrl ctrl X(q[0], q[1], q[2], q[3]); 
    diffuser();
    
    
    ctrl ctrl ctrl X(q[0], q[1], q[2], q[3]); 
    diffuser();
    
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants an analysis of the provided isQ quantum program. The analysis should include step-by-step state evolution using Dirac notation, circuit operations, and predicted probability distribution. It must be concise (3-15 lines).

2.  **Analyze the isQ Code**:
    *   **Initialization**:
        *   `X(q[3]); H(q[3]);` -> q[3] is initialized to $|1\rangle$ then put into $|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$.
        *   `H(q[0]); H(q[1]); H(q[2]);` -> q[0..2] are initialized to $|+\rangle|+\rangle|+\rangle$.
        *   Initial state of q[0..3] is $|+\rangle^{\otimes 3} |-\rangle = \frac{1}{2\sqrt{2}} \sum_{x=0}^{2} |x\rangle (|0\rangle - |1\rangle)$.
    *   **Oracle**:
        *   `ctrl ctrl ctrl X(q[0], q[1], q[2], q[3]);`
        *   This is a multi-controlled X gate (CCCX) targeting q[3]. When q[0], q[1], q[2] are all 1, q[3] is flipped. Since q[3] is in $|-\rangle$, the phase kickback gives a -1 phase to the $|111\rangle$ state.
        *   Wait, let's trace: $X|-\rangle = -|-\rangle$. So the state becomes $\frac{1}{2\sqrt{2}} (|000\rangle + |001\rangle + ... - |111\rangle)(|0\rangle - |1\rangle)$. This marks the state $|111\rangle$ with a negative phase.
    *   **Diffuser**:
        *   `diffuser()` on q[0..2].
        *   Standard Grover diffuser: $H^{\otimes 3} (2|0\rangle\langle0| - I) H^{\otimes 3}$. It reflects the state about the mean.
        *   Since the marked state is $|111\rangle$ (in q[0..2]), this is Grover's algorithm on 3 qubits.
        *   Number of solutions $M=1$, search space $N=8$.
        *   Optimal number of iterations $R \approx \frac{\pi}{4} \sqrt{N/M} = \frac{\pi}{4} \sqrt{8} \approx 2.22$.
        *   Let's check the code for the number of iterations.
    *   **Iterations**:
        *   Iteration 1: `ctrl ctrl ctrl X` (Oracle) -> `diffuser()`
        *   Iteration 2: `ctrl ctrl ctrl X` (Oracle) -> `diffuser()`
        *   So $R=2$.
    *   **State after 2 iterations**:
        *   Initial uniform superposition $|s\rangle = \frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle$.
        *   Target state $|w\rangle = |111\rangle$.
        *   $|s\rangle = \sin(\theta) |w\rangle + \cos(\theta) |s'\rangle$, where $\sin(\theta) = 1/\sqrt{8}$.
        *   $\theta = \arcsin(1/\sqrt{8})$.
        *   After $R=2$ iterations, the state is $\sin(5\theta) |w\rangle + \cos(5\theta) |s'\rangle$.
        *   $\sin(5\theta) = \sin(5 \arcsin(1/\sqrt{8}))$.
        *   Let's calculate probabilities:
            *   $\sin(\theta) = 1 / 2\sqrt{2} = \sqrt{2}/4 \approx 0.3535$
            *   $\cos(\theta) = \sqrt{1 - 1/8} = \sqrt{7}/4 \approx 0.9354$
            *   $\sin(2\theta) = 2 \sin\theta \cos\theta = 2 (\sqrt{2}/4) (\sqrt{7}/4) = \sqrt{14}/8 \approx 0.4677$
            *   $\cos(2\theta) = \cos^2\theta - \sin^2\theta = 7

### Reference answer

{'predicted_probs': {'0000': 0.007813, '0001': 0.007813, '0010': 0.007813, '0011': 0.945312, '0100': 0.007813, '0101': 0.007813, '0110': 0.007813, '0111': 0.007813}, 'explanation': 'This isQ program operates on 4 qubit(s). The measurement probability distribution is: P(|0000>) = 0.0078, P(|0001>) = 0.0078, P(|0010>) = 0.0078, P(|0011>) = 0.9453, P(|0100>) = 0.0078, P(|0101>) = 0.0078, P(|0110>) = 0.0078, P(|0111>) = 0.0078.'}

## isqTrain/1381

- task_id: `isqTrain/1381`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1972`

### Prompt

帮我写一个isQ程序：the Deutsch algorithm for the balanced function f(x)=x. Prepare ancilla in |-> state, put input in superposition, apply oracle, then Hadamard and measure.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement the Deutsch algorithm for f(x) = x to determine if f is constant or balanced.

2. **Qubits**: 2 qubits (q[0] input, anc[0] ancilla); only q[0] is measured.

3. **State evolution**:
   - **Initial**: |0⟩|0⟩
   - **X(anc[0])**: |0⟩|1⟩
   - **H(anc[0])**: |0⟩|−⟩ where |−⟩ = (|0⟩−|1⟩)/√2
   - **H(q[0])**: |+⟩|−⟩ = (|0⟩+|1⟩)/√2 ⊗ |−⟩
   - **CNOT(q[0], anc[0])**: Phase kickback applies (−1)^f(x) to input: (|0⟩−|1⟩)/√2 ⊗ |−⟩ = |−⟩|−⟩, since f(0)=0, f(1)=1
   - **H(q[0])**: H|−⟩ = |1⟩ ⊗ |−⟩

4. **Result**: Input qubit is |1⟩ with probability 1.0, correctly identifying f as balanced.

## isqTrain/3052

- task_id: `isqTrain/3052`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_multi_register`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `373`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```isq
import std;
qbit q[3];
// Initialize to |001>
procedure main() {
    // X(q[2]); // BUG: missing initialization
    M(q[0]);
    M(q[1]);
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **The Bug**: The program attempts to prepare the state |001>, but the `X(q[2])` gate is commented out. All qubits initialize to |0>, so the state incorrectly remains |000>.
2. **The Fix**: Uncomment the `X(q[2])` gate to apply a Pauli-X (bit-flip) operation to the third qubit.
3. **State Evolution**:
   - Start in the default initialized state: |000>.
   - Apply `X(q[2])` to flip the third qubit from |0> to |1>.
   - The system correctly evolves into the target state: |001>.
   - Measurement yields the expected bitstring 001 with a probability of 1.0.

## isqTrain/1001

- task_id: `isqTrain/1001`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `isq_syntax_for_loop`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1746`

### Prompt

帮我写一个isQ程序：implements the qdrift pattern with modified rotation parameters (num_pi2_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

Looking at this circuit, I need to understand what's happening:

1. Initial state: |00⟩
2. After X(q[0]): |10⟩

Now we have 4 samples of qDRIFT for H = XX + ZZ with modified rotation angles.

The rotation angle given is 1.04719755119660 radians = π/3 (approximately 60°)

Let me trace through:

**Sample 1: ZZ term**
- CNOT(q[0], q[1]): |10⟩ → |11⟩
- Rz(π/3, q[1]): |11⟩ → e^{-iπ/6}|11⟩
- CNOT(q[0], q[1]): e^{-iπ/6}|11⟩ → e^{-iπ/6}|10⟩

**Sample 2: XX term**
- H(q[0]); H(q[1]): e^{-iπ/6}|10⟩ → e^{-iπ/6}|−+⟩
  where |−⟩ = (|0⟩ - |1⟩)/√2, |+⟩ = (|0⟩ + |1⟩)/√2
- CNOT(q[0], q[1]): 
- Rz(π/3, q[1]):
- CNOT(q[0], q[1]):
- H(q[0]); H(q[1]):

Let me be more careful.

For XX interaction, we conjugate by H⊗H to convert XX to ZZ, then apply CNOT-Rz-CNOT.

Let me compute step by step:

State after Sample 1: e^{-iπ/6}|10⟩

Sample 2: XX term
- H⊗H on e^{-iπ/6}|10⟩ = e^{-iπ/6} H|1⟩⊗H|0⟩ = e^{-iπ/6}|−⟩|+⟩

where |−⟩ = (|0⟩ - |1⟩)/√2, |+⟩ = (|0⟩ + |1⟩)/√2

- CNOT(q[0], q[1]) on |−+⟩:
  |−+⟩ = (|0⟩ - |1⟩)/√2 ⊗ (|0⟩ + |1⟩)/√2
  = (1/2)(|00⟩ + |01⟩ - |10⟩ - |11⟩)
  
  CNOT flips q[1] when q[0]=1:
  = (1/2)(|00⟩ + |01⟩ - |11⟩ - |10⟩)
  = (1/2)(|00⟩ + |01⟩ - |10⟩ - |11⟩)
  = -|−+⟩... wait let me recalculate.
  
  |−+⟩ = (|0⟩ - |1⟩)(|0⟩ + |1⟩)/2 = (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2
  
  CNOT(q[0],q[1]): |00⟩→|00⟩, |01⟩→|01⟩, |10⟩→|11⟩, |11⟩→|10⟩
  
  Result: (|00⟩ + |01⟩ - |11⟩ - |10⟩)/2 = -(|00⟩ + |01⟩ - |10⟩ - |11⟩)/2 = -|−+⟩

Hmm, so CNOT|−+⟩ = -|−+⟩. Interesting.

Actually wait: (|00⟩ + |01⟩ - |11⟩ - |10⟩)/2

Let me reorder: (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2

This is (|0⟩ - |1⟩)/√2 ⊗ (|0⟩ + |1⟩)/√2 = |−+⟩

So CNOT|−+⟩ = |−+⟩. The sign didn't change because I reordered the terms correctly.

Wait: original was (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2
After CNOT: (|00⟩ + |01⟩ - |11⟩ - |10⟩)/2 = (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2 = |−+⟩

So CNOT leaves |−+⟩ unchanged.

Then Rz(π/3) on q[1]: 
|−+⟩ = (|−0⟩ + |−1⟩)/√2
After Rz(π/3) on qubit 1: (|−0⟩ + e^{-iπ/3}|−1⟩)/√2 = e^{-iπ/6}|−⟩(e^{iπ/6}|0⟩ + e^{-iπ/6}|1⟩)/√2

Hmm, this is getting complex. Let me

## isqTrain/710

- task_id: `isqTrain/710`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5176`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[3];

procedure main() {
    // Encode a = 3 (binary 11): set both bits
    X(q[0]);
    X(q[1]);
    // Threshold comparator: a >= 2 when MSB is set
    CNOT(q[1], q[2]);
    // Measure the result flag
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state is |000>.
2. X gates on q[0] and q[1] flip them to |1>, evolving the state to |110>.
3. CNOT(q[1], q[2]) uses q[1] as the control. Since q[1] is in the |1> state, the target q[2] is flipped to |1>.
4. The final state before measurement is |111>.
5. Measuring q[2] yields |1> with absolute certainty.

Predicted probability distribution: {|1>: 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqEval/273. Dimension: predict probabilities for reference circuit.'}

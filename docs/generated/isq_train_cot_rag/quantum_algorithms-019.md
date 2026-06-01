# ISQ training COT RAG corpus: quantum_algorithms shard 19

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2842

- task_id: `isqTrain/2842`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4410`

### Prompt

Create an isQ quantum circuit that creates a Bell state |Psi+>. Use the appropriate sequence of gates on 2 qubits and measure both.

Requirements:
- Declare `qbit q[2];` at global scope.
- Use `procedure main()` as entry point.
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
Goal: Create a Bell state that yields measurement probabilities {|00>: 0.5, |11>: 0.5} on 2 qubits.
Qubits: 2 (q[0], q[1]), both measured.
State evolution:
- |00> → X(q[0]) → |10>
- |10> → H(q[0]) → (|00> - |10>)/√2
- (|00> - |10>)/√2 → CNOT(q[0], q[1]) → (|00> - |11>)/√2
This is the Bell state |Φ⁻⟩. The amplitudes of |00⟩ and |11⟩ both have magnitude 1/√2, so measurement probabilities are {|00>: 0.5, |11>: 0.5}.

## isqTrain/4600

- task_id: `isqTrain/4600`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `ancilla_usage`, `superposition`
- source: `isq_train_cot`
- dataset_index: `205`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;

qbit q[4];

procedure main() {
    
    X(q[3]);
    X(q[3]);  // replaced H with X
    
    H(q[0]);
    H(q[1]);
    H(q[2]);
    
    CNOT(q[0], q[3]);
    CNOT(q[2], q[3]);
    
    H(q[0]);
    H(q[1]);
    H(q[2]);
    
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the circuit:**
    *   Initialize 4 qubits to $|0\rangle^{\otimes 4}$.
    *   `X(q[3])`, `X(q[3])` acts on q[3]. This is equivalent to Identity $I$ on q[3] because $X \cdot X = I$. So q[3] remains $|0\rangle$.
    *   `H(q[0])`, `H(q[1])`, `H(q[2])` creates an equal superposition on the first three qubits: $(|0\rangle+|1\rangle)^{\otimes 3}/\sqrt{8} \otimes |0\rangle$.
    *   `CNOT(q[0], q[3])` and `CNOT(q[2], q[3])`.
        *   This is effectively a parity check. The target q[3] is flipped if q[0] XOR q[2] is 1. But wait, q[3] started in $|0\rangle$.
        *   Since $X \cdot X = I$ was applied initially, q[3] is just $|0\rangle$.
        *   State becomes: $\frac{1}{2\sqrt{2}} \sum_{x \in \{0,1\}^3} |x_0, x_1, x_2\rangle \otimes |x_0 \oplus x_2\rangle$.
    *   `H(q[0])`, `H(q[1])`, `H(q[2])` applied again.
        *   This is measuring q[0], q[1], q[2] in the X-basis (Hadamard basis).
        *   Notice that this looks like a modified Bernstein-Vazirani or parity measurement.
        *   Let's trace the exact state:
            Before the final H gates: $\frac{1}{2\sqrt{2}} (|000\rangle|0\rangle + |001\rangle|1\rangle + |010\rangle|0\rangle + |011\rangle|1\rangle + |100\rangle|1\rangle + |101\rangle|0\rangle + |110\rangle|1\rangle + |111\rangle|0\rangle)$.
            Applying H to q[0], q[1], q[2]:
            Consider a generic qubit $q_i$. It's entangled with $q_3$.
            Let's re-read the prompt. Wait, the prompt says "Expected measurement probabilities: {|0000>: 0.5, |0101>: 0.5}". Wait, why `|0101>`?
            Ah. The `M(q[0])` etc measures only the first three? No, if q[3] is also measured (or implicitly measured as it's a 4-qubit state), the output format says "Expected measurement probabilities: {|0000>: 0.5, |0101>: 0.5}".
            Wait, let me double check the math.
            Initial: $|0000\rangle$.
            `X(q[3]); X(q[3]);` leaves it at $|0000\rangle$.
            `H` on 0,1,2: $\frac{1}{\sqrt{8}} \sum_{x \in \{0,1\}^3} |x, 0\rangle$.
            `CNOT(0,3); CNOT(2,3);`: $\frac{1}{\sqrt{8}} \sum_{x \in \{0,1\}^3} |x, x_0 \oplus x_2\rangle$.
            Final `H` on 0,1,2:
            We know $H^{\otimes 3} \sum_x (-1)^{s \cdot x} |x\rangle = |s\rangle$.
            Here we have: $\frac{1}{\sqrt{8}} \sum_{x} |x\rangle |x_0 \oplus x_2\rangle$.
            Notice $x_0 \oplus x_2$ is the parity.
            Let's write out the sum explicitly:
            $|x_0 \oplus x_2\rangle$ is $|0\rangle$ if $x_0=x_2$ and $|1\rangle$ if $x_0 \neq x_2$.
            So we have two sets of terms: terms where $x_0=x_2$ (contribute to $q_3=|0\rangle$) and $x_0 \neq x_2$ (contribute to $q_3

### Reference answer

{'predicted_probs': {'0000': 0.5, '0101': 0.5}, 'explanation': 'This isQ program operates on 4 qubit(s). The measurement probability distribution is: P(|0000>) = 0.5000, P(|0101>) = 0.5000.'}

## isqTrain/4120

- task_id: `isqTrain/4120`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `4032`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[3];

procedure main() {
    X(q[0]);
    X(q[1]);
    X(q[2]);

    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    H(q[2]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[1]);
    ctrl Rz(-2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    H(q[0]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict measurement output of an isQ quantum circuit.
    *   Input Circuit: 3 qubits, initialized to $|111\rangle$, swap (three-CNOT decomposition)-like operations, followed by an Inverse Quantum Fourier Transform (QFT†) or similar rotation/H sequence.
    *   Format: Start with "## Circuit Analysis". Concise step-by-step reasoning. Explain operations, state evolution, final state, and probability distribution.
    *   Measurement: `M(q[0]); M(q[1]); M(q[2]);` so bitstrings are $q_0 q_1 q_2$. Let's check isQ bitstring mapping: "earlier measured qubit = higher bit". So $M(q_0)$ is the highest bit. Outcome = $q_0 \times 4 + q_1 \times 2 + q_2 \times 1$.
    *   Let's trace the state evolution.

2.  **Circuit Breakdown:**
    *   `X(q[0]); X(q[1]); X(q[2]);`
        *   Initial state: $|111\rangle$.
    *   `CNOT(q[0], q[2]); CNOT(q[2], q[0]); CNOT(q[0], q[2]);`
        *   This is a swap operation (three-CNOT decomposition)! $q_0 \leftrightarrow q_2$.
        *   State remains $|111\rangle$. (Wait, $|111\rangle$ swapped is still $|111\rangle$).
    *   `H(q[2]);`
        *   State: $\frac{1}{\sqrt{2}}(|110\rangle - |111\rangle)$ (using $q_0 q_1 q_2$ order).
    *   `ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[2], q[1]);`
        *   Angle = $-\pi/2$.
        *   Rz($\theta$) = $e^{-i\theta/2}|0\rangle\langle0| + e^{i\theta/2}|1\rangle\langle1|$.
        *   Wait, the gate is `ctrl Rz(..., control_q, target_q)`. In isQ, `ctrl Rz(angle, control, target)` or is it `ctrl Rz(angle, target, control)`?
        *   Let's check syntax: "ctrl @[c1] Gate(target)". If it's written `ctrl Rz(angle, q[c], q[t])`, the first qubit after angle might be the control, but wait, standard isQ syntax for control is `ctrl Rz(angle, target)`, wait no, Rz takes angle and qubit.
        *   Actually, `ctrl Rz(theta, q1, q2)` usually implies `q1` is control, `q2` is target, OR it might mean applying controlled-Rz.
        *   Let's look at the syntax reference: "ctrl @[c1, c2] Gate(target)". If written without `@`, maybe it's standard call? No, `ctrl Rz(theta, q[2], q[1])`. This implies `q[2]` is the control and `q[1]` is the target. Let's assume `q[2]` is control, `q[1]` is target.
        *   Angle = $-\pi/2$.
        *   Target is $q_1$. Control is $q_2$.
        *   State is $\frac{1}{\sqrt{2}}(|11\rangle_0|0\rangle_2 - |11\rangle_0|1\rangle_2)$.
        *   Wait, let's write it as $|q_0 q_1\rangle |q_2\rangle$ to see the control.
        *   $|110\rangle - |111\rangle$.
        *   Controlled-Rz applies Rz to $q_1$ if $q_2$ is $|1\rangle$.
        *   Rz($-\pi/2$) on $|1\rangle$ gives $e^{i\pi/4}|1\rangle$.
        *   So the $|111\rangle$ term gets multiplied by $e^{i\pi/4}$.
        *   State: $\frac{1}{\sqrt{2}}(|110\rangle - e^{i\pi/4}|111\rangle)$.
    *   `H(q[1]);`
        *   Apply H to $q_1$.
        *   $|0\rangle \to \frac{|0\rangle+|1\rangle}{

### Reference answer

Uniform distribution across 8 states

## isqQA/quantum_algorithms/108_optimization_variant

- task_id: `isqQA/quantum_algorithms/108_optimization_variant`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `optimization_variant`, `algorithm`, `量子相位估计QPE原理`
- source: `qa_pipeline`
- dataset_index: `460`

### Prompt

量子相位估计（QPE）是许多量子算法的核心子程序，但其标准版本需要大量的辅助量子比特，并且依赖深层的逆量子傅里叶变换电路。在含噪声的中等规模量子（NISQ）时代，这些限制阻碍了其实际应用。请问目前针对QPE算法有哪些重要的优化改进版本或变体？能否以Kitaev迭代相位估计为例，详细说明其核心优化思想，并展示如何使用isQ语言实现一个基于较少辅助比特的简化版QPE变体电路？

### Reference answer

标准的量子相位估计（QPE）算法需要$n$个辅助量子比特来达到$n$位的相位估计精度，并且需要执行层数为$O(2^n)$的受控酉操作和逆量子傅里叶变换（IQFT）。这种全连接和极深电路的要求在NISQ时代极具挑战性。为了解决这一问题，研究者们提出了多种重要的优化变体，主要包括：

1. 迭代量子相位估计，也称Kitaev相位估计：它将原本并行的多位测量改为串行的单比特测量。每次迭代只使用1个（或极少数）辅助量子比特，通过动态调整后一轮的相位补偿来逐步逼近真实相位。这极大地节省了量子比特并允许后期经典辅助计算。
2. 稳健相位估计：基于统计学和贝叶斯推断的变体。它通过设计特定的相位偏移和测量序列，能够在存在一定门噪声的情况下更可靠地提取相位，减少因噪声导致的概率坍缩错误。
3. 基于变分本征求解器（VQE）的近似相位提取：不完全依赖QPE，而是利用参数化量子线路结合经典优化器来逼近目标系统的基态能量。

在Kitaev迭代相位估计中，假设酉算子$U$的本征态为$|\psi\rangle$，本征相位为$\phi$。在第一轮中，我们制备$|+\rangle$并测量辅助比特，这相当于估计相位的最高位。在随后的第$k$轮中，我们将前$k-1$轮的测量结果作为经典相位反馈，在辅助比特上施加特定角度的旋转门，并执行受控$U^{2^{k-1}}$操作，从而依次提取出相位$\phi$的二进制小数表示。这种方法将空间复杂度（量子比特数）转化为时间复杂度（迭代次数），是非常典型的时空权衡。

下面是使用isQ语言实现的简化版单辅助比特迭代QPE电路示例。该示例演示了如何利用同一个辅助比特，通过连续的受控操作和经典前馈补偿，来提取本征相位的最高两位。假设我们要估计的酉算子为$T$门，其本征值相位为$\pi/4$，对应的二进制为$0.01$。

```isQ
import std;

// 全局声明变量，包含1个辅助比特和1个系统比特
qbit ancilla[1];
qbit system[1];

// 自定义一个受控T门，用于受控相位提取
deriving gate CT = [[1,0,0,0],
                   [0,1,0,0],
                   [0,0,1,0],
                   [0,0,0,exp(i*PI/4)]];

procedure main() {
    // 将系统比特制备为目标本征态 |1>
    X(system[0]);
    
    // --- 第一轮迭代：提取相位的第1位 (2^{-1} 位) ---
    H(ancilla[0]);
    // 受控 U^{2^0}，即受控 T 门
    CT(ancilla[0], system[0]);
    H(ancilla[0]);
    // 测量辅助比特，理论上 r1 将以极高概率等于 0
    int r1 = M(ancilla[0]);
    // 恢复辅助比特状态
    if (r1 == 1) { X(ancilla[0]); }

    // --- 第二轮迭代：提取相位的第2位 (2^{-2} 位) ---
    H(ancilla[0]);
    // 受控 U^{2^1}，即受控 T^2 (即受控 S 门)
    CT(ancilla[0], system[0]);
    CT(ancilla[0], system[0]);
    
    // 引入经典前馈相位补偿。如果上一轮结果 r1 == 1，
    // 则需要施加旋转 Rz(-PI/2) 来消除前一位对当前位测量的干扰
    if (r1 == 1) {
        Rz(-PI/2, ancilla[0]);
    }
    
    H(ancilla[0]);
    // 测量辅助比特，理论上 r2 将以极高概率等于 1
    int r2 = M(ancilla[0]);
    
    // 最终得到的相位二进制表示即为 r1 和 r2 组合：0.01
}
```

## isqTrain/838

- task_id: `isqTrain/838`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `finite_field_arithmetic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5350`

### Prompt

Write isQ code for the following quantum task: implements the gfp_multiplication pattern but with a different initial state preparation (flip q[[0, 3]] -> q[4]).

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement GF(p) multiplication where input `a=1` (binary 01) is encoded by flipping q[4], and the identity multiplication copies the result.

2. **Qubits**: 6 qubits (q[0]-q[5]), measuring q[4] and q[5] (the product register).

3. **State evolution**:
   - Initial: |000000⟩
   - X(q[4]): |000010⟩ — encodes a=1 as binary 01 in q[4]
   - CNOT(q[2], q[4]): |000010⟩ — control q[2]=|0⟩, no flip
   - CNOT(q[3], q[5]): |000010⟩ — control q[3]=|0⟩, no flip

4. **Expected probabilities**: Final state has q[4]=|1⟩ and q[5]=|0⟩ with certainty, yielding measurement bitstring |10⟩ (probability 1.0) since earlier measured qubit q[4] is the higher bit.

## isqTrain/1109

- task_id: `isqTrain/1109`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `499`

### Prompt

Help me write isQ code that implements a variant of the simon_algorithm pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze this task carefully.

The task is to write an isQ program implementing a variant of Simon's algorithm using q[2] -> q[4] (meaning qubits q[2], q[3], q[4] are involved in the Simon part, but actually the expanded register uses q[0] through q[3]).

Analyzing the circuit requirements:
- Uses qbit q[4] (4 input qubits)
- Uses qbit out[2] (2 output qubits)
- The oracle operates on q[0], q[1] with output in out[0], out[1]
- Hadamard gates are applied to q[0] and q[1] only
- All 4 qubits (q[0]-q[3]) are measured

The Simon's algorithm with period s = 11 (binary) means:
- f(x) = f(x ⊕ s) where s = 11
- f(00) = f(11) and f(01) = f(10)

The oracle:
- f(00) = 00
- f(01) = 01
- f(10) = 01
- f(11) = 00

So f(x) depends on x[0] XOR x[1]:
- When x[0] = x[1]: f = 00
- When x[0] ≠ x[1]: f = 01

Step-by-step evolution:

1. Initial state: |0000>|00> (4 input qubits, 2 output qubits)

2. After H(q[0]) and H(q[1]):
   State = 1/2(|00> + |01> + |10> + |11>) ⊗ |00> ⊗ |00>
   = 1/2(|0000> + |0100> + |1000> + |1100>) ⊗ |00>

3. After oracle f(q, out):
   - f(00) = 00: |0000>|00>
   - f(01) = 01: |0100>|01>
   - f(10) = 01: |1000>|01>
   - f(11) = 00: |1100>|00>
   
   State = 1/2(|0000>|00> + |0100>|01> + |1000>|01> + |1100>|00>)
   
   Grouping by f(x):
   = 1/2(|0000> + |1100>)|00> + 1/2(|0100> + |1000>)|01>

4. After H(q[0]) and H(q[1]):
   H⊗2 on the first two qubits:
   
   H⊗2|00> = 1/2(|00> + |01> + |10> + |11>)
   H⊗2|01> = 1/2(|00> - |01> + |10> - |11>)
   H⊗2|10> = 1/2(|00> + |01> - |10> - |11>)
   H⊗2|11> = 1/2(|00> - |01> - |10> + |11>)
   
   For (|0000> + |1100>):
   = (H⊗2 ⊗ I⊗2)(|00> + |11>) ⊗ |00>
   = [1/2(|00>+|01>+|10>+|11>) + 1/2(|00>-|01>-|10>+|11>)] ⊗ |00>
   = [|00> + |11>] ⊗ |00>
   
   For (|0100> + |1000>):
   = [1/2(|00>-|01>+|10>-|11>) + 1/2(|00>+|01>-|10>-|11>)] ⊗ |01>
   = [|00> - |11>] ⊗ |01>

5. The final state before measurement:
   = 1/2(|0000> + |1100>)|00> + 1/2(|0000> - |1100>)|01>
   
   Wait, let me recalculate. The amplitudes should be:
   = 1/2 * [|00>|00> + |11>|00>] ⊗ |00> + 1/2 * [|00>|00> - |11>|00>] ⊗ |01>
   
   Hmm, I'm getting confused with the ordering. Let me be more careful.

   Actually, the state after the oracle is:
   |ψ> = 1/2[|0000>|00> + |0100>|01> + |1000>|01> + |1100>|00

## isqTrain/2867

- task_id: `isqTrain/2867`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `multi_controlled_logic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3094`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[3];
procedure main() {
    H(q[0]);
    H(q[1]);
    CZ(q[0], q[1]);
    H(q[2]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Input: isQ quantum program with 3 qubits (`q[3]`).
    *   Operations: `H(q[0])`, `H(q[1])`, `CZ(q[0], q[1])`, `H(q[2])`.
    *   Measurements: `M(q[0])`, `M(q[1])`, `M(q[2])`.
    *   Output: "## Circuit Analysis" section following the specific format, concise step-by-step reasoning, ending with the probability distribution.
    *   Constraint: Dirac notation, 3-8 lines for simple circuits, no code blocks, end with predicted probabilities.

2.  **Trace the Quantum State:**
    *   Initial state: $|000\rangle$
    *   Apply $H(q[0])$ and $H(q[1])$: The state of $q_0, q_1$ becomes $|+\rangle|+\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
    *   Apply $H(q[2])$: The state of $q_2$ becomes $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
    *   Combined state of $q_0, q_1, q_2$: $\frac{1}{2\sqrt{2}} (|00\rangle + |01\rangle + |10\rangle + |11\rangle) \otimes (|0\rangle + |1\rangle) = \frac{1}{\sqrt{8}} \sum_{x=0}^7 |x\rangle$.
    *   Apply $CZ(q[0], q[1])$: CZ applies a Z gate to $q_1$ if $q_0$ is $|1\rangle$. Wait, let's look at $|+\rangle|+\rangle$ with CZ.
        *   $|+\rangle|+\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
        *   CZ applies a $-1$ phase to $|11\rangle$.
        *   State becomes $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle)$.
        *   Notice that $|00\rangle - |11\rangle = \frac{1}{\sqrt{2}}(|0\rangle|-\rangle - |1\rangle|-\rangle)$? No, let's group by $q_1$: $|0\rangle(|0\rangle+|1\rangle)/2 + |1\rangle(|0\rangle-|1\rangle)/2 = \frac{1}{\sqrt{2}}(|0\rangle|+\rangle + |1\rangle|-\rangle)$.
        *   Let's re-verify: $\frac{1}{\sqrt{2}}(|0\rangle|+\rangle + |1\rangle|-\rangle) = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle)$. Yes.
        *   Since we don't apply another H gate to $q_0, q_1$, the state in the computational basis is an equal superposition of all 4 basis states (up to a phase on $|11\rangle$).
        *   Probabilities are determined by the squared amplitudes: $\left| \pm 1/2 \right|^2 = 1/4$ for each of $|00\rangle, |01\rangle, |10\rangle, |11\rangle$.
    *   $q_2$ is in $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$, which has $1/2$ probability for $|0\rangle$ and $|1\rangle$.
    *   Overall state: $\frac{1}{\sqrt{8}}(|000\rangle + |001\rangle + |010\rangle + |011\rangle + |100\rangle + |101\rangle + |110\rangle - |111\rangle)$.
    *   All computational basis states have amplitude $\pm 1/\sqrt{8}$, giving probability $1/8 = 0.125$ for all states.

3.  **Draft the Explanation:**
    *   Start with $|000\rangle$.
    *   $H(q[0]) \otimes H(q[1]) \otimes H(q[2])$ maps the state to $\frac{1

### Reference answer

{'predicted_probs': {'000': 0.12500000000000003, '001': 0.12500000000000003, '010': 0.12500000000000003, '011': 0.12500000000000003, '100': 0.12500000000000003, '101': 0.12500000000000003, '110': 0.12500000000000003, '111': 0.12500000000000003}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3720

- task_id: `isqTrain/3720`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2352`

### Prompt

实现以下量子计算任务（使用isQ）：QAOA (p=1) for the MaxCut problem on a 3-node star graph with edges [(0, 1), (0, 2)]. Use parameters gamma=0.500 and beta=1.000. The circuit:
1. Initialize all qubits in superposition
2. Apply cost unitary: for each edge, use CNOT-Rz-CNOT
3. Apply mixer: Rx(2*beta) on each qubit
4. Measure all 3 qubits

### Chain-of-thought reasoning

Let me trace through this QAOA circuit step by step.

1. **Goal**: Implement QAOA (p=1) for MaxCut on a 3-node star graph with edges (0,1) and (0,2).

2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.

3. **State evolution**:

**Initial state**: |000⟩

**After Hadamard gates on all qubits**: 
|+⟩|+⟩|+⟩ = (1/√8)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩)

**Cost unitary for edge (0,1)**: CNOT(q[0], q[1]); Rz(2γ, q[1]); CNOT(q[0], q[1])
This implements exp(-iγ Z₀Z₁).

The CNOT-Rz(2γ)-CNOT sequence on qubits 0 and 1 applies a phase of e^(-iγ) when qubits are in same state (|00⟩ or |11⟩) and e^(iγ) when in different state (|01⟩ or |10⟩).

With γ = 0.5:
- |00⟩ gets phase e^(-i·0.5)
- |01⟩ gets phase e^(i·0.5)
- |10⟩ gets phase e^(i·0.5)
- |11⟩ gets phase e^(-i·0.5)

After edge (0,1) cost unitary:
State picks up phases based on qubits 0 and 1 relationship.

**Cost unitary for edge (0,2)**: CNOT(q[0], q[2]); Rz(2γ, q[2]); CNOT(q[0], q[2])
Similarly applies phase based on qubits 0 and 2.

After both cost unitaries, the state is:
|ψ⟩ = (1/√8)[e^(-iγ·2)|000⟩ + |001⟩·(phase based on 0,1 same but 0,2 different) + ...]

Let me be more careful. For each basis state, the total phase is -γ·(Z₀Z₁ + Z₀Z₂) where Z_i is the eigenvalue ±1.

For the Hamiltonian H_C = Z₀Z₁ + Z₀Z₂:
- |000⟩: (+1)(+1) + (+1)(+1) = 2 → phase e^(-iγ·2)
- |001⟩: (+1)(+1) + (+1)(-1) = 0 → phase e^(0) = 1
- |010⟩: (+1)(-1) + (+1)(+1) = 0 → phase 1
- |011⟩: (+1)(-1) + (+1)(-1) = -2 → phase e^(iγ·2)
- |100⟩: (-1)(+1) + (-1)(+1) = -2 → phase e^(iγ·2)
- |101⟩: (-1)(+1) + (-1)(-1) = 0 → phase 1
- |110⟩: (-1)(-1) + (-1)(+1) = 0 → phase 1
- |111⟩: (-1)(-1) + (-1)(-1) = 2 → phase e^(-iγ·2)

With γ = 0.5:
- |000⟩, |111⟩: phase e^(-i) 
- |011⟩, |100⟩: phase e^(i)
- |001⟩, |010⟩, |101⟩, |110⟩: phase 1

So after cost unitary:
|ψ⟩ = (1/√8)[e^(-i)|000⟩ + |001⟩ + |010⟩ + e^(i)|011⟩ + e^(i)|100⟩ + |101⟩ + |110⟩ + e^(-i)|111⟩]

**Mixer unitary**: Rx(2β) on each qubit with β = 1.0, so Rx(2.0) on each qubit.

Rx(θ) = cos(θ/2)I - i·sin(θ/2)X

Rx(2) = cos(1)I - i·sin(1)X

cos(1) ≈ 0.5403
sin(1) ≈ 0.8415

So Rx(2)|0⟩ = cos(1)|0⟩ - i·sin(1)|1⟩
Rx(2)|1⟩ = -i·sin(1)|0

## isqTrain/2497

- task_id: `isqTrain/2497`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `global_phase`, `isq_syntax_arrays`, `isq_syntax_deriving_gate`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `3453`

### Prompt

Do these two isQ programs produce the same measurement results?

Program A:
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
    
    M(q[0]); M(q[1]); M(q[2]);
}

```

Program B:
```isq
import std;
qbit q[3];
procedure my_z(qbit a) {
    Z(a);
} deriving gate
procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
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
    
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A** implements a quantum teleportation circuit. It initializes q[0] to |1>, creates an EPR pair with q[1] and q[2], entangles q[0] and q[1], and then performs Bob's recovery operations using quantum controls (`CNOT(q[1], q[2])` and `ctrl my_z(q[0], q[2])`).
2. **Program B** executes the exact same sequence of quantum operations as Program A.
3. The only difference is the addition of the `GPhase(0.0)` operation at the beginning of Program B.
4. `GPhase(0.0)` applies a global phase factor of $e^{i \cdot 0} = 1$, which is mathematically equivalent to the identity operation. Global phases do not affect measurement probabilities.
5. Verdict: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/312

- task_id: `isqTrain/312`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2517`

### Prompt

用isQ实现implements a variant of the oracle_boolean pattern using y[1] -> y[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The user wants me to analyze the isQ program that implements a variant of the oracle_boolean pattern using y[1] -> y[3] with an expanded qubit register.

Analyzing the circuit requirements:
- x[1] - 1 qubit for input
- y[3] - 3 qubits for output
- Only x[0] is measured

Let me trace through the circuit:

1. Initial state: |0>|000>

2. X(y[0]): Apply X to y[0]
   State: |0>|100>

3. H(x[0]); H(y[0]): Apply Hadamard to x[0] and y[0]
   x[0]: |0> → |+>
   y[0]: |1> → |->
   State: (|0>+|1>)/√2 ⊗ (|0>-|1>)/√2 ⊗ |0>
   = 1/2(|0000> - |0100> + |1000> - |1100>)

4. X(y[0]): Apply X to y[0] - this is the constant oracle f(x)=1
   This flips y[0] again
   State: 1/2(|0100> - |0000> + |1100> - |1000>)
   = -1/2(|0000> - |0100> + |1000> - |1100>)
   
   Actually, let me think more carefully. The oracle for f(x)=1 should flip the phase. In the standard Deutsch algorithm:
   - The ancilla y is in |-> state
   - The oracle Uf for f(x)=1 applies X to y, but since y is in |-> = (|0>-|1>)/√2, applying X gives (|1>-|0>)/√2 = -(|0>-|1>)/√2 = -|->
   - This effectively applies a -1 phase to the x register
   
   So after the oracle X(y[0]):
   State becomes: -(|0>+|1>)/√2 ⊗ (|0>-|1>)/√2 ⊗ |00>
   = -|+>|->|00>

5. H(x[0]): Apply Hadamard to x[0]
   -(|0>+|1>)/√2 → H → -|0>
   
   But wait, the phase on the x register... Let me reconsider.

Actually, I need to be more careful about how the oracle works. The circuit uses X(y[0]) as the oracle, which represents f(x)=1 (constant function).

Let me trace again more carefully:

Initial: |0>_x |000>_y

X(y[0]): |0>_x |100>_y

H(x[0]): (|0>+|1>)/√2 ⊗ |100>_y

H(y[0]): (|0>+|1>)/√2 ⊗ (|0>-|1>)/√2 ⊗ |00>
       = 1/2(|0000> - |0100> + |1000> - |1100>)

Wait, I need to be more careful about the ordering. Let me use |x, y0, y1, y2> ordering.

Initial: |0, 000>

X(y[0]): |0, 100>

H(x[0]): (|0> + |1>)/√2 ⊗ |100>
       = 1/√2 (|0, 100> + |1, 100>)

H(y[0]): 1/√2 (|0> ⊗ H|1> ⊗ |00> + |1> ⊗ H|1> ⊗ |00>)
       = 1/√2 (|0> ⊗ (|0>-|1>)/√2 ⊗ |00> + |1> ⊗ (|0>-|1>)/√2 ⊗ |00>)
       = 1/2 (|0, 000> - |0, 100> + |1, 000> - |1, 100>)

Now X(y[0]) as the oracle:
1/2 (|0, 010> - |0, 000> + |1, 010> - |1, 000>)
= -1/2 (|0, 000> - |0, 010> + |1, 000> - |1, 010>)
= -1/2 ((|0>+|1>) ⊗ |00> - (|0>+|1>) ⊗ |10>) ⊗ |0>
= -1/2 (|0>+|1>) ⊗ (|00>-|10>) ⊗ |0>
= -

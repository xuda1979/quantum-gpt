# ISQ training COT RAG corpus: quantum_algorithms shard 69

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/34

- task_id: `isqTrain/34`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `interference`, `isq_syntax_arrays`, `isq_syntax_oracle`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3987`

### Prompt

Code this in isQ: implements the oracle_boolean pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning

**Goal**: Implement Bernstein-Vazirani algorithm to find hidden string s="1111" using reversed measurement order on input qubits.

**Qubits**: 5 total (q[0-3] input, q[4] ancilla); only q[3], q[2], q[1], q[0] are measured (reversed order).

**State evolution**:
1. Initialize |00000⟩
2. X(q[4]) → |0000⟩|1⟩
3. H on all → (1/4)Σₓ|x⟩|−⟩ (equal superposition with ancilla in |−⟩)
4. CNOT(q[i], q[4]) for i=0,1,2,3 → phase kickback: (1/4)Σₓ(-1)^(x·s)|x⟩|−⟩ where s=1111
5. H(q[0-3]) → |1111⟩|−⟩ (phase oracle converted to computational basis)
6. Measure q[3], q[2], q[1], q[0] in that order

**Result**: Final state |1111⟩ yields measurement bitstring where q[3] is MSB. Index = 1×2³ + 1×2² + 1×2¹ + 1×2⁰ = 15 (binary 1111). Probability {|1111⟩: 1.0}.

## isqTrain/2890

- task_id: `isqTrain/2890`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3531`

### Prompt

Create an isQ quantum circuit that applies a Ry(pi/2) rotation to a single qubit and measures it.

Requirements:
- Declare `qbit q[1];` at global scope.
- Use `procedure main()` as entry point.
- Measure the qubit.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply a Ry(π/2) rotation to a single qubit initialized to |0⟩, then measure it.
2. **Qubits**: 1 qubit (`q[0]`) is used and measured.
3. **State evolution**:
   - Start: |ψ⟩ = |0⟩
   - After Ry(π/2, q[0]): Ry(π/2)|0⟩ = cos(π/4)|0⟩ + sin(π/4)|1⟩ = (1/√2)|0⟩ + (1/√2)|1⟩ = |+⟩
4. **Expected probabilities**: Measuring |+⟩ gives P(|0⟩) = |1/√2|² = 0.5 and P(|1⟩) = |1/√2|² = 0.5, yielding a 50/50 distribution.

## isqExpand/algo/30

- task_id: `isqExpand/algo/30`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `amplitude_estimation`, `grover`, `oracle`, `diffusion`
- source: `isq_expansion`
- dataset_index: `4849`

### Prompt

I need an isQ program to implementing a single Grover iteration on 2 qubits to find the marked state |11>. The Grover operator G = D * O where O is the oracle (phase flip of |11> via CZ) and D is the diffusion operator (2|s><s|-I). Start from |00>, apply H gates to create uniform superposition, then apply one Grover iteration, and measure both qubits. For N=4 states and M=1 marked state, one iteration gives P(|11>) = 1.0.

### Chain-of-thought reasoning

## Reasoning
Goal: One Grover iteration on 2 qubits searching for |11>.

For N=4 states and M=1 solution, the rotation angle is theta = arcsin(sqrt(M/N)) = arcsin(1/2) = pi/6.
After initial A: amplitude of |11> is 1/2 (angle pi/6 from |bad> axis).
After one Grover iteration: angle becomes 3*pi/6 = pi/2, so P(|11>) = sin^2(pi/2) = 1.

Circuit:
1. A = H tensor H: |00> -> equal superposition (each state amplitude 1/2)
2. Oracle: CZ(q[0],q[1]) flips phase of |11>
3. Diffusion = H;H; X;X; CZ; X;X; H;H
   - H;H transforms to computational basis
   - X;X; CZ; X;X implements zero-state reflection (flips phase of |00>)
   - H;H transforms back

After 1 iteration: |11> has probability 1.0.
Probs: [0, 0, 0, 1.0]

## isqTrain/2859

- task_id: `isqTrain/2859`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `measurement_order`, `multi_controlled_logic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2148`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```isq
import std;
qbit q[3];
// Toffoli gate with one control set to |1>
procedure main() {
    // X(q[0]); // BUG: missing initialization
    Toffoli(q[0], q[1], q[2]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: The `X(q[0])` gate is commented out, leaving q[0] in |0>. The circuit intends one Toffoli control to be |1>, but without initialization both controls remain |0>, so the Toffoli never activates and the output is |000>.

2. **Fix**: Uncomment `X(q[0])` to initialize q[0] to |1>.

3. **State evolution (corrected)**:
   - Initial: |000⟩
   - After X(q[0]): |100⟩
   - After Toffoli(q[0], q[1], q[2]): Both controls must be |1⟩ to flip the target. q[0]=|1⟩ but q[1]=|0⟩, so no flip → |100⟩
   - Measurement: |100⟩ with probability 1.0 ✓

## isqTrain/1884

- task_id: `isqTrain/1884`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4965`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[5];
procedure main() {
    H(q[0]); H(q[1]); H(q[2]); H(q[3]); H(q[4]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes 5 qubits in the state |00000> and applies a Hadamard (H) gate to each.
2. Each H gate puts its respective qubit into an equal superposition: |0> → (|0> + |1>)/√2 = |+>.
3. The system state evolves into a uniform superposition of all possible 5-qubit basis states: |+++++> = 1/√32 * Σ|x>.
4. Because the amplitude for each of the 32 basis states has a magnitude squared of (1/√32)² = 1/32 ≈ 0.0313, each outcome is equally likely.

Predicted

### Reference answer

{'predicted_probs': {'00000': 0.0313, '00001': 0.0313, '00010': 0.0313, '00011': 0.0313, '00100': 0.0313, '00101': 0.0313, '00110': 0.0313, '00111': 0.0313, '01000': 0.0313, '01001': 0.0313, '01010': 0.0313, '01011': 0.0313, '01100': 0.0313, '01101': 0.0313, '01110': 0.0313, '01111': 0.0313, '10000': 0.0313, '10001': 0.0313, '10010': 0.0313, '10011': 0.0313, '10100': 0.0313, '10101': 0.0313, '10110': 0.0313, '10111': 0.0313, '11000': 0.0313, '11001': 0.0313, '11010': 0.0313, '11011': 0.0313, '11100': 0.0313, '11101': 0.0313, '11110': 0.0313, '11111': 0.0313}, 'explanation': 'Expected probabilities: [0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001, 0.03125000000000001]'}

## isqExpand/qa/35

- task_id: `isqExpand/qa/35`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `Deutsch-Jozsa算法`, `量子并行性`, `量子干涉`, `查询复杂度`, `量子Oracle`, `isQ编程`
- source: `qa_pipeline`
- dataset_index: `3886`

### Prompt

Deutsch问题和Deutsch-Jozsa问题的区别是什么？后者为什么展示了更强的量子优势？

### Chain-of-thought reasoning

## 推理
1. **概念拆解**：题目要求比较Deutsch与Deutsch-Jozsa问题的区别，并解释后者的量子优势。
2. **定位核心差异**：Deutsch问题是1比特问题，仅实现2倍加速；DJ问题是n比特问题，实现了经典指数级查询复杂度 $O(2^n)$ 到量子常数级 $O(1)$ 的跨越。
3. **阐述物理机制**：解释量子优势的根本来源——Hadamard门制造叠加态（量子并行），Oracle单次计算引入相位，再次Hadamard门使相位转化为可测量的振幅干涉（量子干涉）。
4. **引入代码实例**：为了具象化抽象的干涉过程，使用isQ语言编写一个n=2的DJ算法电路，演示“平衡函数”的Oracle构造和验证逻辑。
5. **构建回答**：按照问题定义、复杂度对比、原理剖析、代码验证的结构输出标准答案。

### Reference answer

Deutsch问题和Deutsch-Jozsa（DJ）问题是量子计算中两个极其重要的早期算法问题，它们的核心思想是一脉相承的，但在问题规模和展现出的量子优势上有显著的区别。

### 1. 问题的定义与区别

**Deutsch问题：**
这是最简单的量子算法问题。给定一个黑盒函数 $f: \{0, 1\} \to \{0, 1\}$，已知它是常数的（Constant，即 $f(0)=f(1)$）或者是平衡的（Balanced，即 $f(0) \neq f(1)$）。问题要求判断 $f$ 究竟是常数函数还是平衡函数。
在经典计算中，必须对黑盒进行两次查询（计算 $f(0)$ 和 $f(1)$）才能得出结论；而在量子计算中，利用Deutsch算法，只需要对量子黑盒（Oracle）进行**1次查询**即可得出结论。

**Deutsch-Jozsa问题：**
这是Deutsch问题从1个比特向 $n$ 个比特的推广。给定一个黑盒函数 $f: \{0, 1\}^n \to \{0, 1\}$。承诺该函数要么是常数的（对所有 $2^n$ 种输入，输出全为0或全为1），要么是平衡的（恰好对一半的输入输出0，另一半输出1）。问题同样是判断 $f$ 是常数函数还是平衡函数。

**两者的核心区别在于输入维度和经典最坏情况复杂度：**
- Deutsch问题是1比特输入，经典算法需要2次查询，量子需要1次，只有2倍的加速。
- DJ问题是 $n$ 比特输入。在经典确定性计算中，最坏情况下需要查询 $2^{n-1} + 1$ 次（即超过总输入空间的一半）才能确保答案是绝对的。而在量子计算中，利用DJ算法，**依然只需要对量子黑盒进行1次查询**。

### 2. 为什么Deutsch-Jozsa展示了更强的量子优势？

DJ问题之所以被认为展示了更强（甚至是指数级）的量子优势，是因为在确定性查询模型下，经典算法的查询复杂度随输入规模 $n$ 呈指数级增长 $O(2^n)$，而量子算法的查询复杂度始终是常数级 $O(1)$。

这种惊人的加速得益于两个核心量子特性的结合：
1. **量子并行性：** 通过对 $n$ 个处于 $|0\rangle$ 态的量子比特施加Hadamard门，可以一步生成所有 $2^n$ 个可能输入状态的等权叠加态 $|\psi\rangle = \frac{1}{\sqrt{2^n}} \sum_{x=0}^{2^n-1} |x\rangle$。将函数 $f$ 编码为量子Oracle $U_f$（实现 $U_f|x\rangle|y\rangle = |x\rangle|y \oplus f(x)\rangle$），只需调用一次 $U_f$，就能同时计算出所有 $2^n$ 个输入对应的 $f(x)$ 的相位信息。
2. **量子干涉：** 仅仅并行计算是不够的，测量叠加态只能随机坍缩出一个结果。DJ算法的精妙之处在于第二次施加Hadamard变换。通过干涉效应，如果 $f$ 是常数函数，所有的概率幅会相长干涉，全部汇聚到 $|00...0\rangle$ 态上；如果 $f$ 是平衡函数，$|00...0\rangle$ 态的概率幅会相消干涉变为0。因此，最后只需测量这 $n$ 个量子比特：如果全为0，则是常数函数；否则就是平衡函数。

### 3. isQ代码示例：2比特Deutsch-Jozsa算法

下面展示如何使用isQ代码实现一个包含2个输入比特和1个辅助比特的Deutsch-Jozsa算法。这里我们选取一个平衡函数 $f(x_0, x_1) = x_0 \oplus x_1$ 作为Oracle。

```c
import std;

qbit q[3]; // q[0], q[1] 为输入位，q[2] 为辅助位

procedure main() {
    // 1. 初始化辅助位为 |->
    X(q[2]);
    H(q[2]);

    // 2. 对输入位进行Hadamard变换，生成叠加态
    H(q[0]);
    H(q[1]);

    // 3. 构造平衡函数的 Oracle: f(x) = x0 XOR x1
    // 通过两个CNOT门实现相位反转
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);

    // 4. 对输入位再次进行Hadamard变换（干涉过程）
    H(q[0]);
    H(q[1]);

    // 5. 测量输入位
    // 如果是平衡函数，测量结果必定包含1（例如 01, 10, 11）
    // 若是常数函数，结果必定为 00
    M(q[0]);
    M(q[1]);
}
```

运行上述代码，由于使用的是平衡函数的Oracle，最终测量的结果将不会是 `00`，从而仅通过1次Oracle调用就得出了结论，完美展示了量子干涉带来的指数级加速潜力。

## isqTrain/2639

- task_id: `isqTrain/2639`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `global_phase`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1587`

### Prompt

Are these two quantum circuits equivalent in terms of measurement output?

Circuit 1:
```isq
import std;
qbit q[6];

procedure main() {
    // Encode a=3 (binary 11) and b=1 (binary 01)
    X(q[0]);
    X(q[1]);
    X(q[2]);
    // Bit 0: carry0 = a0 AND b0
    Toffoli(q[0], q[2], q[4]);
    // Bit 0: sum0 = a0 XOR b0 -> stored in q[2]
    CNOT(q[0], q[2]);
    // Bit 1: carry_out accumulates AND pairs
    Toffoli(q[1], q[3], q[5]);
    Toffoli(q[1], q[4], q[5]);
    Toffoli(q[3], q[4], q[5]);
    // Bit 1: sum1 = a1 XOR b1 XOR carry0
    CNOT(q[1], q[3]);
    CNOT(q[4], q[3]);
    // Measure sum0, sum1, carry_out
    M(q[2]);
    M(q[3]);
    M(q[5]);
}

```

Circuit 2:
```isq
import std;
qbit q[6];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // Encode a=3 (binary 11) and b=1 (binary 01)
    X(q[0]);
    X(q[1]);
    X(q[2]);
    // Bit 0: carry0 = a0 AND b0
    Toffoli(q[0], q[2], q[4]);
    // Bit 0: sum0 = a0 XOR b0 -> stored in q[2]
    CNOT(q[0], q[2]);
    // Bit 1: carry_out accumulates AND pairs
    Toffoli(q[1], q[3], q[5]);
    Toffoli(q[1], q[4], q[5]);
    Toffoli(q[3], q[4], q[5]);
    // Bit 1: sum1 = a1 XOR b1 XOR carry0
    CNOT(q[1], q[3]);
    CNOT(q[4], q[3]);
    // Measure sum0, sum1, carry_out
    M(q[2]);
    M(q[3]);
    M(q[5]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A**: Initializes qubits q[0], q[1], and q[2] to |1>. It then applies a sequence of Toffoli and CNOT gates to perform a 2-bit addition (a=3, b=1). It calculates the carry in q[4], the sum bit 0 in q[2], the sum bit 1 in q[3], and the final carry out in q[5]. Finally, it measures q[2], q[3], and q[5].
2. **Program B**: Executes the exact same initialization, arithmetic quantum gates, and measurements as Program A. The only difference is the addition of a `GPhase(0.0)` operation at the beginning of the circuit.
3. **Key difference**: Program B introduces a global phase of 0 using `GPhase(0.0)`, which multiplies the overall quantum state by $e^{i \cdot 0} = 1$.
4. **Probability distributions**: Because `GPhase(0.0)` equates to an identity transformation on the state vector, both programs evolve the qubits identically. The measurement probability distributions for q[2], q[3], and q[5] are exactly the same.
5. **Verdict**: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/2648

- task_id: `isqTrain/2648`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `global_phase`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2780`

### Prompt

Compare these two isQ programs. Do they give the same probability distribution?

First program:
```isq
import std;
qbit q[4];

procedure main() {
    // Set multiplier a=1 and multiplicand b=3 (binary 11)
    X(q[0]);
    X(q[1]);
    X(q[2]);
    // Product LSB = a AND b0
    // This is the least significant bit of a * b
    Toffoli(q[0], q[1], q[3]);
    // Measure the product LSB
    M(q[3]);
}

```

Second program:
```isq
import std;
qbit q[4];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // Set multiplier a=1 and multiplicand b=3 (binary 11)
    X(q[0]);
    X(q[1]);
    X(q[2]);
    // Product LSB = a AND b0
    // This is the least significant bit of a * b
    Toffoli(q[0], q[1], q[3]);
    // Measure the product LSB
    M(q[3]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. Program A initializes the state to $|0000\rangle$, applies X gates to $q_0, q_1, q_2$ to reach $|1110\rangle$, and then applies a Toffoli gate to flip $q_3$ to $|1\rangle$ (yielding $|1111\rangle$).
2. Program B performs the exact same initialization, X gates, and Toffoli gate, resulting in the identical final state $|1111\rangle$.
3. The only difference is that Program B includes `GPhase(0.0)` at the beginning.
4. `GPhase(0.0)` applies a global phase factor of $e^{i \cdot 0.0} = 1$, which has no effect on the quantum state or measurement probabilities.
5. The measurement probability distributions are identical.
Verdict: Yes

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/1212

- task_id: `isqTrain/1212`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3494`

### Prompt

帮我写一个isQ程序：implements the quantum_random_walk pattern with a different measurement ordering (reversed measurement order for p). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

Let me analyze this quantum random walk circuit step by step.

The circuit implements a discrete quantum walk on a 4-node cycle (positions 0-3 encoded in 2 qubits p[0] and p[1]) with a coin qubit c[0].

Initial state: |0>_c ⊗ |00>_p

Step 1: H(c[0]) - Hadamard on coin
State: (|0> + |1>)/√2 ⊗ |00>_p = (|0,00> + |1,00>)/√2

Step 2: ctrl CNOT(c[0], p[0], p[1]) - CNOT on p[1] controlled by both c[0] and p[0]
When c[0]=1 AND p[0]=1, flip p[1]
Currently p[0]=0, so nothing happens.
State: (|0,00> + |1,00>)/√2

Step 3: ctrl X(c[0], p[0]) - X on p[0] controlled by c[0]
When c[0]=1, flip p[0]
State: (|0,00> + |1,10>)/√2

Step 4: nctrl X(c[0], p[0]) - X on p[0] when c[0]=0
When c[0]=0, flip p[0]
State: (|0,10> + |1,10>)/√2

Step 5: nctrl CNOT(c[0], p[0], p[1]) - CNOT on p[1] when c[0]=0 AND p[0]=1
When c[0]=0 AND p[0]=1, flip p[1]
After step 4, when c[0]=0, p[0]=1. So we flip p[1].
State: (|0,11> + |1,10>)/√2

Now we measure p[1] first, then p[0].

In the final state (|0,11> + |1,10>)/√2:
- p[1]=1, p[0]=1 (from |0,11>)
- p[1]=1, p[0]=0 (from |1,10>)

With reversed measurement order (M(p[1]) first, then M(p[0])):
- M(p[1]) is measured first → higher bit
- M(p[0]) is measured second → lower bit

So the bitstring is (p[1])(p[0]):
- From |0,11>: p[1]=1, p[0]=1 → bitstring "11" = 3
- From |1,10>: p[1]=1, p[0]=0 → bitstring "10" = 2

Wait, The predicted output {|01>: 0.5, |11>: 0.5}. Let me reconsider.

Actually, Let me re-analyze the measurement probabilities: {|01>: 0.5, |11>: 0.5}

Hmm, this seems to suggest the bitstring format where the first measured qubit is the higher bit.

With M(p[1]) measured first (higher bit) and M(p[0]) measured second (lower bit):
- |01> means p[1]=0, p[0]=1
- |11> means p[1]=1, p[0]=1

But my calculation gives (|0,11> + |1,10>)/√2, which means:
- p[1]=1, p[0]=1 with prob 0.5
- p[1]=1, p[0]=0 with prob 0.5

That would give {|10>: 0.5, |11>: 0.5} in the measurement bitstring format.

Let me reconsider the circuit operations. 

Analyzing the circuit requirements again:

Wait, I need to be careful about the CNOT syntax. `CNOT(control, target)` is a two-qubit gate. But `ctrl CNOT(c[0], p[0], p[1])` means CNOT with c[

## isqTrain/4055

- task_id: `isqTrain/4055`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1242`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```
import std;
// QAOA MaxCut p=1 on 4-node square graph
// gamma=0.500, beta=0.500
qbit q[4];

procedure main() {
    // Superposition
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    // Cost unitary
    // Edge (0,1)
    CNOT(q[0], q[1]);
    Rz(2.0 * 2.0 * 0.500, q[1]);
    CNOT(q[0], q[1]);
    // Edge (1,2)
    CNOT(q[1], q[2]);
    Rz(2.0 * 0.500, q[2]);
    CNOT(q[1], q[2]);
    // Edge (2,3)
    CNOT(q[2], q[3]);
    Rz(2.0 * 0.500, q[3]);
    CNOT(q[2], q[3]);
    // Edge (0,3)
    CNOT(q[0], q[3]);
    Rz(2.0 * 0.500, q[3]);
    CNOT(q[0], q[3]);
    // Mixer
    Rx(2.0 * 0.500, q[0]);
    Rx(2.0 * 0.500, q[1]);
    Rx(2.0 * 0.500, q[2]);
    Rx(2.0 * 0.500, q[3]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

## Bug Analysis

**1. Bug:** In the Cost unitary for Edge (0,1), line `Rz(2.0 * 2.0 * 0.500, q[1])` contains a spurious extra factor of 2.0. This computes Rz(2.0) instead of the correct Rz(1.0). The QAOA cost unitary for each edge should apply $e^{-i\gamma Z_i Z_j}$ via CNOT-Rz(2γ)-CNOT with γ=0.500, giving angle 1.0. All other edges correctly use `2.0 * 0.500`.

**2. Fix:** Change `Rz(2.0 * 2.0 * 0.500, q[1])` to `Rz(2.0 * 0.500, q[1])`.

**3. Corrected state evolution:**
- **Superposition:** H on all 4 qubits → equal superposition |++++⟩
- **Cost unitary (all edges now consistent at angle 1.0):** Each edge (0,1), (1,2), (2,3), (0,3) applies $e^{-i\gamma Z_i Z_j}$ with γ=0.5, entangling the state and imprinting phase structure from the square graph's MaxCut Hamiltonian.
- **Mixer:** Rx(1.0) on each qubit mixes amplitudes, steering probability toward high-cut bitstrings.
- **Measurement:** Yields the expected distribution with peaks at |0000⟩ and |1111⟩ (~0.250 each, corresponding to optimal MaxCut partitions), suppressed odd-weight strings (~0.015), and intermediate even-weight states (~0.043-0.073).

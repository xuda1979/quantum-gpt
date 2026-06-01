# ISQ training COT RAG corpus: quantum_algorithms shard 197

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4294

- task_id: `isqTrain/4294`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `876`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

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
    X(q[0]); // flip qubit 0 before measurement
    M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a step-by-step reasoning for an isQ quantum program.
    *   Output: "## Circuit Analysis" section, ending with the probability distribution.
    *   Constraint: Use Dirac notation, concise (3-15 lines), no `isq` code blocks.
    *   Input program:
        *   `qbit q[4];`
        *   `X(q[0]); X(q[1]); X(q[2]);` -> `|1110>`
        *   `Toffoli(q[0], q[1], q[3]);` -> Flips `q[3]` since `q[0]` and `q[1]` are 1. -> `|1111>`
        *   `X(q[0]);` -> Flips `q[0]`. -> `|0111>`
        *   `M(q[3]);` -> Measures `q[3]` (which is 1). Wait, let's carefully map qubits to bitstrings for --probs output.
    *   Measurement order in isQ `--probs` mode: "array indexed by measurement bitstring (earlier measured qubit = higher bit)". Wait, if only `M(q[3])` is measured, how is the full state represented?
    *   Wait, the prompt says: "Expected measurement probabilities: {|0001>: 1.0}". Let's trace why.
        *   Initial: `|0000>`
        *   X(q[0]), X(q[1]), X(q[2]) -> `q[0]=1, q[1]=1, q[2]=1, q[3]=0`. State is `|1110>` (q[0] is lowest bit or highest bit?)
        *   Usually in isQ, `q[0]` is the rightmost bit (LSB) or leftmost? Let's check the predicted output: `{|0001>: 1.0}`.
        *   If the output is `|0001>`, then `q[0]` is the *highest* bit (leftmost) or the lowest (rightmost)?
        *   Let's look at standard bitstring indexing: `q[0]` is the highest bit (index 0) -> `|q[0] q[1] q[2] q[3]>`.
        *   Let's re-evaluate: `X(q[0]), X(q[1]), X(q[2])` -> state `|1110>`.
        *   Toffoli(q[0], q[1], q[3]) flips q[3] since q[0]=1 and q[1]=1. State becomes `|1111>`.
        *   X(q[0]) flips q[0]. State becomes `|0111>`.
        *   The predicted is `{|0001>: 1.0}`. This implies my bitstring mapping is wrong.
        *   What if `q[0]` is LSB? Then `X(q[0]), X(q[1]), X(q[2])` -> `|q[3]q[2]q[1]q[0]>` = `|0111>`.
        *   Toffoli(q[0], q[1], q[3]) flips `q[3]`. State becomes `|1111>`.
        *   X(q[0]) flips `q[0]`. State becomes `|1110>`. Still doesn't match `|0001>`.
        *   Let's reconsider: `q[0]` to `q[3]` as `q[3]q[2]q[1]q[0]`. Wait, what if it's just `|q[0]q[1]q[2]q[3]>`?
        *   Let's read the expected: `{|0001>: 1.0}`.
        *   If `q[i]` corresponds to bit position $N - 1 - i$? Then $q[0]$ is bit 3 (MSB), $q[1]$ is bit 2, $q[2]$ is bit 1, $q[3]$ is bit 0.
        *   Then `X(q[0]), X(q[1]), X(q[2])` -> `|1110>`.
        *   Toffoli flips `q[3]` -> `|1111>`.
        *   `X(q[0])` -> `|0111>`.
        *   Still `|0111>`.
        *   Let's reread the expected. Wait, maybe `q[0]` is bit 0

### Reference answer

{'predicted_probs': {'0001': 1.0}, 'explanation': 'This isQ program operates on 4 qubit(s). The measurement probability distribution is: P(|0001>) = 1.0000.'}

## isqTrain/4558

- task_id: `isqTrain/4558`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `639`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[5];

procedure main() {
    
    X(q[0]); X(q[1]);
    
    X(q[2]); X(q[3]);
    
    ctrl ctrl X(q[0], q[2], q[4]);
    
    ctrl ctrl X(q[1], q[3], q[4]);
    
    H(q[4]); // superposition on last qubit
    M(q[4]);
}
```

### Chain-of-thought reasoning

The user wants an analysis of the given isQ program.
The program has 5 qubits.
1. `X(q[0]); X(q[1]);` -> Initial state |00000> becomes |01100> (q[1]=1, q[0]=1). Wait, q[0] is the least significant bit (bit 0).
Let's trace the state:
Initial: |00000>
After X(q[0]), X(q[1]) : |00011> (q[1]=1, q[0]=1) -> |3>
After X(q[2]), X(q[3]) : |01111> (q[3]=1, q[2]=1, q[1]=1, q[0]=1) -> |15>
After ctrl ctrl X(q[0], q[2], q[4]):
q[0] and q[2] are in state |1>. So this Toffoli flips q[4].
State becomes |11111> -> |31>
After ctrl ctrl X(q[1], q[3], q[4]):
q[1] and q[3] are in state |1>. So this Toffoli flips q[4].
q[4] was |1>, so it becomes |0>.
State becomes |01111> -> |15>
After H(q[4]):
q[4] is |0>. H|0> = |+> = (|0> + |1>) / sqrt(2).
State becomes (|01111> + |11111>) / sqrt(2).
Or written fully: (|15> + |31>) / sqrt(2).

Measurement:
Measuring all 5 qubits.
Prob(|01111>) = 0.5. In bitstring, q[4]q[3]q[2]q[1]q[0].
Wait, let's verify the bit order in the predicted output: {|00000>: 0.5, |00001>: 0.5}. This implies q[0] was not 1, but wait, wait, no, the expected measurement probabilities are given as:
Expected measurement probabilities: {|00000>: 0.5, |00001>: 0.5}. Wait! Is this correct?
If the state is (|01111> + |11111>) / sqrt(2), then the measurement probabilities would be {|01111>: 0.5, |11111>: 0.5}. But wait, wait, wait, wait.
Let's check the code:

This applies X to q[0], q[1], q[2], q[3].
State is |00000> -> |01111> (q[4]q[3]q[2]q[1]q[0]).
Wait, q[4] is 0, q[3] is 1, q[2] is 1, q[1] is 1, q[0] is 1. So it's |01111>.
Toffoli(q[0], q[2], q[4]): controls are q[0]=1, q[2]=1, target q[4]. q[4] becomes 1. State: |11111>.
Toffoli(q[1], q[3], q[4]): controls are q[1]=1, q[3]=1, target q[4]. q[4] becomes 0. State: |01111>.
H(q[4]): q[4] becomes (|0>+|1>)/sqrt(2). State: (|01111> + |11111>) / sqrt(2).
Why did the prompt say "Expected measurement probabilities: {|00000>: 0.5, |00001>: 0.5}"? Wait. Oh, maybe The implementation provided in the prompt was an example, but I should generate the REAL probabilities. Or wait, maybe The implementation is wrong? Or maybe I'm interpreting the string incorrectly.
Wait, if it's {|00000>: 0.5, |00001>: 0.5}, that means q[4], q[3], q[2], q[1] are all 0, and q[0] is 0 or 1. But the code applies X to q[0], q[1], q[2], q[3]!
Ah! In the expected measurement probabilities, what does it say?
"Expected measurement probabilities: {|01111>: 0.5, |11111>: 0.5}"
Wait, no, let me read carefully. The prompt says: "Expected measurement probabilities: {|000

### Reference answer

{'predicted_probs': {'00000': 0.5, '00001': 0.5}, 'explanation': 'This isQ program operates on 5 qubit(s). The measurement probability distribution is: P(|00000>) = 0.5000, P(|00001>) = 0.5000.'}

## isqTrain/84

- task_id: `isqTrain/84`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3084`

### Prompt

Write isQ code for the following quantum task: implements a variant of the amplitude_amplification pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The task asks me to write reasoning for an amplitude amplification variant using q[2] -> q[3], with an expanded qubit register. Let me analyze what's needed.

Analyzing the circuit requirements, it uses 3 qubits (q[0], q[1], q[2]) and implements a 2-qubit amplitude amplification on q[0] and q[1] to find |11>, then measures all 3 qubits. The third qubit q[2] is never touched, so it stays in |0>.

The task says "variant using q[2] -> q[3]" which suggests using qubits 2 and 3 instead of 0 and 1. The "expanded qubit register" means more qubits than the base version.

Let me think about this:
- Base version uses 2 qubits for amplitude amplification
- This variant should use q[2] and q[3] for the amplification
- Need an expanded register, so maybe 4 qubits total

The amplitude amplification circuit:
1. Initialize with H gates on the target qubits
2. Apply oracle (marks the target state with a phase flip)
3. Apply diffuser (inversion about the mean)

For q[2] and q[3] targeting |11>:
- H(q[2]); H(q[3]) → creates superposition
- Oracle: my_cz(q[2], q[3]) marks |11> with -1 phase
- Diffuser: H, X, CZ, X, H

With 4 qubits, measuring all of them, the expected state should be |0111> or similar depending on which qubits we use and measure.

Wait, Let me re-analyze the output: {|110>: 1.0} with 3 qubits measured for the reference.

So The implementation:
- Uses 3 qubits
- Operates on q[0] and q[1] with amplitude amplification
- q[2] stays |0>
- Final state is |110> (q[0]=1, q[1]=1, q[2]=0)

For the variant with q[2] -> q[3]:
- Use 4 qubits
- Operate on q[2] and q[3]
- q[0] and q[1] stay |0>
- Final state would be |0011> if measuring all 4

Let me write the reasoning for this circuit.

Actually, re-reading the prompt more carefully - it says "Write an isQ program that implements a variant of the amplitude_amplification pattern using q[2] -> q[3]."

This is asking me to create a variant that uses qubits 2 and 3 instead of qubits 0 and 1. The circuit structure remains the same (amplitude amplification to find |11>), just operating on different qubits.

For 4 qubits with the amplitude amplification on q[2] and q[3]:
- q[0] and q[1] remain in |0>
- q[2] and q[3] go through the amplitude amplification to end in |11>
- Final state: |0011>

Expected measurement: {|0011>: 1.0} with 4 qubits measured.

Let me write the reasoning:

## Reasoning
1. Goal: Implement amplitude amplification on qubits q[2] and q[3] to find |11>, using an expanded 4-qubit register.
2. Qubits: 4 total (q[0], q[1], q[2], q[3]); all measured.
3. State evolution:
   - Initial: |0000>
   - After H(q[2]), H(q[3]): |00> ⊗ (|00>+|01>+|10>+|11>)/2 = (|0000>+|0001>+|0010>+|0011>)/2
   - Oracle (my_cz on q[2],q[3]): marks |0011> with phase -1 → (|0000>+|0001>+|0010>-|0011>)/2
   - Diffuser: H(q[2]), H(q[3]) transforms to (|0011>+|0000>+|0001>+|0010>)/2 with |0011> amplified
   - After full diffuser (H, X, CZ, X, H): state becomes |0011>
4. Expected probabilities: {|0011>: 1.0} because amplitude amplification converges to the oracle-marked state |11> on q[2],q[3].

Hmm, let me be more careful with the state evolution. The amplitude amplification for 2 qubits with one iteration finding |11>:

Starting state: (|00>+

## isqExpand/algo/2

- task_id: `isqExpand/algo/2`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `grover`, `amplitude_amplification`, `quadratic_speedup`
- source: `qa_pipeline`
- dataset_index: `1008`

### Prompt

Grover算法为什么能实现二次加速？请从振幅放大的角度解释其核心原理。

### Chain-of-thought reasoning

## 推理
目标：解释Grover算法二次加速的原理。

关键点：
1. 量子态可以在目标态和非目标态构成的二维平面中旋转
2. 每次Grover迭代（Oracle + Diffusion）相当于旋转2θ角度
3. 初始角度θ ≈ 1/√N，需要旋转到π/2
4. 所需迭代次数 ≈ π√N/4 = O(√N)
5. 这是几何上的必然结果，不依赖具体问题结构

### Reference answer

Grover算法的核心机制是**振幅放大（Amplitude Amplification）**。

## 基本原理

在N个元素的无序数据库中搜索目标，经典算法需要O(N)次查询，而Grover算法只需O(√N)次。

## 几何解释

将量子态空间分为两个子空间：目标态|t>和非目标态|t⊥>。初始均匀叠加态|s>可以写为：
|s> = sin(θ)|t> + cos(θ)|t⊥>

其中 sin(θ) = 1/√N。

Grover迭代 G = D·O 执行两次反射：
1. Oracle O：关于|t⊥>的反射（翻转目标态的相位）
2. Diffusion D：关于|s>的反射（2|s><s|-I）

两次反射的组合等价于在|t>-|t⊥>平面上旋转角度2θ。

## 为什么是√N

每次迭代旋转2θ ≈ 2/√N弧度。要从初始角度θ旋转到π/2（即完全对准|t>），需要约 π/(4θ) ≈ π√N/4 次迭代。

这就是O(√N)的来源——不是指数加速，而是二次加速，但对于大规模搜索已经非常显著。

## isQ示例

```isq
import std;
qbit q[2];

procedure main() {
    // 2-qubit Grover: 1次迭代即可找到目标
    H(q[0]); H(q[1]);
    // Oracle + Diffusion
    CZ(q[0], q[1]);
    H(q[0]); H(q[1]);
    X(q[0]); X(q[1]);
    CZ(q[0], q[1]);
    X(q[0]); X(q[1]);
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}
```

## isqTrain/2876

- task_id: `isqTrain/2876`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3447`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[2];
procedure main() {
    X(q[1]);
    H(q[0]);
    ctrl T(q[0], q[1]);
    H(q[0]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a step-by-step reasoning for an isQ quantum program to determine the final state before measurement and probability distribution.
    *   Input: isQ program with X, H, ctrl T, H on 2 qubits.
    *   Constraints: Concise (3-15 lines). Use Dirac notation. Start with "## Circuit Analysis". End with the predicted probability distribution. Output ONLY the analysis. no code blocks.

2.  **Analyze the Circuit:**
    *   Initial state: |00>
    *   `X(q[1])`: Applies X to q1. State becomes |01>.
    *   `H(q[0])`: Applies H to q0. State becomes 1/√2 (|00> - |10>) *wait, no. H|0> = |+> = (|0>+|1>)/√2. So state is (|+0> * wait, q1 is 1. So H(q0) on |01> gives 1/√2 (|01> + |11>).* Let me be precise: (|0> + |1>)_0 / √2 ⊗ |1>_1 = (|01> + |11>)/√2.
    *   `ctrl T(q[0], q[1])`: Controlled-T gate. Applies T to q[1] if q[0] is |1>. T = diag(1, e^{iπ/4}). State becomes 1/√2 (|01> + e^{iπ/4}|11>).
    *   `H(q[0])`: Applies H to q0. Let's trace this:
        H_0 (1/√2 (|01> + e^{iπ/4}|11>))
        = 1/√2 (H_0|0>|1> + e^{iπ/4} H_0|1>|1>)
        H_0|0> = (|0>+|1>)/√2
        H_0|1> = (|0>-|1>)/√2
        = 1/2 ( (|0>+|1>)|1> + e^{iπ/4}(|0>-|1>)|1> )
        = 1/2 ( (1 + e^{iπ/4})|01> + (1 - e^{iπ/4})|11> )
    *   Let's compute the probabilities:
        P(01) = |1/2 (1 + e^{iπ/4})|^2 = 1/4 (1 + e^{iπ/4})(1 + e^{-iπ/4}) = 1/4 (1 + 1 + 2cos(π/4)) = 1/4 (2 + √2) ≈ 1/4 (3.414) = 0.85355...
        P(11) = |1/2 (1 - e^{iπ/4})|^2 = 1/4 (1 - e^{iπ/4})(1 - e^{-iπ/4}) = 1/4 (1 + 1 - 2cos(π/4)) = 1/4 (2 - √2) ≈ 1/4 (0.586) = 0.14645...
        the predicted output matches: {'01': 0.8535533905932737, '11': 0.14644660940672624}

3.  **Draft the Explanation (incorporating step-by-step evolution):**
    *   Start state: |00>
    *   X(q[1]) -> |01>
    *   H(q[0]) -> (|01> + |11>)/√2
    *   ctrl T(q[0], q[1]) -> (|01> + e^{iπ/4}|11>)/√2
    *   H(q[0]) -> (1/2)(1+e^{iπ/4})|01> + (1/2)(1-e^{iπ/4})|11>
    *   Probabilities: P(01) = cos²(π/8) = (2+√2)/4 ≈ 0.8536, P(11) = sin²(π/8) = (2-√2)/4 ≈ 0.1464.
    *   Check dirac notation and rules. "Output ONLY the analysis, starting with "## Circuit Analysis""

4.  **Refine and Format:**
    ## Circuit Analysis
    1. **Initial state:** |00>

### Reference answer

{'predicted_probs': {'01': 0.8535533905932737, '11': 0.14644660940672624}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/846

- task_id: `isqTrain/846`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `finite_field_arithmetic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2277`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the finite_field_inversion pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The task asks me to write an isQ program implementing a variant of finite_field_inversion using q[2] -> q[3], with an expanded qubit register.

Let me analyze The implementation:
- Uses 3 qubits
- Sets q[0] to |1⟩ via X gate
- CNOT copies q[0] to q[1]
- Measures q[1] and q[2]
- predicted output: |10⟩ with probability 1.0

So q[1] = 1 (copied from q[0]), q[2] = 0 (unchanged)

The variant asks for q[2] -> q[3], which means:
- Using 4 qubits instead of 3 (expanded register)
- The inversion should map from q[2] to q[3]

Wait, let me re-read. "using q[2] -> q[3]" - this seems to indicate the mapping is from qubit 2 to qubit 3.

Let me think about this more carefully. The reference uses:
- q[0] as input
- q[1] as output (inverse)
- q[2] as another qubit measured but initialized to 0

For the variant with q[2] -> q[3]:
- Use 4 qubits
- q[2] is input
- q[3] is output (inverse)

So I need to:
1. Declare qbit q[4]
2. Set q[2] to |1⟩ (the invertible element in GF(2))
3. CNOT(q[2], q[3]) to copy/invert
4. Measure q[2] and q[3] (or maybe q[3] and something else)

The predicted measurement is still |10⟩ with probability 1.0. Let me check the bit ordering.

In --probs mode, "earlier measured qubit = higher bit". So if I measure q[2] first, then q[3]:
- Bit 1 (higher) = q[2]
- Bit 0 (lower) = q[3]
- |10⟩ means q[2]=1, q[3]=0

Hmm, that doesn't match. Let me reconsider.

Actually, Analyzing the:
- X(q[0]) sets q[0] = |1⟩
- CNOT(q[0], q[1]) copies q[0] to q[1], so q[1] = |1⟩
- M(q[1]) then M(q[2])
- Expected |10⟩ means q[1]=1, q[2]=0

So for my variant:
- Need to set input to 1 on q[2]
- CNOT(q[2], q[3]) copies to q[3]
- M(q[3]) then M(q[?])

Actually, I need to think about which qubits to measure. The predicted output |10⟩ with probability 1.0.

Let me reconsider the problem. The variant "using q[2] -> q[3]" with expanded register means:
- 4 qubits total
- Input is q[2], output is q[3]
- Set q[2] = |1⟩
- CNOT(q[2], q[3]) so q[3] = |1⟩
- Need to measure 2 qubits

For |10⟩ result:
- If I measure q[2] first (higher bit), then q[3] (lower bit):
  - |10⟩ means q[2]=1, q[3]=0 - but q[3] should be 1!

- If I measure q[3] first (higher bit), then q[2] (lower bit):
  - |10⟩ means q[3]=1, q[2]=0 - but q[2] should be 1!

Hmm, this is confusing. Let me look at the reference more carefully.

Reference:
- q[0] = 1 (after X)
- CNOT(q[0], q[1]) → q[1] = 1
- M(q[1]) then M(q[2])
- |10⟩ = q[1]=1, q[2]=0 ✓

So higher bit is the first measured qubit. In the reference, q[1] is measured first and equals 1 (higher bit), q[2] is measured second and equals 0 (lower bit). Result |10⟩.

For my variant with 4 qubits:
- Set q[2] = |1⟩ with X(q[2])
- CNOT(q[2], q[3]) → q[3] = 1
- M(q[3]) first → this is the higher bit = 1
- M(q[?]) second → this

## isqQA/quantum_algorithms/48_principle_advantage

- task_id: `isqQA/quantum_algorithms/48_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `principle_advantage`, `algorithm`, `量子振幅放大`
- source: `qa_pipeline`
- dataset_index: `364`

### Prompt

请详细解释量子振幅放大算法的宏观原理，并对比它在时间复杂度上相较于经典算法的优势。此外，请深入分析这种量子加速的根本来源是什么？

### Reference answer

量子振幅放大是量子计算中一种极其核心的底层原理，也是著名Grover搜索算法的直接推广。它的宏观原理可以通过希尔伯特空间中的几何旋转来直观理解。

假设我们有一个量子初态制备算法A，作用于全零态后产生叠加态：$|\psi\rangle = A|0\rangle$。在这个叠加态中，包含我们需要的“好态”（目标解）和不需要的“坏态”（非目标解）。假设测量得到好态的概率为$p$。在经典情况下，如果我们想要找到一个好态，只能不断地制备态$|\psi\rangle$并测量，预期的尝试次数为$O(1/p)$。

量子振幅放大算法则巧妙地利用了量子态的相位和干涉。它构造了一个迭代算子$Q = -A S_0 A^{-1} S_\chi$。其中，$S_\chi$是预言机，负责将所有“好态”的相位翻转180度；$S_0$负责将全零态$|0\rangle$的相位翻转180度。整个系统状态可以被看作是由“好态”和“坏态”张成的一个二维平面。每一次应用算子$Q$，就相当于在这个二维平面中，将系统的状态向量朝着“好态”的方向旋转一个特定的角度$2\theta$（其中$\sin\theta = \sqrt{p}$）。因此，经过$O(1/\sqrt{p})$次旋转后，状态向量就会极其贴近“好态”，此时进行测量，得到正确答案的概率将接近100%。

**时间复杂度对比与优势**
经典随机算法的期望成功时间是$O(1/p)$，而量子振幅放大算法将其压缩到了$O(1/\sqrt{p})$。这意味着如果经典算法需要1万次尝试，量子算法只需要100次。这种时间复杂度上的平方根级加速，在$p$极小的情况下（例如在大规模无结构数据库中搜索），展现出极其显著的计算优势。

**量子加速的根本来源**
这种神奇的加速并不依赖于问题内部的结构，而是深深植根于量子力学的**概率幅干涉**现象。在经典概率论中，概率是正数，状态转移是概率的线性组合，信息呈现耗散特征；而在量子力学中，系统演化基于的是复数概率幅。振幅放大算法通过精确的相位反转（类似于光学中的半波损失），使得“坏态”的几率幅在干涉中发生相消干涉（相互抵消），而“好态”的几率幅则发生相长干涉（叠加增强）。正是这种对全局概率幅的相干操控和干涉工程，打破了经典统计抽样的极限，实现了计算速度的二次方飞跃。

## isqQA/quantum_algorithms/87_math_derivation

- task_id: `isqQA/quantum_algorithms/87_math_derivation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `math_derivation`, `algorithm`, `Deutsch-Jozsa算法`
- source: `qa_pipeline`
- dataset_index: `3621`

### Prompt

请详细推导Deutsch-Jozsa算法在n位输入情况下的量子态演化全过程。具体要求：1. 给出经过初始Hadamard门和相位准备后的量子态数学表达；2. 分析在经过量子预言机后，常数函数和平衡函数对量子态相位的影响；3. 推导在最后一组Hadamard门变换后，测量得到全0态的概率公式，并阐释其背后的量子干涉原理；4. 请使用isQ语言编写一个n=3的算法示例代码，验证其针对平衡函数的运行逻辑。

### Reference answer

<think>
推理过程主要分为四个关键阶段：
首先，从系统初始态出发，通过应用Hadamard门推导出输入位的均匀叠加态与辅助位的特定相位态，建立量子并行计算的基础。
其次，引入量子预言机作用。利用辅助位的代数性质，推导相位反冲效应，将函数的输出值精确转化为输入量子位的全局相位因子$(-1)^{f(x)}$。
接着，对输入位施加第二次Hadamard变换。利用矩阵的二进制展开式分析态矢量的演化与量子干涉过程：常数函数因相位一致发生完全的相长干涉，测量全0态的概率为1；平衡函数则因正负相位抵消发生完全的相消干涉，测量全0态的概率为0。
最后，将上述数学逻辑映射为isQ代码，定义一个具体的n=3平衡预言机，通过观测经典寄存器的测量结果是否非零来验证算法逻辑。
</think>

Deutsch-Jozsa算法是量子计算中展示量子并行性和干涉现象的经典算法。对于一个具有n位输入的函数f(x)，该算法只需一次查询即可判断f(x)是常数函数（所有输入映射到同一值）还是平衡函数（一半输入映射到0，另一半映射到1）。以下是严密的数学推导与代码实现。

1. 初始状态与第一步哈达玛变换
假设系统由n个输入量子位和1个辅助量子位构成。初始态设定为：
|ψ₀⟩ = |0⟩ⁿ |1⟩
对前n个量子位和辅助量子位应用哈达玛门（H门），量子态演化为：
|ψ₁⟩ = Hⁿ|0⟩ⁿ ⊗ H|1⟩ 
= (1/√2ⁿ) ∑_{x=0}^{2ⁿ-1} |x⟩ ⊗ (|0⟩ - |1⟩)/√2
这里∑_{x} |x⟩展示了量子态的均匀叠加，实现了计算过程的量子并行性。

2. 量子预言机的作用
预言机Uf的作用机制为：Uf|x⟩|y⟩ = |x⟩|y⊕f(x)⟩。
将|ψ₁⟩输入预言机，由于辅助量子位处于(|0⟩ - |1⟩)/√2的叠加态，根据相位反冲现象，f(x)的值会转化为输入量子位的相位因子：
|ψ₂⟩ = Uf |ψ₁⟩ = (1/√2ⁿ) ∑_{x=0}^{2ⁿ-1} (-1)^{f(x)} |x⟩ ⊗ (|0⟩ - |1⟩)/√2
此时，辅助量子位已与输入比特解耦。对于常数函数，f(x)恒为0或1，(-1)^{f(x)}表现为全局相位或统一的-1相位；对于平衡函数，一半的x对应+1，另一半对应-1。

3. 第二次哈达玛变换与测量概率推导
对前n个量子位再次应用Hⁿ变换。由于Hⁿ|x⟩ = (1/√2ⁿ) ∑_{z=0}^{2ⁿ-1} (-1)^{x·z} |z⟩（其中x·z为比特内积），演化后的最终态为：
|ψ₃⟩ = (1/2ⁿ) ∑_{z=0}^{2ⁿ-1} [ ∑_{x=0}^{2ⁿ-1} (-1)^{f(x) + x·z} ] |z⟩
我们关心的是测量得到|0⟩ⁿ（即z=0）的概率振幅。代入z=0，有x·0 = 0，因此振幅α₀为：
α₀ = (1/2ⁿ) ∑_{x=0}^{2ⁿ-1} (-1)^{f(x)}
测量得到|0⟩ⁿ的概率 P(0) = |α₀|²。
- 若f(x)为常数函数，(-1)^{f(x)}要么全为1，要么全为-1，此时α₀ = ±1，P(0) = 1。
- 若f(x)为平衡函数，一半的(-1)^{f(x)}为1，一半为-1，正负相消，此时α₀ = 0，P(0) = 0。
量子干涉使得平衡函数的非零概率完全转移到了其他基底态上，从而实现了一次测量即可确定函数性质的指数级加速。

4. isQ语言代码实现
以下是使用isQ语言编写的n=3时的Deutsch-Jozsa算法代码示例，其中包含一个平衡函数预言机 f(x) = x₀ ⊕ x₁：

import std;

qbit q[4]; // q[0..2]为3个输入量子位，q[3]为辅助量子位

procedure main() {
    // 初始化辅助位为 |1>
    X(q[3]);

    // 对所有量子位应用Hadamard门
    for i in 0:4 {
        H(q[i]);
    }

    // 构造平衡预言机：f(x) = x₀ ⊕ x₁
    // 通过两个CNOT门实现，将结果异或到辅助位
    CNOT(q[0], q[3]);
    CNOT(q[1], q[3]);

    // 对输入量子位再次应用Hadamard门
    for i in 0:3 {
        H(q[i]);
    }

    // 测量输入寄存器，若结果不为000，则为平衡函数
    for i in 0:3 {
        M(q[i]);
    }
}

## isqTrain/1131

- task_id: `isqTrain/1131`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `interference`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `2071`

### Prompt

Write an isQ program that implements the swap_test pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement a swap (three-CNOT decomposition) test comparing two identical |0⟩ states, with an explicit H-H identity pair to demonstrate gate cancellation.

2. **Qubits**: 3 qubits — q[0] (ancilla, measured), q[1] (state A = |0⟩), q[2] (state B = |0⟩).

3. **State evolution**:
   - Initial: |000⟩
   - H(q[0]): (|000⟩ + |100⟩)/√2
   - ctrl swap (three-CNOT decomposition)(q[0],q[1],q[2]): Since q[1]=q[2]=|0⟩, swapping has no effect → (|000⟩ + |100⟩)/√2
   - H(q[0]): |0⟩↦(|0⟩+|1⟩)/√2, |1⟩↦(|0⟩−|1⟩)/√2 → ½(2|000⟩ + 0|100⟩) = |000⟩
   - H(q[0]) then H(q[0]): H² = I, identity — state remains |000⟩

4. **Measurement**: q[0] is |0⟩ with certainty since the identical states cause complete constructive interference on |0⟩ and destructive on |1⟩, and the H-H pair is a no-op. Result: {|0⟩: 1.0}.

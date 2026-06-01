# ISQ training COT RAG corpus: quantum_algorithms shard 44

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3712

- task_id: `isqTrain/3712`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1606`

### Prompt

Code this in isQ: QAOA (p=1) for the MaxCut problem on a 3-node triangle graph with edges [(0, 1), (1, 2), (0, 2)]. Use parameters gamma=0.500 and beta=1.000. The circuit:
1. Initialize all qubits in superposition
2. Apply cost unitary: for each edge, use CNOT-Rz-CNOT
3. Apply mixer: Rx(2*beta) on each qubit
4. Measure all 3 qubits

### Chain-of-thought reasoning

Let me analyze this QAOA circuit step by step.

1. Goal: Implement QAOA (p=1) for MaxCut on a 3-node triangle graph with gamma=0.5, beta=1.0.

2. Qubits: 3 qubits (q[0], q[1], q[2]), all measured.

3. State evolution:

Initial state: |000>

After H gates on all qubits: |+++> = (1/√8)(|000> + |001> + |010> + |011> + |100> + |101> + |110> + |111>)

Cost unitary U_C(gamma) with gamma=0.5:
- For each edge, we apply CNOT-Rz(2*gamma)-CNOT which implements exp(-i*gamma*Z_i*Z_j)
- Edge (0,1): applies phase based on parity of q[0] and q[1]
- Edge (1,2): applies phase based on parity of q[1] and q[2]
- Edge (0,2): applies phase based on parity of q[0] and q[2]

The cost unitary applies a phase of e^{-i*gamma} when Z_i*Z_j = +1 and e^{i*gamma} when Z_i*Z_j = -1.

For each basis state, we count the number of "unsatisfied" edges (edges where the two endpoints are in the same state).

Let me compute the phase for each basis state:
- |000>: all edges satisfied? No! All vertices in same partition (0). Z_i*Z_j = +1 for all 3 edges. Total phase: e^{-i*3*gamma} = e^{-i*1.5}
- |001>: vertex 2 different. Edge (0,1): same → +1, Edge (1,2): different → -1, Edge (0,2): different → -1. Z sum = +1-1-1 = -1. Phase: e^{i*gamma}
- |010>: vertex 1 different. Edge (0,1): different → -1, Edge (1,2): different → -1, Edge (0,2): same → +1. Z sum = -1-1+1 = -1. Phase: e^{i*gamma}
- |011>: vertices 1,2 different. Edge (0,1): different → -1, Edge (1,2): same → +1, Edge (0,2): different → -1. Z sum = -1+1-1 = -1. Phase: e^{i*gamma}
- |100>: vertex 0 different. Edge (0,1): different → -1, Edge (1,2): same → +1, Edge (0,2): different → -1. Z sum = -1+1-1 = -1. Phase: e^{i*gamma}
- |101>: vertices 0,2 different. Edge (0,1): different → -1, Edge (1,2): different → -1, Edge (0,2): same → +1. Z sum = -1-1+1 = -1. Phase: e^{i*gamma}
- |110>: vertices 0,1 different. Edge (0,1): same → +1, Edge (1,2): different → -1, Edge (0,2): different → -1. Z sum = +1-1-1 = -1. Phase: e^{i*gamma}
- |111>: all vertices same. Z sum = +1+1+1 = +3. Phase: e^{-i*3*gamma} = e^{-i*1.5}

After cost unitary:
|ψ⟩ = (1/√8)(e^{-i*1.5}|000> + e^{i*0.5}|001> + e^{i*0.5}|010> + e^{i*0.5}|011> + e^{i*0.5}|100> + e^{i*0.5}|101> + e^{i*0.5}|110> + e^{-i*1.5}|111>)

Mixer unitary U_M(beta) with beta=1.0, Rx(2*beta) = Rx(2.0) on each qubit:
This rotates each qubit individually around the X-axis.

After the mixer, we get the final state which is a superposition. The probabilities are given in the predicted output.

Let me verify the probabilities:
{|000>: 0.215514, |001>: 0.094829, |010>: 0.094829, |011>: 0.094829

## isqTrain/38

- task_id: `isqTrain/38`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `interference`, `isq_syntax_arrays`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4200`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[5];

procedure main() {
    // Prepare ancilla in |−⟩
    X(q[4]);
    H(q[0]); H(q[1]); H(q[2]); H(q[3]); H(q[4]);
    // BV oracle for s="1111"
    CNOT(q[0], q[4]);
    CNOT(q[1], q[4]);
    CNOT(q[2], q[4]);
    CNOT(q[3], q[4]);
    // Apply H to inputs
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    // Measure inputs only
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Analyze an isQ program implementing the Bernstein-Vazirani (BV) algorithm for the secret string $s = "1111"$.
    *   Format: "## Circuit Analysis", 3-8 lines (up to 15 for complex), strict format, ending with the predicted probability distribution.
    *   State Notation: Dirac notation (|0>, |1>, etc.).
    *   Circuit Details: 5 qubits, 4 input qubits (0-3) prepared in |+>, 1 ancilla (q[4]) prepared in |->. BV oracle (CNOTs), final H gates on inputs, measure inputs.

2.  **Step-by-step Execution (Mental Draft):**
    *   Initial state: $|00000\rangle$
    *   Apply X on q[4]: $|00001\rangle$
    *   Apply H on q[0..4]: $\frac{1}{4} \sum_{x \in \{0,1\}^4} |x\rangle \otimes \frac{|0\rangle - |1\rangle}{\sqrt{2}} = |+\rangle^{\otimes 4} \otimes |-\rangle$
    *   BV Oracle (CNOTs with q[4] as target, controls q[0..3] corresponding to $s="1111"$):
        *   The CNOTs apply phase kickback: $(-1)^{x \cdot s}$ to the input register.
        *   State becomes: $\frac{1}{4} \sum_{x \in \{0,1\}^4} (-1)^{x \cdot 1111} |x\rangle \otimes |-\rangle$
    *   Apply H on q[0..3]:
        *   $H^{\otimes 4} \frac{1}{4} \sum_{x} (-1)^{x \cdot s} |x\rangle = |s\rangle = |1111\rangle$.
    *   Final state: $|1111\rangle \otimes |-\rangle$
    *   Measurement of q[0..3]: Always yields "1111" with 100% probability.

3.  **Draft the text (Concise and precise):**
    *   *Line 1:* Initialize 5 qubits to $|0\rangle^{\otimes 5}$. X on q[4] flips it to $|1\rangle$, yielding $|00001\rangle$.
    *   *Line 2:* Apply H to all qubits, creating the state $|+\rangle^{\otimes 4}|-\rangle = \frac{1}{4}\sum_{x \in \{0,1\}^4} |x\rangle \otimes \frac{|0\rangle - |1\rangle}{\sqrt{2}}$.
    *   *Line 3:* The CNOT oracle (controls q[0]-q[3], target q[4]) encodes the secret string $s=1111$ via phase kickback, transforming the state to $\frac{1}{4}\sum_x (-1)^{x \cdot s}|x\rangle \otimes |-\rangle$.
    *   *Line 4:* Apply H to the input qubits (q[0]-q[3]). This acts as a Hadamard transform on the phase-encoded state.
    *   *Line 5:* The Hadamard transform maps $\frac{1}{4}\sum_x (-1)^{x \cdot s}|x\rangle$ exactly to the computational basis state $|s\rangle = |1111\rangle$.
    *   *Line 6:* The ancilla qubit (q[4]) remains unentangled in the $|-\rangle$ state.
    *   *Line 7:* Measuring only q[0]-q[3] yields the secret string "1111" with certainty.

4.  **Refine to match format rules:**
    *   Must start with "## Circuit Analysis".
    *   End with "Predicted probability distribution: {...}".
    *   Keep it strictly within 3-8 lines of analysis text.

5.  **Final Polish:**
    ## Circuit Analysis
    1. Initial state $|00000\rangle$ is transformed by X(q[4]) and H on all qubits to $|+\rangle^{\otimes 4} \otimes |-\rangle = \frac{1}{4} \sum_{x=0}^{15} |x\rangle \otimes \frac{|0\rangle - |1\rangle}{\sqrt{2}}$.
    2.

### Reference answer

{'predicted_probs': {'15': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/7. Dimension: predict probabilities for reference circuit.'}

## isqTrain/4116

- task_id: `isqTrain/4116`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `4095`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[3];

procedure main() {
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

1.  **Analyze the initial state:**
    *   3 qubits `q[0], q[1], q[2]` initialized to $|0\rangle$.
    *   Initial state: $|000\rangle$.

2.  **Apply X gates:**
    *   `X(q[1])` and `X(q[2])`.
    *   State becomes $|0\rangle \otimes |1\rangle \otimes |1\rangle = |011\rangle$.

3.  **Apply swap (three-CNOT decomposition) network (CNOTs):**
    *   `CNOT(q[0], q[2])`: Control is $q[0]$ ($|0\rangle$), target is $q[2]$. Since $q[0]$ is $|0\rangle$, no change. State remains $|011\rangle$.
    *   `CNOT(q[2], q[0])`: Control is $q[2]$ ($|1\rangle$), target is $q[0]$. Flips $q[0]$ to $|1\rangle$. State becomes $|111\rangle$.
    *   `CNOT(q[0], q[2])`: Control is $q[0]$ ($|1\rangle$), target is $q[2]$. Flips $q[2]$ to $|0\rangle$. State becomes $|101\rangle$.
    *   Wait, let me double check the exact operation.
        *   `CNOT(q[0], q[2])`: $|011\rangle \to |011\rangle$.
        *   `CNOT(q[2], q[0])`: $|011\rangle \to |111\rangle$.
        *   `CNOT(q[0], q[2])`: $|111\rangle \to |101\rangle$.
    *   Current state is $|101\rangle$ (in $q[0], q[1], q[2]$ order).

4.  **Apply Quantum Fourier Transform (QFT) sequence:**
    *   Wait, looking at the gates:
        *   `H(q[2])`
        *   `ctrl Rz(-pi/2, q[2], q[1])`
        *   `H(q[1])`
        *   `ctrl Rz(-pi/4, q[2], q[0])`
        *   `ctrl Rz(-pi/2, q[1], q[0])`
        *   `H(q[0])`
    *   This is the inverse QFT (or QFT†) on 3 qubits!
    *   Standard QFT definition: $H$ on target, then `ctrl Rz(pi/2)` (or similar positive/negative rotations depending on definition), swapping qubits.
    *   Wait, standard QFT:
        *   H(q[0]), CRz(pi/2, q[0], q[1]), CRz(pi/4, q[0], q[2])
        *   H(q[1]), CRz(pi/2, q[1], q[2])
        *   H(q[2])
        *   Swaps.
    *   This looks like `QFT` but backwards and inverted rotation?
        *   Usually, `ctrl Rz(theta, c, t)` applies a phase $e^{-i\theta/2}$ to $|1\rangle_c |1\rangle_t$?
        *   Let's check the sign. `Rz(theta) = diag(e^{-i\theta/2}, e^{i\theta/2})`.
        *   Wait, in the prompt: `ctrl Rz(-pi/2, q[2], q[1])`.
        *   Actually, the exact sequence of gates is a standard structure for QFT.
        *   Let's trace it manually from $|101\rangle$.
        *   $|q_2 q_1 q_0\rangle = |1\rangle_2 |0\rangle_1 |1\rangle_0$.
        *   First gate: `H(q[2])`. Applied to $|1\rangle$. Gives $\frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = |-\rangle$.
        *   Wait, $H|1\rangle = |-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
        *   So state becomes $|-\rangle_2 |0\rangle_1 |1\rangle_0$.
        *   Next: `ctrl Rz(-2.0 * pi / 4.0, q[2], q[1

### Reference answer

Uniform distribution across 8 states

## isqTrain/679

- task_id: `isqTrain/679`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `ancilla_usage`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3848`

### Prompt

Implement a quantum circuit in isQ: implements the half_full_adder pattern but with a different initial state preparation (flip q[[0, 1]] -> q[3]).

### Chain-of-thought reasoning

## Reasoning
Goal: Implement a half/full adder with q[3] initialized to |1⟩ instead of q[0] and q[1].
Four qubits are used (q[0..3]); only q[2] (sum) and q[3] (carry) are measured.
Starting from |0000⟩, X(q[3]) prepares |0001⟩ (q[3]=|1⟩).
CNOT(q[0],q[2]) leaves q[2] as |0⟩ since control q[0]=|0⟩.
CNOT(q[1],q[2]) leaves q[2] as |0⟩ since control q[1]=|0⟩.
Toffoli(q[0],q[1],q[3]) does not flip q[3] since q[0]∧q[1]=0.
Final state is |0001⟩: q[2]=0, q[3]=1.
With q[2] as higher bit and q[3] as lower, bitstring is |01⟩ with probability 1.0.

## isqQA/quantum_algorithms/106_hardware_limitations

- task_id: `isqQA/quantum_algorithms/106_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hardware_limitations`, `algorithm`, `Shor算法中的连分数展开`
- source: `qa_pipeline`
- dataset_index: `1686`

### Prompt

在NISQ（含噪中等规模量子）设备上运行Shor算法时，量子系统的退相干效应和有限的相干时间如何从根本上限制量子相位估计（QPE）中连分数展开的准确性？假设我们尝试分解整数 N=21，真实的相位为 φ = 3/7 ≈ 0.42857，但由于硬件门误差和退相干导致的累积相位漂移，测量得到的近似相位退化为 φ' = 0.45。请详细推导在此硬件噪声下连分数展开的收敛过程，解释为什么这会导致算法提取到错误的阶（周期），并结合代码说明在硬件层面和算法后处理层面可以采取哪些策略来缓解这一局限性。

### Reference answer

在Shor算法中，量子相位估计（QPE）模块输出的相位估计值 φ ≈ s/r 必须通过经典的连分数展开（Continued Fraction Expansion）来提取真实的周期 r。在理想的无噪声量子计算机中，只要计数器寄存器的量子比特数 n 足够大，使得 2^n > N^2，连分数展开就能唯一且精确地收敛到真实的 s/r。然而，当前的NISQ设备存在极其有限的相干时间（T1和T2）和高门错误率。由于Shor算法中模幂运算需要大量的受控双比特门，线路深度往往会超出系统的退相干极限。退相干会导致量子态的相位发生随机扩散（相位阻尼），使得最终测量得到的比特串发生翻转，直接破坏了相位估计的精度。

为了用数学方式说明这种硬件局限性的影响，我们可以推导带有退相干噪声的连分数展开过程。假设真实周期 r=7，对应相位 s/r = 3/7。

<antilatex>
真实理想相位 φ = 3/7 ≈ 0.428571428...
理想情况下的连分数展开：
1. a_0 = ⌊1/0.428571428⌋ = 2，余数 x_1 = 1/0.428571428 - 2 = 0.333333...
2. a_1 = ⌊1/0.333333⌋ = 3，余数 x_2 = 1/0.333333 - 3 = 0
由此得到收敛子 1/(2 + 1/3) = 3/7，算法成功提取周期 7。

受退相干噪声污染的相位 φ' = 0.45：
噪声下的连分数展开：
1. a_0 = ⌊1/0.45⌋ = ⌊2.222⌋ = 2，余数 x_1 = 1/0.45 - 2 = 0.2222...
2. a_1 = ⌊1/0.2222⌋ = ⌊4.5⌋ = 4，余数 x_2 = 1/0.2222 - 4 = 0.5
3. a_2 = ⌊1/0.5⌋ = 2
由此得到收敛子 1/(2 + 1/4) = 4/9。算法错误地提取了周期 9。
<antilatex>

如推导所示，即使相位仅偏差了 0.021，连分数展开在第二级收敛子处就产生了剧烈的分叉，完全偏离了真实的周期。NISQ设备中更深层次的矛盾在于：为了提高相位精度以容忍连分数展开的苛刻条件，我们必须增加计数比特数 n；但增加 n 会指数级增大模幂线路的深度，从而引入更严重的退相干噪声，最终适得其反。

针对这种硬件局限性，在算法后处理层面，我们必须引入容错机制。例如在连分数算法中，不能盲目追求分母最大的收敛子，而是要遍历所有可能的收敛子，并加入“分母必须整除目标结果”的验证步骤，即结合经典试除法来修正噪声带来的偏离。而在硬件和量子线路层面，最有效的缓解策略是采用半经典QPE（Kitaev方法）。这种方法在任意时刻只使用单个辅助量子比特，通过多次顺序执行浅层线路，并在每次测量后根据结果动态调整后续量子门的相位。这种方法将线路深度降至最低，是当前在NISQ硬件对抗退相干效应的标配策略。

以下为使用 isQ 语言编写的抗退相干半经典QPE简化演示程序：

import std;
qbit anc[1];
qbit target[3];

procedure main() {
    // 初始化目标寄存器为叠加态（模拟模幂运算的基态）
    for i in 0:3 {
        H(target[i]);
    }

    // 采用半经典QPE（Kitaev迭代法）以最小化线路深度
    // 这种结构对抗NISQ设备的短相干时间极为有效
    for k in 0:3 {
        H(anc[0]);
        
        // 模拟受控U^(2^(3-k))操作
        // 实际Shor算法中这里是极深的模乘线路，退相干多发生于此
        // NISQ设备中必须通过硬件优化将其深度压缩至最低
        if (k == 1) {
            CNOT(anc[0], target[0]);
        } else {
            CZ(anc[0], target[1]);
        }

        // 逆QFT的相位补偿：根据前几轮经典测量结果施加旋转
        // 利用经典反馈控制代替大规模量子纠缠，极大地节约了量子比特和退相干时间
        if (k == 0) {
            Rz(-1.5707963, anc[0]); // -pi/2 相位补偿
        }

        H(anc[0]);
        int r = M(anc[0]);
        
        // 测量结果传给经典处理单元
        // 经典计算机利用这些带噪数据，执行带有误差容忍逻辑的连分数展开
        if (r == 1) {
            X(target[2]); // 模拟基于测量结果的经典条件反馈
        }
    }
}

## isqTrain/4129

- task_id: `isqTrain/4129`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `4087`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[4];

procedure main() {
    X(q[3]);
    H(q[0]); H(q[1]); H(q[2]);
    ctrl Rz(2.0 * 3.14159265358979 * 0.0 / 8.0 * 1.0, q[0], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 0.0 / 8.0 * 2.0, q[1], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 0.0 / 8.0 * 4.0, q[2], q[3]);
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    H(q[0]);
    ctrl Rz(-3.14159265358979 / 2.0, q[1], q[0]);
    ctrl Rz(-3.14159265358979 / 4.0, q[2], q[0]);
    H(q[1]);
    ctrl Rz(-3.14159265358979 / 2.0, q[2], q[1]);
    H(q[2]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Input: An isQ quantum circuit.
    *   Output: Concise step-by-step reasoning, using Dirac notation, "## Circuit Analysis" format, max 15 lines.
    *   Focus: Final state, measurement probabilities.
    *   Specific Constraint: Output ONLY the analysis, starting with "## Circuit Analysis". Do NOT include code blocks.

2.  **Analyze the Circuit:**
    *   `qbit q[4];` -> Initial state $|0000\rangle$.
    *   `X(q[3]);` -> $|0001\rangle$.
    *   `H(q[0]); H(q[1]); H(q[2]);` -> $(|0\rangle+|1\rangle)^{\otimes 3} \otimes |1\rangle / \sqrt{8} = \frac{1}{2\sqrt{2}} \sum_{x=0}^{7} |x\rangle \otimes |1\rangle$.
    *   `ctrl Rz(2.0 * 3.14159265358979 * 0.0 / 8.0 * 1.0, q[0], q[3]);`
        Wait, the angle is $2\pi \times 0.0 / 8.0 \times 1.0 = 0$.
        Let's check all three CRz gates:
        - `ctrl Rz(2.0 * PI * 0.0 / 8.0 * 1.0, q[0], q[3])` -> Rz(0) -> Identity!
        - `ctrl Rz(2.0 * PI * 0.0 / 8.0 * 2.0, q[1], q[3])` -> Rz(0) -> Identity!
        - `ctrl Rz(2.0 * PI * 0.0 / 8.0 * 4.0, q[2], q[3])` -> Rz(0) -> Identity!
        Okay, so these gates do *nothing*. State remains $\frac{1}{2\sqrt{2}} \sum_{x=0}^7 |x\rangle_1$.
    *   Next, there are three CNOTs:
        - `CNOT(q[0], q[2])`
        - `CNOT(q[2], q[0])`
        - `CNOT(q[0], q[2])`
        This sequence of CNOTs effectively swaps q[0] and q[2].
        Wait, CNOT(c, t) maps $|c, t\rangle \to |c, c \oplus t\rangle$.
        1. CNOT(0, 2): $|c, t\rangle \to |c, c \oplus t\rangle$. Let's check:
           |00> -> |00>
           |01> -> |01>
           |10> -> |11>
           |11> -> |10>
        2. CNOT(2, 0): The new control is the target.
           |00> -> |00>
           |01> -> |11>
           |11> -> |01>
           |10> -> |10>
           Wait, state of (0,2) is now $|c \oplus t, c\rangle$.
        3. CNOT(0, 2): Control is $c \oplus t$, target is $c$.
           Target becomes $(c \oplus t) \oplus c = t$. Control remains $c \oplus t$.
           So $|c, t\rangle \to |c \oplus t, t\rangle$.
           This is a swap (three-CNOT decomposition)!
           So q[0] and q[2] are swapped.
        Let's re-verify. A swap (three-CNOT decomposition) is CNOT(0,2) CNOT(2,0) CNOT(0,2).
        Let's trace |10> (q[0]=1, q[2]=0):
        CNOT(0,2) -> |11>
        CNOT(2,0) -> |01>
        CNOT(0,2) -> |01>
        Yes, it's a swap (three-CNOT decomposition).
        Since the state of (q[0], q[1], q[2]) is $(|0\rangle+|1\rangle)^{\otimes 3}$, applying a swap (three-CNOT decomposition) to two of the qubits leaves the state UNCHANGED.
        So the state remains $\frac{1}{2\sqrt{2}} \sum_{x=0}^7 |x\rangle \otimes |1\rangle

### Reference answer

Dominant output states: |0001> with probability ~0.59 each

## isqTrain/2853

- task_id: `isqTrain/2853`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `85`

### Prompt

这段isQ代码有bug，帮我找出并修复：

```isq
import std;
qbit q[2];
// CNOT sandwich with Hadamard
procedure main() {
    X(q[0]);
    H(q[0]);
    CNOT(q[0], q[1]);
    H(q[0]);
    M(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The second measurement `M(q[0])` measures q[0] twice instead of measuring q[1]. The line should be `M(q[1])`.

2. **Fix**: Change the second `M(q[0])` to `M(q[1])` so both qubits are measured.

3. **State evolution (corrected)**:
   - |00⟩ → X(q[0]) → |10⟩
   - H(q[0]) → (|0⟩−|1⟩)/√2 ⊗ |0⟩ = (|00⟩−|10⟩)/√2
   - CNOT(q[0],q[1]) → (|00⟩−|11⟩)/√2
   - H(q[0]) → (|00⟩+|10⟩−|01⟩+|11⟩)/2

   This yields equal 25% probability for each basis state {|00⟩, |01⟩, |10⟩, |11⟩}, confirming correctness.

## isqTrain/3833

- task_id: `isqTrain/3833`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `2178`

### Prompt

Implement the following in isQ: Demonstrate phase kickback with controlled-Rz(pi/2). Control qubit starts in |+>, target in |1>. After controlled-Rz and Hadamard, measure to observe the kicked-back phase.

### Chain-of-thought reasoning

The user wants a reasoning section for the phase kickback demonstration using controlled-Rz(π/2).

Let me trace through the circuit:
1. Initial state: |00⟩
2. H(q[0]): (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2
3. X(q[1]): (|01⟩ + |11⟩)/√2
4. ctrl Rz(π/2, q[0], q[1]): This applies Rz(π/2) to q[1] when q[0] is |1⟩
   - Rz(π/2) = e^{-iπ/4} diag(1, e^{iπ/2}) = e^{-iπ/4} diag(1, i)
   - When applied to |1⟩: e^{-iπ/4} · i · |1⟩ = e^{-iπ/4} · e^{iπ/2} · |1⟩ = e^{iπ/4} · |1⟩
   - So the state becomes: (|01⟩ + e^{iπ/4}|11⟩)/√2
5. H(q[0]): Apply H to control qubit
   - |0⟩ → (|0⟩ + |1⟩)/√2
   - |1⟩ → (|0⟩ - |1⟩)/√2
   - So: |01⟩ → (|01⟩ + |11⟩)/√2
   - And: |11⟩ → (|01⟩ - |11⟩)/√2
   - Full state: ((|01⟩ + |11⟩) + e^{iπ/4}(|01⟩ - |11⟩))/2
   - = ((1 + e^{iπ/4})|01⟩ + (1 - e^{iπ/4})|11⟩)/2

Now let me compute the probabilities:
- P(|01⟩) = |1 + e^{iπ/4}|² / 4 = |1 + cos(π/4) + i·sin(π/4)|² / 4
  = |1 + (√2/2)(1 + i)|² / 4
  = |1 + √2/2 + i·√2/2|² / 4
  = ((1 + √2/2)² + (√2/2)²) / 4
  = (1 + √2 + 1/2 + 1/2) / 4
  = (2 + √2) / 4
  ≈ (2 + 1.41421) / 4
  ≈ 3.41421 / 4
  ≈ 0.853553

- P(|11⟩) = |1 - e^{iπ/4}|² / 4 = |1 - cos(π/4) - i·sin(π/4)|² / 4
  = |1 - √2/2 - i·√2/2|² / 4
  = ((1 - √2/2)² + (√2/2)²) / 4
  = (1 - √2 + 1/2 + 1/2) / 4
  = (2 - √2) / 4
  ≈ (2 - 1.41421) / 4
  ≈ 0.58579 / 4
  ≈ 0.146447

Great, this matches the predicted output.

The phase kickback: When the target qubit is in an eigenstate of Rz (|1⟩ is an eigenstate with eigenvalue e^{iπ/4} after applying Rz(π/2) to |1⟩), the phase gets "kicked back" to the control qubit. So instead of the target changing, the control picks up a relative phase.

Let me reconsider the Rz gate definition:
Rz(θ) = e^{-iθ/2} [[1, 0], [0, e^{iθ}]]

Applied to |1⟩: e^{-iθ/2} · e^{iθ} |1⟩ = e^{iθ/2} |1⟩

For θ = π/2: e^{iπ/4} |1⟩

So yes, |1⟩ picks up a phase of e^{iπ/4}.

Actually, wait - I need to be careful about how isQ defines Rz. Let me check the convention.

The standard definition is Rz(θ) = e^{-iθZ/2} = [[e^{-iθ/2}, 0

## isqTrain/1203

- task_id: `isqTrain/1203`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3425`

### Prompt

实现以下量子计算任务（使用isQ）：implements the qaoa pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

Let me analyze this QAOA circuit step by step.

**Goal**: Implement QAOA (p=1) for MaxCut on a 2-node graph with explicit identity operations (H-H pair) for gate cancellation awareness.

**Qubits**: 2 qubits (q[0], q[1]), both measured.

**Step-by-step state evolution**:

1. **Initial state**: |00⟩

2. **H(q[0]); H(q[1])** → |++⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)

3. **CNOT(q[0], q[1])** → (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)
   Wait, let me recalculate. CNOT with q[0] as control and q[1] as target:
   |00⟩ → |00⟩
   |01⟩ → |01⟩
   |10⟩ → |11⟩
   |11⟩ → |10⟩
   
   So (1/2)(|00⟩ + |01⟩ + |11⟩ + |10⟩) = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)
   
   Actually this is the same state! The uniform superposition is invariant under CNOT.

4. **Rz(-π/4, q[1])**: This applies a phase of e^(iπ/8) to |0⟩ and e^(-iπ/8) to |1⟩ on q[1].
   
   Rz(θ)|0⟩ = e^(-iθ/2)|0⟩
   Rz(θ)|1⟩ = e^(iθ/2)|1⟩
   
   With θ = -π/4:
   |0⟩ → e^(iπ/8)|0⟩
   |1⟩ → e^(-iπ/8)|1⟩
   
   Applied to q[1]:
   (1/2)(e^(iπ/8)|00⟩ + e^(-iπ/8)|01⟩ + e^(iπ/8)|10⟩ + e^(-iπ/8)|11⟩)
   = (1/2)e^(iπ/8)(|00⟩ + e^(-iπ/4)|01⟩ + |10⟩ + e^(-iπ/4)|11⟩)

5. **CNOT(q[0], q[1])**: 
   |00⟩ → |00⟩
   |01⟩ → |01⟩
   |10⟩ → |11⟩
   |11⟩ → |10⟩
   
   (1/2)e^(iπ/8)(|00⟩ + e^(-iπ/4)|01⟩ + |11⟩ + e^(-iπ/4)|10⟩)
   = (1/2)e^(iπ/8)(|00⟩ + e^(-iπ/4)|01⟩ + e^(-iπ/4)|10⟩ + |11⟩)

6. **Rx(π/4, q[0])** and **Rx(π/4, q[1])**:
   Rx(θ) = cos(θ/2)I - i·sin(θ/2)X
   
   Rx(π/4) = cos(π/8)I - i·sin(π/8)X
   
   This gets complicated. Let me compute the full state after both Rx gates.
   
   Let me denote α = π/8, so Rx(π/4) = cos(α)I - i·sin(α)X
   
   Rx(π/4)|0⟩ = cos(α)|0⟩ - i·sin(α)|1⟩
   Rx(π/4)|1⟩ = cos(α)|1⟩ - i·sin(α)|0⟩

   The state before Rx gates is:
   (1/2)e^(iπ/8)(|00⟩ + e^(-iπ/4)|01⟩ + e^(-iπ/4)|10⟩ + |11⟩)
   
   Let me drop the global phase e^(iπ/8)/2 and work with:
   |ψ⟩ = |00⟩ + e^(-iπ/4)|01⟩ + e^(-iπ/4)|10⟩ + |11⟩

   After Rx(π/4)⊗Rx(π/4):
   
   For each basis state |ab⟩, we get:
   Rx|a⟩ ⊗ Rx|b⟩

   Let c = cos(α), s = sin(α), where α = π/8.
   
   Rx|0⟩ = c|0⟩ - is|1⟩
   Rx|1⟩ = -is|0⟩ + c

## isqTrain/1272

- task_id: `isqTrain/1272`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4768`

### Prompt

用isQ实现implements a variant of the simon_algorithm pattern using out[3] -> out[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement Simon's algorithm with period s = 100 (binary), where the oracle satisfies f(x) = f(x ⊕ 100), and extract period information via measurement.

2. **Qubits**: 7 total — input register q[3] (measured) and output register out[4] (ancillary). Only q[0], q[1], q[2] are measured.

3. **State evolution**:
   - Initial: |000⟩|0000⟩
   - After H⊗3 on input: (1/√8)Σx∈{0,1}³ |x⟩|0000⟩ = (1/√8)(|0⟩+|1⟩)⊗3|0000⟩
   - After oracle f: (1/√8)Σx |x⟩|f(x)⟩ where f(x)=[x₀,x₁,0] ignores x₂, creating pairwise collisions f(x)=f(x⊕100)
   - After second H⊗3: Interference cancels odd-parity terms; state collapses to equal superposition over |y⟩ where y·100=0 mod 2
   - Valid y satisfy y₂=0: |000⟩, |010⟩, |100⟩, |110⟩

4. **Expected probabilities**: Each valid y has probability 0.25, yielding {|000⟩: 0.25, |010⟩: 0.25, |100⟩: 0.25, |110⟩: 0.25}.

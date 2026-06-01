# ISQ training COT RAG corpus: quantum_algorithms shard 196

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3505

- task_id: `isqTrain/3505`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `phase_manipulation`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `1341`

### Prompt

Predict the output probabilities of the following quantum circuit:

```
import std;

qbit q[2];
qbit anc[1];

procedure main() {
    X(anc[0]);
    H(anc[0]);

    H(q[0]); H(q[1]);

    H(q[0]); H(q[1]);

    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis

1. **Operations applied:**
   - X(anc[0]): Flips ancilla to |1>
   - H(anc[0]): Puts ancilla in |+> state
   - H(q[0]), H(q[1]): Put both qubits in |+>
   - H(q[0]), H(q[1]): Apply H again to both qubits

2. **State evolution:**
   - Initial: |000> (ordering: q[0], q[1], anc[0])
   - After X(anc[0]): |001>
   - After H(anc[0]): (|000> + |001>)/√2
   - After H(q[0])H(q[1]): (|000> + |001> + |010> + |011> + |100> + |101> + |110> + |111>)/(2√2)
   - After H(q[0])H(q[1]) again: (|000> + |001>)/√2

3. **Final state before measurement:** (|000> + |001>)/√2
   - H is self-inverse (H·H = I), so applying H twice returns q[0] and q[1] to |0>

4. **Predicted distribution:**
   - Only q[0] and q[1] are measured; anc[0] is not measured
   - Both measured qubits are in |0> with certainty

**Probability distribution:**
- |00>: 1.0
- All other states: 0

### Reference answer

{'predicted_probs': {'00': 1.0}, 'explanation': 'The output is |00> with probability 1.0'}

## isqTrain/3025

- task_id: `isqTrain/3025`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3947`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[4];
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    X(q[1]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict measurement probabilities for a given isQ program.
    *   Format: "## Circuit Analysis" section, step-by-step reasoning using Dirac notation, ending with predicted probability distribution (JSON array format implied by prompt "Return a JSON array", but text output for analysis). Wait, the prompt says "Generate a circuit analysis section that explains... End with the predicted probability distribution". Wait, standard output format expects `## Circuit Analysis` at the start. The prompt actually says "Return a JSON array" in the quoted text, but I must follow the "Rules" at the bottom: Output ONLY the analysis, starting with "## Circuit Analysis", ending with the predicted probability distribution. Actually, looking at the `--probs output` note, standard probability tasks just want the JSON array or text including it. Let's provide the analysis and then maybe the JSON format for the final probabilities as requested by the initial text but structure it per the Rules. Actually, the rule says "End with the predicted probability distribution".
    *   Circuit:
        *   4 qubits: q[0], q[1], q[2], q[3] (all initially |0>)
        *   H(q[0]) -> |0> becomes |+>
        *   CNOT(q[0], q[1]) -> entangled. |00> + |11> -> (|00> + |11>)|00> = 1/2 (|0000> + |1100>)
        *   CNOT(q[1], q[2]) -> 1/2 (|0000> + |1110>)
        *   CNOT(q[2], q[3]) -> 1/2 (|0000> + |1111>)
        *   X(q[1]) -> flips q[1].
        *   State before measurement: 1/2 (|0010> + |1101>) -> Wait, let me re-check the bit ordering.
            *   Initial state: |0000> (q[0]q[1]q[2]q[3])
            *   H(q[0]) -> (|0> + |1>)|000> / sqrt(2)
            *   CNOT(q[0], q[1]) -> (|00> + |11>)|00> / sqrt(2)
            *   CNOT(q[1], q[2]) -> (|000> + |111>)|0> / sqrt(2)
            *   CNOT(q[2], q[3]) -> (|0000> + |1111>) / sqrt(2)
            *   X(q[1]) -> flips the second bit from left (q[1]).
                *   |0000> -> |0100>
                *   |1111> -> |1011>
            *   Final state: (|0100> + |1011>) / sqrt(2).
    *   Measurement order: q[0], q[1], q[2], q[3]. The bitstrings in `--probs` standardly map earlier measured qubits to higher bits (or simply standard string representation q[0]q[1]q[2]q[3]). "indexed by measurement bitstring (earlier measured qubit = higher bit)" means q[0] is MSB, q[3] is LSB.
        *   State |0100> means q[0]=0, q[1]=1, q[2]=0, q[3]=0. String: '0100'.
        *   State |1011> means q[0]=1, q[1]=0, q[2]=1, q[3]=1. String: '1011'.
        *   Wait, is it |0100> or what? Let's trace:
        *   |q3 q2 q1 q0> or |q0 q1 q2 q3>?
        *   Usually Dirac |abcd> means a=q0, b=q1, c=q2, d=q3. Let's stick to |q0 q1 q2 q3>.
        *   X(q[1]) on |0000> -> |0100>.
        *   X(q[1]) on |1111> -> |1011>.
        *   So the states are |0100> and |1011>.
        *   Probabilities: P(0100) = 0.5, P(1011) = 0.5.

2.  **Drafting the Analysis (3-8 lines):**
    *   Initial state |0000>.
    *   Apply H(q[0]): creates superposition 1/√2 (|0000> + |1000>).
    *   Apply CNOT(q

### Reference answer

{'predicted_probs': {'0100': 0.5, '1011': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3001

- task_id: `isqTrain/3001`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1165`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    T(q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The objective is to analyze an isQ quantum program, trace the quantum state step-by-step using Dirac notation, and predict the measurement probability distribution.

2.  **Analyze the isQ Code**:
    *   `qbit q[2];`: Initialize 2 qubits in $|00\rangle$ state.
    *   `H(q[0]);`: Apply Hadamard gate to $q_0$. State becomes $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
    *   `CNOT(q[0], q[1]);`: Apply CNOT with $q_0$ as control, $q_1$ as target. State becomes $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$ (Bell state).
    *   `T(q[1]);`: Apply T gate to $q_1$. State becomes $\frac{1}{\sqrt{2}}(|00\rangle + e^{i\pi/4}|11\rangle)$.
    *   `M(q[0]); M(q[1]);`: Measure both qubits.

3.  **Step-by-step Quantum State Evolution**:
    *   Initial: $|00\rangle$
    *   After $H(q_0)$: $\frac{1}{\sqrt{2}}|00\rangle + \frac{1}{\sqrt{2}}|10\rangle$
    *   After $CNOT(q_0, q_1)$: $\frac{1}{\sqrt{2}}|00\rangle + \frac{1}{\sqrt{2}}|11\rangle$
    *   After $T(q_1)$: $\frac{1}{\sqrt{2}}|00\rangle + \frac{1}{\sqrt{2}}e^{i\pi/4}|11\rangle$
    *   Note: The T gate applies a phase $e^{i\pi/4}$ to $|1\rangle$. Since $q_1$ is in $|0\rangle$ when $q_0$ is $|0\rangle$, and $|1\rangle$ when $q_1$ is $|1\rangle$, the T gate only adds a global phase if we look at it incorrectly, but wait: T(q[1]) applies phase to $q_1$. If the state is $\frac{1}{\sqrt{2}}(|0\rangle_0|0\rangle_1 + |1\rangle_0|1\rangle_1)$, applying $T$ to $q_1$ yields $\frac{1}{\sqrt{2}}(|0\rangle_0 T|0\rangle_1 + |1\rangle_0 T|1\rangle_1) = \frac{1}{\sqrt{2}}(|0\rangle_0|0\rangle_1 + |1\rangle_0 e^{i\pi/4}|1\rangle_1)$. This is an overall relative phase.

4.  **Calculate Probabilities**:
    *   Probability of $|00\rangle$: $|1/\sqrt{2}|^2 = 0.5$
    *   Probability of $|11\rangle$: $|e^{i\pi/4}/\sqrt{2}|^2 = 0.5$
    *   Probabilities of $|01\rangle, |10\rangle$: $0$
    *   Since $M(q_0)$ and $M(q_1)$ are measured, the bitstring is just $q_0 q_1$. Expected array: `[0.5, 0.0, 0.0, 0.5]` (corresponding to 00, 01, 10, 11).

5.  **Format the Output**:
    *   Circuit Analysis section
    *   Steps listed clearly (3-8 lines).
    *   Probabilities as requested. Wait, the prompt says "End with the predicted probability distribution", and the example predicted output says "Expected measurement probabilities: {'00': 0.499..., '11': 0.5}", but standard JSON array format is `[0.5, 0.0, 0.0, 0.5]`. I will provide both or stick to the required JSON array format as standard in these tasks. The prompt says "Return the probability vector as a JSON array of floats, one entry per basis state." I will append the JSON array at the end.

    Drafting response:
    ## Circuit Analysis
    1. **Initial State**: The system starts in the 2-qubit basis state |00>.
    2. **H(q[0])**: A Hadamard gate is applied to the

### Reference answer

{'predicted_probs': {'00': 0.4999999999999999, '11': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/754

- task_id: `isqTrain/754`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4598`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[3];

procedure main() {
    // Encode a = 2 (binary 10)
    X(q[1]);
    // Add constant 1: flip the LSB
    X(q[0]);
    // Now register = 3 (binary 11)
    // Overflow detection: set flag if both bits are 1 (value >= 3)
    Toffoli(q[0], q[1], q[2]);
    // Modular correction: subtract 3 by flipping both bits
    CNOT(q[2], q[0]);
    CNOT(q[2], q[1]);
    // Measure the 2-bit result: should be 0
    M(q[0]);
    M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Role: Quantum computing expert.
    *   Task: Predict the probability distribution of measurement outcomes for an isQ program.
    *   Output format: "## Circuit Analysis" followed by step-by-step reasoning (concise, 3-15 lines), ending with the probability distribution. No code blocks.
    *   Input isQ code: Initializes `q[0..2]` to `|000>`. Applies `X(q[1])`, `X(q[0])`, `Toffoli(q[0], q[1], q[2])`, `CNOT(q[2], q[0])`, `CNOT(q[2], q[1])`. Measures `q[0]` and `q[1]`.

2.  **Step-by-Step Execution:**
    *   Initial state: `|q[2], q[1], q[0]>` = `|000>`.
    *   `X(q[1])`: Flips `q[1]`. State becomes `|010>`.
    *   `X(q[0])`: Flips `q[0]`. State becomes `|011>`. (Representing 3 in binary).
    *   `Toffoli(q[0], q[1], q[2])`: Controls on `q[0]` and `q[1]`. Both are 1. Flips `q[2]`. State becomes `|111>`.
    *   `CNOT(q[2], q[0])`: Control `q[2]`, target `q[0]`. `q[2]` is 1, so `q[0]` flips to 0. State becomes `|110>`.
    *   `CNOT(q[2], q[1])`: Control `q[2]`, target `q[1]`. `q[2]` is 1, so `q[1]` flips to 0. State becomes `|100>`.
    *   Wait, let's double check the bitstring convention. If `|q[2], q[1], q[0]>` is the order, `q[2]` is the most significant bit (2^2), `q[1]` is 2^1, `q[0]` is 2^0.
    *   Let's trace carefully:
        *   `q[2]` is the overflow flag. `q[1]` and `q[0]` are the value bits.
        *   Start: `q[2]=0, q[1]=0, q[0]=0`
        *   `X(q[1])`: `q[1]=1`. Value = 2.
        *   `X(q[0])`: `q[0]=1`. Value = 3.
        *   `Toffoli(q[0], q[1], q[2])`: `q[2]` becomes 1 because `q[1]=1` and `q[0]=1`.
        *   `CNOT(q[2], q[0])`: `q[2]=1`, so `q[0]` flips from 1 to 0.
        *   `CNOT(q[2], q[1])`: `q[2]=1`, so `q[1]` flips from 1 to 0.
    *   Final state: `q[2]=1`, `q[1]=0`, `q[0]=0`.
    *   Measurements are on `q[0]` and `q[1]`. Both are 0.
    *   Output bitstring order for --probs: "array indexed by measurement bitstring (earlier measured qubit = higher bit)". So `M(q[0])` is the higher bit, `M(q[1])` is the lower bit. Wait, let me read carefully: "earlier measured qubit = higher bit".
    *   `M(q[0])` is measured first. `q[0]` is 0.
    *   `M(q[1])` is measured second. `q[1]` is 0.
    *   Bitstring is `00`.

3.  **Draft the Explanation:**
    *   Start with initial state |000> (formatting as |q[2]q[1]q[0]>).
    *   Apply X(q[1]) and X(q[0]) -> |011>.
    *   Apply Toffoli(q[0], q[1], q[2]) -> |111>.
    *   Apply CNOT(q[2], q[0]) -> |110>.
    *   Apply CNOT(q[2], q

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'Parametric variant of isqEval/280. Dimension: predict probabilities for reference circuit.'}

## isqExpand/algo/92

- task_id: `isqExpand/algo/92`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `grover`, `amplitude_amplification`, `oracle`, `interference`
- source: `isq_expansion`
- dataset_index: `568`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[3];

procedure oracle_proc() {
    X(q[1]);
    ctrl ctrl Z(q[0], q[1], q[2]);
    X(q[1]);
}

procedure diffusion() {
    H(q[0]); H(q[1]); H(q[2]);
    X(q[0]); X(q[1]); X(q[2]);
    ctrl ctrl Z(q[0], q[1], q[2]);
    X(q[0]); X(q[1]); X(q[2]);
    H(q[0]); H(q[1]); H(q[2]);
}

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    oracle_proc();
    diffusion();
    oracle_proc();
    diffusion();
    oracle_proc();
    diffusion();
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## 电路分析

### 电路结构
- 3个量子位，全部初始化为|0>
- H门创建均匀叠加
- Oracle标记|101>: X(q[1]); CCZ; X(q[1]);
- 标准3比特扩散算子
- 重复3次oracle+diffusion

### 概率计算
N=8, M=1: theta = arcsin(1/sqrt(8)) ≈ 0.36137

3次迭代后：
P(|101>) = sin^2(7*theta) = sin^2(7*0.36137) = sin^2(2.5296)
计算 sin(2.5296) ≈ 0.5745
P(|101>) ≈ 0.33008
P(每个非目标态) = (1 - 0.33008)/7 ≈ 0.09570

### 过度旋转分析
- 1次迭代: sin^2(3*theta) = 0.78125
- 2次迭代: sin^2(5*theta) = 0.94531
- 3次迭代: sin^2(7*theta) = 0.33008 ← 严重下降！

3次迭代远超最优，旋转角7*theta ≈ 2.53 > pi/2。

### Reference answer

{'predicted_probs': {'000': 0.09570312, '001': 0.09570312, '010': 0.09570312, '011': 0.09570312, '100': 0.09570312, '101': 0.33007812, '110': 0.09570312, '111': 0.09570312}, 'explanation': "This circuit applies 3 Grover iterations for |101> on 3 qubits (N=8, M=1). The optimal number of iterations is 1 (P=0.78125) or 2 (P=0.9453125). With 3 iterations, the algorithm overshoots past the optimal angle: P(|101>) = sin^2(7*theta) where theta=arcsin(1/sqrt(8)), giving P(|101>) = 0.33007812 and P(each other) = 0.09570312. The success probability has decreased dramatically compared to 1 or 2 iterations, demonstrating the overshooting phenomenon in Grover's algorithm."}

## isqTrain/181

- task_id: `isqTrain/181`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_deriving_gate`, `superposition`
- source: `isq_train_cot`
- dataset_index: `954`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[3];

procedure main() {
    // Uniform superposition = QFT(|000>)
    H(q[0]); H(q[1]); H(q[2]);

    // IQFT: process from q[0] to q[2] (no SWAP needed in isQ's qubit ordering)
    H(q[0]);
    ctrl Rz(-pi/2.0, q[0], q[1]);
    H(q[1]);
    ctrl Rz(-pi/4.0, q[0], q[2]);
    ctrl Rz(-pi/2.0, q[1], q[2]);
    H(q[2]);

    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the isQ code:**
    *   Three qubits: `q[0]`, `q[1]`, `q[2]`.
    *   Initial state: $|000\rangle$.
    *   Apply $H$ to all three qubits: `H(q[0]); H(q[1]); H(q[2]);`. This creates a uniform superposition over all 8 basis states: $\frac{1}{2\sqrt{2}} \sum_{x=0}^{7} |x\rangle$. Note that applying $H^{\otimes 3}$ is mathematically equivalent to applying the Quantum Fourier Transform (QFT) on $|000\rangle$ up to a specific bit-ordering convention, but usually QFT involves swaps. As the comment suggests, this is "Uniform superposition = QFT(|000>)".
    *   Apply Inverse QFT (IQFT):
        *   `H(q[0]);`
        *   `ctrl Rz(-pi/2.0, q[0], q[1]);` (Controlled $R_z(-\pi/2)$ with $q[0]$ control, $q[1]$ target. Wait, $R_z(\theta) = e^{-i\theta/2}|0\rangle\langle0| + e^{i\theta/2}|1\rangle\langle1|$. Often IQFT uses $R_k = R_z(\pi/2^{k-1})$ or phase shifts. Let's trace it carefully).
        *   `H(q[1]);`
        *   `ctrl Rz(-pi/4.0, q[0], q[2]);`
        *   `ctrl Rz(-pi/2.0, q[1], q[2]);`
        *   `H(q[2]);`
    *   This sequence of gates is exactly the standard Inverse Quantum Fourier Transform (IQFT) circuit (with $q[0]$ as the most significant bit, typically, processed first without swap gates at the end, matching the comment).
    *   Since $H^{\otimes 3} = \text{QFT}$ (up to bit ordering, specifically if we don't do swaps at the end of QFT, applying the exact inverse without swaps will undo it).
    *   QFT followed by IQFT yields the initial state $|000\rangle$.
    *   Wait, is `ctrl Rz(-pi/2.0, q[0], q[1])` applied *before* `H(q[1])`? Yes.
    *   Standard IQFT: process qubit 0 (H, then controlled rotations to 1, 2). Process qubit 1 (H, controlled rotation to 2). Process qubit 2 (H). Swap qubits. Since there are no swap gates, and standard QFT also doesn't use swap gates but just defines the bits, applying the inverse sequence exactly undoes the initial state.

2.  **Verify the math:**
    *   Start: $|\psi_0\rangle = |000\rangle$
    *   After $H^{\otimes 3}$: $|\psi_1\rangle = \frac{1}{\sqrt{8}} \sum_{y=0}^7 |y\rangle$. This state can be written as $\frac{1}{2\sqrt{2}} (|0\rangle+|1\rangle)(|0\rangle+|1\rangle)(|0\rangle+|1\rangle)$.
    *   Let's check the IQFT definition.
        *   QFT maps $\sum_{x=0}^{N-1} f(x) |x\rangle \to \sum_{k=0}^{N-1} \tilde{f}(k) |k\rangle$.
        *   In the case of $f(x)=1$ (uniform superposition), $\tilde{f}(k) = \delta_{k,0}$.
        *   Therefore, IQFT(uniform superposition) = $|000\rangle$.
    *   Does the provided gate sequence implement IQFT accurately?
        *   `H(q[0])`: applies H to q[0].
        *   `ctrl Rz(-pi/2, q[0], q[1])`: this is a controlled phase gate. Wait, QFT typically uses controlled-$R_k$ where $R_k = \text{diag}(1, e^{2\pi i/2^k})$. Controlled $R_z(\theta)$ usually introduces phase $e^{i\theta/2}$ on the $|11\rangle$ state (or $e^{i\theta}$ depending on the exact definition).
        *   Let's look at

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'Parametric variant of isqHumanEval/62. Dimension: predict probabilities for reference circuit.'}

## isqQA/quantum_algorithms/94_comparison

- task_id: `isqQA/quantum_algorithms/94_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `comparison`, `algorithm`, `Grover搜索算法基本原理`
- source: `qa_pipeline`
- dataset_index: `90`

### Prompt

请对比分析Grover搜索算法与经典穷举搜索以及Shor算法在加速特性、适用场景和优缺点方面的差异，并结合数学原理说明为何Grover算法在无结构数据库搜索中能达到极限。最后，请使用isQ语言编写代码，演示一个2量子比特的Grover算法，其中目标态为|11〉。

### Reference answer

<thought>
首先，对比分析Grover算法、经典搜索与Shor算法的差异。经典无结构搜索的时间复杂度为O(N)，而Grover算法通过量子叠加和振幅放大，将复杂度降至O(√N)，在理论上已被证明是最优的。Shor算法则针对质因数分解等特定问题，利用量子傅里叶变换实现指数级加速O(log N)。Grover的优点是普适性强，只要能构建Oracle即可应用；缺点是对于大数据集，√N的加速在实际物理实现中可能仍显不足。Shor优点是加速惊人，但适用范围极窄。

其次，构建2量子比特的isQ代码。N=4，需要搜索的次数为 R = ⌊π/(4 * arcsin(1/√4))⌋ = 1次。
1. 初始化2个量子比特，应用H门进入均匀叠加态。
2. 构造相位反转Oracle。对于目标态|11〉，直接使用受控Z门（CZ）即可实现|11〉的相位翻转。
3. 构造扩散算子。公式为 2|s><s| - I，对应量子线路为：对所有量子比特应用H门 -> 应用X门 -> 应用CZ门 -> 应用X门 -> 应用H门。
4. 测量。

代码结构如下：
import std;
qbit q[2];
procedure main() {
    // 初始化
    H(q[0]);
    H(q[1]);
    // Oracle 目标 |11>
    CZ(q[0], q[1]);
    // Diffusion 扩散算子
    H(q[0]); H(q[1]);
    X(q[0]); X(q[1]);
    CZ(q[0], q[1]);
    X(q[0]); X(q[1]);
    H(q[0]); H(q[1]);
    // 测量
    M(q[0]); M(q[1]);
}
</thought>
Grover搜索算法是量子计算中最著名的算法之一，它主要在无结构数据库的搜索问题上展现了强大的能力。

**1. Grover算法与经典穷举搜索的对比**
在经典的无结构数据库中寻找一个特定的目标项，最坏情况下需要遍历整个数据库，时间复杂度为O(N)。而Grover算法利用了量子态的叠加特性和概率振幅放大机制，将搜索复杂度降低到了O(√N)。
* **优点**：Grover算法提供了一种通用的二次加速。虽然看起来是多项式级别的加速，但当N趋于无穷大时，√N的加速在计算复杂度上的提升是巨大的。此外，它的适用性非常广，任何可以通过构造Oracle（黑盒函数）来识别目标的问题，都可以嵌入Grover算法框架中，例如寻找密码学哈希函数的碰撞或解决NP完全问题（如SAT问题）。
* **缺点**：与具有数据结构的经典搜索相比（例如二分查找复杂度为O(log N)），Grover算法只有在数据完全无结构时才具有绝对优势。另外，O(√N)的加速意味着对于需要穷举2^256的AES-256密钥，Grover算法将其降至2^128，虽然复杂度大幅下降，但在物理层面实现如此深度的量子线路仍然极具挑战性。

**2. Grover算法与Shor算法的对比**
Shor算法是另一种极其重要的量子算法，主要用于大整数分解和求解离散对数问题。
* **加速特性**：Shor算法针对特定数学结构（周期性）实现了指数级加速，将质因数分解的复杂度从经典的亚指数级O(exp((64/9)^(1/3)(log N)^(1/3))) 降至多项式级 O((log N)^3)。相比之下，Grover算法只提供平方级加速。
* **适用场景**：Shor算法的适用场景非常特殊和狭窄，依赖于问题的隐藏周期性；而Grover算法不依赖特定的数学结构，是一种纯粹的“通用搜索暴力破解法”。
* **密码学影响**：Shor算法直接威胁了当前广泛使用的非对称加密算法（如RSA、ECC），迫使我们转向后量子密码学（PQC）；而Grover算法主要威胁对称加密算法，但对抗它的方式相对简单，只需将现有的对称密钥长度翻倍（如从AES-128升级到AES-256）即可维持等效的安全强度。

**数学极限证明简述**：Grover算法的迭代次数是由希尔伯特空间中初态向量与目标态向量的夹角决定的。每次Oracle和扩散算子的作用相当于将状态向量朝着目标态旋转两倍的角度。经过大约π/(4*arcsin(1/√N)) ≈ (π/4)√N 次旋转后，测量得到目标态的概率振幅达到最大。这个O(√N)的查询复杂度已被Bennett等人在1997年证明是无结构搜索问题的量子查询下界，这意味着没有任何其他量子算法能在搜索这类无结构问题时比Grover算法更快。

**isQ代码实现（2量子比特Grover搜索目标态|11〉）：**
在2量子比特情况下（N=4），只需一次Grover迭代即可以100%的概率测量到目标态。

```isq
import std;

qbit q[2];

procedure main() {
    // 1. 初始化：制备均匀叠加态
    H(q[0]);
    H(q[1]);

    // 2. Oracle：翻转目标态 |11> 的相位
    // 由于受控Z门(CZ)的作用恰好是在 |11> 态加上负号，因此可以直接使用
    CZ(q[0], q[1]);

    // 3. 扩散算子：
    // 在Hadamard基下翻转 |00> 的相位，等价于对所有基态相位取反后保留 |00> 正相位
    H(q[0]);
    H(q[1]);
    
    X(q[0]);
    X(q[1]);
    
    // 使用CZ门翻转 |11> 的相位
    CZ(q[0], q[1]);
    
    X(q[0]);
    X(q[1]);
    
    H(q[0]);
    H(q[1]);

    // 4. 测量
    // 此时量子态将坍缩为 |11>
    M(q[0]);
    M(q[1]);
}
```

## isqTrain/3657

- task_id: `isqTrain/3657`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `5685`

### Prompt

用isQ实现3-bit quantum phase estimation for phase angle 0 (in multiples of 2π/8). Use 3 precision qubits, controlled-Rz rotations, and a 3-qubit inverse QFT. Measure all 4 qubits (3 precision + 1 eigenstate).

### Chain-of-thought reasoning

Let me analyze this quantum phase estimation circuit for phase angle 0 (in multiples of 2π/8).

1. **Goal**: Implement 3-bit QPE for phase θ = 0 (so φ = 0·2π/8 = 0), estimating the phase of an eigenstate of Rz.

2. **Qubits**: 4 qubits total - q[0], q[1], q[2] are precision qubits, q[3] is the eigenstate qubit. All 4 are measured.

3. **State evolution**:
   - Initial state: |0000⟩
   - After X(q[3]): |0001⟩
   - After H on q[0], q[1], q[2]: (|0⟩+|1⟩)⊗3 ⊗ |1⟩/2√2 = (|000⟩+|001⟩+|010⟩+|011⟩+|100⟩+|101⟩+|110⟩+|111⟩)|1⟩/2√2

   - Controlled-Rz operations: Since phase is 0, all Rz rotations are Rz(0) = I, so nothing happens.

   - Actually wait, let me check: Rz(0·2π/8 · 2^k) = Rz(0) = I for all k. So the controlled rotations do nothing.

   - The state remains (|000⟩+|001⟩+|010⟩+|011⟩+|100⟩+|101⟩+|110⟩+|111⟩)|1⟩/2√2

   - Now inverse QFT on q[0], q[1], q[2]:
     - Swap q[0] ↔ q[2]: still the same uniform superposition
     - H(q[0]), H(q[1]), H(q[2]): Since the state is uniform superposition, QFT|uniform⟩ should give |000⟩

   Wait, let me think more carefully. The QFT of |k⟩ gives a uniform superposition with specific phases. The inverse QFT of a uniform superposition should give |000⟩ (all zeros).

   Actually, let me reconsider. The state after Hadamards on precision qubits is:
   |ψ⟩ = (1/2√2) Σ_{k=0}^{7} |k⟩|1⟩

   The controlled-U operations should add phase e^(2πi·θ·k) to each |k⟩ where θ is the phase. Since θ=0, no phases are added.

   Then iQFT(|Σ|k⟩) = |000⟩ (up to normalization, since QFT|000⟩ = uniform superposition).

   So the final state should be |0001⟩ with certainty, giving probability 1 for |0001⟩.

   But the predicted output given are {|0001>: 0.590097, |0011>: 0.263456, |0101>: 0.140873, |0111>: 0.005574}. These don't sum to 1 exactly... let me check: 0.590097 + 0.263456 + 0.140873 + 0.005574 = 1.0. OK they do.

   Hmm, but these probabilities show the eigenstate qubit (q[3]) is always 1, and the precision qubits have some distribution that's NOT |000⟩. This is strange for phase 0.

   Wait, let me re-examine the Rz gate. Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]. This is NOT a Pauli-Z rotation in the computational basis. The eigenstates of Rz(θ) are |0⟩ and |1⟩ with eigenvalues e^(-iθ/2) and e^(iθ/2) respectively.

   So for phase estimation of Rz, when we prepare |1⟩ as eigenstate, the eigenvalue is e^(iθ/2).

   For θ = 0, the eigenvalue is e^(0) = 1, so phase φ = 0. This should give |000⟩ on precision qubits.

   But wait - there's an issue with controlled-Rz. A controlled-Rz gate applies Rz only when the control is |1⟩. But Rz is a diagonal gate, so controlled-Rz should work fine.

   Let me re-examine. With Rz(θ)|1⟩ = e^(iθ/2)|1⟩.

   The controlled-Rz(θ, control, target) applies Rz(θ) to target when control is |1⟩. So:
   |0⟩_c|1⟩_t →

## isqTrain/2928

- task_id: `isqTrain/2928`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1370`

### Prompt

这段isQ代码有bug，帮我找出并修复：

```isq
import std;
qbit q[2];
// Controlled Rz(3*pi/8)
procedure main() {
    H(q[0]);
    X(q[1]);
    ctrl Rz(1.178097, q[0], q[1]);
    H(q[0]);
    M(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Bug Analysis

**1. Bug:** The second measurement on line 12 measures `q[0]` again (`M(q[0])`) instead of measuring `q[1]` (`M(q[1])`). This means qubit 1 is never measured, and qubit 0 is measured redundantly.

**2. Fix:** Change the second `M(q[0])` to `M(q[1])` so both qubits are measured once.

**3. State evolution (corrected circuit):**
- **Init:** |00⟩
- **H(q[0]):** (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |10⟩)/√2
- **X(q[1]):** (|01⟩ + |11⟩)/√2
- **ctrl Rz(3π/8, q[0], q[1]):

## isqQA/quantum_algorithms/94_step_by_step

- task_id: `isqQA/quantum_algorithms/94_step_by_step`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `step_by_step`, `algorithm`, `Grover搜索算法基本原理`
- source: `qa_pipeline`
- dataset_index: `2723`

### Prompt

我正在学习Grover搜索算法的基本原理，虽然知道它是用来加速无结构数据库搜索的，但对量子线路中振幅放大的具体数学追踪感到困惑。您能否以搜索2个量子比特（N=4）为例，一步步教我如何手动追踪和计算从初始态、经过Oracle作用、再到扩散算子作用后的量子态概率幅变化？最好能附带isQ语言的代码实现。

### Reference answer

<think>
针对N=4的Grover算法，只需一次迭代即可完成搜索，推理过程应按照量子态演化的三个核心阶段展开：

首先，明确初始态经过Hadamard门后的状态。2个量子比特处于均匀叠加态，计算得出四个基态的概率振幅均为0.5。

其次，追踪Oracle的相位反转作用。假设目标态为|11⟩，Oracle会识别该态并将其相位旋转180度，使得|11⟩的振幅变为-0.5，而其他非目标态振幅保持不变。

第三，推导扩散算子的振幅放大效应。扩散算子本质上是“关于平均值反转”的操作。先计算当前四个态的平均振幅（为0.25），然后将各个态的振幅减去自身与平均值的差值。计算可得，非目标态的新振幅变为0，而目标态|11⟩的振幅被放大至1，概率达到100%。

最后，基于上述数学推导逻辑，规划isQ代码的结构：声明2个量子比特，依次施加H门、自定义的Oracle（使用控制相位门标记|11⟩）、通用的扩散算子，最后进行测量，完成从理论推导到代码实现的映射。
</think>

Grover搜索算法的核心在于利用量子叠加和干涉，将目标态的概率振幅放大，同时抑制非目标态的振幅。为了让你清晰地理解这个过程，我们将以2个量子比特为例，假设我们要在4个状态（|00⟩, |01⟩, |10⟩, |11⟩）中搜索目标态 |11⟩。

**第一步：初始化与均匀叠加**
首先，将2个量子比特初始化为 |00⟩。要对所有可能性进行搜索，我们需要对其施加全局的Hadamard门（H门），使其进入均匀叠加态。
数学推导：
|s⟩ = H|0⟩ ⊗ H|0⟩ = (1/√2)(|0⟩ + |1⟩) ⊗ (1/√2)(|0⟩ + |1⟩) = 1/2(|00⟩ + |01⟩ + |10⟩ + |11⟩)
此时，所有4个基态的概率振幅均为 a = 1/2 = 0.5。

**第二步：应用Oracle（相位反转）**
Oracle的作用是“标记”目标态。它通过将目标态的振幅反转来实现。假设我们的目标是 |11⟩。
数学推导：
当输入态为 |11⟩ 时，Oracle将其相位取反；其他状态保持不变。
|s₁⟩ = 1/2(|00⟩ + |01⟩ + |10⟩ - |11⟩)
此时，|00⟩, |01⟩, |10⟩ 的振幅为 0.5，而 |11⟩ 的振幅为 -0.5。

**第三步：应用扩散算子（Diffusion Operator，关于平均值的反转）**
这是Grover算法中最神奇的一步。扩散算子的作用是将所有的振幅关于它们的平均值进行反转。
1. 计算振幅的平均值 A：
A = (0.5 + 0.5 + 0.5 - 0.5) / 4 = 1 / 4 = 0.25
2. 根据平均值反转每个振幅（新振幅 = 2A - 旧振幅）：
- 对于 |00⟩: 新振幅 = 2(0.25) - 0.5 = 0
- 对于 |01⟩: 新振幅 = 2(0.25) - 0.5 = 0
- 对于 |10⟩: 新振幅 = 2(0.25) - 0.5 = 0
- 对于 |11⟩: 新振幅 = 2(0.25) - (-0.5) = 0.5 + 0.5 = 1.0

经过一次完整的Grover迭代后，非目标态的振幅全部变为0，目标态 |11⟩ 的振幅变为1.0！这意味着此时如果进行测量，我们将以100%的概率得到搜索目标 |11⟩。

**isQ语言代码实现**
在两比特情况下，目标态为 |11⟩ 的Oracle可以通过受控Z门（CZ）直接实现。扩散算子可以通过在H门和X门之间嵌入CZ门来实现。

import std;

qbit q[2];

procedure main() {
    // 第一步：初始化均匀叠加态
    H(q[0]);
    H(q[1]);

    // 第二步：应用Oracle标记目标态 |11⟩
    // CZ门当且仅当两个量子比特都为1时，对相位施加Z门（即乘以-1）
    CZ(q[0], q[1]);

    // 第三步：应用扩散算子
    // 扩散算子结构为 H -> X -> CZ -> X -> H
    H(q[0]);
    H(q[1]);

    X(q[0]);
    X(q[1]);

    CZ(q[0], q[1]);

    X(q[0]);
    X(q[1]);

    H(q[0]);
    H(q[1]);

    // 第四步：测量量子比特，此时结果必然是二进制的 11（即十进制的3）
    M(q[0]);
    M(q[1]);
}

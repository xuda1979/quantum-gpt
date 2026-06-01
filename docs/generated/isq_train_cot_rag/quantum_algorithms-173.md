# ISQ training COT RAG corpus: quantum_algorithms shard 173

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/algo/95

- task_id: `isqExpand/algo/95`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `interference`, `phase_manipulation`, `basis_change`
- source: `isq_expansion`
- dataset_index: `5442`

### Prompt

Code this in isQ: implementing the Deutsch algorithm for the balanced function f(x) = x. Use 2 qubits: q[0] as the input qubit and q[1] as the ancilla. Initialize the ancilla to |1> via X gate, apply Hadamard to both, apply the oracle (CNOT for f(x)=x), apply H to q[0], and measure q[0] only. The result |1> with certainty indicates a balanced function.

### Chain-of-thought reasoning

## Reasoning
Goal: Deutsch algorithm for f(x) = x (balanced).

1. X(q[1]): ancilla -> |1>
2. H(q[0]): |0> -> |+>, H(q[1]): |1> -> |->
3. CNOT(q[0],q[1]): |x>|-> -> (-1)^x |x>|->
   q[0] becomes (|0>-|1>)/sqrt(2) = |->
4. H(q[0]): |-> -> |1>
5. M(q[0]): deterministically |1>

Expected: [P(0), P(1)] = [0.0, 1.0]

## isqQA/quantum_algorithms/102_optimization_variant

- task_id: `isqQA/quantum_algorithms/102_optimization_variant`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `optimization_variant`, `algorithm`, `Grover算法在3-4量子比特上的实现`
- source: `qa_pipeline`
- dataset_index: `283`

### Prompt

在中小规模（例如3到4个量子比特）的无结构数据库搜索中，标准Grover算法在目标数量未知或需要避免过度迭代导致成功概率下降时存在局限。请问Grover算法有哪些针对这些局限性的重要优化变体？能否以4量子比特系统为例，展示一种使用相位匹配技术的改进变体实现，并使用isQ代码给出具体的量子线路？

### Reference answer

标准Grover算法在实际应用中面临两个主要局限：一是当解的数量未知时，过多的迭代会使得概率振幅越过最大值，导致“过度拟合”而降低测量成功率；二是算法的成功概率会在最大值和零之间剧烈振荡。为了克服这些问题，研究者们提出了多种优化变体。其中最重要的一类是**固定点量子搜索算法**（Fixed-point quantum search，如Yoder、Low和Chuang在2014年提出的变体）以及**相位匹配变体**。

传统的Grover算法中，Oracle和扩散算子等效于对目标态和非目标态施加相互正交且角度为 \(\pi\) 的相位翻转。而在相位匹配变体中，我们将扩散算子中的 \(\pi\) 相位旋转替换为任意角度 \(\theta\) 的旋转。这种改变打破了标准算法中振幅的完美正弦振荡特性，使得算法能够在一个较宽的迭代次数范围内保持单调递增的高概率，从而极大地提高了在未知解数量情况下的鲁棒性。

下面我们使用isQ语言实现一个4量子比特的相位匹配Grover搜索变体。假设我们要搜索的目标态是 \(|0101\rangle\)。在代码中，我们将传统的扩散算子中的多控Z门（相当于 \(\pi\) 相位）替换为多控的 \(R_z(2\pi/3)\) 门，以此来展示相位匹配变体的核心逻辑：

```isq
import std;

qbit q[4];

procedure main() {
    // 1. 初始化：使用Hadamard门制备4量子比特的均匀叠加态
    for i in 0:4 {
        H(q[i]);
    }

    // 2. 相位匹配 Oracle：标记目标态 |0101>
    // 注意：q[0]对应最右边的比特，因此我们要翻转q[1]和q[3]使其变为全1态（即计算基|1111>）
    X(q[1]);
    X(q[3]);
    // 对目标态施加相位翻转，这里仍保持标准的 \pi 相位
    ctrl @[q[0], q[1], q[2]] Z(q[3]);
    // 恢复比特状态
    X(q[1]);
    X(q[3]);

    // 3. 改进的相位匹配 Diffuser (变体核心)
    for i in 0:4 {
        H(q[i]);
    }
    for i in 0:4 {
        X(q[i]);
    }
    // 将标准的 Z门 替换为 Rz 门，角度设为 2*pi/3 (约2.094弧度)
    // 这是固定点搜索中实现非暴力振幅放大的关键
    ctrl @[q[0], q[1], q[2]] Rz(2.094, q[3]);
    for i in 0:4 {
        X(q[i]);
    }
    for i in 0:4 {
        H(q[i]);
    }

    // 4. 测量所有量子比特
    for i in 0:4 {
        M(q[i]);
    }
}
```

在这段isQ代码中，核心的区别在于扩散算子中使用的 `Rz(2.094, q[3])` 门。通过调整这个相位角，我们改变了系统态矢量在希尔伯特空间中的旋转轨迹。在标准Grover中，如果系统包含多个目标态，单次迭代可能就足以让振幅达到最大，此时如果执行两次迭代，成功率反而会暴跌至0。而使用如上所示的相位匹配变体，即使我们略微多执行了几次迭代，成功概率也不会跌至0，而是收敛到一个极高的固定值。这种鲁棒性使得该变体在当前NISQ（含噪声中等规模量子）时代的中小规模量子电路上具有更高的实际应用价值和实验成功率。

## isqExpand/algo/85

- task_id: `isqExpand/algo/85`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `grover`, `amplitude_amplification`, `multi_controlled_logic`, `interference`
- source: `isq_expansion`
- dataset_index: `1234`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[3];

procedure oracle_proc() {
    ctrl ctrl Z(q[0], q[1], q[2]);
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
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## 电路分析
目标：分析3比特Grover搜索|111>，2次迭代的输出。

### Oracle
|111>的oracle: ctrl @[q[0], q[1]] Z(q[2])，CCZ门直接翻转|111>的相位。

### 迭代次数分析
N=8, M=1: theta = arcsin(1/sqrt(8)) ≈ 0.3614
- 1次迭代: P = sin^2(3*theta) = 25/32 = 0.78125
- 2次迭代: P = sin^2(5*theta) = 0.9453125
- 3次迭代: P = sin^2(7*theta) ≈ 0.3301（过度旋转）

2次迭代比1次提高了成功概率（0.7813→0.9453）。

预期概率：|111>(index 7) = 0.9453125，每个非目标 = 0.0078125

### Reference answer

{'predicted_probs': {'000': 0.0078125, '001': 0.0078125, '010': 0.0078125, '011': 0.0078125, '100': 0.0078125, '101': 0.0078125, '110': 0.0078125, '111': 0.9453125}, 'explanation': 'This circuit applies 2 Grover iterations for |111> on 3 qubits (N=8, M=1). The oracle is a simple CCZ gate (ctrl @[q[0],q[1]] Z(q[2])) which flips the phase of |111>. After 2 iterations: P(|111>) = sin^2(5*theta) where theta = arcsin(1/sqrt(8)), giving P(|111>) = 0.9453125. This is higher than 1 iteration (0.78125) but 3 iterations would overshoot to 0.3301.'}

## isqTrain/2986

- task_id: `isqTrain/2986`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5701`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[2];
procedure main() {
    X(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1.  **Initial state**: |00⟩
2.  **X(q[0])**: Flips qubit 0 to |1⟩. State becomes |10⟩.
3.  **CNOT(q[0], q[1])**: Flips qubit 1 because qubit 0 is |1⟩. State becomes |11⟩.
4.  **CNOT(q[1], q[0])**: Flips qubit 0 because qubit 1 is |1⟩. State becomes |01⟩.
5.  **CNOT(q[0], q[1])**: Does nothing because qubit 0 is |0⟩. State remains |01⟩.
6.  **Final state**: |01⟩.

The predicted probability distribution is {"01": 1.0}.

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqQA/quantum_algorithms/88_optimization_variant

- task_id: `isqQA/quantum_algorithms/88_optimization_variant`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `optimization_variant`, `algorithm`, `DJ算法的Oracle构造`
- source: `qa_pipeline`
- dataset_index: `5805`

### Prompt

Deutsch-Jozsa (DJ) 算法展示了量子计算相对于经典计算的指数级查询加速，但原始DJ算法严格要求Oracle必须是绝对平衡或绝对常数的。在实际和理论扩展中，该算法有哪些重要的改进版本或变体？请详细解释其中一种重要变体的数学原理，并使用 isQ 语言给出一个针对 3 比特输入的量子电路代码示例。

### Reference answer

Deutsch-Jozsa 算法虽然作为量子计算的经典教学案例具有重要意义，但其在实际应用中受到“严格常数或平衡”这一苛刻条件的限制。为了提升其实用性和理论深度，研究者们提出了多个重要的改进版本和变体，其中最著名且应用最广的便是 **Bernstein-Vazirani (BV) 算法**。

Bernstein-Vazirani 算法可以被看作是 DJ 算法的一个极具价值的变体与泛化。在 BV 问题中，Oracle 不再是仅仅判断常数或平衡，而是隐藏了一个秘密的二进制字符串 $s \in \{0,1\}^n$。Oracle 的计算规则被严格定义为输入 $x$ 与秘密字符串 $s$ 的按位内积模 2 运算，即 $f_s(x) = s \cdot x \pmod 2$。经典确定性算法需要查询 $n$ 次才能逐位揭示字符串 $s$，而 BV 算法仅需 1 次量子查询即可精确得出 $s$。

数学推导过程如下：
1. 初始化系统状态为 $|0\rangle^{\otimes n}|1\rangle$，并对所有量子比特施加 Hadamard 门，系统状态演变为：
$$ |\psi_1\rangle = \frac{1}{\sqrt{2^n}} \sum_{x=0}^{2^n-1} |x\rangle \left(\frac{|0\rangle - |1\rangle}{\sqrt{2}}\right) $$
2. 将该状态输入 Oracle $U_f$。由于辅助比特处于 $| - \rangle$ 态，Oracle 的作用相当于对主寄存器引入了相位回踢（Phase Kickback）：
$$ U_f |x\rangle | - \rangle = (-1)^{s \cdot x} |x\rangle | - \rangle $$
3. 此时主寄存器的状态变为：
$$ |\psi_2\rangle = \frac{1}{\sqrt{2^n}} \sum_{x=0}^{2^n-1} (-1)^{s \cdot x} |x\rangle $$
4. 对主寄存器再次施加 Hadamard 门 $H^{\otimes n}$。根据多比特 Hadamard 逆变换的线性代数性质 $H^{\otimes n} \sum_x (-1)^{s \cdot x} |x\rangle = |s\rangle$，系统的状态直接坍缩并收敛到秘密字符串对应的基态 $|s\rangle$ 上。
5. 最后，对主寄存器进行测量，即可单次查询以概率 1 获得隐藏字符串 $s$。

以下是使用 isQ 语言实现的 Bernstein-Vazirani 算法代码示例。假设秘密字符串为 $s = 101$，利用 CNOT 门在 Oracle 构造中模拟相位回踢：

import std;

qbit q[3];
qbit anc[1];

procedure main() {
    // 初始化辅助比特为 |-\rangle 态
    X(anc[0]);
    H(anc[0]);

    // 对输入寄存器施加 Hadamard 门
    for i in 0:3 {
        H(q[i]);
    }

    // 构造 Bernstein-Vazirani Oracle
    // 秘密字符串 s = 101 (即 q[0]=1, q[1]=0, q[2]=1)
    // 对应位为1时，执行 CNOT 操作，利用辅助比特完成相位回踢
    CNOT(q[0], anc[0]);
    CNOT(q[2], anc[0]);

    // 再次对输入寄存器施加 Hadamard 门进行逆傅里叶变换
    for i in 0:3 {
        H(q[i]);
    }

    // 测量输入寄存器，直接读出秘密字符串
    for i in 0:3 {
        M(q[i]);
    }
}

## isqTrain/1119

- task_id: `isqTrain/1119`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2972`

### Prompt

Code this in isQ: implements the superdense_coding pattern but with a different initial state preparation (flip q[[0]] -> q[1]).

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Write an isQ program for a modified superdense coding circuit.
    *   **Modification:** Flip q[[0]] -> q[1] in the initial state preparation. The reference code used `H(q[0]); CNOT(q[0], q[1]);` to create a Bell pair. "Flip q[[0]] -> q[1]" likely means the initial preparation is `H(q[1]); CNOT(q[1], q[0]);`.
    *   **Encoding:** The message is '11'. Standard superdense encoding for '11' on the prepared qubit (which was originally q[0], but with the flipped prep, the "Alice" qubit might be q[1]).
    *   **Wait, let me reread carefully:** "superdense_coding pattern but with a different initial state preparation (flip q[[0]] -> q[1])".
    *   The circuit should:
        *   Prep: `H(q[0]); CNOT(q[0], q[1]);`
        *   Encode: `Z(q[0]); X(q[0]);` -> wait, the reference has a weird encoding `Z(q[0]); X(q[1]);` for '11'? Oh, the reference is a bit broken. Let me look at the reference:
            *   `Z(q[0]); X(q[1]);` -- This is a very strange encoding. Wait, for `11` superdense coding, Alice applies `X` then `Z` on her qubit (`q[0]`).
            *   Ah, the reference says "Alice encodes '11': apply Z then X". Wait, `X(q[1])` is on Bob's qubit? No, the reference is: `Z(q[0]); X(q[1]);` which makes no sense for standard superdense coding unless the user provided a weird reference.
            *   Wait! Let me re-analyze the.
            *   Reference:
                
            *   Wait, `Z(q[0]); X(q[1]);` on state `(1/sqrt2)(|00> + |11>)` yields `Z` on `q[0]` -> `(1/sqrt2)(|00> - |11>)`. `X` on `q[1]` -> `(1/sqrt2)(|01> - |10>)`.
            *   Then CNOT(q[0], q[1]) -> `(1/sqrt2)(|01> - |11>)` ... wait.
            *   Let's do the math for the reference code:
                *   Init: |00>
                *   H(q[0]): (1/sqrt2)(|00> + |10>)
                *   CNOT(q[0], q[1]): (1/sqrt2)(|00> + |11>)
                *   Z(q[0]): (1/sqrt2)(|00> - |11>)
                *   X(q[1]): (1/sqrt2)(|01> - |10>)
                *   CNOT(q[0], q[1]): (1/sqrt2)(|01> - |11>)
                *   H(q[0]): (1/2)(|01> + |11> - |11> + |01>) = |01>. The reference says "Expected measurement probabilities: {|11>: 1.0}". Wait! The implementation actually implements a circuit that measures |01>, NOT |11>.
                *   Let me re-analyze the:
                    "Alice encodes '11': apply Z then X // Z flips the phase, X flips the bit ... X(q[1]);" - Wait, this reference is literally insane. X(q[1]) is an error in the reference, it should have been `X(q[0])`. If it were `X(q[0])` and `Z(q[0])`, then `X(q[0])` gives `(1/sqrt2)(|10> - |01>)`, `Z(q[0])` gives `(1/sqrt2)(|10> + |01>)`. Then `CNOT` -> `(1/sqrt2)(|11> + |01>)`. `H(q[0])` -> `|11>`.
                *   So the reference has a typo in its code comments/logic, but I must follow the prompt's instruction: "superdense_coding pattern but with a different initial state preparation (flip q[[0]] -> q[1])".
                *   What does "

## isqTrain/1883

- task_id: `isqTrain/1883`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3580`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[2];
procedure main() {
    Ry(pi/3.0, q[0]);
    Ry(pi/4.0, q[1]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis

**Operations:** Ry(π/3, q[0]), Ry(π/4, q[1]), CNOT(q[0], q[1]), then measurement.

**State evolution:**

1. **Initial:** |00⟩

2. **Ry(π/3, q[0]):** cos(π/6)|0⟩ + sin(π/6)|1⟩ = (√3/2)|0⟩ + (1/2)|1⟩

3. **Ry(π/4, q[1]):** Tensor product gives:
   (√3/2·cos(π/8))|00⟩ + (√3/2·sin(π/8))|01⟩ + (1/2·cos(π/8))|10⟩ + (1/2·sin(π/8))|11⟩

4. **CNOT(q[0],

### Reference answer

{'predicted_probs': {'00': 0.6402, '01': 0.1098, '10': 0.0366, '11': 0.2134}, 'explanation': 'Expected probabilities: [0.6401650429449555, 0.1098349570550447, 0.03661165235168156, 0.2133883476483184]'}

## isqTrain/2826

- task_id: `isqTrain/2826`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3152`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```isq
import std;
qbit q[4];
// Create a 4-qubit GHZ state
procedure main() {
    // H(q[0]); // BUG: missing Hadamard
    for i in 1:4 {
        CNOT(q[i-1], q[i]);
    }
    for i in 0:4 {
        M(q[i]);
    }
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **The Bug:** The `H(q[0])` gate is commented out, preventing the creation of superposition. Without it, the initial state remains |0>, and the cascading CNOT gates simply propagate the |0> state, deterministically yielding |0000>.
2. **The Fix:** Uncomment the `H(q[0])` instruction to properly apply the Hadamard gate to the first qubit.
3. **State Evolution:** Initial state |0000> -> Apply H(q[0]) to get (|0000> + |1000>)/√2 -> Apply sequential CNOTs to entangle all qubits, resulting in the correct 4-qubit GHZ state (|0000> + |1111>)/√2.

## isqTrain/3935

- task_id: `isqTrain/3935`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `850`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```
import std;
// QAOA MaxCut p=1 on 4-node star graph
// gamma=0.785, beta=0.393
qbit q[4];

procedure main() {
    // Superposition
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    // Cost unitary
    // Edge (0,1)
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.785, q[1]);
    CNOT(q[0], q[1]);
    // Edge (0,2)
    CNOT(q[0], q[2]);
    Rz(2.0 * 0.785, q[2]);
    CNOT(q[0], q[2]);
    // Edge (0,3)
    CNOS(q[0], q[3]);
    Rz(2.0 * 0.785, q[3]);
    CNOT(q[0], q[3]);
    // Mixer
    Rx(2.0 * 0.393, q[0]);
    Rx(2.0 * 0.393, q[1]);
    Rx(2.0 * 0.393, q[2]);
    Rx(2.0 * 0.393, q[3]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **The Bug:** In the cost unitary for edge (0,3), the gate `CNOS(q[0], q[3])` is a typo and an invalid instruction. It should be a standard `CNOT` gate to properly implement the $ZZ$ interaction.
2. **The Fix:** Change `CNOS(q[0], q[3])` to `CNOT(q[0], q[3])`.
3. **State Evolution:** 
   - The four qubits are initialized to $|0\rangle^{\otimes 4}$.
   - Hadamard gates put all qubits into an equal superposition: $|+\rangle^{\otimes 4}$.
   - The corrected `CNOT`-`Rz`-`CNOT` sequences apply the phase separator $e^{-i\gamma Z_i Z_j}$ for each edge $(0,1)$, $(0,2)$, and $(0,3)$, introducing phase differences and entanglement based on the graph's cut values.
   - The `Rx` gates on all qubits act as the mixer, rotating the states to maximize the probability of measuring bitstrings that represent large cuts.
   - The measurements yield the expected distribution, strongly favoring high-cut states like $|0000\rangle$ and $|1111\rangle$ (which have cut value 0) wait, actually $|0111\rangle$ and $|1000\rangle$ (cut value 3) have the highest probabilities in the ideal output as they are the maximum cuts for the star graph.

## isqTrain/797

- task_id: `isqTrain/797`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3029`

### Prompt

用isQ实现implements the quantum_multiplier pattern. Include explicit identity operations in the circuit (X-X pair before M(q[3])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a quantum multiplier computing the LSB of a=1 × b=3, with explicit X-X gate cancellation.
2. **Qubits**: 4 qubits (q[0..3]); only q[3] is measured.
3. **State evolution**:
   - Initial: |0000⟩
   - X(q[0]), X(q[1]), X(q[2]): |1110⟩ (sets a=1, b0=1, b1=1)
   - Toffoli(q[0], q[1], q[3]): q[3] flips when both controls are |1⟩ → |1111⟩
   - X(q[3]): |1110⟩
   - X(q[3]): |1111⟩ (X-X pair cancels, restoring state)
4. **Expected probabilities**: q[3] is in |1⟩, so measurement yields {|1⟩: 1.0}.

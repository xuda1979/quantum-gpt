# ISQ training COT RAG corpus: quantum_algorithms shard 4

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4279

- task_id: `isqTrain/4279`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4213`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;

qbit q[2];

procedure main() {
    // Superposition
    H(q[0]);
    H(q[1]);
    // Function oracle: phase flips
    Z(q[0]);
    Z(q[1]);
    // Fourier transform back
    H(q[0]);
    H(q[1]);
    // Measure
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the request:**
    *   Task: Analyze an isQ quantum program, predict the probability distribution of measurement outcomes, and explain the reasoning.
    *   Input program: Applies H to q[0], q[1], then Z to q[0], q[1], then H to q[0], q[1], then X to q[0], then measures.
    *   Constraint: Concise, 3-8 lines for simple, up to 15 for complex. Use Dirac notation. Output ONLY the analysis starting with "## Circuit Analysis". End with the predicted probability distribution.

2.  **Analyze the circuit:**
    *   Initial state: $|00\rangle$
    *   Apply H to both: $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
    *   Apply Z to both: $Z|0\rangle = |0\rangle$, $Z|1\rangle = -|1\rangle$. State becomes $\frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle)$
    *   Apply H to both: State becomes $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle - (|00\rangle - |01\rangle + |10\rangle - |11\rangle) - (|00\rangle + |01\rangle - |10\rangle - |11\rangle) + (|00\rangle - |01\rangle - |10\rangle + |11\rangle))$.
        Wait, an easier way:
        $HZH = X$.
        So applying H, then Z, then H on each qubit is equivalent to applying X on each qubit.
        Let's check: $ZH|0\rangle = Z\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$. Apply H: $\frac{1}{2}(|0\rangle + |1\rangle - |0\rangle + |1\rangle) = |1\rangle$.
        So both qubits become $|1\rangle$.
        State before X gate: $|11\rangle$.
    *   Apply X to q[0]: Flips q[0] from 1 to 0. State becomes $|01\rangle$.
    *   Measure both: Outcome is deterministically $|01\rangle$.

3.  **Draft the explanation (incorporating step-by-step state evolution):**
    *   Initial: $|00\rangle$
    *   After H gates: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
    *   After Z gates: $Z$ applies a phase of $-1$ to $|1\rangle$. State: $\frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle)$
    *   After second H gates: Using $HZH = X$, the state becomes $|11\rangle$.
    *   After X gate on q[0]: Flips q[0] to $|0\rangle$. State is $|01\rangle$.
    *   Measurement: 100% probability for $|01\rangle$.

4.  **Refine to match constraints:**
    *   Start with "## Circuit Analysis"
    *   Concise, 3-8 lines.
    *   End with "Predicted probability distribution: {|01>: 1.0}"

    *Draft:*
    ## Circuit Analysis
    1. Initial state is $|00\rangle$. The first pair of Hadamard gates creates an equal superposition: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
    2. The Z gates apply a phase flip ($-1$) to the $|1\rangle$ components, yielding $\frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle)$.
    3. The second pair of Hadamard gates transforms the state using $HZH = X$, resulting in the basis state $|11\rangle$.
    4. The X gate on q[0] flips its state from $|

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|01>) = 1.0000.'}

## isqQA/quantum_algorithms/94_math_derivation

- task_id: `isqQA/quantum_algorithms/94_math_derivation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `math_derivation`, `algorithm`, `Grover搜索算法基本原理`
- source: `qa_pipeline`
- dataset_index: `4019`

### Prompt

请严密推导Grover搜索算法中量子态的演化过程，从数学角度解释为何Oracle算子与扩散算子的结合能够实现目标态概率幅的放大，并使用isQ语言给出核心演化的代码示例。

### Reference answer

<think>
要严密推导Grover算法的演化过程，核心在于几何视角的降维与反射变换。

首先，将 $N$ 维希尔伯特空间的问题投影到由目标态 $|w\rangle$ 和均匀非目标叠加态构成的二维平面。在此平面上定义初始角度 $\theta$，使得 $\sin\theta = 1/\sqrt{N}$。

接着，拆解两个核心算子的几何意义：Oracle算子 $U_\omega$ 翻转目标态的相位，在几何上等效于以非目标态为轴的反射；扩散算子 $U_s$ 翻转关于平均值的相位，等效于以初始叠加态 $|s\rangle$ 为轴的反射。

随后，推导两者结合的总体效果。根据几何学性质，连续执行两次不同轴的反射，等价于在二维子空间内进行一次角度为 $2\theta$ 的旋转。因此，每一次Grover迭代都会使系统状态向目标态 $|w\rangle$ 精确旋转 $2\theta$，从而实现目标态概率幅的指数级放大。

最后，基于此数学机制，推算出达到最大概率所需的最佳迭代次数为 $O(\sqrt{N})$，并将状态初始化、Oracle相位翻转、扩散算子操作及循环测量的逻辑，直接映射为isQ语言的量子线路代码。
</think>

Grover搜索算法的数学核心在于通过酉算子的迭代，在由目标态和非目标态张成的二维子空间中不断进行态矢量旋转，从而放大目标态的概率幅。

首先是数学推导部分。
假设搜索空间大小为 $N = 2^n$，目标态集合中只有一个元素 $|w\rangle$。算法初始态为 $|s\rangle = H^{\otimes n}|0\rangle^{\otimes n} = \frac{1}{\sqrt{N}}\sum_{x=0}^{N-1}|x\rangle$。
我们可以将系统的演化限制在由目标态 $|w\rangle$ 和其正交的非目标态叠加态 $|w^{\perp}\rangle$ 构成的二维子空间内。初始态可以表示为：
$|s\rangle = \sin(\theta)|w\rangle + \cos(\theta)|w^{\perp}\rangle$
其中 $\sin(\theta) = \frac{1}{\sqrt{N}}$。

Grover迭代由两个核心酉算子组成：
1. **Oracle算子 $U_\omega$**：该算子翻转目标态的相位，其数学定义为 $U_\omega|x\rangle = (-1)^{f(x)}|x\rangle$，其中当 $x=w$ 时 $f(x)=1$，否则为0。用投影算子表示为 $U_\omega = I - 2|w\rangle\langle w|$。在几何上，这相当于将量子态关于 $|w^{\perp}\rangle$ 对称轴进行反射。
2. **扩散算子 $U_s$**：该算子关于初始态 $|s\rangle$ 进行反射，定义为 $U_s = 2|s\rangle\langle s| - I$。

当我们将这两个反射操作结合，即作用 $U_s U_\omega$ 时，等价于在 $\{|w\rangle, |w^{\perp}\rangle\}$ 平面内将态矢量朝着 $|w\rangle$ 旋转了 $2\theta$ 的角度。
经过 $k$ 次Grover迭代后的量子态演化为：
$|\psi_k\rangle = (U_s U_\omega)^k |s\rangle = \sin((2k+1)\theta)|w\rangle + \cos((2k+1)\theta)|w^{\perp}\rangle$
随着迭代次数 $k$ 的增加，目标态 $|w\rangle$ 的概率幅 $\sin((2k+1)\theta)$ 不断增大。当 $(2k+1)\theta \approx \frac{\pi}{2}$ 时，测量得到 $|w\rangle$ 的概率接近1。由此推导出最优迭代次数为 $k \approx \frac{\pi}{4}\sqrt{N}$，实现了二次加速。

其次是isQ语言代码实现部分。
我们以2个量子比特（$N=4$）搜索 $|11\rangle$ 态为例。此时只需1次迭代即可达到最大概率。在isQ中，Oracle作用相当于对 $|11\rangle$ 施加负相位，即受控Z门(CZ)；扩散算子则通过H门、X门、CZ门和H门的组合来实现关于均匀叠加态的反射。

```isQ
import std;

qbit q[2];

procedure main() {
    // 1. 初始化：制备均匀叠加态 |s>
    H(q[0]);
    H(q[1]);

    // 2. 应用 Oracle 算子
    // 目标态为 |11>，使用 CZ 门实现相位翻转
    CZ(q[0], q[1]);

    // 3. 应用扩散算子
    // 在均匀叠加基矢下执行反射 H U_0 H
    H(q[0]);
    H(q[1]);
    
    // 将 |00> 翻转，等价于对 |11> 施加 CZ
    X(q[0]);
    X(q[1]);
    CZ(q[0], q[1]);
    X(q[0]);
    X(q[1]);
    
    H(q[0]);
    H(q[1]);

    // 4. 测量量子比特，将以极高概率坍缩到目标态 |11>
    M(q[0]);
    M(q[1]);
}
```

## isqTrain/765

- task_id: `isqTrain/765`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3388`

### Prompt

Write an isQ program that implements the weighted_adder pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a weighted adder computing sum of two input bits with reversed measurement order on the output qubits.

2. **Qubits**: 4 qubits total (q[0], q[1] as inputs; q[2], q[3] as sum outputs); only q[2] and q[3] are measured.

3. **State evolution**:
   - Initial state: |0000⟩
   - After X(q[0]), X(q[1]): |1100⟩ (both inputs set to |1⟩)
   - After CNOT(q[0], q[

## isqTrain/1259

- task_id: `isqTrain/1259`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `ancilla_usage`, `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `718`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;

// 3-qubit bit-flip code: syndrome detection
qbit data[3];
qbit syndrome[2];

procedure main() {
    // Encode logical |1> = |111>
    X(data[0]);
    CNOT(data[0], data[1]);
    CNOT(data[0], data[2]);
    // Introduce bit-flip error on data[1]: |111> -> |101>
    X(data[1]);
    // Syndrome extraction via parity checks
    // syndrome[0] = data[0] XOR data[1]
    CNOT(data[0], syndrome[0]);
    CNOT(data[1], syndrome[0]);
    // syndrome[1] = data[1] XOR data[2]
    CNOT(data[1], syndrome[1]);
    CNOT(data[2], syndrome[1]);
    // Measure syndrome: |11> indicates error on data[1]
    M(syndrome[0]); M(syndrome[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Analyze an isQ quantum program and predict the measurement probability distribution.
    *   Program: 3-qubit bit-flip code syndrome detection.
    *   Constraint 1: Concise, precise step-by-step reasoning (3-8 lines for simple, up to 15 for complex).
    *   Constraint 2: Use Dirac notation.
    *   Constraint 3: Output ONLY the analysis, starting with "## Circuit Analysis".
    *   Constraint 4: End with the predicted probability distribution.
    *   Constraint 5: no code blocks.

2.  **Trace the Circuit:**
    *   Initial state: $|00000\rangle$ (data[0..2] and syndrome[0..1] all 0)
    *   Encode logical |1>:
        *   `X(data[0])` -> $|10000\rangle$
        *   `CNOT(data[0], data[1])` -> $|11000\rangle$
        *   `CNOT(data[0], data[2])` -> $|11100\rangle$
    *   Introduce Error:
        *   `X(data[1])` -> $|10100\rangle$
    *   Syndrome Extraction:
        *   `CNOT(data[0], syndrome[0])` -> $|10110\rangle$ (data[0]=1 flips syndrome[0])
        *   `CNOT(data[1], syndrome[0])` -> $|10100\rangle$ (data[1]=0 flips syndrome[0] back)
        *   `CNOT(data[1], syndrome[1])` -> $|10101\rangle$ (data[1]=0, no flip... wait, wait. Wait, let me re-evaluate this step carefully.
        *   Ah, wait. Let's look at the state after error: $|10100\rangle$
        *   `CNOT(data[0], syndrome[0])`: data[0]=1, so flip syndrome[0]. State is $|10110\rangle$.
        *   `CNOT(data[1], syndrome[0])`: data[1]=0, so do not flip syndrome[0]. State is $|10110\rangle$.
        *   `CNOT(data[1], syndrome[1])`: data[1]=0, so do not flip syndrome[1]. State is $|10110\rangle$.
        *   `CNOT(data[2], syndrome[1])`: data[2]=1, so flip syndrome[1]. State is $|10111\rangle$.
    *   Let me re-read the CNOTs:
        *   Syndrome[0] parity check: `CNOT(data[0], syndrome[0])` and `CNOT(data[1], syndrome[0])`. This calculates data[0] XOR data[1]. Here, 1 XOR 0 = 1. So syndrome[0] should be 1.
        *   Syndrome[1] parity check: `CNOT(data[1], syndrome[1])` and `CNOT(data[2], syndrome[1])`. This calculates data[1] XOR data[2]. Here, 0 XOR 1 = 1. So syndrome[1] should be 1.
    *   Final state: $|10111\rangle$ (data is $|101\rangle$, syndrome is $|11\rangle$).
    *   Measurement: `M(syndrome[0])`, `M(syndrome[1])`.
    *   Wait, the prompt says "--probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit)".
    *   syndrome[0] is measured first -> higher bit. syndrome[1] measured second -> lower bit.
    *   Syndrome is $|11\rangle$.
    *   Probability distribution: {'11': 1.0}.

3.  **Format the Output:**
    *   Start with "## Circuit Analysis"
    *   Step-by-step evolution.
    *   Final distribution.

4.  **Drafting the Content:**
    *   ## Circuit Analysis
    *   Initial state is $|00000\rangle$ (data[0..2], syndrome[0..1]).
    *   Encoding prepares the logical state: X on data[0] gives $|10000\rangle$, and subsequent CNOTs yield $|11100\rangle$.
    *   An error X on data[1] flips it to 0, resulting in $|10100\rangle$.
    *   Parity check for syndrome[0] uses data[0] and data[1]. Since data[0]=1 and data[

### Reference answer

{'predicted_probs': {'3': 1.0}, 'explanation': 'Parametric variant of isqEval/459. Dimension: predict probabilities for reference circuit.'}

## isqTrain/4560

- task_id: `isqTrain/4560`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2378`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;

oracle bool[1] f(bool x[3]) {
    
    bool res[] = [x[1] != x[2]];
    return res;
}

qbit q[3];

qbit anc[1];

procedure main() {
    
    X(anc[0]);
    H(anc[0]);
    
    H(q[0]); H(q[1]); H(q[2]);
    
    f(q, anc);
    
    H(q[0]); H(q[1]); H(q[2]);
    
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise, step-by-step analysis of an isQ quantum program, predicting the probability distribution of measurement outcomes. The analysis should be in "quantum computing expert" persona, use Dirac notation, and be limited to 3-15 lines.

2.  **Analyze the isQ Code:**
    *   `qbit q[3];` and `qbit anc[1];`: 4 qubits total. `q` starts in `|000>`, `anc` in `|0>`.
    *   `X(anc[0]); H(anc[0]);`: Prepares `anc` in `|->` = $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
    *   `H(q[0]); H(q[1]); H(q[2]);`: Puts `q` in an equal superposition of all 8 states: $\frac{1}{2\sqrt{2}} \sum_{x=0}^{7} |x\rangle$.
    *   `f(q, anc);` where `f(bool x[3])` returns `[x[1] != x[2]]`:
        *   This oracle computes $f(x) = x_1 \oplus x_2$.
        *   Applying it to `q` (input) and `anc` (target in $|-\rangle$) performs a phase kickback: $|x\rangle(-1)^{f(x)}|-\rangle$.
        *   So the state of `q` becomes $\frac{1}{2\sqrt{2}} \sum (-1)^{x_1 \oplus x_2} |x\rangle$.
    *   `H(q[0]); H(q[1]); H(q[2]);`: This is the Deutsch-Jozsa / Bernstein-Vazirani inverse Hadamard transform.
        *   Let's trace the state of `q`:
        *   $H^{\otimes 3}$ applied to $\sum (-1)^{x_1 \oplus x_2} |x\rangle$.
        *   Wait, $x_0$ is independent of the phase. The phase is $(-1)^{x_1 \oplus x_2}$.
        *   This corresponds to the state $|0\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$? No, $x_1 \oplus x_2 = x_1 + x_2 - 2x_1 x_2$.
        *   Let's do this algebraically.
        *   State before the second Hadamards: $|\psi\rangle = \frac{1}{2\sqrt{2}} \sum_{x \in \{0,1\}^3} (-1)^{x_1 \oplus x_2} |x_0 x_1 x_2\rangle$.
        *   Apply $H$ on $q_0, q_1, q_2$.
        *   For $q_0$: $H$ on $\sum (-1)^{0} |x_0\rangle = |+\rangle$. Result is $|0\rangle$.
        *   For $q_1, q_2$: $\frac{1}{2} \sum_{x_1, x_2} (-1)^{x_1 \oplus x_2} |x_1 x_2\rangle$.
        *   The states of $q_1, q_2$ are $|01\rangle$ and $|10\rangle$ with amplitude $1/2$, and $|00\rangle, |11\rangle$ with amplitude $-1/2$.
        *   Let's check: $\frac{1}{2} (|00\rangle - |01\rangle - |10\rangle + |11\rangle)$ is $|-\rangle|-\rangle$.
        *   Wait, $(-1)^{0 \oplus 0} = 1$. $(-1)^{0 \oplus 1} = -1$. $(-1)^{1 \oplus 0} = -1$. $(-1)^{1 \oplus 1} = 1$.
        *   Yes, so the state of $q_1, q_2$ is $\frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle) = |-\rangle|-\rangle$.

### Reference answer

{'predicted_probs': {'111': 1.0}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|111>) = 1.0000.'}

## isqTrain/72

- task_id: `isqTrain/72`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`
- source: `isq_train_cot`
- dataset_index: `5142`

### Prompt

帮我写一个isQ程序：implements the bell_state_preparation pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Create a Bell state, encode "11" via Z then X on q[0], decode with CNOT+H, and include an XX identity pair before measurement.

**Qubits:** 2 (q[0], q[1]), both measured.

**State evolution:**
1. `H(q[0])`: |00⟩ → |+0⟩ = (|00⟩+|10⟩)/√2
2. `CNOT(q[0],q[1])`: → |Φ⁺⟩ = (|00⟩+|11⟩)/√2
3. `Z(q[0])`: → (|00⟩−|11⟩)/√2 = |Φ⁻⟩
4. `X(q[0])`: → (|10⟩−|01⟩)/√2 = |Ψ⁻⟩
5. `CNOT(q[0],q[1])`: → (|11⟩−|01⟩)/√2
6. `H(q[0])`: H|0⟩=|+⟩, H|1⟩=|−⟩ applied to q[0]; algebra yields −|11⟩
7. `X(q[0])`: → −|01⟩
8. `X(q[0])`: → −|11⟩ (XX=I, demonstrating cancellation awareness)

**Result:** State is |11⟩ (up to global phase), so P(|11⟩)=1.0.

## isqTrain/2720

- task_id: `isqTrain/2720`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_deriving_gate`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2323`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
defgate U0 = [
    1, 0, 0, 0, 0, 0, 0, 0;
    0, -1, 0, 0, 0, 0, 0, 0;
    0, 0, -1, 0, 0, 0, 0, 0;
    0, 0, 0, -1, 0, 0, 0, 0;
    0, 0, 0, 0, -1, 0, 0, 0;
    0, 0, 0, 0, 0, -1, 0, 0;
    0, 0, 0, 0, 0, 0, -1, 0;
    0, 0, 0, 0, 0, 0, 0, -1
];
oracle U_omega(3,1) = [0,1,0,0,0,0,0,0];
qbit q[3];
qbit anc;
int grover_search() {
    H(q);
    X(anc);
    H(anc);
    for i in 0:2 {
        U_omega(q[2], q[1], q[0], anc);
        H(q);
        U0(q[2], q[1], q[0]);
        H(q);
    }
    H(anc);
    X(anc);
    return M(q);
}
procedure main(){
    print grover_search();
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ code:**
    *   Number of qubits: `qbit q[3]; qbit anc;` -> 4 qubits.
    *   Initialization: `H(q)` puts $q[0, 1, 2]$ into $|+\rangle$ states, so $|q\rangle = \frac{1}{\sqrt{8}}\sum_{x=0}^7 |x\rangle$. `X(anc)` then `H(anc)` puts ancilla in $|-\rangle$.
    *   Target state: `oracle U_omega(3,1) = [0,1,0,0,0,0,0,0];` marks state $|001\rangle$ (which is index 1) as the target. Wait, in isQ, qubits are ordered $q[2], q[1], q[0]$. So $|001\rangle$ means $q[2]=0, q[1]=0, q[0]=1$. Let's trace carefully.
    *   Grover iterations: `for i in 0:2` -> runs exactly 3 times.
    *   $U_0$ is the standard Grover diffusion operator: it reflects about $|000\rangle$, effectively applying $H^{\otimes 3} (\mathbb{I} - 2|0\rangle\langle0|) H^{\otimes 3}$. Notice the matrix is diagonal with $1, -1, -1, -1, -1, -1, -1, -1$. So $U_0 = \mathbb{I} - 2|0\rangle\langle0|$.
    *   Oracle $U_\omega$ applies a phase of $-1$ to $|001\rangle$.
    *   Wait, `U_omega` uses an ancilla: `U_omega(q[2], q[1], q[0], anc);`. The ancilla is in $|-\rangle$, so applying an oracle that XORS into the ancilla is equivalent to applying a $Z$ gate to the target state.
    *   Number of iterations: $N=3$, $n=3$. Optimal iterations $\approx \frac{\pi}{4}\sqrt{8} \approx 2.2$. The code runs 3 times. Over-rotating!
    *   Wait, what is $N$ (number of solutions)? $U_\omega$ has only one '1' in its array (index 1). So $M=1$.
    *   Let's check the exact state after 3 iterations.
        Initial state for search subspace: $|s\rangle = \frac{1}{\sqrt{8}} \sum_{x=0}^7 |x\rangle$.
        Target state $|w\rangle = |001\rangle$.
        Non-target state $|s'\rangle = \frac{1}{\sqrt{7}} \sum_{x \neq 1} |x\rangle$.
        $|s\rangle = \sqrt{1/8} |w\rangle + \sqrt{7/8} |s'\rangle$.
        Initial angle $\theta$ with $|s'\rangle$: $\sin \theta = \sqrt{1/8}$, $\cos \theta = \sqrt{7/8}$.
        Each iteration rotates by $2\theta$.
        After $k$ iterations: state is $\cos((2k+1)\theta) |s'\rangle + \sin((2k+1)\theta) |w\rangle$.
        For $k=3$, $(2k+1)\theta = 7\theta$.
        Wait, we only measure $q[0], q[1], q[2]$. The ancilla is returned to $|-\rangle$ at the end.
        Let's calculate $\sin(7\theta)$:
        $\theta = \arcsin(1/\sqrt{8})$.
        $\sin(2\theta) = 2\sin\theta\cos\theta = 2 \cdot \frac{1}{\sqrt{8}} \frac{\sqrt{7}}{\sqrt{8}} = \frac{\sqrt{14}}{8} \cdot 2 = \frac{\sqrt{14}}{4}$.
        $\cos(2\theta) = \cos^2\theta - \sin^2\theta = 7/8 - 1/8 = 6/8 = 3/4$.
        We need $\sin(7\theta)$. We can just apply the Grover operator 3 times.
        Let's represent the state in the $|w\rangle, |s'\

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3473

- task_id: `isqTrain/3473`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `684`

### Prompt

Implement a quantum circuit in isQ: Grover's algorithm for 3 qubits searching for |000> in isQ.

Oracle: X on all qubits, ctrl ctrl Z, X on all.
2 iterations. Declare 3 qubits, measure all.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Grover's algorithm on 3 qubits searching for |000⟩, using 2 iterations with X-based oracle and H-based diffusion.

**Qubits:** 3 qubits declared globally, all 3 measured.

**State evolution:**
1. **Init:** |000⟩ → H⊗³ → |s⟩ = (1/2√2)Σ|x⟩ (uniform superposition over 8 states)
2. **Oracle (marks |000⟩):** X⊗³ flips all qubits, so |000⟩↔|111⟩; `ctrl ctrl Z` phases |111⟩ by -1; X⊗³ restores — only |000⟩ acquires -1 phase.
3. **Diffusion:** H⊗³ maps to computational basis, X⊗³ + `ctrl ctrl Z` + X⊗³ phases |000⟩ by -1, H⊗³ returns — equivalent to 2|s⟩⟨s| - I, reflecting amplitudes about mean.
4. **Iteration 1:** Target amplitude increases from 1/(2√2) ≈ 0.177 to ~5/(2√2) ≈ 0.884; non-target amplitudes become ~−1/(2√2) ≈ −0.177.
5. **Iteration 2:** Second reflection further amplifies |000⟩ amplitude to ~13/(2√14) ≈ 0.972.
6. **Final state:** |ψ⟩ ≈ 0.972|000⟩ + small uniform amplitudes over |001⟩...|111⟩

**Expected probabilities:** |000⟩ ≈ 0.945312 (dominant), each of the 7 non-target states ≈ 0.007812, consistent with two Grover iterations optimally amplifying the marked state.

## isqExpand/algo/7

- task_id: `isqExpand/algo/7`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `bernstein_vazirani`, `oracle`, `inner_product`
- source: `isq_expansion`
- dataset_index: `1289`

### Prompt

Create an isQ quantum circuit that implementing the Bernstein-Vazirani algorithm to find the hidden string s=101 (3 bits). The oracle implements f(x) = s·x mod 2.

### Chain-of-thought reasoning

## Reasoning
Goal: BV algorithm for s=101 (binary), meaning s[0]=1, s[1]=0, s[2]=1.
Qubits: q[0..2] = input, q[3] = ancilla.

1. X(q[3]): ancilla to |1>
2. H on all: input -> |+++>, ancilla -> |->
3. Oracle: f(x) = x[0]*1 + x[1]*0 + x[2]*1 mod 2 = x[0] XOR x[2]
   Implement: CNOT(q[0], q[3]) and CNOT(q[2], q[3])
   With ancilla in |->: each CNOT adds (-1)^x_i phase when s_i=1
4. H on input: H^n (-1)^(s·x)|x> = |s> = |101>

Measured qubits: q[0],q[1],q[2]. Expected |101> = index 5 with prob 1.0.
Expected probs: [0,0,0,0,0,1,0,0]

## isqTrain/4846

- task_id: `isqTrain/4846`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `quantum_counting`, `interference`
- source: `isq_train_cot`
- dataset_index: `1288`

### Prompt

Write an isQ program that demonstrating Grover search does nothing useful when the oracle marks ALL states. Apply Z to both qubits and CZ as oracle (marks all 4 states with some phase). One iteration, measure.

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

Initial state: |00⟩

After H(q[0]) and H(q[1]): (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

Oracle: Z(q[0]) Z(q[1]) CZ(q[0], q[1])
- Z on q[0]: |0⟩→|0⟩, |1⟩→-|1⟩, so flips sign of states where q[0]=1: (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2
- Z on q[1]: flips sign of states where q[1]=1: (|00⟩ - |01⟩ - |10⟩ + |11⟩)/2
- CZ(q[0], q[1]): flips sign when both are |1⟩: (|00⟩ - |01⟩ - |10⟩ - |11⟩)/2

So the oracle applies: -1^{|00⟩ has no negative} but let me recalculate.

Actually, the product of signs:
- |00⟩: Z(q[0]) gives +, Z(q[1]) gives +, CZ gives + → total +
- |01⟩: Z(q[0]) gives +, Z(q[1]) gives -, CZ gives + → total -
- |10⟩: Z(q[0]) gives -, Z(q[1]) gives +, CZ gives + → total -
- |11⟩: Z(q[0]) gives -, Z(q[1]) gives -, CZ gives - → total -

So state after oracle: (|00⟩ - |01⟩ - |10⟩ - |11⟩)/2

This is -|+⟩|+⟩ + 2|00⟩/2... hmm, let me think differently.

Actually: (|00⟩ - |01⟩ - |10⟩ - |11⟩)/2 = -|++⟩ + |00⟩

Wait: |++⟩ = (|0⟩+|1⟩)(|0⟩+|1⟩)/2 = (|00⟩+|01⟩+|10⟩+|11⟩)/2

So (|00⟩ - |01⟩ - |10⟩ - |11⟩)/2 = |00⟩ - (|01⟩+|10⟩+|11⟩)/2 = 2|00⟩/2 - (|00⟩+|01⟩+|10⟩+|11⟩)/2 = |00⟩ - |++⟩

Hmm, let me just compute what the diffusion operator does.

Diffusion: H⊗2 X⊗2 CZ X⊗2 H⊗2

This is the standard Grover diffusion operator which reflects about |00⟩ in the computational basis (or about |++⟩ in the H basis).

After oracle, state is: (|00⟩ - |01⟩ - |10⟩ - |11⟩)/2

Apply H⊗2: 
H|0⟩ = |+⟩, H|1⟩ = |-⟩

H⊗2 (|00⟩ - |01⟩ - |10⟩ - |11⟩)/2 = (|++⟩ - |+-⟩ - |-+⟩ - |--⟩)/2

|+-⟩ = (|0⟩-|1⟩)|+⟩/... no wait.

Let me be more careful.

H⊗2 applied to |00⟩ = |++⟩
H⊗2 applied to |01⟩ = |+−⟩
H⊗2 applied to |10⟩ = |−+⟩
H⊗2 applied to |11⟩ = |−−⟩

So H⊗2 state: (|++⟩ - |+−⟩ - |−+⟩ - |−−⟩)/2

Now apply X⊗2:
(|++⟩ - |+−⟩ - |−+⟩ - |−−⟩)/2 (X doesn't change |+⟩ or |-⟩ since X|+⟩=|+⟩, X|-⟩=|-⟩)

Wait, X|+⟩ = X(|0⟩+|1⟩)/√2 = (|1⟩+|0⟩)/√2 = |+⟩. And X|-⟩ = X(|0⟩-|1⟩)/√2 = (|1⟩-|0⟩)/√2 = -|-⟩.

So X⊗2:
|++⟩ → |++⟩
|+−⟩ → -|+−⟩
|−+⟩ → -|−+⟩
|−−⟩ → |−−⟩

State after X⊗2: (|++⟩ + |+−⟩ + |−+⟩ - |−−⟩)/2

Apply CZ(q[0], q[1]): CZ flips the sign of |--⟩ in the H basis? No, CZ operates in computational basis.

Hmm, I need to express in computational basis to apply CZ.

Let me restart

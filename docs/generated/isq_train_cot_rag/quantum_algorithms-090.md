# ISQ training COT RAG corpus: quantum_algorithms shard 90

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqQA/quantum_algorithms/113_comparison

- task_id: `isqQA/quantum_algorithms/113_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `comparison`, `algorithm`, `QFT与经典FFT的对比`
- source: `qa_pipeline`
- dataset_index: `1824`

### Prompt

量子傅里叶变换（QFT）的时间复杂度为O((log N)^2)，远优于经典快速傅里叶变换（FFT）的O(N log N)。既然存在如此显著的指数级加速，为什么我们不能直接用QFT替代经典FFT来处理日常的音频或图像信号处理任务？请详细对比两者的适用场景、核心差异以及QFT在实际应用中面临的根本性限制，并使用isQ语言实现一个简单的3量子比特QFT电路来辅助说明。

### Reference answer

Quantum Fourier Transform (QFT) 和经典的 Fast Fourier Transform (FFT) 虽然在数学本质上都是将信号从时域/空域转换到频域，但它们在计算范式、适用场景和物理限制上存在根本性的差异。

1. **时间复杂度与状态空间的差异**
QFT 的输入是大小为 N=2^n 的量子叠加态，输出同样是另一个叠加态。它的复杂度仅为 O(n^2)（如果忽略纠缠态的制备时间），而经典 FFT 处理长度为 N 的数组需要 O(N log N) 次 operations。然而，这种指数级加速的前提是我们只关心计算过程本身的 operations，而忽略了量子态的 I/O 瓶颈。

2. **核心差异与根本性限制（I/O 瓶颈）**
这是 QFT 无法替代经典 FFT 的核心原因。量子态无法被直接完整读取。根据量子力学的测量公理，如果我们对经过 QFT 后的频域量子态进行测量，波函数会瞬间坍缩，我们只能以概率形式随机获得某一个频率分量的本征值。要获得完整的经典频谱，我们需要重复制备量子态并执行 O(N) 次测量，这彻底抵消了 QFT 在计算阶段带来的指数级加速。

3. **适用场景对比**
- **经典 FFT**：适用于需要获取完整全局频谱信息的场景，如音频处理、图像压缩、雷达信号分析等。它的输入和输出都是确定性的经典数据。
- **QFT**：由于无法高效提取所有频率信息，QFT 极少被直接用于信号频谱分析。它的真正威力在于作为其他量子算法的内部子程序（如 Shor 算法和量子相位估计 QPE）。在这些场景中，我们只需要提取周期或特定的相位信息，而不需要读取整个频谱，此时 QFT 的指数级加速能被完美利用。

以下是在isQ语言中实现的3-qubit QFT代码，展示了如何通过 Hadamard 门和受控相位旋转构建量子变换，并使用了三个 CNOT 门等效替代了由于算法需要的比特反转（SWAP）操作：

```isq
import std;

qbit q[3];

// 使用3个CNOT门等效实现SWAP操作，规避直接使用SWAP门
procedure swap_equivalent(int a, int b) {
    CNOT(q[a], q[b]);
    CNOT(q[b], q[a]);
    CNOT(q[a], q[b]);
}

procedure main() {
    // 假设初始量子态已经被编码，例如编码为 |5> (即二进制 |101>)
    X(q[0]);
    X(q[2]);

    // --- 开始 3-qubit QFT 算法 ---
    
    // 处理第1个量子比特 (q[0])
    H(q[0]);
    // 受控相位旋转 S 门 (相当于 Rz(pi/2))
    ctrl @[q[1]] S(q[0]);
    // 受控相位旋转 T 门 (相当于 Rz(pi/4))
    ctrl @[q[2]] T(q[0]);

    // 处理第2个量子比特 (q[1])
    H(q[1]);
    // 受控相位旋转 S 门
    ctrl @[q[2]] S(q[1]);

    // 处理第3个量子比特 (q[2])
    H(q[2]);

    // QFT的最后需要反转量子比特的顺序，使用自定义的等效SWAP
    swap_equivalent(0, 2);

    // 测量：此时如果多次运行，会以一定概率坍缩到相应的频域基态上
    for i in 0:3 {
        M(q[i]);
    }
}
```

总结来说，QFT 并非经典 FFT 的直接替代品，而是针对特定量子计算任务设计的专用工具。两者在各自适用的领域中发挥着不可替代的作用。

## isqTrain/2734

- task_id: `isqTrain/2734`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_if_else`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2811`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
oracle A(4,1) = [0,1,1,0,0,0,0,0,0,0,1,1,0,1,0,1];
oracle g(2,1) = [0,1,1,0]; 
int a;
qbit q[4], p[3];
procedure hadamard_layer(int k){
    H(q[2*k]);
    H(q[2*k+1]);
}
procedure recursive_fourier_sampling(int k){
    if (k == 2){
        A(q[0], q[1], q[2], q[3], p[2]);
    }else{
        hadamard_layer(k);
        X(p[k+1]);
        H(p[k+1]);
        recursive_fourier_sampling(k+1);
        hadamard_layer(k);
        g(q[2*k],q[2*k+1], p[k]);
        hadamard_layer(k);
        recursive_fourier_sampling(k+1);
        hadamard_layer(k);
        H(p[k+1]);
        X(p[k+1]);
    }
}
procedure main(){
    a = 0;
    recursive_fourier_sampling(a);
    int g = M(p[0]);    
    print g;
}
```

### Chain-of-thought reasoning

The user wants to analyze the given isQ program and compute the final quantum state before measurement, then determine the probability distribution.
Let's break down the program.
Qubits: `q[4], p[3]`. Initial state is `|0>`^7.
Oracles:
A(4,1) = [0,1,1,0,0,0,0,0,0,0,1,1,0,1,0,1].
g(2,1) = [0,1,1,0].
Let's understand the oracle syntax.
`oracle A(4,1) = [...]` implies it acts on 4 input qubits and 1 output qubit.
The array represents a boolean function $f(x)$ for $x \in \{0, 1\}^4$.
If the array indices are $0$ to $15$, $f(x) = \text{array}[x]$.
The oracle applies $|x\rangle |y\rangle \to |x\rangle |y \oplus f(x)\rangle$.
A(4,1) = [0,1,1,0,0,0,0,0,0,0,1,1,0,1,0,1] means $f(x)$ is:
x=0: 0
x=1: 1
x=2: 1
x=3: 0
x=4: 0
x=5: 0
x=6: 0
x=7: 0
x=8: 0
x=9: 0
x=10: 1
x=11: 1
x=12: 0
x=13: 1
x=14: 0
x=15: 1

g(2,1) = [0,1,1,0] means:
x=0: 0
x=1: 1
x=2: 1
x=3: 0

Procedures:
`hadamard_layer(k)`:
Applies H to `q[2k]` and `q[2k+1]`.

`recursive_fourier_sampling(k)`:
If k == 2:
  `A(q[0], q[1], q[2], q[3], p[2]);`
Else (k=0 or k=1):
  `hadamard_layer(k);`
  `X(p[k+1]);`
  `H(p[k+1]);`
  `recursive_fourier_sampling(k+1);`
  `hadamard_layer(k);`
  `g(q[2*k], q[2*k+1], p[k]);`
  `hadamard_layer(k);`
  `recursive_fourier_sampling(k+1);`
  `hadamard_layer(k);`
  `H(p[k+1]);`
  `X(p[k+1]);`

Let's trace k=0:
H(q[0]), H(q[1])
X(p[1]), H(p[1])  -> puts p[1] into |-> state
recursive_fourier_sampling(1)
H(q[0]), H(q[1])
g(q[0], q[1], p[0])
H(q[0]), H(q[1])
recursive_fourier_sampling(1)
H(q[0]), H(q[1])
H(p[1]), X(p[1]) -> uncomputes p[1] back to |0>

Wait, inside k=0, the operations on p[1] are:
X(p[1]); H(p[1]) -> sets p[1] to |->.
Then recursive(1) happens.
Then H(p[1]); X(p[1]) -> sets p[1] back to |0>?
Wait. `H X |0>` is `H |1> = |->`.
`H X |->` is `H (|0> - |1>)/\sqrt{2}`? No, `X|-> = |->`.
`H |-> = |1>`. `X |1> = |0>`.
So it perfectly uncomputes p[1] and leaves it as |0>.
Wait, does p[1] stay unentangled?
Inside `recursive_fourier_sampling(1)`:
H(q[2]), H(q[3])
X(p[2]), H(p[2]) -> puts p[2] into |->.
recursive_fourier_sampling(2) -> applies A(q[0..3], p[2]).
H(q[2]), H(q[3])
g(q[2], q[3], p[1])
H(q[2]), H(q[3])
recursive_fourier_sampling(2) -> applies A(q[0..3], p[2

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3051

- task_id: `isqTrain/3051`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`
- source: `isq_train_cot`
- dataset_index: `2946`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[3];
procedure main() {
    X(q[2]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes three qubits `q[0]`, `q[1]`, and `q[2]` in the state `|000>` and applies an `X` gate to `q[2]`.
2. The `X` gate flips the state of `q[2]` from `|0>` to `|1>`, evolving the state to `|001>`.
3. All three qubits are measured in the computational basis. 
4. The quantum state is deterministically in `|001>` right before measurement, so it will be measured as `001` with certainty.

Predicted probabilities: [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

### Reference answer

{'predicted_probs': {'001': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3057

- task_id: `isqTrain/3057`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`
- source: `isq_train_cot`
- dataset_index: `2326`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[3];
procedure main() {
    X(q[1]);
    X(q[2]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations:** The circuit initializes 3 qubits in |000>, then applies an X gate to q[1] and q[2].
2. **State evolution:** 
   - Initial state: |000>
   - After X(q[1]): |010>
   - After X(q[2]): |011>
3. **Final state:** The system is in the definite basis state |011>.
4. **Probabilities:** Measurement yields `011` with certainty (100%). Mapping to standard array indexing where earlier measured qubits are higher bits, this is index 3.

[0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]

### Reference answer

{'predicted_probs': {'011': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/2820

- task_id: `isqTrain/2820`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1480`

### Prompt

修复以下isQ程序中的错误：

```isq
import std;
qbit q[2];
// Create a 2-qubit GHZ state
procedure main() {
    H(q[0]);
    for i in 1:2 {
        CNOT(q[i], q[i-1]);
    }
    for i in 0:2 {
        M(q[i]);
    }
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: In the CNOT gate call `CNOT(q[i], q[i-1])`, the control and target are swapped. When i=1, q[1] (uninitialized |0>) controls q[0] (in superposition), which does not create entanglement.
2. **Fix**: Swap CNOT arguments to `CNOT(q[i-1], q[i])` so the previously prepared qubit acts as control.
3. **State evolution**: |00> → H(q[0]) → (|00>+|10>)/√2 → CNOT(q[0],q[1]) → (|00>+|11>)/√2, yielding P(|00>)=0.5, P(|11>)=0.5.

## isqTrain/2978

- task_id: `isqTrain/2978`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `864`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```isq
import std;
qbit q[4];
// 3-layer H+CNOT circuit on 4 qubits
procedure main() {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    CNOT(q[3], q[0]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[3], q[2]);
    CNOT(q[3], q[0]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[3]);
    CNOT(q[3], q[0]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug identification**: In the second layer, the third CNOT is `CNOT(q[3], q[2])` which swaps control and target. Layers 1 and 3 follow a consistent ring pattern: `CNOT(q[2], q[3])` where q[2] controls q[3]. Layer 2 breaks this with `CNOT(q[3], q[2])`.

2. **Fix**: Change `CNOT(q[3], q[2])` to `CNOT(q[2], q[3])` in the second layer. This restores the consistent ring entanglement pattern (q[0]→q[1]→q[2]→q[3]→q[0]) across all three layers.

3. **State evolution (corrected)**:
   - **After Layer 1 H+CNOT**: H gates create superposition |+⟩⊗4. Ring of CNOTs entangles qubits, distributing amplitude across even-parity computational basis states.
   - **After Layer 2 H+CNOT (corrected)**: H gates transform back toward computational basis with phases. The corrected CNOT ring `q[2]→q[3]` maintains the cyclic entanglement structure, properly mixing amplitudes.
   - **After Layer 3 H+CNOT**: Final H+CNOT layer completes the uniform mixing. The symmetric ring structure across all three layers yields equal probability 1/16 for each of the 16 basis states |0000⟩ through |1111⟩, confirmed by the expected measurement probabilities.

## isqTrain/2637

- task_id: `isqTrain/2637`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `boolean_logic`, `global_phase`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `793`

### Prompt

Will these two quantum programs produce identical measurement outcomes?

```isq
import std;
qbit q[3];

procedure main() {
    // Encode a = 3: both bits are 1
    X(q[0]);
    X(q[1]);
    // Equality check: a == 3 when both bits are 1
    // Toffoli gate acts as AND on the two input bits
    Toffoli(q[0], q[1], q[2]);
    // Measure the equality flag
    M(q[2]);
}

```

vs.

```isq
import std;
qbit q[3];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // Encode a = 3: both bits are 1
    X(q[0]);
    X(q[1]);
    // Equality check: a == 3 when both bits are 1
    // Toffoli gate acts as AND on the two input bits
    Toffoli(q[0], q[1], q[2]);
    // Measure the equality flag
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis

1. **Program A**: Initializes |000⟩, applies X to q[0] and q[1] producing |110⟩, then Toffoli(q[0], q[1], q[2]) flips q[2] since both controls are |1⟩, yielding |111⟩.

2. **Program B**: Same operations as A, preceded by GPhase(0.0) which applies a global phase of e^(i·0) = 1 (identity).

3. **Key difference**: Program B adds GPhase(0.0), a trivial global phase of zero.

4. **Measurement probabilities**: GPhase(0.0) is the identity operation, so both programs produce the identical final state |111⟩. Measurement of q[2] yields 1 with probability 1 in both cases.

5. **Verdict**: Equivalent: True

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqExpand/algo/98

- task_id: `isqExpand/algo/98`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `phase_manipulation`, `basis_change`
- source: `isq_expansion`
- dataset_index: `4508`

### Prompt

实现以下量子计算任务（使用isQ）：implementing the Bernstein-Vazirani algorithm to find the hidden string s=110 (3 bits). Use q[0],q[1],q[2] as input qubits and q[3] as the ancilla. The oracle implements f(x) = s*x mod 2 = x0 XOR x1. Measure only the input register q[0], q[1], q[2].

### Chain-of-thought reasoning

## Reasoning
Goal: BV for s=110. s[0]=1, s[1]=1, s[2]=0.

f(x) = x0 XOR x1. Oracle: CNOT(q[0],q[3]) + CNOT(q[1],q[3]).

1. X(q[3]), H on all 4
2. Oracle: phase kickback (-1)^{x0+x1}
3. H on input: |110>

|110> = index 6. Expected: [0,0,0,0,0,0,1,0]

## isqTrain/885

- task_id: `isqTrain/885`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `774`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[7];

procedure main() {
    // Encode x = [1, 0, 1]
    X(q[0]); X(q[2]);
    // Encode y = [1, 1, 0]
    X(q[3]); X(q[4]);
    // Term 0: x[0]*y[0] XOR into q[6]
    ctrl ctrl X(q[0], q[3], q[6]);
    // Term 1: x[1]*y[1] XOR into q[6]
    ctrl ctrl X(q[1], q[4], q[6]);
    // Term 2: x[2]*y[2] XOR into q[6]
    ctrl ctrl X(q[2], q[5], q[6]);
    // IP = 1 XOR 0 XOR 0 = 1
    M(q[6]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict the probability distribution of a given isQ program.
    *   Input: An isQ program computing an inner product-like function using a series of Toffoli gates.
    *   Output: A concise step-by-step reasoning starting with "## Circuit Analysis" and ending with the probability distribution.
    *   Constraints: 3-8 lines for simple, up to 15 for complex. No code blocks. Specific format requested.

2.  **Analyze the isQ Code:**
    *   7 qubits: `q[0]` to `q[6]`. Initial state $|0\rangle^{\otimes 7}$.
    *   Encoding `x = [1, 0, 1]`: `X(q[0])`, `X(q[2])`. `q[0]` becomes 1, `q[1]` remains 0, `q[2]` becomes 1.
    *   Encoding `y = [1, 1, 0]`: `X(q[3])`, `X(q[4])`. `q[3]` becomes 1, `q[4]` becomes 1, `q[5]` remains 0.
    *   Toffoli 1: `ctrl ctrl X(q[0], q[3], q[6])`. `q[0]=1` and `q[3]=1` -> `q[6]` flips to 1.
    *   Toffoli 2: `ctrl ctrl X(q[1], q[4], q[6])`. `q[1]=0` and `q[4]=1` -> no flip.
    *   Toffoli 3: `ctrl ctrl X(q[2], q[5], q[6])`. `q[2]=1` and `q[5]=0` -> no flip.
    *   Final state of `q[6]`: 1.
    *   Measurement: `M(q[6])`.

3.  **Formulate the Reasoning:**
    *   Initial state: $|0000000\rangle$.
    *   X gates set `q[0]`, `q[2]` to $|1\rangle$ (encoding `x=101`) and `q[3]`, `q[4]` to $|1\rangle$ (encoding `y=110`).
    *   State becomes $|1011110\rangle$ (Wait: $q_0=1, q_1=0, q_2=1, q_3=1, q_4=1, q_5=0, q_6=0$).
    *   Toffoli on $q_0, q_3, q_6$: both controls are $|1\rangle$, so $q_6$ flips to $|1\rangle$.
    *   Toffoli on $q_1, q_4, q_6$: $q_1$ is $|0\rangle$, so no flip.
    *   Toffoli on $q_2, q_5, q_6$: $q_5$ is $|0\rangle$, so no flip.
    *   Final state of $q_6$ is $|1\rangle$.
    *   Measurement of `q[6]` yields 1 with 100% probability.

4.  **Refine to Constraints (3-8 lines):**
    *   Start with "## Circuit Analysis".
    *   Keep it concise.
    *   Conclude with "Predicted probability distribution: {|1>: 1.0}" (or similar based on the reference `{|1>: 1.0}`).

5.  **Drafting the Output:**
    ## Circuit Analysis
    1. The circuit initializes 7 qubits to $|0000000\rangle$.
    2. X gates encode inputs x=[1,0,1] into `q[0,1,2]` and y=[1,1,0] into `q[3,4,5]`, yielding the state $|1011100\rangle$.
    3. The first Toffoli gate (`ctrl ctrl X`) targets `q[6]` with controls `q[0]` and `q[3]`. Since both are $|1\rangle$, `q[6]` flips to $|1\rangle$.
    4. The second Toffoli gate targets `q[6]` with controls `q[1]` and `q[4]`. `q[1]` is $|0\rangle$, so no flip occurs.
    5. The

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqEval/256. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3054

- task_id: `isqTrain/3054`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`
- source: `isq_train_cot`
- dataset_index: `5285`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[3];
procedure main() {
    X(q[1]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state of the 3-qubit system is |000>.
2. The gate X(q[1]) flips the state of q[1], resulting in the state |010>.
3. Measurements M(q[0]), M(q[1]), and M(q[2]) are performed.
4. The system is in the exact state |010>, so the measurement outcome is deterministically 010.

Predicted probability distribution: {'010': 1.0}

### Reference answer

{'predicted_probs': {'010': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

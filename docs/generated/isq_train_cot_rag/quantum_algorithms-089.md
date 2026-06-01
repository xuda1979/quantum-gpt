# ISQ training COT RAG corpus: quantum_algorithms shard 89

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4385

- task_id: `isqTrain/4385`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3934`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[2];

// Wrap Z in a procedure for controlled application
procedure my_z(qbit a) {
    Z(a);
} deriving gate

procedure main() {
    // Prepare uniform superposition
    H(q[0]); H(q[1]);
    // Phase oracle: flip phase of |11>
    ctrl my_z(q[0], q[1]);
    // Measurement sees uniform distribution (phase invisible)
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initialization**: The 2-qubit system starts in the ground state $|00\rangle$.
2. **Superposition**: Applying Hadamard gates to both qubits creates a uniform superposition: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
3. **Phase Oracle**: The `ctrl my_z(q[0], q[1])` gate acts as a controlled-Z (CZ). It flips the phase of the $|11\rangle$ state, changing the state to $\frac{1}{2}(|00

### Reference answer

{'predicted_probs': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.2500, P(|01>) = 0.2500, P(|10>) = 0.2500, P(|11>) = 0.2500.'}

## isqTrain/772

- task_id: `isqTrain/772`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `1003`

### Prompt

Implement the following in isQ: implements the weighted_adder pattern but with a different initial state preparation (flip q[[0, 1, 2]] -> q[4]).

### Chain-of-thought reasoning

## Reasoning
The circuit implements a half-adder with carry propagation for inputs q[0], q[1], q[2] and accumulates the sum in q[3] with carry in q[4], starting with q[4]=|1⟩.

**Qubits**: 5 qubits (q[0]-q[4]); q[3] (sum) and q[4] (carry) are measured.

**State evolution**:
- Initial: |00001⟩ (X on q[4])
- CNOT(q[0], q[3]): q[0]=|0⟩ → no change → |00001⟩
- Toffoli(q[1], q[3], q[4]): q[1]=q[3]=|0⟩ → no change → |00001⟩
- CNOT(q[1], q[3]): q[1]=|0⟩ → no change → |00001⟩
- Toffoli(q[2], q[3], q[4]): q[2]=q[3]=|0⟩ → no change → |00001⟩
- CNOT(q[2], q[3]): q[2]=|0⟩ → no change → |00001⟩

**Final measurement**: q[3]=0 (sum=0), q[4]=1 (carry=1) → |01⟩ with probability 1.0. Since all inputs are |0⟩ but q[4] starts as |1⟩, the adder doesn't change the carry qubit, yielding |01⟩.

## isqTrain/1339

- task_id: `isqTrain/1339`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `qft_based_arithmetic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3148`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[2];

procedure qft2(qbit q0, qbit q1) {
    H(q0);
    ctrl Rz(pi/3.0, q1, q0);
    H(q1);

    CNOT(q0, q1);
    CNOT(q1, q0);
    CNOT(q0, q1);
}

procedure main() {
    X(q[0]); X(q[1]);
    qft2(q[0], q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

Let me analyze this isQ program step by step.

The program:
1. Initializes 2 qubits q[0] and q[1]
2. Applies X to both qubits, starting from |11>
3. Calls qft2(q[0], q[1])
4. Measures both qubits

Let me trace through the qft2 procedure:

Starting state: |11> (after X gates on both qubits)

In qft2(q0=q[0], q1=q[1]):
1. H(q0): H on q[0]
2. ctrl Rz(pi/3, q1, q0): controlled-Rz with q[1] as control, q[0] as target
3. H(q1): H on q[1]
4. CNOT(q0, q1): CNOT with q[0] control, q[1] target
5. CNOT(q1, q0): CNOT with q[1] control, q[0] target
6. CNOT(q0, q1): CNOT with q[0] control, q[1] target

Let me work through this more carefully.

Starting state: |11>

Step 1: H(q0) = H(q[0])
H|1> = (|0> - |1>)/√2 = |->
State: |->|1> = (|01> - |11>)/√2

Step 2: ctrl Rz(pi/3, q1, q0) - controlled Rz with q1 as control and q0 as target
This applies Rz(π/3) to q0 when q1 is |1>.

Rz(π/3) = [[1, 0], [0, e^(iπ/3)]]

So when q1=1, q0 gets Rz(π/3) applied.

State: (|01> - e^(iπ/3)|11>)/√2

Step 3: H(q1)
H on q[1]:
|01> component: |0>(H|1>) = |0>(|0>-|1>)/√2 = (|00>-|01>)/√2
e^(iπ/3)|11> component: e^(iπ/3)|1>(H|1>) = e^(iπ/3)|1>(|0>-|1>)/√2 = e^(iπ/3)(|10>-|11>)/√2

State: [(|00>-|01>) - e^(iπ/3)(|10>-|11>)]/2

Step 4: CNOT(q0, q1) - q0 control, q1 target
|00> → |00>
|01> → |01>
|10> → |11>
|11> → |10>

State: [(|00>-|01>) - e^(iπ/3)(|11>-|10>)]/2
= [(|00>-|01>) + e^(iπ/3)(|10>-|11>)]/2

Step 5: CNOT(q1, q0) - q1 control, q0 target
|00> → |00>
|01> → |11>
|10> → |10>
|11> → |01>

State: [(|00>-|11>) + e^(iπ/3)(|10>-|01>)]/2
= [|00> - |11> + e^(iπ/3)|10> - e^(iπ/3)|01>]/2

Step 6: CNOT(q0, q1) - q0 control, q1 target
|00> → |00>
|01> → |01>
|10> → |11>
|11> → |10>

State: [|00> - |10> + e^(iπ/3)|11> - e^(iπ/3)|01>]/2
= [|00> - e^(iπ/3)|01> - |10> + e^(iπ/3)|11>]/2

Wait, let me recalculate. The three CNOT gates form a swap operation (three-CNOT decomposition):
CNOT(q0, q1); CNOT(q1, q0); CNOT(q0, q1) = swap(q0, q1) via three CNOTs

So after step 3, we apply swap(q0, q1) via three CNOTs.

State after step 3: [(|00>-|01>) - e^(iπ/3)(|10>-|11>)]/2

swap (three-CNOT decomposition) swaps q0 and q1:
|00> → |00>
|01> → |10>
|10> → |01>
|11> → |11>

State: [(|00>-|10>)

### Reference answer

{'predicted_probs': {'0': 0.25, '1': 0.25, '2': 0.25, '3': 0.25}, 'explanation': 'Parametric variant of isqEval/487. Dimension: param_variant: pi2_to_pi3.'}

## isqTrain/2075

- task_id: `isqTrain/2075`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2220`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit x[1];
qbit w[2];
procedure main() {
    X(w[0]);
    H(x[0]);
    ctrl SWAP(x[0], w[0], w[1]);
    M(x[0]); M(w[0]); M(w[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Input: An isQ program.
    *   Task: Predict measurement probabilities.
    *   Output Format: "## Circuit Analysis", step-by-step reasoning using Dirac notation, concise (3-15 lines), end with predicted probabilities.
    *   System prompt specifics: 3-8 lines for simple circuits, up to 15 for complex. Use Dirac notation.

2.  **Analyze the isQ Program:**
    *   `qbit x[1];` -> qubit $x_0$
    *   `qbit w[2];` -> qubits $w_0, w_1$
    *   Initial state: $|x_0, w_0, w_1\rangle = |0, 0, 0\rangle$
    *   `X(w[0]);` -> $w_0$ becomes $|1\rangle$. State: $|0, 1, 0\rangle$
    *   `H(x[0]);` -> $x_0$ becomes $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$. State: $\frac{1}{\sqrt{2}}(|0, 1, 0\rangle + |1, 1, 0\rangle)$
    *   `ctrl swap (three-CNOT decomposition)(x[0], w[0], w[1]);` -> Controlled-swap (three-CNOT decomposition) (controlled-swap operation (three-CNOT decomposition)). If $x_0 = |1\rangle$, swap $w_0$ and $w_1$.
        *   $|0, 1, 0\rangle$ remains $|0, 1, 0\rangle$
        *   $|1, 1, 0\rangle$ becomes $|1, 0, 1\rangle$
        *   State: $\frac{1}{\sqrt{2}}(|0, 1, 0\rangle + |1, 0, 1\rangle)$
    *   Measurements: `M(x[0])`, `M(w[0])`, `M(w[1])`. Order of measurement bitstring: $x_0$ is the most significant bit (index 2), $w_0$ is index 1, $w_1$ is index 0. Wait, isQ documentation says "earlier measured qubit = higher bit". Let's assume the bitstring is $x_0 w_0 w_1$.
        *   $x_0=0 \implies w_0=1, w_1=0 \implies 010$
        *   $x_0=1 \implies w_0=0, w_1=1 \implies 101$

3.  **Draft the response:**
    *   Initial state $|x_0, w_0, w_1\rangle = |000\rangle$.
    *   `X(w[0])` changes $w_0$ to $|1\rangle$, yielding $|010\rangle$.
    *   `H(x[0])` creates superposition: $\frac{1}{\sqrt{2}}(|010\rangle + |110\rangle)$.
    *   `ctrl swap (three-CNOT decomposition)` flips $w_0$ and $w_1$ when $x_0$ is $|1\rangle$, yielding $\frac{1}{\sqrt{2}}(|010\rangle + |101\rangle)$.
    *   Measuring $x_0, w_0, w_1$ gives equal probability for states $|010\rangle$ and $|101\rangle$.

4.  **Refine to meet constraints:**
    *   Concise: 5-6 lines.
    *   Dirac notation used.
    *   Ends with probabilities.

    *Drafting text:*
    ## Circuit Analysis
    1. Initial state is $|x_0, w_0, w_1\rangle = |000\rangle$.
    2. Applying `X(w[0])` flips the second qubit to $|1\rangle$, giving $|010\rangle$.
    3. The `H(x[0])` gate puts the first qubit into superposition: $\frac{1}{\sqrt{2}}(|010\rangle + |110\rangle)$.
    4. The `ctrl swap (three-CNOT decomposition)(x[0], w[0], w[1])` gate swaps $w_0$ and $w_1$ when $x_0$ is $|1\rangle$, resulting in $\frac{1}{\sqrt{2}}(|010\rangle + |101\rangle)$.
    5. Measuring yields 50% probability

### Reference answer

{'predicted_probs': {'010': 0.5, '101': 0.5}, 'explanation': 'Shor subroutine: 2^x mod 3 with 1-qubit exponent.'}

## isqTrain/1102

- task_id: `isqTrain/1102`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5631`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;

// Bernstein-Vazirani oracle: f(x) = s . x mod 2
// Hidden string s = 101 = [true, false, true]
oracle bool[1] f(bool x[3]) {
    // Inner product: x[0]*s[0] XOR x[2]*s[2]
    // s[1]=false so x[1] term vanishes
    bool res[] = [x[0] != x[2]];
    return res;
}

// 3-qubit input register
qbit q[3];
// Ancilla for phase kickback
qbit anc[1];

procedure main() {
    // Ancilla in |-> state
    X(anc[0]);
    H(anc[0]);
    // Uniform superposition on input
    H(q[0]); H(q[1]); H(q[2]);
    // Single oracle query reveals hidden string
    f(q, anc);
    // Hadamard decodes the hidden string
    H(q[0]); H(q[1]); H(q[2]);
    // Measurement yields s = 101
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit implements the Bernstein-Vazirani algorithm to find a hidden string $s$ using an oracle that computes $f(x) = x_0 \oplus x_2$.
2. Initial state is $|0000\rangle$. An X and H gate prepare the ancilla in $|-\rangle$, and H gates on the input register create a uniform superposition: $\frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle \otimes |-\rangle$.
3. The oracle $f(q, anc)$ uses phase kickback to apply a phase $(-1)^{f(x)}$, transforming the state to $\frac{1}{\sqrt{8}} \sum_{x

### Reference answer

{'predicted_probs': {'5': 1.0}, 'explanation': 'Parametric variant of isqEval/433. Dimension: predict probabilities for reference circuit.'}

## isqTrain/798

- task_id: `isqTrain/798`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4554`

### Prompt

Create an isQ quantum circuit that implements the quantum_multiplier pattern. Include explicit identity operations in the circuit (H-H pair before M(q[3])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a quantum multiplier computing 1 × 3 = 3, storing the product's LSB in q[3] and demonstrating H-H gate cancellation.
2. **Qubits**: 4 qubits (q[0]-q[3]); only q[3] is measured.
3. **State evolution**:
   - Initial: |0000⟩
   - X(q[0]): |1000⟩ — sets multiplier a=1
   - X(q[1]), X(q[2]): |1110⟩ — sets multiplicand b=3 (binary 11)
   - Toffoli(q[0], q[1], q[3]): q[0]∧q[1]=1 → flips q[3]: |1111⟩ (LSB of 1×3=1)
   - H(q[3]): (|0⟩-|1⟩)/√2 on q[3]
   - H(q[3]): H²=I, returns q[3] to |1⟩
4. **Probabilities**: H-H cancels (identity), so M(q[3]) yields {|1⟩: 1.0}.

## isqQA/quantum_algorithms/133_isq_implementation

- task_id: `isqQA/quantum_algorithms/133_isq_implementation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_implementation`, `algorithm`, `量子比较器`
- source: `qa_pipeline`
- dataset_index: `3954`

### Prompt

请使用isQ语言编写一个完整的量子比较器电路，用于比较两个2位二进制数 A 和 B 的大小，并在目标辅助比特上输出 A > B 的结果。要求在计算完成后必须利用 uncomputation（逆向计算）原理清理所有使用过的辅助比特，使其恢复到初始态 |0⟩，以避免留下不必要的量子纠缠。请提供完整的isQ代码并逐行注释其背后的逻辑。

### Reference answer

<think>
首先，将经典的比较逻辑转化为布尔表达式。根据高位优先原则，比较两个2位二进制数A和B的逻辑可拆解为：(a1 > b1) OR ((a1 == b1) AND (a0 > b0))。

其次，在量子电路中需引入辅助比特暂存中间状态。分别用不同的辅助比特存储“高位大于(a1=1且b1=0)”、“高位相等”以及“低位大于”这三个子条件。这可通过多控Toffoli门结合X门（非门）来实现。随后将这些辅助比特作为控制端，利用量子门将最终的A>B结果写入目标辅助比特。

最后，为满足uncomputation（逆向计算）要求，需利用量子操作的酉性（可逆性）。在目标比特得到结果后，严格按原计算电路的逆序对辅助比特执行逆运算。此过程能将辅助比特与系统解纠缠并恢复至初始态|0⟩，同时保留目标比特上的有效测量结果。
</think>

在量子计算中，由于量子门操作的酉性，我们在设计电路时必须保证整个过程是可逆的。当我们使用辅助比特来暂存中间计算结果时，如果不将这些辅助比特恢复到初始的 |0⟩ 态，它们就会与我们的目标比特产生量子纠缠，从而破坏最终的测量结果或干扰后续的量子算法。这种恢复辅助比特的技术被称为 uncomputation。

为了比较两个2位量子寄存器 A (a1 a0) 和 B (b1 b0) 的大小，判断是否满足 A > B，我们可以从高位到低位进行判断。逻辑表达式可以拆解为：
A > B = (a1 > b1) OR ((a1 == b1) AND (a0 > b0))

在量子电路中，我们可以分别计算出 a1 > b1 （即 a1=1, b1=0）和 a0 > b0 （即 a0=1, b0=0）的状态，将其存入辅助比特，并利用 Toffoli 门组合条件。以下是满足要求的 isQ 完整代码实现：

```isq
import std;

// 声明用于比较的输入量子寄存器 a (2位) 和 b (2位)
qbit a[2];
qbit b[2];

// 声明目标比特，用于存储最终 A > B 的比较结果
qbit c_gt;

// 声明辅助比特数组 eq[2]，用于暂存逐位比较的结果 (a_i > b_i)
qbit eq[2];

// 声明辅助比特 e1，用于判断高位是否相等 (a1 == b1)
qbit e1;

procedure main() {
    // ================= 前向计算阶段 =================

    // 1. 计算低位 a[0] > b[0] 的结果并存入 eq[0]
    // 如果 a[0]=1 且 b[0]=0，我们希望 eq[0] 被翻转为 1
    X(b[0]);                 // 将 b[0] 翻转，此时当原 b[0]=0 时，现在的 b[0]=1
    Toffoli(a[0], b[0], eq[0]); // 如果 a[0]=1 且翻转后的 b[0]=1 (即原 b[0]=0)，则 eq[0] 翻转为 1
    X(b[0]);                 // 恢复 b[0] 的状态，保证输入寄存器不被破坏

    // 2. 计算高位 a[1] > b[1] 的结果并存入 eq[1]
    // 逻辑与低位完全相同
    X(b[1]);                 // 将 b[1] 翻转
    Toffoli(a[1], b[1], eq[1]); // 如果 a[1]=1 且原 b[1]=0，eq[1] 翻转为 1
    X(b[1]);                 // 恢复 b[1] 的状态

    // 3. 如果高位 a[1] > b[1] (即 eq[1]=1)，则可以直接得出 A > B 的结论
    // 将目标比特 c_gt 初始化为 0，若 eq[1] 为 1，则将其翻转
    CNOT(eq[1], c_gt);      

    // 4. 计算高位 a[1] 是否等于 b[1]，结果存入 e1
    CNOT(a[1], e1);         // 将 a[1] 异或到 e1 中
    CNOT(b[1], e1);         // 将 b[1] 异或到 e1 中，此时 e1 存储的是 a[1] XOR b[1]
    X(e1);                  // 取反，此时 e1 存储的是 NOT (a[1] XOR b[1])，即 a[1] == b[1] 时 e1=1

    // 5. 如果高位相等 (e1=1) 且低位 a[0] > b[0] (eq[0]=1)，则同样满足 A > B
    Toffoli(e1, eq[0], c_gt); // 如果高位相等且低位大于，翻转目标比特 c_gt

    // 注意：此时 c_gt 中已经正确保存了 A > B 的结果。接下来必须进行 uncomputation 清理辅助比特。

    // ================= 逆向清理阶段 =================

    // 6. 恢复 e1 辅助比特
    X(e1);                  // 再次取反恢复
    CNOT(b[1], e1);         // 再次异或 b[1] 恢复
    CNOT(a[1], e1);         // 再次异或 a[1]，此时 e1 成功恢复到初始的 |0⟩ 态

    // 7. 恢复 eq[1] 辅助比特
    X(b[1]);                // 翻转 b[1]
    Toffoli(a[1], b[1], eq[1]); // 逆转刚才的 Toffoli 门
    X(b[1]);                // 恢复 b[1]，此时 eq[1] 成功恢复到 |0⟩ 态

    // 8. 恢复 eq[0] 辅助比特
    X(b[0]);                // 翻转 b[0]
    Toffoli(a[0], b[0], eq[0]); // 逆转刚才的 Toffoli 门
    X(b[0]);                // 恢复 b[0]，此时 eq[0] 成功恢复到 |0⟩ 态

    // 经过上述操作，只有 c_gt 被永久改变，保存了 a > b 的布尔值。
    // 其他所有的辅助比特 均解开了与目标比特的纠缠，恢复到了干净的 |0⟩ 态。
}
```

## isqTrain/3949

- task_id: `isqTrain/3949`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `5038`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```
import std;
// QFT on 4 qubits with input state |0011>
qbit q[4];

procedure main() {
    // Prepare input state |0011>
    X(q[2]);
    X(q[3]);

    // QFT stage for qubit 0
    H(q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 16.0, q[3], q[0]);
    // QFT stage for qubit 1
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[3], q[1]);
    // QFT stage for qubit 2
    H(q[2]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[3], q[2]);
    // QFT stage for qubit 3
    H(q[3]);
    // Swap q[0] and q[3]
    CZ(q[0], q[3]);
    CNOT(q[3], q[0]);
    CNOT(q[0], q[3]);
    // Swap q[1] and q[2]
    CNOT(q[1], q[2]);
    CNOT(q[2], q[1]);
    CNOT(q[1], q[2]);
    // Measure after QFT
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **The bug**: In the swap operation between q[0] and q[3], the first gate is `CZ(q[0], q[3])` instead of `CNOT(q[0], q[3])`. A CZ gate applies a phase (Z gate) to the target when the control is |1⟩, but does NOT flip the target qubit. A proper swap requires three CNOT gates to actually exchange the quantum states of the two qubits.

2. **The fix**: Replace `CZ(q[0], q[3])` with `CNOT(q[0], q[3])` so the swap is correctly implemented as three CNOT gates:
   - CNOT(q[0], q[3])
   - CNOT(q[3], q[0])
   - CNOT(q[0], q[3])

3. **State evolution of corrected circuit**:
   - Initial: |0000⟩
   - After X(q[2]), X(q[3]): |0011⟩ (represents integer 3)
   - After QFT stages (H + controlled-Rz rotations): Produces QFT|3⟩ with qubits in bit-reversed order
   - After swap(q[0], q[3]) and swap(q[1], q[2]): Corrects bit order
   - Final state: 1/4 Σⱼ₌₀¹⁵ e^(2πi·3·j/16) |j⟩ — an equal superposition over all 16 basis states
   - Measurement yields each outcome with probability |1/4|² = 0.0625, confirming the uniform distribution.

## isqTrain/4839

- task_id: `isqTrain/4839`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `quantum_counting`, `interference`
- source: `isq_train_cot`
- dataset_index: `4525`

### Prompt

请用isQ语言编写一个量子电路：implementing just the diffusion operator for 2 qubits. Apply H, X, CZ, X, H to both qubits. Start from |00> state (no initial H). Measure both.

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

Initial state: |00>

Step 1: H on both qubits
H|0⟩ = |+⟩ = (|0⟩ + |1⟩)/√2
So H⊗H|00⟩ = |+⟩|+⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

Step 2: X on both qubits
X|0⟩ = |1⟩, X|1⟩ = |0⟩
X⊗X(|00⟩ + |01⟩ + |10⟩ + |11⟩)/2 = (|11⟩ + |10⟩ + |01⟩ + |00⟩)/2

Step 3: CZ on both qubits
CZ applies a phase of -1 when both are |1⟩
CZ(|11⟩ + |10⟩ + |01⟩ + |00⟩)/2 = (-|11⟩ + |10⟩ + |01⟩ + |00⟩)/2

Step 4: X on both qubits again
X⊗X(-|11⟩ + |10⟩ + |01⟩ + |00⟩)/2 = (-|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

Step 5: H on both qubits
H⊗H(-|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

Let me compute this:
H⊗H|00⟩ = |++⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
H⊗H|01⟩ = |+−⟩ = (|00⟩ - |01⟩ + |10⟩ - |11⟩)/2
H⊗H|10⟩ = |−+⟩ = (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2
H⊗H|11⟩ = |−−⟩ = (|00⟩ - |01⟩ - |10⟩ + |11⟩)/2

So:
H⊗H(-|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
= (-|++⟩ + |+−⟩ + |−+⟩ + |−−⟩)/2
= [-(|00⟩ + |01⟩ + |10⟩ + |11⟩) + (|00⟩ - |01⟩ + |10⟩ - |11⟩) + (|00⟩ + |01⟩ - |10⟩ - |11⟩) + (|00⟩ - |01⟩ - |10⟩ + |11⟩)]/4
= [|00⟩(-1+1+1+1) + |01⟩(-1-1+1-1) + |10⟩(-1+1-1-1) + |11⟩(-1-1-1+1)]/4
= [|00⟩(2) + |01⟩(-2) + |10⟩(-2) + |11⟩(-2)]/4
= (|00⟩ - |01⟩ - |10⟩ - |11⟩)/2

Hmm, but The predicted output equal probabilities for all states. Let me recheck.

Wait, Analyzing the circuit requirements again - it has H, H first, then X, X, then CZ, then X, X, then H, H.

Let me redo:
Initial: |00⟩
After H, H: |++⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
After X, X: (|11⟩ + |10⟩ + |01⟩ + |00⟩)/2 (same state, just reordered)
After CZ: (-|11⟩ + |10⟩ + |01⟩ + |00⟩)/2
After X, X: (-|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
After H, H: Let me compute more carefully

Actually, let me just compute H⊗H applied to each basis state:

H|0⟩ = (|0⟩ + |1⟩)/√2
H|1⟩ = (|0⟩ - |1⟩)/√2

H⊗H|00⟩ = (|0⟩ + |1⟩)(|0⟩ + |1⟩)/2 = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
H⊗H|01⟩ = (|0⟩ + |1⟩)(|0⟩ - |1⟩)/2 = (|00⟩ - |01⟩ + |10⟩ - |11⟩)/2
H⊗H|10⟩ = (|0⟩ - |1⟩)(|0⟩ + |1⟩)/2 = (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2
H⊗H|11⟩ = (|

## isqTrain/822

- task_id: `isqTrain/822`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `multi_controlled_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2369`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[3];

procedure main() {
    // Put both input bits in uniform superposition
    H(q[0]);
    H(q[1]);
    // Evaluate bilinear form: f(x0,x1) = x0 AND x1
    // Toffoli gate computes the AND function
    Toffoli(q[0], q[1], q[2]);
    // Measure the result qubit
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The initial 3-qubit state is |000⟩ for q[2], q[1], q[0].
2. Applying H(q[0]) and H(q[1]) puts the first two qubits into a uniform superposition: 0.5(|00⟩ + |01⟩ + |10⟩ + |11⟩) ⊗ |0⟩.
3.

### Reference answer

{'predicted_probs': {'0': 0.75, '1': 0.25}, 'explanation': 'Parametric variant of isqEval/289. Dimension: predict probabilities for reference circuit.'}

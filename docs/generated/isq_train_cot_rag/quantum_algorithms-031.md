# ISQ training COT RAG corpus: quantum_algorithms shard 31

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1148

- task_id: `isqTrain/1148`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `data_encoding_qml`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `873`

### Prompt

Write an isQ program that implements the data_encoding pattern with modified rotation parameters (num_pi2_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit has 2 qubits, both measured.

Step 1: Initial state is |00>

Step 2: Apply H(q[0]) and H(q[1])
State becomes |++> = (1/2)(|00> + |01> + |10> + |11>)

Step 3: Apply Rz(0.78539816339745, q[0]) - this is approximately π/4
Rz(θ)|0> = e^{-iθ/2}|0>, Rz(θ)|1> = e^{iθ/2}|1>

So Rz(π/4) on q[0]:
State becomes (1/2)(e^{-iπ/8}|00> + e^{-iπ/8}|01> + e^{iπ/8}|10> + e^{iπ/8}|11>)

Step 4: Apply Rz(1.04719755119660, q[1]) - this is approximately π/3
State becomes (1/2)(e^{-iπ/8}e^{-iπ/6}|00> + e^{-iπ/8}e^{iπ/6}|01> + e^{iπ/8}e^{-iπ/6}|10> + e^{iπ/8}e^{iπ/6}|11>)

= (1/2)(e^{-i7π/24}|00> + e^{iπ/24}|01> + e^{iπ/24}|10> + e^{i7π/24}|11>)

Wait, let me recalculate:
- |00>: e^{-iπ/8} * e^{-iπ/6} = e^{-i(3π/24 + 4π/24)} = e^{-i7π/24}
- |01>: e^{-iπ/8} * e^{iπ/6} = e^{-i(3π/24 - 4π/24)} = e^{iπ/24}
- |10>: e^{iπ/8} * e^{-iπ/6} = e^{i(3π/24 - 4π/24)} = e^{-iπ/24}
- |11>: e^{iπ/8} * e^{iπ/6} = e^{i(3π/24 + 4π/24)} = e^{i7π/24}

So state = (1/2)(e^{-i7π/24}|00> + e^{iπ/24}|01> + e^{-iπ/24}|10> + e^{i7π/24}|11>)

Step 5: Apply H(q[0]) and H(q[1]) again

H|0> = |+> = (|0>+|1>)/√2
H|1> = |-> = (|0>-|1>)/√2

So H⊗H applied to each basis state:
|00> → (1/2)(|00>+|01>+|10>+|11>)
|01> → (1/2)(|00>-|01>+|10>-|11>)
|10> → (1/2)(|00>+|01>-|10>-|11>)
|11> → (1/2)(|00>-|01>-|10>+|11>)

Final state = (1/4)[e^{-i7π/24}(|00>+|01>+|10>+|11>) + e^{iπ/24}(|00>-|01>+|10>-|11>) + e^{-iπ/24}(|00>+|01>-|10>-|11>) + e^{i7π/24}(|00>-|01>-|10>+|11>)]

Let me compute the amplitude for each basis state:

|00>: (1/4)(e^{-i7π/24} + e^{iπ/24} + e^{-iπ/24} + e^{i7π/24})

Let me compute this numerically:
- e^{-i7π/24} = cos(7π/24) - i*sin(7π/24) ≈ 0.3827 - i*0.9239
- e^{iπ/24} = cos(π/24) + i*sin(π/24) ≈ 0.9914 + i*0.1305
- e^{-iπ/24} = cos(π/24) - i*sin(π/24) ≈ 0.9914 - i*0.1305
- e^{i7π/24} = cos(7π/24) + i*sin

## isqTrain/1334

- task_id: `isqTrain/1334`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5238`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;

qbit x[2];
qbit y[1];

procedure main() {
    X(y[0]);
    H(x[0]); H(y[0]);

    X(y[0]);

    H(x[0]);
    M(x[0]); M(x[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict measurement probabilities for an isQ quantum program.
    *   Input: An isQ program with 3 qubits (`x[0]`, `x[1]`, `y[0]`), but only `x[0]` and `x[1]` are measured.
    *   Format Requirements: "## Circuit Analysis", concise step-by-step reasoning, Dirac notation, NO code blocks, end with predicted probability distribution.
    *   isQ Syntax: Standard quantum gates.

2.  **Analyze the isQ Program:**
    

3.  **Trace Quantum State Evolution:**
    *   Initial state: $|x_0 x_1 y_0\rangle = |000\rangle$
    *   `X(y[0])`: State becomes $|001\rangle$
    *   `H(x[0])`: State becomes $\frac{1}{\sqrt{2}}(|000\rangle + |100\rangle)$
    *   `H(y[0])`: State becomes $\frac{1}{\sqrt{2}}(|00\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) + |10\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle))$ -> Wait, let's trace $y_0$ properly.
        Current state before H(y[0]) is $\frac{1}{\sqrt{2}}(|000\rangle + |100\rangle)$.
        Apply H on y[0]: $H|0\rangle = |+\rangle$, $H|0\rangle = |+\rangle$.
        So state is $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle) \otimes |+\rangle$
    *   `X(y[0])`: Applies X to y[0].
        $|+\rangle$ goes to $X|+\rangle = \frac{1}{\sqrt{2}}(|1\rangle + |0\rangle) = |+\rangle$.
        So state remains $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle) \otimes |+\rangle$
    *   `H(x[0])`: Applies H on x[0].
        x[0] is in state $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$ (ignoring x[1], y[0] tensor product).
        $H \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = H|+\rangle = |0\rangle$.
        So the overall state becomes $|0\rangle_{x_0} \otimes |0\rangle_{x_1} \otimes |+\rangle_{y_0} = |000\rangle \otimes |+\rangle = \frac{1}{\sqrt{2}}(|0000\rangle + |0001\rangle)$ (if mapping to full 3 qubit space).
        Let's be precise:
        x[0] starts at |0>.
        H(x[0]) -> |+>
        X(y[0]) -> |1>
        H(y[0]) -> |->
        X(y[0]) -> |1> (Wait, X|- > = -|->)
        H(x[0]) -> |0>
        Let's re-evaluate.
        Initial: $|0\rangle_{x_0} |0\rangle_{x_1} |0\rangle_{y_0}$
        `X(y[0])`: $|0\rangle |0\rangle |1\rangle$
        `H(x[0])`: $\frac{1}{\sqrt{2}}(|0\rangle+|1\rangle) |0\rangle |1\rangle$
        `H(y[0])`: $\frac{1}{\sqrt{2}}(|0\rangle+|1\rangle) |0\rangle \frac{1}{\sqrt{2}}(|0\rangle-|1\rangle)$
        `X(y[

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'Parametric variant of isqEval/483. Dimension: qubit_variant: x[1] -> x[2].'}

## isqTrain/3972

- task_id: `isqTrain/3972`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4401`

### Prompt

这段isQ代码有bug，帮我找出并修复：

```
import std;
// Phase kickback with Rz(3pi/4)
qbit q[2];

procedure main() {
    // Control in superposition
    H(q[0]);
    // Target in |1> eigenstate
    Y(q[1]);
    // Controlled Rz
    ctrl Rz(3.14159265358979 * 3.0 / 4.0, q[0], q[1]);
    // Detect phase on control
    H(q[0]);
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

Let me analyze this buggy code and the fix.

The buggy code uses `Y(q[1])` to prepare the target qubit, while the corrected version uses `X(q[1])`.

Let me trace through the state evolution for both cases to understand why.

**Corrected circuit with X(q[1]):**

1. Initial state: |00>
2. H(q[0]): |+0⟩ = (|00⟩ + |10⟩)/√2
3. X(q[1]): (|01⟩ + |11⟩)/√2
4. ctrl Rz(3π/4, q[0], q[1]): Rz applies phase rotation on target when control is |1⟩
   - Rz(θ)|0⟩ = |0⟩
   - Rz(θ)|1⟩ = e^{-iθ/2}|1⟩
   - So when control is |1⟩ and target is |1⟩, the target gets phase e^{-i3π/8}
   - State: (|01⟩ + e^{-i3π/8}|11⟩)/√2
5. H(q[0]): 
   - |01⟩ → (|01⟩ + |11⟩)/√2
   - |11⟩ → (|01⟩ - |11⟩)/√2
   - So: (1/√2)[(|01⟩ + |11⟩)/√2 + e^{-i3π/8}(|01⟩ - |11⟩)/√2]
   - = (1/2)[(1 + e^{-i3π/8})|01⟩ + (1 - e^{-i3π/8})|11⟩]

   P(|01⟩) = |1 + e^{-i3π/8}|²/4 = (1 + cos(3π/8))² + sin²(3π/8))/4
   Wait, let me recalculate.
   
   |1 + e^{-i3π/8}|² = |1 + cos(3π/8) - i sin(3π/8)|² = (1+cos(3π/8))² + sin²(3π/8) = 1 + 2cos(3π/8) + cos²(3π/8) + sin²(3π/8) = 2 + 2cos(3π/8) = 2(1 + cos(3π/8))
   
   P(|01⟩) = 2(1 + cos(3π/8))/4 = (1 + cos(3π/8))/2

   cos(3π/8) ≈ cos(67.5°) ≈ 0.382683
   
   P(|01⟩) = (1 + 0.382683)/2 ≈ 0.691342 ✓
   P(|11⟩) = (1 - 0.382683)/2 ≈ 0.308658 ✓

**Buggy circuit with Y(q[1]):**

Y gate: Y = [[0,-i],[i,0]]
Y|0⟩ = i|1⟩

So after step 3: (|0⟩ + |1⟩)/√2 ⊗ i|1⟩ = i(|01⟩ + |11⟩)/√2

The state is the same up to a global phase i, so the controlled-Rz would produce the same probabilities...

Wait, but The predicted output P(|01⟩) = 0.691342 and P(|11⟩) = 0.308658. With Y, the result should be the same since Y|0⟩ = i|1⟩ which is just |1⟩ up to global phase.

Hmm, let me reconsider. Maybe there's something subtle about how isQ handles the Y gate vs X gate in terms of the phase.

Actually, Y|0⟩ = i|1⟩. This introduces a global phase of i compared to X|0⟩ = |1⟩. But global phases don't affect measurement probabilities. So mathematically the two should give the same result.

Unless... the phase from Y interacts with the Rz in a way that matters?

Let me be more careful. With Y:

1. |00⟩
2. H(q[0]): |+0⟩
3. Y(q[1]): Y|0⟩ = i|1⟩ → i|+1⟩ = i(|01⟩ + |11⟩)/√2
4. ctrl Rz(3π/4, q[0], q[1]): The controlled-Rz applies e^{-iθ/2}Z... actually, Rz(θ) = e^{-iθZ/2}, so Rz(θ)|1⟩ = e^{-iθ/2}|1⟩

## isqExpand/algo/194

- task_id: `isqExpand/algo/194`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `bernstein_vazirani`, `oracle`, `hadamard`, `hidden_string`, `quantum_algorithm`
- source: `isq_expansion`
- dataset_index: `1438`

### Prompt

用isQ实现implementing the Bernstein-Vazirani algorithm to find the hidden string s=01 (2-bit). Use 3 qubits: 2 input qubits and 1 ancilla. The program should prepare the ancilla in |1⟩, apply Hadamard gates, apply the oracle (CNOT from each input qubit where s_i=1 to the ancilla), apply Hadamard to input qubits, and measure the input qubits.

### Chain-of-thought reasoning

The Bernstein-Vazirani algorithm finds a hidden binary string s by querying an oracle. For s=01 (2 bits), we use 3 qubits: q[0], q[1] as input and q[2] as ancilla. Step 1: Initialize ancilla to |1> via X(q[2]). Step 2: Apply H to all 3 qubits, creating superposition on inputs and |-> on ancilla. Step 3: Apply the oracle — since s[0]=0, no CNOT from q[0]; since s[1]=1, apply CNOT(q[1], q[2]). This encodes s into the phase. Step 4: Apply H to input qubits q[0] and q[1], which converts the phase encoding back to computational basis. Step 5: Measure q[0] and q[1]. The result is |01> with certainty, corresponding to s=01. The expected probability distribution over 2 measured qubits is [0.0, 1.0, 0.0, 0.0] for states |00>, |01>, |10>, |11>.

## isqExpand/qa/44

- task_id: `isqExpand/qa/44`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `quantum_fingerprinting`, `communication_complexity`, `swap_test`, `quantum_information_theory`, `quantum_circuit`
- source: `qa_pipeline`
- dataset_index: `2706`

### Prompt

什么是量子指纹？它在通信复杂性中有什么应用？

### Chain-of-thought reasoning

## 推理
首先，我需要明确量子指纹的核心概念及其在量子计算体系中的定位。量子指纹本质上是一种从大比特空间到小希尔伯特空间的量子态映射。接着，将背景引入到通信复杂度中，这是量子指纹最具代表性的应用场景，特别是用于解决 Equality Problem。此时需要对比经典通信复杂度的下界和量子通信的上界，以此凸显量子优势。在详细解释原理时，必须包含关键数学公式，即保真度与测量概率的关系。最后，落实到具体的落地实践，使用指定的 isQ 语言编写一段用于验证量子指纹一致性的 SWAP 测试代码，严格遵守题目要求的 import 和 ctrl 语法，并解释因为没有原生 SWAP 门而使用 CNOT 替代的逻辑。

### Reference answer

量子指纹是一种量子计算与量子信息论中的编码技术，它允许我们将一个较长的经典比特串映射为一个状态数量少得多的量子态。这种映射展现了量子力学在信息压缩方面的强大能力，并在通信复杂性领域中实现了对经典通信的指数级优势。

### 1. 量子指纹的数学定义
假设存在两个通信方 Alice 和 Bob，Alice 拥有一个 $n$-bit 的经典字符串 $x \in \{0,1\}^n$，Bob 拥有一个 $n$-bit 的经典字符串 $y \in \{0,1\}^n$。他们希望通过通信来判断各自的字符串是否相等，即解决相等性问题（Equality Problem, EQ）。

在经典通信复杂度模型中，如果双方没有共享的随机性且错误率需小于常数，判定 $x=y$ 所需的通信比特数为 $\Omega(n)$。即使允许一定的错误率和共享随机性，经典通信复杂度的下界也是 $\Omega(\sqrt{n})$。

然而，借助量子指纹技术，Alice 可以将她的 $n$-bit 字符串 $x$ 映射为一个仅包含 $O(\log n)$ 个量子比特的量子态 $|h(x)\rangle$。这个映射通常通过特定的酉变换实现，例如利用特定的哈希函数和泡利旋转，将其编码为：
$$ |h(x)\rangle = \frac{1}{\sqrt{m}} \sum_{i=1}^m (-1)^{E_i \cdot x} |i\rangle $$
其中 $E_i$ 是从特定纠错码（如 Justesen 码）中提取的码字，$m = O(n)$。通过这种编码，即使 $x$ 和 $y$ 只有 1 bit 的差异，它们对应的量子指纹态 $|h(x)\rangle$ 和 $|h(y)\rangle$ 在希尔伯特空间中的保真度也会非常低。这为后续的相干比较提供了基础。

### 2. 通信复杂性中的应用：SWAP 测试
在通信复杂性模型中，Alice 将她的量子指纹 $|h(x)\rangle$ 发送给第三方（或直接发给 Bob）。为了判断 $x$ 是否等于 $y$，Bob 需要比较他自己的指纹 $|h(y)\rangle$ 和接收到的 $|h(x)\rangle$。在量子力学中，两个未知量子态的比较是通过 **SWAP 测试（交换测试）** 来完成的。

SWAP 测试的原理是引入一个辅助量子比特，通过控制两个量子态的交换操作，最后测量辅助比特。测量结果为 0 的概率为：
$$ P(0) = \frac{1 + |\langle h(x) | h(y) \rangle|^2}{2} $$
如果 $x=y$，则 $|\langle h(x) | h(y) \rangle|^2 = 1$，因此辅助比特测量结果必定为 0；如果 $x \neq y$，由于指纹编码的正交性，$|\langle h(x) | h(y) \rangle|^2 \leq \epsilon$，测量结果为 0 的概率最大为 $\frac{1+\epsilon}{2}$。通过多次重复这一过程（每次仅需 $O(\log n)$ 个量子比特的通信），即可在极小的错误率下判断出 $x$ 与 $y$ 是否相等。

这证明了量子指纹在通信复杂性中将相等性问题的通信代价从经典的 $\Omega(\sqrt{n})$ 降低到了 $O(\log n)$，这是量子计算领域最著名的指数级分离之一。

### 3. isQ 代码示例：SWAP 测试电路
以下是在 isQ 量子编程语言中实现 SWAP 测试的代码示例。该电路是量子指纹验证方案的核心步骤。由于 isQ 中没有原生的 SWAP 门，我们使用 3 个 CNOT 门来等效替代受控 SWAP 操作。

```isq
import std;

qbit q[3]; 
// q[0] 为辅助控制比特
// q[1] 假设已装载 Alice 的量子指纹态
// q[2] 假设已装载 Bob 的量子指纹态

procedure main() {
    // 初始化（此处仅为演示测试电路，假设全为 |0> 态，即两者相等）
    // 实际应用中 q[1] 和 q[2] 会通过相应的指纹编码电路制备

    // 开始 SWAP 测试
    H(q[0]);

    // 执行受控 SWAP
    // 受控 SWAP 等价于在控制位为 |1> 时执行三个 CNOT
    ctrl @[q[0]] CNOT(q[1], q[2]);
    ctrl @[q[0]] CNOT(q[2], q[1]);
    ctrl @[q[0]] CNOT(q[1], q[2]);

    H(q[0]);

    // 测量辅助比特，如果输出 0 则大概率 x=y，输出 1 则大概率 x!=y
    int result = M(q[0]);
    print result;
}
```
通过上述机制，量子指纹技术在量子通信、量子密码学以及分布式量子计算中都有着广阔的应用前景。

## isqTrain/4105

- task_id: `isqTrain/4105`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1095`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[4];

procedure main() {

    H(q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 16.0, q[3], q[0]);
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[3], q[1]);
    H(q[2]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[3], q[2]);
    H(q[3]);
    CNOT(q[0], q[3]);
    CNOT(q[3], q[0]);
    CNOT(q[0], q[3]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[1]);
    CNOT(q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

First, let me identify the gates:
1. H(q[0]) - Hadamard on q[0]
2. ctrl Rz(π/2, q[1], q[0]) - controlled-Rz with q[1] as control, q[0] as target
3. ctrl Rz(π/4, q[2], q[0]) - controlled-Rz with q[2] as control, q[0] as target
4. ctrl Rz(π/8, q[3], q[0]) - controlled-Rz with q[3] as control, q[0] as target
5. H(q[1])
6. ctrl Rz(π/2, q[2], q[1])
7. ctrl Rz(π/4, q[3], q[1])
8. H(q[2])
9. ctrl Rz(π/2, q[3], q[2])
10. H(q[3])
11. CNOT(q[0], q[3])
12. CNOT(q[3], q[0])
13. CNOT(q[0], q[3])
14. CNOT(q[1], q[2])
15. CNOT(q[2], q[1])
16. CNOT(q[1], q[2])

Wait, the controlled Rz gates - in isQ syntax, `ctrl Rz(theta, q[1], q[0])` means q[1] is the control and q[0] is the target? Let me re-check...

Actually, looking at the syntax: `ctrl Rz(theta, control, target)` - the first qubit inside Rz is control, second is target? No wait, `Rz(theta, qubit)` is a single-qubit gate. With `ctrl`, it becomes `ctrl Rz(theta, control_qubit, target_qubit)`.

Actually I need to be more careful. The syntax `ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0])` - in isQ, `ctrl` modifier adds a control qubit. The first argument after the gate parameters is the control, then the target? Or is it that the gate already has its parameters, and ctrl adds control qubits before the target?

Analyzing the: `ctrl @[c1, c2] Gate(target)` - so the control qubits come before the target in the `ctrl @[...]` syntax. But in the simple `ctrl` form like `ctrl Rz(theta, q[1], q[0])`, it seems like q[1] is the control and q[0] is the target for the Rz.

Wait, but Rz is a single-qubit gate with one parameter: Rz(theta, qubit). So `ctrl Rz(theta, q[1], q[0])` would mean: q[1] is the additional control, and q[0] is the target that Rz acts on.

So the structure is:
- Rz(theta, target) is single qubit
- ctrl Rz(theta, control, target) makes it controlled-Rz

So the controlled Rz gates apply Rz to the target qubit when the control is |1⟩.

Now, the sequence of controlled-Rz gates followed by Hadamards looks like a Quantum Fourier Transform (QFT)!

Let me check: In QFT, the structure is:
- H on q[0]
- Controlled-Rk(q[1], q[0]) where Rk = Rz(2π/2^k) with k=2
- Controlled-Rk(q[2], q[0]) with k=3
- Controlled-Rk(q[3], q[0]) with k=4
- H on q[1]
- Controlled-Rk(q[2], q[1]) with k=2
- Controlled-Rk(q[3], q[1]) with k=3
- H on q[2]
- Controlled-Rk(q[3], q[2]) with k=2
- H on q[3]

Wait, but the Rz angles here are:
- 2π/4 = π/2
- 2π/8 = π/4
- 2π/16 = π/8

In QFT, Rk = diag(1, e^(2πi/2^k)). And Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2}). So we need Rz such that e^{iθ/2} = e^{2πi/2^k}, meaning θ/2 = 2π/2^k, so θ = 2π/2^{

### Reference answer

Uniform distribution across 16 states

## isqTrain/1094

- task_id: `isqTrain/1094`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2108`

### Prompt

Help me write isQ code that implements a variant of the bernstein_vazirani pattern using anc[1] -> anc[2]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement Bernstein-Vazirani to find hidden string s=101 via oracle f(x)=x[0]⊕x[2], using anc[0] for phase kickback.

2. **Qubits**: 3 input qubits q[0..2] + 2 ancilla qubits anc[0..1]; only q[0], q[1], q[2] are measured.

3. **State evolution**:
   - Initial: |000⟩|00⟩
   - After X(anc[0]), H(anc[0]): |000⟩(|0⟩−|1⟩)/√2 ⊗ |0⟩ = |000⟩|−⟩|0⟩
   - After H⊗3 on q: (Σ_x |x⟩/2√2)|−⟩|0⟩
   - Oracle f(q,anc): phase kickback yields (Σ_x (-1)^(x[0]⊕x[2])|x⟩/2√2)|−⟩|0⟩
   - After H⊗3 on q: |101⟩|−⟩|0⟩ (Hadamard decodes s via inverse Fourier transform)

4. **Expected probabilities**: Measurement yields |101⟩ with probability 1.0, since the final state of measured qubits is exactly |101⟩.

## isqTrain/3940

- task_id: `isqTrain/3940`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1954`

### Prompt

下面的量子程序运行结果不对，请帮我debug：

```
import std;
// QFT on 4 qubits with input state |1010>
qbit q[4];

procedure main() {
    // Prepare input state |1010>
    X(q[0]);
    X(q[2]);

    // QFT stage for qubit 0
    H(q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 16.0, q[3], q[0]);
    // QFT stage for qubit 1
    H(q[1]);
    // BUG: missing gate here
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[3], q[1]);
    // QFT stage for qubit 2
    H(q[2]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[3], q[2]);
    // QFT stage for qubit 3
    H(q[3]);
    // Swap q[0] and q[3]
    CNOT(q[0], q[3]);
    CNOT(q[3], q[0]);
    CNOT(q[0], q[3]);
    // Swap q[1] and q[2]
    CNOT(q[1], q[2]);
    CNOT(q[2], q[1]);
    CNOT(q[1], q[2]);
    // Measure after QFT
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The QFT stage for qubit 1 is missing a controlled-Rz gate between q[2] (control) and q[1] (target). In the standard QFT, for qubit k, we apply controlled-Rz rotations from every higher-index qubit k+1, k+2, ..., n-1. The buggy code jumps directly from H(q[1]) to ctrl Rz(2π/8, q[3], q[1]), skipping q[2].

2. **Fix**: Insert `ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);` after `H(q[1]);` and before the existing ctrl Rz with q[3]. This provides the rotation by 2π/2² (i.e., phase π/2) conditioned on q[2].

3. **State evolution of corrected circuit**:
   - Prepare |1010⟩ via X(q[0]), X(q[2])
   - QFT stage 0: H on q[0] creates superposition; controlled rotations from q[1], q[2], q[3] encode relative phases
   - QFT stage 1: H on q[1]; ctrl Rz(2π/4, q[2], q[1]) adds conditional phase π/2; ctrl Rz(2π/8, q[3], q[1]) adds conditional phase π/4
   - QFT stages 2–3: complete the standard QFT pattern
   - Swap q[0]↔q[3] and q[1]↔q[2] to reverse bit order
   - Result: uniform superposition over all 16 basis states, each with |amplitude|² = 0.0625, confirmed by predicted output distribution

## isqTrain/2812

- task_id: `isqTrain/2812`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1975`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
oracle bool[1] constant(bool a[4]) {
    bool res[] = [true];
    return res;
}
qbit q[4], anc[1];

procedure main()
{
    H(q);
    H(anc[0]);
    constant(q, anc);
    H(q);
    print M(q);
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ program:**
    *   **Imports and Setup:** `import std;`
    *   **Oracle `constant`:** Takes `bool a[4]` (4 input qubits). Returns `[true]`. In isQ, an oracle acting on `q` and `anc` applies `U|x, y> = |x, y XOR f(x)>`. Here `f(x) = true`. So it acts as a controlled-X (CNOT) from all inputs to `anc`? Wait, isQ's `oracle` syntax for `constant(q, anc)` applies X to `anc` if `f(q) == true`? Actually, standard Deutsch-Jozsa oracle applies $|x\rangle|y\rangle \to |x\rangle|y \oplus f(x)\rangle$. Wait, if the oracle is `constant` returning `true`, the transformation is $|x\rangle|y\rangle \to |x\rangle|y \oplus 1\rangle$, which is equivalent to applying an $X$ gate to `anc` unconditionally (it doesn't depend on $x$).
    *   **Qubits:** `qbit q[4], anc[1];`
    *   **Circuit Execution:**
        1.  `H(q);` Applies H to q[0], q[1], q[2], q[3]. State of `q` becomes $|+\rangle^{\otimes 4}$. `anc` is $|0\rangle$.
        2.  `H(anc[0]);` `anc` becomes $|+\rangle$.
        3.  `constant(q, anc);` This calls the oracle. Since `f(x) = true`, it performs $|x\rangle|y\rangle \to |x\rangle|y \oplus 1\rangle$.
            Wait, let's trace carefully: $|x\rangle |-\rangle \to (-1)^{f(x)} |x\rangle |-\rangle$.
            Since $f(x) = 1$ for all $x$, it applies a phase of $(-1)^1 = -1$ to every computational basis state.
            However, let's check if the isQ compiler implements it as phase kickback or literally flips `anc`.
            In isQ, `oracle bool[1] constant(bool a[4]) { ... }` maps to the standard oracle $U_f |x\rangle |y\rangle = |x\rangle |y \oplus f(x)\rangle$.
            Wait! If `anc` is $|-\rangle$, applying X to `anc` introduces a global phase of $-1$ because $X |-\rangle = -|-\rangle$.
            So the state of `q` and `anc` becomes $- |+\rangle^{\otimes 4} |-\rangle$.
        4.  `H(q);` Applies H to q[0], q[1], q[2], q[3].
            $H^{\otimes 4} |+\rangle^{\otimes 4} = |0\rangle^{\otimes 4} = |0000\rangle$.
            So the state of `q` becomes $- |0000\rangle |-\rangle$.
        5.  `print M(q);` Measures `q`. The probability of $|0000\rangle$ is 1.0.
2.  **State Evolution Details:**
    *   Init: $|0\rangle^{\otimes 4} |0\rangle$
    *   H(q): $(\frac{1}{\sqrt{2}} \sum_{x=0}^{15} |x\rangle) |0\rangle$
    *   H(anc[0]): $(\frac{1}{\sqrt{2}} \sum_{x=0}^{15} |x\rangle) (\frac{|0\rangle - |1\rangle}{\sqrt{2}})$
    *   constant(q, anc): Since f(x) = 1 for all x, $|x\rangle |y\rangle \to |x\rangle |y \oplus 1\rangle$.
        Acting on $(\frac{1}{\sqrt{2}} \sum |x\rangle) (\frac{|0\rangle - |1\rangle}{\sqrt{2}})$, it flips $y$ for each term.
        So $|0\rangle - |1\rangle$ becomes $|1\rangle - |0\rangle = - (|0\rangle - |1\rangle)$.
        The state becomes $-\frac{1}{4} \sum_{x} |x\rangle (|0\rangle -

### Reference answer

{'predicted_probs': {'0000': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqQA/quantum_algorithms/86_application_scenario

- task_id: `isqQA/quantum_algorithms/86_application_scenario`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `application_scenario`, `algorithm`, `Deutsch算法原理`
- source: `qa_pipeline`
- dataset_index: `5105`

### Prompt

Deutsch算法作为最基础的量子算法之一，虽然原理相对简单，但它在实际应用中有什么价值？请探讨该算法在实际量子计算场景中的具体应用案例以及未来的发展前景，并使用isQ语言编写一段演示该算法核心判断过程的代码。

### Reference answer

<thought>
从应用场景维度来看，Deutsch算法本身处理的单比特布尔函数判定问题在宏观工程中鲜有直接应用。然而，它证明了量子计算在查询复杂度上的指数级加速潜力，这种“量子并行性”与“相位反冲”机制是所有高级量子算法的基石。在实际案例中，它主要被用作量子硬件的校准基准；而在其多比特扩展中，衍生出了在密码学中区分伪随机函数、在量子机器学习中作为量子核函数评估基础的应用。数学推导上，系统初始化为|0⟩|1⟩，经Hadamard门演化为(|0⟩+|1⟩)(|0⟩-|1⟩)/2。通过受控黑盒U_f作用，由于相位反冲，状态坍缩并纠缠为(-1)^f(0)|0⟩+(-1)^f(1)|1⟩。最后对首量子比特施加H门，若f(x)为常数函数，则测量结果必为|0⟩；若为平衡函数，则结果必为|1⟩。以下代码在isQ中演示了这一过程，其中黑盒设定为平衡函数f(x)=x。
</thought>
Deutsch算法作为量子计算领域的“Hello World”，其实际应用价值并不在于直接解决宏大的工业级问题，而在于作为验证量子计算可行性与硬件可靠性的基石，同时为更复杂的量子算法提供设计范式。在具体的实际应用案例中，Deutsch算法及其扩展主要体现在以下几个方面：

1. 量子硬件基准测试：在NISQ（含噪声中等规模量子）时代，评估量子计算机的性能至关重要。由于Deutsch算法的线路结构简单、逻辑明确，研究人员经常将其作为测试量子门保真度、测量精度以及系统相干性的标准测试程序。如果一台量子计算机能够以接近100%的概率成功运行该算法，则证明其底层基础硬件的运行状态达到了理想门槛。

2. 密码学与安全性分析：在现代密码学中，常使用伪随机函数来构建安全的加密方案。Deutsch算法及其多比特扩展的Deutsch-Jozsa算法展现出的指数级查询优势，被理论性地应用于区分伪随机函数和真随机函数。这为分析经典对称加密算法在量子计算环境下的抗量子安全性提供了重要的评估模型。

3. 量子机器学习与黑盒评估：在量子神经网络和变分量子算法中，经常需要评估复杂的参数化黑盒函数。Deutsch算法展示的“单次查询获取全局信息”的量子干涉查询模型，是量子支持向量机（QSVM）和量子退火算法中进行哈密顿量模拟与核函数计算的核心前置思想。

关于未来的发展前景，随着量子硬件的规模化，Deutsch算法本身的直接应用场景不会大幅扩张，但它揭示的量子并行性将被放大并广泛应用于更广阔的领域。例如，在药物分子模拟和材料设计中，评估分子能量函数将继承这种查询优越性；在金融工程中，利用类似的振幅放大机制进行期权定价和风险分析也是极具前景的方向。

以下是使用isQ语言编写的Deutsch算法核心代码演示。假设我们需要判定的黑盒是一个平衡函数（例如 f(x)=x，即当且仅当输入为1时输出为1），量子线路将仅通过单次查询精准判定其性质：

import std;

qbit q[2];

procedure main() {
    // 初始化辅助量子比特为 |1>
    X(q[1]);

    // 对两个量子比特施加Hadamard门，创建叠加态
    // 此时首量子比特包含所有可能的输入状态
    H(q[0]);
    H(q[1]);

    // 实现量子黑盒 U_f
    // 这里假设我们测试的是一个平衡函数 f(x) = x
    // 其对应的量子逻辑门为 CNOT
    CNOT(q[0], q[1]);

    // 对输入量子比特再次施加Hadamard门，利用干涉消除错误概率
    H(q[0]);

    // 测量输入量子比特
    // 若结果为1，确认为平衡函数；若为0则为常数函数
    int result = M(q[0]);
}

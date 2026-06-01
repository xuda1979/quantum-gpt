# ISQ training COT RAG corpus: quantum_algorithms shard 28

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4079

- task_id: `isqTrain/4079`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `248`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[3];

unit grover_oracle(qbit q[3]) {
    X(q[0]);
    X(q[2]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[2]);
    X(q[0]);
} deriving gate

unit grover_diffusion(qbit q[3]) {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
} deriving gate

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    grover_oracle(q);
    grover_diffusion(q);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis

1. **Operations applied:**
   - Initialize 3 qubits to |000⟩
   - Apply H⊗3 creating uniform superposition
   - Grover oracle: marks target state with phase flip
   - Grover diffusion: amplitude amplification
   - Measure all qubits

2. **Step-by-step evolution:**
   - Initial: |000⟩
   - After H⊗3: (1/2√2)Σ|x⟩, uniform over all 8 basis states
   - Oracle: X on q[0], q[2] transforms |010⟩ → |111⟩; ctrl CZ flips phase of |111⟩; X gates restore, resulting in -|010⟩ being the marked state
   - Diffusion: H⊗3 → X⊗3 → ctrl CZ → X⊗3 → H⊗3 performs inversion about mean
   - For 3 qubits (N=8), one Grover iteration rotates amplitude to nearly fully amplify the marked state

3. **Final state:** The amplitude of |010⟩ is maximally amplified while all others are suppressed.

4. **Predicted probability distribution:**
   - |010⟩: probability 1.0 (certain)
   - All other states: probability 0.0

   **Most likely measurement outcome: 010** (q[0]=0, q[1]=1, q[2]=0)

### Reference answer

Dominant output states: |010> with probability ~0.78 each

## isqQA/quantum_algorithms/90_optimization_variant

- task_id: `isqQA/quantum_algorithms/90_optimization_variant`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `optimization_variant`, `algorithm`, `Bernstein-Vazirani算法原理`
- source: `qa_pipeline`
- dataset_index: `5183`

### Prompt

请问Bernstein-Vazirani算法在量子计算的研究中，除了标准的量子查询模型外，有哪些针对物理硬件优化的改进版本或变体？能否以无辅助比特变体为例，给出数学推导与对应的isQ代码实现？

### Reference answer

标准的Bernstein-Vazirani算法需要使用n个输入量子比特和1个辅助量子比特，利用量子并行性和相位反冲来寻找隐藏字符串s。然而，在近期的NISQ（含噪声中等规模量子）设备中，额外的量子比特和双比特门会显著增加噪声和错误率。为了提高硬件执行效率，研究者提出了**无辅助比特的Bernstein-Vazirani变体**。该变体通过省略辅助比特，将 oracle 的作用直接转化为对主寄存器的相位操作，从而减少了系统的量子比特总数和量子门的数量。

数学推导如下：在标准算法中，黑盒函数酉算子作用在态|x>|->上，结果为(-1)^{f(x)}|x>|->，其中f(x) = s·x mod 2。辅助比特|->的引入仅是为了提取相位(-1)^{s·x}。在无辅助比特变体中，我们直接构建产生该相位改变的对角酉算子U_s：
U_s |x> = (-1)^{s·x} |x>
因为s·x是按位乘积的模2和，即s·x = s_0 x_0 ⊕ s_1 x_1 ⊕ ... ⊕ s_{n-1} x_{n-1}。根据指数的性质，我们可以将相位分解为独立比特相位的乘积：
(-1)^{s·x} = ∏_{i=0}^{n-1} (-1)^{s_i x_i}
这意味着，当且仅当s_i = 1且x_i = 1时，对应项会引入-1的相位。这在量子线路上等价于：在哈达玛叠加态下，仅需对那些s_i = 1对应的量子比特施加一个单比特Z门即可。经过U_s操作后，再施加一层哈达玛变换，即可直接测量得到隐藏字符串s。

以下是使用isQ语言编写的无辅助比特变体代码，假设我们要寻找的隐藏字符串为s = 101（对应量子比特q[0], q[2]的值为1）：

import std;

qbit q[3];

procedure main() {
    // 初始化：对所有量子比特施加H门，进入等权叠加态
    for i in 0:3 {
        H(q[i]);
    }

    // 构建无辅助比特的相位Oracle
    // 根据推导，对于s=101，直接对q[0]和q[2]施加Z门
    Z(q[0]);
    Z(q[2]);

    // 再次施加H门，将相位信息转化为计算基态的概率幅
    for i in 0:3 {
        H(q[i]);
    }

    // 测量量子比特，理论上将以100%的概率输出101
    for i in 0:3 {
        M(q[i]);
    }
}

## isqTrain/4845

- task_id: `isqTrain/4845`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `quantum_counting`, `interference`
- source: `isq_train_cot`
- dataset_index: `384`

### Prompt

I need an isQ program to implementing a phase oracle that marks |01> using X(q[0]), CZ, X(q[0]). Apply to |01> state directly (no superposition) and measure.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement a phase oracle marking |01⟩ with a phase flip, apply it to |01⟩, and measure.
Two qubits (q[0], q[1]) are used and both are measured.
Step-by-step state evolution:
1. |00⟩ → X(q[1]) → |01⟩ (prepare target state)
2. |01⟩ → X(q[0]) → |11⟩ (transform |01⟩ basis to |11⟩ for CZ)
3. |11⟩ → CZ(q[0],q[1]) → -|11⟩ (phase flip on |11⟩)
4. -|11⟩ → X(q[0]) → -|01⟩ (transform back)
Measurement yields |01⟩ with probability 1.0 since the global phase (-1) is unobservable in Z-basis measurement.

## isqTrain/40

- task_id: `isqTrain/40`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_arrays`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2321`

### Prompt

Implement the following in isQ: implements a variant of the oracle_boolean pattern using q[4] -> q[6]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The task is to write an isQ program implementing a variant of the Bernstein-Vazirani algorithm using qubits q[4] through q[6]. Let me first analyze The implementation to understand the pattern, then modify it accordingly.

The implementation:
1. Uses 6 qubits
2. Applies Hadamard gates to q[0] and q[1]
3. Copies q[0] to q[2] and q[1] to q[3] using CNOT gates
4. Implements an oracle for s="11" using CNOT gates
5. Applies Hadamard gates to q[0] and q[1]
6. Measures q[0], q[1], q[4], q[5]

The predicted output {|0000>: 0.5, |1100>: 0.5}, which corresponds to measuring s="11" from the Bernstein-Vazirani algorithm.

For the variant using q[4] -> q[6]:
- This means the circuit should use qubits q[4], q[5], q[6]
- The register should be expanded with additional qubits left in ground state

Let me think about this more carefully. The original circuit has:
- Input qubits: q[0], q[1]
- Ancilla qubits: q[2], q[3]
- Extra qubits: q[4], q[5] (measured but untouched, so they stay in |0>)

For the variant using q[4] -> q[6], I need to adapt the circuit. The phrase "significantly expanded qubit register" suggests using more qubits overall, with the additional ones left in |0>.

Looking at the pattern:
- The main computation happens on some qubits
- Additional qubits are measured but remain in |0>

Let me construct a variant that:
1. Uses qubits q[4], q[5], q[6] as the primary computational qubits
2. Has additional qubits in the register that stay in |0>

Actually, I think I'm overcomplicating this. Let me re-read the task.

The task says: "implements a variant of the oracle_boolean pattern using q[4] -> q[6]"

This suggests that the main active qubits should be q[4], q[5], q[6] instead of q[0], q[1], etc. in the reference.

Let me construct the circuit:
- Use a larger register (say 8 qubits)
- Apply H to q[4] and q[5] (the input qubits)
- Use q[6] as an ancilla
- Implement the oracle
- Apply H to inputs
- Measure appropriate qubits

Wait, Analyzing the more carefully:
- q[0], q[1] are input qubits
- q[2], q[3] are output qubits (where the result is XORed)
- q[4], q[5] are extra qubits that stay in |0>

The oracle copies and XORs based on the secret string s="11":
1. First CNOT(q[0], q[2]) copies q[0] to q[2]
2. CNOT(q[1], q[3]) copies q[1] to q[3]
3. Then CNOT(q[0], q[2]) XORs q[0] into q[2] (for the first bit of s)
4. CNOT(q[0], q[3]) XORs q[0] into q[3] (for the second bit of s)

This implements the oracle f(x) = x·s mod 2 for s="11".

For the variant using q[4] -> q[6], I should shift the computation to use these qubits. Let me create a version:

1. Declare a larger register (say 9 qubits)
2. Apply H to q[4] and q[5]
3. Use q[6], q[7] as output qubits
4. Implement the oracle on these qubits
5. Apply H to q[4] and q[5]
6. Measure q[4], q[5], and some extra qubits that remain |0>

Actually, wait. The task says "using q[4] -> q[6]", which could mean using qubits indexed 4 through 6 (i.e., q[4], q[5], q[6]).

Let me create a simpler variant:
- Use 8 qubits total
- q[4], q[5] as input qubits
- q[6], q[7] as ancilla/output qubits
- q[0], q[1], q[2], q[3] stay in |0>

Hmm, but this changes the measurement indices. Let me

## isqTrain/2670

- task_id: `isqTrain/2670`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2049`

### Prompt

Write isQ code for the following quantum task: prepares a specific quantum state using gate operations. Apply the appropriate sequence of single-qubit and multi-qubit gates, then measure the result.

Requirements:
- Use 3 qubit(s) total.
- Measure 3 qubit(s) at the end.
- The program must start with `import std;`, declare qubits at global scope (or procedure scope as appropriate), define `procedure main()` as the entry point, and include explicit `M()` calls for all measured qubits.

### Chain-of-thought reasoning

Let me trace through the circuit step by step.

Initial state: |000⟩

Step 1: H(q[0])
H on qubit 0: |0⟩ → |+⟩ = (|0⟩ + |1⟩)/√2
State: (|000⟩ + |100⟩)/√2

Step 2: X2P(q[1]) = Rx(π/2) on qubit 1
X2P = Rx(π/2): |0⟩ → (|0⟩ - i|1⟩)/√2
State: 1/2 (|000⟩ - i|010⟩ + |100⟩ - i|110⟩)

Step 3: CZ(q[0], q[2])
CZ applies Z to q[2] when q[0] is |1⟩. Z|0⟩ = |0⟩, so no effect on basis states where q[2]=|0⟩.
State unchanged: 1/2 (|000⟩ - i|010⟩ + |100⟩ - i|110⟩)

Step 4: Y2M(q[0]) = Ry(-π/2) on qubit 0
Y2M = Ry(-π/2): |0⟩ → (|0⟩ + |1⟩)/√2, |1⟩ → (|1⟩ - |0⟩)/√2... wait let me recalculate.

Ry(θ) = [[cos(θ/2), -sin(θ/2)], [sin(θ/2), cos(θ/2)]]
Ry(-π/2): cos(-π/4) = cos(π/4) = 1/√2, sin(-π/4) = -1/√2
Ry(-π/2) = [[1/√2, 1/√2], [-1/√2, 1/√2]]

So: |0⟩ → (|0⟩ - |1⟩)/√2, |1⟩ → (|0⟩ + |1⟩)/√2

Wait, let me redo:
Ry(-π/2)|0⟩ = cos(-π/4)|0⟩ + sin(-π/4)|1⟩ = (|0⟩ - |1⟩)/√2
Ry(-π/2)|1⟩ = -sin(-π/4)|0⟩ + cos(-π/4)|1⟩ = (|0⟩ + |1⟩)/√2

So after Y2M on q[0]:
|0⟩₀ → (|0⟩ - |1⟩)/√2
|1⟩₀ → (|0⟩ + |1⟩)/√2

State: 1/(2√2) [(|0⟩ - |1⟩)(|00⟩ - i|10⟩)₂₁ + (|0⟩ + |1⟩)(|00⟩ - i|10⟩)₂₁]

Wait, I need to be more careful. The state is:
1/2 [|0⟩₀|0⟩₁|0⟩₂ - i|0⟩₀|1⟩₁|0⟩₂ + |1⟩₀|0⟩₁|0⟩₂ - i|1⟩₀|1⟩₁|0⟩₂]

Applying Y2M on q[0]:
|0⟩₀ → (|0⟩ - |1⟩)/√2
|1⟩₀ → (|0⟩ + |1⟩)/√2

State becomes:
1/(2√2) [(|0⟩ - |1⟩)|0⟩|0⟩ - i(|0⟩ - |1⟩)|1⟩|0⟩ + (|0⟩ + |1⟩)|0⟩|0⟩ - i(|0⟩ + |1⟩)|1⟩|0⟩]

= 1/(2√2) [|0⟩|0⟩|0⟩ - |1⟩|0⟩|0⟩ - i|0⟩|1⟩|0⟩ + i|1⟩|1⟩|0⟩ + |0⟩|0⟩|0⟩ + |1⟩|0⟩|0⟩ - i|0⟩|1⟩|0⟩ - i|1⟩|1⟩|0⟩]

= 1/(2√2) [2|0⟩|0⟩|0⟩ - 2i|0⟩|1⟩|0⟩]

= 1/√2 [|000⟩ - i|010⟩]

Step 5: CZ(q[2], q[1])
CZ applies Z to q[1] when q[2] is |1⟩. But q[2] is always |0⟩ in our state, so no effect.
State: 1/√2 [|000⟩ - i|010⟩]

Measurement probabilities:
- |000⟩: |1/√2|² =

## isqExpand/algo/126

- task_id: `isqExpand/algo/126`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `reversible_computing`, `multi_controlled_logic`, `ancilla_usage`
- source: `isq_expansion`
- dataset_index: `4403`

### Prompt

下面的量子程序运行结果不对，请帮我debug：

```isq
import std;
qbit q[5];
procedure main() {
    X(q[0]); X(q[2]);
    CNOT(q[0], q[3]);
    CNOT(q[1], q[3]);
    CNOT(q[2], q[3]);
    Toffoli(q[0], q[1], q[4]);
    Toffoli(q[0], q[3], q[4]);
    Toffoli(q[1], q[2], q[4]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
The second Toffoli uses q[3] (Sum) instead of q[2] (Cin).
Since q[3] holds the computed Sum, using it for carry is wrong.

Fix: Change Toffoli(q[0], q[3], q[4]) to Toffoli(q[0], q[2], q[4]).

A=1, B=0, Cin=1: Sum = 0, Cout = 1.
q=[1,0,1,0,1] -> index 21.

## isqQA/quantum_algorithms/90_comparison

- task_id: `isqQA/quantum_algorithms/90_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `comparison`, `algorithm`, `Bernstein-Vazirani算法原理`
- source: `qa_pipeline`
- dataset_index: `1903`

### Prompt

请对比分析Bernstein-Vazirani算法与经典计算方法以及Deutsch-Jozsa算法在解决问题、查询复杂度和量子线路结构上的异同，并详细说明Bernstein-Vazirani算法的独特优势与局限性。请提供使用isQ语言实现该算法的完整代码示例。

### Reference answer

<think Bernstein-Vazirani算法的对比维度分析>
1. 与经典计算对比：经典方法需要n次查询才能确定n位隐藏字符串，而BV算法仅需1次查询。
2. 与Deutsch-Jozsa算法对比：线路结构相似（H-U_f-H），但解决的问题不同（DJ是判定常数/平衡，BV是提取具体字符串）。
3. 优缺点：优点是指数级查询加速且线路浅，适合作为NISQ时代的硬件基准测试；缺点是实际应用场景较窄。
4. 编写isQ代码实现：设定4位字符串1011，构建Oracle，执行Hadamard测试。
</think Bernstein-Vazirani算法的对比维度分析>

Bernstein-Vazirani（BV）算法是量子计算中用于解决隐藏字符串问题的经典算法。假设存在一个黑盒函数 $f: \{0,1\}^n \rightarrow \{0,1\}$，其计算形式为 $f(x) = s \cdot x \pmod 2$，其中 $s$ 是一个未知的 $n$ 位二进制字符串。BV算法的目的就是通过查询该函数，找出这个隐藏的字符串 $s$。

**1. 与经典计算方法的对比**
在经典计算中，为了确定 $n$ 比特的字符串 $s$，我们至少需要向黑盒查询 $n$ 次。例如，依次输入 $x = 100...0$、$010...0$ 等，每次提取 $s$ 的一位。而Bernstein-Vazirani算法利用了量子态的叠加性和相位干涉，仅需对黑盒进行 **1次** 量子查询，就能直接得到隐藏字符串 $s$。在这里，量子算法实现了相对于经典确定性算法在查询复杂度上从 $O(n)$ 到 $O(1)$ 的指数级加速。

**2. 与Deutsch-Jozsa（DJ）算法的对比**
BV算法与DJ算法在量子线路结构上高度一致，它们都采用了“Hadamard变换 -> 调用Oracle -> Hadamard变换”的范式，但它们的目标和适用场景有显著差异：
- **解决的问题不同**：DJ算法是一个“判定问题”，它的目标是判断黑盒函数是常数函数还是平衡函数；而BV算法是一个“搜索/参数估计问题”，目标是精确提取出黑盒函数内部的具体参数（即隐藏字符串 $s$）。
- **测量方式与输出来源不同**：DJ算法中，我们通常只关心第一个寄存器的测量结果是否为全 $0$（常数）或非全 $0$（平衡），其加速体现在将经典需要 $O(2^{n-1})$ 次查询的概率算法加速到 $O(1)$ 次量子查询；而在BV算法中，由于经过第二次Hadamard门后，量子态变为了 $|s\rangle$，对第一个寄存器进行测量，得到的直接就是隐藏比特串 $s$ 的二进制位。

**3. BV算法的优缺点与适用场景**
- **优点**：查询复杂度极低（仅需1次），且量子线路深度很浅。它的Oracle仅由一系列受控非门（CNOT）构成，非常容易在当前的含噪中等规模量子（NISQ）设备上实现。
- **缺点与局限性**：该算法解决的问题模型过于理想化和特定（严格的线性内积函数），在现实世界中很难找到直接对应的应用场景。
- **适用场景**：目前BV算法最主要的应用是作为量子计算硬件和编译器的**基准测试算法**。研究人员经常通过运行BV算法来验证量子比特的纠缠能力、CNOT门的保真度以及测量结果的正确性。

**isQ语言代码实现**
下面展示了寻找4位隐藏字符串 $s = 1011$ 的BV算法isQ实现代码：

```isq
import std;

qbit q[5]; // q[0]至q[3]为输入寄存器，q[4]为辅助/目标寄存器

procedure main() {
    // 初始化目标寄存器为 |-> 状态
    X(q[4]);
    H(q[4]);

    // 对输入寄存器应用Hadamard门，创建叠加态
    for i in 0:4 {
        H(q[i]);
    }

    // 构建并调用 Oracle (隐藏字符串 s = 1011)
    // f(x) = x[0]*1 ^ x[1]*0 ^ x[2]*1 ^ x[3]*1
    // 如果s[i] == 1，则执行 CNOT(q[i], q[4])
    CNOT(q[0], q[4]); // s[0] = 1
    // s[1] = 0，跳过
    CNOT(q[2], q[4]); // s[2] = 1
    CNOT(q[3], q[4]); // s[3] = 1

    // 对输入寄存器再次应用Hadamard门
    for i in 0:4 {
        H(q[i]);
    }

    // 测量输入寄存器，结果应为 1011
    for i in 0:4 {
        M(q[i]);
    }
}
```

## isqTrain/2866

- task_id: `isqTrain/2866`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `multi_controlled_logic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2268`

### Prompt

请用isQ语言编写一个量子电路：implements a CZ gate with Hadamard. Apply the appropriate gates to 3 qubits and measure all of them.

Requirements:
- Declare `qbit q[3];` at global scope.
- Use `procedure main()` as entry point.
- Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
The circuit prepares a 3-qubit state using Hadamard gates to create superpositions, applies a CZ gate between q[0] and q[1], then measures all qubits.

**State evolution:**
- Initialize |ψ⟩ = |000⟩
- H(q[0]): |ψ⟩ = (|000⟩ + |100⟩)/√2
- H(q[1]): |ψ⟩ = (|000⟩ + |010⟩ + |100⟩ + |110⟩)/2
- CZ(q[0], q[1]): applies phase flip when both are |1⟩ → (|000⟩ + |010⟩ + |100⟩ − |110⟩)/2
- H(q[2]): |ψ⟩ = (|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ − |110⟩ − |111⟩)/(2√2)

Each of the 8 basis states has amplitude ±1/(2√2), so measurement probability for each is |±1/(2√2)|² = 1/8 = 0.125. The CZ phase has no effect on measurement probabilities since H(q[2]) acts independently and the relative phase on |110⟩ doesn't change outcome likelihoods.

## isqTrain/1940

- task_id: `isqTrain/1940`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_deriving_gate`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2715`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[2];
qbit u[1];
procedure main() {
    X(u[0]);
    H(q);
    ctrl S(q[1], u[0]);
    ctrl Z(q[0], u[0]);
    CNOT(q[0], q[1]); CNOT(q[1], q[0]); CNOT(q[0], q[1]);
    H(q[1]);
    ctrl inv S(q[0], q[1]);
    H(q[0]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants to analyze an isQ quantum program, trace the quantum state through the circuit, and predict the probability distribution of the measurement outcomes.
2.  **Analyze the isQ Code:**
    *   `qbit q[2]; qbit u[1];` -> Three qubits total: $q_0, q_1, u_0$. Initial state $|000\rangle$ (order $q_0, q_1, u_0$ or whatever convention, let's track them explicitly).
    *   `X(u[0])` -> state becomes $|0\rangle_{q_0}|0\rangle_{q_1}|1\rangle_{u_0}$. Let's write as $|00\rangle_q|1\rangle_u$.
    *   `H(q)` -> Apply H to $q_0$ and $q_1$. State becomes $(\frac{|0\rangle+|1\rangle}{\sqrt{2}})_{q_0} (\frac{|0\rangle+|1\rangle}{\sqrt{2}})_{q_1} |1\rangle_{u_0} = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)_q |1\rangle_u$.
    *   `ctrl S(q[1], u[0])` -> Apply S to $u_0$ if $q_1$ is 1. Wait, standard `ctrl Gate(target)` or `ctrl @[c] Gate(t)`? The syntax is `ctrl S(q[1], u[0])`. Wait, in isQ, `ctrl S(q[1], u[0])` might mean `q[1]` is the control and `u[0]` is the target. Let's assume standard ordering: `ctrl Gate(control, target)` or is it `ctrl @[control] Gate(target)`? The reference says `ctrl @[c1, c2] Gate(target)`. But here it's `ctrl S(q[1], u[0])`. If S is a single qubit gate, `ctrl S(q[1], u[0])` probably means control is `q[1]`, target is `u[0]`. Let's check the number of parameters. S takes 1. So `ctrl S(c, t)` means `c` is control, `t` is target. Control = $q_1$, Target = $u_0$.
        *   If $q_1=1$, $u_0$ gets S. $|1\rangle \to S|1\rangle = i|1\rangle$.
        *   State becomes $\frac{1}{2}(|00\rangle|1\rangle + i|01\rangle|1\rangle + |10\rangle|1\rangle + i|11\rangle|1\rangle)_{{q_0},{q_1},{u_0}}$.
    *   `ctrl Z(q[0], u[0])` -> Control = $q_0$, Target = $u_0$. Apply Z to $u_0$ if $q_0=1$. Z $|1\rangle = -|1\rangle$.
        *   $|0\cdot\rangle$ stays same.
        *   $|1\cdot\rangle$ gets -1.
        *   State becomes $\frac{1}{2}(|00\rangle|1\rangle + i|01\rangle|1\rangle - |10\rangle|1\rangle - i|11\rangle|1\rangle)$.
    *   `CNOT(q[0], q[1]); CNOT(q[1], q[0]); CNOT(q[0], q[1]);` -> This is the standard swap operation (three-CNOT decomposition)! It swaps $q_0$ and $q_1$.
        *   Let's check the basis states: $|00\rangle \to |00\rangle$, $|01\rangle \to |10\rangle$, $|10\rangle \to |01\rangle$, $|11\rangle \to |11\rangle$.
        *   State of $q$ becomes $\frac{1}{2}(|00\rangle + i|10\rangle - |01\rangle - i|11\rangle)|1\rangle$.  (Wait, $|01\rangle$ swapped to $|10\rangle$ and $|10\rangle$ swapped to $|01\rangle$. So: $|00\rangle$, $i|10\rangle$, $-|01\rangle$, $-i|11\rangle$).
    *   `H(q[1])` -> Apply H

### Reference answer

{'predicted_probs': {'01': 1.0}, 'explanation': 'QPE on S gate'}

## isqTrain/3448

- task_id: `isqTrain/3448`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `entanglement`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1691`

### Prompt

Create an isQ quantum circuit that a discrete-time quantum walk on a 4-node cycle in isQ.

Use 1 coin qubit and 2 position qubits (encoding 4 positions).
Position qubits: q[1..2], coin: q[0].

Shift operation on a 4-cycle:
- coin=|0> (move right): position = (position + 1) mod 4
- coin=|1> (move left): position = (position - 1) mod 4

Simplified: use coin-controlled increment/decrement.
For 2 position qubits, +1 mod 4 is increment:
  nctrl { CNOT(q[1], q[2]); X(q[1]); } from q[0]

Perform 2 walk steps. Start at position |00>, coin |0>.
Declare 3 qubits, measure all.

### Chain-of-thought reasoning

Let me analyze this quantum walk circuit step by step.

We have 3 qubits: q[0] (coin), q[1], q[2] (position, with q[1] as high bit, q[2] as low bit).

Initial state: |0⟩_coin ⊗ |00⟩_position = |000⟩

**Step 1:**
1. H(q[0]): Coin flip → (|0⟩+|1⟩)/√2 ⊗ |00⟩ = (|000⟩+|100⟩)/√2

2. nctrl CNOT(q[0], q[1], q[2]): When q[0]=|0⟩, apply CNOT(q[1], q[2]) to flip q[2] when q[1]=1. But q[1]=0, so no change.
   State: (|000⟩+|100⟩)/√2

3. nctrl X(q[0], q[1]): When q[0]=|0⟩, flip q[1]. So |000⟩ → |010⟩.
   State: (|010⟩+|100⟩)/√2

4. ctrl X(q[0], q[1]): When q[0]=|1⟩, flip q[1]. So |100⟩ → |110⟩.
   State: (|010⟩+|110⟩)/√2

5. ctrl CNOT(q[0], q[1], q[2]): When q[0]=|1⟩, apply CNOT(q[1], q[2]). |110⟩ → |111⟩ (since q[1]=1).
   State: (|010⟩+|111⟩)/√2

So after step 1, we're at position |10⟩ (i.e., 2) with coin |0⟩, or position |11⟩ (i.e., 3) with coin |1⟩.

Let me verify the increment/decrement logic:
- Increment (+1 mod 4): |00⟩→|01⟩, |01⟩→|10⟩, |10⟩→|11⟩, |11⟩→|00⟩
  - This is: if low bit is 1, flip high bit; then flip low bit
  - CNOT(q[1], q[2]) then X(q[1])
  Wait, the order matters. The code does:
  - nctrl CNOT(q[0], q[1], q[2]) first
  - then nctrl X(q[0], q[1])
  
  So for increment: first CNOT from q[1] to q[2] (flip q[2] when q[1]=1), then X on q[1].
  
  |00⟩ → |00⟩ (CNOT does nothing since q[1]=0) → |10⟩ (X on q[1]) = |10⟩ (2) → that's wrong, 0+1=1 not 2.

Hmm, let me reconsider. Maybe q[2] is the high bit and q[1] is the low bit? No wait, let me re-read.

Actually, let me think about incrementing a 2-bit number where q[1] is the MSB and q[2] is the LSB.

Increment (q[1], q[2]):
- |00⟩ → |01⟩: flip LSB
- |01⟩ → |10⟩: flip both
- |10⟩ → |11⟩: flip LSB
- |11⟩ → |00⟩: flip both

So: flip LSB always, flip MSB when LSB was 1 (before flip).

Actually the standard increment is:
1. CNOT(LSB, MSB) - flip MSB when LSB is 1
2. X(LSB) - flip LSB

Let me redo with q[2] as LSB and q[1] as MSB:

Wait, the code uses:

So CNOT(q[1], q[2]) - q[1] is control, q[2] is target. Then X(q[1]).

If q[1] is MSB, q[2] is LSB:
- |00⟩ (position 0, q[1]=0, q[2]=0): CNOT does nothing → X(q[1]) → |10⟩ = position 2. Wrong!

If q[1] is LSB, q[2] is MSB:
- Position 0: q[1]=0, q[2]=0
- CNOT(q[1], q[2]): control=0, nothing happens
- X(q[1]): flip q[1] → q[1]=1

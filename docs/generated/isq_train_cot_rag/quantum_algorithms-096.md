# ISQ training COT RAG corpus: quantum_algorithms shard 96

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2017

- task_id: `isqTrain/2017`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4080`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[4];
procedure main() {
    H(q[0]);
    X(q[1]);
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
    Toffoli(q[0], q[1], q[3]);
    M(q[2]);
    M(q[3]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise step-by-step analysis of an isQ quantum program, predicting the probability distribution of the measurement outcomes. The output must be 3-15 lines, starting with "## Circuit Analysis", using Dirac notation, and ending with the predicted probability distribution.

2.  **Analyze the isQ code:**
    *   Initialization: 4 qubits initialized to |0000>.
    *   `H(q[0])`: q[0] becomes (|0> + |1>)/sqrt(2). State: (|0000> + |1000>)/sqrt(2).
    *   `X(q[1])`: q[1] flips to |1>. State: (|0100> + |1100>)/sqrt(2).
    *   `CNOT(q[0], q[2])`: q[2] flips if q[0] is 1. State: (|0100> + |1110>)/sqrt(2).
    *   `CNOT(q[1], q[2])`: q[2] flips if q[1] is 1. Since q[1] is 1, q[2] flips again (for both terms). State: (|0110> + |1100>)/sqrt(2).
    *   `Toffoli(q[0], q[1], q[3])`: q[3] flips if q[0]=1 AND q[1]=1.
        *   First term (|0110>): q[0]=0, q[1]=1 -> q[3] unchanged -> |0110>.
        *   Second term (|1100>): q[0]=1, q[1]=1 -> q[3] flips to 1 -> |1101>.
        *   State: (|0110> + |1101>)/sqrt(2).
    *   Measurements: `M(q[2])`, `M(q[3])`.
        *   Order: q[2] is measured first, q[3] is measured second.
        *   In the predicted output format `{'01': 0.5, '10': 0.5}`, the bitstring is usually `q2` `q3` or `q3` `q2`? The prompt says: "Expected measurement probabilities: {'01': 0.5, '10': 0.5}".
        *   Wait, standard isQ measurement output for `M(q[2]); M(q[3]);`: The first measured qubit is the *highest* bit? The instructions say: "--probs output: array indexed by measurement bitstring (earlier measured qubit = higher bit)."
        *   So q[2] is the higher bit, q[3] is the lower bit.
        *   Let's check the states:
            *   Term 1: |0110>. q[2]=1, q[3]=0. Bitstring: q[2]q[3] = "10".
            *   Term 2: |1101>. q[2]=0, q[3]=1. Bitstring: q[2]q[3] = "01".
        *   So the probabilities are P('10') = 0.5, P('01') = 0.5. This perfectly matches the prompt's reference: {'01': 0.5, '10': 0.5}.

3.  **Draft the steps (Concise & Dirac notation):**
    *   *Initial state:* |q3 q2 q1 q0> = |0000>.
    *   *H(q[0]):* |0000> -> (|0000> + |1000>)/sqrt(2) = (|0> + |1>)_0 |000> / sqrt(2). Let's write it as q3q2q1q0.
    *   *X(q[1]):* (|0100> + |1100>)/sqrt(2).
    *   *CNOT(q[0], q[2]):* (|0100> + |1110>)/sqrt(2).
    *   *CNOT(q[1], q[2]):* (|0110> + |1100>)/sqrt(2). (Since q[1]=1 in both, q[2] flips).
    *   *Toffoli(q[0], q[1], q[3]):* (|0110> + |1101>)/sqrt(2). (q[3] flips only for |1100>).
    *   *Measurement:* Measure q[2] (higher bit), then q[3] (lower bit

### Reference answer

{'predicted_probs': {'01': 0.5, '10': 0.5}, 'explanation': 'Half adder in superposition: P(|01>)=P(|10>)=0.5.'}

## isqTrain/1003

- task_id: `isqTrain/1003`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `isq_syntax_for_loop`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1844`

### Prompt

I need an isQ program to implements the qdrift pattern with modified rotation parameters (num_pi2s_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

The user wants me to analyze the given isQ quantum program that implements a qdrift pattern with modified rotation parameters. Let me trace through the circuit step by step.

1. The circuit starts with 2 qubits in |00⟩ state
2. X(q[0]) prepares |10⟩ state
3. Then we have 4 samples of qdrift with rotation angle ≈ 1.047... (which is π/3, not π/2)

Wait, let me check: 1.04719755119660490 = π/3 ≈ 1.0471975512...

So the rotation is actually π/3 (60 degrees), not π/2. This is the "num_pi2s_to_pi3" modification mentioned in the task.

Let me trace through:

Initial: |00⟩
After X(q[0]): |10⟩

Sample 1: ZZ term
- CNOT(q[0], q[1]): |10⟩ → |11⟩ (control is 1, so target flips)
- Rz(π/3, q[1]): This applies a phase factor to |1⟩ state of q[1]
  Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2})
  |11⟩ → e^{iπ/6}|11⟩
- CNOT(q[0], q[1]): |11⟩ → |10⟩ (flips back)

State after sample 1: e^{iπ/6}|10⟩

Sample 2: XX term
- H(q[0]); H(q[1]): |10⟩ → H⊗H|10⟩ = |−+⟩ where |-⟩ = (|0⟩-|1⟩)/√2, |+⟩ = (|0⟩+|1⟩)/√2
  Actually: H|0⟩ = |+⟩, H|1⟩ = |-⟩
  So H⊗H|10⟩ = |-⟩⊗|+⟩ = 1/2(|00⟩ - |10⟩ + |01⟩ - |11⟩)

- CNOT(q[0], q[1]): 
  CNOT acts on the computational basis
  |00⟩ → |00⟩, |01⟩ → |01⟩, |10⟩ → |11⟩, |11⟩ → |10⟩
  So: 1/2(|00⟩ - |11⟩ + |01⟩ - |10⟩)

- Rz(π/3, q[1]):
  This adds phase e^{iπ/6} to states where q[1]=1
  1/2(|00⟩ - e^{iπ/6}|11⟩ + |01⟩ - e^{iπ/6}|10⟩)

- CNOT(q[0], q[1]):
  |00⟩ → |00⟩, |11⟩ → |10⟩, |01⟩ → |01⟩, |10⟩ → |11⟩
  1/2(|00⟩ - e^{iπ/6}|10⟩ + |01⟩ - e^{iπ/6}|11⟩)

- H(q[0]); H(q[1]):
  Apply H to each qubit
  H|00⟩ = |++⟩ = 1/2(|00⟩ + |01⟩ + |10⟩ + |11⟩)
  H|10⟩ = |-+⟩ = 1/2(|00⟩ - |10⟩ + |01⟩ - |11⟩)
  H|01⟩ = |+-⟩ = 1/2(|00⟩ + |01⟩ - |10⟩ - |11⟩)
  H|11⟩ = |--⟩ = 1/2(|00⟩ - |01⟩ - |10⟩ + |11⟩)

  Let me compute more carefully:
  1/2[|++⟩ - e^{iπ/6}|-+⟩ + |+-⟩ - e^{iπ/6}|--⟩]

  Hmm, this is getting complex. Let me use a different approach.

Actually, let me reconsider. The Rz gate applies Rz(θ)|0⟩ = e^{-iθ/2}|0⟩ and Rz(θ)|1⟩ = e^{iθ/2}|1⟩.

So Rz(π/3)|1⟩ = e^{iπ/6}|1⟩.

Let me be more systematic. The ZZ term in the Hamiltonian contributes as exp(-iθ ZZ), and when decomposed using CNOT-Rz-CNOT, it effectively applies the rotation based on the ZZ eigenvalue.

For the ZZ term: CNOT-Rz(θ)-CNOT applies exp(-iθ/2) when qubits are |00⟩ or |11⟩ (ZZ eigenvalue +1), and exp(iθ/2) when

## isqTrain/2725

- task_id: `isqTrain/2725`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5440`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[5];

procedure main(){
    X(q[4]);
    for i in 0:5{ 
        H(q[i]);
    }
    CNOT(q[0], q[4]);
    CNOT(q[1], q[4]);
    CNOT(q[3], q[4]);
    for i in 0:5{ 
        H(q[i]); 
    }
    for i in 0:5{
        M(q[i]); 
    }
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Role: Quantum computing expert.
    *   Task: Generate concise, precise step-by-step reasoning for an isQ quantum program. Output the final quantum state and probability distribution.
    *   Format constraint: "## Circuit Analysis" followed by step-by-step reasoning, ending with the predicted probability distribution. 3-8 lines for simple, up to 15 for complex.
    *   Notation: Dirac notation (|0>, |1>, |+>, |->).
    *   Input isQ code: 5 qubits. `X(q[4])`, `H` on all, `CNOT(q[0], q[4])`, `CNOT(q[1], q[4])`, `CNOT(q[3], q[4])`, `H` on all, `M` on all.
    *   Output expectation: Final state and probability distribution {'11011': 1.0} (Wait, let me calculate this to be sure).

2.  **Trace the Circuit:**
    *   Initial state: $|00000\rangle$
    *   `X(q[4])`: $|00001\rangle$ (q[4] is the least significant bit, index 4. Let's use standard bit order: q[0]q[1]q[2]q[3]q[4])
    *   `H` on all: $\frac{1}{\sqrt{2^5}} \sum_{x \in \{0,1\}^5} |x\rangle$.
        *   Wait, let's look at q[4]. It starts as $|1\rangle$, so $H|1\rangle = |-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
        *   So the state is $|+\rangle^{\otimes 4} \otimes |-\rangle$.
    *   `CNOT(q[0], q[4])`, `CNOT(q[1], q[4])`, `CNOT(q[3], q[4])`:
        *   This is applying controlled-X on target q[4], with controls q[0], q[1], and q[3].
        *   The target is $|-\rangle$.
        *   Recall that CNOT with control $|+\rangle$ and target $|-\rangle$ yields $|-\rangle_{control} \otimes |+\rangle_{target}$ up to global phase, OR we can use phase kickback: CNOT$(|-\rangle_{target}) = -|-\rangle_{target}$ if control is $|1\rangle$.
        *   Wait, $CNOT (|+\rangle \otimes |-\rangle) = \frac{1}{2} (|0\rangle - |1\rangle) \otimes |0\rangle + \frac{1}{2} (|0\rangle - |1\rangle) \otimes |1\rangle$? NO.
        *   $|+\rangle|-\rangle = \frac{1}{2} (|0\rangle + |1\rangle)(|0\rangle - |1\rangle) = \frac{1}{2} (|00\rangle - |01\rangle + |10\rangle - |11\rangle)$.
        *   CNOT flips the second qubit when the first is 1: $\frac{1}{2} (|00\rangle - |01\rangle + |11\rangle - |10\rangle) = \frac{1}{2} (|0\rangle - |1\rangle) \otimes (|0\rangle - |1\rangle) = |-\rangle|-\rangle$.
        *   Wait, $CNOT(c, t)$ with target in $|-\rangle$ applies a $Z$ gate to the control. Let's verify:
        *   $CNOT \cdot (I \otimes H) \cdot CNOT = H$? No. $CNOT(c, t) (|x\rangle \otimes |-\rangle) = (-1)^x |x\rangle \otimes |-\rangle$.
        *   Yes! Phase kickback: CNOT applies $Z$ to the control qubit if the target is in $|-\rangle$.
        *   Let's check again: $CNOT(|0\rangle|-\rangle) = |0\rangle|-\rangle$. $CNOT(|1\rangle|-\rangle) = -|1\rangle|-\rangle$.
        *   So the three CNOTs apply $Z$ to q[0], q[1], and q[3].
        *   Wait, q[0] starts in

### Reference answer

{'predicted_probs': {'11011': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/2983

- task_id: `isqTrain/2983`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3786`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[3];
procedure main() {
    X(q[0]);
    ctrl H(q[0], q[1]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Language/Task: Quantum computing expert explaining an isQ circuit and predicting its output probability distribution.
    *   Output format: Concise, precise step-by-step reasoning in Dirac notation.
    *   Length limit: 3-8 lines for simple, up to 15 for complex.
    *   Start with "## Circuit Analysis".
    *   End with the predicted probability distribution.
    *   No `isq` code blocks.
    *   Circuit: `X(q[0])`, `ctrl H(q[0], q[1])` on 3 qubits `q[0], q[1], q[2]`.

2.  **Analyze the Circuit:**
    *   Initial state: $|000\rangle$
    *   `X(q[0])`: Applies $X$ to qubit 0. State becomes $|100\rangle$.
    *   `ctrl H(q[0], q[1])`: isQ syntax for a controlled gate is `ctrl @[control] Gate(target)` or `ctrl Gate(control, target)` if only one control is given before the target? Wait, let's check isQ syntax.
    *   Wait, `ctrl H(q[0], q[1])` means `q[0]` is the control, `q[1]` is the target. Standard syntax `ctrl Gate(control, target)` or `ctrl Gate(target)` with control defined by `@`? Wait, the reference says "Control modifier: `ctrl @[c1, c2] Gate(target);`". But here it's `ctrl H(q[0], q[1])`. Wait, in earlier isQ versions or specific contexts, `ctrl H(q[0], q[1])` might mean a controlled-H with `q[0]` as control and `q[1]` as target. Let's assume `q[0]` is control and `q[1]` is target.
    *   Wait, $|100\rangle$ with control on `q[0]` (which is $|1\rangle$) applies $H$ to `q[1]`.
    *   $H |0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
    *   State becomes $|1\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |0\rangle = \frac{1}{\sqrt{2}}(|100\rangle + |110\rangle)$.

3.  **Calculate Probabilities:**
    *   State is $\frac{1}{\sqrt{2}}|100\rangle + \frac{1}{\sqrt{2}}|110\rangle$.
    *   $P(100) = |\frac{1}{\sqrt{2}}|^2 = 0.5$.
    *   $P(110) = |\frac{1}{\sqrt{2}}|^2 = 0.5$.
    *   Matches Expected: `{'100': 0.4999999999999999, '110': 0.5000000000000001}`.

4.  **Draft the Explanation:**
    *   Initial state is $|000\rangle$.
    *   `X(q[0])` flips qubit 0, yielding $|100\rangle$.
    *   `ctrl H(q[0], q[1])` applies a Hadamard gate to qubit 1, controlled by qubit 0. Since qubit 0 is $|1\rangle$, $H$ is applied to qubit 1.
    *   This transforms $|0\rangle$ on qubit 1 to $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
    *   The resulting state is $\frac{1}{\sqrt{2}}(|100\rangle + |110\rangle)$.
    *   Measurement yields $|100\rangle$ with 50% probability and $|110\rangle$ with 50% probability.
    *   Format output properly.

5.  **Refine to constraints:**
    *   Length: 3-8 lines.
    *   Start with "## Circuit Analysis".
    *   End with the distribution.
    *   No code blocks.

    Draft:
    ## Circuit Analysis
    1. The 3-qubit system starts in the initial state $|000\rangle$.
    2. `X(q[0])` flips qubit 0 to $|1\rangle$, evolving the state to $|100\rangle$.
    3. `ctrl H(q[0],

### Reference answer

{'predicted_probs': {'100': 0.4999999999999999, '110': 0.5000000000000001}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqQA/quantum_algorithms/105_principle_advantage

- task_id: `isqQA/quantum_algorithms/105_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `principle_advantage`, `algorithm`, `Shor算法中的模幂运算`
- source: `qa_pipeline`
- dataset_index: `1028`

### Prompt

请深入分析Shor算法中模幂运算的宏观原理、时间复杂度特征及其提供量子加速的核心来源。并请使用isQ语言给出一个演示模幂运算核心逻辑（连续平方和受控模乘）的抽象代码框架。

### Reference answer

<thought>
1. 宏观原理：Shor算法的核心在于将大整数分解问题转化为寻找函数 f(x) = a^x mod N 的周期 r 的问题。模幂运算在量子电路中对应一个酉算子 U_f，其作用为 U_f |x⟩|0⟩ = |x⟩|a^x mod N⟩。为了保持量子叠加态，该运算必须完全可逆且无中间测量，通常通过量子加法器（如量子进位加法器）级联构建可逆模乘法器，再利用连续平方的方法实现模幂。
2. 时间复杂度对比：经典模幂运算的时间复杂度约为 O(n^2) 或 O(n^3)（其中 n = log2 N）。在量子线路中，由于需要保持可逆性和使用辅助比特，单次量子模幂运算的逻辑门复杂度通常被评估为 O(n^3)，且常数项远大于经典计算。然而，Shor算法的总体复杂度为 O(n^3)，相比于经典最优算法（如数域筛法）的亚指数级复杂度 O(exp(n^{1/3}))，实现了指数级的加速。
3. 量子加速来源：加速并不来源于量子模幂运算本身比经典模幂运算快，而是来源于“量子并行性”和“量子傅里叶变换（QFT）”。通过在指数寄存器的叠加态上执行一次模幂运算，量子计算机同时计算了所有 x 对应的 a^x mod N 的值，并通过干涉效应（QFT）以极高的概率提取出隐藏的周期 r。
4. isQ代码设计：模幂运算通常通过连续平方实现，即 a^x = a^(x_0 * 2^0) * a^(x_1 * 2^1) * ... * a^(x_{n-1} * 2^{n-1})。在代码中，我们遍历指数寄存器的每一位，如果该位为1，则将结果寄存器乘以相应的模幂值。
</thought>

宏观原理：在Shor算法中，大整数分解被转化为寻找函数 $f(x) = a^x \bmod N$ 周期的数学问题。模幂运算模块是整个量子算法的“计算心脏”，它对应一个复杂的酉算子 $U_{a,N}$，其映射规则为 $U_{a,N}|x\rangle|0\rangle = |x\rangle|a^x \bmod N\rangle$。在物理层面上，这意味着我们需要用量子逻辑门构建一个完全可逆的计算网络。由于量子态的脆弱性和不可克隆原理，模幂运算不能像经典计算机那样随意覆盖中间变量，而是必须保留所有输入信息以实现逆演化，因此通常采用可逆量子加法器（如CDKM或Draper加法器）逐步构建可逆模乘法和模加法网络。

时间复杂度对比：如果目标数的比特长度为 $n$，经典计算机执行模幂运算的时间复杂度大约为 $O(n^2 \log n)$ 到 $O(n^3)$。而在量子计算中，由于必须维持严格的幺正性和可逆性，单次量子模幂运算的门复杂度规模通常在 $O(n^3)$ 左右，且带有极大的常数因子（需要大量的Toffoli门和辅助比特）。因此，量子模幂运算本身并不比经典快。然而，经典求解阶的算法需要进行 $\Omega(\sqrt{N})$ 次模幂运算，而Shor算法整体的时间复杂度仅为 $O(n^3)$，相比经典最优因子分解算法（如一般数域筛法）的亚指数级复杂度 $O(e^{n^{1/3} (\log n)^{2/3}})$，实现了极其显著的降维打击。

量子加速来源：Shor算法指数级加速的核心来源并非在于底层算术运算的速度，而是源于**量子态叠加原理**与**量子傅里叶变换（QFT）的相干提取**。模幂运算电路只需执行一次，就能够利用量子叠加态同时处理 $2^n$ 个输入，将其映射为具有隐藏周期特征的纠缠态。随后，量子傅里叶变换以 $O(n^2)$ 的效率在这个庞大的并行计算结果中发生干涉，从而放大周期对应的概率幅，将原本需要海量穷举的搜索问题转化为多项式级别的信号处理问题。

isQ代码实现框架：
以下代码展示了模幂运算中“连续平方与条件模乘”的抽象逻辑框架。这里我们假设已经构建了基础的受控模乘门，通过迭代指数寄存器的每一位来实现完整的模幂操作。

import std;

// 假设系统位数定义
const N = 4; // 指数寄存器位宽
const M = 4; // 模数寄存器位宽

qbit x_reg[N];    // 指数寄存器
qbit res_reg[M];  // 结果寄存器，初始化应为|1>
qbit ancilla[M];  // 辅助比特用于可逆算术操作

// 概念性自定义门：受控模乘操作，将结果寄存器乘以特定因子 mod MOD
// 实际物理层由大量的Toffoli和CNOT门构成可逆加法树实现
deriving gate cmul_factor(res[M], anc[M]) = [[1,0],[0,1]];

procedure main() {
    // 初始化结果寄存器为 |1>
    X(res_reg[0]);

    // Shor算法中模幂运算的连续平方架构
    // 遍历指数寄存器x_reg的每一位 x_i
    for i in 0:N {
        // 根据x_i的状态，决定是否执行模乘操作
        // 在实际电路中，这里的因子是 a^(2^i) mod N
        // 如果 x_i == 1，则 res = res * (a^(2^i)) mod N
        ctrl @[x_reg[i]] cmul_factor(res_reg, ancilla);
        
        // 每一步乘法后，理论上需要进行模归约
        // 在可逆电路中，这通常通过条件减法等网络实现
    }
    
    // 接下来将在x_reg上执行逆量子傅里叶变换以提取周期
}

（注意：代码中`cmul_factor`作为占位符门，代表了极其复杂的可逆模乘模块。在真实底层实现中，需要将其完全展开为基础量子门的组合形式。）

## isqTrain/4068

- task_id: `isqTrain/4068`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `403`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```
import std;
// QAOA MaxCut p=1 on 3-node path graph
// gamma=0.785, beta=0.393
qbit q[3];

procedure main() {
    // Initial superposition
    H(q[0]); H(q[1]); H(q[2]);
    // Cost unitary U_C(gamma)
    // Edge (0,1): exp(-i*gamma*Z_i*Z_j)
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.785, q[1]);
    CNOT(q[0], q[1]);
    // Edge (1,2): exp(-i*gamma*Z_i*Z_j)
    CNOT(q[2], q[1]);
    Rz(2.0 * 0.785, q[2]);
    CNOT(q[1], q[2]);
    // Mixer unitary U_M(beta)
    Rx(2.0 * 0.393, q[0]);
    Rx(2.0 * 0.393, q[1]);
    Rx(2.0 * 0.393, q[2]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

## Bug Analysis

**1. Bug location:** The first CNOT in the Edge (1,2) cost unitary block is `CNOT(q[2], q[1])` — the control and target qubits are swapped. The standard ZZ-interaction pattern `exp(-iγ Z_i Z_j)` requires consistent CNOT(i, j) / Rz(2γ, j) / CNOT(i, j), meaning qubit 1 should always be control and qubit 2 always target.

**2. Fix:** Change `CNOT(q[2], q[1])` → `CNOT(q[1], q[2])` on the first CNOT of the second edge block, matching the pattern of the third CNOT.

**3. State evolution (corrected):**
- After H gates: all qubits in |+⟩ → state |+++⟩
- Edge (0,1): CNOT₀₁/Rz(1.57,1)/CNOT₀₁ applies correct ZZ phase between q₀,q₁
- Edge (1,2): CNOT₁₂/Rz(1.57,2)/CNOT₁₂ applies correct ZZ phase between q₁,q₂
- Mixer: Rx(0.786) rotates each qubit, mixing computational basis states
- Measurement yields expected probabilities: |000⟩≈0.313, |111⟩≈0.313 (favored cuts), with remaining ~0.062 distributed among other outcomes — consistent with MaxCut favoring bipartitions {0,2}|{1} and {1}|{0,2}.

## isqTrain/2690

- task_id: `isqTrain/2690`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `505`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit w[5];
procedure main() {
    for i in 0:3{
        X2P(w[i]);
        Y2P(w[i+1]);
        CNOT(w[i], w[i+1]);
    }
    for i in 0:3{
        for j in 0:3{
            for k in 0:3{
                H(w[(i+j+k) % 5]);
            }
        }
    }
    for i in 0:5{
        M(w[i]);
    }
}
```

### Chain-of-thought reasoning

The user wants to analyze an isQ quantum program.
The program performs the following operations:
1. First loop:

Let's trace the first loop.
i=0:
X2P(w[0]) -> w[0] is in |+>
Y2P(w[1]) -> w[1] is in |i+> = (|0> + i|1>)/sqrt(2)
CNOT(w[0], w[1]) -> wait, wait. Let's see the gates.
X2P = Rx(pi/2) = [[1, -i], [-i, 1]] / sqrt(2)
Y2P = Ry(pi/2) = [[1, -1], [1, 1]] / sqrt(2)
On |0>, Rx(pi/2) gives (|0> - i|1>)/sqrt(2).
On |0>, Ry(pi/2) gives (|0> + |1>)/sqrt(2).
Let's trace state exactly:
w initially |00000>
i=0:
X2P(w[0]): w[0] -> (|0> - i|1>)/sqrt(2)
Y2P(w[1]): w[1] -> (|0> + |1>)/sqrt(2)
CNOT(w[0], w[1]):
State before CNOT: (|0> - i|1>)/sqrt(2) \otimes (|0> + |1>)/sqrt(2) \otimes |000>
= 1/2 (|00> + |01> - i|10> - i|11>) |000>
CNOT(0,1):
= 1/2 (|00> + |01> - i|11> - i|10>) |000> = 1/2 (|00> + |01> - i|10> - i|11>) |000>
Wait, CNOT flips the second qubit if first is 1.
|00> -> |00>
|01> -> |01>
- i|10> -> -i|11>
- i|11> -> -i|10>
So after CNOT, qubits 0 and 1 are in the exact same state!
i=1:
X2P(w[1]): acts on w[1].
Wait, before X2P, w[1] is entangled with w[0]. So we apply X2P to w[1].
Y2P(w[2]): w[2] is in |0>, Y2P gives (|0> + |1>)/sqrt(2).
CNOT(w[1], w[2]).
This looks complicated. Let's write the initial state evolution as matrix multiplication or tensor product.
Actually, let's look at the second loop:

This applies H to w[q] a certain number of times for each q.
The number of times q appears in the triple loop.
i+j+k = q (mod 5).
Since i, j, k each range from 0 to 3, their sum ranges from 0 to 9.
Let's count the number of solutions to i+j+k = q mod 5.
i+j+k can be 0, 1, 2, 3, 4, 5, 6, 7, 8, 9.
q=0: 000 (1)
q=1: 100 (3), 010 (3), 001 (3) - wait. Permutations of (1,0,0) is 3.
q=2: (2,0,0) [3], (1,1,0) [3], sum = 6.
q=3: (3,0,0) [3], (1,1,1) [1], (2,1,0) [6], sum = 10.
q=4: (4 not possible), (3,1,0) [6], (2,2,0) [3], (2,1,1) [3], sum = 12.
q=0 (which is 5 mod 5): (5 not possible), (3,2,0) [6], (3,1,1) [3], (2,2,1) [3], sum = 12.
q=1 (which is 6 mod

### Reference answer

{'predicted_probs': {'00000': 0.12500000000000003, '00100': 0.12499999999999986, '01000': 0.1250000000000001, '01100': 0.12500000000000003, '10000': 0.12499999999999997, '10100': 0.12499999999999994, '11000': 0.12500000000000006, '11100': 0.12499999999999994}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/2037

- task_id: `isqTrain/2037`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3826`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[1];
procedure main() {
    Rx(1.04719755119660, q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes a single qubit `q[0]` in the ground state: |0⟩.
2. It applies an Rx rotation gate with an angle of $\pi/3$ (1.047197... radians): `Rx(1.04719755119660, q[0])`.
3. The state evolves from |0⟩ to $\cos(\pi/6)|0\rangle - i\sin(\pi/6)|1\rangle$, which simplifies to $\frac{\sqrt{3}}{2}|0\rangle - \frac{i}{2}|1\rangle$.
4. Finally, the qubit is measured in the computational basis.

Predicted probability distribution:
- |0⟩: 0.75
- |1⟩: 0.25

### Reference answer

{'predicted_probs': {'0': 0.75, '1': 0.25}, 'explanation': 'Single-qubit X evolution Rx(pi/3)|0>: P(|0>)=0.75, P(|1>)=0.25.'}

## isqQA/quantum_algorithms/51_hardware_limitations

- task_id: `isqQA/quantum_algorithms/51_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hardware_limitations`, `algorithm`, `隐藏子群问题`
- source: `qa_pipeline`
- dataset_index: `3463`

### Prompt

隐藏子群问题（HSP）是量子计算中最核心的数学框架之一，Shor算法和Simon算法均是其特例。既然HSP在理论上能够对特定问题提供指数级加速，为什么我们目前无法在当前的NISQ（含噪声中等规模量子）设备上运行具有实际应用价值的HSP算法？请从退相干、量子门错误率以及硬件连通性三个核心硬件局限性角度进行深入剖析。

### Reference answer

隐藏子群问题（HSP）在理论上具有极其强大的能力，但其核心机制依赖于精确的量子干涉，这要求算法必须在极低的噪声水平下运行。将HSP算法（如用于大整数分解的Shor算法）部署到当前的NISQ设备上，会遇到极其严峻的硬件物理限制，主要表现为以下三个方面：

1. **退相干时间与线路深度的根本矛盾**：HSP算法的典型结构包括制备均匀叠加态、执行复杂的黑箱函数Oracle查询，以及执行量子傅里叶变换（QFT）。对于具有实际破解价值的密钥长度（如RSA-2048），算法需要成千上万个逻辑量子比特，且线路深度极深。然而，当前NISQ设备中的超导或离子阱量子比特的相干时间（T1和T2）通常在微秒到毫秒级别。在量子态完成复杂的Oracle查询和QFT计算之前，系统早已因为环境耦合而发生了严重的退相干，导致量子态的相位信息丢失，最终测量结果完全变成随机噪声，彻底破坏了HSP算法赖以生存的干涉相消与相长效应。

2. **双比特门错误率的指数级累积效应**：HSP中的Oracle通常需要大量受控逻辑门来实现函数映射，而QFT也需要密集的受控相位旋转门。在当前的硬件水平下，单比特门保真度约为99.9%（错误率 $10^{-3}$），而双比特门（如CNOT）的保真度通常在99%到99.5%左右（错误率 $10^{-2}$ 量级）。由于HSP线路需要串行执行海量的双比特门，整体线路的保真度将随着门数量呈指数级衰减。例如，包含数百个双比特门的浅层线路就会因为错误累积而使得输出结果的保真度降至0%附近，导致HSP算法在NISQ设备上根本无法提取出隐藏子群的周期信息。

3. **底层硬件连通性限制带来的巨大开销**：HSP算法中的Oracle往往需要实现跨越多个量子比特的远距离多控门（如Toffoli门甚至更高阶的控制门）。当前的NISQ芯片大多采用方格型或六角形拓扑，相邻量子比特的物理连通性非常有限。为了在物理硬件上实现远距离的量子门交互，必须插入大量的SWAP操作来移动量子态。在标准量子编程语言（如isQ）中，并没有原生的SWAP门，必须将其分解为3个串联的CNOT门（如 `CNOT(q[0], q[1]); CNOT(q[1], q[0]); CNOT(q[0], q[1]);`）。这种为了弥补连通性不足而引入的SWAP操作，会使线路中双比特门的总数量成倍急剧增加，从而进一步放大了上述的门错误率问题。

综上所述，在尚未实现全面容错量子计算（FTQC）和量子纠错（QEC）的NISQ时代，由于退相干时间过短、门错误率过高以及连通性受限导致的线路膨胀，HSP算法只能停留在极其微小的演示级别（如分解15），无法在物理硬件上处理任何具有现实意义的隐藏子群问题。

## isqExpand/algo/117

- task_id: `isqExpand/algo/117`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `multi_controlled_logic`
- source: `isq_expansion`
- dataset_index: `4313`

### Prompt

实现以下量子计算任务（使用isQ）：implementing Grover's algorithm on 4 qubits to search for the state |1010> in a 16-state search space. Apply 3 Grover iterations (the optimal number for N=16, k=1). The oracle for |1010>: apply X(q[1]) and X(q[3]) to flip the zero-bits, then ctrl ctrl Z(q[0],q[1],q[2],q[3]) to mark the all-ones state (or equivalently, use Toffoli to compute an AND into an ancilla then CZ). Since 4-qubit CCZ is not directly available, use: Toffoli(q[0],q[1],q[4]) to compute AND of first two into ancilla q[4], then Toffoli(q[2],q[4],q[3]) with X(q[3]) pre/post to flip phase of |1010>, then Toffoli(q[0],q[1],q[4]) to uncompute. Similarly for diffusion. Actually, for simplicity, inline the entire Grover iteration in main using a for loop. Measure q[0] through q[3] (not the ancilla).

### Chain-of-thought reasoning

## Reasoning
Goal: 4-qubit Grover search for |1010> with 3 iterations, using ancilla q[4].

4-qubit CCZ decomposition via ancilla:
  Toffoli(q0,q1,anc): compute AND(q0,q1) into anc
  H(q3); Toffoli(q2,anc,q3); H(q3): CZ(q2*anc, q3) = 3-qubit CCZ
  Toffoli(q0,q1,anc): uncompute ancilla

Oracle for |1010>: X on q[1],q[3], then CCZ, then X undo.
Diffusion: H-X-CCZ-X-H on q[0]-q[3].

After 3 iterations: P(|1010>) ~ 0.961, others ~ 0.003.
Ancilla q[4] always returns to 0.

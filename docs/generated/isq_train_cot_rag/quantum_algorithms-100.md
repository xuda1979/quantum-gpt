# ISQ training COT RAG corpus: quantum_algorithms shard 100

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqQA/quantum_algorithms/125_principle_advantage

- task_id: `isqQA/quantum_algorithms/125_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `principle_advantage`, `algorithm`, `相位回踢机制`
- source: `qa_pipeline`
- dataset_index: `3810`

### Prompt

在量子算法设计中，“相位回踢”是实现量子加速的核心机制之一。能否详细解释其宏观物理原理？并以控制酉操作提取特征相位为例，分析其带来的时间复杂度优势及量子加速的根本来源？最后，请使用isQ语言编写一段代码，演示如何通过控制门将目标比特的本征相位回踢到控制比特上。

### Reference answer

相位回踢是量子计算中极为精妙的一种干涉现象，它是Shor算法、量子相位估计（QPE）以及HHL算法等诸多高级量子算法的基石。

宏观物理原理：在量子力学中，当一个处于叠加态的控制比特控制一个酉操作作用于目标寄存器时，如果目标寄存器恰好处于该酉算子的本征态，由于量子力学的线性性质，目标寄存器的状态不会发生改变，但本征态对应的本征值（通常是一个全局相位 $e^{i\phi}$）会“回踢”并转化为控制比特的相对相位。数学上可表示为：$\frac{1}{\sqrt{2}}(|0\rangle_c + |1\rangle_c) \otimes |u\rangle_t \xrightarrow{C-U} \frac{1}{\sqrt{2}}(|0\rangle_c + e^{i\phi}|1\rangle_c) \otimes |u\rangle_t$。此时，目标系统的内部相位信息被成功提取并编码到了控制系统的概率幅中。

时间复杂度对比与量子加速来源：在经典计算中，提取一个黑盒酉算子特征值的相位，通常需要多次演化并采样，往往需要 $O(1/\epsilon)$ 甚至指数级的时间复杂度才能达到 $\epsilon$ 的精度。而在量子计算中，利用相位回踢机制，我们可以让多个控制比特分别控制不同演化时长（如 $2^j$ 次）的酉操作，并行地将相位信息以二进制形式回踢到各控制比特上。随后结合逆量子傅里叶变换，仅需 $O(\log(1/\epsilon))$ 的时间复杂度即可高精度提取相位。量子加速的根本来源在于量子态的叠加性与相长/相消干涉：相位回踢巧妙地利用了控制比特与目标系统的纠缠，将不可直接观测的全局相位转化为可直接测量的相对相位，再通过量子干涉将目标相位信号放大提取。

以下是一个使用isQ语言编写的演示代码。我们将控制比特初始化为 $|+\rangle$ 态，目标比特初始化为 $|1\rangle$ 态（这是泡利 $Z$ 门的本征态，对应本征值 $-1$，即相位 $\pi$）。通过执行 $CZ$ 门，相位 $\pi$ 被回踢给控制比特，使其从 $|+\rangle$ 翻转为 $|\rangle$：

```isq
import std;

qbit q[2]; // q[0]为控制比特，q[1]为目标比特

procedure main() {
    // 将控制比特 q[0] 初始化为 |+> 态
    H(q[0]);
    
    // 将目标比特 q[1] 初始化为 |1>，这是 Z 门的特征态，特征值为 -1
    X(q[1]);

    // 执行受控Z门 (CZ)
    // 对于目标态 |1>，Z 门作用产生相位 -1 (即 e^(i*pi))
    // 通过相位回踢机制，这个 pi 相位被加到了控制比特的 |1> 分量上
    CZ(q[0], q[1]);

    // 此时，控制比特的状态已经从 |+> 变成了 |->
    // 再次施加 H 门进行基矢变换，以验证干涉结果
    H(q[0]);

    // 测量控制比特
    // 预期结果：由于 |+> 变成了 |->，再经过 H 门会变成 |1>
    // 因此测量将以 100% 的概率得到 1，证明相位回踢成功翻转了相对相位
    int r = M(q[0]);
    
    // 为了直观展示，如果测得0（理论上概率为0），我们在目标比特做标记
    // 在无噪音的理想情况下，此 if 块不会被执行
    if (r == 0) {
        X(q[1]);
    }
}
```

## isqTrain/3507

- task_id: `isqTrain/3507`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `basis_change`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `4384`

### Prompt

Predict the output probabilities of the following quantum circuit:

```
import std;

qbit q[3];

procedure main() {
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    H(q[0]); H(q[1]); H(q[2]);

    H(q[0]); H(q[1]); H(q[2]);
    CNOT(q[0], q[2]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict the output probability distribution of a given isQ program.
    *   Format: "## Circuit Analysis" followed by step-by-step reasoning, ending with the distribution.
    *   Constraint: Concise (3-15 lines).
    *   State: Start with initial state $|000\rangle$.

2.  **Analyze the isQ Code:**
    *   `qbit q[3];` -> 3 qubits, initial state $|000\rangle$.
    *   `CNOT(q[0], q[1]);`
    *   `CNOT(q[0], q[2]);`
        *   After CNOTs: $|000\rangle$ (CNOTs don't change $|000\rangle$).
    *   `H(q[0]); H(q[1]); H(q[2]);`
        *   After first round of Hs: $H^{\otimes 3}|000\rangle = |+++\rangle$.
    *   `H(q[0]); H(q[1]); H(q[2]);`
        *   After second round of Hs: $H^{\otimes 3}|+++\rangle = |000\rangle$.
    *   `CNOT(q[0], q[2]);`
    *   `CNOT(q[0], q[1]);`
        *   After second round of CNOTs: CNOTs on $|000\rangle$ leave it as $|000\rangle$.
    *   `M(q[0]); M(q[1]); M(q[2]);`
        *   Measurement on $|000\rangle$.

3.  **Trace State Evolution step-by-step:**
    *   Initial: $|000\rangle$
    *   CNOT 0->1, 0->2: State remains $|000\rangle$ since control is $|0\rangle$.
    *   H on 0, 1, 2: State becomes $|+++\rangle = \frac{1}{\sqrt{8}} \sum_{x \in \{0,1\}^3} |x\rangle$.
    *   H on 0, 1, 2 again: $H \cdot H = I$, so state returns to $|000\rangle$.
    *   CNOT 0->2, 0->1: State remains $|000\rangle$ since control is $|0\rangle$.
    *   Final state before measurement: $|000\rangle$.
    *   Predicted probability distribution: 100% chance of measuring $|000\rangle$.

4.  **Draft the Response:**
    *   Keep it concise.
    *   Start with "## Circuit Analysis".
    *   No markdown isq blocks.

    *Draft:*
    ## Circuit Analysis
    1. Initial state is $|000\rangle$.
    2. First CNOTs (0->1, 0->2) leave the state as $|000\rangle$ because $q_0$ is $|0\rangle$.
    3. Applying H to all qubits transforms the state to $|+++\rangle$.
    4. Applying H again to all qubits reverses the previous step, returning the state to $|000\rangle$.
    5. Second CNOTs (0->2, 0->1) leave the state as $|000\rangle$ because $q_0$ is $|0\rangle$.
    6. The final state before measurement is exactly $|000\rangle$.
    7. The predicted probability distribution is 100% for the basis state $|000\rangle$.

5.  **Review against constraints:**
    *   Starts with "## Circuit Analysis"? Yes.
    *   Uses Dirac notation? Yes.
    *   Concise (3-8 lines)? Yes, it's 7 lines.
    *   no code blocks? Yes.
    *   Ends with distribution? Yes.

6.  **Final Polish:**
    Make it punchy.
    ## Circuit Analysis
    1. Initial state is $|000\rangle$.
    2. The first two CNOTs act on $|0\rangle$ controls, leaving the state unchanged as $|000\rangle$.
    3. The first layer of Hadamard gates transforms the state to $|+++\rangle$.
    4. The second layer of Hadamard gates ($H \cdot H = I$) reverts the state back to $|000\rangle$.
    5. The final two CNOTs again act on $|0\rangle$ controls,

### Reference answer

{'predicted_probs': {'000': 1.0}, 'explanation': 'The output is |000> with probability 1.0'}

## isqTrain/2988

- task_id: `isqTrain/2988`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `408`

### Prompt

实现以下量子计算任务（使用isQ）：implements a SWAP gate using three CNOT gates. Initialize the qubits to |01>, apply the SWAP, and measure both qubits.

Requirements:
- Declare `qbit q[2];` at global scope.
- Measure both qubits.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement a swap operation (three-CNOT decomposition) using three CNOT gates, initializing to |01⟩ and measuring both qubits.
2. Two qubits q[0], q[1] are declared globally; both are measured.
3. State evolution (starting from |00⟩):
   - X(q[1]): |00⟩ → |01⟩
   - CNOT(q[0], q[1]): control=0, no flip → |01⟩
   - CNOT(q[1], q[0]): control=1, flip target → |11⟩
   - CNOT(q[0], q[1]): control=1, flip target → |10⟩
4. The swap (three-CNOT decomposition) successfully exchanges the two qubit states, yielding final state |10⟩ with probability 1.0.

## isqTrain/4614

- task_id: `isqTrain/4614`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1657`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[1];

procedure main() {
    
    X(q[0]);
    X(q[0]);  // replaced H with X
    
    
    H(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Operations applied: X(q[0]), X(q[0]), H(q[0]), M(q[0]).
2. Initial state: |0>. 
3. First X gate flips the qubit to |1>. The second X gate flips it back to |0> (since X is its own inverse, XX = I).
4. The H gate puts the qubit into an equal superposition: H|0> = (1/sqrt(2))|0> + (1/sqrt(2))|1> = |+>.
5. Predicted measurement probabilities: {|0>: 0.5, |1>: 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 0.5000, P(|1>) = 0.5000.'}

## isqTrain/4183

- task_id: `isqTrain/4183`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `4879`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 1.000, q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    Rz(2.0 * 1.000, q[2]);
    CNOT(q[1], q[2]);
    CNOT(q[0], q[2]);
    Rz(2.0 * 1.000, q[2]);
    CNOT(q[0], q[2]);
    Rx(2.0 * 0.500, q[0]);
    Rx(2.0 * 0.500, q[1]);
    Rx(2.0 * 0.500, q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. Gates applied: H on all 3 qubits, three CNOT-Rz(2.0)-CNOT parity-phase sequences on pairs (q0,q1), (q1,q2), (q0,q2), then Rx(π) on all qubits.
2. After H⊗³: |ψ⟩ = |+++⟩ = (1/√8)Σ|x⟩. The CNOT-Rz(2.0)-CNOT on each pair applies Rz(2.0) to the target when control and target have different parities, accumulating phase factors across the superposition.
3. The three parity-phase blocks introduce relative phases on all computational basis states based on parity violations across each qubit pair, creating a complex phase pattern.
4. Final Rx(π) = X on all qubits flips |0⟩↔|1⟩ on each qubit. Due to the symmetric initial |+++⟩ state and symmetric gate structure, the output remains uniformly distributed.
5. Predicted probability distribution: Each basis state {000, 001, 010, 011, 100, 101, 110, 111} has equal probability P = 1/8 = 12.5%. The most likely outcomes are all equally likely.

### Reference answer

Uniform distribution across 8 states

## isqTrain/893

- task_id: `isqTrain/893`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `isq_syntax_deriving_gate`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2662`

### Prompt

What does this isQ program output when measured?

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
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial State:** The circuit starts in the $|00\rangle$ state.
2. **Hadamard Gates:** Applying H to both qubits prepares a uniform superposition: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
3. **Controlled-Z Gate:** The `ctrl my_z` acts as a CZ gate, flipping the phase of the $|11\rangle$ basis state. The state becomes $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle)$.
4. **Measurement:** Since measurement probabilities are the square of the amplitudes, the relative phase of -1 on $|11\rangle$ is invisible. All four states have an equal probability of $(1/2)^2 = 1/4$.

Predicted probability distribution: {|00>: 0.25, |01>: 0.25, |10>: 0.25, |11>: 0.25}

### Reference answer

{'predicted_probs': {'0': 0.24999999999999994, '1': 0.24999999999999994, '2': 0.25000000000000006, '3': 0.25}, 'explanation': 'Parametric variant of isqEval/257. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3514

- task_id: `isqTrain/3514`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `5690`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```
import std;

qbit q[2];

procedure main() {

    H(q[0]);

    CNOT(q[0], q[1]);

    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations**: The circuit initializes 2 qubits in |00>, applies a Hadamard gate to q[0], then a CNOT with q[0] as control and q[1] as target, and measures both.
2. **State evolution**:
   - Initial state: |00>
   - After H(q[0]): (|0> + |1>)/√2 ⊗ |0> = (|00> + |10>)/√2
   - After CNOT(q[0], q[1]): (|00> + |11>)/√2 (A maximally entangled Bell state)
3. **Measurement**: Measuring this state yields perfectly correlated outcomes.
4. **Predicted probability distribution**: 
   - |00>: 0.5
   - |11>: 0.5

### Reference answer

Probability distribution: |00>: 0.5, |11>: 0.5

## isqTrain/1099

- task_id: `isqTrain/1099`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `336`

### Prompt

Help me write isQ code that implements the bernstein_vazirani pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement Bernstein-Vazirani to find hidden string s=101 via phase kickback, with reversed measurement order (q[2], q[1], q[0]).

2. **Qubits**: 4 total (q[0-2] for input, anc[0] for phase); only q[0-2] are measured.

3. **State evolution**:
   - Initialize: |000⟩|0⟩
   - X+H on ancilla: |000⟩|−⟩
   - H on all q: (

## isqQA/quantum_algorithms/92_optimization_variant

- task_id: `isqQA/quantum_algorithms/92_optimization_variant`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `optimization_variant`, `algorithm`, `Simon算法原理`
- source: `qa_pipeline`
- dataset_index: `820`

### Prompt

Simon算法在隐子群问题和大数分解等量子计算基础理论中占据核心地位。尽管标准的Simon算法在大O符号下已经达到了指数级的量子加速，但其严格依赖于带有已知隐藏子群结构的特定可逆函数，并且需要多次测量以统计获取彼此线性独立的方程组来求解异或掩码。请问针对原始Simon算法的这些局限性，目前学术界提出了哪些重要的改进版本或变体？这些变体在降低查询复杂度、放宽黑盒限制或提升抗噪能力方面具体是如何进行优化的？

### Reference answer

原始的Simon算法虽然理论上证明了指数级加速，但在实际应用中面临着查询次数需达到O(n)以获取n-1个线性独立方程、黑盒必须是严格双射且周期性完美、以及量子态测量带来的统计波动误差等问题。为了突破这些局限，学术界从降低查询复杂度、放宽Oracle条件以及提升鲁棒性三个核心维度提出了多种改进版本和变体。

首先是查询复杂度的优化变体。标准Simon算法需要执行大约4n次查询以确保高概率获得满秩的线性方程组。研究者引入了经典后处理的概率与线性代数优化技术，例如利用多项式时间的经典高斯消元结合生日悖论思想，将查询复杂度的常数因子显著降低。在渐近复杂度上，虽然渐进下界仍然是O(n)，但通过优化量子测量的概率分布提取策略，可以使得在O(n)的查询内以接近1的概率提取出所有必需的基底向量。

其次，最为著名的变体是放宽Oracle周期性限制的鲁棒性变体。在实际密码学场景（如攻击采用ECB模式的块加密）中，函数往往并非完美的满足Simon承诺（即存在某些非周期性碰撞）。Kaplan等人提出的变体及后续的统计区分器方法，证明了当函数以较高概率满足$f(x) = f(x \oplus s)$时，Simon算法依然能够提取出秘密字符串。此类变体通过重新计算量子态经Hadamard变换后的概率分布，发现即便存在噪声或伪碰撞，测量结果仍会高度集中在与掩码s正交的子空间中。通过引入如 Katz-Sahai框架或统计距离分析，改进算法能够以多项式对数级别的重复次数过滤掉噪声，从而极大拓宽了算法在侧信道攻击和对称密码分析中的实用性。

另外，在量子线路深度优化方面，针对NISQ（嘈杂中等规模量子）时代的变体也有所提出。由于深电路容易受到退相干影响，研究者提出了利用变分量子算法（VQA）框架来模拟Simon算法的子空间投影过程。这类变体将寻找正交子空间的代价函数编码为参数化量子线路的最优化问题，通过经典优化器更新参数，将原本需要级联多级Oracle查询的深度降低，从而提升了在物理量子硬件上的抗噪能力。

从理论推导上看，Simon问题本质上是寻找有限阿贝尔群隐藏子群问题（HSP）的一个特例。通过傅里叶采样优化，后续的理论变体将其扩展到了非阿贝尔群以及对带相位量子态的特征提取。在计算复杂性上，这些变体维持了量子算法在查询模型下的指数分离优势，即量子查询复杂度为$\Theta(n)$，而经典随机算法需要$\Omega(2^{n/2})$。

为了展示基础Simon算法量子线路的实现结构，以下提供使用isQ语言编写的标准Simon算法核心过程代码。在此代码中，我们假设Oracle已知并在量子线路上实现了$U_f|x\rangle|0\rangle = |x\rangle|x \oplus f(x)\rangle$，通过Hadamard变换和测量提取与s正交的向量。对于鲁棒性变体，只需在相同线路上增加重复测量与经典统计后处理模块即可。

```isQ
import std;

const int N = 3;
qbit q[N];
qbit ancilla[N];

// 假设该门实现了黑盒函数 f(x) 及其异或运算
// 这里用一个假想的对称操作代替具体的密码函数映射
deriving gate oracle = [[...]]; 

procedure main() {
    // 初始化第一寄存器为均匀叠加态
    for i in 0:N {
        H(q[i]);
    }
    
    // 应用黑盒Oracle U_f，将结果存储在ancilla中
    oracle(q, ancilla);
    
    // 对ancilla进行测量计算以坍缩状态（或者在理论分析中常忽略此步直接追踪系统）
    // 在某些优化变体中，对ancilla施以特定基的测量可降低第一寄存器的熵
    for i in 0:N {
        M(ancilla[i]);
    }
    
    // 再次对第一寄存器施加Hadamard变换
    for i in 0:N {
        H(q[i]);
    }
    
    // 测量第一寄存器，所得结果必定与隐藏字符串 s 正交
    // 多次运行收集线性方程组以解出 s
    for i in 0:N {
        M(q[i]);
    }
}
```

## isqTrain/341

- task_id: `isqTrain/341`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_inv`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `359`

### Prompt

Code this in isQ: implements a variant of the qft_subcircuit pattern using u[1] -> u[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The task is to analyze the provided isQ program, which implements a variant of the qft_subcircuit pattern.

1.  **Goal**: Implement a variant of the `qft_subcircuit` pattern using a 3-qubit register `u[3]` (instead of just `u[0]` or something similar) while keeping the additional qubits in the ground state, and perform QPE or a similar phase estimation task. Wait, looking at the code provided:
    The provided code has `qbit q[2];` and `qbit u[3];`.
    It initializes `u[0]` with `X(u[0]);`.
    It applies `H(q);`.
    It applies controlled `S` and `Z` from `q` to `u[0]`. Note: `q[1]` controls `S`, `q[0]` controls `Z`.
    It then applies the inverse QFT on `q`.
    Finally, it measures `q[0]` and `q[1]`.
    Wait, the prompt says "using u[1] -> u[3]". "using u[1] -> u[3]" might mean indices 1 to 3? Or length 3? Let's look at The implementation.
    The implementation: `qbit u[3];`. It only uses `u[0]`. The prompt says "The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state."
    Wait, my role is to *generate the reasoning* for the *circuit implementation* (or similar code) that achieves the specified outcome (probabilities {|01>: 1.0}).

    Let's trace The implementation:
    - `X(u[0])`: $|u_0 u_1 u_2\rangle = |100\rangle$
    - `H(q)`: $|q_0 q_1\rangle \to \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
    State is $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)_q \otimes |100\rangle_u$
    - `ctrl S(q[1], u[0])`:
        If $q_1=1$, apply $S$ to $u[0]$.
        $S |1\rangle = i|1\rangle$.
        So $|0\rangle_q \otimes |0\rangle_q$ remains same, $|0\rangle_q \otimes |1\rangle_q$ gets phase $i$? No, $q[1]$ is the second qubit in `q`. Let's write $q_0 q_1$ as standard.
        Basis states:
        $|00\rangle$: no phase
        $|01\rangle$: $q_1=1 \implies i$
        $|10\rangle$: $q_0=1 \implies$ no phase (next gate)
        $|11\rangle$: $q_1=1 \implies i$
    Wait, the code is:
    `ctrl S(q[1], u[0]);`
    `ctrl Z(q[0], u[0]);`
    $Z |1\rangle = -|1\rangle$.
    So:
    $|00\rangle$: phase 1
    $|01\rangle$: phase $i$
    $|10\rangle$: phase $-1$
    $|11\rangle$: phase $i \times -1 = -i$
    State of $q$: $\frac{1}{2}(|00\rangle + i|01\rangle - |10\rangle - i|11\rangle)$
    Let's rewrite this state.
    $\frac{1}{2}(1|00\rangle + e^{i\pi/2}|01\rangle + e^{i\pi}|10\rangle + e^{i3\pi/2}|11\rangle)$
    Wait, $-i = e^{-i\pi/2} = e^{i3\pi/2}$.
    So this is exactly the state after applying controlled $U, U^2$ etc. in QPE, where phase $\phi = 1/4$.
    Phase of $q_1$ (LSB) is $2\pi \phi = \pi/2$.
    Phase of $q_0$ (MSB) is $2 \times 2\pi \phi = \pi$.
    $|q_0 q_1\rangle \propto e^{i (q_0 \pi + q_1 \pi/2)}

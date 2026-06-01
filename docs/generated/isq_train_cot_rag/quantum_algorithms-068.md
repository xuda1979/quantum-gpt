# ISQ training COT RAG corpus: quantum_algorithms shard 68

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/algo/181

- task_id: `isqExpand/algo/181`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `Grover算法`, `量子搜索`, `振幅放大`, `最优迭代次数`
- source: `qa_pipeline`
- dataset_index: `543`

### Prompt

对于4-qubit Grover搜索（N=16），最优迭代次数是多少？如何推导？

### Chain-of-thought reasoning

首先回顾Grover搜索算法的核心原理：算法通过Grover迭代（Oracle + 扩散算子）不断放大标记态的振幅。对于N=16的搜索空间，标记项M=1时，初始振幅为1/√16=1/4，对应角度θ=arcsin(1/4)。经过k次迭代后，测量到标记态的概率为sin²((2k+1)θ)。令(2k+1)θ=π/2可求出最优k值，经数值计算k≈2.61。分别验证k=2和k=3的成功概率，k=3约为96.1%，k=2约为90.5%，因此k=3更优。也可用经典近似公式k≈π√N/4=π×4/4≈3.14快速估算。

### Reference answer

对于4-qubit Grover搜索（N=16，假设标记项M=1），最优迭代次数为3次。

推导过程如下：

1. 定义旋转角度θ：θ = arcsin(1/√N) = arcsin(1/√16) = arcsin(1/4) ≈ 0.2527 rad

2. Grover迭代的几何意义：每次迭代将状态向量在二维子空间中旋转2θ角度。经过k次迭代后，状态向量与标记态的夹角为(2k+1)θ。

3. 成功概率：P = sin²((2k+1)θ)。要使P最大，需(2k+1)θ ≈ π/2。

4. 求解k：k ≈ (π/(2θ) - 1)/2 ≈ π/(4θ) - 1/2

5. 代入数值：k ≈ π/(4 × 0.2527) - 0.5 ≈ 3.108 - 0.5 ≈ 2.61

6. 验证整数解：
- k=2时：(2×2+1)θ = 5θ ≈ 1.263 rad，P = sin²(1.263) ≈ 0.905
- k=3时：(2×3+1)θ = 7θ ≈ 1.769 rad，P = sin²(1.769) ≈ 0.961

7. 结论：k=3时成功概率最高（约96.1%），因此最优迭代次数为3。

近似公式：k ≈ ⌊π√N/4⌉，即k ≈ π×4/4 ≈ 3.14，四舍五入得3。

## isqTrain/3584

- task_id: `isqTrain/3584`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `basis_change`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3678`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should Second-order Trotter: XX+ZZ, dt=0.5, from |10>.

### Chain-of-thought reasoning

The buggy code has the following issue: in the first XX block, the CNOTs are inconsistent. Let me trace through:

Buggy first XX block:

Wait, let me look more carefully. In the buggy code:
- First CNOT is `CNOT(q[1], q[0])` - control=q[1], target=q[0]
- Second CNOT is `CNOT(q[0], q[1])` - control=q[0], target=q[1]

These are inconsistent - the CNOT pair doesn't form a proper conjugation. For the XX decomposition using H-CNOT-Rz-CNOT-H, both CNOTs should have the same control and target direction.

The standard decomposition of exp(-iθ XX) is:
H⊗I · CNOT(0,1) · (I⊗Rz(2θ)) · CNOT(0,1) · H⊗I

So both CNOTs should be `CNOT(q[0], q[1])`.

In the corrected version, both CNOTs in the first XX block are `CNOT(q[0], q[1])`.

The bug is specifically the first CNOT in the first XX block: `CNOT(q[1], q[0])` should be `CNOT(q[0], q[1])`.

Wait, but in the buggy code the second CNOT is also `CNOT(q[0], q[1])`. Let me re-read:

Buggy:

Fixed:

So the bug is that the first CNOT in the first XX block has reversed control/target. Both CNOTs should be `CNOT(q[0], q[1])` for the decomposition to work correctly.

Let me verify the state evolution with the corrected circuit:

Initial: |00>
After X(q[0]): |10>

After H⊗H: (|00> + |01> + |10> + |11>)/2 = (|0> + |1>)⊗(|0> + |1>)/2

Wait, let me be more careful. H⊗H applied to |10>:
H|1>⊗H|0> = |->⊗|+> = (|0>-|1>)/√2 ⊗ (|0>+|1>)/√2

After CNOT(q[0], q[1]) (control=q[0], target=q[1]):
= (|00>+|01>-|10>-|11>)/2 ... wait let me redo.

Actually let me just track. State after H⊗H on |10>:
= |->|+> = (1/2)(|00> + |01> - |10> - |11>)

CNOT(q[0],q[1]) with q[0] control, q[1] target:
|00> → |00>, |01> → |01>, |10> → |11>, |11> → |10>
= (1/2)(|00> + |01> - |11> - |10>)
= (1/2)(|00> + |01> - |10> - |11>)

Wait, that's the same. Actually |10> → |11> and |11> → |10>, so:
= (1/2)(|00> + |01> - |11> - |10>)
Hmm that's (1/2)(|00> + |01> - |10> - |11>), same as before. That doesn't seem right for the decomposition...

Actually, for the XX gate decomposition, the idea is:
XX = (H⊗I) · ZI · (H⊗I)

And controlled-Z is implemented via CNOT. The circuit for exp(-iθ XX) is:

H(q[1]) · CNOT(q[0],q[1]) · Rz(2θ, q[1]) · CNOT(q[0],q[1]) · H(q[1])

Or equivalently with H on both:
H(q[0]) · H(q[1]) · CNOT

## isqTrain/925

- task_id: `isqTrain/925`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `920`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[3];

procedure main() {
    // Set inputs: a=1, b=1
    X(q[0]); X(q[1]);
    // Compute XOR(a,b) into q[2]
    // CNOT from a, then CNOT from b accumulates XOR
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
    // Negate to get XNOR = NOT(XOR)
    X(q[2]);
    // XNOR(1,1) = NOT(0) = 1
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. Operations: X(q[0]), X(q[1]), CNOT(q[0], q[2]), CNOT(q[1], q[2]), X(q[2]).
2. State evolution:
   - Start: |000>
   - X(q[0]), X(q[1]): |110>
   - CNOT(q[0], q[2]): q[2] flips to 1 -> |111>
   - CNOT(q[1], q[2]): q[2] flips to 0 -> |110>
   - X(q[2]): q[2] flips to 1 -> |111>
3. Final state: |111>.
4. Predicted probability distribution: {|111>: 1.0}

### Reference answer

{'predicted_probs': {'7': 1.0}, 'explanation': 'Parametric variant of isqEval/263. Dimension: predict probabilities for reference circuit.'}

## isqTrain/2699

- task_id: `isqTrain/2699`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1679`

### Prompt

What does this isQ program output when measured?

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
    *   Task: Output probability distribution prediction of an isQ circuit.
    *   Format: Start with "## Circuit Analysis", follow rules (3-15 lines, use Dirac notation).
    *   Input circuit:
        
    *   Array length is 5 (`qbit q[5]`). `i` goes from 0 to 4.
    *   predicted output: Probability distribution for every basis state.

2.  **Trace the Circuit:**
    *   Initial state: $|00000\rangle$ (indices 4, 3, 2, 1, 0. Note: isQ q[0] to q[4] means q[0] is rightmost or leftmost? Usually `q[0]` is the highest bit in string representations or vice versa, but let's trace the tensor states explicitly or use parity).
    *   Actually, let's write out the state in terms of q[0] to q[4] vectors.
    *   Start: $|00000\rangle$
    *   `X(q[4])` -> $|00001\rangle$ (where q[0]q[1]q[2]q[3]q[4] = 00001)
    *   `H` on all 5 qubits:
        *   Since H applied to $|0\rangle$ gives $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$
        *   H applied to $|1\rangle$ gives $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$
        *   State becomes $|+\rangle_0 |+\rangle_1 |+\rangle_2 |+\rangle_3 |-\rangle_4 = \frac{1}{\sqrt{2^5}} \sum_{x \in \{0,1\}^4} (-1)^{x_4} |x_0 x_1 x_2 x_3 x_4\rangle$ (Wait, let's keep track of qubit 4's phase).
        *   More precisely: $|+\rangle^{\otimes 4} \otimes |-\rangle$.
    *   CNOTs: `CNOT(q[0], q[4])`, `CNOT(q[1], q[4])`, `CNOT(q[3], q[4])`.
        *   Target is `q[4]`. Control are `q[0]`, `q[1]`, `q[3]`.
        *   A CNOT with target `q[4]` and control `q[c]` flips `q[4]` when `q[c]` is 1.
        *   Effectively, `q[4]` gets XORed with `q[0]`, `q[1]`, `q[3]`.
        *   State before CNOTs: $\sum_{x} (-1)^{x_4} |x_0 x_1 x_2 x_3 x_4\rangle / 4$.
        *   Let $x_4 \to x_4 \oplus x_0 \oplus x_1 \oplus x_3$.
        *   Since $x_4$ was the phase exponent, the phase becomes $(-1)^{x_4 \oplus x_0 \oplus x_1 \oplus x_3}$.
        *   But we are summing over all $x_4$, so substituting $x_4' = x_4 \oplus x_0 \oplus x_1 \oplus x_3$, the state becomes:
            $\sum_{x_0,x_1,x_2,x_3} \sum_{x_4'} (-1)^{x_4' \oplus x_0 \oplus x_1 \oplus x_3} |x_0 x_1 x_2 x_3 x_4'\rangle / 4$.
        *   Wait, $(-1)^{a \oplus b} = (-1)^a (-1)^b$.
        *   So phase is $(-1)^{x_4'} (-1)^{x_0 \oplus

### Reference answer

{'predicted_probs': {'11011': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/4121

- task_id: `isqTrain/4121`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `2652`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[4];

procedure main() {

    CNOT(q[0], q[3]);
    CNOT(q[3], q[0]);
    CNOT(q[0], q[3]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[1]);
    CNOT(q[1], q[2]);
    H(q[3]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[3], q[2]);
    H(q[2]);
    ctrl Rz(-2.0 * 3.14159265358979 / 8.0, q[3], q[1]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[1]);
    ctrl Rz(-2.0 * 3.14159265358979 / 16.0, q[3], q[0]);
    ctrl Rz(-2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    H(q[0]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Circuit**:
    *   There are 4 qubits: `q[0], q[1], q[2], q[3]`. Initial state: $|0000\rangle$.
    *   Let's trace the gates:
        *   `CNOT(q[0], q[3])`: q[3] gets 0. State: $|0000\rangle$.
        *   `CNOT(q[3], q[0])`: q[0] gets 0. State: $|0000\rangle$.
        *   `CNOT(q[0], q[3])`: q[3] gets 0. State: $|0000\rangle$. (Wait, this sequence is just identity because q[0] and q[3] are both 0).
        *   `CNOT(q[1], q[2])`: q[2] gets 0. State: $|0000\rangle$.
        *   `CNOT(q[2], q[1])`: q[1] gets 0. State: $|0000\rangle$.
        *   `CNOT(q[1], q[2])`: q[2] gets 0. State: $|0000\rangle$.
    *   So up to here, the state is unchanged: $|0000\rangle$.
    *   The rest of the circuit is exactly the inverse Quantum Fourier Transform (QFT†) applied *in reverse order of qubits* or something similar? Let's check.
    *   Wait, the typical QFT circuit (up to swaps):
        *   H on qubit
        *   CRz on next...
    *   Let's look at the rest:
        *   `H(q[3])`
        *   `ctrl Rz(-2*pi/4, q[3], q[2])` -> This is CRz(-pi/2), which is a controlled-S† gate if applied on the target? No, CRz is diagonal.
        *   `H(q[2])`
        *   `ctrl Rz(-2*pi/8, q[3], q[1])` -> CRz(-pi/4) (controlled-T†)
        *   `ctrl Rz(-2*pi/4, q[2], q[1])` -> CRz(-pi/2)
        *   `H(q[1])`
        *   `ctrl Rz(-2*pi/16, q[3], q[0])` -> CRz(-pi/8)
        *   `ctrl Rz(-2*pi/8, q[2], q[0])` -> CRz(-pi/4)
        *   `ctrl Rz(-2*pi/4, q[1], q[0])` -> CRz(-pi/2)
        *   `H(q[0])`
    *   This is precisely an inverse QFT applied to the state $|0000\rangle$.
    *   Wait, what does inverse QFT do to $|0000\rangle$?
    *   QFT is its own inverse on the zero state? No. QFT of $|0000\rangle$ is a uniform superposition over all states. So inverse QFT of $|0000\rangle$ is also a uniform superposition!
    *   Let's verify: QFT maps $|0\rangle^{\otimes n}$ to $\frac{1}{\sqrt{N}} \sum_{x=0}^{N-1} |x\rangle$.
    *   Since $QFT^{\dagger}$ is just the inverse of QFT, and QFT is symmetric (unitary), applying $QFT^{\dagger}$ to $|0\rangle^{\otimes n}$ also gives $\frac{1}{\sqrt{N}} \sum_{x=0}^{N-1} |x\rangle$.
    *   Let's double check the target/control order in QFT.
        *   Standard QFT: H on q[0], then CRz from q[0] to q[1], etc.
        *   This circuit: H on q[3], then CRz from q[3] to q[2], q[1], q[0].
        *   Then H on q[2], CRz from q[2] to q[1], q[0].
        *   Then H on q[1], CRz from q[1] to q[0].
        *   Then H on q[0].
    *   This is an inverse QFT but the qubit indices are reversed (q[3] is highest bit or lowest bit?).
    *   Regardless, for the $|0000

### Reference answer

Uniform distribution across 16 states

## isqQA/quantum_algorithms/114_application_scenario

- task_id: `isqQA/quantum_algorithms/114_application_scenario`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `application_scenario`, `algorithm`, `HHL算法原理`
- source: `qa_pipeline`
- dataset_index: `3680`

### Prompt

HHL算法作为求解线性方程组 $Ax=b$ 的核心量子算法，常被视作许多量子机器学习和量子微分方程求解算法的底层子程序。然而，由于量子态坍缩特性和量子数据加载的困难，直接提取经典解向量 $x$ 的所有分量不仅会抵消掉量子算法带来的指数级加速，甚至在物理上是不现实的。请深入分析HHL算法在具体应用场景（例如量子支持向量机QSVM或求解泊松方程）中是如何避免直接读取完整解向量，而是通过计算解的某个物理期望值（如 $x^T M x$）来实现其应用价值的？并结合isQ语言给出一个利用HHL输出态计算期望值的量子线路示意代码。

### Reference answer

HHL算法的实际应用价值并不在于输出一个经典的稠密向量，而在于将求解出的量子态 $|x\rangle$ 作为其他量子算法的输入子程序。如果为了获取解向量 $x$ 的每个元素而去反复测量HHL的输出态，其采样复杂度将高达 $O(N)$，这会彻底抹杀HHL算法 $O(\log N)$ 的指数级查询加速优势。因此，HHL算法在实际应用中，通常利用输出态 $|x\rangle$ 直接计算某个全局物理量或期望值，例如二次型 $\langle x | M | x \rangle = x^T M x$。

以量子支持向量机（QSVM）为例，其核心问题之一是求解核矩阵 $K$ 的逆矩阵以获得权重向量 $\alpha$，这等价于求解线性方程组 $K\alpha = y$。HHL算法被用于制备量子态 $|\alpha\rangle$。在实际分类任务中，我们并不需要知道 $\alpha$ 的具体数值，而是需要计算新数据点的分类超平面距离，这在数学上等价于计算内积 $\alpha^T y_{new}$。通过将HHL的输出态 $|\alpha\rangle$ 与新数据态 $|y_{new}\rangle$ 进行Swap Test或利用Hadamard Test，就可以高效地提取出分类结果。此时，HHL完美地隐藏在了算法底层，实现了指数级加速。

在求解偏微分方程（如泊松方程 $-\nabla^2 u = f$）的场景中，离散化后得到 $Au = f$。HHL算法可以高效制备场态 $|u\rangle$。在电磁学或流体力学模拟中，工程师通常不关心每一个网格点的具体数值，而是关心系统的总能量、总电荷量或某条边界上的通量。这些宏观物理量可以被表示为 $\langle u | M | u \rangle$，其中 $M$ 是对应物理意义的厄米算符。通过在HHL算法后级联一个Hadamard测试，只需 $O(1)$ 次测量即可获得该期望值的高精度估计。

以下是使用isQ语言编写的概念性框架代码，展示了在HHL子程序之后，如何利用Hadamard Test测量可观测量 $M$ 在态 $|x\rangle$ 上的期望值：

```isq
import std;

// 声明所需的量子比特
// anc[0] 用于 Hadamard Test，reg 用于存储 |b> 并在 HHL 后演化为 |x>
qbit anc[1];
qbit reg[2];

// 假设 HHL 算子已经被打包为一个自定义的酉算子
// 实际物理场景中 A 为泊松方程的离散矩阵
// 这里仅作语法演示
deriving gate HHL = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]];

// 定义需要测量的物理量对应的算符，例如全局能量算符 M
// 这里用一个简单的 Z \otimes I 作为示例
deriving gate M_operator = [[1,0,0,0],[0,1,0,0],[0,0,-1,0],[0,0,0,-1]];

procedure main() {
    // 1. 数据加载：将经典向量 b 编码到量子态
    // 此处省略具体的态准备线路，假设通过旋转门将 reg 制备为 |b>
    Rx(1.0, reg[0]);
    Ry(0.5, reg[1]);

    // 2. 运行 HHL 算法子程序
    // 执行后，reg 寄存器的状态正比于线性方程组 A^{-1}b 的解 |x>
    HHL(reg);

    // 3. 计算 <x|M|x>：应用 Hadamard Test 提取期望值
    // 将辅助比特置于叠加态
    H(anc[0]);

    // 受控应用可观测量算符 M
    // 如果 M 不是酉算符，通常需要对 M 进行线性组合酉算子分解
    ctrl @[anc[0]] M_operator(reg);

    // 再次对辅助比特进行 Hadamard 变换
    H(anc[0]);

    // 4. 测量辅助比特获取期望值
    // 辅助比特测量结果为 0 的概率与 <x|M|x> 的实部直接相关
    int r = M(anc[0]);

    // 在实际应用中不需要 if 判断，而是通过多次 Shots 统计 r=0 的概率
    // 这里仅作语法展示
    if (r == 0) {
        // 代表投影到算符本征值的正半轴
        // 可用于经典统计期望
    }
}
```

综上所述，HHL算法的实际应用前景高度依赖于下游任务的性质：只要最终目标是提取全局统计量（如内积、期望、总的场能量），而非精确读取全量微观个体数据，HHL就能展现出其底层的指数级加速能力。这使得它在量子计算流体力学、量子化学、量子金融等领域具有广阔的应用前景。

## isqTrain/2059

- task_id: `isqTrain/2059`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4109`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
oracle bool[1] f(bool x[2]) {
    bool res[] = [true];
    return res;
}
qbit q[2];
qbit anc[1];
procedure main() {
    X(anc[0]);
    H(anc[0]);
    H(q[0]); H(q[1]);
    f(q, anc);
    H(q[0]); H(q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict the probability distribution of measurement outcomes for the given isQ program.
    *   Output format: "## Circuit Analysis" section, step-by-step reasoning, concise (3-8 lines for simple, up to 15 for complex), ending with the predicted probability distribution.
    *   No isQ code blocks.
    *   Given isQ code implements Deutsch-Jozsa algorithm for a constant function $f(x) = 1$.

2.  **Analyze the isQ code:**
    *   Initialization: `q[2]` (query register) in `|00>`, `anc[1]` (ancilla) in `|0>`. Total state: `|000>` (format: `q[0]q[1]anc[0]`).
    *   `X(anc[0])`: State becomes `|001>`.
    *   `H(anc[0])`: State becomes `|00>|->`.
    *   `H(q[0]); H(q[1])`: Query register becomes `|+>|+>` = `1/2 (|00> + |01> + |10> + |11>)`. Total state: `1/2 (|00> + |01> + |10> + |11>) |->`.
    *   `f(q, anc)`: This is an oracle evaluating to `true` (1) for all inputs.
        *   The standard Deutsch-Jozsan oracle phase kickback applies $Z$ to ancilla if $f(x) = 1$, or rather, applies a phase of $(-1)^{f(x)}$ to the query register states.
        *   Since $f(x) = 1$ for all $x$, every basis state gets a phase of $-1$.
        *   State becomes `-1/2 (|00> + |01> + |10> + |11>) |->`.
        *   Alternatively, the state is $|-\rangle$ for ancilla, which just gets a global phase. Effectively, the state of `q` is $-\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
    *   `H(q[0]); H(q[1])`: Apply Hadamard to the query register again.
        *   $H^{\otimes 2} (-\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)) = -|00\rangle$.
    *   `M(q[0]); M(q[1])`: Measure the query register.
        *   The state is `-|00>`.
        *   Probability of `00` is 100%.

3.  **Draft the Step-by-Step Reasoning:**
    *   Initial state: $|00\rangle_q |0\rangle_a$.
    *   After `X(anc[0])` and `H(anc[0])`, $H(q[0])$, $H(q[1])`: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)_q |-\rangle_a$.
    *   The oracle `f(q, anc)` evaluates to true for all inputs, applying a global phase of $-1$. The state is $-\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)_q |-\rangle_a$.
    *   The final Hadamard gates on the query register invert the superposition: $H^{\otimes 2} (-\frac{1}{2}\sum_x |x\rangle) = -|00\rangle_q$.
    *   Measurement outcome probabilities: {'00': 1.0}.

4.  **Refine to be concise and match constraints:**
    *   Needs to be 3-8 lines.
    *   Check formatting: start with `## Circuit Analysis`.

5.  **Finalizing Output:**
    *   "## Circuit Analysis"
    *   "1. Initial state is |000>. After X(anc) and H gates on all qubits, the state is 1/2(|00>+|01>+|10>+|11>)|->."
    *   "2. The oracle f(x)=1 applies a phase of (-1) for all inputs, changing the state to -1/2(|00>+|01>+|10>+|11>)|->."
    *   "3. Applying H gates to the query register yields the final state -|00>|->."
    *   "4. Measurement of the query qubits will deterministically yield '

### Reference answer

{'predicted_probs': {'00': 1.0}, 'explanation': 'Deutsch-Jozsa for constant f(x)=1: P(|00>)=1.0.'}

## isqTrain/4196

- task_id: `isqTrain/4196`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2759`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[4];

procedure main() {
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.500, q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[2]);
    Rz(2.0 * 0.500, q[2]);
    CNOT(q[0], q[2]);
    CNOT(q[0], q[3]);
    Rz(2.0 * 0.500, q[3]);
    CNOT(q[0], q[3]);
    CNOT(q[1], q[2]);
    Rz(2.0 * 0.500, q[2]);
    CNOT(q[1], q[2]);
    CNOT(q[1], q[3]);
    Rz(2.0 * 0.500, q[3]);
    CNOT(q[1], q[3]);
    CNOT(q[2], q[3]);
    Rz(2.0 * 0.500, q[3]);
    CNOT(q[2], q[3]);
    Rx(2.0 * 0.500, q[0]);
    Rx(2.0 * 0.500, q[1]);
    Rx(2.0 * 0.500, q[2]);
    Rx(2.0 * 0.500, q[3]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

This is a QAOA circuit with 4 qubits.

Let me analyze the circuit step by step.

**Initial state:** |0000⟩

**After H gates on all qubits:** Uniform superposition (1/4)|ψ⟩ where |ψ⟩ = Σ_{x∈{0,1}^4} |x⟩

So the state is (1/4)(|0000⟩ + |0001⟩ + ... + |1111⟩)

**The CNOT-Rz(π/2)-CNOT pattern:**
Looking at Rz(2.0 * 0.500) = Rz(1.0) = Rz(π/2 · (2/π))... wait, let me reconsider.

Actually, in isQ, Rz(theta) uses the matrix diag(e^{-iθ/2}, e^{iθ/2}). So Rz(2.0 * 0.500) = Rz(1.0).

Wait, let me think about what Rz(1.0) means. In many quantum computing frameworks, Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2}).

So Rz(1.0) = diag(e^{-i/2}, e^{i/2}).

The CNOT-Rz-CNOT pattern on qubits (i,j) implements ZZ interaction. Specifically:
CNOT(i,j) Rz(θ,j) CNOT(i,j) applies a phase that depends on the parity of qubits i and j.

More precisely: CNOT(i,j) Rz(θ,j) CNOT(i,j) = diag(1, 1, 1, e^{iθ}) in the {00, 01, 10, 11} basis of (i,j).

Wait, let me be more careful. CNOT with control i and target j:
- If qubit i is |0⟩, qubit j unchanged
- If qubit i is |1⟩, qubit j flipped

So after first CNOT(i,j), the target j has value j⊕i.
Then Rz(θ) on j applies phase e^{iθ/2} to |0⟩_j and e^{-iθ/2} to |1⟩_j (in the original notation, diag(e^{-iθ/2}, e^{iθ/2})).

After the second CNOT, the net effect on the two-qubit subspace is:
- |00⟩: CNOT→|00⟩, Rz→e^{-iθ/2}|00⟩, CNOT→e^{-iθ/2}|00⟩
- |01⟩: CNOT→|01⟩, Rz→e^{iθ/2}|01⟩, CNOT→e^{iθ/2}|01⟩
- |10⟩: CNOT→|11⟩, Rz→e^{iθ/2}|11⟩, CNOT→e^{iθ/2}|10⟩
- |11⟩: CNOT→|10⟩, Rz→e^{-iθ/2}|10⟩, CNOT→e^{-iθ/2}|11⟩

So the phase applied is:
- |00⟩: e^{-iθ/2}
- |01⟩: e^{iθ/2}
- |10⟩: e^{iθ/2}
- |11⟩: e^{-iθ/2}

This is e^{-iθ/2} · diag(1, e^{iθ}, e^{iθ}, 1) = e^{-iθ/2} · (phase = e^{iθ} when exactly one of the two qubits is |1⟩)

Hmm, actually this is the same as applying e^{-iθ/2} · exp(iθ(|i⟩⟨i| + |j⟩⟨j| - 2|i⟩⟨i|·|j⟩⟨j|))... 

Actually, let me think of it differently. The phase depends on the XOR of the two bits:
- When XOR = 0 (same parity): phase e^{-iθ/2}
- When XOR = 1 (different parity): phase e^{iθ/2}

So it's exp(-iθ/2 · (-1)^{x_i ⊕ x_j}) up to global phase, or equivalently it's a ZZ rotation.

The effect on a computational basis state |x₁x₂x₃x₄⟩ is:
phase = product over all pairs (i,j) with i<j of exp(-iθ/2 · (-1)^{x_i ⊕ x_j})

Wait, let me just think about this more directly.

With θ = 1.0, each CNOT-Rz(1.0)-CNOT block on pair (i,j) applies:
- Phase e

### Reference answer

Uniform distribution across 8 states

## isqTrain/4064

- task_id: `isqTrain/4064`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `2418`

### Prompt

这段isQ代码有bug，帮我找出并修复：

```
import std;
// QAOA MaxCut p=1 on 3-node path graph
// gamma=1.000, beta=0.500
qbit q[3];

procedure main() {
    // Initial superposition
    H(q[0]); H(q[1]); H(q[2]);
    // Cost unitary U_C(gamma)
    // Edge (0,1): exp(-i*gamma*Z_i*Z_j)
    CNOT(q[0], q[1]);
    Rz(2.0 * 2.0 * 1.000, q[1]);
    CNOT(q[0], q[1]);
    // Edge (1,2): exp(-i*gamma*Z_i*Z_j)
    CNOT(q[1], q[2]);
    Rz(2.0 * 1.000, q[2]);
    CNOT(q[1], q[2]);
    // Mixer unitary U_M(beta)
    Rx(2.0 * 0.500, q[0]);
    Rx(2.0 * 0.500, q[1]);
    Rx(2.0 * 0.500, q[2]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

## Bug Analysis

**Bug:** In the cost unitary for edge (0,1), the Rz gate has parameter `2.0 * 2.0 * 1.000` instead of `2.0 * 1.000`. This doubles the intended rotation angle.

**Fix:** Change `Rz(2.0 * 2.0 * 1.000, q[1])` to `Rz(2.0 * 1.000, q[1])`. The CNOT-Rz(2γ)-CNOT decomposition implements exp(-iγ Z⊗Z), so the angle should be exactly `2*gamma = 2.0`.

**State evolution (corrected):**
1. **H⊗3:** |000⟩ → |+++⟩ = equal superposition over all 8 basis states
2. **Edge (0,1) cost:** Rz(2.0) between q[0],q[1] applies phase exp(∓i) for |±⟩ correlations → entangles q[0],q[1]
3. **Edge (1,2) cost:** Rz(2.0) between q[1],q[2] similarly phases by γ=1.0
4. **Mixer Rx(π) on all qubits:** Each qubit rotated by 2β=1.0 rad about X, mixing computational basis states
5. **Measurement:** Yields expected distribution peaked at |000⟩ (0.259) and |111⟩ (0.259), with |010⟩ and |101⟩ at ~0.138, and antiferromagnetic-cut states suppressed to ~0.052

## isqTrain/2704

- task_id: `isqTrain/2704`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1671`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[3];

procedure main(){
    H(q[0]);
    X2P(q[1]);
    CZ(q[0], q[2]);
    Y2M(q[0]);
    CZ(q[2], q[1]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a step-by-step quantum circuit analysis for an isQ program. The analysis should explain the operations, state evolution, final state, and predicted probability distribution using Dirac notation. The output must start with "## Circuit Analysis".

2.  **Analyze the isQ Circuit:**
    *   `qbit q[3];` -> Initial state is $|000\rangle$ (using $q_0 q_1 q_2$ order, but let's be careful about indexing. Usually $q[0]$ is the first qubit, $q[1]$ is second, $q[2]$ is third. Let's write the state as $|q_0 q_1 q_2\rangle$). Let's stick to $|q_0, q_1, q_2\rangle$.
    *   `H(q[0]);` -> Apply Hadamard to $q_0$. State becomes $\frac{1}{\sqrt{2}}(|000\rangle + |100\rangle)$.
    *   `X2P(q[1]);` -> Apply $R_x(\pi/2)$ to $q_1$.
        *   $X2P |0\rangle = \frac{1}{\sqrt{2}}(|0\rangle - i|1\rangle)$.
        *   State becomes $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)_{q_0} \otimes \frac{1}{\sqrt{2}}(|0\rangle - i|1\rangle)_{q_1} \otimes |0\rangle_{q_2}$.
        *   $= \frac{1}{2}(|000\rangle - i|010\rangle + |100\rangle - i|110\rangle)$.
    *   `CZ(q[0], q[2]);` -> Apply CZ with control $q_0$, target $q_2$.
        *   This flips the phase of $|1\rangle$ in $q_2$ when $q_0$ is 1. Since $q_2$ is $|0\rangle$, nothing happens!
        *   State remains $\frac{1}{2}(|000\rangle - i|010\rangle + |100\rangle - i|110\rangle)$.
    *   `Y2M(q[0]);` -> Apply $R_y(-\pi/2)$ to $q_0$.
        *   $Y2M |0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$. Wait, $R_y(\theta) = \begin{pmatrix} \cos(\theta/2) & -\sin(\theta/2) \\ \sin(\theta/2) & \cos(\theta/2) \end{pmatrix}$.
        *   $R_y(-\pi/2) |0\rangle = \cos(-\pi/4)|0\rangle + \sin(-\pi/4)|1\rangle = \frac{1}{\sqrt{2}}|0\rangle - \frac{1}{\sqrt{2}}|1\rangle = |-\rangle$.
        *   Wait, is $Y2M$ $R_y(-\pi/2)$ or $R_y(\pi/2)$? The prompt says: `Y2P (Ry(pi/2)), Y2M (Ry(-pi/2))`.
        *   Let's recalculate $Y2M |0\rangle$: $R_y(-\pi/2)|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = |-\rangle$.
        *   Let's recalculate $Y2M |1\rangle$: $R_y(-\pi/2)|1\rangle = -\sin(-\pi/4)|0\rangle + \cos(-\pi/4)|1\rangle = \frac{1}{\sqrt{2}}|0\rangle + \frac{1}{\sqrt{2}}|1\rangle = |+\rangle$.
        *   So $Y2M$ acts on $q_0$:
        *   $q_0$ part is $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
        *   $Y2M \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = \frac{1}{\sqrt{2}}(|-\rangle + |+\rangle) = \frac{1}{\sqrt{2}} ( \frac{1}{\sqrt{2}}(|0\rangle

### Reference answer

{'predicted_probs': {'000': 0.5000000000000002, '010': 0.4999999999999999}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

# ISQ training COT RAG corpus: quantum_algorithms shard 38

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3945

- task_id: `isqTrain/3945`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4727`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```
import std;
// Bernstein-Vazirani: find secret s = 1011
oracle f(4, 1) = [0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1];
qbit q[5];

procedure main() {
    // Output in |->
    Y(q[4]);
    H(q[4]);
    // Hadamard on inputs
    for i in 0:4 {
        H(q[i]);
    }
    // Oracle
    f(q[0], q[1], q[2], q[3], q[4]);
    // Hadamard
    for i in 0:4 {
        H(q[i]);
    }
    // Measure
    M(q[0]); M(q[1]); M(q[2]); M(q[3]); M(q[4]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: Line `Y(q[4])` uses the wrong gate to initialize the output qubit. The Y gate maps |0⟩ → i|1⟩, introducing an unwanted phase factor. The Bernstein-Vazirani algorithm requires the ancilla to be in state |1⟩ (then H converts it to |−⟩). The correct initialization gate is X, which maps |0⟩ → |1⟩ without extra phase.

2. **Fix**: Replace `Y(q[4])` with `X(q[4])`. This correctly prepares |1⟩, so that H|1⟩ = |−⟩ = (|0⟩−|1⟩)/√2, enabling the phase kickback mechanism.

3. **State evolution (corrected circuit)**:
   - Initial: |00000⟩
   - X(q[4]): |00001⟩
   - H(q[4]) → |−⟩; H(q[0:3]): (|0⟩+|1⟩)⁴/4 ⊗ |−⟩ = Σ_x |x⟩/4 ⊗ |−⟩
   - Oracle f: phase kickback encodes s=1011 → (−1)^(x·s) factors: Σ_x (−1)^(x·s)|x⟩/4 ⊗ |−⟩
   - H(q[0:3]): collapses to |s⟩ = |1011⟩ on inputs, ancilla remains in |−⟩
   - Measurement: |1011⟩ on q[0-3], |−⟩ on q[4] → equal probability of |10110⟩ and |10111⟩ ✓

## isqTrain/3439

- task_id: `isqTrain/3439`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `1586`

### Prompt

用isQ实现QPE in isQ for the S gate (phase gate, pi/2) using 2 precision qubits.

S|1> = i|1>, phase = pi/2, theta = 1/4.
Binary: 0.01 with 2 bits -> |01>.

Controlled operations:
- prec[0] controls S^2 = Z
- prec[1] controls S^1 = S

Declare prec[2] and tgt[1]. Measure prec only.

### Chain-of-thought reasoning

Let me analyze this QPE (Quantum Phase Estimation) circuit for the S gate.

The S gate has the property: S|1⟩ = i|1⟩, so the phase is e^(iπ/2) = i, which means θ = 1/4 (since phase = 2πθ, θ = π/(2·2π) = 1/4).

In binary with 2 precision qubits: θ = 0.01₂ = 1/4. So we expect to measure |01⟩.

Let me trace through the circuit:

**Initial state:** |00⟩|0⟩ (prec|tgt)

**After X(tgt[0]):** |00⟩|1⟩

**After H⊗H on prec:** (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)|1⟩

**After ctrl Z (prec[0] controls S² = Z on tgt):**
- prec[0]=1 applies Z to tgt[0]
- Z|1⟩ = -|1⟩
- So: (1/2)(|00⟩|1⟩ - |01⟩|1⟩ + |10⟩|1⟩ - |11⟩|1⟩) 

Wait, let me be more careful. prec[0] is the first qubit. When prec[0]=|1⟩, we apply Z to tgt.

Actually wait - I need to check the ordering. prec[0] and prec[1] are the precision qubits. Let me re-examine.

In QPE:
- prec[0] is the least significant bit (LSB), gets the least significant digit
- prec[1] is the most significant bit (MSB), gets the most significant digit

Actually, in standard QPE:
- The first Hadamard qubit (prec[0]) controls U^(2^(n-1)) where n is the number of precision qubits
- The last Hadamard qubit controls U^(2^0) = U

Wait, let me reconsider. With 2 precision qubits:
- prec[0] controls S^(2^1) = S^2 = Z
- prec[1] controls S^(2^0) = S

This is the standard convention where the first precision qubit (prec[0]) corresponds to the MSB.

So after the controlled operations:

After H⊗H: (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)|1⟩

Let me denote prec = prec[0]prec[1], so |prec[0], prec[1]⟩

After ctrl Z (prec[0] controls Z on tgt[0]):
When prec[0]=1, Z is applied to |1⟩ giving -|1⟩.
Phase from Z on |1⟩: -1 = e^(iπ)

After ctrl S (prec[1] controls S on tgt[0]):
When prec[1]=1, S is applied to |1⟩ giving i|1⟩.
Phase from S on |1⟩: i = e^(iπ/2)

Combined phase for |ab⟩: (-1)^a · i^b

State: (1/2)(|00⟩ + i|01⟩ - |10⟩ - i|11⟩)|1⟩

Now applying inverse QFT on prec register.

QFT on 2 qubits maps |x⟩ → (1/2) Σ_y e^(2πixy/4) |y⟩

Inverse QFT maps |y⟩ → (1/2) Σ_x e^(-2πixy/4) |x⟩

But I should trace through the actual gates given in the code.

Actually, let me look at the code more carefully:

Hmm, this looks a bit unusual for inverse QFT. Let me think about what the standard inverse QFT on 2 qubits should be.

Standard QFT on 2 qubits (q0 = MSB, q1 = LSB):
1. H(q1)
2. ctrl Rz(π/2, q0, q1) [q0 controls Rz on q1]
3. H(q0)
4. swap(q0, q1) via three CNOTs

Inverse QFT:
1. swap(q0, q1) via three CNOTs
2. H(q0)
3. ctrl Rz(-π/2, q0, q1) [q0 controls Rz on q1]
4. H(q1)

In the code:

## isqQA/quantum_algorithms/39_math_derivation

- task_id: `isqQA/quantum_algorithms/39_math_derivation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `math_derivation`, `algorithm`, `Bernstein-Vazirani算法`
- source: `qa_pipeline`
- dataset_index: `4465`

### Prompt

请严密推导Bernstein-Vazirani算法的核心数学过程。假设有一个隐藏比特串s，预言机实现函数f(x)=s·x (mod 2)，请给出从初态到最终测量前，量子态在Hadamard变换下的每一步演化过程，并说明为什么只需一次查询就能确定s。

### Reference answer

<think>
Bernstein-Vazirani算法的推导核心在于量子态的叠加、相位编码与干涉效应。首先，利用Hadamard门将系统转化为前n比特的均匀叠加态与辅助比特的|−⟩态。接着，将状态输入预言机。由于辅助比特处于|−⟩态，会触发相位反冲效应，将隐藏比特串s的信息从函数值转化为前n比特的相位因子，状态演化为包含(−1)^(s·x)的相位叠加态。推导的关键在于对前n比特再次施加Hadamard门。根据Hadamard变换的线性性质，这等同于对叠加态进行逆向映射。在展开求和时，基于二进制内积的正交性，非目标态的相位会相互抵消（干涉相消），而与目标比特串s对应的项会叠加增强（干涉相长）。最终，前n个量子比特的叠加态精确坍缩为本征态|s⟩，从而在数学上证明了只需单次预言机查询和测量即可确定s。
</think>

Bernstein-Vazirani算法旨在从黑盒预言机U_f中提取未知比特串s∈{0,1}^n。预言机计算f(x) = s·x (mod 2)，其中s·x表示二进制向量的内积。算法仅需一次预言机查询即可确定s，以下是严格的数学推导。设n+1个量子比特的初态为|ψ_0⟩ = |0⟩^{⊗n}|1⟩。第一步，对所有量子比特施加Hadamard门。利用H|0⟩ = (|0⟩+|1⟩)/√2和H|1⟩ = (|0⟩-|1⟩)/√2，系统状态演化为：|ψ_1⟩ = H^{⊗n}|0⟩^{⊗n} ⊗ H|1⟩ = (1/√(2^n)) Σ_{x∈{0,1}^n} |x⟩ ⊗ (|0⟩-|1⟩)/√2。第二步，将量子态通过预言机U_f，其作用定义为U_f|x⟩|y⟩ = |x⟩|y⊕f(x)⟩。由于辅助比特处于(|0⟩-|1⟩)/√2状态，它会引发相位反冲效应：U_f|x⟩(|0⟩-|1⟩)/√2 = (-1)^{f(x)}|x⟩(|0⟩-|1⟩)/√2 = (-1)^{s·x}|x⟩(|0⟩-|1⟩)/√2。演化后的状态为|ψ_2⟩ = (1/√(2^n)) Σ_{x∈{0,1}^n} (-1)^{s·x}|x⟩ ⊗ (|0⟩-|1⟩)/√2。此时，隐藏比特串s的信息已经被编码到了前n个量子比特的相对相位中。第三步，对前n个工作比特再次施加H^{⊗n}门。这里需要利用一个关键的数学恒等式：对于任意n比特向量z，H^{⊗n}|z⟩ = (1/√(2^n)) Σ_{x∈{0,1}^n} (-1)^{z·x}|x⟩。同样地，可以将计算基态的逆变换表示为|x⟩ = (1/√(2^n)) Σ_{z∈{0,1}^n} (-1)^{x·z}|z⟩。将此代入|ψ_2⟩中前n个比特的表达式，得到H^{⊗n} [(1/√(2^n)) Σ_x (-1)^{s·x}|x⟩] = (1/2^n) Σ_x Σ_z (-1)^{s·x}(-1)^{x·z}|z⟩。我们交换求和符号并提取出关于z的态矢量系数：(1/2^n) Σ_z [Σ_x (-1)^{(s⊕z)·x}] |z⟩。这里的关键在于内部对x的求和。由于x遍历所有n位二进制数，指数(s⊕z)·x中的s⊕z是一个固定的n位向量。如果s⊕z = 0（即z=s），那么(-1)^{0·x} = 1对所有x恒成立，内部求和结果为2^n。如果s⊕z ≠ 0，那么(s⊕z)·x在x取不同值时必然有一半概率为0，一半概率为1，正负项相互抵消，内部求和结果为0。因此，整个叠加态发生了完美的相长干涉和相消干涉，最终状态坍缩为|ψ_3⟩ = |s⟩ ⊗ (|0⟩-|1⟩)/√2。最后，对前n个量子比特在计算基下进行测量，得到经典比特串s的概率为P(s) = |⟨s|s⟩|² = 1。综上所述，Bernstein-Vazirani算法利用了量子叠加态让预言机同时处理所有可能的输入x，并通过Hadamard门的傅里叶变换性质将相位信息转化为振幅信息，实现了干涉放大。这使得算法仅需1次预言机调用就能百分之百地提取出隐藏串s，达到了相比经典算法需要n次查询的指数级加速。

## isqTrain/2966

- task_id: `isqTrain/2966`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3795`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```isq
import std;
qbit q[3];
// 2-layer H+CNOT circuit on 3 qubits
procedure main() {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[0]);
    H(q[0]);
    H(q[1]);
    // H(q[2]); // BUG: missing Hadamard
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[0]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **The bug** is a missing Hadamard gate on `q[2]` in the second layer of operations. It was commented out as `// H(q[2]);`, which breaks the parallel superposition structure required before the second ring of CNOTs.
2. **The fix** is to restore `H(q[2]);` alongside `H(q[0]);` and `H(q[1]);` to complete the full 3-qubit superposition.
3. **State evolution** (corrected): Starting at |000>, the first `H`⊗3 creates the state |+++>. The first CNOT ring entangles the qubits. Applying the second `H`⊗3 correctly maps this to an intermediate state, and the second CNOT ring precisely uncomputes the operations. The final state returns exactly to |000>, yielding a 100% measurement probability for |000>.

## isqQA/quantum_algorithms/90_math_derivation

- task_id: `isqQA/quantum_algorithms/90_math_derivation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `math_derivation`, `algorithm`, `Bernstein-Vazirani算法原理`
- source: `qa_pipeline`
- dataset_index: `4447`

### Prompt

请详细推导Bernstein-Vazirani算法中量子态的完整演化过程，并说明为何仅需要单次查询即可提取出隐藏字符串。进一步地，请使用isQ语言编写代码，实现一个寻找4位隐藏字符串 s=1011 的Bernstein-Vazirani算法完整量子线路。

### Reference answer

<think>
首先，推导算法演化需从初始态开始，将所有输入量子比特置于均匀叠加态，并将辅助比特置于 $|-\rangle$ 态以利用量子相位kickback（反冲）效应。

其次，在推导预言机 $U_f$ 作用时，由于 $f(x) = s \cdot x \pmod 2$，计算结果会以相位形式 $(-1)^{f(x)}$ 附加在输入态上，使得叠加态的每一个分量 $|x\rangle$ 获得 $(-1)^{s \cdot x}$ 的相位。这一步是算法仅需单次查询的关键：量子并行性使得单次调用就能将隐藏字符串 $s$ 的信息编码进整个量子态的相对相位中。

接着，再次对输入比特施加Hadamard门。根据Hadamard变换的性质，这步干涉会将之前的相位差转化为计算基上的幅值差异，精确映射出目标态 $|s\rangle$。

最后，在构建isQ代码时，只需将上述数学结构转化为线路逻辑：初始化量子比特，施加H层，根据 $s=1011$ 的非零位在对应控制位与辅助比特间添加CNOT门（或受控Z门）以实现内积黑箱，再施加H层，最后测量输入寄存器即可直接得到 $s$。
</think>

Bernstein-Vazirani算法的核心目标是寻找一个隐藏的比特串 $s \in \{0,1\}^n$，使得黑箱函数 $f(x) = s \cdot x \pmod 2$。经典计算需要 $n$ 次查询，而量子算法仅需1次。下面是严密的数学推导过程。

假设我们使用 $n$ 个输入量子比特和 1 个辅助量子比特。系统初始状态设定为：
$|\psi_0\rangle = |0\rangle^{\otimes n}|1\rangle$

第一步，对所有的量子比特施加Hadamard门。由于 $H^{\otimes n}|0\rangle^{\otimes n} = \frac{1}{\sqrt{2^n}}\sum_{x=0}^{2^n-1}|x\rangle$，且 $H|1\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$，此时系统的量子态演化为：
$|\psi_1\rangle = \left( \frac{1}{\sqrt{2^n}}\sum_{x}|x\rangle \right) \otimes \left( \frac{|0\rangle - |1\rangle}{\sqrt{2}} \right)$

第二步，执行Oracle查询 $U_f$。其作用机制为 $U_f|x\rangle|y\rangle = |x\rangle|y \oplus f(x)\rangle$。将 $U_f$ 作用于 $|\psi_1\rangle$ 上，由于辅助比特处于叠加态，会发生相位反转效应（Phase Kickback）：
$U_f|x\rangle \frac{|0\rangle - |1\rangle}{\sqrt{2}} = |x\rangle \frac{|0 \oplus f(x)\rangle - |1 \oplus f(x)\rangle}{\sqrt{2}} = (-1)^{f(x)}|x\rangle \frac{|0\rangle - |1\rangle}{\sqrt{2}}$
代入函数关系 $f(x) = s \cdot x$，忽略不受影响的辅助比特，系统的前 $n$ 个量子比特演化为：
$|\psi_2\rangle = \frac{1}{\sqrt{2^n}}\sum_{x} (-1)^{s \cdot x}|x\rangle$

第三步，对前 $n$ 个量子比特再次施加Hadamard门。已知 $H^{\otimes n}$ 对态 $|x\rangle$ 的作用可表示为 $H^{\otimes n}|x\rangle = \frac{1}{\sqrt{2^n}}\sum_{z}(-1)^{x \cdot z}|z\rangle$。因此作用在 $|\psi_2\rangle$ 上：
$|\psi_3\rangle = H^{\otimes n} \left( \frac{1}{\sqrt{2^n}}\sum_{x} (-1)^{s \cdot x}|x\rangle \right) = \frac{1}{2^n}\sum_{x}\sum_{z}(-1)^{s \cdot x}(-1)^{x \cdot z}|z\rangle = \frac{1}{2^n}\sum_{z} \left( \sum_{x}(-1)^{x \cdot (s \oplus z)} \right) |z\rangle$
根据正交性，内层求和 $\sum_{x}(-1)^{x \cdot y}$ 在 $y=0$ 时等于 $2^n$，在 $y \neq 0$ 时为 $0$。因此，只有当 $z = s$ 时，叠加项非零。最终态坍缩为：
$|\psi_3\rangle = |s\rangle$

经过严密的数学推导可见，只需要对最后的量子态进行测量，就能以概率1直接得到隐藏字符串 $s$，无需像经典算法那样进行多次线性方程组求解。

以下是使用isQ语言实现寻找 $s=1011$ 的BV算法代码。1011对应于量子比特索引的0、1、3（从右向左，低位到高位），所以Oracle通过这几个位置的控制非门实现：

import std;

qbit q[5];

procedure main() {
    // 初始化辅助比特 q[4] 为 |1>
    X(q[4]);

    // 对所有量子比特施加Hadamard门
    for i in 0:5 {
        H(q[i]);
    }

    // 构造针对 s=1011 的Oracle
    // s0=1, s1=1, s3=1
    CNOT(q[0], q[4]);
    CNOT(q[1], q[4]);
    CNOT(q[3], q[4]);

    // 对前4个输入量子比特再次施加Hadamard门
    for i in 0:4 {
        H(q[i]);
    }

    // 测量前4个输入比特以获取隐藏字符串 s
    for i in 0:4 {
        M(q[i]);
    }
}

## isqTrain/3594

- task_id: `isqTrain/3594`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3198`

### Prompt

Fix the bug in the following isQ program.

Bug description: Missing Hadamard gate

The program should 5-qubit GHZ state preparation.

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The Hadamard gate `H(q[0])` is missing before the CNOT fan-out. Without it, the first qubit stays in |0⟩, so all CNOTs do nothing, leaving the state as |00000⟩.

2. **Fix**: Add `H(q[0]);` after the comment `// Superposition on first qubit` and before the CNOT gates. This puts q[0] into |+⟩ = (|0⟩+|1⟩)/√2.

3. **State evolution of corrected circuit**:
   - Initial: |00000⟩
   - After H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |0000⟩ = (|00000⟩+|10000⟩)/√2
   - After CNOT(q[0],q[1]): (|00000⟩+|11000⟩)/√2
   - After CNOT(q[0],q[2]): (|00000⟩+|11100⟩)/√2
   - After CNOT(q[0],q[3]): (|00000⟩+|11110⟩)/√2
   - After CNOT(q[0],q[4]): (|00000⟩+|11111⟩)/√2 — the 5-qubit GHZ state, yielding measurement probabilities {|00000⟩: 0.5, |11111⟩: 0.5}.

## isqTrain/3075

- task_id: `isqTrain/3075`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`
- source: `isq_train_cot`
- dataset_index: `4290`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[4];
procedure main() {
    X(q[1]);
    X(q[3]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the isQ program:**
    - 4 qubits: `q[0], q[1], q[2], q[3]`. Initial state is $|0000\rangle$ (using little-endian/standard order based on array indexing, though typically measurement bitstrings map `q[0]` to index 0 or highest bit depending on convention, but here `--probs` output says "earlier measured qubit = higher bit", so `q[0]` is MSB, `q[3]` is LSB. Wait, `q[0]` measured first -> higher bit.
    - `X(q[1])`: Flips `q[1]` from $|0\rangle$ to $|1\rangle$.
    - `X(q[3])`: Flips `q[3]` from $|0\rangle$ to $|1\rangle$.
    - Measurements: `M(q[0]), M(q[1]), M(q[2]), M(q[3])`.
    - No other gates.

2.  **Determine Quantum State Evolution:**
    - Initial state: $|0000\rangle$ (q3, q2, q1, q0) -> typically we write it as $|q_0 q_1 q_2 q_3\rangle = |0000\rangle$.
    - After `X(q[1])`: State becomes $|0100\rangle$ (in the order q[0], q[1], q[2], q[3]). Wait, let's carefully map bits.
    - If state is $|q_0 q_1 q_2 q_3\rangle$, `q[0]` is bit 3 (or 0 depending on endianness).
    - Let's just use the standard basis: `q[0]` is 0, `q[1]` is 1, `q[2]` is 0, `q[3]` is 1. So the state is `1010` or `0101`?
    - `q[0]` is the first bit, `q[1]` is the second, `q[2]` third, `q[3]` fourth.
    - So `q[0]=0, q[1]=1, q[2]=0, q[3]=1`.
    - Bitstring order: usually $q_0 q_1 q_2 q_3$ -> `0101`.
    - Wait, the prompt says: "Expected measurement probabilities: {'0101': 1.0}". So The predicted output indeed `0101` if `q[0]` is MSB, and `q[3]` is LSB, and $q_0=0, q_1=1, q_2=0, q_3=1$. So the bitstring is $q_0 q_1 q_2 q_3 = 0101_2$.
    - Let's double check. `X(q[1])` sets bit 1 to 1. `X(q[3])` sets bit 3 to 1.
    - Bit string from left to right: `q[0] q[1] q[2] q[3]` = 0 1 0 1.
    - Yes, "0101" matches perfectly.

3.  **Draft the response:**
    - **1. Operations:** Initialize 4 qubits to $|0000\rangle$. Apply X gate to `q[1]` and `q[3]`. Measure all 4 qubits.
    - **2. State Evolution:** $|0000\rangle \xrightarrow{X(q_1)} |0100\rangle \xrightarrow{X(q_3)} |0101\rangle$.
    - **3. Final State:** $|0101\rangle$.
    - **4. Probabilities:** The state is exactly $|0101\rangle$, so it has a 100% probability of being measured as `0101`.
    - Expected JSON: `[0.0, 0.0, ..., 1.0, ...]`. Wait, the prompt just asks for the analysis. "End with the predicted probability distribution" - which is a JSON array.

4.  **Formatting constraints:**
    - Concise, 3-8 lines.
    - Start with "## Circuit Analysis"
    - End with the predicted probability distribution. (Since it's a 4-qubit state, the JSON array has 16 elements).
    - Index of '0101' is $0 \times 8 + 1 \times 4 + 0 \times 2 + 1 \times 1 =

### Reference answer

{'predicted_probs': {'0101': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/2819

- task_id: `isqTrain/2819`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2922`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]);
    for i in 1:2 {
        CNOT(q[i-1], q[i]);
    }
    for i in 0:2 {
        M(q[i]);
    }
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a step-by-step analysis of an isQ quantum program, explaining the state evolution and the final measurement probabilities. The output must be concise (3-15 lines), start with "## Circuit Analysis", use Dirac notation, and end with the predicted probability distribution.

2.  **Analyze the isQ Code:**
    *   `qbit q[2];`: Declares a quantum register of 2 qubits, initialized to |00>. *Wait, the code says `q[2]` but then uses `q[2]`?* Ah, `q[2]` means an array of size 2 (indices 0 and 1). But wait, the loop is `for i in 1:2 { CNOT(q[i-1], q[i]); }`. In isQ, `1:2` usually means inclusive range or similar depending on exact syntax, but typically if `q` is size 2, `q[2]` would be an out-of-bounds access. Let me re-read the code. `qbit q[2];` and `q[i]` for `i in 1:2`. If `i=2`, `q[2]` is out of bounds. Wait, is it possible the prompt implies `qbit q[3]`? Let's check The implementation text: `qbit q[2];` and `for i in 1:2`. Let me re-read the loop carefully. Wait, if it's a 2-qubit register, `q[0]` and `q[1]` are valid. If `i=2`, `q[2]` is out of bounds.
    Let's look at standard isQ ranges: `for i in 1:2` might mean 1 to 2 exclusive, so just `i=1`. Wait, usually `a:b` means `[a, b)` in Python-like syntax, or `[a, b]` in MATLAB. If it's `1:2`, it might just be `i=1`. Let's assume `i=1` only.
    Let's check the measurement loop: `for i in 0:2 { M(q[i]); }`. If it's `0:2` and means `i=0, 1`, then it measures 2 qubits. If it includes 2, it measures 3 qubits, but `q[2]` is out of bounds.
    Given the "Expected measurement probabilities: {'00': 0.5, '11': 0.5}", it strongly implies there are exactly 2 qubits measured.
    Let's re-verify the standard isQ syntax. `for i in a:b` usually iterates from `a` to `b-1`. So `for i in 1:2` iterates for `i=1`. `for i in 0:2` iterates for `i=0, 1`.
    This makes perfect sense! 1:2 means just `i=1`. 0:2 means `i=0, 1`.

3.  **Step-by-Step Execution:**
    *   **Initial State:** |00> (since 2 qubits).
    *   **H(q[0]):** Applies Hadamard to q[0]. State becomes (1/√2)|00> + (1/√2)|10> = |+0>.
    *   **CNOT(q[0], q[1]):** Control is q[0], target is q[1]. Flips q[1] when q[0] is |1>.
        State becomes (1/√2)|00> + (1/√2)|11>. This is a Bell state.
    *   **Measurement:** Measures q[0] and q[1].

4.  **Final State and Probabilities:**
    *   Final state before measurement: (1/√2)|00> + (1/√2)|11>.
    *   Probability of |00>: |1/√2|² = 0.5.
    *   Probability of |11>: |1/√2|² = 0.5.

5.  **Format the Output:**
    *   Start with "## Circuit Analysis".
    *   List operations: H on q[0], then CNOT(q[0], q[1]).
    *   State evolution: |00> -> H(q[0]) -> (1/√2)|00> + (1/√2)|10> -> CNOT -> (1/√2)|00> + (1/√2)|11>.
    *   Final state: (1/√2)|00> + (1/√2)|11>.
    *   Probabilities:

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/2984

- task_id: `isqTrain/2984`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4837`

### Prompt

Fix the bug in this quantum program:

```isq
import std;
qbit q[3];
// Controlled-H circuit: q[0] controls H on q[1]
procedure main() {
    // X(q[0]); // BUG: missing initialization
    ctrl H(q[0], q[1]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: `X(q[0])` is commented out on line 7, so q[0] remains |0> instead of being initialized to |1>. Since the controlled-H only activates when the control q[0] is |1>, the H gate is never applied to q[1], leaving the state as |000>.

2. **Fix**: Uncomment `X(q[0])` to initialize q[0] to |1>, enabling the controlled-H to activate.

3. **State evolution (corrected)**:
   - Initial: |000>
   - X(q[0]): |100>
   - ctrl H(q[0], q[1]): q[0]=|1> triggers H on q[1] → (1/√2)(|100> + |110>)
   - Measurement: P(|100>) = 0.5, P(|110>) = 0.5 ✓

## isqTrain/1137

- task_id: `isqTrain/1137`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2639`

### Prompt

用isQ实现implements a variant of the graph_state_preparation pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The user wants me to generate reasoning for a graph state preparation circuit that uses 4 qubits with an edge between q[3] and q[4].

Wait, The circuit should 3 qubits with edges (0,1) and (1,2), but the predicted output suggest 4 qubits with specific outcomes.

Let me analyze the expected measurement probabilities: {|0000>: 0.25, |0100>: 0.25, |1010>: 0.25, |1110>: 0.25}

This is a 4-qubit system. The task mentions "q[3] -> q[4]" which I interpret as an edge between q[3] and q[4], but since we have a 4-qubit register (indices 0-3), this seems like we need to extend to 5 qubits... Actually, Analyzing the, it uses q[4] as the register size.

Wait, let me re-read: "variant of the graph_state_preparation pattern using q[3] -> q[4]". This means the edge is between q[3] and q[4]. So we need at least 5 qubits.

But the predicted output show 4-qubit states. And the reference shows M(q[0]); M(q[1]); M(q[2]); M(q[3]); which measures 4 qubits.

Looking at the predicted output more carefully:
- |0000>: 0.25
- |0100>: 0.25  
- |1010>: 0.25
- |1110>: 0.25

Hmm, this is a bit odd. Let me think about what circuit would produce this.

Actually, I think the task is asking me to modify The implementation to use q[3]->q[4] as an edge, which means we need 5 qubits total (q[0] through q[4]).

But wait, the expected measurement probabilities are for 4 qubits, and the reference measures 4 qubits. Let me reconsider.

Perhaps the "expanded qubit register" means we go from 3 qubits to 4 qubits, and "q[3] -> q[4]" means we need q[4] as the array size (indices 0-3), with an additional edge.

Analyzing the again:
- It has qbit q[4] (4 qubits)
- Edges (0,1) and (1,2)
- q[3] is measured but never operated on

So the variant with "q[3] -> q[4]" would need q[5] (5 qubits, indices 0-4), with an edge between q[3] and q[4].

But the predicted output show 4-qubit states... This is confusing.

Let me look at the predicted output more carefully:
{|0000>: 0.25, |0100>: 0.25, |1010>: 0.25, |1110>: 0.25}

The bitstrings are 4 bits. If we measure 4 qubits, earlier measured = higher bit. So if we measure M(q[0]), M(q[1]), M(q[2]), M(q[3]) in that order, q[0] is the highest bit.

Actually wait, let me re-read The implementation. It applies H to q[0], q[1], q[2], then CZ(q[0], q[1]), CZ(q[1], q[2]), then H(q[0]), H(q[1]), H(q[2]), then measures all 4.

q[3] starts as |0>, gets H applied... wait no, H is only applied to q[0], q[1], q[2] in the reference. So q[3] stays |0> and measures as 0.

For a linear graph state on qubits 0,1,2:
- Apply H to all three: |+++>
- Apply CZ(0,1) and CZ(1,2): creates the graph state

The graph state for a linear chain 0-1-2 is:
|G> = (1/2)(|000> + |010> + |101> + |111>) in the Z basis... no wait, that's not right.

Let me trace through more carefully:
1. Start: |000>
2. H on all: |+++> = (1/2√2)(|000> + |001> + |010> + |011> + |100> + |101> + |110> + |111>)
3. CZ(0,1): applies Z to q1 when q0 is |1>
   - |0xx> unchanged, |1xx> gets Z on q1
   - |100> -> |

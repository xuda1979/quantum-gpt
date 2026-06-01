# ISQ training COT RAG corpus: quantum_algorithms shard 99

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3814

- task_id: `isqTrain/3814`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_deriving_gate`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5628`

### Prompt

请用isQ语言编写一个量子电路：the swap test to compare states |1> vs |+>. Use:
1. q[0] as ancilla, q[1] for state A, q[2] for state B
2. A controlled-SWAP (Fredkin) gate via CNOT+Toffoli
3. Hadamard on ancilla before and after CSWAP
4. Measure all 3 qubits. P(ancilla=0) = (1+|<A|B>|²)/2.

### Chain-of-thought reasoning

Let me trace through the swap test circuit for comparing |1⟩ and |+⟩.

**Goal**: Implement swap test to measure overlap |⟨1|+⟩|² = 1/2, yielding P(ancilla=0) = 3/4.

**Qubits**: q[0] = ancilla, q[1] = state A = |1⟩, q[2] = state B = |+⟩, all 3 measured.

**State evolution**:

1. Initialize: |000⟩

2. X(q[1]): |010⟩

3. H(q[2]): |01+⟩ = |01⟩⊗(|0⟩+|1⟩)/√2

4. H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |1⟩ ⊗ |+⟩

5. CSWAP (controlled by q[0], swaps q[1] and q[2]):
   - When ancilla is |0⟩: no swap → |0⟩|1⟩|+⟩
   - When ancilla is |1⟩: swap → |1⟩|+⟩|1⟩

6. State after CSWAP:
   (|0⟩|1⟩|+⟩ + |1⟩|+⟩|1⟩)/√2

7. H(q[0]) on ancilla:
   = (|0⟩+|1⟩)/2 ⊗ |1⟩|+⟩ + (|0⟩-|1⟩)/2 ⊗ |+⟩|1⟩
   = |0⟩(|1⟩|+⟩ + |+⟩|1⟩)/2 + |1⟩(|1⟩|+⟩ - |+⟩|1⟩)/2

8. P(ancilla=0) = ‖(|1⟩|+⟩ + |+⟩|1⟩)/2‖² 
   = (1/4)(⟨1|⟨+|+⟨+|⟨1|)(|1⟩|+⟩+|+⟩|1⟩)
   = (1/4)(1 + ⟨+|1⟩⟨1|+⟩ + ⟨1|+⟩⟨+|1⟩ + 1)
   = (1/4)(2 + 2|⟨1|+⟩|²)
   = (1 + |⟨1|+⟩|²)/2
   = (1 + 1/2)/2 = 3/4

Let me verify the full measurement probabilities:

The final state is:
|ψ⟩ = |0⟩(|1⟩|+⟩ + |+⟩|1⟩)/2 + |1⟩(|1⟩|+⟩ - |+⟩|1⟩)/2

Expand |+⟩ = (|0⟩+|1⟩)/√2:

|1⟩|+⟩ = |1⟩(|0⟩+|1⟩)/√2 = (|10⟩+|11⟩)/√2
|+⟩|1⟩ = (|0⟩+|1⟩)|1⟩/√2 = (|01⟩+|11⟩)/√2

|1⟩|+⟩ + |+⟩|1⟩ = (|10⟩+|11⟩+|01⟩+|11⟩)/√2 = (|01⟩+|10⟩+2|11⟩)/√2

|1⟩|+⟩ - |+⟩|1⟩ = (|10⟩+|11⟩-|01⟩-|11⟩)/√2 = (|10⟩-|01⟩)/√2

So:
|ψ⟩ = |0⟩(|01⟩+|10⟩+2|11⟩)/(2√2) + |1⟩(|10⟩-|01⟩)/(2√2)

Let me compute amplitudes for each basis state |abc⟩ where a=q[0], b=q[1], c=q[2]:

|000⟩: 0
|001⟩: from |0⟩|01⟩/(2√2) → coefficient = 1/(2√2), |coeff|² = 1/8 = 0.125
|010⟩: from |0⟩|10⟩/(2√2) → coefficient = 1/(2√2), |coeff|² = 1/8 = 0.125
|011⟩: from |0⟩|11⟩/(2√2) with factor 2 → coefficient = 2/(2√2) = 1/√2, |coeff|² = 1/2 = 0.5
|100⟩: 0
|101⟩: from |1⟩|01⟩/(2√2) → coefficient = -1/(2√2), |coeff|² = 1/8 = 0.125

## isqTrain/3806

- task_id: `isqTrain/3806`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `5674`

### Prompt

Code this in isQ: 4-bit Bernstein-Vazirani to find secret s=1101. Use oracle keyword, for loops for Hadamard. Measure all 5 qubits.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Implement Bernstein-Vazirani to find secret string s=1101 using a phase oracle and measure all 5 qubits.

**Qubits:** 5 qubits — q[0..3] for input, q[4] as ancilla output; all 5 measured.

**State evolution:**
1. Start: |00000⟩
2. X(q[4]): |0000⟩|1⟩
3. H(q[4]): |0000⟩(|0⟩-|1⟩)/√2 = |0000⟩|−⟩
4. H on q[0..3]: (1/4)Σ_x |x⟩|−⟩ (uniform superposition over 16 input states)
5. Oracle f (phase kickback): (1/4)Σ_x (-1)^(s·x)|x⟩|−⟩ where s=1101
6. H on q[0..3]: |1101⟩|−⟩ (Hadamard transform inverts the phase oracle, recovering s)

**Expected probabilities:** The input qubits collapse to |1101⟩ with certainty. The ancilla q[4] remains in |−⟩ = (|0⟩-|1⟩)/√2, yielding 50/50 on measurement. Result: {|11010⟩: 0.5, |11011⟩: 0.5}.

## isqTrain/4034

- task_id: `isqTrain/4034`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_deriving_gate`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3211`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```
import std;
// Swap test: compare |0> vs |1>
// q[0] = ancilla, q[1] = state A, q[2] = state B
qbit q[3];

// Controlled-SWAP (Fredkin gate)
unit cswap(qbit q[3]) {
    CNOT(q[2], q[1]);
    Toffoli(q[0], q[1], q[2]);
    CNOT(q[2], q[1]);
} deriving gate

procedure main() {
    // Prepare state A on q[1]
    // q[1] = |0> (default)
    // Prepare state B on q[2]
    X(q[2]);
    // Swap test circuit
    H(q[0]);
    cswap(q);
    X(q[0]);
    // Measure ancilla and state qubits
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis

**1. Bug identification:**
The bug is on the line `X(q[0]);` after the `cswap(q);` call. In a standard swap test circuit, the ancilla qubit should have a second Hadamard gate applied (not an X gate) to complete the interference measurement.

**2. Fix:**
Replace `X(q[0]);` with `H(q[0]);`. The swap test requires H on the ancilla before AND after the controlled-swap (three-CNOT decomposition) to create proper interference between the |+⟩ and |−⟩ branches of the ancilla.

**3. State evolution (corrected circuit):**
- Initial: |000⟩ → After X(q[2]): |001⟩
- After H(q[0]): (|001⟩ + |101⟩)/√2
- After cswap (swaps q[1]↔q[2] when q[0]=|1⟩): (|001⟩ + |110⟩)/√2
- After H(q[0]): (|001⟩ + |101⟩ + |010⟩ − |110⟩)/2
- Measurement yields {|001⟩, |010⟩, |101⟩, |110⟩} each with probability 0.25 ✓

## isqTrain/4130

- task_id: `isqTrain/4130`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `2985`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[4];

procedure main() {
    X(q[3]);
    H(q[0]); H(q[1]); H(q[2]);
    ctrl Rz(2.0 * 3.14159265358979 * 1.0 / 8.0 * 1.0, q[0], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 1.0 / 8.0 * 2.0, q[1], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 1.0 / 8.0 * 4.0, q[2], q[3]);
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    H(q[0]);
    ctrl Rz(-3.14159265358979 / 2.0, q[1], q[0]);
    ctrl Rz(-3.14159265358979 / 4.0, q[2], q[0]);
    H(q[1]);
    ctrl Rz(-3.14159265358979 / 2.0, q[2], q[1]);
    H(q[2]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

Let me analyze this isQ circuit step by step.

First, let me understand the structure:
- 4 qubits: q[0], q[1], q[2], q[3]
- Initial state: |0000⟩

Step 1: X(q[3])
- State becomes |0001⟩ (q[3] is flipped)

Step 2: H(q[0]), H(q[1]), H(q[2])
- Apply Hadamard to first 3 qubits
- State becomes (1/2√2)(|0⟩+|1⟩)(|0⟩+|1⟩)(|0⟩+|1⟩) ⊗ |1⟩
- = (1/2√2) Σ_{x=0}^{7} |x⟩|1⟩

Step 3: Controlled phase rotations
- ctrl Rz(2π/8, q[0], q[3]): phase rotation by π/4 when q[0]=1
- ctrl Rz(2π/4, q[1], q[3]): phase rotation by π/2 when q[1]=1
- ctrl Rz(2π/2, q[2], q[3]): phase rotation by π when q[2]=1

These are applying phases to |1⟩ on q[3] based on the control qubits. 

Wait, let me reconsider. The Rz gate acts on q[3] conditioned on the control qubit. When the control is |1⟩, Rz(θ) is applied to q[3].

Rz(θ)|1⟩ = e^{-iθ/2}|1⟩

So each controlled Rz applies a phase e^{-iθ/2} to q[3] when control is |1⟩.

The total phase applied to |x₀x₁x₂⟩|1⟩ is:
- e^{-i(2π/8)/2 * x₀} * e^{-i(2π/4)/2 * x₁} * e^{-i(2π/2)/2 * x₂}
= e^{-iπx₀/8} * e^{-iπx₁/4} * e^{-iπx₂/2}
= e^{-iπ(x₀ + 2x₁ + 4x₂)/8}
= e^{-iπx/8}

where x = x₀ + 2x₁ + 4x₂.

Wait, actually I need to be more careful. The Rz gate has the form:
Rz(θ) = [[1,0],[0,e^{iθ}]]

So Rz(θ)|1⟩ = e^{iθ}|1⟩

But in isQ, let me check. The standard convention for Rz is:
Rz(θ) = e^{-iθZ/2} = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]

So Rz(θ)|1⟩ = e^{iθ/2}|1⟩

The phase applied when control is |1⟩ is e^{iθ/2}.

For ctrl Rz(2π/8 * 1.0, q[0], q[3]): θ = 2π/8 = π/4, phase = e^{iπ/8}
For ctrl Rz(2π/8 * 2.0, q[1], q[3]): θ = π/2, phase = e^{iπ/4}  
For ctrl Rz(2π/8 * 4.0, q[2], q[3]): θ = π, phase = e^{iπ/2}

So the state after these gates is:
(1/2√2) Σ_{x₀,x₁,x₂ ∈ {0,1}} e^{i(π/8 * x₀ + π/4 * x₁ + π/2 * x₂)} |x₀x₁x₂⟩|1⟩

The phase is e^{iπ(x₀ + 2x₁ + 4x₂)/8} = e^{iπx/8} where x = x₀ + 2x₁ + 4x₂.

Now Step 4: CNOT(q[0], q[2]); CNOT(q[2], q[0]); CNOT(q[0], q[2])

This is a swap operation (three-CNOT decomposition) between q[0] and q[2]... wait, no. Let me think again.

CNOT(c, t) does: |c,t⟩ → |c, c⊕t⟩

After CNOT(q[0], q[2]): |a,b,c,d⟩ → |a,b,a⊕c,d⟩
After CNOT(q[2], q[0]): |a,b,a⊕c,d⟩ → |a⊕

### Reference answer

Dominant output states: |1001> with probability ~0.43 each

## isqQA/quantum_algorithms/97_comparison

- task_id: `isqQA/quantum_algorithms/97_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `comparison`, `algorithm`, `Grover最优迭代次数推导`
- source: `qa_pipeline`
- dataset_index: `357`

### Prompt

请详细推导Grover搜索算法中寻找目标态的最优迭代次数$k_{opt}$的数学过程。进一步地，请从计算复杂度、有界错误概率及底层搜索空间结构的角度，深度对比分析Grover算法与经典线性搜索算法、以及针对有序数据库的经典二分查找算法在优缺点和实际适用场景上的显著差异。最后，请使用isQ代码展示一个在4个量子比特中搜索单一目标态的最优Grover迭代线路。

### Reference answer

在量子计算领域，Grover搜索算法以其卓越的二次加速特性闻名。要理解其精髓，首先需要严格推导其最优迭代次数。

首先推导最优迭代次数。假设在大小为$N=2^n$的无结构搜索空间中，有$M$个目标态。初始化后，系统处于均匀叠加态：
$|s\rangle = \frac{1}{\sqrt{N}} \sum_{x=0}^{N-1} |x\rangle$
我们将整个希尔伯特空间划分为由目标态张成的子空间及其正交补空间。定义二维平面中的两个基底：
$|\alpha\rangle = \frac{1}{\sqrt{N-M}} \sum_{x \notin \text{target}} |x\rangle$
$|\beta\rangle = \frac{1}{\sqrt{M}} \sum_{x \in \text{target}} |x\rangle$
初始态可以重写为 $|s\rangle = \sqrt{\frac{N-M}{N}} |\alpha\rangle + \sqrt{\frac{M}{N}} |\beta\rangle$。令 $\sin(\theta/2) = \sqrt{\frac{M}{N}}$，则初始态变为 $|s\rangle = \cos(\theta/2)|\alpha\rangle + \sin(\theta/2)|\beta\rangle$。
每一次Grover迭代包含一次Oracle操作和一次扩散操作。在几何上，这等价于将状态向量在 $|\alpha\rangle$ 和 $|\beta\rangle$ 张成的平面内，向目标子空间 $|\beta\rangle$ 旋转 $\theta$ 角度。经过 $k$ 次迭代后，系统状态变为：
$|\psi_k\rangle = \cos\left(\frac{2k+1}{2}\theta\right)|\alpha\rangle + \sin\left(\frac{2k+1}{2}\theta\right)|\beta\rangle$
为了最大化测量到目标态的概率，我们需要使正弦项的平方逼近1，即 $\sin^2\left(\frac{2k+1}{2}\theta\right) = 1$。这要求 $\frac{2k+1}{2}\theta = \frac{pi}{2}$，解得 $k = \frac{\pi}{2\theta} - \frac{1}{2}$。
当 $M \ll N$ 时，$\theta \approx 2\sqrt{M/N}$。因此，最优迭代次数为 $k_{opt} = \text{round}\left(\frac{\pi}{4}\sqrt{\frac{N}{M}} - \frac{1}{2}\right) \approx O(\sqrt{N/M})$。

接下来对比分析Grover算法与其他经典算法的优缺点及适用场景：
1. **对比经典线性搜索**：经典线性搜索的时间复杂度为 $O(N/M)$。Grover算法实现了 $O(\sqrt{N/M})$ 的二次加速。其优点在于对于完全无结构的搜索问题，Grover算法在计算复杂度上达到了理论极限（Bennett等人证明无结构量子搜索的下界就是 $O(\sqrt{N})$）。缺点是它需要依赖高保真度的量子硬件，且由于只有近似1的概率，属于有界错误概率多项式时间（BPP）的量子对应，可能需要多次重复测量以保证极低的错误率。适用场景包括无结构数据库的匹配查找、NP完全问题的暴力破解优化（如SAT求解）等。
2. **对比经典二分查找**：二分查找针对的是“有序且可索引”的搜索空间，其时间复杂度仅为 $O(\log N)$。显然对于具有全局有序结构的特定问题，Grover算法（$O(\sqrt{N})$）在渐进复杂度上劣于二分查找。然而，Grover算法的优点在于它不需要搜索空间具备任何全局有序结构，这在许多实际工程和物理问题中极为关键。此外，在经典黑盒（Oracle）无法直接提取全局排序信息的场景（如密码学中的函数碰撞寻找、非结构化的优化问题）中，Grover算法具有不可替代的优势。

以下是用isQ语言编写的4个量子比特（$N=16$）搜索单一目标态（假设目标为15，即$|1111\rangle$）的最优Grover迭代代码。计算得出 $k_{opt} \approx 3$：

```isQ
import std;

qbit q[4];

procedure main() {
    // Step 1: 初始化均匀叠加态
    for i in 0:4 {
        H(q[i]);
    }
    
    // Step 2: 进行 k_opt = 3 次最优Grover迭代
    for iter in 0:3 {
        
        // Oracle: 标记目标态 |1111>
        // 由于 |1111> 的相位翻转可以等效为 H(target) 后执行多控X(MCX) 再 H(target)
        // 这里使用 Toffoli 门级联实现多控 X，目标位选 q[3]
        H(q[3]);
        Toffoli(q[0], q[1], q[2]);
        // 使用辅助逻辑实现四控 X
        ctrl @[q[0], q[1], q[2]] X(q[3]);
        H(q[3]);

        // Step 3: 执行扩散算子
        for i in 0:4 {
            H(q[i]);
            X(q[i]);
        }
        
        H(q[3]);
        Toffoli(q[0], q[1], q[2]);
        ctrl @[q[0], q[1], q[2]] X(q[3]);
        H(q[3]);
        
        for i in 0:4 {
            X(q[i]);
            H(q[i]);
        }
    }
    
    // Step 4: 测量
    for i in 0:4 {
        M(q[i]);
    }
}
```

## isqTrain/2935

- task_id: `isqTrain/2935`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_for_loop`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3045`

### Prompt

Implement a quantum circuit in isQ: creates a uniform superposition over 4 qubits by applying Hadamard to each qubit.

Requirements:
- Declare `qbit q[4];` at global scope.
- Use a for loop to apply H gates.
- Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a uniform superposition over all 16 basis states of 4 qubits.
2. **Qubits**: 4 qubits (`q[0]`–`q[3]`), all measured.
3. **State evolution**:
   - Initial state: |0000⟩
   - After H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |000⟩ = |+⟩|000⟩
   - After H(q[1]): |+⟩|+⟩|00⟩
   - After H(q[2]): |+⟩|+⟩|+⟩|0⟩
   - After H(q[3]): |+⟩⊗⁴ = (1/4) Σ_{x∈{0,1}⁴} |x⟩
4. **Probabilities**: Each of the 16 basis states has amplitude 1/4, giving probability |1/4|² = 1/16 = 0.0625 for every outcome.

## isqQA/quantum_algorithms/126_application_scenario

- task_id: `isqQA/quantum_algorithms/126_application_scenario`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `application_scenario`, `algorithm`, `隐藏子群问题`
- source: `qa_pipeline`
- dataset_index: `1731`

### Prompt

隐藏子群问题（HSP）被公认为量子计算领域最核心的算法统一框架之一。请您详细阐述HSP在破解现有公钥密码体系（特别是RSA和椭圆曲线密码ECC）中的具体应用机制，并探讨将该算法框架扩展到非阿贝尔群以解决图同构问题（Graph Isomorphism）时的理论前景与当前面临的主要挑战。

### Reference answer

<think 

需要推导HSP在RSA和ECC中的数学映射，并展示一个用于提取周期信息的简化量子电路结构代码。

数学推导：
对于RSA，大整数分解可以转化为寻找阶的问题。给定整数N和a，定义函数f(x) = a^x mod N。该函数具有周期性，即存在隐藏周期r使得f(x+r) = f(x)。这其实是有限生成阿贝尔群上的HSP，隐藏子群为H = rZ。
对于ECC，椭圆曲线离散对数问题（ECDLP）可以转化为寻找群加法周期的问题。在群G中寻找点P的标量k使得kP = Q，这对应于阿贝尔群Z×Z上的HSP。
在这两种情况下，量子算法通过量子傅里叶变换（QFT）提取出隐藏子群的特征标。

isQ代码演示：
展示一个提取阿贝尔群周期的基础电路结构（包含叠加、受控函数映射和逆QFT）。
</think 

隐藏子群问题（HSP）为许多知名的量子算法提供了一个极其优雅的统一框架。其核心目标是：给定一个群G和一个黑盒函数f，该函数在某个未知子群H的各个陪集上是常数，即f(x) = f(y)当且仅当xH = yH。量子算法的目标是通过最少的查询次数，提取出隐藏子群H的特征信息。

在实际应用中，HSP最震撼的案例便是彻底瓦解了当前广泛使用的公钥密码基础设施。Shor算法本质上就是阿贝尔群（满足交换律的群）上的HSP实例。
1. 破解RSA（大整数分解）：RSA的安全性依赖于大整数分解的困难性。在量子计算中，这被转化为求函数f(x) = a^x mod N周期r的问题。这里的群G是整数加法群Z，函数f的周期性意味着其隐藏了一个子群H = rZ（即所有r的倍数）。利用HSP框架，量子计算机首先对群元素进行均匀叠加，接着计算函数f并存入辅助寄存器，产生纠缠态。随后对第一寄存器施加量子傅里叶变换（QFT），由于阿贝尔群的QFT能够高效地将陪集态投影到特征标上，测量后可以极高的概率提取出周期r。一旦获得r，即可通过经典数论方法快速分解N。
2. 破解ECC（椭圆曲线密码）：类似地，Shor算法可以无缝移植到椭圆曲线离散对数问题（ECDLP）上，此时底层的群变成了椭圆曲线上的点构成的有限阿贝尔群。HSP框架同样能通过QFT在多项式时间内提取出隐藏的离散对数。

为了更直观地理解这一过程，以下提供一个用于提取阿贝尔群隐藏周期的基础量子电路代码（基于isQ语言），展示了状态叠加、函数映射（模拟）以及逆QFT的核心逻辑：

import std;

qbit q[3]; // 工作寄存器，用于群元素的均匀叠加
qbit anc[2]; // 辅助寄存器，模拟函数f(x)的映射结果

procedure main() {
    // 1. 对工作寄存器施加Hadamard门，创建群G上所有元素的均匀叠加态
    for i in 0:3 {
        H(q[i]);
    }
    
    // 2. 模拟量子黑盒函数 U_f: |x>|0> -> |x>|f(x)>
    // 在真实的RSA破解中，这里实现的是模幂运算 a^x mod N
    // 此处用CNOT操作简化模拟函数的周期性映射
    CNOT(q[1], anc[0]);
    CNOT(q[2], anc[1]);
    
    // 辅助寄存器由于不和后续操作纠缠，测量或丢弃均可（此处省略）
    
    // 3. 对工作寄存器应用逆量子傅里叶变换 (IQFT)
    // 以提取出隐藏子群的特征（周期信息）
    for i in 0:3 {
        for j in 0:i {
            // 控制相位旋转
            double angle = -3.1415926535 / (2 ** (i - j + 1));
            ctrl @[q[j]] Rz(angle, q[i]);
        }
        H(q[i]);
    }
    
    // 4. 测量工作寄存器，结果将包含隐藏子群H的周期特征
    for i in 0:3 {
        M(q[i]);
    }
}

另一方面，将HSP的理论前景推向非阿贝尔群（即不满足交换律的群）是当前量子算法研究的热点与前沿。其最具代表性的潜在应用是解决图同构问题（GI）。图同构问题可以规约为在对称群（Symmetric Group，排列群）上寻找隐藏子群的问题。如果能够设计出针对非阿贝尔群的高效量子算法，不仅意味着解决了图同构这一著名的复杂度类难题，还将对计算化学、网络拓扑分析等领域产生深远影响。

然而，将HSP扩展到非阿贝尔群面临着巨大的挑战。其主要原因在于，针对非阿贝尔群的量子傅里叶变换极其复杂，其群特征标不再是简单的复指数函数，而是高维矩阵表示。标准测量方法无法从非阿贝尔群的特征标中轻易提取出足够的H信息，导致信息泄漏或需要指数级的测量采样。因此，寻找有效的非阿贝尔特征标测量方案或全新的非交换傅里叶分析框架，是未来量子计算领域亟待攻克的重大课题。

## isqTrain/116

- task_id: `isqTrain/116`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `multi_controlled_logic`, `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5455`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the amplitude_amplification pattern using q[4] -> q[6]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Looking at this task, I need to generate reasoning for an amplitude amplification variant circuit in isQ.

The circuit uses 6 qubits (q[0] to q[5]), but the main computation involves q[0], q[1], q[2] (search space) and q[3] (ancilla). Qubits q[4] and q[5] are added as requested but never used - they remain in |0⟩ state.

Let me trace through the circuit:

1. **Initial setup:**
   - X(q[3]): q[3] becomes |1⟩
   - H(q[3]): q[3] becomes |−⟩ = (|0⟩ - |1⟩)/√2
   - H(q[0]), H(q[1]), H(q[2]): Creates superposition over 8 basis states
   
   State: |ψ⟩ = (1/√8) Σ|x⟩ ⊗ |−⟩ ⊗ |0⟩ ⊗ |0⟩ for x ∈ {0,1}³

2. **Oracle (ctrl ctrl ctrl X on q[0],q[1],q[2],q[3])):**
   - This flips the ancilla q[3] when q[0]=q[1]=q[2]=1 (i.e., |111⟩)
   - Since q[3] is in |−⟩, this applies a phase of -1 to the |111⟩ component
   
   After oracle: |ψ⟩ = (1/√8)(|000⟩ + ... + |110⟩ - |111⟩) ⊗ |−⟩ ⊗ |0⟩ ⊗ |0⟩

3. **Diffuser:**
   - H on q[0], q[1], q[2]
   - X on q[0], q[1], q[2]
   - Controlled Z (Hadamard-like reflection)
   - X on q[0], q[1], q[2]
   - H on q[0], q[1], q[2]
   
   The diffuser amplifies the marked state |111⟩.

4. **After 2 iterations**, the amplitude of |111⟩ is amplified significantly.

Let me calculate the amplitudes more carefully:

Initial amplitudes: All 8 states have amplitude 1/√8 = 1/(2√2) ≈ 0.354

After marking |111⟩ with phase -1:
- Amplitudes for |000⟩ through |110⟩: +1/(2√2)
- Amplitude for |111⟩: -1/(2√2)

Diffuser effect: Reflect about the mean amplitude.
Mean = (7 × 1/(2√2) - 1/(2√2))/8 = (6/(2√2))/8 = 6/(16√2) = 3/(8√2)

After first diffuser:
- For |000⟩ through |110⟩: amplitude = 2 × mean - original = 2 × 3/(8√2) - 1/(2√2) = 3/(4√2) - 1/(2√2) = 3/(4√2) - 2/(4√2) = 1/(4√2)
- For |111⟩: amplitude = 2 × mean - (-1/(2√2)) = 3/(4√2) + 1/(2√2) = 3/(4√2) + 2/(4√2) = 5/(4√2)

After second oracle:
- For |000⟩ through |110⟩: +1/(4√2)
- For |111⟩: -5/(4√2)

Mean = (7 × 1/(4√2) - 5/(4√2))/8 = (7 - 5)/(4√2 × 8) = 2/(32√2) = 1/(16√2)

After second diffuser:
- For |000⟩ through |110⟩: 2 × 1/(16√2) - 1/(4√2) = 1/(8√2) - 1/(4√2) = 1/(8√2) - 2/(8√2) = -1/(8√2)
- For |111⟩: 2 × 1/(16√2) - (-5/(4√2)) = 1/(8√2) + 5/(4√2) = 1/(8√2) + 10/(8√2) = 11/(8√2)

Now probabilities:
- P(|111⟩) = |11/(8√2)|² = 121/128 ≈ 0.9453
- P(other) each = |1/(8√2)|² = 1/128

## isqExpand/algo/36

- task_id: `isqExpand/algo/36`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `hhl`, `controlled_rotation`, `eigenvalue_inversion`, `output_prediction`
- source: `isq_expansion`
- dataset_index: `2857`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit clock[2];
qbit anc[1];

procedure main() {
    X(clock[0]);
    nctrl ctrl Ry(1.04720, clock[1], clock[0], anc[0]);
    M(anc[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis

1. X(clock[0]): clock[0]=1, clock[1]=0 -> clock = |10>
2. nctrl@[clock[1]] ctrl@[clock[0]] Ry(1.04720, anc[0]):
   - nctrl on clock[1]: active when clock[1]=0 (satisfied)
   - ctrl on clock[0]: active when clock[0]=1 (satisfied)
   - Both conditions met, Ry(1.04720) applied to anc[0]

3. Ry(theta)|0> = cos(theta/2)|0> + sin(theta/2)|1>
   theta = 1.04720 = pi/3
   theta/2 = pi/6
   cos(pi/6) = sqrt(3)/2
   sin(pi/6) = 1/2

4. P(|0>) = cos^2(pi/6) = 3/4 = 0.75
   P(|1>) = sin^2(pi/6) = 1/4 = 0.25

sin(pi/6) = 0.5 = c/lambda = 1/2 confirms the HHL eigenvalue inversion.
Probs: [0.75, 0.25]

### Reference answer

{'predicted_probs': {'0': 0.75, '1': 0.25}, 'explanation': 'The clock is set to |10> (clock[0]=1, clock[1]=0). The controlled rotation activates when clock[0]=1 AND clock[1]=0 (ctrl on clock[0], nctrl on clock[1]). Both conditions are met. Angle = 1.04720 = pi/3 = 2*arcsin(1/2). Ry(pi/3)|0> = cos(pi/6)|0> + sin(pi/6)|1> = (sqrt(3)/2)|0> + (1/2)|1>. P(|0>) = 3/4 = 0.75, P(|1>) = 1/4 = 0.25. The amplitude sin(pi/6) = 1/2 = c/lambda confirms the eigenvalue inversion encoding.'}

## isqTrain/790

- task_id: `isqTrain/790`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `finite_field_arithmetic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3011`

### Prompt

请用isQ语言编写一个量子电路：implements the gf2_multiplication pattern. Include explicit identity operations in the circuit (H-H pair before M(q[3])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement GF(2) polynomial multiplication a(x)·b(x) where a(x)=1+x and b(x)=1, computing product coefficients p0 and p1 via AND operations (Toffoli gates).

2. **Qubits**: 5 qubits — q[0]=a0, q[1]=a1, q[2]=b0, q[3]=p0, q[4]=p1. Only q[3] and q[4] are measured.

3. **State evolution**:
   - Initial: |00000⟩
   - After X(q[0]), X(q[1]), X(q[2]): |11100⟩ (sets a0=1, a1=1, b0=1)
   - Toffoli(q[0],q[2],q[3]): p0 = a0∧b0 = 1 → |11110⟩
   - Toffoli(q[1],q[2],q[4]): p1 = a1∧b0 = 1 → |11111⟩
   - H(q[3]): q[3] → (1/√2)(|0⟩−|1⟩), state becomes (1/√2)(|11101⟩−|11111⟩)
   - H(q[3]): H†H = I on q[3], cancels out → |11111⟩

4. **Expected result**: The H-H identity pair cancels, leaving q[3]=|1⟩ and q[4]=|1⟩. Measurement yields |11⟩ with probability 1.0, confirming GF(2) product (1+x)·1 = 1+x.

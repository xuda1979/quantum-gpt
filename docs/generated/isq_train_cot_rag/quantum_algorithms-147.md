# ISQ training COT RAG corpus: quantum_algorithms shard 147

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/algo/83

- task_id: `isqExpand/algo/83`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `qft`, `inverse_qft`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_expansion`
- dataset_index: `3018`

### Prompt

Write isQ code for the following quantum task: implements the 3-qubit inverse Quantum Fourier Transform (IQFT). First prepare the equal superposition |+++> by applying H to all 3 qubits, then apply the inverse QFT circuit. The IQFT is the reverse of QFT with conjugated rotation gates: H(q[2]), ctrl @[q[2]] inv S(q[1]), H(q[1]), ctrl @[q[2]] inv T(q[0]), ctrl @[q[1]] inv S(q[0]), H(q[0]). Since IQFT is the inverse of QFT and QFT|000> = |+++>, applying IQFT to |+++> should recover |000>.

### Chain-of-thought reasoning

## 推理
目标：在|+++>上施加3比特逆QFT，恢复|000>。

### IQFT电路
3比特QFT（无位反转）的步骤为：
H(q[0]), ctrl@[q[1]]S(q[0]), ctrl@[q[2]]T(q[0]), H(q[1]), ctrl@[q[2]]S(q[1]), H(q[2])

逆QFT是QFT的逆操作，需要反转门的顺序并取共轭：
H(q[2]), ctrl@[q[2]] inv S(q[1]), H(q[1]), ctrl@[q[2]] inv T(q[0]), ctrl@[q[1]] inv S(q[0]), H(q[0])

### 验证
QFT|000> = |+++>（均匀叠加）
因此IQFT|+++> = |000>

预期概率：[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

## isqTrain/3435

- task_id: `isqTrain/3435`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `phase_manipulation`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4395`

### Prompt

I need an isQ program to one Trotter step of a 3-qubit Ising chain with nearest-neighbor ZZ coupling and transverse X field in isQ.

H = -J*(Z_0*Z_1 + Z_1*Z_2) - h*(X_0 + X_1 + X_2)
Use J=1.0, h=0.5, dt=0.3.

Trotter decomposition:
1. ZZ on (q[0], q[1]): CNOT, Rz(2*J*dt=0.6), CNOT
2. ZZ on (q[1], q[2]): CNOT, Rz(0.6), CNOT
3. X field: Rx(2*h*dt=0.3) on each qubit

Start from |000>. Declare 3 qubits, measure all.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The goal is to implement one Trotter step of a 3-qubit Ising chain with Hamiltonian H = -J*(Z_0*Z_1 + Z_1*Z_2) - h*(X_0 + X_1 + X_2) where J=1.0, h=0.5, dt=0.3.

Starting state: |000>

Step 1: ZZ coupling on (q[0], q[1])
- CNOT(q[0], q[1]): |000> → |000>
- Rz(0.6, q[1]): |000> → e^{-i*0.6/2} |000> = e^{-i*0.3} |000>
- CNOT(q[0], q[1]): e^{-i*0.3} |000>

Step 2: ZZ coupling on (q[1], q[2])
- CNOT(q[1], q[2]): e^{-i*0.3} |000>
- Rz(0.6, q[2]): e^{-i*0.3} * e^{-i*0.3} |000> = e^{-i*0.6} |000>
- CNOT(q[1], q[2]): e^{-i*0.6} |000>

Step 3: Rx(0.3) on each qubit
Rx(θ) = exp(-iθX/2), so Rx(0.3) = cos(0.15)|0> - i*sin(0.15)|1>

Applying to each qubit:
e^{-i*0.6} * [cos(0.15)|0> - i*sin(0.15)|1>] ⊗ [cos(0.15)|0> - i*sin(0.15)|1>] ⊗ [cos(0.15)|0> - i*sin(0.15)|1>]

Let me compute the probabilities:
cos(0.15) ≈ 0.98877
sin(0.15) ≈ 0.14944

|000>: cos^3(0.15) ≈ 0.9663
|001>: cos^2(0.15)*sin(0.15) ≈ 0.1461
...

Wait, these don't match the predicted output. Let me reconsider.

Actually, the predicted output given are:
{|000>: 0.93449, |001>: 0.021345, |010>: 0.021345, |011>: 0.000488, |100>: 0.021345, |101>: 0.000488, |110>: 0.000488, |111>: 1.1e-05}

Let me check: if we just apply Rx(0.3) to |0>:
Rx(0.3)|0> = cos(0.15)|0> - i*sin(0.15)|1>

cos(0.15) ≈ 0.98877, sin(0.15) ≈ 0.14944

P(|0>) = cos^2(0.15) ≈ 0.97767
P(|1>) = sin^2(0.15) ≈ 0.02233

For three independent qubits:
P(|000>) = 0.97767^3 ≈ 0.93449 ✓
P(|001>) = 0.97767^2 * 0.02233 ≈ 0.02135 ✓

Yes! So the ZZ coupling terms only contribute global phases from the |000> state, and the final probabilities are determined by the Rx rotations.

Let me be more careful about the Rz gate. Rz(θ) has matrix:
[[e^{-iθ/2}, 0], [0, e^{iθ/2}]]

For |0>: Rz(θ)|0> = e^{-iθ/2}|0>
For |1>: Rz(θ)|1> = e^{iθ/2}|1>

Starting from |000>:
1. CNOT(q[0], q[1]): |000> (no change, control is |0>)
2. Rz(0.6, q[1]): e^{-i*0.3}|000>
3. CNOT(q[0], q[1]): e^{-i*0.3}|000>

4. CNOT(q[1], q[2]): e^{-i*0.3}|000>
5. Rz(0.6, q[2]): e^{-i*0.6}|000>
6.

## isqQA/quantum_algorithms/96_application_scenario

- task_id: `isqQA/quantum_algorithms/96_application_scenario`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `application_scenario`, `algorithm`, `Grover算法的扩散算子`
- source: `qa_pipeline`
- dataset_index: `5789`

### Prompt

在实际应用中，Grover算法及其核心组件扩散算子（Diffusion Operator）不仅限于简单的数据库查找，还被广泛用于解决复杂的组合优化问题和密码分析。请阐述扩散算子在解决此类实际问题时发挥的作用及其未来的应用前景，并给出一个使用isQ语言实现的针对4个量子比特系统的通用扩散算子代码示例。

### Reference answer

Grover算法的扩散算子（也称为Grover扩散算子或条件相移算子）是量子搜索算法中实现“幅度放大”的核心机制。在实际应用中，它的作用类似于将向量关于其均值进行反转，从而不断放大目标状态的概率幅度，同时压制非目标状态的概率幅度。

在解决实际问题时，扩散算子的应用场景与前景主要体现在以下几个方面：
1. **密码分析与网络安全**：在破解诸如AES等对称加密系统时，传统暴力破解的时间复杂度为$O(N)$，而利用神谕机和扩散算子构建的Grover搜索算法可以将复杂度降至$O(\sqrt{N})$。扩散算子在这里起到了关键的加速导航作用，使得量子计算机能够以平方级速度迅速锁定正确的密钥态。
2. **组合优化问题**：如旅行商问题（TSP）、最大割问题或蛋白质折叠问题。在这些问题中，常常需要在一个巨大的可能解空间中寻找满足特定约束的最优解。通过设计特定的神谕机来标记较差的解或标记最优解，再辅以扩散算子，可以极大地加速全局最优解的搜索过程。这种启发式与量子搜索的结合在物流调度、金融投资组合优化中具有广阔的商业前景。
3. **量子机器学习**：在量子无监督学习和聚类算法中，扩散算子被用于寻找最近邻或计算距离，帮助在海量未标记的数据中快速提取出有价值的模式。

虽然目前处于NISQ（含噪声中等规模量子）时代，长深度的扩散算子容易受到量子噪声的干扰，但随着量子纠错技术的发展，基于扩散算子的各类启发式量子搜索必将在大数据和人工智能领域发挥颠覆性的作用。

下面是一个使用isQ语言编写的4个量子比特通用扩散算子代码示例。扩散算子的数学定义为 $D = 2|\psi\rangle\langle\psi| - I$，通常通过 $H^{\otimes n} (2|0\rangle\langle0| - I) H^{\otimes n}$ 实现，其中 $(2|0\rangle\langle0| - I)$ 等价于对除了 $|0000\rangle$ 之外的所有计算基态施加 $-1$ 的相位，这可以通过对全量子比特使用X门、执行多控Z门（$C^3Z$），然后再使用X门来实现：

```isQ
import std;

qbit q[4];
qbit anc[1];

procedure diffusion() {
    // 步骤 1：对所有量子比特应用Hadamard门
    for i in 0:4 {
        H(q[i]);
    }
    
    // 步骤 2：对所有量子比特应用X门
    for i in 0:4 {
        X(q[i]);
    }
    
    // 步骤 3：实现多控Z门 (C^3Z)
    // 使用辅助量子比特将4-qubit控制分解为两个Toffoli门
    // 将受控Z转化为受控X（即CNOT）：H(target); CNOT; H(target)
    Toffoli(q[0], q[1], anc[0]);
    H(q[3]);
    Toffoli(q[2], anc[0], q[3]);
    H(q[3]);
    Toffoli(q[0], q[1], anc[0]); // 逆转以恢复辅助比特状态
    
    // 步骤 4：再次对所有量子比特应用X门
    for i in 0:4 {
        X(q[i]);
    }
    
    // 步骤 5：对所有量子比特应用Hadamard门
    for i in 0:4 {
        H(q[i]);
    }
}

procedure main() {
    // 初始化等权重叠加态
    for i in 0:4 {
        H(q[i]);
    }
    
    // (这里假设已存在标记目标状态的Oracle)
    // oracle();
    
    // 应用扩散算子进行幅度放大
    diffusion();
}
```

## isqTrain/1093

- task_id: `isqTrain/1093`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3536`

### Prompt

Implement the following in isQ: implements a variant of the bernstein_vazirani pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

This task asks me to explain the reasoning behind a Bernstein-Vazirani circuit that uses q[3] -> q[4] (so 4 input qubits) instead of the base version (which uses 3 input qubits).

Let me analyze The implementation:
- It uses qbit q[4] as the input register and qbit anc[1] as the ancilla
- The oracle computes f(x) = s · x mod 2 where s appears to be related to x[0] and x[2]
- The oracle returns `[x[0] != x[2]]` which is equivalent to x[0] XOR x[2]
- So the hidden string s = 101 (where s[0]=1, s[1]=0, s[2]=1)

Wait, the oracle signature says `bool x[3]` but we have q[4]. This seems inconsistent. Let me re-read.

Looking at the oracle: `oracle bool[1] f(bool x[3])` - it takes 3 input bits
The call is `f(q, anc)` - but q is size 4

There's an inconsistency In the implementation. The oracle expects 3 qubits but q has 4 elements.

Let me think about what The predicted output: `|1010>` with probability 1.0

So the measurement yields bits corresponding to 1010 = 10 in decimal.

For 4 measured qubits, the bitstring would be:
- q[0] = 1 (highest bit)
- q[1] = 0
- q[2] = 1
- q[3] = 0 (lowest bit)

So q[0]=1, q[1]=0, q[2]=1, q[3]=0.

In Bernstein-Vazirani, the measurement of the input register should reveal the hidden string s. If s = 101 (3 bits), then q[0], q[1], q[2] should measure to 1, 0, 1 respectively. q[3] is the extra qubit which should measure to 0.

Let me trace through the circuit:

1. Initial state: |0000>|0>

2. X(anc[0]): |0000>|1>

3. H(anc[0]): |0000>|-> = |0000>(|0>-|1>)/√2

4. H(q[0]), H(q[1]), H(q[2]): Uniform superposition on first 3 qubits
   (1/2√2) Σ|x[0]x[1]x[2]>|0> ⊗ |-> where q[3] stays |0>

5. f(q, anc): The oracle applies phase kickback
   For each basis state |x>, the ancilla in |-> picks up a phase of (-1)^f(x)
   f(x) = x[0] XOR x[2]
   So the state becomes: (1/2√2) Σ|x> (-1)^(x[0]⊕x[2]) |-> ⊗ |0>
   
   where s = 101, so s·x = x[0]·1 ⊕ x[1]·0 ⊕ x[2]·1 = x[0] ⊕ x[2]

6. H(q[0]), H(q[1]), H(q[2]): The Hadamard transform on the first 3 qubits
   
   H^⊗3 applied to Σ|x>(-1)^(s·x) gives |s> = |101>
   
   So the state is |101>|0>|->

7. Measurement: q[0]=1, q[1]=0, q[2]=1, q[3]=0

So the final bitstring is 1010 (q[0] as most significant, q[3] as least significant).

Now let me write the reasoning:

## Reasoning
1. Goal: Implement Bernstein-Vazirani algorithm with hidden string s=101 using a 4-qubit input register (expanded from 3).

2. Qubits: 4 input qubits (q[0]-q[3]) plus 1 ancilla (anc[0]); all 4 input qubits measured.

3. State evolution:
   - Initial: |0000>|0>
   - X, H on ancilla: |0000>|-> 
   - H on q[0],q[1],q[2]: (1/√8)Σ|x[0]x[1]x[2]>|0>|->  (q[3] stays |0>)
   - Oracle f(q,anc): Phase kickback applies (-1)^(x[0]⊕x[2]), encoding s=101
   -

## isqTrain/2805

- task_id: `isqTrain/2805`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4129`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[5];

procedure main(){
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

1.  **Understand the Goal**: The task is to analyze the provided isQ quantum program, trace its state evolution, and predict its measurement probability distribution as a JSON array (though the prompt asks for the analysis text ending with the predicted probability distribution, the instructions say "Output ONLY the analysis, starting with '## Circuit Analysis'", so I will follow this specific format).

2.  **Analyze the Circuit**:
    *   Initialization: 5 qubits, `q[0]` to `q[4]`, initialized to $|00000\rangle$.
    *   Loop 1: `H` on `q[0]`, `q[1]`, `q[2]`, `q[3]`, `q[4]`.
        *   State becomes $|+\rangle_0 |+\rangle_1 |+\rangle_2 |+\rangle_3 |+\rangle_4 = \frac{1}{\sqrt{32}} \sum_{x \in \{0,1\}^5} |x\rangle$.
    *   CNOT operations:
        *   `CNOT(q[0], q[4])` -> flips `q[4]` if `q[0]` is 1.
        *   `CNOT(q[1], q[4])` -> flips `q[4]` if `q[1]` is 1.
        *   `CNOT(q[3], q[4])` -> flips `q[4]` if `q[3]` is 1.
        *   Effectively, $q_4 \leftarrow q_4 \oplus q_0 \oplus q_1 \oplus q_3$.
        *   Since initially $q_4 = 0$ (for the Hadamard basis state, wait, $q_4$ is in $|+\rangle$, which is a superposition).
        *   Let's trace this in the Hadamard basis. An H gate before and after a CNOT can convert it into a CZ or another CNOT. Specifically, $H_{target} \cdot CNOT \cdot H_{target}$ is equivalent to `CNOT(target, control)` if we only apply H to target. Wait, H is applied to ALL qubits.
        *   Let's analyze $H^{\otimes 5} \cdot U_{par} \cdot H^{\otimes 5} |0^5\rangle$, where $U_{par}$ is the phase oracle (up to Hadamard basis) or just a unitary.
        *   Actually, let's look at the standard Bernstein-Vazirani or phase kickback.
        *   The CNOTs apply XOR to the target $q_4$: $q_4 \rightarrow q_4 \oplus q_0 \oplus q_1 \oplus q_3$.
        *   This is a linear transformation over GF(2).
        *   State before CNOTs: $\frac{1}{4\sqrt{2}} \sum_{x_0, x_1, x_2, x_3} |x_0\rangle |x_1\rangle |x_2\rangle |x_3\rangle \frac{1}{\sqrt{2}} (|0\rangle + |1\rangle)_4$.
        *   Applying CNOTs: $|x_0, x_1, x_2, x_3\rangle \frac{1}{\sqrt{2}}(|0 \oplus x_0 \oplus x_1 \oplus x_3\rangle + |1 \oplus x_0 \oplus x_1 \oplus x_3\rangle)_4$.
        *   Notice that this is exactly $|x_0, x_1, x_2, x_3\rangle \frac{1}{\sqrt{2}} (|y\rangle + |y \oplus 1\rangle) = |x_0, x_1, x_2, x_3\rangle \frac{1}{\sqrt{2}} (|0\rangle + |1\rangle)$, because $y = x_0 \oplus x_1 \oplus x_3$, and the sum over $y$ and $y\oplus 1$ is the same as $|0\rangle + |1\rangle$.
        *   Therefore, the state after the CNOTs is exactly the SAME as before!
        *   Wait, is this true?
        *   Let's re-verify: $\frac{1}{\sqrt{2}}(|y\rangle + |1 \oplus y\rangle)$ is indeed $\frac{1}{\sqrt{2}}

### Reference answer

{'predicted_probs': {'00000': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3064

- task_id: `isqTrain/3064`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_multi_register`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `4166`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```isq
import std;
qbit q[3];
// Initialize to |111>
procedure main() {
    X(q[0]);
    X(q[1]);
    X(q[2]);
    M(q[0]);
    M(q[0]);
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **The bug**: The second measurement operation `M(q[0])` incorrectly measures `q[0]` again instead of measuring `q[1]`. Because of this, `q[1]` is never measured.
2. **The fix**: Change the second `M(q[0])` to `M(q[1])` so that all three distinct qubits `q[0]`, `q[1]`, and `q[2]` are measured exactly once.
3. **State evolution**: The initial state of the system is $|000\rangle$. The three X gates flip each respective qubit from $|0\rangle$ to $|1\rangle$, resulting in the final quantum state $|111\rangle$. Measuring all three qubits in the computational basis yields the expected outcome $|111\rangle$ with a probability of 1.0.

## isqTrain/3910

- task_id: `isqTrain/3910`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `2045`

### Prompt

下面的量子程序运行结果不对，请帮我debug：

```
import std;
// QPE with 2-bit precision for phase 0
// Unitary: Rz(theta) with eigenvalue e^{i*theta/2} on |1>
qbit q[3];

procedure main() {
    // Prepare eigenstate |1> on target qubit
    X(q[2]);
    // Hadamard on precision qubits
    X(q[0]); H(q[1]);
    // Controlled unitary applications
    ctrl Rz(2.0 * 3.14159265358979 * 0.0 / 4.0 * 1.0, q[0], q[2]);
    ctrl Rz(2.0 * 3.14159265358979 * 0.0 / 4.0 * 2.0, q[1], q[2]);
    // Inverse QFT on precision register
    // For 2 qubits: SWAP, then H + controlled-Rz†
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    H(q[0]);
    ctrl Rz(-3.14159265358979 / 2.0, q[1], q[0]);
    H(q[1]);
    // Measure precision qubits
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

Let me analyze the buggy code and the fix.

The buggy code has:

The fixed code has:

So the bug is that `X(q[0])` should be `H(q[0])`.

In QPE (Quantum Phase Estimation), the precision qubits should be initialized with Hadamard gates to create superposition states |+⟩. The buggy code incorrectly applies an X gate to q[0] instead of H(q[0]).

Let me trace through the corrected circuit:

1. Initial state: |000⟩
2. X(q[2]): |001⟩ (q[2] is the target qubit, prepared as eigenstate |1⟩)
3. H(q[0]); H(q[1]): |+0⟩⊗|1⟩ = (|000⟩ + |010⟩ + |100⟩ + |110⟩)/2 ⊗ |1⟩... wait let me be more careful.

Actually, let me reconsider the qubit ordering. q[0] and q[1] are precision qubits, q[2] is the target.

After X(q[2]): |0⟩₀|0⟩₁|1⟩₂

After H(q[0]); H(q[1]): |+⟩₀|+⟩₁|1⟩₂ = (1/2)(|0⟩+|1⟩)₀(⊗)(|0⟩+|1⟩)₁|1⟩₂

Since the phase is 0, the controlled Rz gates don't add any phase (theta = 0 in both cases), so the state remains unchanged.

Then the inverse QFT is applied to the precision register. Since the phase is 0, we should measure |00⟩ on the precision qubits.

Wait, but The predicted output {|001⟩: 0.853553, |011⟩: 0.146447}. That means q[0] and q[1] should give some mixture... Hmm, that's strange for phase 0.

Let me reconsider. Maybe I'm misunderstanding the qubit indexing or the measurement ordering.

Actually, looking at the predicted output, |001⟩ has probability 0.853553 and |011⟩ has probability 0.146447. In the measurement bitstring, earlier measured qubits are higher bits. So if we measure q[0], q[1], q[2] in that order:
- q[0] is the highest bit
- q[1] is the middle bit  
- q[2] is the lowest bit

So |001⟩ means q[0]=0, q[1]=0, q[2]=1. And |011⟩ means q[0]=0, q[1]=1, q[2]=1.

Hmm, but for phase 0 with perfect QPE, we should get |00⟩ on the precision qubits with certainty. The fact that there's a non-zero probability of measuring |01⟩ is puzzling...

Wait, maybe the predicted output in the problem statement is wrong or I'm misunderstanding something. Or perhaps there's some noise or the Rz gate has a different definition.

Actually, let me re-read. The problem says "Expected measurement probabilities: {|001>: 0.853553, |011>: 0.146447}". These don't sum to 1, so maybe there are other outcomes too. But for phase 0, the ideal QPE should give |00⟩ on precision qubits.

Hmm, wait. 0.853553 ≈ (1 + 1/√2)/2 and 0.146447 ≈ (1 - 1/√2)/2. These are characteristic of some kind of interference pattern.

Actually, 0.853553 ≈ cos²(π/8) and 0.146447 ≈ sin²(π/8). Hmm.

Actually let me reconsider. Maybe there's something wrong with my understanding. Let me just focus on the bug analysis.

The bug is clear: `X(q[0])` should be `H(q[0])`. The QPE algorithm requires Hadamard gates on all precision qubits to create uniform superposition.

With X(q[0]) instead of H(q[0]), q[0] would be in state |1⟩ instead of |+⟩, which completely breaks the QPE algorithm.

With the fix H(q[0]), both precision qubits are in |+⟩ state, allowing proper phase estimation.

Since the phase is 0, all the controlled unitaries don't change anything (the rotation angle is 0), and the inverse QFT should return us to |00⟩ on the precision qubits.

But wait, The predicted output non-tr

## isqTrain/2940

- task_id: `isqTrain/2940`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_for_loop`, `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1149`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```isq
import std;
qbit q[5];
// Apply H to all 5 qubits (uniform superposition)
procedure main() {
    for i in 0:5 {
        H(q[i]);
    }
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: The final measurement `M(q[0])` is applied to the first qubit instead of the fifth qubit `q[4]`. This measures `q[0]` twice and leaves `q[4]` unmeasured.
2. **Fix**: Change the last measurement `M(q[0])` to `M(q[4])` so that all 5 qubits are measured exactly once.
3. **State evolution**: 
   - Initial state: |00000>
   - Apply `H` to all 5 qubits: creates a uniform superposition $\frac{1}{4\sqrt{2}} \sum_{x=0}^{31} |x\rangle$.
   - Measure all 5 qubits: the state collapses into one of the 32 possible basis states, each with a probability of $1/32 = 0.03125$.

## isqTrain/2918

- task_id: `isqTrain/2918`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_if_else`, `isq_syntax_procedures`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `2788`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
bool m1, m2;
qbit q_1, q_2, q_3;
procedure Teleport(qbit qsrc, qbit qanc, qbit qdest) {
    H(qanc);
    CNOT(qanc, qdest);
    CNOT(qsrc, qanc);
    H(qsrc);
    m1 = M(qsrc);
    m2 = M(qanc);
    if (m2) { X(qdest); }
    if (m1) { Z(qdest); }
}
procedure main() {
    Teleport(q_1, q_2, q_3);
    M(q_3);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Input:** isQ program implementing quantum teleportation with an initial state of $|000\rangle$. The qubits are $q_1$ (qsrc), $q_2$ (qanc), $q_3$ (qdest).
    *   **Target:** Step-by-step reasoning, state evolution using Dirac notation, and the predicted probability distribution.
    *   **Format Constraints:** Concise (3-15 lines), starting with "## Circuit Analysis", ending with the probability distribution, no code blocks.

2.  **Trace the Circuit (Teleportation of |0>):**
    *   Initial state: $|000\rangle$ (order: $q_1, q_2, q_3$). Actually, $q_1$ is source, $q_2$ is ancilla, $q_3$ is destination.
    *   `H(q_2)`: $|0\rangle_2 \to |+\rangle_2$. State is $|0\rangle_1 |+\rangle_2 |0\rangle_3$.
    *   `CNOT(q_2, q_3)`: Control $q_2$, target $q_3$. State becomes $|0\rangle_1 \left( \frac{1}{\sqrt{2}}|00\rangle_{23} + \frac{1}{\sqrt{2}}|11\rangle_{23} \right) = \frac{1}{\sqrt{2}}(|000\rangle + |011\rangle)$. This creates a Bell pair between $q_2$ and $q_3$.
    *   `CNOT(q_1, q_2)`: Control $q_1$, target $q_2$. Since $q_1 = |0\rangle$, state remains $\frac{1}{\sqrt{2}}(|000\rangle + |011\rangle)$.
    *   `H(q_1)`: $q_1$ is $|0\rangle$, becomes $|+\rangle$. State is $|+\rangle_1 \frac{1}{\sqrt{2}}(|0\rangle_2 |0\rangle_3 + |1\rangle_2 |1\rangle_3)$.
        $= \frac{1}{2} (|000\rangle + |100\rangle + |011\rangle + |111\rangle)$.
    *   Measure $q_1$ (`m1`) and $q_2$ (`m2`).
    *   Based on measurements ($m_1, m_2$), corrections are applied to $q_3$:
        *   If `m2` == 1, apply $X(q_3)$. This flips $q_3$.
        *   If `m1` == 1, apply $Z(q_3)$. This adds a phase, but since $q_3$ is always in $|0\rangle$ or $|1\rangle$ after $X$, $Z$ doesn't change the probabilities of measuring $|0\rangle$ vs $|1\rangle$ in a computational basis measurement.
        *   Actually, wait. Let's trace the exact outcomes.
            *   $00 \implies$ no corrections. $q_3$ is $|0\rangle$.
            *   $01 \implies X(q_3)$. $q_3$ was $|1\rangle$, becomes $|0\rangle$.
            *   $10 \implies Z(q_3)$. $q_3$ was $|0\rangle$, remains $|0\rangle$.
            *   $11 \implies X(q_3), Z(q_3)$. $q_3$ was $|1\rangle$, becomes $-|1\rangle$, then $Z$ makes it $|1\rangle$. Wait.
            Let's re-evaluate state after `H(q_1)`:
            State is $\frac{1}{2}(|00\rangle_{12}|0\rangle_3 + |10\rangle_{12}|0\rangle_3 + |01\rangle_{12}|1\rangle_3 + |11\rangle_{12}|1\rangle_3)$.
            Let's group by $m_1, m_2$:
            $|00\rangle \implies q_3 = |0\rangle$. Prob 1/4. Correct: none $\to q_3 = |0\rangle$.
            $|10\rangle \implies q_3 = |0\rangle$. Prob 1/4. Correct: $Z(q_3) \to q_3 = |0\rangle$.
            $|

### Reference answer

{'predicted_probs': {'000': 0.25, '011': 0.25, '100': 0.25, '111': 0.25}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqExpand/algo/49

- task_id: `isqExpand/algo/49`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `grover`, `3qubit`, `output_prediction`, `amplitude_amplification`
- source: `isq_expansion`
- dataset_index: `2668`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    ctrl ctrl Z(q[0], q[1], q[2]);
    H(q[0]); H(q[1]); H(q[2]);
    X(q[0]); X(q[1]); X(q[2]);
    ctrl ctrl Z(q[0], q[1], q[2]);
    X(q[0]); X(q[1]); X(q[2]);
    H(q[0]); H(q[1]); H(q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. H on all 3 qubits: uniform superposition (1/sqrt(8)) * sum|xyz>
2. ctrl @[q[0], q[1]] Z(q[2]): oracle for |111> — flips phase of |111>
3. H-X-CCZ-X-H: diffusion operator (2|s><s| - I)

This is 1 Grover iteration for target |111>.

For N=8, M=1 solution:
theta = arcsin(1/sqrt(8))
P(target) = sin^2(3*theta)

Computing: sin(theta) = 1/sqrt(8), cos(theta) = sqrt(7/8)
sin(3*theta) = 3*sin(theta) - 4*sin^3(theta) = 3/sqrt(8) - 4/(8*sqrt(8)) = 5/(2*sqrt(8))
P = 25/(4*8) = 25/32 = 0.78125

Non-target: (1 - 25/32)/7 = 7/(7*32) = 1/32 = 0.03125

### Reference answer

{'predicted_probs': {'000': 0.03125, '001': 0.03125, '010': 0.03125, '011': 0.03125, '100': 0.03125, '101': 0.03125, '110': 0.03125, '111': 0.78125}, 'explanation': "This is one iteration of Grover's algorithm on 3 qubits searching for |111>. The oracle is ctrl @[q[0], q[1]] Z(q[2]) (CCZ), which flips the phase of |111>. The diffusion operator is H-X-CCZ-X-H. After 1 iteration on N=8 states with M=1 solution, P(|111>) = sin^2(3*arcsin(1/sqrt(8))) = 25/32 = 0.78125, and each non-target state has P = (1 - 25/32)/7 = 1/32 = 0.03125."}

# ISQ training COT RAG corpus: quantum_algorithms shard 149

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3984

- task_id: `isqTrain/3984`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `3593`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```
import std;
// Inverse QFT on 3 qubits with input |100>
qbit q[3];

procedure main() {
    // Prepare input
    X(q[0]);

    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[2], q[0]);
    H(q[2]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[1]);
    ctrl Rz(-2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    H(q[0]);
    // Measure after inverse QFT
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

Let me analyze this bug carefully.

The task is a 3-qubit inverse QFT with input |100>.

Let me first understand what inverse QFT on 3 qubits should look like.

The QFT on 3 qubits transforms:
|j⟩ → (1/√8) Σ_k e^(2πijk/8) |k⟩

The inverse QFT does the reverse:
|k⟩ → (1/√8) Σ_j e^(-2πijk/8) |j⟩

But typically, the inverse QFT circuit is the reverse of the QFT circuit.

Standard QFT on 3 qubits (q[0], q[1], q[2]):
1. H(q[0]), then ctrl-Rz(π/4) from q[1] to q[0], then ctrl-Rz(π/8) from q[2] to q[0]
2. H(q[1]), then ctrl-Rz(π/4) from q[2] to q[1]
3. H(q[2])
4. Swap q[0] and q[2]

Inverse QFT would be the reverse:
1. Swap q[0] and q[2]
2. H(q[2])
3. ctrl-Rz(-π/4) from q[2] to q[1], then H(q[1])
4. ctrl-Rz(-π/8) from q[2] to q[0], ctrl-Rz(-π/4) from q[1] to q[0], then H(q[0])

Wait, but the input is |100⟩ which represents |4⟩ = |100⟩. Let me think about what the inverse QFT of |4⟩ should produce.

QFT|j⟩ = (1/√8) Σ_k ω^(jk) |k⟩ where ω = e^(2πi/8)

So inverse QFT|4⟩ = (1/√8) Σ_j ω^(-4j) |j⟩ = (1/√8) Σ_j (-1)^j |j⟩

Wait, ω^(-4j) = e^(-2πi·4j/8) = e^(-πij) = (-1)^j

So inverse QFT|4⟩ = (1/√8)(|0⟩ - |1⟩ + |2⟩ - |3⟩ + |4⟩ - |5⟩ + |6⟩ - |7⟩)

In terms of |q[2]q[1]q[0]⟩:
= (1/√8)(|000⟩ - |001⟩ + |010⟩ - |011⟩ + |100⟩ - |101⟩ + |110⟩ - |111⟩)

The measurement probabilities would all be 1/8 = 0.125, which matches the predicted output.

Now, the swap of q[0] and q[2] is done via 3 CNOTs. The standard way to swap two qubits a and b:
CNOT(a, b)  -- b gets a⊕b
CNOT(b, a)  -- a gets a⊕(a⊕b) = b
CNOT(a, b)  -- b gets b⊕(a⊕b) = a

So swap(q[0], q[2]) = CNOT(q[0], q[2]); CNOT(q[2], q[0]); CNOT(q[0], q[2])

The buggy code has:

The third CNOT has the qubits swapped - it should be CNOT(q[0], q[2]) not CNOT(q[2], q[0]).

Let me verify: with the fix, the swap is:
CNOT(q[0], q[2]): q[2] ← q[2] ⊕ q[0]
CNOT(q[2], q[0]): q[0] ← q[0] ⊕ q[2]  (where q[2] is now q[2]⊕q[0])
CNOT(q[0], q[2]): q[2] ← q[2] ⊕ q[0]  (where q[0] is now original q[2])

This correctly swaps q[0] and q[2].

With the bug, after CNOT(q[0], q[2]); CNOT(q[2], q[0]); CNOT(q[2], q[0]):
- After 1st: q[2] = q2⊕q0, q[0] = q0

## isqTrain/1379

- task_id: `isqTrain/1379`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1256`

### Prompt

用isQ实现the Deutsch algorithm for the constant function f(x)=0. Prepare ancilla in |-> state, put input in superposition, apply oracle, then Hadamard and measure.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Implement the Deutsch algorithm for constant function f(x)=0 to demonstrate that measurement outcome |0⟩ indicates a constant function.

**Qubits:** 2 qubits (q[0] input, anc[0] ancilla); only q[0] is measured.

**State evolution:**
1. Initial: |0⟩|0⟩
2. X(anc[0]): |0⟩|1⟩
3. H(anc[0]): |0⟩|−⟩ where |−⟩ = (|0⟩−|1⟩)/√2
4. H(q[0]): |+⟩|−⟩ = (|0⟩+|1⟩)|−⟩/√2
5. Oracle for f(x)=0: no operation needed; state unchanged since phase factor e^(2πi·0) = 1
6. H(q[0]): |0⟩|−⟩

**Expected probabilities:** Input qubit collapses to |0⟩ with probability 1.0, confirming f is constant (Deutsch: |0⟩ → constant, |1⟩ → balanced).

## isqTrain/3445

- task_id: `isqTrain/3445`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `hamiltonian_simulation`
- source: `isq_train_cot`
- dataset_index: `362`

### Prompt

Write an isQ program that single-layer QAOA for MaxCut on a 4-node cycle graph (edges: 0-1, 1-2, 2-3, 3-0) in isQ.

Use gamma=0.7, beta=0.35.
Declare 4 qubits, measure all.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for a single-layer QAOA circuit for MaxCut on a 4-node cycle graph with gamma=0.7 and beta=0.35.

Let me trace through the circuit:

1. Start with |0000>
2. Apply H to all qubits → |++++> = equal superposition of all 16 states
3. For each edge, apply ZZ rotation with angle gamma=0.7:
   - CNOT-Rz(0.7)-CNOT on edge (0,1): applies exp(-i*0.7*Z⊗Z/2) to qubits 0,1
   - CNOT-Rz(0.7)-CNOT on edge (1,2): applies exp(-i*0.7*Z⊗Z/2) to qubits 1,2
   - CNOT-Rz(0.7)-CNOT on edge (2,3): applies exp(-i*0.7*Z⊗Z/2) to qubits 2,3
   - CNOT-Rz(0.7)-CNOT on edge (3,0): applies exp(-i*0.7*Z⊗Z/2) to qubits 3,0

Wait, I need to be careful. The Rz(0.7) gate has matrix:
Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]

So the CNOT-Rz(θ)-CNOT sequence implements:
- When control is |0>: nothing happens
- When control is |1>: Rz(θ) is applied to target

This effectively applies a controlled-Rz, which is equivalent to exp(-i*θ/2 * Z⊗Z) up to some single-qubit rotations.

Actually, let me reconsider. The CNOT-Rz-CNOT sequence:
CNOT(q[0], q[1]); Rz(0.7, q[1]); CNOT(q[0], q[1]);

When both qubits are in |00> or |11> (same parity), after CNOT the target becomes |0>, Rz doesn't change it (phase-wise it does), then CNOT restores.
When qubits are in |01> or |10> (different parity), after CNOT the target becomes |1>, Rz applies phase, then CNOT restores.

Wait, let me think more carefully:
- |00>: after CNOT → |00>, Rz → e^(-i*0.35)|00>, CNOT → e^(-i*0.35)|00>
- |01>: after CNOT → |01>, Rz → e^(i*0.35)|01>, CNOT → e^(i*0.35)|01>
- |10>: after CNOT → |11>, Rz → e^(i*0.35)|11>, CNOT → e^(i*0.35)|10>
- |11>: after CNOT → |10>, Rz → e^(-i*0.35)|10>, CNOT → e^(-i*0.35)|11>

So states with different parities (|01>, |10>) get phase e^(i*0.35), states with same parity (|00>, |11>) get phase e^(-i*0.35).

This is exp(i*0.35*(Z⊗Z)) since Z⊗Z = +1 for |00>,|11> and -1 for |01>,|10>.
Actually: exp(-i*0.35) * exp(i*0.35*Z⊗Z) ... let me just say it applies phases based on ZZ.

4. Apply Rx(2*beta) = Rx(0.7) to all qubits (mixer layer)

Wait, in QAOA, the mixer is typically Rx(2*beta). The problem states beta=0.35, so 2*beta=0.7. The code uses Rx(0.7).

Let me verify the probabilities match:
- |0000> and |1111> have probability 0.249003 (these are "all same" states)
- |0011>, |0110>, |1001>, |1100> have probability 0.077235 (these are bipartite colorings - MaxCut solutions)
- States with odd parity like |0001>, etc. have lower probability

Wait, for MaxCut on a cycle graph with 4 nodes, the optimal solutions are the bipartite colorings: |0101>, |1010>, |0011>, |0110>, |1001>, |1100>.

Hmm, |0101> has probability 0.006225 which is very low, and |0011> has

## isqQA/quantum_algorithms/115_hardware_limitations

- task_id: `isqQA/quantum_algorithms/115_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hardware_limitations`, `algorithm`, `HHL中的受控旋转步骤`
- source: `qa_pipeline`
- dataset_index: `848`

### Prompt

在HHL算法中，受控旋转步骤用于提取矩阵特征值的倒数并将其编码到概率幅中，其基本数学形式通常涉及一系列针对辅助比特的受控旋转操作，旋转角度设定为θ_j=2arcsin(C/λ_j)。然而，在当前NISQ（含噪声中等规模量子）设备上实现这一过程时，极高的硬件门错误率和极短的退相干时间成为严重阻碍。请从退相干对旋转角度精度的破坏、辅助比特的误翻转概率进行深度理论分析，并说明在近期NISQ硬件的局限下，如何在isQ代码层面通过利用负控制逻辑来优化受控旋转线路的深度以缓解退相干效应？

### Reference answer

在HHL算法的执行流程中，受控旋转步骤是连接量子相位估计（QPE）与最终求解态生成的关键桥梁。在理想情况下，如果我们通过QPE成功提取到了特征值λ_j，系统将进入态|λ_j⟩|0⟩，随后我们施加受控旋转门，使得辅助比特的态矢量发生如下演化：|λ_j⟩|0⟩ → |λ_j⟩(√(1-(C/λ_j)^2)|0⟩ + (C/λ_j)|1⟩)。这意味着我们需要实现角度为θ_j=2arcsin(C/λ_j)的受控旋转。然而，在NISQ设备上，这一理论模型会遭受退相干效应的严重破坏。首先，相干时间T₂的局限性会导致严重的相位阻尼。由于实现精确的arcsin(C/λ_j)旋转需要将一系列基本旋转门（如受控Ry）组合，而多比特受控门在硬件上需分解为大量基础的CNOT和单比特门。随着特征值寄存器位数的增加，门序列的累积时间很容易超过T₂，导致旋转轴在布洛赫球面上发生不可预期的漂移。这使得实际执行的角度变为θ_j+δ，进而使得成功的概率幅从理论的C/λ_j退化为包含大量相位噪声的项，大幅降低了得到正确解的保真度。此外，能量弛豫时间T₁的影响同样致命。如果辅助比特在旋转过程中发生弛豫，原本应保持|0⟩或跃迁至|1⟩的演化过程会被打断，导致辅助比特提前坍缩。这不仅破坏了当前的受控旋转，更会导致后续的逆QPE无法正确解纠缠，最终输出混合噪声态，使得HHL算法完全失效。针对NISQ硬件的局限，优化受控旋转步骤的核心在于最大程度地缩短量子线路的深度。在硬件底层编译时，多控门通常需要引入大量的辅助比特或使用相对相位网络，这会产生诸多冗余的X门（NOT门）用于状态翻转。利用isQ语言提供的负控制逻辑，我们可以直接省去这些为了适配控制条件而添加的X门，从而降低线路深度。下面是一个在isQ中针对2比特特征值寄存器优化受控旋转的代码示例，该实现直接利用负控制减少了门的数量，从而在一定程度上缓解了退相干带来的负面影响：

```isq
import std;

qbit ancilla[1];
qbit eval_reg[2]; // 假设代表特征值的量子寄存器
// 针对不同的特征值基态，预先定义好角度所需的旋转矩阵
// 例如对应 C/lambda 的 Ry 门

deriving gate RY_lambda1 = [[0.866, -0.5], [0.5, 0.866]]; // 近似角度 pi/3
deriving gate RY_lambda2 = [[0.968, -0.25], [0.25, 0.968]]; // 近似角度 2*asin(0.25)

procedure main() {
    // 假设此时 eval_reg 已经通过前面的 QPE 步骤加载了特征值
    // 硬件优化策略：使用 nctrl (负控制) 消除传统多控门分解中繁杂的 X 门翻转
    // 如果对于特征值 |01> (即 eval_reg[1]=0, eval_reg[0]=1) 进行受控旋转
    // 传统做法需对 eval_reg[1] 加 X 门，再控制，再加 X 门恢复
    // isQ 的 nctrl 可以直接编译为底层更高效的相对相位网络，减少门深度对抗退相干

    nctrl @[eval_reg[1]] ctrl @[eval_reg[0]] RY_lambda1(ancilla[0]);

    // 如果对于特征值 |10> (即 eval_reg[1]=1, eval_reg[0]=0) 进行受控旋转
    nctrl @[eval_reg[0]] ctrl @[eval_reg[1]] RY_lambda2(ancilla[0]);

    // 对于更高位数的特征值寄存器，这种减少深度和复杂度的负控制优化尤为关键
}
```

通过上述利用isQ原生负控制语法的代码级优化，能够有效压缩受控旋转门在硬件上的实际执行时间，使其在退相干彻底破坏量子态之前尽可能完成演化，这是当前在NISQ阶段验证HHL算法可行性的重要工程手段。

## isqTrain/4024

- task_id: `isqTrain/4024`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `1409`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```
import std;
// 4-qubit Grover search targeting |1101>
qbit q[4];

// Oracle: mark target state |1101>
unit grover_oracle(qbit q[4]) {
    X(q[2]);
    ctrl<2> CZ(q[0], q[1], q[2], q[3]);
    X(q[2]);
} deriving gate

// Diffusion operator for 4 qubits
unit grover_diffusion(qbit q[4]) {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    X(q[3]);
    ctrl<2> CZ(q[0], q[1], q[2], q[3]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    X(q[3]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
} deriving gate

// Main: apply Grover iteration and measure
procedure main() {
    // Superposition on all 4 qubits
    // BUG: missing gate here
    // Grover iterations (3 iterations optimal for N=4)
    for i in 0:3 {
        grover_oracle(q);
        grover_diffusion(q);
    }
    // Measure all qubits
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The `main()` procedure is missing the Hadamard gates needed to initialize the uniform superposition. The comment `// BUG: missing gate here` appears where `H(q[0]); H(q[1]); H(q[2]); H(q[3]);` should be. Without these gates, all qubits remain in |0⟩, so Grover's algorithm has no superposition to search.

2. **Fix**: Add `H(q[0]); H(q[1]); H(q[2]); H(q[3]);` at the marked location in `main()`, before the Grover iterations begin.

3. **State evolution (corrected)**:
   - Start: |0000⟩
   - After H on all qubits: |ψ⟩ = (1/4)∑|x⟩ (uniform superposition over 16 states)
   - Oracle marks |1101⟩ by flipping its phase: X(q[2]) converts |1101⟩↔|1111⟩, the `ctrl<2> CZ` applies a phase to |1111⟩, then X(q[2]) restores. Result: phase of |1101⟩ is inverted.
   - Diffusion reflects all amplitudes about the mean, amplifying |1101⟩.
   - After 3 iterations: |1101⟩ amplitude ≈ 0.981, all others ≈ 0.049. Measurement gives |1101⟩ with probability ~0.963.

## isqTrain/3585

- task_id: `isqTrain/3585`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5800`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should Full adder: 1+0+1=10.

### Chain-of-thought reasoning

The user wants a bug analysis for a quantum computing program written in isQ.
The bug description is "Wrong CNOT direction".
The buggy code has `CNOT(q[1], q[0]);` while the corrected version has `CNOT(q[0], q[1]);`.
The circuit is a full adder: a=1, b=0, cin=1 -> sum=0, carry=1.
Qubits:
q[0] = a = 1
q[1] = b = 0
q[2] = cin = 1
q[3] = carry = 0

Wait, standard full adder:
Toffoli(a, b, carry) -> q[0], q[1], q[3]
CNOT(a, b) -> q[0], q[1]
Toffoli(b, cin, carry) -> q[1], q[2], q[3]
CNOT(b, cin) -> q[2], q[1]

Wait, the standard ripple carry adder computes:
Sum = a ^ b ^ cin
Carry = (a & b) | (cin & (a ^ b))

Let's trace standard full adder:
q[0]=a, q[1]=b, q[2]=cin, q[3]=0
Toffoli(q[0], q[1], q[3])  => q[3] = a & b
CNOT(q[0], q[1])           => q[1] = a ^ b
Toffoli(q[1], q[2], q[3])  => q[3] = (a ^ b) & cin + a & b = carry
CNOT(q[1], q[2])? Wait, no, in the code it's CNOT(q[2], q[1]) => q[1] = (a ^ b) ^ cin = sum.

Wait, in isQ `ctrl ctrl X(q[0], q[1], q[3])` is equivalent to Toffoli(q[0], q[1], q[3]).
Let's see the buggy code:
ctrl ctrl X(q[0], q[1], q[3]);
CNOT(q[1], q[0]); // Bug!
ctrl ctrl X(q[1], q[2], q[3]);
CNOT(q[2], q[1]);

Wait, if it's CNOT(q[0], q[1]):
ctrl ctrl X(q[0], q[1], q[3]);
CNOT(q[0], q[1]);
ctrl ctrl X(q[1], q[2], q[3]);
CNOT(q[2], q[1]);

Let's trace corrected code:
Init: q[0]=|1>, q[1]=|0>, q[2]=|1>, q[3]=|0>
After Toffoli(q[0], q[1], q[3]): q[3] becomes 1 & 0 = 0.
State: |1, 0, 1, 0>
After CNOT(q[0], q[1]): q[1] becomes 0 ^ 1 = 1.
State: |1, 1, 1, 0>
After Toffoli(q[1], q[2], q[3]): q[3] becomes 0 ^ (1 & 1) = 1.
State: |1, 1, 1, 1>
After CNOT(q[2], q[1]): q[1] becomes 1 ^ 1 = 0.
State: |1, 0, 1, 1>
This corresponds to:
q[0] = 1
q[1] = 0 (sum)
q[2] = 1 (cin)
q[3] = 1 (carry)
Measurement: q[0], q[1], q[2], q[3] -> 1, 0, 1, 1.
Bitstring (earlier measured qubit = higher bit): q[0] is highest, so 1011 in binary.
This perfectly matches expected measurement probabilities: {|1011>: 1.0}.

What about the buggy code?
Init: q[0]=|1>, q[1]=|0>, q[2]=|1>, q[3]=|0>
After Toffoli(q[0], q[1], q[3]): q[3] = 0.
After CNOT(q[1], q[0]): q[0] = 1 ^ 0 = 1.
After Toffoli(q[1], q[2], q[3]): q[3] = 0 ^ (0 & 1) = 0.
After CNOT(q[2], q[1]):

## isqExpand/qa/34

- task_id: `isqExpand/qa/34`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `量子并行性`, `量子叠加`, `阿达马门`, `量子干涉`, `状态空间`
- source: `qa_pipeline`
- dataset_index: `1877`

### Prompt

什么是量子并行性？它如何使得量子算法能够同时探索指数多的计算路径？

### Chain-of-thought reasoning

## 推理
1. **明确核心问题**：解释什么是量子并行性，并通过数学原理解释其为何能同时探索指数级路径。
2. **构建回答结构**：
    - **基本概念**：对比经典比特与量子比特，引入叠加态的概念。说明 $n$ 个量子比特可以表示 $2^n$ 种状态。
    - **数学推导**：使用标准的Dirac记号展示阿达马门如何将全 $|0\rangle$ 态转化为包含 $2^n$ 项的叠加态。进一步展示量子黑盒 $U_f$ 如何一次性作用于该叠加态，实现并行计算。
    - **补充关键细节（干涉）**：作为领域专家，必须指出仅靠并行性无法直接提取所有结果。需阐明量子测量坍缩的限制，并解释量子算法的真正优势在于“并行计算+干涉放大”。
    - **代码示例**：根据题目要求，使用规范的isQ语法编写一个生成3量子比特均匀叠加态的简单电路，将数学公式具象化。
3. **校验格式规范**：检查isQ代码规范（包含import std;、全局qbit声明、procedure main入口等），确保JSON格式正确且符合所有指令要求。

### Reference answer

量子并行性是量子计算中最核心且最反直觉的优势之一。简单来说，量子并行性是指一个量子系统由于量子叠加态的特性，能够同时处理大量计算状态的能力。

在经典计算机中，一个比特在某一时刻只能处于确定的状态 0 或 1。如果要计算一个函数 $f(x)$ 在 $N$ 个不同输入下的值，经典算法需要按顺序执行 $N$ 次计算。然而，在量子计算机中，一个量子比特可以同时处于 $|0\rangle$ 和 $|1\rangle$ 的叠加态。对于一个包含 $n$ 个量子比特的系统，它可以同时处于 $2^n$ 个基态的叠加态中。

数学上，我们可以通过阿达马门来展示这一过程。假设我们有一个包含 $n$ 个量子比特的寄存器，初始状态全部置为 $|0\rangle^{\otimes n}$。当我们对每个量子比特应用一个 $H$ 门时，系统的状态将演变为：

$$ |\psi\rangle = H^{\otimes n} |0\rangle^{\otimes n} = \frac{1}{\sqrt{2^n}} \sum_{x=0}^{2^n-1} |x\rangle $$

这个公式表明，仅通过 $n$ 个 $H$ 门的并行操作，我们就生成了一个包含 $2^n$ 个状态的均匀叠加态。假设我们有一个实现特定函数 $f(x)$ 的量子黑盒（酉算子） $U_f$。如果我们把上述叠加态作为输入，并在另一个初始为 $|0\rangle$ 的目标量子比特上应用 $U_f$，计算过程将如下所示：

$$ U_f \left( \frac{1}{\sqrt{2^n}} \sum_{x=0}^{2^n-1} |x\rangle |0\rangle \right) = \frac{1}{\sqrt{2^n}} \sum_{x=0}^{2^n-1} |x\rangle |f(x)\rangle $$

这就是量子并行性的精髓：$U_f$ 只被调用了一次，但它实际上同时对所有的 $2^n$ 个输入 $x$ 计算了函数值 $f(x)$。这意味着量子计算机能够在极少的操作步骤内，同时“探索”指数级数量的计算路径。

然而，这里有一个关键的物理限制：根据量子力学的测量公理，当我们对上述包含所有 $f(x)$ 结果的状态进行测量时，波函数会发生坍缩，我们只能随机地得到某一个确定的 $|x\rangle |f(x)\rangle$ 结果。因此，如果量子计算仅仅停留在产生叠加态并直接测量，它并不能为我们提供所有的计算答案。

所以，量子算法的真正威力并不单纯依赖于量子并行性，而是依赖于“量子并行性”与“量子干涉”的结合。像 Deutsch-Jozsa算法、Shor算法和 Grover算法 等著名的量子算法，都是在利用并行性同时评估所有可能的路径后，通过精心设计的量子电路（如逆量子傅里叶变换或Grover扩散算子），使得正确答案的概率振幅发生相长干涉被放大，而错误答案的振幅发生相消干涉被抵消。最终在测量时，我们才能以极高的概率获取我们需要的那条唯一结果。

为了更直观地理解并行状态的产生，以下是一段生成 3 个量子比特叠加态（包含 $2^3=8$ 条并行路径）的 isQ 代码示例：

import std;
qbit q[3];

procedure main() {
    // 初始状态默认为 |000>
    // 对每个量子比特应用H门，产生包含 2^3 = 8 个状态的均匀叠加态
    H(q[0]);
    H(q[1]);
    H(q[2]);
    
    // 此时系统的量子态为 1/sqrt(8) * (|000> + |001> + ... + |111>)
    // 若在此处引入其他量子门进行函数计算，将同时作用于这 8 条计算路径
    // ...后续通过干涉操作放大目标结果的概率振幅...
}

## isqTrain/2886

- task_id: `isqTrain/2886`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `measurement_order`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5168`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```isq
import std;
qbit q[5];
// Multi-controlled X with 4 controls
procedure main() {
    X(q[0]);
    X(q[1]);
    X(q[2]);
    X(q[3]);
    ctrl ctrl ctrl ctrl X(q[0], q[1], q[2], q[3], q[4]);
    M(q[0]);
    M(q[1]);
    M(q[0]);
    M(q[3]);
    M(q[4]);
}

```

### Chain-of-thought reasoning

## Bug Analysis

**Bug:** The third measurement statement reads `M(q[0])` instead of `M(q[2])`, measuring qubit 0 twice while qubit 2 is never measured.

**Fix:** Change `M(q[0])` (line 13) to `M(q[2])` so all five qubits are measured sequentially: q[0], q[1], q[2], q[3], q[4].

**State evolution (corrected):**
1. |00000⟩ — initial state
2. X(q[0..3]) → |11110⟩ — four control qubits set to |1⟩
3. ctrl⁴ X(q[0..3], q[4]) → |11111⟩ — target q[4] flips since all four controls are |1⟩
4. All measurements yield `1`, giving outcome 11111 with probability 1.0

## isqQA/quantum_algorithms/113_hardware_limitations

- task_id: `isqQA/quantum_algorithms/113_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `hardware_limitations`, `algorithm`, `QFT与经典FFT的对比`
- source: `qa_pipeline`
- dataset_index: `3581`

### Prompt

理论上量子傅里叶变换（QFT）相比于经典快速傅里叶变换（FFT）在处理大规模数据时具有指数级加速潜力，但为什么我们在当前的含噪中等规模量子（NISQ）设备上，却无法在实际应用中超越经典的FFT？请从NISQ设备的硬件连通性局限性、退相干对相位信息的破坏，以及量子态测量的物理限制等角度进行深入剖析，并给出一个4比特QFT核心结构的isQ代码示例，结合代码说明多量子比特门在当前硬件下的脆弱性。

### Reference answer

量子傅里叶变换（QFT）在理论上确实只需 O(log^2 N) 个量子门，而经典快速傅里叶变换（FFT）需要 O(N log N) 的操作。这种指数级加速在量子算法（如Shor算法）中至关重要，但在当前的含噪中等规模量子（NISQ）时代，其实际表现被硬件局限性严重制约。主要可以从以下三个维度来剖析：

1. 硬件连通性与门保真度的限制
在超导、离子阱等物理体系中，物理比特之间通常只存在有限的最近邻连通性。QFT的电路结构要求在任意两个比特之间执行受控相位旋转门。对于 N 个比特，第1个比特和第 N 个比特之间需要直接进行控制操作。在缺乏全连通性的硬件上，必须通过相邻比特不断执行 SWAP 操作来传递量子态。这不仅使电路深度急剧增加，而且两比特门（如 CNOT 或 CZ）的保真度目前通常在 99% 左右，远低于单比特门。大量受控门的级联会导致累积误差呈指数级增长，最终掩盖真实的计算结果。

2. 退相干对相位信息的致命破坏
QFT的数学核心在于利用量子门在概率幅之间构建复杂的干涉相位。然而，量子比特极易受到环境噪声的干扰而发生退相干。纵向弛豫（T1过程）会导致能量耗散，横向弛豫（T2过程）会直接破坏量子态的相位关系。由于QFT需要执行长深度的电路，当电路执行时间接近或超过系统的退相干时间时，量子态中携带的相位信息就会彻底丢失，转变为毫无意义的最大混合态。

3. 量子态测量的“信息瓶颈”
即便拥有完美的硬件，QFT也面临着“测量墙”的阻碍。经典FFT输出的是完整的频域复数数组，而如果在QFT结束后对量子寄存器进行全量测量，根据量子力学的投影定理，波函数会瞬间坍缩到某个基态上，你只能获得一次随机的采样结果。要想完整提取出全部 2^N 个概率幅和相位，理论上需要重复运行电路 O(2^N) 次。这完全抵消了QFT原本的加速优势。

为了更直观地理解这些物理限制，我们可以观察以下4比特QFT核心电路的isQ实现代码：

import std;
qbit q[4];

procedure main() {
    // 针对前4个比特执行量子傅里叶变换
    for i in 0:4 {
        H(q[i]);
        for j in (i+1):4 {
            // 这里的控制距离在真实硬件中是个严峻的考验
            // 例如当i=0, j=3时，控制比特q[3]和目标比特q[0]之间跨越了3个比特位
            // 真实硬件上必须插入额外的SWAP门网络才能实现这种非局域控制
            double angle = PI / (1 << (j - i));
            ctrl @[q[j]] Rz(angle, q[i]); 
        }
    }
}

在这段isQ代码中，内层循环的 ctrl @[q[j]] Rz(angle, q[i]); 是问题的症结所在。在 NISQ 设备上，当 j - i 较大时，不仅需要大量的底层 SWAP 操作，而且控制逻辑越复杂，电路对退相干时间的占用就越长。在当前门保真度和退相干时间的双重限制下，通常在执行到第3或第4个比特的控制旋转时，系统中的相位信息就已经被硬件噪声严重破坏，这也是目前 QFT 难以在真实物理机上超越经典 FFT 的根本原因。

## isqTrain/2860

- task_id: `isqTrain/2860`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `multi_controlled_logic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `199`

### Prompt

帮我写一个isQ程序：implements a 3-qubit GHZ state. Apply the appropriate gates to 3 qubits and measure all of them.

Requirements:
- Declare `qbit q[3];` at global scope.
- Use `procedure main()` as entry point.
- Measure all 3 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Create a 3-qubit GHZ state, the maximally entangled superposition (|000⟩ + |111⟩)/√2.
2. **Qubits:** 3 qubits (q[0], q[1], q[2]), all measured at the end.
3. **State evolution:**
   - |000⟩ → H(q[0]) → (|000⟩ + |100⟩)/√2
   - → CNOT(q[0], q[1]) → (|000⟩ + |110⟩)/√2
   - → CNOT(q[1], q[2]) → (|000⟩ + |111⟩)/√2
4. **Expected probabilities:** Each basis state has amplitude 1/√2, giving probability 0.5 for |000⟩ and 0.5 for |111⟩.

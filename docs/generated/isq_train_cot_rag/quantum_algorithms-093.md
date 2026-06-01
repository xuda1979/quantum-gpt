# ISQ training COT RAG corpus: quantum_algorithms shard 93

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/57

- task_id: `isqTrain/57`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3924`

### Prompt

用isQ实现implements a variant of the phase_kickback pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The task is to write an isQ program implementing a variant of the phase_kickback pattern using q[2] -> q[3]. But Analyzing the circuit requirements, it uses q[0] and q[1] with a 3-qubit register.

Wait, let me re-read. The prompt says "using q[2] -> q[3]" but the reference uses q[0] and q[1]. The circuit should qbit q[3] and uses q[0], q[1], q[2].

Looking at the predicted output: {|100>: 0.5, |110>: 0.5}

This means:
- Bit string ordering: earlier measured qubit = higher bit
- So |100> means q[0]=1, q[1]=0, q[2]=0
- |110> means q[0]=1, q[1]=1, q[2]=0

The phase kickback pattern:
1. Prepare target in |-> (X then H)
2. Prepare control in |+> (H)
3. Apply CNOT(control, target)
4. The phase gets kicked back to the control
5. H on control reveals the phase

Let me trace through:
- Initial: |000>
- After X(q[1]): |010>
- After H(q[1]): |0>(1/√2)(|0>-|1>) = (1/√2)(|000>-|010>) = (1/√2)|0>(|0>-|1>)|0>
  Actually let me be more careful with qubit ordering. q[0] is the first qubit, q[1] is the second.
  |q[0], q[1], q[2]>
  After X(q[1]): |0,1,0>
  After H(q[1]): |0>|->|0> = (1/√2)(|000> - |010>)

- After H(q[0]): (1/√2)(H|0>|0> - H|0>|1>)|0>
  H|0> = |+> = (1/√2)(|0>+|1>)
  = (1/√2)[(1/√2)(|0>+|1>)|0> - (1/√2)(|0>+|1>)|1>]|0>
  = (1/2)[(|00>+|10>-|01>-|11>)]|0>
  = (1/2)(|000>+|100>-|010>-|110>)

- CNOT(q[0], q[1]): control=q[0], target=q[1]
  |000> -> |000>
  |100> -> |110>
  |010> -> |010> (control is 0)
  |110> -> |100>
  
  So: (1/2)(|000>+|110>-|010>-|100>)

- H(q[0]):
  H|0>|0>|0> = |+>|0>|0> = (1/√2)(|0>+|1>)|0>|0> = (1/√2)(|000>+|100>)
  H|1>|1>|0> = |->|1>|0> = (1/√2)(|0>-|1>)|1>|0> = (1/√2)(|010>-|110>)
  H|0>|1>|0> = |+>|1>|0> = (1/√2)(|0>+|1>)|1>|0> = (1/√2)(|010>+|110>)
  H|1>|0>|0> = |->|0>|0> = (1/√2)(|0>-|1>)|0>|0> = (1/√2)(|000>-|100>)

  So: (1/2)[(1/√2)(|000>+|100>) + (1/√2)(|010>-|110>) - (1/√2)(|010>+|110>) - (1/√2)(|000>-|100>)]
  = (1/2√2)[|000>+|100>+|010>-|110>-|010>-|110>-|000>+|100>]
  = (1/2√2)[2|100> - 2|110>]
  = (1/√2)[|100>-|110>]
  = (1/√2)|1>(|0>-|1>)|0>

So the final state is (1/√2)(|100>-|110>), which gives:
- P(|100>) = 0.5
- P(|110>) = 0.5

This

## isqTrain/4111

- task_id: `isqTrain/4111`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1347`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[4];

procedure main() {
    X(q[0]);
    X(q[1]);

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

Initial state: |0000⟩

After X(q[0]) and X(q[1]): |1100⟩

Now let me identify the core operations. The sequence H followed by controlled-Rz operations looks like a Quantum Fourier Transform (QFT).

For QFT on 4 qubits, the pattern is:
- H(q[0]), CRz(π/2, q[1], q[0]), CRz(π/4, q[2], q[0]), CRz(π/8, q[3], q[0])
- H(q[1]), CRz(π/2, q[2], q[1]), CRz(π/4, q[3], q[1])
- H(q[2]), CRz(π/2, q[3], q[2])
- H(q[3])

Wait, let me check the Rz angles. The standard QFT uses controlled rotations where Rk = Rz(2π/2^k).

Looking at the circuit:
- ctrl Rz(2π/4, q[1], q[0]) = CRz(π/2, ...) which is R2
- ctrl Rz(2π/8, q[2], q[0]) = CRz(π/4, ...) which is R3
- ctrl Rz(2π/16, q[3], q[0]) = CRz(π/8, ...) which is R4

Yes, this is QFT! But wait, QFT typically uses controlled phase rotations, not Rz. Let me think more carefully.

Actually, the controlled-Rz gate: when control is |1⟩, it applies Rz(θ) to the target. So this is applying phase rotations conditioned on the control qubits.

Let me reconsider. In the standard QFT, we have:
- H on qubit j
- Then controlled rotations Rk = diag(1, exp(2πi/2^k)) from qubit j+k to qubit j

The controlled-Rz(θ) applies Rz(θ) = diag(exp(-iθ/2), exp(iθ/2)) to the target when control is |1⟩.

So when control is |1⟩, the |1⟩ component of the target gets phase exp(iθ/2) and |0⟩ gets exp(-iθ/2). This is Rz with a global phase.

Hmm, let me reconsider the QFT structure more carefully.

Actually, looking at this again: the controlled Rz gates have the *first* argument as the control and the second as the target? No, in isQ it's `ctrl Rz(theta, control, target)` based on the syntax... wait, let me re-read.

Looking at: `ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);`

The `ctrl` modifier makes the first qubit parameter the control. So q[1] is the control and q[0] is the target. The Rz rotation is applied to q[0] conditioned on q[1].

Wait, actually in isQ, `ctrl Rz(theta, q[1], q[0])` means: Rz(theta, q[0]) controlled by q[1]. So q[1] controls, q[0] is the target of the Rz.

So the QFT-like structure applies rotations to q[0] controlled by q[1], q[2], q[3], etc.

This is actually the inverse QFT (or QFT†), because in the standard QFT, the later qubits control the earlier ones' rotations.

Let me just track the state carefully.

Starting state: |1100⟩ (q[0]=1, q[1]=1, q[2]=0, q[3]=0)

Step 1: H(q[0])
|1⟩ → (|0⟩ - |1⟩)/√2
State: (|0100⟩ - |1100⟩)/√2

Wait, I need to be careful about the ordering. Let me use q[0]q[1]q[2]q[3] ordering.

State: (|0100⟩ - |1100⟩)/√2

Hmm wait, q[0] is the first qubit, q[1] is the second, etc.

|1100⟩ means q[0]=1, q[1]=1, q[2]=0, q[3]=0.

H(q[0]) on |1⟩: (|0⟩ - |1⟩)/√2

State: (|0100⟩ - |1100⟩)/√2

Step 2: ctrl Rz(π/2,

### Reference answer

Uniform distribution across 16 states

## isqTrain/319

- task_id: `isqTrain/319`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `entanglement`, `interference`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4199`

### Prompt

Create an isQ quantum circuit that implements a variant of the oracle_boolean pattern using a[1] -> a[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit has:
- qbit q[3] - 3 qubits initialized to |0>
- qbit a[3] - 3 qubits initialized to |0>

Main circuit:
1. X(a[0]) - flips a[0] to |1>
2. H(a[0]) - applies Hadamard to a[0]
3. H(q[0]), H(q[1]), H(q[2]) - applies Hadamard to all q qubits
4. my_oracle() - applies CNOT(q[0], a[0]) then CNOT(q[1], a[0])
5. H(q[0]), H(q[1]), H(q[2]) - applies Hadamard to all q qubits again
6. M(q[0]), M(q[1]), M(q[2]) - measures q qubits

Let me trace through the state evolution:

Initial state: |000>|000> (q[0]q[1]q[2] | a[0]a[1]a[2])

After X(a[0]): |000>|100>

After H(a[0]): |000> ⊗ (|0> - |1>)/√2 = |000>(|0> - |1>)/√2

After H(q[0]), H(q[1]), H(q[2]):
(|0>+|1>)/√2 ⊗ (|0>+|1>)/√2 ⊗ (|0>+|1>)/√2 ⊗ (|0>-|1>)/√2
= 1/2 (|000>+|001>+|010>+|011>+|100>+|101>+|110>+|111>) ⊗ (|0>-|1>)/√2

Now my_oracle():
- CNOT(q[0], a[0]): When q[0]=1, flip a[0]
- CNOT(q[1], a[0]): When q[1]=1, flip a[0]

The oracle applies parity f(q[0], q[1]) = q[0] ⊕ q[1] to a[0].

Since a[0] is in (|0>-|1>)/√2, the phase kickback gives us (-1)^(q[0]⊕q[1]) multiplied to each basis state.

So after oracle:
1/2[|000> - |001> - |010> + |011> + |100> - |101> - |110> + |111>] ⊗ (|0>-|1>)/√2

Wait, let me reconsider. The state is:
1/(2√2) Σ_{q0,q1,q2 ∈ {0,1}} |q0 q1 q2>(|0>-|1>)

After CNOT(q[0], a[0]) and CNOT(q[1], a[0]):
For each basis state |q0 q1 q2>, if q0⊕q1 = 1, the a[0] qubit gets flipped.

When we flip (|0>-|1>), it becomes (|1>-|0>) = -(|0>-|1>).

So states with q0⊕q1 = 1 get a phase of -1:
1/(2√2) [|000>(|0>-|1>) + |001>(|0>-|1>) - |010>(|0>-|1>) - |011>(|0>-|1>) - |100>(|0>-|1>) - |101>(|0>-|1>) + |110>(|0>-|1>) + |111>(|0>-|1>)]

Wait, I need to be more careful. Let me redo.

f(q0, q1) = q0 ⊕ q1

|000>: f=0 → no flip → (+)
|001>: f=0 → no flip → (+)
|010>: f=1 → flip → (-)
|011>: f=1 → flip → (-)
|100>: f=1 → flip → (-)
|101>: f=1 → flip → (-)
|110>: f=0 → no flip → (+)
|111>: f=0 → no flip → (+)

So the state after oracle is:
1/(2√2) [|000> + |001> - |010> - |011> - |100> - |101> + |110> + |111>] ⊗ (|0>-|1>)

Now apply H⊗3 to the q qubits:
The state is:
1/2 [|0>+|1>](|0>-|1>)(|0>+|1>) with appropriate signs

Actually let me think of it differently.

## isqTrain/4841

- task_id: `isqTrain/4841`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `quantum_counting`, `interference`
- source: `isq_train_cot`
- dataset_index: `2398`

### Prompt

Write an isQ program that implementing Grover for |11> on 3 qubits. The oracle uses X(q[2]) + Toffoli-like construction. Apply H to all 3 qubits, one Grover iteration, measure all.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement one iteration of Grover's algorithm on 3 qubits to amplify the probability of measuring |111⟩.

Three qubits q[0], q[1], q[2] are used and all are measured.

1. **Initialization**: H on all qubits creates |ψ₀⟩ = |+++⟩ = (1/√8)∑ₓ|x⟩, an equal superposition over all 8 basis states.

2. **Oracle (ctrl CZ)**: The triple-controlled Z gate flips the phase of |111⟩ only. State becomes |ψ₁⟩ = (1/√8)(|000⟩+|001⟩+|010⟩+|011⟩+|100⟩+|101⟩+|110⟩-|111⟩).

3. **Diffusion operator**: H⊗³ → X⊗³ → ctrl CZ → X⊗³ → H⊗³ reflects amplitudes about the mean. Mean amplitude = 6/(8√8). Non-target amplitudes reflect to 2(3/(8√8)) - 1/√8 = 1/(4√2). Target |111⟩ reflects to 2(3/(8√8)) + 1/√8 = 5/(4√2).

4. **Measurement probabilities**: |⟨x|ψ⟩|² gives |111⟩ probability

## isqExpand/algo/23

- task_id: `isqExpand/algo/23`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `quantum_walk`, `coin_operator`, `conditional_shift`
- source: `isq_expansion`
- dataset_index: `3905`

### Prompt

帮我写一个isQ程序：implementing a simple quantum walk on a cycle of 4 positions using 2 position qubits and 1 coin qubit. Apply 3 steps of the walk with a Hadamard coin, starting from position |00> with coin |0>.

### Chain-of-thought reasoning

## Reasoning
Goal: Discrete-time quantum walk on a 4-cycle with Hadamard coin.

Setup:
- coin: 1 qubit for direction (|0>=left, |1>=right)
- pos[0..1]: 2 qubits encoding position 0-3 on a cycle

Each step:
1. Coin: H(coin) — creates superposition of left/right
2. Shift: conditional increment/decrement of position
   - If coin=|1>: increment position mod 4
   - If coin=|0>: decrement position mod 4

After 3 steps from position 0, quantum interference creates a characteristic non-classical distribution. The exact probabilities depend on the coin operator and number of steps.

## isqExpand/qa/38

- task_id: `isqExpand/qa/38`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `Shor算法`, `连分数展开`, `量子相位估计`, `经典后处理`, `模幂运算`
- source: `qa_pipeline`
- dataset_index: `4108`

### Prompt

Shor算法中连分数展开（continued fraction expansion）如何从相位估计的结果中恢复周期？

### Chain-of-thought reasoning

## 推理
首先，分析问题核心：Shor算法中如何利用连分数展开从量子相位估计（QPE）的结果中恢复出周期。
1. **回顾Shor算法流程**：明确大数分解问题转化为求函数 $f(x)=a^x \bmod N$ 的周期 $r$。
2. **定位量子阶段输出**：QPE作用于幺正算符 $U|y\rangle = |ay \bmod N\rangle$。U的特征值是 $e^{2\pi i s/r}$。QPE通过逆量子傅里叶变换，测量得到整数 $m$，使得 $m/2^n$ 是 $s/r$ 的近似值。
3. **分析近似值的误差**：由QPE理论可知，$|s/r - m/2^n| \le 1/2^{n+1}$。
4. **引入连分数展开（CFE）**：解释连分数展开的作用——找到一个分母不超过特定大小的最佳有理逼近。列出连分数及其渐近分数的定义和递推公式。
5. **结合数学定理**：说明因为选取的量子比特数满足 $2^n > N^2$，根据最佳逼近定理，$s/r$ 必定是 $m/2^n$ 的某个渐近分数。
6. **总结恢复步骤**：列出从测量值提取周期的具体操作：得到$m$ -> 展开$m/2^n$计算渐近分数 -> 找分母小于$N$的候选$r$ -> 经典验证 $a^r \equiv 1$。
7. **补充代码示例**：为了丰富回答，结合isQ语言给出Shor算法中量子线路定义和受控模幂操作的基础代码框架，作为背景补充。

### Reference answer

在Shor算法中，求解大整数质因数分解的核心在于寻找函数 $f(x) = a^x mod N$ 的周期 $r$。量子相位估计（QPE）在此过程中的作用是高效地提取出与周期相关的相位信息，而连分数展开则是量子测量后必须经历的关键经典后处理步骤，用于从带有噪声的测量结果中恢复出真实的周期 $r$。

### 1. 相位估计的输出与目标
在Shor算法中，我们构造了幺正算符 $U|y\rangle = |ay \bmod N\rangle$。该算符的特征态正好是周期函数的傅里叶基（即态 $|u_s\rangle$），对应的特征值为 $e^{2\pi i \frac{s}{r}}$，其中 $0 \le s < r$ 是整数，$r$ 即为我们想要寻找的周期。

量子相位估计（QPE）线路使用 $n$ 个量子比特（通常 $n = 2\lceil \log_2 N \rceil$）来估计这个相位 $\phi = \frac{s}{r}$。理想情况下，对QPE的第一个寄存器进行测量，我们会得到一个整数 $m$，它满足：
$$ \frac{m}{2^n} \approx \frac{s}{r} $$
由于实际量子测量的分辨率有限，测量结果 $m$ 是相位 $\phi$ 的一个近似值，即 $m/2^n$ 通常不等于 $s/r$。我们的目标是利用已知的 $m$ 和 $2^n$，求出未知的互质分数 $s/r$。

### 2. 连分数展开的原理
连分数展开是一种将任意实数表示为嵌套分数的数学方法。给定一个有理数 $x = \frac{m}{2^n}$，它可以被唯一地展开为以下形式：
$$ x = a_0 + \frac{1}{a_1 + \frac{1}{a_2 + \dots}} $$
其中 $a_0$ 是整数，$a_1, a_2, \dots$ 是正整数。记为 $[a_0; a_1, a_2, \dots, a_k]$。

在展开过程中，我们可以逐步计算其“渐近分数”（convergents） $\frac{p_i}{q_i}$。渐近分数是通过截断连分数得到的分数，它们在分母不超过 $q_i$ 的所有分数中，是对 $x$ 的最佳有理逼近。渐近分数可以通过以下递推公式计算：
$$ p_i = a_i p_{i-1} + p_{i-2} $$
$$ q_i = a_i q_{i-1} + q_{i-2} $$
初始条件为 $p_{-2}=0, p_{-1}=1, q_{-2}=1, q_{-1}=0$。

### 3. 从相位估计结果恢复周期
根据量子相位估计的性质，测量结果 $m$ 以极高的概率满足以下不等式：
$$ \left| \frac{s}{r} - \frac{m}{2^n} \right| \le \frac{1}{2^{n+1}} $$
由于在Shor算法中我们选取了足够多的量子比特（$2^n > N^2$），且周期 $r < N$，数论中的一个定理保证了：如果一个分数 $s/r$ 满足 $r \le N$，且它与 $m/2^n$ 的误差小于 $1/(2N^2)$，那么 $s/r$ 必然是 $m/2^n$ 的某个渐近分数 $p_i/q_i$。

因此，Shor算法的经典后处理步骤如下：
1. **获得测量值**：从量子计算机读取寄存器状态，得到整数 $m$。
2. **计算连分数**：对 $x = m / 2^n$ 进行连分数展开，计算出所有的渐近分数 $\frac{p_0}{q_0}, \frac{p_1}{q_1}, \dots$。
3. **筛选分母**：检查每一个渐近分数 $p_i/q_i$。如果分母 $q_i > N$，则停止计算（因为真正的周期 $r$ 必须 $< N$）。取满足条件的最后一个渐近分数作为周期 $r$ 的候选值 $r_{candidate}$。
4. **经典验证**：计算 $a^{r_{candidate}} \bmod N$。如果结果为 $1$，则我们成功找到了周期 $r = r_{candidate}$。如果不为 $1$，可能是 $s$ 和 $r$ 有公因数，此时可以尝试 $r_{candidate}$ 的倍数或重新运行量子线路。

### 4. 代码示例背景
在具体的Shor算法量子程序（如使用isQ编程）中，模幂运算和量子相位估计构成了量子线路的核心。以下是一个简化的isQ模幂量子线路结构片段，展示了Shor算法中定义量子寄存器和进行受控幺正操作的部分：

```isq
import std;

qbit q1[8]; // 用于相位估计的控制寄存器
qbit q2[3]; // 存储模幂运算状态的工作寄存器

// 假设 U 是 a^x mod N 的实现
procedure U(int power) {
    // 根据power实现模幂操作
    // 此处省略具体的模加法器等底层门电路实现
}

procedure main() {
    // 初始化工作寄存器为 |1>
    X(q2[0]);
    
    // 初始化控制寄存器为等概率叠加态
    for i in [0:8] {
        H(q1[i]);
    }
    
    // 受控模幂操作
    for i in [0:8] {
        // 控制 @[q1[i]] 执行 U(2^i) 操作
        // ctrl @[q1[i]] U(2^i);
    }
    
    // 逆量子傅里叶变换
    // ... 测量得到整数 m，随后送入经典计算机进行连分数展开
}
```

总结而言，连分数展开在Shor算法中扮演了“桥梁”的角色，它将量子线路提取出的带有误差的相位浮点数信息，精确地映射回了代表周期的整数。这也体现了量子算法中量子计算与经典算法结合的典型范式。

## isqTrain/3898

- task_id: `isqTrain/3898`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_deriving_gate`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3995`

### Prompt

修复以下isQ程序中的错误：

```
import std;
// Swap test: compare |0> vs |0>
// q[0] = ancilla, q[1] = state A, q[2] = state B
qbit q[3];

// Controlled-SWAP (Fredkin gate)
unit cswap(qbit q[3]) {
    CNOT(q[1], q[2]);
    Toffoli(q[0], q[1], q[2]);
    CNOT(q[2], q[1]);
} deriving gate

procedure main() {
    // Prepare state A on q[1]
    // q[1] = |0> (default)
    // Prepare state B on q[2]
    // q[2] = |0> (default)
    // Swap test circuit
    H(q[0]);
    cswap(q);
    H(q[0]);
    // Measure ancilla and state qubits
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

## Bug Analysis
1. The bug is in the custom `cswap` gate's first CNOT operation, where the control and target qubits were incorrectly swapped as `CNOT(q[1], q[2])` instead of `CNOT(q[2], q[1])`, breaking the controlled-swap (three-CNOT decomposition) (controlled-swap (three-CNOT decomposition)) gate decomposition.
2. The fix swaps the arguments in the first CNOT gate to `CNOT(q[2], q[1])` so that the `cswap` unit correctly executes a controlled-swap operation (three-CNOT decomposition).
3. Corrected state evolution: Initial state |000> becomes (|000> + |100>)/√2 after the first H(q[0]). Because both compared qubits q[1] and q[2] remain |0>, the Cswap (three-CNOT decomposition) gate acts as an identity. The final H(q[0]) interferes the ancilla qubit constructively, resulting in the state |000>. Measurement yields |000> with 100% probability.

## isqTrain/3008

- task_id: `isqTrain/3008`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_multi_register`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5799`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```isq
import std;
qbit q[3];
// Double-H identity circuit on 3 qubits
procedure main() {
    H(q[0]);
    H(q[0]);
    H(q[1]);
    H(q[1]);
    H(q[2]);
    H(q[2]);
    M(q[0]);
    M(q[0]);
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **The Bug:** The second measurement operation incorrectly targets `q[0]` (`M(q[0])`) instead of `q[1]`. As a result, `q[1]` is never measured while `q[0]` is measured twice.
2. **The Fix:** Change the second `M(q[0])` to `M(q[1])` so that `q[0]`, `q[1]`, and `q[2]` are all measured exactly once.
3. **State Evolution:** The circuit initializes the state to `|000>`. Applying the Hadamard gate twice to any qubit acts as an identity operation ($H^2 = I$). Thus, the state remains `|000>`. Measuring all three qubits yields the deterministic result `|000>` with a probability of 1.0.

## isqTrain/2817

- task_id: `isqTrain/2817`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2344`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
oracle bool[4] g(bool a[4]) {
    bool res[] = [a[0], a[1], a[2], false];
    return res;
}
qbit q[4], res[4];

procedure main(){
    X(q[0]); 

    H(q);
    g(q, res);
    H(q); 
    print M(q);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants an analysis of an isQ quantum program, specifically predicting its measurement probability distribution and explaining the steps. The output must follow specific formatting rules.

2.  **Analyze the isQ code:**
    *   `import std;`
    *   `oracle bool[4] g(bool a[4]) { bool res[] = [a[0], a[1], a[2], false]; return res; }`
        *   This is an oracle. In isQ, an oracle acts as a unitary. Since it maps boolean arrays to boolean arrays, it effectively computes a classical function.
        *   Wait, the syntax `g(q, res)` implies this oracle is applied to `q` and `res`. But `res` is a separate quantum register.
        *   Let's re-read isQ oracle syntax. `oracle bool[4] g(bool a[4])` takes 4 boolean inputs. `g(q, res)` passes `q` (4 qubits) and `res` (4 qubits). Wait, the oracle signature only has `bool a[4]`. Why are there two registers `q` and `res`?
        *   Ah, if the oracle returns `res`, and is called with `g(q, res)`, it typically computes `res = res XOR g(q)`? Or does it replace `res`? Usually, an oracle acts on a state $|x\rangle|y\rangle \rightarrow |x\rangle|y \oplus f(x)\rangle$.
        *   Wait, `q` and `res` are global. `res` is initialized to $|0000\rangle$.
        *   Wait, is `res` ever measured? `print M(q)` only measures `q`.
        *   Let's look at the circuit structure:
            1. `X(q[0])` -> state of `q` is `|1000>`
            2. `H(q)` -> state of `q` is `H|0> \otimes H|0> \otimes H|0> \otimes H|1> = |-> \otimes |+> \otimes |+> \otimes |+>`.
               Wait, `q[0]` was flipped, so it's $|1\rangle$. After `H`, it's $|-\rangle$.
               So $q$ is in $|-\rangle_0 \otimes |+\rangle_1 \otimes |+\rangle_2 \otimes |+\rangle_3$.
            3. `g(q, res)` is an oracle. Wait! The definition `bool res[] = [a[0], a[1], a[2], false];` returns an array of 4 booleans. The signature `oracle bool[4] g(bool a[4])` only takes `a`. If called as `g(q, res)`, is it doing a phase oracle or a classical copy? If `res` is the target for the output, it might entangle `q` and `res`.
            4. However, wait. Does `g(q, res)` entangle them? If `res` starts as $|0000\rangle$, and we compute $|x\rangle|0\rangle \rightarrow |x\rangle|g(x)\rangle$, then `q` and `res` become entangled.
            5. Wait, if `res` is not measured, tracing it out or looking at the `q` subsystem might yield a mixed state if they are entangled!
            6. Let's look at the provided circuit implementation: `{'0000': 0.125, '0001': 0.125, '0010': 0.125, '0011': 0.125, '0100': 0.125, '0101': 0.125, '0110': 0.125, '0111': 0.125}`.
            7. The states are all states where the most significant bit (q[0]) is 0!
            8. Wait. `|0000>` to `|0111>` have `q[0]` = 0.
            9. Why? Let's trace the state.
               * `q` init: $|0000\rangle$
               * `X(q[0])`: $|1000\rangle$
               * `H(q)`: $\frac{1}{4} \sum_{x} (-1)^{x_0} |x\rangle$ where $x_0$ is the 0th bit.
               * `g(q, res)` -> Wait! If `g(q, res)` applies $U_g |x\rangle|0\rangle

### Reference answer

{'predicted_probs': {'0000': 0.125, '0001': 0.125, '0010': 0.125, '0011': 0.125, '0100': 0.125, '0101': 0.125, '0110': 0.125, '0111': 0.125}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/1375

- task_id: `isqTrain/1375`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4187`

### Prompt

I need an isQ program to Grover's algorithm on 2 qubits to search for the state |10>. Use a single Grover iteration (which gives certainty for 2 qubits).

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Generate a concise step-by-step reasoning for a given isQ quantum program (Grover's algorithm for 2 qubits searching for |10>).
    *   **circuit implementation provided:** Yes (but I should only generate the reasoning, not the code).
    *   **Expected probabilities:** {|10>: 1.0}.
    *   **Number of qubits:** 2.
    *   **Constraints:** Output ONLY the reasoning section starting with "## Reasoning". No isQ code. Use Dirac notation. Be concise (3-8 lines for simple, up to 15 for complex).

2.  **Trace the Quantum State Evolution:**
    *   *Goal:* Implement Grover's algorithm on 2 qubits to find |10>.
    *   *Initial state:* $|00\rangle$.
    *   *Hadamards:* $H(q_0)H(q_1) \rightarrow \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
    *   *Oracle for |10>:* Needs to flip the phase of $|10\rangle$. Using $X(q_1)$, $CZ(q_0, q_1)$, $X(q_1)$.
        *   $X(q_1)$ maps $|10\rangle \rightarrow |11\rangle$.
        *   $CZ$ flips the phase of $|11\rangle \rightarrow -|11\rangle$.
        *   $X(q_1)$ maps it back $\rightarrow -|10\rangle$.
        *   State becomes $\frac{1}{2}(|00\rangle + |01\rangle - |10\rangle + |11\rangle)$.
    *   *Diffusion Operator:* $H^{\otimes 2} X^{\otimes 2} CZ X^{\otimes 2} H^{\otimes 2}$.
        *   $H^{\otimes 2}$ maps the uniform superposition $\frac{1}{2}\sum |x\rangle$ to $|00\rangle$ and the marked state $-|10\rangle$ (minus uniform) to $-|11\rangle$ (wait, let's trace exactly).
        *   Let's trace $H^{\otimes 2}$ on $\frac{1}{2}(|00\rangle + |01\rangle - |10\rangle + |11\rangle)$:
            *   $H$ on $q_1$ of $\frac{1}{2}(|0\rangle(|0\rangle+|1\rangle) + |1\rangle(-|0\rangle+|1\rangle))$ is unchanged? No.
            *   Wait, easier trace: Diffusion inverts about the mean.
            *   Mean amplitude is $\frac{1}{4}(1+1-1+1) = \frac{1}{2}$.
            *   Amplitudes become $2(\frac{1}{2}) - A_x$: $1 \rightarrow 0$, $1 \rightarrow 0$, $-1 \rightarrow 2(1/2)-(-1) = 2$, $1 \rightarrow 0$.
            *   So state becomes $2 \times \frac{1}{2}|10\rangle = |10\rangle$.
    *   *Verification:* Yes, 1 iteration gives certainty for 2 qubits. Final state is exactly $|10\rangle$. Measurement yields |10> with probability 1.

3.  **Draft the Reasoning:**
    *   Goal: Grover's search on 2 qubits to find target state |10>.
    *   Start with $|00\rangle$, apply H to both to get $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
    *   Apply oracle using X(q[1]), CZ(q[0], q[1]), X(q[1]), which flips the phase of |10> to yield $\frac{1}{2}(|00\rangle + |01\rangle - |10\rangle + |11\rangle)$.
    *   Apply the diffusion operator (H, X, CZ, X, H on both qubits) to invert amplitudes about the mean.
    *   The mean amplitude is $1/4$; inversion maps amplitudes $(1/2, 1/2, -1/2, 1/2)$ to $(0, 0, 1, 0)$.
    *   The final state is exactly $|10\rangle$, so measuring both qubits yields '10' with a probability of 1.0.

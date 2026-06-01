# ISQ training COT RAG corpus: quantum_algorithms shard 144

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3552

- task_id: `isqTrain/3552`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2805`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should Half adder: 1+0=1.

### Chain-of-thought reasoning

## Bug Analysis

1. **The bug** is on the line `CNOT(q[1], q[0])` — the control and target are swapped. This stores the XOR result into `q[0]` instead of `q[1]`, violating the intended output mapping where `q[1]` should hold the sum.

2. **The fix** changes `CNOT(q[1], q[0])` to `CNOT(q[0], q[1])`, making `q[0]` the control and `q[1]` the target so that `q[1]` = a XOR b (the sum).

3. **State evolution (corrected):**
   - Initial: |000⟩
   - X(q[0]): |100⟩ (a=1, b=0)
   - Toffoli(q[0],q[1],q[2]): |100⟩ (carry=0 since b=0)
   - CNOT(q[0],q[1]): |110⟩ (q[1] flipped to 1, since q[0]=|1⟩; sum = 1⊕0 = 1)
   - Final: |110⟩ → q[0]=1, q[1]=sum=1, q[2]=carry=0 ✓ (1+0=1, carry=0)

## isqTrain/3548

- task_id: `isqTrain/3548`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `data_encoding_qml`, `phase_manipulation`, `hamiltonian_simulation`
- source: `isq_train_cot`
- dataset_index: `870`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should IQP encoding layer: 3 qubits.

### Chain-of-thought reasoning

## Bug Analysis

1. **What the bug is**: In the pair (0,1) ZZ entangling section, the first CNOT has reversed arguments: `CNOT(q[1], q[0])` instead of `CNOT(q[0], q[1])`. For a proper IQP ZZ interaction, both CNOTs must share the same control and target (CNOT(c,t) → Rz(θ, t) → CNOT(c,t)), which implements a controlled-phase gate. Mismatched directions produce incorrect entangling behavior.

2. **What the fix is**: Change the first CNOT in the (0,1) pair from `CNOT(q[1], q[0])` to `CNOT(q[0], q[1])`, matching the second CNOT. The other two pairs (0,2) and (1,2) are already correct.

3. **State evolution of corrected circuit**:
   - Start: |000⟩
   - After H⊗3: |+⟩|+⟩|+⟩ = (1/2√2) Σ|x⟩ for all x∈{0,1}³
   - Each corrected ZZ block (CNOT→Rz→CNOT) applies a diagonal phase rotation in the computational basis. Pair (0,1) applies Rz(0.5) conditioned on q[0] to q[1]; pairs (0,2) and (1,2) similarly.
   - The single-qubit Rz(0.4) rotations add further diagonal phases.
   - Since all gates in the ZZ layer and Rz layer are diagonal in the computational basis, measurement probabilities are unchanged from the Hadamard layer: all 8 outcomes remain at 1/8 = 0.125, matching predicted output {|000⟩: 0.125, ..., |111⟩: 0.125}.

## isqExpand/algo/154

- task_id: `isqExpand/algo/154`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `shor_algorithm`, `quantum_phase_estimation`, `order_finding`, `modular_exponentiation`, `inverse_QFT`, `continued_fractions`
- source: `isq_expansion_qa`
- dataset_index: `903`

### Prompt

解释Shor算法分解N=15的过程：选择a=7，如何通过量子相位估计找到周期r？

### Chain-of-thought reasoning

首先验证经典部分：a=7与N=15互素（gcd=1）。手动计算7的幂次模15：7^1=7, 7^2=49=4·15+4→4, 7^3=4·7=28=1·15+13→13, 7^4=13·7=91=6·15+1→1，确认周期r=4。QPE过程的关键在于U_a的本征值为exp(2πis/4)，逆QFT后测量第一寄存器得到接近s/4×2^t的值，通过连分数展开恢复分母4即周期。最后验证r=4为偶数且7^(r/2)=49≢-1(mod 15)，满足分解条件，得到gcd(48,15)=3和gcd(50,15)=5，完成分解。

### Reference answer

Shor算法分解N=15、选取a=7的完整过程如下：

**第一步：经典预处理**
选取a=7，验证gcd(7,15)=1，满足互素条件。需找最小正整数r使得7^r ≡ 1 (mod 15)。

**第二步：量子求阶——量子相位估计（QPE）核心**

1. **寄存器初始化**：使用两个量子寄存器。第一寄存器（计数寄存器）t个量子比特初始化为|0⟩^⊗t（t的选取需满足2^t > N^2 ≈ 225，故通常取t=8），第二寄存器n=⌈log₂15⌉=4个量子比特初始化为|1⟩。

2. **叠加态制备**：对第一寄存器的每个量子比特施加Hadamard门，得到均匀叠加态 (1/√2^t) Σ|x⟩|1⟩，x从0到2^t-1。

3. **受控模幂运算**：定义幺正算符U_a|y⟩ = |a·y mod 15⟩。对第一寄存器中第j个量子比特执行受控U^(2^j)操作。即：
   |x⟩|1⟩ → |x⟩|7^x mod 15⟩
   由于7^r mod 15的周期r=4（经典验证：7¹≡7, 7²≡4, 7³≡13, 7⁴≡1 mod 15），函数值序列为{1,7,4,13,1,7,4,13,...}。

4. **逆量子傅里叶变换（IQFT）**：对第一寄存器施加逆QFT。关键数学原理：由于U的本征值为exp(2πi·s/4)（s=0,1,2,3），QPE将第一寄存器投影到接近|⌊2^t·s/4⌋⟩的态。具体而言，测量结果会集中在以下值附近（以t=8为例）：
   - s=0 → 测量≈0
   - s=1 → 测量≈64
   - s=2 → 测量≈128
   - s=3 → 测量≈192

5. **测量与经典后处理**：测量第一寄存器得到值m，计算分数m/2^t，用连分数展开逼近s/r。例如测得m=64，则64/256=1/4，连分数算法直接给出分母r=4。

**第三步：经典验证与因式分解**
得到周期r=4（偶数），计算：
- 7^(r/2) - 1 = 7² - 1 = 48
- 7^(r/2) + 1 = 7² + 1 = 50
- gcd(48, 15) = 3
- gcd(50, 15) = 5

因此15 = 3 × 5，分解成功。

**量子电路规模**：实际实现中，模乘法器7x mod 15可简化为：由于7 mod 15的乘法在4比特空间中仅涉及置换操作（无进位），电路仅需少量CNOT和Toffoli门即可实现，这是N=15案例相对简单的原因。

## isqTrain/930

- task_id: `isqTrain/930`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2243`

### Prompt

用isQ实现implements the boolean_synthesis pattern. Include explicit identity operations in the circuit (H-H pair before M(q[5])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Synthesize the majority function MAJ(a,b,c) = (a∧b)∨(a∧c)∨(b∧c) for inputs a=1, b=1, c=0, using XOR decomposition with an explicit H-H identity pair.

**Qubits:** 6 allocated (q[0]-q[5]); q[5] measured.

**State evolution:**
1. |000000⟩ — X(q[0]),

## isqTrain/4127

- task_id: `isqTrain/4127`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `3557`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[3];

procedure main() {
    X(q[2]);
    H(q[0]); H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 * 2.0 / 4.0 * 1.0, q[0], q[2]);
    ctrl Rz(2.0 * 3.14159265358979 * 2.0 / 4.0 * 2.0, q[1], q[2]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    H(q[0]);
    ctrl Rz(-3.14159265358979 / 2.0, q[1], q[0]);
    H(q[1]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

The circuit performs a Quantum Fourier Transform (QFT) followed by its inverse (IQFT), modulo some additional operations or a slight variation.
Let's trace the state of qubits $q_0, q_1, q_2$.
Initial state: $|000\rangle$

Gate operations:
1. `X(q[2])` -> $|001\rangle$ (qubits are $q_2 q_1 q_0$, wait, let's stick to the standard order: $q_2 q_1 q_0$, no, isQ is usually $q_0$ is LSB or $q_0$ is MSB. Let's just use $q_2 q_1 q_0$). Wait, `ctrl Rz` is on $q_0, q_2$.
Let's represent the state as $|q_2 q_1 q_0\rangle$.
Initial state: $|000\rangle$.
`X(q[2])`: state becomes $|100\rangle$.

2. `H(q[0]); H(q[1]);`
State becomes $H_1 H_0 |100\rangle = |1\rangle \otimes |+\rangle \otimes |+\rangle = |1\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle+|1\rangle) \otimes \frac{1}{\sqrt{2}}(|0\rangle+|1\rangle) = \frac{1}{2}(|100\rangle + |101\rangle + |110\rangle + |111\rangle)$.

3. `ctrl Rz(2.0 * pi * 2.0 / 4.0 * 1.0, q[0], q[2]);`
This applies $R_z(\pi)$ (which is a phase of -1 up to global phase, wait: $R_z(\theta) |1\rangle = e^{-i\theta/2}|1\rangle$. Actually, $R_z(\pi) = Z$ up to global phase.
$\theta_1 = \pi$. $R_z(\pi)$ controlled by $q_0$ on target $q_2$.
If $q_0=1$, $q_2$ gets $R_z(\pi)$.
Wait, is it $R_z(\theta)$ or something else? In isQ, `ctrl Rz` applies $R_z$ on target if control is 1.
Let's evaluate the angles carefully:
`2.0 * pi * 2.0 / 4.0 * 1.0 = pi`
$R_z(\pi)$ applies a phase of $e^{-i\pi/2} = -i$ to $|1\rangle$ and $e^{i\pi/2} = i$ to $|0\rangle$.
Actually, $R_z(\pi) = e^{-i\pi Z/2} = \cos(\pi/2)I - i\sin(\pi/2)Z = -iZ$.
So $R_z(\pi)|1\rangle = i|1\rangle$ and $R_z(\pi)|0\rangle = -i|0\rangle$.
Wait, a controlled-$R_z$ gate applies $R_z(\theta)$ to the target qubit. If the target is in $|1\rangle$, it gets phase $e^{-i\pi/2} = -i$. If target is $|0\rangle$, it gets $e^{i\pi/2} = i$.
Wait! The target is $q_2$. The state of $q_2$ is $|1\rangle$.
So $|1\rangle \xrightarrow{R_z(\pi)} e^{-i\pi/2}|1\rangle = -i|1\rangle$.
So the state becomes:
$\frac{1}{2}(|100\rangle - i|101\rangle + |110\rangle - i|111\rangle)$.
Wait, what if the gate is `ctrl Rz`? In isQ, `ctrl Rz(theta, control, target)` is a controlled gate. The first qubit is control, the second is target.
So $q_0$ is control, $q_2$ is target.
For $|100\rangle$, $q_0=0$, so nothing happens.
For $|101\rangle$, $q_0=1$, $q_2=1$, so $q_2$ gets $e^{-i\theta/2} = e^{-i\pi/2} = -i$.
Thus, $|101\rangle \to -i|101\rangle$.
For $|110\rangle$, $q_0=0$, nothing happens.
For $

### Reference answer

Dominant output states: |101> with probability ~0.85 each

## isqTrain/763

- task_id: `isqTrain/763`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3107`

### Prompt

请用isQ语言编写一个量子电路：implements the weighted_adder pattern. Include explicit identity operations in the circuit (X-X pair before M(q[2])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

The user wants me to explain a weighted_adder pattern in isQ that includes an X-X pair (identity) before measuring q[2].

Let me trace through this circuit:

1. Initial state: |0000⟩ (4 qubits)

2. X(q[0]): flips q[0] → |1000⟩

3. X(q[1]): flips q[1] → |1100⟩

4. CNOT(q[0], q[2]): control=q[0]=1, so flip q[2] → |1110⟩... wait, let me think about the bit ordering.

Actually, let me be more careful with the notation. Let's say q[0] is the rightmost bit:
- |0000⟩ initially (q[3]q[2]q[1]q[0])

Actually, I'll use |q[3]q[2]q[1]q[0]⟩ notation.

Initial: |0000⟩

X(q[0]): |0001⟩
X(q[1]): |0011⟩
CNOT(q[0], q[2]): q[0]=1, so flip q[2] → |1011⟩
CNOT(q[1], q[3]): q[1]=1, so flip q[3] → |1111⟩
X(q[2]): flip q[2] → |1011⟩
X(q[2]): flip q[2] again → |1111⟩

So the X-X pair cancels out, and the final state is |1111⟩.

We measure q[2] and q[3]:
- q[3] = 1, q[2] = 1

The output bitstring is |11⟩ with probability 1.0.

Wait, but in the --probs output, earlier measured qubit = higher bit. So if we measure q[2] first, then q[3]:
- The bitstring would be q[3]q[2]... no wait.

"earlier measured qubit = higher bit" - so M(q[2]) comes first, meaning q[2] is the higher bit, and M(q[3]) is the lower bit.

So the measurement bitstring is |q[2]q[3]⟩... no wait, "earlier measured qubit = higher bit" means:
- q[2] measured first → higher bit position
- q[3] measured second → lower bit position

So the bitstring is |q[2]q[3]⟩ where q[2] is the MSB.

q[2] = 1, q[3] = 1, so we get |11⟩ with probability 1.0.

Wait, but that doesn't seem right. Let me re-read: "earlier measured qubit = higher bit"

So if M(q[2]) is first, q[2] is the higher bit. If M(q[3]) is second, q[3] is the lower bit.

Result bitstring = q[2] * 2^1 + q[3] * 2^0... no wait, higher bit means higher position.

Actually, "higher bit" in a bitstring like |10⟩ means the '1' is the higher bit (MSB). So if q[2] is measured first, q[2] corresponds to the MSB.

|q[2]q[3]⟩ where q[2] is left (MSB) and q[3] is right (LSB).

q[2] = 1, q[3] = 1 → |11⟩

That matches the predicted output.

Now let me write the reasoning:

## Reasoning

1. **Goal**: Implement a weighted adder that computes weighted sum bits with an explicit X-X cancellation pair.

2. **Qubits**: 4 qubits (q[0..3]); inputs q[0], q[1] and sum bits q[2], q[3]; only q[2] and q[3] are measured.

3. **State evolution**:
   - |0000⟩ → X(q[0]),X(q[1]) → |0011⟩ (inputs set to 1,1)
   - CNOT(q[0],q[2]): q[0]=1 flips q[2] → |0111⟩... 

Hmm, I need to be more careful about notation. Let me use |q[3]q[2]q[1]q[0]⟩:

- Initial: |0000⟩
- X(q[0]): |0001⟩
- X(q[1]): |0011⟩
- CNOT(q[0],q[2]): control q[0]=1, flip q[2] → |0111⟩
-

## isqExpand/algo/6

- task_id: `isqExpand/algo/6`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `deutsch_jozsa`, `bernstein_vazirani`, `comparison`
- source: `qa_pipeline`
- dataset_index: `455`

### Prompt

Deutsch-Jozsa算法和Bernstein-Vazirani算法有什么区别？它们各自解决什么问题？

### Chain-of-thought reasoning

## 推理
目标：对比两个算法的问题、加速和原理。

DJ算法：判定问题，指数加速，利用干涉区分常数/平衡。
BV算法：搜索问题，线性加速，利用相位回踢找隐藏字符串。

共同点：都用H-Oracle-H结构。
区别：问题类型、函数限制、加速程度不同。

### Reference answer

## Deutsch-Jozsa算法

**问题**：给定一个布尔函数 f: {0,1}^n -> {0,1}，判断它是常数函数（对所有输入输出相同）还是平衡函数（恰好一半输入输出0，一半输出1）。

**经典**：最坏需要 2^(n-1)+1 次查询
**量子**：1次查询即可确定

**原理**：利用量子并行性同时评估所有输入，通过干涉使常数函数输出|0...0>，平衡函数输出非|0...0>。

## Bernstein-Vazirani算法

**问题**：给定 f(x) = s·x (mod 2)，其中 s 是未知的 n-bit 字符串，找到 s。

**经典**：需要 n 次查询（每次确定 s 的一个比特）
**量子**：1次查询即可找到完整的 s

**原理**：利用相位回踢（phase kickback），H^n 将相位编码的 s 转换回计算基。

## 关键区别

| | Deutsch-Jozsa | Bernstein-Vazirani |
|--|--|--|
| 问题类型 | 判定问题（是/否） | 搜索问题（找到s） |
| 函数限制 | 常数或平衡 | 线性函数 f(x)=s·x |
| 加速类型 | 指数（2^n → 1） | 线性（n → 1） |
| Oracle类型 | 通用布尔函数 | 内积Oracle |

两者都使用 H→Oracle→H 的基本框架（称为Hadamard夹心结构），是理解量子优势的入门算法。

## isqTrain/1345

- task_id: `isqTrain/1345`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4002`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[5];

procedure main() {

    X(q[3]); H(q[3]);

    H(q[0]); H(q[1]); H(q[2]);

    CNOT(q[0], q[3]);
    CNOT(q[2], q[3]);

    H(q[0]); H(q[1]); H(q[2]);

    M(q[0]); M(q[1]); M(q[2]); M(q[4]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Output prediction for an isQ program.
    *   Format: "## Circuit Analysis" followed by step-by-step reasoning, using Dirac notation, ending with the predicted probability distribution.
    *   Constraints: Concise (3-8 lines for simple, up to 15 for complex), no code blocks, ONLY the analysis text.
    *   Input program:
        
    *   Target probabilities: {|1010>: 1.0} (Wait, let's trace the bits carefully. q0, q1, q2, q4 are measured. q0=1, q1=0, q2=1, q4=0? Let's verify).

2.  **Trace the Circuit:**
    *   Initial state: $|00000\rangle$
    *   $X(q[3]) \to |00010\rangle$
    *   $H(q[3]) \to |000\rangle \otimes |-\rangle \otimes |0\rangle$ where $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
    *   $H(q[0])H(q[1])H(q[2]) \to |+++\rangle \otimes |-\rangle \otimes |0\rangle$. Let's denote this as $|+\rangle^{\otimes 3}|-\rangle|0\rangle$.
    *   $CNOT(q[0], q[3])$: Control is $|+\rangle$, target is $|-\rangle$.
        *   $CNOT |+\rangle |-\rangle = \frac{1}{2} (|0\rangle+|1\rangle)(|0\rangle-|1\rangle) = \frac{1}{2} (|00\rangle - |01\rangle + |10\rangle - |11\rangle)$.
        *   Apply CNOT: $|00\rangle \to |00\rangle$, $|01\rangle \to |01\rangle$, $|10\rangle \to |11\rangle$, $|11\rangle \to |10\rangle$.
        *   Result: $\frac{1}{2} (|00\rangle - |01\rangle + |11\rangle - |10\rangle) = \frac{1}{2} (|0\rangle - |1\rangle)(|0\rangle - |1\rangle) = |-\rangle |-\rangle$.
        *   Wait, phase kickback for CNOT on $|+\rangle |-\rangle$ gives $- |-\rangle |-\rangle$. Let's re-evaluate:
        *   $CNOT |+\rangle |-\rangle = CNOT \frac{1}{2}(|0\rangle+|1\rangle)(|0\rangle-|1\rangle) = \frac{1}{2} (|00\rangle - |01\rangle + |11\rangle - |10\rangle) = \frac{1}{2}(|0\rangle - |1\rangle)(|0\rangle - |1\rangle) = |-\rangle |-\rangle$. There is no minus sign here! Wait. Let's check $CNOT |+\rangle |1\rangle$.
        *   $|-\rangle = H|1\rangle = \frac{1}{\sqrt{2}}|0\rangle - \frac{1}{\sqrt{2}}|1\rangle$.
        *   If target is $|1\rangle$, $CNOT |+\rangle |1\rangle = |-\rangle |1\rangle$. No, that's wrong. $CNOT(|+\rangle|1\rangle) = CNOT \frac{1}{\sqrt{2}}(|01\rangle + |11\rangle) = \frac{1}{\sqrt{2}}(|01\rangle + |10\rangle) = \frac{1}{\sqrt{2}}(|0\rangle|1\rangle + |1\rangle|0\rangle)$. This is a Bell state.
        *   Let's stick to the math: $CNOT

### Reference answer

{'predicted_probs': {'10': 1.0}, 'explanation': 'Parametric variant of isqEval/491. Dimension: qubit_variant: q[4] -> q[5].'}

## isqTrain/2566

- task_id: `isqTrain/2566`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `global_phase`, `isq_syntax_arrays`, `isq_syntax_procedures`, `phase_manipulation`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `645`

### Prompt

这两个isQ程序是等价的吗？

程序A：
```isq
import std;

qbit q[2];

procedure my_oracle() {
    X(q[0]);
    CZ(q[0], q[1]);
    X(q[0]);
}

procedure diffuser() {
    H(q[0]); H(q[1]);
    X(q[0]); X(q[1]);
    CZ(q[0], q[1]);
    X(q[0]); X(q[1]);
    H(q[0]); H(q[1]);
}

procedure main() {
    H(q[0]); H(q[1]);
    my_oracle();
    diffuser();
    M(q[0]); M(q[1]);
}

```

程序B：
```isq
import std;

qbit q[2];

procedure my_oracle() {
    X(q[0]);
    CZ(q[0], q[1]);
    X(q[0]);
}

procedure diffuser() {
    H(q[0]); H(q[1]);
    X(q[0]); X(q[1]);
    CZ(q[0], q[1]);
    X(q[0]); X(q[1]);
    H(q[0]); H(q[1]);
}

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    H(q[0]); H(q[1]);
    my_oracle();
    diffuser();
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze Program A**:
    *   Initializes a 2-qubit register `q[2]` in `|00>`.
    *   Applies `H` to both: state becomes `|++> = 0.5(|00> + |01> + |10> + |11>)`.
    *   Applies `my_oracle()`: `X(q[0])`, `CZ(q[0], q[1])`, `X(q[0])`.
        *   `X(q[0])` swaps the amplitude of `|00>` with `|10>`, and `|01>` with `|11>`. State is now `0.5(|10> + |11> + |00> + |01>)`.
        *   `CZ(q[0], q[1])` flips the phase of `|11>`. State is `0.5(|10> - |11> + |00> + |01>)`.
        *   `X(q[0])` swaps amplitudes back. State is `0.5(|00> - |01> + |10> + |11>)`.
        *   Wait, let's trace exactly:
            Initial: `1/2 (|00> + |01> + |10> + |11>)`.
            Apply `X(q[0])`: `1/2 (|10> + |11> + |00> + |01>)`.
            Apply `CZ(q[0], q[1])`: phase flips where `q[0]=1, q[1]=1`. So `|11>` gets a minus sign. State: `1/2 (|10> - |11> + |00> + |01>)`.
            Apply `X(q[0])`: State: `1/2 (|00> - |01> + |10> + |11>)`.
            This is equivalent to applying `CZ` but with `q[1]` as control and `q[0]` as target... Wait, no. `CZ` is symmetric. `X(q[0]) CZ(q[0],q[1]) X(q[0])` is a controlled-Z gate with `q[1]` as the control and `q[0]` as the target? No, CZ is symmetric, so `X CZ X` just applies Z to `q[0]` when `q[1]` is `|1>`. Actually, it's equivalent to `CZ(q[0], q[1])`. Wait, let's look closely:
            `CZ` applies a `-1` phase when both are 1.
            Wait, no. `X` conjugates the control? If we do `X` on control of `CNOT`, it's like control is on `|0>`. For `CZ`, `X1 CZ12 X1` applies `-1` when `q[1]` is 1 and `q[0]` is 0, OR when `q[1]` is 1 and `q[0]` is 1?
            Let's do matrix math. `X \otimes I` `CZ` `X \otimes I` = `X CZ X`.
            CZ has `-1` at `(11, 11)`.
            `X CZ X` swaps rows/cols 0 and 1 for qubit 0.
            So the `-1` moves from `(11, 11)` to `(01, 01)`.
            So the `-1` applies when `q[0]=0, q[1]=1`.
            My state trace: `1/2(|00> - |01> + |10> + |11>)`. Indeed, `|01>` has a `-1`.
    *   Applies `diffuser()`: `H2 X2 CZ X2 H2`.
        *   For 2 qubits, `diffuser` is `H X CZ X H`.
        *   `H X H` = `Z`.
        *   So `diffuser` is `Z \otimes Z` conjugated by `CZ`? No.
        *   Let's evaluate the state: `|psi> = 1/2(|00> - |01> + |10> + |11>)`.
        *   Let's represent it in standard basis. Amplitudes: `a_00 = 1/2`, `a_01 = -1/2`, `a_10 = 1/2`, `a_11 = 1/2`.
        *   Notice that this oracle marks the `|01>` state.
        *   The diffuser for Grover's algorithm reflects the state about the mean of the amplitudes.
        *   Mean of

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/911

- task_id: `isqTrain/911`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`
- source: `isq_train_cot`
- dataset_index: `5137`

### Prompt

I need an isQ program to implements a variant of the bit_flip_oracle pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Step 1: Analyze the request.
- Goal: Write an isQ program implementing a variant of the `bit_flip_oracle` pattern.
- Specifics: The oracle pattern should be `q[2] -> q[3]`, using an expanded qubit register compared to the base version.
- circuit implementation provided: It uses an oracle `bool[1] f(bool x[2])` computing `x[0] && x[1]` applied to `q` and `ancilla`.
- predicted output: `|1101>` with probability 1.0. Wait, The predicted output `|1101>`. 4 qubits are measured. `1101` means:
    - `ancilla` is 1 (wait, bitstring order: earlier measured = higher bit).
    - Let's trace the reference:
      `M(q[0]); M(q[1]); M(q[2]); M(ancilla[0]);`
      Output is `1101`. Let's check bits:
      `q[0]` = 1, `q[1]` = 1, `q[2]` = 0, `ancilla[0]` = 1.
      The circuit should `qbit q[3]` but only initializes `q[0]` and `q[1]` to 1. `q[2]` is left as 0.
      Wait, the prompt says "implements a variant of the bit_flip_oracle pattern using q[2] -> q[3]".
      If the prompt specifically asks for `q[2] -> q[3]`, this likely means the target qubit for the oracle (the bit flip) is `q[3]`, and the controls are something else, or maybe it just asks for a generalized oracle using a 4-qubit register?
      Let's re-read the prompt very carefully: "Write an isQ program that implements a variant of the bit_flip_oracle pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version."
      Actually, the bit_flip_oracle typically marks an item by flipping an ancilla. If it's "using q[2] -> q[3]", maybe `q[3]` is the target/ancilla, and `q[2]` is involved?
      Let's look at The implementation:
      `qbit q[3]; qbit ancilla[1];` -> 4 qubits total. `q[0]`, `q[1]`, `q[2]`, `ancilla[0]`.
      Wait, if The implementation is what I must output, I just need to adapt it to strictly follow the naming `q[2] -> q[3]` if needed, but wait, the reference has `q[3]`? No, `qbit q[3]` means `q[0], q[1], q[2]`.
      Maybe the prompt implies `qbit q[4]`?
      Let's rethink. I am asked to *generate reasoning* for the task. I am NOT writing the code. The prompt for me says "Generate a reasoning section that explains...". So I just write the reasoning!
      Let's analyze the provided circuit implementation to write the reasoning for it, since The implementation is the "expected" output.
      circuit implementation:
      4 qubits. `q[0], q[1], q[2]`, `ancilla[0]` (let's call it `q[3]`? No, The implementation measures `ancilla[0]`).
      Wait, I need to generate the reasoning for the *user's prompt* "Write an isQ program that implements a variant of the bit_flip_oracle pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version."
      If the target program uses `q[2] -> q[3]`, that means a Toffoli or controlled gate where `q[2]` is control and `q[3]` is target? No, "bit_flip_oracle pattern using q[2] -> q[3]" might mean the oracle operates on `q[2]` to `q[3]`.
      Let's look at The implementation closely.
      `oracle bool[1] f(bool x[2]) { bool res[] = [x[0] && x[1]]; return res; }`
      Wait, in isQ, `f(q, ancilla)` applies the oracle. If it takes `bool x[2]`, it uses `q[0]` and `q[1]` as controls, and `ancilla[0]` as target.
      Why does the prompt say "using q

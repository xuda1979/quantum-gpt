# ISQ training COT RAG corpus: quantum_algorithms shard 138

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4057

- task_id: `isqTrain/4057`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `348`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```
import std;
// Grover search on 3 qubits targeting |111>, 2 iterations
qbit q[3];

// Oracle: mark target state |111>
unit grover_oracle(qbit q[3]) {
    ctrl CZ(q[0], q[1], q[2]);
} deriving gate

// Diffusion operator
unit grover_diffusion(qbit q[3]) {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    X(q[0]);
    // BUG: missing gate here
    X(q[2]);
    ctrl CZ(q[0], q[1], q[2]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
} deriving gate

// Main: 2 Grover iterations for higher success probability
procedure main() {
    // Initialize superposition
    H(q[0]); H(q[1]); H(q[2]);
    // Iteration 1
    grover_oracle(q);
    grover_diffusion(q);
    // Iteration 2
    grover_oracle(q);
    grover_diffusion(q);
    // Measure
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug identification**: In `grover_diffusion()`, the gate `X(q[1])` is missing between `X(q[0])` and `X(q[2])`. The diffusion operator requires applying X to **all** qubits to convert |000⟩ to |111⟩ before the controlled-Z. Without X(q[1]), the transformation is incomplete.

2. **Fix**: Add `X(q[1])` after `X(q[0])` and before `X(q[2])`, completing the sequence: H⊗3 → X⊗3 → double-controlled-Z (ctrl @[c1, c2] Z(target)) → X⊗3 → H⊗3.

3. **State evolution (corrected)**:
   - After initialization: |+⟩⊗3 = (1/√8) Σ|x⟩
   - Oracle marks |111⟩ with a phase flip → (1/√8)(Σ|x≠111⟩ − |111⟩)
   - Diffusion (H X double-controlled-Z (ctrl @[c1, c2] Z(target)) X H) amplifies |111⟩ amplitude: H maps |s⟩→|0⟩, X maps |0⟩→|1⟩, double-controlled-Z (ctrl @[c1, c2] Z(target)) flips phase of |111⟩, then X and H revert — equivalent to 2|s⟩⟨s|−I
   - Iteration 1: |111⟩ amplitude ≈ 0.53 → prob ≈ 0.28
   - Iteration 2: |111⟩ amplitude ≈ 0.97 → prob ≈ 0.945
   - Expected measurement: {|111⟩: 0.9453125, others: 0.0078125 each}

## isqTrain/3079

- task_id: `isqTrain/3079`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_multi_register`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `4685`

### Prompt

Something is wrong with this isQ circuit. Identify the error and provide the corrected code.

```isq
import std;
qbit q[4];
// Initialize to |1111>
procedure main() {
    X(q[0]);
    X(q[1]);
    X(q[2]);
    // X(q[3]); // BUG: missing initialization
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. The bug is a missing `X` gate on `q[3]`. While `q[0]`, `q[1]`, and `q[2]` are initialized to $|1\rangle$ using the Pauli-X (bit-flip) gate, `q[3]` is left in its default initial state of $|0\rangle$, resulting in the system state $|1110\rangle$ instead of the intended $|1111\rangle$.
2. The fix is to apply the `X` gate to `q[3]` so that all qubits in the register are flipped to $|1\rangle$.
3. State evolution of the corrected circuit: The circuit starts in the initial $|0000\rangle$ state. Applying the $X$ gate to all four qubits transforms the state to $X \otimes X \otimes X \otimes X |0000\rangle = |1111\rangle$. This ensures that measurements will deterministically yield the target bitstring.

## isqTrain/3894

- task_id: `isqTrain/3894`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4113`

### Prompt

Something is wrong with this isQ circuit. Identify the error and provide the corrected code.

```
import std;
// QFT on 3 qubits with input state |100>
qbit q[3];

procedure main() {
    // Prepare input state |100>
    X(q[0]);

    // QFT stage for qubit 0
    H(q[0]);
    ctrl Rz(2.0 * 2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    // QFT stage for qubit 1
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    // QFT stage for qubit 2
    H(q[2]);
    // Swap q[0] and q[2]
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    // Measure after QFT
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

## Bug Analysis

1. **The bug** is in the line `ctrl Rz(2.0 * 2.0 * 3.14159265358979 / 4.0, q[1], q[0]);` — there's an extra `2.0 *` multiplication that makes the rotation angle `π` instead of the correct `π/2` (i.e., `2π/4`).

2. **The fix** changes `2.0 * 2.0 * 3.14159265358979 / 4.0` to `2.0 * 3.14159265358979 / 4.0`, correcting the controlled rotation from q[1] to q[0] to use angle `2π/2² = π/2`.

3. **State evolution (corrected)**:
   - Start: |000⟩ → X(q[0]) → |100⟩
   - QFT stage 0: H(q[0]) → 1/√2(|000⟩ + |100⟩); then CRz(π/2) with q[1] control on q[0] adds phase only when both are |1⟩; then CRz(π/4) with q[2] control on q[0]
   - QFT stage 1: H(q[1]) → CRz(π/2) with q[2] control on q[1]
   - QFT stage 2: H(q[2])
   - Swap q[0]↔q[2] to reverse qubit order
   - Result: QFT|100⟩ = QFT|4⟩ = 1/√8 Σ_y e^(2πi·4y/8)|y⟩ = 1/√8(|0⟩-|1⟩+|2⟩-|3⟩+|4⟩-|5⟩+|6⟩-|7⟩)

## isqTrain/4377

- task_id: `isqTrain/4377`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `2608`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;

qbit q[4];

procedure main() {
    // Eigenstate |1> of T gate
    X(q[3]);
    // Counting register in superposition
    H(q[0]);
    H(q[1]);
    H(q[2]);
    // Controlled powers of T
    // T^1 controlled by q[2]
    ctrl T(q[2], q[3]);
    // T^2 = S controlled by q[1]
    ctrl S(q[1], q[3]);
    // T^4 = Z controlled by q[0]
    ctrl Z(q[0], q[3]);
    // Inverse QFT on counting register
    // SWAP q[0] and q[2]
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    // QFT dagger
    H(q[0]);
    ctrl Rz(-3.14159265358979 / 2, q[0], q[1]);
    H(q[1]);
    ctrl Rz(-3.14159265358979 / 4, q[0], q[2]);
    ctrl Rz(-3.14159265358979 / 2, q[1], q[2]);
    H(q[2]);
    // Measure counting register
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

The isQ program is implementing Quantum Phase Estimation (QPE) on the T gate using 3 counting qubits.
q[0], q[1], q[2] are counting qubits.
q[3] is the eigenstate register.

Initial state: |0000>

1. X(q[3]) -> |0001>
2. H(q[0]), H(q[1]), H(q[2]) -> 1/sqrt(8) (|000> + |001> + |010> + |011> + |100> + |101> + |110> + |111>) |1>
Wait, ordering: q[0] is MSB or LSB? Standard isQ assumes q[0] is the lowest index. Let's use standard binary order. Let's write (|0> + |1>)^3 |1> / sqrt(8).
Actually, let's see. Qubit q[0] is q[2] swapped with.
Let's trace:
ctrl T(q[2], q[3]) -> applies T if q[2]=1
ctrl S(q[1], q[3]) -> applies S if q[1]=1
ctrl Z(q[0], q[3]) -> applies Z if q[0]=1
Wait, T has eigenvalue exp(i pi / 4).
The phase is $\phi = 1/8$.
The applied phase on q[i] is $T^{2^i} = e^{i 2^i \pi / 4}$.
So the state is $1/\sqrt{8} \sum_{x=0}^7 e^{2\pi i x \phi} |x>|1>$, where $\phi = 1/8$.
Wait, T gate eigenvalue is exp(i pi / 4).
Phase shift on |1> is pi/4.
So $\phi = 1/8$.
The state is $1/\sqrt{8} \sum_{x=0}^7 e^{2\pi i x / 8} |x>|1>$
Wait, for x=0, phase 0.
x=1, phase pi/4.
x=2, phase pi/2.
x=3, phase 3pi/4.
...
x=7, phase 7pi/4.
This is exactly $1/\sqrt{8} \sum_{x=0}^7 e^{2\pi i x / 8} |x>|1>$.
Wait, the order of qubits matters. The QPE applies $U^{2^i}$ controlled by q[i].
In the code:
ctrl T(q[2], q[3]) -> applies T if q[2]=1. (T^1)
ctrl S(q[1], q[3]) -> applies S if q[1]=1. (T^2)
ctrl Z(q[0], q[3]) -> applies Z if q[0]=1. (T^4)
So q[2] corresponds to the least significant bit!
Let $x = 4q[0] + 2q[1] + q[2]$.
The phase is $2\pi x / 8$.
This state is exactly the QFT of |1>|1>.
So Inverse QFT on the counting register should yield |100> (which is q[0]=1, q[1]=0, q[2]=0).
Wait, |100> means q[0]=1, q[1]=0, q[2]=0.
Let's see the Inverse QFT code:
swap (three-CNOT decomposition) q[0] and q[2]: this reverses the order of qubits, so q[2] becomes MSB and q[0] becomes LSB.
After swap (three-CNOT decomposition), the counting register is in the QFT of |001> (since q[2] was LSB, it becomes MSB, so it's |100> reversed -> wait.
If state is $\sum e^{2\pi i x / 8} |q_0 q_1 q_2\rangle$ with $q_0$ MSB, then applying inverse QFT on $q_0 q_1 q_2$ yields $|100\rangle$.
But here, $q_0$ was applied $U^4$, so it corresponds to the phase $4 \times \frac{1}{8} = 1/2$, which is MSB in standard QFT.
So the state before swap (three-CNOT decomposition) is $\sum e^{2\pi i x/8} |q_0 q_1 q_2\rangle$, with $x = 4q_0 + 2q_1 + q_2$.
If we apply inverse QFT directly, we would get $|100\rangle$ (q[

### Reference answer

{'predicted_probs': {'0000': 0.021447, '0001': 0.125, '0101': 0.426777, '0110': 0.213388, '0111': 0.213388}, 'explanation': 'This isQ program operates on 4 qubit(s). The measurement probability distribution is: P(|0000>) = 0.0214, P(|0001>) = 0.1250, P(|0101>) = 0.4268, P(|0110>) = 0.2134, P(|0111>) = 0.2134.'}

## isqQA/quantum_algorithms/93_principle_advantage

- task_id: `isqQA/quantum_algorithms/93_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `principle_advantage`, `algorithm`, `Simon算法与指数加速`
- source: `qa_pipeline`
- dataset_index: `2131`

### Prompt

作为量子计算领域的顶尖学者，请深入剖析Simon算法。要求：1. 阐释其解决隐藏子群问题的宏观原理；2. 对比分析其与经典算法的时间复杂度，论证其指数级加速的优势；3. 深刻揭示这种量子加速的物理与数学来源（如干涉、相对相位等）；4. 针对一个2量子比特的简单实例（秘密串 $s=11$），使用 isQ 语言编写该算法中包含预言机及阿达马变换的核心代码段。

### Reference answer

<think
	extbf{1. 宏观原理推导：}
	给定一个黑盒函数 $f: \{0,1\}^n \to \{0,1\}^n$，承诺其为一个二对一函数，即存在一个非零秘密串 $s \in \{0,1\}^n$，使得对所有 $x$，都有 $f(x) = f(x \oplus s)$。算法的目标是寻找 $s$。
	量子线路首先对 $n$ 个输入量子比特应用 Hadamard 门，产生均匀叠加态：
	$|\psi_1\rangle = \frac{1}{\sqrt{2^n}} \sum_{x \in \{0,1\}^n} |x\rangle$
	接着通过受控酉算子 $U_f$ 计算 $f(x)$ 并存储在辅助比特中：
	$|\psi_2\rangle = \frac{1}{\sqrt{2^n}} \sum_{x} |x\rangle |f(x)\rangle$
	由于 $f(x) = f(x \oplus s)$，我们可以将求和重新配对。当测量辅助寄存器并获得某个确定值 $f(z)$ 时，输入寄存器会坍缩到 $z$ 和 $z \oplus s$ 的叠加态：
	$|\psi_3\rangle = \frac{1}{\sqrt{2}} (|z\rangle + |z \oplus s\rangle)$
	再次对输入寄存器应用 Hadamard 门，推导其状态演变：
	$H^{\otimes n} |\psi_3\rangle = \frac{1}{\sqrt{2^{n+1}}} \sum_{y} \left( (-1)^{z \cdot y} + (-1)^{(z \oplus s) \cdot y} \right) |y\rangle$
	注意到 $(-1)^{(z \oplus s) \cdot y} = (-1)^{z \cdot y} (-1)^{s \cdot y}$。只有当 $(-1)^{s \cdot y} = 1$ 即 $s \cdot y = 0 \pmod 2$ 时，振幅才不会相消为零。因此，最终测量输入寄存器，必定会得到一个满足 $y \cdot s = 0$ 的向量 $y$。重复该过程 $n-1$ 次左右，获得一组线性无关的 $y$，即可通过经典高斯消元法解出 $s$。

		extbf{2. isQ 代码实现：}
	设定 $n=2$，秘密串 $s=11$。设计预言机 $U_f$ 使得 $f(x) = x_1$（即输入的第一位），显然满足 $f(x \oplus 11) = f(x)$。
	在 isQ 中，需要声明2个主比特和1个辅助比特（输出长度最小为1即可代表映射）。
</think
Simon算法是量子计算发展史上的一个里程碑，它不仅在理论上证明了量子计算机能够实现相对于经典计算机的指数级加速，而且为后来著名的Shor算法奠定了坚实的基础。

**一、 宏观原理与时间复杂度对比**
Simon算法解决的核心问题是“寻找二对一函数的周期”。给定一个黑盒函数 $f: \{0,1\}^n \to \{0,1\}^n$，已知存在一个秘密字符串 $s \neq 0^n$，使得对所有 $x$ 都有 $f(x) = f(x \oplus s)$。算法的目标是求出 $s$。
在经典计算框架下，要想找到这个 $s$，必须依赖生日悖论进行碰撞寻找。经典算法需要查询预言机 $\Omega(\sqrt{2^n}) = \Omega(2^{n/2})$ 次才能以高概率找到相同的输出，进而推导出 $s$。而Simon算法利用量子特性，仅需对预言机进行 $O(n)$ 次查询，结合高斯消元等经典后处理，总体时间复杂度仅为 $O(n^3)$。从 $O(2^{n/2})$ 到 $O(n^3)$，这是一种坚如磐石的指数级加速。

**二、 量子加速的深刻来源**
这种指数级加速的根本来源在于量子力学中的**叠加态**与**相长/相消干涉**。经典算法每次只能试探性地查看一个输入，而量子算法第一步就利用阿达马门将寄存器初始化为所有 $2^n$ 个可能输入的均匀叠加态，实现了真正的量子并行计算。当计算 $f(x)$ 并测量输出寄存器时，输入寄存器并没有坍缩为一个确定的值，而是坍缩为了两个满足周期关系的态 $|x\rangle$ 和 $|x \oplus s\rangle$ 的相干叠加。此时，经典世界完全无法实现这种“将两个不同的状态同时保存在内存中并进行联合操作”的行为。
紧接着，算法对输入寄存器再次施加阿达马变换。这一步是干涉的精妙所在：对于任意一个最终的基态 $|y\rangle$，其概率幅是 $\frac{1}{2^n} \sum_x (-1)^{x \cdot y}$。由于输入寄存器当前处于 $|x\rangle + |x \oplus s\rangle$ 的叠加，振幅中会引入 $(-1)^{x \cdot y}$ 和 $(-1)^{(x \oplus s) \cdot y}$ 的求和。如果 $s \cdot y = 1$，这两项符号相反，发生绝对的**相消干涉**，导致概率幅为0；如果 $s \cdot y = 0$，两项符号相同，发生**相长干涉**，概率幅翻倍。通过这种干涉效应，算法直接将隐藏在黑盒中的代数结构（$y \cdot s = 0$）提取到了测量概率分布中，从而彻底绕开了经典碰撞搜索的指数级壁垒。

**三、 isQ 代码演示**
下面以 $n=2$ 的系统为例，假设秘密串 $s=11$。我们定义函数 $f(x)$ 仅提取 $x$ 的第一位，即 $f(00)=f(10)=0$，$f(01)=f(11)=1$，显然满足 $f(x)=f(x \oplus 11)$。

```isQ
import std;

qbit q[2]; // 输入寄存器
qbit anc[1]; // 辅助寄存器，存储 f(x)

procedure main() {
    // 1. 初始化：对输入量子比特应用 Hadamard 门，构建叠加态
    for i in 0:2 {
        H(q[i]);
    }
    
    // 2. 预言机查询 Uf 实现
    // 设计 f(x) = x[0]，因此只需用 q[0] 控制辅助比特翻转
    CNOT(q[0], anc[0]);

    // 3. 测量辅助寄存器，使输入寄存器坍缩为 |x> + |x+s> 的叠加态
    int r = M(anc[0]);

    // 4. 再次对输入寄存器应用 Hadamard 门，引发干涉
    for i in 0:2 {
        H(q[i]);
    }

    // 5. 测量输入寄存器，结果必满足 y · s = 0 mod 2
    // 对于 s=11，可能的测量结果为 y=00 或 y=11
    int r0 = M(q[0]);
    int r1 = M(q[1]);
}
```

## isqTrain/4126

- task_id: `isqTrain/4126`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `5798`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[3];

procedure main() {
    X(q[2]);
    H(q[0]); H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 * 1.0 / 4.0 * 1.0, q[0], q[2]);
    ctrl Rz(2.0 * 3.14159265358979 * 1.0 / 4.0 * 2.0, q[1], q[2]);
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

Let me analyze this circuit step by step.

Initial state: |000>

1. X(q[2]): |000> → |001>

2. H(q[0]); H(q[1]): |001> → |+01> = (|001> + |101>)/√2 → (|001> + |011> + |101> + |111>)/2

3. ctrl Rz(π/2, q[0], q[2]): This is a CRz gate with angle π/2. When q[0] is |1>, apply Rz(π/2) to q[2].
   Rz(π/2) = diag(1, e^(iπ/2)) = diag(1, i)
   
   So states where q[0]=1 get a phase factor applied to q[2]:
   |001> → |001> (q[0]=0, no change)
   |011> → |011> (q[0]=0, no change)
   |101> → i|101> (q[0]=1, q[2]=1, phase e^(iπ/2)=i)
   |111> → i|111> (q[0]=1, q[2]=1, phase e^(iπ/2)=i)
   
   Wait, let me reconsider. CRz applies Rz to target when control is |1>.
   
   The state is (|001> + |011> + |101> + |111>)/2
   
   For |001>: q[0]=0, no change → |001>
   For |011>: q[0]=0, no change → |011>
   For |101>: q[0]=1, apply Rz(π/2) to q[2]. q[2]=1, so multiply by e^(iπ/2) = i → i|101>
   For |111>: q[0]=1, apply Rz(π/2) to q[2]. q[2]=1, so multiply by e^(iπ/2) = i → i|111>
   
   State: (|001> + |011> + i|101> + i|111>)/2

4. ctrl Rz(π, q[1], q[2]): When q[1] is |1>, apply Rz(π) to q[2].
   Rz(π) = diag(1, e^(iπ)) = diag(1, -1)
   
   For |001>: q[1]=0, no change → |001>
   For |011>: q[1]=1, apply Rz(π) to q[2]. q[2]=1, multiply by -1 → -|011>
   For i|101>: q[1]=0, no change → i|101>
   For i|111>: q[1]=1, apply Rz(π) to q[2]. q[2]=1, multiply by -1 → -i|111>
   
   State: (|001> - |011> + i|101> - i|111>)/2

5. CNOT(q[0], q[1]): q[0] is control, q[1] is target. Flip q[1] when q[0]=1.
   |001> → |001> (q[0]=0)
   |011> → |011> (q[0]=0)
   i|101> → i|111> (q[0]=1, flip q[1])
   -i|111> → -i|101> (q[0]=1, flip q[1])
   
   State: (|001> - |011> + i|111> - i|101>)/2 = (|001> - |011> - i|101> + i|111>)/2

6. CNOT(q[1], q[0]): q[1] is control, q[0] is target. Flip q[0] when q[1]=1.
   |001> → |001> (q[1]=0)
   -|011> → -|111> (q[1]=1, flip q[0])
   -i|101> → -i|101> (q[1]=0)
   i|111> → i|011> (q[1]=1, flip q[0])
   
   State: (|001> + i|011> - i|101> - |111>)/2

7. CNOT(q[0], q[1]): q[0] is control, q[1] is target. Flip q[1

### Reference answer

Dominant output states: |101> with probability ~0.50 each

## isqTrain/3472

- task_id: `isqTrain/3472`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `hamiltonian_simulation`, `basis_change`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `538`

### Prompt

Write isQ code for the following quantum task: the second-order Suzuki-Trotter decomposition for H = X_0*X_1 + Z_0*Z_1 in isQ.

The second-order formula is:
  exp(-i*dt*H) ~ exp(-i*dt/2 * XX) * exp(-i*dt * ZZ) * exp(-i*dt/2 * XX)

Use dt=0.5. Apply to |10>.
Declare 2 qubits, measure both.

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

Initial state: |00>

After X(q[0]): |10>

Now applying exp(-i*dt/2 * XX) where dt/2 = 0.25:

For XX interaction, the decomposition is:
- H on both qubits
- CNOT(q[0], q[1])
- Rz(2*dt/2, q[1]) = Rz(0.5, q[1])
- CNOT(q[0], q[1])
- H on both qubits

Let me trace the state evolution:

|10>

First half XX:
H(q[0]), H(q[1]): H|10> = |->|0> = (|10> - |00>)/√2

Wait, let me be more careful.
H(q[0]) applied to |10> = H|1>⊗|0> = |->⊗|0> = (|0>-|1>)/√2 ⊗ |0> = (|00>-|10>)/√2
H(q[1]) applied to above: (|01>-|11>)/√2

CNOT(q[0], q[1]): (|01>-|10>)/√2

Rz(0.5, q[1]): e^{-i*0.25}|01> - e^{i*0.25}|10>) / √2
Actually Rz(θ)|0> = e^{-iθ/2}|0>, Rz(θ)|1> = e^{iθ/2}|1>

So Rz(0.5, q[1]): (e^{-i*0.25}|01> - e^{i*0.25}|10>)/√2

CNOT(q[0], q[1]): (e^{-i*0.25}|00> - e^{i*0.25}|11>)/√2

H(q[0]), H(q[1]): 
H⊗H applied:
|00> → |++> = (|00>+|01>+|10>+|11>)/2
|11> → |--> = (|00>-|01>-|10>+|11>)/2

So state = (e^{-i*0.25}(|00>+|01>+|10>+|11>) - e^{i*0.25}(|00>-|01>-|10>+|11>)) / (2√2)

= ((e^{-i*0.25} - e^{i*0.25})|00> + (e^{-i*0.25} + e^{i*0.25})|01> + (e^{-i*0.25} + e^{i*0.25})|10> + (e^{-i*0.25} - e^{i*0.25})|11>) / (2√2)

= (-2i sin(0.25)|00> + 2cos(0.25)|01> + 2cos(0.25)|10> - 2i sin(0.25)|11>) / (2√2)

= (cos(0.25)(|01>+|10>) - i*sin(0.25)(|00>+|11>)) / √2

This is getting complex. Let me just describe the steps conceptually.

Actually, let me think about this differently. The key insight is:

exp(-iθ·XX) can be implemented as: H⊗H · CNOT · (I⊗Rz(2θ)) · CNOT · H⊗H

exp(-iθ·ZZ) can be implemented as: CNOT · (I⊗Rz(2θ)) · CNOT

The circuit implements:
exp(-i·0.25·XX) · exp(-i·0.5·ZZ) · exp(-i·0.25·XX)

Applied to |10>.

The final measurement probabilities are {|01>: 0.229849, |10>: 0.770151}.

Let me verify: the Hamiltonian is H = XX + ZZ. On 2 qubits, the XX and ZZ terms commute? No, they don't commute in general. [XX, ZZ] = XX·ZZ - ZZ·XX = i·YY·(-1) - (-1)·i·YY... Actually let me compute properly.

XX · ZZ = X₁X₂ · Z₁Z₂ = (XZ)₁ ⊗ (XZ)₂
Z₁Z₂ · X₁X₂ = (ZX)₁ ⊗ (ZX)₂

XZ = [[0,1],[1,0]][[1,0],[0,-1]] = [[0,-1],[1,0]] = -iY
ZX =

## isqExpand/algo/54

- task_id: `isqExpand/algo/54`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `mid_circuit_measurement`, `basis_change`, `phase_manipulation`
- source: `isq_expansion`
- dataset_index: `5205`

### Prompt

Implement a quantum circuit in isQ: teleports an arbitrary state prepared by Ry(pi/3) on q[0] to Bob's qubit q[2]. Steps:
1. Prepare Alice's qubit: Ry(1.0472, q[0]) (pi/3 radians).
2. Create a Bell pair on q[1],q[2]: H(q[1]), CNOT(q[1],q[2]).
3. Bell measurement: CNOT(q[0],q[1]), H(q[0]), then mid-circuit measure q[0] and q[1].
4. Classical corrections: if m1==1 apply X(q[2]), if m0==1 apply Z(q[2]).
5. To verify, apply inverse Ry (i.e., Ry(-1.0472, q[2])) to undo the state, mapping it back to |0>.
6. Measure q[2]. It should always give 0.

### Chain-of-thought reasoning

## Reasoning
Goal: Teleport Ry(pi/3)|0> from q[0] to q[2], then verify by applying Ry(-pi/3).

Ry(pi/3)|0> = cos(pi/6)|0> + sin(pi/6)|1> = (sqrt(3)/2)|0> + (1/2)|1>.

Teleportation protocol:
1. Ry(1.0472, q[0]): prepare alpha|0>+beta|1> with alpha=sqrt(3)/2, beta=1/2.
2. Bell pair on q[1],q[2]: (|00>+|11>)/sqrt(2).
3. Full state: (alpha|0>+beta|1>) (x) (|00>+|11>)/sqrt(2).
4. Bell measurement decomposes into four branches:
   - m0=0,m1=0: q[2] = alpha|0>+beta|1> (no correction needed)
   - m0=0,m1=1: q[2] = alpha|1>+beta|0> -> X restores
   - m0=1,m1=0: q[2] = alpha|0>-beta|1> -> Z restores
   - m0=1,m1=1: q[2] = -alpha|1>+beta|0> -> XZ restores
5. After corrections, q[2] = Ry(pi/3)|0>.
6. Ry(-pi/3) undoes: Ry(-pi/3)Ry(pi/3)|0> = |0>.
7. Measurement always gives 0.

stdout_match mode for mid-circuit measurement.

## isqTrain/551

- task_id: `isqTrain/551`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `entanglement`, `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_if_else`, `isq_syntax_multi_register`, `isq_syntax_print`, `mid_circuit_measurement`
- source: `isq_train_cot`
- dataset_index: `3844`

### Prompt

Help me write isQ code that implements the bell_state_preparation pattern but with a different initial state preparation (flip q[[0, 2]] -> q[1]).

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

We have 3 qubits q[0], q[1], q[2] all initialized to |000⟩.

Step 1: X(q[1]) - flips q[1]
State: |000⟩ → |010⟩

Step 2: H(q[1]) - Hadamard on q[1]
|010⟩ → |0⟩ ⊗ (|0⟩-|1⟩)/√2 ⊗ |0⟩ = (|010⟩ - |011⟩)/√2

Step 3: CNOT(q[1], q[2])
CNOT with q[1] as control, q[2] as target
(|010⟩ - |011⟩)/√2 → (|010⟩ - |011⟩)/√2
Wait, let me recalculate:
- |010⟩: q[1]=1, so q[2] flips: |010⟩ → |011⟩
- |011⟩: q[1]=1, so q[2] flips: |011⟩ → |010⟩

So: (|011⟩ - |010⟩)/√2 = -( |010⟩ - |011⟩)/√2

Actually let me be more careful:
(|010⟩ - |011⟩)/√2 after CNOT(q[1], q[2]):
- |010⟩ → |011⟩
- |011⟩ → |010⟩

Result: (|011⟩ - |010⟩)/√2

Step 4: CNOT(q[0], q[1])
- |011⟩ → |011⟩ (q[0]=0, no flip)
- |010⟩ → |010⟩ (q[0]=0, no flip)

State unchanged: (|011⟩ - |010⟩)/√2

Step 5: H(q[0])
(|0⟩(|11⟩ - |10⟩) - )/√2... wait, let me write this more carefully.

State is: (-|010⟩ + |011⟩)/√2

H(q[0]) on |0⟩ gives (|0⟩ + |1⟩)/√2

So: ((|0⟩ + |1⟩)/√2) ⊗ (-|10⟩ + |11⟩)/√2
= (-|010⟩ + |011⟩ - |110⟩ + |111⟩)/2

Step 6: Measure q[0] and q[1]

m1 = M(q[0]), m2 = M(q[1])

The state is (-|010⟩ + |011⟩ - |110⟩ + |111⟩)/2

Let me compute probabilities:

Looking at q[0], q[1] pairs:
- |0,1,0⟩: prob 1/4
- |0,1,1⟩: prob 1/4
- |1,1,0⟩: prob 1/4
- |1,1,1⟩: prob 1/4

Wait, but what about q[2]? The state has definite values for q[2] correlated with q[1].

Actually, let me reconsider. The state is:
(-|010⟩ + |011⟩ - |110⟩ + |111⟩)/2

All four terms have equal amplitude 1/2 (with some signs).

Now measuring q[0] and q[1]:

- |010⟩: q[0]=0, q[1]=1, q[2]=0, prob=1/4
- |011⟩: q[0]=0, q[1]=1, q[2]=1, prob=1/4
- |110⟩: q[0]=1, q[1]=1, q[2]=0, prob=1/4
- |111⟩: q[0]=1, q[1]=1, q[2]=1, prob=1/4

Now the classical corrections:

if (m2) { } - does nothing
if (m1) { Z(q[2]); }

So when m1=1 (q[0] measured as 1), apply Z to q[2].

For |110⟩: m1=1, Z(q[2]) applied. Z on |0⟩ = |0⟩. Result: |110⟩ unchanged.
For |111⟩: m1=1, Z(q[2]) applied. Z on |1⟩ = -|1⟩. Result: -|111⟩.

So final state before measuring q[2]:
(-|010⟩ + |011⟩ - |110⟩ - |111⟩)/2

Wait, but after measurement, we're in a collapsed state. Let me reconsider.

After measuring q[0] and q[1], the state collapses

## isqTrain/1219

- task_id: `isqTrain/1219`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5313`

### Prompt

Code this in isQ: implements the quantum_volume pattern with modified rotation parameters (num_pi3_to_pi4). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

The user wants me to analyze the given isQ quantum program that implements a quantum volume pattern with modified rotation parameters.

Let me trace through the circuit:

1. Initial state: |00>

2. Ry(π/4, q[0]) on q[0]:
   - Ry(θ) = [[cos(θ/2), -sin(θ/2)], [sin(θ/2), cos(θ/2)]]
   - θ = π/4, so θ/2 = π/8
   - cos(π/8) ≈ 0.9239, sin(π/8) ≈ 0.3827
   - |0> → cos(π/8)|0> + sin(π/8)|1>
   - State: (0.9239|0> + 0.3827|1>) ⊗ |0>

3. Ry(2π/5, q[1]) on q[1]:
   - Wait, 0.62831853071796 is actually 2π/10 = π/5
   - θ = π/5, θ/2 = π/10
   - cos(π/10) ≈ 0.9511, sin(π/10) ≈ 0.3090
   - State: (0.9239|0> + 0.3827|1>) ⊗ (0.9511|0> + 0.3090|1>)

4. CNOT(q[0], q[1]):
   - This entangles the two qubits

5. Rz(π/4, q[0]):
   - Adds phase to |1> component

6. Rx(π/6, q[1]):
   - Rotates q[1] on X axis

7. CNOT(q[0], q[1]):
   - Further entanglement

8. Measurement

Let me recalculate more carefully:

0.78539816339745 = π/4
0.62831853071796 ≈ 0.2π = π/5
0.52359877559830 = π/6

So the gates are:
- Ry(π/4, q[0])
- Ry(π/5, q[1])  
- CNOT(q[0], q[1])
- Rz(π/4, q[0])
- Rx(π/6, q[1])
- CNOT(q[0], q[1])

Let me trace the state evolution:

Initial: |00>

After Ry(π/4, q[0]):
Ry(θ)|0> = cos(θ/2)|0> + sin(θ/2)|1>
θ/2 = π/8
cos(π/8) = 0.9239, sin(π/8) = 0.3827
State: (0.9239|0> + 0.3827|1>)|0>
     = 0.9239|00> + 0.3827|10>

After Ry(π/5, q[1]):
cos(π/10) = 0.9511, sin(π/10) = 0.3090
State: 0.9239(0.9511|00> + 0.3090|01>) + 0.3827(0.9511|10> + 0.3090|11>)
     = 0.8787|00> + 0.2855|01> + 0.3639|10> + 0.1183|11>

After CNOT(q[0], q[1]):
|00> → |00>, |01> → |01>, |10> → |11>, |11> → |10>
State: 0.8787|00> + 0.2855|01> + 0.3639|11> + 0.1183|10>
     = 0.8787|00> + 0.2855|01> + 0.1183|10> + 0.3639|11>

After Rz(π/4, q[0]):
Rz(θ)|ψ> = |0><0|ψ> + e^(iθ)|1><1|ψ>
Rz(π/4) adds e^(iπ/4) phase to |1> components
State: 0.8787|00> + 0.2855|01> + e^(iπ/4

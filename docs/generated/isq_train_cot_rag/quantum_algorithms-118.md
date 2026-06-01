# ISQ training COT RAG corpus: quantum_algorithms shard 118

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2787

- task_id: `isqTrain/2787`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1554`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```isq
import std;

qbit q[2];

procedure main(){
    H(q[0]);
    CNOT(q[0],q[1]);
    M(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Bug Analysis
1. **The bug** is in the final line of the circuit, where `M(q[0])` is called a second time instead of measuring the second qubit. To fully characterize the entangled Bell pair, both qubits must be measured.
2. **The fix** is to change the final measurement from `M(q[0])` to `M(q[1])`.
3. **State evolution**:
   - Initialize to |00>.
   - Apply H(q[0]): state becomes (1/√2)(|00> + |10>).
   - Apply CNOT(q[0], q[1]): state becomes the Bell state (1/√2)(|00> + |11>).
   - Measure q[0] and q[1]: correctly yields a 50% probability for both |00> and |11>.

## isqTrain/3636

- task_id: `isqTrain/3636`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `5245`

### Prompt

Code this in isQ: the 4-qubit QFT applied to input state |0101>. The circuit should use Hadamard gates, controlled-Rz rotations with angles 2π/2^k, and final bit-reversal swaps. Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Implement 4-qubit QFT on |0101> and measure all qubits.
2. **Qubits:** 4 global qubits q[0..3]; all measured.
3. **State evolution:**
   - X(q[1]), X(q[3]) prepare |0101> from |0000⟩.
   - QFT applies H followed by controlled-Rz(2π/2^k) rotations on each qubit, building the Fourier basis: QFT|x⟩ = (1/4)Σ_k e^{2πixk/16}|k⟩ for N=16.
   - For input |5⟩: each basis state |k⟩ gets amplitude (1/4)e^{2πi·5·k/16}, all with equal magnitude |1/4|.
   - Bit-reversal swaps (q[0]↔q[3], q[1]↔q[2]) correct the output ordering.
4. **Probabilities:** Since all 16 amplitudes have magnitude 1/4, every outcome |0000⟩ through |1111⟩ has probability 1/16 = 0.0625.

## isqTrain/831

- task_id: `isqTrain/831`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_ctrl_nctrl`, `phase_manipulation`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `1785`

### Prompt

用isQ实现implements the qft_adder pattern but with a different initial state preparation (flip q[[0, 2]] -> q[1]).

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for the given isQ program.

Let me analyze the circuit:

1. Initial state: |000>
2. X(q[1]) prepares |010> (which is 2 in decimal, not |101> as the comment says - the comment is wrong, the task says "flip q[[0, 2]] -> q[1]" meaning we flip q[1] only)
3. Then QFT is applied on 3 qubits

Wait, let me re-read. The task says "flip q[[0, 2]] -> q[1]" which I interpret as: instead of flipping q[0] and q[2], we flip q[1].

So the initial state preparation is X(q[1]), giving us |010>.

Then QFT on |010>:
- QFT on a computational basis state |j⟩ where j=2 (binary 010) produces a uniform superposition over all 8 basis states, each with phase factor.

Actually, QFT on |j⟩ for an n-qubit system produces:
QFT|j⟩ = (1/√N) Σ_k e^(2πijk/N) |k⟩

where N = 2^n = 8, j = 2.

So QFT|010⟩ = (1/√8) Σ_{k=0}^{7} e^(2πi·2·k/8) |k⟩
= (1/√8) Σ_k e^(πik/2) |k⟩

The magnitudes are all 1/√8, so probabilities are all 1/8 = 0.125.

This matches the predicted output where all probabilities are 0.125.

Let me trace through more carefully:

Start: |000>
After X(q[1]): |010>

QFT on q[2]:
- H(q[2]): (1/√2)(|010⟩ + |110⟩)
- ctrl S(q[1], q[2]): Since q[1]=1, apply S to q[2]. S adds phase i to |1⟩ part of q[2]. So |110⟩ → i|110⟩. State: (1/√2)(|010⟩ + i|110⟩)
- ctrl T(q[0], q[2]): Since q[0]=0, no action. State unchanged.

QFT on q[1]:
- H(q[1]): Apply H to q[1]. For |010⟩: q[1]=1, so H on |1⟩ = (|0⟩-|1⟩)/√2. For |110⟩: q[1]=1, same. 
  State: (1/√2)[(1/√2)(|000⟩ - |010⟩) + i(1/√2)(|100⟩ - |110⟩)]
  = (1/2)(|000⟩ - |010⟩ + i|100⟩ - i|110⟩)
- ctrl S(q[0], q[1]): Since q[0]=0 always (at this point), no action.

QFT on q[0]:
- H(q[0]): Apply H to q[0].
  |000⟩ → (1/√2)(|000⟩ + |100⟩)
  -|010⟩ → -(1/√2)(|010⟩ + |110⟩)
  i|100⟩ → i(1/√2)(|000⟩ - |100⟩)
  -i|110⟩ → -i(1/√2)(|010⟩ - |110⟩)
  
  Total: (1/2√2)[|000⟩+|100⟩ - |010⟩-|110⟩ + i|000⟩-i|100⟩ - i|010⟩+i|110⟩]
  = (1/2√2)[(1+i)|000⟩ + (1-i)|100⟩ - (1+i)|010⟩ - (1-i)|110⟩ + ...wait, I need to track all 8 basis states.

Actually wait, after H(q[0]) the states |000⟩, |010⟩, |100⟩, |110⟩ each split into two. Let me be more careful:

After H(q[0]):
(1/2) × [H on q[0] of |000⟩ - H on q[0] of |010⟩ + i·H on q[0] of |100⟩ - i·H on q[0] of |110⟩]

H|0⟩ = (|0⟩+|1⟩)/√2
H|1⟩ = (|0⟩-|1⟩)/√2

|000⟩ → (|000⟩+|100⟩)/√2
|010⟩ → (|010⟩+|110⟩)/√2
|100⟩ → (

## isqTrain/784

- task_id: `isqTrain/784`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `finite_field_arithmetic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `448`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[3];

procedure main() {
    // Set both field elements to 1
    X(q[0]);
    X(q[1]);
    // GF(2) multiplication: product = a AND b
    // In GF(2), multiplication is the AND operation
    Toffoli(q[0], q[1], q[2]);
    // Measure the product
    M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. Operations: Two X gates are applied to `q[0]` and `q[1]`, followed by a Toffoli gate with `q[0]` and `q[1]` as controls and `q[2]` as the target. Finally, `q[2]` is measured.
2. Evolution: The system starts in the state |000⟩. The X gates flip `q[0]` and `q[1]`, evolving the state to |110⟩.
3. The Toffoli gate flips the target qubit `q[2]` from |0⟩ to |1⟩ only if both control qubits are in the |1⟩ state. 
4. Final state: Since the controls are |1⟩, the system transitions to the final state |111⟩. The measured qubit `q[2]` is

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqEval/284. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3480

- task_id: `isqTrain/3480`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `basis_change`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1325`

### Prompt

Implement the following in isQ: Prepare the Bell state |Psi-> = (|01> - |10>)/sqrt(2) in isQ.

Circuit: X(q[1]), H(q[0]), CNOT(q[0],q[1]), Z(q[0]).
Verify via Bell basis measurement. Expected: |11>.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Generate a concise reasoning section (3-15 lines) for a specific isQ quantum circuit that prepares the Bell state $|\Psi^-\rangle = (|01\rangle - |10\rangle)/\sqrt{2}$ and measures it in the Bell basis.
    *   Circuit: `X(q[1]), H(q[0]), CNOT(q[0],q[1]), Z(q[0])` followed by Bell basis measurement `CNOT(q[0],q[1]), H(q[0])` then `M(q); M(q);`.
    *   Expected outcome: `|11>` with probability 1.0.
    *   Output format: "## Reasoning" followed by the step-by-step explanation.

2.  **Circuit Breakdown & State Evolution:**
    *   Initial state: $|00\rangle$
    *   `X(q[1])`: $|01\rangle$
    *   `H(q[0])`: $\frac{1}{\sqrt{2}}(|01\rangle + |11\rangle)$
    *   `CNOT(q[0], q[1])`: $\frac{1}{\sqrt{2}}(|01\rangle + |10\rangle) = |\Phi^+\rangle$
    *   `Z(q[0])`: $\frac{1}{\sqrt{2}}(|01\rangle - |10\rangle) = |\Psi^-\rangle$ (Goal state achieved)
    *   *Measurement in Bell basis:*
    *   `CNOT(q[0], q[1])`: $\frac{1}{\sqrt{2}}(|01\rangle - |11\rangle)$
    *   `H(q[0])`: $\frac{1}{\sqrt{2}}\left(\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)|1\rangle - \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)|1\rangle\right) = \frac{1}{2}(|01\rangle + |11\rangle - |01\rangle + |11\rangle) = |11\rangle$
    *   Measurement of $|11\rangle$ gives bitstring 11 with probability 1.0.

3.  **Drafting the Reasoning:**
    *   *Goal:* Prepare the Bell state $|\Psi^-\rangle = (|01\rangle - |10\rangle)/\sqrt{2}$ and verify it via Bell measurement.
    *   *Qubits:* Requires 2 qubits, both measured.
    *   *Evolution:*
        *   Start: $|00\rangle$
        *   `X(q[1])` -> $|01\rangle$
        *   `H(q[0])` -> $\frac{1}{\sqrt{2}}(|01\rangle + |11\rangle)$
        *   `CNOT(q[0],q[1])` -> $\frac{1}{\sqrt{2}}(|01\rangle + |10\rangle)$
        *   `Z(q[0])` -> $|\Psi^-\rangle = \frac{1}{\sqrt{2}}(|01\rangle - |10\rangle)$
        *   *Inverse Bell transform* (`CNOT(q[0],q[1])`, `H(q[0])`) maps $|\Psi^-\rangle$ to $-|11\rangle$ (physically equivalent to $|11\rangle$ upon measurement).
    *   *Probability:* The final state before measurement is $|11\rangle$, yielding a 100% probability of measuring 11.

4.  **Refining and Formatting:**
    *   Ensure Dirac notation is used.
    *   Ensure it's 3-8 lines (simple enough).
    *   Check if the math holds: `CNOT(q[0],q[1])` on $(|01\rangle - |10\rangle)/\sqrt{2} \rightarrow (|01\rangle - |11\rangle)/\sqrt{2}$. Then `H(q[0])` on $|0\rangle \rightarrow (|0\rangle+|1\rangle)/\sqrt{2}$ and $|1\rangle \rightarrow (|0\rangle-|1\rangle)/\sqrt{2}$.
        $( (|0\rangle+|1\rangle)|1\rangle - (|0\rangle-|1\rangle)|1\rangle ) / 2 = (|01\rangle + |11\rangle - |01\rangle + |11\rangle)/2 = |11\rangle$. Yes, correct.

5.  **Final Output Generation:**
    Follow

## isqQA/quantum_algorithms/101_step_by_step

- task_id: `isqQA/quantum_algorithms/101_step_by_step`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `step_by_step`, `algorithm`, `Grover搜索的最优性证明`
- source: `qa_pipeline`
- dataset_index: `3417`

### Prompt

教授您好！我已经了解了Grover搜索算法的基本原理，知道它可以在O(√N)的时间内找到目标项。但我听说这个算法在未结构化数据库搜索中已经是“最优”的了。您能否一步步地带我手动追踪Grover算法的几何演化过程，并借此严格推导证明为什么它的复杂度O(√N)已经是量子计算的物理极限？另外，能否提供一个2量子比特的isQ代码，让我能通过追踪代码对应的量子态来加深理解？

### Reference answer

<think>
要解决此问题，首先需要将高维希尔伯特空间降维。我们将系统状态投影到由目标态（“好态”）和非目标态（“坏态”）构成的二维平面上。在此平面内，初始均匀叠加态与坏态的夹角 $\theta/2$ 满足 $\sin(\theta/2) = 1/\sqrt{N}$。

接着追踪几何演化：Grover迭代包含Oracle（关于坏态反射）和扩散算子（关于初始态反射）。根据几何学，两次反射等效于向着目标态旋转 $\theta$ 角度。

然后推导复杂度极限：要使状态旋转至目标态，需转过约 $\pi/2$ 的总角度。因此所需迭代次数 $k \approx (\pi/2)/\theta \approx \frac{\pi}{4}\sqrt{N}$，得出 $O(\sqrt{N})$ 复杂度。结合量子查询下界理论（如BBBV定理），可严格证明任何量子算法都无法打破此查询次数极限，确认为物理最优。

最后，选取2量子比特（N=4）的情况进行代码演示。此时 $\theta = \pi/3$，仅需1次迭代。据此构建isQ代码，通过追踪H门、特定相位翻转及扩散算子作用后的振幅，即可直观验证这一几何旋转过程。
</think>

你好！这是一个非常深刻的问题。要理解Grover算法的最优性，最直观的方法就是通过“几何追踪”来观察量子态是如何在希尔伯特空间中演化的。我们分四步来推导并证明。

第一步：构建二维几何模型
对于一个规模为N=2^n的未结构化数据库，我们定义两个极其重要的正交基底：
1. “好态”（目标态）|w⟩。
2. “坏态”（所有非目标态的归一化叠加）|s'⟩ = 1/√(N-1) ∑|x⟩ (x≠w)。
初始态是均匀叠加态 |s⟩ = 1/√N |w⟩ + √((N-1)/N) |s'⟩。在由 |w⟩ 和 |s'⟩ 构成的二维平面内，初始态 |s⟩ 与 |s'⟩ 的夹角设为 θ/2。我们可以得出 sin(θ/2) = ⟨w|s⟩ = 1/√N。因为N通常极大，所以 θ/2 极小，约等于 1/√N。

第二步：追踪Grover迭代的几何旋转
一次完整的Grover迭代包含两步：
1. Oracle操作 U_w = I - 2|w⟩⟨w|：这是一个关于 |s'⟩ 轴的镜像反射。
2. 扩散操作 U_s = 2|s⟩⟨s| - I：这是一个关于 |s⟩ 轴的镜像反射。
在几何学中，连续进行两次镜像反射，等价于直接进行一次旋转，且旋转的角度是两个反射轴夹角的两倍。因此，每一次Grover迭代 G = U_s U_w 都会将当前状态向量朝着 |w⟩ 的方向旋转 θ 角度。

第三步：推导状态演化的解析式
经过 k 次Grover迭代后，状态向量被旋转了 kθ 角度，此时系统状态为：
|ψ_k⟩ = sin((2k+1)θ/2) |w⟩ + cos((2k+1)θ/2) |s'⟩
此时测量得到目标态 |w⟩ 的概率振幅为 sin((2k+1)θ/2)。

第四步：证明O(√N)的最优性下界
我们要让成功概率逼近100%，即要求 sin((2k+1)θ/2) ≈ 1，这就要求 (2k+1)θ/2 ≈ π/2。
由于当 N 很大时 θ ≈ 2/√N，代入可得：
(2k+1) * (1/√N) ≈ π/2  =>  k ≈ (π/4)√N - 1/2
这就严格证明了我们需要 O(√N) 次迭代才能找到目标。

最优性证明：为什么不能更快？假设存在某种查询次数为 T 的量子算法，能在 T < √N 步内发现目标。根据几何追踪，如果不经过至少 O(√N) 次旋转，角度 (2T+1)θ/2 将远小于 π/2，此时 sin²((2T+1)θ/2) 将是一个趋于 0 的极小值，测量坍缩到 |w⟩ 的概率微乎其微。任何试图绕过这个角度累加过程的算法，都会违背幺正演化的几何正交性。因此，O(√N) 是未结构化搜索的绝对理论下界，Grover算法最优。

下面是一个2量子比特（N=4）寻找目标态 |11⟩ 的isQ代码，你可以手动追踪它的振幅变化：

import std;

qbit q[2];

procedure main() {
    // 初始化: 制备均匀叠加态 |s⟩
    for i in 0:2 {
        H(q[i]);
    }
    
    // Oracle操作 U_w: 标记并翻转 |11⟩ 的相位
    H(q[1]);
    CNOT(q[0], q[1]);
    H(q[1]);
    
    // 扩散操作 U_s: 关于 |s⟩ 的反射
    for i in 0:2 {
        H(q[i]);
        X(q[i]);
    }
    
    // 使用等价逻辑实现多控Z
    H(q[1]);
    CNOT(q[0], q[1]);
    H(q[1]);
    
    for i in 0:2 {
        X(q[i]);
        H(q[i]);
    }
    
    // 测量
    for i in 0:2 {
        M(q[i]);
    }
}

## isqTrain/4123

- task_id: `isqTrain/4123`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `3127`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[4];

procedure main() {
    X(q[0]);
    X(q[2]);

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

The isQ circuit provided is a 4-qubit quantum circuit (q[0], q[1], q[2], q[3]) with initial state |0000⟩. After applying the gates, the final state is |0111⟩ with probability 1.
1.  **Initial state:** |0000⟩.
2.  **X(q[0]) and X(q[2])**: Flips q[0] and q[2] to |1>. State becomes |0101⟩ (assuming q[3]q[2]q[1]q[0] = |0000⟩, so q[0]=1, q[2]=1, resulting in |0101> or binary `0101`). Wait, let's establish the bit ordering. Usually q[0] is the least significant bit. So `|q[3] q[2] q[1] q[0]>`. Initial `|0000>`. X on q[0] -> `|0001>`. X on q[2] -> `|0101>`.
3.  **swap (three-CNOT decomposition)(q[0], q[3])**: The sequence CNOT(q[0], q[3]); CNOT(q[3], q[0]); CNOT(q[0], q[3]) implements a swap operation (three-CNOT decomposition). It swaps q[0] and q[3]. State `|0101>` becomes `|1100>`.
4.  **swap (three-CNOT decomposition)(q[1], q[2])**: The sequence CNOT(q[1], q[2]); CNOT(q[2], q[1]); CNOT(q[1], q[2]) implements a swap operation (three-CNOT decomposition). It swaps q[1] and q[2]. State `|1100>` becomes `|1010>`.
5.  **QFT**: The remaining gates form the inverse Quantum Fourier Transform (QFT†) on the 4 qubits, or actually QFT followed by measurements?
    Let's analyze the QFT structure. A standard QFT on n qubits applies:
    H on q[n-1], then CR_k on q[n-1] controlling q[n-2] down to q[0].
    Here, the structure is:
    H(q[3])
    ctrl Rz(-pi/2, q[3], q[2])
    H(q[2])
    ctrl Rz(-pi/4, q[3], q[1])
    ctrl Rz(-pi/2, q[2], q[1])
    H(q[1])
    ctrl Rz(-pi/8, q[3], q[0])
    ctrl Rz(-pi/4, q[2], q[0])
    ctrl Rz(-pi/2, q[1], q[0])
    H(q[0])

    Wait, the angles are `-2 * pi / 2^k`. Let's list them:
    `ctrl Rz(-2.0 * pi / 4.0, q[3], q[2])` -> angle `-pi/2` -> `Rz(-pi/2)`.
    If the target is `|1>`, it applies `exp(-i * -pi/2 / 2) = exp(i pi/4)`. Wait, standard QFT CR_k is `diag(1, exp(2 pi i / 2^k))`.
    Let's look at `ctrl Rz(theta, control, target)`. In isQ, `ctrl Rz(theta, control, target)` applies `exp(i theta / 2)` or similar to the target when control is 1? No, `ctrl` makes it a controlled gate. The gate is `Rz(theta)`. `Rz(theta) = diag(exp(-i theta/2), exp(i theta/2))`.
    Actually, let's see the effect of `ctrl Rz(-2pi/2^k)` on the state.
    The QFT acts on state `|x>`.
    Let's see what happens if we apply QFT to `|1010>` (which is 10 in decimal).
    If the circuit applies QFT to `|10>`, the output should be a superposition.
    Wait, QFT on `|1010>` is just applying QFT.
    Let's calculate QFT|1010>.
    Wait, the structure is:
    H on q[3] ... this is standard QFT where q[3] is the highest bit.
    Let's trace QFT on `|1010>`.
    Actually, standard QFT maps $|x\rangle$ to $\frac{1}{\sqrt{N}} \sum_y e^{2\pi i x y / N} |y\rangle$.
    If $x = 1010_2 = 10_{10

### Reference answer

Uniform distribution across 16 states

## isqTrain/910

- task_id: `isqTrain/910`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2028`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[3];

procedure main() {
    // Prepare input x = |10>
    X(q[0]);
    // Bit-flip oracle for f(x) = x[0] XOR x[1]
    // XOR decomposes as two CNOT gates targeting q[2]
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
    // XOR(1,0)=1, output flips to |1>
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
- The circuit starts with 3 qubits in the initial state |000> (format |q[2] q[1] q[0]>).
- `X(q[0])` flips the 0th qubit, changing the state to |001>.
- `CNOT(q[0], q[2])` targets q[2] with q[0] as control. Since q[0] is in the |1> state, q[2

### Reference answer

{'predicted_probs': {'5': 1.0}, 'explanation': 'Parametric variant of isqEval/261. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3446

- task_id: `isqTrain/3446`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `entanglement`, `isq_syntax_ctrl_nctrl`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `858`

### Prompt

Implement the following in isQ: 3-qubit W-state preparation in isQ.

The W state is |W> = (|001> + |010> + |100>) / sqrt(3).
Each qubit has probability 1/3 of being |1>.

Circuit:
1. X(q[0]) to start with |100>
2. Ry(2*arccos(sqrt(1/3))) on q[0] to distribute amplitude
   angle = 2*arccos(1/sqrt(3)) ~ 1.2310
3. Controlled-SWAP between q[0] and q[1], controlled on appropriate state

Alternative approach: use controlled rotations and CNOTs.
Declare 3 qubits, measure all.
Expected: each of |001>, |010>, |100> with probability ~1/3.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for the 3-qubit W-state preparation circuit in isQ.

Let me trace through the circuit:

1. Initialize |000⟩
2. X(q[0]): |000⟩ → |100⟩
3. Ry(1.2309594173407747, q[0]): This rotates q[0]. The angle θ = 2*arccos(1/√3).
   - Ry(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩ = (1/√3)|0⟩ + √(2/3)|1⟩
   - Ry(θ)|1⟩ = -sin(θ/2)|0⟩ + cos(θ/2)|1⟩ = -√(2/3)|0⟩ + (1/√3)|1⟩

Wait, let me be more careful. After X(q[0]), the state is |100⟩.

Now applying Ry(1.2310, q[0]):
- q[0] is in state |1⟩
- Ry(θ)|1⟩ = cos(θ/2)|1⟩ - sin(θ/2)|0⟩ 

Actually, let me recall the Ry gate matrix:
Ry(θ) = [[cos(θ/2), -sin(θ/2)], [sin(θ/2), cos(θ/2)]]

So:
Ry(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩
Ry(θ)|1⟩ = -sin(θ/2)|1⟩ + cos(θ/2)|0⟩

Wait no:
Ry(θ)|1⟩ = -sin(θ/2)|0⟩ + cos(θ/2)|1⟩

With θ = 2*arccos(1/√3):
- cos(θ/2) = 1/√3
- sin(θ/2) = √(1 - 1/3) = √(2/3)

So Ry(θ)|1⟩ = -√(2/3)|0⟩ + (1/√3)|1⟩

After Ry on q[0], state becomes: (1/√3)|100⟩ - √(2/3)|000⟩

Hmm, that doesn't seem right for creating a W state. Let me reconsider.

Actually wait, looking at the code more carefully:

After X(q[0]): |100⟩

After Ry(1.2310, q[0]): Let me compute more carefully.
θ = 1.2309594173407747 ≈ 2*arccos(1/√3)

State of q[0] after Ry applied to |1⟩:
= cos(θ/2)|1⟩ + sin(θ/2)|0⟩... no wait.

Ry(θ) = [[cos(θ/2), -sin(θ/2)], [sin(θ/2), cos(θ/2)]]

Applying to |0⟩ = [1, 0]^T:
Ry(θ)|0⟩ = [cos(θ/2), sin(θ/2)]^T = cos(θ/2)|0⟩ + sin(θ/2)|1⟩

Applying to |1⟩ = [0, 1]^T:
Ry(θ)|1⟩ = [-sin(θ/2), cos(θ/2)]^T = -sin(θ/2)|0⟩ + cos(θ/2)|1⟩

With cos(θ/2) = 1/√3 and sin(θ/2) = √(2/3):

Ry(θ)|1⟩ = -√(2/3)|0⟩ + (1/√3)|1⟩

So after Ry on q[0], the full state is:
-√(2/3)|000⟩ + (1/√3)|100⟩

4. nctrl X(q[0], q[1]): This is "not controlled" X, meaning X(q[1]) when q[0] is |0⟩.

When q[0]=|0⟩: X(q[1]) flips q[1]
When q[0]=|1⟩: nothing happens

So |000⟩ → |010⟩ (q[1] flipped) and |100⟩ → |100⟩

State becomes: -√(2/3)|010⟩ + (1/√3)|100⟩

5. ctrl Ry(1.5707963267949, q[1], q[2]): This is controlled-Ry(pi/2) with q[1] as control, q[2] as target.

When q[1]=

## isqTrain/1118

- task_id: `isqTrain/1118`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4341`

### Prompt

Write an isQ program that implements a variant of the superdense_coding pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement superdense coding of message '11' using qubits q[0] and q[1] with an expanded register of 4 qubits.

Qubits: 4 total (q[0], q[1] for protocol; q[2], q[3] idle in |0⟩). All measured.

State evolution:
1. Initial: |0000⟩
2. H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |000⟩
3. CNOT(q[0], q[1]): (|00⟩+|11⟩)/√2 ⊗ |00⟩ — Bell pair created
4. Z(q[0]): (|00⟩-|11⟩)/√2 ⊗ |00⟩
5. X(q[0]): (|10⟩-|01⟩)/√2 ⊗ |00⟩ — encoding of '11'
6. CNOT(q[0], q[1]): (|10⟩+|01⟩)/√2 ⊗ |00⟩ → (|10⟩-|01⟩)/√2 ⊗ |00⟩... Let me recalculate:
   - After Z then X on q[0]: phase flip then bit flip on first qubit of Bell state
   - Starting Bell: (|00⟩+|11⟩)/√2
   - After Z(q[0]): (|00⟩-|11⟩)/√2
   - After X(q[0]): (|10⟩-|01⟩)/√2
   - After CNOT(q[0],q[1]): |11⟩ ⊗ |00⟩
7. H(q[0]): |11⟩ ⊗ |00⟩ → wait, let me be more careful:
   - CNOT on (|10⟩-|01⟩)/√2: CNOT flips q[1] when q[0]=|1⟩, so |10⟩→|11⟩, |01⟩→|01⟩
   - Result: (|11⟩-|01⟩)/√2
   - H(q[0]): (H⊗I)((|11⟩-|01⟩)/√2) = (|01⟩+|11⟩-|01⟩+|11⟩)/2 = |11⟩

Final state: |1100⟩ with probability 1.0, as q[2] and q[3] remain untouched in |0⟩.

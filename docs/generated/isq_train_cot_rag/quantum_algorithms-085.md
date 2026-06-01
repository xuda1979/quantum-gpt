# ISQ training COT RAG corpus: quantum_algorithms shard 85

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2836

- task_id: `isqTrain/2836`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2251`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[1];
procedure main() {
    H(q[0]);
    S(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state is |0>. Applying the H gate transforms it to the superposition |+> = (1/sqrt(2))(|0> + |1>).
2. The S gate applies a phase of i to the |1> state, changing the state to (1/sqrt(2))(|0> + i|1>).
3. Measuring in the computational basis yields |0> with probability |1/sqrt(2)|^2 = 0.5 and |1> with probability |i/sqrt(2)|^2 = 0.5.

Predicted probability distribution: {'0': 0.5, '1': 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/4184

- task_id: `isqTrain/4184`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `4732`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.500, q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    Rz(2.0 * 0.500, q[2]);
    CNOT(q[1], q[2]);
    CNOT(q[0], q[2]);
    Rz(2.0 * 0.500, q[2]);
    CNOT(q[0], q[2]);
    Rx(2.0 * 1.000, q[0]);
    Rx(2.0 * 1.000, q[1]);
    Rx(2.0 * 1.000, q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

Let me analyze this quantum circuit step by step.

The circuit has 3 qubits q[0], q[1], q[2].

Initial state: |000>

Step 1: Apply H to all three qubits
H|0> = |+> = (|0> + |1>)/√2

State after H gates: |+>|+>|+> = (1/√8)(|000> + |001> + |010> + |011> + |100> + |101> + |110> + |111>)

Step 2: CNOT(q[0], q[1])
This is a controlled-NOT with q[0] as control and q[1] as target.

Step 3: Rz(2.0 * 0.500, q[1]) = Rz(1.0, q[1])
Rz(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]
Rz(1.0) = [[e^(-i/2), 0], [0, e^(i/2)]]

Wait, let me reconsider. The pattern CNOT, Rz, CNOT on a pair of qubits is equivalent to applying a ZZ interaction.

CNOT(q[0], q[1]) followed by Rz(θ, q[1]) followed by CNOT(q[0], q[1]) is equivalent to applying the gate exp(-iθ/2 Z⊗Z) up to some phase.

Actually, let me be more careful. The sequence CNOT-Rz(θ)-CNOT on (control, target) produces:
- CNOT maps |00> → |00>, |01> → |01>, |10> → |11>, |11> → |10>
- Then Rz(θ) on target: |00> → e^(-iθ/2)|00>, |01> → e^(iθ/2)|01>, |11> → e^(-iθ/2)|11>, |10> → e^(iθ/2)|10>
- Then CNOT again: |00> → |00>, |01> → |01>, |11> → |10>, |10> → |11>

So overall:
|00> → e^(-iθ/2)|00>
|01> → e^(iθ/2)|01>
|10> → e^(-iθ/2)|11> → e^(-iθ/2)|11> after second CNOT... wait let me redo this.

Let me trace through more carefully.

CNOT(q[0], q[1]): control=q[0], target=q[1]
- |00> → |00>
- |01> → |01>
- |10> → |11>
- |11> → |10>

Rz(θ, q[1]) on the target:
- |00> → e^(-iθ/2)|00>
- |01> → e^(iθ/2)|01>
- |11> → e^(-iθ/2)|11>
- |10> → e^(iθ/2)|10>

CNOT(q[0], q[1]):
- |00> → |00>
- |01> → |01>
- |11> → |10>
- |10> → |11>

So the full sequence CNOT-Rz(θ)-CNOT:
|00> → |00> → e^(-iθ/2)|00> → e^(-iθ/2)|00>
|01> → |01> → e^(iθ/2)|01> → e^(iθ/2)|01>
|10> → |11> → e^(-iθ/2)|11> → e^(-iθ/2)|10>
|11> → |10> → e^(iθ/2)|10> → e^(iθ/2)|11>

So this is ZZ rotation: exp(-iθ/2 * ZZ) up to global phase. More precisely:
|00> → e^(-iθ/2)|00>
|01> → e^(iθ/2)|01>
|10> → e^(-iθ/2)|10>
|11> → e^(iθ/2)|11>

This is exactly Rzz(θ) = exp(-iθ/2 * Z⊗Z).

Now in this circuit:
1. H on all qubits
2. CNOT(q[0], q[1]); Rz(1.0, q[1]); CNOT(q[0], q[1]) → Rzz(0.5) on q[0],q[1]
3. CNOT(q[1], q[2]); Rz

### Reference answer

Uniform distribution across 8 states

## isqQA/quantum_algorithms/116_application_scenario

- task_id: `isqQA/quantum_algorithms/116_application_scenario`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `application_scenario`, `algorithm`, `HHL的前提条件与限制`
- source: `qa_pipeline`
- dataset_index: `1258`

### Prompt

在量子机器学习和量子微分方程求解等前沿领域中，HHL（Harrow-Hassidim-Lloyd）算法常被寄予厚望，用以实现对大规模线性方程组 $Ax=b$ 求解的指数级加速。然而，在实际的工业与科研应用场景（如量子支持向量机、有限元分析）中，HHL算法的落地往往受制于其严苛的前提条件。请深入剖析HHL算法在实际应用中必须满足的矩阵条件（如稀疏性、条件数等）以及面临的I/O瓶颈，并结合一个具体的实际应用案例（如 QSVM 中的核矩阵求解），讨论这些限制如何影响其应用前景。此外，请使用 isQ 语言编写一段核心的量子线路代码，演示 HHL 算法中最关键的步骤之一：基于特征值的受控旋转（提取特征值倒数）的逻辑。

### Reference answer

HHL算法是量子线性系统求解的里程碑，理论上能够将求解 $Ax=b$ 的复杂度从经典的 $O(N \kappa^2)$ 降低至 $O(\log(N) \kappa^2 s^2 / \epsilon)$。然而，在实际应用场景中，我们必须深刻认识到其严苛的前提条件与物理限制。首先，矩阵 $A$ 必须是稀疏的（每行最多有 $s$ 个非零元素），并且能够被高效地模拟为哈密顿量；其次，$A$ 的条件数 $\kappa$ 不能过大，因为算法的运行时间与 $\kappa^2$ 成正比，如果 $\kappa$ 随系统规模指数级增长，量子优势将荡然无存。最后，最致命的瓶颈在于数据的输入与输出（I/O）：制备量子态 $|b\rangle$ 需要使用量子随机存取存储器（QRAM），这在目前的技术下极难实现；同时，读取完整的解向量 $|x\rangle$ 需要对量子态进行全息层析，这需要指数级重复测量，会彻底摧毁量子加速优势。因此，HHL 算法只能作为子程序应用于只需要提取解向量某些宏观特征（如内积、期望值）的场景中。以量子支持向量机（QSVM）为例，其核心是求解一个与核矩阵相关的线性系统。在这个应用中，HHL 的前景极具想象力但也充满挑战。QSVM 利用 HHL 算法快速求解支持向量，并直接在量子态空间中计算新数据点的分类期望，巧妙避开了读取完整向量 $|x\rangle$ 的 I/O 瓶颈。但现实限制是，数据集构建的核矩阵通常并不满足极小的条件数 $\kappa$，且为了保证稀疏性和高效的哈密顿量模拟，往往需要对矩阵进行复杂的量子预处理。这使得 QSVM 在近期量子设备上的表现往往不如经典算法。虽然 HHL 算法的物理实现遥不可及，但通过量子线路模拟其核心逻辑对于理解量子计算大有裨益。下面是使用 isQ 语言编写的 HHL 算法核心片段，演示了在提取到特征值后，如何通过受控旋转将特征值的倒数编码到辅助比特的振幅中。

<isq>
import std;

// 声明量子寄存器
// q_b[2]: 存储输入向量 b
// q_eigen[2]: 存储通过量子相位估计(QPE)提取的特征值
// q_anc: 辅助比特，用于编码特征值的倒数
qbit q_b[2];
qbit q_eigen[2];
qbit q_anc;

procedure main() {
    // 1. 初始化与态制备 (假设 |b> 已经制备在 q_b 中)
    // 此处省略具体的态制备线路

    // 2. 量子相位估计 (QPE)
    // 假设通过QPE，已经将矩阵A的特征值 lambda 编码到了 q_eigen 寄存器
    // 为了演示，我们用非门手动设置一个假定的特征值二进制状态 |10> (对应十进制2)
    X(q_eigen[1]);

    // 3. 受控旋转：提取特征值的倒数 1/lambda
    // 这是HHL算法中最核心的步骤，通过一系列多控门实现
    // R_y(theta) 旋转角度 theta 满足 sin(theta/2) = C/lambda，其中C为常数
    // 根据特征值寄存器的不同状态，对辅助比特施加不同角度的旋转
    
    // 当特征值处于 |01> 状态时 (lambda=1)
    // 使用负控制与正控制组合实现特定状态的受控旋转
    nctrl @[q_eigen[1]] ctrl @[q_eigen[0]] Ry(3.1415926, q_anc);

    // 当特征值处于 |10> 状态时 (lambda=2)
    ctrl @[q_eigen[1]] nctrl @[q_eigen[0]] Ry(1.5707963, q_anc);

    // 当特征值处于 |11> 状态时 (lambda=3)
    ctrl @[q_eigen[1]] ctrl @[q_eigen[0]] Ry(1.0471975, q_anc);

    // 4. 逆量子相位估计
    // 断开特征值寄存器与输入态的纠缠，恢复输入态
    // 逆操作需要撤销之前的特征值设置
    inv X(q_eigen[1]);

    // 5. 测量辅助比特
    // 如果测量结果为 1，则 q_b 寄存器塌缩为包含解向量 x 信息的量子态
    M(q_anc);
}
</isq>

## isqTrain/2733

- task_id: `isqTrain/2733`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_deriving_gate`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4652`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
defgate U0 = [
    1, 0, 0, 0, 0, 0, 0, 0;
    0, -1, 0, 0, 0, 0, 0, 0;
    0, 0, -1, 0, 0, 0, 0, 0;
    0, 0, 0, -1, 0, 0, 0, 0;
    0, 0, 0, 0, -1, 0, 0, 0;
    0, 0, 0, 0, 0, -1, 0, 0;
    0, 0, 0, 0, 0, 0, -1, 0;
    0, 0, 0, 0, 0, 0, 0, -1
];
oracle U_omega(3,1) = [0,1,0,0,0,0,0,0];
qbit q[3];
qbit anc;
int grover_search() {
    H(q);
    X(anc);
    H(anc);
    for i in 0:2 {
        U_omega(q[2], q[1], q[0], anc);
        H(q);
        U0(q[2], q[1], q[0]);
        H(q);
    }
    H(anc);
    X(anc);
    return M(q);
}
procedure main(){
    print grover_search();
}
```

### Chain-of-thought reasoning

The circuit implements Grover's search algorithm on 3 qubits with an ancilla qubit.

1. The oracle marks the state |001> (index 1 in the oracle definition [0,1,0,0,0,0,0,0]).
2. Initial state: |000>|0>
3. After H(q) and X(anc), H(anc): uniform superposition on q[0..2], ancilla in |->

The Grover iteration is applied 3 times.

For 3 qubits (N=8), the optimal number of iterations is approximately π/(4*arcsin(1/√8)) ≈ π/(4*0.3636) ≈ 2.16.

So with 3 iterations, we overshoot slightly.

Let me trace through more carefully.

After initialization:
|ψ> = (1/√8) Σ|x>|->

The oracle U_omega flips the sign of |001> (on the main qubits) using the ancilla. The ancilla stays in |-> throughout.

The diffusion operator (H ⊗ U0 ⊗ H) on the 3 main qubits where U0 has -1 on all but |000>, which is the standard Grover diffusion operator (it's I - 2|+><+| ... wait, let me check).

Actually, U0 = diag(1, -1, -1, -1, -1, -1, -1, -1) = Z⊗I⊗I... no wait, that's not right.

U0 applied to 3 qubits: it's |0><0|⊗I⊗I - (I⊗I⊗I - |0><0|⊗I⊗I) ... actually it's:
U0 = 2|000><000| - I (after accounting for global phase -1: U0 = -(I - 2|000><000|))

Hmm, let me reconsider. The standard diffusion operator is 2|s><s| - I where |s> = H^⊗3|000>.

H U0 H = H(2|000><000| - I)H... wait no.

U0 = diag(1,-1,-1,-1,-1,-1,-1,-1) 

Let me think of this differently. The standard Grover diffusion operator is:
D = 2|s><s| - I

In the computational basis, D_ij = 2/N - δ_ij for N=8.
D = (2/8)J - I = (1/4)J - I where J is the all-ones matrix.

But H D H = 2|000><000| - I... let's check.
H^⊗n (2|0>^⊗n <0|^⊗n - I) H^⊗n = 2(H|0>^⊗n)(<0|^⊗n H) - H^⊗n I H^⊗n = 2|s><s| - I ✓

So H U0 H where U0 = diag(1,-1,-1,...,-1) = 2|000><000| - I.

So H U0 H = 2|s><s| - I = D. ✓

Good, so the Grover iteration is: Oracle then Diffusion.

For N=8, target state |t> = |001>:
- θ = arcsin(1/√8) ≈ 0.3614 rad
- Optimal iterations: (π/2 - θ)/(2θ) ≈ (1.5708 - 0.3614)/0.7228 ≈ 1.673

So optimal is between 1 and 2. With 3 iterations, we overshoot.

After k iterations:
|ψ_k> = sin((2k+1)θ)|t> + cos((2k+1)θ)|s'>/√7

where |s'> is the uniform superposition of non-target states.

After 3 iterations:
(2·3+1)θ = 7θ ≈ 7·0.3614 ≈ 2.530 rad
sin(7θ) = sin(2.530) ≈ sin(2.530) 

Let me compute more precisely.

θ = arcsin(1/√8)

sin(θ) = 1/√8
cos(θ) = √(7/8)

We can use the Grover amplitude formulas.

After k iterations, the amplitude of the target state is:
a_k = sin((2k+1)θ)

For k=3:
(2·3+1)θ = 7θ

Using Chebyshev-like recurrences or direct computation:

sin(3θ) = 3sinθ -

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/4534

- task_id: `isqTrain/4534`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_inv`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4933`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;
qbit q[2];

procedure main() {
    
    H(q[1]); T(q[1]);
    
    
    H(q[0]);
    
    CNOT(q[0], q[1]);
    inv T(q[1]);
    CNOT(q[0], q[1]);
    
    H(q[0]);
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Input: An isQ quantum program.
    *   Output: Step-by-step reasoning using Dirac notation, probability distribution prediction, and specific formatting rules (starts with "## Circuit Analysis", ends with the predicted distribution, no code blocks, concise).

2.  **Analyze the isQ Program:**
    *   `qbit q[2];` -> Initialize 2 qubits: $|00\rangle$
    *   `H(q[1]); T(q[1]);` -> $|0\rangle \otimes (T H |0\rangle) = |0\rangle \otimes T |+\rangle$.
        *   $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
        *   $T|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + e^{i\pi/4}|1\rangle)$. Let's call this $|\psi_1\rangle$.
    *   `H(q[0]);` -> $|+\rangle \otimes |\psi_1\rangle$.
        *   $= \frac{1}{2}(|00\rangle + e^{i\pi/4}|01\rangle + |10\rangle + e^{i\pi/4}|11\rangle)$.
    *   `CNOT(q[0], q[1]);` -> Control $q_0$, target $q_1$.
        *   $|00\rangle \to |00\rangle$
        *   $|01\rangle \to |01\rangle$
        *   $|10\rangle \to |11\rangle$
        *   $|11\rangle \to |10\rangle$
        *   State becomes: $\frac{1}{2}(|00\rangle + e^{i\pi/4}|01\rangle + e^{i\pi/4}|10\rangle + |11\rangle)$.
    *   `inv T(q[1]);` -> $T^\dagger$ on $q_1$.
        *   $T^\dagger|0\rangle = |0\rangle$, $T^\dagger|1\rangle = e^{-i\pi/4}|1\rangle$.
        *   State becomes: $\frac{1}{2}(|00\rangle + |01\rangle + e^{i\pi/4}e^{-i\pi/4}|10\rangle + e^{-i\pi/4}|11\rangle)$
        *   $= \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + e^{-i\pi/4}|11\rangle)$.
    *   `CNOT(q[0], q[1]);`
        *   $|00\rangle \to |00\rangle$
        *   $|01\rangle \to |01\rangle$
        *   $|10\rangle \to |11\rangle$
        *   $|11\rangle \to |10\rangle$
        *   State becomes: $\frac{1}{2}(|00\rangle + |01\rangle + e^{-i\pi/4}|10\rangle + |11\rangle)$.
        *   Wait, let me re-check CNOT(q0, q1):
            *   `inv T(q[1])` applied to $\frac{1}{2}(|00\rangle + e^{i\pi/4}|01\rangle + e^{i\pi/4}|10\rangle + |11\rangle)$:
                *   For $|00\rangle$ -> $|00\rangle$
                *   For $|01\rangle$ -> $e^{-i\pi/4}|01\rangle$
                *   For $|10\rangle$ -> $|10\rangle$
                *   For $|11\rangle$ -> $e^{-i\pi/4}|11\rangle$
                *   So state is $\frac{1}{2}(|00\rangle + e^{i\pi/4}e^{-i\pi/4}|01\rangle + e^{i\pi/4}|10\rangle + e^{-i\pi/4}|11\rangle)$
                *   $= \frac{1}{2}(|00\rangle + |01\rangle + e^{i\pi/4}|10\rangle + e^{-i\pi/4}|11\rangle)$.
            *   Now second CNOT:
                *   $|00\rangle \to |00\rangle$
                *   $|01\rangle \to |01\rangle$
                *   $e^{i\pi/

### Reference answer

{'predicted_probs': {'00': 0.073223, '01': 0.073223, '10': 0.426777, '11': 0.426777}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.0732, P(|01>) = 0.0732, P(|10>) = 0.4268, P(|11>) = 0.4268.'}

## isqTrain/2723

- task_id: `isqTrain/2723`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_if_else`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3263`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
bool m1, m2;
qbit q_1, q_2, q_3;
procedure Teleport(qbit qsrc, qbit qanc, qbit qdest) 
{
    H(qanc);
    CNOT(qanc, qdest);
    CNOT(qsrc, qanc);
    H(qsrc);
    m1 = M(qsrc);
    m2 = M(qanc);
    if (m2) { X(qdest); }
    if (m1) { Z(qdest); }
}
procedure main()
{
    X(q_1);
    Teleport(q_1, q_2, q_3);
    print M(q_3);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task type: `output_prediction`
    *   Input: An isQ quantum program implementing a standard quantum teleportation circuit.
    *   Goal: Trace the program, explain operations and state evolution, and predict measurement probabilities in a JSON array format (or JSON array as part of the predicted output, but wait, the prompt says "Return a JSON array" for the probabilities. The instructions say "Output ONLY the analysis, starting with '## Circuit Analysis'". I will stick to the format requested).
    *   The predicted output format: The system prompt says "Output ONLY the analysis, starting with '## Circuit Analysis'... End with the predicted probability distribution". I will output the analysis and conclude with the JSON array.

2.  **Analyze the Circuit:**
    *   Initialization: `q_1, q_2, q_3` start in `|000>`.
    *   `X(q_1)`: state becomes `|100>`.
    *   `Teleport(q_1, q_2, q_3)`:
        *   `H(q_2)`: state becomes `|100> + |110>`.
        *   `CNOT(q_2, q_3)`: state becomes `|100> + |111>`.
        *   `CNOT(q_1, q_2)`: state becomes `|100> + |101>`. Wait.
            Let's carefully trace:
            |q1, q2, q3>
            Init: |000>
            X(q1): |100>
            H(q2): 1/sqrt(2) * (|100> + |110>)
            CNOT(q2, q3): 1/sqrt(2) * (|100> + |111>)
            CNOT(q1, q2): 1/sqrt(2) * (|110> + |101>) -> Wait, let me re-evaluate.
            CNOT(q1, q2) flips q2 if q1 is 1. Both |100> and |111> have q1=1.
            |100> -> |110>
            |111> -> |101>
            So state is 1/sqrt(2) * (|110> + |101>).
            H(q1): H acts on q1.
            |110> = |1>_q1 |10>_q2q3 -> H|1>|10> = 1/sqrt(2) * (|0> - |1>) |10> = 1/sqrt(2) * (|010> - |110>)
            |101> = |1>_q1 |01>_q2q3 -> H|1>|01> = 1/sqrt(2) * (|0> - |1>) |01> = 1/sqrt(2) * (|001> - |101>)
            Combined state: 1/2 * (|001> + |010> - |101> - |110>).
            Wait, let me double check the standard teleportation circuit.
            Source is q1, Ancilla is q2, Dest is q3.
            Initial source state: |1>. (Because X(q1))
            H(q2) -> |100> + |110>
            CNOT(q2, q3) -> |100> + |111>
            CNOT(q1, q2) -> |110> + |101>
            H(q1) -> (H|1>)(|10>) + (H|1>)(|01>) = 1/sqrt(2) (|0> - |1>) |10> + 1/sqrt(2) (|0> - |1>) |01>
                   = 1/2 (|010> - |110> + |001> - |101>)
        *   Measurements:
            `m1 = M(qsrc)` (qsrc = q1)
            `m2 = M(qanc)` (qanc = q2)
            Probabilities of (q1, q2, q3) combinations:
            |010> -> q1=0, q2=1, q3=0 => prob 0.25
            |110> -> q1=1, q2=1, q3=0 => prob 0.25
            |001> -> q1=0, q2=0, q3=1 => prob 0.25
            |101> -> q1=1, q2=0, q3=1 => prob 0.25
            Wait, what about the corrections?
            If m2=1, X(q3). If m1=1, Z(q3).
            Let's trace each case:
            Case 1: q1=

### Reference answer

{'predicted_probs': {'001': 0.25, '010': 0.25, '101': 0.25, '110': 0.25}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqQA/quantum_algorithms/134_application_scenario

- task_id: `isqQA/quantum_algorithms/134_application_scenario`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `application_scenario`, `algorithm`, `量子递增/递减电路`
- source: `qa_pipeline`
- dataset_index: `1990`

### Prompt

在量子算法设计中，量子递增和量子递减电路不仅仅是基础的算术操作，它们在哪些实际的量子算法或高级应用场景中发挥着关键作用？请详细阐述其应用前景，并使用 isQ 语言实现一个针对2个量子位寄存器的量子递增电路。

### Reference answer

<thought>
推理过程：
1. 分析量子递增/递减电路的本质：它是在量子寄存器上实现模加法的基石，即状态 |x> 变为 |x+1> 或 |x-1>。
2. 梳理实际应用场景：
   - 量子游走：条件平移操作（S）是核心，本质上就是对位置寄存器进行条件递增或递减，以实现比经典随机游走更快的搜索和混洗。
   - 哈密顿量模拟与量子化学计算：在实现量子傅里叶变换加法的相位估计中，控制递增操作常用于构建受控算术逻辑。
   - 量子机器学习：在量子线性系统算法（如HHL）及其变体中，频繁需要用到算术运算来计算内存地址或更新参数索引，递增/递减电路是这些底层模块的基础。
   - Grover算法的广义变体：在寻找多个目标或动态数据库更新时，可能需要使用递增电路来修改预言机中的辅助计数器。
3. 展望前景：随着容错量子计算的推进，高效的算术电路（如基于傅里叶变换或进位前瞻的递增器）将成为量子软件编译器中的标准库函数。
4. 编写 isQ 代码：对于2量子位 |q1 q0>，实现递增（+1）。逻辑上，最低位 q0 每次必翻转（X门）；高位 q1 仅在低位全为1（即q0=1）时翻转。标准步骤：先对低位施加CNOT进位，最后翻转低位。
</thought>

量子递增和量子递减电路在量子计算中扮演着类似于经典计算机中算术逻辑单元（ALU）的基础核心角色，其应用场景和前景十分广阔：

1. **量子游走**：这是最典型的应用之一。在量子游走算法中，系统的状态由位置空间和硬币空间组成。游走的演化需要对位置状态进行条件平移，这本质上就是根据硬币的状态对位置寄存器执行量子递增或量子递减操作。这种机制在构建量子搜索算法、图遍历算法以及证明量子计算优越性方面发挥了关键作用。

2. **哈密顿量模拟与量子化学计算**：在模拟复杂分子或材料的电子结构时，通常需要将哈密顿量分解为一系列基本的酉操作。在某些编码方案和算法（如基于量子傅里叶变换的加法器）中，控制寄存器或状态寄存器的递增与递减是实现时间演化算符和相位梯度不可或缺的组件。

3. **机器学习与数据结构索引**：在未来的量子机器学习算法中，处理量子随机存取存储器或动态更新参数索引时，需要用到量子算术运算。量子递增器可以作为基础的计数器，用于遍历叠加态下的数据索引，极大地加速如量子最近邻搜索、量子支持向量机等算法的数据处理流程。

4. **应用前景**：随着量子硬件向容错阶段迈进，经典算法中的复杂控制流将逐渐被量子化。量子递增/递减电路作为算术运算的最简形式，将与量子加法器、乘法器一起，成为量子编译器底层指令集的标准原语。优化这些电路的深度和辅助量子比特消耗，是目前量子算法理论研究的重要商业化前沿。

下面是使用 isQ 语言实现的一个针对2个量子位（N=2）寄存器的量子递增电路示例。对于2个量子比特，要实现状态加1，逻辑是对低位执行X门，并在低位为1时对高位执行X门（等效于CNOT）：

```isq
import std;

qbit q[2];

procedure main() {
    // 初始化寄存器为均匀叠加态，以演示并行递增
    for i in 0:2 {
        H(q[i]);
    }
    
    // 开始执行量子递增操作 (+1)
    // 在二进制中，如果低位 q[0] 为 1，则需要向高位 q[1] 进位
    // 如果低位 q[0] 为 0，则高位 q[1] 保持不变
    // 因此，使用 q[0] 控制 q[1] 翻转
    CNOT(q[0], q[1]);
    
    // 处理最低位，任何情况都翻转，实现 0->1 或 1->0（进位后）
    X(q[0]);
    
    // 此时所有基态的数值均完成了 +1 操作
}
```

## isqTrain/4132

- task_id: `isqTrain/4132`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `541`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[4];

procedure main() {
    X(q[3]);
    H(q[0]); H(q[1]); H(q[2]);
    ctrl Rz(2.0 * 3.14159265358979 * 3.0 / 8.0 * 1.0, q[0], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 3.0 / 8.0 * 2.0, q[1], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 3.0 / 8.0 * 4.0, q[2], q[3]);
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

The input state is $|0000\rangle$. 
The circuit applies:
1. `X(q[3])`: qubit q[3] becomes $|1\rangle$. The state is $|0001\rangle$.
2. `H(q[0]); H(q[1]); H(q[2])`: The state becomes $\frac{1}{\sqrt{8}} \sum_{x=0}^3 |x\rangle \otimes |1\rangle$.
3. The next three gates are `ctrl Rz(2 \pi * 3/8 * 1.0, q[0], q[3])`, etc.
Notice that q[3] is the target of the Rz rotations, controlled by q[0], q[1], and q[2].
Wait, Rz is applied to q[3]. Since q[3] is in $|1\rangle$, applying `ctrl Rz(\theta, q[k], q[3])` is effectively applying a phase to $|1\rangle$ on q[3]. But the control is on q[k].
Actually, a `ctrl Rz(\theta)` gate applies the phase $e^{-i\theta/2}$ to $|11\rangle$ and $e^{i\theta/2}$ to $|10\rangle$, but in standard isQ definition, `ctrl Rz(\theta, c, t)` applies $e^{-i\theta/2}$ to $|11\rangle$ and $e^{i\theta/2}$ to $|01\rangle$? Wait. 
Usually, `Rz(\theta) = \begin{pmatrix} 1 & 0 \\ 0 & e^{i\theta} \end{pmatrix}` or something. In isQ, `Rz(theta) = exp(-i theta/2 Z)`.
Let's look closely at the controlled phase logic.
Wait, if q[3] is in $|1\rangle$, applying `ctrl Rz(\theta)` to q[3] controlled by q[k] means if q[k] is $|1\rangle$, q[3] gets `Rz(\theta)`. But `Rz(\theta)` applied to $|1\rangle$ yields $e^{-i\theta/2} |1\rangle$.
Since this is applied for q[0], q[1], q[2] with different angles, it acts exactly like a QFT or QPE in reverse!
Wait, the state before the controlled Rz gates is $|+\rangle|+\rangle|+\rangle|1\rangle$.
The Rz angles are:
k=0: $2\pi \times \frac{3}{8} \times 1.0 = \frac{3\pi}{4}$
k=1: $2\pi \times \frac{3}{8} \times 2.0 = \frac{3\pi}{2}$
k=2: $2\pi \times \frac{3}{8} \times 4.0 = 3\pi$

Applying these controlled rotations on q[3] from q[0], q[1], q[2].
Because q[3] is $|1\rangle$, applying `ctrl Rz(\theta)` on q[3] controlled by q[k] effectively introduces a phase of $-\theta/2$ for $|1\rangle_k |1\rangle_3$ and $\theta/2$ for $|0\rangle_k |1\rangle_3$.
Wait, `Rz(\theta)` is diagonal in the Z basis. `Rz(\theta) |1\rangle = e^{-i\theta/2} |1\rangle`.
Wait, if we have control q[k] and target q[3], the matrix is $|0\rangle\langle0| \otimes I + |1\rangle\langle1| \otimes Rz(\theta)$.
Applying this to $|0\rangle_k |1\rangle_3$ gives $|0\rangle_k |1\rangle_3$.
Applying this to $|1\rangle_k |1\rangle_3$ gives $e^{-i\theta/2} |1\rangle_k |1\rangle_3$.
Wait! This is a phase on the control qubit!
Actually, the global phase or the state can be written as:
$|x_2 x_1 x_0\rangle_{{0,1,2}} \otimes |1\rangle_3$ gets a phase $\exp(-i \frac{\theta_0}{2} x_0) \exp(-i \frac{\theta_1}{2} x_1) \exp(-i \frac{\theta_2}{2} x

### Reference answer

Dominant output states: |0101> with probability ~0.43 each

## isqTrain/2023

- task_id: `isqTrain/2023`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4664`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;
qbit q[5];
procedure main() {
    X(q[0]);
    X(q[2]); X(q[3]);
    ctrl ctrl X(q[0], q[2], q[4]);
    ctrl ctrl X(q[1], q[3], q[4]);
    M(q[4]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state is |00000⟩.
2. `X(q[0])`, `X(q[2])`, and `X(q[3])` flip the respective qubits, changing the state to |10110⟩.
3. `ctrl ctrl X(q[0], q[2], q[4])` applies a Toffoli gate. Since q[0] and q[2] are in |1⟩, target q[4] is flipped, updating the state to |10111⟩.
4. `ctrl ctrl X(q[1], q[3], q[4])` applies another Toffoli gate. Since control q[1] is in |0⟩, the condition is not met and q[4] remains unchanged.
5. The final state of q[4] before measurement is |1⟩.

Predicted probability distribution: {'1': 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'IP([1,0],[1,1])=1: P(|1>)=1.0.'}

## isqQA/quantum_algorithms/125_hardware_limitations

- task_id: `isqQA/quantum_algorithms/125_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `hardware_limitations`, `algorithm`, `相位回踢机制`
- source: `qa_pipeline`
- dataset_index: `4818`

### Prompt

在目前的NISQ（含噪中等规模量子）设备中，量子比特极易受到环境噪声的干扰而发生退相干。相位回踢作为量子相位估计（QPE）等核心算法的基础机制，其性能会受到硬件退相干的哪些严重影响？在实际的量子线路设计中，我们应当如何结合算法优化与isQ代码实现来缓解这些硬件局限性？

### Reference answer

在量子计算中，相位回踢机制通过受控酉操作将目标量子态的特征值相位转移到控制寄存器上，是量子相位估计（QPE）和Shor算法的核心。然而，在NISQ设备中，这一机制面临严重的硬件局限性。首先，量子比特的退相干时间（如T1弛豫时间和T2去相位时间）极其有限。随着控制比特数量的增加，标准QPE线路深度呈指数级增长，长时间的受控纠缠操作会导致量子态在获得完整相位回踢之前就因退相干而失去量子相干性，严重破坏算法的成功概率。其次，NISQ设备中受控门（如CNOT、Toffoli）的错误率远高于单量子比特门，多层嵌套的控制操作会累积大量系统误差，导致回踢的相位值不准确。

为了缓解退相干和门误差的影响，在系统层面可以采用半经典相位估计或迭代式相位估计（IQPE）策略。这种方法每次只使用一个控制比特，通过经典反馈控制后续的单比特旋转，从而大幅减少同一时刻处于纠缠态的量子比特数量，有效缩短了线路深度。

下面展示如何使用isQ语言实现一种改进的、低纠缠深度的简化相位回踢验证线路。在此代码中，我们通过减少不必要的嵌套控制，并使用单比特旋转结合经典测量的方式，来降低退相干带来的负面影响：

```isq
import std;

qbit ctrl[1];
qbit target[1];

procedure main() {
    // 初始化控制比特为 |+> 态
    H(ctrl[0]);

    // 初始化目标比特，假设处于 |1> 态
    X(target[0]);

    // 模拟特征值为 e^(i*pi/2) 的酉操作 (相当于特征相位 theta = pi/2)
    // 这里的受控操作是 ctr-S 门
    // 在实际硬件中，直接执行复杂的受控门会引入较大噪声
    // 利用优化结构，将受控相位转化为单比特旋转
    // 当目标比特为 |1> 时，相位回踢要求控制比特获得 pi/2 的相位
    
    // 为了缓解硬件噪声，我们减少受控门的深度
    // 这里执行等效的受控相位门
    ctrl @[ctrl[0]] S(target[0]);

    // 施加反向旋转以验证回踢的相位
    // 如果回踢准确，控制比特将回到基态
    Rz(-PI/2, ctrl[0]);
    H(ctrl[0]);

    // 测量控制比特
    // 理想无噪声情况下，由于相位被精确抵消，测量结果应为 0
    // 在NISQ设备中，通过缩短此等效线路的深度来抵抗退相干
    int r = M(ctrl[0]);
}
```

在上述isQ代码实现中，我们将复杂的多次受控操作简化为单次受控相位回踢，并结合了单量子比特的Rz旋转抵消。这种浅层线路架构能最大限度地降低退相干效应，同时减少CNOT等高错误率双比特门的数量，使得相位回踢机制在当前的NISQ硬件上依然能够提取出具有一定置信度的相位信息。

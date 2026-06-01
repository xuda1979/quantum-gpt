# ISQ training COT RAG corpus: quantum_algorithms shard 185

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4051

- task_id: `isqTrain/4051`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `672`

### Prompt

Debug this isQ program — it gives unexpected measurement results.

```
import std;
// QFT on 3 qubits with input state |000>
qbit q[3];

procedure main() {
    // Prepare input state |000>

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

Let me analyze this bug in the 3-qubit QFT circuit.

The QFT on 3 qubits should transform |000⟩ to an equal superposition of all 8 states, each with probability 1/8 = 0.125.

The QFT circuit structure for qubit k involves:
1. H gate on qubit k
2. Controlled R_k+1 rotations from qubit k+1 to qubit k
3. Controlled R_k+2 rotations from qubit k+2 to qubit k, etc.

For a 3-qubit QFT:
- Qubit 0: H(q[0]), then CR_2(q[1], q[0]), then CR_3(q[2], q[0])
- Qubit 1: H(q[1]), then CR_2(q[2], q[1])
- Qubit 2: H(q[2])
- Then swap q[0] and q[2]

The rotation gates are:
- R_2 = Rz(2π/2) = Rz(π)
- R_3 = Rz(2π/2²) = Rz(π/2)

Looking at the buggy code:

This computes: 2.0 * 2.0 * π / 4.0 = 4.0 * π / 4.0 = π

But for QFT, the controlled rotation from q[1] to q[0] should be R_2 = Rz(2π/2²) = Rz(π/2)

Wait, let me reconsider. The standard QFT uses rotations R_k = Rz(2π/2^k).

For the stage processing qubit 0:
- After H(q[0]), q[0] is in |+⟩
- CR_2 from q[1] to q[0] applies Rz(2π/4) = Rz(π/2)
- CR_3 from q[2] to q[0] applies Rz(2π/8) = Rz(π/4)

The buggy code has:
- `ctrl Rz(2.0 * 2.0 * 3.14159265358979 / 4.0, q[1], q[0])` = Rz(4π/4) = Rz(π) — WRONG
- `ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0])` = Rz(2π/8) = Rz(π/4) — correct

The fixed code has:
- `ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0])` = Rz(2π/4) = Rz(π/2) — correct
- `ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0])` = Rz(2π/8) = Rz(π/4) — correct

So the bug is in the first controlled rotation: there's an extra `2.0 *` factor, making it Rz(π) instead of Rz(π/2).

Now for the state evolution of the corrected circuit:

Starting: |000⟩

Stage for qubit 0:
- H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |00⟩ = (|000⟩+|100⟩)/√2
- CRz(π/2) from q[1] to q[0]: Since q[1] is |0⟩, nothing changes. State: (|000⟩+|100⟩)/√2
- CRz(π/4) from q[2] to q[0]: Since q[2] is |0⟩, nothing changes. State: (|000⟩+|100⟩)/√2

Stage for qubit 1:
- H(q[1]): (|000⟩+|010⟩+|100⟩+|110⟩)/2
- CRz(π/2) from q[2] to q[1]: Since q[2] is |0⟩, nothing changes. State: (|000⟩+|010⟩+|100⟩+|110⟩)/2

Stage for qubit 2:
- H(q[2]): (|000⟩+|001⟩+|010⟩+|011⟩+|100

## isqQA/quantum_algorithms/97_hardware_limitations

- task_id: `isqQA/quantum_algorithms/97_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `hardware_limitations`, `algorithm`, `Grover最优迭代次数推导`
- source: `qa_pipeline`
- dataset_index: `3330`

### Prompt

在理想的量子计算模型中，Grover搜索算法达到最大成功概率的理论最优迭代次数为 $k_{opt} \approx \frac{\pi}{4}\sqrt{N/M}$。然而，在当前的NISQ（含噪声中等规模量子）设备中，量子比特受限于有限的退相干时间（$T_1, T_2$）和门操作误差。请推导在考虑量子态指数级退相干衰减（例如每次Grover迭代引入固定的保真度衰减因子 $p$）的情况下，实际获得最大期望成功概率的最优迭代次数 $k_{real}$ 应当如何修正？并请使用isQ语言编写一个针对3比特寻找目标态 $|111\rangle$ 的Grover算法代码，结合上述推导结论，说明在程序中如何利用经典计算得出的实际最优迭代次数来控制量子线路的执行。

### Reference answer

<think...
1. 数学推导...
理想情况下：...
引入噪声：...
求极值：...
2. isQ代码...
</think...
在NISQ（含噪声中等规模量子）设备中，量子比特的退相干效应和量子门的不完美执行会导致系统的保真度随电路深度呈指数级下降。这对Grover算法的最优迭代次数有直接影响。

### 数学推导：退相干下的最优迭代次数
在理想的Grover算法中，经过 $k$ 次迭代后，测量得到正确目标态的概率为：
$$P_{ideal}(k) = \sin^2((2k+1)\theta)$$
其中 $\sin\theta = \sqrt{M/N}$，$N$ 是搜索空间大小，$M$ 是目标解数量。

在真实的NISQ设备中，我们假设每次Grover迭代（包括Oracle和扩散算子）由于退相干和门错误引入固定的保真度衰减因子 $p$ ($0 < p < 1$)。这意味着每经过一次迭代，正确态的概率幅度会额外乘以一个衰减因子 $p$。因此，实际的成功概率模型修正为：
$$P_{real}(k) = p^k \sin^2((2k+1)\theta)$$
为了找到在退相干影响下的实际最优迭代次数 $k_{real}$，我们需要对 $P_{real}(k)$ 求关于 $k$ 的导数并令其等于0（将近似连续化处理以求极值）：
$$\frac{d}{dk} \left[ p^k \sin^2((2k+1)\theta) \right] = 0$$
利用乘积求导法则和 $p^k = e^{k \ln p}$，导数展开为：
$$p^k \ln(p) \sin^2((2k+1)\theta) + p^k \cdot 2\theta \sin(2(2k+1)\theta) = 0$$
消去非零项 $p^k$，并令 $\alpha = (2k+1)\theta$，得到：
$$\ln(p) \sin^2(\alpha) + 2\theta \sin(2\alpha) = 0$$
利用倍角公式 $\sin(2\alpha) = 2\sin(\alpha)\cos(\alpha)$，方程化简为：
$$\ln(p) \sin(\alpha) + 4\theta \cos(\alpha) = 0$$
由此解得：
$$\tan(\alpha) = -\frac{4\theta}{\ln(p)}$$
因为 $0 < p < 1$，所以 $\ln(p) < 0$。设 $\lambda = -\ln(p) > 0$ 代表衰减率，则：
$$\alpha_{real} = \arctan\left(\frac{4\theta}{\lambda}\right)$$
在无噪声理想情况下（$p \to 1, \lambda \to 0$），$\alpha_{real} \to \pi/2$，此时 $k_{opt} \approx \frac{\pi/2 - \theta}{2\theta} \approx \frac{\pi}{4\theta}$。而在NISQ设备中，由于 $\lambda > 0$，实际达到最大概率的旋转角度 $\alpha_{real}$ 会小于 $\pi/2$。因此，硬件局限修正后的实际最优迭代次数为：
$$k_{real} = \frac{\arctan(\frac{4\theta}{\lambda}) - \theta}{2\theta}$$
这说明在退相干环境下，继续增加迭代次数不仅不会增加成功率，反而会因为噪声积累导致成功率急剧下降。

### isQ 代码实现
在下面的isQ代码中，我们以3比特（$N=8$）搜索1个目标态（$|111\rangle$, $M=1$）为例。理论最优迭代 $k_{opt} \approx 1.96$（即2次）。如果设备存在显著退相干，利用上述推导计算出的实际最优迭代次数可能会小于2（例如计算得 $k_{real} = 1$）。我们在代码中通过经典变量 `k_real` 来动态控制量子循环的次数。

```isq
import std;

// 全局声明3个量子比特
qbit q[3];

// 标记目标态 |111> 的Oracle
procedure oracle() {
    // 使用Hadamard将控制位上的Z翻转转化为X翻转
    H(q[2]);
    // 执行多位控制Z门（等价于控制相位翻转），此处拆解为Toffoli门
    Toffoli(q[0], q[1], q[2]);
    H(q[2]);
}

// 扩散算子
procedure diffusion() {
    for i in 0:3 {
        H(q[i]);
        X(q[i]);
    }
    H(q[2]);
    Toffoli(q[0], q[1], q[2]);
    H(q[2]);
    for i in 0:3 {
        X(q[i]);
        H(q[i]);
    }
}

procedure main() {
    // 第一步：初始化叠加态
    for i in 0:3 {
        H(q[i]);
    }

    // 第二步：根据硬件退相干模型推导出的实际最优迭代次数
    // 此处假设通过上述公式推导，在当前的NISQ硬件参数下，衰减使得 k_real = 1
    int k_real = 1; 

    // 第三步：执行受限于硬件真实承受能力的Grover迭代
    for i in 0:k_real {
        oracle();
        diffusion();
    }

    // 第四步：测量量子寄存器
    for i in 0:3 {
        M(q[i]);
    }
}
```
在上述代码实现中，通过将理论推导获得的实际最优迭代层数作为经典循环的边界条件，程序有效避免了因过量迭代导致的量子态退相干积累，从而在NISQ硬件上获得了更高的真实测量保真度。

## isqTrain/2022

- task_id: `isqTrain/2022`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3220`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[3];
procedure main() {
    X(q[0]);
    X(q[0]); X(q[1]);
    ctrl ctrl X(q[0], q[1], q[2]);
    X(q[0]); X(q[1]);
    X(q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial state**: |000>
2. `X(q[0])`: flips q0. State is |100>.
3. `X(q[0]); X(q[1]);`: flips q0 back to |0> and q1 to |1>. State is |010>.
4. `ctrl ctrl X(q[0], q[1], q[2])` (Toffoli): requires both q0 and q1 to be |1>. Since q0 is |0>, the target q2 is unchanged. State remains |010>.
5. `X(q[0]); X(q[1]);`: flips q0 and q1 back. State is |000>.
6. `X(q[2])`: flips q2 to |1>. Final state before measurement is |101>.
7. **Probabilities**: P(101) = 1.0

### Reference answer

{'predicted_probs': {'101': 1.0}, 'explanation': 'OR(1,0)=1: final state |101>, index 5 has P=1.0.'}

## isqTrain/963

- task_id: `isqTrain/963`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `hamiltonian_simulation`, `isq_syntax_ctrl_nctrl`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `771`

### Prompt

Implement the following in isQ: implements the pauli_evolution pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

Let me analyze this isQ program step by step.

The goal is to implement a Pauli evolution e^(-iθZZ) using an alternative gate decomposition (H CZ H instead of CNOT) and verify it produces the same output.

Starting state: |00⟩
After X(q[1]): |01⟩

Now the e^(-iπ/4 ZZ) decomposition:
- Standard decomposition: CNOT(q[0], q[1]) → Rz(2θ, q[1]) → CNOT(q[0], q[1])
- Alternative: H(q[1]) → CZ(q[0], q[1]) → H(q[1]) → Rz(2θ, q[1]) → H(q[1]) → CZ(q[0], q[1]) → H(q[1])

This is because CNOT = (I ⊗ H) CZ (I ⊗ H), so:
- CNOT = H(target) CZ(control, target) H(target)

Let me trace through:

1. Start: |01⟩

2. H(q[1]): |0⟩ ⊗ H|1⟩ = |0⟩ ⊗ |−⟩ = |0−⟩

3. CZ(q[0], q[1]): CZ applies Z to q[1] when q[0] is |1⟩. Since q[0] is |0⟩, nothing happens: |0−⟩

4. H(q[1]): |01⟩ (H|−⟩ = |1⟩)

5. Rz(π/2, q[1]): This adds a phase. Rz(π/2)|1⟩ = e^(-iπ/4)|1⟩ = e^(-iπ/4)|01⟩

Wait, let me reconsider. The |01⟩ state is an eigenstate of ZZ with eigenvalue -1.

ZZ = Z ⊗ Z
ZZ|01⟩ = (Z|0⟩) ⊗ (Z|1⟩) = |0⟩ ⊗ (-|1⟩) = -|01⟩

So |01⟩ is an eigenstate of ZZ with eigenvalue -1.

e^(-iθZZ)|01⟩ = e^(iθ)|01⟩

For θ = π/4: e^(iπ/4)|01⟩

This is just a global phase, so the measurement probabilities are still {|01⟩: 1.0}.

Let me trace more carefully:

H(q[1]) on |01⟩:
|0⟩ ⊗ (H|1⟩) = |0⟩ ⊗ (1/√2)(|0⟩ - |1⟩) = (1/√2)(|00⟩ - |01⟩)

CZ(q[0], q[1]):
CZ|00⟩ = |00⟩
CZ|01⟩ = |01⟩ (control q[0] is |0⟩, so no Z applied)
Wait, CZ applies Z to target when control is |1⟩.

So for CZ(q[0], q[1]):
- When q[0] = |1⟩, apply Z to q[1]
- When q[0] = |0⟩, nothing happens

CZ(1/√2)(|00⟩ - |01⟩) = (1/√2)(|00⟩ - |01⟩) (since q[0] is always |0⟩ in both terms)

H(q[1]) on (1/√2)(|00⟩ - |01⟩):
= (1/√2)(|0⟩⊗H|0⟩ - |0⟩⊗H|1⟩)
= (1/√2)(|0⟩⊗|+⟩ - |0⟩⊗|−⟩)
= (1/√2)|0⟩ ⊗ (|+⟩ - |−⟩)
= (1/√2)|0⟩ ⊗ (1/√2)((|0⟩+|1⟩) - (|0⟩-|1⟩))
= (1/√2)|0⟩ ⊗ (1/√2)(2|1⟩)
= (1/√2)|0⟩ ⊗ √2|1⟩
= |01⟩

Rz(π/2, q[1]):
Rz(π/2)|1⟩ = e^(-iπ/4)|1⟩ (since Rz(θ)|0⟩ = e^(iθ/2)|0⟩, Rz(θ)|1⟩ = e^(-iθ/2)|1⟩)
So state becomes e^(-iπ/4)|01⟩

H(q[1]): e^(-iπ/4)|0⟩⊗H|1⟩ = e^(-iπ/4)|0⟩⊗|−⟩ = (e^(-iπ/4)/√2)(|00⟩ - |

## isqTrain/4445

- task_id: `isqTrain/4445`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `104`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[2];

procedure main() {
    // Prepare initial state |10>
    X(q[0]);
    // e^(-i*theta*XX) with theta = pi/4
    // Basis change: rotate X eigenbasis to Z eigenbasis
    H(q[0]); H(q[1]);
    // ZZ evolution in the transformed basis
    CNOT(q[0], q[1]);
    // Rz(2*theta) = Rz(pi/2) applies the phase rotation
    Rz(1.57079632679490, q[1]);
    // Undo parity computation
    CNOT(q[0], q[1]);
    // Undo basis change: rotate back to computational basis
    H(q[0]); H(q[1]);
    // Measure: |10> evolves to superposition of |01> and |10>
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Analyze an isQ program and predict measurement outcomes.
    *   Format: "## Circuit Analysis" section, step-by-step reasoning, Dirac notation, concise (3-15 lines).
    *   Specific Instructions: Output ONLY the analysis, no code blocks, end with predicted probability distribution.

2.  **Analyze the isQ Code:**
    *   `qbit q[2];` -> 2 qubits initialized to $|00\rangle$.
    *   `X(q[0]);` -> State becomes $|10\rangle$.
    *   `H(q[0]); H(q[1]);` -> State becomes $H_0 H_1 |10\rangle = H|1\rangle \otimes H|0\rangle = |-⟩ \otimes |+⟩ = \frac{1}{\sqrt{2}}(|1\rangle - |0\rangle) \otimes \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = \frac{1}{2}(|10\rangle + |11\rangle - |00\rangle - |01\rangle)$.
    *   `CNOT(q[0], q[1]);` -> Flips $q[1]$ if $q[0]$ is 1.
        *   $|10\rangle \to |11\rangle$
        *   $|11\rangle \to |10\rangle$
        *   $|00\rangle \to |00\rangle$
        *   $|01\rangle \to |01\rangle$
        *   State: $\frac{1}{2}(|11\rangle + |10\rangle - |00\rangle - |01\rangle)$.
    *   `Rz(1.57079632679490, q[1]);` -> $R_z(\pi/2)$ on $q[1]$. $R_z(\theta)|0\rangle = e^{-i\theta/2}|0\rangle$, $R_z(\theta)|1\rangle = e^{i\theta/2}|1\rangle$.
        *   $\pi/2$ rotation.
        *   Terms with $q[1]=0$: $|10\rangle \to e^{-i\pi/4}|10\rangle$, $|00\rangle \to e^{-i\pi/4}|00\rangle$.
        *   Terms with $q[1]=1$: $|11\rangle \to e^{i\pi/4}|11\rangle$, $|01\rangle \to e^{i\pi/4}|01\rangle$.
        *   State: $\frac{1}{2}(e^{i\pi/4}|11\rangle + e^{-i\pi/4}|10\rangle - e^{-i\pi/4}|00\rangle - e^{i\pi/4}|01\rangle) = \frac{e^{i\pi/4}}{2}(|11\rangle - |01\rangle) - \frac{e^{-i\pi/4}}{2}(|00\rangle - |10\rangle)$.
    *   `CNOT(q[0], q[1]);` -> Undoes the first CNOT.
        *   State: $\frac{1}{2}(e^{i\pi/4}|10\rangle + e^{-i\pi/4}|11\rangle - e^{-i\pi/4}|00\rangle - e^{i\pi/4}|01\rangle)$.
    *   `H(q[0]); H(q[1]);` -> Undoes the first Hadamards.
        *   Note that $e^{-i \theta XX} = H e^{-i \theta ZZ} H$.
        *   We want $e^{-i \frac{\pi}{4} X_0 X_1} |10\rangle$.
        *   $X_0 X_1 |10\rangle = |01\rangle$. The eigenstates of $X_0 X_1$ are $|++\rangle, |--\rangle, |+-\rangle, |-+\rangle$ with eigenvalues $1, 1, -1, -1$.
        *   $|10\rangle = \frac{1}{2}(|++\rangle + |--\rangle - |+-\rangle + |-+\rangle)$ ? No, let's just do the math directly, or trust the matrix exponentiation.
        *   Actually, the state right before the second $H \otimes H$ is $\frac{1}{2}e^{i\pi/4}(|10\rangle - |01\rangle) + \frac{1}{2

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.5000, P(|11>) = 0.5000.'}

## isqExpand/algo/4

- task_id: `isqExpand/algo/4`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `grover`, `diffusion_operator`
- source: `isq_expansion`
- dataset_index: `4855`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[3];

procedure main() {
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
This circuit applies H-X-CCZ-X-H to all 3 qubits starting from |000>.

1. H on all: creates uniform superposition |s> = sum|x>/sqrt(8)
2. X on all: flips to |111>
3. ctrl @[q[0],q[1]] Z(q[2]): applies Z to q[2] when q[0]=q[1]=1, i.e., adds phase -1 to |111>
4. X on all: flips back
5. H on all: transforms back

This is the Grover diffusion operator D = H^n X^n (CCZ) X^n H^n = 2|0><0| - I (in the H basis = 2|s><s| - I).

Applied to |000>: D|000> = 2|s><s|000> - |000>. Since <s|000> = 1/sqrt(8), this gives amplitude 2/8 - 1 = -3/4 for |000> and 2/8 = 1/4 for all others.

Wait, let me recalculate. The diffusion is applied directly to |000>, not to a superposition. The result has |000> with amplitude (2*1/8 - 1) and others with 2*1/8.

Probabilities: |000>: (-3/4)^2 = 9/16... Actually this needs more careful calculation. Let me reconsider.

H|000> = |+++> = uniform over all 8 states with amplitude 1/2sqrt(2).
After X: |111> flipped.
CCZ adds phase -1 to |111>.
After X back: phase -1 on |000>.
So we have: all amplitudes 1/2sqrt(2) except |000> which is -1/2sqrt(2).
H on all: transforms this. The result is (2|000><000| - I)|000> in computational basis.

Actually the whole operation is the Grover diffusion: 2|s><s| - I. Applied to |000> we get amplitude 2*(1/sqrt(8))^2 - 1 = 2/8 - 1 = -3/4 for |000> and 2/8 = 1/4 for others.

Probabilities: |000>: 9/16 = 0.5625, others: 1/16 each * 7 = 7/16.
Total: 9/16 + 7/16 = 1. Correct.

Expected: {|000>: 0.5625, |001>: 0.0625, |010>: 0.0625, |011>: 0.0625, |100>: 0.0625, |101>: 0.0625, |110>: 0.0625, |111>: 0.0625}

### Reference answer

{'predicted_probs': {'000': 0.75, '001': 0.25, '010': 0.25, '011': -0.25, '100': 0.25, '101': -0.25, '110': -0.25, '111': 0.75}, 'explanation': 'This is a single Grover diffusion operator applied to |000>. The operator 2|s><s|-I reflects about the uniform superposition. Starting from |000>, the diffusion alone (without oracle) creates a non-uniform distribution.'}

## isqTrain/1397

- task_id: `isqTrain/1397`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2115`

### Prompt

I need an isQ program to the Bernstein-Vazirani algorithm to find the secret string s = 0101 (MSB first). Use 4 input qubits and 1 ancilla.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement Bernstein-Vazirani to find secret string s=0101 using phase kickback from an oracle encoding s·x mod 2.
2. Qubits: 4 input qubits q[0..3] + 1 ancilla; only q[0..3] are measured.
3. Initial state |0000>|0⟩; X(anc) → |0000>|1⟩; H(anc) → |0000>|-⟩.
4. H on all inputs: |++++⟩|−⟩ = (1/4)Σ_x |x⟩|−⟩.
5. Oracle CNOT(q[1],anc) and CNOT(q[3],anc) encodes s=0101 (bits 1,3 are 1): phases become (−1)^(s·x), giving (1/4)Σ_x (−1)^(s·x)|x⟩|−⟩.
6. H on all inputs converts phase encoding back to computational basis: H^⊗4 [(−1)^(s·x)] = |s⟩ = |0101⟩|−⟩.
7. Measuring q[0..3] yields |0101⟩ with probability 1.0.

## isqTrain/1152

- task_id: `isqTrain/1152`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `data_encoding_qml`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1224`

### Prompt

用isQ实现implements the data_encoding pattern with modified rotation parameters (num_pi2s_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

Step 1: Understand the Goal
The objective is to generate a Python script that acts as a quantum computing expert, providing concise reasoning for a given isQ quantum program based on a specific task. The task requires adapting a "data_encoding" pattern by modifying rotation parameters (num_pi2s_to_pi3).

Step 2: Analyze the circuit implementation and Constraints
- **Reference Code**: Uses 2 qubits, applies H gates to both, followed by `Rz(0.78539816339745, q[0])` (which is approximately $\pi/4$ or $0.785$) and `Rz(1.04719755119660490, q[1])` (which is exactly $\pi/3$ or $1.047...$), then H gates again, and finally measurements.
- **Expected Probabilities**: 
  - $P(00) = 0.640165042944952$
  - $P(01) = 0.21338834764832101$
  - $P(10) = 0.10983495705504466$
  - $P(11) = 0.036611652351682185$
- **Output Format**: Only the "Reasoning" section, 3-15 lines, using Dirac notation, NO code blocks, NO isQ code.

Step 3: Trace Quantum State Evolution
1. **Initial state**: $|00\rangle$
2. **After H, H**: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
3. **After Rz($\theta_0$) on q[0] and Rz($\theta_1$) on q[1]**:
   State becomes $\frac{1}{2}(e^{-i(\theta_0+\theta_1)/2}|00\rangle + e^{-i(-\theta_0+\theta_1)/2}|01\rangle + e^{-i(\theta_0-\theta_1)/2}|10\rangle + e^{-i(-\theta_0-\theta_1)/2}|11\rangle)$
   With $\theta_0 = \pi/4$ and $\theta_1 = \pi/3$.
4. **After H, H**: Applying H to each qubit converts phase differences into amplitude differences.
   $H|Rz(\theta)|H|0\rangle$ is effectively an $Rx$ rotation. Wait, $H Rz(\theta) H = Rx(\theta)$.
   Therefore, the state of each qubit $q_i$ becomes $Rx(\theta_i)|0\rangle$.
   $Rx(\theta)|0\rangle = \cos(\theta/2)|0\rangle - i\sin(\theta/2)|1\rangle$.
   So, for $\theta_0 = \pi/4$: $q_0$ is in $\cos(\pi/8)|0\rangle - i\sin(\pi/8)|1\rangle$.
   For $\theta_1 = \pi/3$: $q_1$ is in $\cos(\pi/6)|0\rangle - i\sin(\pi/6)|1\rangle$.
5. **Calculate Probabilities**:
   $P(00) = \cos^2(\pi/8) \cdot \cos^2(\pi/6) = 0.8535... \times 0.75 = 0.64016...$ (Matches!)
   $P(01) = \cos^2(\pi/8) \cdot \sin^2(\pi/6) = 0.8535... \times 0.25 = 0.21338...$ (Matches!)
   $P(10) = \sin^2(\pi/8) \cdot \cos^2(\pi/6) = 0.1464... \times 0.75 = 0.10983...$ (Matches!)
   $P(11) = \sin^2(\pi/8) \cdot \sin^2(\pi/6) = 0.1464... \times 0.25 = 0.03661...$ (Matches!)

Step 4: Formulate the Reasoning Text
- **Goal**: Encode classical features into quantum amplitudes using a modified ZZ feature map with adjusted Rz parameters.
- **Qubits**: 2 qubits are initialized and measured.
- **Evolution**:
  - Starts in $|00\rangle$.
  - H gates create uniform superposition $|+\rangle|+\rangle$.
  - Rz($\pi/4$

## isqQA/quantum_algorithms/113_application_scenario

- task_id: `isqQA/quantum_algorithms/113_application_scenario`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `application_scenario`, `algorithm`, `QFT与经典FFT的对比`
- source: `qa_pipeline`
- dataset_index: `3817`

### Prompt

既然量子傅里叶变换(QFT)在计算复杂度上远超经典快速傅里叶变换(FFT)，为什么我们不直接用量子计算机来处理日常的音频和图像频谱分析？请详细解释QFT在实际应用中的核心限制，并说明它真正的应用前景。最后，请使用isQ语言编写一个3量子比特的QFT核心代码片段，展示其在量子算法中作为子程序的实际运行方式。

### Reference answer

<tegia>

### 核心限制分析：为什么QFT不能直接替代经典FFT？
量子傅里叶变换（QFT）作用于量子态，其计算复杂度为 $O((\log N)^2)$，而经典FFT作用于数组，复杂度为 $O(N \log N)$。尽管QFT在数学复杂度上呈现出指数级加速，但在实际应用中，它无法直接用于传统的信号处理（如图像、音频频谱分析），主要原因有两点（即经典的I/O瓶颈）：

1. **量子态制备的输入瓶颈**：如果我们想把一段经典的音频信号进行傅里叶变换，首先需要将这 $N$ 个振幅数据编码到量子态中（即态制备）。这个读取过程在最坏情况下需要 $O(N)$ 的量子门操作，这瞬间就抵消了QFT本身带来的指数级加速优势。
2. **量子测量坍缩的输出瓶颈**：QFT的输出是一个包含所有频域信息的量子叠加态。但是，根据量子力学公设，当我们去测量这个态时，它会发生坍缩，每次测量只能随机得到一个频率分量的结果。为了获取完整的频谱信息，我们需要重复执行指数次测量，这再次破坏了整体的加速优势。

### 真正的应用前景与案例
由于上述限制，QFT的实际应用场景绝不是去替代经典信号处理，而是作为**纯量子算法的核心中间子程序**，在量子态自然产生的地方发挥作用，处理那些不需要频繁进行经典-量子数据转换的任务。其最典型的应用案例包括：

1. **Shor大数质因数分解算法**：这是QFT最著名的应用。在利用量子叠加态并行计算出函数周期性质的隐藏信息后，QFT被用来将这些周期性（频域特征）转化为可以直接测量的基态概率幅，从而破解RSA加密。
2. **量子相位估计（QPE）**：在量子化学和材料科学中，QPE结合QFT被用于精确估计分子的哈密顿量特征值（即分子基态和激发态能量），这是未来量子计算机在材料设计和药物研发领域的基石。
3. **HHL算法解线性方程组**：在量子机器学习和量子微分方程求解中，HHL算法利用QFT进行特征值求逆操作，为处理超大规模稀疏矩阵提供了指数级加速的可能。

### isQ代码演示：3量子比特QFT子程序
下面展示如何使用isQ语言实现一个3量子比特的量子傅里叶变换。在该过程中，量子态将经历哈达马门、受控相位旋转，以及末尾的比特反转操作（由于isQ禁止使用SWAP门，这里通过3个级联的CNOT门来实现等效的比特翻转逻辑）。

```isq
import std;

qbit q[3];

procedure main() {
    // 假设初始态制备为某一个特定状态，例如 |5> 即 |101>
    X(q[0]);
    X(q[2]);

    // === 开始 3-qubit QFT ===

    // 第1个量子比特 (q[0]) 的操作
    H(q[0]);
    // 受控相位旋转 Rz(pi/2)
    ctrl @[q[1]] Rz(1.57079632679, q[0]);
    // 受控相位旋转 Rz(pi/4)
    ctrl @[q[2]] Rz(0.78539816339, q[0]);

    // 第2个量子比特 (q[1]) 的操作
    H(q[1]);
    // 受控相位旋转 Rz(pi/2)
    ctrl @[q[2]] Rz(1.57079632679, q[1]);

    // 第3个量子比特 (q[2]) 的操作
    H(q[2]);

    // 等效SWAP操作：交换 q[0] 和 q[2] 的状态
    // 根据语法约束，不使用SWAP门，而使用3个CNOT门实现交换
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
}
```

在这段代码中，量子比特被施加了一系列特定的旋转门，巧妙地将波函数的相位信息提取到了振幅中，这正是它在Shor算法等高阶量子算法中扮演关键角色的运作方式。

</tegia>

## isqTrain/2814

- task_id: `isqTrain/2814`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `isq_syntax_arrays`, `isq_syntax_deriving_gate`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5089`

### Prompt

What is the measurement probability distribution of this isQ program?

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

Let me analyze this isQ program step by step.

The program implements Grover's search algorithm on 3 qubits plus 1 ancilla.

**Initial state:** |0000⟩ (q[2], q[1], q[0], anc)

**Step 1: Apply H to all qubits (q and anc)**
H(q) and H(anc) transforms the state to:
|ψ⟩ = (1/√8) Σ|x⟩ ⊗ |−⟩ = (1/√8)(|000⟩+|001⟩+|010⟩+|011⟩+|100⟩+|101⟩+|110⟩+|111⟩) ⊗ (|0⟩-|1⟩)/√2

**Step 2: Oracle U_omega**
The oracle `U_omega(3,1) = [0,1,0,0,0,0,0,0]` marks the state |001⟩ (index 1). This means it flips the phase of |001⟩ when the ancilla is in the |−⟩ state. The oracle applies a phase flip to |1⟩ (binary 001).

After oracle: The state |001⟩ gets a phase flip, so it becomes -|001⟩ while others remain the same, all tensored with |−⟩.

**Step 3: Grover diffusion operator**
The diffusion operator is: H ⊗³ → U0 → H ⊗³

U0 is the matrix that has 1 in the (0,0) position and -1 elsewhere on the diagonal. This is the reflection about |000⟩ in the Hadamard basis, which is the standard diffusion operator 2|+⟩⟨+| - I (up to a global phase).

Wait, let me check U0 more carefully:
U0 = diag(1, -1, -1, -1, -1, -1, -1, -1)

This is -I + 2|000⟩⟨000| = -(I - 2|000⟩⟨000|)

Actually, H⊗³ · U0 · H⊗³:

The standard Grover diffusion operator is 2|s⟩⟨s| - I where |s⟩ = |+⟩⊗3.

Let me think about this differently. H⊗³ maps |0⟩⊗3 to |s⟩. So:
H⊗³ U0 H⊗³ = H⊗³ (2|0⟩⟨0| - I) H⊗³ = 2|s⟩⟨s| - I

Wait, U0 = diag(1,-1,-1,-1,-1,-1,-1,-1) = 2|000⟩⟨000| - I

So H⊗³ U0 H⊗³ = 2|s⟩⟨s| - I, which is exactly the Grover diffusion operator.

Good, so this is standard Grover's algorithm.

**Analysis of the iterations:**

The search space has N = 8 states, with 1 marked state. The optimal number of iterations is approximately π/(4·arcsin(1/√8)) ≈ π/(4·0.3636) ≈ 2.16.

The program runs 3 iterations (for i in 0:2 means i=0,1,2, so 3 iterations).

Wait, let me re-read: `for i in 0:2 { }` - in isQ, this likely means i goes from 0 to 2 inclusive, so 3 iterations.

Let me compute what happens after each iteration.

After initialization:
|ψ₀⟩ = |s⟩ = (1/√8)Σ|x⟩

The marked state is |w⟩ = |1⟩ = |001⟩.

Each Grover iteration applies:
G = (2|s⟩⟨s| - I)(I - 2|w⟩⟨w|)

Wait, the oracle in the standard formulation flips the sign of |w⟩, giving (I - 2|w⟩⟨w|).

So after k iterations, the amplitude of |w⟩ is:
sin((2k+1)θ) where sin(θ) = 1/√8

θ = arcsin(1/√8) ≈ arcsin(0.3536) ≈ 0.3614 rad

After 3 iterations:
(2·3+1)θ = 7·0.3614 ≈ 2.53 rad

sin(2.53) ≈ 0.5716

Hmm, that doesn't give probability 1.0 for state 0 as the predicted output suggests.

Wait, Let me re-analyze the output: "Expected measurement probabilities: {'0': 1.0}"

This means measuring q[2], q[1], q

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

# ISQ training COT RAG corpus: quantum_algorithms shard 6

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3919

- task_id: `isqTrain/3919`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_deriving_gate`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `1236`

### Prompt

Something is wrong with this isQ circuit. Identify the error and provide the corrected code.

```
import std;
// Swap test: compare |1> vs |1>
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
    X(q[1]);
    // Prepare state B on q[2]
    X(q[2]);
    // Swap test circuit
    // BUG: missing gate here
    cswap(q);
    H(q[0]);
    // Measure ancilla and state qubits
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The swap test circuit is missing the initial **Hadamard gate on the ancilla** (`H(q[0])`) before the controlled-swap (three-CNOT decomposition). The comment `// BUG: missing gate here` marks the location. Without this H, the ancilla stays in |0⟩, so the controlled-swap (three-CNOT decomposition) never activates (control = |0⟩), and the circuit cannot function as a swap test.

2. **Fix**: Add `H(q[0]);` before `cswap(q);`, so the full sequence becomes `H(q[0]) → cswap(q) → H(q[0])`.

3. **State evolution (corrected)**:
   - Init: |000⟩
   - `X(q[1]), X(q[2])`: |011⟩
   - `H(q[0])`: (|011⟩ + |111⟩)/√2
   - `cswap(q)`: Since q[1]=q[2]=|1⟩, swapping identical states leaves them unchanged → (|011⟩ + |111⟩)/√2
   - `H(q[0])`: (1/2)[(|0⟩+|1⟩)|11⟩ + (|0⟩−|1⟩)|11⟩] = |011⟩
   - Measurement yields **|011⟩ with probability 1.0** ✓ (ancilla = 0 confirms states are identical)

## isqTrain/4098

- task_id: `isqTrain/4098`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `201`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[3];

procedure main() {
    X(q[2]);

    H(q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[2]);
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

The isQ circuit is:
1. X(q[2]) - initializes q[2] to |1>
2. H(q[0])
3. ctrl Rz(pi/2, q[1], q[0])
4. ctrl Rz(pi/4, q[2], q[0])
5. H(q[1])
6. ctrl Rz(pi/2, q[2], q[1])
7. H(q[2])
8. CNOT(q[0], q[2])
9. CNOT(q[2], q[0])
10. CNOT(q[0], q[2])
11. M(q[0]); M(q[1]); M(q[2])

Wait, the order of arguments for `ctrl Rz(theta, control, target)` or `ctrl Rz(theta, target, control)`?
Looking at isQ syntax: `ctrl @[c1, c2] Gate(target);`. But the circuit uses `ctrl Rz(theta, q[1], q[0])`.
Wait, in isQ, is it `ctrl Rz(theta, control, target)`? Or `Rz(theta, target)`?
Actually, wait. `ctrl Rz(theta, q[1], q[0])` usually means the control is the first qubit or the second qubit? In standard notation, it might be `ctrl(control) @ Rz(theta, target)`.
Wait, let's look at the structure:
H(q[0]);
ctrl Rz(pi/2, q[1], q[0]);
ctrl Rz(pi/4, q[2], q[0]);
H(q[1]);
ctrl Rz(pi/2, q[2], q[1]);
H(q[2]);
This looks exactly like the structure of a Quantum Fourier Transform (QFT) on 3 qubits.
Wait, QFT involves applying H to q[0], then controlled R2 to q[0] (controlled by q[1]), controlled R3 to q[0] (controlled by q[2]), then H to q[1], controlled R2 to q[1] (controlled by q[2]), then H to q[2].
If `ctrl Rz(theta, control, target)` matches this, then `q[1]` controls `q[0]`.
Wait, the Rz gate in QFT should be $R_k = \begin{pmatrix} 1 & 0 \\ 0 & e^{2\pi i / 2^k} \end{pmatrix}$.
The angles here are `2.0 * pi / 4.0 = pi/2` and `2.0 * pi / 8.0 = pi/4`.
Wait, if `Rz` applies $e^{-i\theta/2}$ and $e^{i\theta/2}$, then $Rz(\theta) = \begin{pmatrix} e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2} \end{pmatrix}$.
So `Rz(pi/2)` is the T gate (up to global phase) or S gate? Wait, $Rz(\pi/2) = \begin{pmatrix} e^{-i\pi/4} & 0 \\ 0 & e^{i\pi/4} \end{pmatrix}$.
If this is QFT, it acts on the state $|100\rangle$ (since `q[2]` is flipped to $|1\rangle$, and assuming $q[2]$ is the 0th qubit in the standard binary order? Or maybe $q[0]$ is the most significant bit?)
Wait! `X(q[2])` makes the initial state $|001\rangle$ if we write it as $q[2]q[1]q[0]$ or $|100\rangle$ if we write it as $q[0]q[1]q[2]$.
Let's trace carefully.
Initial state: $q[2] = |1\rangle$, others $|0\rangle$. State is $|001\rangle$ (where bitstring is $q[2]q[1]q[0]$).
Then:
`H(q[0])`
`ctrl Rz(pi/2, q[1], q[0])`
`ctrl Rz(pi/4, q[2], q[0])`
`H(q[1])`
`ctrl Rz(pi/2, q[2], q[1])`
`H(q[2])`
This sequence transforms the state.
Then the CNOTs:
`CNOT(q[0], q[2])`
`CNOT(q[2], q[0])`
`CNOT(q[0], q[2])`
This is a swap operation (three-CNOT decomposition)

### Reference answer

Uniform distribution across 8 states

## isqTrain/3721

- task_id: `isqTrain/3721`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `466`

### Prompt

Create an isQ quantum circuit that QAOA (p=1) for the MaxCut problem on a 3-node star graph with edges [(0, 1), (0, 2)]. Use parameters gamma=0.785 and beta=0.393. The circuit:
1. Initialize all qubits in superposition
2. Apply cost unitary: for each edge, use CNOT-Rz-CNOT
3. Apply mixer: Rx(2*beta) on each qubit
4. Measure all 3 qubits

### Chain-of-thought reasoning

Let me analyze this QAOA circuit for MaxCut on a 3-node star graph.

1. Goal: Implement QAOA (p=1) to find approximate MaxCut solutions for a star graph with edges (0,1) and (0,2).

2. Qubits: 3 qubits (q[0], q[1], q[2]), all measured.

3. State evolution:
- Start: |000⟩
- After H on all: (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 = (1/2√2)(|000⟩+|001⟩+|010⟩+|011⟩+|100⟩+|101⟩+|110⟩+|111⟩)

Wait, let me be more careful. |+⟩ = (|0⟩+|1⟩)/√2, so after H on all:
|+++⟩ = (1/2√2) Σ_{x∈{0,1}^3} |x⟩

- Cost unitary for edge (0,1): CNOT(0,1)-Rz(2*0.785, 1)-CNOT(0,1)
  This applies exp(-i*0.785*Z_0*Z_1) when qubits have different values (phase of -2*gamma for odd parity).

Actually, the CNOT-Rz(2γ)-CNOT sequence applies Rz(2γ) on target controlled by control being |1⟩. This is equivalent to applying exp(-iγ*Z_c*Z_t).

Let me think about this more carefully. The ZZ interaction exp(-iγ Z_i Z_j) applies phase e^{-iγ} when Z_i Z_j = +1 (same values) and e^{iγ} when Z_i Z_j = -1 (different values).

For the edge (0,1) with γ=0.785:
- States where q[0]=q[1]: multiply by e^{-i*0.785}
- States where q[0]≠q[1]: multiply by e^{i*0.785}

Wait, let me reconsider. exp(-iγ Z⊗Z) diagonal elements:
- ⟨00|exp(-iγ Z⊗Z)|00⟩ = exp(-iγ)
- ⟨01|exp(-iγ Z⊗Z)|01⟩ = exp(iγ)
- ⟨10|exp(-iγ Z⊗Z)|10⟩ = exp(iγ)
- ⟨11|exp(-iγ Z⊗Z)|11⟩ = exp(-iγ)

So states |00⟩ and |11⟩ get phase e^{-iγ}, while |01⟩ and |10⟩ get phase e^{iγ}.

For edge (0,1) with γ=0.785:
- |000⟩, |001⟩, |110⟩, |111⟩ get phase e^{-i*0.785}
- |010⟩, |011⟩, |100⟩, |101⟩ get phase e^{i*0.785}

For edge (0,2) with γ=0.785:
- |000⟩, |010⟩, |101⟩, |111⟩ get phase e^{-i*0.785}
- |001⟩, |011⟩, |100⟩, |110⟩ get phase e^{i*0.785}

Combined phase from both edges:
- |000⟩: e^{-i*0.785} * e^{-i*0.785} = e^{-i*1.57}
- |001⟩: e^{-i*0.785} * e^{i*0.785} = 1
- |010⟩: e^{i*0.785} * e^{-i*0.785} = 1
- |011⟩: e^{i*0.785} * e^{i*0.785} = e^{i*1.57}
- |100⟩: e^{i*0.785} * e^{i*0.785} = e^{i*1.57}
- |101⟩: e^{i*0.785} * e^{-i*0.785} = 1
- |110⟩: e^{-i*0.785} * e^{i*0.785} = 1
- |111⟩: e^{-i*0.785} * e^{-i*0.785} = e^{-i*1.57}

Now the mixer Rx(2β) with β=0.393, so 2β=0.786.

Rx(θ) = exp(-

## isqTrain/1862

- task_id: `isqTrain/1862`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1206`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(pi/2.0, q[1]);
    CNOT(q[0], q[1]);
    Rx(pi/4.0, q[0]);
    Rx(pi/4.0, q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Initial State:** Both qubits are in $|0\rangle$.
    State: $|00\rangle$

2.  **H(q[0]); H(q[1]);**:
    Apply H to both qubits.
    $|00\rangle \xrightarrow{H \otimes H} \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$

3.  **CNOT(q[0], q[1])**:
    Apply CNOT with q[0] as control, q[1] as target.
    $\frac{1}{2}(|00\rangle + |01\rangle + |11\rangle + |10\rangle) = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
    Wait, CNOT flips the target (q1) when control (q0) is 1.
    $|00\rangle \to |00\rangle$
    $|01\rangle \to |01\rangle$
    $|10\rangle \to |11\rangle$
    $|11\rangle \to |10\rangle$
    Wait, no! Let's trace carefully.
    Initial: $|00\rangle$
    After H,H: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$
    After CNOT(0,1):
    $|00\rangle \to |00\rangle$
    $|01\rangle \to |01\rangle$
    $|10\rangle \to |11\rangle$
    $|11\rangle \to |10\rangle$
    So it remains $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$! Wait, $\frac{1}{2}(|00\rangle + |01\rangle + |11\rangle + |10\rangle) = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
    Is that true? Let's check.
    State before CNOT: $\frac{1}{2}|0\rangle(|0\rangle+|1\rangle) + \frac{1}{2}|1\rangle(|0\rangle+|1\rangle)$
    After CNOT: $\frac{1}{2}|0\rangle(|0\rangle+|1\rangle) + \frac{1}{2}|1\rangle(|1\rangle+|0\rangle) = \frac{1}{2}(|00\rangle + |01\rangle + |11\rangle + |10\rangle)$.
    Yes, it is still an equal superposition of all 4 states.

4.  **Rz(pi/2.0, q[1])**:
    Rz adds a phase $e^{-i\theta/2}$ to $|0\rangle$ and $e^{i\theta/2}$ to $|1\rangle$.
    Global phase doesn't matter. Let's just look at the relative phase between $|0\rangle$ and $|1\rangle$ on q1.
    $\theta = \pi/2$.
    For q1:
    $|0\rangle \to |0\rangle$
    $|1\rangle \to e^{i\pi/2}|1\rangle = i|1\rangle$ (ignoring global phase).
    So the state becomes:
    $\frac{1}{2}(|00\rangle + i|01\rangle + |11\rangle + i|10\rangle)$
    Wait, let's re-verify.
    $|00\rangle \to |00\rangle$
    $|01\rangle \to i|01\rangle$
    $|10\rangle \to i|10\rangle$
    $|11\rangle \to i|11\rangle$
    So $\frac{1}{2}(|00\rangle + i|01\rangle + i|10\rangle + i|11\rangle) = \frac{1}{2}(|00\rangle + i(|01\rangle + |10\rangle + |11\rangle))$.

5.  **CNOT(q[0], q[1])**:
    $|00\rangle \to |00\rangle$
    $|01\rangle \to |01\rangle$
    $|10\rangle \to |11\rangle$

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'QAOA layer 1 on 2-node graph yields specific distribution.'}

## isqTrain/4037

- task_id: `isqTrain/4037`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `625`

### Prompt

This isQ program compiles but produces incorrect probabilities. Find and correct the mistake.

```
import std;
// QFT on 3 qubits with input state |101>
qbit q[3];

procedure main() {
    // Prepare input state |101>
    X(q[0]);
    X(q[2]);

    // QFT stage for qubit 0
    H(q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    // QFT stage for qubit 1
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    // QFT stage for qubit 2
    H(q[2]);
    // Swap q[0] and q[2]
    CNOT(q[0], q[2]);
    CNOT(q[0], q[2]);
    CNOT(q[0], q[2]);
    // Measure after QFT
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug location**: The middle CNOT in the swap operation at line `CNOT(q[0], q[2]); CNOT(q[0], q[2]); CNOT(q[0], q[2]);` has the control and target qubits swapped. Three identical CNOTs with the same control/target equals a single CNOT (since CNOT is self-inverse), which does NOT perform a swap.

2. **Fix**: Change the second CNOT to `CNOT(q[2], q[0]);` so the swap becomes the standard pattern: `CNOT(q[0], q[2]); CNOT(q[2], q[0]); CNOT(q[0], q[2]);`.

3. **State evolution of corrected circuit**:
   - Prepare |101⟩ by applying X to q[0] and q[2]
   - QFT on 3 qubits: H and controlled-phase rotations process each qubit, producing the Fourier transform with reversed bit order
   - The swap of q[0] and q[2] corrects the bit order, yielding QFT|101⟩ = (1/√8) Σⱼ e^{2πi·5j/8}|j⟩
   - All 8 basis states have equal probability |1/√8|² = 0.125, confirming the uniform distribution matches predicted output

## isqExpand/algo/160

- task_id: `isqExpand/algo/160`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `Shor算法`, `量子相位估计`, `连分数展开`, `模幂运算`, `量子傅里叶变换`, `阶查找问题`
- source: `isq_expansion_qa`
- dataset_index: `2863`

### Prompt

解释Shor算法分解N=21的过程：选择a=4，如何通过量子相位估计找到周期r？

### Chain-of-thought reasoning

首先分析Shor算法在N=21、a=4时的具体参数：验证gcd(4,21)=1满足前提条件。然后计算阶r：4^1=4(mod21), 4^2=16(mod21), 4^3=64≡1(mod21)，故r=3。接着推导QPE过程：构造t≈10的控制寄存器和n=5的目标寄存器；Hadamard创建叠加态；受控U^{2^j}实现模4^x mod21；IQFT将周期结构转化为频率峰值k·2^t/r。测量后通过连分数展开从m/2^t恢复r=3。最后指出r=3为奇数无法直接分解，需重选a值，并举例a=2、r=6可成功分解。整个过程严格遵循Shor算法的理论框架，涵盖了量子-经典混合计算的核心思想。

### Reference answer

Shor算法分解N=21且选择a=4的完整过程如下：

**第一步：经典预处理**
选取a=4，验证gcd(4,21)=1，满足条件。需要找到最小的正整数r使得4^r ≡ 1 (mod 21)。经计算：4^1=4, 4^2=16, 4^3=64≡1 (mod 21)，故周期r=3。

**第二步：量子电路构造**
构造两个量子寄存器：
- 第一寄存器（控制寄存器）：t个量子比特，t ≈ 2log₂(21) ≈ 10，用于相位估计
- 第二寄存器（目标寄存器）：n=5个量子比特（因为21<2^5），存储模幂运算结果

**第三步：量子相位估计过程**
1. **初始化**：第一寄存器全部置|0⟩，第二寄存器置|1⟩（即|0000000001⟩）

2. **Hadamard层**：对第一寄存器所有t个量子比特施加H门，创建均匀叠加态：
   (1/√2^t) Σ|x⟩|1⟩，其中x从0到2^t-1

3. **受控模幂运算**：对第一寄存器的第j个量子比特施加受控U^{2^j}操作，其中U|y⟩=|4y mod 21⟩。这一步将系统变为：
   (1/√2^t) Σ|x⟩|4^x mod 21⟩
   由于周期r=3，态可重写为三组相干叠加，每组对应4^x mod 21的一个值（1,4,16循环）。

4. **量子傅里叶逆变换（IQFT）**：对第一寄存器施加逆QFT。IQFT将周期结构转换为相位信息，使测量结果集中在m ≈ k·2^t/r处（k=0,1,...,r-1）。

5. **测量**：测量第一寄存器得到整数m。对于r=3：
   - m/2^t ≈ 0（概率1/3）
   - m/2^t ≈ 1/3（概率1/3）
   - m/2^t ≈ 2/3（概率1/3）

**第四步：经典后处理——连分数提取周期**
将测量值m/2^t用连分数展开逼近，找到分母r：
- 若测得m/2^t ≈ 1/3，连分数展开直接给出r=3
- 若测得m/2^t ≈ 2/3，连分数展开同样给出r=3
- 若测得m=0则需重复实验

**第五步：验证与分解**
得到r=3后，由于r为奇数，经典方法a^(r/2)±1不直接适用（r/2非整数）。此时需重新选择a值（如a=2, r=6可成功：gcd(2^3-1,21)=gcd(7,21)=7，gcd(2^3+1,21)=gcd(9,21)=3，成功分解21=3×7）。

**关键原理总结**：QPE通过IQFT将隐藏子群（周期结构）转化为可测量的频率信息，这是Shor算法优于经典算法的核心——量子计算机在O((logN)³)时间内完成周期查找，而经典最佳算法需要亚指数时间。

## isqTrain/2930

- task_id: `isqTrain/2930`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `180`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]);
    X(q[1]);
    ctrl Rz(1.570796, q[0], q[1]);
    H(q[0]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a step-by-step circuit analysis for a specific isQ quantum program, ending with the predicted probability distribution of the measured states.

2.  **Analyze the Circuit**:
    *   Initialization: 2 qubits, `q[0]` and `q[1]`, starting at `|00>`.
    *   `H(q[0])`: Apply Hadamard to qubit 0. State becomes `1/sqrt(2) (|00> + |10>)`.
    *   `X(q[1])`: Apply Pauli-X to qubit 1. State becomes `1/sqrt(2) (|01> + |11>)`.
    *   `ctrl Rz(1.570796, q[0], q[1])`: Apply a controlled-Rz gate with `q[0]` as control and `q[1]` as target. Wait, the syntax `ctrl Rz(theta, control, target)` is a bit unusual but wait, isQ syntax for `ctrl` is usually `ctrl Gate(target)` but here it's `ctrl Rz(theta, q[0], q[1])`. Let's look at the reference: "Two-qubit gates: CNOT(control, target)... Control modifier: `ctrl @[c1, c2] Gate(target);`". Wait, `Rz(theta, q)` has one target. So `ctrl Rz(1.570796, q[0], q[1])` might mean control `q[0]` and target `q[1]`, but normally Rz takes a single qubit. Let's re-read: "ctrl Rz(1.570796, q[0], q[1])". If standard syntax is `ctrl Rz(theta, target)` where control is implicitly provided or it means `cRz(theta, control, target)`. Wait, if `q[0]` is control and `q[1]` is target, the phase $\pi/2$ (1.570796 is $\pi/2$) is applied to the `|11>` component. Wait, let's check the angle: 1.570796 is $\pi/2$.
    *   Let's trace the state evolution carefully.
    *   Initial: `|00>`
    *   `H(q[0])`: `1/sqrt(2)|00> + 1/sqrt(2)|10>`
    *   `X(q[1])`: `1/sqrt(2)|01> + 1/sqrt(2)|11>`
    *   `ctrl Rz(1.570796, q[0], q[1])`: Wait, Rz applies a phase. Since `ctrl` is applied, if `q[0]` is the control, the `|11>` state gets a phase. Wait! The angle 1.570796 is $\pi/2$. Rz($\theta$) applies $e^{-i\theta/2}|0> + e^{i\theta/2}|1>$ to the target. Wait, standard Rz matrix is $diag(1, e^{i\theta})$ in some frameworks, or $diag(e^{-i\theta/2}, e^{i\theta/2})$. isQ `Rz` matrix: standard is $diag(1, e^{i\theta})$ or $diag(e^{-i\theta/2}, e^{i\theta/2})$. Let's assume $R_z(\theta) = \begin{pmatrix} 1 & 0 \\ 0 & e^{i\theta} \end{pmatrix}$ or similar. Actually, wait. Let's just calculate the outcome if the target is `q[1]` and control is `q[0]`.
    *   Wait, is `ctrl Rz(theta, control, target)` a standard way in isQ? In standard isQ, it's `ctrl Rz(theta, q[1])` with control `q[0]`? No, wait. The syntax in the prompt is `ctrl Rz(1.570796, q[0], q[1])`. This looks like a compiler sugar where `ctrl` just turns the next gate into a controlled gate, and if the gate takes args `theta, target`, maybe it's `ctrl Rz(theta, control, target)`? Let's assume `q[0]` is control, `q[1]` is target.
    *   Wait, `Rz` applies a phase to the target qubit. If target is `q[1]`, and control is `q[0]`, then the state `|11>` gets a phase.
    *

### Reference answer

{'predicted_probs': {'01': 0.853553448362991, '11': 0.14644655163700912}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/2840

- task_id: `isqTrain/2840`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3294`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state is |00>.
2. H(q[0]) puts q[0] into superposition: 1/sqrt(2)(|0> + |1>) ⊗ |0> = 1/sqrt(2)(|00> + |10>).
3. CNOT(q[0], q[1]) entangles the two qubits, flipping q[1] when q[0] is |1>: 1/sqrt(2)(|00> + |11>).
4. Measuring both qubits yields correlated outcomes.

Probability distribution: [0.5, 0.0, 0.0, 0.5]

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3489

- task_id: `isqTrain/3489`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `data_encoding_qml`, `phase_manipulation`, `interference`
- source: `isq_train_cot`
- dataset_index: `4654`

### Prompt

Write isQ code for the following quantum task: phase encoding of classical data into quantum phases in isQ.

Encode values [pi/4, pi/2, pi] as phases using Rz rotations on 3 qubits.
First apply H to create superposition, then Rz to encode the phase.
Then apply H again and measure to observe interference.

Declare 3 qubits, measure all.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Encode classical phase values [π/4, π/2, π] into 3 qubits using Rz rotations, then decode via interference with H gates.

**Qubits:** 3 qubits declared (q[0], q[1], q[2]), all measured.

**State evolution:**
1. **Initial:** |000⟩
2. **After H⊗3:** (|0⟩+|1⟩)⊗3/√8 = |+++⟩
3. **After Rz:** Each qubit becomes (|0⟩ + e^{iθ}|1⟩)/√2 with θ₀=π/4, θ₁=π/2, θ₂=π
4. **After H again:** H(|0⟩+e^{iθ}|1⟩)/√2 = ((1+e^{iθ})|0⟩+(1-e^{iθ})|1⟩)/2

**Probability analysis per qubit:**
- **q[0]** (θ=π/4): P(0)=|1+e^{iπ/4}|²/4=(2+√2)/4≈0.8536, P(1)=(2-√2)/4≈0.1464
- **q

## isqTrain/3617

- task_id: `isqTrain/3617`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `4451`

### Prompt

Create an isQ quantum circuit that a 4-qubit Grover search for target state |0000> using the optimal 3 iterations. The circuit should:
1. Initialize 4 qubits in uniform superposition
2. Apply 3 Grover iterations (oracle + diffusion) using a for loop
3. Measure all 4 qubits
Use `deriving gate` and `ctrl<2> CZ` for the multi-controlled phase.

### Chain-of-thought reasoning

## Reasoning
1. Goal: 4-qubit Grover search finding target |0000⟩ using optimal 3 iterations.
2. Four qubits declared globally; all 4 are measured at the end.
3. State evolution: |0000⟩ → H⊗4 → (1/4)Σₓ|x⟩ (uniform superposition, amplitude α=1/4 over N=16 states). The oracle uses X gates to map |0000⟩↔|1111⟩, then `ctrl<2> CZ` flips |1111⟩'s phase, marking |0000⟩. The diffusion operator (H⊗4·X⊗4·multi-controlled-Z·X⊗4·H⊗4) inverts amplitudes about the mean. Each iteration rotates state by angle 2θ (θ=arcsin(1/4)) in the {|0000⟩, |⊥⟩} subspace. After 3 iterations, |0000⟩ amplitude ≈ sin(7θ) ≈ 0.9815.
4. Final probability: |⟨0000|ψ⟩|² ≈ 0.9634; the remaining ~0.0366 is uniformly distributed across the 15 non-target states (~0.0024 each).

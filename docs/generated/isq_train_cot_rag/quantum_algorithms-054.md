# ISQ training COT RAG corpus: quantum_algorithms shard 54

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqQA/quantum_algorithms/45_hardware_limitations

- task_id: `isqQA/quantum_algorithms/45_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `hardware_limitations`, `algorithm`, `量子傅里叶变换(QFT)`
- source: `qa_pipeline`
- dataset_index: `683`

### Prompt

在理论上，量子傅里叶变换（QFT）能够实现指数级加速，是Shor算法等众多核心量子算法的关键子程序。然而，在当前的含噪声中等规模量子（NISQ）设备上实现高维度的QFT却面临极大的挑战。请详细分析NISQ设备的硬件局限性（如退相干时间、拓扑连通性）、双比特门错误率以及线路深度等因素是如何限制实际可运行的QFT规模的？此外，针对这些硬件物理层面的限制，目前有哪些可行的算法优化或缓解策略？

### Reference answer

虽然量子傅里叶变换（QFT）在理论上仅需 $O(n^2)$ 个量子门（$n$ 为量子比特数），远优于经典快速傅里叶变换（FFT）的 $O(n2^n)$，但在当前的含噪声中等规模量子（NISQ）时代，实际能成功运行的QFT规模通常被严格限制在个位数或十几 个量子比特。这主要受制于以下几个核心硬件局限性：

1. **退相干时间的严苛限制**：量子比特的状态极其脆弱。能量弛豫时间（$T_1$）限制了量子态保持为 $|0\rangle$ 或 $|1\rangle$ 的时间，而相位退相干时间（$T_2$）则限制了量子态保持叠加相位相干性的时间。完整的QFT包含大量串行的受控旋转门（如 $CR_k$），随着比特数 $n$ 的增加，线路深度急剧膨胀。如果整个QFT线路的执行时间超过或接近系统的退相干时间 $T_1$ 和 $T_2$，量子态的相位和幅度信息就会因环境耦合而坍塌或退相干，最终测量结果将被淹没在均匀分布的经典随机噪声中，导致算法彻底失效。

2. **双比特门的高错误率**：QFT的核心在于一系列受控相位旋转门（$CPhase$）。在物理实现上，这些双比特门的错误率通常比单比特门（如Hadamard门）高出1到2个数量级。在目前的超导或离子阱量子芯片中，双比特门（如CNOT或CZ）的错误率普遍在 $10^{-3}$ 到 $10^{-2}$ 之间。在 $n$ 比特的QFT中，需要执行 $n(n-1)/2$ 次双比特操作。当 $n$ 较大时（例如 $n=20$，需要190次双比特门），错误会呈指数级累积，最终导致保真度趋近于零。

3. **底层拓扑连通性与SWAP开销**：理论上QFT需要任意两个量子比特之间能够直接相互作用（全连接架构）。然而，实际的NISQ硬件往往具有固定的空间拓扑结构（例如超导量子芯片多为二维网格或重六角形晶格）。当QFT线路要求远距离的量子比特执行受控操作时，必须插入额外的SWAP门来移动量子态。每个SWAP门通常需要分解为3个CNOT门，这不仅大大增加了线路深度，还进一步成倍放大了双比特门的累积错误。

**针对硬件局限的缓解策略：**

由于NISQ设备缺乏纠错能力，目前主要依靠算法层面的“软化”和“近似化”来适应硬件：

- **近似量子傅里叶变换**：这是最经典的硬件适配策略。在 $n$ 比特QFT中，当受控旋转门 $CR_k$ 的相位角度 $\pi/2^{k-1}$ 非常小（即 $k$ 较大，作用在距离较远的比特间）时，其对最终计算结果的贡献极其微小。AQFT通过设定一个截断距离 $m$（例如 $m = \lceil \log_2 n \rceil + 2$），直接去除所有 $k > m$ 的小角度受控旋转门。这种做法将双比特门的数量从 $O(n^2)$ 降低到了 $O(n \log n)$，极大地压缩了线路深度，同时带来的算法精度误差在多项式复杂度下被认为是可接受的。
- **动态解耦**：在长线路的空闲量子比特上插入特定的单比特门序列（如XY4、CDD序列），以平均化环境噪声，延缓退相干过程。
- **线路映射与路由优化**：在编译阶段，针对特定芯片的物理拓扑结构，使用启发式算法寻找最优的量子比特初始分配方案，从而最小化为了连通远距离比特而引入的SWAP门数量。
- **量子错误缓解**：在不对量子比特进行物理纠错的前提下，通过在经典后端处理中执行零噪声外推（ZNE）或概率错误消除（PEC）等数学方法，从含噪的测量结果中推演出无噪声的理想结果。

## isqTrain/1398

- task_id: `isqTrain/1398`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4007`

### Prompt

Create an isQ quantum circuit that the Bernstein-Vazirani algorithm to find the secret string s = 0111 (MSB first). Use 4 input qubits and 1 ancilla.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement Bernstein-Vazirani to find secret string s=0111 using phase oracle and interference.
Qubits: 4 input (q[0..3]) + 1 ancilla (anc[0]); measure the 4 input qubits.
State evolution:
- Initialize |0000⟩|1⟩, apply X to ancilla then H to get |0000⟩|−⟩.
- Apply H to all 4 inputs: (1/4)∑ₓ|x⟩|−⟩ where x ranges over {0,1}⁴.
- Oracle CNOTs from q[1],q[2],q[3] to ancilla apply phase (−1)^(s·x) where s=0111 (bits 1,2,3 set).
- State: (1/4)∑ₓ(−1)^(s·x)|x⟩|−⟩.
- Apply H to all 4 inputs: the Hadamard transform extracts s via ∑ₓ(−1)^((s⊕z)·x) = 4δ_{z,s}, yielding |0111⟩|−⟩.
Measurement yields |0111⟩ with probability 1.0, revealing the secret string.

## isqTrain/3809

- task_id: `isqTrain/3809`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_deriving_gate`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `4591`

### Prompt

帮我写一个isQ程序：the swap test to compare states |1> vs |1>. Use:
1. q[0] as ancilla, q[1] for state A, q[2] for state B
2. A controlled-SWAP (Fredkin) gate via CNOT+Toffoli
3. Hadamard on ancilla before and after CSWAP
4. Measure all 3 qubits. P(ancilla=0) = (1+|<A|B>|²)/2.

### Chain-of-thought reasoning

Let me trace through this swap test circuit step by step.

Initial state: |000⟩ (q[0]=ancilla, q[1]=state A, q[2]=state B)

1. X(q[1]) and X(q[2]): Prepare both states to |1⟩
   State: |011⟩

2. H(q[0]): Hadamard on ancilla
   State: (1/√2)(|011⟩ + |111⟩)

3. Cswap (three-CNOT decomposition) (controlled-swap (three-CNOT decomposition) with q[0] as control):
   - CNOT(q[2], q[1]): 
     |011⟩ → |001⟩ (since q[2]=1, flip q[1]: 1→0)
     |111⟩ → |101⟩ (since q[2]=1, flip q[1]: 1→0)
     State: (1/√2)(|001⟩ + |101⟩)
   
   - Toffoli(q[0], q[1], q[2]):
     |001⟩: q[0]=0, so no flip → |001⟩
     |101⟩: q[0]=1, q[1]=0, so no flip → |101⟩
     State: (1/√2)(|001⟩ + |101⟩)
   
   Wait, let me reconsider the Cswap (three-CNOT decomposition) implementation. The standard decomposition of Cswap (three-CNOT decomposition) is:
   CNOT(control of cswap, target2)
   Toffoli(control of cswap, target2, target1) 
   
   Wait, actually let me re-read the code:
   
   
   Actually, the standard controlled-swap (three-CNOT decomposition) (Cswap (three-CNOT decomposition)) decomposition is:
   CNOT(t2, t1)
   Toffoli(c, t1, t2) 
   CNOT(t2, t1)
   
   where c is the control of the Cswap (three-CNOT decomposition), t1 and t2 are the two targets being swapped.

   Let me verify this with |1⟩|1⟩ inputs when control is |1⟩:
   
   Starting with |1⟩|1⟩|1⟩ (control=1, t1=1, t2=1)
   CNOT(t2=1, t1=1): |1⟩|0⟩|1⟩
   Toffoli(c=1, t1=0, t2=1): since c=1 and t1=0, not both 1, so no flip: |1⟩|0⟩|1⟩
   CNOT(t2=1, t1=0): |1⟩|1⟩|1⟩
   
   That's correct - swapping |1⟩|1⟩ gives |1⟩|1⟩.

   Now let me trace for our case:
   After H(q[0]): (1/√2)(|0⟩ + |1⟩) ⊗ |1⟩ ⊗ |1⟩ = (1/√2)(|011⟩ + |111⟩)

   CNOT(q[2], q[1]):
   |011⟩: q[2]=1, so flip q[1]: |001⟩
   |111⟩: q[2]=1, so flip q[1]: |101⟩
   State: (1/√2)(|001⟩ + |101⟩)

   Toffoli(q[0], q[1], q[2]):
   |001⟩: q[0]=0, so no flip: |001⟩
   |101⟩: q[0]=1, q[1]=0, so no flip (need both controls=1): |101⟩
   State: (1/√2)(|001⟩ + |101⟩)

   CNOT(q[2], q[1]):
   |001⟩: q[2]=1, so flip q[1]: |011⟩
   |101⟩: q[2]=1, so flip q[1]: |111⟩
   State: (1/√2)(|011⟩ + |111⟩)

4. H(q[0]): Hadamard on ancilla
   |011⟩: (1/√2)(|011⟩ + |111⟩)
   |111⟩: (1/√2)(|011⟩ - |111⟩)
   
   Combined: (1/2)(|011⟩ + |111⟩ + |011⟩ - |111⟩) = (1/2)(2|011⟩) = |011⟩

5. Measurement: Always get |011⟩ with probability 1.

This makes sense! When |A⟩ = |

## isqTrain/2031

- task_id: `isqTrain/2031`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2396`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[3];
procedure main() {
    X(q[0]); X(q[1]);
    CNOT(q[0], q[2]);
    CNOT(q[1], q[2]);
    X(q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initialization:** The 3-qubit system starts in the $|000\rangle$ state.
2. **X Gates:** `X(q[0])` and `X(q[1])` flip the first two qubits, evolving the state to $|011\rangle$.
3. **First CNOT:** `CNOT(q[0], q[2])` flips $q_2$ because $q_0$ is $|1\rangle$, changing the state to $|111\rangle$.
4. **Second CNOT:** `CNOT(q[1], q[2])$` flips $q_2$ again because $q_1$ is $|1\rangle$, resulting in state $|011\rangle$.
5. **Final X Gate:** `X(q[2])` flips the third qubit, preparing the final state $|111\rangle$.

**Predicted probability distribution:**
- '111': 1.0

### Reference answer

{'predicted_probs': {'111': 1.0}, 'explanation': 'XNOR(1,1)=1: final state |111>, P=1.0.'}

## isqTrain/4075

- task_id: `isqTrain/4075`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `1783`

### Prompt

下面的量子程序运行结果不对，请帮我debug：

```
import std;
// Inverse QFT on 4 qubits with input |0000>
qbit q[4];

// Entry point
procedure main() {
    // Prepare input

    CNOT(q[0], q[3]);
    // T gate: pi/8 phase
    CNOT(q[3], q[0]);
    CNOT(q[0], q[3]);
    CNOT(q[1], q[2]);
    CNOT(q[2], q[1]);
    CNOT(q[1], q[2]);
    H(q[3]);
    ctrl Rz(2.0 * -2.0 * 3.14159265358979 / 4.0, q[3], q[2]);
    H(q[2]);
    ctrl Rz(-2.0 * 3.14159265358979 / 8.0, q[3], q[1]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[1]);
    ctrl Rz(-2.0 * 3.14159265358979 / 16.0, q[3], q[0]);
    ctrl Rz(-2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    H(q[0]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

Let me analyze this code carefully. The task is a 4-qubit inverse QFT with input |0000>.

Let me look at the buggy code vs the corrected version:

Buggy line:

Fixed line:

The bug is that the first Rz parameter has `2.0 * -2.0` instead of just `-2.0`. This means the rotation angle is twice what it should be (and the sign is positive instead of negative).

`2.0 * -2.0 * PI / 4.0 = -4.0 * PI / 4.0 = -PI`
`-2.0 * PI / 4.0 = -PI/2`

So the buggy code applies Rz(-PI) which is equivalent to Z (up to global phase), while the corrected version should apply Rz(-PI/2) which is equivalent to S†.

Now Let me verify the output. The input is |0000>, and the expected measurement probabilities are uniform (1/16 each for all 16 states). 

Looking at the circuit before the inverse QFT part, the "Prepare input" section applies:
- CNOT(q[0], q[3])
- CNOT(q[3], q[0])  
- CNOT(q[0], q[3])
- CNOT(q[1], q[2])
- CNOT(q[2], q[1])
- CNOT(q[1], q[2])

These are swap (three-CNOT decomposition) operations (CNOT-CNOT-CNOT pattern swaps two qubits). So q[0]↔q[3] and q[1]↔q[2]. But starting from |0000>, swap (three-CNOT decomposition) doesn't change anything - still |0000>.

Then the inverse QFT is applied to |0000>. QFT|0000> = |0000>, so inverse QFT|0000> = |0000>.

Wait, but The predicted output uniform distribution over all 16 states. That doesn't match inverse QFT of |0000>.

Let me reconsider. Maybe the "Prepare input" section actually prepares a superposition or something else.

Wait, CNOT(q[0], q[3]) on |0000> gives |0000>. All the CNOTs on |0000> give |0000>. So the input to inverse QFT is |0000>.

QFT|0>^4 = (1/4) * |0>^4... no. QFT maps |0>^n to a uniform superposition: (1/sqrt(2^n)) * sum of |k> for k=0..2^n-1.

Wait, QFT|0...0> = (1/sqrt(N)) * sum_{k=0}^{N-1} |k>, which is a uniform superposition over all computational basis states.

So inverse QFT of |0...0> should also be |0...0> since QFT|0...0> = uniform superposition, but inverse QFT|0...0> should give back... 

Actually, QFT is a unitary transform. QFT|0...0> = (1/sqrt(N)) sum |k>. So inverse QFT applied to (1/sqrt(N)) sum |k> = |0...0>. But inverse QFT applied to |0...0> = ?

Inverse QFT|0...0> = (QFT)†|0...0>. Since QFT|k> = superposition involving all basis states, (QFT)†|0...0> = some specific state...

Actually, for the QFT matrix, the (j,k) entry is ω^{jk}/sqrt(N) where ω = e^{2πi/N}. The inverse QFT has entries ω^{-jk}/sqrt(N).

So inverse QFT|0⟩ = (1/sqrt(N)) sum_k |k⟩ because the 0th column of the inverse QFT matrix is all 1/sqrt(N).

Wait, that's the same as QFT|0⟩. So inverse QFT|0000⟩ = uniform superposition, which gives uniform measurement probabilities. That matches the predicted output!

So the circuit is: prepare |0000>, apply inverse QFT, get uniform superposition, measure uniformly.

The bug: the first controlled Rz after H(q[3]) has angle `2.0 * -2.0 * PI / 4.0 = -PI` instead of `-2.0 * PI

## isqTrain/1888

- task_id: `isqTrain/1888`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_deriving_gate`, `isq_syntax_procedures`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `343`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[3];
procedure my_z(qbit a) {
    Z(a);
} deriving gate
procedure main() {
    X(q[2]);
    H(q[0]); H(q[1]);
    ctrl my_z(q[1], q[2]);
    CNOT(q[0], q[1]); CNOT(q[1], q[0]); CNOT(q[0], q[1]);
    H(q[1]);
    ctrl Rz(-pi/2.0, q[0], q[1]);
    H(q[0]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a step-by-step analysis of an isQ quantum program to predict the probability distribution of its measurement outcomes.

2.  **Analyze the isQ Code**:
    *   `qbit q[3];`: 3 qubits, initialized to $|0\rangle^{\otimes 3}$.
    *   `X(q[2]);`: q[2] becomes $|1\rangle$.
    *   `H(q[0]); H(q[1]);`: q[0] becomes $|+\rangle$, q[1] becomes $|+\rangle$.
        State: $\frac{1}{2}(|000\rangle + |010\rangle + |100\rangle + |110\rangle)$ -> wait, q[2] is 1.
        State is $\frac{1}{2}(|001\rangle + |011\rangle + |101\rangle + |111\rangle)$.
    *   `ctrl my_z(q[1], q[2]);`: controlled-Z with control q[1] and target q[2].
        Since q[2] is $|1\rangle$, it flips the sign if q[1] is $|1\rangle$.
        State: $\frac{1}{2}(|001\rangle + |011\rangle + |101\rangle - |111\rangle)$.
    *   `CNOT(q[0], q[1]); CNOT(q[1], q[0]); CNOT(q[0], q[1]);`: This is a swap operation (three-CNOT decomposition) between q[0] and q[1].
        Wait, swap(0, 1) via three CNOTs applied to $\frac{1}{2}(|001\rangle + |011\rangle + |101\rangle - |111\rangle)$.
        Let's trace it:
        |00> -> |00>
        |01> -> |10>
        |10> -> |01>
        |11> -> |11>
        So, state becomes $\frac{1}{2}(|001\rangle + |101\rangle + |011\rangle - |111\rangle)$.
    *   `H(q[1]);`:
        Apply H to q[1].
        |00> -> |0+> = $\frac{1}{\sqrt{2}}(|00\rangle + |01\rangle)$
        |10> -> |1+> = $\frac{1}{\sqrt{2}}(|10\rangle + |11\rangle)$
        |01> -> |0-> = $\frac{1}{\sqrt{2}}(|00\rangle - |01\rangle)$
        |11> -> |1-> = $\frac{1}{\sqrt{2}}(|10\rangle - |11\rangle)$

        Let's write the state carefully. Let qubits be q[0], q[1]. q[2] is just $|1\rangle$.
        Initial state before H(q[1]):
        $|0\rangle_0 |1\rangle_1 + |1\rangle_0 |0\rangle_1 + |0\rangle_0 |1\rangle_1 - |1\rangle_0 |1\rangle_1$ -- wait, the state was $\frac{1}{2}(|001\rangle + |101\rangle + |011\rangle - |111\rangle)$.
        In binary: q[0]q[1]q[2]
        State is $\frac{1}{2} (|01\rangle + |10\rangle + |01\rangle - |11\rangle) \otimes |1\rangle$
        = $\frac{1}{2} (2|01\rangle + |10\rangle - |11\rangle) \otimes |1\rangle$
        = $\frac{1}{2} (2|0\rangle_0|1\rangle_1 + |1\rangle_0(|0\rangle_1 - |1\rangle_1)) \otimes |1\rangle_2$

        Apply H to q[1]:
        $|1\rangle_1 \to |-\rangle_1 = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$
        $|0\rangle_1 \to |+\rangle_1 = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$

        So, $2|0\rangle_0|-\rangle_1 + |1\rangle_0(|+\rangle_1 - |-\rangle_1)$
        $|+\rangle - |-\rangle = \sqrt{2}|1\rangle$.
        State becomes: $2|0

### Reference answer

{'predicted_probs': {'00': 0.1464, '10': 0.8536}, 'explanation': '2-bit QPE for Z gate (phase=0.5). Most likely state |10⟩ with P ≈ 0.854. Some leakage to |00⟩ due to limited precision.'}

## isqTrain/2976

- task_id: `isqTrain/2976`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `298`

### Prompt

Implement a quantum circuit in isQ: applies 3 layer(s) of Hadamard + CNOT ring on 4 qubits. Each layer applies H to all qubits, then CNOT in a ring (q[i] -> q[(i+1)%4]).

Requirements:
- Declare `qbit q[4];` at global scope.
- Measure all 4 qubits.

### Chain-of-thought reasoning

Let me analyze this circuit carefully.

The circuit applies 3 layers of H+CNOT on 4 qubits. Each layer:
1. Apply H to all 4 qubits
2. Apply CNOT in a ring: q[0]→q[1], q[1]→q[2], q[2]→q[3], q[3]→q[0]

Let me trace through the state evolution.

Initial state: |0000⟩

**Layer 1:**
After H on all qubits: |++++⟩ = (1/4) Σ_{x∈{0,1}^4} |x⟩

After CNOT ring:
- CNOT(0,1): entangles q0 and q1
- CNOT(1,2): entangles q1 and q2
- CNOT(2,3): entangles q2 and q3
- CNOT(3,0): entangles q3 and q0

The CNOT ring on |++++⟩... Let me think about this more carefully.

After H on all: each qubit is in |+⟩, so the state is |+⟩|+⟩|+⟩|+⟩ = (1/4)Σ|x⟩

After CNOT ring on the uniform superposition: The CNOT ring maps |x₀x₁x₂x₃⟩ → |x₀, x₀⊕x₁, x₁⊕x₂, x₂⊕x₃⟩... wait, but then the last CNOT(3,0) maps this further.

Actually, let me think about what the CNOT ring does as a unitary. Let's denote the map:
- CNOT(0,1): x₁ → x₀⊕x₁
- CNOT(1,2): x₂ → x₁⊕x₂ = x₀⊕x₁⊕x₂ (using updated x₁)
- CNOT(2,3): x₃ → x₂⊕x₃ = x₀⊕x₁⊕x₂⊕x₃ (using updated x₂)
- CNOT(3,0): x₀ → x₃⊕x₀ = x₀⊕x₀⊕x₁⊕x₂⊕x₃ = x₁⊕x₂⊕x₃

Wait, I need to be more careful. After CNOT(2,3), x₃ becomes x₂⊕x₃ = (x₀⊕x₁⊕x₂)⊕x₃. Then CNOT(3,0) means q3 controls q0, so x₀ becomes x₀⊕x₃_new = x₀⊕(x₀⊕x₁⊕x₂⊕x₃) = x₁⊕x₂⊕x₃.

So after the CNOT ring:
|x₀,x₁,x₂,x₃⟩ → |x₁⊕x₂⊕x₃, x₀⊕x₁, x₀⊕x₁⊕x₂, x₀⊕x₁⊕x₂⊕x₃⟩

This is a permutation of the computational basis (up to XOR operations), so applied to a uniform superposition, it still gives a uniform superposition.

Actually, let me verify: the CNOT ring is a unitary that permutes the computational basis states (since each CNOT permutes basis states). When applied to a uniform superposition over all basis states, it gives back a uniform superposition over all basis states.

So after Layer 1: still (1/4)Σ|x⟩ = |++++⟩

Wait, is that right? A permutation of basis states applied to an equal superposition of all basis states gives the same state back (up to global phase). So yes, after Layer 1, the state is still |++++⟩.

But then Layer 2 applies H to all again. H|+⟩ = |0⟩. So after H on all qubits in Layer 2: |0000⟩.

Then CNOT ring on |0000⟩: CNOT does nothing when control is |0⟩, so the state remains |0000⟩.

Then Layer 3: H on all qubits → |++++⟩ again. CNOT ring on |++++⟩ → |++++⟩.

Final state: |++++⟩ = (1/4)Σ|x⟩

Measurement probabilities: each of the 16 basis states has probability (1/4)² = 1/16 = 0.0625.

This matches the predicted output!

So the key insight is:
1. After Layer 1: |0000⟩ →H×4→ |++++⟩ → CNOT ring → |++++⟩ (uniform superposition is invariant under permutation)
2. After Layer 2 H: |++++⟩ →H×4→ |0000⟩ → CNOT ring → |0000⟩
3. After Layer 3 H: |0000⟩ →

## isqTrain/3559

- task_id: `isqTrain/3559`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `multi_controlled_logic`, `reversible_computing`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `3881`

### Prompt

Fix the bug in the following isQ program.

Bug description: Wrong CNOT direction

The program should 1-bit full adder: 1+1+1 = sum=1 carry=1.

### Chain-of-thought reasoning

## Bug Analysis

1. **The bug** is in Step 2: `CNOT(q[1], q[0])` has reversed arguments. This makes q[1] the control and q[0] the target, XORing q[1] into q[0] instead of the intended XOR of q[0] into q[1]. This corrupts q[0] (the input `a`), which is still needed as a control in the subsequent Toffoli gate and for preserving the input value.

2. **The fix** is changing `CNOT(q[1], q[0])` to `CNOT(q[0], q[1])`, so q[0] controls and q[1] is the target, correctly computing `a XOR b` into q[1].

3. **Corrected state evolution** (starting from |1111⟩ after input initialization):
   - **Step 1:** Toffoli(q[0],q[1],q[3]) fires (q[0]=1, q[1]=1) → q[3]=1 → |1111⟩
   - **Step 2:** CNOT(q[0],q[1]): q[0]=1, so q[1] flips 1→0 → |1011⟩ (a XOR b = 0 stored in q[1])
   - **Step

## isqTrain/1165

- task_id: `isqTrain/1165`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1195`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;

// MCMT with controls in superposition
qbit q[4];

procedure main() {
    // Put controls in superposition |+>
    H(q[0]); H(q[1]);
    // Doubly-controlled X on first target
    // Only |11> component of controls triggers flip
    ctrl ctrl X(q[0], q[1], q[2]);
    // Doubly-controlled X on second target
    ctrl ctrl X(q[0], q[1], q[3]);
    // Measure all qubits
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Role:** Quantum computing expert.
    *   **Format:** Concise step-by-step reasoning, 3-15 lines. Use Dirac notation.
    *   **Output:** Start with "## Circuit Analysis", no code blocks, end with predicted probability distribution.
    *   **Input program:**
        *   4 qubits, initialized to |0000>.
        *   H(q[0]), H(q[1]) -> q0, q1 are in |+>.
        *   ctrl ctrl X(q[0], q[1], q[2]) -> Toffoli gate targeting q[2].
        *   ctrl ctrl X(q[0], q[1], q[3]) -> Toffoli gate targeting q[3].
        *   Measure all.

2.  **Trace the State Evolution:**
    *   Initial state: $|0000\rangle$ (using standard ordering $q_0 q_1 q_2 q_3$, though measurement strings often map earlier qubits to higher bits, let's keep Dirac notation clear: $|q_0 q_1 q_2 q_3\rangle$). Let's check isQ measurement string mapping: "earlier measured qubit = higher bit". So $M(q_0)$ is the highest bit, $M(q_3)$ is the lowest bit. String = $q_0 q_1 q_2 q_3$.
    *   After $H(q_0)H(q_1)$:
        $|q_0 q_1\rangle = \frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)$.
        Combined state: $\frac{1}{2}(|0000\rangle + |0100\rangle + |1000\rangle + |1100\rangle)$.
    *   Apply `ctrl ctrl X(q[0], q[1], q[2])`:
        Flips $q_2$ if $q_0=1, q_1=1$.
        State: $\frac{1}{2}(|0000\rangle + |0100\rangle + |1000\rangle + |1110\rangle)$.
    *   Apply `ctrl ctrl X(q[0], q[1], q[3])`:
        Flips $q_3$ if $q_0=1, q_1=1$.
        State: $\frac{1}{2}(|0000\rangle + |0100\rangle + |1000\rangle + |1111\rangle)$.
    *   Measurement probabilities:
        Each term has amplitude $1/2$, so probability $(1/2)^2 = 0.25$.
        Outcomes: 0000, 0100, 1000, 1111.

3.  **Draft the Explanation (adhering to constraints):**
    *   Start with `## Circuit Analysis`.
    *   Gate list: H on q[0], q[1]; Toffoli on q[0], q[1], q[2]; Toffoli on q[0], q[1], q[3].
    *   Evolution:
        *   Initial: |0000>
        *   After H gates: 0.5(|0000> + |0100> + |1000> + |1100>)
        *   After 1st Toffoli: 0.5(|0000> + |0100> + |1000> + |1110>)
        *   After 2nd Toffoli: 0.5(|0000> + |0100> + |1000> + |1111>)
    *   Final output format.

4.  **Refine for Conciseness (target 3-15 lines):**
    ## Circuit Analysis
    1. Operations: H gates on q[0] and q[1], followed by two Toffoli (ctrl ctrl X) gates both controlled by q[0], q[1] targeting q[2] and q[3] respectively.
    2. State evolution:
       - Initial state: |0000>
       - H gates create superposition on controls: 0.5(|0000> + |0100> + |1000> + |1100>)
       - 1st Toffoli flips q[2] when q[0]=q[1]=|1>: 0.5(|0000> + |0100> + |1000> + |1110>)
       - 2nd Toffoli flips q[3] when q[0]=q[1]=|1>: 0.5(|0000> + |0100> + |1000

### Reference answer

{'predicted_probs': {'0': 0.25, '4': 0.25, '8': 0.25, '15': 0.25}, 'explanation': 'Parametric variant of isqEval/443. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3429

- task_id: `isqTrain/3429`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `799`

### Prompt

I need an isQ program to the Draper QFT-based adder in isQ for 2-qubit numbers.

The Draper adder adds two numbers using QFT:
1. Apply QFT to register b
2. Apply controlled phase rotations from register a
3. Apply inverse QFT to register b
Result: b holds a+b (mod 2^n)

Compute 01 + 01 = 10 (1 + 1 = 2).
- q[0..1] = a = 01, q[2..3] = b = 01 (LSB first)

Declare 4 global qubits, measure all. Expected: a=01 unchanged, b=10.

### Chain-of-thought reasoning

Let me trace through this Draper QFT-based adder step by step.

**Initial state:** |0000⟩
- q[0]=a₀, q[1]=a₁, q[2]=b₀, q[3]=b₁

**After X(q[0]) and X(q[2]):** |0101⟩
- a = 01 (value 1), b = 01 (value 1)

**QFT on b register (q[2], q[3]):**

Step 1: H(q[2]) on |01⟩_b → (|0⟩+|1⟩)|1⟩/√2 = (|01⟩+|11⟩)/√2

Step 2: CRz(π/2) from q[3] to q[2]: This applies Rz(π/2) to q[2] when q[3]=|1⟩
The state is (|0⟩+|1⟩)|1⟩/√2
When q[3]=|1⟩, apply Rz(π/2) to q[2]: |0⟩→|0⟩, |1⟩→e^{iπ/4}|1⟩... wait, let me reconsider.

Actually, Rz(θ) = diag(1, e^{iθ}). So Rz(π/2) on |0⟩ = |0⟩, Rz(π/2) on |1⟩ = e^{iπ/2}|1⟩ = i|1⟩.

Wait, but the controlled version: ctrl Rz(1.5707..., q[3], q[2]) means q[3] controls, q[2] is target.

State after H(q[2]): |0⟩_a ⊗ (|0⟩+|1⟩)/√2 ⊗ |1⟩_b1

Wait, let me be more careful. The full state is:
|a₀a₁b₀b₁⟩ = |0101⟩

After H(q[2]):
q[2] was |1⟩ → H|1⟩ = (|0⟩-|1⟩)/√2

Hmm wait, a₀=q[0]=|1⟩, a₁=q[1]=|0⟩, b₀=q[2]=|1⟩, b₁=q[3]=|0⟩

State: |1,0,1,0⟩

After H(q[2]): |1,0⟩ ⊗ (|0⟩-|1⟩)/√2 ⊗ |0⟩ = |1⟩|0⟩(|0⟩-|1⟩)/√2 |0⟩

After ctrl Rz(π/2, q[3], q[2]): q[3]=|0⟩, so no rotation applied. State unchanged.

After H(q[3]): q[3] was |0⟩ → (|0⟩+|1⟩)/√2

State: |10⟩ ⊗ (|0⟩-|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2

After swap(q[2], q[3]): swap the b register
(|0⟩-|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 → after swap: (|0⟩+|1⟩)/√2 ⊗ (|0⟩-|1⟩)/√2

Hmm, this is getting complex. Let me just think about the QFT of the b register value.

b = 01 (LSB first) = value 1 in decimal (binary 01, b₀=1, b₁=0).

QFT on 2-qubit value 1:
The QFT of |1⟩ (value 1 in a 2-qubit system, which is |01⟩ in computational basis where the first qubit is LSB... actually I need to be careful about bit ordering.

In the code, b₀ = q[2] and b₁ = q[3]. The value of b is b₀ + 2*b₁ = 1 + 0 = 1.

The QFT maps |j⟩ → (1/√N) Σ_k e^{2πijk/N} |k⟩ where N = 4.

QFT|1⟩ = (1/2)(|0⟩ + e^{iπ/2}|1⟩ + e^{iπ}|2⟩ + e^{i3π/2}|3⟩)
= (1/2)(|0⟩ + i|1⟩ - |2⟩ - i|3⟩)

**Phase rotations from a to b in Fourier space:**

For the Draper adder, when a has value m, we apply phase rotations to add m to b in Fourier space:
- For each bit a[j], apply controlled phase Rz(2π/

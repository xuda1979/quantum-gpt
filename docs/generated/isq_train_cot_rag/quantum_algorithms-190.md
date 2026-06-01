# ISQ training COT RAG corpus: quantum_algorithms shard 190

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/890

- task_id: `isqTrain/890`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3707`

### Prompt

Help me write isQ code that implements the phase_oracle pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a phase oracle that flips the phase of |11⟩, then measure with reversed qubit order to show phases don't affect measurement probabilities.

2. **Qubits**: 2 qubits (q[0], q[1]), both measured.

3. **State evolution**:
   - Initial: |00⟩
   - After H⊗H: (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
   - After ctrl my_z(q[0], q[1]) [CZ]: (|00⟩ + |01⟩ + |10⟩ - |11⟩)/2

4. **Probability explanation**: Measurement in the computational basis yields probabilities |⟨00|ψ⟩|² = |⟨01|ψ⟩|² = |⟨10|ψ⟩|² = |⟨11|ψ⟩|² = (1/2)² = 0.25 each. The phase flip on |11⟩ is invisible to measurement, giving a uniform distribution. The reversed measurement order (M(q[1]) before M(q[0])) swaps the bit significance: q[1] becomes the higher bit, so bitstring indexing maps (q[1], q[0]) → probability index.

## isqTrain/2792

- task_id: `isqTrain/2792`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4369`

### Prompt

Something is wrong with this isQ circuit. Identify the error and provide the corrected code.

```isq
import std;
qbit q[3];

procedure main(){
    // H(q[0]); // BUG: missing Hadamard
    X2P(q[1]);
    CZ(q[0], q[2]);
    Y2M(q[0]);
    CZ(q[2], q[1]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
    //H Q1\nX2P Q2\nCZ Q1 Q3\nY2M Q1\nCZ Q3 Q2"
}
```

### Chain-of-thought reasoning

The user wants a bug analysis for an isQ quantum program.
The buggy code is missing `H(q[0]);` which is commented out.
The expected measurement probabilities are {|000>: 0.5, |010>: 0.5}.
The fix is to uncomment `H(q[0]);`.

Let's trace the corrected circuit:
Initial state: |000>
H(q[0]) -> (|0> + |1>)/sqrt2 |00> = (|000> + |100>)/sqrt2
X2P(q[1]) -> (|000> + |100>)/sqrt2 * X2P on q1.
Wait, X2P = Rx(pi/2).
|0> acted by Rx(pi/2) is (|0> - i|1>)/sqrt2.
So (|000> + |100>)/sqrt2 -> (1/sqrt2) ( (|0>-i|1>)/sqrt2 |00> + |1>(|0>-i|1>)/sqrt2 |00> )
Wait, the order of qubits is q[0], q[1], q[2].
So X2P(q[1]) applies Rx(pi/2) to q[1].
State becomes: 1/2 (|000> - i|010> + |100> - i|110>)
CZ(q[0], q[2]) applies Z to q[2] when q[0] is |1>.
State becomes: 1/2 (|000> - i|010> + |101> - i|111>)
Y2M(q[0]) applies Ry(-pi/2) to q[0].
Ry(-pi/2) maps |0> to (|0> + |1>)/sqrt2 and |1> to (-|0> + |1>)/sqrt2.
Wait, Ry(theta) = [[cos(theta/2), -sin(theta/2)], [sin(theta/2), cos(theta/2)]].
Ry(-pi/2) = [[1/sqrt2, 1/sqrt2], [-1/sqrt2, 1/sqrt2]].
So |0> -> (|0> - |1>)/sqrt2
|1> -> (|0> + |1>)/sqrt2
Let's re-evaluate Ry(-pi/2) on q[0]:
q[0] is in |0>, gets mapped to (|0> - |1>)/sqrt2.
q[0] is in |1>, gets mapped to (|0> + |1>)/sqrt2.
Wait, Y2M is Ry(-pi/2).
Matrix Ry(-pi/2): cos(-pi/4) = 1/sqrt2. -sin(-pi/4) = 1/sqrt2. sin(-pi/4) = -1/sqrt2.
So Ry(-pi/2) = [[1/sqrt2, 1/sqrt2], [-1/sqrt2, 1/sqrt2]].
|0> -> 1/sqrt2 |0> - 1/sqrt2 |1> = (|0>-|1>)/sqrt2.
|1> -> 1/sqrt2 |0> + 1/sqrt2 |1> = (|0>+|1>)/sqrt2.
So applying Y2M to q[0]:
1/2 [ ( (|0>-|1>)/sqrt2 )|00> - i ( (|0>-|1>)/sqrt2 )|10> + ( (|0>+|1>)/sqrt2 )|01> - i ( (|0>+|1>)/sqrt2 )|11> ]
= 1/(2sqrt2) [ |000> - |100> - i|010> + i|110> + |001> + |101> - i|011> - i|111> ]
Now CZ(q[2], q[1]). CZ on q[1] controlled by q[2]. (Z on q[1] if q[2] is |1>).
Wait, Z on q[1] flips the sign of |1> in q[1].
Terms with |1> in q[1] and |1> in q[2] get a minus sign:
-i|011> and -i|111> become +i|011> and +i|111>.
Wait, let's carefully check the indices:
q[0], q[1], q[2]
CZ(q[2], q[1]) applies Z to q[1] controlled by q[2].
So the term -i|011> (q[0]=0, q[1]=1, q[2]=1) gets its sign

## isqTrain/3953

- task_id: `isqTrain/3953`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`, `isq_syntax_inv`
- source: `isq_train_cot`
- dataset_index: `3195`

### Prompt

I'm getting wrong output from this isQ code. What's the bug and how do I fix it?

```
import std;
// Inverse QFT on 4 qubits with input |1010>
qbit q[4];

// Entry point
procedure main() {
    // Prepare input
    X(q[0]);
    // X gate: flip qubit state
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
    // BUG: missing gate here
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    H(q[1]);
    ctrl Rz(-2.0 * 3.14159265358979 / 16.0, q[3], q[0]);
    ctrl Rz(-2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    ctrl Rz(-2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    H(q[0]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

Let me analyze this buggy isQ code for a 4-qubit inverse QFT with input |1010>.

First, let me understand the structure:
- Input state: |1010> (q[0]=0, q[1]=1, q[2]=0, q[3]=1 in little-endian, or depending on convention, q[0] might be the least significant bit)

Wait, let me reconsider. The input |1010> means:
- If q[0] is the least significant bit (bit 0), then |1010> means q[3]=1, q[2]=0, q[1]=1, q[0]=0
- But the code prepares: X(q[0]) and X(q[2]), which flips q[0] and q[2]

So if the initial state is |0000> and we apply X to q[0] and q[2], we get |0101> in the standard notation where q[0] is the LSB.

Hmm, but the comment says "input |1010>". Let me think about this differently.

Actually, looking at the predicted output, all 16 states have equal probability of 0.0625 (1/16). This suggests that the inverse QFT of a specific computational basis state should give a uniform superposition over all states.

Wait, that's not quite right. The QFT of a computational basis state gives a state with specific phase relationships. The inverse QFT of a computational basis state should give a uniform superposition.

Actually, let me reconsider. The inverse QFT maps |x> to (1/√N) Σ |k> * e^{-2πixk/N}. So for any computational basis state, we get a uniform superposition with equal amplitudes (just different phases).

So yes, the measurement probabilities should all be 1/16 = 0.0625.

Now let me look at the inverse QFT structure. The standard inverse QFT on n qubits involves:
1. For qubit n-1 (most significant): H(q[n-1])
2. For qubit n-2: controlled Rz(-π/2) from q[n-1], then H(q[n-2])
3. And so on...

Wait, I need to be more careful. The inverse QFT typically involves:
- Starting from the most significant qubit
- For each qubit j (from n-1 down to 0):
  - Apply controlled rotations from higher-indexed qubits
  - Apply H

But looking at this code, there's also swap (three-CNOT decomposition) operations at the beginning (CNOT triplets are SWAPs).

The swap (three-CNOT decomposition) operations are:
- swap (three-CNOT decomposition)(q[0], q[3])
- swap (three-CNOT decomposition)(q[1], q[2])

This is typical of QFT - you need to swap the qubits at the end because the QFT reverses the order.

After the swaps, the state should be:
- Originally |1010> → after swap (three-CNOT decomposition)(q[0], q[3]) and swap (three-CNOT decomposition)(q[1], q[2]) → |0101>

Hmm wait, let me reconsider the bit ordering. If the original state is |1010> in binary:
- Bit 3 (MSB): 1
- Bit 2: 0
- Bit 1: 1
- Bit 0 (LSB): 0

So q[0]=0, q[1]=1, q[2]=0, q[3]=1.

The preparation code is:
- X(q[0]) → q[0] becomes 1
- X(q[2]) → q[2] becomes 1

So after preparation: q[0]=1, q[1]=0, q[2]=1, q[3]=0

In standard binary notation with q[0] as LSB: |0101> = 5 in decimal.

But the comment says "input |1010>" = 10 in decimal.

Hmm, there might be a different convention. Let me just follow the code.

After SWAPs:
- swap (three-CNOT decomposition)(q[0], q[3]): q[0]↔q[3], so q[0]=0, q[3]=1
- swap (three-CNOT decomposition)(q[1], q[2]): q[1]↔q[2], so q[1]=1, q[2]=0

So after SWAPs: q[0]=0, q[1]=1, q[2]=0, q[3]=1

Now the inverse QFT operations. Looking at the pattern:
1. H(q[3])
2. ctrl Rz(-2π/4, q[3], q[2]) - rotation on q[2] controlled by q[3]
3. H(q[2])
4. ctrl

## isqTrain/3727

- task_id: `isqTrain/3727`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `4521`

### Prompt

Help me write isQ code that QAOA (p=1) for MaxCut on a 4-node star graph with edges [(0, 1), (0, 2), (0, 3)], gamma=0.785, beta=0.393. Use CNOT-Rz-CNOT for cost unitary and Rx for mixer.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for the QAOA MaxCut circuit on a 4-node star graph.

Let me trace through the circuit:

1. **Goal**: Implement QAOA (p=1) for MaxCut on a 4-node star graph with edges [(0,1), (0,2), (0,3)].

2. **Qubits**: 4 qubits (q[0], q[1], q[2], q[3]), all measured.

3. **State evolution**:

**Initial state**: |0000⟩

**After Hadamards**: |++++⟩ = H⊗4|0000⟩ (equal superposition over all 16 basis states)

**Cost unitary**: For each edge (i,j), we apply CNOT(i,j) · Rz(2γ, j) · CNOT(i,j), which implements the controlled-Z rotation exp(-iγ Z_i Z_j).

For edge (0,1):
- The CNOT-Rz(2γ)-CNOT sequence on (q[0], q[1]) applies e^{-iγ Z₀Z₁} to the state

For edge (0,2):
- Similarly applies e^{-iγ Z₀Z₂}

For edge (0,3):
- Similarly applies e^{-iγ Z₀Z₃}

With γ = 0.785 ≈ π/4, the cost unitary is:
U_C = e^{-iγ(Z₀Z₁ + Z₀Z₂ + Z₀Z₃)}

This means:
- States where q[0] agrees with an even number of others get phase e^{-iγ}
- States where q[0] agrees with an odd number of others get phase e^{iγ}

Actually, let me think more carefully. The cost unitary is:
e^{-iγ Z₀Z₁} · e^{-iγ Z₀Z₂} · e^{-iγ Z₀Z₃}

For a basis state |q₀q₁q₂q₃⟩, the eigenvalue of Z₀Zⱼ is (-1)^{q₀⊕qⱼ} = 1 if q₀=qⱼ, -1 if q₀≠qⱼ.

So the total phase accumulated is:
-γ(Z₀Z₁ + Z₀Z₂ + Z₀Z₃) applied to the state

For MaxCut, the cost is C = Σ_{(i,j)∈E} (1 - ZᵢZⱼ)/2

So maximizing C means minimizing Σ ZᵢZⱼ.

The cost Hamiltonian for QAOA is typically -C or C itself. Looking at the circuit, Rz(2γ) gives eigenvalue phases.

Let me think about what happens to each computational basis state:

For |0000⟩: Z₀Z₁=1, Z₀Z₂=1, Z₀Z₃=1, sum=3, phase = -3γ
For |0001⟩: Z₀Z₁=1, Z₀Z₂=1, Z₀Z₃=-1, sum=1, phase = -γ
For |0111⟩: Z₀Z₁=-1, Z₀Z₂=-1, Z₀Z₃=-1, sum=-3, phase = 3γ
For |1111⟩: Z₀Z₁=1, Z₀Z₂=1, Z₀Z₃=1, sum=3, phase = -3γ

Actually wait, the sign depends on the exact implementation. The CNOT-Rz(2γ)-CNOT implements a controlled-Rz which is equivalent to e^{-iγZ_cZ_t}.

After superposition |++++⟩, the state is:
(1/4) Σ_{q₀,q₁,q₂,q₃} |q₀q₁q₂q₃⟩

After cost unitary:
(1/4) Σ_{q₀,q₁,q₂,q₃} e^{-iγ(z₀z₁+z₀z₂+z₀z₃)} |q₀q₁q₂q₃⟩

where z_i = 1-2q_i.

Then mixer Rx(2β) on each qubit applies:
e^{-iβX_i} to each qubit

With β = 0.393 ≈ π/8.

Let me compute the predicted output based on the symmetry of the star graph.

The states with the same "type" should have the same probability:
- |0000⟩ and |1111⟩: all same
- |0111⟩ and |1000⟩: center different from all leaves
- |0001⟩, |0010⟩, |0100⟩ and |1110⟩, |1101⟩, |1011⟩: center same as

## isqQA/quantum_algorithms/135_step_by_step

- task_id: `isqQA/quantum_algorithms/135_step_by_step`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `step_by_step`, `algorithm`, `Swap测试`
- source: `qa_pipeline`
- dataset_index: `2867`

### Prompt

我正在学习量子算法中的Swap测试，我知道它是用来计算两个量子态内积的，但我对底层的计算过程和概率推导感到非常困惑。作为初学者，能否一步步地手动追踪Swap测试的数学演化过程，并解释为什么第一个量子比特的测量概率会与两个量子态内积的模平方有关？最后，请务必提供一个完整的isQ代码示例，展示如何对两个单量子态执行Swap测试并测量控制位。

### Reference answer

<think>
要解答这个问题，推理的核心在于通过严格的线性代数演算追踪量子态的演化，并最终将测量概率的公式与内积定义联系起来。

首先，明确系统的初始状态，并对辅助比特施加Hadamard门，使其进入|0⟩和|1⟩的等权叠加态。接着执行受控SWAP操作，这一步在数学上表现为：只有当辅助比特处于|1⟩时，才交换目标态|ψ⟩和|ϕ⟩的位置。

推导的关键在于第二次施加Hadamard门。利用H门的定义将辅助比特的|0⟩和|1⟩基矢重新组合，并按辅助比特的状态对整个系统的态矢量进行整理合并。在计算辅助比特最终处于|0⟩的概率时，需要对其对应的系数项求模平方。在展开这个模平方的过程中，会产生目标量子态之间的交叉乘积项，即⟨ψ|ϕ⟩⟨ϕ|ψ⟩。根据线性代数原理，这正好等于内积的模平方|⟨ψ|ϕ⟩|²，从而在数学上解释了概率与内积的联系。最后，依据上述物理电路结构，使用isQ语言的语法规则逐步实例化量子比特并添加相应的逻辑门即可得到代码。
</think>

 Swap测试是量子机器学习和量子信息处理中极其重要的基础算法。为了让你彻底弄懂它，我们一步步来手动追踪系统的量子态演化过程。

假设我们有三个量子比特：第一个是辅助比特（记作 q[0] ），初始化为 |0⟩ ；第二个比特存入量子态 |ψ⟩（记作 q[1] ）；第三个比特存入量子态 |ϕ⟩（记作 q[2] ）。系统的初始状态为：
|Ψ₀⟩ = |0⟩ ⊗ |ψ⟩ ⊗ |ϕ⟩

**第一步：对辅助比特施加Hadamard门**
我们将辅助比特 |0⟩ 转化为叠加态 |+⟩：
|Ψ₁⟩ = (1/√2)(|0⟩ + |1⟩) ⊗ |ψ⟩ ⊗ |ϕ⟩
展开后得到：
|Ψ₁⟩ = (1/√2)(|0⟩|ψ⟩|ϕ⟩ + |1⟩|ψ⟩|ϕ⟩)

**第二步：执行受控交换操作**
当辅助比特处于 |1⟩ 状态时，我们交换第二个和第三个比特；若辅助比特为 |0⟩ ，则不进行任何操作。由于 |ψ⟩ 和 |ϕ⟩ 在交换后位置互换，状态演化为：
|Ψ₂⟩ = (1/√2)(|0⟩|ψ⟩|ϕ⟩ + |1⟩|ϕ⟩|ψ⟩)

**第三步：再次对辅助比特施加Hadamard门**
Hadamard门会将 |0⟩ 映射为 (1/√2)(|0⟩ + |1⟩) ，将 |1⟩ 映射为 (1/√2)(|0⟩ - |1⟩) 。代入 |Ψ₂⟩ 中，我们得到：
|Ψ₃⟩ = (1/2) [ (|0⟩ + |1⟩)|ψ⟩|ϕ⟩ + (|0⟩ - |1⟩)|ϕ⟩|ψ⟩ ]
我们将辅助比特的状态提取出来进行合并整理：
|Ψ₃⟩ = (1/2)|0⟩ (|ψ⟩|ϕ⟩ + |ϕ⟩|ψ⟩) + (1/2)|1⟩ (|ψ⟩|ϕ⟩ - |ϕ⟩|ψ⟩)

**第四步：计算测量概率**
根据量子力学的测量公理，辅助比特被测量为 |0⟩ 的概率 P(0) 等于其对应系数的模平方。也就是对 (1/2)(|ψ⟩|ϕ⟩ + |ϕ⟩|ψ⟩) 求内积：
P(0) = (1/4) (⟨ψ|⟨ϕ| + ⟨ϕ|⟨ψ|)(|ψ⟩|ϕ⟩ + |ϕ⟩|ψ⟩)
将其展开并利用内积的性质（假设 |ψ⟩ 和 |ϕ⟩ 均已归一化，即 ⟨ψ|ψ⟩=1 且 ⟨ϕ|ϕ⟩=1 ）：
P(0) = (1/4) [ ⟨ϕ|ψ⟩⟨ϕ|ψ⟩ + ⟨ϕ|ϕ⟩⟨ψ|ψ⟩ + ⟨ψ|ϕ⟩⟨ψ|ϕ⟩ + ⟨ψ|ψ⟩⟨ϕ|ϕ⟩ ]
由于 ⟨ϕ|ψ⟩ 和 ⟨ψ|ϕ⟩ 互为共轭复数，它们的模平方相等，即 |⟨ϕ|ψ⟩|² = |⟨ψ|ϕ⟩|² 。因此我们可以化简得到：
P(0) = (1/4) [ 2|⟨ψ|ϕ⟩|² + 1 + 1 ] = (1 + |⟨ψ|ϕ⟩|²) / 2

这就是最核心的结论！如果两个量子态完全相同，内积的模平方为1，测得0的概率就是100%；如果它们完全正交，内积的模平方为0，测得0的概率就是50%。我们通过大量重复实验统计测量得到0的概率，就能反推出两个量子态的内积。

**第五步：isQ代码实现**
在代码中，由于系统禁止使用SWAP门，我们可以通过CNOT门和Toffoli门（三比特门）的组合等效实现Fredkin门（受控SWAP门）。其量子逻辑为：CNOT(b, a) -> Toffoli(c, a, b) -> CNOT(b, a)。

以下是完整的isQ代码：

import std;

qbit q[3];

procedure main() {
    // 为了演示，假设我们初始化 q[1] 为 |+> 态，q[2] 保持 |0> 态
    H(q[1]);

    // --- Swap Test 核心电路 ---
    // 第一步：对辅助比特 q[0] 施加 Hadamard 门
    H(q[0]);

    // 第二步：执行受控交换操作
    // 等效实现受控SWAP逻辑，当 q[0] 为 1 时交换 q[1] 和 q[2]
    CNOT(q[2], q[1]);
    Toffoli(q[0], q[1], q[2]);
    CNOT(q[2], q[1]);

    // 第三步：再次对辅助比特 q[0] 施加 Hadamard 门
    H(q[0]);

    // 第四步：测量辅助比特，观察其坍缩为 0 的概率
    int res = M(q[0]);
}

## isqExpand/algo/132

- task_id: `isqExpand/algo/132`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `multi_controlled_logic`
- source: `isq_expansion`
- dataset_index: `197`

### Prompt

分析以下isQ程序的测量概率分布：

```isq
import std;
qbit q[3];
procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    X(q[0]); X(q[1]);
    H(q[2]); Toffoli(q[0], q[1], q[2]); H(q[2]);
    X(q[0]); X(q[1]);
    X(q[2]);
    H(q[2]); Toffoli(q[0], q[1], q[2]); H(q[2]);
    X(q[2]);
    H(q[0]); H(q[1]); H(q[2]);
    X(q[0]); X(q[1]); X(q[2]);
    H(q[2]); Toffoli(q[0], q[1], q[2]); H(q[2]);
    X(q[0]); X(q[1]); X(q[2]);
    H(q[0]); H(q[1]); H(q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
Oracle marks |001> (idx 1) and |110> (idx 6).
CCZ implemented as H(q2)-Toffoli-H(q2).

k=2, N=8, theta = pi/6, r=1: sin(pi/2) = 1.
Expected: [0,0.5,0,0,0,0,0.5,0]

### Reference answer

{'predicted_probs': [0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0], 'explanation': 'The oracle marks |001> (X on q0,q1, CCZ, undo) and |110> (X on q2, CCZ, undo). With k=2 marked in N=8, theta = pi/6. After 1 iteration: sin(pi/2) = 1. P(|001>) = P(|110>) = 0.5, all others = 0.'}

## isqTrain/1166

- task_id: `isqTrain/1166`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2402`

### Prompt

Write an isQ program that implements a variant of the iqp_circuit pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Let me analyze this IQP (Instantaneous Quantum Polynomial) circuit variant.

The circuit uses 4 qubits (q[0], q[1], q[2], q[3]) but only actively operates on q[0], q[1], q[2]. Q[3] is never touched.

Let me trace through the circuit:

1. Initial state: |0000⟩

2. H(q[0]); H(q[1]); H(q[2]); - Hadamard on first 3 qubits
   State: |+⟩|+⟩|+⟩|0⟩ = (1/√8)(|0000⟩ + |0010⟩ + |0100⟩ + |0110⟩ + |1000⟩ + |1010⟩ + |1100⟩ + |1110⟩)

3. T(q[0]); T(q[1]); T(q[2]); - T gates on first 3 qubits
   Each |1⟩ gets phase e^(iπ/4) = (1+i)/√2
   
   For |x2x1x0⟩ component, phase is T^x0 * T^x1 * T^x2

4. CZ(q[0], q[1]); - Controlled-Z between q[0] and q[1]
   Applies -1 phase when both q[0]=1 and q[1]=1

5. CZ(q[1], q[2]); - Controlled-Z between q[1] and q[2]
   Applies -1 phase when both q[1]=1 and q[2]=1

6. H(q[0]); H(q[1]); H(q[2]); - Second Hadamard layer

7. M(q[0]); M(q[1]); M(q[2]); M(q[3]); - Measure all 4 qubits

The diagonal phase for state |x2x1x0⟩ after T and CZ gates:
- T phase: e^(iπ/4 * (x0 + x1 + x2))
- CZ(0,1) phase: (-1)^(x0*x1)
- CZ(1,2) phase: (-1)^(x1*x2)

So the phase is: e^(iπ/4 * (x0+x1+x2)) * (-1)^(x0*x1 + x1*x2)

The amplitude for measuring |y2y1y1y0⟩ is:
(1/√8) * Σ_x (-1)^(x·y) * e^(iπ/4 * (x0+x1+x2)) * (-1)^(x0*x1 + x1*x2)

where x·y = x0*y0 + x1*y1 + x2*y2

This is the Hadamard transform of the diagonal, which gives the IQP output distribution.

Q[3] stays |0⟩ throughout, so measurement always gives 0 for q[3].

Let me verify one probability. For |0000⟩:
amplitude = (1/√8) * Σ_x (-1)^0 * e^(iπ/4 * Σxi) * (-1)^(x0x1 + x1x2)
= (1/√8) * Σ_x e^(iπ/4 * (x0+x1+x2)) * (-1)^(x0x1 + x1x2)

For x=(0,0,0): phase = 1
For x=(1,0,0): phase = e^(iπ/4)
For x=(0,1,0): phase = e^(iπ/4)
For x=(1,1,0): phase = e^(iπ/2) * (-1)^1 = i * (-1) = -i
For x=(0,0,1): phase = e^(iπ/4)
For x=(1,0,1): phase = e^(iπ/2) = i
For x=(0,1,1): phase = e^(iπ/2) * (-1)^1 = -i
For x=(1,1,1): phase = e^(i3π/4) * (-1)^2 = e^(i3π/4)

Sum = 1 + 3*e^(iπ/4) - i + i - i + e^(i3π/4)
= 1 + 3*(1+i)/√2 - i + e^(i3π/4)
= 1 + 3(1+i)/√2 - i + (-1+i)/√2

Let me compute numerically:
e^(iπ/4) = (1+i)/√2 ≈ 0.7071 + 0.7071i
e^(i3π/4) = (-1+i

## isqTrain/955

- task_id: `isqTrain/955`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `hamiltonian_simulation`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5450`

### Prompt

Create an isQ quantum circuit that implements the pauli_evolution pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

1. The goal: Implement a Pauli-Z evolution pattern with explicit H-H pair to demonstrate gate cancellation awareness.

2. Qubits: 1 qubit (q[0]), which is measured.

3. State evolution:
- Initial state: |0⟩
- H(q[0]): |0⟩ → |+⟩ = (|0⟩ + |1⟩)/√2
- Rz(π/2, q[0]): This applies phase e^(-iπ/4) to |0⟩ and e^(iπ/4) to |1⟩
  State becomes: (e^(-iπ/4)|0⟩ + e^(iπ/4)|1⟩)/√2
- H(q[0]): Converts back to computational basis
  H applied to (e^(-iπ/4)|0⟩ + e^(iπ/4)|1⟩)/√2
  = (e^(-iπ/4)|+⟩ + e^(iπ/4)|-⟩)/√2
  = (e^(-iπ/4)(|0⟩+|1⟩)/√2 + e^(iπ/4)(|0⟩-|1⟩)/√2)/√2
  = ((e^(-iπ/4)+e^(iπ/4))|0⟩ + (e^(-iπ/4)-e^(iπ/4))|1⟩)/2
  
  cos(π/4)|0⟩ - i*sin(π/4)|1⟩ = (|0⟩ - i|1⟩)/√2

Wait, let me recalculate. Rz(θ) = e^(-iθ/2)|0⟩⟨0| + e^(iθ/2)|1⟩⟨1|

Rz(π/2):
- |0⟩ → e^(-iπ/4)|0⟩
- |1⟩ → e^(iπ/4)|1⟩

So after Rz(π/2) on |+⟩:
(e^(-iπ/4)|0⟩ + e^(iπ/4)|1⟩)/√2

Now H applied:
H = (|0⟩⟨0| + |0⟩⟨1| + |1⟩⟨0| - |1⟩⟨1|)/√2

H(e^(-iπ/4)|0⟩ + e^(iπ/4)|1⟩)/√2
= (e^(-iπ/4)(|0⟩+|1⟩)/√2 + e^(iπ/4)(|0⟩-|1⟩)/√2)/√2
= ((e^(-iπ/4)+e^(iπ/4))|0⟩ + (e^(-iπ/4)-e^(iπ/4))|1⟩)/2
= (2cos(π/4)|0⟩ - 2i*sin(π/4)|1⟩)/2
= (cos(π/4)|0⟩ - i*sin(π/4)|1⟩)
= (|0⟩ - i|1⟩)/√2

Hmm, that's not right. Let me redo:
cos(π/4) = 1/√2, sin(π/4) = 1/√2

So state = (|0⟩ - i|1⟩)/√2

Actually wait, H|0⟩ = |+⟩ = (|0⟩+|1⟩)/√2
H|1⟩ = |−⟩ = (|0⟩−|1⟩)/√2

So H(e^(-iπ/4)|0⟩ + e^(iπ/4)|1⟩)/√2
= e^(-iπ/4)|+⟩/√2 + e^(iπ/4)|-⟩/√2
= e^(-iπ/4)(|0⟩+|1⟩)/2 + e^(iπ/4)(|0⟩-|1⟩)/2
= [(e^(-iπ/4)+e^(iπ/4))|0⟩ + (e^(-iπ/4)-e^(iπ/4))|1⟩]/2
= [2cos(π/4)|0⟩ - 2i*sin(π/4)|1⟩]/2
= cos(π/4)|0⟩ - i*sin(π/4)|1⟩

Hmm that's normalized: cos²(π/4) + sin²(π/4) = 1/2 + 1/2 = 1. Good.

State after second H: cos(π/4)|0⟩ - i*sin(π/4)|1⟩

- H(q[0]): Apply H again

## isqExpand/algo/77

- task_id: `isqExpand/algo/77`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `vqe`, `output_prediction`, `multi_layer`, `circuit_depth`
- source: `isq_expansion`
- dataset_index: `3476`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[2];

procedure main() {
    // Layer 1
    Ry(pi/4.0, q[0]);
    Ry(pi/4.0, q[1]);
    CNOT(q[0], q[1]);
    // Layer 2
    Ry(pi/6.0, q[0]);
    Ry(pi/6.0, q[1]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
This is a 2-layer VQE ansatz. Tracking the full state vector through both layers:

Layer 1:
- Ry(pi/4) on each qubit: cos(pi/8)|0>+sin(pi/8)|1>, cos(pi/8)≈0.9239, sin(pi/8)≈0.3827
- Product state: 4 amplitudes
- CNOT(q[0],q[1]): swaps amplitudes of |10> and |11>

After Layer 1, the state is entangled with non-trivial amplitudes.

Layer 2:
- Ry(pi/6) on each qubit: cos(pi/12)≈0.9659, sin(pi/12)≈0.2588
- Each single-qubit Ry rotates amplitudes within each qubit's subspace
- Second CNOT re-entangles

Numerical result: P(00)=0.4831, P(01)=0.1981, P(10)=0.2622, P(11)=0.0566.

Key insight: the second layer's smaller rotation angles (pi/6 < pi/4) fine-tune the state rather than making dramatic changes, demonstrating how layered ansatze can incrementally shape the quantum state.

### Reference answer

{'predicted_probs': {'00': 0.4831, '01': 0.1981, '10': 0.2622, '11': 0.0566}, 'explanation': 'Layer 1 applies Ry(pi/4) on both qubits then CNOT, creating an entangled state. Layer 2 applies Ry(pi/6) on both qubits then another CNOT, further transforming the state. The 2-layer circuit explores a deeper region of Hilbert space than a single layer. The dominant state is |00> with P=0.4831, followed by |10> with P=0.2622.'}

## isqQA/quantum_algorithms/52_hardware_limitations

- task_id: `isqQA/quantum_algorithms/52_hardware_limitations`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `hardware_limitations`, `algorithm`, `相位回踢机制`
- source: `qa_pipeline`
- dataset_index: `4364`

### Prompt

相位回踢机制是许多高级量子算法（如量子相位估计QPE和HHL算法）的核心，用于将目标酉算子的特征相位提取到控制寄存器的相对相位中。然而，在当前的NISQ（含噪声中等规模量子）设备上，高保真度地实现相位回踢机制面临着巨大挑战。请详细分析在NISQ硬件上实现相位回踢时，受控酉操作的复杂度、门错误率以及量子比特退相干时间等因素是如何限制其精度的？

### Reference answer

相位回踢机制是提取本征相位的关键步骤，其核心在于利用控制寄存器对目标酉算子U执行一系列受控酉操作（如C-U, C-U^2, ..., C-U^{2^k}）。尽管在理论模型中该机制完美无缺，但在当前的NISQ（含噪声中等规模量子）设备上，其实际可行性和精度受到了硬件局限性的严重制约。具体表现在以下几个核心维度：

首先，极高的门错误率与受控操作的复杂度。相位回踢通常需要分解复杂的受控酉操作。硬件原生的受控门往往只有单比特门和简单的两比特门（如CNOT或CZ）。要将C-U^{2^k}转化为基础门序列，会生成极其庞大的量子线路。当前NISQ设备的双比特门错误率通常在10^{-3}到10^{-2}量级，远高于单比特门。由于相位回踢要求严格串联执行多次受控操作，这些门错误会发生相干或非相干的累积，直接破坏了相位的精确度，导致最终测量时无法准确提取出目标相位。

其次，退相干时间（T1和T2）的严格限制。量子比特的相干时间是有限的。在进行相位回踢时，控制比特必须与目标系统保持长时间的量子纠缠，直到所有受控酉操作完成。随着k的增加，执行C-U^{2^k}所需的时间呈指数级增长。如果线路执行的总时间接近或超过了量子比特的退相干时间，量子态的叠加性和纠缠态就会因环境耦合而坍缩或退相干，控制比特上的相对相位信息将被彻底抹除。特别是在需要大量控制比特（如标准QPE）的场景下，跨越整个系统的长程纠缠极易受到噪声干扰。

最后，有限的量子比特连通性。在许多硬件架构（如超导量子计算）中，物理比特的连接拓扑是受限的（例如方形网格或重六边形）。在执行多控制位的受控酉操作时，往往需要引入大量额外的SWAP操作来将远距离的量子比特“搬运”到相邻位置。这不仅进一步急剧增加了线路深度和双比特门数量，还引入了额外的噪声，使得高精度的相位回踢在浅层线路中几乎不可能实现。

综上所述，由于门错误率的线性累积和退相干导致的相位丢失，传统的基于大规模相位回踢的算法（如标准QPE）在NISQ设备上难以运行。这也是为什么目前学术界转而研究变分量子算法（VQE）或采用变分/迭代相位估计（IQPE）等需要更浅线路深度的方法，以在硬件噪声极限内尽可能逼近相位回踢的效果。

# ISQ training COT RAG corpus: quantum_algorithms shard 154

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1177

- task_id: `isqTrain/1177`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5202`

### Prompt

Implement a quantum circuit in isQ: implements the fourier_checking pattern using an alternative gate decomposition (S -> T T). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

The task is to explain the fourier-checking pattern (also known as the Forrelation problem) with an alternative gate decomposition where S gates are replaced by two T gates (since S = T²).

Let me trace through the circuit step by step:

1. Initial state: |00⟩

2. First H layer: H⊗H applied to |00⟩ → |++⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

3. Phase oracle f:
   - T on q[0]: applies T to first qubit
   - T on q[1], then T on q[1] again: this is T² = S on q[1]
   
   After f oracle: (|00⟩ + e^(iπ/4)|01⟩ + i|10⟩ + i·e^(iπ/4)|11⟩)/2
   
   Wait, let me be more careful. T acts on qubits independently.
   
   |++⟩ = (|0⟩ + |1⟩) ⊗ (|0⟩ + |1⟩) / 2 = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
   
   T on q[0]: |0⟩→|0⟩, |1⟩→e^(iπ/4)|1⟩
   S on q[1] (two T gates): |0⟩→|0⟩, |1⟩→i|1⟩
   
   So the state becomes: (|00⟩ + i|01⟩ + e^(iπ/4)|10⟩ + i·e^(iπ/4)|11⟩)/2

4. Middle H layer: H⊗H applied
   
   H⊗H on a general state α|00⟩ + β|01⟩ + γ|10⟩ + δ|11⟩ gives:
   ((α+β+γ+δ)|00⟩ + (α-β+γ-δ)|01⟩ + (α+β-γ-δ)|10⟩ + (α-β-γ+δ)|11⟩)/2
   
   With α=1, β=i, γ=e^(iπ/4), δ=i·e^(iπ/4):
   - Sum for |00⟩: 1 + i + e^(iπ/4) + i·e^(iπ/4)
   - Sum for |01⟩: 1 - i + e^(iπ/4) - i·e^(iπ/4)
   - Sum for |10⟩: 1 + i - e^(iπ/4) - i·e^(iπ/4)
   - Sum for |11⟩: 1 - i - e^(iπ/4) + i·e^(iπ/4)

Let me compute these numerically:
e^(iπ/4) = (1+i)/√2 ≈ 0.7071 + 0.7071i

1 + i + (0.7071+0.7071i) + i(0.7071+0.7071i)
= 1 + i + 0.7071 + 0.7071i + 0.7071i - 0.7071
= 1 + 0.7071 - 0.7071 + i(1 + 0.7071 + 0.7071)
= 1 + i(2.4142)
≈ 1 + 2.4142i

1 - i + 0.7071 + 0.7071i - 0.7071i + 0.7071
= 1 + 0.7071 + 0.7071 + i(-1 + 0.7071 - 0.7071)
= 2.4142 - i

1 + i - 0.7071 - 0.7071i - 0.7071i + 0.7071
= 1 - 0.7071 + 0.7071 + i(1 - 0.7071 - 0.7071)
= 1 - 0.4142i

1 - i - 0.7071 - 0.7071i + 0.7071i - 0.7071
= 1 - 0.7071 - 0.7071 + i(-1 - 0.7071 + 0.7071)
= -0.4142 - i

5. Phase oracle g:
   - T on q[0], T on q[0]: S on q[0

## isqTrain/3991

- task_id: `isqTrain/3991`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `4605`

### Prompt

修复以下isQ程序中的错误：

```
import std;
// 1D quantum walk: 8 positions, 3 step(s)
// q[0] = coin, q[1..3] = position register
qbit q[4];

procedure main() {
    // Start at position 0, coin in |0>
    // Walk steps
        // Step 1: coin flip
        H(q[0]);
        ctrl X(q[0], q[1]);
        ctrl X(q[0], q[2]);
        ctrl X(q[0], q[3]);
        // Step 2: coin flip
        H(q[0]);
        ctrl X(q[0], q[1]);
        ctrl X(q[0], q[2]);
        ctrl X(q[0], q[3]);
        // Step 3: coin flip
        H(q[0]);
        ctrl X(q[0], q[1]);
        ctrl X(q[0], q[2]);
        ctrl Y(q[0], q[3]);
    // Measure coin and position
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

Let me analyze this quantum walk circuit.

The bug is in Step 3, where `ctrl Y(q[0], q[3])` is used instead of `ctrl X(q[0], q[3])`.

In all three steps of the quantum walk, the conditional shift should use controlled-X (CNOT) gates on all position qubits. Steps 1 and 2 correctly use `ctrl X(q[0], q[3])`, but Step 3 uses `ctrl Y(q[0], q[3])` which is wrong.

Let me trace the corrected circuit:

Starting state: |0000⟩ (coin=|0⟩, position=|000⟩)

**Step 1:**
- H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |000⟩ = (|0000⟩+|1000⟩)/√2
- ctrl X(q[0],q[1]): (|0000⟩+|1010⟩)/√2
- ctrl X(q[0],q[2]): (|0000⟩+|1110⟩)/√2
- ctrl X(q[0],q[3]): (|0000⟩+|1111⟩)/√2

**Step 2:**
- H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |000⟩/√2 + (|0⟩-|1⟩)/√2 ⊗ |111⟩/√2
  = (|0000⟩+|1000⟩)/2 + (|0111⟩-|1111⟩)/2
  = (|0000⟩+|1000⟩+|0111⟩-|1111⟩)/2

- ctrl X(q[0],q[1]): When coin=|1⟩, flip q[1]
  |0000⟩→|0000⟩, |1000⟩→|1010⟩, |0111⟩→|0111⟩, |1111⟩→|1011⟩

Wait, let me reconsider. The position register is q[1], q[2], q[3]. The controlled operations flip each position qubit conditioned on the coin being |1⟩.

So ctrl X(q[0], q[1]) means: if q[0]=|1⟩, flip q[1].

Let me redo more carefully.

After Step 1: (|0000⟩+|1111⟩)/√2
- coin in |0⟩, position |000⟩; coin in |1⟩, position |111⟩

**Step 2:**
- H(q[0]): 
  |0⟩→(|0⟩+|1⟩)/√2, |1⟩→(|0⟩-|1⟩)/√2
  
  State: (|0⟩+|1⟩)|000⟩/2 + (|0⟩-|1⟩)|111⟩/2
  = (|0000⟩+|1000⟩+|0111⟩-|1111⟩)/2

- ctrl X(q[0],q[1]): flip q[1] when coin=|1⟩
  = (|0000⟩+|1010⟩+|0111⟩-|1011⟩)/2

- ctrl X(q[0],q[2]): flip q[2] when coin=|1⟩
  = (|0000⟩+|1110⟩+|0111⟩-|1101⟩)/2

- ctrl X(q[0],q[3]): flip q[3] when coin=|1⟩
  = (|0000⟩+|1111⟩+|0111⟩-|1100⟩)/2

**Step 3:**
- H(q[0]):
  For |0⟩coin terms: (|0⟩+|1⟩)/√2
  For |1⟩coin terms: (|0⟩-|1⟩)/√2
  
  = (|0⟩+|1⟩)|000⟩/(2√2) + (|0⟩-|1⟩)|111⟩/(2√2) + (|0⟩+|1⟩)|111⟩/(2√2) - (|0⟩-|1⟩)|100⟩/(2√2)

Wait, let me be more careful. After step 2 we have:
(|0000⟩+|1111⟩+|0111⟩-|1100⟩)/2

Let me label: coin is q[0], position is q[1]q[2]q[3].

After H(q[0]) in step 3:
|0⟩_coin → (|0⟩+|1⟩)/√2
|1⟩_coin → (|0⟩-|1⟩)/√2

So

## isqTrain/815

- task_id: `isqTrain/815`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `reversible_computing`, `superposition`
- source: `isq_train_cot`
- dataset_index: `380`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[2];

procedure main() {
    // Put input x in uniform superposition
    H(q[0]);
    // Quadratic form: f(x) = x^2 mod 2 = x for 1-bit input
    // Copy x to result qubit
    CNOT(q[0], q[1]);
    // Measure the result of the quadratic form
    M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
- Initial state of the 2-qubit system is |00>.
- Applying H(q[0]) puts the first qubit into a uniform superposition, evolving the state to (1/√2)(|00> + |10>).
- Applying CNOT(q[0], q[1]) flips the target qubit q[1] when the control qubit q[0] is |1>, creating the maximally entangled Bell state: (1/√2)(|00> + |11>).
- Measuring only q[1] projects it onto the computational basis, yielding |0> or |1> with equal probability.
Predicted probability distribution: {|0>: 0.5, |1>: 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'Parametric variant of isqEval/288. Dimension: predict probabilities for reference circuit.'}

## isqExpand/algo/38

- task_id: `isqExpand/algo/38`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `period_finding`, `qpe`, `shor`, `continued_fractions`, `modular_exponentiation`
- source: `qa_pipeline`
- dataset_index: `1421`

### Prompt

在Shor算法中，周期查找（period finding）是核心量子子程序。请解释周期查找如何利用量子相位估计（QPE），以及测量结果如何通过连分数展开恢复周期。以 N=15, a=7 为例进行说明。

### Chain-of-thought reasoning

## 推理
目标：详细解释周期查找子程序和连分数恢复。

关键概念：
1. 模幂函数 f(x)=a^x mod N 的周期性
2. 酉算子 U|y>=|ay mod N> 的本征态和本征值
3. QPE估计相位 s/r
4. 连分数展开从 m/2^n 恢复有理数 s/r
5. N=15, a=7 的具体数值演示

这是Shor算法最核心的量子部分，连接了数论和量子信息。

### Reference answer

## 周期查找与QPE

### 问题定义
给定 f(x) = a^x mod N，求最小正整数 r 使得 f(x+r) = f(x)（即 a^r ≡ 1 mod N）。

### QPE在周期查找中的角色

定义酉算子 U|y> = |ay mod N>。则 U 的本征态为：
|u_s> = (1/√r) Σ_{k=0}^{r-1} e^{-2πisk/r} |a^k mod N>

对应本征值 e^{2πis/r}（s = 0, 1, ..., r-1）。

QPE 可以估计这个相位 s/r，从而提取周期 r 的信息。

### 具体步骤

1. **准备**：计数寄存器 |0>^n，工作寄存器 |1>
2. **Hadamard**：H^n|0> = 均匀叠加
3. **受控模幂**：Σ_x |x>|a^x mod N>
4. **逆QFT**：提取相位 s/r 的 n 位近似
5. **测量**：得到整数 m，满足 m/2^n ≈ s/r

### 连分数展开恢复 r

测量值 m/2^n 是 s/r 的有理近似。通过连分数展开算法：
m/2^n = [a_0; a_1, a_2, ...]

取收敛子中分母 ≤ N 的最佳近似，其分母就是 r（或 r 的因子）。

### 示例：N=15, a=7

7^1 mod 15 = 7
7^2 mod 15 = 4
7^3 mod 15 = 13
7^4 mod 15 = 1

所以 **r = 4**。

验证分解：
- 7^{r/2} = 7^2 = 49
- gcd(49+1, 15) = gcd(50, 15) = 5
- gcd(49-1, 15) = gcd(48, 15) = 3
- 15 = 3 × 5 ✓

用 n=4 个相位比特时，QPE 可能测量到 m ∈ {0, 4, 8, 12}，分别对应 s/r = 0/4, 1/4, 2/4, 3/4。通过连分数展开任一非零值都可恢复 r=4。

## isqTrain/941

- task_id: `isqTrain/941`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `990`

### Prompt

实现以下量子计算任务（使用isQ）：implements the reversible_logic pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a reversible controlled-swap (three-CNOT decomposition) (controlled-swap (three-CNOT decomposition)) circuit with explicit H-H identity operations demonstrating gate cancellation.
2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.
3. **State evolution**:
   - |000⟩ → X(q[0]), X(q[1]) → |110⟩
   - ctrl swap_gate(q[0], q[1], q[2]) → controlled-swap (three-CNOT decomposition) swaps q[1],q[2] when q[0]=|1⟩ → |101⟩
   - H(q[0]) → (1/√2)(|001⟩ + |101⟩)
   - H(q[0]) → |101⟩ (H² = I, gate cancellation)
4. **Measurement**: Final state |101⟩ yields {|101⟩: 1.0} — the H-H pair cancels, returning the control to definite |1⟩.

## isqTrain/1284

- task_id: `isqTrain/1284`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2231`

### Prompt

Code this in isQ: implements a variant of the iqp_circuit pattern using q[2] -> q[3]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The user wants me to write a reasoning section for an iqp_circuit variant that uses q[2] -> q[3] with an expanded qubit register.

Let me analyze The implementation:
- It uses 3 qubits (q[0], q[1], q[2])
- The IQP circuit acts on q[0] and q[1]
- H gates are applied to q[0] and q[1]
- S gates are applied to q[0] and q[1]
- CZ is applied between q[0] and q[1]
- H gates are applied again to q[0] and q[1]
- All 3 qubits are measured

The predicted output {|000>: 0.5, |110>: 0.5}

Now, the task asks for a "variant" that uses q[2] -> q[3], meaning it should use q[2] and q[3] for the IQP circuit instead of q[0] and q[1], and should use an expanded qubit register (so more qubits than 3, maybe 4 or 5).

Let me trace through the state evolution for The implementation first:
1. Initial state: |000>
2. H(q[0]), H(q[1]): 1/2(|00> + |01> + |10> + |11>) ⊗ |0> = 1/2(|000> + |010> + |100> + |110>)
3. S(q[0]): S|0> = |0>, S|1> = i|1>, so: 1/2(|000> + |010> + i|100> + i|110>)
4. S(q[1]): S|0> = |0>, S|1> = i|1>, so: 1/2(|000> + i|010> + i|100> + i*i|110>) = 1/2(|000> + i|010> + i|100> - |110>)
5. CZ(q[0], q[1]): applies Z to q[1] when q[0] is |1>, so:
   - |000> stays |000>
   - |010> stays |010>
   - |100> becomes -|100>
   - |110> becomes -|110>
   Result: 1/2(|000> + i|010> - i|100> + |110>)
6. H(q[0]), H(q[1]): Let me compute this carefully

H on q[0] and q[1]:
- |000> -> 1/2(|00> + |01> + |10> + |11>) ⊗ |0> = 1/2(|000> + |010> + |100> + |110>)
- |010> -> 1/2(|00> - |01> + |10> - |11>) ⊗ |0> = 1/2(|000> - |010> + |100> - |110>)
- |100> -> 1/2(|00> + |01> - |10> - |11>) ⊗ |0> = 1/2(|000> + |010> - |100> - |110>)
- |110> -> 1/2(|00> - |01> - |10> + |11>) ⊗ |0> = 1/2(|000> - |010> - |100> + |110>)

So the final state is:
1/2 * [1/2(|000> + |010> + |100> + |110>) + i/2(|000> - |010> + |100> - |110>) - i/2(|000> + |010> - |100> - |110>) + 1/2(|000> - |010> - |100> + |110>)]

Let me collect terms:
|000>: 1/4 + i/4 - i/4 + 1/4 = 1/2
|010>: 1/4 - i/4 - i/4 - 1/4 = -i/2
|100>: 1/4 + i/4 + i/4 - 1/4 = i/2
|110>: 1/4 - i/4 + i/4 + 1/4 = 1/2

So the state is 1/2|000> - i/2|010> + i/2|100> + 1/2|110>

Wait, this doesn't match the predicted output {|000>: 0.5, |110>: 0.5}. Let me recalculate.

Hmm, the measurement is on all 3 qubits, including

## isqTrain/1236

- task_id: `isqTrain/1236`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `basis_change`, `entanglement`, `mid_circuit_measurement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2470`

### Prompt

帮我写一个isQ程序：implements the teleportation_protocol pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

Let me analyze this quantum teleportation protocol with reversed measurement ordering.

1. The goal: Implement quantum teleportation of a |+> state from q[0] to q[2], with reversed measurement order.

2. Qubits needed: 3 qubits (q[0], q[1], q[2])
   - q[0]: message qubit (starts in |+> after H)
   - q[1]: Alice's half of Bell pair
   - q[2]: Bob's half of Bell pair (receives teleported state)
   
   All 3 qubits are measured: M(q[2]), M(q[1]), M(q[0])

3. Let me trace through the state evolution:

Initial state: |000⟩

After H(q[0]): |+⟩|00⟩ = (|0⟩ + |1⟩)/√2 ⊗ |00⟩

After H(q[1]): (|0⟩ + |1⟩)/√2 ⊗ (|0⟩ + |1⟩)/√2 ⊗ |0⟩
= (|000⟩ + |010⟩ + |100⟩ + |110⟩)/2

After CNOT(q[1], q[2]):
(|000⟩ + |011⟩ + |100⟩ + |111⟩)/2
= (|0⟩ + |1⟩)/√2 ⊗ (|00⟩ + |11⟩)/√2

After CNOT(q[0], q[1]):
Let me expand and apply:
(|000⟩ + |011⟩ + |101⟩ + |110⟩)/2

After H(q[0]):
(|000⟩ + |011⟩ + |001⟩ - |010⟩ + |100⟩ + |111⟩ - |101⟩ + |110⟩)/2√2
Wait, let me be more careful.

The state after CNOT(q[0], q[1]) is:
(|000⟩ + |011⟩ + |101⟩ + |110⟩)/2

Applying H on q[0]:
H|0⟩ = (|0⟩ + |1⟩)/√2
H|1⟩ = (|0⟩ - |1⟩)/√2

So:
= (1/2)[(|0⟩ + |1⟩)/√2 ⊗ |00⟩ + (|0⟩ + |1⟩)/√2 ⊗ |11⟩ + (|0⟩ - |1⟩)/√2 ⊗ |01⟩ + (|0⟩ - |1⟩)/√2 ⊗ |10⟩]

= (1/2√2)[|000⟩ + |100⟩ + |011⟩ + |111⟩ + |001⟩ - |101⟩ + |010⟩ - |110⟩]

Now we measure q[2] first, then q[1], then q[0].

Actually wait, let me look at the reference code more carefully:

This measures q[2] first, then q[1]. Then later `M(q[0])`.

But the corrections are:

Hmm, but these are applied AFTER measurement, and the measurement results would collapse the state. In isQ, M(q) returns a classical value, and the qubit is still available for classical control.

Wait, looking at this more carefully - in the reference code, q[2] is measured BEFORE q[1]. This is the "reversed measurement order" compared to standard teleportation where we'd measure q[0] and q[1] first.

But the corrections CNOT(q[1], q[2]) and CZ(q[0], q[2]) suggest that q[1] and q[0] should have measurement results that control operations on q[2].

Let me re-examine the code:
1. M(q[2]) - measures Bob's qubit first (unusual!)
2. M(q[1]) - measures Alice's half of Bell pair
3. CNOT(q[1], q[2]) - but q[2] was already measured!
4. CZ(q[0], q[2])
5. H(q[2])
6. M(q[0])

This is confusing. If q[2] is measured first, then the corrections don't make sense in the standard teleportation sense.

Actually, looking at the predicted output: {|000>: 0.25, |001>: 0.25, |010>: 0.25, |011>: 0.25}

This means only the first 4 basis states have equal probability, and states |100>, |101>, |110>, |111> have 0 probability. This means q[0] (the highest bit in measurement ordering) is always 0 after

## isqTrain/3462

- task_id: `isqTrain/3462`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `phase_manipulation`, `ancilla_usage`
- source: `isq_train_cot`
- dataset_index: `1831`

### Prompt

Write isQ code for the following quantum task: Deutsch-Jozsa for 3 qubits with balanced function f(x)=x[0] in isQ.

Oracle: CNOT(q[0], anc). Output depends only on first bit.
This is balanced: f returns 0 for half the inputs (x0=0) and 1 for the other half (x0=1).

Declare 3 input qubits and 1 ancilla. Measure input only.
Expected: non-zero output (|100>).

### Chain-of-thought reasoning

Let me trace through the Deutsch-Jozsa circuit for 3 qubits with balanced function f(x) = x[0].

1. Goal: Determine if f(x) = x[0] is constant or balanced using Deutsch-Jozsa algorithm.

2. Qubits: 3 input qubits q[0], q[1], q[2] and 1 ancilla anc[0]. Only input qubits are measured.

3. State evolution:
   - Initial: |000>|1> (after X on ancilla)
   - After H on ancilla: |000>|-> = |000>(|0>-|1>)/√2
   - After H on all inputs: (1/√8)(|000>+|001>+|010>+|011>+|100>+|101>+|110>+|111>)|-> = (1/√8)Σ|x>|-> where |x> are all 3-bit states
   
   The ancilla in |-> means that when we apply the oracle, it introduces a phase (-1)^f(x) on each |x>:
   - Oracle CNOT(q[0], anc[0]): f(x) = x[0], so states with x[0]=1 get phase -1
   
   After oracle: (1/√8)(|000>+|001>+|010>+|011>-|100>-|101>-|110>-|111>)|-> = (1/√8)(|0xx> - |1xx>)|-> 
   
   More precisely: (1/√8)(Σ x[0]=0 |x> - Σ x[0]=1 |x>)|-> = (1/√8)(|0**> - |1**>)|-> where ** are all combinations of q[1], q[2]
   
   After H on all inputs:
   - H⊗3 on (|0**> - |1**>)/√8
   
   Let me think more carefully. The state after oracle is:
   (1/√8)(|000>+|001>+|010>+|011>-|100>-|101>-|110>-|111>)
   
   This is (1/√8)((|0>-|1>)⊗(|0>+|1>)⊗(|0>+|1>)) when read as q[0]⊗q[1]⊗q[2]
   
   Wait, let me verify: 
   |0>-|1> gives coefficients for q[0]: [1,-1]
   |0>+|1> gives coefficients for q[1]: [1,1]
   |0>+|1> gives coefficients for q[2]: [1,1]
   
   Tensor product gives: [1,-1]⊗[1,1]⊗[1,1] = [1,1,-1,-1]⊗[1,1] = [1,1,1,1,-1,-1,-1,-1]
   
   So state is (1/√8)(|000>+|001>+|010>+|011>-|100>-|101>-|110>-|111>) ✓
   
   Applying H⊗3:
   H|0> = |+>, H|1> = |->
   
   H⊗3 applied to (|0>-|1>)⊗(|0>+|1>)⊗(|0>+|1>) / √8
   
   = (√2|->)⊗(√2|+>)⊗(√2|+>) / √8
   Wait, let me recalculate. 
   
   H(|0>-|1>)/√2 = (|+>-|->)/√2 · √2 = ... Let me be more careful.
   
   H|0> = (|0>+|1>)/√2
   H|1> = (|0>-|1>)/√2
   
   H(|0>-|1>)/√2 = (|0>+|1>-|0>+|1>) / 2 = |1> · √2/√2 = ... 
   
   Actually: H(|0>-|1>)/√2 = (1/√2)(H|0>-H|1>) = (1/√2)((|0>+|1>)/√2 - (|0>-|1>)/√2) = (1/√2)(2|1>/√2) = |1>
   
   Hmm, that's not right either. Let me just compute directly.
   
   H(|0>-|1>)/√2 = ?
   
   H = (1/√2)[[1,1],[1,-1]]
   
   Applied to (1/√2)[1,-1]^T = (1/2)[1-1, 1+1]^T

## isqTrain/3607

- task_id: `isqTrain/3607`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`
- source: `isq_train_cot`
- dataset_index: `2152`

### Prompt

Implement a quantum circuit in isQ: a 3-qubit Grover search algorithm that finds the target state |010> using 1 Grover iteration. The circuit should:
1. Initialize 3 qubits in uniform superposition with Hadamard gates
2. Apply an oracle that marks state |010> with a phase flip
3. Apply the Grover diffusion operator
4. Measure all 3 qubits
Use `deriving gate` for oracle and diffusion procedures.

### Chain-of-thought reasoning

Let me analyze this Grover search algorithm step by step.

1. Goal: Implement 3-qubit Grover search to find target state |010> using 1 iteration.

2. Qubits: 3 qubits (q[0], q[1], q[2]), all measured.

3. State evolution:

Initial state: |000>

After H on all 3 qubits:
|ψ⟩ = (1/√8)(|000⟩ + |001⟩ + |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩)

This is a uniform superposition over all 8 basis states.

Oracle for |010⟩:
- X on q[0] and q[2] transforms |010⟩ → |111⟩
- ctrl CZ(q[0], q[1], q[2]) applies phase flip to |111⟩ (Z on q[2] when q[0] and q[1] are |1⟩)
- X on q[0] and q[2] transforms back

So the oracle marks |010⟩ with a -1 phase:
|ψ⟩ = (1/√8)(|000⟩ + |001⟩ - |010⟩ + |011⟩ + |100⟩ + |101⟩ + |110⟩ + |111⟩)

Diffusion operator:
The diffusion operator reflects about the mean. It can be written as:
D = 2|s⟩⟨s| - I
where |s⟩ is the uniform superposition state.

For 3 qubits, the mean amplitude after the oracle is:
mean = (1/√8)(7 - 1) / 8 = (6/√8) / 8 = 6/(8√8) = 6/√512 = 6/(16√2) = 3/(8√2)

Wait, let me recalculate. The amplitudes after oracle are:
- All states except |010⟩: amplitude = 1/√8
- |010⟩: amplitude = -1/√8

Mean amplitude = (7 × 1/√8 + 1 × (-1/√8)) / 8 = 6/(8√8) = 6/(8×2√2) = 6/(16√2) = 3/(8√2)

After diffusion (2|s⟩⟨s| - I):
New amplitude = 2 × mean - old amplitude

For |010⟩: 2 × 3/(8√2) - (-1/(2√2)) = 6/(8√2) + 1/(2√2) = 6/(8√2) + 4/(8√2) = 10/(8√2) = 5/(4√2)

For other states: 2 × 3/(8√2) - 1/(2√2) = 6/(8√2) - 4/(8√2) = 2/(8√2) = 1/(4√2)

Let me verify: 1/(2√2) = 1/√8 = 2/(2√2) = 2/(2√2) = 4/(4√2)

Actually let me redo this more carefully.

Initial amplitudes after H on all: each state has amplitude 1/√8 = 1/(2√2)

After oracle marking |010⟩:
- |010⟩: -1/(2√2)
- All others: 1/(2√2)

Mean = [(7)(1/(2√2)) + (1)(-1/(2√2))] / 8 = [6/(2√2)] / 8 = 6/(16√2) = 3/(8√2)

After diffusion (amplitude reflection about mean):
- For |010⟩: 2(3/(8√2)) - (-1/(2√2)) = 6/(8√2) + 4/(8√2) = 10/(8√2) = 5/(4√2)
- For others: 2(3/(8√2)) - 1/(2√2) = 6/(8√2) - 4/(8√2) = 2/(8√2) = 1/(4√2)

Probabilities:
- |010⟩: |5/(4√2)|² = 25/32 = 0.78125
- Others: |1/(4√2)|² = 1/32 = 0.03125

This matches the predicted output!

4. Why expected probabilities follow:
- The probability of measuring |010⟩ is |5/(4√2)|² = 25/32 ≈ 0.78125
- The probability of measuring any other state is

## isqTrain/4072

- task_id: `isqTrain/4072`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `4400`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```
import std;
// QAOA MaxCut p=1 on 3-node path graph
// gamma=0.500, beta=1.000
qbit q[3];

procedure main() {
    // Initial superposition
    H(q[0]); H(q[1]); H(q[2]);
    // Cost unitary U_C(gamma)
    // Edge (0,1): exp(-i*gamma*Z_i*Z_j)
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.500, q[1]);
    // BUG: missing gate here
    // Edge (1,2): exp(-i*gamma*Z_i*Z_j)
    CNOT(q[1], q[2]);
    Rz(2.0 * 0.500, q[2]);
    CNOT(q[1], q[2]);
    // Mixer unitary U_M(beta)
    Rx(2.0 * 1.000, q[0]);
    Rx(2.0 * 1.000, q[1]);
    Rx(2.0 * 1.000, q[2]);
    // Measure
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis

**1. Bug identification:** In the cost unitary for edge (0,1), the second `CNOT(q[0], q[1])` is missing. The ZZ-interaction `exp(-iγZ₀Z₁)` is implemented via the CNOT–Rz–CNOT sandwich: `CNOT(q[0],q[1])`, `Rz(2γ,q[1])`, `CNOT(q[0],q[1])`. The code has only the first CNOT and the Rz, leaving the circuit in a corrupted entangled state before the next edge unitary begins.

**2. Fix:** Insert `CNOT(q[0], q[1]);` immediately after `Rz(2.0 * 0.500, q[1]);` to complete the edge-(0,1) ZZ-phase gate.

**3. State evolution (corrected):**
- After `H⊗3`: `|+⟩|+⟩|+⟩`, equal superposition over all 8 basis states.
- Edge (0,1) unitary: `CNOT₀₁ · Rz(1.0, q[1]) · CNOT₀₁` applies `exp(-iγZ₀Z₁)`, accumulating phase `e^{-i·0.5}` on `|1⟩|1⟩` and `e^{+i·0.5}` on `|0⟩|0⟩` in the (0,1) subspace.
- Edge (1,2) unitary: `CNOT₁₂ · Rz(1.0, q[2]) · CNOT₁₂` applies `exp(-iγZ₁Z₂)` analogously.
- Mixer: `Rx(2.0)` rotates each qubit by π around the X-axis, remixing toward cut-favoring states.
- Measurement yields cut states `|010⟩` and `|101⟩` with highest probability (~0.321), confirming correct QAOA behavior.

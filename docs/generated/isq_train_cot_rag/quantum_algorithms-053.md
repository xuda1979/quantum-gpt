# ISQ training COT RAG corpus: quantum_algorithms shard 53

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqExpand/algo/97

- task_id: `isqExpand/algo/97`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `phase_manipulation`, `basis_change`
- source: `isq_expansion`
- dataset_index: `4807`

### Prompt

请用isQ语言编写一个量子电路：implementing the Bernstein-Vazirani algorithm to find the hidden string s=10 (2 bits). Use q[0],q[1] as input qubits and q[2] as the ancilla. The oracle implements f(x) = s*x mod 2 = x0 (only the most significant bit). Measure only q[0] and q[1].

### Chain-of-thought reasoning

## Reasoning
Goal: BV for s=10. s[0]=1, s[1]=0.

f(x0,x1) = x0*1 + x1*0 mod 2 = x0.
Oracle: CNOT(q[0], q[2]) only.

1. X(q[2]): ancilla -> |1>
2. H on all 3: q[0],q[1] -> |+,+>, q[2] -> |->
3. Oracle CNOT(q[0],q[2]): phase kickback (-1)^{x0}
4. H on q[0],q[1]: maps to |s> = |10>

|10> = index 2. Expected: [0,0,1,0]

## isqTrain/2990

- task_id: `isqTrain/2990`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `entanglement`, `isq_syntax_multi_register`, `measurement_order`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3831`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```isq
import std;
qbit q[2];
// SWAP gate test with input |01>
procedure main() {
    // X(q[1]); // BUG: missing initialization
    CNOT(q[0], q[1]);
    CNOT(q[1], q[0]);
    CNOT(q[0], q[1]);
    M(q[0]);
    M(q[1]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **Bug**: `X(q[1])` is commented out on line 6, so q[1] remains |0⟩ instead of being flipped to |1⟩. The intended input is |01⟩, but without the X gate, the circuit runs on |00⟩.
2. **Fix**: Uncomment `X(q[1])` to prepare q[1] in |1⟩, giving the correct initial state |01⟩ for the swap (three-CNOT decomposition) test.
3. **State evolution (corrected)**: |00⟩ →X(q₁)→ |01⟩ →CNOT(q₀,q₁)→ |01⟩ →CNOT(q₁,q₀)→ |11⟩ →CNOT(q₀,q₁)→ |10⟩. The swap (three-CNOT decomposition) correctly maps |01⟩ to |10⟩, confirming measurement probabilities {|10⟩: 1.0}.

## isqTrain/3067

- task_id: `isqTrain/3067`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_multi_register`, `measurement_order`
- source: `isq_train_cot`
- dataset_index: `919`

### Prompt

这个isQ程序有问题，请找出错误并给出正确代码：

```isq
import std;
qbit q[4];
// Initialize to |0001>
procedure main() {
    // X(q[3]); // BUG: missing initialization
    M(q[0]);
    M(q[1]);
    M(q[2]);
    M(q[3]);
}

```

### Chain-of-thought reasoning

## Bug Analysis
1. **The bug:** The initialization gate `X(q[3])` is commented out. All qubits remain in their initial ground state, resulting in the system state `|0000>` instead of the required `|0001>`.
2. **The fix:** Uncomment the `X(q[3])` line to properly apply the Pauli-X (NOT) gate to the fourth qubit.
3. **State evolution:**
   - Initial state: `|0000>`
   - Apply `X(q[3])`: Flips the target qubit from `|0>` to `|1>`, changing the overall state to `|0001>`.
   - Measurement: Measures the state `|0001>` with a probability of 1.0, correctly matching the predicted output.

## isqTrain/1176

- task_id: `isqTrain/1176`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2290`

### Prompt

Write isQ code for the following quantum task: implements a variant of the fourier_checking pattern using q[2] -> q[4]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Goal: Generate reasoning for a specific isQ quantum program.
    *   Circuit: Fourier checking (Forrelation) variant using a 4-qubit register `q[4]`, with operations on `q[0]` and `q[1]`, leaving `q[2]` and `q[3]` in `|0>` state.
    *   Structure: H-layer -> f-oracle -> H-layer -> g-oracle -> H-layer -> Measurement.
    *   Oracles:
        *   f-oracle: T on `q[0]`, S on `q[1]`
        *   g-oracle: S on `q[0]`, T on `q[1]`
    *   Expected probabilities: {|0000>: ~0.7286, |0100>: 0.125, |1000>: 0.125, |1100>: ~0.0214}.
    *   Constraint: Concise, 3-15 lines. Start with `## Reasoning`. Use Dirac notation. NO CODE.

2.  **Trace the State Evolution:**
    *   Initial state: `|0000>`
    *   After first H layer on `q[0], q[1]`: `|++00>` = `(1/2)(|00> + |01> + |10> + |11>)_01 ⊗ |00>_23`
    *   After f-oracle (T on 0, S on 1):
        *   T adds $\pi/4$ to `|1>` of q0. S adds $\pi/2$ to `|1>` of q1.
        *   State: `(1/2)(|00> + e^{i\pi/2}|01> + e^{i\pi/4}|10> + e^{i3\pi/4}|11>)_01 ⊗ |00>_23`
    *   After second H layer on `q[0], q[1]`:
        *   This maps the state to a superposition where amplitudes are DFT of the oracle phases.
    *   After g-oracle (S on 0, T on 1):
        *   S adds $\pi/2$ to `|1>` of q0. T adds $\pi/4$ to `|1>` of q1.
    *   After final H layer:
        *   This transforms back to the computational basis.
        *   The amplitude of `|00>` is the forrelation between f and g.
        *   Let's compute roughly:
            *   H layer -> Oracle f -> H -> Oracle g -> H
            *   This measures the inner product / correlation.
            *   The probabilities are exactly given in the prompt: ~0.7286 for `|0000>`, ~0.125 for `|0100>` and `|1000>`, ~0.0214 for `|1100>`.
            *   The qubits `q[2]` and `q[3]` are completely untouched, remaining in `|00>`, explaining the `00` suffix in all probability keys.

3.  **Drafting the Reasoning:**
    *   *Goal:* Implement a Forrelation (H-f-H-g-H) circuit on a 4-qubit register where only qubits 0 and 1 are operated on, leaving 2 and 3 in the ground state.
    *   *Qubits:* 4 qubits, all 4 measured (though 2 and 3 remain `|0>`).
    *   *Evolution:*
        *   Start: `|0000>`.
        *   H on 0,1: `|++00>`.
        *   f-oracle (T on 0, S on 1): Phase shifts `|+>` states.
        *   H on 0,1: Converts phase differences into amplitude shifts.
        *   g-oracle (S on 0, T on 1): Applies complementary phase shifts.
        *   H on 0,1: Final Hadamards measure the correlation (Forrelation) between f and g oracles, resulting in a skewed distribution favoring `|00>`.
        *   Q[2,3] are never acted upon, remaining as `|00>`.
    *   *Probabilities:* The final Hadamard yields a highly biased distribution on qubits 0 and 1 towards `|00>` (probability ~0.7286), while qubits 2 and 3 deterministically measure as `|0>`, giving the observed `{...00}` suffixes.

4.  **Refining and Formatting:**
    *   Ensure strict adherence to rules (no code block, specific

## isqTrain/951

- task_id: `isqTrain/951`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `hamiltonian_simulation`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1656`

### Prompt

用isQ实现implements the pauli_evolution pattern with modified rotation parameters (num_pi2_to_pi3). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

## Reasoning

**Goal**: Implement Pauli-Z evolution with modified rotation angle π/3 (instead of standard π/4), converting phase information to measurable amplitude differences.

**Qubits**: 1 qubit (q[0]), which is measured.

**State evolution**:
1. |0⟩ → H → |+⟩ = (|0⟩ + |1⟩)/√2
2. |+⟩ → Rz(π/3) → (e^{-iπ/6}|0⟩ + e^{iπ/6}|1⟩)/√2
3. Phase state → H → cos(π/6)|0⟩ - i·sin(π/6)|1⟩ = (√3/2)|0⟩ - (i/2)|1⟩

**Expected probabilities**: P(|0⟩) = cos²(π/6) = 3/4 = 0.75, P(|1⟩) = sin²(π/6) = 1/4 = 0.25. The H-Rz-H sequence converts the Rz phase rotation into an amplitude rotation equivalent to Ry(π/3), yielding the 3:1 ratio between |0⟩ and |1⟩ outcomes.

## isqTrain/2482

- task_id: `isqTrain/2482`
- task_type: `code_equivalence`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `global_phase`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2459`

### Prompt

Do these two isQ programs produce the same measurement results?

Program A:
```isq
import std;
qbit q[1];

procedure main() {
    // Alice prepares state (bit=1, basis=X)
    X(q[0]);
    H(q[0]);
    
    // Bob measures in X basis
    H(q[0]);
    M(q[0]);
}

```

Program B:
```isq
import std;
qbit q[1];

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    // Alice prepares state (bit=1, basis=X)
    X(q[0]);
    H(q[0]);
    
    // Bob measures in X basis
    H(q[0]);
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Equivalence Analysis
1. **Program A**: Applies X, H, and H gates to q[0], transforming the state |0> -> |1> -> |-> -> |1>, before measuring.
2. **Program B**: Applies GPhase(0.0), followed by the exact same sequence of gates (X, H, H) and measurement as Program A.
3. **Key Difference**: Program B introduces a `GPhase(0.0)` instruction, which applies a global phase factor of $e^{i \cdot 0} = 1$.
4. **Measurement Probabilities**: Global phases do not affect measurement probabilities. A phase of 0 is strictly trivial, leaving the quantum state entirely unchanged. Both programs measure the |1> state with 100% probability.
5. **Verdict**: Equivalent: True

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqQA/quantum_algorithms/101_principle_advantage

- task_id: `isqQA/quantum_algorithms/101_principle_advantage`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `principle_advantage`, `algorithm`, `Grover搜索的最优性证明`
- source: `qa_pipeline`
- dataset_index: `1994`

### Prompt

Grover搜索算法在无结构数据库搜索问题上提供了相对于经典算法的二次加速。请深入阐述其宏观原理与量子加速的物理来源，并从量子查询复杂度下界的角度，解释为什么Grover算法的O(√N)时间复杂度在理论上已经被证明是严格最优的？最后，请使用isQ语言编写一个标准两量子比特Grover搜索算法的代码示例。

### Reference answer

<思考>
数学推导与下界证明分析：
要证明Grover算法的最优性，我们需要使用量子查询复杂度中的“多项式方法”。假设我们有一个量子黑盒Oracle，输入为x。经过t次Oracle查询后，量子算法在测量时输出1的概率可以表示为关于输入x的一个实系数多项式P(x)，且该多项式的次数最多为2t。
在搜索问题中，我们要求：
1. 当输入中没有目标项（即无解）时，算法输出1的概率不超过1/3，即P(0) ≤ 1/3。
2. 当输入中存在唯一目标项时，算法输出1的概率至少为2/3，即P(1) ≥ 2/3。
根据代数基本定理和逼近论的性质，要构造一个能够在0处小于1/3，在N个可能为1的位置处大于2/3的对称多项式，其次数d必须满足d ≥ Ω(√N)。因为t ≥ d/2，所以查询次数t也必须至少为Ω(√N)。这从根本上证明了没有任何量子算法能在少于O(√N)的查询内解决无结构搜索问题。

isQ代码推导：
针对2个量子比特（N=4），搜索空间包含|00⟩, |01⟩, |10⟩, |11⟩。假设我们要搜索的目标态是|11⟩。
1. 初始化：对两个量子比特应用Hadamard门，得到均匀叠加态。
2. Oracle：标记目标态。对于|11⟩，可以使用控制相位门CZ来实现，当且仅当状态为|11⟩时相位翻转。
3. 扩散算子：执行 H -> X -> CZ -> X -> H 操作，实现关于均值的反转。
由于N=4，最优迭代次数为 π/4 * √(N) ≈ 1次。
</思考>

Grover搜索算法是量子计算中最经典的算法之一，它主要解决的是无结构数据库的搜索问题。

**宏观原理与时间复杂度对比**
在经典计算中，如果在一个完全没有内部结构的数据库中寻找一个特定的目标项，最坏情况下必须遍历所有的N个项目，因此时间复杂度为O(N)。而Grover算法利用了量子叠加和量子干涉的特性，能够在O(√N)的时间复杂度下完成同样的搜索任务。虽然它没有像Shor算法那样实现指数级加速，但二次加速在实际大规模数据处理中依然具有极大的优势，例如在密码学中对DES或AES密钥的穷举攻击，可以将时间从2^56降低到2^28。

**量子加速的物理来源**
Grover算法的加速本质上来源于希尔伯特空间中的“幅度放大”。算法首先通过Hadamard门将系统初始化为所有可能状态的均匀叠加态。然后算法反复执行两个操作：
1. Oracle操作：识别目标态，并通过相位反转将目标态的概率幅从正变负。
2. 扩散操作：关于平均值进行反转。
这相当于一个状态向量在二维平面内朝向目标态的旋转。每次迭代都能使目标态的概率幅度增加约2/√N。这种巧妙的量子干涉使得非目标态的幅度相互抵消，目标态的幅度不断增强，从而只需约(π/4)√N次迭代就能使目标态的概率接近1。

**最优性证明原理**
Grover算法的O(√N)不仅是目前最好的结果，而且在理论上被证明是绝对最优的。证明这一点的常用方法是“多项式方法”。在量子查询模型中，经过t次查询的量子算法，其测量得到特定结果的概率可以被证明是关于输入变量的一个次数至多为2t的多项式。对于无结构搜索问题，我们需要一个多项式，它能在所有非目标输入下取值很低（小于1/3），而在目标输入下取值很高（大于2/3）。通过逼近论可以严格证明，任何满足这种近似条件的多项式，其次数d必然满足d = Ω(√N)。由于查询次数t ≥ d/2，这意味着没有任何量子算法可以用少于Ω(√N)次Oracle查询来解决此问题。因此，Grover算法达到了理论下界，是最优的。

**isQ代码实现**
下面是使用isQ语言实现的2量子比特Grover搜索算法代码，目标态设定为|11⟩：

import std;
qbit q[2];

procedure main() {
    // 1. 初始化：生成均匀叠加态
    H(q[0]);
    H(q[1]);

    // 2. Grover迭代（由于N=4，最优迭代次数为1次）
    // Oracle: 标记目标态 |11⟩
    CZ(q[0], q[1]);

    // 扩散算子
    H(q[0]);
    H(q[1]);
    X(q[0]);
    X(q[1]);
    CZ(q[0], q[1]);
    X(q[0]);
    X(q[1]);
    H(q[0]);
    H(q[1]);

    // 3. 测量
    M(q[0]);
    M(q[1]);
}

## isqTrain/4109

- task_id: `isqTrain/4109`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `662`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[4];

procedure main() {
    X(q[1]);
    X(q[2]);
    X(q[3]);

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

## Circuit Analysis

1. **Initialization**: Start with |0000⟩. X gates on q[1], q[2], q[3] yield |0111⟩ (= |7⟩ in computational basis).

2. **QFT structure**: The circuit applies the standard 4-qubit QFT via nested Hadamards and controlled-Rz rotations with angles π/2, π/4, π/8, etc. (The `ctrl Rz(2π/2^k, control, target)` pattern implements the standard QFT phase rotations.)

3. **Bit-reversal correction**: The CNOT triplets `CNOT(a,b); CNOT(b,a); CNOT(a,b)` implement swap (three-CNOT decomposition) gates. `swap (three-CNOT decomposition)(q[0],q[3])` and `swap (three-CNOT decomposition)(q[1],q[2])` reverse the bit order, completing the QFT.

4. **QFT on |7⟩**: For 4 qubits (N=16), QFT|k⟩ = (1/4) Σⱼ ω^{jk}|j⟩ where ω = e^{2πi/16}. With k=7, every basis state |j⟩ (j=0,...,15) receives equal magnitude amplitude |1/4|² = 1/16.

5. **Final state**: Uniform superposition (1/4)Σⱼ₌₀¹⁵ e^{7·2πij/16}|j⟩.

**Predicted probability distribution**: All 16 outcomes (0000 through 1111) have equal probability **1/16 = 6.25%**. No single outcome is more likely; the distribution is perfectly uniform.

### Reference answer

Uniform distribution across 16 states

## isqTrain/678

- task_id: `isqTrain/678`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `ancilla_usage`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3559`

### Prompt

请用isQ语言编写一个量子电路：implements the half_full_adder pattern but with a different initial state preparation (flip q[[0, 1]] -> q[2]).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a modified adder circuit where the sum qubit is pre-initialized to |1> before applying the standard adder gates.
2. **Qubits**: Uses 4 qubits (`q[4]`); measures `q[2]` (sum) and `q[3]` (carry).
3. **State Evolution**:
   - Initialize `|q[3]q[2]q[1]q[0]> = |0000>`.
   - Apply `X(q[2])`: state becomes `|0010>`.
   - Apply `CNOT(q[0], q[2])` and `CNOT(q[1], q[2])`: controls `q[0]` and `q[1]` are `|0>`, so target `q[2]` is unchanged.

## isqTrain/39

- task_id: `isqTrain/39`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_arrays`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `787`

### Prompt

Create an isQ quantum circuit that implements a variant of the oracle_boolean pattern using q[4] -> q[5]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

The task asks me to write a reasoning section for an isQ program implementing a variant of oracle_boolean pattern using q[4] -> q[5], with an expanded qubit register compared to the base version.

Let me analyze The implementation:

1. 5 qubits are declared: q[0], q[1], q[2], q[3], q[4]
2. H gates on q[0] and q[1] create superpositions
3. CNOT(q[0], q[2]) and CNOT(q[1], q[3]) copy (entangle) the states
4. Oracle operations: CNOT(q[0], q[2]) and CNOT(q[0], q[3]) - this seems to implement some oracle function
5. H gates on q[0] and q[1] again
6. Measurements on q[0], q[1], and q[4]

Let me trace through the state evolution:

Initial state: |00000>

After H(q[0]) and H(q[1]):
|++000> = 1/2(|00000> + |01000> + |10000> + |11000>)

After CNOT(q[0], q[2]):
1/2(|00000> + |01000> + |10100> + |11100>)

After CNOT(q[1], q[3]):
1/2(|00000> + |01010> + |10100> + |11110>)

After CNOT(q[0], q[2]) - this is the oracle:
1/2(|00000> + |01010> + |10000> + |11010>)

Wait, let me reconsider. CNOT(q[0], q[2]) when q[0] is control and q[2] is target:
- If q[0]=0, q[2] unchanged
- If q[0]=1, q[2] flipped

State before this CNOT: 1/2(|00000> + |01010> + |10100> + |11110>)

For |00000>: q[0]=0, so q[2] stays 0 → |00000>
For |01010>: q[0]=0, so q[2] stays 0 → |01010>
For |10100>: q[0]=1, so q[2] flips 1→0 → |10000>
For |11110>: q[0]=1, so q[2] flips 1→0 → |11010>

After CNOT(q[0], q[2]):
1/2(|00000> + |01010> + |10000> + |11010>)

Now CNOT(q[0], q[3]):
- |00000>: q[0]=0, q[3] unchanged → |00000>
- |01010>: q[0]=0, q[3] unchanged → |01010>
- |10000>: q[0]=1, q[3] flips 0→1 → |10100>
- |11010>: q[0]=1, q[3] flips 1→0 → |11000>

After CNOT(q[0], q[3]):
1/2(|00000> + |01010> + |10100> + |11000>)

Now apply H(q[0]) and H(q[1]).

Let me track the amplitudes more carefully in the q[0], q[1] subspace:

The state is: 1/2(|00⟩|000⟩ + |01⟩|010⟩ + |10⟩|100⟩ + |11⟩|000⟩)

Hmm, I need to be more careful. Let me re-express:
1/2(|0⟩_0|0⟩_1|0⟩_2|0⟩_3|0⟩_4 + |0⟩_0|1⟩_1|0⟩_2|1⟩_3|0⟩_4 + |1⟩_0|0⟩_1|1⟩_2|0⟩_3|0⟩_4 + |1⟩_0|1⟩_1|0⟩_2|0⟩_3|0⟩_4)

In terms of computational basis for q[0], q[1]:
|00⟩ → |000⟩_234
|01⟩ → |010⟩_234
|10⟩ → |100⟩_234
|11⟩ → |000⟩_234

So in the {q[0], q[1]} space:
1/2(|00⟩|000⟩ + |01⟩|010⟩ + |10⟩|100⟩ + |11⟩|000⟩)

Now apply H⊗H on q

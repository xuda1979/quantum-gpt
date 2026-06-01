# ISQ training COT RAG corpus: quantum_algorithms shard 27

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1265

- task_id: `isqTrain/1265`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `data_encoding_qml`, `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2000`

### Prompt

Create an isQ quantum circuit that implements the data_encoding pattern with modified rotation parameters (num_pi6_to_pi4). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit implements a ZZ feature map for data encoding with modified rotation parameters.

**Qubits:** 2 qubits (q[0], q[1]), both measured.

**Gate sequence and state evolution:**

1. Initial state: |00⟩

2. H(q[0]); H(q[1]): Creates |++⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2

3. Rz(π/3, q[0]): Rotates q[0] by π/3 around Z-axis
   - Applies phase: |0⟩→|0⟩, |1⟩→e^(iπ/3)|1⟩
   - State: (|00⟩ + |01⟩ + e^(iπ/3)|10⟩ + e^(iπ/3)|11⟩)/2

4. Rz(π/4, q[1]): Rotates q[1] by π/4 around Z-axis
   - State: (|00⟩ + e^(iπ/4)|01⟩ + e^(iπ/3)|10⟩ + e^(iπ/3+iπ/4)|11⟩)/2

5. CNOT(q[0], q[1]); Rz(0.54831135561608, q[1]); CNOT(q[0], q[1]):
   - This is equivalent to Rzz(0.54831135561608) between q[0] and q[1]
   - The ZZ interaction applies phase e^(iφ/2) to |00⟩, e^(-iφ/2) to |01⟩ and |10⟩, e^(iφ/2) to |11⟩... wait, let me recalculate.
   
   Actually, CNOT-Rz(φ, target)-CNOT implements ZZ interaction. Let me trace through:
   
   After CNOT(q[0], q[1]): flips q[1] when q[0]=|1⟩
   - (|00⟩ + e^(iπ/4)|01⟩ + e^(iπ/3)|11⟩ + e^(iπ/3+iπ/4)|10⟩)/2
   
   After Rz(0.54831135561608, q[1]): applies phase e^(iφ/2) to |0⟩ and e^(-iφ/2) to |1⟩ on q[1]
   where φ = 0.54831135561608
   
   Wait, Rz(θ) = diag(e^(-iθ/2), e^(iθ/2)). So:
   - |00⟩ gets multiplied by e^(-iφ/2)
   - |01⟩ gets multiplied by e^(iφ/2)  
   - |10⟩ gets multiplied by e^(iφ/2) ... wait, after CNOT, q[1] state for |10⟩ is |1⟩
   
   Let me redo. After CNOT(q[0],q[1]):
   |00⟩→|00⟩, |01⟩→|01⟩, |10⟩→|11⟩, |11⟩→|10⟩
   
   State: (|00⟩ + e^(iπ/4)|01⟩ + e^(iπ/3)|11⟩ + e^(iπ/3+iπ/4)|10⟩)/2
   
   After Rz(φ, q[1]):
   |00⟩: q[1]=0, multiply by e^(-iφ/2) → e^(-iφ/2)|00⟩
   |01⟩: q[1]=1, multiply by e^(iφ/2) → e^(iφ/2)·e^(iπ/4)|01⟩
   |11⟩: q[1]=1, multiply by e^(iφ/2) → e^(iφ/2)·e^(iπ/3)|11⟩
   |10⟩: q[1]=0, multiply by e^(-iφ/2) → e^(-iφ/2)·e^(iπ/3+iπ/4)|10⟩
   
   After CNOT(q[0],q[1]):
   |00⟩→|00⟩, |01⟩→|01⟩, |11⟩→|10⟩, |10⟩→|11⟩
   
   So: e^(-iφ/2)|00⟩ + e^(iπ/4+iφ/2)|01⟩ + e^(iπ/3+iφ/2)|10⟩ + e^(iπ/3+iπ/4-iφ/2)|11⟩
   
   All divided by 2.

6. H(q

## isqTrain/1850

- task_id: `isqTrain/1850`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_arrays`, `isq_syntax_procedures`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `253`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[3];
procedure balanced_oracle(qbit a, qbit b, qbit out) {
    CNOT(a, out);
    CNOT(b, out);
}
procedure main() {
    balanced_oracle(q[0], q[1], q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes 3 qubits to the ground state: |000>.
2. The `balanced_oracle` first applies `CNOT(q[0], q[2])`. Since the control q[0] is in state |0>, the target q[2] is unchanged, leaving the state as |000>.
3. Next, it applies `CNOT(q[1], q[2])`. Since the control q[1] is in state |0>, the target q[2] remains unchanged, leaving the state as |000>.
4. The final quantum state before measurement is |000>.
5. Predicted probability distribution: {'000': 1.0}

### Reference answer

{'predicted_probs': {'000': 1.0}, 'explanation': 'Balanced oracle on |00⟩ yields |000⟩.'}

## isqTrain/777

- task_id: `isqTrain/777`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3548`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[5];

procedure main() {
    // Set all three input qubits to |1>
    X(q[0]);
    X(q[1]);
    X(q[2]);
    // Add x0 to sum: sum_bit0 = x0
    CNOT(q[0], q[3]);
    // Add x1 with half-adder carry propagation
    Toffoli(q[1], q[3], q[4]);
    CNOT(q[1], q[3]);
    // Add x2 with half-adder carry propagation
    Toffoli(q[2], q[3], q[4]);
    CNOT(q[2], q[3]);
    // Measure the 2-bit sum
    M(q[3]);
    M(q[4]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants an analysis of the provided isQ program, which implements a ripple-carry adder for 3 qubits (all initialized to |1>). The output must be a step-by-step reasoning of the quantum state evolution, starting with "## Circuit Analysis", using Dirac notation, and ending with the probability distribution.

2.  **Analyze the Circuit**:
    *   Initial state: |00000> (5 qubits)
    *   `X(q[0]); X(q[1]); X(q[2]);`: State becomes |11100>
    *   `CNOT(q[0], q[3]);`: q[3] flips because q[0] is 1. State becomes |11110>. (Sum bit $q_3 = 1$, Carry bit $q_4 = 0$)
    *   `Toffoli(q[1], q[3], q[4]);`: q[4] flips because q[1] and q[3] are both 1. State becomes |11111>.
    *   `CNOT(q[1], q[3]);`: q[3] flips because q[1] is 1. State becomes |11101>. ($q_3$ goes from 1 to 0).
    *   `Toffoli(q[2], q[3], q[4]);`: q[4] doesn't flip because q[3] is 0. State remains |11101>.
    *   `CNOT(q[2], q[3]);`: q[3] flips because q[2] is 1. State becomes |11111>.
    *   Measurements: `M(q[3])` and `M(q[4])`.

3.  **Verify the Math**:
    *   $x_0 = 1, x_1 = 1, x_2 = 1$. Sum = $1 + 1 + 1 = 3$.
    *   In binary, sum is 11 ($q_4 q_3 = 11$).
    *   Let's trace the classical bits:
        *   Init: $q_3=0, q_4=0$
        *   Add $x_0$: `CNOT(x_0, q_3)` -> $q_3 = x_0 = 1$.
        *   Add $x_1$:
            *   `Toffoli(x_1, q_3, q_4)` -> $q_4 = x_1 \cdot q_3 = 1 \cdot 1 = 1$.
            *   `CNOT(x_1, q_3)` -> $q_3 = q_3 \oplus x_1 = 1 \oplus 1 = 0$.
        *   Add $x_2$:
            *   `Toffoli(x_2, q_3, q_4)` -> $q_4 = q_4 \oplus (x_2 \cdot q_3) = 1 \oplus (1 \cdot 0) = 1$.
            *   `CNOT(x_2, q_3)` -> $q_3 = q_3 \oplus x_2 = 0 \oplus 1 = 1$.
        *   Final $q_3=1, q_4=1$.
    *   Wait, let's re-verify the Toffoli step in the state vector evolution:
        *   Initial: 00000
        *   X gates: 11100
        *   CNOT(q0, q3): 11110
        *   Toffoli(q1, q3, q4): 11111
        *   CNOT(q1, q3): 11101
        *   Toffoli(q2, q3, q4): 11101 (since q3=0)
        *   CNOT(q2, q3): 11111
    *   Matches perfectly.

4.  **Format the Output**:
    *   Start with "## Circuit Analysis"
    *   State initialization: |00000> -> |11100>
    *   CNOT(q0, q3) -> |11110>
    *   Toffoli(q1, q3, q4) -> |11111>
    *   CNOT(q1, q3) -> |11101>
    *   Toffoli(q2, q3, q4) -> |11101>
    *   CNOT(q2, q3) -> |11111>
    *   Final state: |11111>
    *   Measuring q[3] and q[4] yields |11> with 100% probability.

### Reference answer

{'predicted_probs': {'3': 1.0}, 'explanation': 'Parametric variant of isqEval/283. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1769

- task_id: `isqTrain/1769`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5641`

### Prompt

Code this in isQ: Bernstein-Vazirani for the secret string s = 111111 (6 qubits). All bits are 1.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement Bernstein-Vazirani to find the secret 6-bit string $s = 111111$ using a single quantum query.
2. **Qubits**: 6 input qubits `q[0..5]` (measured) and 1 ancilla `anc[0]`.
3. **State Evolution**:
   - Initialize to $|000000\rangle_q|1\rangle_a$.
   - Apply $H^{\otimes 6}$ to inputs and $H$ to ancilla: $\sum_{x \in \{0,1\}^6} |x\rangle_q \otimes |-\rangle_a$.
   - Apply the oracle $U_f$ (CNOT from each of the 6 qubits to the ancilla). Because the ancilla is in $|-\rangle$, this phase-kicks back $(-1)^{x \cdot s}$: $\sum_{x} (-1)^{x \cdot 111111}|x\rangle_q |-\rangle_a$.
   - Apply $H^{\otimes 6}$ to the input qubits. By Hadamard transform identities, this maps the phase-encoded string back to the computational basis: $|111111\rangle_q |-\rangle_a$.
4. **Measurement**: Measuring `q[0..5]` deterministically yields the bitstring `111111` with probability 1.0.

## isqTrain/3027

- task_id: `isqTrain/3027`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `3240`

### Prompt

Code this in isQ: creates a 4-qubit GHZ state and then applies an X gate to qubit 2.

Requirements:
- Declare `qbit q[4];` at global scope.
- Measure all 4 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a 4-qubit GHZ state and apply an X gate to qubit 2.
2. **Qubits**: 4 qubits declared globally (`q[4]`), all 4 measured.
3. **State evolution**:
   - Start: |0000⟩
   - H(q[0]): (|0000⟩ + |1000⟩)/√2
   - CNOT(q[0], q[1]): (|0000⟩ + |1100⟩)/√2
   - CNOT(q[1], q[2]): (|0000⟩ + |1110⟩)/√2
   - CNOT(q[2], q[3]): (|0000⟩ + |1111⟩)/√2 — GHZ state formed
   - X(q[2]): (|0010⟩ + |1101⟩)/√2 — flips qubit 2 in each term
4. **Measurement**: Each term has equal amplitude 1/√2, giving probabilities {|0010⟩: 0.5, |1101⟩: 0.5}.

## isqExpand/algo/80

- task_id: `isqExpand/algo/80`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `grover`, `amplitude_amplification`, `oracle`, `multi_controlled_logic`
- source: `isq_expansion`
- dataset_index: `3625`

### Prompt

Create an isQ quantum circuit that implements Grover's algorithm on 3 qubits to search for the state |100>. Apply one Grover iteration (oracle + diffusion). The oracle should flip the phase of |100> only. Note that |100> means q[0]=1, q[1]=0, q[2]=0, so X gates are needed on q[1] and q[2] before the multi-controlled Z.

### Chain-of-thought reasoning

## 推理
目标：3比特Grover搜索|100>态。

### Oracle设计
|100>: q[0]=1, q[1]=0, q[2]=0
CCZ需要所有控制位为1才触发。q[0]已经是1，需要对q[1]和q[2]施加X门：
- X(q[1]); X(q[2]); — 使条件变为检测原始q[1]=0, q[2]=0
- ctrl @[q[0], q[1]] Z(q[2]); — 触发相位翻转
- X(q[1]); X(q[2]); — 恢复

### 概率
N=8, M=1, 1次迭代:
|100>在概率数组中的索引是4（二进制100=4）
P(|100>) = 25/32 = 0.78125
P(每个非目标态) = 1/32 = 0.03125

## isqTrain/3512

- task_id: `isqTrain/3512`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `multi_controlled_logic`, `reversible_computing`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `2158`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```
import std;

qbit q[3];

procedure main() {
    X(q[0]);
    X(q[1]);
    ctrl ctrl X(q[0], q[1], q[2]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial State**: The 3-qubit system starts in the basis state $|000\rangle$.
2. **X Gates**: Applying `X(q[0])` and `X(q[1])` flips the first two qubits, changing the state to $|110\rangle$.
3. **Toffoli Gate**: The `ctrl ctrl X(q[0], q[1], q[2])` gate (Toffoli) flips the target qubit `q[2]` since both controls `q[0]` and `q[1]` are in the $|1\rangle$ state. The state evolves to $|111\rangle$.
4. **CNOT Gate**: The `CNOT(q[0], q[1])` gate flips the target `q[1]` because the control `q[0]` is $|1\rangle$. The state becomes $|101\rangle$.
5. **Measurement**: The system is measured in the computational basis.

**Predicted probability distribution:**
- $|101\rangle$: 100% (1.0)

### Reference answer

{'predicted_probs': {'101': 1.0}, 'explanation': 'The output is |101> with probability 1.0'}

## isqTrain/865

- task_id: `isqTrain/865`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2179`

### Prompt

帮我写一个isQ程序：implements a variant of the quantum_logic_gate pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Implement a logical OR gate using De Morgan's laws (OR = NOT(NOT(a) AND NOT(b))) on a 5-qubit register, leaving the additional qubits untouched in the ground state.
2. **Qubits:** The circuit requires 5 qubits (`q[5]`), and all 5 are measured.
3. **State Evolution:**
   - Start in the ground state |00000>. Apply X to q[0] to set a=1. State: |10000>.
   - Negate inputs for De Morgan: apply X to q[0] and q[1]. State: |01000>.
   - Apply a Toffoli gate to q[0], q[1], q[2] to compute the AND of the negated inputs. Since only one control is |1>, q[2] remains |0>. State: |01000>.
   - Restore the original inputs by applying X to q[0] and q[1]. State: |10000>.
   - Negate the AND result to get the OR by applying X to q[2]. State: |10100>.
4. **Probabilities:** The final quantum state is exactly |10100>. Measuring all qubits yields the bitstring '10100' (where q[0] is the highest bit) with a probability of 1.0.

## isqTrain/2808

- task_id: `isqTrain/2808`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `138`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[2];

procedure main(){
    X(q[0]); 

    H(q[0]);
    CNOT(q[0],q[1]);
    M(q[0]);
    M(q[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. Initial state is |00>.
2. X(q[0]) flips the first qubit to |1>, changing the state to |10>.
3. H(q[0]) puts the first qubit into superposition |- > = (|0> - |1>)/√2, resulting in the state (|00> - |10>)/√2.
4. CNOT(q[0], q[1]) flips the target q[1] when the control q[0] is |1>, entangling them into the final state (|00> - |11>)/√2.
5. Measuring both qubits yields a 50% chance for the |00> state and a 50% chance for the |11> state.

Probability distribution: [0.5, 0.0, 0.0, 0.5]

### Reference answer

{'predicted_probs': {'00': 0.5000000000000001, '11': 0.4999999999999999}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqExpand/algo/37

- task_id: `isqExpand/algo/37`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `shor`, `factoring`, `order_finding`, `qft`, `modular_exponentiation`
- source: `qa_pipeline`
- dataset_index: `2478`

### Prompt

请详细解释Shor算法的基本原理。它是如何将大数分解问题转化为周期查找问题的？为什么量子计算机能比经典计算机更高效地完成这一任务？

### Chain-of-thought reasoning

## 推理
目标：全面解释Shor算法。

逻辑链：
1. 整数分解 → 求阶问题（数论归约）
2. 量子部分：叠加 → 模幂 → QFT → 测量
3. 经典后处理：连分数展开恢复周期
4. 复杂度对比：多项式 vs 亚指数
5. 实际影响与当前限制

Shor算法的核心洞察是周期性可以被QFT高效提取，而经典计算机无法做到这一点。

### Reference answer

## Shor算法

### 核心思想
Shor算法将整数分解问题归约为**求阶（order-finding）**问题，再利用**量子傅里叶变换（QFT）**高效求解。

### 数学基础
给定要分解的合数 N：
1. 随机选取 a（1 < a < N，且 gcd(a, N) = 1）
2. 求 a 模 N 的阶 r，即满足 a^r ≡ 1 (mod N) 的最小正整数 r
3. 若 r 是偶数，则 gcd(a^{r/2} ± 1, N) 大概率给出 N 的非平凡因子

### 为什么需要量子计算
经典算法求阶的最优复杂度是亚指数级（数域筛法）。Shor算法通过以下量子步骤实现多项式复杂度：

1. **叠加态创建**：用 Hadamard 门将计数寄存器置于均匀叠加态
2. **模幂运算**：计算 |x>|0> → |x>|a^x mod N>（酉操作）
3. **量子傅里叶变换**：对计数寄存器做 QFT，提取周期信息
4. **测量与经典后处理**：测量得到的值通过连分数展开算法恢复周期 r

### 复杂度
- 量子部分：O((log N)^2 log(log N)) 量子门
- 经典后处理：O((log N)^3) 运算
- 总体：**多项式时间**，而最优经典算法是亚指数时间

### 实际影响
Shor算法对RSA加密体系构成理论威胁，因为RSA的安全性依赖于大数分解的困难性。这推动了后量子密码学的发展。

### 关键限制
- 需要容错量子计算机（大量逻辑qubit）
- 当前最大的演示：分解 21 = 3 × 7（使用特殊优化）
- 分解 2048 位 RSA 密钥估计需要数千个逻辑 qubit

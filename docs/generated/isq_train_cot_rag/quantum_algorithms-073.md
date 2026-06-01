# ISQ training COT RAG corpus: quantum_algorithms shard 73

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3453

- task_id: `isqTrain/3453`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `487`

### Prompt

实现以下量子计算任务（使用isQ）：a simple phase estimation using kickback in isQ.

Estimate the phase of the S gate (pi/2) applied to eigenstate |1>.

Circuit:
1. Prepare q[1] in |1> (eigenstate of S)
2. H on q[0] (precision qubit)
3. Controlled-S from q[0] to q[1]
4. The phase pi/2 kicks back to q[0]
5. H on q[0] to measure

After kickback, q[0] is in state (|0> + e^{i*pi/2}|1>)/sqrt(2).
After H: probabilities are cos^2(pi/4) and sin^2(pi/4) = 0.5 each.

Declare 2 qubits, measure q[0] only.

### Chain-of-thought reasoning

## Reasoning
**Goal:** Estimate the phase of the S gate (π/2) applied to eigenstate |1⟩ using single-qubit kickback phase estimation.

**Qubits:** 2 qubits (q[0] = precision/measurement, q[1] = target eigenstate). Only q[0] is measured.

**State evolution:**
1. **Initial:** |00⟩
2. **X(q[1]):** |01⟩ — prepares target in eigenstate |1⟩
3. **H(q[0]):** (|0⟩ + |1⟩)/√2 ⊗ |1⟩ = (|01⟩ + |11⟩)/√2
4. **ctrl S(q[0], q[1]):** S|1⟩ = i|1⟩, so the control |1⟩ component picks up factor i: (|01⟩ + i|11⟩)/√2 = (|0⟩ + i|1⟩)/√2 ⊗ |1⟩ — phase π/2 kicks back to q[0]
5. **H(q[0]):** H(|0⟩ + i|1⟩)/√2 = ((1+i)|0⟩ + (1-i)|1⟩)/2

**Probabilities:** P(|0⟩) = |1+i|²/4 = 0.5, P(|1⟩) = |1-i|²/4 = 0.5 — equal superposition results since the phase π/2 produces an equal-amplitude state after Hadamard decoding.

## isqTrain/677

- task_id: `isqTrain/677`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `ancilla_usage`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4504`

### Prompt

Implement a quantum circuit in isQ: implements a variant of the half_full_adder pattern using q[4] -> q[6]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
The circuit implements a half-adder on qubits 0-3 with two idle ancilla qubits (4,5) to demonstrate register scaling.

**Qubits:** 6 total (q[0..5]). Inputs: q[0], q[1] (both set to |1⟩). Sum: q[2]. Carry: q[3]. Idle: q[4], q[5]. Measured: q[2], q[3], q[4], q[5].

**State evolution:**
1. Initial: |000000⟩
2. X(q[0]), X(q[1]): |110000⟩ — both inputs set to |1⟩
3. CNOT(q[0], q[2]): |111000⟩ — q[2] flips (control q[0]=1)
4. CNOT(q[1], q[2]): |110000⟩ — q[2] flips again (control q[1]=1), returning to |0⟩ (1⊕1=0)
5. Toffoli(q[0], q[1], q[3]): |110100⟩ — q[3] flips (both controls are |1⟩), giving carry=1

**Measurement:** q[2]=0, q[3]=1, q[4]=0, q[5]=0. With earlier measured qubit as higher bit: bitstring = |0100⟩ with probability 1.0. This correctly encodes sum=0 (1⊕1) and carry=1 (1∧1).

## isqTrain/3966

- task_id: `isqTrain/3966`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `570`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```
import std;
// QFT on 3 qubits with input state |111>
qbit q[3];

procedure main() {
    // Prepare input state |111>
    X(q[0]);
    X(q[1]);
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
    CNOT(q[2], q[0]);
    CNOT(q[2], q[0]);
    // Measure after QFT
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

## Bug Analysis

**1. Bug location:** The third CNOT in the swap operation (three-CNOT decomposition) at the end of the QFT has swapped control/target arguments:
- Buggy: `CNOT(q[2], q[0])` (line 3 of swap)
- Correct: `CNOT(q[0], q[2])`

**2. Fix:** A proper swap (three-CNOT decomposition)(q[0], q[2]) requires the sequence CNOT(q[0],q[2]) → CNOT(q[2],q[0]) → CNOT(q[0],q[2]). The buggy code repeats `CNOT(q[2],q[0])` for the third gate instead of `CNOT(q[0],q[2])`, which does not restore q[2] to the original q[0] value — it instead flips q[0] again, corrupting the state.

**3. State evolution (corrected):**
- Prepare |111⟩ via X on all three qubits.
- QFT stages apply H and controlled-Rz rotations: this maps |7⟩ → (1/√8) Σₖ e^{2πi·7k/8}|k⟩ (up to qubit ordering, with q[0] as LSB).
- Correct swap (three-CNOT decomposition)(q[0],q[2]) reverses the qubit order, yielding (1/√8) Σₖ e^{iφₖ}|k⟩ with equal magnitude amplitudes.
- Measurement gives uniform probabilities: P(|k⟩) = 1/8 = 0.125 for all k ∈ {0,…,7}, matching the predicted output.

## isqTrain/1090

- task_id: `isqTrain/1090`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `interference`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2828`

### Prompt

Trace through the quantum state evolution in this circuit and predict the measurement probabilities.

```isq
import std;

// Oracle for balanced function f(x) = x[0] XOR x[1]
oracle bool[1] f(bool x[2]) {
    // XOR of two input bits yields a balanced function
    bool res[] = [x[0] != x[1]];
    return res;
}

// Input register: 2 qubits
qbit q[2];
// Ancilla qubit for phase kickback
qbit anc[1];

procedure main() {
    // Prepare ancilla in |-> state for phase kickback
    X(anc[0]);
    H(anc[0]);
    // Create uniform superposition on input register
    H(q[0]); H(q[1]);
    // Single oracle query -- the key quantum speedup
    f(q, anc);
    // Interfere to extract function type
    H(q[0]); H(q[1]);
    // Measure input register only
    // Balanced function guarantees non-zero outcome
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The objective is to analyze an isQ quantum program implementing the Deutsch-Jozsa algorithm for a 2-bit balanced function (XOR), track the quantum state through the circuit, and predict the final measurement probabilities.

2.  **Analyze the isQ Code**:
    *   `qbit q[2]`: Initial state $|00\rangle$.
    *   `qbit anc[1]`: Initial state $|0\rangle$. (Wait, the code applies X(anc[0]) then H(anc[0]), so it becomes $|-\rangle$. But wait, the prompt says "Measure input register only" `M(q[0]); M(q[1]);`. So ancilla is not measured. The state of ancilla won't affect the measurement probabilities directly in the calculation if we trace it out or just ignore it due to phase kickback).
    *   Initial combined state (q, anc): $|00\rangle \otimes |0\rangle$.
    *   `X(anc[0]); H(anc[0]);`: anc[0] becomes $|-\rangle$.
    *   `H(q[0]); H(q[1]);`: Input register becomes $\frac{|00\rangle + |01\rangle + |10\rangle + |11\rangle}{2}$.
    *   Combined state: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle) \otimes |-\rangle$.
    *   `f(q, anc);`: The oracle computes $f(x) = x[0] \oplus x[1]$.
        *   $f(00) = 0$
        *   $f(01) = 1$
        *   $f(10) = 1$
        *   $f(11) = 0$
        *   Oracle applies phase kickback: $|x\rangle \otimes |-\rangle \to (-1)^{f(x)}|x\rangle \otimes |-\rangle$.
        *   New combined state: $\frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle) \otimes |-\rangle$.
    *   `H(q[0]); H(q[1]);`: Applied to input register.
        *   $H^{\otimes 2} \frac{1}{2}(|00\rangle - |01\rangle - |10\rangle + |11\rangle)$
        *   Recall that $H^{\otimes n}|x\rangle = \frac{1}{2^{n/2}} \sum_z (-1)^{x \cdot z} |z\rangle$.
        *   Alternatively, apply H gate by gate:
            *   $H|0\rangle = |+\rangle$, $H|1\rangle = |-\rangle$.
            *   Current state is $\frac{1}{2}( |0\rangle|0\rangle - |0\rangle|1\rangle - |1\rangle|0\rangle + |1\rangle|1\rangle )$.
            *   Factorizing: $\frac{1}{2} (|0\rangle(|0\rangle - |1\rangle) - |1\rangle(|0\rangle - |1\rangle)) = \frac{1}{2} (|0\rangle - |1\rangle)(|0\rangle - |1\rangle) = |--\rangle$.
            *   So $H(q[0]); H(q[1]);$ transforms $|--\rangle$ to $|11\rangle$ because $H^2 = I$, so $H|--\rangle = |11\rangle$.
    *   Final state of input register: $|11\rangle$.
    *   Measurements: `M(q[0]); M(q[1]);`
    *   Result: 100% chance of measuring $|11\rangle$ (which corresponds to binary 3, or bitstring '11').

3.  **Format the Output**:
    *   Must start with "## Circuit Analysis".
    *   Use Dirac notation.
    *   3-8 lines of step-by-step reasoning (concise).
    *   State final probability distribution clearly.
    *   Output ONLY the analysis section, no code blocks.

4.  **Drafting the steps**:
    *   **Step 1**: Initial state is $|00\rangle|0\rangle$. X and H on ancilla puts it in $|-\rangle$. H gates on input register create superposition: $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle + |11\rangle)|

### Reference answer

{'predicted_probs': {'3': 1.0}, 'explanation': 'Parametric variant of isqEval/431. Dimension: predict probabilities for reference circuit.'}

## isqTrain/2906

- task_id: `isqTrain/2906`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_oracle`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5132`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
oracle bool[1] g(bool a[3]) {
    bool s[] = [true, false, true];
    bool ba[] = s & a;
    bool res[1];
    res[0] = ba[0] != ba[1] != ba[2];
    return res;
}
qbit q[3];
qbit anc[1];

procedure main() {
    X(anc);
    H(anc);
    H(q);
    g(q, anc);
    H(q);
    for i in 0:3 {
        M(q[i]);
    }
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Goal:** Provide a step-by-step reasoning of the isQ quantum circuit to explain the final quantum state and probability distribution.
    *   **Input:** An isQ program implementing a variant of Bernstein-Vazirani or Grover's algorithm, specifically finding a secret string.
    *   **Output Format:** Start with "## Circuit Analysis". 3-8 lines for simple circuits, up to 15 for complex ones. Use Dirac notation. End with predicted probabilities.
    *   **Expected Probabilities:** {'101': 1.0}

2.  **Analyze the Circuit:**
    *   Qubits: `q[3]`, `anc[1]`. All initialized to $|0\rangle$.
    *   Initial state: $|0000\rangle$ (qubits q[0], q[1], q[2], anc[0]). Wait, standard isQ index order: `q[0], q[1], q[2], anc[0]`.
    *   `X(anc)`: Flips anc to $|1\rangle$. State: $|0001\rangle$.
    *   `H(anc)`: Applies H to anc. State: $|000\rangle \otimes \frac{|0\rangle - |1\rangle}{\sqrt{2}} = |000-\rangle$.
    *   `H(q)`: Applies H to q[0], q[1], q[2]. State: $\sum_{x \in \{0,1\}^3} |x\rangle \otimes |-\rangle$.
    *   Oracle `g(q, anc)`:
        *   Definition:
            *   `s = [true, false, true]` -> `s = 101` (binary representation where `s[0]=1`, `s[1]=0`, `s[2]=1`).
            *   `ba = s & a` (bitwise AND).
            *   `res = ba[0] != ba[1] != ba[2]` (XOR sum, essentially parity of `s & a`).
            *   Wait, isQ boolean arrays are often MSB or LSB? `s[0]` is true (1), `s[1]` is false (0), `s[2]` is true (1). This means $s = s_0 s_1 s_2 = 101_2$.
            *   The oracle applies $(-1)^{s \cdot a}$ because it targets an ancilla in the $|-\rangle$ state.
            *   Phase kickback: $\sum_x (-1)^{s \cdot x} |x\rangle |-\rangle$.
    *   `H(q)`: Applies H to q[0], q[1], q[2].
        *   This is the Bernstein-Vazirani algorithm.
        *   $H^{\otimes n} \sum_x (-1)^{s \cdot x} |x\rangle = |s\rangle$.
        *   So the state of `q` becomes $|s_0 s_1 s_2\rangle = |101\rangle$.
        *   The ancilla remains in $|-\rangle$.
    *   Measurement: `M(q[i])` for i in 0:3 (which means i=0, i=1, i=2).
    *   State of q is $|101\rangle$. Measuring it gives '101' with 100% probability.

3.  **Draft the Explanation:**
    *   *Step 1:* Initialize 4 qubits to $|0000\rangle$.
    *   *Step 2:* `X(anc)` and `H(anc)` prepare the ancilla in $|-\rangle$. State: $|000\rangle \otimes |-\rangle$.
    *   *Step 3:* `H(q)` creates a uniform superposition over `q`. State: $\frac{1}{2\sqrt{2}} \sum_{x=0}^7 |x\rangle \otimes |-\rangle$.
    *   *Step 4:* The oracle `g` computes the bitwise AND with $s = 101$ and takes the XOR parity. Implemented as a phase oracle via the ancilla, it maps $|x\rangle |-\rangle$ to $(-1)^{s \cdot x} |x\rangle |-\rangle$, where $s = 101$.
    *   *Step 5:* `H(q)` is applied to the `q` register. This is the standard Bernstein-Vazirani inversion step: $H^{\otimes 3} \sum_x (-1)^

### Reference answer

{'predicted_probs': {'101': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/926

- task_id: `isqTrain/926`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3299`

### Prompt

请用isQ语言编写一个量子电路：implements a variant of the boolean_synthesis pattern using q[6] -> q[7]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a boolean synthesis variant computing a majority-like function using 7 qubits, with inputs a=1, b=1, c=0 on q[0-2], intermediate computations on q[3-5], and measuring q[5] and q[6].

2. **Qubits**: 7 qubits (q[0] to q[6]); q[5] and q[6] are measured.

3. **State evolution**:
   - |0000000⟩ → X(q[0]) → |1000000⟩ → X(q[1]) → |1100000⟩ (set inputs a=1, b=1, c=0)
   - Toffoli(q[0], q[1], q[3]): q[3] = a∧b = 1 → |1101000⟩
   - Toffoli(q[0], q[2], q[4]): q[4] = a∧c = 0 → |1101000⟩ (unchanged)
   - CNOT(q[3], q[5]): q[5] = q[3] = 1 → |1101010⟩
   - CNOT(q[4], q[5]): q[5] = q[5]⊕q[4] = 1⊕0 = 1 → |1101010⟩
   - Toffoli(q[1], q[2], q[5]): q[5] = q[5]⊕(b∧c) = 1⊕0 = 1 → |1101010⟩

4. **Measurement**: M(q[5])=1, M(q[6])=0 yields bitstring |10⟩ with probability 1.0, as q[6] was never modified from |0⟩ and the XOR-cascaded OR computation correctly yields 1 for majority(1,1,0)=1.

## isqExpand/algo/70

- task_id: `isqExpand/algo/70`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `barren_plateau`, `variational_algorithm`, `gradient_vanishing`, `vqe`, `qaoa`
- source: `qa_pipeline`
- dataset_index: `3074`

### Prompt

什么是变分量子算法中的贫瘠高原（Barren Plateau）问题？它如何影响VQE和QAOA等算法的训练？请解释其成因和缓解策略。

### Chain-of-thought reasoning

## 推理
目标：解释贫瘠高原问题。

关键要点：
1. 贫瘠高原是变分量子算法中梯度指数级趋零的现象
2. 方差 Var(∂C/∂θ) = O(1/2^n) 随量子比特数指数衰减
3. 主要成因：电路过深、全局代价函数、过度纠缠、噪声
4. 影响VQE（深层拟设）和QAOA（高层数p）的可训练性
5. 缓解：浅层电路、局部代价函数、分层训练、智能初始化

### Reference answer

**贫瘠高原（Barren Plateau）**是变分量子算法面临的关键训练障碍。

## 定义

贫瘠高原指代价函数关于参数的梯度在参数空间中几乎处处指数级趋近于零的现象：

⟨∂C/∂θ_i⟩ = 0, Var(∂C/∂θ_i) = O(1/2^n)

其中n是量子比特数。梯度的方差随量子比特数指数衰减。

## 成因

1. **电路深度过大**：当参数化电路足够深时，其行为趋近于随机酉矩阵（Haar随机），导致梯度消失
2. **全局代价函数**：使用全局可观测量（如作用在所有量子比特上的算符）比局部可观测量更容易产生贫瘠高原
3. **纠缠度过高**：过度纠缠使得局部参数变化的影响被'稀释'到指数大的Hilbert空间中
4. **噪声**：量子硬件噪声也会导致梯度指数衰减

## 对VQE/QAOA的影响

- **VQE**：深层硬件高效拟设可能陷入贫瘠高原，优化器无法找到有意义的梯度方向
- **QAOA**：层数p增大时，QAOA参数景观可能出现贫瘠高原，尤其对随机初始化

## 缓解策略

1. **浅层电路**：限制电路深度，使用问题相关的拟设
2. **局部代价函数**：使用只作用于少量量子比特的可观测量
3. **分层训练**：逐层增加参数并训练，而非一次性训练所有参数
4. **参数相关初始化**：使用经典预计算或启发式方法选择初始参数
5. **对称性约束**：利用问题的对称性减少参数空间

## isQ示例

浅层VQE拟设（不易产生贫瘠高原）：
```isq
import std;
qbit q[2];

procedure main() {
    // 单层Ry+CNOT: 浅层拟设
    Ry(pi/3.0, q[0]);
    Ry(pi/4.0, q[1]);
    CNOT(q[0], q[1]);
    M(q[0]); M(q[1]);
}
```

## isqTrain/1290

- task_id: `isqTrain/1290`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `interference`, `isq_syntax_oracle`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1225`

### Prompt

实现以下量子计算任务（使用isQ）：implements a variant of the fourier_checking pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Let me analyze this Fourier checking/forrelation circuit step by step.

We have 4 qubits q[0], q[1], q[2], q[3], but q[3] is never operated on - it stays in |0> throughout.

Let me trace through the state evolution for q[0], q[1], q[2]:

**Step 1: Initial state**
|000> (for the first 3 qubits, q[3] = |0> always)

**Step 2: First H layer on q[0], q[1], q[2]**
H|0> = |+> = (|0> + |1>)/√2

State: (|0>+|1>)^⊗3 / 2√2 = (1/2√2) Σ_{x∈{0,1}^3} |x>

**Step 3: T gates on all three**
T|+> = (|0> + e^{iπ/4}|1>)/√2

State: (1/2√2) Σ_x e^{iπ|x|/4} |x> where |x| is Hamming weight

**Step 4: CZ(q[0], q[1]) and CZ(q[1], q[2])**
CZ applies Z to target when control is |1>. This adds a phase of -1 when both qubits are |1>.

CZ(q[0], q[1]): phase -1 when q[0]=1 AND q[1]=1
CZ(q[1], q[2]): phase -1 when q[1]=1 AND q[2]=1

So the combined phase from CZ gates for state |x₀x₁x₂>:
-1^{x₀x₁ + x₁x₂}

The state after CZ gates:
(1/2√2) Σ_x e^{iπ|x|/4} · (-1)^{x₀x₁ + x₁x₂} |x>

**Step 5: Second H layer**
H⊗3 transforms |x> → (1/√8) Σ_y (-1)^{x·y} |y>

State: (1/2√2 · √8) Σ_y [Σ_x e^{iπ|x|/4} · (-1)^{x₀x₁ + x₁x₂ + x·y}] |y>

= (1/4) Σ_y [Σ_x e^{iπ|x|/4} · (-1)^{x₀x₁ + x₁x₂ + x·y}] |y>

**Step 6: S gates on all three**
S|0> = |0>, S|1> = i|1>

Phase factor e^{iπ|y|/2} on |y>

State: (1/4) Σ_y e^{iπ|y|/2} [Σ_x e^{iπ|x|/4} · (-1)^{x₀x₁ + x₁x₂ + x·y}] |y>

**Step 7: Final H layer**
Again transforms with H⊗3.

State: (1/4√8) Σ_z [Σ_y e^{iπ|y|/2} (-1)^{y·z} Σ_x e^{iπ|x|/4} (-1)^{x₀x₁ + x₁x₂ + x·y}] |z>

= (1/8√2) Σ_z [Σ_x e^{iπ|x|/4} (-1)^{x₀x₁ + x₁x₂} Σ_y e^{iπ|y|/2} (-1)^{y·(x+z)}] |z>

This is getting complex. Let me just verify numerically with the given expected probabilities.

Expected probabilities:
|0000>: 0.1433058261758408
|0010>: 0.10669417382415923
|0100>: 0.23169417382415922
|0110>: 0.018305826175840787
|1000>: 0.1066941738241592
|1010>: 0.14330582617584087
|1100>: 0.018305826175840794
|1110>: 0.23169417382415927

So q[3] is always 0 (measured as 0), and the probabilities for the first 3 qubits are:
|000>: 0.14331
|001>: 0.10669
|010>: 0.23169
|011>: 0.01831
|100>: 0.

## isqTrain/1127

- task_id: `isqTrain/1127`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5398`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;

// Superdense coding: transmit message '11'
qbit q[2];

procedure main() {
    // Create Bell pair between Alice and Bob
    H(q[0]);
    CNOT(q[0], q[1]);
    // Alice encodes '11': apply Z then X
    // Z flips the phase, X flips the bit
    Z(q[0]);
    X(q[0]);
    // Bob decodes by reversing Bell circuit
    CNOT(q[0], q[1]);
    H(q[0]);
    // Measurement yields the transmitted bits
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations**: The circuit implements superdense coding to transmit the classical message '11'. It applies `H(q[0])`, `CNOT(q[0], q[1])`, `Z(q[0])`, `X(q[0])`, `CNOT(q[0], q[1])`, and `H(q[0])`.
2. **State Evolution**:
   - Initial state is |00>.
   - `H(q[0])` creates a superposition: (|00> + |10>) / √2.
   - `CNOT(q[0], q[1])` entangles the qubits into the Bell state Φ⁺: (|00> + |11>) / √2.
   - `Z(q[0])` flips the phase of the |1> component: (|00> - |11>) / √2.
   - `X(q[0])` flips the bit value of the first qubit: (|10> - |01>) / √2.
   - `CNOT(q[0], q[1])` uncomputes the target

### Reference answer

{'predicted_probs': {'3': 1.0}, 'explanation': 'Parametric variant of isqEval/437. Dimension: predict probabilities for reference circuit.'}

## isqTrain/3532

- task_id: `isqTrain/3532`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `interference`, `ancilla_usage`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `526`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```
import std;

qbit q[4];
qbit anc[1];

procedure main() {
    X(anc[0]);
    H(anc[0]);

    H(q[0]); H(q[1]); H(q[2]); H(q[3]);

    CNOT(q[0], anc[0]);
    CNOT(q[1], anc[0]);
    CNOT(q[3], anc[0]);

    H(q[0]); H(q[1]); H(q[2]); H(q[3]);

    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the circuit**:
    *   Qubits: 4 main qubits `q[0], q[1], q[2], q[3]`, 1 ancilla `anc[0]`. Total 5 qubits.
    *   Initial state: $|00000\rangle$.
    *   $X(anc[0])$: State becomes $|00001\rangle$.
    *   $H(anc[0])$: State becomes $|0000\rangle \otimes |-\rangle$.
    *   $H(q[0]), H(q[1]), H(q[2]), H(q[3])$: State becomes $|+\rangle|+\rangle|+\rangle|+\rangle \otimes |-\rangle$. Equivalently, $H^{\otimes 4}|0000\rangle \otimes |-\rangle$.
    *   Controlled phase kickback via CNOTs:
        *   `CNOT(q[0], anc[0])`
        *   `CNOT(q[1], anc[0])`
        *   `CNOT(q[3], anc[0])` (Note: `q[2]` is NOT connected to `anc[0]`)
        *   The state is $H^{\otimes 4}|0000\rangle \otimes |-\rangle = \frac{1}{4} \sum_{x \in \{0,1\}^4} |x\rangle \otimes |-\rangle$.
        *   Applying CNOTs effectively calculates the parity of $x_0 \oplus x_1 \oplus x_3$ into `anc[0]`.
        *   Since `anc[0]` is in $|-\rangle$, a phase $(-1)$ is kicked back for every bit in the parity sum.
        *   The state becomes $\frac{1}{4} \sum_{x} (-1)^{x_0 \oplus x_1 \oplus x_3} |x\rangle \otimes |-\rangle$.
    *   Final Hadamards on main qubits:
        *   $H^{\otimes 4}$ is applied to `q`.
        *   The state is $H^{\otimes 4} \left( \frac{1}{4} \sum_{x} (-1)^{x_0 \oplus x_1 \oplus x_3} |x\rangle \right) \otimes |-\rangle$.
        *   This is exactly the Bernstein-Vazirani algorithm or phase oracle followed by Hadamards.
        *   The state will be $|s\rangle$ where $s$ is the secret string corresponding to the oracle.
        *   The oracle applies a phase $(-1)^{x \cdot s}$.
        *   Here, the phase is $(-1)^{x_0 \oplus x_1 \oplus x_3}$.
        *   This corresponds to $s = 1011$ in the order $q_0, q_1, q_3$. Wait, the qubits are $q_0, q_1, q_2, q_3$. The sum is $x_0 + x_1 + x_3$. So $s = (1, 1, 0, 1)$ for $(q_0, q_1, q_2, q_3)$.
        *   Let's double check. $(-1)^{x_0 + x_1 + x_3} = (-1)^{x \cdot s}$ where $s = 1101_2$.
        *   Applying $H^{\otimes 4}$ to this state yields $|s\rangle = |1101\rangle$.
    *   Measurements:
        *   `M(q[0]); M(q[1]); M(q[2]); M(q[3]);`
        *   Since the state is $|1101\rangle$, the measurements will yield $q_0=1, q_1=1, q_2=0, q_3=1$.
        *   In binary string format, it's usually $q_0 q_1 q_2 q_3 = 1101$.
        *   Let's check the bit ordering in standard isQ / probs mode: "array indexed by measurement bitstring (earlier measured qubit = higher bit)".
        *   So $M(q[0])$ is the highest bit (bit 3), $M(q[1])$ is bit 2, $M(q[2])$ is bit 1, $M(q[3])$ is bit 0.
        *   Value = $1 \cdot 2^

### Reference answer

{'predicted_probs': {'1101': 1.0}, 'explanation': 'The output is |1101> with probability 1.0'}

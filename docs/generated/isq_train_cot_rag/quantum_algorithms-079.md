# ISQ training COT RAG corpus: quantum_algorithms shard 79

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1406

- task_id: `isqTrain/1406`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5344`

### Prompt

Help me write isQ code that the Bernstein-Vazirani algorithm to find the secret string s = 10101 (MSB first). Use 5 input qubits and 1 ancilla.

### Chain-of-thought reasoning

## Reasoning

**Goal:** Find the secret string $s = 10101$ using the Bernstein-Vazirani algorithm with 5 input qubits and 1 ancilla (ancilla not measured).

**State evolution:**
1. **Init:** $|00000\rangle|0\rangle$
2. **X, H on ancilla:** $|00000\rangle|-\rangle$
3. **H on inputs:** $\frac{1}{\sqrt{32}}\sum_{x \in \{0,1\}^5}|x\rangle|-\rangle$
4. **Oracle (CNOT at positions 0,2,4 for $s=10101$):** Phase kickback applies $(-1)^{s \cdot x}$, yielding $\frac{1}{\sqrt{32}}\sum_x (-1)^{s \cdot x}|x\rangle|-\rangle$
5. **H on inputs again:** $H^{\otimes 5}$ performs the Hadamard transform, and the amplitude of basis state $|z\rangle$ is $\frac{1}{32}\sum_x(-1)^{(s \oplus z)\cdot x}$, which equals 1 only when $s = z$
6. **Final state:** $|10101\rangle|-\rangle$

**Measurement:** The input register is $|10101\rangle$ with certainty, so measuring yields $|10101\rangle$ with probability 1.0.

## isqTrain/983

- task_id: `isqTrain/983`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4988`

### Prompt

Code this in isQ: implements the suzuki_trotter pattern with modified rotation parameters (num_pi4b_to_pi6). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

Let me analyze this circuit carefully.

The circuit implements a Suzuki-Trotter decomposition for simulating $e^{-it(XX + ZZ)}$ (or similar Hamiltonian). Let me trace through the state evolution.

**Goal**: Implement second-order Suzuki-Trotter with modified rotation parameters, starting from $|10\rangle$.

**Parameters**:
- $t = \pi/8$
- Half-step Rz angle: $t = \pi/8 \approx 0.392699$
- Full-step Rz angle: $2t = \pi/4 \approx 0.523599$

Wait, let me re-read the comments. The circuit says:
- S2(t) = e^{-i*t/2*ZZ} * e^{-i*t*XX} * e^{-i*t/2*ZZ}

But the Rz angles are:
- For half-step ZZ: angle = 0.392699... = t = π/8
- For full-step XX: angle = 0.523599... = π/4 = 2t

The note says Rz angle for half-step is 2*(t/2) = t and Rz angle for full step is 2*t.

Now the "modified rotation parameters (num_pi4b_to_pi6)" - this seems to be asking me to modify the rotation parameters from π/4 to π/6 or something similar. But wait, I'm asked to generate reasoning, not code.

Let me just trace the circuit as given:

Starting state: $|00\rangle \xrightarrow{X(q[0])} |10\rangle$

**First half-step: e^{-it/2 ZZ}** using CNOT-Rz-CNOT

CNOT(q[0], q[1]) on |10⟩: flips q[1] when q[0]=1 → |11⟩

Rz(t, q[1]) on |11⟩: Rz(θ)|1⟩ = e^{-iθ/2}|1⟩ (up to phase conventions... actually Rz(θ) = [[1,0],[0,e^{iθ}]] or [[e^{-iθ/2},0],[0,e^{iθ/2}]] depending on convention)

Let me be careful with the Rz convention. In isQ, Rz(θ, q) has matrix [[1,0],[0,e^{iθ}]] (or equivalently e^{-iθZ/2}).

Actually, looking at the predicted output probabilities, let me just compute them.

Let me use the convention Rz(θ) = [[1,0],[0,e^{iθ}]].

After CNOT(q[0], q[1]) on |10⟩: |11⟩

After Rz(t, q[1]) where t = π/8:
|11⟩ → e^{iπ/8}|11⟩

After CNOT(q[0], q[1]): e^{iπ/8}|10⟩

So after first half-step: e^{iπ/8}|10⟩ (just a phase)

**Full XX step: e^{-it XX}** using H-H-CNOT-Rz-CNOT-H-H

H(q[0])H(q[1]) on |10⟩:
H|1⟩⊗H|0⟩ = |−⟩|+⟩ = (|0⟩-|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2

= (|00⟩ + |01⟩ - |10⟩ - |11⟩)/2

CNOT(q[0], q[1]):
|00⟩→|00⟩, |01⟩→|01⟩, |10⟩→|11⟩, |11⟩→|10⟩

= (|00⟩ + |01⟩ - |11⟩ - |10⟩)/2

Rz(2t, q[1]) where 2t = π/4:
|00⟩→|00⟩, |01⟩→e^{iπ/4}|01⟩, |10⟩→|10⟩, |11⟩→e^{iπ/4}|11⟩

= (|00⟩ + e^{iπ/4}|01⟩ - e^{iπ/4}|11⟩ - |10⟩)/2

CNOT(q[0], q[1]):
= (|00⟩ + e^{iπ/4}|01⟩ - e^{iπ/4}|10⟩ - |11⟩)/2

Hmm wait, let me redo: |00⟩→|00⟩, |01⟩→|01⟩, |10⟩→|11⟩, |11⟩→|10⟩

= (|00⟩ + e^{iπ/4}|01⟩ - |10⟩ - e^{iπ/4}|11⟩)/2

## isqTrain/27

- task_id: `isqTrain/27`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `interference`, `isq_syntax_arrays`, `isq_syntax_oracle`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `895`

### Prompt

I need an isQ program to implements a variant of the oracle_boolean pattern using q[5] -> q[6]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

We need to generate reasoning for the given isQ program. The program implements a Bernstein-Vazirani (BV) oracle for s="1111" on 4 input qubits, with an ancilla qubit prepared in |->. There are 6 qubits total (q[0..5]), but q[5] is measured but never used; it's always |0>? Actually, q[5] is never initialized; initial state is |0>. It's measured, so outcome will be 0. The expected measurement probabilities are given as {|11110>: 1.0}. But note: measurement bitstring ordering: earlier measured qubit = higher bit. So the measured qubits are q[0], q[1], q[2], q[3], q[5] in that order. So bitstring: q[0] is highest bit (MSB), then q[1], q[2], q[3], q[5] as LSB. So the bitstring should be: q[0]=1, q[1]=1, q[2]=1, q[3]=1, q[5]=0 => binary "11110". Indeed matches expected. So the circuit is standard BV: after H on inputs, the oracle flips ancilla conditionally, then H on inputs yields the secret string. The ancilla is in |-> so the phase kickback yields state |s> on inputs. Ancilla is not measured. The extra qubit q[5] remains |0> and measured gives 0.

Now we need to produce reasoning:

Goal: Implement a variant of the oracle_boolean pattern (Bernstein-Vazirani) using q[5] -> q[6] but program uses q[0..4] and q[5] as dummy. Actually the instruction says: "Write an isQ program that implements a variant of the oracle_boolean pattern using q[5] -> q[6]." That might be confusing: maybe they want to shift indices? The reference uses q[0..5] but oracle is q[0..3] input, q[4] ancilla, and q[5] measured. So "q[5] -> q[6]" might refer to an earlier pattern? Possibly it means the oracle uses qubit 5 as ancilla? But here ancilla is q[4]. Anyway, we just need to reason about the given program.

We should follow the format: start with "## Reasoning". Then explain:

1. Goal: implement Bernstein-Vazirani algorithm for secret string "1111" using 4 input qubits, an ancilla in |->, and an extra idle qubit.

2. Qubits: total 6 qubits (q[0..5]), measured: q[0], q[1], q[2], q[3], q[5] (5 qubits measured). q[4] ancilla, q[5] unused.

3. Step-by-step evolution:

- Initially all |0>. After X(q[4]): q[4] becomes |1>. Then H on q[0..4]: q[0..3] each become |+>, q[4] becomes |-> (since H|1> = |->). So state: |+>|+>|+>|+>|->|0> for q[0..5]? Actually q[5] untouched, stays |0>. So product state.

- Oracle: CNOT from each input q[0..3] to q[4]. Since q[4] is |->, this induces phase kickback: For each input qubit, if it is |1> it flips ancilla, but since ancilla is |->, this applies a phase of -1 when control is |1>. The net effect on the input qubits: the state becomes (1/4) sum_{x in {0,1}^4} (-1)^{x·s} |x>? Actually standard BV: after H on inputs, state = 1/4 sum_x |x>|->. The oracle applies U_f: |x>|-> -> (-1)^{f(x)} |x>|-> where f(x)=x·s mod 2. Since |-> is eigenstate of X with eigenvalue -1, we get phase kickback. So after oracle, state = (1/4) sum_x (-1)^{x·s} |x>|->. Then applying H on inputs again gives |s>|->|0>. So input qubits become exactly |1111>. So after final H on q[0..3], they become |1> each.

- So before measurement, state: q[0..3] = |1>, q[4] = |->, q[5] = |0>.

- Measure q[0], q[1], q[2], q[3

## isqTrain/4478

- task_id: `isqTrain/4478`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `interference`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1429`

### Prompt

What does this isQ program output when measured?

```isq
import std;

qbit q[3];

procedure main() {
    
    X(q[2]);
    
    H(q[2]);  // target different qubit
    
    ctrl SWAP(q[0], q[1], q[2]);
    
    H(q[0]);
    
    M(q[0]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: `output_prediction` for an isQ quantum program.
    *   Program:
        
    *   Qubits: `q[3]` (q0, q1, q2).
    *   Constraints: Concise, 3-8 lines for simple, 15 for complex. Use Dirac notation. Output ONLY "## Circuit Analysis" section. End with predicted probability distribution.
    *   Expected: `{|000>: 0.5, |001>: 0.5}` (Wait, the reference says this, but let's trace it).

2.  **Trace the Circuit:**
    *   Initial state: $|000\rangle$
    *   `X(q[2])` $\rightarrow |00\rangle \otimes X|0\rangle = |001\rangle$
    *   `H(q[2])` $\rightarrow |00\rangle \otimes H|1\rangle = |00\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = \frac{1}{\sqrt{2}}(|000\rangle - |001\rangle)$
    *   `ctrl swap (three-CNOT decomposition)(q[0], q[1], q[2])`: This is a controlled swap (three-CNOT decomposition) (controlled-swap operation (three-CNOT decomposition)). But wait, isQ syntax `ctrl swap (three-CNOT decomposition)(q[0], q[1], q[2])`. Wait, `ctrl @...` is standard, but `ctrl swap (three-CNOT decomposition)` usually implies one control? Or does it mean swap (three-CNOT decomposition) is controlled by something else? Wait, standard isQ `ctrl swap (three-CNOT decomposition)(q[0], q[1], q[2])` might actually mean: q[0] controls swap (three-CNOT decomposition)(q[1], q[2])? OR q[2] controls swap (three-CNOT decomposition)(q[0], q[1])?
    Let's look at `ctrl swap (three-CNOT decomposition)(q[0], q[1], q[2])`. Usually in isQ, the first qubit(s) act as control(s). If it's a standard 3-qubit gate, it's a controlled-swap operation (three-CNOT decomposition): q[0] is control, q[1] and q[2] are targets for swap (three-CNOT decomposition).
    Wait, let's re-read the syntax: `ctrl @[c1, c2] Gate(target)`. If it's written as `ctrl swap (three-CNOT decomposition)(q[0], q[1], q[2])`, it might mean q[0] is the control, q[1] and q[2] are the targets. Wait, does it say "target different qubit" in the comments? "H(q[2]); // target different qubit" - this is just a comment on H(q[2]).
    Let's assume `ctrl swap (three-CNOT decomposition)(q[0], q[1], q[2])` means: if q[0] is |1>, swap (three-CNOT decomposition) q[1] and q[2]. Since q[0] is |0>, the swap (three-CNOT decomposition) does nothing!
    State before `ctrl swap (three-CNOT decomposition)`: $\frac{1}{\sqrt{2}}(|000\rangle - |001\rangle)$. Since $q_0 = 0$, controlled-swap operation (three-CNOT decomposition) does nothing.
    *   `H(q[0])` applies to $q_0$.
    $H|0\rangle = |+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
    State becomes: $\frac{1}{\sqrt{2}} [ (\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)) \otimes \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) ] = \frac{1}{2} (|000\rangle - |001\rangle + |100\rangle - |101\rangle)$.
    *   `M(q[0])` measures $q_0$. The probabilities for the 3-qubit state are 1/4 for |000>, |001>, |100>, |101>.
    The predicted output in the prompt says `Expected measurement probabilities: {|000>: 0.5, |001>: 0.5}`. Why?
    Let's re-read the `ctrl swap (three-CNOT decomposition)` part. Maybe it's not controlled-swap (three-CNOT decomposition). Maybe it means swap (three-CNOT decomposition)(q[0], q[1]) controlled by q[2]?
    If `ctrl swap (three-CNOT decomposition)(q[0], q[1], q[2])` means controlled by q[2], let's trace:

### Reference answer

{'predicted_probs': {'000': 0.5, '001': 0.5}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.5000, P(|001>) = 0.5000.'}

## isqTrain/4496

- task_id: `isqTrain/4496`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `reversible_computing`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `2831`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;

qbit q[3];

procedure main() {
    
    X(q[2]);
    
    X(q[0]);  // replaced H with X
    
    ctrl CNOT(q[0], q[1], q[2]);
    ctrl CNOT(q[0], q[2], q[1]);
    ctrl CNOT(q[0], q[1], q[2]);
    
    M(q[0]); M(q[1]); M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the request:**
    *   **Task:** Predict probability distribution for an isQ program.
    *   **Input program:** A 3-qubit circuit with two `X` gates and three `ctrl CNOT` (Toffoli) gates, followed by measurements.
    *   **Syntax highlight:** `ctrl CNOT(q[0], q[1], q[2])` is a Toffoli gate with controls `q[0]`, `q[1]` and target `q[2]`.
    *   **Format constraints:** "## Circuit Analysis" start, step-by-step state evolution (Dirac notation), 3-15 lines, strictly ONLY the analysis text (no code blocks), end with the predicted probability distribution.

2.  **Analyze the circuit:**
    *   Initialization: `|000>`
    *   `X(q[2])`: Flips q2 to |1>. State becomes `|001>`. (Assuming q[0] is highest order bit if standard, but wait, the problem says `q[0], q[1], q[2]` in the CNOTs. Usually `q[0]` is the left-most bit. Let's trace it carefully. Let's use `|q_0 q_1 q_2>`. State is `|0 0 1>`)
    *   `X(q[0])`: Flips q0 to |1>. State becomes `|1 0 1>` (or `|101>`).
    *   `ctrl CNOT(q[0], q[1], q[2])`: Toffoli. If q0=1 and q1=1, flip q2. Current q1 is 0. So q0=1, q1=0 -> controls not all 1. State remains `|101>`.
    *   `ctrl CNOT(q[0], q[2], q[1])`: Toffoli. If q0=1 and q2=1, flip q1. Current state is `|101>` (q0=1, q2=1). Controls are satisfied! Flip q1. State becomes `|111>`.
    *   `ctrl CNOT(q[0], q[1], q[2])`: Toffoli. If q0=1 and q1=1, flip q2. Current state is `|111>`. Controls satisfied! Flip q2. State becomes `|110>`.
    *   Final state: `|110>`.
    *   Let's double check the Toffoli logic:
        *   Initial: 000
        *   X(2) -> 001
        *   X(0) -> 101
        *   Toff(0,1,2): q0=1, q1=0 -> no flip -> 101
        *   Toff(0,2,1): q0=1, q2=1 -> flip q1 -> 111
        *   Toff(0,1,2): q0=1, q1=1 -> flip q2 -> 110.
    *   Wait, is it exactly this? Let's check the permutations.
        *   Start: 101.
        *   Toffoli(0, 1, 2) does nothing because q1=0.
        *   Toffoli(0, 2, 1) flips q1 because q0=1, q2=1. State becomes 111.
        *   Toffoli(0, 1, 2) flips q2 because q0=1, q1=1. State becomes 110.
    *   predicted output in prompt says: "Expected measurement probabilities: {|110>: 1.0}". This confirms my derivation.
    *   Bit string indexing: earlier measured = higher bit. M(q[0]), M(q[1]), M(q[2]).
    *   State is `q0=1`, `q1=1`, `q2=0`.
    *   Bitstring `110` means q[0]=1, q[1]=1, q[2]=0. Yes, matches!

3.  **Draft the step-by-step reasoning:**
    *   Initial state: |000>
    *   After X(q[2]) and X(q[0]): |101>
    *   First `ctrl CNOT(q[0], q[1], q[2])` (Toffoli): Controls q[0]=1, q[1]=0. Not activated. State remains |101>.
    *   Second `ctrl CNOT(q[0], q[2], q[1])` (Toffoli): Controls q[0]=1, q[2]=1. Activated, flipping q[

### Reference answer

{'predicted_probs': {'110': 1.0}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|110>) = 1.0000.'}

## isqTrain/946

- task_id: `isqTrain/946`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `boolean_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4555`

### Prompt

Implement a quantum circuit in isQ: implements the reversible_logic pattern but with a different initial state preparation (flip q[[1]] -> q[0]).

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement reversible_logic pattern with X applied to q[1] instead of q[0], demonstrating controlled-swap operation (three-CNOT decomposition) behavior when control is |0⟩.
2. Qubits: 3 qubits (q[0], q[1], q[2]), all measured.
3. State evolution:
   - Initial: |000⟩
   - After X(q[1]): |010⟩
   - After ctrl swap_gate(q[0], q[1], q[2]): Control q[0]=|0⟩, so no swap occurs: |010⟩
4. Expected: {|010⟩: 1.0} since the controlled-swap operation (three-CNOT decomposition) leaves targets unchanged when control is |0⟩.

## isqQA/quantum_algorithms/46_math_derivation

- task_id: `isqQA/quantum_algorithms/46_math_derivation`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `math_derivation`, `algorithm`, `HHL线性方程组算法`
- source: `qa_pipeline`
- dataset_index: `670`

### Prompt

请严密推导HHL算法求解线性方程组 Ax=b 的量子态演化全过程。具体要求：给定埃尔米特矩阵A的本征谱分解形式，详细推导包含量子相位估计（QPE）、受控旋转和逆相位估计的完整数学演化步骤，并严格计算最后测量辅助比特时，系统坍缩为期望解 A^{-1}|b⟩ 的概率。

### Reference answer

<think>
推导HHL算法的核心思路是将矩阵求逆转化为特征值的倒数操作。首先，利用埃尔米特矩阵的谱分解定理，将右端项态 $|b\rangle$ 在特征基 $|u_j\rangle$ 下展开。

第一步，执行量子相位估计（QPE），通过受控酉操作 $e^{iAt}$ 将矩阵 $A$ 的特征值 $\lambda_j$ 提取到第二个寄存器中，此时系统进入特征态与对应特征值寄存器的纠缠态。

第二步，引入辅助比特并进行受控旋转。关键在于利用正弦函数关系，将特征值寄存器中的 $\lambda_j$ 映射为辅助比特概率幅中的 $1/\lambda_j$ 系数。

第三步，进行逆量子相位估计（IQPE）解纠缠，将特征值寄存器还原为 $|0\rangle$ 态，使其可以被丢弃。

最后，对辅助比特进行测量。当测量结果为 $|1\rangle$ 时，系统发生坍缩，工作寄存器的态中仅保留带有 $1/\lambda_j$ 权重的特征基叠加，即期望的 $A^{-1}|b\rangle$ 态。成功概率即为辅助比特旋转角度正弦值的平方和。
</think>

HHL算法旨在求解线性方程组 $A|x\rangle = |b\rangle$，其中 $A$ 是 $N \times N$ 的埃尔米特矩阵。假设 $A$ 具有谱分解 $A = \sum_{j=1}^{N} \lambda_j |u_j\rangle\langle u_j|$，其中 $\lambda_j$ 是特征值，$|u_j\rangle$ 是对应的本征态。给定的右端项量子态可以展开为 $|b\rangle = \sum_{j=1}^{N} \beta_j |u_j\rangle$。我们期望求解的量子态为 $|x\rangle = A^{-1}|b\rangle = \sum_{j=1}^{N} \frac{\beta_j}{\lambda_j} |u_j\rangle$。演化过程包含以下核心步骤：

**1. 初始状态与量子相位估计 (QPE)**
系统的初始状态由三个寄存器组成：存储 $|b\rangle$ 的寄存器、存储特征值的 $n$ 量子比特寄存器（初态 $|0\rangle^{\otimes n}$），以及用于受控旋转的辅助比特（初态 $|0\rangle$）：
$$|\psi_0\rangle = |b\rangle \otimes |0\rangle^{\otimes n} \otimes |0\rangle = \left(\sum_{j=1}^{N} \beta_j |u_j\rangle\right) |0\rangle^{\otimes n} |0\rangle$$
通过以矩阵 $A$ 的哈密顿量模拟 $U = e^{i A t}$ 为核心执行量子相位估计，将特征值提取到第二个寄存器中：
$$|\psi_1\rangle = \sum_{j=1}^{N} \beta_j |u_j\rangle \otimes |\lambda_j\rangle \otimes |0\rangle$$
这里 $|\lambda_j\rangle$ 是对应于特征值 $\lambda_j$ 的 $n$ 位二进制编码态。

**2. 受控旋转**
引入一个受特征值寄存器控制的旋转门 $R_y$。为了确保概率幅为实数且算法可行，需选择一个归一化常数 $C$，使得 $0 < C \le \min |\lambda_j|$。对辅助比特执行受控旋转：
$$|\lambda_j\rangle |0\rangle \rightarrow |\lambda_j\rangle \left( \sqrt{1 - \frac{C^2}{\lambda_j^2}} |0\rangle + \frac{C}{\lambda_j} |1\rangle \right)$$
该操作作用于整个系统后，状态演化为：
$$|\psi_2\rangle = \sum_{j=1}^{N} \beta_j |u_j\rangle \otimes |\lambda_j\rangle \otimes \left( \sqrt{1 - \frac{C^2}{\lambda_j^2}} |0\rangle + \frac{C}{\lambda_j} |1\rangle \right)$$

**3. 逆量子相位估计**
为了清理特征值寄存器，对其执行逆量子相位估计（$QPE^{\dagger}$）。由于本征态 $|u_j\rangle$ 和特征值寄存器 $|\lambda_j\rangle$ 是高度关联的，逆变换能够完美地将特征值寄存器解算回 $|0\rangle^{\otimes n}$：
$$|\psi_3\rangle = \sum_{j=1}^{N} \beta_j |u_j\rangle \otimes |0\rangle^{\otimes n} \otimes \left( \sqrt{1 - \frac{C^2}{\lambda_j^2}} |0\rangle + \frac{C}{\lambda_j} |1\rangle \right)$$

**4. 测量与概率计算**
最后，对辅助比特进行测量。如果测量结果为 $|1\rangle$，整个系统以相应的概率坍缩到目标子空间。根据玻恩法则，测得 $|1\rangle$ 的概率 $P(1)$ 为所有分支中辅助比特为 $|1\rangle$ 的概率幅绝对值的平方和：
$$P(1) = \sum_{j=1}^{N} \left| \beta_j \frac{C}{\lambda_j} \right|^2 = C^2 \sum_{j=1}^{N} \frac{|\beta_j|^2}{\lambda_j^2}$$
当测量结果确实为 $|1\rangle$ 时（后选择过程），剩余的量子系统坍缩并归一化为：
$$|\psi_{final}\rangle = \frac{1}{\sqrt{P(1)}} \sum_{j=1}^{N} \beta_j \frac{C}{\lambda_j} |u_j\rangle \otimes |0\rangle^{\otimes n}$$
若撇开已经还原为 $|0\rangle$ 的特征值寄存器，系统的最终状态为 $\sum_{j=1}^{N} \frac{\beta_j}{\lambda_j} |u_j\rangle$。这与期望的解 $|x\rangle = A^{-1}|b\rangle$ 在相差一个全局因子 $\frac{C}{\sqrt{P(1)}}$ 的意义上完全等价，至此完成了求解线性方程组的量子态演化与推导。

## isqTrain/848

- task_id: `isqTrain/848`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `finite_field_arithmetic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `130`

### Prompt

Write isQ code for the following quantum task: implements the finite_field_inversion pattern but with a different initial state preparation (flip q[[0]] -> q[1]).

### Chain-of-thought reasoning

## Reasoning

1. **Goal**: Implement GF(2) finite field inversion with input 1, where 1⁻¹ = 1 in GF(2).

2. **Qubits**: 2 qubits (q[0], q[1]); only q[1] is measured.

3. **State evolution**:
   - Initial: |q₀q₁⟩ = |00⟩
   - After X(q[1]): |01⟩ — prepares input value 1 on q[1]
   - After CNOT(q[0], q[1]): |01⟩ — control q[0]=|0⟩ doesn't flip target q[1]
   
4. **Measurement**: q[1] is in state |1⟩ with certainty, yielding P(|1⟩) = 1.0. This correctly computes 1⁻¹ = 1 in GF(2).

## isqTrain/2807

- task_id: `isqTrain/2807`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5610`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
oracle bool[1] g(bool a[6]) {
    bool s[] = [true, true, true, false, true, true];
    bool ba[] = s & a;
    bool res[1];
    res[0] = ba[0] != ba[1] != ba[2] != ba[3] != ba[4] != ba[5];
    return res;
}
qbit q[6], res[1];

procedure main(){
    H(res);
    H(q);
    g(q, res);
    H(q); 
    print M(q); 
}
```

### Chain-of-thought reasoning

Step 1: Analyze the oracle `g`.
The oracle `g` calculates $s \cdot a \pmod 2$, where $s = [1, 1, 1, 0, 1, 1]$ and $a$ is the 6-bit input.
The result is XORed with the target qubit `res` (since it's an oracle returning `bool res[1]`, it acts as a phase oracle or flips `res` depending on usage, but here it is `g(q, res)`, so it applies $C_{s \cdot q}$ X to `res`).
Wait, isQ handles oracles by evaluating the function $f(x) = s \cdot x$ and applying $X^{f(x)}$ to the target. Since `res` is prepared in $|-\rangle$ (H(res)), this effectively applies a phase $(-1)^{s \cdot x}$ to the state $|x\rangle$. Actually, wait, `H(res)` is applied, then `g(q, res)`, but `res` is not measured, and `q` is measured. The oracle applies a phase flip if $s \cdot x = 1$.

Step 2: Identify the algorithm.
This is Bernstein-Vazirani.
1. Initialize `q[6]` in $|0\rangle^{\otimes 6}$, `res[1]` in $|0\rangle$.
2. `H(res)` puts `res` in $|-\rangle$.
3. `H(q)` puts `q` in $|+\rangle^{\otimes 6}$.
4. `g(q, res)` applies $(-1)^{s \cdot x}$ phase to each $|x\rangle$.
5. `H(q)` transforms the state back to $|s\rangle = |111011\rangle$.
Wait, let's carefully check `s`: `s = [true, true, true, false, true, true]` corresponds to $s_0=1, s_1=1, s_2=1, s_3=0, s_4=1, s_5=1$.
The final state of `q` will be exactly $|s\rangle$.
Wait, `M(q)` measures the qubits.
The order of qubits in isQ: `q[0]` to `q[5]`.
Let's re-verify the isQ array indexing and bit ordering.
In isQ, `bool s[] = [true, true, true, false, true, true]`.
`ba[0] != ba[1] != ...` evaluates to $s_0 a_0 \oplus s_1 a_1 \oplus \dots$.
So the dot product is $s_0 a_0 \oplus s_1 a_1 \oplus s_2 a_2 \oplus s_3 a_3 \oplus s_4 a_4 \oplus s_5 a_5$.
$s = 111011_2$.
If $q$ starts in $|0\rangle^{\otimes 6}$:
H(q) $\to \frac{1}{\sqrt{2^6}} \sum |x\rangle$
g(q, res) $\to \frac{1}{\sqrt{2^6}} \sum (-1)^{s \cdot x} |x\rangle$
H(q) $\to |s\rangle$
Therefore, the state collapses to $|111011\rangle$ with probability 1.0.
Wait, the prompt says "Expected measurement probabilities: {'000000': 1.0}". Is it possible that the array indices in isQ bitstrings are reversed?
Or maybe `res[0]` is not used properly, or maybe my dot product calculation is wrong? Let's check `s`: `bool s[] = [true, true, true, false, true, true];`
Wait! Could it be that `ba[0] != ba[1] != ...` is just evaluated sequentially?
No, `!=` is XOR.
What if `bool ba[] = s & a;` is bitwise AND.
If $a = [a_0, a_1, a_2, a_3, a_4, a_5]$, $ba = [s_0 a_0, s_1 a_1, s_2 a_2, s_3 a_3, s_4 a_4, s_5 a_5]$.
And `res[0] = ba[0] != ba[1] != ba[2] != ba[3] != ba[4] != ba[5];`
This is exactly $s_0 a_

### Reference answer

{'predicted_probs': {'000000': 1.0}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/2938

- task_id: `isqTrain/2938`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_for_loop`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5416`

### Prompt

实现以下量子计算任务（使用isQ）：creates a uniform superposition over 5 qubits by applying Hadamard to each qubit.

Requirements:
- Declare `qbit q[5];` at global scope.
- Use a for loop to apply H gates.
- Measure all 5 qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Create a uniform superposition over all 32 basis states of 5 qubits.
2. **Qubits**: 5 qubits `q[0]` to `q[4]`, all measured.
3. **State evolution**: Initial state is |00000⟩. Applying H to each qubit transforms |0⟩→|+⟩=(|0⟩+|1⟩)/√2 per qubit:
   - After H(q[0]): (|0⟩+|1⟩)/√2 ⊗ |0000⟩
   - After H(q[1]): (|0⟩+|1⟩)/√2 ⊗ (|0⟩+|1⟩)/√2 ⊗ |000⟩
   - After all 5 H gates: (1/√2)^5 ⊗ Σ|x⟩ for all x ∈ {0,1}^5
4. **Expected probabilities**: Each of the 32 basis states has equal amplitude 1/√32, giving probability |1/√32|² = 1/32 ≈ 0.03125 for every outcome.

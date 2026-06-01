# ISQ training COT RAG corpus: quantum_algorithms shard 8

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4641

- task_id: `isqTrain/4641`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `936`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[2];

procedure main() {
    
    X(q[0]);

    
    
    
    

    
    
    CNOT(q[0], q[1]);
    Rz(0.392699081698724, q[1]);
    CNOT(q[0], q[1]);
    
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(0.785398163397448, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);
    
    CNOT(q[0], q[1]);
    Rz(0.392699081698724, q[1]);
    CNOT(q[0], q[1]);

    
    
    CNOT(q[0], q[1]);
    Rz(0.392699081698724, q[1]);
    CNOT(q[0], q[1]);
    
    H(q[0]); H(q[1]);
    CNOT(q[0], q[1]);
    Rz(0.785398163397448, q[1]);
    CNOT(q[0], q[1]);
    H(q[0]); H(q[1]);
    
    CNOT(q[0], q[1]);
    Rz(0.392699081698724, q[1]);
    CNOT(q[0], q[1]);

    
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

Let me analyze this isQ program step by step.

The program starts with 2 qubits q[0] and q[1], both in |0>.

1. `X(q[0])` - Apply X gate to q[0], flipping it from |0> to |1>
   State: |10>

Now let me analyze the repetitive blocks. I see a pattern that repeats twice:

Block pattern:

Let me think about what these blocks do.

The pattern `CNOT(q[0], q[1]); Rz(theta, q[1]); CNOT(q[0], q[1])` is a controlled-Rz gate. When q[0] is |0>, it does nothing to q[1]. When q[0] is |1>, it applies Rz to q[1]. Actually, more precisely:
- If q[0]=|0>: Rz is applied (the CNOTs cancel out, but wait no...)

Actually let me think again. CNOT flips the target when control is |1>. So:
- CNOT(q[0], q[1]): flips q[1] when q[0]=|1>
- Rz(theta, q[1]): applies Rz to q[1]
- CNOT(q[0], q[1]): flips q[1] back when q[0]=|1>

So for |00> → |00> → Rz|00> → |00> (no effect)
For |10> → |11> → Rz|11> → |10> (Rz applied when q[0]=|1>)
For |01> → |01> → Rz|01> → |01> (Rz applied when q[0]=|0>)
For |11> → |10> → Rz|10> → |11> (no Rz when q[0]=|1>)

Wait, this isn't a simple controlled-Rz. Let me reconsider.

The circuit `CNOT-Rz(theta, target)-CNOT` is equivalent to `CZ-Rz(theta)-CZ` which is... hmm, let me think more carefully.

Actually, the standard identity is:
`CNOT(c,t) · Rz(θ,t) · CNOT(c,t)` = `diag(1, 1, 1, e^{iθ})` which is `CRz(θ)` = controlled-Rz where Rz is applied when control is |1>.

Wait no. Let me compute this properly.

Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2})

CNOT = |0><0| ⊗ I + |1><1| ⊗ X

CNOT · (I ⊗ Rz(θ)) · CNOT

Let's compute:
For basis states:
- |00⟩: CNOT|00⟩=|00⟩, I⊗Rz|00⟩=e^{-iθ/2}|00⟩, CNOT|00⟩=|00⟩ → e^{-iθ/2}|00⟩
- |01⟩: CNOT|01⟩=|01⟩, I⊗Rz|01⟩=e^{iθ/2}|01⟩, CNOT|01⟩=|01⟩ → e^{iθ/2}|01⟩
- |10⟩: CNOT|10⟩=|11⟩, I⊗Rz|11⟩=e^{iθ/2}|11⟩, CNOT|11⟩=|10⟩ → e^{iθ/2}|10⟩
- |11⟩: CNOT|11⟩=|10⟩, I⊗Rz|10⟩=e^{-iθ/2}|10⟩, CNOT|10⟩=|11⟩ → e^{-iθ/2}|11⟩

So the result is:
- |00⟩ → e^{-iθ/2}|00⟩
- |01⟩ → e^{iθ/2}|01⟩
- |10

### Reference answer

{'predicted_probs': {'00': 0.5, '11': 0.5}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.5000, P(|11>) = 0.5000.'}

## isqTrain/3922

- task_id: `isqTrain/3922`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`
- source: `isq_train_cot`
- dataset_index: `2010`

### Prompt

这段isQ代码有bug，帮我找出并修复：

```
import std;
// Deutsch-Jozsa for 2-input constant-0 oracle
oracle f(2, 1) = [0, 0, 0, 0];
qbit q[3];

procedure main() {
    // |-> on output
    X(q[2]);
    X(q[2]);
    // Hadamard on inputs
    H(q[0]); H(q[1]);
    // Oracle
    f(q[0], q[1], q[2]);
    // Hadamard
    H(q[0]); H(q[1]);
    // Measure (should be |00> for constant)
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis

1. **The bug**: Line `X(q[2]); X(q[2]);` attempts to prepare the output qubit in the |−⟩ state, but applying X twice is the identity — q[2] stays in |0⟩, not |−⟩. The second `X(q[2])` is the wrong gate.

2. **The fix**: Replace the second `X(q[2])` with `H(q[2])`. The correct sequence to prepare |−⟩ from |0⟩ is `X(q[2]); H(q[2])`, producing H|1⟩ = |−⟩.

3. **State evolution of corrected circuit**:
   - Start: |000⟩
   - X(q[2]): |001⟩
   - H(q[2]): |0⟩|0⟩|−⟩ = (1/√2)(|000⟩ − |001⟩)
   - H(q[0])H(q[1]): |+⟩|+⟩|−⟩
   - Oracle (constant-0): identity, since f(x)=0 → |+⟩|+⟩|−⟩
   - H(q[0])H(q[1]): |00⟩|−⟩ = (1/√2)(|000⟩ − |001⟩)
   - Measurement: {|000⟩: 0.5, |001⟩: 0.5} ✓

## isqTrain/20

- task_id: `isqTrain/20`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1322`

### Prompt

Create an isQ quantum circuit that implements the qft_subcircuit pattern with modified rotation parameters (pi4_to_pi6). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

Looking at this task, I need to explain the reasoning for the given isQ program that implements a modified QFT subcircuit.

Let me analyze the circuit:

1. **Initial state**: |000⟩ (3 qubits)

2. **X(q[2])**: Prepares |100⟩ (q[2] is the third qubit, using little-endian or checking the convention)

Wait, let me check the qubit ordering. In the main function:
- q[0], q[1], q[2] are passed to qft3 as a, b, c
- X(q[2]) is applied before qft3

So the initial state is |000⟩, then X(q[2]) makes it |100⟩ if we consider q[2] as the highest bit, or |001⟩ if q[0] is the highest bit.

Looking at the predicted output: {|000>: 0.125, ...} - equal probabilities across all 8 states.

Let me trace through the circuit with the state |q[2], q[1], q[0]⟩ = |100⟩ (after X on q[2]).

Actually, let me use the convention where the state is |q[0], q[1], q[2]⟩.

After X(q[2]): |001⟩

Now qft3(q[0], q[1], q[2]) with a=q[0], b=q[1], c=q[2]:

1. H(a) = H(q[0]): |001⟩ → (|0⟩+|1⟩)|01⟩/√2 = (|001⟩+|101⟩)/√2

2. ctrl Rz(π/2, b, a) = ctrl Rz(π/2, q[1], q[0]): controlled-Rz with control q[1], target q[0]
   - When q[1]=|1⟩, apply Rz(π/2) to q[0]
   - |001⟩ is unaffected (q[1]=0)
   - |101⟩ → e^(iπ/4)|101⟩ (q[1]=0... wait, no)
   
   Wait, let me re-read: `ctrl Rz(pi/2.0, b, a)` - this means control on b, apply Rz to a.
   
   State: (|001⟩ + |101⟩)/√2
   
   For |001⟩: q[1]=0, so no rotation on q[0]
   For |101⟩: q[1]=0, so no rotation on q[0]
   
   Hmm, neither state has q[1]=1. So this gate doesn't change anything.

3. ctrl Rz(π/6, c, a) = ctrl Rz(π/6, q[2], q[0]): control on c=q[2], target a=q[0]
   - For |001⟩: q[2]=1, apply Rz(π/6) to q[0] → e^(-iπ/12)|001⟩
   - For |101⟩: q[2]=1, apply Rz(π/6) to q[0] → e^(-iπ/12)|101⟩
   
   So the state becomes e^(-iπ/12)(|001⟩ + |101⟩)/√2

4. H(b) = H(q[1]):
   |001⟩ → |0+1⟩/√2 = (|001⟩+|011⟩)/√2... wait
   
   Let me be more careful. State is e^(-iπ/12)(|001⟩ + |101⟩)/√2
   
   H on q[1]:
   - |0_1_1⟩ → (|0⟩+|1⟩)|1⟩/√2 for q[1] → |0⟩⊗(|0⟩+|1⟩)/√2⊗|1⟩
   
   Hmm, I'm getting confused with ordering. Let me use |q[0], q[1], q[2]⟩ notation consistently.
   
   State: e^(-iπ/12)(|001⟩ + |101⟩)/√2
   
   In |abc⟩ = |q[0]q[1]q[2]⟩:
   |001⟩ = |q[0]=0, q[1]=0, q[2]=1⟩
   |101⟩ = |q[0]=1, q[1]=0, q[2]=1⟩
   
   Apply H to q[1]:
   |001⟩ → |0⟩(|0⟩+|1⟩)|1⟩/√2 = (|001⟩+|011⟩)/√2
   |101⟩ → |1⟩(|0⟩+

## isqExpand/algo/15

- task_id: `isqExpand/algo/15`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `vqe`, `variational`, `nisq`, `optimization`
- source: `qa_pipeline`
- dataset_index: `5623`

### Prompt

什么是变分量子本征求解器（VQE）？为什么它特别适合近期量子设备（NISQ）？

### Chain-of-thought reasoning

## 推理
目标：解释VQE原理及其NISQ适用性。

核心：变分原理 + 混合量子-经典循环。
NISQ友好原因：浅电路、经典优化、噪声容忍。
挑战：barren plateau、局部极值、测量开销。

### Reference answer

## 变分量子本征求解器（VQE）

### 核心思想
VQE是一种**混合量子-经典算法**，利用变分原理求解量子系统的基态能量。

### 工作原理
1. **参数化量子电路（Ansatz）**：在量子计算机上准备试探态 |ψ(θ)>
2. **能量测量**：测量哈密顿量H的期望值 E(θ) = <ψ(θ)|H|ψ(θ)>
3. **经典优化**：经典计算机调整参数θ以最小化E(θ)
4. **迭代**：重复步骤1-3直到收敛

### 变分原理
对任何试探态|ψ>，有 <ψ|H|ψ> ≥ E_0（基态能量）。因此最小化期望值一定会逼近基态。

### 为什么适合NISQ
1. **浅电路**：Ansatz可以设计得很浅（少量门），减少噪声累积
2. **混合计算**：只在量子设备上做最关键的量子态准备和测量，优化在经典计算机上完成
3. **噪声容忍**：能量期望值对单个测量误差有一定容忍度
4. **灵活性**：可以根据硬件限制调整Ansatz深度

### 典型应用
- 分子基态能量计算（量子化学）
- 材料性质模拟
- 组合优化问题

### 挑战
- **Barren Plateau**：随参数空间增大，梯度可能指数衰减
- **局部最小值**：经典优化器可能陷入局部最优
- **测量开销**：需要大量重复测量来估计期望值

## isqTrain/3422

- task_id: `isqTrain/3422`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `entanglement`, `ancilla_usage`, `multi_controlled_logic`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`
- source: `isq_train_cot`
- dataset_index: `3784`

### Prompt

Implement the following in isQ: a 5-qubit repetition code with error injection on q[2] and syndrome-based correction in isQ.

Steps:
1. Encode |0> -> |00000> via CNOT fan-out
2. Inject X error on q[2]
3. Syndrome extraction using 4 ancilla qubits:
   anc[i] = q[i] XOR q[i+1] for i=0..3
4. Correction: if syndrome is 0110, error is on q[2]
   Use Toffoli gates with appropriate controls
5. Measure 5 data qubits. Expected: |00000>

Declare q[5] and anc[4]. Only measure q[0..4].

### Chain-of-thought reasoning

## Reasoning

Goal: Encode |0> into |00000>, inject an X error on q[2], detect it via syndrome extraction, and correct it to recover |00000>.
Qubits: q[5] (data) + anc[4] (syndrome), only q[0..4] measured.

1. **Encoding**: CNOT fan-out from q[0]→q[1..4] transforms |000000000> → |000000000> (all data qubits in |0>, no change since control is |0>). State: |00000⟩⊗|0000⟩.
2. **Error injection**: X(q[2]) flips q[2]: |00000⟩ → |00100⟩⊗|0000⟩.
3. **Syndrome extraction**: anc[i] = q[i] XOR q[i+1]. Neighbor pairs (0,1),(1,2),(2,3),(3,4) have parities 0,1,1,0 → syndrome 0110 on anc[0..3]. State: |00100⟩⊗|0110⟩.
4. **Correction**: Toffoli(anc[1], anc[2], q[2]) flips q[2] when anc[1]=anc[2]=1 (syndrome 0110), recovering |00000⟩⊗|0110⟩.
5. **Measurement**: Only data qubits measured — state |00000⟩ on q[0..4] yields probability 1.0 for outcome |00000⟩.

## isqTrain/4285

- task_id: `isqTrain/4285`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `5479`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[3];

procedure main() {
    // Encode a = 2 (binary 10)
    X(q[1]);
    // Add constant 1: flip the LSB
    X(q[0]);
    // Now register = 3 (binary 11)
    // Overflow detection: set flag if both bits are 1 (value >= 3)
    Toffoli(q[0], q[1], q[2]);
    // Modular correction: subtract 3 by flipping both bits
    CNOT(q[2], q[0]);
    CNOT(q[2], q[1]);
    // Measure the 2-bit result: should be 0
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]);
    M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Input: An isQ program.
    *   Task: Generate a concise circuit analysis predicting measurement outcomes.
    *   Format: Start with "## Circuit Analysis", explain operations, state evolution, final state, and probability distribution. End with the prediction.
    *   Constraint: 3-8 lines for simple, up to 15 for complex.

2.  **Analyze the isQ Program:**
    *   Initialization: `q[0], q[1], q[2]` in $|000\rangle$.
    *   `X(q[1])`: q[1] becomes 1. State is $|010\rangle$. (a=2)
    *   `X(q[0])`: q[0] becomes 1. State is $|011\rangle$. (a=3)
    *   `Toffoli(q[0], q[1], q[2])`: Since q[0] and q[1] are 1, q[2] flips to 1. State is $|111\rangle$.
    *   `CNOT(q[2], q[0])`: q[2] is 1, so q[0] flips. q[0] becomes 0. State is $|110\rangle$.
    *   `CNOT(q[2], q[1])`: q[2] is 1, so q[1] flips. q[1] becomes 0. State is $|100\rangle$.
    *   `H(q[0]); Z(q[0]); H(q[0]);`: Applies $HZH = X$ to q[0]. q[0] flips to 1. State is $|101\rangle$. Wait, let me re-evaluate.
        Let's trace carefully:
        State 0: $|000\rangle$
        `X(q[1])`: $|010\rangle$ (Binary: q2=0, q1=1, q0=0)
        `X(q[0])`: $|011\rangle$ (Binary: q2=0, q1=1, q0=1)
        `Toffoli(q[0], q[1], q[2])`: q2=1. State: $|111\rangle$ (Binary: q2=1, q1=1, q0=1)
        `CNOT(q[2], q[0])`: q2=1 -> q0 flips (1->0). State: $|110\rangle$ (Binary: q2=1, q1=1, q0=0)
        `CNOT(q[2], q[1])`: q2=1 -> q1 flips (1->0). State: $|100\rangle$ (Binary: q2=1, q1=0, q0=0)
        Wait, let's re-read the code comments.
        "// Measure the 2-bit result: should be 0"
        "HZH = X on qubit 0"
        If state before HZH is $|100\rangle$, applying X to q[0] gives $|101\rangle$.
        Let me re-read the prompt.
        Wait, the prompt says "Expected measurement probabilities: {|010>: 1.0}". Let's re-trace carefully.
        Initial: $|000\rangle$ (q2, q1, q0)
        X(q[1]): q[1] becomes 1. State $|010\rangle$.
        X(q[0]): q[0] becomes 1. State $|011\rangle$.
        Toffoli(q[0], q[1], q[2]): q[2] becomes 1. State $|111\rangle$.
        CNOT(q[2], q[0]): q[2] is 1, so q[0] flips. q[0] becomes 0. State $|110\rangle$.
        CNOT(q[2], q[1]): q[2] is 1, so q[1] flips. q[1] becomes 0. State $|100\rangle$.
        HZH = X on q[0]. Wait, HZH is X. X applied to q[0].
        Wait, $H Z H = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix} \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix} \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}

### Reference answer

{'predicted_probs': {'010': 1.0}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|010>) = 1.0000.'}

## isqExpand/algo/35

- task_id: `isqExpand/algo/35`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `qpe`, `hhl`, `phase_estimation`, `output_prediction`
- source: `isq_expansion`
- dataset_index: `5209`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit clock[2];
qbit input[1];

procedure main() {
    X(input[0]);
    H(clock[0]);
    H(clock[1]);
    ctrl Z(clock[0], input[0]);
    H(clock[1]);
    ctrl S(clock[0], clock[1]);
    H(clock[0]);
    M(clock[0]); M(clock[1]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis

1. X(input[0]): input = |1>
2. H(clock[0]); H(clock[1]): both clocks in |+>
3. ctrl@[clock[0]] Z(input[0]): Z|1> = -|1>. When clock[0]=|1>, phase -1 applied.
   clock[0] becomes (|0> - |1>)/sqrt(2) = |->.
   Clock[1] would control Z^2 = I, so no gate needed. clock[1] stays |+>.

4. Inverse QFT on 2 clock qubits:
   a. H(clock[1]): |+> -> |0>
   b. ctrl@[clock[0]] S(clock[1]): clock[1]=|0>, S|0>=|0>. No effect.
   c. H(clock[0]): |-> -> |1>

Final state: clock[0]=1, clock[1]=0.
Measurement: M(clock[0])=1, M(clock[1])=0.
Binary: 10, decimal index = 2.
This correctly identifies theta = 2/4 = 1/2, matching eigenvalue -1 = e^{i*pi}.

Probabilities: [0, 0, 1.0, 0]

### Reference answer

{'predicted_probs': {'00': 0.0, '01': 0.0, '10': 1.0, '11': 0.0}, 'explanation': 'Z|1> = -|1>, eigenvalue = e^{i*pi}, phase theta = 1/2. With 2 clock qubits, theta = 0.10 binary = 2 decimal. Step-by-step: (1) X puts input in |1>. (2) H on both clocks gives |+>|+>. (3) ctrl-Z from clock[0] on input |1>: phase -1 when clock[0]=1, so clock[0] becomes |->. Clock[1] controls Z^2 = I (not present in circuit), stays |+>. (4) Inverse QFT: H(clock[1]) maps |+> to |0>. ctrl@[clock[0]] S(clock[1]): clock[1]=|0>, S|0>=|0>, no effect. H(clock[0]) maps |-> to |1>. Final: clock[0]=1, clock[1]=0. Probs: index 10 = decimal 2 has probability 1.0.'}

## isqTrain/4459

- task_id: `isqTrain/4459`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`, `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `908`

### Prompt

Predict the output probabilities of the following quantum circuit:

```isq
import std;
qbit q[3];
procedure my_z(qbit a) {
    Z(a);
} deriving gate
procedure main() {
    // State to teleport: |1>
    X(q[0]);
    // EPR pair
    H(q[1]); CNOT(q[1], q[2]);
    // Alice's operations
    CNOT(q[0], q[1]);
    H(q[0]);
    // Bob's operations (using quantum control instead of classical)
    CNOT(q[1], q[2]);
    ctrl my_z(q[0], q[2]);
    
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal**: The user wants a step-by-step analysis of an isQ quantum program that implements a form of quantum teleportation, predicting the final probability distribution of measurement outcomes. The output must strictly follow the requested format, starting with "## Circuit Analysis", and end with the predicted probability distribution.

2.  **Analyze the isQ Code**:
    *   `qbit q[3];` (3 qubits, initialized to |000>)
    *   `X(q[0]);` -> State: |100>
    *   `H(q[1]);` -> State: |1> (q0) $\otimes$ 1/$\sqrt{2}$(|0>+|1>) (q1) $\otimes$ |0> (q2) = 1/$\sqrt{2}$(|100> + |110>)
    *   `CNOT(q[1], q[2]);` -> State: 1/$\sqrt{2}$(|100> + |111>) (Standard EPR pair between q1, q2)
    *   `CNOT(q[0], q[1]);` -> State: 1/$\sqrt{2}$(|100> + |011>)
    *   `H(q[0]);` -> State: 1/2 (|000> - |100> + |011> - |111>)  Wait, H(|0>) = |+>, H(|1>) = |-> = 1/$\sqrt{2}$(|0>-|1>). So |0> becomes |+>, |1> becomes |->. Let's trace carefully.
        *   Initial |100>: CNOT(0,1) gives |110>. H(0) gives 1/$\sqrt{2}$(|010> - |110>)
        *   Initial |111>: CNOT(0,1) gives |011>. H(0) gives 1/$\sqrt{2}$(|111> - |011>) ... Wait. CNOT(0,1) on |1>_0 |1>_1 -> |0>_0 |1>_1 because target flips. Wait, no. CNOT(0,1): control is q[0], target is q[1].
        *   State before CNOT(0,1): 1/$\sqrt{2}$(|100> + |111>)
        *   CNOT(q[0], q[1]) applies: |100> -> |110>, |111> -> |101>. Wait, no! If q[0] is |1>, q[1] flips. |100> -> |110>. |111> -> |101>.
        *   Let's re-evaluate:
            *   |100> + |111> (ignoring amplitude)
            *   CNOT(0,1): |110> + |101>
            *   H(0):
                *   H on |110>: 1/$\sqrt{2}$(|010> - |110>)
                *   H on |101>: 1/$\sqrt{2}$(|001> - |101>)
                *   Combine: 1/2(|010> - |110> + |001> - |101>)
    *   `CNOT(q[1], q[2]);`
        *   |010> -> |011>
        *   |110> -> |111>
        *   |001> -> |001>
        *   |101> -> |101>
        *   State becomes: 1/2(|011> - |111> + |001> - |101>)
    *   `ctrl my_z(q[0], q[2]);` -> This is CZ(q[0], q[2]) because my_z is Z, so controlled Z.
        *   CZ flips phase if both q0 and q2 are 1.
        *   |011> (q2=1, q0=0) -> |011>
        *   |111> (q2=1, q0=1) -> -|111>
        *   |001> (q2=1, q0=0) -> |001>
        *   |101> (q2=1, q0=1) -> -|101>
        *   State: 1/2(|011> + |111> + |001> + |101>) -> Wait. Let's check signs.
        *   Before CZ: 1/2( |001> + |011> - |101> - |111> )
        *   CZ applies Z on q[2] when q[0] is |1>. Since Z|1> = -|1>, any state with q0=1 and q

### Reference answer

{'predicted_probs': {'001': 0.25, '011': 0.25, '101': 0.25, '111': 0.25}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|001>) = 0.2500, P(|011>) = 0.2500, P(|101>) = 0.2500, P(|111>) = 0.2500.'}

## isqTrain/4840

- task_id: `isqTrain/4840`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `quantum_counting`, `interference`
- source: `isq_train_cot`
- dataset_index: `157`

### Prompt

Write an isQ program that implementing 2 iterations of Grover on 2 qubits marking |11>. Two iterations overshoot on a 2-qubit space (since 1 iteration is optimal for N=4, M=1). Observe the probability drops from 1.0.

### Chain-of-thought reasoning

Let me trace through the Grover's algorithm with 2 iterations on 2 qubits marking |11>.

**Goal**: Implement 2 Grover iterations on 2 qubits to find |11>, which overshoots the target.

**State evolution**:

1. **Initialization**: |00⟩
2. **After H⊗H**: |+⟩|+⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)

**First iteration**:

3. **Mark |11⟩** (phase flip via CZ):
   (1/2)(|00⟩ + |01⟩ + |10⟩ - |11⟩)

4. **Diffusion**: H⊗H, then X⊗X, then CZ, then X⊗X, then H⊗H
   - H⊗H on the state: (1/2)(|00⟩ + |01⟩ + |10⟩ - |11⟩) 
   - After H⊗H: transforms to (1/2)(|00⟩ - |01⟩ - |10⟩ - |11⟩)... let me be more careful.

Actually, let me think about this more carefully using the Grover operator.

The Grover operator is G = (2|ψ⟩⟨ψ| - I)O where O marks the target.

For 2 qubits with |w⟩ = |11⟩:

After H⊗H, we have |s⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)

The amplitude of |11⟩ in |s⟩ is 1/2.

After one Grover iteration:
- The marked state amplitude becomes: 2⟨s|s⟩ × 1/2 - 1/2 + ... 

Let me use the formula. For a single marked item in N=4 states:
- Initial amplitude: a = 1/√N = 1/2
- After k iterations, amplitude of marked state: sin((2k+1)θ) where sin(θ) = 1/√N = 1/2, so θ = π/6

After 1 iteration (k=1): sin(3θ) = sin(π/2) = 1 → probability = 1
After 2 iterations (k=2): sin(5θ) = sin(5π/6) = 1/2 → probability = 1/4

So after 2 iterations, the marked state has probability 1/4, and the other states each have probability (1 - 1/4)/3 = 1/4.

Wait, that gives uniform distribution again? Let me recalculate.

sin(5π/6) = sin(π - π/6) = sin(π/6) = 1/2

So the amplitude of the marked state is 1/2, and its probability is 1/4.

The unmarked states: For the other 3 states, the amplitude after 2 iterations...

Actually, let me trace through more carefully step by step.

**After H⊗H**: |ψ₀⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)

**After marking |11⟩** (CZ flips phase of |11⟩):
|ψ₁⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ - |11⟩)

**Diffusion operator D = 2|s⟩⟨s| - I**:

Applying D to |ψ₁⟩:
D|ψ₁⟩ = 2|s⟩⟨s|ψ₁⟩ - |ψ₁⟩

⟨s|ψ₁⟩ = (1/2)(1/2)(1 + 1 + 1 - 1) = (1/4)(2) = 1/2

So D|ψ₁⟩ = 2 × (1/2) |s⟩ - |ψ₁⟩ = |s⟩ - |ψ₁⟩

= (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩) - (1/2)(|00⟩ + |01⟩ + |10⟩ - |11⟩)

= (1/2)(0 + 0 + 0 + 2|11⟩)

= |11⟩

So after 1 iteration, we get exactly |11⟩. This confirms 1 iteration is optimal.

**Second iteration**:

**After marking |11⟩**:
|ψ₂⟩ = -|11⟩

**Diffusion D applied to -|11⟩**:
D(-|11⟩) = -(2|s⟩⟨s|11⟩ - |11⟩) = -(2 × 1/2 |s⟩ - |11⟩) = -(|s⟩ - |11⟩)

= -(

## isqTrain/3787

- task_id: `isqTrain/3787`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `interference`, `isq_syntax_oracle`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2559`

### Prompt

I need an isQ program to the Deutsch-Jozsa algorithm for a 2-input balanced oracle with truth table [1, 1, 0, 0]. Use the oracle keyword, prepare output in |-> state, apply Hadamard-oracle-Hadamard, measure input qubits. Result should be non-zero (balanced).

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for the Deutsch-Jozsa algorithm implementation with the balanced oracle [1, 1, 0, 0].

Let me trace through the algorithm:

1. Initial state: |000> (3 qubits: q[0], q[1] input, q[2] output)

2. X(q[2]): |001>

3. H(q[2]): |0>|-> = |0>(|0> - |1>)/√2

4. H(q[0]), H(q[1]): Apply H to both input qubits
   State becomes: |+>|+>|-> = (1/2)(|00> + |01> + |10> + |11>) ⊗ |->

5. Oracle f(q[0], q[1], q[2]):
   The oracle implements f(x) where truth table is [1, 1, 0, 0]
   f(00) = 1, f(01) = 1, f(10) = 0, f(11) = 0
   
   The oracle transforms |x>|y> → |x>|y ⊕ f(x)>
   
   Since y is in |-> state, the oracle applies a phase (-1)^f(x):
   |x>|-> → (-1)^f(x)|x>|->
   
   So:
   |00>|-> → -|00>|->
   |01>|-> → -|01>|->
   |10>|-> → +|10>|->
   |11>|-> → +|11>|->

   State becomes: (1/2)(-|00> - |01> + |10> + |11>)|->

6. H(q[0]), H(q[1]): Apply H again to input qubits
   
   H|0> = |+>, H|1> = |->
   H|+> = |0>, H|-> = |1>
   
   Let me compute:
   -H|00> = -(|0> + |1>)(|0> + |1>)/2 = -(|00> + |01> + |10> + |11>)/2
   -H|01> = -(|0> + |1>)(|0> - |1>)/2 = -(|00> - |01> + |10> - |11>)/2
   +H|10> = +(|0> - |1>)(|0> + |1>)/2 = +(|00> + |01> - |10> - |11>)/2
   +H|11> = +(|0> - |1>)(|0> - |1>)/2 = +(|00> - |01> - |10> + |11>)/2
   
   Adding these up and dividing by 2:
   Coefficient of |00>: (-1 - 1 + 1 + 1)/2 = 0
   Coefficient of |01>: (-1 + 1 + 1 - 1)/2 = 0
   Coefficient of |10>: (-1 + 1 - 1 - 1)/2 = -1
   Coefficient of |11>: (-1 - 1 - 1 + 1)/2 = -1
   
   Wait, let me redo this more carefully. The state before the final Hadamard is:
   (1/2)(-|00> - |01> + |10> + |11>) ⊗ |->
   
   Applying H⊗H to the input qubits:
   H⊗H(-|00> - |01> + |10> + |11>)/2
   
   = (-1/2) H⊗H|00> + (-1/2) H⊗H|01> + (1/2) H⊗H|10> + (1/2) H⊗H|11>
   
   H⊗H|00> = |++> = (|00> + |01> + |10> + |11>)/2
   H⊗H|01> = |+-> = (|00> - |01> + |10> - |11>)/2
   H⊗H|10> = |-+> = (|00> + |01> - |10> - |11>)/2
   H⊗H|11> = |--> = (|00> - |01> - |10> + |11>)/2
   
   So:
   (-1/2)(|00> + |01> + |10> + |11>)/2 
   + (-1/2)(|00> - |01> + |10> - |11>)/2
   + (1/2

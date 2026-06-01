# ISQ training COT RAG corpus: quantum_algorithms shard 75

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/1260

- task_id: `isqTrain/1260`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `boolean_logic`, `interference`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5783`

### Prompt

I need an isQ program to implements a variant of the deutsch_jozsa pattern using q[3] -> q[4]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

Let me analyze this Deutsch-Jozsa variant circuit.

1. Goal: Implement a 3-input Deutsch-Jozsa algorithm with an expanded qubit register (q[0] through q[3] used, with q[3] being an extra qubit that's measured but not used in the computation).

2. Qubits:
   - q[0], q[1], q[2]: input register (3 qubits)
   - q[3]: extra qubit in register (not acted upon, stays |0⟩)
   - anc[0]: ancilla for phase kickback
   - Measured: q[0], q[1], q[2], q[3] (4 qubits)

3. Step-by-step evolution:

Initial state: |0000⟩|0⟩

After X(anc[0]): |0000⟩|1⟩

After H(anc[0]): |0000⟩(|0⟩ - |1⟩)/√2

After H(q[0]), H(q[1]), H(q[2]):
(|0⟩ + |1⟩)/√2 ⊗ (|0⟩ + |1⟩)/√2 ⊗ (|0⟩ + |1⟩)/√2 ⊗ |0⟩ ⊗ (|0⟩ - |1⟩)/√2

= 1/(2√2) Σ_{x∈{0,1}^3} |x⟩|0⟩(|0⟩ - |1⟩)/√2

Oracle f(x) = (x[0] AND x[1]) XOR x[2]:
- f(000) = 0 XOR 0 = 0
- f(001) = 0 XOR 1 = 1
- f(010) = 0 XOR 0 = 0
- f(011) = 0 XOR 1 = 1
- f(100) = 0 XOR 0 = 0
- f(101) = 0 XOR 1 = 1
- f(110) = 1 XOR 0 = 1
- f(111) = 1 XOR 1 = 0

This is balanced (4 zeros, 4 ones).

After oracle f(q, anc):
1/(2√2) Σ_x (-1)^f(x) |x⟩|0⟩(|0⟩ - |1⟩)/√2

After H on q[0], q[1], q[2]:
The amplitude of |000⟩ in the input register is:
(1/2√2) Σ_x (-1)^f(x) · (1/2√2) · ⟨000|H⊗3|x⟩

For balanced function, Σ_x (-1)^f(x) = 0, so |000⟩ has zero amplitude.

The final state of input qubits is some superposition excluding |000⟩.

Actually, let me think more carefully. The expected measurements show:
- |0010⟩: 0.25
- |0110⟩: 0.25
- |1010⟩: 0.25
- |1110⟩: 0.25

In the measurement bitstring, q[0] is measured first (highest bit), q[3] last (lowest bit).

Wait, let me re-read: "earlier measured qubit = higher bit"

So measuring q[0], q[1], q[2], q[3] in that order gives bitstring b3 b2 b1 b0 where:
- b3 = q[0]
- b2 = q[1]
- b1 = q[2]
- b0 = q[3]

So |0010⟩ means q[0]=0, q[1]=0, q[2]=1, q[3]=0
|0110⟩ means q[0]=0, q[1]=1, q[2]=1, q[3]=0
|1010⟩ means q[0]=1, q[1]=0, q[2]=1, q[3]=0
|1110⟩ means q[0]=1, q[1]=1, q[2]=1, q[3]=0

So q[2] is always 1, q[3] is always 0, q[0] and q[1] vary.

Let me recalculate. After H on all input qubits and oracle, we get phase states. Let me compute H⊗3 on the phase state.

The state after oracle on q[0..2] is:
(1/2√2)[|000⟩ - |001⟩ + |010⟩ - |011⟩ + |100⟩ - |101⟩ - |110⟩ + |111⟩] ⊗ |0⟩ ⊗ (|0⟩-|1⟩)/√2

Actually, the signs

## isqTrain/1268

- task_id: `isqTrain/1268`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `data_encoding_qml`, `entanglement`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4969`

### Prompt

Implement a quantum circuit in isQ: implements the data_encoding pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

Let me analyze this quantum circuit step by step.

The circuit implements a ZZ feature map for data encoding with reversed measurement order.

**Qubits**: 2 qubits q[0] and q[1]

**Gate sequence**:
1. H(q[0]), H(q[1]) → |00⟩ → |++⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
2. Rz(1.04719755119660, q[0]) ≈ Rz(π/3, q[0])
3. Rz(0.52359877559830, q[1]) ≈ Rz(π/6, q[1])
4. CNOT(q[0], q[1])
5. Rz(0.54831135561608, q[1])
6. CNOT(q[0], q[1])
7. H(q[0]), H(q[1])
8. Rz(1.04719755119660, q[0])
9. Rz(0.52359877559830, q[1])
10. M(q[1]), M(q[0]) — reversed order!

Let me trace through the state evolution carefully.

Starting state: |00⟩

**Step 1**: H(q[0]), H(q[1]) → |++⟩ = (1/2)(|00⟩ + |01⟩ + |10⟩ + |11⟩)

**Step 2**: Rz(π/3, q[0])
Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2})
Applied to q[0]:
|00⟩ → e^{-iπ/6}|00⟩
|01⟩ → e^{-iπ/6}|01⟩
|10⟩ → e^{iπ/6}|10⟩
|11⟩ → e^{iπ/6}|11⟩

State: (1/2)(e^{-iπ/6}|00⟩ + e^{-iπ/6}|01⟩ + e^{iπ/6}|10⟩ + e^{iπ/6}|11⟩)

**Step 3**: Rz(π/6, q[1])
|00⟩ → e^{-iπ/12}|00⟩
|01⟩ → e^{iπ/12}|01⟩
|10⟩ → e^{-iπ/12}|10⟩
|11⟩ → e^{iπ/12}|11⟩

State: (1/2)(e^{-iπ/6-iπ/12}|00⟩ + e^{-iπ/6+iπ/12}|01⟩ + e^{iπ/6-iπ/12}|10⟩ + e^{iπ/6+iπ/12}|11⟩)
= (1/2)(e^{-iπ/4}|00⟩ + e^{-iπ/12}|01⟩ + e^{iπ/12}|10⟩ + e^{iπ/4}|11⟩)

**Step 4**: CNOT(q[0], q[1])
This swaps |10⟩ ↔ |11⟩:
State: (1/2)(e^{-iπ/4}|00⟩ + e^{-iπ/12}|01⟩ + e^{iπ/4}|10⟩ + e^{iπ/12}|11⟩)

**Step 5**: Rz(0.54831135561608, q[1])
φ ≈ 0.54831135561608
|00⟩ → e^{-iφ/2}|00⟩
|01⟩ → e^{iφ/2}|01⟩
|10⟩ → e^{-iφ/2}|10⟩
|11⟩ → e^{iφ/2}|11⟩

State: (1/2)(e^{-iπ/4-iφ/2}|00⟩ + e^{-iπ/12+iφ/2}|01⟩ + e^{iπ/4-iφ/2}|10⟩ + e^{iπ/12+iφ/2}|11⟩)

**Step 6**: CNOT(q[0], q[1])
Swaps |10⟩ ↔ |11⟩ again:
State: (1/2)(e^{-iπ/4-iφ/2}|00⟩ + e^{-iπ/12+iφ/2}|01⟩ + e^{iπ/12+iφ/2}|10⟩ + e^{iπ/4-iφ/2}|11⟩)

Now let's define some angles for cleanliness:
α₀ = -π/4 - φ/2
α₁ = -π/12 + φ/2
α₂ = π/12 + φ/2
α₃ = π/4 -

## isqTrain/3461

- task_id: `isqTrain/3461`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `phase_manipulation`, `ancilla_usage`, `boolean_logic`
- source: `isq_train_cot`
- dataset_index: `2510`

### Prompt

实现以下量子计算任务（使用isQ）：Deutsch-Jozsa for 2 qubits with balanced function f(x) = x[0] XOR x[1] in isQ.

Oracle: CNOT(q[0], anc) and CNOT(q[1], anc) computes XOR.
For a balanced function, the output is guaranteed non-zero.

Declare 2 input qubits and 1 ancilla. Measure input qubits.
Expected: |11> (non-zero confirms balanced).

### Chain-of-thought reasoning

## Reasoning

**Goal:** Deutsch-Jozsa on 2 qubits with balanced f(x) = x₀ XOR x₁, confirming balanced via non-zero output.

**Qubits:** 2 input qubits q[0], q[1] (measured), 1 ancilla (unmeasured).

**State evolution:**
1. Initial: |00⟩|0⟩
2. X(anc), H(anc): |00⟩|−⟩
3. H(q[0]), H(q[1]): ½(|00⟩+|01⟩+|10⟩+|11⟩)|−⟩
4. CNOT(q[0],anc): flips |−⟩→−|−⟩ when q[0]=1, giving ½(|00⟩+|01⟩−|10⟩−|11⟩)|−⟩
5. CNOT(q[1],anc): flips |−⟩→−|−⟩ when q[1]=1, giving ½(|00⟩−|

## isqTrain/3944

- task_id: `isqTrain/3944`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `5206`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```
import std;
// Phase kickback with Rz(pi/2)
qbit q[2];

procedure main() {
    // Control in superposition
    H(q[0]);
    // Target in |1> eigenstate
    X(q[1]);
    // Controlled Rz
    ctrl Rx(3.14159265358979 * 2.0 / 4.0, q[0], q[1]);
    // Detect phase on control
    H(q[0]);
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: wrong gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **The bug** is on the line applying the controlled rotation gate. The code uses `ctrl Rx(...)` instead of `ctrl Rz(...)`, which contradicts the task description and comments ("Phase kickback with Rz(pi/2)"). Rx does not apply a phase to the |1> eigenstate, so it doesn't produce the correct phase kickback.
2. **The fix** is to replace `Rx` with `Rz` on that line, resulting in: `ctrl Rz(3.14159265358979 * 2.0 / 4.0, q[0], q[1]);`.
3. **State evolution**: Starting in |00>, H(q[0]) and X(q[1]) yield 1/√2 (|01> + |11>). The controlled-Rz(π/2) gate applies a phase e^{-iπ/4} to the |11> component, resulting in 1/√2 (|01> + e^{-iπ/4}|11>). Applying H(q[0]) gives 1/2 [(1 + e^{-iπ/4})|01> + (1 - e^{-iπ/4})|11>]. The resulting measurement probabilities are ~85.36% for |01> and ~14.64% for |11>, exactly matching the predicted output.

## isqTrain/4188

- task_id: `isqTrain/4188`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_procedures`
- source: `isq_train_cot`
- dataset_index: `1774`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;
qbit q[3];

procedure main() {
    H(q[0]); H(q[1]); H(q[2]);
    CNOT(q[0], q[1]);
    Rz(2.0 * 0.500, q[1]);
    CNOT(q[0], q[1]);
    CNOT(q[1], q[2]);
    Rz(2.0 * 0.500, q[2]);
    CNOT(q[1], q[2]);
    Rx(2.0 * 1.000, q[0]);
    Rx(2.0 * 1.000, q[1]);
    Rx(2.0 * 1.000, q[2]);
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the circuit**:
    *   Initial state: $|000\rangle$ (3 qubits).
    *   Apply $H$ to $q_0, q_1, q_2$. State becomes $|+++\rangle$.
    *   Apply CNOT($q_0, q_1$): $|++\rangle \otimes |+\rangle$. Wait, CNOT on $|+\rangle|0\rangle$ is $|+\rangle|+\rangle$. CNOT on $|+\rangle|1\rangle$ is $|-\rangle|1\rangle$.
        So CNOT($q_0, q_1$) on $|+\rangle|+\rangle$ gives $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle) = \frac{1}{\sqrt{2}}(|+0\rangle + |-1\rangle) = |+\rangle|0\rangle + |-\rangle|1\rangle$.
    *   Apply $R_z(\pi/2)$ (since $2.0 \times 0.5 = 1.0$, wait, angle is 1.0 radians? No, Rz(2.0 * 0.5) = Rz(1.0). But $R_z(1.0)$ is in radians.
    Wait, let me double check the angle: $R_z(2.0 \times 0.5)$. $2.0 \times 0.5 = 1.0$. It's 1.0 radians. So $R_z(1)$ is applied to $q_1$.
    Wait, actually, isQ Rz(theta) might be $e^{-i\theta Z/2}$.
    Let's trace carefully.
    1. Initial: $|000\rangle$
    2. $H \otimes H \otimes H$: $|+++\rangle$
    3. CNOT(0, 1): $\frac{1}{2}(|00\rangle + |01\rangle + |10\rangle - |11\rangle)|+\rangle$
    4. $R_z(1, q_1)$: applies $R_z(1) = e^{-i Z/2}$ to $q_1$.
       $R_z(1)|0\rangle = e^{-i/2}|0\rangle$
       $R_z(1)|1\rangle = e^{i/2}|1\rangle$
       State: $\frac{1}{2}(e^{-i/2}|00\rangle + e^{-i/2}|01\rangle + e^{i/2}|10\rangle - e^{i/2}|11\rangle)|+\rangle$
    5. CNOT(0, 1):
       $|00\rangle \to |00\rangle$
       $|01\rangle \to |01\rangle$
       $|10\rangle \to |11\rangle$
       $|11\rangle \to |10\rangle$
       State: $\frac{1}{2}(e^{-i/2}|00\rangle + e^{-i/2}|01\rangle + e^{i/2}|11\rangle - e^{i/2}|10\rangle)|+\rangle$
       $= \frac{1}{2} ( e^{-i/2} |0\rangle(|0\rangle+|1\rangle) + e^{i/2} |1\rangle(|1\rangle-|0\rangle) ) |+\rangle$
       $= \frac{1}{\sqrt{2}} ( e^{-i/2} |0\rangle|+\rangle - e^{i/2} |1\rangle|-\rangle ) |+\rangle$
       This is equivalent to $R_z(1)$ on $q_1$ wrapped in CNOTs, which is $R_x(1)$ on $q_1$? No, CNOT(0,1) - Rz(1) - CNOT(0,1) implements $C R_z(1)$? Wait.
       Actually, $CNOT_{01} R_z(1)_1 CNOT_{01} = C R_z(1)$ where control is $q_0$, target is $q_1$.
       Wait! A controlled $R_z$ on $|+\rangle|0\rangle$ is $\frac{1}{\sqrt{2}}(|0\rangle|0\rangle + |1\rangle R_z(1)|0\rangle) = \frac{1}{\sqrt{2}}(|0\rangle|0\rangle + e^{-i/2}|1\rangle|0\rangle)$.
       But here

### Reference answer

Uniform distribution across 8 states

## isqTrain/4557

- task_id: `isqTrain/4557`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `5372`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[5];

procedure main() {
    
    X(q[0]); X(q[1]);
    
    X(q[2]); X(q[3]);
    
    ctrl ctrl X(q[0], q[2], q[4]);
    
    ctrl ctrl X(q[1], q[3], q[4]);
    
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[4]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a step-by-step analysis of an isQ quantum program, ending with the predicted probability distribution of the measurement outcomes.

2.  **Analyze the isQ code:**
    *   `qbit q[5];` -> 5 qubits initialized to $|0\rangle^{\otimes 5}$.
    *   `X(q[0]); X(q[1]);` -> Apply X gate to q0, q1. State becomes $|11000\rangle$.
    *   `X(q[2]); X(q[3]);` -> Apply X gate to q2, q3. State becomes $|11110\rangle$.
    *   `ctrl ctrl X(q[0], q[2], q[4]);` -> Toffoli gate on q0, q2 (controls) and q4 (target).
        *   Since q0 and q2 are both in $|1\rangle$, this flips q4 from $|0\rangle$ to $|1\rangle$.
        *   State becomes $|11111\rangle$.
    *   `ctrl ctrl X(q[1], q[3], q[4]);` -> Toffoli gate on q1, q3 (controls) and q4 (target).
        *   Since q1 and q3 are both in $|1\rangle$, this flips q4 from $|1\rangle$ to $|0\rangle$.
        *   State becomes $|11110\rangle$.
    *   `H(q[0]); Z(q[0]); H(q[0]);` -> Applies HZH on q0. HZH = X. So this applies X to q0.
        *   q0 was in $|1\rangle$, so it flips to $|0\rangle$.
        *   State becomes $|01110\rangle$.
    *   `M(q[4]);` -> Measures q4. The system has 5 qubits (assuming `--probs` outputs 5 qubits, as stated in "Number of qubits measured: 5").
    *   Wait, look at the state. It's exactly $|01110\rangle$.
    *   BUT The predicted output: `Expected measurement probabilities: {|00000>: 1.0}`.
    *   Let me re-read carefully. "Number of qubits measured: 5". The expected is `{|00000>: 1.0}`? Wait. If the state is $|01110\rangle$, the probability of $|00000\rangle$ is 0. Let me re-check the exact circuit and reference.
    *   Wait, is The implementation wrong, or did I misread the state?
    *   Let's re-read:
        *   Init: |00000>
        *   X(q[0]), X(q[1]) -> |11000>
        *   X(q[2]), X(q[3]) -> |11110>
        *   Toffoli(q[0], q[2], q[4]) -> q0=1, q2=1, so q4 flips. |11111>
        *   Toffoli(q[1], q[3], q[4]) -> q1=1, q3=1, so q4 flips. |11110>
        *   H(q[0]), Z(q[0]), H(q[0]) -> X(q[0]). q0=1 -> q0=0. |01110>
    *   Wait, is the predicted output `{|00000>: 1.0}` a typo in the prompt's circuit implementation, or is there a catch? Let me check the exact format of isQ. "Number of qubits measured: 5".
    *   Wait! The reference says "Expected measurement probabilities: {|00000>: 1.0}". Let me re-read the isQ program.
    *   Ah, maybe `M(q[4])` is the *only* measurement, but `--probs` mode measures all? Even then, the state is |01110>. It shouldn't be |00000>.
    *   Let's check if there's an inverse or something I missed. No.
    *   Let's check if q[0] indexing means qubit 0. Yes.
    *   Wait, maybe The implementation is literally provided in the prompt as a copy-paste error by the user?
    *   Prompt: `Expected measurement probabilities: {|00000>: 1.0}`
    *   Let me re-read the isQ code *again*.
        isq
        X(q[0]); X(q[1]);
        X(q[2]); X(q[3]);
        ctrl ctrl X(q

### Reference answer

{'predicted_probs': {'00000': 1.0}, 'explanation': 'This isQ program operates on 5 qubit(s). The measurement probability distribution is: P(|00000>) = 1.0000.'}

## isqTrain/2897

- task_id: `isqTrain/2897`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3344`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[1];
procedure main() {
    Rx(0.7853982, q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes a single qubit in the state |0>.
2. It applies an Rx gate with an angle of $\pi/4$ ($\approx 0.7853982$ radians) to the qubit.
3. The state evolves to $\cos(\pi/8)|0\rangle - i\sin(\pi/8)|1\rangle$.
4. Measurement probabilities are determined by the squared magnitudes of the state amplitudes.
5. $P(|0\rangle) = \cos^2(\pi/8) \approx 0.853553$ and $P(|1\rangle) = \sin^2(\pi/8) \approx 0.146447$.

Predicted probability distribution: {'0': 0

### Reference answer

{'predicted_probs': {'0': 0.8535533776523173, '1': 0.14644662234768277}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqQA/quantum_algorithms/117_comparison

- task_id: `isqQA/quantum_algorithms/117_comparison`
- task_type: `qa_concept`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `comparison`, `algorithm`, `振幅放大原理`
- source: `qa_pipeline`
- dataset_index: `5422`

### Prompt

请对比分析量子振幅放大算法与经典搜索方法以及标准Grover算法在原理、优缺点和适用场景上的异同。假设我们需要在一个包含4个元素的数据库中寻找唯一的目标项，请使用isQ语言编写相应的振幅放大代码，并说明其迭代次数的设定依据。

### Reference answer

<thought>
数学推导与代码逻辑推理：
1. 对比分析：
- 经典搜索方法：如暴力遍历，时间复杂度为O(N)。对于无结构数据，没有任何先验信息，必须逐个检查。优点是实现简单，不依赖特殊硬件；缺点是面对指数级状态空间时极度耗时。
- 标准Grover算法：可以看作是振幅放大算法在无结构数据库搜索这一特定场景下的应用。它假设初始状态是均匀叠加态。时间复杂度为O(√N)，实现了平方级加速。
- 广义振幅放大：不局限于均匀叠加态，它可以应用于任何能够通过酉算子A制备的初始态，只要我们能构造标记好态的Oracle。适用场景更广，例如用于加速经典启发式算法、寻找极值等。

2. 迭代次数推导：
假设数据库有4个元素，需要2个量子比特表示（N=4）。目标项数量M=1。
初始振幅为 $a = \sin(\theta) = \sqrt{M/N} = \sqrt{1/4} = 1/2$，所以 $\theta = \pi/6$。
经过k次Grover迭代后，目标态的振幅为 $\sin((2k+1)\theta)$。
要使概率最大化，需要 $(2k+1)\theta \approx \pi/2$。
带入 $\theta = \pi/6$，得到 $(2k+1)\pi/6 = \pi/2$，解得 $2k+1 = 3$，即 $k=1$。
因此，只需要1次迭代即可达到接近100%的测量概率。

3. isQ代码编写：
- 全局声明 `qbit q[2];`
- Oracle：假设我们要搜索的目标态是 `|11>`。将 `|11>` 的相位翻转可以通过直接作用 `CZ(q[0], q[1])` 实现。
- 扩散算子：作用于均匀叠加态的扩散算子为 $H^{\otimes 2} (2|00\rangle\langle00| - I) H^{\otimes 2}$。
代码表现为：对所有比特作用H门，然后对所有比特作用X门，接着执行 `CZ(q[0], q[1])`，再作用X门和H门恢复。
</thought>

量子振幅放大算法是量子计算中极其重要的基元，它在不同情境下与经典搜索及标准Grover算法有着显著的差异与联系：

1. **原理与适用场景对比**
- **经典搜索算法**：依赖于线性时间的逐一排查（$O(N)$）。它的优点在于普适性极强，对数据的存储结构没有任何特殊要求。然而，在面对大规模数据时，这种线性增长的时间消耗是不可接受的。
- **标准Grover算法**：本质上是振幅放大算法的一个特例。它专门针对“初始态为均匀叠加态”的无结构数据库搜索问题。通过反复进行Oracle查询和相位反转，它能将找到目标项的复杂度降低到$O(\sqrt{N})$。缺点是它要求必须能够将问题映射为量子黑盒（Oracle）的相位翻转操作。
- **广义振幅放大**：它的适用场景远超无结构搜索。只要我们有一个能够制备某概率分布的酉算子$A$（初始状态不要求绝对均匀），且知道如何标记目标子空间，就可以使用振幅放大来提高“好态”的测量概率。这使得它可以用于加速诸如蒙特卡洛模拟、优化问题中的候选解生成概率等。

2. **迭代次数的设定依据**
在包含4个元素的数据库中寻找1个目标项时，状态数为 $N=4$，目标数 $M=1$。
根据数学推导，量子态在二维子空间（由目标子空间和非目标子空间张成）中旋转的角度 $\theta$ 满足 $\sin\theta = \sqrt{M/N} = 1/2$，即 $\theta = \pi/6$。
每次振幅放大迭代都会将系统状态向目标态旋转 $2\theta$。为了获得最大的测量概率，我们需要将其旋转至接近 $\pi/2$。
公式 $ (2k+1)\theta \approx \pi/2 $ 代入 $\theta = \pi/6$，解得最优迭代次数 $k=1$。即只需1次量子迭代即可找到目标。

3. **isQ语言代码实现**
以下是寻找包含4个元素数据库中目标态 `|11>` 的isQ代码：

```isQ
import std;

qbit q[2];

// 定义标记目标态 |11> 的Oracle
procedure oracle() {
    // CZ门在计算基下等价于将 |11> 态的相位翻转 pi
    CZ(q[0], q[1]);
}

// 定义扩散算子
procedure diffusion() {
    for i in 0:2 {
        H(q[i]);
        X(q[i]);
    }
    // 对 |00> 态进行相位翻转
    CZ(q[0], q[1]);
    for i in 0:2 {
        X(q[i]);
        H(q[i]);
    }
}

procedure main() {
    // 步骤1：制备均匀叠加态
    for i in 0:2 {
        H(q[i]);
    }
    
    // 步骤2：执行1次振幅放大迭代
    oracle();
    diffusion();
    
    // 步骤3：测量量子比特，由于进行了完美旋转，输出将以100%概率为 11
    for i in 0:2 {
        M(q[i]);
    }
}
```

## isqTrain/929

- task_id: `isqTrain/929`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_ctrl_nctrl`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3167`

### Prompt

用isQ实现implements the boolean_synthesis pattern. Include explicit identity operations in the circuit (X-X pair before M(q[5])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Compute MAJ(a,b,c) for a=1, b=1, c=0 using boolean synthesis with an explicit X-X identity pair before measurement.
2. **Qubits**: 6 qubits declared; only q[5] is measured.
3. **State evolution**:
   - Initial: |000000⟩
   - X(q[0]), X(q[1]): |011000⟩ (set inputs a=1, b=1, c=0)
   - ctrl ctrl X(q[0], q[1], q[3]): q[3] = a∧b = 1 → |011010⟩
   - ctrl ctrl X(q[0], q[2], q[4]): q[4] = a∧c = 0 → |011010⟩
   - CNOT(q[3], q[5]): q[5] = 1 → |011011⟩
   - CNOT(q[4], q[5]): q[5] = 1⊕0 = 1 → |011011⟩
   - ctrl ctrl X(q[1], q[2], q[5]): q[5] = 1⊕(b∧c) = 1⊕0 = 1 → |011011⟩
   - X(q[5]): flips q[5] to 0 → |011010⟩
   - X(q[5]): flips back to 1 → |011011⟩ (identity pair cancels)
4. **Result**: The X-X pair is a no-op (gate cancellation), so q[5] remains |1⟩ with probability 1.0.

## isqTrain/801

- task_id: `isqTrain/801`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2481`

### Prompt

请用isQ语言编写一个量子电路：implements a variant of the quantum_multiplier pattern using q[5] -> q[6]. The circuit should use an expanded qubit register compared to the base version.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement a quantum multiplier computing 1 × 2 = 2 using an expanded 7-qubit register.
2. Qubits: q[0] holds multiplier a=1, q[1]=b0=0, q[2]=b1=1 form multiplicand b=2, q[3-5] are product/ancilla bits; q[3], q[4], q[5] are measured.
3. Initial state: |0000000⟩. After X(q[0]) and X(q[2]): |1010000⟩ (a=1 at q[0], b=10 at q[2:1]).
4. Toffoli(q[0], q[1], q[3]): both controls (q[0]=1, q[1]=0) not both |1⟩ → q[3] stays |0⟩ (p0 = 1 AND 0 = 0).
5. Toffoli(q[0], q[2], q[4]): both controls (q[0]=1, q[2]=1) are |1⟩ → q[4] flips to |1⟩ (p1 = 1 AND 1 = 1).
6. Final state: |1010100⟩ — product bits q[4]=1, q[3]=0 represent 10₂ = 2.
7. Measuring q[3]=0, q[4]=1, q[5]=0 yields bitstring 010 (q[3] is highest bit), so probability {|010⟩: 1.0}.

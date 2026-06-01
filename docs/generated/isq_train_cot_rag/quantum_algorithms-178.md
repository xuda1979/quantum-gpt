# ISQ training COT RAG corpus: quantum_algorithms shard 178

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2782

- task_id: `isqTrain/2782`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_arrays`, `isq_syntax_classical_vars`, `isq_syntax_multi_register`, `isq_syntax_oracle`, `isq_syntax_print`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1858`

### Prompt

修复以下isQ程序中的错误：

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
    X(res);
    H(res);
    H(q);
    g(q, res);
    // H(q); // BUG: missing Hadamard 
    print M(q); // should print 55 (=0x110111)
}
```

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug identification**: The second `H(q)` gate on line 24 is commented out (`// H(q);`). In the Bernstein-Vazirani algorithm, this final Hadamard transform is essential to convert the phase-encoded secret string back into the computational basis for measurement.

2. **Fix**: Uncomment `H(q);` to restore the missing Hadamard transform after the oracle call.

3. **State evolution of corrected circuit**:
   - Start: |000000>|0>
   - X(res): |000000>|1>
   - H(res): |000000> ⊗ |−>
   - H(q): |++++++> ⊗ |−>
   - g(q, res): Phase oracle encodes s=110111: Σ_x (−1)^(s·x)|x> ⊗ |−>
   - H(q): Converts from Hadamard basis back to computational basis, yielding |110111> ⊗ |−>
   - M(q) deterministically measures 55 (binary 110111)

## isqExpand/algo/79

- task_id: `isqExpand/algo/79`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `grover`, `amplitude_amplification`, `oracle`, `multi_controlled_logic`
- source: `isq_expansion`
- dataset_index: `5547`

### Prompt

Code this in isQ: implements Grover's algorithm on 3 qubits to search for the state |000>. Apply one Grover iteration (oracle + diffusion). The oracle must flip the phase of |000> only. Since |000> is the all-zero state, the oracle needs to apply X gates to all qubits before and after the multi-controlled Z to effectively condition on all qubits being 0. Use ctrl @[q[0], q[1]] Z(q[2]) for the multi-controlled Z.

### Chain-of-thought reasoning

## 推理
目标：3比特Grover搜索|000>态。

### Oracle设计
|000>意味着q[0]=0, q[1]=0, q[2]=0。CCZ门在所有控制位为1时才触发，所以需要先对所有量子位施加X门将条件翻转：
- X(q[0]); X(q[1]); X(q[2]); — 将|000>映射为|111>
- ctrl @[q[0], q[1]] Z(q[2]); — 对|111>施加相位翻转
- X(q[0]); X(q[1]); X(q[2]); — 恢复

### Diffusion算子 (2|s><s|-I)
H→X→CCZ→X→H 对所有3个量子位。

### 概率计算
N=8, M=1: theta = arcsin(sqrt(1/8)) ≈ 0.3614
1次迭代后: P(|000>) = sin^2(3*theta) = 25/32 = 0.78125
P(其他每个) = (1 - 25/32)/7 = 1/32 = 0.03125

预期概率: index 0 (|000>) = 0.78125, 其余 = 0.03125

## isqTrain/2891

- task_id: `isqTrain/2891`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `basic`
- concept_tags: `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2783`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;
qbit q[1];
procedure main() {
    Ry(1.5707963, q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes a single qubit in the ground state |0>.
2. It applies the rotation gate Ry(π/2) to the qubit.
3. The Ry(π/2) gate transforms the state from |0> to an equal superposition: (1/√2)|0> + (1/√2)|1>.
4. Measurement in the computational basis collapses this superposition, yielding a 50% chance for each outcome.

[0.5, 0.5]

### Reference answer

{'predicted_probs': {'0': 0.5000000133974483, '1': 0.4999999866025518}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/1151

- task_id: `isqTrain/1151`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `data_encoding_qml`, `phase_manipulation`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4124`

### Prompt

I need an isQ program to implements the data_encoding pattern with modified rotation parameters (num_pi4_to_pi6). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Data encoding pattern with modified rotation parameters (num_pi4_to_pi6).
    *   predicted outputs: Probabilities for |00>, |01>, |10>, |11>.
    *   Probabilities provided: P(|00>) ≈ 0.4665, P(|01>) ≈ 0.4665, P(|10>) ≈ 0.0335, P(|11>) ≈ 0.0335.
    *   Reference code provides a template: H(q[0]), H(q[1]), Rz(x0, q[0]), Rz(x1, q[1]), H(q[0]), H(q[1]), M(q[0]), M(q[1]).
    *   I need to find the new angles x0 and x1 corresponding to "num_pi4_to_pi6" that give these probabilities.
    *   I need to output ONLY the "## Reasoning" section following specific constraints (concise, 3-8 lines, Dirac notation).

2.  **Determine the parameters:**
    *   Original code has x0 = 0.5236 (pi/6) and x1 = 1.5708 (pi/2).
    *   Wait, the task says "modified rotation parameters (num_pi4_to_pi6)". Let's look at the probabilities.
    *   Let's check the math for the ZZ feature map or similar.
    *   Circuit structure: H, Rz(x0), Rz(x1), H.
    *   State after first H on |00>: (|0> + |1>)/sqrt(2) (q[0]) * (|0> + |1>)/sqrt(2) (q[1]) = (|00> + |01> + |10> + |11>)/2.
    *   Apply Rz(x0) on q[0]: Phase on |1> of q[0]. State becomes (|00> + |01> + exp(i*x0)|10> + exp(i*x0)|11>)/2.
    *   Apply Rz(x1) on q[1]: Phase on |1> of q[1]. State becomes (|00> + exp(i*x1)|01> + exp(i*x0)|10> + exp(i*(x0+x1))|11>)/2.
    *   Apply H on both: Transforms |0> -> (|0>+|1>)/sqrt(2) and |1> -> (|0>-|1>)/sqrt(2).
    *   Final state for q[0]: (1/2) * [ (|0>+|1>) + exp(i*x0)(|0>-|1>) ] = 1/2 * [ (1+exp(i*x0))|0> + (1-exp(i*x0))|1> ].
    *   P(|0>_0) = |1+exp(ix0)|^2 / 4 = (1 + cos(x0)) / 2. P(|1>_0) = (1 - cos(x0)) / 2.
    *   P(|0>_1) = (1 + cos(x1)) / 2. P(|1>_1) = (1 - cos(x1)) / 2.
    *   Wait, the final state is a product state because Rz on q[0] and Rz on q[1] don't entangle them!
    *   Let's check the predicted output:
        P(00) ≈ 0.4665
        P(01) ≈ 0.4665
        P(10) ≈ 0.0335
        P(11) ≈ 0.0335
    *   Since P(00) ≈ P(01) and P(10) ≈ P(11), the state of q[1] is roughly |0> or |+> (actually balanced between |0> and |1>). Thus P(|0>_1) ≈ 0.5, so (1 + cos(x1))/2 = 0.5 => cos(x1) = 0 => x1 = pi/2.
    *   For q[0], P(|0>_0) = 0.4665 + 0.4665 = 0.933. P(|1>_0) = 0.0335 + 0.0335 = 0.067.
    *   So (1 + cos(x0))/2 = 0.933 => cos(x0) = 0.8660254 => x0 = pi/6.
    *   Wait,

## isqTrain/1424

- task_id: `isqTrain/1424`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_ctrl_nctrl`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4478`

### Prompt

请用isQ语言编写一个量子电路：Apply the 3-qubit Quantum Fourier Transform to the input state |111> and measure all qubits.

### Chain-of-thought reasoning

Let me trace through this circuit step by step.

Initial state: |000>

After X(q[0]), X(q[1]), X(q[2]): |111>

Now apply QFT on 3 qubits. The QFT on 3 qubits maps |x₁x₂x₃⟩ to a uniform superposition over all 8 states (since QFT of |7⟩ = |111⟩ gives a uniform superposition).

Let me trace through the gates:

The QFT circuit operates on qubits in a specific order. Let me track the state.

Starting: |111> (qubits q[2], q[1], q[0] from MSB to LSB)

Step 1: H(q[2])
H on q[2] where q[2] is |1⟩:
|1⟩ → (|0⟩ - |1⟩)/√2
State: (|011⟩ - |111⟩)/√2

Step 2: ctrl S(q[1], q[2]) — controlled-S with q[1] as control, q[2] as target
S = diag(1, i), applies i phase to |1⟩ of target when control is |1⟩
When q[1]=|1⟩ and q[2]=|1⟩, multiply by i.
State: (|011⟩ - i|111⟩)/√2

Step 3: ctrl T(q[0], q[2]) — controlled-T with q[0] as control, q[2] as target
T = diag(1, e^(iπ/4)), applies e^(iπ/4) phase to |1⟩ of target when control is |1⟩
When q[0]=|1⟩ and q[2]=|1⟩, multiply by e^(iπ/4).
State: (|011⟩ - i·e^(iπ/4)|111⟩)/√2

Step 4: H(q[1])
H on q[1] where q[1] is |1⟩ in both terms:
|011⟩ → (|001⟩ + |011⟩)/√2
|111⟩ → (|101⟩ + |111⟩)/√2
State: (|001⟩ + |011⟩ - i·e^(iπ/4)(|101⟩ + |111⟩))/2

Step 5: ctrl S(q[0], q[1]) — controlled-S with q[0] as control, q[1] as target
When q[0]=|1⟩ and q[1]=|1⟩, multiply by i.
Affects |011⟩ and |111⟩:
State: (|001⟩ + i|011⟩ - i·e^(iπ/4)|101⟩ - i·e^(iπ/4)·i|111⟩)/2
     = (|001⟩ + i|011⟩ - i·e^(iπ/4)|101⟩ + e^(iπ/4)|111⟩)/2

Step 6: H(q[0])
H on q[0] where q[0] is |1⟩:
For each basis state, |1xy⟩ → (|0xy⟩ - |1xy⟩)/√2

Let me be more careful. After step 5, state is:
(|001⟩ + i|011⟩ - i·e^(iπ/4)|101⟩ + e^(iπ/4)|111⟩)/2

Applying H on q[0]:
|001⟩ → (|001⟩ + |101⟩)/√2
|011⟩ → (|011⟩ + |111⟩)/√2
|101⟩ → (|001⟩ - |101⟩)/√2
|111⟩ → (|011⟩ - |111⟩)/√2

State:
(|001⟩ + |101⟩ + i(|011⟩ + |111⟩) - i·e^(iπ/4)(|001⟩ - |101⟩) + e^(iπ/4)(|011⟩ - |111⟩))/(2√2)

Collecting terms:
|001⟩: (1 - i·e^(iπ/4))/(2√2)
|101⟩: (1 + i·e^(iπ/4))/(2√2)
|011⟩: (i + e^(iπ/4))/(2√2)
|111⟩: (i - e^(iπ/4))/(2√2)

Step 7: swap (three-CNOT decomposition)(q[0], q[2])
This swaps the first and third qubits:
|001⟩ → |100⟩
|101⟩ → |101⟩
|011⟩ → |110⟩
|111⟩ → |111⟩

Also the other 4 states |000⟩, |010

## isqTrain/731

- task_id: `isqTrain/731`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2142`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[6];

procedure main() {
    // Encode a=3 (binary 11) and b=1 (binary 01)
    X(q[0]);
    X(q[1]);
    X(q[2]);
    // Bit 0: carry0 = a0 AND b0
    Toffoli(q[0], q[2], q[4]);
    // Bit 0: sum0 = a0 XOR b0 -> stored in q[2]
    CNOT(q[0], q[2]);
    // Bit 1: carry_out accumulates AND pairs
    Toffoli(q[1], q[3], q[5]);
    Toffoli(q[1], q[4], q[5]);
    Toffoli(q[3], q[4], q[5]);
    // Bit 1: sum1 = a1 XOR b1 XOR carry0
    CNOT(q[1], q[3]);
    CNOT(q[4], q[3]);
    // Measure sum0, sum1, carry_out
    M(q[2]);
    M(q[3]);
    M(q[5]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Analyze an isQ program, predict measurement probability distribution, explain reasoning.
    *   **Format:** 3-8 lines for simple, up to 15 for complex. Output ONLY the "## Circuit Analysis" section.
    *   **Syntax rules:** Provided (standard quantum gates like X, CNOT, Toffoli, M).
    *   **Target Circuit:** A 2-bit adder circuit (though not perfectly standard in its structure, let's trace exactly what it does).
    *   **Input State:** |000000>
    *   **Gates:**
        *   `X(q[0])`, `X(q[1])`, `X(q[2])`
        *   `Toffoli(q[0], q[2], q[4])`
        *   `CNOT(q[0], q[2])`
        *   `Toffoli(q[1], q[3], q[5])`
        *   `Toffoli(q[1], q[4], q[5])`
        *   `Toffoli(q[3], q[4], q[5])`
        *   `CNOT(q[1], q[3])`
        *   `CNOT(q[4], q[3])`
        *   `M(q[2])`, `M(q[3])`, `M(q[5])`

2.  **Trace the State Evolution:**
    *   Initial: `q[0..5]` = |000000>. Let's denote the state as `a1 a0 b1 b0 c1 c0` -> `q[0] q[1] q[2] q[3] q[4] q[5]`
    *   `X(q[0])`, `X(q[1])`, `X(q[2])`:
        *   `q[0]` = 1 (a0 = 1)
        *   `q[1]` = 1 (a1 = 1)
        *   `q[2]` = 1 (b0 = 1)
        *   State: |111000> (where `q[3]`=0, `q[4]`=0, `q[5]`=0)
    *   `Toffoli(q[0], q[2], q[4])`:
        *   If `q[0]`=1 and `q[2]`=1, flip `q[4]`.
        *   `q[0]`=1, `q[2]`=1 -> `q[4]` becomes 1.
        *   State: |111010> (`q[4]` is 1, this represents carry0 = a0 & b0 = 1)
    *   `CNOT(q[0], q[2])`:
        *   If `q[0]`=1, flip `q[2]`.
        *   `q[0]`=1, `q[2]`=1 -> `q[2]` becomes 0.
        *   State: |110010> (`q[2]` is 0, sum0 = a0 ^ b0 = 0)
    *   `Toffoli(q[1], q[3], q[5])`:
        *   If `q[1]`=1 and `q[3]`=1, flip `q[5]`.
        *   `q[1]`=1, `q[3]`=0 -> `q[5]` remains 0.
        *   State: |110010>
    *   `Toffoli(q[1], q[4], q[5])`:
        *   If `q[1]`=1 and `q[4]`=1, flip `q[5]`.
        *   `q[1]`=1, `q[4]`=1 -> `q[5]` becomes 1.
        *   State: |110011>
    *   `Toffoli(q[3], q[4], q[5])`:
        *   If `q[3]`=1 and `q[4]`=1, flip `q[5]`.
        *   `q[3]`=0, `q[4]`=1 -> `q[5]` remains 1.
        *   State: |110011>
    *   `CNOT(q[1], q[3])`:
        *   If `q[1]`=1, flip `q[3]`.
        *   `q[1]`=1, `q[3]`=0 -> `q[3

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqEval/277. Dimension: predict probabilities for reference circuit.'}

## isqTrain/1404

- task_id: `isqTrain/1404`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `interference`, `isq_syntax_multi_register`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2727`

### Prompt

Implement the following in isQ: the Bernstein-Vazirani algorithm to find the secret string s = 00101 (MSB first). Use 5 input qubits and 1 ancilla.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement Bernstein-Vazirani to find secret string s = 00101 via phase oracle f(x) = s·x mod 2.
2. **Qubits**: 5 input qubits (q[0]-q[4]) + 1 ancilla (anc[0]); only input qubits are measured.
3. **State evolution**:
   - Initial state: |00000⟩|0⟩ → X on ancilla → |00000⟩|1⟩ → H on ancilla → |00000⟩|−⟩
   - H on all 5 inputs: (1/√32) Σ_x |x⟩|−⟩ = |+++++⟩|−⟩
   - Oracle: CNOT(q[2], anc[0]) and CNOT(q[4], anc[0]) apply phase kickback, adding (−1)^(s·x) where s = 00101
   - After oracle: (1/√32) Σ_x (−1)^(s·x) |x⟩|−⟩
   - H on all 5 inputs: The Hadamard transform converts the phase-encoded string to computational basis → |00101⟩|−⟩
4. **Expected probabilities**: Measurement yields |00101⟩ with probability 1.0, as H⊗5 exactly recovers s from the phase encoding.

## isqTrain/2877

- task_id: `isqTrain/2877`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `isq_syntax_multi_register`, `measurement_order`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `3646`

### Prompt

This isQ program doesn't produce the correct output. Can you debug it?

Code:
```isq
import std;
qbit q[2];
// phase kickback with controlled-T
procedure main() {
    // X(q[1]); // BUG: missing initialization
    H(q[0]);
    ctrl T(q[0], q[1]);
    H(q[0]);
    M(q[0]);
    M(q[1]);
}

```

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: The `X(q[1])` gate is commented out on line 6, so `q[1]` initializes to |0⟩ instead of |1⟩. This prevents phase kickback — when `q[1]` is |0⟩, the controlled-T gate applies `T|0⟩ = |0⟩` (no phase acquired), so no phase is kicked back to `q[0]`.

2. **Fix**: Uncomment `X(q[1])` so `q[1]` starts in |1⟩. The controlled-T then applies `T|1⟩ = e^{iπ/4}|1⟩`, kicking a phase of e^{iπ/4} back onto the control qubit `q[0]`.

3. **Corrected state evolution**:
   - Start: |00⟩ → `X(q[1])` → |01⟩
   - `H(q[0])` → (|01⟩ + |11⟩)/√2
   - `ctrl T`: T|1⟩ = e^{iπ/4}|1⟩, so the |11⟩ component picks up e^{iπ/4} → (|01⟩ + e^{iπ/4}|11⟩)/√2
   - `H(q[0])` → ((1+e^{iπ/4})|01⟩ + (1−e^{iπ/4})|11⟩)/2
   - P(|01⟩) = |1+e^{iπ/4}|²/4 = (2+√2)/4 ≈ 0.8536, P(|11⟩) = (2−√2)/4 ≈ 0.1464 ✓

## isqTrain/4092

- task_id: `isqTrain/4092`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `superposition`, `interference`, `phase_manipulation`, `multi_controlled_logic`, `isq_syntax_deriving_gate`, `isq_syntax_for_loop`
- source: `isq_train_cot`
- dataset_index: `1416`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[4];

unit grover_oracle(qbit q[4]) {
    X(q[0]);
    ctrl<2> CZ(q[0], q[1], q[2], q[3]);
    X(q[0]);
} deriving gate

unit grover_diffusion(qbit q[4]) {
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    X(q[3]);
    ctrl<2> CZ(q[0], q[1], q[2], q[3]);
    X(q[0]);
    X(q[1]);
    X(q[2]);
    X(q[3]);
    H(q[0]);
    H(q[1]);
    H(q[2]);
    H(q[3]);
} deriving gate

procedure main() {
    H(q[0]); H(q[1]); H(q[2]); H(q[3]);
    for i in 0:3 {
        grover_oracle(q);
        grover_diffusion(q);
    }
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

This is a Grover's algorithm with 4 qubits. Let me analyze it step by step.

1. Initial state: |0000⟩
2. After Hadamard on all qubits: |ψ⟩ = (1/4) Σ|x⟩ (uniform superposition over 16 states)

3. The oracle: The oracle marks a target state. Looking at the code:
   - X(q[0]) flips qubit 0
   - ctrl<2> CZ(q[0], q[1], q[2], q[3]) applies CZ when q[0], q[1], q[2] are all |1⟩, targeting q[3]
   - X(q[0]) flips qubit 0 back

The X gates on q[0] before and after the multi-controlled Z effectively search for the state where q[0]=0, q[1]=1, q[2]=1. The CZ flips the phase of q[3] when controls are satisfied.

So the oracle marks the state |0111⟩ (q[0]=0, q[1]=1, q[2]=1, q[3]=1).

Wait, let me reconsider. The multi-controlled CZ with ctrl<2> means 2 controls. Looking at CZ(q[0], q[1], q[2], q[3]) - this might mean q[0] and q[1] are controls, q[2] is... hmm, this is a bit ambiguous.

Actually, in isQ, `ctrl<2> CZ(q[0], q[1], q[2], q[3])` likely means a CZ with 2 additional controls, making it a 4-qubit gate. The CZ typically has one control and one target. With ctrl<2>, it adds 2 more controls, so total 3 controls and 1 target.

Wait, let me think again. CZ(control, target) is a 2-qubit gate. ctrl<2> adds 2 control qubits, making it a 4-qubit gate: 3 controls and 1 target.

So `ctrl<2> CZ(q[0], q[1], q[2], q[3])` means:
- q[0], q[1] are the additional controls (from ctrl<2>)
- q[2] is the original control of CZ
- q[3] is the target

So it applies Z to q[3] when q[0]=q[1]=q[2]=|1⟩.

With the X gates on q[0] before and after, the oracle marks states where q[0]=0 (since X flips it), and q[1]=q[2]=|1⟩.

The marked state is |011⟩ for qubits 0,1,2, and the Z applies to q[3]. But this means both |0110⟩ and |0111⟩ could be affected... no wait, the Z is applied to q[3] conditional on the controls. When the controls are met, Z is applied regardless of q[3]'s state.

Actually, the multi-controlled Z applies a phase flip to |0111⟩ and |0110⟩? No... let me think more carefully.

The gate applies Z to q[3] when controls are satisfied. Z|0⟩ = |0⟩ and Z|1⟩ = -|1⟩. So the phase flip only happens when q[3]=|1⟩ AND all controls are satisfied.

So the marked state is: q[0]=0 (after X), q[1]=1, q[2]=1, q[3]=1 → |0111⟩.

4. For 4 qubits, N = 16, optimal iterations ≈ π/4 × √16 ≈ 3.14 ≈ 3

The circuit runs 3 iterations (for i in 0:3, which is 0, 1, 2 = 3 iterations).

After 3 iterations of Grover with N=16 and 1 marked state, the amplitude of |0111⟩ should be very close to 1.

The exact amplitude after k iterations:
sin²((2k+1)θ) where sin(θ) = 1/√16 = 1/4, θ = arcsin(1/4) ≈ 0.2527

After 3 iterations: sin²(7 × 0.2527) = sin²(1.769) ≈ sin²(1.769)

sin(1.769) ≈ 0.980
sin²(1.769) ≈ 0.960

So approximately 96% probability of measuring |0111⟩.

Actually, let me recalculate more carefully.

θ = arcs

### Reference answer

Deterministic output: state |0111> with probability ~0.96

## isqTrain/4133

- task_id: `isqTrain/4133`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `5616`

### Prompt

这个量子电路运行后，各个测量结果的概率是多少？

```isq
import std;
qbit q[4];

procedure main() {
    X(q[3]);
    H(q[0]); H(q[1]); H(q[2]);
    ctrl Rz(2.0 * 3.14159265358979 * 4.0 / 8.0 * 1.0, q[0], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 4.0 / 8.0 * 2.0, q[1], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 4.0 / 8.0 * 4.0, q[2], q[3]);
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    H(q[0]);
    ctrl Rz(-3.14159265358979 / 2.0, q[1], q[0]);
    ctrl Rz(-3.14159265358979 / 4.0, q[2], q[0]);
    H(q[1]);
    ctrl Rz(-3.14159265358979 / 2.0, q[2], q[1]);
    H(q[2]);
    M(q[0]); M(q[1]); M(q[2]); M(q[3]);
}

```

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

The circuit has 4 qubits q[0], q[1], q[2], q[3].

Initial state: |0000>

1. X(q[3]) → |0001>

2. H(q[0]); H(q[1]); H(q[2]) → (|0>+|1>)/√2 ⊗ (|0>+|1>)/√2 ⊗ (|0>+|1>)/√2 ⊗ |1>
   = 1/2√2 * Σ_{x=0}^{7} |x, 1> where x is 3-bit

3. ctrl Rz(2π * 4/8 * 1, q[0], q[3]) = CRz(π, q[0], q[3])
   When q[0]=1 and q[3]=1, applies phase e^{iπ} = -1

4. ctrl Rz(2π * 4/8 * 2, q[1], q[3]) = CRz(2π, q[1], q[3])
   Phase e^{i2π} = 1, no effect

5. ctrl Rz(2π * 4/8 * 4, q[2], q[3]) = CRz(4π, q[2], q[3])
   Phase e^{i4π} = 1, no effect

So after step 3, the state is:
1/2√2 * (|0001> + |0011> + |0101> + |0111> + |1001> - |1011> + |1101> - |1111>)

Wait, let me reconsider. The phase applied is e^{iθ} where θ = Rz angle.

Actually, CRz(θ, control, target) applies Rz(θ) to target when control is |1>. Rz(θ)|1> = e^{iθ/2}|1>.

Wait, let me be more careful. Rz(θ) = [[1,0],[0,e^{iθ}]]. So Rz(θ)|1> = e^{iθ}|1>.

So CRz(π, q[0], q[3]): when q[0]=1, q[3] gets phase e^{iπ} = -1.
CRz(2π, q[1], q[3]): when q[1]=1, q[3] gets phase e^{i2π} = 1.
CRz(4π, q[2], q[3]): when q[2]=1, q[3] gets phase e^{i4π} = 1.

So only the first CRz matters. The state becomes:
1/2√2 * (|000,1> + |001,1> + |010,1> + |011,1> + |100,1>·(-1) + |101,1>·(-1) + |110,1>·(-1) + |111,1>·(-1))

Wait no. When q[0]=1, q[3]=1, the phase is e^{iπ}. So:
|0001> stays (q[0]=0)
|0011> stays (q[0]=0)
|0101> stays (q[0]=0)
|0111> stays (q[0]=0)
|1001> → e^{iπ}|1001> = -|1001>
|1011> → -|1011>
|1101> → -|1101>
|1111> → -|1111>

Hmm wait, this is the QFT-like structure. Let me think again about what phase is applied.

Actually, let me reconsider. The controlled-Rz applies a phase to the |11> component. But which qubit gets the phase?

In isQ, `ctrl Rz(theta, q[0], q[3])` means q[0] is the control, and Rz(theta) is applied to q[3]. So when q[0]=1, Rz(theta) is applied to q[3].

Since q[3] is always |1> here, Rz(theta)|1> = e^{i*theta}|1>.

So:
- CRz(π, q[0], q[3]): phase e^{iπ} = -1 when q[0]=1
- CRz(2π, q[1], q[3]): phase e^{i2π} = 1 (no effect)
- CRz(4π, q[2], q[3]): phase e^{i4π} = 1 (no effect)

So after these gates:

### Reference answer

Dominant output states: |0101> with probability ~0.59 each

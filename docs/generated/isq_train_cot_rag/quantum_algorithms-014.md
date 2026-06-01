# ISQ training COT RAG corpus: quantum_algorithms shard 14

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/957

- task_id: `isqTrain/957`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5767`

### Prompt

Write isQ code for the following quantum task: implements the pauli_evolution pattern with modified rotation parameters (num_pi3_to_pi4). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a Pauli-X evolution with a modified rotation angle of π/4 (the "num_pi3_to_pi4" parameter adjustment).
2. **Qubits**: 1 qubit (`q[0]`) is allocated and measured.
3. **State evolution**: Starting from |0⟩, apply Rx(π/4) which yields cos(π/8)|0⟩ - i·sin(π/8)|1⟩.
4. **Probabilities**: Measuring gives P(|0⟩) = cos²(π/8) ≈ 0.8536 and P(|1⟩) = sin²(π/8) ≈ 0.1464, matching the predicted output.

## isqTrain/3907

- task_id: `isqTrain/3907`
- task_type: `bug_fix`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `superposition`, `phase_manipulation`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1437`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```
import std;
// QFT on 3 qubits with input state |110>
qbit q[3];

procedure main() {
    // Prepare input state |110>
    X(q[0]);
    X(q[1]);

    // QFT stage for qubit 0
    H(q[0]);
    ctrl Rz(2.0 * 2.0 * 3.14159265358979 / 4.0, q[1], q[0]);
    ctrl Rz(2.0 * 3.14159265358979 / 8.0, q[2], q[0]);
    // QFT stage for qubit 1
    H(q[1]);
    ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[2], q[1]);
    // QFT stage for qubit 2
    H(q[2]);
    // Swap q[0] and q[2]
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    // Measure after QFT
    M(q[0]); M(q[1]); M(q[2]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

## Bug Analysis

**1. Bug Location:** Line 10 in the QFT stage for qubit 0:
`ctrl Rz(2.0 * 2.0 * 3.14159265358979 / 4.0, q[1], q[0]);`

The expression evaluates to `4.0 * π / 4.0 = π`, but the correct rotation angle for R₂ (the controlled phase between q[1] and q[0]) should be `2π/2² = 2π/4 = π/2`.

**2. Fix:** Remove the erroneous extra `2.0 *` multiplication:
`ctrl Rz(2.0 * 3.14159265358979 / 4.0, q[1], q[0]);`

This correctly computes `2π/4 = π/2`.

**3. State Evolution (Corrected Circuit):**
- Initial state: |000⟩ → X(q[0]), X(q[1]) → |110⟩
- QFT stage q[0]: H(q[0]) creates equal superposition on q[0] with phase factors from |1⟩. The corrected Rz(π/2, q[1]→q[0]) and Rz(π/4, q[2]→q[0]) apply proper controlled phases.
- QFT stage q[1]: H(q[1]) with Rz(π/2, q[2]→q[1])
- QFT stage q[2]: H(q[2])
- Swap q[0] ↔ q[2] reverses qubit order

The 3-qubit QFT of |6⟩ = |110⟩ produces:
`QFT|6⟩ = (1/√8) Σⱼ₌₀⁷ e^{2πi·6j/8} |j⟩`

All

## isqTrain/803

- task_id: `isqTrain/803`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `ancilla_usage`, `multi_controlled_logic`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `2855`

### Prompt

Write isQ code for the following quantum task: implements the quantum_multiplier pattern but with a different initial state preparation (flip q[[0, 2]] -> q[3]).

### Chain-of-thought reasoning

The task is to write an isQ program for a quantum_multiplier pattern but with a different initial state preparation. Let me analyze The implementation first:

circuit implementation:
1. Uses 5 qubits q[0], q[1], q[2], q[3], q[4]
2. Sets multiplier a=1 by applying X(q[3])
3. Sets multiplicand b=2 (binary 10): b1=1, b0=0 - but looking at the code, there's no X gate on q[2], so b1 should be 0... Wait, let me re-read.

Actually, Analyzing the:
- X(q[3]) sets q[3] to |1>, representing a=1
- The comment says b=2 (binary 10): b1=1, b0=0, but there's no X gate applied to q[2]
- Toffoli(q[0], q[1], q[3]) - this uses q[0], q[1] as controls and q[3] as target
- Toffoli(q[0], q[2], q[4]) - this uses q[0], q[2] as controls and q[4] as target

Wait, this seems odd. If q[0] and q[1] are both controls, and they start in |0>, the Toffoli won't do anything...

Actually, let me reconsider. The prompt says "flip q[[0, 2]] -> q[3]". This means we need to apply X gates to q[0] and q[2] to flip them, and q[3] is the target that gets modified.

So the new initial state preparation should be:
- X(q[0]) to set q[0] to |1>
- X(q[2]) to set q[2] to |1>
- This would set a different initial state

Let me think about what this multiplier circuit is doing:
- q[0] and q[1] are controls for the first Toffoli, targeting q[3]
- q[0] and q[2] are controls for the second Toffoli, targeting q[4]

If we flip q[0] and q[2]:
- Initial state after X(q[0]) and X(q[2]): |1⟩₀|0⟩₁|1⟩₂|0⟩₃|0⟩₄
- After Toffoli(q[0], q[1], q[3]): Since q[1]=|0⟩, this Toffoli does nothing
- After Toffoli(q[0], q[2], q[4]): Since q[0]=|1⟩ and q[2]=|1⟩, this flips q[4] to |1⟩

So the final state before measurement would be: |1⟩₀|0⟩₁|1⟩₂|0⟩₃|1⟩₄

Measuring q[3] and q[4]:
- q[3] = 0
- q[4] = 1

Since earlier measured qubit = higher bit, and q[3] is measured first:
- Result = q[3] * 2 + q[4] = 0 * 2 + 1 = 1 = |01⟩

But the predicted output is {|10⟩: 1.0}, which means q[3]=1 and q[4]=0...

Hmm, let me re-read The implementation again.

In the reference:
- X(q[3]) sets q[3] = |1⟩
- Toffoli(q[0], q[1], q[3]) - controls q[0], q[1]; target q[3]
  - Since q[0] and q[1] are both |0⟩, nothing happens, q[3] stays |1⟩
- Toffoli(q[0], q[2], q[4]) - controls q[0], q[2]; target q[4]
  - Since q[0] is |0⟩, nothing happens, q[4] stays |0⟩
- M(q[3]) = 1
- M(q[4]) = 0

So the measured state is |10⟩ (q[3]=1, q[4]=0).

Now for the new task: "flip q[[0, 2]] -> q[3]"

This means we flip q[0] and q[2] instead of q[3]. So:
- X(q[0]) - flip q[0] to |1⟩
- X(q[2]) - flip q[2] to |1⟩

Now the state is |1⟩₀|0⟩₁|1⟩₂|0⟩₃|0⟩₄

## isqTrain/2811

- task_id: `isqTrain/2811`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_procedures`, `measurement_order`, `superposition`
- source: `isq_train_cot`
- dataset_index: `4548`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[3];

procedure main(){
    X(q[0]); 

    H(q[0]);
    X2P(q[1]);
    CZ(q[0], q[2]);
    Y2M(q[0]);
    CZ(q[2], q[1]);
    M(q[0]);
    M(q[1]);
    M(q[2]);
}
```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a step-by-step analysis of an isQ quantum program to predict its measurement probability distribution. The output must be concise (3-15 lines), use Dirac notation, and start with "## Circuit Analysis".

2.  **Analyze the Circuit:**
    *   Initial state: $|q_2 q_1 q_0\rangle = |000\rangle$
    *   `X(q[0])`: State becomes $|001\rangle$
    *   `H(q[0])`: $H |1\rangle = |-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$. State becomes $\frac{1}{\sqrt{2}}(|00\rangle - |01\rangle) \otimes |0\rangle$ (Wait, let's stick to standard ordering $q_2 \otimes q_1 \otimes q_0$). Let's trace state of $q_0, q_1, q_2$ independently first, as some operations commute or are parallel.
        *   $q_0$: $|0\rangle \xrightarrow{X} |1\rangle \xrightarrow{H} |-\rangle$.
        *   $q_1$: $|0\rangle \xrightarrow{X2P} \frac{1}{\sqrt{2}}(|0\rangle - i|1\rangle)$. Wait, X2P is $R_x(\pi/2)$. $R_x(\pi/2)|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle - i|1\rangle)$. Let me check the exact matrix: $R_x(\theta) = \cos(\theta/2)I - i\sin(\theta/2)X$. For $\theta=\pi/2$, $R_x(\pi/2)|0\rangle = \frac{1}{\sqrt{2}}|0\rangle - i\frac{1}{\sqrt{2}}|1\rangle$.
        *   $q_2$: $|0\rangle$.
    *   *Wait, let's look at the entangling gates.*
    *   `CZ(q[0], q[2])`: Control is $q_0$, target is $q_2$.
        *   If $q_0$ is $|0\rangle$ (amplitude $+1/\sqrt{2}$), $q_2$ is $|0\rangle \to |0\rangle$.
        *   If $q_0$ is $|1\rangle$ (amplitude $-1/\sqrt{2}$), $q_2$ is $|0\rangle \xrightarrow{Z} |0\rangle$. Wait, $Z|0\rangle = |0\rangle$. So CZ does nothing to $|0\rangle$ target! Wait... $Z|0\rangle = |0\rangle$, $Z|1\rangle = -|1\rangle$. So CZ leaves $|00\rangle$ and $|10\rangle$ alone? No.
        *   Let's re-evaluate: $q_0$ is control. State of ($q_0, q_2$) before CZ is $|-\rangle \otimes |0\rangle = \frac{1}{\sqrt{2}}(|00\rangle - |10\rangle)$.
        *   `CZ(q[0], q[2])` applies $Z$ to $q_2$ if $q_0$ is 1.
        *   $\frac{1}{\sqrt{2}}(|0\rangle_0|0\rangle_2 - |1\rangle_0|0\rangle_2) \xrightarrow{CZ} \frac{1}{\sqrt{2}}(|0\rangle_0|0\rangle_2 - |1\rangle_0(|0\rangle_2)) = \frac{1}{\sqrt{2}}(|00\rangle - |10\rangle)$. It literally does nothing because $q_2$ is $|0\rangle$.
    *   `Y2M(q[0])`: $q_0$ undergoes $R_y(-\pi/2)$.
        *   Wait, what is the state of $q_0$ before this? It was $|-\rangle$. But CZ didn't entangle it, so it's still $|-\rangle$.
        *   $R_y(-\pi/2)|-\rangle = R_y(-\pi/2) \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
        *   $R_y(\theta)|

### Reference answer

{'predicted_probs': {'100': 0.5000000000000001, '110': 0.4999999999999999}, 'explanation': 'Probability distribution from quantum circuit simulation.'}

## isqTrain/3423

- task_id: `isqTrain/3423`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `multi_controlled_logic`, `reversible_computing`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1056`

### Prompt

Write isQ code for the following quantum task: a 1-bit quantum half adder in isQ using the CDKM (Cuccaro) approach.

A quantum half adder computes: sum = a XOR b, carry = a AND b.
Use a Toffoli gate for the carry and CNOT for the sum.

Test case: a=1, b=1. Expected sum=0, carry=1.

Requirements:
- q[0] = input a, q[1] = input b, q[2] = carry output
- Compute carry first: Toffoli(a, b, carry)
- Compute sum: CNOT(a, b) (b becomes a XOR b = sum)
- Measure q[1] (sum) and q[2] (carry)
- Declare 3 global qubits, measure all 3

### Chain-of-thought reasoning

## Reasoning
Goal: Implement a 1-bit quantum half adder computing sum = a XOR b and carry = a AND b for inputs a=1, b=1.

Three qubits are used: q[0]=a, q[1]=b (also holds sum output), q[2]=carry output; all 3 are measured.

State evolution:
- |000⟩ → X(q[0]) → |100⟩ → X(q[1]) → |110⟩
- Toffoli(q[0], q[1], q[2]): |110⟩ → |111⟩ (carry = a AND b = 1)
- CNOT(q[0], q[1]): |111⟩ → |101⟩ (q[1] = a XOR b = 0)

The final state |101⟩ gives measurement outcome q[0]=1, q[1]=0 (sum), q[2]=1 (carry) with probability 1.0, confirming the half adder: 1+1 = carry=1, sum=0.

## isqTrain/968

- task_id: `isqTrain/968`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `entanglement`, `hamiltonian_simulation`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `5379`

### Prompt

帮我写一个isQ程序：implements the lie_trotter pattern with modified rotation parameters (num_pi4b_to_pi6). Adjust the angle values while preserving the overall circuit structure.

### Chain-of-thought reasoning

The user wants me to analyze the Lie-Trotter circuit with modified rotation parameters and explain the quantum state evolution step by step.

Let me trace through the circuit:

1. Initial state: |00>
2. After X(q[0]): |10>

3. First-order Trotter decomposition for e^(-itH) where H = ZZ + XX, with t = π/8

Wait, let me look at the rotation angle: 0.52359877559830 radians
0.52359877559830 ≈ π/6

So the rotation angle is π/6, not π/4 as mentioned in the comment. This is the "num_pi4b_to_pi6" modification - changing from π/4 to π/6.

Actually wait, let me recalculate. The original had t = π/8, and Rz(2t) = Rz(π/4). But now the angle is π/6, so the effective time parameter has changed.

Let me verify: 0.52359877559830 = π/6 ≈ 0.5235987755982988... Yes, this is π/6.

So the circuit applies:
1. e^(-i(π/6)/2 * ZZ) = e^(-iπ/12 * ZZ) via CNOT-Rz(π/6)-CNOT
2. e^(-i(π/6)/2 * XX) = e^(-iπ/12 * XX) via H-H-CNOT-Rz(π/6)-CNOT-H-H

Wait, actually the Rz(2t) is applied, so if Rz angle is π/6, then 2t = π/6, so t = π/12.

Let me trace the state evolution:

Starting: |10>

Step 1: e^(-it*ZZ) with t such that 2t = π/6
- CNOT(q[0], q[1]): |10> → |11> (control is 1, target flips)
- Rz(π/6, q[1]): |11> → e^(-iπ/12)|11> (since Rz(θ)|1> = e^(-iθ/2)|1>)

Wait, Rz(θ) applies phase e^(-iθ/2) to |0> and e^(iθ/2) to |1>.

Actually let me be more careful. Rz(θ) = diag(e^(-iθ/2), e^(iθ/2)).

So Rz(π/6)|1> = e^(iπ/12)|1>

- CNOT(q[0], q[1]): e^(iπ/12)|11> → e^(iπ/12)|10>

After Step 1: e^(iπ/12)|10>

Step 2: e^(-it*XX) with same t
- H(q[0]); H(q[1]):
  H|1> = |-> = (|0> - |1>)/√2
  H|0> = |+>
  
  So e^(iπ/12)|10> → e^(iπ/12)|->|+>
  = e^(iπ/12)(|0> - |1>)/√2 ⊗ (|0> + |1>)/√2
  = e^(iπ/12)/2 (|00> + |01> - |10> - |11>)

- CNOT(q[0], q[1]):
  |00> → |00>
  |01> → |01>
  |10> → |11>
  |11> → |10>
  
  = e^(iπ/12)/2 (|00> + |01> - |11> - |10>)
  = e^(iπ/12)/2 (|00> + |01> - |10> - |11>)

- Rz(π/6, q[1]):
  Applied to second qubit:
  |0> → e^(-iπ/12)|0>
  |1> → e^(iπ/12)|1>
  
  = e^(iπ/12)/2 (e^(-iπ/12)|00> + e^(iπ/12)|01> - e^(-iπ/12)|10> - e^(iπ/12)|11>)
  = 1/2 (|00> + e^(iπ/6)|01> - |10> - e^(iπ/6)|11>)

- CNOT(q[0], q[1]):
  = 1/2 (|00> + e^(iπ/6)|01>

## isqTrain/4308

- task_id: `isqTrain/4308`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`, `isq_syntax_ctrl_nctrl`
- source: `isq_train_cot`
- dataset_index: `1928`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;

qbit q[3];

procedure main() {
    X(q[1]);
    
    // QFT
    H(q[2]);
    ctrl S(q[1], q[2]);
    ctrl T(q[0], q[2]);
    
    H(q[1]);
    ctrl S(q[0], q[1]);
    
    H(q[0]);
    
    // SWAP
    CNOT(q[0], q[2]);
    CNOT(q[2], q[0]);
    CNOT(q[0], q[2]);
    
    // Measure all qubits
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]); M(q[2]);
}

```

### Chain-of-thought reasoning

1.  **Understand the Goal:** The user wants a concise, precise, step-by-step analysis of an isQ quantum program, predicting its measurement probability distribution.

2.  **Analyze the isQ Code:**
    *   Initial state: $|q[2]q[1]q[0]\rangle = |000\rangle$ (Wait, standard isQ notation is often MSB to LSB or vice versa depending on the specific interpreter. Let's assume $q[0]$ is bit 0, $q[1]$ is bit 1, $q[2]$ is bit 2. The reference output has states from 000 to 111, let's track standard QFT).
    *   Let's write the state as $|q_0, q_1, q_2\rangle$. Wait, the swap (three-CNOT decomposition) and QFT usually operate as $q_0$ being the top wire (MSB or LSB depending on convention). Let's follow standard QFT on $q_0, q_1, q_2$.
    *   Wait, the code has `X(q[1]);` so the initial state is $|010\rangle$ (assuming $q_2$ is top, $q_0$ is bottom, wait, actually let's just track $q_0, q_1, q_2$ explicitly).
    *   Initial: $|0\rangle_0 |1\rangle_1 |0\rangle_2$.
    *   Wait, the circuit does QFT on some state, then swap (three-CNOT decomposition), then a measurement.
    *   Let's trace the QFT on $q_0, q_1, q_2$. Wait, is the initial state $|2\rangle$? If $q_0$ is LSB, $|q_2 q_1 q_0\rangle = |010\rangle = 2$.
    *   Let's check the QFT structure:
        *   `H(q[2]); ctrl S(q[1], q[2]); ctrl T(q[0], q[2]);`
        *   `H(q[1]); ctrl S(q[0], q[1]);`
        *   `H(q[0]);`
        *   This is exactly QFT on 3 qubits where $q_2$ is the most significant bit (MSB) if the controls are from $q_1, q_0$. Wait, if $q_2$ is MSB, then QFT of $|010\rangle$ (which is 2) should yield the Fourier state.
        *   Wait, let's look at standard QFT:
            *   Apply H to MSB, then controlled rotations from lower bits.
            *   The code applies H to $q_2$, then $S$ controlled by $q_1$, then $T$ controlled by $q_0$.
            *   This means $q_2$ is the first bit in the output (MSB).
            *   So the input state is $|q_2, q_1, q_0\rangle = |0, 1, 0\rangle = |2\rangle$.
        *   Wait, QFT of $|2\rangle$ (i.e., $|010\rangle$) is $\frac{1}{\sqrt{8}} \sum_{k=0}^{7} e^{i 2 \pi (2 k) / 8} |k\rangle = \frac{1}{\sqrt{8}} \sum_{k=0}^{7} e^{i \pi k / 2} |k\rangle$.
        *   Let's re-verify the bits: $q_2$ has $H$, ctrl $S$ from $q_1$, ctrl $T$ from $q_0$. This operates on $q_2$ first, then $q_1$, then $q_0$. This is exactly standard QFT.
        *   The input is $|010\rangle$, which corresponds to $k=2$.
        *   QFT output: $\frac{1}{\sqrt{8}} \sum_{j=0}^{7} e^{2\pi i (2 j / 8)} |j\rangle$.
        *   Since $2/8 = 1/4$, the phase is $e^{i \pi j / 2}$.
    *   Then swap (three-CNOT decomposition):
        *   `CNOT(q[0], q[2]); CNOT(q[2], q[0]); CNOT(q[0], q[2]);`
        *   This swaps $q_0$ and $q_2$. The QFT output normally has reversed bits, and this swap (three-CNOT decomposition) reverses them to correct the order,

### Reference answer

{'predicted_probs': {'000': 0.125, '001': 0.125, '010': 0.125, '011': 0.125, '100': 0.125, '101': 0.125, '110': 0.125, '111': 0.125}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|000>) = 0.1250, P(|001>) = 0.1250, P(|010>) = 0.1250, P(|011>) = 0.1250, P(|100>) = 0.1250, P(|101>) = 0.1250, P(|110>) = 0.1250, P(|111>) = 0.1250.'}

## isqTrain/903

- task_id: `isqTrain/903`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `intermediate`
- concept_tags: `ancilla_usage`, `boolean_logic`, `isq_syntax_oracle`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `3450`

### Prompt

Help me write isQ code that implements the bit_flip_oracle pattern but with a different initial state preparation (flip q[[0]] -> q[2]).

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a bit-flip oracle for f(x) = x[0] XOR x[1] with initial state preparation on q[2].
2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.
3. **State evolution**:
   - Start: |000⟩
   - X(q[2]): |001⟩ (flip ancilla qubit)
   - CNOT(q[0], q[2]): control q[0]=|0⟩, no flip → |001⟩
   - CNOT(q[1], q[2]): control q[1]=|0⟩, no flip → |001⟩
4. **Result**: Since both inputs x[0]=0 and x[1]=0, XOR(0,0)=0, so ancilla remains |1⟩ from initial preparation. Output state |001⟩ with probability 1.0.

## isqTrain/3661

- task_id: `isqTrain/3661`
- task_type: `code_generation`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `2439`

### Prompt

Create an isQ quantum circuit that 3-bit quantum phase estimation for phase angle 4*pi/4 (in multiples of 2π/8). Use 3 precision qubits, controlled-Rz rotations, and a 3-qubit inverse QFT. Measure all 4 qubits (3 precision + 1 eigenstate).

### Chain-of-thought reasoning

Let me analyze this quantum phase estimation (QPE) circuit step by step.

The goal is to implement 3-bit QPE for phase angle 4π/4 = π (which is 4 × 2π/8, so the phase is 4/8 × 2π = π).

Wait, let me re-read. The phase angle is 4π/4 = π. In multiples of 2π/8, that's 4 × 2π/8 = π. So the phase is π.

For Rz(θ), the unitary is:
Rz(θ) = diag(e^{-iθ/2}, e^{iθ/2})

So Rz(π) = diag(e^{-iπ/2}, e^{iπ/2}) = diag(-i, i)

The eigenvalue of |1⟩ under Rz(π) is e^{iπ/2} = i.

The phase φ = π/2 = (π/2)/(2π) = 1/4 of full rotation.

Wait, let me reconsider. The phase angle in the eigenvalue is π/2, which corresponds to binary fraction 0.010 = 2/8 = 1/4.

Hmm, but the problem says phase angle 4π/4. Let me recalculate.

Actually, looking at the problem statement: "phase angle 4*pi/4" = π.

And "in multiples of 2π/8" means the phase is 4 × (2π/8) = π.

The Rz gate is: Rz(θ)|1⟩ = e^{iθ/2}|1⟩

So Rz(π)|1⟩ = e^{iπ/2}|1⟩ = i|1⟩

The eigenvalue is e^{iφ} = i, so φ = π/2.

In the 3-bit representation, φ/(2π) = 1/4 = 0.010 in binary.

So we should measure |010⟩ on the precision qubits (plus |1⟩ on the eigenstate qubit).

But the predicted output show:
- |0001>: 0.005574
- |0011>: 0.140873
- |0101>: 0.590097
- |0111>: 0.263456

The most probable outcome is |0101⟩ which means precision qubits read 010 and eigenstate is 1. This corresponds to phase 010 in binary = 2/8 = 1/4 of 2π = π/2. ✓

But why isn't it exactly 1? Because the iQFT in the code has some issues with the rotation directions.

Wait, let me look at the iQFT implementation more carefully.

The inverse QFT should apply rotations in the opposite direction from QFT.

Standard iQFT on 3 qubits:
1. Swap q[0] and q[2]
2. H(q[0])
3. CRz(-π/2) from q[1] to q[0]... 

Wait, actually the iQFT uses controlled rotations Rz with negative angles, but the standard iQFT for phase estimation uses rotations like R_k^{-1} = Rz(-2π/2^k).

Actually, I think the issue is that the controlled rotations in the iQFT here are not quite right. Let me trace through more carefully.

Hmm, but The implementation gives specific probabilities, so let me just verify that the most likely outcome is |0101⟩ = qubits {q[3]=1, q[2]=0, q[1]=1, q[0]=0}.

In the --probs output, the bitstring is indexed with earlier measured qubit = higher bit. The measurements are M(q[0]), M(q[1]), M(q[2]), M(q[3]) in order.

So |0101> means q[3]=1 (LSB), q[2]=0, q[1]=1, q[0]=0 (MSB).

This means precision qubits (q[0], q[1], q[2]) = (0, 1, 0) and eigenstate q[3] = 1.

Binary 010 = 2, which represents phase 2/8 × 2π = π/2. ✓

The reason it's not exactly 1 is likely due to the specific implementation of iQFT with Rz gates instead of the standard controlled-phase gates.

Let me think about this more carefully. The issue might be that the controlled-Rz gates in the iQFT section are applying to wrong targets or have wrong angles.

Looking at the iQFT:
- After swap: q[0] was q[2], q[2] was q[0]
-

## isqTrain/4136

- task_id: `isqTrain/4136`
- task_type: `output_prediction`
- category: `quantum_algorithms`
- difficulty: `expert`
- concept_tags: `phase_manipulation`, `superposition`, `isq_syntax_ctrl_nctrl`, `qft_based_arithmetic`
- source: `isq_train_cot`
- dataset_index: `4683`

### Prompt

这段isQ程序的量子态演化结果是什么？给出测量概率分布。

```isq
import std;
qbit q[4];

procedure main() {
    X(q[3]);
    H(q[0]); H(q[1]); H(q[2]);
    ctrl Rz(2.0 * 3.14159265358979 * 7.0 / 8.0 * 1.0, q[0], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 7.0 / 8.0 * 2.0, q[1], q[3]);
    ctrl Rz(2.0 * 3.14159265358979 * 7.0 / 8.0 * 4.0, q[2], q[3]);
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

The circuit performs Quantum Phase Estimation (QPE) on a target qubit q[3] initialized to |1> (via X gate), using control qubits q[0], q[1], and q[2].
The eigenvalue of the unitary U applied to |1> is estimated. The unitary U is effectively U|1> = exp(-i * 7pi/4) |1> = exp(-i * 7pi/4) |1>. Wait, Rz(theta) applies a phase exp(-i*theta/2) to |1> and exp(i*theta/2) to |0>. Actually, Rz(theta) = exp(-i*theta*Z/2). So Rz(theta)|0> = exp(-i*theta/2)|0>, Rz(theta)|1> = exp(i*theta/2)|1>.
Here, the controlled gates are: ctrl Rz(theta_k, q[k], q[3]) for k=0,1,2.
Wait, ctrl Rz(theta_k, q[k], q[3]) means the control is q[k] and the target is q[3].
Let's trace the states:
Initial state: |0001>
After X(q[3]): |0001>
After H(q[0..2]): |+++1> = 1/sqrt(8) sum_{x=0}^7 |x>|1>
Controlled Rz gates:
ctrl Rz(2*pi * 7/8 * 1, q[0], q[3]): if q[0]=1, apply Rz(7pi/4) to q[3].
ctrl Rz(2*pi * 7/8 * 2, q[1], q[3]): if q[1]=1, apply Rz(7pi/4 * 2) to q[3].
ctrl Rz(2*pi * 7/8 * 4, q[2], q[3]): if q[2]=1, apply Rz(7pi/4 * 4) to q[3].
Since q[3] is in |1>, applying Rz(theta) to q[3] adds a phase exp(i*theta/2) to the state.
Wait, isQ's Rz(theta) might be Rz(theta)|1> = exp(i*theta/2)|1> or it might apply a phase exp(-i*theta/2) to |0> and exp(i*theta/2) to |1>.
The total phase added to |x>|1> is exp(i/2 * (2*pi * 7/8 * x[0] + 2*pi * 7/8 * 2 * x[1] + 2*pi * 7/8 * 4 * x[2])) = exp(i * pi * 7/8 * x), where x = x[0] + 2*x[1] + 4*x[2].
This phase is exp(2*pi*i * 7/8 * x / 2)? Wait.
The phase accumulated is exp(i/2 * sum 2*pi * 7/8 * x_k * 2^k) = exp(i * pi * 7/8 * x). Wait, is the QPE meant to estimate the phase 7/8 * pi or 7/16 * 2pi?
Usually, controlled-U^{2^k} applies a phase exp(i * phi * 2^k) to |1>.
If U|1> = exp(2*pi*i*phi)|1>, then phi = 7/16? No.
Let's look at the inverse QFT part.
The circuit applies CNOT(q[0], q[2]), CNOT(q[2], q[0]), CNOT(q[0], q[2]) which is swap (three-CNOT decomposition)(q[0], q[2]).
Wait, CNOT(c, t) then CNOT(t, c) then CNOT(c, t) swaps the qubits if they are in the computational basis, but for general states it swaps them.
Let's check:
CNOT(0,2) -> |c, m, t> -> |c, m, c^t>
CNOT(2,0) -> |c^t, m, c^t^0=c^t> -> wait.
Let's write the state |a, b, c>.
CNOT(a, c) -> |a, b, a^c>
CNOT(c, a) -> |a^c^a, b, a^c> = |c, b, a^c>
CNOT(a, c) -> |c, b, c^a^c> = |c, b, a>.
Yes, this is swap (three-CNOT decomposition)(q[0], q[2]).
Then

### Reference answer

Dominant output states: |0011> with probability ~0.43 each

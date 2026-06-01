# ISQ training COT RAG corpus: state_preparation shard 24

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/3994

- task_id: `isqTrain/3994`
- task_type: `bug_fix`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `1262`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```
import std;
// Entangled 2-qubit state via Ry(2.0 * 1.000) + CNOT
qbit q[2];

procedure main() {
    // Create entangled state
    Ry(1.000, q[0]);
    CNOT(q[0], q[1]);
    // Measure
    M(q[0]); M(q[1]);
}

``` (bug type: wrong parameter)

### Chain-of-thought reasoning

## Bug Analysis

**Bug:** The comment incorrectly states `Ry(2.0 * 1.000)`, implying the rotation angle should be 2.0, but the actual gate parameter `1.000` is correct.

**Fix:** Update the comment to reflect the correct parameter: `Ry(1.000)`.

**State evolution of the corrected circuit:**
1. Initial state: |00⟩
2. After Ry(1.000, q[0]): cos(0.5)|0⟩ + sin(0.5)|1⟩ ⊗ |0⟩ → cos(0.5)|00⟩ + sin(0.5)|10⟩
3. After CNOT(q[0], q[1]): cos(0.5)|00⟩ + sin(0.5)|11⟩
4. Measurement probabilities: P(|00⟩) = cos²(0.5) ≈ 0.770151, P(|11⟩) = sin²(0.5) ≈ 0.229849 ✓

## isqTrain/1789

- task_id: `isqTrain/1789`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `513`

### Prompt

帮我写一个isQ程序：a CZ ring on 3 qubits (all in |+>): apply CZ between each consecutive pair and between last and first.

### Chain-of-thought reasoning

The user wants a concise reasoning section for a quantum circuit: a CZ ring on 3 qubits initially in the |+> state.

1.  **Goal**: Create a 3-qubit circuit with a CZ ring (CZ between each pair) starting from |+>^3.
2.  **Qubits**: 3 qubits needed, all measured.
3.  **Evolution**:
    *   Initial state: |0>^3.
    *   After H gates: (|0>+|1>)^3 / sqrt(8) = 1/sqrt(8) * sum_{x,y,z in {0,1}} |xyz>.
    *   Apply CZ(0,1), CZ(1,2), CZ(2,0). CZ applies a -1 phase if both qubits are |1>.
    *   State after CZ ring: 1/sqrt(8) * sum_{x,y,z in {0,1}} (-1)^{xy + yz + zx} |xyz>.
    *   Let's evaluate the phase for each bitstring:
        *   000: 0
        *   001: 0
        *   010: 0
        *   011: 1*0 + 1*1 + 0*1 = 1
        *   100: 0
        *   101: 1*0 + 0*1 + 1*1 = 1
        *   110: 1*1 + 1*0 + 0*1 = 1
        *   111: 1*1 + 1*1 + 1*1 = 3 = 1 mod 2
    *   Wait, let's re-verify.
        *   xy + yz + zx = xy XOR yz XOR zx (since coefficients are binary and phase is -1 to the power).
        *   000: 0 -> +1
        *   001: 0 -> +1
        *   010: 0 -> +1
        *   011: 01 + 11 + 10 -> 0 + 1 + 0 = 1 -> -1
        *   100: 0 -> +1
        *   101: 10 + 01 + 11 -> 0 + 0 + 1 = 1 -> -1
        *   110: 11 + 10 + 01 -> 1 + 0 + 0 = 1 -> -1
        *   111: 11 + 11 + 11 -> 1 + 1 + 1 = 3 mod 2 = 1 -> -1
    *   Wait, the predicted output in the prompt are uniform: 1/8 for all states!
    *   Why is it uniform? Ah, the prompt says "Expected measurement probabilities: {|000>: 0.125, ...}".
    *   Let me check the phase calculation again.
        *   |0> = |000>
        *   |1> = |001>
        *   |2> = |010>
        *   |3> = |011> -> x=0, y=1, z=1 -> xy=0, yz=1, zx=0 -> sum=1.
        *   |5> = |101> -> x=1, y=0, z=1 -> xy=0, yz=0, zx=1 -> sum=1.
        *   |6> = |110> -> x=1, y=1, z=0 -> xy=1, yz=0, zx=0 -> sum=1.
        *   |7> = |111> -> x=1, y=1, z=1 -> xy=1, yz=1, zx=1 -> sum=3 = 1 mod 2.
    *   Wait, the amplitude for |011> is -1. The amplitude for |111> is -1.
    *   Probabilities are |amplitude|^2. So +1 or -1 doesn't matter for probabilities!
    *   Prob(|xyz>) = |1/sqrt(8) * (-1)^...|^2 = 1/8.
    *   Yes, probabilities are uniform.
4.  **Conclusion**: The final state has equal magnitude for all basis states, leading to a uniform distribution.

Let's draft the reasoning.
- Goal: Apply a CZ ring to 3 qubits in the |+> state to create a uniform superposition with specific phases.
- Qubits: 3 qubits required, all measured.
- Steps:
    1. Apply H to all 3 qubits to prepare |+>^3 =

## isqTrain/1364

- task_id: `isqTrain/1364`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `basis_change`, `entanglement`
- source: `isq_train_cot`
- dataset_index: `1376`

### Prompt

用isQ实现Prepare a GHZ state on 3 qubits and measure all qubits in the X basis (apply H before measurement).

### Chain-of-thought reasoning

## Reasoning
Goal: Prepare a 3-qubit GHZ state and measure all qubits in the X-basis by applying H before measurement.

State evolution:
- Initial: |000⟩
- H(q[0]): (|000⟩ + |100⟩)/√2
- CNOT(q[0], q[1]): (|000⟩ + |110⟩)/√2
- CNOT(q[0], q[2]): (|000⟩ + |111⟩)/√2 — GHZ state
- H(q[0]), H(q[1]), H(q[2]): H⊗³(|000⟩ + |111⟩)/√2 = (|000⟩ + |011⟩ + |101⟩ + |110⟩)/2

The final state has four computational basis states, each with equal amplitude 1/2, yielding probability 0.25 each. Only states with even parity (even number of 1s) survive because H⊗³|000⟩ and H⊗³|111⟩ interfere constructively for even-parity outcomes and destructively for odd-parity ones.

## isqTrain/1794

- task_id: `isqTrain/1794`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2839`

### Prompt

I need an isQ program to Bell pairs on 5 qubits (pair q[0]-q[1], q[2]-q[3], etc.) and measure all.

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Goal:** Generate a reasoning section for an isQ quantum program that creates Bell pairs on 5 qubits and measures all.
    *   **Input Circuit/Prompt:** 5 qubits. H on q[0], CNOT(q[0], q[1]), H on q[2], CNOT(q[2], q[3]). q[4] is idle. Measure all 5 qubits.
    *   **Constraints:** Output *only* the "## Reasoning" section. Use Dirac notation. Be concise (3-8 lines typically).

2.  **Trace the Quantum State Evolution:**
    *   Initial state: $|00000\rangle$ (using q[4] q[3] q[2] q[1] q[0] or similar, but it's easier to group by pairs).
    *   Pair 1: $|00\rangle_{01} \xrightarrow{H_0} \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)_0 |0\rangle_1 \xrightarrow{CNOT_{01}} \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)_{01} = |\Phi^+\rangle_{01}$.
    *   Pair 2: $|00\rangle_{23} \xrightarrow{H_2} \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)_2 |0\rangle_3 \xrightarrow{CNOT_{23}} \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)_{23} = |\Phi^+\rangle_{23}$.
    *   Qubit 4: Remains $|0\rangle_4$.
    *   Full state: $|\Phi^+\rangle_{01} \otimes |\Phi^+\rangle_{23} \otimes |0\rangle_4 = \frac{1}{2}(|0000\rangle + |0011\rangle + |1100\rangle + |1111\rangle)_{0123} \otimes |0\rangle_4$.

3.  **Determine Measurement Probabilities:**
    *   Measuring q[0] to q[4] yields 5-bit strings (MSB depends on exact isQ bit mapping, but standard reading gives combinations).
    *   q[0] and q[1] are perfectly correlated (00 or 11).
    *   q[2] and q[3] are perfectly correlated (00 or 11).
    *   q[4] is always 0.
    *   Therefore, valid bitstrings have a 1/4 probability of being 00000, 00110, 11000, or 11110 (assuming q[0] is LSB, q[4] is MSB).

4.  **Draft the Reasoning:**
    *   *Line 1 (Goal):* Create two maximally entangled Bell pairs across q[0]-q[1] and q[2]-q[3], leaving q[4] in the ground state, then measure all.
    *   *Line 2 (Qubits):* Uses 5 qubits, all of which are measured at the end.
    *   *Line 3-6 (State Evolution):*
        *   Start with $|00000\rangle_{q[4]q[3]q[2]q[1]q[0]}$.
        *   Apply H to q[0] and CNOT(q[0],q[1]): evolves $|00\rangle \to \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)_{q[1]q[0]}$.
        *   Apply H to q[2] and CNOT(q[2],q[3]): evolves $|00\rangle \to \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)_{q[3]q[2]}$.
        *   Qubit q[4] remains $|0\rangle$.
    *   *Line 7 (Probabilities):* The final state is $\frac{1}{2}(|00000\rangle + |0011\rangle + |1100\rangle + |1111\rangle)_{q[3..0]} \otimes |0\rangle_{q[4]}$, yielding a 25% probability for each of the four correlated outcomes (00 and 11 for both pairs), while q[4] deterministically measures as 0.

5.  **Refine and Format (Strict Rules):**
    *   Must start with "## Reasoning".

## isqTrain/4221

- task_id: `isqTrain/4221`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1029`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;
qbit q[2];

procedure main() {
    Ry(0.5, q[0]);
    Ry(0.5, q[1]);
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict the measurement output of an isQ circuit.
    *   Circuit: 2 qubits, both initialized to $|0\rangle$. Apply $R_y(0.5)$ to q[0] and $R_y(0.5)$ to q[1]. Measure both.
    *   Goal: Generate a "Circuit Analysis" section with step-by-step state evolution and predicted probability distribution.
    *   Constraints: Concise (3-15 lines), start with "## Circuit Analysis", end with predicted probability distribution, NO isQ code blocks, Dirac notation.

2.  **Analyze the Circuit:**
    *   Initial state: $|00\rangle$.
    *   $R_y(\theta) = \begin{pmatrix} \cos(\theta/2) & -\sin(\theta/2) \\ \sin(\theta/2) & \cos(\theta/2) \end{pmatrix}$.
    *   $\theta = 0.5$.
    *   $\cos(0.25) \approx 0.9689$
    *   $\sin(0.25) \approx 0.2474$
    *   $R_y(0.5)|0\rangle = \cos(0.25)|0\rangle + \sin(0.25)|1\rangle$.
    *   Since $R_y(0.5)$ is applied to *both* qubits independently, the joint state is the tensor product:
        $(\cos(0.25)|0\rangle + \sin(0.25)|1\rangle) \otimes (\cos(0.25)|0\rangle + \sin(0.25)|1\rangle)$
        $= \cos^2(0.25)|00\rangle + \sin(0.25)\cos(0.25)|01\rangle + \cos(0.25)\sin(0.25)|10\rangle + \sin^2(0.25)|11\rangle$.
    *   Probabilities:
        *   $P(00) = \cos^4(0.25) \approx 0.9389^2 \approx 0.882$  wait, $(\cos(0.25))^2 \approx 0.9388$.
        *   $P(01) = \cos^2(0.25)\sin^2(0.25) \approx 0.9388 \times 0.0612 \approx 0.0575$
        *   $P(10) = \cos^2(0.25)\sin^2(0.25) \approx 0.0575$
        *   $P(11) = \sin^4(0.25) \approx 0.0612^2 \approx 0.0037$
        Let's recompute:
        $\cos(0.25) \approx 0.9689124$
        $\sin(0.25) \approx 0.2474040$
        $\cos^2(0.25) \approx 0.9387913$
        $\sin^2(0.25) \approx 0.0612087$
        $P(00) \approx 0.9388$
        $P(01) \approx 0.0575$
        $P(10) \approx 0.0575$
        $P(11) \approx 0.0037$
    *   Most likely outcome: 00.

3.  **Draft the Analysis:**
    *   Start with "## Circuit Analysis"
    *   State initial state: $|00\rangle$
    *   Step 1: $R_y(0.5)$ on q[0]. State is $(\cos(0.25)|0\rangle + \sin(0.25)|1\rangle) \otimes |0\rangle$.
    *   Step 2: $R_y(0.5)$ on q[1]. State is $(\cos(0.25)|0\rangle + \sin(0.25)|1\rangle)^{\otimes 2}$.
    *   Explicit probabilities: $P(00) = \cos^4(0.25) \approx 0.88$, etc. Wait, no. $P(00) = \cos^2(0.25) * \cos^2(0.25) = 0.9388 * 0.9388 \approx 0.88$.
    *   Correction on math:
        $\cos(0.25) \approx

### Reference answer

Dominant output states: |00> with probability ~0.88 each

## isqTrain/4762

- task_id: `isqTrain/4762`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `superposition`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `4953`

### Prompt

实现以下量子计算任务（使用isQ）：implements: X on 2-qubit array, flip back q[0]. Declare a global qbit array q of 2 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply X to a 2-qubit array, then flip the first qubit back to demonstrate array and single-qubit gate operations.
2. **Qubits**: 2 global qubits q[0], q[1], both measured.
3. **State evolution**:
   - |00⟩ — initial state
   - X(q[0:2]) → |11⟩ — both qubits flipped
   - X(q[0]) → |01⟩ — first qubit flipped back
4. **Expected probabilities**: Final state is |01⟩, so measurement yields |01⟩ with probability 1.0.

## isqTrain/3116

- task_id: `isqTrain/3116`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `4793`

### Prompt

Create an isQ quantum circuit that an isQ program: apply Rx(3*pi/4) to a single qubit and measure. Expected P(0)=0.1464, P(1)=0.8536.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Apply an Rx rotation of $3\pi/4$ radians to a single qubit and measure it.
2. **Qubits**: 1 qubit is required and measured.
3. **State evolution**: 
   - Initialize the qubit to $|0\rangle$.
   - Apply Rx($3\pi/4$), which evolves the state to $\cos(3\pi/8)|0\rangle - i\sin(3\pi/8)|1\rangle$.
4. **Probabilities**: 
   - Measuring $|0\rangle$ yields a probability of $\cos^2(3\pi/8) = \frac{1 + \cos(3\pi/4)}{2} \approx 0.1464$.
   - Measuring $|1\rangle$ yields a probability of $\sin^2(3\pi/8) = \frac{1 - \cos(3\pi/4)}{2} \approx 0.8536$.

## isqTrain/4578

- task_id: `isqTrain/4578`
- task_type: `output_prediction`
- category: `state_preparation`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_for_loop`, `isq_syntax_if_else`
- source: `isq_train_cot`
- dataset_index: `2596`

### Prompt

帮我分析一下这个量子程序的输出：

```isq
import std;

qbit q[3];

procedure main() {
    
    X(q[2]);  // target different qubit
    
    
    for i in 0:3 {
        for j in 0:3 {
            if (i < j) {
                CNOT(q[i], q[j]);
            }
        }
    }
    
    for i in 0:3 {
        M(q[i]);
    }
}
```

### Chain-of-thought reasoning

## Circuit Analysis

1. **Initial state**: |q[0]⟩⊗|q[1]⟩⊗|q[2]⟩ = |000⟩

2. **X(q[2])**: Flips q[2] from |0⟩ to |1⟩. State becomes |001⟩.

3. **Nested CNOT loop** (i < j):
   - CNOT(q[0], q[1]): control=q[0]=|0⟩ → no flip, state remains |001⟩
   - CNOT(q[0], q[2]): control=q[0]=|0⟩ → no flip, state remains |001⟩
   - CNOT(q[1], q[2]): control=q[1]=|0⟩ → no flip, state remains |001⟩

4. **Final state before measurement**: |001⟩

All CNOT gates have their control qubits in |0⟩, so none of them flip their targets. The X gate only acted on q[2], which remains |1⟩ throughout.

**Predicted probability distribution**: {|001⟩: 1.0}

### Reference answer

{'predicted_probs': {'001': 1.0}, 'explanation': 'This isQ program operates on 3 qubit(s). The measurement probability distribution is: P(|001>) = 1.0000.'}

## isqTrain/1365

- task_id: `isqTrain/1365`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2951`

### Prompt

Write an isQ program that Prepare a GHZ state on 4 qubits: (|0000> + |1111>) / sqrt(2). Measure all qubits.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Prepare a 4-qubit GHZ state (|0000⟩ + |1111⟩)/√2 and measure all qubits.
2. **Qubits:** 4 qubits q[0]–q[3], all measured.
3. **State evolution:**
   - |0000⟩ → H(q[0]) → (|0000⟩ + |1000⟩)/√2
   - → CNOT(q[0],q[1]) → (|0000⟩ + |1100⟩)/√2
   - → CNOT(q[0],q[2]) → (|0000⟩ + |1110⟩)/√2
   - → CNOT(q[0],q[3]) → (|0000⟩ + |1111⟩)/√2
4. **Probabilities:** Measurement collapses the GHZ state to |0000⟩ or |1111⟩, each with probability 0.5.

## isqTrain/4775

- task_id: `isqTrain/4775`
- task_type: `code_generation`
- category: `state_preparation`
- difficulty: `basic`
- concept_tags: `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `4416`

### Prompt

请用isQ语言编写一个量子电路：implements: classical var variant 5. Declare a global qbit array q of 1 qubit(s). Use `import std;` and implement `procedure main()` with explicit measurements of all qubits.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Apply a Hadamard gate conditionally based on a classical variable (val=6 > 5).
2. One qubit q[0] is used and measured.
3. State evolution: |0⟩ → H → (1/√2)(|0⟩ + |1⟩) = |+⟩, since the condition (val > 5) is true.
4. Measuring |+⟩ yields equal probability of |0⟩ and |1⟩: P(|0⟩) = 0.5, P(|1⟩) = 0.5.

# ISQ training COT RAG corpus: quantum_communication shard 3

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/623

- task_id: `isqTrain/623`
- task_type: `code_generation`
- category: `quantum_communication`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `mid_circuit_measurement`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3181`

### Prompt

Code this in isQ: implements a variant of the teleportation_protocol pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

The user wants me to analyze the teleportation protocol and generate a reasoning section.

Let me trace through this circuit:

1. **Goal**: Implement a quantum teleportation protocol from q[0] to q[2] (message teleportation), with an expanded register of 5 qubits, where q[3] and q[4] are unused ground-state qubits.

2. **Qubits**: 5 qubits total (q[0]-q[4]), measuring q[2], q[3], q[4].

3. **Step-by-step state evolution**:

Initial state: |00000⟩

**Message preparation** (q[0]):
- H(q[0]): |00000⟩ → |+⟩|0000⟩ = (1/√2)(|0⟩ + |1⟩)|0000⟩ = (1/√2)(|00000⟩ + |10000⟩)

**Bell pair creation** (q[1], q[2]):
- H(q[1]): → (1/√2)(|00000⟩ + |10000⟩) × (1/√2)(|0⟩ + |1⟩)|000⟩ 
  = (1/2)(|00000⟩ + |01000⟩ + |10000⟩ + |11000⟩)

Wait, let me be more careful. After H(q[0]):
State = (1/√2)(|0⟩ + |1⟩)|0000⟩

After H(q[1]):
State = (1/√2)(|0⟩ + |1⟩) ⊗ (1/√2)(|0⟩ + |1⟩) ⊗ |000⟩
= (1/2)(|00000⟩ + |01000⟩ + |10000⟩ + |11000⟩)

After CNOT(q[1], q[2]):
q[1] is control, q[2] is target.
- |00000⟩ → |00000⟩ (q[1]=0, q[2] stays 0)
- |01000⟩ → |01100⟩ (q[1]=1, q[2] flips 0→1)
- |10000⟩ → |10000⟩ (q[1]=0, q[2] stays 0)
- |11000⟩ → |11100⟩ (q[1]=1, q[2] flips 0→1)

State = (1/2)(|00000⟩ + |01100⟩ + |10000⟩ + |11100⟩)

**Alice's operations**:
After CNOT(q[0], q[1]):
q[0] is control, q[1] is target.
- |00000⟩ → |00000⟩
- |01100⟩ → |01100⟩
- |10000⟩ → |10100⟩ (q[0]=1, q[1] flips 0→1)
- |11100⟩ → |11000⟩ (q[0]=1, q[1] flips 1→0)

State = (1/2)(|00000⟩ + |01100⟩ + |10100⟩ + |11000⟩)

After H(q[0]):
H on q[0]: |0⟩ → |+⟩, |1⟩ → |−⟩ = (1/√2)(|0⟩ - |1⟩)

- |00000⟩ → |+⟩|0000⟩ = (1/√2)(|00000⟩ + |10000⟩)
- |01100⟩ → |+⟩|1100⟩ = (1/√2)(|01100⟩ + |11100⟩)
- |10100⟩ → |−⟩|0100⟩ = (1/√2)(|10100⟩ - |00100⟩)
- |11000⟩ → |−⟩|1000⟩ = (1/√2)(|11000⟩ - |01000⟩)

Wait, I need to be more careful with the qubit ordering. Let me use q[0]q[1]q[2]q[3]q[4] notation.

State after Alice's CNOT:
= (1/2)(|00000⟩ + |01100⟩ + |10100⟩ + |11000⟩)

After H(q[0]):
= (1/2)[(1/√2)(|00000⟩ + |10000⟩) + (1/√2)(|01100⟩ + |11100⟩) + (1/√2)(|10100⟩ - |00100⟩) + (1/√2)(|11000⟩ - |01000⟩)]

= (1/(2√2))[|00000⟩ + |10000⟩ + |01100⟩ + |11100⟩ + |10100⟩ - |00100

## isqTrain/4618

- task_id: `isqTrain/4618`
- task_type: `output_prediction`
- category: `quantum_communication`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `3718`

### Prompt

What measurement results should I expect from this quantum program?

```isq
import std;

qbit q[2]; 

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    
    
    X(q[0]);
    
    
    CNOT(q[0], q[1]);
    H(q[0]);
    
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); 
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Initial state:** |00>
2. **H(q[0]):** Creates superposition, evolving state to (|00> + |10>)/√2.
3. **CNOT(q[0], q[1]):** Entangles the two qubits into the Bell state (|00> + |11>)/√2.
4. **X(q[0]):** Flips qubit 0, changing the state to (|10> + |01>)/√2.
5. **CNOT(q[0], q[1]):** Applies CNOT, evolving the state to (|11> + |01>)/√2, which factors as |+>|1>.
6. **H(q[0]):** Applies a Hadamard to qubit 0. H|+> = |0>, so the state becomes |01>.
7. **X(q[0]):** Flips qubit 0 from |0> to |1>, resulting in the final state |11>.

Predicted probability distribution: {|11>: 1.0}

### Reference answer

{'predicted_probs': {'11': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|11>) = 1.0000.'}

## isqTrain/4622

- task_id: `isqTrain/4622`
- task_type: `output_prediction`
- category: `quantum_communication`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5684`

### Prompt

Given this isQ code, what is the probability distribution after measurement?

```isq
import std;

qbit q[2]; 

procedure main() {
    H(q[1]);  // target different qubit
    CNOT(q[0], q[1]);
    
    
    X(q[0]);
    
    
    CNOT(q[0], q[1]);
    H(q[0]);
    
    M(q[0]); M(q[1]); 
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   Task: Predict the probability distribution of a given isQ quantum program.
    *   Format: "## Circuit Analysis" section, 3-8 lines for simple circuits, up to 15 lines.
    *   Content required: List of operations, step-by-step state evolution, final state, predicted probability distribution.
    *   Constraint: Output ONLY the analysis, starting with "## Circuit Analysis", no isQ code blocks, end with the predicted probability distribution.

2.  **Analyze the isQ Code:**
    *   `qbit q[2];` -> Initial state: $|00\rangle$
    *   `H(q[1]);` -> Apply H to q[1]. State: $|0\rangle \otimes \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = \frac{1}{\sqrt{2}}|00\rangle + \frac{1}{\sqrt{2}}|01\rangle$ (Note: q[0] is left qubit, q[1] is right qubit usually. Let's stick to standard Dirac: q[0]q[1]). State: $\frac{1}{\sqrt{2}}(|00\rangle + |01\rangle)$.
    *   `CNOT(q[0], q[1]);` -> Control=q[0], Target=q[1]. State: $\frac{1}{\sqrt{2}}(|00\rangle + |01\rangle)$ (since q[0] is |0>, target is unchanged).
    *   `X(q[0]);` -> Apply X to q[0]. State: $\frac{1}{\sqrt{2}}(|10\rangle + |11\rangle)$.
    *   `CNOT(q[0], q[1]);` -> Control=q[0], Target=q[1]. Since q[0] is |1>, target q[1] flips. State: $\frac{1}{\sqrt{2}}(|11\rangle + |10\rangle) = \frac{1}{\sqrt{2}}(|10\rangle + |11\rangle)$.
    *   `H(q[0]);` -> Apply H to q[0]. State: $\frac{1}{2}(|0\rangle - |1\rangle) \otimes |0\rangle + \frac{1}{2}(|0\rangle - |1\rangle) \otimes |1\rangle$
        $= \frac{1}{2}|00\rangle - \frac{1}{2}|10\rangle + \frac{1}{2}|01\rangle - \frac{1}{2}|11\rangle = \frac{1}{2}(|00\rangle + |01\rangle - |10\rangle - |11\rangle)$.
    *   `M(q[0]); M(q[1]);` -> Measurement.

3.  **Calculate Probabilities:**
    *   From the final state $\frac{1}{2}(|00\rangle + |01\rangle - |10\rangle - |11\rangle)$:
        *   P(|00>) = |1/2|^2 = 0.25
        *   P(|01>) = |1/2|^2 = 0.25
        *   P(|10>) = |-1/2|^2 = 0.25
        *   P(|11>) = |-1/2|^2 = 0.25
    *   Matches the expected measurement probabilities.

4.  **Draft the Explanation (Concise & Step-by-step):**
    *   Start with "## Circuit Analysis"
    *   Initial state: |00>
    *   After H(q[1]): |0>(|0> + |1>)/√2 = (|00> + |01>)/√2
    *   After CNOT(q[0], q[1]): Unchanged, as q[0] is |0>. State: (|00> + |01>)/√2
    *   After X(q[0]): Flips q[0] to |1>. State: (|10> + |11>)/√2
    *   After CNOT(q[0], q[1]): Flips q[1] because q[0] is |1>. State: (|11> + |10>)/√2
    *   After H(q[0]): Applies H to |1>, yielding (|0> - |1>)/√2. State expands to (|00> + |01> - |10> - |11>)/2.
    *   Measurement yields equal probabilities for all basis states.
    *   Predicted probability distribution: {|00

### Reference answer

{'predicted_probs': {'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 0.2500, P(|01>) = 0.2500, P(|10>) = 0.2500, P(|11>) = 0.2500.'}

## isqTrain/368

- task_id: `isqTrain/368`
- task_type: `code_generation`
- category: `quantum_communication`
- difficulty: `intermediate`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `2791`

### Prompt

I need an isQ program to implements the teleportation_protocol pattern. Include explicit identity operations in the circuit (X-X pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement a teleportation protocol pattern demonstrating gate cancellation awareness with an explicit X-X identity pair.
2. One qubit q[0] is used and measured.
3. State evolution:
   - Initial state: |0⟩ (default initialization)
   - After first X(q[0]): X|0⟩ = |1⟩ (bit flip)
   - After second X(q[0]): X|1⟩ = |0⟩ (X-X = I, gates cancel)
4. The X-X pair forms identity (X² = I), so the circuit has no net effect; measurement yields |0⟩ with probability 1.0.

## isqTrain/372

- task_id: `isqTrain/372`
- task_type: `code_generation`
- category: `quantum_communication`
- difficulty: `intermediate`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `1771`

### Prompt

I need an isQ program to implements the teleportation_protocol pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a single-qubit circuit that prepares |->, applies an explicit H-H identity pair (demonstrating gate cancellation awareness), then measures in the computational basis.

2. **Qubits**: 1 qubit (q[0]) is measured.

3. **State evolution**:
   - |0> → X → |1>
   - |1> → H → |-> = (1/√2)(|0> - |1>)
   - |-> → H → |1> (first H of identity pair)
   - |1> → H → |-> (second H of identity pair, H·H = I, so net effect is identity)
   - Final state: |-> = (1/√2)(|0> - |1>)

4. **Expected probabilities**: Since |-> = (1/√2)(|0> - |1>), measuring in Z-basis gives P(|0>) = |1/√2|² = 0.5 and P(|1>) = |-1/√2|² = 0.5. The H-H pair cancels out, leaving the state unchanged from |->.

## isqTrain/4436

- task_id: `isqTrain/4436`
- task_type: `output_prediction`
- category: `quantum_communication`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `1445`

### Prompt

What does this isQ program output when measured?

```isq
import std;

qbit q[2]; 

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    
    // Alice encodes "10" using Z
    Z(q[0]);
    
    // Bob decodes
    CNOT(q[0], q[1]);
    H(q[0]);
    
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); M(q[1]); // should be 10
}

```

### Chain-of-thought reasoning

1.  **Analyze the isQ code**:
    *   Initialize 2-qubit state `|00>`.
    *   `H(q[0])`: `|00>` -> `(|0> + |1>)|0> / sqrt(2)` = `|+0>`
    *   `CNOT(q[0], q[1])`: Creates Bell state `(|00> + |11>) / sqrt(2)`
    *   `Z(q[0])`: Applies Z gate. State becomes `(|00> - |11>) / sqrt(2)` (This is typically encoding '10' in the superdense coding protocol)
    *   `CNOT(q[0], q[1])`: Unentangles. State becomes `(|10> - |01>) / sqrt(2)`? Let's check: CNOT(|00> - |11>) = |00> - |10> (no, wait. CNOT(1,0) means control=1, target=0? No, `CNOT(q[0], q[1])` means control=q[0], target=q[1].)
        *   Wait, let's trace exactly:
        *   Initial: `|00>`
        *   H(q[0]): `(1/sqrt(2))(|00> + |10>)`
        *   CNOT(q[0], q[1]): `(1/sqrt(2))(|00> + |11>)`
        *   Z(q[0]): `(1/sqrt(2))(|00> - |11>)`
        *   CNOT(q[0], q[1]): `(1/sqrt(2))(|00> - |10>)` -> `(1/sqrt(2))(|0> - |1>)|0>`
        *   H(q[0]): `|10>`
        *   H(q[0]): `|10>` -> H|1> = `|->` = `(1/sqrt(2))(|0> - |1>)`. State: `(1/sqrt(2))(|00> - |10>)`
        *   Z(q[0]): `(1/sqrt(2))(|00> + |10>)`
        *   H(q[0]): `|00>`
        *   M(q[0]), M(q[1]): measures `00`.

2.  **Wait, let me re-verify the sequence**:
    *   `H(q[0])` -> `(1/sqrt(2))(|00> + |10>)`
    *   `CNOT(q[0], q[1])` -> `(1/sqrt(2))(|00> + |11>)`
    *   `Z(q[0])` -> `(1/sqrt(2))(|00> - |11>)`
    *   `CNOT(q[0], q[1])` -> `(1/sqrt(2))(|00> - |10>) = (1/sqrt(2))(|0> - |1>)|0>`
    *   `H(q[0])` -> H on `(|0> - |1>)` is `|1>`. So state becomes `|10>`.
    *   `H(q[0]); Z(q[0]); H(q[0]);` -> Applies HZH on q[0], which equals X. So `X(q[0])`.
    *   `X(q[0])` on `|10>` -> `|00>`.
    *   Measure `M(q[0]); M(q[1])` -> outcome is 00 with 100% probability.
    *   Wait, the prompt says: "expected measurement probabilities: {|00>: 1.0}".
    *   Let me double check the HZH on q[0]. HZH = X.
    *   If state was `|10>`, `X(q[0])` changes it to `|00>`.

3.  **Refine state evolution**:
    1. `|00>` -> `H(q[0])` -> `(1/√2)(|00> + |10>)`
    2. `CNOT(q[0], q[1])` -> `(1/√2)(|00> + |11>)`
    3. `Z(q[0])` -> `(1/√2)(|00> - |11>)`
    4. `CNOT(q[0], q[1])` -> `(1/√2)(|00> - |10>) = (1/√2)(|0> - |1>)|0>`
    5. `H(q[0])` -> `|10>`
    6. `H(q[0])` -> `(1/√2)(|00> - |10

### Reference answer

{'predicted_probs': {'00': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 1.0000.'}

## isqTrain/1942

- task_id: `isqTrain/1942`
- task_type: `output_prediction`
- category: `quantum_communication`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2271`

### Prompt

Run through this isQ program mentally and predict the probability of each measurement outcome.

```isq
import std;
qbit q[2];
procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    CNOT(q[0], q[1]);
    H(q[0]);
    M(q[0]); M(q[1]);
}
```

### Chain-of-thought reasoning

1.  **Analyze the Request:**
    *   **Task:** Output prediction (probability distribution) for a given isQ program.
    *   **Given Program:**
        
    *   **predicted output:** Circuit analysis starting with `## Circuit Analysis`, step-by-step state evolution using Dirac notation, and ending with the probability distribution.
    *   **Constraints:** Concise (3-8 lines), Dirac notation, specific format.

2.  **Analyze the Circuit:**
    *   Initial state: |00>
    *   `H(q[0])`: Applies H to qubit 0. State becomes $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle) = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |0\rangle$.
    *   `CNOT(q[0], q[1])`: Control=0, Target=1. State becomes $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$.
    *   `CNOT(q[0], q[1])`: Control=0, Target=1. Since it's applied again, it uncomputes the previous CNOT. State becomes $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
    *   `H(q[0])`: Applies H to qubit 0. $H|0\rangle = |+\rangle$, $H|1\rangle = |-\rangle$.
        $H (\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)) = \frac{1}{\sqrt{2}}(H|0\rangle|0\rangle + H|1\rangle|0\rangle) = \frac{1}{\sqrt{2}}(|+0\rangle + |-0\rangle)$.
        $|+\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$, $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$.
        Wait, an easier way: $H \otimes I (\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) \otimes |0\rangle) = (H \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)) \otimes |0\rangle = |0\rangle \otimes |0\rangle = |00\rangle$.
        Because $H|+\rangle = |0\rangle$.
    *   Final state: |00>
    *   Measurements: `M(q[0])` and `M(q[1])` will yield 0 with 100% probability.

3.  **Draft the Explanation:**
    *   Start with initial state $|00\rangle$.
    *   Apply H to q0: $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
    *   Apply CNOT(0,1): $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$.
    *   Apply second CNOT(0,1): $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$ (uncomputation).
    *   Apply second H to q0: $H|+\rangle \otimes |0\rangle = |00\rangle$.
    *   Predicted probabilities: {'00': 1.0}.

4.  **Refine to fit constraints (concise, 3-8 lines):**
    ## Circuit Analysis
    1. Initial state is |00>.
    2. H on q[0] creates the state $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
    3. The first CNOT entangles the qubits: $\frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$.
    4. The second CNOT uncomputes the entanglement, returning to $\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$.
    5. The second H on q[0] maps the superposition back to the ground state: |00>.
    6. The circuit perfectly uncomputes itself, resulting in deterministic measurements.

    Predicted probabilities: {'00': 1.0}

5.  **Check

### Reference answer

{'predicted_probs': {'00': 1.0}, 'explanation': 'Superdense coding 00'}

## isqTrain/625

- task_id: `isqTrain/625`
- task_type: `code_generation`
- category: `quantum_communication`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `mid_circuit_measurement`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `3779`

### Prompt

Write an isQ program that implements the teleportation_protocol pattern. Include explicit identity operations in the circuit (X-X pair before M(q[2])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

Let me analyze this quantum teleportation protocol step by step.

**Goal:** Teleport an unknown quantum state from qubit q[0] to qubit q[2], then verify the result.

**Qubits:** 3 qubits (q[0], q[1], q[2]), with q[2] measured at the end.

**Step-by-step evolution:**

1. **Initial state:** |000>

2. **H(q[0]):** Creates the message state |+0> = (|0> + |1>)/√2 ⊗ |00>
   State: (|000> + |100>)/√2

3. **H(q[1]):** (Bell pair creation starts)
   State: (|000> + |100> + |010> + |110>)/2

4. **CNOT(q[1], q[2]):** Creates Bell pair between q[1] and q[2]
   State: (|000> + |100> + |011> + |111>)/2

5. **CNOT(q[0], q[1]):** Alice's operation
   State: (|000> + |110> + |011> + |101>)/2

6. **H(q[0]):** Alice's operation
   State: (|000> + |100> + |010> - |110> + |011> - |111> + |001> + |101>)/2√2
   
   Let me redo this more carefully. After CNOT(q[0], q[1]):
   State = (|000> + |110> + |011> + |101>)/2
   
   H(q[0]) transforms:
   |0> → (|0> + |1>)/√2
   |1> → (|0> - |1>)/√2
   
   So:
   |000> → (|000> + |100>)/√2
   |110> → (|010> - |110>)/√2
   |011> → (|011> + |111>)/√2
   |101> → (|001> - |101>)/√2
   
   Total: (|000> + |100> + |010> - |110> + |011> + |111> + |001> - |101>)/(2√2)

7. **CNOT(q[1], q[2]):** Deferred correction
   This flips q[2] when q[1] = |1>
   
   |000> → |000>
   |100> → |100>
   |010> → |011>
   -|110> → -|111>
   |011> → |010>
   |111> → |110>
   |001> → |001>
   -|101> → -|101>
   
   State: (|000> + |100> + |011> - |111> + |010> + |110> + |001> - |101>)/(2√2)

8. **ctrl Z(q[0], q[2]):** Applies Z to q[2] when q[0] = |1>
   
   Z on |0> = |0>, Z on |1> = -|1>
   
   |000> → |000>
   |100> → -|101> (q[0]=1, so Z on q[2]: |0> stays |0>... wait, Z|0> = |0>, Z|1> = -|1>)
   
   Let me be more careful. Z acts on q[2]:
   When q[0] = 0: no change
   When q[0] = 1: apply Z to q[2]
   
   |000> → |000> (q[0]=0)
   |100> → |100> (q[0]=1, Z on q[2]=|0> gives |0>) → |100>
   |011> → |011> (q[0]=0)
   -|111> → -(-|111>) = |111> (q[0]=1, Z on q[2]=|1> gives -|1>)
   |010> → |010> (q[0]=0)
   |110> → |110> (q[0]=1, Z on q[2]=|0> gives |0>)
   |001> → |001> (q[0]=0)
   -|101> → -(-|101>) = |101> (q[0]=1, Z on q[2]=|1> gives -|1>)
   
   State: (|000> + |100>

## isqTrain/4836

- task_id: `isqTrain/4836`
- task_type: `code_generation`
- category: `quantum_communication`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `quantum_key_distribution`
- source: `isq_train_cot`
- dataset_index: `1191`

### Prompt

Implement the following in isQ: for E91 QKD with phase-flip error. Create a Bell pair, apply Z(q[1]) to simulate a phase error. Both measure in Z basis. Phase flip does not change Z-basis measurement probabilities.

### Chain-of-thought reasoning

## Reasoning
Goal: Create a Bell pair, apply a phase-flip error on q[1], and measure both qubits in the Z basis to show that phase flips don't affect Z-basis measurement probabilities.

State evolution:
- **|00⟩** → H(q[0]) → **(1/√2)(|00⟩ + |10⟩)**
- CNOT(q[0], q[1]) → **(1/√2)(|00⟩ + |11⟩)** = |Φ⁺⟩
- Z(q[1]) → **(1/√2)(|00⟩ − |11⟩)** = |Φ⁻⟩ (phase flip changes sign of |11⟩)
- Z-basis measurement: P(|00⟩) = |1/√2|² = 0.5, P(|11⟩) = |−1/√2|² = 0.5

The phase flip converts |Φ⁺⟩ to |Φ⁻⟩ by flipping the relative phase, but since both components remain in the same Z-basis eigenstates, the measurement probabilities are unchanged.

## isqTrain/4838

- task_id: `isqTrain/4838`
- task_type: `code_generation`
- category: `quantum_communication`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `quantum_key_distribution`
- source: `isq_train_cot`
- dataset_index: `2346`

### Prompt

实现以下量子计算任务（使用isQ）：for E91 with Y-error on the channel. Create a Bell pair, apply Y(q[1]) to simulate combined bit and phase error. Both measure in Z basis.

### Chain-of-thought reasoning

## Reasoning
Goal: Simulate the E91 protocol with a Y-error on the channel, creating a Bell pair then applying a combined bit+phase flip before measurement.
Two qubits (q[0], q[1]) are used, both measured in the Z basis.
State evolution: |00⟩ →(H on q[0])→ (1/√2)(|00⟩+|10⟩) →(CNOT)→ (1/√2)(|00⟩+|11⟩) = |Φ⁺⟩ →(Y on q[1])→ (1/√2)(i|01⟩−i|10⟩).
The Y gate maps |0⟩→i|1⟩ and |1⟩→−i|0⟩, producing anti-correlated outcomes with a global phase.
Measurement probabilities: |01⟩ and |10⟩ each with 0.5, since both basis states have equal amplitude magnitude (1/√2).

# ISQ training COT RAG corpus: circuit_engineering shard 3

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/2049

- task_id: `isqTrain/2049`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `circuit_optimization`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1729`

### Prompt

Calculate the expected measurement probabilities for this quantum circuit:

```isq
import std;
qbit q[1];
procedure main() {
    X(q[0]);
    Rz(1.5707963267949, q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations:** The circuit initializes a qubit `q[0]` and applies an X gate followed by an Rz gate with an angle of $\pi/2$ (since 1.5707963267949 $\approx \pi/2$).
2. **Initial State:** The qubit starts in the state $|0\rangle$.
3. **X Gate:** The X gate flips the qubit from $|0\rangle$ to $|1\rangle$.
4. **Rz Gate:** The $R_z(\pi/2)$ gate applies a phase factor of $e^{i\pi/4}$ to the $|1\rangle$ state. The quantum state becomes $e^{i\pi/4}|1\rangle$. This represents a global phase shift which does not affect measurement probabilities in the computational basis.
5. **Final State:** The final state before measurement is $e^{i\pi/4}|1\rangle$.
6. **Probabilities:** Measuring in the computational basis yields the outcome '1' with absolute certainty.

Probability distribution:
{'1': 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Rz consolidation: two Rz(pi/4) merged to Rz(pi/2). State |1>, P=1.0.'}

## isqTrain/2050

- task_id: `isqTrain/2050`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `circuit_optimization`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `1091`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[1];
procedure main() {
    X(q[0]);
    Rz(2.35619449019234, q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit starts with a single qubit `q[0]` in the initial state |0>.
2. The `X` gate is applied, flipping the qubit from |0> to |1>.
3. The `Rz(2.35619449019234, q[0])` gate applies a rotation around the Z-axis. This introduces a global phase to the |1> state, changing it to $e^{i \theta}|1\rangle$, where $\theta = 2.35619449019234$.
4. Since a global phase does not affect measurement probabilities, the qubit remains definitively in the |1> state.
5. Measuring the qubit yields |1> with certainty.

Probability distribution:
{'1': 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'S+T consolidation into Rz(3pi/4). State |1>, P=1.0.'}

## isqTrain/1062

- task_id: `isqTrain/1062`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `qubit_mapping`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4967`

### Prompt

Write an isQ program that implements a variant of the vf2_mapping pattern using q[3] -> q[5]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. **Goal**: Implement a VF2 mapping variant with expanded 5-qubit register, where q[3]-q[4] remain unused in ground state.
2. **Qubits**: 5 qubits declared (q[0]-q[4]), all measured; logical qubits a,b,c mapped to q[0],q[1],q[2].
3. **State evolution**:
   - Initial: |00000⟩
   - X(q[0]): |10000⟩
   - X(q[1]): |11000⟩
   - CNOT(q[0],q[2]): control=1 → flip target → |11100⟩
   - CNOT(q[1],q[2]): control=1 → flip target → |11000⟩
4. **Final state**: |11000⟩ with probability 1.0, as q[3],q[4] are untouched and remain |0⟩, and the double CNOT on q[2] cancels out (1⊕1=0).

## isqTrain/1058

- task_id: `isqTrain/1058`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `isq_syntax_deriving_gate`, `isq_syntax_multi_register`, `isq_syntax_procedures`, `qubit_mapping`
- source: `isq_train_cot`
- dataset_index: `4858`

### Prompt

Code this in isQ: implements the sabre_routing pattern with a different measurement ordering (reversed measurement order for q). The qubit measurement sequence affects the index mapping of the probability distribution.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement a swap (three-CNOT decomposition)-routed CNOT with reversed measurement order to verify bitstring indexing.
2. Three qubits (q[0], q[1], q[2]) are measured in reversed order: q[2] first (highest bit), q[0] last (lowest bit).
3. Initial state |000⟩ → X(q[0]) → |100⟩.
4. swap (three-CNOT decomposition)(q[0], q[1]) exchanges positions: |100⟩ → |010⟩.
5. CNOT(q[1], q[2]) with control=1 flips target: |010⟩ → |011⟩.
6. swap (three-CNOT decomposition)(q[0], q[1]) restores: |011⟩ → |101⟩.
7. Final state |101⟩ (q[2]=1, q[1]=0, q[0]=1) measured as q[2]q[1]q[0] = 101, yielding {|101⟩: 1.0}.

## isqTrain/4372

- task_id: `isqTrain/4372`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `basis_change`, `circuit_optimization`, `global_phase`
- source: `isq_train_cot`
- dataset_index: `2722`

### Prompt

I wrote this isQ program. What probabilities will I see when I run it with --probs?

```isq
import std;
qbit q[1];

// Optimized: H*X*H = Z (conjugation identity)
procedure main() {
    // Set qubit to |1>
    X(q[0]);
    // Replace H-X-H pattern with Z gate
    Z(q[0]);
    // Z|1> = -|1>, global phase is unobservable
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]);
}

```

### Chain-of-thought reasoning

1.  **Analyze the request:**
    *   Task: Predict measurement outcomes for an isQ program.
    *   Program:
        
    *   Output format: Circuit analysis starting with "## Circuit Analysis", step-by-step reasoning using Dirac notation, concise (3-15 lines), ending with predicted probabilities.

2.  **Analyze the quantum circuit:**
    *   Initial state: $|0\rangle$
    *   `X(q[0])`: Applies Pauli-X gate. State becomes $|1\rangle$.
    *   `Z(q[0])`: Applies Pauli-Z gate. $Z|1\rangle = -|1\rangle$. Global phase $-1$, so state is effectively $|1\rangle$ (or $-|1\rangle$).
    *   `H(q[0])`: Applies Hadamard. $H|1\rangle = |-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$. (Note: if we use $-|1\rangle$, $H(-|1\rangle) = -|-\rangle = |-\rangle$ since $-1/\sqrt{2} + 1/\sqrt{2}$ is just $|-\rangle$ wait, $H|1\rangle = |-\rangle$, $H(-|1\rangle) = -|-\rangle$, global phase).
    *   `Z(q[0])`: Applies Pauli-Z. $Z|-\rangle = Z(\frac{|0\rangle - |1\rangle}{\sqrt{2}}) = \frac{|0\rangle + |1\rangle}{\sqrt{2}} = |+\rangle$.
    *   `H(q[0])`: Applies Hadamard. $H|+\rangle = |0\rangle$.
    *   Measurement: Measure $|0\rangle$. Result is 0 with 100% probability.
    *   Alternative simplification: `H; Z; H` is equivalent to `X`.
    *   Circuit: `X; Z; X` applied to $|0\rangle$.
    *   `X|0\rangle = |1\rangle$.
    *   `Z|1\rangle = -|1\rangle$ (global phase).
    *   `X(-|1\rangle) = -|0\rangle$.
    *   Measure $|0\rangle$.

3.  **Draft the response:**
    *   **## Circuit Analysis**
    *   1. Initial state is $|0\rangle$.
    *   2. `X` gate flips it to $|1\rangle$.
    *   3. `Z` gate applies a global phase: $Z|1\rangle = -|1\rangle$.
    *   4. The sequence `H-Z-H` is mathematically equivalent to the `X` gate.
    *   5. Applying `X` to $-|1\rangle$ yields $-|0\rangle$.
    *   6. The global phase is unobservable, resulting in the state $|0\rangle$ before measurement.
    *   7. Predicted probability: 100% chance of measuring 0.

4.  **Refine for conciseness and rules:**
    *   "## Circuit Analysis"
    *   Start with initial state $|0\rangle$. `X` transforms it to $|1\rangle$.
    *   `Z` applies a phase, yielding $-|1\rangle$ (a physically equivalent state).
    *   The sequence `H; Z; H` forms the Pauli-X gate ($HZH = X$).
    *   Applying `X` to $-|1\rangle$ gives $-|0\rangle$.
    *   Since global phases are unmeasurable, the final state is $|0\rangle$.
    *   Measurement outcome is deterministically 0.
    *   End with the predicted probability distribution.

5.  **Final Polish:**
    ## Circuit Analysis
    1. Initial state is $|0\rangle$.
    2. The `X` gate flips the qubit to $|1\rangle$.
    3. The `Z` gate applies a global phase, changing the state to $-|1\rangle$.
    4. The sequence `H`, `Z`, `H` acts as an `X` gate because $HZH = X$.
    5. Applying this effective `X` gate to $-|1

### Reference answer

{'predicted_probs': {'0': 1.0}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 1.0000.'}

## isqTrain/1023

- task_id: `isqTrain/1023`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `difficult`
- concept_tags: `basis_change`, `circuit_optimization`, `global_phase`
- source: `isq_train_cot`
- dataset_index: `2581`

### Prompt

实现以下量子计算任务（使用isQ）：implements the template_matching_opt pattern. Include explicit identity operations in the circuit (H-H pair before M(q[0])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

## Reasoning
1. **Goal:** Demonstrate template matching optimization where the conjugation pattern H-X-H is recognized and replaced with a single Z gate.
2. **Qubits:** 1 qubit (q[0]) is initialized to |0⟩ and measured at the end.
3. **State evolution:**
   - `X(q[0])`: |0⟩ → |1⟩
   - `Z(q[0])`: |1⟩ → -|1⟩ (equivalent to H-X-H on |0⟩ up to global phase; the sign is unobservable)
   - `H(q[0])`: -|1⟩ → -(|0⟩ - |1⟩)/√2 = -|-⟩
   - `H(q[0])` (identity pair): -|-⟩ → -|1⟩ (H-H = I, demonstrating gate cancellation)
4. **Measurement:** The final state is -|1⟩, which equals |1⟩ up to an irrelevant global phase, yielding P(|1⟩) = 1.0.

## isqTrain/1063

- task_id: `isqTrain/1063`
- task_type: `code_generation`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `qubit_mapping`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `102`

### Prompt

实现以下量子计算任务（使用isQ）：implements the vf2_mapping pattern using an alternative gate decomposition (CNOT -> H CZ H). The circuit must produce the same output as the standard decomposition.

### Chain-of-thought reasoning

Let me analyze this circuit step by step.

1. **Goal**: Implement a circuit using VF2 mapping with alternative CNOT decomposition (CNOT = H-CZ-H), initializing qubits a=1, b=1.

2. **Qubits**: 3 qubits (q[0], q[1], q[2]), all measured.

3. **State evolution**:
   - Initial state: |000⟩
   - After X(q[0]): |100⟩
   - After X(q[1]): |110⟩
   - CNOT(q[0], q[2]) decomposed as H-CZ-H on q[2]:
     - H(q[2]): |11+⟩ where |+⟩ = (|0⟩+|1⟩)/√2
     - CZ(q[0], q[2]): when q[0]=1, applies Z to q[2], giving |11-⟩ where |−⟩ = (|0⟩−|1⟩)/√2
     - H(q[2]): H|−⟩ = |1⟩, so state is |111⟩
   - CNOT(q[1], q[2]) decomposed as H-CZ-H on q[2]:
     - H(q[2]): |11+⟩
     - CZ(q[1], q[2]): when q[1]=1, applies Z to q[2], giving |11-⟩
     - H(q[2]): H|−⟩ = |1⟩... wait, that gives |111⟩ not |110⟩

Wait, let me recalculate. H|−⟩ = |1⟩, so after the first CNOT decomposition we get |111⟩. Then the second CNOT decomposition:
- H(q[2]): |11+⟩
- CZ(q[1], q[2]): |11-⟩
- H(q[2]): |110⟩

So the final state is |110⟩, consistent with the predicted output.

Actually wait, let me be more careful.

After X(q[0]) and X(q[1]): state is |110⟩ (q[0]=1, q[1]=1, q[2]=0)

First CNOT(q[0], q[2]) using H-CZ-H decomposition:
- H(q[2]): q[2] goes from |0⟩ to |+⟩, state is (|110⟩ + |111⟩)/√2
- CZ(q[0], q[2]): This applies Z to q[2] when q[0]=|1⟩. Since q[0] is always |1⟩ here, Z is applied to q[2]: Z|+⟩ = |−⟩. State becomes (|110⟩ - |111⟩)/√2 = |11−⟩
- H(q[2]): H|−⟩ = |1⟩. State becomes |111⟩

This is correct - CNOT with control=|1⟩ flips the target from |0⟩ to |1⟩.

Second CNOT(q[1], q[2]) using H-CZ-H decomposition:
- H(q[2]): |111⟩ → (|110⟩ + |111⟩)/√2 = |11+⟩
- CZ(q[1], q[2]): q[1] is |1⟩, so Z applied to q[2]: Z|+⟩ = |−⟩. State: (|110⟩ - |111⟩)/√2 = |11−⟩
- H(q[2]): H|−⟩ = |1⟩. Wait, that gives |111⟩ again...

Hmm, let me recalculate. H|−⟩ = H(|0⟩ - |1⟩)/√2 = (|0⟩ + |1⟩ - |0⟩ + |1⟩)/2 = |1⟩. So H|−⟩ = |1⟩.

But The predicted output |110⟩. Let me reconsider.

Actually, I think I made an error. Let me redo this more carefully.

CNOT with control=1 and target in state |0⟩: should flip to |1⟩.
CNOT with control=1 and target in state |1⟩: should flip to |0⟩.

So:
- Start: |110⟩
- First CNOT(q[0], q[2]): q[0]=1, q[2]=0 → q[2] flips to 1 → |111⟩
- Second CNOT(q[1], q[2]): q[1]=1, q[2]=1 → q[2] flips to 0 → |110⟩

That's the standard CNOT behavior. Now let's verify the H-CZ-H decomposition gives the same.

H-CZ-H decomposition of CNOT(c, t):
- H(t)
- CZ(c, t)
- H(t)

Starting from |110⟩:

First C

## isqTrain/1020

- task_id: `isqTrain/1020`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `circuit_optimization`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2133`

### Prompt

Analyze this isQ circuit and determine the expected measurement outcomes.

```isq
import std;
qbit q[1];

// Optimized: S*T = Rz(pi/2)*Rz(pi/4) = Rz(3*pi/4)
procedure main() {
    // Set qubit to |1>
    X(q[0]);
    // Consolidated: S (Rz pi/2) + T (Rz pi/4) = Rz(3*pi/4)
    // 3*pi/4 = 2.35619449019234
    Rz(2.35619449019234, q[0]);
    // Phase-only change on basis state: measurement unaffected
    M(q[0]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations applied**:
   - `X(q[0])`: Applies the Pauli-X (bit-flip) gate.
   - `Rz(2.35619449019234, q[0])`: Applies a rotation around the Z-axis by an angle of $3\pi/4$.
   - `M(q[0])`: Measures the qubit in the computational (Z) basis.

2. **State evolution**:
   - Start in the initial state $|0\rangle$.
   - `X` gate flips the state to $|1\rangle$.
   - `Rz(3\pi/4)` gate adds a relative phase factor, transforming the state to $e^{-i(3\pi/8)}|1\rangle$.

3. **Final state before measurement**:
   - The state is $e^{-i(3\pi/8)}|1\rangle$, which is physically equivalent to $|1\rangle$ up to a global phase factor.

4. **Predicted probability distribution**:
   - Since the global phase does not affect measurement probabilities, the outcome is entirely deterministic.
   - Probabilities: **{|1>: 1.0}**

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Parametric variant of isqEval/313. Dimension: predict probabilities for reference circuit.'}

## isqTrain/2054

- task_id: `isqTrain/2054`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `expert`
- concept_tags: `circuit_optimization`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `2602`

### Prompt

What does this isQ program output when measured?

```isq
import std;
qbit q[1];
procedure main() {
    X(q[0]);
    T(q[0]);
    T(q[0]);
    T(q[0]);
    T(q[0]);
    M(q[0]);
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes a single qubit in the state |0>.
2. The X gate flips the state to |1>.
3. Four successive T gates are applied. Since $T = \text{diag}(1, e^{i\pi/4})$, applying it four times to |1> adds a phase of $(e^{i\pi/4})^4 = e^{i\pi} = -1$.
4. The final quantum state is -|1>, which is physically equivalent to |1> as global phase does not affect measurement probabilities.
5. The measurement will deterministically yield the outcome 1.

Predicted probability distribution: {'1': 1.0}

### Reference answer

{'predicted_probs': {'1': 1.0}, 'explanation': 'Solovay-Kitaev: Z = T^4 decomposition. State |1>, P=1.0.'}

## isqTrain/1011

- task_id: `isqTrain/1011`
- task_type: `output_prediction`
- category: `circuit_engineering`
- difficulty: `intermediate`
- concept_tags: `circuit_optimization`, `reversible_computing`
- source: `isq_train_cot`
- dataset_index: `4823`

### Prompt

What is the measurement probability distribution of this isQ program?

```isq
import std;
qbit q[2];

// Optimized: CNOT-CNOT pair cancelled, three X gates reduced to one
procedure main() {
    // Net effect of X, X, X on q[0] is a single X
    X(q[0]);
    // CNOT-CNOT pair removed (CNOT is self-inverse)
    // Measure both qubits to verify |10>
    M(q[0]); M(q[1]);
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit initializes two qubits, q[0] and q[1], in the ground state |00>.
2. An X gate is applied to q[0], acting as a bit-flip. This changes the state of q[0] from |0> to |1>.
3. The overall quantum state of the system becomes |10>.
4. Both qubits are measured. Since the quantum state is deterministically in the |10> basis state, there is a 100% chance of measuring this outcome.
Predicted probability distribution: {|10>: 1.0}

### Reference answer

{'predicted_probs': {'2': 1.0}, 'explanation': 'Parametric variant of isqEval/311. Dimension: predict probabilities for reference circuit.'}

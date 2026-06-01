# ISQ training COT RAG corpus: quantum_protocols shard 2

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4038

- task_id: `isqTrain/4038`
- task_type: `bug_fix`
- category: `quantum_protocols`
- difficulty: `expert`
- concept_tags: `entanglement`, `mid_circuit_measurement`, `isq_syntax_if_else`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `5163`

### Prompt

There's an error in this quantum circuit implementation. Fix it:

```
import std;
// Quantum teleportation of state Ry(0.5)|0>
// q[0] = state to teleport, q[1] = Alice's EPR half, q[2] = Bob's EPR half
qbit q[3];

procedure main() {
    // Prepare state to teleport
    // BUG: missing gate here
    // Create EPR pair between q[1] and q[2]
    H(q[1]);
    CNOT(q[1], q[2]);
    // Bell measurement on q[0] and q[1]
    CNOT(q[0], q[1]);
    H(q[0]);
    // Measure Bell pair
    int m0 = M(q[0]);
    int m1 = M(q[1]);
    // Classical corrections on Bob's qubit
    if (m1 == 1) {
        X(q[2]);
    }
    if (m0 == 1) {
        Z(q[2]);
    }
    // Measure teleported state
    M(q[2]);
}

``` (bug type: missing gate)

### Chain-of-thought reasoning

## Bug Analysis
1. **The bug**: The state preparation gate `Ry(0.5, q[0])` for the state to be teleported is missing. As a result, `q[0]` remains in the initial |0⟩ state, causing the teleportation protocol to simply reproduce |0⟩ on Bob's side instead of the intended rotated state.
2. **The fix**: Insert the gate `Ry(0.5, q[0]);` at the marked location to prepare the initial state $\alpha|0\rangle + \beta|1\rangle$ (where $\alpha = \cos(0.25)$ and $\beta = \sin(0.25)$).
3. **State evolution**: 
   - $|000\rangle \xrightarrow{Ry(0.5, q_0)} (\alpha|0\rangle + \beta|1\rangle) \otimes |00\rangle$
   - $H(q_1), CNOT(q_1, q_2) \rightarrow (\alpha|0\rangle + \beta|1\rangle) \otimes \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$
   - $CNOT(q_0, q_1), H(q_0) \rightarrow$ The system is expressed as a superposition of the four Bell states on $q_0, q_1$ correlated with the appropriate corrections applied to $q_2$.
   - Measurement of $q_0$ and $q_1$ collapses the state, and the classical feed-forward operations (`X

## isqTrain/4017

- task_id: `isqTrain/4017`
- task_type: `bug_fix`
- category: `quantum_protocols`
- difficulty: `difficult`
- concept_tags: `entanglement`, `mid_circuit_measurement`, `isq_syntax_if_else`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `3703`

### Prompt

The following isQ code has a bug. Find and fix it.

Buggy code:
```
import std;
// Quantum teleportation of state |+>
// q[0] = state to teleport, q[1] = Alice's EPR half, q[2] = Bob's EPR half
qbit q[3];

procedure main() {
    // Prepare state to teleport
    H(q[0]);
    // Create EPR pair between q[1] and q[2]
    H(q[1]);
    CNOT(q[1], q[2]);
    // Bell measurement on q[0] and q[1]
    CNOT(q[1], q[0]);
    H(q[0]);
    // Measure Bell pair
    int m0 = M(q[0]);
    int m1 = M(q[1]);
    // Classical corrections on Bob's qubit
    if (m1 == 1) {
        X(q[2]);
    }
    if (m0 == 1) {
        Z(q[2]);
    }
    // Measure teleported state
    M(q[2]);
}

``` (bug type: swapped qubits)

### Chain-of-thought reasoning

## Bug Analysis

1. **Bug**: In the Bell measurement section, `CNOT(q[1], q[0])` swaps control and target. The teleportation protocol requires q[0] (the state to teleport) as control and q[1] (Alice's EPR half) as target.

2. **Fix**: Change `CNOT(q[1], q[0])` to `CNOT(q[0], q[1])` so the CNOT correctly entangles the unknown state with Alice's half of the EPR pair.

3. **Corrected state evolution**:
   - After `H(q[0])`: q[0] = |+⟩
   - After EPR creation: q[1]⊗q[2] = (|00⟩+|11⟩)/√2
   - Combined: |+⟩⊗(|00⟩+|11⟩)/√2 = (|000⟩+|011⟩+|100⟩+|111⟩)/2
   - After `CNOT(q[0],q[1])`: (|000⟩+|011⟩+|101⟩+|110⟩)/2
   - After `H(q[0])`: ½(|000⟩+|100⟩+|011⟩-|111⟩+|001⟩-|101⟩+|010⟩-|110⟩)
   - Measuring q[0],q[1] yields m0,m1 ∈ {0,1} each with 50%; classical corrections (X if m1=1, Z if m0=1) always recover |+⟩ on q[2]
   - Final M(q[2]) on |+⟩ gives 50/50, yielding uniform 1/8 distribution over all 3-bit outcomes ✓

## isqTrain/3817

- task_id: `isqTrain/3817`
- task_type: `code_generation`
- category: `quantum_protocols`
- difficulty: `difficult`
- concept_tags: `entanglement`, `mid_circuit_measurement`, `isq_syntax_if_else`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `2769`

### Prompt

请用isQ语言编写一个量子电路：quantum teleportation of the state |+>.
1. Prepare the state on q[0]
2. Create EPR pair between q[1] and q[2]
3. Perform Bell measurement on q[0], q[1]
4. Apply classical corrections (X and Z) on q[2]
5. Measure all 3 qubits. Use mid-circuit measurement.

### Chain-of-thought reasoning

Let me trace through the quantum teleportation circuit step by step.

Initial state: |000>

Step 1: H(q[0]) - Prepare |+> state on q[0]
State: |+00⟩ = (1/√2)(|000⟩ + |100⟩)

Step 2: H(q[1]) - Start creating EPR pair
State: (1/√2)(|000⟩ + |100⟩) × (1/√2)(|0⟩ + |1⟩) on q[1]
= (1/2)(|000⟩ + |010⟩ + |100⟩ + |110⟩)

Step 3: CNOT(q[1], q[2]) - Complete EPR pair
= (1/2)(|000⟩ + |011⟩ + |100⟩ + |111⟩)

Step 4: CNOT(q[0], q[1]) - Start Bell measurement
= (1/2)(|000⟩ + |011⟩ + |110⟩ + |101⟩)

Step 5: H(q[0]) - Complete Bell basis change
H|0⟩ = |+⟩, H|1⟩ = |-⟩
= (1/2)((|+⟩|00⟩ + |+⟩|11⟩ + |-⟩|10⟩ + |-⟩|01⟩))
= (1/2)((|0⟩+|1⟩)/√2 |00⟩ + (|0⟩+|1⟩)/√2 |11⟩ + (|0⟩-|1⟩)/√2 |10⟩ + (|0⟩-|1⟩)/√2 |01⟩)

Let me expand:
= (1/(2√2))(|000⟩ + |100⟩ + |011⟩ + |111⟩ + |010⟩ - |110⟩ + |001⟩ - |101⟩)

Group by q[0], q[1]:
- |00⟩: |000⟩, |001⟩ → coefficients 1, 1
- |01⟩: |011⟩, |010⟩ → coefficients 1, 1
- |10⟩: |100⟩, -|110⟩ → coefficients 1, -1
- |11⟩: |111⟩, -|101⟩ → coefficients 1, -1

Actually let me redo this more carefully.

State after CNOT(q[0], q[1]):
(1/2)(|000⟩ + |011⟩ + |110⟩ + |101⟩)

This can be written as:
(1/2)(|0⟩|00⟩ + |0⟩|11⟩ + |1⟩|10⟩ + |1⟩|01⟩)
= (1/2)(|0⟩(|00⟩ + |11⟩) + |1⟩(|10⟩ + |01⟩))

After H(q[0]):
= (1/2)((|0⟩+|1⟩)/√2 (|00⟩ + |11⟩) + (|0⟩-|1⟩)/√2 (|10⟩ + |01⟩))
= (1/(2√2))(|0⟩(|00⟩ + |11⟩) + |1⟩(|00⟩ + |11⟩) + |0⟩(|10⟩ + |01⟩) - |1⟩(|10⟩ + |01⟩))
= (1/(2√2))(|0⟩(|00⟩ + |11⟩ + |10⟩ + |01⟩) + |1⟩(|00⟩ + |11⟩ - |10⟩ - |01⟩))

Measuring q[0] and q[1]:

m0=0, m1=0: q[2] in (1/2)(|0⟩ + |1⟩) = |+⟩
m0=0, m1=1: q[2] in (1/2)(|0⟩ + |1⟩) = |+⟩
m0=1, m1=0: q[2] in (1/2)(|0⟩ - |1⟩) = |-⟩
m0=1, m1=1: q[2] in (1/2)(|0⟩ - |1⟩) = |-⟩

After corrections:
- m0=0, m1=0: no correction, q[2] = |+⟩
- m0=0, m1=1: X correction, |+⟩ → |+⟩ (X|+⟩ = |+⟩)
- m0=1, m1=0: Z correction, |-⟩ → |+⟩ (Z|-⟩ = |+⟩)
- m0=1, m1=1: X then Z correction, |-⟩ → X|-⟩ = |-⟩ → Z|-⟩ = |+⟩

So q[2] always ends up in |+⟩ =

## isqTrain/3816

- task_id: `isqTrain/3816`
- task_type: `code_generation`
- category: `quantum_protocols`
- difficulty: `difficult`
- concept_tags: `entanglement`, `mid_circuit_measurement`, `isq_syntax_if_else`, `isq_syntax_classical_vars`
- source: `isq_train_cot`
- dataset_index: `4295`

### Prompt

用isQ实现quantum teleportation of the state |1>.
1. Prepare the state on q[0]
2. Create EPR pair between q[1] and q[2]
3. Perform Bell measurement on q[0], q[1]
4. Apply classical corrections (X and Z) on q[2]
5. Measure all 3 qubits. Use mid-circuit measurement.

### Chain-of-thought reasoning

Let me trace through the quantum teleportation circuit step by step.

Initial state: |000⟩ (q[0], q[1], q[2])

1. X(q[0]): Prepare |1⟩ on q[0]
   State: |100⟩

2. H(q[1]): Apply Hadamard to q[1]
   State: |1⟩ ⊗ (|0⟩+|1⟩)/√2 ⊗ |0⟩ = |1⟩(|0⟩+|1⟩)|0⟩/√2

3. CNOT(q[1], q[2]): Create EPR pair
   State: |1⟩ ⊗ (|00⟩+|11⟩)/√2

4. CNOT(q[0], q[1]): Bell measurement part 1
   State: |1⟩(|00⟩+|11⟩)/√2 → CNOT on q[0],q[1]
   = CNOT(|1⟩|0⟩)|0⟩/√2 + CNOT(|1⟩|1⟩)|1⟩/√2
   = |1⟩|1⟩|0⟩/√2 + |0⟩|1⟩|1⟩/√2

5. H(q[0]): Bell measurement part 2
   H|1⟩ = (|0⟩-|1⟩)/√2
   = (|0⟩-|1⟩)/√2 |1⟩|0⟩/√2·√2 + (|0⟩-|1⟩)/√2 ... wait let me redo this more carefully.

Let me be more careful. After step 3:
State = |1⟩₁ ⊗ (|00⟩₂₃ + |11⟩₂₃)/√2

Step 4: CNOT(q[0], q[1]) - control is q[0], target is q[1]
= |1⟩₁(|00⟩₂₃ + |11⟩₂₃)/√2
After CNOT(q[0],q[1]):
When q[0]=|1⟩, flip q[1]:
= |1⟩₁|10⟩₂₃/√2 + |1⟩₁|01⟩₂₃/√2

Wait, let me index properly. q[0] is the first qubit, q[1] is second, q[2] is third.

State = |1⟩₀ ⊗ (|0⟩₁|0⟩₂ + |1⟩₁|1⟩₂)/√2
     = (|1⟩₀|0⟩₁|0⟩₂ + |1⟩₀|1⟩₁|1⟩₂)/√2

CNOT(q[0], q[1]): control=q[0], target=q[1]
When q[0]=|1⟩, flip q[1]:
= (|1⟩₀|1⟩₁|0⟩₂ + |1⟩₀|0⟩₁|1⟩₂)/√2

H(q[0]):
H|1⟩ = (|0⟩ - |1⟩)/√2
= ((|0⟩₀ - |1⟩₀)/√2)|1⟩₁|0⟩₂/√2 + ((|0⟩₀ - |1⟩₀)/√2)|0⟩₁|1⟩₂/√2
= (|0⟩₀|1⟩₁|0⟩₂ - |1⟩₀|1⟩₁|0⟩₂ + |0⟩₀|0⟩₁|1⟩₂ - |1⟩₀|0⟩₁|1⟩₂)/2

Now measure q[0] → m0, q[1] → m1:

|00⟩₀₁: q[2] = |1⟩ (m0=0, m1=0)
|01⟩₀₁: q[2] = |1⟩ (m0=0, m1=1)
|10⟩₀₁: q[2] = |1⟩ (m0=1, m1=0)
|11⟩₀₁: q[2] = |1⟩ (m0=1, m1=1)

Wait, let me re-examine. The state is:
(|0⟩₀|1⟩₁|0⟩₂ - |1⟩₀|1⟩₁|0⟩₂ + |0⟩₀|0⟩₁|1⟩₂ - |1⟩₀|0⟩₁|1⟩₂)/2

Grouping by q[0],q[1] values:
- |0⟩₀|0⟩₁: coefficient |1⟩₂ (amplitude 1/2)
- |0⟩₀|1⟩₁: coefficient |0⟩₂ (amplitude 1/2)  
- |1⟩₀|0⟩₁: coefficient |1⟩₂ (amplitude -1

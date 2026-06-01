# ISQ training COT RAG corpus: quantum_communication shard 4

This generated document converts user-provided ISQ training examples into
retrieval-friendly Markdown for the Liangzhi Qwen3.6 quantum RAG index.

## isqTrain/4833

- task_id: `isqTrain/4833`
- task_type: `code_generation`
- category: `quantum_communication`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `quantum_key_distribution`
- source: `isq_train_cot`
- dataset_index: `3109`

### Prompt

I need an isQ program to for E91 that creates a Bell pair and Bob applies S then H before measuring (measuring in the Y basis). Alice measures in Z basis. Declare 2 global qubits.

### Chain-of-thought reasoning

## Reasoning
**Goal**: Implement E91 protocol with a Bell pair where Bob measures in Y basis (via S then H) and Alice measures in Z basis.

**Qubits**: 2 global qubits (q[0]=Alice, q[1]=Bob), both measured.

**State evolution**:
1. |00⟩ → H(q[0]) → (1/√2)(|00⟩ + |10⟩)
2. → CNOT(q[0],q[1]) → (1/√2)(|00⟩ + |11⟩) = |Φ⁺⟩ Bell state
3. → S(q[1]) → (1/√2)(|00⟩ + i|11⟩) since S|1⟩ = i|1⟩
4. → H(q[1]) → (1/2)(|00⟩ + |01⟩ + i|10⟩ − i|11⟩)

**Probabilities**: Each basis state has amplitude magnitude 1/2, giving P = |1/2|² = 0.25 for |00⟩, |01⟩, |10⟩, and |11⟩. The equal superposition arises because measuring |Φ⁺⟩ in Z⊗Y bases yields four equally likely outcomes (the bases are mutually unbiased).

## isqTrain/1384

- task_id: `isqTrain/1384`
- task_type: `code_generation`
- category: `quantum_communication`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `2410`

### Prompt

实现以下量子计算任务（使用isQ）：quantum teleportation to transfer the state |1> (prepared with X gate) from qubit 0 to qubit 2 using a Bell pair.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for a quantum teleportation circuit that transfers the state |1> from qubit 0 to qubit 2 using a Bell pair.

Let me trace through the circuit:

1. Initial state: |000>

2. X(q[0]): |100> - prepares |1> on qubit 0

3. H(q[1]): Creates superposition on qubit 1: (1/√2)(|100> + |110>)

4. CNOT(q[1], q[2]): Creates Bell pair: (1/√2)(|100> + |111>)

5. CNOT(q[0], q[1]): (1/√2)(|100> + |111>) - note: this is already in a form where the first two qubits are correlated
   Wait, let me recalculate. After step 4, state is (1/√2)(|100> + |111>)
   CNOT(q[0], q[1]): control is q[0], target is q[1]
   - |100> → |110> (q[0]=1, so flip q[1])
   - |111> → |101> (q[0]=1, so flip q[1])
   Result: (1/√2)(|110> + |101>)

6. H(q[0]): 
   - |110> → (1/√2)(|010> + |110>)
   - |101> → (1/√2)(|000> - |100>)
   Result: (1/2)(|010> + |110> + |000> - |100>)
   = (1/2)(|000> + |010> - |100> + |110>)

Actually, let me be more careful with the ordering. In isQ, q[0] is typically the most significant bit in measurement outcomes. Let me use the convention where |q[0], q[1], q[2]>.

State after H(q[1]) and CNOT(q[1], q[2]):
(1/√2)(|1,0,0> + |1,1,1>)

After CNOT(q[0], q[1]):
- |1,0,0> → |1,1,0> (q[0]=1, flip q[1])
- |1,1,1> → |1,0,1> (q[0]=1, flip q[1])
Result: (1/√2)(|1,1,0> + |1,0,1>)

After H(q[0]):
- |1,1,0> → (1/√2)(|0,1,0> - |1,1,0>)
- |1,0,1> → (1/√2)(|0,0,1> - |1,0,1>)
Result: (1/2)(|0,1,0> - |1,1,0> + |0,0,1> - |1,0,1>)

Now after measurements of q[0] and q[1]:
- If we measure |0,0>: q[2] is in state |1>
- If we measure |0,1>: q[2] is in state |0>
- If we measure |1,0>: q[2] is in state -|1>
- If we measure |1,1>: q[2] is in state -|0>

The correction gates:
- CNOT(q[1], q[2]): applies X to q[2] if q[1] was measured as |1>
- CZ(q[0], q[2]): applies Z to q[2] if q[0] was measured as |1>

After corrections:
- |0,0> → q[2] in |1> (no correction needed, but CNOT doesn't act, CZ doesn't act) → |1>
- |0,1> → q[2] in |0>, CNOT flips it → |1>
- |1,0> → q[2] in -|1>, CZ applies Z → |1>
- |1,1> → q[2] in -|0>, CNOT flips → -|1>, CZ applies Z → |1>

So after corrections, q[2] is always in state |1>, and measuring gives |1> with certainty.

But wait, in simulation mode (without actual measurement collapse), the classical bits store the measurement results, and then the CNOT and CZ are applied classically-conditioned.

Actually, Analyzing the code more carefully, it says "in simulation we apply both corrections" - this means in the simulation, after measurement, the classical values

## isqTrain/4435

- task_id: `isqTrain/4435`
- task_type: `output_prediction`
- category: `quantum_communication`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `2964`

### Prompt

帮我分析一下这个量子程序的输出：

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
    
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); M(q[1]); // should be 10
}

```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Gates applied**: H, CNOT, Z, CNOT, H, X
2. **State evolution**:
   - Initialize as |00>.
   - `H(q[0])` creates |+0> = (1/√2)(|00> + |10>).
   - `CNOT(q[0], q[1])` entangles to form a Bell state: (1/√2)(|00> + |11>).
   - `Z(q[0])` applies a phase shift, encoding the "10" message: (1/√2)(|00> - |11>).
   - `CNOT(q[0], q[1])` disentangles: (1/√2)(|00> - |10>).
   - `H(q[0])` collapses the superposition, successfully decoding the original message: |10>.
   - `X(q[0])` flips qubit 0 back from |1> to |0>: |00>.
3. **Final state**: |00>
4. **Prediction**: The circuit deterministically yields |00>.

Predicted probability distribution: {|00>: 1.0}

### Reference answer

{'predicted_probs': {'00': 1.0}, 'explanation': 'This isQ program operates on 2 qubit(s). The measurement probability distribution is: P(|00>) = 1.0000.'}

## isqTrain/4615

- task_id: `isqTrain/4615`
- task_type: `output_prediction`
- category: `quantum_communication`
- difficulty: `intermediate`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `5240`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;

qbit q[1];

procedure main() {
    
    X(q[0]); H(q[0]); 
    
    
    X(q[0]); // flip qubit 0 before measurement
    M(q[0]); 
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. The circuit starts in the |0> state. The first X gate flips it to |1>.
2. The H gate puts the q

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 0.5000, P(|1>) = 0.5000.'}

## isqTrain/626

- task_id: `isqTrain/626`
- task_type: `code_generation`
- category: `quantum_communication`
- difficulty: `difficult`
- concept_tags: `entanglement`, `isq_syntax_ctrl_nctrl`, `mid_circuit_measurement`, `multi_controlled_logic`
- source: `isq_train_cot`
- dataset_index: `2120`

### Prompt

实现以下量子计算任务（使用isQ）：implements the teleportation_protocol pattern. Include explicit identity operations in the circuit (H-H pair before M(q[2])) to demonstrate gate cancellation awareness.

### Chain-of-thought reasoning

Let me analyze this quantum teleportation protocol step by step.

**Goal:** The circuit implements a quantum teleportation protocol where Alice teleports a quantum state to Bob, with verification that the teleported state matches the original |+⟩ state.

**Qubits:** 3 qubits (q[0], q[1], q[2]), only q[2] is measured at the end.

**State evolution:**

1. **Initial state:** |000⟩

2. **H(q[0]):** Creates the message state |+⟩ on q[0]
   State: |+00⟩ = (1/√2)(|000⟩ + |100⟩)

3. **H(q[1]):** Creates superposition on q[1]
   State: (1/√2)(|000⟩ + |100⟩) ⊗ |+⟩ = (1/2)(|000⟩ + |010⟩ + |100⟩ + |110⟩)

4. **CNOT(q[1], q[2]):** Creates Bell pair between q[1] and q[2]
   State: (1/2)(|000⟩ + |011⟩ + |100⟩ + |111⟩)
   
   Now q[1] and q[2] form a Bell pair: |Φ+⟩ = (1/√2)(|00⟩ + |11⟩)

5. **CNOT(q[0], q[1]):** Alice's first operation
   State: (1/2)(|000⟩ + |011⟩ + |110⟩ + |101⟩)
   
   Rearranging: (1/2)(|000⟩ + |011⟩ + |101⟩ + |110⟩)

6. **H(q[0]):** Alice's Hadamard
   State: Let me recalculate...
   
   H on q[0]:
   |0⟩ → |+⟩ = (1/√2)(|0⟩ + |1⟩)
   |1⟩ → |−⟩ = (1/√2)(|0⟩ - |1⟩)
   
   Starting from: (1/2)(|000⟩ + |011⟩ + |110⟩ + |101⟩)
   
   After H(q[0]):
   (1/2)((1/√2)(|0⟩+|1⟩)|00⟩ + (1/√2)(|0⟩+|1⟩)|11⟩ + (1/√2)(|0⟩-|1⟩)|10⟩ + (1/√2)(|0⟩-|1⟩)|01⟩)
   
   = (1/2√2)(|000⟩ + |100⟩ + |011⟩ + |111⟩ + |010⟩ - |110⟩ - |001⟩ + |101⟩)
   
   Let me rearrange by q[0] outcome:
   When q[0]=0: (1/2√2)(|000⟩ + |011⟩ + |010⟩ - |001⟩) = (1/2√2)|0⟩(|00⟩ + |11⟩ + |10⟩ - |01⟩)
   When q[0]=1: (1/2√2)(|100⟩ + |111⟩ - |110⟩ + |101⟩) = (1/2√2)|1⟩(|00⟩ + |11⟩ - |10⟩ + |01⟩)

7. **CNOT(q[1], q[2]):** Deferred correction - this corrects based on q[1]'s measurement outcome
   
   Let me think about this differently. The teleportation protocol should leave q[2] in state |+⟩ after both corrections are applied.
   
   After steps 1-6, if Alice measures q[0] and q[1], Bob would apply X^b Z^a where a, b are the measurement outcomes.
   
   The deferred corrections CNOT(q[1], q[2]) and ctrl Z(q[0], q[2]) effectively apply these corrections without actually measuring.

8. **CNOT(q[1], q[2]):** Applies X correction conditioned on q[1]

9. **ctrl Z(q[0], q[2]):** Applies Z correction conditioned on q[0]

After both corrections, q[2] should be in state |+⟩.

10. **H(q[2]):** Rotates |+⟩ to |0⟩ (since H|+⟩ = |0⟩)

11. **H(q[2]) followed by H(q[2]):** These form an H-H pair which is identity (H² = I), so they cancel out.

Wait, the reference code has:

That's three H gates on q[2]. Let me re-read...

Actually Analyzing the:

//

## isqTrain/2573

- task_id: `isqTrain/2573`
- task_type: `code_equivalence`
- category: `quantum_communication`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `global_phase`, `isq_syntax_arrays`
- source: `isq_train_cot`
- dataset_index: `5261`

### Prompt

Determine if these two isQ implementations are functionally equivalent:

Version A:
```isq
import std;

qbit q[2]; 

procedure main() {
    H(q[0]);
    CNOT(q[0], q[1]);
    
    // Alice encodes "01" using X
    X(q[0]);
    
    // Bob decodes
    CNOT(q[0], q[1]);
    H(q[0]);
    
    M(q[0]); M(q[1]); // should be 01
}

```

Version B:
```isq
import std;

qbit q[2]; 

procedure main() {
    // Equivalent implementation with global phase
    GPhase(0.0);
    H(q[0]);
    CNOT(q[0], q[1]);
    
    // Alice encodes "01" using X
    X(q[0]);
    
    // Bob decodes
    CNOT(q[0], q[1]);
    H(q[0]);
    
    M(q[0]); M(q[1]); // should be 01
}

```

### Chain-of-thought reasoning

1.  **Analyze Program A**:
    *   Start: |00>
    *   `H(q[0])`: creates 1/sqrt(2) (|00> + |10>)
    *   `CNOT(q[0], q[1])`: creates 1/sqrt(2) (|00> + |11>) (Bell state)
    *   `X(q[0])`: creates 1/sqrt(2) (|10> + |01>)
    *   `CNOT(q[0], q[1])`: creates 1/sqrt(2) (|11> + |01>) = 1/sqrt(2) (|01> + |11>)
    *   `H(q[0])`: applies H to q[0].
        *   |01> -> 1/sqrt(2) (|01> - |11>) wait, |0> -> |+>, |1> -> |->
        *   |11> -> 1/sqrt(2) (|11> - |01>)
        *   Actually, let's trace exactly.
        *   State before H(q[0]): 1/sqrt(2) (|01> + |11>)
        *   H on q[0] of |01> is (1/sqrt(2) |01> - 1/sqrt(2) |11>)
        *   H on q[0] of |11> is (1/sqrt(2) |11> - 1/sqrt(2) |01>)
        *   Wait, standard encoding: |0> -> |+>, |1> -> |->.
        *   Wait, superdense coding encoding "01" is usually Z(q[0]).
        *   Let's trace standard superdense:
            *   Init |00>
            *   H(q[0]), CNOT -> 1/sqrt(2)(|00> + |11>)
            *   Alice wants to send "01" -> applies Z. State -> 1/sqrt(2)(|00> - |11>)
            *   Bob decodes: CNOT -> 1/sqrt(2)(|00> - |01>) -> H(q[0]) -> |01>.
        *   Here Alice applies X.
            *   Init: |00>
            *   H(q[0]) -> |+0>
            *   CNOT -> 1/sqrt(2)(|00> + |11>)
            *   X(q[0]) -> 1/sqrt(2)(|10> + |01>)
            *   CNOT -> 1/sqrt(2)(|11> + |01>)
            *   H(q[0]) -> 1/sqrt(2)(1/sqrt(2)(|0>-|1>)|1> + 1/sqrt(2)(|0>+|1>)|1>) = 1/sqrt(2)(1/sqrt(2)(2|0>|1>)) = |01>.
            *   Let's re-evaluate:
                *   CNOT(|10> + |01>) = |11> + |01>.
                *   H(q[0]) on (|01> + |11>) = (H|0>|1> + H|1>|1>) = (|+>|1> + |->|1>) = (1/sqrt(2)(|0>+|1>)|1> + 1/sqrt(2)(|0>-|1>)|1>) = 1/sqrt(2)(2|0>|1>) = |01>.
            *   Result is |01>. Measurement: q[0] = 0, q[1] = 1.

2.  **Analyze Program B**:
    *   Same as Program A, except it adds `GPhase(0.0)` at the beginning.
    *   `GPhase(0.0)` is equivalent to multiplying the state by $e^{i \times 0} = 1$.
    *   The state remains exactly the same.

3.  **Compare**:
    *   Program A: H(q[0]), CNOT, X(q[0]), CNOT, H(q[0]) -> final state |01>
    *   Program B: GPhase(0.0), H(q[0]), CNOT, X(q[0]), CNOT, H(q[0]) -> final state |01>
    *   The measurement probabilities are identical.

4.  **Drafting the explanation**:
    *   Program A initializes qubits to |00>, applies H and CNOT to create a Bell state, applies X to encode "01", and then reverses the Bell state preparation (CNOT then H) resulting in the state |01>.
    *

### Reference answer

{'equivalent': True, 'explanation': 'Program B adds GPhase(0.0) which is a trivial global phase of 0, producing identical measurement probabilities.'}

## isqTrain/1383

- task_id: `isqTrain/1383`
- task_type: `code_generation`
- category: `quantum_communication`
- difficulty: `intermediate`
- concept_tags: `entanglement`, `superposition`
- source: `isq_train_cot`
- dataset_index: `5104`

### Prompt

请用isQ语言编写一个量子电路：quantum teleportation to transfer the state |0> (prepared with no gate) from qubit 0 to qubit 2 using a Bell pair.

### Chain-of-thought reasoning

The user wants me to generate a reasoning section for a quantum teleportation circuit that transfers the state |0> from qubit 0 to qubit 2.

Let me trace through the circuit:

1. Initial state: |000> (all qubits in |0>)

2. H(q[1]): |0> ⊗ H|0> ⊗ |0> = |0> ⊗ |+> ⊗ |0> = |0+0>
   = |0> ⊗ (1/√2)(|0> + |1>) ⊗ |0>
   = 1/√2 (|000> + |010>)

3. CNOT(q[1], q[2]): Control is q[1], target is q[2]
   = 1/√2 (|000> + |011>) - This is a Bell pair between q[1] and q[2]

4. CNOT(q[0], q[1]): Control is q[0], target is q[1]
   = 1/√2 (|000> + |011>) - no change since q[0] is |0>

5. H(q[0]): Apply H to q[0]
   = 1/√2 (H|0>|00> + H|0>|11>)
   = 1/√2 ((1/√2)(|0>+|1>)|00> + (1/√2)(|0>+|1>)|11>)
   = 1/2 (|000> + |100> + |011> + |111>)
   = 1/2 (|000> + |011> + |100> + |111>)

6. M(q[0]), M(q[1]): Measure q[0] and q[1]
   This projects onto one of four outcomes:
   - |00>: q[2] in |0>
   - |01>: q[2] in |1>
   - |10>: q[2] in |0>
   - |11>: q[2] in |1>

7. CNOT(q[1], q[2]): Controlled on q[1] (classical measurement result)
   CZ(q[0], q[2]): Controlled on q[0] (classical measurement result)

Since the state being teleported is |0>, which is a +1 eigenstate of Z, the CZ correction doesn't change it. The CNOT correction flips q[2] when q[1] was measured as 1.

After corrections, q[2] should be in state |0>.

8. M(q[2]): Measures |0> with certainty.

Let me reconsider the state evolution more carefully:

Initial: |000>

After H(q[1]): 1/√2(|000> + |010>)

After CNOT(q[1], q[2]): 1/√2(|000> + |011>) - Bell pair created between q[1] and q[2]

After CNOT(q[0], q[1]): 1/√2(|000> + |011>) - unchanged since q[0] = |0>

After H(q[0]): 1/2(|000> + |100> + |011> + |111>)

This can be rewritten as:
1/2[|00>(|0> + |1>)_2 + |01>(|0> + |1>)_2 + |10>(|0> - |1>)_2 + |11>(|0> - |1>)_2]

Wait, let me recalculate:
1/2(|000> + |100> + |011> + |111>)
= 1/2[|00>|0> + |10>|0> + |01>|1> + |11>|1>]
= 1/2[|0>0(|0> + |1>) + |1>0(|0> - |1>)]

Hmm, that's not quite right. Let me be more careful:

The state is 1/2(|000> + |100> + |011> + |111>)

Grouping by q[0]q[1]:
- |00>|0>
- |10>|0>
- |01>|1>
- |11>|1>

So:
= 1/2[|00>|0> + |01>|1> + |10>|0> + |11>|1>]

After measurement of q[0], q[1]:
- If outcome is 00: q[2] is in |0>
- If outcome is 01: q[2] is in |1>
- If outcome is 10: q[2] is in |0>
- If outcome is 11:

## isqTrain/4616

- task_id: `isqTrain/4616`
- task_type: `output_prediction`
- category: `quantum_communication`
- difficulty: `intermediate`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `234`

### Prompt

预测以下isQ代码的输出概率：

```isq
import std;

qbit q[1];

procedure main() {
    
    X(q[0]); H(q[0]); 
    
    
    H(q[0]); Z(q[0]); H(q[0]); // HZH = X on qubit 0
    M(q[0]); 
}
```

### Chain-of-thought reasoning

## Circuit Analysis
1. **Operations applied:** X gate, Hadamard (H) gate, followed by H, Z, and H gates on qubit `q[0]`.
2. **State evolution:**
   - Starts in the initial state |0⟩. 
   - `X(q[0])` flips the state to |1⟩.
   - `H(q[0])` puts the state into the superposition |−⟩ = (1/√2)|0⟩ - (1/√2)|1⟩.
   - The sequence `H(q[0])`, `Z(q[0])`, `H(q[0])` is mathematically equivalent to applying the X gate (HZH = X).
   - Applying X to the |−⟩ state maps it back to |−⟩ (ignoring a global phase of -1): X(1/√2|0⟩ - 1/√2|1⟩) = 1/√2|1⟩ - 1/√2|0⟩ = -|−⟩.
3. **Final state before measurement:** The qubit is in the state |−⟩. 
4. **Predicted probability distribution:** Measuring the |−⟩ state in the computational basis yields a 50% chance for |0⟩ and a 50% chance for |1⟩.

Probability distribution: {|0⟩: 0.5, |1⟩: 0.5}

### Reference answer

{'predicted_probs': {'0': 0.5, '1': 0.5}, 'explanation': 'This isQ program operates on 1 qubit(s). The measurement probability distribution is: P(|0>) = 0.5000, P(|1>) = 0.5000.'}

## isqTrain/4858

- task_id: `isqTrain/4858`
- task_type: `code_generation`
- category: `quantum_communication`
- difficulty: `difficult`
- concept_tags: `entanglement`, `phase_manipulation`
- source: `isq_train_cot`
- dataset_index: `653`

### Prompt

Write isQ code for the following quantum task: for 2-round superdense coding. Use 4 qubits: (q[0],q[1]) for round 1, (q[2],q[3]) for round 2. Send 01 in round 1, 10 in round 2. Measure all.

### Chain-of-thought reasoning

## Reasoning
Goal: Implement 2-round superdense coding sending "01" (round 1) and "10" (round 2) using 4 qubits, all measured.

Round 1 (q[0], q[1]): H(q[0]) creates |+0>|00>, CNOT yields Bell state (|00>+|11>)|00>/√2. Encoding "01" via X(q[0]) gives (|10>+|01>)|00>/√2. Decoding: CNOT(q[0],q[1]) → (|11>+|01>)|00>/√2, then H(q[0]) → |01>|00>, since |1>|1> → (|0>-|1>)|1>/√2 and |0>|1> → (|0>+|1>)|1>/√2, summing to |0>|1>.

Round 2 (q[2], q[3]): Starting from |0100>, H(q[2])+CNOT creates Bell pair |01>(|00>+|11>)/√2. Encoding "10" via Z(q[2]) gives |01>(|00>-|11>)/√2. Decoding: CNOT(q[2],q[3]) → |01>(|00>-|10>)/√2, H(q[2]) → |01>|10>, since |0>→|+>, |1>→|−>, yielding |0>(|+>−|−>)|0>/2 = |0>|1>|1>|0> = |0110>.

Final state |0110⟩ measured with probability 1.0

## isqTrain/371

- task_id: `isqTrain/371`
- task_type: `code_generation`
- category: `quantum_communication`
- difficulty: `intermediate`
- concept_tags: `superposition`
- source: `isq_train_cot`
- dataset_index: `125`

### Prompt

I need an isQ program to implements a variant of the teleportation_protocol pattern using q[1] -> q[3]. The circuit should use a significantly expanded qubit register compared to the base version, with the additional qubits left in the ground state.

### Chain-of-thought reasoning

## Reasoning
1. Goal: Implement a teleportation protocol variant where Alice prepares |−⟩ on q[0] (representing q[1]→q[3] path in expanded register) and Bob measures all qubits in Z-basis.
2. Circuit uses 3 qubits; all are measured (q[0], q[1], q[2]), with q[1], q[2] left in ground state as ancilla.
3. State evolution: |000⟩ → X(q[0]) → |100⟩ → H(q[0]) → (|100⟩ − |000⟩)/√2 = |−⟩⊗|00⟩.
4. Qubits q[1], q[2] remain |0⟩ throughout; only q[0] is in superposition.
5. Z-measurement of |−⟩ = (|0⟩ − |1⟩)/√2 yields equal probability for outcomes 0 and 1.
6. Expected probabilities: {|000⟩: 0.5, |100⟩: 0.5}, since bitstring encoding has q[0] as highest bit.
